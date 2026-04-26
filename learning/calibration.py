# learning/calibration.py — 예측 신뢰도 보정 (Calibration)
"""
모델이 70% 확률로 예측했을 때 실제로 70% 맞아야 신뢰도가 "보정"된 것.
GBM·SGD·앙상블의 확률 출력을 Platt Scaling 또는 Isotonic Regression으로 보정.

보정 방법:
  Platt Scaling: 로지스틱 회귀로 확률 재매핑 (파라미터 2개, 과적합 낮음)
  Isotonic Reg.: 단조증가 비모수 보정 (파라미터 많음, 샘플 많을 때 우수)

사용:
  1. 매 분봉 예측 확률 → calibrator.record(prob, actual)
  2. 일정 샘플 후 → calibrator.fit()
  3. 이후 예측 → calibrator.calibrate(raw_prob)

기대 효과: 신뢰도 보정 (사이즈 최적화의 핵심 입력)
"""
import numpy as np
import logging
from collections import deque
from typing import Optional, List

logger = logging.getLogger("LEARNING")

try:
    from sklearn.isotonic import IsotonicRegression
    from sklearn.linear_model import LogisticRegression
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False


class PredictionCalibrator:
    """
    예측 확률 보정기 (Platt Scaling 기본, Isotonic 선택)

    호라이즌별로 독립 관리.
    """

    MIN_SAMPLES   = 100    # 최소 보정 샘플
    WINDOW        = 500    # 슬라이딩 윈도우 (최근 N개만 사용)

    def __init__(self, method: str = "platt"):
        """
        Args:
            method: "platt" (기본, 파라미터 안정) | "isotonic" (샘플 많을 때)
        """
        self.method    = method
        self._fitted   = False
        self._n        = 0

        self._probs  = deque(maxlen=self.WINDOW)
        self._labels = deque(maxlen=self.WINDOW)

        self._model: Optional[object] = None

        if _SKLEARN_OK:
            if method == "isotonic":
                self._model = IsotonicRegression(out_of_bounds="clip")
            else:
                self._model = LogisticRegression(C=1.0, solver="lbfgs")

    def record(self, raw_prob: float, actual_correct: bool):
        """
        예측 결과 누적

        Args:
            raw_prob:        모델 원본 확률 (0~1)
            actual_correct:  실제로 맞았으면 True
        """
        self._probs.append(float(raw_prob))
        self._labels.append(1 if actual_correct else 0)
        self._n += 1

        # 주기적 재보정
        if self._n % 50 == 0 and self._n >= self.MIN_SAMPLES:
            self.fit()

    def fit(self):
        """보정 모델 학습"""
        if not _SKLEARN_OK:
            return

        probs  = np.array(list(self._probs))
        labels = np.array(list(self._labels))

        if len(probs) < self.MIN_SAMPLES:
            return

        try:
            if self.method == "isotonic":
                self._model.fit(probs, labels)
            else:
                # Platt: 로지스틱 회귀 (확률 → 로짓 공간 변환)
                X = probs.reshape(-1, 1)
                self._model.fit(X, labels)

            self._fitted = True
            logger.debug(f"[Calibration] {self.method} 보정 완료 (n={len(probs)})")

        except Exception as e:
            logger.warning(f"[Calibration] fit 오류: {e}")

    def calibrate(self, raw_prob: float) -> float:
        """
        원본 확률 → 보정된 확률

        Returns:
            calibrated probability (0~1), 미보정 시 raw_prob 반환
        """
        if not self._fitted or not _SKLEARN_OK:
            return float(raw_prob)

        try:
            if self.method == "isotonic":
                return float(np.clip(self._model.predict([raw_prob])[0], 0.0, 1.0))
            else:
                X = np.array([[raw_prob]])
                return float(np.clip(self._model.predict_proba(X)[0][1], 0.0, 1.0))
        except Exception:
            return float(raw_prob)

    def get_reliability_diagram(self, bins: int = 10) -> dict:
        """
        신뢰도 다이어그램 데이터 (보정 품질 시각화용)

        Returns:
            {bin_centers, mean_predicted_prob, fraction_positives, ece}
        """
        if len(self._probs) < self.MIN_SAMPLES:
            return {}

        probs  = np.array(list(self._probs))
        labels = np.array(list(self._labels))

        bin_edges   = np.linspace(0, 1, bins + 1)
        bin_centers = []
        mean_preds  = []
        fractions   = []

        for i in range(bins):
            mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
            if mask.sum() == 0:
                continue
            bin_centers.append((bin_edges[i] + bin_edges[i + 1]) / 2)
            mean_preds.append(float(probs[mask].mean()))
            fractions.append(float(labels[mask].mean()))

        # Expected Calibration Error
        ece = 0.0
        n   = len(probs)
        for i in range(len(bin_centers)):
            mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
            ece += (mask.sum() / n) * abs(mean_preds[i] - fractions[i])

        return {
            "bin_centers":          bin_centers,
            "mean_predicted_prob":  mean_preds,
            "fraction_positives":   fractions,
            "ece":                  round(ece, 4),   # 낮을수록 잘 보정됨 (0 = 완벽)
            "n_samples":            n,
        }

    @property
    def is_fitted(self) -> bool:
        return self._fitted

    @property
    def n_samples(self) -> int:
        return self._n


class MultiHorizonCalibrator:
    """호라이즌별 독립 보정기 묶음"""

    def __init__(self, horizons: List[str], method: str = "platt"):
        self.calibrators = {h: PredictionCalibrator(method=method) for h in horizons}

    def record(self, horizon: str, raw_prob: float, correct: bool):
        if horizon in self.calibrators:
            self.calibrators[horizon].record(raw_prob, correct)

    def calibrate(self, horizon: str, raw_prob: float) -> float:
        if horizon in self.calibrators:
            return self.calibrators[horizon].calibrate(raw_prob)
        return raw_prob

    def fit_all(self):
        for cal in self.calibrators.values():
            cal.fit()

    def get_ece(self) -> dict:
        return {
            h: cal.get_reliability_diagram().get("ece", None)
            for h, cal in self.calibrators.items()
        }


if __name__ == "__main__":
    import random
    random.seed(42)

    cal = PredictionCalibrator(method="platt")

    # 시뮬레이션: 높은 확률 예측 → 실제로 더 자주 맞음
    for _ in range(200):
        prob    = random.uniform(0.3, 0.9)
        correct = random.random() < prob * 0.9   # 약간 과신 편향
        cal.record(prob, correct)

    cal.fit()
    print(f"보정 전: 0.70 → {0.70:.4f}")
    print(f"보정 후: 0.70 → {cal.calibrate(0.70):.4f}")
    print(f"보정 전: 0.55 → {0.55:.4f}")
    print(f"보정 후: 0.55 → {cal.calibrate(0.55):.4f}")

    diag = cal.get_reliability_diagram()
    print(f"ECE = {diag.get('ece', 'N/A')} (0에 가까울수록 좋음)")
