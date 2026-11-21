"""CF4H: crowd positioning on the 4H clock (pre-registered in LEDGER.md).

At each 4H close at 08/12/16/20 SGT (00/04/08/12 UTC): score = global long/short ratio, mean of the last 6 4h bars /
mean of the last 84 bars - 1. Long the lowest-scored coin, short the highest (one position per coin). Entry at the next
4H open; stop 3 x ATR(14, 4h), skipped if > 15% away; take-profit 2R; time exit 48h; 1h execution, stop first.
    python3 studies/cf4h.py          -> data/cf4h_candidates.pkl (ranked candidates per signal time, with trade marks)
"""
import os
import sys

from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd

import config
from lib.data import load_1h, load_metrics4h, resample
from lib.indicators import atr

H, DAY = 3600_000, 24 * 3600_000
COST = config.FEE_PER_SIDE + config.SLIP_PER_SIDE
SIGNAL_UTC_CLOSE_HOURS = {0, 4, 8, 12}                    # = 08 / 12 / 16 / 20 SGT
START = int(pd.Timestamp(config.EVAL_START, tz="UTC").timestamp() * 1000)
SPLIT = int(pd.Timestamp(config.SPLIT, tz="UTC").timestamp() * 1000)
RANKS = 3                                                  # keep the top 3 per side per signal (for slot fallbacks)


def coin_frames(coin):
    df = load_1h(coin)
    b = resample(df, 4).set_index("t")
    b["atr"] = atr(b.reset_index())
    m = load_metrics4h(coin).set_index("t").global_ls.reindex(b.index)
    s = m.rolling(6, min_periods=5).mean() / m.rolling(84, min_periods=60).mean() - 1
    b["score"] = s
    b["age"] = np.arange(len(b))
    return df, b


def trade(h1, t_entry, side, stop_dist, max_h=48, target_r=2.0):
    T = h1["t"]
    i = int(np.searchsorted(T, t_entry))
    if i >= len(T) or T[i] != t_entry:
        return None
    entry = h1["o"][i]
    stop, tp = entry - side * stop_dist, entry + side * target_r * stop_dist
    R = lambda px: ((px - entry) * side - COST * (entry + px)) / stop_dist
    ts, mc, mw = [], [], []
    for k in range(0, max_h + 1):
        j = i + k
        if j >= len(T):
            return None
        o, hh, ll, cc = h1["o"][j], h1["h"][j], h1["l"][j], h1["c"][j]
        px = None
        if k == max_h:
            px = o
        elif (side == 1 and ll <= stop) or (side == -1 and hh >= stop):
            px = min(stop, o) if side == 1 else max(stop, o)
        elif k > 0 and ((side == 1 and hh >= tp) or (side == -1 and ll <= tp)):
            px = max(tp, o) if side == 1 else min(tp, o)
        if px is not None:
            r = R(px)
            ts.append(T[j]); mc.append(r); mw.append(r)
            return r, int(T[j]), pd.DataFrame({"close_R": mc, "worst_R": mw}, index=ts)
        adverse = ll if side == 1 else hh
        ts.append(T[j]); mc.append(R(cc)); mw.append(R(adverse))
    return None


def build():
    frames = {c: coin_frames(c) for c in config.COINS}
    S = pd.DataFrame({c: f[1].score for c, f in frames.items()})
    AGE = pd.DataFrame({c: f[1].age for c, f in frames.items()}).reindex(S.index)
    A = pd.DataFrame({c: f[1].atr for c, f in frames.items()}).reindex(S.index)
    C = pd.DataFrame({c: f[1].c for c, f in frames.items()}).reindex(S.index)
    h1 = {c: {k: f[0][k].values for k in ("t", "o", "h", "l", "c")} for c, f in frames.items()}
    rows = []
    for t in S.index:
        t_close = int(t) + 4 * H
        if t_close < START or (t_close // H) % 24 not in SIGNAL_UTC_CLOSE_HOURS:
            continue
        s = S.loc[t][(AGE.loc[t] >= 720)].dropna()
        stop_pct = (3 * A.loc[t] / C.loc[t]).reindex(s.index)
        s = s[stop_pct <= 0.15]
        if len(s) < 20:
            continue
        s = s.sort_values()
        for side, picks in ((1, s.index[:RANKS]), (-1, s.index[::-1][:RANKS])):
            for rank, coin in enumerate(picks, 1):
                res = trade(h1[coin], t_close, side, 3 * A.at[t, coin])
                if res:
                    rows.append({"t": t_close, "coin": coin, "side": side, "rank": rank, "r": res[0], "t_out": res[1],
                                 "stop_pct": float(stop_pct[coin]), "marks": res[2]})
    return pd.DataFrame(rows)


def stats(x):
    w = x.groupby(x.t // (7 * DAY)).r.mean()
    return {"trades": len(x), "avg R": round(x.r.mean(), 3), "win %": round((x.r > 0).mean() * 100),
            "weekly Sharpe": round(w.mean() / w.std() * np.sqrt(52), 2) if w.std() > 0 else None}


if __name__ == "__main__":
    X = build()
    X.to_pickle(os.path.join(config.DATA, "cf4h_candidates.pkl"))
    top = X[X["rank"] == 1]
    # standalone: one position per coin at a time (skip a signal if that coin is still open)
    keep, open_until = [], {}
    for r in top.sort_values("t").itertuples():
        if open_until.get(r.coin, 0) > r.t:
            continue
        keep.append(r.Index)
        open_until[r.coin] = r.t_out
    T = top.loc[keep]
    rows = []
    for per, x in (("old", T[T.t < SPLIT]), ("12m", T[T.t >= SPLIT])):
        for side, y in (("both", x), ("long", x[x.side == 1]), ("short", x[x.side == -1])):
            c = y.groupby("coin").r.sum().sort_values()
            rows.append({"period": per, "side": side, **stats(y), "sum R w/o best 3 coins": round(c.sum() - c.tail(3).sum(), 1)})
    R = pd.DataFrame(rows)
    ok = all((R[(R.side == "both")]["avg R"] > 0)) and all(R[(R.side == "both")]["weekly Sharpe"] >= 0.5) and \
        all(R[(R.side == "both")]["sum R w/o best 3 coins"] > 0)
    print(R.to_string(index=False)); print("VERDICT:", "PASS" if ok else "fail")
    write_report("cf4h standalone", [("Rule", __doc__.split("\n\n")[1]), ("Results", R),
                                     ("Verdict", "PASS" if ok else "fail")])
