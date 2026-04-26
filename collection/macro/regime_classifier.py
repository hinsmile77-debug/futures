# collection/macro/regime_classifier.py — 시장 레짐 분류
"""
매크로 데이터를 기반으로 일 1회 시장 레짐을 분류합니다.
  RISK_ON:  글로벌 위험선호 (공격적 진입 허용)
  NEUTRAL:  중립 (표준 진입)
  RISK_OFF: 위험회피 (방어적 진입, 사이즈 축소)

분류 기준:
  VIX < 20 AND SP500 > 0  → RISK_ON
  VIX > 30 OR SP500 < -1% → RISK_OFF
  나머지                  → NEUTRAL
"""
import logging
from typing import Dict, Optional

from config.constants import REGIME_RISK_ON, REGIME_NEUTRAL, REGIME_RISK_OFF

logger = logging.getLogger("SYSTEM")


class RegimeClassifier:
    """매크로 기반 시장 레짐 분류기"""

    def classify(
        self,
        vix: float,
        sp500_chg_pct: float,
        nasdaq_chg_pct: float = 0.0,
        usd_krw_chg_pct: float = 0.0,
        us10y_chg: float = 0.0,
    ) -> Dict:
        """
        Args:
            vix:             VIX 공포지수
            sp500_chg_pct:   S&P500 선물 등락률 (%)
            nasdaq_chg_pct:  나스닥 선물 등락률 (%)
            usd_krw_chg_pct: 원/달러 변화율 (%)
            us10y_chg:       미국 10년물 금리 변화 (bp)

        Returns:
            {regime, score, factors, description}
        """
        score = 0  # 양수=RISK_ON, 음수=RISK_OFF

        factors = {}

        # VIX (가장 중요)
        if vix < 15:
            score += 2; factors["vix"] = f"VIX={vix:.1f} (극저공포)"
        elif vix < 20:
            score += 1; factors["vix"] = f"VIX={vix:.1f} (저공포)"
        elif vix > 30:
            score -= 2; factors["vix"] = f"VIX={vix:.1f} (고공포)"
        elif vix > 25:
            score -= 1; factors["vix"] = f"VIX={vix:.1f} (공포 상승)"
        else:
            factors["vix"] = f"VIX={vix:.1f} (중립)"

        # S&P500
        if sp500_chg_pct > 0.5:
            score += 1; factors["sp500"] = f"SP500={sp500_chg_pct:+.2f}% (상승)"
        elif sp500_chg_pct < -1.0:
            score -= 1; factors["sp500"] = f"SP500={sp500_chg_pct:+.2f}% (하락)"
        else:
            factors["sp500"] = f"SP500={sp500_chg_pct:+.2f}% (보합)"

        # 원/달러 (환율 상승 = 외인 이탈 압력)
        if usd_krw_chg_pct > 0.5:
            score -= 1; factors["usdkrw"] = f"USD/KRW +{usd_krw_chg_pct:.2f}% (외인 이탈)"
        elif usd_krw_chg_pct < -0.5:
            score += 1; factors["usdkrw"] = f"USD/KRW {usd_krw_chg_pct:.2f}% (외인 유입)"
        else:
            factors["usdkrw"] = f"USD/KRW {usd_krw_chg_pct:+.2f}% (중립)"

        # 레짐 결정
        if score >= 2:
            regime = REGIME_RISK_ON
        elif score <= -2:
            regime = REGIME_RISK_OFF
        else:
            regime = REGIME_NEUTRAL

        description = " | ".join(factors.values())

        logger.info(f"[Regime] {regime} (점수={score}) | {description}")

        return {
            "regime":      regime,
            "score":       score,
            "factors":     factors,
            "description": description,
        }

    def classify_micro(
        self,
        adx: float,
        atr_ratio: float,
    ) -> str:
        """
        미시 레짐 분류 (v6.5 — 매분 실행)

        ADX > 25, ATR < 1.5배 → 추세장
        ADX < 20, ATR < 1.0배 → 횡보장
        ATR > 2.0배           → 급변장
        나머지                → 혼합
        """
        from config.constants import (
            MICRO_REGIME_TREND, MICRO_REGIME_RANGE,
            MICRO_REGIME_VOLATILE, MICRO_REGIME_MIXED,
        )

        if atr_ratio > 2.0:
            return MICRO_REGIME_VOLATILE
        elif adx > 25 and atr_ratio < 1.5:
            return MICRO_REGIME_TREND
        elif adx < 20 and atr_ratio < 1.0:
            return MICRO_REGIME_RANGE
        else:
            return MICRO_REGIME_MIXED
