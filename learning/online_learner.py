# learning/online_learner.py — SGD 분 단위 온라인 학습
"""
매분 예측 결과가 확인되는 즉시 SGD 모델을 업데이트합니다.

GBM과의 블렌딩 비율은 최근 50분 정확도에 따라 동적 조정:
  accuracy > 62% → SGD 비중 +2% (최대 50%)
  accuracy < 48% → SGD 비중 -2% (최소 10%)
"""
import numpy as np
import logging
from collections import deque
from typing import Dict, Optional

from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

from config.settings import (
    SGD_WEIGHT_DEFAULT, GBM_WEIGHT_DEFAULT,
    SGD_WEIGHT_MAX, SGD_WEIGHT_MIN,
    SGD_BOOST_THRESHOLD, SGD_CUT_THRESHOLD,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from config.settings import HORIZONS

logger = logging.getLogger("LEARNING")


class OnlineLearner:
    """SGD 온라인 자가학습기 (호라이즌별)"""

    ACCURACY_WINDOW = 50   # 최근 N분 정확도 추적

    def __init__(self):
        self.models:  Dict[str, SGDClassifier] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self._fitted: Dict[str, bool] = {}

        self.sgd_weight = SGD_WEIGHT_DEFAULT
        self.gbm_weight = GBM_WEIGHT_DEFAULT

        self._accuracy_buf: deque = deque(maxlen=self.ACCURACY_WINDOW)
        self._sample_count: int = 0
        self._horizon_counts: Dict[str, int] = {h: 0 for h in HORIZONS}

        for h in HORIZONS:
            self.models[h] = SGDClassifier(
                loss="log_loss",
                learning_rate="optimal",
                alpha=0.001,
                max_iter=1,
                warm_start=True,
                random_state=42,
                n_jobs=1,
            )
            self.scalers[h] = StandardScaler()
            self._fitted[h] = False

    def learn(
        self,
        horizon: str,
        x: np.ndarray,
        actual_label: int,
        predicted_label: int,
    ):
        """
        매분 학습 (partial_fit)

        Args:
            horizon:         "1m" | "3m" | ...
            x:               피처 벡터 (1D)
            actual_label:    실제 결과 (+1/-1/0)
            predicted_label: 직전 예측 방향
        """
        if horizon not in self.models:
            return

        x2d = x.reshape(1, -1)

        # 스케일러 업데이트 (온라인)
        scaler = self.scalers[horizon]
        if not self._fitted[horizon]:
            scaler.partial_fit(x2d)
        xs = scaler.transform(x2d)

        classes = np.array([DIRECTION_DOWN, DIRECTION_FLAT, DIRECTION_UP])
        self.models[horizon].partial_fit(xs, [actual_label], classes=classes)

        if not self._fitted[horizon]:
            self._fitted[horizon] = True
            logger.info(f"[OnlineLearner] {horizon} 초기 학습 완료")

        # 정확도 추적
        correct = (actual_label == predicted_label)
        self._accuracy_buf.append(1.0 if correct else 0.0)
        self._sample_count += 1
        self._horizon_counts[horizon] = self._horizon_counts.get(horizon, 0) + 1

        self._adjust_weights()

    def predict_proba(self, horizon: str, x: np.ndarray) -> Optional[Dict]:
        """SGD 예측 확률 반환"""
        if not self._fitted.get(horizon):
            return None

        x2d = x.reshape(1, -1)
        xs = self.scalers[horizon].transform(x2d)
        clf = self.models[horizon]
        proba = clf.predict_proba(xs)[0]
        classes = list(clf.classes_)

        proba_map = {int(c): float(p) for c, p in zip(classes, proba)}
        up   = proba_map.get(DIRECTION_UP,   0.0)
        down = proba_map.get(DIRECTION_DOWN, 0.0)
        flat = proba_map.get(DIRECTION_FLAT, 1/3)

        return {"up": up, "down": down, "flat": flat}

    def blend_with_gbm(self, gbm_proba: dict, sgd_proba: Optional[dict]) -> dict:
        """GBM + SGD 블렌딩"""
        if sgd_proba is None:
            return gbm_proba

        w_gbm = self.gbm_weight
        w_sgd = self.sgd_weight

        blended = {}
        for key in ["up", "down", "flat"]:
            blended[key] = (
                gbm_proba.get(key, 1/3) * w_gbm +
                sgd_proba.get(key, 1/3) * w_sgd
            )

        # 정규화
        total = sum(blended.values())
        if total > 0:
            blended = {k: v / total for k, v in blended.items()}

        return blended

    def _adjust_weights(self):
        """50분 정확도 기반 SGD 비중 동적 조정"""
        if len(self._accuracy_buf) < 20:
            return
        acc = sum(self._accuracy_buf) / len(self._accuracy_buf)

        if acc > SGD_BOOST_THRESHOLD:
            delta = +0.02
        elif acc < SGD_CUT_THRESHOLD:
            delta = -0.02
        else:
            return

        new_w = float(np.clip(self.sgd_weight + delta, SGD_WEIGHT_MIN, SGD_WEIGHT_MAX))
        if new_w != self.sgd_weight:
            self.sgd_weight = new_w
            self.gbm_weight = 1.0 - new_w
            logger.info(
                f"[OnlineLearner] 가중치 조정 "
                f"SGD={self.sgd_weight:.0%} GBM={self.gbm_weight:.0%} "
                f"(50분 정확도={acc:.1%})"
            )

    def recent_accuracy(self) -> float:
        if not self._accuracy_buf:
            return 0.5
        return sum(self._accuracy_buf) / len(self._accuracy_buf)

    def reset_daily(self):
        self._accuracy_buf.clear()
        self._sample_count = 0
        logger.info("[OnlineLearner] 일간 리셋 (모델 가중치 유지)")
