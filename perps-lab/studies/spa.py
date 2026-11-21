"""Data-snooping check: did any of the 28 basket books beat cash once we account for having tried all 28?
Hansen's SPA and Romano-Wolf StepM (arch.bootstrap). python3 studies/spa.py"""
import sys
sys.argv = [sys.argv[0], "--list"]
import p151 as a  # noqa: E402
import p151b as b  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from arch.bootstrap import SPA, StepM  # noqa: E402
from common import write_report  # noqa: E402
import config  # noqa: E402
from lib import portfolio as pf  # noqa: E402

P = a.P
series = {}
for name, f in a.STRATS.items():
    W, every = f()
    series[name] = pf.run(P, W, every).net
for name, f in b.STRATS.items():
    W, every = f()
    if every == "returns":
        series[name] = W.mean(axis=1).fillna(0.0)
    else:
        series[name] = pf.run(P, W, every).net
oiv = b.metrics_panel("oi_value")
sc = -(oiv.rolling(7, min_periods=5).mean() / oiv.rolling(30, min_periods=20).mean() - 1)
W_oi = pf.long_short(sc, b.E & sc.notna(), 7)
series["OIFADE"] = pf.run(P, W_oi, "W").net
series["OIFADE+CROWDFADE"] = pf.run(P, 0.5 * W_oi + 0.5 * b.CROWDFADE()[0], "W").net
D = pd.DataFrame(series)
start = int(pd.Timestamp(config.EVAL_START, tz="UTC").timestamp() * 1000)
split = int(pd.Timestamp(config.SPLIT, tz="UTC").timestamp() * 1000)
rows, steps = [], []
for label, sel in (("whole sample", D.index >= start), ("last 12 months", D.index >= split)):
    X = D[sel].fillna(0.0)
    losses = -X
    bench = np.zeros(len(X))
    spa = SPA(bench, losses.values, block_size=10, reps=10000, seed=7)
    spa.compute()
    sm = StepM(bench, losses, size=0.05, block_size=10, reps=10000, seed=7)
    sm.compute()
    sharpe = (X.mean() / X.std() * np.sqrt(365)).sort_values(ascending=False)
    best = sharpe.index[0]
    t = X[best].mean() / X[best].std() * np.sqrt(len(X))
    from scipy.stats import norm
    rows.append({"window": label, "days": len(X), "best book": best, "its Sharpe": round(sharpe.iloc[0], 2),
                 "single-test p (as if only one tried)": round(1 - norm.cdf(t), 4),
                 "SPA p (lower / consistent / upper)": " / ".join("%.3f" % v for v in spa.pvalues.values),
                 "StepM: books that beat cash": ", ".join(map(str, sm.superior_models)) or "none"})
    steps.append(sharpe.round(2).rename(label))
    print(rows[-1], flush=True)
write_report("data snooping check spa stepm", [
    ("Method", "28 basket books (every one tried, incl. rejected), daily net returns, benchmark = cash. SPA asks whether "
               "the best is better than cash after accounting for all 28; StepM lists which beat cash at 5%. "
               "Stationary bootstrap, 10,000 reps, 10-day blocks."),
    ("Results", pd.DataFrame(rows)), ("Sharpe of every book", pd.concat(steps, axis=1).reset_index().rename(columns={"index": "book"}))])
