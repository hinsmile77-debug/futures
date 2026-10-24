import sys, os, json
sys.path.insert(0, os.getcwd())
from strategy.shindong import runner, engine
DB='data/db/'; LD='data/shindong2_live'
COST=0.20; PTV=50000; CAP=15_000_000
SD={1:'매수',-1:'매도',0:'중립',None:'—'}
rows=[]; trades_all=[]
for dd in sorted(x for x in os.listdir(LD) if x.isdigit()):
    d=f"{dd[:4]}-{dd[4:6]}-{dd[6:]}"
    ev=json.load(open(f'{LD}/{dd}/eval.json',encoding='utf-8'))
    sc=json.load(open(f'{LD}/{dd}/ai_score.json',encoding='utf-8'))
    r=runner.compute(d, DB+'raw_data.db', DB+'option_flow.db', DB+'premarket_levels.db', live=False)
    m=r['results']['MAIN']
    mt=[]
    for t in m['trades']:
        net=engine.trade_net(t)/2/PTV   # pt/계약, 수수료·슬리피지 포함
        legs=[(g.get('ts'),g.get('px'),g.get('reason')) for g in t['legs']]
        mt.append(dict(who='MAIN',d=d,rule=t['rule'],side=SD[t['side']],t=t.get('entry_ts') or t.get('t0'),px=t.get('entry_px') or t.get('e'),
                       stop=round(t.get('stop_init') or 0,2),t1=t.get('t1'),exit=t.get('exit_ts'),why='/'.join(str(g[2]) for g in legs),pt=round(net,2)))
    at=[]
    for t in (sc['ai'] or {}).get('trades',[]):
        if t.get('exit_t') is None: continue
        at.append(dict(who='AI',d=d,rule='재량',side=t['side'],t=t['entry_t'],px=t['fill'],stop=t.get('stop'),t1=t.get('target'),exit=t['exit_t'],why=t['why'],pt=round(t['pnl']-COST,2),gross=t['pnl']))
    trades_all+=mt+at
    pm=(ev.get('premarket') or {}).get('live') or {}
    on=(ev.get('overnight') or {}).get('live') or {}
    o=ev['ohlc']
    rows.append(dict(d=d, act=ev['actual_dir'], open=o['open'],close=o['close'],rng=o['range'],prev=ev.get('prev_close'),
        m_bias=SD[m['decision'].get('bias')], m_first=mt[0]['side'] if mt else '—', m_n=len(mt), m_w=sum(x['pt']>0 for x in mt), m_pt=round(sum(x['pt'] for x in mt),2),
        ai_pm=pm.get('dir','—'), ai_pm_hit=pm.get('dir_hit'), ai_on=on.get('dir','—'), ai_on_hit=on.get('dir_hit'),
        ai_n=len(at), ai_w=sum(x['pt']>0 for x in at), ai_pt=round(sum(x['pt'] for x in at),2), ai_first=at[0]['side'] if at else '—',
        vs=(ev.get('rival') or {}).get('main_pt')))
json.dump(dict(rows=rows,trades=trades_all),open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False,indent=1,default=str)
for x in rows: print(x)
