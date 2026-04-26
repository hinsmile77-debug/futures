# research_bot/evolution_engine.py — 진화 엔진
"""
EvolutionEngine: 세대(generation) 단위 알파 진화 루프.

한 세대 흐름:
  1. RandomSearcher로 신규 시드 생성 (population의 30%)
  2. GeneticSearcher로 기존 active 기반 자손 생성 (70%)
  3. AlphaEvaluator로 각 후보 평가
  4. PASS 후보를 AlphaPool에 승격 시도
  5. 세대 통계 기록

파라미터:
  POP_SIZE      : 세대당 총 평가 후보 수 (기본 30)
  SEED_RATIO    : 랜덤 신규 비율 (기본 0.30)
  MAX_GENS      : 세대 수 상한 (기본 무제한)
  TIME_BUDGET_S : 한 세대 최대 시간 (초, 기본 3600)
"""
import time
import logging
from typing import List, Optional

from research_bot.alpha_gene import AlphaGene
from research_bot.alpha_pool import AlphaPool
from research_bot.evaluators.alpha_evaluator import AlphaEvaluator
from research_bot.searchers.random_searcher import RandomSearcher
from research_bot.searchers.genetic_searcher import GeneticSearcher

logger = logging.getLogger(__name__)

POP_SIZE        = 30
SEED_RATIO      = 0.30
TIME_BUDGET_S   = 3600   # 1시간


class EvolutionEngine:
    """세대 기반 알파 진화 엔진."""

    def __init__(
        self,
        pool: AlphaPool,
        pop_size: int = POP_SIZE,
        seed_ratio: float = SEED_RATIO,
        time_budget_s: float = TIME_BUDGET_S,
    ):
        self.pool          = pool
        self.pop_size      = pop_size
        self.seed_ratio    = seed_ratio
        self.time_budget_s = time_budget_s

        self.evaluator      = AlphaEvaluator()
        self.random_searcher = RandomSearcher()
        self.genetic_searcher = GeneticSearcher()

        self.generation     = 0
        self.history: List[dict] = []   # 세대별 통계 이력

    # ── 단일 세대 실행 ─────────────────────────────────────────────
    def run_generation(
        self,
        candles: List[dict],
        feature_matrix: Optional[dict] = None,
    ) -> dict:
        """
        한 세대 진화 실행.

        Args:
            candles        : 역사 1분봉 데이터
            feature_matrix : 사전 계산된 피처 행렬 (없으면 candles에서 추출)

        Returns:
            세대 통계 dict
        """
        gen_start  = time.time()
        self.generation += 1
        gen        = self.generation

        logger.info("=== 세대 %d 시작 ===", gen)

        # 1. 후보 생성
        candidates = self._create_candidates(gen)
        logger.info("세대 %d: %d 개 후보 생성", gen, len(candidates))

        # 2. 평가
        n_pass  = 0
        n_fail  = 0
        promoted = []

        existing_keys = {
            self.genetic_searcher._gene_key(g)
            for g in self.pool.actives + self.pool.candidates
        }

        for i, gene in enumerate(candidates):
            # 시간 예산 초과 시 중단
            elapsed = time.time() - gen_start
            if elapsed > self.time_budget_s:
                logger.warning("세대 %d: 시간 예산 초과 (%.0fs) — %d/%d 평가 완료",
                               gen, elapsed, i, len(candidates))
                break

            passed = self.evaluator.evaluate(gene, candles, feature_matrix)

            if passed:
                n_pass += 1
                success = self.pool.promote(gene)
                if success:
                    promoted.append(gene.gene_id)
            else:
                n_fail += 1

        elapsed_total = time.time() - gen_start

        stats = {
            "generation":   gen,
            "candidates":   len(candidates),
            "evaluated":    n_pass + n_fail,
            "passed":       n_pass,
            "promoted":     len(promoted),
            "promoted_ids": promoted,
            "elapsed_s":    round(elapsed_total, 1),
            "pool_summary": self.pool.summary(),
        }

        self.history.append(stats)

        logger.info(
            "=== 세대 %d 완료: 후보=%d 통과=%d 승격=%d (%.1fs) ===",
            gen, len(candidates), n_pass, len(promoted), elapsed_total,
        )
        return stats

    # ── 다세대 루프 ───────────────────────────────────────────────
    def run(
        self,
        candles: List[dict],
        n_generations: int = 10,
        feature_matrix: Optional[dict] = None,
        stop_on_target: int = 0,
    ) -> List[dict]:
        """
        n_generations 세대 연속 실행.

        Args:
            stop_on_target : active 알파가 이 수에 도달하면 조기 종료 (0=비활성)
        """
        all_stats = []
        for _ in range(n_generations):
            stats = self.run_generation(candles, feature_matrix)
            all_stats.append(stats)

            n_active = stats["pool_summary"]["actives"]
            logger.info("현재 active 알파: %d", n_active)

            if stop_on_target and n_active >= stop_on_target:
                logger.info("목표 달성 (%d active) — 조기 종료", n_active)
                break

        return all_stats

    # ── 후보 생성 ─────────────────────────────────────────────────
    def _create_candidates(self, generation: int) -> List[AlphaGene]:
        n_seed    = max(1, int(self.pop_size * self.seed_ratio))
        n_genetic = self.pop_size - n_seed

        # 랜덤 시드
        seed_genes = self.random_searcher.generate_population(n_seed, generation)

        # 유전 알고리즘 (active 기반)
        parents = self.pool.actives[:20]  # 상위 20개 부모
        if parents:
            existing_keys = {
                self.genetic_searcher._gene_key(g)
                for g in self.pool.actives
            }
            genetic_genes = self.genetic_searcher.evolve(
                parents, generation, n_genetic, existing_keys
            )
        else:
            genetic_genes = self.random_searcher.generate_population(n_genetic, generation)

        return seed_genes + genetic_genes
