# strategy/shadow_evaluator.py — 섀도우 전략 평가기 (Shadow Strategy Evaluator)
"""
파라미터 교체 후보를 WFA → 시뮬 → Live 파이프라인의 "2주 shadow 모니터링" 구간에서
실전 체결 없이 가상으로 구동하여 실제 Live 전략과 성과를 비교한다.

Hot-Swap 승인 조건 (§20):
  ① Shadow 2주 누적 PnL > Live 2주 누적 PnL × 1.10
  ② sync_score(live_daily_pnls) ≥ 0.70
  ③ Shadow WFA Sharpe ≥ 현재 운용 버전 WFA Sharpe

사용 예:
  evaluator = ShadowEvaluator("v1.4-candidate", candidate_params, wfa_sharpe=1.72)
  evaluator.process_tick(bar, features)          # 매분 파이프라인 호출
  score  = evaluator.sync_score(live_daily_pnls)
  ready, reason = evaluator.is_hotswap_ready(live_daily_pnls, live_wfa_sharpe=1.63)
"""
from __future__ import annotations

import logging
import math
from collections import defaultdict
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("ShadowEvaluator")

# KOSPI200 선물 계약 승수 (2017년 이후)
_FUTURES_MULTIPLIER = 250_000


# ─────────────────────────────────────────────────────────────────────────────
class _VirtualPosition:
    """섀도우 전략의 가상 포지션 상태."""

    def __init__(self) -> None:
        self.direction: str = "FLAT"   # "LONG" | "SHORT" | "FLAT"
        self.entry_price: float = 0.0
        self.entry_time: Optional[datetime] = None
        self.qty: int = 0
        self.stop_price: float = 0.0
        self.tp1_price: float = 0.0
        self.tp2_price: float = 0.0
        self.partial1_done: bool = False
        self.partial2_done: bool = False

    @property
    def is_flat(self) -> bool:
        return self.direction == "FLAT"

    def open(
        self,
        direction: str,
        price: float,
        qty: int,
        atr: float,
        stop_mult: float,
        tp1_mult: float,
        tp2_mult: float,
        ts: datetime,
    ) -> None:
        self.direction   = direction
        self.entry_price = price
        self.entry_time  = ts
        self.qty         = qty
        self.partial1_done = False
        self.partial2_done = False

        stop_dist = atr * stop_mult
        tp1_dist  = atr * tp1_mult
        tp2_dist  = atr * tp2_mult

        if direction == "LONG":
            self.stop_price = price - stop_dist
            self.tp1_price  = price + tp1_dist
            self.tp2_price  = price + tp2_dist
        else:
            self.stop_price = price + stop_dist
            self.tp1_price  = price - tp1_dist
            self.tp2_price  = price - tp2_dist

    def reset(self) -> None:
        self.__init__()


# ─────────────────────────────────────────────────────────────────────────────
class ShadowEvaluator:
    """
    섀도우 전략 평가기.

    process_tick()을 매분 파이프라인 호출로 연결하면
    진입/청산 가상 신호를 자동 계산·기록한다.
    실제 체결은 일어나지 않으며, 슬리피지는 assumed_slippage_pt만큼 보수적으로 차감한다.

    Attributes:
        version:           후보 전략 버전 문자열
        params:            후보 파라미터 딕셔너리
        wfa_sharpe:        후보 WFA Sharpe (Hot-Swap 비교용)
        assumed_slippage:  가정 슬리피지 (pt 단위, 기본 0.02pt)
    """

    FORCE_CLOSE_HOUR   = 15
    FORCE_CLOSE_MINUTE = 10

    def __init__(
        self,
        candidate_version: str,
        candidate_params:  Dict,
        wfa_sharpe:        float = 0.0,
        assumed_slippage:  float = 0.02,
    ) -> None:
        self.version          = candidate_version
        self.params           = dict(candidate_params)
        self.wfa_sharpe       = wfa_sharpe
        self.assumed_slippage = assumed_slippage

        self._pos: _VirtualPosition = _VirtualPosition()
        self._virtual_trades: List[Dict] = []
        self._daily_pnl: Dict[str, float] = defaultdict(float)  # "YYYY-MM-DD" → PnL
        self._activation_time = datetime.now()

        # 파라미터 편의 참조
        self._conf_threshold = self.params.get("entry_conf_neutral", 0.58)
        self._stop_mult      = self.params.get("atr_stop_mult",      1.5)
        self._tp1_mult       = self.params.get("atr_tp1_mult",       1.0)
        self._tp2_mult       = self.params.get("atr_tp2_mult",       1.5)
        self._ratio1         = self.params.get("partial_exit_ratio_1", 0.33)
        self._ratio2         = self.params.get("partial_exit_ratio_2", 0.33)

    # ─── 매분 호출 ──────────────────────────────────────────────────────────
    def process_tick(
        self,
        bar:      Dict,
        features: Dict,
    ) -> None:
        """
        매분 분봉 확정 시 호출.  entry_manager 로직 미러링.

        Args:
            bar:      {"close": float, "high": float, "low": float,
                       "ts": datetime, "atr": float}
            features: {"confidence": float, "direction": "LONG"|"SHORT"|"FLAT",
                       "ensemble_conf": float, "grade": "A"|"B"|"C"|"X",
                       "regime": str, "hurst": float}
        """
        ts    = bar.get("ts", datetime.now())
        close = float(bar.get("close", 0.0))
        high  = float(bar.get("high", close))
        low   = float(bar.get("low",  close))
        atr   = max(float(bar.get("atr", 1.0)), 0.5)

        if close <= 0:
            return

        # 15:10 강제 청산
        if (isinstance(ts, datetime)
                and ts.hour == self.FORCE_CLOSE_HOUR
                and ts.minute >= self.FORCE_CLOSE_MINUTE
                and not self._pos.is_flat):
            self._virtual_close(close, ts, "15:10 강제청산")
            return

        # 포지션 보유 중 → 청산 체크 먼저
        if not self._pos.is_flat:
            self._check_virtual_exit(close, high, low, ts)

        # FLAT 상태 → 진입 체크
        if self._pos.is_flat:
            self._check_virtual_entry(close, atr, ts, features)

    # ─── 진입 체크 ──────────────────────────────────────────────────────────
    def _check_virtual_entry(
        self,
        price:    float,
        atr:      float,
        ts:       datetime,
        features: Dict,
    ) -> None:
        conf      = float(features.get("confidence", 0.0))
        direction = features.get("direction", "FLAT")
        grade     = features.get("grade", "X")
        hurst     = float(features.get("hurst", 0.5))

        # 진입 불가 조건
        if direction not in ("LONG", "SHORT"):
            return
        if conf < self._conf_threshold:
            return
        if grade == "X":
            return
        # Hurst 횡보장 필터 (hurst_range_threshold 이하이면 차단)
        hurst_range = self.params.get("hurst_range_threshold", 0.45)
        if hurst <= hurst_range:
            return

        # 사이즈: 간단하게 1계약 (shadow는 성과 비교용이므로 고정)
        qty = 1
        slippage_price = price + self.assumed_slippage if direction == "LONG" else price - self.assumed_slippage

        self._pos.open(
            direction  = direction,
            price      = slippage_price,
            qty        = qty,
            atr        = atr,
            stop_mult  = self._stop_mult,
            tp1_mult   = self._tp1_mult,
            tp2_mult   = self._tp2_mult,
            ts         = ts,
        )
        logger.debug(
            "[Shadow] 가상 진입 %s @ %.2f | conf=%.3f grade=%s",
            direction, slippage_price, conf, grade,
        )

    # ─── 청산 체크 ──────────────────────────────────────────────────────────
    def _check_virtual_exit(
        self,
        close: float,
        high:  float,
        low:   float,
        ts:    datetime,
    ) -> None:
        pos = self._pos
        if pos.direction == "LONG":
            # 손절
            if low <= pos.stop_price:
                self._virtual_close(pos.stop_price, ts, "STOP")
                return
            # TP1 부분청산
            if not pos.partial1_done and high >= pos.tp1_price:
                self._virtual_partial(pos.tp1_price, ts, "TP1", self._ratio1)
                pos.partial1_done = True
            # TP2 부분청산
            if not pos.partial2_done and high >= pos.tp2_price:
                self._virtual_partial(pos.tp2_price, ts, "TP2", self._ratio2)
                pos.partial2_done = True
                # TP2 이후 나머지 전량 청산
                remain_ratio = 1.0 - self._ratio1 - self._ratio2
                if remain_ratio > 0:
                    self._virtual_partial(close, ts, "TP2_TRAIL", remain_ratio)
                self._pos.reset()
        elif pos.direction == "SHORT":
            # 손절
            if high >= pos.stop_price:
                self._virtual_close(pos.stop_price, ts, "STOP")
                return
            # TP1 부분청산
            if not pos.partial1_done and low <= pos.tp1_price:
                self._virtual_partial(pos.tp1_price, ts, "TP1", self._ratio1)
                pos.partial1_done = True
            # TP2 부분청산
            if not pos.partial2_done and low <= pos.tp2_price:
                self._virtual_partial(pos.tp2_price, ts, "TP2", self._ratio2)
                pos.partial2_done = True
                remain_ratio = 1.0 - self._ratio1 - self._ratio2
                if remain_ratio > 0:
                    self._virtual_partial(close, ts, "TP2_TRAIL", remain_ratio)
                self._pos.reset()

    # ─── 가상 체결 기록 ──────────────────────────────────────────────────────
    def _virtual_close(self, exit_price: float, ts: datetime, reason: str) -> None:
        pos = self._pos
        if pos.is_flat:
            return

        exit_with_slip = (
            exit_price - self.assumed_slippage if pos.direction == "LONG"
            else exit_price + self.assumed_slippage
        )
        if pos.direction == "LONG":
            raw_pnl = (exit_with_slip - pos.entry_price) * _FUTURES_MULTIPLIER * pos.qty
        else:
            raw_pnl = (pos.entry_price - exit_with_slip) * _FUTURES_MULTIPLIER * pos.qty

        self._record_trade(raw_pnl, ts, reason, pos.qty)
        self._pos.reset()

    def _virtual_partial(
        self,
        exit_price: float,
        ts:         datetime,
        reason:     str,
        ratio:      float,
    ) -> None:
        pos = self._pos
        qty = max(1, int(pos.qty * ratio))
        exit_with_slip = (
            exit_price - self.assumed_slippage if pos.direction == "LONG"
            else exit_price + self.assumed_slippage
        )
        if pos.direction == "LONG":
            raw_pnl = (exit_with_slip - pos.entry_price) * _FUTURES_MULTIPLIER * qty
        else:
            raw_pnl = (pos.entry_price - exit_with_slip) * _FUTURES_MULTIPLIER * qty
        self._record_trade(raw_pnl, ts, reason, qty)

    def _record_trade(
        self,
        pnl: float,
        ts:  datetime,
        reason: str,
        qty: int,
    ) -> None:
        today_str = ts.strftime("%Y-%m-%d") if isinstance(ts, datetime) else str(date.today())
        self._daily_pnl[today_str] += pnl
        self._virtual_trades.append({
            "date":   today_str,
            "time":   ts.strftime("%H:%M") if isinstance(ts, datetime) else "",
            "pnl":    round(pnl),
            "reason": reason,
            "qty":    qty,
        })
        logger.debug(
            "[Shadow] 가상 청산 %s | PnL %+.0f원 | reason=%s",
            self.version, pnl, reason,
        )

    # ─── 성과 조회 ──────────────────────────────────────────────────────────
    def get_daily_pnls(self) -> List[float]:
        """날짜 순 일별 PnL 리스트 (원 단위)."""
        return [self._daily_pnl[d] for d in sorted(self._daily_pnl)]

    def get_total_pnl(self) -> float:
        """섀도우 전략 총 누적 PnL (원)."""
        return sum(self._daily_pnl.values())

    def get_win_rate(self) -> float:
        if not self._virtual_trades:
            return 0.0
        wins = sum(1 for t in self._virtual_trades if t["pnl"] > 0)
        return wins / len(self._virtual_trades)

    def get_summary(self) -> Dict:
        """성과 요약 딕셔너리."""
        pnls      = list(self._daily_pnl.values())
        total_pnl = sum(pnls)
        n_days    = len(pnls)
        sharpe    = 0.0
        if n_days >= 5:
            avg = total_pnl / n_days
            var = sum((p - avg) ** 2 for p in pnls) / max(n_days - 1, 1)
            std = math.sqrt(var)
            if std > 0:
                sharpe = round((avg / std) * math.sqrt(252), 3)
        return {
            "version":      self.version,
            "total_trades": len(self._virtual_trades),
            "win_rate":     round(self.get_win_rate(), 4),
            "total_pnl":    round(total_pnl),
            "sharpe":       sharpe,
            "uptime_days":  (datetime.now() - self._activation_time).days,
            "wfa_sharpe":   self.wfa_sharpe,
        }

    # ─── Hot-Swap 판단 ───────────────────────────────────────────────────────
    def sync_score(self, live_daily_pnls: List[float]) -> float:
        """
        Live 전략과 Shadow 전략의 일별 PnL 피어슨 상관계수 (Sync Score).

        Args:
            live_daily_pnls: Live 전략의 최근 N일 일별 PnL 리스트 (날짜 정렬)

        Returns:
            -1.0 ~ 1.0.  ≥ 0.70이면 Hot-Swap 승인 기준 충족.
        """
        shadow_pnls = self.get_daily_pnls()
        n = min(len(live_daily_pnls), len(shadow_pnls))
        if n < 5:
            return 0.0

        # 최근 n일 (최신 기준 정렬)
        x = live_daily_pnls[-n:]
        y = shadow_pnls[-n:]

        mean_x = sum(x) / n
        mean_y = sum(y) / n
        cov    = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / n
        std_x  = math.sqrt(sum((xi - mean_x) ** 2 for xi in x) / n) or 1.0
        std_y  = math.sqrt(sum((yi - mean_y) ** 2 for yi in y) / n) or 1.0

        return round(cov / (std_x * std_y), 4)

    def is_hotswap_ready(
        self,
        live_daily_pnls: List[float],
        live_wfa_sharpe: float = 0.0,
        pnl_advantage:   float = 1.10,   # Shadow가 Live 대비 최소 10% 우세
        sync_threshold:  float = 0.70,   # Sync Score 최소 기준
        live_avg_qty:    float = 1.0,    # 라이브 평균 계약수 (Shadow qty=1 정규화용)
    ) -> Tuple[bool, str]:
        """
        Hot-Swap 승인 여부 판정.

        Args:
            live_avg_qty: 라이브 전략의 평균 포지션 계약수.
                          Shadow는 항상 1계약이므로 Live PnL을 이 값으로 나눠
                          1계약 기준으로 정규화한 뒤 비교한다.
                          기본값 1.0 → 기존 동작 유지 (라이브도 1계약 운용 시).

        Returns:
            (승인_여부, 판정_이유_문자열)
        """
        live_total    = sum(live_daily_pnls) if live_daily_pnls else 0.0
        shadow_total  = self.get_total_pnl()
        score         = self.sync_score(live_daily_pnls)

        # qty 스케일 정규화: Live PnL을 1계약 기준으로 환산
        # Shadow는 항상 qty=1이므로 동일 기준에서 비교 가능해진다.
        norm_qty = max(live_avg_qty, 1.0)
        live_total_per_contract = live_total / norm_qty

        # ① 수익 우세 조건 (1계약 기준 비교)
        if live_total_per_contract > 0:
            cond1 = shadow_total >= live_total_per_contract * pnl_advantage
        else:
            cond1 = shadow_total > 0

        # ② Sync Score 조건
        cond2 = score >= sync_threshold

        # ③ WFA Sharpe 유지 조건
        cond3 = (self.wfa_sharpe == 0.0) or (self.wfa_sharpe >= live_wfa_sharpe)

        if cond1 and cond2 and cond3:
            reason = (
                "Hot-Swap 승인 | Shadow {0:+,.0f} > Live/계약 {1:+,.0f} × {2:.0f}%"
                " | Sync={3:.2f} | Sharpe {4:.2f}≥{5:.2f}"
            ).format(shadow_total, live_total_per_contract, pnl_advantage * 100,
                     score, self.wfa_sharpe, live_wfa_sharpe)
            return True, reason

        reasons = []
        if not cond1:
            reasons.append(
                "수익 우세 미달 (Shadow {0:+,.0f} / Live/계약 {1:+,.0f} × {2:.0f}%)".format(
                    shadow_total, live_total_per_contract, pnl_advantage * 100)
            )
        if not cond2:
            reasons.append("Sync Score %.2f < %.2f" % (score, sync_threshold))
        if not cond3:
            reasons.append(
                "WFA Sharpe %.2f < Live %.2f" % (self.wfa_sharpe, live_wfa_sharpe)
            )
        return False, " | ".join(reasons)

    def reset(self, new_version: str, new_params: Dict, new_wfa_sharpe: float = 0.0) -> None:
        """새 후보 버전으로 재초기화."""
        self.__init__(new_version, new_params, new_wfa_sharpe, self.assumed_slippage)
        logger.info("[Shadow] 리셋 → %s (WFA Sharpe=%.2f)", new_version, new_wfa_sharpe)


# ─────────────────────────────────────────────────────────────────────────────
# 전역 싱글턴
# ─────────────────────────────────────────────────────────────────────────────
_shadow_evaluator: Optional[ShadowEvaluator] = None


def get_shadow_evaluator(
    version: str = "vNext",
    params:  Optional[Dict] = None,
    wfa_sharpe: float = 0.0,
) -> ShadowEvaluator:
    """전역 ShadowEvaluator 싱글턴 반환 (없으면 생성)."""
    global _shadow_evaluator
    if _shadow_evaluator is None:
        _shadow_evaluator = ShadowEvaluator(version, params or {}, wfa_sharpe)
    return _shadow_evaluator
