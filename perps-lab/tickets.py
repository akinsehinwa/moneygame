"""Weekly tickets for two Bitfunded accounts (decided 2026-11-21, see LEDGER.md):
  100K: COMBO ranking (crowd + momentum)  top 2 long + top 2 short
  50K:  CROWDFADE ranking (crowd only)    top 2 long + top 2 short, no coin the 100K holds
Risk 1.5% of the account per coin. Stop 3 x daily ATR(14); take-profit 3R (a short's TP floored at 10% of entry);
close everything at the next weekly rebalance (7-day hold rule). Coins whose stop is > 35% away are skipped.
5x isolated: margin = max(notional / 5, notional x (stop distance + 5%)), so liquidation always sits beyond the stop.

    python3 tickets.py            -> tickets/<date>.md (signals and reference prices from Binance archive data)
Stops and take-profits are given as % of the entry, so they can be applied to the actual fill price.
"""
import datetime as dt, json, os, sys, urllib.request

import numpy as np
import pandas as pd

import config

sys.argv = [sys.argv[0], "--list"]
sys.path.insert(0, os.path.join(config.LAB, "studies"))
import prop  # noqa: E402
from lib.btcstate import label  # noqa: E402
from lib.data import load_1h, resample  # noqa: E402

ACCOUNTS = [("100K", 100_000, "COMBO"), ("50K", 50_000, "CROWDFADE")]
RISK = 0.015
K, ATR_MULT, TARGET_R, MAX_STOP = 2, 3.0, 3.0, 0.35
COST = config.FEE_PER_SIDE + config.SLIP_PER_SIDE
SGT = dt.timezone(dt.timedelta(hours=8))


def live_prices(max_age_h=3):
    """Live prices saved from TradingView (data/live_prices.json, Binance contract units), if fresh."""
    f = os.path.join(config.DATA, "live_prices.json")
    if not os.path.exists(f):
        return None, None
    j = json.load(open(f))
    fetched = dt.datetime.strptime(j["fetched_utc"], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
    age = (dt.datetime.now(dt.timezone.utc) - fetched).total_seconds() / 3600
    return (j["prices"], j["fetched_utc"]) if age <= max_age_h else (None, None)


def main():
    live, live_at = live_prices()
    d = prop.C.index[-1]                                    # latest complete daily bar in the archive
    scores = {"COMBO": prop.COMBO_S, "CROWDFADE": prop.CF_S}
    now = dt.datetime.now(SGT)
    iso = now.isocalendar()
    batch = "W%d-%02d" % (iso[0], iso[1])
    used, tickets = set(), []
    for acct, size, strat in ACCOUNTS:
        s = scores[strat].loc[d].where(prop.el.loc[d]).dropna().sort_values()
        stop_pct = (ATR_MULT * prop.ATR.loc[d] / prop.C.loc[d]).reindex(s.index)
        mult = pd.Series({c: 1000.0 if config.BINANCE_SYMBOL.get(c, "").startswith("1000") else 1.0 for c in s.index})
        ok = (stop_pct <= MAX_STOP) & ~s.index.isin(list(used))
        s = s[ok]
        picks = [(c, 1) for c in s.index[::-1][:K]] + [(c, -1) for c in s.index[:K]]
        for n, (coin, side) in enumerate(picks, 1):
            used.add(coin)
            sp = float(stop_pct[coin])
            px = float(live[coin]) if live and coin in live else float(prop.C.at[d, coin])   # Binance contract units
            stop = px * (1 - side * sp)
            target = px * (1 + side * TARGET_R * sp)
            if side == -1:
                target = max(target, 0.1 * px)
            risk_usd = size * RISK
            notional = risk_usd / (sp + 2 * COST)           # fees + slippage included in the risk
            margin = max(notional / 5, notional * (sp + 0.05))
            tickets.append({"batch": batch, "id": "%s-%s-%s-%s" % (batch, acct, coin, "L" if side == 1 else "S"),
                            "margin to enter USDT": notional / 5,
                            "margin to add USDT": margin - notional / 5,
                            "account": acct, "strategy": strat, "coin": coin, "side": "LONG" if side == 1 else "SHORT",
                            "limit entry": px, "stop": stop, "take-profit": target, "stop %": sp * 100,
                            "position size USDT": notional, "margin USDT": margin,
                            "effective leverage": notional / margin, "qty": notional / px,
                            "tp %": abs(target / px - 1) * 100,
                            "risk USDT": risk_usd, "reward at TP USDT": risk_usd * TARGET_R,
                            "unit": "1000 coins" if mult[coin] > 1 else "1 coin"})
    T = pd.DataFrame(tickets)
    st = label(resample(load_1h("BTC"), 24)).iloc[-1]
    lines = ["# Ticket batch %s (generated %s SGT)" % (batch, now.strftime("%a %Y-%m-%d %H:%M")), "",
             "Signals: data through the daily candle of %s (closed %s 08:00 SGT). Prices: %s. **If your fill "
             "differs, set the stop and take-profit from your actual entry using the %% columns** (long: stop = entry x "
             "(1 - stop%%), TP = entry x (1 + TP%%); short: the reverse)." % (
                 pd.to_datetime(d, unit="ms").date(), (pd.to_datetime(d, unit="ms") + pd.Timedelta(days=1)).date(),
                 ("TradingView live (BINANCE perps), fetched %s UTC" % live_at) if live else "last daily close (stale)"),
             "BTC state at that close: %s (20-day move %+.1f%%)." % (st.state, st.r20 * 100), "",
             "How to place: 5x isolated, limit order with the 'margin to enter' in the margin field (position = margin x 5), "
             "stop-loss and take-profit attached. Right after it fills, ADD the 'margin to add' to the position (keeps "
             "liquidation beyond the stop; 0 = nothing to add). Hold until stop, take-profit, or the close at next Monday "
             "08:00 SGT. No early exits (tested: they don't help). Unfilled orders stay until the Thursday 08:00 SGT check-in, "
             "then cancel (tested). Risk %.1f%% of the account per coin." % (RISK * 100), ""]
    for acct, size, strat in ACCOUNTS:
        x = T[T.account == acct]
        lines += ["## %s account (%s), risk $%s per coin" % (acct, strat, f"{size * RISK:,.0f}"), "",
                  "| ticket | coin | side | limit entry | stop-loss | take-profit | margin to enter (USDT) | margin to add (USDT) | stop % | TP % |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for r in x.to_dict("records"):
            f = lambda v: ("%.6g" % v)
            lines.append("| %s | %s%s | %s | %s | %s | %s | %s | %s | %.1f%% | %.1f%% |" % (
                r["id"], r["coin"], " (1000)" if r["unit"] != "1 coin" else "", r["side"], f(r["limit entry"]),
                f(r["stop"]), f(r["take-profit"]), f"{r['margin to enter USDT']:,.0f}", f"{r['margin to add USDT']:,.0f}",
                r["stop %"], r["tp %"]))
        lines += ["", "Total margin: $%s (%.0f%% of the account; firm limit 65%%). Max loss if every stop hits: "
                  "$%s (%.1f%%; daily limit 5%%)." % (f"{x['margin USDT'].sum():,.0f}", x["margin USDT"].sum() / size * 100,
                                                     f"{x['risk USDT'].sum():,.0f}", x["risk USDT"].sum() / size * 100), ""]
    os.makedirs(os.path.join(config.LAB, "tickets"), exist_ok=True)
    f = os.path.join(config.LAB, "tickets", "%s.md" % batch)
    open(f, "w").write("\n".join(lines))
    T.assign(issued_sgt=now.strftime("%Y-%m-%d %H:%M"), signal_day=str(pd.to_datetime(d, unit="ms").date()),
             btc_state=st.state, btc_r20=round(float(st.r20), 4), status="issued").to_json(
        os.path.join(config.LAB, "tickets", "%s.json" % batch), orient="records", indent=1)
    print("\n".join(lines))
    print("written:", f)


if __name__ == "__main__":
    main()
