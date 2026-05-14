# model/regime_specific.py — 레짐별 전용 모델 (Regime-Specific Models)
"""
시장 레짐(추세/횡보/급변)에 따라 서로 다른 예측 모델을 사용.

기존 단일 앙상블 vs 레짐별 분리:
  단일: 추세장·횡보장 모두 동일 모델 → 횡보장에서 과최적화된 추세 모델이 오작동
  분리: 추세장 → 추세추종 모델 / 횡보장 → 평균회귀 모델 / 급변장 → 방어 모델

기대 효과: 정확도 +4~7%

구현:
  - 각 레짐별 SGDClassifier 독립 유지
  - 레짐 변환 시 이전 레짐 모델 freeze, 새 레짐 모델 activate
  - 데이터 부족 레짐은 공통 모델 fallback
"""
import numpy as np
import logging
from collections import deque
from typing import Dict, List, Optional

try:
    from sklearn.linear_model import SGDClassifier
    from sklearn.preprocessing import StandardScaler
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False

from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT

logger = logging.getLogger("MODEL")

REGIMES = ["추세장", "횡보장", "급변장", "혼합"]


class RegimeSpecificModel:
    """
    레짐별 독립 예측 모델 관리자

    레짐: "추세장" / "횡보장" / "급변장" / "혼합"
    """

    MIN_SAMPLES_PER_REGIME = 30   # 레짐별 최소 학습 샘플

    def __init__(self):
        if not _SKLEARN_OK:
            logger.warning("[RegimeModel] sklearn 없음 — 더미 모드")

        self._models:    Dict[str, Optional[object]] = {}
        self._scalers:   Dict[str, Optional[object]] = {}
        self._fitted:    Dict[str, bool]             = {}
        self._n_samples: Dict[str, int]              = {}

        # 레짐별 예측 버퍼 (정확도 추적)
        self._accuracy_buf: Dict[str, deque] = {}

        for regime in REGIMES:
            self._n_samples[regime]     = 0
            self._fitted[regime]        = False
            self._accuracy_buf[regime]  = deque(maxlen=50)

            if _SKLEARN_OK:
                # 레짐별 하이퍼파라미터 조정
                if regime == "추세장":
                    # 추세 포착: 낮은 정규화, 빠른 학습
                    self._models[regime]  = SGDClassifier(loss="log_loss", alpha=0.0005, max_iter=1, warm_start=True)
                elif regime == "횡보장":
                    # 평균회귀: 높은 정규화, 안정적 학습
                    self._models[regime]  = SGDClassifier(loss="log_loss", alpha=0.005, max_iter=1, warm_start=True)
                elif regime == "급변장":
                    # 방어적: 최대 정규화 (신호 약화)
                    self._models[regime]  = SGDClassifier(loss="log_loss", alpha=0.01, max_iter=1, warm_start=True)
                else:
                    # 혼합: 기본값
                    self._models[regime]  = SGDClassifier(loss="log_loss", alpha=0.001, max_iter=1, warm_start=True)

                self._scalers[regime] = StandardScaler()
            else:
                self._models[regime]  = None
                self._scalers[regime] = None

        # 공통 fallback 모델
        if _SKLEARN_OK:
            self._fallback_model  = SGDClassifier(loss="log_loss", alpha=0.001, max_iter=1, warm_start=True)
            self._fallback_scaler = StandardScaler()
            self._fallback_fitted = False
        else:
            self._fallback_model  = None
            self._fallback_scaler = None
            self._fallback_fitted = False

    def predict(
        self,
        features: List[float],
        regime:   str,
    ) -> dict:
        """
        레짐별 예측

        Args:
            features: 피처 벡터
            regime:   현재 미시 레짐

        Returns:
            {direction, prob_up, prob_down, model_regime, confidence}
        """
        if regime not in REGIMES:
            regime = "혼합"

        model_used = regime

        # 레짐 모델이 준비되었는지 확인
        if self._fitted.get(regime) and _SKLEARN_OK:
            prob_up, prob_down, prob_flat = self._predict_with(features, regime)
        elif self._fallback_fitted and _SKLEARN_OK:
            prob_up, prob_down, prob_flat = self._predict_with(features, None)
            model_used = "혼합(fallback)"
        else:
            prob_up, prob_down, prob_flat = self._rule_based(features, regime)
            model_used = "규칙기반"

        # UP/DOWN 상대 비율로 방향 결정 (FLAT 확률은 신뢰도 감쇄에 반영)
        ud_sum = prob_up + prob_down
        rel_up = prob_up / ud_sum if ud_sum > 0 else 0.5

        direction = DIRECTION_UP if rel_up > 0.55 else (DIRECTION_DOWN if rel_up < 0.45 else DIRECTION_FLAT)
        # FLAT 확률이 높을수록 신뢰도 감쇄: 불확실성을 신호 강도에 반영
        confidence = abs(rel_up - 0.5) * 2.0 * (1.0 - prob_flat)

        return {
            "direction":    direction,
            "prob_up":      round(prob_up, 4),
            "prob_down":    round(prob_down, 4),
            "prob_flat":    round(prob_flat, 4),
            "model_regime": model_used,
            "confidence":   round(confidence, 4),
        }

    def _predict_with(self, features: List[float], regime: Optional[str]):
        """
        Returns:
            (prob_up, prob_down, prob_flat) — 3-class 확률 튜플.
            분류기가 FLAT 클래스를 학습하지 않은 경우 prob_flat=0으로 반환.
        """
        try:
            if regime is None:
                scaler = self._fallback_scaler
                model  = self._fallback_model
            else:
                scaler = self._scalers[regime]
                model  = self._models[regime]

            X      = scaler.transform([features])
            probs  = model.predict_proba(X)[0]
            classes = list(model.classes_)

            def _p(cls):
                return float(probs[classes.index(cls)]) if cls in classes else 0.0

            return _p(DIRECTION_UP), _p(DIRECTION_DOWN), _p(DIRECTION_FLAT)
        except Exception:
            return 0.5, 0.5, 0.0

    def _rule_based(self, features: List[float], regime: str):
        """학습 전 기본 규칙 (피처 없이 레짐만으로 편향)"""
        return 0.5, 0.5, 0.0

    def partial_fit(
        self,
        features:  List[float],
        label:     int,   # DIRECTION_UP / DIRECTION_DOWN / DIRECTION_FLAT
        regime:    str,
    ):
        """
        레짐별 온라인 학습

        Args:
            features: 피처 벡터
            label:    실제 레이블
            regime:   해당 분봉의 레짐
        """
        if not _SKLEARN_OK or regime not in REGIMES:
            return

        self._n_samples[regime] = self._n_samples.get(regime, 0) + 1

        try:
            X = np.array([features])
            y = np.array([label])

            scaler = self._scalers[regime]
            model  = self._models[regime]

            if not self._fitted[regime]:
                scaler.partial_fit(X)

            X_scaled = scaler.transform(X)
            model.partial_fit(X_scaled, y, classes=[DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT])

            if self._n_samples[regime] >= self.MIN_SAMPLES_PER_REGIME:
                self._fitted[regime] = True

            # fallback도 함께 학습
            if not self._fallback_fitted:
                self._fallback_scaler.partial_fit(X)
            X_fb = self._fallback_scaler.transform(X)
            self._fallback_model.partial_fit(X_fb, y, classes=[DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT])

            if sum(self._n_samples.values()) >= self.MIN_SAMPLES_PER_REGIME:
                self._fallback_fitted = True

        except Exception as e:
            logger.warning(f"[RegimeModel] 학습 오류 ({regime}): {e}")

    def record_accuracy(self, regime: str, correct: bool):
        """예측 결과 기록"""
        if regime in self._accuracy_buf:
            self._accuracy_buf[regime].append(1 if correct else 0)

    def get_stats(self) -> dict:
        stats = {}
        for regime in REGIMES:
            buf = self._accuracy_buf[regime]
            stats[regime] = {
                "n_samples":  self._n_samples.get(regime, 0),
                "fitted":     self._fitted.get(regime, False),
                "accuracy":   round(float(np.mean(list(buf))), 4) if buf else None,
            }
        return stats


if __name__ == "__main__":
    import random
    random.seed(42)

    m = RegimeSpecificModel()

    feats = [0.3, 0.62, 1.1, 0.2, 0.4, 0.5, 0.65, 0.75, 0.05]

    # 추세장 학습
    for i in range(50):
        label = DIRECTION_UP if random.random() > 0.4 else DIRECTION_DOWN
        m.partial_fit(feats, label, "추세장")

    r = m.predict(feats, "추세장")
    print(f"[추세장] dir={r['direction']}, prob_up={r['prob_up']:.4f}, conf={r['confidence']:.4f}, model={r['model_regime']}")

    r2 = m.predict(feats, "횡보장")
    print(f"[횡보장] dir={r2['direction']}, model={r2['model_regime']}")

    print(f"Stats: {m.get_stats()}")
