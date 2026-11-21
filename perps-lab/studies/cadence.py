"""Which weekday should the weekly tickets be entered, and does a 2-day-old signal (Binance archive delay) hurt?
COMBO top 2+2 and CROWDFADE top 2+2 (stop 3 ATR, target 3R, 7-day hold), entry at 08:00 SGT (00:00 UTC) of each
weekday, signal from the close 1 day before entry (lag 0) or 3 days before (lag 2).
    python3 studies/cadence.py"""
import sys
sys.argv = [sys.argv[0], "--list"]
import prop  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402

DAY = prop.DAY
prop.ATR_STOP = 3.0
NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def run(score, entry_wd, lag):
    ts = pd.to_datetime(prop.C.index, unit="ms")
    entry_days = prop.C.index[(ts.weekday == entry_wd) & (prop.C.index >= prop.START)]
    weekly = {}
    for t_entry in entry_days:
        d = t_entry - DAY * (1 + lag)                     # signal bar (closed lag days before the entry morning)
        if d not in score.index:
            continue
        s = score.loc[d].where(prop.el.loc[d]).dropna().sort_values()
        s = s[(3 * prop.ATR.loc[d] / prop.C.loc[d]).reindex(s.index) <= 0.35]
        if len(s) < 8:
            continue
        rs = []
        for coin, side in [(c, 1) for c in s.index[::-1][:2]] + [(c, -1) for c in s.index[:2]]:
            res = prop.trade(coin, int(t_entry), side, prop.ATR.at[d, coin])
            if res:
                rs.append(res[0])
        if rs:
            weekly[int(t_entry)] = sum(rs) / len(rs)
    return pd.Series(weekly)


rows = []
for strat, score in (("COMBO", prop.COMBO_S), ("CROWDFADE", prop.CF_S)):
    for lag in (0, 2):
        for wd in range(7):
            s = run(score, wd, lag)
            o, n = prop.stats(s[s.index < prop.SPLIT]), prop.stats(s[s.index >= prop.SPLIT])
            rows.append({"strategy": strat, "signal age": "fresh (1 day)" if lag == 0 else "2 days older",
                         "entry day (08:00 SGT)": NAMES[wd], "avg R old": o.get("avg R/position"),
                         "avg R 12m": n.get("avg R/position"), "Sharpe old": o.get("Sharpe"), "Sharpe 12m": n.get("Sharpe")})
            print(rows[-1], flush=True)
write_report("cadence entry weekday and signal age", [("Results", pd.DataFrame(rows))])
