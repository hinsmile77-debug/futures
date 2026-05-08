# strategy/regime_fingerprint.py — 피처 분포 드리프트 감지 (PSI 기반)
"""
WFA 학습 피처 분포 vs. Live 피처 분포를 PSI(Population Stability Index)로 비교하여
CUSUM보다 2~5일 빠른 시장 구조 변화를 감지한다.

PSI = Σ (A_i - B_i) × ln(A_i / B_i)
  A_i: WFA 학습 데이터의 구간별 비율
  B_i: 최근 N분 Live 데이터의 구간별 비율

경보 기준:
  PSI < 0.10 : CLEAR     — 안정
  PSI 0.10~0.20: WATCHLIST — 월간 재최적화 2주 앞당김
  PSI > 0.20 : ALARM     — 즉시 param_optimizer 실행
  PSI > 0.30 : CRITICAL  — 신규 진입 중단 검토

모니터 대상 피처: CVD·VWAP·OFI (CORE 3개)
"""
from __future__ import annotations

import json
import logging
import math
import os
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from strategy.param_drift_detector import DriftLevel

logger = logging.getLogger(__name__)

# ─── 설정 상수 ──────────────────────────────────────────────────────────────
_CORE_FEATURES = ("cvd_divergence", "vwap_position", "ofi_norm")   # CORE 3개 피처 키
_N_BINS        = 10                                  # PSI 히스토그램 구간 수
_LIVE_WIN_MINS = 5000                                # Live 버퍼 크기 (≈ 20 거래일 × 250분)
_EPS           = 1e-6                                # ln(0) 방지 소수점 하한

_PSI_WATCH = 0.10
_PSI_ALARM = 0.20
_PSI_CRIT  = 0.30

_FP_FILE = os.path.join(
    os.path.dirname(__file__),
    "..", "data", "regime_fingerprint.json",
)


class RegimeFingerprint:
    """
    PSI 기반 피처 분포 드리프트 감지기.

    Attributes:
        _training    : 피처명 → (bin_edges, proportions) — WFA 학습 분포
        _live_buf    : 피처명 → deque[float] — 최근 Live 값 버퍼
        _current_psi : 최근 계산된 최대 PSI
        _current_level: 현재 경보 수준 (DriftLevel)
    """

    def __init__(self, fp_path: Optional[str] = None):
        self._fp_path      = fp_path or _FP_FILE
        self._training:    Dict[str, Tuple[List[float], List[float]]] = {}
        self._live_buf:    Dict[str, deque] = {
            feat: deque(maxlen=_LIVE_WIN_MINS) for feat in _CORE_FEATURES
        }
        self._current_psi   = 0.0
        self._current_level = DriftLevel.CLEAR
        self._per_feature_psi: Dict[str, float] = {f: 0.0 for f in _CORE_FEATURES}

        self._load_fingerprint()

    # ─── 공개 인터페이스 ────────────────────────────────────────────────────
    def save_training_fingerprint(self, wfa_features: List[dict]) -> None:
        """
        WFA 학습 피처 분포 저장.
        버전 교체 후 새로운 WFA 학습 결과 적용 시 호출.

        Args:
            wfa_features: 각 원소가 피처 dict인 리스트
                          e.g. [{"cvd": 0.3, "vwap_position": 0.1, "ofi": -0.2}, ...]
        """
        if not wfa_features:
            logger.warning("[RegimeFingerprint] wfa_features 비어 있음 — 저장 생략")
            return

        self._training.clear()
        for feat in _CORE_FEATURES:
            vals = [row[feat] for row in wfa_features if feat in row]
            if len(vals) < _N_BINS * 2:
                logger.warning(
                    "[RegimeFingerprint] %s 샘플 부족(%d) — 피처 스킵", feat, len(vals)
                )
                continue
            edges, props = _build_histogram(vals, _N_BINS)
            self._training[feat] = (edges, props)

        self._save_fingerprint()
        logger.info(
            "[RegimeFingerprint] 학습 분포 저장 완료 — 피처: %s",
            list(self._training.keys()),
        )

    def update_live(self, features: dict) -> float:
        """
        매분 호출 — Live 피처 값을 버퍼에 추가하고 PSI를 계산·반환.

        Args:
            features: 피처 dict (feature_builder.build() 반환값)

        Returns:
            현재 최대 PSI (CORE 3개 중 최고값)
        """
        for feat in _CORE_FEATURES:
            val = features.get(feat)
            if val is not None and math.isfinite(val):
                self._live_buf[feat].append(float(val))

        if not self._training:
            return 0.0

        min_live = _N_BINS * 5   # 구간당 최소 5개
        psi_max  = 0.0
        for feat, (edges, train_props) in self._training.items():
            live_vals = list(self._live_buf[feat])
            if len(live_vals) < min_live:
                continue
            live_props = _compute_proportions(live_vals, edges)
            psi = _compute_psi(train_props, live_props)
            self._per_feature_psi[feat] = psi
            psi_max = max(psi_max, psi)

        self._current_psi   = psi_max
        self._current_level = _psi_to_level(psi_max)

        if self._current_level >= DriftLevel.WATCHLIST:
            logger.warning(
                "[RegimeFingerprint] PSI=%.3f → %s | %s",
                psi_max,
                DriftLevel.name(self._current_level),
                " | ".join(
                    "%s=%.3f" % (f, self._per_feature_psi.get(f, 0.0))
                    for f in _CORE_FEATURES
                ),
            )

        return psi_max

    def get_level(self) -> int:
        """현재 경보 수준 (DriftLevel 호환)."""
        return self._current_level

    def get_psi(self) -> float:
        """현재 최대 PSI 값."""
        return self._current_psi

    def get_per_feature_psi(self) -> Dict[str, float]:
        """피처별 PSI 값 반환."""
        return dict(self._per_feature_psi)

    def reset_to_live_baseline(self) -> bool:
        """
        현재 Live 버퍼를 새로운 학습 기준 분포로 승격.
        버전 교체 시 apply_best() 후 호출 — 새 파라미터 기준 분포로 초기화.

        Returns:
            True if baseline was updated, False if live buffer too small.
        """
        min_samples = _N_BINS * 5
        updated = False
        self._training.clear()
        for feat in _CORE_FEATURES:
            vals = list(self._live_buf[feat])
            if len(vals) < min_samples:
                continue
            edges, props = _build_histogram(vals, _N_BINS)
            self._training[feat] = (edges, props)
            updated = True

        if updated:
            self._save_fingerprint()
            logger.info(
                "[RegimeFingerprint] Live 버퍼 → 학습 기준 승격 (버전 교체 기준선 갱신)"
            )
        else:
            logger.warning(
                "[RegimeFingerprint] Live 버퍼 샘플 부족 — 기준선 갱신 생략 (최소 %d개 필요)",
                min_samples,
            )
        return updated

    def has_training_data(self) -> bool:
        """학습 분포 데이터 보유 여부."""
        return bool(self._training)

    # ─── 내부 헬퍼 ─────────────────────────────────────────────────────────
    def _save_fingerprint(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._fp_path), exist_ok=True)
            payload = {
                "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "features": {
                    feat: {"edges": edges, "props": props}
                    for feat, (edges, props) in self._training.items()
                },
            }
            with open(self._fp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning("[RegimeFingerprint] 저장 실패: %s", e)

    def _load_fingerprint(self) -> None:
        try:
            if not os.path.exists(self._fp_path):
                return
            with open(self._fp_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            for feat, info in payload.get("features", {}).items():
                self._training[feat] = (info["edges"], info["props"])
            logger.info(
                "[RegimeFingerprint] 저장된 분포 로드 — %s (저장일: %s)",
                list(self._training.keys()),
                payload.get("saved_at", "?"),
            )
        except Exception as e:
            logger.warning("[RegimeFingerprint] 로드 실패 (신규 시작): %s", e)


# ─── PSI 계산 유틸리티 ──────────────────────────────────────────────────────
def _build_histogram(
    vals: List[float], n_bins: int
) -> Tuple[List[float], List[float]]:
    """
    균등 구간 히스토그램 생성.

    Returns:
        (bin_edges, proportions) — edges: n_bins+1개, props: n_bins개 (합=1)
    """
    lo, hi = min(vals), max(vals)
    if lo == hi:
        return [lo - _EPS, hi + _EPS], [1.0]

    step  = (hi - lo) / n_bins
    edges = [lo + i * step for i in range(n_bins + 1)]
    edges[-1] += _EPS   # 최대값 포함

    counts = [0] * n_bins
    for v in vals:
        idx = int((v - lo) / step)
        idx = min(idx, n_bins - 1)
        counts[idx] += 1

    total = len(vals)
    props = [c / total for c in counts]
    return edges, props


def _compute_proportions(vals: List[float], edges: List[float]) -> List[float]:
    """
    주어진 bin_edges를 사용해 vals의 구간별 비율 계산.
    학습 분포와 동일한 구간 경계를 사용해야 PSI가 유효하다.
    """
    n_bins = len(edges) - 1
    if n_bins <= 0:
        return [1.0]

    lo   = edges[0]
    hi   = edges[-1]
    span = hi - lo
    step = span / n_bins if span > 0 else 1.0

    counts = [0] * n_bins
    total  = 0
    for v in vals:
        if v < lo:
            counts[0] += 1
        elif v >= hi:
            counts[-1] += 1
        else:
            idx = int((v - lo) / step)
            counts[min(max(idx, 0), n_bins - 1)] += 1
        total += 1

    if total == 0:
        return [0.0] * n_bins
    return [c / total for c in counts]


def _compute_psi(train_props: List[float], live_props: List[float]) -> float:
    """PSI = Σ (A_i - B_i) × ln(A_i / B_i)"""
    psi = 0.0
    n   = min(len(train_props), len(live_props))
    for i in range(n):
        a = max(train_props[i], _EPS)
        b = max(live_props[i],  _EPS)
        psi += (a - b) * math.log(a / b)
    return psi


def _psi_to_level(psi: float) -> int:
    if psi >= _PSI_CRIT:
        return DriftLevel.CRITICAL
    elif psi >= _PSI_ALARM:
        return DriftLevel.ALARM
    elif psi >= _PSI_WATCH:
        return DriftLevel.WATCHLIST
    return DriftLevel.CLEAR


# ─── 전역 싱글턴 ────────────────────────────────────────────────────────────
_fingerprint: Optional[RegimeFingerprint] = None


def get_fingerprint() -> RegimeFingerprint:
    """전역 RegimeFingerprint 싱글턴 반환."""
    global _fingerprint
    if _fingerprint is None:
        _fingerprint = RegimeFingerprint()
    return _fingerprint
