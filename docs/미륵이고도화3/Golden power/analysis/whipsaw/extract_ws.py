# -*- coding: utf-8 -*-
"""휩소 분석용 스냅샷 — 장 마감 후/장전 전용(456차)."""
# [566차 T-BOOK-1c] book_*_tot(점표본) 은 폐기 예정이다 —
# 봉 대표값은 _avg, 봉내 극단은 _max. rho(tot,avg)=+0.288 로 다른 계열처럼 움직인다.
import sys, os, time, sqlite3, json
sys.path.insert(0, 'C:/Users/82108/PycharmProjects/futures')
from utils.dll_bootstrap import ensure_conda_dll_path
ensure_conda_dll_path()
import pandas as pd
OUT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(OUT), 'GP_test')   # [MW0601 631차] pkl/npy 캐시 — 커밋 제외(GP_test/.gitignore)
os.makedirs(CACHE, exist_ok=True)
raw = 'C:/Users/82108/PycharmProjects/futures/data/db/raw_data.db'
t0 = time.time()
con = sqlite3.connect('file:' + raw + '?mode=ro', uri=True)
c = pd.read_sql_query('SELECT ts,open,high,low,close,volume,buy_vol,sell_vol,oi,bar_recovered,book_bid_avg,book_ask_avg,book_bid_max,book_ask_max FROM raw_candles ORDER BY ts', con)
c.to_pickle(os.path.join(CACHE, 'candles.pkl'))
print('candles', len(c), c.ts.iloc[0], c.ts.iloc[-1], '%.1fs' % (time.time()-t0))
KEYS = ['foreign_futures_net','retail_futures_net','institution_futures_net','foreign_call_net','foreign_put_net',
        'quality_investor_supported','quality_investor_stale','quality_investor_option_supported',
        'program_arb_net','program_non_arb_net','atr','ret_1m','ret_5m','ret_15m','multi_timeframe_5m','multi_timeframe_15m',
        'trend_efficiency','vwap_position','vwap_momentum','cvd_delta_norm','ofi_norm','mlofi_norm','bars_since_high_60m','bars_since_low_60m',
        'price_extension_atr','swing_high_60m','swing_low_60m','rsi','opt_chain_pcr','opt_atm_pcr','opt_gex_bn','kyle_lambda','vpin',
        'toxicity_score','spread_ticks','queue_signal','microprice_bias','gp_buy_20','gp_sell_20','ma20_cont','ma60_cont','hurst','above_vwap']
cur = con.cursor()
cur.execute("SELECT ts, features FROM raw_features WHERE ts >= '2026-06-01' ORDER BY ts")
rows = []
for ts, f in cur:
    d = json.loads(f)
    r = {'ts': ts}
    for k in KEYS:
        r[k] = d.get(k)
    rows.append(r)
con.close()
F = pd.DataFrame(rows)
F.to_pickle(os.path.join(CACHE, 'feats.pkl'))
print('feats', len(F), F.ts.iloc[0], F.ts.iloc[-1], '%.1fs' % (time.time()-t0))
print(F[['foreign_futures_net','retail_futures_net','foreign_call_net','quality_investor_supported']].describe())
