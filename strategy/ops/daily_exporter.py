# strategy/ops/daily_exporter.py — 일일/주간 전략 상태 요약 export
"""
매일 장 마감 후 전략 상태를 텍스트로 요약하여 파일에 저장한다.
Slack 메시지 포맷과 동일하게 출력 가능.

사용:
  exporter = DailyExporter()
  report = exporter.build_report()
  exporter.save(report)                 # data/daily_reports/ 에 저장
  print(exporter.slack_format(report))  # Slack 메시지용
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_REPORT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "daily_reports"
)


class DailyExporter:
    """일일 전략 상태 요약 생성·저장."""

    def __init__(self, report_dir: Optional[str] = None):
        self._dir = report_dir or _REPORT_DIR
        os.makedirs(self._dir, exist_ok=True)

    def build_report(self) -> str:
        """
        현재 전략 상태를 종합하여 리포트 문자열을 반환.
        실패해도 빈 문자열 대신 최소 골격 반환.
        """
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = ["=" * 56, "  미륵이 일일 전략 상태 리포트  %s" % today, "=" * 56]

        # ── 현재 버전 & 판정 ─────────────────────────────────────────────
        try:
            from config.strategy_registry import get_registry
            reg  = get_registry()
            curr = reg.get_current_version()
            if curr:
                ver     = curr.get("version", "—")
                verdict = curr.get("verdict", "—")
                days    = curr.get("live_days", 0)
                lines.append("  버전    : %s  (%d일차)" % (ver, days))
                lines.append("  판정    : %s" % verdict)
                live = curr.get("live_snapshot") or {}
                sh = live.get("sharpe")
                md = live.get("mdd_pct")
                wr = live.get("win_rate")
                pf = live.get("profit_factor")
                if sh is not None:
                    lines.append(
                        "  Live    : Sh=%.2f  MDD=%.1f%%  WR=%.1f%%  PF=%.2f" % (
                            sh, abs(md or 0) * 100, (wr or 0) * 100, pf or 0
                        )
                    )
                # 롤링 20일
                rolling = reg.get_rolling_metrics(ver)
                cum = rolling.get("cum_pnl", 0)
                lines.append(
                    "  롤링20일: 누적 %+.0f원  Sh=%.2f  MDD=%.1f%%" % (
                        cum,
                        rolling.get("sharpe", 0) or 0,
                        abs(rolling.get("mdd_pct", 0) or 0) * 100,
                    )
                )
            else:
                lines.append("  버전    : 데이터 없음")
        except Exception as e:
            lines.append("  [Registry 조회 실패: %s]" % e)

        lines.append("-" * 56)

        # ── CUSUM 드리프트 ───────────────────────────────────────────────
        try:
            from strategy.param_drift_detector import get_drift_detector, DriftLevel
            det   = get_drift_detector()
            lv    = max(det.get_levels().values()) if hasattr(det, "get_levels") else 0
            lname = DriftLevel.name(lv)
            cusum = det.detectors["pnl"].get_cusum() if hasattr(det, "detectors") else 0.0
            lines.append("  CUSUM   : %s (%.2f)" % (lname, cusum))
        except Exception as e:
            lines.append("  CUSUM   : [조회 실패: %s]" % e)

        # ── RegimeFingerprint PSI ────────────────────────────────────────
        try:
            from strategy.regime_fingerprint import get_fingerprint, DriftLevel as _DL
            fp  = get_fingerprint()
            psi = fp.get_psi()
            pli = fp.get_level()
            lines.append(
                "  PSI     : %.3f (%s)" % (psi, {0:"CLEAR",1:"WATCHLIST",2:"ALARM",3:"CRITICAL"}.get(pli,"?"))
            )
            feat_psi = fp.get_per_feature_psi()
            if feat_psi:
                lines.append(
                    "  PSI/feat: " + "  ".join(
                        "%s=%.3f" % (k.replace("_divergence","").replace("_norm",""), v)
                        for k, v in feat_psi.items()
                    )
                )
        except Exception as e:
            lines.append("  PSI     : [조회 실패: %s]" % e)

        lines.append("-" * 56)

        # ── 액션 권고 ────────────────────────────────────────────────────
        try:
            from strategy.ops.verdict_engine import compute_action, ACTION_KOR
            from config.strategy_registry import get_registry as _gr
            from strategy.param_drift_detector import get_drift_detector as _gd
            from strategy.regime_fingerprint import get_fingerprint as _gf
            _curr = _gr().get_current_version()
            _verd = _curr.get("verdict", "INSUFFICIENT") if _curr else "INSUFFICIENT"
            _days = _curr.get("live_days", 0) if _curr else 0
            _dd   = _gd()
            _dd_lvs = _dd.get_levels() if hasattr(_dd, "get_levels") else {}
            _dlv  = max(_dd_lvs.values()) if _dd_lvs else 0
            _plv  = _gf().get_level()
            action, reason = compute_action(_verd, _dlv, _days, _plv)
            lines.append("  권고    : %s" % ACTION_KOR.get(action, action))
            lines.append("  사유    : %s" % reason)
        except Exception as e:
            lines.append("  권고    : [계산 실패: %s]" % e)

        lines.append("=" * 56)
        return "\n".join(lines)

    def save(self, report: str, filename: Optional[str] = None) -> str:
        """리포트를 파일로 저장. 저장 경로 반환."""
        if not filename:
            filename = "strategy_report_%s.txt" % datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self._dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info("[DailyExporter] 저장: %s", path)
        except Exception as e:
            logger.warning("[DailyExporter] 저장 실패: %s", e)
        return path

    def slack_format(self, report: str) -> str:
        """
        Slack 메시지용 포맷 변환 (코드 블록 래핑).
        `notify_slack(exporter.slack_format(report))` 로 사용.
        """
        return "```\n%s\n```" % report


# ─── 전역 싱글턴 ─────────────────────────────────────────────────────────────
_exporter: Optional[DailyExporter] = None


def get_exporter() -> DailyExporter:
    """전역 DailyExporter 싱글턴 반환."""
    global _exporter
    if _exporter is None:
        _exporter = DailyExporter()
    return _exporter
