"""Step 5: strategies by coin group x Bitcoin state, validated on HELD-OUT Bitcoin episodes (not by date).

Episodes = runs of consecutive days in the same BTC state (lib/btcstate.py, last completed day). Within each state the
episodes are dealt into 5 folds in turn. For each fold, cells (strategy+side x [state] x [group]) are switched on when
their average R on the other 4 folds is > 0.10 with >= 30 trades, then scored on the held-out fold.
    python3 studies/episodes.py
"""
import os

from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd

import config
from lib.btcstate import label
from lib.data import load_1h, resample

DAY = 24 * 3600_000
STATES = ["STRONG_DOWN", "DOWN", "COIL", "RANGE", "UP", "STRONG_UP"]
MIN_R, MIN_N, K = 0.10, 30, 5

ST = label(resample(load_1h("BTC"), 24))
s = ST.state.dropna()
ep = (s != s.shift()).cumsum()
eps = pd.DataFrame({"state": s, "ep": ep})
first = eps.groupby("ep").agg(state=("state", "first"), start=("state", lambda x: x.index[0]), days=("state", "size"))
first["fold"] = first.groupby("state").cumcount() % K
eps["fold"] = eps.ep.map(first.fold)

d = pd.read_pickle(os.path.join(config.DATA, "trades.pkl"))
d = d[d.t_sig >= int(pd.Timestamp(config.EVAL_START, tz="UTC").timestamp() * 1000)].copy()
day = d.t_sig // DAY * DAY - DAY                               # last completed day at the signal
d["state"] = eps.state.reindex(day.values).values
d["fold"] = eps.fold.reindex(day.values).values
d["episode"] = eps.ep.reindex(day.values).values
CT = pd.read_csv(os.path.join(config.RESULTS, "atlas2-coins.csv"), index_col=0)
d["group"] = d.coin.map(CT.group)
d["leg"] = d.strat + np.where(d.side == 1, " long", " short")
d = d[d.state.notna() & d.group.notna()]

ROUTERS = {"take everything": [], "strategy only": ["leg"], "+ BTC state": ["leg", "state"],
           "+ coin group": ["leg", "group"], "+ state + group": ["leg", "state", "group"]}


def cv(keys, data=d):
    res = []
    for f in range(K):
        tr, te = data[data.fold != f], data[data.fold == f]
        if keys:
            g = tr.groupby(keys).r.agg(["size", "mean"])
            on = g[(g["size"] >= MIN_N) & (g["mean"] > MIN_R)].index
            idx = pd.MultiIndex.from_frame(te[keys]) if len(keys) > 1 else pd.Index(te[keys[0]])
            te = te[idx.isin(on)]
        res.append(te.assign(cvfold=f))
    return pd.concat(res)


def summary(x):
    by = x.groupby("cvfold").r.mean()
    ep_mean = x.groupby("episode").r.mean()
    return {"trades": len(x), "avg R": round(x.r.mean(), 3), "folds +": "%d/%d" % ((by > 0).sum(), K),
            "by fold": " ".join("%+.2f" % v for v in by.values),
            "episodes +": "%d/%d" % ((ep_mean > 0).sum(), len(ep_mean)),
            "pass": "PASS" if x.r.mean() > 0.05 and (by > 0).sum() >= 4 else "fail"}


rows = [{"router": n, **summary(cv(k))} for n, k in ROUTERS.items()]
# per strategy: does routing by state + group help each one?
per = []
for leg, x in d.groupby("leg"):
    r0, r1 = cv([], x), cv(["state", "group"], x)
    per.append({"strategy": leg, "all trades avg R": round(x.r.mean(), 3),
                "routed (out of episode) avg R": round(r1.r.mean(), 3) if len(r1) else None,
                "routed trades": len(r1), "routed folds +": "%d/%d" % ((r1.groupby("cvfold").r.mean() > 0).sum(), K) if len(r1) else ""})
# SW50 map: avg R by state x group, all data
sw = d[d.strat == "SW50"]
swmap = sw.pivot_table(index="group", columns="state", values="r", aggfunc="mean")[STATES].round(2)
swn = sw.pivot_table(index="group", columns="state", values="r", aggfunc="size")[STATES]
swmap.insert(0, "group", swmap.index); swn.insert(0, "group", swn.index)
swdir = sw.assign(direction=np.where(sw.side == 1, "long", "short")).pivot_table(
    index="direction", columns="state", values="r", aggfunc="mean")[STATES].round(2)
swdir.insert(0, "direction", swdir.index)
# current map: cells on using ALL episodes (what a live router would use today)
g = d.groupby(["leg", "state", "group"]).r.agg(["size", "mean"])
live = g[(g["size"] >= MIN_N) & (g["mean"] > MIN_R)].reset_index().sort_values(["state", "mean"], ascending=[True, False])
live["mean"] = live["mean"].round(2)
live.columns = ["strategy", "BTC state", "coin group", "trades", "avg R"]
ep_tbl = first.groupby("state").agg(episodes=("days", "size"), days=("days", "sum"), longest=("days", "max")).reindex(STATES)
ep_tbl.insert(0, "BTC state", ep_tbl.index)
write_report("step 5 held-out episodes", [
    ("Method", "Trades from every strategy in data/trades.pkl (incl. SW50), signals since 2023-11-20, tagged with the "
     "last completed day's BTC state and the coin's atlas group. Cells switched on when avg R > 0.10 with >= 30 trades "
     "on 4 folds of episodes, scored on the 5th. Pass: avg R > 0.05 and >= 4/5 folds positive."),
    ("BTC episodes", ep_tbl),
    ("Routers (out of episode)", pd.DataFrame(rows)),
    ("Each strategy: all trades vs routed by state + group (out of episode)", pd.DataFrame(per)),
    ("SW50 avg R by group x BTC state (all data)", swmap), ("SW50 trade counts", swn),
    ("SW50 avg R by direction x BTC state", swdir),
    ("Cells a live router would switch on today (all episodes)", live)])
