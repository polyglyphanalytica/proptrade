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

## 2026-11-16 - capital rule
Only one funded strategy: fvq@1 with £1000 total (shared across all pairs it quotes). Shadows (fvq@1~*), the control (bookq@1) and the benchmark (hold_btc@1) are counterfactual measurements of that same £1000, not extra capital, and are never summed into P&L. A new strategy only gets funding by replacing fvq@1, still within £1000.

## 2026-11-16 - capital rule revised
Simulated capital is free: every strategy book gets GBP 1000 (supersedes the single-strategy rule above).

## 2026-11-16 - new books (pre-registered)
History checks run before setting rules (Kraken public data): benchmark window 30 days hourly; month-end 720 days daily; staked-token ratios 720 days. Thresholds set from the cost gate, not fitted.
- **fvqx@1** - fvq rule on thin EUR/CAD/AUD/CHF legs (GBP 1000 split, 0.2% FX fee, top 40 pairs by volume). Mechanism as fvq. Prediction 30%: positive net after fees. Kill: negative after 4 weeks or adverse-selection dominated.
- **stale@1** (+~d20) - take thin-leg asks >=1.2% (2.0%) below USD-leg fair value; exit passively at fair, or taker after 24h. Mechanism: slow or panicking quoters on thin legs leave stale offers after USD moves. Prediction 25%: positive per-trade edge after taker fee. Failure mode: discount reflects real information or the fair leg moved; hourly sampling sees few events.
- **brr@1** (+~d10, ~d20) - after the 15:00-16:00 London BTC benchmark-fixing hour falls <= -1.5%, buy BTC and hold 4h. Mechanism: fixing-window flow from ETF/CME-linked trading is non-informational and reverts. History: window hour vol ~2x other hours; corr(window, next 4h) = -0.50 over 30 days (n tiny; overlaps US equity open). Prediction 30%. Kill: average post-window return after fees <= 0 on >= 5 events. Novelty not yet checked against public sources.
- **monthend@1** - hold BTC except from the 25th to the 1st (London). Mined, weak mechanism: original UK-payday-buying hypothesis was contradicted (BTC/GBP averaged -26bp/day on those days vs +1bp otherwise over ~24 months; GBP volume 13% lower). Prediction 15%. Expect it to be noise.
- **lst@1** - quote mETH/ETH +/-0.5% around its 30-day log-linear ratio trend (the only staked-token pair on Kraken with real volume, spread ~68bp). Controls: lsthold@1 (always hold mETH) and hold_eth@1. Prediction 25%: beats lsthold. Failure: trend is a poor proxy for redemption value; too few fills.
Dropped: tokenized-stock weekend gaps (no xStocks on Kraken's public API); listing/delisting flows (partly published, needs an announcements feed); selling retail spikes on thin legs (needs shorting).
