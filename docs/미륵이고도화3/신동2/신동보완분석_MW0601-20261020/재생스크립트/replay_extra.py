# [보관용] 2026-10-20 세션 재생 스크립트 — 인자: <origin/dev 워크트리 경로> <날짜(콤마)> <출력 json>.
# 정식 도구는 scripts/shindong_complement_mw0602.py (워크트리 자동 생성·삭제).
import sys, os, json, datetime as dt
sys.path.insert(0, sys.argv[1]); DB=r"C:\Users\82108\PycharmProjects\futures\data\db"
from strategy.shindong import runner, engine, families
P=[os.path.join(DB,x) for x in ("raw_data.db","option_flow.db","premarket_levels.db")]
out={}
for d0 in sys.argv[2].split(","):
    prod,_,_=runner.select_flow_product(dt.date.fromisoformat(d0))
    c,f,l=runner.load_inputs(d0,prod,*P); fx=runner.load_fx(d0,P[0])
    L=engine.prepare_levels(l); d=engine.DayFrame(c,f,fx=fx)
    v1=engine.run_day(d,L,"SHADOW_V1")
    res={"FLOWF":families.run_family_day(d,L,"flowf",v1_decision=v1["decision"]),
         "V1X4":engine.run_day(d,L,"SHADOW_V1X4")}
    row={}
    for k,r in res.items():
        nets=[sum(g.get("net",0.0) for g in t["legs"] if not g.get("open",True)) for t in r["trades"]]
        row[k]=sum(nets)/1e4
    out[d0]=row; print(d0,row,flush=True)
json.dump(out,open(sys.argv[3],"w"),indent=1)
