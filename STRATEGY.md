# Adaptive strategy playbook

The system runs a loop: **detect the regime → pick the playbook for it → tag every trade → measure → revise.**
Each morning `python3 sim/regime.py` labels the market `trend/volatility/leadership`. Every order is placed
with `--strategy <name> --regime <label>`, and `python3 sim/ledger.py stats` reports results by both.

## 1. Regime detection (sim/regime.py)
| Axis | Rule | States |
|---|---|---|
| Trend | SPY vs 50/200-day SMA, slope of the 20-day SMA | up / range / down |
| Volatility | VIX | low <16, normal 16-22, high 22-30, extreme >=30 |
| Leadership | 20-day return, defensives (XLV XLP XLU) minus cyclicals (XLK XLY XLF XLI) | risk-on < -2pp, mixed, risk-off > +2pp |
| Breadth | sectors above their 20-day EMA | 0-11 |

## 2. Playbook by regime

> **Backtest update 2026-11-18 (journal/backtest-2026-11-18.md). These override the table below where they conflict.**
> 1. `range-mean-reversion` (dip-buying) is allowed in **every** regime: buy sector ETFs or SPY when 2-day RSI < 15.
>    Above the 200-day SMA always; below it only when VIX >= 22. Stop 2.5 ATR. Exit on the first close above the
>    5-day SMA, at 1.5R, or after 7 days. This was the only edge that held out of sample (67% win rate, positive avg R in train and validate).
> 2. `inverse-index-trend` is **dropped** (negative out of sample).
> 3. `defensive-leader-pullback` is kept for down/risk-off regimes (best out-of-sample Sharpe); stops widen to 2.5 ATR.
> 4. Being in cash in downtrends costs returns: average SPY returns after "down" days were higher than after "up" days.
>    The regime sets **position size and stop width**, not whether to be in the market.

| Regime | Strategy name(s) | What to buy | Max invested | Stop / target |
|---|---|---|---|---|
| **up / low-normal / risk-on** | `trend-leader-pullback` | Strongest sectors or mega-caps pulling back to the 10/20 EMA | 90-100% | Stop 1 ATR under the swing low; target 2-3R, then trail |
| **up / high** | `trend-leader-pullback` (half size) | As above, fewer positions | 60% | Tighter: 0.75 ATR |
| **range / any** | `range-mean-reversion` | Quality ETFs at range support with 2-day RSI < 10 | 50-70% | Stop under the range; target the range midpoint (1-1.5R) |
| **down / normal-high / risk-off** | `defensive-leader-pullback`, `inverse-index-trend` | Defensive-sector leaders; unleveraged inverse ETFs (SH, PSQ) on failed bounces | 50-70% | Stop above/below the last swing; target 1.5-2R |
| **down / extreme** | `capitulation-bounce` | SPY/QQQ after a VIX spike >30 plus a reversal day, small size | 25-40% | Stop under the reversal-day low; target 1.5R, take it fast |
| **any, unclear signal** | `cash` | Nothing. Doing nothing is a valid position. | 0-30% | n/a |

Constant across regimes: max 25% per position, limit orders only, every trade has a stop and a target,
risk about 1-2% of equity per trade, no single stocks held through earnings, only tighten stops.

## 3. Learning rules
- Every playbook change must first pass `python3 sim/backtest.py`: better on TRAIN **and** not worse on VALIDATE. The TEST period (2021-26) is run once, at the end.
- At the weekly review (Fridays, plus Thu 2026-12-24), compare each strategy's stats by regime.
- Change a rule only with evidence: at least 5 closed trades for that strategy, or a clear structural error
  (for example, entries that never fill). Record every change in the changelog below, with the reason.
- A strategy with avg R < -0.3 over 8 or more trades in a regime is suspended for that regime.
- Report honestly: a month of data is a small sample. One regime may dominate the whole test.

## 4. Changelog
| Date | Change | Evidence |
|---|---|---|
| 2026-11-16 | Started with `defensive-leader-pullback` (regime: down/normal/risk-off) | Tech-led sell-off, defensives above 20-day EMA |
| 2026-11-17 | Added regime detection, strategy tagging, playbook, and unleveraged inverse ETFs for downtrends | Competition extended to 2026-12-31; organizer asked for an adaptive system |
| 2026-11-17 | Leaders: set entries ~0.3% below last price, not at the prior close | XLP limit at the prior close never filled on Day 1, missing the best performer |
| 2026-11-17 | PROVISIONAL: pause `defensive-leader-pullback` when breadth <= 3/11; cap exposure at 30% | Day 2: breadth 7/11 → 3/11; XLV and XLF both stopped (−1R each) as defensives fell with SPY. Only 2 trades, so re-test at the 11-20 review |
| 2026-11-18 | Built 27-year backtest; adopted dip-buying in all regimes, 2.5-ATR stops; dropped inverse-index-trend; retired the 11-17 breadth rule | journal/backtest-2026-11-18.md: v1 playbook lost to v3 on train and validate; inverse trades negative out of sample; breadth threshold had no effect |
