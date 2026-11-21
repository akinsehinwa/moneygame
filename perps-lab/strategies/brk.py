from lib.indicators import atr, highest, lowest
from strategies import Signal

NAME, TIMEFRAME = "BRK", 4
DESCRIPTION = "4h close through the 55-bar high/low (fresh), body >= 1 ATR. Stop 2 ATR, target 2R, 48h."


def signals(b):
    o, c = b.o.values, b.c.values
    a, hi, lo = atr(b), highest(b.h.values, 55), lowest(b.l.values, 55)
    for i in range(60, len(c)):
        body = abs(c[i] - o[i])
        if body < a[i]:
            continue
        if c[i] > hi[i] and c[i - 1] <= hi[i - 1] and c[i] > o[i]:
            yield Signal(i, 1, c[i] - 2 * a[i], target_r=2.0, max_hours=48)
        elif c[i] < lo[i] and c[i - 1] >= lo[i - 1] and c[i] < o[i]:
            yield Signal(i, -1, c[i] + 2 * a[i], target_r=2.0, max_hours=48)
