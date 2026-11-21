"""Run strategies over the coins and save every trade, tagged with the market and coin regime at signal time.
    python3 backtest.py                    # every strategy, all 72 coins -> data/trades.pkl
    python3 backtest.py --only BRK,STD     # some strategies (merged into data/trades.pkl)
    python3 backtest.py --coins BTC,ETH
Rules: one open trade per strategy per coin; signals with a stop closer than 0.3 ATR are skipped.
"""
import argparse, inspect, os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

import config
import strategies
from lib import regime
from lib.data import load_1h, resample
from lib.execution import simulate
from lib.indicators import atr

H = 3600_000
DAY = 24 * H
TRADES = os.path.join(config.DATA, "trades.pkl")


def run_coin(args):
    coin, names, mreg = args
    btc_d = resample(load_1h("BTC"), 24)
    df1 = load_1h(coin)
    h1 = {k: df1[k].values for k in ("t", "o", "h", "l", "c")}
    bars = {4: resample(df1, 4), 24: resample(df1, 24)}
    btc1 = load_1h("BTC")
    ctx = {"btc": {4: resample(btc1, 4), 24: btc_d}}   # BTC bars for strategies that take a ctx argument
    creg = regime.coin(bars[24], btc_d)
    out = []
    for name in names:
        mod = strategies.load_all()[name]
        b = bars[mod.TIMEFRAME]
        T, C, A = b.t.values, b.c.values, atr(b)
        tf = mod.TIMEFRAME * H
        busy_until = 0
        gen = mod.signals(b, ctx) if len(inspect.signature(mod.signals).parameters) > 1 else mod.signals(b)
        for s in gen:
            t_close = int(T[s.i]) + tf
            if t_close < busy_until or not abs(C[s.i] - s.stop) >= 0.3 * A[s.i]:
                continue
            target = s.target_px
            if s.target_r is not None:
                target = C[s.i] + s.side * s.target_r * abs(C[s.i] - s.stop)
            if target is not None and (target - C[s.i]) * s.side <= 0:
                continue
            trail = None
            if s.trail is not None:
                k, lv = s.trail
                trail = (T[k] + tf, lv)
            res = simulate(h1, t_close, s.side, s.stop, target, trail, s.max_hours)
            if res is None:
                continue
            busy_until = res["t_out"]
            day = t_close // DAY * DAY
            m = mreg.loc[day] if day in mreg.index else None
            c = creg.loc[day] if day in creg.index else None
            res.update(coin=coin, strat=name, side=s.side, t_sig=t_close,
                       mtrend=m.mtrend if m is not None else None, mvol=m.mvol if m is not None else None,
                       ctrend=c.ctrend if c is not None else None, cchar=c.cchar if c is not None else None,
                       corr=float(c["corr"]) if c is not None else np.nan,
                       cvol=float(c.cvol) if c is not None else np.nan)
            out.append(res)
    return coin, out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--coins")
    a = ap.parse_args()
    allmods = strategies.load_all()
    names = a.only.split(",") if a.only else list(allmods)
    coins = a.coins.split(",") if a.coins else config.COINS
    mreg = regime.market(resample(load_1h("BTC"), 24))
    rows = []
    with ProcessPoolExecutor(8) as ex:
        for coin, res in ex.map(run_coin, [(c, names, mreg) for c in coins]):
            rows += res
    new = pd.DataFrame(rows)
    if os.path.exists(TRADES) and (a.only or a.coins):
        old = pd.read_pickle(TRADES)
        old = old[~(old.strat.isin(names) & old.coin.isin(coins))]
        new = pd.concat([old, new], ignore_index=True)
    new.to_pickle(TRADES)
    print("%d trades saved (%s)" % (len(new), ", ".join("%s %d" % kv for kv in new.strat.value_counts().sort_index().items())))
