import sys; sys.path.insert(0,sys.argv[1]); import sim3, sim
b=sim3.run({}); bd={d:sum(t['pt'] for t in v) for d,v in b.items()}; B=sim.summ(b,'')
A=[d for d in sorted(bd) if d<'2026-10-12']; H=[d for d in sorted(bd) if d>='2026-10-12']
def t2(o): return sum(t['pt'] for v in o.values() for t in v if t['mfe']<3 and t['why']!='BE')
def show(lab,cfg):
    o=sim3.run(cfg); s=sim.summ(o,''); od={d:sum(t['pt'] for t in v) for d,v in o.items()}
    tr=[t for v in o.values() for t in v]
    mx=max(t['mae'] for t in tr); n_cut=sum(t['why'] in ('LVSL','REV','MAEX') for t in tr)
    avg_stop=sum(t['stopd'] for t in tr)/len(tr)
    print(f"{lab} | {s['n']} | {s['sum']:+.1f} | {s['sum']-B['sum']:+.1f} | {sum(od[d]-bd[d] for d in A):+.1f} | {sum(od[d]-bd[d] for d in H):+.1f} | {s['oos']:+.1f} | {s['worst_day']:.1f} | {s['worst_tr']:.1f} | {mx:.1f} | {avg_stop:.1f} | {n_cut} | {t2(o):+.1f}")
print('안 | 거래 | 합계 | Δ | 전반Δ | 후반Δ | 10/19~ | 최악일 | 최악거래 | 최대보유역행 | 평균초기손절폭 | 컷 발동 | 유형②합')
show('새 기준(BE3·상한제외)',{})
for src in ('lv','ext','both','all'):
    for md in (2.0,4.0):
        show(f'[2] 구조손절 {src} 최소{md}·버퍼1.5 장중',{'struct':src,'min_dist':md})
        show(f'[2] 구조손절 {src} 최소{md}·버퍼1.5 종가',{'struct':src,'min_dist':md,'struct_close':True})
show('[3] 콜풋 반대신호 청산(본전 전)',{'rev':'opp'})
show('[3] 콜풋 반대신호 + 역행≥3 청산',{'rev':'opp_adv','rev_mae':3})
show('[3] 콜풋 반대신호 청산 · 방향금지 안 함',{'rev':'opp','ban_cut':False})
for m in (0.2,0.25,0.3,0.35,0.4):
    show(f'[4a] 본전 전 역행컷 {m}×ATR',{'mae_cut':m})
show('[4a] 역행컷 0.3×ATR · 방향금지 안 함',{'mae_cut':0.3,'ban_cut':False})
show('[4b] 진입 확인(신호 2봉 지속+가격 동조)',{'confirm':True})
