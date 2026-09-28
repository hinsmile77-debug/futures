import pickle, random
ds,names,out=pickle.load(open('r2.pkl','rb'))
days=sorted({k[0] for k in out if k[1]=='dir'})
mid=days[len(days)//2]
def val(name,p,dd):
    """방향 적중률 p 시나리오: 옳은 방향(15:05 종가 기준) 결과 × p + 틀린 방향 × (1−p)."""
    s=0
    for d in dd:
        r=out[(d,'dir')]
        s+=p*out[(d,r,name)]+(1-p)*out[(d,-r,name)]
    return s
print('거래일',len(days))
for p in (0.5,0.6,0.7,1.0):
    base=val('현행',p,days)
    rk=sorted(names,key=lambda n:-val(n,p,days))
    print('\n## 적중률 %.0f%% — 현행 %+.0f만 (H1 %+.0f / H2 %+.0f)'%(p*100,base/1e4,val('현행',p,[d for d in days if d<mid])/1e4,val('현행',p,[d for d in days if d>=mid])/1e4))
    for n in rk[:7]+[x for x in ('트레일4/4','트레일4/1','익절10','익절20') if x not in rk[:7]]:
        print('   %-9s 합 %+6.0f  H1 %+6.0f  H2 %+6.0f  (순위 %d)'%(n,val(n,p,days)/1e4,val(n,p,[d for d in days if d<mid])/1e4,val(n,p,[d for d in days if d>=mid])/1e4,rk.index(n)+1))
