"""Regime labels, known at the START of each UTC day (built only from daily bars closed before it).

market regime (BTC): trend UP / DOWN / RANGE x vol HIGH / LOW
coin regime (each coin): trend UP / DOWN / RANGE x character TREND / CHOP
  trend: UP if close > EMA50 and EMA50 higher than 10 days ago; DOWN if below and falling; else RANGE
  vol:   HIGH if 20-day realized vol > its 180-day median
  character: TREND if the 20-day efficiency ratio >= 0.3, else CHOP
"""
import numpy as np
import pandas as pd

from lib.indicators import ema, efficiency_ratio

DAY = 24 * 3600_000


def _trend(c):
    e50 = ema(c, 50)
    slope = e50 - np.roll(e50, 10)
    t = np.where((c > e50) & (slope > 0), "UP", np.where((c < e50) & (slope < 0), "DOWN", "RANGE")).astype(object)
    t[:60] = None   # not enough history to label
    return t


def market(btc_daily):
    c = btc_daily.c.values
    rv = np.log(btc_daily.c).diff().rolling(20).std()
    med = rv.rolling(180).median()
    vol = np.where(rv > med, "HIGH", "LOW")
    out = pd.DataFrame({"mtrend": _trend(c), "mvol": vol}, index=btc_daily.t.values + DAY)
    return out[med.notna().values & (np.arange(len(c)) >= 60)]


def coin(daily, btc_daily):
    c = daily.c.values
    er = efficiency_ratio(c, 20)
    a = daily.set_index("t").c
    b = btc_daily.set_index("t").c.reindex(a.index)
    ra, rb = np.log(a).diff(), np.log(b).diff()
    out = pd.DataFrame({
        "ctrend": _trend(c),
        "cchar": np.where(er >= 0.3, "TREND", "CHOP"),
        "er": er,
        "corr": ra.rolling(60).corr(rb).values,
        "cvol": (ra.rolling(30).std() * np.sqrt(365)).values,
    }, index=daily.t.values + DAY)
    return out[~np.isnan(er)]
