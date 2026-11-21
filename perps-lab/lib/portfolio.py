"""Daily portfolio backtester for basket strategies (momentum, carry, low-vol...), with costs AND funding.

Conventions
- Day d = the UTC day whose daily bar closes at 24:00. Weights are decided at the close of day d using data up to d,
  and earn day d+1's return. No look-ahead.
- PnL(d+1) = sum_i w_i * r_i(d+1) - sum_i w_i * funding_i(d+1) - cost * sum_i |w_i(d) - w_i(d-1)|
  (a long pays positive funding, a short receives it). cost = fee + slippage per side.
- Weights are normalized by the strategy: dollar-neutral books use sum|w| = 1 (0.5 long / 0.5 short);
  long-only books use sum w = 1. Between rebalances the target weights are held constant.
- Funding for the current month isn't in Binance's monthly archive yet; those days count as zero funding.
"""
import os

import numpy as np
import pandas as pd

import config
from lib.data import load_1h, load_funding, load_tv, resample

DAY = 24 * 3600_000
COST = config.FEE_PER_SIDE + config.SLIP_PER_SIDE
PANEL = os.path.join(config.DATA, "panel.pkl")


def build_panel(force=False):
    if os.path.exists(PANEL) and not force:
        return pd.read_pickle(PANEL)
    C, Hh, L, QV, F = {}, {}, {}, {}, {}
    tvd = load_tv("daily")
    for coin in config.COINS:
        d = resample(load_1h(coin), 24).set_index("t")
        tv = tvd.get(coin)
        if tv:                               # TradingView daily bars for days after the archive (complete days only)
            x = pd.DataFrame({"o": tv["o"], "h": tv["h"], "l": tv["l"], "c": tv["c"], "v": tv.get("v") or [np.nan] * len(tv["t"])},
                             index=[int(t) * 1000 for t in tv["t"]])
            x = x[x.index > (d.index.max() if len(d) else -1)]
            d = pd.concat([d, x])
        C[coin], Hh[coin], L[coin], QV[coin] = d.c, d.h, d.l, d.v * d.c
        f = load_funding(coin)
        if len(f):
            day = (f.t - 1) // DAY * DAY            # a funding print at 00:00 closes the previous day
            F[coin] = f.groupby(day).rate.sum()
    P = {"C": pd.DataFrame(C).sort_index(), "H": pd.DataFrame(Hh), "L": pd.DataFrame(L), "QV": pd.DataFrame(QV)}
    for k in ("H", "L", "QV"):
        P[k] = P[k].reindex(P["C"].index)
    P["F"] = pd.DataFrame(F).reindex(P["C"].index).reindex(columns=P["C"].columns).fillna(0.0)
    P["R"] = P["C"].pct_change(fill_method=None)
    age = P["C"].notna().cumsum()
    P["AGE"] = age.where(P["C"].notna())
    pd.to_pickle(P, PANEL)
    return P


def eligible(P, min_age=120):
    return (P["AGE"] >= min_age) & P["C"].notna() & (P["QV"] > 0)


def rebalance_days(index, every):
    ts = pd.to_datetime(index, unit="ms")
    if every == "D":
        return np.ones(len(index), bool)
    if every == "W":                                   # Sunday's bar closes at Monday 00:00 UTC
        return ts.weekday == 6
    if every == "4W":
        wk = (ts - pd.Timestamp("2020-01-05")).days // 7
        return (ts.weekday == 6) & (wk % 4 == 0)
    raise ValueError(every)


def run(P, W, every="W"):
    """W: target weights (days x coins), computed with data up to each day. Returns daily DataFrame."""
    W = W.reindex(index=P["C"].index, columns=P["C"].columns).fillna(0.0)
    mask = rebalance_days(W.index, every)
    W = W.where(pd.Series(mask, index=W.index), np.nan).ffill().fillna(0.0)
    R = P["R"].fillna(0.0)
    held = W.shift(1).fillna(0.0)                      # weights set at close d-1 earn day d
    gross = (held * R).sum(axis=1)
    fund = (held * P["F"]).sum(axis=1)
    turn = (W - W.shift(1).fillna(0.0)).abs().sum(axis=1).shift(1).fillna(0.0)
    net = gross - fund - COST * turn
    return pd.DataFrame({"net": net, "gross": gross, "funding": -fund, "cost": -COST * turn,
                         "long": held.clip(lower=0).sum(axis=1), "short": held.clip(upper=0).sum(axis=1)})


def metrics(x):
    if len(x) < 20 or x.net.std() == 0:
        return {}
    eq = (1 + x.net).cumprod()
    wk = (1 + x.net).groupby(pd.to_datetime(x.index, unit="ms").to_period("W")).prod() - 1
    return {"ann %": round(x.net.mean() * 365 * 100, 1), "vol %": round(x.net.std() * np.sqrt(365) * 100, 1),
            "Sharpe": round(x.net.mean() / x.net.std() * np.sqrt(365), 2),
            "maxDD %": round((eq / eq.cummax() - 1).min() * 100, 1),
            "funding %/yr": round(x.funding.mean() * 365 * 100, 1), "costs %/yr": round(x.cost.mean() * 365 * 100, 1),
            "t week": round(wk.mean() / wk.std() * np.sqrt(len(wk)), 1)}


def periods(res):
    ms = lambda s: int(pd.Timestamp(s, tz="UTC").timestamp() * 1000)
    a, b = ms(config.EVAL_START), ms(config.SPLIT)
    return {"old": res[(res.index >= a) & (res.index < b)], "12m": res[res.index >= b]}


# ---------------------------------------------------------------- weight helpers

def long_short(score, E, n=7, scale=None):
    """Long the n highest scores, short the n lowest (eligible coins only); 0.5 gross per side.
    scale: optional DataFrame (e.g. 1/vol) to weight within each side."""
    s = score.where(E)
    rk_hi = s.rank(axis=1, ascending=False, method="first")
    rk_lo = s.rank(axis=1, ascending=True, method="first")
    cnt = s.notna().sum(axis=1)
    ok = cnt >= 3 * n
    lw = (rk_hi <= n).astype(float)
    sw = (rk_lo <= n).astype(float)
    if scale is not None:
        lw, sw = lw * scale, sw * scale
    lw = lw.div(lw.sum(axis=1), axis=0) * 0.5
    sw = sw.div(sw.sum(axis=1), axis=0) * 0.5
    return (lw - sw).where(ok, 0.0).fillna(0.0)


def normalize_gross(W):
    g = W.abs().sum(axis=1)
    return W.div(g.where(g > 0), axis=0).fillna(0.0)


def long_only(mask, E, scale=None, cap=None):
    w = (mask & E).astype(float)
    if scale is not None:
        w = w * scale.where(mask & E, 0.0)
    w = w.div(w.sum(axis=1).where(w.sum(axis=1) > 0), axis=0).fillna(0.0)
    if cap is not None:
        for _ in range(5):
            w = w.clip(upper=cap)
            w = w.div(w.sum(axis=1).where(w.sum(axis=1) > 0), axis=0).fillna(0.0)
    return w
