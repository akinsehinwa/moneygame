#!/usr/bin/env python3
"""Historical backtest of the regime classifier + playbook (daily bars, 1999 -> today).

Same rules as live trading, applied to daily data:
  * signals use data up to the close of day t; limit orders are valid for day t+1 only
  * buy limit fills if low <= limit at min(limit, open); stop fills at min(stop, open);
    target at max(target, open); stop wins ties; on the fill day only the stop is checked
  * max 25% of equity per position, ~23% default size, risk per trade capped at 2% of equity
  * long only; "INV" is a synthetic -1x daily SPY (stand-in for SH, which only exists from 2006)

Modes:
  python3 sim/backtest.py                 # standalone strategies (ungated) + adaptive portfolio
  python3 sim/backtest.py --optimize      # grid search on TRAIN, report on VALIDATE (not TEST)
  python3 sim/backtest.py --test          # also print the held-out TEST period (use once)
Data: sim/data/*.json (adjusted OHLC from Yahoo), refreshed by python3 sim/fetch_history.py.
"""
import itertools, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SECTORS = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
DEFENSIVE, CYCLICAL = ["XLV", "XLP", "XLU"], ["XLK", "XLY", "XLF", "XLI"]
PERIODS = {"train": ("1999-01-01", "2014-12-31"), "validate": ("2015-01-01", "2020-12-31"),
           "test": ("2021-01-01", "2099-12-31")}
SLIP = 0.0002  # 2 bp adverse slippage on every fill

DEFAULT = {"stop_atr": 1.5, "target_r": 2.5, "breadth_off": 3, "pullback_ema": 10,
           "rsi_entry": 10, "trend_hold": 20, "size": 0.23, "trail_atr": 3.0, "pb": "v1"}


# ---------------------------------------------------------------- data + indicators
def load():
    raw = {s: json.load(open(os.path.join(DATA, f"{s}.json"))) for s in SECTORS + ["SPY", "VIX"]}
    dates = [r[0] for r in raw["SPY"]]
    idx = {s: {r[0]: r for r in rows} for s, rows in raw.items()}
    bars = {}
    for s in SECTORS + ["SPY"]:
        rows = [idx[s].get(d) for d in dates]
        for i, r in enumerate(rows):  # forward-fill rare gaps
            if r is None:
                rows[i] = [dates[i]] + [rows[i - 1][4]] * 4
        bars[s] = {k: [r[j] for r in rows] for k, j in (("o", 1), ("h", 2), ("l", 3), ("c", 4))}
    vix, last = [], 20.0
    for d in dates:
        last = idx["VIX"][d][4] if d in idx["VIX"] else last
        vix.append(last)
    # synthetic inverse SPY (-1x daily, close-to-close), with intraday mapped from SPY
    sp = bars["SPY"]
    o, h, l, c = [100.0], [100.0], [100.0], [100.0]
    for i in range(1, len(dates)):
        pc, base = sp["c"][i - 1], c[-1]
        f = lambda x: base * (1 - (x / pc - 1))
        o.append(f(sp["o"][i])); h.append(f(sp["l"][i])); l.append(f(sp["h"][i])); c.append(f(sp["c"][i]))
    bars["INV"] = {"o": o, "h": h, "l": l, "c": c}
    return dates, bars, vix


def sma(x, n):
    out, s = [None] * len(x), 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n: s -= x[i - n]
        if i >= n - 1: out[i] = s / n
    return out


def ema(x, n):
    out, e, k = [], x[0], 2 / (n + 1)
    for v in x:
        e += (v - e) * k
        out.append(e)
    return out


def atr(b, n=14):
    tr = [b["h"][0] - b["l"][0]] + [max(b["h"][i] - b["l"][i], abs(b["h"][i] - b["c"][i - 1]),
                                       abs(b["l"][i] - b["c"][i - 1])) for i in range(1, len(b["c"]))]
    return sma(tr, n)


def rsi(x, n=2):
    out, ag, al = [None] * len(x), 0.0, 0.0
    for i in range(1, len(x)):
        g, l = max(x[i] - x[i - 1], 0), max(x[i - 1] - x[i], 0)
        if i <= n:
            ag += g / n; al += l / n
        else:
            ag = (ag * (n - 1) + g) / n; al = (al * (n - 1) + l) / n
        if i >= n: out[i] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def indicators(bars):
    ind = {}
    for s, b in bars.items():
        c = b["c"]
        ind[s] = {"sma5": sma(c, 5), "sma20": sma(c, 20), "sma50": sma(c, 50), "sma200": sma(c, 200),
                  "ema5": ema(c, 5), "ema10": ema(c, 10), "ema20": ema(c, 20), "atr": atr(b), "rsi2": rsi(c)}
    return ind


# ---------------------------------------------------------------- regime (mirrors sim/regime.py)
def regimes(dates, bars, vix, ind):
    out = [None] * len(dates)
    sp, si = bars["SPY"]["c"], ind["SPY"]
    for i in range(205, len(dates)):
        px, s20, s50, s200 = sp[i], si["sma20"][i], si["sma50"][i], si["sma200"][i]
        slope = s20 / si["sma20"][i - 5] - 1
        trend = "up" if px > s50 > s200 and slope > 0 else "down" if px < s50 and slope < 0 else "range"
        v = vix[i]
        vol = "low" if v < 16 else "normal" if v < 22 else "high" if v < 30 else "extreme"
        r20 = {s: bars[s]["c"][i] / bars[s]["c"][i - 20] - 1 for s in SECTORS}
        spread = (sum(r20[s] for s in DEFENSIVE) / 3 - sum(r20[s] for s in CYCLICAL) / 4) * 100
        lead = "risk-off" if spread > 2 else "risk-on" if spread < -2 else "mixed"
        breadth = sum(1 for s in SECTORS if bars[s]["c"][i] > ind[s]["ema20"][i])
        out[i] = {"trend": trend, "vol": vol, "lead": lead, "breadth": breadth,
                  "label": f"{trend}/{vol}/{lead}"}
    return out


def playbook(rg, p):
    """Allowed strategies and max exposure for a regime: the STRATEGY.md table as code."""
    t, v, b = rg["trend"], rg["vol"], rg["breadth"]
    if p.get("pb") == "v3":  # v3: buy oversold dips in every regime (fear = opportunity); trend-hold in uptrends
        if t == "up" and v in ("low", "normal"): return ["trend-hold", "range-mean-reversion"], 1.0
        return ["capitulation-bounce", "range-mean-reversion"], 1.0
    if p.get("pb") == "v2":  # v2: ride trends with trailing stops; dip-buy in ranges; defend in downtrends
        if v == "extreme": return ["capitulation-bounce", "range-mean-reversion"], 0.5
        if t == "up": return ["trend-hold"], 1.0 if v != "high" else 0.75
        if t == "range": return ["range-mean-reversion", "trend-hold"], 0.75
        if b <= p["breadth_off"]: return ["inverse-index-trend"], 0.3
        return ["range-mean-reversion", "inverse-index-trend"] + (
            ["defensive-leader-pullback"] if rg["lead"] == "risk-off" else []), 0.6
    if t == "up":
        if v in ("low", "normal"): return ["trend-leader-pullback"], 1.0
        if v == "high": return ["trend-leader-pullback"], 0.6
        return ["capitulation-bounce"], 0.4
    if t == "range":
        if v == "extreme": return ["capitulation-bounce"], 0.4
        return ["range-mean-reversion"], 0.7
    if v == "extreme": return ["capitulation-bounce"], 0.4
    if b <= p["breadth_off"]: return ["inverse-index-trend"], 0.3
    strats = ["inverse-index-trend"] + (["defensive-leader-pullback"] if rg["lead"] == "risk-off" else [])
    return strats, 0.7


# ---------------------------------------------------------------- signals (close of day i -> order for i+1)
def signals(i, strat, bars, ind, p):
    out = []  # (symbol, limit, stop, target, max_hold_days, score, exit_rule)
    if strat in ("trend-leader-pullback", "defensive-leader-pullback"):
        uni = SECTORS if strat == "trend-leader-pullback" else DEFENSIVE
        look = 63 if strat == "trend-leader-pullback" else 20
        mom = {s: bars[s]["c"][i] / bars[s]["c"][i - look] - 1 for s in uni}
        spy_mom = bars["SPY"]["c"][i] / bars["SPY"]["c"][i - look] - 1
        top = sorted(uni, key=mom.get, reverse=True)[:3]
        e = "ema10" if p["pullback_ema"] == 10 else "ema20"
        for s in top:
            c, x = bars[s]["c"][i], ind[s]
            if mom[s] <= spy_mom or c <= x["sma50"][i] or c > x[e][i]:
                continue
            lim = c * 0.997
            stop = lim - p["stop_atr"] * x["atr"][i]
            r = 2.0 if strat == "defensive-leader-pullback" else p["target_r"]
            out.append((s, lim, stop, lim + r * (lim - stop), p["trend_hold"], mom[s], None))
    elif strat == "trend-hold":
        mom = {x: bars[x]["c"][i] / bars[x]["c"][i - 63] - 1 for x in SECTORS}
        for x in sorted(SECTORS, key=mom.get, reverse=True)[:4]:
            c, xi = bars[x]["c"][i], ind[x]
            if c <= xi["sma50"][i] or mom[x] <= 0:
                continue
            stop = c - p["trail_atr"] * xi["atr"][i]
            out.append((x, c, stop, c + 6 * (c - stop), 120, mom[x], "trail"))
    elif strat == "range-mean-reversion":
        for s in SECTORS + ["SPY"]:
            c, x = bars[s]["c"][i], ind[s]
            if x["rsi2"][i] is None or x["rsi2"][i] >= p["rsi_entry"]:
                continue
            if c <= x["sma200"][i] and not p.get("_fear"):  # below the 200-day only when fear is high (v3)
                continue
            stop = c - p["stop_atr"] * x["atr"][i]
            out.append((s, c, stop, c + 1.5 * (c - stop), 7, -x["rsi2"][i], "sma5"))
    elif strat == "inverse-index-trend":
        sp, x = bars["SPY"], ind["SPY"]
        failed_bounce = (sp["h"][i] >= x["ema20"][i] * 0.995 and sp["c"][i] < sp["o"][i]
                         and sp["c"][i] < x["ema20"][i] and sp["c"][i] < x["sma50"][i])
        if failed_bounce:
            inv = bars["INV"]["c"][i]
            d = (sp["h"][i] - sp["c"][i]) / sp["c"][i] + 0.5 * x["atr"][i] / sp["c"][i]
            stop = inv * (1 - d)
            out.append(("INV", inv, stop, inv + 1.5 * (inv - stop), 10, 1.0, None))
    elif strat == "capitulation-bounce":
        sp = bars["SPY"]
        rngp = sp["h"][i] - sp["l"][i]
        if (rngp > 0 and sp["c"][i] > sp["o"][i] and (sp["c"][i] - sp["l"][i]) / rngp > 0.6
                and sp["c"][i] / sp["c"][i - 5] - 1 < -0.05):
            c, stop = sp["c"][i], sp["l"][i]
            if c - stop > 0:
                out.append(("SPY", c, stop, c + 1.5 * (c - stop), 5, 1.0, None))
    return sorted(out, key=lambda z: z[5], reverse=True)


# ---------------------------------------------------------------- portfolio simulation
def simulate(dates, bars, ind, rg, p, mode="adaptive", only=None, start="1999-01-01", end="2099-12-31"):
    """mode='adaptive': regime-gated playbook. mode='standalone': run `only` strategy every day."""
    cash, pos, orders, trades, curve = 100.0, [], [], [], []
    first = next(i for i, d in enumerate(dates) if d >= start and rg[i] is not None)
    last = max(i for i, d in enumerate(dates) if d <= end)
    for i in range(first, last + 1):
        # 1) fill yesterday's orders (valid today only)
        for (s, lim, stop, tgt, hold, strat, regime, qty, exit_rule) in orders:
            b = bars[s]
            if b["l"][i] <= lim and qty * lim <= cash + 1e-9:
                px = min(lim, b["o"][i]) * (1 + SLIP)
                cash -= qty * px
                p_ = {"s": s, "qty": qty, "entry": px, "stop": stop, "tgt": tgt, "i0": i, "hold": hold,
                      "strat": strat, "regime": regime, "risk": px - stop, "exit_rule": exit_rule}
                if b["l"][i] <= stop:  # same-bar stop: assume worst
                    ex = min(stop, px) * (1 - SLIP)
                    cash += qty * ex; trades.append(dict(p_, exit=ex, xi=i, why="stop"))
                else:
                    pos.append(p_)
        orders = []
        # 2) manage open positions (bars after the fill bar)
        for p_ in list(pos):
            if p_["i0"] == i:
                continue
            b, s = bars[p_["s"]], p_["s"]
            ex = why = None
            if p_["exit_rule"] == "trail":  # chandelier stop, raised at the prior close (only tightens)
                p_["stop"] = max(p_["stop"], b["c"][i - 1] - p["trail_atr"] * ind[s]["atr"][i - 1])
            if b["l"][i] <= p_["stop"]:
                ex, why = min(p_["stop"], b["o"][i]), "stop"
            elif b["h"][i] >= p_["tgt"]:
                ex, why = max(p_["tgt"], b["o"][i]), "target"
            elif p_["exit_rule"] == "sma5" and b["c"][i] > ind[s]["sma5"][i]:
                ex, why = b["c"][i], "sma5"
            elif p_["exit_rule"] == "trail" and rg[i]["trend"] == "down":
                ex, why = b["c"][i], "regime"
            elif i - p_["i0"] >= p_["hold"]:
                ex, why = b["c"][i], "time"
            if ex is not None:
                ex *= (1 - SLIP)
                cash += p_["qty"] * ex
                trades.append(dict(p_, exit=ex, xi=i, why=why)); pos.remove(p_)
        eq = cash + sum(p_["qty"] * bars[p_["s"]]["c"][i] for p_ in pos)
        curve.append((dates[i], eq, (eq - cash) / eq))
        if i == last:
            break
        # 3) new orders for tomorrow
        allowed, cap = (playbook(rg[i], p) if mode == "adaptive" else ([only], 1.0))
        invested = sum(p_["qty"] * bars[p_["s"]]["c"][i] for p_ in pos)
        held = {p_["s"] for p_ in pos}
        size = p["size"] * (0.5 if mode == "adaptive" and rg[i]["trend"] == "up" and rg[i]["vol"] == "high" else 1)
        budget = cap * eq - invested
        avail = cash
        for strat in allowed:
            pp = dict(p, _fear=(p.get("pb") == "v3" and rg[i]["vol"] in ("high", "extreme")))
            for (s, lim, stop, tgt, hold, _, exit_rule) in signals(i, strat, bars, ind, pp):
                if s in held or len(pos) + len(orders) >= 4:
                    continue
                risk_pct = (lim - stop) / lim
                if risk_pct <= 0:
                    continue
                notional = min(size * eq, 0.25 * eq, 0.02 * eq / risk_pct, budget, avail)
                if notional < 0.05 * eq:
                    continue
                orders.append((s, lim, stop, tgt, hold, strat, rg[i]["label"], notional / lim, exit_rule))
                held.add(s); budget -= notional; avail -= notional
    return trades, curve


# ---------------------------------------------------------------- metrics
def curve_stats(curve):
    eq = [c[1] for c in curve]
    expo = sum(c[2] for c in curve) / len(curve) if len(curve[0]) > 2 else 1.0
    yrs = max(len(eq) / 252, 1e-9)
    rets = [eq[k] / eq[k - 1] - 1 for k in range(1, len(eq))]
    mu = sum(rets) / len(rets) if rets else 0
    sd = math.sqrt(sum((r - mu) ** 2 for r in rets) / len(rets)) if rets else 0
    peak, mdd = eq[0], 0.0
    for e in eq:
        peak = max(peak, e); mdd = min(mdd, e / peak - 1)
    cagr = (eq[-1] / eq[0]) ** (1 / yrs) - 1
    return {"total": eq[-1] / eq[0] - 1, "cagr": cagr, "maxdd": mdd,
            "sharpe": (mu / sd * math.sqrt(252)) if sd else 0, "mar": cagr / abs(mdd) if mdd else 0,
            "expo": expo}


def spy_curve(dates, bars, start, end):
    c = bars["SPY"]["c"]
    return [(d, 100 * c[i] / c[next(k for k, x in enumerate(dates) if x >= start)])
            for i, d in enumerate(dates) if start <= d <= end]


def trade_stats(trades, key):
    g = {}
    for t in trades:
        g.setdefault(t[key], []).append((t["exit"] - t["entry"]) / t["risk"] if t["risk"] > 0 else 0)
    return {k: {"n": len(v), "win": sum(1 for r in v if r > 0) / len(v), "avgR": sum(v) / len(v)}
            for k, v in g.items()}


def fmt(st):
    return (f"total {st['total']:+7.1%}  CAGR {st['cagr']:+6.1%}  maxDD {st['maxdd']:6.1%}  "
            f"Sharpe {st['sharpe']:5.2f}  MAR {st['mar']:5.2f}  invested {st['expo']:4.0%}")


def run_report(dates, bars, ind, rg, p, periods):
    strats = ["trend-hold", "trend-leader-pullback", "defensive-leader-pullback", "range-mean-reversion",
              "inverse-index-trend", "capitulation-bounce"]
    for name in periods:
        start, end = PERIODS[name]
        print(f"\n=================== {name.upper()} {start} .. {min(end, dates[-1])} ===================")
        print(f"SPY buy&hold            {fmt(curve_stats(spy_curve(dates, bars, start, end)))}")
        for pb in ("v1", "v2", "v3"):
            tr, cv = simulate(dates, bars, ind, rg, dict(p, pb=pb), "adaptive", start=start, end=end)
            print(f"ADAPTIVE playbook {pb}    {fmt(curve_stats(cv))}  trades {len(tr)}")
        for s in strats:
            t2, c2 = simulate(dates, bars, ind, rg, p, "standalone", only=s, start=start, end=end)
            print(f"  standalone {s:26} {fmt(curve_stats(c2))}  trades {len(t2)}")
        print("  adaptive trades by strategy:")
        for k, v in sorted(trade_stats(tr, "strat").items()):
            print(f"    {k:28} n={v['n']:4}  win {v['win']:5.1%}  avgR {v['avgR']:+.2f}")
    return


def regime_matrix(dates, bars, ind, rg, p, start, end):
    """Each strategy run ungated; avg R grouped by the regime at entry -> 'what works where'."""
    strats = ["trend-hold", "trend-leader-pullback", "defensive-leader-pullback", "range-mean-reversion",
              "inverse-index-trend", "capitulation-bounce"]
    print(f"\n----- what works where ({start}..{end}): avgR (n) by entry regime, strategies ungated -----")
    table, labels = {}, set()
    for s in strats:
        tr, _ = simulate(dates, bars, ind, rg, p, "standalone", only=s, start=start, end=end)
        for t in tr:
            key = t["regime"].split("/")[0] + "/" + t["regime"].split("/")[1]
            table.setdefault((s, key), []).append((t["exit"] - t["entry"]) / t["risk"])
            labels.add(key)
    order = [f"{t}/{v}" for t in ("up", "range", "down") for v in ("low", "normal", "high", "extreme")]
    cols = [l for l in order if l in labels]
    print(f"{'strategy':28}" + "".join(f"{c:>17}" for c in cols))
    for s in strats:
        row = ""
        for c in cols:
            v = table.get((s, c), [])
            row += f"{(sum(v)/len(v)):+8.2f} ({len(v):4})" if v else f"{'-':>17}"
        print(f"{s:28}{row}")


def optimize(dates, bars, ind, rg):
    grid = {"pb": ["v1", "v2", "v3"], "stop_atr": [1.0, 1.5, 2.0, 2.5], "target_r": [1.5, 2.5, 3.5],
            "breadth_off": [2, 3], "rsi_entry": [5, 10, 15], "trail_atr": [2.5, 3.0, 4.0]}
    keys = list(grid)
    res = []
    for combo in itertools.product(*grid.values()):
        p = dict(DEFAULT, **dict(zip(keys, combo)))
        _, cv = simulate(dates, bars, ind, rg, p, "adaptive", start=PERIODS["train"][0], end=PERIODS["train"][1])
        res.append((curve_stats(cv)["mar"], p))
    res.sort(key=lambda z: z[0], reverse=True)
    print("\nTop 5 parameter sets on TRAIN (ranked by MAR = CAGR / |maxDD|), then VALIDATE:")
    for mar, p in res[:5]:
        _, cv = simulate(dates, bars, ind, rg, p, "adaptive", start=PERIODS["validate"][0], end=PERIODS["validate"][1])
        sub = {k: p[k] for k in keys}
        print(f"  train MAR {mar:5.2f} | validate {fmt(curve_stats(cv))} | {sub}")
    base = [m for m, p in res if all(p[k] == DEFAULT[k] for k in keys)][0]
    print(f"  (default params: train MAR {base:.2f}; {len(res)} combos tested)")
    return res[0][1]


if __name__ == "__main__":
    dates, bars, vix = load()
    ind = indicators(bars)
    rg = regimes(dates, bars, vix, ind)
    if "--optimize" in sys.argv:
        optimize(dates, bars, ind, rg)
        sys.exit()
    periods = ["train", "validate"] + (["test"] if "--test" in sys.argv else [])
    run_report(dates, bars, ind, rg, DEFAULT, periods)
    regime_matrix(dates, bars, ind, rg, DEFAULT, *PERIODS["train"])
