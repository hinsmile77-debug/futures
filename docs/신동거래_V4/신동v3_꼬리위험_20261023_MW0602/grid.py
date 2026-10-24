import sys,json; sys.path.insert(0,sys.argv[1]); import sim
base=sim.run({}); b=sim.summ(base,'기준 v3')
bd={d:sum(t['pt'] for t in v) for d,v in base.items()}
G=[('기준 v3',{}),
 ('손절 0.5ATR',{'cat_mult':0.5}),('손절 0.4ATR',{'cat_mult':0.4}),('손절 0.3ATR',{'cat_mult':0.3}),
 ('손절 상한 15pt',{'cat_cap':15}),('손절 상한 12pt',{'cat_cap':12}),
 ('본전이동 MFE≥3',{'be_at':3}),('본전이동 MFE≥4',{'be_at':4}),('본전이동 MFE≥5',{'be_at':5}),
 ('시간손절 60분',{'ts_min':60}),('시간손절 90분',{'ts_min':90}),('시간손절 120분',{'ts_min':120}),
 ('반전청산 R60',{'rev':'r60'}),('반전청산 누적',{'rev':'cum'}),('반전청산 둘중하나',{'rev':'both'}),
 ('추격필터 0.3ATR',{'chase':0.3}),('추격필터 0.5ATR',{'chase':0.5}),
 ('0.4ATR+반전R60',{'cat_mult':0.4,'rev':'r60'}),('0.4ATR+시간120',{'cat_mult':0.4,'ts_min':120}),
 ('반전R60+시간120',{'rev':'r60','ts_min':120}),('0.4ATR+반전R60+시간120',{'cat_mult':0.4,'rev':'r60','ts_min':120}),
]
print('안 | 거래 | 합계pt | Δ기준 | 10/19~ | 최악일 | 최악거래 | ≤-10pt건 | MDD | 승률 | PF | 10/23 | Δ(10/23제외) | 악화된날')
for lab,cfg in G:
    o=sim.run(cfg); s=sim.summ(o,lab)
    od={d:sum(t['pt'] for t in v) for d,v in o.items()}
    ex=sum(od[d]-bd[d] for d in od if d!='2026-10-23')
    worse=[f"{d[5:]}{od[d]-bd[d]:+.1f}" for d in od if od[d]-bd[d]<-0.5]
    print(f"{lab} | {s['n']} | {s['sum']:+.1f} | {s['sum']-b['sum']:+.1f} | {s['oos']:+.1f} | {s['worst_day']:.1f} | {s['worst_tr']:.1f} | {s['n_le_m10']} | {s['mdd']:.1f} | {s['win']}% | {s['pf']} | {s['d1023']:+.1f} | {ex:+.1f} | {' '.join(worse)}")
