import r3lab as R
from s7lib import struct1, T
fd=['2026-09-21','2026-09-22','2026-09-23','2026-09-28']
F={'현행 R3':None,'F2(흐름순응)':lambda f:T(f['flow_align']),'flip금지':lambda f:not f['flip'],'미륵반대금지':lambda f:f['mk_align'] is not False}
for xn,xf in (('현행청산',None),('X4',struct1)):
    for fn,ff in F.items():
        tot=0; cells=[]
        for d in fd:
            v=R.run_r3(d,'flow',policy=ff,start_busy=R.r2_busy(d),tgt_fn=xf)
            s=sum(t['net'] for t in v); tot+=s
            cells.append('%s %d건 %+.0f'%(d[5:],len(v),s/1e4))
        print('%-8s %-12s 합 %+6.0f만 | %s'%(xn,fn,tot/1e4,' | '.join(cells)))
print()
for xn,xf in (('현행',None),('X4',struct1)):
  for fn,ff in (('무필터',None),('flip금지',F['flip금지']),('F2',F['F2(흐름순응)'])):
    print('--',xn,fn)
    for t in R.run_r3('2026-09-28','flow',policy=ff,start_busy=R.r2_busy('2026-09-28'),tgt_fn=xf):
        print('   %s %+d L0=%s e=%.2f stop=%.2f t1=%s t2=%s %s %+.0f mfe=%.2f'%(t['ent'],t['side'],t['L0'],t['e'],t['stop'],t['t1'] and round(t['t1'],2),t['t2'] and round(t['t2'],2),t['reasons'],t['net'],t['mfe']))
