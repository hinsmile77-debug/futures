# B. 당일 거래중단 — 누적 G 도달 중단 / 고점 A 뒤 K 반납 중단 (R3 대리, 만원)
import pickle, random, sys
import daystop
ds,out=pickle.load(open('trail.pkl','rb'))
mid=ds[len(ds)//2]; H1=[d for d in ds if d<mid]; H2=[d for d in ds if d>=mid]
cfgs=[('기준',None,None,None)]+[('G%d'%g,g*1e4,None,None) for g in (30,50,80,100,150,200,300)] \
    +[('A%dK%d'%(a,k),None,a*1e4,k*1e4) for a in (30,50,80,100,150) for k in (20,30,50,80) if k<=a]
def run(tr,c):
    return {d:daystop.apply([n for _,n in tr[d]],G=c[1],A=c[2],K=c[3])[0] for d in ds}
def mdd(dn):
    c=p=m=0
    for d in ds: c+=dn[d]; p=max(p,c); m=min(m,c-p)
    return m
sel=[('MAIN',(999,0,'keep'))]+[tuple(a) for a in eval(sys.argv[1])] if len(sys.argv)>1 else [('MAIN',(999,0,'keep')),('X4NF',(999,0,'keep'))]
for base,g in sel:
  print('\n=== %s trail=%s ==='%(base,g))
  print('%-9s '%'규칙'+' | '.join('px%.1f 합/H1/H2/MDD'%x for x in (0.5,1.0,1.5)))
  score={}
  for c in cfgs:
    cells=[]; tot=0
    for x in (0.5,1.0,1.5):
        dn=run(out[(x,base,g)][1],c)
        s=sum(dn.values()); tot+=s
        cells.append('%+5.0f/%+5.0f/%+5.0f/%+5.0f'%(s/1e4,sum(dn[d] for d in H1)/1e4,sum(dn[d] for d in H2)/1e4,mdd(dn)/1e4))
    score[c[0]]=tot
    print('%-9s '%c[0]+' | '.join(cells))
