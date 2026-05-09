# strategy/entry/entry_manager.py — 진입 통합 관리자
"""
진입 결정의 최종 관문 — 아래 모든 모듈을 통합 조율

파이프라인:
  1. TimeStrategyRouter  — 시간대 파라미터 확인 (진입 허용 여부)
  2. EntryChecklist       — 9개 체크리스트 → 등급 결정
  3. StagedEntryManager  — 등급별 분할 진입 지시
  4. PositionSizer        — 최종 계약 수 계산
  5. Kiwoom API           — 주문 전송 (외부 의존)

Circuit Breaker / KillSwitch는 main.py 레벨에서 사전 차단
이 클래스는 CB가 NORMAL 상태일 때만 호출됨
"""
import datetime
import logging
from typing import Optional, Dict, TYPE_CHECKING

from config import secrets as _secrets

from config.constants import (
    DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT,
    POSITION_LONG, POSITION_SHORT,
)
from config.settings import FORCE_EXIT_TIME, NEW_ENTRY_CUTOFF

from strategy.entry.checklist import EntryChecklist
from strategy.entry.time_strategy_router import TimeStrategyRouter
from strategy.entry.staged_entry import StagedEntryManager
from strategy.entry.position_sizer import PositionSizer

if TYPE_CHECKING:
    from collection.broker.base import BrokerAPI
    from strategy.position.position_tracker import PositionTracker

logger = logging.getLogger("TRADE")


class EntryManager:
    """
    진입 통합 관리자

    main.py의 run_minute_pipeline()에서 매 분봉 호출:
        result = entry_manager.try_entry(signal_data, market_data)
    """

    def __init__(
        self,
        position_tracker,  # PositionTracker
        kiwoom_api=None,   # KiwoomAPI (None = 시뮬레이션)
        account_balance: float = 50_000_000.0,
    ):
        self._tracker       = position_tracker
        self._api           = kiwoom_api
        self._balance       = account_balance

        self._checklist     = EntryChecklist()
        self._router        = TimeStrategyRouter()
        self._staged        = StagedEntryManager()
        self._sizer         = PositionSizer()

        # 일일 통계
        self._daily_entries = 0

    # ── 매 분봉 메인 호출 ─────────────────────────────────────────
    def try_entry(
        self,
        signal:  dict,   # 앙상블 신호 딕셔너리
        market:  dict,   # 시장 데이터 딕셔너리
        now:     Optional[datetime.datetime] = None,
    ) -> Optional[Dict]:
        """
        진입 시도 — 조건 충족 시 주문 전송 및 결과 반환

        Args:
            signal: {direction, confidence, regime, micro_regime, ...}
            market: {price, atr, vwap_position, cvd_direction, ofi_pressure,
                     foreign_call_net, foreign_put_net, prev_bar_bullish,
                     daily_loss_pct}
            now:    기준 시각

        Returns:
            진입 결과 딕셔너리 or None (진입 안 함)
        """
        if now is None:
            now = datetime.datetime.now()

        # ─ 0. 이미 포지션 있으면 분할 진입 업데이트만 ────────────
        from config.constants import POSITION_FLAT
        if self._tracker.status != POSITION_FLAT:
            return self._handle_staged_update(market.get("price", 0.0), now)

        direction = signal.get("direction", DIRECTION_FLAT)
        if direction == DIRECTION_FLAT:
            return None

        # ─ 1. 시간대 파라미터 ────────────────────────────────────
        params = self._router.route(now)
        if not params["allow_new_entry"]:
            logger.debug(f"[Entry] 진입 금지 구간 ({params['zone']})")
            return None

        # 레짐 보정
        params = self._router.apply_regime_override(params, signal.get("regime", "NEUTRAL"))
        params = self._router.apply_micro_regime_override(params, signal.get("micro_regime", "혼합"))

        if not params["allow_new_entry"]:
            logger.info(f"[Entry] 미시 레짐 진입 차단 ({signal.get('micro_regime')})")
            return None

        # ─ 2. 체크리스트 평가 ────────────────────────────────────
        check_result = self._checklist.evaluate(
            direction          = direction,
            confidence         = signal.get("confidence", 0.0),
            vwap_position      = market.get("vwap_position", 0.0),
            cvd_direction      = market.get("cvd_direction", 0),
            ofi_pressure       = market.get("ofi_pressure", 0),
            foreign_call_net   = market.get("foreign_call_net", 0.0),
            foreign_put_net    = market.get("foreign_put_net", 0.0),
            prev_bar_bullish   = market.get("prev_bar_bullish", False),
            time_zone          = params["zone"],
            daily_loss_pct     = market.get("daily_loss_pct", 0.0),
            min_confidence     = params["min_confidence"],
        )

        grade = check_result["grade"]
        if grade == "X":
            return None

        # ─ 3. 계약 수 결정 ───────────────────────────────────────
        price = market.get("price", 0.0)
        atr   = market.get("atr", 1.0)

        base_qty = self._sizer.calc_size(
            balance        = self._balance,
            price          = price,
            atr            = atr,
            size_mult      = check_result["size_mult"] * params["size_mult"],
            regime         = signal.get("regime", "NEUTRAL"),
            confidence     = signal.get("confidence", 0.5),
        )

        if base_qty < 1:
            logger.info("[Entry] 사이즈 계산 결과 0계약 — 진입 안 함")
            return None

        # ─ 4. 분할 진입 요청 ─────────────────────────────────────
        stop_price = self._calc_stop(price, atr, direction)
        instr = self._staged.request_entry(
            grade       = grade,
            direction   = direction,
            price       = price,
            base_qty    = base_qty,
            atr         = atr,
            stop_price  = stop_price,
        )
        if instr is None:
            return None

        # ─ 5. 주문 전송 ──────────────────────────────────────────
        order_result = self._send_order(instr, price)
        if not order_result.get("ok"):
            logger.error(f"[Entry] 주문 실패: {order_result.get('error')}")
            self._staged.reset()
            return None

        # ─ 6. 포지션 오픈 ────────────────────────────────────────
        self._tracker.open_position(
            direction = instr["direction_str"],
            price     = price,
            quantity  = instr["qty"],
            atr       = atr,
            grade     = grade,
            regime    = signal.get("regime", "NEUTRAL"),
        )

        self._daily_entries += 1

        result = {
            "entered":    True,
            "grade":      grade,
            "direction":  instr["direction_str"],
            "qty":        instr["qty"],
            "price":      price,
            "stop":       stop_price,
            "action":     instr["action"],
            "zone":       params["zone"],
            "note":       instr["note"],
        }
        logger.info(
            f"[Entry] ✅ 진입 완료 | {instr['direction_str']} {instr['qty']}계약 "
            f"@ {price} | 등급={grade} | 구간={params['zone']}"
        )
        return result

    # ── 분할 진입 2차 업데이트 ────────────────────────────────────
    def _handle_staged_update(self, price: float, now: datetime.datetime) -> Optional[Dict]:
        """기존 포지션에 대한 분할 2차 진입 처리"""
        instr = self._staged.update(price, now)
        if instr is None:
            return None

        order_result = self._send_order(instr, price)
        if not order_result.get("ok"):
            return None

        # 포지션 수량 추가
        self._tracker.quantity += instr["qty"]
        logger.info(f"[Entry] ✅ 2차 추가 | {instr['qty']}계약 @ {price}")
        return {
            "entered":  True,
            "action":   instr["action"],
            "qty":      instr["qty"],
            "price":    price,
            "note":     instr["note"],
        }

    # ── 주문 전송 ─────────────────────────────────────────────────
    def _send_order(self, instr: dict, price: float) -> dict:
        """
        Kiwoom API 주문 전송

        API 없으면 시뮬레이션 OK 반환
        """
        if self._api is None:
            logger.info(f"[Entry] [SIM] 주문: {instr['direction_str']} {instr['qty']}계약 @ {price:.2f}")
            return {"ok": True, "order_no": "SIM-0000"}

        try:
            dir_code = "1" if instr["direction_str"] == POSITION_LONG else "2"
            order_no = self._api.send_order(
                rqname     = "진입",
                screen_no  = "1000",
                acc_no     = _secrets.ACCOUNT_NO,
                order_type = 1,    # 신규매수
                code       = "101Q9000",   # 코스피200 선물 근월물
                qty        = instr["qty"],
                price      = 0,    # 시장가
                hoga_gb    = "03", # 시장가
                org_order  = "",
            )
            return {"ok": True, "order_no": order_no}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    def _calc_stop(price: float, atr: float, direction: int) -> float:
        from config.settings import ATR_STOP_MULT
        return price - direction * atr * ATR_STOP_MULT

    # ── 일일 리셋 ─────────────────────────────────────────────────
    def reset_daily(self):
        self._staged.reset()
        self._daily_entries = 0

    def update_balance(self, balance: float):
        self._balance = balance

    def get_stats(self) -> dict:
        return {
            "daily_entries": self._daily_entries,
            "staged_state":  self._staged.state,
            "zone":          self._router.get_zone(),
        }
