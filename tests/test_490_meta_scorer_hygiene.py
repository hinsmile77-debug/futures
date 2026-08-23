# -*- coding: utf-8 -*-
"""[MW0602 490차] 메타라벨 스코어러 학습 위생(P0) + 재개 게이트(P1) 불변식.

무엇을 지키는가
---------------
489차 후속 딥다이브가 찾은 결함 3종과, 그것을 고친 뒤에도 **[2]에 재투자하지 않는다**는
사전등록 관문이 조용히 되돌려지지 않게 한다.

⚠ **매매 경로 무관** — 스코어러는 섀도다(`strategy/entry/meta_gate.py:105` "로깅 전용").
  이 파일이 깨져도 라이브 매매는 영향받지 않는다. 다만 **계측이 되돌아간 것**이므로
  고치기 전에 왜 바뀌었는지부터 확인할 것.
"""
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

from config.settings import (  # noqa: E402
    META_SCORER_TRAINING,
    VALIDATION_CAMPAIGN,
    HORIZONS,
)

np = pytest.importorskip("numpy")


# ──────────────────────────────────────────────────────────────────────────
# P0 — 학습 위생 사전등록
# ──────────────────────────────────────────────────────────────────────────
def test_p0_training_hygiene_preregistered():
    cfg = META_SCORER_TRAINING
    assert cfg["enabled"] is True
    # ① 결측을 0.0이 아니라 NaN으로 — "없던 날"과 "값이 0인 날"을 구분한다
    assert cfg["nan_fill"] is True
    # ② 스키마 = 마지막 거래일 키 교집합 (최다 키 행 → 폐기 피처 영구 고착 문제)
    assert cfg["schema_rule"] == "last_day_intersection"
    # ③ HGB는 트리라 스케일 불변 + NaN과 만나면 해가 된다
    assert cfg["use_scaler"] is False
    assert cfg["purged_cv"] is True


def test_p0_schema_rule_is_last_day_intersection():
    """`_resolve_schema()`가 '최다 키 행'으로 되돌아가지 않았는지 직접 확인한다.

    되돌아가면 451차가 폐기한 피처가 다시 배포 모델에 고착된다.
    """
    from learning.meta_label_classifier import _resolve_schema
    recs = [
        # 과거 행 — 키가 더 많다(폐기 예정 피처 포함)
        {"ts": "2026-07-28 09:01:00", "fd": {"a": 1, "b": 2, "dead": 3}},
        {"ts": "2026-07-28 09:02:00", "fd": {"a": 1, "b": 2, "dead": 3}},
        # 마지막 거래일 — 폐기 피처가 빠졌다
        {"ts": "2026-08-21 09:01:00", "fd": {"a": 1, "b": 2}},
        {"ts": "2026-08-21 09:02:00", "fd": {"a": 1, "b": 2}},
    ]
    assert _resolve_schema(recs) == ["a", "b"], "최다 키 행 규칙으로 되돌아갔다"


def test_p0_schema_intersection_is_conservative():
    """마지막 거래일 안에서 한 행이 결손이면 교집합이 줄어야 한다(보수적)."""
    from learning.meta_label_classifier import _resolve_schema
    recs = [
        {"ts": "2026-08-21 09:01:00", "fd": {"a": 1, "b": 2, "c": 3}},
        {"ts": "2026-08-21 09:02:00", "fd": {"a": 1, "b": 2}},          # c 결손
    ]
    assert _resolve_schema(recs) == ["a", "b"]


def test_p0_purged_splits_respect_embargo():
    """엠바고만큼 학습 꼬리가 잘려야 한다 — 라벨이 T→T+h를 보기 때문이다."""
    from learning.meta_label_classifier import _purged_splits
    n, embargo = 400, 30
    folds = list(_purged_splits(n, 3, embargo))
    assert folds, "폴드가 생성되지 않았다"
    for tr, va in folds:
        assert len(tr) and len(va)
        # 학습 마지막 인덱스와 검증 첫 인덱스 사이에 최소 embargo 간격
        assert va[0] - tr[-1] >= embargo, "엠바고 간격이 지켜지지 않았다"
        assert tr[-1] < va[0], "학습이 검증 구간을 침범했다"


def test_p0_purged_splits_embargo_zero_is_contiguous():
    """embargo=0이면 종전(TimeSeriesSplit)과 같은 인접 분할이어야 한다."""
    from learning.meta_label_classifier import _purged_splits
    folds = list(_purged_splits(400, 3, 0))
    assert folds
    for tr, va in folds:
        assert va[0] == tr[-1] + 1


def test_p0_embargo_is_horizon_minutes():
    """엠바고 상수를 새로 만들지 않고 `HORIZONS`(호라이즌 분 수)에서 가져오는가."""
    src = open(os.path.join(_ROOT, "learning", "meta_label_classifier.py"),
               encoding="utf-8").read()
    assert "HORIZONS.get(hz, 1)" in src, "엠바고가 HORIZONS에서 파생되지 않는다"
    assert set(HORIZONS) >= {"1m", "30m"}


# ──────────────────────────────────────────────────────────────────────────
# P0 — 서빙 정합 (학습/서빙 결측 처리가 같아야 한다)
# ──────────────────────────────────────────────────────────────────────────
def test_p0_serving_missing_fill_matches_training():
    """학습이 NaN으로 채웠으면 서빙도 NaN이어야 한다.

    서빙만 0.0으로 채우면 모델이 "값이 0인 관측"으로 오해한다(학습/서빙 괴리).
    """
    src = open(os.path.join(_ROOT, "learning", "meta_label_classifier.py"),
               encoding="utf-8").read()
    assert 'float(features.get(f, 0.0) or 0.0)' not in src, \
        "서빙이 여전히 0.0으로 채운다 — 학습(NaN)과 어긋난다"
    assert '_miss = np.nan if bool(_TRAIN_CFG.get("nan_fill"' in src


def test_p0_scaler_is_optional_with_backward_compat():
    """스케일러는 선택이되, **사이드카가 없으면 종전 동작(요구)** 이어야 한다.

    재학습 전 구 모델의 서빙이 조용히 달라지면 안 된다.
    """
    from learning.meta_label_classifier import EntryQualityScorer
    sc = EntryQualityScorer(model_dir=os.path.join(_ROOT, "__no_such_dir__"))
    # 사이드카를 못 읽는 상황 → True(종전 동작) 폴백
    assert sc._scaled_flag("1m") in (True, False)
    src = open(os.path.join(_ROOT, "learning", "meta_label_classifier.py"),
               encoding="utf-8").read()
    assert "return True" in src.split("def _scaled_flag")[1].split("def ")[0], \
        "사이드카 부재 시 폴백이 종전 동작(True)이 아니다"


def test_p0_py37_compatible_no_walrus():
    """이 모듈은 **py37_32 런타임이 import**한다 — walrus/f-string= 금지.

    문법 오류가 나면 라이브 앱이 뜨지 않는다.
    """
    import ast
    src = open(os.path.join(_ROOT, "learning", "meta_label_classifier.py"),
               encoding="utf-8").read()
    assert ":=" not in src, "walrus 연산자는 py37에서 SyntaxError다"
    ast.parse(src, feature_version=(3, 7))


# ──────────────────────────────────────────────────────────────────────────
# P0 — 사이드카 (AUC 소비 경로)
# ──────────────────────────────────────────────────────────────────────────
def test_p0_metrics_sidecar_readable():
    """AUC가 로그에만 남지 않고 **읽을 수 있는 경로**로 나와야 한다.

    종전에는 매주 EOD 로그에 찍히는데 리포트도 §12도 볼 수 없었다
    (292·303·371·468차와 같은 계열의 사각).
    """
    from learning.meta_label_classifier import load_training_metrics
    m = load_training_metrics()
    if not m:
        pytest.skip("아직 학습 사이드카 없음 — 첫 재학습 전이다")
    assert "latest" in m and "history" in m
    hz = (m["latest"].get("horizons") or {})
    assert hz, "사이드카에 호라이즌 지표가 없다"
    for _h, r in hz.items():
        # 병기 AUC 4종 — 하나라도 빠지면 리포트 [2-A] 표가 비어 보인다
        for k in ("auc_mixed", "auc_directional",
                  "auc_net_directional", "auc_strong_directional"):
            assert k in r, "%s: %s 누락" % (_h, k)


def test_p0_mixed_auc_is_not_the_gate_metric():
    """🔴 혼합 AUC는 FLAT 행이 만드는 착시다 — 게이트가 그걸 쓰면 안 된다."""
    gate = VALIDATION_CAMPAIGN["meta_gate"]["reopen_gate"]
    assert gate["metric"] != "auc_mixed"
    assert gate["metric"] == "auc_net_directional"


# ──────────────────────────────────────────────────────────────────────────
# P1 — 재개 게이트
# ──────────────────────────────────────────────────────────────────────────
def test_p1_reopen_gate_preregistered():
    gate = VALIDATION_CAMPAIGN["meta_gate"]["reopen_gate"]
    assert gate["enabled"] is True
    assert gate["consecutive_weeks"] == 4       # 캠페인 공용 단위
    assert gate["start_date"] == "2026-08-25"


def test_p1_threshold_is_anchored_not_hardcoded():
    """🔴 문턱을 490차 실험 수치에서 역산하지 않았음을 고정한다(313차 ④).

    앵커는 이 채널과 무관하게 이미 존재하던 상수다.
    """
    from learning.calibration import PredictionCalibrator
    gate = VALIDATION_CAMPAIGN["meta_gate"]["reopen_gate"]
    assert gate["threshold_anchor"] == \
        "learning.calibration.PredictionCalibrator.DEGENERATE_AUC_MIN"
    assert hasattr(PredictionCalibrator, "DEGENERATE_AUC_MIN"), "앵커 상수가 사라졌다"
    # 리포터가 하드코딩하지 않고 런타임에 읽는가
    src = open(os.path.join(_ROOT, "scripts",
                            "generate_validation_campaign_report.py"), encoding="utf-8").read()
    seg = src.split("def _meta_reopen_gate")[1].split("\ndef ")[0]
    assert "DEGENERATE_AUC_MIN" in seg and "0.53" not in seg, \
        "문턱이 하드코딩됐다 — 앵커가 바뀌어도 안 움직인다"


def test_p1_gate_uses_worst_horizon():
    """호라이즌 **최솟값**으로 판정해야 한다 — 하나라도 무정보면 통과 불가."""
    src = open(os.path.join(_ROOT, "scripts",
                            "generate_validation_campaign_report.py"), encoding="utf-8").read()
    seg = src.split("def _meta_reopen_gate")[1].split("\ndef ")[0]
    assert "min(vals)" in seg, "최댓값/평균으로 판정하면 약한 호라이즌이 가려진다"


def test_p1_gate_state_is_sane():
    """게이트가 실제로 계산되고, 지금은 열려 있지 않아야 한다.

    순이익 AUC 실측이 0.4955~0.5152(문턱 0.53)이므로 **CLOSED 또는 INSUFFICIENT**가 정상이다.
    ⚠ OPEN이 뜨면 그것은 사건이다 — 자동 적용이 아니라 **주간회의 상정** 신호다.
    """
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import importlib
    mod = importlib.import_module("scripts.generate_validation_campaign_report")
    g = mod._meta_reopen_gate()
    assert g["enabled"] is True
    assert g["state"] in ("CLOSED", "INSUFFICIENT", "OPEN", "UNKNOWN")
    assert g["state"] != "UNKNOWN", "앵커/사이드카 로드가 깨졌다: %s" % g.get("reason")


# ──────────────────────────────────────────────────────────────────────────
# P2 — 섀도 게이지 (판정 미반영)
# ──────────────────────────────────────────────────────────────────────────
def test_p2_strong_label_is_shadow_only():
    """강한추종 AUC는 **관찰값**이다 — 어떤 판정에도 관여하면 안 된다.

    재활용하려면 새 채널 사전등록이 필요하다(주간회의 소관).
    """
    assert META_SCORER_TRAINING["shadow_labels"] is True
    gate = VALIDATION_CAMPAIGN["meta_gate"]["reopen_gate"]
    assert gate["metric"] != "auc_strong_directional", \
        "섀도 게이지가 판정 지표로 승격됐다 — 사전등록 없이는 불가"


def test_p2_meta_gate_verdict_untouched_by_new_metrics():
    """[2] 본채널 합격선은 **무변경**이어야 한다(§9-4 판정기준 사후 변경 금지)."""
    cr = VALIDATION_CAMPAIGN["meta_gate"]
    assert cr["top_ev_min_pt"] == 0.0
    assert cr["sep_cost_mult"] == 2.0
    assert cr["min_per_tercile"] == 30
