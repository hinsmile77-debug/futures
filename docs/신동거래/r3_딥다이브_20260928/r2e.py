# 시장가 청산(손절·본전·트레일·시간)에 추가 슬리피지를 얹어 민감도 확인
import r3lab as R, trail, sys
sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
from strategy.shindong import engine as E, spec as S
from r2b_fn import pt
ds=R.dates(); ENT='09:03'
rules=[('현행',None),('트레일2/1',trail.make(2,1)),('트레일4/1',trail.make(4,1)),('트레일8/4',trail.make(8,4)),('익절20',pt(20)),('익절10',pt(10))]
rows={}
for d in ds:
    P=R.load_day(d)
    if not P or ENT not in P['D'].c or '09:00' not in P['D'].c: continue
    D,L=P['D'],P['L']; e=D.c[ENT]; seg=D.between('09:00',ENT)
    dirn=1 if D.c[D.last_at_or_before('15:05')]>e else -1
    for side in (1,-1):
        stop=(min(D.l[k] for k in seg)-1.0) if side>0 else (max(D.h[k] for k in seg)+1.0)
        t1,t2=E.targets(L,ENT,side,e)
        for n,fn in rules:
            tr=(fn or E.run_trade)(D,side,ENT,stop,t1,t2)
            nm=sum(1 for g in tr['legs'] if not g['open'] and g.get('mkt'))
            rows[(d,side==dirn,n)]=(E.trade_net(tr),nm)
days=sorted({k[0] for k in rows})
print('거래일',len(days))
for slip in (0.0,0.1,0.25,0.5):
    print('\n추가 슬리피지 %.2fpt/시장가 다리'%slip)
    for n,_ in rules:
        R_=sum(rows[(d,True,n)][0]-slip*S.PT_VALUE_KRW*rows[(d,True,n)][1] for d in days)
        W_=sum(rows[(d,False,n)][0]-slip*S.PT_VALUE_KRW*rows[(d,False,n)][1] for d in days)
        print('  %-8s 옳은 %+6.0f 틀린 %+6.0f | p50 %+6.0f p60 %+6.0f p70 %+6.0f p100 %+6.0f'%(n,R_/1e4,W_/1e4,*( (p*R_+(1-p)*W_)/1e4 for p in (0.5,0.6,0.7,1.0))))
