# -*- coding: utf-8 -*-
"""2차: 순열검정 검증 + 확인봉 변형 + 결합 필터 + 09:22 패턴 발생률 + 개장창."""
import sys, os
sys.path.insert(0, 'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path; ensure_conda_dll_path()
import numpy as np, pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 200)
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), 'GP_test')   # [MW0601 631차] pkl/npy 캐시 — 커밋 제외(GP_test/.gitignore)
os.makedirs(CACHE, exist_ok=True)
COST = 0.246018
rng = np.random.default_rng(7)
S = pd.read_pickle(CACHE + '/signals.pkl'); D = pd.read_pickle(CACHE + '/panel.pkl')
DC = D.close.values; DL = D.low.values
case_ix = S.index[(S.s == '2026-09-10') & (S.hhmm == '09:22')][0]

# ── 순열검정 검증 ─────────────────────────────────────────
def perm_p(x, keep, days, nrep=2000, debug=False):
    x = np.asarray(x, float); keep = np.asarray(keep, bool); days = np.asarray(days)
    obs = x[keep].mean() - x[~keep].mean()
    groups = [np.where(days == d)[0] for d in np.unique(days)]
    sims = np.empty(nrep)
    for r in range(nrep):
        k2 = np.empty_like(keep)
        for ix in groups: k2[ix] = keep[ix][rng.permutation(len(ix))]
        a, b = k2.sum(), (~k2).sum()
        sims[r] = x[k2].mean() - x[~k2].mean() if a and b else np.nan
    p = np.nanmean(np.abs(sims) >= abs(obs))
    if debug: print('   [perm dbg] obs=%.3f sims mean=%.3f sd=%.3f q05=%.3f q95=%.3f p=%.3f' % (obs, np.nanmean(sims), np.nanstd(sims), np.nanquantile(sims, .05), np.nanquantile(sims, .95), p))
    return obs, p

m = ~np.isnan(S.r90.values)
print('=== 순열검정 디버그 (GS0<1.0) ===')
perm_p(S.r90.values[m], (S.gs0 < 1.0).values[m], S.s.values[m], debug=True)
perm_p(S.r90.values[m], (S.gs0 < 1.0).values[m], S.s.values[m], debug=True)
print('   전체 셔플(일자 무시):')
x = S.r90.values[m]; k = (S.gs0 < 1.0).values[m]
sims = np.array([x[kk].mean() - x[~kk].mean() for kk in (rng.permutation(k) for _ in range(2000))])
print('   sims sd=%.3f p=%.3f' % (sims.std(), np.mean(np.abs(sims) >= abs(x[k].mean() - x[~k].mean()))))

def lead(col, k):
    v = D[col].values; out = np.full(len(S), np.nan)
    ok = S.i.values + k < S.n.values; out[ok] = v[S.row.values[ok] + k]; return out
S['cl3'] = lead('close', 3); S['lo1'] = lead('low', 1); S['lo2'] = lead('low', 2)
def ret_from(k, h):
    out = np.full(len(S), np.nan)
    for q, (r, i, n, i5) in enumerate(zip(S.row.values, S.i.values, S.n.values, S.i1505.values)):
        a = i + k; j = min(a + h, i5)
        if j > a and a < n: out[q] = DC[r + (j - i)] - DC[r + k]
    return out
S['c1_r90'] = ret_from(1, 90); S['c3_r90'] = ret_from(3, 90); S['c2_r90'] = ret_from(2, 90)

def backtest(keep_mask, entry_off=0, hold=90, cost=COST, sub=None):
    T = S[keep_mask & (sub if sub is not None else np.ones(len(S), bool))]; pnl = []; days = []
    for s, g in T.groupby('s'):
        busy = -1
        for row, i, i5, n in zip(g.row.values, g.i.values, g.i1505.values, g.n.values):
            a = int(i) + entry_off
            if a <= busy: continue
            j = min(a + hold, int(i5))
            if j <= a or a >= n: continue
            pnl.append(DC[int(row) + (j - int(i))] - DC[int(row) + entry_off] - cost); days.append(s); busy = j
    p = pd.Series(pnl, index=days); dd = p.groupby(level=0).sum()
    allday = pd.Series(0.0, index=sorted(S.s.unique())); allday.loc[dd.index] = dd.values
    cum = allday.cumsum(); mdd = (cum.cummax() - cum).max()
    t = allday.mean() / allday.std(ddof=1) * np.sqrt(len(allday)) if allday.std(ddof=1) > 0 else np.nan
    best3 = allday.nlargest(3).sum()
    return dict(n=len(p), total=p.sum(), per=p.mean() if len(p) else np.nan, win=(p > 0).mean() if len(p) else np.nan, t_day=t, mdd=mdd, ex_best3=p.sum() - best3, days_pos=int((allday > 0).sum()), days_neg=int((allday < 0).sum()))

def bt_table(items, hold=90, title=''):
    rows = []
    for name, k, off in items:
        r = backtest(k, off, hold); r['name'] = name
        r['tot_h1'] = backtest(k & (S.half.values == 1), off, hold)['total']; r['tot_h2'] = backtest(k & (S.half.values == 2), off, hold)['total']
        r['blk0922'] = not bool(k[S.index.get_loc(case_ix)])
        rows.append(r)
    print('\n=== %s (보유 %d분, CYBOS 비용) ===' % (title, hold))
    print(pd.DataFrame(rows)[['name','n','total','per','win','t_day','mdd','ex_best3','days_pos','days_neg','tot_h1','tot_h2','blk0922']].round(2).to_string(index=False))

ALL = np.ones(len(S), bool)
C3 = (S.cl2 > S.close).values; C7 = ((S.cl2 > S.close) & (S.gb2 >= 0.5)).values
C8 = (S.cl1 > S.close).values; C9 = (S.cl3 > S.close).values
C10 = ((S.cl1 >= S.close) & (S.cl2 >= S.close)).values
C11 = ((S.cl2 > S.close) & (S.lo1 >= S.low) & (S.lo2 >= S.low)).values   # 신호봉 저가 미이탈 + 종가 상승
GSlo = (S.gs0 < 1.0).values; SG = (~(S.since_gb0 <= 3)).values; MAup = (~S.ma_down).values; EXT = (S.ext_hi60 < 1.5).values

bt_table([
    ('기준', ALL, 0), ('무조건 i+1', ALL, 1), ('무조건 i+2', ALL, 2), ('무조건 i+3', ALL, 3),
    ('C8 cl1>cl0 → i+1', C8, 1), ('C3 cl2>cl0 → i+2', C3, 2), ('C9 cl3>cl0 → i+3', C9, 3),
    ('C10 cl1,cl2>=cl0 → i+2', C10, 2), ('C11 저가미이탈&cl2>cl0 → i+2', C11, 2), ('C7 cl2>cl0&GB2>=0.5 → i+2', C7, 2),
    ('GS0<1.0 (사전)', GSlo, 0), ('GS0<1.0 & C3 → i+2', GSlo & C3, 2), ('since_gb0>3 & C3 → i+2', SG & C3, 2),
    ('ext<1.5 & C3 → i+2', EXT & C3, 2), ('MA20>=MA60 & C3 → i+2', MAup & C3, 2), ('GS0<1.0 & MAup & C3 → i+2', GSlo & MAup & C3, 2),
], title='확인봉 변형 + 결합 (포지션 단위 비중복)')
bt_table([('기준', ALL, 0), ('무조건 i+2', ALL, 2), ('C3 → i+2', C3, 2), ('C11 → i+2', C11, 2), ('GS0<1.0 & C3 → i+2', GSlo & C3, 2)], hold=30, title='같은 필터 30분 보유')
bt_table([('기준', ALL, 0), ('무조건 i+2', ALL, 2), ('C3 → i+2', C3, 2), ('C11 → i+2', C11, 2), ('GS0<1.0 & C3 → i+2', GSlo & C3, 2)], hold=60, title='같은 필터 60분 보유')

# ── 신호 단위: 확인 통과 vs 탈락 (같은 진입시점 i+2 기준) 순열 p ───
print('\n=== 신호 단위 — 확인 통과/탈락 r90(진입 i+2) 차이 · 일자내 순열 p ===')
m2 = ~np.isnan(S.c2_r90.values)
rows = []
for name, k in [('C3', C3), ('C7', C7), ('C10', C10), ('C11', C11), ('GS0<1.0', GSlo), ('GS0<1.0&C3', GSlo & C3), ('since_gb0>3', SG), ('ext<1.5', EXT), ('MAup', MAup)]:
    d, p = perm_p(S.c2_r90.values[m2], k[m2], S.s.values[m2])
    h1 = (S.half.values == 1)[m2]; h2 = ~h1; xx = S.c2_r90.values[m2]; kk = k[m2]
    d1, p1 = perm_p(xx[h1], kk[h1], S.s.values[m2][h1], nrep=1000); d2, p2 = perm_p(xx[h2], kk[h2], S.s.values[m2][h2], nrep=1000)
    rows.append(dict(name=name, n_keep=int(kk.sum()), n_excl=int((~kk).sum()), keep=xx[kk].mean(), excl=xx[~kk].mean(), d=d, p=p, d_h1=d1, p_h1=p1, d_h2=d2, p_h2=p2, win_keep=(xx[kk] > 0).mean(), win_excl=(xx[~kk] > 0).mean()))
print(pd.DataFrame(rows).round(3).to_string(index=False))

# ── 09:22 패턴(하락 중 신저 반등)의 발생률과 결과 ────────────
print('\n=== 「09:22 패턴」 = GS0>=1.0 & since_gb0<=3 (20봉 고점에서 ≥0.5% 아래 + 신저 3봉 내 반등) ===')
P = ((S.gs0 >= 1.0) & (S.since_gb0 <= 3)).values
for lab, mk in [('전체', ALL), ('H1', S.half.values == 1), ('H2', S.half.values == 2)]:
    mm = mk & m
    a = S.r90.values[mm & P]; b = S.r90.values[mm & ~P]
    print('  %s: 패턴 n=%d (%.1f%%)  r90 패턴=%.3f 비패턴=%.3f  승률 %.3f vs %.3f  stopfirst %.3f vs %.3f  C3통과율(패턴) %.3f' % (
        lab, len(a), 100 * len(a) / mm.sum(), a.mean(), b.mean(), (a > 0).mean(), (b > 0).mean(), S.stopfirst.values[mm & P].mean(), S.stopfirst.values[mm & ~P].mean(), C3[mm & P].mean()))

# ── 개장창(09:20~10:00) 한정 ─────────────────────────────
W = ((S.hhmm >= '09:20') & (S.hhmm <= '10:00')).values
print('\n=== 개장창 09:20~10:00 한정 (딥다이브 §4-1 의 엣지 창) ===')
rows = []
for name, k, off in [('기준', ALL, 0), ('무조건 i+2', ALL, 2), ('C3 → i+2', C3, 2), ('C11 → i+2', C11, 2), ('GS0<1.0', GSlo, 0), ('GS0<1.0 & C3 → i+2', GSlo & C3, 2)]:
    for hold in (10, 30, 90):
        r = backtest(k, off, hold, sub=W); r['name'] = name; r['hold'] = hold
        r['tot_h1'] = backtest(k & (S.half.values == 1), off, hold, sub=W)['total']; r['tot_h2'] = backtest(k & (S.half.values == 2), off, hold, sub=W)['total']
        rows.append(r)
print(pd.DataFrame(rows)[['name','hold','n','total','per','win','t_day','mdd','ex_best3','tot_h1','tot_h2']].round(2).to_string(index=False))

# ── 확인봉 통과율 · 09:22 값 ─────────────────────────────
print('\n=== 확인 조건별 통과율 · 2026-09-10 09:22 ===')
for name, k in [('C3 cl2>cl0', C3), ('C8 cl1>cl0', C8), ('C9 cl3>cl0', C9), ('C10', C10), ('C11', C11), ('C7', C7)]:
    print('  %-14s 통과율 %.3f   09:22 통과=%s' % (name, k.mean(), bool(k[S.index.get_loc(case_ix)])))
r = S.loc[case_ix]
print('  09:22: close=%.2f cl1=%.2f cl2=%.2f cl3=%.2f low=%.2f lo1=%.2f lo2=%.2f gb=%.3f gb1=%.3f gb2=%.3f' % (r.close, r.cl1, r.cl2, r.cl3, r.low, r.lo1, r.lo2, r.gb, r.gb1, r.gb2))
# 09-10 하루 전체 신호별 C3 판정과 r90
print('\n=== 2026-09-10 신호 전수 ===')
T = S[S.s == '2026-09-10'][['hhmm','close','gb','gs0','since_gb0','ma_down','rsi','cl1','cl2','r10','r30','r90','stopfirst']].copy(); T['C3'] = C3[S.s.values == '2026-09-10']
print(T.round(3).to_string(index=False))
