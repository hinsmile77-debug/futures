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
import datetime
import time
import logging
import math
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
    fetch_today_trades, fetch_pnl_history,
    save_daily_stats, fetch_trend_daily, fetch_trend_weekly,
    fetch_trend_monthly, fetch_trend_yearly,
)
from config.settings import TRADES_DB, HORIZONS, PARTIAL_EXIT_RATIOS
from config import secrets as _secrets

# ── 핵심 모듈 ──────────────────────────────────────────────────
from collection.kiwoom import KiwoomAPI, RealtimeData, LatencySync
from collection.macro.regime_classifier import RegimeClassifier
from features.feature_builder import FeatureBuilder
from model.multi_horizon_model import MultiHorizonModel
from model.ensemble_decision import EnsembleDecision
from strategy.position.position_tracker import PositionTracker
from strategy.entry.checklist import EntryChecklist
from strategy.entry.position_sizer import PositionSizer
from strategy.entry.adaptive_kelly import AdaptiveKelly
from strategy.exit.time_exit import TimeExitManager
from learning.online_learner import OnlineLearner
from learning.prediction_buffer import PredictionBuffer
from learning.batch_retrainer import BatchRetrainer, MIN_TRAIN_BARS as _MIN_TRAIN_BARS
from safety.circuit_breaker import CircuitBreaker
from collection.kiwoom.investor_data import InvestorData
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


class TradingSystem:
    """미륵이 메인 트레이딩 시스템"""

    def __init__(self):
        logger.info("[System] 미륵이 초기화")
        log_manager.system("미륵이 초기화")

        # ── 키움 API 컴포넌트 ──────────────────────────────────
        self.kiwoom        = KiwoomAPI()
        self.latency_sync  = LatencySync()
        self.realtime_data: Optional[RealtimeData] = None  # login 후 초기화

        # 핵심 컴포넌트
        self.regime_classifier = RegimeClassifier()
        self.feature_builder   = FeatureBuilder()
        self.model             = MultiHorizonModel()
        self.ensemble          = EnsembleDecision()
        self.position          = PositionTracker()
        self.checklist         = EntryChecklist()
        self.sizer             = PositionSizer(account_balance=100_000_000)  # 기본 1억
        self.kelly             = AdaptiveKelly()
        self.time_exit         = TimeExitManager()
        self.online_learner    = OnlineLearner()
        self.pred_buffer       = PredictionBuffer()
        self.batch_retrainer   = BatchRetrainer()
        self.investor_data     = InvestorData(kiwoom_api=None)  # connect_kiwoom 후 api 주입
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

        # 현재 레짐
        self.current_regime       = "NEUTRAL"
        self.current_micro_regime = "혼합"
        self._verified_today: int = 0        # 당일 SGD 검증 누적 건수
        self._efficacy_tick:  int = 0        # 5분마다 효과 검증 패널 갱신용
        self._last_block_reason: str = ""    # 직전 진입 차단 이유 (중복 로그 방지)
        self._last_recovery_ts:  str = ""    # 마지막 복구 처리 분봉 ts (동일 분봉 반복 방지)

        # 재시작 시 이전 포지션 복원 (당일 데이터만)
        if self.position.load_state():
            msg = (
                f"[Position] 이전 포지션 복원: {self.position.status} "
                f"{self.position.quantity}계약 @ {self.position.entry_price} "
                f"(손절={self.position.stop_price:.2f})"
            )
            logger.warning(msg)           # SYSTEM 로그 파일 + 콘솔
            log_manager.system(msg, "WARNING")   # 대시보드 1 시스템 탭

        # 대시보드
        self.dashboard = create_dashboard()
        self.dashboard.set_account_options(
            [_secrets.ACCOUNT_NO] if _secrets.ACCOUNT_NO else [],
            _secrets.ACCOUNT_NO,
        )
        self.dashboard.btn_save_account.clicked.connect(
            self._save_account_from_dashboard
        )
        self._heartbeat_count: int = 0
        self._session_no: int = 0
        self._pending_order = None
        self._last_order_event_key = None
        self._broker_sync_verified: bool = False
        self._broker_sync_block_new_entries: bool = True
        self._broker_sync_last_error: str = "startup sync not attempted"

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
                _KiwoomOrderAdapter(self.kiwoom, self._futures_code, account_no)
            )

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
    ) -> None:
        self._pending_order = {
            "kind": kind,
            "direction": direction,
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
        result = self.kiwoom.request_futures_balance(account_no)
        if result is None:
            log_manager.system("[BrokerSync] OPW20006 조회 실패로 startup sync를 건너뜁니다.", "WARNING")
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
        self._clear_pending_order()
        after = f"{self.position.status} {self.position.quantity}계약 @ {self.position.entry_price:.2f}"
        log_manager.system(
            f"[BrokerSync] startup sync 완료: {before} -> {after}",
            "CRITICAL" if before != after else "INFO",
        )

    def connect_kiwoom(self) -> bool:
        """로그인 + 근월물 실시간 수신 등록."""
        print("[DBG CK-1] login() 호출 직전", flush=True)
        if not self.kiwoom.login():
            logger.error("[System] 키움 로그인 실패")
            return False
        self.kiwoom.register_chejan_callback(self._on_chejan_event)
        self.kiwoom.register_msg_callback(self._on_order_message)
        acc_raw = self.kiwoom.get_login_info("ACCNO")
        accounts = self.kiwoom.get_account_list()
        logger.info("[Account] ACCNO raw=%s", acc_raw)
        logger.info("[Account] parsed accounts=%s", accounts)
        self.dashboard.set_account_options(accounts, _secrets.ACCOUNT_NO)
        print("[DBG CK-2] login() 성공", flush=True)

        # 서버 종류 확인 (정보 로그용)
        server = self.kiwoom.get_login_info("GetServerGubun")
        server_label = "모의투자" if server == "1" else "실서버"
        print(f"[DBG CK-2b] 서버종류={server!r} ({server_label})", flush=True)
        if server == "1":
            logger.info("[System] 모의투자 서버 접속 — A0166000 SetRealReg 실시간 수신 사용")

        # A0166000: OPT50029 TR 및 SetRealReg 모두 동일 코드 사용
        # (모의투자 서버에서도 A0166000으로 SetRealReg 등록 시 틱 수신 확인됨)
        code = self.kiwoom.get_nearest_futures_code()
        print(f"[DBG CK-3] 근월물 코드={code} 서버={server_label}", flush=True)
        self._futures_code = code
        self.emergency_exit.set_futures_code(code)
        self.emergency_exit.set_order_manager(
            _KiwoomOrderAdapter(self.kiwoom, code, _secrets.ACCOUNT_NO)
        )
        self._sync_position_from_broker()

        self.realtime_data = RealtimeData(
            api              = self.kiwoom,
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

        self.investor_data._api = self.kiwoom  # 실거래 시 TR 폴링 활성화

        # 투자자ticker 실시간 타입 FID·코드 탐색 (진단용)
        # 결과는 PROBE.log 및 콘솔에 [PROBE-TICKER] 라인으로 출력됨
        # 확인 후 불필요하면 이 줄을 제거해도 됨
        self.kiwoom.probe_investor_ticker(extra_codes=[code])

        # 수급 TR은 COM 콜백 체인(run_minute_pipeline) 밖에서 수집해야 스택 오버런 방지
        # QTimer 60초마다 독립 실행 — 파이프라인은 캐시(get_features)만 읽음
        self._investor_timer = QTimer()
        self._investor_timer.timeout.connect(self._fetch_investor_data)
        self._investor_timer.start(60_000)

        logger.info("[System] 키움 실시간 수신 시작 — %s | 수급 타이머 60s 시작", code)
        return True

    def _fetch_investor_data(self) -> None:
        """수급 TR 수집 — QTimer에서 호출 (COM 콜백 체인 외부)."""
        if not is_market_open(datetime.datetime.now()):
            return
        try:
            self.investor_data.fetch_all()
        except Exception as e:
            logger.warning("[Investor] 타이머 수집 오류: %s", e)

    def _on_tick_price_update(self, bar: dict) -> None:
        """틱 수신마다 대시보드 헤더 현재가 갱신."""
        if self.realtime_data is None:
            return
        self.dashboard.update_price(
            price  = bar["close"],
            change = bar["close"] - bar.get("open", bar["close"]),
            code   = self.realtime_data.code,
        )

    def _on_hoga_update(self, bid1: float, ask1: float, bid_qty: int, ask_qty: int) -> None:
        """선물호가잔량 이벤트마다 OFI 누적 (분봉 확정 시 flush_minute()에서 집계)."""
        self.feature_builder.ofi.update_hoga(
            bid_price = bid1,
            bid_qty   = bid_qty,
            ask_price = ask1,
            ask_qty   = ask_qty,
        )

    def _on_candle_closed(self, candle: dict) -> None:
        """분봉 완성 콜백 — Qt 이벤트 스레드에서 호출됨."""
        now = datetime.datetime.now()
        if not is_market_open(now):
            return

        # latency → Circuit Breaker 연동
        self.circuit_breaker.record_api_latency(self.latency_sync.offset_sec)

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
        self._last_recovery_ts = ""   # 실제 분봉 수신 → 복구 ts 초기화

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

        # 대시보드 실시간 가격 동기화
        self.dashboard.update_price(
            price  = close,
            change = close - bar.get("open", close),
            code   = self.realtime_data.code if self.realtime_data else "",
        )

        # ── PendingOrder 타임아웃 체크 ────────────────────────────
        # 모의투자 서버에서 OnReceiveChejanData가 오지 않으면 PendingOrder가 영구 locked됨.
        # 60초 초과 + fill 없음 → 주문 소멸로 간주하고 clear.
        if self._pending_order is not None:
            _pending_age = (datetime.datetime.now() - self._pending_order["created_at"]).total_seconds()
            if _pending_age > 60 and self._pending_order.get("filled_qty", 0) == 0:
                log_manager.system(
                    f"[PendingOrder] 타임아웃 {_pending_age:.0f}s — "
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
            # CB③ 정확도 집계 — bootstrap 1/3 균등 예측(confidence≈0.333)은 제외.
            # 재시작 시 대량 검증으로 33.3% 즉시 충전 → CB 오발동 방지.
            _conf = v.get("confidence", 0.0) or 0.0
            if _conf > 0.38:
                self.circuit_breaker.record_accuracy(v["correct"])
            if v["correct"]:
                log_manager.learning(f"✓ {v['horizon']} 예측 적중 (conf={_conf:.1%})")
            else:
                log_manager.learning(f"✗ {v['horizon']} 예측 실패 (conf={_conf:.1%})")

        # ── STEP 2: SGD 온라인 자가학습 ────────────────────────
        # STEP 1 검증된 예측마다 해당 시점 피처로 즉시 partial_fit
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

        # 미시 레짐 업데이트 (v6.5)
        # TODO: ADX 계산 추가
        adx_dummy = 22.0
        self.current_micro_regime = self.regime_classifier.classify_micro(
            adx_dummy, atr_ratio
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
        decision = self.ensemble.compute(horizon_proba, self.current_regime)
        direction  = decision["direction"]
        confidence = decision["confidence"]
        grade      = decision["grade"]

        self.circuit_breaker.record_signal(direction)

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

            if _final_grade != "X":
                kelly_result = self.kelly.compute_fraction()
                size_result  = self.sizer.compute(
                    confidence          = confidence,
                    atr                 = atr,
                    regime              = self.current_regime,
                    grade_mult          = _cr["size_mult"],
                    adaptive_kelly_mult = kelly_result["multiplier"],
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
        self.dashboard.update_entry(_dir_ko, confidence, _final_grade, _checks_ui,
                                    qty=_qty_display)

        # [DBG-F7] 진입 실행 조건 평가
        debug_log.debug(
            "[DBG-F7] 진입조건: pos=%s CB=%s new_entry=%s grade=%s time_zone=%s",
            self.position.status, self.circuit_breaker.state,
            is_new_entry_allowed(), _final_grade, time_zone,
        )

        # 실제 진입: CB + 시간 조건 + 분봉 품질 모두 충족해야 실행
        if (
            _cr is not None
            and self.circuit_breaker.is_entry_allowed()
            and is_new_entry_allowed()
            and not self._broker_sync_block_new_entries
            and _final_grade not in ("X",)
            and _qty_display > 0
            and not _bar_volume_zero          # Guard-C3: volume=0 분봉 진입 차단
        ):
            dir_str = "LONG" if direction > 0 else "SHORT"
            if _cr["auto_entry"]:
                self._execute_entry(dir_str, close, _qty_display, atr, _final_grade)
            else:
                log_manager.trade(
                    f"[수동 확인 필요] {dir_str} {_qty_display}계약 @ {close} "
                    f"등급={_final_grade}"
                )
                notify(
                    f"진입 확인 요청: {dir_str} {_qty_display}계약\n"
                    f"등급={_final_grade} 신뢰도={confidence:.1%}",
                    "WARNING",
                )

        # ── 진입 차단 이유 로그 (이유가 바뀔 때만 1회 출력) ──────
        if direction != 0 and self.position.status == "FLAT":
            _cb_state = self.circuit_breaker.state
            if _cb_state != "NORMAL":
                _reason = f"[차단] Circuit Breaker {_cb_state} — 진입 불가 (CB 해제까지 대기)"
            elif self._broker_sync_block_new_entries:
                _reason = f"[차단] 브로커 sync 미검증 상태 — 자동진입 금지 ({self._broker_sync_last_error})"
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
        _unreal  = self.position.unrealized_pnl_pts(close) * 500_000  # KRW
        _var_krw = -(atr * 1.65 * self.position.quantity * 500_000) if self.position.quantity else 0.0
        self.dashboard.update_pnl_metrics(_unreal, _daily["pnl_krw"], _var_krw)

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
                    features   = {k: round(float(v), 4) for k, v in features.items()
                                  if v is not None and v == v},  # NaN/None 제외
                )
        except Exception as e:
            logger.warning("[STEP9] save_prediction 오류 (스킵): %s", e)

        # 🧠 자가학습 모니터 패널 갱신 (매분)
        self.dashboard.update_learning(self._gather_learning_stats())

        # 🎯 학습 효과 검증기 패널 갱신 (5분마다 — DB 쿼리 비용 분산)
        self._efficacy_tick += 1
        if self._efficacy_tick % 5 == 1:   # 첫 분 + 이후 5분마다
            self.dashboard.update_efficacy(self._gather_efficacy_stats())

        # 상태 바 '마지막 갱신' 타이머 리셋
        self.dashboard.notify_pipeline_ran()

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
        self.dashboard.append_pnl_log(
            f"부분청산TP{stage} | {result['direction']} {qty}계약 @ {result['exit_price']}",
            f"PnL {pnl:+.2f}pt  {result['pnl_krw']:+,.0f}원  잔여 {result['remaining']}계약",
        )
        _daily = self.position.daily_stats()
        self.dashboard.update_pnl_metrics(
            self.position.unrealized_pnl_pts(result["exit_price"]) * 500_000,
            _daily["pnl_krw"],
            0.0,
        )

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute(
            TRADES_DB,
            """INSERT INTO trades
               (entry_ts, exit_ts, direction, entry_price, exit_price,
                quantity, pnl_pts, pnl_krw, exit_reason, grade, regime)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result.get("entry_ts", now_str),
                now_str,
                result["direction"],
                result["entry_price"],
                result["exit_price"],
                result["quantity"],
                result["pnl_pts"],
                result["pnl_krw"],
                result["exit_reason"],
                result.get("grade", ""),
                self.current_regime,
            ),
        )
        self._refresh_pnl_history()

    def _send_kiwoom_entry_order(self, direction: str, qty: int) -> int:
        """키움 선물 진입 주문 전송 (SendOrderFO). 반환값: 0=성공, 음수=오류"""
        code = getattr(self, "_futures_code", "")
        if not code:
            return -1
        trade_type = 1 if direction == "LONG" else 2  # 1=신규매수, 2=신규매도
        return self.kiwoom.send_order_fo(
            rqname="진입", screen_no="1000",
            acc_no=_secrets.ACCOUNT_NO,
            code=code, trade_type=trade_type,
            qty=qty, price=0.0, hoga_gb="3",
        )

    def _send_kiwoom_exit_order(self, qty: int) -> int:
        """키움 선물 청산 주문 전송 (SendOrderFO). 반환값: 0=성공, 음수=오류"""
        code = getattr(self, "_futures_code", "")
        if not code or self.position.status == "FLAT":
            return -1
        trade_type = 4 if self.position.status == "LONG" else 3  # LONG→매도청산(4), SHORT→매수청산(3)
        return self.kiwoom.send_order_fo(
            rqname="청산", screen_no="1001",
            acc_no=_secrets.ACCOUNT_NO,
            code=code, trade_type=trade_type,
            qty=qty, price=0.0, hoga_gb="3",
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

        # 3순위: 부분 청산 (is_tp1_hit/is_tp2_hit 내부에서 partial_done 이중 체크)
        if self.position.is_tp1_hit(price):
            self._execute_partial_exit(price, stage=1)

        # TP1이 전량청산으로 전환된 경우 포지션이 FLAT → TP2 스킵
        if self.position.status != "FLAT" and self.position.is_tp2_hit(price):
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

        log_manager.trade(
            f"[청산 완료] PnL={pnl:+.2f}pt ({result['pnl_krw']:+,.0f}원)"
        )

        # PnL 패널 즉시 갱신 — 다음 분봉까지 기다리지 않음 [B27]
        _daily = self.position.daily_stats()
        self.dashboard.update_pnl_metrics(0.0, _daily["pnl_krw"], 0.0)
        self.dashboard.append_pnl_log(
            f"청산 | {result['direction']} {result['quantity']}계약 "
            f"@ {result['exit_price']} ({result['exit_reason']})",
            f"PnL {pnl:+.2f}pt  {result['pnl_krw']:+,.0f}원",
        )

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute(
            TRADES_DB,
            """INSERT INTO trades
               (entry_ts, exit_ts, direction, entry_price, exit_price,
                quantity, pnl_pts, pnl_krw, exit_reason, grade, regime)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result.get("entry_ts", now_str),
                now_str,
                result["direction"],
                result["entry_price"],
                result["exit_price"],
                result["quantity"],
                result["pnl_pts"],
                result["pnl_krw"],
                result["exit_reason"],
                result.get("grade", ""),
                self.current_regime,
            ),
        )
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
        return {
            "calibration_bins": calib,
            "grade_stats":      grades,
            "regime_stats":     regime,
            "accuracy_history": hist,
            "updated_at":       datetime.datetime.now().strftime("%H:%M"),
        }

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

    # ── 일일 마감 (15:40) ─────────────────────────────────────
    def daily_close(self):
        """자가학습 일일 마감"""
        stats = self.position.daily_stats()
        logger.info(f"[Daily] 마감 통계: {stats}")
        log_manager.system(
            f"일일 마감 | 승={stats['wins']} 패={stats['losses']} "
            f"PnL={stats['pnl_krw']:+,.0f}원"
        )

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
        self.investor_data.reset_daily()
        self.position.reset_daily()
        self.circuit_breaker.reset_daily()
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
            "trades":         stats["trades"],
            "wins":           stats["wins"],
            "pnl_pts":        stats["pnl_pts"],
            "pnl_krw":        stats["pnl_krw"],
            "sgd_accuracy":   self.online_learner.recent_accuracy(),
            "verified_count": self._verified_today,
        })

        self._refresh_pnl_history()
        self.dashboard.update_trend(self._gather_trend_stats())

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
        log_manager.system("자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료")
        self.dashboard.append_sys_log("자동 종료 예약 — 15초 후 프로그램 종료")
        QTimer.singleShot(15_000, self._auto_shutdown)

    def _auto_shutdown(self) -> None:
        """일일 마감 완료 후 자동 프로그램 종료 — Qt 이벤트 루프 종료."""
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
        import json
        state_path = os.path.join(BASE_DIR, "data", "session_state.json")
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        try:
            if os.path.exists(state_path):
                with open(state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                today = datetime.date.today().isoformat()
                if data.get("date") != today:
                    data = {"date": today, "count": 0}
            else:
                data = {"date": datetime.date.today().isoformat(), "count": 0}
        except Exception:
            data = {"date": datetime.date.today().isoformat(), "count": 0}

        data["count"] = data.get("count", 0) + 1
        try:
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            pass
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
        for row in rows:
            direction  = row["direction"] or "?"
            entry_p    = row["entry_price"] or 0.0
            exit_p     = row["exit_price"]
            qty        = row["quantity"] or 1
            pnl_pts    = row["pnl_pts"] or 0.0
            pnl_krw    = row["pnl_krw"] or 0.0
            reason     = row["exit_reason"] or ""
            grade      = row["grade"] or ""
            entry_ts   = (row["entry_ts"] or "")[:16]   # "YYYY-MM-DD HH:MM"
            exit_ts    = (row["exit_ts"]  or "")[:16]

            if exit_p is not None:
                # 청산 완료 거래
                cumulative_pnl_krw += pnl_krw
                self.dashboard.append_restore_trade(
                    msg=f"진입 {direction} {qty}계약 @ {entry_p}  등급={grade}",
                    ts=entry_ts[11:] if len(entry_ts) > 11 else entry_ts,
                )
                self.dashboard.append_restore_trade(
                    msg=f"청산 {direction} {qty}계약 @ {exit_p}  ({reason})",
                    ts=exit_ts[11:] if len(exit_ts) > 11 else exit_ts,
                    val=f"PnL {pnl_pts:+.2f}pt  {pnl_krw:+,.0f}원",
                )
                self.dashboard.append_restore_pnl(
                    msg=f"청산 | {direction} {qty}계약 @ {exit_p}  ({reason})",
                    ts=exit_ts[11:] if len(exit_ts) > 11 else exit_ts,
                    val=f"PnL {pnl_pts:+.2f}pt  {pnl_krw:+,.0f}원  (누적 {cumulative_pnl_krw:+,.0f}원)",
                )
            else:
                # 진입만 있고 청산 미완료 (비정상 종료)
                self.dashboard.append_restore_trade(
                    msg=f"[미청산] 진입 {direction} {qty}계약 @ {entry_p}  등급={grade}",
                    ts=entry_ts[11:] if len(entry_ts) > 11 else entry_ts,
                )

        # position_tracker 일일 통계 복원
        self.position.restore_daily_stats(rows)

        # 손익 PnL 패널 즉시 갱신 — 재시작 후 "——원" 방지
        _daily = self.position.daily_stats()
        self.dashboard.update_pnl_metrics(0.0, _daily["pnl_krw"], 0.0)

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

        # 대시보드 표시 + 긴급정지 버튼 연결
        self.dashboard.show()
        if hasattr(self.dashboard, "btn_kill"):
            self.dashboard.btn_kill.clicked.connect(
                lambda: self.activate_kill_switch("대시보드 긴급정지")
            )
        if self.realtime_data:
            server       = self.kiwoom.get_login_info("GetServerGubun")
            server_label = "모의투자" if server == "1" else "실서버"
            self.dashboard.append_sys_log(
                f"시스템 시작 | TR={self.realtime_data.code} [{server_label}] 분봉수집=실시간(SetRealReg)"
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
            if self.realtime_data:
                self.realtime_data.stop()
            self.daily_close()
            self._pre_market_done  = False
            self._daily_close_done = True

        # 키움 연결 감시
        if not self.kiwoom.is_connected:
            logger.error("[System] 키움 연결 끊김 — 재연결 시도")
            self.connect_kiwoom()

    def _log_waiting_status(self, now: datetime.datetime) -> None:
        """현재 대기 이유를 로그 + 대시보드에 표시."""
        t = now.time()
        if is_market_open(now):
            reason = "장중 — FC0 실시간 틱 대기 중 (분봉 파이프라인은 틱 수신 시 자동 실행)"
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
    msg = str(payload.get("msg", ""))
    _ts_log_diag(
        self,
        "OrderMsgFlow",
        pending=_ts_get_pending_snapshot(self),
        rq=payload.get("rq_name", ""),
        tr=payload.get("tr_code", ""),
        msg=msg,
    )
    if not self._pending_order:
        return
    if any(token in msg for token in ("거부", "실패", "오류")):
        log_manager.system(f"[Order] 주문 거부/오류: {msg}", "ERROR")
        self._clear_pending_order()


def _ts_handle_entry_fill(self, pending: dict, payload: dict, fill_qty: int, fill_price: float, filled_at: datetime.datetime) -> None:
    result = self.position.apply_entry_fill(
        direction=pending["direction"],
        price=fill_price,
        quantity=fill_qty,
        atr=pending["atr"],
        grade=pending["grade"],
        regime=self.current_regime,
        filled_at=filled_at,
    )
    log_manager.trade(
        f"[체결진입] {pending['direction']} {fill_qty}계약 @ {fill_price} "
        f"| 평균={result['avg_entry_price']} 보유={result['position_qty']}계약"
    )
    self.dashboard.append_pnl_log(
        f"체결진입 | {pending['direction']} {fill_qty}계약 @ {fill_price}",
        f"평균 {self.position.entry_price:.2f} 손절 {self.position.stop_price:.2f} 1차 {self.position.tp1_price:.2f}",
    )


def _ts_handle_exit_fill(self, pending: dict, payload: dict, fill_qty: int, fill_price: float, filled_at: datetime.datetime) -> None:
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
        return

    if "remaining" in result:
        log_manager.trade(
            f"[체결청산-분할] {result['direction']} {fill_qty}계약 @ {fill_price} "
            f"| 잔여={result['remaining']}계약"
        )
        return

    self._post_exit(result)


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
        ret = self._send_kiwoom_exit_order(self.position.quantity)
        if ret == 0:
            self._set_pending_order(
                kind="EXIT_FULL",
                direction=self.position.status,
                qty=self.position.quantity,
                price_hint=exit_price,
                reason="하드스톱",
            )
            log_manager.trade(
                f"[주문요청] 하드스톱 청산 {self.position.status} {self.position.quantity}계약 @ {exit_price}"
            )
        else:
            log_manager.system(f"[Exit] 하드스톱 주문 실패 ret={ret}", "ERROR")
        return

    if self.position.is_tp1_hit(price):
        self._execute_partial_exit(price, stage=1)

    if (not self._has_pending_order()
            and self.position.status != "FLAT"
            and self.position.is_tp2_hit(price)):
        self._execute_partial_exit(price, stage=2)

    if not self._has_pending_order() and self.time_exit.should_force_exit():
        ret = self._send_kiwoom_exit_order(self.position.quantity)
        if ret == 0:
            self._set_pending_order(
                kind="EXIT_FULL",
                direction=self.position.status,
                qty=self.position.quantity,
                price_hint=price,
                reason="15:10 강제청산",
            )
            log_manager.trade(
                f"[주문요청] 시간청산 {self.position.status} {self.position.quantity}계약 @ {price}"
            )
        else:
            log_manager.system(f"[Exit] 시간청산 주문 실패 ret={ret}", "ERROR")


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
    self.dashboard.append_pnl_log(
        f"체결청산-부분 | {result['direction']} {qty}계약 @ {result['exit_price']:.2f}",
        f"PnL {pnl:+.2f}pt  {result['pnl_krw']:+,.0f}원  잔여 {result['remaining']}계약",
    )

    _daily = self.position.daily_stats()
    self.dashboard.update_pnl_metrics(
        self.position.unrealized_pnl_pts(result["exit_price"]) * 500_000,
        _daily["pnl_krw"],
        0.0,
    )

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute(
        TRADES_DB,
        """INSERT INTO trades
           (entry_ts, exit_ts, direction, entry_price, exit_price,
            quantity, pnl_pts, pnl_krw, exit_reason, grade, regime)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            result.get("entry_ts", now_str),
            result.get("exit_ts", now_str),
            result["direction"],
            result["entry_price"],
            result["exit_price"],
            result["quantity"],
            result["pnl_pts"],
            result["pnl_krw"],
            result["exit_reason"],
            result.get("grade", ""),
            self.current_regime,
        ),
    )
    self._refresh_pnl_history()


def _ts_on_order_message(self, payload: dict) -> None:
    if not self._pending_order:
        return
    msg = str(payload.get("msg", ""))
    if any(token in msg for token in ("거부", "실패", "오류")):
        log_manager.system(f"[Order] 주문 거부/오류: {msg}", "ERROR")
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
    )
    log_manager.trade(
        f"[체결진입] {entry_direction} {fill_qty}계약 @ {fill_price} "
        f"| 평균={result['avg_entry_price']} 보유={result['position_qty']}계약"
    )
    self.dashboard.append_pnl_log(
        f"체결진입 | {entry_direction} {fill_qty}계약 @ {fill_price}",
        f"평균 {self.position.entry_price:.2f} 손절 {self.position.stop_price:.2f} 1차 {self.position.tp1_price:.2f}",
    )
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
        return

    if "remaining" in result:
        _ts_record_nonfinal_exit(self, result, pending["reason"])
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
        return

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
        else:
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
        log_manager.trade(
            f"[체결동기화] 외부진입 {side} {remaining_fill}계약 @ {fill_price} "
            f"| 평균={result['avg_entry_price']} 보유={result['position_qty']}계약"
        )
        self.dashboard.append_pnl_log(
            f"외부진입 동기화 | {side} {remaining_fill}계약 @ {fill_price}",
            f"평균 {self.position.entry_price:.2f} 손절 {self.position.stop_price:.2f}",
        )

    after = _ts_get_position_snapshot(self)
    log_manager.system(
        f"[OrderSync] 외부 체결 반영 완료 order_no={payload.get('order_no') or '?'} after={after}",
        "WARNING",
    )


def _ts_sync_from_balance_payload(self, payload: dict) -> None:
    code = self._normalize_broker_code(payload.get("code", ""))
    target_code = self._normalize_broker_code(getattr(self, "_futures_code", ""))
    if not code or not target_code or code != target_code:
        return

    qty = int(payload.get("holding_qty") or 0)
    avg_price = float(payload.get("avg_price") or 0.0)
    side = _ts_order_side_to_direction(payload.get("balance_side", ""))
    before = _ts_get_position_snapshot(self)

    if qty <= 0:
        if self.position.status != "FLAT":
            self.position.sync_flat_from_broker()
            self._clear_pending_order()
            log_manager.system(
                f"[BrokerSync] 잔고 Chejan 반영: {before} -> FLAT",
                "CRITICAL",
            )
        return

    if side not in ("LONG", "SHORT") or avg_price <= 0:
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
    after = _ts_get_position_snapshot(self)
    if before != after:
        self._clear_pending_order()
        log_manager.system(
            f"[BrokerSync] 잔고 Chejan 반영: {before} -> {after}",
            "CRITICAL",
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


def _ts_push_balance_to_dashboard(self, result: dict) -> None:
    if not result:
        return

    rows = list(result.get("nonempty_rows") or result.get("rows") or [])
    summary = dict(result.get("summary") or {})
    probe = dict(result.get("summary_probe") or {})

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

    if (not summary.get("총매매")) and (trade_sum or not rows):
        summary["총매매"] = f"{trade_sum:.0f}"
    if (not summary.get("총평가손익")) and (pnl_sum or not rows):
        summary["총평가손익"] = f"{pnl_sum:.0f}"
    if (not summary.get("총평가")) and (eval_sum or not rows):
        summary["총평가"] = f"{eval_sum:.0f}"

    realized_krw = 0.0
    try:
        realized_krw = float(self.position.daily_stats().get("pnl_krw", 0.0) or 0.0)
    except Exception:
        realized_krw = 0.0
    if not summary.get("실현손익"):
        summary["실현손익"] = f"{realized_krw:.0f}"

    trade_base = trade_sum or _num(summary.get("총매매"))
    pnl_base = _num(summary.get("총평가손익"))
    if not summary.get("총평가수익률"):
        rate = (pnl_base / trade_base * 100.0) if trade_base else 0.0
        summary["총평가수익률"] = f"{rate:.2f}"

    if not summary.get("추정자산"):
        summary["추정자산"] = f"{_num(summary.get('총평가')):.0f}"

    if not any(str(v).strip() for v in result.get("summary", {}).values()):
        logger.warning(
            "[BalanceUIFallback] summary blank from OPW20006; rows=%d probe=%s applied=%s",
            len(rows),
            probe,
            summary,
        )

    self.dashboard.update_account_balance(summary, rows)


def _ts_refresh_dashboard_balance(self) -> None:
    account_no = str(_secrets.ACCOUNT_NO or "").strip()
    if not account_no:
        return
    result = self.kiwoom.request_futures_balance(account_no)
    if result:
        _ts_push_balance_to_dashboard(self, result)


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
    result = self.kiwoom.request_futures_balance(account_no)
    if result is None:
        _ts_set_broker_sync_status(self, False, "OPW20006 returned None", True)
        log_manager.system("[BrokerSync] OPW20006 조회 실패로 startup sync를 건너뜁니다.", "WARNING")
        return
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
            if self.position.status != "FLAT":
                self.position.sync_flat_from_broker()
            self._clear_pending_order()
            _ts_set_broker_sync_status(self, True, "blank/no holdings response interpreted as flat", False)
            log_manager.system(
                f"[BrokerSync] startup sync 무포지션 확인(blank rows): {before} -> FLAT",
                "CRITICAL" if before != "FLAT" else "INFO",
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
        self._clear_pending_order()
        _ts_set_broker_sync_status(self, True, "balance chejan confirmed flat", False)
        log_manager.system(
            f"[BrokerSync] 잔고 Chejan 반영: {before} -> FLAT",
            "CRITICAL",
        )
        _ts_refresh_dashboard_balance(self)
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
    self._clear_pending_order()
    _ts_set_broker_sync_status(self, True, f"balance chejan synced {side} {qty} @ {avg_price}", False)
    after = _ts_get_position_snapshot(self)
    log_manager.system(
        f"[BrokerSync] 잔고 Chejan 반영: {before} -> {after}",
        "CRITICAL" if before != after else "INFO",
    )
    _ts_refresh_dashboard_balance(self)


def _ts_execute_entry(self, direction: str, price: float, quantity: int, atr: float, grade: str):
    _ts_log_diag(
        self,
        "EntryAttempt",
        direction=direction,
        price=price,
        quantity=quantity,
        atr=atr,
        grade=grade,
        broker_sync_verified=self._broker_sync_verified,
        block_new_entries=self._broker_sync_block_new_entries,
        broker_sync_reason=self._broker_sync_last_error,
        pending=_ts_get_pending_snapshot(self),
        position=_ts_get_position_snapshot(self),
    )
    if self._broker_sync_block_new_entries:
        log_manager.system(
            f"[EntryBlock] broker sync 미검증으로 진입 차단 dir={direction} qty={quantity} reason={self._broker_sync_last_error}",
            "CRITICAL",
        )
        logger.warning(
            "[EntryBlock] broker sync gate dir=%s qty=%s reason=%s",
            direction, quantity, self._broker_sync_last_error,
        )
        return
    if self._has_pending_order():
        logger.info("[Entry] pending order exists -> skip new entry %s %s", direction, quantity)
        return
    ret = self._send_kiwoom_entry_order(direction, quantity)
    logger.info(
        "[Entry] send_order result ret=%s dir=%s qty=%s code=%s broker_sync_verified=%s",
        ret, direction, quantity, getattr(self, "_futures_code", ""), self._broker_sync_verified,
    )
    _ts_log_diag(
        self,
        "EntrySendOrderResult",
        ret=ret,
        direction=direction,
        quantity=quantity,
        code=getattr(self, "_futures_code", ""),
        pending=_ts_get_pending_snapshot(self),
        position=_ts_get_position_snapshot(self),
    )
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
    # Fix B: 모의투자에서 Chejan 없음 → 낙관적 오픈으로 이중진입 방지
    # Chejan 체결 시 apply_entry_fill() 가격 보정 경로로 합쳐짐 (_optimistic=True)
    try:
        self.position.open_position(direction, price, quantity, atr, grade, self.current_regime)
        self.position._optimistic = True
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
        pending=_ts_get_pending_snapshot(self),
        position=_ts_get_position_snapshot(self),
    )
    log_manager.trade(
        f"[주문요청] {direction} {quantity}계약 @ {price} 등급={grade} 체결대기"
    )


TradingSystem._on_order_message = _ts_on_order_message
TradingSystem._on_chejan_event = _ts_on_chejan_event
TradingSystem._set_broker_sync_status = _ts_set_broker_sync_status
TradingSystem._push_balance_to_dashboard = _ts_push_balance_to_dashboard
TradingSystem._refresh_dashboard_balance = _ts_refresh_dashboard_balance
TradingSystem._sync_position_from_broker = _ts_sync_position_from_broker
TradingSystem._execute_entry = _ts_execute_entry
TradingSystem._execute_partial_exit = _ts_execute_partial_exit
TradingSystem._check_exit_triggers = _ts_check_exit_triggers


class _KiwoomOrderAdapter:
    """EmergencyExit.set_order_manager()용 어댑터 — KiwoomAPI를 OrderManager 인터페이스로 래핑."""

    def __init__(self, kiwoom_api, futures_code: str, acc_no: str):
        self._api   = kiwoom_api
        self._code  = futures_code
        self._acc   = acc_no

    def send_market_order(self, code: str, side: str, qty: int, reason: str = "") -> int:
        trade_type = 4 if side == "SELL" else 3   # SELL=매도청산(4), BUY=매수청산(3)
        ret = self._api.send_order_fo(
            rqname=reason or "긴급청산",
            screen_no="1002",
            acc_no=self._acc,
            code=code or self._code,
            trade_type=trade_type,
            qty=qty, price=0.0, hoga_gb="3",
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
