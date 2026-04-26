# learning/batch_retrainer.py — GBM 배치 재학습기
"""
주간/월간 전체 모델 재학습

온라인 학습(SGD)은 매 분봉 실시간 — 이 모듈은 배치 GBM 담당

재학습 트리거:
  주간: Walk-Forward 검증 갱신 (매주 월요일 장 전)
  월간: 전체 GBM 모델 재학습 (매월 1일)
  수동: batch_retrainer.retrain_now() 호출

재학습 절차:
  1. DB에서 최근 N주 데이터 로드
  2. target_builder 로 라벨 생성
  3. feature_builder 로 피처 계산
  4. 각 호라이즌 GBM 학습 + 교차검증
  5. 성능 향상 시에만 모델 교체 (안전 교체)
  6. HTML 리포트 생성

Python 3.7 32-bit 호환 (scikit-learn GradientBoostingClassifier)
"""
import os
import logging
import datetime
import pickle
from typing import Optional, Dict, List

import numpy as np

try:
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import accuracy_score, roc_auc_score
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False

from config.settings import (
    MODEL_DIR, HORIZON_DIR, HORIZONS, DB_DIR,
    GBM_WEIGHT_DEFAULT,
)

logger = logging.getLogger("LEARNING")

# GBM 하이퍼파라미터
GBM_PARAMS = {
    "n_estimators":     200,
    "max_depth":        4,
    "learning_rate":    0.05,
    "subsample":        0.8,
    "min_samples_leaf": 20,
    "random_state":     42,
}

# 최소 학습 데이터 (분봉 수)
MIN_TRAIN_BARS = 5000   # 약 13거래일


class BatchRetrainer:
    """
    GBM 모델 배치 재학습기

    사용:
        retrainer = BatchRetrainer()
        result    = retrainer.retrain_now(weeks_back=8)
    """

    def __init__(self, model_dir: str = HORIZON_DIR):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)

        self._last_retrain:  Optional[datetime.datetime] = None
        self._retrain_count: int = 0

    # ── 재학습 스케줄 판단 ────────────────────────────────────────
    def should_retrain_weekly(self, now: Optional[datetime.datetime] = None) -> bool:
        """월요일 08:50~09:00 사이 주간 재학습 여부"""
        if now is None:
            now = datetime.datetime.now()
        return (
            now.weekday() == 0           # 월요일
            and now.hour == 8
            and 50 <= now.minute < 60
        )

    def should_retrain_monthly(self, now: Optional[datetime.datetime] = None) -> bool:
        """매월 1일 07:00 월간 재학습 여부"""
        if now is None:
            now = datetime.datetime.now()
        return now.day == 1 and now.hour == 7

    # ── 재학습 메인 ───────────────────────────────────────────────
    def retrain_now(
        self,
        X:          Optional[np.ndarray] = None,
        y_dict:     Optional[Dict[str, np.ndarray]] = None,
        weeks_back: int = 8,
        force:      bool = False,
    ) -> Dict:
        """
        GBM 모델 전체 재학습

        Args:
            X:          피처 행렬 (None이면 DB에서 로드)
            y_dict:     {horizon: label_array} (None이면 DB에서 로드)
            weeks_back: 학습 기간 (주)
            force:      성능 저하여도 강제 교체

        Returns:
            재학습 결과 딕셔너리
        """
        if not _SKLEARN_OK:
            return {"ok": False, "error": "scikit-learn 미설치"}

        logger.info(f"[Retrain] 배치 재학습 시작 (weeks_back={weeks_back})")
        start_time = datetime.datetime.now()

        # 데이터 로드
        if X is None or y_dict is None:
            X, y_dict = self._load_from_db(weeks_back)

        if X is None or len(X) < MIN_TRAIN_BARS:
            msg = f"학습 데이터 부족 ({len(X) if X is not None else 0} < {MIN_TRAIN_BARS})"
            logger.warning(f"[Retrain] {msg}")
            return {"ok": False, "error": msg}

        results = {}
        for horizon_key in HORIZONS:
            if horizon_key not in y_dict:
                continue
            y = y_dict[horizon_key]
            if len(y) != len(X):
                continue

            result = self._train_horizon(horizon_key, X, y, force=force)
            results[horizon_key] = result

        elapsed = (datetime.datetime.now() - start_time).total_seconds()
        self._last_retrain  = datetime.datetime.now()
        self._retrain_count += 1

        summary = {
            "ok":           True,
            "retrain_count": self._retrain_count,
            "elapsed_sec":  round(elapsed, 1),
            "data_size":    len(X),
            "horizons":     results,
            "timestamp":    self._last_retrain.strftime("%Y-%m-%d %H:%M"),
        }

        logger.info(
            f"[Retrain] 완료 | {elapsed:.1f}초 | "
            f"성공={sum(1 for r in results.values() if r.get('replaced'))}/"
            f"{len(results)} 호라이즌"
        )
        return summary

    # ── 개별 호라이즌 학습 ────────────────────────────────────────
    def _train_horizon(
        self,
        horizon_key: str,
        X:           np.ndarray,
        y:           np.ndarray,
        force:       bool = False,
    ) -> Dict:
        """
        단일 호라이즌 GBM 학습 + 교차검증

        성능 향상 시에만 저장 (안전 교체)
        """
        # 시계열 교차검증 (3폴드)
        tscv    = TimeSeriesSplit(n_splits=3)
        cv_accs = []

        for train_idx, val_idx in tscv.split(X):
            X_tr, X_val = X[train_idx], X[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]

            if len(np.unique(y_tr)) < 2:
                continue

            model = GradientBoostingClassifier(**GBM_PARAMS)
            model.fit(X_tr, y_tr)
            acc = accuracy_score(y_val, model.predict(X_val))
            cv_accs.append(acc)

        if not cv_accs:
            return {"ok": False, "error": "교차검증 실패"}

        cv_acc = float(np.mean(cv_accs))

        # 전체 데이터로 최종 학습
        final_model = GradientBoostingClassifier(**GBM_PARAMS)
        final_model.fit(X, y)

        # 기존 모델과 성능 비교
        old_acc   = self._load_model_acc(horizon_key)
        replaced  = False

        if force or cv_acc > old_acc - 0.01:   # 기존 대비 1% 이내 하락은 허용
            self._save_model(horizon_key, final_model, cv_acc)
            replaced = True
            logger.info(f"[Retrain] {horizon_key} 교체 (acc {old_acc:.4f}→{cv_acc:.4f})")
        else:
            logger.info(f"[Retrain] {horizon_key} 유지 (acc {cv_acc:.4f} < {old_acc:.4f})")

        return {
            "ok":       True,
            "cv_acc":   round(cv_acc, 4),
            "old_acc":  round(old_acc, 4),
            "replaced": replaced,
            "n_samples":len(X),
        }

    # ── 모델 저장/로드 ────────────────────────────────────────────
    def _save_model(self, horizon_key: str, model, acc: float):
        path     = os.path.join(self.model_dir, f"gbm_{horizon_key}.pkl")
        acc_path = os.path.join(self.model_dir, f"gbm_{horizon_key}_acc.txt")
        with open(path, "wb") as f:
            pickle.dump(model, f)
        with open(acc_path, "w") as f:
            f.write(str(acc))

    def _load_model_acc(self, horizon_key: str) -> float:
        acc_path = os.path.join(self.model_dir, f"gbm_{horizon_key}_acc.txt")
        try:
            with open(acc_path, "r") as f:
                return float(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0.0

    def load_model(self, horizon_key: str):
        """저장된 GBM 모델 로드"""
        path = os.path.join(self.model_dir, f"gbm_{horizon_key}.pkl")
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return pickle.load(f)

    # ── DB 로드 (더미 구현 — 실거래 데이터 확보 후 완성) ─────────
    def _load_from_db(self, weeks_back: int):
        """
        SQLite DB에서 과거 분봉 피처/라벨 로드

        TODO: utils/db_utils.py 와 연동하여 실제 데이터 로드
        현재는 데이터 없으면 None 반환
        """
        db_path = os.path.join(DB_DIR, "predictions.db")
        if not os.path.exists(db_path):
            logger.warning("[Retrain] DB 없음 — 학습 데이터 확보 필요")
            return None, None

        try:
            import sqlite3
            conn  = sqlite3.connect(db_path)
            cutoff = (datetime.datetime.now() - datetime.timedelta(weeks=weeks_back)).strftime("%Y-%m-%d")
            df = None
            try:
                import importlib
                if importlib.util.find_spec("pandas"):
                    import pandas as pd
                    df = pd.read_sql(
                        f"SELECT * FROM features WHERE datetime >= '{cutoff}' ORDER BY datetime",
                        conn
                    )
            finally:
                conn.close()

            if df is None or len(df) < MIN_TRAIN_BARS:
                return None, None

            # 피처/라벨 분리 (columns 구조는 feature_builder 출력에 맞게)
            feature_cols = [c for c in df.columns if c not in ("datetime", "label_1m", "label_3m",
                                                                  "label_5m", "label_10m", "label_15m", "label_30m")]
            X = df[feature_cols].values.astype(np.float32)
            y_dict = {}
            for hz in HORIZONS:
                col = f"label_{hz}"
                if col in df.columns:
                    y_dict[hz] = df[col].values.astype(int)

            return X, y_dict

        except Exception as e:
            logger.warning(f"[Retrain] DB 로드 오류: {e}")
            return None, None

    def get_stats(self) -> dict:
        return {
            "retrain_count": self._retrain_count,
            "last_retrain":  self._last_retrain.strftime("%Y-%m-%d %H:%M") if self._last_retrain else "없음",
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if _SKLEARN_OK:
        retrainer = BatchRetrainer()
        # 더미 데이터로 테스트
        np.random.seed(42)
        X_dummy = np.random.randn(6000, 20).astype(np.float32)
        y_dummy = {hz: np.random.randint(0, 2, 6000) for hz in ["1m", "5m", "15m"]}
        result  = retrainer.retrain_now(X=X_dummy, y_dict=y_dummy, force=True)
        print(f"재학습 결과: {result}")
    else:
        print("scikit-learn 미설치")
