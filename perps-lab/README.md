# perps-lab: a research lab for crypto perp strategies

A self-contained workspace for **finding strategies that are profitable after costs** on 72 USDT-margined
perpetuals (Binance USDT-M data). It doesn't place orders or generate tickets. A strategy leaves this lab only
after it passes the pipeline below, and then you decide where it goes.

Nothing here depends on any other project: the folder can be copied out as its own repository unchanged.

## Folder map

| path | what |
|---|---|
| `config.py` | the universe (72 coins), costs, evaluation windows, router thresholds |
| `fetch.py` | download / update 1h history from Binance's public data archive (data.binance.vision) |
| `fetch_metrics.py` | download Binance positioning metrics (open interest, long/short ratios, taker flow) |
| `backtest.py` | run strategies on every coin → `data/trades.pkl`, each trade tagged with regimes |
| `evaluate.py` | scorecards, results by coin regime, walk-forward router test → `results/<date>-<title>.md` |
| `strategies/` | one file per strategy, same interface (see `strategies/__init__.py`) |
| `studies/` | tests that need every coin at once (breadth, rotation, funding); they merge trades into `data/trades.pkl` |
| `lib/` | data, indicators, regimes, trade simulation |
| `ADAPTATION.md` | every chapter of "151 Trading Strategies" mapped to a crypto-perp version |
| `lib/portfolio.py` | daily basket backtester (costs + funding) for momentum / carry / rotation books |
| `shadow.py` | forward paper test of passed strategies: freezes weekly weights, marks PnL → `shadow/STATUS.md` |
| `PROP_RULES.md` | the prop account's rules (5 positions, stops, 7-day hold, loss limits) and what they mean for design |
| `studies/prop.py` | compact 2-4 position books + challenge simulation (pass rates by day 90 / 180) |
| `tickets.py` | weekly tickets for the two accounts (100K COMBO, 50K CROWDFADE, 1.5% per coin) → `tickets/<date>.md` |
| `STRATEGIES.md` | status board: every strategy and where it is in the pipeline |
| `LEDGER.md` | every hypothesis tested, the result and the decision (including the failures) |
| `results/` | dated reports (committed) |
| `data/` | raw bars and trade files (git-ignored, rebuilt by `fetch.py` + `backtest.py`) |

## Quick start

```bash
cd perps-lab
python3 fetch.py                      # ~3 min first time, incremental after
python3 backtest.py                   # every strategy x 72 coins, ~5 s
python3 evaluate.py --title "baseline pool"
python3 backtest.py --only XYZ && python3 evaluate.py --only XYZ --title "XYZ v1"   # one new idea
python3 shadow.py update              # weekly (Mondays): freeze the new rebalance, mark the shadow book
```

## The pipeline (every idea goes through it, in order)

| stage | what has to be true to move on |
|---|---|
| 1. **Idea** | written in `LEDGER.md` *before* testing: the rule, the parameters, why it might work |
| 2. **Backtest** | a file in `strategies/`, run on all 72 coins with the lab's costs and fills |
| 3. **Robust** | positive after costs both before and after the split (last 12 months), and in the walk-forward |
| 4. **Shadow** | paper-traded forward on live data, untouched, for ~100 trades |
| 5. **Candidate** | forward results in line with the backtest → ready for you to use elsewhere |

Failures stay in `LEDGER.md` (the graveyard), so the same idea isn't re-tested by accident.

## House rules for honest results

1. No look-ahead: signals use closed bars only; regimes use daily bars closed before the signal day.
2. Costs on every trade: 0.04% fee + 0.02% slippage per side. Stops fill at the worse of the stop and the bar open.
   When a bar touches both stop and target, the stop counts. Max hold 7 days. Funding payments are not in R yet.
3. Fix parameters before testing. Count every variant in `LEDGER.md`. After ~20 variants of one idea, treat the
   best as luck.
4. Judge on the last 12 months **and** the 2 years before; an idea must be positive in both.
5. Trades on the same day across coins move together: use the weekly t-stat. |t| < 2 is not significant.
6. A filter must raise total R per month, not just average R on fewer trades.

## Time zone

The user trades on Singapore time (SGT, UTC+8). The crypto daily candle opens at **08:00 SGT** (00:00 UTC); 4H
candles open at 00:00 / 04:00 / 08:00 / 12:00 / 16:00 / 20:00 SGT. Code works in UTC internally; every alert or
schedule shown to the user is in SGT and lands at a 4H candle open, based on the previous candle's close.
Weekly books rebalance at **Monday 08:00 SGT**.

## Regimes (lib/regime.py)

- **Market** (BTC daily): trend UP / DOWN / RANGE x volatility HIGH / LOW.
- **Coin** (each coin's own daily bars): trend UP / DOWN / RANGE x character TREND / CHOP (efficiency ratio).
