# element atlas (2026-11-21)

## How to read this

Elements (PLAN.md): E1 momentum = how often the next day follows the past week's direction, in points above 50%. E2 reversal = minus the autocorrelation of 4h returns. E4 / E6 = average move over the next 24h in ATR units after a 2-ATR candle / a sweep that closes back inside. E5 = big legs (>= 6 ATR within 5 days): chance of a 50% pullback before a new extreme, days to reach it, and chance of a new extreme after it (before the 78.6% level). E7 = BTC beta on BTC up / down days. E8 = minus the correlation between crowd long-bias and the next week's return (positive = fading the crowd works). States are the last completed day's BTC state.

## Step 3. Memory test: which elements are stable coin traits?

| element | window pairs | avg rank corr 90d -> next 90d | share of pairs > 0 |
|---|---|---|---|
| E1 momentum hit-50% | 11 | -0.02 | 5/11 |
| E2 reversal (-autocorr) | 11 | 0.1 | 9/11 |
| E3 vol vs BTC | 11 | 0.57 | 11/11 |
| E3 squeeze release (ATR) | 11 | 0.11 | 8/11 |
| E4 displacement follow (ATR) | 1 | 0.26 | 1/1 |
| E5 P(50% pullback) | 11 | -0.05 | 4/11 |
| E5 days to 50% | 11 | 0.01 | 6/11 |
| E5 P(continue after 50%) | 11 | -0.1 | 2/11 |
| E6 sweep reversal (ATR) | 12 | -0.01 | 5/12 |
| E7 beta up | 11 | 0.3 | 11/11 |
| E7 beta down | 11 | 0.17 | 9/11 |
| E7 corr | 11 | 0.43 | 11/11 |
| E8 crowd fade (-corr) | 0 |  | 0/0 |

## Step 4. Groups from the stable elements (E3 vol vs BTC, E7 beta up, E7 corr), k = 5, silhouette 0.36

| group | profile (vs the 72-coin average) | members |
|---|---|---|
| G0 | low vol vs BTC; high corr | ADA, APT, ATOM, AVAX, BCH, BNB, BTC, COMP, DOGE, DOT, ETH, GRT, IMX, LINK, LTC, SHIB, SOL, VET, XRP |
| G1 | average on all stable elements | APE, AR, ARB, ASTER, BEAMX, CFX, CHZ, ENS, FET, FIL, GALA, HBAR, HYPE, ICP, INJ, JASMY, JTO, JUP, LDO, LINEA, LIT, MELANIA, MINA, NEAR, ONDO, OP, ORDI, PENDLE, PUMP, PYTH, SEI, SUI, TAO, TIA, TRUMP, UNI, WLD, ZEC |
| G2 | high vol vs BTC; low beta up; low corr | PIPPIN, RIVER |
| G3 | high vol vs BTC; high beta up | BOME, BONK, BRETT, ENA, ETHFI, FLOKI, PEPE, STX, VIRTUAL, WIF |
| G4 | low vol vs BTC; low beta up; low corr | TRX, WLFI, XMR |

## Groups vs niche tags

| niche | G0 | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|
| ai | 0 | 3 | 0 | 1 | 0 |
| defi | 1 | 6 | 0 | 2 | 1 |
| gaming_nft_fan | 0 | 4 | 0 | 0 | 0 |
| l1_alt | 4 | 10 | 0 | 0 | 0 |
| l1_major | 6 | 0 | 0 | 0 | 1 |
| l2_scaling | 1 | 3 | 0 | 1 | 0 |
| meme | 2 | 2 | 1 | 6 | 0 |
| oracle_data_infra | 2 | 5 | 0 | 0 | 0 |
| platform_other | 0 | 3 | 1 | 0 | 0 |
| privacy | 0 | 1 | 0 | 0 | 1 |
| rwa | 0 | 1 | 0 | 0 | 0 |
| store_of_value | 3 | 0 | 0 | 0 | 0 |

## By group x BTC state: E1 momentum hit-50%

| group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| G0 | -1.76 | -5.35 | -0.64 | -0.15 | 2.54 | -0.89 |
| G1 | -1.78 | -4.81 | 1.46 | 1.77 | 2.3 | -0.27 |
| G2 | -3.29 | 1.04 | -2.07 | 3.02 | -2.36 | -1.94 |
| G3 | -1.68 | -5.96 | 3.53 | 3.24 | 2.92 | -1.04 |
| G4 | 0.61 | -4.96 | -0.58 | -1.06 | 1.61 | 2.8 |

## By group x BTC state: E4 displacement follow (ATR)

| group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| G0 | -0.73 | -0.22 | 0.43 | -0.51 | 0.4 | 0.12 |
| G1 | -0.83 | -0.32 | 0.61 | -0.49 | 0.67 | -0.02 |
| G2 | 0.33 | -0.43 | -0.75 | -0.63 | -1.68 | -0.96 |
| G3 | -0.76 | -0.42 | 1.1 | -0.48 | 0.58 | 0.51 |
| G4 | -0.05 | -0.72 | -0.47 | 0.16 | 0.23 | -0.61 |

## By group x BTC state: E5 P(50% pullback)

| group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| G0 | 0.47 | 0.47 | 0.35 | 0.46 | 0.37 | 0.39 |
| G1 | 0.46 | 0.47 | 0.31 | 0.41 | 0.38 | 0.41 |
| G2 | 0.28 | 0.45 | 0.59 | 0.5 | 0.38 | 0.52 |
| G3 | 0.44 | 0.5 | 0.27 | 0.41 | 0.34 | 0.37 |
| G4 | 0.45 | 0.61 | 0.5 | 0.49 | 0.49 | 0.38 |

## By group x BTC state: E5 days to 50%

| group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| G0 | 1.33 | 1.33 | 1.17 | 1.33 | 1.17 | 1.17 |
| G1 | 1.5 | 1.17 | 1.17 | 1.17 | 1.17 | 1.33 |
| G2 | 0.92 | 0.5 | 0.67 | 0.5 | 0.83 | 0.17 |
| G3 | 1.67 | 1.5 | 1.67 | 0.83 | 1.33 | 1.33 |
| G4 | 1.0 | 1.0 | 0.83 | 1.25 | 1.0 | 0.92 |

## By group x BTC state: E5 P(continue after 50%)

| group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| G0 | 0.17 | 0.23 | 0.41 | 0.36 | 0.35 | 0.29 |
| G1 | 0.19 | 0.24 | 0.41 | 0.28 | 0.38 | 0.34 |
| G2 | 0.25 | 0.23 | 0.1 | 0.45 | 0.3 | 0.23 |
| G3 | 0.19 | 0.25 | 0.41 | 0.26 | 0.51 | 0.3 |
| G4 | 0.19 | 0.37 | 0.29 | 0.23 | 0.28 | 0.18 |

## By group x BTC state: E6 sweep reversal (ATR)

| group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| G0 | -0.0 | 0.09 | -0.14 | 0.11 | -0.12 | -0.13 |
| G1 | 0.03 | 0.14 | -0.09 | 0.07 | -0.16 | -0.07 |
| G2 | -0.52 | -0.09 | 0.15 | -0.31 | 0.15 | 0.21 |
| G3 | 0.04 | 0.13 | -0.1 | 0.01 | -0.16 | -0.1 |
| G4 | -0.1 | 0.27 | -0.28 | 0.01 | 0.02 | -0.37 |

## By group x BTC state: E7 beta down

| group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| G0 | 0.99 | 1.49 | 1.67 | 1.37 | 1.65 | 1.23 |
| G1 | 0.99 | 1.67 | 2.05 | 1.52 | 1.9 | 1.2 |
| G2 | 1.91 | 1.75 | 2.94 | 3.79 | 1.94 | 4.66 |
| G3 | 1.14 | 1.82 | 2.41 | 1.89 | 1.95 | 1.75 |
| G4 | 0.92 | 0.67 | 0.63 | 1.08 | 1.06 | 0.66 |

## By group x BTC state: E8 crowd fade (-corr)

| group | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| G0 | 0.07 | 0.0 | 0.02 | 0.01 | 0.01 | 0.08 |
| G1 | 0.06 | -0.01 | -0.11 | 0.05 | -0.02 | 0.04 |
| G2 | 0.2 | 0.04 | 0.41 | 0.45 | 0.27 | 0.09 |
| G3 | -0.04 | -0.01 | 0.08 | 0.06 | 0.11 | 0.09 |
| G4 | 0.1 | -0.01 | 0.38 | 0.02 | -0.26 | 0.18 |

## By size tier x BTC state: E5 P(50% pullback)

| size tier | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| large | 0.48 | 0.47 | 0.34 | 0.42 | 0.36 | 0.38 |
| mid | 0.45 | 0.5 | 0.31 | 0.44 | 0.38 | 0.42 |
| small | 0.44 | 0.47 | 0.33 | 0.42 | 0.39 | 0.4 |

## By size tier x BTC state: E5 days to 50%

| size tier | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| large | 1.5 | 1.33 | 1.33 | 1.0 | 1.17 | 1.33 |
| mid | 1.33 | 1.33 | 1.42 | 1.0 | 1.33 | 1.17 |
| small | 1.67 | 1.0 | 1.0 | 1.33 | 1.0 | 1.17 |

## By size tier x BTC state: E7 beta down

| size tier | STRONG_DOWN | DOWN | COIL | RANGE | UP | STRONG_UP |
|---|---|---|---|---|---|---|
| large | 1.0 | 1.61 | 1.83 | 1.44 | 1.72 | 1.3 |
| mid | 0.96 | 1.59 | 1.98 | 1.55 | 1.75 | 1.08 |
| small | 1.13 | 1.63 | 2.08 | 1.57 | 1.95 | 1.4 |
