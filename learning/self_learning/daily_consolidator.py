# learning/self_learning/daily_consolidator.py
"""
일일 마감 자가학습 (매크로 수준 회고)

OnlineLearner(분단위 micro 업데이트)를 보완하는 daily 수준 패턴 학습.

역할:
  1. 당일 시간대별 예측 정확도·기대손익(realized_move) 분석
  2. 저성능 구간(최근 풀링 기대손익 CI 상단 < 0)에 confidence penalty factor 부여
  3. 다음 날 시작 시 MetaGate/체크리스트가 해당 구간 진입 기준을 상향 조정

파일:
  data/self_learning_zone_penalty.json — 구간별 패널티 팩터 (0.0~1.0)

[311차 후속3] 개선 이력 (`dev_memory/NEXT_TODO.md` 311차 후속3 참조):
  - 좀비 패널티 차단: 표본 미달일은 이력에 None을 마킹해 낡은 데이터로 판정이
    계속 성립하는 것을 방지 (풀링 창에서 자연 소멸).
  - 판정 기준: 2클래스 발상 accuracy 임계값(구 PENALTY_THRESHOLD=0.45) 대신
    방향예측만(FLAT 제외, CB③과 동일 필터) 집계 + realized_move(pt) 기대손익
    신뢰구간 상단이 0 미만인지로 전환 — "정확도"는 로그 표시용으로만 유지.
  - 일단위 판정 → 최근 며칠 풀링(POOL_WINDOW_DAYS) + Wilson/정규근사 신뢰구간.
  - 표본 확충: 대표 호라이즌을 5m 단독 → 3m+5m 합산(main.py 배선)으로 확대.
    1m은 후속6 딥다이브에서 유의한 역스킬(acc 47.75%, p=0.0048)이 확정돼 제외.

주의: get_penalty()/get_all_penalties()는 현재 어떤 파이프라인 코드도 소비하지
않음 — 다음 날 진입 기준에 실제로 반영하려면 별도 배선이 필요(미착수).
"""
import json
import logging
import datetime
import os
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("LEARNING")

_DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "zone_penalty.json"
)

# 패널티 강도 (신뢰도 임계치를 이만큼 상향 — 기본 0.58 + penalty)
PENALTY_STRENGTH     = 0.04
# 하루 최소 표본 수 (미달 시 그날은 이력에 None 마킹 — 좀비 패널티 방지)
MIN_SAMPLES_PER_ZONE = 5
# 풀링 대상 최근 일수 (창 크기)
POOL_WINDOW_DAYS     = 5
# 풀링 판정에 필요한 최소 유효(표본충분) 일수
POOL_MIN_DAYS        = 3
# 신뢰구간 z값 (양측 95%, norm.ppf(0.975))
_Z95 = 1.959964

# 하루 집계 스냅샷: n=표본수, wins=정답수(로그용), sum/sumsq=realized_move 합/제곱합
_DaySnapshot = Dict[str, float]


def _mean_upper_bound(total: float, sumsq: float, n: int, z: float = _Z95) -> float:
    """표본평균(realized_move, pt 단위)의 신뢰구간 상단 (정규근사)."""
    if n <= 1:
        return float("inf")  # 표본 부족 → 판정 보류(항상 패널티 미적용)
    mean = total / n
    var = max(sumsq / n - mean * mean, 0.0)
    se = (var / n) ** 0.5
    return mean + z * se


class DailyConsolidator:
    """
    일일 마감 시 시간대별 정확도·기대손익을 분석하고
    저성능 구간에 대한 패널티 팩터를 갱신한다.

    사용 (daily_close() 내부):
        consolidator.record(zone="OPENING", correct=True, predicted_dir=1,
                             realized_move=0.35)
        ...
        consolidator.consolidate()          # 15:40 마감 시 호출
        penalty = consolidator.get_penalty("OPENING")  # 다음 날 적용
    """

    def __init__(self, path: str = _DEFAULT_PATH):
        self._path = os.path.abspath(path)
        # 당일 (zone → [(correct, realized_move), ...]) 누적
        self._today: Dict[str, List[Tuple[bool, float]]] = defaultdict(list)
        # 누적 이력 (zone → [일별 스냅샷 dict | None(표본미달), ...], 최근 POOL_WINDOW_DAYS일)
        self._history: Dict[str, List[Optional[_DaySnapshot]]] = defaultdict(list)
        # 현재 적용 중인 패널티
        self._penalties: Dict[str, float] = {}
        self._load()

    # ── 분봉 파이프라인에서 호출 ────────────────────────────────
    def record(self, zone: str, correct: bool, predicted_dir: Optional[int] = None,
               realized_move: float = 0.0) -> None:
        """매분 예측 결과를 시간대별로 기록한다.

        predicted_dir: 예측 방향(1/-1/0). 0(FLAT)은 집계 제외 — CB③과 동일하게
            방향예측만 필터링해 "3클래스 acc vs 2클래스 임계" 불일치를 해소한다.
        realized_move: meta_labels.realized_move (pt, 방향부호 반영). 패널티
            판정은 이 값의 기대손익 기준으로 이뤄진다.
        """
        if predicted_dir == 0:
            return
        self._today[zone].append((bool(correct), float(realized_move)))

    # ── 15:40 마감 시 호출 ──────────────────────────────────────
    def consolidate(self) -> Dict[str, float]:
        """
        당일 시간대별 정확도를 집계하고, 최근 풀링 기대손익 기준으로 패널티
        팩터를 갱신한다.

        Returns:
            {zone: accuracy} 당일 요약 (참고용 — 판정 기준은 realized_move)
        """
        today_summary: Dict[str, float] = {}

        zones = set(self._today.keys()) | set(self._history.keys())
        for zone in zones:
            results = self._today.get(zone, [])
            hist = self._history[zone]

            if len(results) >= MIN_SAMPLES_PER_ZONE:
                n = len(results)
                wins = sum(1 for c, _ in results if c)
                moves = [m for _, m in results]
                sum_move = sum(moves)
                sumsq_move = sum(m * m for m in moves)
                today_summary[zone] = round(wins / n, 4)
                hist.append({
                    "n": n, "wins": wins, "sum": sum_move, "sumsq": sumsq_move,
                })
            else:
                # 표본 미달(0건 포함) — 좀비 패널티 방지: 갱신 없음을 명시적으로 마킹.
                # 풀링 시 valid 판정에서 제외되므로, 표본 미달이 이어지면 오래된
                # 이력만으로 패널티가 무한정 유지되는 문제가 자연 해소된다.
                hist.append(None)

            if len(hist) > POOL_WINDOW_DAYS:
                hist.pop(0)

        # 패널티 갱신 — 최근 POOL_WINDOW_DAYS일 중 유효(표본충분)일을 풀링
        new_penalties: Dict[str, float] = {}
        for zone, hist in self._history.items():
            valid = [h for h in hist if h is not None]
            if len(valid) < POOL_MIN_DAYS:
                new_penalties[zone] = 0.0
                continue

            pooled_n     = sum(h["n"] for h in valid)
            pooled_wins  = sum(h["wins"] for h in valid)
            pooled_sum   = sum(h["sum"] for h in valid)
            pooled_sumsq = sum(h["sumsq"] for h in valid)
            move_ci_upper = _mean_upper_bound(pooled_sum, pooled_sumsq, pooled_n)

            if move_ci_upper < 0.0:
                new_penalties[zone] = PENALTY_STRENGTH
                logger.warning(
                    "[Consolidator] 구간 '%s' 최근 %d일 풀링(n=%d) 기대손익 "
                    "%.3fpt (CI상단 %.3fpt) < 0 → 패널티 +%.2f (참고 정확도 %.1f%%)",
                    zone, len(valid), pooled_n, pooled_sum / pooled_n,
                    move_ci_upper, PENALTY_STRENGTH, pooled_wins / pooled_n * 100,
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
            raw_history = state.get("history", {})
            # [311차 후속3] 구 포맷(zone → [accuracy_float, ...])은 스냅샷 dict가
            # 아니라 재구성 불가 — 폐기하고 풀링을 새로 시작한다(좀비 이력 방지).
            history: Dict[str, List[Optional[_DaySnapshot]]] = defaultdict(list)
            _migrated = 0
            for zone, entries in raw_history.items():
                if entries and not isinstance(entries[0], dict):
                    _migrated += 1
                    continue
                history[zone] = entries
            self._history = history
            if _migrated:
                logger.info(
                    "[Consolidator] 구 포맷 이력 %d개 구간 폐기(풀링 새로 시작)",
                    _migrated,
                )
            logger.info("[Consolidator] 패널티 이력 로드: %s", self._penalties)
        except Exception as e:
            logger.warning("[Consolidator] 로드 실패 (초기화): %s", e)
