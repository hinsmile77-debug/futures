import sys, random, collections
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
import r3lab as R
from strategy.shindong import engine as E
FLOW=["2026-09-21","2026-09-22","2026-09-23","2026-09-28","2026-09-29"]
ALL=[d for d in R.dates() if R.load_day(d)]
def tr44(D,side,ent,stop,t1,t2): return E.run_trade(D,side,ent,stop,t1,t2,trail=(4.0,4.0))
A=lambda f: f["side"]*(f["e"]-f["L0"])>0          # 맥점 반대편에서 진입(이미 깨진 맥점) 금지
B=lambda f: f["risk"]>=1.5                         # 손절폭 1.5pt 미만 금지
C=lambda f: f["day_losses"]<2                      # R3 당일 2패 후 중단
NFp=lambda f: not f["flip"]
def AND(*ps): return lambda f: all(p(f) for p in ps)
POL=collections.OrderedDict([
 ("base",dict()),
 ("A 깨진맥점금지",dict(policy=A)),
 ("B 손절<1.5금지",dict(policy=B)),
 ("A+B",dict(policy=AND(A,B))),
 ("C 2패중단",dict(policy=C)),
 ("NF",dict(policy=NFp)),
 ("X4NF",dict(x4nf=True)),
 ("X4NF+A",dict(x4nf=True,policy=A)),
 ("X4NF+A+B",dict(x4nf=True,policy=AND(A,B))),
 ("TR44",dict(trade_fn=tr44)),
 ("TR44+A",dict(trade_fn=tr44,policy=A)),
 ("TR44+A+B",dict(trade_fn=tr44,policy=AND(A,B))),
 ("TR44+NF+A",dict(trade_fn=tr44,policy=AND(A,NFp))),
])
def run(days, sig, x, kw, flowbusy=False):
    out={}
    for d in days:
        b=R.r2_busy(d) if flowbusy else None
        tr=R.run_r3(d,signal=sig,x=x,start_busy=b,**kw)
        out[d]=tr
    return out
def summ(res, base=None):
    days=sorted(res); nets={d:sum(t["net"] for t in res[d]) for d in days}
    n=sum(len(res[d]) for d in days); w=sum(1 for d in days for t in res[d] if t["net"]>0)
    tot=sum(nets.values())
    h1=sum(v for d,v in nets.items() if d<"2026-08-07"); h2=tot-h1
    cum=pk=mdd=0
    for d in days: cum+=nets[d]; pk=max(pk,cum); mdd=min(mdd,cum-pk)
    p=None
    if base is not None:
        bn={d:sum(t["net"] for t in base[d]) for d in days}; diff=[nets[d]-bn[d] for d in days]
        random.seed(7); k=0
        for _ in range(2000):
            s=sum(random.choice(diff) for _ in diff)
            k+= s<=0
        p=k/2000
    return n,w,tot,h1,h2,mdd,p,nets
print("== 흐름 5일 (실제 흐름 신호, R2 점유 반영) ==")
b=None
for name,kw in POL.items():
    r=run(FLOW,"flow",None,kw,flowbusy=True)
    if name=="base": b=r
    n,w,tot,h1,h2,mdd,p,nets=summ(r)
    print("%-14s n=%2d 승=%2d 합=%+7.0f만 | %s"%(name,n,w,tot/1e4," ".join("%s:%+.0f"%(d[5:],v/1e4) for d,v in nets.items())))
for x in (0.5,1.0,1.5):
    print("\n== 가격대리 px%.1f  %d일 (%s~%s) =="%(x,len(ALL),ALL[0],ALL[-1]))
    b=None
    for name,kw in POL.items():
        r=run(ALL,"px",x,kw)
        if name=="base": b=r
        n,w,tot,h1,h2,mdd,p,nets=summ(r, None if name=="base" else b)
        print("%-14s n=%3d 승률=%4.1f%% 합=%+7.0f만 H1=%+6.0f H2=%+6.0f MDD=%+6.0f P(Δ≤0)=%s"%(name,n,100*w/max(n,1),tot/1e4,h1/1e4,h2/1e4,mdd/1e4,p))
