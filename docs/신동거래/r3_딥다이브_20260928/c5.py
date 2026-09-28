# 모드·발동·거리별 요약(px 3종 평균 개선, 만원) — 고원 확인
import pickle
ds,out=pickle.load(open('trail.pkl','rb'))
BASE=(999,0,'keep')
for base in ('MAIN','X4NF'):
  for m in ('keep','no2'):
    print('\n[%s %s] 행=act 열=dist : px0.5/1.0/1.5 기준 대비 개선 평균(만원)'%(base,m))
    print('act\dist '+' '.join('%7s'%b for b in (1,1.5,2,3,4)))
    for a in (2,3,4,5,6,8):
        row=[]
        for b in (1,1.5,2,3,4):
            if b>a: row.append('%7s'%'-'); continue
            v=[sum(out[(x,base,(a,b,m))][0].values())-sum(out[(x,base,BASE)][0].values()) for x in (0.5,1.0,1.5)]
            row.append('%+7.0f'%(sum(v)/3/1e4))
        print('%-8s '%a+' '.join(row))
