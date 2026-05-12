# challenger/promotion_manager.py — 승격 판정 + 챔피언 교체
"""
PromotionManager: 전역 승격 + 레짐 전문가 승격 모두 지원.

레짐 전문가 승격 기준 (REGIME_SPECIALIST_CRITERIA):
  달력 기준이 아닌 해당 레짐 내 실제 거래 수로 판단.
  탈진처럼 희소한 레짐은 "20 거래일" 아닌 "20 레짐 거래"가 의미 있음.

자동 승격: 금지 (CLAUDE.md 절대 원칙)
사용자 수동 승인([▶ 수동 승격]) 필수.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List

from challenger.challenger_db import ChallengerDB
from challenger.challenger_registry import ChallengerRegistry, CHAMPION_BASELINE_ID

logger = logging.getLogger("CHALLENGER")

# ── 전역 승격 기준 (기존) ─────────────────────────────────────
PROMOTION_CRITERIA = {
    "min_obs_days":    20,
    "min_trades":      30,
    "win_rate_delta": +2.0,
    "mdd_ratio":       0.90,
    "sharpe_min":      1.50,
    "return_delta":   +0.00,
}

# ── 레짐 전문가 승격 기준 (레짐 내 거래 수 기반) ────────────────
REGIME_SPECIALIST_CRITERIA = {
    "min_regime_trades":      20,    # 해당 레짐에서의 거래 수 (달력 무관)
    "win_rate_vs_baseline":  +2.0,   # CHAMPION_BASELINE 동일 레짐 승률 대비 +2%
    "sharpe_min":             1.30,  # 레짐 희소성 고려해 1.30으로 완화
    "pnl_positive":           True,  # 레짐 내 누적 손익 양수
}


class PromotionResult(object):
    __slots__ = ("status", "checks", "failed", "challenger_id",
                 "regime", "obs_days", "win_rate_delta", "mdd_delta")

    def __init__(self, challenger_id, status, checks, failed,
                 regime="GLOBAL", obs_days=0, win_rate_delta=0.0, mdd_delta=0.0):
        self.challenger_id  = challenger_id
        self.status         = status
        self.checks         = checks
        self.failed         = failed
        self.regime         = regime
        self.obs_days       = obs_days
        self.win_rate_delta = win_rate_delta
        self.mdd_delta      = mdd_delta

    def to_dict(self):
        return {
            "status":         self.status,
            "checks":         self.checks,
            "failed":         self.failed,
            "challenger_id":  self.challenger_id,
            "regime":         self.regime,
            "obs_days":       self.obs_days,
            "win_rate_delta": self.win_rate_delta,
            "mdd_delta":      self.mdd_delta,
        }


class PromotionManager(object):
    """전역 승격 + 레짐 전문가 승격 관리."""

    def __init__(self, db=None, registry=None):
        self.db       = db       or ChallengerDB()
        self.registry = registry or ChallengerRegistry()

    # ── 전역 승격 (기존 API 유지) ─────────────────────────────────

    def evaluate_for_promotion(self, challenger_id):
        # type: (str) -> PromotionResult
        cr       = PROMOTION_CRITERIA
        champ_id = self.registry.get_champion_id()
        m        = self.db.get_metrics_summary(challenger_id)
        champ_m  = self.db.get_metrics_summary(champ_id)

        wr_delta  = m["win_rate"] - champ_m.get("win_rate", 0.0)
        mdd_ratio = (abs(m["cum_mdd_pt"]) / (abs(champ_m.get("cum_mdd_pt", 0.0)) + 1e-9)
                     if champ_m.get("cum_mdd_pt", 0.0) != 0.0 else 0.0)
        ret_delta = m["cum_pnl_pt"] - champ_m.get("cum_pnl_pt", 0.0)

        checks = {
            "관찰 기간 (%d/%d일)" % (m["obs_days"], cr["min_obs_days"]):
                m["obs_days"] >= cr["min_obs_days"],
            "거래 횟수 (%d/%d건)" % (m["trade_count"], cr["min_trades"]):
                m["trade_count"] >= cr["min_trades"],
            "승률 델타 (%+.1f%%)" % wr_delta:
                wr_delta >= cr["win_rate_delta"],
            "MDD 비율 (%.1f%%)" % (mdd_ratio * 100):
                mdd_ratio <= cr["mdd_ratio"],
            "Sharpe (%.2f≥%.2f)" % (m["sharpe"], cr["sharpe_min"]):
                m["sharpe"] >= cr["sharpe_min"],
            "수익 델타 (%+.1fpt)" % ret_delta:
                ret_delta >= cr["return_delta"],
        }
        failed = [desc for desc, ok in checks.items() if not ok]
        return PromotionResult(
            challenger_id  = challenger_id,
            status         = "READY" if not failed else "NOT_READY",
            checks         = checks,
            failed         = failed,
            obs_days       = m["obs_days"],
            win_rate_delta = round(wr_delta, 2),
            mdd_delta      = round(mdd_ratio - 1.0, 4),
        )

    def promote(self, challenger_id):
        # type: (str) -> None
        result = self.evaluate_for_promotion(challenger_id)
        if result.status != "READY":
            raise ValueError("승격 조건 미충족: %s" % result.failed)

        old_id   = self.registry.get_champion_id()
        old_m    = self.db.get_metrics_summary(old_id)
        new_m    = self.db.get_metrics_summary(challenger_id)
        ts_now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.db.insert_champion_history(
            promoted_ts    = ts_now,
            from_champion  = old_id,
            to_champion    = challenger_id,
            reason         = "manual_promotion",
            obs_days       = result.obs_days,
            win_rate_delta = round(new_m["win_rate"] - old_m.get("win_rate", 0.0), 2),
            mdd_delta      = round(abs(new_m["cum_mdd_pt"]) - abs(old_m.get("cum_mdd_pt", 0.0)), 2),
            regime         = "GLOBAL",
        )
        self.registry.set_champion(challenger_id)
        logger.info("[Promotion] 전역 챔피언 교체: %s → %s", old_id, challenger_id)

    def rollback(self):
        # type: () -> Tuple[bool, str]
        hist = self.db.get_last_champion_history(regime="GLOBAL")
        if hist is None:
            return False, "챔피언 교체 이력이 없습니다."
        prev_id = hist["from_champion"]
        curr_id = self.registry.get_champion_id()
        if prev_id == curr_id:
            return False, "이미 이전 챔피언 상태입니다."

        self.registry.set_champion(
            prev_id if self.registry.get(prev_id) is not None else CHAMPION_BASELINE_ID
        )
        self.db.insert_champion_history(
            promoted_ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            from_champion=curr_id, to_champion=prev_id,
            reason="rollback", obs_days=0,
            win_rate_delta=0.0, mdd_delta=0.0, regime="GLOBAL",
        )
        msg = "챔피언 롤백: %s → %s" % (curr_id, prev_id)
        logger.info("[Rollback] %s", msg)
        return True, msg

    # ── 레짐 전문가 승격 ─────────────────────────────────────────

    def evaluate_regime_specialist(self, challenger_id, regime):
        # type: (str, str) -> PromotionResult
        """
        레짐 내 거래 수 기반 전문가 승격 조건 평가.
        달력일이 아닌 '해당 레짐에서의 실제 거래 수'로 판단.
        """
        cr = REGIME_SPECIALIST_CRITERIA
        m  = self.db.get_regime_metrics(challenger_id, regime)

        # 기준선의 동일 레짐 성과 (비교 대상)
        baseline_m = self.db.get_regime_metrics(CHAMPION_BASELINE_ID, regime)
        baseline_wr = baseline_m.get("win_rate", 0.0) if baseline_m else 0.0

        wr_delta = m.get("win_rate", 0.0) - baseline_wr
        tc       = m.get("trade_count", 0)
        sharpe   = m.get("sharpe", 0.0)
        pnl      = m.get("total_pnl_pt", 0.0)

        checks = {
            "[%s] 레짐 거래 수 (%d/%d건)" % (regime, tc, cr["min_regime_trades"]):
                tc >= cr["min_regime_trades"],
            "승률 vs 기준선 (%+.1f%%)" % wr_delta:
                wr_delta >= cr["win_rate_vs_baseline"],
            "Sharpe (%.2f≥%.2f)" % (sharpe, cr["sharpe_min"]):
                sharpe >= cr["sharpe_min"],
            "레짐 내 누적 손익 (%+.2fpt)" % pnl:
                (not cr["pnl_positive"]) or pnl > 0,
        }
        failed = [desc for desc, ok in checks.items() if not ok]
        return PromotionResult(
            challenger_id  = challenger_id,
            status         = "READY" if not failed else "NOT_READY",
            checks         = checks,
            failed         = failed,
            regime         = regime,
            obs_days       = tc,           # 레짐 전문가는 obs_days 대신 레짐 거래 수
            win_rate_delta = round(wr_delta, 2),
        )

    def promote_regime_specialist(self, challenger_id, regime):
        # type: (str, str) -> None
        """
        레짐 전문가 승격 (수동 승인 후 호출).
        해당 레짐 슬롯의 챔피언만 교체.
        """
        result = self.evaluate_regime_specialist(challenger_id, regime)
        if result.status != "READY":
            raise ValueError("레짐 전문가 승격 조건 미충족: %s" % result.failed)

        old_id = self.registry.get_regime_champion(regime)
        ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.db.insert_champion_history(
            promoted_ts    = ts_now,
            from_champion  = old_id or "없음",
            to_champion    = challenger_id,
            reason         = "regime_specialist_promotion",
            obs_days       = result.obs_days,
            win_rate_delta = result.win_rate_delta,
            mdd_delta      = 0.0,
            regime         = regime,
        )
        self.registry.set_regime_champion(regime, challenger_id)
        logger.info("[Promotion] 레짐 전문가 승격 [%s]: %s → %s",
                    regime, old_id, challenger_id)

    def rollback_regime_specialist(self, regime):
        # type: (str) -> Tuple[bool, str]
        """레짐 전문가 롤백"""
        hist = self.db.get_last_champion_history(regime=regime)
        if hist is None:
            return False, "[%s] 레짐 교체 이력이 없습니다." % regime
        prev_id = hist["from_champion"]
        curr_id = self.registry.get_regime_champion(regime)
        if prev_id == curr_id:
            return False, "이미 이전 상태입니다."
        self.registry.set_regime_champion(regime, prev_id if prev_id != "없음" else None)
        msg = "[%s] 레짐 전문가 롤백: %s → %s" % (regime, curr_id, prev_id)
        logger.info("[Rollback] %s", msg)
        return True, msg

    def get_regime_ranking(self, regime):
        # type: (str) -> List[Dict[str, Any]]
        """레짐 전문가 풀 성과 순위 목록"""
        pool = self.registry.get_regime_pool(regime)
        return self.db.get_regime_ranking(regime, pool)
