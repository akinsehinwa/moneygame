"""E5 (healthy-trend retracement) split by leg direction vs Bitcoin's state, by group and size tier.
    python3 studies/atlas2_e5.py   (needs studies/atlas2.py run first)"""
import os
from common import *  # noqa: F401,F403
import pandas as pd
import config

EV = pd.read_pickle(os.path.join(config.DATA, "atlas2_events.pkl"))
CT = pd.read_csv(os.path.join(config.RESULTS, "atlas2-coins.csv"), index_col=0)
e5 = EV["E5"].copy()
e5["group"], e5["tier"] = e5.coin.map(CT.group), e5.coin.map(CT["size tier"])
e5["leg"] = e5.side.map({1: "up leg", -1: "down leg"})
e5 = e5[e5.state.notna()]
STATES = ["STRONG_DOWN", "DOWN", "COIL", "RANGE", "UP", "STRONG_UP"]
out = []
for keycol in ("tier", "group"):
    for metric, name in (("hit50", "P(50% pullback)"), ("cont", "P(continue after 50%)")):
        for leg in ("up leg", "down leg"):
            x = e5[e5.leg == leg]
            p = x.groupby([keycol, "state"])[metric].agg(["mean", "count"])
            p = p[p["count"] >= 15]["mean"].unstack()[[s for s in STATES]].round(2)
            p.insert(0, "leg", leg); p.insert(0, keycol, p.index); p.insert(0, "measure", name)
            out.append(p)
n = e5.groupby(["leg", "state"]).size().unstack()[STATES]
n.insert(0, "leg", n.index)
write_report("element atlas E5 by leg direction",
             [("Number of big legs", n)] + [("%s, %s, by %s" % (t.measure.iloc[0], t.leg.iloc[0], t.columns[2] if False else t.columns[1]), t.drop(columns=["measure"])) for t in out])
