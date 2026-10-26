import sys, os, json
sys.path.insert(0, os.environ["SCR"]); from causal_engine import *
D=json.load(open(os.environ["SCR"]+"/causal_full.json",encoding="utf-8"))["days"]
tot=agree=r1zero=0; rows=[]
day_agree=[]
for d0 in D:
    c,f,l=inputs(d0); d=E.DayFrame(c,f); L=E.prepare_levels(l)
    res=run_day_c(d,L,"MAIN"); bias=res["decision"].get("bias")
    base=d.sp.get(S.CONF_BASE)
    # 장중 R3 구간 매분 F2 방향 vs R1
    mins=[k for k in d.idx if "09:30"<=k<="14:30" and k in d.sp]
    tr=[(-1 if (base is not None and d.sp[k]-base>0) else 1) for k in mins]
    a=sum(1 for x in tr if bias and x==bias); n=len(mins)
    flips=sum(1 for i in range(1,len(tr)) if tr[i]!=tr[i-1])
    o9,c15=d.c.get("09:00"),d.c.get(d.last_at_or_before("15:05") or "")
    day=(1 if c15>o9 else -1) if o9 and c15 else 0
    fday=sum(1 for x in tr if x==day)
    rows.append((d0[5:],bias,n,a,flips,day,fday))
print("날짜  R1  R3분 F2=R1분 F2방향전환 일방향 F2=일방향분")
for r in rows: print("%s %+d  %3d  %3d(%3.0f%%)  %3d   %+d  %3d(%3.0f%%)"%(r[0],r[1] or 0,r[2],r[3],100*r[3]/r[2] if r[2] else 0,r[4],r[5],r[6],100*r[6]/r[2] if r[2] else 0))
N=sum(r[2] for r in rows); A=sum(r[3] for r in rows if r[1]); NB=sum(r[2] for r in rows if r[1]); F=sum(r[6] for r in rows)
print("합: F2=R1 %.0f%% (R1 있는 날) · F2=그날 실제 방향 %.0f%% · R1=그날 실제 방향 %d/%d일"%(100*A/NB,100*F/N,sum(1 for r in rows if r[1] and r[1]==r[5]),sum(1 for r in rows if r[1])))
