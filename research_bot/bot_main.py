# research_bot/bot_main.py — 알파 리서치 봇 진입점
"""
ResearchBot: Phase 6 알파 리서치 봇 통합 클래스.

역할:
  - AlphaPool, EvolutionEngine, AlphaScheduler 조립
  - main.py 에서 독립 스레드로 호출 가능
  - CLI 직접 실행 가능 (python -m research_bot.bot_main)

연동 방법 (main.py에서):
    from research_bot.bot_main import ResearchBot
    bot = ResearchBot()
    bot.start_background()          # 장외 시간 자동 실행
    active_genes = bot.get_actives() # 현재 active 알파 반환
"""
import logging
import threading
from typing import List, Optional

from research_bot.alpha_pool import AlphaPool
from research_bot.alpha_gene import AlphaGene
from research_bot.evolution_engine import EvolutionEngine
from research_bot.alpha_scheduler import AlphaScheduler

logger = logging.getLogger(__name__)


class ResearchBot:
    """알파 리서치 봇 통합 클래스."""

    def __init__(self, pool_path: str = None, pop_size: int = 20):
        self.pool      = AlphaPool(pool_path) if pool_path else AlphaPool()
        self.engine    = EvolutionEngine(self.pool, pop_size=pop_size)
        self.scheduler = AlphaScheduler.__new__(AlphaScheduler)
        # scheduler 수동 초기화 (AlphaPool 공유)
        self.scheduler.pool    = self.pool
        self.scheduler.engine  = self.engine
        self.scheduler._running = False
        self.scheduler._thread  = None

        self._started = False

    # ── 백그라운드 스케줄러 ────────────────────────────────────────
    def start_background(self):
        """장외 시간 자동 리서치 스레드 시작."""
        if self._started:
            return
        self._started = True
        self.scheduler.start()
        logger.info("ResearchBot 백그라운드 스케줄러 시작")

    def stop(self):
        self.scheduler.stop()
        self._started = False
        logger.info("ResearchBot 종료")

    # ── Active 알파 조회 ──────────────────────────────────────────
    def get_actives(self, top_n: int = 10) -> List[AlphaGene]:
        """현재 active 상위 알파 반환."""
        return self.pool.top_active(top_n)

    def get_pool_summary(self) -> dict:
        return self.pool.summary()

    # ── 수동 실행 ─────────────────────────────────────────────────
    def run_now(self, candles: List[dict] = None, n_generations: int = 3):
        """
        즉시 리서치 실행 (단위 테스트 / 수동 트리거).

        Args:
            candles      : 1분봉 데이터 (없으면 DB에서 자동 로드)
            n_generations: 실행할 세대 수
        """
        if candles is None:
            candles = self.scheduler._load_candles()

        if not candles:
            logger.warning("ResearchBot.run_now: 데이터 없음")
            return []

        return self.engine.run(candles, n_generations=n_generations)

    # ── 성과 피드백 ───────────────────────────────────────────────
    def report_trade(self, gene_id: str, pnl: float):
        """
        실전 매매 결과를 알파 풀에 피드백.

        Args:
            gene_id : AlphaGene.gene_id
            pnl     : 해당 신호 사용 거래의 손익 (원화 or pt)
        """
        self.pool.report_performance(gene_id, pnl)


# ── CLI 진입점 ────────────────────────────────────────────────────
def main():
    import argparse
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s  %(message)s",
    )

    parser = argparse.ArgumentParser(description="Phase 6 — 알파 리서치 봇")
    sub    = parser.add_subparsers(dest="cmd")

    p_run = sub.add_parser("run",    help="즉시 진화 실행")
    p_run.add_argument("--gens",     type=int, default=5, help="세대 수")
    p_run.add_argument("--pop",      type=int, default=20, help="개체 수")

    sub.add_parser("status", help="풀 현황 출력")

    p_sched = sub.add_parser("schedule", help="장외 스케줄러 데몬 실행")

    args = parser.parse_args()

    bot = ResearchBot()

    if args.cmd == "run":
        bot.engine.pop_size = args.pop
        stats = bot.run_now(n_generations=args.gens)
        if stats:
            total = sum(s["promoted"] for s in stats)
            print(f"\n완료: {len(stats)}세대, {total}개 승격")
            summary = bot.get_pool_summary()
            print(f"Active 알파: {summary['actives']} 개")

    elif args.cmd == "status":
        s = bot.get_pool_summary()
        print(f"candidates={s['candidates']}  active={s['actives']}  retired={s['retired']}")
        print("Top 5:")
        for item in s.get("top5", []):
            print(f"  {item['id']:8s}  score={item['score']:.3f}  "
                  f"sharpe={item['sharpe']:.2f}  IC={item['ic']:.3f}")

    elif args.cmd == "schedule":
        bot.start_background()
        import time
        print("스케줄러 실행 중 (Ctrl+C 종료)")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            bot.stop()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
