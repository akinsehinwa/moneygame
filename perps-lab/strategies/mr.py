from lib.indicators import atr, bollinger, rsi
from strategies import Signal

NAME, TIMEFRAME = "MR", 4
DESCRIPTION = "Mean reversion: close beyond Bollinger(20, 2.5) with RSI(3) < 10 / > 90. Target the 20-bar mean, stop 2 ATR, 48h."


def signals(b):
    c = b.c.values
    a, r3 = atr(b), rsi(c, 3)
    mid, sd = bollinger(c, 20)
    for i in range(30, len(c)):
        if c[i] < mid[i] - 2.5 * sd[i] and r3[i] < 10:
            yield Signal(i, 1, c[i] - 2 * a[i], target_px=mid[i], max_hours=48)
        elif c[i] > mid[i] + 2.5 * sd[i] and r3[i] > 90:
            yield Signal(i, -1, c[i] + 2 * a[i], target_px=mid[i], max_hours=48)
