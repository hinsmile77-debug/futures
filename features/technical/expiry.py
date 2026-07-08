# features/technical/expiry.py — 만기 구조 더미 피처
"""
감사 근거: docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md §6-3 순위9 "만기 구조 더미".
"만기주·위칭데이·월말 리밸런싱 — 수급 왜곡 반복 패턴. time_sin/cos가 못 잡는 달력 효과."

KOSPI200 옵션 만기 구조(dashboard/main_dashboard.py:_calc_cycle_badge()와 동일 규칙):
  - 매주 월요일 : 위클리 만기
  - 매주 목요일 : 위클리 만기 (단, 그 달 두 번째 목요일이면 월간 만기로 분류)

거래소 휴장일력은 반영하지 않는다 — 달력일 기준 근사치("자체 계산" 범위,
정밀 휴장일 캘린더는 별도 데이터 소스가 필요해 범위 밖).
"""
import datetime
from typing import Dict


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> datetime.date:
    """해당 월 n번째 특정 요일(0=월~6=일) 날짜."""
    first = datetime.date(year, month, 1)
    delta = (weekday - first.weekday()) % 7
    return first + datetime.timedelta(days=delta + (n - 1) * 7)


def compute_expiry_features(ts_dt: datetime.datetime) -> Dict[str, float]:
    """주어진 시각의 만기 구조 더미 피처 4종 반환."""
    d = ts_dt.date()
    wd = d.weekday()  # 0=월 ... 6=일

    monthly_expiry = _nth_weekday(d.year, d.month, 3, 2)  # 3=목요일, 2번째

    is_weekly_witching = 1.0 if wd in (0, 3) and d != monthly_expiry else 0.0
    is_monthly_witching = 1.0 if d == monthly_expiry else 0.0

    week_start = d - datetime.timedelta(days=wd)
    week_end = week_start + datetime.timedelta(days=6)
    is_monthly_expiry_week = 1.0 if week_start <= monthly_expiry <= week_end else 0.0

    if d.month == 12:
        next_month_first = datetime.date(d.year + 1, 1, 1)
    else:
        next_month_first = datetime.date(d.year, d.month + 1, 1)
    days_left_in_month = (next_month_first - d).days
    is_month_end_rebalance = 1.0 if days_left_in_month <= 3 else 0.0

    return {
        "is_weekly_witching":     is_weekly_witching,
        "is_monthly_witching":    is_monthly_witching,
        "is_monthly_expiry_week": is_monthly_expiry_week,
        "is_month_end_rebalance": is_month_end_rebalance,
    }


def is_near_monthly_expiry(
    ts_dt: datetime.datetime,
    days_before: int = 2,
    days_after: int = 1,
) -> bool:
    """월간 만기(그 달 두 번째 목요일) 기준 D-days_before ~ D+days_after 이내 여부.

    is_monthly_expiry_week(월~일 캘린더 주 전체)보다 좁은 범위 — ATR 게이트처럼
    "만기 임박 며칠"에만 예외를 걸고 싶은 용도. 달력일 근사(휴장일 미반영)는
    compute_expiry_features()와 동일 원칙.
    """
    d = ts_dt.date()
    monthly_expiry = _nth_weekday(d.year, d.month, 3, 2)
    delta = (d - monthly_expiry).days
    return -days_before <= delta <= days_after
