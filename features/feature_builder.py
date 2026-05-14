import logging
from typing import Any, Dict, Optional

import numpy as np

from features.technical.atr import ATRCalculator
from features.technical.cvd import CVDCalculator
from features.technical.cvd_exhaustion import CvdExhaustionCalculator
from features.technical.microprice import MicropriceCalculator
from features.technical.mlofi import MLOFICalculator
from features.technical.ofi import OFICalculator
from features.technical.ofi_reversal import OfiReversalCalculator
from features.technical.queue_dynamics import QueueDynamicsCalculator
from features.technical.toxicity import ToxicityCalculator
from features.technical.vwap import VWAPCalculator

logger = logging.getLogger("SIGNAL")
micro_log = logging.getLogger("MICRO")


class FeatureBuilder:
    """Assemble per-minute model features from bars and intraminute hoga updates."""

    def __init__(self):
        self.cvd = CVDCalculator(window=10)
        self.cvd_exhaustion_calc = CvdExhaustionCalculator()
        self.vwap = VWAPCalculator()
        self.ofi = OFICalculator(window=5)
        self.ofi_reversal_calc = OfiReversalCalculator()
        self.atr = ATRCalculator(period=14)
        self.microprice = MicropriceCalculator(window=5, max_levels=5)
        self.mlofi = MLOFICalculator(levels=5, window=5)
        self.queue = QueueDynamicsCalculator(window=20, minute_window=5)
        self.toxicity = ToxicityCalculator(window=20)
        self._last_features: Dict[str, float] = {}
        self._last_hoga_snapshot: Dict[str, Any] = {}
        self._micro_tick_count = 0
        self._micro_minute_count = 0
        # CORE 3종(CVD/VWAP/OFI) 연속 실패 카운터 — 3회 연속 시 ERROR 로그
        # 0으로 복구되면 이전 실패 구간이 끝났음을 의미한다.
        self._core_fail_streak: Dict[str, int] = {"cvd": 0, "vwap": 0, "ofi": 0}
        self._core_fail_notified: Dict[str, bool] = {"cvd": False, "vwap": False, "ofi": False}
        self._on_core_fail: Optional[Any] = None  # 외부 CB 경보 콜백 (main.py에서 주입)

    def update_hoga(
        self,
        bid1: float,
        ask1: float,
        bid_qty: int,
        ask_qty: int,
        snapshot: Optional[Dict[str, Any]] = None,
    ) -> None:
        bid_prices = list((snapshot or {}).get("bid_prices") or [bid1])
        ask_prices = list((snapshot or {}).get("ask_prices") or [ask1])
        bid_qtys = list((snapshot or {}).get("bid_qtys") or [bid_qty])
        ask_qtys = list((snapshot or {}).get("ask_qtys") or [ask_qty])

        self._last_hoga_snapshot = {
            "bid_prices": bid_prices,
            "ask_prices": ask_prices,
            "bid_qtys": bid_qtys,
            "ask_qtys": ask_qtys,
        }

        self.ofi.update_hoga(bid_price=bid1, bid_qty=bid_qty, ask_price=ask1, ask_qty=ask_qty)
        micro_tick = self.microprice.update_hoga(bid_prices, bid_qtys, ask_prices, ask_qtys)
        mlofi_tick = self.mlofi.update_hoga(bid_prices, bid_qtys, ask_prices, ask_qtys)
        queue_tick = self.queue.update_hoga(bid_qty=bid_qty, ask_qty=ask_qty)

        self._micro_tick_count += 1
        if self._micro_tick_count <= 20 or self._micro_tick_count % 100 == 0:
            micro_log.debug(
                "[MICRO-TICK] #%d bid1=%.2f/%d ask1=%.2f/%d mp=%s mlofi_tick=%s queue=%s",
                self._micro_tick_count,
                bid1,
                bid_qty,
                ask1,
                ask_qty,
                micro_tick,
                round(float(mlofi_tick), 4) if mlofi_tick is not None else None,
                queue_tick,
            )

    def build(
        self,
        bar: Dict[str, Any],
        supply_demand: Optional[Dict] = None,
        option_data: Optional[Dict] = None,
        macro_data: Optional[Dict] = None,
    ) -> Dict[str, float]:
        features: Dict[str, float] = {}

        # bar 필드 안전 추출 — 직접 키 접근 시 KeyError 방지, None 전파 방지
        close = float(bar.get("close") or 0.0)
        high  = float(bar.get("high")  or close)
        low   = float(bar.get("low")   or close)
        vol   = float(bar.get("volume") or 0.0)
        # buy_vol/sell_vol: key 존재하지만 값이 None인 경우 get() fallback이 무시되므로
        # 명시적 None 체크로 처리한다.
        _bv = bar.get("buy_vol")
        _sv = bar.get("sell_vol")
        buy_vol  = float(_bv) if _bv is not None else vol / 2.0
        sell_vol = float(_sv) if _sv is not None else vol / 2.0

        try:
            cvd_result = self.cvd.update_from_bar(
                close=close, buy_vol=buy_vol, sell_vol=sell_vol,
            )
            features["cvd_divergence"] = float(
                cvd_result["signal_strength"] * (-1 if cvd_result["divergence"] else 1)
            )
            features["cvd_direction"] = float(cvd_result["direction"])
            features["cvd"]           = float(cvd_result.get("cvd", 0.0))
            features["cvd_slope"]     = float(cvd_result.get("cvd_slope", 0.0))
            self._core_fail_streak["cvd"] = 0
            self._core_fail_notified["cvd"] = False
        except Exception as _exc:
            self._core_fail_streak["cvd"] += 1
            streak = self._core_fail_streak["cvd"]
            logger.warning("[FeatureBuilder] CVD 오류 (연속 %d회) — 기본값 사용: %s", streak, _exc)
            if streak >= 3 and not self._core_fail_notified["cvd"]:
                logger.error("[CORE 경보] CVD %d회 연속 실패 — 신호 소멸 위험. 파이프라인 점검 필요.", streak)
                self._core_fail_notified["cvd"] = True
                if callable(self._on_core_fail):
                    self._on_core_fail("CVD", streak)
            features.update({"cvd_divergence": 0.0, "cvd_direction": 0.0,
                             "cvd": 0.0, "cvd_slope": 0.0})

        try:
            exh_result = self.cvd_exhaustion_calc.compute(
                cvd_raw   = features.get("cvd", 0.0),
                cvd_slope = features.get("cvd_slope", 0.0),
                volume    = vol,
            )
            features["cvd_exhaustion"]        = float(exh_result["exhaustion"])
            features["cvd_exhaustion_signal"] = float(exh_result["exhaustion_signal"])
        except Exception as _exc:
            logger.warning("[FeatureBuilder] CVD exhaustion 오류 — 기본값 사용: %s", _exc)
            features.update({"cvd_exhaustion": 0.0, "cvd_exhaustion_signal": 0.0})

        try:
            vwap_result = self.vwap.update(
                high=high, low=low, close=close, volume=vol or 1,
            )
            features["vwap_position"] = float(vwap_result["position"])
            features["vwap"]          = float(vwap_result["vwap"])
            features["above_vwap"]    = float(vwap_result["above_vwap"])
            self._core_fail_streak["vwap"] = 0
            self._core_fail_notified["vwap"] = False
        except Exception as _exc:
            self._core_fail_streak["vwap"] += 1
            streak = self._core_fail_streak["vwap"]
            logger.warning("[FeatureBuilder] VWAP 오류 (연속 %d회) — 기본값 사용: %s", streak, _exc)
            if streak >= 3 and not self._core_fail_notified["vwap"]:
                logger.error("[CORE 경보] VWAP %d회 연속 실패 — 기관 알고리즘 기준선 소멸 위험.", streak)
                self._core_fail_notified["vwap"] = True
                if callable(self._on_core_fail):
                    self._on_core_fail("VWAP", streak)
            features.update({"vwap_position": 0.0, "vwap": 0.0, "above_vwap": 0.0})

        try:
            ofi_result = self.ofi.flush_minute()
            features["ofi_norm"]      = float(ofi_result["ofi_norm"])
            features["ofi_pressure"]  = float(ofi_result["pressure"])
            features["ofi_imbalance"] = float(ofi_result["imbalance_ratio"])
            features["ofi_raw"]       = float(ofi_result["ofi_raw"])
            self._core_fail_streak["ofi"] = 0
            self._core_fail_notified["ofi"] = False
        except Exception as _exc:
            self._core_fail_streak["ofi"] += 1
            streak = self._core_fail_streak["ofi"]
            logger.warning("[FeatureBuilder] OFI 오류 (연속 %d회) — 기본값 사용: %s", streak, _exc)
            if streak >= 3 and not self._core_fail_notified["ofi"]:
                logger.error("[CORE 경보] OFI %d회 연속 실패 — 1~3분 선행신호 소멸 위험.", streak)
                self._core_fail_notified["ofi"] = True
                if callable(self._on_core_fail):
                    self._on_core_fail("OFI", streak)
            features.update({"ofi_norm": 0.0, "ofi_pressure": 0.0,
                             "ofi_imbalance": 0.0, "ofi_raw": 0.0})

        try:
            ofi_rev = self.ofi_reversal_calc.compute(
                ofi_raw    = features.get("ofi_raw", 0.0),
                avg_volume = vol or 1.0,
            )
            features["ofi_reversal_speed"]  = float(ofi_rev["reversal_speed"])
            features["ofi_reversal_signal"] = float(ofi_rev["signal"])
        except Exception as _exc:
            logger.warning("[FeatureBuilder] OFI reversal 오류 — 기본값 사용: %s", _exc)
            features.update({"ofi_reversal_speed": 0.0, "ofi_reversal_signal": 0.0})
        features["avg_volume"] = vol

        try:
            microprice_result = self.microprice.flush_minute()
            features["microprice"]            = float(microprice_result["microprice"])
            features["microprice_bias"]       = float(microprice_result["mp_bias"])
            features["microprice_slope"]      = float(microprice_result["mp_slope"])
            features["microprice_depth_bias"] = float(microprice_result["depth_bias"])
        except Exception as _exc:
            logger.warning("[FeatureBuilder] Microprice 오류 — 기본값 사용: %s", _exc)
            features.update({"microprice": 0.0, "microprice_bias": 0.0,
                             "microprice_slope": 0.0, "microprice_depth_bias": 0.0})

        try:
            mlofi_result = self.mlofi.flush_minute()
            features["mlofi_norm"]     = float(mlofi_result["mlofi_norm"])
            features["mlofi_pressure"] = float(mlofi_result["mlofi_pressure"])
            features["mlofi_slope"]    = float(mlofi_result["mlofi_slope"])
        except Exception as _exc:
            logger.warning("[FeatureBuilder] MLOFI 오류 — 기본값 사용: %s", _exc)
            features.update({"mlofi_norm": 0.0, "mlofi_pressure": 0.0, "mlofi_slope": 0.0})

        try:
            queue_result = self.queue.flush_minute()
            features["queue_signal"]          = float(queue_result["queue_signal_mean"])
            features["queue_signal_ma"]       = float(queue_result["queue_signal_ma"])
            features["queue_momentum"]        = float(queue_result["queue_momentum"])
            features["queue_depletion_speed"] = float(queue_result["queue_depletion_speed"])
            features["queue_refill_rate"]     = float(queue_result["queue_refill_rate"])
            features["imbalance_slope"]       = float(queue_result["imbalance_slope"])
            features["cancel_add_ratio"]      = float(queue_result["cancel_add_ratio"])
        except Exception as _exc:
            logger.warning("[FeatureBuilder] QueueDynamics 오류 — 기본값 사용: %s", _exc)
            features.update({"queue_signal": 0.0, "queue_signal_ma": 0.0,
                             "queue_momentum": 0.0, "queue_depletion_speed": 0.0,
                             "queue_refill_rate": 0.0, "imbalance_slope": 0.0,
                             "cancel_add_ratio": 0.0})

        try:
            atr_result = self.atr.update(high=high, low=low, close=close)
            features["atr"]       = float(atr_result["atr"])
            features["atr_ratio"] = float(atr_result["atr_ratio"])
        except Exception as _exc:
            logger.warning("[FeatureBuilder] ATR 오류 — 기본값 사용: %s", _exc)
            features.update({"atr": 0.0, "atr_ratio": 1.0})

        try:
            bid1 = float(bar.get("bid1") or 0.0)
            ask1 = float(bar.get("ask1") or 0.0)
            tick_size = 0.05
            spread_ticks = max((ask1 - bid1) / tick_size, 0.0) if bid1 > 0 and ask1 > 0 else 0.0
            toxicity_result = self.toxicity.update(
                atr_ratio=features.get("atr_ratio", 1.0),
                spread_ticks=spread_ticks,
                mlofi_norm=features.get("mlofi_norm", 0.0),
                queue_depletion_speed=features.get("queue_depletion_speed", 0.0),
                cancel_add_ratio=features.get("cancel_add_ratio", 0.0),
            )
            features["spread_ticks"]          = float(spread_ticks)
            features["toxicity_score"]        = float(toxicity_result["toxicity_score"])
            features["toxicity_score_ma"]     = float(toxicity_result["toxicity_score_ma"])
            features["toxicity_atr_stress"]   = float(toxicity_result["atr_stress"])
            features["toxicity_spread_stress"] = float(toxicity_result["spread_stress"])
            features["toxicity_flow_stress"]  = float(toxicity_result["flow_stress"])
            features["toxicity_queue_stress"] = float(toxicity_result["queue_stress"])
            features["toxicity_cancel_stress"] = float(toxicity_result["cancel_stress"])
            features["toxicity_regime_code"]  = float(
                2 if toxicity_result["toxicity_regime"] == "toxic"
                else 1 if toxicity_result["toxicity_regime"] == "warning"
                else 0
            )
        except Exception as _exc:
            logger.warning("[FeatureBuilder] Toxicity 오류 — 기본값 사용: %s", _exc)
            features.update({"spread_ticks": 0.0, "toxicity_score": 0.0,
                             "toxicity_score_ma": 0.0, "toxicity_atr_stress": 0.0,
                             "toxicity_spread_stress": 0.0, "toxicity_flow_stress": 0.0,
                             "toxicity_queue_stress": 0.0, "toxicity_cancel_stress": 0.0,
                             "toxicity_regime_code": 0.0})

        if supply_demand:
            for k, v in supply_demand.items():
                features[k] = float(v) if v is not None else 0.0

        if option_data:
            for k, v in option_data.items():
                features[k] = float(v) if v is not None else 0.0

        if macro_data:
            for k, v in macro_data.items():
                features[k] = float(v) if v is not None else 0.0

        self._micro_minute_count += 1
        micro_log.debug(
            "[MICRO-MINUTE] #%d ts=%s close=%.2f mp=%.4f bias=%.6f slope=%.6f depth_bias=%.4f "
            "mlofi_norm=%.6f mlofi_pressure=%.0f mlofi_slope=%.6f "
            "queue_signal=%.4f queue_ma=%.4f queue_momentum=%.4f depletion=%.4f refill=%.4f "
            "imbalance_slope=%.6f cancel_add=%.4f toxicity=%.4f tox_ma=%.4f",
            self._micro_minute_count,
            bar.get("ts"),
            float(bar.get("close", 0.0)),
            features["microprice"],
            features["microprice_bias"],
            features["microprice_slope"],
            features["microprice_depth_bias"],
            features["mlofi_norm"],
            features["mlofi_pressure"],
            features["mlofi_slope"],
            features["queue_signal"],
            features["queue_signal_ma"],
            features["queue_momentum"],
            features["queue_depletion_speed"],
            features["queue_refill_rate"],
            features["imbalance_slope"],
            features["cancel_add_ratio"],
            features["toxicity_score"],
            features["toxicity_score_ma"],
        )

        self._last_features = features
        logger.debug("[FeatureBuilder] built %d features", len(features))
        return features

    def get_feature_vector(self, feature_names: list) -> np.ndarray:
        return np.array([self._last_features.get(name, 0.0) for name in feature_names], dtype=float)

    def get_last_hoga_snapshot(self) -> Dict[str, Any]:
        return dict(self._last_hoga_snapshot)

    def reset_daily(self) -> None:
        self.cvd.reset_daily()
        self.cvd_exhaustion_calc.reset_daily()
        self.vwap.reset_daily()
        self.ofi.reset_daily()
        self.ofi_reversal_calc.reset_daily()
        self.atr.reset_daily()
        self.microprice.reset_daily()
        self.mlofi.reset_daily()
        self.queue.reset_daily()
        self.toxicity.reset_daily()
        self._last_features = {}
        self._last_hoga_snapshot = {}
        self._micro_tick_count = 0
        self._micro_minute_count = 0
        logger.info("[FeatureBuilder] daily reset complete")
