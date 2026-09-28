import r3lab as R, random
from s7lib import struct1, T
ds=R.dates()
C={'현행':(None,None),'X4':(None,struct1),'X4+flip금지':(lambda f:not f['flip'],struct1),
   'X4+trend순응':(lambda f:T(f['trend_align']),struct1),
   'X4+flip금지+미륵반대금지':(lambda f:not f['flip'] and f['mk_align'] is not False,struct1),
   'X4+flip금지+일손실2회중단':(lambda f:not f['flip'] and f['day_losses']<2,struct1),
   '현행+flip금지':(lambda f:not f['flip'],None)}
for x in (0.5,1.0,1.5):
    print('\n=== px%.1f  월별 순손익(만) ==='%x)
    base=None
    for n,(pf,tf) in C.items():
        m={}; dn={}
        for d in ds:
            s=sum(t['net'] for t in R.run_r3(d,'px',policy=pf,start_busy='09:29',x=x,tgt_fn=tf))
            m[d[:7]]=m.get(d[:7],0)+s; dn[d]=s
        if base is None: base=dn
        diff=[dn[d]-base[d] for d in ds]; random.seed(5)
        bs=sorted(sum(random.choice(diff) for _ in ds) for _ in range(2000))
        # 최대낙폭(일 누적)
        cum=pk=mdd=0
        for d in ds: cum+=dn[d]; pk=max(pk,cum); mdd=min(mdd,cum-pk)
        print('%-26s 합%+6.0f MDD%+6.0f P(Δ≤0)%.2f | '%(n,sum(dn.values())/1e4,mdd/1e4,sum(1 for s in bs if s<=0)/2000)+' '.join('%s:%+5.0f'%(k[5:],v/1e4) for k,v in sorted(m.items())))
