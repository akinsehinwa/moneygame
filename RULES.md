# Competition rules & simulation method

## Competition (set by the organizer)
- Start: $100 simulated paper account on Mon 2026-11-16. Originally 5 trading days; **extended on 2026-11-17 to year end: the competition ends at the 16:00 ET close on Thu 2026-12-31** (32 trading days; market closed Thu 2026-11-26 and Fri 2026-12-25; early 13:00 ET closes Fri 2026-11-27 and Thu 2026-12-24).
- Lowest final balance is eliminated.
- No position may exceed 25% of the account (checked at order entry, including any resting orders in the same symbol).
- Limit orders only. Every trade has a planned exit (target) and a stop loss.
- One line before each trade: what, why, entry, exit, stop.
- Daily report at the close: balance, every trade, what changes tomorrow.

## Defaults I chose (the organizer did not specify)
- Universe: US-listed stocks and ETFs, long only, regular session (9:30-16:00 ET). No options, crypto, shorting or margin.
- Fractional quantities allowed (4 decimals). Commission-free. No settlement or PDT limits are modeled.
- Score = cash + open positions marked at the last completed 5-minute close on Thu 2026-12-31.

## How fills are simulated (`sim/ledger.py`)
Data: Yahoo Finance 5-minute regular-session bars; TradingView is used for research and spot checks.
Only *completed* bars that **start after** the order was placed are used.

| Event | Triggers when | Fill price |
|---|---|---|
| Buy limit | bar low <= limit | min(limit, bar open) |
| Stop (sell) | bar low <= stop | min(stop, bar open), so gaps hurt |
| Target (sell limit) | bar high >= target | max(target, bar open) |

Conservative tie-breaks:
- If the stop and the target are both touched in one bar, the **stop** is assumed to have hit.
- On the fill bar, only the stop is checked (exit at min(stop, fill price)); the target can't fill until the next bar.
- Day orders expire unfilled at 16:00 ET of their session.
- Orders are rejected if the market is already at or below the stop, or if the limit is >2% above market.
- No slippage beyond the gap rule above, so real fills would be slightly worse.

Every action is appended to `sim/events.log`; state is in `sim/state.json`. Both are committed after each session.

## Usage
```
python3 sim/ledger.py place SYM --dollars 24 --limit L --stop S --target T --reason "..."
python3 sim/ledger.py update        # process new bars: fills, stops, targets, expiries
python3 sim/ledger.py report
python3 sim/ledger.py modify ID --stop S --reason "..."   # e.g. trail a stop
python3 sim/ledger.py exit ID --limit P --reason "..."    # move target to exit
python3 sim/ledger.py cancel ID
```
