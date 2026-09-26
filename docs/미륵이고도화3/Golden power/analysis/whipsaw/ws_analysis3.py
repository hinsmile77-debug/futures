# -*- coding: utf-8 -*-
"""3차: 필터 효과 분해(일자 선택 vs 일자내 판별) + 일자 페어드 손익 검정."""
import sys, os
sys.path.insert(0, 'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path; ensure_conda_dll_path()
import numpy as np, pandas as pd
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 200)
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), 'GP_test')   # [MW0601 631차] pkl/npy 캐시 — 커밋 제외(GP_test/.gitignore)
os.makedirs(CACHE, exist_ok=True)
COST = 0.246018
rng = np.random.default_rng(11)
S = pd.read_pickle(CACHE + '/signals.pkl'); D = pd.read_pickle(CACHE + '/panel.pkl'); DC = D.close.values
case_ix = S.index[(S.s == '2026-09-10') & (S.hhmm == '09:22')][0]
def lead(col, k):
    v = D[col].values; out = np.full(len(S), np.nan)
    ok = S.i.values + k < S.n.values; out[ok] = v[S.row.values[ok] + k]; return out
S['lo1'] = lead('low', 1); S['lo2'] = lead('low', 2)
ALL = np.ones(len(S), bool)
C3 = (S.cl2 > S.close).values; C7 = ((S.cl2 > S.close) & (S.gb2 >= 0.5)).values
C11 = ((S.cl2 > S.close) & (S.lo1 >= S.low) & (S.lo2 >= S.low)).values
GSlo = (S.gs0 < 1.0).values; SG = (~(S.since_gb0 <= 3)).values; MAup = (~S.ma_down).values; EXT = (S.ext_hi60 < 1.5).values
RSI40 = (S.rsi >= 40).values; PAT = ((S.gs0 >= 1.0) & (S.since_gb0 <= 3)).values

# ── 1. 분해: obs = 일자구성(comp) + 일자내(within) ───────────
def decompose(x, keep, days, nrep=1500):
    x = np.asarray(x, float); keep = np.asarray(keep, bool); days = np.asarray(days)
    ok = ~np.isnan(x); x, keep, days = x[ok], keep[ok], days[ok]
    if keep.sum() < 10 or (~keep).sum() < 10: return dict(n_keep=int(keep.sum()), n_excl=int((~keep).sum()))
    obs = x[keep].mean() - x[~keep].mean()
    groups = [np.where(days == d)[0] for d in np.unique(days)]
    sims = np.empty(nrep)
    for r in range(nrep):
        k2 = np.empty_like(keep)
        for ix in groups: k2[ix] = keep[ix][rng.permutation(len(ix))]
        sims[r] = x[k2].mean() - x[~k2].mean() if k2.sum() and (~k2).sum() else np.nan
    comp = np.nanmean(sims); sd = np.nanstd(sims); within = obs - comp
    p_within = np.nanmean(np.abs(sims - comp) >= abs(within))
    # 일자 무시 전체 셔플 → 총효과 p
    sims2 = np.array([x[kk].mean() - x[~kk].mean() for kk in (rng.permutation(keep) for _ in range(nrep))])
    p_total = np.mean(np.abs(sims2) >= abs(obs))
    return dict(n_keep=int(keep.sum()), n_excl=int((~keep).sum()), keep=x[keep].mean(), excl=x[~keep].mean(), obs=obs, p_total=p_total, comp=comp, within=within, z_within=within / sd if sd > 0 else np.nan, p_within=p_within)

def decomp_table(items, x, sub=None, title=''):
    rows = []
    for name, k in items:
        mm = ALL if sub is None else sub
        r = decompose(x[mm], k[mm], S.s.values[mm]); r['name'] = name
        r1 = decompose(x[mm & (S.half.values == 1)], k[mm & (S.half.values == 1)], S.s.values[mm & (S.half.values == 1)], nrep=600)
        r2 = decompose(x[mm & (S.half.values == 2)], k[mm & (S.half.values == 2)], S.s.values[mm & (S.half.values == 2)], nrep=600)
        r['within_h1'] = r1.get('within', np.nan); r['within_h2'] = r2.get('within', np.nan); r['comp_h1'] = r1.get('comp', np.nan); r['comp_h2'] = r2.get('comp', np.nan)
        r['blk0922'] = not bool(k[S.index.get_loc(case_ix)]); rows.append(r)
    print('\n=== %s ===' % title)
    print('  obs = keep−excl 평균차(pt) · comp = 일자구성 효과(일자내 셔플 중심) · within = obs−comp (같은 날 안에서의 판별력)')
    print(pd.DataFrame(rows)[['name','n_keep','n_excl','keep','excl','obs','p_total','comp','within','z_within','p_within','within_h1','within_h2','comp_h1','comp_h2','blk0922']].round(3).to_string(index=False))

decomp_table([('GS0<1.0', GSlo), ('since_gb0>3', SG), ('MA20>=MA60', MAup), ('ext_hi60<1.5', EXT), ('RSI>=40', RSI40), ('~09:22패턴', ~PAT),
              ('C3 cl2>cl0 (r90 from i)', C3), ('C11', C11)], S.r90.values, title='사전 구조 필터 — r90(진입 i) 분해')
decomp_table([('C3 cl2>cl0', C3), ('C7', C7), ('C11', C11), ('GS0<1.0&C3', GSlo & C3), ('MAup&C3', MAup & C3), ('GS0<1.0&MAup&C3', GSlo & MAup & C3), ('EXT&C3', EXT & C3)],
             S.c2_r90.values, title='사후 확인 — r90(진입 i+2) 분해')
inv_sub = (S.foreign_futures.notna() & S.fi_d10.notna()).values
decomp_table([('외인선물 d10>=0', (S.fi_d10 >= 0).values), ('외인선물 d5>=0', (S.fi_d5 >= 0).values), ('개인선물 d10<=0', (S.rt_d10 <= 0).values), ('기관선물 d10>=0', (S.inst_d10 >= 0).values),
              ('외인콜 d10>=0', (S.fic_d10 >= 0).values), ('외인풋 d10<=0', (S.fip_d10 <= 0).values), ('비차익 d10>=0', (S.nonarb_d10 >= 0).values),
              ('외인 post2>=0', (S.fi_post2 >= 0).values)], S.r90.values, sub=inv_sub, title='수급 필터(2026-06-02~) — r90 분해')
log_sub = (S.rt_call.notna() & S.rt_call_d10.notna()).values
decomp_table([('개인콜 d10>=0', (S.rt_call_d10 >= 0).values), ('개인풋 d10<=0', (S.rt_put_d10 <= 0).values), ('외인선물(log) d10>=0', (S.fi_fut_d10 >= 0).values)], S.r90.values, sub=log_sub, title='개인 콜/풋(로그 2026-08-10~) — r90 분해')
str_sub = ((S.s >= '2026-06-08') & S.str5.notna()).values
decomp_table([('체결강도 MA5>MA20', S.str5_gt20.values.astype(bool)), ('체결강도 MA5 slope3>0', (S.str5_slope3 > 0).values)], S.r90.values, sub=str_sub, title='체결강도(2026-06-08~) — r90 분해')

# ── 2. 일자 페어드 손익: 필터 적용 vs 기준 ─────────────────
def daily_pnl(keep_mask, entry_off=0, hold=90, cost=COST):
    T = S[keep_mask]; out = pd.Series(0.0, index=sorted(S.s.unique())); cnt = pd.Series(0, index=out.index)
    for s, g in T.groupby('s'):
        busy = -1; tot = 0.0; n = 0
        for row, i, i5, nn in zip(g.row.values, g.i.values, g.i1505.values, g.n.values):
            a = int(i) + entry_off
            if a <= busy: continue
            j = min(a + hold, int(i5))
            if j <= a or a >= nn: continue
            tot += DC[int(row) + (j - int(i))] - DC[int(row) + entry_off] - cost; n += 1; busy = j
        out.loc[s] = tot; cnt.loc[s] = n
    return out, cnt
base, cbase = daily_pnl(ALL)
rows = []
for name, k, off in [('무조건 i+2', ALL, 2), ('C3 → i+2', C3, 2), ('C7 → i+2', C7, 2), ('C11 → i+2', C11, 2), ('GS0<1.0', GSlo, 0), ('GS0<1.0 & C3 → i+2', GSlo & C3, 2),
                     ('MAup & C3 → i+2', MAup & C3, 2), ('EXT & C3 → i+2', EXT & C3, 2), ('GS0<1.0&MAup&C3 → i+2', GSlo & MAup & C3, 2), ('~09:22패턴', ~PAT, 0)]:
    f, cf = daily_pnl(k, off); d = f - base
    boots = np.array([d.values[rng.integers(0, len(d), len(d))].sum() for _ in range(3000)])
    nz = d[d != 0]
    from math import comb
    pos = int((nz > 0).sum()); n = len(nz); p_sign = min(1.0, 2 * sum(comb(n, x) for x in range(min(pos, n - pos) + 1)) / 2 ** n) if n else np.nan
    h1 = (d.index < sorted(S.s.unique())[len(S.s.unique()) // 2])
    rows.append(dict(name=name, base_total=base.sum(), filt_total=f.sum(), delta=d.sum(), ci_lo=np.quantile(boots, .025), ci_hi=np.quantile(boots, .975),
                     t_paired=d.mean() / d.std(ddof=1) * np.sqrt(len(d)), days_better=pos, days_worse=n - pos, p_sign=p_sign, delta_h1=d[h1].sum(), delta_h2=d[~h1].sum(),
                     pos_base=int(cbase.sum()), pos_filt=int(cf.sum())))
print('\n=== 일자 페어드 손익 (필터 − 기준, 90분 보유, 251일) · 일자 부트스트랩 95% CI · 부호검정 ===')
print(pd.DataFrame(rows).round(2).to_string(index=False))

# ── 3. 「09:22 패턴」 빈도는 일 단위 신호인가 ─────────────
print('\n=== 일자 단위: 09:22 패턴 비중 vs 그날 기준 손익 ===')
share = pd.Series({s: PAT[(S.s.values == s)].mean() for s in S.s.unique()}).reindex(base.index)
df = pd.DataFrame(dict(share=share, pnl=base, n=cbase))
for lo, hi in [(0, 0.0001), (0.0001, 0.2), (0.2, 0.4), (0.4, 1.01)]:
    q = df[(df.share >= lo) & (df.share < hi)]
    print('  패턴비중 [%.1f,%.1f): 일수 %3d  일평균 기준손익 %+.2f  양일비율 %.2f' % (lo, hi, len(q), q.pnl.mean(), (q.pnl > 0).mean()))
print('  spearman(share, pnl) = %.3f' % df[['share', 'pnl']].corr(method='spearman').iloc[0, 1])
# 그날 첫 패턴 신호 이후 신호의 평균 r90 vs 그 전
first_pat = {s: (S.i.values[(S.s.values == s) & PAT].min() if ((S.s.values == s) & PAT).any() else 10**9) for s in S.s.unique()}
after = np.array([(S.i.values[q] >= first_pat.get(S.s.values[q], 1e9)) for q in range(len(S))])
x = S.r90.values; ok = ~np.isnan(x)
print('  패턴 첫 발생 이후 신호 r90 = %.3f (n=%d) vs 발생 전/무발생일 r90 = %.3f (n=%d)' % (x[ok & after].mean(), (ok & after).sum(), x[ok & ~after].mean(), (ok & ~after).sum()))
d_ = decompose(x, ~after, S.s.values); print('  분해: obs=%.3f comp=%.3f within=%.3f p_within=%.3f' % (d_['obs'], d_['comp'], d_['within'], d_['p_within']))
