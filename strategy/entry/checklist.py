# strategy/entry/checklist.py — 9개 진입 전 체크리스트
"""
9개 항목을 평가하여 통과 수와 등급을 결정합니다.

등급 기준:
  A: 6개 이상 → ×1.5 자동 진입
  B: 4~5개   → ×1.0 자동 진입
  C: 2~3개   → ×0.6 수동 확인
  X: 1개 이하 → 진입 금지
"""
import logging
from typing import Dict, Tuple

from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from config.settings import ENTRY_GRADE

logger = logging.getLogger("SIGNAL")


class EntryChecklist:
    """9개 진입 전 체크리스트"""

    def evaluate(
        self,
        direction: int,
        confidence: float,
        vwap_position: float,
        cvd_direction: int,
        ofi_pressure: int,
        foreign_call_net: float,
        foreign_put_net: float,
        prev_bar_bullish: bool,
        time_zone: str,
        daily_loss_pct: float,
        min_confidence: float = 0.58,
    ) -> Dict:
        """
        Args:
            direction:       앙상블 방향 (+1/-1)
            confidence:      앙상블 신뢰도
            vwap_position:   VWAP 위치 (양수=위, 음수=아래)
            cvd_direction:   CVD 방향 (+1/-1)
            ofi_pressure:    OFI 압력 (+1/-1/0)
            foreign_call_net: 외인 콜 순매수
            foreign_put_net:  외인 풋 순매수
            prev_bar_bullish: 직전 봉 양봉 여부
            time_zone:       현재 시간대 코드
            daily_loss_pct:  당일 누적 손실률 (양수=손실)
            min_confidence:  레짐별 최소 신뢰도

        Returns:
            {pass_count, grade, checks, size_mult, auto_entry}
        """
        is_long = direction == DIRECTION_UP

        checks = {}

        # 1. 앙상블 신호 방향 확인
        checks["1_signal"] = direction in (DIRECTION_UP, DIRECTION_DOWN)

        # 2. 최소 신뢰도
        checks["2_confidence"] = confidence >= min_confidence

        # 3. VWAP 위치
        if is_long:
            checks["3_vwap"] = vwap_position > 0
        else:
            checks["3_vwap"] = vwap_position < 0

        # 4. CVD 방향
        if is_long:
            checks["4_cvd"] = cvd_direction >= 0
        else:
            checks["4_cvd"] = cvd_direction <= 0

        # 5. OFI 압력
        if is_long:
            checks["5_ofi"] = ofi_pressure >= 0
        else:
            checks["5_ofi"] = ofi_pressure <= 0

        # 6. 외인 방향
        if is_long:
            # 콜 순매수 증가 (양수)
            checks["6_foreign"] = foreign_call_net > 0 or foreign_call_net > foreign_put_net
        else:
            # 풋 순매수 or 역발상
            checks["6_foreign"] = foreign_put_net > 0 or foreign_put_net > foreign_call_net

        # 7. 직전 봉
        if is_long:
            checks["7_prev_bar"] = prev_bar_bullish
        else:
            checks["7_prev_bar"] = not prev_bar_bullish

        # 8. 시간 필터 (금지 구간 외)
        checks["8_time"] = time_zone not in ("EXIT_ONLY", "OTHER")

        # 9. 리스크 한도 (일일 손실 < 2%)
        checks["9_risk"] = daily_loss_pct < 0.02

        pass_count = sum(1 for v in checks.values() if v)

        # 등급 결정
        if pass_count >= ENTRY_GRADE["A"]["min_pass"]:
            grade = "A"
        elif pass_count >= ENTRY_GRADE["B"]["min_pass"]:
            grade = "B"
        elif pass_count >= ENTRY_GRADE["C"]["min_pass"]:
            grade = "C"
        else:
            grade = "X"

        size_mult  = ENTRY_GRADE[grade]["size_mult"]
        auto_entry = ENTRY_GRADE[grade]["auto"]

        logger.info(
            f"[Checklist] 통과 {pass_count}/9 → 등급 {grade} "
            f"(자동={auto_entry}, 배수×{size_mult})"
        )

        return {
            "pass_count": pass_count,
            "grade":      grade,
            "checks":     checks,
            "size_mult":  size_mult,
            "auto_entry": auto_entry,
        }
