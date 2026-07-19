# learning/quantile_regressor.py — [260704 감사 P2] 분위 회귀 보조 채널
"""
"확률 60%"보다 "기대 +0.08pt, 하방 -0.21pt"가 트레이더의 언어다 (감사 §1-3 ④).

기존 분류(UP/DOWN/FLAT) 대신 N분 후 가격 변동(포인트)의 q10/q50/q90을 직접
추정하는 호라이즌별 분위 회귀 채널. q50의 부호가 방향, (q90-q10)이 불확실성 폭이며
사이징·TP 거리 산정에 직결될 수 있다.

LightGBM/XGBoost native quantile 지원이 더 우수하지만 32-bit 런타임 wheel이 없어
채택 불가(감사 §1-3 ③) — sklearn 1.0.2에서 안정적으로 지원되는
`GradientBoostingRegressor(loss="quantile", alpha=q)`를 분위별로 3개 학습한다
(HistGradientBoostingRegressor의 quantile loss는 sklearn 1.1+ 필요 — 1.0.2 미지원).

주의 — 실거래 미연결: 현재는 ensemble_decisions에 섀도우 신호로 로깅만 한다.
사이징/TP 거리에 실제로 반영하려면 충분한 검증 기간을 거친 뒤 별도로 결정할 것
(triple-barrier·meta-labeling과 동일한 원칙 — ROADMAP.md 참조).
"""
import json
import logging
import os
import pickle
import sqlite3
from typing import Dict, Optional

import numpy as np

try:
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.preprocessing import StandardScaler
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False

from config.settings import RAW_DATA_DB, HORIZONS, MODEL_DIR

logger = logging.getLogger("LEARNING")

# model/horizons/ 는 .gitignore 처리되어 있음 — PC별 학습 산출물로 취급
_MODEL_SUBDIR = os.path.join(MODEL_DIR, "horizons", "quantile")
QUANTILES = (0.1, 0.5, 0.9)
MIN_ROWS_PER_HORIZON = 2000
GBR_PARAMS = dict(
    n_estimators=150, max_depth=3, learning_rate=0.05,
    subsample=0.8, min_samples_leaf=30, random_state=42,
)


def _load_records(hz: str, h_min: int, weeks_back: int):
    """(records=[(ts, feat_dict)], close_map) — raw_features_horizon 우선, 1m은 raw_features 폴백.
    batch_retrainer.retrain_shadow_triple_barrier()와 동일한 폴백 전략(2026-07-05 확립).
    """
    import datetime
    cutoff = (datetime.datetime.now() - datetime.timedelta(weeks=weeks_back)).strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(RAW_DATA_DB, timeout=10) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT ts, features FROM raw_features_horizon WHERE horizon=? AND ts>=? ORDER BY ts",
            (hz, cutoff),
        ).fetchall()
        if len(rows) < MIN_ROWS_PER_HORIZON:
            rows = conn.execute(
                "SELECT ts, features FROM raw_features WHERE ts>=? ORDER BY ts",
                (cutoff,),
            ).fetchall()
        candle_rows = conn.execute(
            "SELECT ts, close FROM raw_candles WHERE ts>=? ORDER BY ts",
            (cutoff,),
        ).fetchall()

    close_map = {r["ts"]: float(r["close"]) for r in candle_rows}

    records = []
    feat_names = None
    feat_count = 0
    for r in rows:
        try:
            fd = json.loads(r["features"]) if r["features"] else {}
        except (ValueError, TypeError):
            continue
        if not isinstance(fd, dict) or not fd:
            continue
        keys = list(fd.keys())
        if feat_names is None or len(keys) >= feat_count:
            feat_count = len(keys)
            feat_names = keys
        records.append((r["ts"], fd))

    return records, feat_names, close_map


def _future_return_pts(ts: str, h_min: int, close_map: Dict[str, float]) -> Optional[float]:
    import datetime
    c0 = close_map.get(ts)
    if not c0:
        return None
    future_ts = (
        datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=h_min)
    ).strftime("%Y-%m-%d %H:%M:%S")
    cf = close_map.get(future_ts)
    if cf is None:
        return None
    return cf - c0


def _strip_random_state(model):
    """[357차] py37_32 크로스 로드 호환 — 피클 전 RandomState 객체 참조 제거.

    sklearn 1.0.2 GBR은 fit 시 `_rng`(numpy RandomState)를 인스턴스에 저장하고,
    각 트리(`estimators_`의 DecisionTreeRegressor)의 `random_state`에도 동일
    RandomState 객체를 전달한다. numpy 1.26(py310_64 학습환경)에서 피클된
    RandomState는 numpy 1.21(py37_32 런타임)에서 `__randomstate_ctor` 시그니처
    불일치로 언피클 불가 → 스코어러 로드가 전 호라이즌 실패했다(357차 실측).
    predict 경로는 이 RNG들을 전혀 사용하지 않으므로 int/None으로 치환해도 안전.
    """
    if isinstance(getattr(model, "random_state", None), np.random.RandomState):
        model.random_state = 0
    if getattr(model, "_rng", None) is not None:
        model._rng = None
    ests = getattr(model, "estimators_", None)
    if ests is not None:
        for est in np.asarray(ests).ravel():
            if isinstance(getattr(est, "random_state", None), np.random.RandomState):
                est.random_state = 0
    return model


def train_quantile_models(weeks_back: int = 26, min_rows: int = MIN_ROWS_PER_HORIZON) -> Dict:
    """호라이즌별 q10/q50/q90 분위 회귀 학습 + 저장.

    Returns: {"ok": bool, "horizons": {hz: {"ok", "n_samples", "coverage_check", "pinball"}}}
    """
    if not _SKLEARN_OK:
        return {"ok": False, "error": "scikit-learn 미설치"}

    os.makedirs(_MODEL_SUBDIR, exist_ok=True)
    results = {}

    for hz, h_min in HORIZONS.items():
        records, feat_names, close_map = _load_records(hz, h_min, weeks_back)
        if len(records) < min_rows or feat_names is None:
            results[hz] = {"ok": False, "error": "데이터 부족 (%d < %d)" % (len(records), min_rows)}
            continue

        y = []
        keep_idx = []
        for i, (ts, _) in enumerate(records):
            ret = _future_return_pts(ts, h_min, close_map)
            if ret is not None:
                y.append(ret)
                keep_idx.append(i)
        if len(y) < min_rows:
            results[hz] = {"ok": False, "error": "미래가격 결측 후 데이터 부족 (%d < %d)" % (len(y), min_rows)}
            continue

        records = [records[i] for i in keep_idx]
        y = np.array(y, dtype=np.float64)
        X = np.array([[rec[1].get(f, 0.0) for f in feat_names] for rec in records], dtype=np.float32)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 시계열 3폴드로 커버리지(실측 q10 이하 비율 ≈ 10%인지) + pinball loss 점검
        tscv = TimeSeriesSplit(n_splits=3)
        below_q10_flags, above_q90_flags, pinballs = [], [], []
        for train_idx, val_idx in tscv.split(X_scaled):
            X_tr, X_val = X_scaled[train_idx], X_scaled[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]
            preds = {}
            for q in QUANTILES:
                m = GradientBoostingRegressor(loss="quantile", alpha=q, **GBR_PARAMS)
                m.fit(X_tr, y_tr)
                preds[q] = m.predict(X_val)
            below_q10_flags.extend((y_val < preds[0.1]).tolist())
            above_q90_flags.extend((y_val > preds[0.9]).tolist())
            for q in QUANTILES:
                diff = y_val - preds[q]
                pinballs.append(np.mean(np.maximum(q * diff, (q - 1) * diff)))

        coverage_below_q10 = float(np.mean(below_q10_flags)) if below_q10_flags else float("nan")
        coverage_above_q90 = float(np.mean(above_q90_flags)) if above_q90_flags else float("nan")
        pinball = float(np.mean(pinballs)) if pinballs else float("nan")

        # 전체 데이터로 최종 모델 학습 + 저장
        for q in QUANTILES:
            model = GradientBoostingRegressor(loss="quantile", alpha=q, **GBR_PARAMS)
            model.fit(X_scaled, y)
            _strip_random_state(model)
            _tag = int(round(q * 100))
            _path = os.path.join(_MODEL_SUBDIR, f"{hz}_q{_tag}.pkl")
            _tmp = _path + ".tmp"
            with open(_tmp, "wb") as f:
                pickle.dump(model, f, protocol=4)
            os.replace(_tmp, _path)

        _scaler_path = os.path.join(_MODEL_SUBDIR, f"{hz}_scaler.pkl")
        _tmp_s = _scaler_path + ".tmp"
        with open(_tmp_s, "wb") as f:
            pickle.dump(scaler, f, protocol=4)
        os.replace(_tmp_s, _scaler_path)

        _fn_path = os.path.join(_MODEL_SUBDIR, f"{hz}_features.pkl")
        with open(_fn_path, "wb") as f:
            pickle.dump(list(feat_names), f, protocol=4)

        logger.info(
            "[QuantileReg] %s n=%d pinball=%.4f coverage(<q10)=%.3f coverage(>q90)=%.3f",
            hz, len(y), pinball, coverage_below_q10, coverage_above_q90,
        )
        results[hz] = {
            "ok": True,
            "n_samples": len(y),
            "pinball": round(pinball, 4),
            "coverage_below_q10": round(coverage_below_q10, 4),
            "coverage_above_q90": round(coverage_above_q90, 4),
        }

    return {"ok": True, "horizons": results, "model_dir": _MODEL_SUBDIR}


class QuantileScorer:
    """저장된 호라이즌별 분위 회귀 모델을 로드해 실시간 q10/q50/q90 스코어링.

    실거래 게이트/사이징에는 아직 연결되지 않음 — 섀도우 신호로만 로깅한다.
    """

    def __init__(self, model_dir: str = _MODEL_SUBDIR):
        self._model_dir = model_dir
        self._cache: Dict[str, Optional[tuple]] = {}
        # [357차] 스코어링 실패 무음 방지 — 호라이즌당 최초 1회만 WARNING, 이후 debug.
        # ([3] 분위회귀 채널이 로드 실패 무음으로 캠페인 전 기간 표본 0이었던 재발 방지)
        self._score_warned: set = set()

    def _load(self, horizon: str):
        if horizon in self._cache:
            return self._cache[horizon]
        scaler_path = os.path.join(self._model_dir, f"{horizon}_scaler.pkl")
        fn_path = os.path.join(self._model_dir, f"{horizon}_features.pkl")
        model_paths = {q: os.path.join(self._model_dir, f"{horizon}_q{int(round(q*100))}.pkl") for q in QUANTILES}
        if not (os.path.exists(scaler_path) and os.path.exists(fn_path)
                and all(os.path.exists(p) for p in model_paths.values())):
            self._cache[horizon] = None
            return None
        try:
            with open(scaler_path, "rb") as f:
                scaler = pickle.load(f)
            with open(fn_path, "rb") as f:
                feat_names = pickle.load(f)
            models = {}
            for q, p in model_paths.items():
                with open(p, "rb") as f:
                    models[q] = pickle.load(f)
            bundle = (models, scaler, feat_names)
            self._cache[horizon] = bundle
            return bundle
        except Exception as e:
            logger.warning("[QuantileReg] %s 모델 로드 실패: %s", horizon, e)
            self._cache[horizon] = None
            return None

    def score(self, horizon: str, features: Dict) -> Optional[Dict[str, float]]:
        """{"q10","q50","q90","expected_pt","uncertainty_pt"} 반환. 모델 미존재/오류 시 None."""
        bundle = self._load(horizon)
        if bundle is None:
            return None
        models, scaler, feat_names = bundle
        try:
            x = np.array([[float(features.get(f, 0.0) or 0.0) for f in feat_names]], dtype=np.float32)
            x_s = scaler.transform(x)
            q10 = float(models[0.1].predict(x_s)[0])
            q50 = float(models[0.5].predict(x_s)[0])
            q90 = float(models[0.9].predict(x_s)[0])
            return {
                "q10": q10, "q50": q50, "q90": q90,
                "expected_pt": q50,
                "uncertainty_pt": q90 - q10,
            }
        except Exception as e:
            if horizon not in self._score_warned:
                self._score_warned.add(horizon)
                logger.warning("[QuantileReg] %s 스코어링 실패(세션 최초 1회 경고): %s", horizon, e)
            else:
                logger.debug("[QuantileReg] %s 스코어링 실패: %s", horizon, e)
            return None

    def reload(self, horizon: Optional[str] = None) -> None:
        if horizon:
            self._cache.pop(horizon, None)
        else:
            self._cache.clear()


_scorer: Optional[QuantileScorer] = None


def get_quantile_scorer() -> QuantileScorer:
    global _scorer
    if _scorer is None:
        _scorer = QuantileScorer()
    return _scorer
