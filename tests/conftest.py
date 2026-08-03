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

# 저장소 루트를 sys.path에 넣어 `utils.*` import를 보장한다.
# pytest는 `__init__.py`가 없는 테스트 디렉터리를 basedir(= tests/)로 잡아
# sys.path[0]에 넣으므로, 실행 위치에 따라 루트가 빠질 수 있다.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()
