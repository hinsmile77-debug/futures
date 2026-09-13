# -*- coding: utf-8 -*-
"""패널·신호 재생성 (ws_analysis.py 전반부와 동일 규약, Windows conda 의존 제거).

산출: panel.pkl / signals.pkl / fwd.npy — 전부 런타임 산출물(커밋 금지).
라이브 DB는 read-only 로만 연다. 장 마감 후 실행(456차).
"""
import os, sys, json, sqlite3, time
import numpy as np, pandas as pd

ROOT = 'C:/Users/82108/PycharmProjects/futures'
if not os.path.isdir(ROOT):
    ROOT = os.path.expanduser('~/mnt/futures')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))          # [559차 P0-2] analysis/ 를 임포트 경로에
from inv_unit_guard import invert_investor_log1p   # noqa: E402  단위 불일치 가드
RAW = os.path.join(ROOT, 'data/db/raw_data.db')

H = 180; N = 20; BAD = {"2026-05-13"}; LVL = 0.5
INV = ['foreign_futures_net', 'retail_futures_net', 'institution_futures_net',
       'foreign_call_net', 'foreign_put_net', 'program_arb_net', 'program_non_arb_net']

t0 = time.time()
con = sqlite3.connect('file:' + RAW + '?mode=ro', uri=True)
c = pd.read_sql_query('SELECT ts,open,high,low,close,volume,buy_vol,sell_vol,oi,'
                      'bar_recovered,book_bid_tot,book_ask_tot FROM raw_candles ORDER BY ts', con)
print('[db] raw_candles %d  %s ~ %s  %.1fs' % (len(c), c.ts.iloc[0], c.ts.iloc[-1], time.time() - t0))

KEYS = INV + ['quality_investor_supported', 'atr', 'rsi', 'gp_buy_20', 'gp_sell_20', 'ma20_cont', 'ma60_cont']
cur = con.cursor()
cur.execute("SELECT ts, features FROM raw_features WHERE ts >= '2026-06-01' ORDER BY ts")
rows = []
for ts, f in cur:
    d = json.loads(f)
    rows.append({'ts': ts, **{k: d.get(k) for k in KEYS}})
con.close()
F = pd.DataFrame(rows)
print('[db] raw_features %d  %s ~ %s  %.1fs' % (len(F), F.ts.iloc[0], F.ts.iloc[-1], time.time() - t0))

c['dt'] = pd.to_datetime(c.ts); c['s'] = c.dt.dt.strftime('%Y-%m-%d'); c['hhmm'] = c.dt.dt.strftime('%H:%M')
c = c[(c.hhmm >= '09:00') & (c.hhmm <= '15:08')].sort_values('dt').drop_duplicates('dt')

F['dt'] = pd.to_datetime(F.ts).dt.floor('min'); F = F.drop_duplicates('dt').set_index('dt')
# [559차 P0-2] 종전 로컬 inv() 는 clip(|v|,0,30) 이라 압축 이전 단위 4일
# (2026-06-02·04·05·08)에서 expm1(30)*1000 = 1.0686e+16 으로 **포화**했다.
# 그 값이 「센티널 -1.07e16」으로 오독돼 왔다 — 가드가 날짜 규칙으로 먼저 뺀다.
_sup = F['quality_investor_supported'].values if 'quality_investor_supported' in F.columns else None
for k in INV:
    F[k + '_raw'] = invert_investor_log1p(F[k].values, _sup, F.index.astype(str), name=k)

L = pd.read_pickle(os.path.join(HERE, 'divpanel_full.pkl'))
L = L[['fi_fut', 'rt_fut', 'inst_fut', 'fi_call', 'rt_call', 'fi_put', 'rt_put']]

parts, fwds, dropped = [], [], []
for s, g in c.groupby('s'):
    if s in BAD:        dropped.append((s, 'oil')); continue
    if len(g) < 300:    dropped.append((s, 'short%d' % len(g))); continue
    g = g.set_index('dt'); grid = pd.date_range(g.index[0], g.index[-1], freq='1min'); r = g.reindex(grid)
    r[['open', 'high', 'low', 'close']] = r[['open', 'high', 'low', 'close']].ffill()
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
D['ma20c'] = pd.Series(cl).rolling(20).mean().values
D['ma60c'] = pd.Series(cl).rolling(60).mean().values
dlt = pd.Series(cl).diff(); up = dlt.clip(lower=0); dn = (-dlt).clip(lower=0)
rs = up.rolling(14).mean() / dn.rolling(14).mean().replace(0, np.nan)
D['rsi'] = (100 - 100 / (1 + rs)).values
st = (D.bv / D.sv.replace(0, np.nan) * 100.0); st[(D.bv.isna()) | (D.bv + D.sv < 1)] = np.nan
D['str'] = st.values; D['str5'] = st.rolling(5, min_periods=3).mean().values
D['str20'] = st.rolling(20, min_periods=10).mean().values

D = D.merge(F[[k + '_raw' for k in INV]].rename(columns=lambda x: x.replace('_net_raw', '')),
            left_on='dt', right_index=True, how='left')
D = D.merge(L, left_on='dt', right_index=True, how='left')

gbv = D.gb.values; prev = np.r_[np.nan, gbv[:-1]]; same = D.s.values == np.r_[None, D.s.values[:-1]]
sig = (prev < LVL) & (gbv >= LVL) & same & (D.hhmm.values >= '09:20') & (D.hhmm.values <= '14:50')
sig &= (D.i.values + 2 < D.n.values)
S = D.loc[sig].copy(); S['row'] = S.index.values
print('[signals] n=%d days=%d' % (len(S), S.s.nunique()))

R = S.row.values; DC = D.close.values


def lag(col, k):
    v = D[col].values; out = np.full(len(S), np.nan)
    ok = S.i.values - k >= 0; out[ok] = v[R[ok] - k]; return out


def lead(col, k):
    v = D[col].values; out = np.full(len(S), np.nan)
    ok = S.i.values + k < S.n.values; out[ok] = v[R[ok] + k]; return out


def ret_h(h, off=0):
    out = np.full(len(S), np.nan)
    for q, (r, i, n, i5) in enumerate(zip(R, S.i.values, S.n.values, S.i1505.values)):
        a = i + off; j = min(a + h, i5)
        if j > a and a < n: out[q] = DC[r + (j - i)] - DC[r + off]
    return out


for h in (5, 10, 15, 30, 60, 90):
    S['r%d' % h] = ret_h(h)
S['c2_r90'] = ret_h(90, off=2)
atr0 = S.atr.values; f90 = FWD[R, :90]
S['mfe90'] = np.nanmax(f90, axis=1) / atr0
S['mae90'] = -np.nanmin(f90, axis=1) / atr0
S['gs0'] = S.gs; S['ma_down'] = S.ma20c < S.ma60c
S['ret15'] = S.close.values - lag('close', 15)
S['gb1'] = lead('gb', 1); S['gb2'] = lead('gb', 2)
S['cl1'] = lead('close', 1); S['cl2'] = lead('close', 2)

D.to_pickle(os.path.join(HERE, 'panel.pkl'))
S.reset_index(drop=True).to_pickle(os.path.join(HERE, 'signals.pkl'))
np.save(os.path.join(HERE, 'fwd.npy'), FWD)
print('[save] panel/signals/fwd  %.1fs' % (time.time() - t0))
