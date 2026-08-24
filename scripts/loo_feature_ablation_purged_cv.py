# -*- coding: utf-8 -*-
"""[26주 WFA 재검증 보조] 현행 배포 피처셋 leave-one-out ablation — purged walk-forward CV.

배경: `validate_feature_set_purged_cv.py`(L3)는 OLD(배포 pkl) vs NEW(horizon_feature_sets.json)를
비교하는데, 2026-08-24 재검증 시점에 두 집합이 **전 호라이즌 동일**해져 판별력이 0이 됐다
(변화량 +0.0000%p × 4). "현행 피처셋이 여전히 최적 근방인가"라는 26주 WFA 질문에 답하려면
비교 대상이 필요하므로, 각 피처를 하나씩 뺀 셋을 기준셋과 비교한다.

읽기 전용: raw_data.db만 읽는다. 모델·DB·설정 어디에도 쓰지 않는다.
방법론·전처리·레이블·purge는 전부 L3(`validate_feature_set_purged_cv.py`)와 동일 —
새 방법론을 발명하지 않는다. 바뀐 것은 비교 대상 집합뿐이다.

⚠ 한계: 3폴드 단발이라 폴드별 편차가 크다. Δ가 폴드 표준편차보다 작으면 무의미로 읽을 것.
⚠ advisory — 어떤 산출도 ADD/DROP 효력이 없다(피처_발굴_표준절차 §6).

🔴 **실행 환경: `py310_64` 전용** (191차 OOM 결정). `py37_32` 로 돌리지 말 것 —
   numpy float32 배열 OOM 이 재발한다. `<conda>/envs/py310_64/python.exe` 로 실행한다
   (PC마다 경로가 다르므로 **하드코딩 금지**).
🔴 **EOD 체인에 연결돼 있지 않다** — 사람이 명시적으로 돌리는 오프라인 분석이다
   (절대원칙 6 「알파 리서치 봇 자동 통합 금지」와 무관: 자동 큐·자동 통합이 아니다).
   자동 스케줄에 붙이는 것은 **코드 변경**이며 별건으로 논의할 것.

[MW0602 491차 F-3] 이 파일과 `docs/미륵이고도화3/26주WFA_20260824/` 산출물은
**보존만** 한다. 결과를 26주 WFA 판정으로 채택할지는 **주간회의 소관**이며,
⚠ 사후 데이터로 기준을 움직이지 않는다(313차 4).
"""
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from scripts.validate_feature_set_purged_cv import (  # noqa: E402
    load_data, build_labels, purge_train_tail, HORIZONS_MIN,
)
from config.settings import HORIZON_DIR  # noqa: E402
from learning.batch_retrainer import HIST_GBM_PARAMS, _make_sample_weight  # noqa: E402
from model.multi_horizon_model import apply_robust_preprocess  # noqa: E402
from config.constants import DIRECTION_FLAT  # noqa: E402


def eval_set(X_full, y, col_idx, hz, h_min):
    tscv = TimeSeriesSplit(n_splits=3)
    accs, dirs = [], []
    for train_idx, test_idx in tscv.split(X_full):
        train_idx_p, _ = purge_train_tail(train_idx, test_idx, h_min)
        if len(train_idx_p) < 200 or len(np.unique(y[train_idx_p])) < 2:
            continue
        m = HistGradientBoostingClassifier(**HIST_GBM_PARAMS)
        m.fit(X_full[train_idx_p][:, col_idx], y[train_idx_p],
              sample_weight=_make_sample_weight(y[train_idx_p], hz))
        pred = m.predict(X_full[test_idx][:, col_idx])
        y_val = y[test_idx]
        accs.append(float((pred == y_val).mean()))
        nf = y_val != DIRECTION_FLAT
        if nf.sum() > 0:
            dirs.append(float((pred[nf] == y_val[nf]).mean()))
    return accs, dirs


def main():
    feat, close_map = load_data()
    master = [c for c in joblib.load(os.path.join(HORIZON_DIR, "feature_names.pkl"))
              if c in feat.columns]
    print("표본 %d | 기간 %s ~ %s | 마스터 %d" % (len(feat), feat.index.min(), feat.index.max(), len(master)))
    out = {}
    for hz, h_min in HORIZONS_MIN.items():
        ts_all = feat.index.values
        y = build_labels(ts_all, close_map, hz, h_min)
        fut = pd.to_datetime(ts_all) + pd.to_timedelta(h_min, unit="m")
        keep = np.array([t.strftime("%Y-%m-%d %H:%M:%S") in close_map for t in fut])
        y = y[keep]
        X_full = apply_robust_preprocess(feat.loc[keep][master].to_numpy(dtype=np.float64), master)

        names = [n for n in joblib.load(os.path.join(HORIZON_DIR, "feature_names_%s.pkl" % hz))
                 if n in master]
        base_idx = [master.index(n) for n in names]
        b_acc, b_dir = eval_set(X_full, y, base_idx, hz, h_min)
        bA, bD = float(np.mean(b_acc)), float(np.mean(b_dir))
        sdD = float(np.std(b_dir))
        print()
        print("=" * 96)
        print("호라이즌 %s (h=%d분) | 피처 %d개 | 기준셋 acc=%.4f dir=%.4f (폴드 dir sd=%.4f)"
              % (hz, h_min, len(names), bA, bD, sdD))
        print("=" * 96)
        print("  %-30s %9s %9s %9s %9s" % ("제외 피처", "acc", "Δacc", "dir", "Δdir"))
        rows = []
        for n in names:
            idx = [master.index(x) for x in names if x != n]
            a, d = eval_set(X_full, y, idx, hz, h_min)
            aM, dM = float(np.mean(a)), float(np.mean(d))
            rows.append((n, aM, aM - bA, dM, dM - bD))
        for n, aM, da, dM, dd in sorted(rows, key=lambda r: r[4]):
            mark = ""
            if dd > sdD:
                mark = "  ← 제외가 유리(Δ>폴드sd)"
            elif dd < -sdD:
                mark = "  ← 기여 확인(Δ<-폴드sd)"
            print("  %-30s %9.4f %+9.4f %9.4f %+9.4f%s" % (n, aM, da, dM, dd, mark))
        out[hz] = {"base_acc": bA, "base_dir": bD, "fold_dir_sd": sdD,
                   "loo": [{"drop": n, "acc": a, "d_acc": da, "dir": d, "d_dir": dd}
                           for n, a, da, d, dd in rows]}
    p = os.path.join(_PROJECT_ROOT, "docs", "미륵이고도화3", "26주WFA_20260824", "L3b_loo_ablation.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print()
    print("JSON:", p)
    print("※ advisory — Δdir이 폴드 sd보다 작으면 무의미. ADD/DROP 효력 없음(표준절차 §6).")


if __name__ == "__main__":
    main()
