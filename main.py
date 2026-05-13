# main.py — 메인 실행 진입점
"""
KOSPI 200 선물 방향 예측 시스템 — 미륵이 (Futures Edition)

실행 흐름:
  08:50  매크로 수집 → 레짐 판단
  09:00  장 시작 — 매분 파이프라인 시작
  [매분] STEP 1~9 순서대로 실행
  15:10  강제 청산
  15:40  자가학습 일일 마감

사용법:
  python main.py
  python main.py --mode simulation   (기본)
  python main.py --mode live
"""
import sys
import os
import copy
import datetime
import time
import logging
import math
import json
import subprocess
import numpy as np
from typing import Optional

# ── 프로젝트 루트를 PYTHONPATH에 추가 ─────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ── Qt Application (키움 OCX 보다 먼저 생성) ───────────────────
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
_qt_app = QApplication.instance() or QApplication(sys.argv)

# ── 로깅 초기화 (가장 먼저) ────────────────────────────────────
from utils.logger import setup_logging
setup_logging()
logger    = logging.getLogger("SYSTEM")
debug_log = logging.getLogger("DEBUG")

# ── DB 초기화 ──────────────────────────────────────────────────
from utils.db_utils import (
    init_all_dbs, execute, save_candle, save_features, count_raw_candles,
    fetch_today_trades, fetch_pnl_history, normalize_trade_pnl,
    save_daily_stats, fetch_trend_daily, fetch_trend_weekly,
    fetch_trend_monthly, fetch_trend_yearly,
    is_plausible_futures_trade,
)
from config.settings import (
    TRADES_DB, HORIZONS, PARTIAL_EXIT_RATIOS,
    HURST_RANGE_THRESHOLD, ATR_MIN_ENTRY, ATR_STOP_MULT,
)
from config.constants import FUTURES_PT_VALUE, get_contract_spec
from config import secrets as _secrets

# ── 핵심 모듈 ──────────────────────────────────────────────────
from collection.broker import create_broker
from collection.macro.regime_classifier import RegimeClassifier
from collection.macro.micro_regime import MicroRegimeClassifier
from features.feature_builder import FeatureBuilder
from model.multi_horizon_model import MultiHorizonModel
from model.ensemble_decision import EnsembleDecision
from strategy.position.position_tracker import PositionTracker
from strategy.entry.checklist import EntryChecklist
from strategy.entry.position_sizer import PositionSizer
from strategy.entry.meta_gate import MetaGate
from strategy.entry.adaptive_kelly import AdaptiveKelly
from strategy.exit.time_exit import TimeExitManager
from strategy.risk.toxicity_gate import ToxicityGate
from strategy.profit_guard import ProfitGuard, ProfitGuardConfig
from learning.calibration import MultiHorizonCalibrator
from learning.online_learner import OnlineLearner
from learning.prediction_buffer import PredictionBuffer
from learning.batch_retrainer import BatchRetrainer, MIN_TRAIN_BARS as _MIN_TRAIN_BARS
from safety.circuit_breaker import CircuitBreaker
from safety.kill_switch import KillSwitch
from safety.emergency_exit import EmergencyExit
from logging_system.log_manager import log_manager
from utils.time_utils import (
    is_market_open, is_trading_day, get_time_zone, is_force_exit_time, is_new_entry_allowed,
)
from utils.notify import notify
from dashboard.main_dashboard import create_dashboard

# 대시보드 파라미터 바 이름 → 피처 키 매핑 (Fix2/3)
_PARAM_FEAT_MAP = {
    "CVD 다이버전스":  "cvd_divergence",
    "VWAP 위치":       "vwap_position",
    "OFI 불균형":      "ofi_norm",
    "외인 콜순매수":   "foreign_call_net",
    "다이버전스 지수": "foreign_retail_divergence",
    "프로그램 비차익": "program_non_arb_net",
}

EFFECT_MONITOR_HISTORY_PATH = os.path.join(BASE_DIR, "effect_monitor_history.json")
TP1_PROTECT_PLUS_ALPHA_PTS = 0.20
TP1_PROTECT_ATR_LOCK_MULT = 0.25


class TradingSystem:
    """미륵이 메인 트레이딩 시스템"""

    def __init__(self):
        logger.info("[System] 미륵이 초기화")
        log_manager.system("미륵이 초기화")

        # ── 키움 API 컴포넌트 ──────────────────────────────────
        self.broker        = create_broker()
        self.kiwoom        = self.broker.api  # legacy alias kept during migration
        self.latency_sync  = self.broker.create_latency_sync()
        self.realtime_data = None  # login 후 초기화

        # 핵심 컴포넌트
        self.regime_classifier  = RegimeClassifier()
        self.micro_regime_clf   = MicroRegimeClassifier()
        self.feature_builder    = FeatureBuilder()
        self.model             = MultiHorizonModel()
        self.ensemble          = EnsembleDecision()
        self._pt_value         = FUTURES_PT_VALUE   # connect_broker에서 종목코드 확정 후 갱신
        self.position          = PositionTracker(pt_value=self._pt_value)
        self.checklist         = EntryChecklist()
        self.sizer             = PositionSizer(account_balance=100_000_000)  # 기본 1억
        self.kelly             = AdaptiveKelly()
        self.time_exit         = TimeExitManager()
        self.online_learner    = OnlineLearner()
        self.horizon_calibrator = MultiHorizonCalibrator(list(HORIZONS.keys()))
        self.pred_buffer       = PredictionBuffer()
        self.meta_gate         = MetaGate()
        self.toxicity_gate     = ToxicityGate()
        self.batch_retrainer   = BatchRetrainer()
        self.investor_data     = self.broker.create_investor_data()  # connect_broker 후 api 주입
        # ── Phase 2 안전장치 ───────────────────────────────────
        self.emergency_exit  = EmergencyExit(
            position_tracker = self.position,
        )
        self.kill_switch     = KillSwitch(
            emergency_exit_callback = self.emergency_exit.execute
        )
        self.circuit_breaker = CircuitBreaker(
            emergency_exit_callback = self.emergency_exit.execute
        )
        self.profit_guard    = ProfitGuard()

        # 현재 레짐
        self.current_regime       = "NEUTRAL"
        self.current_micro_regime = "혼합"
        self._verified_today: int = 0        # 당일 SGD 검증 누적 건수
        self._efficacy_tick:  int = 0        # 5분마다 효과 검증 패널 갱신용
        self._last_block_reason: str = ""    # 직전 진입 차단 이유 (중복 로그 방지)
        self._last_recovery_ts:  str = ""    # 마지막 복구 처리 분봉 ts (동일 분봉 반복 방지)
        # [B57] CB③ 재시작 오발동 방지 — 이번 세션 시작 시각 (이전 세션 예측은 정확도 집계 제외)
        self._session_start_ts: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 재시작 시 이전 포지션 복원 (당일 데이터만)
        if self.position.load_state():
            msg = (
                f"[Position] 이전 포지션 복원: {self.position.status} "
                f"{self.position.quantity}계약 @ {self.position.entry_price} "
                f"(손절={self.position.stop_price:.2f})"
            )
            logger.warning(msg)           # SYSTEM 로그 파일 + 콘솔
            log_manager.system(msg, "WARNING")   # 대시보드 1 시스템 탭

        # ── 챔피언-도전자 Shadow 엔진 (대시보드 주입 전 먼저 초기화) ───
        self.challenger_engine = None  # type: ignore
        self.promotion_manager = None  # type: ignore
        try:
            from challenger.challenger_engine import ChallengerEngine
            from challenger.promotion_manager import PromotionManager
            self.challenger_engine  = ChallengerEngine()
            self.promotion_manager  = PromotionManager(
                db       = self.challenger_engine.db,
                registry = self.challenger_engine.registry,
            )
        except Exception as _ce:
            logger.warning("[Challenger] ChallengerEngine 초기화 실패 (비활성화): %s", _ce)

        # 대시보드
        self.dashboard = create_dashboard()
        self.dashboard.set_account_options(
            [_secrets.ACCOUNT_NO] if _secrets.ACCOUNT_NO else [],
            _secrets.ACCOUNT_NO,
        )
        self.dashboard.btn_save_account.clicked.connect(
            self._save_account_from_dashboard
        )
        self.dashboard.sig_position_restore.connect(self._manual_position_restore)
        self.dashboard.sig_balance_refresh_requested.connect(self._refresh_dashboard_balance)
        self.dashboard.sig_reverse_entry_toggled.connect(self._on_reverse_entry_toggled)
        self.dashboard.sig_manual_entry_requested.connect(self._on_manual_entry_requested)
        self.dashboard.sig_instant_exit_requested.connect(self._on_instant_exit_requested)
        self.dashboard.sig_auto_mode_changed.connect(self._on_auto_mode_changed)
        self.dashboard.sig_tp1_protect_mode_changed.connect(self._on_tp1_protect_mode_changed)
        self.dashboard.sig_manual_exit_requested.connect(self._on_manual_exit_requested)
        self.dashboard.set_ui_startup_mode()
        if self.challenger_engine is not None:
            try:
                self.dashboard.set_challenger_engine(
                    self.challenger_engine, self.promotion_manager
                )
            except Exception as _ce3:
                logger.warning("[Challenger] 대시보드 엔진 주입 실패: %s", _ce3)
        try:
            self.dashboard.set_profit_guard(self.profit_guard)
        except Exception as _pge:
            logger.warning("[ProfitGuard] 대시보드 주입 실패: %s", _pge)
        if self.position.status != "FLAT":
            self.dashboard.minute_chart_sync_active_position(
                self.position.status,
                self.position.entry_price,
                self.position.entry_time,
            )
        self._reverse_entry_enabled: bool = False
        self._tp1_protect_mode: str = "breakeven"
        self._auto_shutdown_done_today: bool = False
        self._skip_post_close_cycle_today: bool = False
        self._restore_reverse_entry_setting()
        self._restore_tp1_protect_mode_setting()
        self._restore_auto_shutdown_state()
        self._heartbeat_count: int = 0
        self._session_no: int = 0
        self._pending_order = None
        self._auto_entry_enabled: bool = True   # Auto On/Off 토글 상태
        self._manual_entry_ctx: dict = {}        # 마지막 파이프라인 산출값 (수동 진입 버튼용)
        self._last_order_event_key = None
        self._broker_sync_verified: bool = False
        self._broker_sync_block_new_entries: bool = True
        self._broker_sync_last_error: str = "startup sync not attempted"
        self._last_balance_result: dict = {}
        self._last_sizer_balance: float = 100_000_000.0
        self._effect_report_tick: int = 0
        self._entry_cooldown_until: object = None  # [B53] ENTRY 타임아웃 후 재진입 쿨다운
        self._exit_cooldown_until:  object = None  # 청산 후 즉각 재진입 차단 쿨다운
        self._shadow_ev = None  # [Phase2] ShadowEvaluator — 신버전 가상 실행

        # log_manager → 대시보드 5개 탭 배선 (subscribe 없으면 탭에 아무것도 안 보임)
        log_manager.subscribe(
            "SYSTEM",
            lambda e: self.dashboard.append_sys_log_tagged(e.message, e.level),
        )
        log_manager.subscribe(
            "TRADE",
            lambda e: self.dashboard.append_trade_log(e.message),
        )
        log_manager.subscribe(
            "LEARNING",
            lambda e: self.dashboard.append_model_log(e.message),
        )

    # ── 키움 API 연결 ─────────────────────────────────────────
    def _apply_account_no(self, account_no: str) -> None:
        account_no = str(account_no).strip()
        _secrets.ACCOUNT_NO = account_no
        if getattr(self, "_futures_code", ""):
            self.emergency_exit.set_order_manager(
                _BrokerOrderAdapter(self.broker, self._futures_code, account_no)
            )

    def _get_active_account_no(self) -> str:
        account_no = str(_secrets.ACCOUNT_NO or "").strip()
        try:
            selected = str(self.dashboard.get_selected_account() or "").strip()
        except Exception:
            selected = ""
        if selected:
            account_no = selected
        try:
            accounts = [str(x).strip() for x in (self.broker.get_account_list() or []) if str(x).strip()]
        except Exception:
            accounts = []
        if accounts and account_no not in accounts:
            account_no = accounts[0]
            self._apply_account_no(account_no)
        return account_no

    def _write_account_no_to_secrets(self, account_no: str) -> None:
        account_no = str(account_no).strip()
        secrets_path = os.path.join(BASE_DIR, "config", "secrets.py")
        try:
            with open(secrets_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        replaced = False
        for i, line in enumerate(lines):
            if line.lstrip().startswith("ACCOUNT_NO"):
                lines[i] = f'ACCOUNT_NO  = "{account_no}"\n'
                replaced = True
                break
        if not replaced:
            lines.insert(0, f'ACCOUNT_NO  = "{account_no}"\n')

        with open(secrets_path, "w", encoding="utf-8", newline="") as f:
            f.writelines(lines)

    def _save_account_from_dashboard(self) -> None:
        account_no = self.dashboard.get_selected_account().strip()
        if not account_no:
            msg = "[Account] 저장할 계좌번호가 비어 있습니다."
            logger.warning(msg)
            log_manager.system(msg, "WARNING")
            return
        if not account_no.isdigit() or len(account_no) != 10:
            msg = f"[Account] 계좌번호는 10자리 숫자여야 합니다: {account_no}"
            logger.warning(msg)
            log_manager.system(msg, "WARNING")
            return

        self._write_account_no_to_secrets(account_no)
        self._apply_account_no(account_no)
        msg = f"[Account] 주문 계좌번호 저장 완료: {account_no}"
        logger.info(msg)
        log_manager.system(msg)

    def _session_state_path(self) -> str:
        return os.path.join(BASE_DIR, "data", "session_state.json")

    def _read_session_state(self) -> dict:
        state_path = self._session_state_path()
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        try:
            if os.path.exists(state_path):
                with open(state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as exc:
            logger.warning("[SessionState] load failed: %s", exc)
        return {"date": datetime.date.today().isoformat(), "count": 0}

    def _write_session_state(self, data: dict) -> None:
        state_path = self._session_state_path()
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        try:
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as exc:
            logger.warning("[SessionState] save failed: %s", exc)

    def _restore_auto_shutdown_state(self) -> None:
        state = self._read_session_state()
        today = datetime.date.today().isoformat()
        self._auto_shutdown_done_today = (state.get("auto_shutdown_done_date") == today)
        self._skip_post_close_cycle_today = False
        now = datetime.datetime.now()
        if now.time() >= datetime.time(15, 40):
            state = self._read_session_state()
            if state.get("auto_shutdown_done_date") == now.date().isoformat():
                self._auto_shutdown_done_today = True
                self._skip_post_close_cycle_today = True
                self._daily_close_done = True
        if self._auto_shutdown_done_today and now.time() >= datetime.time(15, 40):
            self._skip_post_close_cycle_today = True
            self._daily_close_done = True
            log_manager.system(
                "[System] 오늘 자동 종료 이력이 있어 재시작 후 자동 종료/일일 마감 재실행을 건너뜁니다.",
                "WARNING",
            )

    def _restore_reverse_entry_setting(self) -> None:
        state = self._read_session_state()
        enabled = bool(state.get("reverse_entry_enabled", False))
        self._reverse_entry_enabled = enabled
        self.dashboard.set_reverse_entry_enabled(enabled, emit_signal=False)

    def _restore_tp1_protect_mode_setting(self) -> None:
        state = self._read_session_state()
        mode = str(state.get("tp1_single_contract_mode", "breakeven") or "breakeven").strip().lower()
        if mode not in {"breakeven", "breakeven_plus", "atr_profit"}:
            mode = "breakeven"
        self._tp1_protect_mode = mode
        self.dashboard.set_tp1_protect_mode(mode, emit_signal=False)

    def _on_manual_entry_requested(self, direction: str) -> None:
        """수동 진입 버튼(매수/매도) 클릭 처리."""
        ctx = self._manual_entry_ctx
        if not ctx:
            notify("수동 진입 불가: 파이프라인 데이터 없음 (첫 분봉 대기)", "WARNING")
            return
        if self.position.status != "FLAT":
            notify("수동 진입 불가: 이미 포지션 보유 중", "WARNING")
            return
        qty = ctx.get("qty", 0)
        if qty <= 0:
            notify("수동 진입 불가: 산출 수량 0 (등급 X 또는 신호 없음)", "WARNING")
            return
        if not self.circuit_breaker.is_entry_allowed():
            notify(f"수동 진입 불가: Circuit Breaker {self.circuit_breaker.state}", "WARNING")
            return
        price = ctx.get("price", 0.0)
        atr   = ctx.get("atr", 0.0)
        grade = ctx.get("grade", "C")
        log_manager.trade(
            f"[수동진입] 버튼 클릭 → {direction} {qty}계약 @ {price} 등급={grade}"
        )
        self._execute_entry(direction, price, qty, atr, grade)

    def _on_instant_exit_requested(self) -> None:
        """즉시청산 버튼 클릭 — 보유 포지션 전량 즉시 청산."""
        self._on_manual_exit_requested(100)

    def _on_auto_mode_changed(self, enabled: bool) -> None:
        """Auto On/Off 토글 — 자동 진입 활성화 여부 전환."""
        self._auto_entry_enabled = bool(enabled)
        log_manager.system(
            f"[EntryConfig] 자동진입={'ON' if enabled else 'OFF (수동 전환)'}",
            "WARNING" if not enabled else "INFO",
        )

    def _on_reverse_entry_toggled(self, enabled: bool) -> None:
        enabled = bool(enabled)
        self._reverse_entry_enabled = enabled
        state = self._read_session_state()
        state["reverse_entry_enabled"] = enabled
        self._write_session_state(state)
        log_manager.system(
            f"[EntryConfig] 역방향진입={'ON' if enabled else 'OFF'}",
            "WARNING" if enabled else "INFO",
        )

    def _on_tp1_protect_mode_changed(self, mode: str) -> None:
        mode = str(mode or "breakeven").strip().lower()
        if mode not in {"breakeven", "breakeven_plus", "atr_profit"}:
            mode = "breakeven"
        self._tp1_protect_mode = mode
        state = self._read_session_state()
        state["tp1_single_contract_mode"] = mode
        self._write_session_state(state)
        labels = {
            "breakeven": "TP1 본절보호",
            "breakeven_plus": "본절+alpha",
            "atr_profit": "ATR 기반 보호이익",
        }
        log_manager.system(
            f"[ExitConfig] 1계약 TP1 보호전환 모드 -> {labels.get(mode, mode)}",
            "WARNING",
        )

    def _on_manual_exit_requested(self, percent: int) -> None:
        percent = int(percent or 0)
        if self.position.status == "FLAT" or self.position.quantity <= 0:
            log_manager.system("[ManualExit] 포지션이 없어 수동 청산을 무시했습니다.", "WARNING")
            return
        if self._has_pending_order():
            log_manager.system("[ManualExit] 미체결 주문이 있어 수동 청산을 보류했습니다.", "WARNING")
            return

        total_qty = int(self.position.quantity or 0)
        is_full_close = percent >= 100 or total_qty <= 1
        send_qty = total_qty
        if not is_full_close:
            send_qty = max(1, round(total_qty * (percent / 100.0)))
            if send_qty >= total_qty:
                is_full_close = True
                send_qty = total_qty

        price_hint = float(getattr(self, "_last_pipeline_price", 0.0) or self.position.entry_price or 0.0)
        if is_full_close:
            reason = "수동 전량청산" if percent >= 100 else f"수동 청산 {percent}%→전량"
            kind = "EXIT_FULL"
        else:
            reason = f"수동 부분청산 {percent}%"
            kind = "EXIT_MANUAL_PARTIAL"

        ret = self._send_kiwoom_exit_order(send_qty)
        if ret != 0:
            log_manager.system(
                f"[ManualExit] 주문 실패 ret={ret} pct={percent} qty={send_qty}",
                "ERROR",
            )
            return

        self._set_pending_order(
            kind=kind,
            direction=self.position.status,
            qty=send_qty,
            price_hint=round(price_hint, 2),
            reason=reason,
        )
        log_manager.system(
            f"[ManualExit] 요청 pct={percent} send_qty={send_qty} kind={kind} position={self.position.status}",
            "WARNING",
        )
        log_manager.trade(
            f"[주문요청] {reason} {self.position.status} {send_qty}계약 @ {price_hint:.2f} 체결대기"
        )

    def _resolve_entry_direction(self, raw_direction: str) -> tuple:
        reverse_enabled = bool(self._reverse_entry_enabled)
        final_direction = raw_direction
        if reverse_enabled:
            if raw_direction == "LONG":
                final_direction = "SHORT"
            elif raw_direction == "SHORT":
                final_direction = "LONG"
        return raw_direction, final_direction, reverse_enabled

    @staticmethod
    def _direction_to_korean(direction: str) -> str:
        if direction == "LONG":
            return "매수"
        if direction == "SHORT":
            return "매도"
        return "관망"

    def _trade_metrics_pair(self, result: dict) -> tuple:
        executed_metrics = normalize_trade_pnl(
            entry_price=result["entry_price"],
            quantity=result["quantity"],
            pnl_pts=result["pnl_pts"],
        )
        forward_metrics = normalize_trade_pnl(
            entry_price=result["entry_price"],
            quantity=result["quantity"],
            pnl_pts=result.get("forward_pnl_pts", result["pnl_pts"]),
        )
        return executed_metrics, forward_metrics

    def _record_trade_result(self, result: dict, exit_ts: str = None) -> None:
        now_str = exit_ts or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not is_plausible_futures_trade(
            entry_price=result.get("entry_price"),
            exit_price=result.get("exit_price"),
            quantity=result.get("quantity"),
            pnl_pts=result.get("pnl_pts"),
        ):
            log_manager.system(
                "[TradeGuard] implausible futures trade skipped "
                f"entry={result.get('entry_price')} exit={result.get('exit_price')} "
                f"qty={result.get('quantity')} pnl_pts={result.get('pnl_pts')}",
                "CRITICAL",
            )
            return
        executed_metrics, forward_metrics = self._trade_metrics_pair(result)
        execute(
            TRADES_DB,
            """INSERT INTO trades
               (entry_ts, exit_ts, direction, raw_direction, executed_direction,
                reverse_entry_enabled, entry_price, exit_price, quantity,
                pnl_pts, pnl_krw, gross_pnl_krw, commission_krw, net_pnl_krw,
                forward_pnl_pts, forward_pnl_krw, forward_gross_pnl_krw,
                forward_commission_krw, forward_net_pnl_krw,
                formula_version, exit_reason, grade, regime)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result.get("entry_ts", now_str),
                result.get("exit_ts", now_str),
                result["direction"],
                result.get("raw_direction", result["direction"]),
                result.get("executed_direction", result["direction"]),
                1 if result.get("reverse_entry_enabled", False) else 0,
                result["entry_price"],
                result["exit_price"],
                result["quantity"],
                result["pnl_pts"],
                executed_metrics["net_pnl_krw"],
                executed_metrics["gross_pnl_krw"],
                executed_metrics["commission_krw"],
                executed_metrics["net_pnl_krw"],
                result.get("forward_pnl_pts", result["pnl_pts"]),
                forward_metrics["net_pnl_krw"],
                forward_metrics["gross_pnl_krw"],
                forward_metrics["commission_krw"],
                forward_metrics["net_pnl_krw"],
                executed_metrics["formula_version"],
                result["exit_reason"],
                result.get("grade", ""),
                self.current_regime,
            ),
        )

    def _set_pending_order(
        self,
        kind: str,
        direction: str,
        qty: int,
        price_hint: float,
        reason: str,
        *,
        atr: float = 0.0,
        grade: str = "",
        stage=None,
        raw_direction: str = None,
        reverse_entry_enabled: bool = False,
    ) -> None:
        self._pending_order = {
            "kind": kind,
            "direction": direction,
            "raw_direction": raw_direction or direction,
            "reverse_entry_enabled": bool(reverse_entry_enabled),
            "qty": qty,
            "price_hint": price_hint,
            "reason": reason,
            "atr": atr,
            "grade": grade,
            "stage": stage,
            "order_no": "",
            "filled_qty": 0,
            "created_at": datetime.datetime.now(),
            "requested_at": datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "account_no": str(_secrets.ACCOUNT_NO or "").strip(),
            "code": getattr(self, "_futures_code", ""),
            "position_before": (
                "FLAT" if self.position.status == "FLAT"
                else f"{self.position.status} {self.position.quantity}계약 @ {self.position.entry_price:.2f}"
            ),
        }
        logger.warning("[PendingOrder] set %s", self._pending_order)

    def _clear_pending_order(self) -> None:
        if self._pending_order is not None:
            logger.warning("[PendingOrder] clear %s", self._pending_order)
            # [B56] ENTRY 미체결 소멸 → 어떤 경로든 2분 재진입 금지
            # B52 timeout / balance Chejan FLAT / 주문 거부 등 모든 경로 커버
            if (self._pending_order.get("kind") == "ENTRY"
                    and self._pending_order.get("filled_qty", 0) == 0):
                self._entry_cooldown_until = (
                    datetime.datetime.now() + datetime.timedelta(minutes=2)
                )
                logger.warning(
                    "[EntryCooldown] ENTRY 미체결 소멸 → 2분 재진입 금지 until %s",
                    self._entry_cooldown_until.strftime("%H:%M:%S"),
                )
        self._pending_order = None

    def _has_pending_order(self) -> bool:
        return self._pending_order is not None

    def _normalize_broker_code(self, code: str) -> str:
        code = str(code or "").strip()
        if code.startswith(("A", "J")) and len(code) > 1:
            code = code[1:]
        return code

    def _sync_position_from_broker(self) -> None:
        account_no = str(_secrets.ACCOUNT_NO or "").strip()
        code = self._normalize_broker_code(getattr(self, "_futures_code", ""))
        if not account_no or not code:
            return

        before = (
            "FLAT" if self.position.status == "FLAT"
            else f"{self.position.status} {self.position.quantity}계약 @ {self.position.entry_price:.2f}"
        )
        result = self.broker.request_futures_balance(account_no)
        if result is None:
            log_manager.system("[BrokerSync] 브로커 잔고 TR 조회 실패로 startup sync를 건너뜁니다.", "WARNING")
            return

        rows = result.get("rows") or []
        broker_row = None
        for row in rows:
            row_code = self._normalize_broker_code(
                row.get("종목코드") or row.get("code") or ""
            )
            if row_code == code:
                broker_row = row
                break

        if not broker_row:
            if self.position.status != "FLAT":
                self.position.sync_flat_from_broker()
                self.dashboard.minute_chart_clear_active_position()
                self._clear_pending_order()
                log_manager.system(
                    f"[BrokerSync] startup sync: 브로커 잔고 없음 -> {before} => FLAT",
                    "CRITICAL",
                )
            else:
                log_manager.system("[BrokerSync] startup sync: 브로커/로컬 모두 FLAT")
            return

        qty_text = (
            broker_row.get("잔고수량")
            or "0"
        )
        price_text = (
            broker_row.get("매입단가")
            or broker_row.get("현재가")
            or broker_row.get("평가금액")
            or "0"
        )
        side_text = broker_row.get("매매구분", "")

        try:
            qty = int(str(qty_text).replace(",", "").strip() or "0")
        except ValueError:
            qty = 0
        try:
            avg_price = float(str(price_text).replace(",", "").strip() or "0")
        except ValueError:
            avg_price = 0.0

        side = _ts_order_side_to_direction(side_text)
        if qty <= 0 or side not in ("LONG", "SHORT"):
            log_manager.system(
                f"[BrokerSync] startup sync 응답 해석 실패 code={code} qty={qty_text} side={side_text}",
                "WARNING",
            )
            return

        self.position.sync_from_broker(
            direction=side,
            price=avg_price,
            quantity=qty,
            atr=max(_ts_get_reference_atr(self), 0.5),
            grade="BROKER",
            regime=self.current_regime or "BROKER_SYNC",
        )
        self.dashboard.minute_chart_sync_active_position(
            side,
            avg_price,
            self.position.entry_time,
        )
        self._clear_pending_order()
        after = f"{self.position.status} {self.position.quantity}계약 @ {self.position.entry_price:.2f}"
        log_manager.system(
            f"[BrokerSync] startup sync 완료: {before} -> {after}",
            "CRITICAL" if before != after else "INFO",
        )

    def _apply_horizon_calibration(self, horizon_proba: dict) -> dict:
        calibrated = {}
        for horizon, probs in horizon_proba.items():
            res = dict(probs)
            direction = int(res.get("direction", 0))
            raw_conf = float(res.get("confidence", 1 / 3) or 1 / 3)
            cal_conf = float(self.horizon_calibrator.calibrate(horizon, raw_conf))

            up = float(res.get("up", 1 / 3) or 1 / 3)
            down = float(res.get("down", 1 / 3) or 1 / 3)
            flat = float(res.get("flat", 1 / 3) or 1 / 3)

            if direction == 1:
                other_total = max(down + flat, 1e-9)
                up = cal_conf
                down = (down / other_total) * max(0.0, 1.0 - cal_conf)
                flat = (flat / other_total) * max(0.0, 1.0 - cal_conf)
            elif direction == -1:
                other_total = max(up + flat, 1e-9)
                down = cal_conf
                up = (up / other_total) * max(0.0, 1.0 - cal_conf)
                flat = (flat / other_total) * max(0.0, 1.0 - cal_conf)
            else:
                other_total = max(up + down, 1e-9)
                flat = cal_conf
                up = (up / other_total) * max(0.0, 1.0 - cal_conf)
                down = (down / other_total) * max(0.0, 1.0 - cal_conf)

            best = max([(up, 1), (down, -1), (flat, 0)], key=lambda item: item[0])
            calibrated[horizon] = {
                "up": round(up, 4),
                "down": round(down, 4),
                "flat": round(flat, 4),
                "direction": best[1],
                "confidence": round(best[0], 4),
            }
        return calibrated

    def connect_broker(self) -> bool:
        """로그인 + 근월물 실시간 수신 등록."""
        print("[DBG CK-1] login() 호출 직전", flush=True)
        if not self.broker.connect():
            logger.error("[System] 키움 로그인 실패")
            return False
        self.broker.register_fill_callback(self._on_chejan_event)
        self.broker.register_msg_callback(self._on_order_message)
        self.kiwoom = self.broker.api
        acc_raw = self.broker.get_login_info("ACCNO")
        accounts = self.broker.get_account_list()
        selected_account = str(_secrets.ACCOUNT_NO or "").strip()
        if accounts and selected_account not in accounts:
            fallback_account = str(accounts[0]).strip()
            logger.warning(
                "[Account] configured account %s not in broker session accounts=%s; using %s",
                selected_account,
                accounts,
                fallback_account,
            )
            selected_account = fallback_account
            self._apply_account_no(selected_account)
        logger.info("[Account] ACCNO raw=%s", acc_raw)
        logger.info("[Account] parsed accounts=%s", accounts)
        self.dashboard.set_account_options(accounts, selected_account)
        print("[DBG CK-2] login() 성공", flush=True)

        # 서버 종류 확인 (정보 로그용)
        _broker_name = getattr(self.broker, "name", "")
        if _broker_name == "cybos":
            server_label = "Cybos 실서버"
        else:
            server = self.broker.get_login_info("GetServerGubun")
            server_label = "모의투자" if server == "1" else "실서버"
            if server == "1":
                logger.info("[System] 모의투자 서버 접속 — A0166000 SetRealReg 실시간 수신 사용")
        print(f"[DBG CK-2b] broker={_broker_name!r} 서버종류={server_label}", flush=True)

        # 종목코드 결정: Cybos 실제 코드는 5자 (예: A0166, A0565)
        # 대시보드 UI 코드는 8자 (예: A0166000, A0565000) — 끝 3자리 "000" 제거로 정규화
        broker_code = self.broker.get_nearest_futures_code()
        try:
            ui_code_raw = str(self.dashboard.get_selected_symbol() or "").strip()
        except Exception:
            ui_code_raw = ""
        # 8자 코드(Axxxx000) → 5자 Cybos 코드(Axxxx)로 정규화
        if len(ui_code_raw) == 8 and ui_code_raw.endswith("000"):
            ui_code = ui_code_raw[:-3]
        else:
            ui_code = ui_code_raw

        # 미니선물 여부: A05... 또는 05... 접두사로 판단
        _ui_norm = ui_code[1:] if ui_code.startswith("A") else ui_code
        is_mini_selected = _ui_norm.startswith("05")

        if is_mini_selected:
            # 미니선물: UI 코드 우선, 없으면 FutureMst 프로브 근월물
            # broker_code는 CpFutureCode 기반 일반선물(A01xxx) 전용이므로 사용 불가
            if not ui_code:
                ui_code = self.broker.get_nearest_mini_futures_code()
            code = ui_code
        else:
            # 일반선물: CpFutureCode 반환 5자 코드 우선
            code = broker_code or ui_code
        print(
            f"[DBG CK-3] 근월물 코드={code} (broker={broker_code} ui_raw={ui_code_raw!r} "
            f"ui={ui_code!r} is_mini={is_mini_selected}) 서버={server_label}",
            flush=True,
        )
        self._futures_code = code
        # 계약 스펙 확정 (일반선물 250,000 / 미니선물 50,000)
        _spec = get_contract_spec(code)
        self._pt_value = _spec["pt_value"]
        self.position.set_pt_value(self._pt_value)
        self.position.set_futures_code(code)
        if hasattr(self, "exit_manager"):
            self.exit_manager.set_pt_value(self._pt_value)
        if hasattr(self, "entry_manager"):
            self.entry_manager._sizer.set_pt_value(self._pt_value)
        self.sizer.set_pt_value(self._pt_value)
        print(f"[DBG CK-3b] 계약스펙={_spec['label']} pt_value={self._pt_value:,}", flush=True)

        # [안전] 재시작 시 저장 포지션 종목코드 검증 — 불일치 시 강제 FLAT
        _saved_pos_code = getattr(self.position, "_loaded_futures_code", "")
        if _saved_pos_code and _saved_pos_code != code and self.position.status != "FLAT":
            _mismatch_msg = (
                f"[PositionCodeMismatch] CRITICAL: 저장 포지션 코드({_saved_pos_code}) ≠ "
                f"현재 코드({code}) — 포지션 강제 FLAT. HTS에서 {_saved_pos_code} 잔고 수동 확인 필요."
            )
            logger.critical(_mismatch_msg)
            log_manager.system(_mismatch_msg, "CRITICAL")
            self.position.force_flat("code_mismatch_on_restart")

        self.emergency_exit.set_futures_code(code)
        self.emergency_exit.set_order_manager(
            _BrokerOrderAdapter(self.broker, code, selected_account)
        )
        self._sync_position_from_broker()

        self.realtime_data = self.broker.create_realtime_data(
            code             = code,
            screen_no        = "3000",
            on_candle_closed = self._on_candle_closed,
            on_tick          = self._on_tick_price_update,
            on_hoga          = self._on_hoga_update,
            realtime_code    = code,
            is_mock_server   = False,
        )
        print("[DBG CK-4] RealtimeData 생성 완료", flush=True)

        self.realtime_data.start(load_history=True)
        print("[DBG CK-5] RealtimeData.start() 완료", flush=True)

        self.investor_data._api = self.broker.api  # 실거래 시 TR 폴링 활성화
        self.investor_data.set_futures_code(code)   # UI 선택 종목코드 반영

        # 투자자ticker 실시간 타입 FID·코드 탐색 (진단용)
        # 결과는 PROBE.log 및 콘솔에 [PROBE-TICKER] 라인으로 출력됨
        # 확인 후 불필요하면 이 줄을 제거해도 됨
        self.broker.probe_investor_ticker(extra_codes=[code])

        # 수급 TR은 COM 콜백 체인(run_minute_pipeline) 밖에서 수집해야 스택 오버런 방지
        # QTimer 60초마다 독립 실행 — 파이프라인은 캐시(get_features)만 읽음
        self._investor_timer = QTimer()
        self._investor_timer.timeout.connect(self._fetch_investor_data)
        self._investor_timer.start(60_000)

        logger.info("[System] %s 실시간 수신 시작 — %s | 수급 타이머 60s 시작", self.broker.name, code)
        return True

    def connect_kiwoom(self) -> bool:
        return self.connect_broker()

    def _fetch_investor_data(self) -> None:
        """수급 TR 수집 — QTimer에서 호출 (COM 콜백 체인 외부)."""
        if not is_market_open(datetime.datetime.now()):
            return
        try:
            self.investor_data.fetch_all()
            # FutureCurOnly 틱에서 실시간으로 수집된 미결제약정 동기화
            rt = getattr(self, "realtime_data", None)
            if rt is not None:
                oi = getattr(rt, "_last_oi", 0)
                if oi > 0:
                    self.investor_data._open_interest = oi
        except Exception as e:
            logger.warning("[Investor] 타이머 수집 오류: %s", e)

    def _on_tick_price_update(self, bar: dict) -> None:
        """틱 수신마다 대시보드 헤더 현재가 갱신."""
        if self.realtime_data is None:
            return
        close = float(bar.get("close", 0) or 0.0)
        if close > 0:
            self._last_pipeline_price = close
            self.dashboard.minute_chart_tick(close, bar.get("ts"))
        self.dashboard.update_price(
            price  = bar["close"],
            change = bar["close"] - bar.get("open", bar["close"]),
            code   = self.realtime_data.code,
        )

    def _on_hoga_update(
        self,
        bid1: float,
        ask1: float,
        bid_qty: int,
        ask_qty: int,
        snapshot: Optional[dict] = None,
    ) -> None:
        """선물호가잔량 이벤트마다 미세구조 feature 누적."""
        self.feature_builder.update_hoga(
            bid1=bid1,
            ask1=ask1,
            bid_qty=bid_qty,
            ask_qty=ask_qty,
            snapshot=snapshot,
        )

    def _on_candle_closed(self, candle: dict) -> None:
        """분봉 완성 콜백 — Qt 이벤트 스레드에서 호출됨."""
        now = datetime.datetime.now()
        if not is_market_open(now):
            return

        self._last_recovery_ts = ""   # 실분봉 수신 시에만 복구 ts 초기화
        # latency → Circuit Breaker 연동
        self.circuit_breaker.record_api_latency(self.latency_sync.offset_sec)
        self.dashboard.minute_chart_candle_closed(candle)
        self.run_minute_pipeline(candle)

    # ── 장 전 준비 (08:50) ─────────────────────────────────────
    def pre_market_setup(self):
        """매크로 수집 + 레짐 판단"""
        logger.info("[System] 장 전 매크로 수집 시작")
        log_manager.system("장 전 매크로 수집 시작")

        # TODO Phase 1 Week 1: 실제 매크로 데이터 수집 구현
        # 현재는 더미 데이터로 초기화
        macro_dummy = {
            "vix": 18.5,
            "sp500_chg_pct": 0.3,
            "nasdaq_chg_pct": 0.4,
            "usd_krw_chg_pct": -0.1,
            "us10y_chg": 2.0,
        }

        result = self.regime_classifier.classify(**macro_dummy)
        self.current_regime = result["regime"]

        logger.info(f"[System] 레짐 확정: {self.current_regime} | {result['description']}")
        log_manager.system(f"레짐: {self.current_regime} | {result['description']}")
        notify(f"장 전 레짐: {self.current_regime}", "INFO")

        self.dashboard.update_supply_macro(
            vix=macro_dummy["vix"],
            sp500_chg=macro_dummy["sp500_chg_pct"] / 100,
            regime=self.current_regime,
        )
        self.dashboard.append_sys_log(
            f"레짐 확정: {self.current_regime} | {result['description']}"
        )
        self.dashboard.set_ui_ready_mode()

    # ── 매분 파이프라인 ────────────────────────────────────────
    def run_minute_pipeline(self, bar: dict):
        """
        매분 실행되는 9단계 파이프라인

        Args:
            bar: {ts, open, high, low, close, volume, buy_vol, sell_vol,
                  bid_price, ask_price, bid_qty, ask_qty}
        """
        ts_raw = bar.get("ts", datetime.datetime.now())
        ts     = ts_raw.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts_raw, "strftime") else str(ts_raw)

        # ── 분봉 데이터 유효성 가드 ───────────────────────────────
        # 비정상 분봉이 피처/진입/청산 오발동을 일으키지 않도록 파이프라인 앞단 차단
        _c = float(bar.get("close", 0))
        _h = float(bar.get("high",  0))
        _l = float(bar.get("low",   0))
        _v = int(bar.get("volume",  0))

        if _c <= 0 or _h <= 0 or _l <= 0:
            log_manager.system(
                f"[Guard-C1] 비정상 가격 분봉 차단 — close={_c} high={_h} low={_l} ({ts})",
                "WARNING",
            )
            self.dashboard.notify_pipeline_ran()   # 워치독 카운터 리셋
            return

        if _h < _l:
            log_manager.system(
                f"[Guard-C2] 고가<저가 역전 분봉 차단 — high={_h} low={_l} ({ts})",
                "WARNING",
            )
            self.dashboard.notify_pipeline_ran()   # 워치독 카운터 리셋
            return

        _bar_volume_zero = (_v == 0)
        if _bar_volume_zero:
            log_manager.system(
                f"[Guard-C3] volume=0 분봉 — VWAP/CVD 신호 신뢰도 저하, 진입 보류 ({ts})",
                "WARNING",
            )

        close  = _c
        self._last_pipeline_price = close  # 잔고 UI 합성에 사용

        # 대시보드 실시간 가격 동기화
        self.dashboard.update_price(
            price  = close,
            change = close - bar.get("open", close),
            code   = self.realtime_data.code if self.realtime_data else "",
        )

        # ── PendingOrder 타임아웃 체크 ────────────────────────────
        # [B55] 접수 상태(order_no 확인) vs 미접수(order_no="")를 분리:
        #   미접수: 60s → Kiwoom 서버에 주문 자체가 없는 것으로 간주 (빠른 폐기)
        #   접수됨: 300s → 모의투자 지연 체결 허용, 장시간 미체결 시에만 폐기
        if self._pending_order is not None:
            _pending_age = (datetime.datetime.now() - self._pending_order["created_at"]).total_seconds()
            _has_order_no = bool(self._pending_order.get("order_no", ""))
            _timeout_s = 300 if _has_order_no else 60
            if getattr(getattr(self, "broker", None), "name", "") == "cybos" and not _has_order_no:
                # Cybos mock can delay the first acceptance callback well beyond
                # the Kiwoom-oriented 60s timeout.
                _timeout_s = 180
            if _pending_age > _timeout_s and self._pending_order.get("filled_qty", 0) == 0:
                _accepted_label = f"접수확인(order_no={self._pending_order['order_no']})" if _has_order_no else "미접수"
                # [B52] ENTRY 타임아웃: 낙관적 포지션 복원 + 쿨다운
                if self._pending_order.get("kind") == "ENTRY":
                    if getattr(self.position, "_optimistic", False):
                        # 낙관적 오픈 상태면 포지션을 FLAT으로 복원
                        log_manager.system(
                            f"[FixB] ENTRY 타임아웃 → 낙관적 포지션 FLAT 복원 "
                            f"(direction={self.position.status} entry_price={self.position.entry_price:.2f} {_accepted_label})",
                            "WARNING",
                        )
                        self.position._reset_position()
                    # [B53] 쿨다운은 _optimistic 여부와 무관하게 항상 설정
                    # _clear_pending_order()에서도 설정되지만 여기서 먼저 설정해 STEP 7 차단 보장
                    self._entry_cooldown_until = datetime.datetime.now() + datetime.timedelta(minutes=2)
                    log_manager.system(
                        f"[EntryCooldown] ENTRY 타임아웃 후 2분 재진입 금지 "
                        f"(until {self._entry_cooldown_until.strftime('%H:%M:%S')})",
                        "WARNING",
                    )
                log_manager.system(
                    f"[PendingOrder] 타임아웃 {_pending_age:.0f}s ({_accepted_label}) — "
                    f"kind={self._pending_order['kind']} dir={self._pending_order['direction']} "
                    f"order_no={self._pending_order.get('order_no','?') or '?'} → 주문 소멸 처리",
                    "WARNING",
                )
                self._clear_pending_order()

        log_manager.signal(f"--- {ts} 분봉 파이프라인 시작 ---")

        # ── STEP 1: 과거 예측 검증 ─────────────────────────────
        verified = self.pred_buffer.verify_and_update(ts, close)
        self._verified_today += len(verified)
        for v in verified:
            # CB③ 정확도 집계 조건 (30분 호라이즌 전용):
            #  1) 30분 호라이즌만 — CB③ 정의가 "30분 정확도"이므로 전 호라이즌 혼입 금지
            #  2) bootstrap 1/3 균등 예측(confidence≈0.333) 제외
            #  3) [B57] 이번 세션 시작 이전 예측 제외 — 재시작 시 이전 세션 예측이
            #     대량 검증되어 accuracy_buf 즉시 충전 → CB③ 오발동 방지
            _conf = v.get("confidence", 0.0) or 0.0
            _pred_ts = v.get("ts", "") or ""
            if (v["horizon"] == "30m"
                    and _conf > 0.38
                    and _pred_ts >= self._session_start_ts):
                self.circuit_breaker.record_accuracy(v["correct"])
            self.horizon_calibrator.record(v["horizon"], _conf, v["correct"])
            if v["correct"]:
                log_manager.learning(f"✓ {v['horizon']} 예측 적중 (conf={_conf:.1%})")
            else:
                log_manager.learning(f"✗ {v['horizon']} 예측 실패 (conf={_conf:.1%})")

        # ── STEP 2: SGD 온라인 자가학습 ────────────────────────
        # STEP 1 검증된 예측마다 해당 시점 피처로 즉시 partial_fit
        for v in verified:
            _meta_feats = v.get("features") or {}
            try:
                _meta_eval = self.meta_gate.evaluate(
                    direction=v["predicted"],
                    confidence=float(v.get("confidence", 0.0) or 0.0),
                    regime=self.current_regime,
                    micro_regime=self.current_micro_regime,
                    features=_meta_feats,
                    now=datetime.datetime.strptime(v["ts"], "%Y-%m-%d %H:%M:%S"),
                    recent_accuracy=self.online_learner.recent_accuracy(),
                )
                self.meta_gate.record_outcome(
                    _meta_eval.get("meta_features", []),
                    bool(v["correct"]),
                )
            except Exception as _meta_record_err:
                logger.debug("[MetaGate] verify record skip: %s", _meta_record_err)

        if self.model.feature_names and verified:
            for v in verified:
                feat_dict = v.get("features") or {}
                x = np.array(
                    [feat_dict.get(f, 0.0) for f in self.model.feature_names],
                    dtype=np.float32,
                )
                self.online_learner.learn(
                    horizon         = v["horizon"],
                    x               = x,
                    actual_label    = v["actual"],
                    predicted_label = v["predicted"],
                )
            log_manager.learning(
                f"[SGD] {len(verified)}건 학습 | "
                f"SGD비중={self.online_learner.sgd_weight:.0%} "
                f"50분정확도={self.online_learner.recent_accuracy():.1%}"
            )

        # ── STEP 3: GBM 배치 재학습 (주간/월간 스케줄 확인) ────
        if (self.batch_retrainer.should_retrain_weekly()
                or self.batch_retrainer.should_retrain_monthly()):
            self.dashboard.set_model_status("GBM 재학습중...")
            result = self.batch_retrainer.retrain_now()
            if result.get("ok"):
                self.model._load_all()   # 새 모델 즉시 반영
                log_manager.learning(
                    f"[GBM] 배치 재학습 완료 | {result['elapsed_sec']}초 "
                    f"데이터={result['data_size']}행"
                )
                notify("GBM 배치 재학습 완료", "INFO")
                self.dashboard.set_model_status(
                    "GBM 재학습 완료", f"데이터 {result['data_size']}행"
                )
            else:
                log_manager.learning(f"[GBM] 재학습 건너뜀: {result.get('error','')}")

        # ── STEP 4: 피처 생성 ──────────────────────────────────
        # fetch_all()은 _investor_timer(60s QTimer)에서 COM 콜백 외부로 실행
        # 파이프라인은 이전 분봉에서 수집된 캐시를 읽음 (당일 누적 수급 — 1분 지연 허용)
        supply_feats = self.investor_data.get_features()
        features = self.feature_builder.build(bar, supply_demand=supply_feats)
        # 최소 0.5pt 보장 — 재시작 직후 1개 틱만으로 계산된 비정상 소ATR 방어
        atr      = max(features.get("atr", 0.5), 0.5)
        atr_ratio = features.get("atr_ratio", 1.0)

        # ── CORE 3종 피처 NaN/Inf 가드 ──────────────────────────
        # 진입 체크리스트가 직접 사용하는 피처만 방어 (다른 피처는 앙상블에서 0으로 처리됨)
        for _fk in ("vwap_position", "cvd_direction", "ofi_pressure"):
            _fv = features.get(_fk)
            if _fv is None or (isinstance(_fv, float) and (math.isnan(_fv) or math.isinf(_fv))):
                log_manager.system(
                    f"[Guard-F1] {_fk} 비정상값({_fv}) → 0 교정 ({ts})", "WARNING"
                )
                features[_fk] = 0

        # 분봉·피처 원본 저장 (경로 B 학습 데이터 축적)
        save_candle(bar)
        save_features(ts, features)

        # [§19] RegimeFingerprint — PSI 기반 피처 분포 드리프트 감지 (STEP 4 직후)
        try:
            from strategy.regime_fingerprint import get_fingerprint as _get_fp
            _fp      = _get_fp()
            _fp_psi  = _fp.update_live(features)
            _fp_lv   = _fp.get_level()
            if _fp_psi > 0.30:
                log_manager.system(
                    f"[RegimeFingerprint] PSI={_fp_psi:.3f} CRITICAL — "
                    f"시장 구조 변화 감지, 신규 진입 차단 검토",
                    "WARNING",
                )
            elif _fp_psi > 0.20:
                log_manager.system(
                    f"[RegimeFingerprint] PSI={_fp_psi:.3f} ALARM — "
                    f"param_optimizer 예약 권장",
                    "WARNING",
                )
            # 대시보드 strategy_ops 탭에 PSI 수준 실시간 반영
            self.dashboard.update_strategy_ops({
                "psi_val":   _fp_psi,
                "psi_level": _fp_lv,
            })
        except Exception as _fp_e:
            logger.debug("[RegimeFingerprint] 스킵: %s", _fp_e)

        # GBM 미학습 시 피처명 부트스트랩 → SGD 학습 활성화
        if not self.model.feature_names and features:
            self.model.set_feature_names(sorted(features.keys()))

        # 다이버전스 패널 갱신 (외인·개인 수급)
        _inv = self.investor_data
        _fi_call  = _inv._call.get("foreign", 0)
        _fi_put   = _inv._put.get("foreign", 0)
        _rt_call  = _inv._call.get("individual", 0)
        _rt_put   = _inv._put.get("individual", 0)
        _fi_fut   = _inv._futures.get("foreign", 0)
        _rt_fut   = _inv._futures.get("individual", 0)
        _inst_call = _inv._call.get("institution", 0)
        _inst_put  = _inv._put.get("institution", 0)
        _rt_opt_total = max(abs(_rt_call) + abs(_rt_put), 1)
        _fi_opt_total = max(abs(_fi_call) + abs(_fi_put), 1)
        _rt_bias = (_rt_call - _rt_put) / _rt_opt_total
        _fi_bias = (_fi_call - _fi_put) / _fi_opt_total
        _contrarian = ("역발상 하락" if _rt_bias > 0.3 else
                       "역발상 상승" if _rt_bias < -0.3 else "중립")
        self.dashboard.update_divergence({
            "rt_bias":     _rt_bias,
            "fi_bias":     _fi_bias,
            "rt_call":     _rt_call,
            "rt_put":      _rt_put,
            "rt_strd":     abs(_rt_call) + abs(_rt_put),
            "fi_call":     _fi_call,
            "fi_put":      _fi_put,
            "fi_strangle": abs(_fi_call) + abs(_fi_put),
            "contrarian":  _contrarian,
            "div_score":   float(_fi_fut - _rt_fut),
            "zones":       _inv.get_zone_data(),
        })
        if hasattr(_inv, "get_panel_data"):
            self.dashboard.update_divergence(_inv.get_panel_data())

        # [DBG-F4] ATR floor 적용 전후 + 핵심 피처 원시값 확인
        debug_log.debug(
            "[DBG-F4] ts=%s close=%.2f | ATR raw=%.4fpt → floor=%.4fpt"
            " | cvd_dir=%+d ofi=%+d vwap_pos=%.4f hurst=%.3f vol=%d"
            " | bid=%.2f ask=%.2f buyvol=%d sllvol=%d",
            ts, close,
            features.get("atr", 0.0), atr,
            int(features.get("cvd_direction", 0)),
            int(features.get("ofi_pressure", 0)),
            features.get("vwap_position", 0.0),
            features.get("hurst", 0.5),
            bar.get("volume", 0),
            bar.get("bid1", 0.0), bar.get("ask1", 0.0),
            bar.get("buy_vol", 0), bar.get("sell_vol", 0),
        )

        # 미시 레짐 업데이트 (v6.5) — MicroRegimeClassifier: ADX 자체 계산
        _mr = self.micro_regime_clf.push_1m_candle(
            high             = float(bar.get("high", close) or close),
            low              = float(bar.get("low",  close) or close),
            close            = close,
            cvd_exhaustion   = float(features.get("cvd_exhaustion",  0.0) or 0.0),
            ofi_reversal_speed = float(features.get("ofi_reversal_speed", 0.0) or 0.0),
            vwap_position    = float(features.get("vwap_position",   0.0) or 0.0),
        )
        self.current_micro_regime = _mr["regime"]
        self.dashboard.update_micro_regime(
            _mr["regime"], _mr["adx"], _mr["atr_ratio"], _mr["regime_duration"]
        )
        if _mr.get("regime_changed"):
            log_manager.signal(
                f"[MicroRegime] 레짐 변경 → {_mr['regime']} "
                f"(ADX={_mr['adx']:.1f} ATR비={_mr['atr_ratio']:.2f} "
                f"지속={_mr['regime_duration']}분)"
            )

        # ATR Circuit Breaker
        self.circuit_breaker.record_atr(atr_ratio)

        # ── STEP 5: 멀티 호라이즌 예측 ─────────────────────────
        _gbm_ready = self.model.is_ready()
        _sgd_ready = self.online_learner.is_ready()

        if not _gbm_ready and not _sgd_ready:
            # 아무 모델도 미학습 — 1/3 기본값으로 예측 진행하여 DB 저장
            # (다음 분 STEP1 검증 → STEP2 learn() 호출 → SGD 부트스트랩)
            log_manager.signal("[bootstrap] 모델 미학습 — 1/3 기본값 예측 진행 (SGD 부트스트랩 대기)")

        feat_vec = self.feature_builder.get_feature_vector(self.model.feature_names)

        if _gbm_ready:
            # ─ GBM + SGD 블렌딩 (정상 경로) ─
            horizon_proba = self.model.predict_proba(feat_vec)
            for h_name in list(horizon_proba.keys()):
                sgd_p   = self.online_learner.predict_proba(h_name, feat_vec)
                blended = self.online_learner.blend_with_gbm(horizon_proba[h_name], sgd_p)
                up, dn, fl = blended["up"], blended["down"], blended["flat"]
                best = max([(up, 1), (dn, -1), (fl, 0)], key=lambda t: t[0])
                horizon_proba[h_name] = {
                    "up": round(up, 4), "down": round(dn, 4), "flat": round(fl, 4),
                    "direction": best[1], "confidence": round(best[0], 4),
                }
        else:
            # ─ SGD-only 또는 bootstrap 경로 (GBM 미학습) ─
            horizon_proba = {}
            for h in HORIZONS:
                sgd_p = self.online_learner.predict_proba(h, feat_vec)
                if sgd_p is None:
                    sgd_p = {"up": 1/3, "down": 1/3, "flat": 1/3}
                up, dn, fl = sgd_p["up"], sgd_p["down"], sgd_p["flat"]
                best = max([(up, 1), (dn, -1), (fl, 0)], key=lambda t: t[0])
                horizon_proba[h] = {
                    "up": round(up, 4), "down": round(dn, 4), "flat": round(fl, 4),
                    "direction": best[1], "confidence": round(best[0], 4),
                }
            if _sgd_ready:
                log_manager.signal("[SGD-only] 예측 진행 (GBM 학습 대기)")
            else:
                log_manager.signal("[default] 1/3 균등 예측 → DB 저장 → SGD 부트스트랩")

        # ── STEP 6: 앙상블 진입 판단 ───────────────────────────
        horizon_proba = self._apply_horizon_calibration(horizon_proba)
        decision = self.ensemble.compute(
            horizon_proba,
            self.current_regime,
            features=features,
            adaptive_gating=True,
        )
        direction  = decision["direction"]
        confidence = decision["confidence"]
        grade      = decision["grade"]
        decision["meta_gate"] = self.meta_gate.evaluate(
            direction=direction,
            confidence=confidence,
            regime=self.current_regime,
            micro_regime=self.current_micro_regime,
            features=features,
            now=datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"),
            recent_accuracy=self.online_learner.recent_accuracy(),
        )
        decision["toxicity_gate"] = self.toxicity_gate.evaluate(features)

        self.circuit_breaker.record_signal(direction)

        # [§14] 레짐-파라미터 오버라이드 — STEP 6에서 매분 적용
        try:
            from config.strategy_params import (
                apply_regime_overrides as _aro,
                is_entry_blocked as _ieb,
                PARAM_CURRENT as _PC,
            )
            _MICRO_EN = {
                "추세장": "TREND", "횡보장": "RANGE",
                "급변장": "VOLATILE", "혼합": "TREND",
                "탈진":   "EXHAUSTION",   # 레짐 챔피언 게이트가 실제 차단 담당
            }
            _micro_en = _MICRO_EN.get(self.current_micro_regime, "TREND")
            _regime_params = _aro(_PC, self.current_regime, _micro_en)
            if _ieb(_regime_params):
                direction = 0
                grade     = "X"
                log_manager.signal(
                    f"[RegimeOverride] 진입 금지 "
                    f"— {self.current_regime}×{self.current_micro_regime}"
                )
        except Exception as _ro_e:
            logger.debug("[RegimeOverride] 적용 실패 (스킵): %s", _ro_e)

        # [§19] RegimeFingerprint CRITICAL — 피처 분포 심각 변화 시 진입 차단
        try:
            from strategy.regime_fingerprint import get_fingerprint as _get_fp2
            if _get_fp2().get_level() >= 3:  # DriftLevel.CRITICAL = 3
                direction = 0
                grade     = "X"
                log_manager.signal(
                    f"[RegimeFingerprint] PSI={_get_fp2().get_psi():.3f} CRITICAL "
                    f"— 시장 구조 변화로 진입 차단"
                )
        except Exception as _fp2_e:
            logger.debug("[RegimeFingerprint] STEP6 스킵: %s", _fp2_e)

        # [§20] 레짐 챔피언 게이트 — 챔피언 미설정 레짐 진입 차단
        # 탈진 레짐: 수동 승격 전까지 champion=None → 진입 0
        # CHAMPION_BASELINE: 앙상블 신호 그대로 사용
        # 특정 전문가 챔피언: 앙상블 신호 + 보강 로그
        if self.challenger_engine is not None and direction != 0:
            try:
                from challenger.challenger_registry import CHAMPION_BASELINE_ID as _CB_ID
                _reg_champ = self.challenger_engine.registry.get_regime_champion(
                    self.current_micro_regime
                )
                if _reg_champ is None:
                    direction = 0
                    grade     = "X"
                    log_manager.signal(
                        f"[RegimeChampGate] {self.current_micro_regime} 레짐 "
                        f"전문가 챔피언 미설정 — 진입 차단 (수동 승격 필요)"
                    )
                elif _reg_champ != _CB_ID:
                    log_manager.signal(
                        f"[RegimeChampGate] {self.current_micro_regime} 레짐 "
                        f"전문가 챔피언 [{_reg_champ}] 활성 — 앙상블 신호 보강"
                    )
            except Exception as _cg_e:
                logger.debug("[RegimeChampGate] 스킵: %s", _cg_e)

        log_manager.signal(
            f"앙상블: dir={direction:+d} conf={confidence:.1%} "
            f"grade={grade} micro={self.current_micro_regime}"
        )

        # 대시보드 호라이즌 카드 + 신뢰도 헤더 업데이트 (매분)
        _H_MAP = {"1m":"1분","3m":"3분","5m":"5분","10m":"10분","15m":"15분","30m":"30분"}
        _preds_ui = {
            _H_MAP.get(h, h): {
                "signal": r["direction"],
                "up":     r["up"],
                "dn":     r["down"],
                "flat":   r["flat"],
            }
            for h, r in horizon_proba.items()
        }

        # Fix2: GBM 피처 중요도 → 파라미터 중요도 바
        _importance = self.model.get_feature_importance() if _gbm_ready else {}
        _params_ui  = {
            pname: _importance.get(fname, 0.0)
            for pname, fname in _PARAM_FEAT_MAP.items()
        }

        # Fix3: 상관계수 레이블 문자열 (중요도 상위 4개)
        _CORR_SHORT = {
            "CVD 다이버전스": "CVD", "VWAP 위치": "VWAP", "OFI 불균형": "OFI",
            "외인 콜순매수": "외인콜", "다이버전스 지수": "다이버전스",
            "프로그램 비차익": "프로그램",
        }
        _corr_items = sorted(_params_ui.items(), key=lambda t: -t[1])
        _corr_str   = "  ".join(
            f"{_CORR_SHORT.get(p, p)}+{v:.2f}"
            for p, v in _corr_items if v > 0
        )[:60]  # 레이블 넘침 방지

        self.dashboard.update_prediction(close, _preds_ui, _params_ui, confidence,
                                         corr=_corr_str)

        # GBM 미학습 시 모델 상태 행 재표시 (update_prediction이 행을 숨겼으므로)
        if not _gbm_ready:
            n   = count_raw_candles()
            pct = min(n * 100 // _MIN_TRAIN_BARS, 99)
            if _sgd_ready:
                self.dashboard.set_model_status(
                    "SGD 예측중",
                    f"GBM 대기 {n}/{_MIN_TRAIN_BARS}행",
                    pct,
                    update_signal=False,
                )
            else:
                self.dashboard.set_model_status(
                    "모델 학습 대기",
                    f"데이터 {n}/{_MIN_TRAIN_BARS}행 ({pct}%)",
                    pct,
                )
        # update_entry 는 STEP 7에서 체크리스트 결과 포함해 한 번만 호출

        # [DBG-F6] 호라이즌별 예측 확률 + CB 상태 스냅샷
        _h_summary = " | ".join(
            f"{h}:{r['direction']:+d}@{r['confidence']:.0%}"
            for h, r in horizon_proba.items()
        )
        debug_log.debug("[DBG-F6] horizons: %s", _h_summary)
        _cb = self.circuit_breaker.status_dict()
        debug_log.debug(
            "[DBG-CB] state=%s consec_stops=%d acc30m=%.1f%% latency=%.3fs%s",
            _cb["state"], _cb["consec_stops"],
            _cb["accuracy_30m"] * 100, _cb["last_latency"],
            f" pause_until={_cb['pause_until']}" if _cb["pause_until"] else "",
        )

        # ── STEP 7: 진입 실행 ──────────────────────────────────
        _dir_ko = "상승" if direction > 0 else "하락" if direction < 0 else "관망"
        time_zone = get_time_zone()
        _CHK_MAP = {
            "1_signal":"signal_chk", "2_confidence":"conf_chk",
            "3_vwap":"vwap_chk",    "4_cvd":"cvd_chk",
            "5_ofi":"ofi_chk",      "6_foreign":"fi_chk",
            "7_prev_bar":"candle_chk","8_time":"time_chk",
            "9_risk":"risk_chk",
        }

        # 체크리스트: FLAT + 방향 있을 때 항상 평가 (CB·시간 조건 무관)
        # → 대시보드가 조건 차단 시에도 올바른 체크 결과를 표시할 수 있도록
        _final_grade = grade
        _checks_ui   = {}   # 빈 dict → 대시보드에서 "—" 표시
        _qty_display = 0
        _cr          = None

        if direction != 0 and self.position.status == "FLAT":
            _cr = self.checklist.evaluate(
                direction         = direction,
                confidence        = confidence,
                vwap_position     = features.get("vwap_position", 0),
                cvd_direction     = int(features.get("cvd_direction", 0)),
                ofi_pressure      = int(features.get("ofi_pressure", 0)),
                foreign_call_net  = features.get("foreign_call_net", 0),
                foreign_put_net   = features.get("foreign_put_net", 0),
                prev_bar_bullish  = bar.get("close", 0) >= bar.get("open", 0),
                time_zone         = time_zone,
                daily_loss_pct    = max(-self.position.daily_stats()["pnl_krw"], 0) / 50_000_000,
                min_confidence    = decision["min_conf"],
            )
            _final_grade = _cr["grade"]
            _checks_ui   = {_CHK_MAP.get(k, k): v for k, v in _cr["checks"].items()}

            # [DBG-F7a] 체크리스트 항목별 ✓/✗
            _chk = _cr["checks"]
            debug_log.debug(
                "[DBG-F7a] checklist %d/9 → %s | "
                "sig=%s conf=%s vwap=%s cvd=%s ofi=%s foreign=%s prev=%s time=%s risk=%s",
                _cr["pass_count"], _cr["grade"],
                "✓" if _chk.get("1_signal")     else "✗",
                "✓" if _chk.get("2_confidence") else "✗",
                "✓" if _chk.get("3_vwap")       else "✗",
                "✓" if _chk.get("4_cvd")        else "✗",
                "✓" if _chk.get("5_ofi")        else "✗",
                "✓" if _chk.get("6_foreign")    else "✗",
                "✓" if _chk.get("7_prev_bar")   else "✗",
                "✓" if _chk.get("8_time")       else "✗",
                "✓" if _chk.get("9_risk")       else "✗",
            )

            if _final_grade != "X" and self.circuit_breaker.is_entry_allowed():
                kelly_result = self.kelly.compute_fraction()
                size_result  = self.sizer.compute(
                    confidence          = confidence,
                    atr                 = atr,
                    regime              = self.current_regime,
                    grade_mult          = _cr["size_mult"],
                    adaptive_kelly_mult = kelly_result["multiplier"],
                    account_balance     = _ts_current_sizer_balance(self),
                )
                _qty_display = size_result["quantity"]

                # [DBG-F7b] 사이저 입력/출력 확인
                debug_log.debug(
                    "[DBG-F7b] sizer: conf=%.1f%% ATR=%.4f regime=%s "
                    "grade_mult=%.2f kelly_mult=%.2f → qty=%d",
                    confidence * 100, atr, self.current_regime,
                    _cr["size_mult"], kelly_result.get("multiplier", 1.0),
                    _qty_display,
                )

        # 진입 패널 갱신 — 체크리스트 결과 + 산출 수량 (항상)
        _meta_gate = decision.get("meta_gate") or {}
        _meta_action = _meta_gate.get("action", "")
        _meta_size = float(_meta_gate.get("size_multiplier", 1.0) or 1.0)
        _tox_gate = decision.get("toxicity_gate") or {}
        _tox_action = _tox_gate.get("action", "pass")
        _tox_size = float(_tox_gate.get("size_multiplier", 1.0) or 1.0)
        if direction != 0 and self.position.status == "FLAT":
            if _meta_action == "skip":
                _final_grade = "X"
                _qty_display = 0
            elif _qty_display > 0:
                _qty_display = max(1, int(round(_qty_display * _meta_size)))
            if _meta_action:
                log_manager.signal(
                    f"[MetaGate] action={_meta_action} meta_conf={_meta_gate.get('meta_confidence', 0.0):.1%} "
                    f"size_mult={_meta_size:.2f} reason={_meta_gate.get('reason', '')}"
                )
            if _tox_action == "block":
                _final_grade = "X"
                _qty_display = 0
            elif _qty_display > 0 and _tox_action == "reduce":
                _qty_display = max(1, int(round(_qty_display * _tox_size)))
            if _tox_action != "pass":
                log_manager.signal(
                    f"[ToxicityGate] action={_tox_action} score={_tox_gate.get('score', 0.0):.2f} "
                    f"ma={_tox_gate.get('score_ma', 0.0):.2f} size_mult={_tox_size:.2f} "
                    f"reason={_tox_gate.get('reason', '')}"
                )

        _raw_entry_dir = "LONG" if direction > 0 else "SHORT" if direction < 0 else ""
        _resolved_raw_dir, _resolved_final_dir, _reverse_on = self._resolve_entry_direction(_raw_entry_dir)
        _raw_signal_ko = self._direction_to_korean(_resolved_raw_dir)
        _final_signal_ko = self._direction_to_korean(_resolved_final_dir)
        self.dashboard.update_entry(
            _raw_signal_ko,
            confidence,
            _final_grade,
            _checks_ui,
            qty=_qty_display,
            final_signal=_final_signal_ko,
            reverse_enabled=_reverse_on,
        )
        self._manual_entry_ctx = {
            "price": close,
            "qty":   _qty_display,
            "atr":   atr,
            "grade": _final_grade,
        }

        # [DBG-F7] 진입 실행 조건 평가
        debug_log.debug(
            "[DBG-F7] 진입조건: pos=%s CB=%s new_entry=%s grade=%s time_zone=%s",
            self.position.status, self.circuit_breaker.state,
            is_new_entry_allowed(), _final_grade, time_zone,
        )

        # 실제 진입: CB + 시간 조건 + 분봉 품질 모두 충족해야 실행
        _in_cooldown = (
            self._entry_cooldown_until is not None
            and datetime.datetime.now() < self._entry_cooldown_until
        )
        _in_exit_cooldown = (
            self._exit_cooldown_until is not None
            and datetime.datetime.now() < self._exit_cooldown_until
        )
        _hurst_ok = features.get("hurst", 0.5) >= HURST_RANGE_THRESHOLD
        _atr_ok   = atr >= ATR_MIN_ENTRY   # ATR 너무 낮으면 노이즈 > 손절거리 → 휩쏘

        # 수익 보존 가드 체크 (STEP 7 진입 직전)
        _daily_pnl_now = self.position.daily_stats()["pnl_krw"]
        _size_mult_now = _cr["size_mult"] if _cr else 1.0
        _pg_allowed, _pg_reason = self.profit_guard.is_entry_allowed(
            _daily_pnl_now, _size_mult_now
        )
        if not _pg_allowed and _final_grade not in ("X",):
            _final_grade = "X"
            log_manager.signal(f"[ProfitGuard] 진입 차단: {_pg_reason}")

        if (
            _cr is not None
            and self.circuit_breaker.is_entry_allowed()
            and is_new_entry_allowed()
            and not self._broker_sync_block_new_entries
            and not _in_cooldown                   # [B53] ENTRY 타임아웃 후 쿨다운
            and not _in_exit_cooldown              # 청산 후 즉각 재진입 차단
            and _hurst_ok                          # 횡보 레짐 진입 차단 (Hurst < 0.45)
            and _atr_ok                            # 변동성 너무 낮음 진입 차단
            and _final_grade not in ("X",)
            and _qty_display > 0
            and not _bar_volume_zero          # Guard-C3: volume=0 분봉 진입 차단
        ):
            dir_str = "LONG" if direction > 0 else "SHORT"
            raw_dir_str, final_dir_str, reverse_on = self._resolve_entry_direction(dir_str)
            raw_signal_ko = self._direction_to_korean(raw_dir_str)
            final_signal_ko = self._direction_to_korean(final_dir_str)
            if _cr["auto_entry"] and self._auto_entry_enabled:
                self._execute_entry(
                    final_dir_str, close, _qty_display, atr, _final_grade,
                    raw_direction=raw_dir_str,
                    reverse_enabled=reverse_on,
                )
            else:
                log_manager.signal(
                    f"[EntrySignal] 원신호={raw_dir_str} 실행신호={final_dir_str} "
                    f"역방향진입={'ON' if reverse_on else 'OFF'} 등급={_final_grade} 상태=MANUAL_CONFIRM"
                )
                log_manager.trade(
                    f"[수동 확인 필요] {raw_dir_str}->{final_dir_str} {_qty_display}계약 @ {close} "
                    f"등급={_final_grade} | 역방향진입={'ON' if reverse_on else 'OFF'}"
                )
                notify(
                    f"진입 확인 요청: {raw_signal_ko} -> {final_signal_ko} {_qty_display}계약\n"
                    f"등급={_final_grade} 신뢰도={confidence:.1%} | 역방향진입={'ON' if reverse_on else 'OFF'}",
                    "WARNING",
                )

        # ── 진입 차단 이유 로그 (이유가 바뀔 때만 1회 출력) ──────
        if direction != 0 and self.position.status == "FLAT":
            _cb_state = self.circuit_breaker.state
            if _cb_state != "NORMAL":
                _reason = f"[차단] Circuit Breaker {_cb_state} — 진입 불가 (CB 해제까지 대기)"
            elif self._broker_sync_block_new_entries:
                _reason = f"[차단] 브로커 sync 미검증 상태 — 자동진입 금지 ({self._broker_sync_last_error})"
            elif _in_cooldown:
                _remain = (self._entry_cooldown_until - datetime.datetime.now()).seconds
                _reason = f"[차단] ENTRY 타임아웃 쿨다운 — {_remain}초 후 재진입 가능"
            elif _in_exit_cooldown:
                _remain = (self._exit_cooldown_until - datetime.datetime.now()).seconds
                _reason = f"[차단] 청산 후 쿨다운 — {_remain}초 후 재진입 가능"
            elif not _hurst_ok:
                _hurst_val = features.get("hurst", 0.5)
                _reason = f"[차단] Hurst {_hurst_val:.3f} < {HURST_RANGE_THRESHOLD} — 횡보 레짐 진입 차단"
            elif not _atr_ok:
                _reason = f"[차단] ATR {atr:.2f}pt < {ATR_MIN_ENTRY}pt — 변동성 부족 (휩쏘 위험)"
            elif not is_new_entry_allowed():
                _reason = "[차단] 15:00 이후 — 신규 진입 금지 구간"
            elif _cr is None:
                _reason = ""
            elif _final_grade == "X":
                _failed = [k for k, v in _cr["checks"].items() if not v]
                if "8_time" in _failed and time_zone == "OTHER":
                    _reason = f"[차단] 점심 휴식 구간 (11:50~13:00 OTHER) — 체크리스트 8_time 실패"
                elif "8_time" in _failed:
                    _reason = f"[차단] 진입 금지 시간대 ({time_zone}) — 체크리스트 8_time 실패"
                else:
                    _reason = f"[차단] 등급X — 미통과 항목: {', '.join(_failed)}"
            else:
                _reason = ""
            if _reason and _reason != self._last_block_reason:
                log_manager.signal(_reason)
                self._last_block_reason = _reason
        elif direction == 0 or self.position.status != "FLAT":
            self._last_block_reason = ""

        # ── STEP 8: 청산 트리거 감시 ───────────────────────────
        if self.position.status != "FLAT":
            self._check_exit_triggers(close, features, decision, bar)

        # ── 청산 패널 갱신 (매분 — 실제 PositionTracker 값 전달) ──
        _pos = self.position
        self.dashboard.update_position({
            "status":     _pos.status,
            "entry":      _pos.entry_price,
            "current":    close,
            "qty":        _pos.quantity,
            "atr":        atr,
            "stop":       _pos.stop_price,
            "tp1":        _pos.tp1_price,
            "tp2":        _pos.tp2_price,
            "partial1":   _pos.partial_1_done,
            "partial2":   _pos.partial_2_done,
            "entry_time": _pos.entry_time,
        })

        # ── 대시보드 PnL 패널 갱신 (매분) ──────────────────────────
        _daily   = self.position.daily_stats()
        _forward_daily = self.position.daily_forward_stats()
        _unreal  = self.position.unrealized_pnl_pts(close) * self._pt_value
        _forward_unreal = self.position.unrealized_forward_pnl_pts(close) * self._pt_value
        _var_krw = -(atr * 1.65 * self.position.quantity * self._pt_value) if self.position.quantity else 0.0
        self.dashboard.update_pnl_metrics(
            _unreal,
            _daily["pnl_krw"],
            _var_krw,
            forward_unrealized_krw=_forward_unreal,
            forward_daily_pnl_krw=_forward_daily["pnl_krw"],
        )

        # 당일 진입 통계 갱신 — STEP 9 예외와 무관하게 항상 실행
        _ds = self.position.daily_stats()
        self.dashboard.update_entry_stats(_ds["trades"], _ds["wins"], _ds["pnl_pts"])

        # 주문/체결 탭 메트릭 갱신 (LatencySync 실데이터)
        _ls = self.latency_sync.summary()
        self.dashboard.update_order_metrics(
            trades      = _ds["trades"],
            avg_lat_ms  = _ls["offset_ms"],
            peak_lat_ms = _ls["peak_ms"],
            samples     = _ls["sample_count"],
        )

        # ── STEP 9: 예측 DB 저장 ───────────────────────────────
        try:
            for h_name, h_res in horizon_proba.items():
                self.pred_buffer.save_prediction(
                    ts         = ts,
                    horizon    = h_name,
                    direction  = h_res["direction"],
                    confidence = h_res["confidence"],
                    up_prob    = h_res.get("up"),
                    down_prob  = h_res.get("down"),
                    flat_prob  = h_res.get("flat"),
                    features   = {k: round(float(v), 4) for k, v in features.items()
                                  if v is not None and v == v},  # NaN/None 제외
                )
            self.pred_buffer.save_ensemble_decision(
                ts=ts,
                regime=self.current_regime,
                micro_regime=self.current_micro_regime,
                decision=decision,
                features={k: round(float(v), 4) for k, v in features.items()
                          if v is not None and v == v},
            )
        except Exception as e:
            logger.warning("[STEP9] save_prediction 오류 (스킵): %s", e)

        # ── 챔피언-도전자 Shadow 실행 (STEP 9 이후 훅) ─────────
        if self.challenger_engine is not None:
            _ctx = {
                "ts":     ts,
                "atr":    features.get("atr", 1.0),
                "regime": self.current_micro_regime,
                "candle": bar if isinstance(bar, dict) else {},
            }
            self.challenger_engine.run_shadow(features, _ctx.get("candle", {}), _ctx)

        # 🧠 자가학습 모니터 패널 갱신 (매분)
        self.dashboard.update_learning(self._gather_learning_stats())

        # 🎯 효과 검증 리포트 자동 갱신
        self._effect_report_tick += 1
        if self._effect_report_tick == 1 or self._effect_report_tick % 15 == 1:
            self._run_effect_report_script("generate_calibration_report.py")
            self._run_effect_report_script("generate_meta_gate_tuning_report.py", "5m")
            self._run_effect_report_script("generate_rollout_readiness_report.py")
            if self._effect_report_tick == 1 or self._effect_report_tick % 30 == 1:
                self._run_effect_report_script("run_microstructure_ab_backtest.py")
            self._append_effect_monitor_history()

        # 🎯 학습 효과 검증기 패널 갱신 (5분마다 — DB 쿼리 비용 분산)
        self._efficacy_tick += 1
        if self._efficacy_tick % 5 == 1:   # 첫 분 + 이후 5분마다
            self.dashboard.update_efficacy(self._gather_efficacy_stats())

        # 상태 바 '마지막 갱신' 타이머 리셋
        self.dashboard.notify_pipeline_ran()

        # [Phase2] Shadow Evaluator — 신버전 가상 실행 (실주문 없음)
        if self._shadow_ev is not None:
            try:
                _dir_str = "LONG" if direction == 1 else ("SHORT" if direction == -1 else "FLAT")
                self._shadow_ev.process_tick(
                    bar,
                    {
                        "confidence": confidence,
                        "direction":  _dir_str,
                        "grade":      grade,
                        "hurst":      float(features.get("hurst", 0.5)),
                    },
                )
            except Exception as _se:
                logger.debug("[Shadow] process_tick 오류: %s", _se)

            # [§20 / Phase5] Hot-Swap 게이트 — 2주마다 자동 조건 검사
            try:
                _sv_days = getattr(self._shadow_ev, "_uptime_days", 0)
                if _sv_days > 0 and _sv_days % 10 == 0:   # 10분마다 체크 (실제로는 일 단위)
                    from strategy.ops.hotswap_gate import get_hotswap_gate
                    from utils.db_utils import fetch_pnl_history
                    _live_pnls = [r.get("pnl_krw", 0) for r in (fetch_pnl_history(20) or [])]
                    if len(_live_pnls) >= 10:
                        _gate = get_hotswap_gate()
                        _ok, _reason = _gate.attempt(
                            shadow_ev       = self._shadow_ev,
                            live_daily_pnls = _live_pnls,
                            best_params     = getattr(self._shadow_ev, "params", {}),
                            note            = "Hot-Swap 자동 게이트 검사",
                        )
                        if _ok:
                            log_manager.system(
                                f"[HotSwapGate] ✅ Hot-Swap 승인 — {_reason}", "INFO"
                            )
                            self._shadow_ev = None   # 승인 후 shadow 종료
                        else:
                            logger.info("[HotSwapGate] 보류 — %s", _reason)
            except Exception as _hg_e:
                logger.debug("[HotSwapGate] 스킵: %s", _hg_e)

    def _execute_partial_exit(self, price: float, stage: int) -> None:
        """TP{stage} 부분 청산 — 수량 계산 → API 주문 → 수량 감소 → PnL 기록."""
        total_qty   = self.position.quantity
        ratio       = PARTIAL_EXIT_RATIOS[stage - 1]
        partial_qty = max(1, round(total_qty * ratio))
        reason      = f"TP{stage} 부분청산 {ratio:.0%}"

        if partial_qty >= total_qty:
            # 잔여가 부분 청산 불가 (1계약 포지션 등) → 전량 청산으로 전환
            self._send_kiwoom_exit_order(total_qty)
            result = self.position.close_position(price, f"TP{stage}(전량)")
            self._post_exit(result)
            return

        self._send_kiwoom_exit_order(partial_qty)
        result = self.position.partial_close(price, partial_qty, reason)

        if stage == 1:
            self.position.partial_1_done = True
        else:
            self.position.partial_2_done = True

        self._post_partial_exit(result, stage)

    def _post_partial_exit(self, result: dict, stage: int) -> None:
        """부분 청산 후처리 — CB/Kelly 통계, 대시보드, DB 기록."""
        pnl = result["pnl_pts"]
        qty = result["quantity"]

        if pnl > 0:
            self.circuit_breaker.record_win()
            self.kelly.record(win=True, pnl_pts=pnl)
        else:
            self.circuit_breaker.record_stop_loss()
            self.kelly.record(win=False, pnl_pts=pnl)

        log_manager.trade(
            f"[TP{stage} 부분청산] {qty}계약 @ {result['exit_price']:.2f} "
            f"PnL={pnl:+.2f}pt ({result['pnl_krw']:+,.0f}원) "
            f"잔여={result['remaining']}계약"
        )
        _cum_pnl = self.position.daily_stats()["pnl_krw"]
        self.dashboard.append_pnl_log(
            f"부분청산TP{stage} | {result['direction']} {qty}계약 @ {result['exit_price']}",
            f"PnL {pnl:+.2f}pt  {result['pnl_krw']:+,.0f}원  잔여 {result['remaining']}계약  │ 금일 {_cum_pnl:+,.0f}원",
        )
        self.dashboard.minute_chart_record_exit(
            result["exit_price"],
            datetime.datetime.now(),
            finalize=False,
            pnl_pts=result.get("pnl_pts"),
            reason=f"TP{stage} partial",
            direction=result.get("direction", ""),
        )
        _daily = self.position.daily_stats()
        _forward_daily = self.position.daily_forward_stats()
        self.dashboard.update_pnl_metrics(
            self.position.unrealized_pnl_pts(result["exit_price"]) * self._pt_value,
            _daily["pnl_krw"],
            0.0,
            forward_unrealized_krw=self.position.unrealized_forward_pnl_pts(result["exit_price"]) * self._pt_value,
            forward_daily_pnl_krw=_forward_daily["pnl_krw"],
        )
        self._record_trade_result(result)
        self._refresh_pnl_history()

    def _send_kiwoom_entry_order(self, direction: str, qty: int) -> int:
        """키움 선물 진입 주문 전송 (SendOrderFO). 반환값: 0=성공, 음수=오류"""
        code = getattr(self, "_futures_code", "")
        if not code:
            return -1
        account_no = self._get_active_account_no()
        if not account_no:
            return -1
        # [B54] lOrdKind=1(신규매매) + sSlbyTp 방향 명시
        # trade_type=2는 new convention에서 "정정"으로 해석되어 Kiwoom 서버에서 조용히 거부됨
        slby_tp = "2" if direction == "LONG" else "1"  # "2"=매수, "1"=매도
        side = "BUY" if direction == "LONG" else "SELL"
        return self.broker.send_market_order(
            account_no=account_no,
            code=code,
            side=side,
            qty=qty,
            rqname="진입",
            screen_no="1000",
        )

    def _send_kiwoom_exit_order(self, qty: int) -> int:
        """키움 선물 청산 주문 전송 (SendOrderFO). 반환값: 0=성공, 음수=오류"""
        code = getattr(self, "_futures_code", "")
        if not code or self.position.status == "FLAT":
            return -1
        account_no = self._get_active_account_no()
        if not account_no:
            return -1
        # [B54] lOrdKind=1(신규매매) + sSlbyTp 방향: 거래소 측 자동 네팅으로 청산 처리
        # trade_type=4(구: 청산매도)는 new convention에서 미정의, trade_type=3은 취소로 해석됨
        slby_tp = "1" if self.position.status == "LONG" else "2"  # LONG→매도(1), SHORT→매수(2)
        side = "SELL" if self.position.status == "LONG" else "BUY"
        return self.broker.send_market_order(
            account_no=account_no,
            code=code,
            side=side,
            qty=qty,
            rqname="청산",
            screen_no="1001",
        )

    def _execute_entry(
        self, direction: str, price: float,
        quantity: int, atr: float, grade: str,
    ):
        """진입 실행"""
        ret = self._send_kiwoom_entry_order(direction, quantity)
        if ret != 0:
            logger.error("[Entry] SendOrder 실패로 내부 포지션 오픈을 취소합니다. ret=%s", ret)
            log_manager.system(
                f"[Entry] 주문 실패로 포지션 미오픈 ret={ret} dir={direction} qty={quantity}",
                "ERROR",
            )
            return
        self.position.open_position(
            direction = direction,
            price     = price,
            quantity  = quantity,
            atr       = atr,
            grade     = grade,
            regime    = self.current_regime,
        )
        log_manager.trade(
            f"[진입] {direction} {quantity}계약 @ {price} "
            f"등급={grade} 레짐={self.current_regime}"
        )
        # 수익 보존 가드 — 오후 진입 카운터 업데이트
        self.profit_guard.on_entry()
        # PnL 탭 진입 이벤트 기록 [B28]
        self.dashboard.append_pnl_log(
            f"진입 | {direction} {quantity}계약 @ {price}  등급={grade}",
            f"손절 {self.position.stop_price:.2f}  1차 {self.position.tp1_price:.2f}",
        )

    def _check_exit_triggers(self, price: float, features: dict, decision: dict, bar: dict = None):
        """청산 트리거 감시 (우선순위 1~4)"""
        atr = features.get("atr", 0.5)

        # [DBG-F8] 매분 포지션 현황 스냅샷 — 손절·TP 거리 + 미실현 손익
        if self.position.status != "FLAT":
            _mult     = 1 if self.position.status == "LONG" else -1
            _upnl     = self.position.unrealized_pnl_pts(price)
            _stop_dist = (price - self.position.stop_price) * _mult
            _tp1_dist  = (self.position.tp1_price  - price) * _mult
            _tp2_dist  = (self.position.tp2_price  - price) * _mult
            debug_log.debug(
                "[DBG-F8] %s %dct @%.2f cur=%.2f upnl=%+.2fpt"
                " | stop_dist=%.2f tp1=%.2f tp2=%.2f | stop=%.2f | p1=%s p2=%s",
                self.position.status, self.position.quantity,
                self.position.entry_price, price, _upnl,
                _stop_dist, _tp1_dist, _tp2_dist,
                self.position.stop_price,
                "✓" if self.position.partial_1_done else "○",
                "✓" if self.position.partial_2_done else "○",
            )

        # 트레일링 스톱 업데이트
        self.position.update_trailing_stop(price, atr)

        # 1순위: 하드 스톱 — bar의 고저가 기준으로 체크, exit은 손절가 사용 (close가 개선)
        if self.position.is_stop_hit(price):
            # bar low/high가 stop을 뚫은 경우 stop_price로 청산 (close가보다 유리 또는 동등)
            bar_low  = bar["low"]  if bar else price
            bar_high = bar["high"] if bar else price
            if self.position.status == "LONG":
                exit_price = max(self.position.stop_price, bar_low)   # 손절가 이상 보장
            else:
                exit_price = min(self.position.stop_price, bar_high)  # 손절가 이하 보장
            debug_log.debug(
                "[DBG-STOP] 하드스톱 발동: close=%.2f bar_low=%.2f stop=%.2f → exit=%.2f",
                price, bar_low, self.position.stop_price, exit_price,
            )
            self._send_kiwoom_exit_order(self.position.quantity)
            result = self.position.close_position(exit_price, "하드스톱")
            self._post_exit(result)
            return

        # 3순위: 부분 청산 (pending 가드 + is_tp1_hit/is_tp2_hit 내부 partial_done 이중 체크)
        if (not self._has_pending_order()
                and self.position.status != "FLAT"
                and self.position.is_tp1_hit(price)):
            self._execute_partial_exit(price, stage=1)

        if (not self._has_pending_order()
                and self.position.status != "FLAT"
                and self.position.is_tp2_hit(price)):
            self._execute_partial_exit(price, stage=2)

        # 4순위: 시간 강제 청산
        if self.time_exit.should_force_exit():
            self._send_kiwoom_exit_order(self.position.quantity)
            result = self.position.close_position(price, "15:10 강제청산")
            self._post_exit(result)

    def _post_exit(self, result: dict):
        """청산 후 처리"""
        pnl = result["pnl_pts"]
        if pnl > 0:
            self.circuit_breaker.record_win()
            self.kelly.record(win=True, pnl_pts=pnl)
        else:
            self.circuit_breaker.record_stop_loss()
            self.kelly.record(win=False, pnl_pts=pnl)
        # 수익 보존 가드 — 체결 후 연속 손실 카운터 업데이트
        _daily_after = self.position.daily_stats()["pnl_krw"]
        self.profit_guard.on_trade_close(result["pnl_krw"], _daily_after)

        # 쿨다운 설정 — Cybos 비동기 경로(_ts_on_exit_fill)에서는 이미 호출되지 않으므로
        # 여기서 단일 진입점으로 처리 (레거시 동기 경로 포함 모두 통합)
        if not getattr(self, "_exit_cooldown_applied_this_fill", False):
            _ts_apply_exit_cooldown(self, result)
        self._exit_cooldown_applied_this_fill = False

        log_manager.trade(
            f"[청산 완료] PnL={pnl:+.2f}pt ({result['pnl_krw']:+,.0f}원)"
        )

        # PnL 패널 즉시 갱신 — 다음 분봉까지 기다리지 않음 [B27]
        _daily = self.position.daily_stats()
        _forward_daily = self.position.daily_forward_stats()
        self.dashboard.update_pnl_metrics(
            0.0,
            _daily["pnl_krw"],
            0.0,
            forward_unrealized_krw=0.0,
            forward_daily_pnl_krw=_forward_daily["pnl_krw"],
        )
        self.dashboard.append_pnl_log(
            f"청산 | {result['direction']} {result['quantity']}계약 "
            f"@ {result['exit_price']} ({result['exit_reason']})",
            f"PnL {pnl:+.2f}pt  {result['pnl_krw']:+,.0f}원  │ 금일 {_daily['pnl_krw']:+,.0f}원",
        )
        self.dashboard.minute_chart_record_exit(
            result["exit_price"],
            datetime.datetime.now(),
            finalize=True,
            pnl_pts=result.get("pnl_pts"),
            reason=result.get("exit_reason", ""),
            direction=result.get("direction", ""),
        )
        self.dashboard.set_ui_ready_mode()

        self._record_trade_result(result)
        self._refresh_pnl_history()

    def activate_kill_switch(self, reason: str = "수동 발동") -> None:
        """Ctrl+Alt+K 단축키 또는 외부 호출용."""
        self.kill_switch.activate(reason)
        log_manager.system("KillSwitch 발동: " + reason, "CRITICAL")

    # ── 자가학습 통계 수집 ────────────────────────────────────
    def _gather_learning_stats(self) -> dict:
        """LearningPanel 업데이트용 통계 딕셔너리 반환"""
        ol   = self.online_learner
        gbm  = self.batch_retrainer.get_stats()
        raw  = count_raw_candles()

        # 예측 버퍼 기반 호라이즌별 최근 정확도
        buf_acc = {hz: self.pred_buffer.recent_accuracy(hz, 50)
                   for hz in ["1m", "3m", "5m", "10m", "15m", "30m"]}

        # SGD 내부 정확도 = 전체 정확도 버퍼 (호라이즌 구분 없이 동일)
        h_acc = {hz: ol.recent_accuracy() for hz in ol._fitted}

        last_ev = ""
        if self._verified_today > 0:
            acc = ol.recent_accuracy()
            last_ev = (
                f"{datetime.datetime.now().strftime('%H:%M')} | "
                f"검증 {self._verified_today}건 누적 · "
                f"SGD {ol.sgd_weight:.0%} · 정확도 {acc:.1%}"
            )

        return {
            "verified_today":    self._verified_today,
            "sgd_accuracy_50m":  ol.recent_accuracy(),
            "sgd_weight":        ol.sgd_weight,
            "gbm_weight":        ol.gbm_weight,
            "sgd_fitted":        dict(ol._fitted),
            "sgd_sample_counts": dict(ol._horizon_counts),
            "horizon_accuracy":  h_acc,
            "buffer_accuracy":   buf_acc,
            "gbm_last_retrain":  gbm["last_retrain"],
            "gbm_retrain_count": gbm["retrain_count"],
            "raw_candles_count": raw,
            "last_event":        last_ev,
        }

    def _load_json_file(self, path: str) -> dict:
        try:
            if not os.path.exists(path):
                return {}
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as exc:
            logger.warning("[EffectReports] json load failed %s: %s", path, exc)
            return {}

    def _run_effect_report_script(self, script_name: str, *args: str) -> bool:
        script_path = os.path.join(BASE_DIR, "scripts", script_name)
        try:
            result = subprocess.run(
                [sys.executable, script_path, *args],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
        except Exception as exc:
            logger.warning("[EffectReports] run failed %s: %s", script_name, exc)
            return False

        if result.returncode != 0:
            logger.warning(
                "[EffectReports] %s rc=%s stderr=%s",
                script_name,
                result.returncode,
                (result.stderr or "").strip()[-300:],
            )
            return False
        return True

    def _append_effect_monitor_history(self) -> None:
        ab = self._load_json_file(os.path.join(BASE_DIR, "microstructure_ab_metrics.json"))
        calib = self._load_json_file(os.path.join(BASE_DIR, "calibration_metrics.json"))
        meta = self._load_json_file(os.path.join(BASE_DIR, "meta_gate_tuning_metrics.json"))
        rollout = self._load_json_file(os.path.join(BASE_DIR, "rollout_readiness_metrics.json"))
        if not any([ab, calib, meta, rollout]):
            return

        baseline = ab.get("baseline", {})
        enhanced = ab.get("enhanced", {})
        best_grid = meta.get("best_grid", {})
        snapshot = {
            "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ab_pnl_delta": round(
                float(enhanced.get("total_pnl_pts", 0.0) or 0.0)
                - float(baseline.get("total_pnl_pts", 0.0) or 0.0),
                6,
            ),
            "ab_accuracy_delta": round(
                float(enhanced.get("directional_accuracy", 0.0) or 0.0)
                - float(baseline.get("directional_accuracy", 0.0) or 0.0),
                6,
            ),
            "calibration_ece": round(float(calib.get("overall", {}).get("ece", 0.0) or 0.0), 6),
            "meta_count": int(meta.get("count", 0) or 0),
            "meta_match_rate": round(float(best_grid.get("match_rate", 0.0) or 0.0), 6),
            "rollout_stage": str(rollout.get("recommended_stage", "shadow") or "shadow"),
        }

        history = []
        if os.path.exists(EFFECT_MONITOR_HISTORY_PATH):
            history = self._load_json_file(EFFECT_MONITOR_HISTORY_PATH)
            if not isinstance(history, list):
                history = []
        if history and history[-1] == snapshot:
            return
        history.append(snapshot)
        history = history[-120:]
        try:
            with open(EFFECT_MONITOR_HISTORY_PATH, "w", encoding="utf-8") as fh:
                json.dump(history, fh, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("[EffectReports] history save failed: %s", exc)

    # ── 효과 검증 통계 수집 ──────────────────────────────────
    def _gather_efficacy_stats(self) -> dict:
        """EfficacyPanel 업데이트용 DB 쿼리 결과 반환 (5분마다 호출)"""
        from utils.db_utils import (
            fetch_calibration_bins, fetch_grade_stats,
            fetch_regime_stats, fetch_accuracy_history,
        )
        try:
            calib  = [dict(r) for r in fetch_calibration_bins(days_back=30)]
            grades = [dict(r) for r in fetch_grade_stats()]
            regime = [dict(r) for r in fetch_regime_stats()]
            hist_rows = fetch_accuracy_history(limit=200)
            hist = [int(r["correct"]) for r in hist_rows if r["correct"] is not None]
        except Exception as e:
            logger.warning(f"[Efficacy] 쿼리 실패: {e}")
            calib, grades, regime, hist = [], [], [], []
        ab_metrics = self._load_json_file(os.path.join(BASE_DIR, "microstructure_ab_metrics.json"))
        calibration_metrics = self._load_json_file(os.path.join(BASE_DIR, "calibration_metrics.json"))
        meta_metrics = self._load_json_file(os.path.join(BASE_DIR, "meta_gate_tuning_metrics.json"))
        rollout_metrics = self._load_json_file(os.path.join(BASE_DIR, "rollout_readiness_metrics.json"))
        report_history = self._load_json_file(EFFECT_MONITOR_HISTORY_PATH)
        if not isinstance(report_history, list):
            report_history = []
        return {
            "calibration_bins": calib,
            "grade_stats": grades,
            "regime_stats": regime,
            "accuracy_history": hist,
            "ab_metrics": ab_metrics,
            "calibration_metrics": calibration_metrics,
            "meta_metrics": meta_metrics,
            "rollout_metrics": rollout_metrics,
            "report_history": report_history,
            "updated_at": datetime.datetime.now().strftime("%H:%M"),
        }

    # ── 당일 Profit Factor 계산 ────────────────────────────────
    def _daily_profit_factor(self) -> float:
        """당일 거래 기록에서 Profit Factor(총이익/총손실) 계산. 손실 0이면 999.0."""
        try:
            rows = fetch_today_trades()
        except Exception:
            return 1.0
        gross_win  = sum(r["forward_pnl_krw"] for r in rows if r["forward_pnl_krw"] > 0)
        gross_loss = sum(abs(r["forward_pnl_krw"]) for r in rows if r["forward_pnl_krw"] < 0)
        if gross_loss == 0:
            return 999.0 if gross_win > 0 else 1.0
        return gross_win / gross_loss

    # ── 추이 통계 수집 ───────────────────────────────────────────
    def _gather_trend_stats(self) -> dict:
        """TrendPanel 업데이트용 일/주/월/연간 집계 반환."""
        try:
            return {
                "일별": fetch_trend_daily(30),
                "주별": fetch_trend_weekly(12),
                "월별": fetch_trend_monthly(12),
                "연간": fetch_trend_yearly(),
                "updated_at": datetime.datetime.now().strftime("%H:%M"),
            }
        except Exception as e:
            logger.warning(f"[Trend] 집계 실패: {e}")
            return {"일별": [], "주별": [], "월별": [], "연간": [], "updated_at": "—"}

    # ── 섀도우 평가 모드 ────────────────────────────────────────
    def start_shadow_mode(
        self,
        candidate_params:  dict,
        wfa_sharpe:        float,
        candidate_version: str,
    ) -> None:
        """
        섀도우 평가기 초기화 (PARAM_CURRENT 미변경).

        param_optimizer.propose_for_shadow() 가 data/shadow_candidate.json을
        생성한 뒤 daily_close() 또는 startup 에서 이 메서드를 호출한다.
        """
        from strategy.shadow_evaluator import ShadowEvaluator
        self._shadow_ev = ShadowEvaluator(
            candidate_version = candidate_version,
            candidate_params  = candidate_params,
            wfa_sharpe        = wfa_sharpe,
        )
        logger.info("[Shadow] 섀도우 모드 시작 — %s (WFA Sharpe=%.2f)",
                    candidate_version, wfa_sharpe)
        try:
            from config.strategy_registry import get_registry as _get_reg
            _get_reg().log_event(
                event_type = "SHADOW_START",
                message    = "섀도우 평가 활성화 (WFA Sharpe=%.2f)" % wfa_sharpe,
                version    = candidate_version,
            )
        except Exception as _le:
            logger.warning("[Shadow] registry log_event 실패: %s", _le)

    def _load_shadow_candidate(self) -> None:
        """
        data/shadow_candidate.json 이 존재하면 섀도우 모드를 자동 시작.
        이미 shadow_ev 가 활성화된 경우에는 스킵.
        """
        if self._shadow_ev is not None:
            return
        import json as _json
        _path = os.path.join("data", "shadow_candidate.json")
        if not os.path.exists(_path):
            return
        try:
            with open(_path, "r", encoding="utf-8") as _f:
                _sc = _json.load(_f)
            self.start_shadow_mode(
                candidate_params  = _sc.get("candidate_params", {}),
                wfa_sharpe        = float(_sc.get("wfa_sharpe", 0.0)),
                candidate_version = _sc.get("candidate_version", "shadow-unknown"),
            )
            logger.info("[Shadow] shadow_candidate.json 자동 로드 완료")
        except Exception as _e:
            logger.warning("[Shadow] shadow_candidate.json 로드 실패: %s", _e)

    # ── 일일 마감 (15:40) ─────────────────────────────────────
    def daily_close(self):
        """자가학습 일일 마감"""
        now = datetime.datetime.now()
        state = self._read_session_state()
        auto_shutdown_done_today = (
            state.get("auto_shutdown_done_date") == now.date().isoformat()
        )
        if auto_shutdown_done_today and now.time() >= datetime.time(15, 40):
            self._auto_shutdown_done_today = True
            self._skip_post_close_cycle_today = True
            self._daily_close_done = True
            logger.info("[System] skip daily_close: auto-shutdown already completed today")
            log_manager.system(
                "[System] 오늘 자동 종료 이력이 있어 일일 마감/자동 종료 재실행을 건너뜁니다.",
                "WARNING",
            )
            return

        stats = self.position.daily_stats()
        forward_stats = self.position.daily_forward_stats()
        logger.info(f"[Daily] 마감 통계: {stats}")
        log_manager.system(
            f"일일 마감 | 승={stats['wins']} 패={stats['losses']} "
            f"PnL={stats['pnl_krw']:+,.0f}원"
        )

        # ── 챔피언-도전자 일별 집계 ─────────────────────────────
        if self.challenger_engine is not None:
            try:
                self.challenger_engine.update_daily_metrics(now.date().isoformat())
            except Exception as _ce2:
                logger.warning("[Challenger] update_daily_metrics 실패 (스킵): %s", _ce2)

        # 일일 배치 재학습 (장 마감 후 — 당일 축적 데이터 반영)
        retrain_result = self.batch_retrainer.retrain_now(weeks_back=8)
        retrain_ok = retrain_result.get("ok", False)
        if retrain_ok:
            self.model._load_all()
            retrain_str = f"재학습 완료 ({retrain_result['elapsed_sec']}초, {retrain_result['data_size']}행)"
            log_manager.learning(
                f"[GBM] 일일 마감 재학습 완료 | {retrain_result['elapsed_sec']}초 "
                f"데이터={retrain_result['data_size']}행"
            )
        else:
            retrain_str = f"재학습 건너뜀 ({retrain_result.get('error', '')})"
            log_manager.learning(
                f"[GBM] 일일 마감 재학습 건너뜀: {retrain_result.get('error','')}"
            )

        # 일일 리셋
        if hasattr(self, "_investor_timer"):
            self._investor_timer.stop()
        self.feature_builder.reset_daily()
        self.micro_regime_clf.reset_daily()
        self.investor_data.reset_daily()
        self.position.reset_daily()
        self.circuit_breaker.reset_daily()
        self.profit_guard.reset_daily()
        self.online_learner.reset_daily()
        self._verified_today = 0
        self.emergency_exit.reset()
        self.kill_switch.deactivate()

        notify(
            f"일일 마감\n승:{stats['wins']} 패:{stats['losses']}\n"
            f"PnL:{stats['pnl_krw']:+,.0f}원",
            "INFO",
        )

        # 일일 스냅샷 저장 → 내일 시작 시 자가학습·추이 패널에 어제 데이터 표시
        today_str = datetime.date.today().isoformat()
        save_daily_stats(today_str, {
            "trades":         forward_stats["trades"],
            "wins":           forward_stats["wins"],
            "pnl_pts":        forward_stats["pnl_pts"],
            "pnl_krw":        forward_stats["pnl_krw"],
            "sgd_accuracy":   self.online_learner.recent_accuracy(),
            "verified_count": self._verified_today,
        })

        # [Phase2] 드리프트 감지 — CUSUM 일별 업데이트
        try:
            from strategy.param_drift_detector import get_drift_detector as _get_dd
            _drift_level, _drift_msg = _get_dd().update(
                daily_pnl = forward_stats["pnl_krw"],
                daily_wr  = forward_stats["wins"] / max(forward_stats["trades"], 1),
                daily_pf  = self._daily_profit_factor(),
            )
            logger.info("[DriftDetector] %s", _drift_msg)
            from strategy.param_drift_detector import DriftLevel as _DL
            if _drift_level >= _DL.WATCHLIST:
                log_manager.system("[경보] DriftDetector: " + _drift_msg)
            # 전략 운용현황 탭에 CUSUM 드리프트 수준 반영
            self.dashboard.update_strategy_ops({"drift_level": _drift_level})
        except Exception as _de:
            logger.warning("[DriftDetector] 업데이트 실패 (스킵): %s", _de)

        # [Phase2] StrategyRegistry — 라이브 일별 스냅샷 기록
        try:
            from config.strategy_registry import get_registry as _get_reg
            from config.strategy_params import PARAM_HISTORY as _PH
            _active_ver = _PH[-1]["version"] if _PH else "v1.0"
            _get_reg().record_live_snapshot(
                version = _active_ver,
                metrics = {
                    "win_rate":      forward_stats["wins"] / max(forward_stats["trades"], 1),
                    "total_trades":  forward_stats["trades"],
                    "daily_pnl":     forward_stats["pnl_krw"],
                    "profit_factor": self._daily_profit_factor(),
                },
            )
        except Exception as _re:
            logger.warning("[Registry] live_snapshot 기록 실패 (스킵): %s", _re)

        self._refresh_pnl_history()
        self.dashboard.update_trend(self._gather_trend_stats())

        # [Phase5] 일일 전략 상태 요약 export + 경보 판정
        try:
            from strategy.ops.daily_exporter import get_exporter as _get_exp
            from strategy.ops.verdict_engine import (
                compute_action, rollback_alert_message,
                ACTION_ROLLBACK_REVIEW, ACTION_REPLACE_CANDIDATE,
            )
            from config.strategy_registry import get_registry as _get_reg
            from strategy.param_drift_detector import get_drift_detector as _get_dd2
            from strategy.regime_fingerprint import get_fingerprint as _get_fp3

            _curr_v   = _get_reg().get_current_version()
            _verd     = _curr_v.get("verdict", "INSUFFICIENT") if _curr_v else "INSUFFICIENT"
            _ldays    = _curr_v.get("live_days", 0) if _curr_v else 0
            _dd2_lvs  = _get_dd2().get_levels() if hasattr(_get_dd2(), "get_levels") else {}
            _dlv2     = max(_dd2_lvs.values()) if _dd2_lvs else 0
            _plv2     = _get_fp3().get_level()
            _action, _reason = compute_action(_verd, _dlv2, _ldays, _plv2)

            # 경보 수준 로그 + registry 이벤트 기록
            _ver_str = _curr_v.get("version", "—") if _curr_v else "—"
            if _action in (ACTION_ROLLBACK_REVIEW, ACTION_REPLACE_CANDIDATE):
                _alert = rollback_alert_message(
                    _ver_str, _verd, _dlv2, _action, _reason,
                    pnl_today=stats.get("pnl_krw", 0),
                )
                log_manager.system(_alert, "WARNING")
            try:
                _get_reg().log_event(
                    event_type = _action,
                    message    = _reason[:120],
                    note       = "PnL %+.0f원  verdict=%s  drift=%d" % (
                        stats.get("pnl_krw", 0), _verd, _dlv2),
                    version    = _ver_str if _ver_str != "—" else None,
                )
            except Exception as _ev_e:
                logger.warning("[Phase5] log_event 실패: %s", _ev_e)

            # 일일 리포트 파일 저장
            _exp    = _get_exp()
            _report = _exp.build_report()
            _exp.save(_report)
            logger.info("[Phase5] 일일 전략 리포트 저장 완료")
        except Exception as _ph5_e:
            logger.warning("[Phase5] 일일 export 실패 (스킵): %s", _ph5_e)

        # [Shadow] shadow_candidate.json 체크 → 섀도우 자동 시작
        self._load_shadow_candidate()

        # ── 자동 종료 예약 ────────────────────────────────────────
        win_rate = stats["wins"] / max(stats["trades"], 1)
        pnl_sign = "+" if stats["pnl_krw"] >= 0 else ""
        notify(
            f"🏁 미륵이 일일 마감 완료 — 자동 종료 예정\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"거래: {stats['trades']}회 (승 {stats['wins']} / 패 {stats['losses']})\n"
            f"승률: {win_rate:.0%}  PnL: {pnl_sign}{stats['pnl_krw']:,.0f}원\n"
            f"{retrain_str}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"15초 후 프로그램 자동 종료\n"
            f"다음 시작: 내일 08:45 이후",
            "INFO",
        )
        if self._auto_shutdown_done_today:
            log_manager.system("오늘 자동 종료가 이미 실행되어 자동 종료 예약을 생략합니다.", "WARNING")
            self.dashboard.append_sys_log("오늘 자동 종료 이력 감지 — 자동 종료 예약 생략")
            return
        log_manager.system("자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료")
        self.dashboard.append_sys_log("자동 종료 예약 — 15초 후 프로그램 종료")
        QTimer.singleShot(15_000, self._auto_shutdown)

    def _auto_shutdown(self) -> None:
        """일일 마감 완료 후 자동 프로그램 종료 — Qt 이벤트 루프 종료."""
        state = self._read_session_state()
        state["date"] = datetime.date.today().isoformat()
        state["auto_shutdown_done_date"] = datetime.date.today().isoformat()
        self._write_session_state(state)
        self._auto_shutdown_done_today = True
        self._skip_post_close_cycle_today = True
        logger.info("[System] 자동 종료 실행")
        log_manager.system("미륵이 자동 종료")
        _qt_app.quit()

    # ── 파이프라인 생존 감시 ──────────────────────────────────────

    def _on_pipeline_watchdog(self, elapsed_s: int) -> None:
        """분봉 파이프라인 지연 감지 시 경보 탭 로그 + 단계별 복구 조치.

        임계값 (1분봉 주기=60s 기준 — 30s 버퍼 확보):
          90s  — 경보 로그 (분봉 30초 지연)
         150s  — 경보 로그 + 알림 (심각)
         240s  — 경보 로그 + 알림 + raw_candles 강제 재실행
        """
        m, s = divmod(elapsed_s, 60)
        elapsed_str = f"{m}분 {s:02d}초"

        if elapsed_s >= 240:
            msg = (f"⛔ 파이프라인 {elapsed_str} 미실행 — 원인 불명. 긴급 복구 시도 중  "
                   f"가능한 원인: ① API 무응답 ② on_candle_closed 미호출 "
                   f"③ STEP 내 예외 누락 ④ 장외 시간")
            log_manager.system(msg, "WARNING")
            notify(f"🚨 미륵이 파이프라인 {elapsed_str} 정지 — 긴급 복구 시도")
            QTimer.singleShot(300, self._try_pipeline_recovery)

        elif elapsed_s >= 150:
            msg = (f"⚠ 파이프라인 {elapsed_str} 미실행 — 분봉 수신 또는 API 상태 이상  "
                   f"다음 90초 내 미복구 시 긴급 복구 자동 실행")
            log_manager.system(msg, "WARNING")
            notify(f"⚠ 미륵이 파이프라인 {elapsed_str} 지연 — 90초 내 미복구 시 자동 조치")

        else:  # 90s
            msg = (f"⚠ 파이프라인 {elapsed_str} 미실행 — 분봉 수신 지연 의심  "
                   f"장 시간({is_market_open()}) 확인. 다음 분봉에서 자동 회복 기대")
            log_manager.system(msg, "WARNING")

    def _try_pipeline_recovery(self) -> None:
        """raw_candles 최신 분봉으로 파이프라인 강제 재실행."""
        from utils.db_utils import fetchone
        from config.settings import RAW_DATA_DB

        try:
            row = fetchone(
                RAW_DATA_DB,
                "SELECT * FROM raw_candles ORDER BY ts DESC LIMIT 1",
            )
        except Exception as e:
            log_manager.system(f"[복구 실패] DB 조회 오류: {e}", "WARNING")
            return

        if not row:
            log_manager.system("[복구 실패] raw_candles 비어 있음 — 분봉 데이터 없음", "WARNING")
            if self.position.status != "FLAT":
                log_manager.system("[포지션 경보] 파이프라인 정지 중 포지션 보유 — 수동 확인 필요", "WARNING")
            return

        ts_str = row["ts"]  # "YYYY-MM-DD HH:MM:SS"

        # 동일 분봉 반복 재처리 방지 — 이미 복구한 ts면 스킵 후 감시 리셋
        if ts_str == self._last_recovery_ts:
            log_manager.system(
                f"[복구 스킵] {ts_str} 이미 재처리 완료 — 새 분봉 대기 중",
            )
            self.dashboard.notify_pipeline_ran()   # 워치독 카운터 리셋
            return

        try:
            ts = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            log_manager.system(f"[복구 실패] ts 파싱 오류: {ts_str}", "WARNING")
            return

        age_s = int((datetime.datetime.now() - ts).total_seconds())
        if age_s > 600:
            log_manager.system(
                f"[복구 포기] 최신 분봉이 {age_s}초 전 데이터 — 재처리 무의미 (장외 시간?)", "WARNING"
            )
            if self.position.status != "FLAT":
                log_manager.system(
                    "[포지션 경보] 파이프라인 장기 정지 + 포지션 보유 — 수동 청산 검토 필요", "WARNING"
                )
            return

        bar = {
            "ts":       ts,
            "open":     float(row["open"]),
            "high":     float(row["high"]),
            "low":      float(row["low"]),
            "close":    float(row["close"]),
            "volume":   int(row["volume"] or 0),
            "buy_vol":  0,
            "sell_vol": 0,
        }
        self._last_recovery_ts = ts_str   # 이 ts를 처리 완료로 기록
        log_manager.system(f"[복구 시도] {ts_str} 분봉 강제 재처리...")
        try:
            self.run_minute_pipeline(bar)
            log_manager.system("[복구 완료] 파이프라인 재실행 성공 — 정상 감시 재개")
        except Exception as e:
            log_manager.system(f"[복구 실패] 파이프라인 예외: {e}", "WARNING")

    # ── 재시작 복원 ───────────────────────────────────────────────

    def _increment_session(self) -> int:
        """data/session_state.json 에 세션 카운터를 1 증가하고 현재 번호를 반환."""
        data = self._read_session_state()
        today = datetime.date.today().isoformat()
        if data.get("date") != today:
            data = {
                "date": today,
                "count": 0,
                "reverse_entry_enabled": bool(data.get("reverse_entry_enabled", False)),
                "tp1_single_contract_mode": str(
                    data.get("tp1_single_contract_mode", "breakeven") or "breakeven"
                ).strip().lower(),
                "auto_shutdown_done_date": "",
            }
        data["count"] = data.get("count", 0) + 1
        data["reverse_entry_enabled"] = bool(self._reverse_entry_enabled)
        data["tp1_single_contract_mode"] = str(
            getattr(self, "_tp1_protect_mode", "breakeven") or "breakeven"
        ).strip().lower()
        self._write_session_state(data)
        return data["count"]

    def _restore_daily_state(self) -> None:
        """재시작 시 당일 거래 이력을 trades.db 에서 읽어 대시보드 로그에 복원."""
        today_str = datetime.date.today().isoformat()
        rows = fetch_today_trades(today_str)
        if not rows:
            return

        session_no = self._session_no
        self.dashboard.append_trade_separator(
            f"── 세션 #{session_no} 시작 — 이전 거래 {len(rows)}건 복원 ({today_str}) ──"
        )
        self.dashboard.append_pnl_separator(
            f"── 세션 #{session_no} 시작 — 이전 거래 {len(rows)}건 복원 ({today_str}) ──"
        )

        cumulative_pnl_krw = 0.0
        cumulative_forward_pnl_krw = 0.0
        for row in rows:
            direction  = row["direction"] or "?"
            entry_p    = row["entry_price"] or 0.0
            exit_p     = row["exit_price"]
            qty        = row["quantity"] or 1
            pnl_pts    = row["pnl_pts"] or 0.0
            pnl_krw    = row["pnl_krw"] or 0.0
            forward_pnl_pts = row["forward_pnl_pts"] or pnl_pts
            forward_pnl_krw = row["forward_pnl_krw"] or pnl_krw
            reason     = row["exit_reason"] or ""
            grade      = row["grade"] or ""
            entry_ts   = (row["entry_ts"] or "")[:16]   # "YYYY-MM-DD HH:MM"
            exit_ts    = (row["exit_ts"]  or "")[:16]

            if exit_p is not None:
                # 청산 완료 거래
                cumulative_pnl_krw += pnl_krw
                cumulative_forward_pnl_krw += forward_pnl_krw
                self.dashboard.append_restore_trade(
                    msg=f"진입 {direction} {qty}계약 @ {entry_p}  등급={grade}",
                    ts=entry_ts[11:] if len(entry_ts) > 11 else entry_ts,
                )
                self.dashboard.append_restore_trade(
                    msg=f"청산 {direction} {qty}계약 @ {exit_p}  ({reason})",
                    ts=exit_ts[11:] if len(exit_ts) > 11 else exit_ts,
                    val=(
                        f"실행 {pnl_pts:+.2f}pt  {pnl_krw:+,.0f}원 | "
                        f"순방향 {forward_pnl_pts:+.2f}pt  {forward_pnl_krw:+,.0f}원"
                    ),
                )
                self.dashboard.append_restore_pnl(
                    msg=f"청산 | {direction} {qty}계약 @ {exit_p}  ({reason})",
                    ts=exit_ts[11:] if len(exit_ts) > 11 else exit_ts,
                    val=(
                        f"실행 {pnl_pts:+.2f}pt  {pnl_krw:+,.0f}원 (누적 {cumulative_pnl_krw:+,.0f}원) | "
                        f"순방향 {forward_pnl_pts:+.2f}pt  {forward_pnl_krw:+,.0f}원 "
                        f"(누적 {cumulative_forward_pnl_krw:+,.0f}원)"
                    ),
                )
            else:
                # 진입만 있고 청산 미완료 (비정상 종료)
                self.dashboard.append_restore_trade(
                    msg=f"[미청산] 진입 {direction} {qty}계약 @ {entry_p}  등급={grade}",
                    ts=entry_ts[11:] if len(entry_ts) > 11 else entry_ts,
                )

        # position_tracker 일일 통계 복원
        self.position.reset_daily()
        self.position.restore_daily_stats(rows)

        # 손익 PnL 패널 즉시 갱신 — 재시작 후 "——원" 방지
        _daily = self.position.daily_stats()
        _forward_daily = self.position.daily_forward_stats()
        self.dashboard.update_pnl_metrics(
            0.0,
            _daily["pnl_krw"],
            0.0,
            forward_unrealized_krw=0.0,
            forward_daily_pnl_krw=_forward_daily["pnl_krw"],
        )

        logger.info(f"[Restore] 당일 거래 {len(rows)}건 복원 완료 | 누적 PnL={cumulative_pnl_krw:+,.0f}원")
        log_manager.system(
            f"재시작 복원 완료 | 거래 {len(rows)}건 | 누적 PnL={cumulative_pnl_krw:+,.0f}원"
        )
        self._refresh_pnl_history()

    def _restore_panels_from_history(self) -> None:
        """시작 시 DB 이력으로 자가학습·효과검증·추이 패널 선조회.
        파이프라인이 처음 실행되기 전까지 이전 데이터를 표시한다.
        """
        try:
            self.dashboard.update_learning(self._gather_learning_stats())
        except Exception as e:
            logger.debug(f"[Restore] 자가학습 패널 선조회 실패: {e}")
        try:
            self.dashboard.update_efficacy(self._gather_efficacy_stats())
        except Exception as e:
            logger.debug(f"[Restore] 효과검증 패널 선조회 실패: {e}")
        try:
            self.dashboard.update_trend(self._gather_trend_stats())
        except Exception as e:
            logger.debug(f"[Restore] 추이 패널 선조회 실패: {e}")

    def _refresh_pnl_history(self) -> None:
        """trades.db 최근 90일 조회 → 손익 추이 패널 갱신."""
        try:
            rows = fetch_pnl_history(limit_days=90)
            self.dashboard.update_pnl_history(rows)
        except Exception as e:
            logger.debug(f"[PnL History] 갱신 실패: {e}")
        # 수익 보존 가드 패널 갱신 (청산 직후 최신 트레이드 반영)
        try:
            today_trades = fetch_today_trades() or []
            daily_pnl = self.position.daily_stats()["pnl_krw"]
            self.dashboard.refresh_profit_guard(daily_pnl, today_trades)
        except Exception as _pge2:
            pass

    # ── 메인 루프 (Qt 이벤트 루프 기반) ──────────────────────────
    def run(self):
        """메인 실행 — Qt 이벤트 루프 기반."""
        logger.info("=" * 60)
        logger.info("미륵이 — KOSPI 200 선물 방향 예측 시스템 시작")
        logger.info("=" * 60)

        # 키움 로그인 (블로킹)
        if not self.connect_kiwoom():
            logger.critical("[System] 키움 연결 실패 — 종료")
            return

        self._pre_market_done   = False
        self._daily_close_done  = False

        # 1분 주기 관리 타이머 (분봉 파이프라인은 on_candle_closed 콜백으로 구동)
        self._scheduler = QTimer()
        self._scheduler.setInterval(30_000)   # 30초마다 체크
        self._scheduler.timeout.connect(self._scheduler_tick)
        self._scheduler.start()

        self._balance_ui_timer = QTimer()
        self._balance_ui_timer.setInterval(2_000)
        self._balance_ui_timer.timeout.connect(self._refresh_dashboard_balance_ui_only)
        self._balance_ui_timer.start()

        # 대시보드 표시 + 긴급정지 버튼 연결
        self.dashboard.show()
        if hasattr(self.dashboard, "btn_kill"):
            self.dashboard.btn_kill.clicked.connect(
                lambda: self.activate_kill_switch("대시보드 긴급정지")
            )
        if self.realtime_data:
            _bn = getattr(self.broker, "name", "")
            if _bn == "cybos":
                _srv_lbl = "Cybos 실서버"
                _rt_method = "FutureCurOnly/Subscribe"
            else:
                _srv = self.broker.get_login_info("GetServerGubun")
                _srv_lbl = "모의투자" if _srv == "1" else "실서버"
                _rt_method = "SetRealReg"
            self.dashboard.append_sys_log(
                f"시스템 시작 | TR={self.realtime_data.code} [{_srv_lbl}] 분봉수집=실시간({_rt_method})"
            )
        else:
            self.dashboard.append_sys_log("시스템 시작 | 코드=—")
        self.dashboard.update_system_status(cb_state="NORMAL", latency_ms=0.0)

        # 파이프라인 감시 콜백 등록
        self.dashboard.set_pipeline_watchdog_cb(self._on_pipeline_watchdog)

        # 세션 카운터 증가 + 당일 거래 이력 복원
        self._session_no = self._increment_session()
        self._restore_daily_state()

        # 자가학습·효과검증·추이 패널: DB 이력으로 선조회 (파이프라인 첫 실행 전까지 이전 데이터 표시)
        QTimer.singleShot(500, self._restore_panels_from_history)

        # 이벤트 루프 진입 2초 후 초기 대기 상태 즉시 출력
        QTimer.singleShot(2000, lambda: self._log_waiting_status(datetime.datetime.now()))

        logger.info("[System] Qt 이벤트 루프 진입")
        _qt_app.exec_()


    def _scheduler_tick(self) -> None:
        """30초마다 호출 — 장 전 준비 / 일일 마감 / 연결 감시."""
        now = datetime.datetime.now()

        # 5분(10 tick)마다 현재 상태 로그
        self._heartbeat_count += 1
        if self._heartbeat_count % 10 == 0:
            self._log_waiting_status(now)

        # 장 전 준비 (08:45~, KRX 거래일만)
        if not self._pre_market_done and now.time() >= datetime.time(8, 45) and is_trading_day(now):
            self.pre_market_setup()
            self.latency_sync.reset_daily()
            self._pre_market_done  = True
            self._daily_close_done = False

        # 일일 마감 (15:40~, KRX 거래일만)
        if (
            not self._daily_close_done
            and now.time() >= datetime.time(15, 40)
            and is_trading_day(now)
        ):
            if self._skip_post_close_cycle_today:
                self._daily_close_done = True
                logger.info("[System] today auto-shutdown already executed; skip daily_close on manual restart")
                return
            if self.realtime_data:
                self.realtime_data.stop()
            self.daily_close()
            self._pre_market_done  = False
            self._daily_close_done = True

        # 키움 연결 감시
        if not self.broker.is_connected:
            logger.error("[System] 키움 연결 끊김 — 재연결 시도")
            self.connect_broker()

    def _log_waiting_status(self, now: datetime.datetime) -> None:
        """현재 대기 이유를 로그 + 대시보드에 표시."""
        t = now.time()
        broker_name = getattr(self.broker, "name", "broker")
        if is_market_open(now):
            if broker_name == "cybos":
                reason = "장중 — Cybos 실시간 분봉 대기 중 (FutureCurOnly/FutureJpBid 수신 시 자동 진행)"
            else:
                reason = "장중 — Kiwoom FC0 실시간 틱 대기 중 (분봉 파이프라인은 틱 수신 시 자동 실행)"
        elif not is_trading_day(now):
            if now.weekday() >= 5:
                reason = "주말 — 다음 KRX 거래일 08:45 재개"
            else:
                reason = "공휴일·휴장일 — 다음 KRX 거래일 08:45 재개"
        elif t < datetime.time(8, 45):
            reason = "장 전 — 매크로 수집 대기 (08:45 자동 시작)"
        elif t < datetime.time(9, 0):
            reason = "장 개시 대기 — 09:00 분봉 파이프라인 시작 예정"
        else:
            reason = "장 마감 후 — 내일 08:45 매크로 수집 재개"

        _cb_state = self.circuit_breaker.state
        if _cb_state != "NORMAL" and is_market_open(now):
            reason = f"CB {_cb_state} — 신규 진입 정지 | {reason}"
        logger.info(
            "[System] 대기 중 | %s | 레짐=%s | 포지션=%s | %s",
            reason, self.current_regime,
            self.position.status, now.strftime("%H:%M:%S"),
        )
        self.dashboard.append_sys_log(f"[{now.strftime('%H:%M')}] {reason}")


def _ts_parse_chejan_time(time_str: str) -> datetime.datetime:
    s = "".join(ch for ch in str(time_str or "").strip() if ch.isdigit())
    now = datetime.datetime.now()
    if len(s) >= 6:
        hh, mm, ss = int(s[0:2]), int(s[2:4]), int(s[4:6])
        micro = int(s[6:9]) * 1000 if len(s) >= 9 else 0
        try:
            return now.replace(hour=hh, minute=mm, second=ss, microsecond=micro)
        except ValueError:
            return now
    return now


def _ts_order_side_to_direction(order_gubun: str) -> str:
    text = str(order_gubun or "").strip()
    if "매수" in text:
        return "LONG"
    if "매도" in text:
        return "SHORT"
    return ""


def _ts_on_order_message(self, payload: dict) -> None:
    msg = str(payload.get("msg") or payload.get("message") or "")
    _ts_log_diag(
        self,
        "OrderMsgFlow",
        pending=_ts_get_pending_snapshot(self),
        rq=payload.get("rq_name", ""),
        tr=payload.get("tr_code", ""),
        source=payload.get("source", ""),
        status_code=payload.get("status_code", ""),
        msg=msg,
    )
    if not self._pending_order:
        return
    if any(token in msg for token in ("거부", "실패", "오류")):
        log_manager.system(
            f"[Order] 주문 거부/오류 source={payload.get('source', '')} "
            f"status={payload.get('status_code', '')} msg={msg}",
            "ERROR",
        )
        self._clear_pending_order()


def _ts_execute_entry(self, direction: str, price: float, quantity: int, atr: float, grade: str):
    if self._has_pending_order():
        return
    ret = self._send_kiwoom_entry_order(direction, quantity)
    if ret != 0:
        logger.error("[Entry] SendOrder 실패로 내부 포지션 오픈을 취소합니다. ret=%s", ret)
        log_manager.system(
            f"[Entry] 주문 실패로 포지션 미오픈 ret={ret} dir={direction} qty={quantity}",
            "ERROR",
        )
        return
    self._set_pending_order(
        kind="ENTRY",
        direction=direction,
        qty=quantity,
        price_hint=price,
        reason="진입",
        atr=atr,
        grade=grade,
    )
    # 투기적 포지션 오픈 — Chejan 없는 환경(모의투자)에서도 이중진입을 방지.
    # 실서버에서 Chejan이 도착하면 apply_entry_fill()이 _optimistic=True를 감지해
    # 수량 증가 없이 체결가만 보정한다.
    self.position.open_position(direction, price, quantity, atr, grade, self.current_regime)
    self.position._optimistic = True
    log_manager.trade(
        f"[주문요청] {direction} {quantity}계약 @ {price} 등급={grade} 체결대기"
    )


def _ts_execute_partial_exit(self, price: float, stage: int) -> None:
    _ts_log_diag(
        self,
        "PartialExitAttempt",
        stage=stage,
        price=price,
        pending=_ts_get_pending_snapshot(self),
        position=_ts_get_position_snapshot(self),
    )
    if self._has_pending_order():
        return
    total_qty = self.position.quantity
    if total_qty == 1 and stage == 1:
        atr = _ts_get_reference_atr(self)
        protect_mode = str(getattr(self, "_tp1_protect_mode", "breakeven") or "breakeven").strip().lower()
        protect = self.position.arm_tp1_single_contract_with_mode(
            price,
            atr,
            mode=protect_mode,
            alpha_pts=TP1_PROTECT_PLUS_ALPHA_PTS,
            atr_lock_mult=TP1_PROTECT_ATR_LOCK_MULT,
        )
        _ts_log_diag(
            self,
            "SingleContractTP1Arm",
            stage=stage,
            price=price,
            atr=atr,
            mode=protect_mode,
            protect_offset_pts=protect.get("protect_offset_pts", 0.0),
            stop_before=protect["prev_stop_price"],
            stop_after=protect["new_stop_price"],
            position=_ts_get_position_snapshot(self),
        )
        log_manager.system(
            f"[SingleContractTP1] 1계약 TP1 도달 -> 보호전환 {self.position.status} "
            f"mode={protect_mode} price={price:.2f} stop={protect['prev_stop_price']:.2f}->{protect['new_stop_price']:.2f}",
            "WARNING",
        )
        self.dashboard.append_pnl_log(
            f"TP1 보호전환 | {self.position.status} 1계약 @ {price:.2f}",
            f"{protect_mode} | stop {protect['prev_stop_price']:.2f} -> {protect['new_stop_price']:.2f}",
        )
        return
    ratio = PARTIAL_EXIT_RATIOS[stage - 1]
    partial_qty = max(1, round(total_qty * ratio))
    is_full_close = partial_qty >= total_qty
    send_qty = total_qty if is_full_close else partial_qty
    reason = f"TP{stage}(전량)" if is_full_close else f"TP{stage} 부분청산 {ratio:.0%}"

    ret = self._send_kiwoom_exit_order(send_qty)
    _ts_log_diag(
        self,
        "PartialExitSendOrderResult",
        stage=stage,
        ret=ret,
        send_qty=send_qty,
        reason=reason,
        position=_ts_get_position_snapshot(self),
    )
    if ret != 0:
        log_manager.system(
            f"[Exit] 청산 주문 실패 ret={ret} stage={stage} qty={send_qty}",
            "ERROR",
        )
        return

    self._set_pending_order(
        kind="EXIT_FULL" if is_full_close else "EXIT_PARTIAL",
        direction=self.position.status,
        qty=send_qty,
        price_hint=price,
        reason=reason,
        stage=stage,
    )
    log_manager.trade(
        f"[주문요청] TP{stage} 청산 {self.position.status} {send_qty}계약 @ {price} 체결대기"
    )


def _ts_check_exit_triggers(self, price: float, features: dict, decision: dict, bar: dict = None):
    atr = features.get("atr", 0.5)

    if self.position.status != "FLAT":
        _mult = 1 if self.position.status == "LONG" else -1
        _upnl = self.position.unrealized_pnl_pts(price)
        _stop_dist = (price - self.position.stop_price) * _mult
        _tp1_dist = (self.position.tp1_price - price) * _mult
        _tp2_dist = (self.position.tp2_price - price) * _mult
        debug_log.debug(
            "[DBG-F8] %s %dct @%.2f cur=%.2f upnl=%+.2fpt"
            " | stop_dist=%.2f tp1=%.2f tp2=%.2f | stop=%.2f | p1=%s p2=%s",
            self.position.status, self.position.quantity,
            self.position.entry_price, price, _upnl,
            _stop_dist, _tp1_dist, _tp2_dist,
            self.position.stop_price,
            "O" if self.position.partial_1_done else "X",
            "O" if self.position.partial_2_done else "X",
        )

    self.position.update_trailing_stop(price, atr)

    if self._has_pending_order():
        return

    if self.position.is_stop_hit(price):
        bar_low = bar["low"] if bar else price
        bar_high = bar["high"] if bar else price
        if self.position.status == "LONG":
            exit_price = max(self.position.stop_price, bar_low)
        else:
            exit_price = min(self.position.stop_price, bar_high)
        log_manager.system(
            f"[ExitAttempt] 하드스톱 {self.position.status} {self.position.quantity}ct "
            f"exit_price={exit_price:.2f} stop={self.position.stop_price:.2f} cur={price:.2f}",
            "WARNING",
        )
        ret = self._send_kiwoom_exit_order(self.position.quantity)
        log_manager.system(
            f"[ExitSendOrderResult] ret={ret} kind=하드스톱 "
            f"direction={self.position.status} qty={self.position.quantity}",
            "WARNING",
        )
        if ret == 0:
            self._set_pending_order(
                kind="EXIT_FULL",
                direction=self.position.status,
                qty=self.position.quantity,
                price_hint=round(exit_price, 2),  # [B50] float 오차 방지
                reason="하드스톱",
            )
            log_manager.trade(
                f"[주문요청] 하드스톱 청산 {self.position.status} {self.position.quantity}계약 @ {exit_price:.2f}"
            )
        else:
            log_manager.system(f"[Exit] 하드스톱 주문 실패 ret={ret}", "ERROR")
        return

    if (not self._has_pending_order()
            and self.position.status != "FLAT"
            and self.position.is_tp1_hit(price)):
        self._execute_partial_exit(price, stage=1)

    if (not self._has_pending_order()
            and self.position.status != "FLAT"
            and self.position.is_tp2_hit(price)):
        self._execute_partial_exit(price, stage=2)

    if not self._has_pending_order() and self.time_exit.should_force_exit():
        log_manager.system(
            f"[ExitAttempt] 시간청산 {self.position.status} {self.position.quantity}ct "
            f"price={price:.2f}",
            "WARNING",
        )
        ret = self._send_kiwoom_exit_order(self.position.quantity)
        log_manager.system(
            f"[ExitSendOrderResult] ret={ret} kind=시간청산 "
            f"direction={self.position.status} qty={self.position.quantity}",
            "WARNING",
        )
        if ret == 0:
            self._set_pending_order(
                kind="EXIT_FULL",
                direction=self.position.status,
                qty=self.position.quantity,
                price_hint=round(price, 2),  # [B50] float 오차 방지
                reason="15:10 강제청산",
            )
            log_manager.trade(
                f"[주문요청] 시간청산 {self.position.status} {self.position.quantity}계약 @ {price:.2f}"
            )
        else:
            log_manager.system(f"[Exit] 시간청산 주문 실패 ret={ret}", "ERROR")


def _ts_in_exit_cooldown(self, now: datetime.datetime = None):
    now = now or datetime.datetime.now()
    until = getattr(self, "_exit_cooldown_until", None)
    if until is None:
        return False, 0
    remain = (until - now).total_seconds()
    if remain <= 0:
        return False, 0
    return True, int(remain)


def _ts_apply_exit_cooldown(self, result: dict, filled_at: datetime.datetime = None) -> None:
    now = filled_at or datetime.datetime.now()
    pnl = float(result.get("pnl_pts", 0.0) or 0.0)
    cooldown_min = 2 if pnl > 0 else 3
    self._exit_cooldown_until = now + datetime.timedelta(minutes=cooldown_min)
    self._last_exit_reason = result.get("exit_reason", "")
    self._last_exit_ts = now
    msg = (
        f"[ExitCooldown] {result.get('exit_reason', '청산')} 후 {cooldown_min}분 재진입 금지 "
        f"(until {self._exit_cooldown_until.strftime('%H:%M:%S')})"
    )
    logger.warning(msg)
    log_manager.system(msg, "WARNING")


def _ts_order_side_to_direction(payload_or_order_gubun) -> str:
    if isinstance(payload_or_order_gubun, dict):
        payload = payload_or_order_gubun
        trade_gubun = str(payload.get("trade_gubun", "")).strip()
        if trade_gubun in ("2", "+2", "매수", "+매수"):
            return "LONG"
        if trade_gubun in ("1", "-1", "매도", "-매도"):
            return "SHORT"
        text = str(payload.get("order_gubun", "")).strip()
    else:
        text = str(payload_or_order_gubun or "").strip()

    if any(token in text for token in ("+매수", "매수", "2")):
        return "LONG"
    if any(token in text for token in ("-매도", "매도", "1")):
        return "SHORT"
    return ""


def _ts_get_position_snapshot(self) -> str:
    if self.position.status == "FLAT":
        return "FLAT"
    return f"{self.position.status} {self.position.quantity}계약 @ {self.position.entry_price:.2f}"


def _ts_get_pending_snapshot(self) -> str:
    pending = getattr(self, "_pending_order", None)
    if not pending:
        return "NONE"
    return (
        f"{pending.get('kind')}:{pending.get('direction')} qty={pending.get('qty')} "
        f"filled={pending.get('filled_qty', 0)} order_no={pending.get('order_no') or '?'} "
        f"reason={pending.get('reason', '')} req_at={pending.get('requested_at', '?')}"
    )


def _ts_log_diag(self, tag: str, **fields) -> None:
    parts = [f"{k}={fields[k]!r}" for k in sorted(fields)]
    logger.warning("[%s] %s", tag, " | ".join(parts))


def _ts_should_emit_throttled(self, key: str, min_interval_sec: float = 60.0) -> bool:
    state = getattr(self, "_throttled_info_ts", None)
    if state is None:
        state = {}
        setattr(self, "_throttled_info_ts", state)
    now = time.time()
    last = float(state.get(key, 0.0) or 0.0)
    if (now - last) < float(min_interval_sec):
        return False
    state[key] = now
    return True


def _ts_system_info_throttled(self, key: str, message: str, min_interval_sec: float = 60.0) -> None:
    if not _ts_should_emit_throttled(self, key, min_interval_sec=min_interval_sec):
        return
    log_manager.system(message, "INFO")


def _ts_logger_info_throttled(self, key: str, message: str, *args, min_interval_sec: float = 60.0) -> None:
    if not _ts_should_emit_throttled(self, key, min_interval_sec=min_interval_sec):
        return
    logger.info(message, *args)


def _ts_get_reference_atr(self, pending: Optional[dict] = None) -> float:
    if pending and float(pending.get("atr") or 0.0) > 0:
        return float(pending["atr"])

    if self.position.status != "FLAT" and self.position.stop_price:
        stop_dist = abs(self.position.entry_price - self.position.stop_price)
        if stop_dist > 0:
            return max(stop_dist / ATR_STOP_MULT, 0.5)

    atr_buf = getattr(self.feature_builder.atr, "_atr_buf", None)
    if atr_buf:
        try:
            return max(float(atr_buf[-1]), 0.5)
        except Exception:
            pass

    return 0.5


def _ts_record_nonfinal_exit(self, result: dict, reason_label: str) -> None:
    pnl = result["pnl_pts"]
    qty = result["quantity"]

    if pnl > 0:
        self.circuit_breaker.record_win()
        self.kelly.record(win=True, pnl_pts=pnl)
    else:
        self.circuit_breaker.record_stop_loss()
        self.kelly.record(win=False, pnl_pts=pnl)

    log_manager.trade(
        f"[체결청산-부분] {result['direction']} {qty}계약 @ {result['exit_price']:.2f} "
        f"| PnL={pnl:+.2f}pt ({result['pnl_krw']:+,.0f}원) "
        f"| 잔여={result['remaining']}계약 | 사유={reason_label}"
    )
    _daily = self.position.daily_stats()
    _forward_daily = self.position.daily_forward_stats()
    self.dashboard.append_pnl_log(
        f"체결청산-부분 | {result['direction']} {qty}계약 @ {result['exit_price']:.2f}",
        f"PnL {pnl:+.2f}pt  {result['pnl_krw']:+,.0f}원  잔여 {result['remaining']}계약  │ 금일 {_daily['pnl_krw']:+,.0f}원",
    )
    self.dashboard.update_pnl_metrics(
        self.position.unrealized_pnl_pts(result["exit_price"]) * self._pt_value,
        _daily["pnl_krw"],
        0.0,
        forward_unrealized_krw=self.position.unrealized_forward_pnl_pts(result["exit_price"]) * self._pt_value,
        forward_daily_pnl_krw=_forward_daily["pnl_krw"],
    )
    self._record_trade_result(result)
    self._refresh_pnl_history()


def _ts_on_order_message(self, payload: dict) -> None:
    if not self._pending_order:
        return
    msg = str(payload.get("msg") or payload.get("message") or "")
    if any(token in msg for token in ("거부", "실패", "오류")):
        log_manager.system(
            f"[Order] 주문 거부/오류 source={payload.get('source', '')} "
            f"status={payload.get('status_code', '')} msg={msg}",
            "ERROR",
        )
        self._clear_pending_order()


def _ts_handle_entry_fill(
    self,
    pending: dict,
    payload: dict,
    fill_qty: int,
    fill_price: float,
    filled_at: datetime.datetime,
) -> None:
    actual_side = _ts_order_side_to_direction(payload)
    entry_direction = actual_side or pending["direction"]
    before = _ts_get_position_snapshot(self)
    if actual_side and actual_side != pending["direction"]:
        log_manager.system(
            f"[OrderSync] 엔트리 방향 불일치 pending={pending['direction']} actual={actual_side} "
            f"order_no={payload.get('order_no') or '?'}",
            "CRITICAL",
        )

    result = self.position.apply_entry_fill(
        direction=entry_direction,
        price=fill_price,
        quantity=fill_qty,
        atr=_ts_get_reference_atr(self, pending),
        grade=pending["grade"],
        regime=self.current_regime,
        filled_at=filled_at,
        raw_direction=pending.get("raw_direction") or pending["direction"],
        reverse_entry_enabled=bool(pending.get("reverse_entry_enabled", False)),
    )
    if before.get("status") == "FLAT":
        self.dashboard.minute_chart_record_entry(
            entry_direction,
            fill_price,
            filled_at,
        )
    log_manager.trade(
        f"[체결진입] {entry_direction} {fill_qty}계약 @ {fill_price} "
        f"| 평균={result['avg_entry_price']} 보유={result['position_qty']}계약"
    )
    self.dashboard.append_pnl_log(
        f"체결진입 | {entry_direction} {fill_qty}계약 @ {fill_price}",
        f"평균 {self.position.entry_price:.2f} 손절 {self.position.stop_price:.2f} 1차 {self.position.tp1_price:.2f}",
    )
    self.dashboard.set_ui_position_mode()
    _ts_log_diag(
        self,
        "EntryFillFlow",
        before=before,
        after=_ts_get_position_snapshot(self),
        pending=_ts_get_pending_snapshot(self),
        actual_side=actual_side,
        applied_side=entry_direction,
        fill_qty=fill_qty,
        fill_price=fill_price,
        order_no=payload.get("order_no", ""),
        fill_no=payload.get("fill_no", ""),
    )
    _ts_system_info_throttled(self, "balance_refresh_trigger_entry", "[BalanceRefresh] trigger=EntryFillFlow", min_interval_sec=30.0)
    QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))


def _ts_handle_exit_fill(
    self,
    pending: dict,
    payload: dict,
    fill_qty: int,
    fill_price: float,
    filled_at: datetime.datetime,
) -> None:
    before = _ts_get_position_snapshot(self)
    result = self.position.apply_exit_fill(
        exit_price=fill_price,
        quantity=fill_qty,
        reason=pending["reason"],
        filled_at=filled_at,
    )

    if pending["kind"] == "EXIT_PARTIAL":
        if pending.get("stage") == 1:
            self.position.partial_1_done = True
        elif pending.get("stage") == 2:
            self.position.partial_2_done = True
        self._post_partial_exit(result, pending.get("stage") or 1)
        # COM 콜백 복귀 후 잔고 갱신 (dynamicCall 재진입 방지)
        QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))
        return

    if pending["kind"] == "EXIT_MANUAL_PARTIAL":
        _ts_record_nonfinal_exit(self, result, pending["reason"])
        self.dashboard.minute_chart_record_exit(
            fill_price,
            filled_at,
            finalize=False,
            pnl_pts=result.get("pnl_pts"),
            reason=pending["reason"],
            direction=result.get("direction", ""),
        )
        _ts_log_diag(
            self,
            "ExitFillFlow",
            before=before,
            after=_ts_get_position_snapshot(self),
            pending=_ts_get_pending_snapshot(self),
            fill_qty=fill_qty,
            fill_price=fill_price,
            mode="manual_partial",
            reason=pending["reason"],
        )
        _ts_system_info_throttled(self, "balance_refresh_trigger_exit_manual_partial", "[BalanceRefresh] trigger=ExitFillFlow mode=manual_partial", min_interval_sec=30.0)
        QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))
        return

    if "remaining" in result:
        _ts_record_nonfinal_exit(self, result, pending["reason"])
        self.dashboard.minute_chart_record_exit(
            fill_price,
            filled_at,
            finalize=False,
            pnl_pts=result.get("pnl_pts"),
            reason=pending["reason"],
            direction=result.get("direction", ""),
        )
        _ts_log_diag(
            self,
            "ExitFillFlow",
            before=before,
            after=_ts_get_position_snapshot(self),
            pending=_ts_get_pending_snapshot(self),
            fill_qty=fill_qty,
            fill_price=fill_price,
            mode="partial_or_remaining",
            reason=pending["reason"],
        )
        _ts_system_info_throttled(self, "balance_refresh_trigger_exit_partial", "[BalanceRefresh] trigger=ExitFillFlow mode=partial_or_remaining", min_interval_sec=30.0)
        QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))
        return

    _ts_apply_exit_cooldown(self, result, filled_at)
    self._exit_cooldown_applied_this_fill = True
    self._post_exit(result)
    _ts_log_diag(
        self,
        "ExitFillFlow",
        before=before,
        after=_ts_get_position_snapshot(self),
        pending=_ts_get_pending_snapshot(self),
        fill_qty=fill_qty,
        fill_price=fill_price,
        mode="final",
        reason=pending["reason"],
    )
    if self.position.status == "FLAT":
        self.dashboard.minute_chart_clear_active_position()
        _ts_force_balance_flat_ui(self, f"final_exit:{pending['reason']}")
    _ts_system_info_throttled(self, "balance_refresh_trigger_exit_final", "[BalanceRefresh] trigger=ExitFillFlow mode=final retries=250ms,1200ms", min_interval_sec=30.0)
    QTimer.singleShot(250, lambda: _ts_refresh_dashboard_balance(self))
    QTimer.singleShot(1200, lambda: _ts_refresh_dashboard_balance(self))


def _ts_handle_external_fill(
    self,
    payload: dict,
    side: str,
    fill_qty: int,
    fill_price: float,
    filled_at: datetime.datetime,
) -> None:
    if fill_qty <= 0 or side not in ("LONG", "SHORT"):
        return

    before = _ts_get_position_snapshot(self)
    reason_label = "외부체결(HTS/수동)"
    atr = _ts_get_reference_atr(self)

    log_manager.system(
        f"[OrderSync] 외부 체결 감지 order_no={payload.get('order_no') or '?'} "
        f"side={side} qty={fill_qty} price={fill_price} before={before}",
        "WARNING",
    )

    remaining_fill = fill_qty
    if self.position.status != "FLAT" and self.position.status != side:
        exit_qty = min(remaining_fill, self.position.quantity)
        result = self.position.apply_exit_fill(
            exit_price=fill_price,
            quantity=exit_qty,
            reason=reason_label,
            filled_at=filled_at,
        )
        remaining_fill -= exit_qty
        if "remaining" in result:
            _ts_record_nonfinal_exit(self, result, reason_label)
            self.dashboard.minute_chart_record_exit(
                fill_price,
                filled_at,
                finalize=False,
                pnl_pts=result.get("pnl_pts"),
                reason=reason_label,
                direction=result.get("direction", ""),
            )
        else:
            _ts_apply_exit_cooldown(self, result, filled_at)
            self._exit_cooldown_applied_this_fill = True
            self._post_exit(result)

    if remaining_fill > 0:
        result = self.position.apply_entry_fill(
            direction=side,
            price=fill_price,
            quantity=remaining_fill,
            atr=atr,
            grade="MANUAL",
            regime=self.current_regime,
            filled_at=filled_at,
        )
        self.dashboard.minute_chart_sync_active_position(
            side,
            self.position.entry_price,
            self.position.entry_time,
        )
        log_manager.trade(
            f"[체결동기화] 외부진입 {side} {remaining_fill}계약 @ {fill_price} "
            f"| 평균={result['avg_entry_price']} 보유={result['position_qty']}계약"
        )
        self.dashboard.append_pnl_log(
            f"외부진입 동기화 | {side} {remaining_fill}계약 @ {fill_price}",
            f"평균 {self.position.entry_price:.2f} 손절 {self.position.stop_price:.2f}",
        )
        self.dashboard.set_ui_position_mode()

    after = _ts_get_position_snapshot(self)
    log_manager.system(
        f"[OrderSync] 외부 체결 반영 완료 order_no={payload.get('order_no') or '?'} after={after}",
        "WARNING",
    )


def _ts_on_chejan_event(self, payload: dict) -> None:
    _gubun = str(payload.get("gubun", "")).strip()
    if _gubun not in ("0", "1"):
        return
    event_key = (
        payload.get("gubun"),
        payload.get("order_no"),
        payload.get("fill_no"),
        payload.get("order_status"),
        payload.get("filled_qty"),
        payload.get("fill_price"),
        payload.get("unfilled_qty"),
    )
    if event_key == self._last_order_event_key:
        return
    self._last_order_event_key = event_key

    order_no = payload.get("order_no", "")
    status = payload.get("order_status", "")
    code = payload.get("code", "")
    account_no = str(payload.get("account_no", "")).strip()
    fill_qty = int(payload.get("filled_qty") or 0)
    fill_price = float(payload.get("fill_price") or 0.0) or float(payload.get("current_price") or 0.0)
    unfilled_qty = int(payload.get("unfilled_qty") or 0)
    side = _ts_order_side_to_direction(payload)
    _ts_log_diag(
        self,
        "ChejanFlow",
        gubun=payload.get("gubun", ""),
        account=account_no,
        order_no=order_no,
        status=status,
        code=code,
        side=side,
        fill_qty=fill_qty,
        fill_price=fill_price,
        unfilled_qty=unfilled_qty,
        pending=_ts_get_pending_snapshot(self),
        position=_ts_get_position_snapshot(self),
    )

    if _secrets.ACCOUNT_NO and account_no and account_no != _secrets.ACCOUNT_NO:
        _ts_log_diag(
            self,
            "ChejanAccountIgnored",
            expected=_secrets.ACCOUNT_NO,
            actual=account_no,
            order_no=order_no,
        )
        return

    if str(payload.get("gubun", "")).strip() == "1":
        _ts_sync_from_balance_payload(self, payload)
        return

    log_manager.trade(
        f"[Chejan] 상태={status or '?'} 주문번호={order_no or '?'} "
        f"code={code or '?'} 방향={side or '?'} 체결={fill_qty} 미체결={unfilled_qty}"
    )

    pending = self._pending_order
    pending_matched = False
    if pending:
        if pending.get("order_no") and order_no and pending["order_no"] == order_no:
            pending_matched = True
        elif not pending.get("order_no"):
            pending["order_no"] = order_no or pending.get("order_no", "")
            pending_matched = True
    _ts_log_diag(
        self,
        "ChejanMatch",
        pending_matched=pending_matched,
        order_no=order_no,
        pending=_ts_get_pending_snapshot(self),
    )

    if fill_qty <= 0:
        if pending_matched and status in ("접수", "확인"):
            if not pending.get("accepted_at"):
                pending["accepted_at"] = datetime.datetime.now()  # [B55] 접수 시각 기록
            log_manager.system(
                f"[Order] {status} kind={pending['kind']} qty={pending['qty']} order_no={order_no or '?'}"
            )
        return

    filled_at = _ts_parse_chejan_time(payload.get("order_time", ""))
    if not pending_matched:
        _ts_handle_external_fill(self, payload, side, fill_qty, fill_price, filled_at)
        return

    pending["filled_qty"] += fill_qty
    if pending["kind"] == "ENTRY":
        _ts_handle_entry_fill(
            self,
            pending,
            payload,
            fill_qty,
            fill_price or pending["price_hint"],
            filled_at,
        )
    else:
        _ts_handle_exit_fill(
            self,
            pending,
            payload,
            fill_qty,
            fill_price or pending["price_hint"],
            filled_at,
        )

    if pending["filled_qty"] >= pending["qty"] or unfilled_qty == 0:
        self._clear_pending_order()


def _ts_set_broker_sync_status(self, verified: bool, reason: str, block_new_entries: bool) -> None:
    self._broker_sync_verified = verified
    self._broker_sync_block_new_entries = block_new_entries
    self._broker_sync_last_error = str(reason or "").strip()
    logger.info(
        "[BrokerSync] status verified=%s block_new_entries=%s reason=%s",
        verified, block_new_entries, self._broker_sync_last_error,
    )


def _ts_safe_float_text(value) -> float:
    try:
        text = str(value or "").replace(",", "").strip()
        if not text:
            return 0.0
        return float(text)
    except Exception:
        return 0.0


def _ts_extract_sizer_balance(summary: dict) -> float:
    if not isinstance(summary, dict):
        return 0.0

    for key in ("총매매", "총평가수익률", "추정자산"):
        value = _ts_safe_float_text(summary.get(key))
        if value > 0:
            return value
    return 0.0


def _ts_current_sizer_balance(self) -> float:
    summary = dict((getattr(self, "_last_balance_result", None) or {}).get("summary") or {})
    balance = _ts_extract_sizer_balance(summary)
    if balance > 0:
        return balance

    cached = float(getattr(self, "_last_sizer_balance", 0.0) or 0.0)
    if cached > 0:
        return cached

    return float(getattr(self.sizer, "account_balance", 0.0) or 0.0)


def _ts_force_balance_flat_ui(self, reason: str) -> None:
    cached = copy.deepcopy(getattr(self, "_last_balance_result", None) or {})
    forced = {
        **cached,
        "rows": [],
        "nonempty_rows": [],
        "all_blank_rows": False,
        "summary": dict(cached.get("summary") or {}),
        "summary_probe": dict(cached.get("summary_probe") or {}),
    }
    _ts_system_info_throttled(
        self,
        "balance_ui_force_flat",
        f"[BalanceUI] force flat rows reason={reason} "
        f"cached_summary_nonblank={any(str(v).strip() for v in forced['summary'].values())}",
        min_interval_sec=60.0,
    )
    _ts_push_balance_to_dashboard(self, forced)


def _ts_push_balance_to_dashboard(self, result: dict, *, quiet: bool = False) -> None:
    if not result:
        _ts_system_info_throttled(self, "balance_ui_skipped_empty", "[BalanceUI] skipped: empty result", min_interval_sec=120.0)
        return

    self._last_balance_result = copy.deepcopy(result)

    rows = list(result.get("nonempty_rows") or result.get("rows") or [])
    summary = dict(result.get("summary") or {})
    probe = dict(result.get("summary_probe") or {})
    if not quiet:
        _ts_system_info_throttled(
            self,
            "balance_ui_raw",
            f"[BalanceUI] raw rows={len(result.get('rows') or [])} nonempty={len(result.get('nonempty_rows') or [])} "
            f"summary_nonblank={any(str(v).strip() for v in summary.values())} "
            f"record={result.get('record_name', '')} query_count={result.get('query_count', '')}",
            min_interval_sec=120.0,
        )

    # TR blank + 포지션 보유 중 → position_tracker 기반 합성 행 (모의투자 OPW20006 공란 대응)
    # nonempty_rows=[] 이지만 rows=[{blank}] 케이스도 포함
    _has_real_row = any(any(str(v).strip() for v in r.values()) for r in rows)
    if not _has_real_row and self.position.status != "FLAT":
        _side_label = "매수" if self.position.status == "LONG" else "매도"
        _entry = self.position.entry_price
        _qty = self.position.quantity
        # 미실현 PnL: 마지막 알려진 close 가격이 있으면 계산, 없으면 entry 기준 0
        _last_price = getattr(self, "_last_pipeline_price", _entry) or _entry
        _pnl_pts = self.position.unrealized_pnl_pts(_last_price)
        # KOSPI200 선물 계약 승수: 250,000원/pt (2017년 기준, HTS 일치)
        _pnl_krw = _pnl_pts * 250_000
        _eval_krw = _entry * _qty * 250_000  # 매입금액 = entry_pt × 계약수 × 250,000
        rows = [{
            "종목코드": getattr(self, "_futures_code", ""),
            "종목명": "KOSPI200선물",
            "매매일자": datetime.datetime.now().strftime("%Y%m%d"),
            "매매구분": _side_label,
            "잔고수량": str(_qty),
            "청산가능": str(_qty),
            "주문가능수량": str(_qty),
            "매입단가": f"{_entry:.2f}",
            "매매금액": f"{_eval_krw:.0f}",
            "현재가": f"{_last_price:.2f}",
            "평가손익": f"{_pnl_krw:.0f}",
            "손익율": f"{(_pnl_krw / _eval_krw * 100.0):.2f}" if _eval_krw else "0.00",
            "평가금액": f"{_eval_krw + _pnl_krw:.0f}",
        }]
        if not quiet:
            logger.warning(
                "[BalanceUIFallback-Position] TR blank + 포지션 보유 → 합성 행 생성 side=%s qty=%s entry=%s cur=%s pnl_krw=%s",
                _side_label, _qty, _entry, _last_price, _pnl_krw,
            )

    def _parse_qty(row):
        for key in ("잔고수량", "주문가능수량", "?붽퀬?섎웾", "二쇰Ц媛?μ닔??"):
            try:
                return int(str(row.get(key, "")).replace(",", "").strip() or "0")
            except (ValueError, AttributeError):
                continue
        return 0

    def _parse_price(row, *keys):
        for key in keys:
            try:
                text = str(row.get(key, "")).replace(",", "").strip()
                if text:
                    return float(text)
            except (ValueError, AttributeError):
                continue
        return 0.0

    def _format_krw(value):
        return f"{float(value):.0f}"

    if rows:
        _last_price_hint = float(getattr(self, "_last_pipeline_price", 0.0) or 0.0)
        for row in rows:
            _qty = _parse_qty(row)
            _avg_price = _parse_price(row, "평균가", "매입단가")
            _current_price = _parse_price(row, "현재가")
            if _current_price <= 0 and _last_price_hint > 0:
                _current_price = _last_price_hint
                row["현재가"] = f"{_current_price:.2f}"

            if _qty > 0 and _avg_price > 0 and _current_price > 0:
                _side_text = str(row.get("매매구분") or row.get("구분") or "").replace(" ", "").strip()
                _mult = -1 if "매도" in _side_text else 1
                _trade_base_krw = _avg_price * _qty * self._pt_value
                _pnl_pts = (_current_price - _avg_price) * _mult
                _pnl_krw = _pnl_pts * self._pt_value * _qty
                _eval_amount_krw = _trade_base_krw + _pnl_krw
                _rate = (_pnl_krw / _trade_base_krw * 100.0) if _trade_base_krw else 0.0

                if not str(row.get("평가손익(원)") or row.get("평가손익") or "").strip():
                    row["평가손익(원)"] = _format_krw(_pnl_krw)
                    row["평가손익"] = _format_krw(_pnl_krw)
                if not str(row.get("수익률(%)") or row.get("손익율") or "").strip():
                    row["수익률(%)"] = f"{_rate:.2f}"
                    row["손익율"] = f"{_rate:.2f}"
                if not str(row.get("평가금액") or "").strip():
                    row["평가금액"] = _format_krw(_eval_amount_krw)
                if not str(row.get("매매금액") or "").strip():
                    row["매매금액"] = _format_krw(_trade_base_krw)

    balance_active = (
        self.position.status != "FLAT"
        or any(_parse_qty(row) > 0 for row in rows)
    )

    def _num(value):
        try:
            return float(str(value or "").replace(",", "").replace("%", "").strip() or "0")
        except ValueError:
            return 0.0

    eval_sum = 0.0
    pnl_sum = 0.0
    trade_sum = 0.0
    for row in rows:
        eval_sum += _num(row.get("평가금액", "0"))
        pnl_sum += _num(row.get("평가손익", "0"))
        trade_sum += _num(row.get("매매금액", "0"))

    today_str = datetime.date.today().isoformat()
    realized_krw = None
    is_cybos_balance = str(getattr(getattr(self, "broker", None), "name", "") or "").strip().lower() == "cybos"
    if is_cybos_balance:
        if not str(summary.get("총매매") or "").strip():
            summary["총매매"] = "0"
        if not str(summary.get("총평가손익") or "").strip():
            summary["총평가손익"] = f"{eval_sum:.0f}"
        if not str(summary.get("총평가") or "").strip():
            summary["총평가"] = "0.00"
    else:
        # pnl_sum=0 케이스도 덮어써야 하므로 (or not rows) 가드 제거
        if not str(summary.get("총매매") or "").strip():
            summary["총매매"] = f"{trade_sum:.0f}"
        if not str(summary.get("총평가손익") or "").strip():
            summary["총평가손익"] = f"{pnl_sum:.0f}"
        if not str(summary.get("총평가") or "").strip():
            summary["총평가"] = f"{eval_sum:.0f}"

    broker_realized_text = str(summary.get("실현손익") or "").strip()
    if broker_realized_text:
        try:
            self._last_balance_realized_krw = float(_num(broker_realized_text))
            self._last_balance_realized_date = today_str
        except Exception:
            pass
    if not is_cybos_balance:
        try:
            today_rows = fetch_today_trades(today_str)
            if today_rows:
                realized_krw = float(sum(float(r["pnl_krw"] or 0.0) for r in today_rows))
        except Exception:
            realized_krw = None
    if not str(summary.get("실현손익") or "").strip():
        cached_realized_krw = None
        if getattr(self, "_last_balance_realized_date", "") == today_str:
            cached_realized_krw = getattr(self, "_last_balance_realized_krw", None)
        if cached_realized_krw is not None:
            summary["실현손익"] = f"{cached_realized_krw:.0f}"
        else:
            if is_cybos_balance:
                realized_krw = 0.0
            elif realized_krw is None:
                try:
                    realized_krw = float(self.position.daily_stats().get("pnl_krw", 0.0) or 0.0)
                except Exception:
                    realized_krw = 0.0
            summary["실현손익"] = f"{realized_krw:.0f}"

    if is_cybos_balance:
        if not str(summary.get("총평가수익률") or "").strip():
            summary["총평가수익률"] = "0"
        if not str(summary.get("추정자산") or "").strip():
            summary["추정자산"] = "0"
    else:
        trade_base = trade_sum or _num(summary.get("총매매"))
        pnl_base = _num(summary.get("총평가손익"))
        if not str(summary.get("총평가수익률") or "").strip():
            rate = (pnl_base / trade_base * 100.0) if trade_base else 0.0
            summary["총평가수익률"] = f"{rate:.2f}"

        if not str(summary.get("추정자산") or "").strip():
            summary["추정자산"] = f"{_num(summary.get('총평가')):.0f}"

    sizer_balance = _ts_extract_sizer_balance(summary)
    if sizer_balance > 0:
        self._last_sizer_balance = sizer_balance
        self.sizer.set_account_balance(sizer_balance)

    realized_krw_log = float(realized_krw) if realized_krw is not None else 0.0

    if not quiet:
        _ts_system_info_throttled(
            self,
            "balance_ui_computed",
            f"[BalanceUI] computed trade_sum={trade_sum:.4f} pnl_sum={pnl_sum:.4f} eval_sum={eval_sum:.4f} "
            f"realized_krw={realized_krw_log:.4f} final_summary_nonblank={any(str(v).strip() for v in summary.values())} "
            f"probe_nonblank={any(str(v).strip() for v in probe.values())}",
            min_interval_sec=120.0,
        )

    if not quiet and not any(str(v).strip() for v in result.get("summary", {}).values()):
        logger.warning(
            "[BalanceUIFallback] summary blank from broker balance TR; rows=%d probe=%s applied=%s",
            len(rows),
            probe,
            summary,
        )

    if not quiet:
        _ts_logger_info_throttled(
            self,
            "balance_ui_push",
            "[BalanceUI] push rows=%d preview=%s summary=%s",
            len(rows),
            rows[:3],
            summary,
            min_interval_sec=120.0,
        )
    self.dashboard.update_account_balance(
        summary,
        rows,
        quiet=quiet,
        mark_fresh=(not quiet),
        source="broker",
        balance_active=balance_active,
    )


def _ts_refresh_dashboard_balance(self) -> None:
    account_no = str(_secrets.ACCOUNT_NO or "").strip()
    if not account_no:
        log_manager.system("[BalanceRefresh] skipped: empty account number", "WARNING")
        return
    _ts_system_info_throttled(
        self,
        "balance_refresh_request_start",
        f"[BalanceRefresh] request start account={account_no} position={_ts_get_position_snapshot(self)}",
        min_interval_sec=60.0,
    )
    result = self.broker.request_futures_balance(account_no)
    if result is None:
        log_manager.system("[BalanceRefresh] request returned None", "WARNING")
        return
    _ts_system_info_throttled(
        self,
        "balance_refresh_request_ok",
        f"[BalanceRefresh] request ok rows={len(result.get('rows') or [])} "
        f"nonempty={len(result.get('nonempty_rows') or [])} "
        f"summary_nonblank={any(str(v).strip() for v in (result.get('summary') or {}).values())} "
        f"probe_nonblank={any(str(v).strip() for v in (result.get('summary_probe') or {}).values())}",
        min_interval_sec=60.0,
    )
    _ts_logger_info_throttled(
        self,
        "balance_refresh_result",
        "[BalanceRefresh] balance result rows=%d nonempty=%d summary_nonblank=%s probe_nonblank=%s summary=%s",
        len(result.get("rows") or []),
        len(result.get("nonempty_rows") or []),
        any(str(v).strip() for v in (result.get("summary") or {}).values()),
        any(str(v).strip() for v in (result.get("summary_probe") or {}).values()),
        result.get("summary") or {},
        min_interval_sec=60.0,
    )
    _ts_push_balance_to_dashboard(self, result)


def _ts_refresh_dashboard_balance_ui_only(self) -> None:
    if not getattr(self, "dashboard", None):
        return
    cached = getattr(self, "_last_balance_result", None) or {}
    if not cached:
        cached = {
            "rows": [],
            "nonempty_rows": [],
            "summary": {},
            "summary_probe": {},
        }
    _ts_push_balance_to_dashboard(self, cached, quiet=True)


def _ts_sync_position_from_broker(self) -> None:
    account_no = str(_secrets.ACCOUNT_NO or "").strip()
    code = self._normalize_broker_code(getattr(self, "_futures_code", ""))
    if not account_no or not code:
        _ts_set_broker_sync_status(self, False, "missing account/code for startup sync", True)
        return

    before = _ts_get_position_snapshot(self)
    logger.info(
        "[BrokerSync] startup sync begin account=%s code=%s before=%s",
        account_no, code, before,
    )
    result = self.broker.request_futures_balance(account_no)
    if result is None:
        _ts_set_broker_sync_status(self, False, "broker balance TR returned None", True)
        log_manager.system("[BrokerSync] 브로커 잔고 TR 조회 실패로 startup sync를 건너뜁니다.", "WARNING")
        return
    logger.warning(
        "[BrokerSync] balance result rows=%d nonempty=%d summary_nonblank=%s probe_nonblank=%s summary=%s",
        len(result.get("rows") or []),
        len(result.get("nonempty_rows") or []),
        any(str(v).strip() for v in (result.get("summary") or {}).values()),
        any(str(v).strip() for v in (result.get("summary_probe") or {}).values()),
        result.get("summary") or {},
    )
    _ts_push_balance_to_dashboard(self, result)

    rows = result.get("rows") or []
    nonempty_rows = result.get("nonempty_rows") or []
    all_blank_rows = bool(result.get("all_blank_rows"))
    logger.warning(
        "[BrokerSync] startup sync raw rows=%d nonempty_rows=%d all_blank_rows=%s record_name=%r prev_next=%r rows=%s",
        len(rows),
        len(nonempty_rows),
        all_blank_rows,
        result.get("record_name", ""),
        result.get("prev_next", ""),
        rows,
    )

    broker_row = None
    candidate_rows = nonempty_rows or rows
    for row in candidate_rows:
        row_code = self._normalize_broker_code(row.get("종목코드") or row.get("code") or "")
        logger.warning("[BrokerSync] row candidate normalized_code=%s row=%s", row_code, row)
        if row_code == code:
            broker_row = row
            break

    if not broker_row:
        if not nonempty_rows:
            logger.warning(
                "[BrokerSync] blank-as-flat decision before=%s rows=%s summary=%s probe=%s",
                before,
                rows,
                result.get("summary") or {},
                result.get("summary_probe") or {},
            )
            # Cybos 모의투자 서버는 잔고 TR summary/rows가 blank일 수 있으므로 저장 포지션이 있으면 유지
            try:
                _server_gubun = self.broker.get_login_info("GetServerGubun")
            except Exception:
                _server_gubun = ""
            _is_mock = (_server_gubun == "1")
            if _is_mock and self.position.status != "FLAT":
                log_manager.system(
                    f"[BrokerSync] 모의투자 blank-rows → 저장 포지션 유지 ({before}). "
                    f"브로커 잔고 TR 공란은 모의서버 정상 응답 — FLAT 강제 불가.",
                    "WARNING",
                )
                _ts_set_broker_sync_status(self, True, "mock server blank rows — keeping saved position", False)
                _ts_push_balance_to_dashboard(self, result)
                return
            if self.position.status != "FLAT":
                self.position.sync_flat_from_broker()
                self.dashboard.minute_chart_clear_active_position()
            self._clear_pending_order()
            _ts_set_broker_sync_status(self, True, "blank/no holdings response interpreted as flat", False)
            log_manager.system(
                f"[BrokerSync] startup sync 무포지션 확인(blank rows): {before} -> FLAT",
                "WARNING" if before != "FLAT" else "INFO",
            )
            _ts_log_diag(
                self,
                "BrokerSyncFlatPlaceholder",
                before=before,
                rows=len(rows),
                all_blank_rows=all_blank_rows,
                raw_rows=rows,
            )
            return
        _ts_set_broker_sync_status(self, False, "no broker row matched requested code", True)
        logger.warning(
            "[BrokerSync] no matching broker row target_code=%s candidate_rows=%s summary=%s probe=%s",
            code,
            candidate_rows,
            result.get("summary") or {},
            result.get("summary_probe") or {},
        )
        log_manager.system(
            f"[BrokerSync] startup sync 실패: code={code} 매칭 잔고행 없음. 자동진입 차단 유지 | before={before}",
            "CRITICAL",
        )
        return

    qty_text = broker_row.get("잔고수량") or "0"  # enc 확인: 잔고수량 존재 (보유수량 x)
    price_text = (
        broker_row.get("매입단가")
        or broker_row.get("평균단가")
        or broker_row.get("현재가")
        or "0"
    )
    side_text = broker_row.get("매매구분", "")

    try:
        qty = int(str(qty_text).replace(",", "").strip() or "0")
    except ValueError:
        qty = 0
    try:
        avg_price = float(str(price_text).replace(",", "").strip() or "0")
    except ValueError:
        avg_price = 0.0

    side = _ts_order_side_to_direction(side_text)
    logger.warning(
        "[BrokerSync] parsed candidate code=%s qty_text=%r price_text=%r side_text=%r => qty=%s price=%s side=%s",
        code, qty_text, price_text, side_text, qty, avg_price, side,
    )
    if qty <= 0 or side not in ("LONG", "SHORT"):
        logger.warning(
            "[BrokerSync] parse failure broker_row=%s summary=%s probe=%s",
            broker_row,
            result.get("summary") or {},
            result.get("summary_probe") or {},
        )
        _ts_set_broker_sync_status(
            self,
            False,
            f"parse failure qty={qty_text} side={side_text} price={price_text}",
            True,
        )
        log_manager.system(
            f"[BrokerSync] startup sync 응답 해석 실패 code={code} qty={qty_text} side={side_text}",
            "WARNING",
        )
        return

    self.position.sync_from_broker(
        direction=side,
        price=avg_price,
        quantity=qty,
        atr=max(_ts_get_reference_atr(self), 0.5),
        grade="BROKER",
        regime=self.current_regime or "BROKER_SYNC",
    )
    self.dashboard.minute_chart_sync_active_position(
        side,
        avg_price,
        self.position.entry_time,
    )
    self._clear_pending_order()
    _ts_set_broker_sync_status(self, True, f"synced {side} {qty} @ {avg_price}", False)
    after = _ts_get_position_snapshot(self)
    log_manager.system(
        f"[BrokerSync] startup sync 완료: {before} -> {after}",
        "CRITICAL" if before != after else "INFO",
    )


def _ts_sync_from_balance_payload(self, payload: dict) -> None:
    code = self._normalize_broker_code(payload.get("code", ""))
    target_code = self._normalize_broker_code(getattr(self, "_futures_code", ""))
    if not code or not target_code or code != target_code:
        logger.info(
            "[BrokerSync] balance chejan ignored code=%s target_code=%s payload=%s",
            code, target_code, payload,
        )
        return

    qty = int(payload.get("holding_qty") or 0)
    avg_price = float(payload.get("avg_price") or 0.0)
    side = _ts_order_side_to_direction(payload.get("balance_side", ""))
    before = _ts_get_position_snapshot(self)
    logger.warning(
        "[BrokerSync] balance chejan payload before=%s qty=%s avg=%s side=%s raw=%s",
        before, qty, avg_price, side, payload,
    )
    _ts_log_diag(
        self,
        "BalanceChejanFlow",
        before=before,
        code=code,
        target_code=target_code,
        qty=qty,
        avg_price=avg_price,
        side=side,
        pending=_ts_get_pending_snapshot(self),
    )

    if qty <= 0:
        self.position.sync_flat_from_broker()
        self.dashboard.minute_chart_clear_active_position()
        self._clear_pending_order()   # [B56] 내부에서 ENTRY 미체결이면 cooldown 자동 설정
        _ts_set_broker_sync_status(self, True, "balance chejan confirmed flat", False)
        log_manager.system(
            f"[BrokerSync] 잔고 Chejan 반영: {before} -> FLAT",
            "CRITICAL",
        )
        QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))
        return

    if side not in ("LONG", "SHORT") or avg_price <= 0:
        _ts_set_broker_sync_status(
            self,
            False,
            f"balance chejan parse failure side={payload.get('balance_side')} qty={qty} avg={avg_price}",
            True,
        )
        log_manager.system(
            f"[BrokerSync] 잔고 Chejan 해석 실패 code={code} side={payload.get('balance_side')} qty={qty} avg={avg_price}",
            "WARNING",
        )
        return

    self.position.sync_from_broker(
        direction=side,
        price=avg_price,
        quantity=qty,
        atr=max(_ts_get_reference_atr(self), 0.5),
        grade="BROKER",
        regime=self.current_regime or "BROKER_SYNC",
    )
    self.dashboard.minute_chart_sync_active_position(
        side,
        avg_price,
        self.position.entry_time,
    )
    self._clear_pending_order()
    _ts_set_broker_sync_status(self, True, f"balance chejan synced {side} {qty} @ {avg_price}", False)
    after = _ts_get_position_snapshot(self)
    log_manager.system(
        f"[BrokerSync] 잔고 Chejan 반영: {before} -> {after}",
        "CRITICAL" if before != after else "INFO",
    )
    QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))


def _ts_execute_entry(
    self,
    direction: str,
    price: float,
    quantity: int,
    atr: float,
    grade: str,
    raw_direction: str = None,
    reverse_enabled: bool = False,
):
    cooldown_active, cooldown_remain = _ts_in_exit_cooldown(self)
    raw_direction = raw_direction or direction
    _ts_log_diag(
        self,
        "EntryAttempt",
        raw_direction=raw_direction,
        direction=direction,
        price=price,
        quantity=quantity,
        atr=atr,
        grade=grade,
        reverse_entry_enabled=reverse_enabled,
        broker_sync_verified=self._broker_sync_verified,
        block_new_entries=self._broker_sync_block_new_entries,
        broker_sync_reason=self._broker_sync_last_error,
        exit_cooldown_active=cooldown_active,
        exit_cooldown_remain=cooldown_remain,
        pending=_ts_get_pending_snapshot(self),
        position=_ts_get_position_snapshot(self),
    )
    if self._broker_sync_block_new_entries:
        log_manager.system(
            f"[EntryBlock] broker sync 미검증으로 진입 차단 raw={raw_direction} final={direction} "
            f"qty={quantity} reverse_entry={'ON' if reverse_enabled else 'OFF'} "
            f"reason={self._broker_sync_last_error}",
            "CRITICAL",
        )
        logger.warning(
            "[EntryBlock] broker sync gate raw=%s final=%s qty=%s reverse=%s reason=%s",
            raw_direction, direction, quantity, reverse_enabled, self._broker_sync_last_error,
        )
        return
    if cooldown_active:
        msg = (
            f"[EntryBlock] 청산 후 쿨다운 active -> 진입 차단 raw={raw_direction} final={direction} "
            f"qty={quantity} remain={cooldown_remain}s last_exit={getattr(self, '_last_exit_reason', '')}"
        )
        logger.warning(msg)
        log_manager.system(msg, "WARNING")
        return
    if self._has_pending_order():
        logger.info("[Entry] pending order exists -> skip new entry %s %s", direction, quantity)
        return
    ret = self._send_kiwoom_entry_order(direction, quantity)
    logger.info(
        "[Entry] send_order result ret=%s raw=%s final=%s qty=%s reverse=%s code=%s broker_sync_verified=%s",
        ret, raw_direction, direction, quantity, reverse_enabled,
        getattr(self, "_futures_code", ""), self._broker_sync_verified,
    )
    log_manager.system(
        f"[EntrySendResult] ret={ret} raw={raw_direction} final={direction} qty={quantity} "
        f"reverse_entry={'ON' if reverse_enabled else 'OFF'} code={getattr(self, '_futures_code', '')}",
        "WARNING" if ret != 0 else "INFO",
    )
    _ts_log_diag(
        self,
        "EntrySendOrderResult",
        ret=ret,
        raw_direction=raw_direction,
        direction=direction,
        quantity=quantity,
        reverse_entry_enabled=reverse_enabled,
        code=getattr(self, "_futures_code", ""),
        pending=_ts_get_pending_snapshot(self),
        position=_ts_get_position_snapshot(self),
    )
    if ret != 0:
        logger.error("[Entry] SendOrder 실패로 내부 포지션 오픈을 취소합니다. ret=%s", ret)
        log_manager.system(
            f"[Entry] 주문 실패로 포지션 미오픈 ret={ret} raw={raw_direction} final={direction} "
            f"qty={quantity} reverse_entry={'ON' if reverse_enabled else 'OFF'}",
            "ERROR",
        )
        return
    self._set_pending_order(
        kind="ENTRY",
        direction=direction,
        qty=quantity,
        price_hint=price,
        reason="진입",
        atr=atr,
        grade=grade,
        raw_direction=raw_direction,
        reverse_entry_enabled=reverse_enabled,
    )
    # Fix B: 모의투자에서 Chejan 없음 → 낙관적 오픈으로 이중진입 방지
    # Chejan 체결 시 apply_entry_fill() 가격 보정 경로로 합쳐짐 (_optimistic=True)
    try:
        self.position.open_position(
            direction,
            price,
            quantity,
            atr,
            grade,
            self.current_regime,
            raw_direction=raw_direction,
            reverse_entry_enabled=reverse_enabled,
        )
        self.position._optimistic = True
        self.dashboard.minute_chart_record_entry(
            direction,
            price,
            self.position.entry_time,
        )
        logger.warning(
            "[FixB] 낙관적 오픈 완료 direction=%s status=%s qty=%s optimistic=%s",
            direction, self.position.status, self.position.quantity, self.position._optimistic,
        )
    except Exception as _fixb_err:
        logger.error(
            "[FixB] open_position 실패 direction=%s status_before=%s err=%s",
            direction, self.position.status, _fixb_err,
        )
    _ts_log_diag(
        self,
        "EntryPendingCreated",
        raw_direction=raw_direction,
        direction=direction,
        reverse_entry_enabled=reverse_enabled,
        pending=_ts_get_pending_snapshot(self),
        position=_ts_get_position_snapshot(self),
    )
    log_manager.signal(
        f"[EntrySignal] 원신호={raw_direction} 실행신호={direction} "
        f"역방향진입={'ON' if reverse_enabled else 'OFF'} 등급={grade}"
    )
    log_manager.trade(
        f"[주문요청] {raw_direction}->{direction} {quantity}계약 @ {price} "
        f"등급={grade} 역방향진입={'ON' if reverse_enabled else 'OFF'} 체결대기"
    )


def _ts_manual_position_restore(self, direction: str, price: float, qty: int, atr: float) -> None:
    """대시보드 '포지션 복원' 버튼 핸들러 — 모의투자 TR blank 대응."""
    from PyQt5.QtCore import QTimer as _QTimer
    atr = max(float(atr or 0.0), 0.5)
    log_manager.system(
        f"[PositionRestore] 수동 복원 요청: {direction} {qty}계약 @ {price:.2f}pt ATR={atr:.2f}",
        "WARNING",
    )
    try:
        result = self.position.sync_from_broker(
            direction=direction,
            price=price,
            quantity=qty,
            atr=atr,
            grade="MANUAL",
            regime="MANUAL_RESTORE",
        )
        self.dashboard.minute_chart_sync_active_position(
            direction,
            price,
            self.position.entry_time,
        )
        self._broker_sync_verified = True
        self._broker_sync_block_new_entries = False
        log_manager.system(
            f"[PositionRestore] 완료: {result}  손절={self.position.stop_price:.2f}  "
            f"TP1={self.position.tp1_price:.2f}  TP2={self.position.tp2_price:.2f}",
            "WARNING",
        )
        self.dashboard.set_ui_position_mode()
    except Exception as _e:
        log_manager.system(f"[PositionRestore] sync_from_broker 실패: {_e}", "CRITICAL")
        return
    _QTimer.singleShot(300, lambda: _ts_refresh_dashboard_balance(self))


def _ts_handle_entry_fill_cybos_safe(
    self,
    pending: dict,
    payload: dict,
    fill_qty: int,
    fill_price: float,
    filled_at: datetime.datetime,
) -> None:
    actual_side = _ts_order_side_to_direction(payload)
    entry_direction = actual_side or pending["direction"]
    before = _ts_get_position_snapshot(self)
    if actual_side and actual_side != pending["direction"]:
        log_manager.system(
            f"[OrderSync] side mismatch pending={pending['direction']} actual={actual_side} "
            f"order_no={payload.get('order_no') or '?'}",
            "CRITICAL",
        )

    result = self.position.apply_entry_fill(
        direction=entry_direction,
        price=fill_price,
        quantity=fill_qty,
        atr=_ts_get_reference_atr(self, pending),
        grade=pending["grade"],
        regime=self.current_regime,
        filled_at=filled_at,
        raw_direction=pending.get("raw_direction") or pending["direction"],
        reverse_entry_enabled=bool(pending.get("reverse_entry_enabled", False)),
    )
    if before == "FLAT":
        self.dashboard.minute_chart_record_entry(
            entry_direction,
            fill_price,
            filled_at,
        )
    log_manager.trade(
        f"[체결진입] {entry_direction} {fill_qty}계약 @ {fill_price} "
        f"| 평균={result['avg_entry_price']} 보유={result['position_qty']}계약"
    )
    self.dashboard.append_pnl_log(
        f"체결진입 | {entry_direction} {fill_qty}계약 @ {fill_price}",
        f"평균 {self.position.entry_price:.2f} 손절 {self.position.stop_price:.2f} 1차 {self.position.tp1_price:.2f}",
    )
    self.dashboard.set_ui_position_mode()
    _ts_log_diag(
        self,
        "EntryFillFlow",
        before=before,
        after=_ts_get_position_snapshot(self),
        pending=_ts_get_pending_snapshot(self),
        actual_side=actual_side,
        applied_side=entry_direction,
        fill_qty=fill_qty,
        fill_price=fill_price,
        order_no=payload.get("order_no", ""),
        fill_no=payload.get("fill_no", ""),
    )
    _ts_system_info_throttled(self, "balance_refresh_trigger_entry", "[BalanceRefresh] trigger=EntryFillFlow", min_interval_sec=30.0)
    QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))


def _ts_on_chejan_event_cybos_safe(self, payload: dict) -> None:
    _gubun = str(payload.get("gubun", "")).strip()
    if _gubun not in ("0", "1"):
        return

    event_key = (
        payload.get("gubun"),
        payload.get("order_no"),
        payload.get("fill_no"),
        payload.get("order_status"),
        payload.get("filled_qty"),
        payload.get("fill_price"),
        payload.get("unfilled_qty"),
    )
    if event_key == self._last_order_event_key:
        return
    self._last_order_event_key = event_key

    order_no = payload.get("order_no", "")
    status = payload.get("order_status", "")
    code = payload.get("code", "")
    account_no = str(payload.get("account_no", "")).strip()
    fill_qty = int(payload.get("filled_qty") or 0)
    fill_price = float(payload.get("fill_price") or 0.0) or float(payload.get("current_price") or 0.0)
    unfilled_qty = int(payload.get("unfilled_qty") or 0)
    side = _ts_order_side_to_direction(payload)
    is_final_fill = (status == "체결")

    _ts_log_diag(
        self,
        "ChejanFlow",
        gubun=payload.get("gubun", ""),
        account=account_no,
        order_no=order_no,
        status=status,
        code=code,
        side=side,
        fill_qty=fill_qty,
        fill_price=fill_price,
        unfilled_qty=unfilled_qty,
        pending=_ts_get_pending_snapshot(self),
        position=_ts_get_position_snapshot(self),
    )

    if _secrets.ACCOUNT_NO and account_no and account_no != _secrets.ACCOUNT_NO:
        _ts_log_diag(
            self,
            "ChejanAccountIgnored",
            expected=_secrets.ACCOUNT_NO,
            actual=account_no,
            order_no=order_no,
        )
        return

    if _gubun == "1":
        _ts_sync_from_balance_payload(self, payload)
        return

    # 체결 종목코드 검증 — 거래 코드와 다른 종목 체결은 포지션에 반영하지 않음
    _event_code = self._normalize_broker_code(code)
    _trade_code = self._normalize_broker_code(getattr(self, "_futures_code", ""))
    if _event_code and _trade_code and _event_code != _trade_code:
        _ts_log_diag(
            self,
            "ChejanCodeMismatch",
            event_code=_event_code,
            trade_code=_trade_code,
            order_no=order_no,
            status=status,
        )
        log_manager.system(
            f"[ChejanCodeMismatch] WARNING: 체결 코드({_event_code}) ≠ 거래 코드({_trade_code}) "
            f"— 주문번호={order_no} 포지션 반영 거부. HTS 잔고 직접 확인 필요.",
            "WARNING",
        )
        return

    log_manager.trade(
        f"[Chejan] 상태={status or '?'} 주문번호={order_no or '?'} "
        f"code={code or '?'} 방향={side or '?'} 체결={fill_qty} 미체결={unfilled_qty}"
    )

    pending = self._pending_order
    pending_matched = False
    if pending:
        if pending.get("order_no") and order_no and pending["order_no"] == order_no:
            pending_matched = True
        elif not pending.get("order_no"):
            pending["order_no"] = order_no or pending.get("order_no", "")
            pending_matched = True
    _ts_log_diag(
        self,
        "ChejanMatch",
        pending_matched=pending_matched,
        order_no=order_no,
        pending=_ts_get_pending_snapshot(self),
    )

    if not is_final_fill:
        if pending_matched:
            if not pending.get("accepted_at"):
                pending["accepted_at"] = datetime.datetime.now()
            log_manager.system(
                f"[Order] {status or '?'} kind={pending['kind']} qty={pending['qty']} order_no={order_no or '?'}"
            )
        return

    if fill_qty <= 0:
        return

    filled_at = _ts_parse_chejan_time(payload.get("order_time", ""))
    if not pending_matched:
        _ts_handle_external_fill(self, payload, side, fill_qty, fill_price, filled_at)
        return

    pending["filled_qty"] += fill_qty
    if pending["kind"] == "ENTRY":
        _ts_handle_entry_fill_cybos_safe(
            self,
            pending,
            payload,
            fill_qty,
            fill_price or pending["price_hint"],
            filled_at,
        )
    else:
        _ts_handle_exit_fill(
            self,
            pending,
            payload,
            fill_qty,
            fill_price or pending["price_hint"],
            filled_at,
        )

    if pending["filled_qty"] >= pending["qty"] or unfilled_qty == 0:
        self._clear_pending_order()


TradingSystem._on_order_message = _ts_on_order_message
TradingSystem._on_chejan_event = _ts_on_chejan_event_cybos_safe
TradingSystem._set_broker_sync_status = _ts_set_broker_sync_status
TradingSystem._push_balance_to_dashboard = _ts_push_balance_to_dashboard
TradingSystem._refresh_dashboard_balance = _ts_refresh_dashboard_balance
TradingSystem._refresh_dashboard_balance_ui_only = _ts_refresh_dashboard_balance_ui_only
TradingSystem._sync_position_from_broker = _ts_sync_position_from_broker
TradingSystem._manual_position_restore = _ts_manual_position_restore
TradingSystem._execute_entry = _ts_execute_entry
TradingSystem._execute_partial_exit = _ts_execute_partial_exit
TradingSystem._check_exit_triggers = _ts_check_exit_triggers


class _BrokerOrderAdapter:
    """EmergencyExit.set_order_manager()용 어댑터."""

    def __init__(self, broker, futures_code: str, acc_no: str):
        self._broker = broker
        self._code  = futures_code
        self._acc   = acc_no

    def send_market_order(self, code: str, side: str, qty: int, reason: str = "") -> int:
        ret = self._broker.send_market_order(
            account_no=self._acc,
            code=code or self._code,
            side=side,
            qty=qty,
            rqname=reason or "긴급청산",
            screen_no="1002",
        )
        return ret if ret == 0 else None


def main():
    # DB 초기화
    init_all_dbs()
    logger.info("[System] DB 초기화 완료")

    system = TradingSystem()
    system.run()


if __name__ == "__main__":
    main()
