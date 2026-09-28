# 흐름 4일 — 엔진 run_day 에 트레일 청산을 끼워 R2+R3 전체 재생
import sys; sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
from strategy.shindong import runner, engine
import trail, daystop
R=r"C:\Users\82108\PycharmProjects\futures\data\db\\"
fd=['2026-09-21','2026-09-22','2026-09-23','2026-09-28']
orig=engine.run_trade
for name,fn in (('현행',None),('트레일3/1',trail.make(3,1)),('트레일4/1',trail.make(4,1)),('트레일5/1',trail.make(5,1))):
    engine.run_trade = fn or orig
    for v in ('MAIN','SHADOW_X4NF'):
        cells=[];tot=0;totg=0
        for d in fd:
            res=runner.compute(d,R+'raw_data.db',R+'option_flow.db',R+'premarket_levels.db')['results'][v]
            nets=[engine.trade_net(t) for t in sorted(res['trades'],key=lambda t:t['entry_ts'])]
            s=sum(nets); tot+=s; g=daystop.apply(nets,G=150e4)[0]; totg+=g
            cells.append('%+.0f'%(s/1e4))
        print('%-9s %-12s 합 %+5.0f만 (G150 %+5.0f) | %s'%(name,v,tot/1e4,totg/1e4,' '.join(cells)))
engine.run_trade=orig
