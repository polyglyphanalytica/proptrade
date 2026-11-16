"""Passive quoting and stale-quote taking on thin Kraken fiat legs (simulated only).
Fair value of a thin pair BASE/CCY = mid(BASE/USD) / mid(CCY in USD). Cash is held per quote currency.
Fill model (conservative): quotes stay fixed until the next run; a bid fills only from seller-initiated trades strictly
below it, an ask only from buyer-initiated trades strictly above it, size capped by that traded volume. Maker 0.25%, taker 0.40%."""
import json, time, urllib.request
MAKER, TAKER, FXFEE = 0.0025, 0.004, 0.002
FXP = {"GBP": ("ZGBPZUSD", False), "EUR": ("ZEURZUSD", False), "AUD": ("AUDUSD", False), "CAD": ("ZUSDZCAD", True), "CHF": ("USDCHF", True)}
QC = {"ZGBP": "GBP", "GBP": "GBP", "ZEUR": "EUR", "EUR": "EUR", "ZAUD": "AUD", "AUD": "AUD", "ZCAD": "CAD", "CAD": "CAD", "CHF": "CHF"}
def get(path):
    for _ in range(3):
        try:
            r = json.load(urllib.request.urlopen("https://api.kraken.com/0/public/" + path, timeout=25))
            if not r["error"]: return r["result"]
        except Exception: pass
        time.sleep(2)
    raise RuntimeError(path)
def mid(t): return (float(t["b"][0]) + float(t["a"][0])) / 2
def universe(ccys):
    ap = get("AssetPairs"); usd = {}; thin = []
    for k, v in ap.items():
        if k.endswith(".d") or v.get("status", "online") != "online": continue
        if v["quote"] == "ZUSD": usd[v["base"]] = k
        if QC.get(v["quote"]) in ccys: thin.append((k, v["base"], QC[v["quote"]]))
    skip = {"XXBT", "XETH", "USDC", "USDT", "ZEUR", "ZGBP", "ZUSD"}
    thin = [x for x in thin if x[1] in usd and x[1] not in skip]
    names = sorted({x[0] for x in thin} | {usd[x[1]] for x in thin} | {FXP[c][0] for c in ccys})
    tk = {}
    for i in range(0, len(names), 80): tk.update(get("Ticker?pair=" + ",".join(names[i:i+80]))); time.sleep(1)
    fx = {c: (1 / mid(tk[FXP[c][0]]) if FXP[c][1] else mid(tk[FXP[c][0]])) for c in ccys}   # USD per 1 unit of ccy
    U = {}
    for k, b, c in thin:
        tg, tu = tk.get(k), tk.get(usd[b])
        if not tg or not tu: continue
        bid, ask = float(tg["b"][0]), float(tg["a"][0])
        if bid <= 0 or ask <= 0: continue
        m = (bid + ask) / 2; um = mid(tu)
        U[k] = dict(pair=k, base=b, ccy=c, bid=bid, ask=ask, fair=um / fx[c], spread_bp=(ask - bid) / m * 1e4,
                    vol_usd=float(tg["v"][1]) * float(tg["c"][0]) * fx[c])
    return U, fx
def trades_since(pair, since):
    r = get(f"Trades?pair={pair}&since={since}"); k = [x for x in r if x != "last"][0]; time.sleep(1.1)
    return [(float(t[0]), float(t[1]), t[3]) for t in r[k]], r["last"]
def _init(s, p, fx, now):
    if "cash" in s: return
    c = p["ccys"]; s.update(cash={}, inv={}, q={}, since={}, start=now, mark={})
    for x in c:   # GBP 1000 split equally; non-GBP slices pay an FX conversion fee
        gbp = 1000.0 / len(c); s["cash"][x] = gbp * fx["GBP"] / fx[x] * (1 if x == "GBP" else 1 - FXFEE)
def _settle(book, s, now, out):
    for k, q in list(s["q"].items()):
        try: tr, last = trades_since(k, s["since"].get(k, q["since"]))
        except Exception: continue
        s["since"][k] = last
        for px, v, side in tr:
            if side == "s" and q["bid_qty"] > 0 and px < q["bid"]:
                f = min(v, q["bid_qty"]); q["bid_qty"] -= f; n = f * q["bid"]
                s["cash"][q["ccy"]] -= n * (1 + MAKER); s["inv"][k] = s["inv"].get(k, 0) + f
                s.setdefault("opened", {}).setdefault(k, now); out.append([now, book["id"], "buy", k, round(f, 8), q["bid"], round(n * MAKER, 6)])
            elif side == "b" and q["ask_qty"] > 0 and px > q["ask"] and s["inv"].get(k, 0) > 0:
                f = min(v, q["ask_qty"], s["inv"][k]); q["ask_qty"] -= f; n = f * q["ask"]
                s["cash"][q["ccy"]] += n * (1 - MAKER); s["inv"][k] -= f
                if s["inv"][k] <= 1e-12: s["inv"].pop(k); s.get("opened", {}).pop(k, None)
                out.append([now, book["id"], "sell", k, round(f, 8), q["ask"], round(n * MAKER, 6)])
    s["q"] = {}
def _value(s, U, fx):
    for k in U: s["mark"][k] = U[k]["fair"] * fx[U[k]["ccy"]]
    return sum(v * fx[c] for c, v in s["cash"].items()) + sum(q * s["mark"].get(k, 0) for k, q in s["inv"].items())
def quote_step(book, s, U, fx, now, out):
    """Two-sided passive quotes around an anchor. params: ccys, edge, size_gbp, max_inv_gbp, skew, min_spread_bp, min_vol_gbp, anchor."""
    p = book["params"]; _init(s, p, fx, now); _settle(book, s, now, out)
    ok = [k for k, u in U.items() if u["ccy"] in p["ccys"] and u["spread_bp"] >= p["min_spread_bp"] and u["vol_usd"] >= p["min_vol_gbp"] * fx["GBP"]]
    ok = set(sorted(ok, key=lambda k: -U[k]["vol_usd"])[:p.get("max_pairs", 40)])     # cap API calls / runtime
    for k, u in U.items():
        if u["ccy"] not in p["ccys"]: continue
        elig = k in ok
        held = s["inv"].get(k, 0)
        if not elig and held <= 0: continue
        a = u["fair"] if p["anchor"] == "fair" else (u["bid"] + u["ask"]) / 2
        g = fx[u["ccy"]] / fx["GBP"]                                    # GBP per unit of ccy
        inv_gbp = held * a * g; sk = p["skew"] * inv_gbp / p["max_inv_gbp"]
        bid = min(a * (1 - p["edge"] - sk), u["ask"] * (1 - 1e-4)); ask = max(a * (1 + p["edge"] - sk), u["bid"] * (1 + 1e-4))
        room = max(0.0, p["max_inv_gbp"] - inv_gbp) if elig else 0.0
        bq = max(0.0, min(p["size_gbp"], room, s["cash"].get(u["ccy"], 0) * g)) / g / bid
        aq = min(p["size_gbp"] / g / ask, held)
        if bq > 0 or aq > 0:
            s["since"].setdefault(k, str(time.time_ns()))
            s["q"][k] = dict(ccy=u["ccy"], bid=round(bid, 10), ask=round(ask, 10), bid_qty=bq, ask_qty=aq, since=s["since"][k])
    V = _value(s, U, fx); return V, sum(v * fx[c] for c, v in s["cash"].items())
def stale_step(book, s, U, fx, now, out):
    """Take thin-leg asks that sit far below fair (stale or panic quotes); exit passively at fair, or by taker after max_hold_h.
    params: ccys, discount, size_gbp, max_hold_h."""
    p = book["params"]; _init(s, p, fx, now); _settle(book, s, now, out)
    t = time.time()
    for k in list(s["inv"]):
        u = U.get(k)
        if not u: continue
        age = (t - s.get("opened_ts", {}).get(k, t)) / 3600
        if age >= p["max_hold_h"] or u["bid"] >= u["fair"]:              # time stop, or bid already at/above fair: take it
            q = s["inv"].pop(k); n = q * u["bid"]; s["cash"][u["ccy"]] += n * (1 - TAKER); s.get("opened_ts", {}).pop(k, None)
            out.append([now, book["id"], "sell", k, round(q, 8), u["bid"], round(n * TAKER, 6)])
    for k, u in U.items():
        if u["ccy"] not in p["ccys"] or k in s["inv"]: continue
        if u["ask"] < u["fair"] * (1 - p["discount"]) and u["vol_usd"] > 0:
            g = fx[u["ccy"]] / fx["GBP"]; n = min(p["size_gbp"] / g, s["cash"].get(u["ccy"], 0) / (1 + TAKER))
            if n <= 0: continue
            q = n / u["ask"]; s["cash"][u["ccy"]] -= n * (1 + TAKER); s["inv"][k] = q; s.setdefault("opened_ts", {})[k] = t
            out.append([now, book["id"], "buy", k, round(q, 8), u["ask"], round(n * TAKER, 6)])
    for k, q in s["inv"].items():                                         # resting exit at fair
        if k in U: s["since"].setdefault(k, str(time.time_ns())); s["q"][k] = dict(ccy=U[k]["ccy"], bid=0, ask=round(U[k]["fair"], 10), bid_qty=0, ask_qty=q, since=s["since"][k])
    V = _value(s, U, fx); return V, sum(v * fx[c] for c, v in s["cash"].items())
