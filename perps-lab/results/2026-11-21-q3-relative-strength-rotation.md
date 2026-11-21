# Q3 relative strength rotation (2026-11-21)

Trades 3099, coins 71, signals 2023-11-20 to 2026-11-09. R per trade at 1R risk, costs included. Old = before 2025-11-20, 12m = after. t = weekly-clustered t-stat (|t| < 2 is not significant).

## 1. Scorecard

| strategy | n old | avgR old | n 12m | avgR 12m | win% 12m | t 12m | R/mo 12m | holds |
|---|---|---|---|---|---|---|---|---|
| RS long | 1037 | 0.029 | 508 | -0.029 | 37 | -0.3 | -1.2 |  |
| RS short | 1044 | 0.024 | 510 | 0.037 | 57 | 0.6 | 1.6 | yes |

## 2. By coin regime

| strategy | coin regime | n | avgR | old | 12m | holds |
|---|---|---|---|---|---|---|
| RS long | DOWN/CHOP | 212 | 0.03 | 0.08 | -0.02 |  |
| RS long | DOWN/TREND | 40 | -0.01 | 0.48 | -0.5 |  |
| RS long | RANGE/CHOP | 169 | -0.07 | -0.04 | -0.15 |  |
| RS long | UP/CHOP | 574 | 0.09 | 0.11 | 0.03 |  |
| RS long | UP/TREND | 517 | -0.04 | -0.08 | 0.03 |  |
| RS short | DOWN/CHOP | 593 | 0.06 | 0.1 | -0.02 |  |
| RS short | DOWN/TREND | 606 | 0.01 | -0.05 | 0.08 |  |
| RS short | RANGE/CHOP | 127 | -0.01 | 0.03 | -0.12 |  |
| RS short | UP/CHOP | 181 | -0.02 | -0.04 | 0.04 |  |

## 3. Walk-forward routers (out of sample, 2024-11-20 onward, cell on if past avg R > 0.10, n >= 40)

| router | trades/mo | avgR | t | R/mo | quarters + |
|---|---|---|---|---|---|
| take everything | 85 | 0.02 | 1.1 | 1.7 | 5/8 |
| strategy+side | 0 |  |  | 0.0 | 0/0 |
| + market regime | 18 | 0.023 | 0.2 | 0.4 | 3/7 |
| + coin regime | 20 | 0.006 | -0.9 | 0.1 | 3/7 |
| + market + coin regime | 19 | -0.044 | -1.0 | -0.8 | 4/8 |
| + coin group | 8 | 0.053 | -0.1 | 0.4 | 3/8 |
| + single coin | 14 | -0.018 | -0.3 | -0.3 | 4/8 |
