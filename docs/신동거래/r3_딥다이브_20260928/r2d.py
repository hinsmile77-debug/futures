import pickle, sys
sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
ds,names,out=pickle.load(open('r2.pkl','rb'))
days=sorted({k[0] for k in out if k[1]=='dir'})
def ab(n):
    R=sum(out[(d,out[(d,'dir')],n)] for d in days); W=sum(out[(d,-out[(d,'dir')],n)] for d in days); return R,W
bR,bW=ab('현행')
print('현행: 옳은방향 %+.0f만 / 틀린방향 %+.0f만'%(bR/1e4,bW/1e4))
for n in ('트레일2/1','트레일4/1','트레일8/4','익절20','익절10','트레일4/4'):
    R,W=ab(n)
    # p*bR+(1-p)*bW = p*R+(1-p)*W → p = (W-bW)/((bR-bW)-(R-W))
    p=(W-bW)/((bR-bW)-(R-W))
    print('%-8s 옳은 %+6.0f 틀린 %+6.0f  → 현행보다 나은 적중률 구간: p < %.0f%%'%(n,R/1e4,W/1e4,p*100))
# 실제 R2 3건
from strategy.shindong import runner, engine as E
import trail
from r2b_fn import pt
Rr=r"C:\Users\82108\PycharmProjects\futures\data\db\\"
rules=[('현행',None),('트레일2/1',trail.make(2,1)),('트레일4/4',trail.make(4,4)),('트레일8/4',trail.make(8,4)),('익절10',pt(10)),('익절20',pt(20))]
print('\n실제 R2 (MAIN) — 만원')
for d in ('2026-09-21','2026-09-22','2026-09-23','2026-09-28'):
    res=runner.compute(d,Rr+'raw_data.db',Rr+'option_flow.db',Rr+'premarket_levels.db')['results']['MAIN']
    r2=[t for t in res['trades'] if t['rule']=='R2']
    if not r2: print(d,'R2 없음',res['decision'].get('r2')); continue
    t=r2[0]
    import r3lab as R
    D=R.load_day(d)['D']
    cells=[]
    for n,fn in rules:
        tr=(fn or E.run_trade)(D,t['side'],t['entry_ts'],t['stop_init'],t['t1'],t['t2'])
        cells.append('%s %+.0f(%s)'%(n,E.trade_net(tr)/1e4,'/'.join(g.get('reason','') for g in tr['legs'])))
    print(d,t['entry_ts'],t['side'],t['entry_px'],'|',' · '.join(cells))
