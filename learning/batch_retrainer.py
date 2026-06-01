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
    from sklearn.preprocessing import StandardScaler
    from sklearn.utils.class_weight import compute_sample_weight
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False

from config.settings import (
    MODEL_DIR, HORIZON_DIR, HORIZONS, DB_DIR,
    GBM_WEIGHT_DEFAULT, GBM_MIN_SAMPLES_LEAF,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT

logger = logging.getLogger("LEARNING")


# P6b: 경로 조건부 레이블 파라미터
# UP/DOWN 후보이더라도 중간 경로에서 이 비율 이상 역행하면 FLAT 처리
PATH_LABEL_RATIO: float = 0.45   # threshold × 0.45 이상 역행 시 FLAT


def _path_conditioned_label(
    close_map: dict,
    ts: str,
    h_min: int,
    threshold: float,
    path_ratio: float = PATH_LABEL_RATIO,
) -> int:
    """
    경로 조건부 레이블: T분 후 방향 + 중간 경로 최대 역행폭 조건.

    UP 후보라도 중간에 threshold × path_ratio 이상 하락하면 FLAT.
    DOWN 후보라도 중간에 threshold × path_ratio 이상 상승하면 FLAT.

    경로 데이터 불완전(경계 구간) → build_single_target 방식 fallback.
    """
    c0 = close_map.get(ts)
    if not c0:
        return DIRECTION_FLAT

    future_ts = (
        datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        + datetime.timedelta(minutes=h_min)
    ).strftime("%Y-%m-%d %H:%M:%S")
    cf = close_map.get(future_ts)
    if not cf or threshold <= 0:
        return DIRECTION_FLAT

    end_ret = (cf - c0) / c0

    if end_ret > threshold:  # UP 후보
        # 중간 경로의 최대 하락폭 계산
        path_closes = []
        for m in range(1, h_min):
            mid_ts = (
                datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                + datetime.timedelta(minutes=m)
            ).strftime("%Y-%m-%d %H:%M:%S")
            mc = close_map.get(mid_ts)
            if mc:
                path_closes.append(mc)
        if path_closes:
            max_dd = (min(path_closes) - c0) / c0   # 음수
            if abs(max_dd) > path_ratio * threshold:
                return DIRECTION_FLAT   # 중간 역행 → 노이즈
        return DIRECTION_UP

    elif end_ret < -threshold:  # DOWN 후보
        path_closes = []
        for m in range(1, h_min):
            mid_ts = (
                datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                + datetime.timedelta(minutes=m)
            ).strftime("%Y-%m-%d %H:%M:%S")
            mc = close_map.get(mid_ts)
            if mc:
                path_closes.append(mc)
        if path_closes:
            max_ru = (max(path_closes) - c0) / c0   # 양수
            if max_ru > path_ratio * threshold:
                return DIRECTION_FLAT
        return DIRECTION_DOWN

    return DIRECTION_FLAT

# GBM 하이퍼파라미터 — n_estimators는 배치 재학습 시 200으로 더 정밀하게 사용
# min_samples_leaf는 MultiHorizonModel과 동일한 상수를 공유 (비결정성 방지)
GBM_PARAMS = {
    "n_estimators":     300,   # 200→300: 190일(71,144봉) 데이터 기반 강화 (개선 6)
    "max_depth":        5,
    "learning_rate":    0.04,  # 0.05→0.04: estimators 증가 보상 (과적합 방지)
    "subsample":        0.8,
    "min_samples_leaf": GBM_MIN_SAMPLES_LEAF,
    "random_state":     42,
}

# 최소 학습 데이터 (분봉 수)
# 소급 190일(71,144봉) 확보 완료(2026-06-01) → 기준 상향
# 5000(13거래일)은 과적합 위험 — 15000(약 40거래일=2개월)으로 상향
MIN_TRAIN_BARS = 15000

# 호라이즌별 class weight — multi_horizon_model._make_sample_weight 와 반드시 동기화
# 2026-05-30 threshold 재보정 후: FLAT 비율 ~33% 균형 → 강한 FL 억압 불필요
# 1m/5m: FL 0.60/0.58 → 0.85 (FLAT~34/33%, 강압 해소)
# 30m:   FL 0.65 → 1.00 (balanced, FLAT~30%)
# 3m:    FL 0.75 유지 (threshold 현행 유지, 분포 미변경)
_CW_1M  = {DIRECTION_FLAT: 0.85, DIRECTION_UP: 1.08, DIRECTION_DOWN: 1.08}
_CW_3M  = {DIRECTION_FLAT: 0.75, DIRECTION_UP: 1.12, DIRECTION_DOWN: 1.12}
_CW_5M  = {DIRECTION_FLAT: 0.85, DIRECTION_UP: 1.08, DIRECTION_DOWN: 1.08}
_CW_30M = {DIRECTION_FLAT: 1.00, DIRECTION_UP: 1.00, DIRECTION_DOWN: 1.00}


def _make_sample_weight(y: np.ndarray, horizon_key: str) -> np.ndarray:
    """호라이즌별 sample_weight 계산.
    1m/3m/5m/30m: 명시적 가중치 적용.
    10m/15m: sklearn balanced (FLAT~34~35%, 자동 균형).
    """
    if horizon_key == "1m":
        return np.array([_CW_1M.get(int(lbl), 1.0) for lbl in y])
    if horizon_key == "3m":
        return np.array([_CW_3M.get(int(lbl), 1.0) for lbl in y])
    if horizon_key == "5m":
        return np.array([_CW_5M.get(int(lbl), 1.0) for lbl in y])
    if horizon_key == "30m":
        return np.array([_CW_30M.get(int(lbl), 1.0) for lbl in y])
    return compute_sample_weight("balanced", y)


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
        X:             Optional[np.ndarray] = None,
        y_dict:        Optional[Dict[str, np.ndarray]] = None,
        feature_names: Optional[List[str]] = None,
        weeks_back:    int = 8,
        force:         bool = False,
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
            X, y_dict, feature_names = self._load_from_db(weeks_back)

        if X is None or len(X) < MIN_TRAIN_BARS:
            msg = f"학습 데이터 부족 ({len(X) if X is not None else 0} < {MIN_TRAIN_BARS})"
            logger.warning(f"[Retrain] {msg}")
            return {"ok": False, "error": msg}

        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(X.shape[1])]

        # Robust 전처리 — 예측 경로(predict_proba)와 동일 변환 적용 (일관성 보장)
        from model.multi_horizon_model import apply_robust_preprocess
        X = apply_robust_preprocess(X, feature_names)

        results = {}
        for horizon_key in HORIZONS:
            if horizon_key not in y_dict:
                continue
            y = y_dict[horizon_key]
            if len(y) != len(X):
                continue

            result = self._train_horizon(
                horizon_key,
                X,
                y,
                feature_names=feature_names,
                force=force,
            )
            results[horizon_key] = result

        self._save_feature_names(feature_names)

        # P6c: RF 이종 앙상블 학습 (GBM과 동일 데이터 사용)
        try:
            from model.rf_horizon_model import RFHorizonModel
            rf_model = RFHorizonModel(self.model_dir)
            rf_model.train(X, y_dict, feature_names)
            if rf_model.is_ready():
                rf_model.save_all()
                logger.info("[Retrain] RF 학습 완료 OOB=%s", rf_model.get_oob_scores())
        except Exception as _rf_exc:
            logger.warning("[Retrain] RF 학습 실패 (GBM 계속 사용): %s", _rf_exc)

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
        feature_names: List[str],
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

            scaler = StandardScaler()
            X_tr_s = scaler.fit_transform(X_tr)
            X_val_s = scaler.transform(X_val)

            model = GradientBoostingClassifier(**GBM_PARAMS)
            model.fit(X_tr_s, y_tr, sample_weight=_make_sample_weight(y_tr, horizon_key))
            acc = accuracy_score(y_val, model.predict(X_val_s))
            cv_accs.append(acc)

        if not cv_accs:
            return {"ok": False, "error": "교차검증 실패"}

        cv_acc = float(np.mean(cv_accs))

        # 전체 데이터로 최종 학습
        final_scaler = StandardScaler()
        X_scaled = final_scaler.fit_transform(X)
        final_model = GradientBoostingClassifier(**GBM_PARAMS)
        final_model.fit(X_scaled, y, sample_weight=_make_sample_weight(y, horizon_key))

        # 기존 모델과 성능 비교
        old_acc   = self._load_model_acc(horizon_key)
        replaced  = False

        if force or cv_acc > old_acc - 0.01:   # 기존 대비 1% 이내 하락은 허용
            self._save_model(horizon_key, final_model, final_scaler, cv_acc, feature_names)
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
    def _save_model(self, horizon_key: str, model, scaler, acc: float, feature_names: List[str]):
        path     = os.path.join(self.model_dir, f"gbm_{horizon_key}.pkl")
        acc_path = os.path.join(self.model_dir, f"gbm_{horizon_key}_acc.txt")
        scaler_dir = os.path.join(MODEL_DIR, "scaler")
        scaler_path = os.path.join(scaler_dir, f"scaler_{horizon_key}.pkl")
        os.makedirs(scaler_dir, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(model, f)
        with open(scaler_path, "wb") as f:
            pickle.dump(scaler, f)
        with open(acc_path, "w") as f:
            f.write(str(acc))
        self._save_feature_names(feature_names)

    def _save_feature_names(self, feature_names: List[str]) -> None:
        feature_path = os.path.join(self.model_dir, "feature_names.pkl")
        with open(feature_path, "wb") as f:
            pickle.dump(list(feature_names), f)

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

    # ── 스케일러 워밍업용 피처 로드 ──────────────────────────────────

    def load_features_for_warmup(
        self, lookback_bars: int = 500
    ):
        """raw_data.db 에서 최근 N봉 피처만 로드 (라벨 계산 없음).

        refit_scalers_only() 에 전달할 X 행렬과 feature_names 반환.
        데이터 부족 또는 오류 시 (None, None) 반환.
        """
        import json as _json
        import sqlite3

        from config.settings import RAW_DATA_DB

        raw_db = RAW_DATA_DB
        if not os.path.exists(raw_db):
            logger.warning("[ScalerWarmup] raw_data.db 없음 — 워밍업 건너뜀")
            return None, None

        try:
            with sqlite3.connect(raw_db, timeout=10) as conn:
                conn.row_factory = sqlite3.Row
                feat_rows = conn.execute(
                    "SELECT features FROM raw_features ORDER BY ts DESC LIMIT ?",
                    (lookback_bars,),
                ).fetchall()
        except Exception as _e:
            logger.warning("[ScalerWarmup] DB 읽기 실패: %s", _e)
            return None, None

        if not feat_rows:
            logger.warning("[ScalerWarmup] raw_features 비어있음 — 워밍업 건너뜀")
            return None, None

        # managed feature set 적용 (batch_retrainer._load_from_db와 동일)
        registry_path = os.path.join(DB_DIR, "shap_feature_registry.json")
        managed_feats = None
        try:
            import json as _json2
            if os.path.exists(registry_path):
                with open(registry_path, "r", encoding="utf-8") as fh:
                    registry = _json2.load(fh)
                active = list(registry.get("active_features") or [])
                if active:
                    managed_feats = active
        except Exception:
            pass

        records = []
        feat_names = None
        feat_name_count = 0
        for r in feat_rows:
            try:
                fd = _json.loads(r["features"])
            except (ValueError, TypeError):
                continue
            if not isinstance(fd, dict):
                continue
            curr_keys = list(fd.keys())
            if feat_names is None or len(curr_keys) >= feat_name_count:
                feat_name_count = len(curr_keys)
                feat_names = curr_keys
            records.append(fd)

        if not records or feat_names is None:
            return None, None

        if managed_feats:
            available = set(feat_names)
            filtered = [n for n in managed_feats if n in available]
            if filtered:
                feat_names = filtered

        X = np.array(
            [[rec.get(f, 0.0) for f in feat_names] for rec in records],
            dtype=np.float32,
        )
        logger.info("[ScalerWarmup] 피처 로드 완료 n=%d feat=%d", len(X), len(feat_names))
        return X, feat_names

    # ── DB 로드 (raw_features + raw_candles 기반) ────────────────
    def _load_from_db(self, weeks_back: int):
        """
        raw_data.db 의 raw_features / raw_candles 테이블에서 학습 데이터 로드.

        raw_features: ts, features(JSON)
        raw_candles:  ts, close
        라벨: 각 호라이즌 N분 후 수익률 방향 (+1/0/-1)
        """
        import json as _json
        import sqlite3

        from config.settings import RAW_DATA_DB, HORIZON_THRESHOLDS
        from model.target_builder import build_single_target

        raw_db = RAW_DATA_DB
        if not os.path.exists(raw_db):
            logger.warning("[Retrain] raw_data.db 없음 — 학습 데이터 축적 대기")
            return None, None, None

        try:
            cutoff = (
                datetime.datetime.now() - datetime.timedelta(weeks=weeks_back)
            ).strftime("%Y-%m-%d %H:%M:%S")

            with sqlite3.connect(raw_db, timeout=10) as conn:
                conn.row_factory = sqlite3.Row

                feat_rows = conn.execute(
                    "SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts",
                    (cutoff,),
                ).fetchall()

                candle_rows = conn.execute(
                    "SELECT ts, close FROM raw_candles WHERE ts >= ? ORDER BY ts",
                    (cutoff,),
                ).fetchall()

            if len(feat_rows) < MIN_TRAIN_BARS:
                logger.warning(
                    f"[Retrain] 피처 데이터 부족 ({len(feat_rows)} < {MIN_TRAIN_BARS})"
                )
                return None, None, None

            # close 맵 (ts → close)
            close_map = {r["ts"]: float(r["close"]) for r in candle_rows}

            # X 행렬 구성
            records = []
            feat_names = None
            feat_name_count = 0
            for r in feat_rows:
                try:
                    fd = _json.loads(r["features"])
                except (ValueError, TypeError):
                    continue
                if not isinstance(fd, dict):
                    continue
                curr_keys = list(fd.keys())
                if feat_names is None or len(curr_keys) >= feat_name_count:
                    feat_name_count = len(curr_keys)
                    feat_names = curr_keys
                records.append((r["ts"], fd))

            if not records or feat_names is None:
                return None, None, None

            registry_path = os.path.join(DB_DIR, "shap_feature_registry.json")
            try:
                import json as _json2
                if os.path.exists(registry_path):
                    with open(registry_path, "r", encoding="utf-8") as fh:
                        registry = _json2.load(fh)
                    active_features = list(registry.get("active_features") or [])
                    if active_features:
                        available = set(feat_names)
                        managed = [name for name in active_features if name in available]
                        if managed:
                            feat_names = managed
                            logger.info(
                                "[Retrain] managed feature set 적용: %d개",
                                len(feat_names),
                            )
            except Exception as exc:
                logger.warning("[Retrain] managed feature set load 실패: %s", exc)

            X = np.array(
                [[rec[1].get(f, 0.0) for f in feat_names] for rec in records],
                dtype=np.float32,
            )

            # y 라벨 (호라이즌별 미래 수익률 방향)
            # 방법B: 각 봉의 시점별 rolling sigma × k 로 threshold 계산
            # → 날별 변동성 차이를 레이블에 반영 (FLAT std 14%p → 3%p)
            from collections import deque as _deque
            import math as _math
            from config.settings import (
                SIGMA_K as _SK, SIGMA_W as _SW, SIGMA_W_MIN as _SW_MIN,
                USE_ROLLING_SIGMA_THRESHOLD as _USE_ROLLING,
                SIGMA_K_PER_HORIZON as _SK_PER_H,
                USE_FIXED_LABEL_THRESHOLD as _USE_FIXED_LABEL,
            )

            # 개선 4: 학습 레이블 고정화
            # USE_FIXED_LABEL_THRESHOLD=True → HORIZON_THRESHOLDS 고정값으로 레이블 생성
            # 실전 rolling sigma와 학습 임계값을 분리 → 레이블 드리프트 제거
            _use_fixed = _USE_FIXED_LABEL
            if _use_fixed:
                logger.info("[Retrain] 레이블 고정 임계값 사용 (USE_FIXED_LABEL_THRESHOLD=True)")

            y_dict = {}
            for hz, h_min in HORIZONS.items():
                y = []
                _sigma_buf_rt = _deque(maxlen=_SW)
                # P5: 호라이즌별 최적 k (없으면 공통 k fallback)
                _hz_k = _SK_PER_H.get(hz, _SK)
                # 고정 임계값 (개선 4)
                _fixed_thresh = HORIZON_THRESHOLDS.get(hz, 0.0003)

                for ts, _ in records:
                    if _use_fixed:
                        # 개선 4: 고정 임계값 — rolling sigma 계산 생략
                        threshold = _fixed_thresh
                    elif _USE_ROLLING:
                        # 기존 rolling sigma 방식
                        _c0 = close_map.get(ts)
                        _t_prev = (
                            datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                            - datetime.timedelta(minutes=1)
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        _c_prev = close_map.get(_t_prev)
                        if _c0 and _c_prev and _c_prev > 0:
                            _sigma_buf_rt.append((_c0 - _c_prev) / _c_prev * 100)

                        _n = len(_sigma_buf_rt)
                        if _n >= _SW_MIN and _n > 1:
                            _v = list(_sigma_buf_rt)
                            _m = sum(_v) / _n
                            _sig = _math.sqrt(sum((x - _m) ** 2 for x in _v) / (_n - 1))
                            threshold = _sig / 100.0 * _hz_k * _math.sqrt(h_min)
                        else:
                            threshold = _fixed_thresh
                    else:
                        threshold = _fixed_thresh

                    # P6b: 경로 조건부 레이블
                    # 중간 역행 과다 케이스를 FLAT으로 처리 → 레이블 순도 향상
                    label = _path_conditioned_label(
                        close_map, ts, h_min, threshold,
                    )
                    y.append(label)
                y_dict[hz] = np.array(y, dtype=int)

            logger.info(
                f"[Retrain] DB 로드 완료: {len(X)}행 × {len(feat_names)}피처 "
                f"(cutoff={cutoff[:10]})"
            )
            return X, y_dict, feat_names

        except Exception as e:
            logger.warning(f"[Retrain] DB 로드 오류: {e}")
            return None, None, None

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
        result  = retrainer.retrain_now(
            X=X_dummy,
            y_dict=y_dummy,
            feature_names=[f"feature_{i}" for i in range(X_dummy.shape[1])],
            force=True,
        )
        print(f"재학습 결과: {result}")
    else:
        print("scikit-learn 미설치")
