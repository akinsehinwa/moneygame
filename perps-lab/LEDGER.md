# Research ledger

Every hypothesis, written before the test, with the result and the decision. Variants are counted.
Decisions: ADOPT (moves up the pipeline) / PROBATION (keep testing) / REJECT (graveyard).

| date | hypothesis | variants | result | decision |
|---|---|---|---|---|
| 2026-11-21 | Baseline pool: 7 fixed strategies (BRK, PB, MR, SWP, SQZ, ST4, STD) x long/short on all 72 coins | 7 (no tuning) | 59k trades, −0.02R unfiltered after costs | baseline |
| 2026-11-21 | Not every coin suits one strategy: pick strategies per coin from past results | 3 thresholds | walk-forward −0.02R (no better than taking everything) | REJECT (overfits) |
| 2026-11-21 | Route strategies by market regime (BTC trend x vol) | 3 thresholds | walk-forward +0.06R, 3/8 quarters, t −0.2 | REJECT (inconsistent) |
| 2026-11-21 | Route strategies by the coin's own regime (trend x efficiency ratio) | 3 thresholds | walk-forward +0.06 to +0.08R, 6/8 quarters, t ≤ 0.9 | PROBATION (best router, not significant) |
| 2026-11-21 | Q1 BRKB: breakout only in BTC's 4h trend direction | 1 | long +0.06 old (BRK +0.09) / +0.14 12m (BRK +0.09); short −0.09 / −0.04; R/month unchanged (long 9.0 vs 9.0) | REJECT (fails the old period; helps only the last 12m) |
| 2026-11-21 | Q2 breadth >= 3 coins on BRK | 3 (thr 2/3/5) | long: dropped trades +0.09 old / −0.07 12m (kept +0.10 / +0.18); short: breadth HURTS (isolated shorts +0.18 / +0.05, crowded +0.07 / −0.08) | REJECT (dropped longs positive in the old period) |
| 2026-11-21 | Q3 RS: weekly rotation, long top 10 / short bottom 10 by 30-day return vs BTC | 1 | long +0.03 old (t 0.4) / −0.03 12m; short +0.02 (t 0.4) / +0.04 (t 0.6) | REJECT (short leg positive but not significant) |
| 2026-11-21 | Q4 FUND: fade funding >= +0.05% / <= −0.05% per 8h | 1 | short +0.04 old (t 1.8) / −0.03 12m (only 9 coins hit the threshold); long +0.02 / −0.04 | REJECT (edge gone in the last 12 months) |
| 2026-11-21 | p151 batch 1: 20 basket strategies (direct + lateral), costs + funding | 20 | 4 pass the Sharpe >= 0.5 bar in both periods: MOM (0.71 / 1.12), TRENDLO (0.74 / 1.56), MOMCARRY (1.42 / 0.74), SECTOR (0.83 / 1.32). All four are momentum-family, so one finding, not four. Fails: LOWVOL, RESMOM (−0.02 / 1.51), CONTRA, MA2, MA3, TSMOM (0.78 / 0.45), CHANFADE, DUALMOM, RSQ, CARRY (1.36 / −0.10), DOLLARCARRY, SKEW, NEWLIST, VOLTARGET, FOMCDAY, DISTRESS | see below |
| 2026-11-21 | Robustness of the 4 passes (results/2026-11-21-p151-robustness-of-batch-1-passes.md) | 42 neighbours | MOM: positive across most neighbours with formation 30-60 days and skip 0-7 days (crypto momentum is short-horizon; skip 14+ fails); without its best 3 coins ~0 in both periods. SECTOR: positive at 5 of 6 lookbacks; without best 3 coins ~0 in the last 12m. TRENDLO: the last 12m is one coin (PIPPIN +1.96 of +1.59); without it, negative. MOMCARRY: carry leg dead in the last 12m | MOM, SECTOR: PROBATION → shadow. MOMCARRY: PROBATION. TRENDLO: REJECT (one-coin result) |
| 2026-11-21 | SWP: liquidity-sweep fade at the 20-bar extreme | 1 | −0.06 to −0.10R both periods, nearly every regime | REJECT |

## Queue (not tested yet)
- Breadth scaled to 72 coins (e.g. >= 10 same-side breakouts = top half) on BRK longs only. CAUTION: suggested by the Q2 data (median breadth 10), so it needs the next 6 months as a true out-of-sample check.
- Strategies from "151 Trading Strategies" (Kakushadze & Serur) that apply to a single perp or a cross-section of coins (pending: the paper couldn't be downloaded from this environment).

### Pre-registered 2026-11-21: Q1 breakout in BTC's direction (BRKB)
Rule: identical to BRK, but longs only while BTC's 4h EMA50 > EMA200 and shorts only while below, read on the BTC
4h bar that closes with the signal bar. 1 variant, no tuning. Pass if: avg R and R/month both beat BRK in the last
12 months and the 2 years before, and BRKB is positive in both.

### Pre-registered 2026-11-21: Q2 breadth filter on BRK
Rule: take a BRK trade only when at least 3 of the 72 coins give a same-side BRK signal on the same 4h close
(counted from raw signals, so it is known at the close: no look-ahead). Test threshold = 3. Thresholds 2 and 5 are
reported for context and counted as variants (3 total). Pass if: avg R and R/month (filtered trades) beat BRK's
in both periods... R/month can't beat unfiltered BRK with fewer trades unless the dropped trades lose, so the test is:
the dropped trades (breadth < 3) are negative in both periods and the kept ones positive in both.

### Pre-registered 2026-11-21: Q3 relative strength vs BTC (RS)
Rule: every Monday 00:00 UTC, rank coins with >= 90 days of history by 30-day return minus BTC's 30-day return.
Long the top 10, short the bottom 10, entry at the Monday 00:00 open. Stop 2 x daily ATR(14) from the signal close,
no target, exit after 7 days (next rebalance). BTC itself excluded. 1 variant (momentum direction only). Pass if: a leg
is positive in both periods with weekly t > 1 in at least one.

### Pre-registered 2026-11-21: Q4 funding-rate extremes (FUND)
Rule: when a coin's funding rate, normalized to 8 hours, is >= +0.05% (crowded longs), go short; <= -0.05%
(crowded shorts), go long. Signal at the first hour after the funding time, entry at that hour's open. Stop 2 x 4h
ATR(14), target 2R, max 48h, one trade per coin at a time. Funding received/paid is NOT added to R (fades usually
receive it, so this is conservative). 1 variant. Pass if: positive in both periods with weekly t > 1 in at least one.

### Pre-registered 2026-11-21: "151 Trading Strategies" batch 1 (studies/p151.py, map in ADAPTATION.md)
20 basket strategies, one fixed variant each (parameters in each function's docstring): direct ports MOM, LOWVOL,
RESMOM, CONTRA, MA2, MA3, TSMOM, CHANFADE, DUALMOM, TRENDLO, RSQ; lateral adaptations CARRY, MOMCARRY, DOLLARCARRY,
SKEW, NEWLIST, SECTOR, VOLTARGET, FOMCDAY, DISTRESS. Daily portfolio engine, net of 0.06%/side costs AND funding.
Pass rule: net Sharpe >= 0.5 in both periods; long-only books must also beat the equal-weight long basket in both.
With 20 tests, about 1 could pass by luck at this bar: a pass is a candidate for shadow testing, not proof.

Caveat for every basket result: the universe is today's 72 listed coins, so it has survivorship bias (coins that
were delisted after crashing are missing). That flatters long legs and hurts short legs.
