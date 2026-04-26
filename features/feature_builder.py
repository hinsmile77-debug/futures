# features/feature_builder.py — 전체 피처 통합 빌더
"""
매분 실행되어 전체 피처 벡터를 조립합니다.

CORE 3개 (절대 교체 불가):
  - cvd_divergence  (CORE-1)
  - vwap_position   (CORE-2)
  - ofi_norm        (CORE-3)

수급 8개 + 옵션 12개 + 매크로 5개 + 동적 SHAP 풀
"""
import numpy as np
import logging
from typing import Dict, Any, Optional

from features.technical.cvd  import CVDCalculator
from features.technical.vwap import VWAPCalculator
from features.technical.ofi  import OFICalculator
from features.technical.atr  import ATRCalculator

logger = logging.getLogger("SIGNAL")


class FeatureBuilder:
    """매분 피처 벡터 빌드"""

    def __init__(self):
        self.cvd  = CVDCalculator(window=10)
        self.vwap = VWAPCalculator()
        self.ofi  = OFICalculator(window=5)
        self.atr  = ATRCalculator(period=14)

        # 최근 피처 캐시
        self._last_features: Dict[str, float] = {}

    def build(
        self,
        bar: Dict[str, Any],
        supply_demand: Optional[Dict] = None,
        option_data: Optional[Dict] = None,
        macro_data: Optional[Dict] = None,
    ) -> Dict[str, float]:
        """
        피처 벡터 조립

        Args:
            bar: {open, high, low, close, volume, buy_vol, sell_vol,
                  bid_price, ask_price, bid_qty, ask_qty}
            supply_demand: 수급 데이터 딕셔너리
            option_data:   옵션 플로우 데이터
            macro_data:    매크로 지표 데이터

        Returns:
            피처명 → 값 딕셔너리
        """
        features: Dict[str, float] = {}

        # ── CORE 피처 ──────────────────────────────────────────
        # CORE-1: CVD 다이버전스
        cvd_result = self.cvd.update_from_bar(
            close    = bar["close"],
            buy_vol  = bar.get("buy_vol", bar.get("volume", 0) / 2),
            sell_vol = bar.get("sell_vol", bar.get("volume", 0) / 2),
        )
        features["cvd_divergence"] = float(cvd_result["signal_strength"]
                                            * (-1 if cvd_result["divergence"] else 1))
        features["cvd_direction"]  = float(cvd_result["direction"])

        # CORE-2: VWAP 위치
        vwap_result = self.vwap.update(
            high   = bar["high"],
            low    = bar["low"],
            close  = bar["close"],
            volume = bar.get("volume", 1),
        )
        features["vwap_position"]  = float(vwap_result["position"])
        features["vwap"]           = float(vwap_result["vwap"])
        features["above_vwap"]     = float(vwap_result["above_vwap"])

        # CORE-3: OFI
        ofi_result = self.ofi.flush_minute()
        features["ofi_norm"]        = float(ofi_result["ofi_norm"])
        features["ofi_pressure"]    = float(ofi_result["pressure"])
        features["ofi_imbalance"]   = float(ofi_result["imbalance_ratio"])

        # ATR (손절 계산용 + 레짐)
        atr_result = self.atr.update(
            high  = bar["high"],
            low   = bar["low"],
            close = bar["close"],
        )
        features["atr"]       = float(atr_result["atr"])
        features["atr_ratio"] = float(atr_result["atr_ratio"])

        # ── 수급 피처 ──────────────────────────────────────────
        if supply_demand:
            for k, v in supply_demand.items():
                features[k] = float(v) if v is not None else 0.0

        # ── 옵션 피처 ──────────────────────────────────────────
        if option_data:
            for k, v in option_data.items():
                features[k] = float(v) if v is not None else 0.0

        # ── 매크로 피처 ────────────────────────────────────────
        if macro_data:
            for k, v in macro_data.items():
                features[k] = float(v) if v is not None else 0.0

        self._last_features = features
        logger.debug(f"[FeatureBuilder] {len(features)}개 피처 빌드 완료")
        return features

    def get_feature_vector(self, feature_names: list) -> np.ndarray:
        """지정된 피처명 순서대로 numpy 배열 반환"""
        return np.array([
            self._last_features.get(name, 0.0)
            for name in feature_names
        ], dtype=float)

    def reset_daily(self):
        """장 시작 시 일간 리셋"""
        self.cvd.reset_daily()
        self.vwap.reset_daily()
        self.ofi.reset_daily()
        self.atr.reset_daily()
        self._last_features = {}
        logger.info("[FeatureBuilder] 일간 리셋 완료")
