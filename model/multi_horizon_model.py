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
import pickle as _pickle
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

from config.settings import (
    HORIZONS, HORIZON_DIR, SCALER_DIR, DB_DIR, GBM_MIN_SAMPLES_LEAF,
    SCALER_LOG1P_FEATURES, SCALER_CLIP_FEATURES,
    SCALER_OPEN_REFRESH_INTERVAL_MIN, SCALER_OPEN_END_MINUTE,
    SCALER_GBM_REFRESH_INTERVAL_MIN,
    SCALER_FORCE_EXTREME_CONSEC, SCALER_FORCE_FEATURE_REPEAT,
    SCALER_FORCE_REFRESH_COOLDOWN_MIN,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT

logger = logging.getLogger("SIGNAL")


# 절대 가격 피처 목록 — 장 시작 갭 오프셋 보정 대상 (Phase 2 제거 완료 시 목록에서 삭제)
_PRICE_LEVEL_FEATURES = ("microprice", "vwap")


def apply_robust_preprocess(
    X: np.ndarray,
    feature_names: List[str],
    log1p_feats: tuple = SCALER_LOG1P_FEATURES,
    clip_feats: dict = SCALER_CLIP_FEATURES,
    price_gap_offsets: Optional[Dict[str, float]] = None,
) -> np.ndarray:
    """GBM 입력 직전 Robust 전처리 — 학습·예측·워밍업 공통.

    atr / avg_volume : log1p (양수 long-tail 완화)
    spread_ticks     : clip(0, 20)  (극단 스프레드 cap)
    mlofi_slope      : clip(-300, 300) (slope 범위 제한)
    price_gap_offsets: 절대 가격 피처를 당일 시가 대비 편차로 변환
                       (갭하락/갭상승 시 z폭발 방어 — Phase 2 완료 전 임시)

    SGD 경로(online_learner)에는 적용하지 않는다.
    원본 배열을 수정하지 않고 복사본을 반환한다.
    """
    if not log1p_feats and not clip_feats and not price_gap_offsets:
        return X

    idx_map = {name: i for i, name in enumerate(feature_names)}
    X_out = X.astype(np.float64, copy=True)

    # ① 갭 오프셋 보정 — clip보다 먼저 적용해야 보정 후 값이 clip 범위에 들어옴
    if price_gap_offsets:
        for feat, offset in price_gap_offsets.items():
            idx = idx_map.get(feat)
            if idx is not None:
                X_out[:, idx] -= offset

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
# P0: 호라이즌별 FLAT 상한 — 동적 가중치에서도 FLAT 과잉 억제 유지
_FLAT_CAP = {
    "1m": 0.75, "3m": 0.55, "5m": 0.55,
    "10m": 0.65, "15m": 0.60, "30m": 0.55,
}
_DYN_HALFLIFE   = 70   # batch_retrainer와 동기화 (100→70, 최근 70분 강조)
_DYN_CLIP_RATIO = 3.0


def _make_sample_weight(y: np.ndarray, horizon: str) -> np.ndarray:
    """P0: 동적 역빈도 + 시간감쇠 sample_weight. batch_retrainer와 동일 로직."""
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

    flat_cap = _FLAT_CAP.get(horizon)
    if flat_cap is not None:
        weights[DIRECTION_FLAT] = min(weights[DIRECTION_FLAT], flat_cap)

    return np.array([weights.get(int(lbl), 1.0) for lbl in y], dtype=np.float64)


class MultiHorizonModel:
    """6개 호라이즌 GBM 모델 묶음"""

    # GBM predict_proba 극단 확률 상한 (conf=1.000 과신 방지)
    # 학습 범위를 벗어난 피처 입력 시 GBM이 0/1 극단 확률을 반환하는 현상 완화
    # 개선3: 0.92 → 0.80 — 앙상블 캘리브레이션 최종 cap(0.85)보다 낮게 맞춰
    #        GBM 극단 출력을 조기에 억제하고 calibrator 학습 분포 정상화
    CONF_CLIP = 0.80

    # 개선5: GBM 출력 temperature scaling (T>1: 극단 확률 완만하게 억제)
    # T=1.0이면 비활성. p^(1/T) / Σp^(1/T) 으로 rank order 보존하며 극단값 완화
    GBM_TEMP_SCALE = 1.2

    # 스케일러 노후화 경고 임계값 (분) — 변동성 레짐 시프트 감지
    SCALER_WARN_MINUTES = 90
    # 극단 z-score 임계값 — 스케일러 기준통계와 현재 피처가 심하게 벗어남을 감지
    EXTREME_ZSCORE_THRESHOLD = 4.0
    EXTREME_ZSCORE_LOG_TOPK = 5

    # 이상값 피처 격리 예측 (Masked Fallback)
    MASKED_FALLBACK_MIN_STREAK = 5    # 동일 피처 연속 N분 극단 → 격리 대상
    MASKED_FALLBACK_CONF_GAIN  = 0.05 # 격리 후 conf 이 이상 오르면 채택

    # CORE 피처 AutoMask 면제 목록 — 호라이즌 그룹별 분리
    # 극단 z-score는 "데이터 오류"가 아니라 "강한 방향 신호"이므로 마스킹 금지
    # (예: 강한 하락장 → cvd_delta_norm=-0.9 연속 → z=-5 → 정상 방향 신호)
    # settings.CORE_MASK_EXEMPT_BY_GROUP 을 런타임에 참조하여 호라이즌별 적용
    # backward compat: 임포트 실패 시 단기 CORE(구 전체 CORE) 고정 사용
    try:
        from config.settings import CORE_MASK_EXEMPT_BY_GROUP as _CEMG, HORIZON_CORE_GROUP as _HCG
        _CORE_MASK_EXEMPT_BY_HZ: dict = {
            hz: _CEMG[grp] for hz, grp in _HCG.items()
        }
    except Exception:
        _CEMG = {}
        _HCG = {}
        _CORE_MASK_EXEMPT_BY_HZ: dict = {}

    # 전체 호라이즌 CORE 면제 union — predict_proba AutoMask·chronic 체크에 사용
    # (어느 호라이즌에서라도 CORE인 피처는 전체에서 마스킹 금지)
    _CORE_MASK_EXEMPT: frozenset = frozenset({
        # 단기 CORE (1m~5m) — cvd_direction/cvd 제거 (2026-06-25 Cybos 편향 확인)
        # cvd_direction: Cybos buy_vol 시스템 편향으로 +0.5 고착(98.6%), 보호 불필요
        # cvd_delta_norm: price-action 기반(Williams A/D), 극단 z = 실제 방향 신호
        "cvd_delta_norm", "cvd_divergence",
        "vwap_position", "vwap_ratio", "vwap_dev",
        "ofi_norm", "ofi_pressure",
        # macro_vix 제거 (2026-06-25): CORE 강등 — 일봉 상수, SHAP 기여 ≈ 0
        # macro_risk_off 제거 (2026-06-25): 모든 호라이즌 feature_names_hz 미포함
        #   GBM gain=0, SHAP=0 — 유령 CORE, 면제 보호 대상 없음
        # 장기 CORE (30m) 추가
        "above_vwap", "opt_chain_pcr", "opt_gex_bn",
    })

    # macro 피처 스케일러 σ 하한 — 학습기간 저변동 시 σ 극소화로 실전 z-score 폭발 방지
    # macro_feature_transformer가 이미 정규화([0,1]/[-1,1])한 값을 StandardScaler가
    # 재정규화할 때, 학습기간 VIX가 낮아 σ≈0.005이면 VIX=22 → z=35 같은 폭발 발생.
    # 각 하한은 해당 피처 이론 범위의 10~20% 수준으로 설정 (실질 변동을 허용하는 최소값).
    # 이진(0/1) 피처(risk_off·risk_on·event_flag): 이론 최대 σ=0.5(p=0.5 시).
    # floor=0.5 → z=(1-mean)/0.5 ≤ 2.0, AutoMask 임계(4.0) 미만 보장.
    # 192차 AutoMask CORE 면제와 세트여야 하는데 ScaleFloor 등록이 누락됐던 버그(232차 수정).
    _MACRO_SCALE_FLOOR: dict = {
        "macro_vix":          0.10,   # [0,1] — VIX 정규화값
        "macro_sp500_chg":    0.15,   # [-1,1] — S&P500 변동률 정규화값
        "macro_nasdaq_chg":   0.15,   # [-1,1]
        "macro_krw_chg":      0.10,   # [-1,1] — USD/KRW 변동률
        "macro_us10y_chg":    0.10,   # [-1,1] — 미국 10년물 변동률
        # macro_risk_off 제거 (2026-06-25): 모델 미포함 — global scaler 보호 불필요
        "macro_risk_on":      0.50,   # 이진(0/1) — 동일 구조
        "macro_event_flag":   0.50,   # 이진(0/1) — 동일 구조
    }

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
        # Phase C: 호라이즌별 독립 피처셋 (없으면 feature_names 공유 fallback)
        self.horizon_feature_names: Dict[str, List[str]] = {}
        # 추론 슬라이싱용 사전계산 인덱스 (predict_proba에서 배열 슬라이스에 사용)
        self._hz_feat_indices: Dict[str, np.ndarray] = {}
        self._is_fitted: Dict[str, bool] = {h: False for h in HORIZONS}
        self._scaler_fitted_at: Dict[str, datetime.datetime] = {}

        # Phase B: 정기/강제 refresh 상태
        self._last_scaler_refit_at: Optional[datetime.datetime] = None
        # P0-A: B/C PERIODIC 전용 타이머 — D_FORCE 발동으로 리셋되지 않음
        self._last_periodic_refit_at: Optional[datetime.datetime] = None
        self._extreme_feat_streak: Dict[str, int] = {}       # 피처 → 연속 극단 분 수
        self._recent_extreme_feat_history: List[List[str]] = []  # 최근 N봉 극단 피처 이력
        self._force_cooldown_until: Optional[datetime.datetime] = None
        # 재가동 cold-start 워밍업: elapsed=inf 감지 시 설정, 이 시간까지 진입 차단
        self._startup_warmup_until: Optional[datetime.datetime] = None
        self.last_extreme_features: List[str] = []           # predict_proba 후 노출
        # [⑥] opt_pcr_* 피처 감쇠 타이머 — D_FORCE가 opt_pcr 피처에서 발동 시 30분간 0.3× 감쇠
        self._pcr_dampen_until: Optional[datetime.datetime] = None
        # Gap Offset — 장 시작 시 절대 가격 피처(microprice/vwap)를 당일 시가 대비 편차로 보정
        self._price_gap_offset: Dict[str, float] = {}
        self._PCR_DAMPEN_FACTOR: float = 0.3   # 감쇠 계수
        self._PCR_DAMPEN_MINUTES: int  = 30    # 감쇠 유지 시간(분)

        # 이상값 피처 격리 예측 결과 (main.py에서 참조)
        self.last_masked_proba:    Optional[Dict] = None
        self.last_masked_features: List[str]      = []
        # 섹션 8: 모니터 행 — predict_proba()가 채우고 main.py _db_write_worker가 비동기 처리
        self.last_monitor_rows: List[dict]        = []
        # ScalerMonitor / 극단 z 경고 스로틀 — (prefix, horizon, feat) → 마지막 로그 시각
        self._scaler_warn_throttle: Dict[tuple, datetime.datetime] = {}

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
            self._apply_macro_scale_floor(scaler, horizon)

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
    def predict_proba(
        self,
        x: np.ndarray,
        monitor_ts: str = "",
        hz_feat_vecs: Optional[Dict[str, np.ndarray]] = None,
    ) -> Dict[str, Dict]:
        """
        단일 샘플 예측.

        Args:
            x:            1D 피처 배열 (기본 feat_vec)
            monitor_ts:   스케일러 모니터 타임스탬프
            hz_feat_vecs: 호라이즌별 반감기 적용 feat_vec dict (Phase 1-1).
                          주어지면 해당 호라이즌 예측에 사용; 없는 호라이즌은 x로 fallback.

        Returns:
            {"1m": {"up": 0.45, "down": 0.35, "flat": 0.20,
                    "direction": 1, "confidence": 0.45}, ...}
        """
        results = {}
        x2d = x.reshape(1, -1)

        # Robust 전처리 — log1p / clip + 갭 오프셋 (SGD 경로와 무관, 매 예측마다 적용)
        x2d_proc = (
            apply_robust_preprocess(
                x2d, self.feature_names,
                price_gap_offsets=self._price_gap_offset or None,
            )
            if self.feature_names else x2d
        )

        _all_extreme_names: List[str] = []  # Phase B: 전 호라이즌 극단 피처 누적
        _monitor_rows: List[dict] = []      # 섹션 8: 분봉 이벤트 행 (루프 후 일괄 INSERT)

        for horizon, clf in self.models.items():
            if not self._is_fitted.get(horizon):
                results[horizon] = self._default_result()
                continue

            scaler = self.scalers.get(horizon)

            # 스케일러 피처 수 불일치 방어 — 재학습 전환기에 구 스케일러가 잔존하는 경우
            # 97개 입력에 12개짜리 스케일러가 물려 ERR-FATAL 발생 방지. 다음 ScalerRefresh까지 스킵.
            if scaler is not None and self.feature_names:
                _sc_n = getattr(scaler, "n_features_in_", len(self.feature_names))
                if _sc_n != len(self.feature_names):
                    _throttle_key = ("SC_MISMATCH", horizon)
                    _now_mm = datetime.datetime.now()
                    _last_mm = self._scaler_warn_throttle.get(_throttle_key)
                    if _last_mm is None or (_now_mm - _last_mm).total_seconds() > 300:
                        logger.warning(
                            "[Model] %s 스케일러 피처 수 불일치(scaler=%d vs model=%d)"
                            " — ScalerRefresh까지 스케일러 스킵",
                            horizon, _sc_n, len(self.feature_names),
                        )
                        self._scaler_warn_throttle[_throttle_key] = _now_mm
                    scaler = None

            # 스케일러 노후화 경고: 마지막 fit 이후 SCALER_WARN_MINUTES 경과 시 WARN
            fitted_at = self._scaler_fitted_at.get(horizon)
            if fitted_at is not None:
                age_min = (datetime.datetime.now() - fitted_at).total_seconds() / 60.0
                if age_min > self.SCALER_WARN_MINUTES:
                    logger.warning(
                        f"[Model] {horizon} 스케일러 {age_min:.0f}분 미갱신 "
                        f"(≥{self.SCALER_WARN_MINUTES}분) — 변동성 레짐 시프트 시 z-score 왜곡 가능"
                    )

            # Phase C: 호라이즌별 피처 슬라이싱 인덱스
            _h_idx = self._hz_feat_indices.get(horizon)  # None이면 전체 피처 사용

            # Phase 1-1: 반감기/N분봉 feat_vec이 있으면 예측에 사용, 모니터링은 원본 유지
            if hz_feat_vecs is not None and horizon in hz_feat_vecs:
                _hx = hz_feat_vecs[horizon].reshape(1, -1)
                _hx_proc = apply_robust_preprocess(
                    _hx, self.feature_names,
                    price_gap_offsets=self._price_gap_offset or None,
                ) if self.feature_names else _hx
                # Phase C 슬라이싱: 스케일러(97개 전체)→변환 후 호라이즌 피처 슬라이싱→GBM 입력
                # 스케일러는 97개 전체 피처로 적합되므로 슬라이싱을 먼저 하면 차원 불일치 에러
                _hx_scaled = scaler.transform(_hx_proc) if scaler else _hx_proc
                xs = _hx_scaled[:, _h_idx] if _h_idx is not None else _hx_scaled
                # 모니터링은 항상 전체 피처(공유 스케일러 기준) 원본 사용
                xs_mon = scaler.transform(x2d_proc) if scaler else x2d_proc
            else:
                _x2d_scaled = scaler.transform(x2d_proc) if scaler else x2d_proc
                xs = _x2d_scaled[:, _h_idx] if _h_idx is not None else _x2d_scaled
                xs_mon = _x2d_scaled

            # [⑥] opt_pcr_* 피처 감쇠 — D_FORCE opt_pcr 발동 후 30분간 0.3× 적용
            if (
                self._pcr_dampen_until is not None
                and datetime.datetime.now() < self._pcr_dampen_until
            ):
                # Phase C: 슬라이싱 후 xs 기준으로 opt_pcr 컬럼 색인
                h_names = self.horizon_feature_names.get(horizon, self.feature_names)
                _pcr_cols = [
                    i for i, fn in enumerate(h_names)
                    if fn.startswith("opt_pcr")
                ]
                if _pcr_cols:
                    xs = xs.copy()
                    xs[0, _pcr_cols] *= self._PCR_DAMPEN_FACTOR

            # 극단 z-score 감지: 원본(xs_mon) 기준 — 모니터링 목적이므로 반감기 미적용값 사용
            extreme_mask = np.abs(xs_mon[0]) > self.EXTREME_ZSCORE_THRESHOLD
            extreme_count = int(np.sum(extreme_mask))
            if extreme_count > 0:
                extreme_summary = self._summarize_extreme_zscores(xs_mon[0], extreme_mask)
                _ex_key = ("EX", horizon)
                _now_ex = datetime.datetime.now()
                _last_ex = self._scaler_warn_throttle.get(_ex_key)
                if _last_ex is None or (_now_ex - _last_ex).total_seconds() > 600:
                    logger.warning(
                        f"[Model] {horizon} 극단 z-score {extreme_count}개 피처 감지 "
                        f"(|z|>{self.EXTREME_ZSCORE_THRESHOLD:.0f}) — 스케일러 노후화 또는 이상 데이터 의심"
                    )
                    logger.warning(f"[Model] {horizon} extreme z-score top={extreme_summary}")
                    self._scaler_warn_throttle[_ex_key] = _now_ex
                # Phase B 강제 트리거용 피처명 누적
                _all_extreme_names.extend(
                    self._get_extreme_feature_names(xs_mon[0], extreme_mask)
                )

            # 섹션 8: 호라이즌별 max_z / max_z_feature 수집 (원본 기준)
            # 매분 저장으로 실시간 패널 업데이트 보장.
            # raw/pre/mean/std 는 extreme 발생 시에만 저장 (DB 크기 절약).
            if monitor_ts and scaler:
                _z_abs = np.abs(xs_mon[0])
                _max_z_idx  = int(np.argmax(_z_abs))
                _max_z_val  = float(xs_mon[0][_max_z_idx])
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
                if extreme_count > 0:
                    _raw_val  = float(x2d[0][_max_z_idx])
                    _pre_val  = float(x2d_proc[0][_max_z_idx])
                    _sc_mean  = float(scaler.mean_[_max_z_idx])
                    _sc_std   = float(scaler.scale_[_max_z_idx])
                else:
                    _raw_val = _pre_val = _sc_mean = _sc_std = None
                _monitor_rows.append({
                    "ts":            monitor_ts,
                    "date":          monitor_ts[:10],
                    "horizon":       horizon,
                    "fitted_at":     _fa.strftime("%Y-%m-%d %H:%M:%S") if _fa else None,
                    "age_minutes":   round(_age, 1) if _age is not None else None,
                    "max_z":         round(_max_z_val, 4),
                    "max_z_feature": _max_z_feat,
                    "extreme_count": extreme_count,
                    "raw_value":     round(_raw_val, 6) if _raw_val is not None else None,
                    "pre_value":     round(_pre_val, 6) if _pre_val is not None else None,
                    "scaler_mean":   round(_sc_mean, 6) if _sc_mean is not None else None,
                    "scaler_std":    round(_sc_std,  6) if _sc_std  is not None else None,
                })
                # [ScalerMonitor] 구조화 로그 — 극단 z 또는 노후화 시만 출력 (10분 스로틀)
                if extreme_count > 0 or (_age is not None and _age > self.SCALER_WARN_MINUTES):
                    _sm_key = ("SM", horizon, _max_z_feat)
                    _now_sm = datetime.datetime.now()
                    _last_sm = self._scaler_warn_throttle.get(_sm_key)
                    if _last_sm is None or (_now_sm - _last_sm).total_seconds() > 600:
                        logger.warning(
                            "[ScalerMonitor] ts=%s horizon=%s age=%.0fm max_z=%+.2f(%s) extreme=%d",
                            monitor_ts[11:16], horizon,
                            _age or 0.0, _max_z_val, _max_z_feat, extreme_count,
                        )
                        self._scaler_warn_throttle[_sm_key] = _now_sm

            # 피처 차원 불일치 방어 — feature_names_hz.pkl과 모델 간 동기화 깨진 경우
            # (retrain에서 모델 미교체 + feature_names_hz만 갱신되는 버그 잔류물 대비)
            _model_n_in = getattr(clf, "n_features_in_", None)
            if _model_n_in is not None and xs.shape[1] != _model_n_in:
                _dim_key = ("DIM_MISMATCH", horizon)
                _now_dm = datetime.datetime.now()
                _last_dm = self._scaler_warn_throttle.get(_dim_key)
                if _last_dm is None or (_now_dm - _last_dm).total_seconds() > 300:
                    logger.error(
                        "[Model] %s 피처 차원 불일치 (xs=%d vs model.n_features_in_=%d)"
                        " — feature_names_%s.pkl 재동기화 필요, fallback 반환",
                        horizon, xs.shape[1], _model_n_in, horizon,
                    )
                    self._scaler_warn_throttle[_dim_key] = _now_dm
                results[horizon] = self._default_result()
                continue

            classes = list(clf.classes_)
            proba   = clf.predict_proba(xs)[0]

            # 개선5: temperature scaling — 극단 확률 rank-preserving 완화
            # p^(1/T) / Σp^(1/T): T=1.2 → 0.95→≈0.89, 0.80→≈0.77
            if self.GBM_TEMP_SCALE > 1.0 + 1e-6:
                _scaled = np.power(proba + 1e-9, 1.0 / self.GBM_TEMP_SCALE)
                _s_sum  = _scaled.sum()
                if _s_sum > 1e-9:
                    proba = _scaled / _s_sum

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

            # [Fix3] 방향 확률 극소값 floor — CONF_CLIP 미발동 구간(flat < 0.80)에서
            # up/down이 0.00005 미만이면 round(4)에서 0.0이 되어 앙상블 flat_score
            # 인플레이션(1-0-0=1.0)으로 이어지는 경로 예방.
            # Fix1(직접 가중합)의 1차 방어를 보완하는 호라이즌 레벨 안전망.
            _PROB_FLOOR = 0.0001
            if up < _PROB_FLOOR and direction != DIRECTION_UP:
                up = _PROB_FLOOR
            if down < _PROB_FLOOR and direction != DIRECTION_DOWN:
                down = _PROB_FLOOR

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

        # 이상값 피처 격리 예측 — 연속 MASKED_FALLBACK_MIN_STREAK 분 극단 피처 격리
        # _extreme_feat_streak 는 check_refresh_trigger 호출 전이므로 이전 분 streak 반영
        # CORE 피처(_CORE_MASK_EXEMPT) 제외: 강한 방향 추세 → 극단 z-score = 올바른 신호
        _chronic = [
            feat for feat, streak in self._extreme_feat_streak.items()
            if streak >= self.MASKED_FALLBACK_MIN_STREAK
            and feat in set(self.last_extreme_features)
            and feat not in self._CORE_MASK_EXEMPT
        ]
        # AutoMaskedFallback: 이상값 피처 3개+ 동시 발생 시 streak 없이 즉시 격리 예측
        # CORE 피처 제외 후 남은 비핵심 피처만 격리 (cvd/vwap/ofi 는 방향 신호 보존)
        _non_core_extreme = [
            f for f in self.last_extreme_features
            if f not in self._CORE_MASK_EXEMPT
        ]
        _auto_mask_feats = _non_core_extreme[:5] if len(self.last_extreme_features) >= 3 else []
        if _chronic and self.feature_names:
            self.last_masked_proba    = self._predict_masked(x2d_proc, _chronic)
            self.last_masked_features = _chronic
        elif _auto_mask_feats and self.feature_names:
            self.last_masked_proba    = self._predict_masked(x2d_proc, _auto_mask_feats)
            self.last_masked_features = _auto_mask_feats
            logger.info(
                "[AutoMasked] 이상값 %d개 즉시 격리 예측 (CORE 제외): %s",
                len(_auto_mask_feats), _auto_mask_feats,
            )
        else:
            self.last_masked_proba    = None
            self.last_masked_features = []

        # 섹션 8: 모니터 행을 caller에 위임 — 파이프라인 타이밍 윈도우 밖에서 비동기 처리
        # predict_proba()는 DB I/O 없이 반환. main.py의 _db_write_worker가 비동기로 처리.
        self.last_monitor_rows = _monitor_rows  # caller가 큐에 투입

        return results

    def _predict_masked(
        self, x2d_proc: np.ndarray, mask_features: List[str]
    ) -> Dict[str, Dict]:
        """극단 피처를 0(중립)으로 대체한 뒤 호라이즌별 예측을 반환한다.

        GBM 재학습 없이 스케일러 통과 → predict_proba 만 재실행하므로 수 ms 이내 완료.
        반환 형식은 predict_proba 와 동일 (extreme_count=0 으로 고정).
        """
        mask_idx = {
            i for i, name in enumerate(self.feature_names)
            if name in set(mask_features)
        }
        if not mask_idx:
            return {}

        xm = x2d_proc.copy()
        for i in mask_idx:
            xm[0, i] = 0.0

        results: Dict[str, Dict] = {}
        for horizon, clf in self.models.items():
            if not self._is_fitted.get(horizon):
                results[horizon] = self._default_result()
                continue
            scaler = self.scalers.get(horizon)
            _h_idx_m = self._hz_feat_indices.get(horizon)
            _xs_full_m = scaler.transform(xm) if scaler else xm
            xs = _xs_full_m[:, _h_idx_m] if _h_idx_m is not None else _xs_full_m

            _model_n_in_m = getattr(clf, "n_features_in_", None)
            if _model_n_in_m is not None and xs.shape[1] != _model_n_in_m:
                results[horizon] = self._default_result()
                continue

            classes   = list(clf.classes_)
            proba     = clf.predict_proba(xs)[0]
            if self.GBM_TEMP_SCALE > 1.0 + 1e-6:
                _scaled = np.power(proba + 1e-9, 1.0 / self.GBM_TEMP_SCALE)
                _s_sum  = _scaled.sum()
                if _s_sum > 1e-9:
                    proba = _scaled / _s_sum
            proba_map = {int(c): float(p) for c, p in zip(classes, proba)}
            up   = proba_map.get(DIRECTION_UP,   0.0)
            down = proba_map.get(DIRECTION_DOWN, 0.0)
            flat = proba_map.get(DIRECTION_FLAT, 0.0)
            direction  = max(proba_map, key=proba_map.get)
            confidence = max(up, down, flat)

            if confidence > self.CONF_CLIP:
                excess = confidence - self.CONF_CLIP
                if direction == DIRECTION_UP:
                    up    = self.CONF_CLIP; down += excess / 2.0; flat += excess / 2.0
                elif direction == DIRECTION_DOWN:
                    down  = self.CONF_CLIP; up   += excess / 2.0; flat += excess / 2.0
                else:
                    flat  = self.CONF_CLIP; up   += excess / 2.0; down += excess / 2.0
                confidence = self.CONF_CLIP

            # [Fix3] 방향 확률 극소값 floor (predict_proba와 동일 로직)
            _PROB_FLOOR = 0.0001
            if up < _PROB_FLOOR and direction != DIRECTION_UP:
                up = _PROB_FLOOR
            if down < _PROB_FLOOR and direction != DIRECTION_DOWN:
                down = _PROB_FLOOR

            results[horizon] = {
                "up":            round(up, 4),
                "down":          round(down, 4),
                "flat":          round(flat, 4),
                "direction":     direction,
                "confidence":    round(confidence, 4),
                "extreme_count": 0,
            }
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

    def _apply_macro_scale_floor(self, sc, horizon_label: str) -> None:
        """macro 피처 σ 하한 적용. fit_and_train·refresh_scalers 양쪽에서 공유.

        macro_feature_transformer가 이미 [0,1]/[-1,1]로 정규화한 값에 StandardScaler가
        재정규화하면서 학습기간 저변동 → σ 극소 → 실전 z-score 폭발 방지.
        """
        if not (self.feature_names and hasattr(sc, "scale_")):
            return
        for _feat, _floor in self._MACRO_SCALE_FLOOR.items():
            if _feat not in self.feature_names:
                continue
            _fi = self.feature_names.index(_feat)
            if _fi >= len(sc.scale_):
                continue
            if float(sc.scale_[_fi]) < _floor:
                logger.warning(
                    "[ScalerFloor] %s macro '%s' scale=%.4f → floor=%.2f 적용 (z-score 폭발 방지)",
                    horizon_label, _feat, sc.scale_[_fi], _floor,
                )
                sc.scale_[_fi] = _floor
                if hasattr(sc, "var_") and _fi < len(sc.var_):
                    sc.var_[_fi] = _floor ** 2

    def _save_all(self):
        # 스케일러는 순수 pickle.dump(protocol=4) 사용.
        # joblib.dump(protocol=4)는 헤더만 4이고 내부 numpy 배열을 별도 서브스트림으로
        # 직렬화할 때 DEFAULT_PROTOCOL(Python 3.10 = 5)을 사용해 BYTEARRAY8 opcode가
        # 삽입된다. Python 3.7(py37_32)은 opcode 63을 인식하지 못해 KeyError: 63 crash.
        # 모델(gbm_*.pkl)은 HistGBM C 확장이 별도 직렬화해 문제 없으므로 joblib 유지.
        _PROTO = 4
        for h in self.models:
            joblib.dump(self.models[h], self._model_path(h), protocol=_PROTO)
            _sp = self._scaler_path(h)
            with open(_sp, "wb") as _f:
                _pickle.dump(self.scalers[h], _f, protocol=_PROTO)
        # 공유 pkl (backward compat)
        joblib.dump(self.feature_names,
                    os.path.join(HORIZON_DIR, "feature_names.pkl"), protocol=_PROTO)
        # Phase C: 호라이즌별 전용 pkl
        for h, h_names in self.horizon_feature_names.items():
            if h_names != self.feature_names:
                h_path = os.path.join(HORIZON_DIR, "feature_names_{}.pkl".format(h))
                joblib.dump(h_names, h_path, protocol=_PROTO)
        logger.info("[Model] 전체 모델 저장 완료")

    def _load_all(self):
        # 공유 pkl (전체 피처셋 기준 — 전처리·모니터링에 사용)
        fn_path = os.path.join(HORIZON_DIR, "feature_names.pkl")
        if os.path.exists(fn_path):
            self.feature_names = joblib.load(fn_path)

        for h in HORIZONS:
            mp = self._model_path(h)
            sp = self._scaler_path(h)
            if os.path.exists(mp) and os.path.exists(sp):
                self.models[h] = joblib.load(mp)
                with open(sp, "rb") as _sf:
                    self.scalers[h] = _pickle.load(_sf)
                self._is_fitted[h] = True
                self._scaler_fitted_at[h] = datetime.datetime.fromtimestamp(
                    os.path.getmtime(sp)
                )
                logger.info(f"[Model] {h} 로드 성공")

            # Phase C: 호라이즌별 전용 pkl 로드 (없으면 공유 fallback)
            h_fn_path = os.path.join(HORIZON_DIR, "feature_names_{}.pkl".format(h))
            if os.path.exists(h_fn_path):
                _h_fnames = joblib.load(h_fn_path)
                # 모델·pkl 불일치 방어 — subprocess 타임아웃 강제 종료 시
                # gbm_{h}.pkl(저장 완료) + feature_names_{h}.pkl(미갱신) 불일치 발생 가능.
                # 불일치 감지 시 pkl을 무효화해 전체 피처셋 fallback으로 복구.
                _clf = self.models.get(h)
                _model_n = getattr(_clf, "n_features_in_", None) if _clf else None
                if _model_n is not None and len(_h_fnames) != _model_n:
                    logger.error(
                        "[Model] %s feature_names_%s.pkl(%d개) vs GBM(%d개) 불일치 — "
                        "타임아웃 강제 종료 잔류 파일 의심. pkl 무효화, 전체 피처셋 fallback.",
                        h, h, len(_h_fnames), _model_n,
                    )
                    try:
                        _bak = h_fn_path + ".mismatch_bak"
                        # os.replace: Windows에서 대상 파일이 이미 존재해도 덮어씀
                        # (os.rename은 대상 존재 시 WinError 183 발생 → 원본 잔류 → 매 시작 ERROR 반복)
                        os.replace(h_fn_path, _bak)
                        logger.warning("[Model] %s 불일치 pkl → %s 백업", h, _bak)
                    except OSError:
                        try:
                            os.remove(h_fn_path)
                            logger.warning("[Model] %s 불일치 pkl 삭제 (백업 실패)", h)
                        except OSError:
                            pass
                    # horizon_feature_names에 등록하지 않음 → 슬라이싱 비활성화 (97개 fallback)
                else:
                    self.horizon_feature_names[h] = _h_fnames
                    logger.debug("[Model] %s 전용 피처셋 로드: %d개", h, len(_h_fnames))

        # 슬라이싱 인덱스 사전계산
        self._rebuild_hz_feat_indices()

        self._check_registry_feature_consistency()
        return self.validate_and_resync()

    def _rebuild_hz_feat_indices(self) -> None:
        """horizon_feature_names → _hz_feat_indices 사전계산.

        self.feature_names 기준으로 각 호라이즌 피처의 컬럼 인덱스를 np.ndarray로 캐싱.
        predict_proba 내 슬라이싱에서 배열 인덱싱으로 O(1) 접근.
        """
        if not self.feature_names:
            self._hz_feat_indices = {}
            return
        fn_index = {n: i for i, n in enumerate(self.feature_names)}
        self._hz_feat_indices = {}
        for h, h_names in self.horizon_feature_names.items():
            if h_names == self.feature_names:
                continue  # 전체 사용 — 슬라이싱 불필요
            idx = np.array(
                [fn_index[n] for n in h_names if n in fn_index],
                dtype=np.intp,
            )
            if len(idx) > 0:
                self._hz_feat_indices[h] = idx

    def _check_registry_feature_consistency(self) -> None:
        """시작 시 registry.active_features vs feature_names.pkl 불일치 경고."""
        if not self.feature_names:
            return
        import json as _json
        registry_path = os.path.join(DB_DIR, "shap_feature_registry.json")
        if not os.path.exists(registry_path):
            return
        try:
            with open(registry_path, "r", encoding="utf-8") as fh:
                reg = _json.load(fh)
            active = list(reg.get("active_features") or [])
            if not active:
                return
            if len(active) != len(self.feature_names):
                logger.error(
                    "[Model] 시작 시 정합성 오류: registry.active=%d vs pkl.feature_names=%d"
                    " — ScalerWarmup 입력과 모델 차원이 어긋날 수 있음."
                    " 예측은 pkl 기준(%d개)으로 진행. registry 정합성 수동 확인 필요.",
                    len(active), len(self.feature_names), len(self.feature_names),
                )
        except Exception as _e:
            logger.warning("[Model] registry 정합성 확인 실패 (무해): %s", _e)

    def validate_and_resync(self) -> list:
        """
        feature_names ↔ 각 호라이즌 scaler 차원 정합성 검증.

        불일치 호라이즌을 _is_fitted=False로 비활성화하고 목록을 반환한다.
        반환값이 비어있지 않으면 호출부에서 즉시 GBM 재학습을 트리거해야 한다.
        """
        bad = []
        if not self.feature_names:
            return bad
        for h in list(HORIZONS):
            scaler = self.scalers.get(h)
            if scaler is None or not self._is_fitted.get(h):
                continue
            expected = getattr(scaler, "n_features_in_", None)
            # 스케일러는 호라이즌 무관 항상 전체 feature_names(97개) 기준으로 적합된다
            # (batch_retrainer._train_horizon: final_scaler.fit_transform(X_full) 참조).
            # Phase C 호라이즌별 슬라이싱은 스케일링 *후* GBM 입력 단계에서만 적용되므로
            # 여기서 슬라이싱된 horizon_feature_names 크기와 비교하면 항상(영구) 불일치로
            # 오판 — 매 재학습/재시작마다 전 호라이즌이 거짓으로 비활성화되고
            # resync_mismatch 재학습이 무한 재트리거되는 버그였음 (260616 발견).
            n_feat = len(self.feature_names)
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

    def validate_horizon_scaler_consistency(self):
        # type: () -> None
        """
        Phase 2: 호라이즌별 스케일러가 해당 N분봉 데이터로 적합됐는지 메타 검증.
        _scaler_meta[h]["bar_horizon"] != h 이면 재적합 예약.
        """
        scaler_meta = getattr(self, "_scaler_meta", {})
        for h, scaler in list(self.scalers.items()):
            h_meta = scaler_meta.get(h, {})
            bar_h  = h_meta.get("bar_horizon")
            if bar_h and bar_h != h:
                logger.warning(
                    "[ScalerMeta] %s 스케일러 봉 불일치 (meta=%s) → 재적합 예약", h, bar_h
                )
                self._is_fitted[h] = False

    def predict_proba_multi(self, feat_vecs):
        # type: (dict) -> dict
        """
        Phase 2: 호라이즌별 완성봉 기반 독립 벡터로 예측.
        feat_vecs = {"1m": np.array, "3m": np.array, ...}
        기존 predict_proba(x, hz_feat_vecs) 인터페이스를 활용.
        """
        import numpy as _np_pm
        base_vec = feat_vecs.get("1m")
        if base_vec is None:
            for v in feat_vecs.values():
                if v is not None:
                    base_vec = v
                    break
        if base_vec is None:
            return {}
        return self.predict_proba(base_vec, hz_feat_vecs=feat_vecs)

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
        # refit 시에는 gap_offset 미적용 — 과거 데이터 기반 재학습이라 당일 갭 보정 불필요
        X_proc = apply_robust_preprocess(X, names)

        refreshed = []
        for horizon in HORIZONS:
            # 스케일러는 GBM 학습 완료(_is_fitted) 여부와 독립적으로 재적합 가능.
            # 재시작 직후 B_INTRADAY startup_stale 등 빠른 트리거 시 _is_fitted=False 상태
            # 에서도 스케일러를 97개로 갱신해야 ERR-FATAL 방지됨.
            try:
                _new_sc = StandardScaler().fit(X_proc)

                # CORE 피처 scale 보호: 일방향 장에서 데이터가 상수에 가까울 때 scaler 보호
                # 일방향 장에서 cvd_direction=-1 연속 → raw_std=0 → sklearn이 scale_=1.0으로
                # 치환 → transform(-1)=0 → GBM이 "중립 CVD"로 해석 → FLAT 100% 고착 방지
                # 주의: scale_ < 0.05 체크는 sklearn의 자동 치환(std=0→scale=1) 때문에 무력화됨
                # → raw std를 직접 계산하여 감지
                _old_sc = self.scalers.get(horizon)
                if (
                    _old_sc is not None
                    and hasattr(_new_sc, "scale_")
                    and self.feature_names
                ):
                    # 호라이즌별 CORE 면제셋 사용 — 해당 호라이즌 CORE만 보호
                    _hz_core_exempt = self._CORE_MASK_EXEMPT_BY_HZ.get(
                        horizon, self._CORE_MASK_EXEMPT
                    )
                    for _feat in _hz_core_exempt:
                        if _feat not in self.feature_names:
                            continue
                        _fi = self.feature_names.index(_feat)
                        if _fi >= len(_new_sc.scale_):
                            continue
                        # raw std 직접 계산 — sklearn 치환 전 실제 분산 확인
                        _raw_std = float(np.std(X_proc[:, _fi]))
                        if _raw_std < 0.05:
                            # identity transform(mean=0, scale=1) 강제 적용
                            # 이유: 이전 스케일러도 std≈0 조건에서 학습됐을 경우 mean≈편향값,
                            # scale=1(sklearn 자동치환) → 복원해도 transform=0 고착 재발.
                            # 6/9 실증: C_PERIODIC→mean_=-0.5, scale_=1.0 → transform(-0.5)=0 →
                            # 재시동 후 이전 스케일러 복원해도 동일 결과 → FLAT 100% 144분 지속.
                            # identity: transform(x)=x → cvd_direction=-0.5가 -0.5로 GBM 전달.
                            _new_sc.mean_[_fi]  = 0.0
                            _new_sc.scale_[_fi] = 1.0
                            if hasattr(_new_sc, "var_") and _fi < len(_new_sc.var_):
                                _new_sc.var_[_fi] = 1.0
                            logger.warning(
                                "[ScalerRefresh] %s CORE '%s' raw_std≈0(%.4f)"
                                " → identity(0,1) 강제 (FLAT 100%% 방지)",
                                horizon, _feat, _raw_std,
                            )

                self._apply_macro_scale_floor(_new_sc, horizon)
                self.scalers[horizon] = _new_sc
                self._scaler_fitted_at[horizon] = datetime.datetime.now()
                # 원자적 저장: tmp에 쓴 후 os.replace로 교체 — 읽기 도중 corrupt 방지
                # pickle.dump(protocol=4): joblib.dump는 내부 numpy 서브스트림에
                # DEFAULT_PROTOCOL(=5) 사용 → BYTEARRAY8 삽입 → py37_32 KeyError: 63
                _dst = self._scaler_path(horizon)
                _tmp = _dst + ".tmp"
                with open(_tmp, "wb") as _sf:
                    _pickle.dump(self.scalers[horizon], _sf, protocol=4)
                os.replace(_tmp, _dst)
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

        # [⑥] D_FORCE + opt_pcr 피처 → 30분 감쇠 타이머 설정
        if trigger_type == "D_FORCE" and "opt_pcr" in trigger_reason:
            self._pcr_dampen_until = datetime.datetime.now() + datetime.timedelta(
                minutes=self._PCR_DAMPEN_MINUTES
            )
            logger.warning(
                "[PCR-Dampen] opt_pcr_* 피처 D_FORCE 발동 → %d분간 %.1f× 감쇠 적용",
                self._PCR_DAMPEN_MINUTES, self._PCR_DAMPEN_FACTOR,
            )

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
        # 이진(0/1) 피처는 스케일러 재적합으로 z폭발 해소 불가 → D_FORCE 트리거 제외
        from config.settings import DFORCE_EXCLUDE_FEATURES
        current_set = set(f for f in extreme_feats if f not in DFORCE_EXCLUDE_FEATURES)

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
        # DFORCE_EXCLUDE_FEATURES를 이력에서도 제거 — 제외 피처가 repeat 카운터에 포함되던 버그 수정
        self._recent_extreme_feat_history.append([f for f in extreme_feats if f not in DFORCE_EXCLUDE_FEATURES])
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
        # P0-A: _last_periodic_refit_at 사용 — D_FORCE 발동으로 타이머가 리셋되지 않도록 분리
        market_open = bar_dt.replace(hour=9, minute=0, second=0, microsecond=0)
        minutes_since_open = (bar_dt - market_open).total_seconds() / 60.0
        in_open_period = 0.0 <= minutes_since_open <= SCALER_OPEN_END_MINUTE
        interval_min = (
            SCALER_OPEN_REFRESH_INTERVAL_MIN if in_open_period
            else SCALER_GBM_REFRESH_INTERVAL_MIN
        )
        trigger_type = "B_OPEN" if in_open_period else "C_PERIODIC"

        elapsed_min = (
            (bar_dt - self._last_periodic_refit_at).total_seconds() / 60.0
            if self._last_periodic_refit_at is not None
            else float("inf")
        )

        if elapsed_min >= interval_min:
            # 즉시 타임스탬프 갱신 — refit 스레드 완료 전 이중 트리거 방지
            self._last_periodic_refit_at = bar_dt
            self._last_scaler_refit_at = bar_dt  # 공통 타임스탬프도 동기화 (age 계산 등 호환)
            # cold-start 감지: 최초 재적합(elapsed=inf)이면 3분 진입 차단 워밍업 설정
            if elapsed_min == float("inf"):
                self._startup_warmup_until = bar_dt + datetime.timedelta(minutes=3)
            return trigger_type, f"elapsed={elapsed_min:.0f}min"

        return None, ""

    def is_in_startup_warmup(self, bar_dt: datetime.datetime) -> bool:
        """재가동 cold-start 워밍업 기간 여부 (True이면 진입 차단)."""
        return (
            self._startup_warmup_until is not None
            and bar_dt < self._startup_warmup_until
        )

    def set_feature_names(self, names: List[str]) -> None:
        """GBM 미학습 상태에서 SGD 활성화를 위한 피처명 부트스트랩."""
        if not self.feature_names:
            self.feature_names = list(names)
            self._rebuild_hz_feat_indices()

    def set_daily_gap_offset(self, today_open: float) -> None:
        """장 시작 시 1회 호출 — 절대 가격 피처의 갭 오프셋을 설정한다.

        스케일러 μ와 당일 시가의 차이를 오프셋으로 기록한다.
        이후 apply_robust_preprocess에서 절대 가격 피처값에서 오프셋을 차감하여
        스케일러가 실질적으로 '당일 시가 대비 편차'를 z-score로 변환하게 한다.

        효과: z = (microprice - today_open) / σ → 갭 크기와 무관하게 z 안정
        제거 조건: Phase 2-C/D (microprice/vwap 절대값 피처 제거) 완료 후 불필요.
        """
        if not self.feature_names:
            return
        offsets = {}
        for feat in _PRICE_LEVEL_FEATURES:
            if feat not in self.feature_names:
                continue
            idx = self.feature_names.index(feat)
            for h, scaler in self.scalers.items():
                if scaler is None or not hasattr(scaler, "mean_"):
                    continue
                if idx < len(scaler.mean_):
                    mu = float(scaler.mean_[idx])
                    offsets[feat] = today_open - mu
                    break  # 호라이즌별 μ가 다를 수 있으나 가격 피처는 동일 수준이므로 첫 호라이즌 사용
        self._price_gap_offset = offsets
        logger.info(
            "[GapOffset] today_open=%.2f | offset: %s",
            today_open,
            {k: round(v, 3) for k, v in offsets.items()},
        )

    def reset_daily_gap_offset(self) -> None:
        """장 마감 후 오프셋 초기화 — EOD reset_daily에서 호출."""
        self._price_gap_offset = {}

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
