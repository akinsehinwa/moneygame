# Q1 BRK with BTC direction (2026-11-21)

Trades 12001, coins 72, signals 2023-11-20 to 2026-11-18. R per trade at 1R risk, costs included. Old = before 2025-11-20, 12m = after. t = weekly-clustered t-stat (|t| < 2 is not significant).

## 1. Scorecard

| strategy | n old | avgR old | n 12m | avgR 12m | win% 12m | t 12m | R/mo 12m | holds |
|---|---|---|---|---|---|---|---|---|
| BRK long | 2563 | 0.094 | 1259 | 0.086 | 42 | -2.0 | 9.0 | yes |
| BRK short | 2031 | 0.08 | 1497 | -0.059 | 43 | -2.1 | -7.4 |  |
| BRKB long | 1932 | 0.056 | 755 | 0.144 | 45 | -1.3 | 9.0 | yes |
| BRKB short | 970 | -0.086 | 994 | -0.041 | 43 | -1.1 | -3.4 |  |

## 2. By coin regime

| strategy | coin regime | n | avgR | old | 12m | holds |
|---|---|---|---|---|---|---|
| BRK long | DOWN/CHOP | 1153 | 0.16 | 0.21 | 0.07 | yes |
| BRK long | DOWN/TREND | 180 | -0.05 | -0.13 | 0.02 |  |
| BRK long | RANGE/CHOP | 578 | 0.21 | 0.14 | 0.34 | yes |
| BRK long | RANGE/TREND | 130 | 0.2 | 0.36 | 0.02 |  |
| BRK long | UP/CHOP | 865 | -0.05 | -0.08 | 0.02 |  |
| BRK long | UP/TREND | 916 | 0.08 | 0.11 | 0.02 |  |
| BRK short | DOWN/CHOP | 1473 | 0.12 | 0.24 | -0.03 |  |
| BRK short | DOWN/TREND | 1045 | -0.04 | -0.06 | -0.01 |  |
| BRK short | RANGE/CHOP | 440 | -0.06 | -0.04 | -0.11 |  |
| BRK short | RANGE/TREND | 46 | -0.3 | -0.1 | -0.72 |  |
| BRK short | UP/CHOP | 462 | -0.03 | 0.05 | -0.2 |  |
| BRK short | UP/TREND | 62 | -0.19 | -0.13 | -0.28 |  |
| BRKB long | DOWN/CHOP | 478 | 0.16 | 0.14 | 0.19 | yes |
| BRKB long | DOWN/TREND | 48 | -0.47 | -0.49 | -0.45 |  |
| BRKB long | RANGE/CHOP | 433 | 0.26 | 0.16 | 0.51 | yes |
| BRKB long | RANGE/TREND | 115 | 0.24 | 0.42 | 0.03 |  |
| BRKB long | UP/CHOP | 744 | -0.07 | -0.12 | 0.07 |  |
| BRKB long | UP/TREND | 869 | 0.08 | 0.1 | 0.04 |  |
| BRKB short | DOWN/CHOP | 957 | -0.03 | -0.0 | -0.06 |  |
| BRKB short | DOWN/TREND | 834 | -0.06 | -0.1 | -0.03 |  |
| BRKB short | RANGE/CHOP | 104 | -0.28 | -0.41 | -0.05 |  |
| BRKB short | UP/CHOP | 56 | -0.31 | -0.46 | 0.03 |  |

## 3. Walk-forward routers (out of sample, 2024-11-20 onward, cell on if past avg R > 0.10, n >= 40)

| router | trades/mo | avgR | t | R/mo | quarters + |
|---|---|---|---|---|---|
| take everything | 346 | 0.023 | -2.3 | 8.0 | 5/8 |
| strategy+side | 69 | -0.059 | -2.3 | -4.1 | 2/4 |
| + market regime | 127 | -0.023 | -2.6 | -2.9 | 2/8 |
| + coin regime | 144 | 0.062 | -0.6 | 9.0 | 4/8 |
| + market + coin regime | 96 | 0.041 | -0.9 | 4.0 | 4/8 |
| + coin group | 101 | 0.056 | -0.5 | 5.7 | 3/8 |
| + single coin | 118 | 0.02 | -2.4 | 2.4 | 5/8 |
