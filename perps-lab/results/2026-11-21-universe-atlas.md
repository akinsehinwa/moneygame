# universe atlas (2026-11-21)

## How to read this

Every day since 2023-11-20 is labeled with Bitcoin's state (lib/btcstate.py) and days are pooled by state, not by date. 'Excess vs BTC' = coin daily return minus BTC's on the same day. Retracement = 4h swings of 2 x ATR; '50% retrace prob' = share of swings whose counter-move reached half the leg. Size tier = terciles of median daily trading volume. Per-coin numbers: results/atlas-coins.csv.

## A. Bitcoin states

| BTC state | days (old 2y) | days (last 12m) |
|---|---|---|
| STRONG_DOWN | 59 | 69 |
| DOWN | 165 | 71 |
| COIL | 91 | 49 |
| RANGE | 93 | 60 |
| UP | 146 | 73 |
| STRONG_UP | 177 | 43 |

## B. Inch vs mile: median coin weekly move by BTC's weekly move

| group by | group | coins | BTC <-7% | -7..-2% | -2..+2% | +2..+7% | BTC >+7% |
|---|---|---|---|---|---|---|---|
| reference | BTC itself | 1 | -10.9% | -4.3% | -0.1% | +4.0% | +9.8% |
| size tier | large | 24 | -14.5% | -5.8% | -1.1% | +4.0% | +10.0% |
| size tier | mid | 24 | -15.6% | -6.5% | -1.6% | +4.2% | +10.2% |
| size tier | small | 24 | -16.5% | -6.4% | -1.1% | +3.0% | +9.7% |
| niche | ai | 4 | -16.4% | -7.9% | -1.1% | +3.3% | +11.1% |
| niche | defi | 10 | -15.1% | -5.7% | -0.5% | +2.0% | +6.6% |
| niche | gaming_nft_fan | 4 | -17.0% | -8.5% | -2.0% | +5.1% | +12.9% |
| niche | l1_alt | 14 | -17.0% | -7.7% | -2.2% | +4.2% | +11.5% |
| niche | l1_major | 7 | -13.2% | -4.9% | -0.4% | +3.1% | +9.4% |
| niche | l2_scaling | 5 | -17.9% | -7.4% | -2.1% | +4.6% | +10.9% |
| niche | meme | 11 | -15.2% | -6.7% | -2.7% | +4.1% | +9.5% |
| niche | oracle_data_infra | 7 | -17.7% | -8.0% | -2.5% | +4.9% | +12.1% |
| niche | platform_other | 4 | -12.4% | -0.2% | +0.0% | +0.0% | +0.0% |
| niche | privacy | 2 | -12.1% | -2.4% | +1.2% | +3.8% | +5.3% |
| niche | rwa | 1 | -15.9% | -7.0% | -2.0% | +5.6% | +12.9% |
| niche | store_of_value | 3 | -11.5% | -4.4% | -0.6% | +3.5% | +9.6% |
| cluster | C0 | 2 | -3.3% | +0.0% | +0.0% | +0.0% | +0.0% |
| cluster | C1 | 52 | -16.3% | -7.1% | -1.9% | +4.1% | +11.3% |
| cluster | C2 | 9 | -18.2% | -7.8% | -3.1% | +6.4% | +13.2% |
| cluster | C3 | 9 | -7.9% | -1.1% | +0.0% | +1.3% | +2.8% |

## C1. Excess return vs BTC (% per day) by BTC state

| group by | group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|---|
| cluster | C0 | 2.7 | 0.92 | -0.71 | 1.07 | -0.33 | -0.58 |
| cluster | C1 | -0.07 | -0.38 | -0.14 | -0.07 | -0.21 | 0.47 |
| cluster | C2 | -0.13 | -0.65 | -0.23 | -0.13 | -0.21 | 1.65 |
| cluster | C3 | 0.52 | 0.07 | 0.24 | 0.27 | -0.1 | -0.09 |
| niche | ai | -0.01 | -0.46 | -0.23 | 0.1 | -0.37 | 1.12 |
| niche | defi | 0.1 | -0.54 | 0.01 | 0.13 | -0.11 | 0.46 |
| niche | gaming_nft_fan | -0.22 | -0.47 | -0.31 | -0.04 | -0.26 | 0.48 |
| niche | l1_alt | -0.01 | -0.29 | -0.14 | -0.16 | -0.11 | 0.4 |
| niche | l1_major | 0.2 | -0.17 | 0.07 | -0.12 | -0.1 | 0.23 |
| niche | l2_scaling | -0.35 | -0.5 | -0.3 | -0.07 | -0.26 | 0.47 |
| niche | meme | 0.35 | -0.52 | -0.18 | -0.12 | -0.54 | 1.26 |
| niche | oracle_data_infra | -0.09 | -0.33 | -0.24 | -0.09 | -0.2 | 0.57 |
| niche | platform_other | -0.05 | 0.12 | -0.1 | 0.34 | -0.04 | 0.15 |
| niche | privacy | 0.36 | 0.37 | 0.32 | 0.51 | 0.08 | 0.06 |
| niche | rwa | -0.24 | -0.58 | 0.11 | 0.28 | 0.31 | 0.69 |
| niche | store_of_value | 0.21 | -0.13 | -0.09 | 0.16 | -0.15 | -0.01 |
| size tier | large | 0.03 | -0.32 | -0.04 | -0.05 | -0.17 | 0.57 |
| size tier | mid | -0.01 | -0.36 | -0.06 | 0.03 | -0.18 | 0.58 |
| size tier | small | 0.13 | -0.35 | -0.26 | -0.03 | -0.25 | 0.47 |

## C2. Probability that a swing retraces 50% by BTC state

| group by | group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|---|
| cluster | C0 | 0.83 | 0.9 | 0.88 | 0.86 | 0.87 | 0.85 |
| cluster | C1 | 0.84 | 0.89 | 0.84 | 0.89 | 0.86 | 0.89 |
| cluster | C2 | 0.86 | 0.89 | 0.84 | 0.88 | 0.88 | 0.86 |
| cluster | C3 | 0.86 | 0.89 | 0.88 | 0.89 | 0.87 | 0.89 |
| niche | ai | 0.84 | 0.88 | 0.83 | 0.88 | 0.88 | 0.88 |
| niche | defi | 0.86 | 0.89 | 0.86 | 0.88 | 0.88 | 0.88 |
| niche | gaming_nft_fan | 0.85 | 0.89 | 0.84 | 0.89 | 0.86 | 0.9 |
| niche | l1_alt | 0.84 | 0.89 | 0.84 | 0.88 | 0.86 | 0.88 |
| niche | l1_major | 0.84 | 0.88 | 0.87 | 0.89 | 0.85 | 0.88 |
| niche | l2_scaling | 0.83 | 0.91 | 0.83 | 0.88 | 0.87 | 0.88 |
| niche | meme | 0.85 | 0.89 | 0.83 | 0.89 | 0.88 | 0.88 |
| niche | oracle_data_infra | 0.83 | 0.89 | 0.83 | 0.89 | 0.86 | 0.89 |
| niche | platform_other | 0.87 | 0.89 | 0.86 | 0.9 | 0.88 | 0.87 |
| niche | privacy | 0.85 | 0.91 | 0.89 | 0.87 | 0.88 | 0.92 |
| niche | rwa | 0.85 | 0.9 | 0.83 | 0.9 | 0.85 | 0.91 |
| niche | store_of_value | 0.85 | 0.88 | 0.89 | 0.89 | 0.87 | 0.91 |
| size tier | large | 0.84 | 0.88 | 0.85 | 0.89 | 0.87 | 0.88 |
| size tier | mid | 0.84 | 0.9 | 0.84 | 0.87 | 0.87 | 0.88 |
| size tier | small | 0.85 | 0.89 | 0.85 | 0.9 | 0.87 | 0.89 |

## D. The day after each BTC daily CRT pattern (mean move)

| BTC pattern today | days | BTC next day | large caps next day | mid caps next day | small caps next day |
|---|---|---|---|---|---|
| BULL_CRT | 169 | -0.13% | -0.26% | -0.30% | -0.28% |
| BEAR_CRT | 180 | +0.12% | +0.29% | +0.12% | +0.18% |
| BREAK_UP | 250 | +0.19% | +0.22% | +0.11% | +0.03% |
| BREAK_DN | 231 | -0.03% | -0.21% | -0.02% | -0.15% |
| INSIDE | 217 | +0.07% | +0.03% | +0.02% | -0.04% |
| OUTSIDE | 49 | +0.58% | +0.96% | +1.32% | +1.01% |

## E. Trait clusters (k = 4, silhouette 0.21)

| cluster | profile | members |
|---|---|---|
| C0 | falls harder than BTC, loosely tied to BTC, holds up in BTC falls, very volatile | PIPPIN, RIVER |
| C1 | average | ADA, APE, APT, AR, ARB, ATOM, AVAX, BCH, BEAMX, BOME, BTC, CFX, CHZ, COMP, DOGE, DOT, ENS, ETH, FET, FIL, GALA, GRT, HBAR, ICP, IMX, INJ, JASMY, JTO, JUP, LDO, LINEA, LINK, LTC, MELANIA, MINA, NEAR, ONDO, OP, PUMP, PYTH, SEI, SHIB, SOL, STX, SUI, TAO, TIA, TRUMP, UNI, VET, WLD, XRP |
| C2 | falls harder than BTC, rises more than BTC, lags in BTC falls, leads in BTC rises, very volatile | BONK, BRETT, ENA, ETHFI, FLOKI, ORDI, PEPE, VIRTUAL, WIF |
| C3 | falls less than BTC, loosely tied to BTC, retraces deep often, holds up in BTC falls | ASTER, BNB, HYPE, LIT, PENDLE, TRX, WLFI, XMR, ZEC |

## E2. Clusters vs niche tags (coin counts)

| niche | C0 | C1 | C2 | C3 |
|---|---|---|---|---|
| ai | 0 | 3 | 1 | 0 |
| defi | 0 | 5 | 2 | 3 |
| gaming_nft_fan | 0 | 4 | 0 | 0 |
| l1_alt | 0 | 13 | 0 | 1 |
| l1_major | 0 | 5 | 0 | 2 |
| l2_scaling | 0 | 5 | 0 | 0 |
| meme | 1 | 5 | 5 | 0 |
| oracle_data_infra | 0 | 7 | 0 | 0 |
| platform_other | 1 | 1 | 1 | 1 |
| privacy | 0 | 0 | 0 | 2 |
| rwa | 0 | 1 | 0 | 0 |
| store_of_value | 0 | 3 | 0 | 0 |

## F. Stability: same traits in the old 2 years and the last 12 months?

| trait | coins | rank correlation old vs 12m |
|---|---|---|
| beta_up | 71 | 0.18 |
| beta_down | 71 | 0.25 |
| corr | 71 | 0.48 |
| vol_ratio | 71 | 0.54 |
| retr50_p | 71 | 0.26 |
| retr_depth | 71 | 0.22 |
| excess_down | 71 | 0.15 |
| excess_up | 71 | 0.19 |
| excess_flat | 71 | 0.13 |
| lag4h_corr | 71 | 0.32 |
| cluster membership (adjusted Rand, 1 = identical, 0 = random) | 71 | 0.03 |
