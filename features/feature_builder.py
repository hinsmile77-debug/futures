import datetime
import logging
import math
from collections import deque
from typing import Any, Dict, Optional

import numpy as np

from features.technical.atr import ATRCalculator
from features.technical.volume_profile import VolumeProfileCalculator
from features.technical.cvd import CVDCalculator
from features.technical.cvd_exhaustion import CvdExhaustionCalculator
from features.technical.microprice import MicropriceCalculator
from features.technical.mlofi import MLOFICalculator
from features.technical.ofi import OFICalculator
from features.technical.ofi_reversal import OfiReversalCalculator
from features.technical.queue_dynamics import QueueDynamicsCalculator
from features.technical.toxicity import ToxicityCalculator
from features.supply_demand.vpin import VPINCalculator
from features.technical.vwap import VWAPCalculator
from features.technical.hurst_exponent import calculate_hurst
from features.technical.trend_efficiency import calculate_trend_efficiency
from features.technical.kyle_lambda import KyleLambdaCalculator
from features.technical.multi_timeframe import MultiTimeframeAnalyzer
from features.technical.round_number import nearest_round_distance_symmetric
from features.technical.realized_vol import RealizedVolCalculator
from features.technical.expiry import compute_expiry_features
from config.constants import MINI_FUTURES_TICK_SIZE as _DEFAULT_TICK_SIZE  # [235차] 미니선물 전용 기본값 0.02
from utils.error_policy import ErrorLevel, classify_exception
from config.settings import (
    HORIZON_THRESHOLDS, HURST_WINDOW_N, HURST_MAX_LAG,
    HURST_WARMUP_COLDSTART_MIN, HURST_WARMUP_LAG_FLOOR, HURST_WARMUP_LAG_RATIO,
    TREND_EFFICIENCY_WINDOW, KYLE_LAMBDA_WINDOW, RV_IV_WINDOW,
    CHASE_FILTER_LOOKBACK_MIN, REGIME_EXHAUSTION_LOOKBACK_MIN,
)

logger = logging.getLogger("SIGNAL")
micro_log = logging.getLogger("MICRO")


class FeatureBuilder:
    """Assemble per-minute model features from bars and intraminute hoga updates."""

    def __init__(self):
        # [235차] 종목코드(미니/일반선물) 기반 동적 tick_size.
        # 기본값은 미니선물(0.02); connect_broker 완료 후 set_tick_size()로 재확정된다.
        self._tick_size: float = _DEFAULT_TICK_SIZE
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
        self.vpin_calc = VPINCalculator(bucket_size=1000)
        self.kyle_lambda_calc = KyleLambdaCalculator(window=KYLE_LAMBDA_WINDOW)
        self.rv_calc = RealizedVolCalculator(window=RV_IV_WINDOW)
        self.multi_timeframe = MultiTimeframeAnalyzer()
        self._last_features: Dict[str, float] = {}
        self._last_hoga_snapshot: Dict[str, Any] = {}
        self._micro_tick_count = 0
        self._micro_minute_count = 0
        # CORE 3종(CVD/VWAP/OFI) 연속 실패 카운터 — 3회 연속 시 ERROR 로그
        # 0으로 복구되면 이전 실패 구간이 끝났음을 의미한다.
        self._core_fail_streak: Dict[str, int] = {"cvd": 0, "vwap": 0, "ofi": 0}
        self._core_fail_notified: Dict[str, bool] = {"cvd": False, "vwap": False, "ofi": False}
        self._on_core_fail: Optional[Any] = None  # 외부 CB 경보 콜백 (main.py에서 주입)
        self._close_history: deque = deque(maxlen=HURST_WINDOW_N)  # Hurst 계산용 종가 버퍼
        # CVD 모노톤 비율 계산용 — 20구간(21개 포인트) 이력
        self._cvd_history: deque = deque(maxlen=21)
        # 방향성 고도화 피처용
        self._ema5: float = 0.0
        self._ema20: float = 0.0
        self._ema_initialized: bool = False
        self._vol_profile = VolumeProfileCalculator(n=60, bins=20)
        # 개선 3 추가 방향성 피처용 버퍼
        self._vol_history: deque = deque(maxlen=10)   # volume_acceleration용
        self._vwap_history: deque = deque(maxlen=10)  # VWAP 이동 속도용
        self._prev_day_same_hour_ret: float = 0.0     # 전일 동시간대 수익률 (daily_close에서 갱신)
        self._prev_day_close_buf: Dict[str, float] = {}  # {ts: close} 전일 전체 버퍼

    def set_tick_size(self, tick_size: float) -> None:
        """[235차] 종목코드 확정 후 틱 사이즈 주입 — spread_ticks 계산 정확도 보정.

        미니선물 0.02pt vs 일반선물 0.05pt 차이로 spread_ticks가 2.5배 왜곡됨.
        connect_broker() 완료 후 get_contract_spec(code)["tick_size"]로 호출한다.
        """
        ts = float(tick_size)
        if ts <= 0:
            return
        self._tick_size = ts
        logger.info("[FeatureBuilder] tick_size 갱신: %.4f (spread_ticks 계산 기준)", ts)

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

    def update_tick(self, price: float, volume: float, is_buy: Optional[bool] = None) -> None:
        """체결 틱마다 VPIN 버킷 누적 (main.py:_on_tick_price_update에서 호출)."""
        if price <= 0 or volume <= 0:
            return
        self.vpin_calc.update_tick(price=price, volume=volume, is_buy=is_buy)

    def build(
        self,
        bar: Dict[str, Any],
        supply_demand: Optional[Dict] = None,
        option_data: Optional[Dict] = None,
        macro_data: Optional[Dict] = None,
        basis_data: Optional[Dict] = None,
        micro_regime: str = "혼합",
    ) -> Dict[str, float]:
        features: Dict[str, float] = {}
        recoverable_errors = 0
        degraded = False

        def _mark_feature_error(exc: Exception, default_level: ErrorLevel = ErrorLevel.RECOVERABLE) -> None:
            nonlocal recoverable_errors, degraded
            level = classify_exception(exc, default=default_level)
            if level == ErrorLevel.FATAL:
                degraded = True
            if level in (ErrorLevel.RECOVERABLE, ErrorLevel.DEGRADED):
                recoverable_errors += 1
            if level == ErrorLevel.DEGRADED:
                degraded = True

        # bar 필드 안전 추출 — 직접 키 접근 시 KeyError 방지, None 전파 방지
        close = float(bar.get("close") or 0.0)
        high  = float(bar.get("high")  or close)
        low   = float(bar.get("low")   or close)
        vol   = float(bar.get("volume") or 0.0)
        # buy_vol/sell_vol: key 존재하지만 값이 None인 경우 get() fallback이 무시되므로
        # 명시적 None 체크로 처리한다.
        # buy_vol/sell_vol 없을 때 vol/2 fallback은 delta=0 → CVD 고정 → cvd_divergence 이진화.
        # 가격 기반(고저종) 추정으로 교체하여 과거 데이터에서도 의미 있는 CVD 생성.
        _bv = bar.get("buy_vol")
        _sv = bar.get("sell_vol")
        if _bv is not None and _sv is not None:
            buy_vol  = float(_bv)
            sell_vol = float(_sv)
        else:
            _rng = max(high - low, 1e-9)
            buy_vol  = vol * max(close - low,  0.0) / _rng
            sell_vol = vol * max(high - close, 0.0) / _rng

        try:
            cvd_result = self.cvd.update_from_bar(
                close=close, buy_vol=buy_vol, sell_vol=sell_vol,
            )
            # cvd_divergence: -1~+1 연속값
            # 다이버전스(가격↑CVD↓ 또는 가격↓CVD↑) → 음수, 동방향 → 양수
            features["cvd_divergence"] = float(
                -cvd_result["signal_strength"] if cvd_result["divergence"]
                else cvd_result["signal_strength"]
            )
            features["cvd_direction"]   = float(cvd_result["direction"]) * 0.5
            # cvd/cvd_slope 절대값 → 일중 max 대비 정규화값으로 교체 (Phase 3-A)
            features["cvd"]             = float(cvd_result.get("cvd_norm", 0.0))
            features["cvd_slope"]       = float(cvd_result.get("cvd_slope_norm", 0.0))
            self._core_fail_streak["cvd"] = 0
            self._core_fail_notified["cvd"] = False
        except Exception as _exc:
            _mark_feature_error(_exc)
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

        # CVD 모노톤 비율 — 최근 20구간 중 CVD가 증가한 비율 (0.0~1.0)
        # GBM 장기 학습용: 추세 지속성을 포인트 스냅샷이 아닌 시계열로 표현
        _cvd_val = float(features.get("cvd", 0.0))
        self._cvd_history.append(_cvd_val)
        _ch_len = len(self._cvd_history)
        if _ch_len >= 2:
            _up = sum(
                1 for _i in range(1, _ch_len)
                if self._cvd_history[_i] > self._cvd_history[_i - 1]
            )
            features["cvd_monotone_ratio"] = float(_up) / float(_ch_len - 1)
        else:
            features["cvd_monotone_ratio"] = 0.5  # 초기 중립값

        try:
            exh_result = self.cvd_exhaustion_calc.compute(
                cvd_raw   = features.get("cvd", 0.0),    # 이미 cvd_norm [-1,1]
                cvd_slope = features.get("cvd_slope", 0.0),  # 이미 cvd_slope_norm
                volume    = vol,
            )
            features["bear_exhaustion"]        = float(exh_result["bear_exhaustion"])
            features["bull_exhaustion"]        = float(exh_result["bull_exhaustion"])
            features["bear_exhaustion_signal"] = float(exh_result["bear_exhaustion_signal"])
            features["bull_exhaustion_signal"] = float(exh_result["bull_exhaustion_signal"])
            features["cvd_exhaustion"]         = float(exh_result["exhaustion"])        # deprecated
            features["cvd_exhaustion_signal"]  = float(exh_result["exhaustion_signal"]) # deprecated
        except Exception as _exc:
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] CVD exhaustion 오류 — 기본값 사용: %s", _exc)
            features.update({
                "bear_exhaustion": 0.0, "bull_exhaustion": 0.0,
                "bear_exhaustion_signal": 0.0, "bull_exhaustion_signal": 0.0,
                "cvd_exhaustion": 0.0, "cvd_exhaustion_signal": 0.0,
            })

        try:
            vwap_result = self.vwap.update(
                high=high, low=low, close=close, volume=vol or 1,
            )
            features["vwap_position"] = float(vwap_result["position"])
            # vwap 절대값 제거 — vwap_position/above_vwap으로 완전 대체 가능
            # (절대가격이 StandardScaler μ와 드리프트 시 z폭발, Phase 2-D)
            features["above_vwap"]    = float(vwap_result["above_vwap"])
            self._core_fail_streak["vwap"] = 0
            self._core_fail_notified["vwap"] = False
        except Exception as _exc:
            _mark_feature_error(_exc)
            self._core_fail_streak["vwap"] += 1
            streak = self._core_fail_streak["vwap"]
            logger.warning("[FeatureBuilder] VWAP 오류 (연속 %d회) — 기본값 사용: %s", streak, _exc)
            if streak >= 3 and not self._core_fail_notified["vwap"]:
                logger.error("[CORE 경보] VWAP %d회 연속 실패 — 기관 알고리즘 기준선 소멸 위험.", streak)
                self._core_fail_notified["vwap"] = True
                if callable(self._on_core_fail):
                    self._on_core_fail("VWAP", streak)
            features.update({"vwap_position": 0.0, "above_vwap": 0.0})

        # ofi_raw: features 미저장(② 제거) — GBM z-score 폭발 방지.
        # avg_vol 기반 ±3배 클리핑 후 로컬 변수로만 유지 → reversal_calc에 전달.
        # OfiReversalChallenger는 features["ofi_raw"] 의존성으로 비활성화됨
        # (향후 챌린저 ofi_raw 독립 계산으로 리팩토링 예정).
        _ofi_raw_val = 0.0
        try:
            ofi_result = self.ofi.flush_minute()
            _clip_bound = max(float(vol or 1.0), 1.0) * 3.0
            _ofi_raw_val = float(np.clip(ofi_result["ofi_raw"], -_clip_bound, _clip_bound))
            features["ofi_norm"]      = float(ofi_result["ofi_norm"])
            features["ofi_pressure"]  = float(ofi_result["pressure"])
            features["ofi_imbalance"] = float(ofi_result["imbalance_ratio"])
            self._core_fail_streak["ofi"] = 0
            self._core_fail_notified["ofi"] = False
        except Exception as _exc:
            _mark_feature_error(_exc)
            self._core_fail_streak["ofi"] += 1
            streak = self._core_fail_streak["ofi"]
            logger.warning("[FeatureBuilder] OFI 오류 (연속 %d회) — 기본값 사용: %s", streak, _exc)
            if streak >= 3 and not self._core_fail_notified["ofi"]:
                logger.error("[CORE 경보] OFI %d회 연속 실패 — 1~3분 선행신호 소멸 위험.", streak)
                self._core_fail_notified["ofi"] = True
                if callable(self._on_core_fail):
                    self._on_core_fail("OFI", streak)
            features.update({"ofi_norm": 0.0, "ofi_pressure": 0.0, "ofi_imbalance": 0.0})

        try:
            ofi_rev = self.ofi_reversal_calc.compute(
                ofi_raw    = _ofi_raw_val,   # 클리핑된 로컬값 사용 (speed 폭발 방지)
                avg_volume = vol or 1.0,
            )
            features["ofi_reversal_speed"]   = float(ofi_rev["reversal_speed"])
            features["bull_reversal_signal"] = float(ofi_rev["bull_reversal_signal"])
            # bear_reversal_signal 삭제 (일평균 10봉/일 희소 이진 신호 — 재학습 기여 없음, 260617)
        except Exception as _exc:
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] OFI reversal 오류 — 기본값 사용: %s", _exc)
            features.update({
                "ofi_reversal_speed":   0.0,
                "bull_reversal_signal": 0.0,
            })
        features["bar_volume"] = float(vol)
        _vh = list(self._vol_history)
        features["avg_volume"] = float(sum(_vh) / len(_vh)) if _vh else float(vol)

        try:
            microprice_result = self.microprice.flush_minute()
            # microprice 절대값 제거 — microprice_bias/slope/depth_bias로 완전 대체 가능
            # (절대가격이 StandardScaler μ와 드리프트 시 z폭발, Phase 2-C)
            features["microprice_bias"]       = float(microprice_result["mp_bias"])
            features["microprice_slope"]      = float(microprice_result["mp_slope"])
            features["microprice_depth_bias"] = float(microprice_result["depth_bias"])
        except Exception as _exc:
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] Microprice 오류 — 기본값 사용: %s", _exc)
            features.update({"microprice_bias": 0.0,
                             "microprice_slope": 0.0, "microprice_depth_bias": 0.0})

        try:
            mlofi_result = self.mlofi.flush_minute()
            features["mlofi_norm"]     = float(mlofi_result["mlofi_norm"])
            features["mlofi_pressure"] = float(mlofi_result["mlofi_pressure"])
            features["mlofi_slope"]    = float(mlofi_result["mlofi_slope"])
        except Exception as _exc:
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] MLOFI 오류 — 기본값 사용: %s", _exc)
            features.update({"mlofi_norm": 0.0, "mlofi_pressure": 0.0, "mlofi_slope": 0.0})

        try:
            queue_result = self.queue.flush_minute()
            features["queue_signal"]                  = float(queue_result["queue_signal_mean"])
            features["queue_signal_ma"]               = float(queue_result["queue_signal_ma"])
            features["queue_momentum"]                = float(queue_result["queue_momentum"])
            # 절대값 속도 → 총량 대비 비율로 교체 (Phase 3-B, 유동성 수준 독립)
            features["queue_depletion_speed"]         = float(queue_result["queue_depletion_ratio"])
            features["queue_refill_rate"]             = float(queue_result["queue_refill_ratio"])
            # 방향 강도: 양수=매수압(매도호가 고갈), 음수=매도압(매수호가 고갈) [-1,1]
            features["queue_directional_depletion"]   = float(queue_result["queue_directional_depletion"])
            features["imbalance_slope"]               = float(queue_result["imbalance_slope"])
            features["cancel_add_ratio"]              = float(queue_result["cancel_add_ratio"])
            # [380차] ToxicityGate 전용 무방향 취소폭주 지표 — cancel_add_ratio(부호 있는
            # 평균)와 달리 bid/ask 절대값 합산이라 반대부호 상쇄가 없다.
            features["cancel_churn_ratio"]            = float(queue_result["cancel_churn_ratio"])
        except Exception as _exc:
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] QueueDynamics 오류 — 기본값 사용: %s", _exc)
            features.update({"queue_signal": 0.0, "queue_signal_ma": 0.0,
                             "queue_momentum": 0.0, "queue_depletion_speed": 0.5,
                             "queue_refill_rate": 0.5, "queue_directional_depletion": 0.0,
                             "imbalance_slope": 0.0, "cancel_add_ratio": 0.0,
                             "cancel_churn_ratio": 0.0})

        # VPIN — update_tick()이 매 체결 틱마다 누적한 값을 그대로 읽기만 함(버킷 미완성 시
        # 직전 완성 버킷값 유지, bucket_size=1000계약 미달 시 0.0).
        features["vpin"] = float(self.vpin_calc.get_current_vpin())

        # Kyle's Lambda — 분봉 단위(close·buy_vol·sell_vol)만으로 계산, 틱 배선 불필요.
        # 틱 사이즈로 정규화(브로커·미니/일반선물 tick_size 차이 흡수) 후 안전 클리핑.
        try:
            kyle_result = self.kyle_lambda_calc.update(close=close, buy_vol=buy_vol, sell_vol=sell_vol)
            features["kyle_lambda"] = float(np.clip(
                kyle_result["kyle_lambda"] / self._tick_size, -5.0, 5.0
            ))
        except Exception as _exc:
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] Kyle's Lambda 오류 — 기본값 사용: %s", _exc)
            features["kyle_lambda"] = 0.0

        try:
            atr_result = self.atr.update(high=high, low=low, close=close)
            features["atr"]       = float(atr_result["atr"])
            features["atr_ratio"] = float(atr_result["atr_ratio"])
        except Exception as _exc:
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] ATR 오류 — 기본값 사용: %s", _exc)
            features.update({"atr": 0.0, "atr_ratio": 1.0})

        _prev_atr = float(self._last_features.get("atr", 0.0))
        _cur_atr  = features.get("atr", 0.0)
        # ATR 급변 시 unbounded 폭발 방지 — 학습 μ≈0.003, σ≈0.063 기준 ±50% 클리핑
        _raw_expansion = (_cur_atr - _prev_atr) / (_prev_atr + 1e-9) if _prev_atr > 1e-6 else 0.0
        features["atr_expansion_rate"] = float(np.clip(_raw_expansion, -0.5, 0.5))

        # Hurst Exponent — 317차 3단계 워밍업 스케줄(n=버퍼 크기, reset_daily 후 경과 분봉수):
        #   ① n<HURST_WARMUP_COLDSTART_MIN: 미신뢰 구간 → H=0.5 + hurst_ready=False
        #      (237차 자동진입 차단 유지 — max_lag 20→9 축소로 콜드스타트가 40→18분으로
        #      의도치 않게 줄던 것을 복원)
        #   ② COLDSTART<=n<HURST_WINDOW_N: 적응형 max_lag=max(FLOOR,round(n*RATIO))
        #      (n_min 스윕 실측: 이 시점 bias가 이미 구 운영값(N=60/max_lag=20)보다 낫다)
        #   ③ n>=HURST_WINDOW_N: 검증된 정상 운영값(HURST_MAX_LAG) 고정
        if close > 0:
            self._close_history.append(close)
        _n_buf = len(self._close_history)
        try:
            if _n_buf < HURST_WARMUP_COLDSTART_MIN:
                features["hurst"] = 0.5
                features["hurst_ready"] = False
            else:
                if _n_buf < HURST_WINDOW_N:
                    _lag_eff = max(HURST_WARMUP_LAG_FLOOR, round(_n_buf * HURST_WARMUP_LAG_RATIO))
                else:
                    _lag_eff = HURST_MAX_LAG
                # 317차 후속: 잔여 편향(n=90에서 -0.044) 보정을 상수이동·선형
                # de-shrinkage 두 방식 모두 시도했으나, 60거래일 실측 검증에서 둘 다
                # FalsePass를 14.4%→30~33%로 악화시켜(실제 횡보장 분봉이 합성데이터의
                # H_true=0.3만큼 깊지 않은 경우가 많아, 보정이 그 구간까지 과도하게
                # 밀어올림) 채택 보류 — 원시 H 그대로 사용(dev_memory 317차 항목 참조).
                features["hurst"] = calculate_hurst(list(self._close_history), max_lag=_lag_eff)
                features["hurst_ready"] = True
        except Exception as _exc:
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] Hurst 오류 — 기본값 0.5 사용: %s", _exc)
            features["hurst"] = 0.5
            features["hurst_ready"] = False

        # Trend Efficiency Ratio(Kaufman) — Hurst와 취지(추세 지속성)는 겹치나 계산방식이
        # 달라(경로비율 vs variance-scaling) 상관 1이 아닐 것으로 기대되는 보완 신호.
        features["trend_efficiency"] = calculate_trend_efficiency(
            list(self._close_history), window=TREND_EFFICIENCY_WINDOW,
        )

        # [343차] 연장 추격 필터용 signed 확장폭 — (현재가 - N분전 종가) / ATR.
        # 부호는 연장 방향(양수=상승 연장, 음수=하락 연장)을 그대로 인코딩해
        # EntryChecklist가 신규 진입 방향과 비교(추격 여부 판정)할 수 있게 한다.
        # 워밍업 구간(버퍼 부족)이나 atr<=0이면 0.0(체크 자동 통과) 반환.
        _ch_ext = list(self._close_history)
        _atr_now = features.get("atr", 0.0)
        if len(_ch_ext) > CHASE_FILTER_LOOKBACK_MIN and _atr_now > 1e-6:
            _close_n_ago = _ch_ext[-(CHASE_FILTER_LOOKBACK_MIN + 1)]
            features["price_extension_atr"] = float(
                np.clip((close - _close_n_ago) / _atr_now, -10.0, 10.0)
            )
        else:
            features["price_extension_atr"] = 0.0

        # [379차] RegimeExhaustionGate용 느린(60분) 연장폭 — price_extension_atr과
        # 동일 산식이나 룩백만 60분으로 늘려 여러 다리에 걸쳐 서서히 진행된 탈진을
        # 포착한다. 0723 딥다이브: 직전 10분 룩백(price_extension_atr)은 11:41 SHORT
        # 진입 시점에 이미 안정돼 chase 미감지였으나, 그 전 90분간의 하락은 컸음 —
        # 10분 룩백 하나로는 못 잡는 "느린 탈진"을 별도 신호로 분리.
        if len(_ch_ext) > REGIME_EXHAUSTION_LOOKBACK_MIN and _atr_now > 1e-6:
            _close_60m_ago = _ch_ext[-(REGIME_EXHAUSTION_LOOKBACK_MIN + 1)]
            features["price_extension_atr_60m"] = float(
                np.clip((close - _close_60m_ago) / _atr_now, -10.0, 10.0)
            )
        else:
            features["price_extension_atr_60m"] = 0.0

        # 마디가(Round Number) 거리 — 방향 인자 없이 상/하 최근접 레벨 중 더 가까운 쪽만 사용
        # (nearest_round_distance()는 direction 인자가 필요해 피처 생성 시점엔 사용 불가).
        # 상태 없는 순수 함수라 reset_daily() 대상 아님.
        features["round_number_distance"] = nearest_round_distance_symmetric(close)

        try:
            bid1 = float(bar.get("bid1") or 0.0)
            ask1 = float(bar.get("ask1") or 0.0)
            spread_ticks = max((ask1 - bid1) / self._tick_size, 0.0) if bid1 > 0 and ask1 > 0 else 0.0
            toxicity_result = self.toxicity.update(
                atr_ratio=features.get("atr_ratio", 1.0),
                spread_ticks=spread_ticks,
                mlofi_norm=features.get("mlofi_norm", 0.0),
                queue_depletion_ratio=features.get("queue_depletion_speed", 0.5),
                cancel_churn_ratio=features.get("cancel_churn_ratio", 0.0),
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
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] Toxicity 오류 — 기본값 사용: %s", _exc)
            features.update({"spread_ticks": 0.0, "toxicity_score": 0.0,
                             "toxicity_score_ma": 0.0, "toxicity_atr_stress": 0.0,
                             "toxicity_spread_stress": 0.0, "toxicity_flow_stress": 0.0,
                             "toxicity_queue_stress": 0.0, "toxicity_cancel_stress": 0.0,
                             "toxicity_regime_code": 0.0})

        if supply_demand:
            _INV_LOG_COLS = {
                "foreign_futures_net", "foreign_call_net", "foreign_put_net",
                "retail_futures_net", "institution_futures_net",
                "program_arb_net", "program_non_arb_net", "foreign_retail_divergence",
            }
            for k, v in supply_demand.items():
                _fv = float(v) if v is not None else 0.0
                if k in _INV_LOG_COLS:
                    # 계약수 단위 원시값 → 로그 압축: ±1000계약≈0.69, ±20000계약≈3.0
                    features[k] = float(np.sign(_fv) * np.log1p(abs(_fv) / 1000.0))
                else:
                    features[k] = _fv

        if option_data:
            for k, v in option_data.items():
                features[k] = float(v) if v is not None else 0.0

        # [260704 감사 P2] 선물-현물 베이시스 — main.py의 BasisCalculator가 계산해 전달.
        if basis_data:
            for k, v in basis_data.items():
                features[k] = float(v)

        # rv_iv_spread(328차) — RV(실현변동성) - IV(내재변동성) 스프레드.
        # IV 측은 Cybos OptionMst 개별종목 IV 필드(108)가 미검증 "추정" 단계라
        # 대신 main.py가 이미 실시간 검증·운영 중인 VKOSPI(KRX 공식 지수, basis_data 위에서
        # 병합된 "vkospi"/"vkospi_ready")를 IV 프록시로 재사용한다(features/technical/
        # realized_vol.py 모듈 docstring 참조).
        try:
            _rv = self.rv_calc.update(close)
            _vkospi = features.get("vkospi", 0.0)
            _vkospi_ready = features.get("vkospi_ready", 0.0) > 0.0
            features["realized_vol_ann"] = _rv["realized_vol_ann"]
            if _rv["ready"] and _vkospi_ready and _vkospi > 0:
                features["rv_iv_spread"] = _rv["realized_vol_ann"] - _vkospi
                features["rv_iv_spread_ready"] = True
            else:
                features["rv_iv_spread"] = 0.0
                features["rv_iv_spread_ready"] = False
        except Exception as _exc:
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] rv_iv_spread 오류 — 기본값 사용: %s", _exc)
            features["realized_vol_ann"] = 0.0
            features["rv_iv_spread"] = 0.0
            features["rv_iv_spread_ready"] = False

        # macro_quality_{available,stale,age_sec,fallback_used}는 아래 quality_macro_* 로 별도 저장
        # → merge 시 제외하여 managed feature set 중복 방지
        _MACRO_QUALITY_SKIP = {
            "macro_quality_available", "macro_quality_stale",
            "macro_quality_age_sec", "macro_quality_fallback_used",
        }
        if macro_data:
            for k, v in macro_data.items():
                if k not in _MACRO_QUALITY_SKIP:
                    features[k] = float(v) if v is not None else 0.0

        opt_available = float((option_data or {}).get("opt_available", 0.0) or 0.0)
        macro_available = float((macro_data or {}).get("macro_quality_available", 1.0 if macro_data else 0.0) or 0.0)
        supply_available = float((supply_demand or {}).get("quality_investor_supported", 1.0 if supply_demand else 0.0) or 0.0)
        macro_stale = float((macro_data or {}).get("macro_quality_stale", 0.0) or 0.0)
        macro_age_sec = float((macro_data or {}).get("macro_quality_age_sec", 0.0) or 0.0)
        macro_fallback = float((macro_data or {}).get("macro_quality_fallback_used", 0.0) or 0.0)
        investor_stale = float((supply_demand or {}).get("quality_investor_stale", 0.0) or 0.0)
        # quality_investor_age_sec: 학습 분포는 0~180초 범위.
        # 09:00 첫 파이프라인은 첫 fetch 이전이라 ~840초 → z=+45.70 극단값 발생.
        # 5분(300s) 상한 적용 — 그 이상은 quality_investor_stale=1.0이 이미 커버.
        investor_age_sec = min(
            float((supply_demand or {}).get("quality_investor_age_sec", 0.0) or 0.0),
            300.0,
        )
        if recoverable_errors > 0:
            degraded = True
        quality_penalty = (
            recoverable_errors * 0.08
            + (0.2 if degraded else 0.0)
            + (0.12 if macro_stale > 0.0 else 0.0)
            + (0.12 if investor_stale > 0.0 else 0.0)
            + (0.10 if macro_fallback > 0.0 else 0.0)
            + (0.08 if macro_available < 1.0 else 0.0)
            + (0.08 if supply_available < 1.0 else 0.0)
            + (0.06 if opt_available < 1.0 else 0.0)
        )
        quality_penalty = min(0.85, quality_penalty)
        features["feature_degraded"] = 1.0 if degraded else 0.0
        features["feature_quality_score"] = round(max(0.0, 1.0 - quality_penalty), 4)
        features["quality_option_available"] = opt_available
        features["quality_macro_available"] = macro_available
        features["quality_supply_available"] = supply_available
        features["quality_macro_stale"] = macro_stale
        features["quality_macro_age_sec"] = macro_age_sec
        features["quality_macro_fallback_used"] = macro_fallback
        features["quality_investor_stale"] = investor_stale
        features["quality_investor_age_sec"] = investor_age_sec / 300.0

        # ── 저변동성 인식 피처 ──────────────────────────────────────
        # threshold_feasibility: 현재 ATR이 1m threshold를 초과할 수 있는가
        #   < 1.0 → ATR < threshold → 대부분의 분봉이 FLAT 구간 (저변동성)
        #   = 1.0 → ATR ≈ threshold → UP/DN/FL 균형 구간
        #   > 1.0 → ATR > threshold → UP/DN 라벨 빈번 (고변동성)
        # micro_regime_code: 이전 분 레짐 분류값 (1분 lag 허용 — 레짐 전환은 느림)
        #   0=횡보장(FLAT 우세) 1=혼합 2=추세장 3=탈진 4=급변장
        _atr_val   = max(float(features.get("atr", 0.0)), 0.01)
        _thresh_pt = max(HORIZON_THRESHOLDS.get("1m", 0.0005) * max(close, 1.0), 1e-9)
        features["threshold_feasibility"] = round(_atr_val / _thresh_pt, 4)
        features["micro_regime_code"] = {
            "횡보장": 0.0,
            "혼합":   1.0,
            "추세장": 2.0,
            "탈진":   3.0,
            "급변장": 4.0,
        }.get(micro_regime, 1.0)

        self._micro_minute_count += 1
        try:
            micro_log.debug(
                "[MICRO-MINUTE] #%d ts=%s close=%.2f bias=%.6f slope=%.6f depth_bias=%.4f "
                "mlofi_norm=%.6f mlofi_pressure=%.0f mlofi_slope=%.6f "
                "queue_signal=%.4f queue_ma=%.4f queue_momentum=%.4f depletion=%.4f refill=%.4f "
                "imbalance_slope=%.6f cancel_add=%.4f toxicity=%.4f tox_ma=%.4f",
                self._micro_minute_count,
                bar.get("ts"),
                float(bar.get("close", 0.0)),
                features.get("microprice_bias", 0.0),
                features.get("microprice_slope", 0.0),
                features.get("microprice_depth_bias", 0.0),
                features.get("mlofi_norm", 0.0),
                features.get("mlofi_pressure", 0.0),
                features.get("mlofi_slope", 0.0),
                features.get("queue_signal", 0.0),
                features.get("queue_signal_ma", 0.0),
                features.get("queue_momentum", 0.0),
                features.get("queue_depletion_speed", 0.0),
                features.get("queue_refill_rate", 0.0),
                features.get("imbalance_slope", 0.0),
                features.get("cancel_add_ratio", 0.0),
                features.get("toxicity_score", 0.0),
                features.get("toxicity_score_ma", 0.0),
            )
        except Exception:
            pass

        # ── 시간대 피처 ─────────────────────────────────────────
        _ts_str = str(bar.get("ts") or "")
        try:
            _ts_dt = datetime.datetime.strptime(_ts_str[:19], "%Y-%m-%d %H:%M:%S")
            _mkt   = _ts_dt.replace(hour=9, minute=0, second=0, microsecond=0)
            _mod   = max(0, min(389, int((_ts_dt - _mkt).total_seconds() / 60)))
            features["time_sin"]          = math.sin(2.0 * math.pi * _mod / 390.0)
            features["time_cos"]          = math.cos(2.0 * math.pi * _mod / 390.0)
            features["is_open_volatile"]  = 1.0 if _mod < 30 else 0.0
            features["is_close_volatile"] = 1.0 if _mod > 360 else 0.0
            # [260704 감사 §6-3 순위9] 만기 구조 더미 — time_sin/cos가 못 잡는 달력 효과
            features.update(compute_expiry_features(_ts_dt))
        except Exception:
            features["time_sin"]          = 0.0
            features["time_cos"]          = 1.0
            features["is_open_volatile"]  = 0.0
            features["is_close_volatile"] = 0.0
            features.update({
                "is_weekly_witching": 0.0, "is_monthly_witching": 0.0,
                "is_monthly_expiry_week": 0.0, "is_month_end_rebalance": 0.0,
            })

        # ── 가격 모멘텀 ─────────────────────────────────────────
        _ch = list(self._close_history)
        _n  = len(_ch)
        features["ret_1m"]  = float(np.clip(
            (_ch[-1] - _ch[-2])  / (_ch[-2]  + 1e-9) if _n >= 2  else 0.0, -0.01, 0.01))
        features["ret_5m"]  = float(np.clip(
            (_ch[-1] - _ch[-6])  / (_ch[-6]  + 1e-9) if _n >= 6  else 0.0, -0.02, 0.02))
        features["ret_15m"] = float(np.clip(
            (_ch[-1] - _ch[-16]) / (_ch[-16] + 1e-9) if _n >= 16 else 0.0, -0.05, 0.05))

        # ── 멀티 타임프레임 추세(이산값) ───────────────────────────
        # ret_5m/15m(연속 수익률)과 달리 -1/0/+1 레짐 이산화 — GBM에 보완적 표현 기대.
        # push_1m_candle()이 내부에서 5분봉·15분봉을 자동 집계하므로 매 확정 1분봉마다 1회만
        # 호출하면 됨(build()가 이미 그 호출 빈도).
        try:
            _open = float(bar.get("open") or close)
            mtf_result = self.multi_timeframe.push_1m_candle(
                open_=_open, high=high, low=low, close=close, volume=vol,
            )
            features["multi_timeframe_5m"]  = float(mtf_result["trend_5m"])
            features["multi_timeframe_15m"] = float(mtf_result["trend_15m"])
        except Exception as _exc:
            _mark_feature_error(_exc)
            logger.warning("[FeatureBuilder] MultiTimeframe 오류 — 기본값 사용: %s", _exc)
            features.update({"multi_timeframe_5m": 0.0, "multi_timeframe_15m": 0.0})

        # ── EMA cross ────────────────────────────────────────────
        if close > 0:
            if not self._ema_initialized:
                self._ema5  = close
                self._ema20 = close
                self._ema_initialized = True
            else:
                self._ema5  = self._ema5  * (1.0 - 2.0 / 6.0)  + close * (2.0 / 6.0)
                self._ema20 = self._ema20 * (1.0 - 2.0 / 21.0) + close * (2.0 / 21.0)
        features["ema_cross"] = (self._ema5 - self._ema20) / (self._ema20 + 1e-9)

        # ── 볼린저 밴드 위치 ─────────────────────────────────────
        if _n >= 20:
            _sma20 = sum(_ch[-20:]) / 20.0
            _std20 = math.sqrt(sum((x - _sma20) ** 2 for x in _ch[-20:]) / 20.0)
            _bb_rng = 4.0 * _std20 + 1e-9   # bb_upper - bb_lower = 4σ
            features["bb_position"] = (close - (_sma20 - 2.0 * _std20)) / _bb_rng
        else:
            features["bb_position"] = 0.5

        # ── CVD delta 고도화 (Bull/Bear Volume 분해) ─────────────
        _rng_hilo = max(high - low, 1e-9)
        _bull_v   = vol * max(close - low,  0.0) / _rng_hilo
        _bear_v   = vol * max(high - close, 0.0) / _rng_hilo
        features["cvd_delta_norm"] = (_bull_v - _bear_v) / (vol + 1e-9)

        # ── 개선 3 추가 방향성 피처 ─────────────────────────────
        # 거래량 가속도 (volume acceleration)
        self._vol_history.append(vol)
        _vl = list(self._vol_history)
        _nv = len(_vl)
        if _nv >= 6:
            _vol_recent = sum(_vl[-3:]) / 3.0
            _vol_prev   = sum(_vl[-6:-3]) / 3.0
            features["volume_acceleration"] = float(np.clip(
                (_vol_recent - _vol_prev) / (_vol_prev + 1e-9), -3.0, 3.0
            ))
        else:
            features["volume_acceleration"] = 0.0

        # VWAP 포지션 5분 변화량 (vwap_momentum)
        # features["vwap"]는 Phase 2-D에서 제거됨 → vwap_position(정규화값)으로 대체
        _vwap_cur = features.get("vwap_position", 0.0)
        self._vwap_history.append(_vwap_cur)
        _vh = list(self._vwap_history)
        if len(_vh) >= 5:
            features["vwap_momentum"] = float(np.clip(_vh[-1] - _vh[-5], -2.0, 2.0))
        else:
            features["vwap_momentum"] = 0.0

        # 전일 동시간대 수익률 (main.py daily_close에서 _prev_day_same_hour_ret 갱신)
        features["prev_day_same_hour_ret"] = self._prev_day_same_hour_ret

        # ── Volume Profile (POC / Value Area) ───────────────────
        try:
            vp = self._vol_profile.update(high=high, low=low, close=close, volume=vol)
            features["poc_distance"]  = vp["poc_distance"]
            features["in_value_area"] = vp["in_value_area"]
            features["va_bandwidth"]  = vp["va_bandwidth"]
            features["poc_above"]     = vp["poc_above"]
        except Exception as _exc:
            _mark_feature_error(_exc)
            features.update({"poc_distance": 0.0, "in_value_area": 0.5,
                              "va_bandwidth": 0.0, "poc_above": 0.5})

        features["entry_ok"] = 1.0 if (
            features.get("toxicity_score", 1.0)        < 0.6 and
            features.get("feature_quality_score", 0.0) > 0.7 and
            features.get("spread_ticks", 99.0)         <= 1.0
        ) else 0.0

        self._last_features = features
        logger.debug("[FeatureBuilder] built %d features", len(features))
        return features

    def set_prev_day_closes(self, close_map: Dict[str, float]) -> None:
        """
        전일 종가 맵(ts→close)을 저장해 `prev_day_same_hour_ret` 계산에 사용.
        main.py daily_close()에서 당일 종가 버퍼를 전달.
        """
        self._prev_day_close_buf = dict(close_map)

    def update_prev_day_same_hour_ret(self, current_ts: str) -> None:
        """
        현재 ts와 동일 HH:MM의 전일 봉 수익률을 계산해 버퍼에 저장.
        main.py STEP 4 직전(매분)에 호출.
        """
        try:
            dt     = datetime.datetime.strptime(current_ts[:19], "%Y-%m-%d %H:%M:%S")
            prev_d = dt - datetime.timedelta(days=1)
            # 주말 건너뜀
            while prev_d.weekday() >= 5:
                prev_d -= datetime.timedelta(days=1)
            prev_ts = prev_d.strftime("%Y-%m-%d ") + dt.strftime("%H:%M:%S")
            prev_ts_m1 = prev_d.strftime("%Y-%m-%d ") + (dt - datetime.timedelta(minutes=1)).strftime("%H:%M:%S")
            c0 = self._prev_day_close_buf.get(prev_ts_m1)
            c1 = self._prev_day_close_buf.get(prev_ts)
            if c0 and c1 and c0 > 0:
                self._prev_day_same_hour_ret = (c1 - c0) / c0
            else:
                self._prev_day_same_hour_ret = 0.0
        except Exception:
            self._prev_day_same_hour_ret = 0.0

    def get_feature_vector(self, feature_names: list) -> np.ndarray:
        return np.array([self._last_features.get(name, 0.0) for name in feature_names], dtype=float)

    def feats_to_vec(self, feats, feature_names):
        # type: (dict, list) -> np.ndarray
        """피처 dict → numpy 1D 배열. feature_names 순서 보장."""
        return np.array([feats.get(n, 0.0) for n in feature_names], dtype=float)

    def build_for_horizon(self, bar_n, horizon_min):
        # type: (dict, int) -> dict
        """
        N분봉 기준 bar-level 피처 재계산.
        반드시 build(bar_1m) 호출 후 사용 — _last_features(1m 기반)에서 복사 후 N분봉 값 덮어씀.
        """
        feats = dict(self._last_features)
        close  = float(bar_n.get("close",    0.0) or 0.0)
        high   = float(bar_n.get("high",     0.0) or 0.0)
        low    = float(bar_n.get("low",      0.0) or 0.0)
        vol    = int(bar_n.get("volume",     0)   or 0)
        open_  = float(bar_n.get("open",     close) or close)
        buy_v  = float(bar_n.get("buy_vol",  0)   or 0)
        sell_v = float(bar_n.get("sell_vol", 0)   or 0)

        # N분봉 bar-level 피처 덮어쓰기
        feats["atr"]        = max(high - low, 0.5)
        feats["bar_volume"] = float(vol)
        feats["ret_{}m".format(horizon_min)] = (close - open_) / (open_ + 1e-9)

        # N분봉 CVD 방향 재계산 (bar_aggregator buy_vol/sell_vol 합계 기반)
        # 125차 scaling 동일: net_ratio × 0.5 → (-0.45, 0.45) clip
        _tot_v = buy_v + sell_v
        if _tot_v > 0:
            feats["cvd_direction"] = float(
                np.clip((buy_v - sell_v) / _tot_v * 0.5, -0.45, 0.45)
            )

        # 반감기 적용 (Phase 1-1)
        from features.feature_decay import get_horizon_features
        return get_horizon_features(feats, "{}m".format(horizon_min))

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
        self.vpin_calc.reset_daily()
        self.kyle_lambda_calc.reset_daily()
        self.rv_calc.reset_daily()
        self.multi_timeframe.reset_daily()
        self._last_features = {}
        self._last_hoga_snapshot = {}
        self._micro_tick_count = 0
        self._micro_minute_count = 0
        # 317차: 누락돼있던 Hurst 종가 버퍼 리셋 — 개장 후 최초 ~40분간 전일/주말
        # 종가가 창에 섞여 들어가 Hurst가 비정상적으로 낮게 나오던 원인(316차 딥다이브).
        self._close_history.clear()
        logger.info("[FeatureBuilder] daily reset complete")
