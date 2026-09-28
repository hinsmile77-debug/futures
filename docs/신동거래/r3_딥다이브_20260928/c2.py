import r3lab as R, trail, pickle, itertools, time
ds=R.dates(); mid=ds[len(ds)//2]
out={}
t0=time.time()
grid=[(999,0,'keep')]+[(a,b,m) for m in ('keep','no2') for a in (2,3,4,5,6,8) for b in (1,1.5,2,3,4) if b<=a]
for x in (0.5,1.0,1.5):
  for base in ('MAIN','X4NF'):
    for g in grid:
        fn=None if g[0]==999 else trail.make(*g)
        dn={}; tr={}
        for d in ds:
            v=R.run_r3(d,'px',start_busy='09:29',x=x,trade_fn=fn,x4nf=(base=='X4NF'))
            dn[d]=sum(t['net'] for t in v); tr[d]=[(t['ent'],t['net']) for t in v]
        out[(x,base,g)]=(dn,tr)
  print('px',x,'done',round(time.time()-t0))
pickle.dump((ds,out),open('trail.pkl','wb'))
