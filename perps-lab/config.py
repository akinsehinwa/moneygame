"""Lab-wide settings. Every script reads these, so a change here applies everywhere."""
import os

LAB = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(LAB, "data")          # git-ignored: raw bars and trade files
RESULTS = os.path.join(LAB, "results")    # committed: dated reports

# The universe: 72 USDT-margined perpetuals (TradingView "<SYM>USDT.P"), in the user's order.
COINS = [
    "BTC", "ETH", "LTC", "BCH", "TRX", "FIL", "LINK", "DOT", "XRP", "DOGE", "SHIB", "ADA", "SOL", "BNB", "AVAX",
    "UNI", "CHZ", "APE", "ATOM", "ARB", "SUI", "PEPE", "OP", "WLD", "COMP", "ORDI", "SEI", "APT", "LDO", "MINA",
    "CFX", "FLOKI", "JTO", "INJ", "FET", "ICP", "BONK", "ENS", "NEAR", "WIF", "TIA", "IMX", "JUP", "PYTH", "GALA",
    "BOME", "STX", "HBAR", "JASMY", "GRT", "ONDO", "PENDLE", "ENA", "AR", "TAO", "VET", "BEAMX", "ETHFI", "TRUMP",
    "MELANIA", "HYPE", "VIRTUAL", "BRETT", "WLFI", "PUMP", "LINEA", "ASTER", "ZEC", "LIT", "RIVER", "PIPPIN", "XMR",
]
# Binance lists some low-priced coins per 1000 units.
BINANCE_SYMBOL = {"SHIB": "1000SHIB", "PEPE": "1000PEPE", "FLOKI": "1000FLOKI", "BONK": "1000BONK"}

# Data: Binance USDT-M futures klines from Binance's public archive (data.binance.vision).
HISTORY_START = "2023-08-01"     # coins
BTC_HISTORY_START = "2022-06-01" # BTC needs extra warm-up for the regime filter

# Costs and execution (applied to every strategy).
FEE_PER_SIDE = 0.0004            # 0.04% taker
SLIP_PER_SIDE = 0.0002           # 0.02% slippage
MAX_HOLD_HOURS = 7 * 24          # hard cap on any trade

# Evaluation windows.
EVAL_START = "2023-11-20"        # first signal counted
SPLIT = "2025-11-20"             # before = "old" (2 years), after = "last 12 months"
WF_START = "2024-11-20"          # walk-forward: first out-of-sample quarter
WF_STEP_MONTHS = 3

# A strategy (or a strategy in a regime) is "on" in the walk-forward when its PAST trades show
# avg R above ROUTER_MIN_R with at least ROUTER_MIN_N trades.
ROUTER_MIN_R = 0.10
ROUTER_MIN_N = 40
