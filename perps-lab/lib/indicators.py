"""Indicators on a bar DataFrame (columns t o h l c v). All return numpy arrays aligned to the bars;
value i uses bars 0..i only."""
import numpy as np
import pandas as pd


def ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False).mean().values


def sma(x, n):
    return pd.Series(x).rolling(n).mean().values


def atr(b, n=14):
    pc = b.c.shift(1)
    tr = np.maximum(b.h - b.l, np.maximum((b.h - pc).abs(), (b.l - pc).abs())).fillna(b.h - b.l)
    return tr.ewm(alpha=1 / n, adjust=False).mean().values


def rsi(c, n):
    c = np.asarray(c, dtype=float)
    d = np.diff(c, prepend=c[0])
    up = pd.Series(np.where(d > 0, d, 0.0)).ewm(alpha=1 / n, adjust=False).mean()
    dn = pd.Series(np.where(d < 0, -d, 0.0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn.replace(0, np.nan))).fillna(50).values


def highest(x, n, shift=1):
    """Highest of the n bars BEFORE bar i (shift=1 excludes the current bar)."""
    return pd.Series(x).rolling(n).max().shift(shift).values


def lowest(x, n, shift=1):
    return pd.Series(x).rolling(n).min().shift(shift).values


def bollinger(c, n=20):
    s = pd.Series(c)
    return s.rolling(n).mean().values, s.rolling(n).std().values


def supertrend(b, n, mult):
    """(line, direction): direction +1 = line below price (up), -1 = above (down)."""
    a = atr(b, n)
    hl2 = ((b.h + b.l) / 2).values
    c = b.c.values
    ub, lb = hl2 + mult * a, hl2 - mult * a
    fu, fl = ub.copy(), lb.copy()
    d = np.ones(len(c))
    line = np.full(len(c), np.nan)
    for i in range(1, len(c)):
        fu[i] = ub[i] if (ub[i] < fu[i - 1] or c[i - 1] > fu[i - 1]) else fu[i - 1]
        fl[i] = lb[i] if (lb[i] > fl[i - 1] or c[i - 1] < fl[i - 1]) else fl[i - 1]
        d[i] = (-1 if c[i] < fl[i] else 1) if d[i - 1] == 1 else (1 if c[i] > fu[i] else -1)
        line[i] = fl[i] if d[i] == 1 else fu[i]
    line[:n] = np.nan
    return line, d


def efficiency_ratio(c, n=20):
    """Kaufman efficiency ratio: net move / sum of absolute moves over n bars (1 = straight line, 0 = noise)."""
    s = pd.Series(c)
    return ((s - s.shift(n)).abs() / s.diff().abs().rolling(n).sum()).values
