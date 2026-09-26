# -*- coding: utf-8 -*-
"""4차: 일자 상태(day-state) 규칙 — 당일 선행 정보만으로 만든 인과적 차단 규칙 + 일자내 페어드 검정."""
import sys, os
sys.path.insert(0, 'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path; ensure_conda_dll_path()
import numpy as np, pandas as pd
from math import comb
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 200)
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), 'GP_test')   # [MW0601 631차] pkl/npy 캐시 — 커밋 제외(GP_test/.gitignore)
os.makedirs(CACHE, exist_ok=True)
COST = 0.246018
rng = np.random.default_rng(21)
S = pd.read_pickle(CACHE + '/signals.pkl'); D = pd.read_pickle(CACHE + '/panel.pkl'); DC = D.close.values
S = S.sort_values(['s', 'i']).reset_index(drop=True)
case_q = S.index[(S.s == '2026-09-10') & (S.hhmm == '09:22')][0]
ALL = np.ones(len(S), bool)
C3 = (S.cl2 > S.close).values
PAT = ((S.gs0 >= 1.0) & (S.since_gb0 <= 3)).values
DEEP = (S.gs0 >= 1.0).values
days_sorted = sorted(S.s.unique()); mid = days_sorted[len(days_sorted) // 2]

# 당일 선행 패턴 신호 수 (자기 제외)
prior_pat = np.zeros(len(S), int); prior_deep = np.zeros(len(S), int); prior_sig = np.zeros(len(S), int)
for s, g in S.groupby('s'):
    ix = g.index.values
    prior_pat[ix] = np.r_[0, np.cumsum(PAT[ix])[:-1]]
    prior_deep[ix] = np.r_[0, np.cumsum(DEEP[ix])[:-1]]
    prior_sig[ix] = np.arange(len(ix))
S['prior_pat'] = prior_pat; S['prior_deep'] = prior_deep; S['prior_sig'] = prior_sig

def run_rule(keep_mask, entry_off=0, hold=90, cost=COST, loss_stop=None, sub=None):
    """비중복 포지션 시뮬. loss_stop=n: 당일 종료 포지션 손실 n건 누적 시 그날 신규진입 정지(인과적)."""
    sub = ALL if sub is None else sub
    daily = pd.Series(0.0, index=days_sorted); cnt = pd.Series(0, index=days_sorted); trades = []
    for s, g in S.groupby('s'):
        busy = -1; tot = 0.0; n = 0; losses = 0; open_list = []  # (exit_i, pnl)
        for q in g.index.values:
            if not (keep_mask[q] and sub[q]): continue
            i = int(S.i.values[q]); a = i + entry_off
            # 종료된 포지션 정산(인과)
            if loss_stop is not None:
                for ex, pn in list(open_list):
                    if ex <= a: losses += int(pn < 0); open_list.remove((ex, pn))
                if losses >= loss_stop: continue
            if a <= busy: continue
            j = min(a + hold, int(S.i1505.values[q]))
            if j <= a or a >= S.n.values[q]: continue
            row = int(S.row.values[q]); pn = DC[row + (j - i)] - DC[row + entry_off] - cost
            tot += pn; n += 1; busy = j; open_list.append((j, pn)); trades.append((s, S.hhmm.values[q], pn))
        daily.loc[s] = tot; cnt.loc[s] = n
    return daily, cnt, trades

def summarize(name, daily, cnt, base):
    d = daily - base; nz = d[d != 0]; pos = int((nz > 0).sum()); n = len(nz)
    p_sign = min(1.0, 2 * sum(comb(n, x) for x in range(min(pos, n - pos) + 1)) / 2 ** n) if n else np.nan
    boots = np.array([d.values[rng.integers(0, len(d), len(d))].sum() for _ in range(3000)])
    cum = daily.cumsum(); mdd = (cum.cummax() - cum).max()
    h1 = np.array([s < mid for s in daily.index])
    return dict(name=name, pos=int(cnt.sum()), total=daily.sum(), tot_h1=daily[h1].sum(), tot_h2=daily[~h1].sum(), mdd=mdd, t_day=daily.mean() / daily.std(ddof=1) * np.sqrt(len(daily)),
                delta=d.sum(), ci_lo=np.quantile(boots, .025), ci_hi=np.quantile(boots, .975), t_pair=d.mean() / d.std(ddof=1) * np.sqrt(len(d)) if d.std(ddof=1) > 0 else np.nan,
                days_better=pos, days_worse=n - pos, p_sign=p_sign, ex_best3=daily.sum() - daily.nlargest(3).sum(), ex_worst3=daily.sum() - daily.nsmallest(3).sum())

base, cbase, _ = run_rule(ALL)
rows = [summarize('기준 GB0.5 90분', base, cbase, base)]
items = [
    ('당일 선행 패턴 ≥1 이면 차단', (S.prior_pat < 1).values, 0, None),
    ('당일 선행 패턴 ≥2 이면 차단', (S.prior_pat < 2).values, 0, None),
    ('당일 선행 패턴 ≥3 이면 차단', (S.prior_pat < 3).values, 0, None),
    ('당일 선행 deep(GS≥1) ≥2 차단', (S.prior_deep < 2).values, 0, None),
    ('당일 선행 deep ≥3 차단', (S.prior_deep < 3).values, 0, None),
    ('당일 종료손실 1건 후 정지', ALL, 0, 1),
    ('당일 종료손실 2건 후 정지', ALL, 0, 2),
    ('당일 종료손실 3건 후 정지', ALL, 0, 3),
    ('무조건 i+2', ALL, 2, None),
    ('C3 → i+2', C3, 2, None),
    ('C3 → i+2 & 선행패턴≥2 차단', C3 & (S.prior_pat < 2).values, 2, None),
    ('C3 → i+2 & 종료손실 2건 정지', C3, 2, 2),
    ('선행패턴≥2 차단 & 종료손실 2건 정지', (S.prior_pat < 2).values, 0, 2),
    ('무조건 i+2 & 선행패턴≥2 차단', (S.prior_pat < 2).values, 2, None),
]
for name, k, off, ls in items:
    d_, c_, _ = run_rule(k, off, loss_stop=ls); rows.append(summarize(name, d_, c_, base))
print('=== 일자 상태 규칙 (인과적, 당일 선행 정보만) · 90분 보유 · CYBOS 비용 · 251일 ===')
print(pd.DataFrame(rows).round(2).to_string(index=False))

# 09-10 적용 결과
print('\n=== 2026-09-10 적용: 어느 포지션이 막히는가 ===')
for name, k, off, ls in [('기준', ALL, 0, None), ('선행패턴≥2 차단', (S.prior_pat < 2).values, 0, None), ('종료손실 2건 정지', ALL, 0, 2), ('C3 → i+2', C3, 2, None), ('C3 → i+2 & 선행패턴≥2', C3 & (S.prior_pat < 2).values, 2, None)]:
    _, _, tr = run_rule(k, off, loss_stop=ls, sub=(S.s == '2026-09-10').values)
    print('  %-22s %s  합계 %+.2f' % (name, ' | '.join('%s %+.2f' % (h, p) for _, h, p in tr), sum(p for _, _, p in tr)))
print(S[S.s == '2026-09-10'][['hhmm', 'gs0', 'since_gb0', 'prior_pat', 'prior_deep', 'r90']].round(2).to_string(index=False))

# ── 일자내 페어드: 같은 날 패턴 vs 비패턴 신호 평균차 ───────
print('\n=== 일자내 페어드 — 같은 날 안에서 패턴(GS≥1&신저3봉) 신호 r90 − 비패턴 신호 r90 ===')
rows = []
for lab, mk in [('전체', ALL), ('H1', (S.s < mid).values), ('H2', (S.s >= mid).values)]:
    diffs = []
    for s, g in S[mk].groupby('s'):
        a = g.r90[PAT[g.index.values]].dropna(); b = g.r90[~PAT[g.index.values]].dropna()
        if len(a) and len(b): diffs.append(a.mean() - b.mean())
    diffs = np.array(diffs); pos = int((diffs > 0).sum()); n = len(diffs)
    p = min(1.0, 2 * sum(comb(n, x) for x in range(min(pos, n - pos) + 1)) / 2 ** n)
    rows.append(dict(구간=lab, 일수=n, 평균차=diffs.mean(), 중앙차=np.median(diffs), 패턴우세일=pos, 부호검정p=p, t=diffs.mean() / diffs.std(ddof=1) * np.sqrt(n)))
print(pd.DataFrame(rows).round(3).to_string(index=False))
print('  → 같은 날 안에서는 09:22형 "신저 반등" 신호가 다른 신호보다 나쁘지 않다(오히려 낫다)는 것을 일자 페어드로 재확인')

# 진입 지연이 왜 이득인가: 신호봉 자체 수익 분포
print('\n=== 신호봉 성질: 신호봉 종가 − 전봉 종가, 다음봉 수익 ===')
prev_cl = np.array([DC[r - 1] for r in S.row.values]); nxt = S.cl1.values - S.close.values
print('  신호봉 상승폭 평균 %.3f pt (중앙 %.3f) · 다음봉(i→i+1) 평균 %.3f · i+1→i+2 평균 %.3f' % (np.mean(S.close.values - prev_cl), np.median(S.close.values - prev_cl), np.nanmean(nxt), np.nanmean(S.cl2.values - S.cl1.values)))
