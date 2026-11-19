import json,re,math,bisect,statistics as st
from datetime import datetime
L=json.load(open('ladders2.json')); kd=json.load(open('kd.json'))
D=[c[0] for c in kd]   # candle open times (UTC midnight)
def P(s): return int(datetime.fromisoformat(s.replace('Z','+00:00')).timestamp())
N=lambda x:0.5*(1+math.erf(x/2**.5)); lg=lambda p:math.log(p/(1-p))
def parse(q):
    m=re.search(r'\$([\d,\.]+)\s*([kK])?',q)
    if not m: return None
    K=float(m.group(1).replace(',',''))*(1000 if m.group(2) else 1)
    down=any(w in q.lower() for w in ('dip','below','fall','drop'))
    return K,not down
rows={}   # day -> list of (up, div)
for x in L:
    pk=parse(x['q'])
    if not pk or not x['h']: continue
    K,up=pk; end=P(x['end']); h=sorted((o['t'],o['p']) for o in x['h']); ht=[a for a,b in h]
    st0=P(x['start']) if x.get('start') else h[0][0]
    for i in range(31,len(kd)-1):
        t=D[i]                               # midnight; price = close of candle i-1
        if t<st0+86400 or t>end-2*86400: continue
        j=bisect.bisect_right(ht,t)-1
        if j<0 or t-ht[j]>6*3600: continue
        p=h[j][1]; S=kd[i-1][4]
        # touched already? running hi/lo from event start day
        a=bisect.bisect_left(D,st0- st0%86400); hi=max(c[2] for c in kd[a:i]) if a<i else S; lo=min(c[3] for c in kd[a:i]) if a<i else S
        if (up and K<=hi) or ((not up) and K>=lo): continue
        rets=[math.log(kd[n][4]/kd[n-1][4]) for n in range(i-30,i)]; sig=st.pstdev(rets)*math.sqrt(365)
        tau=(end-t)/(365*86400); d=abs(math.log(K/S))/(sig*math.sqrt(tau)); pm_=2*(1-N(d))
        if not(0.05<=pm_<=0.95 and 0.01<=p<=0.99): continue
        rows.setdefault(i,[]).append((up,lg(p)-lg(pm_)))
import random
days=sorted(rows); print("days",len(days), datetime.utcfromtimestamp(D[days[0]]).date(), datetime.utcfromtimestamp(D[days[-1]]).date())
U=[];Dn=[];F={1:[],3:[],7:[]}; I=[]
for i in days:
    u=[d for up,d in rows[i] if up]; dn=[d for up,d in rows[i] if not up]
    if not u or not dn: continue
    U.append(st.mean(u)); Dn.append(st.mean(dn)); I.append(i)
print("n",len(I),"mean up div",round(st.mean(U),3),"mean dn div",round(st.mean(Dn),3))
def rank(v): s=sorted(range(len(v)),key=v.__getitem__); r=[0]*len(v)
def sp(a,b):
    ra=[sorted(a).index(x) for x in a]; rb=[sorted(b).index(x) for x in b]; return st.correlation(ra,rb)
for name,sigv in (("up",U),("dn",Dn),("skew",[a-b for a,b in zip(U,Dn)]),("level",[(a+b)/2 for a,b in zip(U,Dn)])):
    out=[]
    for hz in (1,3,7):
        xs=[];ys=[]
        for s,i in zip(sigv,I):
            if i-1+hz < len(kd): xs.append(s); ys.append(math.log(kd[i-1+hz][4]/kd[i-1][4]))
        h=len(xs)//2
        out.append(f"{hz}d rho={sp(xs,ys):+.3f} (h1 {sp(xs[:h],ys[:h]):+.3f}, h2 {sp(xs[h:],ys[h:]):+.3f}) n={len(xs)}")
    print(name," | ".join(out))
json.dump(dict(I=I,U=U,Dn=Dn),open('sig.json','w'))
