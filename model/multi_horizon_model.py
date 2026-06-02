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
from sklearn.utils.class_weight import compute_sample_weight

from config.settings import (
    HORIZONS, HORIZON_DIR, SCALER_DIR, GBM_MIN_SAMPLES_LEAF,
    SCALER_LOG1P_FEATURES, SCALER_CLIP_FEATURES,
    SCALER_OPEN_REFRESH_INTERVAL_MIN, SCALER_OPEN_END_MINUTE,
    SCALER_GBM_REFRESH_INTERVAL_MIN,
    SCALER_FORCE_EXTREME_CONSEC, SCALER_FORCE_FEATURE_REPEAT,
    SCALER_FORCE_REFRESH_COOLDOWN_MIN,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT

logger = logging.getLogger("SIGNAL")


def apply_robust_preprocess(
    X: np.ndarray,
    feature_names: List[str],
    log1p_feats: tuple = SCALER_LOG1P_FEATURES,
    clip_feats: dict = SCALER_CLIP_FEATURES,
) -> np.ndarray:
    """GBM 입력 직전 Robust 전처리 — 학습·예측·워밍업 공통.

    atr / avg_volume : log1p (양수 long-tail 완화)
    spread_ticks     : clip(0, 20)  (극단 스프레드 cap)
    mlofi_slope      : clip(-500, 500) (slope 범위 제한)

    SGD 경로(online_learner)에는 적용하지 않는다.
    원본 배열을 수정하지 않고 복사본을 반환한다.
    """
    if not log1p_feats and not clip_feats:
        return X

    idx_map = {name: i for i, name in enumerate(feature_names)}
    X_out = X.astype(np.float64, copy=True)

    for feat in log1p_feats:
        idx = idx_map.get(feat)
        if idx is not None:
            X_out[:, idx] = np.log1p(np.maximum(X_out[:, idx], 0.0))

    for feat, (lo, hi) in clip_feats.items():
        idx = idx_map.get(feat)
        if idx is not None:
            X_out[:, idx] = np.clip(X_out[:, idx], lo, hi)

    return X_out

# 호라이즌별 class weight
# 2026-05-30 임계값 재보정 후 FLAT 비율이 ~33%로 균형잡힘.
# 이전의 강한 FL 다운웨이팅은 FL이 60~100%로 편향된 구 임계값 전용이었으므로 완화.
#
# 1m: FL=0.85 (이전 0.60 — 새 threshold로 FL~34%, 강한 억압 불필요)
_CW_1M  = {DIRECTION_FLAT: 0.85, DIRECTION_UP: 1.08, DIRECTION_DOWN: 1.08}
# 3m: FL=0.75 유지 (threshold 현행 유지, 레이블 분포 미변경)
_CW_3M  = {DIRECTION_FLAT: 0.75, DIRECTION_UP: 1.12, DIRECTION_DOWN: 1.12}
# 5m: FL=0.85 (이전 0.58 — 새 threshold로 FL~33%, 강한 억압 불필요)
_CW_5M  = {DIRECTION_FLAT: 0.85, DIRECTION_UP: 1.08, DIRECTION_DOWN: 1.08}
# 30m: balanced (이전 FL=0.65 — 새 threshold로 FL~30%, UP/DN 미세 다수이므로 balanced)
_CW_30M = {DIRECTION_FLAT: 1.00, DIRECTION_UP: 1.00, DIRECTION_DOWN: 1.00}
# 10m, 15m: compute_sample_weight("balanced") 유지 (FL~34~35%, 자동 균형)


def _make_sample_weight(y: np.ndarray, horizon: str) -> np.ndarray:
    if horizon == "30m":
        return np.array([_CW_30M.get(int(lbl), 1.0) for lbl in y])
    if horizon == "3m":
        return np.array([_CW_3M.get(int(lbl), 1.0) for lbl in y])
    if horizon == "1m":
        return np.array([_CW_1M.get(int(lbl), 1.0) for lbl in y])
    if horizon == "5m":
        return np.array([_CW_5M.get(int(lbl), 1.0) for lbl in y])
    return compute_sample_weight("balanced", y)


class MultiHorizonModel:
    """6개 호라이즌 GBM 모델 묶음"""

    # GBM predict_proba 극단 확률 상한 (conf=1.000 과신 방지)
    # 학습 범위를 벗어난 피처 입력 시 GBM이 0/1 극단 확률을 반환하는 현상 완화
    CONF_CLIP = 0.92

    # 스케일러 노후화 경고 임계값 (분) — 변동성 레짐 시프트 감지
    SCALER_WARN_MINUTES = 90
    # 극단 z-score 임계값 — 스케일러 기준통계와 현재 피처가 심하게 벗어남을 감지
    EXTREME_ZSCORE_THRESHOLD = 4.0
    EXTREME_ZSCORE_LOG_TOPK = 5

    GBM_PARAMS = {
        "n_estimators":     200,   # 100→200: BatchRetrainer 동일 수준, PreRetrain 품질 개선
        "max_depth":        5,     # 4→5: 3000샘플×balanced weight 환경에서 표현력 확대
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

        # Phase B: 정기/강제 refresh 상태
        self._last_scaler_refit_at: Optional[datetime.datetime] = None
        self._extreme_feat_streak: Dict[str, int] = {}       # 피처 → 연속 극단 분 수
        self._recent_extreme_feat_history: List[List[str]] = []  # 최근 N봉 극단 피처 이력
        self._force_cooldown_until: Optional[datetime.datetime] = None
        self.last_extreme_features: List[str] = []           # predict_proba 후 노출

        os.makedirs(HORIZON_DIR, exist_ok=True)
        os.makedirs(SCALER_DIR, exist_ok=True)

        # 섹션 8: scaler_monitor.db 초기화
        try:
            from model.scaler_monitor_db import init_db as _smdb_init
            _smdb_init()
        except Exception as _e:
            logger.debug("[ScalerMonitor] DB 초기화 스킵: %s", _e)

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

        # Robust 전처리 — 학습·예측 일관성 보장
        X_proc = apply_robust_preprocess(X, feature_names)

        for horizon in HORIZONS:
            y = targets.get(horizon)
            if y is None:
                continue

            # NaN 제거
            mask = ~np.isnan(y)
            Xm, ym = X_proc[mask], y[mask].astype(int)

            if len(np.unique(ym)) < 2:
                logger.warning(f"[Model] {horizon}: 클래스 부족, 학습 건너뜀")
                continue

            # 스케일러
            scaler = StandardScaler()
            Xs = scaler.fit_transform(Xm)

            # GBM 학습 — 30m: FL 다운웨이팅, 그 외: balanced
            clf = GradientBoostingClassifier(**self.GBM_PARAMS)
            sw = _make_sample_weight(ym, horizon)
            clf.fit(Xs, ym, sample_weight=sw)

            self.models[horizon]  = clf
            self.scalers[horizon] = scaler
            self._is_fitted[horizon] = True
            self._scaler_fitted_at[horizon] = datetime.datetime.now()

            logger.info(f"[Model] {horizon} 학습 완료 (n={len(ym)})")

        self._save_all()

    # ── 예측 ──────────────────────────────────────────────────
    def predict_proba(self, x: np.ndarray, monitor_ts: str = "") -> Dict[str, Dict]:
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

        # Robust 전처리 — log1p / clip (SGD 경로와 무관, 매 예측마다 적용)
        x2d_proc = apply_robust_preprocess(x2d, self.feature_names) if self.feature_names else x2d

        _all_extreme_names: List[str] = []  # Phase B: 전 호라이즌 극단 피처 누적
        _monitor_rows: List[dict] = []      # 섹션 8: 분봉 이벤트 행 (루프 후 일괄 INSERT)

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

            xs = scaler.transform(x2d_proc) if scaler else x2d_proc

            # 극단 z-score 감지: |z| > EXTREME_ZSCORE_THRESHOLD 피처 수 로깅
            extreme_mask = np.abs(xs[0]) > self.EXTREME_ZSCORE_THRESHOLD
            extreme_count = int(np.sum(extreme_mask))
            if extreme_count > 0:
                extreme_summary = self._summarize_extreme_zscores(xs[0], extreme_mask)
                logger.warning(
                    f"[Model] {horizon} 극단 z-score {extreme_count}개 피처 감지 "
                    f"(|z|>{self.EXTREME_ZSCORE_THRESHOLD:.0f}) — 스케일러 노후화 또는 이상 데이터 의심"
                )
                logger.warning(f"[Model] {horizon} extreme z-score top={extreme_summary}")
                # Phase B 강제 트리거용 피처명 누적
                _all_extreme_names.extend(
                    self._get_extreme_feature_names(xs[0], extreme_mask)
                )

            # 섹션 8: 호라이즌별 max_z / max_z_feature 수집 (모니터 INSERT용)
            if monitor_ts and scaler:
                _z_abs = np.abs(xs[0])
                _max_z_idx  = int(np.argmax(_z_abs))
                _max_z_val  = float(xs[0][_max_z_idx])
                _max_z_feat = (
                    self.feature_names[_max_z_idx]
                    if _max_z_idx < len(self.feature_names)
                    else f"f{_max_z_idx}"
                )
                _fa = self._scaler_fitted_at.get(horizon)
                _age = (
                    (datetime.datetime.now() - _fa).total_seconds() / 60.0
                    if _fa else None
                )
                _monitor_rows.append({
                    "ts":            monitor_ts,
                    "date":          monitor_ts[:10],
                    "horizon":       horizon,
                    "fitted_at":     _fa.strftime("%Y-%m-%d %H:%M:%S") if _fa else None,
                    "age_minutes":   round(_age, 1) if _age is not None else None,
                    "max_z":         round(_max_z_val, 4),
                    "max_z_feature": _max_z_feat,
                    "extreme_count": extreme_count,
                })
                # [ScalerMonitor] 구조화 로그 — 노후화 또는 극단 z 발생 시만 출력
                if extreme_count > 0 or (_age is not None and _age > self.SCALER_WARN_MINUTES):
                    logger.warning(
                        "[ScalerMonitor] ts=%s horizon=%s age=%.0fm max_z=%+.2f(%s) extreme=%d",
                        monitor_ts[11:16], horizon,
                        _age or 0.0, _max_z_val, _max_z_feat, extreme_count,
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
                "up":           round(up, 4),
                "down":         round(down, 4),
                "flat":         round(flat, 4),
                "direction":    direction,
                "confidence":   round(confidence, 4),
                "extreme_count": extreme_count,
            }

        # 전체 호라이즌 중 최대 극단 z-score 피처 수 (MarketDNA·대시보드용)
        self.last_z_warn_count = max(
            (r.get("extreme_count", 0) for r in results.values()), default=0
        )
        # Phase B: 전 호라이즌 union (순서 보존 dedup)
        self.last_extreme_features = list(dict.fromkeys(_all_extreme_names))

        # 섹션 8: scaler_events 일괄 INSERT (오류 시 무시 — 모니터링 전용)
        if _monitor_rows:
            try:
                from model.scaler_monitor_db import insert_events_batch
                insert_events_batch(_monitor_rows)
            except Exception as _sme:
                logger.debug("[ScalerMonitor] INSERT 스킵: %s", _sme)

        return results

    def _summarize_extreme_zscores(self, z_row: np.ndarray, extreme_mask: np.ndarray) -> str:
        """Format the largest extreme z-score features for logging."""
        feature_names = self.feature_names or []
        tagged = []

        for idx, is_extreme in enumerate(extreme_mask):
            if not is_extreme:
                continue
            name = feature_names[idx] if idx < len(feature_names) else "f{}".format(idx)
            tagged.append((name, float(z_row[idx])))

        if not tagged:
            return "none"

        tagged.sort(key=lambda item: abs(item[1]), reverse=True)
        top_items = tagged[:self.EXTREME_ZSCORE_LOG_TOPK]
        return ", ".join("{}={:+.2f}".format(name, z_value) for name, z_value in top_items)

    def _get_extreme_feature_names(
        self, z_row: np.ndarray, extreme_mask: np.ndarray
    ) -> List[str]:
        """극단 z-score 피처명 리스트 반환 (Phase B 강제 트리거용)."""
        feature_names = self.feature_names or []
        return [
            feature_names[idx] if idx < len(feature_names) else "f{}".format(idx)
            for idx, is_extreme in enumerate(extreme_mask)
            if is_extreme
        ]

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
                # pkl mtime 기준으로 in-memory 노후 시계 동기화 (재시작·EOD 로드 후 정확성 보장)
                self._scaler_fitted_at[h] = datetime.datetime.fromtimestamp(
                    os.path.getmtime(sp)
                )
                logger.info(f"[Model] {h} 로드 성공")

        self.validate_and_resync()

    def validate_and_resync(self) -> list:
        """
        feature_names ↔ 각 호라이즌 scaler 차원 정합성 검증.

        불일치 호라이즌을 _is_fitted=False로 비활성화하고 목록을 반환한다.
        반환값이 비어있지 않으면 호출부에서 즉시 GBM 재학습을 트리거해야 한다.
        """
        bad = []
        n_feat = len(self.feature_names)
        if n_feat == 0:
            return bad
        for h in list(HORIZONS):
            scaler = self.scalers.get(h)
            if scaler is None or not self._is_fitted.get(h):
                continue
            expected = getattr(scaler, "n_features_in_", None)
            if expected is not None and n_feat != expected:
                logger.error(
                    "[Model] %s 피처 불일치 — feature_names=%d scaler=%d"
                    " → 호라이즌 비활성화 (재학습 후 복구)",
                    h, n_feat, expected,
                )
                self._is_fitted[h] = False
                bad.append(h)
        if bad:
            logger.error(
                "[Model] 정합성 오류 %d개 호라이즌: %s — 즉시 재학습 필요",
                len(bad), bad,
            )
        return bad

    def is_ready(self) -> bool:
        """최소 1개 호라이즌 학습 완료 여부"""
        return any(self._is_fitted.values())

    # ── Warm Scaler Canary ────────────────────────────────────────

    def canary_stale_age_hours(self) -> float:
        """scaler pkl 파일 mtime 기준 최대 노후 시간(시간). 파일 없으면 999."""
        max_age = 0.0
        found_any = False
        for h in HORIZONS:
            sp = self._scaler_path(h)
            if os.path.exists(sp):
                age_h = (
                    datetime.datetime.now()
                    - datetime.datetime.fromtimestamp(os.path.getmtime(sp))
                ).total_seconds() / 3600.0
                max_age = max(max_age, age_h)
                found_any = True
        return max_age if found_any else 999.0

    def canary_z_warn_count(self, X_recent: np.ndarray) -> int:
        """X_recent (N×F)에 현재 scaler 적용 후 극단 z피처 수 반환 (행별 최대 합산)."""
        scaler = self.scalers.get("1m") or (
            next(iter(self.scalers.values())) if self.scalers else None
        )
        if scaler is None:
            return 0
        try:
            z = scaler.transform(X_recent)
            return int(np.sum((np.abs(z) > self.EXTREME_ZSCORE_THRESHOLD).any(axis=0)))
        except Exception:
            return 0

    # ── 스케일러 단독 재적합 (Phase A 워밍업 / 정기 refresh) ─────────

    def refit_scalers_only(
        self,
        X: np.ndarray,
        feature_names: Optional[List[str]] = None,
        trigger_ts: str = "",
        trigger_type: str = "",
        trigger_reason: str = "",
    ) -> dict:
        """GBM 모델을 유지한 채 스케일러만 재적합한다.

        GBM은 트리 기반이라 스케일 불변이므로 모델 재학습 없이 스케일러만
        갱신해도 예측 품질에 영향 없음. pkl도 저장해 재시작 후에도 유지된다.

        Args:
            X:              피처 행렬 (n_samples × n_features)
            feature_names:  피처명 리스트 (None이면 self.feature_names 사용)
            trigger_ts:     트리거 분봉 ts (섹션 8 DB UPDATE용)
            trigger_type:   'A_WARMUP'|'B_OPEN'|'C_PERIODIC'|'D_FORCE'
            trigger_reason: 트리거 사유 문자열

        Returns:
            {"ok": True, "n_bars": int, "horizons": [...], "elapsed_sec": float}
        """
        import time as _time
        _t0 = _time.time()

        # 재적합 기준은 반드시 self.feature_names (predict_proba 경로와 동일해야 함)
        # feature_names 인수가 달라도 self.feature_names 기준으로 컬럼을 재정렬하여
        # scaler 피처 수와 predict_proba 입력 피처 수가 항상 일치하도록 보장
        if X is None or len(X) == 0:
            logger.warning("[ScalerWarmup] 데이터 없음 — 재적합 건너뜀")
            return {"ok": False, "error": "데이터 없음"}

        if not self.feature_names:
            logger.warning("[ScalerWarmup] self.feature_names 없음 — 재적합 건너뜀")
            return {"ok": False, "error": "feature_names 없음"}

        names = self.feature_names   # 항상 model 기준 피처셋 사용

        # 입력 feature_names 가 제공됐으면 그에 맞게 X 컬럼 재정렬
        # (load_features_for_warmup 반환 피처셋이 달라도 안전하게 처리)
        if feature_names is not None and list(feature_names) != list(names):
            src_idx = {f: i for i, f in enumerate(feature_names)}
            try:
                col_idx = [src_idx[f] for f in names if f in src_idx]
                missing  = [f for f in names if f not in src_idx]
                if missing:
                    logger.warning(
                        "[ScalerWarmup] 입력 데이터에 없는 피처 %d개 (0 패딩): %s",
                        len(missing), missing[:5],
                    )
                X_aligned = np.zeros((len(X), len(names)), dtype=np.float64)
                src_cols   = [src_idx[f] for f in names if f in src_idx]
                dst_cols   = [i for i, f in enumerate(names) if f in src_idx]
                X_aligned[:, dst_cols] = X[:, src_cols]
                X = X_aligned
            except Exception as _ae:
                logger.warning("[ScalerWarmup] 피처 재정렬 실패 — 건너뜀: %s", _ae)
                return {"ok": False, "error": "feature realign failed"}
        elif X.shape[1] != len(names):
            logger.warning(
                "[ScalerWarmup] 피처 수 불일치 X=%d names=%d — 건너뜀",
                X.shape[1], len(names),
            )
            return {"ok": False, "error": "feature dim mismatch"}

        # 예측 경로와 동일한 Robust 전처리 후 fit (일관성 보장)
        X_proc = apply_robust_preprocess(X, names)

        refreshed = []
        for horizon in HORIZONS:
            if not self._is_fitted.get(horizon):
                continue
            if horizon not in self.scalers:
                continue
            try:
                self.scalers[horizon] = StandardScaler().fit(X_proc)
                self._scaler_fitted_at[horizon] = datetime.datetime.now()
                joblib.dump(self.scalers[horizon], self._scaler_path(horizon))
                refreshed.append(horizon)
            except Exception as _e:
                logger.warning("[ScalerWarmup] %s 재적합 실패: %s", horizon, _e)

        elapsed = round(_time.time() - _t0, 2)
        _trig_label = trigger_type or "A_WARMUP"
        logger.info(
            "[ScalerRefresh] ts=%s trigger=%s %s n=%d bars horizons=%s elapsed=%.2fs",
            trigger_ts[11:16] if trigger_ts else "—",
            _trig_label, trigger_reason,
            len(X), refreshed, elapsed,
        )
        self._last_scaler_refit_at = datetime.datetime.now()

        # 섹션 8: 트리거 분봉 행에 refresh 정보 UPDATE
        if trigger_ts:
            try:
                from model.scaler_monitor_db import update_event_refresh
                update_event_refresh(trigger_ts, _trig_label, trigger_reason)
            except Exception as _ue:
                logger.debug("[ScalerMonitor] UPDATE 스킵: %s", _ue)

        return {"ok": True, "n_bars": len(X), "horizons": refreshed, "elapsed_sec": elapsed}

    # ── Phase B: 정기/강제 스케일러 refresh 트리거 판단 ────────────────

    def check_refresh_trigger(
        self,
        bar_dt: datetime.datetime,
        extreme_feats: List[str],
    ) -> Tuple[Optional[str], str]:
        """정기(B/C) 또는 강제(D) 스케일러 refresh 트리거 여부를 판단한다.

        호출 후 trigger_type 이 None 이 아니면 호출자가 refit_scalers_only() 를
        백그라운드 스레드로 실행해야 한다.

        Args:
            bar_dt:       현재 분봉 datetime
            extreme_feats: 직전 predict_proba 에서 노출된 극단 z 피처명 리스트

        Returns:
            (trigger_type, reason)
            trigger_type: 'B_OPEN' | 'C_PERIODIC' | 'D_FORCE' | None
            reason:       사유 문자열 (로그용)
        """
        # ── 극단 피처 streak / 이력 갱신 ──────────────────────────
        current_set = set(extreme_feats)

        # 이전 분봉에 없던 피처는 streak 초기화
        for feat in list(self._extreme_feat_streak.keys()):
            if feat in current_set:
                self._extreme_feat_streak[feat] += 1
            else:
                del self._extreme_feat_streak[feat]
        for feat in current_set:
            if feat not in self._extreme_feat_streak:
                self._extreme_feat_streak[feat] = 1

        # 최근 N봉 이력 유지 (SCALER_FORCE_FEATURE_REPEAT 봉)
        self._recent_extreme_feat_history.append(list(extreme_feats))
        if len(self._recent_extreme_feat_history) > SCALER_FORCE_FEATURE_REPEAT:
            self._recent_extreme_feat_history.pop(0)

        # ── D: 강제 트리거 (쿨다운 외) ──────────────────────────────
        in_cooldown = (
            self._force_cooldown_until is not None
            and bar_dt < self._force_cooldown_until
        )
        if not in_cooldown and current_set:
            force_reason = None

            # 조건1: 동일 피처 연속 SCALER_FORCE_EXTREME_CONSEC 분
            for feat, streak in self._extreme_feat_streak.items():
                if streak >= SCALER_FORCE_EXTREME_CONSEC:
                    force_reason = f"feat={feat} consec={streak}"
                    break

            # 조건2: 최근 N봉 내 동일 피처 SCALER_FORCE_FEATURE_REPEAT 회 반복
            if not force_reason:
                from collections import Counter
                flat_feats = [
                    f
                    for bar_feats in self._recent_extreme_feat_history
                    for f in bar_feats
                ]
                for feat, cnt in Counter(flat_feats).items():
                    if cnt >= SCALER_FORCE_FEATURE_REPEAT:
                        force_reason = f"feat={feat} repeat={cnt}회"
                        break

            if force_reason:
                self._force_cooldown_until = bar_dt + datetime.timedelta(
                    minutes=SCALER_FORCE_REFRESH_COOLDOWN_MIN
                )
                self._extreme_feat_streak.clear()
                self._recent_extreme_feat_history.clear()
                return "D_FORCE", force_reason

        # ── B/C: 정기 트리거 ─────────────────────────────────────
        market_open = bar_dt.replace(hour=9, minute=0, second=0, microsecond=0)
        minutes_since_open = (bar_dt - market_open).total_seconds() / 60.0
        in_open_period = 0.0 <= minutes_since_open <= SCALER_OPEN_END_MINUTE
        interval_min = (
            SCALER_OPEN_REFRESH_INTERVAL_MIN if in_open_period
            else SCALER_GBM_REFRESH_INTERVAL_MIN
        )
        trigger_type = "B_OPEN" if in_open_period else "C_PERIODIC"

        elapsed_min = (
            (bar_dt - self._last_scaler_refit_at).total_seconds() / 60.0
            if self._last_scaler_refit_at is not None
            else float("inf")
        )

        if elapsed_min >= interval_min:
            # 즉시 타임스탬프 갱신 — refit 스레드 완료 전 이중 트리거 방지
            self._last_scaler_refit_at = bar_dt
            return trigger_type, f"elapsed={elapsed_min:.0f}min"

        return None, ""

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
