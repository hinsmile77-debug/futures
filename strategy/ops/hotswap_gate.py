# strategy/ops/hotswap_gate.py — §20 Hot-Swap 승인 게이트
"""
Shadow 전략의 Hot-Swap 3-gate 조건을 검사하고,
통과 시 StrategyRegistry 등록 + DriftDetector 리셋 + Fingerprint 기준선 갱신을 수행한다.

3-gate 조건 (§20-2):
  ① Shadow 2주 누적 PnL > Live 2주 누적 PnL × 1.10  (10% 이상 우세)
  ② Sync Score ≥ 0.70  (같은 날 같이 이기고 짐)
  ③ Shadow WFA Sharpe ≥ 현재 버전 WFA Sharpe

전략 교체 게이트 전체 흐름 (§20-5):
  WFA 통과
    → Shadow 가동 (2주)
      → HotSwapGate.attempt()
        → 통과: registry.register_version() + drift_detector.reset_all() + fingerprint.reset()
        → 거부: 1주 추가 관찰 예약

사용:
  gate = HotSwapGate()
  ok, reason = gate.attempt(shadow_ev, live_daily_pnls, best_params, note="주간 최적화")
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class HotSwapGate:
    """
    Shadow 전략 → Live 전략 Hot-Swap 승인 게이트.

    Attributes:
        pnl_advantage  : Shadow 누적 PnL 우세 배율 (기본 1.10)
        sync_threshold : Sync Score 최소 기준 (기본 0.70)
    """

    def __init__(
        self,
        pnl_advantage:  float = 1.10,
        sync_threshold: float = 0.70,
    ):
        self.pnl_advantage  = pnl_advantage
        self.sync_threshold = sync_threshold
        self._last_attempt:  Optional[str]  = None
        self._last_result:   Optional[bool] = None
        self._last_reason:   str            = ""

    def attempt(
        self,
        shadow_ev:       object,           # ShadowEvaluator 인스턴스
        live_daily_pnls: List[float],      # 최근 N일 Live 일별 PnL
        best_params:     Dict,             # Shadow 전략 파라미터
        wfa_metrics:     Optional[Dict] = None,
        note:            str = "",
    ) -> Tuple[bool, str]:
        """
        Hot-Swap 3-gate 검사 후 통과 시 버전 등록까지 수행.

        Args:
            shadow_ev       : ShadowEvaluator 인스턴스
            live_daily_pnls : Live 전략 최근 일별 PnL 리스트
            best_params     : Shadow 전략이 사용할 파라미터
            wfa_metrics     : Shadow WFA 성과 dict (sharpe, mdd_pct, win_rate 등)
            note            : 버전 등록 메모

        Returns:
            (approved: bool, reason: str)
        """
        self._last_attempt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ── 1단계: ShadowEvaluator.is_hotswap_ready() 검사 ────────────────
        try:
            curr_wfa_sharpe = self._get_current_wfa_sharpe()
            ready, reason = shadow_ev.is_hotswap_ready(
                live_daily_pnls  = live_daily_pnls,
                live_wfa_sharpe  = curr_wfa_sharpe,
                pnl_advantage    = self.pnl_advantage,
                sync_threshold   = self.sync_threshold,
            )
        except Exception as e:
            reason = "ShadowEvaluator 검사 실패: %s" % e
            self._last_result = False
            self._last_reason = reason
            logger.warning("[HotSwapGate] %s", reason)
            return False, reason

        self._last_result = ready
        self._last_reason = reason

        if not ready:
            logger.info("[HotSwapGate] 보류 — %s", reason)
            try:
                from config.strategy_registry import get_registry as _gr
                _ver = getattr(shadow_ev, "version", None)
                _gr().log_event("HOTSWAP_DENIED", reason[:120], version=_ver)
            except Exception:
                pass
            return False, reason

        # ── 2단계: Hot-Swap 실행 ──────────────────────────────────────────
        try:
            self._execute_hotswap(shadow_ev, best_params, wfa_metrics or {}, note)
        except Exception as e:
            err = "Hot-Swap 실행 오류: %s" % e
            logger.error("[HotSwapGate] %s", err)
            return False, err

        logger.info("[HotSwapGate] Hot-Swap 승인 완료 — %s", reason)
        return True, reason

    def get_last_status(self) -> Dict:
        """마지막 검사 결과 요약."""
        return {
            "attempted_at": self._last_attempt,
            "approved":     self._last_result,
            "reason":       self._last_reason,
        }

    # ─── 내부 헬퍼 ──────────────────────────────────────────────────────────
    def _get_current_wfa_sharpe(self) -> float:
        """현재 운용 버전의 WFA Sharpe 반환."""
        try:
            from config.strategy_registry import get_registry
            info = get_registry().get_current_version()
            if info:
                stages = info.get("stages", {})
                wfa = stages.get("WFA", {})
                return float(wfa.get("sharpe", 0.0) or 0.0)
        except Exception:
            pass
        return 0.0

    def _execute_hotswap(
        self,
        shadow_ev:   object,
        best_params: Dict,
        wfa_metrics: Dict,
        note:        str,
    ) -> None:
        """Hot-Swap 승인 후 실행 시퀀스."""
        from config.strategy_params import PARAM_CURRENT, PARAM_HISTORY

        # 신규 버전명 생성
        last_ver = PARAM_HISTORY[-1]["version"] if PARAM_HISTORY else "v1.0"
        try:
            major, minor = last_ver.lstrip("v").split(".")
            new_version = "v%s.%d" % (major, int(minor) + 1)
        except ValueError:
            new_version = "v%s-swap" % datetime.now().strftime("%Y%m%d")

        # PARAM_CURRENT 업데이트
        changed: Dict = {}
        for k, new_v in best_params.items():
            old_v = PARAM_CURRENT.get(k)
            if old_v != new_v:
                PARAM_CURRENT[k] = new_v
                changed[k] = {"from": old_v, "to": new_v}

        # StrategyRegistry 등록
        try:
            from config.strategy_registry import get_registry
            get_registry().register_version(
                version        = new_version,
                changed_params = changed,
                wfa_metrics    = wfa_metrics,
                note           = note or "HotSwapGate 자동 승인",
            )
            logger.info("[HotSwapGate] StrategyRegistry 등록: %s", new_version)
        except Exception as e:
            logger.warning("[HotSwapGate] Registry 등록 실패: %s", e)

        # DriftDetector 리셋 (새 기준선 설정)
        try:
            from strategy.param_drift_detector import get_drift_detector
            pnl_mean = wfa_metrics.get("avg_daily_pnl", 0.0)
            pnl_std  = wfa_metrics.get("std_daily_pnl", 1.0)
            get_drift_detector().reset_all(pnl_ref=(pnl_mean, pnl_std))
            logger.info("[HotSwapGate] DriftDetector 리셋 완료")
        except Exception as e:
            logger.warning("[HotSwapGate] DriftDetector 리셋 실패: %s", e)

        # RegimeFingerprint 기준선 갱신
        try:
            from strategy.regime_fingerprint import get_fingerprint
            get_fingerprint().reset_to_live_baseline()
            logger.info("[HotSwapGate] RegimeFingerprint 기준선 갱신 완료")
        except Exception as e:
            logger.warning("[HotSwapGate] Fingerprint 리셋 실패: %s", e)

        # strategy_events 기록
        try:
            from config.strategy_registry import get_registry as _gr2
            _gr2().log_event(
                event_type = "HOTSWAP_APPROVED",
                message    = "Hot-Swap 완료 — %d개 파라미터 변경 | %s" % (len(changed), note or ""),
                version    = new_version,
            )
        except Exception as _ev_e:
            logger.warning("[HotSwapGate] log_event 실패: %s", _ev_e)

        # shadow_candidate.json 삭제 (다음 사이클 불필요 재로드 방지)
        try:
            import os as _os
            _sp = _os.path.normpath(_os.path.join(
                _os.path.dirname(__file__), "..", "..", "data", "shadow_candidate.json"
            ))
            if _os.path.exists(_sp):
                _os.remove(_sp)
                logger.info("[HotSwapGate] shadow_candidate.json 삭제")
        except Exception as _rm_e:
            logger.warning("[HotSwapGate] shadow_candidate.json 삭제 실패: %s", _rm_e)

        logger.info("[HotSwapGate] Hot-Swap 완료 → %s (%d개 파라미터 변경)", new_version, len(changed))


# ─── 전역 싱글턴 ─────────────────────────────────────────────────────────────
_gate: Optional[HotSwapGate] = None


def get_hotswap_gate() -> HotSwapGate:
    """전역 HotSwapGate 싱글턴 반환."""
    global _gate
    if _gate is None:
        _gate = HotSwapGate()
    return _gate
