# Weekly review — week 1 (Mon 11-16 to Fri 11-20)

## Scoreboard
| | Value |
|---|---|
| Balance | **$84.83** (−15.2%) |
| SPY since start | −8.5% (754.37 → 690.43) |
| Vs SPY | −6.7 pp |
| Max drawdown | −15.2% (peak $100 at the start; the low is today) |
| Goal ($1,000 by 12-31) | needs +9.6%/day for 27 days; **not realistically reachable** |
| Trades | 9 (7 closed: 1 win, 6 losses or flat) |

## Regimes seen (sim/regime_log.csv)
down/normal (11-16) → down/high (11-17 to 11-19) → **down/extreme** (11-20, VIX 39.7). Breadth fell 7/11 → 0-1/11.
**Untested: every up and range regime.** The system has only seen one falling market so far.

## Results by strategy (ledger stats; R = profit ÷ risk at entry)
| Strategy | Type | Trades | Result | Avg R |
|---|---|---|---|---|
| defensive-leader-pullback | early playbook | 3 closed | −$1.24 | −0.89 |
| range-mean-reversion (ETF dip-buy) | backtested | 2 closed | +$0.16 | +0.07 |
| lev-dip-buy (3x ETFs) | backtested | 1 closed, 1 open | −$6.68 | −0.86 |
| event-panic-rebound (NVDA) | judgment | 1 closed | −$4.44 | −1.00 |
| momentum-pullback (APP) | judgment | 1 open | −$2.97 | −0.94 |

## Changes made this week (STRATEGY.md changelog)
11-17 regime detection and tagging · 11-18 built the 27-year backtest; switched to dip-buying in all regimes; dropped inverse ETFs ·
**11-19 aggressive mode** (organizer: $1,000 goal): 3x ETFs, single stocks, fully invested, 3-5% risk per trade · 11-19 rule: no
repricing dip-buys up into gaps · Ledger fixes: time-ordered fills, and a look-ahead bug (reversed and logged).

## Honest assessment
1. **The aggressive switch is what hurt.** Before it (11-16 to 11-18) the account was −1.2% while SPY was −3.2%. Since it
   (11-19 to 11-20), the account fell −14.2% while SPY fell −5.5%. Three-times leverage into a falling market did what leverage does.
   The stops worked exactly as designed, and losses were the planned size. But four long-beta positions were one bet,
   so the stops all hit together.
2. **The backtested edge isn't refuted, but it's being tested in its worst case.** Dip-buying in extreme volatility has
   positive average R over 1999-2020. The average hides crashes like this one, where it loses big before it wins. A five-day sample
   says almost nothing about the edge. It says a lot about sizing.
3. **Would this hold up on live capital? Not yet.** The evidence is 9 trades in one regime, a −6.7 pp gap to SPY, and a 15% drawdown
   in one week. No strategy has positive live results except the small ETF dip-buy. Up and range regimes haven't been seen at all.
4. **Should the test be extended? Yes.** One down-trending week can't validate or reject an adaptive system. The point of the
   test is to see the system across regimes, and so far it has seen one.

## What I'm doing next week
- Stay aggressive in exposure, but **deploy new cash only on backtested signals** (capitulation-bounce, lev-dip-buy at prior-close entries).
  Judgment setups (event-panic-rebound, momentum-pullback) stay allowed but rank last until they have more trades.
- **Correlation cap:** at most 2 of 4 positions in 3x index ETFs at the same time, so one bad SPY day can't stop out the whole book.
- Keep the stops. I won't widen anything to avoid realizing a loss.
