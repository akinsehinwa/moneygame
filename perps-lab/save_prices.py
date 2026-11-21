"""Save TradingView live prices for tickets / check-ins.
Pipe the "data" objects of one or more get_symbol_data_batch results (column close) as JSON on stdin, e.g.
    echo '{"BINANCE:BTCUSDT.P":{"close":57829.9}, ...}' | python3 save_prices.py
Writes data/live_prices.json keyed by our coin names (BINANCE:1000PEPEUSDT.P -> PEPE), Binance contract units."""
import datetime as dt, json, os, sys

import config

raw = {}
for chunk in sys.stdin.read().split("\n"):
    if chunk.strip():
        raw.update(json.loads(chunk))
rev = {"%sUSDT.P" % config.BINANCE_SYMBOL.get(c, c): c for c in config.COINS}
prices = {rev[k.split(":")[1]]: v["close"] for k, v in raw.items() if k.split(":")[1] in rev and v.get("close")}
missing = [c for c in config.COINS if c not in prices]
json.dump({"source": "TradingView BINANCE perps", "fetched_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
           "prices": prices}, open(os.path.join(config.DATA, "live_prices.json"), "w"), indent=1)
print("%d prices saved; missing: %s" % (len(prices), missing or "none"))
