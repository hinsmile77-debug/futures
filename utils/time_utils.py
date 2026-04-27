# utils/time_utils.py — 시간·만기일 계산 유틸리티
import datetime
from typing import Optional

from config.krx_holidays import is_krx_holiday


# ── 거래일 / 시장 시간 판단 ────────────────────────────────────

def is_trading_day(dt: Optional[datetime.datetime] = None) -> bool:
    """KRX 거래일 여부 (평일 AND 공휴일 아님)."""
    if dt is None:
        dt = datetime.datetime.now()
    d = dt.date() if isinstance(dt, datetime.datetime) else dt
    return d.weekday() < 5 and not is_krx_holiday(d)


def is_market_open(dt: Optional[datetime.datetime] = None) -> bool:
    """장 중 여부 (09:00~15:30, KRX 거래일)."""
    if dt is None:
        dt = datetime.datetime.now()
    t = dt.time()
    return (
        datetime.time(9, 0) <= t <= datetime.time(15, 30)
        and is_trading_day(dt)
    )


def minutes_to_close(dt: Optional[datetime.datetime] = None) -> int:
    """장 마감까지 남은 분 수"""
    if dt is None:
        dt = datetime.datetime.now()
    close = dt.replace(hour=15, minute=30, second=0, microsecond=0)
    delta = close - dt
    return max(0, int(delta.total_seconds() // 60))


def is_force_exit_time(dt: Optional[datetime.datetime] = None) -> bool:
    """15:10 강제 청산 시각 도달 여부"""
    if dt is None:
        dt = datetime.datetime.now()
    return dt.time() >= datetime.time(15, 10)


def is_new_entry_allowed(dt: Optional[datetime.datetime] = None) -> bool:
    """신규 진입 허용 여부 (15:00 이후 금지)"""
    if dt is None:
        dt = datetime.datetime.now()
    return dt.time() < datetime.time(15, 0)


def get_time_zone(dt: Optional[datetime.datetime] = None) -> str:
    """시간대 구간 분류 (v6.5)"""
    if dt is None:
        dt = datetime.datetime.now()
    t = dt.time()

    if datetime.time(9, 5) <= t < datetime.time(10, 30):
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


# ── 위클리 만기 계산 ───────────────────────────────────────────
def get_next_thursday(dt: Optional[datetime.date] = None) -> datetime.date:
    """다음 목요일 날짜 (위클리 만기)"""
    if dt is None:
        dt = datetime.date.today()
    days_ahead = 3 - dt.weekday()   # 목요일 = 3
    if days_ahead <= 0:
        days_ahead += 7
    return dt + datetime.timedelta(days=days_ahead)


def get_next_monday(dt: Optional[datetime.date] = None) -> datetime.date:
    """다음 월요일 날짜"""
    if dt is None:
        dt = datetime.date.today()
    days_ahead = 0 - dt.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return dt + datetime.timedelta(days=days_ahead)


def days_to_weekly_expiry(dt: Optional[datetime.date] = None) -> dict:
    """목 위클리·월 위클리 잔존일 계산"""
    if dt is None:
        dt = datetime.date.today()
    thu = get_next_thursday(dt)
    mon = get_next_monday(dt)
    return {
        "thursday": (thu - dt).days,
        "monday":   (mon - dt).days,
    }


def get_active_weekly(dt: Optional[datetime.date] = None) -> str:
    """현재 활성 위클리 만기 타입"""
    if dt is None:
        dt = datetime.date.today()
    expiry = days_to_weekly_expiry(dt)
    # 목요일이 더 가까우면 THU, 아니면 MON
    if expiry["thursday"] <= expiry["monday"]:
        return "THU"
    return "MON"


def format_hhmmss(dt: Optional[datetime.datetime] = None) -> str:
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime("%H:%M:%S")
