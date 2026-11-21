"""Funded-account risk plan: 180 days from every Monday since 2023-11-20, no target, 5% daily limit, 8% floor
(fixed at the starting balance; after each payout the balance resets and the floor stays, so the cushion stays 8%).
Payout of any profit at the first weekly close at least 15 days after the previous payout; trader keeps 80%.
Books: 100K COMBO top 2+2, 50K CROWDFADE top 2+2 (no overlap), stop 3 ATR, TP 3R, weekly.
    python3 studies/funded.py"""
import sys
sys.argv = [sys.argv[0], "--list"]
import prop  # noqa: E402
import prop_pair as pp  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402

DAY, H = prop.DAY, 3600_000
A, B = pp.build_pair(prop.CF_S)
rows = []
for acct, W, size in (("100K", A, 100_000), ("50K", B, 50_000)):
    for risk in (0.005, 0.0075, 0.01, 0.0125, 0.015):
        path = prop.hourly_path(W, risk)
        wt = [w["t"] for w in W]
        res = []
        for si in range(len(wt)):
            if wt[si] > prop.C.index[-1] - 180 * DAY:
                break
            bal, paid, last_pay, blown = 0.0, 0.0, wt[si], False
            for wi in range(si, len(wt)):
                if wt[wi] >= wt[si] + 180 * DAY:
                    break
                wk = path[path.week == wt[wi]]
                cur_day, day_start = None, None
                for t, r in zip(wk.index, wk.itertuples()):
                    dd = (t - 16 * H) // DAY
                    ec, ew = bal + r.close, bal + r.worst
                    if dd != cur_day:
                        cur_day, day_start = dd, ec
                    if ew <= -0.08 or ew - day_start <= -0.05:
                        blown = True
                        break
                if blown:
                    break
                bal += wk.final.iloc[0]
                if wk.index[-1] - last_pay >= 15 * DAY and bal > 0:
                    paid += bal
                    bal, last_pay = 0.0, wk.index[-1]
            res.append({"blown": blown, "paid": paid})
        R = pd.DataFrame(res)
        rows.append({"account": acct, "risk/coin %": risk * 100, "starts": len(R),
                     "breached within 180 days %": round(R.blown.mean() * 100),
                     "avg payout to you per month (USD)": round(R.paid.mean() * size * 0.8 / 6),
                     "median payout per month (USD)": round(R.paid.median() * size * 0.8 / 6),
                     "worst 10% payout per month (USD)": round(R.paid.quantile(0.1) * size * 0.8 / 6)})
        print(rows[-1], flush=True)
write_report("funded risk plan", [("Setup", __doc__.split("\n\n")[0]), ("Results", pd.DataFrame(rows))])
