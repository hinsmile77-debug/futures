# challenger/variants/absorption.py — 방안 E: 호가 흡수 감지
"""
대량 지정가 매수가 시장가 매도를 흡수하는 패턴 = 분기점 가장 선행 신호.

흡수 조건 (3단계 순차 확인):
  STEP 1. 호가 잔량 감시 — ask_qty가 N초간 소진되지 않음
  STEP 2. 체결량 급증 — filled_qty_at_level > avg_filled × 2.0
  STEP 3. 가격 지지 — 연속 3분 이상 하락 저지

데이터 소스: Cybos CpSysDib.FutureJpBid (호가 잔량 실시간)

※ 방안 E는 구현 난이도가 가장 높음.
   Cybos FutureJpBid 호가 구독이 선행 구현되어 있지 않으면
   기능이 비활성화 상태(active=False)로 대기함.
"""
from collections import deque
from typing import Dict, Any, Optional

from challenger.variants.base_challenger import BaseChallenger, ChallengerSignal


class AbsorptionChallenger(BaseChallenger):
    challenger_id = "E_ABSORPTION"
    name_kr       = "흡수감지"

    FILLED_MULT    = 2.0   # 체결량 배수 임계값
    SUPPORT_BARS   = 3     # 가격 지지 확인 최소 분봉 수
    AVG_FILL_WIN   = 20    # 평균 체결량 계산 윈도우

    def __init__(self):
        super(AbsorptionChallenger, self).__init__()
        self._filled_buf   = deque(maxlen=self.AVG_FILL_WIN)
        self._support_cnt  = 0     # 연속 지지 봉 카운터
        self._support_level = None  # type: Optional[float]
        self._hoga_active  = False  # Cybos FutureJpBid 구독 여부

        # 호가 흡수 실시간 상태 (update_hoga()로 외부에서 주입)
        self._ask_wall_qty   = 0.0    # 최우선 매도호가 잔량
        self._filled_at_wall = 0.0    # 해당 레벨 체결량

    def update_hoga(self, ask_wall_qty, filled_at_wall):
        # type: (float, float) -> None
        """
        Cybos FutureJpBid 콜백에서 분리된 상태 업데이트용.
        (COM 콜백 내 emit/dynamicCall 금지 원칙: 상태 저장만 허용)
        """
        self._ask_wall_qty   = ask_wall_qty
        self._filled_at_wall = filled_at_wall
        self._hoga_active    = True

    def generate_signal(self, features, context):
        # type: (Dict[str, Any], Dict[str, Any]) -> ChallengerSignal
        ts          = context.get("ts", "")
        close_price = float(context.get("candle", {}).get("close", 0) or 0)
        low_price   = float(context.get("candle", {}).get("low", close_price) or close_price)
        volume      = float(context.get("candle", {}).get("volume", 0) or 0)

        self._filled_buf.append(volume)

        direction  = 0
        confidence = 0.0
        grade      = "X"
        meta       = {}

        # Cybos 호가 구독 미활성화 시 신호 없음
        if not self._hoga_active:
            return ChallengerSignal(
                ts=ts, challenger_id=self.challenger_id,
                direction=0, confidence=0.0, grade="X",
                entry_price=None,
                signal_meta={"status": "hoga_inactive"},
            )

        avg_fill = (sum(self._filled_buf) / len(self._filled_buf)
                    if self._filled_buf else 1.0)

        # STEP 2: 체결량 급증
        step2 = avg_fill > 0 and self._filled_at_wall > avg_fill * self.FILLED_MULT

        # STEP 1: 호가 잔량 유지 (벽이 존재하면 양수)
        step1 = self._ask_wall_qty > 0

        # STEP 3: 가격 지지 (지지선 설정 + 연속 확인)
        if self._support_level is None:
            self._support_level = low_price

        if low_price >= self._support_level:
            self._support_cnt += 1
        else:
            self._support_cnt  = 0
            self._support_level = low_price

        step3 = self._support_cnt >= self.SUPPORT_BARS

        if step1 and step2 and step3:
            absorption_ratio = (self._filled_at_wall / (self._ask_wall_qty + 1e-9))
            absorption_ratio = min(absorption_ratio, 1.0)

            confidence = 0.56 + absorption_ratio * 0.14   # 0.56~0.70
            direction  = 1
            grade      = self._grade_from_confidence(confidence)
            meta = {
                "ask_wall_qty":    round(self._ask_wall_qty, 0),
                "filled_at_wall":  round(self._filled_at_wall, 0),
                "avg_fill":        round(avg_fill, 1),
                "absorption_ratio": round(absorption_ratio, 3),
                "support_cnt":     self._support_cnt,
                "support_level":   round(self._support_level, 2),
            }

        return ChallengerSignal(
            ts            = ts,
            challenger_id = self.challenger_id,
            direction     = direction,
            confidence    = round(confidence, 4),
            grade         = grade,
            entry_price   = close_price if direction != 0 else None,
            signal_meta   = meta,
        )
