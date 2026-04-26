# research_bot/alpha_pool.py — 알파 풀 관리
"""
AlphaPool: 발견된 알파 유전자의 생명주기 관리.

상태 전이:
  candidate → active   : PASS 평가 후 승격
  active    → retired  : 연속 N회 부진 또는 만료
  retired              : 보관만 (재활성화 불가)

CORE 보호:
  - cvd / vwap_dev / ofi 만을 사용하는 유전자 제거 금지

영속화:
  - data/alpha_pool.json 에 저장 (매 변경 시 자동 저장)
  - 최대 active 50개, retired 200개 보관

승격 기준 (PROMOTE):
  IC ≥ 0.02  AND  Sharpe ≥ 0.8  AND  OOS Sharpe > 0

강등 기준 (DEMOTE):
  consecutive_fails ≥ 3  OR  score < 0.05
"""
import os
import json
import time
import logging
from typing import List, Dict, Optional

from research_bot.alpha_gene import AlphaGene

logger = logging.getLogger(__name__)

POOL_PATH       = os.path.join("data", "alpha_pool.json")
MAX_ACTIVE      = 50
MAX_RETIRED     = 200
PROMOTE_IC      = 0.02
PROMOTE_SHARPE  = 0.8
PROMOTE_OOS     = 0.0
DEMOTE_FAILS    = 3
DEMOTE_SCORE    = 0.05


class AlphaPool:
    """알파 유전자 풀 (candidate + active + retired)."""

    def __init__(self, pool_path: str = POOL_PATH):
        self.pool_path  = pool_path
        self._pool: Dict[str, AlphaGene] = {}   # gene_id → AlphaGene
        self._load()

    # ── 조회 ──────────────────────────────────────────────────────
    @property
    def candidates(self) -> List[AlphaGene]:
        return [g for g in self._pool.values() if g.status == "candidate"]

    @property
    def actives(self) -> List[AlphaGene]:
        return sorted(
            [g for g in self._pool.values() if g.status == "active"],
            key=lambda g: g.score, reverse=True,
        )

    @property
    def retired(self) -> List[AlphaGene]:
        return [g for g in self._pool.values() if g.status == "retired"]

    def get(self, gene_id: str) -> Optional[AlphaGene]:
        return self._pool.get(gene_id)

    def top_active(self, n: int = 10) -> List[AlphaGene]:
        """score 상위 n개 active 유전자."""
        return self.actives[:n]

    # ── 추가·승격·강등·퇴역 ────────────────────────────────────────
    def add_candidate(self, gene: AlphaGene):
        """후보 유전자 추가."""
        gene.status = "candidate"
        self._pool[gene.gene_id] = gene
        logger.debug("Pool add candidate: %s", gene.gene_id)

    def promote(self, gene: AlphaGene) -> bool:
        """
        candidate → active 승격.
        PASS 기준: IC ≥ 0.02, Sharpe ≥ 0.8, OOS Sharpe > 0
        active 풀이 꽉 찬 경우 최하위 active를 교체.
        """
        if not self._check_promote_criteria(gene):
            logger.info("Pool promote FAIL %s: IC=%.3f Sharpe=%.2f OOS=%.2f",
                        gene.gene_id, gene.ic, gene.sharpe, gene.oos_sharpe)
            return False

        # active 풀 초과 시 최하위 교체
        if len(self.actives) >= MAX_ACTIVE:
            worst = min(self.actives, key=lambda g: g.score)
            if worst.score >= gene.score:
                logger.info("Pool promote SKIP %s: 풀 만석 + 더 나은 대체재 없음", gene.gene_id)
                return False
            self._retire(worst)

        gene.status      = "active"
        gene.promoted_at = time.time()
        self._pool[gene.gene_id] = gene
        self._save()
        logger.info("Pool PROMOTE: %s  score=%.3f IC=%.3f Sharpe=%.2f",
                    gene.gene_id, gene.score, gene.ic, gene.sharpe)
        return True

    def report_performance(self, gene_id: str, pnl: float):
        """실전 성과 업데이트 (성공/실패 카운트)."""
        gene = self._pool.get(gene_id)
        if gene is None or gene.status != "active":
            return
        if pnl > 0:
            gene.consecutive_fails = 0
        else:
            gene.consecutive_fails += 1

        if gene.consecutive_fails >= DEMOTE_FAILS or gene.score < DEMOTE_SCORE:
            self._retire(gene)
            self._save()
        else:
            self._save()

    def _retire(self, gene: AlphaGene):
        """active → retired."""
        gene.status     = "retired"
        gene.retired_at = time.time()
        logger.info("Pool RETIRE: %s", gene.gene_id)

        # retired 보관 한도 초과 시 오래된 것 제거
        all_retired = sorted(self.retired, key=lambda g: g.retired_at or 0)
        while len(all_retired) > MAX_RETIRED:
            oldest = all_retired.pop(0)
            del self._pool[oldest.gene_id]

    def _check_promote_criteria(self, gene: AlphaGene) -> bool:
        return (
            gene.ic        >= PROMOTE_IC     and
            gene.sharpe    >= PROMOTE_SHARPE  and
            gene.oos_sharpe >= PROMOTE_OOS    and
            gene.n_samples >= 300
        )

    # ── 통계 ──────────────────────────────────────────────────────
    def summary(self) -> dict:
        return {
            "candidates": len(self.candidates),
            "actives":    len(self.actives),
            "retired":    len(self.retired),
            "top5": [
                {"id": g.gene_id, "score": g.score, "sharpe": g.sharpe, "ic": g.ic}
                for g in self.top_active(5)
            ],
        }

    # ── 영속화 ────────────────────────────────────────────────────
    def _save(self):
        os.makedirs(os.path.dirname(self.pool_path) or ".", exist_ok=True)
        try:
            data = {gid: g.to_dict() for gid, g in self._pool.items()}
            with open(self.pool_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("AlphaPool 저장 실패: %s", e)

    def _load(self):
        if not os.path.exists(self.pool_path):
            return
        try:
            with open(self.pool_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._pool = {gid: AlphaGene.from_dict(d) for gid, d in data.items()}
            logger.info("AlphaPool 로드: %d 개체 (%d active)",
                        len(self._pool), len(self.actives))
        except Exception as e:
            logger.error("AlphaPool 로드 실패: %s", e)
            self._pool = {}
