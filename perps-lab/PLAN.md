# Plan: understand the coins first, then test strategies by coin type x Bitcoin state

Why: chronological backtests mix very different Bitcoin cycles. Instead, pool history by **Bitcoin state** and describe
each coin by the **elements strategies are built from**. Then test strategies where their elements are present.

## Step 1. Bitcoin states (done: lib/btcstate.py)
STRONG_DOWN / DOWN / COIL / RANGE / UP / STRONG_UP (20-day move + Bollinger squeeze), and daily CRT patterns.

## Step 2. Element profiles for each coin, in each Bitcoin state (studies/atlas2.py)
The common core of most strategies (the paper's 151 included):
| element | question | measure |
|---|---|---|
| E1 momentum | do moves continue? | next-day sign agrees with the past 7 days |
| E2 reversal | do short moves snap back? | 4h return vs the next 4h return |
| E3 volatility | how wild, and do squeezes release? | vol vs BTC; move after a squeeze |
| E4 displacement | do big impulse candles follow through? | 4h body >= 2 ATR, next 24h move |
| E5 retracement (healthy trend) | after a big leg (>= 6 ATR), does price pull back to 50% and then continue? | P(50% pullback), days to it, P(continuation after it) |
| E6 liquidity sweeps | do sweeps of highs/lows reverse? | 20-bar sweep that closes back inside, next 24h move |
| E7 BTC link | inch vs mile, leader or follower | up/down beta, correlation, 4h lag |
| E8 crowd | does crowd positioning mean-revert on this coin? | crowd score vs next-week return |
Tokenomics, news and unlocks: not now (no data here; too coin-specific for the macro picture).

## Step 3. Memory test: which elements are stable traits?
For each element: does a coin's value over 90 days predict its value over the next 90 days (rank correlation across
coins)? Stable elements can be used as coin filters; unstable ones must be measured fresh (short windows) or ignored.

## Step 4. Coin groups from stable elements only, compared with niche and size tags.

## Step 5. Strategy x coin group x Bitcoin state, validated on held-out Bitcoin episodes
Each strategy is tested only where its key element is present (e.g. a retracement strategy on coins/states where E5 is
strong). Validation: learn on some episodes of a Bitcoin state, test on other episodes of the same state that were
left out (not just "the last 12 months").

## Status (2026-11-21)
- Steps 1-4 done (results/2026-11-21-element-atlas*.md). Key: Bitcoin's state drives behaviour; coin identity only
  shows in its BTC link and volatility.
- Step 5 first pass done (results/2026-11-21-step-5-held-out-episodes.md): blanket routing fails out of episode;
  a handful of individual strategy legs survive selective routing. Next: a selective router of only those legs,
  pre-registered, with the same held-out-episode test; then the 4H CROWDFADE version.
