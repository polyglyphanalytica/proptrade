"""Polymarket BTC ladder signal (read-only data; nothing is traded on Polymarket - FCA rule).
Polymarket's monthly "What price will Bitcoin hit in <Month>?" ladder prices the chance BTC touches each strike before month end.
level = mean over the up and down sides of logit(Polymarket price) - logit(driftless touch probability from Kraken 30-day realised vol).
High level = the crowd pays more than realised vol justifies for big moves. Same filters as the history check (JOURNAL 2026-11-19)."""
import json, math, re, time, urllib.request, datetime as dt, statistics as st
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
def _get(url):
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25))
        except Exception as e: err = e; time.sleep(2)
    raise err
def _kraken(path):
    r = _get("https://api.kraken.com/0/public/" + path)
    if r["error"]: raise RuntimeError(r["error"])
    return r["result"]
def _ts(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
def _parse(q):
    m = re.search(r"\$([\d,\.]+)\s*([kK])?", q)
    if not m: return None
    return float(m.group(1).replace(",", "")) * (1000 if m.group(2) else 1), not any(w in q.lower() for w in ("dip", "below", "fall", "drop"))
N = lambda x: 0.5 * (1 + math.erf(x / 2 ** .5)); lg = lambda p: math.log(p / (1 - p))
_cache = {}
def level(now=None):
    """Cached per process (one Polymarket/Kraken fetch per run). Returns dict(level, up, dn, n_up, n_dn, spot, sigma, slug) or None if the ladder is unusable (missing, or < 2 days left)."""
    if now is None and "v" in _cache: return _cache["v"]
    key = now is None; now = now or time.time(); d = dt.datetime.fromtimestamp(now, dt.timezone.utc)
    slug = f"what-price-will-bitcoin-hit-in-{d.strftime('%B').lower()}-{d.year}"
    ev = _get(f"https://gamma-api.polymarket.com/events?slug={slug}")
    if not ev:
        if key: _cache["v"] = None
        return None
    ev = ev[0]
    r = _kraken("OHLC?pair=XBTUSD&interval=1440"); k = [x for x in r if x != "last"][0]; c = r[k]
    closes = [float(x[4]) for x in c[:-1]]; rets = [math.log(closes[i] / closes[i - 1]) for i in range(len(closes) - 30, len(closes))]
    sig = st.pstdev(rets) * math.sqrt(365)
    t = _kraken("Ticker?pair=XBTUSD"); t = list(t.values())[0]; S = (float(t["b"][0]) + float(t["a"][0])) / 2
    up, dn = [], []
    for m in ev["markets"]:
        if m.get("closed"): continue
        pk = _parse(m["question"]); end = _ts(m.get("endDate") or ev["endDate"])
        if not pk or end - now < 2 * 86400: continue
        K, isup = pk
        st0 = _ts(m.get("startDate") or ev["startDate"]); since = [x for x in c if int(x[0]) >= st0 - st0 % 86400]   # touches count from the strike's own listing day
        hi = max([float(x[2]) for x in since] + [S]); lo = min([float(x[3]) for x in since] + [S])
        if (isup and K <= hi) or (not isup and K >= lo): continue
        try:
            bb, ba = float(m.get("bestBid") or 0), float(m.get("bestAsk") or 0)
            p = (bb + ba) / 2 if bb > 0 and ba > 0 else float(json.loads(m["outcomePrices"])[0])
        except Exception: continue
        tau = (end - now) / (365 * 86400); pm_ = 2 * (1 - N(abs(math.log(K / S)) / (sig * math.sqrt(tau))))
        if not (0.05 <= pm_ <= 0.95 and 0.01 <= p <= 0.99): continue
        (up if isup else dn).append(lg(p) - lg(pm_))
    if not up or not dn:
        if key: _cache["v"] = None
        return None
    u, w = st.mean(up), st.mean(dn)
    v = dict(level=(u + w) / 2, up=u, dn=w, n_up=len(up), n_dn=len(dn), spot=S, sigma=sig, slug=slug)
    if key: _cache["v"] = v
    return v
