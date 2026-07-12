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

    MIN_SAMPLES   = 80     # 최소 보정 샘플
    # 6/29 분석: WINDOW=100에서 conf≥0.6 tail 샘플 ~7건 → tail 보정 불안정.
    # 200으로 복원: tail 샘플 ~15건 확보, 시장 컨디션 적응(~3.4일)과 tail 안정성 균형.
    WINDOW        = 200    # 슬라이딩 윈도우 (최근 N개만 사용)

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
                # C 이력: 1.0 → 0.1 → 0.05 → 0.02
                # 6/29 분석: WINDOW=200(tail ~15건) + C=0.02로 tail 압축 추가 강화.
                # C=0.05에서 conf 0.7+ tail이 여전히 0.7+ 출력 — 실측 acc 29-31%.
                # C=0.02: 계수 w를 더 0에 가깝게 → tail의 sigmoid가 base rate(33%)에 더 밀착.
                self._model = LogisticRegression(C=0.02, solver="lbfgs")

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

        # 주기적 재보정 (85차: 50→20, 6/11: 20→10, 6/29: 10→5 — 200건 윈도우에서 tail 반영 속도 향상)
        if self._n % 5 == 0 and self._n >= self.MIN_SAMPLES:
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


# ── [311차 후속 B안] 극단성 보정 — 2단 구조(빠른 raw_prob 보정과 분리) ────────
# Phase 0/1 딥다이브 결론:
#   1) 선형 가산항으로는 tail 집중 효과를 못 잡음 — 30m 전체배치에서 vwap_hinge
#      계수가 +0.03~+0.25(반대 방향)로 나옴. 실측 분해 결과 이 효과는
#      conf<0.55에서는 거의 없고 conf≥0.55에서만 강하게 나타나는 상호작용
#      패턴(30m: hinge>0 acc=0.234 vs hinge=0 acc=0.426, t=-5.38 p<0.0001)이라
#      raw_prob×extra 상호작용항이 있어야 학습 가능(추가 후 계수 정상 부호 회귀).
#   2) 그런데 PredictionCalibrator의 실거래 WINDOW=200(빠른 시장적응용)에서는
#      conf≥0.55 & hinge>0 교집합이 6~58건뿐이라 5파라미터 모델이 안정적으로
#      학습되지 않음(전체배치 5,278건에서는 잘 되던 게 200건에서는 실패).
#   → raw_prob 보정(빠른層, WINDOW=200, 기존 PredictionCalibrator 그대로)과
#     극단성 보정(느린層, GBM 배치재학습과 같은 리듬으로 큰 배치에서만 재적합)을
#     분리. ExtremityCorrector는 "빠른層이 이미 보정한 확률"에서 극단성으로
#     인한 초과 과신분만 추가로 깎는 감산 보정치를 계산한다.
EXTREMITY_VWAP_THRESHOLD = -1.5
EXTREMITY_BB_THRESHOLD   = -0.3


def compute_extremity_hinge(
    features: dict,
    direction: int,
    vwap_threshold: float = EXTREMITY_VWAP_THRESHOLD,
    bb_threshold: float = EXTREMITY_BB_THRESHOLD,
) -> np.ndarray:
    """예측방향 기준으로 부호 정렬한 bb_position/vwap_position의 힌지(hinge) 값.

    "가격이 예측방향 반대편 밴드/VWAP 극단으로 밀린 상태에서 그 방향을 확신"하는
    꼬리과적합 패턴(docs 레슨런 딥다이브)을 계량화. 문턱 이내(정상 범위)면 0,
    문턱을 넘어 반대극단으로 갈수록 선형 증가.

    Returns:
        np.array([bb_hinge, vwap_hinge]) — 둘 다 0 이상, 클수록 극단적 반대베팅.
    """
    if direction == 0:
        return np.zeros(2)
    sign = 1 if direction > 0 else -1
    bb   = float(features.get("bb_position", 0.5) or 0.5)
    vwap = float(features.get("vwap_position", 0.0) or 0.0)
    bb_signed   = (bb - 0.5) * sign
    vwap_signed = vwap * sign
    bb_hinge   = max(0.0, bb_threshold - bb_signed)
    vwap_hinge = max(0.0, vwap_threshold - vwap_signed)
    return np.array([bb_hinge, vwap_hinge])


# ── [311차 후속 ②안] 규칙 기반 최소 보정폭(안전망) ────────────────────────
# ExtremityCorrector(reg_scale=1.0, C=0.02 균일 정규화)의 학습된 보정폭은 방향은
# 맞지만 얇은 표본(30m 기준 극단∩고conf 58건) 탓에 약함(Phase 1 실측: 30m 2.1%p
# 보정 vs 실제격차 33.7%p). 이미 두 지표(realized_move·정확도)로 재현된 최악
# 패턴(conf≥0.55 & 극단피처)엔 학습된 값과 무관하게 최소 보정폭을 규칙으로
# 못박아 안전망 역할을 하게 한다. AdaptiveKelly.MIN_MULT=0.1, ToxicityGate
# reduce=0.7 고정상수와 같은 패턴 — 실전 전환 전 재검토 대상(교집합 표본이
# 충분해지면 학습된 값이 이 하한을 자연히 상회하게 되고, 그때부터는 floor가
# 사실상 무의미해지며 자동으로 학습된 보정으로 넘어간다 — max()로 결합하므로
# 별도 스위치 전환 없이 자연 인수인계됨).
EXTREMITY_FLOOR_CONF_THRESHOLD = 0.55
EXTREMITY_FLOOR_MIN_PENALTY    = 0.05


def extremity_floor_penalty(raw_prob: float, extra_features) -> float:
    """conf≥EXTREMITY_FLOOR_CONF_THRESHOLD & 극단(hinge>0)이면 최소 보정폭 반환."""
    if raw_prob < EXTREMITY_FLOOR_CONF_THRESHOLD:
        return 0.0
    extra = np.asarray(extra_features, dtype=float)
    if not np.any(extra > 0):
        return 0.0
    return EXTREMITY_FLOOR_MIN_PENALTY


class ExtremityCorrector:
    """[311차 후속 B안] GBM 꼬리과적합(극단 피처 → 과신) 느린-재적합 보정 레이어.

    PredictionCalibrator(WINDOW=200, 빠른 시장적응)와 완전히 분리된 별도 버퍼로,
    훨씬 큰 배치(BATCH_SIZE)가 쌓여야만 재적합한다. 극단성-과신 관계는 시장
    컨디션이 아니라 GBM 모델 자체의 구조적 특성(재학습 전까지 안 변함)이라
    빠르게 재적합할 이유가 없고, 오히려 상호작용항(raw_prob×hinge)을 안정적으로
    학습하려면 더 많은 표본이 필요하다(Phase 1 검증: 200건 표본에서는 실패,
    5,278건에서는 성공).

    fit()은 main.py의 GBM 배치재학습(EOD/장중)과 같은 타이밍에 명시적으로
    호출하는 것을 전제로 한다 — record()가 자동으로 fit()을 트리거하지 않음
    (fast layer와 달리 온라인 자동 재적합 없음).
    """

    MIN_SAMPLES = 1000     # fast layer(80)보다 훨씬 큰 표본 요구 — 상호작용항 안정성
    BATCH_SIZE  = 5000     # 슬라이딩이 아니라 "최근 N건 배치" — GBM 재학습 주기와 유사

    def __init__(self, n_extra_features: int = 2, reg_scale: float = 1.0):
        """
        Args:
            n_extra_features: hinge 피처 수 (예: [bb_hinge, vwap_hinge] = 2)
            reg_scale: [311차 후속 ①안] hinge/interaction 컬럼에만 적용하는 스케일
                계수(>1). L2 페널티는 λ·w²라서 피처를 k배 키워 학습하면 그 피처의
                실효 정규화 강도가 1/k²로 약해짐(raw_prob 자신의 계수·C=0.02는 그대로
                유지) — sklearn이 계수별 개별 C를 지원하지 않아 쓰는 우회 기법.
                1.0=기존 균일-C 동작과 완전히 동일(라이브 안전망용), >1=완화된
                정규화(섀도우 검증용, 아직 라이브 반영 금지 — 58건 같은 얇은 표본에서
                분산이 커질 위험 있어 여러 시점 분할로 안정성 확인 전까지 로그 전용).
        """
        self.n_extra_features = int(n_extra_features)
        self.reg_scale = float(reg_scale)
        self._probs   = deque(maxlen=self.BATCH_SIZE)
        self._extra   = deque(maxlen=self.BATCH_SIZE)
        self._labels  = deque(maxlen=self.BATCH_SIZE)
        self._n       = 0
        self._fitted  = False
        self._model: Optional[object] = None
        if _SKLEARN_OK:
            self._model = LogisticRegression(C=0.02, solver="lbfgs", max_iter=1000)

    def record(self, raw_prob: float, extra_features, actual_correct: bool) -> None:
        self._probs.append(float(raw_prob))
        self._extra.append(np.asarray(extra_features, dtype=float))
        self._labels.append(1 if actual_correct else 0)
        self._n += 1

    def _build_X(self, probs: np.ndarray, extra_arr: np.ndarray) -> np.ndarray:
        probs = probs.reshape(-1, 1)
        extra_scaled = extra_arr * self.reg_scale
        interaction = probs * extra_scaled
        return np.hstack([probs, extra_scaled, interaction])

    def fit(self) -> bool:
        """명시적으로 호출 — GBM 배치재학습과 같은 타이밍에서만 실행할 것."""
        if not _SKLEARN_OK or len(self._probs) < self.MIN_SAMPLES:
            return False
        probs  = np.array(list(self._probs))
        extra  = np.array(list(self._extra))
        labels = np.array(list(self._labels))
        try:
            self._model.fit(self._build_X(probs, extra), labels)
            self._fitted = True
            logger.info(f"[ExtremityCorrector] 재적합 완료 (n={len(probs)})")
            return True
        except Exception as e:
            logger.warning(f"[ExtremityCorrector] fit 오류: {e}")
            return False

    def penalty(self, raw_prob: float, extra_features) -> float:
        """극단성으로 인해 깎여야 할 확률량(양수 = 과신 보정, 음수도 이론상 허용).

        extra_features가 전부 0(정상 범위)이면 항상 0을 반환 — 즉 정상 피처
        구간에서는 fast layer의 결과에 아무 영향을 주지 않는다.
        """
        if not self._fitted:
            return 0.0
        extra = np.asarray(extra_features, dtype=float).reshape(1, -1)
        if not np.any(extra):
            return 0.0
        zero = np.zeros_like(extra)
        p_base = self._model.predict_proba(self._build_X(np.array([raw_prob]), zero))[0][1]
        p_ext  = self._model.predict_proba(self._build_X(np.array([raw_prob]), extra))[0][1]
        return float(p_base - p_ext)

    def correct(self, raw_prob: float, fast_calibrated_prob: float, extra_features) -> float:
        """PredictionCalibrator(빠른層)의 결과 위에 극단성 감산 보정을 적용."""
        penalty = self.penalty(raw_prob, extra_features)
        return float(np.clip(fast_calibrated_prob - penalty, 0.0, 1.0))

    @property
    def is_fitted(self) -> bool:
        return self._fitted

    @property
    def n_samples(self) -> int:
        return self._n


# [311차 후속 ①안] 섀도우 모델의 hinge/interaction 스케일 계수.
# C_effective ≈ 0.02 × SHADOW_REG_SCALE² = 0.18 (라이브의 0.02보다 9배 완화).
# 아직 실거래 반영 안 함 — 여러 시점 분할로 안정성 확인 전까지 로그 전용.
SHADOW_REG_SCALE = 3.0


class MultiHorizonExtremityCorrector:
    """호라이즌별 독립 ExtremityCorrector 쌍(라이브+섀도우) 묶음.

    - live: reg_scale=1.0 (기존 균일 C=0.02) — floor(②안)와 max()로 결합해
      correct_with_floor()의 실제 반환값에 반영된다.
    - shadow: reg_scale=SHADOW_REG_SCALE(①안, 완화된 정규화) — 로그/비교 전용,
      correct_with_floor()가 반환하는 calibrated_prob에는 전혀 영향을 주지
      않는다. 여러 시점 분할로 안정성이 확인되기 전까지는 live로 승격하지 않는다.
    """

    def __init__(
        self,
        horizons: List[str],
        n_extra_features: int = 2,
        shadow_reg_scale: float = SHADOW_REG_SCALE,
    ):
        self.correctors = {
            h: ExtremityCorrector(n_extra_features=n_extra_features, reg_scale=1.0)
            for h in horizons
        }
        self.shadow_correctors = {
            h: ExtremityCorrector(n_extra_features=n_extra_features, reg_scale=shadow_reg_scale)
            for h in horizons
        }

    def record(self, horizon: str, raw_prob: float, extra_features, actual_correct: bool) -> None:
        if horizon in self.correctors:
            self.correctors[horizon].record(raw_prob, extra_features, actual_correct)
            self.shadow_correctors[horizon].record(raw_prob, extra_features, actual_correct)

    def correct(self, horizon: str, raw_prob: float, fast_calibrated_prob: float, extra_features) -> float:
        """학습된 live 모델만 적용 — floor 미포함 하위호환용."""
        if horizon in self.correctors:
            return self.correctors[horizon].correct(raw_prob, fast_calibrated_prob, extra_features)
        return fast_calibrated_prob

    def correct_with_floor(
        self, horizon: str, raw_prob: float, fast_calibrated_prob: float, extra_features
    ) -> dict:
        """[311차 후속 ①+②안 병행] floor(규칙)와 live 학습모델 중 더 보수적인(강한)
        보정을 적용. 섀도우(①안, 완화된 정규화) 결과는 diagnostics에만 포함되고
        반환되는 calibrated_prob에는 영향을 주지 않는다 — 섀도우가 충분히 검증되면
        live의 reg_scale을 올려 자연스럽게 승격시킨다.

        Returns:
            {calibrated_prob, floor_penalty, live_penalty, shadow_penalty, applied_penalty}

        horizon이 이 인스턴스의 적용 범위(생성자 horizons)에 없으면 전부 0으로
        패스스루한다 — [311차 후속 30m 전용 축소] Phase 3 워크포워드 종합검증에서
        30m 외 호라이즌은 기존 빠른層 calibrator가 이미 실제정확도에 근접해 있어
        (예: 3m 오차 0.003) 극단성 보정이 오히려 ECE를 악화시킴(6개 호라이즌 전부
        ECE 상승). floor 규칙(extremity_floor_penalty) 자체는 호라이즌을 보지
        않으므로, 범위 밖 호라이즌엔 아예 진입하지 않게 여기서 차단해야 한다.
        """
        if horizon not in self.correctors:
            return {
                "calibrated_prob": fast_calibrated_prob,
                "floor_penalty": 0.0, "live_penalty": 0.0,
                "shadow_penalty": 0.0, "applied_penalty": 0.0,
            }
        floor_pen = extremity_floor_penalty(raw_prob, extra_features)
        live_pen = self.correctors[horizon].penalty(raw_prob, extra_features)
        shadow_pen = self.shadow_correctors[horizon].penalty(raw_prob, extra_features)
        applied_penalty = max(floor_pen, live_pen)
        calibrated = float(np.clip(fast_calibrated_prob - applied_penalty, 0.0, 1.0))
        return {
            "calibrated_prob": calibrated,
            "floor_penalty": floor_pen,
            "live_penalty": live_pen,
            "shadow_penalty": shadow_pen,
            "applied_penalty": applied_penalty,
        }

    def fit_all(self) -> dict:
        return {
            "live":   {h: c.fit() for h, c in self.correctors.items()},
            "shadow": {h: c.fit() for h, c in self.shadow_correctors.items()},
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
