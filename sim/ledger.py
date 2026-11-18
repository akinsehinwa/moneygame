#!/usr/bin/env python3
"""Simulated paper-trading ledger for the 5-day AI trading competition.

Orders are filled only against real 5-minute bars (Yahoo chart API, regular session),
using conservative rules documented in RULES.md. All state lives in sim/state.json and
every action is appended to sim/events.log so the history can be audited.
"""
import argparse, json, math, os, sys, time, urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HERE = os.environ.get("LEDGER_DIR") or os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
LOG = os.path.join(HERE, "events.log")
BAR = 300  # 5-minute bars
MAX_POS_PCT = 0.25
START_CASH = 100.0


# ---------- state ----------
def load():
    if not os.path.exists(STATE):
        return {"start_cash": START_CASH, "cash": START_CASH, "next_id": 1,
                "orders": [], "positions": [], "closed": [], "marks": {}}
    with open(STATE) as f:
        return json.load(f)


def save(s):
    with open(STATE, "w") as f:
        json.dump(s, f, indent=2, sort_keys=True)


def log(msg):
    line = f"{datetime.now(ET):%Y-%m-%d %H:%M:%S %Z} | {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def fmt_t(ts):
    return datetime.fromtimestamp(ts, ET).strftime("%Y-%m-%d %H:%M ET")


# ---------- market data ----------
def fetch_bars(symbol, start_ts, end_ts=None):
    end_ts = end_ts or int(time.time())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?interval=5m&period1={int(start_ts) - BAR}&period2={int(end_ts)}&includePrePost=false")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.load(r)["chart"]["result"][0]
            break
        except Exception as e:  # network hiccup: back off and retry
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    q = d["indicators"]["quote"][0]
    now = time.time()
    bars = []
    for i, t in enumerate(d.get("timestamp") or []):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c):
            continue
        if t + BAR > now:  # still forming: never fill on an incomplete bar
            continue
        bars.append({"t": t, "o": o, "h": h, "l": l, "c": c})
    return bars


def session_close_ts(ts):
    """16:00 ET of the session an order placed at ts belongs to (next session if after hours)."""
    d = datetime.fromtimestamp(ts, ET)
    close = d.replace(hour=16, minute=0, second=0, microsecond=0)
    if d >= close or d.weekday() >= 5:
        close += timedelta(days=1)
        while close.weekday() >= 5:
            close += timedelta(days=1)
    return int(close.timestamp())


# ---------- accounting ----------
def reserved_cash(s):
    return sum(o["qty"] * o["limit"] for o in s["orders"] if o["status"] == "open")


def equity(s):
    pos_val = sum(p["qty"] * s["marks"].get(p["symbol"], p["entry"]) for p in s["positions"])
    return s["cash"] + pos_val


# ---------- commands ----------
def cmd_place(a):
    s = load()
    sym = a.symbol.upper()
    if not (a.stop < a.limit < a.target):
        sys.exit("Rejected: need stop < limit < target.")
    eq = equity(s)
    last = fetch_bars(sym, time.time() - 5 * 86400)
    if last:
        mkt = last[-1]["c"]
        if mkt <= a.stop:
            sys.exit(f"Rejected: market {mkt} already at/below stop {a.stop}.")
        if a.limit > mkt * 1.02:
            sys.exit(f"Rejected: limit {a.limit} is >2% above market {mkt}; reprice.")
    if a.qty:
        qty = a.qty
    else:
        qty = math.floor(a.dollars / a.limit * 10000) / 10000
    notional = qty * a.limit
    if notional > MAX_POS_PCT * eq + 1e-9:
        sys.exit(f"Rejected: ${notional:.2f} exceeds 25% cap (${MAX_POS_PCT*eq:.2f}).")
    existing = sum(p["qty"] * p["entry"] for p in s["positions"] if p["symbol"] == sym)
    existing += sum(o["qty"] * o["limit"] for o in s["orders"] if o["symbol"] == sym and o["status"] == "open")
    if existing + notional > MAX_POS_PCT * eq + 1e-9:
        sys.exit(f"Rejected: combined {sym} exposure would exceed 25% cap.")
    avail = s["cash"] - reserved_cash(s)
    if notional > avail + 1e-9:
        sys.exit(f"Rejected: ${notional:.2f} > available cash ${avail:.2f}.")
    now = int(time.time())
    oid = s["next_id"]; s["next_id"] += 1
    o = {"id": oid, "symbol": sym, "side": "buy", "qty": qty, "limit": a.limit, "stop": a.stop,
         "target": a.target, "tif": a.tif, "placed_at": now,
         "expires_at": session_close_ts(now) if a.tif == "day" else None,
         "status": "open", "reason": a.reason, "strategy": a.strategy, "regime": a.regime,
         "orig_stop": a.stop}
    s["orders"].append(o)
    save(s)
    risk = qty * (a.limit - a.stop)
    log(f"PLACE #{oid} BUY {qty} {sym} LMT {a.limit} | target {a.target} stop {a.stop} | "
        f"${notional:.2f} ({notional/eq:.0%} of equity), max risk ${risk:.2f} | [{a.strategy} @ {a.regime}] {a.reason}")


def cmd_cancel(a):
    s = load()
    for o in s["orders"]:
        if o["id"] == a.id and o["status"] == "open":
            o["status"] = "cancelled"; save(s); log(f"CANCEL #{a.id} {o['symbol']}"); return
    sys.exit("No open order with that id.")


def cmd_modify(a):
    s = load()
    for p in s["positions"] + [o for o in s["orders"] if o["status"] == "open"]:
        if p["id"] == a.id:
            old = (p["stop"], p["target"])
            if a.stop is not None: p["stop"] = a.stop
            if a.target is not None: p["target"] = a.target
            save(s)
            log(f"MODIFY #{a.id} {p['symbol']} stop {old[0]}->{p['stop']} target {old[1]}->{p['target']} | {a.reason}")
            return
    sys.exit("No open order/position with that id.")


def close_position(s, p, price, ts, why):
    proceeds = p["qty"] * price
    s["cash"] += proceeds
    pnl = proceeds - p["qty"] * p["entry"]
    rec = dict(p, exit=price, exit_time=ts, exit_reason=why, pnl=round(pnl, 4))
    s["closed"].append(rec)
    s["positions"].remove(p)
    log(f"EXIT #{p['id']} SELL {p['qty']} {p['symbol']} @ {price:.4f} ({why}) at {fmt_t(ts)} | P&L ${pnl:+.2f}")


def cmd_update(a=None):
    s = load()
    syms = {o["symbol"] for o in s["orders"] if o["status"] == "open"} | {p["symbol"] for p in s["positions"]}
    syms |= set(s["marks"].keys()) if a and getattr(a, "all", False) else set()
    now = int(time.time())
    for sym in sorted(syms):
        starts = [o["placed_at"] for o in s["orders"] if o["symbol"] == sym and o["status"] == "open"]
        starts += [p["processed_to"] for p in s["positions"] if p["symbol"] == sym]
        start = min(starts) if starts else now - 86400
        bars = fetch_bars(sym, start)
        for b in bars:
            t = b["t"]
            # 1) entries: bar must START at/after placement
            for o in [o for o in s["orders"] if o["symbol"] == sym and o["status"] == "open"]:
                if o["expires_at"] and t >= o["expires_at"]:
                    o["status"] = "expired"; log(f"EXPIRE #{o['id']} {sym} (day order unfilled)"); continue
                if t < o["placed_at"] or b["l"] > o["limit"]:
                    continue
                px = min(o["limit"], b["o"])
                cost = o["qty"] * px
                s["cash"] -= cost
                o["status"] = "filled"
                p = {"id": o["id"], "symbol": sym, "qty": o["qty"], "entry": px, "entry_time": t,
                     "stop": o["stop"], "target": o["target"], "reason": o["reason"],
                     "strategy": o.get("strategy", "untagged"), "regime": o.get("regime", "untagged"),
                     "orig_stop": o.get("orig_stop", o["stop"]), "processed_to": t + BAR}
                s["positions"].append(p)
                log(f"FILL #{o['id']} BUY {o['qty']} {sym} @ {px:.4f} at {fmt_t(t)} (${cost:.2f})")
                if b["l"] <= p["stop"]:  # same-bar stop: assume the worst case happened
                    close_position(s, p, min(p["stop"], px), t, "stop (fill bar)")
            # 2) exits on bars after the fill bar; stop wins if both levels touched in one bar
            for p in [p for p in s["positions"] if p["symbol"] == sym]:
                if t < p["processed_to"]:
                    continue
                if b["l"] <= p["stop"]:
                    close_position(s, p, min(p["stop"], b["o"]), t, "stop"); continue
                if b["h"] >= p["target"]:
                    close_position(s, p, max(p["target"], b["o"]), t, "target"); continue
                p["processed_to"] = t + BAR
        # expire day orders whose session ended with no further bars
        for o in s["orders"]:
            if o["symbol"] == sym and o["status"] == "open" and o["expires_at"] and now >= o["expires_at"] + 600:
                o["status"] = "expired"; log(f"EXPIRE #{o['id']} {sym} (day order unfilled)")
        if bars:
            s["marks"][sym] = bars[-1]["c"]
    save(s)


def cmd_exit(a):
    """Exit at the next bar: implemented as a sell-limit target; use target<=market for an immediate exit."""
    s = load()
    for p in s["positions"]:
        if p["id"] == a.id:
            old = p["target"]; p["target"] = a.limit; save(s)
            log(f"EXIT-ORDER #{a.id} {p['symbol']} sell limit {a.limit} (was target {old}) | {a.reason}")
            return
    sys.exit("No position with that id.")


def cmd_report(a):
    s = load()
    eq = equity(s)
    print(f"Equity ${eq:.2f} | cash ${s['cash']:.2f} | start ${s['start_cash']:.2f} | "
          f"P&L ${eq - s['start_cash']:+.2f} ({(eq/s['start_cash']-1):+.2%})")
    for p in s["positions"]:
        m = s["marks"].get(p["symbol"], p["entry"])
        print(f"  OPEN #{p['id']} {p['symbol']} {p['qty']} @ {p['entry']:.2f} mark {m:.2f} "
              f"unreal ${p['qty']*(m-p['entry']):+.2f} | stop {p['stop']} target {p['target']}")
    for o in s["orders"]:
        if o["status"] == "open":
            print(f"  ORDER #{o['id']} BUY {o['qty']} {o['symbol']} LMT {o['limit']} stop {o['stop']} target {o['target']}")
    for c in s["closed"]:
        print(f"  CLOSED #{c['id']} {c['symbol']} {c['qty']} {c['entry']:.2f}->{c['exit']:.2f} ({c['exit_reason']}) ${c['pnl']:+.2f}")


def r_multiple(p, exit_px):
    risk = p["entry"] - p.get("orig_stop", p["stop"])
    return (exit_px - p["entry"]) / risk if risk > 0 else 0.0


def cmd_stats(a):
    """Performance by strategy and by regime: closed trades (realized) plus open positions (marked)."""
    s = load()
    rows = [(c, c["exit"], "closed") for c in s["closed"]]
    rows += [(p, s["marks"].get(p["symbol"], p["entry"]), "open") for p in s["positions"]]
    for key in ("strategy", "regime"):
        groups = {}
        for p, px, st in rows:
            groups.setdefault(p.get(key, "untagged"), []).append((p, px, st))
        print(f"== by {key} ==")
        for g, items in sorted(groups.items()):
            closed = [(p, px) for p, px, st in items if st == "closed"]
            wins = sum(1 for p, px in closed if px > p["entry"])
            pnl = sum(p["qty"] * (px - p["entry"]) for p, px, _ in items)
            avg_r = sum(r_multiple(p, px) for p, px, _ in items) / len(items)
            print(f"  {g}: {len(items)} trades ({len(closed)} closed, {wins} wins), "
                  f"P&L ${pnl:+.2f}, avg R {avg_r:+.2f}")


def cmd_snapshot(a):
    """Append today's closing equity and SPY close to sim/equity.csv (one row per date)."""
    s = load()
    spy = fetch_bars("SPY", time.time() - 5 * 86400)
    day = getattr(a, "date", None) or datetime.now(ET).strftime("%Y-%m-%d")
    path = os.path.join(HERE, "equity.csv")
    lines = []
    if os.path.exists(path):
        with open(path) as f:
            lines = [l for l in f.read().splitlines()[1:] if not l.startswith(day)]
    lines.append(f"{day},{equity(s):.4f},{s['cash']:.4f},{spy[-1]['c'] if spy else ''}")
    with open(path, "w") as f:
        f.write("date,equity,cash,spy_close\n" + "\n".join(lines) + "\n")
    print(lines[-1])


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("place"); p.add_argument("symbol")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--qty", type=float); g.add_argument("--dollars", type=float)
    p.add_argument("--limit", type=float, required=True); p.add_argument("--stop", type=float, required=True)
    p.add_argument("--target", type=float, required=True); p.add_argument("--tif", default="day", choices=["day", "gtc"])
    p.add_argument("--reason", required=True)
    p.add_argument("--strategy", required=True, help="playbook strategy name from STRATEGY.md")
    p.add_argument("--regime", required=True, help="regime label from sim/regime.py")
    c = sp.add_parser("cancel"); c.add_argument("id", type=int)
    m = sp.add_parser("modify"); m.add_argument("id", type=int)
    m.add_argument("--stop", type=float); m.add_argument("--target", type=float); m.add_argument("--reason", required=True)
    e = sp.add_parser("exit"); e.add_argument("id", type=int); e.add_argument("--limit", type=float, required=True)
    e.add_argument("--reason", required=True)
    u = sp.add_parser("update"); u.add_argument("--all", action="store_true")
    sp.add_parser("report"); sp.add_parser("stats")
    sn = sp.add_parser("snapshot"); sn.add_argument("--date", help="session date if run late (YYYY-MM-DD)")
    a = ap.parse_args()
    {"place": cmd_place, "cancel": cmd_cancel, "modify": cmd_modify, "exit": cmd_exit,
     "update": cmd_update, "report": cmd_report,
     "stats": cmd_stats, "snapshot": cmd_snapshot}[a.cmd](a)


if __name__ == "__main__":
    main()
