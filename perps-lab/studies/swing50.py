"""SW50: big-leg 50% retracement continuation (pre-registered in LEDGER.md, step 5).

After a big 4h leg (>= 6 ATR within 5 days) confirmed by a 1-ATR pullback from its extreme: a limit order at the 50%
retracement, stop at the 78.6% level, target the leg's extreme. Cancelled if price makes a new extreme first or after
10 days unfilled. Max hold 7 days after the fill. 1h fills; costs 0.06% per side.
    python3 studies/swing50.py   -> merges SW50 trades into data/trades.pkl
"""
from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd

import config
from lib.data import load_1h, resample
from lib.indicators import atr

H = 3600_000
COST = config.FEE_PER_SIDE + config.SLIP_PER_SIDE


def legs(b):
    t, h, l, cl = (b[k].values for k in ("t", "h", "l", "c"))
    A = atr(b)
    n = len(cl)
    out = []
    for side in (1, -1):
        i, cool = 40, 0
        while i < n - 2:
            a = A[i]
            if i < cool or not a > 0:
                i += 1
                continue
            if side == 1:
                start, ext = l[i - 30:i + 1].min(), h[i]
                fresh = h[i] >= h[i - 30:i].max()
            else:
                start, ext = h[i - 30:i + 1].max(), l[i]
                fresh = l[i] <= l[i - 30:i].min()
            if not (fresh and abs(ext - start) >= 6 * a):
                i += 1
                continue
            k = i
            while k < n - 1:
                k += 1
                if side == 1 and h[k] > ext:
                    ext = h[k]
                elif side == -1 and l[k] < ext:
                    ext = l[k]
                elif (ext - cl[k]) * side >= A[k]:
                    break
            out.append((int(t[k]) + 4 * H, side, start, ext, A[k]))
            cool, i = k + 6, k + 1
    return out


def run_coin(coin):
    df = load_1h(coin)
    T, O, Hh, L = (df[k].values for k in ("t", "o", "h", "l"))
    rows, busy = [], 0
    for t_conf, side, start, ext, a in sorted(legs(resample(df, 4))):
        leg = abs(ext - start)
        entry_px = ext - side * 0.5 * leg
        stop, target = ext - side * 0.786 * leg, ext
        i = int(np.searchsorted(T, t_conf))
        if t_conf < busy:
            continue
        fill = None
        for j in range(i, min(len(T), i + 240)):            # 10 days to fill
            if (side == 1 and Hh[j] > ext) or (side == -1 and L[j] < ext):
                break                                          # new extreme first: cancel
            if (side == 1 and L[j] <= entry_px) or (side == -1 and Hh[j] >= entry_px):
                fill = j
                break
        if fill is None:
            continue
        e = min(entry_px, O[fill]) if side == 1 else max(entry_px, O[fill])
        risk = (e - stop) * side
        if risk <= 0:
            continue
        px, why, j = None, None, fill
        for j in range(fill, min(len(T), fill + 168)):
            if (side == 1 and L[j] <= stop) or (side == -1 and Hh[j] >= stop):
                px, why = (min(stop, O[j]) if side == 1 else max(stop, O[j])), "stop"
                break
            if j > fill and ((side == 1 and Hh[j] >= target) or (side == -1 and L[j] <= target)):
                px, why = (max(target, O[j]) if side == 1 else min(target, O[j])), "target"
                break
        if px is None:
            if fill + 168 >= len(T):
                continue
            j = fill + 168
            px, why = O[j], "time"
        r = ((px - e) * side - COST * (e + px)) / risk
        rows.append({"coin": coin, "side": side, "t_sig": t_conf, "t_in": int(T[fill]), "t_out": int(T[j]),
                     "entry": e, "exit": px, "stop0": stop, "r": r, "why": why, "risk_pct": risk / e,
                     "leg_atr": leg / a})
        busy = int(T[j])
    return rows


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(8) as ex:
        rows = [r for rs in ex.map(run_coin, config.COINS) for r in rs]
    d = pd.DataFrame(rows)
    print(len(d), "SW50 trades; avg R %.3f; win %.0f%%" % (d.r.mean(), (d.r > 0).mean() * 100))
    tag_and_save(d, "SW50")
