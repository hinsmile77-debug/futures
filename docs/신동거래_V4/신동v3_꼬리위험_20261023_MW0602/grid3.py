import sys; sys.path.insert(0,sys.argv[1]); import sim, sim2
b=sim2.run({}); bd={d:sum(t['pt'] for t in v) for d,v in b.items()}; B=sim.summ(b,'')
A=[d for d in sorted(bd) if d<'2026-10-12']; Bh=[d for d in sorted(bd) if d>='2026-10-12']
print('BE문턱 | 손절ATR | 합계 Δ | 전반Δ | 후반Δ | 10/19~ | 최악일 | 최악거래 | ≤-10건 | MDD | 10/23 | 10/01 | 10/07')
for be in (None,2.0,2.5,3.0,3.5,4.0):
  for cm in (0.6,0.5,0.4):
    lc={'cat_mult':cm}
    if be: lc['be_at']=be
    o=sim2.run({'leg1':lc,'leg2':lc}); s=sim.summ(o,''); od={d:sum(t['pt'] for t in v) for d,v in o.items()}
    print(f"{be} | {cm} | {s['sum']-B['sum']:+.1f} | {sum(od[d]-bd[d] for d in A):+.1f} | {sum(od[d]-bd[d] for d in Bh):+.1f} | {s['oos']:+.1f} | {s['worst_day']:.1f} | {s['worst_tr']:.1f} | {s['n_le_m10']} | {s['mdd']:.1f} | {od['2026-10-23']:+.1f} | {od['2026-10-01']:+.1f} | {od['2026-10-07']:+.1f}")
