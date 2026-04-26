# research_bot/searchers/random_searcher.py — 랜덤 알파 시드 생성기
"""
RandomSearcher: 탐색 공간에서 무작위로 AlphaGene을 생성.

역할:
  - 1세대 초기 개체군 생성 (population seeding)
  - 유전 다양성 유지를 위해 매 세대 일부 신규 랜덤 개체 보충
  - 파라미터 범위는 SEARCH_SPACE 에서 정의
"""
import random
import logging
from typing import List

from research_bot.alpha_gene import AlphaGene, AVAILABLE_FEATURES, LOGIC_TYPES, CORE_FEATURES

logger = logging.getLogger(__name__)

# ── 탐색 공간 정의 ─────────────────────────────────────────────────
SEARCH_SPACE = {
    "n_features":        (1, 4),        # 피처 개수 범위
    "hold_bars":         (1, 15),       # 홀딩 기간
    "entry_threshold":   (0.1, 2.0),    # 진입 임계값
    "exit_threshold":    (-1.0, 0.5),   # 청산 임계값
    "vwap_window":       [5, 10, 20, 30, 60],
    "atr_window":        [7, 14, 21],
    "direction":         [1, -1, 0],    # 1=롱전용, -1=숏전용, 0=양방향
}



class RandomSearcher:
    """무작위 AlphaGene 생성기."""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)

    def generate(self, generation: int = 0) -> AlphaGene:
        """랜덤 유전자 하나 생성."""
        n_feats = random.randint(*SEARCH_SPACE["n_features"])

        # CORE 피처 1개 반드시 포함 (50% 확률)
        feature_ids = []
        if random.random() < 0.5:
            feature_ids.append(random.choice(CORE_FEATURES))

        # 나머지 피처 랜덤 선택 (중복 제거)
        pool = [f for f in AVAILABLE_FEATURES if f not in feature_ids]
        extra = random.sample(pool, min(n_feats - len(feature_ids), len(pool)))
        feature_ids.extend(extra)

        if not feature_ids:
            feature_ids = [random.choice(AVAILABLE_FEATURES)]

        # 파라미터
        params = {
            "vwap_window": random.choice(SEARCH_SPACE["vwap_window"]),
            "atr_window":  random.choice(SEARCH_SPACE["atr_window"]),
        }

        logic_type      = random.choice(LOGIC_TYPES)
        direction       = random.choice(SEARCH_SPACE["direction"])
        hold_bars       = random.randint(*SEARCH_SPACE["hold_bars"])
        entry_threshold = round(random.uniform(*SEARCH_SPACE["entry_threshold"]), 3)
        exit_threshold  = round(random.uniform(*SEARCH_SPACE["exit_threshold"]), 3)

        gene = AlphaGene(
            feature_ids     = feature_ids,
            params          = params,
            logic_type      = logic_type,
            direction       = direction,
            hold_bars       = hold_bars,
            entry_threshold = entry_threshold,
            exit_threshold  = exit_threshold,
            generation      = generation,
        )
        logger.debug("RandomSearcher → %s", gene)
        return gene

    def generate_population(self, size: int, generation: int = 0) -> List[AlphaGene]:
        """초기 개체군 생성."""
        pop = [self.generate(generation) for _ in range(size)]
        logger.info("RandomSearcher: %d 개 초기 개체 생성 (gen=%d)", size, generation)
        return pop
