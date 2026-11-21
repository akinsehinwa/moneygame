# cf1d standalone (2026-11-21)

## Rule

At each 4H close at 08/12/16/20 SGT (00/04/08/12 UTC): score = global long/short ratio, mean of the last 6 4h bars /
mean of the last 84 bars - 1. Long the lowest-scored coin, short the highest (one position per coin). Entry at the next
4H open; stop 3 x ATR(14, 4h), skipped if > 15% away; take-profit 2R; time exit 48h; 1h execution, stop first.
    python3 studies/cf4h.py          -> data/cf4h_candidates.pkl (ranked candidates per signal time, with trade marks)


## Results

| period | side | trades | avg R | win % | weekly Sharpe | sum R w/o best 3 coins |
|---|---|---|---|---|---|---|
| old | both | 742 | 0.033 | 47 | 1.02 | -2.5 |
| old | long | 379 | -0.005 | 45 | -0.13 | -20.3 |
| old | short | 363 | 0.072 | 48 | 0.96 | 1.8 |
| 12m | both | 355 | 0.037 | 50 | 1.03 | -1.6 |
| 12m | long | 171 | -0.019 | 43 | -0.26 | -11.9 |
| 12m | short | 184 | 0.089 | 57 | 1.51 | 2.1 |

## Verdict

fail
