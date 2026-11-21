"""Helpers for cross-coin studies (filters or strategies that need every coin at once)."""
import os, sys

LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LAB)

import pandas as pd  # noqa: E402

import config  # noqa: E402
import evaluate  # noqa: E402
from lib.data import load_1h, resample  # noqa: E402

H = 3600_000


def bars(coin, hours):
    return resample(load_1h(coin), hours)


def write_report(title, sections):
    """sections: list of (heading, DataFrame or text)."""
    import datetime as dt
    out = ["# %s (%s)" % (title, dt.date.today().isoformat()), ""]
    for h, body in sections:
        out += ["## " + h, "", evaluate.md(body) if isinstance(body, pd.DataFrame) else str(body), ""]
    text = "\n".join(out)
    f = os.path.join(config.RESULTS, "%s-%s.md" % (dt.date.today().isoformat(), title.lower().replace(" ", "-")))
    open(f, "w").write(text)
    print(text)
    print("written:", f)


def tag_and_save(trades, name):
    """Tag study trades with market/coin regimes like backtest.py does, and merge them into data/trades.pkl."""
    import numpy as np
    from lib import regime
    DAY = 24 * H
    btc_d = bars("BTC", 24)
    mreg = regime.market(btc_d)
    out = []
    for coin, x in trades.groupby("coin"):
        creg = regime.coin(bars(coin, 24), btc_d)
        day = (x.t_sig // DAY) * DAY
        m = mreg.reindex(day.values)
        c = creg.reindex(day.values)
        out.append(x.assign(mtrend=m.mtrend.values, mvol=m.mvol.values, ctrend=c.ctrend.values,
                            cchar=c.cchar.values, corr=c["corr"].values, cvol=c.cvol.values))
    new = pd.concat(out, ignore_index=True).assign(strat=name)
    f = os.path.join(config.DATA, "trades.pkl")
    old = pd.read_pickle(f)
    pd.concat([old[old.strat != name], new], ignore_index=True).to_pickle(f)
    print("%d %s trades saved" % (len(new), name))
