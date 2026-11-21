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
| 2026-11-21 | Prop compact books (results/2026-11-21-prop-compact-books.md) | 4 books + 5 risk levels | Tradable (weekly R Sharpe old / 12m): COMBO4 1.17 / 2.02, CF2 0.76 / 1.38, CF4 0.55 / 2.17 pass; MOM4 0.47 / 0.98 fails. But the edge per position is thin (+0.05 to +0.07R), so challenges are slow: best case COMBO4 at 1.5% risk per position, by day 180: 34% passed both stages, 24% passed stage 1, 15% failed (mostly the total-loss floor), 26% still running. Higher risk raises failures faster than passes | COMBO4: ADOPT → shadow (prop version). Conclusion: good as a slow funded-account engine, too slow alone for passing challenges |
| 2026-11-21 | SWP: liquidity-sweep fade at the 20-bar extreme | 1 | −0.06 to −0.10R both periods, nearly every regime | REJECT |

## Queue (not tested yet)
- CROWDFADE on the 4H clock (positioning data is 5-minute; signals at 4H closes, entries at the next 4H open, 24-72h holds): more trades per week so challenges pass faster. Matches the user's 4H execution preference.
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

### 2026-11-21: data fix + new direction
- Data: LIT's history before 2025-12-23 and PUMP's before 2025-07-10 were dead contracts (zero volume, frozen prices;
  LIT's ticker was reused for a new token). lib/data.load_1h now drops everything before the last 3+ day zero-volume
  stretch. Re-run: MOM 0.83 / 1.22, SECTOR 0.86 / 1.10, MOMCARRY 1.61 / 0.73, TRENDLO 0.75 / 1.56, CROWDFADE
  0.96 / 1.91 (w/o best 3: 0.15 / 0.04). Same verdicts.
- Universe atlas v1 (results/2026-11-21-universe-atlas.md): coin traits are NOT stable between the old 2 years and the
  last 12 months (rank correlations 0.13-0.54; cluster membership ARI 0.03). Only volatility ratio and correlation
  are fairly persistent. The 2-ATR retracement measure was too loose (85-90% everywhere) and is replaced in atlas v2.
- New plan (PLAN.md): element profiles per coin per Bitcoin state, memory test, groups, then strategy tests validated
  on held-out Bitcoin episodes.

### 2026-11-21: element atlas (results/2026-11-21-element-atlas.md, -element-atlas-e5-by-leg-direction.md)
- Memory test (90 days -> next 90 days, rank correlation across coins): only the BTC link and volatility are stable
  coin traits (vol vs BTC 0.57, correlation 0.43, beta up 0.30). Momentum, retracement, displacement and sweep
  behaviour are NOT stable per coin (about 0): they depend on Bitcoin's state, not on which coin it is.
- Groups from the stable traits (k=5): G0 majors (low vol, tight BTC link), G1 mid alts (38 coins), G3 high-beta
  (PEPE BONK WIF FLOKI BRETT BOME ENA ETHFI VIRTUAL STX), G4 independents (TRX WLFI XMR), G2 outliers (PIPPIN RIVER).
- Bitcoin state matters more than coin type: after a big leg pulls back 50%, the chance of continuing to a new
  extreme is about 0.2 when BTC is in DOWN / STRONG_DOWN, versus 0.35-0.45 in COIL / RANGE / UP (break-even for a 50%
  entry, 78.6% stop, prior-extreme target is about 0.36). Small caps' down legs pull back 50% less often in a strong
  BTC fall (0.42 vs 0.48 for large caps) and much less in COIL (0.26).
- Displacement candles follow through in COIL and UP (+0.4 to +1.1 ATR over 24h) and reverse in STRONG_DOWN / RANGE.
  Daily momentum reverses in DOWN (next day agrees with the past week only 45% of the time).

### Pre-registered 2026-11-21: step 5, strategies by coin group x Bitcoin state, held-out episodes (studies/episodes.py)
- New strategy SW50 (from the user's swing description + atlas E5): after a big leg (>= 6 ATR within 5 days on 4h)
  confirmed by a 1-ATR pullback, a limit order at the 50% retracement; stop at the 78.6% level; target the leg's
  extreme; cancelled if price makes a new extreme first or after 10 days unfilled; max hold 7 days; both directions;
  1h fills, costs 0.06%/side.
- Episodes = runs of consecutive days in the same BTC state (last completed day). Within each state, episodes are
  assigned to 5 folds in turn. For each fold: switch on cells (strategy+side x coin group x BTC state) whose average R
  on the OTHER folds is > 0.10 with >= 30 trades; score the held-out fold. Routers compared: take everything,
  strategy only, + BTC state, + coin group, + both. Pass: router avg R > 0.05 out of episode, positive in >= 4 of 5
  folds. Trades from all strategies in data/trades.pkl plus SW50.
| 2026-11-21 | Step 5 (results/2026-11-21-step-5-held-out-episodes.md): routers across ALL strategies, validated on held-out BTC episodes | 5 routers | All fail: take everything −0.008R; + BTC state −0.034; + coin group −0.009; + both −0.026 (1-2 of 5 folds positive). Picking many cells by state/group overfits across episodes | REJECT (blanket routing) |
| 2026-11-21 | Step 5 per strategy: routed by state + group, out of episode | 22 legs | Survive in >= 4/5 held-out folds: STD long +0.19R (5/5), BRK short +0.23 (4/5), STD short +0.10 (4/5), BRKB long +0.08 (4/5), FUND short +0.07 (4/5), SW50 short +0.04 (4/5), ST4 short +0.02 (4/5) | PROBATION: selective routing of these legs only (next test) |
| 2026-11-21 | SW50 (user's swing idea: big leg, 50% pullback, continue to the extreme), all 72 coins | 1 | 4,402 trades, +0.004R overall. As the atlas predicted, longs lose when BTC is DOWN / STRONG_DOWN (−0.31 / −0.49R) and are slightly positive in RANGE / UP / STRONG_UP (+0.05 / +0.11 / +0.07); shorts best in UP (+0.42R, small sample). Fixed a bug first (signals processed longs-then-shorts blocked most shorts) | PROBATION: SW50 only in COIL / RANGE / UP states (filter implied by the atlas before SW50 was run) — needs its own forward check |

### 2026-11-21: COMBO4 (prop version) added to the shadow book from the 2026-11-23 rebalance, marked trade by trade
(stop 3 ATR, target 3R; a short's take-profit is floored at 10% of entry so it is always a valid order price).

### Pre-registered 2026-11-21: multi-account study (studies/prop_multi.py)
Accounts: 50K two-step + two 100K two-step; only ONE 100K can ever be funded, so the two 100Ks are a race (only the
first pass matters). Rules as PROP_RULES.md (same % limits on 100K). Weekly books with stop 3 ATR / target 3R.
- 100K race schemes (each account <= 5 positions): R1 same book in both (COMBO4 + COMBO4); R2 one 8-coin COMBO book
  dealt out (account A gets long/short ranks 1 and 3, account B ranks 2 and 4); R3 different strategies (CF4 + MOM4);
  R4 = R3 with unequal risk (CF4 at 2%, MOM4 at 1%). Risk per position 1 / 1.5 / 2% (equal) for R1-R3.
  Measures from every weekly start with 180+ days of data after it: P(at least one 100K passes both stages) by day 90
  and 180, median day of the first pass, P(both failed by day 180).
- 50K: COMBO4 / CF4 / MOM4 at 1 / 1.5 / 2%: P(passed both stages) by day 180.
- Funded phase (100K and 50K): same books at 0.5 / 1 / 1.5%: 180 days from every start, payout of any profit every
  15 days at 80% (balance resets, the 8% floor stays): P(blown within 180 days), average payout per month in USD.
Informational (no pass rule). Same caveat: strategies were chosen on this history, so results are optimistic.

### 2026-11-21: live-trading constraints (user trades 5x isolated, limit entries, 1.75% risk today)
- Bug fixed in studies/prop.py: on the exit candle the wick beyond the stop was counted as loss (up to -3.5R instead of
  -1R), which overstated daily-limit breaches. Earlier prop results were too pessimistic; re-run below.
- 5x isolated liquidates about 19.5% from entry, but the tested 3-ATR stop is median 24% away (90th pct 37%).
  Variants tested now (counted): stop 1.5 x ATR and 2 x ATR, coins skipped if the stop is > 15% away, target 3R.
| 2026-11-21 | Tighter stops for 5x isolated (stop 1.5 / 2 ATR, skip stops > 15%) | 2 | 1.5 ATR: one account negative in the old period; 2 ATR: weaker than 3 ATR. Solution instead: keep 3 ATR and ADD isolated margin so liquidation sits beyond the stop (user's suggestion) | keep 3 ATR + added margin |
| 2026-11-21 | Two-account allocation (results/2026-11-21-prop-two-accounts-different-rankings.md) | 3 schemes | Alternate ranks (1+3 / 2+4): the 2+4 account has no edge (Sharpe −0.67 / 0.08). Different rankings, no overlap: 100K COMBO top 2+2 (0.46 / 1.09) + 50K CROWDFADE top 2+2 (1.13 / 1.78): at 1.5-1.75% risk, at least one account passes both stages by day 180 in 23-35% of starts, both fail together 0%, daily limit never hit. MOM as the second account fails more | ADOPT: 100K COMBO, 50K CROWDFADE, 1.5% per coin |
| 2026-11-21 | Entry weekday and signal age (results/2026-11-21-cadence-entry-weekday-and-signal-age.md) | 14 | Monday 08:00 SGT entry is among the best days for both strategies with fresh or 2-day-old signals; results swing a lot by weekday (the edge is noisy) | Tickets generated Monday 08:07 SGT (scheduled task) from the newest archive data (usually 1-2 days old), placed as limit orders around 08:30 SGT |

### 2026-11-21: live data from TradingView (user's choice)
Monday tickets use TradingView for everything recent: daily candles and the long/short ratio (BINANCE:<SYM>USDT.P_LSR,
correlation 0.94 / 0.98 with the archive's account ratio for BTC / SOL, same level) fill the archive's 1-2 day gap,
so signals use Sunday's completed candle; entry, stop and take-profit prices come from TradingView live prices. First
real tickets: Monday 2026-11-23 just after 08:00 SGT. The 2026-11-21 tickets file is a format preview only.

### Pre-registered 2026-11-21: trade management for the weekly tickets (studies/manage.py)
Books: 100K COMBO top 2+2 and 50K CROWDFADE top 2+2 (no overlap), stop 3 ATR, TP 3R, entry Monday 08:00 SGT.
Check-ins at Thursday 08:00 SGT (72h) and Sunday 08:00 SGT (144h). Variants (6):
- V0 hold to the Monday exit (baseline, 7 days).
- V1 cut losers: at a check-in, close if the trade is at or below -0.5R.
- V2 protect winners: at a check-in, if the trade is at or above +1R, move the stop to breakeven.
- V3 = V1 + V2.
- V4 majors to day 10: majors (BTC ETH BNB XRP SOL TRX HYPE ZEC DOGE ADA) that are in profit at the Monday exit are
  held up to Thursday 08:00 (day 10) with their stop and TP; everything else exits Monday.
- V5 = V4 for any coin in profit (NOT allowed for non-majors by the firm; reference only, to see if holding longer pays).
Measure avg R per position, weekly Sharpe, both periods. Adopt a rule only if it beats V0 in both periods.
| 2026-11-21 | Trade management (results/2026-11-21-trade-management-variants.md) | 6 | Cut losers at -0.5R (V1), breakeven at +1R (V2), both (V3): no meaningful change (+/-0.003R). Majors in profit to day 10 (V4): 50K better (0.041 / 0.069 vs 0.031 / 0.044R), 100K worse in the last 12m (0.022 vs 0.038R). Any coin to day 10 (V5): worse in both | Hold 7 days, no early exits, fresh list every Monday. V4 not adopted (fails "better in both"). Thursday / Sunday check-ins are for sanity only (fills, unfilled orders cancelled Thursday, stops in place, limits) |

### Pre-registered 2026-11-21: limit-order fills and cancel timing (studies/fills.py)
The backtest entered at Monday's open; live tickets are limit orders placed ~08:30 SGT. Model: limit at Monday's open
price moved 0.5% in the trade's favour (long 0.5% below, short 0.5% above: price has drifted by placement time).
Fill when price trades through the limit. Stop / TP at the same % distances from the fill; exit at Monday 08:00 SGT
regardless of fill time. Compare cancel rules: cancel if not filled within 4h, 24h (Tue 08:00), 72h (Thu 08:00), or
never (until Monday). Measure: fill rate, avg R of filled trades, and R per ticket issued (unfilled = 0), both
periods, both accounts. Also avg R by fill delay. Pick the rule with the best R per ticket in both periods.
| 2026-11-21 | Limit fills and cancel timing (results/2026-11-21-limit-fills-and-cancel-timing.md) | 4 rules | Cancel after 4h is worst (fill rate ~75%, R per ticket negative in the last 12m). Fills after 4-72h are as good as fast ones; fills after 72h mixed (50K -0.17R, n=16). Cancel at Thursday 08:00 SGT: best or near-best in 3 of 4 period x account cells, ~94% filled | Keep unfilled orders until the Thursday 08:00 SGT check-in, then cancel |

### Pre-registered 2026-11-21: CF4H, crowd positioning on the 4H clock (studies/cf4h.py)
Rule: at each 4H close at 08:00 / 12:00 / 16:00 / 20:00 SGT (daytime only), crowd score per coin = mean of the global
long/short account ratio over the last 6 4h bars (1 day) / its mean over the last 84 bars (14 days) - 1. Long the
coin with the lowest score (crowd most short vs its norm), short the coin with the highest score; skip a coin already
held. Entry at the next 4H open (limit at that price). Stop 3 x ATR(14, 4h); skip if the stop is > 15% away (fits 5x
isolated without extra margin). Take-profit 2R. Time exit 48h. Costs 0.06% per side. 1 variant.
Pass (standalone): avg R > 0 and weekly Sharpe >= 0.5 in both periods, and positive in both without the 3 best coins.
If it passes, a slot-constrained two-account simulation (pre-registered here): max 5 open positions per account,
unfilled limits don't count as positions but count toward margin; margin (open + pending) <= 60%; when 5 are open,
pending limits are cancelled. Allocation schemes: A) each account = its weekly book (4 slots) + CF4H in the free slot;
B) 100K weekly COMBO + 1 CF4H slot, 50K CF4H only (5 slots); C) both accounts CF4H only (5 slots, the 50K takes the
2nd-ranked signal so the accounts never hold the same coin). Risk 1.5% per position (weekly) and 1.0% (CF4H).
Challenge outcomes by day 90 / 180 as before.
Note: Bitfunded's treatment of pending-order margin is unverified (site blocked here); the simulation counts it.
| 2026-11-21 | CF4H: crowd positioning on the 4H clock (results/2026-11-21-cf4h-standalone.md) | 1 | Old: +0.015R, weekly Sharpe 0.27 (shorts +0.033, longs ~0); last 12m: -0.064R, Sharpe -3.2 (both sides negative); without best 3 coins negative in both | REJECT. The crowd edge is slow; at 4H speed it is noise. Combined two-account test not run (pre-registered condition not met) |

### Pre-registered 2026-11-21: CF1D, crowd positioning on the daily clock (studies/cf4h.py with --daily)
Same as CF4H except: one signal a day at 08:00 SGT (00:00 UTC close); score = mean of the 4h long/short ratio over the
last 18 bars (3 days) / its mean over the last 180 bars (30 days) - 1; time exit 72h. Stop 3 x ATR(14, 4h) (<= 15%),
TP 2R, long lowest / short highest. 1 variant (2nd speed tried for the crowd idea after weekly and 4H). Same pass rule;
if it passes, the slot-constrained two-account simulation runs with CF1D in place of CF4H.
| 2026-11-21 | CF1D: crowd positioning on the daily clock (results/2026-11-21-cf1d-standalone.md) | 1 | Both sides: +0.033R old (Sharpe 1.02) / +0.037R 12m (1.03), but negative without the best 3 coins (−2.5 / −1.6R) → fails the pre-set rule. Shorts alone: +0.072 / +0.089R, Sharpe 0.96 / 1.51, positive without the best 3 coins; longs alone negative in both periods | REJECT as pre-registered. Data-suggested follow-up (not a pass): CF1D shorts only → paper-trade forward before any live use |

### 2026-11-21: CF1D SHORTS ONLY frozen for a forward test (studies/cf1d_forward.py), paper only, not on the tickets
Rules exactly as the CF1D test, shorts only. Forward window starts with the 2026-11-22 08:00 SGT signal. Report due
2026-12-23 (scheduled): avg R, win %, sum R vs the backtest (+0.072 / +0.089R, 57% win in the last 12m). Promotion to the
free 5th slot only if the forward avg R is positive with ~15+ trades AND the next month confirms; otherwise graveyard.
| 2026-11-21 | Weekly books by BTC state (results/2026-11-21-weekly-books-by-btc-state.md) | descriptive | STRONG_DOWN (the current state): 100K avg week +0.03%, worst -1.53%; 50K -0.09%, worst -1.08% (17 weeks each, 59% losing). Most profit came in COIL / UP for the 100K and DOWN / RANGE / UP for the 50K | Expect flat weeks now. No state filter added (would be chosen after seeing these numbers) |
| 2026-11-21 | Funded-phase risk plan (results/2026-11-21-funded-risk-plan.md) | 5 risk levels x 2 | 100K (COMBO): breach within 180 days 1% / 9% / 12% / 16% / 30% at 0.5 / 0.75 / 1.0 / 1.25 / 1.5% per coin; avg payout to the trader $311 / 466 / 621 / 776 / 916 per month. 50K (CROWDFADE): no breach at any level up to 1.5%; avg payout $135 / 202 / 269 / 337 / 404 per month | Once funded: 100K drops to 1.0% per coin, 50K stays at 1.5% (plan; re-check before switching) |

### Pre-registered 2026-11-21: research batch 3 (studies/batch3.py)
1. OIFADE (weekly basket, portfolio engine, costs + funding): score = -(7-day mean of open-interest VALUE / its 30-day
   mean - 1); long the 7 highest scores (OI flushed out), short the 7 lowest (OI piling in). Weekly, Monday 08:00 SGT.
2. OIFADE + CROWDFADE: 50/50 of the two books.
   Pass rule (both): net Sharpe >= 0.5 in both periods AND positive in both without the 3 best coins.
3. Perp premium: NOT tested. Binance's funding rate is computed from the premium index, so it is the same signal as
   CARRY (rejected: Sharpe 1.36 old / -0.10 last 12m).
4. BTC daily CRT patterns (BULL_CRT, BEAR_CRT, BREAK_UP, BREAK_DN, INSIDE, OUTSIDE; lib/btcstate.py): next-day
   return of the equal-weight basket of eligible coins and of BTC. A pattern is a candidate only if the basket's
   next-day mean has the same sign in both periods with |t| >= 2 over the whole sample (6 patterns tested, so ~0.3
   could pass by chance at this bar).
| 2026-11-21 | Batch 3 (results/2026-11-21-research-batch-3.md) | 2 books + 6 patterns | OIFADE: Sharpe -1.33 old / -0.97 12m (fails; the reverse looks like momentum: OI piling into trending coins). OIFADE + CROWDFADE: -0.43 / 0.77 (fails). BTC OUTSIDE day: alt basket next day +1.15% (t 2.21; old +1.31, 12m +0.74; 49 days) = candidate; the other 5 CRT patterns not significant | OUTSIDE: paper forward test. OIFOLLOW (reverse of OIFADE, data-suggested): paper forward test. Both frozen in studies/batch3_forward.py, reported with the 2026-12-23 report |

### 2026-11-21: conclusion on prop suitability + operations paused
User decision: not trading these books. Agreed conclusion: the weekly books are NOT prop-challenge strategies. They
earn +0.03 to +0.09R per position with ~16 positions a month, i.e. about 0.5-1.5R a month; passing +8% in about a
month at 1% risk needs about 8R a month (e.g. 20 trades at +0.4R or 40 at +0.2R), roughly 5-10x more edge or volume.
Weekly ticket, check-in and shadow tasks paused; all paper books and forward tests are replayed in one batch on
2026-12-23 (rules are frozen and signals are deterministic, so a batch replay equals running weekly).
New bar for prop strategies: >= +0.2R per trade after costs with >= 20 trades a month per account, positive in both
periods, and a challenge simulation passing stage 1 within ~45 days in most starts.

### Pre-registered 2026-11-21: data-snooping check with arch (studies/spa.py)
All 28 basket books tested so far (p151 batch 1: 20, batch 2: 6, batch 3: OIFADE and OIFADE+CROWDFADE), daily net
returns (costs + funding), loss = -return, benchmark = cash (0). Hansen's SPA test (is the best book better than cash
after accounting for all 28 tried?) and Romano-Wolf StepM (which books beat cash), stationary bootstrap, 10,000 reps,
block 10 days, 5% level. Run on the whole sample (2023-11-20 onward) and on the last 12 months.
| 2026-11-21 | Data-snooping check, SPA + StepM over all 28 basket books (results/2026-11-21-data-snooping-check-spa-stepm.md) | 28 | Whole sample: best = MOMCARRY (Sharpe 1.30; CROWDFADE 1.28), single-test p 0.012 but SPA p 0.24-0.36; StepM: no book beats cash. Last 12m: best = PAIRS (2.62), SPA p 0.19-0.33; StepM: none | Nothing we found is statistically better than cash once all tries are counted (and 28 undercounts: ~100+ variants were tried in total). The robustness checks were encouraging but not proof; forward tests decide. From now on every candidate also goes through SPA / StepM over the full list of variants tried |

### Pre-registered 2026-11-21: shortlist setup detectors (studies/shortlist_bt.py)
Scans at the 4H closes of 08:00 and 20:00 SGT, all 72 coins, 4H bars, ATR(14, 4H) = A. BTC state = last completed day.
- COIL: Bollinger(20) width in the lowest 10% of the last 120 bars AND close within 1 A of the 20-bar high or low.
  Levels: break above the 20-bar high (long) or below the 20-bar low (short), whichever comes first within 48h;
  entry on the touch (stop order), stop at the range middle, target 2R, time exit 72h.
- SWING50: a leg >= 6 A within the last 30 bars whose extreme formed in the last 12 bars, now retraced 20-45%.
  Level: limit at the 50% retracement (valid 48h), stop at 78.6% + 0.1 A, target the leg's extreme, time exit 72h.
- DISP: the scan bar's body >= 2 A. Level: limit at the body's midpoint (valid 24h), stop beyond the bar's opposite
  extreme + 0.1 A, target 2R, time exit 72h.
1h fills, stop first on ambiguous bars, costs 0.06% per side. Questions: (1) do flagged coins move more over the next
24h than the rest (range in ATR units)? (2) per detector x side x BTC state: hit rate of the level and avg R after the
fill, both periods. A detector (x side) is useful only if avg R > 0 in both periods; per-state cells reported for
context, not used to pick (would be data-mined). 3 detectors x 2 sides = 6 tested legs.
| 2026-11-21 | Shortlist detectors (results/2026-11-21-shortlist-detectors.md) | 6 legs | (1) Flagged coins do NOT move more over the next 24h than unflagged ones in ATR terms (median 2.20 vs 2.24 ATR; COIL 2.44, DISP 2.90, SWING50 2.07). (2) Mechanical trades at the levels: COIL breakouts +0.17 / +0.04R old but -0.02 / -0.30R last 12m (recent breakouts fake out, longs especially); DISP pullbacks mixed (-0.28 / +0.13 old, +0.01 / -0.08 12m); SWING50 short +0.018 / +0.091 (only leg positive in both, small), SWING50 long +0.033 / -0.031. Context only: swing longs +0.21R when BTC is UP, -0.17R when DOWN | No setup has a reliable mechanical edge. A shortlist would be attention management + BTC context, with the edge coming from the trader's discretion |
