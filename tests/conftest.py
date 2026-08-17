# tests/conftest.py — 테스트 실행 격리 부트스트랩
"""[MW0601 422차] pytest 실행 시 프로덕션 부작용을 끄는 진입점.

pytest는 conftest.py를 **테스트 모듈보다 먼저** import한다. 따라서 여기서
환경변수를 세우면 `utils.logger.setup_logging()`이 파일 핸들러를 만들기 전에
테스트 모드가 확정된다(로그 초기화는 첫 `get_logger()` 호출 시 지연 실행이라
import 순서에 의존한다 — 그래서 "먼저"가 중요하다).

경위: 2026-08-03 장전에 `tests/test_circuit_breaker.py`가 5회 실행되며
CRITICAL CB 알림 30건을 프로덕션 로그(`20260803_SYSTEM.log`/`WARN.log`)에
남겼다. 장중 실제 CB 발동은 0건이었다. 상세는 `utils/runtime_mode.py` 참조.

⚠ conftest는 **pytest 경로만** 덮는다. `python tests/test_x.py`로 직접
실행하면 conftest가 로드되지 않으므로, 각 테스트 파일 상단에도 동등한 2줄을
둔다(두 겹 방어). 새 테스트를 추가할 때 그 2줄을 함께 넣을 것.
"""
import os
import sys

import pytest

# 저장소 루트를 sys.path에 넣어 `utils.*` import를 보장한다.
# pytest는 `__init__.py`가 없는 테스트 디렉터리를 basedir(= tests/)로 잡아
# sys.path[0]에 넣으므로, 실행 위치에 따라 루트가 빠질 수 있다.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()


# ── [MW0601 473차] 만성도 상태 파일 격리 ────────────────────────────────────
#
# `features/horizon_feature_registry.py:_chronic_suffix()`는 부작용이 있다 —
# 호출될 때마다 `data/feature_exclusion_state.json`에 **쓴다**. 458차 P2-C가
# "이 피처가 며칠째 학습에서 빠져 있는가"를 재려고 만든 누적 상태 파일이다.
#
# 그런데 `tests/test_457_daily_fixes.py`가 `get_available_feature_set()`을
# 부르면서 그 경로를 격리하지 않아 **실제 파일에 썼다.** 결과(2026-08-17 실측):
#
#   30m: 16종 기록 — 그중 11종이 97 슈퍼셋에 **이미 들어 있는** 피처
#        (above_vwap · atr_ratio · macro_vix · opt_pcr_bearish · in_value_area …)
#        = need_add일 수가 없는 것들. first_seen이 전부 테스트 실행일.
#
# 더 나쁜 것은 `_chronic_suffix()`의 "다시 가용해진 피처는 상태에서 제거"
# 로직(같은 파일 :76-78)이다 — 테스트가 넘긴 가짜 missing 목록에 없는 이름이
# 통째로 지워져 **진짜 30m 만성 기록(opt_chain_pcr, 2026-07-15 기산)이 소실**됐다.
# 즉 계측이 오염된 게 아니라 **삭제**됐다.
#
# 개별 테스트만 고치면 다음 사람이 같은 곳을 밟는다(458차 테스트 4개는 각자
# 올바로 patch하고 있었으므로, 규율이 아니라 구조가 문제다). 그래서 여기서
# 전 테스트를 일괄 격리한다. 자기 경로를 따로 patch하는 테스트는 이 뒤에
# 적용되므로 그쪽이 이긴다(pytest monkeypatch는 역순 복원).
#
# ⚠ conftest는 **pytest 경로만** 덮는다(위 docstring 참조). `python tests/x.py`로
#   직접 실행하는 테스트가 이 함수를 건드리게 되면 그 파일에서 직접 patch할 것.
@pytest.fixture(autouse=True)
def _isolate_feature_exclusion_state(tmp_path, monkeypatch):
    try:
        import features.horizon_feature_registry as _reg
    except Exception:
        return  # 레지스트리를 안 쓰는 환경 — 격리할 대상이 없다
    monkeypatch.setattr(
        _reg, "_CHRONIC_PATH",
        str(tmp_path / "feature_exclusion_state.json"), raising=False,
    )
    monkeypatch.setattr(_reg, "_CHRONIC_CACHE", None, raising=False)
