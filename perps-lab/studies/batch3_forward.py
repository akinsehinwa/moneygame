"""Forward tests frozen 2026-11-21 (paper only, never on the tickets; see LEDGER.md):
  OUTSIDE  after a BTC 'outside' day (daily candle sweeps the previous day's high AND low and closes inside it), go long
           the equal-weight basket of eligible coins for the next day (08:00 to 08:00 SGT). Costs 0.06% per side.
  OIFOLLOW the reverse of OIFADE (data-suggested): weekly basket long the 7 coins whose open-interest value rose most vs
           its 30-day norm, short the 7 where it fell most; portfolio engine with costs and funding.
Forward window: from 2026-11-22.
    python3 studies/batch3_forward.py"""
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

FROZEN = int(pd.Timestamp("2026-11-22", tz="UTC").timestamp() * 1000)
P, C, R, E = b.P, b.C, b.R, b.E
st = label(resample(load_1h("BTC"), 24)).reindex(C.index)
basket_next = R.where(E).mean(axis=1).shift(-1) - 2 * (config.FEE_PER_SIDE + config.SLIP_PER_SIDE)
ev = basket_next[(st.crt == "OUTSIDE") & (C.index >= FROZEN) & basket_next.notna()]
out_tbl = pd.DataFrame({"outside day (SGT close)": (pd.to_datetime(ev.index, unit="ms") + pd.Timedelta(days=1, hours=8)).strftime("%Y-%m-%d"),
                        "basket next day %": (ev.values * 100).round(2)})
oiv = b.metrics_panel("oi_value")
score = oiv.rolling(7, min_periods=5).mean() / oiv.rolling(30, min_periods=20).mean() - 1
res = pf.run(P, pf.long_short(score, E & score.notna(), 7), "W")
fw = res[res.index >= FROZEN]
summary = pd.DataFrame([
    {"test": "OUTSIDE", "events": len(ev), "avg %": round(ev.mean() * 100, 2) if len(ev) else None,
     "total %": round(ev.sum() * 100, 2), "backtest": "+1.15%/event (old +1.31, 12m +0.74), ~1.4 events/month"},
    {"test": "OIFOLLOW", "events": len(fw), "avg %": round(fw.net.mean() * 100, 3) if len(fw) else None,
     "total %": round(((1 + fw.net).prod() - 1) * 100, 2) if len(fw) else None,
     "backtest": "reverse of OIFADE (Sharpe -1.33 / -0.97 for the fade): data-suggested, unproven"}])
print(summary.to_string(index=False)); print(out_tbl.to_string(index=False))
write_report("batch 3 forward tests", [("Rules (frozen 2026-11-21)", __doc__.split("\n\n")[0]), ("Summary", summary),
                                       ("Outside-day events", out_tbl)])
