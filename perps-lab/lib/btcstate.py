"""Bitcoin daily state labels (each day labeled with data up to and including that day's close).

trend (20-day return):  STRONG_DOWN <= -10% < DOWN <= -3% < RANGE < +3% <= UP < +10% <= STRONG_UP
COIL: a RANGE day whose Bollinger(20) width is in the lowest 20% of the past 365 days (tight consolidation).
CRT (today's daily candle vs yesterday's range):
  BULL_CRT  swept yesterday's low, closed back inside      BEAR_CRT  swept yesterday's high, closed back inside
  BREAK_UP  closed above yesterday's high                  BREAK_DN  closed below yesterday's low
  INSIDE    inside yesterday's range                       OUTSIDE   swept both sides, closed inside
"""
import numpy as np
import pandas as pd


def label(btc_daily):
    d = btc_daily.set_index("t")
    c = d.c
    r20 = c.pct_change(20)
    trend = pd.Series(np.select([r20 <= -0.10, r20 <= -0.03, r20 < 0.03, r20 < 0.10], ["STRONG_DOWN", "DOWN", "RANGE", "UP"],
                                "STRONG_UP"), index=d.index).where(r20.notna())
    mid, sd = c.rolling(20).mean(), c.rolling(20).std()
    bw = 4 * sd / mid
    pct = bw.rolling(365, min_periods=180).apply(lambda x: (x[-1] >= x).mean(), raw=True)
    state = trend.where(~((trend == "RANGE") & (pct <= 0.20)), "COIL")
    ph, pl = d.h.shift(1), d.l.shift(1)
    up_sweep, dn_sweep = d.h > ph, d.l < pl
    inside_close = (c <= ph) & (c >= pl)
    crt = np.select([c > ph, c < pl, up_sweep & dn_sweep & inside_close, up_sweep & inside_close,
                     dn_sweep & inside_close], ["BREAK_UP", "BREAK_DN", "OUTSIDE", "BEAR_CRT", "BULL_CRT"], "INSIDE")
    out = pd.DataFrame({"trend": trend, "state": state, "crt": crt, "r20": r20}, index=d.index)
    out.loc[ph.isna(), "crt"] = None
    return out
