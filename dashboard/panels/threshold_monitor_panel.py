# dashboard/panels/threshold_monitor_panel.py — Phase A k값 / FLAT 비율 모니터 패널
"""
ThresholdMonitorPanel:
  - 주별 FLAT 비율 이력 테이블 (최근 4주)
  - 호라이즌별 현재 FLAT, drift, 경보 수준 표시
  - WATCHLIST(±6%p), UPDATE(δ±15%) 경보 시 색상 강조
  - k값, FLAT 목표, 재산출 권고값 표시

5분 주기 자동 갱신.
daily_close() 에서 ThresholdRecalibrator.run() 호출 후 DB에 기록된 값을 읽어 표시.
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
from PyQt5.QtGui import QColor, QFont

logger = logging.getLogger("SYSTEM")

_HORIZONS = ["1m", "3m", "5m", "10m", "15m", "30m"]
_FLAT_TARGET = 34.0
_FLAT_ALARM  = 6.0     # ±%p 경보
_DELTA_ALARM = 15.0    # ±% 경보

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
    "blue":      "#58a6ff",
}

_ALERT_COLOR = {
    "CLEAR":     _COL["green"],
    "WATCHLIST": _COL["yellow"],
    "UPDATE":    _COL["red"],
}


def _db_path() -> str:
    from config.settings import DB_DIR
    return os.path.join(DB_DIR, "threshold_monitor.db")


def _load_recent(n_rows: int = 50):
    """threshold_monitor.db 에서 최근 N행 로드."""
    path = _db_path()
    if not os.path.exists(path):
        return []
    try:
        with sqlite3.connect(path, timeout=5) as conn:
            rows = conn.execute(
                """SELECT date, horizon, current_base, recalc_sym,
                          flat_actual, flat_drift, threshold_delta,
                          atr_ratio, alert_level
                   FROM threshold_log
                   ORDER BY date DESC, horizon
                   LIMIT ?""",
                (n_rows,),
            ).fetchall()
        return rows
    except Exception as exc:
        logger.warning("[ThresholdMonitor] DB 로드 실패: %s", exc)
        return []


class ThresholdMonitorPanel(QWidget):
    """Phase A k값 / FLAT 비율 모니터 패널 (5분 자동 갱신)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(300_000)   # 5분
        self.refresh()

    # ── 레이아웃 ─────────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # ── 헤더 행: k값 + 목표 + 마지막 실행 ────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(16)

        self._lbl_k = self._small_card("k값", "0.41", _COL["cyan"])
        self._lbl_target = self._small_card("FLAT 목표", "34%", _COL["muted"])
        self._lbl_last = self._small_card("마지막 실행", "—", _COL["muted"])
        self._lbl_next = self._small_card("다음 갱신", "—", _COL["muted"])
        self._lbl_alert_global = self._alert_badge("CLEAR")

        hdr.addWidget(self._lbl_k)
        hdr.addWidget(self._lbl_target)
        hdr.addWidget(self._lbl_last)
        hdr.addWidget(self._lbl_next)
        hdr.addStretch()
        hdr.addWidget(self._lbl_alert_global)
        root.addLayout(hdr)

        # ── 호라이즌별 최신 상태 카드 ───────────────────────────
        grp = QGroupBox("호라이즌별 FLAT 현황")
        grp.setStyleSheet(
            f"QGroupBox{{color:{_COL['muted']};border:1px solid {_COL['border']};"
            f"margin-top:6px;font-size:11px;}}"
            f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}"
        )
        glay = QHBoxLayout(grp)
        glay.setSpacing(4)
        self._horizon_cards = {}
        for h in _HORIZONS:
            card = self._horizon_card(h)
            self._horizon_cards[h] = card
            glay.addWidget(card["frame"])
        root.addWidget(grp)

        # ── 이력 테이블 ────────────────────────────────────────────
        grp2 = QGroupBox("Phase A 재보정 이력 (최근 4주)")
        grp2.setStyleSheet(grp.styleSheet())
        glay2 = QVBoxLayout(grp2)
        glay2.setContentsMargins(4, 4, 4, 4)

        self._tbl = QTableWidget()
        self._tbl.setColumnCount(8)
        self._tbl.setHorizontalHeaderLabels([
            "날짜", "호라이즌", "현재BASE%", "재산출%",
            "FLAT%", "Drift%p", "δ%", "경보",
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

        # Phase A 경보 설명 라벨
        tip = QLabel(
            "WATCHLIST: |Drift| >= 6%p    UPDATE: |delta| >= 15%    "
            "재산출 권고 시 수동 확인 후 settings.py 반영"
        )
        tip.setStyleSheet(f"color:{_COL['muted']};font-size:10px;")
        glay2.addWidget(tip)
        root.addWidget(grp2)

    # ── 위젯 헬퍼 ────────────────────────────────────────────────────
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

    def _horizon_card(self, horizon: str) -> dict:
        frame = QFrame()
        frame.setStyleSheet(
            f"background:{_COL['bg2']};border:1px solid {_COL['border']};border-radius:4px;"
        )
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(2)

        lbl_h = QLabel(horizon)
        lbl_h.setAlignment(Qt.AlignCenter)
        lbl_h.setStyleSheet(f"color:{_COL['muted']};font-size:10px;font-weight:bold;")

        lbl_flat = QLabel("—")
        lbl_flat.setAlignment(Qt.AlignCenter)
        lbl_flat.setStyleSheet(f"color:{_COL['text']};font-size:14px;font-weight:bold;")

        lbl_drift = QLabel("drift —")
        lbl_drift.setAlignment(Qt.AlignCenter)
        lbl_drift.setStyleSheet(f"color:{_COL['muted']};font-size:10px;")

        lbl_alert = QLabel("CLEAR")
        lbl_alert.setAlignment(Qt.AlignCenter)
        lbl_alert.setStyleSheet(f"color:{_COL['green']};font-size:10px;font-weight:bold;")

        lay.addWidget(lbl_h)
        lay.addWidget(lbl_flat)
        lay.addWidget(lbl_drift)
        lay.addWidget(lbl_alert)

        return {"frame": frame, "flat": lbl_flat, "drift": lbl_drift, "alert": lbl_alert}

    # ── 갱신 ─────────────────────────────────────────────────────────
    def _update_next_refresh(self):
        """다음 갱신(금요일 15:40)까지 남은 일수를 헤더 카드에 반영."""
        today = datetime.date.today()
        dow = today.weekday()   # 0=월 … 4=금 … 6=일
        if dow == 4:
            label = "오늘 15:40"
            color = _COL["green"]
        else:
            days = (4 - dow) % 7
            next_fri = today + datetime.timedelta(days=days)
            label = f"{next_fri.strftime('%m/%d')} ({days}일 후)"
            color = _COL["yellow"] if days <= 2 else _COL["muted"]
        self._lbl_next.setText(
            f"<b style='color:{_COL['muted']};font-size:10px;'>다음 갱신</b>"
            f"<br><span style='color:{color};font-size:12px;'>{label}</span>"
        )

    def refresh(self):
        """DB에서 최신 데이터 로드 후 UI 갱신."""
        self._update_next_refresh()

        rows = _load_recent(n_rows=6 * 4 * 4)   # 6호라이즌 × 4주 × 4주기

        if not rows:
            return

        # 최신 날짜 데이터 추출 (호라이즌별)
        latest: dict = {}
        for r in rows:
            date, h = r[0], r[1]
            if h not in latest:
                latest[h] = r

        # 마지막 실행 날짜
        all_dates = sorted({r[0] for r in rows}, reverse=True)
        if all_dates:
            self._lbl_last.setText(
                f"<b style='color:{_COL['muted']};font-size:10px;'>마지막 실행</b>"
                f"<br><span style='color:{_COL['text']};font-size:12px;'>{all_dates[0]}</span>"
            )

        # 전체 경보 수준 (최악 기준)
        all_alerts = [r[8] for r in rows if r[8]]
        global_alert = "CLEAR"
        if "UPDATE" in all_alerts:
            global_alert = "UPDATE"
        elif "WATCHLIST" in all_alerts:
            global_alert = "WATCHLIST"
        col = _ALERT_COLOR.get(global_alert, _COL["muted"])
        self._lbl_alert_global.setText(f"<b style='font-size:13px;'>{global_alert}</b>")
        self._lbl_alert_global.setStyleSheet(
            f"color:{col};background:{_COL['bg2']};"
            f"border:2px solid {col};border-radius:6px;padding:4px 14px;"
        )

        # 호라이즌별 카드 갱신
        for h, r in latest.items():
            card = self._horizon_cards.get(h)
            if not card:
                continue
            flat_actual  = r[4] or 0.0
            flat_drift   = r[5] or 0.0
            alert        = r[8] or "CLEAR"
            alert_col    = _ALERT_COLOR.get(alert, _COL["muted"])
            # FLAT 색상: 목표±6%p 범위면 green, 벗어나면 alert 색상
            flat_col = (
                _COL["red"]    if abs(flat_drift) >= _FLAT_ALARM * 1.5 else
                _COL["orange"] if abs(flat_drift) >= _FLAT_ALARM else
                _COL["green"]
            )
            card["flat"].setText(f"{flat_actual:.1f}%")
            card["flat"].setStyleSheet(f"color:{flat_col};font-size:14px;font-weight:bold;")
            drift_sign = "+" if flat_drift >= 0 else ""
            card["drift"].setText(f"drift {drift_sign}{flat_drift:.1f}%p")
            card["drift"].setStyleSheet(f"color:{alert_col};font-size:10px;")
            card["alert"].setText(alert)
            card["alert"].setStyleSheet(f"color:{alert_col};font-size:10px;font-weight:bold;")

        # 이력 테이블 갱신
        display_rows = [r for r in rows if r[0] in all_dates[:4 * 7]]   # 최근 4주
        self._tbl.setRowCount(len(display_rows))
        for row_idx, r in enumerate(display_rows):
            date, h, base, recalc, flat_a, drift, delta, atr_r, alert = r
            alert = alert or "CLEAR"
            alert_col = _ALERT_COLOR.get(alert, _COL["muted"])

            items = [
                (date or "—",                        _COL["muted"]),
                (h or "—",                           _COL["text"]),
                (f"{base:.4f}%" if base else "—",    _COL["muted"]),
                (f"{recalc:.4f}%" if recalc else "—",_COL["cyan"]),
                (f"{flat_a:.1f}%" if flat_a else "—",
                 _COL["red"] if abs(drift or 0) >= _FLAT_ALARM else _COL["green"]),
                ((f"+{drift:.1f}" if drift >= 0 else f"{drift:.1f}") + "%p" if drift is not None else "—",
                 _COL["red"] if abs(drift or 0) >= _FLAT_ALARM else _COL["muted"]),
                ((f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}") + "%" if delta is not None else "—",
                 _COL["red"] if abs(delta or 0) >= _DELTA_ALARM else _COL["muted"]),
                (alert,                              alert_col),
            ]
            for col_idx, (text, color) in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setForeground(QColor(color))
                item.setTextAlignment(Qt.AlignCenter)
                self._tbl.setItem(row_idx, col_idx, item)
