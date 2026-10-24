import sys; sys.path.insert(0,sys.argv[1]); import sim, sim2
from strategy.shindong import families as F, spec as S
orig_rs=F._run_signal
def rs_be_free(d,sig,rule,stop_fn,trail,tp,max_trades,**kw):
    """BE 청산은 상한에 세지 않는다: 상한을 넉넉히 두고, 진입 직전 '비BE 거래 수' 로 다시 막는다."""
    real={'n':0}
    def gate(k, _s=sig):
        return _s(k)
    out=orig_rs(d,sig,rule,stop_fn,trail,tp,max_trades+10,**kw)
    keep=[]; n=0
    for t in out:
        if n>=max_trades: break
        keep.append(t)
        if 'BE' not in (t['legs'][0].get('reason') or ''): n+=1
    return keep
b=sim2.run({}); bd={d:sum(t['pt'] for t in v) for d,v in b.items()}; B=sim.summ(b,'')
A=[d for d in sorted(bd) if d<'2026-10-12']; Bh=[d for d in sorted(bd) if d>='2026-10-12']
def show(lab,o):
    s=sim.summ(o,''); od={d:sum(t['pt'] for t in v) for d,v in o.items()}
    print(f"{lab} | {s['n']} | {s['sum']:+.1f} | {s['sum']-B['sum']:+.1f} | {sum(od[d]-bd[d] for d in A):+.1f} | {sum(od[d]-bd[d] for d in Bh):+.1f} | {s['oos']:+.1f} | {s['worst_day']:.1f} | {s['worst_tr']:.1f} | {s['mdd']:.1f} | {od['2026-10-23']:+.1f} | {sum(v>0 for v in od.values())}/21")
print('안 | 거래 | 합계 | Δ | 전반Δ | 후반Δ | 10/19~ | 최악일 | 최악거래 | MDD | 10/23 | 이익일')
show('기준 v3 상한3',b)
for mx in (4,5):
    S.FLOW_MAX_TRADES=mx; show(f'기준 v3 상한{mx}(공정대조)',sim2.run({}))
S.FLOW_MAX_TRADES=3
for be in (2.5,3.0,3.5):
    F._run_signal=rs_be_free
    show(f'BE{be} · BE청산 상한 제외',sim2.run({'leg1':{'be_at':be},'leg2':{'be_at':be}}))
    F._run_signal=orig_rs
    show(f'BE{be} · 상한 그대로',sim2.run({'leg1':{'be_at':be},'leg2':{'be_at':be}}))
