# -*- coding: utf-8 -*-
"""개인 콜/풋 매수·매도 조합에서 만든 흐름 게이트 — 창 안/밖 분포로 문턱을 잡고 6일 R3 방어를 시험.
게이트 3종(모두 30분 롤링, 미래 참조 없음):
  flowrange = 콜−풋 누적의 30분 고저 범위
  conviction = (|Σ콜순액| + |Σ풋순액|) / Σ총회전   — 방향 확신(순매수가 한쪽으로 쌓이는가)
  turnover  = Σ총회전 / 그날 09:31~그때까지 분당 평균 회전  — 활동 수준(상대)"""
import os, sys, sqlite3, collections, statistics as st, random
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..",".."))
sys.path.insert(0,ROOT); sys.path.insert(0,os.path.join(ROOT,"docs","신동거래","r3_딥다이브_20260929_MW0602"))
import r3lab as R
from strategy.shindong import engine as E
from strategy.shindong.calendar import select_flow_product
import datetime as dt
FLOW=["2026-09-21","2026-09-22","2026-09-23","2026-09-28","2026-09-29","2026-09-30"]
W={"2026-09-28":("10:28","15:05"),"2026-09-29":("11:54","14:16"),"2026-09-30":("11:43","15:05")}
c=sqlite3.connect(os.path.join(ROOT,"data/db/option_flow.db"))
RAWF={}
for d in FLOW:
    p,_,_=select_flow_product(dt.date.fromisoformat(d)); S=collections.defaultdict(dict)
    for bt,prod,sq,bq,na in c.execute("select bar_time,product,sell_qty,buy_qty,net_amt from option_investor_flow where trade_date=? and investor='individual' and product in (?,?)",(d,p+"_call",p+"_put")):
        S[bt]["call" if prod.endswith("call") else "put"]=(sq,bq,na)
    ks=sorted(k for k in S if "09:00"<=k<="15:08" and len(S[k])==2)
    inc={}
    for k1,k2 in zip(ks,ks[1:]):
        inc[k2]=dict(cn=S[k2]["call"][2]-S[k1]["call"][2],pn=S[k2]["put"][2]-S[k1]["put"][2],
                     to=sum(S[k2][x][i]-S[k1][x][i] for x in ("call","put") for i in (0,1)))
    RAWF[d]=inc
def gates_at(d,hm,n=30):
    inc=RAWF[d]; ks=[k for k in sorted(inc) if k<=hm][-n:]
    if len(ks)<n: return None
    D=R.load_day(d)["D"]; sk=[k for k in D.idx if k<=hm and k in D.sp][-n:]
    fr=max(D.sp[k] for k in sk)-min(D.sp[k] for k in sk) if sk else None
    cs=sum(inc[k]["cn"] for k in ks); ps=sum(inc[k]["pn"] for k in ks); to=sum(inc[k]["to"] for k in ks)
    allk=[k for k in sorted(inc) if "09:31"<=k<=hm]; avg=st.mean(inc[k]["to"] for k in allk) if allk else None
    return dict(flowrange=fr, conviction=(abs(cs)+abs(ps))/to if to else None, turnover=(to/n/avg) if avg else None)
# 분포
dist=collections.defaultdict(lambda: collections.defaultdict(list))
for d in W:
    a,b=W[d]
    for hm in sorted(RAWF[d]):
        if not("10:00"<=hm<="15:05"): continue
        g=gates_at(d,hm)
        if not g: continue
        for k,v in g.items():
            if v is not None: dist["창안" if a<=hm<=b else "창밖"][k].append(v)
for d in ("2026-09-21","2026-09-22","2026-09-23"):
    for hm in sorted(RAWF[d]):
        if "10:00"<=hm<="15:05":
            g=gates_at(d,hm)
            if g:
                for k,v in g.items():
                    if v is not None: dist["비대상일"][k].append(v)
print("게이트 값 분포(30분 롤링) — 중앙 [p25, p75]")
TH={}
for k in ("flowrange","conviction","turnover"):
    row=[]
    for lab in ("창안","창밖","비대상일"):
        v=sorted(dist[lab][k]); row.append("%s %.3f [%.3f, %.3f] n=%d"%(lab,v[len(v)//2],v[len(v)//4],v[3*len(v)//4],len(v)))
    print("  %-11s %s"%(k," | ".join(row)))
    vi=sorted(dist["창안"][k]); vo=sorted(dist["창밖"][k]); TH[k]=(vi[len(vi)//2]+vo[len(vo)//2])/2   # 창안·창밖 중앙의 중간
print("문턱(창안·창밖 중앙의 중간):",{k:round(v,3) for k,v in TH.items()})
GATES=collections.OrderedDict([
 ("flowrange<th", lambda f:(lambda g:g and g["flowrange"] is not None and g["flowrange"]<TH["flowrange"])(gates_at(f["date"],f["ent"]))),
 ("conviction<th", lambda f:(lambda g:g and g["conviction"] is not None and g["conviction"]<TH["conviction"])(gates_at(f["date"],f["ent"]))),
 ("turnover<th", lambda f:(lambda g:g and g["turnover"] is not None and g["turnover"]<TH["turnover"])(gates_at(f["date"],f["ent"]))),
 ("conv&turn", lambda f:(lambda g:g and g["conviction"] is not None and g["turnover"] is not None and g["conviction"]<TH["conviction"] and g["turnover"]<TH["turnover"])(gates_at(f["date"],f["ent"]))),
])
def x4_if(gate):
    def tf(f):
        P=R.load_day(f["date"])
        if gate(f):
            t1,t2=E.targets_x4(P["L"],f["ent"],f["side"],f["e"]); return t1,t2,f["stop"]
        return f["t1"],f["t2"],f["stop"]
    return tf
def run(policy=None,tgt_fn=None,x4nf=False,collect=None):
    return {d:R.run_r3(d,signal="flow",start_busy=R.r2_busy(d),policy=policy,tgt_fn=tgt_fn,x4nf=x4nf,collect=collect) for d in FLOW}
def summ(res,base=None):
    days=sorted(res); nets={d:sum(t["net"] for t in res[d]) for d in days}; n=sum(len(res[d]) for d in days); w=sum(1 for d in days for t in res[d] if t["net"]>0); tot=sum(nets.values())
    p=None
    if base is not None:
        bn={d:sum(t["net"] for t in base[d]) for d in days}; diff=[nets[d]-bn[d] for d in days]; random.seed(7)
        p=sum(1 for _ in range(2000) if sum(random.choice(diff) for _ in diff)<=0)/2000
    return n,w,tot,p,nets
base=run(); n,w,tot,_,nets=summ(base)
def line(name,r):
    n,w,tot,p,nets=summ(r,base); print("%-24s n=%2d 승=%2d 합=%+6.0f만 P(Δ≤0)=%s | %s"%(name,n,w,tot/1e4,"-" if p is None else "%.2f"%p," ".join("%s:%+.0f"%(d[5:],v/1e4) for d,v in nets.items())))
print("\n== 흐름 6일 R3 (실신호 · R2 점유 반영) ==")
line("base",base)
bmap={(t["date"],t["ent"]):t["net"] for d in base for t in base[d]}
for gname,g in GATES.items():
    col=[]; r=run(policy=lambda f,g=g: not g(f),collect=col)
    bl=[f for f in col if not f["taken"] and (f["date"],f["ent"]) in bmap]
    line("block:"+gname,r); print("      차단 %d건 (base 손익 %+.0f만)"%(len(bl),sum(bmap[(f["date"],f["ent"])] for f in bl)/1e4))
    line("x4nf_if:"+gname,run(policy=lambda f,g=g: not (g(f) and f["flip"]),tgt_fn=x4_if(g)))
line("X4NF 상시(참고)",run(x4nf=True))
# base R3 거래별 게이트 값과 손익 — 손실이 어느 구간에 몰리나
print("\n== base R3 거래별(6일): 진입 시 게이트 값 vs 손익 ==")
rows=[]
for d in FLOW:
    for t in base[d]:
        g=gates_at(d,t["ent"]) or {}
        rows.append((d,t["ent"],t["side"],t["net"],g.get("flowrange"),g.get("conviction"),g.get("turnover"),t["flip"],t["mfe"]))
for k,i in (("flowrange",4),("conviction",5),("turnover",6)):
    v=[r for r in rows if r[i] is not None]; v.sort(key=lambda r:r[i]); h=len(v)//2
    lo,hi=v[:h],v[h:]
    print("  %-11s 하위 절반: n=%d 승=%d 합=%+.0f만 | 상위 절반: n=%d 승=%d 합=%+.0f만"%(k,len(lo),sum(r[3]>0 for r in lo),sum(r[3] for r in lo)/1e4,len(hi),sum(r[3]>0 for r in hi),sum(r[3] for r in hi)/1e4))
