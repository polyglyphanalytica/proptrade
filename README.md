# proptrade
Kraken paper-trading research book. Simulated only: public data, no API keys, no orders.
- `books.json`: live strategy versions (frozen once started; tweak by adding a new version)
- `paper.py`: runner (hourly via GitHub Actions); `report.py`: summary vs BTC buy&hold
- `data/`: equity.csv, trades.csv, features.csv (ledger and research data)
- `RESEARCH.md`: protocol for evolving strategies (read first)
- `JOURNAL.md`: hypotheses and changes. Not investment advice.

Capital: one funded strategy (fvq@1, GBP 1000 total). Shadow, control and benchmark books are counterfactual copies of that GBP 1000, not additional capital.
