# strategy/ops/verdict_engine.py — 전략 액션 매핑 엔진 (P2 판정)
"""
OUTPERFORM/NORMAL/UNDERPERFORM 판정 + CUSUM 드리프트 수준 + 운용 일수를 결합하여
KEEP / WATCH / REPLACE_CANDIDATE / ROLLBACK_REVIEW 액션을 결정한다.

액션 정의:
  KEEP              : 정상 운용 유지
  WATCH             : 모니터링 강화 — 파라미터 재점검 예약 (2주 이내)
  REPLACE_CANDIDATE : 교체 후보 탐색 — WFA 즉시 예약
  ROLLBACK_REVIEW   : 롤백 검토 — 사이즈 50% 축소 + 긴급 점검

사용:
  action, reason = compute_action(verdict, drift_level, days_active=10)
"""
from __future__ import annotations

from typing import Tuple

# ─── 액션 상수 ────────────────────────────────────────────────────────────────
ACTION_KEEP              = "KEEP"
ACTION_WATCH             = "WATCH"
ACTION_REPLACE_CANDIDATE = "REPLACE_CANDIDATE"
ACTION_ROLLBACK_REVIEW   = "ROLLBACK_REVIEW"

# DriftLevel 상수 (param_drift_detector.DriftLevel 와 동일값 — 직접 의존 없이 사용)
_DRIFT_CLEAR     = 0
_DRIFT_WATCHLIST = 1
_DRIFT_ALARM     = 2
_DRIFT_CRITICAL  = 3

# 판정 상수 (strategy_registry 와 동일값)
_VERDICT_OUTPERFORM   = "OUTPERFORM"
_VERDICT_NORMAL       = "NORMAL"
_VERDICT_UNDERPERFORM = "UNDERPERFORM"
_VERDICT_INSUFFICIENT = "INSUFFICIENT"

# 신규 버전 안착 유예 기간 — 이 기간 중 UNDERPERFORM은 WATCH로 완화
_GRACE_PERIOD_DAYS = 5

# 액션별 색상 (UI 용)
ACTION_COLORS = {
    ACTION_KEEP:              "#3FB950",  # 초록
    ACTION_WATCH:             "#E3B341",  # 노랑
    ACTION_REPLACE_CANDIDATE: "#D29922",  # 주황
    ACTION_ROLLBACK_REVIEW:   "#F85149",  # 빨강
}

# 액션별 한국어
ACTION_KOR = {
    ACTION_KEEP:              "● 정상 유지",
    ACTION_WATCH:             "⚠ 모니터링 강화",
    ACTION_REPLACE_CANDIDATE: "🔄 교체 후보 탐색",
    ACTION_ROLLBACK_REVIEW:   "⛔ 롤백 검토",
}


def compute_action(
    verdict:      str,
    drift_level:  int,
    days_active:  int = 0,
    psi_level:    int = 0,
) -> Tuple[str, str]:
    """
    전략 상태에서 권장 액션과 이유 문자열을 반환한다.

    Args:
        verdict     : OUTPERFORM / NORMAL / UNDERPERFORM / INSUFFICIENT
        drift_level : DriftLevel (0~3)
        days_active : 현재 버전 운용 일수
        psi_level   : RegimeFingerprint PSI DriftLevel (0~3)

    Returns:
        (action_const, reason_str)
    """
    # ── 최우선: CUSUM CRITICAL (성과 급락) ────────────────────────────────
    if drift_level >= _DRIFT_CRITICAL:
        return ACTION_ROLLBACK_REVIEW, (
            "CUSUM CRITICAL — 성과 6σ 이탈. 롤백 검토 및 사이즈 50%% 축소 필요."
        )

    # ── CUSUM ALARM (성과 저하 진행 중) ──────────────────────────────────
    if drift_level >= _DRIFT_ALARM:
        if verdict == _VERDICT_UNDERPERFORM:
            return ACTION_ROLLBACK_REVIEW, (
                "CUSUM ALARM + 기대값 하회 — param_optimizer 즉시 실행. "
                "사이즈 80%% 임시 축소."
            )
        return ACTION_REPLACE_CANDIDATE, (
            "CUSUM ALARM — 성과 저하 진행 중. WFA 즉시 예약."
        )

    # ── 유예 기간 (신규 버전 안착 중) ────────────────────────────────────
    in_grace = days_active < _GRACE_PERIOD_DAYS

    # ── 판정 기반 ─────────────────────────────────────────────────────────
    if verdict == _VERDICT_OUTPERFORM:
        if drift_level >= _DRIFT_WATCHLIST:
            return ACTION_WATCH, (
                "기대값 상회지만 CUSUM WATCHLIST — 피처 이상 여부 추가 확인."
            )
        return ACTION_KEEP, "기대값 상회 & 드리프트 정상 — 현재 전략 유지."

    if verdict == _VERDICT_NORMAL:
        if drift_level >= _DRIFT_WATCHLIST:
            return ACTION_WATCH, (
                "기대값 부합이나 CUSUM WATCHLIST — 파라미터 재점검 2주 이내 예약."
            )
        if psi_level >= _DRIFT_ALARM:
            return ACTION_WATCH, (
                "PSI ALARM — 시장 구조 변화 감지. 조기 재최적화 검토."
            )
        return ACTION_KEEP, "기대값 부합 & 드리프트 정상 — 현재 전략 유지."

    if verdict == _VERDICT_UNDERPERFORM:
        if in_grace:
            return ACTION_WATCH, (
                "기대값 하회 (유예 %d일차 — 안착 중). 5일 추가 관찰 후 재판단." % days_active
            )
        return ACTION_REPLACE_CANDIDATE, (
            "기대값 하회 — param_optimizer + WFA 즉시 예약. "
            "Shadow 전략 2주 가동 후 Hot-Swap 검토."
        )

    # INSUFFICIENT (데이터 부족)
    return ACTION_WATCH, (
        "데이터 부족 (%d일) — %d일 이후 재판정. 관찰 지속." % (
            days_active, _GRACE_PERIOD_DAYS
        )
    )


def rollback_alert_message(
    version:     str,
    verdict:     str,
    drift_level: int,
    action:      str,
    reason:      str,
    pnl_today:   float = 0.0,
) -> str:
    """
    롤백 경보 / 상태 요약 메시지 (로그·Slack 겸용).

    Returns:
        포맷된 경보 문자열
    """
    action_kor = ACTION_KOR.get(action, action)
    lines = [
        "═" * 52,
        "[전략 상태 경보] %s" % version,
        "  판정  : %s" % verdict,
        "  드리프트: %s (Lv.%d)" % (_drift_name(drift_level), drift_level),
        "  액션  : %s" % action_kor,
        "  사유  : %s" % reason,
    ]
    if pnl_today:
        lines.append("  오늘 PnL: %+.0f원" % pnl_today)
    lines.append("═" * 52)
    return "\n".join(lines)


def _drift_name(level: int) -> str:
    return {0: "CLEAR", 1: "WATCHLIST", 2: "ALARM", 3: "CRITICAL"}.get(level, "?")
