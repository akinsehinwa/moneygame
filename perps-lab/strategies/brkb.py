import numpy as np
from lib.indicators import ema
from strategies import brk

NAME, TIMEFRAME = "BRKB", 4
DESCRIPTION = "BRK, but only in BTC's 4h trend direction (BTC EMA50 vs EMA200 on the same closed bar)."


def signals(b, ctx):
    btc = ctx["btc"][4]
    c = btc.c.values
    up = dict(zip(btc.t.values, ema(c, 50) > ema(c, 200)))
    T = b.t.values
    for s in brk.signals(b):
        u = up.get(T[s.i])
        if u is None:
            continue
        if (s.side == 1) == bool(u):
            yield s
