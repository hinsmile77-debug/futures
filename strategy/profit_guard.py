# strategy/profit_guard.py — 당일 수익 보존 통합 가드
"""
4-Layer 수익 보존 시스템 (Profit Protection Guard)

Layer 1: DailyPnlTrailingGuard  — 피크 대비 하락률 감지 → 당일 거래 중단
Layer 2: ProfitTierGate         — 수익 구간별 최소 등급 상향
Layer 3: AfternoonRiskMode      — 오후 시간대 진입 횟수·RR 제한
Layer 4: ProfitProtectionCB     — 수익 상태에서 연속 손실 → 즉시 중단

설계 원칙:
  - 손실 중에는 보호 모드 발동 안 함 (회복 기회 보존)
  - 각 Layer는 독립적으로 동작, 어느 하나라도 BLOCK → 진입 차단
  - 파라미터는 ProfitGuardConfig로 런타임 변경 가능 (대시보드 연동)
"""
import datetime
import logging
from typing import Optional, List, Tuple

from utils.time_utils import now_kst

from logging_system.log_manager import log_manager

logger = logging.getLogger("TRADE")


# ── 파라미터 설정 오브젝트 ────────────────────────────────────────
class ProfitGuardConfig:
    """ProfitGuard 전체 파라미터 — 대시보드에서 실시간 변경 가능"""

    def __init__(self):
        # Layer 1: 피크 트레일링 가드
        self.trail_activation_krw: float = 2_000_000   # 200만원 이상 벌어야 발동
        self.trail_ratio: float           = 0.35        # 피크 대비 35% 하락 시 중단

        # Layer 2: 수익 구간별 등급 게이트
        # (누적수익 하한, 최소 size_mult, 최대계약수 — None=거래중단)
        self.profit_tiers: List[Tuple[float, Optional[float], Optional[int]]] = [
            (0,           0.6,  None),   # Tier 0: 정상 (C급 이상)
            (1_000_000,   1.0,  None),   # Tier 1: 100만+ → B급 이상
            (2_000_000,   1.2,  None),   # Tier 2: 200만+ → A급 이상
            (3_000_000,   1.5,  None),   # Tier 3: 300만+ → A+ 전용
            (4_000_000,   None, 0),      # Tier 4: 400만+ → 완전 중단
        ]

        # Layer 3: 오후 리스크 압축
        self.afternoon_enabled: bool      = True
        self.afternoon_cutoff_hour: int   = 13          # 13:00 이후
        self.afternoon_min_pnl_krw: float = 1_000_000  # 100만원 이상 수익일 때만 발동
        self.afternoon_max_trades: int    = 3           # 오후 최대 진입 횟수
        self.afternoon_min_rr: float      = 2.5         # 최소 보상:리스크 비율

        # Layer 4: 연속 손실 보존 CB
        self.profit_cb_enabled: bool      = True
        self.profit_cb_min_pnl_krw: float = 1_500_000  # 발동 최소 수익 150만원
        self.profit_cb_consec_loss: int   = 2           # 연속 손실 N회 → 중단

    def to_dict(self) -> dict:
        return {
            "trail_activation_krw": self.trail_activation_krw,
            "trail_ratio":          self.trail_ratio,
            "profit_tiers":         self.profit_tiers,
            "afternoon_enabled":    self.afternoon_enabled,
            "afternoon_cutoff_hour": self.afternoon_cutoff_hour,
            "afternoon_min_pnl_krw": self.afternoon_min_pnl_krw,
            "afternoon_max_trades": self.afternoon_max_trades,
            "afternoon_min_rr":     self.afternoon_min_rr,
            "profit_cb_enabled":    self.profit_cb_enabled,
            "profit_cb_min_pnl_krw": self.profit_cb_min_pnl_krw,
            "profit_cb_consec_loss": self.profit_cb_consec_loss,
        }


# ── Layer 1: 피크 트레일링 가드 ──────────────────────────────────
class _TrailingGuard:
    def __init__(self):
        self.peak_pnl: float   = 0.0
        self.is_halted: bool   = False
        self._halt_reason: str = ""

    def update(self, current_pnl: float, cfg: ProfitGuardConfig) -> bool:
        """True = 진입 차단. 매분 호출."""
        if self.is_halted:
            return True

        if current_pnl > self.peak_pnl:
            self.peak_pnl = current_pnl

        if self.peak_pnl >= cfg.trail_activation_krw:
            floor = self.peak_pnl * (1.0 - cfg.trail_ratio)
            if current_pnl < floor:
                self.is_halted = True
                self._halt_reason = (
                    f"피크 {self.peak_pnl:+,.0f}원 대비 "
                    f"{cfg.trail_ratio:.0%} 하락 "
                    f"(현재 {current_pnl:+,.0f}원 < 보호선 {floor:+,.0f}원)"
                )
                msg = f"[ProfitGuard-L1] 트레일링 발동 — {self._halt_reason}"
                logger.warning(msg)
                log_manager.system(msg, "WARNING")
                return True

        return False

    def trail_floor(self, cfg: ProfitGuardConfig) -> Optional[float]:
        if self.peak_pnl >= cfg.trail_activation_krw:
            return self.peak_pnl * (1.0 - cfg.trail_ratio)
        return None

    def reset(self):
        self.peak_pnl   = 0.0
        self.is_halted  = False
        self._halt_reason = ""


# ── Layer 2: 수익 구간별 등급 게이트 ────────────────────────────
class _TierGate:
    def __init__(self):
        # 거래중단 임계 도달 시 당일 영구 차단(latch)
        self._halted: bool = False
        self._halt_tier: int = 0
        self._halt_threshold: float = 0.0

    def check(
        self,
        current_pnl: float,
        size_mult: float,
        cfg: ProfitGuardConfig,
    ) -> Tuple[bool, int, str]:
        """
        Returns:
            (blocked, tier_index, reason)
        """
        if self._halted:
            return (
                True,
                self._halt_tier,
                f"Tier {self._halt_tier}: 중단 임계 {self._halt_threshold:,.0f}원 도달로 당일 영구 중단",
            )

        active_tier = 0
        min_mult = 0.6
        max_qty  = None
        stop_tier_hit: Optional[Tuple[int, float]] = None

        for i, (threshold, t_min_mult, t_max_qty) in enumerate(cfg.profit_tiers):
            if current_pnl >= threshold:
                active_tier = i
                min_mult    = t_min_mult
                max_qty     = t_max_qty
                if t_max_qty == 0 and stop_tier_hit is None:
                    stop_tier_hit = (i, float(threshold))

        if stop_tier_hit is not None:
            self._halted = True
            self._halt_tier, self._halt_threshold = stop_tier_hit
            return (
                True,
                self._halt_tier,
                f"Tier {self._halt_tier}: 중단 임계 {self._halt_threshold:,.0f}원 도달 → 당일 영구 중단",
            )

        if max_qty == 0:
            return True, active_tier, f"Tier {active_tier}: {current_pnl:+,.0f}원 → 거래 완전 중단"

        if min_mult is not None and size_mult < min_mult:
            return (
                True, active_tier,
                f"Tier {active_tier}: size_mult {size_mult:.1f} < 최소 {min_mult:.1f} 요구"
            )

        return False, active_tier, ""

    def get_tier(self, current_pnl: float, cfg: ProfitGuardConfig) -> int:
        tier = 0
        for i, (threshold, _, _) in enumerate(cfg.profit_tiers):
            if current_pnl >= threshold:
                tier = i
        return tier

    def get_min_mult(self, current_pnl: float, cfg: ProfitGuardConfig) -> Optional[float]:
        min_mult = 0.6
        for threshold, t_min_mult, t_max_qty in cfg.profit_tiers:
            if current_pnl >= threshold:
                min_mult = t_min_mult
        return min_mult

    def reset(self):
        self._halted = False
        self._halt_tier = 0
        self._halt_threshold = 0.0

    @property
    def halt_threshold(self) -> float:
        """거래중단 임계값 (0 = 미활성)"""
        return self._halt_threshold

    @property
    def halt_tier(self) -> int:
        """거래중단 티어 인덱스"""
        return self._halt_tier


# ── Layer 3: 오후 리스크 압축 ────────────────────────────────────
class _AfternoonMode:
    def __init__(self):
        self._afternoon_count: int = 0

    def can_enter(
        self,
        now: datetime.datetime,
        current_pnl: float,
        size_mult: float,
        cfg: ProfitGuardConfig,
    ) -> Tuple[bool, str]:
        """True = 진입 허용."""
        if not cfg.afternoon_enabled:
            return True, ""
        if now.hour < cfg.afternoon_cutoff_hour:
            return True, ""
        if current_pnl < cfg.afternoon_min_pnl_krw:
            return True, ""

        if self._afternoon_count >= cfg.afternoon_max_trades:
            return (
                False,
                f"오후 진입 횟수 소진 ({self._afternoon_count}/{cfg.afternoon_max_trades}회)"
            )

        # size_mult를 RR 프록시로 사용 (1.5=A급≈높은RR)
        if size_mult < cfg.afternoon_min_rr / 2.0:
            return (
                False,
                f"오후 신호 품질 미달 (mult {size_mult:.1f} < 기준 {cfg.afternoon_min_rr/2:.1f})"
            )

        return True, ""

    def on_entry(self, now: datetime.datetime, cfg: ProfitGuardConfig):
        if now.hour >= cfg.afternoon_cutoff_hour:
            self._afternoon_count += 1

    def reset(self):
        self._afternoon_count = 0

    @property
    def afternoon_count(self) -> int:
        return self._afternoon_count


# ── Layer 4: 수익 상태 연속 손실 CB ─────────────────────────────
class _ProfitCB:
    def __init__(self):
        self._consec_loss: int = 0
        self._halted: bool     = False

    def on_trade_close(self, pnl_krw: float, current_daily_pnl: float, cfg: ProfitGuardConfig):
        if not cfg.profit_cb_enabled:
            return
        if current_daily_pnl < cfg.profit_cb_min_pnl_krw:
            self._consec_loss = 0
            return
        if pnl_krw < 0:
            self._consec_loss += 1
            if self._consec_loss >= cfg.profit_cb_consec_loss:
                self._halted = True
                msg = (
                    f"[ProfitGuard-L4] 수익 보존 CB 발동 — "
                    f"당일 수익 {current_daily_pnl:+,.0f}원 상태에서 "
                    f"{self._consec_loss}연속 손실 → 당일 진입 중단"
                )
                logger.warning(msg)
                log_manager.system(msg, "WARNING")
        else:
            self._consec_loss = 0

    @property
    def is_halted(self) -> bool:
        return self._halted

    @property
    def consec_loss(self) -> int:
        return self._consec_loss

    def reset(self):
        self._consec_loss = 0
        self._halted      = False


# ── 통합 ProfitGuard ─────────────────────────────────────────────
class ProfitGuard:
    """
    당일 수익 보존 통합 관리자.

    매분 파이프라인 STEP 7 진입 직전에 호출:
        allowed, reason = profit_guard.is_entry_allowed(daily_pnl, size_mult, now)

    거래 체결 후:
        profit_guard.on_trade_close(pnl_krw, daily_pnl_after)

    진입 체결 후:
        profit_guard.on_entry(now)

    장 시작 시:
        profit_guard.reset_daily()
    """

    def __init__(self, config: Optional[ProfitGuardConfig] = None):
        self.cfg = config or ProfitGuardConfig()

        self._trail  = _TrailingGuard()
        self._tier   = _TierGate()
        self._arisk  = _AfternoonMode()
        self._pcb    = _ProfitCB()

        # 통계
        self._blocked_today: int   = 0
        self._block_log: list      = []   # [(시각, layer, reason)]

    # ── 진입 허용 여부 ─────────────────────────────────────────────
    def is_entry_allowed(
        self,
        daily_pnl_krw: float,
        size_mult: float,
        now: Optional[datetime.datetime] = None,
    ) -> Tuple[bool, str]:
        """
        Returns:
            (allowed: bool, reason: str)
        """
        if now is None:
            now = now_kst()

        # Layer 1
        if self._trail.update(daily_pnl_krw, self.cfg):
            return self._block("L1-Trail", self._trail._halt_reason)

        # Layer 2
        blocked, tier, reason = self._tier.check(daily_pnl_krw, size_mult, self.cfg)
        if blocked:
            return self._block(f"L2-Tier{tier}", reason)

        # Layer 3
        ok, reason = self._arisk.can_enter(now, daily_pnl_krw, size_mult, self.cfg)
        if not ok:
            return self._block("L3-Afternoon", reason)

        # Layer 4
        if self._pcb.is_halted:
            return self._block("L4-ProfitCB", f"수익 보존 CB 발동 ({self._pcb.consec_loss}연속 손실)")

        return True, ""

    def _block(self, layer: str, reason: str) -> Tuple[bool, str]:
        self._blocked_today += 1
        ts = now_kst().strftime("%H:%M")
        self._block_log.append((ts, layer, reason))
        if len(self._block_log) > 200:
            self._block_log = self._block_log[-200:]
        log_manager.signal(f"[ProfitGuard] 진입 차단 [{layer}] {reason}")
        return False, f"[{layer}] {reason}"

    # ── 이벤트 훅 ─────────────────────────────────────────────────
    def on_trade_close(self, pnl_krw: float, daily_pnl_krw: float):
        self._pcb.on_trade_close(pnl_krw, daily_pnl_krw, self.cfg)

    def on_entry(self, now: Optional[datetime.datetime] = None):
        if now is None:
            now = now_kst()
        self._arisk.on_entry(now, self.cfg)

    # ── 일일 리셋 ─────────────────────────────────────────────────
    def reset_daily(self):
        self._trail.reset()
        self._tier.reset()
        self._arisk.reset()
        self._pcb.reset()
        self._blocked_today = 0
        self._block_log.clear()
        logger.info("[ProfitGuard] 일간 리셋 완료")

    # ── 상태 조회 ─────────────────────────────────────────────────
    def status_dict(self, daily_pnl_krw: float = 0.0) -> dict:
        tier   = self._tier.get_tier(daily_pnl_krw, self.cfg)
        floor  = self._trail.trail_floor(self.cfg)
        return {
            "peak_pnl":       self._trail.peak_pnl,
            "trail_floor":    floor,
            "trail_halted":   self._trail.is_halted,
            "current_tier":   tier,
            "min_mult":       self._tier.get_min_mult(daily_pnl_krw, self.cfg),
            "afternoon_count": self._arisk.afternoon_count,
            "pcb_consec":     self._pcb.consec_loss,
            "pcb_halted":     self._pcb.is_halted,
            "tier_halted":    self._tier.is_halted,
            "tier_halt_threshold": self._tier.halt_threshold,
            "blocked_today":  self._blocked_today,
            "block_log":      list(self._block_log[-20:]),
        }

    def get_l2_halt_info(self, daily_pnl_krw: Optional[float] = None) -> dict:
        """L2 Tier Gate 영구중단 상태 반환
        Returns:
            {
                'is_halted': bool,
                'halt_threshold': float,
                'halt_tier': int
            }
        """
        if daily_pnl_krw is not None and not self._tier.is_halted:
            for i, (threshold, _, max_qty) in enumerate(self.cfg.profit_tiers):
                if max_qty == 0 and daily_pnl_krw >= threshold:
                    self._tier._halted = True
                    self._tier._halt_tier = i
                    self._tier._halt_threshold = float(threshold)
                    break

        return {
            'is_halted': self._tier.is_halted,
            'halt_threshold': self._tier.halt_threshold,
            'halt_tier': self._tier.halt_tier,
        }

    def update_config(self, new_cfg: ProfitGuardConfig):
        """대시보드에서 파라미터 변경 시 호출."""
        self.cfg = new_cfg
        logger.info("[ProfitGuard] 설정 업데이트 완료")

    # ── 시뮬레이션 (백테스트용) ───────────────────────────────────
    @staticmethod
    def simulate(trades: list, cfg: ProfitGuardConfig) -> dict:
        """
        거래 목록에 ProfitGuard를 소급 적용해 가상 성과를 계산한다.

        Args:
            trades: [{"exit_time": "HH:MM", "pnl_krw": int,
                       "size_mult": float, "hour": int}, ...]
            cfg: 적용할 ProfitGuardConfig

        Returns:
            {total_pnl, trade_count, wins, losses, peak_pnl,
             blocked_count, blocked_trades, surviving_trades}
        """
        trail  = _TrailingGuard()
        tier   = _TierGate()
        arisk  = _AfternoonMode()
        pcb    = _ProfitCB()

        cum_pnl     = 0.0
        peak_pnl    = 0.0
        wins        = 0
        losses      = 0
        blocked     = 0
        surviving   = []
        blocked_list = []

        for t in trades:
            pnl       = t.get("pnl_krw", 0)
            mult      = t.get("size_mult", 1.0)
            hour      = t.get("hour", 10)
            exit_time = t.get("exit_time", "10:00")
            now_dt    = now_kst().replace(
                hour=hour, minute=int(t.get("minute", 0))
            )

            # 진입 허용 체크
            l1 = trail.update(cum_pnl, cfg)
            l2_blocked, _, _ = tier.check(cum_pnl, mult, cfg)
            l3_ok, _ = arisk.can_enter(now_dt, cum_pnl, mult, cfg)
            l4 = pcb.is_halted

            if l1 or l2_blocked or not l3_ok or l4:
                blocked += 1
                blocked_list.append({**t, "cum_pnl_at_block": cum_pnl})
                continue

            # 거래 실행
            arisk.on_entry(now_dt, cfg)
            cum_pnl += pnl
            peak_pnl = max(peak_pnl, cum_pnl)
            pcb.on_trade_close(pnl, cum_pnl, cfg)

            if pnl >= 0:
                wins += 1
            else:
                losses += 1
            surviving.append({**t, "cum_pnl_after": cum_pnl})

        total_trades = wins + losses
        win_rate = wins / total_trades if total_trades > 0 else 0.0
        mdd = 0.0
        running_peak = 0.0
        for t in surviving:
            running_peak = max(running_peak, t["cum_pnl_after"])
            dd = running_peak - t["cum_pnl_after"]
            mdd = max(mdd, dd)

        return {
            "total_pnl":       cum_pnl,
            "trade_count":     total_trades,
            "wins":            wins,
            "losses":          losses,
            "win_rate":        win_rate,
            "peak_pnl":        peak_pnl,
            "mdd":             mdd,
            "blocked_count":   blocked,
            "blocked_trades":  blocked_list,
            "surviving_trades": surviving,
        }
