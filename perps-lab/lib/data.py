"""Binance USDT-M perp klines: download from the public archive, load, resample."""
import csv, datetime as dt, io, json, os, urllib.error, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

import config

H = 3600_000
ARCHIVE = "https://data.binance.vision/data/futures/um/%s/klines/%sUSDT/1h/%sUSDT-1h-%s.zip"


def _get(url):
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except Exception:
            pass
    return None


def _parse(blob):
    out = []
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for n in z.namelist():
            for r in csv.reader(io.TextIOWrapper(z.open(n), "utf-8")):
                if r and r[0].strip().isdigit():
                    t = int(r[0])
                    t = t // 1000 if t > 10 ** 14 else t
                    out.append([t, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])])
    return out


def path_1h(coin):
    return os.path.join(config.DATA, "%s-1h.json" % coin)


def download(coin, start=None):
    """Monthly archive files from start, then daily files for the current month. Incremental."""
    start = dt.date.fromisoformat(start or (config.BTC_HISTORY_START if coin == "BTC" else config.HISTORY_START))
    sym = config.BINANCE_SYMBOL.get(coin, coin)
    f = path_1h(coin)
    have = {b[0]: b for b in json.load(open(f))} if os.path.exists(f) else {}
    today = dt.datetime.now(dt.timezone.utc).date()
    first = today.replace(day=1)
    jobs, y, m = [], start.year, start.month
    while dt.date(y, m, 1) < first:
        jobs.append(("monthly", "%04d-%02d" % (y, m), dt.date(y, m, 1)))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    d = first
    while d < today:
        jobs.append(("daily", d.isoformat(), d))
        d += dt.timedelta(days=1)
    for kind, tag, d0 in jobs:
        t0 = int(dt.datetime(d0.year, d0.month, d0.day, tzinfo=dt.timezone.utc).timestamp() * 1000)
        if t0 in have and (kind == "daily" or t0 + 27 * 24 * H in have):
            continue
        blob = _get(ARCHIVE % (kind, sym, sym, tag))
        if blob:
            for b in _parse(blob):
                have[b[0]] = b
    bars = sorted(have.values())
    os.makedirs(config.DATA, exist_ok=True)
    json.dump(bars, open(f, "w"))
    return coin, len(bars)


def download_all(coins=None, workers=12):
    with ThreadPoolExecutor(workers) as ex:
        yield from ex.map(download, coins or config.COINS)


def load_1h(coin):
    a = np.array(json.load(open(path_1h(coin))), dtype=float)
    df = pd.DataFrame(a[:, :6], columns=["t", "o", "h", "l", "c", "v"])
    df["t"] = df.t.astype("int64")
    return df


def resample(df1, hours):
    """Complete bars only, aligned to UTC (4h bars close at 00/04/08/12/16/20 UTC; daily at 00:00 UTC)."""
    ms = hours * H
    g = df1.assign(k=(df1.t // ms) * ms).groupby("k")
    out = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "v": g.v.sum(),
                        "n": g.t.count()})
    out = out[out.n == hours].drop(columns="n")
    out.index.name = "t"
    return out.reset_index()


FUNDING = "https://data.binance.vision/data/futures/um/monthly/fundingRate/%sUSDT/%sUSDT-fundingRate-%s.zip"


def path_funding(coin):
    return os.path.join(config.DATA, "%s-funding.json" % coin)


def download_funding(coin):
    """Monthly funding files: [[funding_time_ms, interval_hours, rate], ...]. The current month isn't archived yet."""
    sym = config.BINANCE_SYMBOL.get(coin, coin)
    start = dt.date.fromisoformat(config.HISTORY_START)
    first = dt.datetime.now(dt.timezone.utc).date().replace(day=1)
    rows, y, m = {}, start.year, start.month
    while dt.date(y, m, 1) < first:
        blob = _get(FUNDING % (sym, sym, "%04d-%02d" % (y, m)))
        if blob:
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                for n in z.namelist():
                    for r in csv.reader(io.TextIOWrapper(z.open(n), "utf-8")):
                        if r and r[0].strip().isdigit():
                            rows[int(r[0])] = [int(r[0]), float(r[1] or 8), float(r[2])]
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    out = sorted(rows.values())
    json.dump(out, open(path_funding(coin), "w"))
    return coin, len(out)


def load_funding(coin):
    a = json.load(open(path_funding(coin))) if os.path.exists(path_funding(coin)) else []
    return pd.DataFrame(a, columns=["t", "interval_h", "rate"])
