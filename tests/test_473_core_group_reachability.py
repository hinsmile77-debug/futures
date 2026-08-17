# -*- coding: utf-8 -*-
"""[MW0601 473차 / D9] CORE 호라이즌 그룹의 **도달 가능성** 불변식.

무엇을 발견했나 (2026-08-17)
----------------------------
`CLAUDE.md` 절대원칙 §3은 CORE 피처를 호라이즌 그룹 3개로 나눈다 —
단기(1m·3m·5m) / 중기(10m·15m) / 장기(30m). 체크리스트가
`entry_horizon` 인자로 그룹을 고른다.

그런데 그 `entry_horizon`을 만드는 `model/ensemble_decision.py:select_entry_horizon()`은
경계가 셋(`ENTRY_HORIZON_LOW_BLOCK` / `_B1` / `_B2`)뿐이라
**`1m` · `3m` · `5m` · `None` 밖에 반환하지 못한다**(함수 docstring도 그렇게 적고 있다).

    ∴ 중기·장기 그룹은 **구조적으로 도달 불가**다. 표본이 없어서가 아니다.

`CLAUDE.md` 458차 항목은 *"장기 그룹 체크리스트가 발동한 적이 없다 …
`trades.entry_horizon`은 1m/3m/5m뿐"* 이라고 **현상**은 정확히 적었지만 원인을
표본 부재로 읽었다. 실제 원인은 코드 구조이고, 중기 그룹도 같은 상태라는 것은
어디에도 적혀 있지 않았다. 471차 F-1(15:10 강제청산 1차 경로가 구조적 도달 불가)과
같은 유형이며, 6개월간 어떤 계측에도 걸리지 않은 것까지 같다.

실측 (2026-08-17, `trades` 전량):
    entry_horizon = 3m 92 · 5m 74 · 1m 15 · NULL 132 · '' 5
    10m · 15m · 30m = **0건**
그리고 하필 앙상블 가중이 가장 큰 두 호라이즌이 10m(0.29)·15m(0.28)로,
**합쳐서 57%**가 CORE 게이팅이 한 번도 돌지 않는 그룹에 속한다.

이 파일이 하는 일
-----------------
**이 상태를 "정상"이라고 주장하지 않는다.** 처분(D9)은 주간회의 안건이고
`CLAUDE.md` 절대원칙 개정은 사용자 결정이다. 여기서는 현재 상태를 **명시적으로
고정**해, 라우터나 그룹 정의가 바뀌면 테스트가 깨져 문서 갱신을 강제한다.

- 라우터에 4번째 분기가 생기면 → `test_router_reachable_set_is_declared` 실패
- 새 CORE 그룹이 추가되면 → `test_every_group_is_either_reachable_or_declared` 실패

둘 다 "고쳐야 할 버그"가 아니라 **"CLAUDE.md §3과 이 파일을 함께 갱신하라"** 는
신호다. 그렇게 하지 않으면 도달 불가 그룹이 또 조용히 늘어난다.

실행:
    pytest tests/test_473_core_group_reachability.py
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

from config.settings import CORE_FEATURES_BY_GROUP, HORIZON_CORE_GROUP  # noqa: E402
from model.ensemble_decision import select_entry_horizon  # noqa: E402

#: 2026-08-17 실측으로 확정한 라우터 치역. 여기가 바뀌면 §3 서술도 바뀌어야 한다.
_DECLARED_REACHABLE_HORIZONS = {"1m", "3m", "5m"}

#: 도달 불가로 **확인된** 그룹. 빈 집합이 아니라는 것 자체가 미해결 안건이다(D9).
_DECLARED_UNREACHABLE_GROUPS = {"mid", "long"}


def _reachable_horizons():
    """라우터가 실제로 낼 수 있는 값 전체 — feasibility를 넓게 훑어 수집한다."""
    seen = set()
    v = 0.0
    while v <= 200.0:                     # 실측 max feasibility 대비 충분히 넓게
        h = select_entry_horizon(v, 1.0)
        if h is not None:
            seen.add(h)
        v += 0.01
    return seen


def test_router_reachable_set_is_declared():
    """라우터 치역이 선언과 같은가.

    실패하면 라우터에 분기가 늘거나 줄었다는 뜻이다. 그 자체는 좋은 변화일 수
    있으나(D9 C안), CLAUDE.md §3의 그룹 표와 이 파일을 함께 고쳐야 한다.
    """
    got = _reachable_horizons()
    assert got == _DECLARED_REACHABLE_HORIZONS, (
        "select_entry_horizon 치역이 바뀌었다: %s (선언: %s). "
        "CLAUDE.md 절대원칙 §3의 CORE 그룹 표와 이 테스트를 함께 갱신할 것."
        % (sorted(got), sorted(_DECLARED_REACHABLE_HORIZONS)))


def test_every_group_is_either_reachable_or_declared():
    """모든 CORE 그룹은 '도달 가능'이거나 '도달 불가로 선언됨' 둘 중 하나여야 한다.

    새 그룹을 추가하면서 라우터를 안 고치면 여기서 걸린다 — 조용히 죽은 그룹이
    하나 더 생기는 것을 막는다.
    """
    reachable_groups = {HORIZON_CORE_GROUP.get(h) for h in _reachable_horizons()}
    reachable_groups.discard(None)
    all_groups = set(CORE_FEATURES_BY_GROUP)

    undeclared = all_groups - reachable_groups - _DECLARED_UNREACHABLE_GROUPS
    assert not undeclared, (
        "도달 가능하지도, 도달 불가로 선언되지도 않은 CORE 그룹: %s" % sorted(undeclared))

    # 반대 방향 — 도달 불가로 선언해 뒀는데 실제로는 도달 가능해진 경우.
    resolved = _DECLARED_UNREACHABLE_GROUPS & reachable_groups
    assert not resolved, (
        "도달 불가로 선언된 그룹이 이제 도달 가능하다: %s — "
        "D9가 해소된 것이므로 이 파일과 CLAUDE.md §3을 갱신할 것." % sorted(resolved))


def test_unreachable_groups_are_still_unreachable():
    """중기·장기가 여전히 도달 불가인지 — D9 안건이 살아 있음을 확인한다.

    ⚠ 이 테스트가 **통과하는 것은 좋은 상태가 아니다.** 통과 = 문제가 그대로라는
      뜻이다. 해소되면 위 `test_every_group_is_either_reachable_or_declared`가
      먼저 실패해 갱신을 요구한다.
    """
    reachable = _reachable_horizons()
    for hz, grp in HORIZON_CORE_GROUP.items():
        if grp in _DECLARED_UNREACHABLE_GROUPS:
            assert hz not in reachable, (
                "%s(%s 그룹)가 도달 가능해졌다 — 선언 갱신 필요" % (hz, grp))


def test_long_group_core_feature_is_not_in_the_model():
    """장기 CORE(`opt_chain_pcr`)가 학습 슈퍼셋에 없다 — 이중 사문화의 두 번째 축.

    도달 불가(체크리스트가 안 돈다)와 별개로, 그 피처는 registry에도 없어서
    모델이 쓸 수조차 없다. D9 판단에 두 사실이 모두 필요하다.
    """
    import json
    cfg = CORE_FEATURES_BY_GROUP.get("long") or {}
    core = cfg.get("opt")
    if not core:
        import pytest
        pytest.skip("장기 그룹에 opt CORE가 지정돼 있지 않음 — D9가 처분된 상태")

    reg_path = os.path.join(_ROOT, "data", "db", "shap_feature_registry.json")
    if not os.path.exists(reg_path):
        import pytest
        pytest.skip("registry 없음 — 이 PC에서는 검증 불가")
    with open(reg_path, encoding="utf-8") as f:
        active = set(json.load(f).get("active_features") or [])

    assert core not in active, (
        "'%s'가 active_features에 편입됐다 — 30m CORE의 '모델에 들어간 적 없다'는 "
        "서술이 더 이상 사실이 아니다. CLAUDE.md §3과 D9 안건을 갱신할 것." % core)
