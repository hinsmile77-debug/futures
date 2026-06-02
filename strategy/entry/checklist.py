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
        prev_bar_direction: int,
        time_zone: str,
        daily_loss_pct: float,
        min_confidence: float = 0.58,
        bear_exhaustion: float = 0.0,
        bull_exhaustion: float = 0.0,
        micro_regime: str = "혼합",
        disabled_gates: set = None,
    ) -> Dict:
        """
        Args:
            direction:       앙상블 방향 (+1/-1)
            confidence:      앙상블 신뢰도
            vwap_position:   VWAP 위치 (양수=위, 음수=아래)
            cvd_direction:   CVD 방향 (+1/-1)
            ofi_pressure:    OFI 압력 (+1/-1/0)
            foreign_call_net:   외인 콜 순매수
            foreign_put_net:    외인 풋 순매수
            prev_bar_direction: 직전 봉 방향 +1(양봉) / 0(도지) / -1(음봉)
            time_zone:          현재 시간대 코드
            daily_loss_pct:  당일 누적 손실률 (양수=손실)
            min_confidence:  레짐별 최소 신뢰도
            bear_exhaustion: 하락 압력 소진 강도 0.0~1.0 (LONG MR 분기용)
            bull_exhaustion: 상승 압력 소진 강도 0.0~1.0 (SHORT MR 분기용)
            micro_regime:    현재 미시 레짐 (탈진 레짐 시 Hurst 차단 무효화)
            disabled_gates:  UI 체크박스 OFF 항목의 내부 키 집합
                             (예: {"3_vwap", "6_foreign"}) — 해당 항목은 항상 통과 처리

        Returns:
            {pass_count, grade, checks, size_mult, auto_entry, entry_mode}
        """
        from collection.macro.micro_regime import REGIME_EXHAUSTION

        disabled = set(disabled_gates) if disabled_gates else set()

        # FLAT 신호는 방향 없음 → SHORT로 오분류되어 8/9 통과 후 A등급 AUTO진입이
        # 발생하는 버그를 차단한다. 반드시 즉시 X등급 반환해야 한다.
        if direction == DIRECTION_FLAT:
            logger.debug("[Checklist] FLAT 방향 → 즉시 X등급 (진입 금지)")
            return {
                "pass_count": 0,
                "grade":      "X",
                "checks":     {"1_signal": False},
                "size_mult":  0,
                "auto_entry": False,
                "entry_mode": "NO_ENTRY",
            }

        is_long = direction == DIRECTION_UP
        is_exhaustion_regime = (micro_regime == REGIME_EXHAUSTION)

        checks = {}
        entry_mode = "TREND_FOLLOW"

        # 1. 앙상블 신호 방향 확인
        checks["1_signal"] = "1_signal" in disabled or direction in (DIRECTION_UP, DIRECTION_DOWN)

        # 2. 최소 신뢰도 (탈진 레짐은 0.56으로 완화)
        min_conf_effective = 0.56 if is_exhaustion_regime else min_confidence
        checks["2_confidence"] = "2_confidence" in disabled or confidence >= min_conf_effective
        if not checks["2_confidence"]:
            logger.warning(
                "[Checklist] 신뢰도 미달 %.1f%% < %.1f%% → 강제 X등급",
                confidence * 100, min_conf_effective * 100,
            )
            return {
                "pass_count":        1,
                "grade":             "X",
                "checks":            checks,
                "size_mult":         0,
                "auto_entry":        False,
                "entry_mode":        entry_mode,
                "conf_check_failed": True,   # [P3] 신뢰도 차단 식별 플래그
            }

        # 3. VWAP 위치
        # LONG MR: VWAP 하방 1.5σ 초과 + 하락 압력 소진(bear_exhaustion) → 역추세 매수
        # SHORT MR: VWAP 상방 1.5σ 초과 + 상승 압력 소진(bull_exhaustion) → 역추세 매도
        if "3_vwap" in disabled:
            checks["3_vwap"] = True
        elif is_long:
            if vwap_position < -1.5 and bear_exhaustion > 0.0:
                checks["3_vwap"] = True
                entry_mode = "MEAN_REVERSION"
            else:
                checks["3_vwap"] = vwap_position > 0
        else:
            if vwap_position > 1.5 and bull_exhaustion > 0.0:
                checks["3_vwap"] = True
                entry_mode = "MEAN_REVERSION"
            else:
                checks["3_vwap"] = vwap_position < 0

        # 4. CVD 방향 (0 = 중립 → 방향 확인 불가 = 미통과)
        if "4_cvd" in disabled:
            checks["4_cvd"] = True
        elif is_long:
            checks["4_cvd"] = cvd_direction > 0
        else:
            checks["4_cvd"] = cvd_direction < 0

        # 5. OFI 압력 (0 = 중립 → 방향 확인 불가 = 미통과)
        if "5_ofi" in disabled:
            checks["5_ofi"] = True
        elif is_long:
            checks["5_ofi"] = ofi_pressure > 0
        else:
            checks["5_ofi"] = ofi_pressure < 0

        # 6. 외인 방향 (콜/풋 순매수 양수 AND 상대우위 — 둘 다 충족해야 통과)
        if "6_foreign" in disabled:
            checks["6_foreign"] = True
        elif is_long:
            checks["6_foreign"] = foreign_call_net > 0 and foreign_call_net > foreign_put_net
        else:
            checks["6_foreign"] = foreign_put_net > 0 and foreign_put_net > foreign_call_net

        # 7. 직전 봉 (도지=0은 양쪽 모두 불통과)
        if "7_prev_bar" in disabled:
            checks["7_prev_bar"] = True
        elif is_long:
            checks["7_prev_bar"] = prev_bar_direction == 1   # 양봉만
        else:
            checks["7_prev_bar"] = prev_bar_direction == -1  # 음봉만

        # 8. 시간 필터 (금지 구간 외)
        checks["8_time"] = "8_time" in disabled or time_zone not in ("EXIT_ONLY", "OTHER")

        # 9. 리스크 한도 (일일 손실 < 2%)
        checks["9_risk"] = "9_risk" in disabled or daily_loss_pct < 0.02

        pass_count = sum(1 for v in checks.values() if v)

        # CORE 3개(CVD·VWAP·OFI) 중 하나라도 ✗ → 즉시 X등급 (절대 원칙)
        core_fail = not checks["4_cvd"] or not checks["3_vwap"] or not checks["5_ofi"]
        if core_fail:
            failed = [k for k in ("3_vwap", "4_cvd", "5_ofi") if not checks[k]]
            # [CORE-DIAG] 탈락 원인 진단 — 데이터 문제 vs 로직 문제 구분용
            _diag_parts = []
            if not checks["3_vwap"]:
                _need = ">0 (LONG)" if is_long else "<0 (SHORT)"
                _diag_parts.append(
                    f"VWAP pos={vwap_position:+.3f} need {_need}"
                    + (f" bear_exh={bear_exhaustion:.2f}" if is_long else f" bull_exh={bull_exhaustion:.2f}")
                )
            if not checks["4_cvd"]:
                _need_cvd = ">0" if is_long else "<0"
                _diag_parts.append(f"CVD dir={cvd_direction:+d} need {_need_cvd}")
            if not checks["5_ofi"]:
                _need_ofi = ">0" if is_long else "<0"
                _diag_parts.append(f"OFI pres={ofi_pressure:+d} need {_need_ofi}")
            logger.warning(
                "[Checklist] CORE 피처 ✗ %s → 강제 X등급 (pass_count=%d) | %s",
                failed, pass_count, "  |  ".join(_diag_parts),
            )
            return {
                "pass_count": pass_count,
                "grade":      "X",
                "checks":     checks,
                "size_mult":  0,
                "auto_entry": False,
                "entry_mode": entry_mode,
            }

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
            "[Checklist] 통과 %d/9 → 등급 %s (자동=%s, 배수×%s, 모드=%s)",
            pass_count, grade, auto_entry, size_mult, entry_mode,
        )

        return {
            "pass_count": pass_count,
            "grade":      grade,
            "checks":     checks,
            "size_mult":  size_mult,
            "auto_entry": auto_entry,
            "entry_mode": entry_mode,
        }
