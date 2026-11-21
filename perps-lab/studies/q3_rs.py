"""Q3: weekly relative-strength rotation vs BTC: long the 10 strongest, short the 10 weakest (30-day return)."""
from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd
import config
from lib.data import load_1h
from lib.execution import simulate
from lib.indicators import atr

H, DAY = 3600_000, 24 * 3600_000
TOP, LOOKBACK, MIN_HIST = 10, 30, 90

btc = bars("BTC", 24).set_index("t").c
daily, h1, A = {}, {}, {}
for coin in config.COINS:
    if coin == "BTC":
        continue
    d = bars(coin, 24)
    daily[coin] = d.set_index("t").c
    A[coin] = pd.Series(atr(d), index=d.t.values)
    df = load_1h(coin)
    h1[coin] = {k: df[k].values for k in ("t", "o", "h", "l", "c")}

closes = pd.DataFrame(daily)
rel = closes.pct_change(LOOKBACK).sub(btc.reindex(closes.index).pct_change(LOOKBACK), axis=0)
hist = closes.notna().cumsum()
rows = []
for t in closes.index:
    t_close = t + DAY
    if pd.Timestamp(t_close, unit="ms").weekday() != 0:    # the daily bar closing at Monday 00:00 UTC
        continue
    r = rel.loc[t][hist.loc[t] >= MIN_HIST].dropna()
    if len(r) < 2 * TOP + 10:
        continue
    r = r.sort_values()
    for side, picks in ((1, r.index[-TOP:]), (-1, r.index[:TOP])):
        for coin in picks:
            px, a = closes.at[t, coin], A[coin].get(t)
            if not a > 0:
                continue
            res = simulate(h1[coin], t_close, side, px - side * 2 * a, None, None, 7 * 24)
            if res:
                res.update(coin=coin, side=side, t_sig=t_close)
                rows.append(res)
tag_and_save(pd.DataFrame(rows), "RS")
