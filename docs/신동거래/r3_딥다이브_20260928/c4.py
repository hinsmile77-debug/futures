import pickle, random
import daystop
ds,out=pickle.load(open('trail.pkl','rb'))
mid=ds[len(ds)//2]; H1=[d for d in ds if d<mid]; H2=[d for d in ds if d>=mid]
def S(dn,dd): return sum(dn[d] for d in dd)
def mdd(dn):
    c=p=m=0
    for d in ds: c+=dn[d]; p=max(p,c); m=min(m,c-p)
    return m
def boot(diff):
    random.seed(11); bs=sorted(sum(random.choice(diff) for _ in diff) for _ in range(2000)); return sum(1 for s in bs if s<=0)/2000
BASE=(999,0,'keep')
print('## A. 거래 단위 트레일링 (만원)')
for base in ('MAIN','X4NF'):
  for x in (0.5,1.0,1.5):
    b=out[(x,base,BASE)][0]
    keys=[k for k in out if k[0]==x and k[1]==base]
    rank=sorted(keys,key=lambda k:-S(out[k][0],ds))
    h1best=max(keys,key=lambda k:S(out[k][0],H1))
    print('\n[%s px%.1f] 기준 합 %+.0f (H1 %+.0f / H2 %+.0f) MDD %+.0f'%(base,x,S(b,ds)/1e4,S(b,H1)/1e4,S(b,H2)/1e4,mdd(b)/1e4))
    for k in rank[:6]:
        dn=out[k][0]; diff=[dn[d]-b[d] for d in ds]
        print('   act%-3s dist%-4s %-4s 합 %+6.0f H1 %+6.0f H2 %+6.0f MDD %+6.0f P(Δ≤0) %.2f'%(k[2][0],k[2][1],k[2][2],S(dn,ds)/1e4,S(dn,H1)/1e4,S(dn,H2)/1e4,mdd(dn)/1e4,boot(diff)))
    dn=out[h1best][0]
    print('   ▶ H1에서 고른 최선 act%s dist%s %s → H2 %+.0f (기준 H2 %+.0f)'%(h1best[2][0],h1best[2][1],h1best[2][2],S(dn,H2)/1e4,S(b,H2)/1e4))
pickle.dump(None,open('c4.done','wb'))
