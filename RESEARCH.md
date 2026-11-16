# Research protocol (read before changing any book)
1. Mechanism first: every hypothesis names who is on the other side and why they lose (forced, slow or uninformed flow). No pattern mining without a mechanism.
2. Cost gate: compute breakeven edge per trade (taker round trip is ~0.9%) before testing. Reject ideas that cannot clear it; prefer maker/low-turnover variants.
3. Pre-register in JOURNAL.md: rule, prediction with confidence, kill criterion, expected failure mode. Max 2 new hypotheses per week (multiple-testing budget).
4. Discover on history, confirm only on forward data. A book's rules are frozen once started; tweaks are new versions.
5. Robustness: run neighbouring parameters as shadow books; a real edge is stable across neighbours, an overfit one is a spike.
6. Skill vs luck: compare each book to random-timing books with the same exposure, and report alpha after regressing on BTC (beta stripped out).
7. Red team: before a book is promoted, a separate reviewer tries to break it (lookahead, survivorship, fee omission, regime dependence).
8. Score predictions: log predicted vs actual each week to calibrate confidence. Post-mortem every retired book.
9. Promote to a small live test only if it beats BTC hold risk-adjusted after fees, alpha is positive after beta, and shadow books agree.
10. Novelty gate: before testing a new idea, search papers/Quantpedia/SSRN/arXiv and record the verdict in NOVELTY.md. Public ideas run only as baselines or controls.
11. Run `python3 analysis.py` weekly; judge books by alpha after beta, rank vs random controls and neighbour stability, not raw return.
