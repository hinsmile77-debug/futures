import r3lab as R, trail, pickle
ds,out=pickle.load(open('trail.pkl','rb')); mid=ds[len(ds)//2]
fd=['2026-09-21','2026-09-22','2026-09-23','2026-09-28']
def mdd(dn):
    c=p=m=0
    for d in ds: c+=dn[d]; p=max(p,c); m=min(m,c-p)
    return m
cands=[(999,0),(3,1),(4,1),(3,3),(4,3),(4,4),(5,3),(5,4),(6,4),(8,4)]
print('%-9s | 흐름4일 R3만(R2는 현행) | 74일 대리 합/H2/MDD px0.5 · px1.0 · px1.5'%'act/dist')
for a,b in cands:
    fn=None if a==999 else trail.make(a,b)
    fl=[sum(t['net'] for t in R.run_r3(d,'flow',start_busy=R.r2_busy(d),trade_fn=fn)) for d in fd]
    cells=[]
    for x in (0.5,1.0,1.5):
        dn=out[(x,'MAIN',(a,b,'keep') if a!=999 else (999,0,'keep'))][0]
        cells.append('%+5.0f/%+5.0f/%+5.0f'%(sum(dn.values())/1e4,sum(dn[d] for d in ds if d>=mid)/1e4,mdd(dn)/1e4))
    print('%-9s | %+5.0f (%s) | %s'%('%s/%s'%(a,b) if a!=999 else '현행',sum(fl)/1e4,' '.join('%+.0f'%(v/1e4) for v in fl),' · '.join(cells)))
