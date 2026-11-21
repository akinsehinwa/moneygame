"""Trade management variants for the weekly tickets (pre-registered in LEDGER.md).
    python3 studies/manage.py"""
import sys
sys.argv = [sys.argv[0], "--list"]
import prop  # noqa: E402
import prop_pair as pp  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402
from lib.data import load_1h  # noqa: E402

DAY = prop.DAY
COST = prop.COST
MAJORS = {"BTC", "ETH", "BNB", "XRP", "SOL", "TRX", "HYPE", "ZEC", "DOGE", "ADA"}
H1 = {}


def h1(coin):
    if coin not in H1:
        df = load_1h(coin)
        H1[coin] = {k: df[k].values for k in ("t", "o", "h", "l", "c")}
    return H1[coin]


def sim(coin, t_entry, side, atr, v):
    d = h1(coin)
    T = d["t"]
    i = int(np.searchsorted(T, t_entry))
    if i >= len(T) or T[i] != t_entry or i + 240 >= len(T):
        return None
    entry, risk = d["o"][i], 3.0 * atr
    stop, target = entry - side * risk, entry + side * 3.0 * risk
    if side == -1:
        target = max(target, 0.1 * entry)
    R = lambda px: ((px - entry) * side - COST * (entry + px)) / risk
    end = 168
    for k in range(0, 240):
        j = i + k
        o, hh, ll, cc = d["o"][j], d["h"][j], d["l"][j], d["c"][j]
        if k in (72, 144):                                  # check-in at the open of this bar (Thu / Sun 08:00 SGT)
            mark = R(o)
            if v in ("V1", "V3") and mark <= -0.5:
                return R(o)
            if v in ("V2", "V3") and mark >= 1.0:
                stop = entry if side == 1 else entry            # breakeven
                stop = max(stop, entry) if side == 1 else min(stop, entry)
        if k == end:                                        # Monday 08:00 exit (or extension decision)
            mark = R(o)
            extend = (v == "V4" and coin in MAJORS and mark > 0) or (v == "V5" and mark > 0)
            if not extend:
                return mark
            end = 240
        if k == 239:
            return R(d["o"][j + 1])
        if (side == 1 and ll <= stop) or (side == -1 and hh >= stop):
            return R(min(stop, o) if side == 1 else max(stop, o))
        if k > 0 and ((side == 1 and hh >= target) or (side == -1 and ll <= target)):
            return R(max(target, o) if side == 1 else min(target, o))
    return None


def weeks_for(book):
    out = []
    days = prop.C.index[prop.b.REB.values & (prop.C.index >= prop.START - 7 * DAY)]
    for d in days:
        pa = pp.picks_for(prop.COMBO_S, d)
        pb = pp.picks_for(prop.CF_S, d, exclude=[c for c, _ in pa])
        out.append((int(d) + DAY, d, pa if book == "100K" else pb))
    return out


rows, extra = [], []
for book in ("100K", "50K"):
    W = weeks_for(book)
    for v in ("V0", "V1", "V2", "V3", "V4", "V5"):
        wk = {}
        for t_entry, d, picks in W:
            rs = [sim(c, t_entry, s, prop.ATR.at[d, c], v) for c, s in picks]
            rs = [r for r in rs if r is not None]
            if rs:
                wk[t_entry] = np.mean(rs)
        s = pd.Series(wk)
        o, n = prop.stats(s[s.index < prop.SPLIT]), prop.stats(s[s.index >= prop.SPLIT])
        rows.append({"account": book, "variant": v, "avg R old": o.get("avg R/position"), "avg R 12m": n.get("avg R/position"),
                     "Sharpe old": o.get("Sharpe"), "Sharpe 12m": n.get("Sharpe")})
        print(rows[-1], flush=True)
    n_major = sum(c in MAJORS for _, _, p in W for c, _ in p)
    extra.append({"account": book, "positions": sum(len(p) for _, _, p in W), "major positions": n_major})
write_report("trade management variants", [
    ("Variants", "V0 hold 7 days; V1 cut at <= -0.5R at Thu/Sun check; V2 breakeven stop at >= +1R at check; V3 both; "
                 "V4 majors in profit held to day 10; V5 any coin in profit to day 10 (not allowed, reference)."),
    ("Results (avg R per position, weekly Sharpe)", pd.DataFrame(rows)), ("How often majors are picked", pd.DataFrame(extra))])
