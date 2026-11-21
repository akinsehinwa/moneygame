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
| 2026-11-21 | p151 batch 2: PAIRS (most-correlated pairs, short the 7-day winner) | 1 | Sharpe −1.59 old / +2.67 12m; w/o best 3 coins −0.67 / +0.10 | REJECT (works only in the last 12m) |
| 2026-11-21 | p151 batch 2: ECO (mean reversion inside ETH / SOL / BTC / BNB ecosystems) | 1 | Sharpe −0.91 / +1.58 | REJECT (same regime flip as PAIRS) |
| 2026-11-21 | p151 batch 2: PIVOT (daily pivot, 1h execution) | 1 | Sharpe −3.05 / −4.89, about −110%/yr: costs from constant flipping | REJECT |
| 2026-11-21 | p151 batch 2: DISPMOM (MOM only when dispersion is high) | 1 | Sharpe 0.30 / 1.81 vs plain MOM 0.71 / 1.12; w/o best 3 −0.16 / +0.07 | REJECT (the gate hurts in the old period) |
| 2026-11-21 | p151 batch 2: CROWDFADE (fade the crowd: global long/short account ratio, 7d vs 90d, short the 7 most crowded-long, long the 7 most crowded-short) | 1 | Sharpe 0.92 old / 1.85 12m; w/o best 3 coins +0.13 / +0.02; robustness: 26 of 27 neighbours positive in both periods, every calendar year positive, correlation with MOM 0.13, 50/50 with MOM Sharpe 1.10 / 1.98 | ADOPT → shadow |
| 2026-11-21 | p151 batch 2: CROWDTOP (follow top traders vs the crowd) | 1 | Sharpe 0.36 / 0.93; w/o best 3 negative both | REJECT |
| 2026-11-21 | SWP: liquidity-sweep fade at the 20-bar extreme | 1 | −0.06 to −0.10R both periods, nearly every regime | REJECT |

## Queue (not tested yet)
- Regime switch between MOM (momentum) and PAIRS/ECO (mean reversion): mean reversion won the last 12m, momentum both periods. CAUTION: suggested by batch-2 results, so it needs a walk-forward rule chosen without peeking.
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

### 2026-11-21: shadow book started (shadow.py)
MOM (60d / skip 7 / 7 per side, weekly) and SECTOR (30d, weekly) paper-traded forward from the rebalance closing
2026-11-23 00:00 UTC. Weights frozen on record, never regenerated. Promotion review after ~12 rebalances: forward
Sharpe >= 0.5 and no drawdown beyond the backtest's worst (MOM −25%, SECTOR −24%) → Candidate; otherwise back to the ledger.

### Pre-registered 2026-11-21: "151 Trading Strategies" batch 2 (studies/p151b.py)
6 strategies, one fixed variant each (rules in the file's docstring): PAIRS (3.8), ECO (3.9.1 / 14.4 ecosystem
clusters), PIVOT (3.14, 1h execution), CROWDFADE and CROWDTOP (9.2 hedging pressure via Binance long/short metrics),
DISPMOM (6.3 dispersion as a gate on MOM). Pass rule, stricter than batch 1 after its lessons: net Sharpe >= 0.5 in
both periods AND positive in both periods without the book's 3 best coins.

### 2026-11-21: CROWDFADE added to the shadow book (before its first rebalance on 2026-11-23). Same review rule:
after ~12 rebalances, forward Sharpe >= 0.5 and drawdown within the backtest's worst (−23%).

### Pre-registered 2026-11-21: prop-ready compact books (studies/prop.py, rules in PROP_RULES.md)
Books (weekly, Monday 00:00 UTC = 08:00 SGT; every position closed and reopened weekly because of the 7-day hold):
- CF2: CROWDFADE score, 1 long + 1 short.   - CF4: CROWDFADE, 2 long + 2 short.
- MOM4: MOM score, 2 long + 2 short.        - COMBO4: average cross-sectional rank of CROWDFADE and MOM, 2 + 2.
Every position: stop 3 x daily ATR(14) from entry, take-profit 3R, time exit before the next rebalance; 1h execution,
stop first on ambiguous bars, stops fill at the worse of stop and open. Costs 0.04% fee + 0.02% slippage per side,
no funding (the firm charges none). Equal risk per position.
Pass (tradable): avg R > 0 and Sharpe of the weekly R series >= 0.5 in both periods.
Challenge simulation (informational, all books, risk 0.5 / 1 / 1.5 / 2% of the starting balance per position): every
weekly start date from 2023-11-20; stage 1 (+8% / -10% floor / -5% daily from the day's starting equity, floating
losses at each hour's worst price) then stage 2 (+5% / -8%); close everything once floating profit reaches the target.
CAUTION: the strategies were chosen on this same history, so the simulation is optimistic.
