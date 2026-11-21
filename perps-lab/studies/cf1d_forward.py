"""Forward test of CF1D SHORTS ONLY (rules frozen 2026-11-21, see LEDGER.md). Paper only; never on the tickets.

Rule (unchanged from the CF1D test): one signal a day at 08:00 SGT; score per coin = mean of the 4h global long/short
ratio over the last 18 bars (3 days) / its mean over the last 180 bars (30 days) - 1; SHORT the coin with the highest
score (crowd most long vs its norm), one position per coin; entry at the 08:00 SGT open; stop 3 x ATR(14, 4h), skipped
if > 15% away; take-profit 2R; time exit 72h; costs 0.06% per side.
Forward window: signals from 2026-11-22 (first 08:00 SGT open after the rules were frozen) whose 72h hold has finished.
    python3 studies/cf1d_forward.py
"""
import sys
sys.argv = [sys.argv[0], "--daily"]
import cf4h  # noqa: E402  (CF1D parameters via --daily)
import pandas as pd  # noqa: E402
from common import write_report  # noqa: E402

FROZEN = int(pd.Timestamp("2026-11-22", tz="UTC").timestamp() * 1000)      # first signal: 2026-11-22 08:00 SGT
BACKTEST = {"avg R old": 0.072, "avg R 12m": 0.089, "win % 12m": 57, "trades/month": 15}

X = cf4h.build()
S = X[(X["rank"] == 1) & (X.side == -1)].sort_values("t")
keep, open_until = [], {}
for r in S.itertuples():
    if open_until.get(r.coin, 0) > r.t:
        continue
    keep.append(r.Index)
    open_until[r.coin] = r.t_out
S = S.loc[keep]
F = S[S.t >= FROZEN].copy()
F["signal (SGT)"] = (pd.to_datetime(F.t, unit="ms") + pd.Timedelta(hours=8)).dt.strftime("%Y-%m-%d %H:%M")
F["R"] = F.r.round(2)
F["P&L on 50K at 1% risk (USDT)"] = (F.r * 500).round(0)
summary = pd.DataFrame([{
    "forward trades": len(F), "avg R": round(F.r.mean(), 3) if len(F) else None,
    "win %": round((F.r > 0).mean() * 100) if len(F) else None, "sum R": round(F.r.sum(), 2),
    "P&L at 1% risk on 50K (USDT)": round(F.r.sum() * 500), "worst trade R": round(F.r.min(), 2) if len(F) else None,
    "backtest avg R (old / 12m)": "%.3f / %.3f" % (BACKTEST["avg R old"], BACKTEST["avg R 12m"]),
    "backtest win % (12m)": BACKTEST["win % 12m"]}])
print(summary.T.to_string()); print(F[["signal (SGT)", "coin", "R"]].to_string(index=False))
write_report("cf1d shorts forward test", [
    ("Rule (frozen 2026-11-21)", __doc__.split("\n\n")[1]), ("Summary", summary),
    ("Every forward trade", F[["signal (SGT)", "coin", "stop_pct", "R", "P&L on 50K at 1% risk (USDT)"]])])
