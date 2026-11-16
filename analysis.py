"""Skill vs luck. Reads data/*.csv (stdlib only). Prints: per-book return, alpha/beta vs BTC hold (hourly OLS), rank vs random-timing
controls, parameter-neighbour stability, and whether logged features predict next-day BTC return (Spearman, with n)."""
import csv, collections, os, statistics as S
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
eq = collections.defaultdict(list)
for r in csv.DictReader(open(os.path.join(D, "equity.csv"))): eq[r["book"]].append((r["time"], float(r["equity"])))
rets = {b: {t: v/p[1]-1 for (t, v), p in zip(s[1:], s[:-1])} for b, s in eq.items() if len(s) > 2}
def ols(y, x):
    mx, my = S.mean(x), S.mean(y); vx = sum((a-mx)**2 for a in x)
    b = sum((a-mx)*(c-my) for a, c in zip(x, y))/vx if vx else 0; return my-b*mx, b
bench = rets.get("hold_btc@1", {}); tot = {b: s[-1][1]/s[0][1]-1 for b, s in eq.items()}
ctl = sorted(v for b, v in tot.items() if b.startswith("rand@"))
print(f"{'book':20s} {'ret':>7s} {'alpha/day':>10s} {'beta':>5s} {'vs ctl':>8s}  (alpha = excess return after stripping BTC beta)")
for b in sorted(eq):
    if b == "hold_btc@1" or len(eq[b]) < 3: continue
    ts = [t for t in rets[b] if t in bench]; a, be = ols([rets[b][t] for t in ts], [bench[t] for t in ts]) if len(ts) > 24 else (float("nan"),)*2
    rk = f"{sum(c < tot[b] for c in ctl)}/{len(ctl)}" if ctl and not b.startswith("rand@") else "-"
    print(f"{b:20s} {tot[b]:7.2%} {a*24:10.3%} {be:5.2f} {rk:>8s}")
print("\nStability (neighbours of each base book; a real edge is flat across neighbours, an overfit one spikes):")
for base in sorted({b.split("~")[0] for b in tot if "~" in b and not b.startswith("rand@")}):
    g = {b: tot[b] for b in tot if b.split("~")[0] == base}; v = list(g.values())
    print(f"  {base}: min {min(v):.2%} max {max(v):.2%} spread {max(v)-min(v):.2%}  n={len(v)}")
fp = os.path.join(D, "features.csv")
if os.path.exists(fp):
    F = list(csv.DictReader(open(fp))); day = collections.defaultdict(list)
    for r in F: day[r["time"][:10]].append(r)
    ds = sorted(day); mid = {d: float(day[d][-1]["BTC_mid"]) for d in ds}
    def rank(x): o = sorted(range(len(x)), key=x.__getitem__); r = [0]*len(x); [r.__setitem__(i, k) for k, i in enumerate(o)]; return r
    def sp(x, y): rx, ry = rank(x), rank(y); return ols(ry, rx)[1]*S.pstdev(rx)/S.pstdev(ry) if len(x) > 3 and S.pstdev(ry) else float("nan")
    print(f"\nFeature -> next-day BTC return (Spearman, n={len(ds)-1} days; |rho| < ~{2/max(len(ds)-1,1)**.5:.2f} is noise):")
    for k in ("BTC_obi10", "ETH_obi10", "BTC_spread", "btc_gbp_prem"):
        x = [S.mean(float(r[k]) for r in day[d] if r[k] != "") for d in ds[:-1] if any(r[k] != "" for r in day[d])]
        y = [mid[ds[i+1]]/mid[ds[i]]-1 for i in range(len(ds)-1) if any(r[k] != "" for r in day[ds[i]])]
        print(f"  {k:14s} rho={sp(x, y):6.2f}" if len(x) > 3 else f"  {k:14s} too little data ({len(x)} days)")
