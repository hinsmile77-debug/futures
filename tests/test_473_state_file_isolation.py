# -*- coding: utf-8 -*-
"""[MW0601 473차] 테스트가 프로덕션 상태 파일에 쓰지 못하게 하는 불변식.

무엇을 지키는가
---------------
**부작용 있는 계측 함수를 테스트가 부를 때, 그 부작용이 실제 데이터에 닿지 않는다.**

왜 필요한가 (실제 사고, 2026-08-17 발견)
----------------------------------------
`features/horizon_feature_registry.py:_chronic_suffix()`는 호출될 때마다
`data/feature_exclusion_state.json`에 **쓴다** — 458차 P2-C가 "이 피처가 며칠째
학습에서 빠져 있는가"(만성도)를 재려고 만든 누적 상태 파일이다.

`tests/test_457_daily_fixes.py`가 `get_available_feature_set("30m", desired[:2])`로
**가짜 missing 목록**을 만들어 로그 절단(C6)을 검증하는데, 경로를 격리하지 않아
그 가짜 목록이 실제 파일에 기록됐다. 실측된 오염:

    30m: 16종 — 그중 11종이 97 슈퍼셋에 **이미 들어 있는** 피처
         (above_vwap · atr_ratio · macro_vix · opt_pcr_bearish · in_value_area …)
         = 정의상 need_add일 수 없다. first_seen이 전부 테스트 실행일.

그리고 같은 함수의 "다시 가용해진 피처는 상태에서 제거"(`:76-78`)가 가짜 목록에
없는 이름을 통째로 지워, **진짜 30m 만성 기록(opt_chain_pcr, 2026-07-15 기산)이
소실**됐다. 오염이 아니라 **삭제**다. 458차가 만든 계측이 그 시점부터 무의미해졌고,
그동안 아무도 몰랐다 — 파일이 gitignore 대상이라 diff에도 안 잡힌다.

이 파일이 깨지면 그 사고가 재발한 것이다.

무엇을 덮고 무엇을 안 덮나
--------------------------
- 덮는다: pytest 실행 중 `_CHRONIC_PATH`가 실제 `data/` 경로가 아님(conftest
  autouse 격리가 살아 있음), 그리고 `_chronic_suffix()` 호출이 실제 파일을
  만들지 않음.
- 안 덮는다: `python tests/x.py` 직접 실행 경로(conftest가 로드되지 않는다).
  그 경로로 도는 테스트가 이 함수를 건드리게 되면 그 파일에서 직접 patch할 것.

실행:
    pytest tests/test_473_state_file_isolation.py
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

import features.horizon_feature_registry as reg  # noqa: E402

#: 보호 대상 — 프로덕션 만성도 상태 파일의 실제 경로.
_REAL_PATH = os.path.normpath(os.path.join(
    _ROOT, "data", "feature_exclusion_state.json",
))


def test_chronic_path_is_isolated_under_pytest():
    """conftest autouse 격리가 살아 있는가 — 이 테스트가 이 파일의 핵심이다."""
    assert os.path.normpath(reg._CHRONIC_PATH) != _REAL_PATH, (
        "테스트 실행 중 _CHRONIC_PATH가 프로덕션 경로를 가리킨다 — "
        "conftest의 _isolate_feature_exclusion_state 격리가 죽었다. "
        "이 상태로 get_available_feature_set()을 부르는 테스트가 하나라도 있으면 "
        "458차 만성도 계측이 조용히 삭제된다."
    )


def test_chronic_suffix_does_not_touch_real_file():
    """부작용의 종착지가 실제 파일이 아님을 직접 확인한다.

    경로 비교(위 테스트)는 "가리키지 않는다"까지만 보장한다. 여기서는 실제로
    써 보고 프로덕션 파일이 생기지 않는지 본다 — 458차 사고의 재현 경로 그대로.
    """
    existed_before = os.path.exists(_REAL_PATH)
    mtime_before = os.path.getmtime(_REAL_PATH) if existed_before else None

    # 457차 C6 테스트가 하던 것과 같은 모양의 "가짜 missing" 호출.
    reg._chronic_suffix("30m", ["__fake_feature_for_test__"])

    if not existed_before:
        assert not os.path.exists(_REAL_PATH), (
            "테스트가 프로덕션 만성도 파일을 새로 만들었다: %s" % _REAL_PATH)
    else:
        assert os.path.getmtime(_REAL_PATH) == mtime_before, (
            "테스트가 프로덕션 만성도 파일을 수정했다: %s" % _REAL_PATH)


def test_featurereg_helper_is_covered_by_isolation():
    """오염을 실제로 일으킨 진입점(`get_available_feature_set`)도 안전한가.

    `_chronic_suffix`를 직접 부르는 것과 달리, 이쪽은 457차 테스트가 쓰던
    실제 경로다. 격리가 이 경로까지 덮는지 확인한다.
    """
    desired = reg.get_feature_set("30m")
    if not desired or len(desired) < 4:
        import pytest
        pytest.skip("30m 레지스트리 미구성 — 이 PC에서는 검증 불가")

    existed_before = os.path.exists(_REAL_PATH)
    mtime_before = os.path.getmtime(_REAL_PATH) if existed_before else None

    reg.get_available_feature_set("30m", list(desired[:2]))

    if not existed_before:
        assert not os.path.exists(_REAL_PATH)
    else:
        assert os.path.getmtime(_REAL_PATH) == mtime_before


def test_no_test_module_writes_state_files_unguarded():
    """소스 스캔 — 부작용 함수를 부르면서 격리하지 않는 테스트를 찾아낸다.

    conftest autouse가 pytest 경로를 덮지만, `python tests/x.py` 직접 실행
    경로는 못 덮는다(conftest 미로드). 직접 실행이 가능한 파일
    (`if __name__ == "__main__"`)이 부작용 함수를 부르면 자기 파일에서
    patch해야 한다 — 그 누락을 여기서 잡는다.
    """
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    offenders = []
    for name in sorted(os.listdir(tests_dir)):
        if not name.startswith("test_") or not name.endswith(".py"):
            continue
        if name == os.path.basename(__file__):
            continue
        path = os.path.join(tests_dir, name)
        try:
            with open(path, encoding="utf-8") as f:
                src = f.read()
        except (IOError, OSError, UnicodeDecodeError):
            continue
        calls_side_effect = (
            "get_available_feature_set(" in src or "_chronic_suffix(" in src
        )
        if not calls_side_effect:
            continue
        runs_standalone = '__name__ == "__main__"' in src
        patches_path = "_CHRONIC_PATH" in src
        if runs_standalone and not patches_path:
            offenders.append(name)

    assert not offenders, (
        "직접 실행 가능한 테스트가 만성도 상태 파일 경로를 격리하지 않고 "
        "부작용 함수를 부른다(conftest는 pytest 경로만 덮는다): %s" % offenders
    )
