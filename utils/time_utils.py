# utils/time_utils.py — 시간·만기일 계산 유틸리티
import datetime
from typing import Optional

from config.krx_holidays import is_krx_holiday

# 한국 표준시 (UTC+9). 운영 환경이 UTC로 설정된 컨테이너/VM에서도
# 모든 시간 판단이 KST 기준으로 일관되게 동작하도록 명시한다.
KST = datetime.timezone(datetime.timedelta(hours=9))


def now_kst() -> datetime.datetime:
    """현재 KST 시각을 naive datetime으로 반환 (기존 naive 비교 코드와 호환)."""
    return datetime.datetime.now(KST).replace(tzinfo=None)


# ── 거래일 / 시장 시간 판단 ────────────────────────────────────

def is_trading_day(dt: Optional[datetime.datetime] = None) -> bool:
    """KRX 거래일 여부 (평일 AND 공휴일 아님)."""
    if dt is None:
        dt = now_kst()
    d = dt.date() if isinstance(dt, datetime.datetime) else dt
    return d.weekday() < 5 and not is_krx_holiday(d)


def is_market_open(dt: Optional[datetime.datetime] = None) -> bool:
    """장 중 여부 (09:00~15:30, KRX 거래일)."""
    if dt is None:
        dt = now_kst()
    t = dt.time()
    return (
        datetime.time(9, 0) <= t <= datetime.time(15, 30)
        and is_trading_day(dt)
    )


def minutes_to_close(dt: Optional[datetime.datetime] = None) -> int:
    """장 마감까지 남은 분 수"""
    if dt is None:
        dt = now_kst()
    close = dt.replace(hour=15, minute=30, second=0, microsecond=0)
    delta = close - dt
    return max(0, int(delta.total_seconds() // 60))


def is_force_exit_time(dt: Optional[datetime.datetime] = None) -> bool:
    """15:10 강제 청산 시각 도달 여부"""
    if dt is None:
        dt = now_kst()
    return dt.time() >= datetime.time(15, 10)


def is_new_entry_allowed(dt: Optional[datetime.datetime] = None) -> bool:
    """신규 진입 허용 여부 (15:00 이후 금지)"""
    if dt is None:
        dt = now_kst()
    return dt.time() < datetime.time(15, 0)


def get_time_zone(dt: Optional[datetime.datetime] = None) -> str:
    """시간대 구간 분류 (v6.6)"""
    if dt is None:
        dt = now_kst()
    t = dt.time()

    if datetime.time(9, 0) <= t < datetime.time(9, 5):
        return "GAP_OPEN"
    elif datetime.time(9, 5) <= t < datetime.time(10, 30):
        return "OPEN_VOLATILE"
    elif datetime.time(10, 30) <= t < datetime.time(11, 50):
        return "STABLE_TREND"
    elif datetime.time(13, 0) <= t < datetime.time(14, 0):
        return "LUNCH_RECOVERY"
    elif datetime.time(14, 0) <= t < datetime.time(15, 0):
        return "CLOSE_VOLATILE"
    elif datetime.time(15, 0) <= t < datetime.time(15, 10):
        return "EXIT_ONLY"
    else:
        return "OTHER"


# ── KOSPI200 선물 월물 만기일 계산 ─────────────────────────────
# 매월 두 번째 목요일. 해당일이 KRX 휴장이면 전 거래일(수요일)이 실제 만기.

def get_monthly_expiry_date(year: int, month: int) -> datetime.date:
    """KOSPI200 선물 월물 만기일 — 해당 월의 두 번째 목요일."""
    first_day = datetime.date(year, month, 1)
    # 첫 번째 목요일까지 오프셋 (weekday: 목=3)
    first_thu_offset = (3 - first_day.weekday()) % 7
    first_thu = first_day + datetime.timedelta(days=first_thu_offset)
    second_thu = first_thu + datetime.timedelta(weeks=1)
    # 만기일이 KRX 휴장이면 전 거래일(1일 전)로 이동
    while is_krx_holiday(second_thu):
        second_thu -= datetime.timedelta(days=1)
    return second_thu


def days_to_monthly_expiry(dt: Optional[datetime.date] = None) -> int:
    """오늘부터 이번 달 월물 만기일까지 남은 거래일 수 (음수이면 이미 지난 만기)."""
    if dt is None:
        dt = now_kst().date()
    expiry = get_monthly_expiry_date(dt.year, dt.month)
    return (expiry - dt).days


def is_expiry_day(dt: Optional[datetime.datetime] = None) -> bool:
    """오늘이 KOSPI200 선물 월물 만기일인지."""
    if dt is None:
        dt = now_kst()
    d = dt.date() if isinstance(dt, datetime.datetime) else dt
    return d == get_monthly_expiry_date(d.year, d.month)


# ── FOMC 발표일 (한국 기준) ────────────────────────────────────
# FOMC 결과는 미국 동부 오후 2시 → 한국 익일 새벽 3~4시 발표.
# 장 시작 전 이미 결과가 반영되므로 당일(발표 다음날 KST)을 마킹.
# 매년 FOMC 일정 발표 후 갱신 필요 (https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)
_FOMC_DATES_KST: frozenset = frozenset([
    # 2026
    datetime.date(2026, 1, 29),
    datetime.date(2026, 3, 19),
    datetime.date(2026, 5, 7),
    datetime.date(2026, 6, 18),
    datetime.date(2026, 7, 30),
    datetime.date(2026, 9, 17),
    datetime.date(2026, 11, 5),
    datetime.date(2026, 12, 17),
    # 2027
    datetime.date(2027, 1, 28),
    datetime.date(2027, 3, 18),
    datetime.date(2027, 5, 6),
    datetime.date(2027, 6, 17),
    datetime.date(2027, 7, 29),
    datetime.date(2027, 9, 16),
    datetime.date(2027, 11, 4),
    datetime.date(2027, 12, 16),
])


def is_fomc_day(dt: Optional[datetime.datetime] = None) -> bool:
    """FOMC 결과 발표 당일(한국 기준) 여부."""
    if dt is None:
        dt = now_kst()
    d = dt.date() if isinstance(dt, datetime.datetime) else dt
    return d in _FOMC_DATES_KST


# ── 위클리 만기 계산 ───────────────────────────────────────────
def get_next_thursday(dt: Optional[datetime.date] = None) -> datetime.date:
    """다음 목요일 날짜 (위클리 만기)"""
    if dt is None:
        dt = now_kst().date()
    days_ahead = 3 - dt.weekday()   # 목요일 = 3
    if days_ahead <= 0:
        days_ahead += 7
    return dt + datetime.timedelta(days=days_ahead)


def get_next_monday(dt: Optional[datetime.date] = None) -> datetime.date:
    """다음 월요일 날짜"""
    if dt is None:
        dt = now_kst().date()
    days_ahead = 0 - dt.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return dt + datetime.timedelta(days=days_ahead)


def days_to_weekly_expiry(dt: Optional[datetime.date] = None) -> dict:
    """목 위클리·월 위클리 잔존일 계산"""
    if dt is None:
        dt = now_kst().date()
    thu = get_next_thursday(dt)
    mon = get_next_monday(dt)
    return {
        "thursday": (thu - dt).days,
        "monday":   (mon - dt).days,
    }


def get_active_weekly(dt: Optional[datetime.date] = None) -> str:
    """현재 활성 위클리 만기 타입"""
    if dt is None:
        dt = now_kst().date()
    expiry = days_to_weekly_expiry(dt)
    # 목요일이 더 가까우면 THU, 아니면 MON
    if expiry["thursday"] <= expiry["monday"]:
        return "THU"
    return "MON"


def format_hhmmss(dt: Optional[datetime.datetime] = None) -> str:
    if dt is None:
        dt = now_kst()
    return dt.strftime("%H:%M:%S")
