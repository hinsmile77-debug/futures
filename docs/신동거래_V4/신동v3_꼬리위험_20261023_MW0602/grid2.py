import sys; sys.path.insert(0,sys.argv[1]); import sim, sim2
b=sim2.run({}); bd={d:sum(t['pt'] for t in v) for d,v in b.items()}; B=sim.summ(b,'')
A=[d for d in sorted(bd) if d<'2026-10-12']; Bh=[d for d in sorted(bd) if d>='2026-10-12']
G=[('기준 v3 (2다리 동일)',{}),
 ('A 양다리 BE@3',{'leg1':{'be_at':3},'leg2':{'be_at':3}}),
 ('B 1다리만 BE@3',{'leg1':{'be_at':3}}),
 ('B 1다리만 BE@2.5',{'leg1':{'be_at':2.5}}),('B 1다리만 BE@3.5',{'leg1':{'be_at':3.5}}),('B 1다리만 BE@4',{'leg1':{'be_at':4}}),
 ('C 양다리 0.4ATR',{'leg1':{'cat_mult':0.4},'leg2':{'cat_mult':0.4}}),
 ('D 1다리 BE@3 + 양다리 0.4ATR',{'leg1':{'be_at':3,'cat_mult':0.4},'leg2':{'cat_mult':0.4}}),
 ('D 1다리 BE@3 + 양다리 0.45ATR',{'leg1':{'be_at':3,'cat_mult':0.45},'leg2':{'cat_mult':0.45}}),
 ('D 1다리 BE@3 + 양다리 0.35ATR',{'leg1':{'be_at':3,'cat_mult':0.35},'leg2':{'cat_mult':0.35}}),
 ('E 1다리 BE@3+0.4ATR · 2다리 원형',{'leg1':{'be_at':3,'cat_mult':0.4}}),
]
print('안 | 합계 | Δ | 전반(9/21-10/08) Δ | 후반(10/12-10/23) Δ | 10/19~ | 최악일 | 최악거래 | ≤-10건 | MDD | 10/23 | 이익일 | 악화일(≤-3)')
for lab,cfg in G:
    o=sim2.run(cfg); s=sim.summ(o,lab); od={d:sum(t['pt'] for t in v) for d,v in o.items()}
    da=sum(od[d]-bd[d] for d in A); db=sum(od[d]-bd[d] for d in Bh)
    w=[f"{d[5:]}{od[d]-bd[d]:+.1f}" for d in od if od[d]-bd[d]<=-3]
    print(f"{lab} | {s['sum']:+.1f} | {s['sum']-B['sum']:+.1f} | {da:+.1f} | {db:+.1f} | {s['oos']:+.1f} | {s['worst_day']:.1f} | {s['worst_tr']:.1f} | {s['n_le_m10']} | {s['mdd']:.1f} | {s['d1023']:+.1f} | {sum(v>0 for v in od.values())}/{len(od)} | {' '.join(w)}")
    if lab.startswith('E') or lab.startswith('B 1다리만 BE@3 ') or lab=='B 1다리만 BE@3':
        print('   일별:', ' '.join(f"{d[5:]}:{od[d]:+.1f}({od[d]-bd[d]:+.1f})" for d in sorted(od)))
