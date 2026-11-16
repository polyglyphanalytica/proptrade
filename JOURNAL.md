# Strategy journal
Rule: a live book's rules are frozen. To tweak, add a new version in `books.json` (new id, e.g. trend@2), retire the old one, and log the hypothesis, change and evidence here. Compare versions on forward data only, never on data used to design them.

## 2026-11-16 - launch
Books: hold_btc@1 (benchmark), trend@1 (SMA50 equal weight), mom@1 (30d, top 2), voltgt@1 (SMA50, 40% vol target), pullback@1 (buy 3d -5% dips above SMA100, hold 5d).
Features logged hourly to data/features.csv (spread, top-10 order book imbalance, 24h volume, BTC GBP/USD premium) to research signals from data Kraken does not archive.
Each book funded with GBP 1000 (converted to USD at Kraken GBPUSD at start; returns shown in USD terms).
Fees 0.40%/side taker + 0.05% slippage. None of these is a validated edge yet.
