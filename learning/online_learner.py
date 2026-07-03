# learning/online_learner.py — SGD 분 단위 온라인 학습
"""
매분 예측 결과가 확인되는 즉시 SGD 모델을 업데이트합니다.

[Phase C 피처셋 분리 적용 → P2(288차)에서 GBM과 완전 분리]
  호라이즌별 슬라이싱된 x 를 learn()/predict_proba()에서 수신.
  config.settings.SGD_FEATURE_NAMES_BY_HORIZON(호라이즌별 상위 5개 IC 피처) 전용 —
  GBM SHAP 피처셋(11~15개)과 더 이상 공유하지 않는다. 선형모델인 SGD에 GBM 전용
  비선형 상호작용 피처(hurst·macro_vix 등, 단독 IC≈0)를 넣으면 잡음 차원이 될 뿐이라
  main.py 쪽에서 별도 인덱스(_sgd_feat_indices)로 슬라이싱해 전달한다.

[P1-B: 호라이즌별 독립 가중치]
  버킷(short/long 묶음) → 6개 호라이즌 완전 독립.
  1m 노이즈가 3m·5m 가중치에 전파되는 문제 해소.

[P3(288차): 3클래스 → 방향 이진화]
  FLAT은 threshold(레이블 임계값)가 이미 결정하는 몫이므로 SGD는 UP/DN 방향만
  학습·예측한다. actual_label==FLAT인 표본은 learn()에서 그대로 스킵(기권) —
  P1-C의 FLAT sample_weight 보정은 FLAT이 학습 대상에서 아예 빠지며 불필요해져 제거.
  predict_proba()는 up/down만 반환하고, blend_with_gbm()은 GBM의 flat 질량을 그대로
  보존한 채 (1-flat) 안에서 up/down 비율만 SGD 의견으로 조정한다 — SGD가 flat 여부
  자체를 뒤집는 일은 구조적으로 불가능해짐.

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
    SGD_BLEND_DISABLED_HORIZONS,
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
    "10m": 0.48, "15m": 0.50,
    # 30m는 랜덤워크에 근접해 52% 달성이 구조적으로 어려움 → SGD 바닥 고착 방지
    "30m": 0.42,
}


class OnlineLearner:
    """SGD 온라인 자가학습기 — 호라이즌별 완전 독립 가중치 (Phase C 대응)"""

    ACCURACY_WINDOW = 100       # 호라이즌별 독립 100분 윈도우
    _ADJUST_EVERY   = 1         # 1건 학습마다 조정 (호라이즌 독립이므로 묶음 불필요)
    _MIN_SAMPLES    = 15        # 가중치 조정 최소 샘플 수

    # SGD 단방향 붕괴 감지 임계
    # 95%→80%: 5m SGD는 극단 확신을 잘 찍지 않아 DN=83% 편향에서도 미발동됐던 문제 해소
    # 15→12분: BiasReset(5분)보다 길고 기존(15분)보다 짧은 중간값, 데이터 최저 발동 Bias 76%에서 마진 확보
    _COLLAPSE_THR   = 0.80
    _COLLAPSE_TICKS = 12

    # 바닥 회복 파라미터
    _FLOOR_RECOVERY_INTERVAL = 30
    _FLOOR_RECOVERY_ACC_MIN  = 0.40
    _FLOOR_RECOVERY_DELTA    = 0.005
    _FLOOR_RECOVERY_MAX_UP   = 0.05

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

        x: 호라이즌 전용 슬라이싱된 피처 벡터 (SGD_FEATURE_NAMES_BY_HORIZON, 5개).
           GBM 피처셋과 별도 — config.settings.SGD_FEATURE_NAMES_BY_HORIZON 참조.

        [P3] actual_label==FLAT이면 학습을 스킵한다. FLAT은 threshold(레이블 임계값)가
        이미 결정한 결과이므로 SGD가 다시 배울 대상이 아니고, 방향(UP/DN) 이진분류기에
        FLAT 레이블을 섞으면 클래스 정의 자체가 어긋난다.
        """
        if horizon not in self.models:
            return
        if actual_label == DIRECTION_FLAT:
            return

        x2d = x.reshape(1, -1)
        scaler = self.scalers[horizon]

        # 피처 수 불일치 방어: 피처셋 교체 전환기에 스케일러가 이전 피처 수로 학습된
        # 상태에서 새 슬라이싱 피처가 들어오면 partial_fit에서 ValueError 반복 진입.
        # 불일치 감지 시 스케일러·모델을 함께 리셋해 새 피처 공간에 재적응.
        clf = self.models[horizon]
        classes = np.array([DIRECTION_DOWN, DIRECTION_UP])
        _dim_mismatch   = hasattr(scaler, "n_features_in_") and scaler.n_features_in_ != x2d.shape[1]
        # [P3] 클래스 체계 불일치 방어: 구 3클래스(-1,0,1) 모델이 남아있으면 이진 classes로
        # partial_fit 시 sklearn이 ValueError 발생 — 배포 직후 전환기 1회성 가드.
        _cls_mismatch   = hasattr(clf, "classes_") and set(clf.classes_.tolist()) != set(classes.tolist())
        if _dim_mismatch or _cls_mismatch:
            logger.warning(
                "[OnlineLearner] %s %s → 리셋",
                horizon,
                "피처 수 불일치" if _dim_mismatch else "클래스 체계 변경(3클래스→이진)",
            )
            self._do_sgd_reset(horizon)
            scaler = self.scalers[horizon]
            clf = self.models[horizon]

        scaler.partial_fit(x2d)
        xs = scaler.transform(x2d)

        clf.partial_fit(
            xs, [actual_label],
            classes=classes,
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
        """SGD 예측 — [P3] UP/DN 방향만 반환한다 (flat 키 없음, blend_with_gbm 참조).

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
            "up":   proba_map.get(DIRECTION_UP,   0.5),
            "down": proba_map.get(DIRECTION_DOWN, 0.5),
        }

        # SGD 단방향 붕괴 감지: up/dn > _COLLAPSE_THR 연속 _COLLAPSE_TICKS회 → 리셋
        # [P3] flat은 SGD가 더 이상 예측하지 않으므로 붕괴 감지 대상에서 제외
        collapse_dir = None
        if result["up"]   > self._COLLAPSE_THR:
            collapse_dir = "up"
        elif result["down"] > self._COLLAPSE_THR:
            collapse_dir = "dn"

        if collapse_dir:
            if collapse_dir == self._sgd_collapse_dir.get(horizon, ""):
                self._sgd_collapse_ticks[horizon] = self._sgd_collapse_ticks.get(horizon, 0) + 1
            else:
                self._sgd_collapse_ticks[horizon] = 1
                self._sgd_collapse_dir[horizon] = collapse_dir

            if self._sgd_collapse_ticks[horizon] >= self._COLLAPSE_TICKS:
                self._do_sgd_reset(horizon)
                logger.info(
                    "[OnlineLearner] %s SGD %s붕괴 자동 복구 (≥%d%% %d분 지속) "
                    "→ 모델·스케일러 리셋",
                    horizon, collapse_dir.upper(),
                    int(self._COLLAPSE_THR * 100), self._COLLAPSE_TICKS,
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

        [P3] SGD는 UP/DN 방향 이진 확률만 갖고 있다(sgd_proba["up"]가 곧 방향 비율).
        GBM의 flat 질량은 그대로 보존하고, (1-flat) 예산 안에서 up/down 배분 비율만
        GBM·SGD 가중 평균으로 조정한다 — SGD가 flat 여부 자체를 뒤집을 수 없다.

        [P5] SGD_BLEND_DISABLED_HORIZONS(1m/15m/30m)는 학습은 계속하되 블렌딩엔
        반영하지 않는다 — 표본 부족·신호 부재로 온라인 학습이 기여할 수 없다고
        판단된 "정직한 손절" 호라이즌. GBM 확률을 그대로 반환.
        """
        if sgd_proba is None or horizon in SGD_BLEND_DISABLED_HORIZONS:
            return gbm_proba

        h_count = self._horizon_counts.get(horizon, 0)
        gbm_flat = gbm_proba.get("flat", 1/3)
        gbm_up   = gbm_proba.get("up", 1/3)
        gbm_dn   = gbm_proba.get("down", 1/3)

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

        gbm_dir_mass  = gbm_up + gbm_dn
        gbm_up_ratio  = gbm_up / gbm_dir_mass if gbm_dir_mass > 0 else 0.5
        sgd_up_ratio  = sgd_proba.get("up", 0.5)
        blended_up_ratio = gbm_up_ratio * w_gbm + sgd_up_ratio * w_sgd

        non_flat_mass = max(0.0, 1.0 - gbm_flat)
        blended = {
            "up":   blended_up_ratio * non_flat_mass,
            "down": (1.0 - blended_up_ratio) * non_flat_mass,
            "flat": gbm_flat,
        }
        total = sum(blended.values())
        if total > 0:
            blended = {k: v / total for k, v in blended.items()}
        return blended

    # ── 가중치 조정 ─────────────────────────────────────────────
    def _adjust_weights(self, horizon: str):
        """호라이즌별 독립 정확도 기반 SGD 비중 조정.

        [P5] 블렌딩 비활성 호라이즌은 _sgd_w/_gbm_w가 애초에 안 쓰이므로
        조정 자체를 스킵 — 안 읽히는 값을 튜닝하는 척하는 로그를 남기지 않는다.
        """
        if horizon in SGD_BLEND_DISABLED_HORIZONS:
            return
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

    @property
    def sample_count(self) -> int:
        """reset_daily() 이후 누적된 당일 전체 학습(검증) 표본 수 — 호라이즌 합산"""
        return self._sample_count

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

    def horizon_acc_samples(self, horizon: str) -> int:
        """호라이즌별 정확도 버퍼 표본 수 — horizon_accuracy()의 5건 미만 가드 판별용 (대시보드 표시)"""
        return len(self._acc_buf.get(horizon, ()))

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

    def _do_sgd_reset(self, horizon: str) -> None:
        """모델·스케일러·가중치·붕괴 카운터 리셋 공통 로직."""
        self.models[horizon] = self.models[horizon].__class__(
            loss="log", learning_rate="optimal", alpha=0.001,
            max_iter=1, warm_start=True, random_state=42, n_jobs=1,
        )
        self.scalers[horizon] = self.scalers[horizon].__class__()
        self._fitted[horizon] = False
        self._sgd_w[horizon]  = SGD_WEIGHT_DEFAULT
        self._gbm_w[horizon]  = GBM_WEIGHT_DEFAULT
        self._sgd_collapse_ticks[horizon] = 0
        self._sgd_collapse_dir[horizon]   = ""
        self._floor_ticks[horizon]        = 0

    def boost_sgd_for_bias(self, horizon: str, target_w: float = 0.15) -> None:
        """GBM 방향 편향 감지 시 해당 호라이즌 SGD 비중 복구 (가중치만)."""
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

    def reset_sgd_for_bias(self, horizon: str) -> None:
        """BiasReset 발동 시 해당 호라이즌 SGD 전체 리셋.

        boost_sgd_for_bias(가중치만 올림)와 달리 오염된 모델 파라미터 자체를 제거.
        BiasReset uniform fallback 기간 중 실행되므로 SGD 공백이 fallback과 동기화됨.
        """
        self._do_sgd_reset(horizon)
        logger.info(
            "[OnlineLearner] %s BiasReset 연계 SGD 리셋 → 모델·스케일러·가중치 초기화",
            horizon,
        )

    def reset_daily(self):
        """일간 리셋 — 모델 가중치 유지, 정확도 버퍼만 초기화."""
        for h in HORIZONS:
            self._acc_buf[h].clear()
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
            self._sgd_w[h] = SGD_WEIGHT_DEFAULT
            self._gbm_w[h] = GBM_WEIGHT_DEFAULT
            self._learn_count[h] = 0
            self._floor_ticks[h] = 0
            self._sgd_collapse_ticks[h] = 0
            self._sgd_collapse_dir[h] = ""
        self._sample_count = 0
        self._horizon_counts = {h: 0 for h in HORIZONS}
        logger.info("[OnlineLearner] 완전 초기화 — 모델·스케일러·가중치 전체 리셋")
