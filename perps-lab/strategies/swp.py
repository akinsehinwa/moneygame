from lib.indicators import atr, highest, lowest
from strategies import Signal

NAME, TIMEFRAME = "SWP", 4
DESCRIPTION = "Liquidity sweep fade: wick through the 20-bar extreme (>= 50% of the range), close back inside. 1.5R, 24h."


def signals(b):
    o, h, l, c = b.o.values, b.h.values, b.l.values, b.c.values
    a, hi, lo = atr(b), highest(h, 20), lowest(l, 20)
    for i in range(30, len(c)):
        rng = h[i] - l[i]
        if rng <= 0:
            continue
        if h[i] > hi[i] and c[i] < hi[i] and h[i] - max(o[i], c[i]) >= 0.5 * rng:
            yield Signal(i, -1, h[i] + 0.25 * a[i], target_r=1.5, max_hours=24)
        elif l[i] < lo[i] and c[i] > lo[i] and min(o[i], c[i]) - l[i] >= 0.5 * rng:
            yield Signal(i, 1, l[i] - 0.25 * a[i], target_r=1.5, max_hours=24)
