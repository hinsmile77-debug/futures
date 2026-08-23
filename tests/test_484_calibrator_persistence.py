# -*- coding: utf-8 -*-
"""[MW0602 485차 F-1] 앙상블 보정기 영속화 불변식 4종.

무엇을 발견했나 (2026-08-21, 0821 리포트 1-1)
--------------------------------------------
`PredictionCalibrator.save()`가 "fit 상태일 때만 저장" 게이트를 갖고 있어,
마감 시각에 축퇴/도달불가(_fitted=False) 상태면 **그날 쌓인 누적 표본까지 통째로
버려졌다** — 2026-08-12~21 7거래일 동안 `data/ensemble_calibrator.pkl`이 한 번도
갱신되지 않았고(mtime 08-11 고정), 부정 분기에 로그가 없어 아무도 몰랐다.

짝 결함(1-7): `load()`가 `_fitted = True`를 무조건 세워, 저장 게이트를 풀면
축퇴 상태의 저장본이 다음 기동에 fitted로 되살아날 위험이 있었다.

고친 것 (485차 F-1)
-------------------
- save(): fit 게이트 제거(모델이 존재하면 저장) + payload에 `fitted`/`degenerate`/
  `unreachable` 3키 추가.
- load(): `state.get("fitted", True)` — 구버전 저장본(키 없음)은 True 폴백으로
  종전 동작 보존, 신버전은 저장 시점 상태 그대로 복원.
- main.py daily_close(): save() False 반환 시 WARNING 로그(부정 분기 무로그 금지).

이 파일이 고정하는 불변식 4종
-----------------------------
① _fitted=False(축퇴)여도 save()가 True를 반환하고 파일이 생긴다
② 그 파일을 load()하면 is_fitted가 False다 (축퇴 저장본이 fitted로 부활 금지)
③ 구버전 payload(3키 없음)를 load()하면 is_fitted가 True다 (하위호환)
④ _model이 None(한 번도 생성 안 됨)이면 save()가 False다

실행:
    pytest tests/test_484_calibrator_persistence.py
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

import pytest  # noqa: E402

from learning import calibration  # noqa: E402
from learning.calibration import PredictionCalibrator  # noqa: E402

pytestmark = pytest.mark.skipif(
    not calibration._SKLEARN_OK,
    reason="sklearn 미설치 환경 — save/load 경로 자체가 비활성이라 검증 대상 아님",
)


def _fitted_platt_model():
    """라이브와 동일 설정(C=0.02, lbfgs)으로 fit까지 마친 모델.

    라벨을 균형(0/1 각 2건)으로 줘서 강한 규제 하의 출력이 기저율 ~0.5 근처가
    되게 한다 — out_max(~0.5)가 자동진입 하한(0.33) 위라 load()의 도달불가
    재평가가 fitted를 내리지 않는다(테스트 ③의 전제).
    """
    import numpy as np
    from sklearn.linear_model import LogisticRegression

    m = LogisticRegression(C=0.02, solver="lbfgs")
    m.fit(np.array([0.2, 0.8, 0.3, 0.7]).reshape(-1, 1), np.array([0, 1, 0, 1]))
    return m


def _degenerate_saved_file(tmp_path):
    """축퇴로 fitted가 해제된 보정기를 저장한 파일 경로를 만든다."""
    cal = PredictionCalibrator()
    cal._model = _fitted_platt_model()
    cal._fitted = False          # 축퇴/도달불가로 해제된 마감 시각 상태 재현
    cal._degenerate = True
    path = str(tmp_path / "ensemble_calibrator_degen.pkl")
    return cal, path


def test_1_save_true_even_when_not_fitted(tmp_path):
    """① fit 상태가 아니어도 저장된다 — 누적 표본은 모델 계수와 수명이 다르다."""
    cal, path = _degenerate_saved_file(tmp_path)
    assert cal.save(path) is True
    assert os.path.exists(path)


def test_2_degenerate_savefile_loads_as_not_fitted(tmp_path):
    """② 축퇴 저장본은 fitted로 부활하지 않는다 → calibrate()는 raw 통과로 시작."""
    cal, path = _degenerate_saved_file(tmp_path)
    assert cal.save(path) is True

    cal2 = PredictionCalibrator()
    assert cal2.load(path) is True
    assert cal2.is_fitted is False


def test_3_legacy_payload_defaults_to_fitted(tmp_path):
    """③ 구버전 저장본(상태 3키 없음)은 True 폴백 — 구버전은 fitted일 때만
    저장됐으므로 이것이 종전 동작 보존(하위호환)이다."""
    import joblib

    path = str(tmp_path / "ensemble_calibrator_legacy.pkl")
    joblib.dump(
        {
            "model":  _fitted_platt_model(),
            "probs":  [],
            "labels": [],
            "n":      0,
            "method": "platt",
        },
        path,
        protocol=4,
    )

    cal = PredictionCalibrator()
    assert cal.load(path) is True
    assert cal.is_fitted is True


def test_4_save_false_when_model_never_created(tmp_path):
    """④ 모델 객체 자체가 없으면(_model=None) 종전대로 저장하지 않는다."""
    cal = PredictionCalibrator()
    cal._model = None
    path = str(tmp_path / "ensemble_calibrator_none.pkl")
    assert cal.save(path) is False
    assert not os.path.exists(path)
