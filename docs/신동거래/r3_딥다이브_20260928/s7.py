import r3lab as R, random
from strategy.shindong import engine as E
ds=R.dates(); mid=ds[len(ds)//2]
T=lambda v: v is True
def near_struct(f):
    P=R.load_day(f['date']); L=P['L']; _,lv=E.levels_at(L,f['ent'])
    c=[x for x in lv if f['side']*(x-f['e'])>=2.0]
    return (min(c) if f['side']>0 else max(c)) if c else None
def cap(k1,k2=None):
    def fn(f):
        s,e,r=f['side'],f['e'],f['risk']
        t1,t2=f['t1'],f['t2']
        c1=e+s*k1*r
        t1=c1 if (t1 is None or s*(t1-c1)>0) else t1
        if k2:
            c2=e+s*k2*r
            t2=c2 if (t2 is None or s*(t2-c2)>0) else t2
        if t2 is not None and s*(t2-t1)<0: t2=t1
        return t1,t2,f['stop']
    return fn
def struct1(f):
    s,e=f['side'],f['e']; n=near_struct(f)
    t1=f['t1']
    if n is not None:
        n=n-s*0.5
        if t1 is None or s*(t1-n)>0: t1=n
    t2=f['t2'] if f['t2'] is not None else t1
    if t1 is not None and s*(t2-t1)<0: t2=t1
    return t1,t2,f['stop']
X={'현행청산':None,'X1 1차=1R':cap(1.0),'X2 1차=1.5R':cap(1.5),'X3 1차1R+최종3R':cap(1.0,3.0),'X4 1차=가까운구조맥점':struct1}
F={'진입무필터':None,'+am':lambda f:T(f['am_align']),'+flip금지':lambda f:not f['flip'],'+미륵반대금지':lambda f:f['mk_align'] is not False,
   '+am+미륵반대금지':lambda f:T(f['am_align']) and f['mk_align'] is not False}
base={}
for x in (0.5,1.0,1.5):
    b=None
    print('\n=== px%.1f ==='%x)
    print('%-22s %-14s %4s %5s %8s %7s %7s %7s  %-17s %5s'%('청산','진입','n','승률','순(만)','H1','H2','최악일','Δ현행 95%CI','P≤0'))
    for xn,xf in X.items():
        for fn,ff in F.items():
            dn={}; tr=[]
            for d in ds:
                v=R.run_r3(d,'px',policy=ff,start_busy='09:29',x=x,tgt_fn=xf); tr+=v; dn[d]=sum(t['net'] for t in v)
            if b is None: b=dn
            diff=[dn[d]-b[d] for d in ds]; random.seed(3); bs=sorted(sum(random.choice(diff) for _ in ds) for _ in range(2000))
            n=len(tr)
            print('%-22s %-14s %4d %4.0f%% %+8.0f %+7.0f %+7.0f %+7.0f  [%+5.0f,%+5.0f] %5.2f'%(xn,fn,n,100*sum(1 for t in tr if t['net']>0)/max(n,1),sum(dn.values())/1e4,
                sum(v for d,v in dn.items() if d<mid)/1e4,sum(v for d,v in dn.items() if d>=mid)/1e4,min(dn.values())/1e4,bs[50]/1e4,bs[1950]/1e4,sum(1 for s in bs if s<=0)/2000))
