# challenger/variants/champion_tp1_skip_trail.py — 방안 E: 챔피언 미러 + TP1 스킵·트레일 단독
"""
감사 근거: docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md
  "P2 | TP1 부분청산 A/B | 챌린저 variant로 'TP1 스킵·트레일 단독' 버전 등록
   → 기존 인프라로 20일 병행 평가"

진입 신호는 챔피언(실거래 앙상블)의 그 분 확정 decision을 그대로 미러링한다.
다른 방안 A~D는 독자적인 알파 신호를 실험하지만, 이 variant는 진입 타이밍/방향을
챔피언과 동일하게 맞춰 "청산 규칙"만 격리해서 비교하기 위함이다 — 진입 알파 차이가
섞이면 TP1 부분청산 유무의 순수 효과를 판별할 수 없다.

청산 규칙 차이:
  챔피언(실거래) : TP1 도달 시 물량 일부 부분청산 (position_tracker.partial_close)
  이 variant     : TP1 도달을 부분청산 트리거로 쓰지 않고, 대신 트레일 스톱을 무장(arm)
                   한다. 이후 고점(롱)/저점(숏) 대비 TRAIL_MULT×ATR 되돌림 시 전량 청산.
                   TP2·SL·FORCE는 챔피언과 동일하게 유지(트레일이 그보다 더 유리한
                   가격에서 반드시 먼저 잡히지는 않으므로 안전망으로 유지).
"""
from typing import Dict, Any

from challenger.variants.base_challenger import BaseChallenger, ChallengerSignal, ExitReason


class ChampionTp1SkipTrailChallenger(BaseChallenger):
    challenger_id = "E_CHAMPION_TP1_SKIP_TRAIL"
    name_kr       = "챔피언미러 - TP1스킵 트레일단독"

    ATR_TP1_MULT = 1.0   # 트레일 무장(arm) 기준선 (챔피언 fallback과 동일 — 실제 TP1가는 entry_horizon마다 다르지만 여기선 무장 판단용 근사치)
    ATR_TP2_MULT = 1.5
    ATR_SL_MULT  = 1.5
    TRAIL_MULT   = 0.5   # 무장 후 되돌림 허용폭 (ATR 배수) — TP1~SL 폭(0.5~1.0 ATR)의 중간값

    def generate_signal(self, features, context):
        # type: (Dict[str, Any], Dict[str, Any]) -> ChallengerSignal
        ts       = context.get("ts", "")
        decision = context.get("decision") or {}

        direction  = int(decision.get("direction", 0) or 0)
        confidence = float(decision.get("confidence", 0.0) or 0.0)
        grade      = decision.get("grade", "X") or "X"

        entry_price = float(context.get("candle", {}).get("close", 0) or 0)
        return ChallengerSignal(
            ts            = ts,
            challenger_id = self.challenger_id,
            direction     = direction,
            confidence    = round(confidence, 4),
            grade         = grade,
            entry_price   = entry_price if direction != 0 else None,
            signal_meta   = {"mirrored_from": "champion_decision"},
        )

    def should_exit(self, trade, current_price, current_ts, atr=None):
        # type: (Any, float, str, float) -> Any
        if trade is None:
            return None

        atr_val = atr if atr else trade.atr_at_entry
        if not atr_val or atr_val <= 0:
            return None

        # 추적 고점/저점 갱신 (부분청산 없이 전량 포지션을 트레일링)
        if trade.direction == 1:
            trade.trail_extreme = max(trade.trail_extreme or trade.entry_price, current_price)
        else:
            trade.trail_extreme = min(trade.trail_extreme or trade.entry_price, current_price)

        tp1_arm_level = trade.entry_price + trade.direction * self.ATR_TP1_MULT * atr_val
        tp2 = trade.entry_price + trade.direction * self.ATR_TP2_MULT * atr_val
        sl  = trade.entry_price - trade.direction * self.ATR_SL_MULT  * atr_val

        armed = (
            (trade.direction == 1 and trade.trail_extreme >= tp1_arm_level)
            or (trade.direction == -1 and trade.trail_extreme <= tp1_arm_level)
        )

        if trade.direction == 1:
            if current_price >= tp2:
                return ExitReason.TP2
            if current_price <= sl:
                return ExitReason.SL
            if armed:
                trail_stop = trade.trail_extreme - self.TRAIL_MULT * atr_val
                if current_price <= trail_stop:
                    return ExitReason.TRAIL
        else:
            if current_price <= tp2:
                return ExitReason.TP2
            if current_price >= sl:
                return ExitReason.SL
            if armed:
                trail_stop = trade.trail_extreme + self.TRAIL_MULT * atr_val
                if current_price >= trail_stop:
                    return ExitReason.TRAIL

        return None
