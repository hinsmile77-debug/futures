import r3lab as R, random, pickle
ds=R.dates(); mid=ds[len(ds)//2]
T=lambda v: v is True
P={
 'P0 기준(현행 R3)': None,
 'P1 추세순응(trend)': lambda f:T(f['trend_align']),
 'P2 오전추세순응(am)': lambda f:T(f['am_align']),
 'P3 맥점flip금지': lambda f:not f['flip'],
 'P4 미륵일치만': lambda f:T(f['mk_align']),
 'P5 미륵반대금지': lambda f:f['mk_align'] is not False,
 'P6 trend+flip금지': lambda f:T(f['trend_align']) and not f['flip'],
 'P7 am+trend': lambda f:T(f['am_align']) and T(f['trend_align']),
 'P8 am+flip금지': lambda f:T(f['am_align']) and not f['flip'],
 'P9 trend+미륵반대금지': lambda f:T(f['trend_align']) and f['mk_align'] is not False,
 'P10 am+미륵반대금지': lambda f:T(f['am_align']) and f['mk_align'] is not False,
 'P11 맥점당손실1회까지': lambda f:f['lvl_losses']==0,
}
res={}
for x in (0.5,1.0,1.5):
    for name,pol in P.items():
        byday={}
        for d in ds:
            byday[d]=R.run_r3(d,'px',policy=pol,start_busy='09:29',x=x)
        res[(x,name)]=byday
pickle.dump(res,open('pol.pkl','wb'))
def summ(x):
    base=res[(x,'P0 기준(현행 R3)')]
    b0={d:sum(t['net'] for t in v) for d,v in base.items()}
    print('\n=== px%.1f ==='%x)
    print('%-22s %4s %5s %8s %8s %8s %8s %18s %6s'%('정책','n','승률','순(만)','H1','H2','최악일','Δ기준 95%CI(만)','P(Δ≤0)'))
    for name in P:
        by=res[(x,name)]; tr=[t for v in by.values() for t in v]
        dn={d:sum(t['net'] for t in v) for d,v in by.items()}
        n=len(tr); w=sum(1 for t in tr if t['net']>0)
        h1=sum(v for d,v in dn.items() if d<mid); h2=sum(v for d,v in dn.items() if d>=mid)
        diff=[dn[d]-b0[d] for d in ds]
        random.seed(7); bs=[]
        for _ in range(3000):
            s=sum(random.choice(diff) for _ in ds); bs.append(s)
        bs.sort()
        print('%-22s %4d %4.0f%% %+8.0f %+8.0f %+8.0f %+8.0f  [%+5.0f,%+5.0f] %5.2f'%(name,n,100*w/max(n,1),sum(dn.values())/1e4,h1/1e4,h2/1e4,min(dn.values())/1e4,bs[75]/1e4,bs[2925]/1e4,sum(1 for s in bs if s<=0)/3000))
for x in (0.5,1.0,1.5): summ(x)
