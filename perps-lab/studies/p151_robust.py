"""Robustness checks for the batch-1 passes (added after the first run; they only make the bar stricter):
(a) drop each book's 3 best coins per period: is the rest still positive?
(b) neighbouring parameters: MOM formation x skip x n, SECTOR lookback.
    python3 studies/p151_robust.py
"""
import sys
sys.argv = [sys.argv[0], "--list"]
import p151 as s  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402
from lib import portfolio as pf  # noqa: E402

P, R, C, E = s.P, s.R, s.C, s.E
B = int(pd.Timestamp("2025-11-20", tz="UTC").timestamp() * 1000)


def held(W, every):
    W = W.reindex(index=C.index, columns=C.columns).fillna(0.0)
    m = pf.rebalance_days(W.index, every)
    return W.where(pd.Series(m, index=W.index), np.nan).ffill().fillna(0.0).shift(1).fillna(0.0)


def sharpe(W, every):
    p = pf.periods(pf.run(P, W, every))
    return pf.metrics(p["old"]).get("Sharpe"), pf.metrics(p["12m"]).get("Sharpe")


conc = []
for name in ("MOM", "TRENDLO", "MOMCARRY", "SECTOR"):
    h = held(*s.STRATS[name]())
    contrib = h * R.fillna(0.0) - h * P["F"]
    for per, sel in (("old", contrib.index < B), ("12m", contrib.index >= B)):
        c = contrib[sel].sum().sort_values()
        conc.append({"strategy": name, "period": per, "sum of returns": round(c.sum(), 2),
                     "best 3 coins": ", ".join("%s %+.2f" % kv for kv in c.tail(3)[::-1].items()),
                     "without best 3": round(c.sum() - c.tail(3).sum(), 2)})


def mom(form, skip, n):
    rm = R.shift(skip).rolling(form, min_periods=int(form * 0.8))
    return pf.long_short(rm.mean() / rm.std(), E, n, s.inv(s.vol(60))), "W"


grid = []
for f in (30, 60, 90, 120):
    for sk in (0, 7, 14):
        for n in (5, 7, 10):
            o, r = sharpe(*mom(f, sk, n))
            grid.append({"formation": f, "skip": sk, "n": n, "Sharpe old": o, "Sharpe 12m": r})


def sector(lb):
    r = C.pct_change(lb, fill_method=None).where(E)
    sec = pd.DataFrame({k: r[[c for c in v if c in r]].mean(axis=1) for k, v in s.SECTORS.items()})
    rk = sec.rank(axis=1, ascending=False)
    W = pd.DataFrame(0.0, index=C.index, columns=C.columns)
    for k, coins in s.SECTORS.items():
        for c in coins:
            W.loc[(rk[k] <= 2) & E[c], c] = 1.0
            W.loc[(rk[k] >= 5) & E[c], c] = -1.0
    lw, sw = W.clip(lower=0), -W.clip(upper=0)
    lw = lw.div(lw.sum(axis=1).where(lw.sum(axis=1) > 0), axis=0) * 0.5
    sw = sw.div(sw.sum(axis=1).where(sw.sum(axis=1) > 0), axis=0) * 0.5
    return (lw - sw).fillna(0.0), "W"


sec = [dict(zip(("lookback", "Sharpe old", "Sharpe 12m"), (lb,) + sharpe(*sector(lb)))) for lb in (14, 21, 30, 45, 60, 90)]
write_report("p151 robustness of batch-1 passes", [("(a) Concentration: per-coin return contribution", pd.DataFrame(conc)),
                                                    ("(b) MOM neighbours (pre-registered: 60 / 7 / 7)", pd.DataFrame(grid)),
                                                    ("(b) SECTOR lookback (pre-registered: 30)", pd.DataFrame(sec))])
