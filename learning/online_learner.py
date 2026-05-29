# learning/online_learner.py — SGD 분 단위 온라인 학습
"""
매분 예측 결과가 확인되는 즉시 SGD 모델을 업데이트합니다.

GBM과의 블렌딩 비율은 short(1/3/5m) / long(10/15/30m) 버킷별로
독립된 50분 정확도에 따라 동적 조정합니다:
  accuracy > 62% → SGD 비중 +2% (최대 50%)
  accuracy < 48% → SGD 비중 -2% (최소 10%)

버킷 분리 이유: 단기 반전장에서 1m/3m가 흔들릴 때
  장기 추세(15m/30m) 가중치까지 함께 벌을 받는 문제 해소.
"""
import numpy as np
import logging
from collections import deque
from typing import Dict, Optional, Tuple

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
    """SGD 온라인 자가학습기 (호라이즌별, short/long 2버킷 가중치)"""

    # 버킷당 호라이즌 3개 × 50분 = 150 샘플 = 실질 50분 윈도우
    # (이전 50은 3 호라이즌/분이 들어오면 실질 17분치에 불과했음)
    ACCURACY_WINDOW = 150

    # short 버킷: 단기 반전 민감 / long 버킷: 추세 추종
    BUCKET_SHORT: Tuple[str, ...] = ("1m", "3m", "5m")
    BUCKET_LONG:  Tuple[str, ...] = ("10m", "15m", "30m")

    # 1분치(버킷당 호라이즌 수) 학습 완료 후 가중치 1회 조정
    # 매 샘플 즉시 조정 시 연속 실패로 SGD 가중치가 1분 내 절반 붕괴하는 문제 방지
    _ADJUST_EVERY = 3

    def __init__(self):
        self.models:  Dict[str, SGDClassifier] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self._fitted: Dict[str, bool] = {}

        # 버킷별 독립 가중치
        self._sgd_w: Dict[str, float] = {
            "short": SGD_WEIGHT_DEFAULT,
            "long":  SGD_WEIGHT_DEFAULT,
        }
        self._gbm_w: Dict[str, float] = {
            "short": GBM_WEIGHT_DEFAULT,
            "long":  GBM_WEIGHT_DEFAULT,
        }

        # 버킷별 독립 정확도 버퍼
        self._acc_buf: Dict[str, deque] = {
            "short": deque(maxlen=self.ACCURACY_WINDOW),
            "long":  deque(maxlen=self.ACCURACY_WINDOW),
        }
        # 호라이즌별 독립 정확도 버퍼 (Qualification 카드 표시용)
        self._horizon_acc_buf: Dict[str, deque] = {
            h: deque(maxlen=self.ACCURACY_WINDOW) for h in HORIZONS
        }

        self._sample_count: int = 0
        self._horizon_counts: Dict[str, int] = {h: 0 for h in HORIZONS}
        # 버킷별 learn() 호출 횟수 — _ADJUST_EVERY마다 가중치 1회 조정
        self._bucket_learn_count: Dict[str, int] = {"short": 0, "long": 0}

        for h in HORIZONS:
            self.models[h] = SGDClassifier(
                loss="log",
                learning_rate="optimal",
                alpha=0.001,
                max_iter=1,
                warm_start=True,
                random_state=42,
                n_jobs=1,
            )
            self.scalers[h] = StandardScaler()
            self._fitted[h] = False

    # ── 버킷 분류 헬퍼 ──────────────────────────────────────────
    def _bucket(self, horizon: str) -> str:
        return "short" if horizon in self.BUCKET_SHORT else "long"

    # ── 학습 ────────────────────────────────────────────────────
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

        scaler = self.scalers[horizon]
        scaler.partial_fit(x2d)   # 매 샘플마다 적응적 스케일 업데이트
        xs = scaler.transform(x2d)

        classes = np.array([DIRECTION_DOWN, DIRECTION_FLAT, DIRECTION_UP])
        self.models[horizon].partial_fit(xs, [actual_label], classes=classes)

        if not self._fitted[horizon]:
            self._fitted[horizon] = True
            logger.info(f"[OnlineLearner] {horizon} 초기 학습 완료")

        # 정확도 추적 — 버킷별 + 호라이즌별 독립 버퍼에 기록
        bucket = self._bucket(horizon)
        correct = (actual_label == predicted_label)
        self._acc_buf[bucket].append(1.0 if correct else 0.0)
        if horizon in self._horizon_acc_buf:
            self._horizon_acc_buf[horizon].append(1.0 if correct else 0.0)
        self._sample_count += 1
        self._horizon_counts[horizon] = self._horizon_counts.get(horizon, 0) + 1
        self._bucket_learn_count[bucket] += 1

        # 1분치(=_ADJUST_EVERY 호라이즌) 완료 후 1회만 조정
        # — 매 샘플 즉시 조정 시 연속 실패 7건 → -14%p 급감하는 과민 반응 방지
        if self._bucket_learn_count[bucket] % self._ADJUST_EVERY == 0:
            self._adjust_weights(bucket)

    # ── 예측 ────────────────────────────────────────────────────
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

    # ── 블렌딩 ──────────────────────────────────────────────────
    def blend_with_gbm(
        self,
        gbm_proba: dict,
        sgd_proba: Optional[dict],
        horizon: str = "",
    ) -> dict:
        """GBM + SGD 블렌딩 (버킷별 가중치 적용)"""
        if sgd_proba is None:
            return gbm_proba

        # 초기 30건 미만: GBM 전용 모드 (uniform SGD가 GBM conf를 희석하는 현상 방지)
        # SGD가 학습 초기(1~20건)에 1/3에 가까운 확률을 출력하면 블렌딩 후 conf -5~8%p 저하
        h_count = self._horizon_counts.get(horizon, 0)
        if h_count < 30:
            w_gbm, w_sgd = 0.95, 0.05
        else:
            bucket = self._bucket(horizon) if horizon else "short"
            w_gbm = self._gbm_w[bucket]
            w_sgd = self._sgd_w[bucket]

        blended = {}
        for key in ["up", "down", "flat"]:
            blended[key] = (
                gbm_proba.get(key, 1/3) * w_gbm +
                sgd_proba.get(key, 1/3) * w_sgd
            )

        total = sum(blended.values())
        if total > 0:
            blended = {k: v / total for k, v in blended.items()}

        return blended

    # ── 가중치 조정 ─────────────────────────────────────────────
    def _adjust_weights(self, bucket: str):
        """버킷 정확도 기반 SGD 비중 독립 조정"""
        buf = self._acc_buf[bucket]
        if len(buf) < 20:
            return
        acc = sum(buf) / len(buf)

        if acc > SGD_BOOST_THRESHOLD:
            delta = +0.02
        elif acc < SGD_CUT_THRESHOLD:
            delta = -0.02
        else:
            return

        new_w = float(np.clip(self._sgd_w[bucket] + delta, SGD_WEIGHT_MIN, SGD_WEIGHT_MAX))
        if new_w != self._sgd_w[bucket]:
            self._sgd_w[bucket] = new_w
            self._gbm_w[bucket] = 1.0 - new_w
            logger.info(
                f"[OnlineLearner] {bucket} 가중치 조정 "
                f"SGD={self._sgd_w[bucket]:.0%} GBM={self._gbm_w[bucket]:.0%} "
                f"(50분 정확도={acc:.1%})"
            )

    # ── 상태 조회 ────────────────────────────────────────────────
    def is_ready(self) -> bool:
        return any(self._fitted.values())

    def recent_accuracy(self) -> float:
        """전체 버킷 가중 평균 정확도 (대시보드용)"""
        short_buf = self._acc_buf["short"]
        long_buf  = self._acc_buf["long"]
        short_acc = sum(short_buf) / len(short_buf) if short_buf else 0.5
        long_acc  = sum(long_buf)  / len(long_buf)  if long_buf  else 0.5
        # short 3개 호라이즌 / long 3개 — 동등 가중
        return (short_acc + long_acc) / 2.0

    def recent_accuracy_by_bucket(self) -> Dict[str, float]:
        """버킷별 정확도 반환 (로그·대시보드 상세용)"""
        result = {}
        for bk in ("short", "long"):
            buf = self._acc_buf[bk]
            result[bk] = sum(buf) / len(buf) if buf else 0.5
        return result

    def horizon_accuracy(self, horizon: str) -> float:
        """호라이즌별 정확도 반환 (Qualification 카드 표시용).

        샘플 5개 미만이면 0.0 반환 (불안정한 초기값 표시 억제).
        """
        buf = self._horizon_acc_buf.get(horizon)
        if not buf or len(buf) < 5:
            return 0.0
        return sum(buf) / len(buf)

    # 단일 가중치 프로퍼티 — 기존 로그 참조 호환
    @property
    def sgd_weight(self) -> float:
        return (self._sgd_w["short"] + self._sgd_w["long"]) / 2.0

    @property
    def gbm_weight(self) -> float:
        return 1.0 - self.sgd_weight

    def reset_daily(self):
        for bk in ("short", "long"):
            self._acc_buf[bk].clear()
            self._sgd_w[bk] = SGD_WEIGHT_DEFAULT
        for h in self._horizon_acc_buf:
            self._horizon_acc_buf[h].clear()
            self._gbm_w[bk] = GBM_WEIGHT_DEFAULT
            self._bucket_learn_count[bk] = 0
        self._sample_count = 0
        logger.info("[OnlineLearner] 일간 리셋 (모델 가중치 유지)")
