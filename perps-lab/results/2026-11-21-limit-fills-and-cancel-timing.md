# limit fills and cancel timing (2026-11-21)

## Setup

Limit at Monday's open moved 0.5% in the trade's favour; stop / TP distances as tested; exit Monday 08:00 SGT.

## Cancel rules

| account | period | rule | tickets | fill rate % | avg R of filled | R per ticket issued |
|---|---|---|---|---|---|---|
| 100K | old | cancel after 4h | 408 | 77 | 0.017 | 0.013 |
| 100K | old | cancel after 24h (Tue 08:00) | 408 | 89 | 0.016 | 0.014 |
| 100K | old | cancel after 72h (Thu 08:00) | 408 | 94 | 0.015 | 0.014 |
| 100K | old | never cancel (until Monday) | 408 | 95 | 0.017 | 0.016 |
| 100K | 12m | cancel after 4h | 204 | 75 | -0.014 | -0.01 |
| 100K | 12m | cancel after 24h (Tue 08:00) | 204 | 89 | 0.01 | 0.009 |
| 100K | 12m | cancel after 72h (Thu 08:00) | 204 | 96 | 0.019 | 0.018 |
| 100K | 12m | never cancel (until Monday) | 204 | 96 | 0.019 | 0.018 |
| 50K | old | cancel after 4h | 408 | 77 | 0.051 | 0.04 |
| 50K | old | cancel after 24h (Tue 08:00) | 408 | 91 | 0.043 | 0.039 |
| 50K | old | cancel after 72h (Thu 08:00) | 408 | 94 | 0.038 | 0.036 |
| 50K | old | never cancel (until Monday) | 408 | 97 | 0.034 | 0.033 |
| 50K | 12m | cancel after 4h | 204 | 73 | -0.01 | -0.007 |
| 50K | 12m | cancel after 24h (Tue 08:00) | 204 | 86 | 0.038 | 0.033 |
| 50K | 12m | cancel after 72h (Thu 08:00) | 204 | 92 | 0.049 | 0.045 |
| 50K | 12m | never cancel (until Monday) | 204 | 95 | 0.038 | 0.036 |

## Avg R by how long the fill took

| account | filled after | trades | avg R |
|---|---|---|---|
| 100K | first hour | 357 | 0.031 |
| 100K | 1-4h | 119 | -0.069 |
| 100K | 4-24h | 73 | 0.08 |
| 100K | 24-72h | 28 | 0.025 |
| 100K | 72h+ | 5 | 0.184 |
| 50K | first hour | 351 | 0.036 |
| 50K | 1-4h | 121 | -0.003 |
| 50K | 4-24h | 77 | 0.137 |
| 50K | 24-72h | 23 | 0.036 |
| 50K | 72h+ | 16 | -0.172 |
