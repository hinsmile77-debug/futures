"""[360차] 역추세 진입 캡(Countertrend Cap) 오프라인 검증 스크립트.

EntryChecklist/PositionSizer는 COM/브로커 의존이 없는 순수 함수이므로 단독 검증 가능:
1. hurst=0.60(trend), price_extension_atr=-2.5(하락 연장), direction=LONG(역추세)
   -> checks["11_countertrend"]=False, max_qty_override=1
2. 동일 조건, direction=SHORT(순방향, 대조군) -> 캡 미발동
3. entry_mode=MEAN_REVERSION으로 떨어지는 입력(VWAP+exhaustion) + hurst=trend +
   역추세 조건 동시 충족 -> MR 예외로 캡 미발동
4. PositionSizer.compute(max_qty_override=1)이 A등급(grade_mult=1.5)에서도 quantity=1로
   캡되는지, kelly_advised_skip은 원래 raw_qty 기준 그대로(오염 없음) 유지되는지 확인

검증 후 삭제 예정 — 임시 스크립트.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.entry.checklist import EntryChecklist
from strategy.entry.position_sizer import PositionSizer
from config.constants import DIRECTION_UP, DIRECTION_DOWN

FAILURES = []


def check(name, cond):
    status = "OK" if cond else "FAIL"
    print(f"[{status}] {name}")
    if not cond:
        FAILURES.append(name)


# 나머지 체크 항목이 전부 통과하도록 우호적인 기본값 (11번 항목 하나만 변수로 둔다)
BASE_KWARGS = dict(
    confidence=0.65,
    vwap_position=0.0,          # 3_vwap: LONG이면 >0 필요, SHORT면 <0 필요 — 방향별로 오버라이드
    cvd_direction=0.0,
    ofi_pressure=0,
    foreign_call_net=0,
    foreign_put_net=0,
    prev_bar_direction=0,
    time_zone="REGULAR",
    daily_loss_pct=0.0,
    min_confidence=0.58,
    micro_regime="혼합",
    disabled_gates={"3_vwap", "4_cvd", "5_ofi", "6_foreign", "7_prev_bar"},  # 11번만 순수 측정
    entry_horizon="5m",
)


def scenario_1_long_countertrend_in_trend():
    print("\n=== 시나리오 1: hurst=trend, 하락연장 중 LONG(역추세) ===")
    cl = EntryChecklist()
    result = cl.evaluate(
        direction=DIRECTION_UP,
        hurst=0.60,
        price_extension_atr=-2.5,  # 하락 연장
        **BASE_KWARGS,
    )
    check("11_countertrend == False (역추세 감지)", result["checks"]["11_countertrend"] is False)
    check("max_qty_override == 1", result.get("max_qty_override") == 1)


def scenario_2_short_with_trend_control():
    print("\n=== 시나리오 2(대조군): hurst=trend, 하락연장 중 SHORT(순방향) ===")
    cl = EntryChecklist()
    result = cl.evaluate(
        direction=DIRECTION_DOWN,
        hurst=0.60,
        price_extension_atr=-2.5,  # 하락 연장, SHORT는 순방향
        **BASE_KWARGS,
    )
    check("11_countertrend == True (순방향이라 미발동)", result["checks"]["11_countertrend"] is True)
    check("max_qty_override is None", result.get("max_qty_override") is None)


def scenario_3_mean_reversion_exempt():
    print("\n=== 시나리오 3: MEAN_REVERSION 모드는 역추세 조건 충족해도 예외 ===")
    cl = EntryChecklist()
    kwargs = dict(BASE_KWARGS)
    kwargs["disabled_gates"] = {"4_cvd", "5_ofi", "6_foreign", "7_prev_bar"}  # 3_vwap은 살려서 MR 유도
    # SHORT MR: VWAP +1.5σ 초과 상승 + bull_exhaustion>=0.60
    result = cl.evaluate(
        direction=DIRECTION_DOWN,
        vwap_position=2.0,
        bull_exhaustion=0.80,
        hurst=0.60,
        price_extension_atr=2.5,  # 상승 연장, SHORT는 역추세 조건에 해당하는 크기
        **{k: v for k, v in kwargs.items() if k != "vwap_position"},
    )
    check("entry_mode == MEAN_REVERSION", result["entry_mode"] == "MEAN_REVERSION")
    check("11_countertrend == True (MR 예외로 캡 미발동)", result["checks"]["11_countertrend"] is True)
    check("max_qty_override is None (MR 예외)", result.get("max_qty_override") is None)


def scenario_4_sizer_clamped_kelly_unpolluted():
    print("\n=== 시나리오 4: PositionSizer가 max_qty_override로 클램프, kelly_advised_skip 오염 없음 ===")
    sizer = PositionSizer(account_balance=500_000_000)
    # grade_mult=1.5(A등급)로 raw_qty가 2 이상 나오도록 파라미터 구성
    baseline = sizer.compute(
        confidence=0.70, atr=2.0, regime="RISK_ON", grade_mult=1.5,
        adaptive_kelly_mult=1.0,
    )
    print(f"baseline(캡 없음) quantity={baseline['quantity']} kelly_advised_skip={baseline['kelly_advised_skip']}")
    check("사전조건: baseline quantity >= 2 (캡이 실제로 뭔가를 깎는지 확인)",
          baseline["quantity"] >= 2)

    capped = sizer.compute(
        confidence=0.70, atr=2.0, regime="RISK_ON", grade_mult=1.5,
        adaptive_kelly_mult=1.0, max_qty_override=1,
    )
    check("max_qty_override=1 적용 시 quantity == 1", capped["quantity"] == 1)
    check("kelly_advised_skip은 baseline과 동일(오염 없음 — raw_qty>=1이라 원래도 False)",
          capped["kelly_advised_skip"] == baseline["kelly_advised_skip"] == False)


if __name__ == "__main__":
    scenario_1_long_countertrend_in_trend()
    scenario_2_short_with_trend_control()
    scenario_3_mean_reversion_exempt()
    scenario_4_sizer_clamped_kelly_unpolluted()

    print("\n=== 결과 ===")
    if FAILURES:
        print(f"FAIL {len(FAILURES)}건: {FAILURES}")
        sys.exit(1)
    else:
        print("전부 통과")
        sys.exit(0)
