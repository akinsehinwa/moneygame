"""Download 4-hour Binance positioning metrics (from the 5-minute daily files) for the 72 coins.  python3 fetch_metrics4h.py"""
import sys
from concurrent.futures import ThreadPoolExecutor

import config
from lib.data import download_metrics4h

if __name__ == "__main__":
    coins = sys.argv[1].split(",") if len(sys.argv) > 1 else config.COINS
    with ThreadPoolExecutor(4) as ex:
        for coin, n in ex.map(download_metrics4h, coins):
            print("%-8s %5d 4h bars" % (coin, n), flush=True)
