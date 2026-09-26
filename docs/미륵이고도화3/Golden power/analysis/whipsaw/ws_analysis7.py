# -*- coding: utf-8 -*-
"""7차: 6차에서 살아남은 두 가지만 확증 검정.
   A) C3→i+2 (GP_LONG_GB90_D2C) — 로그와 무관하므로 전 표본 252일로
   B) 개인풋 Δ20 채널 — 6차에서 z=-3.0 으로 유일 생존, 반기 분할·포지션 단위로 재확인
"""
import os
import numpy as np, pandas as pd
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40)
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), 'GP_test')   # [MW0601 631차] pkl/npy 캐시 — 커밋 제외(GP_test/.gitignore)
os.makedirs(CACHE, exist_ok=True)
COST = 0.246018
rng = np.random.default_rng(7)

S = pd.read_pickle(CACHE + '/signals.pkl').reset_index(drop=True)
D = pd.read_pickle(CACHE + '/panel.pkl'); DC = D.close.values


def lag(col, k):
    v = D[col].values; out = np.full(len(S), np.nan)
    ok = S.i.values - k >= 0; out[ok] = v[S.row.values[ok] - k]; return out


for k in ['rt_call', 'rt_put', 'fi_fut']:
    S[k + '_d20'] = S[k].values - lag(k, 20)
C3 = (S.cl2 > S.close).values


def bt(mask, mode, days):
    T = S[mask]; pnl = []; dl = []
    for s, g in T.groupby('s'):
        busy = -1
        for qq, row, i, i5, n in zip(g.index.values, g.row.values, g.i.values, g.i1505.values, g.n.values):
            if mode == 'base': off = 0
            elif mode == 'd2': off = 2
            elif mode == 'c3d2':
                if not C3[qq]: continue
                off = 2
            a = int(i) + off
            if a <= busy or a >= n: continue
            j = min(a + 90, int(i5))
            if j <= a: continue
            pnl.append(DC[int(row) + (j - int(i))] - DC[int(row) + off] - COST); dl.append(s); busy = j
    p = pd.Series(pnl, index=dl)
    return p, p.groupby(level=0).sum().reindex(days).fillna(0)


def boot(d, nrep=5000):
    v = d.values; idx = rng.integers(0, len(v), (nrep, len(v)))
    return np.percentile(v[idx].sum(axis=1), [2.5, 97.5])


def worstk(dd, k=3):
    return dd.sum() - dd.nsmallest(k).sum()


print('=' * 100)
print('A) C3 → i+2  — 전 표본 (로그 무관)')
print('=' * 100)
ALL = np.ones(len(S), bool)
for nm, m in [('전체 252일', ALL),
              ('전반 (~2026-03-20)', (S.s.values <= '2026-03-20')),
              ('후반 (2026-03-23~)', (S.s.values > '2026-03-20'))]:
    days = sorted(S.s[m].unique())
    bp, bd = bt(m, 'base', days)
    rows = []
    for tag, mode in [('기준', 'base'), ('무조건 i+2', 'd2'), ('C3→i+2', 'c3d2')]:
        p, dd = bt(m, mode, days)
        d = dd - bd
        lo, hi = (np.nan, np.nan) if mode == 'base' else boot(d)
        rows.append(dict(구간=nm, 규칙=tag, n=len(p), 총손익=p.sum(), 거래당=p.mean(),
                         승률=(p > 0).mean(), MDD=(dd.cumsum().cummax() - dd.cumsum()).max(),
                         최악3일제외=worstk(dd), Δ=d.sum(), ci_lo=lo, ci_hi=hi,
                         우세일=int((d > 0).sum()), 열세일=int((d < 0).sum())))
    print(pd.DataFrame(rows).round(2).to_string(index=False)); print()

print('=' * 100)
print('B) 개인풋 Δ20 채널 — 6차 유일 생존 셀(z=-3.03)의 확증')
print('=' * 100)
sub = S.rt_put_d20.notna().values
KEEP = (S.rt_put_d20 > 0).values          # 개인이 풋을 사는 중 = 통과(역지표 가설)


def decompose(x, keep, days, nrep=4000):
    x = np.asarray(x, float); keep = np.asarray(keep, bool); days = np.asarray(days)
    ok = ~np.isnan(x); x, keep, days = x[ok], keep[ok], days[ok]
    obs = x[keep].mean() - x[~keep].mean()
    groups = [np.where(days == d)[0] for d in np.unique(days)]
    sims = np.empty(nrep)
    for r in range(nrep):
        k2 = np.empty_like(keep)
        for ix in groups:
            k2[ix] = keep[ix][rng.permutation(len(ix))]
        sims[r] = x[k2].mean() - x[~k2].mean()
    comp = sims.mean(); within = obs - comp
    return dict(n_keep=int(keep.sum()), n_excl=int((~keep).sum()), keep=x[keep].mean(), excl=x[~keep].mean(),
                obs=obs, comp=comp, within=within, z=within / sims.std(),
                p_within=np.mean(np.abs(sims - comp) >= abs(within)))


rows = []
mid = '2026-07-15'
for nm, m in [('전체 82일', sub),
              ('전반 (~07-14)', sub & (S.s.values < mid)),
              ('후반 (07-15~)', sub & (S.s.values >= mid))]:
    r = decompose(S.r90.values[m], KEEP[m], S.s.values[m]); r['구간'] = nm; rows.append(r)
print('신호 단위 (통과 = 개인풋 Δ20 > 0, r90 from i)')
print(pd.DataFrame(rows)[['구간', 'n_keep', 'n_excl', 'keep', 'excl', 'obs', 'comp', 'within', 'z', 'p_within']].round(3).to_string(index=False))

print('\n포지션 단위 (개인풋 Δ20 ≤ 0 인 신호 차단)')
days = sorted(S.s[sub].unique())
bp, bd = bt(sub, 'base', days)
mask = sub & KEEP
p, dd = bt(mask, 'base', days)
d = dd - bd; lo, hi = boot(d)
print(pd.DataFrame([dict(규칙='기준', n=len(bp), 총손익=bp.sum(), MDD=(bd.cumsum().cummax() - bd.cumsum()).max()),
                    dict(규칙='풋Δ20≤0 차단', n=len(p), 총손익=p.sum(), MDD=(dd.cumsum().cummax() - dd.cumsum()).max(),
                         Δ=d.sum(), ci_lo=lo, ci_hi=hi, 우세일=int((d > 0).sum()), 열세일=int((d < 0).sum()))]).round(2).to_string(index=False))

print('\n결합: 풋Δ20>0 통과 + C3→i+2')
T = S[mask]; pnl = []; dl = []
for s, g in T.groupby('s'):
    busy = -1
    for qq, row, i, i5, n in zip(g.index.values, g.row.values, g.i.values, g.i1505.values, g.n.values):
        if not C3[qq]: continue
        a = int(i) + 2
        if a <= busy or a >= n: continue
        j = min(a + 90, int(i5))
        if j <= a: continue
        pnl.append(DC[int(row) + (j - int(i))] - DC[int(row) + 2] - COST); dl.append(s); busy = j
p2 = pd.Series(pnl, index=dl); dd2 = p2.groupby(level=0).sum().reindex(days).fillna(0)
d2 = dd2 - bd; lo2, hi2 = boot(d2)
pc3, ddc3 = bt(sub, 'c3d2', days); dc3 = ddc3 - bd
print(pd.DataFrame([
    dict(규칙='C3→i+2 (풋 무관)', n=len(pc3), 총손익=pc3.sum(), MDD=(ddc3.cumsum().cummax() - ddc3.cumsum()).max(), Δ=dc3.sum()),
    dict(규칙='풋Δ20>0 + C3→i+2', n=len(p2), 총손익=p2.sum(), MDD=(dd2.cumsum().cummax() - dd2.cumsum()).max(),
         Δ=d2.sum(), ci_lo=lo2, ci_hi=hi2, 우세일=int((d2 > 0).sum()), 열세일=int((d2 < 0).sum()))]).round(2).to_string(index=False))
