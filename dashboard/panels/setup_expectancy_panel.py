# dashboard/panels/setup_expectancy_panel.py — 셋업 유형별 기대값 집계 패널
"""
📊 셋업 기대값 패널

trades.db의 meta_action / hurst_bucket / hour_bucket / grade 컬럼을 기준으로
거래 결과를 집계해 셋업 유형별 기대값(승률, 평균 PnL/pt)을 보여준다.

시간 필터: 전체 / 오늘 / 이번주 / 이번달
"""
import datetime
import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush, QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
    QFrame, QSizePolicy,
)

logger = logging.getLogger("SYSTEM")

_BASE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
_DB_PATH = os.path.join(_BASE_DIR, "data", "trades.db")

# ── 색상 팔레트 ───────────────────────────────────────────────────
C = {
    "bg":     "#0D1117", "bg2": "#161B22", "bg3": "#21262D",
    "border": "#30363D", "text": "#E6EDF3", "text2": "#8B949E",
    "green":  "#3FB950", "red":  "#F85149", "blue":  "#58A6FF",
    "orange": "#D29922", "cyan": "#39D3BB", "yellow": "#E3B341",
    "purple": "#A371F7",
}

_FILTER_LABELS = ["전체", "오늘", "이번주", "이번달"]
_REFRESH_MS = 60_000  # 1분마다 자동 갱신


@contextmanager
def _conn():
    conn = sqlite3.connect(_DB_PATH, timeout=5, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _date_filter(label: str) -> str:
    """label → WHERE 절용 날짜 필터 문자열 반환 (entry_ts 기준)"""
    today = datetime.date.today()
    if label == "오늘":
        return f"DATE(entry_ts) = '{today.isoformat()}'"
    if label == "이번주":
        monday = today - datetime.timedelta(days=today.weekday())
        return f"DATE(entry_ts) >= '{monday.isoformat()}'"
    if label == "이번달":
        first = today.replace(day=1)
        return f"DATE(entry_ts) >= '{first.isoformat()}'"
    return "1=1"  # 전체


def _query_grouped(group_col: str, date_where: str) -> List[Dict[str, Any]]:
    """group_col 기준으로 집계 (청산 완료 거래만)."""
    if not os.path.exists(_DB_PATH):
        return []
    sql = f"""
        SELECT
            COALESCE({group_col}, '(미분류)') AS bucket,
            COUNT(*)                           AS cnt,
            SUM(CASE WHEN pnl_pts > 0 THEN 1 ELSE 0 END) AS wins,
            ROUND(AVG(pnl_pts), 3)             AS avg_pts,
            ROUND(AVG(forward_pnl_pts), 3)     AS avg_fwd_pts,
            ROUND(SUM(pnl_krw), 0)             AS total_krw
        FROM trades
        WHERE exit_price IS NOT NULL
          AND {date_where}
        GROUP BY bucket
        ORDER BY cnt DESC
    """
    try:
        with _conn() as conn:
            rows = conn.execute(sql).fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.debug("[SetupExpectancy] 쿼리 오류 (%s): %s", group_col, e)
        return []


def _mk_btn(text: str, active: bool = False) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(24)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setCheckable(True)
    btn.setChecked(active)
    _apply_btn_style(btn, active)
    return btn


def _apply_btn_style(btn: QPushButton, active: bool):
    bg = C["blue"] if active else C["bg3"]
    btn.setStyleSheet(
        f"QPushButton{{background:{bg};color:{C['text']};border:1px solid {C['border']};"
        f"border-radius:3px;padding:2px 8px;font-size:11px;}}"
        f"QPushButton:checked{{background:{C['blue']};color:#fff;border-color:{C['blue']};}}"
        f"QPushButton:hover{{background:{C['bg2']};}}"
    )


def _make_table(headers: List[str]) -> QTableWidget:
    tbl = QTableWidget(0, len(headers))
    tbl.setHorizontalHeaderLabels(headers)
    tbl.setEditTriggers(QTableWidget.NoEditTriggers)
    tbl.setSelectionBehavior(QTableWidget.SelectRows)
    tbl.setAlternatingRowColors(False)
    tbl.verticalHeader().setVisible(False)
    tbl.horizontalHeader().setStretchLastSection(True)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    tbl.setStyleSheet(
        f"QTableWidget{{background:{C['bg2']};color:{C['text']};gridline-color:{C['border']};"
        f"border:none;font-size:11px;}}"
        f"QTableWidget::item{{padding:3px 6px;}}"
        f"QTableWidget::item:selected{{background:{C['blue']}22;color:{C['text']};}}"
        f"QHeaderView::section{{background:{C['bg3']};color:{C['text2']};"
        f"border:none;border-right:1px solid {C['border']};"
        f"border-bottom:1px solid {C['border']};padding:4px 6px;font-size:11px;}}"
    )
    return tbl


def _pnl_color(val: float) -> str:
    if val > 0:
        return C["green"]
    if val < 0:
        return C["red"]
    return C["text2"]


def _item(text: str, color: str = None, align=Qt.AlignCenter) -> QTableWidgetItem:
    it = QTableWidgetItem(str(text))
    it.setTextAlignment(align | Qt.AlignVCenter)
    if color:
        it.setForeground(QBrush(QColor(color)))
    return it


class _SectionWidget(QFrame):
    """그룹 기준별 집계 테이블 섹션."""

    HEADERS = ["버킷", "거래수", "승률", "평균실행 PnL(pt)", "평균순방향(pt)", "누적(원)"]

    def __init__(self, title: str, group_col: str, parent=None):
        super().__init__(parent)
        self._group_col = group_col
        self.setStyleSheet(
            f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};"
            f"border-radius:4px;}}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(4)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            f"background:transparent;color:{C['cyan']};font-size:12px;font-weight:bold;"
        )
        layout.addWidget(lbl_title)

        self.table = _make_table(self.HEADERS)
        self.table.setMinimumHeight(90)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(self.table)

    def refresh(self, date_where: str):
        rows = _query_grouped(self._group_col, date_where)
        self.table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            cnt   = int(row.get("cnt", 0) or 0)
            wins  = int(row.get("wins", 0) or 0)
            wr    = wins / cnt if cnt else 0.0
            avg_p = float(row.get("avg_pts") or 0.0)
            avg_f = float(row.get("avg_fwd_pts") or 0.0)
            total = float(row.get("total_krw") or 0.0)

            wr_color  = C["green"] if wr >= 0.5 else C["red"]
            self.table.setItem(r_idx, 0, _item(str(row.get("bucket", "")), align=Qt.AlignLeft))
            self.table.setItem(r_idx, 1, _item(str(cnt)))
            self.table.setItem(r_idx, 2, _item(f"{wr:.1%}", wr_color))
            self.table.setItem(r_idx, 3, _item(f"{avg_p:+.3f}", _pnl_color(avg_p)))
            self.table.setItem(r_idx, 4, _item(f"{avg_f:+.3f}", _pnl_color(avg_f)))
            self.table.setItem(r_idx, 5, _item(f"{total:+,.0f}", _pnl_color(total), align=Qt.AlignRight))

        self.table.resizeColumnsToContents()
        self.table.setFixedHeight(
            max(90, self.table.horizontalHeader().height() + len(rows) * 24 + 4)
        )


class SetupExpectancyPanel(QWidget):
    """셋업 유형별 기대값 집계 패널."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter = "전체"
        self._setup_ui()
        self._setup_timer()

    def _setup_ui(self):
        self.setStyleSheet(f"background:{C['bg']};color:{C['text']};")
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # ── 헤더 행 ──────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        lbl = QLabel("📊 셋업 유형별 기대값")
        lbl.setStyleSheet(
            f"background:transparent;color:{C['text']};font-size:13px;font-weight:bold;"
        )
        hdr.addWidget(lbl)
        hdr.addStretch()

        self._filter_btns: Dict[str, QPushButton] = {}
        for lbl_text in _FILTER_LABELS:
            btn = _mk_btn(lbl_text, active=(lbl_text == self._filter))
            btn.clicked.connect(lambda _, t=lbl_text: self._on_filter(t))
            self._filter_btns[lbl_text] = btn
            hdr.addWidget(btn)

        self._btn_refresh = QPushButton("↻ 새로고침")
        self._btn_refresh.setFixedHeight(24)
        self._btn_refresh.setCursor(Qt.PointingHandCursor)
        self._btn_refresh.setStyleSheet(
            f"QPushButton{{background:{C['bg3']};color:{C['cyan']};border:1px solid {C['border']};"
            f"border-radius:3px;padding:2px 8px;font-size:11px;}}"
            f"QPushButton:hover{{background:{C['bg2']};}}"
        )
        self._btn_refresh.clicked.connect(self.refresh)
        hdr.addWidget(self._btn_refresh)
        root.addLayout(hdr)

        # 마지막 갱신 시각
        self._lbl_updated = QLabel("")
        self._lbl_updated.setStyleSheet(
            f"background:transparent;color:{C['text2']};font-size:10px;"
        )
        root.addWidget(self._lbl_updated)

        # ── 스크롤 영역 ──────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea{{border:none;background:{C['bg']};}}"
            f"QScrollBar:vertical{{background:{C['bg2']};width:8px;border-radius:4px;}}"
            f"QScrollBar::handle:vertical{{background:{C['bg3']};border-radius:4px;min-height:20px;}}"
        )
        container = QWidget()
        container.setStyleSheet(f"background:{C['bg']};")
        self._content_layout = QVBoxLayout(container)
        self._content_layout.setContentsMargins(0, 0, 4, 0)
        self._content_layout.setSpacing(8)

        self._sec_action  = _SectionWidget("메타게이트 액션별",  "meta_action")
        self._sec_hurst   = _SectionWidget("허스트 지수 버킷별", "hurst_bucket")
        self._sec_hour    = _SectionWidget("시간대별 (hour)",    "CAST(hour_bucket AS TEXT)")
        self._sec_grade   = _SectionWidget("등급별 (A/B/C)",     "grade")

        for sec in (self._sec_action, self._sec_hurst, self._sec_hour, self._sec_grade):
            self._content_layout.addWidget(sec)

        self._content_layout.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

    def _setup_timer(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(_REFRESH_MS)

    def _on_filter(self, label: str):
        self._filter = label
        for lbl_text, btn in self._filter_btns.items():
            btn.setChecked(lbl_text == label)
            _apply_btn_style(btn, lbl_text == label)
        self.refresh()

    def refresh(self):
        date_where = _date_filter(self._filter)
        for sec in (self._sec_action, self._sec_hurst, self._sec_hour, self._sec_grade):
            try:
                sec.refresh(date_where)
            except Exception as e:
                logger.debug("[SetupExpectancy] 섹션 갱신 실패: %s", e)
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        self._lbl_updated.setText(f"최종 갱신: {now_str}  |  필터: {self._filter}")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
