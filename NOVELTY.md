# Novelty check (search public sources before testing any idea; update when new ideas arise)
Checked 2026-11-16. A search can show an idea is public, never that it is novel; "not found" = candidate only.

| Idea | Public? | Notes / sources |
|---|---|---|
| Trend following (SMA filter) on crypto | **Public** (baseline) | Le & Ruthbah 2024 SMA rules on BTC/ETH (cxoadvisory.com/?p=45889); Rozario et al, "A Decade of Evidence of Trend Following in Cryptocurrencies" (arXiv 2009.12155) |
| Time-series / cross-sectional momentum, vol targeting | **Public** (baseline) | Momentum and vol-normalised signals in digital assets (journals.vu.lt BATP/44540); AdaptiveTrend (arXiv 2602.11708) |
| Buy dips in uptrend; BTC MIN/MAX reversal-continuation | **Public** (baseline) | Quantpedia, Trend-following and Mean-reversion in Bitcoin (quantpedia.com/?p=17895); altFINS pullback guides |
| Order book imbalance -> short-horizon returns | **Public**, and too fast for us | arXiv 2312.16190, 2602.00776 (1s data, Binance); edge is at second horizons; hourly sampling and 0.9% costs rule it out as a standalone signal |
| Cross-venue / cross-currency BTC premium (Kimchi, shadow FX) | **Partly public** | arXiv 2410.22443 (P2P premiums predict FX); Makarov & Schoar arbitrage paper (quantpedia.com/arbitrage-opportunities-in-cryptocurrency-markets). Not found: Kraken GBP vs USD premium as a *predictor of BTC returns or as a regime filter*; candidate only |

Verdict: the four live books and their shadows are public baselines and controls, not the novel strategy. Novelty candidates must come from the feature log (e.g. premium and imbalance as regime filters on a slow strategy, rather than fast standalone signals). Re-run this check before promoting any book.
