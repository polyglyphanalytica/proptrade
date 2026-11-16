"""Kraken paper trader (simulated only; public data, no keys). Runs hourly.
Books come from books.json; signals use completed daily candles; fills use live bid/ask + fee + slippage.
Also logs market features each run (data/features.csv) to research novel signals from data Kraken doesn't archive."""
import json, csv, os, time, urllib.request, datetime as dt
ROOT = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(ROOT, "data")
PAIRS = {"BTC": "XBTUSD", "ETH": "ETHUSD", "SOL": "SOLUSD"}
START_GBP = 1000.0   # each book is funded with GBP 1000, converted to USD at Kraken's GBPUSD when the book starts
FEE = float(os.getenv("FEE_TAKER", "0.004")); SLIP = float(os.getenv("SLIPPAGE", "0.0005")); MIN_TRADE = 0.01
def get(path, **q):
    url = "https://api.kraken.com/0/public/" + path + "?" + "&".join(f"{k}={v}" for k, v in q.items())
    for _ in range(3):
        try:
            r = json.load(urllib.request.urlopen(url, timeout=20))
            if not r["error"]: return r["result"]
        except Exception: pass
        time.sleep(2)
    raise RuntimeError("kraken " + path + " failed")
def closes(pair):
    r = get("OHLC", pair=pair, interval=1440); k = [x for x in r if x != "last"][0]
    return [float(c[4]) for c in r[k][:-1]]
def quote(pair):
    t = list(get("Ticker", pair=pair).values())[0]; return float(t["b"][0]), float(t["a"][0]), float(t["v"][1])
sma = lambda x, n: sum(x[-n:]) / n
def vol(x, n=30):
    r = [x[i]/x[i-1]-1 for i in range(len(x)-n, len(x))]; m = sum(r)/n
    return (sum((a-m)**2 for a in r)/(n-1))**.5 * 365**.5
# ---- strategy library: f(closes, params, state) -> target weights. Add new ones here, version via books.json ----
def hold(c, p, s): return {p["asset"]: 1.0}
def trend(c, p, s): return {a: 1/len(c) for a in c if c[a][-1] > sma(c[a], p["sma"])}
def momentum(c, p, s):
    n = p["lookback"]; sc = {a: c[a][-1]/c[a][-n-1]-1 for a in c}; top = sorted(sc, key=sc.get, reverse=True)[:p["top"]]
    return {a: 1/p["top"] for a in top if sc[a] > 0}
def voltarget(c, p, s):
    return {a: min(1.0, p["target"]/vol(c[a]))/len(c) for a in c if c[a][-1] > sma(c[a], p["sma"])}
def pullback(c, p, s):           # buy sharp dips inside an uptrend, exit after hold_days or trend break
    held = s.setdefault("held", {}); w = {}; today = int(time.time()//86400)
    for a in c:
        x = c[a]
        if x[-1] < sma(x, p["sma"]): held.pop(a, None); continue
        if a in held and today - held[a] < p["hold_days"]: w[a] = 1/len(c); continue
        held.pop(a, None)
        if x[-1]/x[-1-p["days"]]-1 <= p["dip"]: held[a] = today; w[a] = 1/len(c)
    return w
def randtime(c, p, s):          # control: random on/off by UTC day, equal weight, same coins; skill must beat this
    import hashlib; day = int(time.time()//86400); h = int(hashlib.sha256(f"{p['seed']}-{day}".encode()).hexdigest(), 16) % 1000 / 1000
    return {a: 1/len(c) for a in c} if h < p["p"] else {}
def brr(c, p, s):                # buy BTC after a sharp fall in the 15:00-16:00 London benchmark window; hold hold_h hours
    from zoneinfo import ZoneInfo
    L = dt.datetime.now(ZoneInfo("Europe/London")); t = time.time()
    if t < s.get("until", 0): return {"BTC": 1.0}
    day = L.strftime("%Y-%m-%d")
    if 16 <= L.hour < 18 and s.get("checked") != day:
        s["checked"] = day; r = get("OHLC", pair="XBTUSD", interval=60); k = [x for x in r if x != "last"][0]
        w0 = int(L.replace(hour=15, minute=0, second=0, microsecond=0).timestamp())
        bar = [x for x in r[k] if int(x[0]) == w0]
        if bar:
            ret = float(bar[0][4]) / float(bar[0][1]) - 1; s.setdefault("windows", []).append([day, round(ret, 5)])
            if ret <= p["drop"]: s["until"] = t + p["hold_h"] * 3600; return {"BTC": 1.0}
    return {}
def monthend(c, p, s):           # hold BTC, but stay in cash from the 25th to the 1st (London date)
    from zoneinfo import ZoneInfo
    d = dt.datetime.now(ZoneInfo("Europe/London")).day
    return {} if (d >= p["from_day"] or d <= p["to_day"]) else {"BTC": 1.0}
STRATS = dict(brr=brr, monthend=monthend, randtime=randtime, hold=hold, trend=trend, momentum=momentum, voltarget=voltarget, pullback=pullback)
def log_features(now, Q, C):
    ob = {}
    for a, p in PAIRS.items():
        d = list(get("Depth", pair=p, count=10).values())[0]
        bv = sum(float(x[1]) for x in d["bids"]); av = sum(float(x[1]) for x in d["asks"]); ob[a] = (bv-av)/(bv+av)
    row = [now]
    for a in PAIRS: row += [round((Q[a][0]+Q[a][1])/2, 4), round((Q[a][1]-Q[a][0])/Q[a][0], 6), round(ob[a], 4), round(Q[a][2], 2)]
    try:    # GBP/USD premium: BTC priced in GBP vs USD price converted at Kraken's GBPUSD
        g = quote("GBPUSD"); gm = (g[0]+g[1])/2; b = quote("XBTGBP"); row.append(round(((b[0]+b[1])/2)*gm/((Q["BTC"][0]+Q["BTC"][1])/2)-1, 6))
    except Exception: row.append("")
    p = os.path.join(D, "features.csv"); new = not os.path.exists(p)
    with open(p, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["time"] + [f"{a}_{k}" for a in PAIRS for k in ("mid", "spread", "obi10", "vol24h")] + ["btc_gbp_prem"])
        w.writerow(row)
def log_thin(now, U):
    p = os.path.join(D, "thin.csv"); new = not os.path.exists(p)
    with open(p, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["time", "base", "pair", "spread_bp", "vol24h_usd", "book_mid_vs_fair_bp"])
        for b, u in U.items():
            if u["spread_bp"] >= 25: w.writerow([now, u["base"], b, round(u["spread_bp"], 1), round(u["vol_usd"]), round(((u["bid"]+u["ask"])/2/u["fair"]-1)*1e4, 1)])
def main():
    os.makedirs(D, exist_ok=True); sp = os.path.join(D, "state.json")
    books = json.load(open(os.path.join(ROOT, "books.json"))); st = json.load(open(sp)) if os.path.exists(sp) else {}
    C = {a: closes(p) for a, p in PAIRS.items()}; Q = {a: quote(p) for a, p in PAIRS.items()}
    g = quote("GBPUSD"); gbpusd = (g[0]+g[1])/2
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"); trades = []; eq = []; changed = False
    SPECIAL = ("quote", "stale", "lst")
    QB = [b for b in books["books"] if b["status"] != "retired" and b["strategy"] in ("quote", "stale")]
    if QB:
        import quoting
        ccys = sorted({c for b in QB for c in b["params"]["ccys"]} | {"GBP"})
        try: U, fx = quoting.universe(ccys)
        except Exception as e: U = None; print("quote universe failed", e)
        if U is not None:
            for b in QB:
                s = st.setdefault(b["id"], {})
                if b["started"] is None: b["started"] = now; changed = True
                fn = quoting.quote_step if b["strategy"] == "quote" else quoting.stale_step
                try: V, cash = fn(b, s, U, fx, now, trades)
                except Exception as e: print(b["id"], "failed", e); continue
                eq.append([now, b["id"], round(V, 2), round(cash, 2), 0, 0, 0])
            log_thin(now, U)
    for b in [b for b in books["books"] if b["status"] != "retired" and b["strategy"] == "lst"]:
        import lst
        s = st.setdefault(b["id"], {})
        if b["started"] is None: b["started"] = now; changed = True
        try: V, cash = lst.step({**b, "params": {**b["params"], "_gbp_usd": gbpusd}}, s, now, trades)
        except Exception as e: print(b["id"], "failed", e); continue
        eq.append([now, b["id"], round(V, 2), round(cash, 2), 0, 0, 0])
    for b in books["books"]:
        if b["status"] == "retired" or b["strategy"] in SPECIAL: continue
        s = st.setdefault(b["id"], {"cash": START_GBP*gbpusd, "pos": {}, "start": now, "gbpusd0": gbpusd})
        if b["started"] is None: b["started"] = now; changed = True
        mid = {a: (Q[a][0]+Q[a][1])/2 for a in Q}
        V = s["cash"] + sum(q*mid[a] for a, q in s["pos"].items()); w = STRATS[b["strategy"]](C, b["params"], s)
        want = {a: w.get(a, 0)*V for a in PAIRS}; have = {a: s["pos"].get(a, 0)*mid[a] for a in PAIRS}
        for side in ("sell", "buy"):
            for a in PAIRS:
                diff = want[a]-have[a]; closing = w.get(a, 0) == 0 and have[a] > 0
                if abs(diff) < MIN_TRADE*V and not closing: continue
                if side == "sell" and diff < 0:
                    px = Q[a][0]*(1-SLIP); qty = min(s["pos"].get(a, 0), -diff/mid[a]); n = qty*px
                    s["cash"] += n*(1-FEE); s["pos"][a] = s["pos"].get(a, 0)-qty
                elif side == "buy" and diff > 0:
                    px = Q[a][1]*(1+SLIP); n = min(diff, s["cash"]/(1+FEE))
                    if n <= 0: continue
                    qty = n/px; s["cash"] -= n*(1+FEE); s["pos"][a] = s["pos"].get(a, 0)+qty
                else: continue
                trades.append([now, b["id"], side, a, round(qty, 8), round(px, 4), round(n*FEE, 4)])
        V = s["cash"] + sum(q*mid[a] for a, q in s["pos"].items())
        eq.append([now, b["id"], round(V, 2), round(s["cash"], 2)] + [round(s["pos"].get(a, 0), 8) for a in PAIRS])
    json.dump(st, open(sp, "w"), indent=1)
    if changed: json.dump(books, open(os.path.join(ROOT, "books.json"), "w"), indent=1)
    for name, rows, hdr in (("trades.csv", trades, ["time", "book", "side", "asset", "qty", "price", "fee"]),
                            ("equity.csv", eq, ["time", "book", "equity", "cash"] + list(PAIRS))):
        p = os.path.join(D, name); new = not os.path.exists(p)
        with open(p, "a", newline="") as f:
            w_ = csv.writer(f)
            if new: w_.writerow(hdr)
            w_.writerows(rows)
    log_features(now, Q, C)
    print(now, {r[1]: r[2] for r in eq}, len(trades), "trades")
if __name__ == "__main__": main()
