"""Limit-order fills and cancel timing for the weekly tickets (pre-registered in LEDGER.md).
    python3 studies/fills.py"""
import sys
sys.argv = [sys.argv[0], "--list"]
import prop  # noqa: E402
import manage as mg  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402

COST, DELTA = prop.COST, 0.005


def one(coin, t_entry, side, atr):
    d = mg.h1(coin)
    T = d["t"]
    i = int(np.searchsorted(T, t_entry))
    if i >= len(T) or T[i] != t_entry or i + 170 >= len(T):
        return None
    lim = d["o"][i] * (1 - side * DELTA)
    stop_pct = 3.0 * atr / d["o"][i]
    fill = None
    for k in range(0, 167):
        j = i + k
        if (side == 1 and d["l"][j] <= lim) or (side == -1 and d["h"][j] >= lim):
            fill = k
            break
    if fill is None:
        return {"delay": None, "r": 0.0}
    entry = lim
    risk = entry * stop_pct
    stop, tp = entry - side * risk, entry + side * 3.0 * risk
    if side == -1:
        tp = max(tp, 0.1 * entry)
    R = lambda px: ((px - entry) * side - COST * (entry + px)) / risk
    for k in range(fill, 168):
        j = i + k
        o, hh, ll = d["o"][j], d["h"][j], d["l"][j]
        if k == 167:
            return {"delay": fill, "r": R(d["o"][j + 1])}
        if (side == 1 and ll <= stop) or (side == -1 and hh >= stop):
            return {"delay": fill, "r": R(min(stop, o) if side == 1 else max(stop, o))}
        if k > fill and ((side == 1 and hh >= tp) or (side == -1 and ll <= tp)):
            return {"delay": fill, "r": R(max(tp, o) if side == 1 else min(tp, o))}
    return None


rows_t = []
for book in ("100K", "50K"):
    for t_entry, d, picks in mg.weeks_for(book):
        for c, s in picks:
            x = one(c, t_entry, s, prop.ATR.at[d, c])
            if x:
                rows_t.append({"account": book, "t": t_entry, **x})
X = pd.DataFrame(rows_t)
X["period"] = np.where(X.t < prop.SPLIT, "old", "12m")
out = []
for book in ("100K", "50K"):
    for per in ("old", "12m"):
        x = X[(X.account == book) & (X.period == per)]
        for name, h in (("cancel after 4h", 4), ("cancel after 24h (Tue 08:00)", 24), ("cancel after 72h (Thu 08:00)", 72),
                        ("never cancel (until Monday)", 167)):
            f = x.delay.notna() & (x.delay < h)
            out.append({"account": book, "period": per, "rule": name, "tickets": len(x), "fill rate %": round(f.mean() * 100),
                        "avg R of filled": round(x[f].r.mean(), 3), "R per ticket issued": round(x.r.where(f, 0).mean(), 3)})
bucket = pd.cut(X.delay, [-1, 0, 4, 24, 72, 167], labels=["first hour", "1-4h", "4-24h", "24-72h", "72h+"])
bd = X.assign(b=bucket).groupby(["account", "b"], observed=True).r.agg(["size", "mean"]).round(3).reset_index()
bd.columns = ["account", "filled after", "trades", "avg R"]
write_report("limit fills and cancel timing", [
    ("Setup", "Limit at Monday's open moved 0.5% in the trade's favour; stop / TP distances as tested; exit Monday 08:00 SGT."),
    ("Cancel rules", pd.DataFrame(out)), ("Avg R by how long the fill took", bd)])
print(pd.DataFrame(out).to_string(index=False)); print(bd.to_string(index=False))
