#!/usr/bin/env python3
"""Market-regime classifier for the adaptive trading loop.

Classifies the US market on four axes from daily data (Yahoo chart API):
  trend      - SPY vs its 50/200-day SMAs and the 20-day SMA slope: up / down / range
  volatility - VIX level: low (<16) / normal (16-22) / high (22-30) / extreme (>=30)
  leadership - 20-day return of defensives (XLV XLP XLU) minus cyclicals (XLK XLY XLF XLI):
               risk-on / mixed / risk-off
  breadth    - how many of the 11 sector ETFs close above their 20-day EMA

The combined label (e.g. "down/high/risk-off") selects a playbook entry in STRATEGY.md.
`python3 sim/regime.py` prints today's regime and appends it to sim/regime_log.csv
(one row per date; re-running the same day overwrites that day's row).
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
LOGF = os.path.join(HERE, "regime_log.csv")
SECTORS = ["XLK", "XLF", "XLV", "XLP", "XLU", "XLE", "XLI", "XLY", "XLC", "XLB", "XLRE"]
DEFENSIVE = ["XLV", "XLP", "XLU"]
CYCLICAL = ["XLK", "XLY", "XLF", "XLI"]
FIELDS = ["date", "label", "trend", "volatility", "leadership", "breadth", "spy", "sma20", "sma50",
          "sma200", "sma20_slope_pct", "vix", "def_minus_cyc_20d_pct", "leaders"]


def daily_closes(sym, rng="1y"):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}"
           f"?interval=1d&range={rng}")
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.load(r)["chart"]["result"][0]
            break
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    closes = d["indicators"]["quote"][0]["close"]
    return [c for c in closes if c is not None]


def sma(xs, n):
    return sum(xs[-n:]) / n


def ema(xs, n):
    e = xs[0]
    for x in xs[1:]:
        e += (x - e) * 2 / (n + 1)
    return e


def ret(xs, n):
    return xs[-1] / xs[-1 - n] - 1


def classify():
    spy = daily_closes("SPY")
    vix = daily_closes("^VIX", "3mo")[-1]
    s20, s50, s200 = sma(spy, 20), sma(spy, 50), sma(spy, 200)
    slope = (s20 / (sum(spy[-25:-5]) / 20) - 1) * 100  # 20-day SMA now vs 5 days ago
    px = spy[-1]
    if px > s50 and s50 > s200 and slope > 0:
        trend = "up"
    elif px < s50 and slope < 0:
        trend = "down"
    else:
        trend = "range"
    vol = "low" if vix < 16 else "normal" if vix < 22 else "high" if vix < 30 else "extreme"

    sec = {s: daily_closes(s, "6mo") for s in SECTORS}
    r20 = {s: ret(c, 20) for s, c in sec.items()}
    spread = (sum(r20[s] for s in DEFENSIVE) / 3 - sum(r20[s] for s in CYCLICAL) / 4) * 100
    lead = "risk-off" if spread > 2 else "risk-on" if spread < -2 else "mixed"
    breadth = sum(1 for c in sec.values() if c[-1] > ema(c[-60:], 20))
    leaders = sorted(r20, key=r20.get, reverse=True)[:3]

    return {"date": datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d"),
            "label": f"{trend}/{vol}/{lead}", "trend": trend, "volatility": vol, "leadership": lead,
            "breadth": f"{breadth}/11", "spy": round(px, 2), "sma20": round(s20, 2),
            "sma50": round(s50, 2), "sma200": round(s200, 2), "sma20_slope_pct": round(slope, 2),
            "vix": round(vix, 2), "def_minus_cyc_20d_pct": round(spread, 2), "leaders": " ".join(leaders)}


def append(row):
    rows = []
    if os.path.exists(LOGF):
        with open(LOGF) as f:
            rows = [r for r in csv.DictReader(f) if r["date"] != row["date"]]
    rows.append(row)
    with open(LOGF, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    r = classify()
    if "--no-log" not in sys.argv:
        append(r)
    print(json.dumps(r, indent=2))
