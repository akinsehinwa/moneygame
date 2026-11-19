#!/usr/bin/env python3
"""Download adjusted daily OHLC (1999 -> today) for the backtest into sim/data/ (git-ignored)."""
import json, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SYMS = ["SPY", "QQQ", "^VIX", "XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
for s in SYMS:
    u = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(s)}"
         f"?interval=1d&period1=915148800&period2={int(time.time())}&events=div%2Csplit")
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, timeout=60))["chart"]["result"][0]
    q, adj = d["indicators"]["quote"][0], d["indicators"].get("adjclose", [{}])[0].get("adjclose")
    rows = []
    for i, t in enumerate(d["timestamp"]):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c) or c == 0:
            continue
        f = (adj[i] / c) if adj and adj[i] else 1.0  # dividend/split adjustment
        rows.append([time.strftime("%Y-%m-%d", time.gmtime(t)), o * f, h * f, l * f, c * f])
    json.dump(rows, open(os.path.join(HERE, "data", f"{s.replace('^', '')}.json"), "w"))
    print(s, len(rows), rows[0][0], rows[-1][0])
