"""Prop-ready compact books + challenge simulation (rules: PROP_RULES.md, pre-registration: LEDGER.md).

    python3 studies/prop.py

1. Weekly picks per book from the CROWDFADE / MOM scores (data up to the Sunday close).
2. Each pick traded on 1h bars: entry at Monday 00:00 UTC open, stop 3 x daily ATR(14), take-profit 3R, exit
   before the next rebalance. Hourly marks (close and worst price) kept for the account simulation.
3. Weekly R series -> Sharpe / avg R by period (tradability test).
4. Challenge simulation from every weekly start: stage 1 then stage 2, hourly floating P&L vs the daily and total
   loss limits, close-all when floating profit reaches the target.
"""
import sys

sys.argv = [sys.argv[0], "--list"]
import p151b as b  # noqa: E402
from common import write_report  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import config  # noqa: E402
from lib.data import load_1h  # noqa: E402

P, C, R, E = b.P, b.C, b.R, b.E
H, DAY = 3600_000, 24 * 3600_000
COST = config.FEE_PER_SIDE + config.SLIP_PER_SIDE
ATR_STOP, TARGET_R, HOLD_H = 3.0, 3.0, 167
SPLIT = int(pd.Timestamp(config.SPLIT, tz="UTC").timestamp() * 1000)
START = int(pd.Timestamp(config.EVAL_START, tz="UTC").timestamp() * 1000)

# ---------------------------------------------------------------- scores and picks
rm = R.shift(7).rolling(60, min_periods=50)
MOM_S = rm.mean() / rm.std()
g = b.metrics_panel("global_ls")
CF_S = -(g.rolling(7, min_periods=5).mean() / g.rolling(90, min_periods=60).mean() - 1)
el = E & MOM_S.notna() & CF_S.notna()
COMBO_S = (MOM_S.where(el).rank(axis=1, pct=True) + CF_S.where(el).rank(axis=1, pct=True)) / 2
BOOKS = {"CF2": (CF_S, 1), "CF4": (CF_S, 2), "MOM4": (MOM_S, 2), "COMBO4": (COMBO_S, 2)}

pc = C.shift(1)
TR = np.maximum(P["H"] - P["L"], np.maximum((P["H"] - pc).abs(), (P["L"] - pc).abs()))
ATR = TR.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()

H1 = {}


def h1(coin):
    if coin not in H1:
        df = load_1h(coin)
        H1[coin] = {k: df[k].values for k in ("t", "o", "h", "l", "c")}
    return H1[coin]


def trade(coin, t_entry, side, atr):
    """Returns (final R, hourly marks DataFrame index=t with columns close_R, worst_R) or None."""
    d = h1(coin)
    T = d["t"]
    i = int(np.searchsorted(T, t_entry))
    if i >= len(T) or T[i] != t_entry:
        return None
    entry = d["o"][i]
    risk = ATR_STOP * atr
    stop, target = entry - side * risk, entry + side * TARGET_R * risk
    ts, mc, mw = [], [], []
    for j in range(i, min(i + HOLD_H + 1, len(T))):
        o, hh, ll, cc = d["o"][j], d["h"][j], d["l"][j], d["c"][j]
        adverse = ll if side == 1 else hh
        exit_px = None
        if j == i + HOLD_H:
            exit_px = o
        elif (side == 1 and ll <= stop) or (side == -1 and hh >= stop):
            exit_px = min(stop, o) if side == 1 else max(stop, o)
        elif (side == 1 and hh >= target) or (side == -1 and ll <= target):
            exit_px = max(target, o) if side == 1 else min(target, o)
        if exit_px is not None:
            r = ((exit_px - entry) * side - COST * (entry + exit_px)) / risk
            ts.append(T[j]); mc.append(r); mw.append(min(r, ((adverse - entry) * side - COST * entry * 2) / risk))
            return r, pd.DataFrame({"close_R": mc, "worst_R": mw}, index=ts)
        ts.append(T[j])
        mc.append(((cc - entry) * side - COST * entry * 2) / risk)
        mw.append(((adverse - entry) * side - COST * entry * 2) / risk)
    return None


def build(book):
    score, k = BOOKS[book]
    weeks = []
    days = C.index[b.REB.values & (C.index >= START - 7 * DAY)]
    for d in days:
        s = score.loc[d].where(el.loc[d]).dropna()
        if len(s) < 20:
            continue
        s = s.sort_values()
        picks = [(c, 1) for c in s.index[-k:]] + [(c, -1) for c in s.index[:k]]
        t_entry = int(d) + DAY
        pos = []
        for coin, side in picks:
            res = trade(coin, t_entry, side, ATR.at[d, coin])
            if res:
                pos.append({"coin": coin, "side": side, "r": res[0], "marks": res[1]})
        if pos:
            weeks.append({"t": t_entry, "pos": pos})
    return weeks


# ---------------------------------------------------------------- tradability
def weekly_r(weeks):
    return pd.Series({w["t"]: np.mean([p["r"] for p in w["pos"]]) for w in weeks})


def stats(s):
    if len(s) < 5:
        return {}
    return {"weeks": len(s), "avg R/position": round(s.mean(), 3),
            "Sharpe": round(s.mean() / s.std() * np.sqrt(52), 2) if s.std() > 0 else np.nan,
            "win weeks %": round((s > 0).mean() * 100)}


# ---------------------------------------------------------------- challenge simulation
def hourly_path(weeks, risk):
    """Account P&L in % of the starting balance, hourly: realized (closed) + floating close + floating worst."""
    rows = []
    for w in weeks:
        m = None
        for p in w["pos"]:
            x = p["marks"] * risk
            m = x if m is None else m.add(x, fill_value=np.nan)
        # positions that already exited keep their final R for the rest of the week
        allm = pd.concat([p["marks"].reindex(range(w["t"], w["t"] + (HOLD_H + 1) * H, H)).ffill() * risk
                          for p in w["pos"]], axis=1, keys=range(len(w["pos"])))
        close = allm.xs("close_R", axis=1, level=1).sum(axis=1)
        worst = allm.xs("worst_R", axis=1, level=1).sum(axis=1)
        final = sum(p["r"] for p in w["pos"]) * risk
        rows.append(pd.DataFrame({"week": w["t"], "close": close, "worst": worst, "final": final}))
    return pd.concat(rows)


def run_stage(path, weeks_t, start_i, target, max_loss, daily=0.05):
    """Walk weeks from start_i. Returns ('pass'|'fail'|'open', end time, index of next week)."""
    bal = 0.0
    for wi in range(start_i, len(weeks_t)):
        wk = path[path.week == weeks_t[wi]]
        day_start_eq, cur_day = None, None
        for t, r in zip(wk.index, wk.itertuples()):
            dday = (t - 16 * H) // DAY                    # Singapore day boundary 16:00 UTC
            eq_close, eq_worst = bal + r.close, bal + r.worst
            if dday != cur_day:
                cur_day, day_start_eq = dday, eq_close
            if eq_worst <= -max_loss:
                return "fail-total", t, wi + 1
            if eq_worst - day_start_eq <= -daily:
                return "fail-daily", t, wi + 1
            if eq_close >= target:
                return "pass", t, wi + 1
        bal += wk.final.iloc[0]
        if bal >= target:
            return "pass", int(wk.index[-1]), wi + 1
    return "open", None, len(weeks_t)


def challenge(weeks, risk):
    path = hourly_path(weeks, risk)
    wt = [w["t"] for w in weeks]
    out = []
    for si in range(len(wt)):
        s1, t1, nxt = run_stage(path, wt, si, 0.08, 0.10)
        rec = {"start": wt[si], "s1": s1, "d1": (t1 - wt[si]) / DAY if t1 else np.nan, "s2": "-", "d2": np.nan}
        if s1 == "pass":
            s2, t2, _ = run_stage(path, wt, nxt, 0.05, 0.08)
            rec["s2"] = s2
            rec["d2"] = (t2 - wt[si]) / DAY if t2 else np.nan
        out.append(rec)
    return pd.DataFrame(out)


def outcome_at(ch, horizon):
    """Status of each start at `horizon` days: passed both / passed stage 1 / failed (daily or total) / running."""
    def st(r):
        if r.s1.startswith("fail") and r.d1 <= horizon:
            return r.s1
        if r.s1 == "pass" and r.d1 <= horizon:
            if r.s2 == "pass" and r.d2 <= horizon:
                return "passed both"
            if r.s2.startswith("fail") and r.d2 <= horizon:
                return "s2 " + r.s2
            return "passed stage 1"
        return "running"
    return ch.apply(st, axis=1).value_counts(normalize=True) * 100


def _unused():
    out = []
    for rec in []:
        out.append(rec)
    return pd.DataFrame(out)


if __name__ == "__main__":
    trad, sims = [], []
    for book in BOOKS:
        weeks = build(book)
        s = weekly_r(weeks)
        o, n = stats(s[s.index < SPLIT]), stats(s[s.index >= SPLIT])
        ok = all(x.get("avg R/position", -1) > 0 and (x.get("Sharpe") or -1) >= 0.5 for x in (o, n))
        trad.append({"book": book, **{k + " old": v for k, v in o.items()}, **{k + " 12m": v for k, v in n.items()},
                     "tradable": "PASS" if ok else "fail"})
        print(book, trad[-1]["tradable"], o, n, flush=True)
        last = C.index[-1] - 180 * DAY
        for risk in (0.005, 0.01, 0.015, 0.02, 0.03):
            ch = challenge(weeks, risk)
            ch = ch[ch.start <= last]                      # starts with 180+ days of data after them
            for hz in (90, 180):
                o = outcome_at(ch, hz)
                row = {"book": book, "risk/position %": risk * 100, "by day": hz, "starts": len(ch)}
                for k in ("passed both", "passed stage 1", "running", "fail-daily", "fail-total",
                          "s2 fail-daily", "s2 fail-total"):
                    row[k + " %"] = round(o.get(k, 0))
                sims.append(row)
            print("  risk %.1f%%: by day 180 passed both %d%%, stage 1 only %d%%, failed %d%%, running %d%%" % (
                risk * 100, row["passed both %"], row["passed stage 1 %"],
                row["fail-daily %"] + row["fail-total %"] + row["s2 fail-daily %"] + row["s2 fail-total %"], row["running %"]), flush=True)
    write_report("prop compact books", [
        ("Rules", "See PROP_RULES.md. Weekly books, max 4 positions, stop 3 ATR, target 3R, costs 0.06%/side, no funding. "
                  "Challenge: every weekly start since 2023-11-20 with 180+ days of data after it; status at day 90 and day 180; stage 1 +8% / -10% / -5% daily, then stage 2 +5% / -8%. "
                  "Optimistic: strategies were chosen on this history."),
        ("Tradability (weekly R per position)", pd.DataFrame(trad)),
        ("Challenge simulation", pd.DataFrame(sims))])
