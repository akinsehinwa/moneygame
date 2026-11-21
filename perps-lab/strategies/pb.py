import pandas as pd
from lib.indicators import atr, ema, rsi
from strategies import Signal

NAME, TIMEFRAME = "PB", 4
DESCRIPTION = "Trend pullback: EMA20>50>200, close reclaims EMA20 after an RSI(14) dip < 45. Stop under 5-bar low, 2R, 72h."


def signals(b):
    c, l, h = b.c.values, b.l.values, b.h.values
    a, e20, e50, e200, r = atr(b), ema(c, 20), ema(c, 50), ema(c, 200), rsi(c, 14)
    rmin, rmax = pd.Series(r).rolling(5).min().values, pd.Series(r).rolling(5).max().values
    lo5, hi5 = pd.Series(l).rolling(5).min().values, pd.Series(h).rolling(5).max().values
    for i in range(210, len(c)):
        if e20[i] > e50[i] > e200[i] and c[i - 1] < e20[i - 1] and c[i] > e20[i] and rmin[i] < 45:
            yield Signal(i, 1, min(lo5[i] - 0.25 * a[i], c[i] - a[i]), target_r=2.0, max_hours=72)
        elif e20[i] < e50[i] < e200[i] and c[i - 1] > e20[i - 1] and c[i] < e20[i] and rmax[i] > 55:
            yield Signal(i, -1, max(hi5[i] + 0.25 * a[i], c[i] + a[i]), target_r=2.0, max_hours=72)
