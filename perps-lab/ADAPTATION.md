# "151 Trading Strategies" mapped to crypto perps

Source: Kakushadze & Serur, *151 Trading Strategies* (2018). Each chapter's strategies are mapped to the economic
mechanism behind them, then to its closest crypto-perp version. "Test" names refer to `studies/p151.py` (basket books)
or `strategies/` (single-coin trades). Status lives in STRATEGIES.md and LEDGER.md.

| ch | paper strategies | mechanism | crypto-perp adaptation | test |
|---|---|---|---|---|
| 2 | options: straddles, strangles | pay for a big move either way | two-sided breakout after a volatility squeeze | SQZ (done) |
| 2 | options: short straddle, iron condor, butterflies | sell range / collect premium | fade the edges of a range when volatility is high | MR, CHANFADE |
| 2 | covered call, protective put, collar | cap upside / floor downside | take-profit + stop-loss on every trade | built into the engine |
| 3.1 | price momentum | winners keep winning | cross-sectional momentum, 60d skip 7d | MOM |
| 3.2-3.3 | earnings momentum, value | fundamentals | no earnings or book value in crypto | not adaptable |
| 3.4 | low-volatility anomaly | lottery demand overprices risky assets | long low-vol / short high-vol coins | LOWVOL |
| 3.5 | implied volatility | options-implied info | needs crypto option data (DVOL) | deferred (data) |
| 3.6, 3.20 | multifactor, alpha combos | diversify across signals | combine the books that pass | after single tests |
| 3.7 | residual momentum | momentum net of market factors | momentum of returns net of BTC beta | RESMOM |
| 3.8 | pairs trading | correlated assets re-converge | correlated coin pairs, re-picked weekly | PAIRS |
| 3.9-3.10 | mean reversion in clusters | overreaction vs peers | weekly contrarian vs the cross-section | CONTRA |
| 3.11-3.13 | 1/2/3 moving averages | trends persist | per-coin MA trend book | MA2, MA3 |
| 3.14 | support / resistance (pivots) | intraday levels | daily pivot trades on 1h bars | PIVOT |
| 3.15 | channel | bounce off range edges | 20-day channel fade (breakout = BRK, done) | CHANFADE |
| 3.16 | event-driven M&A | events misprice | **new perp listings** underperform like IPOs | NEWLIST |
| 3.17, 18.2 | KNN, neural nets | nonlinear patterns | ML on technical features (walk-forward only) | deferred (overfitting risk) |
| 3.18-3.19 | stat-arb optimization, market making | | needs automation / maker fills | not for manual trading |
| 4.1 | sector momentum rotation (+ MA filter, dual momentum) | sector trends | **crypto sectors** (L1, DeFi, meme, AI...) and dual momentum with a BTC filter | SECTOR, DUALMOM |
| 4.2-4.3 | alpha rotation, R-squared | skill = alpha with low market dependence | alpha and R² vs BTC | RSQ |
| 4.5 | leveraged ETF decay | volatility drag | no direct perp version | not adaptable |
| 4.6 | multi-asset trend following | trends, risk-weighted | long-only coin trend book, return/variance weights | TRENDLO |
| 5.5-5.8 | immunization, duration-neutral butterflies | hedge the common factor | beta-neutral to BTC (as in RESMOM / RSQ) | via RESMOM, RSQ |
| 5.9 | low-risk factor | | same as low volatility | LOWVOL |
| 5.11, 8.2, 9.1 | bond carry, FX carry, roll yield | get paid to hold | **funding-rate carry**: long negative funding, short high funding | CARRY |
| 8.3 | dollar carry | average carry times the market | **average funding across coins** to time the basket | DOLLARCARRY |
| 8.4 | momentum & carry combo | two weakly correlated premia | MOM + CARRY | MOMCARRY |
| 6.2 | cash-and-carry | spot vs future basis | perp premium vs spot (needs a spot leg) | deferred (data) |
| 6.3 | dispersion | index vs constituent volatility | cross-sectional dispersion as a gate on momentum | DISPMOM |
| 6.5 | volatility targeting | constant risk | basket scaled to 40% vol | VOLTARGET |
| 7.2-7.4 | VIX basis, vol carry, vol risk premium | volatility term structure | short-term vs long-term realized vol as a regime | deferred (filter test) |
| 9.2 | hedging pressure | follow / fade the hedgers | fade the crowd's long/short ratio; follow top traders vs the crowd | CROWDFADE, CROWDTOP |
| 9.5 | skewness premium | lottery tickets overpriced | short the most positively skewed coins | SKEW |
| 14.4 | spark spread | input vs output spread | mean reversion inside ecosystems (ETH, SOL, BTC, BNB groups) | ECO |
| 15 | distressed debt | buy after capitulation | coins > 75% below their 1-year high that turn up | DISTRESS |
| 19.5 | economic announcements | pre-announcement drift | long the basket on FOMC decision days | FOMCDAY |
| 5, 11-13, 16, 17 | bonds, CDOs, MBS, convertibles, tax, real estate, cash | | no perp counterpart (or illegal: ch 17's laundering / loan sharking, excluded) | not adaptable |
