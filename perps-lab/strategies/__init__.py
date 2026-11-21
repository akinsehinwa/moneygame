"""Strategy registry. Each module in this folder defines:

    NAME = "BRK"                 # short code used in every report
    TIMEFRAME = 4                # signal bar size in hours (4 or 24)
    DESCRIPTION = "..."          # one line
    def signals(bars):           # bars = DataFrame t o h l c v, closed bars only
        yield Signal(...)
    def signals(bars, ctx):      # optional form: ctx["btc"][4] / ctx["btc"][24] are BTC bars (same columns)

A Signal fires at the CLOSE of bar i. Give either target_r (R multiple from the signal close) or target_px, or
neither (exit by stop / trail / time). trail = (bar index array, stop level array): level k becomes the stop at the
close of bar k (only if it tightens); a level of +/-execution.EXIT_NOW exits at the next open.
Add a strategy by dropping a new file here; nothing else needs to change.
"""
import importlib, pkgutil
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class Signal:
    i: int
    side: int                 # +1 long, -1 short
    stop: float
    target_r: Optional[float] = None
    target_px: Optional[float] = None
    max_hours: int = 168
    trail: Optional[tuple] = None


def supertrend_trail(line, d, i, side):
    """Trail on a SuperTrend line from bar i+1 until the direction flips (then exit at the next open)."""
    from lib.execution import EXIT_NOW
    k = np.arange(i + 1, len(d))
    lv = np.where(d[k] == side, line[k], np.nan)
    flip = np.where(d[k] != side)[0]
    if len(flip):
        k, lv = k[:flip[0] + 1], lv[:flip[0] + 1].copy()
        lv[-1] = EXIT_NOW if side == 1 else -EXIT_NOW
    return k, lv


def load_all():
    mods = {}
    for m in pkgutil.iter_modules(__path__):
        mod = importlib.import_module("strategies." + m.name)
        if hasattr(mod, "signals"):
            mods[mod.NAME] = mod
    return dict(sorted(mods.items()))
