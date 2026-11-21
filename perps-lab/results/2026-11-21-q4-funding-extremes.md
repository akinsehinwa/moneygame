# Q4 funding extremes (2026-11-21)

Trades 3902, coins 72, signals 2023-11-21 to 2026-10-31. R per trade at 1R risk, costs included. Old = before 2025-11-20, 12m = after. t = weekly-clustered t-stat (|t| < 2 is not significant).

## 1. Scorecard

| strategy | n old | avgR old | n 12m | avgR 12m | win% 12m | t 12m | R/mo 12m | holds |
|---|---|---|---|---|---|---|---|---|
| FUND long | 1217 | 0.018 | 861 | -0.041 | 41 | -0.9 | -2.9 |  |
| FUND short | 1587 | 0.044 | 237 | -0.026 | 48 | 0.1 | -0.5 |  |

## 2. By coin regime

| strategy | coin regime | n | avgR | old | 12m | holds |
|---|---|---|---|---|---|---|
| FUND long | DOWN/CHOP | 782 | -0.04 | 0.02 | -0.11 |  |
| FUND long | DOWN/TREND | 526 | 0.07 | 0.12 | 0.0 |  |
| FUND long | RANGE/CHOP | 207 | 0.0 | 0.07 | -0.09 |  |
| FUND long | RANGE/TREND | 54 | 0.31 | 0.23 | 0.48 | yes |
| FUND long | UP/CHOP | 295 | -0.1 | -0.13 | -0.05 |  |
| FUND long | UP/TREND | 214 | -0.04 | -0.1 | 0.04 |  |
| FUND short | DOWN/CHOP | 206 | 0.08 | 0.05 | 0.12 |  |
| FUND short | DOWN/TREND | 85 | 0.07 | -0.04 | 0.15 |  |
| FUND short | RANGE/CHOP | 84 | -0.1 | -0.05 | -0.3 |  |
| FUND short | UP/CHOP | 713 | 0.09 | 0.1 | -0.01 |  |
| FUND short | UP/TREND | 716 | -0.02 | 0.01 | -0.4 |  |

## 3. Walk-forward routers (out of sample, 2024-11-20 onward, cell on if past avg R > 0.10, n >= 40)

| router | trades/mo | avgR | t | R/mo | quarters + |
|---|---|---|---|---|---|
| take everything | 94 | -0.015 | 0.3 | -1.5 | 4/8 |
| strategy+side | 0 |  |  | 0.0 | 0/0 |
| + market regime | 26 | -0.102 | -0.3 | -2.6 | 1/5 |
| + coin regime | 20 | -0.024 | 1.7 | -0.5 | 4/7 |
| + market + coin regime | 6 | -0.154 | 1.5 | -1.0 | 4/7 |
| + coin group | 21 | -0.021 | 1.3 | -0.4 | 2/4 |
| + single coin | 13 | -0.093 | -0.6 | -1.3 | 3/8 |
