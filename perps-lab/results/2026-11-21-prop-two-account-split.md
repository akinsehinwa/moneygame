# prop two-account split (2026-11-21)

## Setup

100K gets long/short ranks 1 and 3, 50K ranks 2 and 4 of the weekly COMBO ranking (no coin in both). Coins whose stop is > 15% away are skipped (5x isolated). Target 3R, weekly exit. Every weekly start since 2023-11-20 with 180+ days after it.

## Per account (weekly R)

| stop | account | avg R old | avg R 12m | Sharpe old | Sharpe 12m |
|---|---|---|---|---|---|
| 1.5 ATR | 100K (ranks 1+3) | -0.008 | 0.147 | -0.13 | 2.52 |
| 1.5 ATR | 50K (ranks 2+4) | -0.027 | -0.014 | -0.49 | -0.26 |
| 2.0 ATR | 100K (ranks 1+3) | 0.043 | 0.046 | 0.88 | 0.97 |
| 2.0 ATR | 50K (ranks 2+4) | 0.02 | 0.035 | 0.44 | 0.82 |

## Challenge simulation

| stop | risk/position % | starts | 100K passed both by d180 % | 100K failed % | 100K median days | 50K passed both % | 50K failed % | 50K median days | at least one passed % | daily-limit fails 100K / 50K % |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.5 ATR | 0.75 | 124 | 16 | 17 | 151.45833333333331 | 0 | 17 |  | 16 | 0 / 0 |
| 1.5 ATR | 1.0 | 124 | 32 | 25 | 134.58333333333331 | 1 | 28 | 122.20833333333333 | 32 | 0 / 0 |
| 1.5 ATR | 1.25 | 124 | 41 | 43 | 117.66666666666667 | 2 | 48 | 107.58333333333333 | 41 | 0 / 0 |
| 1.5 ATR | 1.5 | 124 | 48 | 42 | 92.33333333333333 | 7 | 58 | 121.25 | 48 | 2 / 0 |
| 1.5 ATR | 1.7500000000000002 | 124 | 47 | 50 | 75.39583333333334 | 12 | 65 | 114.79166666666667 | 51 | 6 / 0 |
| 2.0 ATR | 0.75 | 102 | 0 | 0 |  | 0 | 0 |  | 0 | 0 / 0 |
| 2.0 ATR | 1.0 | 102 | 13 | 1 | 136.45833333333334 | 6 | 3 | 126.0 | 18 | 0 / 0 |
| 2.0 ATR | 1.25 | 102 | 18 | 12 | 130.22916666666666 | 11 | 12 | 108.79166666666667 | 25 | 0 / 0 |
| 2.0 ATR | 1.5 | 102 | 31 | 26 | 103.79166666666666 | 19 | 30 | 107.58333333333333 | 39 | 12 / 0 |
| 2.0 ATR | 1.7500000000000002 | 102 | 40 | 36 | 95.875 | 32 | 38 | 79.70833333333333 | 53 | 12 / 2 |
