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
from PyQt5.QtCore import QObject, Qt, QThread, QTimer, pyqtSignal
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
    fetch_recent_raw_features, fetch_recent_raw_candles,
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
    SIGNAL_DECAY_EXIT_ENABLED,
    LOSS_TIER1_ENABLED, LOSS_TIER1_TICK_ENABLED,
    TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED, TOXICITY_SEVERE_SPREAD_BLOCK_TICKS,
    LIMIT_ENTRY_FIRST_ENABLED, LIMIT_ENTRY_TIMEOUT_SEC,
    HZ_DEPLOY_POLICY,
    HURST_RANGE_THRESHOLD, ATR_MIN_ENTRY, ATR_MAX_ENTRY, ATR_OPEN_GAP_MULT,
    ATR_STOP_MULT, ATR_HORIZON_TP1_MULT, ATR_TP1_MULT,
    HURST_REGIME_ATR_MULT, HURST_REGIME_ATR_MULT_ENABLED,
    HURST_SOFT_BLOCK_ENABLED, HURST_SOFT_BLOCK_SIZE_MULT,
    ATR_ADAPTIVE_MAX_WINDOW, ATR_ADAPTIVE_MAX_MULT, ATR_ADAPTIVE_MAX_CEILING,
    ATR_ADAPTIVE_MIN_SAMPLES,
    ATR_EXPIRY_CEILING_ENABLED, ATR_EXPIRY_CEILING_DAYS_BEFORE,
    ATR_EXPIRY_CEILING_DAYS_AFTER, ATR_EXPIRY_CEILING_MULT,
    CB_HIGH_CONF_THRESHOLD, MAX_CONTRACTS,
    SHAP_MIN_DATA_POINTS,
    FRED_API_KEY,
    HEALTH_LATENCY_WARN_MS, HEALTH_LATENCY_CRIT_MS,
    HEALTH_QUALITY_WARN, HEALTH_QUALITY_CRIT,
    HEALTH_CACHE_AGE_WARN_SEC, HEALTH_CACHE_AGE_CRIT_SEC,
    HEALTH_EXCEPTION_DENSITY_WARN_10M, HEALTH_EXCEPTION_DENSITY_CRIT_10M,
    HEALTH_EXCEPTION_EXCLUDE_TAGS,
    HEALTH_TREND_WINDOW_MIN,
    HEALTH_DEGRADED_ENABLED, HEALTH_DEGRADED_ENTER_STREAK, HEALTH_DEGRADED_EXIT_STREAK,
    HEALTH_DEGRADED_WINDOW, HEALTH_DEGRADED_EXIT_RATIO,
    HEALTH_DEGRADED_SIZE_MULT, HEALTH_DEGRADED_MIN_CONF,
    HEALTH_DEGRADED_BLOCK_AUTO_ENTRY, HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY,
    HEALTH_POLICY_HOT_RELOAD_ENABLED, HEALTH_POLICY_HOT_RELOAD_INTERVAL_SEC,
    ENTRY_GRADE_C_AUTO_EXP, C_AUTO_EXP_SIZE_MULT, C_AUTO_EXP_ZONES,  # [P5]
    ENS_CONF_FLOOR_FOR_AUTO,                                          # [239차] C급 conf_floor
    REGIME_EXHAUSTION_EXT_ATR_THRESHOLD,                              # [379차]
)
import config.settings as runtime_settings
from config.constants import MINI_FUTURES_PT_VALUE, get_contract_spec, CB_STATE_HALTED, DIRECTION_FLAT
from config import secrets as _secrets

# ── 핵심 모듈 ──────────────────────────────────────────────────
from collection.broker import create_broker
from collection.macro.regime_classifier import RegimeClassifier
from collection.macro.micro_regime import MicroRegimeClassifier, REGIME_EXHAUSTION
from collection.macro.macro_fetcher import MacroFetcher
from collection.macro.intraday_tactical_regime import (
    IntradayTacticalRegime,
    INTRADAY_NORMAL, INTRADAY_DAY_RISK_OFF, INTRADAY_CRASH,
)
from collection.options.pcr_store import PCRStore
from collection.options.option_chain_snapshot import OptionChainSnapshot
from collection.options.option_chain_worker import OptionChainWorker
from features.macro.macro_feature_transformer import MacroFeatureTransformer
from features.options.option_features import OptionFeatureCalculator
from learning.self_learning.daily_consolidator import DailyConsolidator
from learning.self_learning.drift_adjuster import DriftAdjuster
from features.feature_builder import FeatureBuilder
from features.technical.basis import BasisCalculator
from features.technical.expiry import is_near_monthly_expiry
from collection.cybos.api_connector import VKOSPI_INDEX_CODE
from features.bar_aggregator import BarAggregator
from model.multi_horizon_model import MultiHorizonModel, apply_robust_preprocess
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
from strategy.entry.fq_accuracy_gate import compute_fq_adjusted_min_conf
from strategy.exit.time_exit import TimeExitManager
from strategy.risk.toxicity_gate import ToxicityGate
from strategy.runtime.broker_runtime_service import BrokerRuntimeService
from strategy.runtime.execution_governor import ExecutionGovernor
from strategy.runtime.session_recovery_service import SessionRecoveryService
from strategy.profit_guard import ProfitGuard, ProfitGuardConfig
from learning.calibration import (
    MultiHorizonCalibrator, MultiHorizonExtremityCorrector, compute_extremity_hinge,
)
from learning.online_learner import OnlineLearner
from learning.prediction_buffer import PredictionBuffer
from learning.batch_retrainer import BatchRetrainer, MIN_TRAIN_BARS as _MIN_TRAIN_BARS
from learning.threshold_recalibrator import ThresholdRecalibrator
from learning.atr_ceiling_recalibrator import ATRCeilingRecalibrator
from learning.entry_horizon_recalibrator import EntryHorizonRecalibrator
from learning.shap.shap_tracker import ShapTracker, compute_horizon_importance
from features.horizon_feature_registry import get_available_feature_set
from safety.circuit_breaker import CircuitBreaker
from safety.kill_switch import KillSwitch
from safety.emergency_exit import EmergencyExit
from safety.system_health import SystemHealthScore
from logging_system.log_manager import log_manager
from utils.time_utils import (
    is_market_open, is_trading_day, get_time_zone, is_force_exit_time, is_new_entry_allowed,
    is_pre_market, NEW_ENTRY_CUTOFF,
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


class _DailyCloseUiSignal(QObject):
    """DailyClose 스레드 → 메인 Qt 스레드 대시보드 갱신 (스레드-안전).

    daily_close()는 백그라운드 스레드(_run_daily_close)에서 실행되는데
    update_strategy_ops/update_trend/update_exchange_cb_badge 등 대시보드 위젯을
    거기서 직접 호출하면 GUI 스레드 밖에서 위젯을 조작하게 되어 PyQt에서
    정의되지 않은 동작(access violation)이 발생한다.
    ([304차 후속] 0708 15:40~15:43 daily_close 재진입마다 access violation →
    launcher AUTO-RESTART → daily_close 재실행이 반복되는 크래시 루프 실측.
    crash_fault.log: main.py:8413 daily_close → dashboard.update_strategy_ops →
    set_fingerprint_level → refresh 스택에서 크래시. log_manager.py의
    _warn_cross_thread 계측(302차)이 지목한 근본 원인과 동일 — GUI 콜백은
    반드시 메인 스레드에서 실행되어야 한다.)
    QueuedConnection으로 연결하면 emit()을 어느 스레드에서 호출해도
    슬롯은 반드시 메인 이벤트 루프에서 실행된다.
    payload는 인자 없이 호출 가능한 callable(주로 lambda) — 대시보드 위젯을
    건드리는 코드 조각을 통째로 메인 스레드로 옮길 수 있게 한다.
    """
    request = pyqtSignal(object)


_daily_close_ui_sig = _DailyCloseUiSignal()  # 모듈 로드(메인 스레드)에서 생성 — thread affinity = main


def _is_deployable(hz, bar_aggregator):
    # type: (str, object) -> bool
    """호라이즌별 배포 정책에 따라 이번 분에 predict_proba를 앙상블에 반영할지 결정.

    Returns:
        True  → predict_proba() 결과를 앙상블에 포함
        False → 해당 호라이즌 스킵 (완성봉 캐시 오래됨 — 학습/추론 분포 불일치 방지)
    """
    policy = HZ_DEPLOY_POLICY.get(hz, {"mode": "always", "max_age": 999})
    mode = policy["mode"]
    max_age = policy["max_age"]

    if mode == "always":
        return True
    if mode == "filter_only":
        # 앙상블 가중합에서 제외하되 30m 필터로 전달 — ensemble_decision 내부에서 차단
        return True
    # "bar_only" or "bar_plus1"
    return bar_aggregator.is_bar_fresh(hz, max_age=max_age)


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
        self._load_prev_day_closes_at_startup()
        # [260704 감사 P2] 선물-현물 베이시스 — KOSPI200 현물지수 폴링(60s) + 계산기
        self.basis_calc         = BasisCalculator()
        self._last_kospi200_spot: Optional[float] = None
        # [260704 감사 P2] VKOSPI 장중값 — 같은 60s 타이머에서 함께 폴링
        self._last_vkospi: Optional[float] = None
        # Phase 2: 1분봉 → N분봉 집계기 + 호라이즌별 피처 벡터 캐시
        self.bar_aggregator     = BarAggregator()
        self._hz_feat_cache     = {}   # {h_name: np.ndarray} — 마지막 완성봉 기반 피처 벡터
        self._hz_bar_age        = {}   # {h_name: int} — 마지막 완성봉 이후 경과 분 수
        self.model             = MultiHorizonModel()
        # [P2, 288차] SGD 전용 피처 인덱스 — GBM _hz_feat_indices와 별도 관리.
        # config.settings.SGD_FEATURE_NAMES_BY_HORIZON을 model.feature_names 안에서
        # 찾아 인덱스화. 모델 재학습으로 feature_names가 바뀔 때마다 재계산 필요(S0 참조).
        self._sgd_feat_indices: dict = {}
        self._rebuild_sgd_feat_indices()
        self.rf_model          = RFHorizonModel()
        self.rf_model.load_all()   # pkl 없으면 is_ready()=False로 graceful 유지
        self.ensemble          = EnsembleDecision()
        self._pt_value         = MINI_FUTURES_PT_VALUE  # [235차] 미니선물 전용 초기값 — connect_broker에서 get_contract_spec으로 재확정
        self.position          = PositionTracker(pt_value=self._pt_value)
        self.checklist         = EntryChecklist()
        self.sizer             = PositionSizer(account_balance=100_000_000)  # 기본 1억
        self.kelly             = AdaptiveKelly()
        self.time_exit         = TimeExitManager()
        self.online_learner    = OnlineLearner()
        self.horizon_calibrator = MultiHorizonCalibrator(list(HORIZONS.keys()))
        # [311차 후속 B안] GBM 꼬리과적합(극단 피처→과신) 느린-재적합 보정 레이어 —
        # horizon_calibrator(빠른 WINDOW=200)와 분리, fit_all()은 daily_close()에서만 호출.
        # [311차 후속 30m 전용 축소] Phase 3 워크포워드 종합검증(06-01~07-10 전기간)에서
        # 30m 외 호라이즌은 기존 빠른層이 이미 실제정확도에 근접해 있어(3m 오차 0.003 등)
        # 극단성 보정이 오히려 ECE를 악화시킴(6개 호라이즌 전부 ECE 상승, 30m만 일관 개선).
        # 검증된 30m만 적용 — 나머지 호라이즌 확대는 별도 재검증 후 결정.
        self.extremity_corrector = MultiHorizonExtremityCorrector(["30m"])
        self._preload_horizon_calibration()          # DB에서 사전 fit → 첫 tick부터 보정 효과
        self.ensemble.calibrator = self.horizon_calibrator   # 앙상블 2차 압축 연결
        self.pred_buffer       = PredictionBuffer()
        self.meta_gate         = MetaGate()
        # selection bias 해소: skip된 신호의 meta_features 임시 보관
        # key=ts_str, value=[(meta_features, confidence), ...]
        # STEP 2 에서 동일 ts 검증 결과가 도착할 때 record_outcome 처리
        self._meta_shadow      = {}
        self.toxicity_gate     = ToxicityGate(
            severe_spread_block_ticks=TOXICITY_SEVERE_SPREAD_BLOCK_TICKS,
            severe_spread_block_enabled=TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED,
        )
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
                self._session_open_price = _gap_open
                logger.info("[GapOffset] 재시작 복원: today_open=%.2f", _gap_open)
            except Exception as _ge:
                logger.warning("[GapOffset] 재시작 복원 실패: %s", _ge)
        self.threshold_recalibrator   = ThresholdRecalibrator()
        self.atr_ceiling_recalibrator = ATRCeilingRecalibrator()
        self.entry_horizon_recalibrator = EntryHorizonRecalibrator()
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
        # 273차: ATR_MAX_ENTRY 적응형 상한용 — 최근 N분 ATR 롤링 윈도우
        self._atr_recent_window: "_deque[float]" = _deque(maxlen=ATR_ADAPTIVE_MAX_WINDOW)

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
        self._ecb_observation_until: Optional[datetime.datetime] = None  # CB 해제 후 관망 기간
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
        # [234차] 종목변경 재시작 배지 시그널 연결
        self.dashboard.sig_code_change_restart_requested.connect(
            self._on_code_change_restart_requested
        )
        self.dashboard.set_ui_startup_mode()
        # 스레드-안전 종료 예약: DailyClose 스레드가 emit() → 메인 스레드에서 _schedule_shutdown 호출
        _shutdown_sig.request.connect(self._schedule_shutdown, Qt.QueuedConnection)
        # 스레드-안전 대시보드 갱신: DailyClose 스레드가 emit() → 메인 스레드에서 위젯 갱신 실행
        _daily_close_ui_sig.request.connect(self._apply_dashboard_call, Qt.QueuedConnection)
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
        # 차트 리로드 후 reset_session이 _active_trade를 초기화하므로
        # 훅을 통해 현재 포지션 상태를 재동기화한다 (장중 재시동 시 포지션 마커 복원)
        _system = self
        def _chart_reload_hook():
            if _system.position.status != "FLAT":
                _system.dashboard.minute_chart_sync_active_position(
                    _system.position.status,
                    _system.position.entry_price,
                    _system.position.entry_time,
                )
        self.dashboard.set_minute_chart_post_reload_hook(_chart_reload_hook)
        self._reverse_entry_enabled: bool = False
        # [339차] 1계약 TP1 보호모드 기본값 breakeven → atr_profit — 손절은 항상
        # 풀사이즈(ATR×1.5)로 나가는데 TP1은 본전(+0원)에서 캡되던 비대칭 완화.
        # atr_profit은 TP1 도달 시 ATR×0.25만큼 확정 이익을 잠근다(그대로 반전해도 소액 실현승).
        self._tp1_protect_mode: str = "atr_profit"
        # [339차] 신호소멸청산 섀도우 기록 — 같은 포지션(entry_time)당 1회만 기록해
        # 반대신호 조건이 여러 분봉에 걸쳐 지속돼도 signal_decay_exits에 중복 적재 방지.
        self._signal_decay_shadow_key = None
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
        # [225차 P1] 데몬 스레드 → 메인 스레드 콜백 큐
        # QTimer.singleShot(0, ...) 은 daemon thread에서 PyQt5 이벤트 루프 전달 보장이 없음.
        # worker 완료 시 (tag, *args) 를 put → 매분 S0 drain → 메인 스레드에서 안전 실행.
        self._deferred_callbacks: _queue.Queue = _queue.Queue()
        self._auto_entry_enabled: bool = True   # Auto On/Off 토글 상태
        self._auto_entry_disabled_until: object = None  # FATAL 정책이 끈 자동진입 자동복구 시각
        self._manual_entry_ctx: dict = {}        # 마지막 파이프라인 산출값 (수동 진입 버튼용)
        self._last_order_event_key = None
        self._broker_sync_verified: bool = False
        self._broker_sync_block_new_entries: bool = True
        self._broker_sync_last_error: str = "startup sync not attempted"
        self._warmup_retrain_pending: bool = False   # 세션 재시작 후 GBM 즉시 재학습 예약 플래그
        self._eod_retrain_ok: bool = False           # 전날 EOD 재학습 성공 여부 — 08:55 PreRetrain 스킵 판단용
        self._gbm_retrain_running: bool = False      # GBM 재학습 중복 실행 방지 플래그
        self._gbm_retrain_started_at: Optional[datetime.datetime] = None  # P1-B: 30분 타임아웃 감시용
        self._drift_retrain_last_attempt: Optional[datetime.datetime] = None  # DriftRetrain 시도 시각 (실패 포함)
        # [228차] 실제 분봉 완료 시각 — 복구 스킵 경로와 구별해 ExchangeCB 정확히 감지
        self._last_real_pipeline_dt: Optional[datetime.datetime] = datetime.datetime.now()
        # [230차] TickUI 차트 업데이트 쓰로틀 — 100ms 이내 중복 minute_chart_tick 스킵
        self._last_tick_chart_update: float = 0.0
        # [266차] tick-level 하드스톱 — COM 콜백에서 flag 세팅, S0-C에서 메인스레드 주문 전송
        self._tick_stop_triggered: bool  = False
        self._tick_stop_price:     float = 0.0
        # [363차] tick-level 손절1차(Loss Tier1) — 0721 딥다이브: 분당 STEP8 체크뿐이라
        # 급락이 한 틱/한 분 안에 tier1과 풀스톱을 동시에 뚫으면 tier1이 관측될 기회
        # 자체가 없었음(0721 트레이드③ 39초 내 직행). 풀스톱과 동일한 패턴으로 확장.
        self._tick_loss_tier1_triggered: bool  = False
        self._tick_loss_tier1_price:     float = 0.0
        # [320차] VPIN 배선 — bar 누적 buy_vol/sell_vol의 틱 델타로 개별 체결 복원용
        self._vpin_bar_ts: Optional[datetime.datetime] = None
        self._vpin_prev_buy_vol:  float = 0.0
        self._vpin_prev_sell_vol: float = 0.0
        self._chejan_exit_miss_count: int = 0   # [269차] EXIT Chejan 이벤트 유실 일별 카운터
        # [226차] 64비트 서브프로세스 재학습 추적 — Popen·결과 경로·warmup 플래그
        self._retrain_subproc = None                     # subprocess.Popen handle
        self._retrain_subproc_is_warmup: bool = False
        self._retrain_subproc_result_path: str = ""
        # [267차] 서브프로세스 stderr 파일 핸들 — py310 경고·오류 캡처 (DEVNULL 대체)
        self._retrain_subproc_stderr_fh = None           # open() handle, 완료 후 닫힘
        # [228차] 시작 시 이전 세션의 잔류 결과 JSON 정리 — 이중 인스턴스 경합 잔류 파일 방지
        try:
            import glob as _glob
            _stale = _glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "_gbm_result_*.json"))
            for _sf in _stale:
                try:
                    os.remove(_sf)
                except Exception:
                    pass
            if _stale:
                logger.info("[GBM-64] 시작 시 잔류 결과 JSON %d개 정리: %s", len(_stale), _stale)
        except Exception:
            pass
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
        # [225차 P0] sigma 전전봉 종가 — _on_tick_price_update가 같은 틱에서
        # _last_pipeline_price를 현재봉 종가로 덮어써 ret=0 고착 버그 수정.
        # 이전 파이프라인 완료 시점에만 갱신하여 tick 오염 차단.
        self._sigma_prev_price: float = 0.0
        # GBM 첫 재학습 완료 전 보수 진입 제어
        self._pre_retrain_done: bool = False         # True이면 방법3 레이블 GBM 사용 중
        self._last_balance_result: dict = {}
        self._last_sizer_balance: float = 100_000_000.0
        self._effect_report_tick: int = 0
        self._effect_report_running: bool = False
        self._canary_1m_last_run_date: object = None  # [331차 후속2] 1일 1회 실행 게이트
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

        # ── 15:18 FINAL_CLOSE 안전망 ───────────────────────────────────────────
        self._final_close_done: bool = False     # 1회만 실행 (중복 방지)

        # ── P3-a: OnlineLearner stuck 학습 오염 가드 ───────────────────────────
        self._stuck_this_minute: bool = False    # 이번 분봉에 stuck 해소 발생 여부

        # ── 호라이즌별 롤링 Bias 버퍼 ────────────────────────────────────────
        # [241차] 1m=45분: 단기 DN 편향이 하루 지속돼도 감지할 증거 기반 확보
        # 단기(1m) 편향은 SGD 누적이 빠르므로 더 넓은 윈도우 필요
        # 10m/15m/30m는 봉 수 자체가 적어 윈도우 줄임
        _BIAS_MAXLEN = {"1m": 45, "3m": 30, "5m": 30,
                        "10m": 20, "15m": 15, "30m": 10}
        self._bias_buf: dict = {
            h: deque(maxlen=_BIAS_MAXLEN.get(h, 30)) for h in HORIZONS
        }
        self._bias_log_tick: int = 0   # 10분마다 요약 로그 출력 카운터

        # ── [P2] FL 편향 고착 → uniform fallback 제어 ──────────────────────
        # FL 예측 비율 90%+ 가 20분 이상 지속되면 해당 호라이즌 예측을 (1/3,1/3,1/3)으로
        # 치환해 앙상블 오염을 차단한다. 2026-06-05 10m/15m FL 100% 고착 사례 대응.
        self._bias_fl_streak: dict = {h: 0 for h in HORIZONS}  # FL 편향 연속 분 카운터
        self._bias_override_horizons: set = set()               # uniform fallback 적용 호라이즌
        # 자동 해제 타이머: 발동 후 N분 경과 시 자동 해제 (buf 스킵으로 조기해제 불가 대비)
        self._bias_override_timer: dict = {h: 0 for h in HORIZONS}

        # ── [P2-진단] conf 고착 감지 ────────────────────────────────────────
        # conf가 N분 연속 동일값일 때 WARN 로그로 GBM/SGD 분해값을 기록
        self._conf_prev: dict = {}      # {h_name: float} 직전 틱 blended conf
        self._conf_stuck: dict = {h: 0 for h in HORIZONS}  # 연속 동일 카운터

        # ── [P1] SGD 학습 호라이즌별 봉단위 dedup ───────────────────────────
        # 검증은 매분 발생하지만 같은 N분봉에서 파생된 예측은 (N-1)/N이 동일 정보의
        # 재탕(30m: 봉당 29/30 겹침) — 매분 학습하면 같은 레이블을 반복 주입해
        # SGD가 한 방향으로 붕괴(콜드스타트 루프의 2번째 원인). 호라이즌별 최소 학습
        # 간격을 자기 봉 길이(N분)로 제한해 "완성봉당 최대 1회"만 학습에 반영한다.
        self._sgd_learn_last_ts: dict = {h: "" for h in HORIZONS}

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
        # [342차] 켈리가 "자본 대비 1계약도 부적절"이라 판단했는데 min_qty로
        # 강제 진입된 경우를 태깅 — 실거래 의사결정에는 미관여, 리포트 전용 계측
        # (VALIDATION_CAMPAIGN["kelly_skip"], eval_kelly_skip_grade_c() 참조).
        self._entry_kelly_advised_skip: int = 0
        # [311차 후속] 진입 출처 태그 — trades.entry_source에 그대로 기록되어
        # 유령/정상 레코드를 사후 구분한다(306차 pending_miss 유령 포지션 사후분석 대응).
        self._entry_source:       str  = "SYSTEM_AUTO"
        # [260704 감사 P1] 지정가 우선 집행 상태 (LIMIT_ENTRY_FIRST_ENABLED=False면 미사용)
        self._pending_limit_is_active: bool = False
        self._pending_limit_order_no: str = ""
        self._pending_limit_submitted_at: Optional[float] = None
        self._pending_limit_price: float = 0.0
        self._shadow_ev = None  # [Phase2] ShadowEvaluator — 신버전 가상 실행
        self._last_health_level: str = "INFO"
        self._fp_last_logged_level: Optional[int] = None
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
        # [311차 후속9] 라벨(검증완료 실제 방향) 있는 SHAP용 (X, y) 버퍼 —
        # permutation_importance 계산에 필요. 재시작 시 DB 복원 없이 이번 세션
        # 라이브 검증만으로 채워짐(SHAP_MIN_DATA_POINTS=100건 ≈ 100분 내 충족).
        self._shap_labeled_window: dict = {
            h: deque(maxlen=240) for h in ("1m", "3m", "5m")
        }
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
            "exception_exclude_tags": list(getattr(mod, "HEALTH_EXCEPTION_EXCLUDE_TAGS", HEALTH_EXCEPTION_EXCLUDE_TAGS)),
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
        all_feature_names = list(self.model.feature_names or [])
        if not all_feature_names:
            return
        self._sync_feature_registry_with_model()
        # [311차 후속9] ShapTracker는 실제 1m GBM 모델(호라이즌 슬라이싱된 12개
        # 피처)을 대상으로 계산하는데 예전엔 전체 97개 피처명으로 생성돼 있었음
        # (self._n_features=97 vs 실제 model.n_features_in_=12 불일치) — 1~3단계
        # 중요도 계산이 길이 체크(len(fi)==self._n_features)에서 전부 실패하는
        # 구조적 원인 중 하나. 1m 전용 피처 서브셋으로 생성해 정합성 확보.
        # [337차] get_available_feature_set()은 horizon_feature_sets.json의 "다음 재학습
        # 계획"(예: 331차 딥다이브 P0-1, 미탑재 상태)을 그대로 읽어온다 — 실제 배포된
        # gbm_1m.pkl이 아직 구 피처셋으로 학습된 채면 여기서 만든 X가 모델이 기대하는
        # 입력 shape와 어긋나 permutation_importance가 매분 예외로 조용히 실패한다
        # (동적피처 탭이 몇 시간째 갱신 안 되는 증상의 원인). 모델 로드 시 이미
        # n_features_in_로 검증된 self.model.horizon_feature_names(실제 배포 모델의
        # 피처셋)를 최우선으로 쓰고, 없을 때만 레지스트리 기반 선택으로 fallback.
        feature_names = (
            list(self.model.horizon_feature_names.get("1m") or [])
            or get_available_feature_set("1m", all_feature_names)
            or all_feature_names
        )
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
        """ConstOut 재적합·드리프트 트리거 시 호출 — 64비트 subprocess 경량 재학습."""
        return self._start_gbm_retrain_subprocess(
            force=force, reason=reason, is_warmup=False, intraday=True,
        )

    def _start_gbm_retrain_subprocess(
        self, force: bool, reason: str, is_warmup: bool, intraday: bool = True,
    ) -> bool:
        """[226차] GBM 재학습을 py310_64 서브프로세스로 실행 — 32비트 OOM 완전 차단.

        기존 데몬 스레드 방식(retrain_now() → 32비트 numpy 14.8 MiB 연속 블록 OOM)을
        64비트 독립 프로세스로 대체. retrain_intraday.py 스크립트가 결과 JSON을 기록하고,
        main.py S0 루프가 poll()로 완료를 감지 → _on_gbm_retrain_done() 정상 호출.
        """
        if getattr(self, "_gbm_retrain_running", False):
            log_manager.system(f"[GBM-64] 재학습 진행 중 — 스킵 ({reason})", "WARN")
            return False

        from config.settings import PYTHON_64_EXEC
        import uuid

        _script  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retrain_intraday.py")
        _rpath   = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data",
            f"_gbm_result_{uuid.uuid4().hex[:8]}.json",
        )
        _force_s   = "1" if force    else "0"
        _intraday_s = "1" if intraday else "0"

        # [267차] stderr → 타임스탬프 로그파일 캡처 (DEVNULL 대체)
        # py310_64 subprocess의 Python 경고·오류가 DEVNULL로 사라지는 문제 해소.
        # 동일 UUID 기반 경로로 결과 JSON과 쌍을 이뤄 추적 가능.
        _stderr_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "logs",
            f"retrain_stderr_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        )
        try:
            _stderr_fh = open(_stderr_path, "w", encoding="utf-8")
        except Exception:
            _stderr_fh = None  # 파일 오픈 실패 시 DEVNULL 폴백

        try:
            _proc = subprocess.Popen(
                [PYTHON_64_EXEC, _script, _rpath, _force_s, _intraday_s],
                stdout=subprocess.DEVNULL,
                stderr=_stderr_fh if _stderr_fh is not None else subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except FileNotFoundError:
            if _stderr_fh:
                _stderr_fh.close()
            log_manager.system(
                f"[GBM-64] py310_64 Python 없음 ({PYTHON_64_EXEC}) — 재학습 불가", "ERROR",
            )
            return False
        except Exception as _pe:
            if _stderr_fh:
                _stderr_fh.close()
            log_manager.system(f"[GBM-64] subprocess 시작 실패: {_pe}", "WARNING")
            return False

        self._gbm_retrain_running      = True
        self._gbm_retrain_started_at   = datetime.datetime.now()
        self._gbm_retrain_done_event.clear()
        self._retrain_subproc             = _proc
        self._retrain_subproc_is_warmup   = is_warmup
        self._retrain_subproc_result_path = _rpath
        self._retrain_subproc_stderr_fh   = _stderr_fh
        self.circuit_breaker.set_gbm_retrain_active(True)
        log_manager.learning(
            f"[GBM-64] 64비트 서브프로세스 재학습 시작 "
            f"| force={force} intraday={intraday} pid={_proc.pid} | {reason}"
        )
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
            # [312차] ShapTracker는 "1m" 호라이즌 피처 서브셋(h_names_1m, 예: 12개)으로
            # 생성되는데(_ensure_shap_tracker) 여기서 self.model.feature_names(전체
            # 피처, 예: 97개)로 X를 만들면 TreeExplainer가 컬럼수만큼(97) 중요도를
            # 반환해 tracker.feature_names(12개)와 길이가 안 맞아 get_current_ranking()
            # 에서 IndexError로 초기화 전체가 크래시함. 반드시 tracker 자신의
            # feature_names로 슬라이싱하고, "1m" 모델이 없으면 다른 호라이즌으로
            # fallback하지 않는다(다른 호라이즌 모델은 애초에 tracker 피처셋과 무관).
            h_names_1m = list(getattr(self._shap_tracker, "feature_names", []) or [])
            if horizon_model is not None and h_names_1m:
                restored_vectors = np.array(
                    [
                        [float(feat.get(name, 0.0) or 0.0) for name in h_names_1m]
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

        # VP 버퍼 복원: 재시작 후 poc_distance cold-start z폭발 방지
        # 재시작 전 60봉 OHLCV를 VP 계산기에 미리 투입 → 첫 분봉부터 성숙 윈도우 사용
        _vp_restored = 0
        try:
            _vp_bars = fetch_recent_raw_candles(limit=60)
            for _vrow in _vp_bars:
                self.feature_builder._vol_profile.update(
                    float(_vrow["high"]), float(_vrow["low"]),
                    float(_vrow["close"]), float(_vrow["volume"]),
                )
            _vp_restored = len(_vp_bars)
        except Exception as _vpe:
            logger.warning("[VPRestore] VP 버퍼 복원 실패 — cold start 유지: %s", _vpe)

        # [371차] RegimeFingerprint 라이브 버퍼 워밍업 — _live_buf는 디스크에
        # 영속화된 적이 없어 매 거래일 재기동마다 비어서 시작했고, 그 결과
        # PSI가 min_live(50분) 문턱을 막 넘긴 장 시작 직후 소표본 노이즈로
        # 크게 튀는 문제(0723 PSI=18 관측)가 있었다. raw_features(수개월치
        # 보관)에서 최근 값을 읽어와 재시작 직후에도 다표본으로 시작시킨다.
        _fp_warmed = 0
        try:
            from strategy.regime_fingerprint import get_fingerprint as _get_fp_restore
            from strategy.regime_fingerprint import _LIVE_WIN_MINS as _FP_WIN
            _fp_rows = fetch_recent_raw_features(limit=_FP_WIN)
            _fp_feat_rows = []
            for _frow in _fp_rows:
                try:
                    _fd = json.loads(_frow["features"])
                except Exception:
                    continue
                if isinstance(_fd, dict):
                    _fp_feat_rows.append(_fd)
            _fp_warmed = _get_fp_restore().warm_live_buffer(_fp_feat_rows)
        except Exception as _fpe:
            logger.warning("[AnalysisRestore] RegimeFingerprint 라이브버퍼 복원 실패 — cold start 유지: %s", _fpe)

        logger.info(
            "[AnalysisRestore] live_corr=%d restored_corr=%s live_shap=%d live_ready=%s shap_features=%d vp_bars=%d fp_live=%d",
            len(self._param_corr_history),
            "yes" if self._restored_corr_str else "no",
            len(self._shap_feature_window),
            "yes" if self._live_shap_ready else "no",
            len(self._cached_shap_importance),
            _vp_restored,
            _fp_warmed,
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

    def _prep_shap_xy(self, horizon: str, h_names: list):
        """[311차 후속9] _shap_labeled_window[horizon]을 프로덕션 학습과 동일한
        전처리(robust_preprocess → 호라이즌 스케일러 → 컬럼 슬라이싱)로 변환.

        `learning/batch_retrainer.py:_train_horizon()`의 전처리 순서와 반드시
        일치해야 함 — 순서가 틀리면 permutation_importance가 모델이 실제 학습한
        피처공간과 다른 입력을 채점하게 되어 결과가 무의미해짐.
        """
        window = self._shap_labeled_window.get(horizon)
        if not window or len(window) < SHAP_MIN_DATA_POINTS:
            return None, None
        vecs, labels = zip(*window)
        X_raw = np.array(vecs, dtype=np.float64)
        y = np.array(labels, dtype=np.int64)
        try:
            X_proc = apply_robust_preprocess(X_raw, self.model.feature_names)
        except Exception as e:
            logger.debug("[ShapRefresh] %s robust_preprocess 실패: %s", horizon, e)
            return None, None
        scaler = self.model.scalers.get(horizon)
        X_scaled = scaler.transform(X_proc) if scaler is not None else X_proc
        try:
            h_idx = [self.model.feature_names.index(n) for n in h_names]
        except ValueError:
            return None, None
        return X_scaled[:, h_idx], y

    def _refresh_shap_state(self, ts: str) -> None:
        self._ensure_shap_tracker()
        if not self.model.is_ready() or self._shap_tracker is None:
            return

        minute_key = str(ts or "")[:16]
        if minute_key and self._shap_last_update_minute == minute_key:
            return
        self._shap_last_update_minute = minute_key

        # ── 1m: 기존 ShapTracker(주간 심사·후보교체 상태 유지) ──────
        horizon_model = self.model.models.get("1m")
        h_names_1m = list(getattr(self._shap_tracker, "feature_names", []) or [])
        if horizon_model is not None and h_names_1m:
            X_1m, y_1m = self._prep_shap_xy("1m", h_names_1m)
            if X_1m is not None:
                sample_n = min(120, len(X_1m))
                updated = self._shap_tracker.update(
                    horizon_model, X_1m, y_1m, sample_size=sample_n,
                )
                if updated:
                    ranking = self._shap_tracker.get_current_ranking()
                    if ranking:
                        score_map = {row["feature"]: float(row["importance"]) for row in ranking}
                        self._cached_shap_importance = score_map
                        self._live_shap_ready = True
                        save_shap_scores(ts, "1m", score_map)
                        self._update_shap_dashboard()
                else:
                    logger.debug(
                        "[ShapRefresh] 1m update() False — n=%d, tracker_feat=%d",
                        len(X_1m), len(h_names_1m),
                    )

        # ── 3m/5m: [311차 후속9 신규] ShapTracker 상태와 분리된 단발 계산 ──
        # 1m 전용 ShapTracker 인스턴스(_history/_current_importance/주간심사)를
        # 공유하면 서로 다른 호라이즌 데이터로 매분 덮어써 오염되므로
        # compute_horizon_importance()로 상태 없이 계산 후 DB만 직접 저장.
        for _h in ("3m", "5m"):
            _model_h = self.model.models.get(_h)
            if _model_h is None:
                continue
            _h_names = get_available_feature_set(_h, self.model.feature_names) or []
            if not _h_names:
                continue
            X_h, y_h = self._prep_shap_xy(_h, _h_names)
            if X_h is None:
                continue
            _idx = np.random.choice(len(X_h), min(120, len(X_h)), replace=False)
            _score_map = compute_horizon_importance(_model_h, X_h[_idx], y_h[_idx], _h_names)
            if _score_map:
                save_shap_scores(ts, _h, _score_map)

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

    def _canary_load_z_warn_features(self, n_rows: int = 60) -> list:
        """raw_data.db 최근 n_rows 피처로 현재 scaler z-score 극단 피처명 목록 반환.

        Phase refit 진단 전용(호출 빈도 낮음) — _canary_load_z_warn과 별도 쿼리.
        """
        import sqlite3 as _sq3
        import json as _json
        from config.settings import RAW_DATA_DB as _RAW_DB
        if not os.path.exists(_RAW_DB):
            return []
        try:
            with _sq3.connect(_RAW_DB, timeout=5) as _conn:
                _rows = _conn.execute(
                    "SELECT features FROM raw_features ORDER BY ts DESC LIMIT ?",
                    (n_rows,),
                ).fetchall()
            if not _rows:
                return []
            _fn = self.model.feature_names
            if not _fn:
                return []
            _X = np.array(
                [[_json.loads(r[0]).get(k, 0.0) for k in _fn] for r in _rows],
                dtype=float,
            )
            return self.model.canary_z_warn_features(_X)
        except Exception as _e:
            logger.debug("[Canary] z_warn 피처 로드 실패: %s", _e)
            return []

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

            level_counts = log_manager.get_level_counts(
                since_sec=600,
                layer="SYSTEM",
                exclude_prefixes=p.get("exception_exclude_tags", HEALTH_EXCEPTION_EXCLUDE_TAGS),
            )
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
                    _, _ts, _h_name, _h_feats, _regime = item
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
        # (1) acc30m 버퍼 리셋 (표본 부족 시 [277차] 기아 방지로 내부에서 스킵될 수 있음)
        _acc30m_did_reset = self.circuit_breaker.reset_acc30m_buffer()
        log_manager.system(
            f"[ConstOut] {hz} 재적합 완료 → "
            + ("acc30m 버퍼 리셋" if _acc30m_did_reset else "acc30m 버퍼 리셋 스킵(표본 누적 중)"),
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

    def _is_degraded_entry_blocked(
        self,
        confidence: float,
        is_manual: bool,
        latency_ms: float = 0.0,
        quality_score: float = 1.0,
        cache_age_sec: float = 0.0,
        exception_density_10m: float = 0.0,
    ) -> tuple:
        """현재 Degraded 정책 기준으로 진입 차단 여부를 반환한다.

        _emit_runtime_health 가 파이프라인 끝(STEP 9 이후)에 호출되므로
        _health_degraded_mode 플래그는 항상 1사이클 늦다.
        latency_ms 등 현재 사이클 지표가 전달되면 '이번 사이클에 Degraded 진입 예정'
        여부를 미리 계산해 진입을 차단한다.
        """
        p = self._health_policy
        is_degraded = self._health_degraded_mode

        # Lookahead: 현재 사이클 지표로 Degraded 진입 여부를 선제 판단
        if not is_degraded and latency_ms > 0:
            _cur_level = self._classify_health_level(
                latency_ms=latency_ms,
                quality_score=quality_score,
                cache_age_sec=cache_age_sec,
                exception_density_10m=exception_density_10m,
            )
            if _cur_level in ("WARNING", "CRITICAL"):
                _soft_ms = float(p.get("degraded_soft_latency_ms", 1300.0))
                _soft_w  = float(p.get("degraded_soft_warn_weight", 0.35))
                _w = _soft_w if _cur_level == "WARNING" and latency_ms < _soft_ms else 1.0
                _enter_thresh = float(p.get("degraded_enter_streak", HEALTH_DEGRADED_ENTER_STREAK))
                if self._health_warn_streak + _w >= _enter_thresh:
                    is_degraded = True
                    logger.warning(
                        "[HealthPolicy] Degraded 선제차단: streak=%.2f+%.2f ≥ %.0f "
                        "(latency=%.0fms quality=%.2f cache=%.0fs exc10m=%.0f)",
                        self._health_warn_streak, _w, _enter_thresh,
                        latency_ms, quality_score, cache_age_sec, exception_density_10m,
                    )

        if not is_degraded:
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
        mode = str(state.get("tp1_single_contract_mode", "atr_profit") or "atr_profit").strip().lower()
        if mode not in {"breakeven", "breakeven_plus", "atr_profit"}:
            mode = "atr_profit"
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
        # _execute_entry() 내부에서 기본값(SYSTEM_AUTO)으로 설정되므로 호출 후 덮어씀
        self._entry_source = "OPERATOR_MANUAL"

    def _on_instant_exit_requested(self) -> None:
        """즉시청산 버튼 클릭 — 보유 포지션 전량 즉시 청산."""
        self._on_manual_exit_requested(100)

    def _on_auto_mode_changed(self, enabled: bool) -> None:
        """Auto On/Off 토글 — 자동 진입 활성화 여부 전환."""
        self._auto_entry_enabled = bool(enabled)
        # 사용자가 직접 토글을 조작하면 FATAL 정책의 15분 자동복구 타이머는 무의미
        # (수동 결정이 우선) — 남겨두면 사용자가 의도적으로 끈 OFF를 나중에 타이머가
        # 되돌리거나, 반대로 이미 ON인데 불필요한 복구 로그가 남을 수 있음.
        self._auto_entry_disabled_until = None
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
        mode = str(mode or "atr_profit").strip().lower()
        if mode not in {"breakeven", "breakeven_plus", "atr_profit"}:
            mode = "atr_profit"
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
            # CB HALT 또는 브로커 확인된 stuck EXIT pending 시 강제 소멸 후 청산 진행
            # — stuck pending 때문에 운영자가 수동 청산조차 불가능한 상태 방지
            _po_kind = self._pending_order.get("kind", "")
            _stuck_exit = (
                _po_kind.startswith("EXIT")
                and self._pending_order.get("_broker_confirm_count", 0) >= 1
            )
            if self.circuit_breaker.state == CB_STATE_HALTED:
                log_manager.system(
                    "[ManualExit] CB HALT 상태 — stuck pending 강제 소멸 후 수동 청산 진행",
                    "WARNING",
                )
                self._clear_pending_order()
            elif _stuck_exit:
                log_manager.system(
                    f"[ManualExit] stuck EXIT pending({_po_kind}) 브로커 확인 완료 → 강제 소멸 후 수동 청산 진행",
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
                was_restart_after, had_partial_fill, entry_horizon, entry_source,
                kelly_advised_skip)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                       ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                result.get("entry_horizon") or "",
                getattr(self, "_entry_source", "SYSTEM_AUTO"),
                getattr(self, "_entry_kelly_advised_skip", 0),
            ),
        )
        try:
            from utils.db_utils import fetch_recent_ev
            _ev = fetch_recent_ev(20)
            self.dashboard.update_recent_ev(_ev["cnt"], _ev["avg_net_pnl_krw"], _ev["win_rate"])
        except Exception as _ev_e:
            logger.warning("[EV20] 대시보드 갱신 실패 (무해): %s", _ev_e)

        # [308차] EXIT pending의 부분체결 합계가 이 결과로 DB에 반영됐음을 표시.
        # _clear_pending_order()의 안전망 flush가 여기서 이미 기록된 합계를
        # 중복으로 다시 기록하지 않도록 한다.
        if self._pending_order is not None:
            self._pending_order["agg_flushed"] = True

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
            # [308차] EXIT pending이 부분체결 합계를 DB에 flush하지 못한 채 소멸하는
            # 경우의 안전망. Chejan 이벤트 유실로 마지막 체결이 끝내 도착하지 않으면
            # 정상 완결 경로(_post_exit 등)가 한 번도 안 불려 이미 확정된 부분체결
            # 이익/손실이 그대로 증발한다(2026-07-09 실사고, +2,206,345원 유실).
            if (
                _cleared_kind.startswith("EXIT")
                and not self._pending_order.get("agg_flushed")
                and int(self._pending_order.get("agg_exit_qty") or 0) > 0
            ):
                self._flush_unrecorded_exit_agg(self._pending_order)
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

    def _flush_unrecorded_exit_agg(self, pending: dict) -> None:
        """[308차] EXIT pending 소멸 시 미기록 부분체결 합계를 trades.db에 안전망 기록.

        _ts_agg_exit_fill()이 누적한 agg_exit_*는 정상적으로는 마지막 체결에서
        _post_exit()/_post_partial_exit()/_ts_record_nonfinal_exit()를 통해 DB에
        반영된다. 하지만 마지막 체결의 Chejan 콜백이 유실되면 그 경로가 한 번도
        불리지 않아 이미 확정된 앞선 부분체결 전부가 조용히 사라진다. 여기서는
        pending이 어떤 사유로든 소멸하는 순간 그 시점까지의 합계를 최선껏 기록해
        "0건 기록"보다 "이미 아는 부분만이라도 기록"을 보장한다.
        entry_price/grade 등은 self.position이 이미 sync_from_broker() 등으로
        갱신됐을 수 있어 100% 정확하지 않을 수 있으므로 exit_reason에 표식을 남긴다.
        """
        agg_qty = int(pending.get("agg_exit_qty") or 0)
        if agg_qty <= 0:
            return
        price_x_qty = float(pending.get("agg_exit_price_x_qty") or 0.0)
        avg_price = (
            price_x_qty / agg_qty if agg_qty > 0 and price_x_qty > 0
            else float(pending.get("price_hint") or 0.0)
        )
        if avg_price <= 0:
            logger.error(
                "[PendingOrder] EXIT agg flush 실패 — 평균가 계산 불가 pending=%s", pending
            )
            return
        raw_pts = float(pending.get("agg_exit_pnl_pts") or 0.0)
        raw_fwd = float(pending.get("agg_exit_fwd_pts") or 0.0)
        entry_price = float(getattr(self.position, "entry_price", 0.0) or 0.0)
        entry_time = (
            getattr(self.position, "entry_time", None)
            or pending.get("last_fill_at") or datetime.datetime.now()
        )
        last_fill_at = pending.get("last_fill_at") or datetime.datetime.now()
        result = {
            "direction": pending.get("direction", ""),
            "raw_direction": pending.get("raw_direction", pending.get("direction", "")),
            "executed_direction": pending.get("direction", ""),
            "reverse_entry_enabled": pending.get("reverse_entry_enabled", False),
            "entry_price": entry_price,
            "exit_price": round(avg_price, 4),
            "quantity": agg_qty,
            "pnl_pts": round(raw_pts / agg_qty, 4) if agg_qty > 0 else 0.0,
            "pnl_krw": round(float(pending.get("agg_exit_pnl_krw") or 0.0), 0),
            "forward_pnl_pts": round(raw_fwd / agg_qty, 4) if agg_qty > 0 else 0.0,
            "forward_pnl_krw": round(
                float(pending.get("agg_exit_fwd_krw") or pending.get("agg_exit_pnl_krw") or 0.0), 0
            ),
            "exit_reason": f"{pending.get('reason','')}_유실복구",
            "grade": str(getattr(self.position, "grade", "") or ""),
            "entry_horizon": getattr(self.position, "entry_horizon", None),
            "entry_ts": (
                entry_time.strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(entry_time, "strftime") else str(entry_time)
            ),
            "exit_ts": (
                last_fill_at.strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(last_fill_at, "strftime") else str(last_fill_at)
            ),
        }
        try:
            self._record_trade_result(result)
            self._refresh_pnl_history()
            log_manager.system(
                f"[PendingOrder] EXIT agg flush 안전망 기록: {result['direction']} {agg_qty}계약 "
                f"@ {avg_price:.2f} pnl={result['pnl_pts']:+.2f}pt ({result['pnl_krw']:+,.0f}원) "
                f"order_no={pending.get('order_no','?')} filled={pending.get('filled_qty')}/{pending.get('qty')}",
                "CRITICAL",
            )
        except Exception as _flush_e:
            logger.error(
                "[PendingOrder] EXIT agg flush 실패 pending=%s err=%s", pending, _flush_e
            )

    def _has_pending_order(self) -> bool:
        return self._pending_order is not None

    def _normalize_broker_code(self, code: str) -> str:
        code = str(code or "").strip()
        if code.startswith(("A", "J")) and len(code) > 1:
            code = code[1:]
        return code

    def _rebuild_sgd_feat_indices(self) -> None:
        """[P2] SGD_FEATURE_NAMES_BY_HORIZON → self.model.feature_names 인덱스 재계산.

        model.feature_names는 GBM 재학습으로 바뀔 수 있으므로 __init__ 최초 1회+
        모델 리로드(S0) 시점마다 다시 호출한다. 마스터 리스트에 없는 피처명은 경고
        후 건너뛴다(안전 방어 — 정상 운영 중이면 발생하지 않아야 함).
        """
        from config.settings import SGD_FEATURE_NAMES_BY_HORIZON
        fn_list = self.model.feature_names or []
        new_indices = {}
        for h, names in SGD_FEATURE_NAMES_BY_HORIZON.items():
            idx = []
            for name in names:
                try:
                    idx.append(fn_list.index(name))
                except ValueError:
                    logger.warning(
                        "[SGD-Feat] %s: '%s' 피처가 model.feature_names에 없음 — 제외",
                        h, name,
                    )
            if idx:
                new_indices[h] = np.array(idx, dtype=np.int64)
        self._sgd_feat_indices = new_indices

    def _preload_horizon_calibration(self) -> None:
        """기동 시 DB 검증 예측(최근 3000건/호라이즌)으로 calibrator를 사전 fit.

        이 호출 없이는 calibrator가 fit=False 상태로 시작하여
        첫 ~100건은 raw prob이 그대로 통과(과신 억제 효과 없음).
        """
        from utils.db_utils import fetchall
        from config.settings import PREDICTIONS_DB as _PRED_DB
        import json as _json_cal
        try:
            rows = fetchall(
                _PRED_DB,
                """SELECT horizon, direction, confidence, correct, features
                   FROM predictions
                   WHERE actual IS NOT NULL
                   ORDER BY ts DESC
                   LIMIT 18000""",   # 호라이즌 6개 × 최대 3000건
            )
            for row in rows:
                _h = str(row["horizon"])
                _conf = float(row["confidence"] or 0.0)
                _correct = bool(int(row["correct"] or 0))
                self.horizon_calibrator.record(_h, _conf, _correct)
                try:
                    _feat = _json_cal.loads(row["features"]) if row["features"] else {}
                except (ValueError, TypeError):
                    _feat = {}
                _extra = compute_extremity_hinge(_feat, int(row["direction"] or 0))
                self.extremity_corrector.record(_h, _conf, _extra, _correct)
            self.horizon_calibrator.fit_all()
            _ext_fit = self.extremity_corrector.fit_all()
            logger.info(
                "[Calib] 기동 사전 학습 완료: %d건 (극단성보정 live=%s)",
                len(rows), _ext_fit.get("live", {}),
            )
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
            # ConstOut 구간 conf 제외: 동일 값(±0.01 반올림)이 전체의 15% 이상 점유 시
            # GBM 상수 출력 고착 구간 데이터가 p65를 왜곡하는 것을 방지.
            if len(confs) >= 50:
                _cr = [round(c, 2) for c in confs]
                _freq: dict = {}
                for _v in _cr:
                    _freq[_v] = _freq.get(_v, 0) + 1
                _stuck = {_v for _v, _cnt in _freq.items() if _cnt > len(confs) * 0.15}
                if _stuck:
                    _filtered = [c for c, r in zip(confs, _cr) if r not in _stuck]
                    if len(_filtered) >= 30:
                        logger.info(
                            "[DynMC] ConstOut 고착 conf 제외: %s → %d건 제거 (잔여 %d건)",
                            sorted(_stuck), len(confs) - len(_filtered), len(_filtered),
                        )
                        confs = _filtered
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

    def _apply_horizon_calibration(self, horizon_proba: dict, features: dict = None) -> dict:
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
            # [311차 후속 B안] 극단성 보정(②규칙 안전망 + ①섀도우 학습모델) — 10m/15m
            # 하한 보정 *뒤에* 적용해야 함(먼저 적용하면 위 하한 로직이 되돌려버림).
            # bb_position/vwap_position이 예측방향 반대편 극단일 때 과신을 추가로 깎는다.
            # correct_with_floor()는 max(floor, live)만 실제 반영, shadow는 로그 전용.
            _ext_extra = compute_extremity_hinge(features or {}, direction)
            if np.any(_ext_extra > 0):
                _ext_result = self.extremity_corrector.correct_with_floor(
                    horizon, raw_conf, _calibrated_raw, _ext_extra
                )
                if _ext_result["applied_penalty"] > 0:
                    logger.debug(
                        "[ExtremityCorrector] %s conf=%.3f→%.3f "
                        "(floor=%.3f live=%.3f shadow참고=%.3f)",
                        horizon, _calibrated_raw, _ext_result["calibrated_prob"],
                        _ext_result["floor_penalty"], _ext_result["live_penalty"],
                        _ext_result["shadow_penalty"],
                    )
                _calibrated_raw = _ext_result["calibrated_prob"]
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
        # [234차] 기동 시 확정 코드 → 대시보드에 등록 (UI 변경 시 재시작 배지 기준)
        try:
            self.dashboard.set_active_futures_code(code)
        except Exception as _ace:
            logger.debug("[SymbolChange] set_active_futures_code 실패 (무해): %s", _ace)
        # [235차] 종목코드 기반 계약 스펙 주입 — tick_size·pt_value 동적 확정
        # 미니선물 0.02pt/50,000원 vs 일반선물 0.05pt/250,000원 미구분으로
        # spread_ticks 2.5배 왜곡 + PnL 5배 오류 유발하던 버그 수정
        try:
            from config.constants import get_contract_spec as _gcs
            _spec = _gcs(code)
            self.feature_builder.set_tick_size(_spec["tick_size"])
            self._pt_value = _spec["pt_value"]
            self.position.set_pt_value(self._pt_value)
            log_manager.system(
                f"[ContractSpec] 계약스펙 확정: {_spec['label']} "
                f"tick_size={_spec['tick_size']} pt_value={_spec['pt_value']:,}",
                "INFO",
            )
        except Exception as _tse:
            logger.warning("[ContractSpec] 계약스펙 주입 실패 (기본값 유지): %s", _tse)
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
            is_trading_day(_rst_now)
            and datetime.time(9, 0) <= _rst_now.time() < datetime.time(15, 10)
            and not self._gbm_retrain_running
            and not _already_retrained_today
            and not _late_restart
        ):
            self._warmup_retrain_pending = False
            # [P0 260719] 여기서 _gbm_retrain_running=True 등을 미리 세팅하면 바로 아래
            # _start_gbm_retrain_subprocess()의 최초 가드(이미 실행 중이면 스킵)가 이
            # 자기 자신의 사전 세팅을 "이미 실행 중"으로 오인해 subprocess를 한 번도
            # 실제로 띄우지 못하고 매번 자기 발목을 잡던 버그(0719 정기점검 발견) —
            # 상태 세팅은 _start_gbm_retrain_subprocess() 내부(성공적으로 Popen한 뒤)에서만
            # 하도록 위임한다. 실패 시(py310_64 미탐지 등)에도 플래그가 고착되지 않는 부수 이득.
            self.dashboard.set_model_status("GBM 장중 재학습중...")
            _rt_gap_tag = (
                f" ({_mins_since_last_rt:.0f}분 경과, {_last_rt.strftime('%H:%M')} 이후)"
                if _last_rt else ""
            )
            log_manager.system(
                f"[WarmupRetrain] 장중 재시작 — GBM 경량 재학습 시작{_rt_gap_tag} (intraday)", "INFO"
            )

            # [226차] 64비트 subprocess 경량 재학습 — 32비트 OOM 없이 실행
            self._start_gbm_retrain_subprocess(
                force=False, reason="장중 재시작 WarmupRetrain", is_warmup=True, intraday=True,
            )
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
        now = datetime.datetime.now()
        if not is_market_open(now):
            return
        # [CB⑤ 방어] 09:00~09:02: 장 개시 직후 CpSysDib.CpSvrNew7221 서버 피크 부하
        # → BlockRequest 응답 7초+ 소요 → 메인 스레드 7,187ms 블로킹 실증(6/26 09:01)
        # 이 구간은 investor_data가 stale(age≥300s)이므로 스킵해도 정보 손실 없음.
        # quality_investor_stale=1.0 플래그가 이미 파이프라인에 전달됨.
        if datetime.time(9, 0) <= now.time() < datetime.time(9, 2):
            logger.debug("[LiveDBG] _fetch_investor_data 09:00~09:02 서버피크 스킵")
            return
        _t0 = time.perf_counter()
        logger.debug("[LiveDBG] _fetch_investor_data 시작 (메인 스레드 점유 시작)")
        try:
            # [2026-07-14 딥다이브 P2-2] include_program=False(108차, 2026-06-04)는 당시
            # CpSysDib.ProgramTrade/8119 계열의 반복 실패 로그 비용 때문이었음 — 그 이후
            # 260704 감사 P2(2026-07-05, 실제 Creon 연결로 검증)가 request_program_investor()를
            # 완전히 재작성해 검증된 필드 매핑(Dscbo1.CpSvr8111 idx19/37)만 단발 조회하도록
            # 바꿨는데, 이 런타임 플래그는 그 이후로도 갱신되지 않아 program_arb_net/
            # program_non_arb_net이 raw_features에 07-05 이후로도 계속 상수 0으로 남아있었음
            # (무스킬_피처셋_딥다이브_보고서_2026-07-13.md F5). 실패 시에도 api_connector.py의
            # _system_info_throttled(600s)가 로그 폭주를 막으므로 108차 우려는 이미 해소됨.
            self.investor_data.fetch_all(include_program=True)
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
        finally:
            _elapsed_ms = (time.perf_counter() - _t0) * 1000
            if _elapsed_ms > 500:
                logger.warning(
                    "[LiveDBG] _fetch_investor_data 지연 %.0fms — "
                    "메인 스레드 %.0fms 점유 (live 중단 원인 후보)",
                    _elapsed_ms, _elapsed_ms,
                )
            else:
                logger.debug("[LiveDBG] _fetch_investor_data 완료 %.0fms", _elapsed_ms)

    def _poll_kospi200_index(self) -> None:
        """[260704 감사 P2] KOSPI200 현물지수 + VKOSPI 1분 폴링 — QTimer 콜백.

        get_index_price()는 내부적으로 BlockRequest를 백그라운드 스레드에서 실행하고
        메인 스레드는 메시지 펌프만 하므로(_run_block_request) 여기서 직접 호출해도
        파이프라인을 블로킹하지 않는다. 실패해도 캐시된 이전 값을 유지(None으로
        리셋하지 않음) — BasisCalculator/feature 병합부가 결측을 ready=False로 처리.
        """
        if not is_market_open(datetime.datetime.now()):
            return
        try:
            price = self.broker.get_index_price()
        except Exception as e:
            logger.debug("[KOSPI200Index] 폴링 예외 (무해, 이전값 유지): %s", e)
            price = None
        if price:
            self._last_kospi200_spot = price

        try:
            vkospi = self.broker.get_index_price(VKOSPI_INDEX_CODE, name_contains="변동성")
        except Exception as e:
            logger.debug("[VKOSPI] 폴링 예외 (무해, 이전값 유지): %s", e)
            vkospi = None
        if vkospi:
            self._last_vkospi = vkospi

    def _poll_option_chain(self) -> None:
        """옵션 체인 5분 폴링 — QTimer 콜백.

        OptionChainWorker(QThread)를 기동하여 BlockRequest 루프를 메인 스레드에서 분리.
        Qt 이벤트 루프가 정상 동작하므로 Cybos 응답 수신 보장.
        """
        if not is_market_open(datetime.datetime.now()):
            return
        spot = self._last_close
        if not self.option_chain_snap.is_due(spot):
            return

        _prev = getattr(self, "_option_chain_worker", None)
        if _prev is not None:
            try:
                if _prev.isRunning():
                    logger.debug("[OptionChain] 이전 워커 실행 중 — 스킵 spot=%.1f", spot)
                    return
            except RuntimeError:
                # deleteLater()로 C++ 객체가 이미 소멸됐지만 Python wrapper는 살아있는 경우
                self._option_chain_worker = None

        self.option_chain_snap.mark_refresh_started()
        logger.debug("[LiveDBG] OptionChainWorker 기동 spot=%.1f", spot)

        _worker = OptionChainWorker(
            chain_raw     = self.option_chain_snap.get_chain_raw(),
            spot          = spot,
            cache_path    = self.option_chain_snap.cache_path,
            atm_window_pt = self.option_chain_snap.atm_window,
            pause_ms      = self.option_chain_snap.pause_ms,
        )
        _worker.result_ready.connect(self._on_option_chain_done)
        _worker.finished.connect(_worker.deleteLater)   # Qt C++ 객체 정리
        self._option_chain_worker = _worker             # GC 방지용 참조 보관
        _worker.start()

    def _on_option_chain_done(self, feats: dict, chain_raw: list) -> None:
        """OptionChainWorker.result_ready 수신 — 메인 스레드."""
        self.option_chain_snap.on_worker_done(feats, chain_raw)
        if self.dashboard and feats:
            self.dashboard.update_option_chain(self.option_chain_snap.get_features())

    def _on_tick_price_update(self, bar: dict) -> None:
        """틱 수신마다 대시보드 헤더 현재가 갱신.

        [230차] 쓰로틀링: 초당 최대 10회만 chart.update() 호출.
        CB 후·단일가 구간에서 sub-second 틱 폭증 시 348 candles paintEvent 연쇄 재진입으로
        32비트 스택 소진 → 0xC0000409 크래시. 100ms 이내 중복 호출 스킵으로 방지.
        """
        if self.realtime_data is None:
            return
        close = float(bar.get("close", 0) or 0.0)
        # [320차] VPIN 배선 — bar는 분봉 누적치라 buy_vol/sell_vol의 틱간 델타로
        # 이번 틱 단독 체결량·매수/매도 방향을 복원해 VPINCalculator에 전달.
        _vpin_bar_ts = bar.get("ts")
        if _vpin_bar_ts != self._vpin_bar_ts:
            self._vpin_bar_ts = _vpin_bar_ts
            self._vpin_prev_buy_vol = 0.0
            self._vpin_prev_sell_vol = 0.0
        _vpin_cur_buy = float(bar.get("buy_vol", 0.0) or 0.0)
        _vpin_cur_sell = float(bar.get("sell_vol", 0.0) or 0.0)
        _vpin_d_buy = max(0.0, _vpin_cur_buy - self._vpin_prev_buy_vol)
        _vpin_d_sell = max(0.0, _vpin_cur_sell - self._vpin_prev_sell_vol)
        self._vpin_prev_buy_vol = _vpin_cur_buy
        self._vpin_prev_sell_vol = _vpin_cur_sell
        if close > 0 and (_vpin_d_buy + _vpin_d_sell) > 0:
            self.feature_builder.update_tick(
                price=close, volume=_vpin_d_buy + _vpin_d_sell,
                is_buy=(_vpin_d_buy >= _vpin_d_sell),
            )
        logger.info(
            "[TickUI] begin code=%s close=%.2f ts=%s",
            self.realtime_data.code,
            close,
            bar.get("ts"),
        )
        if close > 0:
            self._last_pipeline_price = close
            # [266차] tick-level 하드스톱 감지 — COM 콜백 내 dynamicCall 금지로 flag만 세팅.
            # [348차] 과거엔 실제 주문 전송을 run_minute_pipeline S0-C(다음 분봉
            # 롤오버 시점)까지 미뤄 최악 60초 지연 → 그 사이 급변장에서 슬리피지
            # 누적(2026-07-16 14:12 사고 실측 -6.37pt). QTimer.singleShot(0, ...)은
            # dynamicCall/emit이 아니라 "다음 이벤트루프 패스에서 실행 예약"일 뿐이라
            # §4 위반이 아니며, 이 콜백 자체가 이미 메인 스레드(50ms 간격
            # _pump_messages 타이머가 PumpWaitingMessages를 호출하는 구조 —
            # api_connector.py:_ensure_message_pump)에서 실행 중이므로 daemon
            # thread 전달 미보장 문제(225차, L519 주석)도 해당 없음. singleShot
            # 콜백은 현재 콜 스택(OnReceived→...→_on_tick_price_update)이 완전히
            # 풀린 뒤 실행되므로 COM 콜백 내부 직접 호출과 다르다.
            # 조건: 포지션 보유 + pending 주문 없음 + 미감지 상태 + CB HALT 아님
            if (not self._tick_stop_triggered
                    and self._pending_order is None
                    and self.position.status != "FLAT"
                    and self.circuit_breaker.state != CB_STATE_HALTED
                    and self.position.is_stop_hit(close)):
                self._tick_stop_triggered = True
                self._tick_stop_price     = close
                logger.warning(
                    "[TickStop] 스톱 히트 감지 (틱) %s tick=%.2f stop=%.2f → 즉시 처리 예약",
                    self.position.status, close, self.position.stop_price,
                )
                QTimer.singleShot(0, self._process_tick_stop)
            # [363차] tick-level 손절1차(Loss Tier1) 감지 — 풀스톱과 상호 배타(elif).
            # 풀스톱이 이미 위에서 감지됐다면(같은 틱이 tier1과 stop을 동시에 뚫은
            # 경우) 여기 도달하지 않는다 — STEP8 파이프라인의 우선순위(풀스톱이
            # 손절계단화보다 먼저 평가)와 동일하게 맞춘 것. is_loss_tier1_hit()가
            # quantity<=1을 이미 자체 배제하므로 qty 체크를 여기서 중복하지 않는다.
            elif (LOSS_TIER1_ENABLED
                    and LOSS_TIER1_TICK_ENABLED
                    and not self._tick_loss_tier1_triggered
                    and self._pending_order is None
                    and self.position.status != "FLAT"
                    and self.circuit_breaker.state != CB_STATE_HALTED
                    and self.position.is_loss_tier1_hit(close)):
                self._tick_loss_tier1_triggered = True
                self._tick_loss_tier1_price     = close
                logger.warning(
                    "[TickLossTier1] 손절1차 히트 감지 (틱) %s tick=%.2f tier1=%.2f → 즉시 처리 예약",
                    self.position.status, close, self.position.loss_tier1_price,
                )
                QTimer.singleShot(0, self._process_tick_loss_tier1)
            # [230차] 100ms 쓰로틀 — minute_chart_tick(chart.update) 은 heavy (348 candles paintEvent)
            _now_tick = time.perf_counter()
            _last_tick_ui = getattr(self, "_last_tick_chart_update", 0.0)
            if _now_tick - _last_tick_ui >= 0.10:   # 100ms 미만이면 스킵
                self._last_tick_chart_update = _now_tick
                logger.info("[TickUI] minute_chart_tick code=%s close=%.2f", self.realtime_data.code, close)
                self.dashboard.minute_chart_tick(close, bar.get("ts"))
        logger.info("[TickUI] update_price code=%s close=%.2f", self.realtime_data.code, float(bar["close"]))
        self.dashboard.update_price(
            price  = bar["close"],
            change = bar["close"] - bar.get("open", bar["close"]),
            code   = self.realtime_data.code,
        )
        logger.info("[TickUI] end code=%s close=%.2f", self.realtime_data.code, float(bar["close"]))

    def _process_tick_stop(self) -> None:
        """[266차] tick-level 하드스톱 실주문 전송 — 메인 스레드에서만 호출.
        COM 콜백(_on_tick_price_update) 내부에서 직접 호출 금지(§4) — 감지는
        그쪽에서 flag만 세팅하고 QTimer.singleShot(0, ...)으로 이 메서드를
        예약([348차] 다음 분봉 롤오버까지 최악 60초 걸리던 것을 다음 이벤트루프
        패스로 단축). run_minute_pipeline S0-C에서도 폴백으로 호출되나, 이
        메서드 자체가 멱등(맨 위에서 flag를 즉시 클리어)이라 두 경로가 겹쳐도
        중복 주문은 없다.

        분봉 파이프라인 진입 즉시(STEP 1 이전) 처리 → 기존 인트라바스톱(STEP 8)보다
        파이프라인 내 순서가 앞서 동일 분봉 내 조기 주문 전송.
        [2026-07-09 실사고 수정] 과거엔 pending 미등록 상태로 주문만 보내고
        close_position()을 즉시(낙관적으로) 호출해 포지션을 먼저 FLAT 처리했다.
        이 경우 뒤늦게 도착하는 실체결이 pending 매칭 실패로 "미추적체결
        (pending_miss)" 경로로 빠져 반대방향 유령 포지션을 새로 여는 사고가
        발생(0709 두 차례, 손실 약 6.75M원 — dev_memory 305차). 수동청산·TP청산·
        정규 하드스톱(_ts_check_exit_triggers)과 동일하게 주문 전송 "전"에 pending을
        선등록하도록 수정 — close_position()/_post_exit()는 더 이상 여기서 즉시
        호출하지 않고, 실제 Chejan 체결이 pending과 매칭돼 정상 ExitFillFlow
        경로로 마감되도록 위임한다. 이중 발동 차단은 STEP 8
        (_ts_check_exit_triggers 최상단의 `_has_pending_order()` 조기 반환)이
        position.status==FLAT 대신 pending 존재 여부로 그대로 보장한다.
        """
        if not getattr(self, "_tick_stop_triggered", False):
            return
        self._tick_stop_triggered = False           # 중복 처리 방지 — 결과 무관 즉시 해제
        _tk_px   = self._tick_stop_price
        _tk_stop = self.position.stop_price
        if (self.position.status != "FLAT"
                and not self._has_pending_order()
                and self.circuit_breaker.state != CB_STATE_HALTED
                and _tk_px > 0):
            # PnL 기준: 손절가 사용 (실제 체결가는 broker fill이 결정)
            _tk_exit = _tk_stop
            _tk_qty = self.position.quantity
            _tk_direction = self.position.status
            log_manager.trade(
                f"[TickStop-S0C] 하드스톱(틱) {_tk_direction} "
                f"{_tk_qty}ct "
                f"tick={_tk_px:.2f} stop={_tk_stop:.2f} → 주문 전송"
            )
            # pending을 주문 전송 전에 먼저 등록 — BlockRequest() 내부 메시지
            # 펌프로 체결 콜백이 먼저 도착하는 race condition 방지
            # (수동청산·TP청산·정규 하드스톱과 동일한 순서).
            self._set_pending_order(
                kind="EXIT_FULL",
                direction=_tk_direction,
                qty=_tk_qty,
                price_hint=round(_tk_exit, 2),
                reason="하드스톱(틱)",
            )
            ret = self._send_broker_exit_order(_tk_qty)
            log_manager.system(
                f"[ExitSendOrderResult] ret={ret} kind=하드스톱(틱) "
                f"direction={_tk_direction} qty={_tk_qty}",
                "WARNING",
            )
            if ret == 0:
                log_manager.trade(
                    f"[주문요청] 하드스톱(틱) 청산 {_tk_direction} {_tk_qty}계약 "
                    f"@ {_tk_exit:.2f} 체결대기"
                )
            else:
                self._clear_pending_order()
                log_manager.system(f"[Exit] 하드스톱(틱) 주문 실패 ret={ret}", "ERROR")

    def _process_tick_loss_tier1(self) -> None:
        """[363차] 손절 계단화 1차 tick-level 처리 — 메인 스레드에서만 호출.

        _process_tick_stop과 동일한 뼈대(flag 최상단 즉시 클리어로 멱등 보장, 상태
        재확인 후 실행)이나 실제 주문 전송 로직은 새로 작성하지 않고 분당 파이프라인
        (STEP8)이 이미 쓰는 self._execute_loss_tier1_exit()(=_ts_execute_loss_tier1_exit,
        pending 선등록→주문→실패 시 롤백까지 내장)를 그대로 재사용한다 — 주문 전송
        로직을 두 곳에 복붙하지 않기 위함. 그 함수 내부의 self._has_pending_order()
        가드가 풀스톱 경로와의 이중발동도 막아준다(둘 다 메인 스레드 순차 실행이라
        진짜 동시성 race는 없음 — §4).
        """
        if not getattr(self, "_tick_loss_tier1_triggered", False):
            return
        self._tick_loss_tier1_triggered = False   # 중복 처리 방지 — 결과 무관 즉시 해제
        price = self._tick_loss_tier1_price
        if (self.position.status != "FLAT"
                and not self._has_pending_order()
                and self.circuit_breaker.state != CB_STATE_HALTED
                and price > 0):
            self._execute_loss_tier1_exit(price)

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
          ② 피처 계산 → raw_data.db 동기 저장 — refit이 갭오픈 분포 자동 흡수
          ③ PRE_MARKET_REFIT_STEPS봉마다 점진 scaler 재적합 (3·5·10·14봉)
          ④ 프리장 conf 히스토리 수집 + z경고 업데이트
        """
        from config.settings import PRE_MARKET_REFIT_STEPS

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
                    self._session_open_price = _pre_close
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

        # ② 피처 계산 → raw_data.db 동기 저장
        # 프리장 봉이 DB에 쌓이면 load_features_for_warmup()이 갭오픈 분포를 자동 흡수.
        # 동기 저장: refit 스레드 기동 전 DB 반영 확정 (race 방지).
        _pm_feats = None
        if self.model.is_ready():
            try:
                _pm_feats = self.feature_builder.build(
                    candle,
                    supply_demand={},
                    macro_data={},
                    option_data={},
                    micro_regime=self.current_micro_regime,
                )
                if _pm_feats:
                    _pm_ts = candle.get("time", now_dt.strftime("%Y-%m-%d %H:%M:%S"))
                    try:
                        save_candle_and_features(candle, _pm_ts, _pm_feats)
                    except Exception as _dbe:
                        logger.debug("[PreMarket] 피처 DB 저장 실패: %s", _dbe)
            except Exception as _fe:
                logger.debug("[PreMarket] 피처 계산 스킵: %s", _fe)

        # ③ PRE_MARKET_REFIT_STEPS봉마다 점진 재적합
        # 3봉(08:47): 통계 안정성 확보, 5·10·14봉: 수렴 → 09:00 GAP_OPEN 완벽 준비.
        # DB 동기 저장(②) 완료 후 스레드 기동 → race 없음.
        if n_bars in PRE_MARKET_REFIT_STEPS and not getattr(self, "_scaler_refresh_running", False):
            _phase = sorted(PRE_MARKET_REFIT_STEPS).index(n_bars) + 1
            _z_feats_now = self._canary_load_z_warn_features(n_rows=n_bars)
            _z_now = len(_z_feats_now)
            self._scaler_refresh_running = True
            if n_bars == min(PRE_MARKET_REFIT_STEPS):
                # Phase1 기동 즉시 ScalerWarmup(08:55) 스킵 예약
                self._pre_market_scaler_refitted = True
            log_manager.system(
                f"[PreMarket] Phase{_phase} refit 기동 ({n_bars}봉 z경고={_z_now}개)",
                "INFO",
            )
            def _pm_refit_worker(_nb=n_bars, _ph=_phase, _z=_z_now, _zf=_z_feats_now):
                try:
                    # 단기 window 사용: 500봉은 전날 분포 위주 → 오늘 갭오픈 z경고 고착
                    # PRE_MARKET_SCALER_BARS(30봉)로 오늘 비율 최대화 (bar14: 47% today)
                    from config.settings import PRE_MARKET_SCALER_BARS as _PM_LB
                    _Xpm, _fnpm = self.batch_retrainer.load_features_for_warmup(
                        lookback_bars=_PM_LB
                    )
                    if _Xpm is not None:
                        self.model.refit_scalers_only(
                            _Xpm, _fnpm,
                            trigger_type="A_WARMUP",
                            trigger_reason=f"pre_market_phase{_ph}_{_nb}bars",
                        )
                        _z_feats_after = self._canary_load_z_warn_features(n_rows=_nb)
                        _z_after = len(_z_feats_after)
                        _z_worsened = _z_after > _z + 3
                        # 273차: refit 전후 모두 z경고인 피처 = 이번 refit이 억제 못한 피처
                        # (Phase4가 Phase1~3와 달리 무효했던 원인 진단용, 08:59 딥다이브)
                        _persist = sorted(set(_zf) & set(_z_feats_after))
                        log_manager.system(
                            f"[PreMarket] Phase{_ph} refit 완료 n={len(_Xpm)}봉"
                            f" z경고 {_z}→{_z_after}개"
                            + (" ⚠ 악화 (봉 수 부족)" if _z_worsened else "")
                            + (f" | 잔존={','.join(_persist)}" if _persist else ""),
                            "WARNING" if _z_worsened else "INFO",
                        )
                    else:
                        log_manager.system(
                            f"[PreMarket] Phase{_ph} refit 스킵 — 데이터 없음", "WARNING"
                        )
                except Exception as _pme:
                    logger.warning("[PreMarket] Phase%d refit 실패: %s", _ph, _pme)
                finally:
                    self._scaler_refresh_running = False
            threading.Thread(target=_pm_refit_worker, daemon=True).start()

        # ④ conf 히스토리 수집 + z경고 업데이트
        if _pm_feats and self.model.is_ready():
            try:
                _pm_proba = self.model.predict_proba(_pm_feats)
                _pm_conf = 0.0
                if _pm_proba:
                    _pm_conf = max(
                        abs(float(v) - 0.5) * 2
                        for v in _pm_proba.values()
                        if isinstance(v, float)
                    )
                self._pre_market_conf_history.append(_pm_conf)
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
            _ecb_start_dt = self._exchange_cb_start
            _gap_min = int(
                (now - _ecb_start_dt).total_seconds() / 60
            ) if _ecb_start_dt else 0
            self._exchange_cb_start = None
            # [303차] EOD 리포트 halt 요약용 — halt 구간 1건 영속 기록
            if _ecb_start_dt:
                try:
                    from utils.db_utils import record_exchange_cb_halt
                    record_exchange_cb_halt(
                        _ecb_start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        now.strftime("%Y-%m-%d %H:%M:%S"),
                        _gap_min,
                    )
                except Exception as _ecb_rec_e:
                    log_manager.system(
                        f"[ExchangeCB] halt 이력 기록 실패 (무해): {_ecb_rec_e}",
                        "WARNING",
                    )
            # [227차] CB⑤ 임계 복원 — ExchangeCB 진입 시 완화했던 것 해제
            # GBM 재학습이 이미 시작되면 set_gbm_retrain_active(True)가 유지됨
            if not getattr(self, "_gbm_retrain_running", False):
                self.circuit_breaker.set_gbm_retrain_active(False)
            log_manager.system(
                f"[ExchangeCB] 거래소 CB 해제 — {_gap_min}분 공백 후 분봉 재개. "
                f"상태 초기화 시작",
                "INFO",
            )
            notify(f"▶ 미륵이 거래소 CB 해제 — {_gap_min}분 후 분봉 재개")
            # 거래소 CB 중 포지션이 열려 있었다면 즉시 시장가 청산
            # (CB 중에는 체결 불가 → 해제 첫 분봉의 close 기준으로 즉시 청산)
            if self.position.status != "FLAT":
                _ecb_close = float(candle.get("close", 0) or 0)
                log_manager.system(
                    f"[ExchangeCB] CB 해제 직후 포지션 보유 ({self.position.status}) — "
                    f"즉시 청산 실행 (close={_ecb_close})",
                    "WARNING",
                )
                try:
                    _ts_broker_direct_force_exit(self, _ecb_close, "ExchangeCB_해제_즉시청산")
                except Exception as _ecb_ex:
                    log_manager.system(
                        f"[ExchangeCB] 즉시 청산 실패: {_ecb_ex} — 수동 확인 필요",
                        "CRITICAL",
                    )
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
                        self._session_open_price = _today_open
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

        try:
            self.dashboard.minute_chart_candle_closed(candle)
        except Exception as _ce:
            logger.debug("[ChartWarn] candle_closed 예외 무시: %s", _ce)
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
            # [193차] 모델 교체를 파이프라인 밖으로 지연 — race condition 방지
            # _load_all() 즉시 호출 시 run_minute_pipeline predict_proba() 와 동시 실행돼
            # "X has N features, expected M" ValueError → apply_error_policy(FATAL) → 자동재시작
            # 반복 패턴: RF 로드 완료 → 8초 → RESTART (오늘 7회 관찰, 2026-06-18)
            # → 플래그로 표시하고 다음 파이프라인 시작 직전(STEP 0)에서 안전하게 교체
            self._pending_model_reload = True
            logger.info("[Model] 재학습 완료 — 다음 파이프라인 시작 전 모델 교체 예약")
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
                # [280차] self.batch_retrainer._retrain_count는 항상 0 — 실제 재학습은
                # _start_gbm_retrain_subprocess()가 매번 새 BatchRetrainer 인스턴스를 만드는
                # py310_64 서브프로세스(retrain_intraday.py)에서 수행되고, 그 안의 카운터는
                # 서브프로세스 종료와 함께 사라진다. 세션에 영속된 누적값에 +1하는 방식으로 대체.
                _prev_count = int(_ss2.get("gbm_total_retrain_count", 0) or 0)
                _new_count  = _prev_count + 1
                _ss2["gbm_last_retrain"] = result.get("timestamp", "")
                _ss2["gbm_total_retrain_count"] = _new_count
                with open(_ss_path, "w", encoding="utf-8") as _ssf:
                    json.dump(_ss2, _ssf, ensure_ascii=False)
                self.batch_retrainer._retrain_count = _new_count  # get_stats() 대시보드 즉시 동기화
                logger.info(
                    "[GBM] 재학습 이력 저장: %s (%d회)",
                    _ss2["gbm_last_retrain"], _new_count,
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

            # 새 GBM 기준으로 BiasReset 상태만 초기화
            # 구 GBM 편향 판정(bias_override_horizons, bias_fl_streak, bias_buf)이
            # 새 모델에 그대로 남으면 uniform fallback 고착 + SGD 대항력 약화 지속
            self._bias_override_horizons.clear()
            self._bias_fl_streak = {h: 0 for h in HORIZONS}
            self._bias_override_timer = {h: 0 for h in HORIZONS}
            for _bh in HORIZONS:
                self._bias_buf[_bh].clear()
            # [P0] online_learner.reset_daily() 호출 제거 (288차)
            # 장중 GBM 재학습(수십 회/일)마다 SGD acc_buf·가중치·표본카운트가 매번
            # 초기화되어 _adjust_weights()의 _MIN_SAMPLES=15 문턱을 영원히 못 넘기는
            # 영구 콜드스타트 루프 유발 — DriftAdjuster도 매번 "표본부족→스킵" 고착.
            # SGD 일간 리셋은 하루 1회 EOD 마감(daily_close 루틴, self.online_learner.reset_daily() 호출부)에서만 수행.
            log_manager.learning(
                "[GBM] 재학습 완료 → BiasReset 상태 초기화 (SGD 누적 학습은 유지)"
            )

            # ── ConstOut 원인 CB③ HALT 해제 시도 ──────────────────────────
            # 스케일러 재적합(scaler refit)만으로는 GBM 트리 구조가 미변경이라 ConstOut 재발 가능.
            # GBM 재학습까지 완료된 시점이 원인 완전 해소 시점이므로 여기서 해제한다.
            if self.circuit_breaker.lift_cb3_halt():
                log_manager.system(
                    "[CB③→RESUME] ConstOut 회복 + GBM 재학습 완료 → HALT 해제 — 거래 재개",
                    "INFO",
                )
                notify(
                    "CB③ HALT 해제 — 거래 재개 (ConstOut 회복 + GBM 재학습 완료)",
                    "INFO",
                )
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
        레짐 확정은 _pre_market_stage2_fetch()에서 2회차 fetch(08:58) 후 실행한다."""
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
                        def _canary_refit_worker(_thresh=_z_bad_thresh):
                            try:
                                # 단기 window(PRE_MARKET_SCALER_BARS=30) 사용:
                                # 500봉은 전날 490봉 위주 → 오늘 갭오픈 z경고 고착
                                # 60봉 = 어제 마지막 1시간 + 오늘 pre-market → 오늘 비율 ≥17%
                                from config.settings import PRE_MARKET_SCALER_BARS
                                _Xcr, _fncr = self.batch_retrainer.load_features_for_warmup(
                                    lookback_bars=PRE_MARKET_SCALER_BARS
                                )
                                if _Xcr is not None:
                                    self.model.refit_scalers_only(_Xcr, _fncr)
                                    self._pre_market_scaler_refitted = True
                                    # post-refit z경고 재측정 — 효과 검증
                                    _pm_n = min(len(getattr(self, "_pre_market_bars", [])), 15)
                                    _z_after = self._canary_load_z_warn(n_rows=max(_pm_n, 10))
                                    _improved = _z_after < _thresh
                                    # [P3] EKS 원인 진단값 갱신 — 재적합 후 최신값으로 덮어쓰기
                                    # (08:55 pre-refit 값인 _last_canary_z_warn 이 EKS 원인으로
                                    #  그대로 사용되면 stale이 됨 — 재적합 완료 시점에 업데이트)
                                    self._last_canary_z_warn = _z_after
                                    self.system_health.update_z_warn(_z_after)
                                    log_manager.system(
                                        f"[Canary] 장전 재적합 완료 n={len(_Xcr)}봉"
                                        f" z경고 →{_z_after}개"
                                        + (" ✓ 임계 이하" if _improved else " ⚠ z경고 지속 — bar14 재적합 대기"),
                                        "INFO" if _improved else "WARNING",
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
                    # 08:55 ScalerWarmup도 단기 window 사용:
                    # 이 경로는 Canary refit / 프리장 refit이 모두 스킵됐을 때만 실행됨
                    from config.settings import PRE_MARKET_SCALER_BARS
                    X_w, fn_w = self.batch_retrainer.load_features_for_warmup(
                        lookback_bars=PRE_MARKET_SCALER_BARS
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
            # GBM 재학습 중(_gbm_retrain_running): 즉시 완료 표시 (재학습 완료 후 scaler 갱신됨)
            # Canary/프리장 refit 실행 중(_scaler_refresh_running): 해당 refit이 완료된 후 event set.
            # _canary_stale=True이면 아래에서 _warmup_done_event.wait()하므로 완료를 기다려야 함.
            if getattr(self, "_gbm_retrain_running", False):
                _warmup_done_event.set()
            else:
                # refit 실행 중 — 완료 시점에 event 설정
                def _wait_refit_done(_evt=_warmup_done_event):
                    import time as _time
                    # _canary_stale=True 시 caller가 wait(timeout=90)으로 기다리므로
                    # 이 스레드가 90초 전에 event를 set해야 타임아웃 전에 unblock 가능.
                    # 85초 = 90초 wait - 마진 5초
                    _deadline = _time.monotonic() + 85
                    while getattr(self, "_scaler_refresh_running", False):
                        if _time.monotonic() > _deadline:
                            logger.warning("[ScalerWarmup] refit 완료 대기 85초 초과 — 강제 진행")
                            break
                        _time.sleep(0.5)
                    _evt.set()
                threading.Thread(target=_wait_refit_done, daemon=True).start()

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
                        self._eod_retrain_gap_date = _eod_d   # [359차] 최종 스킵 로그용 보존
                        log_manager.system(
                            f"[PreRetrain] EOD 재학습 날짜 복원: {_eod_date_str} "
                            f"({_days_ago}일 전) → PreRetrain 스킵 검토",
                            "INFO",
                        )
            except Exception as _pre_ss_e:
                logger.warning("[PreRetrain] eod_retrain_ok_date 복원 실패 (무해): %s", _pre_ss_e)
        # [Fallback] session_state 미기록 시 마커 파일 직접 확인
        # 원인: daily_close(15:40) 시점에 retrain_eod.py 미완료 → 마커 없음 → session_state 저장 생략
        #       retrain_eod.py가 15:40 이후 완료(예: 15:57)되면 다음날까지 eod_retrain_ok_date 공백
        if not getattr(self, "_eod_retrain_ok", False):
            try:
                _mdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
                for _d in range(1, 6):
                    _prev = datetime.date.today() - datetime.timedelta(days=_d)
                    _mf = os.path.join(_mdir, f"eod_retrain_done_{_prev.strftime('%Y%m%d')}.txt")
                    if os.path.exists(_mf):
                        self._eod_retrain_ok = True
                        self._eod_retrain_gap_date = _prev   # [359차] 최종 스킵 로그용 보존
                        log_manager.system(
                            f"[PreRetrain] EOD 마커 파일 직접 확인 ({_d}일 전: {_prev}) "
                            f"→ PreRetrain 스킵 (session_state 미기록 보완)",
                            "INFO",
                        )
                        break
            except Exception as _mf_e:
                logger.warning("[PreRetrain] 마커 파일 직접 확인 실패 (무해): %s", _mf_e)
        if (
            getattr(self, "_warmup_retrain_pending", False)
            and not getattr(self, "_gbm_retrain_running", False)
        ):
            self._warmup_retrain_pending = False
            if getattr(self, "_eod_retrain_ok", False):
                # [359차] "전날" 하드코딩 → 실제 경과 영업일 반영 (휴장 낀 재시동 시 혼동 방지)
                _gap_date = getattr(self, "_eod_retrain_gap_date", None)
                if _gap_date:
                    _today_d = datetime.date.today()
                    _gap_biz_days = sum(
                        1 for _gi in range(1, 6)
                        if (_gap_date + datetime.timedelta(days=_gi)) <= _today_d
                        and is_trading_day(_gap_date + datetime.timedelta(days=_gi))
                    ) or 1
                    _gap_tag = f"{_gap_biz_days}영업일 전({_gap_date})"
                else:
                    _gap_tag = "전날"
                log_manager.system(
                    f"[PreRetrain] 08:55 사전 재학습 스킵 — {_gap_tag} EOD 재학습 성공 (동일 데이터 중복 불필요)",
                    "INFO",
                )
            else:
                self.dashboard.set_model_status("GBM 사전 재학습중(64bit)...")
                log_manager.system(
                    "[PreRetrain] 08:55 GBM 사전 재학습 시작 — EOD 미완료 또는 재시작 복구 (64bit subprocess)", "INFO"
                )
                # [226차] PreRetrain도 64비트 subprocess — 32비트 OOM 없이 full 재학습
                self._start_gbm_retrain_subprocess(
                    force=True, reason="08:55 PreRetrain", is_warmup=True, intraday=False,
                )

    def _pre_market_stage2_fetch(self):
        """[359차] 2단계(08:58) 실제 fetch — 백그라운드 스레드 전용.
        macro fetch(최대 5회 순차 blocking requests)와 investor fetch(COM BlockRequest
        폴링 대기)가 도합 3~4초 이상 걸려 메인스레드(Qt 이벤트루프)를 정체시키던 것을
        `_b_intraday_worker`와 동일한 threading.Thread+플래그폴링 패턴으로 이관한다.
        여기서는 Qt 위젯을 절대 건드리지 않는다 — 대시보드 반영은 _pre_market_stage2_apply()가
        다음 하트비트 틱에서 메인스레드로 수행."""
        try:
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

            # 투자자 warmup fetch — _last_fetch 초기화로 09:00 첫 파이프라인 z-score 폭발 방지.
            # _last_fetch=None 상태에서는 age_sec=9999 → quality_investor_stale z-score +27 발생.
            # 장전 fetch라 nets={}가 예상되지만 _last_fetch 설정만으로도 효과가 있다.
            try:
                self.investor_data.fetch_all(include_program=False)
                logger.info("[System] PreOpen 투자자 warmup fetch 완료 (age_sec 초기화)")
                log_manager.system("PreOpen 투자자 warmup fetch 완료")
            except Exception as _e:
                logger.warning("[System] PreOpen 투자자 warmup fetch 실패 (무해): %s", _e)

            notify_premarket_ready(self.current_regime, getattr(self, "_futures_code", "?"))

            self._stage2_result = {"macro_data": macro_data, "description": result["description"]}
        except Exception as _s2_e:
            logger.warning(
                "[PreMarketStage2] fetch 실패 (무해, 09:05까지 다음 하트비트에서 재시도): %s", _s2_e
            )
        finally:
            self._pre_market_stage2_running = False

    def _pre_market_stage2_apply(self, _res: dict):
        """[359차] Qt 위젯 반영 전용 — 반드시 메인스레드(하트비트)에서만 호출할 것."""
        _macro = _res["macro_data"]
        self.dashboard.update_supply_macro(
            vix=_macro["vix"],
            sp500_chg=_macro["sp500_chg_pct"] / 100,
            usd_krw=_macro["usd_krw_chg_pct"],
            regime=self.current_regime,
        )
        self.dashboard.append_sys_log(
            f"레짐 확정: {self.current_regime} | {_res['description']}"
        )
        self.dashboard.set_ui_ready_mode()

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

        # ── [S0-A] 64비트 GBM subprocess 완료 체크 ────────────────────────
        # [226차] poll()은 non-blocking — subprocess가 완료되면 returncode 반환.
        # 완료 즉시 결과 JSON 읽고 _on_gbm_retrain_done() 호출 (메인 스레드 안전).
        _subproc = getattr(self, "_retrain_subproc", None)
        if _subproc is not None:
            _rc = _subproc.poll()
            if _rc is not None:
                _result = {"ok": _rc == 0, "error": f"exit={_rc}"}
                _rpath  = getattr(self, "_retrain_subproc_result_path", "")
                if _rpath and os.path.exists(_rpath):
                    try:
                        with open(_rpath, "r", encoding="utf-8") as _rf:
                            _result = json.load(_rf)
                        os.remove(_rpath)
                    except Exception as _rpe:
                        logger.warning("[GBM-64] 결과 JSON 읽기 실패: %s", _rpe)
                _is_wu = getattr(self, "_retrain_subproc_is_warmup", False)
                # [267차] stderr 파일 닫기 + 내용 로깅 (py310 경고 가시화)
                _stderr_fh = getattr(self, "_retrain_subproc_stderr_fh", None)
                if _stderr_fh is not None:
                    try:
                        _stderr_fh.flush()
                        _stderr_fh.close()
                        _spath = getattr(_stderr_fh, "name", "")
                        if _spath and os.path.exists(_spath):
                            _stderr_size = os.path.getsize(_spath)
                            if _stderr_size > 0:
                                with open(_spath, "r", encoding="utf-8", errors="replace") as _sf:
                                    _stderr_txt = _sf.read(2000)  # 최대 2000자
                                logger.warning(
                                    "[GBM-64] subprocess stderr (%d bytes):\n%s",
                                    _stderr_size, _stderr_txt,
                                )
                            else:
                                os.remove(_spath)  # 빈 파일 삭제
                    except Exception as _sfe:
                        logger.debug("[GBM-64] stderr 파일 처리 오류: %s", _sfe)
                    self._retrain_subproc_stderr_fh = None
                self._retrain_subproc = None
                self._retrain_subproc_result_path = ""
                self._gbm_retrain_running     = False
                self._gbm_retrain_started_at  = None
                self._gbm_retrain_done_event.set()
                self.circuit_breaker.set_gbm_retrain_active(False)
                log_manager.learning(
                    f"[GBM-64] subprocess 완료 (returncode={_rc}) → _on_gbm_retrain_done 호출"
                )
                self._on_gbm_retrain_done(_result, _is_wu)

        # ── [S0-B] ConstOut 재적합 완료 콜백 큐 drain — P1 QTimer 불안정 대체 ──
        # ConstOut refit worker → _deferred_callbacks.put("const_out_done") →
        # 여기서 메인 스레드 소비. GBM done은 [226차] subprocess poll로 이동.

        # ── [S0-C] tick-level 하드스톱 처리 (폴백 안전망) ────────────────────
        # [348차] 실제 주문 전송 경로는 이제 _on_tick_price_update에서 직접
        # QTimer.singleShot(0, ...)으로 예약 — 최악 60초(다음 분봉 롤오버)
        # 지연되던 것을 다음 이벤트루프 패스(수십ms)로 단축. 이 블록은 그
        # 싱글샷이 어떤 이유로든(이벤트루프 기아 등) 못 돈 경우를 대비한
        # 폴백일 뿐이며, _process_tick_stop() 내부에서 flag를 즉시 클리어하는
        # 멱등 설계라 두 경로가 겹쳐도 중복 주문은 발생하지 않는다.
        self._process_tick_stop()

        while True:
            try:
                _dcb = self._deferred_callbacks.get_nowait()
            except _queue.Empty:
                break
            try:
                _dcb_tag = _dcb[0]
                if _dcb_tag == "const_out_done":
                    self._on_const_out_refit_done(_dcb[1])
                # gbm_done 태그: [226차] subprocess 이관 — 큐에서 수신 시 무시(잔여 배출)
            except Exception as _dcb_e:
                logger.warning("[DeferredCB] 콜백 처리 오류 (tag=%s): %s", _dcb[0] if _dcb else "?", _dcb_e)

        # ── [P3] CB③ HALT 주기적 해제 재시도 ─────────────────────────────
        # ConstOut 재적합 + GBM 재학습이 완료됐으나 콜백 누락으로 lift 안 된 경우 복구.
        # 15분마다 조건 확인: HALTED + cb3 원인 + 재학습·스케일러 재적합 미실행.
        if (not getattr(self, "_gbm_retrain_running", False)
                and not getattr(self, "_scaler_refresh_running", False)):
            _cb3_state = self.circuit_breaker
            if (_cb3_state.state == "HALTED"
                    and getattr(_cb3_state, "_halt_cause", "") == "cb3"):
                _ts_min_for_cb3 = int(ts[14:16]) if len(ts) >= 16 else -1
                if _ts_min_for_cb3 >= 0 and _ts_min_for_cb3 % 15 == 0:
                    if _cb3_state.lift_cb3_halt():
                        log_manager.system(
                            "[CB③→RESUME] 주기적 재시도 → HALT 해제 "
                            "(ConstOut 재적합·GBM 재학습 완료 누락 복구)",
                            "INFO",
                        )

        # ── [S0] 재학습 완료 모델 교체 — predict_proba 전 안전 지점 ─────────
        # _on_gbm_retrain_done 이 플래그를 세우면 여기서 소비.
        # 파이프라인 실행 중 모델 객체 교체 race condition 방지 (193차).
        if getattr(self, "_pending_model_reload", False):
            self._pending_model_reload = False
            _bad = self.model._load_all()
            if _bad:
                logger.error(
                    "[Model] 재학습 후 %d개 호라이즌 차원 불일치: %s → 재학습 재트리거",
                    len(_bad), _bad,
                )
                self._start_manual_retrain(force=True, reason="resync_mismatch")
            try:
                self.rf_model.load_all()
            except Exception:
                pass
            self._rebuild_sgd_feat_indices()   # [P2] feature_names 교체 반영
            logger.info("[Model] 재학습 완료 모델 교체 적용 (S0)")

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
        # [225차 P0] _last_pipeline_price 는 _on_tick_price_update(현재 봉 tick)에 의해
        # 파이프라인 진입 전 이미 cur_p 로 덮어써져 ret=0 고착 → 전용 변수 사용
        _prev_pipeline_price      = self._sigma_prev_price     # sigma 계산용 이전 종가
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
                    # [269차] EXIT Chejan 이벤트 유실 카운터 — 빈도 집계 후 daily_close에서 보고
                    self._chejan_exit_miss_count = getattr(self, "_chejan_exit_miss_count", 0) + 1
                    log_manager.system(
                        f"[ChejanMiss] EXIT 이벤트 유실 #{self._chejan_exit_miss_count} "
                        f"filled={_po['filled_qty']}/{_po['qty']} order_no={_po.get('order_no','?')} "
                        f"elapsed={_since_last_fill:.0f}s",
                        "WARNING",
                    )
                    log_manager.system(
                        f"[PendingOrder] EXIT 부분체결 stuck {_since_last_fill:.0f}s — "
                        f"filled={_po['filled_qty']}/{_po['qty']} "
                        f"kind={_po['kind']} order_no={_po.get('order_no','?')} "
                        f"→ 브로커 잔고 조회 후 처리 (소멸 여부는 조회 결과에 따름)",
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
            # [311차 후속 B안] 극단성 보정기 기록 — fit()은 daily_close()에서만(느린層)
            _ext_extra = compute_extremity_hinge(v.get("features") or {}, _pred_dir)
            self.extremity_corrector.record(v["horizon"], _conf, _ext_extra, v["correct"])
            # [311차 후속9] SHAP 중요도용 라벨 있는 (X, y) 버퍼 — permutation_importance는
            # 검증완료 실제 레이블이 있어야 계산 가능(TreeExplainer/feature_importances_와
            # 달리 라벨 없이는 동작 불가). 1m/3m/5m만 추적(단기군 CORE 딥다이브 대상).
            if v["horizon"] in self._shap_labeled_window and self.model.feature_names:
                _shap_vec = [
                    float((v.get("features") or {}).get(name, 0.0) or 0.0)
                    for name in self.model.feature_names
                ]
                self._shap_labeled_window[v["horizon"]].append(
                    (_shap_vec, int(v.get("actual", 0)))
                )
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
            # 시간대별 정확도/기대손익 기록 (15:40 DailyConsolidator.consolidate()에서 집계)
            # [311차 후속3] 표본 확충: 5m 단독 → 3m+5m 합산(하루 표본 66%↑, P1).
            # 1m은 후속6 딥다이브에서 유의한 역스킬(acc 47.75%, p=0.0048) 확정돼 제외.
            if v["horizon"] in ("3m", "5m"):
                _zone = get_time_zone(datetime.datetime.strptime(v["ts"], "%Y-%m-%d %H:%M:%S"))
                self.daily_consolidator.record(
                    _zone, bool(v["correct"]), predicted_dir=_pred_dir,
                    realized_move=float(v.get("realized_move", 0.0)),
                )
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
                _need_trained = getattr(
                    runtime_settings, "HORIZON_QUALIFY_MIN_TRAINED", {}
                ).get(_h, _need)
                if _qs["verified_cycles"] >= _need and _qs["trained_cycles"] >= _need_trained:
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
                    "[Qualify] %s verified=%d/%d trained=%d/%d status=%s",
                    _h, _qs["verified_cycles"], _need,
                    _qs["trained_cycles"], _need_trained, _qs["status"],
                )

        # ── 호라이즌별 롤링 Bias 통계 (30건 윈도우) ──────────────────────────
        # 분봉 1건씩 누적 → 15건 이상 쌓이면 편향 판정 / 10분마다 요약 출력
        # bias_override active 호라이즌은 기록 스킵:
        #   uniform fallback 후 direction=0이 쌓이면 FL 카운트가 유지되어
        #   해제 조건(_dir_bias_r < 0.60)이 영구 달성 불가 → 타이머로만 해제
        if verified:
            for _v in verified:
                _h_name_v = _v["horizon"]
                if _h_name_v in self._bias_override_horizons:
                    continue
                self._bias_buf[_h_name_v].append({
                    "predicted": int(_v.get("predicted", 0)),
                    "correct":   bool(_v["correct"]),
                })

            self._bias_log_tick += 1
            _log_summary = (self._bias_log_tick % 10 == 0)

            # ── bias_override 자동 해제 타이머 ────────────────────────────────
            # buf 스킵 중이므로 조기 해제(bias < 60%) 평가 불가 → 타이머로 해제
            for _ht in list(self._bias_override_horizons):
                _t = self._bias_override_timer.get(_ht, 0)
                if _t > 0:
                    self._bias_override_timer[_ht] = _t - 1
                if self._bias_override_timer.get(_ht, 0) <= 0:
                    self._bias_override_horizons.discard(_ht)
                    self._bias_buf[_ht].clear()
                    self._bias_fl_streak[_ht] = 0
                    log_manager.learning(
                        f"[BiasReset] {_ht} uniform fallback 자동 해제 (20분 경과)"
                    )

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
                    # [241차] 0.75→0.60/0.65: 실측 편향(47~64%)이 기존 75% 임계 아래에서
                    # 감지 불가했던 문제 해소. FL은 자연 발생 가능성이 높아 0.65 유지.
                    if _up_r >= 0.60:
                        _bias_tag = f" [UP편향⚠ {_up_r:.0%}]"
                    elif _dn_r >= 0.60:
                        _bias_tag = f" [DN편향⚠ {_dn_r:.0%}]"
                    elif _fl_r >= 0.65:
                        _bias_tag = f" [FL편향⚠ {_fl_r:.0%}]"

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
                # [241차] 1m UP/DN streak 5→8분: 임계 하향(0.62)으로 인한 오발동 방지
                # 0.62×8분 = 충분한 증거, 단순 잡음과 구조적 편향 구분
                _dn_up_streak = 8 if _h == "1m" else 5
                _bias_thresh_min = (5 if _in_coldstart else 10) if _biased_dir == "FL" else _dn_up_streak
                # 0.80→0.70: 3m/5m FL=75~79% 구간이 80% 미달로 BiasReset 미발동하는 gap 해소
                # 적중률 >= 0.55이면 BiasReset 스킵 — 편향이지만 정확하면 오히려 정상 신호
                # (30m UP=100% 적중=100% 사례: 시장이 실제 상승 중인데 BiasReset이 신호 소멸)
                # [241차] 1m DN/UP: 0.70→0.62, acc 0.55→0.50
                #   근거: 6/16~6/24 실측 편향이 0.60~0.64 구간에 집중 (기존 0.70 미달로 무감지)
                #   1m만 하향: 타 호라이즌은 봉 단위가 길어 60~65% 방향성이 자연 발생 가능
                _BIAS_RESET_THR = {"1m": 0.62}   # 1m 전용 하향, 나머지 0.70 유지
                _bias_thr_h     = _BIAS_RESET_THR.get(_h, 0.70)
                _acc_ok_for_bias = _acc_h < (0.50 if _h == "1m" else 0.55)
                if _tot >= 15 and _dir_bias_r >= _bias_thr_h and _acc_ok_for_bias:
                    self._bias_fl_streak[_h] = self._bias_fl_streak.get(_h, 0) + 1
                    if (self._bias_fl_streak[_h] >= _bias_thresh_min
                            and _h not in self._bias_override_horizons):
                        self._bias_override_horizons.add(_h)
                        # buf clear: 이전 FL 이력 제거 → 발동 후 Bias⚠ 반복 출력 차단
                        # 이전 이력 유지 시 FL 26건이 남아 해제 조건(_dir_bias_r < 0.60) 영구 미달
                        self._bias_buf[_h].clear()
                        self._bias_fl_streak[_h] = 0
                        # 20분 자동 해제 타이머 (buf 스킵으로 조기해제 불가 대비)
                        self._bias_override_timer[_h] = 20
                        log_manager.learning(
                            f"[BiasReset] {_h} {_biased_dir}편향 {_dir_bias_r:.0%} "
                            f"적중={_acc_h:.0%} {_bias_thresh_min}분 지속 → uniform fallback 적용 (20분 후 자동해제)"
                        )
                        self.circuit_breaker.record_horizon_fl_bias(
                            _h, _dir_bias_r, _bias_thresh_min
                        )
                        # P4: GBM 편향 감지 → SGD 오염 파라미터 제거 (모델·스케일러·가중치 리셋)
                        # boost_sgd_for_bias(가중치만 올림)에서 교체: boost 후 UP 방향 고착 부작용 제거
                        # BiasReset uniform fallback 기간에 SGD 리셋이 동기화되어 공백 없음
                        self.online_learner.reset_sgd_for_bias(_h)
                else:
                    # P1: fallback 해제 조건 — 아래 중 하나 충족 시 해제
                    #  A) 방향편향 < 60% (정상화)
                    #  B) 적중률 >= 0.60 (편향 지속이지만 정확함 = 원웨이장 전환)
                    # B 추가 근거: 12:13 30m BiasReset 발동(적중=0%) 후 12:29 시장 상승 전환.
                    #   적중률이 60%+ 되면 "편향이 아니라 원웨이"로 판단 → uniform 해제.
                    _can_release = _dir_bias_r < 0.60 or _acc_h >= 0.60
                    if _h in self._bias_override_horizons:
                        if _can_release:
                            _release_reason = (
                                f"방향편향 해소({_dir_bias_r:.0%})" if _dir_bias_r < 0.60
                                else f"적중률 회복({_acc_h:.0%}→원웨이 판정)"
                            )
                            self._bias_override_horizons.discard(_h)
                            # P0: 오염된 편향 이력도 함께 초기화 → 해제 즉시 재고착 방지
                            self._bias_buf[_h].clear()
                            self._conf_stuck[_h] = 0
                            log_manager.learning(
                                f"[BiasReset] {_h} {_biased_dir}편향 "
                                f"→ uniform fallback 해제 ({_release_reason})"
                            )
                        # else: 60~80% 구간 + 저적중률 → fallback 유지, streak만 리셋
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
                        context="verify",  # [316차] STEP1 검증 재평가 — 실거래 게이팅 아님, skip 로그 DEBUG로 격하
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
        # 조건A: 5분 정확도 25% 미만 + 최소 20건 집계 + 마지막 재학습 60분 이상 경과
        # 조건B(조기): 5분 정확도 15% 미만 + 최소 15건 + 30분 이상 경과 (극단 혼란 시 조기화)
        # 근거: 6/12 13:51 CB③ 발동 — acc30m=6.7%, 마지막 재학습 11:10 (약 2.5시간 전)
        # [P1, 303차 후속] 기준 호라이즌을 30m→5m으로 교체.
        #   296차로 30m은 앙상블·CB③·CascadeCoherence에서 전면 퇴역(EOD full_cv acc=0.3052,
        #   랜덤 이하)됐음에도 DriftRetrain은 CB의 30m 전용 accuracy_buf를 그대로 읽고
        #   있었음 — 실거래에 반영되지 않는 호라이즌의 잡음성 저하로 재학습을 반복
        #   트리거하는 낭비. 5m은 단기 CORE(CVD/VWAP/OFI)로 앙상블에 실제 반영되는
        #   활성 호라이즌 — online_learner._acc_buf(호라이즌별 100분 롤링, 일간 리셋,
        #   conf>=0.52·봉단위 dedup 적용)를 그대로 조회해 DB 쿼리 추가 없이 대체.
        # 부작용 방어:
        #   n >= 20(A)/15(B) 조건: 표본 부족(<5) 시 horizon_accuracy()가 0.0을 반환해도
        #   n 게이트가 먼저 막아 오발동 방지 (세션 초기·재시작 직후 n=0 상태 포함)
        _dr_acc5m     = self.online_learner.horizon_accuracy("5m")
        _dr_acc5m_n   = self.online_learner.horizon_acc_samples("5m")
        _dr_last_rt   = getattr(self.batch_retrainer, "_last_retrain", None)
        _dr_mins = (
            (datetime.datetime.now() - _dr_last_rt).total_seconds() / 60
            if _dr_last_rt else float("inf")
        )
        _not_halted   = self.circuit_breaker.state != CB_STATE_HALTED
        _not_running  = not getattr(self, "_gbm_retrain_running", False)
        # 실패 쿨다운: 성공 여부와 무관하게 시도 후 5분간 재트리거 차단
        # 재학습이 즉시 실패해 _last_retrain이 갱신되지 않아도 매분 재실행되는 현상 방지
        _dr_last_attempt = getattr(self, "_drift_retrain_last_attempt", None)
        _dr_attempt_mins = (
            (datetime.datetime.now() - _dr_last_attempt).total_seconds() / 60
            if _dr_last_attempt else float("inf")
        )
        _drift_cooldown_ok = _dr_attempt_mins >= 5.0
        # 조건A: 표준 — acc<25% + n>=20 + 60분 경과
        _drift_trigger_a = (
            _not_halted
            and _dr_acc5m < 0.25
            and _dr_acc5m_n >= 20
            and _dr_mins >= 60.0
            and _not_running
            and _drift_cooldown_ok
        )
        # 조건B: 조기 — acc<15% + n>=15 + 30분 경과 (UP/DN 혼재 극단 혼란)
        _drift_trigger_b = (
            _not_halted
            and _dr_acc5m < 0.15
            and _dr_acc5m_n >= 15
            and _dr_mins >= 30.0
            and _not_running
            and _drift_cooldown_ok
        )
        _drift_trigger = _drift_trigger_a or _drift_trigger_b
        if _drift_trigger:
            _dt_reason = (
                f"acc5m={_dr_acc5m:.1%}(n={_dr_acc5m_n}) < 15% → 조기 트리거 ({_dr_mins:.0f}분 경과)"
                if _drift_trigger_b
                else f"acc5m={_dr_acc5m:.1%}(n={_dr_acc5m_n}) < 25% ({_dr_mins:.0f}분 경과)"
            )
            log_manager.system(
                f"[DriftRetrain] {_dt_reason} → 장중 경량 재학습 트리거",
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
            _reason_s = "WarmupRetrain" if _warmup_forced else ("DriftRetrain" if _drift_trigger else "periodic")
            if _warmup_forced:
                self._warmup_retrain_pending = False
            elif _drift_trigger:
                self._drift_retrain_last_attempt = datetime.datetime.now()
            # [226차] 64비트 subprocess 경량 재학습 — 32비트 OOM 없이 실행
            self.dashboard.set_model_status("GBM 재학습중(64bit)...")
            self._start_gbm_retrain_subprocess(
                force=False, reason=f"STEP3 {_reason_s}",
                is_warmup=bool(_warmup_forced), intraday=True,
            )

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
        # 옵션 체인 폴링은 _option_chain_timer(QTimer 300s)에서 OptionChainWorker(QThread)로 비동기 실행.
        # 파이프라인은 캐시된 피처만 읽는다 (1분 지연 허용, 메인 스레드 블로킹 없음).
        _chain_feats = self.option_chain_snap.get_features()
        # [BUG FIX] _chain_feats(opt_chain_pcr/opt_gex_bn/opt_atm_*)를 option_data에 병합.
        # 이전: _chain_feats가 읽혔지만 build()에 전달되지 않아 raw_features에 저장 안 됨.
        _option_combined = dict(_option_feats)
        _option_combined.update(_chain_feats)
        # [260704 감사 P2] 베이시스 — KOSPI200 현물지수는 _kospi200_index_timer(60s)가
        # 캐시한 self._last_kospi200_spot을 읽는다 (1분 지연 허용, 메인 스레드 블로킹 없음).
        _basis_feats = self.basis_calc.update(
            float(bar.get("close", 0.0) or 0.0), self._last_kospi200_spot,
        )
        # [260704 감사 P2] VKOSPI 장중값 — 같은 60s 타이머가 캐시한 self._last_vkospi.
        # 별도 계산 없이 원값 그대로 전달, 결측 시 ready=False로 표시(0 리셋 방지).
        _basis_feats["vkospi"] = float(self._last_vkospi) if self._last_vkospi else 0.0
        _basis_feats["vkospi_ready"] = 1.0 if self._last_vkospi else 0.0
        features = self.feature_builder.build(
            bar,
            supply_demand = supply_feats,
            macro_data    = _macro_feats,
            option_data   = _option_combined,
            basis_data    = _basis_feats,
            micro_regime  = self.current_micro_regime,  # 직전 분 레짐 (1분 lag 허용)
        )
        # 최소 0.5pt 보장 — 재시작 직후 1개 틱만으로 계산된 비정상 소ATR 방어
        atr      = max(features.get("atr", 0.5), 0.5)
        atr_ratio = features.get("atr_ratio", 1.0)
        self._atr_recent_window.append(atr)  # 273차: 적응형 ATR 상한용 롤링 이력

        # SHAP 대시보드용 VIX·PCR 실측값 캐싱 (매분)
        _mv = features.get("macro_vix")
        if _mv is not None:
            self._last_macro_vix_raw = float(_mv)
        _pcr = features.get("opt_chain_pcr")
        if _pcr and float(_pcr) > 0:
            self._last_opt_chain_pcr = float(_pcr)
        # RV-IV 스프레드 대시보드 표시 (328차)
        self.dashboard.update_rv_iv_spread(features)

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
                        self._db_write_queue.put_nowait(("horizon_features", ts, _h_name, _h_feats, self.current_regime))
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
            # 레벨이 유지되는 동안 매분 동일 WARN이 반복 적재되는 것을 방지 —
            # 레벨 전환 시점은 즉시 로그, 그 외에는 5분 간격 하트비트로 축소.
            _fp_lv_changed = _fp_lv != self._fp_last_logged_level
            self._fp_last_logged_level = _fp_lv
            # [303차] PSI 계측 결함(균등폭 10-bin 첨봉 분포)으로 CRITICAL/ALARM이
            # 상시 고착 — 차단은 이미 비활성(FP_CRITICAL_GRADE_BLOCK_ENABLED=False)이고
            # 실제로 라이브에 반영되지 않는 계측치이므로 대시보드 경보 탭에는 올리지
            # 않는다(오탐지성 반복 경보로 실제 이상 신호를 파묻음). file 로거로만 남겨
            # 셰도우 모니터링(사후 grep·재설계 검증용)은 유지 — CLAUDE.md FP-CRITICAL 참조.
            if _fp_psi > 0.30:
                if _fp_lv_changed or _ts_should_emit_throttled(
                    self, "fp_psi_critical", min_interval_sec=300.0
                ):
                    logger.warning(
                        "[RegimeFingerprint] PSI=%.3f CRITICAL — "
                        "시장 구조 변화 감지, 감시전용(차단 비활성, 대시보드 미표시)",
                        _fp_psi,
                    )
            elif _fp_psi > 0.20:
                if _fp_lv_changed or _ts_should_emit_throttled(
                    self, "fp_psi_alarm", min_interval_sec=300.0
                ):
                    logger.warning(
                        "[RegimeFingerprint] PSI=%.3f ALARM — "
                        "param_optimizer 예약 권장(대시보드 미표시)",
                        _fp_psi,
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
            " | cvd_delta=%.3f ofi=%+d vwap_pos=%.4f hurst=%.3f vol=%d"
            " | bid=%.2f ask=%.2f buyvol=%d sllvol=%d",
            ts, close,
            features.get("atr", 0.0), atr,
            float(features.get("cvd_delta_norm", 0.0) or 0.0),
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
        self._micro_regime_instability = _mr.get("instability_10m", 0)   # [359차]
        self.dashboard.update_micro_regime(
            _mr["regime"], _mr["adx"], _mr["atr_ratio"], _mr["regime_duration"]
        )
        self.dashboard.update_micro_regime_warmup(_mr.get("warmup"))
        # 1분봉 차트 레짐 색상 바 업데이트 + 재시작 복원용 DB 저장
        try:
            self.dashboard.minute_chart_set_regime(ts, _mr["regime"])
        except Exception as _cre:
            logger.debug("[ChartWarn] set_regime_at 예외 무시: %s", _cre)
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
                        # Q3: 피처 decay 제거 — 완성봉 원본 그대로 투입
                        # (학습/추론 분포 일치. decay는 하단 confidence 감쇠에서만 유지)
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
                # [P2] SGD 전용 피처 슬라이싱 — GBM(_hz_feat_indices)과 별도 인덱스 사용
                _sgd_h_idx  = self._sgd_feat_indices.get(h_name)
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
                            f"u={sgd_p['up']:.3f}/d={sgd_p['down']:.3f}"  # [P3] SGD는 방향만 보유
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

            # Q3: 배포 정책 미충족 호라이즌 앙상블에서 제거
            # bar_only (3m/5m): age>0 제거, bar_plus1 (10m/15m): age>1 제거
            # filter_only (30m): 항상 통과 — 앙상블 내부에서 직접 진입 차단
            for _h_dp in list(horizon_proba.keys()):
                if not _is_deployable(_h_dp, self.bar_aggregator):
                    _dp_age = self.bar_aggregator.get_bar_age(_h_dp)
                    del horizon_proba[_h_dp]
                    logger.debug(
                        "[Deploy] %s 스킵 (age=%d, policy=%s)",
                        _h_dp, _dp_age,
                        HZ_DEPLOY_POLICY.get(_h_dp, {}).get("mode", "?"),
                    )

            # [Deploy] 배포 상태 요약 로그
            for _dl_h in HORIZONS:
                _dl_age = self.bar_aggregator.get_bar_age(_dl_h)
                _dl_dep = _dl_h in horizon_proba
                _dl_pol = HZ_DEPLOY_POLICY.get(_dl_h, {}).get("mode", "?")
                logger.debug(
                    "[Deploy] %-4s | age=%2d | policy=%-12s | %s",
                    _dl_h, _dl_age, _dl_pol,
                    "✅ 배포" if _dl_dep else "⏸ 스킵",
                )

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
            # [P3] SGD는 UP/DN 방향만 판단 — GBM 부재 시 flat 판단 근거가 없으므로 1/3 고정
            horizon_proba = {}
            for h in HORIZONS:
                _sgd_fv_raw = _hz_feat_vecs[h] if _hz_feat_vecs else feat_vec
                # [P2] SGD 전용 피처 슬라이싱 (기존엔 누락돼 있었음 — 미학습 상태라 무해했으나
                # 학습이 시작되는 즉시 학습/예측 피처 공간 불일치가 생길 수 있어 함께 수정)
                _sgd_h_idx = self._sgd_feat_indices.get(h)
                _sgd_fv    = _sgd_fv_raw[_sgd_h_idx] if _sgd_h_idx is not None else _sgd_fv_raw
                sgd_p = self.online_learner.predict_proba(h, _sgd_fv)
                if sgd_p is None:
                    sgd_p = {"up": 0.5, "down": 0.5}
                fl = 1 / 3
                up = sgd_p["up"] * (1 - fl)
                dn = sgd_p["down"] * (1 - fl)
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
        # [225차 P4] GBM 재학습 타임아웃 — 장전 PreRetrain 행/완료 미콜백 시 조기 해제
        # deferred 큐 도입으로 콜백 누락은 해소됐으나, retrain_now() 자체 행 대비 안전망 유지.
        # 기존 30분(1800s) → 10분(600s): PreRetrain은 ~3분 내 완료 기대.
        # intraday 재학습(force=False)은 더 빠르므로 600s 임계 안에 항상 수렴.
        _gbm_started = getattr(self, "_gbm_retrain_started_at", None)
        if (self._gbm_retrain_running and _gbm_started is not None
                and (_ts_dt_obj - _gbm_started).total_seconds() > 600):
            log_manager.system(
                f"[GBM-64] 재학습 10분 타임아웃 강제 해제 "
                f"(started={_gbm_started.strftime('%H:%M:%S')}) — subprocess 강제 종료",
                "WARNING",
            )
            _sp = getattr(self, "_retrain_subproc", None)
            if _sp is not None:
                try:
                    _sp.terminate()
                except Exception:
                    pass
                self._retrain_subproc = None
                _rp = getattr(self, "_retrain_subproc_result_path", "")
                if _rp and os.path.exists(_rp):
                    try:
                        os.remove(_rp)
                    except Exception:
                        pass
                self._retrain_subproc_result_path = ""
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
        # 273차: S6(STEP6) PipePerf 병목 딥다이브용 세부 타이머 — 항상 INFO 기록
        _s6_prof = [("t0", time.perf_counter())]
        _entry_horizon = None   # ATR 레짐별 진입 호라이즌 (STEP 6 말미에 확정)
        horizon_proba = self._apply_horizon_calibration(horizon_proba, features=features)
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

        # [268차-P1] FQAdj를 앙상블 호출 전으로 이동 — 앙상블·체크리스트 동일 mc 기준 적용.
        # 기존: 앙상블(mc=0.352) → FQAdj → 체크리스트(mc=0.322) → grade 불일치 진입버그.
        # 수정: FQAdj 먼저 → zone_mc=0.322로 앙상블·체크리스트 모두 동일 기준 사용.
        # [344차] fq(데이터 품질)만으로 완화를 결정하면 "데이터는 깨끗하지만 모델이
        # 요즘 못 맞히는" 날에도 완화되는 방향 오류가 생긴다(7/15 진입0 딥다이브 실측
        # 사례) — 실측 단기 정확도(1m/3m/5m)를 함께 반영해 완화를 동결/강화로 전환한다.
        _fq_score_pre = float(features.get("feature_quality_score", 0.5) or 0.5)
        _mc_floor_pre = getattr(runtime_settings, "MC_ABS_FLOOR", 0.25)
        _mc_ceil_pre  = getattr(runtime_settings, "MC_ABS_CEIL",  0.62)
        _short_acc_pre = self.online_learner.short_horizon_accuracy(
            min_samples=getattr(runtime_settings, "FQADJ_ACC_MIN_SAMPLES", 15)
        )
        _zone_mc_new, _fq_action, _fq_reason = compute_fq_adjusted_min_conf(
            fq_score=_fq_score_pre,
            zone_mc=_zone_mc,
            short_horizon_acc=_short_acc_pre,
            mc_floor=_mc_floor_pre,
            mc_ceil=_mc_ceil_pre,
            acc_freeze_min=getattr(runtime_settings, "FQADJ_ACC_FREEZE_MIN", 0.45),
            acc_strengthen_min=getattr(runtime_settings, "FQADJ_ACC_STRENGTHEN_MIN", 0.40),
        )
        if _fq_action != "none":
            _fq_action_ko = {"relax": "완화", "tighten": "강화", "freeze": "완화 동결"}[_fq_action]
            log_manager.signal(
                f"[FQAdj] {_fq_reason} → min_conf {_zone_mc:.2f}→{_zone_mc_new:.2f} ({_fq_action_ko})"
            )
        _zone_mc = _zone_mc_new

        # [353차] 확신도 고착 임시 부스트(P2-b 옵션 c) 입력값 — 타깃 호라이즌
        # 최근 정확도는 표본 5건 미만이면 None(판단 불가 → ensemble_decision.py가
        # 허용 처리)으로 전달, horizon_accuracy() 자체는 표본 부족 시 0.0을 반환해
        # "정확도 0%"로 오인될 수 있어 여기서 samples 체크로 방어한다.
        _csb_target = getattr(runtime_settings, "CONF_STUCK_BOOST_TARGET", "3m")
        _csb_target_samples = self.online_learner.horizon_acc_samples(_csb_target)
        _csb_target_acc = (
            self.online_learner.horizon_accuracy(_csb_target)
            if _csb_target_samples >= 5 else None
        )
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
            bias_override_horizons=self._bias_override_horizons,
            conf_stuck_streak=dict(self._conf_stuck),
            target_recent_acc=_csb_target_acc,
        )
        _s6_prof.append(("ensemble", time.perf_counter()))
        if decision.get("conf_stuck_boost_applied"):
            log_manager.signal(
                "[ConfStuckBoost] {}→{} 가중치 부스트 적용 (고착 {}분, {} 최근acc={})".format(
                    runtime_settings.CONF_STUCK_BOOST_SOURCE,
                    _csb_target,
                    self._conf_stuck.get(runtime_settings.CONF_STUCK_BOOST_SOURCE, 0),
                    _csb_target,
                    "{:.1%}".format(_csb_target_acc) if _csb_target_acc is not None else "N/A",
                )
            )
        direction  = decision["direction"]
        confidence = decision["confidence"]
        grade      = decision["grade"]
        self._last_ensemble_direction = direction  # Contrarian Mode 동방향 추적용
        # 1분봉 차트 방향예측 바 업데이트 (닫힌 봉에 색상 기록)
        try:
            self.dashboard.minute_chart_set_direction(ts, direction)
        except Exception as _cde:
            logger.debug("[ChartWarn] set_direction_at 예외 무시: %s", _cde)
        # 방향카드 즉시 갱신 — DB 폴링(10s) 지연 없이 매분 확정값 반영
        try:
            self.dashboard.push_direction_live(decision, ts)
        except Exception as _pde:
            logger.debug("[DirPush] push_direction_live 예외 무시: %s", _pde)

        # [MaskedFallback] 격리 예측 채택 — 정상 앙상블이 FLAT이고 격리 예측이 더 높을 때
        if direction == 0 and _masked_hp_blended and self.model.last_masked_features:
            # [313차] features= 인자에 self.model.last_masked_features(마스킹된
            # 피처 "이름" 리스트, 로깅용)를 잘못 넘겨 compute_extremity_hinge()가
            # list.get() 호출로 크래시(09:02:56 실크래시, ERR-FATAL). 실제 피처
            # 값 dict인 지역변수 features를 넘겨야 함(라인 5309 호출부와 동일).
            _mhp_cal  = self._apply_horizon_calibration(
                _masked_hp_blended, features=features
            )
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

        # checklist_reason: 차단사유 DB 저장 — 앙상블 확정 직후 초기값 설정
        if direction == 0:
            decision["checklist_reason"] = "FLAT"
        elif grade == "X":
            decision["checklist_reason"] = "Coherence↓" if decision.get("coherence_blocked") else "conf↓"

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
                    # [진단] PipePerf S0 스파이크와의 상관관계 확인용 — 백그라운드
                    # 스레드의 CPU 집약 구간(로드/fit)이 GIL을 통해 메인 스레드
                    # S0 구간을 지연시키는지 타임스탬프로 직접 대조하기 위함.
                    _refit_ok = False
                    _w_t0 = time.perf_counter()
                    log_manager.system(f"[ConstOut][Worker] 시작 hz={_hz}", "INFO")
                    try:
                        from config.settings import SCALER_WARMUP_LOOKBACK_BARS
                        _w_load0 = time.perf_counter()
                        _Xco, _fnco = self.batch_retrainer.load_features_for_warmup(
                            lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
                        )
                        _w_load_ms = (time.perf_counter() - _w_load0) * 1000
                        if _Xco is not None:
                            _w_fit0 = time.perf_counter()
                            self.model.refit_scalers_only(
                                _Xco, _fnco,
                                trigger_ts=_tts,
                                trigger_type="D_FORCE",
                                trigger_reason=f"const_output={_hz}",
                            )
                            _w_fit_ms = (time.perf_counter() - _w_fit0) * 1000
                            _refit_ok = True
                            log_manager.system(
                                f"[ConstOut][Worker] 완료 hz={_hz} "
                                f"load={_w_load_ms:.0f}ms fit={_w_fit_ms:.0f}ms "
                                f"total={(time.perf_counter()-_w_t0)*1000:.0f}ms",
                                "INFO",
                            )
                    except Exception as _co_e:
                        logger.warning("[ConstOut] 스케일러 재적합 실패: %s", _co_e)
                    finally:
                        self._scaler_refresh_running = False
                    if _refit_ok:
                        # [225차 P1] QTimer 대신 deferred 큐 — daemon thread QTimer 미전달 버그 수정
                        self._deferred_callbacks.put(("const_out_done", _hz))
                threading.Thread(target=_const_out_refit_worker, daemon=True).start()

        # 앙상블 보정기: 현재 ts의 conf 캐시 (STEP 1에서 T-1m conf 조회용)
        # 1m 포함 여부 함께 저장 — 1m OFF 중에는 1m 결과로 앙상블 보정기 학습 불가
        # [238차] raw conf 저장 — calibrated conf를 저장하면 calibrator가 자신의 출력을
        #         입력으로 재학습하는 피드백 루프 발생 → A≈0, 상수 0.21 출력 고착
        self._ensemble_conf_cache[ts] = (
            float(decision.get("confidence_raw", confidence)), "1m" in _hp_ens
        )
        if len(self._ensemble_conf_cache) > 35:
            self._ensemble_conf_cache.pop(min(self._ensemble_conf_cache), None)
        # 시간대·레짐 두 기준 중 더 엄격한 값으로 통일 (checklist·dashboard 공용)
        # _zone_mc는 ensemble.compute() 호출 전 계산됨 (cold-start zone_mc로 전달)
        # [297차] decision["min_conf"]가 이미 zone_mc(FQAdj 반영) 기준이므로(RISK_OFF만
        # REGIME_MIN_CONFIDENCE와 max) 아래 max()는 RISK_OFF 강화만 실질적으로 반영하고
        # RISK_ON/NEUTRAL에서는 zone_mc 그대로 통과한다 — FQAdj 완화가 이제 실제로 적용됨.
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

        # [359차] 레짐 불안정도(휩쏘) 게이트 — 0720 정기점검: MicroRegime 분당 급변 구간에서
        # 1m/3m/5m/10m 예측정확도가 랜덤 이하로 붕괴 확인(predictions.db 실측). 검증 없이
        # 켠 게이트가 FP-CRITICAL·CB③-P4처럼 오발동한 선례가 있어 섀도 모드로 먼저 배선
        # (config/settings.py INSTABILITY_GATE_ENABLED=False 기본 — 로그만, min_conf 불변).
        _instab = getattr(self, "_micro_regime_instability", 0)
        if _instab >= runtime_settings.INSTABILITY_TRANSITION_THRESHOLD:
            if runtime_settings.INSTABILITY_GATE_ENABLED:
                actual_min_conf = min(0.90, actual_min_conf + runtime_settings.INSTABILITY_MC_BOOST)
                log_manager.signal(
                    f"[InstabilityGate] 레짐전환 {_instab}회/{runtime_settings.INSTABILITY_WINDOW_MIN}분 "
                    f"→ min_conf +{runtime_settings.INSTABILITY_MC_BOOST * 100:.0f}%p → {actual_min_conf:.2f}"
                )
            else:
                log_manager.signal(
                    f"[InstabilityGate] (섀도) 레짐전환 {_instab}회/{runtime_settings.INSTABILITY_WINDOW_MIN}분 "
                    f"— 활성 시 min_conf +{runtime_settings.INSTABILITY_MC_BOOST * 100:.0f}%p 예상(미적용)"
                )

        # ── Phase 1: FQAdj — [268차-P1] 앙상블 호출 전으로 이동 완료, 여기서 재적용 불필요 ──
        # zone_mc가 이미 앙상블 호출 전 FQAdj 적용됨 → actual_min_conf도 동일 기준 반영.
        # 이중 적용 시 actual_min_conf가 과도하게 낮아지는 부작용 발생 → 블록 비활성화.

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
                        cvd_direction      = float(features.get("cvd_delta_norm", 0.0) or 0.0),
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
                        ensemble_grade     = grade,
                        hurst              = float(features.get("hurst", 0.5) or 0.5),
                        price_extension_atr = float(features.get("price_extension_atr", 0.0) or 0.0),
                    )
                    _pre_cl_grade = _pre_cr_cache.get("grade", grade)
                except Exception as _pre_cl_e:
                    logger.debug("[Checklist.pre] 선행 평가 실패, 앙상블 등급 사용: %s", _pre_cl_e)
        _s6_prof.append(("checklist_pre", time.perf_counter()))

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
            horizon=getattr(self, "_entry_horizon_pre", "1m") or "1m",  # [260704 P1] entry_quality_prob 섀도우 스코어링
            context="live",  # [316차] STEP6 실거래 게이팅 — skip 로그 SIGNAL.log(INFO)에 유지
        )
        _s6_prof.append(("meta_gate", time.perf_counter()))
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
                decision["checklist_reason"] = "RegimeOverride"
                log_manager.signal(
                    f"[RegimeOverride] 진입 금지 "
                    f"— {self.current_regime}×{self.current_micro_regime}"
                )
        except Exception as _ro_e:
            logger.debug("[RegimeOverride] 적용 실패 (스킵): %s", _ro_e)

        # [§19] RegimeFingerprint CRITICAL — 피처 분포 심각 변화 시 진입 차단
        # [303차] 부활 후 이틀 연속 상시 CRITICAL 고착(계측 결함 의심)으로 차단만
        # 한시 비활성 — config/settings.py FP_CRITICAL_GRADE_BLOCK_ENABLED 주석 참조.
        # PSI 계산·로그는 그대로 유지(모니터링 단절 없음).
        try:
            from strategy.regime_fingerprint import get_fingerprint as _get_fp2
            if _get_fp2().get_level() >= 3:  # DriftLevel.CRITICAL = 3
                if runtime_settings.FP_CRITICAL_GRADE_BLOCK_ENABLED:
                    direction = 0
                    grade     = "X"
                    decision["checklist_reason"] = "FP-CRITICAL"
                    log_manager.signal(
                        f"[RegimeFingerprint] PSI={_get_fp2().get_psi():.3f} CRITICAL "
                        f"— 시장 구조 변화로 진입 차단"
                    )
                else:
                    log_manager.signal(
                        f"[RegimeFingerprint] PSI={_get_fp2().get_psi():.3f} CRITICAL "
                        f"— 감시전용(차단 비활성), 계측만 기록"
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
                    decision["checklist_reason"] = "ChampGate"
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
                decision["checklist_reason"] = "σ미수집"
                log_manager.signal(
                    f"[EntryGate] sigma_20봉 미수집({len(self._sigma_buf)}봉) "
                    f"— 진입 대기 (09:20 해제)"
                )
        elif _now_hm < "0930":
            # 09:20~09:29: grade A만, min_conf 0.60 상향, size×0.5 (STEP 7에서 적용)
            if grade in ("B", "C"):
                direction = 0
                grade     = "X"
                decision["checklist_reason"] = "조건부구간"
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
        _s6_prof.append(("gates", time.perf_counter()))

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
        _s6_prof.append(("dashboard", time.perf_counter()))

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
            decision["checklist_reason"] = "ATR저변동"
        elif direction != 0:
            log_manager.signal(
                f"[ATR-Horizon] 진입 호라이즌={_entry_horizon} tf={_tf:.2f} "
                f"→ TP1×{ATR_HORIZON_TP1_MULT.get(_entry_horizon, 1.0)}"
            )

        # ── Phase 1: 진입0 자동 원인 진단 ───────────────────────
        if direction == 0 or grade == "X":
            self._diagnose_zero_entry(features, horizon_proba, decision)

        _s6_prof.append(("tail", time.perf_counter()))
        # 273차: S6 세부 구간 — PipePerf S6 지배(전체 80%+) 원인 특정용, 매분 INFO 기록
        _s6_detail = " ".join(
            f"{_s6_prof[i][0]}={(_s6_prof[i][1] - _s6_prof[i - 1][1]) * 1000:.0f}ms"
            for i in range(1, len(_s6_prof))
        )
        log_manager.system(f"[S6Detail] {_s6_detail}", "INFO")

        # ── STEP 7: 진입 실행 ──────────────────────────────────
        _st.append(("S7", time.perf_counter()))
        _dir_ko = "상승" if direction > 0 else "하락" if direction < 0 else "관망"
        time_zone = get_time_zone()
        _CHK_MAP = {
            "1_signal":"signal_chk", "2_confidence":"conf_chk",
            "3_vwap":"vwap_chk",    "4_cvd":"cvd_chk",
            "5_ofi":"ofi_chk",      "6_foreign":"fi_chk",
            "7_prev_bar":"candle_chk","8_time":"time_chk",
            "9_risk":"risk_chk",   "10_chase":"chase_chk",
        }

        # 체크리스트: FLAT + 방향 있을 때 항상 평가 (CB·시간 조건 무관)
        # → 대시보드가 조건 차단 시에도 올바른 체크 결과를 표시할 수 있도록
        _final_grade = grade
        _checks_ui   = {}   # 빈 dict → 대시보드에서 "—" 표시
        _qty_display = 0
        _kelly_advised_skip = False  # [311차 후속] 켈리가 목표자본 대비 1계약도 부적절하다고 판단했는지
        _vb_stop_widen_mult = 1.0  # [349차] 급변장 사전 가드가 "reduce" 발동 시에만 >1.0
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
                decision["checklist_reason"] = "Warmup대기"
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
                        cvd_direction     = float(features.get("cvd_delta_norm", 0.0) or 0.0),
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
                        ensemble_grade    = grade,
                        hurst             = float(features.get("hurst", 0.5) or 0.5),
                        price_extension_atr = float(features.get("price_extension_atr", 0.0) or 0.0),
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
                    decision["checklist_reason"] = "coldstart"

            # [268차-P2] ENS_CONF_FLOOR_FOR_AUTO 동적 연동 — actual_min_conf 기반 상향.
            # 기존 고정 floor(0.33)가 앙상블 mc(예: 0.352)보다 낮아 최후 방어선이 허술했음.
            # 동적 floor = max(static_floor, actual_min_conf - 0.01) 으로 mc에 근접 설정.
            # 예: actual_min_conf=0.352 → floor=max(0.33, 0.342)=0.342 → conf 0.331 차단.
            if _cr is not None and _cr.get("auto_entry"):
                _ens_conf_floor_dyn = max(ENS_CONF_FLOOR_FOR_AUTO, actual_min_conf - 0.01)
                if _ens_conf_floor_dyn > ENS_CONF_FLOOR_FOR_AUTO and confidence < _ens_conf_floor_dyn:
                    _cr = dict(_cr)
                    _cr["auto_entry"] = False
                    log_manager.signal(
                        "[P2] conf_floor dynamic=%.1f%% (static=%.1f%%) → auto_entry=OFF "
                        "(conf=%.1f%%)",
                        _ens_conf_floor_dyn * 100, ENS_CONF_FLOOR_FOR_AUTO * 100,
                        confidence * 100,
                    )

            _final_grade = _cr["grade"]

            # [268차-P4] 단기 그룹 CVD+OFI 동시 역방향 → 자동진입 등급 상한 C.
            # 두 CORE 지표가 모두 진입 방향과 반대이면 모멘텀이 완전 역방향으로
            # A/B 등급 자동진입은 EV 음수 가능성이 높음 → C 이하로 강제 하향.
            # 중기(10m·15m)·장기(30m) 그룹은 4·5번 체크가 항상 True(면제)이므로
            # 조건 not(4) AND not(5)가 동시에 False가 되어 이 분기에 진입하지 않음.
            if (_final_grade in ("A", "B")
                    and _cr is not None
                    and not _cr.get("checks", {}).get("4_cvd", True)
                    and not _cr.get("checks", {}).get("5_ofi", True)):
                log_manager.signal(
                    f"[P4] CVD+OFI 동시 역방향 → 등급 {_final_grade}→C 강등 (자동진입 A/B 차단)"
                )
                _final_grade = "C"
                _cr = dict(_cr)
                _cr["grade"]      = "C"
                _cr["size_mult"]  = runtime_settings.ENTRY_GRADE["C"]["size_mult"]
                _cr["auto_entry"] = runtime_settings.ENTRY_GRADE["C"]["auto"]

            # [366차 신설] GradeEVGuard — 등급 A 롤링 실현EV 가드.
            # HCGuard(conf 기반, 261차)와 동일 원칙을 등급 축에 적용 — A등급 순EV가
            # 롤링 관찰창(기본 30일) 동안 임계 미달 + 표본 충분이면 강등.
            # GRADE_EV_GUARD_ENABLED=False(기본)면 섀도 로그만 남기고 등급은 그대로
            # (§9 사전등록 원칙 — INSTABILITY_GATE_ENABLED와 동일한 도입 순서).
            if _final_grade == "A":
                _ge_blocked, _ge_diag = _ts_grade_ev_guard_check(self)
                if _ge_blocked:
                    _ge_demote = getattr(runtime_settings, "GRADE_EV_GUARD_DEMOTE_TO", "B")
                    if getattr(runtime_settings, "GRADE_EV_GUARD_ENABLED", False):
                        log_manager.signal(
                            f"[GradeEVGuard] 등급 A→{_ge_demote} 강등: {_ge_diag}"
                        )
                        _final_grade = _ge_demote
                        _cr = dict(_cr)
                        _cr["grade"]      = _ge_demote
                        _cr["size_mult"]  = runtime_settings.ENTRY_GRADE[_ge_demote]["size_mult"]
                        _cr["auto_entry"] = runtime_settings.ENTRY_GRADE[_ge_demote]["auto"]
                    else:
                        log_manager.signal(
                            f"[GradeEVGuard] (섀도) 등급 A→{_ge_demote} 강등 조건 충족"
                            f"(미적용): {_ge_diag}"
                        )

            # [368차 신설] ChaseForeignComboGuard(섀도) — 10_chase+6_foreign 동시
            # 실패 조합 감시. 0722 정기점검 딥다이브(MW0601): 이 조합(나머지 9개
            # 항목 전부 통과)이 09:32~09:53 21분 사이 3회 발화해 3회 전부 하드스톱
            # (-536,097원, 그날 최대 손실뭉치의 72%) — P4(CVD+OFI)와 동일 계열이나
            # 표본이 작아(n=5, 7/21 포함) 즉시 강제 강등이 아니라 섀도 로그만
            # (§9 사전등록 원칙). 검증캠페인 [16] chase_foreign_combo_watch로
            # 표본 축적 후 CHASE_FOREIGN_COMBO_GUARD_ENABLED 수동 전환 검토.
            if (_final_grade in ("A", "B")
                    and _cr is not None
                    and not _cr.get("checks", {}).get("10_chase", True)
                    and not _cr.get("checks", {}).get("6_foreign", True)):
                _cfc_demote = getattr(runtime_settings, "CHASE_FOREIGN_COMBO_DEMOTE_TO", "C")
                if getattr(runtime_settings, "CHASE_FOREIGN_COMBO_GUARD_ENABLED", False):
                    log_manager.signal(
                        f"[ChaseForeignComboGuard] chase+foreign 동시 실패 → "
                        f"등급 {_final_grade}→{_cfc_demote} 강등"
                    )
                    _final_grade = _cfc_demote
                    _cr = dict(_cr)
                    _cr["grade"]      = _cfc_demote
                    _cr["size_mult"]  = runtime_settings.ENTRY_GRADE[_cfc_demote]["size_mult"]
                    _cr["auto_entry"] = runtime_settings.ENTRY_GRADE[_cfc_demote]["auto"]
                else:
                    log_manager.signal(
                        f"[ChaseForeignComboGuard] (섀도) chase+foreign 동시 실패, "
                        f"등급={_final_grade} → {_cfc_demote} 강등 후보 (미적용)"
                    )

            _checks_ui   = {_CHK_MAP.get(k, k): v for k, v in _cr["checks"].items()}
            # checklist_reason: STEP7 체크리스트 X 원인 기록 (stage 8 차단사유 표시)
            if _final_grade == "X" and _cr.get("checks"):
                if not _cr["checks"].get("3_vwap", True):
                    decision["checklist_reason"] = "VWAP강제X"
                else:
                    decision["checklist_reason"] = "pass %d/9" % _cr.get("pass_count", 0)
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
                # [297차] 30m 퇴역(296차) 이후 CB_ACC_RESTRICTED_MIN(0.30)이 30m의
                # 확정된 구조적 성능(0.3052)과 거의 같아 상시 RESTRICTED로 붙박여
                # 무관한 정상 호라이즌의 C등급까지 차단하는 부작용 확인 → 설정 플래그로
                # 차단만 비활성(모니터링은 유지). config/settings.py 주석 참조.
                if (runtime_settings.CB3_P4_GRADE_BLOCK_ENABLED
                        and _final_grade == "C" and self.circuit_breaker.is_grade_restricted()):
                    log_manager.signal(
                        f"[CB③-P4] RESTRICTED(acc30m<{int(0.30*100)}%) — C등급 차단"
                        f" (acc30m={self.circuit_breaker.status_dict()['accuracy_30m']:.1%})"
                    )
                    _final_grade = "X"

                # [285차-P5] 앙상블 CoherenceGate 차단 + 체크리스트 C등급 동시 발생 → 차단.
                # 근거: 5/8~7/3 백테스트 — 앙상블 X(Coherence↓)와 체크리스트가 동시에
                # 발생한 케이스 중 A/B등급은 14건 13승1패(+378만원, 승률92.9%)로 견조했으나
                # C등급은 유일 표본(07-03 11:45, SHORT)이 손실(-26만원)이었음. 두 독립 게이트
                # (앙상블 호라이즌 합의도·체크리스트 CVD+OFI 역행)가 동시에 신호를 의심할 때만
                # 차단 — A/B등급 자동진입은 이 조건과 무관하게 그대로 허용.
                if _final_grade == "C" and decision.get("coherence_blocked"):
                    log_manager.signal(
                        "[P5] CoherenceGate+체크리스트C 동시발생 — C등급 차단 "
                        f"(conf={confidence:.1%})"
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
                    max_qty_override    = _cr.get("max_qty_override"),
                )
                _qty_display = size_result["quantity"]
                _qty_sizer_raw = _qty_display  # 게이트 조정 전 Sizer 원본값 보존
                _kelly_advised_skip = bool(size_result.get("kelly_advised_skip", False))

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
            # [P3] HORIZON_TIME_POLICY=[] 설계적 차단(cold-start) vs 파이프라인 지연 구분
            _gap_horizon_blocked = bool(decision.get("active_horizons_blocked", False))
            self.system_health.record_gap_open_bar(
                conf=confidence,
                core_all_passed=_core_all_ok,
                pipeline_delayed=_gap_pipe_delayed,
                horizon_policy_blocked=_gap_horizon_blocked,
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
                    "[SHS-EKS] Early Kill Switch 발동 — 일시 관망 "
                    f"conf_max={_shs_d['gap_open_conf_max']*100:.1f}% bars={_shs_d['gap_open_bars']} "
                    "→ 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가)",
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
                _p3_z_warn     = getattr(self.model, "last_z_warn_count", 0)
                _p3_window     = list(self._eks_recovery_conf_window)
                _p3_conf_hits = sum(1 for c in _p3_window if c >= actual_min_conf)
                if self.system_health.try_eks_recovery(
                    _p3_scaler_age, _p3_window, actual_min_conf, _p3_z_warn
                ):
                    log_manager.system(
                        f"[SHS-EKS] EKS 자동 해제 확정 — 장중 진입 재개 "
                        f"scaler_age={_p3_scaler_age:.1f}h "
                        f"conf_window={[f'{c:.0%}' for c in _p3_window[-3:]]}",
                        "WARNING",
                    )
                    from utils.notify import notify_kill_switch_cleared as _nksc
                    _nksc(
                        scaler_age_h=_p3_scaler_age,
                        conf_hits=_p3_conf_hits,
                        conf_window=len(_p3_window),
                    )
                    # [232차] EKS 해제 직후 GBM 재학습 — 관망 중 누락된 당일 데이터 반영.
                    # 장전 기동 + EOD 성공 스킵 조합으로 WarmupRetrain이 실행되지 않은 경우
                    # EKS 해제 후 첫 진입까지 전날 EOD 모델이 그대로 사용되는 공백을 메움.
                    # _start_gbm_retrain_subprocess 내부에서 중복 실행 차단(_gbm_retrain_running).
                    if not getattr(self, "_gbm_retrain_running", False):
                        self.dashboard.set_model_status("GBM 재학습중(EKS해제)...")
                        log_manager.system(
                            "[SHS-EKS] EKS 해제 → GBM 경량 재학습 시작 (관망 구간 데이터 반영)",
                            "INFO",
                        )
                        self._start_gbm_retrain_subprocess(
                            force=False,
                            reason="EKS 해제 후 즉시 재학습",
                            is_warmup=False,
                            intraday=True,
                        )

        # EKS 활성 시 매분 진입 차단 로그 (방향 있을 때만)
        if self.system_health.kill_switch_active and direction != 0:
            log_manager.signal("[SHS-EKS] EKS 활성 — 자동진입 차단 (conf 회복 대기)")

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
                # DynMC zone_mc(actual_min_conf)를 기준으로 동적 계산.
                # 고정값 0.62는 현 Platt-보정 conf 분포(32~42%)에서 상시 차단.
                # Degraded 상태의 보호는 size_mult 축소로 충분 — 진입 기준은 zone_mc 동일 적용.
                _dg_mc = max(actual_min_conf, 0.30)   # 절대 하한 0.30 (극단 상황 방어)
                if confidence < _dg_mc:
                    _final_grade = "X"
                    _qty_display = 0
                    log_manager.signal(
                        f"[HealthPolicy] Degraded Mode 차단: conf={confidence:.1%} < {_dg_mc:.1%} (zone_mc 기준)"
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

            # ── [349차] 급변장 사전 가드 — 분당 틱수·1분 변화폭(atr_ratio) 동시 초과 ──
            # 기존 RegimeOverride(§14, config/strategy_params.py)는 MicroRegimeClassifier가
            # "완결된 봉"의 ATR비/ADX로만 판정해 급변이 막 시작되는 봉 자체(예: 7/16
            # 14:10:01 진입 — 급변 직전)는 걸러내지 못한다. 이 게이트는 방금 완결된
            # 봉의 tick_count(주문흐름 폭주, collection/cybos/realtime_data.py:_update_bar
            # 누적)와 atr_ratio(features/technical/atr.py, "1분 변화폭")를 함께 봐서
            # RegimeOverride보다 더 이른 신호로 판단한다. 두 조건 모두 초과해야 발동
            # (오탐 최소화 — 개장 직후처럼 틱수만 자연히 높은 정상 구간 배제).
            if runtime_settings.VOLATILITY_BURST_GUARD_ENABLED and _qty_display > 0:
                _vb_tick = int(bar.get("tick_count", 0) or 0)
                _vb_atr_ratio = float(features.get("atr_ratio", 1.0) or 1.0)
                if (_vb_tick >= runtime_settings.VOLATILITY_BURST_TICK_RATE_MIN
                        and _vb_atr_ratio >= runtime_settings.VOLATILITY_BURST_ATR_RATIO_MIN):
                    if runtime_settings.VOLATILITY_BURST_ACTION == "skip":
                        _final_grade = "X"
                        _qty_display = 0
                        log_manager.signal(
                            f"[VolatilityBurst] 신규 진입 차단 — tick={_vb_tick}"
                            f"(임계{runtime_settings.VOLATILITY_BURST_TICK_RATE_MIN}) "
                            f"atr_ratio={_vb_atr_ratio:.2f}"
                            f"(임계{runtime_settings.VOLATILITY_BURST_ATR_RATIO_MIN})"
                        )
                    else:
                        _vb_stop_widen_mult = float(runtime_settings.VOLATILITY_BURST_STOP_WIDEN_MULT)
                        _qty_display = max(
                            1, int(round(_qty_display * runtime_settings.VOLATILITY_BURST_SIZE_MULT))
                        )
                        log_manager.signal(
                            f"[VolatilityBurst] 사이즈 축소 ×{runtime_settings.VOLATILITY_BURST_SIZE_MULT:.2f} "
                            f"+ 스톱 확대 ×{_vb_stop_widen_mult:.2f} — tick={_vb_tick} "
                            f"atr_ratio={_vb_atr_ratio:.2f}"
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

        # [313차 후속] FATAL 정책이 끈 자동진입 — 15분 경과 시 자동 복구.
        # 수동 토글 재조작이나 프로세스 재시작 없이는 당일 내내 MANUAL_CONFIRM에
        # 묶이던 문제(2026-07-13 09:02:56 실사고) 재발 방지.
        if (
            not self._auto_entry_enabled
            and self._auto_entry_disabled_until is not None
            and datetime.datetime.now() >= self._auto_entry_disabled_until
        ):
            self._auto_entry_enabled = True
            self._auto_entry_disabled_until = None
            log_manager.system(
                "[EntryConfig] FATAL 자동진입OFF 15분 쿨다운 경과 → 자동 복구(ON)",
                "WARNING",
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
        # 273차: Hurst<0.45(횡보) 게이트는 TREND_FOLLOW 전용 안전장치다.
        # MEAN_REVERSION 모드는 원래 이 레짐(횡보/평균회귀)에서 쓰라고 만든 대응 전략이므로
        # 같은 게이트로 함께 막으면 안 된다 — 그동안 Hurst<0.45 구간이 통째로 무전략
        # 관망이 되어온 원인.
        # [hurst 점검] REGIME_EXHAUSTION_PARAMS.hurst_override=True 의도대로, 탈진 레짐도
        # MEAN_REVERSION과 동일하게 Hurst 차단을 무효화한다 (기존에는 정의만 되고 미소비).
        _entry_mode_for_gate = (_cr or {}).get("entry_mode", "TREND_FOLLOW")
        _hurst_ok = (
            _entry_mode_for_gate == "MEAN_REVERSION"
            or self.current_micro_regime == REGIME_EXHAUSTION
            or features.get("hurst", 0.5) >= HURST_RANGE_THRESHOLD
        )

        # [333차 후속, §3-6 FAIL 완화] hurst_gate_shadow counterfactual n=111, 누적
        # hyp_pnl=42.49pt(>왕복비용×2), 승률73.9%(>기준선62.5%) — 하드차단 대신 사이징
        # ×0.5로 완화(즉시 언블록 아님, 사전등록 원칙). 손절/TP1은 _entry_hurst_bucket이
        # 그대로 raw hurst 기준으로 "mean-revert" 버킷을 매겨 HURST_REGIME_ATR_MULT가
        # counterfactual 계측과 동일한 조건으로 자동 적용된다(코드 변경 불필요).
        _hurst_size = 1.0
        if (HURST_SOFT_BLOCK_ENABLED and not _hurst_ok
                and direction != 0 and self.position.status == "FLAT" and _qty_display > 0):
            _hurst_size = HURST_SOFT_BLOCK_SIZE_MULT
            _qty_display = max(1, int(round(_qty_display * _hurst_size)))
            log_manager.signal(
                f"[HurstGate] 하드차단 대신 사이즈축소: hurst={features.get('hurst', 0.5):.3f} "
                f"< {HURST_RANGE_THRESHOLD} size_mult={_hurst_size:.2f} (§3-6 FAIL 완화, 333차 후속)"
            )

        # 273차: 정적 3.5pt 상한이 최근 장기간 시장 ATR 중앙값(3.5~6pt대)에 만성적으로
        # 걸려 정상 변동성에서도 A등급 신호를 연속 차단하는 문제 확인 → 최근 60분 ATR
        # 롤링평균 × 배수로 상한을 적응시키되, 절대 상한(ceiling)과 정적 하한(ATR_MAX_ENTRY)
        # 사이로 클램프해 순간 스파이크·표본 부족 구간의 과도한 완화는 막는다.
        # 303차: 옵션/선물 만기 전후는 롤오버·프로그램매매로 ATR이 구조적으로 튀는 캘린더
        # 이벤트(07-08 만기 전날 딥다이브, 실측 피크 10.22pt). 장기 롤링 캡은 변동성
        # "상승 초입"에 과거 낮은 레벨에 발목 잡혀 오히려 차단율이 커지는 역효과가
        # 시뮬레이션으로 확인됐으므로, 원인이 뚜렷한 만기는 롤링 대신 캘린더 예외로
        # 절대 상한 자체를 일시 확대한다(평소 상한 × ATR_EXPIRY_CEILING_MULT).
        _atr_ceiling_effective = ATR_ADAPTIVE_MAX_CEILING
        if ATR_EXPIRY_CEILING_ENABLED and is_near_monthly_expiry(
            _now_dt, ATR_EXPIRY_CEILING_DAYS_BEFORE, ATR_EXPIRY_CEILING_DAYS_AFTER
        ):
            _atr_ceiling_effective = ATR_ADAPTIVE_MAX_CEILING * ATR_EXPIRY_CEILING_MULT
        if len(self._atr_recent_window) >= ATR_ADAPTIVE_MIN_SAMPLES:
            _atr_recent_avg = sum(self._atr_recent_window) / len(self._atr_recent_window)
            _atr_max_adaptive = min(
                _atr_ceiling_effective,
                max(ATR_MAX_ENTRY, _atr_recent_avg * ATR_ADAPTIVE_MAX_MULT),
            )
        else:
            _atr_recent_avg = None
            _atr_max_adaptive = ATR_MAX_ENTRY
        _atr_ok = ATR_MIN_ENTRY <= atr <= _atr_max_adaptive  # 하한: 휩쏘, 상한: 과도 손절거리(적응형)

        # ── [A] OPEN_VOLATILE 시가 이격 필터 ─────────────────────────────────
        # 장 초반 TREND_FOLLOW 진입 시 이미 시가 대비 ATR × N배 이상 이탈했으면
        # 낙폭/상승폭 소진으로 반전 위험이 높아 차단한다.
        _open_p_for_gap   = getattr(self, "_session_open_price", 0.0) or 0.0
        _cr_entry_mode    = (_cr.get("entry_mode") if _cr else "") or ""
        if (_open_p_for_gap > 0 and atr > 0
                and time_zone == "OPEN_VOLATILE"
                and _cr_entry_mode == "TREND_FOLLOW"):
            _gap_in_dir = (
                (_open_p_for_gap - close) if direction < 0
                else (close - _open_p_for_gap)
            )
            _open_gap_ok = _gap_in_dir <= atr * ATR_OPEN_GAP_MULT
        else:
            _gap_in_dir  = 0.0
            _open_gap_ok = True
        _hp = self._health_policy
        # Degraded 선제차단용 현재 사이클 지표 (1-사이클 지연 버그 수정)
        # _last_pipe_ms: 직전 사이클 지연 (현재 사이클 _pipe_ms는 STEP9 이후 확정)
        _dg_latency_ms  = float(getattr(self, "_last_pipe_ms", 0.0) or 0.0)
        _dg_quality     = float(features.get("feature_quality_score", 1.0) or 1.0)
        _dg_cache_age   = float(features.get("quality_investor_age_sec", 0.0) or 0.0)
        _dg_level_counts = log_manager.get_level_counts(
            since_sec=600,
            layer="SYSTEM",
            exclude_prefixes=_hp.get("exception_exclude_tags", HEALTH_EXCEPTION_EXCLUDE_TAGS),
        )
        _dg_exc_density = float(
            _dg_level_counts.get("WARNING", 0)
            + _dg_level_counts.get("ERROR", 0)
            + _dg_level_counts.get("CRITICAL", 0)
        )
        _auto_blocked, _deg_min_conf = self._is_degraded_entry_blocked(
            confidence, is_manual=False,
            latency_ms=_dg_latency_ms,
            quality_score=_dg_quality,
            cache_age_sec=_dg_cache_age,
            exception_density_10m=_dg_exc_density,
        )
        _qty_auto = _qty_display
        if self._health_degraded_mode and _qty_auto > 0:
            _qty_auto = max(1, int(round(_qty_auto * float(_hp.get("degraded_size_mult", HEALTH_DEGRADED_SIZE_MULT)))))

        # [재발방지] 최대허용수량을 만족해도 증거금이 부족하면 브로커가 주문을 거부한다
        # (2026-07-03 10:28:59 LONG 3계약 ret=-1 사례). 실제 진입 실행과 패널의
        # "진입 수량" 표시가 동일한 최종수량을 쓰도록 여기 한 곳에서만 캡핑한다.
        # _qty_display(산출 수량, raw)는 그대로 두고 _qty_auto만 캡핑해 두 카드의
        # "산출 수량 vs 진입 수량" 구분을 유지한다.
        if _qty_auto > 0 and self._max_entry_qty > 0:
            _qty_auto = max(1, min(_qty_auto, self._max_entry_qty))
        # 증거금 조회는 CYBOS COM BlockRequest 1회를 추가로 소모하므로, grade=X(가장
        # 흔한 무신호 상태)나 conf_floor 미달로 auto_entry가 이미 꺼진 사이클은 걸러
        # 매분 무조건 호출을 피한다. entry_mode(auto/hybrid/manual)는 이 시점에
        # 아직 확정 전이라 A/B/C 모두 대상에 포함 — 수동확인 케이스도 정확한
        # 증거금 반영 수량을 볼 수 있어야 하므로 보수적으로 넓게 잡는다.
        _margin_check_eligible = bool(_cr) and bool(_cr.get("auto_entry")) and _final_grade != "X"
        if _qty_auto > 0 and _margin_check_eligible:
            _margin_dir = "LONG" if direction > 0 else ("SHORT" if direction < 0 else "")
            if _margin_dir:
                _qty_auto = _ts_margin_capped_qty(self, _margin_dir, close, _qty_auto)

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
        # grade X 시 size_mult=0.0을 ProfitGuard에 전달하면 Tier0(min_mult=0.6)이
        # 불필요하게 발동해 중복 차단 로그가 쌓임 (ZeroDiag→grade X→size_mult=0 경로).
        # Tier4(daily_pnl>=400만 완전중단) 감지는 size_mult=1.0으로도 작동하므로 대체.
        _size_mult_for_pg = 1.0 if _final_grade == "X" else (_cr["size_mult"] if _cr else 1.0)
        _pg_allowed, _pg_reason = self.profit_guard.is_entry_allowed(
            _daily_pnl_now, _size_mult_for_pg
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
        # 거래소 CB 해제 후 관망 기간 — 극단 변동성 구간 신규 진입 차단
        _ecb_obs = getattr(self, "_ecb_observation_until", None)
        if _ecb_obs and datetime.datetime.now() >= _ecb_obs:
            self._ecb_observation_until = None
            _ecb_obs = None
            # 관망 기간 만료 → 배지 정상 리셋
            try:
                self.dashboard.update_exchange_cb_badge("NORMAL")
            except Exception:
                pass
        elif _ecb_obs is not None:
            # 관망 중 — 매분 남은 시간 갱신
            try:
                self.dashboard.update_exchange_cb_badge("OBSERVING", until_dt=_ecb_obs)
            except Exception:
                pass
        _ecb_observation_ok = _ecb_obs is None
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
            and (_hurst_ok or HURST_SOFT_BLOCK_ENABLED)  # 333차: 하드차단→사이징 완화
            and _atr_ok
            and _open_gap_ok
            and mode_filter_passed
            and _qty_display > 0
            and not _bar_volume_zero
            and not _intraday_block
            and not self.system_health.kill_switch_active   # [SHS-EKS] 당일 관망일
            and _ecb_observation_ok                         # 거래소 CB 해제 후 관망 기간
        )

        # [297차, P1-4] Hurst 게이트 counterfactual 섀도우 — "Hurst만 아니었으면
        # 진입했을" 분봉의 가상 결과를 기록한다(검증 캠페인 §3-6). Hurst를 제외한
        # 나머지 게이트가 전부 통과했고 등급도 X가 아닌 경우만 대상 — 다른 이유로
        # 이미 죽은 신호를 섞지 않는다. 읽기 전용 계측 — 실거래 의사결정에 관여하지
        # 않음(scripts/generate_validation_campaign_report.py가 주간 사후 판정).
        if (direction != 0
                and self.position.status == "FLAT"
                and not _hurst_ok
                and _final_grade != "X"):
            _hgs_no_hurst_ok = (
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
                and _atr_ok
                and _open_gap_ok
                and mode_filter_passed
                and _qty_display > 0
                and not _bar_volume_zero
                and not _intraday_block
                and not self.system_health.kill_switch_active
                and _ecb_observation_ok
            )
            if _hgs_no_hurst_ok:
                try:
                    # HURST_REGIME_ATR_MULT["mean-revert"] — hurst<0.45일 때만
                    # 이 블록에 도달하므로 버킷은 항상 mean-revert 고정.
                    _hgs_mult = (
                        HURST_REGIME_ATR_MULT.get("mean-revert", {})
                        if HURST_REGIME_ATR_MULT_ENABLED else {}
                    )
                    _hgs_stop_mult = ATR_STOP_MULT * _hgs_mult.get("stop", 1.0)
                    _hgs_tp1_mult = (
                        ATR_HORIZON_TP1_MULT.get(_entry_horizon, ATR_TP1_MULT)
                        * _hgs_mult.get("tp1", 1.0)
                    )
                    _hgs_dir_mult = 1 if direction == 1 else -1
                    execute(
                        TRADES_DB,
                        """INSERT INTO hurst_gate_shadow
                           (ts, direction, grade, hurst, conf,
                            entry_price, stop_price, tp1_price)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                            "LONG" if direction == 1 else "SHORT",
                            _final_grade,
                            float(features.get("hurst", 0.5) or 0.5),
                            float(confidence),
                            float(close),
                            float(close - _hgs_dir_mult * atr * _hgs_stop_mult),
                            float(close + _hgs_dir_mult * atr * _hgs_tp1_mult),
                        ),
                    )
                except Exception as _hgs_e:
                    logger.warning("[HurstShadow] counterfactual 기록 실패 (무해): %s", _hgs_e)

        # [354차] OPEN_VOLATILE 시가이격 필터 counterfactual 섀도우 — "gap 필터만
        # 아니었으면 진입했을" 분봉의 가상 결과를 기록한다(검증 캠페인 [9], §14).
        # Hurst 섀도우와 동일 패턴 — gap을 제외한 나머지 게이트가 전부 통과했고
        # 등급도 X가 아닌 경우만 대상. 읽기 전용 계측 — 실거래 의사결정에 관여하지
        # 않음(scripts/generate_validation_campaign_report.py가 주간 사후 판정).
        if (direction != 0
                and self.position.status == "FLAT"
                and not _open_gap_ok
                and _final_grade != "X"):
            _ogs_no_gap_ok = (
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
                and _atr_ok
                and _hurst_ok
                and mode_filter_passed
                and _qty_display > 0
                and not _bar_volume_zero
                and not _intraday_block
                and not self.system_health.kill_switch_active
                and _ecb_observation_ok
            )
            if _ogs_no_gap_ok:
                try:
                    # 실제 체결이었다면 사용됐을 hurst_bucket 배수 그대로 사용
                    # (Hurst 섀도우와 달리 여기선 hurst가 정상 통과했으므로 버킷이
                    # trend/neutral/mean-revert 어느 쪽이든 될 수 있음).
                    _ogs_mult = (
                        HURST_REGIME_ATR_MULT.get(self._entry_hurst_bucket, {})
                        if HURST_REGIME_ATR_MULT_ENABLED and self._entry_hurst_bucket else {}
                    )
                    _ogs_stop_mult = ATR_STOP_MULT * _ogs_mult.get("stop", 1.0)
                    _ogs_tp1_mult = (
                        ATR_HORIZON_TP1_MULT.get(_entry_horizon, ATR_TP1_MULT)
                        * _ogs_mult.get("tp1", 1.0)
                    )
                    _ogs_dir_mult = 1 if direction == 1 else -1
                    execute(
                        TRADES_DB,
                        """INSERT INTO open_gap_shadow
                           (ts, direction, grade, gap_pt, atr_at_block, conf,
                            entry_price, stop_price, tp1_price)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                            "LONG" if direction == 1 else "SHORT",
                            _final_grade,
                            float(_gap_in_dir),
                            float(atr),
                            float(confidence),
                            float(close),
                            float(close - _ogs_dir_mult * atr * _ogs_stop_mult),
                            float(close + _ogs_dir_mult * atr * _ogs_tp1_mult),
                        ),
                    )
                except Exception as _ogs_e:
                    logger.warning("[OpenGapShadow] counterfactual 기록 실패 (무해): %s", _ogs_e)

        # [379차 신설] RegimeExhaustionGate(섀도) — hurst<0.45(평균회귀) + 60분 느린
        # 연장폭(price_extension_atr_60m) 임계 초과 + 10_chase/11_countertrend 소프트
        # 실패 동시성립 시 "탈진 반전 위험" counterfactual 기록. hurst_gate_shadow·
        # open_gap_shadow와 달리 "특정 게이트 하나를 무시했다면"이 아니라 "이 복합
        # 경고 신호 자체가 유효한가"를 묻는 것이라, 별도의 "무시 가정" 조건 없이
        # 신호 발동 시점 자체를 그대로 기록한다(chase_foreign_combo_watch와 같은
        # "발동=기록" 철학, 다만 이쪽은 direct DB 기록이라 로그 재파싱이 불필요).
        # 검증캠페인 [18] regime_exhaustion_watch — §9 사전등록 원칙, 하드 차단 아님.
        # 읽기 전용 계측 — 실거래 의사결정에 관여하지 않음.
        _reg_ext_60m = float(features.get("price_extension_atr_60m", 0.0) or 0.0)
        _reg_hurst_now = float(features.get("hurst", 0.5) or 0.5)
        _reg_is_chasing_60m = (_reg_ext_60m > 0) == (direction == 1)
        _reg_chase_failed = not _cr.get("checks", {}).get("10_chase", True) if _cr else False
        _reg_ctr_failed = not _cr.get("checks", {}).get("11_countertrend", True) if _cr else False
        _reg_exhaustion_cond = (
            direction != 0
            and self.position.status == "FLAT"
            and _final_grade != "X"
            and _cr is not None
            and _reg_hurst_now < HURST_RANGE_THRESHOLD
            and _reg_is_chasing_60m
            and abs(_reg_ext_60m) > REGIME_EXHAUSTION_EXT_ATR_THRESHOLD
            and (_reg_chase_failed or _reg_ctr_failed)
        )
        if _reg_exhaustion_cond:
            try:
                # hurst<0.45 조건이 이미 보장하므로 버킷은 항상 mean-revert 고정
                # (hurst_gate_shadow와 동일 근거).
                _res_mult = (
                    HURST_REGIME_ATR_MULT.get("mean-revert", {})
                    if HURST_REGIME_ATR_MULT_ENABLED else {}
                )
                _res_stop_mult = ATR_STOP_MULT * _res_mult.get("stop", 1.0)
                _res_tp1_mult = (
                    ATR_HORIZON_TP1_MULT.get(_entry_horizon, ATR_TP1_MULT)
                    * _res_mult.get("tp1", 1.0)
                )
                _res_dir_mult = 1 if direction == 1 else -1
                execute(
                    TRADES_DB,
                    """INSERT INTO regime_exhaustion_shadow
                       (ts, direction, grade, hurst, ext_atr_60m, chase_failed,
                        countertrend_failed, conf, entry_price, stop_price, tp1_price)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                        "LONG" if direction == 1 else "SHORT",
                        _final_grade,
                        _reg_hurst_now,
                        _reg_ext_60m,
                        int(_reg_chase_failed),
                        int(_reg_ctr_failed),
                        float(confidence),
                        float(close),
                        float(close - _res_dir_mult * atr * _res_stop_mult),
                        float(close + _res_dir_mult * atr * _res_tp1_mult),
                    ),
                )
                log_manager.signal(
                    f"[RegimeExhaustionGate] (섀도) 탈진 반전 위험 감지 — "
                    f"hurst={_reg_hurst_now:.3f} ext60m={_reg_ext_60m:+.2f}ATR "
                    f"chase={'X' if _reg_chase_failed else 'O'} "
                    f"countertrend={'X' if _reg_ctr_failed else 'O'} (계측만, 미적용)"
                )
            except Exception as _res_e:
                logger.warning("[RegimeExhaustionGate] counterfactual 기록 실패 (무해): %s", _res_e)

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
            "open_gap_ok":      _open_gap_ok,
            "mode_filter_ok":   mode_filter_passed,
            "qty_ok":           _qty_display > 0,
            "bar_volume_ok":    not _bar_volume_zero,
            "intraday_ok":      not _intraday_block,
            "kill_switch_ok":   not self.system_health.kill_switch_active,
            "ecb_observe_ok":   _ecb_observation_ok,
        }

        _entry_block_reason = ""
        if direction != 0 and self.position.status == "FLAT":
            _cb_state = self.circuit_breaker.state
            if not _ecb_observation_ok:
                _obs_remain = int((self._ecb_observation_until - datetime.datetime.now()).total_seconds() / 60) + 1
                _entry_block_reason = (
                    f"[차단] 거래소 CB 해제 후 관망 중 — 약 {_obs_remain}분 후 진입 재개 "
                    f"({self._ecb_observation_until.strftime('%H:%M')} 해제)"
                )
            elif _cb_state != "NORMAL":
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
            elif not _hurst_ok and not HURST_SOFT_BLOCK_ENABLED:
                _hurst_val = features.get("hurst", 0.5)
                _entry_block_reason = f"[차단] Hurst {_hurst_val:.3f} < {HURST_RANGE_THRESHOLD} — 횡보 레짐 진입 차단"
            elif not _atr_ok:
                if atr < ATR_MIN_ENTRY:
                    _entry_block_reason = f"[차단] ATR {atr:.2f}pt < {ATR_MIN_ENTRY}pt — 변동성 부족 (휩쏘 위험)"
                else:
                    _expiry_tag = "만기캡 " if _atr_ceiling_effective > ATR_ADAPTIVE_MAX_CEILING else ""
                    _entry_block_reason = (
                        f"[차단] ATR {atr:.2f}pt > {_atr_max_adaptive:.2f}pt({_expiry_tag}적응형, 정적={ATR_MAX_ENTRY}) — "
                        f"손절거리 {atr * ATR_STOP_MULT:.1f}pt 과대 (고변동성 진입 차단)"
                    )
            elif not _open_gap_ok:
                _entry_block_reason = (
                    f"[차단] OPEN_VOLATILE 시가이격 과다 — "
                    f"방향이탈 {_gap_in_dir:.1f}pt > ATR×{ATR_OPEN_GAP_MULT}={atr * ATR_OPEN_GAP_MULT:.1f}pt "
                    f"(시가={_open_p_for_gap:.2f} 반등위험)"
                )
            elif not is_new_entry_allowed():
                _entry_block_reason = (
                    f"[차단] {NEW_ENTRY_CUTOFF.strftime('%H:%M')} 이후 — 신규 진입 금지 구간 (345차)"
                )
            elif _auto_blocked:
                _entry_block_reason = f"[차단] 자동진입 Degraded 최소신뢰도 {_deg_min_conf:.1%} 미달"
            elif not mode_filter_passed and _final_grade != "X":
                # allowed_grades는 A/B/C만 포함 — grade=="X"는 모드 설정과 무관하게
                # 항상 mode_filter_passed=False가 되어 진짜 사유(등급X/체크리스트
                # 미통과)를 가리는 오분류가 났었다. X는 아래 등급X 분기로 넘긴다.
                _entry_block_reason = (
                    f"[차단] 모드필터 — {_final_grade}급 신호 vs {entry_mode} 모드"
                    f"({allowed_grades.get(entry_mode, ['A','B','C'])} 만 허용)"
                )
            elif _qty_display <= 0:
                _entry_block_reason = "[차단] 사이저 산출 수량 0 — 리스크 한도/신뢰도 기준 미달"
            elif _bar_volume_zero:
                _entry_block_reason = "[차단] 거래량 0봉 — Guard-C3 진입 차단"
            elif self.system_health.kill_switch_active:
                _entry_block_reason = (
                    f"[차단] SHS-EKS 당일 관망 활성 — {getattr(self.system_health, '_eks_reason', '')}"
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
            elif not self._auto_entry_enabled:
                # [347차] 자동진입 전역 비활성 — grade는 A/B/C로 정상 산출됐지만
                # 사용자가 자동매매 토글을 꺼둔 상태. _final_entry_ok(fo)는 이 토글과
                # 무관하게 True일 수 있어(STEP7 게이트 자체는 통과) 기존 elif 체인
                # 어디에도 안 걸리고 else로 빠지며 "fo=0인데 사유 미매칭"으로 오탐 처리됐다.
                _entry_block_reason = "[차단] 자동진입 비활성화 — 사용자 설정으로 자동매매 꺼짐 (수동 진입만 가능)"
            elif not _cr.get("auto_entry", True):
                # [347차] 체크리스트 conf_floor(ENS_CONF_FLOOR_FOR_AUTO, 동적 상향 포함)
                # 미달 — grade는 A/B/C 그대로 유지한 채 auto_entry만 False로 꺼진 케이스
                # (checklist.py 말미 및 main.py:6088 동적 floor 두 경로 모두 해당).
                # 7/15 14시대 빈 사유 8건 전부 conf 32.9~35.3%로 floor(33%) 바로 위/아래
                # 경계에 몰려 있었음 — 딱 이 케이스.
                _entry_block_reason = (
                    f"[차단] 자동진입 conf_floor 미달 — conf={confidence:.1%} "
                    f"(기준≈{ENS_CONF_FLOOR_FOR_AUTO:.1%}, 동적 상향 가능) "
                    f"— 등급={_final_grade} 유지, 수동확인 필요"
                )
            else:
                # 위 모든 차단 조건을 통과했다는 뜻 — 즉 fo=1이고 진입이 정상 진행되는
                # 케이스다(경고 대상 아님). 336차가 "상세 미수집"을 보강하며 넣었던
                # 이 자리의 경고가 진입 성공 분마다 오탐으로 찍히던 문제 수정.
                _entry_block_reason = ""

        _entry_executed_this_cycle = False

        _prev_bar_dir = (1 if bar.get("close", 0) > bar.get("open", 0)
                         else (-1 if bar.get("close", 0) < bar.get("open", 0) else 0))
        _dl_pct = (max(-self.position.daily_stats()["pnl_krw"], 0)
                   / max(_ts_current_sizer_balance(self), 50_000_000))
        _atr_state = (
            "↑고변동" if atr > _atr_max_adaptive
            else ("↓저변동" if atr < ATR_MIN_ENTRY else "OK")
        )
        # 두 시간창(현재 14분 ATR vs 상한 산출용 60분 롤링평균)을 한 줄로 노출 —
        # "3.91>3.50인데 왜?" 질문에 대시보드만 보고 답 나오게.
        if _atr_recent_avg is not None:
            _atr_expiry_tag = "·만기캡" if _atr_ceiling_effective > ATR_ADAPTIVE_MAX_CEILING else ""
            _atr_chk_detail = (
                f"14m ATR {atr:.2f}pt → 상한 {_atr_max_adaptive:.2f}pt "
                f"(60m평균 {_atr_recent_avg:.2f}×{ATR_ADAPTIVE_MAX_MULT}{_atr_expiry_tag})"
            )
        else:
            _atr_chk_detail = (
                f"14m ATR {atr:.2f}pt → 상한 {_atr_max_adaptive:.2f}pt "
                f"(표본{len(self._atr_recent_window)}<{ATR_ADAPTIVE_MIN_SAMPLES} 정적)"
            )
        if time_zone != "OPEN_VOLATILE":
            _gap_chk_val = "구간외"  # 09:05~10:30 전용 — 시간대 밖
        elif _cr_entry_mode != "TREND_FOLLOW":
            _gap_chk_val = "모드외(TREND_FOLLOW Only)"  # MR 등 비TREND_FOLLOW 분
        elif _open_p_for_gap <= 0:
            _gap_chk_val = "N/A (시가 미캡처)"  # GapOffset 캡처 실패 — 실제 이상 신호
        else:
            _gap_chk_val = f"{_gap_in_dir:.1f}pt"
        _check_vals = {
            "signal_chk": "UP" if direction > 0 else ("DN" if direction < 0 else "FLAT"),
            "conf_chk":   f"{confidence:.1%}",
            "vwap_chk":   f"{float(features.get('vwap_position', 0)):+.3f}",
            "cvd_chk":    f"{int(features.get('cvd_direction', 0)):+d}",
            "ofi_chk":    f"{int(features.get('ofi_pressure', 0)):+d}",
            "fi_chk":     f"C{float(features.get('foreign_call_net', 0)):+.0f}",
            "candle_chk": "▲" if _prev_bar_dir > 0 else ("▼" if _prev_bar_dir < 0 else "—"),
            "time_chk":   time_zone or "—",
            "risk_chk":   f"{_dl_pct:.1%}",
            "atr_chk":    f"{atr:.2f}pt {_atr_state}",
            "atr_chk_detail": _atr_chk_detail,
            "gap_chk":    _gap_chk_val,
        }
        # 게이트 필터 결과를 checks_ui에 합산 → 대시보드 게이트 필터 섹션 V/X 아이콘 구동
        _checks_ui["atr_chk"]  = _atr_ok
        _checks_ui["gap_chk"]  = _open_gap_ok
        self.dashboard.update_entry(
            _raw_signal_ko,
            confidence,
            _final_grade,
            _checks_ui,
            qty=_qty_display,
            qty_entry_final=_qty_auto,
            final_signal=_final_signal_ko,
            reverse_enabled=_reverse_on,
            min_conf=actual_min_conf,
            ensemble_grade=grade,
            checklist_grade=_checklist_grade,
            final_entry=_final_entry_ok,
            check_values=_check_vals,
            entry_block_reason=_entry_block_reason,
            hurst=float(features.get("hurst", 0.5)),
            atr=atr,
            regime=self.current_micro_regime,
            kelly_advised_skip=_kelly_advised_skip,
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
            and (_hurst_ok or HURST_SOFT_BLOCK_ENABLED)  # 333차: 하드차단→사이징 완화
            and _atr_ok                            # 변동성 너무 낮음 진입 차단
            and _open_gap_ok                  # [370차 수정] 263차 OPEN_VOLATILE 시가이격 필터 —
                                               # _final_entry_ok에만 있고 실행 게이트엔 누락돼 있던 버그
            and not self.system_health.kill_switch_active  # [370차 수정] 86차 SHS-EKS 킬스위치 —
                                                             # 동일 누락 버그
            and _ecb_observation_ok           # [370차 수정] 254차 거래소CB 해제 후 관망 — 동일 누락 버그
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
                    self._entry_kelly_advised_skip = 1 if _kelly_advised_skip else 0
                    # [SizerMatch] Sizer 제안 vs 실제 진입 수량 불일치 감지
                    _qty_sizer_raw_val = locals().get("_qty_sizer_raw", _qty_auto)
                    if _qty_sizer_raw_val != _qty_auto:
                        log_manager.signal(
                            f"[SizerMatch] sizer={_qty_sizer_raw_val}계약 → actual={_qty_auto}계약 "
                            f"(gap={_qty_sizer_raw_val - _qty_auto}) | "
                            f"kelly={kelly_result.get('multiplier', 1.0):.2f} "
                            f"meta={_meta_size:.2f} tox={_tox_size:.2f} exec={_exec_size:.2f}"
                        )
                    # MetaGate + ToxicityGate 동시 reduce → 합산 mult < 0.50 시 진입 차단
                    # 두 게이트가 각각 독립적으로 "위험하다"고 판단한 상황이므로 진입 의미 없음
                    # 5일 실거래 분석: 이 조건은 6/24 14:04(-1.27M), 6/18 14:14 손실 케이스에 해당
                    _joint_mult = _meta_size * _tox_size
                    _joint_blocked = (
                        _meta_action == "reduce"
                        and _tox_action == "reduce"
                        and _joint_mult < 0.50
                    )
                    if _joint_blocked:
                        log_manager.signal(
                            f"[JointGateBlock] MetaGate({_meta_size:.2f})×ToxGate({_tox_size:.2f})"
                            f"={_joint_mult:.3f} < 0.50 → 진입 차단"
                        )
                        log_manager.trade(
                            f"[JointGateBlock 차단] {raw_dir_str} {_qty_auto}계약 {_final_grade}급 "
                            f"(meta={_meta_size:.2f} tox={_tox_size:.2f} joint={_joint_mult:.3f})"
                        )
                        # [EOD리포트 진단용] 체크리스트 통과 후 2차 게이트(JointGateBlock)
                        # 차단임을 entry_block_reason에 기록 — 미기록 시 EOD 리포트에서
                        # "체결실패"로만 뭉뚱그려져 원인이 JointGateBlock인지 구분 불가.
                        _entry_block_reason = (
                            f"[차단] JointGateBlock — meta={_meta_size:.2f} tox={_tox_size:.2f} "
                            f"joint={_joint_mult:.3f} < 0.50"
                        )
                        # [327차] JointGateBlock counterfactual 섀도우 — hurst_gate_shadow와
                        # 동일 패턴(§3-6). tox_size가 상수(0.7)라 joint_mult이 사실상
                        # meta_size 단일 임계와 동치라는 구조적 의문(07-14 실측 분석,
                        # docs/Ref/jointfateBlock.txt)을 누적 검증한다. 읽기 전용 계측 —
                        # 실거래 의사결정에 관여하지 않음(scripts/generate_validation_
                        # campaign_report.py가 주간 사후 판정).
                        try:
                            _jgs_mult = (
                                HURST_REGIME_ATR_MULT.get(self._entry_hurst_bucket, {})
                                if HURST_REGIME_ATR_MULT_ENABLED else {}
                            )
                            _jgs_stop_mult = ATR_STOP_MULT * _jgs_mult.get("stop", 1.0)
                            _jgs_tp1_mult = (
                                ATR_HORIZON_TP1_MULT.get(_entry_horizon, ATR_TP1_MULT)
                                * _jgs_mult.get("tp1", 1.0)
                            )
                            _jgs_dir_mult = 1 if direction == 1 else -1
                            execute(
                                TRADES_DB,
                                """INSERT INTO joint_gate_shadow
                                   (ts, direction, grade, meta_size, tox_size, joint_mult,
                                    conf, entry_price, stop_price, tp1_price)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (
                                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                                    raw_dir_str,
                                    _final_grade,
                                    float(_meta_size),
                                    float(_tox_size),
                                    float(_joint_mult),
                                    float(confidence),
                                    float(close),
                                    float(close - _jgs_dir_mult * atr * _jgs_stop_mult),
                                    float(close + _jgs_dir_mult * atr * _jgs_tp1_mult),
                                ),
                            )
                        except Exception as _jgs_e:
                            logger.warning("[JointGateShadow] counterfactual 기록 실패 (무해): %s", _jgs_e)
                    else:
                        # [237차] Hurst 미계산 진입 차단 — 워밍업 미완료(데이터 부족·오류) 시 손실 방지
                        if not features.get("hurst_ready", False):
                            log_manager.signal(
                                f"[차단] Hurst 미계산 — 워밍업 중 자동진입 차단"
                                f" (hurst={features.get('hurst', 0.5):.3f})"
                            )
                            log_manager.trade(
                                f"[Hurst 미계산 차단] {raw_dir_str} {_qty_auto}계약 {_final_grade}급"
                            )
                            _entry_block_reason = (
                                f"[차단] Hurst 미계산 — 워밍업 중 (hurst={features.get('hurst', 0.5):.3f})"
                            )
                        else:
                            # 최대허용수량·증거금 캡핑은 상단(_qty_auto 산출부)에서 이미 적용됨
                            # (패널 표시값과 동일 기준 공유 — _ts_margin_capped_qty 참조)
                            if _qty_auto <= 0:
                                log_manager.signal(
                                    f"[차단] 증거금 부족 — {raw_dir_str} 자동진입 차단"
                                )
                                _entry_block_reason = "[차단] 증거금 부족 — 자동진입 차단"
                            else:
                                # [269차] 진입 직전 체크리스트 결과 TRADE 로그 — 사후 분석용
                                _chk_d = (_cr or {}).get("checks", {})
                                log_manager.trade(
                                    "[진입체크] %s→%s %d계약 %s급 | %s | conf=%s" % (
                                        raw_dir_str, final_dir_str, _qty_auto, _final_grade,
                                        " ".join(
                                            "%s%s" % (k.split("_", 1)[1][:4], "✅" if v else "❌")
                                            for k, v in _chk_d.items() if not k.startswith("0_")
                                        ),
                                        "%.1f%%" % (confidence * 100),
                                    )
                                )
                                # L2 통과 && 모드 필터 통과 → 진입
                                # [363차 후속] 진입 순간 quantile 기대엣지 스냅샷 — 사후
                                # 분석(loss_tier1_qty1_shadow 등) 전용, 리스크 판단 무관여
                                _q_est = (decision.get("meta_gate") or {}).get("quantile_estimate") or {}
                                self._execute_entry(
                                    final_dir_str, close, _qty_auto, atr, _final_grade,
                                    raw_direction=raw_dir_str,
                                    reverse_enabled=reverse_on,
                                    entry_horizon=_entry_horizon,
                                    hurst_bucket=self._entry_hurst_bucket,
                                    extra_stop_mult=_vb_stop_widen_mult,
                                    quantile_expected_pt=_q_est.get("expected_pt"),
                                    quantile_uncertainty_pt=_q_est.get("uncertainty_pt"),
                                )
                                self._log_exec_1m_shadow(
                                    final_dir_str, _final_grade, features, horizon_proba,
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
                # [237차] P2-b 셋업 컨텍스트 — C급 경로에도 동일 설정 (hurst_bucket 공백 방지)
                _hurst_now_c = float(features.get("hurst", 0.5) or 0.5)
                self._entry_hurst_bucket = (
                    "trend"       if _hurst_now_c >= 0.55
                    else "neutral" if _hurst_now_c >= 0.45
                    else "mean-revert"
                )
                self._entry_hour_bucket = datetime.datetime.now().hour
                self._entry_was_restart = 1 if self._session_no > 1 else 0
                self._entry_had_partial = 0
                self._entry_kelly_advised_skip = 1 if _kelly_advised_skip else 0
                # [237차] Hurst 미계산 시 C급 진입도 차단
                if not features.get("hurst_ready", False):
                    log_manager.signal(
                        f"[차단] Hurst 미계산 — C급 자동진입 차단"
                        f" (hurst={features.get('hurst', 0.5):.3f})"
                    )
                    log_manager.trade(
                        f"[Hurst 미계산 차단] {raw_dir_str} C급 {_qty_auto}계약 {_final_grade}급"
                    )
                # [239차] conf_floor — C급 경로에도 동일 하한 적용
                # checklist.py는 auto_entry=True 시에만 floor를 체크하므로
                # C급(auto_entry=False)은 여기서 별도로 차단해야 함
                elif confidence < ENS_CONF_FLOOR_FOR_AUTO:
                    log_manager.signal(
                        f"[차단] conf_floor — C급 자동진입 차단"
                        f" (conf={confidence:.1%} < floor={ENS_CONF_FLOOR_FOR_AUTO:.1%})"
                    )
                    log_manager.trade(
                        f"[conf_floor 차단] {raw_dir_str} C급 {_qty_auto}계약"
                        f" (conf={confidence:.1%} floor={ENS_CONF_FLOOR_FOR_AUTO:.1%})"
                    )
                elif _qty_auto <= 0:
                    # [재발방지] 증거금 부족으로 이미 0 캡핑됨(_qty_auto 산출부 참조) —
                    # max(1, ...) 라운딩으로 인해 유령 1계약 주문이 나가지 않도록 여기서 차단
                    log_manager.signal(
                        f"[차단] 증거금 부족 — {raw_dir_str} C급 실험 자동진입 차단"
                    )
                else:
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
                    # [269차] C급 경로도 동일하게 체크 결과 로그
                    _chk_d_c = (_cr or {}).get("checks", {})
                    log_manager.trade(
                        "[진입체크] %s→%s %d계약 C급(실험) | %s | conf=%s" % (
                            raw_dir_str, final_dir_str, _qty_c_exp,
                            " ".join(
                                "%s%s" % (k.split("_", 1)[1][:4], "✅" if v else "❌")
                                for k, v in _chk_d_c.items() if not k.startswith("0_")
                            ),
                            "%.1f%%" % (confidence * 100),
                        )
                    )
                    _q_est_c = (decision.get("meta_gate") or {}).get("quantile_estimate") or {}
                    self._execute_entry(
                        final_dir_str, close, _qty_c_exp, atr, _final_grade,
                        raw_direction=raw_dir_str,
                        reverse_enabled=reverse_on,
                        entry_horizon=_entry_horizon,
                        hurst_bucket=self._entry_hurst_bucket,
                        extra_stop_mult=_vb_stop_widen_mult,
                        quantile_expected_pt=_q_est_c.get("expected_pt"),
                        quantile_uncertainty_pt=_q_est_c.get("uncertainty_pt"),
                    )
                    self._log_exec_1m_shadow(
                        final_dir_str, _final_grade, features, horizon_proba,
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
            "stop_move_reason": _pos.last_update_reason or "",
            "bar_low":  bar.get("low",  0.0) if bar else 0.0,
            "bar_high": bar.get("high", 0.0) if bar else 0.0,
            "atr_ok":      _atr_ok,
            "open_gap_ok": _open_gap_ok,
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
        self._last_pipe_ms = _pipe_ms   # 다음 사이클 Degraded 선제차단 lookahead용
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
        # [진단] PipePerf 항상 INFO 출력 — 임계값 무관하게 매 봉 기록 (병목 분석용)
        log_manager.system(
            f"[PipePerf][DBG]{_retrain_tag_pipe} "
            f"total={_pipe_ms:.0f}ms | {_all_steps_str or '─'}",
            "INFO",
        )
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
            logger.error("[STEP9] save_step9_batch 실패 — DB 미기록 (conf=%s grade=%s): %s",
                         decision.get("confidence", "?"), decision.get("grade", "?"), e)

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
                _min_conf_sgd  = 0.52   # P2-D: 저신뢰 레이블 오염 차단
                for _dv in _sgd_deferred_verified:
                    # P2-D: 고신뢰도 필터 — conf < 0.52 예측 결과는 학습 제외
                    if float(_dv.get("confidence", 0.0)) < _min_conf_sgd:
                        continue
                    # [P3] FLAT 결과는 SGD 학습 대상에서 제외(기권) — online_learner.learn()도
                    # 동일 가드를 갖지만, 여기서 먼저 걸러야 아래 dedup 타임스탬프가
                    # "실제로 학습하지 않은 분"에 소비되지 않는다.
                    if int(_dv.get("actual", 0)) == DIRECTION_FLAT:
                        continue
                    _hz_learn = _dv["horizon"]
                    # [P1] 호라이즌별 봉단위 dedup — 검증은 매분 발생하지만 같은
                    # N분봉에서 파생된 예측은 (N-1)/N이 동일 정보 재탕(예: 30m은
                    # 봉당 29/30 겹침). 자기 봉 길이(N분) 미만 간격이면 스킵해
                    # 같은 레이블 반복 주입 → 단방향 붕괴를 방지한다.
                    _last_learn_ts_s = self._sgd_learn_last_ts.get(_hz_learn, "")
                    if _last_learn_ts_s:
                        _gap_min = (
                            datetime.datetime.strptime(_dv["ts"], "%Y-%m-%d %H:%M:%S")
                            - datetime.datetime.strptime(_last_learn_ts_s, "%Y-%m-%d %H:%M:%S")
                        ).total_seconds() / 60.0
                        if _gap_min < HORIZONS.get(_hz_learn, 1):
                            continue
                    _dfeat = _dv.get("features") or {}
                    _dx_full = np.array(
                        [_dfeat.get(f, 0.0) for f in self.model.feature_names],
                        dtype=np.float32,
                    )
                    # [P2] SGD 전용 피처 슬라이싱 — GBM(_hz_feat_indices)과 별도.
                    # 구 B군 N분봉 교정(hurst·atr_ratio 등)은 GBM 전용 피처였던 시절 로직 —
                    # 새 SGD_FEATURE_NAMES_BY_HORIZON에는 해당 피처가 없어 제거함.
                    _h_idx_learn = self._sgd_feat_indices.get(_hz_learn)
                    _dx_learn = _dx_full[_h_idx_learn] if _h_idx_learn is not None else _dx_full
                    self.online_learner.learn(
                        horizon         = _hz_learn,
                        x               = _dx_learn,
                        actual_label    = _dv["actual"],
                        predicted_label = _dv["predicted"],
                    )
                    self._sgd_learn_last_ts[_hz_learn] = _dv["ts"]
            log_manager.learning(
                f"[SGD] {len(_sgd_deferred_verified)}건 학습 | "
                f"SGD비중={self.online_learner.sgd_weight:.0%} "
                f"50분정확도={self.online_learner.recent_accuracy():.1%}"
            )
            # [Qualify] trained_cycles 동기화 — online_learner._horizon_counts 반영
            _hc = getattr(self.online_learner, "_horizon_counts", {})
            _need = getattr(runtime_settings, "HORIZON_QUALIFY_MIN_CYCLES", 3)
            _need_trained_map = getattr(runtime_settings, "HORIZON_QUALIFY_MIN_TRAINED", {})
            for _h, _cnt in _hc.items():
                if _h not in self._horizon_runtime_state:
                    continue
                _qs = self._horizon_runtime_state[_h]
                _qs["trained_cycles"] = _cnt
                _need_trained = _need_trained_map.get(_h, _need)
                if _qs["verified_cycles"] >= _need and _qs["trained_cycles"] >= _need_trained:
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
                # [260704 감사 P2] E_CHAMPION_TP1_SKIP_TRAIL 전용 — 진입 알파를 챔피언과
                # 동일하게 미러링해 청산 규칙(TP1 부분청산 vs 트레일 단독) 효과만 격리한다.
                "decision": {
                    "direction":  direction,
                    "confidence": confidence,
                    "grade":      grade,
                },
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

        # [225차 P0] 이번 봉 종가를 다음 파이프라인의 sigma 전봉 가격으로 확정
        # tick 이벤트(_on_tick_price_update)와 분리해 ret=0 고착 차단
        self._sigma_prev_price = close

        # [228차] 실제 분봉 완료 시각 기록 — 복구 스킵 경로와 구별해 ExchangeCB 정확히 감지
        self._last_real_pipeline_dt = datetime.datetime.now()

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

        # ── TP1 달성 후 잔여분 손절 → 손익분기(진입가) 이동 ──────────
        # 체결 확인 후(Chejan) 호출되므로 진짜 fill 기준으로 이동
        # - 조건: stage==1, 아직 포지션 잔여 있음, 이동이 스톱 개선 방향일 때만
        # - 1계약 포지션은 arm_tp1 경로에서 이미 처리됨(여기 도달 안 함)
        if stage == 1 and self.position.status != "FLAT":
            _mult = 1 if self.position.status == "LONG" else -1
            _entry = self.position.entry_price
            _prev_stop = self.position.stop_price
            if _mult * (_entry - _prev_stop) > 0:
                self.position.stop_price = _entry
                self.position.last_update_reason = "tp1_breakeven"
                self.position._save_state()
                log_manager.system(
                    f"[TP1-Breakeven] {self.position.status} 잔여 {self.position.quantity}계약 "
                    f"손절 {_prev_stop:.2f} → 진입가 {_entry:.2f}",
                    "INFO",
                )
                self.dashboard.append_pnl_log(
                    f"TP1 손절이동 | {self.position.status} 잔여 {self.position.quantity}계약",
                    f"손절 {_prev_stop:.2f} → 진입가 {_entry:.2f} (손익분기 보호)",
                )

    def _post_loss_tier1_exit(self, result: dict) -> None:
        """[360차] 손절 계단화 1차 후처리 — CB/Kelly 통계, 대시보드, DB 기록.

        _post_partial_exit()과 달리 stop_price는 절대 건드리지 않는다 — 잔여 포지션은
        기존 stop_price(전체 ATR×1.5 폭) 그대로 유지해야 "조기축소 후 잔여는 원래 폭까지
        태운다"는 설계 의도가 지켜진다(TP1의 손익분기 이동 로직을 여기서 재사용하면
        안 되는 이유는 이 함수를 별도로 둔 것 자체가 그 답).
        """
        pnl = result["pnl_pts"]
        qty = result["quantity"]

        if pnl > 0:
            self.circuit_breaker.record_win()
            self.kelly.record(win=True, pnl_pts=pnl)
        else:
            self.circuit_breaker.record_stop_loss()
            self.kelly.record(win=False, pnl_pts=pnl)

        log_manager.trade(
            f"[손절1차 조기축소] {qty}계약 @ {result['exit_price']:.2f} "
            f"PnL={pnl:+.2f}pt ({result['pnl_krw']:+,.0f}원) "
            f"잔여={result['remaining']}계약"
        )
        _cum_pnl = self.position.daily_stats()["pnl_krw"]
        self.dashboard.append_pnl_log(
            f"손절1차 조기축소 | {result['direction']} {qty}계약 @ {result['exit_price']}",
            f"PnL {pnl:+.2f}pt  {result['pnl_krw']:+,.0f}원  잔여 {result['remaining']}계약  │ 금일 {_cum_pnl:+,.0f}원",
        )
        self.dashboard.minute_chart_record_exit(
            result["exit_price"],
            datetime.datetime.now(),
            finalize=False,
            pnl_pts=result.get("pnl_pts"),
            reason="손절1차 조기축소",
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
        """선물 진입 주문. 0=성공, 음수=오류.

        [260704 감사 P1] LIMIT_ENTRY_FIRST_ENABLED=True면 microprice 기준 유리한 쪽
        1틱 지정가로 먼저 시도한다. 이 경우 즉시 체결이 보장되지 않으므로 호출부
        (_ts_execute_entry)는 self._pending_limit_is_active를 확인해 낙관적 포지션
        오픈을 건너뛰어야 한다 — 실제 오픈은 Chejan 체결 이벤트로만 반영된다.
        """
        code = getattr(self, "_futures_code", "")
        if not code:
            return -1
        account_no = self._get_active_account_no()
        if not account_no:
            return -1
        side = "BUY" if direction == "LONG" else "SELL"

        self._pending_limit_is_active = False
        if LIMIT_ENTRY_FIRST_ENABLED:
            _rd = getattr(self, "realtime_data", None)
            bid1 = float(getattr(_rd, "_last_bid1", 0.0) or 0.0)
            ask1 = float(getattr(_rd, "_last_ask1", 0.0) or 0.0)
            try:
                tick = float(get_contract_spec(code).get("tick_size", 0.0) or 0.0)
            except Exception:
                tick = 0.0
            if bid1 > 0 and ask1 > 0 and tick > 0:
                limit_price = round(bid1 + tick, 4) if direction == "LONG" else round(ask1 - tick, 4)
                logger.info(
                    "[LimitEntry][ORDER_SENT] dir=%s qty=%d price=%.2f bid1=%.2f ask1=%.2f tick=%.2f t=%.3f",
                    direction, qty, limit_price, bid1, ask1, tick, time.time(),
                )
                res = self.broker.send_limit_order(
                    account_no=account_no,
                    code=code,
                    side=side,
                    qty=qty,
                    price=limit_price,
                    rqname="지정가진입",
                    screen_no="1000",
                )
                ret = int(res.get("ret", -1))
                order_no = str(res.get("order_no", "") or "")
                if ret == 0 and order_no:
                    self._pending_limit_is_active = True
                    self._pending_limit_order_no = order_no
                    self._pending_limit_submitted_at = time.time()
                    self._pending_limit_price = limit_price
                else:
                    logger.warning(
                        "[LimitEntry][ORDER_SENT] 지정가 접수 실패 ret=%s order_no=%s — 시장가로 폴백",
                        ret, order_no,
                    )
                    return self.broker.send_market_order(
                        account_no=account_no, code=code, side=side, qty=qty,
                        rqname="진입", screen_no="1000",
                    )
                return ret
            logger.warning(
                "[LimitEntry] bid1/ask1/tick_size 미확보(bid1=%.2f ask1=%.2f tick=%.2f) — 시장가로 진행",
                bid1, ask1, tick,
            )

        return self.broker.send_market_order(
            account_no=account_no,
            code=code,
            side=side,
            qty=qty,
            rqname="진입",
            screen_no="1000",
        )

    def _check_limit_entry_timeout(self) -> None:
        """[260704 감사 P1] 지정가 진입 타임아웃 감시 (2초 주기 QTimer).

        LIMIT_ENTRY_TIMEOUT_SEC 경과 시 무조건 취소만 한다 — 시장가 전환 없음
        (2026-07-05 사용자 지시: 가정이 깨져도 안전하도록 포지션을 억지로 열지 않는다).
        부분체결분이 있었다면 그만큼은 이미 실제 체결로 반영되어 있으므로 그대로 두고,
        미체결 잔량만 취소한다.
        """
        if not getattr(self, "_pending_limit_is_active", False):
            return
        pending = self._pending_order
        if not pending or not pending.get("is_limit_entry"):
            # 이미 전량 체결되어 pending이 정리됐거나 다른 사유로 소멸 — 플래그만 리셋
            self._pending_limit_is_active = False
            return

        submitted_at = getattr(self, "_pending_limit_submitted_at", None)
        if submitted_at is None:
            return
        elapsed = time.time() - submitted_at
        if elapsed < LIMIT_ENTRY_TIMEOUT_SEC:
            return

        order_no = str(pending.get("order_no") or getattr(self, "_pending_limit_order_no", "") or "")
        filled = int(pending.get("filled_qty", 0) or 0)
        target = int(pending.get("qty", 0) or 0)
        remaining = max(target - filled, 0)

        logger.info(
            "[LimitEntry][TIMEOUT] order_no=%s filled=%d/%d elapsed=%.1fs — 취소(시장가 전환 없음) t=%.3f",
            order_no, filled, target, elapsed, time.time(),
        )
        log_manager.system(
            f"[LimitEntry] 지정가 진입 타임아웃 — 취소 filled={filled}/{target} order_no={order_no or '?'}",
            "WARNING",
        )
        if order_no and remaining > 0:
            account_no = self._get_active_account_no()
            code = getattr(self, "_futures_code", "")
            cancel_ret = self.broker.cancel_order(
                account_no=account_no, order_no=order_no, code=code, qty=remaining,
            )
            logger.info("[LimitEntry][CANCEL] order_no=%s ret=%s t=%.3f", order_no, cancel_ret, time.time())

        self._pending_limit_is_active = False
        self._clear_pending_order()

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

    def _log_exec_1m_shadow(
        self, direction: str, grade: str,
        features: Optional[dict], horizon_proba: Optional[dict],
    ) -> None:
        """[331차 후속2] 1m 활용방안 A(집행/타이밍 필터) 후보 검증용 섀도우 계측.

        실제 체결된 진입에 1m 마이크로구조 피처·1m GBM 자체 예측을 진단 태그로
        붙여 exec_1m_shadow에 기록한다. 라이브 의사결정에는 전혀 관여하지 않음
        (게이트·사이징 어디에도 이 결과를 소비하는 코드 없음) — 축적 후
        trades 테이블과 entry_ts로 조인해 승패/pnl과의 상관을 사후 분석하는 용도.
        """
        try:
            _feat = features or {}
            _hp1m = (horizon_proba or {}).get("1m") or {}
            _tox = self.toxicity_gate.evaluate(_feat)
            _dir_sign = 1 if direction == "LONG" else (-1 if direction == "SHORT" else 0)
            _hz1m_dir = int(_hp1m.get("direction", 0) or 0)
            _hz1m_agrees = 1 if (_hz1m_dir != 0 and _hz1m_dir == _dir_sign) else 0
            execute(
                TRADES_DB,
                """INSERT INTO exec_1m_shadow
                   (ts, direction, grade, spread_ticks, toxicity_score, cancel_add_ratio,
                    tox_gate_action, tox_gate_score, hz1m_direction, hz1m_confidence, hz1m_agrees)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                    direction,
                    grade,
                    float(_feat.get("spread_ticks", 0.0) or 0.0),
                    float(_feat.get("toxicity_score", 0.0) or 0.0),
                    float(_feat.get("cancel_add_ratio", 0.0) or 0.0),
                    str(_tox.get("action", "")),
                    float(_tox.get("score", 0.0) or 0.0),
                    _hz1m_dir,
                    float(_hp1m.get("confidence", 0.0) or 0.0),
                    _hz1m_agrees,
                ),
            )
        except Exception as _e1s_e:
            logger.warning("[Exec1mShadow] 기록 실패 (무해): %s", _e1s_e)

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
        h_acc_n = {
            hz: ol.horizon_acc_samples(hz)
            for hz in ol._fitted
        }

        # CB③ 30분 정확도
        cb_status = self.circuit_breaker.status_dict()

        # DriftAdjuster — SGD alpha 조정 상태 (DRIFT_UP/RECOVERY_DOWN/HOLD/SKIP_LOW_SAMPLE)
        drift_status = self.drift_adjuster.get_status()

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
            "horizon_acc_samples": h_acc_n,
            "buffer_accuracy":   buf_acc,
            "cb_accuracy_30m":   cb_status["accuracy_30m"],
            "cb_samples":        cb_status["cb3_samples"],
            "cb_streak":         cb_status["high_conf_wrong_streak"],
            "drift_alpha":       drift_status["alpha"],
            "drift_action":      drift_status["action"],
            "drift_history":     drift_status["history"],
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
                # [331차 후속2] 1m 활용방안 C(카나리아) — 하루 1회만. 28일 롤링 IC는
                # 15분 주기로 다시 돌려도 값이 거의 안 바뀌어 계산 낭비이므로 날짜 게이트.
                _today = datetime.date.today()
                if self._canary_1m_last_run_date != _today:
                    if self._run_effect_report_script("compute_canary_1m_ic.py"):
                        self._canary_1m_last_run_date = _today
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
                # [350차 후속] 극단 z-score 스캔은 호라이즌별 실사용 슬라이스가 아니라
                # 공유 스케일러 기준 전체 피처(SHAP 후보 포함)를 본다 — DYNAMIC_FEATURES_POOL
                # 후보(예: opt_atm_pcr, 아직 어떤 호라이즌의 active_features에도 미편입)의
                # 노이즈가 실거래에 쓰이는 이상값과 구분 없이 찍혀 트러블슈팅 시 혼동을 준다
                # (2026-07-16 정기점검 P2-c 딥다이브). 어떤 호라이즌에도 편입 안 된 이름에
                # "(candidate)" 태그를 붙여 실사용 여부를 로그만 보고 구분할 수 있게 한다.
                _active_feat_names = set()
                for _hz_names in (getattr(self.model, "horizon_feature_names", None) or {}).values():
                    _active_feat_names.update(_hz_names)
                _tagged_feats = [
                    fn if (not _active_feat_names or fn in _active_feat_names)
                    else f"{fn}(candidate)"
                    for fn in _outlier_feats[:3]
                ]
                reasons.append("이상값피처({})".format(",".join(_tagged_feats)))
            if reasons:
                log_manager.signal("[ZeroDiag] 진입X 원인: {}".format(" / ".join(reasons)))
        except Exception as _de:
            logger.debug("[ZeroDiag] 진단 실패: %s", _de)

    def _load_prev_day_closes_at_startup(self) -> None:
        """[2026-07-14 딥다이브 P2-2] 기동 시 DB에서 가장 최근 과거 거래일 종가맵을 로드.

        daily_close()가 당일 종가 버퍼를 feature_builder에 채워 다음날 prev_day_same_hour_ret
        계산에 쓰는데, 이 버퍼는 순수 인메모리 상태 — 프로세스가 매 거래일 아침 새로
        기동되는 이 시스템의 실제 운영 패턴에서는 daily_close() 실행 후 프로세스가 종료되면
        버퍼가 유실돼 다음날 STEP4가 빈 버퍼를 보고 갱신을 건너뛴다(main.py:4671 가드).
        그 결과 prev_day_same_hour_ret이 raw_features에서 관측 기간 내내(2025-08-19~) 상수
        0으로 남아있었음(무스킬_피처셋_딥다이브_보고서_2026-07-13.md F5). 기동 시점에 DB에서
        직접 전전일(주말/휴장 자동 스킵 — MAX(ts) < 오늘 날짜)을 조회해 채우면 daily_close()를
        기다리지 않고도 당일 첫 분봉부터 정상 계산된다.
        """
        try:
            from config.settings import RAW_DATA_DB as _RDB
            import sqlite3 as _sqlite3
            today_str = datetime.datetime.now().date().isoformat()
            with _sqlite3.connect(_RDB, timeout=10) as _conn:
                _conn.row_factory = _sqlite3.Row
                _row = _conn.execute(
                    "SELECT MAX(ts) AS ts FROM raw_candles WHERE ts < ?", (today_str,)
                ).fetchone()
                _prev_day = (_row["ts"] or "")[:10] if _row else ""
                if not _prev_day:
                    logger.info("[FeatureBuilder] 기동 시 전일 종가 없음(초기 DB) — 스킵")
                    return
                _rows = _conn.execute(
                    "SELECT ts, close FROM raw_candles WHERE ts >= ? AND ts < ? ORDER BY ts",
                    (_prev_day, _prev_day + "Z"),
                ).fetchall()
            _prev_closes = {r["ts"]: float(r["close"]) for r in _rows}
            if _prev_closes:
                self.feature_builder.set_prev_day_closes(_prev_closes)
                logger.info(
                    "[FeatureBuilder] 기동 시 전일(%s) 종가 버퍼 로드: %d봉",
                    _prev_day, len(_prev_closes),
                )
        except Exception as _e:
            logger.warning("[FeatureBuilder] 기동 시 전일 종가 버퍼 로드 실패: %s", _e)

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

        # [269차] EXIT Chejan 이벤트 유실 일별 집계 보고 후 리셋
        _miss_cnt = getattr(self, "_chejan_exit_miss_count", 0)
        if _miss_cnt > 0:
            log_manager.system(
                f"[ChejanMiss] 금일 EXIT 이벤트 유실 총 {_miss_cnt}건"
                + (" — 재검토 권고 (3건 이상)" if _miss_cnt >= 3 else ""),
                "WARNING" if _miss_cnt >= 3 else "INFO",
            )
        self._chejan_exit_miss_count = 0

        # ── 챔피언-도전자 일별 집계 ─────────────────────────────
        if self.challenger_engine is not None:
            try:
                self.challenger_engine.update_daily_metrics(now.date().isoformat())
            except Exception as _ce2:
                logger.warning("[Challenger] update_daily_metrics 실패 (스킵): %s", _ce2)

        # ── [260704 감사 P2] 챔피언 heartbeat — 일별 1회 체크 ─────
        # 주의: CHAMPION_BASELINE_ID는 challenger_engine에 shadow 도전자로 등록되어
        # 있지 않아(_register_default_challengers 참조) 자체 거래 이력이 없다 —
        # 최초 승격이 일어나기 전까지는 "표본 부족"으로만 나온다(콜드스타트, 정상).
        # 승격 후에는 새 챔피언이 도전자였을 때의 이력이 그대로 재활용된다.
        # 사이즈 자동축소는 아직 실거래 배선에 연결하지 않았다 — 실측 데이터가
        # 쌓여 정상 동작이 확인된 뒤 연결 여부를 별도로 결정할 것.
        if self.promotion_manager is not None:
            try:
                _hb = self.promotion_manager.check_champion_heartbeat()
                log_manager.system(
                    f"[ChampionHeartbeat] {_hb['reason']}", "WARNING" if _hb["degraded"] else "INFO",
                )
            except Exception as _hb_e:
                logger.warning("[ChampionHeartbeat] 체크 실패 (스킵): %s", _hb_e)

        # 개선 3: 당일 종가 버퍼를 feature_builder에 전달 → 내일 prev_day_same_hour_ret 계산
        try:
            from utils.db_utils import fetchall
            from config.settings import RAW_DATA_DB as _RDB
            import sqlite3 as _sqlite3
            today_str = now.date().isoformat()
            with _sqlite3.connect(_RDB, timeout=10) as _conn:
                _conn.row_factory = _sqlite3.Row
                _rows = _conn.execute(
                    "SELECT ts, close FROM raw_candles WHERE ts >= ? AND ts < ? ORDER BY ts",
                    (today_str, today_str + "Z"),
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

        # GBM 재학습 + P8 스케일러 재적합은 py310_64 장외 스케줄러(MireukiEODRetrain, 15:45)가
        # retrain_eod.py를 통해 수행한다 (191차~, OOM 방지).
        # daily_close()에서 retrain_now()를 직접 호출하지 않는다:
        #   - py37_32 메인 스레드 동기 실행 → 12분+ Qt 블로킹 → UI 행 상태 (오늘 실증)
        #   - py310_64 스케줄러 완료 후 마커 파일로 성공 여부 확인

        # 마커 파일 기반으로 내일 08:55 PreRetrain 스킵 신호 기록
        _eod_marker_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data",
            f"eod_retrain_done_{datetime.date.today().strftime('%Y%m%d')}.txt",
        )
        if os.path.exists(_eod_marker_path):
            self._eod_retrain_ok = True
            try:
                _eod_ss = self._read_session_state()
                _eod_ss["eod_retrain_ok_date"] = datetime.date.today().isoformat()
                self._write_session_state(_eod_ss)
            except Exception as _eod_ss_e:
                logger.warning("[EOD] eod_retrain_ok_date 저장 실패 (무해): %s", _eod_ss_e)
            log_manager.system(
                "[DailyClose] EOD 재학습 마커 확인 — 스케줄러 완료, 내일 PreRetrain 스킵 예약",
                "INFO",
            )
        else:
            log_manager.system(
                "[DailyClose] EOD 재학습 마커 없음 — retrain_eod.py 미실행 또는 실패 "
                "(내일 PreRetrain에서 보완 재학습 예약됨)",
                "WARNING",
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
        _today_n_samples = self.online_learner.sample_count
        try:
            self.daily_consolidator.consolidate()
        except Exception as _dce:
            logger.warning("[DailyConsolidator] 집계 실패 (스킵): %s", _dce)
        try:
            _drift_result = self.drift_adjuster.record_accuracy(
                _today_accuracy, n_samples=_today_n_samples
            )
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
                        f"docs/정기점검/LABEL_THRESHOLD_RECALIBRATION_GUIDE.md 참조",
                        "WARNING",
                    )
            except Exception as _tre:
                logger.warning("[ThresholdRecal] 실행 실패 (스킵): %s", _tre)

        # ── ATR 게이트 상/하한 재보정 제안 모니터 (303차, 금요일 + 최근 실행 후
        #    10일 이상 경과 시에만 — 사실상 1~2주 주기). 자동 반영 없음, 제안만
        #    기록 + WATCHLIST 이상이면 Slack 알림(utils.notify) — 알파봇과 동일하게
        #    사람이 config/settings.py를 검토 후 수동 반영한다.
        if now.weekday() == 4:   # 금요일
            try:
                _atr_recal = self.atr_ceiling_recalibrator.run_if_due(
                    today=now.date().isoformat()
                )
                if _atr_recal and _atr_recal["alert"] != "CLEAR":
                    log_manager.system(
                        f"[ATRCeilingRecal] {_atr_recal['alert']} — "
                        f"floor {_atr_recal['current_floor']}→{_atr_recal['suggested_floor']}pt "
                        f"({_atr_recal['floor_delta_pct']:+.0f}%), "
                        f"ceiling {_atr_recal['current_ceiling']}→{_atr_recal['suggested_ceiling']}pt "
                        f"({_atr_recal['ceiling_delta_pct']:+.0f}%) — Slack 알림 발송, 수동 검토 필요",
                        "WARNING",
                    )
            except Exception as _atre:
                logger.warning("[ATRCeilingRecal] 실행 실패 (스킵): %s", _atre)

        # ── entry_horizon(select_entry_horizon) 경계값 재보정 모니터 (375차,
        #    금요일 + 최근 실행 후 7일 이상 경과 시에만). 374차가 발견한
        #    "경계값 고착"(61건 실거래 전부 5m 분류) 재발 여부를 매주 확인.
        #    자동 반영 없음 — ThresholdRecal/ATRCeilingRecal과 동일하게 제안만
        #    기록, model/ensemble_decision.py의 ENTRY_HORIZON_B1/B2는 사람이
        #    검토 후 수동 반영한다.
        if now.weekday() == 4:   # 금요일
            try:
                _eh_recal = self.entry_horizon_recalibrator.run_if_due(
                    today=now.date().isoformat()
                )
                if _eh_recal and _eh_recal["alert"] != "CLEAR":
                    log_manager.system(
                        f"[EntryHorizonRecal] {_eh_recal['alert']} — "
                        f"경계 {_eh_recal['current_b1']}/{_eh_recal['current_b2']} → "
                        f"재계산 {_eh_recal['recalc_b1']}/{_eh_recal['recalc_b2']} "
                        f"(δ{_eh_recal['b1_delta_pct']:+.0f}%/{_eh_recal['b2_delta_pct']:+.0f}%), "
                        f"버킷비중(1m/3m/5m)="
                        f"{_eh_recal['bucket_1m_pct']:.0f}%/{_eh_recal['bucket_3m_pct']:.0f}%/"
                        f"{_eh_recal['bucket_5m_pct']:.0f}% — 수동 검토 필요",
                        "WARNING",
                    )
            except Exception as _ehe:
                logger.warning("[EntryHorizonRecal] 실행 실패 (스킵): %s", _ehe)

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
        self.basis_calc.reset_daily()
        self._last_vkospi = None
        self.position.reset_daily()
        self.circuit_breaker.reset_daily()
        self.profit_guard.reset_daily()
        self.online_learner.reset_daily()
        # [311차 후속 B안] 극단성 보정기 — GBM 배치재학습과 같은 리듬(일 1회)으로 재적합.
        # reset_daily 없음 — 버퍼(BATCH_SIZE=5000)는 날짜 경계와 무관하게 계속 누적.
        try:
            _ext_fit = self.extremity_corrector.fit_all()
            log_manager.learning(f"[ExtremityCorrector] 일일 재적합: {_ext_fit}")
        except Exception as _ext_e:
            logger.warning("[ExtremityCorrector] daily fit_all 실패 (무해): %s", _ext_e)
        self.market_dna.reset_daily()
        self.core_health.reset_daily()
        self.model.reset_daily_gap_offset()
        self._first_tick_notified = False        # 다음 날 첫 분봉에서 갭 오프셋 재설정
        self._session_open_price = 0.0            # 시가이격 필터·day_ret 산정용 당일 시가 초기화
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
        self._bias_override_timer = {h: 0 for h in HORIZONS}
        self._conf_prev.clear()
        self._conf_stuck = {h: 0 for h in HORIZONS}
        self._sgd_learn_last_ts = {h: "" for h in HORIZONS}
        self._ensemble_conf_cache.clear()
        self._param_corr_history.clear()
        self._shap_feature_window.clear()
        for _h in self._shap_labeled_window:
            self._shap_labeled_window[_h].clear()
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
        # CB 3단계(당일 장 조기 종료) 대비: 마감 시 거래소 CB 모드 강제 해제.
        # 3단계 발동 시 _on_candle_closed가 다시 불리지 않아 _exchange_cb_mode=True가
        # 다음날까지 잔류하며 불필요한 GBM 재학습·스케일러 재적합을 유발하는 것을 방지.
        if self._exchange_cb_mode:
            log_manager.system(
                "[DailyClose] 거래소 CB 모드 잔류 감지 → 일일 마감 시 강제 해제 "
                "(CB 3단계 또는 장중 종료로 인한 미해제 추정)",
                "WARNING",
            )
        self._exchange_cb_mode = False
        self._exchange_cb_start = None
        self._ecb_observation_until = None
        try:
            # [304차 후속] daily_close()는 백그라운드 스레드 실행 — 직접 호출 금지, 메인 스레드로 위임
            _daily_close_ui_sig.request.emit(lambda: self.dashboard.update_exchange_cb_badge("NORMAL"))
        except Exception:
            pass

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

        _gross_sign_dc = "+" if stats["gross_krw"] >= 0 else ""
        _net_sign_dc = "+" if stats["pnl_krw"] >= 0 else ""
        notify(
            f"📊 미륵이 일일 마감 집계\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"거래: {stats['trades']}회 (승 {stats['wins']} / 패 {stats['losses']})\n"
            f"총손익: {_gross_sign_dc}{stats['gross_krw']:,.0f}원  "
            f"(수수료 -{stats['commission']:,.0f}원)\n"
            f"순손익: {_net_sign_dc}{stats['pnl_krw']:,.0f}원\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"정산·재학습 마무리 중 — 완료 시 종료 알림 예정",
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
            # [304차 후속] daily_close()는 백그라운드 스레드 실행 — 직접 호출 금지, 메인 스레드로 위임
            # (0708 15:40~15:43 access violation 크래시 루프 실측: main.py daily_close →
            # update_strategy_ops → set_fingerprint_level → refresh 스택)
            _daily_close_ui_sig.request.emit(
                lambda _dl=_drift_level: self.dashboard.update_strategy_ops({"drift_level": _dl})
            )
        except Exception as _de:
            logger.warning("[DriftDetector] 업데이트 실패 (스킵): %s", _de)

        # [297차, P1-5] mc–conf 괴리 조기경보 — 경보만 출력, mc·임계값 자동 조정 없음
        # (§3-7). 진입후보(confidence>=min_conf) 분 수가 붕괴하면 4주 검증 캠페인
        # 표본 자체가 희소해지므로 사용자가 조기에 알아채야 한다.
        _mc_gap_today = 0
        _mc_gap_avg = 0.0
        try:
            if getattr(runtime_settings, "MC_CONF_GAP_ALERT_ENABLED", True):
                from utils.db_utils import fetch_entry_candidate_gap
                _gap = fetch_entry_candidate_gap(
                    lookback_days=runtime_settings.MC_CONF_GAP_ALERT_LOOKBACK_DAYS
                )
                _mc_gap_today = _gap.get("today", 0)
                _mc_gap_avg = _gap.get("avg", 0.0)
                _min_today = runtime_settings.MC_CONF_GAP_ALERT_MIN_TODAY
                _min_avg   = runtime_settings.MC_CONF_GAP_ALERT_MIN_AVG
                if _gap["days"] and _mc_gap_today < _min_today:
                    log_manager.system(
                        f"[경보] mc-conf 괴리: 금일 진입후보(conf≥mc) {_mc_gap_today}분"
                        f" < 하한 {_min_today}분 — 최근 {_gap['lookback_days']}거래일 평균"
                        f" {_gap['avg']:.0f}분/일. mc는 자동 조정하지 않음(사용자 판단 필요).",
                        "WARNING",
                    )
                elif _gap["days"] and _gap["avg"] < _min_avg:
                    log_manager.system(
                        f"[경보] mc-conf 괴리: 최근 {_gap['lookback_days']}거래일 평균"
                        f" 진입후보 {_gap['avg']:.0f}분/일 < 하한 {_min_avg}분 — 금일 {_mc_gap_today}분.",
                        "WARNING",
                    )
                else:
                    logger.info(
                        "[mc-conf gap] 정상: 금일 %d분, %d일 평균 %.0f분",
                        _mc_gap_today, _gap["lookback_days"], _gap.get("avg", 0.0),
                    )
        except Exception as _mcg_e:
            logger.warning("[mc-conf gap] 계산 실패 (스킵): %s", _mcg_e)

        # [Phase2] StrategyRegistry — 라이브 일별 스냅샷 기록
        # registry.is_current를 유일한 활성 버전 소스로 사용 (PARAM_HISTORY[-1]과
        # 별도로 갈라지면 스냅샷이 엉뚱한 버전에 쌓여 daily_exporter가 실거래
        # 실적을 못 찾는 "1일차 고정" 버그가 재발함 — docs/MW0601 참고)
        try:
            from config.strategy_registry import get_registry as _get_reg
            _cur_ver_info = _get_reg().get_current_version()
            _active_ver = _cur_ver_info["version"] if _cur_ver_info else "v1.0"
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

        # [304차 후속] daily_close()는 백그라운드 스레드 실행 — 아래 두 메서드는 내부에서
        # 대시보드 위젯을 직접 건드리므로 메인 스레드로 위임한다.
        _daily_close_ui_sig.request.emit(self._refresh_pnl_history)
        _trend_stats = self._gather_trend_stats()  # DB 조회 — Qt 미사용, 백그라운드에서 계산해도 안전
        _daily_close_ui_sig.request.emit(
            lambda _ts=_trend_stats: self.dashboard.update_trend(_ts)
        )

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
                extra_stats={
                    "checklist_conf_fail": _ccf_today,
                    "mc_gap_today": _mc_gap_today,
                    "mc_gap_avg": _mc_gap_avg,
                }
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

        # [303차] 오래된 거래소 CB halt 이력 정리 (30일 초과분 삭제)
        try:
            from utils.db_utils import purge_old_exchange_cb_halts
            purge_old_exchange_cb_halts(keep_days=30)
        except Exception as _pech_e:
            logger.warning("[ExchangeCB] halt 이력 정리 실패 (무해): %s", _pech_e)

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
        retrain_str = (
            "재학습: 완료 (스케줄러)"
            if getattr(self, "_eod_retrain_ok", False)
            else "재학습: 미완료 (내일 PreRetrain 보완)"
        )
        win_rate = stats["wins"] / max(stats["trades"], 1)
        gross_sign = "+" if stats["gross_krw"] >= 0 else ""
        pnl_sign = "+" if stats["pnl_krw"] >= 0 else ""
        notify(
            f"🏁 미륵이 일일 마감 완료 — 자동 종료 예정\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"거래: {stats['trades']}회 (승 {stats['wins']} / 패 {stats['losses']})  "
            f"승률: {win_rate:.0%}\n"
            f"총손익: {gross_sign}{stats['gross_krw']:,.0f}원  "
            f"(수수료 -{stats['commission']:,.0f}원)\n"
            f"순손익: {pnl_sign}{stats['pnl_krw']:,.0f}원\n"
            f"{retrain_str}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"15초 후 프로그램 자동 종료\n"
            f"다음 시작: 내일 08:45 이후",
            "INFO",
        )
        # WaitDC 마커 — retrain_eod.py가 daily_close 완료를 감지하는 전용 파일.
        # _exit_normally는 launcher가 읽은 직후 삭제하므로 EOD 재학습(16:10)이 항상 놓쳤음.
        # 이 파일은 launcher가 건드리지 않으므로 retrain_eod.py가 안정적으로 감지 가능.
        try:
            _dc_marker = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data",
                f"daily_close_done_{datetime.date.today().strftime('%Y%m%d')}.txt",
            )
            with open(_dc_marker, "w", encoding="utf-8") as _f:
                _f.write(datetime.datetime.now().isoformat() + "\n")
        except Exception as _dcm_e:
            logger.warning("[DailyClose] WaitDC 마커 기록 실패 (무해): %s", _dcm_e)

        # [233차] DailyClose 완료 즉시 _exit_normally 플래그 생성.
        # _auto_shutdown()은 Qt 타이머(15초 지연) 경유로 생성하므로
        # 타이머 미실행·예외 시 플래그가 누락돼 런처가 재시작을 시도하는 버그 방지.
        # 다음날 08:40 스케줄러 자동 시작 시 GUARD 취소 근본 원인 차단.
        self._write_exit_normally_flag("daily_close")
        # 종료 예약은 메인 Qt 스레드에서 수행 (QueuedConnection → _schedule_shutdown 에서 처리)
        _shutdown_sig.request.emit()

    def _on_code_change_restart_requested(self) -> None:
        """[234차] 종목변경 재시작 배지 클릭 → 포지션·시각 안전 조건 확인 후 재시작.

        안전 조건:
          ① 포지션 FLAT — 보유 중이면 청산 코드 불일치 위험
          ② 15:10 이전 — 이후는 오버나이트 방지 원칙
        조건 충족 시 _exit_normally 파일 없이 quit() → AUTO-RESTART 루프 재시작.
        """
        from PyQt5.QtWidgets import QMessageBox as _MB
        _now = datetime.datetime.now()
        if self.position.status != "FLAT":
            _MB.warning(
                None,
                "재시작 불가 — 포지션 보유 중",
                f"현재 {self.position.status} {self.position.quantity}계약 보유 중입니다.\n"
                "포지션을 청산한 뒤 재시작 버튼을 클릭하세요.",
            )
            return
        if _now.time() >= datetime.time(15, 10):
            _MB.warning(
                None,
                "재시작 불가 — 15:10 이후",
                "15:10 이후 재시작은 오버나이트 방지 원칙에 따라 허용되지 않습니다.\n"
                "내일 기동 시 자동 반영됩니다.",
            )
            return
        _active  = getattr(self, "_futures_code", "?")
        _selected = self.dashboard.get_selected_symbol()
        # 전환 전후 스펙 비교 — 경고 내용 구성
        try:
            from config.constants import get_contract_spec as _gcs
            _spec_a = _gcs(_active)
            _spec_s = _gcs(_selected)
            _label_a = _spec_a["label"]   # "미니선물" / "일반선물"
            _label_s = _spec_s["label"]
            _tick_a  = _spec_a["tick_size"]
            _tick_s  = _spec_s["tick_size"]
            _pt_a    = _spec_a["pt_value"]
            _pt_s    = _spec_s["pt_value"]
        except Exception:
            _label_a = _label_s = "?"
            _tick_a = _tick_s = _pt_a = _pt_s = 0

        _tick_warn = (
            f"\n• 틱 사이즈 변경: {_tick_a}pt → {_tick_s}pt\n"
            f"  (spread_ticks 기준이 변경됩니다)"
            if _tick_a != _tick_s else ""
        )
        _pt_warn = (
            f"\n• pt_value 변경: {_pt_a:,}원 → {_pt_s:,}원\n"
            f"  (포지션 손익·사이즈 계산 기준이 변경됩니다)"
            if _pt_a != _pt_s else ""
        )

        _msg = (
            f"현재: {_active}  ({_label_a})\n"
            f"변경: {_selected}  ({_label_s})\n"
            f"\n"
            f"[전환 후 주의사항]\n"
            f"• 첫 1~2시간은 spread_ticks·toxicity가\n"
            f"  이전 종목 기준으로 계산될 수 있습니다.{_tick_warn}{_pt_warn}\n"
            f"• 학습 DB(raw_candles)에 이전 종목 데이터가 섞여\n"
            f"  GBM 재학습 품질이 일시 저하될 수 있습니다.\n"
            f"• 실투자 전환 전 모의투자에서 1주일 이상 검증을\n"
            f"  권장합니다.\n"
            f"\n재시작하시겠습니까?"
        )
        from PyQt5.QtWidgets import QMessageBox as _MB2
        ret = _MB2.question(
            None,
            "종목변경 재시작 확인",
            _msg,
            _MB2.Yes | _MB2.No,
            _MB2.No,
        )
        if ret != _MB2.Yes:
            return

        log_manager.system(
            f"[SymbolChange] 종목변경 재시작 확정 — "
            f"{_active}({_label_a}) → {_selected}({_label_s}) "
            f"포지션=FLAT 시각={_now.strftime('%H:%M')}",
            "INFO",
        )
        # _exit_normally 미생성 → AUTO-RESTART 루프가 재시작 처리
        _qt_app.quit()

    def _apply_dashboard_call(self, fn) -> None:
        """[304차 후속] DailyClose 스레드가 emit()한 대시보드 갱신을 메인 스레드에서 대신 실행.

        _daily_close_ui_sig.request 시그널(QueuedConnection)을 통해 호출되므로
        DailyClose 스레드에서 emit() 해도 이 메서드는 메인 이벤트 루프에서 실행된다.
        """
        try:
            fn()
        except Exception as _dc_ui_e:
            logger.warning("[DailyCloseUI] 대시보드 갱신 실패: %s", _dc_ui_e)

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
        self._write_exit_normally_flag("auto_shutdown")
        _qt_app.quit()

    def _write_exit_normally_flag(self, reason: str = "user_close") -> None:
        """정상 종료 플래그 파일 생성 — 런처 RESTART_LOOP 재시작 방지.

        [229차] UI X 버튼·자동 종료 등 의도된 종료 시 생성.
        런처(start_mireuk_Cybos.bat)가 이 파일을 감지하면 AUTO-RESTART 건너뜀.
        → X 버튼 후 스케줄러 클릭으로 인한 이중 인스턴스 방지.
        """
        try:
            _flag = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "_exit_normally")
            with open(_flag, "w", encoding="utf-8") as _f:
                import datetime as _dt
                _f.write(f"{reason}\n{_dt.datetime.now().isoformat()}\n")
            logger.info("[Shutdown] 정상 종료 플래그 기록: %s (%s)", _flag, reason)
        except Exception as _e:
            logger.warning("[Shutdown] 정상 종료 플래그 기록 실패 (무해): %s", _e)

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
        # [228차] elapsed_s 는 워치독 타이머 기반(복구 스킵으로 리셋될 수 있음)이므로
        # _last_real_pipeline_dt 기반 실 경과 시간을 ExchangeCB 감지의 우선 기준으로 사용.
        _real_gap = (
            (datetime.datetime.now() - self._last_real_pipeline_dt).total_seconds()
            if self._last_real_pipeline_dt else elapsed_s
        )
        _ecb_trigger_s = max(elapsed_s, _real_gap)

        if _ecb_trigger_s >= 300:
            if not self._exchange_cb_mode:
                self._exchange_cb_mode = True
                self._exchange_cb_start = datetime.datetime.now()
                _ecb_resume_est_300 = (
                    self._exchange_cb_start + datetime.timedelta(minutes=30)
                ).strftime("%H:%M")
                msg = (
                    f"[ExchangeCB] 분봉 {elapsed_str} 미수신 (실경과={int(_real_gap)}s) — "
                    f"거래소 CB/단일가 구간 추정. 복구 시도 중단, 재개 대기 모드 진입 "
                    f"(예상 재개 ≈ {_ecb_resume_est_300})"
                )
                log_manager.system(msg, "WARNING")
                notify(
                    f"⏸ 미륵이 거래소 CB 대기 — {elapsed_str} 분봉 미수신\n"
                    f"예상: 20분 중단→10분 단일가→정규매매 재개 ≈ {_ecb_resume_est_300}"
                )
                self.shadow_session.mark_exchange_cb(True)
                # [227차] CB⑤ 임계 완화 — CB 모드 중 파이프라인 지연 오발동 방지
                self.circuit_breaker.set_gbm_retrain_active(True)
                try:
                    self.dashboard.update_exchange_cb_badge("CB_ACTIVE", resume_est=_ecb_resume_est_300)
                except Exception:
                    pass
            else:
                # CB 모드 중 — 30분마다 생존 알림 (30분=KRX CB 총 중단 시간이므로 재개 임박 메시지 포함)
                _gap_min = int(
                    (datetime.datetime.now() - self._exchange_cb_start).total_seconds() / 60
                ) if self._exchange_cb_start else m
                if _gap_min > 0 and _gap_min % 30 == 0 and s < 60:
                    _resume_msg = "재개 임박 — 분봉 수신 즉시 자동 복구" if _gap_min == 30 else "분봉 재개 시 자동 복구"
                    notify(f"⏸ 거래소 CB 대기 중 {_gap_min}분 — {_resume_msg}")
            return  # CB 모드 중에는 _try_pipeline_recovery 절대 호출 안 함

        if elapsed_s >= 240:
            # [ExchangeCB 조기 감지] Cybos 서버 연결이 정상인데 분봉이 4분 이상 미수신
            # → 네트워크/API 문제가 아니라 거래소 서킷브레이커로 판단하고 CB 모드 즉시 진입.
            # 연결 이상이면 기존 긴급 복구 로직을 그대로 실행.
            try:
                _broker_connected = bool(self.broker.is_connected)
            except Exception:
                _broker_connected = False

            if _broker_connected and not self._exchange_cb_mode:
                self._exchange_cb_mode = True
                self._exchange_cb_start = datetime.datetime.now()
                _ecb_resume_est = (
                    self._exchange_cb_start + datetime.timedelta(minutes=30)
                ).strftime("%H:%M")
                msg = (
                    f"[ExchangeCB] 분봉 {elapsed_str} 미수신 (실경과={int(_real_gap)}s) + "
                    f"Cybos 연결 정상 → 거래소 CB/단일가 구간 조기 확정. "
                    f"복구 시도 중단, 재개 대기 모드 진입 "
                    f"(KRX: 20분 중단+10분 단일가, 예상 재개 ≈ {_ecb_resume_est})"
                )
                log_manager.system(msg, "WARNING")
                notify(
                    f"⏸ 미륵이 거래소 CB 감지 — {elapsed_str} 미수신\n"
                    f"예상: 20분 중단→10분 단일가→정규매매 재개 ≈ {_ecb_resume_est}"
                )
                self.shadow_session.mark_exchange_cb(True)
                self.circuit_breaker.set_gbm_retrain_active(True)
                try:
                    self.dashboard.update_exchange_cb_badge("CB_ACTIVE", resume_est=_ecb_resume_est)
                except Exception:
                    pass
            elif not _broker_connected:
                msg = (f"⛔ 파이프라인 {elapsed_str} 미실행 — 원인 불명. 긴급 복구 시도 중  "
                       f"가능한 원인: ① API 무응답 ② on_candle_closed 미호출 "
                       f"③ STEP 내 예외 누락 ④ 장외 시간")
                log_manager.system(msg, "WARNING")
                notify(f"🚨 미륵이 파이프라인 {elapsed_str} 정지 — 긴급 복구 시도")
                QTimer.singleShot(300, self._try_pipeline_recovery)

        elif _ecb_trigger_s >= 150:
            msg = (f"⚠ 파이프라인 {elapsed_str} 미실행 (실경과={int(_real_gap)}s) — 분봉 수신 또는 API 상태 이상  "
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
        self.shadow_session.mark_exchange_cb(False)
        self.shadow_session.force_live(reason=f"exchange_cb_resume gap={gap_min}m")

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

        # ⑥ [227차] GBM 재학습 트리거 — KOSPI CB 후 가격레벨·변동성·구조 전면 변화
        # 스케일러 재적합(④)만으론 GBM 트리 구조가 유지돼 구형 시장 패턴 그대로 적용.
        # CB 재개 후 최우선 재학습 — acc30m 버퍼가 비어있어 CB③ 재발동도 방지됨.
        if not getattr(self, "_gbm_retrain_running", False):
            self._start_gbm_retrain_subprocess(
                force=True,
                reason=f"ExchangeCB_{gap_min}분_재개",
                is_warmup=False,
                intraday=True,
            )
            log_manager.system(
                f"[ExchangeCB] GBM 재학습 예약 — CB {gap_min}분 공백 후 시장 구조 변화 대응",
                "INFO",
            )
        else:
            log_manager.system(
                "[ExchangeCB] GBM 재학습 스킵 — 이미 진행 중",
                "INFO",
            )

        # ⑦ [227차] CB③ 쿨다운 강화 — CB 재개 직후 시장이 불안정하여 즉시 재HALT 위험
        # 기본 reset_acc30m_buffer()의 쿨다운(15샘플)보다 2배 강화 (30샘플)
        self.circuit_breaker._cb3_reset_cooldown_samples = max(
            getattr(self.circuit_breaker, "_cb3_reset_cooldown_samples", 0), 30
        )
        log_manager.system(
            "[ExchangeCB] CB③ 쿨다운 강화 → 30샘플 전 CB③ 재발동 억제",
            "INFO",
        )

        # ⑧ [227차] ExchangeCB 해제 직후 CB⑤ 파이프라인 지연 임계 완화
        # CB 재개 첫 분봉: 스케일러 재적합·GBM 재학습·앙상블 복구 중첩 → 파이프라인 과중
        # GBM 재학습 중 CB⑤ 완화(set_gbm_retrain_active=True)가 이미 적용되므로 추가 불필요.
        # 단, 워치독 리셋: CB 해제 직후 watchdog이 즉시 경보하지 않도록 파이프라인 타이머 리셋
        self.dashboard.notify_pipeline_ran()

        # ⑨ CB 해제 후 관망 기간 — 극단 변동성 구간에서 신규 진입 차단
        # CB 재개 직후는 반등/급락이 과격해 1분봉 모델 예측 신뢰 불가.
        # GBM 재학습·스케일러 재적합이 완료되기 전 진입도 방지.
        # KRX CB 구조: 20분 거래 중단 → 10분 단일가매매 = 30분 총 블랙아웃.
        # 단일가매매 시작과 동시에 분봉이 도착하는 경우에도 단일가 10분 전체를 커버하려면 10분 필요.
        _ECB_OBSERVE_MIN = 10
        self._ecb_observation_until = (
            datetime.datetime.now() + datetime.timedelta(minutes=_ECB_OBSERVE_MIN)
        )
        log_manager.system(
            f"[ExchangeCB] 관망 기간 설정 — {_ECB_OBSERVE_MIN}분 신규 진입 차단 "
            f"(단일가매매 커버, 해제: {self._ecb_observation_until.strftime('%H:%M')})",
            "INFO",
        )

        log_manager.system(
            f"[ExchangeCB] 재개 초기화 완료 | gap={gap_min}m | "
            f"ShadowLIVE/acc리셋/앙상블리셋/스케일러재적합/쿨다운리셋/GBM재학습예약/관망{_ECB_OBSERVE_MIN}분",
            "INFO",
        )
        try:
            self.dashboard.update_exchange_cb_badge(
                "OBSERVING", until_dt=self._ecb_observation_until
            )
        except Exception:
            pass

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

        # 동일 분봉 반복 재처리 방지 — 이미 복구한 ts면 스킵
        if ts_str == self._last_recovery_ts:
            # [228차] notify_pipeline_ran() 제거 — 워치독 타이머를 리셋하지 않음.
            # 이전 코드: notify_pipeline_ran() → elapsed_s가 항상 90s로 고착 → ExchangeCB 미발동.
            # 수정 후: 워치독이 실제 경과 시간 누적 → 300s 도달 시 ExchangeCB 정상 진입.
            _real_elapsed = (
                datetime.datetime.now() - self._last_real_pipeline_dt
            ).total_seconds() if self._last_real_pipeline_dt else 9999
            log_manager.system(
                f"[복구 스킵] {ts_str} 이미 재처리 완료 "
                f"(실 분봉 {int(_real_elapsed)}초 전) — 새 분봉 대기 중",
            )
            # 안전망: 실 분봉 없이 10분 초과 → ExchangeCB 모드 강제 진입
            if _real_elapsed > 600 and not self._exchange_cb_mode:
                self._exchange_cb_mode = True
                self._exchange_cb_start = datetime.datetime.now()
                log_manager.system(
                    f"[ExchangeCB] 복구 스킵 {int(_real_elapsed)}초 지속 — "
                    f"거래소 CB/단일가 구간 추정. 재개 대기 모드 강제 진입",
                    "WARNING",
                )
                notify(f"⏸ 미륵이 거래소 CB 대기 — 실 분봉 {int(_real_elapsed//60)}분 미수신 (강제 진입)")
                self.shadow_session.mark_exchange_cb(True)
                self.circuit_breaker.set_gbm_retrain_active(True)
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
            # [228차] 장중에 분봉이 10분 이상 없으면 거래소 CB로 판단 → ExchangeCB 진입
            if is_market_open() and not self._exchange_cb_mode:
                self._exchange_cb_mode = True
                self._exchange_cb_start = datetime.datetime.now()
                log_manager.system(
                    f"[ExchangeCB] 복구 포기({age_s}s) + 장중 → 거래소 CB 추정, 재개 대기 모드 진입",
                    "WARNING",
                )
                self.shadow_session.mark_exchange_cb(True)
                self.circuit_breaker.set_gbm_retrain_active(True)
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
        _rph_t0 = time.perf_counter()
        logger.debug("[LiveDBG] _refresh_pnl_history 시작")
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
        _rph_ms1 = (time.perf_counter() - _rph_t0) * 1000
        if _rph_ms1 > 200:
            logger.warning("[LiveDBG] _refresh_pnl_history fetch+update_pnl %.0fms", _rph_ms1)
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
        _rph_total = (time.perf_counter() - _rph_t0) * 1000
        if _rph_total > 200:
            logger.warning("[LiveDBG] _refresh_pnl_history 총 %.0fms", _rph_total)

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

        self._pre_market_done          = False
        self._pre_market_stage1_done   = False
        self._pre_market_stage2_running = False   # [359차]
        self._stage2_result            = None     # [359차]
        self._daily_close_done = getattr(self, "_daily_close_done", False)
        # preserve True restored by _restore_auto_shutdown_state() on post-market restart
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

        # [260704 감사 P2] KOSPI200 현물지수 주기 폴링 — 60초 (베이시스 계산용)
        self._kospi200_index_timer = QTimer()
        self._kospi200_index_timer.setInterval(60_000)
        self._kospi200_index_timer.timeout.connect(self._poll_kospi200_index)
        self._kospi200_index_timer.start()

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

        # [260704 감사 P1] 지정가 우선 집행 — 분봉 주기(60s)보다 짧은 타임아웃(10~15s)을
        # 봐야 하므로 전용 QTimer로 확인. LIMIT_ENTRY_FIRST_ENABLED=False면 매 tick
        # 즉시 반환하므로 평상시 오버헤드는 무시할 수준.
        self._limit_entry_timer = QTimer()
        self._limit_entry_timer.setInterval(2_000)
        self._limit_entry_timer.timeout.connect(self._check_limit_entry_timeout)
        self._limit_entry_timer.start()

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
        # exec_() 반환 후 COM 스레드·비데몬 스레드가 프로세스를 붙잡는 경우 방지
        # → sys.exit(0)으로 프로세스 확실 종료, 런처 RESTART_LOOP 정상 감지
        import sys as _sys
        _sys.exit(0)


    def _scheduler_tick(self) -> None:
        """30초마다 호출 — 장 전 준비 / 일일 마감 / 연결 감시."""
        _sched_t0 = time.perf_counter()
        now = datetime.datetime.now()
        logger.debug(
            "[LiveDBG] _scheduler_tick 시작 #%d | %s (메인 스레드 점유 시작)",
            getattr(self, "_heartbeat_count", 0) + 1,
            now.strftime("%H:%M:%S"),
        )

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
                        f" (매 영업일 필수 실행 — 30봉 단기 window로 오늘 분포 갱신)",
                        "INFO",
                    )
                    def _early_warmup_worker():
                        try:
                            # 단기 window(PRE_MARKET_SCALER_BARS=30)로 로드:
                            # 500봉은 전날 분포 위주 → 오늘 갭오픈 분포 미반영 → z경고 고착
                            # 30봉(어제 마지막 30분+오늘 pre-market)으로 오늘 비율 최대화
                            from config.settings import PRE_MARKET_SCALER_BARS as _LB
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
                    # [P1] Cybos 실시간 구독 08:45 선행 시작 — 기존 08:55에서 앞당김
                    # 프리장 봉을 08:45부터 수집 → PRE_MARKET_REFIT_STEPS 전 단계 발동 가능
                    _rd_ew = getattr(self, "realtime_data", None)
                    if _rd_ew is not None and not getattr(_rd_ew, "_running", False):
                        _rd_ew.start(load_history=True)
                        log_manager.system(
                            "[EarlyWarmup] Cybos RT 08:45 선행 구독 시작 (프리장 봉 15봉 확보)",
                            "INFO",
                        )
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
        # 08:58 이후 최초 heartbeat에서 1회 트리거. 폴백 상한 09:05로 GAP_OPEN 이내 보장.
        # [359차] macro(순차 requests 최대 5회)+investor(COM BlockRequest 폴링) fetch가
        # 3~4초대 메인스레드 정체를 일으켜(0720 정기점검 관측) 백그라운드 스레드로 이관.
        # 결과 적용(Qt 위젯)은 fetch 완료 후 다음 하트비트 틱에서 메인스레드가 수행.
        if (
            getattr(self, "_pre_market_stage1_done", False)
            and not self._pre_market_done
            and not getattr(self, "_pre_market_stage2_running", False)
            and is_trading_day(now)
            and datetime.time(8, 58) <= now.time() < datetime.time(9, 5)
        ):
            self._pre_market_stage2_running = True
            threading.Thread(target=self._pre_market_stage2_fetch, daemon=True).start()

        _s2_result = getattr(self, "_stage2_result", None)
        if _s2_result is not None:
            self._pre_market_stage2_apply(_s2_result)
            self._stage2_result = None
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
                    self._pre_market_done          = False
                    self._pre_market_stage1_done   = False
                    self._pre_market_stage2_running = False   # [359차]
                    self._stage2_result            = None     # [359차]
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
                    self._sync_from_broker_via_scheduler = True
                    try:
                        _ts_sync_position_from_broker(self)
                    finally:
                        self._sync_from_broker_via_scheduler = False
                # 장 시작 후에도 sync 차단이 지속되면 CRITICAL 슬랙 알림 (1회)
                if not getattr(self, "_broker_sync_critical_notified", False):
                    self._broker_sync_critical_notified = True
                    notify_broker_sync_blocked(self._broker_sync_last_error)

            # 장중 롤오버 감시 — 60 tick(30분)마다 근월물 재확인
            # 롤오버가 감지되면 WARNING 로그 + UI 갱신만 수행; 재구독은 재기동 시 자동 처리
            if self._heartbeat_count % 60 == 0 and not getattr(self, "_rollover_detected", False):
                if self.broker_runtime_service.check_rollover(self):
                    self._rollover_detected = True  # 이후 반복 알림 억제

        _sched_elapsed_ms = (time.perf_counter() - _sched_t0) * 1000
        if _sched_elapsed_ms > 1000:
            logger.warning(
                "[LiveDBG] _scheduler_tick 지연 %.0fms #%d — "
                "메인 스레드 %.0fms 점유 (live 중단 원인 후보)",
                _sched_elapsed_ms, self._heartbeat_count, _sched_elapsed_ms,
            )
        else:
            logger.debug(
                "[LiveDBG] _scheduler_tick 완료 %.0fms #%d",
                _sched_elapsed_ms, self._heartbeat_count,
            )

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
        protect_mode = str(getattr(self, "_tp1_protect_mode", "atr_profit") or "atr_profit").strip().lower()
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
        _syn_pnl = protect.get("synthetic_tp1_pnl_pts")
        _syn_frac = protect.get("synthetic_tp1_fraction")
        self.dashboard.append_pnl_log(
            f"TP1 보호전환 | {self.position.status} 1계약 @ {price:.2f}",
            f"{protect_mode} | stop {protect['prev_stop_price']:.2f} -> {protect['new_stop_price']:.2f}"
            + (f" | 회계상 확정 {_syn_frac:.0%} {_syn_pnl:+.2f}pt(물리 미체결)"
               if _syn_pnl is not None else ""),
        )
        # [339차 후속] 회계적 분할청산(synthetic partial) 기록 — signal_decay_exits와
        # 동일하게 리포트 전용 계측 테이블일 뿐 실거래 의사결정(CB/Kelly/사이징)에는
        # 절대 반영하지 않는다. 아직 물리적으로 열려 있는 1계약의 리스크 노출은
        # 위 stop 이동(atr_profit 등)이 유일한 실제 관리 수단이며, 이 INSERT는 그
        # 판단이 "TP1까지는 왔었다"는 사후 분석용 사실 기록일 뿐이다.
        try:
            execute(
                TRADES_DB,
                """INSERT INTO synthetic_partial_exits
                   (ts, entry_ts, direction, entry_price, synthetic_price,
                    synthetic_fraction, synthetic_pnl_pts, protect_mode, stop_after)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                    (self.position.entry_time.strftime("%Y-%m-%d %H:%M:%S")
                     if self.position.entry_time else None),
                    self.position.status,
                    float(self.position.entry_price),
                    float(protect.get("synthetic_tp1_price") or price),
                    float(_syn_frac or 0.0),
                    float(_syn_pnl or 0.0),
                    protect_mode,
                    float(protect["new_stop_price"]),
                ),
            )
        except Exception as _spe:
            logger.warning("[SyntheticPartial] 기록 실패 (무해): %s", _spe)
        # [363차 후속, 0721 딥다이브 제안4 편입] qty=1 TP1 이후 트레일 폭 섀도 —
        # 361차 tp2_hold_shadow와 같은 패턴(발동 시점 상태 기록 → 주간 리포트가
        # compute_trailing_stop_tier로 사후 시뮬레이션). qty=1은 TP1 이후 4단계
        # 트레일링(update_trailing_stop) 대신 이 static ATR-lock 1회 보호전환만
        # 받는데, 그 정적 보호가 이후 되돌림에 너무 타이트한지(0721 딥다이브: 승리
        # 3건이 TP1 직후 곧바로 보호손절가로 되돌아온 패턴 반복)를 "그때부터 qty=2와
        # 동일한 4단계 트레일링을 계속 적용했다면"과 실현치를 대조해 계측한다.
        self._record_tp1_trail_shadow(price, atr, protect, protect_mode)
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

    # [361차] TP2 홀드 A/B 섀도우 — qty=2 포지션이 TP2에서 잔량 1계약을 100% 종료하는
    # 순간, "이 계약을 홀드해서 TP3/트레일링까지 갔다면 어땠을까"를 counterfactual로
    # 기록한다. 실제 주문(아래 _send_broker_exit_order)은 그대로 실행 — 실거래 영향 없음.
    # 근거: 0720 정기점검 TP3 도달 0건 딥다이브(트레일링 아니라 qty 사이징 구조가 원인).
    if stage == 2 and is_full_close and total_qty == 2:
        try:
            execute(
                TRADES_DB,
                """INSERT INTO tp2_hold_shadow
                   (ts, direction, entry_price, tp2_price, tp3_price, stop_price_at_hook,
                    atr_at_hook, grade, entry_horizon)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                    self.position.status,
                    float(self.position.entry_price),
                    float(price),
                    float(self.position.tp3_price),
                    float(self.position.stop_price),
                    float(_ts_get_reference_atr(self)),
                    self.position.grade,
                    self.position.entry_horizon,
                ),
            )
        except Exception as _t2h_e:
            logger.warning("[TP2HoldShadow] 기록 실패 (무해): %s", _t2h_e)

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


def _ts_record_tp1_trail_shadow(self, price: float, atr: float, protect: dict, protect_mode: str) -> None:
    """[363차 후속] qty=1 TP1 이후 트레일 폭 섀도 기록 — hurst_gate_shadow/
    tp2_hold_shadow와 동일 패턴(발동 시점 상태만 기록, 실거래 액션 없음).

    resolve_and_eval_tp1_trail_shadow()가 compute_trailing_stop_tier()로 "그때부터
    qty=2와 동일한 4단계 트레일링을 계속 적용했다면"을 사후 시뮬레이션하고, entry_ts
    조인으로 실거래 실현 pnl_pts와 대조한다.
    """
    try:
        execute(
            TRADES_DB,
            """INSERT INTO tp1_trail_shadow
               (ts, entry_ts, direction, entry_price, tp1_price,
                protect_stop_at_hook, atr_at_hook, protect_mode, grade, entry_horizon)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                (self.position.entry_time.strftime("%Y-%m-%d %H:%M:%S")
                 if self.position.entry_time else None),
                self.position.status,
                float(self.position.entry_price),
                float(price),
                float(protect["new_stop_price"]),
                float(atr),
                protect_mode,
                self.position.grade,
                self.position.entry_horizon,
            ),
        )
    except Exception as _t1t_e:
        logger.warning("[Tp1TrailShadow] 기록 실패 (무해): %s", _t1t_e)


def _ts_record_exit_fill_slippage(self, pending: dict, fill_price: float) -> None:
    """[369차, 0723 정기점검 딥다이브] 청산 주문 체결 슬리피지 계측 — 검증캠페인
    §17 exit_fill_slippage_watch. 순수 계측 채널, 정책/실거래 판단에 관여하지 않음.

    price_hint(주문 전송 시점 의도가 — 손절가/목표가)와 실제 체결가(fill_price)의
    괴리를 방향 보정해 기록한다. 계기: 0723 유일 거래에서 TP1 ATR보호전환
    (+0.35pt 확정 예정)이 체결 슬리피지(price_hint=1122.49 → fill=1122.12,
    0.37pt≈18틱 불리)로 순손실(-0.02pt)로 뒤집힘 — VALIDATION_CAMPAIGN 전 채널의
    왕복비용 계산이 가정하는 slippage_ticks_per_side=1.0(0.02pt)과 실측 간
    괴리 가능성을 처음 발견, 실측치를 쌓기 위해 신설.

    direction은 "청산 대상 포지션"의 방향(LONG/SHORT, pending["direction"])이지
    주문 매수/매도 방향이 아니다 — LONG 청산(매도)은 fill < price_hint가 불리,
    SHORT 청산(매수)은 fill > price_hint가 불리하므로 부호를 반대로 계산한다.
    """
    try:
        direction = str(pending.get("direction") or "").strip().upper()
        price_hint = float(pending.get("price_hint") or 0.0)
        if direction not in ("LONG", "SHORT") or price_hint <= 0 or fill_price <= 0:
            return
        slippage_pts = (
            (price_hint - fill_price) if direction == "LONG"
            else (fill_price - price_hint)
        )
        entry_ts = (
            self.position.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            if getattr(self.position, "entry_time", None) else None
        )
        execute(
            TRADES_DB,
            """INSERT INTO exit_fill_slippage
               (ts, entry_ts, direction, reason, price_hint, fill_price, slippage_pts)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                entry_ts,
                direction,
                str(pending.get("reason") or ""),
                round(price_hint, 2),
                round(float(fill_price), 2),
                round(slippage_pts, 4),
            ),
        )
    except Exception as _efs_e:
        logger.warning("[ExitFillSlippage] 기록 실패 (무해): %s", _efs_e)


def _ts_execute_loss_tier1_exit(self, price: float) -> None:
    """[360차] 손절 계단화 1차 — entry~stop 절반 지점 조기 축소 주문 전송.

    _ts_execute_partial_exit(TP1/2/3)와 같은 뼈대(pending 선등록 → 주문 → 실패 시
    롤백)이나 kind="EXIT_LOSS_TIER1"로 별도 처리한다 — EXIT_PARTIAL로 보내면
    _ts_handle_exit_fill()의 stage 기반 partial_N_done 강제설정과 _post_partial_exit()의
    stage==1 손익분기 이동(이익 전제)이 손실 케이스에 오적용된다.
    """
    if self._has_pending_order():
        return
    cut_qty = self.position.get_loss_tier1_exit_qty()
    if cut_qty <= 0:
        return
    direction = self.position.status
    self._set_pending_order(
        kind="EXIT_LOSS_TIER1",
        direction=direction,
        qty=cut_qty,
        price_hint=round(price, 2),
        reason="손절1차 조기축소",
    )
    ret = self._send_broker_exit_order(cut_qty)
    log_manager.system(
        f"[ExitSendOrderResult] ret={ret} kind=손절1차 direction={direction} qty={cut_qty}",
        "WARNING",
    )
    if ret == 0:
        log_manager.trade(
            f"[주문요청] 손절1차 조기축소 {direction} {cut_qty}계약 @ {price} 체결대기"
        )
    else:
        self._clear_pending_order()
        log_manager.system(f"[Exit] 손절1차 주문 실패 ret={ret}", "ERROR")


def _ts_record_loss_tier1_qty1_shadow(self, price: float) -> None:
    """[363차] qty=1 손실1차 섀도 — hurst_gate_shadow/joint_gate_shadow/open_gap_shadow/
    tp2_hold_shadow와 동일한 패턴(발동 시점 상태만 기록 → 주간 리포트가 사후 판정).

    is_loss_tier1_hit()는 qty<=1을 물리적 분할 불가로 원천 제외하는데, "그 시점에
    전량 조기청산했다면"의 counterfactual은 여기서 계측만 한다 — 실제 청산 액션은
    전혀 없다(entry~stop 전체 폭 그대로 유지, 기존 동작 무변경). 실거래 pnl_pts는
    trades 테이블에 이미 별도로 쌓이므로, resolver(generate_validation_campaign_report.py)가
    entry_ts로 조인해 "조기청산 vs 실제 결과"를 사후 비교한다 — tp2_hold_shadow처럼
    별도 캔들 시뮬레이션이 불필요(포지션이 실제로 계속 진행되므로 실현치를 그대로 대조).
    """
    self.position.loss_tier1_qty1_shadow_logged = True
    try:
        execute(
            TRADES_DB,
            """INSERT INTO loss_tier1_qty1_shadow
               (ts, entry_ts, direction, entry_price, loss_tier1_price, stop_price,
                grade, entry_horizon, cf_outcome, cf_exit_price,
                quantile_expected_pt, quantile_uncertainty_pt)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                (self.position.entry_time.strftime("%Y-%m-%d %H:%M:%S")
                 if self.position.entry_time else None),
                self.position.status,
                float(self.position.entry_price),
                float(self.position.loss_tier1_price),
                float(self.position.stop_price),
                self.position.grade,
                self.position.entry_horizon,
                "EARLY_CUT",
                float(self.position.loss_tier1_price),
                self.position.entry_quantile_expected_pt,
                self.position.entry_quantile_uncertainty_pt,
            ),
        )
    except Exception as _lt1q1_e:
        logger.warning("[LossTier1Qty1Shadow] 기록 실패 (무해): %s", _lt1q1_e)


def _ts_record_loss_tier2_shadow(self, price: float) -> None:
    """[367차] Tier1 발동 후 잔여계약 2단계 조기청산 섀도 — loss_tier1_qty1_shadow와
    동일 패턴(발동 시점 상태만 기록 → 주간 리포트가 사후 판정). Tier1이 qty=2 중
    1계약만 잘라내고 남은 1계약은 원래 stop_price까지 그대로 노출되는 사각지대
    (0722 딥다이브 07-22 10:26 사례)를 계측한다 — 실제 청산 액션은 없다(잔여 계약은
    기존 stop_price 그대로 유지, 기존 동작 무변경).
    """
    self.position.loss_tier2_shadow_logged = True
    try:
        execute(
            TRADES_DB,
            """INSERT INTO loss_tier2_remainder_shadow
               (ts, entry_ts, direction, entry_price, loss_tier2_price, stop_price,
                remaining_qty, grade, entry_horizon, cf_outcome, cf_exit_price)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                (self.position.entry_time.strftime("%Y-%m-%d %H:%M:%S")
                 if self.position.entry_time else None),
                self.position.status,
                float(self.position.entry_price),
                float(self.position.loss_tier2_price),
                float(self.position.stop_price),
                int(self.position.quantity),
                self.position.grade,
                self.position.entry_horizon,
                "EARLY_CUT",
                float(self.position.loss_tier2_price),
            ),
        )
    except Exception as _lt2_e:
        logger.warning("[LossTier2Shadow] 기록 실패 (무해): %s", _lt2_e)


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

    # 트레일링 갱신 전 스톱을 보존 — 갱신 후 스톱을 이 봉의 과거 고저가에 소급
    # 적용하면 "유령 하드스톱"(아직 조여지지 않았던 시점의 고저가로 방금 조인
    # 스톱을 때리는 오판정)이 발생한다 (2026-07-15 #7 트레이드 딥다이브).
    _prev_stop_price = self.position.stop_price
    self.position.update_trailing_stop(price, atr)

    if self._has_pending_order():
        return

    bar_low  = bar.get("low",  price) if bar else price
    bar_high = bar.get("high", price) if bar else price
    _close_stop_hit = self.position.is_stop_hit(price)
    _intrabar_stop_hit = self.position.is_stop_hit_intrabar(
        bar_low, bar_high, stop_price=_prev_stop_price
    )
    _stop_hit_ts = _close_stop_hit or _intrabar_stop_hit
    if _stop_hit_ts:
        # 종가 히트는 방금 갱신된(최신) 스톱 기준, 봉중 히트는 그 봉 동안
        # 실제로 유효했던(갱신 전) 스톱 기준으로 청산가를 계산한다.
        _effective_stop = self.position.stop_price if _close_stop_hit else _prev_stop_price
        if self.position.status == "LONG":
            exit_price = max(_effective_stop, bar_low)
        else:
            exit_price = min(_effective_stop, bar_high)
        log_manager.system(
            f"[ExitAttempt] 하드스톱 {self.position.status} {self.position.quantity}ct "
            f"exit_price={exit_price:.2f} stop={_effective_stop:.2f} cur={price:.2f}",
            "WARNING",
        )
        _hs_qty = self.position.quantity
        _hs_direction = self.position.status
        # pending을 주문 전송 전에 먼저 등록 — BlockRequest() 내부 메시지 펌프로 체결
        # 콜백이 먼저 도착하는 race condition 방지 (수동청산·TP청산과 동일한 순서)
        self._set_pending_order(
            kind="EXIT_FULL",
            direction=_hs_direction,
            qty=_hs_qty,
            price_hint=round(exit_price, 2),  # [B50] float 오차 방지
            reason="하드스톱",
        )
        ret = self._send_broker_exit_order(_hs_qty)
        log_manager.system(
            f"[ExitSendOrderResult] ret={ret} kind=하드스톱 "
            f"direction={_hs_direction} qty={_hs_qty}",
            "WARNING",
        )
        if ret == 0:
            log_manager.trade(
                f"[주문요청] 하드스톱 청산 {_hs_direction} {_hs_qty}계약 @ {exit_price:.2f}"
            )
        else:
            self._clear_pending_order()
            log_manager.system(f"[Exit] 하드스톱 주문 실패 ret={ret}", "ERROR")
        return

    # [360차] 손절 계단화 1차 — 하드스톱(위 블록)이 우선이라 return으로 이미 빠지지
    # 않은 경우에만 평가된다. entry~stop 절반 지점 도달 시 조기 축소, 잔여는 기존
    # stop_price(전체 폭) 그대로 유지 — TP1/2/3 체크와 동일하게 _has_pending_order()로
    # 보호되므로 발동한 틱엔 아래 TP 체크가 자동으로 건너뛴다.
    if (LOSS_TIER1_ENABLED
            and not self._has_pending_order()
            and self.position.status != "FLAT"
            and self.position.is_loss_tier1_hit(price)):
        self._execute_loss_tier1_exit(price)

    # [363차] qty=1 손실1차 섀도 — is_loss_tier1_hit()가 qty<=1이라 제외하는 바로 그
    # 케이스를 계측 전용으로 기록한다(실거래 액션 없음, 순서·pending 상태와 무관).
    # 0721 딥다이브: 오늘 손실 2건 다 qty=1(대상 제외) 또는 틱 급락(항목2로 해소)이라
    # Loss Tier1이 한 번도 못 떴음 — qty=1 조기청산이 실제로 유리한지는 §9 사전등록
    # 원칙에 따라 VALIDATION_CAMPAIGN["loss_tier1_qty1_shadow"] 누적판정으로 확인한다.
    if (LOSS_TIER1_ENABLED
            and self.position.status != "FLAT"
            and self.position.is_loss_tier1_qty1_shadow_hit(price)):
        self._record_loss_tier1_qty1_shadow(price)

    # [367차] Tier1 발동 후 잔여계약 2단계 조기청산 섀도 — 0722 딥다이브에서 확인한
    # "Tier1이 qty=2 중 1계약만 자르고 남은 1계약은 원래 stop까지 무방비" 사각지대를
    # 계측 전용으로 기록(실거래 액션 없음). loss_tier1_qty1_shadow와 동일 원칙.
    if (LOSS_TIER1_ENABLED
            and self.position.status != "FLAT"
            and self.position.is_loss_tier2_shadow_hit(price)):
        self._record_loss_tier2_shadow(price)

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

    # 3.5순위: [260704 감사 P1, 339차 섀도우 복구] 신호소멸청산 counterfactual —
    # 보유 포지션과 반대 방향의 앙상블 신호가 zone_mc(시간대×호라이즌 동적 min_conf)
    # 이상 신뢰도로 확정되는 시점을 "기록"만 한다. 실제 청산은 하지 않는다(shadow-only).
    # [이력] 290차가 이 로직을 실거래 즉시청산으로 구현했으나, main.py 최하단의
    # `TradingSystem._check_exit_triggers = _ts_check_exit_triggers` 몽키패치로 이미
    # 대체돼 있던 클래스 본문 메서드에 넣는 바람에 작성 즉시 죽은 코드였고, 306차가
    # 그 죽은 코드를 정리하며 통째로 삭제 — 실제로는 단 한 번도 실행된 적이 없었다
    # (dev_memory 339차 딥다이브). signal_decay_exits 테이블 자체 주석("리포트 전용
    # 계측 테이블 — 실거래 의사결정에 관여하지 않는다", utils/db_utils.py)과
    # VALIDATION_CAMPAIGN["signal_decay"](§3-5, config/settings.py)가 애초에 shadow
    # counterfactual 전제로 사전등록돼 있었으므로, 이번 복구는 원안(즉시 실청산)이
    # 아니라 그 설계대로 기록만 되살린다. 매주 금요일 검증캠페인 리포트 [4]번 항목이
    # 자동으로 PASS/FAIL/보류를 판정하며, 실거래 반영 여부는 주간회의에서 수동 결정한다.
    if (SIGNAL_DECAY_EXIT_ENABLED
            and not self._has_pending_order()
            and self.position.status != "FLAT"
            and getattr(self, "_signal_decay_shadow_key", None) != self.position.entry_time):
        _sd_dir     = decision.get("direction", 0)
        _sd_conf    = float(decision.get("confidence", 0.0) or 0.0)
        _sd_zone_mc = float(decision.get("min_conf", 1.0) or 1.0)
        _sd_opposite = (
            (self.position.status == "LONG" and _sd_dir == -1)
            or (self.position.status == "SHORT" and _sd_dir == 1)
        )
        if _sd_opposite and _sd_conf >= _sd_zone_mc:
            debug_log.debug(
                "[SignalDecayShadow] 반대신호 감지(기록만, 실청산 없음): "
                "pos=%s dir=%d conf=%.3f zone_mc=%.3f",
                self.position.status, _sd_dir, _sd_conf, _sd_zone_mc,
            )
            try:
                execute(
                    TRADES_DB,
                    """INSERT INTO signal_decay_exits
                       (ts, direction, exit_price, stop_price, tp1_price,
                        quantity, conf, zone_mc)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00"),
                        self.position.status,
                        float(price),
                        float(self.position.stop_price or 0.0),
                        float(self.position.tp1_price or 0.0),
                        int(self.position.quantity),
                        _sd_conf,
                        _sd_zone_mc,
                    ),
                )
            except Exception as _sde:
                logger.warning("[SignalDecayShadow] counterfactual 기록 실패 (무해): %s", _sde)
            self._signal_decay_shadow_key = self.position.entry_time

    if not self._has_pending_order() and self.time_exit.should_force_exit():
        _engine_qty  = self.position.quantity
        _broker_cached = int(getattr(self, "_integrity_broker_qty", 0) or 0)
        log_manager.system(
            f"[ExitAttempt] 시간청산 status={self.position.status} "
            f"engine={_engine_qty}ct broker_cached={_broker_cached}ct price={price:.2f}",
            "WARNING",
        )
        if self.position.status != "FLAT":
            # 정상 경로: 내부 포지션 있음 — broker_cached가 더 크면 그 수량으로 청산
            _force_qty = max(_engine_qty, _broker_cached) if _broker_cached > 0 else _engine_qty
            _force_direction = self.position.status
            # pending을 주문 전송 전에 먼저 등록 — BlockRequest() 내부 메시지 펌프로 체결
            # 콜백이 먼저 도착하는 race condition 방지 (수동청산·TP청산과 동일한 순서)
            self._set_pending_order(
                kind="EXIT_FULL",
                direction=_force_direction,
                qty=_force_qty,
                price_hint=round(price, 2),  # [B50] float 오차 방지
                reason="15:10 강제청산",
            )
            ret = self._send_broker_exit_order(_force_qty)
            log_manager.system(
                f"[ExitSendOrderResult] ret={ret} kind=시간청산 "
                f"direction={_force_direction} qty={_force_qty}",
                "WARNING",
            )
            if ret == 0:
                log_manager.trade(
                    f"[주문요청] 시간청산 {_force_direction} {_force_qty}계약 @ {price:.2f}"
                )
            else:
                self._clear_pending_order()
                log_manager.system(f"[Exit] 시간청산 주문 실패 ret={ret}", "ERROR")
        elif _broker_cached > 0:
            # 폴백: 내부 FLAT이지만 broker 캐시에 잔량 → broker 직접 조회 후 청산
            log_manager.system(
                f"[ExitAttempt] 내부FLAT broker_cached={_broker_cached}계약 — BrokerDirect 청산 시도",
                "ERROR",
            )
            _ts_broker_direct_force_exit(self, price, "15:10 FLAT불일치 강제청산")

    # 5순위: 15:18 FINAL_CLOSE 안전망 — broker 직접 조회 후 잔량 무조건 청산
    if (not self._has_pending_order()
            and self.time_exit.should_final_close()
            and not getattr(self, "_final_close_done", False)):
        log_manager.system(
            f"[FinalClose] 15:18 안전망 발동 — broker 잔고 직접 조회 후 잔량 청산 price={price:.2f}",
            "ERROR",
        )
        _ts_broker_direct_force_exit(self, price, "15:18 FINAL_CLOSE 안전망")
        self._final_close_done = True


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
        "stop_move_reason": _pos.last_update_reason or "",
        "bar_low":  0.0,
        "bar_high": 0.0,
        "atr_ok":      True,
        "open_gap_ok": True,
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
        # [360차] 손절1차 조기축소는 TP 단계 진행과 무관한 수량감소이므로
        # initial_quantity도 같이 줄여 잔여 포지션의 TP1 재도달을 보존한다.
        shrink_initial=(pending["kind"] == "EXIT_LOSS_TIER1"),
    )

    # 분할체결 집계 (CB/Kelly 통계 중복 방지: 마지막 체결에서만 반영)
    _ts_agg_exit_fill(pending, result, fill_price, fill_qty)
    is_last_fill = pending["filled_qty"] >= pending["qty"]

    if pending["kind"] == "EXIT_LOSS_TIER1":
        if not is_last_fill:
            log_manager.trade(
                f"[손절1차 분할체결] {result.get('direction','')} {fill_qty}계약 @ {fill_price:.2f} "
                f"| 잔여포지션={result.get('remaining', '?')}계약"
            )
            QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))
            return
        # partial_1_done은 여기서 건드리지 않는다 — apply_exit_fill(shrink_initial=True)가
        # initial_quantity도 같이 줄여놓아 _sync_partial_progress()가 정확히 계산한다.
        self.position.loss_tier1_done = True
        # [367차] Tier1 발동 후 잔여계약 2단계 조기청산 섀도 가격 계산 — 실제 체결가
        # (fill_price) 기준, "방금 체결된 tier1가 ~ 원래 stop_price" 구간의 50% 지점.
        # apply_exit_fill()이 이미 quantity를 잔여치로 줄여놓았으므로(shrink_initial=
        # True) 여기서 quantity>=1이면 잔여 포지션이 남아있다는 뜻.
        if self.position.quantity >= 1:
            self.position.loss_tier2_price = (
                fill_price
                + (self.position.stop_price - fill_price)
                * runtime_settings.LOSS_TIER1_STOP_FRACTION
            )
        agg_result = _ts_build_agg_exit_result(result, pending)
        self._post_loss_tier1_exit(agg_result)
        QTimer.singleShot(800, lambda: _ts_refresh_dashboard_balance(self))
        return

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
        # [311차 후속] pending 미등록 상태로 들어온 체결 → 306차 이전 근본원인
        # 재발 시 사후 식별 가능하도록 유령 진입으로 명시 태깅.
        self._entry_source = "GHOST_PENDING_MISS"
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
    self._entry_source = "BROKER_SYNC_RECOVERY"
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
        # [285차-Fix2] agg_exit_pnl_pts/agg_exit_fwd_pts는 per-contract×fill_qty의 가중합
        # (_ts_agg_exit_fill, main.py:9834/9836) → qty로 나눠 per-contract 복원해야 함
        # (_ts_build_agg_exit_result의 정상 경로 main.py:9846-9853과 동일 패턴).
        # 나눗셈 누락 시 normalize_trade_pnl()이 quantity를 다시 곱해 pnl_krw가
        # quantity배로 부풀려짐 — 07-01 13:00 6계약 stuck exit에서 5배 부풀림 실측.
        _sq_pnl_pts = (
            float(pending.get("agg_exit_pnl_pts") or 0.0) / _sq_filled
            if _sq_filled > 0 else 0.0
        )
        _sq_fwd_pts = (
            float(pending.get("agg_exit_fwd_pts") or 0.0) / _sq_filled
            if _sq_filled > 0 else _sq_pnl_pts
        )
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
                    "forward_pnl_pts": _sq_fwd_pts,
                    "forward_pnl_krw": float(pending.get("agg_exit_fwd_krw") or _sq_pnl_krw),
                    "exit_reason": "stuck_exit_flat",
                    # [MW0601 딥다이브] grade는 EXIT 주문(pending)이 아니라 진입 시점
                    # self.position에서 읽어야 함 — _set_pending_order가 EXIT 생성 시
                    # grade 인자 없이 기본값 ""로 호출해 pending.get("grade")는 항상
                    # 빈값이었음(정상 청산 경로 _build_exit_result와 동일 패턴으로 통일).
                    "grade": str(getattr(self.position, "grade", "") or ""),
                    "entry_horizon": getattr(self.position, "entry_horizon", None),
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

        # [Bug1] 브로커 FLAT 확인 시 엔진 잔여 계약 PnL 계산·기록
        # Chejan 콜백 누락으로 position.quantity > 0이 남은 경우, 브로커 가격 기준으로
        # PnL을 계산하고 trades DB·TRADE 로그·PnL 탭에 기록한다.
        _rem_qty = self.position.quantity if self.position.status != "FLAT" else 0
        if _rem_qty > 0:
            _rem_exit = _sq_avg_price or float(getattr(self, "_last_pipeline_price", 0.0) or 0.0)
            if _rem_exit > 0:
                _rem_entry_ts_obj = getattr(self.position, "entry_time", None) or _sq_last_fill_at
                _rem_entry_ts_str = (
                    _rem_entry_ts_obj.strftime("%Y-%m-%d %H:%M:%S")
                    if hasattr(_rem_entry_ts_obj, "strftime") else str(_rem_entry_ts_obj)
                )
                _rem_exit_ts_str = (
                    _sq_last_fill_at.strftime("%Y-%m-%d %H:%M:%S")
                    if hasattr(_sq_last_fill_at, "strftime") else str(_sq_last_fill_at)
                )
                _rem_result = self.position.close_position(_rem_exit, "stuck_exit_remainder")
                _rem_result["entry_ts"] = _rem_entry_ts_str
                _rem_result["exit_ts"]  = _rem_exit_ts_str
                _rem_cum = self.position.daily_stats()["pnl_krw"]
                # [Bug3] TRADE 로그에 잔여 계약 처리 내용 기록
                log_manager.trade(
                    f"[잔여청산] {_rem_result['direction']} {_rem_qty}계약 @ {_rem_exit:.2f} "
                    f"PnL={_rem_result['pnl_pts']:+.2f}pt ({_rem_result['pnl_krw']:+,.0f}원) "
                    f"│ 금일누적 {_rem_cum:+,.0f}원 [브로커FLAT 추정가]"
                )
                self.dashboard.append_pnl_log(
                    f"잔여청산 | {_rem_result['direction']} {_rem_qty}계약 @ {_rem_exit:.2f}",
                    f"PnL {_rem_result['pnl_pts']:+.2f}pt  {_rem_result['pnl_krw']:+,.0f}원 (추정) │ 금일 {_rem_cum:+,.0f}원",
                )
                try:
                    self._record_trade_result(_rem_result)
                    self._refresh_pnl_history()
                except Exception as _rem_e:
                    log_manager.system(f"[StuckExit] 잔여계약 DB 기록 실패: {_rem_e}", "WARNING")
                log_manager.system(
                    f"[StuckExit] 잔여 {_rem_qty}계약 PnL 확정: "
                    f"{_rem_result['pnl_pts']:+.2f}pt ({_rem_result['pnl_krw']:+,.0f}원) @ {_rem_exit:.2f}",
                    "INFO",
                )
            else:
                log_manager.system(
                    f"[StuckExit] 잔여 {_rem_qty}계약 가격 추정 불가 "
                    f"(avg={_sq_avg_price} pipeline={getattr(self, '_last_pipeline_price', 0)}) → PnL 미계산",
                    "WARNING",
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
    self._entry_source = "BROKER_SYNC_RECOVERY"
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
        _confirm_count = pending.get("_broker_confirm_count", 0) + 1
        pending["_broker_confirm_count"] = _confirm_count
        _ts_set_broker_sync_status(self, True, f"stuck exit still holding {side} {qty} @ {avg_price}", False)
        log_manager.system(
            f"[PendingOrder] EXIT partial fill timeout -> 브로커 잔량 확인 {side} {qty} @ {avg_price:.2f}, pending 유지 "
            f"(broker_confirm={_confirm_count}/3)",
            "WARNING",
        )
        if _confirm_count >= 3:
            # 3회 연속 브로커 확인 후에도 잔량 미체결 → 시장가 주문 거래소 취소로 간주
            # _clear_pending_order()가 EXIT_PARTIAL 해소 시 자동으로 TP 재점검 스케줄 (IntrabarTPSchedule)
            log_manager.system(
                f"[PendingOrder] EXIT stuck {_confirm_count}회 브로커 확인 → "
                f"원주문(order_no={pending.get('order_no','?')}) 거래소 취소 간주, pending 소멸 후 TP 재점검",
                "CRITICAL",
            )
            self._clear_pending_order()
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
        _ts_broker_direct_force_exit(self, _force_price, "EXIT잔여 반대포지션 긴급청산")
    return True


def _ts_broker_direct_force_exit(self, price: float, reason: str = "강제청산") -> bool:
    """Cybos 잔고를 직접 조회해 남은 포지션을 시장가로 청산.

    내부 position=FLAT이지만 broker에 잔량이 남은 경우 안전망으로 사용.
    _send_broker_exit_order의 FLAT 가드를 우회해 send_market_order를 직접 호출한다.
    Returns True if an order was sent successfully.
    """
    account_no = str(_secrets.ACCOUNT_NO or "").strip()
    code = getattr(self, "_futures_code", "")
    target_code = self._normalize_broker_code(code)
    if not account_no or not target_code:
        log_manager.system(
            f"[BrokerDirectExit] account_no 또는 code 없음 — 청산 불가 reason={reason}",
            "ERROR",
        )
        return False

    result = self.broker.request_futures_balance(account_no)
    if result is None:
        log_manager.system(
            f"[BrokerDirectExit] broker balance TR 실패 — 청산 불가 reason={reason}",
            "ERROR",
        )
        return False

    rows = result.get("nonempty_rows") or result.get("rows") or []
    broker_row = None
    for row in rows:
        row_code = self._normalize_broker_code(
            row.get("종목코드") or row.get("code") or ""
        )
        if row_code == target_code:
            broker_row = row
            break

    if broker_row is None:
        log_manager.system(
            f"[BrokerDirectExit] broker 잔고 없음 → 진짜 FLAT ({reason})",
            "INFO",
        )
        return False

    def _num(v):
        try:
            return float(str(v or "").replace(",", "").strip())
        except Exception:
            return 0.0

    broker_qty = int(_num(
        broker_row.get("잔고수량") or broker_row.get("position_qty") or broker_row.get("qty")
    ))
    broker_side = _ts_order_side_to_direction({
        "balance_side":      broker_row.get("구분") or broker_row.get("매매구분"),
        "balance_side_code": broker_row.get("side_code"),
    })

    if broker_qty <= 0 or broker_side not in ("LONG", "SHORT"):
        log_manager.system(
            f"[BrokerDirectExit] 브로커 행 해석 실패 qty={broker_qty} side={broker_side} "
            f"row={broker_row} reason={reason}",
            "WARNING",
        )
        return False

    close_side = "BUY" if broker_side == "SHORT" else "SELL"
    log_manager.system(
        f"[BrokerDirectExit] {reason} — broker {broker_side} {broker_qty}계약 → {close_side} 직접주문",
        "ERROR",
    )
    ret = self.broker.send_market_order(
        account_no=account_no,
        code=code,
        side=close_side,
        qty=broker_qty,
        rqname="강제청산",
        screen_no="1001",
    )
    log_manager.system(
        f"[BrokerDirectExit] send_market_order ret={ret} {broker_side} {broker_qty}계약 reason={reason}",
        "ERROR" if ret != 0 else "WARNING",
    )
    return ret == 0


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
    if pending.get("is_limit_entry"):
        # [260704 감사 P1] 계측 — 지정가 진입의 체결 타이밍 실측 (가정 검증용, 2026-07-05)
        logger.info(
            "[LimitEntry][CHEJAN_EVENT] order_no=%s fill_qty=%d cumulative=%d/%d fill_price=%.2f t=%.3f",
            order_no, fill_qty, pending["filled_qty"], pending.get("qty", 0), fill_price, time.time(),
        )
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

    # [Bug2] 총평가수익률 = Cybos 익일예탁금(header 2) — 당일 실현손익 반영된 실시간 잔고
    # 총매매 = 예탁금(header 1) — 정적, 당일 거래로 변하지 않음
    for key in ("총평가수익률", "총매매", "추정자산"):
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


def _ts_grade_ev_guard_check(self):
    """[366차 신설] GradeEVGuard — 등급 A 롤링 실현EV 가드 판정.

    HCGuard(conf≥0.65 롤링 정확도 가드, 261차, model/ensemble_decision.py)와
    동일 원칙을 "신뢰도" 대신 "체크리스트 등급"에 적용한다. 0722 정기점검
    딥다이브: A등급 순EV가 최소 3주 지속 음수(C등급은 지속 양수)이면서 평균
    신뢰도는 A/C 거의 동일 — 신뢰도가 아니라 pass_count(등급) 자체가 원인.

    fetch_ev_by_grade() 결과를 GRADE_EV_GUARD_REFRESH_SEC 주기로 인스턴스에
    캐싱해 매분 파이프라인마다 DB를 반복 조회하지 않는다(HCGuard의 인메모리
    deque와 달리 실현 거래는 하루 몇 건뿐이라 trades.db 롤링창 집계가 더
    안정적 — 프로세스 재시작에도 값이 유지됨).

    Returns:
        (blocked, diag): blocked=True면 A등급 최근 실현EV가 임계 미달 +
        표본 충분. diag는 로그용 진단 문자열.
    """
    _now = datetime.datetime.now()
    _refresh_sec = getattr(runtime_settings, "GRADE_EV_GUARD_REFRESH_SEC", 300)
    _cache = getattr(self, "_grade_ev_guard_cache", None)
    if _cache is None or (_now - _cache["ts"]).total_seconds() >= _refresh_sec:
        from utils.db_utils import fetch_ev_by_grade
        _lookback = getattr(runtime_settings, "GRADE_EV_GUARD_LOOKBACK_DAYS", 30)
        try:
            _rows = fetch_ev_by_grade(days_back=_lookback)
            _a_row = next((r for r in _rows if r["grade"] == "A"), None)
            _cache = {
                "ts": _now,
                "a_n": int(_a_row["cnt"]) if _a_row else 0,
                "a_avg": float(_a_row["avg_net_pnl_krw"]) if _a_row else 0.0,
            }
        except Exception as _e:
            logger.debug("[GradeEVGuard] 조회 실패(무해, 다음 주기 재시도): %s", _e)
            _cache = {"ts": _now, "a_n": 0, "a_avg": 0.0}
        self._grade_ev_guard_cache = _cache

    _min_n = getattr(runtime_settings, "GRADE_EV_GUARD_MIN_N", 30)
    _thr_krw = getattr(runtime_settings, "GRADE_EV_GUARD_EV_THR_KRW", 0.0)
    _blocked = _cache["a_n"] >= _min_n and _cache["a_avg"] < _thr_krw
    _diag = "A등급 최근 %d일 n=%d 평균순EV=%.0f원" % (
        getattr(runtime_settings, "GRADE_EV_GUARD_LOOKBACK_DAYS", 30),
        _cache["a_n"], _cache["a_avg"],
    )
    return _blocked, _diag


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
        # [235차] 계약 승수: connect_broker에서 확정된 _pt_value 사용 (미니=50,000 / 일반=250,000)
        _pnl_krw = _pnl_pts * self._pt_value
        _eval_krw = _entry * _qty * self._pt_value  # 매입금액 = entry_pt × 계약수 × pt_value
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
    # 인플라이트 가드: 이미 실행 중이면 스킵 — 중첩 30s 블로킹 방지.
    # Fill → BalanceRefresh → processEvents() → 파이프라인 → 또 Fill → 또 BalanceRefresh
    # 패턴에서 두 번째 이후 호출이 중첩되면 메인스레드 60s+ 블로킹 발생.
    if getattr(self, "_balance_refresh_in_flight", False):
        log_manager.system("[BalanceRefresh] skipped: in-flight", "DEBUG")
        return
    self._balance_refresh_in_flight = True
    try:
        _ts_refresh_dashboard_balance_inner(self)
    finally:
        self._balance_refresh_in_flight = False


def _ts_refresh_dashboard_balance_inner(self) -> None:
    # 장외 시간 가드: Cybos BlockRequest가 장외에서 ~30초 타임아웃 →
    # 큐에 쌓인 singleShot이 연속 3회 실행되면 90초+ 메인 스레드 블로킹.
    # 잔고 TR은 장 중에만 의미 있으므로 장외 호출은 즉시 반환한다.
    _now_inner = datetime.datetime.now()
    if not is_market_open(_now_inner):
        logger.debug(
            "[LiveDBG] BalanceRefresh 장외 스킵 %s — BlockRequest 블로킹 방지",
            _now_inner.strftime("%H:%M:%S"),
        )
        return
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
    _br_t0 = time.perf_counter()
    logger.debug("[LiveDBG] BalanceRefresh BlockRequest 시작 (메인 스레드 점유 시작)")
    result = self.broker.request_futures_balance(account_no)
    _br_elapsed_ms = (time.perf_counter() - _br_t0) * 1000
    if _br_elapsed_ms > 1000:
        logger.warning(
            "[LiveDBG] BalanceRefresh BlockRequest 지연 %.0fms — "
            "메인 스레드 %.0fms 점유 (live 중단 원인 후보)",
            _br_elapsed_ms, _br_elapsed_ms,
        )
    else:
        logger.debug("[LiveDBG] BalanceRefresh BlockRequest 완료 %.0fms", _br_elapsed_ms)
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
    # 장외 가드: 장외 BlockRequest는 ~30초 타임아웃 → 메인 스레드 블로킹.
    # 장 시작 전 startup sync는 is_market_open 이전에 실행되므로 예외적으로 허용.
    # 스케줄러 장중 재시도 경로(is_market_open 조건 내부)에서 호출될 때만 차단.
    _now_sync = datetime.datetime.now()
    _caller_is_scheduler = getattr(self, "_sync_from_broker_via_scheduler", False)
    if _caller_is_scheduler and not is_market_open(_now_sync):
        logger.debug(
            "[LiveDBG] _ts_sync_position_from_broker 장외 스킵 %s — BlockRequest 블로킹 방지",
            _now_sync.strftime("%H:%M:%S"),
        )
        return
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
    _br_sync_t0 = time.perf_counter()
    result = self.broker.request_futures_balance(account_no)
    _br_sync_ms = (time.perf_counter() - _br_sync_t0) * 1000
    if _br_sync_ms > 500:
        logger.warning(
            "[LiveDBG] _ts_sync_position_from_broker BlockRequest %.0fms — "
            "메인 스레드 %.0fms 점유",
            _br_sync_ms, _br_sync_ms,
        )
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
                # [Bug3] blank-as-flat 강제 시 TRADE 로그 기록
                _baf_dir   = self.position.status
                _baf_qty   = self.position.quantity
                _baf_entry = self.position.entry_price
                log_manager.trade(
                    f"[BrokerSync] blank-as-flat 강제: {_baf_dir} {_baf_qty}계약 @ {_baf_entry:.2f} → FLAT "
                    f"(PnL 미계산 — 브로커 잔고 blank rows)"
                )
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

    self._entry_source = "BROKER_SYNC_RECOVERY"
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

    self._entry_source = "BROKER_SYNC_RECOVERY"
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
    hurst_bucket: str = None,
    extra_stop_mult: float = 1.0,
    quantile_expected_pt: float = None,
    quantile_uncertainty_pt: float = None,
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
    # [재발방지] ret만으로는 거부 사유를 알 수 없어 2026-07-03 10:28:59 LONG 3계약
    # 주문 거부(ret=-1) 원인을 사후 추적할 수 없었음 — 브로커가 보관한 상세
    # (status/msg = GetDibStatus/GetDibMsg1)를 함께 로그에 남긴다.
    _order_err = self.broker.get_last_order_error() if ret != 0 else None
    _order_err_suffix = (
        f" status={_order_err.get('status')} msg={_order_err.get('msg')}"
        if _order_err else ""
    )
    logger.info(
        "[Entry] send_order result ret=%s raw=%s final=%s qty=%s reverse=%s code=%s broker_sync_verified=%s%s",
        ret, raw_direction, direction, quantity, reverse_enabled,
        getattr(self, "_futures_code", ""), self._broker_sync_verified, _order_err_suffix,
    )
    log_manager.system(
        f"[EntrySendResult] ret={ret} raw={raw_direction} final={direction} qty={quantity} "
        f"reverse_entry={'ON' if reverse_enabled else 'OFF'} code={getattr(self, '_futures_code', '')}"
        f"{_order_err_suffix}",
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
            logger.error("[Entry] SendOrder 실패로 내부 포지션 오픈을 취소합니다. ret=%s%s", ret, _order_err_suffix)
            log_manager.system(
                f"[Entry] 주문 실패로 포지션 미오픈 ret={ret} raw={raw_direction} final={direction} "
                f"qty={quantity} reverse_entry={'ON' if reverse_enabled else 'OFF'}{_order_err_suffix}",
                "ERROR",
            )
            self._clear_pending_order()  # pending 롤백
            return

    # [260704 감사 P1] 지정가 우선 집행 — 주문은 접수됐지만 즉시 체결이 보장되지
    # 않으므로 낙관적 오픈을 건너뛴다. 실제 포지션 오픈은 Chejan 체결 이벤트로만
    # 반영되며(apply_entry_fill의 status==FLAT 분기가 신규 오픈 처리), 타임아웃
    # 시 QTimer(_ts_check_limit_entry_timeout)가 취소한다 — 시장가 전환 없음.
    if getattr(self, "_pending_limit_is_active", False):
        if self._pending_order is not None:
            self._pending_order["order_no"] = getattr(self, "_pending_limit_order_no", "")
            self._pending_order["is_limit_entry"] = True
        logger.info(
            "[LimitEntry] 낙관적 오픈 스킵 — Chejan 체결 대기 order_no=%s price=%s",
            getattr(self, "_pending_limit_order_no", ""), getattr(self, "_pending_limit_price", ""),
        )
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
            hurst_bucket=hurst_bucket,
            extra_stop_mult=extra_stop_mult,
            quantile_expected_pt=quantile_expected_pt,
            quantile_uncertainty_pt=quantile_uncertainty_pt,
        )
        self.position._optimistic = True
        if self._pending_order is not None:
            self._pending_order["open_position_done"] = True
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


def _ts_margin_capped_qty(self, direction: str, price: float, qty: int) -> int:
    """증거금 반영 신규주문가능수량으로 산출수량을 최종 캡핑한다.

    최대허용수량(UI 설정)을 만족해도 계좌 증거금이 부족하면 브로커가 주문을
    거부한다 (2026-07-03 10:28:59 LONG 3계약 ret=-1 사례 — 산출수량은 A급
    체크리스트를 전부 통과했지만 증거금 부족으로 SendOrder 자체가 거부됨).
    CpTd6722(선물 신규주문가능수량조회)로 실제 주문 가능 수량을 확인해
    그 이상은 애초에 산출하지 않는다.

    브로커가 조회를 지원하지 않거나(Kiwoom) 조회 자체가 실패하면 원래 qty를
    그대로 반환한다 — 최종 판정은 이 경우에도 여전히 SendOrder가 담당한다.
    """
    if qty <= 0:
        return qty
    account_no = self._get_active_account_no()
    code = getattr(self, "_futures_code", "")
    if not account_no or not code:
        return qty
    try:
        margin_info = self.broker.get_order_available_qty(account_no, code, price)
    except Exception as _mq_e:
        logger.debug("[MarginQty] 조회 예외 — 원 산출수량 유지: %s", _mq_e)
        return qty
    if not margin_info:
        return qty
    key = "buy_new_qty" if direction == "LONG" else "sell_new_qty"
    margin_qty = int(margin_info.get(key, 0) or 0)
    if margin_qty <= 0:
        log_manager.system(
            f"[MarginBlock] {direction} 신규주문가능수량=0 — 증거금 부족 추정, 진입 차단 "
            f"(산출수량={qty})",
            "WARNING",
        )
        log_manager.trade(f"[증거금부족 차단] {direction} 산출={qty}계약 → 가능=0")
        return 0
    if margin_qty < qty:
        log_manager.trade(
            f"[MarginCap] {direction} 산출={qty}계약 → 증거금상한={margin_qty}계약으로 축소"
        )
        return margin_qty
    return qty


def _ts_manual_position_restore(self, direction: str, price: float, qty: int, atr: float) -> None:
    """대시보드 '포지션 복원' 버튼 핸들러 — 모의투자 TR blank 대응."""
    from PyQt5.QtCore import QTimer as _QTimer
    atr = max(float(atr or 0.0), 0.5)
    log_manager.system(
        f"[PositionRestore] 수동 복원 요청: {direction} {qty}계약 @ {price:.2f}pt ATR={atr:.2f}",
        "WARNING",
    )
    try:
        self._entry_source = "OPERATOR_RESTORE"
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
    # open_position_done=True(정상 흐름)일 때만 진입 — qty는 open_position에서 이미 설정됨.
    # False(레이스 컨디션: BlockRequest 내 Chejan 선행)이면 else→apply_entry_fill로 qty 누적.
    if (
        pending.get("optimistic_opened")
        and pending.get("open_position_done")
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

    # [308차] Cybos CpFConclusion은 fill_no/unfilled_qty를 항상 빈값/0으로
    # 채워 반환한다(_extract_fill_payload). 그 결과 원래 dedup 키가
    # (gubun, order_no, status, filled_qty, fill_price)로 퇴화해, 다계약
    # 시장가 주문에서 "같은 가격에 1계약씩 연속 체결"되는 정상 케이스를
    # 서로 구별하지 못하고 두 번째 이후를 전부 중복으로 폐기해왔다
    # (2026-07-09 실사고 — 체결 3건 연속 유실, 진단 로그 참조:
    # dev_memory/DECISION_LOG.md 308차). position_qty(체결 시점 잔고,idx46)는
    # 체결마다 반드시 바뀌므로 키에 추가해 진짜 중복(잔고까지 동일)만 걸러낸다.
    event_key = (
        payload.get("gubun"),
        payload.get("order_no"),
        payload.get("fill_no"),
        payload.get("order_status"),
        payload.get("filled_qty"),
        payload.get("fill_price"),
        payload.get("unfilled_qty"),
        payload.get("position_qty"),
    )
    if event_key == self._last_order_event_key:
        log_manager.system(
            f"[ChejanDedup] 동일 이벤트 폐기 order_no={payload.get('order_no','?')} "
            f"key={event_key}",
            "WARNING",
        )
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

    # [308차 관측용] 브로커가 이벤트에 실어 보내는 체결 시점 잔고 스냅샷을
    # 그대로 로그에 남긴다 — 콜백 유실/중복 시 "내부 카운트 vs 브로커 잔고"
    # 대조가 가능해야 L1(잔고 기준 self-healing 대사) 설계의 실측 근거가 된다.
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
        position_qty=payload.get("position_qty"),
        closable_qty=payload.get("closable_qty"),
        sell_balance=payload.get("sell_balance"),
        buy_balance=payload.get("buy_balance"),
        balance_side_code=payload.get("balance_side_code"),
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
        # [369차] 실체결가(fill_price)와 주문 의도가(price_hint)가 아직 분리된
        # 상태일 때만 슬리피지를 계측할 수 있다 — 아래 _ts_handle_exit_fill 호출은
        # 폴백 병합값을 넘기므로 그 전에 원본 fill_price로 기록한다.
        _ts_record_exit_fill_slippage(self, pending, fill_price)
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
TradingSystem._execute_loss_tier1_exit = _ts_execute_loss_tier1_exit
TradingSystem._record_loss_tier1_qty1_shadow = _ts_record_loss_tier1_qty1_shadow
TradingSystem._record_loss_tier2_shadow = _ts_record_loss_tier2_shadow
TradingSystem._record_tp1_trail_shadow = _ts_record_tp1_trail_shadow
TradingSystem._record_exit_fill_slippage = _ts_record_exit_fill_slippage
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

    # ── [230차] faulthandler 크래시 핸들러 ────────────────────────────────
    # 목적: C 레벨 치명 예외(0xC0000409 STATUS_STACK_BUFFER_OVERRUN, SIGSEGV 등) 발생 시
    #       Python exception handler 도달 전 OS가 프로세스를 강제 종료해도
    #       logs/crash_fault.log 에 전체 스레드 Python 스택 트레이스를 기록.
    #
    # 기능:
    #   ① faulthandler.enable(all_threads=True)
    #        — 크래시 즉시 전 스레드 트레이스 덤프
    #        — Windows: AddVectoredExceptionHandler 등록 → 0xC0000409 포함 치명 예외 포착
    #   ② faulthandler.dump_traceback_later(timeout=30, repeat=True)
    #        — 30초 동안 GIL 해제 안 되면(COM BlockRequest 행 등) 주기적 트레이스 덤프
    #        — 15:09 크래시 재현 시: _scheduler_tick 안에서 무엇이 30초 블로킹했는지 즉시 확인
    #   ③ atexit: 정상 종료 시 "CLEAN EXIT" 마커 → 크래시 여부 구별
    #
    # 파일: logs/crash_fault.log (append — 이전 세션 로그 누적 보관)
    # 인코딩: faulthandler는 fd에 직접 ASCII 바이트 씀 → BOM·인코딩 지정 불필요
    _fault_file = None
    try:
        import faulthandler as _fh
        import atexit    as _atexit
        import sys       as _sys_fh
        import datetime  as _dt_fh

        _fault_path = os.path.join("logs", "crash_fault.log")
        os.makedirs("logs", exist_ok=True)

        # append + no encoding → faulthandler가 fd에 직접 ASCII 쓰므로 충돌 없음
        _fault_file = open(_fault_path, "a")

        # ── 세션 헤더 ───────────────────────────────────────────────────
        _now_s  = _dt_fh.datetime.now().isoformat(timespec="seconds")
        _pid    = os.getpid()
        _bits   = "32bit" if _sys_fh.maxsize <= 2**32 else "64bit"
        _pyver  = _sys_fh.version.split()[0]
        try:
            import psutil as _psu
            _mem_mb = _psu.Process(_pid).memory_info().rss / 1024 / 1024
            _mem_s  = f"  RSS={_mem_mb:.0f}MB"
        except Exception:
            _mem_s  = ""
        _fault_file.write(
            f"\n{'='*64}\n"
            f"[START] {_now_s}  PID={_pid}  Python {_pyver} {_bits}{_mem_s}\n"
            f"  → 크래시 시 아래에 전 스레드 트레이스 자동 기록됩니다\n"
            f"{'='*64}\n"
        )
        _fault_file.flush()
        try:
            os.fsync(_fault_file.fileno())   # OS 캐시 → 디스크 강제 기록
        except Exception:
            pass

        # ── ① 크래시 핸들러 활성화 ─────────────────────────────────────
        # all_threads=True: 메인 + GBM 재학습 스레드 + 워치독 스레드 전부 덤프
        _fh.enable(file=_fault_file, all_threads=True)

        # ── ② 행 감지 (30초 GIL 미해제 시 트레이스 덤프) ──────────────
        # _poll_option_chain은 OptionChainWorker(QThread)로 분리되어 메인 스레드 블로킹 없음.
        # _scheduler_tick 중 COM 호출이나 DB 쿼리가 30초 이상 블로킹되면 "TIMEOUT" 덤프 기록.
        # repeat=True: 계속 블로킹 중이면 30초마다 반복 덤프.
        _fh.dump_traceback_later(30, repeat=True, file=_fault_file)

        # ── ③ 정상 종료 마커 (atexit) ──────────────────────────────────
        # 크래시 종료: 마커 없음 → "CLEAN EXIT" 부재로 비정상 확인
        # 정상 종료: "CLEAN EXIT" 기록 → 크래시 아님 확인
        def _fault_atexit():
            try:
                _fh.cancel_dump_traceback_later()   # 행 감지 타이머 해제
                _fault_file.write(
                    f"[CLEAN EXIT] {_dt_fh.datetime.now().isoformat(timespec='seconds')}"
                    f"  PID={_pid}\n"
                )
                _fault_file.flush()
                _fault_file.close()
            except Exception:
                pass
        _atexit.register(_fault_atexit)

        logger.info(
            "[FaultHandler] 활성화 | file=%s PID=%d | "
            "행감지=30s all_threads=True",
            _fault_path, _pid,
        )

    except Exception as _fh_e:
        try:
            logger.warning("[FaultHandler] 설치 실패 (무해): %s", _fh_e)
        except Exception:
            pass

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
