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

import bisect
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
            self._try_bootstrap_baseline()
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

    def _try_bootstrap_baseline(self) -> None:
        """[298차] 학습 분포 최초 자동 부트스트랩.

        save_training_fingerprint()(WFA 피처 분포 저장)를 호출하는 곳이 파이프라인
        어디에도 없어 self._training이 영원히 비어 있었고, update_live()의
        `if not self._training: return 0.0` 가드에 매번 걸려 PSI가 항상 0.000/CLEAR로
        고정되는 문제가 있었다(data/regime_fingerprint.json 자체가 존재하지 않았음).

        reset_to_live_baseline()(원래 HotSwap 이후에만 수동 호출)과 동일한 로직을
        최소 표본이 쌓이면 자동으로 1회 수행해, "비교할 기준 분포 자체가 없는" 상태를
        벗어난다. 이 시점 이후로는 이 스냅샷 대비 실제 라이브 분포 이동을 감지한다.
        """
        min_samples = _N_BINS * 5
        if any(len(self._live_buf[f]) < min_samples for f in _CORE_FEATURES):
            return
        if self.reset_to_live_baseline():
            logger.info(
                "[RegimeFingerprint] 학습 분포 없음 — live 버퍼 %d개로 최초 자동 부트스트랩",
                min_samples,
            )

    def has_training_data(self) -> bool:
        """학습 분포 데이터 보유 여부."""
        return bool(self._training)

    def warm_live_buffer(self, feature_rows: List[dict]) -> int:
        """[371차] 재시작 시 라이브 버퍼 워밍업.

        `_live_buf`는 디스크에 영속화된 적이 없는 순수 인메모리 버퍼라, 매 거래일
        새 프로세스로 기동될 때마다(오버나이트 금지 원칙상 하루 1프로세스) 비어서
        시작했다. `_LIVE_WIN_MINS`(20거래일 취지)와 달리 실제로는 그날 하루치
        (최대 ~370분)만 쌓인 뒤 다음날 다시 초기화되길 반복 — 특히 장 시작 후
        min_live(50분) 문턱을 막 넘긴 시점의 PSI가 소표본 노이즈로 크게 튀는
        현상(0723 장 시작 직후 PSI=18 관측, 하루 종일 필터로도 PSI=1.6대 CRITICAL
        고착)의 핵심 원인이었다(dev_memory DECISION_LOG 371차 항목 — 재현
        시뮬레이션으로 확정). `raw_features` 테이블(수개월치 보관)에서 최근 값을
        읽어와 재시작 직후에도 다표본 상태로 시작하게 한다.

        Args:
            feature_rows: 오래된 것부터 최신 순 피처 dict 리스트
                          (utils.db_utils.fetch_recent_raw_features() 파싱 결과)

        Returns:
            CORE 3피처 중 가장 적게 채워진 개수(진단 로그용, 0이면 워밍업 실패)
        """
        counts = {}
        for feat in _CORE_FEATURES:
            self._live_buf[feat].clear()
            for row in feature_rows:
                val = row.get(feat)
                if isinstance(val, (int, float)) and math.isfinite(val):
                    self._live_buf[feat].append(float(val))
            counts[feat] = len(self._live_buf[feat])
        return min(counts.values()) if counts else 0

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
    분위수(quantile) 기반 히스토그램 생성 — 균등폭(equal-width) 대신 학습 데이터
    기준 각 구간이 동일한 비율(~1/n_bins)을 갖도록 경계를 잡는다(equal-frequency
    binning). [371차] CVD divergence·OFI norm처럼 0 부근에 뾰족하게 몰린
    (leptokurtic) 분포에 균등폭을 적용하면 구간 하나에 97~98%가 쏠리는
    "메가빈"이 생겨 PSI가 수학적으로 과대 산출됐다(실측: cvd_divergence 98.31%,
    ofi_norm 97.47%가 10구간 중 1구간에 집중, dev_memory DECISION_LOG 371차
    항목). 분위수 기반은 학습 시점 기준 정의상 메가빈이 생기지 않는다.

    Returns:
        (bin_edges, proportions) — edges: 최대 n_bins+1개(동일값이 많아 구간이
        저절로 합쳐지면 그보다 적을 수 있음), props: edges와 짝 맞음(합=1)
    """
    if not vals:
        return [0.0, 1.0], [1.0]
    lo, hi = min(vals), max(vals)
    if lo == hi:
        return [lo - _EPS, hi + _EPS], [1.0]

    sorted_vals = sorted(vals)
    n = len(sorted_vals)
    raw_edges = (
        [lo]
        + [sorted_vals[min(int(round(i * n / n_bins)), n - 1)] for i in range(1, n_bins)]
        + [hi + _EPS]
    )

    # 동일값이 많아 분위수 경계가 겹치면(저카디널리티) 중복 경계를 합친다 —
    # 구간 수가 n_bins보다 줄어들 뿐 계산 자체는 그대로 유효.
    edges = [raw_edges[0]]
    for e in raw_edges[1:]:
        if e > edges[-1]:
            edges.append(e)
    if len(edges) < 2:
        return [lo - _EPS, hi + _EPS], [1.0]

    props = _compute_proportions(vals, edges)
    return edges, props


def _compute_proportions(vals: List[float], edges: List[float]) -> List[float]:
    """
    주어진 bin_edges를 사용해 vals의 구간별 비율 계산.
    학습 분포와 동일한 구간 경계를 사용해야 PSI가 유효하다.
    [371차] 분위수 기반 경계는 폭이 균등하지 않으므로 산술 나눗셈으로 구간
    인덱스를 구할 수 없다 — bisect로 실제 경계와 비교해 구간을 찾는다.
    """
    n_bins = len(edges) - 1
    if n_bins <= 0:
        return [1.0]

    lo = edges[0]
    hi = edges[-1]

    counts = [0] * n_bins
    total  = 0
    for v in vals:
        if v < lo:
            counts[0] += 1
        elif v >= hi:
            counts[-1] += 1
        else:
            idx = bisect.bisect_right(edges, v) - 1
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
