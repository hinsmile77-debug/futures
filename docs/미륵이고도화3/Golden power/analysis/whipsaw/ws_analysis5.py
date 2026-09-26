# -*- coding: utf-8 -*-
"""5차: 사용자 가설 — 외인 하방 & 개인콜 20봉 추세상승(역지표) → 휩소 후보 → 2봉 확인 후 진입."""
import sys, os
sys.path.insert(0, 'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path; ensure_conda_dll_path()
import numpy as np, pandas as pd
from math import comb
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40)
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), 'GP_test')   # [MW0601 631차] pkl/npy 캐시 — 커밋 제외(GP_test/.gitignore)
os.makedirs(CACHE, exist_ok=True)
COST = 0.246018; rng = np.random.default_rng(5)
S = pd.read_pickle(CACHE + '/signals.pkl').reset_index(drop=True); D = pd.read_pickle(CACHE + '/panel.pkl'); DC = D.close.values
L = pd.read_pickle(CACHE + '/divpanel.pkl')

# ── 0. 개인 콜/풋 누계의 성질: 하루 중 단조 증가인가 ─────────
L = L.sort_index(); L['d'] = L.index.strftime('%Y-%m-%d'); L['hhmm'] = L.index.strftime('%H:%M')
L = L[(L.hhmm >= '09:00') & (L.hhmm <= '15:08')]
print('=== 개인 콜/풋 누계 성질 (로그 23일, 분단위) ===')
for k in ['rt_call', 'rt_put', 'fi_call', 'fi_put', 'fi_fut', 'rt_fut']:
    d20 = L.groupby('d')[k].diff(20); d1 = L.groupby('d')[k].diff(1)
    last = L.groupby('d')[k].last(); first = L.groupby('d')[k].first()
    print('  %-8s Δ20>0 비율 %.2f · Δ1>0 비율 %.2f (Δ1=0 %.2f) · 일중 상승마감일 %d/%d · |종가| 중앙 %.0f · 일중 Δ1 표준편차 중앙 %.0f'
          % (k, (d20 > 0).mean(), (d1 > 0).mean(), (d1 == 0).mean(), int((last > first).sum()), len(last), np.median(np.abs(last)), np.median(L.groupby('d')[k].apply(lambda x: x.diff().std()))))
# 개인콜 Δ20 부호와 이후 20분 선물 수익률 상관 (전 봉, 일자내)
P = L.merge(D[['dt', 'close']], left_index=True, right_on='dt', how='inner').set_index('dt')
P['d'] = P.index.strftime('%Y-%m-%d')
for k in ['rt_call', 'rt_put', 'fi_fut', 'rt_fut']:
    P[k + '_d20'] = P.groupby('d')[k].diff(20)
P['fwd20'] = P.groupby('d')['close'].shift(-20) - P['close']; P['fwd90'] = P.groupby('d')['close'].shift(-90) - P['close']
P['ret20'] = P.groupby('d')['close'].diff(20)
print('\n=== 전 봉 기준: Δ20 부호 vs 이후 20/90분 수익 (스피어만, 일자내 정보) ===')
for k in ['rt_call', 'rt_put', 'fi_fut', 'rt_fut']:
    q = P[[k + '_d20', 'fwd20', 'fwd90', 'ret20']].dropna()
    print('  %-8s n=%d  ρ(Δ20, fwd20)=%+.3f  ρ(Δ20, fwd90)=%+.3f  ρ(Δ20, ret20 동행)=%+.3f' % (k, len(q), q[k + '_d20'].corr(q.fwd20, method='spearman'), q[k + '_d20'].corr(q.fwd90, method='spearman'), q[k + '_d20'].corr(q.ret20, method='spearman')))

# ── 1. 신호 단위: 사용자 규칙 ───────────────────────────────
def lag(col, k):
    v = D[col].values; out = np.full(len(S), np.nan)
    ok = S.i.values - k >= 0; out[ok] = v[S.row.values[ok] - k]; return out
for k in ['rt_call', 'rt_put', 'fi_fut', 'rt_fut', 'foreign_futures', 'retail_futures']:
    S[k + '_d20'] = S[k].values - lag(k, 20)
sub = (S.rt_call_d20.notna() & S.fi_fut_d20.notna()).values
C3 = (S.cl2 > S.close).values
H_call = (S.rt_call_d20 > 0).values            # 개인콜 20봉 추세 상승 → 역지표 하락 암시
H_fi = (S.fi_fut_d20 < 0).values               # 외인 하방
H_put = (S.rt_put_d20 > 0).values              # 개인풋 상승(시세 동행이면 하락)
WHIP = H_call & H_fi                           # 사용자 정의 휩소 후보
print('\n=== 신호 단위 (로그 23일 · n=%d) ===' % sub.sum())
print('  개인콜Δ20>0 비율 %.2f · 외인Δ20<0 비율 %.2f · 휩소후보(둘 다) 비율 %.2f' % (H_call[sub].mean(), H_fi[sub].mean(), WHIP[sub].mean()))

def decompose(x, keep, days, nrep=2000):
    x = np.asarray(x, float); keep = np.asarray(keep, bool); days = np.asarray(days); ok = ~np.isnan(x); x, keep, days = x[ok], keep[ok], days[ok]
    if keep.sum() < 8 or (~keep).sum() < 8: return dict(n_keep=int(keep.sum()), n_excl=int((~keep).sum()))
    obs = x[keep].mean() - x[~keep].mean(); groups = [np.where(days == d)[0] for d in np.unique(days)]; sims = np.empty(nrep)
    for r in range(nrep):
        k2 = np.empty_like(keep)
        for ix in groups: k2[ix] = keep[ix][rng.permutation(len(ix))]
        sims[r] = x[k2].mean() - x[~k2].mean() if k2.sum() and (~k2).sum() else np.nan
    comp = np.nanmean(sims); within = obs - comp
    return dict(n_keep=int(keep.sum()), n_excl=int((~keep).sum()), keep=x[keep].mean(), excl=x[~keep].mean(), obs=obs, comp=comp, within=within, z=within / np.nanstd(sims), p_within=np.nanmean(np.abs(sims - comp) >= abs(within)), win_keep=(x[keep] > 0).mean(), win_excl=(x[~keep] > 0).mean())
rows = []
for name, keep, x in [('통과=개인콜Δ20≤0 (r90 from i)', ~H_call, S.r90.values), ('통과=외인Δ20≥0', ~H_fi, S.r90.values), ('통과=개인풋Δ20≤0', ~H_put, S.r90.values),
                      ('통과=~휩소후보(콜↑&외인↓)', ~WHIP, S.r90.values), ('통과=~휩소후보 (r90 from i+2)', ~WHIP, S.c2_r90.values),
                      ('휩소후보 중 C3 통과 vs 탈락 (i+2)', C3, np.where(WHIP, S.c2_r90.values, np.nan)),
                      ('비후보 중 C3 통과 vs 탈락 (i+2)', C3, np.where(~WHIP, S.c2_r90.values, np.nan))]:
    r = decompose(x[sub], keep[sub], S.s.values[sub]); r['name'] = name; rows.append(r)
print(pd.DataFrame(rows).round(3).to_string(index=False))

# 09:22 값
q = S.index.get_loc(S.index[(S.s == '2026-09-10') & (S.hhmm == '09:22')][0])
print('\n  09:22: 개인콜Δ20=%+.0f 개인풋Δ20=%+.0f 외인Δ20=%+.0f 개인선물Δ20=%+.0f → 휩소후보=%s' % (S.rt_call_d20.values[q], S.rt_put_d20.values[q], S.fi_fut_d20.values[q], S.rt_fut_d20.values[q], bool(WHIP[q])))

# ── 2. 포지션 단위 (23일) ──────────────────────────────────
def bt(keep, off=0, hold=90):
    T = S[keep & sub]; pnl = []; days = []
    for s, g in T.groupby('s'):
        busy = -1
        for row, i, i5, n in zip(g.row.values, g.i.values, g.i1505.values, g.n.values):
            a = int(i) + off
            if a <= busy: continue
            j = min(a + hold, int(i5))
            if j <= a or a >= n: continue
            pnl.append(DC[int(row) + (j - int(i))] - DC[int(row) + off] - COST); days.append(s); busy = j
    p = pd.Series(pnl, index=days); dd = p.groupby(level=0).sum().reindex(sorted(S.s[sub].unique())).fillna(0)
    return dict(n=len(p), total=p.sum(), per=p.mean() if len(p) else np.nan, win=(p > 0).mean() if len(p) else np.nan, mdd=(dd.cumsum().cummax() - dd.cumsum()).max(), days_pos=int((dd > 0).sum()), days_neg=int((dd < 0).sum())), dd
rows = []; base, dbase = bt(np.ones(len(S), bool))
ALL = np.ones(len(S), bool)
for name, keep, off in [('기준(23일)', ALL, 0), ('무조건 i+2', ALL, 2), ('C3 → i+2', C3, 2),
                        ('휩소후보 차단', ~WHIP, 0), ('개인콜Δ20>0 차단', ~H_call, 0), ('외인Δ20<0 차단', ~H_fi, 0),
                        ('사용자 규칙: 후보면 C3→i+2, 아니면 즉시', (~WHIP) | C3, 0),   # off 처리 아래 별도
                        ('후보→C3&i+2 / 비후보→즉시 (정확)', ALL, -1)]:
    if off == -1:
        # 혼합: 후보는 i+2 진입(C3 통과 시), 비후보는 즉시
        T = S[sub]; pnl = []; days = []
        for s, g in T.groupby('s'):
            busy = -1
            for qq, row, i, i5, n in zip(g.index.values, g.row.values, g.i.values, g.i1505.values, g.n.values):
                if WHIP[qq]:
                    if not C3[qq]: continue
                    o = 2
                else: o = 0
                a = int(i) + o
                if a <= busy: continue
                j = min(a + hold if False else a + 90, int(i5))
                if j <= a or a >= n: continue
                pnl.append(DC[int(row) + (j - int(i))] - DC[int(row) + o] - COST); days.append(s); busy = j
        p = pd.Series(pnl, index=days); dd = p.groupby(level=0).sum().reindex(sorted(S.s[sub].unique())).fillna(0)
        r = dict(n=len(p), total=p.sum(), per=p.mean(), win=(p > 0).mean(), mdd=(dd.cumsum().cummax() - dd.cumsum()).max(), days_pos=int((dd > 0).sum()), days_neg=int((dd < 0).sum()))
    else:
        r, dd = bt(keep, off)
    d = (dd - dbase); r['delta'] = d.sum(); r['d_better'] = int((d > 0).sum()); r['d_worse'] = int((d < 0).sum()); r['name'] = name; rows.append(r)
print('\n=== 포지션 단위 (로그 23일 · 90분 · CYBOS) ===')
print(pd.DataFrame(rows)[['name', 'n', 'total', 'per', 'win', 'mdd', 'days_pos', 'days_neg', 'delta', 'd_better', 'd_worse']].round(2).to_string(index=False))

# ── 3. 개인선물(06-02~, 780신호)로 같은 역지표 논리 ───────────
sub2 = (S.retail_futures_d20.notna() & S.foreign_futures_d20.notna()).values
Wf = ((S.retail_futures_d20 > 0) & (S.foreign_futures_d20 < 0)).values
print('\n=== 대용: 개인선물Δ20>0 & 외인Δ20<0 (2026-06-02~ n=%d, 후보비율 %.2f) ===' % (sub2.sum(), Wf[sub2].mean()))
for name, keep, x in [('통과=~후보 (r90 from i)', ~Wf, S.r90.values), ('통과=개인선물Δ20≤0', ~(S.retail_futures_d20 > 0).values, S.r90.values), ('후보 중 C3 통과 vs 탈락 (i+2)', C3, np.where(Wf, S.c2_r90.values, np.nan))]:
    r = decompose(x[sub2], keep[sub2], S.s.values[sub2]); r['name'] = name; print(pd.DataFrame([r]).round(3).to_string(index=False, header=(name.startswith('통과=~'))))
