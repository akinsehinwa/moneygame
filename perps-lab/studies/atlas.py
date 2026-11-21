"""Universe atlas: how each of the 72 coins moves relative to Bitcoin, pooled by Bitcoin STATE rather than by date.

    python3 studies/atlas.py   -> results/<date>-universe-atlas.md, results/atlas-coins.csv

Sections
A. Bitcoin states: how often each occurs, before vs the last 12 months.
B. "Inch vs mile": coin weekly moves in each bucket of BTC's weekly move (by size tier and niche).
C. By BTC state: excess return vs BTC, beta, and 50%-retracement behaviour (by size tier, niche, cluster).
D. Day after each BTC daily CRT pattern: next-day moves by group.
E. Trait clusters (k-means on standardized traits) vs niche tags.
F. Stability: are the traits the same in the 2 older years and the last 12 months?
Descriptive only: no strategy is chosen here.
"""
import os

from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

import config
from lib.btcstate import label
from lib.data import load_1h, resample
from lib.indicators import atr
from lib.tags import COIN_NICHE

DAY, H = 24 * 3600_000, 3600_000
ms = lambda s: int(pd.Timestamp(s, tz="UTC").timestamp() * 1000)
A0, SPLIT = ms(config.EVAL_START), ms(config.SPLIT)
STATES = ["STRONG_DOWN", "DOWN", "COIL", "RANGE", "UP", "STRONG_UP"]

# ---------------------------------------------------------------- data
daily, four = {}, {}
for c in config.COINS:
    df = load_1h(c)
    daily[c] = resample(df, 24).set_index("t")
    four[c] = resample(df, 4).set_index("t")
btcd = resample(load_1h("BTC"), 24)
ST = label(btcd)
Cd = pd.DataFrame({c: daily[c].c for c in config.COINS}).sort_index()
Rd = Cd.pct_change(fill_method=None)
Rd = Rd[Rd.index >= A0]
st = ST.reindex(Rd.index)
QV = pd.DataFrame({c: daily[c].v * daily[c].c for c in config.COINS}).reindex(Rd.index)
rb = Rd["BTC"]

# size tier from median daily quote volume (proxy for market cap), terciles
liq = QV.median()
tier = pd.Series(pd.qcut(liq.rank(method="first"), 3, labels=["small", "mid", "large"]), index=liq.index).astype(str)
niche = pd.Series(COIN_NICHE)


def beta(y, x):
    m = y.notna() & x.notna()
    if m.sum() < 20 or x[m].var() == 0:
        return np.nan
    return np.cov(y[m], x[m])[0, 1] / x[m].var()


# ---------------------------------------------------------------- retracement legs (4h zigzag, 2 x ATR)
def legs(coin):
    b = four[coin]
    b = b[b.index >= A0 - 30 * DAY]
    h, l, c, t = b.h.values, b.l.values, b.c.values, b.index.values
    a = atr(b.reset_index())
    piv, d = [], 0
    hi, hi_i, lo, lo_i = h[0], 0, l[0], 0
    for i in range(1, len(c)):
        th = 2 * a[i]
        if d == 0:                                   # undecided: wait for the first 2-ATR move
            if h[i] > hi: hi, hi_i = h[i], i
            if l[i] < lo: lo, lo_i = l[i], i
            if hi - l[i] >= th and hi_i < i:
                piv.append((hi_i, hi, 1)); d, lo, lo_i = -1, l[i], i
            elif h[i] - lo >= th and lo_i < i:
                piv.append((lo_i, lo, -1)); d, hi, hi_i = 1, h[i], i
        elif d == 1:                                 # in an up-leg: track the high
            if h[i] > hi:
                hi, hi_i = h[i], i
            elif hi - l[i] >= th:
                piv.append((hi_i, hi, 1)); d, lo, lo_i = -1, l[i], i
        else:                                        # in a down-leg: track the low
            if l[i] < lo:
                lo, lo_i = l[i], i
            elif h[i] - lo >= th:
                piv.append((lo_i, lo, -1)); d, hi, hi_i = 1, h[i], i
    out = []
    for k in range(1, len(piv) - 1):
        (i0, p0, _), (i1, p1, s1), (i2, p2, _) = piv[k - 1], piv[k], piv[k + 1]
        leg = abs(p1 - p0)
        if leg <= 0:
            continue
        depth = abs(p2 - p1) / leg
        half = p1 - (p1 - p0) * 0.5                      # 50% retracement level of the leg
        j = i1 + 1
        hit = None
        while j <= i2:
            if (s1 == 1 and l[j] <= half) or (s1 == -1 and h[j] >= half):
                hit = j - i1
                break
            j += 1
        out.append({"coin": coin, "t_end": int(t[i1]), "dir": "up" if s1 == 1 else "down", "leg_pct": leg / p0,
                    "depth": depth, "ret50": depth >= 0.5, "bars_to_50": hit, "counter_bars": i2 - i1})
    return out


L = pd.DataFrame([x for c in config.COINS for x in legs(c)])
L = L[L.t_end >= A0]
L["day"] = L.t_end // DAY * DAY
L["state"] = ST.state.reindex(L.day.values).values
L["tier"], L["niche"] = L.coin.map(tier), L.coin.map(niche)


# ---------------------------------------------------------------- per-coin traits
def traits(mask_days, mask_legs):
    rows = {}
    R, s = Rd[mask_days], st[mask_days]
    b_ = R["BTC"]
    f4 = {}
    for c in config.COINS:
        y = R[c]
        if y.notna().sum() < 60:
            continue
        up, dn = b_ > 0, b_ < 0
        lg = L[(L.coin == c) & mask_legs(L)]
        r = {"beta_up": beta(y[up], b_[up]), "beta_down": beta(y[dn], b_[dn]), "corr": y.corr(b_),
             "vol_ratio": y.std() / b_.std(),
             "retr50_p": lg.ret50.mean() if len(lg) >= 10 else np.nan,
             "retr_depth": lg.depth.median() if len(lg) >= 10 else np.nan}
        for grp, sts in (("down", ["STRONG_DOWN", "DOWN"]), ("up", ["STRONG_UP", "UP"]), ("flat", ["RANGE", "COIL"])):
            m = s.state.isin(sts) & y.notna()
            r["excess_" + grp] = (y[m] - b_[m]).mean() * 365 if m.sum() >= 15 else np.nan
        # lag: does the coin follow BTC with a 4h delay?
        x4 = four[c].c.pct_change(fill_method=None)
        bb = four["BTC"].c.pct_change(fill_method=None).reindex(x4.index)
        sel = x4.index.isin(np.concatenate([np.arange(d, d + DAY, 4 * H) for d in R.index[y.notna()]]))
        r["lag4h_corr"] = x4[sel].corr(bb.shift(1)[sel])
        rows[c] = r
    return pd.DataFrame(rows).T


T_all = traits(Rd.index >= A0, lambda x: x.t_end >= A0)
T_all["tier"], T_all["niche"], T_all["liq_musd"] = tier, niche, (liq / 1e6).round(1)
FEATS = ["beta_up", "beta_down", "corr", "vol_ratio", "retr50_p", "retr_depth", "excess_down", "excess_up",
         "excess_flat", "lag4h_corr"]

# ---------------------------------------------------------------- clusters
X = T_all[FEATS].astype(float)
X = X.fillna(X.median())
Z = (X - X.mean()) / X.std()
best = None
for k in range(3, 8):
    km = KMeans(k, n_init=50, random_state=7).fit(Z)
    sc = silhouette_score(Z, km.labels_)
    if best is None or sc > best[1]:
        best = (k, sc, km)
k, sil, km = best
T_all["cluster"] = ["C%d" % x for x in km.labels_]
cent = pd.DataFrame(km.cluster_centers_, columns=FEATS, index=["C%d" % i for i in range(k)])


def name(row):
    tags = []
    if row.beta_down > 0.5: tags.append("falls harder than BTC")
    if row.beta_down < -0.5: tags.append("falls less than BTC")
    if row.beta_up > 0.5: tags.append("rises more than BTC")
    if row["corr"] < -0.5: tags.append("loosely tied to BTC")
    if row["corr"] > 0.5: tags.append("tightly tied to BTC")
    if row.retr50_p > 0.5: tags.append("retraces deep often")
    if row.retr50_p < -0.5: tags.append("rarely retraces 50%")
    if row.excess_down < -0.5: tags.append("lags in BTC falls")
    if row.excess_down > 0.5: tags.append("holds up in BTC falls")
    if row.excess_up > 0.5: tags.append("leads in BTC rises")
    if row.vol_ratio > 0.5: tags.append("very volatile")
    return ", ".join(tags) or "average"


cent["profile"] = cent.apply(name, axis=1)
members = T_all.groupby("cluster").apply(lambda x: ", ".join(sorted(x.index)), include_groups=False)

# ---------------------------------------------------------------- B. inch vs mile (weekly buckets)
wk = (1 + Rd).groupby(pd.to_datetime(Rd.index, unit="ms").to_period("W-SUN")).prod() - 1
bucket = pd.cut(wk["BTC"], [-1, -0.07, -0.02, 0.02, 0.07, 10], labels=["BTC <-7%", "-7..-2%", "-2..+2%", "+2..+7%", "BTC >+7%"])
inch = []
for grpname, keyser in (("size tier", tier), ("niche", niche), ("cluster", T_all.cluster)):
    for g, coins in keyser.groupby(keyser).groups.items():
        row = {"group by": grpname, "group": g, "coins": len(coins)}
        for bk in bucket.cat.categories:
            m = bucket == bk
            row[bk] = "%+.1f%%" % (wk.loc[m, list(coins)].stack().median() * 100)
        inch.append(row)
inch = pd.DataFrame(inch)
btc_row = {"group by": "reference", "group": "BTC itself", "coins": 1}
for bk in bucket.cat.categories:
    btc_row[bk] = "%+.1f%%" % (wk.loc[bucket == bk, "BTC"].median() * 100)
inch = pd.concat([pd.DataFrame([btc_row]), inch], ignore_index=True)

# ---------------------------------------------------------------- C. by BTC state
bystate = []
for grpname, keyser in (("size tier", tier), ("cluster", T_all.cluster), ("niche", niche)):
    for g, coins in keyser.groupby(keyser).groups.items():
        coins = [c for c in coins if c != "BTC"]
        if not coins:
            continue
        for s_ in STATES:
            m = (st.state == s_).values
            ex = Rd.loc[m, coins].sub(Rd.loc[m, "BTC"], axis=0).stack()
            lg = L[(L.coin.isin(coins)) & (L.state == s_)]
            bystate.append({"group by": grpname, "group": g, "BTC state": s_, "days": int(m.sum()),
                            "excess vs BTC %/day": round(ex.mean() * 100, 2),
                            "50% retrace prob": round(lg.ret50.mean(), 2) if len(lg) > 20 else None,
                            "median 4h bars to 50%": lg.bars_to_50.median() if len(lg) > 20 else None})
bystate = pd.DataFrame(bystate)
piv_ex = bystate.pivot_table(index=["group by", "group"], columns="BTC state", values="excess vs BTC %/day")[STATES]
piv_rt = bystate.pivot_table(index=["group by", "group"], columns="BTC state", values="50% retrace prob")[STATES]

# ---------------------------------------------------------------- D. day after BTC CRT patterns
nxt = Rd.shift(-1)
crt_rows = []
for pat in ["BULL_CRT", "BEAR_CRT", "BREAK_UP", "BREAK_DN", "INSIDE", "OUTSIDE"]:
    m = (st.crt == pat).values
    row = {"BTC pattern today": pat, "days": int(m.sum()), "BTC next day": "%+.2f%%" % (nxt.loc[m, "BTC"].mean() * 100)}
    for g, coins in tier.groupby(tier).groups.items():
        row[g + " caps next day"] = "%+.2f%%" % (nxt.loc[m, [c for c in coins if c != "BTC"]].stack().mean() * 100)
    crt_rows.append(row)
crt = pd.DataFrame(crt_rows)

# ---------------------------------------------------------------- F. stability (old vs last 12m)
T_old = traits(Rd.index < SPLIT, lambda x: x.t_end < SPLIT)
T_new = traits(Rd.index >= SPLIT, lambda x: x.t_end >= SPLIT)
both = T_old.index.intersection(T_new.index)
stab = pd.DataFrame([{"trait": f, "coins": len(both),
                      "rank correlation old vs 12m": round(T_old.loc[both, f].astype(float).corr(
                          T_new.loc[both, f].astype(float), method="spearman"), 2)} for f in FEATS])
Xo, Xn = T_old.loc[both, FEATS].astype(float), T_new.loc[both, FEATS].astype(float)
Xo, Xn = Xo.fillna(Xo.median()), Xn.fillna(Xn.median())
lo = KMeans(k, n_init=50, random_state=7).fit_predict((Xo - Xo.mean()) / Xo.std())
ln = KMeans(k, n_init=50, random_state=7).fit_predict((Xn - Xn.mean()) / Xn.std())
ari = adjusted_rand_score(lo, ln)

# ---------------------------------------------------------------- report
states_tbl = pd.DataFrame({"days (old 2y)": st[st.index < SPLIT].state.value_counts(),
                           "days (last 12m)": st[st.index >= SPLIT].state.value_counts()}).reindex(STATES).fillna(0).astype(int)
states_tbl.insert(0, "BTC state", states_tbl.index)
clu = cent[["profile"]].copy()
clu["members"] = members
clu.insert(0, "cluster", clu.index)
cross = pd.crosstab(T_all.niche, T_all.cluster)
cross.insert(0, "niche", cross.index)
pe = piv_ex.reset_index()
pr = piv_rt.reset_index()
T_all.round(3).to_csv(os.path.join(config.RESULTS, "atlas-coins.csv"))
write_report("universe atlas", [
    ("How to read this", "Every day since 2023-11-20 is labeled with Bitcoin's state (lib/btcstate.py) and days are "
     "pooled by state, not by date. 'Excess vs BTC' = coin daily return minus BTC's on the same day. Retracement = "
     "4h swings of 2 x ATR; '50% retrace prob' = share of swings whose counter-move reached half the leg. Size tier = "
     "terciles of median daily trading volume. Per-coin numbers: results/atlas-coins.csv."),
    ("A. Bitcoin states", states_tbl),
    ("B. Inch vs mile: median coin weekly move by BTC's weekly move", inch),
    ("C1. Excess return vs BTC (% per day) by BTC state", pe),
    ("C2. Probability that a swing retraces 50% by BTC state", pr),
    ("D. The day after each BTC daily CRT pattern (mean move)", crt),
    ("E. Trait clusters (k = %d, silhouette %.2f)" % (k, sil), clu),
    ("E2. Clusters vs niche tags (coin counts)", cross),
    ("F. Stability: same traits in the old 2 years and the last 12 months?",
     pd.concat([stab, pd.DataFrame([{"trait": "cluster membership (adjusted Rand, 1 = identical, 0 = random)",
                                     "coins": len(both), "rank correlation old vs 12m": round(ari, 2)}])]))])
