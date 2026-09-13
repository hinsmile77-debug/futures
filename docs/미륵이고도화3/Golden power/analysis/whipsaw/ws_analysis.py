# -*- coding: utf-8 -*-
"""GB 0.5 상향돌파 휩소 판별 — 사전 컨텍스트 필터 + 사후 1~2봉 확인 평가.
진입가 = 신호봉 종가(라이브 섀도 GP_LONG_GB90 과 동일: 09:22 진입가 1111.48 = 09:22 종가)."""
import sys, os
sys.path.insert(0, 'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path; ensure_conda_dll_path()
import numpy as np, pandas as pd
np.set_printoptions(suppress=True)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 200)
HERE = os.path.dirname(os.path.abspath(__file__))
H = 180; N = 20; BAD = {"2026-05-13"}; COST = 0.246018; LVL = 0.5
rng = np.random.default_rng(553)

c = pd.read_pickle(HERE + '/candles.pkl')
c['dt'] = pd.to_datetime(c.ts); c['s'] = c.dt.dt.strftime('%Y-%m-%d'); c['hhmm'] = c.dt.dt.strftime('%H:%M')
c = c[(c.hhmm >= '09:00') & (c.hhmm <= '15:08')].sort_values('dt').drop_duplicates('dt')
F = pd.read_pickle(HERE + '/feats.pkl'); F['dt'] = pd.to_datetime(F.ts).dt.floor('min'); F = F.drop_duplicates('dt').set_index('dt')
# [559차 P0-2] 종전 로컬 inv() 는 클립조차 없어 압축 이전 단위 4일에서 inf 가 됐다.
sys.path.insert(0, os.path.dirname(HERE))
from inv_unit_guard import invert_investor_log1p  # noqa: E402
INV = ['foreign_futures_net','retail_futures_net','institution_futures_net','foreign_call_net','foreign_put_net','program_arb_net','program_non_arb_net']
_sup = F['quality_investor_supported'].values if 'quality_investor_supported' in F.columns else None
for k in INV: F[k + '_raw'] = invert_investor_log1p(F[k].values, _sup, F.index.astype(str), name=k)
L = pd.read_pickle(HERE + '/divpanel.pkl')

# ── 세션 패널 ──────────────────────────────────────────────
parts, fwds, dropped = [], [], []
for s, g in c.groupby('s'):
    if s in BAD: dropped.append((s, 'oil')); continue
    if len(g) < 300: dropped.append((s, 'short%d' % len(g))); continue
    g = g.set_index('dt'); grid = pd.date_range(g.index[0], g.index[-1], freq='1min'); r = g.reindex(grid)
    r[['open','high','low','close']] = r[['open','high','low','close']].ffill()
    cl = r.close.values.astype(float); hi = r.high.values.astype(float); lo = r.low.values.astype(float)
    n = len(cl); sr = pd.Series(cl)
    gb = ((sr - sr.rolling(N, min_periods=N).min()) / sr * 200).values
    gs = ((sr.rolling(N, min_periods=N).max() - sr) / sr * 200).values
    pc = np.r_[np.nan, cl[:-1]]
    tr = np.nanmax(np.c_[hi - lo, np.abs(hi - pc), np.abs(lo - pc)], axis=1)
    atr = pd.Series(tr).rolling(14, min_periods=14).mean().values
    fwd = np.full((n, H), np.nan, np.float32)
    for t in range(H):
        j = np.arange(n) + 1 + t; ok = j < n
        fwd[ok, t] = cl[j[ok]] - cl[ok]
    hh = [t.strftime('%H:%M') for t in grid]
    i1505 = next((k for k, x in enumerate(hh) if x >= '15:05'), n - 1)
    parts.append(pd.DataFrame(dict(dt=grid, s=s, i=np.arange(n), hhmm=hh, close=cl, high=hi, low=lo,
                                   vol=r.volume.values, bv=r.buy_vol.values, sv=r.sell_vol.values,
                                   gb=gb, gs=gs, atr=atr, i1505=i1505, n=n)))
    fwds.append(fwd)
D = pd.concat(parts, ignore_index=True); FWD = np.vstack(fwds)
print('[panel] sessions %d bars %d dropped %d' % (D.s.nunique(), len(D), len(dropped)))
cl = D.close.values
D['ma20c'] = pd.Series(cl).rolling(20).mean().values; D['ma60c'] = pd.Series(cl).rolling(60).mean().values
dlt = pd.Series(cl).diff(); up = dlt.clip(lower=0); dn = (-dlt).clip(lower=0)
rs = up.rolling(14).mean() / dn.rolling(14).mean().replace(0, np.nan)
D['rsi'] = (100 - 100 / (1 + rs)).values
obv = (np.sign(dlt.fillna(0)) * D.vol.fillna(0)).cumsum(); D['obv'] = obv.values; D['obv_sig'] = obv.rolling(9).mean().values
st = (D.bv / D.sv.replace(0, np.nan) * 100.0)
st[(D.bv.isna()) | (D.bv + D.sv < 1)] = np.nan
D['str'] = st.values
D['str5'] = st.rolling(5, min_periods=3).mean().values; D['str20'] = st.rolling(20, min_periods=10).mean().values; D['str60'] = st.rolling(60, min_periods=30).mean().values
D = D.merge(F[[k + '_raw' for k in INV]].rename(columns=lambda x: x.replace('_net_raw', '')), left_on='dt', right_index=True, how='left')
D = D.merge(L, left_on='dt', right_index=True, how='left')

# ── 신호 ────────────────────────────────────────────────────
gbv = D.gb.values; prev = np.r_[np.nan, gbv[:-1]]; same = D.s.values == np.r_[None, D.s.values[:-1]]
sig = (prev < LVL) & (gbv >= LVL) & same & (D.hhmm.values >= '09:20') & (D.hhmm.values <= '14:50')
sig &= (D.i.values + 2 < D.n.values)
S = D.loc[sig].copy(); S['row'] = S.index.values
print('[signals] n=%d days=%d' % (len(S), S.s.nunique()))

def lag(col, k):
    v = D[col].values; out = np.full(len(S), np.nan)
    ok = S.i.values - k >= 0; out[ok] = v[S.row.values[ok] - k]; return out
def lead(col, k):
    v = D[col].values; out = np.full(len(S), np.nan)
    ok = S.i.values + k < S.n.values; out[ok] = v[S.row.values[ok] + k]; return out
def win_max(col, k):
    v = D[col].values; return np.array([np.nanmax(v[r - k:r]) if i >= k else np.nan for r, i in zip(S.row.values, S.i.values)])
def bars_since(cond):
    out = np.full(len(S), np.nan)
    for q, (r, i) in enumerate(zip(S.row.values, S.i.values)):
        seg = cond[r - i:r]; w = np.where(seg)[0]
        if len(w): out[q] = i - w[-1]
    return out

R = S.row.values; atr0 = S.atr.values
def ret_h(h):
    out = np.full(len(S), np.nan)
    for q, (r, i, n, i5) in enumerate(zip(R, S.i.values, S.n.values, S.i1505.values)):
        j = min(i + h, i5)
        if j > i: out[q] = D.close.values[r + (j - i)] - D.close.values[r]
    return out
for h in (5, 10, 15, 30, 60, 90): S['r%d' % h] = ret_h(h)
f90 = FWD[R, :90]
S['mfe90'] = np.nanmax(f90, axis=1) / atr0; S['mae90'] = -np.nanmin(f90, axis=1) / atr0
def stop_first(k=1.0):
    out = np.zeros(len(S), bool)
    for q in range(len(S)):
        p = f90[q] / atr0[q]; a = np.where(p <= -k)[0]; b = np.where(p >= k)[0]
        out[q] = (len(a) > 0) and (len(b) == 0 or a[0] < b[0])
    return out
S['stopfirst'] = stop_first()
S['win90'] = S.r90 > 0

S['gs0'] = S.gs; S['dir0'] = S.gb - S.gs
S['gb_max10'] = win_max('gb', 10); S['gb_max5'] = win_max('gb', 5)
S['since_gb0'] = bars_since(D.gb.values <= 1e-9)
S['since_gs0'] = bars_since(D.gs.values <= 1e-9)
S['ma_down'] = S.ma20c < S.ma60c
S['ma20_slope5'] = S.ma20c.values - lag('ma20c', 5)
S['ret15'] = S.close.values - lag('close', 15); S['ret5'] = S.close.values - lag('close', 5)
S['ext_hi60'] = (np.array([np.nanmax(D.close.values[max(r - 60, r - i):r + 1]) for r, i in zip(R, S.i.values)]) - S.close.values) / atr0
S['rsi_slope3'] = S.rsi.values - lag('rsi', 3)
S['obv_above'] = S.obv > S.obv_sig; S['obv_slope5'] = S.obv.values - lag('obv', 5)
S['str5_slope3'] = S.str5.values - lag('str5', 3); S['str5_gt20'] = S.str5 > S.str20; S['str5_gt60'] = S.str5 > S.str60
for k, nm in [('foreign_futures', 'fi'), ('retail_futures', 'rt'), ('institution_futures', 'inst'), ('foreign_call', 'fic'), ('foreign_put', 'fip'), ('program_non_arb', 'nonarb')]:
    for d in (5, 10, 15):
        S['%s_d%d' % (nm, d)] = S[k].values - lag(k, d)
for k in ('rt_call', 'rt_put', 'fi_call', 'fi_put', 'fi_fut'):
    for d in (5, 10): S['%s_d%d' % (k, d)] = S[k].values - lag(k, d)
S['gb1'] = lead('gb', 1); S['gb2'] = lead('gb', 2); S['cl1'] = lead('close', 1); S['cl2'] = lead('close', 2)
S['fi_post2'] = lead('foreign_futures', 2) - S.foreign_futures.values
S['rtc_post2'] = lead('rt_call', 2) - S.rt_call.values; S['rtp_post2'] = lead('rt_put', 2) - S.rt_put.values
S['gs1'] = lead('gs', 1); S['gs2'] = lead('gs', 2)
def ret_from(k, h):
    out = np.full(len(S), np.nan)
    for q, (r, i, n, i5) in enumerate(zip(R, S.i.values, S.n.values, S.i1505.values)):
        a = i + k; j = min(a + h, i5)
        if j > a and a < n: out[q] = D.close.values[r + (j - i)] - D.close.values[r + k]
    return out
for h in (10, 30, 60, 90): S['c2_r%d' % h] = ret_from(2, h)
S['c1_r90'] = ret_from(1, 90)
S['half'] = np.where(S.s < sorted(S.s.unique())[len(S.s.unique()) // 2], 1, 2)
S.to_pickle(HERE + '/signals.pkl'); D.to_pickle(HERE + '/panel.pkl')

case = S[(S.s == '2026-09-10') & (S.hhmm == '09:22')]
print('\n=== 2026-09-10 09:22 사례 ===')
cols = ['close','gb','gs0','dir0','gb_max10','since_gb0','since_gs0','ma20c','ma60c','ma_down','ma20_slope5','ret5','ret15','ext_hi60','rsi','rsi_slope3','obv_above','obv_slope5','str5','str20','str60','str5_slope3',
        'fi_d5','fi_d10','fi_d15','rt_d5','rt_d10','inst_d5','fic_d5','fip_d5','nonarb_d5','rt_call_d5','rt_put_d5','fi_call_d5','fi_put_d5',
        'gb1','gb2','cl1','cl2','fi_post2','rtc_post2','rtp_post2','r10','r30','r60','r90','mfe90','mae90','stopfirst']
print(case[cols].T.to_string())

def perm_p(x, keep, days, nrep=2000):
    obs = np.nanmean(x[keep]) - np.nanmean(x[~keep]); cnt = 0
    idx_by_day = [np.where(days == d)[0] for d in np.unique(days)]
    for _ in range(nrep):
        k2 = keep.copy()
        for ix in idx_by_day: k2[ix] = rng.permutation(keep[ix])
        if k2.sum() == 0 or (~k2).sum() == 0: continue
        if abs(np.nanmean(x[k2]) - np.nanmean(x[~k2])) >= abs(obs): cnt += 1
    return obs, cnt / nrep

def evaluate(filters, sub=None, label=''):
    T = S if sub is None else S[sub]
    rows = []
    rows.append(dict(name='(무필터)', n_keep=len(T), n_excl=0, r10_k=T.r10.mean(), r90_k=T.r90.mean(), r90_e=np.nan, d90=np.nan, p=np.nan,
                     win_k=T.win90.mean(), win_e=np.nan, sf_k=T.stopfirst.mean(), sf_e=np.nan, d90_h1=np.nan, d90_h2=np.nan, blk0922=np.nan))
    for name, fn in filters:
        keep = np.asarray(fn(T)).astype(bool)
        m = ~np.isnan(T.r90.values)
        if keep[m].sum() < 10 or (~keep[m]).sum() < 10:
            rows.append(dict(name=name, n_keep=int(keep[m].sum()), n_excl=int((~keep[m]).sum()))); continue
        x = T.r90.values[m]; k = keep[m]; days = T.s.values[m]
        d, p = perm_p(x, k, days)
        h = T.half.values[m]
        d1 = np.nanmean(x[k & (h == 1)]) - np.nanmean(x[~k & (h == 1)]) if (k & (h == 1)).sum() > 5 and (~k & (h == 1)).sum() > 5 else np.nan
        d2 = np.nanmean(x[k & (h == 2)]) - np.nanmean(x[~k & (h == 2)]) if (k & (h == 2)).sum() > 5 and (~k & (h == 2)).sum() > 5 else np.nan
        cq = case.index[0] if len(case) else None
        blk = (not bool(keep[T.index.get_loc(cq)])) if (cq is not None and cq in T.index) else np.nan
        rows.append(dict(name=name, n_keep=int(k.sum()), n_excl=int((~k).sum()), r10_k=np.nanmean(T.r10.values[m][k]), r90_k=np.nanmean(x[k]), r90_e=np.nanmean(x[~k]),
                         d90=d, p=p, win_k=T.win90.values[m][k].mean(), win_e=T.win90.values[m][~k].mean(),
                         sf_k=T.stopfirst.values[m][k].mean(), sf_e=T.stopfirst.values[m][~k].mean(), d90_h1=d1, d90_h2=d2, blk0922=blk))
    out = pd.DataFrame(rows)
    print('\n=== 필터 평가 %s (r90 = 90분 보유 gross pt, keep=필터 통과) ===' % label)
    print(out.round(3).to_string(index=False))
    return out

F_STRUCT = [
    ('GS0<1.0 (20봉고점 근접)', lambda T: T.gs0 < 1.0),
    ('GS0<0.5', lambda T: T.gs0 < 0.5),
    ('dir0>0 (GB>GS)', lambda T: T.dir0 > 0),
    ('GB_max10<1.0 (직전10봉 GB 낮음)', lambda T: T.gb_max10 < 1.0),
    ('since_gb0>3 (신저 직후 반등 아님)', lambda T: ~(T.since_gb0 <= 3)),
    ('since_gb0>5', lambda T: ~(T.since_gb0 <= 5)),
    ('MA20>=MA60 (cont)', lambda T: ~T.ma_down),
    ('MA20 slope5>=0', lambda T: T.ma20_slope5 >= 0),
    ('ret15>=0', lambda T: T.ret15 >= 0),
    ('ext_hi60<1.5ATR', lambda T: T.ext_hi60 < 1.5),
    ('RSI>=40', lambda T: T.rsi >= 40),
    ('RSI>=50', lambda T: T.rsi >= 50),
    ('RSI slope3>0', lambda T: T.rsi_slope3 > 0),
    ('OBV>Signal9', lambda T: T.obv_above),
    ('OBV slope5>0', lambda T: T.obv_slope5 > 0),
]
evaluate(F_STRUCT, label='구조 — 전기간')
F_STR = [
    ('체결강도 MA5>MA20', lambda T: T.str5_gt20),
    ('체결강도 MA5>MA60', lambda T: T.str5_gt60),
    ('체결강도 MA5 slope3>0', lambda T: T.str5_slope3 > 0),
    ('체결강도 MA5>100', lambda T: T.str5 > 100),
]
evaluate(F_STR, sub=(S.s >= '2026-06-08') & S.str5.notna(), label='체결강도 — 2026-06-08~')
inv_sub = S.foreign_futures.notna() & S.fi_d10.notna()
F_INV = [
    ('외인선물 d5>=0', lambda T: T.fi_d5 >= 0), ('외인선물 d10>=0', lambda T: T.fi_d10 >= 0), ('외인선물 d15>=0', lambda T: T.fi_d15 >= 0),
    ('외인선물 d10>0 엄격', lambda T: T.fi_d10 > 0),
    ('개인선물 d10<=0', lambda T: T.rt_d10 <= 0), ('기관선물 d10>=0', lambda T: T.inst_d10 >= 0),
    ('외인콜 d10>=0', lambda T: T.fic_d10 >= 0), ('외인풋 d10<=0', lambda T: T.fip_d10 <= 0),
    ('비차익 d10>=0', lambda T: T.nonarb_d10 >= 0),
    ('외인선물 d10>=0 & 개인 d10<=0', lambda T: (T.fi_d10 >= 0) & (T.rt_d10 <= 0)),
]
evaluate(F_INV, sub=inv_sub, label='수급(TR 원값 역변환) — 2026-06-02~')
log_sub = S.rt_call.notna() & S.rt_call_d10.notna()
F_LOG = [
    ('개인콜 d10>=0', lambda T: T.rt_call_d10 >= 0), ('개인풋 d10<=0', lambda T: T.rt_put_d10 <= 0),
    ('개인콜↑&개인풋↓ d10', lambda T: (T.rt_call_d10 >= 0) & (T.rt_put_d10 <= 0)),
    ('외인선물(log) d10>=0', lambda T: T.fi_fut_d10 >= 0),
]
evaluate(F_LOG, sub=log_sub, label='개인 콜/풋(로그) — 2026-08-10~')

print('\n=== 사후 확인 — 확인 통과 신호를 close[i+2]에 진입 vs 기준 ===')
confs = [
    ('C1 GB1>GB0', S.gb1 > S.gb), ('C2 GB2>=0.5', S.gb2 >= 0.5), ('C3 cl2>cl0', S.cl2 > S.close),
    ('C4 GB1>=0.5&GB2>=0.5', (S.gb1 >= 0.5) & (S.gb2 >= 0.5)), ('C5 GB2>GB0', S.gb2 > S.gb),
    ('C6 GB2>GB1>GB0 (연속상승)', (S.gb2 > S.gb1) & (S.gb1 > S.gb)),
    ('C7 cl2>cl0 & GB2>=0.5', (S.cl2 > S.close) & (S.gb2 >= 0.5)),
]
rows = []
m0 = ~np.isnan(S.c2_r90.values) & ~np.isnan(S.r90.values)
rows.append(dict(name='기준 close[i] 전신호', n=int(m0.sum()), r10=S.r10[m0].mean(), r90=S.r90[m0].mean(), win=S.win90[m0].mean()))
rows.append(dict(name='기준 close[i+2] 전신호(무조건 2봉 지연)', n=int(m0.sum()), r10=S.c2_r10[m0].mean(), r90=S.c2_r90[m0].mean(), win=(S.c2_r90[m0] > 0).mean()))
for name, k in confs:
    k = k.values & m0
    d, p = perm_p(S.c2_r90.values[m0], k[m0], S.s.values[m0])
    rows.append(dict(name=name + ' → close[i+2]', n=int(k.sum()), r10=S.c2_r10[k].mean(), r90=S.c2_r90[k].mean(), win=(S.c2_r90[k] > 0).mean(),
                     r90_same_from_i=S.r90[k].mean(), excl_r90_i2=S.c2_r90[m0 & ~k].mean(), d_vs_excl=d, p=p,
                     h1=S.c2_r90[k & (S.half.values == 1)].mean() - S.c2_r90[m0 & ~k & (S.half.values == 1)].mean(),
                     h2=S.c2_r90[k & (S.half.values == 2)].mean() - S.c2_r90[m0 & ~k & (S.half.values == 2)].mean(),
                     blk0922=(not bool(k[S.index.get_loc(case.index[0])])) if len(case) else np.nan))
print(pd.DataFrame(rows).round(3).to_string(index=False))
print('\n--- 수급 사후 확인 (2026-06-02~ 지원행) ---')
rows = []
mi = m0 & inv_sub.values
for name, k in [('P1 외인선물 post2>=0', S.fi_post2 >= 0), ('P2 외인 d10>=0 & post2>=0', (S.fi_d10 >= 0) & (S.fi_post2 >= 0)), ('P3 C4 & 외인 post2>=0', (S.gb1 >= 0.5) & (S.gb2 >= 0.5) & (S.fi_post2 >= 0))]:
    k = k.values & mi
    d, p = perm_p(S.c2_r90.values[mi], k[mi], S.s.values[mi])
    rows.append(dict(name=name, n=int(k.sum()), n_all=int(mi.sum()), r90_keep=S.c2_r90[k].mean(), r90_excl=S.c2_r90[mi & ~k].mean(), d=d, p=p, win=(S.c2_r90[k] > 0).mean()))
print(pd.DataFrame(rows).round(3).to_string(index=False))

def backtest(keep_mask, entry_off=0, hold=90, cost=COST):
    T = S[keep_mask]; pnl = []; days = []
    for s, g in T.groupby('s'):
        busy = -1
        for _, rw in g.iterrows():
            i = int(rw.i) + entry_off
            if i <= busy: continue
            j = min(i + hold, int(rw.i1505))
            if j <= i or i >= rw.n: continue
            pnl.append(D.close.values[int(rw.row) + (j - int(rw.i))] - D.close.values[int(rw.row) + entry_off] - cost); days.append(s); busy = j
    p = pd.Series(pnl, index=days); dd = p.groupby(level=0).sum()
    allday = pd.Series(0.0, index=sorted(S.s.unique())); allday.loc[dd.index] = dd.values
    cum = allday.cumsum(); mdd = (cum.cummax() - cum).max()
    t = allday.mean() / allday.std(ddof=1) * np.sqrt(len(allday)) if allday.std(ddof=1) > 0 else np.nan
    best3 = allday.nlargest(3).sum()
    return dict(n=len(p), total=p.sum(), per=p.mean() if len(p) else np.nan, win=(p > 0).mean() if len(p) else np.nan, t_day=t, mdd=mdd, ex_best3=p.sum() - best3, days_pos=int((allday > 0).sum()), days_neg=int((allday < 0).sum()))
print('\n=== 포지션 단위 백테스트 (비중복 90분, CYBOS 비용 %.3f) ===' % COST)
BT = [('기준 GB0.5 90분', np.ones(len(S), bool), 0),
      ('GS0<1.0', (S.gs0 < 1.0).values, 0), ('since_gb0>3', (~(S.since_gb0 <= 3)).values, 0), ('RSI>=40', (S.rsi >= 40).values, 0),
      ('MA20>=MA60', (~S.ma_down).values, 0), ('OBV>Sig9', S.obv_above.values, 0),
      ('C4 GB1,GB2>=0.5 → i+2', ((S.gb1 >= 0.5) & (S.gb2 >= 0.5)).values, 2), ('C3 cl2>cl0 → i+2', (S.cl2 > S.close).values, 2),
      ('C7 cl2>cl0&GB2>=0.5 → i+2', ((S.cl2 > S.close) & (S.gb2 >= 0.5)).values, 2),
      ('무조건 i+2 지연', np.ones(len(S), bool), 2)]
rows = []
for name, k, off in BT:
    r = backtest(k, off); r['name'] = name; rows.append(r)
    r1 = backtest(k & (S.half.values == 1), off); r2 = backtest(k & (S.half.values == 2), off)
    r['tot_h1'] = r1['total']; r['tot_h2'] = r2['total']
print(pd.DataFrame(rows)[['name','n','total','per','win','t_day','mdd','ex_best3','days_pos','days_neg','tot_h1','tot_h2']].round(2).to_string(index=False))
print('\n--- 같은 필터, 10분 보유 ---')
rows = []
for name, k, off in BT:
    r = backtest(k, off, hold=10); r['name'] = name; rows.append(r)
print(pd.DataFrame(rows)[['name','n','total','per','win','t_day','mdd','ex_best3']].round(2).to_string(index=False))
