"""Intraday timing facts (descriptive, SGT): volume by 4H slot; does the first 4H candle of the day (08-12 SGT) set the
direction for the rest of the day (12:00 -> 08:00 next day)? Same for the 20:00 SGT candle (20-24 SGT -> rest).
Absolute move (range) by slot. All 72 coins since 2023-11-20.  python3 studies/timing.py"""
from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd
import config
from lib.data import load_1h, resample

H = 3600_000
A0 = int(pd.Timestamp(config.EVAL_START, tz="UTC").timestamp() * 1000)
vol_rows, dir_rows, rng_rows = [], [], []
for c in config.COINS:
    b = resample(load_1h(c), 4)
    b = b[b.t >= A0].copy()
    b["slot"] = ((b.t // H) % 24 + 8) % 24          # SGT open hour: 8, 12, 16, 20, 0, 4
    b["qv"] = b.v * b.c
    b["day"] = (b.t - 0) // (24 * H)                 # UTC day = 08:00 SGT to 08:00 SGT
    b["absmove"] = (b.h - b.l) / b.o
    day_qv = b.groupby("day").qv.transform("sum")
    vol_rows.append(b.assign(share=b.qv / day_qv).groupby("slot").share.mean().rename(c))
    rng_rows.append(b.groupby("slot").absmove.mean().rename(c))
    for d, g in b.groupby("day"):
        if len(g) != 6:
            continue
        g = g.set_index("slot")
        first = g.at[8, "c"] / g.at[8, "o"] - 1
        rest = g.at[4, "c"] / g.at[8, "c"] - 1           # 12:00 SGT -> 08:00 next day
        ny = g.at[20, "c"] / g.at[20, "o"] - 1
        after_ny = g.at[4, "c"] / g.at[20, "c"] - 1      # 24:00 -> 08:00 next day
        dir_rows.append({"coin": c, "first": first, "rest": rest, "ny": ny, "after_ny": after_ny})
V = pd.DataFrame(vol_rows).mean().reindex([8, 12, 16, 20, 0, 4])
Rg = pd.DataFrame(rng_rows).mean().reindex([8, 12, 16, 20, 0, 4])
D = pd.DataFrame(dir_rows)
def agree(x, y, big=None):
    m = x.abs() > (x.abs().quantile(big) if big else 0)
    return round((np.sign(x[m]) == np.sign(y[m])).mean() * 100, 1), round(x[m].corr(y[m]), 3), int(m.sum())
rows = []
for name, x, y in (("first 4H (08-12) -> rest of day (12-08)", D["first"], D.rest),
                   ("20:00 4H (20-24) -> overnight (24-08)", D.ny, D.after_ny)):
    for lab, q in (("all days", None), ("big candles (top 20% moves)", 0.8)):
        a, r, n = agree(x, y, q)
        rows.append({"question": name, "days": lab, "same direction %": a, "correlation": r, "coin-days": n})
slots = pd.DataFrame({"4H candle opening (SGT)": ["%02d:00" % s for s in V.index], "share of daily volume %": (V.values * 100).round(1),
                      "avg high-low range %": (Rg.values * 100).round(2)})
print(slots.to_string(index=False)); print(pd.DataFrame(rows).to_string(index=False))
write_report("intraday timing facts", [("Volume and range by 4H candle (SGT)", slots), ("Does an early candle set the direction?", pd.DataFrame(rows))])
