import r3lab as R, trail, random, pickle
ds,out=pickle.load(open('trail.pkl','rb'))
mid=ds[len(ds)//2]
def mdd(dn):
    c=p=m=0
    for d in ds: c+=dn[d]; p=max(p,c); m=min(m,c-p)
    return m
nf=lambda f: not f['flip']
print('%-22s '%'구성'+' | '.join('px%.1f 합/H2/MDD P'%x for x in (0.5,1.0,1.5)))
for name,pol,fn in (('MAIN 현행',None,None),('X4NF',None,'x4'),('MAIN+트레일4/1',None,trail.make(4,1)),('NF+트레일4/1',nf,trail.make(4,1)),('NF+트레일3/1',nf,trail.make(3,1)),('NF+트레일5/1',nf,trail.make(5,1))):
    cells=[]
    for x in (0.5,1.0,1.5):
        b=out[(x,'MAIN',(999,0,'keep'))][0]
        if fn=='x4': dn=out[(x,'X4NF',(999,0,'keep'))][0]
        else: dn={d:sum(t['net'] for t in R.run_r3(d,'px',policy=pol,start_busy='09:29',x=x,trade_fn=fn)) for d in ds}
        diff=[dn[d]-b[d] for d in ds]; random.seed(2)
        bs=[sum(random.choice(diff) for _ in ds) for _ in range(2000)]
        cells.append('%+5.0f/%+5.0f/%+5.0f %.2f'%(sum(dn.values())/1e4,sum(dn[d] for d in ds if d>=mid)/1e4,mdd(dn)/1e4,sum(1 for s in bs if s<=0)/2000))
    print('%-22s '%name+' | '.join(cells))
