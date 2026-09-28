import pickle, random
ds,out=pickle.load(open('base.pkl','rb'))
mid=ds[len(ds)//2]
def bk(name,fn):
    print('\n##',name)
    for x in (0.5,1.0,1.5):
        rows=out[x]
        g={}
        for r in rows:
            try: k=fn(r)
            except Exception: k='NA'
            g.setdefault(k,[]).append(r)
        line=[]
        for k in sorted(g,key=str):
            v=g[k]; n=len(v); net=sum(r['net'] for r in v)
            a=[r['net'] for r in v if r['date']<mid]; b=[r['net'] for r in v if r['date']>=mid]
            line.append('%s: n=%d win=%.0f%% avg=%+.0f  H1 %+.0f(%d) H2 %+.0f(%d)'%(k,n,100*sum(1 for r in v if r['net']>0)/n,net/n/1e3, sum(a)/max(len(a),1)/1e3,len(a),sum(b)/max(len(b),1)/1e3,len(b)))
        print(' px%.1f'%x); print('   '+'\n   '.join(line))
def q(v,cuts):
    if v is None: return 'NA'
    for c in cuts:
        if v<c: return '<%s'%c
    return '>=%s'%cuts[-1]
bk('trend_align(진입방향=09:00대비 추세방향)',lambda r:r['trend_align'])
bk('am_align(09:00->09:30 방향 일치)',lambda r:r['am_align'])
bk('fx_align(외국인선물 당일누적 방향 일치)',lambda r:r['fx_align'])
bk('vwap_align(VWAP 쪽으로 되돌림)',lambda r:r['vwap_align'])
bk('mk_align(미륵이 앙상블 방향 일치)',lambda r:r['mk_align'])
bk('has_tgt',lambda r:r['has_tgt'])
bk('rr',lambda r:q(r['rr'],[1,2,4]))
bk('risk pt',lambda r:q(r['risk'],[2,3,5]))
bk('entries_n(같은 맥점 이전 진입수)',lambda r:min(r['entries_n'],2))
bk('lvl_losses(같은 맥점 이전 손실)',lambda r:min(r['lvl_losses'],2))
bk('flip(같은 맥점 방향 뒤집기)',lambda r:r['flip'])
bk('day_losses(당일 R3 누적 손실)',lambda r:min(r['day_losses'],2))
bk('n_prior',lambda r:min(r['n_prior'],3))
bk('outside(맥점 범위 밖)',lambda r:r['outside'])
bk('trend_atr',lambda r:q(r['trend_atr'],[0.3,0.6,1.0]))
bk('range_atr',lambda r:q(r['range_atr'],[0.5,0.8,1.2]))
bk('hour',lambda r:r['hour'])
bk('pos_in_range',lambda r:q(r['pos_in_range'],[0.2,0.5,0.8]))
bk('touch_n',lambda r:q(r['touch_n'],[2,4,8]))
