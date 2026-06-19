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
import os
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

    MIN_SAMPLES   = 80     # 최소 보정 샘플 (100→80: 신규 시장 컨디션 빠른 적용)
    # 85차: 500→200 — 현재 시장 컨디션 반영 속도 향상 (500건 ≈ 과거 8거래일 평균으로 희석)
    # 6/11 분석: ECE=0.155, conf 역전(0.60+ 구간 정확도 오히려 낮음) — 오래된 데이터 희석 효과
    # 200→100: 최근 ~1.7일 데이터만 반영, 최신 시장 컨디션 빠른 추적
    WINDOW        = 100    # 슬라이딩 윈도우 (최근 N개만 사용)

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

        self._transition_steps: int = 0  # P3: is_fitted 전환 후 블렌딩 카운터

        if _SKLEARN_OK:
            if method == "isotonic":
                self._model = IsotonicRegression(out_of_bounds="clip")
            else:
                # P2: C=1.0→0.1 — overconfident 데이터에서 급경사 Platt 커브 완화
                # 6/11 분석: 0.60+ 구간 conf-accuracy 역전 → C=0.1→0.05 추가 정규화
                self._model = LogisticRegression(C=0.05, solver="lbfgs")

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

        # 주기적 재보정 (85차: 50→20, 6/11: 20→10 — 100건 윈도우에서 20건 주기는 느림)
        if self._n % 10 == 0 and self._n >= self.MIN_SAMPLES:
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

            # P3: 첫 fitted 전환 시 블렌딩 카운터 설정 (conf 점프 완화)
            if not self._fitted:
                self._transition_steps = 20
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
                cal = float(np.clip(self._model.predict([raw_prob])[0], 0.0, 1.0))
            else:
                X = np.array([[raw_prob]])
                cal = float(np.clip(self._model.predict_proba(X)[0][1], 0.0, 1.0))

            # P3: is_fitted 첫 전환 후 N봉 동안 raw↔calibrated 블렌딩 (점프 완화)
            if self._transition_steps > 0:
                alpha = 1.0 - self._transition_steps / 20.0  # 0.05→1.0 선형 증가
                cal = alpha * cal + (1.0 - alpha) * float(raw_prob)
                self._transition_steps -= 1
            return cal
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

    def save(self, path: str) -> bool:
        """보정 모델 + 누적 데이터를 디스크에 저장 (joblib)."""
        if not _SKLEARN_OK or not self._fitted:
            return False
        try:
            import joblib
            joblib.dump({
                "model":   self._model,
                "probs":   list(self._probs),
                "labels":  list(self._labels),
                "n":       self._n,
                "method":  self.method,
            }, path, protocol=4)
            return True
        except Exception as e:
            logger.warning("[Calibration] save 실패: %s", e)
            return False

    def load(self, path: str) -> bool:
        """디스크에서 보정 모델 + 누적 데이터 복원."""
        if not _SKLEARN_OK or not os.path.exists(path):
            return False
        try:
            import joblib
            state = joblib.load(path)
            self._model  = state["model"]
            self._fitted = True
            self._n      = state.get("n", 0)
            for p in state.get("probs", []):
                self._probs.append(p)
            for lb in state.get("labels", []):
                self._labels.append(lb)
            logger.info("[Calibration] 보정기 복원 완료 (n=%d method=%s)", self._n, self.method)
            return True
        except Exception as e:
            logger.warning("[Calibration] load 실패: %s", e)
            return False

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
