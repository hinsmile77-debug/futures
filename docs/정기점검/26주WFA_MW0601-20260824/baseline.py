# -*- coding: utf-8 -*-
"""L3 해석용 무정보 기준선 — 라벨 분포와 '항상 최빈 클래스' 정확도.
L3의 acc=0.3834 / dir_acc=0.3592가 좋은지 나쁜지는 이 기준선 없이는 말할 수 없다."""
import os, sys, json, sqlite3
sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
from config.settings import RAW_DATA_DB, HORIZON_THRESHOLDS
from learning.batch_retrainer import _path_conditioned_label, PATH_LABEL_RATIO_BY_HZ
from config.constants import DIRECTION_FLAT

con = sqlite3.connect(RAW_DATA_DB)
rf = pd.read_sql("SELECT ts FROM raw_features ORDER BY ts", con)
rc = pd.read_sql("SELECT ts, close FROM raw_candles ORDER BY ts", con)
con.close()
if len(rf) > 30000:
    rf = rf.iloc[-30000:].reset_index(drop=True)
close_map = dict(zip(rc["ts"], rc["close"].astype(float)))
ts_all = rf["ts"].values
print("표본 %d | %s ~ %s" % (len(ts_all), ts_all[0], ts_all[-1]))
print()
print("%-5s %8s %8s %8s %8s | %-22s %-24s" % (
    "hz", "UP", "FLAT", "DOWN", "n", "최빈클래스 예측 acc3", "3클래스 균등추측 acc3"))
for hz, h in [("1m",1),("3m",3),("5m",5),("15m",15)]:
    y = np.array([_path_conditioned_label(close_map, t, h,
                  HORIZON_THRESHOLDS.get(hz,0.0003),
                  path_ratio=PATH_LABEL_RATIO_BY_HZ.get(hz,0.55)) for t in ts_all], dtype=int)
    fut = pd.to_datetime(ts_all) + pd.to_timedelta(h, unit="m")
    hasf = np.array([t.strftime("%Y-%m-%d %H:%M:%S") in close_map for t in fut])
    y = y[hasf]; n = len(y)
    up = (y==1).sum(); fl = (y==DIRECTION_FLAT).sum(); dn = (y==-1).sum()
    maj = max(up,fl,dn)/float(n)
    # 실제가 non-FLAT인 표본만 대상으로 한 '방향' 무정보 기준선
    nf = n - fl
    dir_coin = (max(up,dn)/float(nf)) if nf else float("nan")
    print("%-5s %7.1f%% %7.1f%% %7.1f%% %8d | %20.4f %22.4f" % (
        hz, 100.0*up/n, 100.0*fl/n, 100.0*dn/n, n, maj, 1.0/3))
    print("      └ 실제 non-FLAT %d건 중 UP/DOWN 최빈 비율(방향 동전던지기 상한) = %.4f"
          % (nf, dir_coin))
