# cf4h standalone (2026-11-21)

## Rule

At each 4H close at 08/12/16/20 SGT (00/04/08/12 UTC): score = global long/short ratio, mean of the last 6 4h bars /
mean of the last 84 bars - 1. Long the lowest-scored coin, short the highest (one position per coin). Entry at the next
4H open; stop 3 x ATR(14, 4h), skipped if > 15% away; take-profit 2R; time exit 48h; 1h execution, stop first.
    python3 studies/cf4h.py          -> data/cf4h_candidates.pkl (ranked candidates per signal time, with trade marks)


## Results

| period | side | trades | avg R | win % | weekly Sharpe | sum R w/o best 3 coins |
|---|---|---|---|---|---|---|
| old | both | 1433 | 0.015 | 49 | 0.27 | -6.2 |
| old | long | 739 | -0.003 | 47 | -0.15 | -16.6 |
| old | short | 694 | 0.033 | 51 | 1.19 | 1.6 |
| 12m | both | 662 | -0.064 | 45 | -3.2 | -55.9 |
| 12m | long | 314 | -0.088 | 41 | -1.57 | -38.3 |
| 12m | short | 348 | -0.043 | 48 | -0.62 | -24.0 |

## Verdict

fail
