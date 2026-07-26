# -*- coding: utf-8 -*-
"""3m/5m 개편(331차/373차) 사후 분해분석 — 어떤 개별 피처가 방향적중률 변화를 유발했는지.

07-13/14 딥다이브 §9-4, 373차/376차 NEXT_TODO가 요청한 "개편 항목을 하나씩 넣고 빼며
분해"를 이제 실행. 07-24 EOD 재학습으로 3m/5m 개편이 이미 라이브 반영된 뒤라(사후검증),
`validate_feature_set_purged_cv.py`의 OLD/NEW 이분법 대신 임의 피처리스트 2개를 직접
비교하는 범용 버전. 읽기 전용, 모델/DB/설정 어디에도 쓰지 않음.
"""
import json
import os
import sqlite3
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from config.settings import RAW_DATA_DB, HORIZON_DIR  # noqa: E402
from learning.batch_retrainer import (  # noqa: E402
    _path_conditioned_label, PATH_LABEL_RATIO_BY_HZ, HIST_GBM_PARAMS, _make_sample_weight,
)
from config.settings import HORIZON_THRESHOLDS  # noqa: E402
from model.multi_horizon_model import apply_robust_preprocess  # noqa: E402
from config.constants import DIRECTION_FLAT  # noqa: E402

MAX_ROWS = 15000

# 3m — OLD(개편 전, 07-13 딥다이브 §3-2 실측 기준) 12개 대비, 5개 신규 편입 각각의 한계기여도.
# BASE_3M = OLD에서 07-13 딥다이브가 무정보로 확인해 제거한 5개(va_bandwidth·is_open_volatile·
# time_sin·time_cos·macro_vix)만 뺀 "공통 7개" — CVD 교체효과(cvd_direction->cvd_delta_norm)는
# 별도 스위치로 분리.
BASE_3M = ["cvd_divergence", "microprice_bias", "poc_above", "ret_15m", "ofi_norm", "macro_us10y_chg"]
CVD_OLD_3M = "cvd_direction"
CVD_NEW_3M = "cvd_delta_norm"
ADD_CANDIDATES_3M = ["poc_distance", "bb_position", "ema_cross", "vwap_position", "microprice_depth_bias"]

# 5m — 373차가 제거를 제안한 4개(va_bandwidth·macro_vix·cvd_monotone_ratio·opt_pcr_slope_norm)를
# 현재 배포(12개, 이미 제거된 상태)에 하나씩 되돌려 넣어 어느 제거가 폴드3 하락의 원인이었는지 확인.
BASE_5M = [
    "bb_position", "ema_cross", "ret_5m", "ret_15m", "poc_distance", "poc_above",
    "vwap_position", "above_vwap", "is_open_volatile", "is_close_volatile",
    "in_value_area", "cvd_slope",
]
REMOVED_CANDIDATES_5M = ["va_bandwidth", "macro_vix", "cvd_monotone_ratio", "opt_pcr_slope_norm"]

HORIZONS_MIN = {"3m": 3, "5m": 5}


def load_data():
    con = sqlite3.connect(RAW_DATA_DB)
    rf = pd.read_sql(
        "SELECT ts, features FROM raw_features ORDER BY ts DESC LIMIT %d" % MAX_ROWS, con
    ).iloc[::-1].reset_index(drop=True)
    rc = pd.read_sql("SELECT ts, close FROM raw_candles ORDER BY ts", con)
    con.close()
    feat = pd.DataFrame([json.loads(s) for s in rf["features"]])
    feat.index = rf["ts"].values
    feat = feat.apply(pd.to_numeric, errors="coerce").fillna(0.0)
    close_map = dict(zip(rc["ts"], rc["close"].astype(float)))
    return feat, close_map


def build_labels(ts_list, close_map, hz, h_min):
    thresh = HORIZON_THRESHOLDS.get(hz, 0.0003)
    ratio = PATH_LABEL_RATIO_BY_HZ.get(hz, 0.55)
    return np.array(
        [_path_conditioned_label(close_map, ts, h_min, thresh, path_ratio=ratio) for ts in ts_list],
        dtype=int,
    )


def purge_train_tail(train_idx, test_idx, h_min):
    test_start = test_idx[0]
    keep = train_idx[(train_idx + h_min) < test_start]
    return keep


def eval_feature_set(names, X_full, master_cols, y, h_min):
    names = [n for n in names if n in master_cols]
    col_idx = [master_cols.index(n) for n in names]
    tscv = TimeSeriesSplit(n_splits=3)
    dir_accs = []
    for train_idx, test_idx in tscv.split(X_full):
        train_idx_p = purge_train_tail(train_idx, test_idx, h_min)
        if len(train_idx_p) < 200 or len(np.unique(y[train_idx_p])) < 2:
            dir_accs.append(None)
            continue
        X_tr = X_full[train_idx_p][:, col_idx]
        X_val = X_full[test_idx][:, col_idx]
        y_tr, y_val = y[train_idx_p], y[test_idx]
        model = HistGradientBoostingClassifier(**HIST_GBM_PARAMS)
        model.fit(X_tr, y_tr, sample_weight=_make_sample_weight(y_tr, "3m"))
        pred = model.predict(X_val)
        nonflat = y_val != DIRECTION_FLAT
        dir_accs.append(float((pred[nonflat] == y_val[nonflat]).mean()) if nonflat.sum() > 0 else None)
    valid = [d for d in dir_accs if d is not None]
    mean_acc = float(np.mean(valid)) if valid else None
    return mean_acc, dir_accs


def run(hz, h_min, feat, close_map, master_cols, variants):
    ts_all = feat.index.values
    y = build_labels(ts_all, close_map, hz, h_min)
    future_ts = pd.to_datetime(ts_all) + pd.to_timedelta(h_min, unit="m")
    has_future = np.array([t.strftime("%Y-%m-%d %H:%M:%S") in close_map for t in future_ts])
    ts_all = ts_all[has_future]
    y = y[has_future]
    feat_h = feat.loc[has_future]
    X_full = feat_h[master_cols].to_numpy(dtype=np.float64)
    X_full = apply_robust_preprocess(X_full, master_cols)

    print("=" * 70)
    print(f"호라이즌 {hz} — 유효표본 {len(ts_all)}")
    baseline_acc = None
    for tag, names in variants:
        mean_acc, per_fold = eval_feature_set(names, X_full, master_cols, y, h_min)
        delta = "" if baseline_acc is None else f"  (Δ={mean_acc - baseline_acc:+.4f}, {(mean_acc - baseline_acc)*100:+.2f}%p)"
        print(f"  [{tag}] n_feat={len(names)} dir_acc={mean_acc:.4f} fold={['%.3f'%d if d else 'NA' for d in per_fold]}{delta}")
        if tag.startswith("BASE"):
            baseline_acc = mean_acc
    print()


def main():
    feat, close_map = load_data()
    master_cols = list(joblib.load(os.path.join(HORIZON_DIR, "feature_names.pkl")))
    master_cols = [c for c in master_cols if c in feat.columns]
    print("표본:", len(feat), feat.index.min(), "~", feat.index.max(), "| 마스터피처:", len(master_cols))
    print()

    # 3m: baseline(공통 7 + cvd_direction) 대비 (a) CVD 교체 단독, (b) 신규 5개 각각 단독 추가
    variants_3m = [("BASE(구7+cvd_direction)", BASE_3M + [CVD_OLD_3M])]
    variants_3m.append(("BASE+CVD swap만(cvd_delta_norm)", BASE_3M + [CVD_NEW_3M]))
    for cand in ADD_CANDIDATES_3M:
        variants_3m.append((f"BASE+cvd_direction+{cand}", BASE_3M + [CVD_OLD_3M, cand]))
    variants_3m.append(("현재 라이브(구7+cvd_delta_norm+5개 전체)", BASE_3M + [CVD_NEW_3M] + ADD_CANDIDATES_3M))
    run("3m", 3, feat, close_map, master_cols, variants_3m)

    # 5m: baseline(현재 라이브 12개) 대비 제거됐던 4개를 하나씩 되돌려 추가
    variants_5m = [("BASE(현재 라이브 12개)", BASE_5M)]
    for cand in REMOVED_CANDIDATES_5M:
        variants_5m.append((f"BASE+{cand}(되돌리기)", BASE_5M + [cand]))
    variants_5m.append(("전체 복원(구16개, 373차 이전)", BASE_5M + REMOVED_CANDIDATES_5M))
    run("5m", 5, feat, close_map, master_cols, variants_5m)


if __name__ == "__main__":
    main()
