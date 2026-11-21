"""Two-account split of the COMBO ranking (100K + 50K, no coin in both): master list of 4 longs + 4 shorts, dealt so
account A (100K) gets long/short ranks 1 and 3 and account B (50K) ranks 2 and 4. Coins whose stop would be more than
15% away are skipped (5x isolated liquidates near 19.5%). Challenge simulation per account and 'at least one passes'.
Used to choose the stop width and the risk per position for live tickets.
    python3 studies/prop_two.py
"""
import sys
sys.argv = [sys.argv[0], "--list"]
import prop  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402

DAY = prop.DAY
MAX_STOP = 0.15


def build_split(score, ranks, mult):
    prop.ATR_STOP = mult
    weeks = []
    days = prop.C.index[prop.b.REB.values & (prop.C.index >= prop.START - 7 * DAY)]
    for d in days:
        s = score.loc[d].where(prop.el.loc[d]).dropna().sort_values()
        s = s[((mult * prop.ATR.loc[d] / prop.C.loc[d]).reindex(s.index) <= MAX_STOP)]
        if len(s) < 8:
            continue
        picks = [(s.index[::-1][r - 1], 1) for r in ranks] + [(s.index[r - 1], -1) for r in ranks]
        pos = []
        for coin, side in picks:
            res = prop.trade(coin, int(d) + DAY, side, prop.ATR.at[d, coin])
            if res:
                pos.append({"coin": coin, "side": side, "r": res[0], "marks": res[1]})
        if pos:
            weeks.append({"t": int(d) + DAY, "pos": pos})
    return weeks


def outcome(ch, idx, hz=180):
    c = ch.loc[idx]
    passed = c.apply(lambda r: r.s2 == "pass" and r.d2 <= hz, axis=1)
    failed = c.apply(lambda r: (r.s1.startswith("fail") and r.d1 <= hz) or (str(r.s2).startswith("fail") and r.d2 <= hz), axis=1)
    daily = c.apply(lambda r: (r.s1 == "fail-daily" and r.d1 <= hz) or (r.s2 == "fail-daily" and r.d2 <= hz), axis=1)
    days = c[passed].d2.median()
    return passed, failed, daily, days


if __name__ == "__main__":
    last = prop.C.index[-1] - 180 * DAY
    trad, sims = [], []
    for mult in (1.5, 2.0):
        A, B = build_split(prop.COMBO_S, [1, 3], mult), build_split(prop.COMBO_S, [2, 4], mult)
        for nm, w in (("100K (ranks 1+3)", A), ("50K (ranks 2+4)", B)):
            s = prop.weekly_r(w)
            o, n = prop.stats(s[s.index < prop.SPLIT]), prop.stats(s[s.index >= prop.SPLIT])
            trad.append({"stop": "%.1f ATR" % mult, "account": nm, "avg R old": o.get("avg R/position"),
                         "avg R 12m": n.get("avg R/position"), "Sharpe old": o.get("Sharpe"), "Sharpe 12m": n.get("Sharpe")})
            print(trad[-1], flush=True)
        for risk in (0.0075, 0.01, 0.0125, 0.015, 0.0175):
            ca = prop.challenge(A, risk); ca = ca[ca.start <= last].set_index("start")
            cb = prop.challenge(B, risk); cb = cb[cb.start <= last].set_index("start")
            both = ca.index.intersection(cb.index)
            pa, fa, da, ta = outcome(ca, both)
            pb, fb, db, tb = outcome(cb, both)
            sims.append({"stop": "%.1f ATR" % mult, "risk/position %": risk * 100, "starts": len(both),
                         "100K passed both by d180 %": round(pa.mean() * 100), "100K failed %": round(fa.mean() * 100),
                         "100K median days": ta, "50K passed both %": round(pb.mean() * 100), "50K failed %": round(fb.mean() * 100),
                         "50K median days": tb, "at least one passed %": round((pa | pb).mean() * 100),
                         "daily-limit fails 100K / 50K %": "%d / %d" % (da.mean() * 100, db.mean() * 100)})
            print(sims[-1], flush=True)
    write_report("prop two-account split", [
        ("Setup", "100K gets long/short ranks 1 and 3, 50K ranks 2 and 4 of the weekly COMBO ranking (no coin in both). "
                  "Coins whose stop is > 15% away are skipped (5x isolated). Target 3R, weekly exit. Every weekly start "
                  "since 2023-11-20 with 180+ days after it."),
        ("Per account (weekly R)", pd.DataFrame(trad)), ("Challenge simulation", pd.DataFrame(sims))])
