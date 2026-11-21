# Strategy status board

> 2026-11-21: the user is not trading these. Conclusion: none of the strategies below are prop-challenge strategies
> (too little edge per month to pass +8% fast). Weekly operations are paused; paper books and forward tests are
> replayed in one batch on 2026-12-23. New prop bar: >= +0.2R/trade with >= 20 trades/month per account (LEDGER.md).

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
| MOM | basket: cross-sectional momentum, 60d skip 7d, top/bottom 7 (paper 3.1) | **Shadow (from 2026-11-23)** | Sharpe 0.71 | Sharpe 1.12 | robust for 30-60d formation, skip 0-7d; gains lean on big winners |
| SECTOR | basket: crypto-sector momentum rotation (paper 4.1) | **Shadow (from 2026-11-23)** | Sharpe 0.83 | Sharpe 1.32 | robust at 5/6 lookbacks; hand-made sector map |
| CROWDFADE | basket: fade crowd positioning (Binance long/short account ratio) (paper 9.2, lateral) | **Shadow (from 2026-11-23)** | Sharpe 0.92 | Sharpe 1.85 | best result so far: 26/27 neighbours positive, every year positive, low correlation with MOM |
| COMBO4 | prop version: 2 long + 2 short by combined CROWDFADE + MOM rank, stop 3 ATR, target 3R, weekly (Mon 08:00 SGT) | **Shadow (from 2026-11-23)** | weekly Sharpe 1.17 | weekly Sharpe 2.02 | fits the 5-position rule; slow for challenges (34% pass both by day 180 at 1.5% risk) |
| MOMCARRY | basket: 50/50 momentum + funding carry (paper 8.4) | Probation | Sharpe 1.42 | Sharpe 0.74 | carry leg alone failed the last 12m |
| TRENDLO | long-only trend book (paper 4.6) | **Rejected** | Sharpe 0.74 | Sharpe 1.56 | last 12m = one coin (PIPPIN) |
| CARRY | basket: funding carry (paper 5.11/8.2/9.1) | Rejected | Sharpe 1.36 | Sharpe −0.10 | strong before, gone in the last 12m |
| other p151 | LOWVOL, RESMOM, CONTRA, MA2, MA3, TSMOM, CHANFADE, DUALMOM, RSQ, DOLLARCARRY, SKEW, NEWLIST, VOLTARGET, FOMCDAY, DISTRESS | Rejected | | | see results/2026-11-21-p151-all.md |
| PAIRS, ECO | mean reversion in correlated pairs / ecosystems (paper 3.8, 3.9.1, 14.4) | Rejected | Sharpe −1.6 / −0.9 | Sharpe +2.7 / +1.6 | strong only in the last 12m (regime-dependent) |
| PIVOT, CROWDTOP, DISPMOM | daily pivots; follow top traders; MOM gated by dispersion | Rejected | | | see results/2026-11-21-p151-batch-2-all.md |
| ROUTER | the pool switched by coin regime | **Robust? (no)** | | | walk-forward +0.064R, 6/8 quarters, t 0.3: not significant yet |

## Next ideas queued
0. MOM, SECTOR and CROWDFADE are in the shadow book (shadow.py, shadow/STATUS.md) from the 2026-11-23 rebalance. Judge after ~3 months / 12 rebalances: forward Sharpe should not be far below the backtest's.
1. Queue round 1 (BTC direction, breadth, relative strength, funding) done: all rejected. Next: the applicable
   strategies from "151 Trading Strategies", and breadth scaled to 72 coins (flagged as data-suggested).
2. Put the coin-regime router into a shadow paper book once one cell is clearly significant.
