import numpy as np
from lib.indicators import supertrend
from strategies import Signal, supertrend_trail

NAME, TIMEFRAME = "ST4", 4
DESCRIPTION = "4h SuperTrend(10, 3) flip, both sides; the line is the trailing stop; exit on flip or after 7 days."


def signals(b):
    line, d = supertrend(b, 10, 3)
    for i in range(60, len(b)):
        if d[i] != d[i - 1] and not np.isnan(line[i]):
            yield Signal(i, int(d[i]), line[i], trail=supertrend_trail(line, d, i, int(d[i])))
