"""Universe atlas v2: element profiles for each coin in each Bitcoin state (PLAN.md steps 2-4).

    python3 studies/atlas2.py  -> results/<date>-element-atlas.md, results/atlas2-coins.csv, data/atlas2_events.pkl

Every event is tagged with the Bitcoin state of the last COMPLETED day (no look-ahead), so the same event tables can
be reused for strategy tests in step 5.
"""
import os

from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import config
from lib.btcstate import label
from lib.data import load_1h, load_metrics, resample
from lib.indicators import atr
from lib.tags import COIN_NICHE

DAY, H = 24 * 3600_000, 3600_000
A0 = int(pd.Timestamp(config.EVAL_START, tz="UTC").timestamp() * 1000)
STATES = ["STRONG_DOWN", "DOWN", "COIL", "RANGE", "UP", "STRONG_UP"]
ST = label(resample(load_1h("BTC"), 24))
state_of = lambda t: ST.state.reindex((np.asarray(t) // DAY * DAY) - DAY).values   # last completed day

D4, DD = {}, {}
for c in config.COINS:
    df = load_1h(c)
    D4[c], DD[c] = resample(df, 4), resample(df, 24)
btc_d = DD["BTC"].set_index("t").c.pct_change()
btc_4 = D4["BTC"].set_index("t").c.pct_change()


def ev_coin(c):
    b = D4[c]
    t, o, h, l, cl = (b[k].values for k in ("t", "o", "h", "l", "c"))
    A = atr(b)
    n = len(cl)
    tc = t + 4 * H                                            # bar close time
    out = {k: [] for k in ("E2", "E3", "E4", "E5", "E6")}
    # E2 reversal: consecutive 4h returns
    r = np.r_[np.nan, cl[1:] / cl[:-1] - 1]
    for i in range(1, n - 1):
        out["E2"].append((tc[i], r[i], r[i + 1]))
    # E3 squeeze release / E4 displacement / E6 sweeps (next 6 bars = 24h)
    s = pd.Series(cl)
    bw = (4 * s.rolling(20).std() / s.rolling(20).mean()).values
    bwmin = pd.Series(bw).rolling(120).min().values
    hi20 = pd.Series(h).rolling(20).max().shift(1).values
    lo20 = pd.Series(l).rolling(20).min().shift(1).values
    for i in range(130, n - 6):
        a = A[i - 1]
        if not a > 0:
            continue
        if bw[i] <= bwmin[i] * 1.0001:
            out["E3"].append((tc[i], (h[i + 1:i + 7].max() - l[i + 1:i + 7].min()) / a))
        body = cl[i] - o[i]
        if abs(body) >= 2 * a:
            out["E4"].append((tc[i], np.sign(body) * (cl[i + 6] - cl[i]) / a))
        if h[i] > hi20[i] and cl[i] < hi20[i]:
            out["E6"].append((tc[i], (cl[i] - cl[i + 6]) / a))
        if l[i] < lo20[i] and cl[i] > lo20[i]:
            out["E6"].append((tc[i], (cl[i + 6] - cl[i]) / a))
    # E5 big legs (>= 6 ATR within 30 bars), confirmed by a 1-ATR pullback from the extreme
    for side in (1, -1):
        i, cool = 40, 0
        while i < n - 2:
            a = A[i]
            if i < cool or not a > 0:
                i += 1
                continue
            if side == 1:
                j0 = i - 30 + int(np.argmin(l[i - 30:i + 1]))
                start, ext = l[j0], h[i]
                fresh = h[i] >= h[i - 30:i].max()
            else:
                j0 = i - 30 + int(np.argmax(h[i - 30:i + 1]))
                start, ext = h[j0], l[i]
                fresh = l[i] <= l[i - 30:i].min()
            if not (fresh and abs(ext - start) >= 6 * a):
                i += 1
                continue
            k = i                                             # extend while new extremes come; confirm on 1-ATR pullback
            while k < n - 1:
                k += 1
                if side == 1 and h[k] > ext:
                    ext = h[k]
                elif side == -1 and l[k] < ext:
                    ext = l[k]
                elif (ext - cl[k]) * side >= A[k]:
                    break
            leg = abs(ext - start)
            half, deep = ext - side * 0.5 * leg, ext - side * 0.786 * leg
            hit50, bars50, cont, m = False, np.nan, np.nan, k
            while m < min(n - 1, k + 60):
                m += 1
                if (side == 1 and h[m] > ext) or (side == -1 and l[m] < ext):
                    break                                     # continued without a 50% pullback
                if (side == 1 and l[m] <= half) or (side == -1 and h[m] >= half):
                    hit50, bars50 = True, m - k
                    cont = 0.0
                    for q in range(m, min(n, m + 60)):
                        if (side == 1 and l[q] <= deep) or (side == -1 and h[q] >= deep):
                            break
                        if (side == 1 and h[q] > ext) or (side == -1 and l[q] < ext):
                            cont = 1.0
                            break
                    break
            out["E5"].append((tc[k], side, leg / a, hit50, bars50, cont))
            cool = m + 1
            i = k + 1
    frames = {
        "E2": pd.DataFrame(out["E2"], columns=["t", "r", "r_next"]),
        "E3": pd.DataFrame(out["E3"], columns=["t", "release_atr"]),
        "E4": pd.DataFrame(out["E4"], columns=["t", "follow_atr"]),
        "E5": pd.DataFrame(out["E5"], columns=["t", "side", "leg_atr", "hit50", "bars50", "cont"]),
        "E6": pd.DataFrame(out["E6"], columns=["t", "reversal_atr"]),
    }
    # E1 momentum (daily) and E7 BTC link (daily returns)
    d = DD[c].set_index("t").c
    p7 = d.pct_change(7)
    nx = d.pct_change().shift(-1)
    e1 = pd.DataFrame({"t": d.index + DAY, "hit": (np.sign(nx) == np.sign(p7)).astype(float),
                       "edge": nx * np.sign(p7)}).dropna()
    frames["E1"] = e1
    rd = d.pct_change()
    frames["E7"] = pd.DataFrame({"t": rd.index + DAY, "r": rd.values, "rb": btc_d.reindex(rd.index).values}).dropna()
    # E8 crowd: weekly crowd score vs next week's return
    m = load_metrics(c).set_index("t").global_ls.reindex(d.index)
    z = m.rolling(7, min_periods=5).mean() / m.rolling(90, min_periods=60).mean() - 1
    wk = pd.to_datetime(d.index, unit="ms").weekday == 6
    nwk = d.shift(-7) / d - 1
    frames["E8"] = pd.DataFrame({"t": d.index[wk] + DAY, "z": z[wk].values, "next_week": nwk[wk].values}).dropna()
    for k, f in frames.items():
        f["coin"] = c
        f.query("t >= @A0", inplace=True)
        f["state"] = state_of(f.t.values)
    return frames


EV = {}
for c in config.COINS:
    for k, f in ev_coin(c).items():
        EV.setdefault(k, []).append(f)
EV = {k: pd.concat(v, ignore_index=True) for k, v in EV.items()}
pd.to_pickle(EV, os.path.join(config.DATA, "atlas2_events.pkl"))


def beta(y, x):
    return np.cov(y, x)[0, 1] / x.var() if len(x) > 20 and x.var() > 0 else np.nan


def metrics(sub):
    """One row of element metrics from event subsets (dict of DataFrames already filtered)."""
    e = {}
    x = sub["E1"]; e["E1 momentum hit-50%"] = (x.hit.mean() - 0.5) * 100 if len(x) >= 30 else np.nan
    x = sub["E2"]; e["E2 reversal (-autocorr)"] = -x.r.corr(x.r_next) if len(x) >= 100 else np.nan
    x = sub["E7"]; e["E3 vol vs BTC"] = x.r.std() / x.rb.std() if len(x) >= 30 else np.nan
    x = sub["E3"]; e["E3 squeeze release (ATR)"] = x.release_atr.mean() if len(x) >= 10 else np.nan
    x = sub["E4"]; e["E4 displacement follow (ATR)"] = x.follow_atr.mean() if len(x) >= 10 else np.nan
    x = sub["E5"]
    e["E5 P(50% pullback)"] = x.hit50.mean() if len(x) >= 8 else np.nan
    e["E5 days to 50%"] = x.bars50.median() / 6 if x.hit50.sum() >= 5 else np.nan
    e["E5 P(continue after 50%)"] = x.cont.mean() if x.cont.notna().sum() >= 5 else np.nan
    x = sub["E6"]; e["E6 sweep reversal (ATR)"] = x.reversal_atr.mean() if len(x) >= 10 else np.nan
    x = sub["E7"]
    up, dn = x[x.rb > 0], x[x.rb < 0]
    e["E7 beta up"] = beta(up.r.values, up.rb.values)
    e["E7 beta down"] = beta(dn.r.values, dn.rb.values)
    e["E7 corr"] = x.r.corr(x.rb) if len(x) >= 30 else np.nan
    x = sub["E8"]; e["E8 crowd fade (-corr)"] = -x.z.corr(x.next_week) if len(x) >= 15 else np.nan
    return e


ELEMS = list(metrics({k: v.iloc[:0] for k, v in EV.items()}).keys())


def table(mask_fn):
    return {k: v[mask_fn(v)] for k, v in EV.items()}


# per coin (all states)
coin_rows = {c: metrics(table(lambda v, c=c: v.coin == c)) for c in config.COINS}
CT = pd.DataFrame(coin_rows).T

# memory test: 90-day windows, rank correlation across coins between consecutive windows
win = lambda t: (t - A0) // (90 * DAY)
nwin = int(win(max(v.t.max() for v in EV.values()))) + 1
per_win = {}
for w in range(nwin):
    per_win[w] = pd.DataFrame({c: metrics(table(lambda v, c=c, w=w: (v.coin == c) & (win(v.t) == w)))
                               for c in config.COINS}).T
mem = []
for el in ELEMS:
    rs = [per_win[w][el].astype(float).corr(per_win[w + 1][el].astype(float), method="spearman")
          for w in range(nwin - 1) if per_win[w][el].notna().sum() >= 20 and per_win[w + 1][el].notna().sum() >= 20]
    rs = [x for x in rs if not np.isnan(x)]
    mem.append({"element": el, "window pairs": len(rs), "avg rank corr 90d -> next 90d": round(np.mean(rs), 2) if rs else None,
                "share of pairs > 0": "%d/%d" % (sum(x > 0 for x in rs), len(rs))})
MEM = pd.DataFrame(mem)
stable = [r["element"] for r in mem if (r["avg rank corr 90d -> next 90d"] or 0) >= 0.3]

# groups from stable elements only
X = CT[stable].astype(float)
X = X.fillna(X.median())
Z = (X - X.mean()) / X.std()
best = None
for k in range(3, 7):
    km = KMeans(k, n_init=50, random_state=7).fit(Z)
    sc = silhouette_score(Z, km.labels_)
    if best is None or sc > best[1]:
        best = (k, sc, km)
k, sil, km = best
CT["group"] = ["G%d" % i for i in km.labels_]
CT["niche"] = pd.Series(COIN_NICHE)
qv = pd.Series({c: (DD[c].v * DD[c].c).median() for c in config.COINS})
CT["size tier"] = pd.qcut(qv.rank(method="first"), 3, labels=["small", "mid", "large"]).astype(str)
cent = pd.DataFrame(km.cluster_centers_, columns=stable, index=["G%d" % i for i in range(k)])


def describe(row):
    words = []
    for el, v in row.items():
        if abs(v) >= 0.6:
            words.append(("high " if v > 0 else "low ") + el.split(" ", 1)[1])
    return "; ".join(words) or "average on all stable elements"


grp = pd.DataFrame({"group": cent.index, "profile (vs the 72-coin average)": cent.apply(describe, axis=1).values,
                    "members": [", ".join(sorted(CT.index[CT.group == g])) for g in cent.index]})

# group x BTC state tables for the key elements
def by_state(keycol):
    rows = []
    for g in sorted(CT[keycol].unique()):
        coins = list(CT.index[CT[keycol] == g])
        for s_ in STATES:
            m = metrics(table(lambda v, coins=coins, s_=s_: v.coin.isin(coins) & (v.state == s_)))
            rows.append({keycol: g, "BTC state": s_, **m})
    return pd.DataFrame(rows)


BS_G = by_state("group")
BS_T = by_state("size tier")
key = ["E1 momentum hit-50%", "E4 displacement follow (ATR)", "E5 P(50% pullback)", "E5 days to 50%",
       "E5 P(continue after 50%)", "E6 sweep reversal (ATR)", "E7 beta down", "E8 crowd fade (-corr)"]


def pivot(df, keycol, el):
    p = df.pivot_table(index=keycol, columns="BTC state", values=el)[STATES].round(2)
    p.insert(0, keycol, p.index)
    return p


CT.round(3).to_csv(os.path.join(config.RESULTS, "atlas2-coins.csv"))
cross = pd.crosstab(CT.niche, CT.group); cross.insert(0, "niche", cross.index)
sections = [
    ("How to read this", "Elements (PLAN.md): E1 momentum = how often the next day follows the past week's direction, "
     "in points above 50%. E2 reversal = minus the autocorrelation of 4h returns. E4 / E6 = average move over the next "
     "24h in ATR units after a 2-ATR candle / a sweep that closes back inside. E5 = big legs (>= 6 ATR within 5 days): "
     "chance of a 50% pullback before a new extreme, days to reach it, and chance of a new extreme after it (before "
     "the 78.6% level). E7 = BTC beta on BTC up / down days. E8 = minus the correlation between crowd long-bias and "
     "the next week's return (positive = fading the crowd works). States are the last completed day's BTC state."),
    ("Step 3. Memory test: which elements are stable coin traits?", MEM),
    ("Step 4. Groups from the stable elements (%s), k = %d, silhouette %.2f" % (", ".join(stable), k, sil), grp),
    ("Groups vs niche tags", cross)]
for el in key:
    sections.append(("By group x BTC state: " + el, pivot(BS_G, "group", el)))
for el in ("E5 P(50% pullback)", "E5 days to 50%", "E7 beta down"):
    sections.append(("By size tier x BTC state: " + el, pivot(BS_T, "size tier", el)))
write_report("element atlas", sections)
