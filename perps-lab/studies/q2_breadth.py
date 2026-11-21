"""Q2: breadth filter on BRK. Breadth = number of coins with a same-side BRK signal on the same 4h close."""
from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd
import config, evaluate
from strategies import brk

H = 3600_000
rows = []
for coin in config.COINS:
    b = bars(coin, 4)
    T = b.t.values
    for s in brk.signals(b):
        rows.append((coin, int(T[s.i]) + 4 * H, s.side))
sig = pd.DataFrame(rows, columns=["coin", "t_sig", "side"])
breadth = sig.groupby(["t_sig", "side"]).size().rename("breadth").reset_index()

d = evaluate.load()
d = d[d.strat == "BRK"].merge(breadth, on=["t_sig", "side"], how="left")
months_old = 24

tab = []
for thr in (2, 3, 5):
    for leg, x in d.groupby("leg"):
        for part, y in (("kept (breadth >= %d)" % thr, x[x.breadth >= thr]), ("dropped", x[x.breadth < thr])):
            o, r = y[~y.recent], y[y.recent]
            tab.append({"threshold": thr, "strategy": leg, "group": part, "n old": len(o),
                        "avgR old": round(o.r.mean(), 3), "R/mo old": round(o.r.sum() / months_old, 1),
                        "n 12m": len(r), "avgR 12m": round(r.r.mean(), 3), "R/mo 12m": round(r.r.sum() / 12, 1)})
dist = d.breadth.describe(percentiles=[.5, .75, .9]).round(1).to_frame().T
write_report("Q2 breadth filter on BRK", [("Breadth distribution (signals per 4h close, same side)", dist),
                                          ("Kept vs dropped trades", pd.DataFrame(tab))])
