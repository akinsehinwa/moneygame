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
| BRKB | BRK only in BTC's 4h trend direction | **Rejected** | long +0.06 / short −0.09 | long +0.14 / short −0.04 | helps the last 12m only; R/month unchanged |
| BRK+breadth | BRK when >= 3 coins break out together | **Rejected** | | | dropped longs still positive in the old period; breadth hurts shorts |
| RS | weekly relative strength vs BTC, top/bottom 10 | **Rejected** | long +0.03 / short +0.02 | long −0.03 / short +0.04 | short leg positive but t < 1 |
| FUND | fade funding-rate extremes | **Rejected** | short +0.04 (t 1.8) | short −0.03 | edge faded; extremes now rare |
| MOM | basket: cross-sectional momentum, 60d skip 7d, top/bottom 7 (paper 3.1) | **Shadow next** | Sharpe 0.71 | Sharpe 1.12 | robust for 30-60d formation, skip 0-7d; gains lean on big winners |
| SECTOR | basket: crypto-sector momentum rotation (paper 4.1) | **Shadow next** | Sharpe 0.83 | Sharpe 1.32 | robust at 5/6 lookbacks; hand-made sector map |
| MOMCARRY | basket: 50/50 momentum + funding carry (paper 8.4) | Probation | Sharpe 1.42 | Sharpe 0.74 | carry leg alone failed the last 12m |
| TRENDLO | long-only trend book (paper 4.6) | **Rejected** | Sharpe 0.74 | Sharpe 1.56 | last 12m = one coin (PIPPIN) |
| CARRY | basket: funding carry (paper 5.11/8.2/9.1) | Rejected | Sharpe 1.36 | Sharpe −0.10 | strong before, gone in the last 12m |
| other p151 | LOWVOL, RESMOM, CONTRA, MA2, MA3, TSMOM, CHANFADE, DUALMOM, RSQ, DOLLARCARRY, SKEW, NEWLIST, VOLTARGET, FOMCDAY, DISTRESS | Rejected | | | see results/2026-11-21-p151-all.md |
| ROUTER | the pool switched by coin regime | **Robust? (no)** | | | walk-forward +0.064R, 6/8 quarters, t 0.3: not significant yet |

## Next ideas queued
0. Batch-1 of the paper: MOM and SECTOR go to shadow testing (paper-traded forward, weekly rebalance).
1. Queue round 1 (BTC direction, breadth, relative strength, funding) done: all rejected. Next: the applicable
   strategies from "151 Trading Strategies", and breadth scaled to 72 coins (flagged as data-suggested).
2. Put the coin-regime router into a shadow paper book once one cell is clearly significant.
