"""Trade simulation on 1h bars. Conservative by design:
- entry at the open of the first 1h bar after the signal bar closes (market order) + costs;
- a bar that touches both stop and target counts as a stop;
- stops fill at the worse of the stop and the bar open (gaps hurt);
- time exit at the open of the first bar past the max hold;
- R = (profit per unit - round-trip costs) / initial risk per unit."""
import numpy as np

import config

H = 3600_000
COST = config.FEE_PER_SIDE + config.SLIP_PER_SIDE
EXIT_NOW = 1e18   # a trail level of +/-EXIT_NOW means "exit at the next bar open"


def simulate(h1, t_signal_close, side, stop, target=None, trail=None, max_hours=None):
    """h1: dict of numpy arrays t,o,h,l,c. trail: (times, levels) - each level becomes the stop from that time,
    only if it tightens. Returns a dict, or None if there's no entry bar or the trade is still open."""
    max_hours = min(max_hours or config.MAX_HOLD_HOURS, config.MAX_HOLD_HOURS)
    T, O, Hh, L = h1["t"], h1["o"], h1["h"], h1["l"]
    i = int(np.searchsorted(T, t_signal_close))
    if i >= len(T):
        return None
    entry = O[i]
    risk = (entry - stop) * side
    if risk <= 0:
        return None
    end_t = T[i] + max_hours * H
    cur, ti = stop, 0
    for j in range(i, len(T)):
        if trail is not None:
            tt, lv = trail
            while ti < len(tt) and tt[ti] <= T[j]:
                if not np.isnan(lv[ti]) and (lv[ti] - cur) * side > 0:
                    cur = lv[ti]
                ti += 1
        if T[j] >= end_t:
            px, why = O[j], "time"
        elif side == 1 and L[j] <= cur:
            px, why = min(cur, O[j]), "stop"
        elif side == -1 and Hh[j] >= cur:
            px, why = max(cur, O[j]), "stop"
        elif target is not None and side == 1 and Hh[j] >= target:
            px, why = max(target, O[j]), "target"
        elif target is not None and side == -1 and L[j] <= target:
            px, why = min(target, O[j]), "target"
        else:
            continue
        r = ((px - entry) * side - COST * (entry + px)) / risk
        return {"t_in": int(T[i]), "t_out": int(T[j]), "entry": entry, "exit": px, "stop0": stop,
                "r": r, "why": why, "risk_pct": risk / entry}
    return None
