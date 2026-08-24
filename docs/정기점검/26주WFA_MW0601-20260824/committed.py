# -*- coding: utf-8 -*-
"""L3 해석 보강 — 모델이 '방향을 냈을 때'의 적중률(committed direction accuracy).

`validate_feature_set_purged_cv.py`의 dir_acc는 실제가 non-FLAT인 표본만 필터링하고
모델이 FLAT을 예측한 것도 오답으로 센다(스크립트 자체가 그 한계를 고지). 라이브 진입은
모델이 방향을 냈을 때만 일어나므로, 그 조건부 정확도를 따로 재야 비교가 성립한다.
"""
import os, sys, json, sqlite3
sys.path.insert(0, r"C:\Users\82108\PycharmProjects\futures")
sys.stdout.reconfigure(encoding="utf-8")
import joblib, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit
from config.settings import RAW_DATA_DB, HORIZON_DIR, HORIZON_THRESHOLDS
from learning.batch_retrainer import (_path_conditioned_label, PATH_LABEL_RATIO_BY_HZ,
                                      HIST_GBM_PARAMS, _make_sample_weight)
from model.multi_horizon_model import apply_robust_preprocess
from config.constants import DIRECTION_FLAT

con = sqlite3.connect(RAW_DATA_DB)
rf = pd.read_sql("SELECT ts, features FROM raw_features ORDER BY ts", con)
rc = pd.read_sql("SELECT ts, close FROM raw_candles ORDER BY ts", con)
con.close()
rf = rf.iloc[-30000:].reset_index(drop=True)
feat = pd.DataFrame([json.loads(s) for s in rf["features"]])
feat.index = rf["ts"].values
feat = feat.apply(pd.to_numeric, errors="coerce").fillna(0.0)
close_map = dict(zip(rc["ts"], rc["close"].astype(float)))
master = [c for c in joblib.load(os.path.join(HORIZON_DIR, "feature_names.pkl")) if c in feat.columns]

print("표본 %d | %s ~ %s" % (len(feat), feat.index.min(), feat.index.max()))
print()
print("%-4s %8s %8s %9s %10s %10s %12s %9s" % ("hz","FLAT예측","방향예측n","적중률","UP재현율","DOWN재현율","균형정확도","다수클래스"))
for hz, h in [("1m",1),("3m",3),("5m",5),("15m",15)]:
    ts_all = feat.index.values
    y = np.array([_path_conditioned_label(close_map, t, h, HORIZON_THRESHOLDS.get(hz,0.0003),
                  path_ratio=PATH_LABEL_RATIO_BY_HZ.get(hz,0.55)) for t in ts_all], dtype=int)
    fut = pd.to_datetime(ts_all) + pd.to_timedelta(h, unit="m")
    hasf = np.array([t.strftime("%Y-%m-%d %H:%M:%S") in close_map for t in fut])
    y = y[hasf]; fh = feat.loc[hasf]
    X = apply_robust_preprocess(fh[master].to_numpy(dtype=np.float64), master)
    names = [n for n in joblib.load(os.path.join(HORIZON_DIR, "feature_names_%s.pkl" % hz)) if n in master]
    ci = [master.index(n) for n in names]
    P, Y = [], []
    for tr, te in TimeSeriesSplit(n_splits=3).split(X):
        tr = tr[(tr + h) < te[0]]
        if len(tr) < 200 or len(np.unique(y[tr])) < 2: continue
        m = HistGradientBoostingClassifier(**HIST_GBM_PARAMS)
        m.fit(X[tr][:, ci], y[tr], sample_weight=_make_sample_weight(y[tr], hz))
        P.append(m.predict(X[te][:, ci])); Y.append(y[te])
    p = np.concatenate(P); yy = np.concatenate(Y)
    flat_rate = float((p == DIRECTION_FLAT).mean())
    com = p != DIRECTION_FLAT
    # 방향예측 적중률: 모델이 방향을 낸 표본에서, 실제 방향과 부호 일치 (실제 FLAT은 제외)
    both = com & (yy != DIRECTION_FLAT)
    acc_com = float((p[both] == yy[both]).mean()) if both.sum() else float("nan")
    _yb = yy[both]; _pb = p[both]
    base_maj = max((_yb==1).mean(), (_yb==-1).mean()) if both.sum() else float("nan")
    pred_up = float((_pb==1).mean()) if both.sum() else float("nan")
    true_up = float((_yb==1).mean()) if both.sum() else float("nan")
    old = p[yy != DIRECTION_FLAT] == yy[yy != DIRECTION_FLAT]
    up_m = _yb == 1; dn_m = _yb == -1
    rec_up = float((_pb[up_m] == 1).mean()) if up_m.sum() else float("nan")
    rec_dn = float((_pb[dn_m] == -1).mean()) if dn_m.sum() else float("nan")
    bal = 0.5 * (rec_up + rec_dn)
    print("%-4s %7.1f%% %8d %8.4f %9.4f %10.4f %11.4f %9.4f" % (
        hz, 100*flat_rate, int(both.sum()), acc_com, rec_up, rec_dn, bal, base_maj))
