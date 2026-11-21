# Prop account rules this lab designs for (Bitfunded 50K two-step, as provided by the user on 2026-11-21)

✔ = confirmed by the user · ❓ = assumption, not verified against the firm's website.

| rule | stage 1 | stage 2 | funded |
|---|---|---|---|
| profit target | +8% ($4,000) | +5% ($2,500) | none |
| max daily loss | 5% | 5% | 5% |
| max total loss | 10% (floor $45,000) | 8% (floor $46,000) | 8% |

- Daily reset 00:00 Singapore time (16:00 UTC). Loss limits include open (floating) losses.
- Max-loss floor fixed at the starting balance ❓. Profit target counts closed trades only ❓.
- Leverage up to 5x. Fees 0.04% per side; **no funding or overnight costs** ✔.
- **Max 5 open positions**, total margin under 65% of the account.
- **Max hold: 10 days for majors** (BTC ETH BNB XRP SOL TRX HYPE ZEC DOGE ADA), **7 days for other coins**.
- At least 2 closed trades per stage, each held 10+ minutes.
- **A stop-loss and take-profit on every trade.** No hedging (opposite positions on the same coin).
- Max position size per coin is a fixed dollar amount (e.g. LTC $80k, LINK $50k); not binding at the sizes used here.
- Weekend holding allowed ✔. No stage time limit known ❓.
- Funded: 80% split, payout every 15 days ❓.

## What this means for strategy design
1. **Max 5 positions:** the 14-coin basket books can't be traded; they need compact versions (2-5 coins).
2. **Stop + target on every trade:** each position gets a stop at entry and a (wide) take-profit.
3. **7-day hold:** weekly books close every position at the rebalance and reopen (full turnover costs each week).
4. **No funding:** basket results are re-run without funding.
5. **Loss limits:** size so that a bad day can't break the 5% daily limit; judge by a challenge simulation
   (chance to reach +8% before -10% / -5% daily, and how long it takes), not only by Sharpe.
