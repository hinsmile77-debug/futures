# -*- coding: utf-8 -*-
"""횡보 감지 게이트 × R3 방어 — 흐름 6일(실신호) + 76일 가격대리. 저장소 루트에서 실행.
방어 2종: block(게이트 켜지면 R3 진입 안 함) · x4nf_if(게이트 켜진 동안만 X4 목표 + flip 금지)."""
import os, sys, json, sqlite3, collections, random, statistics as st
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..",".."))
sys.path.insert(0,ROOT); sys.path.insert(0,os.path.join(ROOT,"docs","신동거래","r3_딥다이브_20260929_MW0602"))
import r3lab as R
from strategy.shindong import engine as E
FLOW=["2026-09-21","2026-09-22","2026-09-23","2026-09-28","2026-09-29","2026-09-30"]
ALL=[d for d in R.dates() if R.load_day(d)]
# ── 피처(미래 참조 없음: 그 분 값) ──
FE=collections.defaultdict(dict)
c=sqlite3.connect(os.path.join(ROOT,"data/db/raw_data.db"))
for ts,f in c.execute("select ts,features from raw_features where ts>=? and ts<'2026-10-01'",(ALL[0],)):
    f=json.loads(f); FE[ts[:10]][ts[11:16]]={k:f.get(k) for k in ("atr","realized_vol_ann","in_value_area","multi_timeframe_15m","va_bandwidth","bar_volume")}
pool=collections.defaultdict(list)
for d in ALL:
    for hm,f in FE[d].items():
        if "09:31"<=hm<="14:30":
            for k in ("atr","realized_vol_ann"):
                if isinstance(f.get(k),(int,float)): pool[k].append(f[k])
Q={k:sorted(v)[len(v)//3] for k,v in pool.items()}   # 하위 1/3 문턱(전체 풀)
print("문턱(하위1/3): atr %.3f · realized_vol %.2f"%(Q["atr"],Q["realized_vol_ann"]))
def trailing_range(D,ent,n=60):
    ks=[k for k in D.idx if k<=ent and k in D.h][-n:]
    return max(D.h[k] for k in ks)-min(D.l[k] for k in ks) if ks else None
def flow_quiet(D,ent,n=30):
    ks=[k for k in D.idx if k<=ent and k in D.sp][-n:]
    return (max(D.sp[k] for k in ks)-min(D.sp[k] for k in ks)) if len(ks)>=n else None
def fe(f,k):
    v=FE.get(f["date"],{}).get(f["ent"],{}).get(k); return v if isinstance(v,(int,float)) else None
GATES=collections.OrderedDict([
 ("range60<=8pt", lambda f: (lambda r: r is not None and r<=8.0)(trailing_range(R.load_day(f["date"])["D"],f["ent"]))),
 ("range60<=0.30*ATR14", lambda f: (lambda r,a: r is not None and a and r<=0.30*a)(trailing_range(R.load_day(f["date"])["D"],f["ent"]),R.load_day(f["date"])["atr"])),
 ("rv_lo", lambda f: (lambda v: v is not None and v<=Q["realized_vol_ann"])(fe(f,"realized_vol_ann"))),
 ("atr_lo", lambda f: (lambda v: v is not None and v<=Q["atr"])(fe(f,"atr"))),
 ("iva", lambda f: fe(f,"in_value_area")==1),
 ("mtf15==0", lambda f: fe(f,"multi_timeframe_15m")==0),
 ("rv_lo&iva", lambda f: (lambda v: v is not None and v<=Q["realized_vol_ann"])(fe(f,"realized_vol_ann")) and fe(f,"in_value_area")==1),
 ("flowq30<60", lambda f: (lambda q: q is not None and q<60)(flow_quiet(R.load_day(f["date"])["D"],f["ent"]))),
])
def x4_if(gate):
    def tf(f):
        P=R.load_day(f["date"])
        if gate(f):
            t1,t2=E.targets_x4(P["L"],f["ent"],f["side"],f["e"]); return t1,t2,f["stop"]
        return f["t1"],f["t2"],f["stop"]
    return tf
def run(days,sig,x,policy=None,tgt_fn=None,x4nf=False,flowbusy=False,collect=None):
    return {d:R.run_r3(d,signal=sig,x=x,start_busy=(R.r2_busy(d) if flowbusy else None),policy=policy,tgt_fn=tgt_fn,x4nf=x4nf,collect=collect) for d in days}
def summ(res,base=None):
    days=sorted(res); nets={d:sum(t["net"] for t in res[d]) for d in days}
    n=sum(len(res[d]) for d in days); w=sum(1 for d in days for t in res[d] if t["net"]>0); tot=sum(nets.values())
    h=len(days)//2; h1=sum(nets[d] for d in days[:h]); h2=tot-h1
    cum=pk=mdd=0
    for d in days: cum+=nets[d]; pk=max(pk,cum); mdd=min(mdd,cum-pk)
    p=None
    if base is not None:
        bn={d:sum(t["net"] for t in base[d]) for d in days}; diff=[nets[d]-bn[d] for d in days]; random.seed(7)
        p=sum(1 for _ in range(2000) if sum(random.choice(diff) for _ in diff)<=0)/2000
    return n,w,tot,h1,h2,mdd,p,nets
def report(title,days,sig,x,flowbusy):
    print("\n== %s =="%title)
    base=run(days,sig,x,flowbusy=flowbusy); n,w,tot,h1,h2,mdd,_,nets=summ(base)
    print("%-28s n=%3d 승=%3d 합=%+8.0f만 H1/H2 %+6.0f/%+6.0f MDD %+6.0f"%("base",n,w,tot/1e4,h1/1e4,h2/1e4,mdd/1e4)+("  | "+" ".join("%s:%+.0f"%(d[5:],v/1e4) for d,v in nets.items()) if flowbusy else ""))
    for gname,g in GATES.items():
        if gname.startswith("flowq") and not flowbusy: continue
        col=[]
        r=run(days,sig,x,policy=lambda f,g=g: not g(f),flowbusy=flowbusy,collect=col)
        blocked=[f for f in col if not f["taken"]]
        # 막힌 진입이 base 에서 실제로 어떤 손익이었나(같은 시각 base 거래 매칭)
        bmap={(t["date"],t["ent"]):t["net"] for d in base for t in base[d]}
        bl_net=sum(bmap.get((f["date"],f["ent"]),0) for f in blocked); bl_n=sum(1 for f in blocked if (f["date"],f["ent"]) in bmap)
        n,w,tot,h1,h2,mdd,p,nets=summ(r,base)
        print("%-28s n=%3d 승=%3d 합=%+8.0f만 H1/H2 %+6.0f/%+6.0f MDD %+6.0f P(Δ≤0)=%.2f | 차단 %d건(base 손익 %+.0f만)"%("block:"+gname,n,w,tot/1e4,h1/1e4,h2/1e4,mdd/1e4,p,bl_n,bl_net/1e4)+("  | "+" ".join("%s:%+.0f"%(d[5:],v/1e4) for d,v in nets.items()) if flowbusy else ""))
    for gname in ("rv_lo","iva","range60<=0.30*ATR14","flowq30<60"):
        if gname.startswith("flowq") and not flowbusy: continue
        g=GATES[gname]
        r=run(days,sig,x,policy=lambda f,g=g: not (g(f) and f["flip"]),tgt_fn=x4_if(g),flowbusy=flowbusy)
        n,w,tot,h1,h2,mdd,p,nets=summ(r,base)
        print("%-28s n=%3d 승=%3d 합=%+8.0f만 H1/H2 %+6.0f/%+6.0f MDD %+6.0f P(Δ≤0)=%.2f"%("x4nf_if:"+gname,n,w,tot/1e4,h1/1e4,h2/1e4,mdd/1e4,p)+("  | "+" ".join("%s:%+.0f"%(d[5:],v/1e4) for d,v in nets.items()) if flowbusy else ""))
    r=run(days,sig,x,x4nf=True,flowbusy=flowbusy); n,w,tot,h1,h2,mdd,p,nets=summ(r,base)
    print("%-28s n=%3d 승=%3d 합=%+8.0f만 H1/H2 %+6.0f/%+6.0f MDD %+6.0f P(Δ≤0)=%.2f"%("X4NF 상시(참고)",n,w,tot/1e4,h1/1e4,h2/1e4,mdd/1e4,p)+("  | "+" ".join("%s:%+.0f"%(d[5:],v/1e4) for d,v in nets.items()) if flowbusy else ""))
report("흐름 6일 (실신호 · R2 점유 반영)",FLOW,"flow",None,True)
for x in (0.5,1.0,1.5):
    report("가격대리 px%.1f  %d일"%(x,len(ALL)),ALL,"px",x,False)
