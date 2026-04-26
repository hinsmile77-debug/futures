# learning/meta_confidence.py — 메타 신뢰도 학습기 (TIER S)
"""
"이 상황에서 내 예측이 얼마나 신뢰할 만한가"를 별도 학습

Renaissance Technologies의 핵심 기법:
  주 모델(GBM + SGD) 예측 → 메타 모델이 신뢰도 점수 부여
  → 신뢰도 낮은 구간에서 사이즈 자동 축소

입력 피처 (컨텍스트):
  - 시장 레짐 (추세/횡보/급변)
  - Hurst 지수
  - 최근 N분 정확도
  - 변동성 수준 (ATR ratio)
  - 시간대
  - LOB 불균형 강도
  - VPIN 수준

출력:
  confidence_score: 0.0 ~ 1.0
  size_multiplier:  0.0 ~ 1.5

기대 효과: 정확도 +5~8%
"""
import numpy as np
import logging
from collections import deque
from typing import Dict, Optional, List

try:
    from sklearn.linear_model import SGDClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.calibration import CalibratedClassifierCV
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False

logger = logging.getLogger("LEARNING")


class MetaConfidenceLearner:
    """
    예측 신뢰도를 별도 학습하는 메타 모델

    메타 피처 → 신뢰도 점수 → 포지션 사이즈 조정
    """

    ACCURACY_WINDOW = 20    # 최근 N분 정확도 추적
    MIN_SAMPLES     = 50    # 학습 최소 샘플 수

    def __init__(self):
        if not _SKLEARN_OK:
            logger.warning("[MetaConf] sklearn 없음 — 규칙 기반 모드로 동작")

        self._model: Optional[object]   = None
        self._scaler: Optional[object]  = None
        self._fitted                    = False
        self._sample_count              = 0

        # 결과 추적 (label: 예측 맞음=1, 틀림=0)
        self._X_buf: List[List[float]] = []
        self._y_buf: List[int]         = []

        # 최근 N분 정확도
        self._accuracy_buf = deque(maxlen=self.ACCURACY_WINDOW)

        # 신뢰도 히스토리
        self._conf_history = deque(maxlen=200)

        if _SKLEARN_OK:
            self._model  = SGDClassifier(loss="log_loss", max_iter=1, warm_start=True, alpha=0.001)
            self._scaler = StandardScaler()

    def build_meta_features(
        self,
        regime:        str,     # "추세장" / "횡보장" / "급변장" / "혼합"
        hurst:         float,
        atr_ratio:     float,   # ATR / ATR_평균
        hour_minute:   int,     # HHMM (e.g. 1030)
        lob_imbalance: float,   # -1 ~ +1
        vpin:          float,   # 0 ~ 1
        recent_accuracy: float, # 최근 N분 정확도
        signal_strength: float, # 앙상블 신호 강도 (0~1)
    ) -> List[float]:
        """
        메타 피처 벡터 구성

        Returns:
            [regime_code, hurst, atr_ratio, time_code,
             lob_imbalance, vpin, recent_acc, signal_strength,
             accuracy_trend]
        """
        regime_map = {"추세장": 1.0, "횡보장": -1.0, "급변장": -2.0, "혼합": 0.0}
        regime_code = regime_map.get(regime, 0.0)

        # 시간대 코드: 개장 초반(1), 안정(0), 마감 근접(-1)
        if   hour_minute < 1030:  time_code = 1.0
        elif hour_minute < 1400:  time_code = 0.0
        elif hour_minute < 1500:  time_code = -0.5
        else:                     time_code = -1.0

        # 최근 정확도 추세 (최근 10분 평균 - 이전 10분 평균)
        acc_arr = list(self._accuracy_buf)
        if len(acc_arr) >= 10:
            acc_trend = float(np.mean(acc_arr[-5:])) - float(np.mean(acc_arr[-10:-5]))
        else:
            acc_trend = 0.0

        return [
            regime_code,
            float(hurst),
            float(atr_ratio),
            float(time_code),
            float(lob_imbalance),
            float(vpin),
            float(recent_accuracy),
            float(signal_strength),
            float(acc_trend),
        ]

    def predict_confidence(
        self,
        meta_features: List[float],
    ) -> dict:
        """
        현재 컨텍스트에서 예측 신뢰도 추정

        Returns:
            {confidence_score, size_multiplier, model_source}
        """
        if self._fitted and _SKLEARN_OK:
            try:
                X = self._scaler.transform([meta_features])
                prob = self._model.predict_proba(X)[0]
                # prob[1] = 예측이 맞을 확률
                conf = float(prob[1]) if len(prob) > 1 else 0.5
                source = "SGD"
            except Exception:
                conf   = self._rule_based_confidence(meta_features)
                source = "규칙(오류fallback)"
        else:
            conf   = self._rule_based_confidence(meta_features)
            source = "규칙기반"

        self._conf_history.append(conf)

        # 사이즈 배율: 신뢰도 선형 매핑 (0.5→0.5x, 0.7→1.0x, 0.9→1.5x)
        if conf >= 0.7:
            size_mult = 1.0 + (conf - 0.7) * 2.5   # 최대 1.5x
        elif conf >= 0.5:
            size_mult = 0.5 + (conf - 0.5) * 2.5   # 0.5x ~ 1.0x
        else:
            size_mult = 0.0   # 신뢰도 50% 미만 → 진입 안 함

        return {
            "confidence_score": round(conf, 4),
            "size_multiplier":  round(min(size_mult, 1.5), 3),
            "model_source":     source,
        }

    def _rule_based_confidence(self, features: List[float]) -> float:
        """
        학습 전 또는 fallback용 규칙 기반 신뢰도

        features 순서: [regime, hurst, atr_ratio, time, lob, vpin, acc, strength, trend]
        """
        regime, hurst, atr_ratio, time_code, lob, vpin, acc, strength, trend = features

        score = 0.6  # 기본값

        # 레짐
        if regime == 1.0:  score += 0.08   # 추세장
        if regime == -1.0: score -= 0.15   # 횡보장
        if regime == -2.0: score -= 0.30   # 급변장

        # Hurst
        if hurst > 0.6:  score += 0.08
        if hurst < 0.45: score -= 0.15

        # ATR 급등
        if atr_ratio > 2.0: score -= 0.20

        # VPIN
        if vpin > 0.7:  score += 0.05

        # 최근 정확도
        score += (acc - 0.55) * 0.5   # 기준 55% 대비 편차 반영

        # 신호 강도
        score += (strength - 0.5) * 0.1

        return float(np.clip(score, 0.0, 1.0))

    def record_outcome(self, meta_features: List[float], correct: bool):
        """
        예측 결과 피드백 — 온라인 학습

        Args:
            meta_features: predict_confidence 에 쓴 것과 동일한 피처
            correct:       예측 정답 여부
        """
        label = 1 if correct else 0
        self._accuracy_buf.append(float(label))
        self._X_buf.append(meta_features)
        self._y_buf.append(label)
        self._sample_count += 1

        # 충분한 샘플 쌓이면 온라인 학습
        if _SKLEARN_OK and self._sample_count >= self.MIN_SAMPLES:
            self._partial_fit()

    def _partial_fit(self):
        """SGD 부분 학습"""
        try:
            X = np.array(self._X_buf[-100:])
            y = np.array(self._y_buf[-100:])

            if not self._fitted:
                self._scaler.fit(X)
                self._fitted = True

            X_scaled = self._scaler.transform(X)
            self._model.partial_fit(X_scaled, y, classes=[0, 1])

        except Exception as e:
            logger.warning(f"[MetaConf] 학습 오류: {e}")

    def get_stats(self) -> dict:
        recent_acc = float(np.mean(list(self._accuracy_buf))) if self._accuracy_buf else 0.0
        avg_conf   = float(np.mean(list(self._conf_history))) if self._conf_history else 0.0
        return {
            "sample_count":    self._sample_count,
            "recent_accuracy": round(recent_acc, 4),
            "avg_confidence":  round(avg_conf, 4),
            "model_fitted":    self._fitted,
        }

    def reset_daily(self):
        self._accuracy_buf.clear()


if __name__ == "__main__":
    mc = MetaConfidenceLearner()

    # 추세장 + 높은 Hurst + 좋은 정확도
    feats = mc.build_meta_features(
        regime="추세장", hurst=0.62, atr_ratio=1.1,
        hour_minute=1030, lob_imbalance=0.3, vpin=0.5,
        recent_accuracy=0.65, signal_strength=0.75,
    )
    r = mc.predict_confidence(feats)
    print(f"[추세장] conf={r['confidence_score']:.4f}, size_mult={r['size_multiplier']:.3f}, src={r['model_source']}")

    # 횡보장 + 낮은 Hurst
    feats2 = mc.build_meta_features(
        regime="횡보장", hurst=0.42, atr_ratio=0.9,
        hour_minute=1400, lob_imbalance=0.05, vpin=0.3,
        recent_accuracy=0.48, signal_strength=0.4,
    )
    r2 = mc.predict_confidence(feats2)
    print(f"[횡보장] conf={r2['confidence_score']:.4f}, size_mult={r2['size_multiplier']:.3f}, src={r2['model_source']}")
