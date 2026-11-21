"""Robustness of CROWDFADE (batch-2 pass): neighbouring windows / basket sizes, overlap with MOM, yearly split.
    python3 studies/p151b_robust.py"""
import sys
sys.argv = [sys.argv[0], "--list"]
import p151b as b  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402
from lib import portfolio as pf  # noqa: E402

P, E = b.P, b.E
g = b.metrics_panel("global_ls")


def crowd(short, long, n):
    score = g.rolling(short, min_periods=max(2, int(short * 0.7))).mean() / g.rolling(long, min_periods=int(long * 0.6)).mean() - 1
    return pf.long_short(-score, E & score.notna(), n), "W"


def sh(W, every):
    p = pf.periods(pf.run(P, W, every))
    return pf.metrics(p["old"]).get("Sharpe"), pf.metrics(p["12m"]).get("Sharpe")


grid = []
for s in (3, 7, 14):
    for l in (30, 90, 180):
        for n in (5, 7, 10):
            o, r = sh(*crowd(s, l, n))
            grid.append({"short window": s, "long window": l, "n per side": n, "Sharpe old": o, "Sharpe 12m": r})
grid = pd.DataFrame(grid)

# overlap with MOM: correlation of daily returns, and the combo
cf = pf.run(P, *crowd(7, 90, 7))
mo = pf.run(P, *b.base.MOM())
corr = round(cf.net.corr(mo.net), 2)
combo = pf.run(P, 0.5 * crowd(7, 90, 7)[0] + 0.5 * b.base.MOM()[0], "W")
pc = pf.periods(combo)
yrs = cf.net.groupby(pd.to_datetime(cf.index, unit="ms").year).agg(
    lambda x: "%+.1f%% (Sharpe %.2f)" % (x.sum() * 100, x.mean() / x.std() * np.sqrt(365) if x.std() > 0 else 0))
pos = (grid[["Sharpe old", "Sharpe 12m"]] > 0).all(axis=1).sum()
summary = pd.DataFrame([
    {"check": "neighbours positive in both periods", "result": "%d of %d" % (pos, len(grid))},
    {"check": "daily-return correlation with MOM", "result": corr},
    {"check": "50/50 CROWDFADE + MOM Sharpe", "result": "%.2f old / %.2f 12m" % (pf.metrics(pc["old"])["Sharpe"], pf.metrics(pc["12m"])["Sharpe"])},
    {"check": "by calendar year", "result": "; ".join("%s %s" % kv for kv in yrs.items())}])
write_report("p151 batch 2 crowdfade robustness", [("Summary", summary), ("Neighbours (pre-registered: 7 / 90 / 7)", grid)])
