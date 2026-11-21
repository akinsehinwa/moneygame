# Research ledger

Every hypothesis, written before the test, with the result and the decision. Variants are counted.
Decisions: ADOPT (moves up the pipeline) / PROBATION (keep testing) / REJECT (graveyard).

| date | hypothesis | variants | result | decision |
|---|---|---|---|---|
| 2026-11-21 | Baseline pool: 7 fixed strategies (BRK, PB, MR, SWP, SQZ, ST4, STD) x long/short on all 72 coins | 7 (no tuning) | 59k trades, −0.02R unfiltered after costs | baseline |
| 2026-11-21 | Not every coin suits one strategy: pick strategies per coin from past results | 3 thresholds | walk-forward −0.02R (no better than taking everything) | REJECT (overfits) |
| 2026-11-21 | Route strategies by market regime (BTC trend x vol) | 3 thresholds | walk-forward +0.06R, 3/8 quarters, t −0.2 | REJECT (inconsistent) |
| 2026-11-21 | Route strategies by the coin's own regime (trend x efficiency ratio) | 3 thresholds | walk-forward +0.06 to +0.08R, 6/8 quarters, t ≤ 0.9 | PROBATION (best router, not significant) |
| 2026-11-21 | SWP: liquidity-sweep fade at the 20-bar extreme | 1 | −0.06 to −0.10R both periods, nearly every regime | REJECT |

## Queue (not tested yet)
- Breakout only in BTC's direction (BTC 4h EMA50 vs EMA200).
- Breadth: count of the 72 coins breaking out on the same bar as a filter.
- Relative strength: long the strongest coins vs BTC over 30 days, short the weakest, weekly rebalance.
- Funding-rate extremes (needs funding history from the Binance archive).
