"""Two accounts, top picks of DIFFERENT rankings, no coin in both: 100K = COMBO top 2 long + 2 short; 50K = top 2+2 of
a second ranking (CROWDFADE or MOM) skipping coins the 100K holds. Stop 3 x daily ATR (coins with a stop > 35% away
skipped; margin is added so liquidation sits beyond the stop), target 3R, weekly exit.
    python3 studies/prop_pair.py"""
import sys
sys.argv = [sys.argv[0], "--list"]
import prop  # noqa: E402
import prop_two as t  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402

DAY, MAX_STOP, K = prop.DAY, 0.35, 2


def picks_for(score, d, exclude=()):
    s = score.loc[d].where(prop.el.loc[d]).dropna().sort_values()
    s = s[((3 * prop.ATR.loc[d] / prop.C.loc[d]).reindex(s.index) <= MAX_STOP) & ~s.index.isin(list(exclude))]
    if len(s) < 8:
        return []
    return [(c, 1) for c in s.index[::-1][:K]] + [(c, -1) for c in s.index[:K]]


def build_pair(second):
    prop.ATR_STOP = 3.0
    A, B = [], []
    days = prop.C.index[prop.b.REB.values & (prop.C.index >= prop.START - 7 * DAY)]
    for d in days:
        pa = picks_for(prop.COMBO_S, d)
        pb = picks_for(second, d, exclude=[c for c, _ in pa])
        for picks, out in ((pa, A), (pb, B)):
            pos = []
            for coin, side in picks:
                res = prop.trade(coin, int(d) + DAY, side, prop.ATR.at[d, coin])
                if res:
                    pos.append({"coin": coin, "side": side, "r": res[0], "marks": res[1]})
            if pos:
                out.append({"t": int(d) + DAY, "pos": pos})
    return A, B


if __name__ == "__main__":
    last = prop.C.index[-1] - 180 * DAY
    trad, sims = [], []
    for name, second in (("CROWDFADE", prop.CF_S), ("MOM", prop.MOM_S)):
        A, B = build_pair(second)
        for nm, w in (("100K: COMBO top 2+2", A), ("50K: %s top 2+2 (no overlap)" % name, B)):
            s = prop.weekly_r(w)
            o, n = prop.stats(s[s.index < prop.SPLIT]), prop.stats(s[s.index >= prop.SPLIT])
            trad.append({"pairing": "COMBO + " + name, "account": nm, "avg R old": o.get("avg R/position"),
                         "avg R 12m": n.get("avg R/position"), "Sharpe old": o.get("Sharpe"), "Sharpe 12m": n.get("Sharpe")})
            print(trad[-1], flush=True)
        for risk in (0.0125, 0.015, 0.0175, 0.02):
            ca = prop.challenge(A, risk); ca = ca[ca.start <= last].set_index("start")
            cb = prop.challenge(B, risk); cb = cb[cb.start <= last].set_index("start")
            both = ca.index.intersection(cb.index)
            pa, fa, da, ta = t.outcome(ca, both)
            pb, fb, db, tb = t.outcome(cb, both)
            sims.append({"pairing": "COMBO + " + name, "risk/position %": risk * 100,
                         "100K pass by d180 %": round(pa.mean() * 100), "100K fail %": round(fa.mean() * 100),
                         "50K pass %": round(pb.mean() * 100), "50K fail %": round(fb.mean() * 100),
                         "at least one %": round((pa | pb).mean() * 100), "both fail %": round((fa & fb).mean() * 100),
                         "daily-limit fails %": "%d / %d" % (da.mean() * 100, db.mean() * 100)})
            print(sims[-1], flush=True)
    write_report("prop two accounts different rankings", [("Per account (weekly R)", pd.DataFrame(trad)),
                                                          ("Challenge simulation (by day 180)", pd.DataFrame(sims))])
