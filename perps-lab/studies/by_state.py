"""How the two weekly books (100K COMBO, 50K CROWDFADE) did in each Bitcoin state (state of the signal day).
    python3 studies/by_state.py"""
import sys
sys.argv = [sys.argv[0], "--list"]
import prop  # noqa: E402
import manage as mg  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402
from lib.btcstate import label  # noqa: E402
from lib.data import load_1h, resample  # noqa: E402

ST = label(resample(load_1h("BTC"), 24))
STATES = ["STRONG_DOWN", "DOWN", "COIL", "RANGE", "UP", "STRONG_UP"]
rows = []
for book in ("100K", "50K"):
    for t_entry, d, picks in mg.weeks_for(book):
        state = ST.state.get(d)
        rs = [mg.sim(c, t_entry, s, prop.ATR.at[d, c], "V0") for c, s in picks]
        for (c, s), r in zip(picks, rs):
            if r is not None:
                rows.append({"account": book, "state": state, "side": "long" if s == 1 else "short", "r": r,
                             "week": t_entry, "pnl": r * 0.015})
X = pd.DataFrame(rows)
wk = X.groupby(["account", "state", "week"]).pnl.sum().reset_index()
out = []
for (acct, st), g in wk.groupby(["account", "state"]):
    x = X[(X.account == acct) & (X.state == st)]
    out.append({"account": acct, "BTC state": st, "weeks": len(g), "avg week %": round(g.pnl.mean() * 100, 2),
                "worst week %": round(g.pnl.min() * 100, 2), "best week %": round(g.pnl.max() * 100, 2),
                "losing weeks %": round((g.pnl < 0).mean() * 100), "longs avg R": round(x[x.side == "long"].r.mean(), 2),
                "shorts avg R": round(x[x.side == "short"].r.mean(), 2)})
T = pd.DataFrame(out)
T["o"] = T["BTC state"].map({s: i for i, s in enumerate(STATES)})
T = T.sort_values(["account", "o"]).drop(columns="o")
print(T.to_string(index=False))
write_report("weekly books by btc state", [("Per Bitcoin state (state of the signal day; 1.5% risk per coin)", T)])
