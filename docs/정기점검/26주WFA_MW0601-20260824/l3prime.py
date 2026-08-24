# -*- coding: utf-8 -*-
"""L3' — 현행 배포 피처셋의 leave-one-out 한계기여도 (purged walk-forward CV, 읽기전용).

`feature_ablation_purged_cv.py`의 하드코딩 후보리스트(331/373차 시점) 대신 **현재 배포된
pkl 그대로**를 기준선으로 삼고 피처를 하나씩 빼서 방향적중률 변화를 잰다.
26주 WFA 질문("현행 피처셋이 여전히 최적 근방인가")에 직접 답하는 형태.

⚠ `feature_ablation_purged_cv.eval_feature_set`은 sample_weight를 "3m"으로 고정하므로
그대로 쓰지 않고, 호라이즌별 가중을 올바로 넘기는 동등 구현을 여기 둔다.
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

MAX_ROWS = 30000
HZ = {"1m": 1, "3m": 3, "5m": 5}


def load_data():
    con = sqlite3.connect(RAW_DATA_DB)
    rf = pd.read_sql("SELECT ts, features FROM raw_features ORDER BY ts", con)
    rc = pd.read_sql("SELECT ts, close FROM raw_candles ORDER BY ts", con)
    con.close()
    if len(rf) > MAX_ROWS:
        rf = rf.iloc[-MAX_ROWS:].reset_index(drop=True)
    feat = pd.DataFrame([json.loads(s) for s in rf["features"]])
    feat.index = rf["ts"].values
    feat = feat.apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return feat, dict(zip(rc["ts"], rc["close"].astype(float)))


def evaluate(names, X_full, master_cols, y, h_min, hz):
    col_idx = [master_cols.index(n) for n in names]
    accs3, dirs = [], []
    for tr, te in TimeSeriesSplit(n_splits=3).split(X_full):
        tr = tr[(tr + h_min) < te[0]]                      # PURGE
        if len(tr) < 200 or len(np.unique(y[tr])) < 2:
            continue
        m = HistGradientBoostingClassifier(**HIST_GBM_PARAMS)
        m.fit(X_full[tr][:, col_idx], y[tr], sample_weight=_make_sample_weight(y[tr], hz))
        pred = m.predict(X_full[te][:, col_idx])
        accs3.append(float((pred == y[te]).mean()))
        nf = y[te] != DIRECTION_FLAT
        dirs.append(float((pred[nf] == y[te][nf]).mean()) if nf.sum() else None)
    v = [d for d in dirs if d is not None]
    return (float(np.mean(accs3)) if accs3 else None,
            float(np.mean(v)) if v else None, accs3, dirs)


def main():
    feat, close_map = load_data()
    master = [c for c in joblib.load(os.path.join(HORIZON_DIR, "feature_names.pkl")) if c in feat.columns]
    print("표본 %d행 | %s ~ %s | 마스터피처 %d" % (len(feat), feat.index.min(), feat.index.max(), len(master)))
    for hz, h_min in HZ.items():
        ts_all = feat.index.values
        y = np.array([_path_conditioned_label(close_map, t, h_min,
                                              HORIZON_THRESHOLDS.get(hz, 0.0003),
                                              path_ratio=PATH_LABEL_RATIO_BY_HZ.get(hz, 0.55))
                      for t in ts_all], dtype=int)
        fut = pd.to_datetime(ts_all) + pd.to_timedelta(h_min, unit="m")
        hasf = np.array([t.strftime("%Y-%m-%d %H:%M:%S") in close_map for t in fut])
        yh, fh = y[hasf], feat.loc[hasf]
        X = apply_robust_preprocess(fh[master].to_numpy(dtype=np.float64), master)
        base = [n for n in joblib.load(os.path.join(HORIZON_DIR, "feature_names_%s.pkl" % hz)) if n in master]
        print("\n" + "=" * 78)
        print("호라이즌 %s (h=%d) — 유효표본 %d · 기준선 피처 %d개" % (hz, h_min, hasf.sum(), len(base)))
        print("=" * 78)
        a3, ad, f3, fd = evaluate(base, X, master, yh, h_min, hz)
        print("  %-34s acc3=%.4f dir=%.4f fold_dir=%s" % ("BASE(현행 배포)", a3, ad, ["%.3f" % d for d in fd]))
        rows = []
        for drop in base:
            sub = [n for n in base if n != drop]
            if len(sub) < 2:
                continue
            a3b, adb, _, fdb = evaluate(sub, X, master, yh, h_min, hz)
            rows.append((drop, adb, adb - ad, a3b - a3, fdb))
        rows.sort(key=lambda r: -r[2])          # 뺐을 때 좋아지는 순
        print("  --- leave-one-out (Δ>0 = 그 피처를 빼면 방향적중률이 올라간다 = 역기여) ---")
        for nm, adb, d_dir, d_acc, fdb in rows:
            flag = "  ← 역기여" if d_dir > 0.005 else ""
            print("  −%-33s dir=%.4f  Δdir=%+.4f (%+.2f%%p)  Δacc3=%+.4f%s"
                  % (nm, adb, d_dir, d_dir * 100, d_acc, flag))


if __name__ == "__main__":
    main()
