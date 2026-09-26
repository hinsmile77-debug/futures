# -*- coding: utf-8 -*-
"""6차: §11 사용자 가설(외인 하방 & 개인콜 Δ20↑ → 휩소 후보 → 2봉 확인)을
     divpanel_full(85거래일)로 재검정. ws_analysis5.py 와 동일 규약·동일 통계량."""
import os
import numpy as np, pandas as pd

pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40)
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), 'GP_test')   # [MW0601 631차] pkl/npy 캐시 — 커밋 제외(GP_test/.gitignore)
os.makedirs(CACHE, exist_ok=True)
COST = 0.246018
rng = np.random.default_rng(5)


def spearman(a, b):
    """scipy 없는 환경용 — 순위 변환 후 피어슨(= 스피어만 ρ, 동점 평균순위)."""
    return pd.Series(a).rank().corr(pd.Series(b).rank())

S = pd.read_pickle(CACHE + '/signals.pkl').reset_index(drop=True)
D = pd.read_pickle(CACHE + '/panel.pkl'); DC = D.close.values
L = pd.read_pickle(CACHE + '/divpanel_full.pkl').sort_index()

# ── 0. 개인 콜/풋 누계 성질 ───────────────────────────────────
L['d'] = L.index.strftime('%Y-%m-%d'); L['hhmm'] = L.index.strftime('%H:%M')
L = L[(L.hhmm >= '09:00') & (L.hhmm <= '15:08')]
print('=== 개인 콜/풋 누계 성질 (로그 %d일 · %d봉) ===' % (L.d.nunique(), len(L)))
for k in ['rt_call', 'rt_put', 'fi_call', 'fi_put', 'fi_fut', 'rt_fut']:
    d20 = L.groupby('d')[k].diff(20); d1 = L.groupby('d')[k].diff(1)
    last = L.groupby('d')[k].last(); first = L.groupby('d')[k].first()
    print('  %-8s Δ20>0 비율 %.2f · Δ1>0 %.2f (Δ1=0 %.2f) · 일중 상승마감 %d/%d · |종가| 중앙 %.0f'
          % (k, (d20 > 0).mean(), (d1 > 0).mean(), (d1 == 0).mean(),
             int((last > first).sum()), len(last), np.median(np.abs(last))))

P = L.merge(D[['dt', 'close']], left_index=True, right_on='dt', how='inner').set_index('dt')
P['d'] = P.index.strftime('%Y-%m-%d')
for k in ['rt_call', 'rt_put', 'fi_fut', 'rt_fut']:
    P[k + '_d20'] = P.groupby('d')[k].diff(20)
P['fwd20'] = P.groupby('d')['close'].shift(-20) - P['close']
P['fwd90'] = P.groupby('d')['close'].shift(-90) - P['close']
P['ret20'] = P.groupby('d')['close'].diff(20)
print('\n=== 전 봉: Δ20 vs 최근20분(동행) / 이후20분 / 이후90분 (스피어만) ===')
for k in ['rt_call', 'rt_put', 'fi_fut', 'rt_fut']:
    q = P[[k + '_d20', 'fwd20', 'fwd90', 'ret20']].dropna()
    print('  %-8s n=%5d  ρ(동행)=%+.3f  ρ(fwd20)=%+.3f  ρ(fwd90)=%+.3f'
          % (k, len(q), spearman(q[k + '_d20'], q.ret20),
             spearman(q[k + '_d20'], q.fwd20),
             spearman(q[k + '_d20'], q.fwd90)))

# ── 1. 신호 단위 ──────────────────────────────────────────────
def lag(col, k):
    v = D[col].values; out = np.full(len(S), np.nan)
    ok = S.i.values - k >= 0; out[ok] = v[S.row.values[ok] - k]; return out


for k in ['rt_call', 'rt_put', 'fi_fut', 'rt_fut', 'foreign_futures', 'retail_futures']:
    S[k + '_d20'] = S[k].values - lag(k, 20)

sub = (S.rt_call_d20.notna() & S.fi_fut_d20.notna()).values
C3 = (S.cl2 > S.close).values
H_call = (S.rt_call_d20 > 0).values
H_fi = (S.fi_fut_d20 < 0).values
H_put = (S.rt_put_d20 > 0).values
WHIP = H_call & H_fi
print('\n=== 신호 단위 (n=%d · %d일) ===' % (sub.sum(), S.s[sub].nunique()))
print('  개인콜Δ20>0 %.2f · 외인Δ20<0 %.2f · 휩소후보 %.2f'
      % (H_call[sub].mean(), H_fi[sub].mean(), WHIP[sub].mean()))


def decompose(x, keep, days, nrep=2000):
    x = np.asarray(x, float); keep = np.asarray(keep, bool); days = np.asarray(days)
    ok = ~np.isnan(x); x, keep, days = x[ok], keep[ok], days[ok]
    if keep.sum() < 8 or (~keep).sum() < 8:
        return dict(n_keep=int(keep.sum()), n_excl=int((~keep).sum()))
    obs = x[keep].mean() - x[~keep].mean()
    groups = [np.where(days == d)[0] for d in np.unique(days)]
    sims = np.empty(nrep)
    for r in range(nrep):
        k2 = np.empty_like(keep)
        for ix in groups:
            k2[ix] = keep[ix][rng.permutation(len(ix))]
        sims[r] = x[k2].mean() - x[~k2].mean() if k2.sum() and (~k2).sum() else np.nan
    comp = np.nanmean(sims); within = obs - comp
    return dict(n_keep=int(keep.sum()), n_excl=int((~keep).sum()),
                keep=x[keep].mean(), excl=x[~keep].mean(), obs=obs, comp=comp, within=within,
                z=within / np.nanstd(sims), p_within=np.nanmean(np.abs(sims - comp) >= abs(within)),
                win_keep=(x[keep] > 0).mean(), win_excl=(x[~keep] > 0).mean())


rows = []
for name, keep, x in [
        ('통과=개인콜Δ20≤0 (r90 from i)', ~H_call, S.r90.values),
        ('통과=외인Δ20≥0',               ~H_fi,   S.r90.values),
        ('통과=개인풋Δ20≤0',             ~H_put,  S.r90.values),
        ('통과=~휩소후보(콜↑&외인↓)',     ~WHIP,   S.r90.values),
        ('통과=~휩소후보 (r90 from i+2)', ~WHIP,   S.c2_r90.values),
        ('휩소후보 중 C3 통과 vs 탈락 (i+2)', C3, np.where(WHIP,  S.c2_r90.values, np.nan)),
        ('비후보 중 C3 통과 vs 탈락 (i+2)',   C3, np.where(~WHIP, S.c2_r90.values, np.nan))]:
    r = decompose(x[sub], keep[sub], S.s.values[sub]); r['name'] = name; rows.append(r)
print(pd.DataFrame(rows)[['name', 'n_keep', 'n_excl', 'keep', 'excl', 'obs', 'comp', 'within', 'z',
                          'p_within', 'win_keep', 'win_excl']].round(3).to_string(index=False))

# 전·후반 분할 (동일 가설, 독립 반기)
half = S.s.values < '2026-07-15'
print('\n=== 휩소후보 내 C3 판별력 — 반기 분할 ===')
for nm, m in [('전반(~07-14)', half), ('후반(07-15~)', ~half)]:
    ss = sub & m
    r = decompose(np.where(WHIP, S.c2_r90.values, np.nan)[ss], C3[ss], S.s.values[ss])
    r['name'] = nm
    print(pd.DataFrame([r]).round(3).to_string(index=False))

q = S.index[(S.s == '2026-09-10') & (S.hhmm == '09:22')]
if len(q):
    q = q[0]
    print('\n  09:22: 개인콜Δ20=%+.0f 개인풋Δ20=%+.0f 외인Δ20=%+.0f → 휩소후보=%s'
          % (S.rt_call_d20.values[q], S.rt_put_d20.values[q], S.fi_fut_d20.values[q], bool(WHIP[q])))

# ── 2. 포지션 단위 ────────────────────────────────────────────
DAYS = sorted(S.s[sub].unique())


def bt_mixed(mode):
    """mode: 'base'|'d2'|'c3d2'|'block'|'user'"""
    T = S[sub]; pnl = []; days = []
    for s, g in T.groupby('s'):
        busy = -1
        for qq, row, i, i5, n in zip(g.index.values, g.row.values, g.i.values, g.i1505.values, g.n.values):
            if mode == 'base':   off = 0
            elif mode == 'd2':   off = 2
            elif mode == 'c3d2':
                if not C3[qq]: continue
                off = 2
            elif mode == 'block':
                if WHIP[qq]: continue
                off = 0
            elif mode == 'user':
                if WHIP[qq]:
                    if not C3[qq]: continue
                    off = 2
                else:
                    off = 0
            a = int(i) + off
            if a <= busy or a >= n: continue
            j = min(a + 90, int(i5))
            if j <= a: continue
            pnl.append(DC[int(row) + (j - int(i))] - DC[int(row) + off] - COST); days.append(s); busy = j
    p = pd.Series(pnl, index=days)
    dd = p.groupby(level=0).sum().reindex(DAYS).fillna(0)
    return p, dd


def boot_ci(d, nrep=3000):
    v = d.values; idx = rng.integers(0, len(v), (nrep, len(v)))
    s = v[idx].sum(axis=1)
    return np.percentile(s, [2.5, 97.5])


base_p, base_d = bt_mixed('base')
rows = []
for nm, mode in [('기준', 'base'), ('무조건 i+2', 'd2'), ('C3 → i+2', 'c3d2'),
                 ('휩소후보 차단', 'block'), ('사용자 규칙(후보→C3&i+2, 비후보→즉시)', 'user')]:
    p, dd = bt_mixed(mode)
    d = dd - base_d
    lo, hi = boot_ci(d) if mode != 'base' else (np.nan, np.nan)
    rows.append(dict(name=nm, n=len(p), total=p.sum(), per=p.mean(), win=(p > 0).mean(),
                     mdd=(dd.cumsum().cummax() - dd.cumsum()).max(),
                     delta=d.sum(), ci_lo=lo, ci_hi=hi,
                     better=int((d > 0).sum()), worse=int((d < 0).sum())))
print('\n=== 포지션 단위 (%d일 · 90분 · CYBOS 왕복 %.6f) ===' % (len(DAYS), COST))
print(pd.DataFrame(rows).round(2).to_string(index=False))

# ── 3. 대용: 개인선물 역지표 (raw_features, 2026-06-02~) ──────
sub2 = (S.retail_futures_d20.notna() & S.foreign_futures_d20.notna()).values
Wf = ((S.retail_futures_d20 > 0) & (S.foreign_futures_d20 < 0)).values
print('\n=== 대용: 개인선물Δ20>0 & 외인Δ20<0 (n=%d · %d일 · 후보비율 %.2f) ==='
      % (sub2.sum(), S.s[sub2].nunique(), Wf[sub2].mean()))
out = []
for name, keep, x in [('통과=~후보 (r90 from i)', ~Wf, S.r90.values),
                      ('통과=개인선물Δ20≤0', ~(S.retail_futures_d20 > 0).values, S.r90.values),
                      ('후보 중 C3 통과 vs 탈락 (i+2)', C3, np.where(Wf, S.c2_r90.values, np.nan))]:
    r = decompose(x[sub2], keep[sub2], S.s.values[sub2]); r['name'] = name; out.append(r)
print(pd.DataFrame(out)[['name', 'n_keep', 'n_excl', 'obs', 'comp', 'within', 'z', 'p_within']].round(3).to_string(index=False))
