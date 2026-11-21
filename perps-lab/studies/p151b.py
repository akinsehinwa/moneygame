"""Batch 2 of "151 Trading Strategies" adaptations (pre-registered in LEDGER.md before running).

    python3 studies/p151b.py --list
    python3 studies/p151b.py ALL

PAIRS     3.8   pairs trading: 10 most correlated non-overlapping coin pairs (90-day daily returns), re-picked weekly;
                each week short the pair member with the higher 7-day return, long the other (paper's rule).
ECO       3.9.1 / 14.4  multi-cluster mean reversion on ecosystems ("spark spread"): within each fixed group (an L1 and
                its ecosystem tokens) weights = -(7-day return - group mean); groups get equal gross; weekly.
PIVOT     3.14  daily pivot: long when an hourly close is above the pivot C, short below; take profit at R (long) /
                S (short), then no re-entry on that side until the next UTC day; 1h execution, equal weight per coin.
CROWDFADE 9.2   hedging pressure -> fade the crowd: global long/short account ratio, 7-day mean vs its own 90-day mean;
                short the 7 most crowded-long coins, long the 7 most crowded-short; weekly.
CROWDTOP  9.2   follow the "hedgers" -> top traders' position ratio divided by the global account ratio, 7-day mean vs
                90-day mean; long the 7 where top traders lean longest vs the crowd, short the 7 lowest; weekly.
DISPMOM   6.3   dispersion as a filter on MOM: run the batch-1 MOM book only while the cross-sectional dispersion of
                30-day returns is above its trailing 180-day median; flat otherwise.

Pass rule (all): net Sharpe >= 0.5 in both periods AND still positive in both periods without the book's 3 best
coins. Long/short books only (no long-only here).
"""
import sys

sys.argv = [sys.argv[0]] + (sys.argv[1:] or ["--list"])
_arg = sys.argv[1]
sys.argv = [sys.argv[0], "--list"]
import p151 as base  # noqa: E402  (shared panel, helpers, MOM)
from common import write_report  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import config  # noqa: E402
from lib import portfolio as pf  # noqa: E402
from lib.data import load_1h, load_metrics  # noqa: E402

P, C, R, E = base.P, base.C, base.R, base.E
DAY, H = 24 * 3600_000, 3600_000
REB = pd.Series(pf.rebalance_days(C.index, "W"), index=C.index)

ECOSYSTEMS = {
    "ETH": ["ETH", "ARB", "OP", "LDO", "ETHFI", "ENS", "PENDLE", "LINEA", "IMX", "ENA"],
    "SOL": ["SOL", "JUP", "PYTH", "JTO", "BONK", "WIF", "BOME", "PUMP"],
    "BTC": ["BTC", "STX", "ORDI"],
    "BNB": ["BNB", "ASTER"],
}


def PAIRS():
    lr = np.log(C).diff()
    W = pd.DataFrame(0.0, index=C.index, columns=C.columns)
    r7 = C.pct_change(7, fill_method=None)
    for d in C.index[REB.values]:
        i = C.index.get_loc(d)
        if i < 120:
            continue
        el = E.loc[d][E.loc[d]].index
        cm = lr.iloc[i - 89:i + 1][el].corr(min_periods=70)
        cm = cm.where(np.triu(np.ones(cm.shape, bool), 1)).stack().sort_values(ascending=False)
        used, n = set(), 0
        for (a, b), _ in cm.items():
            if a in used or b in used:
                continue
            ra, rb = r7.at[d, a], r7.at[d, b]
            if np.isnan(ra) or np.isnan(rb):
                continue
            rich, cheap = (a, b) if ra > rb else (b, a)
            W.at[d, rich], W.at[d, cheap] = -0.05, 0.05
            used |= {a, b}
            n += 1
            if n == 10:
                break
    return W, "W"


def ECO():
    r7 = C.pct_change(7, fill_method=None).where(E)
    W = pd.DataFrame(0.0, index=C.index, columns=C.columns)
    for g, coins in ECOSYSTEMS.items():
        x = r7[coins]
        dm = -(x.sub(x.mean(axis=1), axis=0))
        g_w = dm.div(dm.abs().sum(axis=1).where(dm.abs().sum(axis=1) > 0), axis=0).fillna(0.0) / len(ECOSYSTEMS)
        W[coins] = W[coins] + g_w
    return W, "W"


def pivot_coin(coin):
    """Daily net return series of the pivot strategy on one coin (1h execution)."""
    df = load_1h(coin)
    t, o, h, l, c = (df[k].values for k in ("t", "o", "h", "l", "c"))
    day = t // DAY
    g = df.assign(day=day).groupby("day").agg(H=("h", "max"), L=("l", "min"), C=("c", "last"))
    piv = ((g.H + g.L + g.C) / 3).shift(1)
    Rl, Sl = (2 * piv - g.L.shift(1)), (2 * piv - g.H.shift(1))
    Pc, Pr, Ps = piv.reindex(day).values, Rl.reindex(day).values, Sl.reindex(day).values
    cost = config.FEE_PER_SIDE + config.SLIP_PER_SIDE
    ret = np.zeros(len(t))
    pos, blk_l, blk_s, cur_day = 0, False, False, -1
    for j in range(1, len(t)):
        if day[j] != cur_day:
            cur_day, blk_l, blk_s = day[j], False, False
        # bar j with the position chosen at the close of bar j-1
        if pos == 1:
            if h[j] >= Pr[j]:
                ret[j] = max(Pr[j], o[j]) / c[j - 1] - 1 - cost
                pos, blk_l = 0, True
            else:
                ret[j] = c[j] / c[j - 1] - 1
        elif pos == -1:
            if l[j] <= Ps[j]:
                ret[j] = 1 - min(Ps[j], o[j]) / c[j - 1] - cost
                pos, blk_s = 0, True
            else:
                ret[j] = 1 - c[j] / c[j - 1]
        if np.isnan(Pc[j]):
            continue
        want = 1 if c[j] > Pc[j] else -1
        if (want == 1 and blk_l) or (want == -1 and blk_s):
            want = 0 if pos != want else pos
        if want != pos:
            ret[j] -= cost * abs(want - pos)
            pos = want
    return pd.Series(ret, index=t).groupby(day * DAY).sum()


def PIVOT():
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(8) as ex:
        cols = dict(zip(config.COINS, ex.map(pivot_coin, config.COINS)))
    D = pd.DataFrame(cols).reindex(C.index).where(E)
    return D, "returns"           # already net daily returns per coin: equal weight across eligible coins


def metrics_panel(col):
    return pd.DataFrame({c: load_metrics(c).set_index("t")[col] for c in config.COINS}).reindex(C.index)


def CROWDFADE():
    g = metrics_panel("global_ls")
    score = g.rolling(7, min_periods=5).mean() / g.rolling(90, min_periods=60).mean() - 1
    return pf.long_short(-score, E & score.notna(), 7), "W"


def CROWDTOP():
    tp, g = metrics_panel("top_pos"), metrics_panel("global_ls")
    x = tp / g
    score = x.rolling(7, min_periods=5).mean() / x.rolling(90, min_periods=60).mean() - 1
    return pf.long_short(score, E & score.notna(), 7), "W"


def DISPMOM():
    W, every = base.MOM()
    disp = C.pct_change(30, fill_method=None).where(E).std(axis=1)
    on = disp > disp.rolling(180, min_periods=120).median()
    return W.mul(on.astype(float), axis=0), every


STRATS = {"PAIRS": PAIRS, "ECO": ECO, "PIVOT": PIVOT, "CROWDFADE": CROWDFADE, "CROWDTOP": CROWDTOP, "DISPMOM": DISPMOM}


def result(name):
    W, every = STRATS[name]()
    if every == "returns":
        net = W.mean(axis=1).fillna(0.0)
        res = pd.DataFrame({"net": net, "gross": net, "funding": 0.0, "cost": 0.0, "long": np.nan, "short": np.nan})
        contrib = W.fillna(0.0) / W.notna().sum(axis=1).replace(0, np.nan).values[:, None]
        return res, contrib.fillna(0.0), "funding not modeled (intraday flips)"
    res = pf.run(P, W, every)
    Wm = W.reindex(index=C.index, columns=C.columns).fillna(0.0)
    Wm = Wm.where(pd.Series(pf.rebalance_days(Wm.index, every), index=Wm.index), np.nan).ffill().fillna(0.0)
    h = Wm.shift(1).fillna(0.0)
    return res, h * R.fillna(0.0) - h * P["F"], ""


def evaluate(name):
    res, contrib, note = result(name)
    B = int(pd.Timestamp(config.SPLIT, tz="UTC").timestamp() * 1000)
    row = {"strategy": name}
    ok = True
    for per, x in pf.periods(res).items():
        m = pf.metrics(x)
        sel = (contrib.index >= B) if per == "12m" else (contrib.index < B) & (contrib.index >= x.index.min())
        c = contrib[sel].sum().sort_values()
        ex3 = c.sum() - c.tail(3).sum()
        row.update({"ann % " + per: m.get("ann %"), "Sharpe " + per: m.get("Sharpe"), "maxDD % " + per: m.get("maxDD %"),
                    "w/o best 3 " + per: round(ex3, 2)})
        ok = ok and (m.get("Sharpe") or -9) >= 0.5 and ex3 > 0
    row["verdict"] = "PASS" if ok else "fail"
    row["note"] = note
    return row


if __name__ == "__main__":
    if _arg == "--list":
        print(__doc__)
        sys.exit()
    names = list(STRATS) if _arg == "ALL" else _arg.split(",")
    rows = []
    for n in names:
        r = evaluate(n)
        rows.append(r)
        print(n, r["verdict"], "Sharpe old %s / 12m %s, w/o best 3: %s / %s" % (
            r["Sharpe old"], r["Sharpe 12m"], r["w/o best 3 old"], r["w/o best 3 12m"]), flush=True)
    write_report("p151 batch 2 " + ("all" if _arg == "ALL" else _arg.lower()),
                 [("Rules", "Net of 0.06%/side costs and funding (except PIVOT). Pass = Sharpe >= 0.5 in both periods "
                   "AND positive in both periods without the book's 3 best coins."), ("Results", pd.DataFrame(rows))])
