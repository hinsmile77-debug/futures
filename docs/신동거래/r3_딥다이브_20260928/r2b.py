# R2 형 개장 진입 — 09:03 종가, 양방향. 손절 = 09:00–진입 극값 ±1.0, 목표 = engine.targets (R2 와 같은 기하)
import r3lab as R, trail, pickle, sys
sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
from strategy.shindong import engine as E, spec as S
ds=R.dates()
def pt(G):
    """당일(=거래) 수익중단: 미실현 +G pt 도달 시 두 다리 모두 청산(지정가)."""
    def fn(d, side, t0, stop, t1, t2, e2=False):
        e=d.c[t0]; c=e+side*G
        n=lambda t: c if (t is None or side*(t-c)>0) else t
        return E.run_trade(d, side, t0, stop, n(t1), n(t2))
    return fn
rules=[('현행',None)]+[('트레일%s/%s'%(a,b),trail.make(a,b)) for a in (2,3,4,5,6,8,10) for b in (1,2,3,4,6) if b<=a] \
     +[('익절%s'%g,pt(g)) for g in (3,5,8,10,15,20)]
ENT='09:03'
out={}
for d in ds:
    P=R.load_day(d)
    if not P or ENT not in P['D'].c or '09:00' not in P['D'].c: continue
    D,L=P['D'],P['L']; e=D.c[ENT]
    seg=D.between('09:00',ENT)
    dirn=None
    tx=D.last_at_or_before('15:05')
    for side in (1,-1):
        stop=(min(D.l[k] for k in seg)-S.OR_STOP_BUF) if side>0 else (max(D.h[k] for k in seg)+S.OR_STOP_BUF)
        t1,t2=E.targets(L,ENT,side,e)
        for name,fn in rules:
            tr=(fn or E.run_trade)(D,side,ENT,stop,t1,t2)
            out[(d,side,name)]=E.trade_net(tr)
    out[(d,'dir')]=1 if D.c[tx]>e else -1
pickle.dump((ds,[r[0] for r in rules],out),open('r2.pkl','wb'))
print('days',len({k[0] for k in out}))
