# strategy/position/position_tracker.py — 현재 포지션 상태 추적
"""
실시간 포지션 상태를 관리합니다.
진입 → 보유 → 청산의 전체 생명주기를 추적.
"""
import datetime
import json
import logging
import os
from typing import Optional, Dict, Tuple

from utils.time_utils import now_kst

from config.constants import POSITION_LONG, POSITION_SHORT, POSITION_FLAT, FUTURES_PT_VALUE
from config.settings import (
    ATR_STOP_MULT, ATR_TP1_MULT, ATR_TP2_MULT, ATR_TP3_MULT,
    ATR_HORIZON_TP1_MULT, FUTURES_COMMISSION_RATE,
    HURST_REGIME_ATR_MULT_ENABLED, HURST_REGIME_ATR_MULT,
    PARTIAL_EXIT_RATIOS,
    LOSS_TIER1_STOP_FRACTION, LOSS_TIER1_CUT_RATIO,
)

# 인스턴스별 pt_value를 주입받기 전 module-level fallback 으로만 사용
def _calc_commission(price: float, quantity: int, pt_value: float = FUTURES_PT_VALUE) -> float:
    """편도 수수료 계산 (왕복은 호출부에서 × 2)"""
    return price * quantity * pt_value * FUTURES_COMMISSION_RATE

logger = logging.getLogger("TRADE")

_STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "position_state.json",
)


def compute_trailing_stop_tier(
    entry_price: float,
    direction: str,
    atr: float,
    current_price: float,
    prev_anchor: float,
    prev_stop: float,
) -> Tuple[float, float]:
    """[361차] PositionTracker.update_trailing_stop()의 4단계 티어 계산을 순수함수로
    분리 — scripts/generate_validation_campaign_report.py의 tp2_hold_shadow 리졸버가
    동일 로직을 import해 재사용한다. 라이브 트레일링과 계측용 카운터팩추얼 시뮬레이션이
    복붙으로 갈라져 드리프트하는 것을 막기 위함(단일 소스 유지).

    반환: (new_anchor, new_stop). direction은 POSITION_LONG/POSITION_SHORT 문자열.
    """
    mult = 1 if direction == POSITION_LONG else -1
    unrealized_pts = (current_price - entry_price) * mult

    anchor = prev_anchor if prev_anchor > 0 else entry_price
    if direction == POSITION_LONG:
        anchor = max(anchor, current_price)
    else:
        anchor = min(anchor, current_price)

    stop = prev_stop
    candidate = None
    if unrealized_pts >= atr * 2.0:
        # 2ATR 이상 수익 → 최고점 추적 (1ATR 간격)
        candidate = anchor - mult * atr
    elif unrealized_pts >= atr * 1.5:
        # 1.5ATR 이상 → +0.5ATR 보장
        candidate = entry_price + mult * atr * 0.5
    elif unrealized_pts >= atr * 1.0:
        # 1ATR 이상 → 본전 손절
        candidate = entry_price
    elif unrealized_pts >= atr * 0.5:
        # 0.5ATR 이상 → 최대손실 -0.75ATR로 축소 (무방비 구간 보호)
        candidate = entry_price - mult * atr * 0.75

    if candidate is not None and mult * (candidate - stop) > 0:
        stop = candidate
    return anchor, stop


class PositionTracker:
    """단일 포지션 상태 관리"""

    def __init__(self, pt_value: float = FUTURES_PT_VALUE):
        self._pt_value: float = float(pt_value)
        self.status:       str   = POSITION_FLAT
        self.entry_price:  float = 0.0
        self.quantity:     int   = 0
        self.entry_time:   Optional[datetime.datetime] = None
        self.grade:        str   = ""
        self.regime:       str   = ""
        self.signal_direction: str = ""
        self.reverse_entry_enabled: bool = False
        self.entry_horizon: Optional[str] = None
        self.entry_hurst_bucket: Optional[str] = None
        self.entry_extra_stop_mult: float = 1.0  # [349차] 급변장 사전 가드 스톱확대 배수

        self.stop_price:   float = 0.0
        # [MW0602 423차] 스톱이 마지막으로 조여진 시각 — "유령 하드스톱" 차단용.
        # is_stop_hit_intrabar()가 이 시각과 봉 시작시각을 비교해, 스톱을 조인
        # 그 분봉의 고저가로는 봉중 판정을 하지 않는다(그 고저가는 조이기 이전에
        # 형성된 값이라 새 스톱을 소급 적용하면 오판정이 된다).
        self.stop_updated_at: Optional[datetime.datetime] = None
        # [MW0602 424차] 섀도 전용 조이기 기록 — **가드가 읽지 않는다**.
        # 왜 `stop_updated_at`과 따로 두는가:
        #   423차 가드는 qty==1 경로(arm_tp1_*)만 계측했고, qty>=2의 TP1 손익분기
        #   이동(main.py `tp1_breakeven`)은 stop_price를 직접 대입해 계측이 없다.
        #   그래서 08-04에 qty=2 포지션 3건이 유령 하드스톱으로 청산됐다.
        #   그런데 그 3건의 실현손익이 **+8.76pt(+433,609원, 당일 순익의 57.6%)** 로
        #   유리했다(08-03 8건 +1.42pt와 부호 동일 — 2거래일 11건 연속 유리).
        #   유령 청산은 "봉 고가가 스톱을 스쳤으나 현재가는 유리하게 되돌아왔다"는
        #   조건에서만 터져 시장가가 스톱보다 좋은 국면을 고른다 — 결함이 아니라
        #   미발견 청산 알파일 가능성이 있다.
        #   따라서 지금 가드를 qty>=2까지 켜면 **손익이 줄어들 수 있다**. 표본 11건
        #   2거래일로 확정하는 것은 313차 원칙 위반이므로, 라이브 청산은 그대로 두고
        #   "정상 가드였다면 억제됐을 건"만 기록해 캠페인 채널로 판정한다.
        self.stop_shadow_tightened_at: Optional[datetime.datetime] = None
        self.stop_shadow_tighten_path: Optional[str] = None
        self.tp1_price:    float = 0.0
        self.tp2_price:    float = 0.0
        self.tp3_price:    float = 0.0
        self.trailing_anchor_price: float = 0.0

        self.partial_1_done: bool = False
        self.partial_2_done: bool = False
        self.partial_3_done: bool = False
        self.initial_quantity: int = 0

        # [MW0601 421차] 진입 계약수 — `initial_quantity`와 분리한 별도 필드.
        # 둘은 진입 시점에 같은 값으로 출발하지만 **수명이 다르다**:
        #   initial_quantity : 360차 shrink_initial(손절1차 조기축소)이 청산분만큼
        #                      깎는다. TP 진행률 매칭(_sync_partial_progress)이
        #                      "잔여 포지션은 처음부터 이 수량이었던 새 포지션"으로
        #                      보여야 하므로 **의도된 동작**이다.
        #   entry_quantity   : 진입 시점 값을 그대로 보존한다. 어떤 청산 경로에서도
        #                      줄지 않는다(추가진입 시에만 증가).
        # 417차가 `entry_qty` 기록을 initial_quantity에서 가져가면서 이 수명 차이와
        # 충돌했다 — 08-03 10:19 SHORT 3계약이 손절1차를 거치며 레그별 entry_qty가
        # 3이 아니라 2·1로 기록됐다(감소하는 값의 스냅샷). db_utils 구버전 백필은
        # `SUM(quantity) GROUP BY entry_ts`라 3을 넣으므로 라이브와 백필이 갈렸다.
        self.entry_quantity: int = 0

        # [360차] 손절 계단화 1차 — entry~stop 거리의 50% 지점(진입 시 1회 계산, 고정)
        self.loss_tier1_price: float = 0.0
        self.loss_tier1_done: bool = False
        # [363차] qty=1 손실1차 섀도 — 물리적 분할 불가라 실제 축소는 안 하지만,
        # "그 시점에 전량 조기청산했다면"의 counterfactual 기록 여부(포지션당 1회).
        self.loss_tier1_qty1_shadow_logged: bool = False
        # [367차] Tier1 발동 후 잔여계약 2단계 조기청산 섀도 — Tier1이 qty=2 중 1계약만
        # 잘라내고 남은 1계약은 원래 stop_price까지 무방비로 노출되는 사각지대(0722
        # 딥다이브에서 확인) 계측용. Tier1 체결가(fill_price) ~ 원래 stop_price 구간의
        # 50% 지점 — main.py:_ts_handle_exit_fill()의 loss_tier1_done=True 시점에 계산.
        self.loss_tier2_price: float = 0.0
        self.loss_tier2_shadow_logged: bool = False
        # [363차 후속] 진입 시점 quantile 기대엣지 — ensemble_decisions에는 매분
        # 찍히지만 "이 포지션이 진입한 바로 그 순간의 값"을 그대로 들고 있어야
        # loss_tier1_qty1_shadow 등 사후 분석에서 재조인 없이 바로 쓸 수 있다.
        self.entry_quantile_expected_pt: Optional[float] = None
        self.entry_quantile_uncertainty_pt: Optional[float] = None

        # [2026-07-16 339차 후속] 1계약 TP1 회계적 분할청산(synthetic partial) —
        # Cybos 최소 체결단위가 1계약이라 물리적으로 못 쪼개는 상황에서, TP1 도달
        # 시점 가격을 "포지션의 33%를 여기서 확정했다고 치는" 회계상 기록으로만
        # 남긴다. 실제 계약수·리스크 노출은 변경하지 않음 — arm_tp1_single_contract_
        # with_mode()의 스탑 이동(물리적 리스크 관리)과 완전히 별개.
        self.synthetic_tp1_price:    Optional[float] = None
        self.synthetic_tp1_pnl_pts:  Optional[float] = None
        self.synthetic_tp1_fraction: Optional[float] = None
        self.synthetic_tp1_ts:       Optional[datetime.datetime] = None

        self._optimistic: bool = False  # True = open_position() called speculatively; Chejan will correct price

        self._daily_pnl_pts:   float = 0.0
        self._daily_trades:    int   = 0
        self._daily_wins:      int   = 0
        self._daily_commission: float = 0.0
        self._daily_forward_pnl_pts: float = 0.0
        self._daily_forward_trades: int = 0
        self._daily_forward_wins: int = 0
        self._daily_forward_commission: float = 0.0

        # [459차 F1] 포지션 단위 승패 판정용 레그 누적기 — 부분청산(TP1/TP2,
        # 손절1차 축소 등)으로 여러 레그에 나뉜 현재 포지션의 실현 Σ(pnl_pts×qty).
        # 최종 청산(apply_exit_fill is_final / close_position)에서 이 총합으로
        # 승패를 1회 판정한다. 종전에는 마지막 레그의 pnl_pts만 봐서 앞선 레그
        # 손실(-3.04pt×2)이 마지막 레그 이익(+0.70pt×1)에 가려 순손실 포지션이
        # 승으로 집계됐다. 장중 재기동 대비 상태 JSON에 함께 영속화된다.
        self._pos_acc_pnl_pts: float = 0.0
        self._pos_acc_fwd_pnl_pts: float = 0.0
        self.last_update_reason: str = "init"
        self.last_update_ts: Optional[datetime.datetime] = None

        self._futures_code: str = ""          # 현재 거래 종목코드 (connect_broker 후 주입)
        self._loaded_futures_code: str = ""   # load_state() 에서 복원된 저장 코드

    def set_pt_value(self, pt_value: float) -> None:
        """계약 종류 변경 시 pt_value 갱신 (FLAT 상태에서만 유효)."""
        self._pt_value = float(pt_value)

    def set_futures_code(self, code: str) -> None:
        """거래 종목코드 주입 — connect_broker() 완료 후 호출."""
        self._futures_code = str(code or "").strip()

    def force_flat(self, reason: str = "forced") -> None:
        """포지션 강제 초기화 — 코드 불일치 등 비정상 상태 복구용."""
        self.status = POSITION_FLAT
        self.entry_price = 0.0
        self.quantity = 0
        self.entry_time = None
        self.entry_hurst_bucket = None
        self.entry_extra_stop_mult = 1.0
        self.stop_price = 0.0
        self.stop_updated_at = None
        self.stop_shadow_tightened_at = None   # [424차]
        self.stop_shadow_tighten_path = None   # [424차]
        self.tp1_price = 0.0
        self.tp2_price = 0.0
        self.tp3_price = 0.0
        self.trailing_anchor_price = 0.0
        self.partial_1_done = False
        self.partial_2_done = False
        self.partial_3_done = False
        self.initial_quantity = 0
        self.entry_quantity = 0
        self.loss_tier1_price = 0.0
        self.loss_tier1_done = False
        self.loss_tier1_qty1_shadow_logged = False
        self.loss_tier2_price = 0.0
        self.loss_tier2_shadow_logged = False
        self.entry_quantile_expected_pt = None
        self.entry_quantile_uncertainty_pt = None
        self.synthetic_tp1_price = None
        self.synthetic_tp1_pnl_pts = None
        self.synthetic_tp1_fraction = None
        self.synthetic_tp1_ts = None
        self._pos_acc_pnl_pts = 0.0       # [459차 F1]
        self._pos_acc_fwd_pnl_pts = 0.0
        self._optimistic = False
        self.last_update_reason = reason
        self.last_update_ts = now_kst()
        self._save_state()

    def open_position(
        self,
        direction: str,
        price: float,
        quantity: int,
        atr: float,
        grade: str = "B",
        regime: str = "NEUTRAL",
        raw_direction: Optional[str] = None,
        reverse_entry_enabled: bool = False,
        entry_horizon: Optional[str] = None,
        hurst_bucket: Optional[str] = None,
        extra_stop_mult: float = 1.0,
        quantile_expected_pt: Optional[float] = None,
        quantile_uncertainty_pt: Optional[float] = None,
    ):
        """
        포지션 진입

        Args:
            direction:      LONG | SHORT
            price:          진입가
            quantity:       계약 수
            atr:            현재 ATR (손절/목표 계산)
            grade:          진입 등급 (A/B/C)
            regime:         매크로 레짐
            entry_horizon:  ATR 레짐 선택 호라이즌 ("1m"/"3m"/"5m"/None)
                            지정 시 ATR_HORIZON_TP1_MULT로 TP1 단축, None이면 ATR_TP1_MULT(1.0) 사용
            hurst_bucket:   "trend"/"neutral"/"mean-revert" (None이면 배수 미적용)
                            HURST_REGIME_ATR_MULT_ENABLED=True일 때 손절/TP1/TP2 폭에
                            추가로 곱해지는 레짐 조건부 배수 (260704 감사 P2)
            extra_stop_mult: [349차] 급변장 사전 가드(VolatilityBurstGate)가 사이즈
                            축소와 함께 적용하는 손절폭 확대 배수(기본 1.0=미적용).
                            hurst_bucket 배수와 별개로 손절 거리에만 곱해진다 —
                            TP는 건드리지 않아 위험:보상비가 더 보수적으로 변한다
                            (사이즈 축소로 절대 리스크는 상쇄).
            quantile_expected_pt/quantile_uncertainty_pt: [363차 후속] 진입 결정 순간의
                            분위 회귀 기대값/불확실성(pt) 스냅샷 — 리스크 관리에는
                            관여하지 않고 loss_tier1_qty1_shadow 등 사후 분석 계측
                            전용(None 허용, 미전달 시 그대로 None).
        """
        assert direction in (POSITION_LONG, POSITION_SHORT), f"Invalid direction: {direction}"
        assert self.status == POSITION_FLAT, "이미 포지션 보유 중"

        self.status      = direction
        self.entry_price = price
        self.quantity    = quantity
        self.entry_time  = now_kst()
        self.grade       = grade
        self.regime      = regime
        self.signal_direction = raw_direction or direction
        self.reverse_entry_enabled = bool(reverse_entry_enabled)
        self.entry_horizon = entry_horizon
        self.entry_hurst_bucket = hurst_bucket
        self.entry_extra_stop_mult = float(extra_stop_mult or 1.0)
        self.initial_quantity = quantity
        self.entry_quantity = quantity
        self.trailing_anchor_price = price
        self.entry_quantile_expected_pt = (
            float(quantile_expected_pt) if quantile_expected_pt is not None else None
        )
        self.entry_quantile_uncertainty_pt = (
            float(quantile_uncertainty_pt) if quantile_uncertainty_pt is not None else None
        )

        mult = 1 if direction == POSITION_LONG else -1
        _tp1_mult = ATR_HORIZON_TP1_MULT.get(entry_horizon, ATR_TP1_MULT) if entry_horizon else ATR_TP1_MULT
        _stop_mult, _tp2_mult = ATR_STOP_MULT, ATR_TP2_MULT
        _regime_mult = (
            HURST_REGIME_ATR_MULT.get(hurst_bucket) if HURST_REGIME_ATR_MULT_ENABLED and hurst_bucket else None
        )
        if _regime_mult:
            _stop_mult = ATR_STOP_MULT * _regime_mult.get("stop", 1.0)
            _tp1_mult  = _tp1_mult     * _regime_mult.get("tp1", 1.0)
            _tp2_mult  = ATR_TP2_MULT  * _regime_mult.get("tp2", 1.0)
        _extra_stop_mult = self.entry_extra_stop_mult
        _stop_mult = _stop_mult * _extra_stop_mult
        self.stop_price = price - mult * atr * _stop_mult
        # [423차] 진입(또는 레벨 재계산) 시각도 기록한다 — 진입 분봉의 고저가는
        # 진입 이전 구간을 포함하므로, 그 봉의 봉중 판정 역시 유령이다.
        self._mark_stop_tightened("entry")
        self.tp1_price  = price + mult * atr * _tp1_mult
        self.tp2_price  = price + mult * atr * _tp2_mult
        # [360차] 손절 계단화 1차 — entry~stop 사이 선형보간 50% 지점(진입 시 1회 계산,
        # 고정). LONG/SHORT 방향(mult)과 무관하게 entry→stop 벡터의 절반이므로 부호
        # 분기가 필요 없다. HURST_REGIME_ATR_MULT·extra_stop_mult가 이미 반영된
        # stop_price를 기준으로 삼아 별도 배수 재계산 없이 실제 손절 거리를 따라간다.
        self.loss_tier1_price = price + (self.stop_price - price) * LOSS_TIER1_STOP_FRACTION

        self.partial_1_done = False
        self.partial_2_done = False
        self.partial_3_done = False
        self.loss_tier1_done = False
        self.loss_tier1_qty1_shadow_logged = False
        self.loss_tier2_price = 0.0
        self.loss_tier2_shadow_logged = False
        self._pos_acc_pnl_pts = 0.0       # [459차 F1] 새 포지션 — 레그 누적 초기화
        self._pos_acc_fwd_pnl_pts = 0.0
        self.last_update_reason = f"open_position:{direction}"
        self.last_update_ts = now_kst()

        _hz_tag = f" horizon={entry_horizon}" if entry_horizon else ""
        _hb_tag = f" hurst={hurst_bucket}" if _regime_mult else ""
        _vb_tag = f" stop×{_extra_stop_mult:.2f}(VolBurst)" if _extra_stop_mult != 1.0 else ""
        logger.info(
            f"[Position] 진입 {direction} {quantity}계약 @ {price} "
            f"| 손절={self.stop_price:.2f} 1차={self.tp1_price:.2f}(×{_tp1_mult:.2f}) "
            f"2차={self.tp2_price:.2f}{_hz_tag}{_hb_tag}{_vb_tag}"
        )
        self._save_state()

    def close_position(self, exit_price: float, reason: str) -> Dict:
        """포지션 청산 후 손익 반환"""
        assert self.status != POSITION_FLAT, "포지션 없음"

        mult = 1 if self.status == POSITION_LONG else -1
        pnl_pts = (exit_price - self.entry_price) * mult
        commission = _calc_commission(self.entry_price, self.quantity, self._pt_value) * 2  # 왕복
        pnl_krw = pnl_pts * self._pt_value * self.quantity - commission
        forward_direction = self.signal_direction or self.status
        forward_pnl_pts = self._calc_directional_pnl_pts(forward_direction, exit_price)
        forward_commission = _calc_commission(self.entry_price, self.quantity, self._pt_value) * 2
        forward_pnl_krw = forward_pnl_pts * self._pt_value * self.quantity - forward_commission

        self._daily_pnl_pts += pnl_pts * self.quantity
        self._daily_commission += commission
        # [459차 F1] 승패는 포지션 누적 총합으로 판정 — partial_close를 거친
        # 잔량 청산이면 이 레그의 pnl_pts만으로는 포지션 손익을 대표하지 못한다.
        # 동률(총합 0.0)은 패 — 종전 레그 단위 `>0` 규약과 같은 방향(변경 금지).
        self._pos_acc_pnl_pts += pnl_pts * self.quantity
        self._pos_acc_fwd_pnl_pts += forward_pnl_pts * self.quantity
        self._daily_trades  += 1
        if self._pos_acc_pnl_pts > 0:
            self._daily_wins += 1
        self._daily_forward_pnl_pts += forward_pnl_pts * self.quantity
        self._daily_forward_commission += forward_commission
        self._daily_forward_trades += 1
        if self._pos_acc_fwd_pnl_pts > 0:
            self._daily_forward_wins += 1

        entry_ts_str = (
            self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.entry_time else ""
        )
        result = {
            "direction":    self.status,
            "executed_direction": self.status,
            "raw_direction": forward_direction,
            "entry_price":  self.entry_price,
            "exit_price":   exit_price,
            "quantity":     self.quantity,
            "pnl_pts":      round(pnl_pts, 4),
            "pnl_krw":      round(pnl_krw, 0),
            "forward_pnl_pts": round(forward_pnl_pts, 4),
            "forward_pnl_krw": round(forward_pnl_krw, 0),
            "commission":   round(commission, 0),
            "forward_commission": round(forward_commission, 0),
            "exit_reason":  reason,
            "hold_minutes": self._hold_minutes(),
            "entry_ts":     entry_ts_str,
            "grade":        self.grade,
            "entry_horizon": self.entry_horizon,
            "reverse_entry_enabled": self.reverse_entry_enabled,
        }

        logger.info(
            f"[Position] 청산 {self.status} @ {exit_price} "
            f"| PnL={pnl_pts:+.2f}pt ({pnl_krw:+,.0f}원) 수수료={commission:,.0f}원 | {reason}"
        )

        # 초기화
        self.last_update_reason = f"close_position:{reason}"
        self.last_update_ts = now_kst()
        self._reset_position()
        return result

    def apply_entry_fill(
        self,
        direction: str,
        price: float,
        quantity: int,
        atr: float,
        grade: str = "B",
        regime: str = "NEUTRAL",
        filled_at: Optional[datetime.datetime] = None,
        raw_direction: Optional[str] = None,
        reverse_entry_enabled: bool = False,
        entry_horizon: Optional[str] = None,
    ) -> Dict:
        """Chejan 체결 기준으로 포지션을 오픈하거나 증액한다."""
        assert direction in (POSITION_LONG, POSITION_SHORT), f"Invalid direction: {direction}"
        assert quantity > 0, f"Invalid fill quantity: {quantity}"

        if self._optimistic and self.status == direction:
            # 투기적 오픈(open_position) 후 Chejan이 실제 체결가로 보정
            self.entry_price = price
            if filled_at:
                self.entry_time = filled_at
            self._optimistic = False
            self.signal_direction = raw_direction or self.signal_direction or direction
            self.reverse_entry_enabled = bool(reverse_entry_enabled or self.reverse_entry_enabled)
            self.trailing_anchor_price = price
            self._recalculate_levels(atr)
            self.last_update_reason = f"apply_entry_fill_correction:{direction}"
            self.last_update_ts = filled_at or now_kst()
            self._save_state()
            logger.info(
                f"[Position] 체결보정 {direction} {quantity}계약 @ {price} "
                f"| 평균={self.entry_price:.2f} 보유={self.quantity}계약"
            )
            return {
                "direction": self.status,
                "fill_price": round(price, 4),
                "filled_qty": quantity,
                "avg_entry_price": round(self.entry_price, 4),
                "position_qty": self.quantity,
                "entry_ts": (
                    self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
                    if self.entry_time else ""
                ),
                "grade": self.grade,
                "regime": self.regime,
            }

        _is_new_position = (self.status == POSITION_FLAT)

        if self.status == POSITION_FLAT:
            self.status = direction
            self.entry_price = price
            self.quantity = quantity
            self.initial_quantity = quantity
            self.entry_quantity = quantity
            self.trailing_anchor_price = price
            self.entry_time = filled_at or now_kst()
            self.grade = grade
            self.regime = regime
            self.signal_direction = raw_direction or direction
            self.reverse_entry_enabled = bool(reverse_entry_enabled)
            self.entry_horizon = entry_horizon
        else:
            assert self.status == direction, (
                f"Opposite fill mismatch: status={self.status} fill={direction}"
            )
            total_qty = self.quantity + quantity
            self.entry_price = (
                (self.entry_price * self.quantity) + (price * quantity)
            ) / total_qty
            self.quantity = total_qty
            self.initial_quantity = max(int(self.initial_quantity or 0), total_qty)
            # [421차] 추가진입은 진입 규모가 실제로 커진 것이므로 함께 올린다
            # (줄지 않을 뿐, 증가는 정상 — 위 필드 주석 참조).
            self.entry_quantity = max(int(self.entry_quantity or 0), total_qty)
            self.grade = grade or self.grade
            self.regime = regime or self.regime
            self.signal_direction = raw_direction or self.signal_direction or direction
            self.reverse_entry_enabled = bool(reverse_entry_enabled or self.reverse_entry_enabled)
            if self.entry_time is None:
                self.entry_time = filled_at or now_kst()
            if entry_horizon and not self.entry_horizon:
                self.entry_horizon = entry_horizon

        self._recalculate_levels(atr)
        # 신규 포지션(FLAT→진입)일 때만 partial_done 리셋
        # 분할체결·증량 시에는 이미 실행된 TP 플래그를 보존하여 재발동 방지
        if _is_new_position:
            self.partial_1_done = False
            self.partial_2_done = False
            self.partial_3_done = False
            self._pos_acc_pnl_pts = 0.0       # [459차 F1] FLAT→진입만 초기화 (증량 시 보존)
            self._pos_acc_fwd_pnl_pts = 0.0
        self.last_update_reason = f"apply_entry_fill:{direction}"
        self.last_update_ts = filled_at or now_kst()
        self._save_state()

        logger.info(
            f"[Position] 체결진입 {direction} {quantity}계약 @ {price} "
            f"| 평균={self.entry_price:.2f} 보유={self.quantity}계약"
        )
        return {
            "direction": self.status,
            "fill_price": round(price, 4),
            "filled_qty": quantity,
            "avg_entry_price": round(self.entry_price, 4),
            "position_qty": self.quantity,
            "entry_ts": (
                self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
                if self.entry_time else ""
            ),
            "grade": self.grade,
            "regime": self.regime,
        }

    def apply_exit_fill(
        self,
        exit_price: float,
        quantity: int,
        reason: str,
        filled_at: Optional[datetime.datetime] = None,
        shrink_initial: bool = False,
    ) -> Dict:
        """Chejan 체결 기준으로 포지션을 부분/전량 청산한다.

        승패 규약 [459차 F1]: 전량 청산(is_final) 시 포지션의 레그 누적
        Σ(pnl_pts×qty) > 0 이면 승, **동률(0.0)은 패**(종전 `>0` 판정과 같은
        방향 — 과거 통계 불연속 방지, 변경 금지). 수수료는 판정에 미반영(종전 동일).

        shrink_initial: [360차] True면 quantity 차감과 동시에 initial_quantity도
        같은 폭만큼 줄인다. 손절 계단화 1차 축소처럼 "TP 단계 진행과 무관한 이유"로
        수량이 줄었을 때, _sync_partial_progress()의 목표수량 매칭이 우연히 맞아떨어져
        partial_1_done이 오염되는 것을 막는다(잔여 포지션이 "처음부터 이 수량이었던
        새 포지션"처럼 TP 진행률 0으로 유지되어 TP1을 정상적으로 다시 노릴 수 있다).
        기존 호출부(TP1/2/3, 외부체결 동기화 등)는 이 인자를 넘기지 않으므로 기본값
        False로 동작 100% 보존.
        """
        assert self.status != POSITION_FLAT, "포지션 없음"
        assert 0 < quantity <= self.quantity, (
            f"Invalid exit fill quantity: fill={quantity} total={self.quantity}"
        )

        mult = 1 if self.status == POSITION_LONG else -1
        pnl_pts = (exit_price - self.entry_price) * mult
        commission = _calc_commission(self.entry_price, quantity, self._pt_value) * 2  # 왕복
        pnl_krw = pnl_pts * self._pt_value * quantity - commission
        forward_direction = self.signal_direction or self.status
        forward_pnl_pts = self._calc_directional_pnl_pts(forward_direction, exit_price)
        forward_commission = _calc_commission(self.entry_price, quantity, self._pt_value) * 2
        forward_pnl_krw = forward_pnl_pts * self._pt_value * quantity - forward_commission
        self._daily_pnl_pts += pnl_pts * quantity
        self._daily_commission += commission
        self._daily_forward_pnl_pts += forward_pnl_pts * quantity
        self._daily_forward_commission += forward_commission
        # [459차 F1] 레그 실현손익을 포지션 누적기에 쌓는다 — 승패 판정은
        # is_final에서 누적 총합으로 1회. 종전에는 마지막 레그 pnl_pts만 봐서
        # (-3.04pt×2, +0.70pt×1) 순손실 포지션이 승으로 집계됐다.
        self._pos_acc_pnl_pts += pnl_pts * quantity
        self._pos_acc_fwd_pnl_pts += forward_pnl_pts * quantity

        is_final = quantity == self.quantity
        if is_final:
            # 동률(총합 0.0)은 패 — 종전 레그 단위 `>0` 규약과 같은 방향(변경 금지).
            self._daily_trades += 1
            if self._pos_acc_pnl_pts > 0:
                self._daily_wins += 1
            self._daily_forward_trades += 1
            if self._pos_acc_fwd_pnl_pts > 0:
                self._daily_forward_wins += 1

        result = self._build_exit_result(
            exit_price=exit_price,
            quantity=quantity,
            pnl_pts=pnl_pts,
            pnl_krw=pnl_krw,
            reason=reason,
            filled_at=filled_at,
        )
        result["forward_pnl_pts"] = round(forward_pnl_pts, 4)
        result["forward_pnl_krw"] = round(forward_pnl_krw, 0)
        result["forward_commission"] = round(forward_commission, 0)

        if is_final:
            # ── [MW0602 468차 F-2 / A안] 표시 계층에서만 보호트레일을 분리한다 ──────
            # `exit_reason` **문자열은 바꾸지 않는다.** 465차 P4가 같은 안(`보호트레일`
            # 라벨 신설)을 검토 후 기각했다 — `exit_reason LIKE '%하드스톱%'`가 사전등록
            # 채널 [15]·[26]·[48]과 `scripts/bar_stop_path_watch.py:134`(정확일치),
            # `tests/test_439_p2_slippage_judgment.py`의 필터라 갈아치우면 그 채널들의
            # 판정이 조용히 뒤집힌다(캠페인 거버넌스 위반).
            #
            # 그런데 같은 `하드스톱` 라벨에 **정반대 두 사건**이 들어 있다 — 진짜 손절과
            # TP1 도달 후 보호 스톱(이익 청산). 로그만 읽는 요약 도구는 그것을 구분할
            # 방법이 없어 오독을 자동 생산했다(0813 실측: `하드스톱` 2건이 **둘 다**
            # 보호 트레일인데 일일 점검이 "하드스톱·손절 계열 2/3건(67%)"으로 집계).
            # → DB에는 465차의 `tp1_reached` 컬럼을 그대로 쓰고, **로그 줄에만** 같은
            #   값을 태그로 덧붙인다. 손절 계열에만 붙여 TP 청산 줄은 건드리지 않는다.
            _stop_family = any(_k in str(reason) for _k in ("스톱", "손절"))
            _tp1_tag = ""
            if _stop_family:
                _tp1_tag = " [TP1보호]" if result.get("tp1_reached") else " [TP1미도달]"
            logger.info(
                f"[Position] 체결청산 {self.status} @ {exit_price} "
                f"| PnL={pnl_pts:+.2f}pt ({pnl_krw:+,.0f}원) | {reason}{_tp1_tag}"
            )
            self.last_update_reason = f"apply_exit_fill_final:{reason}"
            self.last_update_ts = filled_at or now_kst()
            self._reset_position()
        else:
            self.quantity -= quantity
            if shrink_initial:
                self.initial_quantity = max(0, self.initial_quantity - quantity)
                # [421차] `entry_quantity`는 **의도적으로 건드리지 않는다** — 여기서
                # 같이 줄이면 417차 `entry_qty` 기록 버그가 그대로 재발한다.
                # initial_quantity 축소는 TP 진행률 매칭용이지 "진입 규모 정정"이
                # 아니다. 이 불변식을 깨려면 tests/test_entry_qty_invariant.py를
                # 먼저 볼 것.
            self._sync_partial_progress()
            self.last_update_reason = f"apply_exit_fill_partial:{reason}"
            self.last_update_ts = filled_at or now_kst()
            self._save_state()
            result["remaining"] = self.quantity
            logger.info(
                f"[Position] 체결부분청산 {quantity}계약 @ {exit_price} "
                f"| 잔여={self.quantity}계약 | PnL={pnl_pts:+.2f}pt ({pnl_krw:+,.0f}원) | {reason}"
            )

        return result

    def sync_from_broker(
        self,
        direction: str,
        price: float,
        quantity: int,
        atr: float,
        *,
        synced_at: Optional[datetime.datetime] = None,
        grade: str = "BROKER",
        regime: str = "BROKER_SYNC",
    ) -> Dict:
        """브로커 잔고 스냅샷을 기준으로 포지션 상태를 강제 동기화한다."""
        assert direction in (POSITION_LONG, POSITION_SHORT), f"Invalid direction: {direction}"
        assert quantity > 0, f"Invalid broker quantity: {quantity}"

        prev_status = self.status
        prev_initial = max(int(self.initial_quantity or 0), int(self.quantity or 0))
        # [421차] entry_quantity는 shrink_initial의 영향을 받지 않으므로 prev_initial
        # 보다 크거나 같다 — 셋 중 최대를 취해 구버전 상태파일(entry_quantity 없음)
        # 에서 복원된 경우에도 종전과 동일한 값이 나오게 한다.
        prev_entry_qty = max(int(self.entry_quantity or 0), prev_initial)
        prev_entry_time = self.entry_time
        prev_stop = float(self.stop_price or 0.0)
        prev_anchor = float(self.trailing_anchor_price or 0.0)
        same_side_sync = prev_status == direction

        self.status = direction
        self.entry_price = price
        self.quantity = quantity
        self.entry_time = prev_entry_time if same_side_sync and prev_entry_time else (synced_at or now_kst())
        # 같은 방향 동기화 시 기존 신호 등급(A/B/C) 보존 — BROKER로 덮어쓰지 않음
        self.grade = grade if (not same_side_sync or not self.grade or self.grade == "BROKER") else self.grade
        self.regime = regime
        self.signal_direction = direction
        self.reverse_entry_enabled = False
        if same_side_sync and prev_initial > 0:
            self.initial_quantity = max(prev_initial, quantity)
            self.entry_quantity = max(prev_entry_qty, quantity)
        else:
            # 반대방향/신규 동기화는 별개 포지션이므로 진입 규모도 새로 잡는다.
            self.initial_quantity = quantity
            self.entry_quantity = quantity
        # 같은 방향 동기화 시 이미 실행된 TP 플래그 보존 (잔고 Chejan이 와도 재발동 방지)
        if not same_side_sync:
            self.partial_1_done = False
            self.partial_2_done = False
            self.partial_3_done = False
            self._pos_acc_pnl_pts = 0.0       # [459차 F1] 별개 포지션 — 레그 누적 초기화
            self._pos_acc_fwd_pnl_pts = 0.0
        self.last_update_reason = f"sync_from_broker:{direction}"
        self.last_update_ts = synced_at or now_kst()
        self._recalculate_levels(atr)
        if same_side_sync:
            if prev_stop > 0:
                if direction == POSITION_LONG:
                    self.stop_price = max(self.stop_price, prev_stop)
                else:
                    self.stop_price = min(self.stop_price, prev_stop)
            if prev_anchor > 0:
                if direction == POSITION_LONG:
                    self.trailing_anchor_price = max(prev_anchor, price)
                else:
                    self.trailing_anchor_price = min(prev_anchor, price)
            else:
                self.trailing_anchor_price = price
        else:
            self.trailing_anchor_price = price
        self._sync_partial_progress()
        self._save_state()

        logger.warning(
            f"[Position] 브로커 기준 동기화: {direction} {quantity}계약 @ {price} "
            f"| 손절={self.stop_price:.2f}"
        )
        return {
            "direction": self.status,
            "entry_price": round(self.entry_price, 4),
            "quantity": self.quantity,
            "entry_ts": (
                self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
                if self.entry_time else ""
            ),
        }

    def sync_flat_from_broker(self) -> None:
        """브로커 기준 무포지션 상태로 강제 동기화한다."""
        self.last_update_reason = "sync_flat_from_broker"
        self.last_update_ts = now_kst()
        self._reset_position()
        logger.warning("[Position] 브로커 기준 동기화: FLAT")

    def partial_close(self, exit_price: float, qty: int, reason: str) -> Dict:
        """부분 청산 — qty 계약만 청산하고 잔여 포지션 유지.

        _daily_trades는 증가시키지 않음 (최종 close_position에서만 카운트).
        """
        assert self.status != POSITION_FLAT, "포지션 없음"
        assert 0 < qty < self.quantity, (
            f"부분청산 수량 오류: qty={qty} total={self.quantity}"
        )

        mult    = 1 if self.status == POSITION_LONG else -1
        pnl_pts = (exit_price - self.entry_price) * mult
        commission = _calc_commission(self.entry_price, qty, self._pt_value) * 2  # 왕복
        pnl_krw = pnl_pts * self._pt_value * qty - commission
        forward_direction = self.signal_direction or self.status
        forward_pnl_pts = self._calc_directional_pnl_pts(forward_direction, exit_price)
        forward_commission = _calc_commission(self.entry_price, qty, self._pt_value) * 2
        forward_pnl_krw = forward_pnl_pts * self._pt_value * qty - forward_commission

        self._daily_pnl_pts += pnl_pts * qty
        self._daily_commission += commission
        self._daily_forward_pnl_pts += forward_pnl_pts * qty
        self._daily_forward_commission += forward_commission
        # [459차 F1] 최종 청산(close_position/is_final)의 포지션 단위 승패 판정용
        self._pos_acc_pnl_pts += pnl_pts * qty
        self._pos_acc_fwd_pnl_pts += forward_pnl_pts * qty
        self.quantity        -= qty
        self._sync_partial_progress()
        self.last_update_reason = f"partial_close:{reason}"
        self.last_update_ts = now_kst()

        entry_ts_str = (
            self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.entry_time else ""
        )
        result = {
            "direction":    self.status,
            "executed_direction": self.status,
            "raw_direction": forward_direction,
            "entry_price":  self.entry_price,
            "exit_price":   exit_price,
            "quantity":     qty,
            "remaining":    self.quantity,
            "pnl_pts":      round(pnl_pts, 4),
            "pnl_krw":      round(pnl_krw, 0),
            "forward_pnl_pts": round(forward_pnl_pts, 4),
            "forward_pnl_krw": round(forward_pnl_krw, 0),
            "exit_reason":  reason,
            "hold_minutes": self._hold_minutes(),
            "entry_ts":     entry_ts_str,
            "grade":        self.grade,
            "entry_horizon": self.entry_horizon,
            "forward_commission": round(forward_commission, 0),
            "reverse_entry_enabled": self.reverse_entry_enabled,
        }

        logger.info(
            f"[Position] 부분청산 {qty}계약 @ {exit_price} "
            f"| 잔여={self.quantity}계약 "
            f"| PnL={pnl_pts:+.2f}pt ({pnl_krw:+,.0f}원) | {reason}"
        )
        self._save_state()
        return result

    def arm_tp1_single_contract(self, current_price: float, atr: float = 0.0) -> Dict:
        """For single-contract positions, convert TP1 into protection instead of full exit."""
        assert self.status != POSITION_FLAT, "포지션 없음"
        assert self.quantity == 1, f"single-contract only: qty={self.quantity}"

        mult = 1 if self.status == POSITION_LONG else -1
        prev_stop = self.stop_price
        protected_stop = self.entry_price
        if mult * (prev_stop - protected_stop) > 0:
            protected_stop = prev_stop

        if mult * (protected_stop - self.stop_price) > 0:
            self.stop_price = protected_stop
            # [423차] 이 경로가 유령 하드스톱의 주 발생원 — 틱 핸들러가 분봉 도중
            # 호출하므로 조이기 시각을 남겨 봉중 판정에서 그 봉을 배제한다.
            self._mark_stop_tightened("arm_tp1_qty1")

        self.partial_1_done = True
        self._sync_partial_progress()
        self.last_update_reason = "arm_tp1_single_contract"
        self.last_update_ts = now_kst()
        self._save_state()

        logger.info(
            f"[Position] 1계약 TP1 암(arm) @ {current_price:.2f} "
            f"| stop {prev_stop:.2f} -> {self.stop_price:.2f}"
        )
        return {
            "direction": self.status,
            "entry_price": round(self.entry_price, 4),
            "current_price": round(current_price, 4),
            "prev_stop_price": round(prev_stop, 4),
            "new_stop_price": round(self.stop_price, 4),
            "tp1_price": round(self.tp1_price, 4),
            "tp2_price": round(self.tp2_price, 4),
            "quantity": self.quantity,
        }

    def arm_tp1_single_contract_with_mode(
        self,
        current_price: float,
        atr: float = 0.0,
        mode: str = "breakeven",
        alpha_pts: float = 0.20,
        atr_lock_mult: float = 0.25,
    ) -> Dict:
        """For single-contract positions, convert TP1 into protection instead of full exit."""
        assert self.status != POSITION_FLAT, "FLAT 상태에서 TP1 암 호출 불가"
        assert self.quantity == 1, f"single-contract only: qty={self.quantity}"

        mult = 1 if self.status == POSITION_LONG else -1
        prev_stop = self.stop_price
        mode = str(mode or "breakeven").strip().lower()

        protect_offset_pts = 0.0
        if mode == "breakeven_plus":
            protect_offset_pts = max(float(alpha_pts or 0.0), 0.0)
        elif mode == "atr_profit":
            protect_offset_pts = max(float(atr or 0.0) * float(atr_lock_mult or 0.0), 0.0)

        protected_stop = self.entry_price + mult * protect_offset_pts
        if mult * (prev_stop - protected_stop) > 0:
            protected_stop = prev_stop

        if mult * (protected_stop - self.stop_price) > 0:
            self.stop_price = protected_stop
            # [423차] 이 경로가 유령 하드스톱의 주 발생원 — 틱 핸들러가 분봉 도중
            # 호출하므로 조이기 시각을 남겨 봉중 판정에서 그 봉을 배제한다.
            self._mark_stop_tightened("arm_tp1_qty1_mode")

        self.partial_1_done = True

        # [339차 후속] 회계적 분할청산(synthetic partial) — 실제로는 못 쪼개는 1계약을
        # "TP1 도달가에서 PARTIAL_EXIT_RATIOS[0](33%)를 확정했다"고 회계상으로만 기록.
        # 물리적 계약수·스탑 관리(위 protected_stop)와는 완전히 별개이며, 이 값은
        # CB/Kelly 등 실시간 리스크 판단에는 전달하지 않고(부록 참조) DB·대시보드
        # 표시용으로만 쓴다.
        self.synthetic_tp1_price = round(current_price, 4)
        self.synthetic_tp1_pnl_pts = round((current_price - self.entry_price) * mult, 4)
        self.synthetic_tp1_fraction = PARTIAL_EXIT_RATIOS[0]
        self.synthetic_tp1_ts = now_kst()

        self._sync_partial_progress()
        self.last_update_reason = f"arm_tp1_single_contract:{mode}"
        self.last_update_ts = now_kst()
        self._save_state()

        logger.info(
            f"[Position] 1계약 TP1 보호전환 @ {current_price:.2f} "
            f"| mode={mode} | stop {prev_stop:.2f} -> {self.stop_price:.2f} "
            f"| 회계상 확정 {self.synthetic_tp1_fraction:.0%} @ {self.synthetic_tp1_pnl_pts:+.2f}pt"
        )
        return {
            "direction": self.status,
            "entry_price": round(self.entry_price, 4),
            "current_price": round(current_price, 4),
            "prev_stop_price": round(prev_stop, 4),
            "new_stop_price": round(self.stop_price, 4),
            "mode": mode,
            "protect_offset_pts": round(protect_offset_pts, 4),
            "tp1_price": round(self.tp1_price, 4),
            "tp2_price": round(self.tp2_price, 4),
            "quantity": self.quantity,
            "synthetic_tp1_price": self.synthetic_tp1_price,
            "synthetic_tp1_pnl_pts": self.synthetic_tp1_pnl_pts,
            "synthetic_tp1_fraction": self.synthetic_tp1_fraction,
        }

    def update_trailing_stop(self, current_price: float, atr: float):
        """트레일링 스톱 업데이트"""
        if self.status == POSITION_FLAT:
            return

        _prev = self.stop_price
        self.trailing_anchor_price, self.stop_price = compute_trailing_stop_tier(
            self.entry_price, self.status, atr, current_price,
            self.trailing_anchor_price, self.stop_price,
        )
        # [423차] 값이 실제로 바뀐 때만 시각을 갱신한다. 매분 호출되므로 무조건
        # 찍으면 stop_updated_at이 항상 "이번 봉"이 되어 봉중 판정이 영구 무력화된다.
        # 이 경로는 호출측 `_prev_stop_price`가 이미 되돌리고 있어 중복 방어지만,
        # 틱 경로와 기준을 하나로 맞춰 두는 편이 이후 회귀에 안전하다.
        if abs(self.stop_price - _prev) > 1e-9:
            self._mark_stop_tightened("trailing")

    def _mark_stop_tightened(self, path: str, live_guard: bool = True) -> None:
        """[MW0602 424차] 스톱 조이기 시각 기록 — 라이브 가드 / 섀도 이원화.

        `live_guard=True`  → 423차 가드용 `stop_updated_at`과 섀도를 **둘 다** 갱신.
        `live_guard=False` → 섀도만 갱신한다. 봉중 판정은 종전 그대로 살아 있으므로
                             **라이브 청산 동작이 바뀌지 않는다**(main.py의 qty>=2
                             TP1 손익분기 경로가 이쪽을 쓴다).

        두 필드를 한 곳에서만 쓰도록 묶은 이유: 423차는 조이기 지점 4곳 중 3곳만
        계측했고 main.py의 네 번째 지점이 빠져 가드가 통째로 우회됐다. 대입을
        분산시키면 같은 누락이 또 생긴다.
        """
        _now = now_kst()
        if live_guard:
            self.stop_updated_at = _now
        self.stop_shadow_tightened_at = _now
        self.stop_shadow_tighten_path = path

    def mark_stop_tightened_shadow(self, path: str) -> None:
        """[424차] 섀도 전용 기록 (라이브 가드 무변경). main.py에서 호출."""
        self._mark_stop_tightened(path, live_guard=False)

    def would_guard_suppress_intrabar(
        self, bar_start: "Optional[datetime.datetime]" = None
    ) -> bool:
        """[424차] "가드가 모든 조이기 경로를 덮었다면 봉중 판정을 억제했을까".

        `is_stop_hit_intrabar()`의 억제 조건과 같은 식이되 **섀도 시각**을 본다.
        판정만 하고 아무것도 바꾸지 않는다 — 계측 전용.
        """
        return bool(
            bar_start is not None
            and self.stop_shadow_tightened_at is not None
            and self.stop_shadow_tightened_at >= bar_start
        )

    def is_stop_hit(self, price: float) -> bool:
        if self.status == POSITION_FLAT:
            return False
        if self.status == POSITION_LONG:
            return price <= self.stop_price
        return price >= self.stop_price

    def is_stop_hit_intrabar(
        self,
        bar_low: float,
        bar_high: float,
        stop_price: float = None,
        bar_start: "Optional[datetime.datetime]" = None,
    ) -> bool:
        """분봉 고저가로 스톱 히트 판단 — 종가 기준보다 빠른 감지 (Proposal D)

        stop_price를 명시하지 않으면 현재 self.stop_price를 사용한다. 봉 내에서
        트레일링 스톱이 이미 갱신된 뒤 호출하는 경우, 그 봉의 고저가는 갱신 전
        스톱 기준으로 형성된 것이므로 호출측에서 갱신 전 stop_price를 넘겨야
        "유령 하드스톱"(갱신된 스톱을 과거 고저가에 소급 적용)을 피할 수 있다.

        [MW0602 423차] 위 `stop_price` 인자만으로는 **틱 경로가 조인 스톱**을 막지
        못한다. 호출측(`_ts_check_exit_triggers`)의 `_prev_stop_price`는 그 함수
        안에서 `update_trailing_stop()`이 조인 것만 되돌리는데, TP1 보호전환은
        COM 틱 핸들러가 **함수 밖에서 비동기로** stop_price를 바꾸므로 그 시점엔
        이미 조여진 값이 `_prev_stop_price`로 들어온다.

        2026-08-03 실측: 비틱 `하드스톱` 청산 8건이 **전부** 이 경로였다. 예)
        13:49:54 진입 SHORT@988.88 → 13:50:09 틱 TP1이 스톱을 991.00→988.53으로
        조임 → 13:50:55 파이프라인이 분봉 13:50의 고가 988.94(≥988.53)로 히트
        판정. 그 고가는 13:50:00~13:50:09 사이, **조이기 이전**에 찍힌 값이다.

        그래서 `bar_start`(평가 대상 분봉의 시작시각)를 받아, 스톱이 그 봉 안에서
        조여졌으면(`stop_updated_at >= bar_start`) 봉중 판정을 포기한다. 종가 기준
        `is_stop_hit()`은 그대로 살아 있으므로 **진짜 스톱 히트를 놓치지 않는다** —
        다음 봉부터는 새 스톱으로 정상 판정된다.
        `bar_start`를 넘기지 않으면 종전과 완전히 동일하게 동작한다(하위호환).
        """
        if self.status == POSITION_FLAT:
            return False
        if (
            bar_start is not None
            and self.stop_updated_at is not None
            and self.stop_updated_at >= bar_start
        ):
            return False
        _stop = self.stop_price if stop_price is None else stop_price
        if self.status == POSITION_LONG:
            return bar_low <= _stop
        return bar_high >= _stop

    def is_tp1_hit(self, price: float) -> bool:
        if self.status == POSITION_FLAT or self.partial_1_done:
            return False
        if self.status == POSITION_LONG:
            return price >= self.tp1_price
        return price <= self.tp1_price

    def is_tp2_hit(self, price: float) -> bool:
        if self.status == POSITION_FLAT or self.partial_2_done:
            return False
        if self.status == POSITION_LONG:
            return price >= self.tp2_price
        return price <= self.tp2_price

    def is_tp3_hit(self, price: float) -> bool:
        if self.status == POSITION_FLAT or self.partial_3_done:
            return False
        if self.status == POSITION_LONG:
            return price >= self.tp3_price
        return price <= self.tp3_price

    def is_loss_tier1_hit(self, price: float) -> bool:
        """[360차] 손절 계단화 1차 — entry~stop 절반 지점 도달 여부.

        qty==1은 물리적으로 분할 불가하므로 대상에서 제외(339차 atr_profit 보호와
        영역이 겹치지 않는다).
        """
        if (self.status == POSITION_FLAT or self.loss_tier1_done
                or self.quantity <= 1 or self.loss_tier1_price <= 0):
            return False
        if self.status == POSITION_LONG:
            return price <= self.loss_tier1_price
        return price >= self.loss_tier1_price

    def get_loss_tier1_exit_qty(self) -> int:
        """[360차] 손절 계단화 1차 축소 수량 — 최소 1계약 잔여 보장(전량청산 금지)."""
        if self.quantity <= 1:
            return 0
        cut = max(1, round(self.quantity * LOSS_TIER1_CUT_RATIO))
        return min(cut, self.quantity - 1)

    def is_loss_tier1_qty1_shadow_hit(self, price: float) -> bool:
        """[363차] qty=1 손실1차 섀도 — is_loss_tier1_hit()가 qty<=1이라 제외하는 바로 그
        케이스를 계측 전용으로 별도 판정한다. 실거래 액션은 전혀 없음(기록만) — §9
        사전등록 원칙에 따라 VALIDATION_CAMPAIGN 누적판정 후 채택 여부를 수동 결정한다.
        포지션당 1회만 True(loss_tier1_qty1_shadow_logged로 중복 기록 방지).
        """
        if (self.status == POSITION_FLAT or self.loss_tier1_qty1_shadow_logged
                or self.quantity != 1 or self.loss_tier1_price <= 0):
            return False
        if self.status == POSITION_LONG:
            return price <= self.loss_tier1_price
        return price >= self.loss_tier1_price

    def is_loss_tier2_shadow_hit(self, price: float) -> bool:
        """[367차] Tier1 발동 후 잔여계약 2단계 조기청산 섀도 — Tier1이 qty=2 중
        1계약만 잘라내고 남은 1계약은 원래 stop_price까지 그대로 노출되는 사각지대
        (0722 딥다이브: 07-22 10:26 사례에서 형제계약 tier1 성공 후 잔여 1계약이
        추가 방어 없이 하드스톱까지 밀림)를 계측 전용으로 기록한다. 실거래 액션
        없음(기록만) — loss_tier1_qty1_shadow와 동일 원칙. loss_tier2_price는
        Tier1 체결 시점(main.py:_ts_handle_exit_fill)에 계산되므로, 그 전에는
        0.0으로 자연히 비활성.
        """
        if (self.status == POSITION_FLAT or not self.loss_tier1_done
                or self.loss_tier2_shadow_logged or self.loss_tier2_price <= 0):
            return False
        if self.status == POSITION_LONG:
            return price <= self.loss_tier2_price
        return price >= self.loss_tier2_price

    def get_stage_plan(self) -> Tuple[int, int, int]:
        total_qty = int(self.initial_quantity or self.quantity or 0)
        if total_qty <= 0:
            return (0, 0, 0)
        if total_qty == 1:
            return (1, 0, 0)
        if total_qty == 2:
            return (1, 1, 0)

        raw = [
            total_qty * 0.33,
            total_qty * 0.33,
            total_qty * 0.34,
        ]
        plan = [int(value) for value in raw]
        remainder = total_qty - sum(plan)
        order = sorted(
            range(3),
            key=lambda idx: (raw[idx] - plan[idx], idx == 2, -idx),
            reverse=True,
        )
        for idx in order:
            if remainder <= 0:
                break
            plan[idx] += 1
            remainder -= 1
        return tuple(plan)

    def get_stage_targets(self) -> Tuple[int, int, int]:
        q1, q2, q3 = self.get_stage_plan()
        return (q1, q1 + q2, q1 + q2 + q3)

    def get_closed_quantity(self) -> int:
        if self.status == POSITION_FLAT and self.initial_quantity <= 0:
            return 0
        current_qty = max(int(self.quantity or 0), 0)
        initial_qty = max(int(self.initial_quantity or 0), current_qty)
        return max(0, initial_qty - current_qty)

    def get_stage_exit_qty(self, stage: int) -> int:
        stage = int(stage or 0)
        if stage < 1 or stage > 3:
            return 0
        targets = self.get_stage_targets()
        closed_qty = self.get_closed_quantity()
        needed = max(0, targets[stage - 1] - closed_qty)
        return min(max(int(self.quantity or 0), 0), needed)

    def resolve_stage_for_exit_qty(self, exit_qty: int, *, full_close: bool = False) -> int:
        exit_qty = max(int(exit_qty or 0), 0)
        if exit_qty <= 0:
            return 0
        if full_close:
            return 3
        targets = self.get_stage_targets()
        closed_after = self.get_closed_quantity() + exit_qty
        if closed_after >= targets[2]:
            return 3
        if closed_after >= targets[1]:
            return 2
        if closed_after >= targets[0]:
            return 1
        return 0

    def unrealized_pnl_pts(self, current_price: float) -> float:
        if self.status == POSITION_FLAT:
            return 0.0
        mult = 1 if self.status == POSITION_LONG else -1
        return (current_price - self.entry_price) * mult * self.quantity

    def unrealized_forward_pnl_pts(self, current_price: float) -> float:
        if self.status == POSITION_FLAT:
            return 0.0
        return self._calc_directional_pnl_pts(
            self.signal_direction or self.status,
            current_price,
        ) * self.quantity

    def _hold_minutes(self) -> int:
        if not self.entry_time:
            return 0
        delta = now_kst() - self.entry_time
        return int(delta.total_seconds() // 60)

    def _recalculate_levels(self, atr: float) -> None:
        mult = 1 if self.status == POSITION_LONG else -1
        _tp1_mult = (
            ATR_HORIZON_TP1_MULT.get(self.entry_horizon, ATR_TP1_MULT)
            if self.entry_horizon else ATR_TP1_MULT
        )
        _stop_mult, _tp2_mult = ATR_STOP_MULT, ATR_TP2_MULT
        _regime_mult = (
            HURST_REGIME_ATR_MULT.get(self.entry_hurst_bucket)
            if HURST_REGIME_ATR_MULT_ENABLED and self.entry_hurst_bucket else None
        )
        if _regime_mult:
            _stop_mult = ATR_STOP_MULT * _regime_mult.get("stop", 1.0)
            _tp1_mult  = _tp1_mult     * _regime_mult.get("tp1", 1.0)
            _tp2_mult  = ATR_TP2_MULT  * _regime_mult.get("tp2", 1.0)
        # [349차] 체결보정·브로커동기화로 재계산될 때도 진입 시점 급변장 스톱확대
        # 배수를 유지 — getattr 기본값 1.0은 이 필드가 없던 구버전 저장 상태 호환용.
        _stop_mult = _stop_mult * float(getattr(self, "entry_extra_stop_mult", 1.0) or 1.0)
        self.stop_price = self.entry_price - mult * atr * _stop_mult
        self.tp1_price = self.entry_price + mult * atr * _tp1_mult
        self.tp2_price = self.entry_price + mult * atr * _tp2_mult
        self.tp3_price = self.entry_price + mult * atr * ATR_TP3_MULT

    def get_trailing_reference_price(self, current_price: float, atr: float) -> float:
        if self.status == POSITION_FLAT:
            return 0.0
        mult = 1 if self.status == POSITION_LONG else -1
        unrealized_pts = (current_price - self.entry_price) * mult
        if unrealized_pts >= atr * 2.0:
            return float(self.trailing_anchor_price or current_price or self.entry_price)
        if unrealized_pts >= atr * 1.5:
            return self.entry_price + mult * atr * 0.5
        if unrealized_pts >= atr * 1.0:
            return self.entry_price
        if unrealized_pts >= atr * 0.5:
            return self.entry_price - mult * atr * 0.75
        return self.entry_price - mult * atr * ATR_STOP_MULT

    def _sync_partial_progress(self) -> None:
        target_1, target_2, target_3 = self.get_stage_targets()
        closed_qty = self.get_closed_quantity()
        self.partial_1_done = bool(self.partial_1_done or (target_1 > 0 and closed_qty >= target_1))
        self.partial_2_done = bool(self.partial_2_done or (target_2 > 0 and closed_qty >= target_2))
        self.partial_3_done = bool(self.partial_3_done or (target_3 > 0 and closed_qty >= target_3))

    def _build_exit_result(
        self,
        exit_price: float,
        quantity: int,
        pnl_pts: float,
        pnl_krw: float,
        reason: str,
        filled_at: Optional[datetime.datetime] = None,
    ) -> Dict:
        entry_ts_str = (
            self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.entry_time else ""
        )
        return {
            "direction": self.status,
            "executed_direction": self.status,
            "raw_direction": self.signal_direction or self.status,
            "entry_price": self.entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "pnl_pts": round(pnl_pts, 4),
            "pnl_krw": round(pnl_krw, 0),
            "exit_reason": reason,
            "hold_minutes": self._hold_minutes(),
            "entry_ts": entry_ts_str,
            "exit_ts": (
                (filled_at or now_kst()).strftime("%Y-%m-%d %H:%M:%S")
            ),
            "grade": self.grade,
            "entry_horizon": self.entry_horizon,
            "reverse_entry_enabled": self.reverse_entry_enabled,
            # [MW0601 417차 / ②] 진입 계약수 — 위 "quantity"는 **이번 청산 레그의
            # 수량**이라 부분청산이면 진입 규모와 다르다. 사이징 축 분석이 그 둘을
            # 혼동해 "계약수가 클수록 진다"를 인과 없이 만들어낸 사고가 네 번
            # 반복돼(311차→402차→405차→409차) 기록 측에 값을 남긴다.
            # [MW0601 421차] 출처를 `initial_quantity` → `entry_quantity`로 교체.
            # 전자는 360차 shrink_initial이 깎으므로 손절1차를 거친 포지션에서
            # 진입 규모가 아니라 "그 시점 잔여치"가 찍혔다(08-03 10:19 실측: 3계약
            # 진입인데 레그별 2·1로 기록). 폴백 순서는 구버전 상태파일에서 복원된
            # 직후(entry_quantity=0)를 위한 것으로, 종전 동작을 그대로 보존한다.
            "entry_qty": int(
                self.entry_quantity or self.initial_quantity or self.quantity or 0
            ),
            # [MW0602 465차 P4] 이 청산 시점에 TP1이 이미 도달돼 있었는가.
            # `exit_reason`이 "하드스톱"이어도 여기가 1이면 그것은 손절이 아니라
            # 보호 스톱(이익 트레일)이다 — 두 사건이 같은 라벨을 공유하기 때문에
            # 기록 측에 구분값을 남긴다(utils/db_utils.py `tp1_reached` 주석 참조).
            # `partial_1_done`은 qty≥2 TP1 부분청산과 qty=1 보호전환
            # (`arm_tp1_single_contract_with_mode`) 양쪽에서 True가 된다.
            "tp1_reached": 1 if self.partial_1_done else 0,
        }

    def _reset_position(self) -> None:
        self.status = POSITION_FLAT
        self.entry_price = 0.0
        self.quantity = 0
        self.entry_time = None
        self.grade = ""
        self.regime = ""
        self.signal_direction = ""
        self.reverse_entry_enabled = False
        self.entry_horizon = None
        self.entry_extra_stop_mult = 1.0
        self.stop_price = 0.0
        self.stop_updated_at = None
        self.stop_shadow_tightened_at = None   # [424차]
        self.stop_shadow_tighten_path = None   # [424차]
        self.tp1_price = 0.0
        self.tp2_price = 0.0
        self.tp3_price = 0.0
        self.trailing_anchor_price = 0.0
        self.partial_1_done = False
        self.partial_2_done = False
        self.partial_3_done = False
        self.initial_quantity = 0
        self.entry_quantity = 0
        self.loss_tier1_price = 0.0
        self.loss_tier1_done = False
        self.loss_tier1_qty1_shadow_logged = False
        self.loss_tier2_price = 0.0
        self.loss_tier2_shadow_logged = False
        self.entry_quantile_expected_pt = None
        self.entry_quantile_uncertainty_pt = None
        self.synthetic_tp1_price = None
        self.synthetic_tp1_pnl_pts = None
        self.synthetic_tp1_fraction = None
        self.synthetic_tp1_ts = None
        self._pos_acc_pnl_pts = 0.0       # [459차 F1] 판정은 이미 끝났다 — 다음 포지션 대비 초기화
        self._pos_acc_fwd_pnl_pts = 0.0
        self._optimistic = False
        self.last_update_ts = self.last_update_ts or now_kst()
        self._save_state()

    # ── 일일 통계 ──────────────────────────────────────────────
    def daily_stats(self) -> dict:
        gross_krw = round(self._daily_pnl_pts * self._pt_value, 0)
        return {
            "trades":     self._daily_trades,
            "wins":       self._daily_wins,
            "losses":     self._daily_trades - self._daily_wins,
            "win_rate":   self._daily_wins / max(self._daily_trades, 1),
            "pnl_pts":    round(self._daily_pnl_pts, 4),
            "pnl_krw":    round(gross_krw - self._daily_commission, 0),  # 수수료 차감 순손익
            "gross_krw":  gross_krw,
            "commission": round(self._daily_commission, 0),
        }

    def daily_forward_stats(self) -> dict:
        gross_krw = round(self._daily_forward_pnl_pts * self._pt_value, 0)
        return {
            "trades": self._daily_forward_trades,
            "wins": self._daily_forward_wins,
            "losses": self._daily_forward_trades - self._daily_forward_wins,
            "win_rate": self._daily_forward_wins / max(self._daily_forward_trades, 1),
            "pnl_pts": round(self._daily_forward_pnl_pts, 4),
            "pnl_krw": round(gross_krw - self._daily_forward_commission, 0),
            "gross_krw": gross_krw,
            "commission": round(self._daily_forward_commission, 0),
        }

    def restore_daily_stats(self, rows) -> None:
        """재시작 시 trades.db 당일 행으로 일일 통계 복원 — 포지션 단위 [459차 F1].

        trades.db 행은 **청산 레그** 단위다(pnl_pts=계약당, quantity=레그 수량 —
        TP1/TP2/TP3 부분청산이 각각 한 행). 손익·수수료는 종전대로 레그별 누적하되,
        trades/wins는 entry_ts로 레그를 묶어 포지션 단위로 센다(라이브 경로
        apply_exit_fill is_final과 동일 단위 — 종전 레그 단위 카운트는 재기동일
        트레이드 수를 레그 수만큼 부풀렸다).

        규약:
        - 승패: 포지션 누적 Σ(pnl_pts×qty) > 0 = 승. 동률(0.0)은 패(종전 `>0`
          판정과 같은 방향 — 과거 통계 불연속 방지, 변경 금지).
        - entry_ts가 빈 레그는 포지션 귀속 불가 → 종전대로 행 단위 1트레이드.
        - 미청산 행(exit_price IS NULL)은 손익·카운트 모두 제외(종전에는 0pt
          1패로 세던 잠재 결함 — fetch_today_trades는 원래 청산 행만 주지만
          호출부가 미청산 행을 섞어도 안전하게).
        - 현재 보유 중(load_state 선복원) 포지션의 기청산 레그 그룹은 손익만
          누적하고 trades/wins에서 제외 — 잔량 청산 시 라이브 경로가
          _pos_acc_pnl_pts(상태 JSON에서 복원)로 1회 판정한다.
        """
        open_entry_ts = (
            self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.status != POSITION_FLAT and self.entry_time else ""
        )
        groups: Dict[str, Dict[str, float]] = {}

        for row in rows:
            keys = row.keys()
            if "exit_price" in keys and row["exit_price"] is None:
                continue  # 미청산 진입 행 — 실현손익 아님
            pnl_pts = float(row["pnl_pts"] or 0.0)
            qty     = int(row["quantity"] or 1)
            self._daily_pnl_pts += pnl_pts * qty
            forward_pnl_pts = float(
                row["forward_pnl_pts"]
                if "forward_pnl_pts" in keys and row["forward_pnl_pts"] is not None
                else pnl_pts
            )
            self._daily_forward_pnl_pts += forward_pnl_pts * qty
            # trades.db에 commission_krw 컬럼이 있으면 복원, 없으면 재계산
            commission = float(
                row["commission_krw"]
                if "commission_krw" in keys and row["commission_krw"] is not None
                else 0.0
            )
            if commission == 0.0 and "entry_price" in keys:
                ep = float(row["entry_price"] or 0.0)
                commission = _calc_commission(ep, qty, self._pt_value) * 2
            self._daily_commission += commission
            forward_commission = float(
                row["forward_commission_krw"]
                if "forward_commission_krw" in keys and row["forward_commission_krw"] is not None
                else commission
            )
            self._daily_forward_commission += forward_commission

            entry_ts = str(row["entry_ts"] or "") if "entry_ts" in keys else ""
            if entry_ts:
                g = groups.setdefault(entry_ts, {"pnl": 0.0, "fwd": 0.0})
                g["pnl"] += pnl_pts * qty
                g["fwd"] += forward_pnl_pts * qty
            else:
                # 포지션 귀속 불가 — 종전대로 행 단위 1트레이드
                self._daily_trades += 1
                if pnl_pts > 0:
                    self._daily_wins += 1
                self._daily_forward_trades += 1
                if forward_pnl_pts > 0:
                    self._daily_forward_wins += 1

        for entry_ts, g in groups.items():
            if entry_ts == open_entry_ts:
                continue  # 미완결 포지션 — 최종 청산 시 라이브 경로가 센다
            self._daily_trades += 1
            if g["pnl"] > 0:
                self._daily_wins += 1
            self._daily_forward_trades += 1
            if g["fwd"] > 0:
                self._daily_forward_wins += 1

    def reset_daily(self):
        self._daily_pnl_pts = 0.0
        self._daily_trades  = 0
        self._daily_wins    = 0
        self._daily_commission = 0.0
        self._daily_forward_pnl_pts = 0.0
        self._daily_forward_trades = 0
        self._daily_forward_wins = 0
        self._daily_forward_commission = 0.0

    # ── 포지션 상태 퍼시스턴스 ────────────────────────────────────

    def _save_state(self) -> None:
        """포지션 상태를 JSON 파일에 저장 — 재시작 시 복원용."""
        try:
            state = {
                "status":       self.status,
                "entry_price":  self.entry_price,
                "quantity":     self.quantity,
                "entry_time":   (self.entry_time.isoformat()
                                 if self.entry_time else None),
                "grade":        self.grade,
                "regime":       self.regime,
                "signal_direction": self.signal_direction,
                "reverse_entry_enabled": self.reverse_entry_enabled,
                "entry_horizon": self.entry_horizon,
                "entry_hurst_bucket": self.entry_hurst_bucket,
                "entry_extra_stop_mult": self.entry_extra_stop_mult,
                "stop_price":   self.stop_price,
                # [423차] 유령 하드스톱 가드용 조이기 시각. 장중 재기동 시 이 값이
                # 없으면 복원 직후 첫 봉에서 봉중 판정이 되살아나므로 함께 남긴다.
                "stop_updated_at": (self.stop_updated_at.isoformat()
                                    if self.stop_updated_at else None),
                # [424차] 섀도 계측도 함께 남긴다 — 장중 재기동 후 첫 봉에서
                # would_suppress 판정이 근거 없이 False가 되는 것을 막는다.
                "stop_shadow_tightened_at": (
                    self.stop_shadow_tightened_at.isoformat()
                    if self.stop_shadow_tightened_at else None),
                "stop_shadow_tighten_path": self.stop_shadow_tighten_path,
                "tp1_price":    self.tp1_price,
                "tp2_price":    self.tp2_price,
                "tp3_price":    self.tp3_price,
                "trailing_anchor_price": self.trailing_anchor_price,
                "initial_quantity": self.initial_quantity,
                "entry_quantity": self.entry_quantity,
                "partial_1_done": self.partial_1_done,
                "partial_2_done": self.partial_2_done,
                "partial_3_done": self.partial_3_done,
                "loss_tier1_price": self.loss_tier1_price,
                "loss_tier1_done": self.loss_tier1_done,
                "loss_tier1_qty1_shadow_logged": self.loss_tier1_qty1_shadow_logged,
                "entry_quantile_expected_pt": self.entry_quantile_expected_pt,
                "entry_quantile_uncertainty_pt": self.entry_quantile_uncertainty_pt,
                "synthetic_tp1_price": self.synthetic_tp1_price,
                "synthetic_tp1_pnl_pts": self.synthetic_tp1_pnl_pts,
                "synthetic_tp1_fraction": self.synthetic_tp1_fraction,
                "synthetic_tp1_ts": (
                    self.synthetic_tp1_ts.isoformat() if self.synthetic_tp1_ts else None
                ),
                # [459차 F1] 장중 재기동 시 기청산 레그 손익이 승패 판정에서
                # 빠지지 않도록 포지션 레그 누적기도 함께 남긴다.
                "pos_acc_pnl_pts": self._pos_acc_pnl_pts,
                "pos_acc_fwd_pnl_pts": self._pos_acc_fwd_pnl_pts,
                "last_update_reason": self.last_update_reason,
                "last_update_ts": (
                    self.last_update_ts.isoformat() if self.last_update_ts else None
                ),
                "futures_code": self._futures_code,
                "saved_at":     now_kst().isoformat(),
            }
            os.makedirs(os.path.dirname(_STATE_FILE), exist_ok=True)
            with open(_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"[Position] 상태 저장 실패: {e}")

    def load_state(self) -> bool:
        """저장된 포지션 상태 복원. 반환값: 복원 성공 여부."""
        if not os.path.exists(_STATE_FILE):
            return False
        try:
            with open(_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)

            # 당일 데이터만 복원 (날짜 다르면 무시)
            saved_at = datetime.datetime.fromisoformat(state.get("saved_at", ""))
            if saved_at.date() != datetime.date.today():
                logger.info("[Position] 저장 상태가 어제 데이터 — 무시")
                return False

            # FLAT이면 복원 불필요
            if state.get("status") == POSITION_FLAT:
                return False

            self._loaded_futures_code = str(state.get("futures_code") or "").strip()
            self.status      = state["status"]
            self.entry_price = float(state["entry_price"])
            self.quantity    = int(state["quantity"])
            self.entry_time  = (datetime.datetime.fromisoformat(state["entry_time"])
                                if state.get("entry_time") else None)
            self.grade        = state.get("grade", "")
            self.regime       = state.get("regime", "")
            self.signal_direction = state.get("signal_direction", self.status)
            self.reverse_entry_enabled = bool(state.get("reverse_entry_enabled", False))
            self.entry_horizon = state.get("entry_horizon")
            self.entry_hurst_bucket = state.get("entry_hurst_bucket")
            self.entry_extra_stop_mult = float(state.get("entry_extra_stop_mult", 1.0) or 1.0)
            self.stop_price   = float(state.get("stop_price", 0))
            # [423차] 구버전 상태파일에는 이 키가 없다 — None이면 가드가 비활성
            # 되어 종전과 동일하게 동작한다(하위호환, 재기동 1회 한정 노출).
            _sua_raw = state.get("stop_updated_at")
            try:
                self.stop_updated_at = (
                    datetime.datetime.fromisoformat(_sua_raw) if _sua_raw else None
                )
            except (TypeError, ValueError):
                self.stop_updated_at = None
            # [424차] 구버전 상태파일엔 없다 — None이면 would_suppress가 False로
            # 나오고, 그건 "억제 안 됨"이 아니라 "판정 근거 없음"이다. 섀도 판정
            # 전용이라 라이브 동작에는 영향이 없다(재기동 1회 한정 노출).
            _sst_raw = state.get("stop_shadow_tightened_at")
            try:
                self.stop_shadow_tightened_at = (
                    datetime.datetime.fromisoformat(_sst_raw) if _sst_raw else None
                )
            except (TypeError, ValueError):
                self.stop_shadow_tightened_at = None
            self.stop_shadow_tighten_path = state.get("stop_shadow_tighten_path")
            self.tp1_price    = float(state.get("tp1_price", 0))
            self.tp2_price    = float(state.get("tp2_price", 0))
            self.tp3_price    = float(state.get("tp3_price", 0))
            self.trailing_anchor_price = float(state.get("trailing_anchor_price", self.entry_price))
            self.initial_quantity = int(state.get("initial_quantity", self.quantity))
            # [421차] 구버전 상태파일에는 이 키가 없다 — 그때는 initial_quantity로
            # 폴백해 종전과 동일하게 동작한다(장중 재기동 호환). 단 그 포지션이
            # 이미 손절1차를 거쳤다면 폴백값은 축소된 값이므로, 복원 직후 청산되는
            # 레그의 entry_qty는 여전히 과소일 수 있다 — 재기동 1회 한정 잔여 오차.
            self.entry_quantity = int(
                state.get("entry_quantity", self.initial_quantity) or 0
            )
            self.partial_1_done = bool(state.get("partial_1_done", False))
            self.partial_2_done = bool(state.get("partial_2_done", False))
            self.partial_3_done = bool(state.get("partial_3_done", False))
            self.loss_tier1_price = float(state.get("loss_tier1_price", 0.0) or 0.0)
            self.loss_tier1_done = bool(state.get("loss_tier1_done", False))
            self.loss_tier1_qty1_shadow_logged = bool(state.get("loss_tier1_qty1_shadow_logged", False))
            self.entry_quantile_expected_pt = state.get("entry_quantile_expected_pt")
            self.entry_quantile_uncertainty_pt = state.get("entry_quantile_uncertainty_pt")
            self.synthetic_tp1_price = state.get("synthetic_tp1_price")
            self.synthetic_tp1_pnl_pts = state.get("synthetic_tp1_pnl_pts")
            self.synthetic_tp1_fraction = state.get("synthetic_tp1_fraction")
            self.synthetic_tp1_ts = (
                datetime.datetime.fromisoformat(state["synthetic_tp1_ts"])
                if state.get("synthetic_tp1_ts") else None
            )
            # [459차 F1] 구버전 상태파일에는 이 키가 없다 — 0.0 폴백이면 최종
            # 청산 판정이 종전(마지막 레그 이후 누적만)과 동일하게 동작한다
            # (재기동 1회 한정 잔여 오차, 하위호환).
            self._pos_acc_pnl_pts = float(state.get("pos_acc_pnl_pts", 0.0) or 0.0)
            self._pos_acc_fwd_pnl_pts = float(state.get("pos_acc_fwd_pnl_pts", 0.0) or 0.0)
            if self.tp3_price == 0.0 and self.stop_price and self.tp1_price and self.tp2_price:
                atr = abs(self.entry_price - self.stop_price) / ATR_STOP_MULT if ATR_STOP_MULT else 0.0
                mult = 1 if self.status == POSITION_LONG else -1
                self.tp3_price = self.entry_price + mult * max(atr, 0.0) * ATR_TP3_MULT
            self._sync_partial_progress()
            self.last_update_reason = state.get("last_update_reason", "unknown")
            self.last_update_ts = (
                datetime.datetime.fromisoformat(state["last_update_ts"])
                if state.get("last_update_ts") else None
            )

            logger.warning(
                f"[Position] 이전 포지션 복원: {self.status} {self.quantity}계약 "
                f"@ {self.entry_price} (손절={self.stop_price:.2f})"
            )
            logger.warning(
                "[PositionDiag] restore source=%s saved_at=%s last_update_ts=%s",
                self.last_update_reason,
                state.get("saved_at", ""),
                state.get("last_update_ts", ""),
            )
            return True
        except Exception as e:
            logger.warning(f"[Position] 상태 복원 실패: {e}")
            return False

    def peek_saved_entry_time(self, direction: str = "") -> Optional[datetime.datetime]:
        """같은 날 저장된 상태 파일에서 진입시각 힌트를 읽는다."""
        if not os.path.exists(_STATE_FILE):
            return None
        try:
            with open(_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            saved_at = datetime.datetime.fromisoformat(state.get("saved_at", ""))
            if saved_at.date() != datetime.date.today():
                return None
            status = str(state.get("status") or "").strip().upper()
            if status == POSITION_FLAT:
                return None
            if direction and status != str(direction).strip().upper():
                return None
            entry_time_raw = state.get("entry_time")
            if not entry_time_raw:
                return None
            return datetime.datetime.fromisoformat(str(entry_time_raw))
        except Exception:
            return None

    def _calc_directional_pnl_pts(self, direction: str, exit_price: float) -> float:
        mult = 1 if direction == POSITION_LONG else -1
        return (exit_price - self.entry_price) * mult
