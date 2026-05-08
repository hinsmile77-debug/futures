# strategy/param_drift_detector.py — 성과 드리프트 조기 경보 시스템
"""
CUSUM(Cumulative Sum) 통계 검정 기반 전략 성과 저하 조기 경보.

핵심 아이디어:
  - WFA 기준 Sharpe에서 일별 PnL Z-score를 누적합산(CUSUM)
  - 정상 성과는 누적합이 0 근처를 유지
  - 성과 저하 시 누적합이 음의 방향으로 이탈 → 조기 감지
  - 롤백 경보(Sharpe < 0.8) 보다 2~4일 앞서 WATCHLIST 경보 발생

CUSUM 공식:
  S_n = max(0, S_{n-1} + (x_n - μ_ref) / σ_ref - k)
  여기서:
    x_n   = 당일 일별 PnL (정규화)
    μ_ref = WFA 기준 일별 기대값
    σ_ref = WFA 기준 일별 PnL 표준편차
    k     = 허용 슬랙 (기본 0.5σ — 작은 하락은 경보 안 내도록)
    h     = 경보 임계값 (기본 4.0 — 4σ 누적 이탈 시 경보)

경보 수준:
  CLEAR    : CUSUM < 2.0  — 정상
  WATCHLIST: CUSUM >= 2.0 — 모니터링 강화 (파라미터 재점검 예고)
  ALARM    : CUSUM >= 4.0 — 즉시 파라미터 재최적화 검토
  CRITICAL : CUSUM >= 6.0 — 롤백 검토 / 규모 축소

사용 예:
  detector = DriftDetector(ref_daily_pnl_mean=50000, ref_daily_pnl_std=80000)
  level, cusum, msg = detector.update(today_pnl=30000)
  if level >= DriftLevel.ALARM:
      notify_slack(msg)
"""
from __future__ import annotations

import logging
import math
from collections import deque
from datetime import datetime
from typing import Deque, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ─── 경보 수준 정의 ──────────────────────────────────────────────────────
class DriftLevel:
    CLEAR     = 0   # 정상
    WATCHLIST = 1   # 모니터링 강화
    ALARM     = 2   # 즉시 검토 권고
    CRITICAL  = 3   # 롤백 / 사이즈 축소 검토

    _NAMES = {0: "CLEAR", 1: "WATCHLIST", 2: "ALARM", 3: "CRITICAL"}
    _COLORS = {0: "#3FB950", 1: "#E3B341", 2: "#D29922", 3: "#F85149"}

    @classmethod
    def name(cls, level: int) -> str:
        return cls._NAMES.get(level, "UNKNOWN")

    @classmethod
    def color(cls, level: int) -> str:
        return cls._COLORS.get(level, "#8B949E")


# ─────────────────────────────────────────────────────────────────────────
class DriftDetector:
    """
    일별 PnL 기반 CUSUM 성과 드리프트 감지기.

    Attributes:
        ref_mean : WFA 기준 일별 PnL 기대값 (원)
        ref_std  : WFA 기준 일별 PnL 표준편차 (원)
        k_slack  : CUSUM 슬랙 계수 (기본 0.5 — 작은 하락 허용)
        h_watch  : WATCHLIST 임계값 (기본 2.0)
        h_alarm  : ALARM 임계값 (기본 4.0)
        h_crit   : CRITICAL 임계값 (기본 6.0)
        window   : CUSUM 초기화 전 최대 누적 기간 (기본 20 거래일)
    """

    def __init__(
        self,
        ref_daily_pnl_mean: float = 0.0,
        ref_daily_pnl_std:  float = 1.0,
        k_slack:  float = 0.5,
        h_watch:  float = 2.0,
        h_alarm:  float = 4.0,
        h_crit:   float = 6.0,
        window:   int   = 20,
    ):
        self.ref_mean = ref_daily_pnl_mean
        self.ref_std  = max(ref_daily_pnl_std, 1.0)  # 0-division 방지
        self.k_slack  = k_slack
        self.h_watch  = h_watch
        self.h_alarm  = h_alarm
        self.h_crit   = h_crit
        self.window   = window

        self._cusum_neg: float = 0.0   # 하방 CUSUM (성과 저하 감지용)
        self._cusum_pos: float = 0.0   # 상방 CUSUM (성과 급등 감지용)
        self._history:  Deque[Tuple[str, float, float, int]] = deque(maxlen=window)
        self._days_since_reset: int = 0

    def update(self, daily_pnl: float) -> Tuple[int, float, str]:
        """
        일별 PnL을 입력받아 CUSUM 통계 갱신 후 경보 수준 반환.

        Args:
            daily_pnl: 당일 실현 PnL (원)

        Returns:
            (DriftLevel, cusum_neg_value, 경보 메시지)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        z = (daily_pnl - self.ref_mean) / self.ref_std

        # 하방 CUSUM: 성과 저하(z가 낮을수록) 누적
        # S_n = max(0, S_{n-1} - z - k)  ← 음의 방향으로 이탈 추적
        self._cusum_neg = max(0.0, self._cusum_neg - z - self.k_slack)
        # 상방 CUSUM: 성과 급등 누적 (사이즈 확대 참고용)
        self._cusum_pos = max(0.0, self._cusum_pos + z - self.k_slack)

        self._days_since_reset += 1

        level = self._compute_level(self._cusum_neg)
        msg   = self._build_message(today, daily_pnl, z, self._cusum_neg, level)

        self._history.append((today, daily_pnl, self._cusum_neg, level))

        # CUSUM 자동 초기화: 20 거래일 경과 후 리셋
        if self._days_since_reset >= self.window:
            self._reset()

        logger.debug(
            "[DriftDetector] %s PnL=%+.0f Z=%.2f CUSUM_neg=%.2f → %s",
            today, daily_pnl, z, self._cusum_neg, DriftLevel.name(level),
        )
        return level, self._cusum_neg, msg

    def get_level(self) -> int:
        """현재 경보 수준 반환 (업데이트 없이 조회)."""
        return self._compute_level(self._cusum_neg)

    def get_cusum(self) -> float:
        """현재 하방 CUSUM 값 반환."""
        return self._cusum_neg

    def get_cusum_pos(self) -> float:
        """현재 상방 CUSUM 값 반환 (성과 급등 강도)."""
        return self._cusum_pos

    def get_history(self) -> List[Tuple[str, float, float, int]]:
        """히스토리: [(date, daily_pnl, cusum_neg, level), ...]"""
        return list(self._history)

    def reset(self, new_ref_mean: Optional[float] = None,
              new_ref_std: Optional[float] = None) -> None:
        """
        전략 버전 교체 시 호출 — CUSUM 초기화 및 기준값 갱신.

        Args:
            new_ref_mean: 신규 WFA 기준 일별 PnL 기대값
            new_ref_std:  신규 WFA 기준 일별 PnL 표준편차
        """
        if new_ref_mean is not None:
            self.ref_mean = new_ref_mean
        if new_ref_std is not None:
            self.ref_std = max(new_ref_std, 1.0)
        self._reset()
        logger.info(
            "[DriftDetector] 리셋 — 기준값 μ=%.0f σ=%.0f",
            self.ref_mean, self.ref_std,
        )

    def estimate_ref_from_trades(
        self,
        daily_pnls: List[float],
        wfa_sharpe: Optional[float] = None,
    ) -> None:
        """
        최근 거래 데이터에서 기준값 추정 후 적용.
        WFA Sharpe가 있으면 기대값 스케일링에 활용.

        Args:
            daily_pnls: 일별 PnL 리스트 (원)
            wfa_sharpe: WFA 평균 Sharpe (선택)
        """
        if not daily_pnls:
            return
        n    = len(daily_pnls)
        mean = sum(daily_pnls) / n
        var  = sum((x - mean) ** 2 for x in daily_pnls) / max(n - 1, 1)
        std  = math.sqrt(var)

        # WFA Sharpe 보정: 실제 기대값 ≈ Sharpe × std / sqrt(252)
        if wfa_sharpe is not None and std > 0:
            daily_expected = wfa_sharpe * std / (252 ** 0.5)
            mean = daily_expected

        self.ref_mean = mean
        self.ref_std  = max(std, 1.0)
        logger.info(
            "[DriftDetector] 기준값 추정 완료 — μ=%.0f σ=%.0f (n=%d)",
            self.ref_mean, self.ref_std, n,
        )

    # ─── 내부 헬퍼 ───────────────────────────────────────────────────────
    def _compute_level(self, cusum_neg: float) -> int:
        if cusum_neg >= self.h_crit:
            return DriftLevel.CRITICAL
        elif cusum_neg >= self.h_alarm:
            return DriftLevel.ALARM
        elif cusum_neg >= self.h_watch:
            return DriftLevel.WATCHLIST
        return DriftLevel.CLEAR

    def _build_message(
        self,
        date:      str,
        pnl:       float,
        z:         float,
        cusum_neg: float,
        level:     int,
    ) -> str:
        level_name = DriftLevel.name(level)
        msg = (
            "[DriftDetector] %s | PnL %+.0f원 (Z=%.2f) "
            "CUSUM=%.2f → %s"
        ) % (date, pnl, z, cusum_neg, level_name)

        if level == DriftLevel.WATCHLIST:
            msg += " | 파라미터 재점검 예약 권장"
        elif level == DriftLevel.ALARM:
            msg += " | param_optimizer 즉시 실행 검토"
        elif level == DriftLevel.CRITICAL:
            msg += " | 롤백 또는 사이즈 50% 축소 검토 필요"
        return msg

    def _reset(self) -> None:
        self._cusum_neg        = 0.0
        self._cusum_pos        = 0.0
        self._days_since_reset = 0


# ─────────────────────────────────────────────────────────────────────────
# 멀티 지표 종합 드리프트 감지기
# ─────────────────────────────────────────────────────────────────────────
class MultiMetricDriftDetector:
    """
    PnL 외 Sharpe·승률·Profit Factor를 함께 감시.
    3개 이상 지표가 동시에 WATCHLIST 이상이면 종합 경보 격상.

    Attributes:
        detectors: 지표명 → DriftDetector 매핑
        vote_threshold: 경보 격상에 필요한 최소 동시 경보 수 (기본 2)
    """

    def __init__(self, vote_threshold: int = 2):
        self.vote_threshold = vote_threshold
        self.detectors: dict = {
            "pnl":   DriftDetector(k_slack=0.50, h_watch=2.0, h_alarm=4.0, h_crit=6.0),
            "wr":    DriftDetector(k_slack=0.50, h_watch=2.5, h_alarm=5.0, h_crit=7.0),
            "pf":    DriftDetector(k_slack=0.50, h_watch=2.0, h_alarm=4.5, h_crit=6.5),
        }
        self._last_levels: dict = {k: DriftLevel.CLEAR for k in self.detectors}

    def update(
        self,
        daily_pnl:     float,
        daily_wr:      float,   # 당일 승률 (0~1)
        daily_pf:      float,   # 당일 Profit Factor
    ) -> Tuple[int, str]:
        """
        세 지표 동시 업데이트.

        Returns:
            (종합_DriftLevel, 종합_메시지)
        """
        level_pnl, _, msg_pnl = self.detectors["pnl"].update(daily_pnl)
        # WR/PF는 0~1 스케일이므로 별도 처리
        level_wr,  _, _       = self.detectors["wr"].update(daily_wr)
        level_pf,  _, _       = self.detectors["pf"].update(daily_pf)

        self._last_levels = {
            "pnl": level_pnl, "wr": level_wr, "pf": level_pf,
        }

        # 투표: WATCHLIST 이상 지표 수로 종합 경보 결정
        above_watch = sum(
            1 for lv in self._last_levels.values()
            if lv >= DriftLevel.WATCHLIST
        )
        above_alarm = sum(
            1 for lv in self._last_levels.values()
            if lv >= DriftLevel.ALARM
        )

        if above_alarm >= self.vote_threshold:
            composite = DriftLevel.ALARM
        elif above_watch >= self.vote_threshold:
            composite = DriftLevel.WATCHLIST
        else:
            composite = max(self._last_levels.values())

        levels_str = " | ".join(
            "%s=%s" % (k, DriftLevel.name(v))
            for k, v in self._last_levels.items()
        )
        composite_msg = (
            "[MultiDrift] 종합:%s (%s)"
        ) % (DriftLevel.name(composite), levels_str)

        if composite >= DriftLevel.WATCHLIST:
            logger.warning(composite_msg)
        else:
            logger.debug(composite_msg)

        return composite, composite_msg

    def reset_all(
        self,
        pnl_ref:  Optional[Tuple[float, float]] = None,
        wr_ref:   Optional[Tuple[float, float]] = None,
        pf_ref:   Optional[Tuple[float, float]] = None,
    ) -> None:
        """
        버전 교체 시 전체 리셋.

        Args:
            pnl_ref: (mean, std) 일별 PnL 기준값
            wr_ref:  (mean, std) 일별 승률 기준값
            pf_ref:  (mean, std) 일별 PF 기준값
        """
        def _do_reset(det: DriftDetector, ref: Optional[Tuple[float, float]]) -> None:
            if ref:
                det.reset(new_ref_mean=ref[0], new_ref_std=ref[1])
            else:
                det.reset()

        _do_reset(self.detectors["pnl"], pnl_ref)
        _do_reset(self.detectors["wr"],  wr_ref)
        _do_reset(self.detectors["pf"],  pf_ref)

    def get_levels(self) -> dict:
        """현재 각 지표별 경보 수준 반환."""
        return dict(self._last_levels)


# ─────────────────────────────────────────────────────────────────────────
# 전역 싱글턴
# ─────────────────────────────────────────────────────────────────────────
_detector: Optional[MultiMetricDriftDetector] = None


def get_drift_detector() -> MultiMetricDriftDetector:
    """전역 MultiMetricDriftDetector 싱글턴 반환."""
    global _detector
    if _detector is None:
        _detector = MultiMetricDriftDetector()
    return _detector
