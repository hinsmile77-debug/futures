# challenger/challenger_engine.py — Shadow 실행 오케스트레이터
"""
ChallengerEngine: 매분 파이프라인 STEP 9 이후 훅으로 호출.

- 실제 주문 없음 (Shadow 실행)
- 신호·가상 거래에 regime 태깅
- 일별 마감 시 레짐별 순위 계산 → 1위 변경 시 대시보드 WARNING
- 소요 시간 목표: < 5ms
"""
import math
import time
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List

from challenger.challenger_db import ChallengerDB
from challenger.challenger_registry import ChallengerRegistry, REGIME_POOLS
from challenger.variants.base_challenger import ChallengerTrade, ExitReason

logger = logging.getLogger("CHALLENGER")

SHADOW_WARN_MS  = 5.0
FORCE_EXIT_TIME = "15:10"

# 레짐 전문가 풀이 있는 레짐만 순위 감시
RANKED_REGIMES = [r for r, pool in REGIME_POOLS.items() if len(pool) > 1]


class ChallengerEngine(object):
    """Shadow 실행 오케스트레이터."""

    def __init__(self, db=None, registry=None):
        self.db       = db       or ChallengerDB()
        self.registry = registry or ChallengerRegistry()
        self._open_trades = {}   # type: Dict[str, Optional[ChallengerTrade]]
        self._register_default_challengers()

    def _register_default_challengers(self):
        try:
            from challenger.variants.cvd_exhaustion   import CvdExhaustionChallenger
            from challenger.variants.ofi_reversal     import OfiReversalChallenger
            from challenger.variants.vwap_reversal    import VwapReversalChallenger
            from challenger.variants.exhaustion_regime import ExhaustionRegimeChallenger
            from challenger.variants.absorption       import AbsorptionChallenger

            for cls in (CvdExhaustionChallenger, OfiReversalChallenger,
                        VwapReversalChallenger, ExhaustionRegimeChallenger,
                        AbsorptionChallenger):
                inst = cls()
                self.registry.register(inst)
                self._open_trades[inst.challenger_id] = None

        except Exception as e:
            logger.warning("[Engine] 도전자 등록 실패: %s", e)

    # ── 공개 API ──────────────────────────────────────────────────

    def run_shadow(self, features, candle, context):
        # type: (Dict[str, Any], Dict[str, Any], Dict[str, Any]) -> None
        t0 = time.time()
        try:
            self._run_shadow_inner(features, candle, context)
        except Exception:
            logger.error("[Engine] run_shadow 예외:\n%s", traceback.format_exc())
        finally:
            elapsed_ms = (time.time() - t0) * 1000.0
            if elapsed_ms > SHADOW_WARN_MS:
                logger.warning("[Engine] run_shadow %.1fms (목표 <5ms)", elapsed_ms)

    def update_daily_metrics(self, date_str):
        # type: (str) -> None
        """15:40 마감 — 일별·레짐별 집계 + 순위 감지 + WARNING"""
        try:
            self._compute_and_save_daily(date_str)
            self._compute_regime_metrics(date_str)
            self._check_regime_rankings(date_str)
        except Exception:
            logger.error("[Engine] update_daily_metrics 예외:\n%s", traceback.format_exc())

    # ── 내부 구현 ─────────────────────────────────────────────────

    def _run_shadow_inner(self, features, candle, context):
        ts          = context.get("ts", "")
        close_price = float(candle.get("close", 0) or 0)
        atr         = float(context.get("atr", 1.0) or 1.0)
        regime      = context.get("regime", "혼합")
        is_force    = self._is_force_exit_time(ts)

        for challenger in self.registry.active_challengers():
            cid = challenger.challenger_id

            # 1. 열린 가상 포지션 청산 체크
            open_trade = self._open_trades.get(cid)
            if open_trade is not None:
                reason = (ExitReason.FORCE if is_force
                          else challenger.should_exit(open_trade, close_price, ts, atr))
                if reason:
                    self._close_virtual_trade(open_trade, close_price, ts, reason)
                    self._open_trades[cid] = None
                    open_trade = None

            # 2. 신호 생성
            try:
                signal = challenger.generate_signal(features, context)
            except Exception:
                logger.error("[Engine] %s generate_signal:\n%s",
                             cid, traceback.format_exc())
                continue

            try:
                self.db.insert_signal(signal, regime=regime)
            except Exception:
                logger.error("[Engine] insert_signal 실패: %s", cid)

            # 3. 신규 가상 진입
            if (open_trade is None
                    and signal.direction != 0
                    and signal.grade in ("A", "B")
                    and not is_force):
                self._open_virtual_trade(challenger, signal, close_price, ts, atr, regime)

    def _open_virtual_trade(self, challenger, signal, entry_price, ts, atr, regime):
        trade = ChallengerTrade(
            trade_id      = None,
            challenger_id = challenger.challenger_id,
            entry_ts      = ts,
            direction     = signal.direction,
            entry_price   = entry_price,
            grade         = signal.grade,
            atr_at_entry  = atr,
        )
        try:
            row_id = self.db.insert_trade(trade, regime=regime)
            trade.trade_id = row_id
            self._open_trades[challenger.challenger_id] = trade
        except Exception:
            logger.error("[Engine] insert_trade 실패: %s", challenger.challenger_id)

    def _close_virtual_trade(self, trade, exit_price, exit_ts, reason):
        pnl = self._calc_pnl(trade, exit_price)
        try:
            self.db.close_trade(trade.trade_id, exit_ts, exit_price, pnl, reason)
        except Exception:
            logger.error("[Engine] close_trade 실패: id=%s", trade.trade_id)

    # ── 일별 집계 ─────────────────────────────────────────────────

    def _compute_and_save_daily(self, date_str):
        for cid in self.registry.ids():
            trades = self.db.get_today_closed_trades(cid, date_str)
            signal_count = self.db.get_today_signal_count(cid, date_str)
            trade_count = len(trades)
            if trade_count == 0:
                continue
            pnl_list  = [t["pnl_pt"] for t in trades if t["pnl_pt"] is not None]
            win_count = sum(1 for p in pnl_list if p > 0)
            total_pnl = sum(pnl_list)
            cum = self.db.get_metrics_summary(cid)
            self.db.upsert_daily_metrics({
                "date":          date_str,
                "challenger_id": cid,
                "signal_count":  signal_count,
                "trade_count":   trade_count,
                "win_count":     win_count,
                "win_rate":      round(win_count / trade_count * 100, 2) if trade_count else 0.0,
                "total_pnl_pt":  round(total_pnl, 2),
                "mdd_pt":        self._calc_mdd(pnl_list),
                "sharpe":        self._calc_sharpe(pnl_list),
                "cum_pnl_pt":    round(cum["cum_pnl_pt"] + total_pnl, 2),
                "cum_mdd_pt":    min(cum["cum_mdd_pt"], self._calc_mdd(pnl_list)),
            })

    def _compute_regime_metrics(self, date_str):
        """레짐별 누적 집계 갱신 (전체 이력 기준)"""
        for regime, pool in REGIME_POOLS.items():
            for cid in pool:
                if cid not in self.registry.ids():
                    continue
                trades = self.db.get_regime_closed_trades(cid, regime)
                if not trades:
                    continue
                pnl_list  = [t["pnl_pt"] for t in trades if t["pnl_pt"] is not None]
                trade_count = len(trades)
                win_count   = sum(1 for p in pnl_list if p > 0)
                self.db.upsert_regime_metrics(cid, regime, {
                    "trade_count": trade_count,
                    "win_count":   win_count,
                    "win_rate":    round(win_count / trade_count * 100, 2) if trade_count else 0.0,
                    "total_pnl_pt": round(sum(pnl_list), 2),
                    "mdd_pt":      self._calc_mdd(pnl_list),
                    "sharpe":      self._calc_sharpe(pnl_list),
                })

    # ── 레짐 순위 감지 + WARNING ──────────────────────────────────

    def _check_regime_rankings(self, date_str):
        """
        레짐별 전문가 풀 순위 계산.
        1위가 이전과 다르면:
          1) registry Shadow 1위 갱신
          2) DB rank_history 기록
          3) 대시보드 WARNING 발송
        """
        ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for regime in RANKED_REGIMES:
            pool = self.registry.get_regime_pool(regime)
            if not pool:
                continue

            ranking = self.db.get_regime_ranking(regime, pool)
            if not ranking:
                continue

            new_rank1  = ranking[0]["challenger_id"] if len(ranking) > 0 else None
            new_rank2  = ranking[1]["challenger_id"] if len(ranking) > 1 else None
            new_rank3  = ranking[2]["challenger_id"] if len(ranking) > 2 else None
            prev_entry = self.db.get_latest_regime_rank(regime)
            prev_rank1 = prev_entry["rank_1_id"] if prev_entry else None

            changed = self.registry.update_regime_shadow_rank1(regime, new_rank1)

            self.db.insert_regime_rank(
                ts=ts_now, regime=regime,
                rank1=new_rank1, rank2=new_rank2, rank3=new_rank3,
                prev_rank1=prev_rank1, changed=changed,
            )

            if changed and new_rank1:
                self._emit_rank_change_warning(
                    regime, prev_rank1, new_rank1, ranking[0]
                )

    def _emit_rank_change_warning(self, regime, prev_id, new_id, new_metrics):
        # type: (str, Optional[str], str, Dict[str, Any]) -> None
        """대시보드 WARNING + logger 발송"""
        name_map = {
            "A_CVD_EXHAUSTION":    "CVD탈진",
            "C_VWAP_REVERSAL":     "VWAP반전",
            "D_EXHAUSTION_REGIME": "탈진레짐",
            "B_OFI_REVERSAL":      "OFI반전",
            "E_ABSORPTION":        "흡수감지",
            "CHAMPION_BASELINE":   "챔피언기준선",
        }
        prev_name = name_map.get(prev_id or "", prev_id or "없음")
        new_name  = name_map.get(new_id, new_id)
        tc  = new_metrics.get("trade_count", 0)
        wr  = new_metrics.get("win_rate", 0.0)
        sh  = new_metrics.get("sharpe", 0.0)

        msg = (
            "[도전자] ⚔ [%s] 레짐 Shadow 1위 변경: %s → %s "
            "| 거래 %d건 · 승률 %.1f%% · Sharpe %.2f "
            "| 수동 승격 검토 권장"
            % (regime, prev_name, new_name, tc, wr, sh)
        )
        logger.warning(msg)

        # 대시보드 WARNING 탭에 발송
        try:
            from logging_system.log_manager import log_manager as _lm
            _lm.system(msg, "WARNING")
        except Exception:
            pass  # 대시보드 없는 환경(백테스트 등)에서는 무시

    # ── 유틸 ─────────────────────────────────────────────────────

    @staticmethod
    def _calc_pnl(trade, exit_price):
        raw = (exit_price - trade.entry_price) * trade.direction
        commission = (trade.entry_price + exit_price) * 0.000015 * 2
        return round(raw - commission, 4)

    @staticmethod
    def _calc_mdd(pnl_list):
        # type: (List[float]) -> float
        if not pnl_list:
            return 0.0
        equity = peak = mdd = 0.0
        for p in pnl_list:
            equity += p
            if equity > peak:
                peak = equity
            dd = equity - peak
            if dd < mdd:
                mdd = dd
        return round(mdd, 2)

    @staticmethod
    def _calc_sharpe(pnl_list):
        # type: (List[float]) -> float
        if len(pnl_list) < 3:
            return 0.0
        n   = len(pnl_list)
        avg = sum(pnl_list) / n
        var = sum((p - avg) ** 2 for p in pnl_list) / n
        std = math.sqrt(var) if var > 0 else 1e-9
        return round(avg / std * (252 ** 0.5), 2)

    @staticmethod
    def _is_force_exit_time(ts):
        # type: (str) -> bool
        try:
            return ts[11:16] >= FORCE_EXIT_TIME
        except Exception:
            return False
