# model/rf_horizon_model.py — 호라이즌별 Random Forest 보조 앙상블 (P6c)
"""
GBM+SGD 앙상블에 RF(Random Forest) 다양성을 추가한다.

특성:
  - 배깅 기반 → GBM과 근본적으로 다른 결정 경계 (앙상블 다양성 확보)
  - OFI=0 소급 데이터의 영향을 자동 희석 (개별 트리가 일부 피처 무시)
  - n_jobs=1 → Python 3.7 32-bit 안정성 보장
  - oob_score=True → 재학습 없이 Out-of-Bag 정확도 모니터링

사용법:
  # 학습 (batch_retrainer에서 호출)
  rf_model = RFHorizonModel(model_dir)
  rf_model.train(X, y_dict, feature_names)

  # 예측 (main.py STEP 5에서)
  rf_p = rf_model.predict_proba_single("1m", feat_vec)  # {"up", "down", "flat"}

  # 저장/로드
  rf_model.save_all()
  rf_model.load_all()
"""
import logging
import os
import pickle
from typing import Dict, List, Optional

import numpy as np

from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from config.settings import HORIZONS, HORIZON_DIR

logger = logging.getLogger("LEARNING")

# RF 파라미터 — 32-bit Python 안정성 우선
RF_PARAMS = {
    "n_estimators":     150,
    "max_depth":        10,
    "min_samples_leaf": 8,
    "class_weight":     "balanced",   # UP/DOWN/FLAT 자동 균형
    "n_jobs":           1,            # 32-bit Python 멀티코어 불안정
    "random_state":     42,
    "oob_score":        True,         # 재학습 없이 OOB 정확도 모니터링
}


class RFHorizonModel:
    """호라이즌별 Random Forest 모델 묶음."""

    MODEL_FILE = "rf_horizons.pkl"   # HORIZON_DIR에 저장

    def __init__(self, model_dir: Optional[str] = None):
        self._dir    = model_dir or HORIZON_DIR
        self._models: Dict[str, object] = {}
        self._ready  = False
        self._oob:   Dict[str, float]   = {}
        self.feature_names: List[str]   = []

    # ── 학습 ─────────────────────────────────────────────────────
    def train(
        self,
        X: np.ndarray,
        y_dict: Dict[str, np.ndarray],
        feature_names: List[str],
        sample_weights: Optional[np.ndarray] = None,
    ) -> None:
        """GBM batch_retrainer와 동일한 X, y_dict, feature_names로 학습."""
        try:
            from sklearn.ensemble import RandomForestClassifier
        except ImportError:
            logger.warning("[RF] scikit-learn 없음 — RF 학습 건너뜀")
            return

        self.feature_names = list(feature_names)
        trained = 0

        for hz in HORIZONS:
            y = y_dict.get(hz)
            if y is None or len(y) != len(X):
                continue

            # 클래스 다양성 확인 (최소 2클래스 필요)
            unique = set(int(c) for c in y)
            if len(unique) < 2:
                logger.warning("[RF] %s 클래스 다양성 부족 (%s) — 건너뜀", hz, unique)
                continue

            try:
                rf = RandomForestClassifier(**RF_PARAMS)
                rf.fit(X, y, sample_weight=sample_weights)
                self._models[hz] = rf
                self._oob[hz] = round(float(rf.oob_score_), 4) if rf.oob_score_ else 0.0
                trained += 1
                logger.info(
                    "[RF] %s 학습 완료 (n=%d OOB=%.1f%%)",
                    hz, len(X), self._oob[hz] * 100,
                )
            except Exception as exc:
                logger.warning("[RF] %s 학습 실패: %s", hz, exc)

        self._ready = trained == len(HORIZONS)
        logger.info(
            "[RF] 전체 학습 완료: %d/%d 호라이즌 ready=%s",
            trained, len(HORIZONS), self._ready,
        )

    # ── 예측 ─────────────────────────────────────────────────────
    def predict_proba_single(
        self,
        horizon: str,
        x: np.ndarray,
    ) -> Optional[Dict[str, float]]:
        """단일 봉 예측 → {"up", "down", "flat"} 또는 None (미학습 시).

        학습과 동일한 apply_robust_preprocess(log1p/clip)를 적용한 뒤 예측.
        이 변환 없이 raw feat_vec를 넣으면 atr·avg_volume 스케일이 훈련과 다르다.
        """
        rf = self._models.get(horizon)
        if rf is None:
            return None

        try:
            from model.multi_horizon_model import apply_robust_preprocess
            x2d = x.reshape(1, -1)
            if self.feature_names:
                x2d = apply_robust_preprocess(x2d, self.feature_names)
            classes = list(rf.classes_)
            proba  = rf.predict_proba(x2d)[0]
            pm     = {int(c): float(p) for c, p in zip(classes, proba)}
            return {
                "up":   pm.get(DIRECTION_UP,   0.0),
                "down": pm.get(DIRECTION_DOWN, 0.0),
                "flat": pm.get(DIRECTION_FLAT, 0.0),
            }
        except Exception as exc:
            logger.debug("[RF] %s 예측 오류: %s", horizon, exc)
            return None

    # ── 저장 / 로드 ──────────────────────────────────────────────
    def save_all(self) -> None:
        path = os.path.join(self._dir, self.MODEL_FILE)
        os.makedirs(self._dir, exist_ok=True)
        payload = {
            "models":        self._models,
            "oob":           self._oob,
            "feature_names": self.feature_names,
        }
        # [S2-D] 원자 쓰기: .tmp 먼저 쓴 뒤 os.replace()
        _tmp = path + ".tmp"
        with open(_tmp, "wb") as f:
            pickle.dump(payload, f, protocol=2)   # protocol=2: Python 3.7 호환
        os.replace(_tmp, path)
        logger.info("[RF] 저장 완료: %s (%d호라이즌)", path, len(self._models))

    def load_all(self) -> bool:
        path = os.path.join(self._dir, self.MODEL_FILE)
        if not os.path.exists(path):
            return False
        try:
            with open(path, "rb") as f:
                payload = pickle.load(f)
            self._models       = payload.get("models", {})
            self._oob          = payload.get("oob", {})
            self.feature_names = payload.get("feature_names", [])
            self._ready = len(self._models) == len(HORIZONS)
            logger.info(
                "[RF] 로드 완료: %d호라이즌 ready=%s",
                len(self._models), self._ready,
            )
            return True
        except Exception as exc:
            logger.warning("[RF] 로드 실패: %s", exc)
            return False

    def is_ready(self) -> bool:
        return self._ready and len(self._models) > 0

    def get_oob_scores(self) -> Dict[str, float]:
        return dict(self._oob)

    def get_model(self, horizon: str):
        """[346차] EOD 모델가드 비교용 — 특정 호라이즌의 학습된 모델 객체 반환."""
        return self._models.get(horizon)

    def override_horizon(self, horizon: str, model, oob: float) -> None:
        """[346차] EOD 모델가드 — 신규 학습 결과가 허용 하락폭을 초과할 때 그
        호라이즌만 구모델(model)/구 OOB(oob)로 되돌린다. 나머지 호라이즌은
        새로 학습된 모델을 그대로 유지 — rf_horizons.pkl이 6개 호라이즌을 한
        파일에 묶어 저장하는 구조라(GBM처럼 호라이즌별 개별 파일이 아님) 저장
        직전에 슬롯 단위로 교체해야 한다."""
        self._models[horizon] = model
        self._oob[horizon] = oob
