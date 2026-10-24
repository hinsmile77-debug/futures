import sys,json,sqlite3; sys.path.insert(0,sys.argv[1]); import sim
base=json.load(open(sys.argv[2],encoding='utf-8'))
con=sqlite3.connect('data/db/raw_data.db')
ds=sorted(base)
print('날짜 방향 진입 pt | 갭(시가-전일종가) 갭동조 | FX변화(09:00→진입,계약) FX동조 | 09:00→진입 이동 | 개장~진입 고저폭/ATR')
for i,d in enumerate(ds):
    D,L=sim.frame(d); t=[x for x in base[d] if x['rule']=='FLOW']
    if not t: continue
    t=t[0]; s=t['side']
    pc=con.execute("select close from raw_candles where ts<? order by ts desc limit 1",(d,)).fetchone()[0]
    op=L['0850'].get('open_price')
    gap=op-pc
    fx=D.fx; f0=fx.get('09:00') or next((fx[k] for k in sorted(fx) if k>='09:00'),None); f1=max((fx[k] for k in [k for k in sorted(fx) if k<=t['t']][-1:]),default=None)
    fxd=None if f0 is None or f1 is None else f1-f0
    rng=max(D.h[k] for k in D.idx if k<=t['t'] and k in D.h)-min(D.l[k] for k in D.idx if k<=t['t'] and k in D.h)
    print(d[5:], 'B' if s>0 else 'S', t['t'], f"{t['pt']:+.2f}", '|', f"{gap:+.1f}", 'Y' if gap*s>0 else 'N','|', fxd, None if fxd is None else ('Y' if fxd*s>0 else 'N'), '|', (round((t['px']-D.c['09:00'])*s,1) if '09:00' in D.c else None), '|', round(rng/L['0850']['atr14'],2))
