"""Q4: fade funding-rate extremes. Funding >= +0.05% per 8h -> short; <= -0.05% -> long."""
from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd
import config
from lib.data import load_1h, load_funding
from lib.execution import simulate
from lib.indicators import atr

H = 3600_000
THR = 0.0005
rows = []
for coin in config.COINS:
    f = load_funding(coin)
    if f.empty:
        continue
    b4 = bars(coin, 4)
    t4, a4 = b4.t.values + 4 * H, atr(b4)            # ATR known at each 4h close
    df = load_1h(coin)
    h1 = {k: df[k].values for k in ("t", "o", "h", "l", "c")}
    f["r8"] = f.rate * 8 / f.interval_h.replace(0, 8)
    busy = 0
    for t, r8 in zip(f.t.values, f.r8.values):
        side = -1 if r8 >= THR else (1 if r8 <= -THR else 0)
        if side == 0:
            continue
        t_sig = int(-(-t // H) * H)                    # first full hour after the funding time
        if t_sig < busy:
            continue
        k = np.searchsorted(t4, t_sig, side="right") - 1   # last 4h bar closed by then
        j = np.searchsorted(h1["t"], t_sig) - 1            # last 1h close before entry
        if k < 20 or j < 0:
            continue
        px, a = h1["c"][j], a4[k]
        stop = px - side * 2 * a
        res = simulate(h1, t_sig, side, stop, px + side * 2 * abs(px - stop), None, 48)
        if res:
            busy = res["t_out"]
            res.update(coin=coin, side=side, t_sig=t_sig, funding8h=r8)
            rows.append(res)
tag_and_save(pd.DataFrame(rows), "FUND")
