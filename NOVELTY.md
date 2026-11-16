# Novelty check
A search can show an idea is public, never prove it novel. Public ideas are not traded here.

## Abandoned 2026-11-16 (public)
- Trend/SMA, time-series & cross-sectional momentum, vol targeting, dip-buying: extensively published (Le & Ruthbah 2024; Rozario et al. arXiv 2009.12155; Quantpedia BTC MIN/MAX; arXiv 2602.11708).
- Order book imbalance: published (arXiv 2312.16190, 2602.00776); works at second horizons only.
- Cross-exchange / cross-fiat BTC price dispersion and arbitrage: published (Makarov & Schoar; Borri & Shakhnov 2023; arXiv 2510.14435 runs a CARB strategy using Kraken as benchmark).
- USDT peg premium as a regime signal: published (Research Square rs-10129317; Boido & Jones 2026 preprint).

## Own tests on Kraken history (2024-11-26 to 2026-11-15, daily; 721h hourly)
- GBP and EUR leg premium, cross-fiat dispersion, USDT/USDC premia, ETH GBP-leg premium, local-currency volume share vs next-1d/7d BTC return, next-7d vol and ETH/BTC: all |rho| inside the noise band or sign-unstable across halves. No directional edge.
- BTC GBP-vs-USD leg mispricing hourly: median 4.7bp, p95 23bp, half-life ~0.2h; only 2 of 721 hours exceed 3-leg taker costs. Uncapturable hourly.
- Thin GBP pairs (GRT, MINA, FIL, AAVE, BCH...) show 35-110bp+ spreads on hundreds to thousands of £/day. Capacity-limited: irrelevant to funds, relevant to a £1000 book.

## Live candidate
- fvq: passive quotes on thin GBP legs anchored to the liquid USD leg's fair value. Market making in general is public; the claim is not secrecy but capacity (an edge too small for anyone else to bother with). Control bookq anchors to the GBP book instead; if fvq does not beat bookq, the fair-value idea adds nothing.
