def apply(nets, G=None, A=None, K=None):
    """nets: 진입순 거래 순손익. G: 누적 ≥G 이면 중단. (A,K): 고점 ≥A 뒤 고점−K 이하로 밀리면 중단."""
    cum=peak=0.0; kept=[]
    for n in nets:
        kept.append(n); cum+=n; peak=max(peak,cum)
        if G is not None and cum>=G: break
        if A is not None and peak>=A and peak-cum>=K: break
    return sum(kept), len(kept)
