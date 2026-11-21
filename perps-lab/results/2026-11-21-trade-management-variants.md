# trade management variants (2026-11-21)

## Variants

V0 hold 7 days; V1 cut at <= -0.5R at Thu/Sun check; V2 breakeven stop at >= +1R at check; V3 both; V4 majors in profit held to day 10; V5 any coin in profit to day 10 (not allowed, reference).

## Results (avg R per position, weekly Sharpe)

| account | variant | avg R old | avg R 12m | Sharpe old | Sharpe 12m |
|---|---|---|---|---|---|
| 100K | V0 | 0.02 | 0.038 | 0.45 | 1.17 |
| 100K | V1 | 0.02 | 0.041 | 0.45 | 1.28 |
| 100K | V2 | 0.02 | 0.038 | 0.45 | 1.17 |
| 100K | V3 | 0.02 | 0.041 | 0.45 | 1.28 |
| 100K | V4 | 0.021 | 0.022 | 0.43 | 0.63 |
| 100K | V5 | 0.017 | 0.016 | 0.33 | 0.4 |
| 50K | V0 | 0.031 | 0.044 | 1.14 | 1.71 |
| 50K | V1 | 0.029 | 0.042 | 1.05 | 1.61 |
| 50K | V2 | 0.031 | 0.043 | 1.14 | 1.67 |
| 50K | V3 | 0.029 | 0.042 | 1.05 | 1.57 |
| 50K | V4 | 0.041 | 0.069 | 1.35 | 2.13 |
| 50K | V5 | 0.035 | 0.021 | 0.98 | 0.64 |

## How often majors are picked

| account | positions | major positions |
|---|---|---|
| 100K | 616 | 143 |
| 50K | 616 | 171 |
