"""Per-book return (USD-denominated books funded with GBP 1000 each), drawdown, trades and excess over BTC buy&hold measured from each book's own start."""
import csv, collections, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
by = collections.defaultdict(list)
for r in csv.DictReader(open(os.path.join(D, "equity.csv"))): by[r["book"]].append((r["time"], float(r["equity"])))
tp = os.path.join(D, "trades.csv"); nt = collections.Counter(r["book"] for r in csv.DictReader(open(tp))) if os.path.exists(tp) else {}
bench = dict(by.get("hold_btc@1", []))
print(f"{'book':12s} {'start':20s} {'return':>8s} {'vsBTC':>8s} {'maxDD':>7s} {'trades':>6s}")
for b, s in by.items():
    e = [x[1] for x in s]; pk = e[0]; dd = 0
    for x in e: pk = max(pk, x); dd = min(dd, x/pk-1)
    ret = e[-1]/e[0]-1; bm = (list(bench.values())[-1]/bench[s[0][0]]-1) if s[0][0] in bench and bench else float("nan")
    print(f"{b:12s} {s[0][0]:20s} {ret:8.2%} {ret-bm:8.2%} {dd:7.2%} {nt.get(b, 0):6d}")
