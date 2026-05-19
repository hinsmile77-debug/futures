# safety/market_dna.py — 장 시작 5분 DNA 진단 [4순위]
"""
09:00~09:05 첫 5개 봉으로 "오늘의 장 DNA"를 진단한다.

진단 항목 4가지:
  ① 첫 3봉 방향 일치율  (2/3 이하 → 혼조)
  ② 첫 1분봉 거래량 vs 20일 평균  (150% 초과 → 급등락 가능성)
  ③ z-score 경고 누적 피처 수  (2개 이상 → 스케일러 불신)
  ④ CORE 피처 3개 정상 작동 수  (1개 이하 → 당일 관망 검토)

4개 중 3개 이상 이상 → "조심의 날" 선언:
  - 신규 진입 사이즈 25% (size_mult = 0.25)
  - CB③ 측정만, 자동 진입 최소화
"""
import logging
from collections import deque
from typing import Optional

from logging_system.log_manager import log_manager

logger = logging.getLogger("SYSTEM")

_DNA_BARS         = 5      # 진단에 사용할 봉 수
_CAUTION_THRESH   = 3      # 이상 항목 수 임계값 (이 이상이면 조심의 날)
_VOLUME_SPIKE_PCT = 1.50   # 거래량 스파이크 기준 (20일 평균 대비 배수)
_ZSCORE_WARN      = 2      # z-score 경고 누적 피처 수 기준
_CORE_FAIL_MIN    = 2      # 정상 CORE 피처 수 최소 기준 (이 미만이면 이상)


class MarketDNA:
    """
    장 시작 5분 DNA 진단기.

    매분 파이프라인에서 add_bar() 호출 → 5봉 수집 후 diagnose() 가능.
    당일 09:05 이후 diagnose()를 한 번 호출하면 결과 캐싱.
    """

    def __init__(self, avg_volume_20d: float = 0.0):
        """
        Args:
            avg_volume_20d: 20일 평균 1분봉 거래량 (0이면 거래량 체크 스킵)
        """
        self._avg_volume_20d = float(avg_volume_20d)
        self._bars: deque = deque(maxlen=_DNA_BARS)   # (direction, volume, z_warn, core_ok)
        self._result: Optional[dict] = None           # 진단 결과 캐시

    def set_avg_volume(self, avg_volume_20d: float) -> None:
        """20일 평균 거래량 업데이트 (08:55 매크로 수집 시점에 주입)."""
        self._avg_volume_20d = float(avg_volume_20d)

    def add_bar(
        self,
        direction: int,
        volume: float,
        z_score_warn_count: int,
        core_ok_count: int,
    ) -> None:
        """
        매분 파이프라인에서 호출. 최대 5봉까지 누적.

        Args:
            direction:          해당 봉 방향 (+1 LONG / -1 SHORT / 0 FLAT)
            volume:             해당 봉 거래량
            z_score_warn_count: 해당 봉에서 경고가 발생한 피처 수
            core_ok_count:      CORE 3종 중 정상 작동한 피처 수 (0~3)
        """
        if self._result is not None:
            return
        self._bars.append((direction, volume, z_score_warn_count, core_ok_count))

    def is_ready(self) -> bool:
        """5봉 수집 완료 여부."""
        return len(self._bars) >= _DNA_BARS

    def diagnose(self) -> dict:
        """
        5봉 누적 후 진단 실행. 이후 캐싱.

        Returns:
            {
              "caution":   bool,   # True = 조심의 날
              "size_mult": float,  # 0.25 (조심) or 1.0 (정상)
              "score":     int,    # 이상 항목 수 (0~4)
              "checks":    dict,   # 항목별 통과/실패
              "reason":    str,    # 조심 사유 요약
            }
        """
        if self._result is not None:
            return self._result

        bars = list(self._bars)
        if not bars:
            return {"caution": False, "size_mult": 1.0, "score": 0,
                    "checks": {}, "reason": "데이터 없음"}

        checks = {}

        # ① 첫 3봉 방향 일치율
        dirs = [b[0] for b in bars[:3]]
        nonzero = [d for d in dirs if d != 0]
        if len(nonzero) >= 2:
            majority = max(set(nonzero), key=nonzero.count)
            agree_cnt = nonzero.count(majority)
            checks["direction_agree"] = agree_cnt >= 2   # 2/3 이상 일치
        else:
            checks["direction_agree"] = True  # 데이터 부족 → 패스

        # ② 첫 1분봉 거래량 vs 20일 평균
        first_vol = bars[0][1] if bars else 0.0
        if self._avg_volume_20d > 0:
            vol_ratio = first_vol / self._avg_volume_20d
            checks["volume_normal"] = vol_ratio < _VOLUME_SPIKE_PCT
        else:
            checks["volume_normal"] = True  # 평균 없으면 패스

        # ③ z-score 경고 누적 피처 수 (5봉 합산)
        total_z_warn = sum(b[2] for b in bars)
        checks["zscore_stable"] = total_z_warn < _ZSCORE_WARN

        # ④ CORE 피처 정상 작동 수 (5봉 평균)
        avg_core_ok = sum(b[3] for b in bars) / len(bars)
        checks["core_healthy"] = avg_core_ok >= _CORE_FAIL_MIN

        # 이상 항목 수
        abnormal = [k for k, ok in checks.items() if not ok]
        score    = len(abnormal)
        caution  = score >= _CAUTION_THRESH

        reason_parts = []
        if not checks["direction_agree"]:
            reason_parts.append("방향 혼조")
        if not checks["volume_normal"]:
            reason_parts.append("거래량 급등")
        if not checks["zscore_stable"]:
            reason_parts.append("z-score 불안정")
        if not checks["core_healthy"]:
            reason_parts.append("CORE 피처 붕괴")
        reason = " | ".join(reason_parts) if reason_parts else "정상"

        self._result = {
            "caution":   caution,
            "size_mult": 0.25 if caution else 1.0,
            "score":     score,
            "checks":    checks,
            "reason":    reason,
        }

        level = "WARNING" if caution else "INFO"
        msg = (
            f"[MarketDNA] 장초반 DNA 진단 완료 | "
            f"{'⚠ 조심의 날' if caution else '정상'} | "
            f"이상 {score}/4 | {reason}"
        )
        logger.warning(msg) if caution else logger.info(msg)
        log_manager.system(msg, level)

        return self._result

    def reset_daily(self) -> None:
        """다음 거래일을 위한 리셋."""
        self._bars.clear()
        self._result = None

    def status_dict(self) -> dict:
        """대시보드 표시용 현재 상태."""
        res = self._result or {}
        return {
            "bars_collected": len(self._bars),
            "ready":          self.is_ready(),
            "caution":        res.get("caution", False),
            "size_mult":      res.get("size_mult", 1.0),
            "score":          res.get("score", 0),
            "checks":         res.get("checks", {}),
            "reason":         res.get("reason", "진단 전"),
        }
