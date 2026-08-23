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


def test_long_group_core_feature_stays_a_plain_feature():
    """장기 CORE(`opt_chain_pcr`)는 **일반 피처로 남는다** — CORE 게이트로 승격되지 않는다.

    ↩️ **[2026-08-23 사용자 결정 / MW0602 488차 후속2] 이 테스트의 단언이 뒤집혔다.**

    종전 단언은 `core not in active` 였다 — 473·474차가 "장기 CORE는 이중으로 사문화됐다
    (① 체크리스트 도달 불가 ② 모델 슈퍼셋에도 없음)"고 정리한 상태를 고정한 것이다.
    그런데 `opt_chain_pcr` 가 이후 `active_features` 에 편입되면서 ②가 깨졌고, 테스트는
    *"CLAUDE.md §3과 D9 안건을 갱신할 것"* 이라고 스스로 지시하며 실패해 왔다.

    **사용자 결정(2026-08-23)**: *"30m CORE 는 모델에 들지 않지만 `opt_chain_pcr` 가
    `active_features` 에 편입하고 데이터 수집은 계속하자."*

    → 두 축을 **분리**한다. 이제 지켜야 할 불변식은 이렇다.
      ① **CORE 게이트로는 여전히 안 돈다** — 장기 그룹은 `select_entry_horizon()` 이
         `1m/3m/5m/None` 만 반환하므로 도달 불가다(위 도달성 테스트가 고정).
         `opt_chain_pcr` 미통과가 등급을 떨어뜨리는 일은 일어나지 않는다.
      ② **일반 피처로는 산다** — 모델 슈퍼셋에 편입돼 있고 수집도 계속된다.
         (생산: `collection/options/option_chain_worker.py:102`)

    ⚠ **①과 ②는 모순이 아니다.** "CORE"는 체크리스트 게이트의 자격이고, `active_features`
      편입은 GBM 이 그 값을 피처로 쓴다는 뜻이다. 한쪽이 죽었다고 다른 쪽을 끌 이유가 없다 —
      끄면 IC 재검증(26주 WFA 항목)에 쓸 표본이 함께 끊긴다.
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

    # ② 편입 유지 — 빠지면 수집·재검증 표본이 끊긴다(사용자 결정 역행).
    assert core in active, (
        "'%s'가 active_features 에서 빠졌다 — 2026-08-23 사용자 결정"
        "('편입하고 데이터 수집은 계속하자')에 역행한다. 뺐다면 DECISION_LOG 에 "
        "근거가 있어야 한다." % core)

    # ① 그래도 CORE 게이트로는 도달 불가여야 한다 — 편입이 게이트 부활을 뜻하지 않는다.
    reachable = _reachable_horizons()
    long_hz = [hz for hz, grp in HORIZON_CORE_GROUP.items() if grp == "long"]
    assert long_hz, "장기 그룹 호라이즌 정의가 사라졌다"
    for hz in long_hz:
        assert hz not in reachable, (
            "%s(장기 그룹)가 도달 가능해졌다 — `opt_chain_pcr` 편입은 피처 사용이지 "
            "CORE 체크리스트 부활이 아니다. 라우터를 바꿨다면 CLAUDE.md §3 갱신 필요" % hz)
