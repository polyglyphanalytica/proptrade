import json,sys,time,re; sys.path.insert(0,'.'); from pmget import g
slugs=set()
for y in (2024,2025,2026):
  for m in "january february march april may june july august september october november december".split():
    for s in (f"what-price-will-bitcoin-hit-in-{m}-{y}", f"what-price-will-bitcoin-hit-in-{m}"):
        r=g(f"https://gamma-api.polymarket.com/events?slug={s}")
        if r: slugs.add(s)
out=[]
for s in sorted(slugs):
    e=g(f"https://gamma-api.polymarket.com/events?slug={s}")[0]
    for m in e['markets']:
        t=m.get('groupItemTitle') or m['question']; q=m['question']
        k=re.search(r'\$?([\d,]+)(k?)',q.replace('$','$'))
        nums=re.findall(r'\$([\d,\.]+)\s*(k|K)?',q)
        if not nums: continue
        v=float(nums[0][0].replace(',',''))*(1000 if nums[0][1] else 1)
        up = ('dip' not in q.lower() and 'below' not in q.lower() and 'fall' not in q.lower() and '↓' not in t)
        tok=json.loads(m['clobTokenIds'])[0]
        h=g(f"https://clob.polymarket.com/prices-history?market={tok}&interval=max&fidelity=60")["history"]
        out.append(dict(slug=s,end=m.get('endDate') or e['endDate'],q=q,K=v,up=up,h=h)); time.sleep(0.15)
    print(s,len(e['markets']),flush=True)
json.dump(out,open('ladders.json','w'))
