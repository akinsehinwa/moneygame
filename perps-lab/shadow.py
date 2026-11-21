"""Shadow book: paper-trade the strategies that passed the backtest, forward in time, untouched.

    python3 shadow.py update     # fetch data, freeze any new weekly rebalance, mark PnL, write shadow/STATUS.md
    python3 shadow.py status     # just re-mark and print

Rules (so the forward test stays honest)
- A rebalance is frozen into shadow/book.json the first time its data exists (the Sunday bar that closes at Monday
  00:00 UTC). Frozen weights are never edited or regenerated. Each entry records when it was frozen.
- Only rebalances on or after START count. Missed runs are caught up from the data as it stood (the signal only
  uses closes up to that Sunday), and are marked "late" so it's visible.
- PnL is recomputed from the frozen weights on every run: daily closes, 0.06%/side costs, funding. Binance only
  archives funding monthly, so the current month counts zero funding until its file is published; the next run
  after that fills it in automatically.
"""
import datetime as dt, json, os, sys

import numpy as np
import pandas as pd

import config
from lib import portfolio as pf
from lib.data import download_all, download_funding, download_metrics

START = "2026-11-22"            # first rebalance bar (Sunday 2026-11-22, closes Monday 2026-11-23 08:00 SGT = 00:00 UTC)
SHADOW = ["MOM", "SECTOR", "CROWDFADE"]   # strategies in the shadow book (see STRATEGIES.md)
DIR = os.path.join(config.LAB, "shadow")
BOOK = os.path.join(DIR, "book.json")
DAY = 24 * 3600_000
# Backtest expectations, for comparison (results/2026-11-21-p151-all.md).
EXPECT = {"MOM": {"Sharpe old": 0.71, "Sharpe 12m": 1.12, "ann % 12m": 30.7},
          "SECTOR": {"Sharpe old": 0.83, "Sharpe 12m": 1.32, "ann % 12m": 17.9},
          "CROWDFADE": {"Sharpe old": 0.92, "Sharpe 12m": 1.85, "ann % 12m": 50.9}}   # results/2026-11-21-p151-batch-2-all.md


def fetch():
    from concurrent.futures import ThreadPoolExecutor
    list(download_all())
    with ThreadPoolExecutor(12) as ex:
        list(ex.map(download_funding, config.COINS))
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(download_metrics, config.COINS))


def load_book():
    return json.load(open(BOOK)) if os.path.exists(BOOK) else {"start": START, "rebalances": {}}


def freeze(book, P):
    sys.argv = [sys.argv[0], "--list"]
    sys.path.insert(0, os.path.join(config.LAB, "studies"))
    import p151
    import p151b
    strats = {**p151.STRATS, **p151b.STRATS}
    start_ms = int(pd.Timestamp(START, tz="UTC").timestamp() * 1000)
    now = dt.datetime.now(dt.timezone.utc)
    new = 0
    for name in SHADOW:
        W, every = strats[name]()
        days = W.index[pf.rebalance_days(W.index, every) & (W.index >= start_ms)]
        rb = book["rebalances"].setdefault(name, {})
        for d in days:
            key = pd.Timestamp(int(d), unit="ms").strftime("%Y-%m-%d")
            if key in rb or P["C"].loc[d].notna().sum() < 50:      # already frozen, or the bar isn't complete yet
                continue
            w = W.loc[d]
            w = w[w.abs() > 1e-9].round(5)
            closes_at = pd.Timestamp(int(d) + DAY, unit="ms", tz="UTC")
            rb[key] = {"weights": w.to_dict(), "frozen_at": now.strftime("%Y-%m-%d %H:%M UTC"),
                       "late": (now - closes_at.to_pydatetime()).total_seconds() > 36 * 3600}
            new += 1
    return new


def mark(book, P):
    out = {}
    for name, rb in book["rebalances"].items():
        if not rb:
            continue
        W = pd.DataFrame(0.0, index=P["C"].index, columns=P["C"].columns)
        for key, e in rb.items():
            d = int(pd.Timestamp(key, tz="UTC").timestamp() * 1000)
            for c, w in e["weights"].items():
                W.loc[d, c] = w
        res = pf.run(P, W, "W")
        first = int(pd.Timestamp(min(rb), tz="UTC").timestamp() * 1000) + DAY
        out[name] = res[res.index >= first]
    return out


def write_status(book, marks):
    lines = ["# Shadow book status", "",
             "Paper only. Frozen weekly weights, marked to Binance daily closes with costs and funding.",
             "Started %s. Updated %s." % (START, dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")), ""]
    if not marks:
        lines += ["No rebalance frozen yet: the first one is the bar that closes Monday 2026-11-23 08:00 SGT.", ""]
    for name in SHADOW:
        rb = book["rebalances"].get(name, {})
        x = marks.get(name)
        lines += ["## %s" % name, ""]
        if x is None or x.empty:
            lines += ["No marked days yet (%d rebalance(s) frozen)." % len(rb), ""]
        else:
            eq = (1 + x.net).cumprod()
            wk = (1 + x.net).groupby(pd.to_datetime(x.index, unit="ms").to_period("W-SUN")).prod() - 1
            lines += ["| metric | shadow | backtest |", "|---|---|---|",
                      "| days marked | %d | |" % len(x),
                      "| total return | %+.1f%% | |" % ((eq.iloc[-1] - 1) * 100),
                      "| annualized | %+.1f%% | %+.1f%% (last 12m) |" % (x.net.mean() * 365 * 100, EXPECT[name]["ann % 12m"]),
                      "| Sharpe | %s | %.2f old / %.2f last 12m |" % (
                          "%.2f" % (x.net.mean() / x.net.std() * np.sqrt(365)) if len(x) > 20 and x.net.std() > 0 else "n/a (< 20 days)",
                          EXPECT[name]["Sharpe old"], EXPECT[name]["Sharpe 12m"]),
                      "| max drawdown | %.1f%% | |" % ((eq / eq.cummax() - 1).min() * 100),
                      "| funding | %+.2f%% | |" % (x.funding.sum() * 100),
                      "| costs | %+.2f%% | |" % (x.cost.sum() * 100), "",
                      "Weekly returns: " + ", ".join("%s %+.1f%%" % (str(k.end_time.date()), v * 100) for k, v in wk.items()), ""]
        if rb:
            last = max(rb)
            w = pd.Series(rb[last]["weights"]).sort_values()
            lines += ["Current positions (rebalance %s, frozen %s%s):" % (last, rb[last]["frozen_at"],
                                                                         ", LATE" if rb[last]["late"] else ""), "",
                      "| side | coin | weight |", "|---|---|---|"]
            lines += ["| %s | %s | %+.1f%% |" % ("long" if v > 0 else "short", c, v * 100) for c, v in w[::-1].items()]
            lines += [""]
    open(os.path.join(DIR, "STATUS.md"), "w").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    os.makedirs(DIR, exist_ok=True)
    if cmd == "update":
        fetch()
    P = pf.build_panel(force=(cmd == "update"))
    book = load_book()
    if cmd == "update":
        n = freeze(book, P)
        json.dump(book, open(BOOK, "w"), indent=1, sort_keys=True)
        print("froze %d new rebalance(s)" % n)
    write_status(book, mark(book, P))
