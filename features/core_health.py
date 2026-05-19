# features/core_health.py — CORE 3종 피처 건강 점수 [5순위]
"""
CORE 3종(CVD·VWAP·OFI) 실시간 건강 점수 (0~100).

점수 → 사이즈 배수:
  < 70  → 0.0  (진입 금지 — 엔진 경고등 켜진 채 액셀 금지)
  70~85 → 0.5  (절반 사이즈)
  ≥ 85  → 1.0  (정상 사이즈)

점수 계산 항목:
  ① 연속 실패 없음(streak=0): 각 피처당 25점 (3종 × 25 = 75점 기본)
  ② z-score 경고 없음:         10점
  ③ 최근 5분 실패율 0%:        15점 (롤링 에러 비율 기반)
"""
import logging
from collections import deque
from typing import Dict

logger = logging.getLogger("SYSTEM")

_SCORE_STREAK_OK   = 25   # 피처 하나가 연속 실패 없을 때 점수 (3개 → 75점)
_SCORE_ZSCORE_OK   = 10   # z-score 경고 0개일 때 점수
_SCORE_RECENT_OK   = 15   # 최근 5분 실패율 0%일 때 점수
_PENALTY_PER_FAIL  = 5    # streak 1회당 점수 패널티 (최대 15점 차감)
_WINDOW_RECENT     = 5    # 최근 n분 실패율 추적 창


class CoreHealthScore:
    """
    CORE 피처 3종 건강 점수 실시간 계산기.
    PositionSizer.compute() 호출 전에 health_size_mult를 주입한다.
    """

    def __init__(self):
        self._streak: Dict[str, int] = {"cvd": 0, "vwap": 0, "ofi": 0}
        self._z_warn_count: int = 0
        self._recent_fails: deque = deque(maxlen=_WINDOW_RECENT)  # (cvd_ok, vwap_ok, ofi_ok)
        self._score: int = 100
        self._size_mult: float = 1.0

    # ── 외부 업데이트 API ─────────────────────────────────────────

    def update(
        self,
        cvd_streak: int,
        vwap_streak: int,
        ofi_streak: int,
        z_warn_count: int = 0,
    ) -> None:
        """
        매분 파이프라인 STEP 4 직후 호출.

        Args:
            cvd_streak:   CVD 연속 실패 횟수 (0 = 정상)
            vwap_streak:  VWAP 연속 실패 횟수
            ofi_streak:   OFI 연속 실패 횟수
            z_warn_count: 해당 봉에서 극단 z-score 경고가 발생한 피처 수
        """
        self._streak = {"cvd": cvd_streak, "vwap": vwap_streak, "ofi": ofi_streak}
        self._z_warn_count = z_warn_count
        self._recent_fails.append((cvd_streak > 0, vwap_streak > 0, ofi_streak > 0))
        self._recompute()

    # ── 점수 계산 ─────────────────────────────────────────────────

    def _recompute(self) -> None:
        score = 0

        # ① streak 점수: 정상이면 25점, 실패 1회당 5점 차감 (최저 0점)
        for name in ("cvd", "vwap", "ofi"):
            streak = self._streak.get(name, 0)
            pts = max(0, _SCORE_STREAK_OK - streak * _PENALTY_PER_FAIL)
            score += pts

        # ② z-score 점수: 0개이면 10점, 1개 이상이면 0점
        if self._z_warn_count == 0:
            score += _SCORE_ZSCORE_OK

        # ③ 최근 5분 실패율: 완전 정상(실패 없음)이면 15점
        if self._recent_fails:
            total_fails = sum(any(row) for row in self._recent_fails)
            if total_fails == 0:
                score += _SCORE_RECENT_OK

        self._score = min(100, max(0, score))

        if self._score < 70:
            self._size_mult = 0.0
        elif self._score < 85:
            self._size_mult = 0.5
        else:
            self._size_mult = 1.0

        if self._size_mult < 1.0:
            logger.warning(
                "[CoreHealth] 점수=%d → 사이즈 배수=%.1f | streak cvd=%d vwap=%d ofi=%d z_warn=%d",
                self._score, self._size_mult,
                self._streak["cvd"], self._streak["vwap"], self._streak["ofi"],
                self._z_warn_count,
            )

    # ── 공개 속성 ─────────────────────────────────────────────────

    @property
    def score(self) -> int:
        return self._score

    @property
    def size_mult(self) -> float:
        """PositionSizer에 전달할 CORE 건강 배수 (0.0 / 0.5 / 1.0)."""
        return self._size_mult

    def is_entry_allowed(self) -> bool:
        """점수 < 70이면 A/B 등급도 진입 금지."""
        return self._size_mult > 0.0

    def reset_daily(self) -> None:
        self._streak = {"cvd": 0, "vwap": 0, "ofi": 0}
        self._z_warn_count = 0
        self._recent_fails.clear()
        self._score = 100
        self._size_mult = 1.0

    def status_dict(self) -> dict:
        return {
            "score":       self._score,
            "size_mult":   self._size_mult,
            "cvd_streak":  self._streak["cvd"],
            "vwap_streak": self._streak["vwap"],
            "ofi_streak":  self._streak["ofi"],
            "z_warn":      self._z_warn_count,
        }
