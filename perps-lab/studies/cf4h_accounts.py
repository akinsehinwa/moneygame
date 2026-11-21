"""Two accounts, slot-constrained: weekly books + CF4H (pre-registered in LEDGER.md; rules in PROP_RULES.md).

Per account: max 5 open positions (open + resting limits; fills at the next 4H open are modelled as immediate, so
nothing rests), margin of open positions <= 60%, at most 2 new CF4H entries per 4H alert, one position per coin,
the two accounts never hold the same coin. Weekly trades take priority on Monday 08:00 SGT.
Schemes: A) weekly book (4 slots) + CF4H in the 5th slot, both accounts; B) 100K as A, 50K CF4H only (5 slots);
C) both accounts CF4H only (5 slots). Risk 1.5% per weekly position, 1.0% per CF4H position.
Challenge from every Monday since 2023-11-20 with 180+ days after it.
    python3 studies/cf4h_accounts.py
"""
import os
import sys
sys.argv = [sys.argv[0], "--list"]
import prop  # noqa: E402
import prop_pair as pp  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402
import config  # noqa: E402

H, DAY = 3600_000, 24 * 3600_000
COST = prop.COST
RISK_W, RISK_4 = 0.015, 0.010
prop.ATR_STOP = 3.0


def margin_frac(risk, stop_pct):
    notional = risk / (stop_pct + 2 * COST)
    return max(notional / 5, notional * (stop_pct + 0.05))


# ---------------------------------------------------------------- candidates
def weekly(acct):
    out = []
    for d in prop.C.index[prop.b.REB.values & (prop.C.index >= prop.START - 7 * DAY)]:
        t = int(d) + DAY
        pa = pp.picks_for(prop.COMBO_S, d)
        picks = pa if acct == "100K" else pp.picks_for(prop.CF_S, d, exclude=[c for c, _ in pa])
        for coin, side in picks:
            res = prop.trade(coin, t, side, prop.ATR.at[d, coin])
            if res:
                m = res[1]
                out.append({"t": t, "coin": coin, "side": side, "r": res[0], "t_out": int(m.index[-1]), "marks": m,
                            "risk": RISK_W, "kind": "W",
                            "margin": margin_frac(RISK_W, 3 * prop.ATR.at[d, coin] / prop.C.at[d, coin])})
    return out


CF = pd.read_pickle(os.path.join(config.DATA, "cf4h_candidates.pkl"))


def simulate(scheme):
    books = {"100K": [], "50K": []}
    wk = {a: (weekly(a) if (scheme == "A" or (scheme == "B" and a == "100K")) else []) for a in books}
    cf_cap = {"A": {"100K": 1, "50K": 1}, "B": {"100K": 1, "50K": 5}, "C": {"100K": 5, "50K": 5}}[scheme]
    events = sorted(set([x["t"] for a in wk for x in wk[a]]) | set(CF.t.unique()))
    cf_by_t = {t: g for t, g in CF.groupby("t")}
    for t in events:
        for acct in ("100K", "50K"):
            book = books[acct]
            open_ = [x for x in book if x["t"] <= t < x["t_out"]]
            other = {x["coin"] for x in books["50K" if acct == "100K" else "100K"] if x["t"] <= t < x["t_out"]}
            for x in [w for w in wk[acct] if w["t"] == t]:          # weekly batch first
                if len(open_) < 5 and x["coin"] not in {o["coin"] for o in open_} | other and \
                        sum(o["margin"] for o in open_) + x["margin"] <= 0.60:
                    book.append(x); open_.append(x)
            g = cf_by_t.get(t)
            if g is None:
                continue
            new = 0
            for side in (1, -1):
                n_cf = sum(1 for o in open_ if o["kind"] == "4")
                if len(open_) >= 5 or n_cf >= cf_cap[acct] or new >= 2:
                    break
                cands = g[g.side == side].sort_values("rank")
                if scheme == "C" and acct == "50K":
                    cands = cands.iloc[1:]                           # the 50K takes the 2nd-ranked signal
                for c in cands.itertuples():
                    held = {o["coin"] for o in open_} | other
                    mg = margin_frac(RISK_4, c.stop_pct)
                    if c.coin in held or sum(o["margin"] for o in open_) + mg > 0.60:
                        continue
                    x = {"t": c.t, "coin": c.coin, "side": c.side, "r": c.r, "t_out": c.t_out, "marks": c.marks,
                         "risk": RISK_4, "kind": "4", "margin": mg}
                    book.append(x); open_.append(x); new += 1
                    break
    return books


def equity(trades, s, horizon=180):
    n = horizon * 24
    grid0 = s
    close = np.zeros(n); worst = np.zeros(n); real = np.zeros(n + 1)
    for x in trades:
        if x["t"] < s or x["t"] >= s + n * H:
            continue
        m = x["marks"]
        idx = ((m.index.values - grid0) // H).astype(int)
        ok = idx < n
        # floating marks before the exit bar; realized from the exit bar on
        fl = idx[:-1][ok[:-1]]
        close[fl] += x["risk"] * m.close_R.values[:-1][ok[:-1]]
        worst[fl] += x["risk"] * m.worst_R.values[:-1][ok[:-1]]
        e = min(idx[-1], n)
        real[e] += x["risk"] * x["r"]
    r = np.cumsum(real)[:n]
    return r + close, r + worst


def stage(trades, s, target, floor):
    ec, ew = equity(trades, s)
    hours = s // H + np.arange(len(ec))
    day = (hours * H - 16 * H) // DAY
    first = np.r_[True, day[1:] != day[:-1]]
    day_start = pd.Series(np.where(first, ec, np.nan)).ffill().values
    fail = np.where((ew <= -floor) | (ew - day_start <= -0.05))[0]
    win = np.where(ec >= target)[0]
    f = fail[0] if len(fail) else 10 ** 9
    w = win[0] if len(win) else 10 ** 9
    if f == w == 10 ** 9:
        return "open", None
    return ("pass", s + w * H) if w < f else ("fail", s + f * H)


def challenge(trades):
    mondays = [int(t) for t in prop.C.index[prop.b.REB.values] + DAY if prop.START <= t <= prop.C.index[-1] - 180 * DAY]
    out = []
    for s in mondays:
        r1, t1 = stage(trades, s, 0.08, 0.10)
        rec = {"start": s, "s1": r1, "d1": (t1 - s) / DAY if t1 else np.nan, "s2": "-", "d2": np.nan}
        if r1 == "pass":
            s2 = min([m for m in mondays + [t1 + 7 * DAY] if m > t1] or [t1 + 7 * DAY])
            s2 = (t1 // (7 * DAY) + 1) * 7 * DAY + 4 * DAY     # next Monday 00:00 UTC
            r2, t2 = stage(trades, s2, 0.05, 0.08)
            rec["s2"], rec["d2"] = r2, ((t2 - s) / DAY if t2 else np.nan)
        out.append(rec)
    return pd.DataFrame(out)


if __name__ == "__main__":
    rows, tpw = [], []
    for scheme in ("A", "B", "C"):
        books = simulate(scheme)
        for acct, tr in books.items():
            weeks = (prop.C.index[-1] - prop.START) / (7 * DAY)
            r = pd.Series([x["r"] * x["risk"] for x in tr], index=[x["t"] for x in tr])
            wkr = r.groupby(r.index // (7 * DAY)).sum()
            old, new = wkr[wkr.index * 7 * DAY < prop.SPLIT], wkr[wkr.index * 7 * DAY >= prop.SPLIT]
            ch = challenge(tr)
            for hz in (90, 180):
                passed = ((ch.s2 == "pass") & (ch.d2 <= hz)).mean() * 100
                failed = (((ch.s1 == "fail") & (ch.d1 <= hz)) | ((ch.s2 == "fail") & (ch.d2 <= hz))).mean() * 100
                p1 = ((ch.s1 == "pass") & (ch.d1 <= hz)).mean() * 100
                rows.append({"scheme": scheme, "account": acct, "by day": hz, "trades/week": round(len(tr) / weeks, 1),
                             "weekly Sharpe old": round(old.mean() / old.std() * np.sqrt(52), 2),
                             "weekly Sharpe 12m": round(new.mean() / new.std() * np.sqrt(52), 2),
                             "avg %/week": round(wkr.mean() * 100, 2), "passed stage 1 %": round(p1),
                             "passed both %": round(passed), "failed %": round(failed),
                             "median days to pass both": round(ch[(ch.s2 == "pass")].d2.median()) if (ch.s2 == "pass").any() else None})
                print(rows[-1], flush=True)
    write_report("cf4h two-account schemes", [
        ("Setup", __doc__.split("\n\n")[1]), ("Results", pd.DataFrame(rows))])
