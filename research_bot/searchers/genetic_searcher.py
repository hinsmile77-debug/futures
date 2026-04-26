# research_bot/searchers/genetic_searcher.py — 유전 알고리즘 탐색기
"""
GeneticSearcher: 기존 알파 풀에서 교차·돌연변이로 새로운 유전자를 생성.

연산:
  - 선택 (Selection)    : 토너먼트 선택 (k=3)
  - 교차 (Crossover)   : 단일점 교차 (feature_ids 분리점)
  - 돌연변이 (Mutation) : 피처 교체 / 파라미터 조정 / 로직 변경
  - 엘리트 보존         : 상위 20%는 그대로 다음 세대로

다양성 유지:
  - 동일한 feature_ids 조합이 이미 풀에 있으면 추가 돌연변이 적용
  - 세대 내 중복 유전자 허용 안 함
"""
import random
import logging
from typing import List, Optional

from research_bot.alpha_gene import AlphaGene, AVAILABLE_FEATURES, LOGIC_TYPES, CORE_FEATURES
from research_bot.searchers.random_searcher import RandomSearcher, SEARCH_SPACE

logger = logging.getLogger(__name__)

TOURNAMENT_K    = 3
MUTATION_RATE   = 0.25   # 각 유전자 속성의 돌연변이 확률
ELITE_RATIO     = 0.20   # 엘리트 보존 비율
MAX_RETRIES     = 5      # 중복 방지 재시도 횟수


class GeneticSearcher:
    """유전 알고리즘 기반 새로운 알파 생성기."""

    def __init__(self, mutation_rate: float = MUTATION_RATE):
        self.mutation_rate = mutation_rate
        self._random_searcher = RandomSearcher()

    # ── 메인 진화 ─────────────────────────────────────────────────
    def evolve(
        self,
        parents: List[AlphaGene],
        generation: int,
        target_size: int,
        existing_keys: Optional[set] = None,
    ) -> List[AlphaGene]:
        """
        parents를 기반으로 다음 세대 개체군 생성.

        Args:
            parents       : 이전 세대 유전자 (score 순 정렬됨)
            generation    : 현재 세대 번호
            target_size   : 목표 개체 수
            existing_keys : 이미 존재하는 gene key set (중복 방지)

        Returns:
            새 세대 유전자 목록
        """
        if not parents:
            return self._random_searcher.generate_population(target_size, generation)

        existing_keys = existing_keys or set()
        offspring: List[AlphaGene] = []

        # 1. 엘리트 보존
        sorted_parents = sorted(parents, key=lambda g: g.score, reverse=True)
        n_elite        = max(1, int(len(sorted_parents) * ELITE_RATIO))
        for p in sorted_parents[:n_elite]:
            child = AlphaGene.from_dict(p.to_dict())
            child.gene_id   = None  # 새 ID 발급
            child.generation = generation
            child.parent_ids = [p.gene_id]
            child.status     = "candidate"
            # AlphaGene.__init__에서 gene_id를 None으로 받으면 새로 발급됨
            import uuid
            child.gene_id = str(uuid.uuid4())[:8]
            offspring.append(child)

        # 2. 교차 + 돌연변이로 나머지 채우기
        while len(offspring) < target_size:
            if random.random() < 0.7 and len(parents) >= 2:
                # 교차
                p1 = self._tournament_select(sorted_parents)
                p2 = self._tournament_select(sorted_parents)
                child = self._crossover(p1, p2, generation)
            else:
                # 단일 부모 돌연변이
                p1 = self._tournament_select(sorted_parents)
                child = self._mutate(p1, generation)

            # 중복 체크
            key = self._gene_key(child)
            if key in existing_keys:
                child = self._mutate(child, generation, force=True)
                key   = self._gene_key(child)

            existing_keys.add(key)
            offspring.append(child)

        logger.info("GeneticSearcher: gen=%d → %d 개체 생성 (elite=%d)",
                    generation, len(offspring), n_elite)
        return offspring

    # ── 선택 ──────────────────────────────────────────────────────
    def _tournament_select(self, sorted_parents: List[AlphaGene]) -> AlphaGene:
        """토너먼트 선택 (k=TOURNAMENT_K)."""
        pool = random.sample(sorted_parents, min(TOURNAMENT_K, len(sorted_parents)))
        return max(pool, key=lambda g: g.score)

    # ── 교차 ──────────────────────────────────────────────────────
    def _crossover(self, p1: AlphaGene, p2: AlphaGene, generation: int) -> AlphaGene:
        """단일점 교차."""
        import uuid

        # feature_ids 교차
        all_feats = list(set(p1.feature_ids + p2.feature_ids))
        random.shuffle(all_feats)
        n_take = random.randint(1, min(4, len(all_feats)))
        child_feats = all_feats[:n_take]

        # 파라미터는 양 부모에서 랜덤 선택
        child_params = {}
        for k in set(list(p1.params.keys()) + list(p2.params.keys())):
            if k in p1.params and k in p2.params:
                child_params[k] = random.choice([p1.params[k], p2.params[k]])
            elif k in p1.params:
                child_params[k] = p1.params[k]
            else:
                child_params[k] = p2.params[k]

        # 나머지 속성 랜덤 선택
        child = AlphaGene(
            feature_ids     = child_feats,
            params          = child_params,
            logic_type      = random.choice([p1.logic_type, p2.logic_type]),
            direction       = random.choice([p1.direction, p2.direction]),
            hold_bars       = random.choice([p1.hold_bars, p2.hold_bars]),
            entry_threshold = random.choice([p1.entry_threshold, p2.entry_threshold]),
            exit_threshold  = random.choice([p1.exit_threshold, p2.exit_threshold]),
            generation      = generation,
            parent_ids      = [p1.gene_id, p2.gene_id],
        )
        return child

    # ── 돌연변이 ──────────────────────────────────────────────────
    def _mutate(self, parent: AlphaGene, generation: int, force: bool = False) -> AlphaGene:
        """돌연변이 적용."""
        import uuid
        import copy

        child             = AlphaGene.from_dict(parent.to_dict())
        child.gene_id     = str(uuid.uuid4())[:8]
        child.generation  = generation
        child.parent_ids  = [parent.gene_id]
        child.status      = "candidate"
        child.score       = 0.0

        rate = 1.0 if force else self.mutation_rate

        # 피처 돌연변이
        if random.random() < rate:
            mut_type = random.choice(["add", "remove", "replace"])
            feats    = list(child.feature_ids)

            if mut_type == "add" and len(feats) < 5:
                available = [f for f in AVAILABLE_FEATURES if f not in feats]
                if available:
                    feats.append(random.choice(available))

            elif mut_type == "remove" and len(feats) > 1:
                # CORE 피처는 제거 안 함
                non_core = [f for f in feats if f not in CORE_FEATURES]
                if non_core:
                    feats.remove(random.choice(non_core))

            elif mut_type == "replace":
                available = [f for f in AVAILABLE_FEATURES if f not in feats]
                if available and feats:
                    non_core = [f for f in feats if f not in CORE_FEATURES]
                    if non_core:
                        feats.remove(random.choice(non_core))
                        feats.append(random.choice(available))

            child.feature_ids = feats

        # 로직 타입 돌연변이
        if random.random() < rate:
            child.logic_type = random.choice(LOGIC_TYPES)

        # 파라미터 돌연변이
        if random.random() < rate and "vwap_window" in child.params:
            child.params["vwap_window"] = random.choice(SEARCH_SPACE["vwap_window"])
        if random.random() < rate and "atr_window" in child.params:
            child.params["atr_window"] = random.choice(SEARCH_SPACE["atr_window"])

        # 홀딩 기간 돌연변이
        if random.random() < rate:
            child.hold_bars = max(1, min(15, child.hold_bars + random.choice([-2, -1, 1, 2])))

        # 임계값 돌연변이
        if random.random() < rate:
            child.entry_threshold = round(
                max(0.05, child.entry_threshold + random.uniform(-0.3, 0.3)), 3
            )

        # 방향 돌연변이
        if random.random() < rate * 0.3:
            child.direction = random.choice(SEARCH_SPACE["direction"])

        return child

    # ── 유틸 ──────────────────────────────────────────────────────
    @staticmethod
    def _gene_key(gene: AlphaGene) -> str:
        """중복 체크용 키 (피처 + 로직 + 홀딩)."""
        feats = tuple(sorted(gene.feature_ids))
        return f"{feats}|{gene.logic_type}|{gene.hold_bars}|{gene.direction}"
