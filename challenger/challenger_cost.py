# challenger/challenger_cost.py — 섀도 가상손익의 **비용 축** [MW0601 553차 Phase 2]
"""도전자 가상거래의 왕복비용을 한 곳에서 만든다.

왜 모듈로 빼는가
----------------
🔴 **같은 공식이 두 벌 있었고 둘 다 틀렸다.**
    `challenger_engine.ChallengerEngine._calc_pnl()`  (실제로 쓰이던 쪽)
    `variants/base_challenger.BaseChallenger.calc_pnl()`  (쓰이지 않던 쪽)
둘 다 편도 요율을 **`0.000015` 로 하드코딩**하고 있었다. 그 값은 493차가 규명한
**키움 잔재**이며 이 PC(CYBOS 채널) 실제 요율 `9.8104e-05` 의 **1/6.54** 다.
게다가 **슬리피지 축이 아예 없었다** — 수수료만 뺐다.

두 결함 다 「틀려도 크래시가 안 나고, 틀린 방향이 항상 **낙관**」이라는 493차 수수료
사건과 정확히 같은 형태다. 공식을 한 벌로 모으고 값을 채널 스펙에서 **파생**시킨다
(핀값 금지).

비용 구성 (계측 4원칙 ⑤ — 파생값을 대사하려면 구성요소를 각각 걸어라)
--------------------------------------------------------------------
    왕복비용(pt) = 2 × (진입가+청산가)/2 × 편도요율   ← 수수료
                 + 2 × slip_ticks × 틱크기            ← 슬리피지

참조가 1,050 · 미니선물 1계약 기준 실측:

    CYBOS  편도 0.0098104%  →  수수료 0.206018pt + 슬립 0.04pt = **0.246018pt** (12,301원)
    CREON  편도 0.0019%     →  수수료 0.039900pt + 슬립 0.04pt = **0.079900pt** ( 3,995원)

**3.08배 차이다.** 그래서 채널을 감지해 쓰고, 어떤 세대로 계산했는지 행에 남긴다.
"""
import logging

logger = logging.getLogger("CHALLENGER")

#: 슬리피지 기본값(편도 틱). 사전등록 `VALIDATION_CAMPAIGN["gp_rule_cost"]` 와 같은 값이며
#: 캠페인 공통 가정(`slippage_ticks_per_side`)과도 일치한다.
DEFAULT_SLIP_TICKS_PER_SIDE = 1.0

#: 🔴 교체 대상이었던 키움 잔재 요율. 회귀 가드가 이 값의 부재를 검사한다.
LEGACY_KIWOOM_RATE = 1.5e-05


def _spec():
    """(채널명, 편도요율, 틱크기).

    🔴 **감지 로직을 여기서 또 만들지 않는다.** `config.settings` 가 이미
      `detect_broker_channel()` 을 **단일 원천**으로 두고 폴백·경고까지 처리한다
      (`BROKER_CHANNEL` / `BROKER_CHANNEL_SOURCE` / `FUTURES_COMMISSION_RATE`).
      초판이 `detect_broker_channel()` 을 직접 불렀다가 그 함수가 `(channel, source)`
      **튜플**을 돌려준다는 걸 놓쳐 매번 폴백으로 빠지고 채널명이 `UNKNOWN` 으로 찍혔다 —
      값은 우연히 맞았지만(폴백이 최댓값=CYBOS) **근거 표기가 거짓**이 됐다.
      감지 사본은 드리프트한다(539차 「스크립트가 상수를 자체 정의하고 있다」와 같은 교훈).
    """
    try:
        from config.settings import BROKER_CHANNEL, FUTURES_COMMISSION_RATE
        from config.constants import MINI_FUTURES_TICK_SIZE
        return (str(BROKER_CHANNEL), float(FUTURES_COMMISSION_RATE),
                float(MINI_FUTURES_TICK_SIZE))
    except Exception as exc:
        # 폴백은 **비싼 쪽**을 고른다. 싼 쪽으로 틀리면 가상손익이 조용히 부푼다.
        try:
            from config.constants import BROKER_CHANNEL_SPECS, MINI_FUTURES_TICK_SIZE
            rate = max(float(v["one_way_commission_rate"])
                       for v in BROKER_CHANNEL_SPECS.values())
            tick = float(MINI_FUTURES_TICK_SIZE)
        except Exception:
            rate, tick = 9.8104e-05, 0.02
        logger.warning("[CostModel] 채널 감지 실패(%s) — 보수적 폴백 요율 %.8f 사용", exc, rate)
        return "UNKNOWN", rate, tick


def cost_context(slip_ticks_per_side=None):
    """이번 계산이 쓴 비용 세대. **행에 같이 저장하라**(계측 4원칙 ④).

    Returns:
        dict(broker_channel, one_way_rate, tick_size, slip_ticks_per_side)
    """
    ch, rate, tick = _spec()
    slip = (DEFAULT_SLIP_TICKS_PER_SIDE if slip_ticks_per_side is None
            else float(slip_ticks_per_side))
    return {
        "broker_channel": ch,
        "one_way_rate": rate,
        "tick_size": tick,
        "slip_ticks_per_side": slip,
    }


def roundtrip_cost_pt(entry_price, exit_price, ctx=None):
    """왕복비용(pt). 수수료는 **진입가·청산가 각각**에 붙는다."""
    c = ctx or cost_context()
    try:
        ep = float(entry_price)
        xp = float(exit_price)
    except (TypeError, ValueError):
        return 0.0
    commission = (ep + xp) * c["one_way_rate"]          # = 2 × 평균가 × 요율
    slippage = 2.0 * c["slip_ticks_per_side"] * c["tick_size"]
    return commission + slippage


def calc_pnl_pt(direction, entry_price, exit_price, ctx=None):
    """방향 손익에서 왕복비용을 뺀 **순손익(pt)**.

    ⚠ 반환은 pt 다. 원화 환산은 **미니선물 50,000원/pt**(`MINI_FUTURES_PT_VALUE`)이며
      정규선물 250,000 이 아니다 — 소비자가 5배 틀리기 쉬운 지점이다.
    """
    c = ctx or cost_context()
    try:
        raw = (float(exit_price) - float(entry_price)) * int(direction)
    except (TypeError, ValueError):
        return 0.0
    return round(raw - roundtrip_cost_pt(entry_price, exit_price, c), 4)
