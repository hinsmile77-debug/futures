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

import numpy as np

from challenger.challenger_db import ChallengerDB
from challenger.challenger_registry import ChallengerRegistry, CHAMPION_BASELINE_ID

logger = logging.getLogger("CHALLENGER")

# ── 전역 승격 기준 (기존) ─────────────────────────────────────
# [260704 감사 P2] min_trades 30→100: "승률 55% 전략의 30거래 표본오차는 ±18%p —
# 승률 델타 +2%p 기준은 이 노이즈 안에서 동전 던지기"(감사 §4-2 ①). 100건이면
# 표본오차가 대략 ±10%p 이내로 줄어든다.
PROMOTION_CRITERIA = {
    "min_obs_days":    20,
    "min_trades":      100,
    "win_rate_delta": +2.0,
    "mdd_ratio":       0.90,
    "sharpe_min":      1.50,
    "return_delta":   +0.00,
}

# ── 레짐 전문가 승격 기준 (레짐 내 거래 수 기반) ────────────────
# [260704 감사 P2] min_regime_trades 20→50 — 레짐 트랙은 표본이 원래 희소하므로
# 전역(100)보다는 완화하되 기존 20보다는 상향(감사 §4-3 권고).
REGIME_SPECIALIST_CRITERIA = {
    "min_regime_trades":      50,    # 해당 레짐에서의 거래 수 (달력 무관)
    "win_rate_vs_baseline":  +2.0,   # CHAMPION_BASELINE 동일 레짐 승률 대비 +2%
    "sharpe_min":             1.30,  # 레짐 희소성 고려해 1.30으로 완화
    "pnl_positive":           True,  # 레짐 내 누적 손익 양수
}

# ── [260704 감사 P2] 부트스트랩 승격 판정 기준 ──────────────────
# 감사 §4-2 ①②: 승률/샤프 점추정 대신 거래별 PnL을 리샘플해 "챌린저가 챔피언보다
# 우위일 확률"을 직접 추정한다 — 이 확률이 승격 조건.
BOOTSTRAP_CRITERIA = {
    "min_trades":        100,     # 전역 기준과 동일 표본 하한
    "n_resamples":        5000,
    "prob_superior_min":  0.95,   # "챌린저 우위 확률 ≥ 95%" (다중비교 보정 전 기준값)
}

# [260704 감사 P3] 다중 비교 보정 (Bonferroni) — 감사 §4-2 ④·4-3:
# "챌린저를 5종+ 동시 운용하면 그중 하나는 우연히 기준을 통과한다. 보정 없는 다중
# 후보 비교는 과적합 선택 장치다." 동시 활성 챌린저 수 n에 대해 유의수준 α를 α/n으로
# 나눠 요구 우위확률을 상향한다(예: α=0.05, n=5 → α/n=0.01 → 요구확률 0.95→0.99).
BONFERRONI_CORRECTION_ENABLED = True


def _bonferroni_prob_min(base_prob_min: float, n_concurrent: int) -> float:
    """다중비교 보정된 요구 우위확률. n_concurrent<=1이면 보정 없음(base 그대로)."""
    if n_concurrent <= 1:
        return base_prob_min
    alpha = 1.0 - base_prob_min
    return 1.0 - (alpha / n_concurrent)

# ── [260704 감사 P2] 챔피언 heartbeat 기준 ──────────────────────
# 감사 §4-2 ③: "챔피언 강등 기준 부재 — 승격 심사만 있고, 현 챔피언의 성능 붕괴를
# 감지해 사이즈를 줄이는 체계적 경로가 없다." 롤링 60거래 승률의 Wilson CI 하한이
# 기준선(CHAMPION_BASELINE 전체기간 승률) 밑으로 떨어지면 사이즈만 축소 — 강등은 수동.
HEARTBEAT_CRITERIA = {
    "window_trades":  60,
    "ci_confidence":  0.95,
    "degraded_size_mult": 0.5,
}


def _wilson_lower_bound(wins: int, n: int, confidence: float = 0.95) -> float:
    """Wilson score interval 하한 (표본 비율의 신뢰구간, 소표본에서 정규근사보다 안정적)."""
    if n <= 0:
        return 0.0
    from scipy.stats import norm
    z = float(norm.ppf(1.0 - (1.0 - confidence) / 2.0))
    p_hat = wins / n
    denom = 1.0 + z * z / n
    center = p_hat + z * z / (2 * n)
    margin = z * ((p_hat * (1 - p_hat) / n + z * z / (4 * n * n)) ** 0.5)
    return max(0.0, (center - margin) / denom)


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

    def evaluate_for_promotion_bootstrap(self, challenger_id, seed=None):
        # type: (str, Optional[int]) -> PromotionResult
        """
        [260704 감사 P2] 부트스트랩 기반 승격 판정.

        감사 근거: §4-2 ①② — "min_trades=30으로 승률 +2%p 판정은 수학적으로 불가능.
        승률 55% 전략의 30거래 표본오차는 ±18%p." 점추정(evaluate_for_promotion) 대신
        챌린저/챔피언 각각의 거래별 PnL을 독립적으로 5,000회 리샘플(복원추출)해,
        "리샘플된 챌린저 평균이 리샘플된 챔피언 평균보다 큰 비율"을 우위 확률로 추정한다.

        이 메서드는 evaluate_for_promotion()을 대체하지 않는다 — 두 판정 방식을
        병행 비교하다가(감사 문서 자체가 권고) 신뢰할 만하면 이쪽으로 전환할 것.
        """
        cr = BOOTSTRAP_CRITERIA
        champ_id = self.registry.get_champion_id()
        challenger_pnls = self.db.get_closed_trade_pnls(challenger_id)
        champion_pnls = self.db.get_closed_trade_pnls(champ_id)

        n_c = len(challenger_pnls)
        n_h = len(champion_pnls)

        checks = {
            "챌린저 거래 수 (%d/%d건)" % (n_c, cr["min_trades"]): n_c >= cr["min_trades"],
            "챔피언 거래 수 (%d/%d건)" % (n_h, cr["min_trades"]): n_h >= cr["min_trades"],
        }

        if n_c < cr["min_trades"] or n_h < cr["min_trades"]:
            failed = [desc for desc, ok in checks.items() if not ok]
            return PromotionResult(
                challenger_id=challenger_id, status="NOT_READY",
                checks=checks, failed=failed, obs_days=0,
                win_rate_delta=0.0, mdd_delta=0.0,
            )

        rng = np.random.default_rng(seed)
        arr_c = np.asarray(challenger_pnls, dtype=float)
        arr_h = np.asarray(champion_pnls, dtype=float)
        n_resamples = int(cr["n_resamples"])

        # 각각 독립적으로 복원추출 리샘플 n_resamples회 → 리샘플 평균 분포 생성
        resampled_c_means = rng.choice(arr_c, size=(n_resamples, n_c), replace=True).mean(axis=1)
        resampled_h_means = rng.choice(arr_h, size=(n_resamples, n_h), replace=True).mean(axis=1)
        prob_superior = float(np.mean(resampled_c_means > resampled_h_means))

        n_concurrent = len(self.registry.active_challengers())
        prob_min = (
            _bonferroni_prob_min(cr["prob_superior_min"], n_concurrent)
            if BONFERRONI_CORRECTION_ENABLED else cr["prob_superior_min"]
        )
        checks["챌린저 우위 확률 (%.1f%%≥%.1f%%, 동시챌린저=%d)" % (
            prob_superior * 100, prob_min * 100, n_concurrent
        )] = prob_superior >= prob_min

        failed = [desc for desc, ok in checks.items() if not ok]
        wr_c = sum(1 for p in challenger_pnls if p > 0) / n_c * 100
        wr_h = sum(1 for p in champion_pnls if p > 0) / n_h * 100

        logger.info(
            "[BootstrapPromotion] %s vs %s: n_c=%d n_h=%d prob_superior=%.3f "
            "prob_min=%.3f(n_concurrent=%d) status=%s",
            challenger_id, champ_id, n_c, n_h, prob_superior,
            prob_min, n_concurrent, "READY" if not failed else "NOT_READY",
        )
        return PromotionResult(
            challenger_id=challenger_id,
            status="READY" if not failed else "NOT_READY",
            checks=checks, failed=failed, obs_days=0,
            win_rate_delta=round(wr_c - wr_h, 2), mdd_delta=0.0,
        )

    def check_champion_heartbeat(self):
        # type: () -> Dict[str, Any]
        """
        [260704 감사 P2] 챔피언 heartbeat — 성능 붕괴 자동 감지(강등은 여전히 수동).

        감사 근거: §4-2 ③ — "챔피언 강등 기준 부재... 현 챔피언의 성능 붕괴를 감지해
        사이즈를 줄이는 체계적 경로가 없다." 챔피언의 최근 60거래 롤링 승률에 대한
        Wilson score 신뢰구간 하한이 CHAMPION_BASELINE(기준선) 전체기간 승률보다
        낮아지면 "degraded"로 판정 — 사이즈 축소(0.5배) + Slack 알림만 수행하고,
        실제 챔피언 교체(강등)는 여전히 사용자 수동 조작(rollback())으로 남긴다.

        Returns:
            {"degraded": bool, "size_mult": float, "reason": str,
             "champion_id": str, "window_trades": int, "ci_lower": float,
             "baseline_win_rate": float}
        """
        cr = HEARTBEAT_CRITERIA
        champ_id = self.registry.get_champion_id()
        recent = self.db.get_recent_closed_trades(champ_id, limit=cr["window_trades"])
        n = len(recent)

        if n < cr["window_trades"]:
            return {
                "degraded": False,
                "size_mult": 1.0,
                "reason": "표본 부족 (%d/%d건) — heartbeat 판정 보류" % (n, cr["window_trades"]),
                "champion_id": champ_id,
                "window_trades": n,
                "ci_lower": 0.0,
                "baseline_win_rate": 0.0,
            }

        wins = sum(1 for r in recent if (r["pnl_pt"] or 0.0) > 0)
        ci_lower = _wilson_lower_bound(wins, n, confidence=cr["ci_confidence"])

        baseline_m = self.db.get_metrics_summary(CHAMPION_BASELINE_ID)
        baseline_wr = float(baseline_m.get("win_rate", 0.0)) / 100.0  # %  → 비율

        degraded = ci_lower < baseline_wr
        result = {
            "degraded": degraded,
            "size_mult": cr["degraded_size_mult"] if degraded else 1.0,
            "reason": (
                "롤링 %d거래 승률 CI하한(%.1f%%) < 기준선(%.1f%%) — 사이즈 %.0f%%로 축소"
                % (n, ci_lower * 100, baseline_wr * 100, cr["degraded_size_mult"] * 100)
                if degraded else
                "정상 — 롤링 %d거래 승률 CI하한(%.1f%%) ≥ 기준선(%.1f%%)"
                % (n, ci_lower * 100, baseline_wr * 100)
            ),
            "champion_id": champ_id,
            "window_trades": n,
            "ci_lower": round(ci_lower, 4),
            "baseline_win_rate": round(baseline_wr, 4),
        }

        if degraded:
            logger.warning("[ChampionHeartbeat] %s", result["reason"])
            try:
                from utils.notify import notify
                notify(
                    "[챔피언 heartbeat] %s 성능 저하 감지 — %s (강등은 수동 확인 필요)"
                    % (champ_id, result["reason"]),
                    level="WARNING",
                )
            except Exception as exc:
                logger.debug("[ChampionHeartbeat] Slack 알림 실패(무해): %s", exc)
        else:
            logger.debug("[ChampionHeartbeat] %s", result["reason"])

        return result

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
