# funded risk plan (2026-11-21)

## Setup

Funded-account risk plan: 180 days from every Monday since 2023-11-20, no target, 5% daily limit, 8% floor
(fixed at the starting balance; after each payout the balance resets and the floor stays, so the cushion stays 8%).
Payout of any profit at the first weekly close at least 15 days after the previous payout; trader keeps 80%.
Books: 100K COMBO top 2+2, 50K CROWDFADE top 2+2 (no overlap), stop 3 ATR, TP 3R, weekly.
    python3 studies/funded.py

## Results

| account | risk/coin % | starts | breached within 180 days % | avg payout to you per month (USD) | median payout per month (USD) | worst 10% payout per month (USD) |
|---|---|---|---|---|---|---|
| 100K | 0.5 | 128 | 1 | 311 | 242 | 0 |
| 100K | 0.75 | 128 | 9 | 466 | 364 | 0 |
| 100K | 1.0 | 128 | 12 | 621 | 485 | 0 |
| 100K | 1.25 | 128 | 16 | 776 | 606 | 0 |
| 100K | 1.5 | 128 | 30 | 916 | 727 | 0 |
| 50K | 0.5 | 128 | 0 | 135 | 131 | 32 |
| 50K | 0.75 | 128 | 0 | 202 | 197 | 47 |
| 50K | 1.0 | 128 | 0 | 269 | 263 | 63 |
| 50K | 1.25 | 128 | 0 | 337 | 328 | 79 |
| 50K | 1.5 | 128 | 0 | 404 | 394 | 95 |
