# features/supply_demand/herding.py — 군집 행동 (Herding) 지표
"""
개인 투자자의 군집 행동(herding)을 감지하여 역발상 신호 생성.

한국 시장 특성:
  개인 투자자 군집 매수 → 단기 과매수 → 역추세 하락 선행
  개인 투자자 군집 매도 → 단기 과매도 → 역추세 상승 선행
  (외국인/기관은 반대 방향으로 역이용)

군집 행동 지수 (HI — Herding Index):
  HI = |개인_순매수| / (|개인_순매수| + |기관_순매수| + |외인_순매수| + ε)
  HI → 1.0: 개인 거래가 지배 (군집 위험↑)
  HI → 0.0: 균형 상태

역발상 신호:
  HI > 0.7 AND 개인_순매수 > 0 → 단기 매도 신호 (과매수 해소 예상)
  HI > 0.7 AND 개인_순매수 < 0 → 단기 매수 신호 (과매도 해소 예상)
"""
import numpy as np
from collections import deque
from typing import Optional


class HerdingDetector:
    """투자자별 수급 기반 군집 행동 감지기"""

    # 군집 판단 임계값
    HERDING_THRESHOLD = 0.65    # HI > 0.65 → 군집 의심
    STRONG_THRESHOLD  = 0.80    # HI > 0.80 → 강한 군집

    def __init__(self, window: int = 10):
        """
        Args:
            window: 이동평균 창 (분 또는 수집 주기)
        """
        self.window = window
        self._hi_buf   = deque(maxlen=window)
        self._net_buf  = deque(maxlen=window)   # 개인 순매수 이동평균

    def compute(
        self,
        individual_net: float,   # 개인 순매수 (양=매수우위, 음=매도우위, 계약 수)
        institution_net: float,  # 기관 순매수
        foreign_net: float,      # 외국인 순매수
    ) -> dict:
        """
        군집 행동 지수 계산

        Args:
            individual_net:  개인 순매수량
            institution_net: 기관 순매수량
            foreign_net:     외국인 순매수량

        Returns:
            {herding_index, hi_ma, individual_net, herding_signal,
             contrarian_signal, strength, reason}
        """
        denom = abs(individual_net) + abs(institution_net) + abs(foreign_net) + 1e-9
        hi    = abs(individual_net) / denom
        hi    = float(np.clip(hi, 0.0, 1.0))

        self._hi_buf.append(hi)
        self._net_buf.append(individual_net)

        hi_ma  = float(np.mean(list(self._hi_buf)))
        net_ma = float(np.mean(list(self._net_buf)))

        # 군집 방향
        if individual_net > 0:
            herd_dir = 1    # 개인 군집 매수
        elif individual_net < 0:
            herd_dir = -1   # 개인 군집 매도
        else:
            herd_dir = 0

        # 역발상 신호 (개인 반대 방향)
        contrarian_signal = 0
        strength          = "없음"
        reason            = "군집 없음"

        if hi_ma >= self.STRONG_THRESHOLD:
            contrarian_signal = -herd_dir   # 강한 역발상
            strength          = "강함"
            reason = (f"강한 군집 (HI={hi_ma:.2f}) — "
                      f"{'개인매수' if herd_dir > 0 else '개인매도'} 집중 → 역발상")
        elif hi_ma >= self.HERDING_THRESHOLD:
            contrarian_signal = -herd_dir   # 보통 역발상
            strength          = "보통"
            reason = (f"군집 감지 (HI={hi_ma:.2f}) — "
                      f"{'개인매수' if herd_dir > 0 else '개인매도'}")
        else:
            reason = f"균형 상태 (HI={hi_ma:.2f})"

        # 외국인/기관 방향 확인 (smart money)
        smart_net = institution_net + foreign_net
        smart_dir = 1 if smart_net > 0 else (-1 if smart_net < 0 else 0)

        # 스마트 머니와 역발상이 일치하면 신호 강화
        if contrarian_signal != 0 and contrarian_signal == smart_dir:
            reason += " [스마트머니 동조 ✓]"

        return {
            "herding_index":      round(hi, 4),
            "hi_ma":              round(hi_ma, 4),    # CORE 피처값
            "individual_net":     individual_net,
            "institution_net":    institution_net,
            "foreign_net":        foreign_net,
            "smart_money_net":    smart_net,
            "herding_signal":     herd_dir,            # 군집 방향
            "contrarian_signal":  contrarian_signal,   # CORE 피처값 (역발상)
            "strength":           strength,
            "reason":             reason,
        }

    def reset_daily(self):
        self._hi_buf.clear()
        self._net_buf.clear()


if __name__ == "__main__":
    herd = HerdingDetector(window=10)

    print("=== 개인 군집 매수 시나리오 ===")
    for i in range(5):
        r = herd.compute(
            individual_net=+800,    # 개인 대량 매수
            institution_net=-200,   # 기관 매도
            foreign_net=-150,       # 외인 매도
        )
        print(f"[{i+1}] HI={r['herding_index']:.3f}, HI_ma={r['hi_ma']:.3f}, "
              f"역발상={r['contrarian_signal']:+d}, 강도={r['strength']}")
        print(f"     {r['reason']}")
