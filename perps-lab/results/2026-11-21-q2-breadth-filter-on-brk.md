# Q2 breadth filter on BRK (2026-11-21)

## Breadth distribution (signals per 4h close, same side)

| count | mean | std | min | 50% | 75% | 90% | max |
|---|---|---|---|---|---|---|---|
| 7350.0 | 15.6 | 15.4 | 1.0 | 10.0 | 25.0 | 38.0 | 62.0 |

## Kept vs dropped trades

| threshold | strategy | group | n old | avgR old | R/mo old | n 12m | avgR 12m | R/mo 12m |
|---|---|---|---|---|---|---|---|---|
| 2 | BRK long | kept (breadth >= 2) | 2014 | 0.101 | 8.5 | 949 | 0.121 | 9.6 |
| 2 | BRK long | dropped | 549 | 0.071 | 1.6 | 310 | -0.022 | -0.6 |
| 2 | BRK short | kept (breadth >= 2) | 1886 | 0.076 | 6.0 | 1350 | -0.069 | -7.8 |
| 2 | BRK short | dropped | 145 | 0.137 | 0.8 | 147 | 0.031 | 0.4 |
| 3 | BRK long | kept (breadth >= 3) | 1662 | 0.097 | 6.8 | 770 | 0.183 | 11.8 |
| 3 | BRK long | dropped | 901 | 0.089 | 3.3 | 489 | -0.067 | -2.7 |
| 3 | BRK short | kept (breadth >= 3) | 1821 | 0.068 | 5.2 | 1274 | -0.078 | -8.3 |
| 3 | BRK short | dropped | 210 | 0.184 | 1.6 | 223 | 0.047 | 0.9 |
| 5 | BRK long | kept (breadth >= 5) | 1218 | 0.119 | 6.0 | 586 | 0.211 | 10.3 |
| 5 | BRK long | dropped | 1345 | 0.072 | 4.0 | 673 | -0.023 | -1.3 |
| 5 | BRK short | kept (breadth >= 5) | 1711 | 0.058 | 4.1 | 1199 | -0.085 | -8.5 |
| 5 | BRK short | dropped | 320 | 0.2 | 2.7 | 298 | 0.045 | 1.1 |
