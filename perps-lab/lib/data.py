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


def load_1h(coin, trim_dead=True):
    """1h bars. trim_dead: drop everything up to the end of the last stretch of >= 3 days with zero volume
    (a delisted contract whose ticker was later reused for a different token, e.g. LIT; or a dead pre-launch period)."""
    a = np.array(json.load(open(path_1h(coin))), dtype=float)
    df = pd.DataFrame(a[:, :6], columns=["t", "o", "h", "l", "c", "v"])
    df["t"] = df.t.astype("int64")
    if trim_dead and len(df):
        day = df.t // (24 * H)
        dv = df.groupby(day).v.sum()
        dead = (dv == 0).astype(int)
        runs = dead.groupby((dead != dead.shift()).cumsum()).transform("sum") * dead
        long_dead = runs[runs >= 3]
        if len(long_dead):
            df = df[day > long_dead.index.max()].reset_index(drop=True)
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


METRICS = "https://data.binance.vision/data/futures/um/daily/metrics/%sUSDT/%sUSDT-metrics-%s.zip"


def path_metrics(coin):
    return os.path.join(config.DATA, "%s-metrics.json" % coin)


def _metrics_day(sym, day):
    blob = _get(METRICS % (sym, sym, day.isoformat()))
    if not blob:
        return None
    rows = []
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for n in z.namelist():
            for r in csv.reader(io.TextIOWrapper(z.open(n), "utf-8")):
                if r and r[0][:2] == "20":
                    try:
                        rows.append([float(x) if x else np.nan for x in r[2:8]])
                    except ValueError:
                        pass
    if not rows:
        return None
    a = np.array(rows)
    t = int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp() * 1000)
    # daily: open interest (last), OI value (last), top-trader account ratio, top-trader position ratio,
    # global account long/short ratio, taker buy/sell volume ratio (means over the day's 5-minute rows)
    return [t, a[-1, 0], a[-1, 1]] + [float(np.nanmean(a[:, k])) for k in (2, 3, 4, 5)]


def download_metrics(coin, workers=8):
    """Binance positioning metrics, one daily file per day -> [[day_ms, oi, oi_value, top_acct_ratio,
    top_pos_ratio, global_ls_ratio, taker_ratio], ...]. Incremental."""
    sym = config.BINANCE_SYMBOL.get(coin, coin)
    f = path_metrics(coin)
    have = {r[0]: r for r in json.load(open(f))} if os.path.exists(f) else {}
    start = dt.date.fromisoformat(config.HISTORY_START)
    today = dt.datetime.now(dt.timezone.utc).date()
    days, d = [], start
    while d < today:
        t = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() * 1000)
        if t not in have:
            days.append(d)
        d += dt.timedelta(days=1)
    with ThreadPoolExecutor(workers) as ex:
        for r in ex.map(lambda x: _metrics_day(sym, x), days):
            if r:
                have[r[0]] = r
    json.dump(sorted(have.values()), open(f, "w"))
    return coin, len(have)


def load_tv(kind):
    """Recent daily bars saved from TradingView (data/tv_<kind>.json: {coin: {"t": [sec], "o": [], "h": [], "l": [],
    "c": [], "v": []}}), used to fill the days the Binance archive hasn't published yet. kind = "daily" or "lsr"."""
    f = os.path.join(config.DATA, "tv_%s.json" % kind)
    return json.load(open(f)) if os.path.exists(f) else {}


def load_metrics(coin):
    cols = ["t", "oi", "oi_value", "top_acct", "top_pos", "global_ls", "taker"]
    a = json.load(open(path_metrics(coin))) if os.path.exists(path_metrics(coin)) else []
    df = pd.DataFrame(a, columns=cols)
    tv = load_tv("lsr").get(coin)
    if tv:                                   # TradingView long/short ratio for days after the archive (daily bar average)
        last = df.t.max() if len(df) else -1
        for i, t in enumerate(tv["t"]):
            ms = int(t) * 1000
            if ms > last:
                avg = (tv["o"][i] + tv["h"][i] + tv["l"][i] + tv["c"][i]) / 4
                df.loc[len(df)] = [ms, np.nan, np.nan, np.nan, np.nan, avg, np.nan]
    return df
