"""Thursday / Sunday check-in for the current ticket batch (sanity check, not management: holding 7 days tested best).

    python3 checkin.py            -> tickets/<batch>-checkin-<date>.md

Needs, fetched from TradingView just before (see the scheduled task):
  data/live_prices.json   live prices {coin: price} (Binance contract units)
  data/tv_checkin.json    daily bars since the batch was issued, INCLUDING today's forming bar:
                          {coin: {"t": [unix sec], "o": [], "h": [], "l": [], "c": []}}
For each ticket: filled? (price traded through the limit since issue), stop or take-profit hit (if both inside one daily
bar, the stop is assumed first), otherwise open with its current R and P&L. Actions (tested, LEDGER.md): open ->
HOLD; not filled by the Thursday check-in -> CANCEL; hit -> nothing to do. Close early only to protect a firm limit.
"""
import datetime as dt, glob, json, os

import pandas as pd

import config

SGT = dt.timezone(dt.timedelta(hours=8))
COST = config.FEE_PER_SIDE + config.SLIP_PER_SIDE
ACCOUNT_SIZE = {"100K": 100_000, "50K": 50_000}


def main():
    files = sorted(glob.glob(os.path.join(config.LAB, "tickets", "W*.json")))
    files = [f for f in files if "-checkin" not in f]
    if not files:
        print("no ticket batch yet"); return
    T = pd.read_json(files[-1])
    batch = T.batch.iloc[0]
    live = json.load(open(os.path.join(config.DATA, "live_prices.json")))
    bars = json.load(open(os.path.join(config.DATA, "tv_checkin.json")))
    issued = dt.datetime.strptime(T.issued_sgt.iloc[0], "%Y-%m-%d %H:%M").replace(tzinfo=SGT)
    issued_day = int(issued.astimezone(dt.timezone.utc).replace(hour=0, minute=0).timestamp())
    now = dt.datetime.now(SGT)
    rows = []
    for r in T.to_dict("records"):
        side = 1 if r["side"] == "LONG" else -1
        b = bars.get(r["coin"])
        px = live["prices"].get(r["coin"])
        status, R = "no data", None
        if b and px:
            x = pd.DataFrame(b)
            x = x[x.t >= issued_day]
            lim, stop, tp = r["limit entry"], r["stop"], r["take-profit"]
            filled = ((x.l <= lim).any() if side == 1 else (x.h >= lim).any()) or abs(px / lim - 1) < 0.002
            status = "OPEN"
            if not filled:
                status = "NOT FILLED"
            else:
                for bar in x.to_dict("records"):
                    hit_stop = bar["l"] <= stop if side == 1 else bar["h"] >= stop
                    hit_tp = bar["h"] >= tp if side == 1 else bar["l"] <= tp
                    if hit_stop:
                        status, px = "STOP HIT", stop; break
                    if hit_tp:
                        status, px = "TP HIT", tp; break
            if status != "NOT FILLED":
                risk = abs(lim - stop)
                R = ((px - lim) * side - COST * (lim + px)) / risk
        action = {"OPEN": "HOLD (stop and TP stay in place; closes Monday 08:00 SGT)",
                  "NOT FILLED": "CANCEL the order (not filled by Thursday: tested rule)",
                  "STOP HIT": "done (-1R)", "TP HIT": "done (+3R)", "no data": "check manually"}[status]
        rows.append({"ticket": r["id"], "account": r["account"], "coin": r["coin"], "side": r["side"], "status": status,
                     "price now": px, "R": None if R is None else round(R, 2),
                     "P&L USDT": None if R is None else round(R * r["risk USDT"]), "action": action})
    C = pd.DataFrame(rows)
    day = "Thursday" if now.weekday() == 3 else "Sunday" if now.weekday() == 6 else now.strftime("%A")
    lines = ["# Check-in %s, batch %s (%s SGT)" % (day, batch, now.strftime("%Y-%m-%d %H:%M")), "",
             "Sanity check only: the tested plan is to hold every filled trade until its stop, take-profit, or Monday "
             "08:00 SGT (early exits didn't help in testing). Prices: TradingView live. Fills are inferred from prices; "
             "tell me if a fill differs.", "",
             "| ticket | status | price now | R | P&L (USDT) | action |", "|---|---|---|---|---|---|"]
    lines += ["| %s | %s | %s | %s | %s | %s |" % (r.ticket, r.status, "%.6g" % r._6 if r._6 else "-",
                                                 "-" if pd.isna(r.R) else "%+.2f" % r.R,
                                                 "-" if pd.isna(r._8) else "%+,.0f" % r._8, r.action) for r in C.itertuples()]
    lines += [""]
    for acct, size in ACCOUNT_SIZE.items():
        x = C[C.account == acct]
        pnl = x["P&L USDT"].fillna(0).sum()
        open_n = (x.status == "OPEN").sum()
        warn = " **Near a firm limit: consider closing the biggest loser.**" if pnl <= -0.035 * size else ""
        lines.append(("- **%s:** batch P&L %+,.0f USDT (%+.2f%% of the account), %d open, %d not filled. Daily limit 5%% "
                     "(%s), total floor 10%% in stage 1 / 8%% in stage 2." % (acct, pnl, pnl / size * 100, open_n,
                                                                         (x.status == "NOT FILLED").sum(),
                                                                         f"{size * 0.05:,.0f} USDT")) + warn)
    if day == "Sunday":
        lines += ["", "Tomorrow (Monday) 08:00 SGT: close every open position from this batch, then place the new batch."]
    out = os.path.join(config.LAB, "tickets", "%s-checkin-%s.md" % (batch, now.strftime("%Y-%m-%d")))
    open(out, "w").write("\n".join(lines))
    print("\n".join(lines))
    print("written:", out)


if __name__ == "__main__":
    main()
