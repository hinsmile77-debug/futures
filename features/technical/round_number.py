# features/technical/round_number.py — 마디가(Round Number) 필터 ⭐v7.0
"""
KOSPI 200 선물 한국 시장 특화 마디가 필터

심리적 저항/지지가 형성되는 2.5pt·5pt 단위 라운드 넘버를 감지.
목표가까지 경로에 마디가가 많으면 헛 진입 위험이 높다.

v7.0 Gemini 제안:
  진입~목표가 사이 마디가 2개↑ → 진입 차단
  마디가 1개       → 등급 하향 (A→B)
  마디가 0개       → 정상 진입

KOSPI 200 기준:
  2.5pt 단위: 387.5, 390.0, 392.5, 395.0, ...
  5.0pt 단위: 385.0, 390.0, 395.0, 400.0, ...  (심리적 저항 더 강함)

기대 효과: 헛 진입 -15%
"""
import numpy as np
from typing import List, Optional


# KOSPI 200 선물 마디가 간격
ROUND_INTERVALS = [5.0, 2.5]   # 강도 순: 5pt > 2.5pt


def find_round_numbers_in_range(
    entry_price: float,
    target_price: float,
    intervals: List[float] = None,
) -> dict:
    """
    진입가 ~ 목표가 사이 마디가 목록 반환

    Args:
        entry_price:  현재 진입가
        target_price: 목표 청산가
        intervals:    마디가 간격 리스트 (기본: [5.0, 2.5])

    Returns:
        {round_numbers, count_5pt, count_2pt5, total_count,
         block_entry, grade_penalty, reason}
    """
    if intervals is None:
        intervals = ROUND_INTERVALS

    lo = min(entry_price, target_price)
    hi = max(entry_price, target_price)

    # 5pt 마디가
    rounds_5pt  = _collect_levels(lo, hi, 5.0)
    # 2.5pt 마디가 (5pt 제외한 중간 마디)
    rounds_2pt5 = [r for r in _collect_levels(lo, hi, 2.5) if r not in rounds_5pt]

    # 진입가·목표가 자체는 제외 (도달한 곳은 저항 아님)
    rounds_5pt  = [r for r in rounds_5pt  if abs(r - entry_price) > 0.1 and abs(r - target_price) > 0.1]
    rounds_2pt5 = [r for r in rounds_2pt5 if abs(r - entry_price) > 0.1 and abs(r - target_price) > 0.1]

    all_rounds    = sorted(set(rounds_5pt + rounds_2pt5))
    total_count   = len(all_rounds)
    # 5pt 마디가 2개 이상이면 훨씬 강한 차단 조건
    strong_count  = len(rounds_5pt)

    block_entry   = False
    grade_penalty = 0   # 등급 하향 단계 수
    reason        = ""

    if strong_count >= 2:
        block_entry = True
        reason      = f"5pt 마디가 {strong_count}개 → 진입 차단 (강한 저항)"
    elif total_count >= 2:
        block_entry = True
        reason      = f"마디가 {total_count}개 → 진입 차단"
    elif total_count == 1:
        grade_penalty = 1
        reason        = f"마디가 {all_rounds[0]:.1f}pt 1개 → 등급 하향 (A→B)"
    else:
        reason = "마디가 없음 — 정상 진입"

    return {
        "round_numbers":  all_rounds,
        "count_5pt":      len(rounds_5pt),
        "count_2pt5":     len(rounds_2pt5),
        "total_count":    total_count,
        "block_entry":    block_entry,
        "grade_penalty":  grade_penalty,   # 1 = 등급 1단계 하향
        "reason":         reason,
    }


def _collect_levels(lo: float, hi: float, interval: float) -> List[float]:
    """lo~hi 사이 interval 배수 목록"""
    start = np.ceil(lo / interval) * interval
    levels = []
    val = start
    while val <= hi + 1e-6:
        levels.append(round(val, 2))
        val += interval
    return levels


def nearest_round_distance(price: float, direction: int) -> dict:
    """
    현재가 기준 다음 마디가까지의 거리

    Args:
        price:     현재가
        direction: +1 (위) / -1 (아래)

    Returns:
        {level_5pt, dist_5pt, level_2pt5, dist_2pt5}
    """
    if direction == 1:
        lv5   = np.ceil(price / 5.0) * 5.0
        lv2p5 = np.ceil(price / 2.5) * 2.5
    else:
        lv5   = np.floor(price / 5.0) * 5.0
        lv2p5 = np.floor(price / 2.5) * 2.5

    # 현재가와 동일한 레벨은 다음 레벨로
    if abs(lv5 - price) < 0.01:
        lv5   += direction * 5.0
    if abs(lv2p5 - price) < 0.01:
        lv2p5 += direction * 2.5

    return {
        "level_5pt":   round(float(lv5), 2),
        "dist_5pt":    round(abs(float(lv5) - price), 2),
        "level_2pt5":  round(float(lv2p5), 2),
        "dist_2pt5":   round(abs(float(lv2p5) - price), 2),
    }


def nearest_round_distance_symmetric(price: float, intervals: List[float] = None) -> float:
    """
    현재가에서 가장 가까운 마디가까지의 거리(포인트, 방향 무관) — GBM 피처용 ⭐320차대.

    `nearest_round_distance()`는 direction 인자가 필요한데, 피처 생성 시점엔 아직 예측
    방향·목표가가 정해지지 않아(닭-달걀 문제) 그대로 쓸 수 없다. 이 함수는 방향 인자 없이
    상/하 양쪽 최근접 레벨을 모두 확인해 더 가까운 쪽의 거리만 반환한다.

    Args:
        price:     현재가
        intervals: 마디가 간격 리스트 (기본: ROUND_INTERVALS = [5.0, 2.5])

    Returns:
        가장 가까운 마디가까지의 거리(포인트, 0 이상). intervals 중 가장 촘촘한 간격의
        절반이 이론적 상한(기본 2.5pt 간격 기준 최대 1.25pt).
    """
    if intervals is None:
        intervals = ROUND_INTERVALS
    if price <= 0:
        return 0.0

    dists = []
    for itv in intervals:
        lower = np.floor(price / itv) * itv
        upper = np.ceil(price / itv) * itv
        dists.append(min(abs(price - lower), abs(price - upper)))

    return float(round(min(dists), 4))


if __name__ == "__main__":
    # 마디가 2개 있는 구간
    r = find_round_numbers_in_range(entry_price=391.3, target_price=395.8)
    print(f"마디가: {r['round_numbers']} | count={r['total_count']} | block={r['block_entry']} | {r['reason']}")

    # 마디가 1개 구간
    r = find_round_numbers_in_range(entry_price=390.5, target_price=392.3)
    print(f"마디가: {r['round_numbers']} | count={r['total_count']} | penalty={r['grade_penalty']} | {r['reason']}")

    # 마디가 없는 구간
    r = find_round_numbers_in_range(entry_price=390.1, target_price=391.2)
    print(f"마디가: {r['round_numbers']} | block={r['block_entry']} | {r['reason']}")

    # 다음 마디가 거리
    d = nearest_round_distance(price=391.3, direction=1)
    print(f"위 방향 — 5pt 마디: {d['level_5pt']} (거리 {d['dist_5pt']}pt), 2.5pt: {d['level_2pt5']} (거리 {d['dist_2pt5']}pt)")

    # 방향 무관 최근접 마디가 거리 (GBM 피처용)
    for p in (391.3, 390.0, 392.5):
        print(f"price={p} -> round_number_distance={nearest_round_distance_symmetric(p):.4f}pt")
