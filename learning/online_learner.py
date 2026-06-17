# learning/online_learner.py — SGD 분 단위 온라인 학습
"""
매분 예측 결과가 확인되는 즉시 SGD 모델을 업데이트합니다.

[Phase C 피처셋 분리 적용]
  호라이즌별 슬라이싱된 x 를 learn()/predict_proba()에서 수신.
  GBM과 동일한 피처셋으로 학습하여 신호 일관성 확보.

[P1-B: 호라이즌별 독립 가중치]
  버킷(short/long 묶음) → 6개 호라이즌 완전 독립.
  1m 노이즈가 3m·5m 가중치에 전파되는 문제 해소.

[P1-C: sample_weight FLAT 억제]
  FLAT 실제 비율 > 50% 구간에서 FLAT 레이블 가중치 0.5, UP/DN 1.5.
  SGD가 FLAT 편향을 흡수하지 않도록 차단.

[P2-E: 초기 부스트 + GBM FLAT 편향 대항]
  GBM flat_score > 0.6 → 학습 건수 부족해도 SGD 20% 즉시 투입.

가중치 조정 기준 (호라이즌별 임계값):
  1m/3m : BOOST=58%  CUT=45%
  5m    : BOOST=60%  CUT=47%
  10m   : BOOST=62%  CUT=48%
  15m   : BOOST=62%  CUT=50%
  30m   : BOOST=65%  CUT=52%
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
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from config.settings import HORIZONS

logger = logging.getLogger("LEARNING")

# P1-B: 호라이즌별 독립 임계값
_BOOST_THR: Dict[str, float] = {
    "1m": 0.58, "3m": 0.58, "5m": 0.60,
    "10m": 0.62, "15m": 0.62, "30m": 0.65,
}
_CUT_THR: Dict[str, float] = {
    "1m": 0.45, "3m": 0.45, "5m": 0.47,
    "10m": 0.48, "15m": 0.50, "30m": 0.52,
}


class OnlineLearner:
    """SGD 온라인 자가학습기 — 호라이즌별 완전 독립 가중치 (Phase C 대응)"""

    ACCURACY_WINDOW = 100       # 호라이즌별 독립 100분 윈도우
    _ADJUST_EVERY   = 1         # 1건 학습마다 조정 (호라이즌 독립이므로 묶음 불필요)
    _MIN_SAMPLES    = 15        # 가중치 조정 최소 샘플 수

    # 바닥 회복 파라미터
    _FLOOR_RECOVERY_INTERVAL = 30
    _FLOOR_RECOVERY_ACC_MIN  = 0.40
    _FLOOR_RECOVERY_DELTA    = 0.005
    _FLOOR_RECOVERY_MAX_UP   = 0.05

    # P1-C: FLAT 비율 추적 윈도우
    FLAT_TRACK_WINDOW = 50

    def __init__(self):
        self.models:  Dict[str, SGDClassifier] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self._fitted: Dict[str, bool] = {}

        # P1-B: 호라이즌별 완전 독립 가중치
        self._sgd_w: Dict[str, float] = {h: SGD_WEIGHT_DEFAULT for h in HORIZONS}
        self._gbm_w: Dict[str, float] = {h: GBM_WEIGHT_DEFAULT for h in HORIZONS}

        # 호라이즌별 독립 정확도 버퍼
        self._acc_buf: Dict[str, deque] = {
            h: deque(maxlen=self.ACCURACY_WINDOW) for h in HORIZONS
        }
        # P1-C: 호라이즌별 실제 레이블 버퍼 (FLAT 비율 추적)
        self._label_buf: Dict[str, deque] = {
            h: deque(maxlen=self.FLAT_TRACK_WINDOW) for h in HORIZONS
        }

        self._sample_count: int = 0
        self._horizon_counts: Dict[str, int] = {h: 0 for h in HORIZONS}
        self._learn_count:    Dict[str, int] = {h: 0 for h in HORIZONS}
        self._floor_ticks:    Dict[str, int] = {h: 0 for h in HORIZONS}
        # SGD 단방향 붕괴 감지 (up/dn/fl > 0.95 연속) — 방향 포함
        self._sgd_collapse_ticks: Dict[str, int] = {h: 0 for h in HORIZONS}
        self._sgd_collapse_dir:   Dict[str, str]  = {h: ""  for h in HORIZONS}

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

    # ── 학습 ────────────────────────────────────────────────────
    def learn(
        self,
        horizon: str,
        x: np.ndarray,
        actual_label: int,
        predicted_label: int,
    ):
        """매분 partial_fit.

        x: 호라이즌 전용 슬라이싱된 피처 벡터 (Phase C 적용 시 12~15개).
           GBM과 동일한 피처 공간에서 학습.
        """
        if horizon not in self.models:
            return

        x2d = x.reshape(1, -1)
        scaler = self.scalers[horizon]
        scaler.partial_fit(x2d)
        xs = scaler.transform(x2d)

        # P1-C: FLAT 비율 기반 sample_weight
        self._label_buf[horizon].append(actual_label)
        buf_labels = list(self._label_buf[horizon])
        n_buf = len(buf_labels)
        flat_ratio = buf_labels.count(DIRECTION_FLAT) / n_buf if n_buf > 0 else 0.33

        if flat_ratio > 0.50:
            sw = 0.5 if actual_label == DIRECTION_FLAT else 1.5
        elif flat_ratio < 0.20:
            # UP/DN 과다 구간: FLAT 강화
            sw = 1.3 if actual_label == DIRECTION_FLAT else 0.85
        else:
            sw = 1.0

        classes = np.array([DIRECTION_DOWN, DIRECTION_FLAT, DIRECTION_UP])
        self.models[horizon].partial_fit(
            xs, [actual_label],
            classes=classes,
            sample_weight=[sw],
        )

        if not self._fitted[horizon]:
            self._fitted[horizon] = True
            logger.info("[OnlineLearner] %s 초기 학습 완료", horizon)

        # 정확도 추적
        correct = (actual_label == predicted_label)
        self._acc_buf[horizon].append(1.0 if correct else 0.0)
        self._sample_count += 1
        self._horizon_counts[horizon] = self._horizon_counts.get(horizon, 0) + 1
        self._learn_count[horizon]    = self._learn_count.get(horizon, 0) + 1

        # 1건마다 해당 호라이즌 가중치 독립 조정
        self._adjust_weights(horizon)

    # ── 예측 ────────────────────────────────────────────────────
    def predict_proba(self, horizon: str, x: np.ndarray) -> Optional[Dict]:
        """SGD 예측.

        x: 호라이즌 전용 슬라이싱된 피처 벡터.
        """
        if not self._fitted.get(horizon):
            return None

        x2d = x.reshape(1, -1)
        try:
            xs = self.scalers[horizon].transform(x2d)
        except Exception:
            return None

        clf = self.models[horizon]
        try:
            proba = clf.predict_proba(xs)[0]
        except Exception:
            return None

        classes = list(clf.classes_)
        proba_map = {int(c): float(p) for c, p in zip(classes, proba)}
        result = {
            "up":   proba_map.get(DIRECTION_UP,   0.0),
            "down": proba_map.get(DIRECTION_DOWN, 0.0),
            "flat": proba_map.get(DIRECTION_FLAT, 1/3),
        }

        # SGD 단방향 붕괴 감지: up/dn/fl > 0.95 연속 15회 → 해당 호라이즌 모델 리셋
        collapse_dir = None
        if result["up"]   > 0.95:
            collapse_dir = "up"
        elif result["down"] > 0.95:
            collapse_dir = "dn"
        elif result["flat"] > 0.95:
            collapse_dir = "fl"

        if collapse_dir:
            if collapse_dir == self._sgd_collapse_dir.get(horizon, ""):
                self._sgd_collapse_ticks[horizon] = self._sgd_collapse_ticks.get(horizon, 0) + 1
            else:
                self._sgd_collapse_ticks[horizon] = 1
                self._sgd_collapse_dir[horizon] = collapse_dir

            if self._sgd_collapse_ticks[horizon] >= 15:
                self.models[horizon] = self.models[horizon].__class__(
                    loss="log", learning_rate="optimal", alpha=0.001,
                    max_iter=1, warm_start=True, random_state=42, n_jobs=1,
                )
                self.scalers[horizon] = self.scalers[horizon].__class__()
                self._fitted[horizon] = False
                self._sgd_w[horizon] = SGD_WEIGHT_DEFAULT
                self._gbm_w[horizon] = GBM_WEIGHT_DEFAULT
                self._sgd_collapse_ticks[horizon] = 0
                self._sgd_collapse_dir[horizon] = ""
                self._floor_ticks[horizon] = 0
                logger.info(
                    "[OnlineLearner] %s SGD %s붕괴 자동 복구 (≥95%% 15분 지속) "
                    "→ 모델·스케일러 리셋",
                    horizon, collapse_dir.upper(),
                )
        else:
            self._sgd_collapse_ticks[horizon] = 0
            self._sgd_collapse_dir[horizon] = ""

        return result

    # ── 블렌딩 ──────────────────────────────────────────────────
    def blend_with_gbm(
        self,
        gbm_proba: dict,
        sgd_proba: Optional[dict],
        horizon: str = "1m",
    ) -> dict:
        """GBM + SGD 블렌딩 — 호라이즌별 독립 가중치.

        P2-E: GBM FLAT 편향(flat_score > 0.60) 감지 시 초기 부스트 적용.
        """
        if sgd_proba is None:
            return gbm_proba

        h_count = self._horizon_counts.get(horizon, 0)
        gbm_flat = gbm_proba.get("flat", 1/3)

        # P2-E 임계: 장기 호라이즌(10m 이상)은 FL 구조 편향이 더 강해 낮은 임계에서 SGD 투입
        _p2e_flat_thr = 0.48 if horizon in ("10m", "15m", "30m") else 0.60

        if h_count < 20:
            # 완전 초기: GBM 전용 (uniform SGD가 conf 희석)
            w_gbm, w_sgd = 1.0, 0.0
        elif h_count < 50 and gbm_flat > _p2e_flat_thr:
            # P2-E: GBM FLAT 편향 감지 → 조기 SGD 20% 투입
            # 장기 호라이즌 임계 0.48 (기존 0.60): 30m gbm_flat≈0.47도 포착
            w_gbm, w_sgd = 0.80, 0.20
        elif h_count < 50:
            w_gbm, w_sgd = 0.95, 0.05
        else:
            w_sgd = self._sgd_w.get(horizon, SGD_WEIGHT_DEFAULT)
            w_gbm = self._gbm_w.get(horizon, GBM_WEIGHT_DEFAULT)

        blended = {
            k: gbm_proba.get(k, 1/3) * w_gbm + sgd_proba.get(k, 1/3) * w_sgd
            for k in ("up", "down", "flat")
        }
        total = sum(blended.values())
        if total > 0:
            blended = {k: v / total for k, v in blended.items()}
        return blended

    # ── 가중치 조정 ─────────────────────────────────────────────
    def _adjust_weights(self, horizon: str):
        """호라이즌별 독립 정확도 기반 SGD 비중 조정."""
        buf = self._acc_buf[horizon]
        if len(buf) < self._MIN_SAMPLES:
            return
        acc = sum(buf) / len(buf)

        _at_floor = self._sgd_w[horizon] <= SGD_WEIGHT_MIN + 1e-6

        if _at_floor:
            self._floor_ticks[horizon] += 1
            if (self._floor_ticks[horizon] >= self._FLOOR_RECOVERY_INTERVAL
                    and acc >= self._FLOOR_RECOVERY_ACC_MIN):
                new_w = min(
                    self._sgd_w[horizon] + self._FLOOR_RECOVERY_DELTA,
                    SGD_WEIGHT_MIN + self._FLOOR_RECOVERY_MAX_UP,
                )
                self._sgd_w[horizon] = new_w
                self._gbm_w[horizon] = 1.0 - new_w
                self._floor_ticks[horizon] = 0
                logger.info(
                    "[OnlineLearner] %s 바닥 회복 SGD=%.0f%% GBM=%.0f%%"
                    " (정확도=%.1f%% 바닥체류=%d회)",
                    horizon,
                    self._sgd_w[horizon] * 100,
                    self._gbm_w[horizon] * 100,
                    acc * 100,
                    self._FLOOR_RECOVERY_INTERVAL,
                )
            return

        self._floor_ticks[horizon] = 0
        boost = _BOOST_THR.get(horizon, 0.62)
        cut   = _CUT_THR.get(horizon, 0.48)

        if acc > boost:
            delta = +0.02
        elif acc < cut:
            delta = -0.02
        else:
            return

        new_w = float(np.clip(self._sgd_w[horizon] + delta, SGD_WEIGHT_MIN, SGD_WEIGHT_MAX))
        if abs(new_w - self._sgd_w[horizon]) > 1e-6:
            self._sgd_w[horizon] = new_w
            self._gbm_w[horizon] = 1.0 - new_w
            logger.info(
                "[OnlineLearner] %s 가중치 조정 SGD=%.0f%% GBM=%.0f%%"
                " (정확도=%.1f%%)",
                horizon,
                self._sgd_w[horizon] * 100,
                self._gbm_w[horizon] * 100,
                acc * 100,
            )

    # ── 상태 조회 ────────────────────────────────────────────────
    def is_ready(self) -> bool:
        return any(self._fitted.values())

    def recent_accuracy(self) -> float:
        """전 호라이즌 단순 평균 정확도 (대시보드용)"""
        accs = [sum(b) / len(b) for b in self._acc_buf.values() if b]
        return sum(accs) / len(accs) if accs else 0.5

    def recent_accuracy_by_bucket(self) -> Dict[str, float]:
        """버킷별 정확도 — 기존 로그 호환용 (short/long 평균)"""
        short_hz = ("1m", "3m", "5m")
        long_hz  = ("10m", "15m", "30m")
        def _avg(hzs):
            vals = [sum(self._acc_buf[h]) / len(self._acc_buf[h])
                    for h in hzs if self._acc_buf.get(h)]
            return sum(vals) / len(vals) if vals else 0.5
        return {"short": _avg(short_hz), "long": _avg(long_hz)}

    def horizon_accuracy(self, horizon: str) -> float:
        """호라이즌별 정확도 (Qualification 카드용)"""
        buf = self._acc_buf.get(horizon)
        if not buf or len(buf) < 5:
            return 0.0
        return sum(buf) / len(buf)

    # 기존 코드 호환 프로퍼티
    @property
    def sgd_weight(self) -> float:
        vals = list(self._sgd_w.values())
        return sum(vals) / len(vals)

    @property
    def gbm_weight(self) -> float:
        return 1.0 - self.sgd_weight

    def _bucket(self, horizon: str) -> str:
        """하위 호환 — 기존 코드에서 _bucket() 호출 시"""
        return "short" if horizon in ("1m", "3m", "5m") else "long"

    def boost_sgd_for_bias(self, horizon: str, target_w: float = 0.15) -> None:
        """GBM 방향 편향 감지 시 해당 호라이즌 SGD 비중 복구."""
        current = self._sgd_w.get(horizon, SGD_WEIGHT_DEFAULT)
        if current < target_w:
            new_w = float(np.clip(target_w, SGD_WEIGHT_MIN, SGD_WEIGHT_MAX))
            self._sgd_w[horizon] = new_w
            self._gbm_w[horizon] = 1.0 - new_w
            self._floor_ticks[horizon] = 0
            logger.info(
                "[OnlineLearner] %s bias fallback SGD 복구 %.0f%%→%.0f%%",
                horizon, current * 100, new_w * 100,
            )

    def reset_daily(self):
        """일간 리셋 — 모델 가중치 유지, 정확도 버퍼만 초기화."""
        for h in HORIZONS:
            self._acc_buf[h].clear()
            self._label_buf[h].clear()
            self._sgd_w[h] = SGD_WEIGHT_DEFAULT
            self._gbm_w[h] = GBM_WEIGHT_DEFAULT
            self._learn_count[h] = 0
            self._floor_ticks[h] = 0
            self._sgd_collapse_ticks[h] = 0
            self._sgd_collapse_dir[h] = ""
        self._sample_count = 0
        logger.info("[OnlineLearner] 일간 리셋 (모델 가중치 유지)")

    def reset_full(self):
        """완전 초기화 — 임계값 교체 후 레이블 체계 불일치 해소."""
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
            self._acc_buf[h].clear()
            self._label_buf[h].clear()
            self._sgd_w[h] = SGD_WEIGHT_DEFAULT
            self._gbm_w[h] = GBM_WEIGHT_DEFAULT
            self._learn_count[h] = 0
            self._floor_ticks[h] = 0
            self._sgd_collapse_ticks[h] = 0
            self._sgd_collapse_dir[h] = ""
        self._sample_count = 0
        self._horizon_counts = {h: 0 for h in HORIZONS}
        logger.info("[OnlineLearner] 완전 초기화 — 모델·스케일러·가중치 전체 리셋")
