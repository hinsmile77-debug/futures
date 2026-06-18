# dashboard/panels/dynamic_mc_panel.py
"""
Dynamic min_conf monitor panel.

- 상단: 시간대별 현재 mc 카드
- 중단: 신호 통과율 + 금일 mc 갱신 이벤트
- 하단1: 금일 conf -> 진입단계 추적
- 하단2: mc 변경 이력
"""
import datetime
import json
import logging
import os
import re
import sqlite3

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config.settings import DB_DIR, LOG_DIR, PREDICTIONS_DB, TRADES_DB

logger = logging.getLogger("SYSTEM")
MC_HISTORY_DB = os.path.join(DB_DIR, "mc_history.db")

_COL = {
    "bg": "#0d1117",
    "bg2": "#161b22",
    "bg3": "#1c2128",
    "border": "#30363d",
    "text": "#e6edf3",
    "muted": "#8b949e",
    "green": "#3fb950",
    "yellow": "#e3b341",
    "orange": "#d29922",
    "red": "#f85149",
    "blue": "#58a6ff",
    "purple": "#bc8cff",
}

_TABLE_STYLE = (
    "QTableWidget {"
    " background:%s;"
    " color:%s;"
    " gridline-color:%s;"
    " border:1px solid %s;"
    " font-size:11px;"
    " selection-background-color:%s;"
    " selection-color:%s;"
    "}"
    "QHeaderView::section {"
    " background:%s;"
    " color:%s;"
    " border:none;"
    " padding:4px 6px;"
    " font-size:11px;"
    " font-weight:bold;"
    "}"
) % (
    _COL["bg2"],
    _COL["text"],
    _COL["border"],
    _COL["border"],
    _COL["bg3"],
    _COL["text"],
    _COL["bg3"],
    _COL["muted"],
)

_ZONES = [
    "GAP_OPEN",
    "OPEN_VOLATILE",
    "STABLE_TREND",
    "LUNCH_RECOVERY",
    "CLOSE_VOLATILE",
]
_ZONE_KR = {
    "GAP_OPEN": "시초가",
    "OPEN_VOLATILE": "개장",
    "STABLE_TREND": "안정",
    "LUNCH_RECOVERY": "점심",
    "CLOSE_VOLATILE": "마감",
}

_ENTRY_STAGE_TOOLTIP = (
    "진입단계 판정 순서\n"
    "1. conf미달: conf < mc\n"
    "2. FLAT(X): direction=0 또는 grade=X\n"
    "3. gate차단: gate_blocked=1 또는 gate_reason='blocked_by_microstructure'\n"
    "4. regime불일치: regime_ok=0\n"
    "5. Meta skip: meta_action='skip'\n"
    "6. Toxic block/reduce: toxicity_action='block' 또는 'reduce'\n"
    "7. Auto 불가: 체크리스트 auto_entry=0\n"
    "8. STEP7 차단: 체크리스트는 통과했지만 CB·Hurst·ATR·쿨다운·재시작유예·\n"
    "   포지션무결성·역방향클램프·IntradayRegime·모드필터 등 STEP7 마스터\n"
    "   게이트 중 하나라도 실패 — '차단사유' 칸에 구체 원인 표시, 단계 칸\n"
    "   호버 시 16개 조건 ✓/✗ 전체 표시\n"
    "9. 진입후보(최종): STEP7 마스터 게이트 전체 통과 — 자동진입 대기/실행 중\n"
    "10. 진입완료: 실제 체결(trades.db/TRADE.log) 확인됨\n"
    "\n"
    "색상 규칙\n"
    "Δ: +초록 / -빨강\n"
    "grade: A,B 초록 / C 노랑 / X 빨강\n"
    "dir: F 회색\n"
    "진입단계: 1,8 빨강 / 2 주황 / 3,4 노랑 / 5,6 보라 / 7 파랑 / 9,10 초록"
)


def _card(title: str, widget: QWidget) -> QGroupBox:
    box = QGroupBox(title)
    box.setStyleSheet(
        "QGroupBox { font-size:11px; font-weight:bold; color:%s;"
        " border:1px solid %s; border-radius:4px; margin-top:6px; padding:4px; }"
        "QGroupBox::title { subcontrol-origin:margin; left:8px; padding:0 4px; }"
        % (_COL["muted"], _COL["border"])
    )
    lay = QVBoxLayout(box)
    lay.setContentsMargins(4, 6, 4, 4)
    lay.addWidget(widget)
    return box


class DynamicMcPanel(QWidget):
    """동적 min_conf 모니터 패널."""

    REFRESH_MS = 30_000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:%s; color:%s;" % (_COL["bg"], _COL["text"]))
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(self.REFRESH_MS)
        self.refresh()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        root.addWidget(_card("현재 min_conf (시간대별)", self._build_mc_cards()))
        root.addWidget(_card("신호 통과율 & 갱신 이벤트", self._build_gauge_area()))
        trend_card = _card("금일 conf → 진입단계 추적", self._build_trend_area())
        trend_card.setToolTip(_ENTRY_STAGE_TOOLTIP)
        root.addWidget(trend_card)
        root.addWidget(_card("mc 변경 이력 (최근 20건)", self._build_history_table()))

        self._dir_dialog    = None
        self._candle_dialog = None

        btn_row = QHBoxLayout()

        btn_dir = QPushButton("▲▼ 호라이즌 합창판")
        btn_dir.setStyleSheet(
            "QPushButton { background:#1c2128; color:#e6edf3; border:1px solid #30363d;"
            " border-radius:4px; padding:5px 10px; font-size:12px; font-weight:bold; }"
            "QPushButton:hover { background:#30363d; }"
            "QPushButton:pressed { background:#0d1117; }"
        )
        btn_dir.clicked.connect(self._open_dir_indicator)
        btn_row.addWidget(btn_dir)

        btn_chart = QPushButton("📊 봉차트 방향")
        btn_chart.setStyleSheet(
            "QPushButton { background:#1c2128; color:#e6edf3; border:1px solid #30363d;"
            " border-radius:4px; padding:5px 10px; font-size:12px; font-weight:bold; }"
            "QPushButton:hover { background:#30363d; }"
            "QPushButton:pressed { background:#0d1117; }"
        )
        btn_chart.clicked.connect(self._open_candle_chart)
        btn_row.addWidget(btn_chart)

        root.addLayout(btn_row)

    def _build_mc_cards(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        self._mc_labels = {}

        for zone in _ZONES:
            card = QFrame()
            card.setFrameStyle(QFrame.StyledPanel)
            card.setStyleSheet(
                "QFrame { background:%s; border:1px solid %s; border-radius:4px; }"
                % (_COL["bg3"], _COL["border"])
            )
            cl = QVBoxLayout(card)
            cl.setContentsMargins(6, 4, 6, 4)
            cl.setSpacing(2)

            zone_lbl = QLabel(_ZONE_KR.get(zone, zone))
            zone_lbl.setAlignment(Qt.AlignCenter)
            zone_lbl.setStyleSheet("font-size:10px; color:%s;" % _COL["muted"])

            mc_lbl = QLabel("-.---")
            mc_lbl.setAlignment(Qt.AlignCenter)
            mc_lbl.setStyleSheet(
                "font-size:16px; font-weight:bold; color:%s;" % _COL["blue"]
            )
            mc_lbl.setFont(QFont("Consolas", 14, QFont.Bold))

            diff_lbl = QLabel("")
            diff_lbl.setAlignment(Qt.AlignCenter)
            diff_lbl.setStyleSheet("font-size:10px; color:%s;" % _COL["muted"])

            cl.addWidget(zone_lbl)
            cl.addWidget(mc_lbl)
            cl.addWidget(diff_lbl)
            lay.addWidget(card)
            self._mc_labels[zone] = (mc_lbl, diff_lbl)

        return w

    def _build_trend_area(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self._lbl_today_avg = QLabel("오늘 conf 평균: --")
        self._lbl_today_avg.setStyleSheet("font-size:11px; color:%s;" % _COL["text"])
        self._lbl_today_pass = QLabel("통과율: --")
        self._lbl_today_pass.setStyleSheet("font-size:11px; color:%s;" % _COL["green"])

        sumrow = QHBoxLayout()
        sumrow.addWidget(self._lbl_today_avg)
        sumrow.addStretch()
        sumrow.addWidget(self._lbl_today_pass)
        lay.addLayout(sumrow)

        self._bar_table = QTableWidget(0, 10)
        self._bar_table.setHorizontalHeaderLabels(
            ["시각", "conf(ema)", "mc", "Δ", "dir", "grade", "gate", "meta/tox",
             "차단사유", "진입단계"]
        )
        hdr = self._bar_table.horizontalHeader()
        for idx in (0, 1, 2, 3, 4, 5, 6):
            hdr.setSectionResizeMode(idx, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(7, QHeaderView.Stretch)
        hdr.setSectionResizeMode(8, QHeaderView.Stretch)
        hdr.setSectionResizeMode(9, QHeaderView.Stretch)
        self._bar_table.setMinimumHeight(260)
        self._bar_table.setMaximumHeight(380)
        self._bar_table.setAlternatingRowColors(False)
        self._bar_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._bar_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._bar_table.setSelectionMode(QTableWidget.NoSelection)
        self._bar_table.setShowGrid(True)
        self._bar_table.verticalHeader().setDefaultSectionSize(22)
        self._bar_table.verticalHeader().setMinimumSectionSize(22)
        self._bar_table.setStyleSheet(_TABLE_STYLE)
        self._bar_table.setFont(QFont("Consolas", 11))
        lay.addWidget(self._bar_table)
        return w

    def _build_gauge_area(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self._pass_bar = QProgressBar()
        self._pass_bar.setRange(0, 100)
        self._pass_bar.setValue(0)
        self._pass_bar.setTextVisible(True)
        self._pass_bar.setFormat("통과율 %p%")
        self._pass_bar.setStyleSheet(
            "QProgressBar { border:1px solid %s; border-radius:4px; background:%s; "
            "color:%s; text-align:center; height:24px; font-size:12px; font-weight:bold; }"
            "QProgressBar::chunk { background:#58a6ff; border-radius:3px; }"
            % (_COL["border"], _COL["bg3"], _COL["text"])
        )
        lay.addWidget(QLabel("금일 신호 통과율"))
        lay.addWidget(self._pass_bar)

        lbl_target = QLabel("목표: 15~35% (너무 낮으면 기회 부족 / 너무 높으면 품질 저하)")
        lbl_target.setStyleSheet("font-size:10px; color:%s;" % _COL["muted"])
        lbl_target.setWordWrap(True)
        lay.addWidget(lbl_target)
        lay.addSpacing(8)

        lbl_ev = QLabel("금일 mc 갱신 이벤트")
        lbl_ev.setStyleSheet(
            "font-size:11px; font-weight:bold; color:%s;" % _COL["text"]
        )
        lay.addWidget(lbl_ev)

        self._event_log = QTextEdit()
        self._event_log.setReadOnly(True)
        self._event_log.setPlainText("(금일 갱신 이벤트 없음)")
        self._event_log.setStyleSheet(
            "QTextEdit { font-size:10px; color:%s; background:%s; "
            "padding:6px; border:1px solid %s; border-radius:3px; }"
            % (_COL["muted"], _COL["bg3"], _COL["border"])
        )
        self._event_log.setMinimumHeight(120)
        self._event_log.setFont(QFont("Consolas", 10))
        self._event_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addWidget(self._event_log)
        lay.addStretch()
        return w

    def _build_history_table(self) -> QWidget:
        t = QTableWidget(0, 7)
        t.setHorizontalHeaderLabels(
            ["시각", "트리거", "시간대", "이전mc", "새mc", "변화", "기반(p65)"]
        )
        t.setMinimumHeight(150)
        t.setMaximumHeight(220)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.setAlternatingRowColors(False)
        t.setShowGrid(True)
        t.verticalHeader().setDefaultSectionSize(22)
        t.setStyleSheet(_TABLE_STYLE)
        t.setFont(QFont("Consolas", 10))
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        self._hist_table = t
        return t

    def _open_dir_indicator(self):
        from dashboard.panels.direction_indicator_dialog import DirectionIndicatorDialog
        if self._dir_dialog is None or not self._dir_dialog.isVisible():
            self._dir_dialog = DirectionIndicatorDialog(parent=None)
        self._dir_dialog.show()
        self._dir_dialog.raise_()
        self._dir_dialog.activateWindow()

    def _open_candle_chart(self):
        from dashboard.panels.candle_chart_dialog import CandleChartDialog
        if self._candle_dialog is None or not self._candle_dialog.isVisible():
            self._candle_dialog = CandleChartDialog(parent=None)
        self._candle_dialog.show()
        self._candle_dialog.raise_()
        self._candle_dialog.activateWindow()

    def refresh(self):
        try:
            self._refresh_mc_cards()
            self._refresh_trend()
            self._refresh_history()
        except Exception as e:
            logger.debug("[DynMCPanel] refresh error: %s", e)

    def _refresh_mc_cards(self):
        try:
            from strategy.entry.time_strategy_router import _ZONE_PARAMS
        except Exception:
            return

        old_mc = {}
        try:
            hist = self._get_recent_history(5)
            for row in hist:
                zone = row.get("zone", "")
                if zone not in old_mc:
                    old_mc[zone] = row.get("old_mc")
        except Exception:
            pass

        for zone, (mc_lbl, diff_lbl) in self._mc_labels.items():
            mc = _ZONE_PARAMS.get(zone, {}).get("min_confidence", 0.0)
            mc_lbl.setText("%.3f" % mc)

            old = old_mc.get(zone)
            if old is not None and abs(mc - old) >= 0.005:
                delta = mc - old
                color = _COL["green"] if delta < 0 else _COL["orange"]
                sign = "+" if delta > 0 else ""
                diff_lbl.setText("%s%.3f" % (sign, delta))
                diff_lbl.setStyleSheet("font-size:10px; color:%s;" % color)
                mc_lbl.setStyleSheet(
                    "font-size:16px; font-weight:bold; color:%s;" % color
                )
            else:
                diff_lbl.setText("")
                mc_lbl.setStyleSheet(
                    "font-size:16px; font-weight:bold; color:%s;" % _COL["blue"]
                )

    def _refresh_trend(self):
        today = datetime.date.today().isoformat()
        try:
            from strategy.entry.time_strategy_router import _ZONE_PARAMS

            fallback_mc = _ZONE_PARAMS.get("STABLE_TREND", {}).get("min_confidence", 0.57)
        except Exception:
            fallback_mc = 0.57

        completed_entries = self._get_completed_entry_map(today)

        rows = []
        try:
            conn = sqlite3.connect(PREDICTIONS_DB, timeout=5)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT ts, direction, confidence, grade, auto_entry, regime_ok, "
                "       min_conf, gate_reason, gate_blocked, meta_action, meta_confidence, "
                "       meta_reason, toxicity_action, toxicity_score, toxicity_reason, "
                "       entry_gate_json, entry_final_ok, entry_qty, entry_mode, "
                "       entry_executed, entry_block_reason "
                "FROM ensemble_decisions "
                "WHERE substr(ts,1,10)=? ORDER BY ts",
                (today,),
            ).fetchall()
            conn.close()
        except Exception:
            pass

        if not rows:
            self._bar_table.setRowCount(0)
            return

        confs = [float(r["confidence"]) for r in rows]
        mcs = [float(r["min_conf"] or fallback_mc) for r in rows]
        avg_c = sum(confs) / len(confs)
        avg_mc = sum(mcs) / len(mcs)
        pass_n = sum(
            1 for r in rows if float(r["confidence"]) >= float(r["min_conf"] or fallback_mc)
        )
        pass_r = pass_n / len(rows) * 100

        self._lbl_today_avg.setText(
            "오늘 conf 평균: <b>%.3f</b>  mc=%.3f  여유:%+.3f"
            % (avg_c, avg_mc, avg_c - avg_mc)
        )
        self._lbl_today_avg.setTextFormat(Qt.RichText)
        self._lbl_today_pass.setText(
            "통과율: <b>%.0f%%</b> (%d/%d봉)" % (pass_r, pass_n, len(rows))
        )
        self._lbl_today_pass.setTextFormat(Qt.RichText)
        self._lbl_today_pass.setStyleSheet(
            "font-size:11px; color:%s;"
            % (
                _COL["green"]
                if 15 <= pass_r <= 35
                else _COL["yellow"]
                if pass_r < 15
                else _COL["orange"]
            )
        )

        self._pass_bar.setValue(int(pass_r))
        chunk_color = (
            _COL["green"]
            if 15 <= pass_r <= 35
            else _COL["orange"]
            if pass_r > 35
            else _COL["red"]
        )
        self._pass_bar.setStyleSheet(
            "QProgressBar { border:1px solid %s; border-radius:4px; background:%s; "
            "color:%s; text-align:center; height:24px; font-size:12px; font-weight:bold; }"
            "QProgressBar::chunk { background:%s; border-radius:3px; }"
            % (_COL["border"], _COL["bg3"], _COL["text"], chunk_color)
        )

        # P4: 전체 오늘 데이터 기준으로 span=20 EMA 계산 (display용 — 실거래 로직 무영향)
        _ema_alpha = 2.0 / (20 + 1)
        _ema_val = None
        _ema_list = []
        for _r in rows:
            _c = float(_r["confidence"])
            _ema_val = _c if _ema_val is None else (_ema_alpha * _c + (1.0 - _ema_alpha) * _ema_val)
            _ema_list.append(_ema_val)
        ema_sample = _ema_list[-24:]

        sample = rows[-24:]
        self._bar_table.setRowCount(len(sample))
        for i, r in enumerate(sample):
            conf = ema_sample[i]      # P4: EMA 표시
            mc = float(r["min_conf"] or fallback_mc)
            delta = conf - mc
            ts_str = r["ts"][11:16]
            direction = self._fmt_direction(r["direction"])
            grade = str(r["grade"] or "")
            gate = self._fmt_gate(r["gate_reason"], r["gate_blocked"], conf, mc)
            meta_tox = self._fmt_meta_tox(
                r["meta_action"],
                r["meta_confidence"],
                r["toxicity_action"],
                r["toxicity_score"],
            )
            completed_entry = self._lookup_completed_entry(completed_entries, str(r["ts"]))
            stage, stage_reason = self._resolve_stage(r, conf, mc, completed_entry)
            block_reason = self._resolve_block_reason(r, stage, stage_reason)

            conf_bg, conf_fg = self._conf_colors(conf, mc)
            items = [
                self._make_item(ts_str, bold=True),
                self._make_item("%.3f" % conf, fg=conf_fg, bg=conf_bg, bold=True),
                self._make_item("%.3f" % mc, fg=_COL["text"], bold=True),
                self._make_item("%+.3f" % delta, fg=_COL["green"] if delta >= 0 else _COL["red"], bold=True),
                self._make_item(direction, fg=self._direction_color(direction), bold=True),
                self._make_item(grade, fg=self._grade_color(grade), bold=True),
                self._make_item(gate, fg=self._gate_color(gate), bold=True),
                self._make_item(meta_tox, fg=self._meta_color(meta_tox)),
                self._make_item(block_reason, fg=self._stage_color(stage)),
                self._make_item(stage, fg=self._stage_color(stage), bold=True),
            ]
            _gate_tip = self._entry_gate_tooltip(
                r["entry_gate_json"] if "entry_gate_json" in r.keys() else ""
            )
            for j, item in enumerate(items):
                if j == 9 and completed_entry:
                    item.setToolTip(self._entry_complete_tooltip(completed_entry))
                elif j in (8, 9) and _gate_tip:
                    item.setToolTip(_gate_tip)
                self._bar_table.setItem(i, j, item)

    def _refresh_history(self):
        hist = self._get_recent_history(20)
        today = datetime.date.today().isoformat()

        today_events = [h for h in hist if h.get("ts", "")[:10] == today]
        if today_events:
            lines = []
            for ev in today_events:
                lines.append(
                    "[%s] %s  %s: %.3f→%.3f"
                    % (
                        ev["ts"][11:16],
                        ev["trigger"],
                        ev["zone"],
                        ev["old_mc"],
                        ev["new_mc"],
                    )
                )
            self._event_log.setPlainText("\n".join(lines))
        else:
            self._event_log.setPlainText("(금일 갱신 이벤트 없음)")

        self._hist_table.setRowCount(len(hist))
        for i, row in enumerate(hist):
            delta = row["new_mc"] - row["old_mc"]
            color = (
                _COL["green"]
                if delta < -0.001
                else _COL["orange"]
                if delta > 0.001
                else _COL["muted"]
            )
            ts_raw = row.get("ts", "")
            ts_short = (
                ts_raw[5:7] + ts_raw[8:10] + "-" + ts_raw[11:13] + ts_raw[14:16]
                if len(ts_raw) >= 16
                else ts_raw
            )

            vals = [
                ts_short,
                row.get("trigger", ""),
                _ZONE_KR.get(row.get("zone", ""), row.get("zone", "")),
                "%.3f" % row.get("old_mc", 0),
                "%.3f" % row.get("new_mc", 0),
                "%+.3f" % delta,
                "%.3f" % row.get("conf_p65", 0),
            ]
            for j, val in enumerate(vals):
                item = self._make_item(val, fg=color if j == 5 else None, bold=(j == 5))
                self._hist_table.setItem(i, j, item)

    def _get_completed_entry_map(self, today: str) -> dict:
        done = {}
        done.update(self._get_completed_entry_map_from_db(today))
        done.update(self._get_completed_entry_map_from_log(today))
        return done

    def _get_completed_entry_map_from_db(self, today: str) -> dict:
        if not os.path.exists(TRADES_DB):
            return {}
        try:
            conn = sqlite3.connect(TRADES_DB, timeout=5)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT entry_ts, direction, quantity, grade, had_partial_fill "
                "FROM trades WHERE substr(entry_ts,1,10)=?",
                (today,),
            ).fetchall()
            conn.close()
        except Exception:
            return {}

        done = {}
        for row in rows:
            ts = row["entry_ts"]
            if not ts:
                continue
            key = self._minute_key(str(ts))
            if not key:
                continue
            done[key] = {
                "direction": row["direction"] or "",
                "quantity": int(row["quantity"] or 0),
                "grade": row["grade"] or "",
                "had_partial_fill": int(row["had_partial_fill"] or 0),
                "source": "trades.db",
                "entry_ts": str(ts),
            }
        return done

    def _get_completed_entry_map_from_log(self, today: str) -> dict:
        log_path = os.path.join(LOG_DIR, today.replace("-", "") + "_TRADE.log")
        if not os.path.exists(log_path):
            return {}

        patterns = (
            "[체결진입]",
            "[체결진입보정]",
            "[체결동기화] 외부진입",
        )
        done = {}
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as fp:
                for line in fp:
                    if not any(token in line for token in patterns):
                        continue
                    key = self._minute_key(line[:19])
                    if not key:
                        continue
                    direction, quantity = self._parse_trade_log_fill(line)
                    done[key] = {
                        "direction": direction,
                        "quantity": quantity,
                        "grade": "",
                        "had_partial_fill": 1 if "보정" in line else 0,
                        "source": os.path.basename(log_path),
                        "entry_ts": line[:19],
                    }
        except Exception:
            return {}
        return done

    def _parse_trade_log_fill(self, line: str) -> tuple:
        direction = ""
        if " LONG " in line or "LONG" in line:
            direction = "LONG"
        elif " SHORT " in line or "SHORT" in line:
            direction = "SHORT"

        match = re.search(r"(\d+)계약", line)
        quantity = int(match.group(1)) if match else 0
        return direction, quantity

    def _minute_key(self, ts: str) -> str:
        if not ts or len(ts) < 16:
            return ""
        return str(ts)[:16]

    def _lookup_completed_entry(self, completed_entries: dict, ts: str):
        if not completed_entries:
            return None

        base_dt = self._parse_minute_dt(ts)
        if base_dt is None:
            return completed_entries.get(self._minute_key(ts))

        for offset_min in (0, -1, 1, -2, 2):
            key = (base_dt + datetime.timedelta(minutes=offset_min)).strftime("%Y-%m-%d %H:%M")
            entry = completed_entries.get(key)
            if entry:
                return entry
        return None

    def _parse_minute_dt(self, ts: str):
        key = self._minute_key(ts)
        if not key:
            return None
        try:
            return datetime.datetime.strptime(key, "%Y-%m-%d %H:%M")
        except Exception:
            return None

    def _entry_complete_tooltip(self, completed_entry: dict) -> str:
        direction = completed_entry.get("direction") or "-"
        quantity = int(completed_entry.get("quantity") or 0)
        grade = completed_entry.get("grade") or "-"
        partial = "예" if int(completed_entry.get("had_partial_fill") or 0) else "아니오"
        source = completed_entry.get("source") or "-"
        entry_ts = completed_entry.get("entry_ts") or "-"
        return (
            "실제 진입완료 확인\n"
            "시각: %s\n"
            "방향: %s\n"
            "수량: %d계약\n"
            "등급: %s\n"
            "부분체결: %s\n"
            "근거: %s"
        ) % (entry_ts, direction, quantity, grade, partial, source)

    def _get_recent_history(self, limit: int) -> list:
        if not os.path.exists(MC_HISTORY_DB):
            return []
        try:
            conn = sqlite3.connect(MC_HISTORY_DB, timeout=5)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM mc_history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []

    def _make_item(
        self,
        text: str,
        fg: str = None,
        bg: QColor = None,
        bold: bool = False,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        if fg:
            item.setForeground(QColor(fg))
        if bg is not None:
            item.setBackground(bg)
        if bold:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        return item

    def _conf_colors(self, conf: float, mc: float):
        if conf >= mc:
            return QColor("#153624"), _COL["green"]
        if conf >= mc - 0.05:
            return QColor("#3a3012"), _COL["yellow"]
        return QColor("#3a1212"), _COL["red"]

    def _fmt_direction(self, direction) -> str:
        direction = int(direction or 0)
        if direction > 0:
            return "UP"
        if direction < 0:
            return "DN"
        return "F"

    def _fmt_gate(self, gate_reason, gate_blocked, conf, mc) -> str:
        if conf < mc:
            return "conf↓"
        if int(gate_blocked or 0):
            return "blocked"
        reason = str(gate_reason or "")
        if reason and reason != "inactive":
            return reason[:10]
        return "pass"

    def _fmt_meta_tox(
        self,
        meta_action,
        meta_confidence,
        toxicity_action,
        toxicity_score,
    ) -> str:
        meta = str(meta_action or "-")
        meta_conf = float(meta_confidence or 0.0)
        tox = str(toxicity_action or "-")
        tox_score = float(toxicity_score or 0.0)
        return "%s %.2f / %s %.2f" % (meta, meta_conf, tox, tox_score)

    def _resolve_stage(self, row, conf: float, mc: float, completed_entry=None):
        """진입단계 판정. (stage_label, detail) 튜플 반환 — detail은 8단계(STEP7 차단)일 때
        main.py가 산출한 구체 차단사유, 그 외 단계는 _resolve_block_reason()이 별도 생성."""
        direction = int(row["direction"] or 0)
        grade = str(row["grade"] or "")
        gate_reason = str(row["gate_reason"] or "")
        gate_blocked = int(row["gate_blocked"] or 0)
        regime_ok = int(row["regime_ok"] or 0)
        meta_action = str(row["meta_action"] or "")
        toxicity_action = str(row["toxicity_action"] or "")
        auto_entry = int(row["auto_entry"] or 0)
        _keys = row.keys()
        _raw_final_ok = row["entry_final_ok"] if "entry_final_ok" in _keys else None
        entry_final_ok = None if _raw_final_ok is None else int(_raw_final_ok)
        entry_block_reason = (
            str(row["entry_block_reason"] or "") if "entry_block_reason" in _keys else ""
        )

        if completed_entry:
            return "10. 진입완료 ✓", ""
        if conf == 0.0 and direction == 0 and grade == "X":
            return "0. cold-start 대기", ""
        if conf < mc:
            return "1. conf미달", ""
        if direction == 0 or grade == "X":
            return "2. FLAT(X)", ""
        if gate_blocked or gate_reason == "blocked_by_microstructure":
            return "3. gate차단", ""
        if regime_ok == 0:
            return "4. regime불일치", ""
        if meta_action == "skip":
            return "5. Meta skip", ""
        if toxicity_action == "block":
            return "6. Toxic block", ""
        if toxicity_action == "reduce":
            return "6. Toxic reduce", ""
        if auto_entry == 0:
            return "7. Auto 불가", ""
        # STEP7 마스터 게이트(CB·Hurst·ATR·쿨다운·재시작유예 등) — main.py에서 산출된 값
        if entry_final_ok == 0:
            return "8. STEP7 차단", entry_block_reason
        return "9. 진입후보(최종) ▶", ""

    def _resolve_block_reason(self, row, stage: str, stage_detail: str) -> str:
        """단계별 차단사유를 트레이더가 한눈에 읽을 수 있는 한 줄 텍스트로 변환."""
        if stage.startswith("0."):
            return "초기화(cold-start) 대기 중"
        if stage.startswith("1."):
            return "신뢰도 미달 (conf < mc)"
        if stage.startswith("2."):
            return "방향 없음(FLAT) 또는 앙상블 등급 X"
        if stage.startswith("3."):
            gr = str(row["gate_reason"] or "")
            return f"마이크로구조 게이트 차단 ({gr})" if gr else "마이크로구조 게이트 차단"
        if stage.startswith("4."):
            return "레짐 불일치 (regime_ok=0)"
        if stage.startswith("5."):
            mr = str(row["meta_reason"] or "") if "meta_reason" in row.keys() else ""
            return f"MetaGate skip ({mr})" if mr else "MetaGate skip"
        if stage.startswith("6."):
            tr = str(row["toxicity_reason"] or "") if "toxicity_reason" in row.keys() else ""
            tox_act = str(row["toxicity_action"] or "")
            return f"ToxicityGate {tox_act} ({tr})" if tr else f"ToxicityGate {tox_act}"
        if stage.startswith("7."):
            return "체크리스트 자동진입 조건 미달 (auto_entry=0)"
        if stage.startswith("8."):
            return stage_detail or "STEP7 마스터 게이트 차단 (상세 미수집)"
        if stage.startswith("9."):
            return "모든 조건 통과 — 진입 대기/실행 중"
        if stage.startswith("10."):
            return "체결 완료"
        return "-"

    _GATE_CHECK_LABELS = {
        "cb_normal":        "Circuit Breaker 정상",
        "hc_ok":            "고신뢰 연속오답 차단 없음",
        "new_entry_time":   "신규진입 시간대 (15:00 이전)",
        "broker_sync_ok":   "브로커 sync 검증됨",
        "cooldown_ok":      "ENTRY 타임아웃 쿨다운 해제",
        "exit_cooldown_ok": "청산 후 쿨다운 해제",
        "armistice_ok":     "재시작 유예(Armistice) 해제",
        "integrity_ok":     "포지션 무결성 정상",
        "reverse_clamp_ok": "역방향 클램프 해제",
        "hurst_ok":         "Hurst ≥ 0.45 (추세장)",
        "atr_ok":           "ATR ≥ 최소 변동성",
        "mode_filter_ok":   "등급-진입모드 필터 통과",
        "qty_ok":           "산출수량 > 0",
        "bar_volume_ok":    "분봉 거래량 ≠ 0",
        "intraday_ok":      "IntradayRegime(L2) 허용",
        "kill_switch_ok":   "Early Kill Switch 비활성",
    }

    def _entry_gate_tooltip(self, gate_json: str) -> str:
        """STEP7 마스터 게이트의 조건별 통과 여부를 ✓/✗ 목록으로 보여주는 툴팁."""
        if not gate_json:
            return ""
        try:
            gate = json.loads(gate_json)
        except Exception:
            return ""
        if not gate:
            return ""
        lines = ["STEP7 마스터 게이트 상세"]
        for key, label in self._GATE_CHECK_LABELS.items():
            if key in gate:
                mark = "✓" if gate[key] else "✗"
                lines.append(f"{mark} {label}")
        return "\n".join(lines)

    def _direction_color(self, direction: str) -> str:
        if direction == "UP":
            return _COL["green"]
        if direction == "DN":
            return _COL["blue"]
        return _COL["muted"]

    def _grade_color(self, grade: str) -> str:
        if grade in ("A", "B"):
            return _COL["green"]
        if grade == "C":
            return _COL["yellow"]
        return _COL["red"]

    def _gate_color(self, gate: str) -> str:
        if gate == "pass":
            return _COL["green"]
        if gate == "conf↓":
            return _COL["red"]
        if gate == "blocked":
            return _COL["yellow"]
        return _COL["yellow"]

    def _meta_color(self, meta_tox: str) -> str:
        if "skip" in meta_tox:
            return _COL["purple"]
        if "block" in meta_tox:
            return _COL["purple"]
        if "reduce" in meta_tox:
            return _COL["orange"]
        return _COL["muted"]

    def _stage_color(self, stage: str) -> str:
        if stage.startswith("10."):
            return _COL["green"]
        if stage.startswith("9."):
            return _COL["green"]
        if stage.startswith("8."):
            return _COL["red"]
        if stage.startswith("1."):
            return _COL["red"]
        if stage.startswith("2."):
            return _COL["orange"]
        if stage.startswith("3.") or stage.startswith("4."):
            return _COL["yellow"]
        if stage.startswith("5.") or stage.startswith("6."):
            return _COL["purple"]
        if stage.startswith("7."):
            return _COL["blue"]
        return _COL["muted"]
