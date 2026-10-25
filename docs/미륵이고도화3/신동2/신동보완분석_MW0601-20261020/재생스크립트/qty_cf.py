# -*- coding: utf-8 -*-
"""신동2 진입 수량 정책 반사실 — MAIN(v3) 21거래일 재생 거래에 수량 정책을 입혀 손익 재계산. 읽기 전용."""
import sys, os, json, math, statistics as st, sqlite3
ROOT=r"C:\Users\82108\PycharmProjects\futures"; sys.path.insert(0, ROOT)
from strategy.shindong import runner, engine as E
DB=os.path.join(ROOT,"data","db"); P=[os.path.join(DB,x) for x in ("raw_data.db","option_flow.db","premarket_levels.db")]
DAYS="2026-09-21,2026-09-22,2026-09-23,2026-09-28,2026-09-29,2026-09-30,2026-10-01,2026-10-02,2026-10-06,2026-10-07,2026-10-08,2026-10-12,2026-10-13,2026-10-14,2026-10-15,2026-10-16,2026-10-19,2026-10-20,2026-10-21,2026-10-22,2026-10-23".split(",")
lv=sqlite3.connect("file:%s?mode=ro"%P[2].replace("\\","/"),uri=True)
ATR={r[0]:r[1] for r in lv.execute("select date,atr14 from premarket_levels where stage='0850'")}
TR={}
for d in DAYS:
    r=runner.compute(d,*P)
    TR[d]=[dict(rule=t["rule"],e=t["entry_ts"],stop=abs(t["entry_px"]-t["stop_init"]),l1=t["legs"][0]["net"],l2=t["legs"][1]["net"])
           for t in r["results"]["MAIN"]["trades"] if t["status"]=="CLOSED"]
CAP=34_000_000; QMAX=3; PT=50_000
def pnl(t,q): return t["l1"]+(q-1)*t["l2"] if q>=1 else 0.0
POL={
 "고정 2계약(가상 규격)": lambda d,t: 2,
 "고정 3계약(현행 상한)": lambda d,t: 3,
 "R2만 1계약 · R3 3": lambda d,t: 1 if t["rule"]=="R2" else 3,
 "dev식 7%·0.6ATR": lambda d,t: min(QMAX,max(1,int(CAP*0.07//(0.6*ATR[d]*PT)))),
}
for x in (0.010,0.015,0.020,0.025):
    for buf in (1.0,):
        POL["신동2식 손절거리 %.1f%%(+%.0fpt)"%(x*100,buf)]=(lambda x,buf: lambda d,t: min(QMAX,max(1,int(CAP*x//((t["stop"]+buf)*PT)))))(x,buf)
res={}
def mdd(xs):
    c=p=m=0
    for v in xs: c+=v;p=max(p,c);m=min(m,c-p)
    return m
print("%-26s %8s %7s %7s %5s %6s %8s %7s %6s"%("정책","21일합","최악일","MDD","효율","평균q","최악거래","10-23","R2평균q"))
for nm,f in POL.items():
    day=[];qs=[];worst=0;q2=[]
    for d in DAYS:
        s=0
        for t in TR[d]:
            q=f(d,t); qs.append(q); v=pnl(t,q); s+=v; worst=min(worst,v)
            if t["rule"]=="R2": q2.append(q)
        day.append(s/1e4)
    res[nm]=day
    print("%-26s %+8.1f %+7.1f %+7.1f %5.2f %6.2f %+8.1f %+7.1f %6.2f"%(nm,sum(day),min(day),mdd(day),st.mean(day)/st.stdev(day),st.mean(qs),worst/1e4,day[-1],st.mean(q2) if q2 else 0))
json.dump(dict(days=DAYS,res=res),open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("R3 손절 중앙 %.2f · R2 손절 %s"%(st.median([t["stop"] for d in DAYS for t in TR[d] if t["rule"]=="R3"]),[round(t["stop"],1) for d in DAYS for t in TR[d] if t["rule"]=="R2"]))

print("\n--- 민감도·분할 (전반 09-21~10-06 / 후반 10-07~10-23) ---")
H1=[d for d in DAYS if d<="2026-10-06"]; H2=[d for d in DAYS if d>"2026-10-06"]
def run(f,days):
    out=[]
    for d in days: out.append(sum(pnl(t,f(d,t)) for t in TR[d])/1e4)
    return out
base=lambda d,t:2
for x in (0.015,0.020):
    for buf in (0.5,1.0,1.5):
        f=(lambda x,buf: lambda d,t: min(QMAX,max(1,int(CAP*x//((t["stop"]+buf)*PT)))))(x,buf)
        a=run(f,DAYS); h1=run(f,H1); h2=run(f,H2); b1=run(base,H1); b2=run(base,H2)
        print("X %.1f%% 버퍼 %.1f | 21일 %+7.1f 효율 %.2f | 전반 %+6.1f(고정2 %+6.1f) 효율 %.2f(%.2f) | 후반 %+6.1f(%+6.1f) 효율 %.2f(%.2f) | 10-23 제외 효율 %.2f"%(
            x*100,buf,sum(a),st.mean(a)/st.stdev(a),sum(h1),sum(b1),st.mean(h1)/st.stdev(h1),st.mean(b1)/st.stdev(b1),sum(h2),sum(b2),st.mean(h2)/st.stdev(h2),st.mean(b2)/st.stdev(b2),
            st.mean(a[:-1])/st.stdev(a[:-1])))
b=run(base,DAYS); print("고정2 10-23 제외 효율 %.2f"%(st.mean(b[:-1])/st.stdev(b[:-1])))
