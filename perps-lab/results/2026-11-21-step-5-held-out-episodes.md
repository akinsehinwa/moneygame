# step 5 held-out episodes (2026-11-21)

## Method

Trades from every strategy in data/trades.pkl (incl. SW50), signals since 2023-11-20, tagged with the last completed day's BTC state and the coin's atlas group. Cells switched on when avg R > 0.10 with >= 30 trades on 4 folds of episodes, scored on the 5th. Pass: avg R > 0.05 and >= 4/5 folds positive.

## BTC episodes

| BTC state | episodes | days | longest |
|---|---|---|---|
| STRONG_DOWN | 35 | 199 | 25 |
| DOWN | 112 | 324 | 17 |
| COIL | 57 | 202 | 17 |
| RANGE | 103 | 249 | 12 |
| UP | 119 | 308 | 10 |
| STRONG_UP | 55 | 331 | 39 |

## Routers (out of episode)

| router | trades | avg R | folds + | by fold | episodes + | pass |
|---|---|---|---|---|---|---|
| take everything | 70987 | -0.008 | 2/5 | -0.00 -0.03 -0.03 +0.01 +0.01 | 146/323 | fail |
| strategy only | 5410 | -0.025 | 2/5 | +0.02 -0.08 +0.03 -0.05 | 76/228 | fail |
| + BTC state | 15837 | -0.034 | 2/5 | -0.02 +0.02 -0.07 +0.06 -0.19 | 110/291 | fail |
| + coin group | 6842 | -0.009 | 2/5 | +0.17 -0.04 -0.08 +0.02 -0.02 | 116/298 | fail |
| + state + group | 16683 | -0.026 | 1/5 | -0.01 -0.01 -0.08 +0.07 -0.13 | 129/316 | fail |

## Each strategy: all trades vs routed by state + group (out of episode)

| strategy | all trades avg R | routed (out of episode) avg R | routed trades | routed folds + |
|---|---|---|---|---|
| BRK long | 0.096 | 0.004 | 1879 | 3/5 |
| BRK short | 0.018 | 0.232 | 1054 | 4/5 |
| BRKB long | 0.09 | 0.076 | 1397 | 4/5 |
| BRKB short | -0.07 | -0.436 | 188 | 0/5 |
| FUND long | -0.011 | 0.028 | 363 | 2/5 |
| FUND short | 0.011 | 0.065 | 368 | 4/5 |
| MR long | -0.027 | -0.119 | 991 | 2/5 |
| MR short | -0.123 | 0.036 | 481 | 3/5 |
| PB long | 0.019 | -0.083 | 573 | 1/5 |
| PB short | 0.009 | -0.136 | 500 | 2/5 |
| RS long | 0.01 | -0.168 | 269 | 1/5 |
| RS short | 0.029 | -0.213 | 399 | 0/5 |
| SQZ long | -0.036 | -0.302 | 376 | 0/5 |
| SQZ short | 0.117 | 0.028 | 763 | 2/5 |
| ST4 long | 0.051 | -0.144 | 1638 | 1/5 |
| ST4 short | 0.068 | 0.015 | 1883 | 4/5 |
| STD long | 0.08 | 0.19 | 566 | 5/5 |
| STD short | 0.006 | 0.103 | 440 | 4/5 |
| SW50 long | -0.035 | -0.182 | 519 | 1/5 |
| SW50 short | 0.042 | 0.039 | 898 | 4/5 |
| SWP long | -0.088 | -0.243 | 814 | 3/5 |
| SWP short | -0.058 | 0.007 | 324 | 3/5 |

## SW50 avg R by group x BTC state (all data)

| group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| G0 | -0.25 | -0.19 | -0.02 | 0.27 | 0.16 | 0.05 |
| G1 | 0.0 | -0.21 | 0.07 | 0.04 | 0.21 | 0.05 |
| G2 | 0.01 | -0.24 | -0.36 | 0.14 | -0.1 | 0.1 |
| G3 | -0.18 | -0.23 | 0.07 | 0.06 | 0.58 | 0.02 |
| G4 | -0.62 | -0.16 | -0.25 | -0.23 | 0.26 | -0.61 |

## SW50 trade counts

| group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| G0 | 169 | 262 | 142 | 140 | 247 | 266 |
| G1 | 267 | 502 | 217 | 252 | 433 | 424 |
| G2 | 6 | 12 | 10 | 10 | 10 | 13 |
| G3 | 79 | 135 | 58 | 65 | 105 | 106 |
| G4 | 19 | 40 | 21 | 21 | 37 | 23 |

## SW50 avg R by direction x BTC state

| direction | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| long | -0.49 | -0.31 | -0.04 | 0.05 | 0.11 | 0.07 |
| short | -0.01 | -0.14 | 0.05 | 0.13 | 0.42 | -0.11 |

## Cells a live router would switch on today (all episodes)

| strategy | BTC state | coin group | trades | avg R |
|---|---|---|---|---|
| SQZ short | COIL | G0 | 64 | 0.42 |
| ST4 long | COIL | G3 | 129 | 0.37 |
| BRK long | COIL | G3 | 68 | 0.33 |
| RS long | COIL | G3 | 32 | 0.31 |
| FUND short | COIL | G2 | 46 | 0.28 |
| ST4 long | COIL | G0 | 249 | 0.28 |
| STD long | COIL | G3 | 36 | 0.25 |
| SQZ short | COIL | G3 | 48 | 0.25 |
| RS long | COIL | G0 | 51 | 0.19 |
| PB long | COIL | G0 | 60 | 0.15 |
| PB short | COIL | G3 | 65 | 0.13 |
| SW50 long | COIL | G1 | 85 | 0.12 |
| SW50 short | COIL | G3 | 30 | 0.11 |
| SW50 short | COIL | G0 | 88 | 0.11 |
| FUND long | DOWN | G2 | 36 | 0.49 |
| ST4 long | DOWN | G4 | 38 | 0.27 |
| SQZ long | DOWN | G1 | 202 | 0.21 |
| SWP short | DOWN | G4 | 48 | 0.2 |
| SQZ short | DOWN | G0 | 114 | 0.19 |
| SWP long | DOWN | G4 | 61 | 0.18 |
| ST4 short | DOWN | G3 | 150 | 0.18 |
| SWP short | DOWN | G3 | 187 | 0.15 |
| FUND long | DOWN | G1 | 292 | 0.14 |
| SQZ short | DOWN | G3 | 64 | 0.14 |
| FUND long | DOWN | G4 | 32 | 0.14 |
| ST4 short | DOWN | G0 | 288 | 0.14 |
| FUND short | RANGE | G0 | 52 | 0.63 |
| SQZ long | RANGE | G3 | 38 | 0.61 |
| SW50 short | RANGE | G0 | 77 | 0.31 |
| BRKB short | RANGE | G0 | 92 | 0.26 |
| FUND short | RANGE | G1 | 121 | 0.23 |
| SW50 long | RANGE | G0 | 63 | 0.22 |
| MR long | RANGE | G0 | 196 | 0.22 |
| BRKB short | RANGE | G1 | 163 | 0.2 |
| FUND short | RANGE | G3 | 33 | 0.19 |
| MR long | RANGE | G3 | 78 | 0.19 |
| MR long | RANGE | G1 | 318 | 0.18 |
| SW50 short | RANGE | G3 | 40 | 0.17 |
| PB long | RANGE | G1 | 111 | 0.16 |
| SQZ long | RANGE | G1 | 135 | 0.16 |
| BRK short | RANGE | G3 | 74 | 0.15 |
| RS long | RANGE | G1 | 100 | 0.14 |
| ST4 short | RANGE | G0 | 193 | 0.13 |
| BRKB short | RANGE | G3 | 53 | 0.12 |
| PB short | RANGE | G0 | 155 | 0.12 |
| SQZ short | RANGE | G0 | 73 | 0.11 |
| STD short | RANGE | G3 | 33 | 0.11 |
| MR short | RANGE | G0 | 180 | 0.1 |
| MR short | STRONG_DOWN | G0 | 99 | 0.31 |
| MR short | STRONG_DOWN | G3 | 61 | 0.31 |
| MR short | STRONG_DOWN | G1 | 173 | 0.18 |
| STD short | STRONG_DOWN | G1 | 56 | 0.15 |
| FUND long | STRONG_DOWN | G4 | 42 | 0.15 |
| SW50 short | STRONG_DOWN | G1 | 201 | 0.13 |
| SWP short | STRONG_DOWN | G3 | 94 | 0.13 |
| ST4 long | STRONG_UP | G3 | 86 | 0.88 |
| PB short | STRONG_UP | G0 | 40 | 0.7 |
| STD long | STRONG_UP | G3 | 48 | 0.67 |
| SQZ short | STRONG_UP | G1 | 130 | 0.64 |
| PB short | STRONG_UP | G1 | 87 | 0.5 |
| SQZ short | STRONG_UP | G0 | 69 | 0.43 |
| STD long | STRONG_UP | G0 | 97 | 0.35 |
| RS short | STRONG_UP | G3 | 31 | 0.34 |
| FUND short | STRONG_UP | G2 | 49 | 0.28 |
| BRKB long | STRONG_UP | G3 | 174 | 0.23 |
| BRK long | STRONG_UP | G0 | 392 | 0.22 |
| BRKB long | STRONG_UP | G0 | 388 | 0.21 |
| STD long | STRONG_UP | G1 | 203 | 0.2 |
| BRK long | STRONG_UP | G3 | 180 | 0.2 |
| ST4 long | STRONG_UP | G0 | 200 | 0.17 |
| SQZ short | STRONG_UP | G3 | 32 | 0.14 |
| RS long | STRONG_UP | G0 | 57 | 0.14 |
| BRK long | STRONG_UP | G4 | 40 | 0.14 |
| BRKB long | STRONG_UP | G4 | 40 | 0.14 |
| SW50 long | STRONG_UP | G3 | 83 | 0.12 |
| ST4 short | STRONG_UP | G3 | 127 | 0.1 |
| SW50 short | UP | G3 | 47 | 0.72 |
| ST4 long | UP | G4 | 32 | 0.54 |
| BRK short | UP | G1 | 412 | 0.48 |
| BRK short | UP | G3 | 125 | 0.48 |
| SW50 long | UP | G3 | 58 | 0.46 |
| STD long | UP | G3 | 58 | 0.44 |
| SW50 short | UP | G1 | 172 | 0.42 |
| BRK short | UP | G0 | 230 | 0.39 |
| FUND short | UP | G0 | 50 | 0.36 |
| SW50 short | UP | G0 | 103 | 0.3 |
| BRKB long | UP | G3 | 136 | 0.28 |
| ST4 long | UP | G1 | 432 | 0.26 |
| STD short | UP | G0 | 119 | 0.23 |
| ST4 short | UP | G3 | 178 | 0.23 |
| ST4 long | UP | G3 | 99 | 0.23 |
| PB short | UP | G1 | 165 | 0.22 |
| BRKB long | UP | G0 | 285 | 0.22 |
| BRK long | UP | G3 | 147 | 0.21 |
| PB short | UP | G3 | 37 | 0.19 |
| ST4 short | UP | G1 | 633 | 0.18 |
| FUND short | UP | G1 | 163 | 0.18 |
| MR short | UP | G4 | 31 | 0.18 |
| STD short | UP | G3 | 59 | 0.18 |
| PB long | UP | G3 | 72 | 0.17 |
| BRKB long | UP | G1 | 481 | 0.16 |
| BRK long | UP | G0 | 310 | 0.16 |
| STD long | UP | G1 | 202 | 0.16 |
| BRK long | UP | G1 | 517 | 0.15 |
| STD long | UP | G0 | 108 | 0.15 |
| ST4 short | UP | G0 | 340 | 0.15 |
| STD short | UP | G1 | 210 | 0.15 |
| ST4 long | UP | G0 | 233 | 0.14 |
| RS long | UP | G3 | 48 | 0.13 |
| SQZ short | UP | G1 | 135 | 0.12 |
| SQZ long | UP | G1 | 153 | 0.11 |
