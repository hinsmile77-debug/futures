# features/macro/macro_feature_transformer.py
"""
MacroFetcher 출력(raw) → ML 모델 입력 피처 변환

MacroFetcher는 절대값(VIX) + 소수 변동률(sp500_chg=0.005 = 0.5%)을 반환한다.
GBM/SGD 피처로 주입하려면 0~1 범위 정규화 + 바이너리 플래그 추출이 필요하다.

반환 키:
  macro_vix           — VIX 정규화 (0=안정 15, 1=공포 40)
  macro_vix_abs       — VIX 원본값 (레짐 판단용 참고)
  macro_sp500_chg     — S&P500 변동률 정규화 [-1, +1]
  macro_nasdaq_chg    — 나스닥 변동률 정규화 [-1, +1]
  macro_krw_chg       — USD/KRW 변동률 정규화 [-1, +1]
  macro_us10y_chg     — 미국 10년물 변동률 정규화 [-1, +1]
  macro_risk_on       — 1.0 if VIX<18 AND SP500 상승 (글로벌 위험선호)
  macro_risk_off      — 1.0 if VIX>28 OR SP500 -1% 이하 (글로벌 위험회피)
  macro_event_flag    — 1.0 if FOMC/CPI 등 이벤트 당일 (변동성 주의)
"""
import logging
from typing import Dict

import numpy as np

logger = logging.getLogger("MACRO")

# VIX 정규화 기준 (이 범위 밖은 클리핑)
_VIX_BASE  = 15.0   # 안정 하한
_VIX_FEAR  = 40.0   # 공포 상한

# 변동률 클리핑 (소수 단위 — ±3% 초과를 극단값으로 처리)
_CHG_CLIP  = 0.03


class MacroFeatureTransformer:
    """
    MacroFetcher.get_features() → ML 피처 딕셔너리

    사용:
        transformer = MacroFeatureTransformer()
        feats = transformer.transform(macro_fetcher.get_features())
        feature_builder.build(bar, macro_data=feats)
    """

    def transform(self, raw: Dict[str, float]) -> Dict[str, float]:
        """
        Args:
            raw: MacroFetcher.get_features() 반환값
                 {vix, sp500_chg, nasdaq_chg, usd_krw_chg, us10y_chg, event_flag}

        Returns:
            9개 정규화 피처 딕셔너리 (모두 float, NaN 없음)
        """
        vix    = float(raw.get("vix",          20.0) or 20.0)
        sp500  = float(raw.get("sp500_chg",     0.0) or 0.0)
        nasdaq = float(raw.get("nasdaq_chg",    0.0) or 0.0)
        krw    = float(raw.get("usd_krw_chg",   0.0) or 0.0)
        us10y  = float(raw.get("us10y_chg",     0.0) or 0.0)
        event  = float(raw.get("event_flag",    0.0) or 0.0)
        quality_available = float(raw.get("macro_quality_available", 1.0) or 0.0)
        quality_stale = float(raw.get("macro_quality_stale", 0.0) or 0.0)
        quality_age_sec = float(raw.get("macro_quality_age_sec", 0.0) or 0.0)
        quality_fallback = float(raw.get("macro_quality_fallback_used", 0.0) or 0.0)
        quality_source_code = float(raw.get("macro_quality_source_code", 0.0) or 0.0)

        # VIX: 0(안정) ~ 1(공포)
        vix_norm = float(np.clip(
            (vix - _VIX_BASE) / (_VIX_FEAR - _VIX_BASE), 0.0, 1.0
        ))

        def _norm(v: float) -> float:
            """소수 변동률 → [-1, +1] 정규화"""
            return float(np.clip(v, -_CHG_CLIP, _CHG_CLIP) / _CHG_CLIP)

        # 위험 레짐 바이너리 플래그
        risk_on  = 1.0 if (vix < 18.0 and sp500 > 0.002)  else 0.0
        risk_off = 1.0 if (vix > 28.0 or sp500 < -0.010)  else 0.0

        result = {
            "macro_vix":        vix_norm,
            "macro_vix_abs":    round(vix, 2),
            "macro_sp500_chg":  _norm(sp500),
            "macro_nasdaq_chg": _norm(nasdaq),
            "macro_krw_chg":    _norm(krw),
            "macro_us10y_chg":  _norm(us10y),
            "macro_risk_on":    risk_on,
            "macro_risk_off":   risk_off,
            "macro_event_flag": event,
            # Day 8 quality passthrough
            "macro_quality_available": quality_available,
            "macro_quality_stale": quality_stale,
            "macro_quality_age_sec": quality_age_sec,
            "macro_quality_fallback_used": quality_fallback,
            "macro_quality_source_code": quality_source_code,
        }

        logger.debug(
            "[MacroFeat] VIX=%.1f(norm=%.2f) SP500=%+.3f KRW=%+.3f "
            "risk_on=%s risk_off=%s event=%s",
            vix, vix_norm, sp500, krw,
            bool(risk_on), bool(risk_off), bool(event),
        )
        return result

    @staticmethod
    def empty() -> Dict[str, float]:
        """MacroFetcher 미수집 시 안전 기본값"""
        return {
            "macro_vix":        0.125,   # VIX≈20 정규화값
            "macro_vix_abs":    20.0,
            "macro_sp500_chg":  0.0,
            "macro_nasdaq_chg": 0.0,
            "macro_krw_chg":    0.0,
            "macro_us10y_chg":  0.0,
            "macro_risk_on":    0.0,
            "macro_risk_off":   0.0,
            "macro_event_flag": 0.0,
            "macro_quality_available": 0.0,
            "macro_quality_stale": 1.0,
            "macro_quality_age_sec": 9999.0,
            "macro_quality_fallback_used": 1.0,
            "macro_quality_source_code": 0.0,
        }
