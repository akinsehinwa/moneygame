# prop two accounts different rankings (2026-11-21)

## Per account (weekly R)

| pairing | account | avg R old | avg R 12m | Sharpe old | Sharpe 12m |
|---|---|---|---|---|---|
| COMBO + CROWDFADE | 100K: COMBO top 2+2 | 0.021 | 0.035 | 0.46 | 1.09 |
| COMBO + CROWDFADE | 50K: CROWDFADE top 2+2 (no overlap) | 0.03 | 0.046 | 1.13 | 1.78 |
| COMBO + MOM | 100K: COMBO top 2+2 | 0.021 | 0.035 | 0.46 | 1.09 |
| COMBO + MOM | 50K: MOM top 2+2 (no overlap) | -0.001 | -0.005 | -0.05 | -0.11 |

## Challenge simulation (by day 180)

| pairing | risk/position % | 100K pass by d180 % | 100K fail % | 50K pass % | 50K fail % | at least one % | both fail % | daily-limit fails % |
|---|---|---|---|---|---|---|---|---|
| COMBO + CROWDFADE | 1.25 | 1 | 12 | 5 | 0 | 6 | 0 | 0 / 0 |
| COMBO + CROWDFADE | 1.5 | 11 | 16 | 12 | 0 | 23 | 0 | 0 / 0 |
| COMBO + CROWDFADE | 1.7500000000000002 | 21 | 21 | 14 | 0 | 35 | 0 | 0 / 0 |
| COMBO + CROWDFADE | 2.0 | 23 | 43 | 25 | 0 | 45 | 0 | 0 / 0 |
| COMBO + MOM | 1.25 | 1 | 12 | 2 | 2 | 2 | 1 | 0 / 0 |
| COMBO + MOM | 1.5 | 11 | 16 | 9 | 21 | 20 | 9 | 0 / 0 |
| COMBO + MOM | 1.7500000000000002 | 21 | 21 | 12 | 30 | 32 | 11 | 0 / 0 |
| COMBO + MOM | 2.0 | 23 | 43 | 18 | 48 | 40 | 20 | 0 / 0 |
