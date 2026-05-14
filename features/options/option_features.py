# features/options/option_features.py
"""
옵션 피처 계산기

PCRStore + 매크로 레짐을 결합해 ML 입력 피처를 생성한다.

반환 키:
  opt_pcr_norm       — PCR 정규화 [-1(콜우세), +1(풋우세)]
  opt_pcr_bearish    — 1.0 if PCR ≥ 1.2 (약세 신호)
  opt_pcr_bullish    — 1.0 if PCR ≤ 0.8 (강세 신호)
  opt_pcr_extreme    — 1.0 if PCR ≥ 1.5 (역발상 반등)
  opt_pcr_slope_norm — PCR 추세 정규화 [-1, +1]
  opt_available      — 1.0 if 실데이터
"""
import logging
from typing import Dict

import numpy as np

logger = logging.getLogger("OPTIONS")

# PCR 정규화 기준: [0.5, 1.5] → [-1, +1]
_PCR_MID  = 1.0
_PCR_HALF = 0.5   # PCR_MID ± PCR_HALF 범위를 [-1, +1]로 정규화

# slope 클리핑 범위
_SLOPE_CLIP = 0.3


class OptionFeatureCalculator:
    """
    PCRStore.get_features() → ML 입력 피처 변환

    사용:
        calc = OptionFeatureCalculator()
        opt_feats = calc.transform(pcr_store.get_features())
        feature_builder.build(bar, ..., option_data=opt_feats)
    """

    def transform(self, pcr_feats: Dict[str, float]) -> Dict[str, float]:
        """
        Args:
            pcr_feats: PCRStore.get_features() 반환값

        Returns:
            6개 정규화 피처 딕셔너리
        """
        pcr       = float(pcr_feats.get("pcr_current",  1.0) or 1.0)
        pcr_slope = float(pcr_feats.get("pcr_slope",    0.0) or 0.0)
        available = float(pcr_feats.get("pcr_available", 0.0) or 0.0)

        # PCR: 1.0을 중립으로 [-1, +1] 정규화
        pcr_norm = float(np.clip((pcr - _PCR_MID) / _PCR_HALF, -1.0, 1.0))

        # slope: ±0.3 범위 클리핑 후 정규화
        slope_norm = float(np.clip(pcr_slope / _SLOPE_CLIP, -1.0, 1.0))

        result = {
            "opt_pcr_norm":       round(pcr_norm,   4),
            "opt_pcr_bearish":    pcr_feats.get("pcr_bearish",  0.0),
            "opt_pcr_bullish":    pcr_feats.get("pcr_bullish",  0.0),
            "opt_pcr_extreme":    pcr_feats.get("pcr_extreme",  0.0),
            "opt_pcr_slope_norm": round(slope_norm, 4),
            "opt_available":      available,
        }

        logger.debug(
            "[OptFeat] PCR=%.3f(norm=%.2f) slope_norm=%.2f bearish=%s bullish=%s extreme=%s",
            pcr, pcr_norm, slope_norm,
            bool(result["opt_pcr_bearish"]),
            bool(result["opt_pcr_bullish"]),
            bool(result["opt_pcr_extreme"]),
        )
        return result

    @staticmethod
    def empty() -> Dict[str, float]:
        """PCRStore 미수집 시 안전 기본값"""
        return {
            "opt_pcr_norm":       0.0,
            "opt_pcr_bearish":    0.0,
            "opt_pcr_bullish":    0.0,
            "opt_pcr_extreme":    0.0,
            "opt_pcr_slope_norm": 0.0,
            "opt_available":      0.0,
        }
