"""[MW0601 600차 / F-10·F-11] 보정기 영속화 이식 + 로그 출처 식별 회귀 가드.

두 가지를 고정한다.

**F-10 (이식)** — `dev` 브랜치 `2356820`([MW0602] 485차)의 영속화 복구를 v9-dev 로
가져왔다. 다만 원 커밋은 payload 에 `clean_probs`/`clean_labels`/`artifact_n`
(MW0602 461차 산물) 3키도 실었는데 **이 브랜치에는 그 속성이 없어** 이식에서 뺐다.
그것이 다시 섞여 들어오면 저장 시 `AttributeError` 로 죽으므로 여기서 막는다.

**F-11 (로그 출처)** — `learning/calibration.py` 의 `logger` 는 모듈 단위라
앙상블·호라이즌 6개·극단성 보정기가 `[Calibration]` 하나를 공유했다. 그래서
2026-09-17 딥다이브가 축퇴 전이 1,591회를 앙상블 보정기 **단독인 것처럼** 집계하는
오류를 냈다(그날 리포트 제2부-E §7 자체 정정). 이제 인스턴스마다 접두가 붙는다.

⚠ 두 변경 모두 **판정·보정 동작을 바꾸지 않는다.** 그 불변식도 여기서 고정한다.

근거: `docs/정기점검/매일점검/MW0601-20260917-점검리포트.md` 제2부-D·E.
"""

from utils.dll_bootstrap import ensure_conda_dll_path   # 448차
ensure_conda_dll_path()

import inspect
import io
import logging
import os
import random
import tempfile

import pytest

from learning import calibration as CAL
from learning.calibration import PredictionCalibrator, MultiHorizonCalibrator


def _trained(name="", n=140, seed=0):
    """MIN_SAMPLES 를 넘겨 fit 된 보정기 하나."""
    c = PredictionCalibrator(name=name)
    rnd = random.Random(seed)
    for _ in range(n):
        c.record(rnd.uniform(0.25, 0.75), rnd.random() < 0.33)
    return c


def _trained_informative(name="", n=160, seed=3):
    """축퇴 가드에 걸리지 않을 만큼 **순위 정보가 있는** 보정기.

    `_trained()` 는 난수라 raw↔적중이 무관해 auc≈0.5 → 축퇴로 강등된다. 그건 가드의
    정상 동작이므로, "강등이 없을 때"를 봐야 하는 테스트에서는 이쪽을 쓴다.
    """
    c = PredictionCalibrator(name=name)
    rnd = random.Random(seed)
    for _ in range(n):
        raw = rnd.uniform(0.20, 0.80)
        c.record(raw, rnd.random() < raw)      # 높은 raw 일수록 실제로 자주 맞는다
    return c


def _capture(cal):
    """그 인스턴스가 실제로 뱉는 렌더링된 메시지를 모은다.

    ⚠ `caplog` 를 쓰지 않는다 — 이 프로젝트 로거는 루트로 전파되지 않아 빈 목록이
    돌아오고, 그러면 **항상 통과하는 가짜 테스트**가 된다(599차에서 실제로 겪었다).
    """
    msgs = []

    class _Grab(logging.Handler):
        def emit(self, record):
            msgs.append(record.getMessage())

    h = _Grab()
    h.setLevel(logging.DEBUG)
    prev = CAL.logger.level
    CAL.logger.setLevel(logging.DEBUG)
    CAL.logger.addHandler(h)
    try:
        yield_msgs = msgs
        cal.fit()                      # 축퇴/해소 계열 로그를 유발
    finally:
        CAL.logger.removeHandler(h)
        CAL.logger.setLevel(prev)
    return yield_msgs


# ── F-10. 영속화 ─────────────────────────────────────────────────────

def test_save_succeeds_while_degenerate():
    """🔴 이식의 핵심 — 마감 시각에 축퇴여도 그날 표본을 저장한다.

    종전(`if not _SKLEARN_OK or not self._fitted`)에는 `False` 를 **조용히** 돌려줘
    2026-08-13~09-17 35일간 아티팩트가 얼어붙었다.
    """
    c = _trained()
    c._fitted = False                  # 마감 시각 축퇴 상태 재현
    p = os.path.join(tempfile.mkdtemp(), "c.pkl")
    assert c.save(p) is True, "축퇴 상태에서 저장이 건너뛰어졌다 — F-10 미적용"
    assert os.path.exists(p)


def test_save_still_refuses_when_never_fitted():
    """한 번도 fit 된 적 없어 모델 자체가 없으면 종전대로 저장하지 않는다."""
    c = PredictionCalibrator()
    c._model = None
    assert c.save(os.path.join(tempfile.mkdtemp(), "c.pkl")) is False


def test_load_restores_degenerate_state_not_true():
    """축퇴로 저장된 보정기가 다음 기동에 fitted 로 되살아나지 않는다(원 커밋 1-7)."""
    c = _trained()
    c._fitted, c._degenerate = False, True
    p = os.path.join(tempfile.mkdtemp(), "c.pkl")
    assert c.save(p)
    d = PredictionCalibrator()
    assert d.load(p) is True
    assert d.is_fitted is False, "축퇴 저장본이 fitted=True 로 부활했다"
    assert d.is_degenerate is True
    assert d.n_samples == c.n_samples, "표본 수가 유실됐다"


def test_legacy_artifact_without_state_keys_defaults_to_fitted():
    """구버전 저장본(3키 없음)은 fitted=True 폴백 — 종전 동작 보존.

    ⚠ `_trained()`(난수)로는 검증되지 않는다 — load() 직후의 축퇴 재평가가 fitted 를
    **내리기** 때문이다(그건 가드의 정상 동작이며 이식 코드 주석이 명시한 계약이다).
    폴백 자체를 보려면 강등되지 않을 표본이 필요하다.
    """
    import joblib
    c = _trained_informative()
    assert c.is_degenerate is False, "표본이 축퇴라 이 테스트의 전제가 성립하지 않는다"
    p = os.path.join(tempfile.mkdtemp(), "legacy.pkl")
    joblib.dump({"model": c._model, "probs": list(c._probs),
                 "labels": list(c._labels), "n": c._n, "method": c.method},
                p, protocol=4)
    d = PredictionCalibrator()
    assert d.load(p) is True
    assert d.is_fitted is True


def test_payload_has_no_dev_only_keys():
    """🔴 `dev` 전용 461차 키가 섞여 들어오면 저장이 AttributeError 로 죽는다.

    이 브랜치에는 `_clean_probs`/`_clean_labels`/`_artifact_n` 속성이 **없다**.
    원 커밋을 다시 체리픽할 때 이 테스트가 재발을 막는다.
    """
    # 주석은 제외한다 — 왜 뺐는지를 주석으로 남기는 것은 권장 사항이고,
    # 금지하려는 것은 **코드가 그 키를 저장하는 것**이다.
    _lines = inspect.getsource(PredictionCalibrator.save).splitlines()
    src = "\n".join(ln.split("#", 1)[0] for ln in _lines)
    for k in ("clean_probs", "clean_labels", "artifact_n"):
        assert k not in src, (
            "save() 가 이 브랜치에 없는 속성 %r 을 저장하려 한다 — "
            "dev 2356820 이식 시 제외해야 하는 키다" % k
        )
    for attr in ("_clean_probs", "_clean_labels", "_artifact_n"):
        assert not hasattr(PredictionCalibrator(), attr), attr


def test_main_logs_both_branches_of_save():
    """저장 실패가 **조용하지 않은지** — 부정 분기 무로그 금지(원 커밋 핵심)."""
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
    src = io.open(p, encoding="utf-8", errors="replace").read()
    i = src.find("앙상블 보정기 저장 — 다음 기동")
    assert i > 0
    blk = src[i:i + 1600]
    assert "저장 완료" in blk
    assert "저장 건너뜀" in blk, (
        "save() 가 False 를 돌려줄 때 아무 로그도 남지 않는다 — "
        "이것이 35일 동결을 숨긴 결함이다"
    )


# ── F-11. 로그 출처 식별 ─────────────────────────────────────────────

def test_named_instance_prefixes_logs():
    c = _trained(name="ensemble")
    msgs = _capture(c)
    tagged = [m for m in msgs if m.startswith("[Calibration:ensemble]")]
    assert tagged, "이름을 줬는데 접두가 안 붙었다 — 잡은 로그: %r" % msgs[:3]


def test_unnamed_instance_is_byte_identical_to_before():
    """이름이 없으면 종전과 **완전히 같은** 문자열이어야 한다(하위호환)."""
    c = _trained(name="")
    msgs = _capture(c)
    assert msgs, "로그가 아예 없다 — 캡처 헬퍼를 의심하라"
    for m in msgs:
        assert not m.startswith("[Calibration:"), "이름 없는 인스턴스에 접두가 붙었다: %r" % m


def test_capture_helper_actually_captures():
    """헬퍼가 정말 잡는지 먼저 확인한다 — 안 잡히면 위 두 테스트가 위증이 된다."""
    assert _capture(_trained(name="probe")), "핸들러가 아무것도 못 잡았다"


def test_multihorizon_names_each_calibrator():
    m = MultiHorizonCalibrator(["1m", "3m", "5m"])
    assert {h: c.name for h, c in m.calibrators.items()} == {
        "1m": "1m", "3m": "3m", "5m": "5m"
    }


def test_ensemble_calibrator_is_named():
    """앙상블 보정기가 이름을 받는지 — 이것이 F-11 의 실사용 목적이다."""
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "model", "ensemble_decision.py")
    src = io.open(p, encoding="utf-8", errors="replace").read()
    i = src.find("self.ensemble_calibrator = PredictionCalibrator(")
    assert i > 0
    assert 'name="ensemble"' in src[i:i + 300], "앙상블 보정기에 name 이 안 붙었다"


def test_no_bare_logger_left_in_calibrator_class():
    """클래스 본문에 `logger.` 직접 호출이 남으면 그 줄만 접두가 빠진다."""
    src = inspect.getsource(PredictionCalibrator)
    bare = [ln.strip() for ln in src.split("\n")
            if "logger." in ln and "self._log." not in ln and not ln.strip().startswith("#")]
    assert not bare, "접두가 빠지는 로그 호출이 남아 있다: %r" % bare[:3]


# ── 불변식: 동작은 바뀌지 않는다 ─────────────────────────────────────

def test_naming_does_not_change_calibration_output():
    """같은 입력이면 이름 유무와 무관하게 보정 출력이 동일하다."""
    a, b = _trained(name="", seed=7), _trained(name="ensemble", seed=7)
    for raw in (0.20, 0.33, 0.45, 0.60, 0.85):
        assert abs(a.calibrate(raw) - b.calibrate(raw)) < 1e-12, raw
    assert a.is_fitted == b.is_fitted
    assert a.is_degenerate == b.is_degenerate


def test_degeneracy_thresholds_untouched():
    """600차가 축퇴 임계를 건드리지 않았음을 고정 — 그쪽은 매매 정책(주간회의)이다."""
    assert PredictionCalibrator.DEGENERATE_AUC_MIN == 0.53
    assert PredictionCalibrator.DEGENERATE_SPAN_MIN == 0.02
    assert PredictionCalibrator.WINDOW == 200
    assert PredictionCalibrator.MIN_SAMPLES == 80
