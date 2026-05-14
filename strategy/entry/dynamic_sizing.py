# strategy/entry/dynamic_sizing.py — 동적 포지션 사이징 (Dynamic Sizing)
"""
여러 신호를 종합하여 최종 포지션 사이즈를 결정.

입력:
  1. 적응형 켈리 (strategy/entry/adaptive_kelly.py)
  2. 변동성 표적화 배율 (vol_targeting.py)
  3. 메타 신뢰도 배율 (meta_confidence.py)
  4. 체크리스트 등급 (A/B/C)
  5. 시장 레짐

최종 사이즈:
  size = base_contracts
         × kelly_fraction
         × vol_mult
         × confidence_mult
         × grade_mult
         × regime_mult
  (상한: max_contracts, 하한: 1)

기대 효과: MDD -20%
"""
import numpy as np
import logging
from typing import Optional

logger = logging.getLogger("STRATEGY")


class DynamicSizer:
    """
    다중 팩터 결합 최종 포지션 사이저

    절대 원칙:
      - 최소 1계약, 최대 max_contracts
      - 급변장 (ATR > 2×) → 강제 사이즈 절반
      - 일일 손실 한도 도달 → 사이즈 0
    """

    # combined_fraction 최소 임계값 — 이 이하면 계약 수 계산 없이 차단
    # 7개 팩터 곱셈 연쇄 시 각자 "약간 낮음"이 지수적으로 수렴하는 현상 방지.
    # 0.15 = kelly 0.4 × vol 0.9 × conf 0.7 × B등급 0.5 × NEUTRAL 1.0 × 혼합 0.9 × ATR 1.0 ≈ 0.11
    # → C등급·횡보장·저신뢰도 복합 상황에서 소수 계약 강제 진입을 차단한다.
    MIN_COMBINED_FRACTION = 0.12

    # 체크리스트 등급 배율
    GRADE_MULT = {
        "A": 1.0,   # 6개 통과 → 100% 즉시
        "B": 0.5,   # 4~5개 → 50% 우선 (추가 진입 별도)
        "C": 0.3,   # 2~3개 → 30% 리스크 축소
    }

    # 레짐 배율
    REGIME_MULT = {
        "RISK_ON":  1.1,
        "NEUTRAL":  1.0,
        "RISK_OFF": 0.7,
    }

    # 미시 레짐 배율
    MICRO_REGIME_MULT = {
        "추세장":  1.1,
        "횡보장":  0.5,
        "급변장":  0.0,   # 강제 차단
        "혼합":    0.9,
    }

    def __init__(
        self,
        base_contracts: int   = 1,
        max_contracts:  int   = 5,
        daily_loss_limit: float = 5_000_000,   # 일일 손실 한도 (원)
    ):
        self.base_contracts   = base_contracts
        self.max_contracts    = max_contracts
        self.daily_loss_limit = daily_loss_limit

        self._daily_pnl       = 0.0
        self._halted          = False

    def compute(
        self,
        kelly_fraction:    float,   # 0 ~ 1 (adaptive_kelly 출력)
        vol_multiplier:    float,   # 변동성 표적화 배율
        confidence_mult:   float,   # 메타 신뢰도 배율
        grade:             str,     # "A" / "B" / "C"
        macro_regime:      str    = "NEUTRAL",   # RISK_ON / NEUTRAL / RISK_OFF
        micro_regime:      str    = "혼합",
        atr_ratio:         float  = 1.0,         # ATR / ATR_평균
        override_halt:     bool   = False,
    ) -> dict:
        """
        최종 포지션 사이즈 계산

        Returns:
            {contracts, size_fraction, breakdown, blocked, reason}
        """
        # 0. 일일 손실 한도 / Circuit Breaker 정지
        if self._halted and not override_halt:
            return self._blocked("일일 손실 한도 도달 — 당일 거래 정지")

        # 1. 미시 레짐 차단
        micro_mult = self.MICRO_REGIME_MULT.get(micro_regime, 0.9)
        if micro_mult == 0.0:
            return self._blocked(f"미시 레짐 차단: {micro_regime}")

        # 2. 급변장 ATR 과도
        atr_mult = 1.0
        if atr_ratio > 2.0:
            atr_mult = 0.5
            logger.warning(f"[DynSize] ATR급등({atr_ratio:.1f}×) → 사이즈 ÷2")
        elif atr_ratio > 1.5:
            atr_mult = 0.75

        # 3. 각 팩터 배율 수집
        grade_mult  = self.GRADE_MULT.get(grade, 0.5)
        regime_mult = self.REGIME_MULT.get(macro_regime, 1.0)

        # 4. 종합 사이즈 계산
        combined_fraction = (
            kelly_fraction
            * vol_multiplier
            * confidence_mult
            * grade_mult
            * regime_mult
            * micro_mult
            * atr_mult
        )

        # 5. 사이즈 과소 차단 — 7팩터 곱이 임계값 미만이면 진입 의미 없음
        if combined_fraction < self.MIN_COMBINED_FRACTION:
            logger.warning(
                f"[DynSize] fraction={combined_fraction:.4f} < {self.MIN_COMBINED_FRACTION} "
                f"(kelly={kelly_fraction:.2f}, vol={vol_multiplier:.2f}, conf={confidence_mult:.2f}, "
                f"{grade}/{micro_regime}) → 사이즈 과소 차단"
            )
            return self._blocked(f"사이즈 과소 (fraction={combined_fraction:.4f}) — 진입 의미 없음")

        # 6. 계약 수 변환
        raw_contracts = self.base_contracts * combined_fraction
        contracts     = int(np.clip(round(raw_contracts), 1, self.max_contracts))

        breakdown = {
            "kelly":       round(kelly_fraction, 3),
            "vol_mult":    round(vol_multiplier, 3),
            "conf_mult":   round(confidence_mult, 3),
            "grade_mult":  round(grade_mult, 3),
            "regime_mult": round(regime_mult, 3),
            "micro_mult":  round(micro_mult, 3),
            "atr_mult":    round(atr_mult, 3),
            "combined":    round(combined_fraction, 4),
        }

        logger.info(f"[DynSize] {grade}등급 → {contracts}계약 "
                    f"(kelly={kelly_fraction:.2f}, vol={vol_multiplier:.2f}, "
                    f"conf={confidence_mult:.2f}, micro={micro_regime})")

        return {
            "contracts":      contracts,
            "size_fraction":  round(combined_fraction, 4),
            "breakdown":      breakdown,
            "blocked":        False,
            "reason":         "정상",
        }

    def _blocked(self, reason: str) -> dict:
        return {
            "contracts":    0,
            "size_fraction": 0.0,
            "breakdown":    {},
            "blocked":      True,
            "reason":       reason,
        }

    def record_pnl(self, pnl_krw: float):
        """손익 기록 → 일일 한도 체크"""
        self._daily_pnl += pnl_krw
        if self._daily_pnl <= -abs(self.daily_loss_limit):
            self._halted = True
            logger.critical(f"[DynSize] 일일 손실 한도 도달: {self._daily_pnl:,.0f}원 → 거래 정지")

    def reset_daily(self):
        self._daily_pnl = 0.0
        self._halted    = False


if __name__ == "__main__":
    sizer = DynamicSizer(base_contracts=1, max_contracts=5)

    # A등급 추세장 시나리오
    r = sizer.compute(
        kelly_fraction=0.42, vol_multiplier=1.2, confidence_mult=0.85,
        grade="A", macro_regime="RISK_ON", micro_regime="추세장", atr_ratio=1.1,
    )
    print(f"[A등급 추세장] {r['contracts']}계약 | fraction={r['size_fraction']:.4f} | {r['reason']}")
    print(f"  breakdown: {r['breakdown']}")

    # B등급 횡보장 (신뢰도 낮음)
    r2 = sizer.compute(
        kelly_fraction=0.20, vol_multiplier=0.9, confidence_mult=0.55,
        grade="B", macro_regime="NEUTRAL", micro_regime="횡보장", atr_ratio=1.0,
    )
    print(f"[B등급 횡보장] {r2['contracts']}계약 | fraction={r2['size_fraction']:.4f}")

    # 급변장 차단
    r3 = sizer.compute(
        kelly_fraction=0.30, vol_multiplier=0.5, confidence_mult=0.6,
        grade="A", macro_regime="RISK_OFF", micro_regime="급변장", atr_ratio=2.5,
    )
    print(f"[급변장] blocked={r3['blocked']} | {r3['reason']}")
