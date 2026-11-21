"""Historical test of the shortlist setup detectors (pre-registered in LEDGER.md).
    python3 studies/shortlist_bt.py   -> results/<date>-shortlist-detectors.md, data/shortlist_events.pkl"""
import os
from concurrent.futures import ProcessPoolExecutor

from common import *  # noqa: F401,F403
import numpy as np
import pandas as pd

import config
from lib.btcstate import label
from lib.data import load_1h, resample
from lib.indicators import atr

H, DAY = 3600_000, 24 * 3600_000
COST = config.FEE_PER_SIDE + config.SLIP_PER_SIDE
A0 = int(pd.Timestamp(config.EVAL_START, tz="UTC").timestamp() * 1000)
SPLIT = int(pd.Timestamp(config.SPLIT, tz="UTC").timestamp() * 1000)
SCAN_CLOSE_UTC = {0, 12}                              # 08:00 and 20:00 SGT


def run_trade(h1, i0, side, kind, level, stop, target, valid_h, hold_h=72):
    """kind 'stop' = enter when price trades through level in the trade direction; 'limit' = enter on a pullback touch."""
    T, O, Hh, L = h1["t"], h1["o"], h1["h"], h1["l"]
    fill = None
    for j in range(i0, min(len(T), i0 + valid_h)):
        if kind == "stop":
            if (side == 1 and Hh[j] >= level) or (side == -1 and L[j] <= level):
                fill, entry = j, (max(level, O[j]) if side == 1 else min(level, O[j]))
                break
        else:
            if (side == 1 and L[j] <= level) or (side == -1 and Hh[j] >= level):
                fill, entry = j, (min(level, O[j]) if side == 1 else max(level, O[j]))
                break
    if fill is None:
        return None
    risk = (entry - stop) * side
    if risk <= 0:
        return {"filled": True, "r": np.nan}
    for j in range(fill, min(len(T), fill + hold_h + 1)):
        if j == fill + hold_h or j == len(T) - 1:
            px = O[j]
        elif (side == 1 and L[j] <= stop) or (side == -1 and Hh[j] >= stop):
            px = min(stop, O[j]) if side == 1 else max(stop, O[j])
        elif j > fill and ((side == 1 and Hh[j] >= target) or (side == -1 and L[j] <= target)):
            px = max(target, O[j]) if side == 1 else min(target, O[j])
        else:
            continue
        return {"filled": True, "r": ((px - entry) * side - COST * (entry + px)) / risk}
    return None


def coin_events(coin):
    df = load_1h(coin)
    h1 = {k: df[k].values for k in ("t", "o", "h", "l", "c")}
    b = resample(df, 4)
    t, o, h, l, c = (b[k].values for k in ("t", "o", "h", "l", "c"))
    A = atr(b)
    s = pd.Series(c)
    bw = (4 * s.rolling(20).std() / s.rolling(20).mean()).values
    bwq = pd.Series(bw).rolling(120).quantile(0.10).values
    out = []
    for i in range(130, len(c) - 20):
        tc = int(t[i]) + 4 * H
        if tc < A0 or (tc // H) % 24 not in SCAN_CLOSE_UTC:
            continue
        a = A[i]
        if not a > 0:
            continue
        i1 = int(np.searchsorted(h1["t"], tc))
        fut = slice(i + 1, i + 7)                               # next 24h of 4H bars
        rng24 = (h[fut].max() - l[fut].min()) / a if i + 7 <= len(c) else np.nan
        base = {"coin": coin, "t": tc, "range24_atr": rng24}
        flagged = []
        # COIL
        hi20, lo20 = h[i - 19:i + 1].max(), l[i - 19:i + 1].min()
        if bw[i] <= bwq[i] and ((hi20 - c[i]) <= a or (c[i] - lo20) <= a):
            mid = (hi20 + lo20) / 2
            up = run_trade(h1, i1, 1, "stop", hi20, mid, hi20 + 2 * (hi20 - mid), 48)
            dn = run_trade(h1, i1, -1, "stop", lo20, mid, lo20 - 2 * (mid - lo20), 48)
            # only the side that triggers first counts (one trade per coil)
            first = None
            if up and dn:
                first = None                                     # resolved below by fill time
            for side, res in ((1, up), (-1, dn)):
                if res:
                    flagged.append({"det": "COIL", "side": side, **res})
            if up and dn:                                        # keep only the earlier trigger
                flagged = [x for x in flagged if x["det"] != "COIL"]
                ju = next(j for j in range(i1, len(h1["t"])) if h1["h"][j] >= hi20)
                jd = next(j for j in range(i1, len(h1["t"])) if h1["l"][j] <= lo20)
                flagged.append({"det": "COIL", "side": 1 if ju <= jd else -1, **(up if ju <= jd else dn)})
            if not up and not dn:
                flagged.append({"det": "COIL", "side": 0, "filled": False, "r": np.nan})
        # SWING50 (both directions)
        for side in (1, -1):
            if side == 1:
                j0 = i - 30 + int(np.argmin(l[i - 30:i + 1]))
                jx = j0 + int(np.argmax(h[j0:i + 1]))
                start, ext = l[j0], h[jx]
            else:
                j0 = i - 30 + int(np.argmax(h[i - 30:i + 1]))
                jx = j0 + int(np.argmin(l[j0:i + 1]))
                start, ext = h[j0], l[jx]
            leg = abs(ext - start)
            if leg < 6 * a or i - jx > 12 or jx <= j0:
                continue
            retr = abs(ext - c[i]) / leg
            if 0.20 <= retr <= 0.45:
                lvl = ext - side * 0.5 * leg
                stp = ext - side * 0.786 * leg - side * 0.1 * a
                res = run_trade(h1, i1, side, "limit", lvl, stp, ext, 48)
                flagged.append({"det": "SWING50", "side": side, **(res or {"filled": False, "r": np.nan})})
        # DISP
        body = c[i] - o[i]
        if abs(body) >= 2 * A[i - 1]:
            side = 1 if body > 0 else -1
            lvl = (o[i] + c[i]) / 2
            stp = (l[i] - 0.1 * a) if side == 1 else (h[i] + 0.1 * a)
            res = run_trade(h1, i1, side, "limit", lvl, stp, lvl + side * 2 * abs(lvl - stp), 24)
            flagged.append({"det": "DISP", "side": side, **(res or {"filled": False, "r": np.nan})})
        if not flagged:
            out.append({**base, "det": None})
        for x in flagged:
            out.append({**base, **x})
    return out


if __name__ == "__main__":
    with ProcessPoolExecutor(8) as ex:
        X = pd.DataFrame([r for rows in ex.map(coin_events, config.COINS) for r in rows])
    ST = label(resample(load_1h("BTC"), 24))
    X["state"] = ST.state.reindex(X.t // DAY * DAY - DAY).values
    X["period"] = np.where(X.t < SPLIT, "old", "12m")
    X.to_pickle(os.path.join(config.DATA, "shortlist_events.pkl"))
    # (1) do flagged coins move more over the next 24h?
    rng = X.assign(flag=X.det.notna()).drop_duplicates(["coin", "t", "flag"]).groupby(["flag", "period"]).range24_atr.median().unstack().round(2)
    rng.insert(0, "coin flagged", ["no", "yes"][: len(rng)])
    rng_det = X[X.det.notna()].groupby(["det"]).range24_atr.median().round(2).rename("median next-24h range (ATR)").reset_index()
    # (2) per detector x side: hit rate and avg R after fill, both periods
    F = X[X.det.notna() & (X.side != 0)]
    rows = []
    for (det, side), g in F.groupby(["det", "side"]):
        row = {"setup": det, "side": "long" if side == 1 else "short", "flags": len(g)}
        ok = True
        for per in ("old", "12m"):
            gp = g[g.period == per]
            filled = gp[gp.filled == True]  # noqa: E712
            row["fill % " + per] = round(len(filled) / max(len(gp), 1) * 100)
            row["avg R " + per] = round(filled.r.mean(), 3)
            row["trades " + per] = len(filled)
            ok = ok and filled.r.mean() > 0
        row["useful"] = "yes" if ok else ""
        rows.append(row)
    R = pd.DataFrame(rows)
    SS = F[F.filled == True].groupby(["det", "side", "state"]).r.agg(["size", "mean"]).round(3).reset_index()  # noqa: E712
    SS["side"] = SS.side.map({1: "long", -1: "short"})
    SS.columns = ["setup", "side", "BTC state", "trades", "avg R"]
    print(rng.to_string(index=False)); print(rng_det.to_string(index=False)); print(R.to_string(index=False))
    write_report("shortlist detectors", [
        ("(1) Next-24h range (median, in 4H ATR units) for flagged vs other coins", rng), ("By setup", rng_det),
        ("(2) Levels: fill rate and avg R after the fill", R),
        ("By BTC state (context only, not used to pick)", SS)])
