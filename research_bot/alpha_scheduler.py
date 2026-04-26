# research_bot/alpha_scheduler.py — 장외 시간 자동 스케줄러
"""
AlphaScheduler: 장외 시간(15:30~08:30)에 알파 리서치 자동 실행.

스케줄 전략:
  - 매일 16:00 에 데이터 로드 후 진화 엔진 실행
  - 매일 08:00 에 active 알파 요약 리포트 출력
  - 운영 중(09:00~15:10) 에는 리서치 금지 (CPU 보호)

데이터 로드 전략:
  - 로컬 DB (data/candles.db) 에서 읽기 (db_utils 활용)
  - DB 없으면 candles.pkl fallback
  - 데이터 부족 시 스킵

실행 방법:
  python -m research_bot.alpha_scheduler       # 백그라운드 스케줄러 데몬
  python -m research_bot.alpha_scheduler --now # 즉시 한 세대 실행
"""
import os
import sys
import time
import logging
import datetime
import argparse
import threading
from typing import List, Optional

logger = logging.getLogger(__name__)

# ── 시장 시간 정의 ─────────────────────────────────────────────────
MARKET_OPEN_H   = 9
MARKET_OPEN_M   = 0
MARKET_CLOSE_H  = 15
MARKET_CLOSE_M  = 10

# 리서치 실행 시각 (장 마감 후)
RESEARCH_H      = 16
RESEARCH_M      = 0

# 리포트 시각 (장 시작 전)
REPORT_H        = 8
REPORT_M        = 0

# 한 세대 파라미터
N_GENERATIONS   = 5
POP_SIZE        = 20


class AlphaScheduler:
    """장외 알파 리서치 스케줄러."""

    def __init__(self, pool_path: str = None):
        from research_bot.alpha_pool import AlphaPool
        from research_bot.evolution_engine import EvolutionEngine

        self.pool   = AlphaPool(pool_path) if pool_path else AlphaPool()
        self.engine = EvolutionEngine(
            self.pool,
            pop_size      = POP_SIZE,
            n_generations = N_GENERATIONS if hasattr(EvolutionEngine, 'n_generations') else N_GENERATIONS,
        )
        self._running   = False
        self._thread: Optional[threading.Thread] = None

    # ── 공개 API ───────────────────────────────────────────────────
    def start(self):
        """백그라운드 스케줄러 시작."""
        if self._running:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True, name="AlphaScheduler")
        self._thread.start()
        logger.info("AlphaScheduler 시작")

    def stop(self):
        """스케줄러 정지."""
        self._running = False
        logger.info("AlphaScheduler 정지 요청")

    def run_now(self, n_generations: int = N_GENERATIONS):
        """즉시 리서치 실행 (테스트/수동 호출용)."""
        candles = self._load_candles()
        if not candles:
            logger.warning("run_now: 데이터 없음 — 스킵")
            return

        logger.info("run_now: %d 봉 데이터로 %d 세대 진화 시작", len(candles), n_generations)
        stats_list = self.engine.run(candles, n_generations=n_generations)
        self._print_report(stats_list)
        return stats_list

    # ── 스케줄 루프 ──────────────────────────────────────────────
    def _loop(self):
        logger.info("스케줄 루프 진입")
        last_research_date = None
        last_report_date   = None

        while self._running:
            now  = datetime.datetime.now()
            date = now.date()

            # 리포트 시각 (장 시작 전)
            if (now.hour == REPORT_H and now.minute == REPORT_M
                    and last_report_date != date):
                self._morning_report()
                last_report_date = date

            # 리서치 시각 (장 마감 후)
            if (now.hour == RESEARCH_H and now.minute >= RESEARCH_M
                    and last_research_date != date):
                if not self._is_market_hours(now):
                    self._run_daily_research()
                    last_research_date = date

            time.sleep(30)   # 30초 간격 체크

    def _run_daily_research(self):
        logger.info("=== 일일 알파 리서치 시작 ===")
        try:
            candles = self._load_candles()
            if not candles:
                logger.warning("데이터 없음 — 리서치 스킵")
                return

            stats_list = self.engine.run(candles, n_generations=N_GENERATIONS)
            self._print_report(stats_list)

        except Exception as e:
            logger.error("일일 리서치 오류: %s", e, exc_info=True)

    def _morning_report(self):
        """장 시작 전 active 알파 요약 출력."""
        summary = self.pool.summary()
        logger.info(
            "[아침 리포트] active=%d candidates=%d retired=%d",
            summary["actives"], summary["candidates"], summary["retired"],
        )
        for item in summary.get("top5", []):
            logger.info("  ▶ %s  score=%.3f  sharpe=%.2f  IC=%.3f",
                        item["id"], item["score"], item["sharpe"], item["ic"])

    @staticmethod
    def _is_market_hours(dt: datetime.datetime) -> bool:
        t = (dt.hour, dt.minute)
        open_t  = (MARKET_OPEN_H,  MARKET_OPEN_M)
        close_t = (MARKET_CLOSE_H, MARKET_CLOSE_M)
        return open_t <= t <= close_t

    # ── 데이터 로드 ──────────────────────────────────────────────
    def _load_candles(self) -> List[dict]:
        """로컬 캔들 데이터 로드 (DB → pickle fallback)."""
        # 1. SQLite DB
        try:
            candles = self._load_from_db()
            if candles:
                return candles
        except Exception as e:
            logger.debug("DB 로드 실패: %s", e)

        # 2. pickle fallback
        try:
            candles = self._load_from_pickle()
            if candles:
                return candles
        except Exception as e:
            logger.debug("pickle 로드 실패: %s", e)

        return []

    @staticmethod
    def _load_from_db() -> List[dict]:
        import sqlite3
        db_path = os.path.join("data", "candles.db")
        if not os.path.exists(db_path):
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.execute(
                "SELECT open,high,low,close,volume,timestamp "
                "FROM candles ORDER BY timestamp ASC LIMIT 10000"
            )
            rows = cur.fetchall()
            return [
                {"open": r[0], "high": r[1], "low": r[2],
                 "close": r[3], "volume": r[4], "timestamp": r[5]}
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def _load_from_pickle() -> List[dict]:
        import pickle
        pkl_path = os.path.join("data", "candles.pkl")
        if not os.path.exists(pkl_path):
            return []
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)
        if isinstance(data, list):
            return data
        return []

    # ── 리포트 출력 ──────────────────────────────────────────────
    def _print_report(self, stats_list: List[dict]):
        total_promoted = sum(s.get("promoted", 0) for s in stats_list)
        logger.info(
            "리서치 완료: %d 세대 / 총 %d 개 승격 / active=%d",
            len(stats_list),
            total_promoted,
            self.pool.summary()["actives"],
        )
        for s in stats_list:
            logger.info(
                "  gen=%d 후보=%d 통과=%d 승격=%d (%.1fs)",
                s["generation"], s["candidates"],
                s["passed"], s["promoted"], s["elapsed_s"],
            )


# ── 직접 실행 ────────────────────────────────────────────────────
def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s  %(message)s",
    )

    parser = argparse.ArgumentParser(description="Alpha Research Bot Scheduler")
    parser.add_argument("--now",  action="store_true", help="즉시 한 세대 실행")
    parser.add_argument("--gens", type=int, default=N_GENERATIONS, help="세대 수")
    args = parser.parse_args()

    scheduler = AlphaScheduler()

    if args.now:
        scheduler.run_now(n_generations=args.gens)
    else:
        scheduler.start()
        logger.info("스케줄러 데몬 실행 중 (Ctrl+C 로 종료)")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.stop()
            logger.info("스케줄러 종료")


if __name__ == "__main__":
    main()
