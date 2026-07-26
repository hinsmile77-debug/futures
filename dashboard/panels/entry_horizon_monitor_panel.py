# dashboard/panels/entry_horizon_monitor_panel.py — entry_horizon 경계값 재보정 모니터 패널
"""
EntryHorizonMonitorPanel:
  - 현재 경계값(ENTRY_HORIZON_B1/B2) + 재산출값 카드
  - 1m/3m/5m 버킷 비중 카드 (고착 여부 직관적 확인)
  - 재보정 이력 테이블 (최근 4주)

5분 주기 자동 갱신.
daily_close() 에서 EntryHorizonRecalibrator.run_if_due() 호출 후
threshold_monitor.db:entry_horizon_log 에 기록된 값을 읽어 표시.
자동 반영 없음 — 제안만(model/ensemble_decision.py::select_entry_horizon() 참조).
"""
import logging
import os
import sqlite3
import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

logger = logging.getLogger("SYSTEM")

_BUCKETS = ["1m", "3m", "5m"]
_BUCKET_TARGET = 33.3
_BUCKET_WATCH_LO, _BUCKET_WATCH_HI = 13.0, 54.0
_BUCKET_UPDATE_LO, _BUCKET_UPDATE_HI = 3.0, 74.0

_COL = {
    "bg":        "#0d1117",
    "bg2":       "#161b22",
    "border":    "#30363d",
    "text":      "#e6edf3",
    "muted":     "#8b949e",
    "green":     "#3fb950",
    "yellow":    "#e3b341",
    "orange":    "#d29922",
    "red":       "#f85149",
    "cyan":      "#39d3bb",
}

_ALERT_COLOR = {
    "CLEAR":     _COL["green"],
    "WATCHLIST": _COL["yellow"],
    "UPDATE":    _COL["red"],
}


def _db_path() -> str:
    from config.settings import DB_DIR
    return os.path.join(DB_DIR, "threshold_monitor.db")


def _load_recent(n_rows: int = 12):
    """threshold_monitor.db:entry_horizon_log 에서 최근 N행 로드."""
    path = _db_path()
    if not os.path.exists(path):
        return []
    try:
        with sqlite3.connect(path, timeout=5) as conn:
            rows = conn.execute(
                """SELECT date, current_b1, current_b2, recalc_b1, recalc_b2,
                          b1_delta_pct, b2_delta_pct,
                          bucket_1m_pct, bucket_3m_pct, bucket_5m_pct,
                          alert_level, n_samples
                   FROM entry_horizon_log
                   ORDER BY date DESC
                   LIMIT ?""",
                (n_rows,),
            ).fetchall()
        return rows
    except Exception as exc:
        logger.warning("[EntryHorizonMonitor] DB 로드 실패: %s", exc)
        return []


class EntryHorizonMonitorPanel(QWidget):
    """entry_horizon(select_entry_horizon) 경계값 재보정 모니터 패널 (5분 자동 갱신)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(300_000)  # 5분
        self.refresh()

    # ── 레이아웃 ─────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        hdr = QHBoxLayout()
        hdr.setSpacing(16)
        self._lbl_b1 = self._small_card("경계 B1 (1m/3m)", "3.5", _COL["cyan"])
        self._lbl_b2 = self._small_card("경계 B2 (3m/5m)", "4.0", _COL["cyan"])
        self._lbl_last = self._small_card("마지막 실행", "—", _COL["muted"])
        self._lbl_next = self._small_card("다음 갱신", "—", _COL["muted"])
        self._lbl_alert_global = self._alert_badge("CLEAR")
        hdr.addWidget(self._lbl_b1)
        hdr.addWidget(self._lbl_b2)
        hdr.addWidget(self._lbl_last)
        hdr.addWidget(self._lbl_next)
        hdr.addStretch()
        hdr.addWidget(self._lbl_alert_global)
        root.addLayout(hdr)

        grp = QGroupBox("버킷 비중 (1m / 3m / 5m, 목표 33.3%씩)")
        grp.setStyleSheet(
            f"QGroupBox{{color:{_COL['muted']};border:1px solid {_COL['border']};"
            f"margin-top:6px;font-size:11px;}}"
            f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}"
        )
        glay = QHBoxLayout(grp)
        glay.setSpacing(6)
        self._bucket_cards = {}
        for b in _BUCKETS:
            card = self._bucket_card(b)
            self._bucket_cards[b] = card
            glay.addWidget(card["frame"])
        root.addWidget(grp)

        grp2 = QGroupBox("재보정 이력 (최근 12회, 주 1회 간격)")
        grp2.setStyleSheet(grp.styleSheet())
        glay2 = QVBoxLayout(grp2)
        glay2.setContentsMargins(4, 4, 4, 4)

        self._tbl = QTableWidget()
        self._tbl.setColumnCount(9)
        self._tbl.setHorizontalHeaderLabels([
            "날짜", "B1", "재계산B1", "B2", "재계산B2",
            "1m%", "3m%", "5m%", "경보",
        ])
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl.setSelectionMode(QTableWidget.NoSelection)
        self._tbl.setAlternatingRowColors(True)
        self._tbl.setStyleSheet(
            f"QTableWidget{{background:{_COL['bg2']};color:{_COL['text']};"
            f"gridline-color:{_COL['border']};border:none;font-size:11px;}}"
            f"QHeaderView::section{{background:{_COL['bg']};color:{_COL['muted']};"
            f"border:1px solid {_COL['border']};padding:2px;}}"
            f"QTableWidget::item:alternate{{background:#1c2128;}}"
        )
        glay2.addWidget(self._tbl)

        tip = QLabel(
            "WATCHLIST: 버킷비중 [13%,54%] 밖 또는 |δ|>=15%    "
            "UPDATE: 버킷비중 [3%,74%] 밖 또는 |δ|>=30%    "
            "재산출 권고 시 수동 확인 후 model/ensemble_decision.py의 ENTRY_HORIZON_B1/B2 반영"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color:{_COL['muted']};font-size:10px;")
        glay2.addWidget(tip)
        root.addWidget(grp2)

    # ── 위젯 헬퍼 ────────────────────────────────────────────────
    def _small_card(self, title: str, value: str, color: str) -> QLabel:
        lbl = QLabel(f"<b style='color:{_COL['muted']};font-size:10px;'>{title}</b>"
                     f"<br><span style='color:{color};font-size:15px;font-weight:bold;'>{value}</span>")
        lbl.setStyleSheet(
            f"background:{_COL['bg2']};border:1px solid {_COL['border']};"
            f"border-radius:4px;padding:4px 10px;"
        )
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    def _alert_badge(self, level: str) -> QLabel:
        col = _ALERT_COLOR.get(level, _COL["muted"])
        lbl = QLabel(f"<b style='font-size:13px;'>{level}</b>")
        lbl.setStyleSheet(
            f"color:{col};background:{_COL['bg2']};"
            f"border:2px solid {col};border-radius:6px;padding:4px 14px;"
        )
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    def _bucket_card(self, name: str) -> dict:
        frame = QFrame()
        frame.setStyleSheet(
            f"background:{_COL['bg2']};border:1px solid {_COL['border']};border-radius:4px;"
        )
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(2)

        lbl_name = QLabel(name)
        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setStyleSheet(f"color:{_COL['muted']};font-size:10px;font-weight:bold;")

        lbl_pct = QLabel("—%")
        lbl_pct.setAlignment(Qt.AlignCenter)
        lbl_pct.setStyleSheet(f"color:{_COL['text']};font-size:18px;font-weight:bold;")

        lay.addWidget(lbl_name)
        lay.addWidget(lbl_pct)
        return {"frame": frame, "pct": lbl_pct}

    def _update_next_refresh(self):
        """다음 갱신(금요일 15:40)까지 남은 일수를 헤더 카드에 반영."""
        today = datetime.date.today()
        dow = today.weekday()
        if dow == 4:
            label, color = "오늘 15:40", _COL["green"]
        else:
            days = (4 - dow) % 7
            next_fri = today + datetime.timedelta(days=days)
            label = f"{next_fri.strftime('%m/%d')} ({days}일 후)"
            color = _COL["yellow"] if days <= 2 else _COL["muted"]
        self._lbl_next.setText(
            f"<b style='color:{_COL['muted']};font-size:10px;'>다음 갱신</b>"
            f"<br><span style='color:{color};font-size:12px;'>{label}</span>"
        )

    # ── 갱신 ─────────────────────────────────────────────────────
    def refresh(self):
        self._update_next_refresh()
        rows = _load_recent(n_rows=12)
        if not rows:
            return

        latest = rows[0]
        (date, b1, b2, rb1, rb2, b1d, b2d, p1, p3, p5, alert, n) = latest
        alert = alert or "CLEAR"

        self._lbl_b1.setText(
            f"<b style='color:{_COL['muted']};font-size:10px;'>경계 B1 (1m/3m)</b>"
            f"<br><span style='color:{_COL['cyan']};font-size:15px;font-weight:bold;'>{b1:.2f}</span>"
        )
        self._lbl_b2.setText(
            f"<b style='color:{_COL['muted']};font-size:10px;'>경계 B2 (3m/5m)</b>"
            f"<br><span style='color:{_COL['cyan']};font-size:15px;font-weight:bold;'>{b2:.2f}</span>"
        )
        self._lbl_last.setText(
            f"<b style='color:{_COL['muted']};font-size:10px;'>마지막 실행</b>"
            f"<br><span style='color:{_COL['text']};font-size:12px;'>{date or '—'}</span>"
        )

        col = _ALERT_COLOR.get(alert, _COL["muted"])
        self._lbl_alert_global.setText(f"<b style='font-size:13px;'>{alert}</b>")
        self._lbl_alert_global.setStyleSheet(
            f"color:{col};background:{_COL['bg2']};"
            f"border:2px solid {col};border-radius:6px;padding:4px 14px;"
        )

        for name, pct in zip(_BUCKETS, (p1, p3, p5)):
            card = self._bucket_cards.get(name)
            if not card or pct is None:
                continue
            pcol = (
                _COL["red"] if (pct < _BUCKET_UPDATE_LO or pct > _BUCKET_UPDATE_HI) else
                _COL["orange"] if (pct < _BUCKET_WATCH_LO or pct > _BUCKET_WATCH_HI) else
                _COL["green"]
            )
            card["pct"].setText(f"{pct:.1f}%")
            card["pct"].setStyleSheet(f"color:{pcol};font-size:18px;font-weight:bold;")

        # 이력 테이블
        self._tbl.setRowCount(len(rows))
        for row_idx, r in enumerate(rows):
            (d, cb1, cb2, crb1, crb2, cb1d, cb2d, cp1, cp3, cp5, al, cn) = r
            al = al or "CLEAR"
            al_col = _ALERT_COLOR.get(al, _COL["muted"])
            items = [
                (d or "—", _COL["muted"]),
                (f"{cb1:.2f}" if cb1 is not None else "—", _COL["muted"]),
                (f"{crb1:.2f}" if crb1 is not None else "—", _COL["cyan"]),
                (f"{cb2:.2f}" if cb2 is not None else "—", _COL["muted"]),
                (f"{crb2:.2f}" if crb2 is not None else "—", _COL["cyan"]),
                (f"{cp1:.1f}" if cp1 is not None else "—",
                 _COL["red"] if cp1 is not None and (cp1 < _BUCKET_UPDATE_LO or cp1 > _BUCKET_UPDATE_HI) else _COL["muted"]),
                (f"{cp3:.1f}" if cp3 is not None else "—",
                 _COL["red"] if cp3 is not None and (cp3 < _BUCKET_UPDATE_LO or cp3 > _BUCKET_UPDATE_HI) else _COL["muted"]),
                (f"{cp5:.1f}" if cp5 is not None else "—",
                 _COL["red"] if cp5 is not None and (cp5 < _BUCKET_UPDATE_LO or cp5 > _BUCKET_UPDATE_HI) else _COL["muted"]),
                (al, al_col),
            ]
            for col_idx, (text, color) in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setForeground(QColor(color))
                item.setTextAlignment(Qt.AlignCenter)
                self._tbl.setItem(row_idx, col_idx, item)
