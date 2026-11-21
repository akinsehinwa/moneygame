"""Download / update 1h Binance USDT-M perp klines and funding-rate history for the 72 coins.
    python3 fetch.py              # all coins (incremental)
    python3 fetch.py BTC,SOL      # some coins
"""
import sys

import config
from concurrent.futures import ThreadPoolExecutor

from lib.data import download_all, download_funding

if __name__ == "__main__":
    coins = sys.argv[1].split(",") if len(sys.argv) > 1 else config.COINS
    for coin, n in download_all(coins):
        print("%-8s %6d 1h bars" % (coin, n), flush=True)
    with ThreadPoolExecutor(12) as ex:
        for coin, n in ex.map(download_funding, coins):
            print("%-8s %6d funding prints" % (coin, n), flush=True)
