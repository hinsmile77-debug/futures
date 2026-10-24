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

try:
    # [MW0601 707차 → dev 이식] 실전 자본 3층 — 설정 설명은 config/settings.py 해당 절.
    from config.settings import (RISK_MDD_LIMIT_PCT, SHINDONG_MDD_PER_CONTRACT_KRW,
                                 PROFIT_GUARD_QTY_BASE, FUTURES_MARGIN_RATE_INITIAL,
                                 RISK_CAPITAL_DEPOSIT_CAP_ENABLED)
except ImportError:
    RISK_MDD_LIMIT_PCT, SHINDONG_MDD_PER_CONTRACT_KRW = 0.15, 0
    PROFIT_GUARD_QTY_BASE, FUTURES_MARGIN_RATE_INITIAL = 2, 0.0
    RISK_CAPITAL_DEPOSIT_CAP_ENABLED = False

try:
    # [MW0602 657차 · 신동 V4] 한 거래 위험 한도(X%) 수량 — config/settings.py ④ 절.
    from config.settings import (SHINDONG_RISK_QTY_ENABLED, SHINDONG_RISK_CAPITAL_KRW,
                                 SHINDONG_TRADE_RISK_PCT)
except ImportError:
    SHINDONG_RISK_QTY_ENABLED, SHINDONG_RISK_CAPITAL_KRW, SHINDONG_TRADE_RISK_PCT = False, 0, 0.0

SHINDONG_PT_VALUE_KRW = 50_000   # 미니선물 1pt — strategy/shindong/spec.PT_VALUE_KRW 와 같다(테스트가 고정)

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


def risk_capital(actual_balance=0.0, deposit_krw=None) -> float:
    """[MW0601 707차 → dev 이식] 손실 한도의 기준 자본 = sizing_capital().

    RISK_CAPITAL_DEPOSIT_CAP_ENABLED 이고 deposit_krw(당일 시가 예탁현금)가 측정됐으면 min(sizing_capital, 예탁금).
    꺼져 있거나 미측정(None·0 이하)이면 sizing_capital() 그대로 — 종전 동작.
    """
    base = sizing_capital(actual_balance)
    dep = _f(deposit_krw)
    if RISK_CAPITAL_DEPOSIT_CAP_ENABLED and dep > 0 and base > 0:
        return min(base, dep)
    return base


def daily_loss_ratio(loss_krw, actual_balance=0.0, deposit_krw=None) -> float:
    """당일 손실률(양수=손실). 분모는 sizing_capital() 하나뿐이다.

    구 코드는 `max(잔고, 50_000_000)` 으로 분모에 하한을 박아 뒀는데, 그 하한은
    자본이 그보다 작을 때 손실률을 **과소평가**해 2% 한도를 느슨하게 만든다.
    기준자본이 0이면(잔고 미확보 등) 0.0 을 돌려준다 — 0으로 나누지 않으며,
    "손실 없음"이 아니라 "판정 근거 없음"이라는 뜻이다. 이 경우 9_risk 체크는
    통과하지만, 잔고 미확보 상태는 broker sync 게이트가 별도로 막는다.
    """
    base = risk_capital(actual_balance, deposit_krw)
    if base <= 0:
        return 0.0
    return max(0.0, _f(loss_krw)) / base


def base_risk_krw(actual_balance=0.0) -> float:
    """사이저가 쓰는 1회 리스크 예산(원). = 기준자본 x ACCOUNT_BASE_RISK"""
    return sizing_capital(actual_balance) * _f(ACCOUNT_BASE_RISK)


def daily_loss_limit_krw(actual_balance=0.0, deposit_krw=None) -> float:
    """일일 손실 한도의 원화 환산(표시·로그용). = risk_capital x DAILY_LOSS_LIMIT_PCT"""
    return risk_capital(actual_balance, deposit_krw) * _f(DAILY_LOSS_LIMIT_PCT)


# ── [MW0601 707차] 관측 → 정책 → 통제 ─────────────────────────────────────────────
def margin_per_contract_est(price, pt_value) -> float:
    """1계약 위탁증거금 **추정치**(참고). = 가격 × pt_value × FUTURES_MARGIN_RATE_INITIAL.

    ⚠ 판정에 쓰지 않는다 — 주문 가능 여부는 브로커 CpTd6722 가 정한다(settings 주석 그대로).
    """
    return max(0.0, _f(price) * _f(pt_value) * _f(FUTURES_MARGIN_RATE_INITIAL))


def risk_max_qty(risk_cap):
    """위험 기준 최대계약수 = floor(위험자본 × MDD 한도 ÷ 계약당 MDD 실측). 근거값 없으면 None."""
    per = _f(SHINDONG_MDD_PER_CONTRACT_KRW)
    cap = _f(risk_cap)
    if per <= 0 or cap <= 0:
        return None
    return int(cap * _f(RISK_MDD_LIMIT_PCT) // per)


def profit_guard_krw_scale(live_qty) -> float:
    """ProfitGuard 원화 임계 배율 = max(1, 실주문 수량 ÷ PROFIT_GUARD_QTY_BASE)."""
    base = _f(PROFIT_GUARD_QTY_BASE)
    q = _f(live_qty)
    if base <= 0 or q <= 0:
        return 1.0
    return max(1.0, q / base)


def shindong_risk_qty(atr14, capital_krw=None, risk_pct=None, cat_atr=None, pt_value=None):
    """[MW0602 657차 · 신동 V4] 한 거래 위험 한도 수량 = floor(자본 × X% ÷ (재난손절 배수 × ATR14 × 1pt 원)), 최소 1.

    ATR14 를 모르면 **None**(미측정 — 이 항을 걸지 않는다. 신동 엔진도 그날 진입을 내지 않는다).
    꺼져 있으면(SHINDONG_RISK_QTY_ENABLED=False) None. 재난손절 배수는 신동 규격(spec.FLOW_CAT_STOP_ATR) 단일 출처.
    """
    if not SHINDONG_RISK_QTY_ENABLED:
        return None
    a = _f(atr14, 0.0)
    if a <= 0:
        return None
    if cat_atr is None:
        from strategy.shindong import spec as _sd_spec     # 지연 import — 규격 단일 출처
        cat_atr = _sd_spec.FLOW_CAT_STOP_ATR
    cap = _f(SHINDONG_RISK_CAPITAL_KRW if capital_krw is None else capital_krw)
    pct = _f(SHINDONG_TRADE_RISK_PCT if risk_pct is None else risk_pct)
    per = _f(cat_atr) * a * _f(SHINDONG_PT_VALUE_KRW if pt_value is None else pt_value)
    if cap <= 0 or pct <= 0 or per <= 0:
        return None
    return max(1, int((cap * pct) // per))


def shindong_planned_qty(ui_max_qty, day_start_margin_qty=None, configured_qty=None, risk_qty=None) -> int:
    """신동 계획 수량 = min(최대허용수량, 장시작 주문가능수량). 장시작 미측정이면 min(최대허용수량, SHINDONG_LIVE_QTY).

    [MW0601 707차 후속 / 사용자 결정 2026-10-23] 「장시작 증거금에 따라 부족하면 줄이고 충분하면 늘리되
    최대허용수량까지」. 장시작 값으로 고정하므로 장중 이익으로 증거금 여유가 늘어도 커지지 않는다.
    반환 0 = 증거금 없음(진입 기각).
    """
    ui = int(_f(ui_max_qty, 0))
    if day_start_margin_qty is not None:
        base = max(0, int(_f(day_start_margin_qty, 0)))
    else:
        base = max(1, int(_f(configured_qty, 1)))
    q = min(ui, base) if ui > 0 else base
    if risk_qty is not None and q > 0:
        q = min(q, max(1, int(_f(risk_qty, 1))))    # [V4] X% 위험 수량 — 0(증거금 없음)은 그대로 둔다
    return q


def shindong_entry_qty(planned_qty, margin_qty_now=None) -> int:
    """진입 수량 = min(계획 수량, 진입 직전 주문가능수량). 직전 미측정이면 계획 수량(최종 판정은 브로커)."""
    p = max(0, int(_f(planned_qty, 0)))
    if margin_qty_now is None:
        return p
    return min(p, max(0, int(_f(margin_qty_now, 0))))


def capital_state(policy_krw=None, deposit_krw=None, price=None, pt_value=0.0,
                  margin_qty=None, configured_qty=None, ui_max_qty=None,
                  day_start_margin_qty=None, qty_from_margin=True, deposit_cap=True,
                  risk_qty=None, risk_atr=None, risk_atr_src=None) -> dict:
    """실전 운영 상태 한 덩어리 — 우측패널 「3 주문/체결」 모니터와 `[Capital]` 로그가 같은 값을 쓴다.

    margin_qty          : 지금 신규주문가능수량(CpTd6722, 매수·매도 중 작은 값). None = 미측정.
    day_start_margin_qty: 그날 장시작(FLAT 첫 실측) 주문가능수량. None = 미측정 → SHINDONG_LIVE_QTY 폴백.
    configured_qty      : SHINDONG_LIVE_QTY(폴백) · ui_max_qty: 진입관리탭 최대허용수량(MAX_CONTRACTS 상한).
    level               : OK / WARN(위험 기준 초과 — 사람이 판단) / BLOCK(가능 0 — 신동 진입 기각).
    risk_qty            : [V4] X% 위험 수량(`shindong_risk_qty`). None = 미적용(꺼짐 또는 ATR14 미측정).
                          risk_atr·risk_atr_src 는 사유 표시용(그 수량을 만든 ATR14 와 출처).
    [dev] qty_from_margin=False(SHINDONG_QTY_FROM_MARGIN_ENABLED 꺼짐) → 실주문 = SHINDONG_LIVE_QTY 고정,
          계획 수량은 「켜면」 값으로만 보여 준다. deposit_cap=False → 위험자본 = 정책값(예탁금 상한 미적용).
    """
    pol = sizing_capital(0.0) if policy_krw is None else _f(policy_krw)
    dep = _f(deposit_krw)
    dep_measured = dep > 0
    if deposit_cap:
        rcap = (min(pol, dep) if (pol > 0 and dep_measured) else (pol if pol > 0 else (dep if dep_measured else 0.0)))
    else:
        rcap = pol
    m1 = margin_per_contract_est(price, pt_value) if price else 0.0
    est_qty = int(dep // m1) if (dep_measured and m1 > 0) else None
    rmax = risk_max_qty(rcap)
    cq = int(_f(configured_qty, 0)) if configured_qty is not None else None
    uq = int(_f(ui_max_qty, 0)) if ui_max_qty is not None else None
    planned = (shindong_planned_qty(uq, day_start_margin_qty, cq, risk_qty)
               if (uq is not None or cq is not None) else None)
    eff = None if planned is None else shindong_entry_qty(planned, margin_qty)
    level, reasons = "OK", []
    if not qty_from_margin:
        # [dev] 증거금 연동 꺼짐 — 실주문은 SHINDONG_LIVE_QTY 고정. 연동 시 값은 사유에만 남긴다.
        reasons.append("증거금 연동 꺼짐 — 켜면 %s계약" % ("미측정" if eff is None else eff))
        eff = cq if (cq is None or risk_qty is None) else min(cq, max(1, int(risk_qty)))
        planned = eff
    if risk_qty is not None:
        reasons.append("X%%위험 %d계약(ATR %s%s)" % (int(risk_qty),
                                                  "미측정" if risk_atr is None else "%.1f" % _f(risk_atr),
                                                  "" if not risk_atr_src or risk_atr_src == "0850" else " · " + str(risk_atr_src)[:40]))
    elif SHINDONG_RISK_QTY_ENABLED:
        reasons.append("X%위험 미적용(ATR14 미측정)")
    if eff is not None and eff <= 0:
        level = "BLOCK"
        reasons.append("주문가능 0 — 신동 진입 기각")
    elif eff is not None and planned is not None and eff < planned:
        reasons.append("지금 증거금 기준 축소 %d→%d" % (planned, eff))
    if not qty_from_margin:
        pass
    elif day_start_margin_qty is None:
        reasons.append("장시작 가능수량 미측정 — SHINDONG_LIVE_QTY=%s 폴백" % cq)
    elif cq is not None and planned is not None:
        _pm = shindong_planned_qty(uq, day_start_margin_qty, cq)    # [V4] 증거금 몫만 — X% 축소는 위 사유가 따로 말한다
        if _pm != cq:
            reasons.append("장시작 증거금 기준 %s %d→%d" % ("확대" if _pm > cq else "축소", cq, _pm))
    if eff is not None and rmax is not None and eff > rmax:
        if level == "OK":
            level = "WARN"
        reasons.append("위험 기준 초과(실주문 %d > 위험최대 %d)" % (eff, rmax))
    if margin_qty is None:
        reasons.append("지금 주문가능수량 미측정")
    if not dep_measured:
        reasons.append("예탁금 미측정 — 위험자본=정책값")
    elif not deposit_cap:
        reasons.append("예탁금 상한 꺼짐 — 위험자본=정책값")
    return {
        "policy_krw": pol, "deposit_krw": dep if dep_measured else None, "deposit_measured": dep_measured,
        "risk_capital_krw": rcap, "risk_capital_src": ("예탁금" if (deposit_cap and dep_measured and dep < pol) else "정책"),
        "margin_per_contract_est": m1 if m1 > 0 else None, "margin_qty_est": est_qty,
        "margin_qty": None if margin_qty is None else int(margin_qty),
        "day_start_margin_qty": None if day_start_margin_qty is None else int(day_start_margin_qty),
        "risk_max_qty": rmax, "configured_qty": cq, "ui_max_qty": uq,
        "planned_qty": planned, "effective_qty": eff, "risk_qty": None if risk_qty is None else int(risk_qty),
        "daily_loss_limit_krw": rcap * _f(DAILY_LOSS_LIMIT_PCT),
        "pg_scale": profit_guard_krw_scale(eff or 0),
        "level": level, "reasons": reasons,
    }


def format_capital_state(st: dict) -> str:
    """capital_state() → 한 줄. 미측정은 「미측정」으로 쓴다(0 으로 쓰지 않는다)."""
    def _m(v):
        return "미측정" if v is None else "%s만" % format(int(round(_f(v) / 1e4)), ",")
    def _q(v):
        return "미측정" if v is None else "%d" % int(v)
    _mq = _q(st.get("margin_qty"))
    if st.get("margin_qty") is None and st.get("margin_qty_est") is not None:
        _mq = "미측정(추정 %d)" % st["margin_qty_est"]
    _mark = {"OK": "✅", "WARN": "⚠", "BLOCK": "⛔"}.get(st.get("level"), "?")
    line = ("[Capital] 예탁금 %s · 위험자본 %s(%s) · 계약당 증거금≈%s | 가능수량 지금 %s · 장시작 %s · 위험최대 %s | "
            "신동 실주문 %s(최대허용 %s · 폴백 %s) %s | 일일한도 %s · PG ×%.2f(%s)" % (
                _m(st.get("deposit_krw")), _m(st.get("risk_capital_krw")), st.get("risk_capital_src", "?"),
                _m(st.get("margin_per_contract_est")), _mq, _q(st.get("day_start_margin_qty")),
                _q(st.get("risk_max_qty")),
                _q(st.get("effective_qty")), _q(st.get("ui_max_qty")), _q(st.get("configured_qty")), _mark,
                _m(st.get("daily_loss_limit_krw")), _f(st.get("pg_scale"), 1.0),
                st.get("principal") or "신동 기준"))
    if st.get("reasons"):
        line += " | " + " · ".join(st["reasons"])
    return line


def check_consistency(actual_balance=0.0, index_price=0.0, pt_value=0.0,
                      is_simulation=None, effective_max_qty=None,
                      balance_measured=True):
    """자본 설정 정합성 점검. (level, message) 리스트를 반환한다.

    **자동 조치는 하지 않는다.** 어긋난 사실을 드러내기만 한다 — 자동 보정은
    2026-08-06 계좌 대체 폴백 사고와 같은 부류의 위험을 만든다.

    is_simulation:      True=모의 / False=실서버 / None=판정불가(경고 생략)
    effective_max_qty:  대시보드 ui_prefs 의 실효 상한(있으면 MAX_CONTRACTS 와 대조)
    balance_measured:   [MW0602 628차] False 면 actual_balance 는 브로커 실측이 아니라
                        **코드 기본값**이다. 그 값을 「실제 잔고」로 쓰지 않고, 그것으로
                        괴리(②)를 계산하지 않는다 — 2026-10-14 기본값 1억으로 「괴리
                        +566.7%」를 냈다(계측 4원칙 ②). 대신 미측정 사실을 WARNING 으로 남긴다.
    """
    out = []
    base = sizing_capital(actual_balance)
    bal = _f(actual_balance)
    _bal_txt = (format(int(bal), ",") + "원") if balance_measured else "**미측정**(브로커 잔고 미수신)"

    if not balance_measured:
        out.append((
            "WARNING",
            "실제 잔고 미측정 — 브로커 잔고 조회가 아직 응답하지 않아 코드 기본값(%s원)이 "
            "쓰이고 있다. 이 값은 실측이 아니므로 잔고 괴리 점검을 생략한다. "
            "사이징 기준은 %s." % (
                format(int(bal), ","),
                ("목표자본 %s원(영향 없음)" % format(int(SIZING_TARGET_CAPITAL_KRW), ","))
                if SIZING_TARGET_CAPITAL_ENABLED else "**이 기본값** — 실잔고 확인 전 진입 주의")
        ))

    # ① 실서버인데 목표자본 모드 -- 실전에서 실제 잔고와 무관하게 사이징된다.
    if is_simulation is False and SIZING_TARGET_CAPITAL_ENABLED:
        out.append((
            "CRITICAL",
            "실서버 접속인데 SIZING_TARGET_CAPITAL_ENABLED=True 입니다 — "
            "실제 잔고(%s)와 무관하게 목표자본(%s원)으로 사이징됩니다. "
            "실전에서는 False 로 전환하거나 _KRW 를 실제 자본으로 맞추십시오."
            % (_bal_txt, format(int(SIZING_TARGET_CAPITAL_KRW), ","))
        ))

    # ② 실제잔고 vs 기준자본 괴리 -- 계좌 재발급/자본 변동 감지.
    if balance_measured and base > 0 and bal > 0:
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


def capital_profile(actual_balance=0.0, index_price=0.0, pt_value=0.0,
                    balance_measured=True) -> dict:
    """기동 시 1회 로그용 자본 프로파일.

    [628차] balance_measured=False 면 잔고는 기본값 — `gap_pct` 는 None(미측정)이다.
    """
    base = sizing_capital(actual_balance)
    bal = _f(actual_balance)
    return {
        "mode": "target" if SIZING_TARGET_CAPITAL_ENABLED else "actual",
        "base_capital": base,
        "actual_balance": bal,
        "balance_measured": bool(balance_measured),
        "gap_pct": (((bal - base) / base * 100.0) if (base > 0 and bal > 0) else 0.0)
                   if balance_measured else None,
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
    _measured = profile.get("balance_measured", True)
    _bal_txt = (format(int(profile["actual_balance"]), ",") + "원") if _measured \
        else "미측정(기본값 %s원)" % format(int(profile["actual_balance"]), ",")
    _gap_txt = ("%+.1f%%" % profile["gap_pct"]) if profile.get("gap_pct") is not None else "미측정"
    return (
        "[Capital] 기준자본=%s원(%s) | 실제잔고=%s | 괴리=%s | "
        "base_risk=%s원(%.1f%%) | 일일한도=%s원(%.1f%%) | "
        "MAX_CONTRACTS=%d 최대노출=%s원%s"
        % (
            format(int(profile["base_capital"]), ","),
            profile["mode"],
            _bal_txt,
            _gap_txt,
            format(int(profile["base_risk_krw"]), ","), _f(ACCOUNT_BASE_RISK) * 100.0,
            format(int(profile["daily_loss_limit_krw"]), ","), _f(DAILY_LOSS_LIMIT_PCT) * 100.0,
            profile["max_contracts"],
            format(int(profile["max_exposure_krw"]), ","),
            lev,
        )
    )
