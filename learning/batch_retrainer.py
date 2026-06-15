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
    from sklearn.ensemble import (
        GradientBoostingClassifier, RandomForestClassifier,
        HistGradientBoostingClassifier,
    )
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import accuracy_score, roc_auc_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.utils.class_weight import compute_sample_weight
    _SKLEARN_OK = True
    # HistGBM 가용 여부 별도 확인 (sklearn 0.21+ 필요, 1.0.2에서 확인됨)
    try:
        _test = HistGradientBoostingClassifier(max_iter=1)
        _HIST_GBM_OK = True
    except Exception:
        _HIST_GBM_OK = False
except ImportError:
    _SKLEARN_OK = False
    _HIST_GBM_OK = False

from config.settings import (
    MODEL_DIR, HORIZON_DIR, HORIZONS, DB_DIR,
    GBM_WEIGHT_DEFAULT, GBM_MIN_SAMPLES_LEAF,
    RETRAIN_WEEKS_BACK, MAX_TRAIN_BARS, RAW_DATA_PRUNE_WEEKS,
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

# ── sklearn GBM (HistGBM 불가 시 fallback) ───────────────────────
# 정상 환경(_HIST_GBM_OK=True)에서는 사용 안 됨.
GBM_PARAMS = {
    "n_estimators":     300,
    "max_depth":        5,
    "learning_rate":    0.04,
    "subsample":        0.8,
    "min_samples_leaf": GBM_MIN_SAMPLES_LEAF,
    "random_state":     42,
}
GBM_PARAMS_INTRADAY = {
    "n_estimators":     100,
    "max_depth":        4,
    "learning_rate":    0.08,
    "subsample":        0.8,
    "min_samples_leaf": GBM_MIN_SAMPLES_LEAF,
    "random_state":     42,
}

# ── HistGradientBoostingClassifier (주 경로) ─────────────────────
# 벤치마크 실측 (20k봉×97피처, daemon thread, 20260611):
#   GBM(n=100):     total=272s  main_blocked=253,706ms (93%)
#   HistGBM(n=100): total=  0.6s  main_blocked=559ms   (0.2%)
# C++ OpenMP 백엔드가 fit() 중 GIL을 해제 → S2 5s 차단 근본 제거
HIST_GBM_PARAMS = {
    "max_iter":         300,   # GBM n_estimators=300 동등
    "max_depth":        5,
    "learning_rate":    0.04,
    "min_samples_leaf": GBM_MIN_SAMPLES_LEAF,
    "random_state":     42,
}
HIST_GBM_PARAMS_INTRADAY = {
    "max_iter":         100,
    "max_depth":        4,
    "learning_rate":    0.08,
    "min_samples_leaf": GBM_MIN_SAMPLES_LEAF,
    "random_state":     42,
}

# 최소 학습 데이터 (분봉 수)
# RETRAIN_WEEKS_BACK=26 기준 실측 ~44,000봉 → 충분히 초과
# (구 weeks_back=10 기준 ~15,750봉으로 간신히 달성 → 26주로 확장)
MIN_TRAIN_BARS = 15000

# 장중 재학습 최대 봉 수: 최근 ~2.5주 (최신 데이터 우선 + 속도 우선)
MAX_TRAIN_BARS_INTRADAY = 20_000

# Phase 2: 호라이즌별 학습 최소 데이터 — 시간 등가 기준 (72k 봉 기준 전 호라이즌 충족)
MIN_TRAIN_BARS_PER_HORIZON = {
    "1m": 15000, "3m": 5000, "5m": 3000,
    "10m": 1500, "15m": 1000, "30m": 500,
}

# P0: 호라이즌별 FLAT 상한 — 동적 가중치에서도 FLAT 과잉 억제 유지
_FLAT_CAP = {
    "1m": 0.85, "3m": 0.75, "5m": 0.85,
    "10m": 0.80, "15m": 0.75, "30m": 0.70,
}
_DYN_HALFLIFE   = 100   # 시간감쇠 반감기 (봉 수, ≈100분)
_DYN_CLIP_RATIO = 3.0   # 최대 가중치 = 중간값 × 배율 (역보정 폭발 방지)


def _make_sample_weight(y: np.ndarray, horizon_key: str) -> np.ndarray:
    """
    P0: 동적 역빈도 + 시간감쇠 sample_weight.

    y는 시간순 정렬 레이블 (DB ORDER BY ts 보장).
    최근 데이터 우선(halflife=100봉), DOWN 과다 시 DN 가중치 자동 감소.
    클리핑 = 중간값×3으로 역보정 폭발 방지.
    multi_horizon_model._make_sample_weight 와 동일 로직 유지 필수.
    """
    n = len(y)
    if n == 0:
        return np.ones(0, dtype=np.float64)

    decay = np.exp(-np.arange(n)[::-1] * (np.log(2) / max(_DYN_HALFLIFE, 1)))

    weighted_counts = {}
    for cls in [DIRECTION_FLAT, DIRECTION_UP, DIRECTION_DOWN]:
        mask = (y == cls)
        weighted_counts[cls] = float(decay[mask].sum()) if mask.any() else 1e-6

    total = sum(weighted_counts.values())
    inv_freq = {cls: total / (3.0 * cnt) for cls, cnt in weighted_counts.items()}

    median_w = sorted(inv_freq.values())[1]
    max_w = median_w * _DYN_CLIP_RATIO
    weights = {cls: min(v, max_w) for cls, v in inv_freq.items()}

    flat_cap = _FLAT_CAP.get(horizon_key)
    if flat_cap is not None:
        weights[DIRECTION_FLAT] = min(weights[DIRECTION_FLAT], flat_cap)

    logger.debug(
        "[Retrain] %s 동적가중치 FL=%.2f UP=%.2f DN=%.2f",
        horizon_key,
        weights.get(DIRECTION_FLAT, 1.0),
        weights.get(DIRECTION_UP, 1.0),
        weights.get(DIRECTION_DOWN, 1.0),
    )
    return np.array([weights.get(int(lbl), 1.0) for lbl in y], dtype=np.float64)


def _cusum_filter(records, close_map, h_mult=0.7):
    """
    P1: CUSUM 이벤트 필터.

    연속 하락/상승 구간에서 동일 방향 신호가 반복 학습되는 것을 방지.
    CUSUM 누적통계가 동적 임계값 h를 초과하는 시점만 선택.
    선택 결과가 원본의 30% 미만이면 전체 반환 (데이터 부족 안전망).

    records: [(ts, feat_dict), ...]  — 시간순 정렬
    close_map: {ts: float}
    h_mult: 임계값 배율 (평균 표준편차 × h_mult)
      0.5 → 0.7 변경 근거: 6/12 장전 재학습에서 40211→12067봉(70% 제거)으로
      안전망 30% 경계선에서 학습 데이터 부족 경고 상시 발생. h_mult 상향으로
      이벤트 선택 기준 완화 → ~50% 유지 목표 (최소 20000봉 확보).
    """
    n = len(records)
    if n < 40:
        return list(range(n))

    closes = [close_map.get(ts, 0.0) for ts, _ in records]

    stds = []
    for i in range(20, n):
        window = closes[i - 20:i]
        mean_w = sum(window) / 20.0
        if mean_w <= 0:
            continue
        var_w = sum((x - mean_w) ** 2 for x in window) / 19.0
        stds.append(var_w ** 0.5)

    if not stds:
        return list(range(n))
    h = (sum(stds) / len(stds)) * h_mult
    if h <= 0:
        return list(range(n))

    selected = []
    s_pos, s_neg = 0.0, 0.0
    for i in range(1, n):
        prev_c, curr_c = closes[i - 1], closes[i]
        if prev_c <= 0 or curr_c <= 0:
            continue
        diff = curr_c - prev_c
        s_pos = max(0.0, s_pos + diff)
        s_neg = min(0.0, s_neg + diff)
        if s_pos > h or s_neg < -h:
            selected.append(i)
            s_pos = s_neg = 0.0

    if len(selected) < n * 0.30:
        logger.info(
            "[CUSUM] 이벤트 %d/%d (%.1f%%) < 30%% — 전체 사용",
            len(selected), n, 100.0 * len(selected) / max(n, 1),
        )
        return list(range(n))

    logger.info(
        "[CUSUM] %d → %d봉 (%.1f%% 유지)",
        n, len(selected), 100.0 * len(selected) / max(n, 1),
    )
    return selected


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
        intraday:             bool = False,
        full_cv:              bool = False,
    ) -> Dict:
        """
        GBM 모델 전체 재학습

        Args:
            X:                    피처 행렬 (None이면 DB에서 로드)
            y_dict:               {horizon: label_array} (None이면 DB에서 로드)
            weeks_back:           학습 기간 (주)
            force:                성능 저하여도 강제 교체
            use_horizon_features: Phase 2 경로 활성화 — raw_features_horizon 테이블 사용
            intraday:             True이면 경량 파라미터 사용 (장중 GIL 차단 방지)

        Returns:
            재학습 결과 딕셔너리
        """
        if not _SKLEARN_OK:
            return {"ok": False, "error": "scikit-learn 미설치"}

        logger.info(
            "[Retrain] 배치 재학습 시작 (weeks_back=%d, phase2=%s, intraday=%s)",
            weeks_back, use_horizon_features, intraday,
        )
        start_time = datetime.datetime.now()

        # Phase 2: 호라이즌별 독립 X로 재학습
        if use_horizon_features and (X is None or y_dict is None):
            if self._has_horizon_features_table():
                return self._retrain_phase2(weeks_back, force, start_time, full_cv=full_cv)
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

        # 장중 모드: 최신 데이터 MAX_TRAIN_BARS_INTRADAY 봉만 사용 (GIL 블로킹 시간 비례 단축)
        if intraday and len(X) > MAX_TRAIN_BARS_INTRADAY:
            logger.info(
                "[Retrain] 장중 경량 모드: %d → %d봉 (최신 데이터 우선)", len(X), MAX_TRAIN_BARS_INTRADAY
            )
            X = X[-MAX_TRAIN_BARS_INTRADAY:]
            y_dict = {h: y[-MAX_TRAIN_BARS_INTRADAY:] for h, y in y_dict.items()}

        if feature_names is None:
            feature_names = ["feature_{}".format(i) for i in range(X.shape[1])]

        # Robust 전처리 — 예측 경로(predict_proba)와 동일 변환 적용 (일관성 보장)
        from model.multi_horizon_model import apply_robust_preprocess
        X = apply_robust_preprocess(X, feature_names)

        # Phase C: 호라이즌별 피처셋 레지스트리 로드
        try:
            from features.horizon_feature_registry import get_available_feature_set
            _registry_ok = True
        except ImportError:
            _registry_ok = False

        results = {}
        for horizon_key in HORIZONS:
            if horizon_key not in y_dict:
                continue
            y = y_dict[horizon_key]
            if len(y) != len(X):
                continue

            # 호라이즌별 피처 슬라이싱 (Phase C)
            if _registry_ok:
                h_names = get_available_feature_set(horizon_key, feature_names)
            else:
                h_names = None

            if h_names and len(h_names) < len(feature_names):
                # 해당 호라이즌 전용 컬럼만 추출
                h_idx = [feature_names.index(n) for n in h_names]
                X_h = X[:, h_idx]
                logger.info(
                    "[Retrain] %s 호라이즌 피처 슬라이싱: %d → %d개",
                    horizon_key, len(feature_names), len(h_names),
                )
            else:
                X_h = X
                h_names = feature_names

            result = self._train_horizon(
                horizon_key,
                X_h,
                y,
                feature_names=h_names,
                force=force,
                intraday=intraday,
                full_cv=full_cv,
            )
            results[horizon_key] = result

            # 호라이즌 전용 pkl 저장 (Phase C)
            self._save_feature_names(h_names, horizon_key=horizon_key)

        # 공유 pkl도 유지 (backward compat: 구 모델·ScalerWarmup 경로)
        self._save_feature_names(feature_names)

        # P6c: RF 이종 앙상블 학습 — 장중 모드에서는 스킵 (GIL 블로킹 추가 방지)
        if intraday:
            logger.info("[Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)")
        else:
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
        intraday:    bool = False,
        full_cv:     bool = False,
    ) -> Dict:
        """
        단일 호라이즌 학습 + 교차검증

        HistGBM 가용 시 HistGradientBoostingClassifier 우선 사용 (GIL-free).
        불가 시 GradientBoostingClassifier fallback.
        intraday=True: 경량 파라미터 + CV 없이 전체 직접 학습.
        """
        # 모델 팩토리 선택 — HistGBM은 GIL을 학습 중 해제 (C++ OpenMP)
        if _HIST_GBM_OK:
            _params = HIST_GBM_PARAMS_INTRADAY if intraday else HIST_GBM_PARAMS
            def _make_model():
                return HistGradientBoostingClassifier(**_params)
        else:
            _params = GBM_PARAMS_INTRADAY if intraday else GBM_PARAMS
            def _make_model():
                return GradientBoostingClassifier(**_params)

        cv_accs = []
        if not intraday:
            # 정규 재학습: 시계열 교차검증 3폴드
            # full_cv=False (기본): 32-bit Python 메모리 방어 — fold 훈련 세트를 20k행으로 절단
            #   (Cybos+Qt+데이터수집 동시 실행 구간 — 장중·프리마켓)
            # full_cv=True: Cybos 단절 후 장 마감 재학습 전용 — 캡 해제, 전체 데이터로 정직한 CV
            tscv = TimeSeriesSplit(n_splits=3)
            for train_idx, val_idx in tscv.split(X):
                X_tr, X_val = X[train_idx], X[val_idx]
                y_tr, y_val = y[train_idx], y[val_idx]

                if not full_cv and len(X_tr) > MAX_TRAIN_BARS_INTRADAY:
                    X_tr = X_tr[-MAX_TRAIN_BARS_INTRADAY:]
                    y_tr = y_tr[-MAX_TRAIN_BARS_INTRADAY:]

                if len(np.unique(y_tr)) < 2:
                    continue

                scaler = StandardScaler()
                X_tr_s = scaler.fit_transform(X_tr)
                X_val_s = scaler.transform(X_val)

                model = _make_model()
                model.fit(X_tr_s, y_tr, sample_weight=_make_sample_weight(y_tr, horizon_key))
                acc = accuracy_score(y_val, model.predict(X_val_s))
                cv_accs.append(acc)

            if not cv_accs:
                return {"ok": False, "error": "교차검증 실패"}

        cv_acc = float(np.mean(cv_accs)) if cv_accs else None

        # 전체 데이터로 최종 학습 (장중 모드: CV 없이 여기만 실행)
        final_scaler = StandardScaler()
        X_scaled = final_scaler.fit_transform(X)
        final_model = _make_model()
        final_model.fit(X_scaled, y, sample_weight=_make_sample_weight(y, horizon_key))
        _model_type = "HistGBM" if _HIST_GBM_OK else "GBM"
        logger.debug("[Retrain] %s %s 학습 완료 (n=%d)", _model_type, horizon_key, len(X))

        # 기존 모델과 성능 비교
        old_acc  = self._load_model_acc(horizon_key)
        replaced = False

        # intraday=True: CV 없으므로 cv_acc=None → force로 취급 (기존 모델 보호 로직 비적용)
        if intraday or force or (cv_acc is not None and cv_acc > old_acc - 0.01):
            _disp_acc = cv_acc if cv_acc is not None else float("nan")
            self._save_model(horizon_key, final_model, final_scaler, _disp_acc, feature_names)
            replaced = True
            logger.info(f"[Retrain] {horizon_key} 교체 (acc {old_acc:.4f}→{_disp_acc:.4f})")
        else:
            _disp_acc = cv_acc if cv_acc is not None else float("nan")
            logger.info(f"[Retrain] {horizon_key} 유지 (acc {_disp_acc:.4f} < {old_acc:.4f})")

        return {
            "ok":       True,
            "cv_acc":   round(cv_acc, 4) if cv_acc is not None else None,
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

    def _save_feature_names(self, feature_names: List[str], horizon_key: str = None) -> None:
        """feature_names 저장.

        horizon_key 지정 시: feature_names_{horizon_key}.pkl (호라이즌 전용)
        항상: feature_names.pkl (공유, backward compat)
        """
        if horizon_key:
            h_path = os.path.join(self.model_dir, "feature_names_{}.pkl".format(horizon_key))
            with open(h_path, "wb") as f:
                pickle.dump(list(feature_names), f)
        else:
            # 공유 pkl: 전체 피처셋 저장 (구버전 모델과의 호환성)
            feature_path = os.path.join(self.model_dir, "feature_names.pkl")
            with open(feature_path, "wb") as f:
                pickle.dump(list(feature_names), f)

    def _load_feature_names(self, horizon_key: str = None):
        # type: (str) -> list
        """저장된 feature_names 로드.

        horizon_key 지정 시 전용 pkl → 없으면 공유 pkl → 없으면 빈 리스트.
        """
        if horizon_key:
            h_path = os.path.join(self.model_dir, "feature_names_{}.pkl".format(horizon_key))
            if os.path.exists(h_path):
                try:
                    with open(h_path, "rb") as f:
                        return pickle.load(f)
                except (IOError, OSError, pickle.UnpicklingError):
                    pass
        # fallback: 공유 pkl
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

    def _retrain_phase2(self, weeks_back, force, start_time, full_cv=False):
        # type: (int, bool, object, bool) -> dict
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

            # P1: CUSUM 이벤트 필터
            cusum_idx = _cusum_filter(records, close_map)
            if len(cusum_idx) < len(records):
                records = [records[i] for i in cusum_idx]

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

            result = self._train_horizon(hz, X_hz, y_hz, feature_names=use_feat_names, force=force, full_cv=full_cv)
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

            # MAX_TRAIN_BARS 상한: weeks_back 오설정·이상 입력으로 행 수 폭증 방지
            # 슬라이딩 창(26주) 정상 운영 시 ~40,000행 → 50,000 초과 불가
            # 초과 시 최신 N행 사용 (시계열 특성상 최신 우선)
            if len(records) > MAX_TRAIN_BARS:
                logger.warning(
                    "[Retrain] MAX_TRAIN_BARS 상한 적용: %d → %d행",
                    len(records), MAX_TRAIN_BARS,
                )
                records = records[-MAX_TRAIN_BARS:]

            # P1: CUSUM 이벤트 필터 — 연속 구간 반복학습 차단
            cusum_idx = _cusum_filter(records, close_map)
            if len(cusum_idx) < len(records):
                records = [records[i] for i in cusum_idx]

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

    def prune_raw_data_db(self, keep_weeks: int = RAW_DATA_PRUNE_WEEKS) -> int:
        """raw_data.db 오래된 데이터 정리 — 매주 월요일 EOD 1회 호출 권장.

        keep_weeks 이전 데이터를 raw_features / raw_candles / raw_features_horizon 에서 삭제.
        RETRAIN_WEEKS_BACK(26주)의 2배(52주)를 기본 보존 기간으로 유지.
        삭제된 총 행 수를 반환.
        """
        import sqlite3
        from config.settings import RAW_DATA_DB

        if not os.path.exists(RAW_DATA_DB):
            return 0

        cutoff = (
            datetime.datetime.now() - datetime.timedelta(weeks=keep_weeks)
        ).strftime("%Y-%m-%d %H:%M:%S")

        deleted = 0
        try:
            with sqlite3.connect(RAW_DATA_DB, timeout=15) as conn:
                for table in ("raw_features", "raw_candles", "raw_features_horizon"):
                    try:
                        r = conn.execute(
                            "DELETE FROM {} WHERE ts < ?".format(table), (cutoff,)
                        )
                        deleted += r.rowcount
                    except Exception:
                        pass  # 테이블 없으면 무시
                conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
            logger.info(
                "[Retrain] DB pruning 완료: %d행 삭제 (cutoff=%s, keep=%d주)",
                deleted, cutoff[:10], keep_weeks,
            )
        except Exception as e:
            logger.warning("[Retrain] DB pruning 실패: %s", e)
        return deleted

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
