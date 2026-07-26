# dashboard/panels/atr_ceiling_monitor_panel.py — ATR 게이트 상/하한 재보정 모니터 패널
"""
ATRCeilingMonitorPanel:
  - 현재/제안 하한(ATR_MAX_ENTRY)·상한(ATR_ADAPTIVE_MAX_CEILING) 카드
  - 마지막 실행일 + 다음 재실행 예상(마지막 실행 + 10일)
  - 재보정 이력 테이블 (최근 8회)

5분 주기 자동 갱신.
daily_close() 에서 ATRCeilingRecalibrator.run_if_due() 호출 후
atr_ceiling_monitor.db 에 기록된 값을 읽어 표시. 자동 반영 없음 — 제안만.
"""
import logging
import os
import sqlite3
import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

logger = logging.getLogger("SYSTEM")

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

_RUN_INTERVAL_DAYS = 10  # learning/atr_ceiling_recalibrator.py:RUN_INTERVAL_CAL_DAYS


def _db_path() -> str:
    from config.settings import DB_DIR
    return os.path.join(DB_DIR, "atr_ceiling_monitor.db")


def _load_recent(n_rows: int = 8):
    """atr_ceiling_monitor.db 에서 최근 N행 로드."""
    path = _db_path()
    if not os.path.exists(path):
        return []
    try:
        with sqlite3.connect(path, timeout=5) as conn:
            rows = conn.execute(
                """SELECT date, current_floor, current_ceiling,
                          suggested_floor, suggested_ceiling,
                          floor_delta_pct, ceiling_delta_pct,
                          n_days, n_bars, alert_level
                   FROM atr_ceiling_log
                   ORDER BY date DESC
                   LIMIT ?""",
                (n_rows,),
            ).fetchall()
        return rows
    except Exception as exc:
        logger.warning("[ATRCeilingMonitor] DB 로드 실패: %s", exc)
        return []


class ATRCeilingMonitorPanel(QWidget):
    """ATR 게이트 상/하한 재보정 제안 모니터 패널 (5분 자동 갱신)."""

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
        self._lbl_last = self._small_card("마지막 실행", "—", _COL["muted"])
        self._lbl_next = self._small_card("다음 재실행", "—", _COL["muted"])
        self._lbl_alert_global = self._alert_badge("CLEAR")
        hdr.addWidget(self._lbl_last)
        hdr.addWidget(self._lbl_next)
        hdr.addStretch()
        hdr.addWidget(self._lbl_alert_global)
        root.addLayout(hdr)

        grp = QGroupBox("ATR 게이트 현재값 vs 제안값")
        grp.setStyleSheet(
            f"QGroupBox{{color:{_COL['muted']};border:1px solid {_COL['border']};"
            f"margin-top:6px;font-size:11px;}}"
            f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}"
        )
        glay = QHBoxLayout(grp)
        glay.setSpacing(8)
        self._floor_card = self._value_card("하한 (ATR_MAX_ENTRY)")
        self._ceiling_card = self._value_card("상한 (ATR_ADAPTIVE_MAX_CEILING)")
        glay.addWidget(self._floor_card["frame"])
        glay.addWidget(self._ceiling_card["frame"])
        root.addWidget(grp)

        grp2 = QGroupBox("재보정 이력 (최근 8회, 약 10일 간격)")
        grp2.setStyleSheet(grp.styleSheet())
        glay2 = QVBoxLayout(grp2)
        glay2.setContentsMargins(4, 4, 4, 4)

        self._tbl = QTableWidget()
        self._tbl.setColumnCount(8)
        self._tbl.setHorizontalHeaderLabels([
            "날짜", "현재하한", "제안하한", "δ하한%",
            "현재상한", "제안상한", "δ상한%", "경보",
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
            "WATCHLIST: |δ| >= 15%    UPDATE: |δ| >= 30%    "
            "제안값은 만기(D-2~D+1) 제외 최근 15거래일 기준 — 수동 확인 후 settings.py 반영"
        )
        tip.setStyleSheet(f"color:{_COL['muted']};font-size:10px;")
        glay2.addWidget(tip)
        root.addWidget(grp2)
        root.addStretch()

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

    def _value_card(self, title: str) -> dict:
        from PyQt5.QtWidgets import QFrame
        frame = QFrame()
        frame.setStyleSheet(
            f"background:{_COL['bg2']};border:1px solid {_COL['border']};border-radius:4px;"
        )
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet(f"color:{_COL['muted']};font-size:10px;font-weight:bold;")

        lbl_cur = QLabel("현재 —pt")
        lbl_cur.setAlignment(Qt.AlignCenter)
        lbl_cur.setStyleSheet(f"color:{_COL['text']};font-size:16px;font-weight:bold;")

        lbl_suggest = QLabel("제안 — (δ—)")
        lbl_suggest.setAlignment(Qt.AlignCenter)
        lbl_suggest.setStyleSheet(f"color:{_COL['muted']};font-size:11px;")

        lay.addWidget(lbl_title)
        lay.addWidget(lbl_cur)
        lay.addWidget(lbl_suggest)
        return {"frame": frame, "cur": lbl_cur, "suggest": lbl_suggest}

    # ── 갱신 ─────────────────────────────────────────────────────
    def refresh(self):
        rows = _load_recent(n_rows=8)
        if not rows:
            return

        latest = rows[0]
        (date, cur_floor, cur_ceiling, sug_floor, sug_ceiling,
         floor_d, ceiling_d, n_days, n_bars, alert) = latest
        alert = alert or "CLEAR"

        self._lbl_last.setText(
            f"<b style='color:{_COL['muted']};font-size:10px;'>마지막 실행</b>"
            f"<br><span style='color:{_COL['text']};font-size:12px;'>{date or '—'}</span>"
        )
        if date:
            try:
                last_dt = datetime.date.fromisoformat(date)
                next_dt = last_dt + datetime.timedelta(days=_RUN_INTERVAL_DAYS)
                remain = (next_dt - datetime.date.today()).days
                label = "오늘 이후 조건 충족" if remain <= 0 else f"{next_dt.strftime('%m/%d')} ({remain}일 후)"
                color = _COL["green"] if remain <= 0 else (_COL["yellow"] if remain <= 2 else _COL["muted"])
            except Exception:
                label, color = "—", _COL["muted"]
            self._lbl_next.setText(
                f"<b style='color:{_COL['muted']};font-size:10px;'>다음 재실행</b>"
                f"<br><span style='color:{color};font-size:12px;'>{label}</span>"
            )

        col = _ALERT_COLOR.get(alert, _COL["muted"])
        self._lbl_alert_global.setText(f"<b style='font-size:13px;'>{alert}</b>")
        self._lbl_alert_global.setStyleSheet(
            f"color:{col};background:{_COL['bg2']};"
            f"border:2px solid {col};border-radius:6px;padding:4px 14px;"
        )

        def _fmt_card(card, cur, sug, delta):
            card["cur"].setText(f"현재 {cur:.1f}pt" if cur is not None else "현재 —pt")
            if sug is not None and delta is not None:
                dcol = _COL["red"] if abs(delta) >= 30 else (_COL["yellow"] if abs(delta) >= 15 else _COL["green"])
                sign = "+" if delta >= 0 else ""
                card["suggest"].setText(f"제안 {sug:.1f}pt ({sign}{delta:.1f}%)")
                card["suggest"].setStyleSheet(f"color:{dcol};font-size:11px;font-weight:bold;")
            else:
                card["suggest"].setText("제안 —")
                card["suggest"].setStyleSheet(f"color:{_COL['muted']};font-size:11px;")

        _fmt_card(self._floor_card, cur_floor, sug_floor, floor_d)
        _fmt_card(self._ceiling_card, cur_ceiling, sug_ceiling, ceiling_d)

        # 이력 테이블
        self._tbl.setRowCount(len(rows))
        for row_idx, r in enumerate(rows):
            (d, cf, cc, sf, sc, fd, cd, nd, nb, al) = r
            al = al or "CLEAR"
            al_col = _ALERT_COLOR.get(al, _COL["muted"])
            items = [
                (d or "—", _COL["muted"]),
                (f"{cf:.1f}" if cf is not None else "—", _COL["muted"]),
                (f"{sf:.1f}" if sf is not None else "—", _COL["cyan"]),
                ((f"+{fd:.1f}" if fd >= 0 else f"{fd:.1f}") if fd is not None else "—",
                 _COL["red"] if abs(fd or 0) >= 15 else _COL["muted"]),
                (f"{cc:.1f}" if cc is not None else "—", _COL["muted"]),
                (f"{sc:.1f}" if sc is not None else "—", _COL["cyan"]),
                ((f"+{cd:.1f}" if cd >= 0 else f"{cd:.1f}") if cd is not None else "—",
                 _COL["red"] if abs(cd or 0) >= 15 else _COL["muted"]),
                (al, al_col),
            ]
            for col_idx, (text, color) in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setForeground(QColor(color))
                item.setTextAlignment(Qt.AlignCenter)
                self._tbl.setItem(row_idx, col_idx, item)
