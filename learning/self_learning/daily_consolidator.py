# learning/self_learning/daily_consolidator.py
"""
일일 마감 자가학습 (매크로 수준 회고)

OnlineLearner(분단위 micro 업데이트)를 보완하는 daily 수준 패턴 학습.

역할:
  1. 당일 시간대별 예측 정확도 분석
  2. 저성능 구간(accuracy < PENALTY_THRESHOLD)에 confidence penalty factor 부여
  3. 다음 날 시작 시 MetaGate/체크리스트가 해당 구간 진입 기준을 상향 조정

파일:
  data/self_learning_zone_penalty.json — 구간별 패널티 팩터 (0.0~1.0)
"""
import json
import logging
import datetime
import os
from collections import defaultdict
from typing import Dict, List, Tuple

logger = logging.getLogger("LEARNING")

_DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "zone_penalty.json"
)

# 이 정확도 이하인 구간에 패널티 부여
PENALTY_THRESHOLD   = 0.45
# 패널티 강도 (신뢰도 임계치를 이만큼 상향 — 기본 0.58 + penalty)
PENALTY_STRENGTH    = 0.04
# 연속 N일 저성능 구간만 패널티 적용 (단발 노이즈 무시)
MIN_DAYS_REQUIRED   = 2
# 샘플 최소 수 (샘플이 너무 적으면 통계 무의미)
MIN_SAMPLES_PER_ZONE = 5


class DailyConsolidator:
    """
    일일 마감 시 시간대별 정확도를 분석하고
    저성능 구간에 대한 패널티 팩터를 갱신한다.

    사용 (daily_close() 내부):
        consolidator.record(zone="OPENING", correct=True)
        ...
        consolidator.consolidate()          # 15:40 마감 시 호출
        penalty = consolidator.get_penalty("OPENING")  # 다음 날 적용
    """

    def __init__(self, path: str = _DEFAULT_PATH):
        self._path = os.path.abspath(path)
        # 당일 (zone → [correct: bool]) 누적
        self._today: Dict[str, List[bool]] = defaultdict(list)
        # 누적 이력 (zone → [daily_accuracy, ...], 최근 5일)
        self._history: Dict[str, List[float]] = defaultdict(list)
        # 현재 적용 중인 패널티
        self._penalties: Dict[str, float] = {}
        self._load()

    # ── 분봉 파이프라인에서 호출 ────────────────────────────────
    def record(self, zone: str, correct: bool) -> None:
        """매분 예측 결과를 시간대별로 기록한다."""
        self._today[zone].append(correct)

    # ── 15:40 마감 시 호출 ──────────────────────────────────────
    def consolidate(self) -> Dict[str, float]:
        """
        당일 시간대별 정확도를 집계하고 패널티 팩터를 갱신한다.

        Returns:
            {zone: accuracy} 당일 요약
        """
        today_summary: Dict[str, float] = {}

        for zone, results in self._today.items():
            if len(results) < MIN_SAMPLES_PER_ZONE:
                continue
            acc = sum(results) / len(results)
            today_summary[zone] = round(acc, 4)

            # 이력 갱신 (최근 5일 유지)
            hist = self._history[zone]
            hist.append(acc)
            if len(hist) > 5:
                hist.pop(0)

        # 패널티 갱신
        new_penalties: Dict[str, float] = {}
        for zone, hist in self._history.items():
            if len(hist) < MIN_DAYS_REQUIRED:
                continue
            recent = hist[-MIN_DAYS_REQUIRED:]
            if all(a < PENALTY_THRESHOLD for a in recent):
                # 연속 저성능: confidence 임계치 상향 패널티
                new_penalties[zone] = PENALTY_STRENGTH
                logger.warning(
                    "[Consolidator] 구간 '%s' %d일 연속 정확도 %.0f%% 미만 → 패널티 +%.2f",
                    zone, MIN_DAYS_REQUIRED, PENALTY_THRESHOLD * 100, PENALTY_STRENGTH,
                )
            else:
                new_penalties[zone] = 0.0

        self._penalties = new_penalties
        self._today.clear()
        self._save()

        logger.info(
            "[Consolidator] 마감 집계: %s | 패널티 적용 구간: %s",
            {z: f"{a:.0%}" for z, a in today_summary.items()},
            [z for z, p in new_penalties.items() if p > 0],
        )
        return today_summary

    # ── 다음 날 파이프라인에서 호출 ──────────────────────────────
    def get_penalty(self, zone: str) -> float:
        """
        해당 시간대의 confidence 임계치 추가 상향 폭 반환 (0.0 = 패널티 없음).

        Args:
            zone: 시간대 코드 (예: "OPENING", "LUNCH", "CLOSING")
        Returns:
            추가 confidence 임계치 (기본 min_confidence에 더함)
        """
        return self._penalties.get(zone, 0.0)

    def get_all_penalties(self) -> Dict[str, float]:
        return dict(self._penalties)

    def reset_daily(self) -> None:
        self._today.clear()

    # ── 영속성 ────────────────────────────────────────────────
    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        state = {
            "updated":   datetime.datetime.now().isoformat(),
            "penalties": self._penalties,
            "history":   dict(self._history),
        }
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning("[Consolidator] 저장 실패: %s", e)

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                state = json.load(f)
            self._penalties = state.get("penalties", {})
            self._history   = defaultdict(list, state.get("history", {}))
            logger.info("[Consolidator] 패널티 이력 로드: %s", self._penalties)
        except Exception as e:
            logger.warning("[Consolidator] 로드 실패 (초기화): %s", e)
