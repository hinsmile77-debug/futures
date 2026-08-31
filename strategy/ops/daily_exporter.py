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

    def build_report(self, extra_stats: Optional[Dict] = None) -> str:
        """
        현재 전략 상태를 종합하여 리포트 문자열을 반환.
        실패해도 빈 문자열 대신 최소 골격 반환.

        Args:
            extra_stats: 런타임에서만 알 수 있는 당일 통계.
                         {"checklist_conf_fail": int, ...}
        """
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        extra_stats = extra_stats or {}
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
                # [461차, F-7] 라벨에 **기간과 분모**를 박는다(계측 4원칙 ①).
                # Sh/MDD는 롤링 20일 값이고 WR/PF는 당일 값인데, 종전 배너는 넷을
                # 한 줄에 `Live :` 로 묶어 같은 기간처럼 보였다. MDD도 자본 대비를
                # 쓴다 — peak 대비(215.4% 같은 값)는 WFA 기준과 비교 불가.
                sh = live.get("sharpe")
                md = live.get("mdd_pct_of_capital")
                if sh is not None:
                    lines.append(
                        "  Live(20일): Sh=%.2f  MDD(자본대비)=%s" % (
                            sh,
                            "%.1f%%" % (abs(md) * 100) if md is not None else "미측정",
                        )
                    )
                # 당일 WR/PF — 거래 0건이면 0.0/1.00 폴백 대신 미측정으로 표기
                measured = live.get("metrics_measured")
                if measured is False:
                    lines.append("  당일      : WR=미측정(거래0건)  PF=미측정")
                else:
                    wr = live.get("win_rate")
                    pf = live.get("profit_factor")
                    lines.append(
                        "  당일      : WR=%s  PF=%s%s" % (
                            "%.1f%%" % (wr * 100) if wr is not None else "미측정",
                            "%.2f" % pf if pf is not None else "미측정",
                            "" if measured else "  (측정여부 불명 — F-7 이전 기록)",
                        )
                    )
                # 롤링 20일
                rolling = reg.get_rolling_metrics(ver)
                cum = rolling.get("cum_pnl", 0)
                _rc = rolling.get("mdd_pct_of_capital")
                lines.append(
                    "  롤링20일: 누적 %+.0f원  Sh=%.2f  MDD(자본대비)=%s  MDD(peak대비)=%.1f%%" % (
                        cum,
                        rolling.get("sharpe", 0) or 0,
                        "%.1f%%" % (abs(_rc) * 100) if _rc is not None else "미측정",
                        abs(rolling.get("mdd_pct_of_peak", 0) or 0) * 100,
                    )
                )
            else:
                lines.append("  버전    : 데이터 없음")
        except Exception as e:
            lines.append("  [Registry 조회 실패: %s]" % e)

        # ── [MW0601 477차 후속2 / 476차 F-4] 당일 gross/수수료/net 3행 ─────────
        # broker(gross)와 engine(net)이 나란히 보이면 매일 수수료만큼의 설명 불가
        # 격차로 읽힌다(0818: 685,000 vs 661,668). 단위를 같은 자리에 박는다.
        # 실전 전환 기준 ①(4주 통산 수익률)은 net 기준이다.
        try:
            import datetime as _dt
            from utils.db_utils import fetchone as _f4_fetchone, TRADES_DB as _F4_DB
            _f4_row = _f4_fetchone(
                _F4_DB,
                """SELECT pnl_krw, commission_krw, pnl_net_krw
                     FROM daily_broker_pnl WHERE date = ?""",
                (_dt.date.today().isoformat(),))
            if _f4_row is not None:
                _f4_g = _f4_row["pnl_krw"]
                _f4_c = _f4_row["commission_krw"]
                _f4_n = _f4_row["pnl_net_krw"]
                lines.append(
                    "  당일손익 : broker(gross) %s  수수료 %s  net %s  ※ 전환기준①=net" % (
                        ("{:+,.0f}원".format(_f4_g)) if _f4_g is not None else "미측정",
                        ("{:,.0f}원".format(_f4_c)) if _f4_c is not None else "미기입(EOD 전)",
                        ("{:+,.0f}원".format(_f4_n)) if _f4_n is not None else "미기입(EOD 전)",
                    )
                )
        except Exception:
            pass

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
            # 🔴 [MW0601 507차 후속 / F-12] 미측정을 `0.000 (CLEAR)` 로 찍지 않는다.
            #   2026-08-31에 `update_live()` 가 하루 종일 예외로 죽었는데(기준선 키
            #   불일치 — F-7) 이 줄이 `PSI : 0.000 (CLEAR)` 를 찍어, 실제로는
            #   **계측이 통째로 없는 날**이 「가장 조용한 정상」으로 보고됐다.
            #   `CLEAR` 는 「정상 확인됨」이 아니라 그냥 초기값이다(계측 4원칙 ②·④).
            if psi is None:
                lines.append(
                    "  PSI     : 미측정 (오늘 update_live 성공 0회 — 0.000이 아니다)"
                )
            else:
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
            else:
                lines.append("  PSI/feat: 미측정")
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

        # ── [260704 감사 P0] 거래당 순EV(수수료 차감 후) ─────────────────────
        # "방향 적중률" 대신 "이 진입이 수수료 차감 후 돈이 되는가"를 보는 지표.
        try:
            from utils.db_utils import fetch_recent_ev, fetch_ev_by_grade, fetch_ev_by_horizon

            lines.append("-" * 56)
            recent = fetch_recent_ev(20)
            if recent["cnt"] > 0:
                lines.append(
                    f"  최근{recent['cnt']:2d}건 순EV: 평균 {recent['avg_net_pnl_krw']:+,.0f}원  "
                    f"승률 {recent['win_rate'] * 100:.1f}%  합계 {recent['total_net_pnl_krw']:+,.0f}원"
                )
            else:
                lines.append("  최근 순EV   : 체결 데이터 없음")

            grade_rows = fetch_ev_by_grade(days_back=30)
            if grade_rows:
                lines.append("  등급별 순EV(30일): " + "  ".join(
                    f"{r['grade']}={r['avg_net_pnl_krw']:+,.0f}원({r['cnt']}건,승{r['win_rate'] * 100:.0f}%)"
                    for r in grade_rows
                ))

            hz_rows = fetch_ev_by_horizon(days_back=30)
            if hz_rows:
                lines.append("  호라이즌별 순EV(30일): " + "  ".join(
                    f"{r['entry_horizon']}={r['avg_net_pnl_krw']:+,.0f}원({r['cnt']}건)"
                    for r in hz_rows
                ))
        except Exception as e:
            lines.append("  거래당 순EV : [계산 실패: %s]" % e)

        # ── [P3] 당일 Checklist 신뢰도 차단 카운터 ──────────────────────────
        _ccf = extra_stats.get("checklist_conf_fail")
        if _ccf is not None:
            lines.append("-" * 56)
            lines.append("  CL신뢰도차단: %d회 (앙상블 통과→conf 미달 강제 X)" % _ccf)

        # ── [297차, P1-5] mc–conf 괴리 조기경보 계기판 ───────────────────────
        _mc_gap_today = extra_stats.get("mc_gap_today")
        _mc_gap_avg = extra_stats.get("mc_gap_avg")
        if _mc_gap_today is not None:
            try:
                from config.settings import MC_CONF_GAP_ALERT_MIN_TODAY, MC_CONF_GAP_ALERT_MIN_AVG
                _flag = (
                    " ⚠ 하한 미달" if (
                        _mc_gap_today < MC_CONF_GAP_ALERT_MIN_TODAY
                        or (_mc_gap_avg or 0) < MC_CONF_GAP_ALERT_MIN_AVG
                    ) else ""
                )
            except Exception:
                _flag = ""
            lines.append("-" * 56)
            lines.append(
                "  진입후보(conf≥mc): 금일 %d분  5일평균 %.0f분%s"
                % (_mc_gap_today, _mc_gap_avg or 0.0, _flag)
            )
            # [369차, 0723 정기점검] 하한 미달 시 "모델 이상 vs 시장 자체가 조용함"을
            # 즉시 구분하도록 실측 변동성 컨텍스트를 덧붙인다 — 순수 진단용, 권고/판정에는 미반영.
            if _flag:
                try:
                    from utils.db_utils import fetch_realized_volatility_context
                    _vol = fetch_realized_volatility_context(lookback_days=5)
                    if _vol:
                        lines.append(
                            "    └ 변동성(참고): 당일 레인지 %.1fpt(%d일평균 %.1fpt)  "
                            "1분평균변동 %.2fpt(%d일평균 %.2fpt)"
                            % (
                                _vol["today_range"], _vol["n_days"], _vol["avg_range"],
                                _vol["today_mean_abs_move"], _vol["n_days"], _vol["avg_mean_abs_move"],
                            )
                        )
                except Exception as _vol_e:
                    lines.append("    └ 변동성(참고): [계산 실패: %s]" % _vol_e)

        # ── [297차, P1-6] 진입 퍼널 일일 자동 리포트 ─────────────────────────
        # "진입0이 어느 층에서 발생했는가"를 매일 자동으로 남긴다(§4-2 고정 안건 ⑥).
        try:
            from utils.db_utils import fetch_daily_entry_funnel
            _fn = fetch_daily_entry_funnel()
            if _fn["total"] > 0:
                lines.append("-" * 56)
                lines.append("  진입 퍼널(%s, 총 %d분):" % (_fn["date"], _fn["total"]))
                lines.append(
                    "    FLAT %d → conf미달 %d → CoherenceGate %d"
                    " → 게이트차단 %d → 후보 %d → 진입 %d"
                    % (
                        _fn["flat"], _fn["conf_fail"], _fn["coherence_blocked"],
                        _fn["gate_blocked"], _fn["candidate"], _fn["entered"],
                    )
                )
                if _fn.get("grade_override"):
                    # [461차, F-5] 앙상블 grade='X'인데 체크리스트 상향으로 최종관문까지
                    # 간 행(285차-P5가 허용한 합법 경로). 구 집계는 이 행을
                    # CoherenceGate/conf미달로 잘못 계상하고 진입에서 누락했다.
                    lines.append(
                        "    └ 등급상향경로(앙상블X→체크리스트통과): %d건 [285차-P5]"
                        % _fn["grade_override"]
                    )
                if _fn["gate_breakdown"]:
                    _bd = sorted(_fn["gate_breakdown"].items(), key=lambda kv: -kv[1])
                    lines.append(
                        "    게이트별: " + "  ".join("%s=%d" % (k, v) for k, v in _bd)
                    )
                if _fn["exec_fail"]:
                    # [305차] "체결실패"는 주문 미체결로 오해되기 쉬움 — 실제로는 체크리스트
                    # 통과 후 JointGateBlock 등 2차 게이트가 진입 자체를 차단한 것이 대부분.
                    lines.append(
                        "    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): %d건" % _fn["exec_fail"]
                    )
                    if _fn.get("exec_fail_breakdown"):
                        _efbd = sorted(_fn["exec_fail_breakdown"].items(), key=lambda kv: -kv[1])
                        lines.append(
                            "      └ 상세: " + "  ".join("%s=%d" % (k, v) for k, v in _efbd)
                        )

                # ── [461차, G-6] JointGateBlock 무정보폴백 비율 ──────────────
                # 460차 F-1의 판정 조건("3거래일 연속 80% 초과면 게이트 원인")을
                # 사람 손 없이 채운다. 판정문은 min_samples 도달 전까지 내지 않는다.
                try:
                    from utils.db_utils import fetch_daily_joint_gate_fallback
                    _jg = fetch_daily_joint_gate_fallback()
                    if _jg["n"] > 0:
                        _seg = "      └ JointGateBlock %d건" % _jg["n"]
                        if _jg["pct"] is not None:
                            _seg += " (무정보폴백 %d건 = %.1f%%)" % (_jg["fallback"], _jg["pct"])
                        if _jg["unmeasured"]:
                            _seg += " ⚠미계측 %d건(420차 이전)" % _jg["unmeasured"]
                        if not _jg["verdict_ready"]:
                            # [313차] 소표본 확정 금지 — 세기만 하고 판정하지 않는다
                            _seg += " [표본 %d건 부족 — 판정보류]" % _jg["remain_to_min"]
                        lines.append(_seg)
                except Exception as _jge:
                    lines.append("      └ JointGateBlock 폴백집계: [실패: %s]" % _jge)

                # ── [461차, G-4] 퍼널 자기검증 ──────────────────────────────
                # F-5가 고친 누락은 6주 넘게 무경보로 지나갔다. 본질은 버그가
                # 아니라 검산 부재다. 정상이어도 반드시 한 줄 남긴다 —
                # "검산이 돌았다"는 사실 자체가 관측값이기 때문이다.
                try:
                    from utils.db_utils import verify_daily_entry_funnel
                    _bad = verify_daily_entry_funnel(_fn)
                    if _bad:
                        _msg = "⚠ 퍼널 정합성 실패: " + " / ".join(_bad)
                        lines.append("    " + _msg)
                        try:
                            logger.warning("[EntryFunnel] %s", _msg)
                        except Exception:
                            pass
                    else:
                        lines.append("    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)")
                except Exception as _vfe:
                    lines.append("    └ 정합성: [검산 실패: %s]" % _vfe)
        except Exception as e:
            lines.append("  진입 퍼널 : [계산 실패: %s]" % e)

        # ── [303차] 거래소 CB(단일가/서킷브레이커) halt 이력 요약 ─────────────
        # "halt로 인한 데이터 공백"과 "API 지연·연결 끊김"을 로그 없이 구분하기 위함
        # (302차 후속: 진입0 원인분석 시간 단축 목적, dev_memory/NEXT_TODO.md 302차 항목).
        try:
            from utils.db_utils import fetch_daily_exchange_cb_halts
            _ecb = fetch_daily_exchange_cb_halts()
            if _ecb["count"] > 0:
                lines.append("-" * 56)
                lines.append(
                    "  거래소CB halt: %d건, 총 %d분 (%s)"
                    % (
                        _ecb["count"],
                        _ecb["total_gap_min"],
                        ", ".join(
                            "%s~%s(%d분)" % (
                                e["start"][11:16], e["end"][11:16], e["gap_min"]
                            )
                            for e in _ecb["events"]
                        ),
                    )
                )
        except Exception as e:
            lines.append("  거래소CB halt: [계산 실패: %s]" % e)

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
