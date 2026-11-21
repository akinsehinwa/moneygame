import pandas as pd
from lib.indicators import atr, bollinger
from strategies import Signal

NAME, TIMEFRAME = "SQZ", 4
DESCRIPTION = "Squeeze breakout: Bollinger width at a 120-bar low within 6 bars, then a close outside the band. 1.5 ATR stop, 2.5R, 72h."


def signals(b):
    c = b.c.values
    a = atr(b)
    mid, sd = bollinger(c, 20)
    bw = pd.Series(4 * sd / mid)
    tight = (bw <= bw.rolling(120).min() * 1.0001).astype(float).rolling(6).max().values
    up, dn = mid + 2 * sd, mid - 2 * sd
    for i in range(130, len(c)):
        if tight[i - 1] != 1:
            continue
        if c[i] > up[i] and c[i - 1] <= up[i - 1]:
            yield Signal(i, 1, c[i] - 1.5 * a[i], target_r=2.5, max_hours=72)
        elif c[i] < dn[i] and c[i - 1] >= dn[i - 1]:
            yield Signal(i, -1, c[i] + 1.5 * a[i], target_r=2.5, max_hours=72)
