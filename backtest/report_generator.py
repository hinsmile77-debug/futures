# backtest/report_generator.py — HTML 성과 리포트 자동 생성
"""
Walk-Forward 검증 결과를 HTML 리포트로 저장.
생성 위치: logs/report_YYYYMMDD_HHMMSS.html
다크 테마, 창별 테이블, Phase 2 기준 충족 여부 포함.
"""
import os
import datetime
import logging
from typing import Optional

from config.settings import LOG_DIR

logger = logging.getLogger(__name__)


class ReportGenerator:
    """HTML 성과 리포트 생성기."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or LOG_DIR

    def generate(
        self,
        walk_forward_result: dict,
        title: str = "미륵이 Walk-Forward 검증 리포트",
    ) -> str:
        """
        HTML 리포트 파일 생성.

        Returns:
            str: 저장된 파일 경로
        """
        os.makedirs(self.output_dir, exist_ok=True)

        ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "report_%s.html" % ts
        filepath = os.path.join(self.output_dir, filename)

        html = self._build_html(walk_forward_result, title, ts)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info("[ReportGenerator] 리포트 저장: %s", filepath)
        return filepath

    # ── HTML 생성 ──────────────────────────────────────────────

    def _build_html(self, result: dict, title: str, ts: str) -> str:
        avg  = result.get("avg_metrics", {})
        crit = result.get("criteria_check", {})

        verdict_color = "#2ecc71" if result.get("passed") else "#e74c3c"
        verdict_text  = crit.get("verdict", "결과 없음")

        n_windows = result.get("total_windows", 0)

        # 평균 지표 카드 생성
        def check(flag):
            return "<span style='color:#2ecc71'>✓</span>" if flag else "<span style='color:#e74c3c'>✗</span>"

        sharpe_check  = check(avg.get("pass_sharpe"))
        mdd_check     = check(avg.get("pass_mdd"))
        winrate_check = check(avg.get("pass_winrate"))

        metric_cards = """
        <div class="metric-card">
          <div class="label">Sharpe Ratio (연간화)</div>
          <div class="value">%(sharpe).2f &nbsp;%(sc)s</div>
          <div class="note">기준 ≥ 1.5</div>
        </div>
        <div class="metric-card">
          <div class="label">최대 낙폭 (MDD)</div>
          <div class="value">%(mdd).1f%% &nbsp;%(mc)s</div>
          <div class="note">기준 ≤ 15%%</div>
        </div>
        <div class="metric-card">
          <div class="label">승률</div>
          <div class="value">%(wr).1f%% &nbsp;%(wc)s</div>
          <div class="note">기준 ≥ 53%%</div>
        </div>
        <div class="metric-card">
          <div class="label">총 거래 횟수</div>
          <div class="value">%(trades)d회</div>
        </div>
        <div class="metric-card">
          <div class="label">누적 손익</div>
          <div class="value">%(pnl)s원</div>
        </div>
        <div class="metric-card">
          <div class="label">Profit Factor</div>
          <div class="value">%(pf).2f</div>
        </div>
        """ % dict(
            sharpe=avg.get("sharpe", 0),
            sc=sharpe_check,
            mdd=abs(avg.get("mdd_pct", 0)) * 100,
            mc=mdd_check,
            wr=avg.get("win_rate", 0) * 100,
            wc=winrate_check,
            trades=avg.get("total_trades", 0),
            pnl="{:,}".format(avg.get("total_pnl_krw", 0)),
            pf=avg.get("profit_factor", 0),
        )

        # 창별 테이블 행 생성
        window_rows = ""
        for w in result.get("windows", []):
            m  = w["metrics"]
            sc = "✓" if m.get("pass_sharpe")  else "✗"
            mc = "✓" if m.get("pass_mdd")     else "✗"
            wc = "✓" if m.get("pass_winrate") else "✗"
            row_class = "pass-row" if (m.get("pass_sharpe") and m.get("pass_mdd") and m.get("pass_winrate")) else ""
            window_rows += (
                "<tr class='%s'>"
                "<td>%d</td><td>%s</td><td>%s</td>"
                "<td>%.2f %s</td><td>%.1f%% %s</td><td>%.1f%% %s</td>"
                "<td>%d</td><td>%s원</td>"
                "</tr>"
            ) % (
                row_class,
                w["window"], w["train_range"], w["test_range"],
                m.get("sharpe", 0), sc,
                abs(m.get("mdd_pct", 0)) * 100, mc,
                m.get("win_rate", 0) * 100, wc,
                m.get("total_trades", 0),
                "{:,}".format(m.get("total_pnl_krw", 0)),
            )

        # Phase 2 기준 테이블
        def crit_row(label, req, actual, passed):
            cls  = "pass" if passed else "fail"
            mark = "통과 ✓" if passed else "미달 ✗"
            return "<tr><td>%s</td><td>%s</td><td>%s</td><td class='%s'>%s</td></tr>" % (
                label, req, actual, cls, mark)

        criteria_rows = (
            crit_row("Sharpe Ratio", "≥ 1.5",
                     "%.2f" % avg.get("sharpe", 0),
                     avg.get("pass_sharpe", False))
            + crit_row("최대 낙폭 (MDD)", "≤ 15%",
                       "%.1f%%" % (abs(avg.get("mdd_pct", 0)) * 100),
                       avg.get("pass_mdd", False))
            + crit_row("승률", "≥ 53%",
                       "%.1f%%" % (avg.get("win_rate", 0) * 100),
                       avg.get("pass_winrate", False))
        )

        css = """
        body{font-family:'Malgun Gothic',sans-serif;background:#1a1a2e;color:#eee;padding:24px;margin:0}
        h1{color:#00d4ff;margin-bottom:4px}
        h2{color:#a0c4ff;border-bottom:1px solid #333;padding-bottom:6px;margin-top:28px}
        .sub{color:#888;font-size:.9em;margin-bottom:16px}
        .verdict{font-size:1.3em;font-weight:bold;color:%(vc)s;padding:10px 16px;
          border:2px solid %(vc)s;border-radius:6px;display:inline-block;margin:10px 0}
        .metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:16px 0}
        .metric-card{background:#16213e;padding:16px;border-radius:8px;border-left:4px solid #00d4ff}
        .metric-card .label{color:#888;font-size:.82em}
        .metric-card .value{font-size:1.5em;font-weight:bold;color:#00d4ff;margin:4px 0}
        .metric-card .note{color:#555;font-size:.78em}
        table{width:100%%;border-collapse:collapse;margin:14px 0}
        th{background:#0f3460;padding:9px;text-align:center;font-size:.9em}
        td{padding:7px;text-align:center;border-bottom:1px solid #2a2a3e}
        tr:hover{background:#1e1e3a}
        .pass-row{background:#0d2d1a}
        .pass{color:#2ecc71} .fail{color:#e74c3c}
        footer{color:#555;font-size:.78em;margin-top:32px}
        """ % {"vc": verdict_color}

        html = (
            "<!DOCTYPE html><html lang='ko'>\n"
            "<head><meta charset='UTF-8'><title>%s</title>"
            "<style>%s</style></head>\n"
            "<body>\n"
            "<h1>%s</h1>\n"
            "<p class='sub'>생성 시각: %s &nbsp;|&nbsp; Walk-Forward %d개 창</p>\n"
            "<div class='verdict'>%s</div>\n"
            "<h2>평균 성과 요약</h2>\n"
            "<div class='metric-grid'>%s</div>\n"
            "<h2>창별 상세 결과</h2>\n"
            "<table><tr>"
            "<th>#</th><th>학습 구간</th><th>검증 구간</th>"
            "<th>Sharpe</th><th>MDD</th><th>승률</th>"
            "<th>거래수</th><th>손익</th>"
            "</tr>%s</table>\n"
            "<h2>Phase 2 실전 진입 기준</h2>\n"
            "<table><tr><th>기준</th><th>요구값</th><th>실제값</th><th>결과</th></tr>"
            "%s</table>\n"
            "<footer>Generated by 미륵이 BacktestSystem | KOSPI200 Futures</footer>\n"
            "</body></html>"
        ) % (
            title, css,
            title, ts, n_windows,
            verdict_text,
            metric_cards,
            window_rows,
            criteria_rows,
        )
        return html
