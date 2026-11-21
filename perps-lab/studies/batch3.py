"""Research batch 3 (pre-registered in LEDGER.md): OIFADE, OIFADE + CROWDFADE, BTC daily CRT next-day effects.
    python3 studies/batch3.py"""
import sys
sys.argv = [sys.argv[0], "--list"]
import p151b as b  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402

import config  # noqa: E402
from lib import portfolio as pf  # noqa: E402
from lib.btcstate import label  # noqa: E402
from lib.data import load_1h, resample  # noqa: E402

P, C, R, E = b.P, b.C, b.R, b.E
B = int(pd.Timestamp(config.SPLIT, tz="UTC").timestamp() * 1000)

oiv = b.metrics_panel("oi_value")
oi_score = -(oiv.rolling(7, min_periods=5).mean() / oiv.rolling(30, min_periods=20).mean() - 1)
W_oi = pf.long_short(oi_score, E & oi_score.notna(), 7)
W_cf = b.CROWDFADE()[0]
books = {"OIFADE": W_oi, "OIFADE + CROWDFADE": 0.5 * W_oi + 0.5 * W_cf, "CROWDFADE (reference)": W_cf}
rows = []
for name, W in books.items():
    res = pf.run(P, W, "W")
    Wm = W.where(pd.Series(pf.rebalance_days(W.index, "W"), index=W.index), np.nan).ffill().fillna(0.0)
    h = Wm.shift(1).fillna(0.0)
    contrib = h * R.fillna(0.0) - h * P["F"]
    row, ok = {"book": name}, True
    for per, x in pf.periods(res).items():
        m = pf.metrics(x)
        sel = (contrib.index >= B) if per == "12m" else (contrib.index < B) & (contrib.index >= x.index.min())
        c = contrib[sel].sum().sort_values()
        ex3 = c.sum() - c.tail(3).sum()
        row.update({"Sharpe " + per: m.get("Sharpe"), "ann % " + per: m.get("ann %"), "maxDD % " + per: m.get("maxDD %"),
                    "w/o best 3 " + per: round(ex3, 2)})
        ok = ok and (m.get("Sharpe") or -9) >= 0.5 and ex3 > 0
    row["verdict"] = "" if "reference" in name else ("PASS" if ok else "fail")
    rows.append(row)
    print(row, flush=True)
corr = round(pf.run(P, W_oi, "W").net.corr(pf.run(P, W_cf, "W").net), 2)

# BTC CRT patterns: next-day equal-weight basket and BTC returns
st = label(resample(load_1h("BTC"), 24)).reindex(C.index)
basket = R.where(E).mean(axis=1)
nxt_b, nxt_btc = basket.shift(-1), R["BTC"].shift(-1)
crt = []
for pat in ["BULL_CRT", "BEAR_CRT", "BREAK_UP", "BREAK_DN", "INSIDE", "OUTSIDE"]:
    m = (st.crt == pat) & nxt_b.notna() & (C.index >= int(pd.Timestamp(config.EVAL_START, tz="UTC").timestamp() * 1000))
    x = nxt_b[m]
    t = x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
    o, n = x[x.index < B], x[x.index >= B]
    ok = abs(t) >= 2 and np.sign(o.mean()) == np.sign(n.mean()) == np.sign(x.mean())
    crt.append({"BTC pattern today": pat, "days": int(m.sum()), "alt basket next day %": round(x.mean() * 100, 2),
                "t": round(t, 2), "old %": round(o.mean() * 100, 2), "12m %": round(n.mean() * 100, 2),
                "BTC next day %": round(nxt_btc[m].mean() * 100, 2), "candidate": "yes" if ok else ""})
CRT = pd.DataFrame(crt)
print(CRT.to_string(index=False)); print("OIFADE vs CROWDFADE daily-return correlation:", corr)
write_report("research batch 3", [("OI fade books (pass = Sharpe >= 0.5 both periods and positive w/o best 3 coins)",
                                    pd.DataFrame(rows)),
                                   ("Correlation", "OIFADE vs CROWDFADE daily returns: %s" % corr),
                                   ("BTC daily CRT patterns: next-day moves", CRT)])
