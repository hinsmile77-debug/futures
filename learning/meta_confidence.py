# learning/meta_confidence.py — 메타 신뢰도 학습기 (TIER S)
"""
"이 상황에서 내 예측이 얼마나 신뢰할 만한가"를 별도 학습

Renaissance Technologies의 핵심 기법:
  주 모델(GBM + SGD) 예측 → 메타 모델이 신뢰도 점수 부여
  → 신뢰도 낮은 구간에서 사이즈 자동 축소

v4 변경:
  - 레짐별 독립 LR 모델 4개 (추세장/횡보장/급변장/혼합)
  - selection bias 해소는 main.py _meta_shadow 에서 처리
  - 레짐 특성이 다른 구간을 하나의 LR로 학습하면 공선성 발생
    → 레짐별 분리로 각 구간 특화 학습

입력 피처 (컨텍스트):
  - 시장 레짐 (추세/횡보/급변)
  - Hurst 지수
  - 최근 N분 정확도
  - 변동성 수준 (ATR ratio)
  - 시간대
  (mlofi_norm / cancel_add_ratio 는 EnsembleGater 전담 → 중복 제외)

출력:
  confidence_score: 0.0 ~ 1.0  (정상 범위 0.40~0.70)
  size_multiplier:  0.0 ~ 1.5
"""
import copy
import threading
import numpy as np
import logging
from collections import deque
from typing import Dict, Optional, List, Tuple

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False

logger = logging.getLogger("LEARNING")

# 4개 레짐 키 — 순서 고정 (save/load 정합성)
_REGIME_KEYS: Tuple[str, ...] = ("추세장", "횡보장", "급변장", "혼합")

# regime_code(float) → regime 키 역방향 매핑
_CODE_TO_REGIME: Dict[float, str] = {
    1.0:  "추세장",
    -1.0: "횡보장",
    -2.0: "급변장",
    0.0:  "혼합",
}


class MetaConfidenceLearner:
    """
    예측 신뢰도를 별도 학습하는 메타 모델 (v4)

    레짐별 독립 LR 4개 + 4급 품질 레이블 + 30분 배치 학습
    → meta_raw 0.40~0.70 정상 범위 달성
    """

    ACCURACY_WINDOW        = 20   # 최근 N분 정확도 추적
    MIN_SAMPLES_PER_REGIME = 30   # 레짐별 최초 학습 최소 샘플 (≈30분)
    BATCH_INTERVAL         = 30   # 레짐별 배치 재학습 주기 (봉 수)
    CONF_HIGH              = 0.60 # 고신뢰도 기준 (Q2/Q3 경계)
    _BUF_MAX               = 300  # 레짐별 최대 버퍼 (≈5시간)
    # 피처 버전 — 피처 셋·모델 구조 변경 시 올려서 구버전 pkl warm-start 자동 거부
    _FEATURE_VERSION = 4          # v4: 레짐별 독립 LR (v3: 단일 LR)

    # Q0(최하·틀림+고신뢰)=0.00, Q1(하·틀림+저신뢰)=0.33
    # Q2(상·맞음+저신뢰)=0.67,   Q3(최상·맞음+고신뢰)=1.00
    _QUALITY_WEIGHTS = [0.0, 1/3, 2/3, 1.0]

    def __init__(self):
        if not _SKLEARN_OK:
            logger.warning("[MetaConf] sklearn 없음 — 규칙 기반 모드로 동작")

        # 레짐별 독립 모델·스케일러·상태
        self._models:  Dict[str, object] = {}
        self._scalers: Dict[str, object] = {}
        self._fitted:  Dict[str, bool]   = {}

        # 레짐별 학습 버퍼: (feats, confidence, correct) 트리플
        self._bufs: Dict[str, List[Tuple[List[float], float, bool]]] = {}

        # 레짐별 샘플 카운터 및 마지막 fit 카운터
        self._sample_counts:   Dict[str, int] = {}
        self._last_fit_counts: Dict[str, int] = {}

        for r in _REGIME_KEYS:
            if _SKLEARN_OK:
                # lbfgs: 소규모(30~300 샘플, 7피처) 다중클래스에 최적
                # class_weight='balanced': Q0~Q3 빈도 불균형 보정
                self._models[r]  = LogisticRegression(
                    C=1.0, max_iter=1000, solver='lbfgs', class_weight='balanced',
                )
                self._scalers[r] = StandardScaler()
            else:
                self._models[r]  = None
                self._scalers[r] = None
            self._fitted[r]          = False
            self._bufs[r]            = []
            self._sample_counts[r]   = 0
            self._last_fit_counts[r] = 0

        # 전체 통계
        self._total_count  = 0
        self._accuracy_buf = deque(maxlen=self.ACCURACY_WINDOW)
        self._conf_history = deque(maxlen=200)

        # 레짐별 신뢰도 히스토리 (모니터링용)
        self._conf_hist_by_regime: Dict[str, deque] = {
            r: deque(maxlen=100) for r in _REGIME_KEYS
        }

        # 비동기 LR.fit() 상태 — GIL 경합 제거
        self._fit_lock     = threading.Lock()
        self._fit_running: Dict[str, bool]  = {r: False for r in _REGIME_KEYS}
        self._pending_fitted: Dict[str, tuple] = {}

    # ── 피처 유틸 ─────────────────────────────────────────────────

    def _coerce_feature_vector(self, meta_features) -> Optional[List[float]]:
        if not isinstance(meta_features, (list, tuple, np.ndarray)):
            return None
        flat: List[float] = []
        try:
            for value in list(meta_features):
                if isinstance(value, (list, tuple, np.ndarray)):
                    if np.size(value) != 1:
                        return None
                    value = np.asarray(value).reshape(-1)[0]
                flat.append(float(value))
        except Exception:
            return None
        if len(flat) != 7:
            return None
        return flat

    def _decode_regime(self, features: List[float]) -> str:
        """features[0](regime_code) → regime 키.  알 수 없으면 '혼합'."""
        code = round(float(features[0]), 1)
        return _CODE_TO_REGIME.get(code, "혼합")

    def build_meta_features(
        self,
        regime:             str,   # "추세장" / "횡보장" / "급변장" / "혼합"
        hurst:              float,
        atr_ratio:          float, # ATR / ATR_평균
        hour_minute:        int,   # HHMM (e.g. 1030)
        recent_accuracy:    float, # 최근 N분 정확도
        signal_strength:    float, # 앙상블 신호 강도 (0~1) — cal_gap 계산용으로만 사용
        horizon_agreement:  float = 0.5,  # 호라이즌 방향 일치율 0~1
    ) -> List[float]:
        """
        메타 피처 벡터 (7개) — v2/v3/v4 동일
        [regime_code, hurst, atr_ratio, time_code, recent_acc, cal_gap, horizon_agreement]
        """
        regime_map = {"추세장": 1.0, "횡보장": -1.0, "급변장": -2.0, "혼합": 0.0}
        regime_code = regime_map.get(regime, 0.0)

        if   hour_minute < 1030:  time_code =  1.0
        elif hour_minute < 1400:  time_code =  0.0
        elif hour_minute < 1500:  time_code = -0.5
        else:                     time_code = -1.0

        # calibration 갭: 양수(과신 중) → MetaConf 낮춰야, 음수(과소신뢰) → 높여도 됨
        cal_gap = float(np.clip(signal_strength - recent_accuracy, -0.5, 0.5))

        return [
            regime_code,
            float(hurst),
            float(atr_ratio),
            float(time_code),
            float(recent_accuracy),
            cal_gap,
            float(np.clip(horizon_agreement, 0.0, 1.0)),
        ]

    # ── 품질 레이블 ────────────────────────────────────────────────

    def _quality_label(self, confidence: float, correct: bool) -> int:
        """4급 품질 레이블 — (confidence, correct) → Q0/Q1/Q2/Q3

        Q3(최상): 맞음 + 고신뢰  → meta_conf ↑
        Q2(상):   맞음 + 저신뢰  → meta_conf 중상
        Q1(하):   틀림 + 저신뢰  → meta_conf 중하
        Q0(최하): 틀림 + 고신뢰  → meta_conf ↓ (진입 차단)
        """
        if correct and confidence >= self.CONF_HIGH:
            return 3
        elif correct:
            return 2
        elif confidence < self.CONF_HIGH:
            return 1
        else:
            return 0

    def _proba_to_score(self, regime: str, proba: np.ndarray) -> float:
        """LR predict_proba → 0~1 신뢰도 점수 (품질 가중 평균)

        model.classes_ 가 [0,1,2,3] 부분집합일 수 있어 인덱스 매핑 필요
        """
        model = self._models[regime]
        classes = list(model.classes_)
        weights = np.array([self._QUALITY_WEIGHTS[c] for c in classes])
        return float(np.clip(np.dot(proba, weights), 0.0, 1.0))

    # ── 추론 ───────────────────────────────────────────────────────

    def predict_confidence(
        self,
        meta_features: List[float],
    ) -> dict:
        """현재 컨텍스트에서 예측 신뢰도 추정 — 레짐별 모델 라우팅"""
        meta_features = self._coerce_feature_vector(meta_features)
        if meta_features is None:
            conf   = 0.5
            source = "rule(input_invalid)"
            self._conf_history.append(conf)
            return self._make_result(conf, source)

        regime  = self._decode_regime(meta_features)
        fitted  = self._fitted.get(regime, False)
        model   = self._models.get(regime)
        scaler  = self._scalers.get(regime)

        if fitted and _SKLEARN_OK and model is not None and scaler is not None:
            try:
                X    = scaler.transform([meta_features])
                prob = model.predict_proba(X)[0]
                conf = self._proba_to_score(regime, prob)
                source = "LR[{}]".format(regime[:2])
            except Exception:
                conf   = self._rule_based_confidence(meta_features)
                source = "rule[{}](오류)".format(regime[:2])
        else:
            conf   = self._rule_based_confidence(meta_features)
            source = "rule[{}]".format(regime[:2])

        self._conf_history.append(conf)
        self._conf_hist_by_regime[regime].append(conf)

        return self._make_result(conf, source)

    @staticmethod
    def _make_result(conf: float, source: str) -> dict:
        if conf >= 0.7:
            size_mult = 1.0 + (conf - 0.7) * 2.5
        elif conf >= 0.5:
            size_mult = 0.5 + (conf - 0.5) * 2.5
        else:
            size_mult = 0.0
        return {
            "confidence_score": round(conf, 4),
            "size_multiplier":  round(min(size_mult, 1.5), 3),
            "model_source":     source,
        }

    def _rule_based_confidence(self, features: List[float]) -> float:
        """학습 전 또는 fallback용 규칙 기반 신뢰도

        features 순서 (v2/v3/v4): [regime, hurst, atr_ratio, time, acc, cal_gap, horizon_agreement]
        """
        regime, hurst, atr_ratio, time_code, acc, cal_gap, horizon_agreement = features

        score = 0.6
        if regime == 1.0:   score += 0.08   # 추세장
        if regime == -1.0:  score -= 0.15   # 횡보장
        if regime == -2.0:  score -= 0.30   # 급변장
        if hurst > 0.6:     score += 0.08
        if hurst < 0.45:    score -= 0.15
        if atr_ratio > 2.0: score -= 0.20
        score += (acc - 0.55) * 0.5
        score -= cal_gap * 0.30
        score += (horizon_agreement - 0.5) * 0.20

        return float(np.clip(score, 0.0, 1.0))

    # ── 학습 ───────────────────────────────────────────────────────

    def record_outcome(
        self,
        meta_features: List[float],
        correct: bool,
        confidence: float = 0.5,
    ):
        """예측 결과 피드백 — 레짐별 배치 학습 버퍼에 추가

        Args:
            meta_features: build_meta_features 출력값
            correct:       예측 정답 여부
            confidence:    앙상블 신뢰도 (0~1) — 4급 품질 레이블 계산용
        """
        meta_features = self._coerce_feature_vector(meta_features)
        if meta_features is None:
            logger.debug("[MetaConf] skip invalid meta_features=%r", meta_features)
            return

        regime = self._decode_regime(meta_features)

        self._accuracy_buf.append(float(correct))
        self._bufs[regime].append((meta_features, float(confidence), bool(correct)))
        if len(self._bufs[regime]) > self._BUF_MAX:
            del self._bufs[regime][:-self._BUF_MAX]
        self._sample_counts[regime] = self._sample_counts.get(regime, 0) + 1
        self._total_count += 1

    def flush_fit(self):
        """STEP 2 말미에 1회 호출 — 레짐별 비동기 배치 재학습 트리거 (GIL-free)

        LR.fit()을 daemon 스레드로 분리해 메인 스레드 GIL 블로킹 제거.
        완료된 모델은 apply_pending()으로 다음 틱 S2 진입 시 반영.
        """
        for regime in _REGIME_KEYS:
            buf_len = len(self._bufs[regime])
            cnt     = self._sample_counts.get(regime, 0)
            last    = self._last_fit_counts.get(regime, 0)
            if buf_len < self.MIN_SAMPLES_PER_REGIME or cnt - last < self.BATCH_INTERVAL:
                continue
            with self._fit_lock:
                if self._fit_running.get(regime, False):
                    continue  # 이전 틱 학습 진행 중 — 중복 실행 차단
                self._fit_running[regime] = True
            # 메인 스레드에서 스냅샷 + deep-copy (thread-safe, GIL 보호)
            snapshot    = list(self._bufs[regime])
            model_snap  = copy.deepcopy(self._models[regime])
            scaler_snap = copy.deepcopy(self._scalers[regime])
            already_fit = bool(self._fitted.get(regime, False))
            threading.Thread(
                target=self._async_fit_regime,
                args=(regime, snapshot, model_snap, scaler_snap, already_fit, cnt),
                daemon=True,
                name="MetaFit-{}".format(regime[:2]),
            ).start()

    def _async_fit_regime(self, regime, snapshot, model, scaler, already_fit, cnt):
        """daemon 스레드: LR.fit() GIL 블로킹을 메인 스레드 밖으로 이동.

        model/scaler 는 메인 스레드에서 deep-copy된 독립 객체 — 경합 없음.
        완료 후 _pending_fitted 에 저장, apply_pending()으로 swap-in.
        """
        try:
            recent = snapshot[-self._BUF_MAX:]
            pairs  = [(f, self._quality_label(c, ok)) for f, c, ok in recent]
            y      = np.array([lbl for _, lbl in pairs], dtype=np.int32)
            seen   = set(y.tolist())
            if len(seen) < 2:
                logger.debug(
                    "[MetaConf] [%s] 비동기 배치 스킵 — 클래스 다양성 부족 (%d종)",
                    regime, len(seen),
                )
                return
            X = np.array([f for f, _ in pairs], dtype=np.float32)
            if not already_fit:
                scaler.fit(X)
            X_s = scaler.transform(X)
            model.fit(X_s, y)
            logger.info(
                "[MetaConf] LR[%s] 비동기 학습 완료 (n=%d, classes=%s)",
                regime, len(pairs), sorted(seen),
            )
            with self._fit_lock:
                self._pending_fitted[regime] = (model, scaler, cnt)
        except Exception as e:
            logger.warning("[MetaConf] LR[%s] 비동기 학습 오류: %s", regime, e)
        finally:
            with self._fit_lock:
                self._fit_running[regime] = False

    def apply_pending(self):
        """메인 스레드 전용: 완료된 비동기 학습 결과를 활성 모델에 반영.

        STEP 2 진입 시 1회 호출 — 전 틱 daemon 학습 결과를 swap-in.
        predict_confidence()는 메인 스레드 전용이므로 추가 락 불필요.
        """
        with self._fit_lock:
            if not self._pending_fitted:
                return
            pending = dict(self._pending_fitted)
            self._pending_fitted.clear()
        for regime, (model, scaler, cnt) in pending.items():
            self._models[regime]          = model
            self._scalers[regime]         = scaler
            self._fitted[regime]          = True
            self._last_fit_counts[regime] = cnt
            logger.info("[MetaConf] LR[%s] 비동기 결과 반영 (cnt=%d)", regime, cnt)

    # ── 통계 ───────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        recent_acc = float(np.mean(list(self._accuracy_buf))) if self._accuracy_buf else 0.0
        avg_conf   = float(np.mean(list(self._conf_history))) if self._conf_history else 0.0

        per_regime = {}
        for r in _REGIME_KEYS:
            ch = list(self._conf_hist_by_regime[r])
            per_regime[r] = {
                "samples": self._sample_counts.get(r, 0),
                "fitted":  self._fitted.get(r, False),
                "avg_conf": round(float(np.mean(ch)), 4) if ch else None,
            }

        return {
            "total_count":     self._total_count,
            "recent_accuracy": round(recent_acc, 4),
            "avg_confidence":  round(avg_conf, 4),
            "per_regime":      per_regime,
        }

    # ── 영속화 ─────────────────────────────────────────────────────

    def save(self, path: str) -> bool:
        """학습 상태 저장 — 다음 날 warm-start용."""
        if not any(self._fitted.values()) or not _SKLEARN_OK:
            return False
        try:
            import pickle, os
            state = {
                "models":          self._models,
                "scalers":         self._scalers,
                "fitted":          self._fitted,
                "bufs":            {r: list(b[-200:]) for r, b in self._bufs.items()},
                "sample_counts":   self._sample_counts,
                "total_count":     self._total_count,
                "feature_version": self._FEATURE_VERSION,
            }
            with open(path, "wb") as f:
                pickle.dump(state, f, protocol=2)
            fitted_str = ", ".join(r for r in _REGIME_KEYS if self._fitted.get(r))
            logger.info("[MetaConf] 상태 저장 완료: %s (fitted=[%s], total=%d)",
                        os.path.basename(path), fitted_str, self._total_count)
            return True
        except Exception as e:
            logger.warning("[MetaConf] 상태 저장 실패: %s", e)
            return False

    def load(self, path: str) -> bool:
        """저장된 학습 상태 복원 — 장 시작 cold-start 제거."""
        try:
            import pickle, os
            if not os.path.exists(path):
                return False
            with open(path, "rb") as f:
                state = pickle.load(f)
            saved_ver = state.get("feature_version", 1)
            if saved_ver != self._FEATURE_VERSION:
                logger.warning(
                    "[MetaConf] warm-start 버전 불일치 (saved=%d current=%d) → cold-start",
                    saved_ver, self._FEATURE_VERSION,
                )
                return False

            loaded_models  = state.get("models", {})
            loaded_scalers = state.get("scalers", {})
            loaded_fitted  = state.get("fitted", {})
            loaded_bufs    = state.get("bufs", {})
            loaded_counts  = state.get("sample_counts", {})

            for r in _REGIME_KEYS:
                if r in loaded_models:
                    self._models[r]  = loaded_models[r]
                    self._scalers[r] = loaded_scalers.get(r, StandardScaler() if _SKLEARN_OK else None)
                    self._fitted[r]  = loaded_fitted.get(r, False)
                    self._bufs[r]    = loaded_bufs.get(r, [])
                    cnt = loaded_counts.get(r, 0)
                    self._sample_counts[r]   = cnt
                    self._last_fit_counts[r] = cnt  # 로드 직후 불필요한 즉시 재학습 방지

            self._total_count = state.get("total_count", 0)
            fitted_str = ", ".join(r for r in _REGIME_KEYS if self._fitted.get(r))
            logger.info("[MetaConf] 상태 복원 완료: %s (fitted=[%s], total=%d, ver=%d)",
                        os.path.basename(path), fitted_str, self._total_count, self._FEATURE_VERSION)
            return True
        except Exception as e:
            logger.warning("[MetaConf] 상태 복원 실패 (cold-start로 진행): %s", e)
            return False

    def reset_daily(self):
        """일일 마감 시 정확도 버퍼 초기화 (모델·버퍼는 warm-start용으로 유지)"""
        self._accuracy_buf.clear()
        for r in _REGIME_KEYS:
            self._conf_hist_by_regime[r].clear()


# ── 단독 실행 테스트 ─────────────────────────────────────────────

if __name__ == "__main__":
    import os
    mc = MetaConfidenceLearner()

    print("=== 4급 품질 레이블 확인 ===")
    print(f"맞음+고신뢰(Q3): {mc._quality_label(0.72, True)}")    # 3
    print(f"맞음+저신뢰(Q2): {mc._quality_label(0.55, True)}")    # 2
    print(f"틀림+저신뢰(Q1): {mc._quality_label(0.55, False)}")   # 1
    print(f"틀림+고신뢰(Q0): {mc._quality_label(0.72, False)}")   # 0

    print("\n=== 규칙 기반 (학습 전) ===")
    feats_trend = mc.build_meta_features(
        regime="추세장", hurst=0.62, atr_ratio=1.1,
        hour_minute=1030, recent_accuracy=0.65, signal_strength=0.75,
    )
    feats_range = mc.build_meta_features(
        regime="횡보장", hurst=0.42, atr_ratio=0.9,
        hour_minute=1400, recent_accuracy=0.48, signal_strength=0.4,
    )
    feats_vol = mc.build_meta_features(
        regime="급변장", hurst=0.38, atr_ratio=2.5,
        hour_minute=930, recent_accuracy=0.40, signal_strength=0.55,
    )
    for name, feats in [("추세장", feats_trend), ("횡보장", feats_range), ("급변장", feats_vol)]:
        r = mc.predict_confidence(feats)
        print(f"[{name}] conf={r['confidence_score']:.4f}, src={r['model_source']}")

    print("\n=== 레짐별 LR 학습 시뮬레이션 (각 35샘플) ===")
    rng = np.random.default_rng(42)
    regime_list = ["추세장", "횡보장", "급변장", "혼합"]
    for regime in regime_list:
        for i in range(35):
            f = mc.build_meta_features(
                regime=regime,
                hurst=float(rng.uniform(0.4, 0.7)),
                atr_ratio=float(rng.uniform(0.8, 2.5)),
                hour_minute=int(rng.choice([930, 1030, 1200, 1400, 1500])),
                recent_accuracy=float(rng.uniform(0.35, 0.70)),
                signal_strength=float(rng.uniform(0.50, 0.80)),
                horizon_agreement=float(rng.uniform(0.3, 0.8)),
            )
            mc.record_outcome(f, bool(rng.random() > 0.45), float(rng.uniform(0.50, 0.75)))
    mc.flush_fit()

    print("\n=== LR 학습 후 레짐별 출력 ===")
    for name, feats in [("추세장", feats_trend), ("횡보장", feats_range), ("급변장", feats_vol)]:
        r = mc.predict_confidence(feats)
        print(f"[{name}] conf={r['confidence_score']:.4f}, src={r['model_source']}")

    print("\n=== 레짐별 통계 ===")
    stats = mc.get_stats()
    for r, s in stats["per_regime"].items():
        print(f"  {r}: samples={s['samples']}, fitted={s['fitted']}, avg_conf={s['avg_conf']}")
