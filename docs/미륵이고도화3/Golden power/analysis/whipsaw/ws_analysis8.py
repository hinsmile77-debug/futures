# -*- coding: utf-8 -*-
"""8차: 개인풋 Δ20 채널의 적대적 검증 — 가격의 거울인가, 독립 정보인가."""
import os
import numpy as np, pandas as pd
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40)
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), 'GP_test')   # [MW0601 631차] pkl/npy 캐시 — 커밋 제외(GP_test/.gitignore)
os.makedirs(CACHE, exist_ok=True)
rng = np.random.default_rng(8)
S = pd.read_pickle(CACHE + '/signals.pkl').reset_index(drop=True)
D = pd.read_pickle(CACHE + '/panel.pkl')


def lag(col, k):
    v = D[col].values; out = np.full(len(S), np.nan)
    ok = S.i.values - k >= 0; out[ok] = v[S.row.values[ok] - k]; return out


for k in ['rt_put', 'rt_call', 'fi_fut']:
    S[k + '_d20'] = S[k].values - lag(k, 20)
S['ret20'] = S.close.values - lag('close', 20)
sub = S.rt_put_d20.notna().values
PUT = (S.rt_put_d20 > 0).values


def decompose(x, keep, days, nrep=4000):
    x = np.asarray(x, float); keep = np.asarray(keep, bool); days = np.asarray(days)
    ok = ~np.isnan(x) & ~pd.isna(keep); x, keep, days = x[ok], keep[ok], days[ok]
    if keep.sum() < 10 or (~keep).sum() < 10:
        return dict(n_keep=int(keep.sum()), n_excl=int((~keep).sum()), within=np.nan, z=np.nan, p_within=np.nan)
    obs = x[keep].mean() - x[~keep].mean()
    groups = [np.where(days == d)[0] for d in np.unique(days)]
    sims = np.empty(nrep)
    for r in range(nrep):
        k2 = np.empty_like(keep)
        for ix in groups:
            k2[ix] = keep[ix][rng.permutation(len(ix))]
        sims[r] = x[k2].mean() - x[~k2].mean()
    comp = sims.mean(); within = obs - comp
    return dict(n_keep=int(keep.sum()), n_excl=int((~keep).sum()), obs=obs, comp=comp,
                within=within, z=within / sims.std(), p_within=np.mean(np.abs(sims - comp) >= abs(within)))


print('=== 1. 가격 momentum 층화 — 같은 ret20 부호 안에서도 살아있는가 ===')
rows = []
for nm, m in [('ret20 < 0 (반락 중)', sub & (S.ret20.values < 0)),
              ('ret20 ≥ 0 (상승 중)', sub & (S.ret20.values >= 0))]:
    r = decompose(S.r90.values[m], PUT[m], S.s.values[m]); r['층'] = nm; rows.append(r)
print(pd.DataFrame(rows)[['층', 'n_keep', 'n_excl', 'obs', 'comp', 'within', 'z', 'p_within']].round(3).to_string(index=False))

print('\n=== 2. 경쟁 필터 — 가격 대용이 같은 일을 하는가 ===')
rows = []
for nm, keep in [('개인풋 Δ20 > 0', PUT),
                 ('ret20 < 0 (가격 대용)', (S.ret20.values < 0)),
                 ('GS0 ≥ 1.0 (가격 대용)', (S.gs0.values >= 1.0)),
                 ('개인콜 Δ20 ≤ 0', ~(S.rt_call_d20 > 0).values),
                 ('외인 Δ20 ≥ 0', ~(S.fi_fut_d20 < 0).values)]:
    r = decompose(S.r90.values[sub], keep[sub], S.s.values[sub]); r['필터'] = nm; rows.append(r)
print(pd.DataFrame(rows)[['필터', 'n_keep', 'n_excl', 'obs', 'comp', 'within', 'z', 'p_within']].round(3).to_string(index=False))

print('\n=== 3. 이중 층화 — 개인풋 × 가격(ret20) 4분면 평균 r90 ===')
q = pd.DataFrame(dict(r90=S.r90.values[sub], put=PUT[sub], dn=(S.ret20.values < 0)[sub]))
print(q.pivot_table(index='put', columns='dn', values='r90', aggfunc=['mean', 'size']).round(2).to_string())

print('\n=== 4. 월별 안정성 (within) ===')
S['ym'] = pd.to_datetime(S.s).dt.to_period('M').astype(str)
rows = []
for ym, g in S[sub].groupby('ym'):
    m = sub & (S.ym.values == ym)
    r = decompose(S.r90.values[m], PUT[m], S.s.values[m], nrep=2000); r['월'] = ym; rows.append(r)
print(pd.DataFrame(rows)[['월', 'n_keep', 'n_excl', 'within', 'z', 'p_within']].round(3).to_string(index=False))

print('\n=== 5. 문턱 민감도 (개인풋 Δ20 분위 기준) ===')
v = S.rt_put_d20.values
rows = []
for p in [0.3, 0.4, 0.5, 0.6, 0.7]:
    thr = np.nanquantile(v[sub], p)
    keep = v > thr
    r = decompose(S.r90.values[sub], keep[sub], S.s.values[sub], nrep=2000)
    r['문턱'] = '%d%% (%+.0f)' % (p * 100, thr); rows.append(r)
print(pd.DataFrame(rows)[['문턱', 'n_keep', 'n_excl', 'within', 'z', 'p_within']].round(3).to_string(index=False))

print('\n=== 6. Δ20 창 길이 민감도 ===')
rows = []
for w in [5, 10, 20, 30, 60]:
    d = S.rt_put.values - lag('rt_put', w)
    keep = d > 0
    m = sub & ~np.isnan(d)
    r = decompose(S.r90.values[m], keep[m], S.s.values[m], nrep=2000)
    r['창'] = '%d봉' % w; rows.append(r)
print(pd.DataFrame(rows)[['창', 'n_keep', 'n_excl', 'within', 'z', 'p_within']].round(3).to_string(index=False))
