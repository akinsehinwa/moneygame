"""Use-case tags for the 72 coins (one primary niche each). Hand-assigned; uncertain ones are marked.
Size tier is NOT hand-assigned: it comes from trading volume in the atlas (a proxy for market cap)."""

NICHE = {
    "store_of_value": ["BTC", "LTC", "BCH"],
    "privacy": ["XMR", "ZEC"],
    "l1_major": ["ETH", "SOL", "BNB", "XRP", "ADA", "TRX", "AVAX"],
    "l1_alt": ["DOT", "ATOM", "NEAR", "APT", "SUI", "SEI", "ICP", "HBAR", "VET", "MINA", "CFX", "TIA", "INJ", "HYPE"],
    "l2_scaling": ["ARB", "OP", "IMX", "LINEA", "STX"],
    "defi": ["UNI", "COMP", "LDO", "JUP", "JTO", "ENA", "PENDLE", "ETHFI", "ASTER", "WLFI"],
    "oracle_data_infra": ["LINK", "PYTH", "GRT", "FIL", "AR", "ENS", "JASMY"],
    "rwa": ["ONDO"],
    "ai": ["FET", "TAO", "WLD", "VIRTUAL"],
    "gaming_nft_fan": ["APE", "GALA", "BEAMX", "CHZ"],
    "meme": ["DOGE", "SHIB", "PEPE", "FLOKI", "BONK", "WIF", "BOME", "BRETT", "PIPPIN", "TRUMP", "MELANIA"],
    "platform_other": ["PUMP", "ORDI", "LIT", "RIVER"],   # LIT and RIVER: niche uncertain
}
COIN_NICHE = {c: k for k, v in NICHE.items() for c in v}
