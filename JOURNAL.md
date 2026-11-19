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

## 2026-11-19 - owner rules clarified
The "max 2 hypotheses per week" budget (RESEARCH.md) and the single-£1000 capital rule were set by the assistant, not the owner; both removed. Paper books are unlimited, each funded GBP 1000. Owner rules: public ideas are not traded (their alpha is gone); only FCA-permitted strategies (spot only; derivatives and prediction-market data may be read as signals).

## 2026-11-19 - new books (pre-registered)
- **fvp@1** (+~e90; control fvqp@1) - fvq rule, but fair value = Kraken Futures perpetual mid / GBPUSD instead of the USD spot mid; only pairs that have a perp (fvqp@1 = same pairs, spot anchor, isolating the anchor). Perps are read as data only; no derivatives traded. Mechanism: price discovery happens in perps first, so a perp anchor should leave fewer stale quotes for informed takers. Caveat: quotes are set hourly and the perp-spot gap at snapshot is ~1-10bp vs a 60bp edge, so the effect may be too small to see. Prediction 25%: fvp@1 beats fvqp@1 net of fees after 4 weeks with fewer adverse fills. Kill: no better than fvqp@1 after 4 weeks, or < 20 fills.
- **fvpx@1** (control fvqxp@1) - the same perp anchor on EUR/CAD/AUD/CHF legs, a direct test of whether fvqx@1's early losses (-4% in 2 days, 391 fills) come from a stale anchor. Prediction 20%: beats fvqxp@1. Kill as fvp@1.
- Wider neighbours of existing books (shadows, no new hypothesis): fvqx@1~e90/~e130 (does a wider edge stop the bleed?), fvq@1~v100 (more pairs: min volume £100), stale@1~d30 and ~h6 (deeper discount; 6h time stop), brr@1~d05 (-0.5% trigger, more events) and ~h8 (8h hold), lst@1~e30/~e80 (tighter/wider band).

## 2026-11-19 - Polymarket research and pmlvl@1 (pre-registered)
Polymarket is read as data only (FCA rule); the book trades Kraken spot BTC. Scripts in research/polymarket/.
History check: 23 monthly "What price will Bitcoin hit in <Month>?" ladders (Oct 2024 to Nov 2026), hourly prices per strike, against Kraken XBTUSD. For each day and each untouched strike, divergence = logit(Polymarket price) - logit(driftless touch probability from 30-day realised vol). Kept strikes with model probability 5-95%. n = 367 days.
- Polymarket overprices touches on average (down side +0.23 logit, up side +0.03), matching arXiv 2606.19517.
- Daily divergence vs next 1/3/7-day BTC return: all |rho| <= 0.08 against a noise band of about +/-0.10. The steadiest is level (mean of up and down) vs next day: +0.077 (halves +0.09/+0.08). Null by our standard.
- Hourly (last 30 days, 621 h): spot leads Polymarket (corr 0.33); Polymarket's move predicts next-hour spot weakly negative (t = -2.0), far too small to clear 0.9% round-trip costs.
- Token-event markets (airdrops, listings, ETFs) with Kraken-listed tokens: about 20 with real volume, too few to test.
- **pmlvl@1** - once per UTC day compute level from the live ladder (strikes untouched since each strike's listing day, >= 2 days to expiry); hold BTC when level > 0.40, go to cash when < -0.10 (the sample's quartiles; hysteresis to keep turnover low). In-sample after fees: -1.8% vs BTC +3.1% on the same days, halves -11.5%/+9.7%. Mechanism (weak): a crowd paying up for moves, especially downside, marks fear that reverts. Prediction 10%. Kill: after 8 weeks not ahead of hold_btc@1 net of fees. Expected failure: noise.
- **pmlvl@1~med** - shadow: in BTC when level > 0.195 (median), else cash. Higher turnover; failed the cost gate in-sample (-16% net).
- Polymarket level is logged hourly to data/polymarket.csv to build forward data. No signal when the month's ladder has < 2 days left, so the book holds its position.
