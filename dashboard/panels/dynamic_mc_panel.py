# dashboard/panels/dynamic_mc_panel.py
"""
Dynamic min_conf monitor panel.

- 상단: 시간대별 현재 mc 카드
- 중단: 신호 통과율 + 금일 mc 갱신 이벤트
- 하단: mc 변경 이력
"""
import datetime
import logging
import os
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

from config.settings import DB_DIR, PREDICTIONS_DB

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

    def _refresh_gauge_pass(self):
        """금일 신호 통과율 계산 → _pass_bar 갱신."""
        today = datetime.date.today().isoformat()
        try:
            from strategy.entry.time_strategy_router import _ZONE_PARAMS
            fallback_mc = _ZONE_PARAMS.get("STABLE_TREND", {}).get("min_confidence", 0.57)
        except Exception:
            fallback_mc = 0.57

        rows = []
        try:
            conn = sqlite3.connect(PREDICTIONS_DB, timeout=5)
            rows = conn.execute(
                "SELECT confidence, min_conf FROM ensemble_decisions "
                "WHERE ts >= ? AND ts < ?",
                (today, today + "Z"),
            ).fetchall()
            conn.close()
        except Exception:
            pass

        if not rows:
            return

        total = len(rows)
        pass_n = sum(1 for c, mc in rows if float(c) >= float(mc or fallback_mc))
        pass_r = pass_n / total * 100

        self._pass_bar.setValue(int(pass_r))
        chunk_color = (
            _COL["green"] if 15 <= pass_r <= 35 else
            _COL["orange"] if pass_r > 35 else _COL["red"]
        )
        self._pass_bar.setStyleSheet(
            "QProgressBar { border:1px solid %s; border-radius:4px; background:%s; "
            "color:%s; text-align:center; height:24px; font-size:12px; font-weight:bold; }"
            "QProgressBar::chunk { background:%s; border-radius:3px; }"
            % (_COL["border"], _COL["bg3"], _COL["text"], chunk_color)
        )

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
        import time as _t, logging as _log
        _t0 = _t.monotonic()
        try:
            self._refresh_mc_cards()
            self._refresh_gauge_pass()
            self._refresh_history()
        except Exception as e:
            logger.debug("[DynMCPanel] refresh error: %s", e)
        _ms = (_t.monotonic() - _t0) * 1000
        if _ms > 200:
            _log.getLogger("SYSTEM").warning("[LiveDBG] DynMCPanel.refresh slow %.0fms", _ms)

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
