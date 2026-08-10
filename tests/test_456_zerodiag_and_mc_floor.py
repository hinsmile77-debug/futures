# tests/test_456_zerodiag_and_mc_floor.py — 456차 P1-c·P2·P3 회귀 테스트
"""main.py 전체를 import하면 COM/PyQt 의존이 걸리므로, 세 변경의 **순수 로직만**
같은 규칙으로 재현해 검증한다. 원본과 규칙이 갈라지지 않도록 각 테스트에
원본 위치를 주석으로 못박아 둔다.

실행:  python tests/test_456_zerodiag_and_mc_floor.py
"""
from __future__ import annotations

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FAIL = []


def check(name, got, want):
    if got == want:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s\n       got  = %r\n       want = %r" % (name, got, want))
        FAIL.append(name)


# ─────────────────────────────────────────────────────────────────────────
# P1-c — ZeroDiag 원인/참고 분리  (원본: main.py _diagnose_zero_entry)
# ─────────────────────────────────────────────────────────────────────────
def zerodiag_msg(checklist_reason="", coherence=False, cascade=False,
                 direction=1, conf=0.5, min_conf=0.4, outliers=()):
    reasons, notes = [], []
    primary = str(checklist_reason or "").strip()
    if primary and primary not in ("FLAT", "conf↓", "Coherence↓"):
        reasons.append(primary)
    if coherence:
        reasons.append("CoherenceGate")
    if cascade:
        reasons.append("CascadeCoherence")
    if direction == 0:
        reasons.append("FLAT수렴")
    if conf < min_conf:
        reasons.append("conf미달({:.3f}<mc{:.3f})".format(conf, min_conf))
    if outliers:
        notes.append("이상값피처({})".format(",".join(outliers)))
    if not (reasons or notes):
        return None
    if not reasons:
        reasons.append("⚠원인미상")
    msg = "진입X 원인: {}".format(" / ".join(reasons))
    if notes:
        msg += " | 참고: {}".format(" / ".join(notes))
    return msg


def test_zerodiag():
    print("[P1-c] ZeroDiag 원인/참고 분리")

    # 2026-08-10 09:19 실사고 재현 — 진짜 차단자는 RegimeOverride였는데
    # 구버전은 "이상값피처(...)"만 찍어 그것이 원인으로 읽혔다.
    check(
        "실사고 재현: RegimeOverride가 원인으로 나온다",
        zerodiag_msg(checklist_reason="RegimeOverride", direction=1,
                     conf=0.370, min_conf=0.360,
                     outliers=("opt_pcr_bearish", "opt_pcr_extreme")),
        "진입X 원인: RegimeOverride | 참고: 이상값피처(opt_pcr_bearish,opt_pcr_extreme)",
    )

    # 참고만 있고 원인을 못 찾으면 반드시 명시된다 (오독 방지 핵심)
    check(
        "원인 미발견 시 ⚠원인미상 명시",
        zerodiag_msg(direction=1, conf=0.5, min_conf=0.4,
                     outliers=("opt_atm_pcr",)),
        "진입X 원인: ⚠원인미상 | 참고: 이상값피처(opt_atm_pcr)",
    )

    # 종전 동작 보존 — 일반 원인은 그대로
    check(
        "FLAT수렴+conf미달 종전 형식 유지",
        zerodiag_msg(checklist_reason="FLAT", direction=0,
                     conf=0.393, min_conf=1.000),
        "진입X 원인: FLAT수렴 / conf미달(0.393<mc1.000)",
    )

    # checklist_reason이 이미 개별 진단으로 표현되는 값이면 중복 출력하지 않는다
    check(
        "conf↓ 중복 제거",
        zerodiag_msg(checklist_reason="conf↓", direction=1,
                     conf=0.30, min_conf=0.40),
        "진입X 원인: conf미달(0.300<mc0.400)",
    )
    check(
        "Coherence↓ 중복 제거",
        zerodiag_msg(checklist_reason="Coherence↓", coherence=True,
                     direction=1, conf=0.5, min_conf=0.4),
        "진입X 원인: CoherenceGate",
    )

    # 아무것도 없으면 로그 자체를 찍지 않는다 (종전 동작)
    check("무이상 시 미출력", zerodiag_msg(direction=1, conf=0.5, min_conf=0.4), None)


# ─────────────────────────────────────────────────────────────────────────
# P2 — min_conf 완화 하한  (원본: main.py TrendGate 블록)
# ─────────────────────────────────────────────────────────────────────────
def apply_trendgate(actual_mc, tp_override, relax_floor, enabled):
    """TrendGate 완화 + 456차 완화 하한 클램프."""
    mc = min(actual_mc, tp_override)
    clamped = False
    if enabled and relax_floor is not None and mc < relax_floor:
        mc = relax_floor
        clamped = True
    return round(mc, 10), clamped


def test_mc_floor():
    print("[P2] min_conf 완화 하한")

    # 2026-08-10 14:49 실사고 재현: FQAdj가 실측acc=20%로 0.41→0.46 강화했는데
    # TrendGate가 0.44로 되돌려 진입 → -162,926원.
    check("실사고 재현: 강화선 0.46이 유지된다",
          apply_trendgate(0.46, 0.44, 0.46, True), (0.46, True))
    check("플래그 OFF면 종전대로 0.44로 완화",
          apply_trendgate(0.46, 0.44, 0.46, False), (0.44, False))

    # FQAdj가 강화하지 않은 날(floor=None)은 동작이 완전히 같아야 한다
    check("floor 없음 → 종전 완화 그대로",
          apply_trendgate(0.42, 0.38, None, True), (0.38, False))

    # 완화 폭이 강화선 위에서 끝나면 클램프하지 않는다
    check("완화가 강화선 위 → 클램프 없음",
          apply_trendgate(0.50, 0.47, 0.46, True), (0.47, False))

    # TrendGate가 오히려 더 엄격하면 min()이 그대로 이긴다
    check("TrendGate가 더 엄격 → 그 값 유지",
          apply_trendgate(0.46, 0.52, 0.46, True), (0.46, False))


# ─────────────────────────────────────────────────────────────────────────
# P3 — JointGateBlock 폴백 중립화  (원본: main.py JointGateBlock 블록)
# ─────────────────────────────────────────────────────────────────────────
def joint_block(meta_size, tox_size, meta_action, tox_action,
                fallback, neutralize_enabled, thr=0.50):
    """차단 판정 + 폴백 중립화 반사실을 함께 계산."""
    eff = 1.0 if (neutralize_enabled and fallback) else meta_size
    live = (meta_action == "reduce" and tox_action == "reduce"
            and eff * tox_size < thr)
    # 섀도: 항상 '중립화했다면' 기준으로 계산 (플래그와 무관)
    shadow = (meta_action == "reduce" and tox_action == "reduce"
              and (1.0 if fallback else meta_size) * tox_size < thr)
    return live, shadow, round(eff * tox_size, 4)


def test_joint():
    print("[P3] JointGateBlock 폴백 중립화")

    # 2026-08-10 09:40/09:41 실측: meta=0.50(폴백) × tox=0.70 = 0.350 → 차단
    check("기본 OFF: 종전대로 차단 (라이브 무변경)",
          joint_block(0.50, 0.70, "reduce", "reduce", True, False),
          (True, False, 0.35))
    check("ON이면 중립화되어 통과",
          joint_block(0.50, 0.70, "reduce", "reduce", True, True),
          (False, False, 0.70))

    # 폴백이 아닌 진짜 0.50은 중립화 대상이 아니다 — 켜도 차단 유지
    check("비폴백 0.50은 ON에서도 차단 유지",
          joint_block(0.50, 0.70, "reduce", "reduce", False, True),
          (True, True, 0.35))

    # reduce×reduce가 아니면 애초에 게이트 대상이 아니다
    check("take 밴드는 차단 안 함",
          joint_block(0.50, 0.70, "take", "reduce", True, False),
          (False, False, 0.35))


if __name__ == "__main__":
    test_zerodiag()
    print()
    test_mc_floor()
    print()
    test_joint()
    print()
    if FAIL:
        print("실패 %d건: %s" % (len(FAIL), ", ".join(FAIL)))
        sys.exit(1)
    print("전체 통과")
