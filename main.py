# main.py — 메인 실행 진입점
"""
KOSPI 200 선물 방향 예측 시스템 — 미륵이 (Futures Edition)

실행 흐름:
  08:55  매크로 수집 → 레짐 판단 + 실시간 구독 사전 시작
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
import importlib
import queue as _queue
import subprocess
import threading
from collections import deque
import numpy as np
from typing import Optional

# ── 프로젝트 루트를 PYTHONPATH에 추가 ─────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ── Qt Application (키움 OCX 보다 먼저 생성) ───────────────────
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, Qt, QTimer, pyqtSignal
_qt_app = QApplication.instance() or QApplication(sys.argv)

# ── 로깅 초기화 (가장 먼저) ────────────────────────────────────
from utils.logger import setup_logging
setup_logging()
logger    = logging.getLogger("SYSTEM")
debug_log = logging.getLogger("DEBUG")

# ── DB 초기화 ──────────────────────────────────────────────────
from utils.db_utils import (
    init_all_dbs, execute, save_candle, save_features, save_candle_and_features,
    save_horizon_features, count_raw_candles,
    fetch_recent_raw_features,
    fetch_today_trades, fetch_pnl_history, normalize_trade_pnl,
    save_daily_stats, fetch_trend_daily, fetch_trend_weekly,
    fetch_trend_monthly, fetch_trend_yearly,
    is_plausible_futures_trade,
    upsert_daily_broker_pnl,
    save_shap_scores,
    save_regime_at, purge_old_regime_history,
)
from config.settings import (
    TRADES_DB, DB_DIR, HORIZONS, HORIZON_DIR, PARTIAL_EXIT_RATIOS,
    HURST_RANGE_THRESHOLD, ATR_MIN_ENTRY, ATR_STOP_MULT, ATR_HORIZON_TP1_MULT,
    CB_HIGH_CONF_THRESHOLD, MAX_CONTRACTS,
    SHAP_MIN_DATA_POINTS,
    FRED_API_KEY,
    HEALTH_LATENCY_WARN_MS, HEALTH_LATENCY_CRIT_MS,
    HEALTH_QUALITY_WARN, HEALTH_QUALITY_CRIT,
    HEALTH_CACHE_AGE_WARN_SEC, HEALTH_CACHE_AGE_CRIT_SEC,
    HEALTH_EXCEPTION_DENSITY_WARN_10M, HEALTH_EXCEPTION_DENSITY_CRIT_10M,
    HEALTH_TREND_WINDOW_MIN,
    HEALTH_DEGRADED_ENABLED, HEALTH_DEGRADED_ENTER_STREAK, HEALTH_DEGRADED_EXIT_STREAK,
    HEALTH_DEGRADED_WINDOW, HEALTH_DEGRADED_EXIT_RATIO,
    HEALTH_DEGRADED_SIZE_MULT, HEALTH_DEGRADED_MIN_CONF,
    HEALTH_DEGRADED_BLOCK_AUTO_ENTRY, HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY,
    HEALTH_POLICY_HOT_RELOAD_ENABLED, HEALTH_POLICY_HOT_RELOAD_INTERVAL_SEC,
    ENTRY_GRADE_C_AUTO_EXP, C_AUTO_EXP_SIZE_MULT, C_AUTO_EXP_ZONES,  # [P5]
)
import config.settings as runtime_settings
from config.constants import FUTURES_PT_VALUE, get_contract_spec, CB_STATE_HALTED, DIRECTION_FLAT
from config import secrets as _secrets

# ── 핵심 모듈 ──────────────────────────────────────────────────
from collection.broker import create_broker
from collection.macro.regime_classifier import RegimeClassifier
from collection.macro.micro_regime import MicroRegimeClassifier
from collection.macro.macro_fetcher import MacroFetcher
from collection.macro.intraday_tactical_regime import (
    IntradayTacticalRegime,
    INTRADAY_NORMAL, INTRADAY_DAY_RISK_OFF, INTRADAY_CRASH,
)
from collection.options.pcr_store import PCRStore
from collection.options.option_chain_snapshot import OptionChainSnapshot
from features.macro.macro_feature_transformer import MacroFeatureTransformer
from features.options.option_features import OptionFeatureCalculator
from learning.self_learning.daily_consolidator import DailyConsolidator
from learning.self_learning.drift_adjuster import DriftAdjuster
from features.feature_builder import FeatureBuilder
from features.bar_aggregator import BarAggregator
from model.multi_horizon_model import MultiHorizonModel
from model.rf_horizon_model import RFHorizonModel
from model.ensemble_decision import EnsembleDecision, select_entry_horizon
from strategy.position.position_tracker import PositionTracker
from strategy.entry.checklist import EntryChecklist
from strategy.entry.time_strategy_router import (
    get_zone_min_confidence, get_horizon_min_confs, update_dynamic_mc,
)
from strategy.entry.position_sizer import PositionSizer
from strategy.entry.meta_gate import MetaGate
from strategy.entry.trend_persistence import TrendPersistenceGate
from strategy.entry.adaptive_kelly import AdaptiveKelly
from strategy.exit.time_exit import TimeExitManager
from strategy.risk.toxicity_gate import ToxicityGate
from strategy.runtime.broker_runtime_service import BrokerRuntimeService
from strategy.runtime.execution_governor import ExecutionGovernor
from strategy.runtime.session_recovery_service import SessionRecoveryService
from strategy.profit_guard import ProfitGuard, ProfitGuardConfig
from learning.calibration import MultiHorizonCalibrator
from learning.online_learner import OnlineLearner
from learning.prediction_buffer import PredictionBuffer
from learning.batch_retrainer import BatchRetrainer, MIN_TRAIN_BARS as _MIN_TRAIN_BARS
from learning.threshold_recalibrator import ThresholdRecalibrator
from learning.shap.shap_tracker import ShapTracker
from safety.circuit_breaker import CircuitBreaker
from safety.kill_switch import KillSwitch
from safety.emergency_exit import EmergencyExit
from safety.system_health import SystemHealthScore
from logging_system.log_manager import log_manager
from utils.time_utils import (
    is_market_open, is_trading_day, get_time_zone, is_force_exit_time, is_new_entry_allowed,
    is_pre_market,
)
from utils.notify import (
    notify,
    notify_startup,
    notify_premarket_ready,
    notify_first_tick,
    notify_broker_sync_blocked,
    notify_connection_lost,
    notify_pipeline_delayed,
    set_slack_enabled,
    is_slack_enabled,
)
from utils.error_policy import ErrorLevel, apply_error_policy, classify_exception
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


def _dir_sign(v) -> int:
    """float 방향값(±0.5 등)을 -1/0/+1 정수 방향으로 안전 변환.

    int() 잘림(int(0.5)=0) 방지 — 부호 기반 변환.
    """
    f = float(v or 0)
    return 1 if f > 0 else (-1 if f < 0 else 0)


class _ShutdownSignal(QObject):
    """DailyClose 스레드 → 메인 Qt 스레드 종료 예약 (스레드-안전).

    QueuedConnection 으로 연결하면 emit() 을 어느 스레드에서 호출해도
    슬롯은 반드시 메인 이벤트 루프에서 실행된다.
    """
    request = pyqtSignal()


_shutdown_sig = _ShutdownSignal()  # 모듈 로드(메인 스레드)에서 생성 — thread affinity = main


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
        self.broker_runtime_service = BrokerRuntimeService()
        self.execution_governor = ExecutionGovernor()
        self.session_recovery_service = SessionRecoveryService()

        # 핵심 컴포넌트
        self.regime_classifier      = RegimeClassifier()
        self.micro_regime_clf       = MicroRegimeClassifier()
        self.intraday_regime        = IntradayTacticalRegime()
        self.macro_fetcher          = MacroFetcher(api_key_fred=FRED_API_KEY)
        self.macro_fetcher.start()
        self.feature_builder    = FeatureBuilder()
        self.feature_builder._on_core_fail = self._on_core_feature_fail
        # Phase 2: 1분봉 → N분봉 집계기 + 호라이즌별 피처 벡터 캐시
        self.bar_aggregator     = BarAggregator()
        self._hz_feat_cache     = {}   # {h_name: np.ndarray} — 마지막 완성봉 기반 피처 벡터
        self._hz_bar_age        = {}   # {h_name: int} — 마지막 완성봉 이후 경과 분 수
        self.model             = MultiHorizonModel()
        self.rf_model          = RFHorizonModel()
        self.rf_model.load_all()   # pkl 없으면 is_ready()=False로 graceful 유지
        self.ensemble          = EnsembleDecision()
        self._pt_value         = FUTURES_PT_VALUE   # connect_broker에서 종목코드 확정 후 갱신
        self.position          = PositionTracker(pt_value=self._pt_value)
        self.checklist         = EntryChecklist()
        self.sizer             = PositionSizer(account_balance=100_000_000)  # 기본 1억
        self.kelly             = AdaptiveKelly()
        self.time_exit         = TimeExitManager()
        self.online_learner    = OnlineLearner()
        self.horizon_calibrator = MultiHorizonCalibrator(list(HORIZONS.keys()))
        self._preload_horizon_calibration()          # DB에서 사전 fit → 첫 tick부터 보정 효과
        self.ensemble.calibrator = self.horizon_calibrator   # 앙상블 2차 압축 연결
        self.pred_buffer       = PredictionBuffer()
        self.meta_gate         = MetaGate()
        # selection bias 해소: skip된 신호의 meta_features 임시 보관
        # key=ts_str, value=[(meta_features, confidence), ...]
        # STEP 2 에서 동일 ts 검증 결과가 도착할 때 record_outcome 처리
        self._meta_shadow      = {}
        self.toxicity_gate     = ToxicityGate()
        self.trend_gate        = TrendPersistenceGate()
        self.batch_retrainer          = BatchRetrainer()
        _ss = self._read_session_state()
        _gbm_last  = _ss.get("gbm_last_retrain", "")
        _gbm_count = int(_ss.get("gbm_total_retrain_count", 0) or 0)
        if not _gbm_last:
            # session_state에 기록 없으면 feature_names.pkl mtime으로 fallback
            _fn_path = os.path.join(HORIZON_DIR, "feature_names.pkl")
            if os.path.exists(_fn_path):
                _gbm_last = datetime.datetime.fromtimestamp(
                    os.path.getmtime(_fn_path)
                ).strftime("%Y-%m-%d %H:%M")
        self.batch_retrainer.restore_stats(_gbm_last, _gbm_count)
        # GapOffset 재시작 복원 — 당일 session_state에 today_open 이 있으면 모델에 주입
        _gap_today = _ss.get("date", "")
        _gap_open  = float(_ss.get("today_open", 0.0) or 0.0)
        if _gap_today == datetime.date.today().isoformat() and _gap_open > 0:
            try:
                self.model.set_daily_gap_offset(_gap_open)
                self._first_tick_notified = True       # 첫 분봉에서 덮어쓰기 방지
                self._pre_market_gap_offset_set = True # [Bug-2] 플래그 동기화 — 이후 논리 일관성
                logger.info("[GapOffset] 재시작 복원: today_open=%.2f", _gap_open)
            except Exception as _ge:
                logger.warning("[GapOffset] 재시작 복원 실패: %s", _ge)
        self.threshold_recalibrator   = ThresholdRecalibrator()
        self.investor_data     = self.broker.create_investor_data()  # connect_broker 후 api 주입
        self.pcr_store          = PCRStore()
        self.option_chain_snap  = OptionChainSnapshot(
            chain_cache_path="data/option_chain.json",
            refresh_interval_min=5,
            atm_window_pt=30.0,
        )
        self.macro_transformer = MacroFeatureTransformer()
        self.option_feat_calc  = OptionFeatureCalculator()
        self.daily_consolidator = DailyConsolidator()
        self.drift_adjuster    = DriftAdjuster()
        # ── Phase 2 안전장치 ───────────────────────────────────
        self.emergency_exit  = EmergencyExit(
            position_tracker  = self.position,
            pending_registrar = self._set_pending_order,
        )
        self.kill_switch     = KillSwitch(
            emergency_exit_callback = self.emergency_exit.execute
        )
        self.circuit_breaker = CircuitBreaker(
            emergency_exit_callback = self.emergency_exit.execute
        )
        self.profit_guard    = ProfitGuard()

        # [4순위] 장 시작 5분 DNA 진단 (09:00~09:05 첫 5봉 채점)
        from safety.market_dna import MarketDNA
        self.market_dna = MarketDNA()

        # [5순위] CORE 피처 건강 점수 → Sizer 연동
        from features.core_health import CoreHealthScore
        self.core_health = CoreHealthScore()

        # [SHS] 시스템 건강 점수 + Early Kill Switch
        self.system_health = SystemHealthScore()

        # [6순위] Shadow Session + Contrarian Mode 트래커
        from safety.shadow_session import ShadowSessionTracker
        from safety.contrarian_mode import ContrarianModeTracker
        self.shadow_session = ShadowSessionTracker()
        self.contrarian_mode = ContrarianModeTracker(enable_real_order=False)
        from collections import deque as _deque
        self._z_warn_5m: "_deque[int]" = _deque(maxlen=5)  # Shadow 배지용 5분 z경고 롤링
        self._eks_recovery_conf_window: "_deque[float]" = _deque(maxlen=10)  # EKS 회복 판정용 최근 conf

        # 현재 레짐
        self.current_regime         = "NEUTRAL"
        self.current_micro_regime   = "혼합"
        self.current_intraday_regime = INTRADAY_NORMAL   # Layer 2 장중 전술 레짐
        self._verified_today: int = 0        # 당일 SGD 검증 누적 건수
        self._efficacy_tick:  int = 0        # 5분마다 효과 검증 패널 갱신용
        self._last_block_reason: str = ""    # 직전 진입 차단 이유 (중복 로그 방지)
        self._last_recovery_ts:  str = ""    # 마지막 복구 처리 분봉 ts (동일 분봉 반복 방지)
        # 거래소 CB 대기 모드
        self._exchange_cb_mode:  bool = False
        self._exchange_cb_start: Optional[datetime.datetime] = None
        # EnsembleGater 온라인 학습: 마지막 진입의 gate signals / direction 저장
        self._last_gate_signals: dict = {}
        self._last_gate_direction: int = 0
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
        self.dashboard.sig_layer2_gate_toggled.connect(self._on_layer2_gate_ui_toggled)
        self.dashboard.sig_tp1_protect_mode_changed.connect(self._on_tp1_protect_mode_changed)
        self.dashboard.sig_manual_exit_requested.connect(self._on_manual_exit_requested)
        self.dashboard.sig_apply_candidate_requested.connect(self._on_apply_shap_candidate_requested)
        self.dashboard.sig_force_retrain_requested.connect(self._on_force_feature_retrain_requested)
        self.dashboard.sig_reset_feature_set_requested.connect(self._on_reset_feature_set_requested)
        self.dashboard.sig_max_qty_changed.connect(self._on_max_qty_changed)
        self._max_entry_qty = self.dashboard.get_max_qty()
        self.dashboard.set_ui_startup_mode()
        # 스레드-안전 종료 예약: DailyClose 스레드가 emit() → 메인 스레드에서 _schedule_shutdown 호출
        _shutdown_sig.request.connect(self._schedule_shutdown, Qt.QueuedConnection)
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
        self._feature_registry_path = os.path.join(DB_DIR, "shap_feature_registry.json")
        self._restore_reverse_entry_setting()
        self._restore_tp1_protect_mode_setting()
        self._restore_auto_shutdown_state()
        self._heartbeat_count: int = 0
        self._session_no: int = 0
        self._restart_cause: str = "STARTUP"   # STARTUP / MANUAL / AUTO_DISCONNECT
        self._pending_order = None
        self._completed_order_nos: list = []   # 최근 완료 주문번호 (중복 chejan 콜백 방어)
        # Chejan 이벤트 큐: COM 콜백에서 push, 파이프라인 틱에서 drain
        # → BlockRequest() 메시지 펌프 도중 _pending_order 동시 접근 차단
        self._chejan_event_queue = _queue.Queue()
        self._auto_entry_enabled: bool = True   # Auto On/Off 토글 상태
        self._manual_entry_ctx: dict = {}        # 마지막 파이프라인 산출값 (수동 진입 버튼용)
        self._last_order_event_key = None
        self._broker_sync_verified: bool = False
        self._broker_sync_block_new_entries: bool = True
        self._broker_sync_last_error: str = "startup sync not attempted"
        self._warmup_retrain_pending: bool = False   # 세션 재시작 후 GBM 즉시 재학습 예약 플래그
        self._eod_retrain_ok: bool = False           # 전날 EOD 재학습 성공 여부 — 08:55 PreRetrain 스킵 판단용
        self._gbm_retrain_running: bool = False      # GBM 재학습 중복 실행 방지 플래그
        self._gbm_retrain_started_at: Optional[datetime.datetime] = None  # P1-B: 30분 타임아웃 감시용
        self._gbm_retrain_done_event = threading.Event()  # daily_close 대기용 — 초기값 set(완료 상태)
        self._gbm_retrain_done_event.set()
        self._pipeline_fatal_streak: int = 0         # [P0] 연속 ERR-FATAL 카운터
        self._scaler_refresh_running: bool = False   # Phase B 스케일러 refresh 중복 방지
        # ── 프리장 warmup 상태 (08:45~09:00) ──────────────────────
        self._pre_market_bars: list = []             # 프리장 분봉 버퍼
        self._pre_market_scaler_refitted: bool = False  # 프리장 refit 완료 플래그
        self._pre_market_gap_offset_set: bool = False   # GapOffset 사전 설정 완료
        self._pre_market_conf_history: list = []     # 프리장 conf 히스토리
        # ── 비동기 DB write 큐 (STEP 4 분봉·피처·호라이즌 저장용) ──────
        # 파이프라인 타이밍 윈도우 밖에서 SQLite 쓰기를 처리해 I/O 블로킹 제거.
        # maxsize=60: 약 1분치 6봉 × 10배 여유. 포화 시 동기 fallback.
        self._db_write_queue: _queue.Queue = _queue.Queue(maxsize=60)
        _db_writer = threading.Thread(
            target=self._db_write_worker, daemon=True, name="DBWriter"
        )
        _db_writer.start()
        self._const_out_refit_until = None           # ConstOut 트리거 쿨다운 (30분)
        self._const_out_heavy_cooldown_until = None  # ConstOut 직후 heavy 작업 유예 (3분)
        self._price_momentum_refit_until = None      # D_PRICE_MOMENTUM 쿨다운 (20분)
        self._grade_x_count: int = 0                 # 섹션 8: 당일 grade=X 분봉 수 집계
        self._checklist_conf_fail_count: int = 0     # [P3] 앙상블 통과 → Checklist 신뢰도 차단 횟수
        self._last_close: float = 0.0                # 직전 분봉 종가 — 옵션체인 QTimer 폴링에 사용
        # ── rolling σ 임계값 (방법3) ──────────────────────────────────────
        self._sigma_buf: deque = deque(maxlen=20)    # 1분봉 수익률 rolling 버퍼
        self._price_struct_buf: deque = deque(maxlen=8)  # 가격 구조 감지용 최근 8봉 OHLC
        self._sigma_20:  float = 0.0                 # 현재 rolling σ (%, 방법3 threshold 계산용)
        self._sigma_ready: bool = False              # sigma_20봉 달성 플래그
        self._last_sigma_20: float = 0.0            # 전날 EOD sigma (장 초반 20봉 미수집 구간 폴백)
        # GBM 첫 재학습 완료 전 보수 진입 제어
        self._pre_retrain_done: bool = False         # True이면 방법3 레이블 GBM 사용 중
        self._last_balance_result: dict = {}
        self._last_sizer_balance: float = 100_000_000.0
        self._effect_report_tick: int = 0
        self._effect_report_running: bool = False
        self._entry_cooldown_until: object = None  # [B53] ENTRY 타임아웃 후 재진입 쿨다운
        self._exit_cooldown_until:  object = None  # 청산 후 즉각 재진입 차단 쿨다운

        # ── P1-a: Restart Armistice ────────────────────────────────────────────
        # 재시작 직후 90초간 + broker sync 2회 clean 전까지 신규 진입 차단.
        # state_persist_enabled=False(개발 모드)일 때도 항상 적용.
        self._restart_armistice_until: object = (
            datetime.datetime.now() + datetime.timedelta(seconds=90)
        )
        self._restart_armistice_sync_count: int = 0

        # ── P1-b: Position Integrity Checksum ─────────────────────────────────
        self._integrity_broker_qty:  int  = 0   # 최근 balance chejan/TR에서 갱신
        self._integrity_fail_count:  int  = 0   # 연속 불일치 횟수

        # ── P3-a: OnlineLearner stuck 학습 오염 가드 ───────────────────────────
        self._stuck_this_minute: bool = False    # 이번 분봉에 stuck 해소 발생 여부

        # ── 호라이즌별 롤링 Bias 버퍼 (30건 윈도우) ──────────────────────────
        # 분봉 1건 통계(tot=1)는 100%/0%만 나와 무의미 → 30건 누적 후 편향 판정
        self._bias_buf: dict = {h: deque(maxlen=30) for h in HORIZONS}
        self._bias_log_tick: int = 0   # 10분마다 요약 로그 출력 카운터

        # ── [P2] FL 편향 고착 → uniform fallback 제어 ──────────────────────
        # FL 예측 비율 90%+ 가 20분 이상 지속되면 해당 호라이즌 예측을 (1/3,1/3,1/3)으로
        # 치환해 앙상블 오염을 차단한다. 2026-06-05 10m/15m FL 100% 고착 사례 대응.
        self._bias_fl_streak: dict = {h: 0 for h in HORIZONS}  # FL 편향 연속 분 카운터
        self._bias_override_horizons: set = set()               # uniform fallback 적용 호라이즌

        # ── [P2-진단] conf 고착 감지 ────────────────────────────────────────
        # conf가 N분 연속 동일값일 때 WARN 로그로 GBM/SGD 분해값을 기록
        self._conf_prev: dict = {}      # {h_name: float} 직전 틱 blended conf
        self._conf_stuck: dict = {h: 0 for h in HORIZONS}  # 연속 동일 카운터

        # ── 호라이즌 자격 상태 (Qualification) ──────────────────────────────────
        # qualified=True: 3 사이클 완료 → 앙상블 참여 허가 (Phase 3에서 실제 필터링)
        # 현재(Phase 1): 상태 추적만 — 앙상블 비중 변경 없음
        self._horizon_runtime_state: dict = {
            h: {
                "verified_cycles":  0,
                "trained_cycles":   0,
                "qualified":        False,
                "active":           False,
                "status":           "not_qualified",
                "weight":           0.0,
                "recent_accuracy":  0.0,
            }
            for h in HORIZONS
        }

        # ── 앙상블 보정기 conf 캐시 (T-1m 앙상블 conf 추적) ──────────────────
        # STEP 6에서 저장 → STEP 1에서 T-1m 앙상블 conf 조회 → ensemble_calibrator 누적
        self._ensemble_conf_cache: dict = {}  # {ts_str: (conf_float, 1m_included_bool)}

        # ── P3-b: Reverse Entry Clamp ─────────────────────────────────────────
        self._last_exit_direction: str = ""      # 마지막 청산 방향 "LONG" or "SHORT"

        # ── P0: 상태 영속화 On/Off ────────────────────────────────────────────
        # ui_prefs.json의 state_persist_enabled 키. 기본 True.
        self._state_persist_enabled: bool = self._load_state_persist_flag()

        # ── 진입 컨텍스트 (trade 기록용 셋업 태그) ─────────────────────────────
        self._entry_meta_action:  str  = ""      # take/reduce/skip
        self._entry_hurst_bucket: str  = ""      # trend/mean-revert/neutral
        self._entry_hour_bucket:  int  = 0       # 진입 시각 hour
        self._entry_was_restart:  int  = 0       # 세션 재시작 직후 진입 여부
        self._entry_had_partial:  int  = 0       # 해당 포지션에서 partial fill 발생
        self._shadow_ev = None  # [Phase2] ShadowEvaluator — 신버전 가상 실행
        self._last_health_level: str = "INFO"
        self._health_degraded_mode: bool = False
        self._health_warn_streak: int = 0
        self._health_info_streak: int = 0
        self._health_level_history: deque = deque(maxlen=10)
        self._health_policy: dict = self._build_health_policy()
        self._health_settings_path: str = os.path.join(BASE_DIR, "config", "settings.py")
        self._health_settings_mtime: float = 0.0
        self._health_policy_last_reload_check: float = 0.0
        self._param_corr_history = deque(maxlen=120)
        self._shap_feature_window = deque(maxlen=240)
        self._shap_tracker = None
        self._shap_last_update_minute = None
        self._cached_shap_importance = {}
        self._restored_corr_str: str = ""
        self._live_shap_ready: bool = False
        try:
            self._health_settings_mtime = float(os.path.getmtime(self._health_settings_path))
        except Exception:
            self._health_settings_mtime = 0.0

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
        log_manager.subscribe(
            "HEALTH",
            lambda e: self.dashboard.append_health_log(e.message, e.level),
        )
        self._restore_analysis_buffers()
        self._ensure_shap_tracker()
        self._update_shap_dashboard()

    @staticmethod
    def _build_health_policy(src=None) -> dict:
        mod = src or runtime_settings
        return {
            "latency_warn_ms": float(getattr(mod, "HEALTH_LATENCY_WARN_MS", HEALTH_LATENCY_WARN_MS)),
            "latency_crit_ms": float(getattr(mod, "HEALTH_LATENCY_CRIT_MS", HEALTH_LATENCY_CRIT_MS)),
            "quality_warn": float(getattr(mod, "HEALTH_QUALITY_WARN", HEALTH_QUALITY_WARN)),
            "quality_crit": float(getattr(mod, "HEALTH_QUALITY_CRIT", HEALTH_QUALITY_CRIT)),
            "cache_age_warn_sec": float(getattr(mod, "HEALTH_CACHE_AGE_WARN_SEC", HEALTH_CACHE_AGE_WARN_SEC)),
            "cache_age_crit_sec": float(getattr(mod, "HEALTH_CACHE_AGE_CRIT_SEC", HEALTH_CACHE_AGE_CRIT_SEC)),
            "exception_warn_10m": float(getattr(mod, "HEALTH_EXCEPTION_DENSITY_WARN_10M", HEALTH_EXCEPTION_DENSITY_WARN_10M)),
            "exception_crit_10m": float(getattr(mod, "HEALTH_EXCEPTION_DENSITY_CRIT_10M", HEALTH_EXCEPTION_DENSITY_CRIT_10M)),
            "trend_window_min": int(getattr(mod, "HEALTH_TREND_WINDOW_MIN", HEALTH_TREND_WINDOW_MIN)),
            "degraded_enabled": bool(getattr(mod, "HEALTH_DEGRADED_ENABLED", HEALTH_DEGRADED_ENABLED)),
            "degraded_enter_streak": int(getattr(mod, "HEALTH_DEGRADED_ENTER_STREAK", HEALTH_DEGRADED_ENTER_STREAK)),
            "degraded_exit_streak": int(getattr(mod, "HEALTH_DEGRADED_EXIT_STREAK", HEALTH_DEGRADED_EXIT_STREAK)),
            "degraded_window": int(getattr(mod, "HEALTH_DEGRADED_WINDOW", HEALTH_DEGRADED_WINDOW)),
            "degraded_exit_ratio": float(getattr(mod, "HEALTH_DEGRADED_EXIT_RATIO", HEALTH_DEGRADED_EXIT_RATIO)),
            "degraded_size_mult": float(getattr(mod, "HEALTH_DEGRADED_SIZE_MULT", HEALTH_DEGRADED_SIZE_MULT)),
            "degraded_min_conf": float(getattr(mod, "HEALTH_DEGRADED_MIN_CONF", HEALTH_DEGRADED_MIN_CONF)),
            "degraded_block_auto_entry": bool(getattr(mod, "HEALTH_DEGRADED_BLOCK_AUTO_ENTRY", HEALTH_DEGRADED_BLOCK_AUTO_ENTRY)),
            "degraded_block_manual_entry": bool(getattr(mod, "HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY", HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY)),
            "degraded_soft_latency_ms": float(getattr(mod, "HEALTH_DEGRADED_SOFT_LATENCY_MS", 1300.0)),
            "degraded_soft_warn_weight": float(getattr(mod, "HEALTH_DEGRADED_SOFT_WARN_WEIGHT", 0.35)),
            "const_out_heavy_cooldown_sec": float(getattr(mod, "CONST_OUT_HEAVY_COOLDOWN_SEC", 180.0)),
            "hot_reload_enabled": bool(getattr(mod, "HEALTH_POLICY_HOT_RELOAD_ENABLED", HEALTH_POLICY_HOT_RELOAD_ENABLED)),
            "hot_reload_interval_sec": float(getattr(mod, "HEALTH_POLICY_HOT_RELOAD_INTERVAL_SEC", HEALTH_POLICY_HOT_RELOAD_INTERVAL_SEC)),
        }

    def _ensure_shap_tracker(self) -> None:
        feature_names = list(self.model.feature_names or [])
        if not feature_names:
            return
        self._sync_feature_registry_with_model()
        if self._shap_tracker is None:
            self._shap_tracker = ShapTracker(feature_names)
            return
        if list(getattr(self._shap_tracker, "feature_names", [])) != feature_names:
            self._record_shap_feature_changes(
                list(getattr(self._shap_tracker, "feature_names", [])),
                feature_names,
            )
            self._shap_tracker = ShapTracker(feature_names)

    def _record_shap_feature_changes(self, old_names, new_names) -> None:
        if self._shap_tracker is None:
            return
        old_only = [name for name in old_names if name not in set(new_names)]
        new_only = [name for name in new_names if name not in set(old_names)]
        if not old_only and not new_only:
            return
        pair_count = max(len(old_only), len(new_only))
        for idx in range(pair_count):
            old_feat = old_only[idx] if idx < len(old_only) else "(removed)"
            new_feat = new_only[idx] if idx < len(new_only) else "(added)"
            self._shap_tracker.record_replacement(
                old_feat,
                new_feat,
                reason="[model_reload]",
            )

    def _load_feature_registry(self) -> dict:
        try:
            with open(self._feature_registry_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return {}

    def _save_feature_registry(self, data: dict) -> None:
        try:
            os.makedirs(os.path.dirname(self._feature_registry_path), exist_ok=True)
            with open(self._feature_registry_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("[FeatureRegistry] save failed: %s", exc)

    def _get_active_feature_set(self) -> list:
        registry = self._load_feature_registry()
        active = registry.get("active_features") or []
        if isinstance(active, list) and active:
            return list(active)
        return list(self.model.feature_names or [])

    def _sync_feature_registry_with_model(self) -> None:
        current = list(self.model.feature_names or [])
        if not current:
            return
        registry = self._load_feature_registry()
        changed = False
        if not registry.get("active_features"):
            registry["active_features"] = list(current)
            changed = True
        if not registry.get("baseline_features"):
            registry["baseline_features"] = list(current)
            changed = True
        if changed:
            self._save_feature_registry(registry)

    def _get_recent_available_feature_names(self) -> list:
        rows = fetch_recent_raw_features(limit=5)
        available = set()
        for row in rows:
            try:
                feat_dict = json.loads(row["features"])
            except Exception:
                continue
            if isinstance(feat_dict, dict):
                available.update(feat_dict.keys())
        return sorted(available)

    def _get_pretty_feature_name(self, feature_name: str) -> str:
        name_map = {
            "cvd_divergence": "CVD 다이버전스",
            "vwap_position": "VWAP 위치",
            "ofi_norm": "OFI 불균형",
            "foreign_call_net": "외인 콜순매수",
            "foreign_retail_divergence": "다이버전스 지수",
            "program_non_arb_net": "프로그램 비차익",
            "atr_ratio": "ATR 비율",
            "atr": "ATR",
            "vwap": "VWAP",
            "ofi_imbalance": "OFI 불균형도",
            "ofi_pressure": "OFI 압력",
            "cvd_direction": "CVD 방향",
            "above_vwap": "VWAP 상회",
        }
        return name_map.get(feature_name, feature_name)

    def _pick_shap_candidate(self, review: dict = None):
        self._ensure_shap_tracker()
        if self._shap_tracker is None:
            return None, "SHAP tracker 없음"
        # review를 인자로 받으면 재사용 — weekly_review() 중복 호출 방지
        if review is None:
            review = self._shap_tracker.weekly_review()
        candidates = list(review.get("candidates") or []) if isinstance(review, dict) else []
        if not candidates:
            return None, "추천 후보 없음"
        replace_allowed = (review.get("replace_allowed") or {}) if isinstance(review, dict) else {}
        if not bool(replace_allowed.get("allowed", False)):
            return None, str(replace_allowed.get("reason", "교체 불가"))
        available = set(self._get_recent_available_feature_names())
        for candidate in candidates:
            replacement = candidate.get("replacement")
            if replacement and replacement in available:
                return candidate, ""
        return None, "실데이터에 존재하는 대체 후보 없음"

    def _start_manual_retrain(self, force: bool, reason: str) -> bool:
        if getattr(self, "_gbm_retrain_running", False):
            log_manager.system(f"[FeatureOps] 재학습 진행 중 - {reason}", "WARN")
            return False
        self._gbm_retrain_running = True
        self._gbm_retrain_started_at = datetime.datetime.now()  # P1-B: 타임아웃 추적
        self._gbm_retrain_done_event.clear()
        self.circuit_breaker.set_gbm_retrain_active(True)   # CB⑤ 임계 완화
        log_manager.learning(f"[GBM] 수동 재학습 시작 | {reason}")

        def _retrain_worker():
            try:
                result = self.batch_retrainer.retrain_now(force=force)
            except Exception as exc:
                result = {"ok": False, "error": str(exc)}
            # P1-A 강화: ok/fail 무관 worker에서 즉시 해제 (QTimer daemon-thread 불안정 대비)
            self._gbm_retrain_running = False
            self._gbm_retrain_done_event.set()   # worker 스레드에서 직접 해제 (QTimer 전달 불안정 대비)
            QTimer.singleShot(0, lambda r=result: self._on_gbm_retrain_done(r, False))

        threading.Thread(target=_retrain_worker, daemon=True).start()
        return True

    def _on_apply_shap_candidate_requested(self) -> None:
        candidate, reason = self._pick_shap_candidate()
        if candidate is None:
            log_manager.system(f"[FeatureOps] 추천 적용 불가: {reason}", "WARN")
            return

        active = self._get_active_feature_set()
        old_feat = str(candidate.get("feature"))
        new_feat = str(candidate.get("replacement"))
        if old_feat not in active:
            log_manager.system(f"[FeatureOps] 현재 세트에 {old_feat} 없음", "WARN")
            return

        updated = [new_feat if feat == old_feat else feat for feat in active]
        registry = self._load_feature_registry()
        registry["active_features"] = updated
        registry["baseline_features"] = registry.get("baseline_features") or list(active)
        registry["pending_change"] = {
            "old": old_feat,
            "new": new_feat,
            "approved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reason": "weekly_review",
        }
        self._save_feature_registry(registry)
        if self._shap_tracker is not None:
            self._shap_tracker.record_replacement(old_feat, new_feat, reason="[approved]")
        log_manager.system(
            "[FeatureOps] 추천 승인: {} -> {}".format(
                self._get_pretty_feature_name(old_feat),
                self._get_pretty_feature_name(new_feat),
            ),
            "INFO",
        )
        self._start_manual_retrain(True, f"feature swap {old_feat}->{new_feat}")
        self._update_shap_dashboard()

    def _on_force_feature_retrain_requested(self) -> None:
        log_manager.system("[FeatureOps] 수동 재학습 버튼 클릭", "INFO")
        try:
            active = self._get_active_feature_set()
            registry = self._load_feature_registry()
            if not registry.get("active_features") and active:
                registry["active_features"] = list(active)
                registry["baseline_features"] = list(active)
                self._save_feature_registry(registry)
            self._start_manual_retrain(True, "current managed feature set")
        except Exception as _exc:
            log_manager.system(f"[FeatureOps] 수동 재학습 오류: {_exc}", "ERROR")

    def _on_reset_feature_set_requested(self) -> None:
        registry = self._load_feature_registry()
        baseline = list(registry.get("baseline_features") or [])
        if not baseline:
            baseline = list(self.model.feature_names or [])
        if not baseline:
            log_manager.system("[FeatureOps] 원복할 baseline feature set 없음", "WARN")
            return
        self._reset_rollback_active = list(registry.get("active_features") or [])
        registry["active_features"] = list(baseline)
        registry["pending_change"] = {
            "old": "*",
            "new": "baseline",
            "approved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reason": "reset",
        }
        self._save_feature_registry(registry)
        log_manager.system("[FeatureOps] baseline feature set으로 원복", "INFO")
        self._start_manual_retrain(True, "reset to baseline feature set")
        self._update_shap_dashboard()

    def _restore_analysis_buffers(self) -> None:
        """Restore restart-sensitive analysis buffers from persisted state."""
        try:
            rows = fetch_recent_raw_features(limit=max(self._param_corr_history.maxlen, self._shap_feature_window.maxlen))
        except Exception as exc:
            logger.warning("[AnalysisRestore] raw_features load failed: %s", exc)
            rows = []

        all_feat_rows = []
        if rows:
            for row in rows:
                try:
                    feat_dict = json.loads(row["features"])
                except Exception:
                    continue
                if not isinstance(feat_dict, dict):
                    continue

                all_feat_rows.append(feat_dict)

        self._restored_corr_str = self._build_param_corr_string(all_feat_rows)

        # _shap_feature_window 복원: 재시작 직후에도 SHAP_MIN_DATA_POINTS 충족 시 즉시 live 계산 가능
        if self.model.feature_names and all_feat_rows:
            for feat_dict in all_feat_rows[-self._shap_feature_window.maxlen:]:
                vec = [float(feat_dict.get(name, 0.0) or 0.0) for name in self.model.feature_names]
                self._shap_feature_window.append(vec)

        self._ensure_shap_tracker()
        if self._shap_tracker is not None:
            try:
                ranking = self._shap_tracker.get_current_ranking()
            except Exception as exc:
                logger.warning("[AnalysisRestore] shap history load failed: %s", exc)
                ranking = []
            if ranking:
                self._cached_shap_importance = {
                    row["feature"]: float(row["importance"])
                    for row in ranking
                }

        self._live_shap_ready = False
        if (
            not self._cached_shap_importance
            and self.model.is_ready()
            and self._shap_tracker is not None
            and self.model.feature_names
            # SHAP_MIN_DATA_POINTS(100)로 조건 통일 — 이전 >= 30은 update() 내부에서
            # len(X) < 100 체크로 항상 False를 반환해 복원 후 계산이 불가능했음
            and len(all_feat_rows) >= SHAP_MIN_DATA_POINTS
        ):
            horizon_model = self.model.models.get("1m")
            if horizon_model is None:
                horizon_model = next(iter(self.model.models.values()), None)
            if horizon_model is not None:
                restored_vectors = np.array(
                    [
                        [float(feat.get(name, 0.0) or 0.0) for name in self.model.feature_names]
                        for feat in all_feat_rows[-self._shap_feature_window.maxlen:]
                    ],
                    dtype=np.float32,
                )
                _restored_ok = self._shap_tracker.update(
                    horizon_model,
                    restored_vectors,
                    sample_size=min(120, len(restored_vectors)),
                )
                ranking = self._shap_tracker.get_current_ranking()
                if ranking:
                    self._cached_shap_importance = {
                        row["feature"]: float(row["importance"])
                        for row in ranking
                    }
                logger.info(
                    "[AnalysisRestore] SHAP 복원 계산: ok=%s, rows=%d, cached=%d",
                    _restored_ok, len(restored_vectors), len(self._cached_shap_importance),
                )

        logger.info(
            "[AnalysisRestore] live_corr=%d restored_corr=%s live_shap=%d live_ready=%s shap_features=%d",
            len(self._param_corr_history),
            "yes" if self._restored_corr_str else "no",
            len(self._shap_feature_window),
            "yes" if self._live_shap_ready else "no",
            len(self._cached_shap_importance),
        )

    def _record_param_corr_snapshot(self, features: dict) -> None:
        row = {
            label: float(features.get(fname, 0.0) or 0.0)
            for label, fname in _PARAM_FEAT_MAP.items()
        }
        self._param_corr_history.append(row)

    def _build_param_corr_string(self, history=None) -> str:
        history = list(self._param_corr_history) if history is None else list(history)
        if len(history) < 20:
            return ""
        labels = list(_PARAM_FEAT_MAP.keys())
        matrix = np.array(
            [
                [
                    float(
                        row.get(label, 0.0)
                        if label in row else row.get(_PARAM_FEAT_MAP[label], 0.0)
                    ) for label in labels
                ]
                for row in history
            ],
            dtype=float,
        )
        if matrix.shape[0] < 2:
            return ""

        corr_scores = []
        for idx, label in enumerate(labels):
            col = matrix[:, idx]
            if np.std(col) < 1e-9:
                continue
            vals = []
            for other_idx, other_label in enumerate(labels):
                if other_idx == idx:
                    continue
                other_col = matrix[:, other_idx]
                if np.std(other_col) < 1e-9:
                    continue
                rho = float(np.corrcoef(col, other_col)[0, 1])
                if np.isnan(rho):
                    continue
                vals.append(abs(rho))
            if vals:
                corr_scores.append((label, float(sum(vals) / len(vals))))

        if not corr_scores:
            return ""

        short_names = {
            "CVD 다이버전스":  "CVD",
            "VWAP 위치":       "VWAP",
            "OFI 불균형":      "OFI",
            "외인 콜순매수":   "외인콜",
            "다이버전스 지수": "다이버전스",
            "프로그램 비차익": "프로그램",
        }
        corr_scores.sort(key=lambda item: item[1], reverse=True)
        return "  ".join(
            f"{short_names.get(label, label)} ρ{score:.2f}"
            for label, score in corr_scores[:4]
        )

    def _get_param_corr_display(self) -> str:
        live_corr = self._build_param_corr_string()
        if live_corr:
            return live_corr
        if self._restored_corr_str:
            return "[RESTORED] " + self._restored_corr_str
        return ""

    def _record_shap_feature_window(self, features: dict) -> None:
        if not self.model.feature_names:
            return
        vec = [float(features.get(name, 0.0) or 0.0) for name in self.model.feature_names]
        self._shap_feature_window.append(vec)

    def _refresh_shap_state(self, ts: str) -> None:
        self._ensure_shap_tracker()
        if not self.model.is_ready() or self._shap_tracker is None:
            return
        if len(self._shap_feature_window) < SHAP_MIN_DATA_POINTS:
            return

        minute_key = str(ts or "")[:16]
        if minute_key and self._shap_last_update_minute == minute_key:
            return
        self._shap_last_update_minute = minute_key

        horizon_model = self.model.models.get("1m")
        if horizon_model is None:
            horizon_model = next(iter(self.model.models.values()), None)
        if horizon_model is None:
            return

        X_recent = np.array(list(self._shap_feature_window), dtype=np.float32)
        updated = self._shap_tracker.update(horizon_model, X_recent, sample_size=min(120, len(X_recent)))
        if not updated:
            logger.warning(
                "[ShapRefresh] update() False — window=%d, model_feat=%d, tracker_feat=%d",
                len(X_recent),
                len(self.model.feature_names or []),
                len(getattr(self._shap_tracker, "feature_names", []) or []),
            )
            return

        ranking = self._shap_tracker.get_current_ranking()
        if not ranking:
            return

        score_map = {
            row["feature"]: float(row["importance"])
            for row in ranking
        }
        self._cached_shap_importance = score_map
        self._live_shap_ready = True
        save_shap_scores(ts, "1m", score_map)
        self._update_shap_dashboard()

    def _update_shap_dashboard(self) -> None:
        self._ensure_shap_tracker()
        if self._shap_tracker is None:
            return
        ranking = self._shap_tracker.get_current_ranking()
        if not ranking:
            # [fallback] SHAP 히스토리 없음 → GBM 내장 importance로 기본 표시
            # 히스토리 길이 불일치(피처 수 변경 후 첫 재시작) 또는 아직 미계산 상태에서
            # 중간 패널이 완전히 비는 것을 방지한다.
            _gbm_imp = self.model.get_feature_importance() if self.model.is_ready() else {}
            if not _gbm_imp:
                return
            ranking = [
                {"rank": i + 1, "feature": fn, "importance": float(v)}
                for i, (fn, v) in enumerate(
                    sorted(_gbm_imp.items(), key=lambda t: -t[1])
                )
            ]
            logger.debug("[ShapDash] SHAP ranking 없음 → GBM importance fallback (n=%d)", len(ranking))

        def _pretty_name(feature_name: str) -> str:
            name_map = {
                "cvd_divergence": "CVD 다이버전스",
                "vwap_position": "VWAP 위치",
                "ofi_norm": "OFI 불균형",
                "foreign_call_net": "외인 콜순매수",
                "foreign_retail_divergence": "다이버전스 지수",
                "program_non_arb_net": "프로그램 비차익",
                "atr_ratio": "ATR 비율",
                "atr": "ATR",
                "vwap": "VWAP",
                "ofi_imbalance": "OFI 불균형도",
                "ofi_pressure": "OFI 압력",
                "cvd_direction": "CVD 방향",
                "above_vwap": "VWAP 상회",
            }
            return name_map.get(feature_name, feature_name)

        review = self._shap_tracker.weekly_review()
        score_map = {row["feature"]: float(row["importance"]) for row in ranking}
        rank_map = {row["feature"]: int(row["rank"]) for row in ranking}
        candidate_map = {
            row["feature"]: row
            for row in review.get("candidates", [])
        } if isinstance(review, dict) else {}
        declining = set(review.get("declining", [])) if isinstance(review, dict) else set()
        # 단기 CORE — SHAP 대시보드 패널 기준 (1m GBM 기준 SHAP 계산이므로 단기 CORE 고정)
        # 중기/장기 CORE(opt_gex_bn 등)는 해당 호라이즌 SHAP 탭 구현 후 확장 예정
        # ── 단기 CORE (1m~5m) ───────────────────────────────────────
        _short_core_feats = [
            ("CVD 다이버전스", "cvd_divergence", False),
            ("VWAP 위치",      "vwap_position",  True),   # forced_x=True
            ("OFI 불균형",     "ofi_norm",        False),
        ]
        core_items = []
        for pretty, feat, forced_x in _short_core_feats:
            feat_rank = rank_map.get(feat, 999)
            recent_ranks = self._shap_tracker.get_recent_ranks(feat, lookback=4)
            if feat in declining:
                status = "약화"
            elif feat_rank <= 3:
                status = "핵심"
            elif feat_rank <= 6:
                status = "안정"
            elif recent_ranks and recent_ranks[-1] > min(recent_ranks):
                status = "주의"
            else:
                status = "모니터"
            core_items.append({
                "name": pretty,
                "shap": score_map.get(feat, 0.0),
                "status": status,
                "forced_x": forced_x,
            })

        # ── 중기 CORE (10m~15m) ─────────────────────────────────────
        _vix_raw   = getattr(self, "_last_macro_vix_raw", None)    # 0~1 정규화값
        _vix_lbl   = f"VIX={_vix_raw*100:.0f} {'↓' if _vix_raw and _vix_raw < 0.5 else '↑'}" if _vix_raw else ""
        _mid_core_feats = [
            ("VWAP 위치",    "vwap_position", True,  ""),
            ("macro_vix",    "macro_vix",     False, _vix_lbl),
        ]
        mid_core_items = []
        for pretty, feat, forced_x, extra in _mid_core_feats:
            feat_rank = rank_map.get(feat, 999)
            recent_ranks = self._shap_tracker.get_recent_ranks(feat, lookback=4)
            if feat in declining:
                status = "약화"
            elif feat_rank <= 3:
                status = "핵심"
            elif feat_rank <= 8:
                status = "안정"
            elif recent_ranks and recent_ranks[-1] > min(recent_ranks):
                status = "주의"
            else:
                status = "모니터"
            mid_core_items.append({
                "name": pretty,
                "shap": score_map.get(feat, 0.0),
                "status": status,
                "forced_x": forced_x,
                "extra": extra,
            })

        # ── 장기 CORE (30m) ──────────────────────────────────────────
        _pcr_raw   = getattr(self, "_last_opt_chain_pcr", None)
        _pcr_lbl   = f"PCR={_pcr_raw:.2f}" if _pcr_raw else ""
        _long_core_feats = [
            ("opt_chain_pcr", "opt_chain_pcr", False, _pcr_lbl),
            ("macro_vix",     "macro_vix",     False, _vix_lbl),
        ]
        long_core_items = []
        for pretty, feat, forced_x, extra in _long_core_feats:
            feat_rank = rank_map.get(feat, 999)
            recent_ranks = self._shap_tracker.get_recent_ranks(feat, lookback=4)
            if feat in declining:
                status = "약화"
            elif feat_rank <= 3:
                status = "핵심"
            elif feat_rank <= 8:
                status = "안정"
            else:
                status = "모니터"
            long_core_items.append({
                "name": pretty,
                "shap": score_map.get(feat, 0.0),
                "status": status,
                "forced_x": forced_x,
                "extra": extra,
            })

        # ── 단기 CORE 제외 동적 TOP3 ────────────────────────────────
        _all_core_feats = {f for _, f, *_ in _short_core_feats + _mid_core_feats + _long_core_feats}
        dynamic_items = []
        for row in ranking:
            feat = row["feature"]
            if feat in _all_core_feats:
                continue
            if feat in candidate_map:
                status = "교체후보"
            elif feat in declining:
                status = "약화"
            elif self._live_shap_ready:
                status = "유지"
            else:
                status = "복원"
            dynamic_items.append({
                "rank": row["rank"],
                "name": _pretty_name(feat),
                "shap": score_map.get(feat, 0.0),
                "status": status,
            })
            if len(dynamic_items) >= 3:
                break

        rank_items = [
            {
                "name": _pretty_name(row["feature"]),
                "shap": score_map.get(row["feature"], 0.0),
            }
            for row in ranking[:6]
        ]

        replace_state = self._shap_tracker.get_replace_state()
        cooldown = {
            "progress": replace_state.get("cooldown_progress", 0),
            "label": replace_state.get("reason", "기록 없음"),
        }

        replace_log = self._shap_tracker.get_replace_log(limit=5)
        change_lines = []
        for entry in reversed(replace_log):
            change_lines.append(
                "{}  교체  {} -> {}  {}".format(
                    str(entry.get("date", ""))[5:10],
                    _pretty_name(str(entry.get("old", "-"))),
                    _pretty_name(str(entry.get("new", "-"))),
                    str(entry.get("reason", "")).strip() or "[수동]",
                )
            )

        candidate, candidate_reason = self._pick_shap_candidate(review=review)
        registry = self._load_feature_registry()
        pending = registry.get("pending_change") or {}
        if candidate is not None:
            summary = "{} -> {} | 승인 즉시 재학습".format(
                _pretty_name(str(candidate.get("feature", "-"))),
                _pretty_name(str(candidate.get("replacement", "-"))),
            )
        elif pending:
            summary = "대기 변경: {} -> {}".format(
                _pretty_name(str(pending.get("old", "-"))),
                _pretty_name(str(pending.get("new", "-"))),
            )
        else:
            summary = "추천 없음: {}".format(candidate_reason or "후보 대기")
        action_state = {
            "summary": summary,
            "can_apply": candidate is not None,
            "can_retrain": not getattr(self, "_gbm_retrain_running", False),
            "can_reset": bool(registry.get("baseline_features")),
        }

        self.dashboard.update_shap(
            core_items,
            dynamic_items,
            rank_items,
            cooldown=cooldown,
            change_lines=change_lines,
            action_state=action_state,
            mid_core_items=mid_core_items,
            long_core_items=long_core_items,
            entry_horizon=getattr(self, "_entry_horizon", "1m") or "1m",
        )

    def _maybe_reload_health_policy(self) -> None:
        policy = self._health_policy
        if not bool(policy.get("hot_reload_enabled", True)):
            return
        now_ts = time.time()
        min_interval = max(1.0, float(policy.get("hot_reload_interval_sec", 5.0) or 5.0))
        if now_ts - self._health_policy_last_reload_check < min_interval:
            return
        self._health_policy_last_reload_check = now_ts
        try:
            current_mtime = float(os.path.getmtime(self._health_settings_path))
        except Exception:
            return
        if current_mtime <= float(self._health_settings_mtime):
            return

        try:
            reloaded = importlib.reload(runtime_settings)
            self._health_policy = self._build_health_policy(reloaded)
            self._health_settings_mtime = current_mtime
            p = self._health_policy
            log_manager.system(
                "[HealthPolicy] settings.py 핫리로드 반영 "
                f"(lat_warn={p['latency_warn_ms']:.0f}ms, q_warn={p['quality_warn']:.2f}, "
                f"block_auto={p['degraded_block_auto_entry']}, block_manual={p['degraded_block_manual_entry']})",
                "INFO",
            )
        except Exception as _reload_e:
            logger.warning("[HealthPolicy] settings.py 핫리로드 실패: %s", _reload_e)

    def _canary_load_z_warn(self, n_rows: int = 60) -> int:
        """raw_data.db 최근 n_rows 피처로 현재 scaler z-score 극단 피처 수 반환."""
        import sqlite3 as _sq3
        import json as _json
        from config.settings import RAW_DATA_DB as _RAW_DB
        if not os.path.exists(_RAW_DB):
            return 0
        try:
            with _sq3.connect(_RAW_DB, timeout=5) as _conn:
                _rows = _conn.execute(
                    "SELECT features FROM raw_features ORDER BY ts DESC LIMIT ?",
                    (n_rows,),
                ).fetchall()
            if not _rows:
                return 0
            _fn = self.model.feature_names
            if not _fn:
                return 0
            _X = np.array(
                [[_json.loads(r[0]).get(k, 0.0) for k in _fn] for r in _rows],
                dtype=float,
            )
            return self.model.canary_z_warn_count(_X)
        except Exception as _e:
            logger.debug("[Canary] z_warn 로드 실패: %s", _e)
            return 0

    def _emit_runtime_health(self, features: dict, latency_ms: float) -> None:
        """Day10: 운영 헬스 스냅샷 생성/전파 (대시보드 + HEALTH 로그)."""
        try:
            self._maybe_reload_health_policy()
            p = self._health_policy
            quality_score = float(features.get("feature_quality_score", 1.0) or 0.0)
            macro_stats = self.macro_fetcher.get_stats() if hasattr(self, "macro_fetcher") else {}
            macro_cache_age = float(macro_stats.get("cache_age", -1) or -1)
            investor_age = float(features.get("quality_investor_age_sec", -1) or -1)
            cache_age_sec = max(macro_cache_age, investor_age, 0.0)

            level_counts = log_manager.get_level_counts(since_sec=600, layer="SYSTEM")
            exception_density_10m = float(
                level_counts.get("WARNING", 0)
                + level_counts.get("ERROR", 0)
                + level_counts.get("CRITICAL", 0)
            )

            health_level = self._classify_health_level(
                latency_ms=latency_ms,
                quality_score=quality_score,
                cache_age_sec=cache_age_sec,
                exception_density_10m=exception_density_10m,
            )
            self._update_degraded_mode(health_level, latency_ms=latency_ms)

            self.dashboard.update_runtime_health({
                "latency_ms": latency_ms,
                "quality_score": quality_score,
                "cache_age_sec": cache_age_sec,
                "exception_density_10m": exception_density_10m,
                "trend_window_min": int(p.get("trend_window_min", HEALTH_TREND_WINDOW_MIN)),
                "health_level": health_level,
                "degraded_mode": self._health_degraded_mode,
                "thresholds": {
                    "latency_warn_ms": float(p.get("latency_warn_ms", HEALTH_LATENCY_WARN_MS)),
                    "latency_crit_ms": float(p.get("latency_crit_ms", HEALTH_LATENCY_CRIT_MS)),
                    "quality_warn": float(p.get("quality_warn", HEALTH_QUALITY_WARN)),
                    "quality_crit": float(p.get("quality_crit", HEALTH_QUALITY_CRIT)),
                    "cache_age_warn_sec": float(p.get("cache_age_warn_sec", HEALTH_CACHE_AGE_WARN_SEC)),
                    "cache_age_crit_sec": float(p.get("cache_age_crit_sec", HEALTH_CACHE_AGE_CRIT_SEC)),
                    "exception_warn_10m": float(p.get("exception_warn_10m", HEALTH_EXCEPTION_DENSITY_WARN_10M)),
                    "exception_crit_10m": float(p.get("exception_crit_10m", HEALTH_EXCEPTION_DENSITY_CRIT_10M)),
                },
            })

            # HEALTH 로그는 상태 변경 또는 비정상 구간에서만 발행해 노이즈를 줄인다.
            if health_level != self._last_health_level or health_level != "INFO":
                log_manager.health(
                    "[Health] level=%s degraded=%s | latency=%.0fms | quality=%.2f | cache_age=%.0fs | exceptions_10m=%.0f"
                    % (
                        health_level,
                        "ON" if self._health_degraded_mode else "OFF",
                        latency_ms,
                        quality_score,
                        cache_age_sec,
                        exception_density_10m,
                    ),
                    health_level,
                )
                self._last_health_level = health_level
        except Exception as _h_e:
            logger.debug("[Health] snapshot emit 실패: %s", _h_e)

    def _classify_health_level(
        self,
        *,
        latency_ms: float,
        quality_score: float,
        cache_age_sec: float,
        exception_density_10m: float,
    ) -> str:
        p = self._health_policy
        if (
            latency_ms >= float(p.get("latency_crit_ms", HEALTH_LATENCY_CRIT_MS))
            or quality_score < float(p.get("quality_crit", HEALTH_QUALITY_CRIT))
            or cache_age_sec >= float(p.get("cache_age_crit_sec", HEALTH_CACHE_AGE_CRIT_SEC))
            or exception_density_10m >= float(p.get("exception_crit_10m", HEALTH_EXCEPTION_DENSITY_CRIT_10M))
        ):
            return "CRITICAL"
        if (
            latency_ms >= float(p.get("latency_warn_ms", HEALTH_LATENCY_WARN_MS))
            or quality_score < float(p.get("quality_warn", HEALTH_QUALITY_WARN))
            or cache_age_sec >= float(p.get("cache_age_warn_sec", HEALTH_CACHE_AGE_WARN_SEC))
            or exception_density_10m >= float(p.get("exception_warn_10m", HEALTH_EXCEPTION_DENSITY_WARN_10M))
        ):
            return "WARNING"
        return "INFO"

    def _update_degraded_mode(self, health_level: str, latency_ms: float = 0.0) -> None:
        p = self._health_policy
        if not bool(p.get("degraded_enabled", HEALTH_DEGRADED_ENABLED)):
            self._health_degraded_mode = False
            self._health_warn_streak = 0
            self._health_info_streak = 0
            self._health_level_history.clear()
            return

        warn_weight = 0.0
        if health_level in ("WARNING", "CRITICAL"):
            soft_ms = float(p.get("degraded_soft_latency_ms", 1300.0))
            soft_weight = float(p.get("degraded_soft_warn_weight", 0.35))
            warn_weight = soft_weight if health_level == "WARNING" and latency_ms < soft_ms else 1.0

        self._health_level_history.append(warn_weight)
        window = int(p.get("degraded_window", HEALTH_DEGRADED_WINDOW))
        history = list(self._health_level_history)[-window:]
        warn_score = sum(float(v) for v in history)
        warn_ratio = warn_score / max(1, len(history))

        if health_level in ("WARNING", "CRITICAL"):
            self._health_warn_streak += warn_weight
            self._health_info_streak = 0
            _enter_thresh = float(p.get("degraded_enter_streak", HEALTH_DEGRADED_ENTER_STREAK))
            if (not self._health_degraded_mode) and self._health_warn_streak >= _enter_thresh:
                # 09:00~09:10 장 시작 초기: ERR-FATAL·파이프라인 버스트로 인한
                # 구조적 지연이 warn_streak을 쌓아 섣불리 Degraded Mode에 진입하지 않도록 유예.
                _now_t = datetime.datetime.now().time()
                _open_warmup = datetime.time(9, 0) <= _now_t < datetime.time(9, 10)
                if _open_warmup:
                    log_manager.system(
                        "[HealthPolicy] Degraded Mode 진입 유예 — 장 시작 초기 (09:10 전) "
                        f"warn_streak={self._health_warn_streak:.2f}",
                        "WARNING",
                    )
                else:
                    self._health_degraded_mode = True
                    log_manager.system(
                        "[HealthPolicy] 자동 Degraded Mode 진입 "
                        f"(warn_streak={self._health_warn_streak:.2f}, warn_ratio={warn_ratio:.0%}, window={len(history)}분)",
                        "WARNING",
                    )
        else:
            self._health_warn_streak = 0
            self._health_info_streak += 1
            if self._health_degraded_mode:
                exit_ratio = float(p.get("degraded_exit_ratio", HEALTH_DEGRADED_EXIT_RATIO))
                if warn_ratio < exit_ratio:
                    self._health_degraded_mode = False
                    log_manager.system(
                        "[HealthPolicy] 자동 Degraded Mode 해제 "
                        f"(warn_ratio={warn_ratio:.0%} < {exit_ratio:.0%}, window={len(history)}분)",
                        "INFO",
                    )

    # ── 비동기 DB write 워커 ─────────────────────────────────────
    def _db_write_worker(self) -> None:
        """STEP 4에서 큐에 넣은 candle/feature/horizon 쓰기를 백그라운드 처리.

        파이프라인 타이밍 윈도우(_pipe_t0 ~ end)에서 SQLite I/O를 분리해
        WAL 체크포인트·디스크 경합이 파이프라인 지연으로 이어지지 않게 한다.

        None 센티넬을 받으면 종료 (daily_close 이후 정리용).
        """
        while True:
            item = self._db_write_queue.get()
            if item is None:
                self._db_write_queue.task_done()
                break
            try:
                op = item[0]
                if op == "candle_features":
                    _, _bar, _ts, _feats = item
                    save_candle_and_features(_bar, _ts, _feats)
                elif op == "horizon_features":
                    _, _ts, _h_name, _h_feats = item
                    save_horizon_features(_ts, _h_name, _h_feats)
                elif op == "scaler_monitor":
                    # predict_proba()가 위임한 scaler_events 행 INSERT
                    # WAL 모드 + 배경 스레드 → main pipeline 블로킹 없음
                    _, _sm_rows = item
                    if _sm_rows:
                        from model.scaler_monitor_db import insert_events_batch as _smib
                        _smib(_sm_rows)
            except Exception as _dq_e:
                logger.warning("[DBQueue] 쓰기 실패 (op=%s): %s", item[0] if item else "?", _dq_e)
            finally:
                self._db_write_queue.task_done()

    def _is_const_out_heavy_cooldown_active(self, now_dt: datetime.datetime = None) -> bool:
        until = getattr(self, "_const_out_heavy_cooldown_until", None)
        if until is None:
            return False
        now_dt = now_dt or datetime.datetime.now()
        return now_dt < until

    def _start_const_out_heavy_cooldown(self, now_dt: datetime.datetime, reason: str) -> None:
        seconds = float(self._health_policy.get("const_out_heavy_cooldown_sec", 180.0))
        self._const_out_heavy_cooldown_until = now_dt + datetime.timedelta(seconds=seconds)
        logger.info(
            "[ConstOut] heavy cooldown armed until %s (%s)",
            self._const_out_heavy_cooldown_until.strftime("%H:%M:%S"),
            reason,
        )

    def _on_const_out_refit_done(self, hz: list) -> None:
        """ConstOut scaler 재적합 완료 후 메인 스레드에서 실행되는 콜백.

        1) acc30m 버퍼 리셋 — 노후 스케일러 기반 예측은 무효
        2) GBM 재학습 예약 — scaler만 재적합해도 GBM 트리 구조 미변경 시 ConstOut 재발
        """
        # (1) acc30m 버퍼 리셋
        self.circuit_breaker.reset_acc30m_buffer()
        log_manager.system(
            f"[ConstOut] {hz} 재적합 완료 → acc30m 버퍼 리셋",
            "INFO",
        )
        # (2) GBM 재학습 예약 — 상호 잠금: 이미 재학습 중이면 skip
        if self._gbm_retrain_running:
            log_manager.system(
                f"[ConstOut] GBM 재학습 진행 중 — 재학습 예약 skip (hz={hz})",
                "INFO",
            )
            return
        log_manager.system(
            f"[ConstOut] {hz} → GBM 재학습 예약 (scaler 재적합 후 트리 구조 갱신 필요)",
            "INFO",
        )
        self._start_manual_retrain(force=True, reason=f"const_out={hz}")

    def _is_degraded_entry_blocked(self, confidence: float, is_manual: bool) -> tuple:
        """현재 Degraded 정책 기준으로 진입 차단 여부를 반환한다."""
        p = self._health_policy
        if not self._health_degraded_mode:
            return False, 0.0
        min_conf = float(p.get("degraded_min_conf", HEALTH_DEGRADED_MIN_CONF))
        if is_manual:
            enabled = bool(p.get("degraded_block_manual_entry", HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY))
        else:
            enabled = bool(p.get("degraded_block_auto_entry", HEALTH_DEGRADED_BLOCK_AUTO_ENTRY))
        return bool(enabled and confidence < min_conf), min_conf

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
        except Exception as _acc_e:
            logger.debug("[Account] get_selected_account 실패: %s", _acc_e)
            selected = ""
        if selected:
            account_no = selected
        try:
            accounts = [str(x).strip() for x in (self.broker.get_account_list() or []) if str(x).strip()]
        except Exception as _acl_e:
            logger.debug("[Account] get_account_list 실패: %s", _acl_e)
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

    def _load_state_persist_flag(self) -> bool:
        """ui_prefs.json에서 state_persist_enabled 플래그를 읽는다. 기본 True."""
        try:
            prefs_path = os.path.join(BASE_DIR, "data", "ui_prefs.json")
            if os.path.exists(prefs_path):
                with open(prefs_path, "r", encoding="utf-8") as f:
                    return bool(json.load(f).get("state_persist_enabled", True))
        except Exception:
            pass
        return True

    def _write_session_state(self, data: dict) -> None:
        state_path = self._session_state_path()
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        # P0: state_persist_enabled 시 ProfitGuard + CircuitBreaker 상태 추가 저장
        if getattr(self, "_state_persist_enabled", True):
            try:
                data["profit_guard_state"]    = self.profit_guard.to_state_dict()
                data["circuit_breaker_state"] = self.circuit_breaker.to_state_dict()
            except Exception as _se:
                logger.debug("[SessionState] PG/CB 상태 직렬화 실패: %s", _se)
        else:
            data.pop("profit_guard_state", None)
            data.pop("circuit_breaker_state", None)
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
        confidence = float(ctx.get("confidence", 0.0) or 0.0)
        p = self._health_policy
        manual_blocked, min_conf = self._is_degraded_entry_blocked(confidence, is_manual=True)
        if manual_blocked:
            notify(f"수동 진입 차단: Degraded Mode 최소신뢰도 {min_conf:.1%} 미달", "WARNING")
            log_manager.signal(
                f"[차단] 수동진입 Degraded 정책 차단 — conf={confidence:.1%} < {min_conf:.1%}"
            )
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

    def _on_layer2_gate_ui_toggled(self, enabled: bool) -> None:
        """Layer 2 Intraday Gate UI 토글 — ON 시 DAY_RISK_OFF/CRASH 규칙 적용, OFF 시 무시."""
        log_manager.system(
            f"[IntradayRegime] Layer 2 Gate UI={'ON' if enabled else 'OFF (우회 모드)'}",
            "INFO" if enabled else "WARNING",
        )

    def _on_max_qty_changed(self, max_qty: int) -> None:
        """최대허용수량 변경 — 대시보드 ▲▼ 버튼 클릭 시 호출."""
        self._max_entry_qty = max(1, int(max_qty))
        log_manager.system(f"[Sizer] 최대허용수량 변경: {self._max_entry_qty}계약")

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
            # CB HALT 상태에서는 pending을 강제 소멸 후 청산 진행
            # — stuck pending 때문에 운영자가 수동 청산조차 불가능한 상태 방지
            if self.circuit_breaker.state == CB_STATE_HALTED:
                log_manager.system(
                    "[ManualExit] CB HALT 상태 — stuck pending 강제 소멸 후 수동 청산 진행",
                    "WARNING",
                )
                self._clear_pending_order()
            else:
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
        stage = self.position.resolve_stage_for_exit_qty(send_qty, full_close=is_full_close)
        if is_full_close:
            reason = "수동 전량청산" if percent >= 100 else f"수동 청산 {percent}%→전량"
            kind = "EXIT_FULL"
        else:
            reason = f"수동 부분청산 {percent}%"
            kind = "EXIT_MANUAL_PARTIAL"

        # BlockRequest() 내부 메시지 펌프로 체결 콜백이 먼저 도착하는 race condition 방지:
        # pending을 주문 전송 전에 먼저 등록하고, 실패 시 롤백
        self._set_pending_order(
            kind=kind,
            direction=self.position.status,
            qty=send_qty,
            price_hint=round(price_hint, 2),
            reason=reason,
            stage=stage or None,
        )
        ret = self._send_broker_exit_order(send_qty)
        if ret != 0:
            self._clear_pending_order()
            log_manager.system(
                f"[ManualExit] 주문 실패 ret={ret} pct={percent} qty={send_qty}",
                "ERROR",
            )
            return

        log_manager.system(
            f"[ManualExit] 요청 pct={percent} send_qty={send_qty} kind={kind} stage={stage} position={self.position.status}",
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
            pt_value=self._pt_value,
        )
        forward_metrics = normalize_trade_pnl(
            entry_price=result["entry_price"],
            quantity=result["quantity"],
            pnl_pts=result.get("forward_pnl_pts", result["pnl_pts"]),
            pt_value=self._pt_value,
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
                formula_version, exit_reason, grade, regime,
                meta_action, hurst_bucket, hour_bucket,
                was_restart_after, had_partial_fill)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                       ?, ?, ?, ?, ?)""",
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
                getattr(self, "_entry_meta_action",  ""),
                getattr(self, "_entry_hurst_bucket", ""),
                getattr(self, "_entry_hour_bucket",  0),
                getattr(self, "_entry_was_restart",  0),
                getattr(self, "_entry_had_partial",  0),
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

    def _on_core_feature_fail(self, feature_name: str, streak: int) -> None:
        """CORE 피처(CVD/VWAP/OFI) 연속 실패 시 호출 — Slack 알림 + CB 진입 차단 여부 판단."""
        from utils.notify import notify
        notify(
            f"[CORE 경보] {feature_name} {streak}회 연속 실패",
            f"STEP 4 피처 계산 불능 — 기본값(0) 대체 중. 모델 신호 품질 저하.",
            level="ERROR",
        )

    def _clear_pending_order(self) -> None:
        _cleared_kind = str((self._pending_order or {}).get("kind") or "")
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
        # 완료된 주문번호를 보관 → 중복 chejan 콜백이 _ts_handle_external_fill 오호출하는 것을 방지
        _done_no = str((self._pending_order or {}).get("order_no") or "").strip()
        if _done_no:
            if not hasattr(self, "_completed_order_nos"):
                self._completed_order_nos = []
            self._completed_order_nos.append(_done_no)
            if len(self._completed_order_nos) > 20:
                self._completed_order_nos.pop(0)
        self._pending_order = None
        try:
            _ts_push_exit_panel_now(self)
        except Exception as _ep_e:
            logger.debug("[ExitPanel] push 실패 (UI 무시): %s", _ep_e)
        # EXIT_PARTIAL 해소 후 잔여 TP 즉시 재점검 (다음 분봉 대기 없이)
        # _cleared_kind가 ENTRY/EXIT_FULL이면 추가 TP 점검 불필요
        if _cleared_kind in ("EXIT_PARTIAL", "EXIT_MANUAL_PARTIAL") and self.position.status != "FLAT":
            _price = float(getattr(self, "_last_pipeline_price", 0.0) or self.position.entry_price or 0.0)
            if _price > 0:
                logger.warning(
                    "[IntrabarTPSchedule] EXIT_PARTIAL 해소 → 300ms 후 TP 재점검 스케줄 price=%.2f pos=%s "
                    "p1=%s p2=%s p3=%s",
                    _price, self.position.status,
                    self.position.partial_1_done,
                    self.position.partial_2_done,
                    self.position.partial_3_done,
                )
                QTimer.singleShot(300, lambda p=_price: _ts_intrabar_tp_check(self, p))
            else:
                logger.warning(
                    "[IntrabarTPSchedule] price=0 → 스케줄 취소 (entry_price=%.2f)",
                    self.position.entry_price or 0.0,
                )

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

        entry_time_hint = self.position.entry_time or self.position.peek_saved_entry_time(side)
        self.position.sync_from_broker(
            direction=side,
            price=avg_price,
            quantity=qty,
            atr=max(_ts_get_reference_atr(self), 0.5),
            synced_at=entry_time_hint,
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

    def _preload_horizon_calibration(self) -> None:
        """기동 시 DB 검증 예측(최근 3000건/호라이즌)으로 calibrator를 사전 fit.

        이 호출 없이는 calibrator가 fit=False 상태로 시작하여
        첫 ~100건은 raw prob이 그대로 통과(과신 억제 효과 없음).
        """
        from utils.db_utils import fetchall
        from config.settings import PREDICTIONS_DB as _PRED_DB
        try:
            rows = fetchall(
                _PRED_DB,
                """SELECT horizon, confidence, correct
                   FROM predictions
                   WHERE actual IS NOT NULL
                   ORDER BY ts DESC
                   LIMIT 18000""",   # 호라이즌 6개 × 최대 3000건
            )
            for row in rows:
                self.horizon_calibrator.record(
                    str(row["horizon"]),
                    float(row["confidence"] or 0.0),
                    bool(int(row["correct"] or 0)),
                )
            self.horizon_calibrator.fit_all()
            logger.info("[Calib] 기동 사전 학습 완료: %d건", len(rows))
        except Exception as exc:
            logger.warning("[Calib] 기동 사전 학습 실패 (보정 비활성): %s", exc)

    def _recalibrate_mc(self, trigger: str = "RETRAIN") -> None:
        """
        동적 min_conf 재보정.
        최근 MC_LOOKBACK_DAYS 거래일의 앙상블 conf 분포를 측정하고
        _ZONE_PARAMS의 min_confidence를 런타임 업데이트.
        mc_history.db에 이력 저장.
        """
        from utils.db_utils import fetchall
        from config.settings import PREDICTIONS_DB as _PDBP, MC_LOOKBACK_DAYS
        try:
            rows = fetchall(
                _PDBP,
                """SELECT confidence FROM ensemble_decisions
                   WHERE substr(ts,1,10) >= date('now',?)
                   AND confidence IS NOT NULL""",
                ("-%d days" % (MC_LOOKBACK_DAYS * 2),),   # 거래일 환산 여유
            )
            confs = [float(r["confidence"]) for r in rows if r["confidence"]]
            if not confs:
                logger.warning("[DynMC] conf 데이터 없음 — 갱신 스킵")
                return
            base = update_dynamic_mc(confs, trigger=trigger, record=True)
            if base is not None:
                log_manager.system(
                    f"[DynMC] mc 재보정 완료 trigger={trigger}  base={base:.3f}"
                    f"  (n={len(confs)}봉)", "INFO"
                )
                # 대시보드 패널 갱신
                try:
                    if getattr(self, "dashboard", None):
                        _panel = getattr(self.dashboard, "dynamic_mc_panel", None)
                        if _panel and hasattr(_panel, "refresh"):
                            _panel.refresh()
                except Exception:
                    pass
        except Exception as exc:
            logger.warning("[DynMC] _recalibrate_mc 실패: %s", exc)

    def _apply_horizon_calibration(self, horizon_proba: dict) -> dict:
        calibrated = {}
        for horizon, probs in horizon_proba.items():
            res = dict(probs)
            direction = int(res.get("direction", 0))
            raw_conf = float(res.get("confidence", 1 / 3) or 1 / 3)
            # 보정 후에도 과신 방지 — calibrator가 1.0 반환 가능하므로 재클립
            _calibrated_raw = self.horizon_calibrator.calibrate(horizon, raw_conf)
            # 10m/15m: Platt 과도 압축 방지 — raw_conf의 85% 이상 보장
            # 이유: balanced class_weight 구조상 GBM 내부 확률이 낮게 출력되고
            #       과거 평균 성능 기반 Platt가 현재 시장 컨디션을 과소평가하는 현상 완화
            if horizon in ("10m", "15m"):
                _floor = raw_conf * 0.85
                if _calibrated_raw < _floor:
                    logger.debug("[Calib] %s Platt 하한 %.3f→%.3f", horizon, _calibrated_raw, _floor)
                    _calibrated_raw = _floor
            cal_conf = float(np.clip(_calibrated_raw, 0.0, 0.85))
            if _calibrated_raw > 0.85:
                logger.debug("[Calib] %s clipped %.3f→0.85", horizon, _calibrated_raw)

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

    # [SERVICE-BOUNDARY 1/4] BrokerRuntimeService
    # 책임: 로그인/계좌선택/종목결정/실시간+수급 타이머 시작
    # 입력: secrets 계좌, 대시보드 종목 선택값, broker capability
    # 출력: _futures_code, realtime_data, investor timer, startup sync 상태
    def connect_broker(self) -> bool:
        """로그인 + 근월물 실시간 수신 등록."""
        runtime_ctx = self.broker_runtime_service.login_and_prepare(self)
        if runtime_ctx is None:
            return False
        selected_account = runtime_ctx.selected_account
        code = runtime_ctx.code

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
        self._warmup_retrain_pending = True
        log_manager.system("[WarmupRetrain] 세션 재시작 감지 → GBM 즉시 재학습 예약", "INFO")
        self._session_no += 1
        self.system_health.update_restart(self._session_no)
        _cause = self._restart_cause
        _unintended = _cause == "AUTO_DISCONNECT"
        log_manager.system(
            f"[Session] 재기동 #{self._session_no} | cause={_cause}"
            + (" ← 의도치 않은 재기동" if _unintended else ""),
            "WARNING" if _unintended else "INFO",
        )
        self._restart_cause = "MANUAL"   # 다음 재기동 기본값 복원

        # 장중(09:00~15:10) 재시작: pre_market_setup()이 재호출되지 않으므로 즉시 시작.
        # 그렇지 않으면 첫 분봉 STEP 3에서 시작되어 파이프라인과 CPU 경합 → CB⑤ 5026ms 발동.
        # [P0] 당일 08:50 이후 이미 재학습 완료된 경우 장중 재학습 중복 차단.
        #      단, 마지막 재학습으로부터 _RESTART_RETRAIN_GAP_MIN 이상 경과 시 재학습 허용.
        #      근거: 12:18 재시작에서 11:10 재학습 완료 이유로 스킵 → 오후 방향 전환 무감지.
        #      오전/오후 시장 방향이 달라지는 경우 60분+ 경과 후 재시작 시 재학습이 필요.
        # [P0-Gate] 14:30 이후 재시작: 장 마감 40분 전 — 재학습해도 실사용 시간 없음 → 스킵.
        _RESTART_RETRAIN_GAP_MIN = 60   # 마지막 재학습으로부터 이 시간(분) 경과 시 재학습 허용
        _rst_now = datetime.datetime.now()
        _today_0850 = _rst_now.replace(hour=8, minute=50, second=0, microsecond=0)
        _last_rt = getattr(self.batch_retrainer, "_last_retrain", None)
        _mins_since_last_rt = (
            (_rst_now - _last_rt).total_seconds() / 60 if _last_rt else float("inf")
        )
        _already_retrained_today = (
            _last_rt is not None
            and _last_rt.date() == _rst_now.date()
            and _last_rt >= _today_0850
            and _mins_since_last_rt < _RESTART_RETRAIN_GAP_MIN   # 60분 이내 재학습은 스킵
        )
        _late_restart = _rst_now.time() >= datetime.time(14, 30)   # 14:30 이후 재학습 무의미
        if (
            datetime.time(9, 0) <= _rst_now.time() < datetime.time(15, 10)
            and not self._gbm_retrain_running
            and not _already_retrained_today
            and not _late_restart
        ):
            self._warmup_retrain_pending = False
            self._gbm_retrain_running = True
            self._gbm_retrain_started_at = datetime.datetime.now()  # P1-B: 타임아웃 추적
            self._gbm_retrain_done_event.clear()
            self.circuit_breaker.set_gbm_retrain_active(True)   # CB⑤ 임계 완화
            self.dashboard.set_model_status("GBM 장중 재학습중...")
            _rt_gap_tag = (
                f" ({_mins_since_last_rt:.0f}분 경과, {_last_rt.strftime('%H:%M')} 이후)"
                if _last_rt else ""
            )
            log_manager.system(
                f"[WarmupRetrain] 장중 재시작 — GBM 경량 재학습 시작{_rt_gap_tag} (intraday)", "INFO"
            )

            def _intraday_retrain_worker():
                result = {"ok": False, "error": "unknown"}
                try:
                    result = self.batch_retrainer.retrain_now(force=False, intraday=True)
                except BaseException as _re:  # MemoryError 등 BaseException 포함
                    result = {"ok": False, "error": str(_re)}
                # P1-A 강화: BaseException(MemoryError 포함) 무관 항상 해제
                self._gbm_retrain_running = False
                self._gbm_retrain_done_event.set()   # worker 스레드에서 직접 해제 (QTimer 전달 불안정 대비)
                QTimer.singleShot(0, lambda r=result: self._on_gbm_retrain_done(r, True))

            threading.Thread(target=_intraday_retrain_worker, daemon=True).start()
        elif _late_restart and not _already_retrained_today:
            self._warmup_retrain_pending = False
            log_manager.system(
                f"[WarmupRetrain] 14:30 이후 재시작 → 재학습 스킵 (잔여시간 {(datetime.time(15, 10).hour*60+10) - (_rst_now.hour*60+_rst_now.minute)}분)",
                "INFO",
            )
        elif _already_retrained_today:
            self._warmup_retrain_pending = False
            log_manager.system(
                f"[WarmupRetrain] 최근 재학습({_last_rt.strftime('%H:%M')}, {_mins_since_last_rt:.0f}분 전) → 장중 재학습 스킵",
                "INFO",
            )

        if self.position.status != "FLAT":
            self.dashboard.set_ui_position_mode()
        else:
            self.dashboard.set_ui_ready_mode()

        self.broker_runtime_service.start_realtime_and_investor(
            self,
            code=code,
            market_open_now=runtime_ctx.market_open_now,
        )
        self.option_chain_snap.initialize()
        return True

    def connect_kiwoom(self) -> bool:
        return self.connect_broker()

    def _fetch_investor_data(self) -> None:
        """수급 TR 수집 — QTimer에서 호출 (COM 콜백 체인 외부)."""
        if not is_market_open(datetime.datetime.now()):
            return
        try:
            self.investor_data.fetch_all(include_program=False)
            # FutureCurOnly 틱에서 실시간으로 수집된 미결제약정 동기화
            rt = getattr(self, "realtime_data", None)
            if rt is not None:
                oi = getattr(rt, "_last_oi", 0)
                if oi > 0:
                    self.investor_data._open_interest = oi
        except Exception as e:
            apply_error_policy(
                system=self,
                level=ErrorLevel.DEGRADED,
                context="investor_timer_fetch",
                exc=e,
                logger=logger,
                dashboard_logger=log_manager.system,
            )

    def _poll_option_chain(self) -> None:
        """옵션 체인 5분 폴링 — QTimer 콜백 (메인 스레드, COM 안전).
        파이프라인 STEP 4 에서 BlockRequest 루프를 제거하고 이쪽으로 이전했다.
        """
        if not is_market_open(datetime.datetime.now()):
            return
        spot = self._last_close
        try:
            refreshed = self.option_chain_snap.refresh(spot=spot)
            if refreshed and self.dashboard:
                self.dashboard.update_option_chain(self.option_chain_snap.get_features())
        except Exception as _e:
            logger.warning("[OptionChain] 폴링 오류: %s", _e)

    def _on_tick_price_update(self, bar: dict) -> None:
        """틱 수신마다 대시보드 헤더 현재가 갱신."""
        if self.realtime_data is None:
            return
        close = float(bar.get("close", 0) or 0.0)
        logger.info(
            "[TickUI] begin code=%s close=%.2f ts=%s",
            self.realtime_data.code,
            close,
            bar.get("ts"),
        )
        if close > 0:
            self._last_pipeline_price = close
            logger.info("[TickUI] minute_chart_tick code=%s close=%.2f", self.realtime_data.code, close)
            self.dashboard.minute_chart_tick(close, bar.get("ts"))
        logger.info("[TickUI] update_price code=%s close=%.2f", self.realtime_data.code, float(bar["close"]))
        self.dashboard.update_price(
            price  = bar["close"],
            change = bar["close"] - bar.get("open", bar["close"]),
            code   = self.realtime_data.code,
        )
        logger.info("[TickUI] end code=%s close=%.2f", self.realtime_data.code, float(bar["close"]))

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

    def _on_pre_market_bar(self, candle: dict) -> None:
        """프리장 분봉 처리 (08:45~09:00) — 진입 없이 warmup만.

        목적:
          ① GapOffset 사전 설정 (첫 분봉 close 기준) — 본장 z경고 원천 차단
          ② 프리장 실데이터로 scaler 재적합 (PRE_MARKET_REFIT_MIN_BARS봉 후)
          ③ z경고 점진적 해소 → 09:00 EKS 발동 방지
          ④ 프리장 conf 히스토리 수집 → EKS GAP_OPEN 판정 보완용
        """
        from config.settings import PRE_MARKET_REFIT_MIN_BARS, SCALER_WARMUP_LOOKBACK_BARS

        now_dt = datetime.datetime.now()
        self._pre_market_bars.append(candle)
        n_bars = len(self._pre_market_bars)

        # ① GapOffset 사전 설정 — 첫 프리장 분봉의 close를 기준으로 갭 오프셋 산정
        # 본장 첫 분봉(09:00)보다 최대 15분 선행 → z경고 원천 억제
        if not self._pre_market_gap_offset_set:
            _pre_close = float(candle.get("close", 0.0) or 0.0)
            if _pre_close > 0:
                try:
                    self.model.set_daily_gap_offset(_pre_close)
                    self._pre_market_gap_offset_set = True
                    _lead_min = int(
                        (datetime.time(9, 0).hour * 60)
                        - (now_dt.hour * 60 + now_dt.minute)
                    )
                    log_manager.system(
                        f"[PreMarket] GapOffset 사전 설정 close={_pre_close:.2f}"
                        f" (본장 {_lead_min}분 선행)",
                        "INFO",
                    )
                    # session_state에도 저장 — 장중 재시작 시 복원용
                    try:
                        _pm_ss = self._read_session_state()
                        _pm_ss["today_open"] = _pre_close
                        self._write_session_state(_pm_ss)
                    except Exception:
                        pass
                except Exception as _goe:
                    logger.warning("[PreMarket] GapOffset 설정 실패: %s", _goe)

        # ② PRE_MARKET_REFIT_MIN_BARS봉 누적 후 scaler 재적합
        # EarlyWarmup(전날 데이터)과 달리 오늘 갭오픈 분포를 직접 반영
        if (
            n_bars >= PRE_MARKET_REFIT_MIN_BARS
            and not self._pre_market_scaler_refitted
            and not getattr(self, "_scaler_refresh_running", False)
        ):
            _z_now = self._canary_load_z_warn(n_rows=min(n_bars, 10))
            if _z_now >= 5:   # 실제 이상 임계 (Canary의 완화된 12개와 구분)
                self._scaler_refresh_running = True
                self._pre_market_scaler_refitted = True
                log_manager.system(
                    f"[PreMarket] {n_bars}봉 z경고={_z_now}개 → scaler refit 시작"
                    f" (프리장 실데이터 기반)",
                    "WARNING",
                )
                def _pm_refit_worker(_nb=n_bars):
                    try:
                        _Xpm, _fnpm = self.batch_retrainer.load_features_for_warmup(
                            lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
                        )
                        if _Xpm is not None:
                            self.model.refit_scalers_only(
                                _Xpm, _fnpm,
                                trigger_type="A_WARMUP",
                                trigger_reason=f"pre_market_{_nb}bars",
                            )
                            log_manager.system(
                                f"[PreMarket] refit 완료 n={len(_Xpm)}봉", "INFO"
                            )
                        else:
                            log_manager.system("[PreMarket] refit 스킵 — 데이터 없음", "WARNING")
                    except Exception as _pme:
                        logger.warning("[PreMarket] refit 실패: %s", _pme)
                    finally:
                        self._scaler_refresh_running = False
                threading.Thread(target=_pm_refit_worker, daemon=True).start()
            else:
                # z경고 정상 범위 → refit 불필요, 완료로 표시해 ScalerWarmup 스킵 유도
                self._pre_market_scaler_refitted = True
                log_manager.system(
                    f"[PreMarket] {n_bars}봉 z경고={_z_now}개 — 정상 범위, refit 스킵",
                    "INFO",
                )

        # ③④ 모델이 준비됐으면 예측 → conf 히스토리 수집
        if self.model.is_ready():
            try:
                _pm_feats = self.feature_builder.build(
                    candle,
                    supply_demand={},
                    macro_data={},
                    option_data={},
                    micro_regime=self.current_micro_regime,
                )
                _pm_proba = self.model.predict_proba(_pm_feats)
                # conf = 가장 강한 방향 확률의 중립(0.5) 대비 편차
                _pm_conf = 0.0
                if _pm_proba:
                    _pm_conf = max(
                        abs(float(v) - 0.5) * 2
                        for v in _pm_proba.values()
                        if isinstance(v, float)
                    )
                self._pre_market_conf_history.append(_pm_conf)
                # SHS z경고 최신화
                _z_update = self._canary_load_z_warn(n_rows=min(n_bars, 10))
                self.system_health.update_z_warn(_z_update)
                log_manager.system(
                    f"[PreMarket] {now_dt.strftime('%H:%M')} "
                    f"n={n_bars}봉 conf={_pm_conf:.1%} z경고={_z_update}개",
                    "INFO",
                )
            except Exception as _pme2:
                logger.debug("[PreMarket] 예측 스킵: %s", _pme2)

        # 대시보드 차트 갱신 (선택적)
        try:
            self.dashboard.minute_chart_candle_closed(candle)
        except Exception:
            pass

    def _on_candle_closed(self, candle: dict) -> None:
        """분봉 완성 콜백 — Qt 이벤트 스레드에서 호출됨."""
        now = datetime.datetime.now()

        # ── 프리장 처리 경로 (08:45~09:00) ──────────────────────────
        # 진입 없이 scaler warmup · 피처 검증 · GapOffset 사전 설정만 수행
        if is_pre_market(now):
            self._on_pre_market_bar(candle)
            return

        if not is_market_open(now):
            return
        # 15:10 강제 청산 이후 예측 파이프라인 중단 (TimeRouter·앙상블 불필요 실행 방지)
        if is_force_exit_time(now):
            return

        self._last_recovery_ts = ""   # 실분봉 수신 시에만 복구 ts 초기화

        # ── 거래소 CB 해제 감지 ─────────────────────────────────────────
        # CB 대기 모드 중 분봉이 재수신되면 해제 후처리 실행
        if self._exchange_cb_mode:
            self._exchange_cb_mode = False
            _gap_min = int(
                (now - self._exchange_cb_start).total_seconds() / 60
            ) if self._exchange_cb_start else 0
            self._exchange_cb_start = None
            log_manager.system(
                f"[ExchangeCB] 거래소 CB 해제 — {_gap_min}분 공백 후 분봉 재개. "
                f"상태 초기화 시작",
                "INFO",
            )
            notify(f"▶ 미륵이 거래소 CB 해제 — {_gap_min}분 후 분봉 재개")
            self._post_exchange_cb_resume(_gap_min)

        # 09:00 이후 첫 분봉 수신 — 정상 작동 슬랙 알림 + 갭 오프셋 설정 (1회만)
        if not getattr(self, "_first_tick_notified", False):
            self._first_tick_notified = True
            notify_first_tick(candle)
            # 갭 오프셋: 프리장에서 이미 설정됐으면 스킵 (프리장 선행 설정 우선)
            # 프리장 미수신(장중 재시작 등)이면 첫 본장 분봉 기준으로 설정
            if not getattr(self, "_pre_market_gap_offset_set", False):
                try:
                    _today_open = float(candle.get("close", 0.0) or 0.0)
                    if _today_open > 0:
                        self.model.set_daily_gap_offset(_today_open)
                        try:
                            _gap_ss = self._read_session_state()
                            _gap_ss["today_open"] = _today_open
                            self._write_session_state(_gap_ss)
                        except Exception:
                            pass
                except Exception as _gap_exc:
                    logger.warning("[GapOffset] 오프셋 설정 실패: %s", _gap_exc)
            else:
                log_manager.system(
                    "[GapOffset] 프리장 사전 설정 확인 → 본장 첫 분봉 재설정 스킵", "INFO"
                )

        self.dashboard.minute_chart_candle_closed(candle)
        try:
            self.run_minute_pipeline(candle)
            self._pipeline_fatal_streak = 0
        except Exception as exc:
            # [P0] 피처↔스케일러 불일치 ValueError 연속 2회 → 자동 복구
            _is_feat_mismatch = (
                isinstance(exc, ValueError)
                and "features" in str(exc)
                and "expecting" in str(exc)
            )
            if _is_feat_mismatch:
                self._pipeline_fatal_streak += 1
                if self._pipeline_fatal_streak >= 2:
                    _bad = self.model.validate_and_resync()
                    if _bad:
                        log_manager.system(
                            f"[P0] 피처 불일치 {self._pipeline_fatal_streak}회 연속"
                            f" — 비활성화: {_bad} | 즉시 재학습 요청",
                            "ERROR",
                        )
                        self._start_manual_retrain(force=True, reason="feature_mismatch_P0")
                    self._pipeline_fatal_streak = 0
            else:
                self._pipeline_fatal_streak = 0

            apply_error_policy(
                system=self,
                level=classify_exception(exc, default=ErrorLevel.FATAL),
                context="minute_pipeline",
                exc=exc,
                logger=logger,
                dashboard_logger=log_manager.system,
            )

    def _on_gbm_retrain_done(self, result: dict, is_warmup: bool) -> None:
        """GBM 재학습 daemon thread 완료 콜백 — 메인 스레드에서 실행."""
        self._gbm_retrain_running = False
        self._gbm_retrain_started_at = None  # P1-B: 타임아웃 허위 경고 방지
        self._gbm_retrain_done_event.set()  # daily_close 대기 해제
        self.circuit_breaker.set_gbm_retrain_active(False)  # CB⑤ 임계 복원
        prefix = "웜업 " if is_warmup else ""
        if result.get("ok"):
            _bad = self.model._load_all()
            if _bad:
                logger.error(
                    "[Model] 재학습 후 %d개 호라이즌 차원 불일치: %s → 재학습 재트리거",
                    len(_bad), _bad,
                )
                self._start_manual_retrain(force=True, reason="resync_mismatch")
            # P6c: GBM 재학습 완료 시 RF도 최신 pkl 로드
            try:
                self.rf_model.load_all()
            except Exception:
                pass
            self._ensure_shap_tracker()
            registry = self._load_feature_registry()
            if registry.get("pending_change"):
                active = list(registry.get("active_features") or [])
                if active and active == list(self.model.feature_names or []):
                    registry["last_applied_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    registry["pending_change"] = {}
                    self._save_feature_registry(registry)

            # 동적 mc 재보정 — 주기 1: GBM 재학습 완료 즉시
            try:
                self._recalibrate_mc(trigger="RETRAIN")
            except Exception as _mc_e:
                logger.warning("[DynMC] 재학습 후 mc 재보정 실패: %s", _mc_e)

            # threshold 교체 후 SGD 1회 완전 리셋 (플래그가 True인 경우만 실행)
            from config import settings as _cfg_sgd
            if getattr(_cfg_sgd, "SGD_FULL_RESET_PENDING", False):
                self.online_learner.reset_full()
                _cfg_sgd.SGD_FULL_RESET_PENDING = False
                log_manager.learning("[SGD] threshold 교체 후 완전 리셋 완료 (1회)")

            # 방법3 레이블 기반 GBM 첫 재학습 완료 → 보수 진입 제한 해제
            if not self._pre_retrain_done:
                self._pre_retrain_done = True
                log_manager.system(
                    "[EntryGate] GBM 첫 재학습 완료(방법3 레이블) "
                    f"— 사이즈 제한 해제 (×{runtime_settings.PRE_RETRAIN_SIZE_MULT:.1f} → ×1.0)"
                )

            # 재학습 이력 영속화 — 재시동 후에도 마지막 재학습일·누적 횟수 복원
            # _write_session_state 대신 직접 merge-write로 profit_guard 직렬화와 격리
            try:
                _ss_path = self._session_state_path()
                _ss2 = self._read_session_state()
                _ss2["gbm_last_retrain"] = result.get("timestamp", "")
                _ss2["gbm_total_retrain_count"] = self.batch_retrainer._retrain_count
                with open(_ss_path, "w", encoding="utf-8") as _ssf:
                    json.dump(_ss2, _ssf, ensure_ascii=False)
                logger.info(
                    "[GBM] 재학습 이력 저장: %s (%d회)",
                    _ss2["gbm_last_retrain"], _ss2["gbm_total_retrain_count"],
                )
            except Exception as _pe:
                logger.warning("[GBM] 재학습 이력 저장 실패 (무해): %s", _pe)

            log_manager.learning(
                f"[GBM] {prefix}배치 재학습 완료 | "
                f"{result.get('elapsed_sec', '?')}초 데이터={result.get('data_size', '?')}행"
            )
            notify("GBM 배치 재학습 완료", "INFO")
            self.dashboard.set_model_status(
                f"GBM {prefix}재학습 완료", f"데이터 {result.get('data_size', '?')}행"
            )
            # ATR 동적 threshold 갱신 제거 (P2) — rolling σ×k 방법3이 매분 갱신
            self._reset_rollback_active = None
        else:
            log_manager.learning(f"[GBM] {prefix}재학습 건너뜀: {result.get('error', '')}")
            self.dashboard.set_model_status("대기")
            rollback = getattr(self, "_reset_rollback_active", None)
            if rollback:
                registry = self._load_feature_registry()
                registry["active_features"] = rollback
                registry.pop("pending_change", None)
                self._save_feature_registry(registry)
                log_manager.system(
                    "[FeatureOps] 재학습 실패 — active_features 롤백 (%d개 복원)" % len(rollback),
                    "WARN",
                )
                self._reset_rollback_active = None
        # 재학습 완료(성공/실패 모두) 후 SHAP 패널 버튼 상태 갱신
        # 파이프라인이 멈춘 상태(장 마감 후 등)에서도 버튼 enabled 복원
        try:
            self._update_shap_dashboard()
        except Exception:
            pass

    # _log_threshold_monitor() — P2에서 제거 (91차)
    # rolling σ × k 방법3이 HORIZON_THRESHOLDS를 매분 갱신하므로 ATR 동적 불필요

    # ── 장 전 준비 (08:45) ─────────────────────────────────────
    def pre_market_setup(self):
        """1단계 (08:55): macro seed fetch + PreRetrain 시작.
        SP500·KRW chg는 첫 fetch에서 항상 0.0(설계된 동작)이므로
        레짐 확정은 _pre_market_stage2()에서 2회차 fetch(08:58) 후 실행한다."""
        logger.info("[System] 장 전 매크로 수집 시작 (1단계 — seed fetch)")
        log_manager.system("장 전 매크로 수집 시작")

        # [MetaConf] 전일 학습 상태 복원 — cold-start 없이 장 시작부터 SGD 예측 경로 사용
        try:
            from config.settings import META_CONF_STATE_PATH
            _mc_loaded = self.meta_gate.learner.load(META_CONF_STATE_PATH)
            if not _mc_loaded:
                log_manager.system("[MetaConf] warm-start 파일 없음 — cold-start로 진행", "INFO")
        except Exception as _mc_l_e:
            logger.warning("[MetaConf] warm-start 로드 실패 (cold-start 진행): %s", _mc_l_e)

        # 첫 fetch: prev 시드 저장 전용. SP500·KRW chg = 0.0 (MacroFetcher 설계)
        self.macro_fetcher.get_features()
        logger.info("[System] 매크로 seed fetch 완료 — 레짐 확정은 08:58 2단계로 연기")

        # [PreOpen-이상점2] 장 시작 전 현재가 스냅샷 사전 조회 — realtime.start() 시 BlockRequest 병목 방지
        # start() 내부에서 _last_price > 0 이면 _prime_from_snapshot 재실행 스킵
        _rd = getattr(self, "realtime_data", None)
        if _rd is not None and not getattr(_rd, "_running", False):
            try:
                _rd._prime_from_snapshot()
                log_manager.system(
                    "[PreOpen] 현재가 스냅샷 워밍업 완료 "
                    f"(price={_rd._last_price:.2f} bid={_rd._last_bid1:.2f} ask={_rd._last_ask1:.2f})",
                    "INFO",
                )
            except Exception as _snap_e:
                logger.warning("[PreOpen] 스냅샷 워밍업 실패 (장 시작 시 재시도): %s", _snap_e)

        # ── Warm Scaler Canary ──────────────────────────────────────
        # scaler pkl mtime 기준 노후 점검 → 24h+ 경과 시 경고 + SHS z_warn 업데이트
        _canary_stale = False   # [P2] warmup 대기 조건 참조를 위해 try 블록 밖에서 초기화
        try:
            _canary_age_h = self.model.canary_stale_age_hours()
            _canary_z_warn = 0
            if self.model.feature_names:
                _canary_z_warn = self._canary_load_z_warn(n_rows=60)
            _canary_stale = _canary_age_h > 24.0
            # EarlyWarmup 완료 직후는 전날 데이터 기준 scaler라 장전 피처 분포와 괴리 발생.
            # 임계를 12개로 완화하여 허위 z경고 알림 억제 (실제 이상은 5개 기준 유지).
            _z_bad_thresh = 12 if getattr(self, "_early_warmup_started", False) else 5
            _canary_z_bad = _canary_z_warn >= _z_bad_thresh
            _ew_tag = f" (EarlyWarmup 완료 — 임계 {_z_bad_thresh}개)" if getattr(self, "_early_warmup_started", False) else ""
            log_manager.system(
                f"[Canary] scaler 노후={_canary_age_h:.0f}h  z경고피처={_canary_z_warn}개{_ew_tag}"
                + ("  ⚠ 스케일러 24h+ 노후" if _canary_stale else "")
                + ("  ⚠ z경고 폭증" if _canary_z_bad else ""),
                "WARNING" if (_canary_stale or _canary_z_bad) else "INFO",
            )
            if _canary_stale or _canary_z_bad:
                from utils.notify import notify as _ncanary
                _ncanary(
                    f"🌡 Canary 이상 감지\n"
                    f"scaler 노후: {_canary_age_h:.0f}시간  z경고 피처: {_canary_z_warn}개\n"
                    f"PreRetrain으로 갱신 예정 — 09:00 전 완료 목표",
                    "WARNING",
                )
            # [P1] z경고 폭증 시 08:58 전 즉시 재적합 — EarlyWarmup 이후 갭오픈 분포 갱신
            # EarlyWarmup은 전날 데이터 기준이라 오늘 갭오픈 이후 분포와 괴리가 생김.
            # 08:58 전에 한 번 더 재적합해 GAP_OPEN 분봉의 conf 신뢰성을 높임.
            # [P0] _scaler_refresh_running 선점 — ScalerWarmup과 상호 배제 (race condition 방지)
            if _canary_z_bad:
                _p1_now_t = datetime.datetime.now().time()
                if _p1_now_t < datetime.time(8, 58):
                    if not getattr(self, "_scaler_refresh_running", False):
                        self._scaler_refresh_running = True
                        log_manager.system(
                            f"[Canary] z경고 폭증({_canary_z_warn}개 ≥ {_z_bad_thresh}개)"
                            f" → 장전 scaler 재적합 시도 (08:58 전)",
                            "WARNING",
                        )
                        def _canary_refit_worker():
                            try:
                                from config.settings import SCALER_WARMUP_LOOKBACK_BARS
                                _Xcr, _fncr = self.batch_retrainer.load_features_for_warmup(
                                    lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
                                )
                                if _Xcr is not None:
                                    self.model.refit_scalers_only(_Xcr, _fncr)
                                    log_manager.system(
                                        f"[Canary] 장전 재적합 완료 n={len(_Xcr)}봉", "INFO"
                                    )
                                else:
                                    log_manager.system("[Canary] 장전 재적합 스킵 — 데이터 없음", "WARNING")
                            except Exception as _e:
                                logger.warning("[Canary] 장전 재적합 실패: %s", _e)
                            finally:
                                self._scaler_refresh_running = False
                        threading.Thread(target=_canary_refit_worker, daemon=True).start()
                    else:
                        log_manager.system(
                            f"[Canary] z경고 폭증({_canary_z_warn}개) — refit 스킵: 다른 refit 진행 중",
                            "INFO",
                        )
            # [P3] EKS 원인 진단용 — 마지막 Canary z경고 수 인스턴스 변수로 보존
            self._last_canary_z_warn = _canary_z_warn
            self.system_health.update_z_warn(_canary_z_warn)
        except Exception as _ce:
            logger.warning("[Canary] 점검 실패 (무시): %s", _ce)

        # [ScalerWarmup] 08:55 스케일러 단독 워밍업.
        # [P8] _warmup_retrain_pending(예약됨)만으로는 스킵하지 않음.
        #       GBM 재학습이 이미 실행 중(_gbm_retrain_running)일 때만 스킵
        #       → GBM 완료 전에도 스케일러를 신선하게 유지 (오늘 641분 재발 방지).
        # [P2] _canary_stale=True 시 완료 이벤트 대기 — GAP_OPEN 전 신선도 보장.
        # EarlyWarmup·Canary refit·프리장 refit 실행 중(_scaler_refresh_running)이면 스킵.
        # [P0] 프리장 refit 이미 완료(_pre_market_scaler_refitted)이면 스킵 — 중복 refit 방지.
        _warmup_done_event = threading.Event()
        if getattr(self, "_pre_market_scaler_refitted", False):
            log_manager.system(
                "[ScalerWarmup] 프리장 refit 완료 확인 → 스킵 (중복 방지)", "INFO"
            )
            _warmup_done_event.set()
        elif (
            not getattr(self, "_gbm_retrain_running", False)
            and not getattr(self, "_scaler_refresh_running", False)
        ):
            self._scaler_refresh_running = True   # [P0] 스레드 시작 전 선점 — Canary refit과 상호 배제
            def _scaler_warmup_worker(_evt=_warmup_done_event):
                try:
                    from config.settings import SCALER_WARMUP_LOOKBACK_BARS
                    X_w, fn_w = self.batch_retrainer.load_features_for_warmup(
                        lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
                    )
                    if X_w is not None:
                        self.model.refit_scalers_only(X_w, fn_w)
                        log_manager.system(
                            f"[ScalerWarmup] 완료 n={len(X_w)}봉 — 스케일러 노후화 차단", "INFO"
                        )
                    else:
                        log_manager.system("[ScalerWarmup] 데이터 없음 — 워밍업 건너뜀", "WARNING")
                    # 동적 mc 재보정 — 주기 2: 08:55 워밍업 완료 직후
                    try:
                        self._recalibrate_mc(trigger="DAILY_WARMUP")
                    except Exception as _mc_e2:
                        logger.warning("[DynMC] 워밍업 후 mc 재보정 실패: %s", _mc_e2)
                    # [Platt] 앙상블 보정기 복원 — 재시동마다 100건 재누적 방지
                    try:
                        from config.settings import ENSEMBLE_CALIBRATOR_PATH
                        if self.ensemble.ensemble_calibrator.load(ENSEMBLE_CALIBRATOR_PATH):
                            log_manager.system(
                                f"[Calibration] 앙상블 보정기 복원 완료 "
                                f"n={self.ensemble.ensemble_calibrator.n_samples}",
                                "INFO",
                            )
                    except Exception as _cal_e:
                        logger.warning("[Calibration] 보정기 복원 실패 (무해): %s", _cal_e)
                except Exception as _sw_e:
                    logger.warning("[ScalerWarmup] 실패 (무해): %s", _sw_e)
                finally:
                    self._scaler_refresh_running = False   # [P0] 완료 시 해제
                    _evt.set()

            threading.Thread(target=_scaler_warmup_worker, daemon=True).start()
        else:
            _warmup_done_event.set()   # GBM 재학습 중 or refit 실행 중 → 스킵이므로 즉시 완료 표시

        # [P2] Canary stale(24h+)이면 최대 90초 동기 대기 — 08:55~09:00 사이 여유로 허용
        if _canary_stale:
            log_manager.system("[Canary] stale 감지 — warmup 완료 대기 시작 (최대 90초)", "WARNING")
            _warmup_done_event.wait(timeout=90)
            log_manager.system("[Canary] warmup 완료 대기 종료 — GAP_OPEN 진입", "INFO")

        # [PreRetrain] 08:55 GBM 사전 재학습 — 09:00 첫 파이프라인 CB⑤ 지연 방지.
        # warmup 플래그가 설정되어 있으면 여기서 바로 백그라운드 스레드 시작.
        # 재학습이 09:00 이전에 완료되면 STEP 3 에서 _gbm_retrain_running=True 이므로 중복 실행 없음.
        # [Skip] 전날 EOD 재학습이 성공했으면 동일 데이터로 재학습하는 중복을 스킵.
        #        EOD force=True 로 교체가 완료됐으므로 09:00 파이프라인 지연도 없다.
        #        __init__이 False로 초기화하는 것을 session_state 날짜 기록으로 보완:
        #        08:45 신규 시작 시 전날 EOD 성공이면 여기서 복원 → PreRetrain 스킵.
        #        단, 장중 재시작(__init__ 이후 08:55 미경유)은 _warmup_retrain_pending=False
        #        로 이미 이 블록 자체를 건너뛰므로 인트라데이 즉시재학습 동작에 영향 없음.
        if not getattr(self, "_eod_retrain_ok", False):
            try:
                _pre_ss = self._read_session_state()
                _eod_date_str = _pre_ss.get("eod_retrain_ok_date", "")
                if _eod_date_str:
                    _eod_d = datetime.date.fromisoformat(_eod_date_str)
                    _days_ago = (datetime.date.today() - _eod_d).days
                    if 1 <= _days_ago <= 5:   # 주말·공휴일 포함 최대 5 영업일 이내
                        self._eod_retrain_ok = True
                        log_manager.system(
                            f"[PreRetrain] EOD 재학습 날짜 복원: {_eod_date_str} "
                            f"({_days_ago}일 전) → PreRetrain 스킵 검토",
                            "INFO",
                        )
            except Exception as _pre_ss_e:
                logger.warning("[PreRetrain] eod_retrain_ok_date 복원 실패 (무해): %s", _pre_ss_e)
        if (
            getattr(self, "_warmup_retrain_pending", False)
            and not getattr(self, "_gbm_retrain_running", False)
        ):
            self._warmup_retrain_pending = False
            if getattr(self, "_eod_retrain_ok", False):
                log_manager.system(
                    "[PreRetrain] 08:55 사전 재학습 스킵 — 전날 EOD 재학습 성공 (동일 데이터 중복 불필요)",
                    "INFO",
                )
            else:
                self._gbm_retrain_running = True
                self._gbm_retrain_started_at = datetime.datetime.now()  # P1-B: 타임아웃 추적
                self._gbm_retrain_done_event.clear()
                self.dashboard.set_model_status("GBM 사전 재학습중...")
                log_manager.system(
                    "[PreRetrain] 08:55 GBM 사전 재학습 시작 — EOD 미완료 또는 재시작 복구", "INFO"
                )

                def _pre_retrain_worker():
                    result = {"ok": False, "error": "unknown"}
                    try:
                        result = self.batch_retrainer.retrain_now(force=True)
                    except BaseException as _pre_e:  # MemoryError 등 BaseException 포함
                        result = {"ok": False, "error": str(_pre_e)}
                    # P1-A 강화: BaseException(MemoryError 포함) 무관 항상 해제
                    self._gbm_retrain_running = False
                    self._gbm_retrain_done_event.set()   # worker 스레드에서 직접 해제 (QTimer 전달 불안정 대비)
                    QTimer.singleShot(0, lambda r=result: self._on_gbm_retrain_done(r, True))

                threading.Thread(target=_pre_retrain_worker, daemon=True).start()

    def _pre_market_stage2(self):
        """2단계 (08:58): 2회차 macro fetch → SP500·KRW 실수치 반영 → 레짐 확정.
        MacroFetcher._first_fetch_done=True 상태에서 호출되므로 chg가 실제값으로 계산된다."""
        self.macro_fetcher.manual_fetch()  # 강제 2회차 fetch
        _fetched = self.macro_fetcher.get_features()
        # MacroFetcher는 변동률을 소수 형태(0.005 = 0.5%)로 반환하고
        # RegimeClassifier는 퍼센트 단위(0.5 = 0.5%)를 기대하므로 ×100 변환한다.
        macro_data = {
            "vix":             _fetched.get("vix", 20.0),
            "sp500_chg_pct":   round(_fetched.get("sp500_chg", 0.0) * 100, 4),
            "nasdaq_chg_pct":  round(_fetched.get("nasdaq_chg", 0.0) * 100, 4),
            "usd_krw_chg_pct": round(_fetched.get("usd_krw_chg", 0.0) * 100, 4),
            "us10y_chg":       _fetched.get("us10y_chg", 0.0),
        }
        logger.info(
            "[System] 매크로 수집 완료 | VIX=%.1f SP500=%+.2f%% KRW=%+.2f%%",
            macro_data["vix"], macro_data["sp500_chg_pct"], macro_data["usd_krw_chg_pct"],
        )

        result = self.regime_classifier.classify(**macro_data)
        self.current_regime = result["regime"]

        logger.info("[System] 레짐 확정: %s | %s", self.current_regime, result["description"])
        log_manager.system(f"레짐: {self.current_regime} | {result['description']}")

        self.dashboard.update_supply_macro(
            vix=macro_data["vix"],
            sp500_chg=macro_data["sp500_chg_pct"] / 100,
            usd_krw=macro_data["usd_krw_chg_pct"],
            regime=self.current_regime,
        )
        self.dashboard.append_sys_log(
            f"레짐 확정: {self.current_regime} | {result['description']}"
        )
        self.dashboard.set_ui_ready_mode()

        # 투자자 warmup fetch — _last_fetch 초기화로 09:00 첫 파이프라인 z-score 폭발 방지.
        # _last_fetch=None 상태에서는 age_sec=9999 → quality_investor_stale z-score +27 발생.
        # 장전 fetch라 nets={}가 예상되지만 _last_fetch 설정만으로도 효과가 있다.
        try:
            self.investor_data.fetch_all(include_program=False)
            logger.info("[System] PreOpen 투자자 warmup fetch 완료 (age_sec 초기화)")
            log_manager.system("PreOpen 투자자 warmup fetch 완료")
        except Exception as _e:
            logger.warning("[System] PreOpen 투자자 warmup fetch 실패 (무해): %s", _e)

    # [SERVICE-BOUNDARY 2/4] MinutePipelineService
    # 책임: 분봉 단위 의사결정(검증→학습→피처→예측→진입/청산→기록)
    # 입력: bar(분봉), 실시간 누적 피처 상태, 현재 포지션/리스크 상태
    # 출력: decision, 주문 요청, DB/대시보드 업데이트
    # ── 매분 파이프라인 ────────────────────────────────────────
    def run_minute_pipeline(self, bar: dict):
        """
        매분 실행되는 9단계 파이프라인

        Args:
            bar: {ts, open, high, low, close, volume, buy_vol, sell_vol,
                  bid_price, ask_price, bid_qty, ask_qty}
        """
        _pipe_t0 = time.perf_counter()
        _st: list = [("start", _pipe_t0)]
        ts_raw = bar.get("ts", datetime.datetime.now())
        ts     = ts_raw.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts_raw, "strftime") else str(ts_raw)
        # [S2-A] 지연 SGD 학습 변수 — S2에서 채워지고 "end" 이후에 소비
        # 초기값 [] 로 설정해 early return 시에도 NameError 방지
        _sgd_deferred_verified: list = []
        _sgd_deferred_stuck: bool = False

        # ── 분봉 데이터 유효성 가드 ───────────────────────────────
        # 비정상 분봉이 피처/진입/청산 오발동을 일으키지 않도록 파이프라인 앞단 차단
        try:
            _c = float(bar.get("close", 0))
            _h = float(bar.get("high",  0))
            _l = float(bar.get("low",   0))
            _v = int(float(bar.get("volume", 0)))
        except (ValueError, TypeError) as _e:
            log_manager.system(
                f"[Guard-C0] bar 타입 변환 오류 차단 — 브로커 데이터 이상: {_e} ({ts})",
                "WARNING",
            )
            self.dashboard.notify_pipeline_ran()
            return

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
        _prev_pipeline_price      = self._last_pipeline_price  # sigma 계산용 이전 종가 선점
        self._last_pipeline_price = close  # 잔고 UI 합성에 사용
        self._last_close = close           # 옵션체인 QTimer 폴링용 최신 종가

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
        # [C1] 로컬 레퍼런스 선점 — 이후 접근에서 _pending_order가 None으로 바뀌더라도
        #       _po는 원래 dict를 유지하므로 AttributeError 없이 안전하게 읽을 수 있다.
        _po = self._pending_order
        if _po is not None:
            _pending_age = (datetime.datetime.now() - _po["created_at"]).total_seconds()
            _has_order_no = bool(_po.get("order_no", ""))
            _timeout_s = 300 if _has_order_no else 60
            if getattr(getattr(self, "broker", None), "name", "") == "cybos" and not _has_order_no:
                # Cybos mock can delay the first acceptance callback well beyond
                # the Kiwoom-oriented 60s timeout.
                _timeout_s = 180
            _pending_filled = _po.get("filled_qty", 0)
            _pending_total = _po.get("qty", 0)
            if _pending_age > _timeout_s and _pending_filled == 0:
                _accepted_label = f"접수확인(order_no={_po['order_no']})" if _has_order_no else "미접수"
                # [B52] ENTRY 타임아웃: 낙관적 포지션 복원 + 쿨다운
                if _po.get("kind") == "ENTRY":
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
                    f"kind={_po['kind']} dir={_po['direction']} "
                    f"order_no={_po.get('order_no','?') or '?'} → 주문 소멸 처리",
                    "WARNING",
                )
                self._clear_pending_order()
            elif (
                _po.get("kind") == "ENTRY"
                and 0 < _pending_filled < _pending_total
            ):
                # [Fix-EntryStuck] ENTRY 부분체결 후 잔량 미체결 stuck
                # 브로커 Chejan 이벤트 유실 vs 실제 미체결을 구분하기 위해
                # EXIT stuck 처리와 동일하게 브로커 잔고 TR 조회 후 실제 수량으로 sync.
                # 주의: 브로커 확인 없이 position.quantity를 낮추면
                #   이벤트 유실 케이스에서 실잔량 > 청산수량 → 잔여 포지션 발생.
                _last_fill_at = _po.get("last_fill_at")
                _since_last_fill = (
                    (datetime.datetime.now() - _last_fill_at).total_seconds()
                    if _last_fill_at else _pending_age
                )
                if _since_last_fill > 60:
                    _unfilled = _pending_total - _pending_filled
                    self._stuck_this_minute = True   # P3-a: stuck 발생 → 이번 분봉 학습 스킵
                    log_manager.system(
                        f"[PendingOrder] ENTRY 부분체결 stuck {_since_last_fill:.0f}s — "
                        f"filled={_pending_filled}/{_pending_total} (미체결={_unfilled}계약) "
                        f"→ 브로커 잔고 조회로 실수량 확인",
                        "WARNING",
                    )
                    if not _ts_resolve_stuck_entry_pending(self):
                        # 브로커 조회 실패 시: 수량 하향 보정 없이 pending만 소멸
                        # (잔여 포지션 발생 위험보다 임의 수량 축소 위험이 더 큼)
                        log_manager.system(
                            f"[PendingOrder] ENTRY stuck 브로커 조회 실패 — "
                            f"pending 소멸, position.qty={self.position.quantity} 유지",
                            "WARNING",
                        )
                        self._clear_pending_order()
            elif (
                _po.get("kind", "").startswith("EXIT")
                and 0 < _po.get("filled_qty", 0) < _po.get("qty", 0)
            ):
                # EXIT 부분체결 stuck: 브로커가 나머지 수량을 취소했거나 이벤트 유실
                # last_fill_at 기준 30초 경과 시 pending 소멸 → 하드스톱 재발동 허용
                _last_fill_at = _po.get("last_fill_at")
                _since_last_fill = (
                    (datetime.datetime.now() - _last_fill_at).total_seconds()
                    if _last_fill_at else _pending_age
                )
                if _since_last_fill > 10:
                    self._stuck_this_minute = True   # P3-a: stuck 발생 → 이번 분봉 학습 스킵
                    log_manager.system(
                        f"[PendingOrder] EXIT 부분체결 stuck {_since_last_fill:.0f}s — "
                        f"filled={_po['filled_qty']}/{_po['qty']} "
                        f"kind={_po['kind']} order_no={_po.get('order_no','?')} "
                        f"→ pending 소멸, 잔여 포지션 긴급청산 시도",
                        "WARNING",
                    )
                    if not _ts_resolve_stuck_exit_pending(self):
                        self._clear_pending_order()

        # P3-a: 매 분봉 시작 시 stuck 플래그 초기화
        self._stuck_this_minute = False
        log_manager.signal(f"--- {ts} 분봉 파이프라인 시작 ---")

        # 가격 구조 감지용 버퍼 갱신
        self._price_struct_buf.append({
            "high": float(bar.get("high", 0.0) or 0.0),
            "low":  float(bar.get("low",  0.0) or 0.0),
        })

        # ── rolling σ 갱신 (방법3) ─────────────────────────────────────
        # 매분 1분봉 수익률을 sigma_buf에 추가 → HORIZON_THRESHOLDS 실시간 갱신
        # _prev_pipeline_price: 이 틱 진입 전 캡처 (2790에서 close로 덮어쓰이기 전 값)
        _last_p = _prev_pipeline_price
        if _last_p and _last_p > 0 and close and close > 0:
            _ret_1m = (close - _last_p) / _last_p * 100
            self._sigma_buf.append(_ret_1m)

        _n_sig = len(self._sigma_buf)
        if _n_sig >= runtime_settings.SIGMA_W_MIN and _n_sig > 1:
            _v = list(self._sigma_buf)
            _m = sum(_v) / _n_sig
            self._sigma_20 = (
                sum((x - _m) ** 2 for x in _v) / (_n_sig - 1)
            ) ** 0.5
            self._sigma_ready = (_n_sig >= runtime_settings.SIGMA_W)
        elif self._last_sigma_20 > 0:
            self._sigma_20 = self._last_sigma_20

        # P5: sigma_at_t 검증 로그 — 157차 P3 수정(sigma 항상 0 버그) 효과 확인
        # 장 초반 20봉 누적 전(SIGMA_W_MIN 미달)에도 _last_sigma_20 폴백이 작동하는지 포함
        # _last_p가 None(재시작 첫 분봉)일 수 있으므로 float 변환 후 포맷
        _sigma_nonzero = sum(1 for x in self._sigma_buf if x != 0.0)
        if _n_sig <= 5 or (_n_sig % 10 == 0):
            log_manager.learning(
                f"[sigma] sigma_at_t={self._sigma_20:.4f}% "
                f"buf_n={_n_sig} nonzero={_sigma_nonzero} "
                f"prev_p={float(_last_p or 0.0):.2f} cur_p={float(close or 0.0):.2f}"
            )

        if (
            runtime_settings.USE_ROLLING_SIGMA_THRESHOLD
            and self._sigma_20 > 0
        ):
            import math as _math_s
            from config import settings as _cfg_s
            _K = _cfg_s.SIGMA_K
            _cfg_s.HORIZON_THRESHOLDS.update({
                "1m":  self._sigma_20 / 100.0 * _K * _math_s.sqrt(1),
                "3m":  self._sigma_20 / 100.0 * _K * _math_s.sqrt(3),
                "5m":  self._sigma_20 / 100.0 * _K * _math_s.sqrt(5),
                "10m": self._sigma_20 / 100.0 * _K * _math_s.sqrt(10),
                "15m": self._sigma_20 / 100.0 * _K * _math_s.sqrt(15),
                "30m": self._sigma_20 / 100.0 * _K * _math_s.sqrt(30),
            })

        # ── STEP 1: 과거 예측 검증 ─────────────────────────────
        _st.append(("S1", time.perf_counter()))
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
            # CB③: 30m 방향성 예측만 집계 (FLAT 예측 제외)
            # FLAT 예측(direction=0)이 틀려도 모델이 방향을 포기한 것 → 패널티 부적절
            # UP/DOWN 예측의 정확도만 "방향 신뢰도"로 평가
            _pred_dir = int(v.get("predicted", 0))
            if (v["horizon"] == "30m"
                    and _conf > 0.38
                    and _pred_dir != 0          # FLAT 예측 제외
                    and _pred_ts >= self._session_start_ts):
                _contra_active = self.contrarian_mode.should_contra_enter()
                self.circuit_breaker.record_accuracy(
                    v["correct"], confidence=_conf,
                    contrarian_active=_contra_active,
                    eks_active=self.system_health.kill_switch_active,
                )
            self.horizon_calibrator.record(v["horizon"], _conf, v["correct"])
            # 앙상블 보정기: 1m 결과를 앙상블 정확도 대리 지표로 사용
            # (1m이 가장 빠른 피드백 — 당시 앙상블 conf와 적중 여부로 보정기 학습)
            # 단, 당시 앙상블에 1m가 포함됐을 때만 유효 — OFF 중 결과로 학습하면
            # "1m 제외 앙상블 conf"를 "1m 단독 적중 여부"로 검증하는 논리 불일치 발생
            if v["horizon"] == "1m":
                _cached = self._ensemble_conf_cache.get(v["ts"])
                if _cached is not None:
                    _ens_conf_at_t, _1m_was_active = _cached
                    if _1m_was_active:
                        self.ensemble.record_ensemble_outcome(_ens_conf_at_t, bool(v["correct"]))
            # F1 적응형 가중치: 전 호라이즌 검증 결과 누적 (이번 세션 예측만)
            if _pred_ts >= self._session_start_ts:
                self.ensemble.record_horizon_verification(
                    v["horizon"],
                    int(v.get("predicted", 0)),
                    int(v.get("actual", 0)),
                )
            # 시간대별 정확도 기록 (15:40 DailyConsolidator.consolidate()에서 집계)
            if v["horizon"] == "5m":
                _zone = get_time_zone(datetime.datetime.strptime(v["ts"], "%Y-%m-%d %H:%M:%S"))
                self.daily_consolidator.record(_zone, bool(v["correct"]))
            _dir_map = {1: "UP", -1: "DN", 0: "FL"}
            _pred_str   = _dir_map.get(v.get("predicted", 0), "?")
            _actual_str = _dir_map.get(v.get("actual",    0), "?")
            if v["correct"]:
                log_manager.learning(
                    f"✓ {v['horizon']} 예측 적중 (conf={_conf:.1%} {_pred_str})"
                )
            else:
                log_manager.learning(
                    f"✗ {v['horizon']} 예측 실패 (conf={_conf:.1%} 예측={_pred_str} 실제={_actual_str})"
                )
            # [Qualify] 검증 사이클 카운트 — 이번 세션 예측만 (이전 세션 carry-over 제외)
            _h = v["horizon"]
            _pred_ts_q = v.get("ts", "") or ""
            if _h in self._horizon_runtime_state and _pred_ts_q >= self._session_start_ts:
                _qs = self._horizon_runtime_state[_h]
                _qs["verified_cycles"] += 1
                _qs["recent_accuracy"] = self.online_learner.horizon_accuracy(_h)
                _need = getattr(runtime_settings, "HORIZON_QUALIFY_MIN_CYCLES", 3)
                if _qs["verified_cycles"] >= _need and _qs["trained_cycles"] >= _need:
                    if not _qs["qualified"]:
                        _qs["qualified"] = True
                        _qs["active"]    = True
                        _qs["status"]    = "active"
                        log_manager.signal(
                            f"[Qualify] {_h} 자격 획득 "
                            f"(verified={_qs['verified_cycles']} trained={_qs['trained_cycles']})"
                        )
                elif not _qs["qualified"]:
                    _qs["status"] = "not_qualified"
                logger.debug(
                    "[Qualify] %s verified=%d/3 trained=%d/3 status=%s",
                    _h, _qs["verified_cycles"], _qs["trained_cycles"], _qs["status"],
                )

        # ── 호라이즌별 롤링 Bias 통계 (30건 윈도우) ──────────────────────────
        # 분봉 1건씩 누적 → 15건 이상 쌓이면 편향 판정 / 10분마다 요약 출력
        if verified:
            for _v in verified:
                self._bias_buf[_v["horizon"]].append({
                    "predicted": int(_v.get("predicted", 0)),
                    "correct":   bool(_v["correct"]),
                })

            self._bias_log_tick += 1
            _log_summary = (self._bias_log_tick % 10 == 0)

            for _h in sorted(self._bias_buf):
                _buf = self._bias_buf[_h]
                _tot = len(_buf)
                if _tot == 0:
                    continue
                _ok = sum(1 for e in _buf if e["correct"])
                _up = sum(1 for e in _buf if e["predicted"] ==  1)
                _dn = sum(1 for e in _buf if e["predicted"] == -1)
                _fl = sum(1 for e in _buf if e["predicted"] ==  0)
                _acc_h = _ok / _tot

                _bias_tag = ""
                _up_r = _dn_r = _fl_r = 0.0
                if _tot >= 15:
                    _up_r, _dn_r, _fl_r = _up / _tot, _dn / _tot, _fl / _tot
                    if _up_r >= 0.75:
                        _bias_tag = f" [UP편향! {_up_r:.0%}]"
                    elif _dn_r >= 0.75:
                        _bias_tag = f" [DN편향! {_dn_r:.0%}]"
                    elif _fl_r >= 0.75:
                        _bias_tag = f" [FL편향! {_fl_r:.0%}]"

                if _bias_tag:
                    log_manager.learning(
                        f"[Bias⚠] {_h} 적중={_acc_h:.0%}({_ok}/{_tot})"
                        f" UP={_up} DN={_dn} FL={_fl}{_bias_tag}"
                    )
                elif _log_summary and _tot >= 5:
                    log_manager.learning(
                        f"[Bias] {_h} 적중={_acc_h:.0%}({_ok}/{_tot})"
                        f" UP={_up} DN={_dn} FL={_fl}"
                    )

                # [P2+] 방향 편향 고착 → uniform fallback 제어 (FL/UP/DN 공통)
                # 127차: FL 전용 → 전 방향 공통
                # 수정: FL 20분→10분, UP/DN 10분→5분, tot>=20→15, bias>=0.90→0.80
                #   근거: 3m FL 100%가 18분 지속돼도 BiasReset 미발동(20분 미달) 확인.
                #   FL 자연 발생은 맞지만 GBM 붕괴급 편향(80%+)에는 빠른 대응 필요.
                _dir_bias_r = max(_up_r, _dn_r, _fl_r)
                _biased_dir = (
                    "FL" if _fl_r == _dir_bias_r else
                    ("UP" if _up_r == _dir_bias_r else "DN")
                )
                # coldstart 구간(재기동 직후 GBM 초기화 중)은 FL 기준 완화 10분→5분
                _in_coldstart = self.model.is_in_startup_warmup(
                    datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                )
                _bias_thresh_min = (5 if _in_coldstart else 10) if _biased_dir == "FL" else 5
                if _tot >= 15 and _dir_bias_r >= 0.80:
                    self._bias_fl_streak[_h] = self._bias_fl_streak.get(_h, 0) + 1
                    if (self._bias_fl_streak[_h] >= _bias_thresh_min
                            and _h not in self._bias_override_horizons):
                        self._bias_override_horizons.add(_h)
                        log_manager.learning(
                            f"[BiasReset] {_h} {_biased_dir}편향 {_dir_bias_r:.0%} "
                            f"{self._bias_fl_streak[_h]}분 지속 → uniform fallback 적용"
                        )
                        self.circuit_breaker.record_horizon_fl_bias(
                            _h, _dir_bias_r, self._bias_fl_streak[_h]
                        )
                        # P4: GBM 편향 감지 → SGD 비중 min floor 탈출 (대항력 회복)
                        self.online_learner.boost_sgd_for_bias(_h)
                else:
                    # P1: fallback 해제 임계값 60% (진입 80%와 비대칭)
                    # 이력이 충분히 정상화된 후에만 해제 → 경계 flip-flop 방지
                    _can_release = _dir_bias_r < 0.60
                    if _h in self._bias_override_horizons:
                        if _can_release:
                            self._bias_override_horizons.discard(_h)
                            # P0: 오염된 편향 이력도 함께 초기화 → 해제 즉시 재고착 방지
                            self._bias_buf[_h].clear()
                            self._conf_stuck[_h] = 0
                            log_manager.learning(
                                f"[BiasReset] {_h} {_biased_dir}편향 해소 ({_dir_bias_r:.0%})"
                                f" → uniform fallback 해제"
                            )
                        # else: 60~80% 구간은 fallback 유지, streak만 리셋
                    self._bias_fl_streak[_h] = 0

        # ── STEP 2: SGD 온라인 자가학습 ────────────────────────
        _st.append(("S2", time.perf_counter()))
        _s2_enter_t = _st[-1][1]                                    # [P1a] GIL 대기 측정 기준점
        self.meta_gate.learner.apply_pending()                       # [P0] 이전 틱 비동기 LR 결과 반영
        _s2_meta_t = time.perf_counter()
        _s2_gil_wait_ms = int((_s2_meta_t - _s2_enter_t) * 1000)   # [P1a] S2 마커→실행 gap
        # STEP 1 검증된 예측마다 해당 시점 피처로 즉시 partial_fit
        # FLAT 예측도 포함: evaluate() FLAT early-return 경우 meta_features를 직접 build
        for v in verified:
            _meta_feats = v.get("features") or {}
            try:
                _v_dir = v["predicted"]
                _v_ts  = datetime.datetime.strptime(v["ts"], "%Y-%m-%d %H:%M:%S")
                _v_conf = float(v.get("confidence", 0.5) or 0.5)
                if _v_dir == DIRECTION_FLAT:
                    # FLAT early-return 경로는 meta_features를 반환하지 않으므로 직접 빌드
                    _flat_meta_feats = self.meta_gate.learner.build_meta_features(
                        regime=self.current_micro_regime,
                        hurst=float((_meta_feats or {}).get("hurst", 0.5) or 0.5),
                        atr_ratio=float((_meta_feats or {}).get("atr_ratio", 1.0) or 1.0),
                        hour_minute=_v_ts.hour * 100 + _v_ts.minute,
                        recent_accuracy=self.online_learner.recent_accuracy(),
                        signal_strength=_v_conf,
                    )
                    self.meta_gate.record_outcome(_flat_meta_feats, bool(v["correct"]), _v_conf)
                else:
                    _meta_eval = self.meta_gate.evaluate(
                        direction=_v_dir,
                        confidence=_v_conf,
                        regime=self.current_regime,
                        micro_regime=self.current_micro_regime,
                        features=_meta_feats,
                        now=_v_ts,
                        recent_accuracy=self.online_learner.recent_accuracy(),
                    )
                    self.meta_gate.record_outcome(
                        _meta_eval.get("meta_features", []),
                        bool(v["correct"]),
                        _v_conf,
                    )
                # selection bias 해소: 동일 ts에 skip된 shadow 신호도 동일 결과로 기록
                for _sf, _sc in self._meta_shadow.pop(v.get("ts", ""), []):
                    self.meta_gate.record_outcome(_sf, bool(v["correct"]), _sc)
            except Exception as _meta_record_err:
                logger.debug("[MetaGate] verify record skip: %s", _meta_record_err)

        # shadow 버퍼 오래된 항목 정리 (60분 초과) — 검증 도달 없는 항목 누적 방지
        if self._meta_shadow and ts:
            try:
                _shadow_cutoff = (
                    datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    - datetime.timedelta(minutes=60)
                ).strftime("%Y-%m-%d %H:%M:%S")
                _stale = [k for k in self._meta_shadow if k < _shadow_cutoff]
                for _k in _stale:
                    del self._meta_shadow[_k]
            except Exception:
                pass

        # [S2-A] online_learner.learn() 은 파이프라인 "end" 이후로 지연 실행
        # — GBM 배치 재학습 중 Python GC/CPU 포화로 5~7s 블로킹 방지
        # — _sgd_deferred_stuck 과 verified 를 보존해 두고 "end" 이후에 소비
        _sgd_deferred_stuck    = bool(self._stuck_this_minute)
        _sgd_deferred_verified = list(verified)  # snapshot (verified 는 이후 재활용 안 됨)

        # MetaGate 분봉 말미 학습 — record_outcome() 누적 분을 1회에 소화
        # flush_fit()은 daemon 스레드 비동기 실행 → 즉시 반환 (GIL 블로킹 없음)
        # 완료된 결과는 다음 틱 apply_pending()에서 swap-in
        _s2_flush_t = time.perf_counter()
        self.meta_gate.learner.flush_fit()
        _s2_meta_ms  = int((_s2_flush_t - _s2_meta_t) * 1000)
        _s2_flush_ms = int((time.perf_counter() - _s2_flush_t) * 1000)
        _s2_total_ms = _s2_gil_wait_ms + _s2_meta_ms + _s2_flush_ms
        if _s2_total_ms > 200:
            # [S2-B] SYSTEM logger(INFO 레벨)에는 debug 가 필터링되므로 debug_log 사용
            debug_log.debug(
                "[S2] gil_wait=%dms meta=%dms flush=%dms verified=%d",
                _s2_gil_wait_ms, _s2_meta_ms, _s2_flush_ms, len(verified),
            )
        if _s2_total_ms > 1000:
            # [S2-C] 1000ms 초과 시 SYSTEM WARN 으로도 출력 (CB 임박 진단용)
            logger.warning(
                "[S2-느림] gil_wait=%dms meta=%dms flush=%dms verified=%d",
                _s2_gil_wait_ms, _s2_meta_ms, _s2_flush_ms, len(verified),
            )

        # ── STEP 3: GBM 배치 재학습 (주간/월간 스케줄 또는 세션 재시작 즉시) ────
        _st.append(("S3", time.perf_counter()))
        # [P1a-보완] S2 wall-time vs 측정합계 괴리 = 분산 GIL 대기 (체크포인트 밖 누적분)
        _s2_wall_ms    = int((_st[-1][1] - _st[-2][1]) * 1000)
        _s2_hidden_gil = _s2_wall_ms - _s2_total_ms
        if _s2_hidden_gil > 500:
            _gil_src = "GBM" if self._gbm_retrain_running else "MetaConf-LR"
            # MetaConf-LR 원인 시 각 레짐 버퍼 크기 포함 → cold-start n 진단
            _meta_buf_info = ""
            if _gil_src == "MetaConf-LR":
                try:
                    _meta_buf_info = " buf=" + "/".join(
                        f"{r[:2]}:{len(self.meta_gate.learner._bufs[r])}"
                        for r in self.meta_gate.learner._bufs
                    )
                except Exception:
                    pass
            logger.warning(
                "[S2-분산GIL] wall=%dms measured=%dms hidden_gil=%dms src=%s%s",
                _s2_wall_ms, _s2_total_ms, _s2_hidden_gil, _gil_src, _meta_buf_info,
            )
            log_manager.system(
                f"[S2-분산GIL] wall={_s2_wall_ms}ms hidden={_s2_hidden_gil}ms "
                f"src={_gil_src}{_meta_buf_info}",
                "WARNING",
            )
        # [이상점3 수정] 재학습을 daemon thread로 분리 — 메인 스레드 블로킹 방지.
        # 완료 시 QTimer.singleShot(0, ...) 으로 메인 스레드에서 모델 로드.
        # _gbm_retrain_running 플래그로 중복 실행 차단.
        _warmup_forced = self._warmup_retrain_pending

        # [DriftRetrain] 방향 드리프트 감지 → 자동 장중 재학습
        # 오전/오후 시장 방향이 전환될 때 GBM이 오전 편향을 유지하는 문제 대응.
        # 조건: 30분 정확도 25% 미만 + 최소 20건 집계 + 마지막 재학습 60분 이상 경과
        # 근거: 6/12 13:51 CB③ 발동 — acc30m=6.7%, 마지막 재학습 11:10 (약 2.5시간 전)
        # 부작용 방어:
        #   n >= 20 조건: _accuracy_buf 비어있으면 0/1=0.0 → 오발동 방지
        #   (세션 초기·재시작 직후 n=0인 상태에서 acc30m=0.0으로 잘못 감지되는 현상)
        _dr_cb_status = self.circuit_breaker.status_dict()
        _dr_acc30m    = _dr_cb_status.get("accuracy_30m", 1.0)
        _dr_acc30m_n  = _dr_cb_status.get("cb3_samples",  0)
        _dr_last_rt   = getattr(self.batch_retrainer, "_last_retrain", None)
        _dr_mins = (
            (datetime.datetime.now() - _dr_last_rt).total_seconds() / 60
            if _dr_last_rt else float("inf")
        )
        _drift_trigger = (
            self.circuit_breaker.state != CB_STATE_HALTED  # HALT 중에는 재학습 불필요
            and _dr_acc30m < 0.25                          # 30분 정확도 25% 미만
            and _dr_acc30m_n >= 20                         # 최소 20건 집계 후 판단 (빈 버퍼 오발동 방지)
            and _dr_mins >= 60.0                           # 마지막 재학습으로부터 60분 이상
            and not getattr(self, "_gbm_retrain_running", False)
        )
        if _drift_trigger:
            log_manager.system(
                f"[DriftRetrain] 30분 정확도 {_dr_acc30m:.1%} (n={_dr_acc30m_n}) < 25% "
                f"({_dr_mins:.0f}분 경과) → 장중 경량 재학습 트리거",
                "WARNING",
            )

        # 주간 재학습(월요일 08:50): 전날(금요일) EOD full_cv 재학습이 성공했으면 스킵
        # → daily_close()가 월요일 포함 매일 정규 파라미터로 재학습하므로 중복 불필요
        _weekly_needed = (
            self.batch_retrainer.should_retrain_weekly()
            and not getattr(self, "_eod_retrain_ok", False)
        )
        _need_retrain = (
            _warmup_forced
            or _drift_trigger
            or _weekly_needed
            or self.batch_retrainer.should_retrain_monthly()
        )
        if _need_retrain and not getattr(self, "_gbm_retrain_running", False):
            if _warmup_forced:
                self._warmup_retrain_pending = False
                log_manager.system(
                    "[WarmupRetrain] 세션 재시작 후 첫 GBM 경량 재학습 — 별도 스레드 시작 (intraday)", "INFO"
                )
            elif _drift_trigger:
                log_manager.system(
                    f"[DriftRetrain] GBM 경량 재학습 시작 "
                    f"(acc30m={_dr_acc30m:.1%} n={_dr_acc30m_n} 경과={_dr_mins:.0f}분)",
                    "WARNING",
                )
            self._gbm_retrain_running = True
            self._gbm_retrain_started_at = datetime.datetime.now()  # P1-B: 타임아웃 추적
            self._gbm_retrain_done_event.clear()
            self.circuit_breaker.set_gbm_retrain_active(True)   # CB⑤ 임계 완화
            self.dashboard.set_model_status("GBM 재학습중...")
            _is_warmup = bool(_warmup_forced)

            def _retrain_worker():
                result = {"ok": False, "error": "unknown"}
                try:
                    # intraday=True: n_estimators 100, 20k봉, CV 없음 → 장중 GIL 블로킹 최소화
                    # 08:55 pre-market(_pre_retrain_worker)만 풀 파라미터 유지
                    result = self.batch_retrainer.retrain_now(force=False, intraday=True)
                except BaseException as _re:  # MemoryError 등 BaseException 포함
                    result = {"ok": False, "error": str(_re)}
                # P1-A: BaseException(MemoryError 포함) 무관 항상 해제
                self._gbm_retrain_running = False
                self._gbm_retrain_done_event.set()   # worker 스레드에서 직접 해제 (QTimer 전달 불안정 대비)
                QTimer.singleShot(0, lambda r=result: self._on_gbm_retrain_done(r, _is_warmup))

            threading.Thread(target=_retrain_worker, daemon=True).start()

        # ── STEP 4: 피처 생성 ──────────────────────────────────
        _st.append(("S4", time.perf_counter()))
        # 개선 3: 전일 동시간대 수익률 매분 갱신 (prev_day_close_buf가 있는 경우만)
        if self.feature_builder._prev_day_close_buf:
            self.feature_builder.update_prev_day_same_hour_ret(ts)
        # fetch_all()은 _investor_timer(60s QTimer)에서 COM 콜백 외부로 실행
        # 파이프라인은 이전 분봉에서 수집된 캐시를 읽음 (당일 누적 수급 — 1분 지연 허용)
        supply_feats = self.investor_data.get_features()
        self.pcr_store.update(supply_feats)
        _raw_macro   = self.macro_fetcher.get_features()
        _macro_feats = self.macro_transformer.transform(_raw_macro)
        _option_feats = self.option_feat_calc.transform(self.pcr_store.get_features())
        # 옵션 체인 폴링은 _option_chain_timer(QTimer 300s) 에서 메인 스레드 COM 안전하게 수행.
        # 파이프라인은 캐시된 피처만 읽는다 (1분 지연 허용, BlockRequest 루프 블로킹 제거).
        _chain_feats = self.option_chain_snap.get_features()
        # [BUG FIX] _chain_feats(opt_chain_pcr/opt_gex_bn/opt_atm_*)를 option_data에 병합.
        # 이전: _chain_feats가 읽혔지만 build()에 전달되지 않아 raw_features에 저장 안 됨.
        _option_combined = dict(_option_feats)
        _option_combined.update(_chain_feats)
        features = self.feature_builder.build(
            bar,
            supply_demand = supply_feats,
            macro_data    = _macro_feats,
            option_data   = _option_combined,
            micro_regime  = self.current_micro_regime,  # 직전 분 레짐 (1분 lag 허용)
        )
        # 최소 0.5pt 보장 — 재시작 직후 1개 틱만으로 계산된 비정상 소ATR 방어
        atr      = max(features.get("atr", 0.5), 0.5)
        atr_ratio = features.get("atr_ratio", 1.0)

        # SHAP 대시보드용 VIX·PCR 실측값 캐싱 (매분)
        _mv = features.get("macro_vix")
        if _mv is not None:
            self._last_macro_vix_raw = float(_mv)
        _pcr = features.get("opt_chain_pcr")
        if _pcr and float(_pcr) > 0:
            self._last_opt_chain_pcr = float(_pcr)

        # ── CORE 3종 피처 NaN/Inf 가드 ──────────────────────────
        # 진입 체크리스트가 직접 사용하는 피처만 방어 (다른 피처는 앙상블에서 0으로 처리됨)
        for _fk in ("vwap_position", "cvd_direction", "ofi_pressure"):
            _fv = features.get(_fk)
            if _fv is None or (isinstance(_fv, float) and (math.isnan(_fv) or math.isinf(_fv))):
                log_manager.system(
                    f"[Guard-F1] {_fk} 비정상값({_fv}) → 0 교정 ({ts})", "WARNING"
                )
                features[_fk] = 0

        # 분봉·피처 원본 저장 — 비동기 큐에 투입 (파이프라인 블로킹 제거)
        try:
            self._db_write_queue.put_nowait(("candle_features", bar, ts, features))
        except _queue.Full:
            logger.warning("[DBQueue] 큐 포화 — candle_features 동기 write fallback")
            save_candle_and_features(bar, ts, features)

        # ── Phase 2: N분봉 집계 + 호라이즌별 피처 저장 ────────────
        try:
            _p2_completed = self.bar_aggregator.push(bar)
            for _h_min, _h_name in [(3, "3m"), (5, "5m"), (10, "10m"), (15, "15m"), (30, "30m")]:
                if _p2_completed.get(_h_min) is not None:
                    _h_feats = self.feature_builder.build_for_horizon(
                        _p2_completed[_h_min], _h_min
                    )
                    try:
                        self._db_write_queue.put_nowait(("horizon_features", ts, _h_name, _h_feats))
                    except _queue.Full:
                        logger.warning("[DBQueue] 큐 포화 — %s horizon_features 동기 write fallback", _h_name)
                        save_horizon_features(ts, _h_name, _h_feats)
        except Exception as _p2_err:
            logger.debug("[Phase2-STEP4] N분봉 처리 오류 (무해): %s", _p2_err)
            _p2_completed = {1: bar}

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
        self._ensure_shap_tracker()
        self._record_param_corr_snapshot(features)
        self._record_shap_feature_window(features)

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
            _dir_sign(features.get("cvd_direction", 0)),
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
            bear_exhaustion  = float(features.get("bear_exhaustion",  0.0) or 0.0),
            bull_exhaustion  = float(features.get("bull_exhaustion",  0.0) or 0.0),
            vwap_position    = float(features.get("vwap_position",    0.0) or 0.0),
            z_warn_count     = getattr(self.model, "last_z_warn_count", 0),
        )
        self.current_micro_regime = _mr["regime"]
        self.dashboard.update_micro_regime(
            _mr["regime"], _mr["adx"], _mr["atr_ratio"], _mr["regime_duration"]
        )
        self.dashboard.update_micro_regime_warmup(_mr.get("warmup"))
        # 1분봉 차트 레짐 색상 바 업데이트 + 재시작 복원용 DB 저장
        self.dashboard.minute_chart_set_regime(ts, _mr["regime"])
        try:
            save_regime_at(ts, _mr["regime"])
        except Exception:
            pass
        if _mr.get("regime_changed"):
            log_manager.signal(
                f"[MicroRegime] 레짐 변경 → {_mr['regime']} "
                f"(ADX={_mr['adx']:.1f} ATR비={_mr['atr_ratio']:.2f} "
                f"지속={_mr['regime_duration']}분)"
            )

        # ATR Circuit Breaker
        self.circuit_breaker.record_atr(atr_ratio)

        # ── [6순위] Shadow Session + Contrarian Mode 매분 업데이트 ──
        _cb_status = self.circuit_breaker.status_dict()
        _acc30m    = _cb_status.get("accuracy_30m", 0.0)
        _z_warn    = getattr(self.model, "last_z_warn_count", 0)
        self.system_health.update_z_warn(_z_warn)
        self._z_warn_5m.append(_z_warn)          # 배지용 5분 롤링 (state 무관)
        _ts_dt_obj = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        # pred_buffer 기반 30분 정확도 — CB accuracy_buf(거래 기반)보다 훨씬 빠르게 채워짐
        # CB③와 동일 기준: FLAT 제외 + conf>0.38 + 이번 세션 예측만 집계
        # min_samples=10: 샘플 부족(세션 초기 30분) 시 0.5 반환 → 게이트 통과 유지
        _last_dir = getattr(self, "_last_ensemble_direction", 0)
        try:
            _contra_acc30m = self.pred_buffer.recent_accuracy(
                "30m",
                last_n=30,
                exclude_flat=True,
                min_conf=0.38,
                since_ts=self._session_start_ts,
                min_samples=10,
            )
        except Exception:
            _contra_acc30m = _acc30m
        self.shadow_session.update(
            ts_dt            = _ts_dt_obj,
            core_health_score= self.core_health.score,
            z_warn_count     = _z_warn,
        )
        self.contrarian_mode.update(
            acc30m           = _contra_acc30m,
            signal_direction = _last_dir,
            regime           = self.current_regime,
            cb3_samples      = _cb_status.get("cb3_samples", 0),
        )
        # Contrarian ACTIVE 시 진입 관리 패널 역방향 버튼 힌트 전달
        _contra_active = self.contrarian_mode.should_contra_enter()
        _contra_d = self.contrarian_mode.contra_direction
        _contra_dir_str = "LONG" if _contra_d == 1 else "SHORT" if _contra_d == -1 else ""
        self.dashboard.set_contrarian_hint(_contra_active, _contra_dir_str)
        # 대시보드 실험 게이트 패널 갱신
        if getattr(self.dashboard, "experiment_gate_panel", None):
            self.dashboard.experiment_gate_panel.update_shadow(
                self.shadow_session.status_dict()
            )
            self.dashboard.experiment_gate_panel.update_contrarian(
                self.contrarian_mode.status_dict()
            )

        # ── Layer 2 장중 전술 레짐 갱신 ──────────────────────────
        # _ts_dt_obj, _z_warn, _contra_active 모두 이 시점에 정의 완료
        _open_p  = getattr(self, "_session_open_price", 0.0) or 0.0
        _day_ret = (close - _open_p) / (_open_p + 1e-9) if _open_p > 0 else 0.0
        _ret_1m  = (
            (close - float(bar.get("open", close) or close))
            / (float(bar.get("open", close) or close) + 1e-9)
        )
        _ofi_15m = float(
            features.get("ofi_imbalance_15m", 0.0) or
            features.get("ofi_imbalance",     0.0) or 0.0
        )
        _prev_intraday = self.current_intraday_regime
        self.current_intraday_regime = self.intraday_regime.update(
            ts_dt            = _ts_dt_obj,
            futures_day_ret  = _day_ret,
            open_price       = _open_p,
            close_price      = close,
            atr_ratio        = _mr["atr_ratio"],
            ofi_15m_avg      = _ofi_15m,
            z_warn_count     = _z_warn,
            ret_1m           = _ret_1m,
            contrarian_active= _contra_active,
        )
        if self.current_intraday_regime != _prev_intraday:
            log_manager.signal(
                f"[IntradayRegime] {_prev_intraday} → {self.current_intraday_regime} "
                f"| day={_day_ret*100:+.2f}% ATR={_mr['atr_ratio']:.2f} z={_z_warn}"
            )
        if getattr(self.dashboard, "regime_panel", None):
            self.dashboard.regime_panel.update_intraday(
                self.intraday_regime.status_dict()
            )
        self.dashboard.update_layer2(self.intraday_regime.status_dict())

        # ── STEP 5: 멀티 호라이즌 예측 ─────────────────────────
        _st.append(("S5", time.perf_counter()))
        _gbm_ready = self.model.is_ready()
        _sgd_ready = self.online_learner.is_ready()

        if not _gbm_ready and not _sgd_ready:
            # 아무 모델도 미학습 — 1/3 기본값으로 예측 진행하여 DB 저장
            # (다음 분 STEP1 검증 → STEP2 learn() 호출 → SGD 부트스트랩)
            log_manager.signal("[bootstrap] 모델 미학습 — 1/3 기본값 예측 진행 (SGD 부트스트랩 대기)")

        feat_vec = self.feature_builder.get_feature_vector(self.model.feature_names)

        # ── Phase 2: 호라이즌별 완성봉 기반 feat_vec 캐시 관리 ──────
        # _p2_completed는 STEP 4 끝에서 생성됨
        # 30m: 0.90→0.97 완화 — 0.90^22=0.098으로 방향성 신호가 22분 후 사실상 소멸해
        # 블렌딩이 FL로 수렴하는 문제 방지. 0.97^22=0.515로 절반 수준까지만 감쇠.
        _BAR_CACHE_DECAY = {3: 0.97, 5: 0.95, 10: 0.93, 15: 0.92, 30: 0.97}
        try:
            import numpy as _np_p2
            _fn = self.model.feature_names
            _H_MINS = {"1m": 1, "3m": 3, "5m": 5, "10m": 10, "15m": 15, "30m": 30}
            if _fn:
                # 1m 캐시: 매 분봉마다 현재 피처로 갱신
                _p2_1m_feats = self.feature_builder.build_for_horizon(bar, 1)
                self._hz_feat_cache["1m"] = _np_p2.array(
                    [_p2_1m_feats.get(n, 0.0) for n in _fn], dtype=float
                )
                self._hz_bar_age["1m"] = 0

                # N분봉 캐시: 완성 시 갱신, 미완성 시 나이 증가
                for _h_name, _h_min in list(_H_MINS.items()):
                    if _h_min == 1:
                        continue
                    _comp_bar = _p2_completed.get(_h_min)
                    if _comp_bar is not None:
                        _h_feats_p2 = self.feature_builder.build_for_horizon(_comp_bar, _h_min)
                        self._hz_feat_cache[_h_name] = _np_p2.array(
                            [_h_feats_p2.get(n, 0.0) for n in _fn], dtype=float
                        )
                        self._hz_bar_age[_h_name] = 0
                    else:
                        self._hz_bar_age[_h_name] = self._hz_bar_age.get(_h_name, 0) + 1

                # hz_feat_vecs: 캐시에서 로드, 없으면 Phase 1-1 반감기 fallback
                # Phase C: 캐시 벡터는 항상 전체 피처(_fn) 기준으로 저장
                #          모델 내부 predict_proba에서 호라이즌별 슬라이싱 수행
                _hz_feat_vecs = {}
                from features.feature_decay import get_horizon_features as _gHF
                for _h_name in HORIZONS:
                    if _h_name in self._hz_feat_cache:
                        _hz_feat_vecs[_h_name] = self._hz_feat_cache[_h_name]
                    else:
                        _hz_feat_vecs[_h_name] = _np_p2.array(
                            [_gHF(features, _h_name).get(n, 0.0) for n in _fn],
                            dtype=float,
                        )
            else:
                _hz_feat_vecs = None
        except Exception as _p2e:
            logger.debug("[Phase2-STEP5] 캐시 갱신 오류 — 기본 feat_vec 사용: %s", _p2e)
            _hz_feat_vecs = None

        if _gbm_ready:
            # ─ GBM + SGD + RF 블렌딩 (정상 경로) ─
            horizon_proba = self.model.predict_proba(
                feat_vec, monitor_ts=ts, hz_feat_vecs=_hz_feat_vecs
            )
            # [STEP5-P0 보완] GBM ready임에도 빈 예측 반환 — 조기 감지
            # ensemble.compute()의 P0가 conf=0.0으로 차단하지만,
            # 여기서 로그를 남겨 "어느 단계에서 비어있었는가"를 즉시 파악한다.
            if not horizon_proba:
                logger.warning(
                    "[STEP5] GBM ready=%s 이나 predict_proba()={} — 빈 예측 감지",
                    _gbm_ready,
                )
                log_manager.signal("[STEP5] predict_proba()={} — ensemble P0 방어 진입")
            _rf_ready = self.rf_model.is_ready()
            for h_name in list(horizon_proba.keys()):
                _sgd_fv_raw = _hz_feat_vecs[h_name] if _hz_feat_vecs else feat_vec
                # P0-SGD: 호라이즌별 피처 슬라이싱 — GBM과 동일한 피처셋으로 학습·예측 일치
                _sgd_h_idx  = getattr(self.model, "_hz_feat_indices", {}).get(h_name)
                _sgd_fv     = _sgd_fv_raw[_sgd_h_idx] if _sgd_h_idx is not None else _sgd_fv_raw
                _gbm_raw_conf = horizon_proba[h_name].get("confidence", 0.0)  # P2: blend 전 GBM conf
                sgd_p   = self.online_learner.predict_proba(h_name, _sgd_fv)
                blended = self.online_learner.blend_with_gbm(horizon_proba[h_name], sgd_p, h_name)
                # P6c: RF 블렌딩 — OOB 기반 동적 가중치
                # OOB < 0.45 (랜덤+12pp 미만): 해당 호라이즌 RF 제외
                # 3-class random=33%, OOB 45% 미만은 신호 약해 오히려 앙상블 오염
                if _rf_ready:
                    _oob_hz = self.rf_model.get_oob_scores().get(h_name, 0.0)
                    _w_rf = 0.30 if _oob_hz >= 0.45 else 0.0
                    if _w_rf > 0:
                        rf_p = self.rf_model.predict_proba_single(h_name, feat_vec)
                        if rf_p is not None:
                            blended = {
                                "up":   blended["up"]   * (1 - _w_rf) + rf_p["up"]   * _w_rf,
                                "down": blended["down"] * (1 - _w_rf) + rf_p["down"] * _w_rf,
                                "flat": blended["flat"] * (1 - _w_rf) + rf_p["flat"] * _w_rf,
                            }
                up, dn, fl = blended["up"], blended["down"], blended["flat"]
                best = max([(up, 1), (dn, -1), (fl, 0)], key=lambda t: t[0])
                horizon_proba[h_name] = {
                    "up": round(up, 4), "down": round(dn, 4), "flat": round(fl, 4),
                    "direction": best[1], "confidence": round(best[0], 4),
                }

                # [P2-진단] conf 고착 감지 — 3분+ 동일값이면 LEARNING 로그
                _curr_conf = horizon_proba[h_name]["confidence"]
                if abs(_curr_conf - self._conf_prev.get(h_name, -1.0)) < 1e-6:
                    self._conf_stuck[h_name] = self._conf_stuck.get(h_name, 0) + 1
                    if self._conf_stuck[h_name] >= 3:
                        _sgd_str = (
                            f"u={sgd_p['up']:.3f}/d={sgd_p['down']:.3f}/f={sgd_p['flat']:.3f}"
                            if sgd_p else "None"
                        )
                        log_manager.learning(
                            f"[CONF⚠] {h_name} conf={_curr_conf:.4f} "
                            f"{self._conf_stuck[h_name]}분 고착 | "
                            f"gbm_raw={_gbm_raw_conf:.4f} sgd={_sgd_str} "
                            f"bar_age={self._hz_bar_age.get(h_name, 0)}"
                        )
                else:
                    self._conf_stuck[h_name] = 0
                self._conf_prev[h_name] = _curr_conf

                # Phase 2: BAR_CACHE_DECAY — 봉 미완성 구간 신뢰도 감쇠
                _h_min_v = {"1m":1,"3m":3,"5m":5,"10m":10,"15m":15,"30m":30}.get(h_name, 1)
                _bar_age = self._hz_bar_age.get(h_name, 0)
                if _bar_age > 0 and _h_min_v > 1:
                    _decay_f = _BAR_CACHE_DECAY.get(_h_min_v, 1.0) ** _bar_age
                    horizon_proba[h_name]["confidence"] = round(
                        horizon_proba[h_name]["confidence"] * _decay_f, 4
                    )

                # [P2] FL 편향 고착 호라이즌 → uniform fallback (앙상블 오염 차단)
                if h_name in self._bias_override_horizons:
                    horizon_proba[h_name] = {
                        "up": round(1/3, 4), "down": round(1/3, 4),
                        "flat": round(1/3, 4), "direction": 0,
                        "confidence": round(1/3, 4),
                    }

            # [MaskedFallback] 격리 예측 SGD 블렌딩 (GBM 경로에서만 실행)
            _masked_hp_blended: dict = {}
            if self.model.last_masked_proba:
                for _hm, _gbm_m in self.model.last_masked_proba.items():
                    _sgd_m   = self.online_learner.predict_proba(_hm, feat_vec)
                    _blend_m = self.online_learner.blend_with_gbm(_gbm_m, _sgd_m, _hm)
                    _um, _dm, _fm = _blend_m["up"], _blend_m["down"], _blend_m["flat"]
                    _best_m = max([(_um, 1), (_dm, -1), (_fm, 0)], key=lambda t: t[0])
                    _masked_hp_blended[_hm] = {
                        "up": round(_um, 4), "down": round(_dm, 4), "flat": round(_fm, 4),
                        "direction": _best_m[1], "confidence": round(_best_m[0], 4),
                    }
        else:
            # ─ SGD-only 또는 bootstrap 경로 (GBM 미학습) ─
            horizon_proba = {}
            for h in HORIZONS:
                _sgd_fv = _hz_feat_vecs[h] if _hz_feat_vecs else feat_vec
                sgd_p = self.online_learner.predict_proba(h, _sgd_fv)
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
            _masked_hp_blended = {}  # SGD-only 경로: 격리 예측 미지원

        # scaler_monitor 행 — predict_proba()가 last_monitor_rows에 위임, 비동기 큐 투입
        # (파이프라인 타이밍 윈도우 밖에서 처리 → insert_events_batch 5초 블로킹 해소)
        _sm_rows = getattr(self.model, "last_monitor_rows", [])
        if _sm_rows:
            try:
                self._db_write_queue.put_nowait(("scaler_monitor", list(_sm_rows)))
            except _queue.Full:
                pass  # 모니터링 전용 — 유실 허용

        # ── [5순위] CORE Health Score 매분 업데이트 ───────────────────
        _cfs = self.feature_builder._core_fail_streak
        self.core_health.update(
            cvd_streak   = _cfs.get("cvd", 0),
            vwap_streak  = _cfs.get("vwap", 0),
            ofi_streak   = _cfs.get("ofi", 0),
            z_warn_count = getattr(self.model, "last_z_warn_count", 0),
        )

        # ── [4순위] MarketDNA — 장 시작 5분 피드 (09:00~09:04) ──────
        _dna_ts_hour = _ts_dt_obj.hour if hasattr(_ts_dt_obj, "hour") else 9
        _dna_ts_min  = _ts_dt_obj.minute if hasattr(_ts_dt_obj, "minute") else 0
        if _dna_ts_hour == 9 and _dna_ts_min < 5 and not self.market_dna.is_ready():
            _dna_dir    = 1 if bar.get("close", 0) > bar.get("open", 0) else (
                          -1 if bar.get("close", 0) < bar.get("open", 0) else 0)
            _dna_vol    = float(bar.get("volume", 0.0) or 0.0)
            _dna_z_warn = getattr(self.model, "last_z_warn_count", 0)
            _core_fs    = self.feature_builder._core_fail_streak
            _dna_core_ok = sum(1 for v in _core_fs.values() if v == 0)
            self.market_dna.add_bar(
                direction          = _dna_dir,
                volume             = _dna_vol,
                z_score_warn_count = _dna_z_warn,
                core_ok_count      = _dna_core_ok,
            )
        if _dna_ts_hour == 9 and _dna_ts_min == 5 and self.market_dna.is_ready():
            _dna_result = self.market_dna.diagnose()
            if _dna_result.get("caution"):
                log_manager.system(
                    f"[MarketDNA] 조심의 날 — 오전 사이즈 25% 고정 | {_dna_result['reason']}",
                    "WARNING",
                )

        # ── Phase B: 정기/강제 스케일러 refresh 트리거 ─────────────────
        # predict_proba 완료 후 last_extreme_features 가 갱신된 시점에 실행.
        # refit 자체는 daemon thread — 파이프라인 블로킹 없음.
        # P1-B: GBM 재학습 플래그 30분 타임아웃 — QTimer.singleShot 미실행 시 강제 해제
        _gbm_started = getattr(self, "_gbm_retrain_started_at", None)
        if (self._gbm_retrain_running and _gbm_started is not None
                and (_ts_dt_obj - _gbm_started).total_seconds() > 1800):
            logger.warning(
                "[GBM] 재학습 플래그 30분 타임아웃 강제 해제 (started=%s)",
                _gbm_started.strftime("%H:%M:%S"),
            )
            self._gbm_retrain_running = False
            self._gbm_retrain_started_at = None
        # P3: B_OPEN / C_PERIODIC은 GBM 재학습 여부와 무관하게 실행 허용
        # D_FORCE만 raw_data.db 동시 접근 17s 지연 방지를 위해 GBM 재학습 중 skip
        if (not self._scaler_refresh_running
                and not self._is_const_out_heavy_cooldown_active(_ts_dt_obj)):
            _extreme_feats_b = getattr(self.model, "last_extreme_features", [])
            _refresh_trig, _refresh_reason = self.model.check_refresh_trigger(
                _ts_dt_obj, _extreme_feats_b
            )
            if _refresh_trig:
                if _refresh_trig == "D_FORCE" and self._gbm_retrain_running:
                    pass  # D_FORCE: GBM 재학습 중 raw_data.db 동시 접근 방지
                else:
                    self._scaler_refresh_running = True  # 스레드 시작 전 선점 — 이중 트리거 방지
                    def _scaler_refresh_worker(
                        _trig=_refresh_trig, _rsn=_refresh_reason, _trigger_ts=ts
                    ):
                        try:
                            from config.settings import SCALER_WARMUP_LOOKBACK_BARS
                            _Xr, _fnr = self.batch_retrainer.load_features_for_warmup(
                                lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
                            )
                            if _Xr is not None:
                                self.model.refit_scalers_only(
                                    _Xr, _fnr,
                                    trigger_ts=_trigger_ts,
                                    trigger_type=_trig,
                                    trigger_reason=_rsn,
                                )
                        except Exception as _sr_e:
                            logger.warning("[ScalerRefresh] 실패: %s", _sr_e)
                        finally:
                            self._scaler_refresh_running = False
                    threading.Thread(target=_scaler_refresh_worker, daemon=True).start()

        # ── D_PRICE_MOMENTUM: 5분 가격 급변 기반 스케일러 즉시 트리거 ────
        # 기존 D_FORCE(z-score >4 탐지)는 장세 전환 후 약 20분 지연이 발생.
        # 가격 자체로 급변을 감지하면 전환 후 1~2분 내 스케일러를 재적합할 수 있다.
        # 6/2 실증: 13:39 급등 시작 → z-score 탐지 13:57 → 리프레시 13:59 (20분 지연).
        # 본 트리거가 있었다면 13:41~13:42에 즉시 실행 가능.
        #
        # 발동 조건:
        #   1. sigma_buf에 5봉+ 수익률 누적 (장 시작 5분 이후)
        #   2. 최근 5분 누적 수익률 절대값 > HORIZON_THRESHOLDS["5m"] × 100 × 2.5
        #      (5m 레이블 임계값의 2.5배 급변 = 약 0.23%p 이상)
        #   3. 쿨다운 20분 경과 (중복 리프레시 방지)
        #   4. 다른 리프레시 작업 미실행 중
        #
        # 쿨다운을 ConstOut(30분)보다 짧게(20분) 설정한 이유:
        #   가격 모멘텀은 추세 지속 중 연속적으로 발생할 수 있으며,
        #   30분 쿨다운이면 추세 중반 이후 스케일러를 다시 맞출 기회를 놓친다.
        if (not self._scaler_refresh_running
                and not self._gbm_retrain_running
                and not self._is_const_out_heavy_cooldown_active(_ts_dt_obj)):
            _n_sig_pm = len(self._sigma_buf)
            if _n_sig_pm >= 5:
                _ret_5m_pct = sum(list(self._sigma_buf)[-5:])   # 최근 5분 누적 수익률(%)
                _thr_5m_pct = (
                    runtime_settings.HORIZON_THRESHOLDS.get("5m", 0.00092) * 100 * 2.5
                )
                _pm_cooldown_ok = (
                    self._price_momentum_refit_until is None
                    or _ts_dt_obj >= self._price_momentum_refit_until
                )
                if abs(_ret_5m_pct) > _thr_5m_pct and _pm_cooldown_ok:
                    self._price_momentum_refit_until = (
                        _ts_dt_obj + datetime.timedelta(minutes=20)
                    )
                    log_manager.system(
                        f"[ScalerRefresh] 5분 누적 수익률 {_ret_5m_pct:+.3f}% "
                        f"(임계 ±{_thr_5m_pct:.3f}%) → D_PRICE_MOMENTUM 트리거 "
                        f"(쿨다운 20분)",
                        "WARNING",
                    )
                    self._scaler_refresh_running = True  # 스레드 시작 전 선점 — 이중 트리거 방지
                    def _pm_refit_worker(_tts=ts, _ret=_ret_5m_pct):
                        try:
                            from config.settings import SCALER_WARMUP_LOOKBACK_BARS
                            _Xpm, _fnpm = self.batch_retrainer.load_features_for_warmup(
                                lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
                            )
                            if _Xpm is not None:
                                self.model.refit_scalers_only(
                                    _Xpm, _fnpm,
                                    trigger_ts=_tts,
                                    trigger_type="D_FORCE",
                                    trigger_reason=f"price_momentum_5m={_ret:+.3f}%",
                                )
                        except Exception as _pm_e:
                            logger.warning(
                                "[ScalerRefresh] D_PRICE_MOMENTUM 실패: %s", _pm_e
                            )
                        finally:
                            self._scaler_refresh_running = False
                    threading.Thread(target=_pm_refit_worker, daemon=True).start()

        # ── STEP 6: 앙상블 진입 판단 ───────────────────────────
        _st.append(("S6", time.perf_counter()))
        _entry_horizon = None   # ATR 레짐별 진입 호라이즌 (STEP 6 말미에 확정)
        horizon_proba = self._apply_horizon_calibration(horizon_proba)
        _h_conf_values = [float(v.get("confidence", 0.0) or 0.0) for v in horizon_proba.values()]
        _gov_conf = (sum(_h_conf_values) / len(_h_conf_values)) if _h_conf_values else 0.0
        _gov_quality = float(features.get("feature_quality_score", 1.0) or 0.0)
        _gov_latency = float(getattr(self.latency_sync, "offset_sec", 0.0) or 0.0)
        _exec_gate_pre = self.execution_governor.evaluate(
            confidence=_gov_conf,
            quality_score=_gov_quality,
            latency_sec=_gov_latency,
            context={
                "regime": self.current_regime,
                "micro_regime": self.current_micro_regime,
                "ts": ts,
            },
        )
        # TrendPersistenceGate — ensemble.compute() 이전에 먼저 업데이트
        # (StuckBreaker가 TrendGate 상태를 참조하므로 순서가 중요)
        # UP:   above_vwap=1 AND cvd_direction=1  이 10분+ → UP  min_conf → 0.44
        # DOWN: above_vwap=0 AND cvd_direction=-1 이 10분+ → DN  min_conf → 0.44
        _tp = self.trend_gate.update(
            features, recent_bars=list(self._price_struct_buf)
        )
        # P4: 시간대 × 호라이즌 min_conf 필터링
        # OPEN_VOLATILE 구간 15m/30m처럼 해당 시간대에서 F1이 낮은 호라이즌 제외
        _zone_h_confs = get_horizon_min_confs(get_time_zone())
        if _zone_h_confs:
            _hp_conf_filtered = {
                h: v for h, v in horizon_proba.items()
                if float(v.get("confidence", 0.0) or 0.0)
                >= _zone_h_confs.get(h, 0.0)
            }
            # 최소 2개 이상 남아야 앙상블 의미 있음 — 부족 시 원래 사용
            if len(_hp_conf_filtered) >= 2:
                _excluded = sorted(set(horizon_proba) - set(_hp_conf_filtered))
                if _excluded:
                    logger.debug(
                        "[P4] 호라이즌 conf 필터: 제외=%s (시간대=%s)",
                        _excluded, get_time_zone(),
                    )
                horizon_proba = _hp_conf_filtered

        # 대시보드 체크박스 필터: 비활성 호라이즌은 앙상블 판정에서 제외
        _enabled_hz = None
        if getattr(self, "dashboard", None):
            try:
                _enabled_hz = self.dashboard._win.pred_panel.get_enabled_horizons()
            except Exception:
                pass
        _hp_ens = (
            {h: v for h, v in horizon_proba.items() if h in _enabled_hz}
            if _enabled_hz and len(_enabled_hz) < len(horizon_proba)
            else horizon_proba
        )
        _tz = get_time_zone()
        _zone_mc = get_zone_min_confidence(_tz)
        decision = self.ensemble.compute(
            _hp_ens,
            self.current_regime,
            features=features,
            adaptive_gating=True,
            acc30m=_acc30m,
            trend_gate_up_active=_tp["up_active"],
            trend_gate_dn_active=_tp["dn_active"],
            time_zone=_tz,
            active_horizons=self._get_active_horizons(
                _ts_dt_obj.hour * 100 + _ts_dt_obj.minute
                if hasattr(_ts_dt_obj, "hour") else 930
            ),
            zone_mc=_zone_mc,
        )
        direction  = decision["direction"]
        confidence = decision["confidence"]
        grade      = decision["grade"]
        self._last_ensemble_direction = direction  # Contrarian Mode 동방향 추적용

        # [MaskedFallback] 격리 예측 채택 — 정상 앙상블이 FLAT이고 격리 예측이 더 높을 때
        if direction == 0 and _masked_hp_blended and self.model.last_masked_features:
            _mhp_cal  = self._apply_horizon_calibration(_masked_hp_blended)
            _mhp_filt = {
                h: v for h, v in _mhp_cal.items()
                if float(v.get("confidence", 0.0)) >= _zone_h_confs.get(h, 0.0)
            } if _zone_h_confs else _mhp_cal
            _mhp_ens = (
                {h: v for h, v in _mhp_filt.items() if h in _enabled_hz}
                if _enabled_hz and len(_enabled_hz) < len(_mhp_filt)
                else _mhp_filt
            )
            if len(_mhp_ens) >= 2:
                _mdec  = self.ensemble.compute(
                    _mhp_ens, self.current_regime, features=features,
                    adaptive_gating=True, acc30m=_acc30m,
                    trend_gate_up_active=_tp["up_active"],
                    trend_gate_dn_active=_tp["dn_active"],
                    time_zone=_tz,
                    active_horizons=self._get_active_horizons(
                        _ts_dt_obj.hour * 100 + _ts_dt_obj.minute
                        if hasattr(_ts_dt_obj, "hour") else 930
                    ),
                    zone_mc=_zone_mc,
                )
                _mdir  = _mdec["direction"]
                _mconf = _mdec["confidence"]
                _gain  = _mconf - confidence
                if (_mdir != 0
                        and _gain >= self.model.MASKED_FALLBACK_CONF_GAIN):
                    _old_conf  = confidence
                    decision   = _mdec
                    direction  = _mdir
                    confidence = _mconf
                    grade      = decision["grade"]
                    log_manager.signal(
                        f"[MaskedFallback] {self.model.last_masked_features} 격리 "
                        f"→ conf {_old_conf:.1%}→{_mconf:.1%} "
                        f"dir={_mdir:+d} grade={grade}"
                    )

        # ── 상수 출력 호라이즌 감지 → 스케일러 재적합 트리거 ────────────
        # GBM이 동일 conf를 5분+ 출력하면 스케일러 노후로 모든 입력이 같은 리프에
        # 도달 중일 가능성이 높음 → 즉시 스케일러 재적합으로 분포 복원.
        # GBM 재학습(수분 소요)과 달리 스케일러만 재적합은 수초 이내 완료.
        # 쿨다운 30분: 재적합 중 또 다른 트리거로 중복 실행 방지.
        _const_hz = decision.get("const_output_horizons", [])
        # GBM 재학습 중이면 skip — raw_data.db 동시 접근 + CPU 경합 방지
        if _const_hz and not self._scaler_refresh_running and not self._gbm_retrain_running:
            _now_dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            _co_cooldown_ok = (
                self._const_out_refit_until is None
                or _now_dt >= self._const_out_refit_until
            )
            if _co_cooldown_ok:
                self._const_out_refit_until = (
                    _now_dt + datetime.timedelta(minutes=30)
                )
                self._start_const_out_heavy_cooldown(_now_dt, reason="const_output")
                self._scaler_refresh_running = True  # 스레드 시작 전 선점 — 이중 트리거 방지
                log_manager.system(
                    f"[ConstOut] {_const_hz} 상수 출력 확정 → 스케일러 재적합 시작",
                    "WARNING",
                )
                def _const_out_refit_worker(_hz=_const_hz, _tts=ts):
                    _refit_ok = False
                    try:
                        from config.settings import SCALER_WARMUP_LOOKBACK_BARS
                        _Xco, _fnco = self.batch_retrainer.load_features_for_warmup(
                            lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
                        )
                        if _Xco is not None:
                            self.model.refit_scalers_only(
                                _Xco, _fnco,
                                trigger_ts=_tts,
                                trigger_type="D_FORCE",
                                trigger_reason=f"const_output={_hz}",
                            )
                            _refit_ok = True
                    except Exception as _co_e:
                        logger.warning("[ConstOut] 스케일러 재적합 실패: %s", _co_e)
                    finally:
                        self._scaler_refresh_running = False
                    if _refit_ok:
                        # 재적합 완료 → 메인 스레드에서 acc30m 리셋 + GBM 재학습 예약
                        QTimer.singleShot(
                            0, lambda _h=_hz: self._on_const_out_refit_done(_h)
                        )
                threading.Thread(target=_const_out_refit_worker, daemon=True).start()

        # 앙상블 보정기: 현재 ts의 conf 캐시 (STEP 1에서 T-1m conf 조회용)
        # 1m 포함 여부 함께 저장 — 1m OFF 중에는 1m 결과로 앙상블 보정기 학습 불가
        self._ensemble_conf_cache[ts] = (float(confidence), "1m" in _hp_ens)
        if len(self._ensemble_conf_cache) > 35:
            self._ensemble_conf_cache.pop(min(self._ensemble_conf_cache), None)
        # 시간대·레짐 두 기준 중 더 엄격한 값으로 통일 (checklist·dashboard 공용)
        # _zone_mc는 ensemble.compute() 호출 전 계산됨 (cold-start zone_mc로 전달)
        actual_min_conf = max(
            decision.get("min_conf", _zone_mc),
            _zone_mc,
        )
        _zone_base_mc = actual_min_conf   # [P1] L2·TrendGate 적용 전 기준값 보존
        _tp_active = (
            (_tp["up_active"] and direction == 1) or
            (_tp["dn_active"] and direction == -1)
        )
        if _tp_active:
            _prev_mc = actual_min_conf
            actual_min_conf = min(actual_min_conf, _tp["min_conf_override"])
            if actual_min_conf < _prev_mc:
                _tp_label  = "UP" if direction == 1 else "DN"
                _tp_streak = _tp["up_streak"] if direction == 1 else _tp["dn_streak"]
                _ps_tag = " [가격구조부스트]" if _tp.get("price_boost_active") else ""
                log_manager.signal(
                    f"[TrendGate] {_tp_label} 추세 지속 {_tp_streak}분{_ps_tag}"
                    f" — min_conf {_prev_mc:.2f}→{actual_min_conf:.2f}"
                )
        # 대시보드 등급 카드 깜빡임: UP 상방 원웨이=녹색 / DN 하방 원웨이=오렌지
        _tp_dash_mode = (
            "UP" if _tp["up_active"] else
            "DN" if _tp["dn_active"] else ""
        )
        if getattr(self, "dashboard", None):
            self.dashboard.set_trend_gate_mode(_tp_dash_mode)
        # Layer 2 장중 전술 레짐 — min_conf 사전 상향 (사후 차단보다 먼저 적용)
        # DAY_RISK_OFF: +5%p / CRASH: +12%p / NORMAL: ±0
        # UI에서 L2 OFF 시 우회
        _l2_gate_on = getattr(self.dashboard, "is_layer2_gate_enabled", lambda: True)()
        _l2_mc_adj = self.intraday_regime.min_conf_adjust() / 100.0
        if _l2_gate_on and _l2_mc_adj > 0.0:
            actual_min_conf = min(0.90, actual_min_conf + _l2_mc_adj)
            log_manager.signal(
                f"[IntradayRegime] {self.current_intraday_regime} — min_conf +{_l2_mc_adj * 100:.0f}%p → {actual_min_conf:.2f}"
            )

        # ── Phase 1: feature_quality_score 기반 dynamic_mc 양방향 조정 ──
        # 피처 품질 우수(≥0.9) → 진입 문턱 낮춤(-3%p) / 불량(<0.6) → 강화(+5%p)
        # MC_ABS_FLOOR~MC_ABS_CEIL 범위 내 조정만 허용
        _fq_score = float(features.get("feature_quality_score", 0.5) or 0.5)
        _mc_floor = getattr(runtime_settings, "MC_ABS_FLOOR", 0.42)
        _mc_ceil  = getattr(runtime_settings, "MC_ABS_CEIL",  0.62)
        if _fq_score >= 0.9:
            _fq_adj = max(actual_min_conf - 0.03, _mc_floor)
            if _fq_adj < actual_min_conf:
                log_manager.signal(
                    f"[FQAdj] fq={_fq_score:.2f} → min_conf {actual_min_conf:.2f}→{_fq_adj:.2f} (완화)"
                )
                actual_min_conf = _fq_adj
        elif _fq_score < 0.6:
            _fq_adj = min(actual_min_conf + 0.05, _mc_ceil)
            if _fq_adj > actual_min_conf:
                log_manager.signal(
                    f"[FQAdj] fq={_fq_score:.2f} → min_conf {actual_min_conf:.2f}→{_fq_adj:.2f} (강화)"
                )
                actual_min_conf = _fq_adj

        # 호라이즌 방향 합의율: 6개 호라이즌 중 앙상블 최종 방향과 동일한 비율
        _hz_detail = decision.get("detail") or {}
        if _hz_detail:
            _hz_agree = sum(
                1 for _hd in _hz_detail.values()
                if isinstance(_hd, dict) and _hd.get("direction") == direction
            )
            _hz_agreement = _hz_agree / len(_hz_detail)
        else:
            _hz_agreement = 0.5

        # Checklist 선행 평가 — MetaGate checklist_grade 결정용
        # 체크리스트는 MetaGate와 독립(features만 사용) → FLAT 포지션 진입 후보 분에 한해 선행 실행
        # 결과(_pre_cr_cache)는 이후 STEP 7 체크리스트 절에서 재사용해 이중 계산 방지
        _pre_cl_grade = grade        # 기본: 앙상블 등급 (포지션 청산 감시 분 등은 이 값 유지)
        _pre_cr_cache = None
        if direction != DIRECTION_FLAT and self.position.status == "FLAT":
            if not self.model.is_in_startup_warmup(_ts_dt_obj):
                try:
                    _cl_min_conf_pre = actual_min_conf
                    if _l2_mc_adj > 0.0:
                        _cl_min_conf_pre = min(actual_min_conf, _zone_base_mc + 0.04)
                    if _tp_active:
                        _cl_min_conf_pre = min(_cl_min_conf_pre, _tp["min_conf_override"] + 0.02)
                    _pre_cr_cache = self.checklist.evaluate(
                        direction          = direction,
                        confidence         = confidence,
                        vwap_position      = features.get("vwap_position", 0),
                        cvd_direction      = _dir_sign(features.get("cvd_direction", 0)),
                        ofi_pressure       = int(features.get("ofi_pressure", 0)),
                        foreign_call_net   = features.get("foreign_call_net", 0),
                        foreign_put_net    = features.get("foreign_put_net", 0),
                        prev_bar_direction = (1 if bar.get("close", 0) > bar.get("open", 0)
                                              else (-1 if bar.get("close", 0) < bar.get("open", 0) else 0)),
                        time_zone          = _tz,
                        daily_loss_pct     = max(-self.position.daily_stats()["pnl_krw"], 0)
                                             / max(_ts_current_sizer_balance(self), 50_000_000),
                        min_confidence     = _cl_min_conf_pre,
                        bear_exhaustion    = float(features.get("bear_exhaustion", 0.0) or 0.0),
                        bull_exhaustion    = float(features.get("bull_exhaustion", 0.0) or 0.0),
                        micro_regime       = getattr(self, "current_micro_regime", "혼합"),
                        disabled_gates     = self.dashboard.get_disabled_gates(),
                        entry_horizon      = getattr(self, "_entry_horizon_pre", "1m") or "1m",
                        macro_vix          = float(features.get("macro_vix", 0.5) or 0.5),
                        opt_chain_pcr      = float(features.get("opt_chain_pcr", 0.0) or 0.0),
                    )
                    _pre_cl_grade = _pre_cr_cache.get("grade", grade)
                except Exception as _pre_cl_e:
                    logger.debug("[Checklist.pre] 선행 평가 실패, 앙상블 등급 사용: %s", _pre_cl_e)

        decision["meta_gate"] = self.meta_gate.evaluate(
            direction=direction,
            confidence=confidence,
            regime=self.current_regime,
            micro_regime=self.current_micro_regime,
            features=features,
            now=datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"),
            recent_accuracy=self.online_learner.recent_accuracy(),
            min_conf=actual_min_conf,
            horizon_agreement=_hz_agreement,
            checklist_grade=_pre_cl_grade,  # 체크리스트 선행 등급 (A/B/C/X)
            trend_gate_active=bool(_tp_active),   # ② TrendGate 편향패널티 비활성화
            time_zone=_tz,                        # ③ STABLE_TREND reduce_thr 완화
        )
        # selection bias 해소: skip된 비-FLAT 신호를 shadow 버퍼에 보존
        # → STEP 2에서 동일 ts 검증 결과 도착 시 record_outcome 처리
        if direction != DIRECTION_FLAT and decision["meta_gate"]["action"] == "skip":
            self._meta_shadow.setdefault(ts, []).append((
                decision["meta_gate"].get("meta_features", []),
                float(confidence),
            ))

        decision["toxicity_gate"] = self.toxicity_gate.evaluate(features)
        decision["execution_governor"] = _exec_gate_pre

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

        # ── 최적 진입 시점 게이트 (방법3 sigma 안정화 기준) ────────────
        _now_hm = datetime.datetime.now().strftime("%H%M")
        if _now_hm < "0920":
            # 09:00~09:19: sigma_20봉 미수집 → 진입 금지
            if direction != 0:
                direction = 0
                grade     = "X"
                log_manager.signal(
                    f"[EntryGate] sigma_20봉 미수집({len(self._sigma_buf)}봉) "
                    f"— 진입 대기 (09:20 해제)"
                )
        elif _now_hm < "0930":
            # 09:20~09:29: grade A만, min_conf 0.60 상향, size×0.5 (STEP 7에서 적용)
            if grade in ("B", "C"):
                direction = 0
                grade     = "X"
                log_manager.signal("[EntryGate] 조건부 구간 — A등급만 허용 (09:30까지)")
            elif grade == "A":
                actual_min_conf = max(actual_min_conf, 0.60)

        # GBM 첫 재학습(방법3 레이블) 완료 전 사이즈 축소 플래그
        # → STEP 7 진입 실행 시 size_mult 에 _pre_retrain_size_factor 곱함
        _pre_retrain_size_factor = (
            1.0 if self._pre_retrain_done
            else runtime_settings.PRE_RETRAIN_SIZE_MULT
        )

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

        self._refresh_shap_state(ts)
        if _gbm_ready and self._cached_shap_importance:
            _params_ui = {
                pname: self._cached_shap_importance.get(fname, 0.0)
                for pname, fname in _PARAM_FEAT_MAP.items()
            }
        _corr_str = self._get_param_corr_display()

        self.dashboard.update_prediction(close, _preds_ui, _params_ui, confidence,
                                         corr=_corr_str, min_conf=actual_min_conf,
                                         bar_ages=self._hz_bar_age)
        # [Qualify] 자격 현황 카드 갱신
        try:
            self.dashboard.update_qualification(self._horizon_runtime_state)
        except Exception:
            pass

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

        # ── ATR 레짐별 진입 호라이즌 선택 (2순위) ──────────────────
        # threshold_feasibility = atr / threshold_1m_pt (feature_builder에서 계산)
        # select_entry_horizon(tf, 1.0) 호출 시 내부에서 feasibility = tf / 1.0 = tf
        _tf = float(features.get("threshold_feasibility", 1.0))
        _entry_horizon = select_entry_horizon(_tf, 1.0)
        if _entry_horizon is None and direction != 0:
            log_manager.signal(
                f"[ATR-Horizon] tf={_tf:.2f} < 0.8 → 저변동성 진입 차단 "
                f"(ATR={atr:.3f})"
            )
            direction = 0
            grade = "X"
        elif direction != 0:
            log_manager.signal(
                f"[ATR-Horizon] 진입 호라이즌={_entry_horizon} tf={_tf:.2f} "
                f"→ TP1×{ATR_HORIZON_TP1_MULT.get(_entry_horizon, 1.0)}"
            )

        # ── Phase 1: 진입0 자동 원인 진단 ───────────────────────
        if direction == 0 or grade == "X":
            self._diagnose_zero_entry(features, horizon_proba, decision)

        # ── STEP 7: 진입 실행 ──────────────────────────────────
        _st.append(("S7", time.perf_counter()))
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
            # 재가동 cold-start 워밍업 — elapsed=infmin 이후 3분간 진입 차단
            if self.model.is_in_startup_warmup(_ts_dt_obj):
                _warmup_remain = int(
                    (self.model._startup_warmup_until - _ts_dt_obj).total_seconds() / 60.0
                ) + 1
                log_manager.signal(
                    "[StartupWarmup] 재가동 초기화 대기 중 — grade=X 강제 (약 %d분 남음)", _warmup_remain
                )
                _final_grade = "X"
                _cr = {
                    "grade": "X", "pass_count": 0, "checks": {},
                    "size_mult": 0, "auto_entry": False, "entry_mode": "STARTUP_WARMUP",
                }
            else:
                _disabled_gates = self.dashboard.get_disabled_gates()

                # [P1] Checklist 전용 min_conf — L2(CRASH/DAY_RISK_OFF) 페널티를 최대 +4%p로 제한.
                # actual_min_conf 는 앙상블 등급·대시보드용으로 L2 전량 포함한 채 유지한다.
                _checklist_min_conf = actual_min_conf
                if _l2_mc_adj > 0.0:
                    _checklist_min_conf = min(actual_min_conf, _zone_base_mc + 0.04)
                if _tp_active:
                    # TrendGate active: override + 2%p 상한 (101차 TrendBoost로 conf가 약간 높아지므로 여유 2%p)
                    _checklist_min_conf = min(_checklist_min_conf, _tp["min_conf_override"] + 0.02)
                # ① STABLE_TREND·LUNCH_RECOVERY 점심 추세 구간 min_conf 완화
                #    ConstOut 순환으로 conf=45~49% 고착 시 62% 기준이 모든 진입을 차단하는 문제 해소
                #    C등급 자동 진입은 별도 UI 토글로 제어 — 안전 장치 유지
                _trend_mc_zones = ("STABLE_TREND", "LUNCH_RECOVERY")
                if time_zone in _trend_mc_zones:
                    _trend_mc_cap = 0.48   # STABLE_TREND 구간 체크리스트 상한 (52%→48%)
                    # 근거: ConstOut 순환 시 conf=45~49%로 억제 → 52% 기준 전면 차단
                    # 48% = 랜덤(33%) + 15%p — 최소 신뢰도 보장선
                    if _checklist_min_conf > _trend_mc_cap:
                        _checklist_min_conf = _trend_mc_cap
                if _checklist_min_conf < actual_min_conf:
                    log_manager.signal(
                        f"[P1] Checklist min_conf 분리: {actual_min_conf:.2f}→{_checklist_min_conf:.2f}"
                        f" (L2={_l2_mc_adj*100:.0f}%p cap, TrendGate={'ON' if _tp_active else 'OFF'}"
                        f", zone={time_zone})"
                    )

                # MetaGate 선행 평가에서 캐시된 결과 재사용 (동일 입력 → 재계산 불필요)
                if _pre_cr_cache is not None:
                    _cr = _pre_cr_cache
                else:
                    _cr = self.checklist.evaluate(
                        direction         = direction,
                        confidence        = confidence,
                        vwap_position     = features.get("vwap_position", 0),
                        cvd_direction     = _dir_sign(features.get("cvd_direction", 0)),
                        ofi_pressure      = int(features.get("ofi_pressure", 0)),
                        foreign_call_net  = features.get("foreign_call_net", 0),
                        foreign_put_net   = features.get("foreign_put_net", 0),
                        prev_bar_direction = (1 if bar.get("close", 0) > bar.get("open", 0)
                                              else (-1 if bar.get("close", 0) < bar.get("open", 0) else 0)),
                        time_zone         = time_zone,
                        daily_loss_pct    = max(-self.position.daily_stats()["pnl_krw"], 0) / max(_ts_current_sizer_balance(self), 50_000_000),
                        min_confidence    = _checklist_min_conf,
                        bear_exhaustion   = float(features.get("bear_exhaustion", 0.0) or 0.0),
                        bull_exhaustion   = float(features.get("bull_exhaustion", 0.0) or 0.0),
                        micro_regime      = getattr(self, "current_micro_regime", "혼합"),
                        disabled_gates    = _disabled_gates,
                        entry_horizon     = _entry_horizon or "1m",
                        macro_vix         = float(features.get("macro_vix", 0.5) or 0.5),
                        opt_chain_pcr     = float(features.get("opt_chain_pcr", 0.0) or 0.0),
                    )

            # [Phase 1] cold-start 구간 최소 pass 수 강화 (HORIZON_COLDSTART_MIN_PASS)
            # 09:05~09:10: 7개 이상, 09:10~09:15: 6개 이상 — 활성 호라이즌이 제한된 구간의
            # 저품질 신호로 A등급 자동진입 방지
            if _cr and _cr.get("grade") not in ("X",):
                _hhmm_now = (
                    _ts_dt_obj.hour * 100 + _ts_dt_obj.minute
                    if hasattr(_ts_dt_obj, "hour") else 930
                )
                _cs_policy = getattr(runtime_settings, "HORIZON_COLDSTART_MIN_PASS", {})
                _cs_min_pass = None
                for (_cs_start, _cs_end), _cs_req in _cs_policy.items():
                    if _cs_start <= _hhmm_now < _cs_end:
                        _cs_min_pass = _cs_req
                        break
                if _cs_min_pass is not None and _cr["pass_count"] < _cs_min_pass:
                    log_manager.signal(
                        "[ColdStart] pass=%d < required=%d (%d~%d) → X등급 강등",
                        _cr["pass_count"], _cs_min_pass, _cs_start, _cs_end,
                    )
                    _cr = dict(_cr)
                    _cr["grade"]      = "X"
                    _cr["size_mult"]  = 0
                    _cr["auto_entry"] = False

            _final_grade = _cr["grade"]
            _checks_ui   = {_CHK_MAP.get(k, k): v for k, v in _cr["checks"].items()}
            # 섹션 8: grade=X 분봉 수 집계 (scaler_daily EOD용)
            if _final_grade == "X":
                self._grade_x_count += 1

            # [P3] 앙상블은 통과(C 이상)했지만 Checklist 신뢰도 항목에서 X로 강등된 경우 집계
            if (grade != "X" and _final_grade == "X"
                    and _cr.get("conf_check_failed", False)):
                self._checklist_conf_fail_count += 1
                log_manager.signal(
                    f"[P3] Checklist 신뢰도 차단 — 앙상블={grade} → X"
                    f" | 금일 누적 {self._checklist_conf_fail_count}회"
                )

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
                # [P4] CB③ RESTRICTED 단계: acc30m 저하 구간 → C등급 차단, A/B만 허용
                if _final_grade == "C" and self.circuit_breaker.is_grade_restricted():
                    log_manager.signal(
                        f"[CB③-P4] RESTRICTED(acc30m<{int(0.30*100)}%) — C등급 차단"
                        f" (acc30m={self.circuit_breaker.status_dict()['accuracy_30m']:.1%})"
                    )
                    _final_grade = "X"

                kelly_result = self.kelly.compute_fraction()
                # [5순위] CORE Health 차단 시 진입 스킵
                _core_health = getattr(self, "core_health", None)
                if _core_health and not _core_health.is_entry_allowed():
                    log_manager.signal(
                        f"[CoreHealth] 건강점수={_core_health.score} < 70 — 진입 차단"
                    )
                    _final_grade = "X"
                else:
                    pass
                size_result  = self.sizer.compute(
                    confidence          = confidence,
                    atr                 = atr,
                    regime              = self.current_regime,
                    grade_mult          = _cr["size_mult"],
                    adaptive_kelly_mult = kelly_result["multiplier"],
                    account_balance     = _ts_current_sizer_balance(self),
                    core_health_mult    = _core_health.size_mult if _core_health else 1.0,
                    brier_mult          = self.circuit_breaker.brier_size_mult,
                    restart_mult        = self.circuit_breaker.restart_size_mult,
                    dna_mult            = (self.market_dna.diagnose().get("size_mult", 1.0)
                                          if self.market_dna.is_ready() else 1.0),
                )
                _qty_display = size_result["quantity"]
                _qty_sizer_raw = _qty_display  # 게이트 조정 전 Sizer 원본값 보존

                # [DBG-F7b] 사이저 입력/출력 확인
                debug_log.debug(
                    "[DBG-F7b] sizer: conf=%.1f%% ATR=%.4f regime=%s "
                    "grade_mult=%.2f kelly_mult=%.2f → qty=%d",
                    confidence * 100, atr, self.current_regime,
                    _cr["size_mult"], kelly_result.get("multiplier", 1.0),
                    _qty_display,
                )

        # ── SHS: GAP_OPEN 기록 + Early Kill Switch 09:05 판정 ────
        if time_zone == "GAP_OPEN":
            # [P4] CORE 3개 중 2개 이상 통과 = core_ok (AND → 다수결)
            # GAP_OPEN은 거래량 부족·갭으로 1개 실패가 잦아 AND 조건이 EKS 과발동을 유발
            _core_votes = (
                int(bool(_cr is not None and _cr["checks"].get("3_vwap")))
                + int(bool(_cr is not None and _cr["checks"].get("4_cvd")))
                + int(bool(_cr is not None and _cr["checks"].get("5_ofi")))
            )
            _core_all_ok = _core_votes >= 2
            # [P2] 파이프라인 지연 분봉은 conf 신뢰 불가 — EKS conf_max에서 제외
            # _pipe_t0 기준 현재까지 경과시간으로 현재 분봉 지연 여부 판정
            _gap_pipe_delayed = (time.perf_counter() - _pipe_t0) * 1000 >= 1000
            self.system_health.record_gap_open_bar(
                conf=confidence,
                core_all_passed=_core_all_ok,
                pipeline_delayed=_gap_pipe_delayed,
            )
        elif not self.system_health._eks_evaluated:
            _eks_fired = self.system_health.evaluate_early_kill_switch(
                gap_open_mc=get_zone_min_confidence("GAP_OPEN"),
            )
            if _eks_fired:
                from utils.notify import notify_kill_switch as _nks
                _shs_d = self.system_health.to_dict()
                _nks(
                    gap_open_conf_max=_shs_d["gap_open_conf_max"],
                    gap_open_bars=_shs_d["gap_open_bars"],
                )
                log_manager.system(
                    "[SHS-EKS] Early Kill Switch 발동 — 당일 관망 선언. "
                    f"conf_max={_shs_d['gap_open_conf_max']*100:.1f}% bars={_shs_d['gap_open_bars']}",
                    "CRITICAL",
                )
                # [C2][P3] EKS 발동 원인 — 멀티 태그 복합 분류
                # 스케일러 노후·z경고·파이프라인 지연·P8 실패를 모두 체크해
                # 반복 패턴 추적에 사용한다.
                try:
                    _eks_causes = []
                    _eks_stale_h = self.model.canary_stale_age_hours()
                    if _eks_stale_h > 24.0:
                        _ss_eks = self._read_session_state()
                        _p8_ok_date = _ss_eks.get("p8_last_success_date", "")
                        _today = datetime.date.today()
                        _yesterday = _today - datetime.timedelta(days=1)
                        if _p8_ok_date != _yesterday.isoformat():
                            _dow = _today.weekday()  # 0=Mon
                            _eks_causes.append(
                                f"주말갭({_eks_stale_h:.0f}h)" if _dow == 0
                                else f"휴장/중단갭({_eks_stale_h:.0f}h)"
                            )
                        else:
                            _eks_causes.append(f"스케일러{_eks_stale_h:.0f}h노후")
                    # z경고 폭증 (Canary 최신값 — 인스턴스 변수로 보존)
                    _eks_z = getattr(self, "_last_canary_z_warn", 0)
                    if _eks_z >= 10:
                        _eks_causes.append(f"z경고{_eks_z}개")
                    # 파이프라인 지연 분봉 수
                    _eks_delayed = self.system_health._gap_open_delayed_count
                    if _eks_delayed >= 3:
                        _eks_causes.append(f"파이프라인지연{_eks_delayed}분")
                    # conf 미달 (항상 포함 — EKS 발동 1차 조건)
                    _eks_causes.append(f"conf{_shs_d['gap_open_conf_max']*100:.0f}%미달")
                    _eks_reason_str = "+".join(_eks_causes)
                    self.system_health._eks_reason = _eks_reason_str
                    log_manager.system(f"[SHS-EKS] 원인: {_eks_reason_str}", "WARNING")
                except Exception as _ek_re:
                    logger.debug("[SHS-EKS] 원인 추론 실패 (무시): %s", _ek_re)

        # [P3] EKS 동적 회복 — 30분 간격, 11:30 이전
        # 슬라이딩 윈도우에 conf 축적 후 can_attempt_recovery가 True이면 재평가
        if self.system_health.kill_switch_active:
            self._eks_recovery_conf_window.append(confidence)
            if self.system_health.can_attempt_recovery(ts_raw):
                _p3_scaler_age = self.model.canary_stale_age_hours()
                _p3_z_warn     = getattr(self, "_last_canary_z_warn", 0)
                _p3_window     = list(self._eks_recovery_conf_window)
                if self.system_health.try_eks_recovery(
                    _p3_scaler_age, _p3_window, actual_min_conf, _p3_z_warn
                ):
                    log_manager.system(
                        f"[SHS-EKS] EKS 자동 해제 확정 — 장중 진입 재개 "
                        f"scaler_age={_p3_scaler_age:.1f}h "
                        f"conf_window={[f'{c:.0%}' for c in _p3_window[-3:]]}",
                        "WARNING",
                    )

        # EKS 활성 시 매분 진입 차단 로그 (방향 있을 때만)
        if self.system_health.kill_switch_active and direction != 0:
            log_manager.signal("[SHS-EKS] 당일 관망 — 자동진입 차단")

        # 진입 패널 갱신 — 체크리스트 결과 + 산출 수량 (항상)
        _meta_gate = decision.get("meta_gate") or {}
        _meta_action = _meta_gate.get("action", "")
        _meta_size = float(_meta_gate.get("size_multiplier", 1.0) or 1.0)
        _tox_gate = decision.get("toxicity_gate") or {}
        _tox_action = _tox_gate.get("action", "pass")
        _tox_size = float(_tox_gate.get("size_multiplier", 1.0) or 1.0)
        _exec_gate = decision.get("execution_governor") or {}
        _exec_action = _exec_gate.get("action", "pass")
        _exec_size = float(_exec_gate.get("size_multiplier", 1.0) or 1.0)
        if direction != 0 and self.position.status == "FLAT":
            if self._health_degraded_mode:
                if confidence < float(HEALTH_DEGRADED_MIN_CONF):
                    _final_grade = "X"
                    _qty_display = 0
                    log_manager.signal(
                        f"[HealthPolicy] Degraded Mode 차단: conf={confidence:.1%} < {HEALTH_DEGRADED_MIN_CONF:.1%}"
                    )
                elif _qty_display > 0:
                    _qty_display = max(1, int(round(_qty_display * float(HEALTH_DEGRADED_SIZE_MULT))))
                    log_manager.signal(
                        f"[HealthPolicy] Degraded Mode 축소: size_mult={float(HEALTH_DEGRADED_SIZE_MULT):.2f}"
                    )
            # 방법3: GBM 첫 재학습 전 / 09:20~09:29 조건부 구간 사이즈 축소
            if _pre_retrain_size_factor < 1.0 and _qty_display > 0:
                _qty_display = max(1, int(round(_qty_display * _pre_retrain_size_factor)))
                log_manager.signal(
                    f"[EntryGate] 사이즈 축소 ×{_pre_retrain_size_factor:.1f} "
                    f"({'GBM 재학습 전' if not self._pre_retrain_done else '조건부 진입 구간'})"
                )

            if _exec_action == "block":
                _final_grade = "X"
                _qty_display = 0
            elif _qty_display > 0 and _exec_action == "reduce":
                _qty_display = max(1, int(round(_qty_display * _exec_size)))
            if _exec_action != "pass":
                log_manager.signal(
                    f"[ExecutionGovernor] action={_exec_action} score={_exec_gate.get('tradability_score', 0.0):.2f} "
                    f"size_mult={_exec_size:.2f} reason={_exec_gate.get('reason', '')}"
                )
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
            # Layer 2 사이즈 축소 — DAY_RISK_OFF=×0.5 / CRASH=×0.3 (마지막 단계 적용)
            # UI L2 OFF이면 우회
            if _l2_gate_on:
                _l2_size = self.intraday_regime.size_mult()
                if _l2_size < 1.0 and _qty_display > 0:
                    _qty_display = max(1, int(round(_qty_display * _l2_size)))
                    log_manager.signal(
                        f"[IntradayRegime] {self.current_intraday_regime} 사이즈 축소 "
                        f"×{_l2_size:.1f} → {_qty_display}계약"
                    )

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

        # ── P1-a: Restart Armistice ───────────────────────────────────────────
        _now_dt = datetime.datetime.now()
        _armistice_time_ok = (
            self._restart_armistice_until is None
            or _now_dt >= self._restart_armistice_until
        )
        _armistice_sync_ok = self._restart_armistice_sync_count >= 2
        _in_armistice = not (_armistice_time_ok and _armistice_sync_ok)
        if _in_armistice and _final_grade not in ("X",):
            _remain_sec = max(
                0,
                int((self._restart_armistice_until - _now_dt).total_seconds())
                if self._restart_armistice_until and _now_dt < self._restart_armistice_until
                else 0,
            )
            log_manager.signal(
                f"[Armistice] 재시작 유예 중 — 진입 차단 "
                f"(time_ok={_armistice_time_ok} sync={self._restart_armistice_sync_count}/2 "
                f"남은={_remain_sec}s)"
            )

        # ── P1-b: Position Integrity Checksum ─────────────────────────────────
        _integrity_ok = _ts_check_position_integrity(self)

        # ── P3-b: Reverse Entry Clamp ─────────────────────────────────────────
        _last_exit_dir = getattr(self, "_last_exit_direction", "")
        _last_exit_t   = getattr(self, "_last_exit_ts", None)
        _entry_dir_str = "LONG" if direction > 0 else "SHORT" if direction < 0 else ""
        _in_reverse_clamp = (
            bool(_last_exit_dir)
            and bool(_last_exit_t)
            and _entry_dir_str != ""
            and _entry_dir_str != _last_exit_dir
            and (_now_dt - _last_exit_t).total_seconds() < 180
        )
        if _in_reverse_clamp and _final_grade not in ("X",):
            _clamp_remain = int(180 - (_now_dt - _last_exit_t).total_seconds())
            log_manager.signal(
                f"[ReverseClamp] 청산 후 {_clamp_remain}s 이내 역방향({_last_exit_dir}→{_entry_dir_str}) 진입 금지"
            )
        _hurst_ok = features.get("hurst", 0.5) >= HURST_RANGE_THRESHOLD
        _atr_ok   = atr >= ATR_MIN_ENTRY   # ATR 너무 낮으면 노이즈 > 손절거리 → 휩쏘
        _hp = self._health_policy
        _auto_blocked, _deg_min_conf = self._is_degraded_entry_blocked(confidence, is_manual=False)
        _qty_auto = _qty_display
        if self._health_degraded_mode and _qty_auto > 0:
            _qty_auto = max(1, int(round(_qty_auto * float(_hp.get("degraded_size_mult", HEALTH_DEGRADED_SIZE_MULT)))))

        # 수익 보존 가드 체크 (STEP 7 진입 직전)
        _engine_daily_pnl_now = float(self.position.daily_stats().get("pnl_krw", 0.0) or 0.0)
        _broker_daily_pnl_now = None
        _daily_pnl_now = _engine_daily_pnl_now
        _daily_pnl_source = "engine"
        # Cybos는 브로커 요약(실현손익)과 엔진 누적값이 어긋날 수 있어, 당일 캐시가 있으면 우선 사용한다.
        if str(getattr(getattr(self, "broker", None), "name", "") or "").strip().lower() == "cybos":
            _today_key = datetime.date.today().isoformat()
            _cached_date = str(getattr(self, "_last_balance_realized_date", "") or "")
            _cached_realized = getattr(self, "_last_balance_realized_krw", None)
            if _cached_date == _today_key and _cached_realized is not None:
                try:
                    _broker_daily_pnl_now = float(_cached_realized)
                    _daily_pnl_now = _broker_daily_pnl_now
                    _daily_pnl_source = "broker"
                except Exception as _pnl_e:
                    logger.warning("[PnL] 브로커 일일손익 float 변환 실패 — 내부 추정값 사용: %s", _pnl_e)
        _size_mult_now = _cr["size_mult"] if _cr else 1.0
        _pg_allowed, _pg_reason = self.profit_guard.is_entry_allowed(
            _daily_pnl_now, _size_mult_now
        )
        if not _pg_allowed and _final_grade not in ("X",):
            _final_grade = "X"
            log_manager.signal(f"[ProfitGuard] 진입 차단: {_pg_reason}")
            _broker_str = "n/a" if _broker_daily_pnl_now is None else f"{_broker_daily_pnl_now:+,.0f}"
            log_manager.signal(
                f"[ProfitGuard][DebugPnL] source={_daily_pnl_source} used={_daily_pnl_now:+,.0f}원 "
                f"engine={_engine_daily_pnl_now:+,.0f}원 broker={_broker_str}원"
            )

        _hc_block = self.circuit_breaker.high_conf_entry_block(confidence)
        if _hc_block:
            log_manager.signal(
                f"[보호] 고신뢰 연속오답 {self.circuit_breaker._high_conf_wrong_streak}회 "
                f"(conf={confidence:.1%} ≥ {CB_HIGH_CONF_THRESHOLD:.0%}) — 신규 진입 차단",
                level="WARNING",
            )

        # ── Layer 2 장중 전술 레짐 진입 정책 적용 ──────────────────
        # DAY_RISK_OFF: 신규 롱 금지 | CRASH: 모든 신규 진입 금지
        # UI L2 OFF이면 게이트 우회 → 전 방향 허용
        if _l2_gate_on:
            _intraday_long_ok  = self.intraday_regime.is_long_allowed()
            _intraday_short_ok = self.intraday_regime.is_short_allowed()
        else:
            _intraday_long_ok  = True
            _intraday_short_ok = True
        _intraday_block = False
        if direction > 0 and not _intraday_long_ok:
            _intraday_block = True
            _final_grade = "X"
            log_manager.signal(
                f"[IntradayRegime] {self.current_intraday_regime} — 신규 롱 금지 "
                f"(day={self.intraday_regime._last_factors.get('day_ret', 0)*100:+.2f}%)",
                level="WARNING",
            )
        elif direction < 0 and not _intraday_short_ok:
            # CRASH 상태에서도 A등급 숏 추세추종은 예외 허용 (crash=숏이 맞는 방향)
            if self.intraday_regime.allow_crash_grade_a_short() and _final_grade == "A":
                log_manager.signal(
                    f"[IntradayRegime] CRASH — A등급 숏 추세추종 예외 허용 "
                    f"(day={self.intraday_regime._last_factors.get('day_ret', 0)*100:+.2f}%)",
                    level="WARNING",
                )
                # _intraday_block = False 유지 → 진입 허용, 사이즈는 CRASH size_mult=×0.3 적용됨
            else:
                _intraday_block = True
                _final_grade = "X"
                log_manager.signal(
                    f"[IntradayRegime] {self.current_intraday_regime} — 신규 숏 금지 "
                    f"(grade={_final_grade} day={self.intraday_regime._last_factors.get('day_ret', 0)*100:+.2f}%)",
                    level="WARNING",
                )

        entry_mode = "manual"
        if getattr(self, "dashboard", None) is not None:
            try:
                entry_mode = self.dashboard.get_entry_mode()
            except Exception:
                entry_mode = "manual"
        allowed_grades = {
            "auto":   ["A"],
            "hybrid": ["A", "B"],
            "manual": ["A", "B", "C"],
        }
        mode_filter_passed = _final_grade in allowed_grades.get(entry_mode, ["A", "B", "C"])

        _raw_entry_dir = "LONG" if direction > 0 else "SHORT" if direction < 0 else ""
        _resolved_raw_dir, _resolved_final_dir, _reverse_on = self._resolve_entry_direction(_raw_entry_dir)
        _raw_signal_ko = self._direction_to_korean(_resolved_raw_dir)
        _final_signal_ko = self._direction_to_korean(_resolved_final_dir)
        _checklist_grade = _cr["grade"] if _cr is not None else None
        _final_entry_ok = (
            _cr is not None
            and self.circuit_breaker.is_entry_allowed()
            and not _hc_block
            and is_new_entry_allowed()
            and not self._broker_sync_block_new_entries
            and not _in_cooldown
            and not _in_exit_cooldown
            and not _in_armistice
            and _integrity_ok
            and not _in_reverse_clamp
            and _hurst_ok
            and _atr_ok
            and mode_filter_passed
            and _qty_display > 0
            and not _bar_volume_zero
            and not _intraday_block
            and not self.system_health.kill_switch_active   # [SHS-EKS] 당일 관망일
        )

        # ── [DashboardHistory] STEP7 마스터 게이트 — 조건별 통과 여부 + 차단사유
        # "금일 Conf → 진입단계 추적" 카드가 과거 분봉의 진입 차단 원인을 그대로
        # 복원할 수 있도록 ensemble_decisions DB에 함께 저장한다 (STEP 9에서 사용).
        _gate_checks = {
            "cb_normal":        self.circuit_breaker.is_entry_allowed(),
            "hc_ok":            not _hc_block,
            "new_entry_time":   is_new_entry_allowed(),
            "broker_sync_ok":   not self._broker_sync_block_new_entries,
            "cooldown_ok":      not _in_cooldown,
            "exit_cooldown_ok": not _in_exit_cooldown,
            "armistice_ok":     not _in_armistice,
            "integrity_ok":     _integrity_ok,
            "reverse_clamp_ok": not _in_reverse_clamp,
            "hurst_ok":         _hurst_ok,
            "atr_ok":           _atr_ok,
            "mode_filter_ok":   mode_filter_passed,
            "qty_ok":           _qty_display > 0,
            "bar_volume_ok":    not _bar_volume_zero,
            "intraday_ok":      not _intraday_block,
            "kill_switch_ok":   not self.system_health.kill_switch_active,
        }

        _entry_block_reason = ""
        if direction != 0 and self.position.status == "FLAT":
            _cb_state = self.circuit_breaker.state
            if _cb_state != "NORMAL":
                _entry_block_reason = f"[차단] Circuit Breaker {_cb_state} — 진입 불가 (CB 해제까지 대기)"
            elif _hc_block:
                _entry_block_reason = (
                    f"[차단] 고신뢰 연속오답 {self.circuit_breaker._high_conf_wrong_streak}회 "
                    f"(conf={confidence:.1%}) — HC 차단"
                )
            elif self._broker_sync_block_new_entries:
                _entry_block_reason = f"[차단] 브로커 sync 미검증 상태 — 자동진입 금지 ({self._broker_sync_last_error})"
            elif _in_armistice:
                _entry_block_reason = (
                    f"[차단] Restart Armistice — 재시작 유예 중 "
                    f"(time_ok={_armistice_time_ok} sync={self._restart_armistice_sync_count}/2)"
                )
            elif not _integrity_ok:
                _entry_block_reason = (
                    f"[차단] 포지션 무결성 실패 (P1-b) — "
                    f"연속불일치={self._integrity_fail_count}회"
                )
            elif _in_cooldown:
                _remain = (self._entry_cooldown_until - datetime.datetime.now()).seconds
                _entry_block_reason = f"[차단] ENTRY 타임아웃 쿨다운 — {_remain}초 후 재진입 가능"
            elif _in_exit_cooldown:
                _remain = (self._exit_cooldown_until - datetime.datetime.now()).seconds
                _entry_block_reason = f"[차단] 청산 후 쿨다운 — {_remain}초 후 재진입 가능"
            elif _in_reverse_clamp:
                _clamp_remain = int(180 - (_now_dt - _last_exit_t).total_seconds())
                _entry_block_reason = (
                    f"[차단] Reverse Clamp (P3-b) — "
                    f"청산 후 역방향({_last_exit_dir}→{_entry_dir_str}) {_clamp_remain}s 이내 진입 금지"
                )
            elif _intraday_block:
                _idr = self.current_intraday_regime
                _idf = self.intraday_regime._last_factors
                _entry_block_reason = (
                    f"[차단] IntradayRegime {_idr} — "
                    f"{'롱' if direction > 0 else '숏'} 금지 "
                    f"(day={_idf.get('day_ret', 0)*100:+.2f}% "
                    f"ATR={_idf.get('atr_ratio', 0):.2f} "
                    f"z={_idf.get('z_warn_count', 0)})"
                )
            elif not _hurst_ok:
                _hurst_val = features.get("hurst", 0.5)
                _entry_block_reason = f"[차단] Hurst {_hurst_val:.3f} < {HURST_RANGE_THRESHOLD} — 횡보 레짐 진입 차단"
            elif not _atr_ok:
                _entry_block_reason = f"[차단] ATR {atr:.2f}pt < {ATR_MIN_ENTRY}pt — 변동성 부족 (휩쏘 위험)"
            elif not is_new_entry_allowed():
                _entry_block_reason = "[차단] 15:00 이후 — 신규 진입 금지 구간"
            elif _auto_blocked:
                _entry_block_reason = f"[차단] 자동진입 Degraded 최소신뢰도 {_deg_min_conf:.1%} 미달"
            elif not mode_filter_passed:
                _entry_block_reason = (
                    f"[차단] 모드필터 — {_final_grade}급 신호 vs {entry_mode} 모드"
                    f"({allowed_grades.get(entry_mode, ['A','B','C'])} 만 허용)"
                )
            elif _cr is None:
                _entry_block_reason = ""
            elif _final_grade == "X":
                _failed = [k for k, v in _cr["checks"].items() if not v]
                if "8_time" in _failed and time_zone == "OTHER":
                    _entry_block_reason = "[차단] 점심 휴식 구간 (11:50~13:00 OTHER) — 체크리스트 8_time 실패"
                elif "8_time" in _failed:
                    _entry_block_reason = f"[차단] 진입 금지 시간대 ({time_zone}) — 체크리스트 8_time 실패"
                else:
                    _entry_block_reason = f"[차단] 등급X — 미통과 항목: {', '.join(_failed)}"
            else:
                _entry_block_reason = ""

        _entry_executed_this_cycle = False

        self.dashboard.update_entry(
            _raw_signal_ko,
            confidence,
            _final_grade,
            _checks_ui,
            qty=_qty_display,
            final_signal=_final_signal_ko,
            reverse_enabled=_reverse_on,
            min_conf=actual_min_conf,
            ensemble_grade=grade,
            checklist_grade=_checklist_grade,
            final_entry=_final_entry_ok,
        )
        self._manual_entry_ctx = {
            "price": close,
            "qty":   _qty_display,
            "atr":   atr,
            "grade": _final_grade,
            "confidence": confidence,
        }

        if (
            _cr is not None
            and self.circuit_breaker.is_entry_allowed()
            and not _hc_block                      # 고신뢰 연속오답 사전 차단
            and is_new_entry_allowed()
            and not self._broker_sync_block_new_entries
            and not _in_cooldown                   # [B53] ENTRY 타임아웃 후 쿨다운
            and not _in_exit_cooldown              # 청산 후 즉각 재진입 차단
            and not _in_armistice                  # P1-a: 재시작 유예
            and _integrity_ok                      # P1-b: 포지션 무결성
            and not _in_reverse_clamp              # P3-b: 역방향 클램프
            and _hurst_ok                          # 횡보 레짐 진입 차단 (Hurst < 0.45)
            and _atr_ok                            # 변동성 너무 낮음 진입 차단
            and _final_grade not in ("X",)
            and _qty_display > 0
            and not _bar_volume_zero          # Guard-C3: volume=0 분봉 진입 차단
            and not _intraday_block           # Layer 2: DAY_RISK_OFF/CRASH 진입 금지
        ):
            dir_str = "LONG" if direction > 0 else "SHORT"
            raw_dir_str, final_dir_str, reverse_on = self._resolve_entry_direction(dir_str)
            raw_signal_ko = self._direction_to_korean(raw_dir_str)
            final_signal_ko = self._direction_to_korean(final_dir_str)
            
            # ── 2순위: 진입 모드 필터 (1순위 L2 체크 후) ──────────────────────────
            allowed_grades = {
                "auto":   ["A"],
                "hybrid": ["A", "B"],
                "manual": ["A", "B", "C"],
            }
            mode_filter_passed = _final_grade in allowed_grades.get(entry_mode, ["A", "B", "C"])
            
            if _cr["auto_entry"] and self._auto_entry_enabled:
                if _auto_blocked:
                    log_manager.signal(
                        f"[차단] 자동진입 Degraded 정책 차단 — conf={confidence:.1%} < {_deg_min_conf:.1%}"
                    )
                    log_manager.trade(
                        f"[자동진입 차단] {raw_dir_str}->{final_dir_str} {_qty_auto}계약 {_final_grade}급 "
                        f"(degraded_conf={confidence:.1%}, min={_deg_min_conf:.1%})"
                    )
                elif mode_filter_passed:
                    # EnsembleGater 온라인 학습을 위해 진입 시점 signals/direction 저장
                    self._last_gate_signals   = decision.get("gating", {}).get("signals", {})
                    self._last_gate_direction = direction
                    # P2-b: 셋업 컨텍스트 저장 (trade 기록 시 태그로 사용)
                    _hurst_now = float(features.get("hurst", 0.5) or 0.5)
                    self._entry_meta_action  = str(_meta_action or "")
                    self._entry_hurst_bucket = (
                        "trend"       if _hurst_now >= 0.55
                        else "neutral" if _hurst_now >= 0.45
                        else "mean-revert"
                    )
                    self._entry_hour_bucket  = datetime.datetime.now().hour
                    self._entry_was_restart  = 1 if self._session_no > 1 else 0
                    self._entry_had_partial  = 0   # 진입 시 초기화, 체결 후 갱신
                    # [SizerMatch] Sizer 제안 vs 실제 진입 수량 불일치 감지
                    _qty_sizer_raw_val = locals().get("_qty_sizer_raw", _qty_auto)
                    if _qty_sizer_raw_val != _qty_auto:
                        log_manager.signal(
                            f"[SizerMatch] sizer={_qty_sizer_raw_val}계약 → actual={_qty_auto}계약 "
                            f"(gap={_qty_sizer_raw_val - _qty_auto}) | "
                            f"kelly={kelly_result.get('multiplier', 1.0):.2f} "
                            f"meta={_meta_size:.2f} tox={_tox_size:.2f} exec={_exec_size:.2f}"
                        )
                    # 최대허용수량 클리핑 (산출수량 > 0인 경우에만, 최소 1 보장)
                    if _qty_auto > 0 and self._max_entry_qty > 0:
                        _qty_auto = max(1, min(_qty_auto, self._max_entry_qty))
                    # L2 통과 && 모드 필터 통과 → 진입
                    self._execute_entry(
                        final_dir_str, close, _qty_auto, atr, _final_grade,
                        raw_direction=raw_dir_str,
                        reverse_enabled=reverse_on,
                        entry_horizon=_entry_horizon,
                    )
                    _entry_executed_this_cycle = True
                else:
                    # 모드 필터 차단
                    log_manager.signal(
                        f"[모드필터] {_final_grade}급 신호 → {entry_mode} 모드({allowed_grades.get(entry_mode, ['A','B','C'])}) 불일치 — 진입 차단"
                    )
                    log_manager.trade(
                        f"[모드필터 차단] {raw_dir_str}->{final_dir_str} {_qty_auto}계약 {_final_grade}급 "
                        f"(모드={entry_mode}, 허용={allowed_grades.get(entry_mode, ['A','B','C'])})"
                    )
            elif (
                # [P5] C등급 실험적 자동 진입
                # OFF 기본값 — settings.ENTRY_GRADE_C_AUTO_EXP = True 로 명시 활성화 필요
                ENTRY_GRADE_C_AUTO_EXP
                and _final_grade == "C"
                and self._auto_entry_enabled
                and not _auto_blocked                              # Degraded 차단 없음
                and _tp_active                                     # TrendGate active + 방향 일치
                and time_zone in C_AUTO_EXP_ZONES                 # STABLE_TREND / LUNCH_RECOVERY
                and not self.circuit_breaker.is_grade_restricted() # P4 RESTRICTED 아님
            ):
                _qty_c_exp = max(1, int(round(_qty_auto * C_AUTO_EXP_SIZE_MULT)))
                if self._max_entry_qty > 0:
                    _qty_c_exp = max(1, min(_qty_c_exp, self._max_entry_qty))
                log_manager.signal(
                    f"[P5] C등급 실험 자동 진입 | {raw_dir_str}→{final_dir_str}"
                    f" {_qty_c_exp}계약 (size×{C_AUTO_EXP_SIZE_MULT})"
                    f" | zone={time_zone} TrendGate=ON conf={confidence:.1%}"
                )
                log_manager.trade(
                    f"[P5 자동진입] {raw_dir_str}->{final_dir_str} {_qty_c_exp}계약 @ {close} "
                    f"C급 실험 | TrendGate active"
                )
                self._execute_entry(
                    final_dir_str, close, _qty_c_exp, atr, _final_grade,
                    raw_direction=raw_dir_str,
                    reverse_enabled=reverse_on,
                    entry_horizon=_entry_horizon,
                )
                _entry_executed_this_cycle = True

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
        # _entry_block_reason은 위(_final_entry_ok 계산 직후)에서 동일 우선순위로 산출됨
        if direction != 0 and self.position.status == "FLAT":
            if _entry_block_reason and _entry_block_reason != self._last_block_reason:
                log_manager.signal(_entry_block_reason)
                self._last_block_reason = _entry_block_reason
        elif direction == 0 or self.position.status != "FLAT":
            self._last_block_reason = ""

        # ── STEP 8: 청산 트리거 감시 ───────────────────────────
        _st.append(("S8", time.perf_counter()))
        if self.position.status != "FLAT":
            self._check_exit_triggers(close, features, decision, bar)

        # ── 청산 패널 갱신 (매분 — 실제 PositionTracker 값 전달) ──
        _pos = self.position
        _pending = self._pending_order or {}
        _pending_kind = str(_pending.get("kind") or "")
        _pending_reason = str(_pending.get("reason") or "")
        _now = datetime.datetime.now()
        _force_dt = datetime.datetime.combine(_now.date(), self.time_exit.FORCE_EXIT)
        _time_left_s = int((_force_dt - _now).total_seconds())
        if _time_left_s < 0:
            _time_left_s = 0
        self.dashboard.update_position({
            "status":     _pos.status,
            "entry":      _pos.entry_price,
            "current":    close,
            "qty":        _pos.quantity,
            "pt_value":   self._pt_value,
            "atr":        atr,
            "stop":       _pos.stop_price,
            "trail_basis": _pos.get_trailing_reference_price(close, atr),
            "tp1":        _pos.tp1_price,
            "tp2":        _pos.tp2_price,
            "tp3":        _pos.tp3_price,
            "partial1":   _pos.partial_1_done,
            "partial2":   _pos.partial_2_done,
            "partial3":   _pos.partial_3_done,
            "stage_plan": _pos.get_stage_plan(),
            "entry_time": _pos.entry_time,
            "pending_active": bool(_pending),
            "pending_kind": _pending_kind,
            "pending_reason": _pending_reason,
            "pending_stage": int(_pending.get("stage") or 0),
            "pending_filled": int(_pending.get("filled_qty") or 0),
            "pending_qty": int(_pending.get("qty") or 0),
            "time_exit_countdown_sec": _time_left_s,
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

        # 주문/체결 탭 메트릭 갱신 (LatencySync — Cybos에서는 항상 0ms)
        _ls = self.latency_sync.summary()
        _latency_ms = float(_ls.get("offset_ms", 0.0) or 0.0)
        self.dashboard.update_order_metrics(
            trades      = _ds["trades"],
            avg_lat_ms  = _latency_ms,
            peak_lat_ms = _ls["peak_ms"],
            samples     = _ls["sample_count"],
        )
        # 파이프라인 처리시간 (CB⑤ 대체 지표) — 헬스 패널·SYSTEM 로그 공용
        _st.append(("end", time.perf_counter()))
        _pipe_ms = (_st[-1][1] - _pipe_t0) * 1000
        # P5: 전 단계 분해 문자열 — CB임박/WARN 양쪽에서 재사용
        # [라벨 수정] 마커는 각 STEP "시작" 지점에 찍힌다(예: S2 마커 = STEP2 시작).
        # 따라서 구간 _st[i-1]→_st[i]의 실제 소요시간은 "_st[i-1]에 적힌 STEP"의 본문이다
        # (예: S1마커→S2마커 구간 = STEP1(검증) 본문, 종전엔 이를 "S2"로 오표기해
        #  STEP1의 verify_and_update() 정체를 STEP2(SGD)로 오인하게 만들었음).
        # start 마커는 STEP1 진입 전 준비 구간이므로 "S0"으로 표기.
        _all_steps_str = " ".join(
            f"{_st[i-1][0] if _st[i-1][0] != 'start' else 'S0'}="
            f"{(_st[i][1] - _st[i-1][1]) * 1000:.0f}ms"
            for i in range(1, len(_st))
        )
        _retrain_tag_pipe = (
            " [GBM재학습중]" if self.circuit_breaker._gbm_retrain_active else ""
        )
        if _pipe_ms >= HEALTH_LATENCY_CRIT_MS:
            # CB⑤ 발동 임계값 이상 — 전 단계 무조건 출력 (진단용)
            _pipeperf_msg = (
                f"[PipePerf][CB임박]{_retrain_tag_pipe} "
                f"total={_pipe_ms:.0f}ms | {_all_steps_str or '─'}"
            )
            logger.warning(_pipeperf_msg)
            log_manager.system(_pipeperf_msg, "WARNING")  # SYSTEM 로그에도 기록 — 진단 가시성
        elif _pipe_ms > HEALTH_LATENCY_WARN_MS:
            # P5: 경고 수준도 전 단계 분해 출력 (100ms+ 필터 제거 — 병목 단계 특정에 필요)
            _pipeperf_warn_msg = (
                f"[PipePerf]{_retrain_tag_pipe} "
                f"total={_pipe_ms:.0f}ms | {_all_steps_str or '─'}"
            )
            logger.warning(_pipeperf_warn_msg)
            log_manager.system(_pipeperf_warn_msg, "WARNING")
        self._emit_runtime_health(features, _pipe_ms)

        # ── SHS: S2 latency + CORE pass rate 업데이트 + 대시보드/슬랙 ──
        _s2_dur_sec = 0.0
        for _i in range(1, len(_st)):
            if _st[_i][0] == "S3":
                _s2_dur_sec = max(0.0, _st[_i][1] - _st[_i - 1][1])
                break
        self.system_health.update_s2_latency(_s2_dur_sec)

        _core_pass_cnt = sum(
            1 for k in ("3_vwap", "4_cvd", "5_ofi")
            if (_cr is not None and bool(_cr["checks"].get(k)))
        ) if _cr is not None else 0
        self.system_health.update_core_pass(_core_pass_cnt / 3.0)

        _shs_state = self.system_health.to_dict()
        self.dashboard.update_shs_badge(
            shs=_shs_state["shs"],
            entry_blocked=_shs_state["entry_blocked"],
            kill_switch=_shs_state["kill_switch_active"],
            eks_reason=getattr(self.system_health, "_eks_reason", ""),
        )
        self.dashboard.update_shadow_badge(
            state        = self.shadow_session.state,
            acc30m       = _contra_acc30m,        # pred_buffer 기반 (CB보다 빠르게 갱신)
            core_health  = self.core_health.score,
            z_warn_count = sum(self._z_warn_5m),  # state 무관 5분 롤링 버퍼
        )
        if self.system_health.should_send_alert():
            from utils.notify import notify_shs_alert as _nsa
            _nsa(shs=_shs_state["shs"], components=_shs_state)

        # ── STEP 9: 예측 DB 저장 (배치 — 1연결 트랜잭션) ──────────
        # STEP7 마스터 게이트 결과 — 대시보드 "진입단계 추적" 카드 복원용
        decision["entry_gate"]         = _gate_checks
        decision["entry_final_ok"]     = bool(_final_entry_ok)
        decision["entry_qty"]          = int(_qty_display)
        decision["entry_mode"]         = entry_mode
        decision["entry_executed"]     = bool(_entry_executed_this_cycle)
        decision["entry_block_reason"] = _entry_block_reason

        _feat_clean = {k: round(float(v), 4) for k, v in features.items()
                       if v is not None and v == v}
        try:
            self.pred_buffer.save_step9_batch(
                ts            = ts,
                sigma_at_t    = self._sigma_20,
                horizon_proba = horizon_proba,
                features_clean= _feat_clean,
                regime        = self.current_regime,
                micro_regime  = self.current_micro_regime,
                decision      = decision,
            )
        except Exception as e:
            logger.warning("[STEP9] save_step9_batch 오류 (스킵): %s", e)

        # ── [S2-A] 지연 SGD 학습 — 파이프라인 크리티컬 경로 밖에서 실행 ──
        # online_learner.learn() 을 "end" 이후로 이동 → _pipe_ms 에 포함 안 됨
        # GBM 배치 재학습 중 5~7s 지연이 파이프라인 CB 를 트리거하던 문제 해소
        _sgd_deferred_t0 = time.perf_counter()
        if self.model.feature_names and _sgd_deferred_verified:
            if _sgd_deferred_stuck:
                log_manager.learning(
                    f"[SGD] stuck 발생 분봉 — {len(_sgd_deferred_verified)}건 학습 스킵 (레이블 오염 방지)"
                )
            else:
                _sgd_h_indices = getattr(self.model, "_hz_feat_indices", {})
                _min_conf_sgd  = 0.52   # P2-D: 저신뢰 레이블 오염 차단
                for _dv in _sgd_deferred_verified:
                    # P2-D: 고신뢰도 필터 — conf < 0.52 예측 결과는 학습 제외
                    if float(_dv.get("confidence", 0.0)) < _min_conf_sgd:
                        continue
                    _dfeat = _dv.get("features") or {}
                    _dx_full = np.array(
                        [_dfeat.get(f, 0.0) for f in self.model.feature_names],
                        dtype=np.float32,
                    )
                    # P0-SGD: 호라이즌별 피처 슬라이싱 — GBM과 동일한 피처셋 사용
                    _hz_learn = _dv["horizon"]
                    _h_idx_learn = _sgd_h_indices.get(_hz_learn)
                    _dx_learn = _dx_full[_h_idx_learn] if _h_idx_learn is not None else _dx_full
                    self.online_learner.learn(
                        horizon         = _hz_learn,
                        x               = _dx_learn,
                        actual_label    = _dv["actual"],
                        predicted_label = _dv["predicted"],
                    )
            log_manager.learning(
                f"[SGD] {len(_sgd_deferred_verified)}건 학습 | "
                f"SGD비중={self.online_learner.sgd_weight:.0%} "
                f"50분정확도={self.online_learner.recent_accuracy():.1%}"
            )
            # [Qualify] trained_cycles 동기화 — online_learner._horizon_counts 반영
            _hc = getattr(self.online_learner, "_horizon_counts", {})
            _need = getattr(runtime_settings, "HORIZON_QUALIFY_MIN_CYCLES", 3)
            for _h, _cnt in _hc.items():
                if _h not in self._horizon_runtime_state:
                    continue
                _qs = self._horizon_runtime_state[_h]
                _qs["trained_cycles"] = _cnt
                if _qs["verified_cycles"] >= _need and _qs["trained_cycles"] >= _need:
                    if not _qs["qualified"]:
                        _qs["qualified"] = True
                        _qs["active"]    = True
                        _qs["status"]    = "active"
                        log_manager.signal(
                            f"[Qualify] {_h} 자격 획득 "
                            f"(verified={_qs['verified_cycles']} trained={_qs['trained_cycles']})"
                        )
        _sgd_deferred_ms = int((time.perf_counter() - _sgd_deferred_t0) * 1000)
        if _sgd_deferred_ms > 500:
            debug_log.debug(
                "[SGD-deferred] %dms verified=%d (크리티컬 경로 외)",
                _sgd_deferred_ms, len(_sgd_deferred_verified),
            )
            if _sgd_deferred_ms > 2000:
                logger.warning(
                    "[SGD-deferred] %dms — 다음 분봉 전 완료 필요 (verified=%d)",
                    _sgd_deferred_ms, len(_sgd_deferred_verified),
                )

        # ── 챔피언-도전자 Shadow 실행 (STEP 9 이후 훅) ─────────
        if self.challenger_engine is not None:
            _ctx = {
                "ts":     ts,
                "atr":    features.get("atr", 1.0),
                "regime": self.current_micro_regime,
                "candle": bar if isinstance(bar, dict) else {},
            }
            self.challenger_engine.run_shadow(features, _ctx.get("candle", {}), _ctx)

        # ── CB⑤ 파이프라인 지연 감시 + CB 배지 매분 갱신 ─────────
        self.circuit_breaker.record_pipe_latency(_pipe_ms)
        try:
            self.dashboard.update_system_status(
                cb_state=self.circuit_breaker.state,
                latency_ms=_pipe_ms,
                accuracy=_acc30m,
                cb3_samples=_cb_status.get("cb3_samples", 0),
            )
        except Exception as _ds_e:
            logger.debug("[Dashboard] update_system_status 실패: %s", _ds_e)

        # ── 창5 모델 AI 카드 갱신 ──────────────────────────────
        try:
            _ol = self.online_learner
            self.dashboard.update_model_cards(
                accuracy=_ol.recent_accuracy(),
                sgd_weight=_ol.sgd_weight,
                is_active=any(_ol._fitted.values()),
            )
        except Exception as _mc_e:
            logger.debug("[Dashboard] update_model_cards 실패: %s", _mc_e)

        # ── L2 Tier Gate 영구중단 배지 갱신 ────────────────────
        try:
            l2_info = self.profit_guard.get_l2_halt_info(_daily_pnl_now)
            self.dashboard.update_l2_halt_badge(
                is_halted=l2_info['is_halted'],
                threshold=l2_info['halt_threshold']
            )
        except Exception as _l2_e:
            logger.debug("[Dashboard] L2 배지 갱신 실패: %s", _l2_e)

        if not self._is_const_out_heavy_cooldown_active(_ts_dt_obj):
            # 🧠 자가학습 모니터 패널 갱신 (매분)
            self.dashboard.update_learning(self._gather_learning_stats())

            # 🎯 학습 효과 검증기 패널 갱신 (5분마다 — DB 쿼리 비용 분산)
            self._efficacy_tick += 1
            if self._efficacy_tick % 5 == 1:   # 첫 분 + 이후 5분마다
                self.dashboard.update_efficacy(self._gather_efficacy_stats())
        else:
            logger.debug("[PipePerf] heavy dashboard refresh deferred by ConstOut cooldown")

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
            self._send_broker_exit_order(total_qty)
            result = self.position.close_position(price, f"TP{stage}(전량)")
            self._post_exit(result)
            return

        self._send_broker_exit_order(partial_qty)
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

    # [SERVICE-BOUNDARY 3/4] OrderLifecycleService
    # 책임: 진입/청산 주문 전송, pending 상태관리, 체결결과 반영
    # 입력: direction/qty, _futures_code, account_no, broker API
    # 출력: broker ret code, pending state, 포지션/로그 동기화
    def _send_broker_entry_order(self, direction: str, qty: int) -> int:
        """선물 진입 시장가 주문. 0=성공, 음수=오류"""
        code = getattr(self, "_futures_code", "")
        if not code:
            return -1
        account_no = self._get_active_account_no()
        if not account_no:
            return -1
        side = "BUY" if direction == "LONG" else "SELL"
        return self.broker.send_market_order(
            account_no=account_no,
            code=code,
            side=side,
            qty=qty,
            rqname="진입",
            screen_no="1000",
        )

    def _send_broker_exit_order(self, qty: int) -> int:
        """선물 청산 시장가 주문. 0=성공, 음수=오류, -99=BlockRequest 타임아웃"""
        code = getattr(self, "_futures_code", "")
        if not code or self.position.status == "FLAT":
            return -1
        account_no = self._get_active_account_no()
        if not account_no:
            return -1
        side = "SELL" if self.position.status == "LONG" else "BUY"
        ret = self.broker.send_market_order(
            account_no=account_no,
            code=code,
            side=side,
            qty=qty,
            rqname="청산",
            screen_no="1001",
        )
        # -99: BlockRequest 타임아웃 — 청산 주문 상태 불명, CB API지연 트리거 발동
        if ret == -99:
            log_manager.system(
                f"[ExitOrder] BlockRequest 타임아웃(-99) — 청산 주문 상태 불명! "
                f"CB API지연 트리거 발동. code={code} qty={qty} side={side}",
                "ERROR",
            )
            try:
                self.circuit_breaker.check_api_delay(10.0)  # CB 트리거 ⑤
            except Exception as _cb_delay_e:
                logger.warning("[CB] check_api_delay 예외 (스킵): %s", _cb_delay_e)
        return ret

    def _execute_entry(
        self, direction: str, price: float,
        quantity: int, atr: float, grade: str,
    ):
        """진입 실행"""
        if not self.dashboard.is_server_match():
            log_manager.system(
                "[Entry] 서버 모드 불일치 — 라디오 버튼 선택과 실접속 서버가 다릅니다. 진입 차단.",
                "WARNING",
            )
            return
        ret = self._send_broker_entry_order(direction, quantity)
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
            self._send_broker_exit_order(self.position.quantity)
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
            self._send_broker_exit_order(self.position.quantity)
            result = self.position.close_position(price, "15:10 강제청산")
            self._post_exit(result)

    def _post_exit(self, result: dict, filled_at=None):
        """청산 후 처리.
        filled_at: Cybos Chejan 콜백에서 전달된 실제 체결 시각 (None이면 now() 사용)
        """
        pnl = result["pnl_pts"]
        was_correct = pnl > 0
        if was_correct:
            self.circuit_breaker.record_win()
            self.kelly.record(win=True, pnl_pts=pnl)
        else:
            self.circuit_breaker.record_stop_loss()
            self.kelly.record(win=False, pnl_pts=pnl)
        # EnsembleGater 온라인 가중치 갱신 — 진입 시 저장된 gate signals 사용
        if self._last_gate_signals and self._last_gate_direction != 0:
            try:
                self.ensemble.record_trade_outcome(
                    was_correct=was_correct,
                    signals=self._last_gate_signals,
                    direction=self._last_gate_direction,
                )
            except Exception as _ge:
                logger.debug("[EnsembleGater] record_outcome 오류: %s", _ge)
            self._last_gate_signals = {}
            self._last_gate_direction = 0
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
        # [Fix2] filled_at 우선 사용 — Cybos 비동기 경로에서 실제 체결 시각으로 마커 위치 정확화
        self.dashboard.minute_chart_record_exit(
            result["exit_price"],
            filled_at or datetime.datetime.now(),
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

        # 예측 버퍼 기반 호라이즌별 최근 정확도 (실제 검증 정확도)
        buf_acc = {hz: self.pred_buffer.recent_accuracy(hz, 50)
                   for hz in ["1m", "3m", "5m", "10m", "15m", "30m"]}

        # SGD 호라이즌별 정확도 (P1-B: 호라이즌별 독립 가중치 대응)
        bucket_acc = ol.recent_accuracy_by_bucket()  # short/long 평균 — 하위 호환 로그용
        h_acc = {
            hz: ol.horizon_accuracy(hz)
            for hz in ol._fitted
        }

        # CB③ 30분 정확도
        cb_status = self.circuit_breaker.status_dict()

        last_ev = ""
        if self._verified_today > 0:
            acc = ol.recent_accuracy()
            last_ev = (
                f"{datetime.datetime.now().strftime('%H:%M')} | "
                f"검증 {self._verified_today}건 누적 · "
                f"SGD S:{bucket_acc['short']:.1%} L:{bucket_acc['long']:.1%} · "
                f"CB③ {cb_status['accuracy_30m']:.1%}"
            )

        return {
            "verified_today":    self._verified_today,
            "sgd_accuracy_50m":  ol.recent_accuracy(),
            "sgd_acc_short":     bucket_acc["short"],
            "sgd_acc_long":      bucket_acc["long"],
            "sgd_weight":        ol.sgd_weight,
            "gbm_weight":        ol.gbm_weight,
            "sgd_fitted":        dict(ol._fitted),
            "sgd_sample_counts": dict(ol._horizon_counts),
            "horizon_accuracy":  h_acc,
            "buffer_accuracy":   buf_acc,
            "cb_accuracy_30m":   cb_status["accuracy_30m"],
            "cb_samples":        cb_status["cb3_samples"],
            "cb_streak":         cb_status["high_conf_wrong_streak"],
            "gbm_last_retrain":  gbm["last_retrain"],
            "gbm_retrain_count": gbm["retrain_count"],
            "raw_candles_count": raw,
            "last_event":        last_ev,
            **self._load_effect_report_metrics(),
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

    def _load_effect_report_metrics(self) -> dict:
        """A/B·Calibration·Meta Gate·Rollout 리포트 JSON 일괄 로드.

        LearningPanel(자가학습)·EfficacyPanel(효과 검증) 양쪽 모두
        동일한 리포트 탭(A/B, Calibration, Meta Gate, Rollout)을 표시하므로
        로딩 로직을 한 곳에서 공유해 두 패널 간 데이터 불일치를 방지한다.
        """
        report_history = self._load_json_file(EFFECT_MONITOR_HISTORY_PATH)
        if not isinstance(report_history, list):
            report_history = []
        return {
            "ab_metrics": self._load_json_file(os.path.join(BASE_DIR, "microstructure_ab_metrics.json")),
            "calibration_metrics": self._load_json_file(os.path.join(BASE_DIR, "calibration_metrics.json")),
            "meta_metrics": self._load_json_file(os.path.join(BASE_DIR, "meta_gate_tuning_metrics.json")),
            "rollout_metrics": self._load_json_file(os.path.join(BASE_DIR, "rollout_readiness_metrics.json")),
            "report_history": report_history,
        }

    def _run_effect_report_script(self, script_name: str, *args: str) -> bool:
        script_path = os.path.join(BASE_DIR, "scripts", script_name)
        try:
            result = subprocess.run(
                [sys.executable, script_path, *args],
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=180,
                check=False,
            )
        except Exception as exc:
            import traceback as _tb
            logger.warning(
                "[EffectReports] run failed %s: %s\n%s",
                script_name, exc, _tb.format_exc().strip()[-600:],
            )
            return False

        def _decode(b: bytes) -> str:
            for enc in ("utf-8", "cp949"):
                try:
                    return b.decode(enc)
                except UnicodeDecodeError:
                    pass
            return b.decode("utf-8", errors="replace")

        stdout_text = _decode(result.stdout or b"")
        stderr_text = _decode(result.stderr or b"")

        if result.returncode != 0:
            logger.warning(
                "[EffectReports] %s rc=%s stdout=%s stderr=%s",
                script_name,
                result.returncode,
                stdout_text.strip()[-200:],
                stderr_text.strip()[-400:],
            )
            return False
        return True

    def _effect_report_timer_tick(self) -> None:
        now = datetime.datetime.now()
        if not is_market_open(now):
            return
        if self._is_const_out_heavy_cooldown_active(now):
            logger.debug("[EffectReports] skipped during ConstOut cooldown")
            return
        if self._effect_report_running:
            logger.debug("[EffectReports] previous worker still running")
            return
        self._effect_report_tick += 1
        if not (self._effect_report_tick == 1 or self._effect_report_tick % 15 == 1):
            return
        run_backtest = bool(self._effect_report_tick == 1 or self._effect_report_tick % 30 == 1)
        self._start_effect_report_worker(run_backtest=run_backtest)

    def _start_effect_report_worker(self, run_backtest: bool = False) -> None:
        if self._effect_report_running:
            return
        self._effect_report_running = True

        def _worker():
            try:
                self._run_effect_report_script("generate_calibration_report.py")
                self._run_effect_report_script("generate_meta_gate_tuning_report.py", "5m")
                self._run_effect_report_script("generate_rollout_readiness_report.py")
                if run_backtest:
                    self._run_effect_report_script("run_microstructure_ab_backtest.py")
                self._append_effect_monitor_history()
            finally:
                self._effect_report_running = False

        threading.Thread(target=_worker, daemon=True).start()

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
        return {
            "calibration_bins": calib,
            "grade_stats": grades,
            "regime_stats": regime,
            "accuracy_history": hist,
            **self._load_effect_report_metrics(),
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

    # ── Phase 1 헬퍼 메서드 ──────────────────────────────────────

    def _get_active_horizons(self, hhmm):
        # type: (int) -> list
        """HORIZON_TIME_POLICY 기반 활성 호라이즌 목록 반환.

        Returns:
            None = 전체 허용 / [] = 전 차단 / ["1m", "3m", ...] = 지정 목록
        """
        try:
            policy = getattr(runtime_settings, "HORIZON_TIME_POLICY", None)
            if not policy:
                return None
            for (start, end), horizons in policy.items():
                if start <= hhmm < end:
                    return horizons
        except Exception:
            pass
        return None

    def _diagnose_zero_entry(self, features, horizon_proba, ensemble_result):
        # type: (dict, dict, dict) -> None
        """진입0 원인을 자동 진단하여 [ZeroDiag] 로그 출력.

        STEP 7 전 grade==X 또는 direction==0 시 호출.
        """
        try:
            reasons = []
            if ensemble_result.get("coherence_blocked"):
                reasons.append("CoherenceGate")
            if ensemble_result.get("cascade_blocked"):
                reasons.append("CascadeCoherence")
            if ensemble_result.get("direction") == 0:
                reasons.append("FLAT수렴")
            try:
                _eks_active = (
                    self.system_health.is_eks_active()
                    if hasattr(self.system_health, "is_eks_active")
                    else (
                        not getattr(self.system_health, "_eks_evaluated", True)
                        and getattr(self.system_health, "_eks_fired", False)
                    )
                )
                if _eks_active:
                    reasons.append("EKS발동")
            except Exception:
                pass
            _conf = ensemble_result.get("confidence", 0)
            _mc   = ensemble_result.get("min_conf", 0)
            if _conf < _mc:
                reasons.append("conf미달({:.3f}<mc{:.3f})".format(_conf, _mc))
            _fl_horizons = [
                h for h, v in horizon_proba.items()
                if isinstance(v, dict) and float(v.get("flat", 0.0) or 0.0) > 0.7
            ]
            if _fl_horizons:
                reasons.append("FL고착({})".format(",".join(_fl_horizons)))
            _outlier_feats = [
                fn for fn in (self.model.last_extreme_features or [])
                if fn
            ]
            if _outlier_feats:
                reasons.append("이상값피처({})".format(",".join(_outlier_feats[:3])))
            if reasons:
                log_manager.signal("[ZeroDiag] 진입X 원인: {}".format(" / ".join(reasons)))
        except Exception as _de:
            logger.debug("[ZeroDiag] 진단 실패: %s", _de)

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

        # 개선 3: 당일 종가 버퍼를 feature_builder에 전달 → 내일 prev_day_same_hour_ret 계산
        try:
            from utils.db_utils import fetchall
            from config.settings import RAW_DATA_DB as _RDB
            import sqlite3 as _sqlite3
            today_str = now.date().isoformat()
            with _sqlite3.connect(_RDB, timeout=10) as _conn:
                _conn.row_factory = _sqlite3.Row
                _rows = _conn.execute(
                    "SELECT ts, close FROM raw_candles WHERE substr(ts,1,10)=? ORDER BY ts",
                    (today_str,),
                ).fetchall()
            _today_closes = {r["ts"]: float(r["close"]) for r in _rows}
            self.feature_builder.set_prev_day_closes(_today_closes)
            logger.info("[FeatureBuilder] 전일 종가 버퍼 갱신: %d봉", len(_today_closes))
        except Exception as _fbe:
            logger.warning("[FeatureBuilder] 전일 종가 버퍼 갱신 실패: %s", _fbe)

        # ── STEP 3 재학습 완료 대기 ──────────────────────────────
        # 장중 마지막 30분 배치 재학습이 아직 실행 중이면 완료될 때까지 기다린다.
        # 대기 없이 retrain_now()를 동시 호출하면 pkl 경합 + 미완료 상태로 종료됨.
        # 15:40 이후 분봉 파이프라인은 없으므로 메인 스레드 블로킹 허용.
        # [I] 진입 시 retrain 상태 항상 기록 — _gbm_retrain_running=False 경로도 추적 가능
        _retrain_at_dc = "진행중" if getattr(self, "_gbm_retrain_running", False) else "완료/미시작"
        log_manager.system(
            f"[DailyClose] 진입 | retrain={_retrain_at_dc} | {datetime.datetime.now().strftime('%H:%M:%S')}",
            "INFO",
        )
        if getattr(self, "_gbm_retrain_running", False):
            log_manager.system(
                "[DailyClose] STEP 3 재학습 진행 중 — EOD 재학습 전 완료 대기 (최대 20분)",
                "INFO",
            )
            completed = self._gbm_retrain_done_event.wait(timeout=20 * 60)
            if completed:
                log_manager.system("[DailyClose] STEP 3 재학습 완료 확인 — EOD 재학습 시작", "INFO")
            else:
                log_manager.system(
                    "[DailyClose] STEP 3 재학습 20분 초과 — 강제 진행 (타임아웃)", "WARNING"
                )
                # [J] 타임아웃 발생 시 슬랙 알림 — P8 지연 가능성 사전 고지
                try:
                    from utils.notify import notify as _nfy_step3
                    _nfy_step3(
                        "⚠️ DailyClose STEP3 타임아웃 — GBM 재학습 20분 초과\n"
                        "P8 지연 발생 가능 | 내일 EarlyWarmup 보완 예정",
                        "WARNING",
                    )
                except Exception:
                    pass

        # 일일 배치 재학습 (장 마감 후 — 당일 축적 데이터 반영)
        # force=True: 26주 데이터 기준 acc 안정화 → cv_acc 소폭 하락도 교체가 안전
        # intraday=False + full_cv=True: Cybos 단절 후 메모리 경쟁 프로세스 없음
        #   → 300그루 정규 파라미터 + 3-fold CV 20k 캡 해제 + 50k봉 최종 fit
        #   (구 intraday=True는 장 마감 후에도 Cybos COM 경쟁 우려로 제한했던 것 — 해소)
        # 월요일: 주간 재학습도 여기서 통합 → STEP 3 08:50 주간 재학습 중복 스킵됨
        _is_monday_eod = (datetime.datetime.now().weekday() == 0)
        self._eod_retrain_ok = False   # EOD 진입 시 초기화 — 완료 후 True로 설정
        log_manager.system(
            "[DailyClose] EOD 재학습 시작 — 정규 파라미터 (300그루, full_cv=True)"
            + (" [월요일: 주간 재학습 포함]" if _is_monday_eod else ""),
            "INFO",
        )
        # [P0] retrain_now() 예외(예: 32bit 프로세스 MemoryError) 시에도 EOD 잔여 단계
        # (P8 스케일러 재적합·Platt/MetaConf 저장·일일 리셋·WAL 체크포인트)는 계속 진행.
        # 06-11/06-16 동일 패턴 MemoryError로 daily_close() 전체가 중단되며
        # 위 단계 전부 스킵됐던 문제 재발 방지 — catch_up_eod.py로 수동 복구하던 것을
        # 구조적으로 차단.
        try:
            retrain_result = self.batch_retrainer.retrain_now(
                force=True,
                intraday=False,   # 정규 파라미터 (max_iter=300, max_depth=5, lr=0.04)
                full_cv=True,     # CV 20k 캡 해제 — Cybos 단절 후 메모리 여유
            )
        except BaseException as _retrain_exc:  # MemoryError 등 BaseException 포함
            logger.error(
                "[DailyClose] EOD 재학습 예외 — 스킵하고 EOD 잔여 단계 계속 진행: %s",
                _retrain_exc, exc_info=True,
            )
            log_manager.system(
                f"[DailyClose] EOD 재학습 예외(스킵, 잔여단계 계속): {_retrain_exc}",
                "ERROR",
            )
            retrain_result = {"ok": False, "error": str(_retrain_exc)}
        retrain_ok = retrain_result.get("ok", False)
        # 재학습 성공 여부와 무관하게 최신 pkl 로드 — EOD 스케일러 강제 초기화
        # (실패해도 이전 EOD 재학습 pkl이 있으면 _scaler_fitted_at 시계가 맞춰짐)
        _bad = self.model._load_all()
        if _bad:
            logger.error(
                "[Model] EOD 재학습 후 %d개 호라이즌 차원 불일치: %s",
                len(_bad), _bad,
            )
        if retrain_ok:
            self._eod_retrain_ok = True   # 내일 08:55 PreRetrain 스킵 신호
            # 다음날 08:45 신규 시작 시 __init__이 False로 초기화하는 것을 보완:
            # session_state에 날짜를 기록해 pre_market_setup()에서 복원한다.
            try:
                _eod_ss = self._read_session_state()
                _eod_ss["eod_retrain_ok_date"] = datetime.date.today().isoformat()
                self._write_session_state(_eod_ss)
            except Exception as _eod_ss_e:
                logger.warning("[EOD] eod_retrain_ok_date 저장 실패 (무해): %s", _eod_ss_e)
            self._ensure_shap_tracker()
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

        # DB pruning — 매주 월요일 EOD 1회 실행 (RAW_DATA_PRUNE_WEEKS=52주 이전 삭제)
        # 슬라이딩 창(26주) 정상 운영 시 학습 행 수는 ~40,000 안정적
        # 하지만 raw_data.db 자체는 누적 → 52주 초과분 정리로 DB 비대화 방지
        if datetime.datetime.now().weekday() == 0:  # 월요일
            try:
                _pruned = self.batch_retrainer.prune_raw_data_db()
                if _pruned > 0:
                    log_manager.learning(
                        f"[GBM] DB pruning: {_pruned:,}행 삭제 (52주 초과분)"
                    )
            except Exception as _pe:
                logger.warning("[GBM] DB pruning 실패: %s", _pe)

        # [P8] EOD 스케일러 재적합 — 금일 최근 N봉 기준으로 pkl 갱신
        # GBM retrain의 8주 스케일러(분포 폭넓음) 위에 금일 데이터로 추가 재적합.
        # 내일 08:55 warmup이 _warmup_retrain_pending으로 스킵돼도
        # 스케일러 age가 ~17h 이내(GBM retrain 포함 641+분 방지)로 보장된다.
        # [B안] 실패 시 30초 후 1회 재시도 — 일시적 DB lock·메모리 부족 대응
        _p8_done = False
        for _p8_try in range(2):
            try:
                if _p8_try == 1:
                    import time as _p8_time
                    log_manager.system("[P8] EOD 재적합 실패 — 30초 후 재시도", "WARNING")
                    _p8_time.sleep(30)
                from config.settings import SCALER_WARMUP_LOOKBACK_BARS
                _p8_X, _p8_fn = self.batch_retrainer.load_features_for_warmup(
                    lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
                )
                if _p8_X is not None and len(_p8_X) > 0:
                    _p8_res = self.model.refit_scalers_only(
                        _p8_X, _p8_fn,
                        trigger_ts    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        trigger_type  = "E_EOD",
                        trigger_reason= f"EOD 스케일러 재적합 (P8{' 재시도' if _p8_try else ''})"
                                        f" — 내일 시초 z-score 안정화",
                    )
                    _retry_tag = " [재시도 성공]" if _p8_try else ""
                    # [H] _p8_res None 방어 — refit_scalers_only 반환값 타입 불일치 시에도 로그 보장
                    _p8_elapsed = (_p8_res or {}).get("elapsed_sec", 0)
                    _p8_horizons = (_p8_res or {}).get("horizons", [])
                    log_manager.system(
                        f"[P8] EOD 스케일러 재적합 완료{_retry_tag}"
                        f" n={len(_p8_X)}봉 elapsed={_p8_elapsed:.2f}s horizons={_p8_horizons}",
                        "INFO",
                    )
                    _p8_done = True
                    # [C1] P8 성공일 기록 — 다음날 08:45 EarlyWarmup·EKS 원인 진단용
                    try:
                        _ss_p8 = self._read_session_state()
                        _ss_p8["p8_last_success_date"] = datetime.date.today().isoformat()
                        self._write_session_state(_ss_p8)
                    except Exception as _ss_e:
                        # [G] debug → WARNING 격상 — 기록 실패 시 다음날 EKS 원인 오진단 방지
                        log_manager.system(f"[P8] session_state 기록 실패: {_ss_e}", "WARNING")
                else:
                    log_manager.system("[P8] EOD 스케일러 재적합 스킵 — 데이터 없음", "WARNING")
                break   # 성공 or 데이터없음 → 반복 종료
            except Exception as _p8_e:
                logger.warning("[P8] EOD 스케일러 재적합 실패 (시도 %d/2): %s", _p8_try + 1, _p8_e)
                if _p8_try == 1:   # 재시도까지 실패 → 슬랙 알림 (P1)
                    try:
                        from utils.notify import notify as _np8_notify
                        _np8_notify(
                            f"⚠️ P8 EOD 스케일러 재적합 실패 (재시도 포함)\n{_p8_e}\n"
                            f"내일 08:45 EarlyWarmup이 보완 — Canary 발화 가능성 있음",
                            "WARNING",
                        )
                    except Exception:
                        pass

        # [Platt] 앙상블 보정기 저장 — 다음 기동 시 즉시 복원 가능
        try:
            from config.settings import ENSEMBLE_CALIBRATOR_PATH
            if self.ensemble.ensemble_calibrator.save(ENSEMBLE_CALIBRATOR_PATH):
                log_manager.system(
                    f"[Calibration] 앙상블 보정기 저장 완료 "
                    f"n={self.ensemble.ensemble_calibrator.n_samples}",
                    "INFO",
                )
        except Exception as _cal_s_e:
            logger.warning("[Calibration] 보정기 저장 실패 (무해): %s", _cal_s_e)

        # [MetaConf] 학습 상태 저장 — 다음 날 warm-start (cold-start 제거)
        try:
            from config.settings import META_CONF_STATE_PATH
            self.meta_gate.learner.save(META_CONF_STATE_PATH)
        except Exception as _mc_s_e:
            logger.warning("[MetaConf] EOD 상태 저장 실패 (무해): %s", _mc_s_e)

        # ── 자가학습 일일 마감 집계 ──────────────────────────────
        _today_accuracy = self.online_learner.recent_accuracy()
        try:
            self.daily_consolidator.consolidate()
        except Exception as _dce:
            logger.warning("[DailyConsolidator] 집계 실패 (스킵): %s", _dce)
        try:
            _drift_result = self.drift_adjuster.record_accuracy(_today_accuracy)
            _new_alpha = _drift_result.get("alpha", 0.001)
            if hasattr(self.online_learner, "set_alpha"):
                self.online_learner.set_alpha(_new_alpha)
                logger.info("[DriftAdjuster] SGD alpha 갱신: %.5f (%s)", _new_alpha, _drift_result.get("action"))
        except Exception as _dae:
            logger.warning("[DriftAdjuster] 갱신 실패 (스킵): %s", _dae)

        # ── Phase A 임계값 재보정 모니터 (매주 금요일만 실행) ────────
        if now.weekday() == 4:   # 금요일
            try:
                recal_results = self.threshold_recalibrator.run(
                    today=now.date().isoformat()
                )
                alerts = {h: r["alert"] for h, r in recal_results.items() if r["alert"] != "CLEAR"}
                if alerts:
                    log_manager.system(
                        f"[ThresholdRecal] 경보 발생: {alerts}  "
                        f"docs/THRESHOLD_WFA_MONITOR.md Phase A 참조",
                        "WARNING",
                    )
            except Exception as _tre:
                logger.warning("[ThresholdRecal] 실행 실패 (스킵): %s", _tre)

        # 일일 리셋
        if hasattr(self, "_investor_timer"):
            self._investor_timer.stop()
        if hasattr(self, "_option_chain_timer"):
            self._option_chain_timer.stop()
        # MetaGate shadow 버퍼 초기화 — 다음 날 전일 shadow 잔재 방지
        if hasattr(self, "_meta_shadow"):
            self._meta_shadow.clear()
        self.meta_gate.learner.reset_daily()
        self.feature_builder.reset_daily()
        self.bar_aggregator.reset_daily()
        self._hz_feat_cache.clear()
        self._hz_bar_age.clear()
        self.micro_regime_clf.reset_daily()
        self.current_micro_regime = "혼합"  # threshold_feasibility 피처에 1분 lag로 전달됨
        self.intraday_regime.reset_daily()
        self.current_intraday_regime = INTRADAY_NORMAL
        self.investor_data.reset_daily()
        self.pcr_store.reset_daily()
        self.option_chain_snap.reset_daily()
        self.position.reset_daily()
        self.circuit_breaker.reset_daily()
        self.profit_guard.reset_daily()
        self.online_learner.reset_daily()
        self.market_dna.reset_daily()
        self.core_health.reset_daily()
        self.model.reset_daily_gap_offset()
        self._first_tick_notified = False        # 다음 날 첫 분봉에서 갭 오프셋 재설정
        self._intraday_startup_warmup_done = False  # 다음 날 B_INTRADAY 재발동 허용
        # 프리장 warmup 상태 일일 리셋 — 다음 날 프리장 처리 재활성
        self._pre_market_bars               = []
        self._pre_market_scaler_refitted    = False
        self._pre_market_gap_offset_set     = False
        self._pre_market_conf_history       = []
        self.shadow_session.reset_daily()
        self.contrarian_mode.reset_daily()
        self.trend_gate.reset_daily()
        self.ensemble.reset_daily()
        self._last_ensemble_direction = 0
        for _h in self._bias_buf:
            self._bias_buf[_h].clear()
        self._bias_log_tick = 0
        self._bias_fl_streak = {h: 0 for h in HORIZONS}
        self._bias_override_horizons.clear()
        self._conf_prev.clear()
        self._conf_stuck = {h: 0 for h in HORIZONS}
        self._ensemble_conf_cache.clear()
        self._param_corr_history.clear()
        self._shap_feature_window.clear()
        self._shap_last_update_minute = None
        self._restored_corr_str = ""
        self._live_shap_ready = False
        self._cached_shap_importance = {}
        self._verified_today = 0
        for _h in self._horizon_runtime_state:
            self._horizon_runtime_state[_h] = {
                "verified_cycles":  0,
                "trained_cycles":   0,
                "qualified":        False,
                "active":           False,
                "status":           "not_qualified",
                "weight":           0.0,
                "recent_accuracy":  0.0,
            }
        self.emergency_exit.reset()
        self.kill_switch.deactivate()
        self.system_health.reset_daily()    # EKS·GAP_OPEN 상태 초기화 (z_warn·restart는 유지)

        # rolling σ EOD 저장 + 초기화 (방법3)
        if self._sigma_20 > 0:
            self._last_sigma_20 = self._sigma_20
            log_manager.learning(
                f"[Sigma] EOD sigma_20={self._sigma_20:.5f}% 저장 "
                f"(내일 장 초반 20봉 미수집 구간 폴백용)"
            )
        self._sigma_buf.clear()
        self._sigma_ready = False
        self._sigma_20 = 0.0
        self._pre_retrain_done = False   # 내일 첫 재학습 완료 전까지 보수 사이즈 재활성

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

        # 섹션 8: scaler_daily EOD 집계 저장
        try:
            from model.scaler_monitor_db import aggregate_daily, insert_daily
            _sm_stats = aggregate_daily(today_str)
            _cb3_fired = int(bool(getattr(self.circuit_breaker, "_daily_halt", False)))
            insert_daily(
                today_str, _sm_stats,
                grade_x_minutes=self._grade_x_count,
                cb3_triggered=_cb3_fired,
            )
        except Exception as _sm_e:
            logger.warning("[ScalerMonitor] EOD 집계 저장 실패 (스킵): %s", _sm_e)
        self._grade_x_count = 0   # 내일을 위해 리셋
        _ccf_today = self._checklist_conf_fail_count   # [P3] 리포트 전달용 — 리셋 전에 캡처
        log_manager.system(
            f"[P3] 금일 Checklist 신뢰도 차단: {_ccf_today}회"
            f" (앙상블 통과 후 conf 미달 강제 X)",
            "INFO",
        )
        self._checklist_conf_fail_count = 0

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
            _report = _exp.build_report(
                extra_stats={"checklist_conf_fail": _ccf_today}
            )
            _exp.save(_report)
            logger.info("[Phase5] 일일 전략 리포트 저장 완료")
        except Exception as _ph5_e:
            logger.warning("[Phase5] 일일 export 실패 (스킵): %s", _ph5_e)

        # [Shadow] shadow_candidate.json 체크 → 섀도우 자동 시작
        self._load_shadow_candidate()

        # ── DBWriter 큐 플러시 — 마지막 분봉 쓰기 완료 후 WAL 체크포인트 ────
        # 15:10 강제청산 ~ 15:40 사이 큐에 남은 candle/feature/scaler_monitor 기록을
        # 모두 처리한 뒤 체크포인트를 수행해야 WAL에 미반영 데이터가 없다.
        try:
            self._db_write_queue.put(None)  # DBWriter 종료 sentinel
            self._db_write_queue.join()     # 모든 pending write 완료 대기
            logger.info("[DBQueue] EOD 플러시 완료")
        except Exception as _dq_eod_e:
            logger.warning("[DBQueue] EOD 플러시 실패 (무해): %s", _dq_eod_e)

        # 오래된 레짐 히스토리 정리 (30일 초과분 삭제)
        try:
            purge_old_regime_history(keep_days=30)
        except Exception as _prh_e:
            logger.warning("[RegimeHistory] 정리 실패 (무해): %s", _prh_e)

        # ── WAL 체크포인트 — 장중 누적된 WAL 파일 강제 플러시 ────────
        # WAL auto-checkpoint(1000 page)는 장중 파이프라인 타이밍에 걸릴 수 있음.
        # 장 마감 후 TRUNCATE 체크포인트로 WAL을 0 바이트로 초기화해 내일 새벽을 준비.
        try:
            import sqlite3 as _wal_sqlite3
            from config.settings import EOD_WAL_CHECKPOINT_DBS as _WAL_DBS
            for _wal_db in _WAL_DBS:
                try:
                    with _wal_sqlite3.connect(_wal_db, timeout=30) as _wc:
                        _wc.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                    logger.info("[WAL] 체크포인트 완료: %s", _wal_db)
                except Exception as _wal_db_e:
                    logger.warning("[WAL] 체크포인트 실패 (%s): %s", _wal_db, _wal_db_e)
        except Exception as _wal_e:
            logger.warning("[WAL] 체크포인트 전체 실패 (무해): %s", _wal_e)

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
        # 종료 예약은 메인 Qt 스레드에서 수행 (QueuedConnection → _schedule_shutdown 에서 처리)
        _shutdown_sig.request.emit()

    def _schedule_shutdown(self) -> None:
        """자동 종료 15초 예약 — 반드시 메인 Qt 스레드에서 실행.

        _shutdown_sig.request 시그널(QueuedConnection)을 통해 호출되므로
        DailyClose 스레드에서 emit() 해도 이 메서드는 메인 이벤트 루프에서 실행된다.
        """
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
         300s  — 거래소 CB 추정 → CB 대기 모드 진입 (복구 시도 중단)
        """
        # 장 마감 후에는 파이프라인이 정상적으로 멈추므로 워치독 무시
        if not is_market_open():
            return
        # 15:10 강제청산 이후는 예측 파이프라인이 정상적으로 멈추는 구간 —
        # _try_pipeline_recovery()의 "이미 복구함" 스킵 분기가 notify_pipeline_ran()으로
        # 워치독을 매번 리셋해 90초 경보가 무한 반복되는 문제 방지 (감시 자체를 끔)
        if is_force_exit_time(datetime.datetime.now()):
            return
        m, s = divmod(elapsed_s, 60)
        elapsed_str = f"{m}분 {s:02d}초"

        # ── 거래소 CB 대기 모드 ─────────────────────────────────────────
        # 5분 이상 미수신 = 네트워크 단절이 아닌 거래소 CB/단일가 구간으로 판단.
        # 이후 복구 시도를 멈추고 분봉 재개를 기다린다.
        if elapsed_s >= 300:
            if not self._exchange_cb_mode:
                self._exchange_cb_mode = True
                self._exchange_cb_start = datetime.datetime.now()
                msg = (
                    f"[ExchangeCB] 분봉 {elapsed_str} 미수신 — "
                    f"거래소 CB/단일가 구간 추정. 복구 시도 중단, 재개 대기 모드 진입"
                )
                log_manager.system(msg, "WARNING")
                notify(f"⏸ 미륵이 거래소 CB 대기 — {elapsed_str} 분봉 미수신")
                self._shadow_tracker.mark_exchange_cb(True)
            else:
                # CB 모드 중 — 30분마다 생존 알림만 발송
                _gap_min = int(
                    (datetime.datetime.now() - self._exchange_cb_start).total_seconds() / 60
                ) if self._exchange_cb_start else m
                if _gap_min > 0 and _gap_min % 30 == 0 and s < 60:
                    notify(f"⏸ 거래소 CB 대기 중 {_gap_min}분 — 분봉 재개 시 자동 복구")
            return  # CB 모드 중에는 _try_pipeline_recovery 절대 호출 안 함

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
                   f"장 시간({is_market_open()}) 확인. 자동 복구 시도 예약 (300ms 후)")
            log_manager.system(msg, "WARNING")
            notify_pipeline_delayed(elapsed_str)
            QTimer.singleShot(300, self._try_pipeline_recovery)  # [P1b] 90s 자동 재진입

    def _post_exchange_cb_resume(self, gap_min: int) -> None:
        """거래소 CB 해제 후 상태 초기화 루틴.

        CB 구간은 분봉 공백이므로 공백 전 상태가 그대로 잔존한다.
        재개 즉시 다음 5가지를 초기화해 오판을 방지한다.

          ① ShadowSession BLOCKED 강제 LIVE 복구 (연결 단절이 아닌 거래소 중단)
          ② acc30m 버퍼 리셋 (CB 전 예측이 오방향 오판 오염 방지)
          ③ 앙상블 ConstOut/CascadeCoherence/FL 버퍼 리셋 (공백 전 방향 잔존 제거)
          ④ 스케일러 즉시 재적합 (CB 후 분포 급변 대응)
          ⑤ D_PRICE_MOMENTUM 쿨다운 리셋 (CB 직후 급변 구간에서 즉시 트리거 허용)
        """
        # ① ShadowSession — CB 해제이므로 core_health 조건 면제하고 LIVE 복귀
        self._shadow_tracker.mark_exchange_cb(False)
        self._shadow_tracker.force_live(reason=f"exchange_cb_resume gap={gap_min}m")

        # ② acc30m 버퍼 리셋 — CB 전 예측은 전혀 다른 시장 상황
        self.circuit_breaker._accuracy_buf.clear()
        log_manager.system(
            f"[ExchangeCB] acc30m 버퍼 초기화 — CB {gap_min}분 공백 전 예측 제거",
            "INFO",
        )

        # ③ 앙상블 상태 리셋 — ConstOut/CascadeCoherence/FL streak/StuckBreaker
        self.ensemble.reset_exchange_cb()
        log_manager.system(
            "[ExchangeCB] 앙상블 버퍼 초기화 — ConstOut/Cascade/FL/Stuck 리셋",
            "INFO",
        )

        # ④ 스케일러 즉시 재적합 (백그라운드 daemon thread)
        # CB 후 가격 레벨이 크게 변해 microprice/vwap 등 절대값 피처가 극단값을 가짐
        if not self._scaler_refresh_running:
            def _ecb_scaler_worker(_gap=gap_min):
                self._scaler_refresh_running = True
                try:
                    from config.settings import SCALER_WARMUP_LOOKBACK_BARS
                    _X, _fn = self.batch_retrainer.load_features_for_warmup(
                        lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
                    )
                    if _X is not None:
                        self.model.refit_scalers_only(
                            _X, _fn,
                            trigger_type="ExchangeCB",
                            trigger_reason=f"거래소CB {_gap}분 공백 후 재개",
                        )
                        log_manager.system(
                            f"[ExchangeCB] 스케일러 재적합 완료 (gap={_gap}m)",
                            "INFO",
                        )
                except Exception as _e:
                    logger.warning("[ExchangeCB] 스케일러 재적합 실패: %s", _e)
                finally:
                    self._scaler_refresh_running = False
            import threading as _th
            _th.Thread(target=_ecb_scaler_worker, daemon=True).start()
        else:
            log_manager.system(
                "[ExchangeCB] 스케일러 재적합 스킵 — 이미 진행 중",
                "INFO",
            )

        # ⑤ D_PRICE_MOMENTUM 쿨다운 리셋 — CB 직후 급변 구간에서 즉시 트리거 허용
        self._price_momentum_refit_until = None

        log_manager.system(
            f"[ExchangeCB] 재개 초기화 완료 | gap={gap_min}m | "
            f"ShadowLIVE/acc리셋/앙상블리셋/스케일러재적합/쿨다운리셋",
            "INFO",
        )

    def _try_pipeline_recovery(self) -> None:
        """raw_candles 최신 분봉으로 파이프라인 강제 재실행."""
        # 거래소 CB 대기 모드 중에는 분봉 자체가 없으므로 복구 시도 무의미
        if self._exchange_cb_mode:
            log_manager.system(
                "[복구 스킵] 거래소 CB 대기 모드 — 분봉 재개 시 자동 복구",
                "INFO",
            )
            return
        # 15:10 강제청산 이후는 파이프라인 정지가 의도된 상태 —
        # 복구를 시도하면 _on_candle_closed()의 force-exit 가드를 우회해
        # run_minute_pipeline()이 강제로 다시 돌아버리는 부작용 방지
        if is_force_exit_time(datetime.datetime.now()):
            return

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

    # [SERVICE-BOUNDARY 4/4] SessionRecoveryService
    # 책임: 재시작 세션 번호 증가, 당일 거래/패널/통계 복원
    # 입력: trades.db, session_state.json
    # 출력: dashboard 복원 로그, position 일일통계, pnl panel 초기화
    # ── 재시작 복원 ───────────────────────────────────────────────

    def _increment_session(self) -> int:
        """호환 래퍼: SessionRecoveryService.increment_session 위임."""
        return self.session_recovery_service.increment_session(self)

    def _restore_daily_state(self) -> None:
        """호환 래퍼: SessionRecoveryService.restore_daily_state 위임."""
        self.session_recovery_service.restore_daily_state(self)

    def _restore_panels_from_history(self) -> None:
        """호환 래퍼: SessionRecoveryService.restore_panels_from_history 위임."""
        self.session_recovery_service.restore_panels_from_history(self)

    def _refresh_pnl_history(self) -> None:
        """trades.db 최근 90일 조회 → 손익 추이 패널 갱신."""
        try:
            rows = fetch_pnl_history(limit_days=90)
            self.dashboard.update_pnl_history(rows)
        except Exception as e:
            apply_error_policy(
                system=self,
                level=ErrorLevel.RECOVERABLE,
                context="pnl_history_refresh",
                exc=e,
                logger=logger,
                dashboard_logger=log_manager.system,
            )
        # 수익 보존 가드 패널 갱신 (청산 직후 최신 트레이드 반영)
        try:
            today_trades = fetch_today_trades() or []
            daily_pnl = self.position.daily_stats()["pnl_krw"]
            self.dashboard.refresh_profit_guard(daily_pnl, today_trades)
        except Exception as _pge2:
            apply_error_policy(
                system=self,
                level=ErrorLevel.RECOVERABLE,
                context="profit_guard_panel_refresh",
                exc=_pge2,
                logger=logger,
                dashboard_logger=log_manager.system,
            )

    def _collect_broker_capability_summary(self) -> dict:
        """브로커 기능 지원/현재 세션 검증 상태 요약."""
        rt = getattr(self, "realtime_data", None)
        tick_events = int(getattr(rt, "_tick_event_count", 0) or 0)
        hoga_events = int(getattr(rt, "_hoga_event_count", 0) or 0)
        investor_fetch_count = int(getattr(self.investor_data, "_fetch_count", 0) or 0)
        investor_supported = bool(
            getattr(self.investor_data, "_futures_supported", False)
            or getattr(self.investor_data, "_program_supported", False)
        )

        return {
            "connect": {
                "supported": True,
                "verified": bool(getattr(self.broker, "is_connected", False)),
            },
            "balance": {
                "supported": True,
                "verified": bool(getattr(self, "_broker_sync_verified", False)),
            },
            "order": {
                "supported": True,
                "verified": bool(getattr(self, "_last_order_event_key", None) is not None),
            },
            "fill_callback": {
                "supported": True,
                "verified": bool(getattr(self, "_last_order_event_key", None) is not None),
            },
            "tick": {
                "supported": True,
                "verified": tick_events > 0,
                "events": tick_events,
            },
            "hoga": {
                "supported": True,
                "verified": hoga_events > 0,
                "events": hoga_events,
            },
            "investor_tr": {
                "supported": bool(hasattr(self.broker, "probe_investor_ticker")),
                "verified": investor_fetch_count > 0,
                "fetch_count": investor_fetch_count,
                "runtime_supported": investor_supported,
            },
            "server_label": {
                "supported": True,
                "verified": True,
                "value": (
                    ("Cybos 모의투자" if self.broker.get_login_info("GetServerGubun") == "1" else "Cybos 실서버")
                    if getattr(self.broker, "name", "") == "cybos"
                    else ("모의투자" if self.broker.get_login_info("GetServerGubun") == "1" else "실서버")
                ),
            },
        }

    def _log_broker_capability_summary(self) -> None:
        summary = self._collect_broker_capability_summary()

        def _yn(value: bool) -> str:
            return "Y" if value else "N"

        msg = (
            "[Capability] broker=%s "
            "connect=%s/%s balance=%s/%s order=%s/%s fill=%s/%s "
            "tick=%s/%s(%s) hoga=%s/%s(%s) investor=%s/%s(fetch=%s,runtime=%s) "
            "server=%s"
        ) % (
            getattr(self.broker, "name", "unknown"),
            _yn(summary["connect"]["supported"]), _yn(summary["connect"]["verified"]),
            _yn(summary["balance"]["supported"]), _yn(summary["balance"]["verified"]),
            _yn(summary["order"]["supported"]), _yn(summary["order"]["verified"]),
            _yn(summary["fill_callback"]["supported"]), _yn(summary["fill_callback"]["verified"]),
            _yn(summary["tick"]["supported"]), _yn(summary["tick"]["verified"]), summary["tick"]["events"],
            _yn(summary["hoga"]["supported"]), _yn(summary["hoga"]["verified"]), summary["hoga"]["events"],
            _yn(summary["investor_tr"]["supported"]), _yn(summary["investor_tr"]["verified"]),
            summary["investor_tr"]["fetch_count"],
            _yn(summary["investor_tr"]["runtime_supported"]),
            summary["server_label"]["value"],
        )
        logger.info(msg)
        self.dashboard.append_sys_log(msg)

    # 오케스트레이션 진입점: 서비스 경계 호출 순서만 관리
    # ── 메인 루프 (Qt 이벤트 루프 기반) ──────────────────────────
    def run(self):
        """메인 실행 — Qt 이벤트 루프 기반."""
        logger.info("=" * 60)
        logger.info("미륵이 — KOSPI 200 선물 방향 예측 시스템 시작")
        logger.info("=" * 60)

        # 키움 로그인 (블로킹)
        if not self.connect_kiwoom():
            logger.critical("[System] 키움 연결 실패 — 종료")
            notify("🚨 미륵이 기동 실패 — 브로커 연결 불가\n수동 재시작 필요", "CRITICAL")
            return

        # 기동 완료 슬랙 알림
        _startup_code = getattr(self, "_futures_code", "?")
        _bn = getattr(self.broker, "name", "")
        _srv = self.broker.get_login_info("GetServerGubun")
        _is_simul = (_srv == "1")
        if _bn == "cybos":
            _startup_srv = "Cybos 모의투자" if _is_simul else "Cybos 실서버"
        else:
            _startup_srv = "모의투자" if _is_simul else "실서버"
        notify_startup(_startup_code, _startup_srv)
        # 대시보드 서버 모드 동기화 (라디오 버튼 불일치 시 진입 차단)
        self.dashboard.set_server_mode("simul" if _is_simul else "real")

        self._pre_market_done        = False
        self._pre_market_stage1_done = False
        self._daily_close_done       = False
        # [Bug-1] 장중 재시작 시 __init__ 에서 복원된 True를 보존.
        # (False로 무조건 덮어쓰면 GapOffset 재복원 보호가 무효화되어 첫 수신봉 가격으로 오염됨)
        self._first_tick_notified = getattr(self, "_first_tick_notified", False)
        self._broker_sync_critical_notified = False  # broker sync CRITICAL 알림 1회 플래그
        # 프리장 warmup 상태 초기화 (앱 최초 기동 시)
        self._pre_market_bars               = getattr(self, "_pre_market_bars", [])
        self._pre_market_scaler_refitted    = getattr(self, "_pre_market_scaler_refitted", False)
        self._pre_market_gap_offset_set     = getattr(self, "_pre_market_gap_offset_set", False)
        self._pre_market_conf_history       = getattr(self, "_pre_market_conf_history", [])

        # [Bug-4] 장중 재시작 감지 로그 — GapOffset·scaler 복원 상태 명시
        _startup_now = datetime.datetime.now()
        if is_market_open(_startup_now):
            _gap_restored = self._first_tick_notified  # True = __init__ 에서 복원 성공
            log_manager.system(
                f"[RESTART] 장중 재시작 감지 {_startup_now.strftime('%H:%M')} — "
                f"GapOffset={'복원됨' if _gap_restored else '미설정(첫분봉 재설정 예정)'}  "
                f"pre_market_scaler={self._pre_market_scaler_refitted}",
                "WARNING",
            )

        # 1분 주기 관리 타이머 (분봉 파이프라인은 on_candle_closed 콜백으로 구동)
        self._scheduler = QTimer()
        self._scheduler.setInterval(30_000)   # 30초마다 체크
        self._scheduler.timeout.connect(self._scheduler_tick)
        self._scheduler.start()

        # 수급 TR 주기 폴링 — 60초 (COM 콜백 외부에서 안전하게 실행)
        self._investor_timer = QTimer()
        self._investor_timer.setInterval(60_000)
        self._investor_timer.timeout.connect(self._fetch_investor_data)
        self._investor_timer.start()

        # 옵션 체인 주기 폴링 — 300초 (opt_chain_pcr / opt_gex_bn / opt_atm_* 수집)
        self._option_chain_timer = QTimer()
        self._option_chain_timer.setInterval(300_000)
        self._option_chain_timer.timeout.connect(self._poll_option_chain)
        self._option_chain_timer.start()

        self._balance_ui_timer = QTimer()
        self._balance_ui_timer.setInterval(2_000)
        self._balance_ui_timer.timeout.connect(self._refresh_dashboard_balance_ui_only)
        self._balance_ui_timer.start()

        self._effect_report_timer = QTimer()
        self._effect_report_timer.setInterval(60_000)
        self._effect_report_timer.timeout.connect(self._effect_report_timer_tick)
        self._effect_report_timer.start()

        # 대시보드 표시 + 긴급정지 버튼 연결
        self.dashboard.show()
        self._log_broker_capability_summary()
        if hasattr(self.dashboard, "btn_kill"):
            self.dashboard.btn_kill.clicked.connect(
                lambda: self.activate_kill_switch("대시보드 긴급정지")
            )
        if self.realtime_data:
            _bn = getattr(self.broker, "name", "")
            _srv2 = self.broker.get_login_info("GetServerGubun")
            if _bn == "cybos":
                _srv_lbl = "Cybos 모의투자" if _srv2 == "1" else "Cybos 실서버"
                _rt_method = "FutureCurOnly/Subscribe"
            else:
                _srv_lbl = "모의투자" if _srv2 == "1" else "실서버"
                _rt_method = "SetRealReg"
            self.dashboard.append_sys_log(
                f"시스템 시작 | TR={self.realtime_data.code} [{_srv_lbl}] 분봉수집=실시간({_rt_method})"
            )
        else:
            self.dashboard.append_sys_log("시스템 시작 | 코드=—")
        self.dashboard.update_system_status(cb_state="NORMAL", latency_ms=0.0)

        # 파이프라인 감시 콜백 등록
        self.dashboard.set_pipeline_watchdog_cb(self._on_pipeline_watchdog)

        # 슬랙 On/Off 체크박스 → notify 모듈 플래그 연결
        # _restore_ui_prefs()에서 이미 체크박스 초기값이 복원됐으므로, 여기서 초기 동기화
        set_slack_enabled(self.dashboard.chk_slack.isChecked())
        self.dashboard.chk_slack.stateChanged.connect(
            lambda state: set_slack_enabled(bool(state))
        )

        # 세션 카운터 증가 + 당일 거래/패널 복원 (Day 3 서비스 단일 호출)
        self.session_recovery_service.restore_on_startup(self)

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

        # [A] 08:45 얼리버드 warmup — scaler age > EARLY_WARMUP_MIN_AGE_HOURS 시 선행 갱신
        # 커버: 전날 P8 실패 / 휴장일 / 중간 멈춤 / 주말 등 원인 무관 모든 노후화 케이스
        # → 08:55 Canary 체크 시점엔 이미 완료 → P2 90초 대기 사실상 0초
        # 기존 24h 조건은 장 마감(15:30)→다음날 08:45 = ~17h 케이스를 커버 못 함
        # 4h로 완화 → 매 영업일 항상 발동하여 scaler 노후화 원천 차단
        # 상한 08:57: 08:40 이전 시작 + Cybos 로그인 지연 시에도 EarlyWarmup 창 확보
        if (
            not getattr(self, "_early_warmup_started", False)
            and is_trading_day(now)
            and datetime.time(8, 45) <= now.time() < datetime.time(8, 57)
        ):
            try:
                from config.settings import EARLY_WARMUP_MIN_AGE_HOURS as _EW_MIN_AGE
                _early_age = self.model.canary_stale_age_hours()
                if _early_age > _EW_MIN_AGE:
                    self._early_warmup_started = True
                    self._scaler_refresh_running = True   # ScalerWarmup 동시 실행 방지
                    log_manager.system(
                        f"[EarlyWarmup] scaler 노후={_early_age:.0f}h → 08:45 선행 warmup 시작"
                        f" (전날 P8 실패·휴장·중단 대응)",
                        "WARNING",
                    )
                    def _early_warmup_worker():
                        try:
                            from config.settings import SCALER_WARMUP_LOOKBACK_BARS as _LB
                            _X_ew, _fn_ew = self.batch_retrainer.load_features_for_warmup(
                                lookback_bars=_LB
                            )
                            if _X_ew is not None:
                                self.model.refit_scalers_only(_X_ew, _fn_ew)
                                log_manager.system(
                                    f"[EarlyWarmup] 완료 n={len(_X_ew)}봉"
                                    f" — 08:55 canary 체크 전 scaler 갱신 완료",
                                    "INFO",
                                )
                            else:
                                log_manager.system("[EarlyWarmup] 데이터 없음 — 스킵", "WARNING")
                        except Exception as _ew_e:
                            logger.warning("[EarlyWarmup] 실패: %s", _ew_e)
                        finally:
                            self._scaler_refresh_running = False
                    threading.Thread(target=_early_warmup_worker, daemon=True).start()
            except Exception as _ea_e:
                logger.warning("[EarlyWarmup] age 체크 실패 (무시): %s", _ea_e)

        # [B_INTRADAY] 장중 재시작 스케일러 즉시 warmup (1회만 실행)
        # 근거: pre_market_setup(08:55)은 장중 재시작에서 실행되지 않으므로
        #   scaler가 수십~백분 노후화된 채로 D_FORCE 발동(90분 지연)까지 방치됨.
        #   재시작 후 첫 scheduler tick(≤30s)에 age > 30min이면 즉시 refit.
        # [Bug-3] 하한 09:00 (기존 09:05에서 변경):
        #   GAP_OPEN(09:00~09:05) 재시작 시 ScalerWarmup·EarlyWarmup 모두 miss →
        #   09:05 까지 scaler 보호 공백 발생. _scaler_refresh_running 가드가 충돌 방지 역할.
        if (
            not getattr(self, "_intraday_startup_warmup_done", False)
            and is_trading_day(now)
            and datetime.time(9, 0) <= now.time() < datetime.time(15, 10)
            and not getattr(self, "_scaler_refresh_running", False)
            and not getattr(self, "_gbm_retrain_running", False)
        ):
            try:
                _bi_age_min = self.model.canary_stale_age_hours() * 60.0
                if _bi_age_min > 30.0:
                    self._intraday_startup_warmup_done = True
                    log_manager.system(
                        f"[StartupWarmup] 장중 재시작 감지 — scaler {_bi_age_min:.0f}분 노후 "
                        f"(>30분) → B_INTRADAY refit 트리거",
                        "WARNING",
                    )
                    self._scaler_refresh_running = True
                    def _b_intraday_worker(_age=_bi_age_min):
                        try:
                            from config.settings import SCALER_WARMUP_LOOKBACK_BARS
                            _X_bi, _fn_bi = self.batch_retrainer.load_features_for_warmup(
                                lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
                            )
                            if _X_bi is not None:
                                self.model.refit_scalers_only(
                                    _X_bi, _fn_bi,
                                    trigger_type="B_INTRADAY",
                                    trigger_reason=f"startup_stale_{_age:.0f}m",
                                )
                                log_manager.system(
                                    f"[StartupWarmup] 완료 n={len(_X_bi)}봉", "INFO"
                                )
                            else:
                                log_manager.system("[StartupWarmup] 데이터 없음 — 스킵", "WARNING")
                        except Exception as _bi_e:
                            logger.warning("[StartupWarmup] 실패: %s", _bi_e)
                        finally:
                            self._scaler_refresh_running = False
                    threading.Thread(target=_b_intraday_worker, daemon=True).start()
                else:
                    # scaler 신선 (≤30분) — B_INTRADAY 불필요
                    self._intraday_startup_warmup_done = True
            except Exception as _bi_e2:
                logger.warning("[StartupWarmup] age 체크 실패 (무시): %s", _bi_e2)

        # 1단계 (08:55): macro seed fetch + PreRetrain + 실시간 구독 시작
        # - pre_market_setup(): SP500·KRW seed fetch, PreRetrain 시작
        # - realtime_data.start(): 09:00 첫 틱 누락 방지. 구독 후 틱은 is_market_open 가드가 차단(안전)
        # - 레짐 확정은 하지 않음 → 2단계(08:58)에서 2회차 fetch 후 결정
        if (
            not getattr(self, "_pre_market_stage1_done", False)
            and is_trading_day(now)
            and datetime.time(8, 55) <= now.time() < datetime.time(9, 0)
        ):
            self.pre_market_setup()
            self.latency_sync.reset_daily()
            self._pre_market_stage1_done = True
            self._daily_close_done   = False
            self._rollover_detected  = False
            self._pre_sync_attempted = False
            _rd = getattr(self, "realtime_data", None)
            if _rd is not None and not getattr(_rd, "_running", False):
                _rd.start(load_history=True)
                log_manager.system("[PreOpen] 09:00 대비 실시간 구독 사전 시작 (08:55~)", "INFO")

        # 2단계 (08:58~09:05): 2회차 macro fetch → SP500·KRW 실수치 → 레짐 확정
        # 08:58 이후 최초 heartbeat에서 1회 실행. 폴백 상한 09:05로 GAP_OPEN 이내 보장.
        if (
            getattr(self, "_pre_market_stage1_done", False)
            and not self._pre_market_done
            and is_trading_day(now)
            and datetime.time(8, 58) <= now.time() < datetime.time(9, 5)
        ):
            self._pre_market_stage2()
            notify_premarket_ready(
                self.current_regime,
                getattr(self, "_futures_code", "?"),
            )
            self._pre_market_done = True

        # [PreOpen-이상점4] 장 시작 직전(08:58~08:59:30) broker sync 선실행
        # → GAP_OPEN 구간(09:00~09:05) 진입 차단 방지. 장중 재시도(3분 간격)보다 먼저 실행.
        # _pre_sync_attempted 플래그로 당일 1회만 실행.
        if (
            self._broker_sync_block_new_entries
            and is_trading_day(now)
            and datetime.time(8, 58) <= now.time() < datetime.time(9, 0)
            and not getattr(self, "_pre_sync_attempted", False)
        ):
            self._pre_sync_attempted = True
            log_manager.system(
                "[BrokerSync] 장 시작 전 sync 선실행 (08:58~) "
                f"reason={self._broker_sync_last_error}",
                "INFO",
            )
            _ts_sync_position_from_broker(self)

        # 일일 마감 (15:40~, KRX 거래일만)
        if (
            not self._daily_close_done
            and now.time() >= datetime.time(15, 40)
            and is_trading_day(now)
            and not getattr(self, "_daily_close_running", False)
        ):
            if self._skip_post_close_cycle_today:
                self._daily_close_done = True
                logger.info("[System] today auto-shutdown already executed; skip daily_close on manual restart")
                return
            if self.realtime_data:
                self.realtime_data.stop()
            # Qt 타이머는 소유 스레드(메인)에서 정지해야 안전 — 스레드 분기 전에 처리
            if hasattr(self, "_investor_timer"):
                self._investor_timer.stop()
            if hasattr(self, "_option_chain_timer"):
                self._option_chain_timer.stop()
            self._daily_close_running = True
            self._daily_close_done = True  # 중복 진입 방지 — 스레드 완료 전에 플래그 선점

            def _run_daily_close():
                _emit_done = False
                try:
                    self.daily_close()
                    _emit_done = True   # daily_close() 마지막 emit() 이 정상 실행된 경우
                except Exception as _dc_exc:
                    # daily_close() 중 예외 → emit() 이 호출되지 않은 경우 여기서 보강
                    logger.error("[DailyClose] 예외 발생 — 강제 종료 예약: %s", _dc_exc, exc_info=True)
                    log_manager.system(f"[DailyClose] 예외 → 강제 종료 예약: {_dc_exc}", "ERROR")
                finally:
                    self._daily_close_running = False
                    self._pre_market_done        = False
                    self._pre_market_stage1_done = False
                    if not _emit_done:
                        _shutdown_sig.request.emit()

            import threading as _threading
            _threading.Thread(target=_run_daily_close, daemon=True, name="DailyClose").start()

        # 연결 감시 — 끊김 시 슬랙 CRITICAL 알림 후 재연결
        if not self.broker.is_connected:
            logger.error("[System] 키움 연결 끊김 — 재연결 시도")
            notify_connection_lost(getattr(self.broker, "name", "브로커"))
            self._restart_cause = "AUTO_DISCONNECT"
            self.connect_broker()
        elif is_market_open(now):
            self.broker_runtime_service.ensure_market_open_runtime_started(
                self,
                reason="scheduler_market_open",
            )
            # Startup balance sync 실패 시 장중 재시도 (30초 tick마다 확인, 3분 간격 제한)
            if self._broker_sync_block_new_entries and is_market_open(now):
                last_retry = getattr(self, "_broker_sync_retry_at", None)
                if last_retry is None or (now - last_retry).total_seconds() >= 180:
                    self._broker_sync_retry_at = now
                    log_manager.system(
                        f"[BrokerSync] startup sync 미검증 상태 — 장중 재시도 "
                        f"(reason={self._broker_sync_last_error})",
                        "WARNING",
                    )
                    _ts_sync_position_from_broker(self)
                # 장 시작 후에도 sync 차단이 지속되면 CRITICAL 슬랙 알림 (1회)
                if not getattr(self, "_broker_sync_critical_notified", False):
                    self._broker_sync_critical_notified = True
                    notify_broker_sync_blocked(self._broker_sync_last_error)

            # 장중 롤오버 감시 — 60 tick(30분)마다 근월물 재확인
            # 롤오버가 감지되면 WARNING 로그 + UI 갱신만 수행; 재구독은 재기동 시 자동 처리
            if self._heartbeat_count % 60 == 0 and not getattr(self, "_rollover_detected", False):
                if self.broker_runtime_service.check_rollover(self):
                    self._rollover_detected = True  # 이후 반복 알림 억제

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
    ret = self._send_broker_entry_order(direction, quantity)
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
    target_qty = self.position.get_stage_exit_qty(stage)
    if target_qty <= 0:
        _ts_log_diag(
            self,
            "PartialExitSkipped",
            stage=stage,
            ratio=ratio,
            target_qty=target_qty,
            stage_plan=self.position.get_stage_plan(),
            position=_ts_get_position_snapshot(self),
        )
        return
    is_full_close = target_qty >= total_qty or stage >= 3
    send_qty = total_qty if is_full_close else target_qty
    reason = f"TP{stage}(전량)" if is_full_close else f"TP{stage} 부분청산 {ratio:.0%}"

    # pending을 주문 전에 먼저 등록 — BlockRequest() 메시지 펌프 race condition 방지
    # (수동 청산과 동일한 순서: pending 선등록 → 주문 → 실패 시 롤백)
    self._set_pending_order(
        kind="EXIT_FULL" if is_full_close else "EXIT_PARTIAL",
        direction=self.position.status,
        qty=send_qty,
        price_hint=price,
        reason=reason,
        stage=stage,
    )
    ret = self._send_broker_exit_order(send_qty)
    _ts_log_diag(
        self,
        "PartialExitSendOrderResult",
        stage=stage,
        ret=ret,
        target_qty=target_qty,
        send_qty=send_qty,
        reason=reason,
        stage_plan=self.position.get_stage_plan(),
        position=_ts_get_position_snapshot(self),
    )
    if ret != 0:
        self._clear_pending_order()
        log_manager.system(
            f"[Exit] 청산 주문 실패 ret={ret} stage={stage} qty={send_qty} — pending 롤백",
            "ERROR",
        )
        return
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
        _tp3_dist = (self.position.tp3_price - price) * _mult
        debug_log.debug(
            "[DBG-F8] %s %dct @%.2f cur=%.2f upnl=%+.2fpt"
            " | stop_dist=%.2f tp1=%.2f tp2=%.2f tp3=%.2f | stop=%.2f | p1=%s p2=%s p3=%s",
            self.position.status, self.position.quantity,
            self.position.entry_price, price, _upnl,
            _stop_dist, _tp1_dist, _tp2_dist, _tp3_dist,
            self.position.stop_price,
            "O" if self.position.partial_1_done else "X",
            "O" if self.position.partial_2_done else "X",
            "O" if self.position.partial_3_done else "X",
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
        ret = self._send_broker_exit_order(self.position.quantity)
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

    if (not self._has_pending_order()
            and self.position.status != "FLAT"
            and self.position.is_tp3_hit(price)):
        self._execute_partial_exit(price, stage=3)

    if not self._has_pending_order() and self.time_exit.should_force_exit():
        log_manager.system(
            f"[ExitAttempt] 시간청산 {self.position.status} {self.position.quantity}ct "
            f"price={price:.2f}",
            "WARNING",
        )
        ret = self._send_broker_exit_order(self.position.quantity)
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
    # P3-b: 역방향 클램프용 마지막 청산 방향 저장
    self._last_exit_direction = str(result.get("executed_direction") or result.get("direction", "") or "")
    msg = (
        f"[ExitCooldown] {result.get('exit_reason', '청산')} 후 {cooldown_min}분 재진입 금지 "
        f"(until {self._exit_cooldown_until.strftime('%H:%M:%S')})"
    )
    logger.warning(msg)
    log_manager.system(msg, "WARNING")


def _ts_check_position_integrity(self) -> bool:
    """P1-b: 엔진·브로커·pending 수량 무결성 검사.

    Returns:
        True  = 정상 (진입 허용)
        False = 불일치 2회 이상 누적 (진입 차단, Slack 경보)
    """
    engine_qty  = int(getattr(self.position, "quantity", 0) or 0)
    broker_qty  = int(getattr(self, "_integrity_broker_qty", 0) or 0)
    pending     = getattr(self, "_pending_order", None)
    pending_qty = int((pending or {}).get("qty", 0) or 0)

    # 포지션 없고 브로커 잔량도 0이면 무결성 OK
    if engine_qty == 0 and broker_qty == 0:
        self._integrity_fail_count = max(0, self._integrity_fail_count - 1)
        return True

    # 브로커 잔량 미수신 상태이면 검사 스킵 (false alarm 방지)
    if broker_qty == 0 and engine_qty > 0:
        return True

    expected_broker = engine_qty + pending_qty
    mismatch = abs(broker_qty - expected_broker)

    if mismatch > 0:
        self._integrity_fail_count += 1
        _msg = (
            f"[Integrity] 수량 불일치 {self._integrity_fail_count}회 — "
            f"engine={engine_qty} broker={broker_qty} pending={pending_qty} "
            f"(expected={expected_broker} diff={mismatch})"
        )
        logger.warning(_msg)
        log_manager.system(_msg, "WARNING")
        if self._integrity_fail_count >= 2:
            try:
                from utils.notify import notify_circuit_breaker
                notify_circuit_breaker(
                    f"포지션 수량 불일치 {self._integrity_fail_count}회 누적",
                    f"engine={engine_qty} broker={broker_qty} pending={pending_qty} — 수동 확인 필요",
                )
            except Exception:
                pass
        if self._integrity_fail_count >= 3:
            self._broker_sync_block_new_entries = True
            log_manager.system(
                "[Integrity] 3회 누적 → 자동진입 차단 + 수동 정리 요망", "CRITICAL"
            )
        return self._integrity_fail_count < 2
    else:
        self._integrity_fail_count = max(0, self._integrity_fail_count - 1)
        return True


def _ts_order_side_to_direction(payload_or_order_gubun) -> str:
    if isinstance(payload_or_order_gubun, dict):
        payload = payload_or_order_gubun
        trade_gubun = str(payload.get("trade_gubun", "")).strip()
        if trade_gubun in ("2", "+2", "매수", "+매수"):
            return "LONG"
        if trade_gubun in ("1", "-1", "매도", "-매도"):
            return "SHORT"
        text = ""
        for key in ("balance_side", "order_gubun", "side", "balance_side_code", "side_code"):
            text = str(payload.get(key, "")).strip()
            if text:
                break
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


def _ts_push_exit_panel_now(self, current_price: float = None) -> None:
    """Chejan 체결 직후 청산 패널을 즉시 갱신해 '주문중' 잔상을 줄인다."""
    if not hasattr(self, "dashboard"):
        return

    _pos = self.position
    _pending = self._pending_order or {}
    _pending_kind = str(_pending.get("kind") or "")
    _pending_reason = str(_pending.get("reason") or "")

    if current_price is None:
        current_price = float(
            getattr(self, "_last_pipeline_price", 0.0)
            or _pos.entry_price
            or 0.0
        )

    _now = datetime.datetime.now()
    _force_dt = datetime.datetime.combine(_now.date(), self.time_exit.FORCE_EXIT)
    _time_left_s = int((_force_dt - _now).total_seconds())
    if _time_left_s < 0:
        _time_left_s = 0

    atr = _ts_get_reference_atr(self, _pending if _pending else None)
    self.dashboard.update_position({
        "status": _pos.status,
        "entry": _pos.entry_price,
        "current": current_price,
        "qty": _pos.quantity,
        "pt_value": self._pt_value,
        "atr": atr,
        "stop": _pos.stop_price,
        "trail_basis": _pos.get_trailing_reference_price(current_price, atr),
        "tp1": _pos.tp1_price,
        "tp2": _pos.tp2_price,
        "tp3": _pos.tp3_price,
        "partial1": _pos.partial_1_done,
        "partial2": _pos.partial_2_done,
        "partial3": _pos.partial_3_done,
        "stage_plan": _pos.get_stage_plan(),
        "entry_time": _pos.entry_time,
        "pending_active": bool(_pending),
        "pending_kind": _pending_kind,
        "pending_reason": _pending_reason,
        "pending_stage": int(_pending.get("stage") or 0),
        "pending_filled": int(_pending.get("filled_qty") or 0),
        "pending_qty": int(_pending.get("qty") or 0),
        "time_exit_countdown_sec": _time_left_s,
    })


def _ts_intrabar_tp_check(self, price: float) -> None:
    """EXIT_PARTIAL 해소 직후 잔여 TP 즉시 재점검 — 다음 분봉 대기 없이 청산 유지.

    _clear_pending_order()에서 QTimer.singleShot(300ms)으로 호출된다.
    하드스톱·슬랭스톱은 분봉 파이프라인이 담당하므로 여기서는 TP만 점검한다.
    """
    # [B114] 가드 실패 케이스별 경고 로그 — 발동 누락 원인 파악용
    if self._has_pending_order():
        logger.warning(
            "[IntrabarTPCheck] skip: pending 존재 kind=%s",
            (self._pending_order or {}).get("kind", "?"),
        )
        return
    if self.position.status == "FLAT":
        logger.warning("[IntrabarTPCheck] skip: FLAT (포지션 없음)")
        return
    if price <= 0:
        logger.warning("[IntrabarTPCheck] skip: price=%.2f", price)
        return
    log_manager.system(
        f"[IntrabarTPCheck] pending 해소 후 TP 즉시 재점검 price={price:.2f} "
        f"p1={self.position.partial_1_done} p2={self.position.partial_2_done} p3={self.position.partial_3_done}",
        "INFO",
    )
    if self.position.is_tp1_hit(price):
        self._execute_partial_exit(price, stage=1)
    if not self._has_pending_order() and self.position.is_tp2_hit(price):
        self._execute_partial_exit(price, stage=2)
    if not self._has_pending_order() and self.position.is_tp3_hit(price):
        self._execute_partial_exit(price, stage=3)


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
        except Exception as _atr_e:
            logger.debug("[ATR] 버퍼 읽기 실패 — 기본값 사용: %s", _atr_e)

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
        entry_horizon=pending.get("entry_horizon"),
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


def _ts_agg_exit_fill(pending: dict, result: dict, fill_price: float, fill_qty: int) -> None:
    """분할체결 집계 누적 — 마지막 체결에서 agg_result 생성에 사용."""
    pending.setdefault("agg_exit_qty", 0)
    pending.setdefault("agg_exit_pnl_pts", 0.0)
    pending.setdefault("agg_exit_pnl_krw", 0.0)
    pending.setdefault("agg_exit_fwd_pts", 0.0)
    pending.setdefault("agg_exit_fwd_krw", 0.0)
    pending.setdefault("agg_exit_price_x_qty", 0.0)
    pending["agg_exit_qty"] += fill_qty
    # pnl_pts는 per-contract이므로 fill_qty로 가중합산 → agg 시 qty로 나눠 per-contract 복원
    pending["agg_exit_pnl_pts"] += float(result.get("pnl_pts", 0.0) or 0.0) * fill_qty
    pending["agg_exit_pnl_krw"] += float(result.get("pnl_krw", 0.0) or 0.0)
    pending["agg_exit_fwd_pts"] += float(result.get("forward_pnl_pts", 0.0) or 0.0) * fill_qty
    pending["agg_exit_fwd_krw"] += float(result.get("forward_pnl_krw", 0.0) or 0.0)
    pending["agg_exit_price_x_qty"] += fill_price * fill_qty


def _ts_build_agg_exit_result(last_result: dict, pending: dict) -> dict:
    """분할체결 집계값을 단일 체결 result로 합산 반환."""
    agg_qty = pending.get("agg_exit_qty", 1)
    price_x_qty = pending.get("agg_exit_price_x_qty", 0.0)
    vwap = price_x_qty / agg_qty if agg_qty > 0 else last_result.get("exit_price", 0.0)
    # agg_exit_pnl_pts는 per-contract × fill_qty의 가중합 → qty로 나눠 per-contract 복원
    raw_pts = pending.get("agg_exit_pnl_pts", last_result.get("pnl_pts", 0.0) * agg_qty)
    raw_fwd = pending.get("agg_exit_fwd_pts", last_result.get("forward_pnl_pts", 0.0) * agg_qty)
    return {
        **last_result,
        "quantity": agg_qty,
        "exit_price": round(vwap, 4),
        "pnl_pts": round(raw_pts / agg_qty, 4) if agg_qty > 0 else 0.0,
        "pnl_krw": round(pending.get("agg_exit_pnl_krw", last_result.get("pnl_krw", 0.0)), 0),
        "forward_pnl_pts": round(raw_fwd / agg_qty, 4) if agg_qty > 0 else 0.0,
        "forward_pnl_krw": round(pending.get("agg_exit_fwd_krw", last_result.get("forward_pnl_krw", 0.0)), 0),
    }


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

    # 분할체결 집계 (CB/Kelly 통계 중복 방지: 마지막 체결에서만 반영)
    _ts_agg_exit_fill(pending, result, fill_price, fill_qty)
    is_last_fill = pending["filled_qty"] >= pending["qty"]

    if pending["kind"] == "EXIT_PARTIAL":
        if pending.get("stage") == 1:
            self.position.partial_1_done = True
        elif pending.get("stage") == 2:
            self.position.partial_2_done = True
        elif pending.get("stage") == 3:
            self.position.partial_3_done = True
        if not is_last_fill:
            log_manager.trade(
                f"[TP{pending.get('stage')} 분할체결] {result.get('direction','')} {fill_qty}계약 @ {fill_price:.2f} "
                f"| 잔여포지션={result.get('remaining', '?')}계약"
            )
            QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))
            return
        agg_result = _ts_build_agg_exit_result(result, pending)
        self._post_partial_exit(agg_result, pending.get("stage") or 1)
        QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))
        return

    if pending["kind"] == "EXIT_MANUAL_PARTIAL":
        if pending.get("stage") == 1:
            self.position.partial_1_done = True
        elif pending.get("stage") == 2:
            self.position.partial_2_done = True
        elif pending.get("stage") == 3:
            self.position.partial_3_done = True
        if not is_last_fill:
            log_manager.trade(
                f"[수동청산 분할체결] {result.get('direction','')} {fill_qty}계약 @ {fill_price:.2f} "
                f"| 잔여포지션={result.get('remaining', '?')}계약"
            )
            QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))
            return
        agg_result = _ts_build_agg_exit_result(result, pending)
        _ts_record_nonfinal_exit(self, agg_result, pending["reason"])
        self.dashboard.minute_chart_record_exit(
            agg_result["exit_price"],
            filled_at,
            finalize=False,
            pnl_pts=agg_result.get("pnl_pts"),
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

    # EXIT_FULL 분할체결 — 중간 체결은 로그만, 통계 없음
    if not is_last_fill:
        log_manager.trade(
            f"[체결청산-부분] {result.get('direction','')} {fill_qty}계약 @ {fill_price:.2f} "
            f"| PnL={result.get('pnl_pts',0):+.2f}pt ({result.get('pnl_krw',0):+,.0f}원) "
            f"| 잔여={result.get('remaining', '?')}계약 | 사유={pending['reason']}"
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

    # 최종 체결 (전량 또는 주문 완결) — 집계 결과로 통계 반영
    agg_result = _ts_build_agg_exit_result(result, pending)
    _ts_apply_exit_cooldown(self, agg_result, filled_at)
    self._exit_cooldown_applied_this_fill = True
    self._post_exit(agg_result, filled_at=filled_at)
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
    reason_label = "미추적체결(pending_miss)"
    atr = _ts_get_reference_atr(self)

    log_manager.system(
        f"[OrderSync] 미추적 체결 감지 (pending_miss) order_no={payload.get('order_no') or '?'} "
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
            self._post_exit(result, filled_at=filled_at)
            if self.position.status == "FLAT":
                self.dashboard.minute_chart_clear_active_position()
                _ts_force_balance_flat_ui(self, f"external_exit:{reason_label}")
            _ts_system_info_throttled(self, "balance_refresh_trigger_external_exit", "[BalanceRefresh] trigger=ExternalFill final_exit retries=250ms,1200ms", min_interval_sec=30.0)
            QTimer.singleShot(250, lambda: _ts_refresh_dashboard_balance(self))
            QTimer.singleShot(1200, lambda: _ts_refresh_dashboard_balance(self))

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
        _ts_system_info_throttled(
            self,
            "balance_refresh_trigger_external_entry",
            "[BalanceRefresh] trigger=ExternalFill entry retries=250ms,1200ms",
            min_interval_sec=30.0,
        )
        QTimer.singleShot(250, lambda: _ts_refresh_dashboard_balance(self))
        QTimer.singleShot(1200, lambda: _ts_refresh_dashboard_balance(self))

    after = _ts_get_position_snapshot(self)
    log_manager.system(
        f"[OrderSync] 미추적 체결 반영 완료 (pending_miss) order_no={payload.get('order_no') or '?'} after={after}",
        "WARNING",
    )


def _ts_resolve_stuck_entry_pending(self) -> bool:
    """ENTRY 부분체결 stuck 시 브로커 잔고 TR 조회 → 실제 수량으로 포지션 보정.

    반환:
        True  — 브로커 조회 성공, 포지션 sync 완료 (pending은 내부 처리)
        False — 브로커 조회 실패 또는 잔고 행 해석 불가
    """
    pending = self._pending_order or {}
    if pending.get("kind") != "ENTRY":
        return False

    account_no = str(_secrets.ACCOUNT_NO or "").strip()
    target_code = self._normalize_broker_code(getattr(self, "_futures_code", ""))
    if not account_no or not target_code:
        return False

    result = self.broker.request_futures_balance(account_no)
    if result is None:
        log_manager.system(
            "[EntryStuck] ENTRY stuck 브로커 잔고 TR 실패 — pending 유지",
            "WARNING",
        )
        return False

    _ts_push_balance_to_dashboard(self, result)

    rows = result.get("nonempty_rows") or result.get("rows") or []
    broker_row = None
    for row in rows:
        row_code = self._normalize_broker_code(row.get("종목코드") or row.get("code") or "")
        if row_code == target_code:
            broker_row = row
            break

    def _num(value):
        try:
            return float(str(value or "").replace(",", "").strip())
        except Exception:
            return 0.0

    if broker_row is None:
        # 브로커 무포지션 → 체결이 실제로 안 됐거나 취소됨
        before = _ts_get_position_snapshot(self)
        self.position.sync_flat_from_broker()
        self.dashboard.minute_chart_clear_active_position()
        self._clear_pending_order()
        _ts_set_broker_sync_status(self, True, "entry stuck: broker confirms flat", False)
        log_manager.system(
            f"[EntryStuck] 브로커 무포지션 확인 → {before} => FLAT (진입 미체결 처리)",
            "WARNING",
        )
        return True

    broker_qty = int(_num(broker_row.get("잔고수량") or broker_row.get("position_qty") or broker_row.get("qty")))
    broker_avg = _num(
        broker_row.get("평균가") or broker_row.get("매입단가")
        or broker_row.get("avg_price") or broker_row.get("buy_avg_price")
        or broker_row.get("sell_avg_price")
    )
    broker_side = _ts_order_side_to_direction({
        "balance_side": broker_row.get("구분") or broker_row.get("매매구분"),
        "balance_side_code": broker_row.get("side_code"),
    })

    if broker_qty <= 0 or broker_avg <= 0 or broker_side not in ("LONG", "SHORT"):
        log_manager.system(
            f"[EntryStuck] 브로커 행 해석 실패 row={broker_row} — pending 유지",
            "WARNING",
        )
        return False

    before_qty = self.position.quantity
    # 브로커 실수량으로 포지션 sync (이벤트 유실로 인한 수량 불일치 해소)
    self.position.sync_from_broker(
        direction=broker_side,
        price=broker_avg,
        quantity=broker_qty,
        atr=max(_ts_get_reference_atr(self), 0.5),
        grade=pending.get("grade") or "BROKER",
        regime=self.current_regime or "BROKER_SYNC",
    )
    self.dashboard.minute_chart_sync_active_position(
        broker_side, broker_avg, self.position.entry_time,
    )
    _ts_set_broker_sync_status(
        self, True,
        f"entry stuck resolved broker {broker_side} {broker_qty} @ {broker_avg}",
        False,
    )
    self._clear_pending_order()
    log_manager.system(
        f"[EntryStuck] 브로커 잔량 확인 → position.qty {before_qty} → {broker_qty}계약 @ {broker_avg:.2f} sync 완료",
        "WARNING",
    )
    return True


def _ts_resolve_stuck_exit_pending(self) -> bool:
    pending = self._pending_order or {}
    if pending.get("kind") not in ("EXIT_FULL", "EXIT_PARTIAL", "EXIT_MANUAL_PARTIAL"):
        return False

    account_no = str(_secrets.ACCOUNT_NO or "").strip()
    target_code = self._normalize_broker_code(getattr(self, "_futures_code", ""))
    if not account_no or not target_code:
        return False

    result = self.broker.request_futures_balance(account_no)
    if result is None:
        log_manager.system(
            "[PendingOrder] EXIT partial fill timeout but broker balance TR failed; pending 유지",
            "WARNING",
        )
        return False

    _ts_push_balance_to_dashboard(self, result)

    rows = result.get("nonempty_rows") or result.get("rows") or []
    broker_row = None
    for row in rows:
        row_code = self._normalize_broker_code(row.get("종목코드") or row.get("code") or "")
        if row_code == target_code:
            broker_row = row
            break

    if broker_row is None:
        before = _ts_get_position_snapshot(self)

        # [Fix1] stuck exit 차트·DB 합성 기록
        # _active_trade가 clear 전에 completed_trades로 이동해야 이력이 보존됨
        _sq_filled = int(pending.get("agg_exit_qty") or 0)
        _sq_price_x_qty = float(pending.get("agg_exit_price_x_qty") or 0.0)
        _sq_pnl_pts = float(pending.get("agg_exit_pnl_pts") or 0.0)
        _sq_pnl_krw = float(pending.get("agg_exit_pnl_krw") or 0.0)
        _sq_direction = str(pending.get("direction") or "")
        _sq_last_fill_at = pending.get("last_fill_at") or datetime.datetime.now()
        _sq_avg_price = (
            _sq_price_x_qty / _sq_filled
            if _sq_filled > 0 and _sq_price_x_qty > 0
            else float(pending.get("price_hint") or 0.0)
        )
        if _sq_avg_price > 0:
            # (a) 차트 — finalize=True 로 _active_trade → completed_trades 이동
            self.dashboard.minute_chart_record_exit(
                _sq_avg_price,
                _sq_last_fill_at,
                finalize=True,
                pnl_pts=_sq_pnl_pts,
                reason="stuck_exit_flat",
                direction=_sq_direction,
            )
            # (b) trades DB — 집계된 체결 수량만큼 합성 기록
            if _sq_filled > 0:
                _sq_entry_price = float(getattr(self.position, "entry_price", 0.0) or 0.0)
                _sq_entry_time = getattr(self.position, "entry_time", None) or _sq_last_fill_at
                _sq_result = {
                    "direction": _sq_direction,
                    "entry_price": _sq_entry_price,
                    "exit_price": _sq_avg_price,
                    "quantity": _sq_filled,
                    "pnl_pts": _sq_pnl_pts,
                    "pnl_krw": _sq_pnl_krw,
                    "forward_pnl_pts": float(pending.get("agg_exit_fwd_pts") or _sq_pnl_pts),
                    "forward_pnl_krw": float(pending.get("agg_exit_fwd_krw") or _sq_pnl_krw),
                    "exit_reason": "stuck_exit_flat",
                    "grade": str(pending.get("grade") or ""),
                    "entry_ts": (
                        _sq_entry_time.strftime("%Y-%m-%d %H:%M:%S")
                        if hasattr(_sq_entry_time, "strftime")
                        else str(_sq_entry_time)
                    ),
                    "exit_ts": (
                        _sq_last_fill_at.strftime("%Y-%m-%d %H:%M:%S")
                        if hasattr(_sq_last_fill_at, "strftime")
                        else str(_sq_last_fill_at)
                    ),
                }
                try:
                    self._record_trade_result(_sq_result)
                    self._refresh_pnl_history()
                except Exception as _sq_e:
                    log_manager.system(
                        f"[ChartFix] stuck exit DB 합성 기록 실패(무해): {_sq_e}", "WARNING"
                    )
            log_manager.system(
                f"[ChartFix] stuck exit 차트·DB 합성 기록: {_sq_direction} {_sq_filled}계약 "
                f"@ {_sq_avg_price:.2f} pnl={_sq_pnl_pts:+.2f}pt",
                "INFO",
            )

        self.position.sync_flat_from_broker()
        self.dashboard.minute_chart_clear_active_position()
        self._clear_pending_order()
        _ts_set_broker_sync_status(self, True, "stuck exit resolved flat by broker balance", False)
        log_manager.system(
            f"[PendingOrder] EXIT partial fill timeout -> 브로커 무포지션 확인, {before} => FLAT",
            "WARNING",
        )
        return True

    def _num(value) -> float:
        try:
            return float(str(value or "").replace(",", "").strip())
        except Exception:
            return 0.0

    qty = int(_num(broker_row.get("잔고수량") or broker_row.get("position_qty") or broker_row.get("qty")))
    avg_price = _num(
        broker_row.get("평균가")
        or broker_row.get("매입단가")
        or broker_row.get("avg_price")
        or broker_row.get("buy_avg_price")
        or broker_row.get("sell_avg_price")
    )
    side = _ts_order_side_to_direction({
        "balance_side": broker_row.get("구분") or broker_row.get("매매구분"),
        "balance_side_code": broker_row.get("side_code"),
    })

    if qty <= 0 or avg_price <= 0 or side not in ("LONG", "SHORT"):
        log_manager.system(
            f"[PendingOrder] EXIT partial fill timeout -> 브로커 행 해석 실패, pending 유지 row={broker_row}",
            "WARNING",
        )
        return False

    # sync 전 포지션 수량 저장 — expected_remaining 비교에 사용
    prev_pos_qty = self.position.quantity

    entry_time_hint = self.position.entry_time or self.position.peek_saved_entry_time(side)
    self.position.sync_from_broker(
        direction=side,
        price=avg_price,
        quantity=qty,
        atr=max(_ts_get_reference_atr(self), 0.5),
        synced_at=entry_time_hint,
        grade="BROKER",
        regime=self.current_regime or "BROKER_SYNC",
    )
    self.dashboard.minute_chart_sync_active_position(
        side,
        avg_price,
        self.position.entry_time,
    )

    if side == pending.get("direction"):
        # Chejan 이벤트 유실 감지: 브로커 잔량이 (진입수량 - 주문수량)과 일치하면
        # 실제로는 전량 체결됐음에도 이벤트 누락으로 부분체결로 오판한 것 → pending 소멸
        expected_remaining = prev_pos_qty - pending.get("qty", 0)
        if qty == expected_remaining:
            self._clear_pending_order()
            _ts_set_broker_sync_status(
                self, True,
                f"stuck exit resolved via broker qty match {side} {qty} @ {avg_price}",
                False,
            )
            log_manager.system(
                f"[PendingOrder] EXIT partial fill timeout -> "
                f"브로커 잔량 {qty}계약 = 예상잔량 {expected_remaining}계약 일치 "
                f"→ Chejan 이벤트 유실로 인한 오판, pending 소멸",
                "WARNING",
            )
            return True
        pending["last_fill_at"] = datetime.datetime.now()
        _ts_set_broker_sync_status(self, True, f"stuck exit still holding {side} {qty} @ {avg_price}", False)
        log_manager.system(
            f"[PendingOrder] EXIT partial fill timeout -> 브로커 잔량 확인 {side} {qty} @ {avg_price:.2f}, pending 유지",
            "WARNING",
        )
        return True

    self._clear_pending_order()
    _ts_set_broker_sync_status(self, True, f"stuck exit resolved broker side {side} {qty} @ {avg_price}", False)
    log_manager.system(
        f"[PendingOrder] EXIT partial fill timeout -> 브로커 반대포지션 동기화 {side} {qty} @ {avg_price:.2f}",
        "CRITICAL",
    )
    # 의도한 청산 방향과 반대 포지션이 남은 경우 → 즉시 긴급청산 (하드스톱 다음분봉 대기 제거)
    _force_price = getattr(self, "_last_pipeline_price", 0.0) or avg_price
    if _force_price > 0 and self.position.status != "FLAT":
        log_manager.system(
            f"[PendingOrder] EXIT잔여 반대포지션({side} {qty}계약) → 즉시 긴급청산 @ {_force_price:.2f}",
            "CRITICAL",
        )
        self.exit_manager.force_exit(_force_price, reason="EXIT잔여 반대포지션 긴급청산")
    return True


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
        _completed = getattr(self, "_completed_order_nos", [])
        if order_no and order_no in _completed:
            log_manager.system(
                f"[ChejanDup] 중복 콜백 무시 order_no={order_no} side={side} qty={fill_qty}",
                "WARNING",
            )
            return
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

    if payload.get("position_qty") is not None or payload.get("closable_qty") is not None:
        _ts_sync_from_balance_payload(self, payload)

    if pending["filled_qty"] >= pending["qty"]:
        self._clear_pending_order()
        # [B112] 청산 완전 체결 후 FLAT이면 stale broker_sync_reason 클리어
        # stuck 해소 캐시("entry stuck resolved broker LONG N @ price")가
        # 다음 EntryAttempt 까지 남아 오염되는 문제 방지
        if self.position.status == "FLAT":
            self._broker_sync_last_error = "flat after exit"


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
    # pending EXIT 주문 대기 중이면 합성 행 생성 억제 (체결 콜백 도착 전 깜빡임 방지)
    _pending_is_exit = (
        getattr(self, "_pending_order", None) is not None
        and str(self._pending_order.get("kind", "")).startswith("EXIT")
    )
    if not _has_real_row and self.position.status != "FLAT" and not _pending_is_exit:
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

    def _parse_closable_qty(row):
        for key in ("청산가능", "주문가능수량", "청산가능수량"):
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

    _pending_exists = getattr(self, "_pending_order", None) is not None
    if rows and self.position.status == "FLAT" and not _pending_exists:
        filtered_rows = []
        suppressed_rows = []
        for row in rows:
            qty = _parse_qty(row)
            closable_qty = _parse_closable_qty(row)
            if qty > 0 and closable_qty <= 0:
                suppressed_rows.append(row)
                continue
            filtered_rows.append(row)
        if suppressed_rows:
            rows = filtered_rows
            logger.warning(
                "[BalanceUIGhostRow] suppressed stale broker rows flat=%s pending=%s suppressed=%s kept=%s",
                self.position.status,
                _pending_exists,
                suppressed_rows,
                rows,
            )

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
        except Exception as _brk_e:
            logger.warning("[Balance] 실현손익 파싱 실패 — ProfitGuard 기준값 부정확 가능성: %s", _brk_e)
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
    if is_cybos_balance and not quiet:
        try:
            import datetime as _dt
            _today = _dt.date.today()
            _yesterday = (_today - _dt.timedelta(days=1)).isoformat()
            _today_str = _today.isoformat()
            _today_pnl = float(str(summary.get("실현손익") or "0").replace(",", "") or "0")
            _prev_pnl  = float(str(summary.get("추정자산") or "0").replace(",", "") or "0")
            # FLAT 상태에서만 저장: 포지션 보유 중 CpTd6197 today_pnl에 미실현손익이
            # 포함되면 broker_daily_pnl 테이블이 오염되어 손익 추이 탭 값이 부풀려짐.
            if self.position.status == "FLAT":
                upsert_daily_broker_pnl(_today_str, _today_pnl)
                self._refresh_pnl_history()
            upsert_daily_broker_pnl(_yesterday, _prev_pnl)
        except Exception as _bpnl_e:
            logger.debug("[BrokerPnl] 일별 손익 저장 실패: %s", _bpnl_e)

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

    rows = result.get("rows") or []
    nonempty_rows = result.get("nonempty_rows") or []
    all_blank_rows = bool(result.get("all_blank_rows"))
    # before=FLAT + rows=0: 정상 무포지션 확인 → DEBUG (실전 포지션 보유 중이면 WARNING 유지)
    _is_flat_confirm = (before == "FLAT" and not rows)
    _balance_log = logger.debug if _is_flat_confirm else logger.warning
    _balance_log(
        "[BrokerSync] balance result rows=%d nonempty=%d summary_nonblank=%s probe_nonblank=%s summary=%s",
        len(rows),
        len(nonempty_rows),
        any(str(v).strip() for v in (result.get("summary") or {}).values()),
        any(str(v).strip() for v in (result.get("summary_probe") or {}).values()),
        result.get("summary") or {},
    )
    _ts_push_balance_to_dashboard(self, result)

    _balance_log(
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
            _blank_log = logger.info if _is_flat_confirm else logger.warning
            _blank_log(
                "[BrokerSync] blank-as-flat decision before=%s rows=%s summary=%s probe=%s",
                before,
                rows,
                result.get("summary") or {},
                result.get("summary_probe") or {},
            )
            # Cybos 모의투자 서버는 잔고 TR summary/rows가 blank일 수 있으므로 저장 포지션이 있으면 유지
            try:
                _server_gubun = self.broker.get_login_info("GetServerGubun")
            except Exception as _sg_e:
                logger.debug("[Balance] GetServerGubun 조회 실패: %s", _sg_e)
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
            # P1-a: blank-as-flat = FLAT 확인 완료 → Armistice 즉시 해제 (sync_count=2 직접 설정)
            # +1 방식은 FLAT 재시작 시 두 번째 sync가 영구적으로 오지 않아 장 종료까지 Armistice가 지속되는 버그 유발
            self._restart_armistice_sync_count = 2
            logger.info(
                "[BrokerSync] startup sync 무포지션 확인(blank rows): %s -> FLAT (armistice cleared)",
                before,
            )
            if _is_flat_confirm:
                logger.debug(
                    "[BrokerSyncFlatPlaceholder] before=%r | raw_rows=%s | rows=%d | all_blank_rows=%s",
                    before, rows, len(rows), all_blank_rows,
                )
            else:
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

    def _to_int(value) -> int:
        try:
            return int(str(value or "").replace(",", "").strip() or "0")
        except (ValueError, TypeError):
            return 0

    def _to_float(value) -> float:
        try:
            return float(str(value or "").replace(",", "").strip() or "0")
        except (ValueError, TypeError):
            return 0.0

    qty = _to_int(
        payload.get("holding_qty")
        or payload.get("position_qty")
        or payload.get("buy_balance")
        or payload.get("sell_balance")
    )
    closable_qty = _to_int(payload.get("available_qty") or payload.get("closable_qty"))
    avg_price = _to_float(
        payload.get("avg_price")
        or payload.get("buy_avg_price")
        or payload.get("sell_avg_price")
        or payload.get("fill_price")
    )
    # P1-b: balance 이벤트에서 브로커 보유수량 갱신 (integrity checksum용)
    self._integrity_broker_qty = closable_qty if closable_qty > 0 else qty
    side = _ts_order_side_to_direction(payload)
    before = _ts_get_position_snapshot(self)
    logger.warning(
        "[BrokerSync] balance chejan payload before=%s qty=%s closable=%s avg=%s side=%s raw=%s",
        before, qty, closable_qty, avg_price, side, payload,
    )
    _ts_log_diag(
        self,
        "BalanceChejanFlow",
        before=before,
        code=code,
        target_code=target_code,
        qty=qty,
        closable_qty=closable_qty,
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
            f"balance chejan parse failure side={payload.get('balance_side')} qty={qty} closable={closable_qty} avg={avg_price}",
            True,
        )
        log_manager.system(
            f"[BrokerSync] 잔고 Chejan 해석 실패 code={code} side={payload.get('balance_side')} qty={qty} closable={closable_qty} avg={avg_price}",
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
    # EXIT pending이 날아가 있는 중이면 소멸 금지 — Chejan이 돌아올 때 매칭돼야 함
    _pending = self._pending_order
    if _pending and _pending.get("kind", "").startswith("EXIT"):
        log_manager.system(
            f"[BrokerSync] 잔고 Chejan — EXIT pending 진행 중, pending 유지 "
            f"(kind={_pending.get('kind')} order_no={_pending.get('order_no') or '?'})",
            "INFO",
        )
    else:
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
    entry_horizon: str = None,
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
    # [Fix-PendingFirst] CYBOS BlockRequest()는 COM 이벤트 루프를 pump하므로
    # send_market_order() 반환 전에 Chejan 콜백이 먼저 실행될 수 있음.
    # pending을 SendOrder 이전에 등록해 pending_matched=False 및 ret=1 오판 방지.
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
    # 낙관적 오픈 후 분할체결 VWAP 보정을 위한 플래그
    self._pending_order["optimistic_opened"] = True
    self._pending_order["partial_fill_count"] = 0
    self._pending_order["entry_horizon"] = entry_horizon
    ret = self._send_broker_entry_order(direction, quantity)
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
    # [C1] BlockRequest가 백그라운드 스레드에서 완료된 후 _pending_order가
    # None으로 변경되었을 경우 방어: 큐에 쌓인 Chejan이 이미 체결 처리를 완료했을 수 있음.
    if self._pending_order is None:
        logger.warning("[Entry] _pending_order가 BlockRequest 완료 후 None — Chejan 선행 체결 처리로 추정, 진입 완료로 간주")
        return
    if ret != 0:
        # -99는 BlockRequest 타임아웃. CB API지연 트리거 발동 후 롤백.
        if ret == -99:
            log_manager.system(
                f"[Entry] BlockRequest 타임아웃(-99) — 주문 상태 불명. CB 발동 + pending 롤백.",
                "ERROR",
            )
            self.circuit_breaker.check_api_delay(10.0)  # CB 트리거 ⑤ 강제 발동
            self._clear_pending_order()
            return
        _already_filled = (self._pending_order or {}).get("filled_qty", 0)
        if _already_filled > 0:
            logger.warning(
                "[Entry] ret=%s but filled_qty=%s 이미 체결 → 주문 접수된 것으로 처리",
                ret, _already_filled,
            )
            log_manager.system(
                f"[Entry] ret={ret} 오류코드이나 filled_qty={_already_filled} 확인 → pending 유지",
                "WARNING",
            )
        else:
            logger.error("[Entry] SendOrder 실패로 내부 포지션 오픈을 취소합니다. ret=%s", ret)
            log_manager.system(
                f"[Entry] 주문 실패로 포지션 미오픈 ret={ret} raw={raw_direction} final={direction} "
                f"qty={quantity} reverse_entry={'ON' if reverse_enabled else 'OFF'}",
                "ERROR",
            )
            self._clear_pending_order()  # pending 롤백
            return
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
            entry_horizon=entry_horizon,
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
        # P1-a: Armistice sync 카운터 — 2회 누적 후 유예 해제 가능
        self._restart_armistice_sync_count = getattr(
            self, "_restart_armistice_sync_count", 0
        ) + 1
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

    # 낙관적 오픈 주문의 두 번째 이후 분할체결: 수량 증가 없이 VWAP 가격 보정
    # _optimistic=False이면 첫 보정은 이미 완료됨 → 이후 체결은 평균가 업데이트만
    if (
        pending.get("optimistic_opened")
        and self.position.status == entry_direction
        and not self.position._optimistic
    ):
        prev_count = pending.get("partial_fill_count", 0)
        total_count = prev_count + fill_qty
        if total_count > 0:
            vwap = (self.position.entry_price * prev_count + fill_price * fill_qty) / total_count
        else:
            vwap = fill_price
        self.position.entry_price = vwap
        pending["partial_fill_count"] = total_count
        if filled_at:
            self.position.entry_time = filled_at
        self.position._recalculate_levels(_ts_get_reference_atr(self, pending))
        self.position._save_state()
        result = {
            "avg_entry_price": round(vwap, 4),
            "position_qty": self.position.quantity,
        }
        log_manager.trade(
            f"[체결진입보정] {entry_direction} {fill_qty}계약 @ {fill_price} "
            f"| 평균={result['avg_entry_price']} 보유={result['position_qty']}계약"
        )
    else:
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
        # 첫 체결 완료: partial_fill_count 초기화 (이후 분할체결 VWAP 기준점)
        if pending.get("optimistic_opened"):
            pending["partial_fill_count"] = fill_qty
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
    # status 블랭크 + fill_qty > 0 → Cybos GetHeaderValue 인덱스 불일치 대응 폴백
    is_final_fill = (status == "체결") or (
        not status and fill_qty > 0 and fill_price > 0
    )

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
            # order_no 미확보 시 방향 교차 검증으로 오탐 매칭 차단
            # ENTRY pending → 같은 방향 체결만 허용
            # EXIT_* pending → 반대 방향 체결만 허용 (LONG 포지션 청산은 SELL)
            _pending_kind = pending.get("kind", "")
            _pending_dir = pending.get("direction", "")
            _dir_ok = (
                not side  # side 불명이면 관대하게 허용
                or (_pending_kind == "ENTRY" and side == _pending_dir)
                or (_pending_kind not in ("ENTRY",) and side != _pending_dir)
            )
            if _dir_ok:
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
        _completed = getattr(self, "_completed_order_nos", [])
        if order_no and order_no in _completed:
            log_manager.system(
                f"[ChejanDup] 중복 콜백 무시 order_no={order_no} side={side} qty={fill_qty}",
                "WARNING",
            )
            return
        _ts_handle_external_fill(self, payload, side, fill_qty, fill_price, filled_at)
        return

    pending["filled_qty"] += fill_qty
    pending["last_fill_at"] = datetime.datetime.now()
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

    _ts_push_exit_panel_now(self, current_price=(fill_price or pending.get("price_hint") or 0.0))

    if pending["filled_qty"] >= pending["qty"]:
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
TradingSystem._intrabar_tp_check = _ts_intrabar_tp_check


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
    import traceback as _tb
    # DB 초기화
    init_all_dbs()
    logger.info("[System] DB 초기화 완료")

    try:
        system = TradingSystem()
    except Exception as _init_exc:
        _crash_msg = _tb.format_exc()
        print("[CRASH] TradingSystem.__init__ 실패:\n" + _crash_msg, flush=True)
        logger.error("[System] TradingSystem 초기화 실패: %s", _init_exc)
        try:
            import os as _os
            with open(_os.path.join("logs", "crash_init.log"), "a", encoding="utf-8") as _f:
                import datetime as _dt
                _f.write("[%s]\n%s\n" % (_dt.datetime.now().isoformat(), _crash_msg))
        except Exception:
            pass
        raise
    system.run()


if __name__ == "__main__":
    main()
