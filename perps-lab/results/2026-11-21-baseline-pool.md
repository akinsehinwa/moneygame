# baseline pool (2026-11-21)

Trades 54312, coins 72, signals 2023-11-20 to 2026-11-19. R per trade at 1R risk, costs included. Old = before 2025-11-20, 12m = after. t = weekly-clustered t-stat (|t| < 2 is not significant).

## 1. Scorecard

| strategy | n old | avgR old | n 12m | avgR 12m | win% 12m | t 12m | holds |
|---|---|---|---|---|---|---|---|
| BRK long | 2563 | 0.094 | 1259 | 0.086 | 42 | -2.0 | yes |
| BRK short | 2031 | 0.08 | 1497 | -0.059 | 43 | -2.1 |  |
| MR long | 2487 | -0.033 | 1507 | -0.014 | 50 | 1.8 |  |
| MR short | 2896 | -0.178 | 1779 | -0.029 | 48 | 2.3 |  |
| PB long | 1171 | 0.009 | 571 | 0.041 | 43 | 0.7 | yes |
| PB short | 1610 | -0.063 | 1182 | 0.105 | 48 | 0.8 |  |
| SQZ long | 981 | 0.06 | 560 | -0.201 | 29 | -1.5 |  |
| SQZ short | 973 | 0.312 | 653 | -0.194 | 32 | -0.1 |  |
| ST4 long | 3021 | 0.086 | 1769 | -0.027 | 29 | -0.9 |  |
| ST4 short | 3041 | 0.125 | 1766 | -0.029 | 39 | -1.2 |  |
| STD long | 914 | 0.053 | 470 | 0.132 | 44 | -1.1 | yes |
| STD short | 961 | -0.007 | 481 | 0.033 | 60 | 0.4 |  |
| SWP long | 6333 | -0.104 | 3514 | -0.062 | 44 | -0.3 |  |
| SWP short | 5672 | -0.067 | 2650 | -0.029 | 46 | 2.3 |  |

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
| MR long | DOWN/CHOP | 1479 | -0.09 | -0.14 | -0.01 |  |
| MR long | DOWN/TREND | 1152 | 0.09 | 0.23 | -0.04 |  |
| MR long | RANGE/CHOP | 397 | 0.03 | 0.03 | 0.03 |  |
| MR long | RANGE/TREND | 60 | 0.17 | 0.17 | 0.17 | yes |
| MR long | UP/CHOP | 693 | -0.09 | -0.13 | 0.01 |  |
| MR long | UP/TREND | 213 | -0.13 | -0.19 | 0.06 |  |
| MR short | DOWN/CHOP | 1675 | -0.13 | -0.26 | 0.04 |  |
| MR short | DOWN/TREND | 434 | -0.0 | 0.0 | -0.01 |  |
| MR short | RANGE/CHOP | 554 | -0.31 | -0.31 | -0.32 |  |
| MR short | RANGE/TREND | 108 | -0.03 | -0.05 | -0.01 |  |
| MR short | UP/CHOP | 1037 | -0.04 | -0.05 | -0.03 |  |
| MR short | UP/TREND | 867 | -0.15 | -0.21 | 0.0 |  |
| PB long | DOWN/CHOP | 143 | -0.05 | -0.18 | 0.05 |  |
| PB long | RANGE/CHOP | 103 | 0.04 | -0.13 | 0.35 |  |
| PB long | UP/CHOP | 1013 | 0.05 | 0.05 | 0.06 | yes |
| PB long | UP/TREND | 454 | -0.02 | 0.01 | -0.1 |  |
| PB short | DOWN/CHOP | 1741 | -0.01 | -0.08 | 0.08 |  |
| PB short | DOWN/TREND | 835 | 0.03 | -0.07 | 0.16 |  |
| PB short | RANGE/CHOP | 109 | -0.03 | -0.02 | -0.06 |  |
| PB short | UP/CHOP | 95 | 0.16 | 0.12 | 0.27 | yes |
| SQZ long | DOWN/CHOP | 717 | 0.14 | 0.36 | -0.18 |  |
| SQZ long | DOWN/TREND | 228 | -0.3 | -0.3 | -0.3 |  |
| SQZ long | RANGE/CHOP | 116 | -0.2 | -0.25 | -0.06 |  |
| SQZ long | UP/CHOP | 357 | -0.15 | -0.11 | -0.28 |  |
| SQZ long | UP/TREND | 117 | -0.06 | -0.11 | 0.06 |  |
| SQZ short | DOWN/CHOP | 653 | -0.03 | 0.23 | -0.35 |  |
| SQZ short | DOWN/TREND | 293 | -0.05 | -0.03 | -0.07 |  |
| SQZ short | RANGE/CHOP | 148 | 0.23 | 0.45 | -0.17 |  |
| SQZ short | UP/CHOP | 405 | 0.28 | 0.41 | -0.14 |  |
| SQZ short | UP/TREND | 116 | 0.51 | 0.61 | 0.28 | yes |
| ST4 long | DOWN/CHOP | 2123 | 0.13 | 0.25 | -0.05 |  |
| ST4 long | DOWN/TREND | 986 | -0.12 | -0.14 | -0.08 |  |
| ST4 long | RANGE/CHOP | 354 | 0.04 | 0.04 | 0.05 |  |
| ST4 long | UP/CHOP | 1075 | 0.03 | -0.01 | 0.14 |  |
| ST4 long | UP/TREND | 236 | 0.05 | 0.14 | -0.21 |  |
| ST4 short | DOWN/CHOP | 1795 | 0.16 | 0.31 | -0.03 |  |
| ST4 short | DOWN/TREND | 574 | 0.04 | 0.11 | -0.04 |  |
| ST4 short | RANGE/CHOP | 396 | 0.14 | 0.19 | 0.03 |  |
| ST4 short | RANGE/TREND | 47 | 0.33 | 0.64 | -0.17 |  |
| ST4 short | UP/CHOP | 1407 | -0.01 | 0.0 | -0.04 |  |
| ST4 short | UP/TREND | 588 | -0.06 | -0.09 | 0.01 |  |
| STD long | DOWN/CHOP | 475 | -0.02 | 0.0 | -0.04 |  |
| STD long | RANGE/CHOP | 496 | 0.16 | 0.13 | 0.25 | yes |
| STD long | RANGE/TREND | 46 | 0.22 | 0.43 | -0.03 |  |
| STD long | UP/CHOP | 267 | 0.03 | -0.06 | 0.31 |  |
| STD long | UP/TREND | 81 | 0.3 | 0.13 | 0.54 | yes |
| STD short | DOWN/CHOP | 424 | 0.17 | 0.19 | 0.13 | yes |
| STD short | DOWN/TREND | 54 | 0.0 | -0.02 | 0.06 |  |
| STD short | RANGE/CHOP | 520 | -0.01 | -0.02 | 0.02 |  |
| STD short | UP/CHOP | 382 | -0.14 | -0.19 | -0.04 |  |
| SWP long | DOWN/CHOP | 3818 | -0.1 | -0.17 | 0.0 |  |
| SWP long | DOWN/TREND | 2302 | 0.0 | 0.05 | -0.05 |  |
| SWP long | RANGE/CHOP | 1067 | -0.21 | -0.2 | -0.25 |  |
| SWP long | RANGE/TREND | 123 | -0.15 | -0.01 | -0.37 |  |
| SWP long | UP/CHOP | 1960 | -0.1 | -0.1 | -0.11 |  |
| SWP long | UP/TREND | 577 | -0.08 | -0.06 | -0.13 |  |
| SWP short | DOWN/CHOP | 2905 | -0.09 | -0.14 | 0.0 |  |
| SWP short | DOWN/TREND | 767 | 0.07 | 0.11 | 0.02 |  |
| SWP short | RANGE/CHOP | 1107 | -0.12 | -0.09 | -0.2 |  |
| SWP short | RANGE/TREND | 205 | -0.19 | -0.22 | -0.13 |  |
| SWP short | UP/CHOP | 1880 | -0.01 | -0.02 | 0.03 |  |
| SWP short | UP/TREND | 1458 | -0.04 | -0.03 | -0.07 |  |

## 3. Walk-forward routers (out of sample, 2024-11-20 onward, cell on if past avg R > 0.10, n >= 40)

| router | trades/mo | avgR | t | R/mo | quarters + |
|---|---|---|---|---|---|
| take everything | 1581 | -0.02 | -1.8 | -32.0 | 3/8 |
| strategy+side | 222 | -0.014 | -0.8 | -3.0 | 3/8 |
| + market regime | 422 | 0.054 | -0.1 | 22.8 | 3/8 |
| + coin regime | 399 | 0.065 | 0.3 | 25.8 | 6/8 |
| + market + coin regime | 362 | 0.053 | 0.5 | 19.0 | 4/8 |
| + coin group | 368 | 0.039 | 0.1 | 14.3 | 5/8 |
| + single coin | 316 | -0.019 | -1.0 | -6.0 | 4/8 |
