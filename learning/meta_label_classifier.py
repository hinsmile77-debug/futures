# learning/meta_label_classifier.py — [260704 감사 P1] Meta-labeling 진입품질 분류기
"""
`meta_labels` 테이블(learning/meta_labeling.py가 STEP 1 예측검증마다 축적, 6개 호라이즌
합산 65,000+건 — 260704 감사가 "이미 존재하고 rollout 리포트가 '메타 라벨 준비 완료'라고
말하는데 자산이 놀고 있다"고 지적한 데이터)을 학습 데이터로 써서 "이 신호로 진입하면
방향이 맞고 실이익이 나는가"를 직접 학습하는 호라이즌별 이진 분류기.

레이블: meta_action != "skip" (take/reduce — derive_meta_label()에서 이미
        realized_move > 0 조건을 통과한 케이스) → 1
        meta_action == "skip" (오답 또는 무이익) → 0

주의 — 실거래 게이트 미연결: strategy/entry/meta_gate.py에서 섀도우 신호
(entry_quality_prob)로만 로깅되며 action/size_multiplier에는 아직 영향을 주지 않는다.
9항목 체크리스트(strategy/entry/checklist.py)를 실제로 대체하려면 이 확률과 실현
손익의 상관을 충분 기간 검증한 뒤 결정할 것 (ROADMAP.md 참조).
"""
import json
import logging
import os
import pickle
import sqlite3
from typing import Dict, Optional

import numpy as np

try:
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import roc_auc_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.utils.class_weight import compute_sample_weight
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False

from config.settings import PREDICTIONS_DB, HORIZONS, MODEL_DIR

logger = logging.getLogger("LEARNING")

# model/horizons/ 는 .gitignore 처리되어 있음 — 그 아래에 두어 PC별 학습 산출물로 취급
_MODEL_SUBDIR = os.path.join(MODEL_DIR, "horizons", "meta_gate")
MIN_ROWS_PER_HORIZON = 2000
HGB_PARAMS = dict(max_iter=200, max_depth=4, learning_rate=0.05, min_samples_leaf=30, random_state=42)


def _load_meta_label_rows(horizon: str):
    if not os.path.exists(PREDICTIONS_DB):
        return []
    with sqlite3.connect(PREDICTIONS_DB, timeout=10) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT features, meta_action FROM meta_labels WHERE horizon=? ORDER BY ts",
            (horizon,),
        ).fetchall()
    return rows


def train_entry_quality_models(min_rows: int = MIN_ROWS_PER_HORIZON) -> Dict:
    """호라이즌별 진입품질(수익여부) 이진 분류기 학습 + 저장.

    Returns: {"ok": bool, "horizons": {hz: {"ok", "auc", "n_samples", "pos_rate"}}, "model_dir": str}
    """
    if not _SKLEARN_OK:
        return {"ok": False, "error": "scikit-learn 미설치"}

    os.makedirs(_MODEL_SUBDIR, exist_ok=True)
    results = {}
    for hz in HORIZONS:
        rows = _load_meta_label_rows(hz)
        if len(rows) < min_rows:
            results[hz] = {"ok": False, "error": "데이터 부족 (%d < %d)" % (len(rows), min_rows)}
            continue

        feat_names = None
        feat_count = 0
        records = []
        for r in rows:
            try:
                fd = json.loads(r["features"]) if r["features"] else {}
            except (ValueError, TypeError):
                fd = {}
            if not isinstance(fd, dict) or not fd:
                continue
            keys = list(fd.keys())
            if feat_names is None or len(keys) >= feat_count:
                feat_count = len(keys)
                feat_names = keys
            records.append((fd, r["meta_action"]))

        if not records or feat_names is None:
            results[hz] = {"ok": False, "error": "피처 파싱 실패"}
            continue

        X = np.array(
            [[rec[0].get(f, 0.0) for f in feat_names] for rec in records], dtype=np.float32
        )
        y = np.array([0 if rec[1] == "skip" else 1 for rec in records], dtype=int)

        if len(np.unique(y)) < 2:
            results[hz] = {"ok": False, "error": "레이블 단일 클래스 — 학습 불가"}
            continue

        # 시계열 3폴드 CV로 AUC 추정 (batch_retrainer와 동일 검증 철학)
        tscv = TimeSeriesSplit(n_splits=3)
        aucs = []
        for train_idx, val_idx in tscv.split(X):
            X_tr, X_val = X[train_idx], X[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]
            if len(np.unique(y_tr)) < 2 or len(np.unique(y_val)) < 2:
                continue
            scaler = StandardScaler()
            X_tr_s = scaler.fit_transform(X_tr)
            X_val_s = scaler.transform(X_val)
            model = HistGradientBoostingClassifier(**HGB_PARAMS)
            sw = compute_sample_weight("balanced", y_tr)
            model.fit(X_tr_s, y_tr, sample_weight=sw)
            proba = model.predict_proba(X_val_s)[:, 1]
            aucs.append(roc_auc_score(y_val, proba))

        auc = float(np.mean(aucs)) if aucs else None

        # 전체 데이터로 최종 모델 학습 + 저장
        final_scaler = StandardScaler()
        X_scaled = final_scaler.fit_transform(X)
        final_model = HistGradientBoostingClassifier(**HGB_PARAMS)
        final_model.fit(X_scaled, y, sample_weight=compute_sample_weight("balanced", y))

        _model_path = os.path.join(_MODEL_SUBDIR, "%s_entry_quality.pkl" % hz)
        _tmp = _model_path + ".tmp"
        with open(_tmp, "wb") as f:
            pickle.dump(final_model, f, protocol=4)
        os.replace(_tmp, _model_path)

        _scaler_path = os.path.join(_MODEL_SUBDIR, "%s_entry_quality_scaler.pkl" % hz)
        _tmp_s = _scaler_path + ".tmp"
        with open(_tmp_s, "wb") as f:
            pickle.dump(final_scaler, f, protocol=4)
        os.replace(_tmp_s, _scaler_path)

        _fn_path = os.path.join(_MODEL_SUBDIR, "%s_entry_quality_features.pkl" % hz)
        with open(_fn_path, "wb") as f:
            pickle.dump(list(feat_names), f, protocol=4)

        pos_rate = float(y.mean())
        logger.info(
            "[MetaLabelClf] %s AUC=%s n=%d pos_rate=%.3f",
            hz, ("%.4f" % auc) if auc is not None else "N/A", len(X), pos_rate,
        )
        results[hz] = {
            "ok": True,
            "auc": round(auc, 4) if auc is not None else None,
            "n_samples": len(X),
            "pos_rate": round(pos_rate, 4),
        }

    return {"ok": True, "horizons": results, "model_dir": _MODEL_SUBDIR}


class EntryQualityScorer:
    """저장된 호라이즌별 진입품질 분류기를 로드해 실시간 확률 스코어링.

    실거래 게이트에는 아직 연결되지 않음 — MetaGate가 섀도우 신호로만 사용한다.
    """

    def __init__(self, model_dir: str = _MODEL_SUBDIR):
        self._model_dir = model_dir
        self._cache: Dict[str, Optional[tuple]] = {}  # hz -> (model, scaler, feat_names) 또는 None(미존재 캐시)

    def _load(self, horizon: str):
        if horizon in self._cache:
            return self._cache[horizon]
        model_path = os.path.join(self._model_dir, "%s_entry_quality.pkl" % horizon)
        scaler_path = os.path.join(self._model_dir, "%s_entry_quality_scaler.pkl" % horizon)
        fn_path = os.path.join(self._model_dir, "%s_entry_quality_features.pkl" % horizon)
        if not (os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(fn_path)):
            self._cache[horizon] = None
            return None
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            with open(scaler_path, "rb") as f:
                scaler = pickle.load(f)
            with open(fn_path, "rb") as f:
                feat_names = pickle.load(f)
            bundle = (model, scaler, feat_names)
            self._cache[horizon] = bundle
            return bundle
        except Exception as e:
            logger.warning("[MetaLabelClf] %s 모델 로드 실패: %s", horizon, e)
            self._cache[horizon] = None
            return None

    def score(self, horizon: str, features: Dict) -> Optional[float]:
        """진입품질(수익 확률) 스코어. 모델 미존재/오류 시 None."""
        bundle = self._load(horizon)
        if bundle is None:
            return None
        model, scaler, feat_names = bundle
        try:
            x = np.array(
                [[float(features.get(f, 0.0) or 0.0) for f in feat_names]], dtype=np.float32
            )
            x_s = scaler.transform(x)
            return float(model.predict_proba(x_s)[0, 1])
        except Exception as e:
            logger.debug("[MetaLabelClf] %s 스코어링 실패: %s", horizon, e)
            return None

    def reload(self, horizon: Optional[str] = None) -> None:
        """캐시 무효화 — 재학습 후 최신 모델 반영."""
        if horizon:
            self._cache.pop(horizon, None)
        else:
            self._cache.clear()


_scorer: Optional[EntryQualityScorer] = None


def get_entry_quality_scorer() -> EntryQualityScorer:
    global _scorer
    if _scorer is None:
        _scorer = EntryQualityScorer()
    return _scorer
