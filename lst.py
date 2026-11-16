"""Staked-token ratio quoting (simulated). mETH/ETH drifts up smoothly as staking yield accrues; fair = 30-day log-linear
trend of the daily ratio, extrapolated to now. Book holds ETH and mETH only (ETH-denominated): quotes a bid for mETH
below fair and an ask above it. Judge vs hold_eth@1 and lsthold@1 (always hold mETH). Same conservative fill rules."""
import math, time
import quoting as Q
def fair_ratio(pair):
    r = Q.get(f"OHLC?pair={pair}&interval=1440"); k = [x for x in r if x != "last"][0]
    y = [math.log(float(c[4])) for c in r[k][:-1]][-30:]; n = len(y); x = list(range(n)); mx = sum(x)/n; my = sum(y)/n
    b = sum((a-mx)*(c-my) for a, c in zip(x, y)) / sum((a-mx)**2 for a in x); return math.exp(my + b*(n - mx))   # one day ahead ~ now
def step(book, s, now, out):
    p = book["params"]; pair = p["pair"]
    tk = Q.get(f"Ticker?pair={pair},XETHZUSD"); t = tk[[k for k in tk if k != "XETHZUSD"][0]]; ethusd = Q.mid(tk["XETHZUSD"])
    bid, ask = float(t["b"][0]), float(t["a"][0]); f = fair_ratio(pair)
    if "eth" not in s:   # GBP 1000 -> ETH at the ETHUSD ask with taker fee (GBPUSD supplied by caller)
        s.update(eth=p["_gbp_usd"] * 1000 / float(tk["XETHZUSD"]["a"][0]) * (1 - Q.TAKER), meth=0.0, q=None, since=None, start=now)
        if p["mode"] == "hold":
            s["meth"] = s["eth"] / ask * (1 - Q.TAKER); s["eth"] = 0.0; out.append([now, book["id"], "buy", pair, round(s["meth"], 8), ask, 0])
    if p["mode"] == "quote" and s["q"]:
        q = s["q"]
        try:
            tr, last = Q.trades_since(pair, s["since"]); s["since"] = last
            for px, v, side in tr:
                if side == "s" and q["bq"] > 0 and px < q["bid"]:
                    x = min(v, q["bq"]); q["bq"] -= x; s["eth"] -= x*q["bid"]*(1+Q.MAKER); s["meth"] += x
                    out.append([now, book["id"], "buy", pair, round(x, 8), q["bid"], round(x*q["bid"]*Q.MAKER, 8)])
                elif side == "b" and q["aq"] > 0 and px > q["ask"] and s["meth"] > 0:
                    x = min(v, q["aq"], s["meth"]); q["aq"] -= x; s["eth"] += x*q["ask"]*(1-Q.MAKER); s["meth"] -= x
                    out.append([now, book["id"], "sell", pair, round(x, 8), q["ask"], round(x*q["ask"]*Q.MAKER, 8)])
        except Exception: pass
    if p["mode"] == "quote":
        b = min(f*(1-p["edge"]), ask*(1-1e-4)); a = max(f*(1+p["edge"]), bid*(1+1e-4))
        s["q"] = dict(bid=b, ask=a, bq=max(0, s["eth"])/b/(1+Q.MAKER), aq=s["meth"]); s["since"] = s["since"] or str(time.time_ns())
    V = (s["eth"] + s["meth"] * f) * ethusd
    return V, s["eth"] * ethusd
