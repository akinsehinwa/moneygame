"""Basket strategies from "151 Trading Strategies" (Kakushadze & Serur 2018), direct ports and lateral adaptations
to crypto perps. Parameters are fixed here BEFORE running (pre-registered in LEDGER.md); one variant each.

    python3 studies/p151.py --list
    python3 studies/p151.py MOM            # one strategy -> results/<date>-p151-<name>.md
    python3 studies/p151.py ALL            # every strategy, one table

Pass rule (all): net Sharpe >= 0.5 in BOTH periods (old = 2023-11-20..2025-11-20, 12m = after), after
costs and funding. Long-only books must also beat the equal-weight long benchmark's Sharpe in both periods.
"""
import sys

from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd

import config
from lib import portfolio as pf

P = pf.build_panel()
C, R, F, QV = P["C"], P["R"], P["F"], P["QV"]
E = pf.eligible(P)
DAY = 24 * 3600_000
vol = lambda n: R.rolling(n, min_periods=int(n * 0.8)).std()
inv = lambda x: 1 / x.replace(0, np.nan)

# Sector map for the sector-rotation test (fixed before testing; rough by design).
SECTORS = {
    "pow_payments": ["BTC", "LTC", "BCH", "XMR", "ZEC"],
    "l1": ["ETH", "SOL", "BNB", "ADA", "AVAX", "TRX", "DOT", "ATOM", "NEAR", "APT", "SUI", "SEI", "ICP", "HBAR",
           "VET", "TIA", "INJ", "MINA", "CFX", "HYPE"],
    "l2_infra": ["ARB", "OP", "IMX", "LINEA", "STX", "FIL", "AR", "GRT", "ENS", "JASMY", "ORDI"],
    "defi": ["UNI", "LINK", "COMP", "LDO", "JUP", "PYTH", "JTO", "ENA", "PENDLE", "ETHFI", "ONDO", "ASTER", "WLFI"],
    "meme": ["DOGE", "SHIB", "PEPE", "FLOKI", "BONK", "WIF", "BOME", "BRETT", "TRUMP", "MELANIA", "PIPPIN", "PUMP"],
    "ai_gaming": ["FET", "TAO", "WLD", "VIRTUAL", "APE", "GALA", "BEAMX", "CHZ", "LIT", "RIVER"],
}

# FOMC decision days (second day of each meeting), Dec 2023 - Oct 2026.
FOMC = ["2023-12-13", "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18",
        "2024-11-07", "2024-12-18", "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30",
        "2025-09-17", "2025-10-29", "2025-12-10", "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17",
        "2026-07-29", "2026-09-16", "2026-10-28"]


def bench_ew():
    return pf.long_only(E, E), "W"


def bench_btc():
    W = pd.DataFrame(0.0, index=C.index, columns=C.columns)
    W["BTC"] = 1.0
    return W, "D"


# ------------------------------------------------------------------ direct ports

def MOM():
    """3.1 price momentum: risk-adjusted mean daily return over 60 days, skipping the last 7; top/bottom 7; 1/vol."""
    rm = R.shift(7).rolling(60, min_periods=50)
    score = rm.mean() / rm.std()
    return pf.long_short(score, E, 7, inv(vol(60))), "W"


def LOWVOL():
    """3.4 low-volatility anomaly: long the 7 lowest 90-day vol, short the 7 highest; rebalance every 4 weeks."""
    return pf.long_short(-vol(90), E, 7), "4W"


def RESMOM():
    """3.7 residual momentum: residuals vs BTC (beta over 90 days), risk-adjusted mean over 60 days skipping 7."""
    rb = R["BTC"]
    beta = R.rolling(90, min_periods=70).cov(rb).div(rb.rolling(90, min_periods=70).var(), axis=0).shift(7)
    res = R.sub(beta.mul(rb, axis=0))
    rm = res.shift(7).rolling(60, min_periods=50)
    score = (rm.mean() / rm.std()).drop(columns="BTC")
    return pf.long_short(score.reindex(columns=C.columns), E, 7), "W"


def CONTRA():
    """3.9 / 10.3 contrarian: w = -(7-day return - cross-sectional mean) / vol, gross 1, weekly."""
    r7 = C.pct_change(7, fill_method=None).where(E)
    dm = r7.sub(r7.mean(axis=1), axis=0)
    return pf.normalize_gross((-dm * inv(vol(30))).fillna(0.0)), "W"


def MA2():
    """3.12 two moving averages: SMA10 vs SMA30 on daily closes, long/short, weights sign/vol, gross 1."""
    s = np.sign(C.rolling(10).mean() - C.rolling(30).mean()).where(E)
    return pf.normalize_gross((s * inv(vol(30))).fillna(0.0)), "D"


def MA3():
    """3.13 three moving averages (3/10/21): enter when stacked, exit when the fast crosses the middle."""
    m1, m2, m3 = C.rolling(3).mean(), C.rolling(10).mean(), C.rolling(21).mean()
    st = np.zeros(C.shape)
    a1, a2, a3, e = m1.values, m2.values, m3.values, E.values
    for t in range(1, len(C)):
        prev = st[t - 1]
        cur = prev.copy()
        cur[(prev == 1) & (a1[t] <= a2[t])] = 0
        cur[(prev == -1) & (a1[t] >= a2[t])] = 0
        cur[(a1[t] > a2[t]) & (a2[t] > a3[t])] = 1
        cur[(a1[t] < a2[t]) & (a2[t] < a3[t])] = -1
        cur[~e[t]] = 0
        st[t] = cur
    s = pd.DataFrame(st, index=C.index, columns=C.columns)
    return pf.normalize_gross((s * inv(vol(30))).fillna(0.0)), "D"


def TSMOM():
    """10.4 time-series momentum: sign of the 30-day return / vol, gross 1, weekly."""
    s = np.sign(C.pct_change(30, fill_method=None)).where(E)
    return pf.normalize_gross((s * inv(vol(30))).fillna(0.0)), "W"


def CHANFADE():
    """3.15 channel: long at the 20-day low, short at the 20-day high (the paper's bounce version); hold until the
    opposite signal; weights sign/vol."""
    lo, hi = P["L"].rolling(20).min().shift(1), P["H"].rolling(20).max().shift(1)
    sig = pd.DataFrame(np.where(C <= lo, 1.0, np.where(C >= hi, -1.0, np.nan)), index=C.index, columns=C.columns)
    s = sig.ffill().where(E).fillna(0.0)
    return pf.normalize_gross(s * inv(vol(30)).fillna(0.0)), "D"


def DUALMOM():
    """4.1.1 + 4.1.2 dual momentum, long only: top 7 by 90-day return that are above their SMA100, only while BTC is
    above its SMA150; otherwise cash."""
    r90 = C.pct_change(90, fill_method=None)
    ok = E & (C > C.rolling(100).mean())
    rk = r90.where(ok).rank(axis=1, ascending=False, method="first")
    btc_up = C["BTC"] > C["BTC"].rolling(150).mean()
    W = pf.long_only(rk <= 7, E)
    return W.where(btc_up, 0.0), "W"


def TRENDLO():
    """4.6 multi-asset trend following, long only: coins with a positive 90-day return above their SMA150,
    weights proportional to return / variance, capped at 20%."""
    r90 = C.pct_change(90, fill_method=None)
    m = (r90 > 0) & (C > C.rolling(150).mean())
    return pf.long_only(m, E, scale=r90 / vol(90) ** 2, cap=0.2), "W"


def RSQ():
    """4.2 + 4.3 alpha and R-squared vs BTC (90 days): long low-R2 / high-alpha, short high-R2 / low-alpha (terciles)."""
    rb = R["BTC"]
    cov = R.rolling(90, min_periods=70).cov(rb)
    vb = rb.rolling(90, min_periods=70).var()
    beta = cov.div(vb, axis=0)
    alpha = R.rolling(90, min_periods=70).mean() - beta.mul(rb.rolling(90, min_periods=70).mean(), axis=0)
    r2 = (R.rolling(90, min_periods=70).corr(rb)) ** 2
    e = E.copy()
    e["BTC"] = False
    r2t = r2.where(e).rank(axis=1, pct=True)
    alt = alpha.where(e).rank(axis=1, pct=True)
    lw = ((r2t <= 1 / 3) & (alt >= 2 / 3)).astype(float)
    sw = ((r2t >= 2 / 3) & (alt <= 1 / 3)).astype(float)
    lw = lw.div(lw.sum(axis=1).where(lw.sum(axis=1) > 0), axis=0) * 0.5
    sw = sw.div(sw.sum(axis=1).where(sw.sum(axis=1) > 0), axis=0) * 0.5
    return (lw - sw).fillna(0.0), "W"


# ------------------------------------------------------------------ lateral adaptations

def CARRY():
    """5.11 / 8.2.1 / 9.1 carry -> funding: short the 7 highest 7-day funding, long the 7 lowest. Funding in PnL."""
    f7 = F.rolling(7, min_periods=5).sum()
    return pf.long_short(-f7, E & (F.abs().rolling(7).sum() > 0), 7), "W"


def MOMCARRY():
    """8.4 momentum & carry combo: 50/50 of the MOM and CARRY books."""
    return 0.5 * MOM()[0] + 0.5 * CARRY()[0], "W"


def DOLLARCARRY():
    """8.3 dollar carry -> market timing on average funding: long the equal-weight basket when the 7-day average
    funding across coins is below the 0.01%-per-8h baseline (forward discount positive), short it when above."""
    avg = F.where(E).rolling(7, min_periods=5).sum().mean(axis=1) / 7     # per day
    side = np.sign(0.0003 - avg)
    return pf.long_only(E, E).mul(side, axis=0), "W"


def SKEW():
    """9.5 skewness premium -> lottery effect: short the 7 most positively skewed coins (90-day daily returns), long
    the 7 least skewed."""
    sk = R.rolling(90, min_periods=70).skew()
    return pf.long_short(-sk, E, 7), "W"


def NEWLIST():
    """3.16 event-driven (IPO underperformance) -> new perp listings: short every coin first listed after
    2023-09-01 from day 7 to day 60 of its life; equal weight across those active; gross 1 short."""
    first = C.apply(lambda s: s.first_valid_index())
    cut = int(pd.Timestamp("2023-09-01", tz="UTC").timestamp() * 1000)
    new = first[first > cut].index
    age = P["AGE"][new]
    m = (age >= 7) & (age <= 60)
    W = pd.DataFrame(0.0, index=C.index, columns=C.columns)
    w = m.astype(float)
    W[new] = -w.div(w.sum(axis=1).where(w.sum(axis=1) > 0), axis=0).fillna(0.0)
    return W, "D"


def SECTOR():
    """4.1 sector momentum rotation -> crypto sectors: rank 6 sectors by 30-day equal-weight return; long the coins of
    the top 2 sectors, short the coins of the bottom 2; weekly."""
    r30 = C.pct_change(30, fill_method=None).where(E)
    sec = pd.DataFrame({k: r30[[c for c in v if c in r30]].mean(axis=1) for k, v in SECTORS.items()})
    rk = sec.rank(axis=1, ascending=False)
    W = pd.DataFrame(0.0, index=C.index, columns=C.columns)
    for k, coins in SECTORS.items():
        top, bot = (rk[k] <= 2), (rk[k] >= 5)
        for c in coins:
            W.loc[top & E[c], c] = 1.0
            W.loc[bot & E[c], c] = -1.0
    lw, sw = W.clip(lower=0), -W.clip(upper=0)
    lw = lw.div(lw.sum(axis=1).where(lw.sum(axis=1) > 0), axis=0) * 0.5
    sw = sw.div(sw.sum(axis=1).where(sw.sum(axis=1) > 0), axis=0) * 0.5
    return (lw - sw).fillna(0.0), "W"


def VOLTARGET():
    """6.5 volatility targeting -> the equal-weight long basket scaled to 40% annualized vol (20-day), max 1x."""
    base = pf.long_only(E, E)
    br = (base.shift(1) * R).sum(axis=1)
    k = (0.40 / (br.rolling(20).std() * np.sqrt(365))).clip(upper=1.0).fillna(0.0)
    return base.mul(k, axis=0), "W"


def FOMCDAY():
    """19.5 trading on economic announcements -> long the equal-weight basket for the UTC day of each FOMC decision
    (pre-announcement drift); flat otherwise."""
    days = [int(pd.Timestamp(d, tz="UTC").timestamp() * 1000) - DAY for d in FOMC]   # weights set the day before
    on = pd.Series(C.index.isin(days), index=C.index)
    return pf.long_only(E, E).mul(on.astype(float), axis=0), "D"


def DISTRESS():
    """15.1 / 15.3 distressed investing -> long coins more than 75% below their 1-year high that have reclaimed their
    20-day SMA; equal weight; weekly; cash if none."""
    dd = C / C.rolling(365, min_periods=200).max() - 1
    m = (dd < -0.75) & (C > C.rolling(20).mean())
    return pf.long_only(m, E), "W"


STRATS = {
    "MOM": MOM, "LOWVOL": LOWVOL, "RESMOM": RESMOM, "CONTRA": CONTRA, "MA2": MA2, "MA3": MA3, "TSMOM": TSMOM,
    "CHANFADE": CHANFADE, "DUALMOM": DUALMOM, "TRENDLO": TRENDLO, "RSQ": RSQ,
    "CARRY": CARRY, "MOMCARRY": MOMCARRY, "DOLLARCARRY": DOLLARCARRY, "SKEW": SKEW, "NEWLIST": NEWLIST,
    "SECTOR": SECTOR, "VOLTARGET": VOLTARGET, "FOMCDAY": FOMCDAY, "DISTRESS": DISTRESS,
}
LONG_ONLY = {"DUALMOM", "TRENDLO", "VOLTARGET", "DISTRESS", "FOMCDAY"}


def evaluate_one(name):
    W, every = STRATS[name]()
    res = pf.run(P, W, every)
    out = {}
    for per, x in pf.periods(res).items():
        out[per] = pf.metrics(x)
        out[per]["avg long"] = round(x.long.mean(), 2)
        out[per]["avg short"] = round(x.short.mean(), 2)
    return out


def verdict(name, m, bench):
    s_old, s_new = m["old"].get("Sharpe", np.nan), m["12m"].get("Sharpe", np.nan)
    ok = s_old >= 0.5 and s_new >= 0.5
    if name in LONG_ONLY:
        ok = ok and s_old > bench["old"]["Sharpe"] and s_new > bench["12m"]["Sharpe"]
    return "PASS" if ok else "fail"


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "--list"
    if arg == "--list":
        for k, f in STRATS.items():
            print("%-12s %s" % (k, f.__doc__.split("\n")[0]))
        sys.exit()
    STRATS["BENCH_EW"], STRATS["BENCH_BTC"] = bench_ew, bench_btc
    bench = evaluate_one("BENCH_EW")
    names = [k for k in STRATS if not k.startswith("BENCH")] if arg == "ALL" else arg.split(",")
    rows = []
    for n in ["BENCH_EW", "BENCH_BTC"] + names:
        m = evaluate_one(n)
        row = {"strategy": n}
        for per in ("old", "12m"):
            for k in ("ann %", "Sharpe", "maxDD %", "funding %/yr", "costs %/yr"):
                row["%s %s" % (k, per)] = m[per].get(k)
        row["verdict"] = "" if n.startswith("BENCH") else verdict(n, m, bench)
        rows.append(row)
        print(n, row["verdict"], "Sharpe old %s / 12m %s" % (row["Sharpe old"], row["Sharpe 12m"]), flush=True)
    title = "p151 " + ("all" if arg == "ALL" else arg.lower())
    write_report(title, [("Rules", "Net of 0.06%/side costs and funding. Pass = Sharpe >= 0.5 in both periods "
                          "(long-only books must also beat the equal-weight basket)."),
                         ("Results", pd.DataFrame(rows))])
