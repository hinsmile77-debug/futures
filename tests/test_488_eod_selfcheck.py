# -*- coding: utf-8 -*-
"""[MW0602 488차 계획 C / 476차 G-1] EOD 재학습 자체 사후검증 불변식.

무엇을 막는가
-------------
EOD 재학습이 완료 마커를 찍으면, 다음날 08:55 PreRetrain 이 그것을 근거로
"모델이 현행"이라 믿고 보수 사이즈 제한(×0.6)을 푼다. 그런데 0819 P1-1 에서
사이드카 `label_scheme` 이 `null` 로 기록되는 결함이 있었고 **다음날 장전에야**
드러났다 — 그 사이 하루치 노출이 잘못된 전제 위에 있었다.

방금 저장한 사이드카를 되읽어 같은 판정식으로 확인하면 **당일 15:45 에** 안다.

이 파일이 고정하는 불변식
------------------------
① `wants_from_settings()` 가 세 레이블 체계(fixed / rolling_sigma / atr)를 정확히 뽑는다
② `main.py` 어댑터와 `retrain_eod.py` SelfCheck 가 **같은 헬퍼**를 쓴다(복제 금지)
③ 정상 사이드카 6개 → ok=True / 1개 오염 → ok=False / 전부 부재 → ok=False
④ 🔴 **SelfCheck 는 재학습을 실패로 만들지 않는다** — 예외가 나도 마커는 찍힌다
⑤ 마커 파일에 `selfcheck_label_state:` 줄이 남는다

실행:
    python tests/test_488_eod_selfcheck.py
"""
import io
import json
import os
import re
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from learning.model_meta import read_label_state, wants_from_settings

HZ = ["1m", "3m", "5m", "10m", "15m", "30m"]


class _FakeSettings(object):
    """`config.settings` 의 필요한 속성만 흉내낸다 — 임포트 부작용 없이 순수 검증."""

    def __init__(self, fixed=True, rolling=True):
        self.USE_FIXED_LABEL_THRESHOLD = fixed
        self.USE_ROLLING_SIGMA_THRESHOLD = rolling
        self.HORIZON_THRESHOLDS = dict((h, 0.0005) for h in HZ)
        self.SIGMA_K_PER_HORIZON = dict((h, 1.25) for h in HZ)
        self.SIGMA_K = 1.0
        self.HORIZONS = dict((h, i) for i, h in enumerate(HZ))


def _write_sidecars(d, scheme="fixed", param=0.0005, bad=None):
    """호라이즌 6개의 사이드카를 만든다. `bad` 로 한 개만 오염시킨다."""
    for h in HZ:
        meta = {"label_scheme": scheme, "label_param": param}
        if bad and h == bad[0]:
            meta.update(bad[1])
        io.open(os.path.join(d, "gbm_%s_meta.json" % h), "w", encoding="utf-8").write(
            json.dumps(meta))


def test_wants_from_settings_three_schemes():
    """① 세 레이블 체계를 정확히 뽑는다."""
    scheme, param_of = wants_from_settings(_FakeSettings(fixed=True))
    assert scheme == "fixed", scheme
    assert abs(param_of("3m") - 0.0005) < 1e-12, param_of("3m")

    scheme, param_of = wants_from_settings(_FakeSettings(fixed=False, rolling=True))
    assert scheme == "rolling_sigma", scheme
    assert abs(param_of("3m") - 1.25) < 1e-12, param_of("3m")

    scheme, param_of = wants_from_settings(_FakeSettings(fixed=False, rolling=False))
    assert scheme == "atr", scheme
    assert param_of("3m") is None, "atr 은 파라미터를 비교하지 않는다"


def test_single_source_of_truth():
    """② `main.py` 도 `retrain_eod.py` 도 **같은 헬퍼**를 쓴다 — 복제 금지.

    복제하면 레이블 체계를 바꿀 때 한쪽만 고쳐져 조용히 갈라지고, 그때 SelfCheck 는
    "이상 없음"을 계속 찍으면서 실제로는 다른 기준을 본다.
    """
    for rel in ("main.py", "retrain_eod.py"):
        src = io.open(os.path.join(_ROOT, rel), encoding="utf-8", errors="replace").read()
        assert "wants_from_settings" in src, "%s 가 헬퍼를 안 쓴다" % rel
        # 기대치 구성 로직이 되살아나지 않았는지 — `USE_FIXED_LABEL_THRESHOLD` 를
        # 직접 읽어 want_scheme 을 만드는 코드가 남아 있으면 복제가 부활한 것이다.
        assert 'want_scheme = "fixed" if' not in src.replace("_want_scheme", "want_scheme"), (
            "%s 에 기대치 구성 로직이 복제돼 있다" % rel)


def test_healthy_sidecars_pass():
    """③-a 정상 6개 → ok=True."""
    s = _FakeSettings()
    with tempfile.TemporaryDirectory() as d:
        _write_sidecars(d)
        scheme, param_of = wants_from_settings(s)
        ok, detail = read_label_state(d, HZ, scheme, param_of)
        assert ok is True, detail
        assert "6/6" in detail, detail


def test_one_null_label_scheme_fails():
    """③-b 한 개만 `label_scheme=null` → ok=False.

    0819 P1-1 이 정확히 이 형태였다. 476차 F-3 이 진단 문구를 분리해뒀으므로
    "구버전"이 아니라 **기록경로 결함**으로 읽혀야 한다.
    """
    s = _FakeSettings()
    with tempfile.TemporaryDirectory() as d:
        _write_sidecars(d, bad=("5m", {"label_scheme": None}))
        scheme, param_of = wants_from_settings(s)
        ok, detail = read_label_state(d, HZ, scheme, param_of)
        assert ok is False, detail
        assert "기록경로 결함" in detail, detail


def test_missing_sidecars_fail_closed():
    """③-c 전부 부재 → ok=False. **모르면 False다**(모른다를 괜찮다로 바꾸지 않는다)."""
    s = _FakeSettings()
    with tempfile.TemporaryDirectory() as d:
        scheme, param_of = wants_from_settings(s)
        ok, detail = read_label_state(d, HZ, scheme, param_of)
        assert ok is False, detail


def test_selfcheck_is_non_fatal_and_recorded():
    """④⑤ 🔴 SelfCheck 는 재학습을 실패로 만들지 않고, 결과는 마커에 남는다.

    소스를 정적으로 확인한다 — `retrain_eod.py` 는 py310_64 전용이고 DB·모델을
    요구해 테스트에서 실행할 수 없다(191차 OOM 결정 때문에 py37 로 돌리면 안 된다).
    """
    src = io.open(os.path.join(_ROOT, "retrain_eod.py"),
                  encoding="utf-8", errors="replace").read()
    block = src[src.index("EOD 재학습 자체 사후검증"):src.index("완료 마커 저장")]

    # 예외를 삼킨다 — 검사 실패가 재학습 실패가 되면 안 된다
    assert "except Exception as _sc_e:" in block, "SelfCheck 가 예외를 안 삼킨다"
    # ERROR 를 쓰지 않는다 — 이 프로젝트는 ERROR 를 거의 안 남긴다(점검 함정 ④)
    assert "log.error" not in block, "SelfCheck 가 ERROR 를 쓴다 — WARNING 이어야 한다"
    assert "log.warning" in block, "부정 분기에 로그가 없다(무로그 금지)"
    # 조용히 넘어가지 않는다 — 성공/실패/수행실패 셋 다 로그가 있다
    assert "log.info" in block, "성공 분기 로그가 없다"
    # 마커에 결과가 남는다
    assert "selfcheck_label_state" in block, "마커에 SelfCheck 결과가 안 남는다"
    # 마커 기록이 SelfCheck **뒤**에 온다(마커가 먼저 찍히면 관측 의미가 준다)
    assert src.index("_sc_line = \"unknown\"") < src.index("완료 마커 기록"), (
        "SelfCheck 가 마커 기록 뒤로 갔다")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _fails = 0
    for _name, _fn in sorted(globals().items()):
        if not _name.startswith("test_") or not callable(_fn):
            continue
        try:
            _fn()
            print("PASS %s" % _name)
        except AssertionError as _e:
            _fails += 1
            print("FAIL %s\n  %s" % (_name, _e))
    print("-" * 60)
    print("%s (%d fail)" % ("ALL PASS" if not _fails else "FAILED", _fails))
    sys.exit(1 if _fails else 0)
