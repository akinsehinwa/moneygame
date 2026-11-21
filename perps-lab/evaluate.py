"""Scorecards and the walk-forward router test. Writes a dated report to results/.
    python3 evaluate.py                 # all strategies in data/trades.pkl
    python3 evaluate.py --only STD      # one strategy's scorecard
    python3 evaluate.py --title "new idea X"

Sections
1. Scorecard per strategy and side: old period vs last 12 months.
2. By coin regime (the coin's own trend x character) for each strategy and side.
3. Walk-forward routers: each quarter, switch on cells with good PAST results only and score the next quarter.
   Compares taking everything vs routing by strategy, market regime, coin regime, coin group, and single coin.
Trades on the same day across coins are not independent: the t-stat uses weekly mean R as the unit.
"""
import argparse, datetime as dt, os

import numpy as np
import pandas as pd

import config

H = 3600_000
ms = lambda s: int(pd.Timestamp(s, tz="UTC").timestamp() * 1000)

ROUTERS = {
    "take everything": [],
    "strategy+side": ["leg"],
    "+ market regime": ["leg", "mreg"],
    "+ coin regime": ["leg", "creg"],
    "+ market + coin regime": ["leg", "mreg", "creg"],
    "+ coin group": ["leg", "grp"],
    "+ single coin": ["leg", "coin"],
}


def load():
    d = pd.read_pickle(os.path.join(config.DATA, "trades.pkl"))
    d = d[(d.t_sig >= ms(config.EVAL_START)) & d.mtrend.notna() & d.ctrend.notna()].copy()
    d["leg"] = d.strat + np.where(d.side == 1, " long", " short")
    d["mreg"] = d.mtrend + "/" + d.mvol
    d["creg"] = d.ctrend + "/" + d.cchar
    d["grp"] = np.where(d["corr"] >= 0.7, "hiCorr", "loCorr") + "/" + np.where(d.cvol >= 0.8, "hiVol", "loVol")
    d["week"] = d.t_sig // (7 * 24 * H)
    d["recent"] = d.t_sig >= ms(config.SPLIT)
    return d


def stats(x):
    if len(x) == 0:
        return dict(n=0, win=np.nan, avgR=np.nan, t=np.nan)
    w = x.groupby("week").r.mean()
    t = w.mean() / (w.std(ddof=1) / np.sqrt(len(w))) if len(w) > 2 and w.std() > 0 else np.nan
    return dict(n=len(x), win=round((x.r > 0).mean() * 100), avgR=round(x.r.mean(), 3), t=round(t, 1))


def scorecard(d):
    rows = []
    for leg, x in d.groupby("leg"):
        o, r = stats(x[~x.recent]), stats(x[x.recent])
        rows.append({"strategy": leg, "n old": o["n"], "avgR old": o["avgR"], "n 12m": r["n"], "avgR 12m": r["avgR"],
                     "win% 12m": r["win"], "t 12m": r["t"], "holds": "yes" if (o["avgR"] > 0 and r["avgR"] > 0) else ""})
    return pd.DataFrame(rows)


def by_coin_regime(d, min_n=40):
    g = d.groupby(["leg", "creg"])
    rows = []
    for (leg, cr), x in g:
        o, r = x[~x.recent], x[x.recent]
        if len(x) < min_n:
            continue
        rows.append({"strategy": leg, "coin regime": cr, "n": len(x), "avgR": round(x.r.mean(), 2),
                     "old": round(o.r.mean(), 2) if len(o) else np.nan,
                     "12m": round(r.r.mean(), 2) if len(r) else np.nan,
                     "holds": "yes" if len(o) and len(r) and o.r.mean() > 0.05 and r.r.mean() > 0.05 else ""})
    return pd.DataFrame(rows)


def walk(d, keys, min_r, min_n):
    q0, end = pd.Timestamp(config.WF_START, tz="UTC"), pd.Timestamp(config.SPLIT, tz="UTC") + pd.DateOffset(years=1)
    out = []
    while q0 < end:
        q1 = q0 + pd.DateOffset(months=config.WF_STEP_MONTHS)
        a, b = int(q0.timestamp() * 1000), int(q1.timestamp() * 1000)
        cur = d[(d.t_sig >= a) & (d.t_sig < b)]
        if keys:
            hist = d[d.t_out < a]
            g = hist.groupby(keys).r.agg(["size", "mean"])
            on = g[(g["size"] >= min_n) & (g["mean"] > min_r)].index
            idx = pd.MultiIndex.from_frame(cur[keys]) if len(keys) > 1 else pd.Index(cur[keys[0]])
            cur = cur[idx.isin(on)]
        out.append(cur.assign(q=q0.strftime("%Y-%m")))
        q0 = q1
    return pd.concat(out)


def routers(d):
    rows = []
    months = 12 * (pd.Timestamp(config.SPLIT) + pd.DateOffset(years=1) - pd.Timestamp(config.WF_START)).days / 365.25
    for name, keys in ROUTERS.items():
        mn = 15 if "coin" in keys else config.ROUTER_MIN_N
        t = walk(d, keys, config.ROUTER_MIN_R, mn)
        s = stats(t)
        byq = t.groupby("q").r.mean()
        rows.append({"router": name, "trades/mo": round(len(t) / months), "avgR": s["avgR"], "t": s["t"],
                     "R/mo": round(t.r.sum() / months, 1), "quarters +": "%d/%d" % ((byq > 0).sum(), len(byq))})
    return pd.DataFrame(rows)


def md(df):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join("" if (isinstance(v, float) and np.isnan(v)) else str(v) for v in r) + " |")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--title", default="strategy pool")
    a = ap.parse_args()
    d = load()
    if a.only:
        d = d[d.strat.isin(a.only.split(","))]
    today = dt.date.today().isoformat()
    parts = ["# %s (%s)" % (a.title, today), "",
             "Trades %d, coins %d, signals %s to %s. R per trade at 1R risk, costs included. "
             "Old = before %s, 12m = after. t = weekly-clustered t-stat (|t| < 2 is not significant)." %
             (len(d), d.coin.nunique(), pd.to_datetime(d.t_sig.min(), unit="ms").date(),
              pd.to_datetime(d.t_sig.max(), unit="ms").date(), config.SPLIT), "",
             "## 1. Scorecard", "", md(scorecard(d)), "",
             "## 2. By coin regime", "", md(by_coin_regime(d)), "",
             "## 3. Walk-forward routers (out of sample, %s onward, cell on if past avg R > %.2f, n >= %d)" %
             (config.WF_START, config.ROUTER_MIN_R, config.ROUTER_MIN_N), "", md(routers(d)), ""]
    text = "\n".join(parts)
    print(text)
    os.makedirs(config.RESULTS, exist_ok=True)
    f = os.path.join(config.RESULTS, "%s-%s.md" % (today, a.title.lower().replace(" ", "-")))
    open(f, "w").write(text)
    print("\nwritten:", f)
