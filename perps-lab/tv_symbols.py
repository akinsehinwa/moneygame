"""TradingView symbols for the Monday ticket run (prices: BINANCE:<SYM>USDT.P; crowd: BINANCE:<SYM>USDT.P_LSR).
    python3 tv_symbols.py          # one line per coin: coin, price symbol, long/short-ratio symbol
Save results as data/tv_daily.json and data/tv_lsr.json ({coin: {"t": [unix sec], "o": [], "h": [], "l": [], "c": [],
"v": []}}, COMPLETE daily bars only, i.e. drop the bar still forming) and data/live_prices.json
({"source": ..., "fetched_utc": "YYYY-MM-DD HH:MM", "prices": {coin: price}}); prices are in Binance contract units
(e.g. 1000PEPE). Then rebuild the panel and run tickets.py."""
import config

for c in config.COINS:
    s = config.BINANCE_SYMBOL.get(c, c)
    print(c, "BINANCE:%sUSDT.P" % s, "BINANCE:%sUSDT.P_LSR" % s)
