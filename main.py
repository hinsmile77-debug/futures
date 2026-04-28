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
from utils.db_utils import init_all_dbs, execute, save_candle, save_features, count_raw_candles
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
from safety.circuit_breaker import CircuitBreaker
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
        self._heartbeat_count: int = 0

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
        for v in verified:
            self.circuit_breaker.record_accuracy(v["correct"])
            if v["correct"]:
                log_manager.learning(f"✓ {v['horizon']} 예측 적중 (conf={v['confidence']:.1%})")
            else:
                log_manager.learning(f"✗ {v['horizon']} 예측 실패")

        # ── STEP 2: SGD 온라인 자가학습 ────────────────────────
        # (STEP 1 검증 결과로 즉시 학습 — OnlineLearner.learn())
        # TODO: 피처 벡터 + actual_label 연동

        # ── STEP 3: GBM 배치 재학습 (30분마다) ─────────────────
        # TODO Phase 1 Week 3: batch_retrainer 구현

        # ── STEP 4: 피처 생성 ──────────────────────────────────
        features = self.feature_builder.build(bar)
        # 최소 0.5pt 보장 — 재시작 직후 1개 틱만으로 계산된 비정상 소ATR 방어
        atr      = max(features.get("atr", 0.5), 0.5)
        atr_ratio = features.get("atr_ratio", 1.0)

        # 분봉·피처 원본 저장 (경로 B 학습 데이터 축적)
        save_candle(bar)
        save_features(ts, features)

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
                "up": r["confidence"] if r["direction"] == 1 else (1 - r["confidence"]),
                "dn": r["confidence"] if r["direction"] == -1 else (1 - r["confidence"]),
            }
            for h, r in horizon_proba.items()
        }
        _dir_ko = "매수" if direction > 0 else ("매도" if direction < 0 else "관망")
        self.dashboard.update_prediction(close, _preds_ui, {}, confidence)
        self.dashboard.update_entry(_dir_ko, confidence, grade, {})

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

        # [DBG-F7] 진입 4개 조건 평가 — 차단 이유 파악용
        debug_log.debug(
            "[DBG-F7] 진입조건: pos=%s CB=%s new_entry=%s grade=%s time_zone=%s",
            self.position.status,
            self.circuit_breaker.state,
            is_new_entry_allowed(),
            grade,
            time_zone,
        )

        if (
            self.position.status == "FLAT"
            and self.circuit_breaker.is_entry_allowed()
            and is_new_entry_allowed()
            and grade not in ("X",)
        ):
            checklist_result = self.checklist.evaluate(
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

            # 체크리스트 결과 → 대시보드 진입 패널 업데이트 (체크마크 포함)
            _CHK_MAP = {
                "1_signal":"signal_chk", "2_confidence":"conf_chk",
                "3_vwap":"vwap_chk",    "4_cvd":"cvd_chk",
                "5_ofi":"ofi_chk",      "6_foreign":"fi_chk",
                "7_prev_bar":"candle_chk","8_time":"time_chk",
                "9_risk":"risk_chk",
            }
            _checks_ui = {_CHK_MAP.get(k, k): v for k, v in checklist_result["checks"].items()}
            self.dashboard.update_entry(_dir_ko, confidence, checklist_result["grade"], _checks_ui)

            # [DBG-F7a] 체크리스트 항목별 ✓/✗
            _chk = checklist_result["checks"]
            debug_log.debug(
                "[DBG-F7a] checklist %d/9 → %s | "
                "sig=%s conf=%s vwap=%s cvd=%s ofi=%s foreign=%s prev=%s time=%s risk=%s",
                checklist_result["pass_count"], checklist_result["grade"],
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

            final_grade = checklist_result["grade"]
            if final_grade != "X":
                kelly_result = self.kelly.compute_fraction()
                size_result  = self.sizer.compute(
                    confidence          = confidence,
                    atr                 = atr,
                    regime              = self.current_regime,
                    grade_mult          = checklist_result["size_mult"],
                    adaptive_kelly_mult = kelly_result["multiplier"],
                )

                # [DBG-F7b] 사이저 입력/출력 확인
                debug_log.debug(
                    "[DBG-F7b] sizer: conf=%.1f%% ATR=%.4f regime=%s "
                    "grade_mult=%.2f kelly_mult=%.2f → qty=%d",
                    confidence * 100, atr, self.current_regime,
                    checklist_result["size_mult"],
                    kelly_result.get("multiplier", 1.0),
                    size_result["quantity"],
                )

                qty = size_result["quantity"]
                dir_str = "LONG" if direction > 0 else "SHORT"

                if checklist_result["auto_entry"] or self.mode == "SIMULATION":
                    self._execute_entry(dir_str, close, qty, atr, final_grade)
                else:
                    log_manager.trade(
                        f"[수동 확인 필요] {dir_str} {qty}계약 @ {close} "
                        f"등급={final_grade}"
                    )
                    notify(
                        f"진입 확인 요청: {dir_str} {qty}계약\n"
                        f"등급={final_grade} 신뢰도={confidence:.1%}",
                        "WARNING",
                    )

        # ── STEP 8: 청산 트리거 감시 ───────────────────────────
        if self.position.status != "FLAT":
            self._check_exit_triggers(close, features, decision, bar)

        # ── 대시보드 PnL 패널 갱신 (매분) ──────────────────────────
        _daily   = self.position.daily_stats()
        _unreal  = self.position.unrealized_pnl_pts(close) * 500_000  # KRW
        _var_krw = -(atr * 1.65 * self.position.quantity * 500_000) if self.position.quantity else 0.0
        self.dashboard.update_pnl_metrics(_unreal, _daily["pnl_krw"], _var_krw)

        # ── STEP 9: 예측 DB 저장 ───────────────────────────────
        for h_name, h_res in horizon_proba.items():
            self.pred_buffer.save_prediction(
                ts         = ts,
                horizon    = h_name,
                direction  = h_res["direction"],
                confidence = h_res["confidence"],
                features   = {k: round(v, 4) for k, v in list(features.items())[:20]},
            )

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

    def activate_kill_switch(self, reason: str = "수동 발동") -> None:
        """Ctrl+Alt+K 단축키 또는 외부 호출용."""
        self.kill_switch.activate(reason)
        log_manager.system("KillSwitch 발동: " + reason, "CRITICAL")

    # ── 일일 마감 (15:40) ─────────────────────────────────────
    def daily_close(self):
        """자가학습 일일 마감"""
        stats = self.position.daily_stats()
        logger.info(f"[Daily] 마감 통계: {stats}")
        log_manager.system(
            f"일일 마감 | 승={stats['wins']} 패={stats['losses']} "
            f"PnL={stats['pnl_krw']:+,.0f}원"
        )

        # 일일 리셋
        self.feature_builder.reset_daily()
        self.position.reset_daily()
        self.circuit_breaker.reset_daily()
        self.online_learner.reset_daily()
        self.emergency_exit.reset()
        self.kill_switch.deactivate()

        notify(
            f"일일 마감\n승:{stats['wins']} 패:{stats['losses']}\n"
            f"PnL:{stats['pnl_krw']:+,.0f}원",
            "INFO",
        )

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

        # 연결 즉시 시뮬레이션 타이머 중지 (가짜 388.xx 로그 차단)
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
