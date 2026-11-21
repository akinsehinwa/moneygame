# data snooping check spa stepm (2026-11-21)

## Method

28 basket books (every one tried, incl. rejected), daily net returns, benchmark = cash. SPA asks whether the best is better than cash after accounting for all 28; StepM lists which beat cash at 5%. Stationary bootstrap, 10,000 reps, 10-day blocks.

## Results

| window | days | best book | its Sharpe | single-test p (as if only one tried) | SPA p (lower / consistent / upper) | StepM: books that beat cash |
|---|---|---|---|---|---|---|
| whole sample | 1097 | MOMCARRY | 1.3 | 0.0123 | 0.237 / 0.329 / 0.361 | none |
| last 12 months | 366 | PAIRS | 2.62 | 0.0043 | 0.190 / 0.324 / 0.333 | none |

## Sharpe of every book

| book | whole sample | last 12 months |
|---|---|---|
| MOMCARRY | 1.3 | 0.68 |
| CROWDFADE | 1.28 | 1.89 |
| TRENDLO | 1.04 | 1.48 |
| MOM | 0.93 | 1.15 |
| CARRY | 0.9 | -0.21 |
| SECTOR | 0.89 | 1.09 |
| TSMOM | 0.72 | 0.59 |
| DISPMOM | 0.68 | 1.65 |
| CROWDTOP | 0.61 | 1.05 |
| DUALMOM | 0.58 | -0.29 |
| RESMOM | 0.54 | 1.36 |
| MA3 | 0.48 | 1.0 |
| MA2 | 0.43 | 0.77 |
| VOLTARGET | 0.39 | -0.36 |
| FOMCDAY | 0.37 | -1.3 |
| RSQ | 0.18 | 0.35 |
| DISTRESS | 0.12 | -0.03 |
| ECO | 0.07 | 1.62 |
| OIFADE+CROWDFADE | 0.02 | 0.77 |
| LOWVOL | -0.37 | -0.42 |
| NEWLIST | -0.45 | 0.39 |
| PAIRS | -0.5 | 2.62 |
| CHANFADE | -0.59 | -0.83 |
| DOLLARCARRY | -0.61 | -0.59 |
| SKEW | -0.96 | -1.24 |
| OIFADE | -1.22 | -0.97 |
| CONTRA | -1.6 | -0.64 |
| PIVOT | -3.54 | -4.76 |
