import sys,io,contextlib; sys.path.insert(0,sys.argv[1])
import sim, sim2
from strategy.shindong import families as F, spec as S, engine as E
orig_rs=F._run_signal; orig_mk=sim2.make_pos
MODE={'ban':False,'free':False}
def mk(d,cfg,atr):
    p=orig_mk(d,cfg,atr)
    def pos(*a):
        t=p(*a); t['_be']=any(g['reason']=='BE' for g in t['legs'])
        if MODE['ban'] and t['_be']:          # 본전 방향도 손절처럼 누적 금지
            t['legs']=[dict(g,reason='SL') for g in t['legs']]
        return t
    return pos
sim2.make_pos=mk
def rs(d,sig,rule,stop_fn,trail,tp,max_trades,**kw):
    if not MODE['free']: return orig_rs(d,sig,rule,stop_fn,trail,tp,max_trades,**kw)
    out=orig_rs(d,sig,rule,stop_fn,trail,tp,max_trades+10,**kw); keep=[]; n=0
    for t in out:
        if n>=max_trades: break
        keep.append(t); n+= 0 if t.get('_be') else 1
    return keep
F._run_signal=rs
b=sim2.run({}); bd={d:sum(t['pt'] for t in v) for d,v in b.items()}; B=sim.summ(b,'')
cfg={'leg1':{'be_at':3},'leg2':{'be_at':3}}
print('안 | 거래 | 합계 | Δ기준 | 10/19~ | 최악일 | MDD | 10/23 | 같은방향 재진입(본전 직후) n·합')
for lab,ban,free in [('본전 방향 허용 · 상한 그대로',0,0),('본전 방향 금지 · 상한 그대로',1,0),('본전 방향 허용 · 본전 상한제외',0,1),('본전 방향 금지 · 본전 상한제외',1,1)]:
    MODE.update(ban=ban,free=free); o=sim2.run(cfg); s=sim.summ(o,''); od={d:sum(t['pt'] for t in v) for d,v in o.items()}
    same=[]; 
    for v in o.values():
        for a,c in zip(v,v[1:]):
            if 'BE' in a['why'] or (ban and False): pass
            if ('BE' in a['why'] or (ban and a['why']=='SL/SL' and False)) and c['side']==a['side']: same.append(c['pt'])
    print(f"{lab} | {s['n']} | {s['sum']:+.1f} | {s['sum']-B['sum']:+.1f} | {s['oos']:+.1f} | {s['worst_day']:.1f} | {s['mdd']:.1f} | {od['2026-10-23']:+.1f} | {len(same)}건 {sum(same):+.1f}")
    if ban: print('   10/23:',[(t['rule'],'B' if t['side']>0 else 'S',t['t'],t['x'],t['pt']) for t in o['2026-10-23']], ' 10/20:',[(t['rule'],'B' if t['side']>0 else 'S',t['t'],t['pt']) for t in o['2026-10-20']])
