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

# ⚠ `import pytest` 는 489차 D9(만성도 격리 fixture 제거)로 미사용이 되어 뺐다.
#   fixture 를 다시 넣을 때 함께 되살릴 것.

# 저장소 루트를 sys.path에 넣어 `utils.*` import를 보장한다.
# pytest는 `__init__.py`가 없는 테스트 디렉터리를 basedir(= tests/)로 잡아
# sys.path[0]에 넣으므로, 실행 위치에 따라 루트가 빠질 수 있다.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()


# ── [MW0602 489차 / 0823 주간회의 D9] 만성도 상태 파일 격리 — **제거됨** ────
#
# 473차(MW0601)가 여기에 autouse 격리를 두었다. 이유는 진짜였다: 458차 P2-C가
# 만든 `features/horizon_feature_registry.py:_chronic_suffix()`가 호출될 때마다
# `data/feature_exclusion_state.json`에 쓰고, `tests/test_457_daily_fixes.py`가
# 가짜 missing 목록으로 그 함수를 불러 **진짜 30m 만성 기록(opt_chain_pcr,
# 2026-07-15 기산)을 삭제**했다(2026-08-17 실측).
#
# 🔴 **그런데 그 생산부가 이 브랜치에 없다.** `dev`의 `horizon_feature_registry.py`
#    는 178차 이후 무변경이고 `chronic` 문자열이 한 번도 등장하지 않는다.
#    격리 대상이 없는 격리였다. 게다가 `raising=False` 때문에 monkeypatch가
#    **없는 속성을 만들어 주어**, 지킬 것이 없는데도 초록불이 켜졌다 —
#    488차 후속2가 잡아낸 *"지킨다고 믿는 초록불"* 과 같은 형태다.
#
# 0823 주간회의 D9는 (A) 생산부 이관 / (B) 소비부 제거 중 **(B)** 를 택했고,
# 이 fixture 와 `tests/test_473_state_file_isolation.py` 를 **함께** 지웠다.
# 한쪽만 지우면 다음 이관 때 같은 함정이 다시 생긴다.
#
# 🔴 **458차 만성도 계측을 이 브랜치로 이관하는 사람에게 —**
#    이 격리를 **반드시 함께 되살릴 것.** 되살릴 코드는 git 이력에 있다:
#        git show HEAD~1:tests/conftest.py
#        git show HEAD~1:tests/test_473_state_file_isolation.py
#    복원 조건은 `.claude/skills/mireuk-daily-check/references/invariants.md`
#    §0-C 에도 등재돼 있다. 근거: `dev_memory/DECISION_LOG.md` 489차 D9.
