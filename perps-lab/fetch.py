"""Download / update 1h Binance USDT-M perp history for the 72 coins.
    python3 fetch.py              # all coins (incremental)
    python3 fetch.py BTC,SOL      # some coins
"""
import sys

import config
from lib.data import download_all

if __name__ == "__main__":
    coins = sys.argv[1].split(",") if len(sys.argv) > 1 else config.COINS
    for coin, n in download_all(coins):
        print("%-8s %6d 1h bars" % (coin, n), flush=True)
