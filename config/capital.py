# -*- coding: utf-8 -*-
"""자본금 단일 출처 — 사이징·리스크 비율이 참조하는 기준 자본을 한 곳에서 정한다.

[왜 필요한가 — 2026-08-06]
자본 기준이 세 군데로 흩어져 있었다.
  ① config/settings.py:SIZING_TARGET_CAPITAL_KRW  (사이저 base_risk 전용)
  ② main.py 3곳의 **하드코딩** `max(잔고, 50_000_000)`  (daily_loss_pct 분모)
  ③ strategy/entry/checklist.py 의 **하드코딩** `daily_loss_pct < 0.02`
     (config/settings.py:DAILY_LOSS_LIMIT_PCT 는 소비처가 0건인 죽은 설정이었다)

②가 특히 위험했다. 분모에 5천만원 하한이 박혀 있어서 **실전 자본이 5천만 미만이면
당일 손실률이 실제보다 작게 계산되고 2% 진입차단이 늦게 걸린다.** 모의 잔고가
마침 4,988만원이라 지금은 증상이 없지만, 값이 우연히 일치했을 뿐이다.

같은 날 모의계좌 재발급으로 자본이 4.9억 -> 5천만으로 바뀌었는데 시스템 어디에도
그 사실이 드러나지 않았다(로그를 사람이 대조해서야 알았다). capital_profile() 은
그 상황을 기동 시 한 줄로 드러내기 위한 것이다.

[연동하는 것과 하지 않는 것 — 의도적 구분]
자본이 바뀌면 함께 따라가야 하는 값과, 따라가면 **안 되는** 값이 있다.

  연동함:  사이징 기준자본, daily_loss_pct 분모, 한도의 원화 환산(표시용)
  연동 안 함:
    - MAX_CONTRACTS : 431차가 **손익 카운터팩추얼**로 정한 값이다
                      (cap=2 +169만 / cap=3 +53만 / cap=5 -233만).
                      자본 공식으로 자동 파생하면 실측으로 얻은 안전 상한을
                      산술식이 덮어쓴다. CLAUDE.md 실전전환기준 ⑧도 수동 결정으로
                      규정한다. => 여기서는 **경고만** 한다(check_consistency).
    - ACCOUNT_BASE_RISK(3%) / DAILY_LOSS_LIMIT_PCT(2%)
                    : 리스크 "정책"이라 자본과 독립이어야 한다. 비율을 자본에
                      연동하면 base_risk = 자본 x 비율 에서 이중 반영된다.
    - 계약 스펙(pt_value 등) : 거래소 상수.
"""
from __future__ import annotations

from config.settings import (
    SIZING_TARGET_CAPITAL_ENABLED,
    SIZING_TARGET_CAPITAL_KRW,
    ACCOUNT_BASE_RISK,
    DAILY_LOSS_LIMIT_PCT,
    MAX_CONTRACTS,
)

# 최대노출 레버리지 경고 임계 (기준자본 대비 MAX_CONTRACTS 총 계약가치 배수).
# 자동 조치는 하지 않는다 — 경고만.
LEVERAGE_WARN_MULT = 5.0
# 실제잔고 vs 기준자본 괴리 경고 임계(비율). 2026-08-06 계좌 재발급(4.9억 -> 5천만,
# 괴리 -89.8%)이 이 임계에 걸린다.
BALANCE_GAP_WARN = 0.50


def _f(value, default=0.0):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    if out != out:          # NaN
        return default
    return out


def sizing_capital(actual_balance=0.0) -> float:
    """사이징·리스크 비율 계산의 기준 자본.

    **자본을 참조하는 모든 코드는 이 함수만 쓴다.** 리터럴 금지.

    SIZING_TARGET_CAPITAL_ENABLED 가 True(모의투자 한정)면 목표자본을,
    False(실전)면 실제 브로커 잔고를 쓴다.
    """
    if SIZING_TARGET_CAPITAL_ENABLED:
        return max(0.0, _f(SIZING_TARGET_CAPITAL_KRW))
    return max(0.0, _f(actual_balance))


def daily_loss_ratio(loss_krw, actual_balance=0.0) -> float:
    """당일 손실률(양수=손실). 분모는 sizing_capital() 하나뿐이다.

    구 코드는 `max(잔고, 50_000_000)` 으로 분모에 하한을 박아 뒀는데, 그 하한은
    자본이 그보다 작을 때 손실률을 **과소평가**해 2% 한도를 느슨하게 만든다.
    기준자본이 0이면(잔고 미확보 등) 0.0 을 돌려준다 — 0으로 나누지 않으며,
    "손실 없음"이 아니라 "판정 근거 없음"이라는 뜻이다. 이 경우 9_risk 체크는
    통과하지만, 잔고 미확보 상태는 broker sync 게이트가 별도로 막는다.
    """
    base = sizing_capital(actual_balance)
    if base <= 0:
        return 0.0
    return max(0.0, _f(loss_krw)) / base


def base_risk_krw(actual_balance=0.0) -> float:
    """사이저가 쓰는 1회 리스크 예산(원). = 기준자본 x ACCOUNT_BASE_RISK"""
    return sizing_capital(actual_balance) * _f(ACCOUNT_BASE_RISK)


def daily_loss_limit_krw(actual_balance=0.0) -> float:
    """일일 손실 한도의 원화 환산(표시·로그용). = 기준자본 x DAILY_LOSS_LIMIT_PCT"""
    return sizing_capital(actual_balance) * _f(DAILY_LOSS_LIMIT_PCT)


def check_consistency(actual_balance=0.0, index_price=0.0, pt_value=0.0,
                      is_simulation=None, effective_max_qty=None):
    """자본 설정 정합성 점검. (level, message) 리스트를 반환한다.

    **자동 조치는 하지 않는다.** 어긋난 사실을 드러내기만 한다 — 자동 보정은
    2026-08-06 계좌 대체 폴백 사고와 같은 부류의 위험을 만든다.

    is_simulation:      True=모의 / False=실서버 / None=판정불가(경고 생략)
    effective_max_qty:  대시보드 ui_prefs 의 실효 상한(있으면 MAX_CONTRACTS 와 대조)
    """
    out = []
    base = sizing_capital(actual_balance)
    bal = _f(actual_balance)

    # ① 실서버인데 목표자본 모드 -- 실전에서 실제 잔고와 무관하게 사이징된다.
    if is_simulation is False and SIZING_TARGET_CAPITAL_ENABLED:
        out.append((
            "CRITICAL",
            "실서버 접속인데 SIZING_TARGET_CAPITAL_ENABLED=True 입니다 — "
            "실제 잔고(%s원)와 무관하게 목표자본(%s원)으로 사이징됩니다. "
            "실전에서는 False 로 전환하거나 _KRW 를 실제 자본으로 맞추십시오."
            % (format(int(bal), ","), format(int(SIZING_TARGET_CAPITAL_KRW), ","))
        ))

    # ② 실제잔고 vs 기준자본 괴리 -- 계좌 재발급/자본 변동 감지.
    if base > 0 and bal > 0:
        gap = (bal - base) / base
        if abs(gap) >= BALANCE_GAP_WARN:
            out.append((
                "WARNING",
                "기준자본(%s원)과 실제잔고(%s원) 괴리 %+.1f%% — 계좌가 바뀌었거나 "
                "자본 설정이 낡았을 수 있습니다(config/settings.py:"
                "SIZING_TARGET_CAPITAL_KRW)."
                % (format(int(base), ","), format(int(bal), ","), gap * 100.0)
            ))

    # ③ MAX_CONTRACTS 최대노출 레버리지 -- 경고만. 자동 인하 금지.
    exposure = _f(MAX_CONTRACTS) * _f(index_price) * _f(pt_value)
    if base > 0 and exposure > 0:
        lev = exposure / base
        if lev > LEVERAGE_WARN_MULT:
            out.append((
                "WARNING",
                "MAX_CONTRACTS=%s 최대노출 %s원 = 기준자본의 %.1f배 "
                "(임계 %.1f배). 자동 조정하지 않습니다 — MAX_CONTRACTS 는 손익 "
                "실측으로 정하는 값입니다(CLAUDE.md ⑧)."
                % (MAX_CONTRACTS, format(int(exposure), ","), lev, LEVERAGE_WARN_MULT)
            ))

    # ④ 대시보드 실효 상한이 MAX_CONTRACTS 와 다름 -- ui_prefs 잔존값 감지.
    if effective_max_qty is not None:
        eff = int(_f(effective_max_qty, MAX_CONTRACTS))
        if eff != int(MAX_CONTRACTS):
            out.append((
                "INFO",
                "대시보드 실효 최대수량=%d 이 MAX_CONTRACTS=%s 와 다릅니다 "
                "(data/ui_prefs.json:max_entry_qty 잔존값)."
                % (eff, MAX_CONTRACTS)
            ))
    return out


def capital_profile(actual_balance=0.0, index_price=0.0, pt_value=0.0) -> dict:
    """기동 시 1회 로그용 자본 프로파일."""
    base = sizing_capital(actual_balance)
    bal = _f(actual_balance)
    return {
        "mode": "target" if SIZING_TARGET_CAPITAL_ENABLED else "actual",
        "base_capital": base,
        "actual_balance": bal,
        "gap_pct": ((bal - base) / base * 100.0) if (base > 0 and bal > 0) else 0.0,
        "base_risk_krw": base_risk_krw(actual_balance),
        "daily_loss_limit_krw": daily_loss_limit_krw(actual_balance),
        "max_contracts": int(_f(MAX_CONTRACTS, 0)),
        "max_exposure_krw": _f(MAX_CONTRACTS) * _f(index_price) * _f(pt_value),
    }


def format_profile(profile: dict) -> str:
    """capital_profile() 결과를 한 줄 로그 문자열로."""
    lev = ""
    if profile.get("base_capital", 0) > 0 and profile.get("max_exposure_krw", 0) > 0:
        lev = " (레버리지 %.2fx)" % (profile["max_exposure_krw"] / profile["base_capital"])
    return (
        "[Capital] 기준자본=%s원(%s) | 실제잔고=%s원 | 괴리=%+.1f%% | "
        "base_risk=%s원(%.1f%%) | 일일한도=%s원(%.1f%%) | "
        "MAX_CONTRACTS=%d 최대노출=%s원%s"
        % (
            format(int(profile["base_capital"]), ","),
            profile["mode"],
            format(int(profile["actual_balance"]), ","),
            profile["gap_pct"],
            format(int(profile["base_risk_krw"]), ","), _f(ACCOUNT_BASE_RISK) * 100.0,
            format(int(profile["daily_loss_limit_krw"]), ","), _f(DAILY_LOSS_LIMIT_PCT) * 100.0,
            profile["max_contracts"],
            format(int(profile["max_exposure_krw"]), ","),
            lev,
        )
    )
