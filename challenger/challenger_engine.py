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

from challenger.challenger_cost import calc_pnl_pt, cost_context
from challenger.challenger_db import ChallengerDB
from challenger.challenger_registry import ChallengerRegistry, REGIME_POOLS
from challenger.variants.base_challenger import ChallengerTrade, ExitReason

logger = logging.getLogger("CHALLENGER")

SHADOW_WARN_MS  = 5.0
#: 도전자가 `FORCE_EXIT_TIME` 을 선언하지 않을 때의 기본값(절대원칙 §1).
#: ⚠ [553차] 실제로는 파이프라인이 15:10 이후 봉을 주지 않아 **발화하지 않는다** —
#:   남은 포지션은 마감 훅의 `EOD_FORCE` 가 닫는다. `_recover_open_trades()` 참조.
FORCE_EXIT_TIME = "15:10"

# 레짐 전문가 풀이 있는 레짐만 순위 감시
RANKED_REGIMES = [r for r, pool in REGIME_POOLS.items() if len(pool) > 1]


class ChallengerEngine(object):
    """Shadow 실행 오케스트레이터."""

    def __init__(self, db=None, registry=None, recover=True):
        self.db       = db       or ChallengerDB()
        self.registry = registry or ChallengerRegistry()
        self._open_trades = {}   # type: Dict[str, Optional[ChallengerTrade]]
        # [553차] 마지막으로 본 봉 — EOD 강제마감의 청산가 원천.
        # 🔴 `getattr(self, "_x", default)` 로 읽지 않기 위해 여기서 명시 초기화한다.
        #   미설정을 None 으로 두면 폴백 시점에 로그를 남길 수 있다(계측 4원칙 ④).
        self._last_close = None   # type: Optional[float]
        self._last_ts    = None   # type: Optional[str]
        self._register_default_challengers()
        if recover:
            self._recover_open_trades()

    def _register_default_challengers(self):
        try:
            from challenger.variants.cvd_exhaustion   import CvdExhaustionChallenger
            from challenger.variants.ofi_reversal     import OfiReversalChallenger
            from challenger.variants.vwap_reversal    import VwapReversalChallenger
            from challenger.variants.exhaustion_regime import ExhaustionRegimeChallenger
            from challenger.variants.absorption       import AbsorptionChallenger
            from challenger.variants.champion_tp1_skip_trail import ChampionTp1SkipTrailChallenger

            for cls in (CvdExhaustionChallenger, OfiReversalChallenger,
                        VwapReversalChallenger, ExhaustionRegimeChallenger,
                        AbsorptionChallenger, ChampionTp1SkipTrailChallenger):
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
        """15:40 마감 — **미청산 강제마감** → 일별·레짐별 집계 + 순위 감지 + WARNING

        🔴 강제마감이 집계보다 **먼저**여야 한다. `_compute_and_save_daily()` 는
          `get_today_closed_trades()` 로 **청산분만** 세므로, 열린 채로 두면 그 거래가
          집계에서 조용히 사라진다 — 손실이었는지 이익이었는지 모르는 채로 성과가
          좋아지는 방향이다(계측 4원칙 ②).
        """
        try:
            self._force_close_open_trades(date_str)
            self._compute_and_save_daily(date_str)
            self._compute_regime_metrics(date_str)
            self._check_regime_rankings(date_str)
        except Exception:
            logger.error("[Engine] update_daily_metrics 예외:\n%s", traceback.format_exc())

    # ── [MW0601 553차 Phase 2] 미청산 누수 차단 ──────────────────────────
    #
    # 무엇이 문제였나 (실측: `challenger_trades` 28건 중 **3건 = 10.7%** 가 exit_ts NULL)
    #   ① 엔진 안전망 `FORCE_EXIT_TIME="15:10"` 이 **도달 불가**다. 파이프라인은 15:10
    #      이후 봉을 처리하지 않으므로(`main.py:_on_candle_closed` force-exit 분기가
    #      return) 엔진이 보는 마지막 봉은 15:08 이다.
    #   ② `_open_trades` 가 **인메모리**다. 프로세스가 재시작하면 열린 가상거래를 잃고
    #      DB 행은 `exit_ts=NULL` 로 굳는다 — 552-10(`_broker_dep_base_today`)·
    #      552-11(`entry_source` 오귀속)과 같은 **「재시작이 지운 상태」 계열**이다.
    #   그리고 `_compute_and_save_daily()` 는 청산분만 세므로 그 거래가 집계에서
    #   **조용히 사라진다**(계측 4원칙 ②).
    #
    # 두 경로로 막는다:
    #   · 정상 마감 → `_force_close_open_trades()` (그날 마지막 종가, `EOD_FORCE`)
    #   · 마감을 못 하고 죽은 경우 → 다음 기동의 `_recover_open_trades()` 가
    #     그 날짜 마지막 정규장 종가를 **재구성**해 닫는다(`EOD_FORCE_RECON`).
    #     재구성값은 관측값이 아니므로 **사유 이름으로 그 사실을 남긴다**(원칙 ④).

    def _force_close_open_trades(self, date_str):
        # type: (str) -> None
        """마감 시각에 남아 있는 가상 포지션을 그날 마지막 종가로 닫는다."""
        price = self._last_close
        ts = self._last_ts
        if not price or price <= 0:
            # 값을 지어내지 않는다 — 다음 기동의 복구 경로가 재구성으로 처리한다.
            if any(t is not None for t in self._open_trades.values()):
                logger.error("[Engine] EOD 강제마감 불가 — 마지막 종가 미측정(%s). "
                             "다음 기동의 복구 경로가 재구성으로 닫는다", date_str)
            return
        closed = 0
        for cid, trade in list(self._open_trades.items()):
            if trade is None:
                continue
            self._close_virtual_trade(trade, price, ts or date_str + " 15:10:00",
                                      ExitReason.EOD_FORCE)
            self._open_trades[cid] = None
            closed += 1
        if closed:
            logger.info("[Engine] EOD 강제마감 %d건 @%.2f (%s)", closed, price, ts)

    def _recover_open_trades(self):
        # type: () -> None
        """기동 시 DB 의 미청산 행을 승계하거나 재구성 청산한다.

        · `entry_ts` 가 **오늘**이면 → 인메모리로 승계(같은 날 이어서 관리).
          같은 도전자에 여러 건이면 최신 1건만 승계하고 나머지는 재구성 청산한다
          (엔진은 도전자당 1포지션이 불변식이다).
        · **이전 날짜**면 → 그날 마지막 정규장 종가로 재구성 청산(`EOD_FORCE_RECON`).
        · 종가를 못 구하면 **열린 채로 두고 ERROR** 를 남긴다. 지어내지 않는다.
        """
        try:
            rows = self.db.get_all_open_trades()
        except Exception:
            logger.warning("[Engine] 미청산 조회 실패 — 복구 스킵", exc_info=True)
            return
        if not rows:
            return

        today = datetime.now().strftime("%Y-%m-%d")
        by_cid = {}
        for r in rows:
            by_cid.setdefault(r["challenger_id"], []).append(r)

        adopted = reconned = failed = 0
        for cid, items in by_cid.items():
            items.sort(key=lambda x: x["entry_ts"] or "")
            todays = [r for r in items if (r["entry_ts"] or "")[:10] == today]
            stale = [r for r in items if (r["entry_ts"] or "")[:10] != today]
            # 오늘 것이 2건 이상이면 최신만 남긴다(불변식 복구)
            if len(todays) > 1:
                stale.extend(todays[:-1])
                todays = todays[-1:]
            for r in stale:
                if self._recon_close(r):
                    reconned += 1
                else:
                    failed += 1
            if todays and cid in self._open_trades:
                self._open_trades[cid] = self._row_to_trade(todays[0])
                adopted += 1

        if adopted or reconned or failed:
            logger.warning(
                "[Engine] 미청산 복구 — 승계 %d · 재구성청산 %d · 실패 %d "
                "(재구성 청산가는 관측값이 아니다: exit_reason=%s)",
                adopted, reconned, failed, ExitReason.EOD_FORCE_RECON)

    @staticmethod
    def _row_to_trade(row):
        # type: (Any) -> ChallengerTrade
        t = ChallengerTrade(
            trade_id      = row["id"],
            challenger_id = row["challenger_id"],
            entry_ts      = row["entry_ts"],
            direction     = int(row["direction"]),
            entry_price   = float(row["entry_price"]),
            grade         = row["grade"],
            atr_at_entry  = None,   # 미측정 — should_exit 가 현재 atr 로 판단한다
        )
        return t

    def _recon_close(self, row):
        # type: (Any) -> bool
        """이전 날짜 미청산 행을 그날 마지막 정규장 종가로 재구성 청산."""
        day = (row["entry_ts"] or "")[:10]
        if not day:
            return False
        price, ts = self._last_regular_close_of(day)
        if not price:
            logger.error("[Engine] 재구성 청산 불가 — %s 정규장 종가 없음 (id=%s)",
                         day, row["id"])
            return False
        ctx = cost_context()
        pnl = calc_pnl_pt(int(row["direction"]), float(row["entry_price"]), price, ctx)
        try:
            self.db.close_trade(row["id"], ts, price, pnl,
                                ExitReason.EOD_FORCE_RECON, cost_ctx=ctx)
            return True
        except Exception:
            logger.error("[Engine] 재구성 청산 DB 실패 id=%s", row["id"], exc_info=True)
            return False

    @staticmethod
    def _last_regular_close_of(day):
        # type: (str) -> Any
        """그 거래일의 마지막 정규장(09:00~15:09) 종가와 ts. 없으면 (None, None).

        ⚠ 조회는 ts(PK) 역순 1행이라 456차 전수 스캔 금지에 걸리지 않는다.
        """
        try:
            from config.settings import RAW_DATA_DB
            from utils.db_utils import fetchall
            rows = fetchall(
                RAW_DATA_DB,
                """SELECT ts, close FROM raw_candles
                   WHERE ts LIKE ?
                     AND substr(ts, 12, 5) >= '09:00'
                     AND substr(ts, 12, 5) <= '15:09'
                     AND close > 0
                   ORDER BY ts DESC LIMIT 1""",
                (day + "%",),
            )
            if rows:
                return float(rows[0]["close"]), rows[0]["ts"]
        except Exception:
            logger.debug("[Engine] %s 마지막 종가 조회 실패", day, exc_info=True)
        return None, None

    # ── 내부 구현 ─────────────────────────────────────────────────

    def _run_shadow_inner(self, features, candle, context):
        ts          = context.get("ts", "")
        close_price = float(candle.get("close", 0) or 0)
        atr         = float(context.get("atr", 1.0) or 1.0)
        regime      = context.get("regime", "혼합")

        # [553차] EOD 강제마감의 청산가 원천. 값이 성립할 때만 갱신한다.
        if close_price > 0 and ts:
            self._last_close = close_price
            self._last_ts    = ts

        for challenger in self.registry.active_challengers():
            cid = challenger.challenger_id
            # [553차] 강제청산 시각은 **도전자별**이다(GP 규칙은 15:05).
            # Base 가 항상 정의하므로 getattr 폴백을 쓰지 않는다(계측 4원칙 ④).
            is_force = self._is_force_exit_time(ts, challenger.FORCE_EXIT_TIME)

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
            # [553차] 등급 개념이 없는 도전자(GP 규칙 등)는 등급 조건을 건너뛴다.
            # 종전에는 통과하려고 grade="A" 를 지어내야 했다 — **등급 위장**이며
            # 계측 4원칙 ④ 위반이다. 선언으로 대신한다.
            grade_ok = challenger.GRADE_NA or signal.grade in ("A", "B")
            if (open_trade is None
                    and signal.direction != 0
                    and grade_ok
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
        ctx = cost_context()
        pnl = calc_pnl_pt(trade.direction, trade.entry_price, exit_price, ctx)
        try:
            self.db.close_trade(trade.trade_id, exit_ts, exit_price, pnl, reason,
                                cost_ctx=ctx)
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

    # 🔴 [553차] `_calc_pnl()` 제거 — 키움 잔재 요율 0.000015 하드코딩 + 슬리피지 누락.
    #   같은 공식이 `BaseChallenger.calc_pnl()` 에도 한 벌 더 있었다. 둘 다
    #   `challenger_cost.calc_pnl_pt()` 로 일원화했다(핀값 금지, 493차).

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
    def _is_force_exit_time(ts, force_time=None):
        # type: (str, Optional[str]) -> bool
        try:
            return ts[11:16] >= (force_time or FORCE_EXIT_TIME)
        except Exception:
            return False
