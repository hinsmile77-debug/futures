# -*- coding: utf-8 -*-
"""호라이즌별 피처셋(OLD=배포 pkl vs NEW=horizon_feature_sets.json) — Purged Walk-Forward CV.

읽기 전용: raw_data.db만 읽는다. 모델 파일·DB·설정 어디에도 쓰지 않는다.
py310_64 환경에서 실행 권장: python scripts/validate_feature_set_purged_cv.py

배경: `learning/batch_retrainer.py`의 프로덕션 CV(TimeSeriesSplit n_splits=3)는 purge/embargo가
없어, 호라이즌 레이블(N분 후 가격 기반)이 검증 폴드 경계 근처 학습 표본에 룩어헤드 정보를
유출할 수 있다(AFML ch.7). "purged 워크포워드 통과 확인"은 275차·311차 후속4가 요구하는
원칙인데 이를 실제로 재는 자동 도구가 없었음 — 이 스크립트가 그 최초 구현.
(무스킬_피처셋_딥다이브_보고서_2026-07-13.md §8 / dev_memory/DECISION_LOG.md 331차)

프로덕션과 최대한 동일하게 재현:
  - 레이블: learning.batch_retrainer._path_conditioned_label (고정 임계값 HORIZON_THRESHOLDS
    + PATH_LABEL_RATIO_BY_HZ, 실제 프로덕션 라벨링 함수 그대로 재사용)
  - 전처리: model.multi_horizon_model.apply_robust_preprocess (log1p/clip 동일)
  - 모델: HistGradientBoostingClassifier(**HIST_GBM_PARAMS), sample_weight도 동일 함수 재사용
  - CV 골격: sklearn.TimeSeriesSplit(n_splits=3) — 프로덕션과 동일 분할

프로덕션과 다른 점(이 스크립트가 추가한 것):
  - PURGE: 각 폴드 학습셋 꼬리에서, 레이블 산정 구간이 검증 구간 시작점과 겹치는 표본 제거
    (h_min분 룩어헤드 레이블이 검증 구간 정보를 학습에 유출하는 것을 차단).
    embargo는 이 분할 구조(train이 test보다 항상 앞섬)에서는 불필요 — 반대 방향 유출 경로가 없음.
  - 두 지표 병행 보고: (a) 3클래스 정확도(cv_acc, 프로덕션 지표와 동일 정의)
                       (b) 방향적중률(실제 UP/DOWN인 표본만 대상, 딥다이브 보고서와 유사 정의 —
                          단 "모델도 non-FLAT을 예측했는가"는 보지 않고 "실제가 non-FLAT인가"만
                          필터링하므로 라이브 conf-층화 방향적중률과 완전히 같은 정의는 아님)

한계(정직하게 고지):
  - 3폴드 단발 실행 — 폴드별 편차가 커서(예: 특정 구간이 유독 저성능) 평균값만으로 결론짓지
    말고 fold별 수치도 함께 볼 것.
  - 피처 자체의 lookback(예: bb_position/hurst가 과거 N봉을 쓰는 것)에서 오는 유출은 다루지
    않음 — 그건 폴드 경계 워밍업 구간 오염이라 별도 문제. 여기서는 "레이블 룩어헤드"만
    purge한다(AFML이 강조하는 핵심 유출 경로).
  - 이 결과가 좋아도 라이브 성능을 보장하지 않음 — 최종 판단은 실제 재학습 + 모의투자
    라이브 관찰까지 거쳐야 함.
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

from config.settings import HORIZON_THRESHOLDS, RAW_DATA_DB, MODEL_DIR, HORIZON_DIR  # noqa: E402
from learning.batch_retrainer import (  # noqa: E402
    _path_conditioned_label, PATH_LABEL_RATIO_BY_HZ, HIST_GBM_PARAMS, _make_sample_weight,
)
from model.multi_horizon_model import apply_robust_preprocess  # noqa: E402
from features.horizon_feature_registry import get_available_feature_set  # noqa: E402
from config.constants import DIRECTION_FLAT  # noqa: E402

HORIZONS_MIN = {"1m": 1, "3m": 3, "5m": 5, "15m": 15}
MAX_ROWS = 30000  # 런타임 방어 (프로덕션 MAX_TRAIN_BARS=50000의 축소판)


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
    close_map = dict(zip(rc["ts"], rc["close"].astype(float)))
    return feat, close_map


def build_labels(ts_list, close_map, hz, h_min):
    thresh = HORIZON_THRESHOLDS.get(hz, 0.0003)
    ratio = PATH_LABEL_RATIO_BY_HZ.get(hz, 0.55)
    y = np.array(
        [_path_conditioned_label(close_map, ts, h_min, thresh, path_ratio=ratio) for ts in ts_list],
        dtype=int,
    )
    return y


def purge_train_tail(train_idx, test_idx, h_min):
    """학습 폴드 꼬리에서 레이블 룩어헤드가 검증 구간과 겹치는 표본 제거.

    train_idx는 test_idx보다 전부 작다(TimeSeriesSplit 보장). 학습 표본 i의 레이블은
    [i, i+h_min] 구간 가격을 사용하므로, i+h_min >= test_idx[0] 이면 검증 구간 정보가
    이미 그 학습 레이블에 스며든 것 — 그런 표본을 제거한다.
    """
    test_start = test_idx[0]
    keep = train_idx[(train_idx + h_min) < test_start]
    n_purged = len(train_idx) - len(keep)
    return keep, n_purged


def run_horizon(hz, h_min, feat, close_map, master_cols):
    ts_all = feat.index.values
    y = build_labels(ts_all, close_map, hz, h_min)

    # 미래 가격 없는 꼬리(레이블 FLAT으로 인위 고정된 것) 제거 — 프로덕션과 동일 취급
    future_ts = pd.to_datetime(ts_all) + pd.to_timedelta(h_min, unit="m")
    has_future = np.array([t.strftime("%Y-%m-%d %H:%M:%S") in close_map for t in future_ts])
    ts_all = ts_all[has_future]
    y = y[has_future]
    feat_h = feat.loc[has_future]

    old_pkl_path = os.path.join(HORIZON_DIR, "feature_names_%s.pkl" % hz)
    old_names = list(joblib.load(old_pkl_path))
    old_names = [n for n in old_names if n in feat_h.columns]

    new_names = get_available_feature_set(hz, master_cols) or []
    new_names = [n for n in new_names if n in feat_h.columns]

    results = {}
    for label_tag, names in (("OLD(현재 배포)", old_names), ("NEW(개편안)", new_names)):
        X_full = feat_h[master_cols].to_numpy(dtype=np.float64)
        X_full = apply_robust_preprocess(X_full, master_cols)
        col_idx = [master_cols.index(n) for n in names]

        tscv = TimeSeriesSplit(n_splits=3)
        accs, dir_accs, purged_counts = [], [], []
        for train_idx, test_idx in tscv.split(X_full):
            train_idx_p, n_purged = purge_train_tail(train_idx, test_idx, h_min)
            purged_counts.append(n_purged)
            if len(train_idx_p) < 200 or len(np.unique(y[train_idx_p])) < 2:
                continue
            X_tr = X_full[train_idx_p][:, col_idx]
            X_val = X_full[test_idx][:, col_idx]
            y_tr, y_val = y[train_idx_p], y[test_idx]

            model = HistGradientBoostingClassifier(**HIST_GBM_PARAMS)
            model.fit(X_tr, y_tr, sample_weight=_make_sample_weight(y_tr, hz))
            pred = model.predict(X_val)

            accs.append(float((pred == y_val).mean()))

            nonflat = y_val != DIRECTION_FLAT
            dir_accs.append(float((pred[nonflat] == y_val[nonflat]).mean()) if nonflat.sum() > 0 else None)

        results[label_tag] = {
            "n_features": len(names),
            "features": names,
            "cv_acc_3class": float(np.mean(accs)) if accs else None,
            "acc_per_fold": accs,
            "dir_acc_nonflat": (
                float(np.mean([d for d in dir_accs if d is not None]))
                if any(d is not None for d in dir_accs) else None
            ),
            "dir_acc_per_fold": dir_accs,
            "n_folds_used": len(accs),
            "purged_per_fold": purged_counts,
        }
    return results, len(ts_all)


def main():
    feat, close_map = load_data()
    master_cols = list(joblib.load(os.path.join(HORIZON_DIR, "feature_names.pkl")))
    master_cols = [c for c in master_cols if c in feat.columns]
    print("표본 수(전체):", len(feat), "| 기간:", feat.index.min(), "~", feat.index.max())
    print("마스터 피처(교집합):", len(master_cols))
    print()

    for hz, h_min in HORIZONS_MIN.items():
        print("=" * 70)
        print("호라이즌 %s (h=%d분)" % (hz, h_min))
        results, n = run_horizon(hz, h_min, feat, close_map, master_cols)
        print("유효표본(미래가격 있는 것):", n)
        for tag, r in results.items():
            print("  [%s] n_feat=%d folds=%d purged/fold=%s" % (
                tag, r["n_features"], r["n_folds_used"], r["purged_per_fold"]))
            print("      3클래스 acc = %s | fold별=%s" % (
                "%.4f" % r["cv_acc_3class"] if r["cv_acc_3class"] is not None else "N/A",
                ["%.3f" % a for a in r["acc_per_fold"]]))
            print("      방향적중률(non-FLAT) = %s | fold별=%s" % (
                "%.4f" % r["dir_acc_nonflat"] if r["dir_acc_nonflat"] is not None else "N/A",
                ["%.3f" % d if d is not None else "N/A" for d in r["dir_acc_per_fold"]]))
        old_dir = results["OLD(현재 배포)"]["dir_acc_nonflat"]
        new_dir = results["NEW(개편안)"]["dir_acc_nonflat"]
        if old_dir is not None and new_dir is not None:
            print("  → 방향적중률 변화: %+.4f (%.2f%%p)" % (new_dir - old_dir, (new_dir - old_dir) * 100))
        print()


if __name__ == "__main__":
    main()
