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
    RETRAIN_WEEKS_BACK,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT

logger = logging.getLogger("LEARNING")


# P6b: 경로 조건부 레이블 파라미터
# UP/DOWN 후보이더라도 중간 경로에서 이 비율 이상 역행하면 FLAT 처리
# 0.45 → 0.55: FLAT 과다 레이블 방지 (11시 반전 시 FLAT 고착 CB③ 발동 원인)
# 임계값의 55% 이상 역행 시만 FLAT → FLAT 비율 줄고 UP/DOWN 예측 증가
PATH_LABEL_RATIO: float = 0.55


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
# RETRAIN_WEEKS_BACK=26 기준 실측 ~44,000봉 → 충분히 초과
# (구 weeks_back=10 기준 ~15,750봉으로 간신히 달성 → 26주로 확장)
MIN_TRAIN_BARS = 15000

# Phase 2: 호라이즌별 학습 최소 데이터 — 시간 등가 기준 (72k 봉 기준 전 호라이즌 충족)
MIN_TRAIN_BARS_PER_HORIZON = {
    "1m": 15000, "3m": 5000, "5m": 3000,
    "10m": 1500, "15m": 1000, "30m": 500,
}

# 호라이즌별 class weight — multi_horizon_model._make_sample_weight 와 반드시 동기화
# 2026-05-30 threshold 재보정 후: FLAT 비율 ~33% 균형 → 강한 FL 억압 불필요
# 1m/5m: FL 0.60/0.58 → 0.85 (FLAT~34/33%, 강압 해소)
# 3m:    FL 0.75 유지 (threshold 현행 유지, 분포 미변경)
# 30m:   FL 0.65 → 0.70 (FLAT 편향 억제, 반전 시 UP/DN 강화)
# 10m/15m: 2026-06-05 balanced → 명시적 설정 변경
#   근거: 2026-06-05 세션에서 10m FL 100%, 15m FL 100% 고착 재발.
#   balanced는 훈련 데이터 분포에 종속 → 강한 하락장(FL 과다 학습 기간)에서
#   FL 억압 불가. 85차에서 1m/5m와 동일 문제 → 명시적 가중치로 전환.
_CW_1M  = {DIRECTION_FLAT: 0.85, DIRECTION_UP: 1.08, DIRECTION_DOWN: 1.08}
_CW_3M  = {DIRECTION_FLAT: 0.75, DIRECTION_UP: 1.12, DIRECTION_DOWN: 1.12}
_CW_5M  = {DIRECTION_FLAT: 0.85, DIRECTION_UP: 1.08, DIRECTION_DOWN: 1.08}
_CW_10M = {DIRECTION_FLAT: 0.80, DIRECTION_UP: 1.10, DIRECTION_DOWN: 1.10}
_CW_15M = {DIRECTION_FLAT: 0.75, DIRECTION_UP: 1.15, DIRECTION_DOWN: 1.15}
# 30m: FL 억제 유지 + UP 강화로 DN 100% 편향 상쇄 (127차, 2026-06-08 DN 100% 고착 사례)
# DN=1.15→0.90 (과잉 가중치 제거), UP=1.15→1.40 (DN 편향 상쇄), FL=0.70 유지
_CW_30M = {DIRECTION_FLAT: 0.70, DIRECTION_UP: 1.40, DIRECTION_DOWN: 0.90}


def _make_sample_weight(y: np.ndarray, horizon_key: str) -> np.ndarray:
    """호라이즌별 sample_weight 계산. 전 호라이즌 명시적 가중치 적용.

    10m/15m은 2026-06-05까지 balanced(sklearn 자동 균형)를 사용했으나,
    강한 하락장에서 FL 100% 고착 재발 → 명시적 설정으로 전환.
    """
    if horizon_key == "1m":
        return np.array([_CW_1M.get(int(lbl), 1.0) for lbl in y])
    if horizon_key == "3m":
        return np.array([_CW_3M.get(int(lbl), 1.0) for lbl in y])
    if horizon_key == "5m":
        return np.array([_CW_5M.get(int(lbl), 1.0) for lbl in y])
    if horizon_key == "10m":
        return np.array([_CW_10M.get(int(lbl), 1.0) for lbl in y])
    if horizon_key == "15m":
        return np.array([_CW_15M.get(int(lbl), 1.0) for lbl in y])
    if horizon_key == "30m":
        return np.array([_CW_30M.get(int(lbl), 1.0) for lbl in y])
    return compute_sample_weight("balanced", y)


class BatchRetrainer:
    """
    GBM 모델 배치 재학습기

    사용:
        retrainer = BatchRetrainer()
        result    = retrainer.retrain_now(weeks_back=RETRAIN_WEEKS_BACK)
    """

    def __init__(self, model_dir: str = HORIZON_DIR):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)

        self._last_retrain:  Optional[datetime.datetime] = None
        self._retrain_count: int = 0

    def restore_stats(self, last_retrain_str: str, total_count: int) -> None:
        """재시동 후 이전 세션 이력 복원."""
        if last_retrain_str:
            try:
                self._last_retrain = datetime.datetime.strptime(last_retrain_str, "%Y-%m-%d %H:%M")
            except Exception:
                pass
        if total_count > 0:
            self._retrain_count = total_count

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
        X:                    Optional[np.ndarray] = None,
        y_dict:               Optional[Dict[str, np.ndarray]] = None,
        feature_names:        Optional[List[str]] = None,
        weeks_back:           int = RETRAIN_WEEKS_BACK,
        force:                bool = False,
        use_horizon_features: bool = False,
    ) -> Dict:
        """
        GBM 모델 전체 재학습

        Args:
            X:                    피처 행렬 (None이면 DB에서 로드)
            y_dict:               {horizon: label_array} (None이면 DB에서 로드)
            weeks_back:           학습 기간 (주)
            force:                성능 저하여도 강제 교체
            use_horizon_features: Phase 2 경로 활성화 — raw_features_horizon 테이블 사용

        Returns:
            재학습 결과 딕셔너리
        """
        if not _SKLEARN_OK:
            return {"ok": False, "error": "scikit-learn 미설치"}

        logger.info(
            "[Retrain] 배치 재학습 시작 (weeks_back=%d, phase2=%s)",
            weeks_back, use_horizon_features,
        )
        start_time = datetime.datetime.now()

        # Phase 2: 호라이즌별 독립 X로 재학습
        if use_horizon_features and (X is None or y_dict is None):
            if self._has_horizon_features_table():
                return self._retrain_phase2(weeks_back, force, start_time)
            else:
                logger.warning("[Retrain] raw_features_horizon 테이블 없음 — Phase 1 경로로 fallback")

        # 데이터 로드 (Phase 0/1 경로)
        if X is None or y_dict is None:
            X, y_dict, feature_names = self._load_from_db(weeks_back)

        if X is None or len(X) < MIN_TRAIN_BARS:
            msg = "학습 데이터 부족 ({} < {})".format(
                len(X) if X is not None else 0, MIN_TRAIN_BARS
            )
            logger.warning("[Retrain] %s", msg)
            return {"ok": False, "error": msg}

        if feature_names is None:
            feature_names = ["feature_{}".format(i) for i in range(X.shape[1])]

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
        path       = os.path.join(self.model_dir, f"gbm_{horizon_key}.pkl")
        acc_path   = os.path.join(self.model_dir, f"gbm_{horizon_key}_acc.txt")
        scaler_dir = os.path.join(MODEL_DIR, "scaler")
        scaler_path = os.path.join(scaler_dir, f"scaler_{horizon_key}.pkl")
        os.makedirs(scaler_dir, exist_ok=True)
        # [S2-D] 원자 쓰기: .tmp 에 먼저 쓴 뒤 os.replace() 로 교체
        # — 직접 open(path,"wb") 은 쓰는 중 main 스레드가 joblib.load() 하면 불완전 파일 읽기 발생
        _tmp_model  = path       + ".tmp"
        _tmp_scaler = scaler_path + ".tmp"
        with open(_tmp_model, "wb") as f:
            pickle.dump(model, f)
        os.replace(_tmp_model, path)
        with open(_tmp_scaler, "wb") as f:
            pickle.dump(scaler, f)
        os.replace(_tmp_scaler, scaler_path)
        with open(acc_path, "w") as f:
            f.write(str(acc))

    def _save_feature_names(self, feature_names: List[str]) -> None:
        feature_path = os.path.join(self.model_dir, "feature_names.pkl")
        with open(feature_path, "wb") as f:
            pickle.dump(list(feature_names), f)

    def _load_feature_names(self):
        # type: () -> list
        """저장된 feature_names.pkl 로드. 없으면 빈 리스트."""
        feature_path = os.path.join(self.model_dir, "feature_names.pkl")
        try:
            with open(feature_path, "rb") as f:
                return pickle.load(f)
        except (IOError, OSError, pickle.UnpicklingError):
            return []

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

        X = np.array(
            [[rec.get(f, 0.0) for f in feat_names] for rec in records],
            dtype=np.float32,
        )
        logger.info("[ScalerWarmup] 피처 로드 완료 n=%d feat=%d", len(X), len(feat_names))
        return X, feat_names

    # ── Phase 2: 호라이즌별 독립 재학습 ─────────────────────────
    def _has_horizon_features_table(self):
        # type: () -> bool
        """raw_features_horizon 테이블 존재 여부 확인."""
        import sqlite3
        from config.settings import RAW_DATA_DB
        if not os.path.exists(RAW_DATA_DB):
            return False
        try:
            with sqlite3.connect(RAW_DATA_DB, timeout=5) as conn:
                row = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='raw_features_horizon'"
                ).fetchone()
                if row is None:
                    return False
                cnt = conn.execute(
                    "SELECT COUNT(*) FROM raw_features_horizon"
                ).fetchone()
                return (cnt[0] if cnt else 0) > 0
        except Exception:
            return False

    def _retrain_phase2(self, weeks_back, force, start_time):
        # type: (int, bool, object) -> dict
        """Phase 2 경로: raw_features_horizon 테이블에서 호라이즌별 독립 X 로드 후 재학습."""
        import json as _json2
        import sqlite3

        from config.settings import RAW_DATA_DB, HORIZON_THRESHOLDS
        from model.multi_horizon_model import apply_robust_preprocess

        raw_db = RAW_DATA_DB
        cutoff = (
            datetime.datetime.now() - datetime.timedelta(weeks=weeks_back)
        ).strftime("%Y-%m-%d %H:%M:%S")

        results = {}
        # Phase 2에서는 feature_names.pkl을 덮어쓰지 않음.
        # 1m 모델(Phase 1 경로)은 기존 105+ 피처 기반이므로 전역 feature_names 보존.
        # 각 호라이즌 모델의 피처명은 _train_horizon 내부에서 해당 pkl에 저장됨.
        _existing_feat_names = self._load_feature_names()  # 기존 전역 피처명 백업

        for hz, h_min in HORIZONS.items():
            min_bars = MIN_TRAIN_BARS_PER_HORIZON.get(hz, MIN_TRAIN_BARS)
            try:
                with sqlite3.connect(raw_db, timeout=10) as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute(
                        "SELECT ts, features FROM raw_features_horizon "
                        "WHERE horizon=? AND ts>=? ORDER BY ts",
                        (hz, cutoff),
                    ).fetchall()
                    candle_rows = conn.execute(
                        "SELECT ts, close FROM raw_candles WHERE ts>=? ORDER BY ts",
                        (cutoff,),
                    ).fetchall()
            except Exception as _e:
                logger.warning("[Retrain-P2] %s DB 조회 실패: %s", hz, _e)
                results[hz] = {"replaced": False, "error": str(_e)}
                continue

            if len(rows) < min_bars:
                logger.warning(
                    "[Retrain-P2] %s 데이터 부족 %d < %d -- 건너뜀",
                    hz, len(rows), min_bars,
                )
                results[hz] = {"replaced": False, "error": "데이터 부족"}
                continue

            close_map = {r["ts"]: float(r["close"]) for r in candle_rows}

            # X 행렬 구성
            feat_names = None
            feat_name_count = 0
            records = []
            for r in rows:
                try:
                    fd = _json2.loads(r["features"])
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
                results[hz] = {"replaced": False, "error": "피처 파싱 실패"}
                continue

            # global feature_names(1m 기준)로 X 구성 → 추론 공간과 일치.
            # raw_features_horizon의 cvd_direction/atr 등은 build_for_horizon에서
            # N분봉 완성봉 기반으로 재계산되어 저장되므로 (127차~) 자동 반영됨.
            use_feat_names = _existing_feat_names if _existing_feat_names else feat_names
            X_hz = np.array(
                [[rec[1].get(f, 0.0) for f in use_feat_names] for rec in records],
                dtype=np.float32,
            )
            # N분봉 재계산 피처 채움 검증: cvd_direction 비제로 비율 로깅
            _cvd_idx = (use_feat_names.index("cvd_direction")
                        if "cvd_direction" in use_feat_names else None)
            if _cvd_idx is not None:
                _nonzero = int(np.count_nonzero(X_hz[:, _cvd_idx]))
                logger.info(
                    "[Retrain-P2] %s cvd_direction 비제로 %d/%d (%.1f%%)",
                    hz, _nonzero, len(records),
                    100.0 * _nonzero / max(len(records), 1),
                )
            X_hz = apply_robust_preprocess(X_hz, use_feat_names)

            # y 레이블 (Phase 2는 고정 임계값 사용)
            _fixed_thresh = HORIZON_THRESHOLDS.get(hz, 0.0003)
            y_hz = []
            for ts, _ in records:
                label = _path_conditioned_label(close_map, ts, h_min, _fixed_thresh)
                y_hz.append(label)
            y_hz = np.array(y_hz, dtype=int)

            result = self._train_horizon(hz, X_hz, y_hz, feature_names=use_feat_names, force=force)
            results[hz] = result

        # 전역 feature_names.pkl 복원 (Phase 2는 1m 기존 피처명 보존)
        if _existing_feat_names:
            self._save_feature_names(_existing_feat_names)
            logger.info("[Retrain-P2] feature_names.pkl 보존 (n=%d, 1m 기준)", len(_existing_feat_names))

        # RF 재학습 (Phase 2에서는 생략 — 1m X 없음)

        elapsed = (datetime.datetime.now() - start_time).total_seconds()
        self._last_retrain  = datetime.datetime.now()
        self._retrain_count += 1
        return {
            "ok":           True,
            "phase2":       True,
            "retrain_count": self._retrain_count,
            "elapsed_sec":  round(elapsed, 1),
            "horizons":     results,
            "timestamp":    self._last_retrain.strftime("%Y-%m-%d %H:%M"),
        }

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

            # ── 미래 가격 없는 행 제거 (BUG-B 수정) ──────────────────────────
            # 오늘 세션 끝 근처 행은 max_horizon(30m) 후 가격이 close_map에 없음
            # → _path_conditioned_label이 FLAT 반환 → validation fold acc 하락
            # → EOD Retrain에서 acc가 89%로 폭등하는 역현상 방지
            # 해결: 30m 미래 가격이 close_map에 없는 행을 학습 전 제거
            _max_h_min = max(HORIZONS.values())  # 30
            _n_before = len(records)
            records = [
                (ts, feat) for ts, feat in records
                if (
                    datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    + datetime.timedelta(minutes=_max_h_min)
                ).strftime("%Y-%m-%d %H:%M:%S") in close_map
            ]
            _n_dropped = _n_before - len(records)
            if _n_dropped > 0:
                logger.info(
                    "[Retrain] 미래 가격 불완전 행 %d개 제거 (max_horizon=%dm 후 종가 없음)",
                    _n_dropped, _max_h_min,
                )

            # P2: MIN_TRAIN_BARS 체크를 미래가격 제거 후 실제 행 수 기준으로 수행
            if len(records) < MIN_TRAIN_BARS:
                logger.warning(
                    "[Retrain] 학습 데이터 부족 (미래가격 제거 후 %d < %d)",
                    len(records), MIN_TRAIN_BARS,
                )
                return None, None, None

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
