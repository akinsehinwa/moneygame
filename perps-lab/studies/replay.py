"""Replay the live two-account setup over a date range, week by week, with the Bitfunded stage rules.
100K: COMBO top 2+2; 50K: CROWDFADE top 2+2 (no coin in both); 1.5% risk per coin; stop 3 ATR (coins with a stop
> 35% away skipped), TP 3R; entry Monday 08:00 SGT; exit at stop / TP / next Monday 08:00 SGT.
Stage 1: +8% target, -10% floor, -5% daily (floating losses at each hour's worst price). Stage 2 starts with the next
weekly batch: +5% / -8%. After stage 2: funded, trading continues (8% floor). Target reached = close everything.
    python3 studies/replay.py 2026-09-07 2026-10-26"""
import sys
args = sys.argv[1:] or ["2026-09-07", "2026-10-26"]
sys.argv = [sys.argv[0], "--list"]
import prop  # noqa: E402
import prop_pair as pp  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402

DAY, RISK = prop.DAY, 0.015
first = int(pd.Timestamp(args[0], tz="UTC").timestamp() * 1000)
last = int(pd.Timestamp(args[1], tz="UTC").timestamp() * 1000)
prop.ATR_STOP = 3.0

weeks = {"100K": [], "50K": []}
detail = []
for d in prop.C.index[prop.b.REB.values]:
    t_entry = int(d) + DAY
    if not first <= t_entry <= last:
        continue
    pa = pp.picks_for(prop.COMBO_S, d)
    pb = pp.picks_for(prop.CF_S, d, exclude=[c for c, _ in pa])
    for acct, picks in (("100K", pa), ("50K", pb)):
        pos = []
        for coin, side in picks:
            res = prop.trade(coin, t_entry, side, prop.ATR.at[d, coin])
            if res:
                pos.append({"coin": coin, "side": side, "r": res[0], "marks": res[1]})
                detail.append({"account": acct, "week of": pd.to_datetime(t_entry, unit="ms").date(), "coin": coin,
                               "side": "long" if side == 1 else "short", "R": round(res[0], 2),
                               "P&L %": round(res[0] * RISK * 100, 2)})
        weeks[acct].append({"t": t_entry, "pos": pos})


def run(acct):
    W = weeks[acct]
    path = prop.hourly_path(W, RISK)
    wt = [w["t"] for w in W]
    size = 100_000 if acct == "100K" else 50_000
    log, i, stage = [], 0, 1
    while i < len(wt) and stage <= 2:
        tgt, floor = (0.08, 0.10) if stage == 1 else (0.05, 0.08)
        res, t, nxt = prop.run_stage(path, wt, i, tgt, floor)
        log.append({"account": acct, "stage": stage, "started": pd.to_datetime(wt[i], unit="ms").date(),
                    "result": res, "ended": pd.to_datetime(t, unit="ms").date() if t else None,
                    "days": round((t - wt[i]) / DAY, 1) if t else None})
        if res != "pass":
            return log, None
        stage, i = stage + 1, nxt
    funded = None
    if stage == 3:
        rest = W[i:]
        funded = sum(p["r"] for w in rest for p in w["pos"]) * RISK
        log.append({"account": acct, "stage": "funded", "started": pd.to_datetime(wt[i], unit="ms").date() if i < len(wt) else None,
                    "result": "trading", "ended": None, "days": None})
    return log, funded


rows, summ = [], []
for acct in ("100K", "50K"):
    log, funded = run(acct)
    rows += log
    size = 100_000 if acct == "100K" else 50_000
    tot = sum(p["r"] for w in weeks[acct] for p in w["pos"]) * RISK
    summ.append({"account": acct, "sum of all weeks %": round(tot * 100, 2), "sum of all weeks USDT": round(tot * size),
                 "profit while funded %": None if funded is None else round(funded * 100, 2),
                 "profit while funded USDT": None if funded is None else round(funded * size),
                 "your 80% of funded profit": None if funded is None else round(funded * size * 0.8)})
D = pd.DataFrame(detail)
wk = D.groupby(["account", "week of"])["P&L %"].sum().unstack(0).round(2)
wk.insert(0, "week of", wk.index.astype(str))
print(pd.DataFrame(rows).to_string(index=False)); print(pd.DataFrame(summ).to_string(index=False)); print(wk.to_string(index=False))
write_report("replay %s to %s" % (args[0], args[1]), [("Stages", pd.DataFrame(rows)), ("Summary", pd.DataFrame(summ)),
                                                       ("Weekly P&L (% of account)", wk), ("Every trade", D)])
