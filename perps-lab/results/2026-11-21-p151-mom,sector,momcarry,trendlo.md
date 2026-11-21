# p151 mom,sector,momcarry,trendlo (2026-11-21)

## Rules

Net of 0.06%/side costs and funding. Pass = Sharpe >= 0.5 in both periods (long-only books must also beat the equal-weight basket).

## Results

| strategy | ann % old | Sharpe old | maxDD % old | funding %/yr old | costs %/yr old | ann % 12m | Sharpe 12m | maxDD % 12m | funding %/yr 12m | costs %/yr 12m | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BENCH_EW | 38.6 | 0.47 | -70.3 | -7.6 | -0.1 | -31.6 | -0.49 | -45.6 | 3.4 | -0.0 |  |
| BENCH_BTC | 46.9 | 0.98 | -29.4 | -9.3 | 0.0 | -32.3 | -0.73 | -39.7 | -3.1 | 0.0 |  |
| MOM | 23.3 | 0.83 | -24.8 | 1.3 | -2.3 | 33.3 | 1.22 | -16.7 | 3.6 | -2.2 | PASS |
| SECTOR | 19.3 | 0.86 | -26.1 | 0.5 | -2.1 | 15.1 | 1.1 | -10.4 | 3.6 | -2.0 | PASS |
| MOMCARRY | 30.2 | 1.61 | -20.0 | 6.6 | -2.5 | 13.9 | 0.73 | -14.4 | 9.7 | -2.2 | PASS |
| TRENDLO | 49.3 | 0.75 | -57.8 | -8.4 | -1.5 | 157.2 | 1.56 | -59.5 | 54.9 | -1.7 | PASS |
