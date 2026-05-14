# model/multi_horizon_model.py — GBM 멀티 호라이즌 예측 모델
"""
6개 호라이즌(1·3·5·10·15·30분)에 대한 GBM 모델 관리.

- 학습: GBM (GradientBoostingClassifier)
- 저장/로드: joblib (.pkl)
- 30분마다 배치 재학습 (batch_retrainer가 호출)
- 예측 시 확률값 반환 → 앙상블에서 가중합
"""
import os
import datetime
import joblib
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from config.settings import HORIZONS, HORIZON_DIR, SCALER_DIR, GBM_MIN_SAMPLES_LEAF
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT

logger = logging.getLogger("SIGNAL")


class MultiHorizonModel:
    """6개 호라이즌 GBM 모델 묶음"""

    # GBM predict_proba 극단 확률 상한 (conf=1.000 과신 방지)
    # 학습 범위를 벗어난 피처 입력 시 GBM이 0/1 극단 확률을 반환하는 현상 완화
    CONF_CLIP = 0.92

    # 스케일러 노후화 경고 임계값 (분) — 변동성 레짐 시프트 감지
    SCALER_WARN_MINUTES = 90
    # 극단 z-score 임계값 — 스케일러 기준통계와 현재 피처가 심하게 벗어남을 감지
    EXTREME_ZSCORE_THRESHOLD = 4.0

    GBM_PARAMS = {
        "n_estimators":     100,
        "max_depth":        4,
        "learning_rate":    0.05,
        "subsample":        0.8,
        "random_state":     42,
        "min_samples_leaf": GBM_MIN_SAMPLES_LEAF,
    }

    def __init__(self):
        self.models:  Dict[str, GradientBoostingClassifier] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.feature_names: List[str] = []
        self._is_fitted: Dict[str, bool] = {h: False for h in HORIZONS}
        self._scaler_fitted_at: Dict[str, datetime.datetime] = {}

        os.makedirs(HORIZON_DIR, exist_ok=True)
        os.makedirs(SCALER_DIR, exist_ok=True)

        # 저장된 모델 로드 시도
        self._load_all()

    # ── 학습 ──────────────────────────────────────────────────
    def fit(
        self,
        X: np.ndarray,
        targets: Dict[str, np.ndarray],
        feature_names: List[str],
    ):
        """
        전체 호라이즌 일괄 학습

        Args:
            X:            피처 행렬 (n_samples × n_features)
            targets:      {"1m": labels, "3m": labels, ...}
            feature_names: 피처명 리스트
        """
        self.feature_names = feature_names

        for horizon in HORIZONS:
            y = targets.get(horizon)
            if y is None:
                continue

            # NaN 제거
            mask = ~np.isnan(y)
            Xm, ym = X[mask], y[mask].astype(int)

            if len(np.unique(ym)) < 2:
                logger.warning(f"[Model] {horizon}: 클래스 부족, 학습 건너뜀")
                continue

            # 스케일러
            scaler = StandardScaler()
            Xs = scaler.fit_transform(Xm)

            # GBM 학습
            clf = GradientBoostingClassifier(**self.GBM_PARAMS)
            clf.fit(Xs, ym)

            self.models[horizon]  = clf
            self.scalers[horizon] = scaler
            self._is_fitted[horizon] = True
            self._scaler_fitted_at[horizon] = datetime.datetime.now()

            logger.info(f"[Model] {horizon} 학습 완료 (n={len(ym)})")

        self._save_all()

    # ── 예측 ──────────────────────────────────────────────────
    def predict_proba(self, x: np.ndarray) -> Dict[str, Dict]:
        """
        단일 샘플 예측

        Args:
            x: 1D 피처 배열

        Returns:
            {"1m": {"up": 0.45, "down": 0.35, "flat": 0.20,
                    "direction": 1, "confidence": 0.45}, ...}
        """
        results = {}
        x2d = x.reshape(1, -1)

        for horizon, clf in self.models.items():
            if not self._is_fitted.get(horizon):
                results[horizon] = self._default_result()
                continue

            scaler = self.scalers.get(horizon)

            # 스케일러 노후화 경고: 마지막 fit 이후 SCALER_WARN_MINUTES 경과 시 WARN
            fitted_at = self._scaler_fitted_at.get(horizon)
            if fitted_at is not None:
                age_min = (datetime.datetime.now() - fitted_at).total_seconds() / 60.0
                if age_min > self.SCALER_WARN_MINUTES:
                    logger.warning(
                        f"[Model] {horizon} 스케일러 {age_min:.0f}분 미갱신 "
                        f"(≥{self.SCALER_WARN_MINUTES}분) — 변동성 레짐 시프트 시 z-score 왜곡 가능"
                    )

            xs = scaler.transform(x2d) if scaler else x2d

            # 극단 z-score 감지: |z| > EXTREME_ZSCORE_THRESHOLD 피처 수 로깅
            extreme_count = int(np.sum(np.abs(xs[0]) > self.EXTREME_ZSCORE_THRESHOLD))
            if extreme_count > 0:
                logger.warning(
                    f"[Model] {horizon} 극단 z-score {extreme_count}개 피처 감지 "
                    f"(|z|>{self.EXTREME_ZSCORE_THRESHOLD:.0f}) — 스케일러 노후화 또는 이상 데이터 의심"
                )

            classes = list(clf.classes_)
            proba   = clf.predict_proba(xs)[0]

            proba_map = {int(c): float(p) for c, p in zip(classes, proba)}
            up   = proba_map.get(DIRECTION_UP,   0.0)
            down = proba_map.get(DIRECTION_DOWN, 0.0)
            flat = proba_map.get(DIRECTION_FLAT, 0.0)

            direction  = max(proba_map, key=proba_map.get)
            confidence = max(up, down, flat)

            # 극단 확률 클리핑: 학습 외 입력 시 GBM이 0/1 극단값을 반환하는 현상 완화
            # 초과분을 나머지 두 클래스에 균등 분배해 합=1 유지
            if confidence > self.CONF_CLIP:
                excess = confidence - self.CONF_CLIP
                if direction == DIRECTION_UP:
                    up    = self.CONF_CLIP
                    down += excess / 2.0
                    flat += excess / 2.0
                elif direction == DIRECTION_DOWN:
                    down  = self.CONF_CLIP
                    up   += excess / 2.0
                    flat += excess / 2.0
                else:
                    flat  = self.CONF_CLIP
                    up   += excess / 2.0
                    down += excess / 2.0
                confidence = self.CONF_CLIP

            results[horizon] = {
                "up":         round(up, 4),
                "down":       round(down, 4),
                "flat":       round(flat, 4),
                "direction":  direction,
                "confidence": round(confidence, 4),
            }

        return results

    def _default_result(self) -> dict:
        return {
            "up": 1/3, "down": 1/3, "flat": 1/3,
            "direction": DIRECTION_FLAT, "confidence": 1/3,
        }

    # ── 저장 / 로드 ────────────────────────────────────────────
    def _model_path(self, horizon: str) -> str:
        return os.path.join(HORIZON_DIR, f"gbm_{horizon}.pkl")

    def _scaler_path(self, horizon: str) -> str:
        return os.path.join(SCALER_DIR, f"scaler_{horizon}.pkl")

    def _save_all(self):
        for h in self.models:
            joblib.dump(self.models[h],  self._model_path(h))
            joblib.dump(self.scalers[h], self._scaler_path(h))
        joblib.dump(self.feature_names,
                    os.path.join(HORIZON_DIR, "feature_names.pkl"))
        logger.info("[Model] 전체 모델 저장 완료")

    def _load_all(self):
        fn_path = os.path.join(HORIZON_DIR, "feature_names.pkl")
        if os.path.exists(fn_path):
            self.feature_names = joblib.load(fn_path)

        for h in HORIZONS:
            mp = self._model_path(h)
            sp = self._scaler_path(h)
            if os.path.exists(mp) and os.path.exists(sp):
                self.models[h]  = joblib.load(mp)
                self.scalers[h] = joblib.load(sp)
                self._is_fitted[h] = True
                logger.info(f"[Model] {h} 로드 성공")

    def is_ready(self) -> bool:
        """최소 1개 호라이즌 학습 완료 여부"""
        return any(self._is_fitted.values())

    def set_feature_names(self, names: List[str]) -> None:
        """GBM 미학습 상태에서 SGD 활성화를 위한 피처명 부트스트랩."""
        if not self.feature_names:
            self.feature_names = list(names)

    def get_feature_importance(self) -> Dict[str, float]:
        """GBM 전체 호라이즌 평균 피처 중요도 반환.

        Returns:
            {feature_name: 0~1 float} — 모델 미학습 시 빈 dict
        """
        if not self.feature_names:
            return {}

        acc = np.zeros(len(self.feature_names))
        n   = 0
        for h, clf in self.models.items():
            if not self._is_fitted.get(h):
                continue
            imp = getattr(clf, "feature_importances_", None)
            if imp is not None and len(imp) == len(self.feature_names):
                acc += imp
                n   += 1

        if n == 0:
            return {}

        avg = acc / n
        return {name: float(v) for name, v in zip(self.feature_names, avg)}

