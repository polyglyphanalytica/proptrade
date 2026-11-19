import json,sys,time,datetime as dt; sys.path.insert(0,'.'); from pmget import g
from concurrent.futures import ThreadPoolExecutor
L=json.load(open('ladders.json')); slugs=sorted({x['slug'] for x in L}); out=[]
def P(s): return int(dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp())
def hist(m, e=None):
    tok=json.loads(m['clobTokenIds'])[0]; a=P(m.get('startDate') or m.get('createdAt') or E['startDate']); b=P(m.get('endDate') or E['endDate'])+86400; h=[]
    t=a
    while t<b:
        try: h+=g(f"https://clob.polymarket.com/prices-history?market={tok}&startTs={t}&endTs={min(b,t+7*86400)}&fidelity=60")["history"]
        except Exception as e: pass
        t+=7*86400
    return h
for s in slugs:
    e=g(f"https://gamma-api.polymarket.com/events?slug={s}")[0]
    ms=e['markets']; globals()['E']=e
    with ThreadPoolExecutor(6) as ex: H=list(ex.map(hist,ms))
    for m,h in zip(ms,H): out.append(dict(slug=s,q=m['question'],title=m.get('groupItemTitle'),end=m.get('endDate') or e['endDate'],start=m.get('startDate'),h=h))
    print(s,sum(len(h) for h in H),flush=True)
json.dump(out,open('ladders2.json','w'))
print("done")
