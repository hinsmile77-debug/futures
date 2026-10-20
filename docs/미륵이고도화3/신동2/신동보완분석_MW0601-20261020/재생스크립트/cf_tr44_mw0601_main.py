# -*- coding: utf-8 -*-
"""MW0601 신동 MAIN(v2 규칙) vs 같은 규칙 + R3 트레일 4/4(TR44) — 이 PC 엔진(v9-dev, v3)으로 일관 재생."""
import sys, os, json
ROOT=r"C:\Users\82108\PycharmProjects\futures"; sys.path.insert(0, ROOT)
from strategy.shindong import runner, engine
DB=os.path.join(ROOT,"data","db"); P=[os.path.join(DB,x) for x in ("raw_data.db","option_flow.db","premarket_levels.db")]
out={}
for d in sys.argv[1].split(","):
    r=runner.compute(d,*P,live=False); row={}
    for v,lab in (("SHADOW_V2","v2"),("MAIN","tr44")):
        tr=[t for t in r["results"][v]["trades"] if t["status"]=="CLOSED"]
        nets=[engine.trade_net(t) for t in tr]
        # 실계좌 1계약 = 1차 레그만(1차 목표에서 전량 청산 · 그 전 손절/트레일/시간이면 그 레그 값)
        l1=[t["legs"][0]["net"] for t in tr]
        row[lab]=dict(net=sum(nets)/1e4,n=len(tr),w=sum(1 for x in nets if x>0),q1=sum(l1)/1e4,q1w=sum(1 for x in l1 if x>0),
                      r3=sum(engine.trade_net(t) for t in tr if t["rule"]=="R3")/1e4,
                      ntr=sum(1 for t in tr if any(g.get("reason")=="TR" for g in t["legs"])),
                      trades=[dict(rule=t["rule"],side=t["side"],e=t["entry_ts"],px=t["entry_px"],x=t["exit_ts"],
                                   why="/".join(g.get("reason") or "" for g in t["legs"]),net=round(engine.trade_net(t)/1e4,1)) for t in tr])
    out[d]=row; print(d,"v2 %+.1f | TR44 %+.1f (%+.1f) TR청산 %d"%(row["v2"]["net"],row["tr44"]["net"],row["tr44"]["net"]-row["v2"]["net"],row["tr44"]["ntr"]),flush=True)
json.dump(out,open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
