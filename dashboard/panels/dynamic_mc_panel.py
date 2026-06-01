# dashboard/panels/dynamic_mc_panel.py — 동적 min_conf 모니터 패널
"""
DynamicMcPanel — 선물 1% 수익율 트레이더 관점 설계

레이아웃 (3단):
  ┌─────────────────────────────────────────────────────────────┐
  │ 상단: 현재 mc 현황 카드 (시간대별 6개)                        │
  ├────────────────────────┬────────────────────────────────────┤
  │ 중단 좌: 금일 conf vs mc  │ 중단 우: 신호 통과율 + 갱신 트리거  │
  │ 분봉별 추이 바 (390봉)    │ 게이지 + 재학습/워밍업 이벤트 마커  │
  ├────────────────────────┴────────────────────────────────────┤
  │ 하단: mc 변경 이력 테이블 (최근 20건)                          │
  └─────────────────────────────────────────────────────────────┘

핵심 지표:
  - 현재 mc (시간대별)
  - 금일 conf 평균 vs mc (얼마나 여유/부족한지)
  - 신호 통과율 (conf >= mc 비율) — 목표: 15~35%
  - mc 갱신 이력 (언제 얼마나 바뀌었는지)
  - 재학습/워밍업 이벤트 마커

30초 자동 갱신.
"""
import datetime
import logging
import os
import sqlite3

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QFrame, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QProgressBar, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from config.settings import PREDICTIONS_DB, DB_DIR

logger = logging.getLogger("SYSTEM")
MC_HISTORY_DB = os.path.join(DB_DIR, "mc_history.db")

_COL = {
    "bg":      "#0d1117",
    "bg2":     "#161b22",
    "bg3":     "#1c2128",
    "border":  "#30363d",
    "text":    "#e6edf3",
    "muted":   "#8b949e",
    "green":   "#3fb950",
    "yellow":  "#e3b341",
    "orange":  "#d29922",
    "red":     "#f85149",
    "blue":    "#58a6ff",
    "purple":  "#bc8cff",
}

_ZONES = ["GAP_OPEN", "OPEN_VOLATILE", "STABLE_TREND",
          "LUNCH_RECOVERY", "CLOSE_VOLATILE"]
_ZONE_KR = {
    "GAP_OPEN":       "시초가",
    "OPEN_VOLATILE":  "개장",
    "STABLE_TREND":   "안정",
    "LUNCH_RECOVERY": "점심",
    "CLOSE_VOLATILE": "마감",
}


def _card(title: str, widget: QWidget, color: str = _COL["bg2"]) -> QGroupBox:
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

    REFRESH_MS = 30_000   # 30초 갱신

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:%s; color:%s;" % (_COL["bg"], _COL["text"]))
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(self.REFRESH_MS)
        self.refresh()

    # ── 레이아웃 구성 ────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # 상단: 시간대별 mc 카드
        root.addWidget(_card("현재 min_conf (시간대별)", self._build_mc_cards()))

        # 중단: 금일 추이 + 통과율
        mid = QWidget()
        mid_lay = QHBoxLayout(mid)
        mid_lay.setContentsMargins(0, 0, 0, 0)
        mid_lay.setSpacing(6)
        mid_lay.addWidget(_card("금일 conf vs mc 추이", self._build_trend_area()), 3)
        mid_lay.addWidget(_card("신호 통과율 & 갱신 이벤트", self._build_gauge_area()), 2)
        root.addWidget(mid)

        # 하단: mc 변경 이력 테이블
        root.addWidget(_card("mc 변경 이력 (최근 20건)", self._build_history_table()))

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
            mc_lbl.setStyleSheet("font-size:16px; font-weight:bold; color:%s;" % _COL["blue"])
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
        lay.setSpacing(3)

        # 요약 행
        self._lbl_today_avg  = QLabel("오늘 conf 평균: --")
        self._lbl_today_avg.setStyleSheet("font-size:11px; color:%s;" % _COL["text"])
        self._lbl_today_pass = QLabel("통과율: --")
        self._lbl_today_pass.setStyleSheet("font-size:11px; color:%s;" % _COL["green"])

        sumrow = QHBoxLayout()
        sumrow.addWidget(self._lbl_today_avg)
        sumrow.addStretch()
        sumrow.addWidget(self._lbl_today_pass)
        lay.addLayout(sumrow)

        # 분봉별 conf 바 (간략 히트맵)
        self._bar_table = QTableWidget(0, 2)
        self._bar_table.setHorizontalHeaderLabels(["시각", "conf"])
        self._bar_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._bar_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._bar_table.setMaximumHeight(240)
        self._bar_table.setStyleSheet(
            "QTableWidget { background:%s; color:%s; gridline-color:%s; }"
            "QHeaderView::section { background:%s; color:%s; }"
            % (_COL["bg2"], _COL["text"], _COL["border"], _COL["bg3"], _COL["muted"])
        )
        lay.addWidget(self._bar_table)
        return w

    def _build_gauge_area(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # 통과율 게이지
        self._pass_bar = QProgressBar()
        self._pass_bar.setRange(0, 100)
        self._pass_bar.setValue(0)
        self._pass_bar.setTextVisible(True)
        self._pass_bar.setFormat("통과율 %p%")
        self._pass_bar.setStyleSheet(
            "QProgressBar { border:1px solid %s; border-radius:4px; background:%s; "
            "color:%s; text-align:center; height:24px; }"
            "QProgressBar::chunk { background:#58a6ff; border-radius:3px; }"
            % (_COL["border"], _COL["bg3"], _COL["text"])
        )
        lay.addWidget(QLabel("금일 신호 통과율"))
        lay.addWidget(self._pass_bar)

        # 목표 범위 안내
        lbl_target = QLabel("목표: 15~35%  (너무 낮으면 기회 부족 / 너무 높으면 품질 저하)")
        lbl_target.setStyleSheet("font-size:10px; color:%s;" % _COL["muted"])
        lbl_target.setWordWrap(True)
        lay.addWidget(lbl_target)

        lay.addSpacing(8)

        # 갱신 이벤트 로그
        lbl_ev = QLabel("금일 mc 갱신 이벤트")
        lbl_ev.setStyleSheet("font-size:11px; font-weight:bold; color:%s;" % _COL["text"])
        lay.addWidget(lbl_ev)

        self._event_log = QLabel("(갱신 이벤트 없음)")
        self._event_log.setWordWrap(True)
        self._event_log.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._event_log.setStyleSheet(
            "font-size:10px; color:%s; background:%s; "
            "padding:6px; border:1px solid %s; border-radius:3px;"
            % (_COL["muted"], _COL["bg3"], _COL["border"])
        )
        self._event_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addWidget(self._event_log)
        return w

    def _build_history_table(self) -> QWidget:
        t = QTableWidget(0, 7)
        t.setHorizontalHeaderLabels(
            ["시각", "트리거", "시간대", "이전mc", "새mc", "변화", "기반(p65)"]
        )
        t.setMaximumHeight(160)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.setStyleSheet(
            "QTableWidget { background:%s; color:%s; gridline-color:%s; }"
            "QHeaderView::section { background:%s; color:%s; border:none; }"
            % (_COL["bg2"], _COL["text"], _COL["border"], _COL["bg3"], _COL["muted"])
        )
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        self._hist_table = t
        return t

    # ── 데이터 갱신 ─────────────────────────────────────────────
    def refresh(self):
        try:
            self._refresh_mc_cards()
            self._refresh_trend()
            self._refresh_history()
        except Exception as e:
            logger.debug("[DynMCPanel] refresh 오류: %s", e)

    def _refresh_mc_cards(self):
        """현재 _ZONE_PARAMS에서 mc 읽어 카드 업데이트."""
        try:
            from strategy.entry.time_strategy_router import _ZONE_PARAMS
        except Exception:
            return

        # 전날 이력에서 old mc 가져오기 (변화량 표시용)
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
                sign  = "+" if delta > 0 else ""
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
        """금일 분봉별 conf vs mc 추이."""
        today = datetime.date.today().isoformat()
        try:
            from strategy.entry.time_strategy_router import _ZONE_PARAMS
            stable_mc = _ZONE_PARAMS.get("STABLE_TREND", {}).get("min_confidence", 0.57)
        except Exception:
            stable_mc = 0.57

        rows = []
        try:
            conn = sqlite3.connect(PREDICTIONS_DB, timeout=5)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT ts, confidence FROM ensemble_decisions "
                "WHERE substr(ts,1,10)=? ORDER BY ts",
                (today,),
            ).fetchall()
            conn.close()
        except Exception:
            pass

        if not rows:
            return

        confs = [float(r["confidence"]) for r in rows]
        avg_c = sum(confs) / len(confs)
        pass_n = sum(1 for c in confs if c >= stable_mc)
        pass_r = pass_n / len(confs) * 100

        self._lbl_today_avg.setText(
            "오늘 conf 평균: <b>%.3f</b>  mc=%.3f  여유:%+.3f" % (
                avg_c, stable_mc, avg_c - stable_mc
            )
        )
        self._lbl_today_avg.setTextFormat(Qt.RichText)
        self._lbl_today_pass.setText("통과율: <b>%.0f%%</b> (%d/%d봉)" % (
            pass_r, pass_n, len(confs)))
        self._lbl_today_pass.setTextFormat(Qt.RichText)
        color_pass = (_COL["green"] if 15 <= pass_r <= 35
                      else _COL["yellow"] if pass_r < 15
                      else _COL["orange"])
        self._lbl_today_pass.setStyleSheet("font-size:11px; color:%s;" % color_pass)

        self._pass_bar.setValue(int(pass_r))
        chunk_color = (_COL["green"] if 15 <= pass_r <= 35
                       else _COL["orange"] if pass_r > 35
                       else _COL["red"])
        self._pass_bar.setStyleSheet(
            "QProgressBar { border:1px solid %s; border-radius:4px; background:%s; "
            "color:%s; text-align:center; height:24px; }"
            "QProgressBar::chunk { background:%s; border-radius:3px; }"
            % (_COL["border"], _COL["bg3"], _COL["text"], chunk_color)
        )

        # 분봉별 히트맵 (매 5봉 샘플링)
        sample = rows[::5]  # 5봉 간격 샘플링
        self._bar_table.setRowCount(len(sample))
        for i, r in enumerate(sample):
            c = float(r["confidence"])
            ts_str = r["ts"][11:16]

            t_item = QTableWidgetItem(ts_str)
            t_item.setTextAlignment(Qt.AlignCenter)

            # conf 색상: mc 이상=초록, mc-0.05~mc=노랑, 미만=빨강
            if c >= stable_mc:
                bg = QColor("#1a3a2a"); fg = QColor(_COL["green"])
            elif c >= stable_mc - 0.05:
                bg = QColor("#3a3012"); fg = QColor(_COL["yellow"])
            else:
                bg = QColor("#3a1212"); fg = QColor(_COL["red"])

            c_item = QTableWidgetItem("%.3f" % c)
            c_item.setTextAlignment(Qt.AlignCenter)
            c_item.setBackground(bg)
            c_item.setForeground(fg)

            self._bar_table.setItem(i, 0, t_item)
            self._bar_table.setItem(i, 1, c_item)
            self._bar_table.setRowHeight(i, 18)

    def _refresh_history(self):
        """mc 변경 이력 테이블 + 금일 이벤트 로그."""
        hist = self._get_recent_history(20)
        today = datetime.date.today().isoformat()

        today_events = [h for h in hist if h.get("ts", "")[:10] == today]
        if today_events:
            lines = []
            for ev in today_events:
                lines.append("[%s] %s  %s: %.3f→%.3f" % (
                    ev["ts"][11:16], ev["trigger"],
                    ev["zone"], ev["old_mc"], ev["new_mc"],
                ))
            self._event_log.setText("\n".join(lines))
        else:
            self._event_log.setText("(금일 갱신 이벤트 없음)")

        self._hist_table.setRowCount(len(hist))
        for i, row in enumerate(hist):
            delta = row["new_mc"] - row["old_mc"]
            delta_str = "%+.3f" % delta
            color = (_COL["green"] if delta < -0.001
                     else _COL["orange"] if delta > 0.001
                     else _COL["muted"])

            vals = [
                row.get("ts", "")[:16],
                row.get("trigger", ""),
                _ZONE_KR.get(row.get("zone", ""), row.get("zone", "")),
                "%.3f" % row.get("old_mc", 0),
                "%.3f" % row.get("new_mc", 0),
                delta_str,
                "%.3f" % row.get("conf_p65", 0),
            ]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                if j == 5:
                    item.setForeground(QColor(color))
                self._hist_table.setItem(i, j, item)
            self._hist_table.setRowHeight(i, 20)

    def _get_recent_history(self, limit: int) -> list:
        if not os.path.exists(MC_HISTORY_DB):
            return []
        try:
            conn = sqlite3.connect(MC_HISTORY_DB, timeout=5)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM mc_history ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []
