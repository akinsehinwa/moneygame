# Strategy status board

Stages: Idea → Backtest → Robust → Shadow → Candidate (see README). Results: avg R per trade after costs.
"Old" = 2023-11-20 to 2025-11-20, "12m" = the last 12 months. Latest report: `results/2026-11-21-baseline-pool.md`.

| code | strategy | stage | old | 12m | notes |
|---|---|---|---|---|---|
| BRK | 4h 55-bar breakout, body ≥ 1 ATR | Backtest | long +0.10 / short +0.08 | long +0.09 / short −0.06 | long works in RANGE/CHOP and DOWN/CHOP coins |
| PB | 4h trend pullback to EMA20 | Backtest | ~0 | small + | few trades in the regimes where it's positive |
| MR | 4h Bollinger + RSI(3) fade | Backtest | negative | ~0 | long only works in RANGE coins (small sample) |
| SWP | 4h liquidity-sweep fade | **Rejected** | negative | negative | negative in almost every regime |
| SQZ | 4h squeeze breakout | Backtest | positive | negative | short in UP/TREND coins holds (+0.61 / +0.28) |
| ST4 | 4h SuperTrend(10,3) | Backtest | positive | ~0 | edge faded in the last 12 months |
| STD | daily SuperTrend(10,2) | Backtest | long +0.05 | long +0.13 | long in UP/TREND + RANGE/CHOP; short in DOWN/CHOP |
| ROUTER | the pool switched by coin regime | **Robust? (no)** | | | walk-forward +0.064R, 6/8 quarters, t 0.3: not significant yet |

## Next ideas queued
1. Add better building blocks (see LEDGER "queue"): e.g. BTC-direction filter on breakouts, breadth (many coins
   breaking out together), relative strength vs BTC.
2. Put the coin-regime router into a shadow paper book once one cell is clearly significant.
