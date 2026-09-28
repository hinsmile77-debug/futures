import sys; sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
from strategy.shindong import runner, engine
import daystop
R=r"C:\Users\82108\PycharmProjects\futures\data\db\\"
fd=['2026-09-21','2026-09-22','2026-09-23','2026-09-28']
res={d:runner.compute(d,R+'raw_data.db',R+'option_flow.db',R+'premarket_levels.db')['results'] for d in fd}
for v in ('MAIN','SHADOW_E2F2','SHADOW_X4NF'):
    seq={d:[engine.trade_net(t) for t in sorted(res[d][v]['trades'],key=lambda t:t['entry_ts'])] for d in fd}
    print('\n',v,{d[5:]:[round(n/1e4) for n in s] for d,s in seq.items()})
    for G in (None,50e4,80e4,100e4,150e4):
        r=[daystop.apply(seq[d],G=G) for d in fd]
        print('  G=%s  합 %+.0f만  | %s'%(G and int(G/1e4),sum(x[0] for x in r)/1e4,' '.join('%+.0f(%d)'%(x[0]/1e4,x[1]) for x in r)))
