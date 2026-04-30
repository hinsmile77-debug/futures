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
import argparse
import logging
import numpy as np

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
from utils.db_utils import init_all_dbs, execute, save_candle, save_features, count_raw_candles, fetch_today_trades, fetch_pnl_history
from config.settings import TRADES_DB

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
from learning.batch_retrainer import BatchRetrainer
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


class TradingSystem:
    """미륵이 메인 트레이딩 시스템"""

    def __init__(self, mode: str = "SIMULATION"):
        self.mode = mode
        logger.info(f"[System] 미륵이 초기화 | 모드={mode}")
        log_manager.system(f"미륵이 초기화 | 모드={mode}")

        # ── 키움 API 컴포넌트 ──────────────────────────────────
        self.kiwoom        = KiwoomAPI()
        self.latency_sync  = LatencySync()
        self.realtime_data: RealtimeData | None = None  # login 후 초기화

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
        self.dashboard = create_dashboard(sim_mode=(self.mode == "SIMULATION"))
        self._heartbeat_count: int = 0
        self._session_no: int = 0

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
    def connect_kiwoom(self) -> bool:
        """로그인 + 근월물 실시간 수신 등록."""
        print("[DBG CK-1] login() 호출 직전", flush=True)
        if not self.kiwoom.login():
            logger.error("[System] 키움 로그인 실패")
            return False
        print("[DBG CK-2] login() 성공", flush=True)

        code = self.kiwoom.get_nearest_futures_code()
        print(f"[DBG CK-3] 근월물 코드={code}", flush=True)
        self.emergency_exit.set_futures_code(code)

        self.realtime_data = RealtimeData(
            api              = self.kiwoom,
            code             = code,
            screen_no        = "3000",
            on_candle_closed = self._on_candle_closed,
            on_tick          = self._on_tick_price_update,
        )
        print("[DBG CK-4] RealtimeData 생성 완료", flush=True)

        self.realtime_data.start(load_history=True)
        print("[DBG CK-5] RealtimeData.start() 완료", flush=True)

        self.investor_data._api = self.kiwoom  # 실거래 시 TR 폴링 활성화
        logger.info("[System] 키움 실시간 수신 시작 — %s", code)
        return True

    def _on_tick_price_update(self, bar: dict) -> None:
        """틱 수신마다 대시보드 헤더·패널 현재가 갱신 + OFI 호가 누적."""
        if self.realtime_data is None:
            return
        # OFI: 틱마다 호가 변화 누적 (분봉 확정 시 flush_minute() 에서 집계)
        bid1 = bar.get("bid1", 0.0)
        ask1 = bar.get("ask1", 0.0)
        if bid1 and ask1:
            self.feature_builder.ofi.update_hoga(
                bid_price = bid1,
                bid_qty   = bar.get("bid_qty", 0),
                ask_price = ask1,
                ask_qty   = bar.get("ask_qty", 0),
            )
        self.dashboard.update_price(
            price  = bar["close"],
            change = bar["close"] - bar.get("open", bar["close"]),
            code   = self.realtime_data.code,
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
        close  = bar["close"]

        # 대시보드 실시간 가격 동기화
        self.dashboard.update_price(
            price  = close,
            change = close - bar.get("open", close),
            code   = self.realtime_data.code if self.realtime_data else "",
        )

        log_manager.signal(f"--- {ts} 분봉 파이프라인 시작 ---")

        # ── STEP 1: 과거 예측 검증 ─────────────────────────────
        verified = self.pred_buffer.verify_and_update(ts, close)
        self._verified_today += len(verified)
        for v in verified:
            # SIMULATION: 더미 모델 정확도로 CB③(30분 35% 미만) 조기 발동 방지
            if self.mode != "SIMULATION":
                self.circuit_breaker.record_accuracy(v["correct"])
            if v["correct"]:
                log_manager.learning(f"✓ {v['horizon']} 예측 적중 (conf={v['confidence']:.1%})")
            else:
                log_manager.learning(f"✗ {v['horizon']} 예측 실패")

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
            result = self.batch_retrainer.retrain_now()
            if result.get("ok"):
                self.model._load_all()   # 새 모델 즉시 반영
                log_manager.learning(
                    f"[GBM] 배치 재학습 완료 | {result['elapsed_sec']}초 "
                    f"데이터={result['data_size']}행"
                )
                notify("GBM 배치 재학습 완료", "INFO")
            else:
                log_manager.learning(f"[GBM] 재학습 건너뜀: {result.get('error','')}")

        # ── STEP 4: 피처 생성 ──────────────────────────────────
        self.investor_data.fetch_all()                          # 시뮬: 더미, 실거래: TR 요청
        supply_feats = self.investor_data.get_features()
        features = self.feature_builder.build(bar, supply_demand=supply_feats)
        # 최소 0.5pt 보장 — 재시작 직후 1개 틱만으로 계산된 비정상 소ATR 방어
        atr      = max(features.get("atr", 0.5), 0.5)
        atr_ratio = features.get("atr_ratio", 1.0)

        # 분봉·피처 원본 저장 (경로 B 학습 데이터 축적)
        save_candle(bar)
        save_features(ts, features)

        # 다이버전스 패널 갱신 (외인·개인 수급)
        _inv = self.investor_data
        _fi_call = _inv._call.get("foreign", 0)
        _fi_put  = _inv._put.get("foreign", 0)
        _rt_call = _inv._call.get("individual", 0)
        _rt_put  = _inv._put.get("individual", 0)
        _fi_fut  = _inv._futures.get("foreign", 0)
        _rt_fut  = _inv._futures.get("individual", 0)
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
            "rt_strd":     0,
            "fi_call":     _fi_call,
            "fi_put":      _fi_put,
            "fi_strangle": 0,
            "contrarian":  _contrarian,
            "div_score":   float(_fi_fut - _rt_fut),
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
        if not self.model.is_ready():
            log_manager.signal("모델 미학습 상태 — 예측 건너뜀")
            return

        feat_vec = self.feature_builder.get_feature_vector(self.model.feature_names)
        horizon_proba = self.model.predict_proba(feat_vec)

        # SGD 블렌딩: 호라이즌별로 GBM + SGD 확률 혼합
        for h_name in list(horizon_proba.keys()):
            sgd_p   = self.online_learner.predict_proba(h_name, feat_vec)
            blended = self.online_learner.blend_with_gbm(horizon_proba[h_name], sgd_p)
            up, dn, fl = blended["up"], blended["down"], blended["flat"]
            best = max([(up, 1), (dn, -1), (fl, 0)], key=lambda t: t[0])
            horizon_proba[h_name] = {
                "up": round(up, 4), "down": round(dn, 4), "flat": round(fl, 4),
                "direction": best[1], "confidence": round(best[0], 4),
            }

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
        _dir_ko = "매수" if direction > 0 else ("매도" if direction < 0 else "관망")
        self.dashboard.update_prediction(close, _preds_ui, {}, confidence)
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
                daily_loss_pct    = abs(self.position.daily_stats()["pnl_pts"]) / 1_000,
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

        # 실제 진입: CB + 시간 조건까지 모두 충족해야 실행
        if (
            _cr is not None
            and self.circuit_breaker.is_entry_allowed()
            and is_new_entry_allowed()
            and _final_grade not in ("X",)
            and _qty_display > 0
        ):
            dir_str = "LONG" if direction > 0 else "SHORT"
            if _cr["auto_entry"] or self.mode == "SIMULATION":
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

    def _execute_entry(
        self, direction: str, price: float,
        quantity: int, atr: float, grade: str,
    ):
        """진입 실행"""
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
            result = self.position.close_position(exit_price, "하드스톱")
            self._post_exit(result)
            return

        # 3순위: 부분 청산
        if self.position.is_tp1_hit(price) and not self.position.partial_1_done:
            log_manager.trade(f"[1차 부분청산] @ {price}")
            self.position.partial_1_done = True

        if self.position.is_tp2_hit(price) and not self.position.partial_2_done:
            log_manager.trade(f"[2차 부분청산] @ {price}")
            self.position.partial_2_done = True

        # 4순위: 시간 강제 청산
        if self.time_exit.should_force_exit():
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
        if retrain_result.get("ok"):
            self.model._load_all()
            log_manager.learning(
                f"[GBM] 일일 마감 재학습 완료 | {retrain_result['elapsed_sec']}초 "
                f"데이터={retrain_result['data_size']}행"
            )
        else:
            log_manager.learning(
                f"[GBM] 일일 마감 재학습 건너뜀: {retrain_result.get('error','')}"
            )

        # 일일 리셋
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
        self._refresh_pnl_history()

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
        logger.info(f"모드: {self.mode}")
        logger.info("=" * 60)

        # 키움 로그인 (블로킹)
        if not self.connect_kiwoom():
            logger.critical("[System] 키움 연결 실패 — 종료")
            return

        # SIMULATION 모드: 키움 연결 후 시뮬 타이머 중지 (가짜 388.xx 로그 차단)
        if self.mode == "SIMULATION":
            self.dashboard.stop_sim_timer()

        # SIMULATION: 모델 미학습 시 더미 주입 — 파이프라인 통과 검증용
        if self.mode == "SIMULATION" and not self.model.is_ready():
            logger.warning("[System] SIMULATION — 더미 모델 주입 (파이프라인 통과 검증)")
            log_manager.system("더미 모델 주입 — STEP5 이후 진입/청산 로직 검증 시작")
            self.model.force_ready_for_test()

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
        self.dashboard.append_sys_log(f"시스템 시작 | 모드={self.mode} | 코드={self.realtime_data.code if self.realtime_data else '—'}")
        self.dashboard.update_system_status(cb_state="NORMAL", latency_ms=0.0)

        # 세션 카운터 증가 + 당일 거래 이력 복원
        self._session_no = self._increment_session()
        self._restore_daily_state()

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


def main():
    parser = argparse.ArgumentParser(description="미륵이 선물 트레이딩 시스템")
    parser.add_argument(
        "--mode",
        choices=["simulation", "live"],
        default="simulation",
        help="실행 모드 (기본: simulation)",
    )
    args = parser.parse_args()

    # DB 초기화
    init_all_dbs()
    logger.info("[System] DB 초기화 완료")

    mode = args.mode.upper()
    if mode == "LIVE":
        logger.warning("=" * 60)
        logger.warning("⚠️  실전 매매 모드 — 실제 계좌가 사용됩니다!")
        logger.warning("=" * 60)

    system = TradingSystem(mode=mode)
    system.run()


if __name__ == "__main__":
    main()
