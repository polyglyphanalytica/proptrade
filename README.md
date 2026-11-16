# proptrade
Kraken paper-trading research book. Simulated only: public data, no API keys, no orders.
- `books.json`: live strategy versions (frozen once started; tweak by adding a new version)
- `paper.py`: runner (hourly via GitHub Actions); `report.py`: summary vs BTC buy&hold
- `data/`: equity.csv, trades.csv, features.csv (ledger and research data)
- `RESEARCH.md`: protocol for evolving strategies (read first)
- `JOURNAL.md`: hypotheses and changes. Not investment advice.

Capital: every strategy book starts with GBP 1000 (simulated). Shadows, controls and benchmarks are counterfactual comparisons.
