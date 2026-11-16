# Strategy journal
Rule: a live book's rules are frozen. To tweak, add a new version in `books.json` (new id, e.g. trend@2), retire the old one, and log the hypothesis, change and evidence here. Compare versions on forward data only, never on data used to design them.

## 2026-11-16 - launch
Books: hold_btc@1 (benchmark), trend@1 (SMA50 equal weight), mom@1 (30d, top 2), voltgt@1 (SMA50, 40% vol target), pullback@1 (buy 3d -5% dips above SMA100, hold 5d).
Features logged hourly to data/features.csv (spread, top-10 order book imbalance, 24h volume, BTC GBP/USD premium) to research signals from data Kraken does not archive.
Each book funded with GBP 1000 (converted to USD at Kraken GBPUSD at start; returns shown in USD terms).
Fees 0.40%/side taker + 0.05% slippage. None of these is a validated edge yet.

## 2026-11-16 - pivot: public strategies abandoned
All public books retired before start (see NOVELTY.md). Directional fiat-leg signals tested null on 720 days of Kraken data.
Pre-registered H1 (fvq@1): passive two-sided quotes +/-0.60% around fair value (USD-leg mid / GBPUSD) on GBP pairs with spread >= 40bp and 24h volume >= £300; £50 clips, £150 max inventory per pair, inventory skew; maker fee 0.25%; conservative fills (trades strictly through our price).
- Mechanism: few makers serve thin GBP legs; retail takers there pay wide spreads; anchoring to the liquid leg limits being picked off.
- Prediction (confidence 30%): after 4 weeks fvq@1 has positive net P&L after fees, beats bookq@1, and shadows e40/e90/e130 agree in sign.
- Kill: net P&L negative after 4 weeks, or losses dominated by fills that preceded adverse fair-value moves (adverse selection), or fewer than 20 fills (untestable).
- Expected failure mode: the wide spread exists because the takers are informed arbitrageurs, so our fills are adverse; or volume is too low to fill.
Benchmark hold_btc@1 kept. Directional random controls retired (no directional books left).
