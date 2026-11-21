"""Download / update Binance positioning metrics (open interest, long/short ratios, taker ratio) for the 72 coins.
~1,200 small daily files per coin; the first run takes a while.  python3 fetch_metrics.py [BTC,ETH]"""
import sys
from concurrent.futures import ThreadPoolExecutor

import config
from lib.data import download_metrics

if __name__ == "__main__":
    coins = sys.argv[1].split(",") if len(sys.argv) > 1 else config.COINS
    with ThreadPoolExecutor(4) as ex:
        for coin, n in ex.map(download_metrics, coins):
            print("%-8s %5d days of metrics" % (coin, n), flush=True)
