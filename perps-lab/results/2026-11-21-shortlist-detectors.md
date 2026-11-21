# shortlist detectors (2026-11-21)

## (1) Next-24h range (median, in 4H ATR units) for flagged vs other coins

| coin flagged | 12m | old |
|---|---|---|
| no | 2.24 | 2.28 |
| yes | 2.2 | 2.24 |

## By setup

| det | median next-24h range (ATR) |
|---|---|
| COIL | 2.44 |
| DISP | 2.9 |
| SWING50 | 2.07 |

## (2) Levels: fill rate and avg R after the fill

| setup | side | flags | fill % old | avg R old | trades old | fill % 12m | avg R 12m | trades 12m | useful |
|---|---|---|---|---|---|---|---|---|---|
| COIL | short | 4372 | 100 | 0.175 | 2586 | 100 | -0.003 | 1786 |  |
| COIL | long | 3857 | 100 | 0.045 | 2547 | 100 | -0.275 | 1310 |  |
| DISP | short | 653 | 50 | -0.282 | 206 | 48 | 0.007 | 115 |  |
| DISP | long | 935 | 52 | 0.131 | 295 | 61 | -0.083 | 224 |  |
| SWING50 | short | 9844 | 46 | 0.018 | 3025 | 40 | 0.091 | 1304 | yes |
| SWING50 | long | 7504 | 51 | 0.033 | 2661 | 56 | -0.031 | 1291 |  |

## By BTC state (context only, not used to pick)

| setup | side | BTC state | trades | avg R |
|---|---|---|---|---|
| COIL | short | COIL | 544 | 0.248 |
| COIL | short | DOWN | 1092 | -0.15 |
| COIL | short | RANGE | 765 | -0.012 |
| COIL | short | STRONG_DOWN | 608 | 0.246 |
| COIL | short | STRONG_UP | 694 | 0.473 |
| COIL | short | UP | 669 | 0.011 |
| COIL | long | COIL | 548 | -0.189 |
| COIL | long | DOWN | 971 | -0.034 |
| COIL | long | RANGE | 628 | -0.049 |
| COIL | long | STRONG_DOWN | 432 | -0.087 |
| COIL | long | STRONG_UP | 578 | -0.134 |
| COIL | long | UP | 700 | 0.052 |
| DISP | short | COIL | 58 | 0.114 |
| DISP | short | DOWN | 60 | 0.087 |
| DISP | short | RANGE | 77 | -0.734 |
| DISP | short | STRONG_DOWN | 4 | -1.045 |
| DISP | short | STRONG_UP | 45 | -0.377 |
| DISP | short | UP | 77 | 0.109 |
| DISP | long | COIL | 44 | -0.504 |
| DISP | long | DOWN | 55 | -0.097 |
| DISP | long | RANGE | 96 | -0.341 |
| DISP | long | STRONG_DOWN | 41 | 0.354 |
| DISP | long | STRONG_UP | 146 | 0.131 |
| DISP | long | UP | 137 | 0.341 |
| SWING50 | short | COIL | 655 | 0.198 |
| SWING50 | short | DOWN | 1390 | -0.085 |
| SWING50 | short | RANGE | 506 | 0.211 |
| SWING50 | short | STRONG_DOWN | 790 | -0.056 |
| SWING50 | short | STRONG_UP | 384 | 0.087 |
| SWING50 | short | UP | 604 | 0.11 |
| SWING50 | long | COIL | 368 | 0.011 |
| SWING50 | long | DOWN | 677 | -0.17 |
| SWING50 | long | RANGE | 405 | -0.083 |
| SWING50 | long | STRONG_DOWN | 265 | 0.028 |
| SWING50 | long | STRONG_UP | 1307 | -0.005 |
| SWING50 | long | UP | 930 | 0.205 |
