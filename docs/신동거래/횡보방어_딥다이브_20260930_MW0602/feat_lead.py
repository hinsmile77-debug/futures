# -*- coding: utf-8 -*-
"""76일 — 어떤 피처가 **앞으로 60분의 횡보**를 미리 알려주나(사전 감지).
라벨: t 이후 60분 고저 범위(pt). 「횡보」= 전체 분포 하위 1/3. 피처는 t 시점 값(미래 참조 없음).
지표: 피처 하위/상위 1/3 구간에서 횡보 비율(기저 33%) · 순위상관(스피어만)."""
import sqlite3, json, collections, statistics as st, math, sys
r=sqlite3.connect("data/db/raw_data.db")
KEYS=["trend_efficiency","hurst","atr","atr_bp","realized_vol_ann","bar_volume","va_bandwidth","in_value_area","multi_timeframe_5m","multi_timeframe_15m","rv_iv_spread","swing60_range_pos","swing_day_range_pos","bb_position","price_extension_atr_60m","kyle_lambda","vpin","toxicity_score_ma","atr_ratio","atr_expansion_rate","cvd_delta_norm","volume_acceleration","mlofi_norm","queue_signal_ma","vwap_position","opt_pcr_norm","rv_iv_spread_ready"]
days=[x[0] for x in r.execute("select distinct substr(ts,1,10) from raw_candles where ts>='2026-06-09' and ts<'2026-10-01' order by 1")]
rows=[]   # (day, hm, fwd_range, trailing_range, feats)
for d in days:
    C={ts[11:16]:(h,l) for ts,h,l in r.execute("select ts,high,low from raw_candles where ts like ?",(d+"%",))}
    F={ts[11:16]:json.loads(f) for ts,f in r.execute("select ts,features from raw_features where ts like ?",(d+"%",))}
    ks=sorted(k for k in C if "09:00"<=k<="15:05")
    for i,k in enumerate(ks):
        if not ("09:31"<=k<="14:00") or k not in F: continue
        fw=ks[i+1:i+61]; bw=ks[max(0,i-59):i+1]
        if len(fw)<55: continue
        fr=max(C[x][0] for x in fw)-min(C[x][1] for x in fw); br=max(C[x][0] for x in bw)-min(C[x][1] for x in bw)
        rows.append((d,k,fr,br,F[k]))
fr_all=sorted(x[2] for x in rows); thr=fr_all[len(fr_all)//3]
print("표본 %d분 · %d일 · 앞 60분 범위 중앙 %.2fpt · 횡보 문턱(하위 1/3) %.2fpt"%(len(rows),len(days),fr_all[len(fr_all)//2],thr))
def spearman(xs,ys):
    def rank(v):
        o=sorted(range(len(v)),key=lambda i:v[i]); rk=[0]*len(v)
        for j,i in enumerate(o): rk[i]=j
        return rk
    rx,ry=rank(xs),rank(ys); mx,my=st.mean(rx),st.mean(ry)
    sxy=sum((a-mx)*(b-my) for a,b in zip(rx,ry)); sx=math.sqrt(sum((a-mx)**2 for a in rx)); sy=math.sqrt(sum((b-my)**2 for b in ry))
    return sxy/(sx*sy) if sx and sy else 0
print("%-24s %6s %8s %8s %8s  %s"%("피처","n","하위1/3","상위1/3","스피어만","(횡보 비율 — 기저 33%)"))
res=[]
for k in KEYS+["_trailing60_range","_trailing60_over_atr"]:
    xs,ys=[],[]
    for d,hm,fr,br,f in rows:
        v = br if k=="_trailing60_range" else (br/f["atr"] if k=="_trailing60_over_atr" and f.get("atr") else f.get(k))
        if isinstance(v,(int,float)) and v==v: xs.append(v); ys.append(1 if fr<=thr else 0)
    if len(xs)<1000 or len(set(xs))<3: continue
    o=sorted(range(len(xs)),key=lambda i:xs[i]); n=len(o); lo=o[:n//3]; hi=o[-(n//3):]
    res.append((k,n,st.mean(ys[i] for i in lo),st.mean(ys[i] for i in hi),spearman(xs,[float(y) for y in ys])))
for k,n,lo,hi,sp in sorted(res,key=lambda z:-abs(z[4])):
    print("%-24s %6d %7.0f%% %7.0f%% %+8.3f"%(k,n,100*lo,100*hi,sp))
