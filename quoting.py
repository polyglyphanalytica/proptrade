"""Fair-value-anchored passive quoting on thin Kraken GBP legs (simulated).
Hypothesis: thin GBP pairs carry wide spreads because few makers serve them; anchoring quotes to the liquid USD leg
(fair = XUSD mid / GBPUSD mid) lets a small book earn spread with limited adverse selection. Capacity-limited by design.
Fill model (conservative): quotes are posted at run time and left unchanged until the next run; a bid fills only from
seller-initiated trades strictly BELOW it, an ask only from buyer-initiated trades strictly ABOVE it (full queue priority
is never assumed), fill size capped by that traded volume. Maker fee applied. Inventory marked at fair value."""
import json, time, urllib.request
MAKER = 0.0025
def _get(path):
    for _ in range(3):
        try:
            r = json.load(urllib.request.urlopen("https://api.kraken.com/0/public/" + path, timeout=20))
            if not r["error"]: return r["result"]
        except Exception: pass
        time.sleep(2)
    raise RuntimeError(path)
def universe(min_spread_bp, min_vol_gbp):
    ap = _get("AssetPairs"); usd = {}; gbp = {}
    for k, v in ap.items():
        if k.endswith(".d") or v.get("status", "online") != "online": continue
        if v["quote"] == "ZUSD": usd[v["base"]] = k
        if v["quote"] in ("ZGBP", "GBP"): gbp[v["base"]] = k
    skip = {"XXBT", "XETH", "USDC", "USDT", "ZEUR"}
    base = [b for b in gbp if b in usd and b not in skip]
    tk = _get("Ticker?pair=" + ",".join(gbp[b] for b in base) + "," + ",".join(usd[b] for b in base) + ",ZGBPZUSD")
    out = {}
    for b in base:
        tg, tu = tk.get(gbp[b]), tk.get(usd[b])
        if not tg or not tu: continue
        bid, ask = float(tg["b"][0]), float(tg["a"][0]); mid = (bid + ask) / 2
        if bid <= 0 or ask <= 0: continue
        sp = (ask - bid) / mid * 1e4; vol = float(tg["v"][1]) * float(tg["c"][0])
        out[b] = dict(eligible=sp >= min_spread_bp and vol >= min_vol_gbp, gbp=gbp[b], usd=usd[b], bid=bid, ask=ask, umid=(float(tu["b"][0]) + float(tu["a"][0])) / 2, spread_bp=sp, vol=vol)
    fx = tk["ZGBPZUSD"]; gbpusd = (float(fx["b"][0]) + float(fx["a"][0])) / 2
    for b in out: out[b]["fair"] = out[b]["umid"] / gbpusd
    return out, gbpusd
def trades_since(pair, since):
    r = _get(f"Trades?pair={pair}&since={since}"); k = [x for x in r if x != "last"][0]; time.sleep(1.1)
    return [(float(t[0]), float(t[1]), t[3]) for t in r[k]], r["last"]
def step(book, s, U, gbpusd, now, trades_out):
    """book params: edge (fraction from anchor), size_gbp, max_inv_gbp, anchor ('fair' or 'book'), skew."""
    p = book["params"]; s.setdefault("q", {}); s.setdefault("inv", {}); s.setdefault("since", {})
    # 1) settle fills on quotes posted last run
    for b, q in list(s["q"].items()):
        pair = q["pair"]
        try: tr, last = trades_since(pair, s["since"].get(pair, q["since"]))
        except Exception: continue
        s["since"][pair] = last
        for px, v, side in tr:
            if side == "s" and q["bid_qty"] > 0 and px < q["bid"]:
                f = min(v, q["bid_qty"]); q["bid_qty"] -= f; n = f * q["bid"]
                s["cash"] -= n * (1 + MAKER); s["inv"][b] = s["inv"].get(b, 0) + f
                trades_out.append([now, book["id"], "buy", pair, round(f, 8), q["bid"], round(n * MAKER, 4)])
            elif side == "b" and q["ask_qty"] > 0 and px > q["ask"] and s["inv"].get(b, 0) > 0:
                f = min(v, q["ask_qty"], s["inv"][b]); q["ask_qty"] -= f; n = f * q["ask"]
                s["cash"] += n * (1 - MAKER); s["inv"][b] -= f
                trades_out.append([now, book["id"], "sell", pair, round(f, 8), q["ask"], round(n * MAKER, 4)])
    # 2) post fresh quotes
    s["q"] = {}
    for b, u in U.items():
        if not u["eligible"] and s["inv"].get(b, 0) <= 0: continue
        anchor = u["fair"] if p["anchor"] == "fair" else (u["bid"] + u["ask"]) / 2
        inv_gbp = s["inv"].get(b, 0) * anchor; sk = p["skew"] * inv_gbp / p["max_inv_gbp"]   # lean against inventory
        bid = anchor * (1 - p["edge"] - sk); ask = anchor * (1 + p["edge"] - sk)
        bid = min(bid, u["ask"] * (1 - 1e-4)); ask = max(ask, u["bid"] * (1 + 1e-4))       # never cross the book
        room = max(0.0, p["max_inv_gbp"] - inv_gbp) if u["eligible"] else 0.0; bq = min(p["size_gbp"], room, max(0.0, s["cash"])) / bid
        aq = min(p["size_gbp"] / ask, s["inv"].get(b, 0))
        if bq > 0 or aq > 0:
            s["since"].setdefault(u["gbp"], str(time.time_ns()))
            s["q"][b] = dict(pair=u["gbp"], bid=round(bid, 8), ask=round(ask, 8), bid_qty=bq, ask_qty=aq, since=s["since"][u["gbp"]])
    # 3) mark to fair (GBP), report in USD for comparability with other books
    for b in list(s["inv"]):
        if b not in U and s["inv"][b] > 0: s.setdefault("stale_mark", {})[b] = True
    mark = sum(q * U[b]["fair"] for b, q in s["inv"].items() if b in U) + sum(q * s.get("last_fair", {}).get(b, 0) for b, q in s["inv"].items() if b not in U)
    s["last_fair"] = {**s.get("last_fair", {}), **{b: U[b]["fair"] for b in U}}
    return (s["cash"] + mark) * gbpusd, s["cash"] * gbpusd
