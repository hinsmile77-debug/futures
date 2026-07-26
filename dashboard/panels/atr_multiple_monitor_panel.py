# dashboard/panels/atr_multiple_monitor_panel.py — ATR배수 임계값 3종 발동률 드리프트 패널
"""
ATRMultipleMonitorPanel:
  - 4개 타깃(CHASE_FILTER×2/COUNTERTREND/REGIME_EXHAUSTION) 발동률 카드
  - 직전 실행 대비 발동률 변화(δ%p) 색상 강조
  - 이력 테이블 (최근 8주)

5분 주기 자동 갱신.
daily_close() 에서 ATRMultipleRecalibrator.run_if_due() 호출 후
atr_multiple_monitor.db 에 기록된 값을 읽어 표시. 자동 반영 없음 — 발동률
드리프트 경보만(재계산 "권장값" 제안 아님 — config/settings.py 주석 참조).
"""
import logging
import os
import sqlite3

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

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


def _db_path() -> str:
    from config.settings import DB_DIR
    return os.path.join(DB_DIR, "atr_multiple_monitor.db")


def _load_recent(n_rows: int = 40):
    path = _db_path()
    if not os.path.exists(path):
        return []
    try:
        with sqlite3.connect(path, timeout=5) as conn:
            rows = conn.execute(
                """SELECT date, target_key, threshold, trigger_rate_pct, n_samples,
                          prev_trigger_rate_pct, delta_pct_pts, alert_level
                   FROM atr_multiple_log
                   ORDER BY date DESC, target_key
                   LIMIT ?""",
                (n_rows,),
            ).fetchall()
        return rows
    except Exception as exc:
        logger.warning("[ATRMultipleMonitor] DB 로드 실패: %s", exc)
        return []


class ATRMultipleMonitorPanel(QWidget):
    """ATR배수 임계값 3종(4타깃) 발동률 드리프트 모니터 패널 (5분 자동 갱신)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(300_000)  # 5분
        self.refresh()

    # ── 레이아웃 ─────────────────────────────────────────────────
    def _build(self):
        from config.settings import ATR_MULTIPLE_RECAL_TARGETS
        self._target_order = list(ATR_MULTIPLE_RECAL_TARGETS.keys())
        self._target_labels = {k: v["label"] for k, v in ATR_MULTIPLE_RECAL_TARGETS.items()}

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        grp = QGroupBox("발동률 현황 (최근 21거래일 기준, 매주 갱신)")
        grp.setStyleSheet(
            f"QGroupBox{{color:{_COL['muted']};border:1px solid {_COL['border']};"
            f"margin-top:6px;font-size:11px;}}"
            f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}"
        )
        glay = QGridLayout(grp)
        glay.setSpacing(6)
        self._cards = {}
        for idx, key in enumerate(self._target_order):
            card = self._target_card(self._target_labels[key])
            self._cards[key] = card
            glay.addWidget(card["frame"], idx // 2, idx % 2)
        root.addWidget(grp)

        grp2 = QGroupBox("재보정 이력 (최근 8주)")
        grp2.setStyleSheet(grp.styleSheet())
        glay2 = QVBoxLayout(grp2)
        glay2.setContentsMargins(4, 4, 4, 4)

        self._tbl = QTableWidget()
        self._tbl.setColumnCount(7)
        self._tbl.setHorizontalHeaderLabels([
            "날짜", "대상", "임계값", "발동률%", "이전%", "δ%p", "경보",
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
            "WATCHLIST: 발동률 직전 대비 |δ|>=8%p    UPDATE: |δ|>=15%p    "
            "\"발동률\"은 지금 임계값이면 최근 데이터에서 얼마나 자주 걸렸을지의 실측치 — "
            "재산출 권고값이 아니라 드리프트 감시용(대상 임계값 자체가 근거 부족한 차용값이라 "
            "percentile 역산 대신 이 방식 채택). 급변 시 CHASE_FILTER/COUNTERTREND/"
            "REGIME_EXHAUSTION_EXT_ATR_THRESHOLD(config/settings.py) 수동 재검토."
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color:{_COL['muted']};font-size:10px;")
        glay2.addWidget(tip)
        root.addWidget(grp2)

    # ── 위젯 헬퍼 ────────────────────────────────────────────────
    def _target_card(self, title: str) -> dict:
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
        lbl_title.setWordWrap(True)
        lbl_title.setStyleSheet(f"color:{_COL['muted']};font-size:10px;font-weight:bold;")

        row = QVBoxLayout()
        lbl_rate = QLabel("—%")
        lbl_rate.setAlignment(Qt.AlignCenter)
        lbl_rate.setStyleSheet(f"color:{_COL['text']};font-size:18px;font-weight:bold;")

        lbl_detail = QLabel("임계값 — / δ —")
        lbl_detail.setAlignment(Qt.AlignCenter)
        lbl_detail.setStyleSheet(f"color:{_COL['muted']};font-size:10px;")

        lbl_alert = QLabel("CLEAR")
        lbl_alert.setAlignment(Qt.AlignCenter)
        lbl_alert.setStyleSheet(f"color:{_COL['green']};font-size:10px;font-weight:bold;")

        lay.addWidget(lbl_title)
        lay.addWidget(lbl_rate)
        lay.addWidget(lbl_detail)
        lay.addWidget(lbl_alert)
        return {"frame": frame, "rate": lbl_rate, "detail": lbl_detail, "alert": lbl_alert}

    # ── 갱신 ─────────────────────────────────────────────────────
    def refresh(self):
        rows = _load_recent(n_rows=4 * 8 * 2)  # 4타깃 × 8주 × 여유
        if not rows:
            return

        latest: dict = {}
        for r in rows:
            date, key = r[0], r[1]
            if key not in latest:
                latest[key] = r

        for key, r in latest.items():
            card = self._cards.get(key)
            if not card:
                continue
            (_, _, threshold, rate, n, prev, delta, alert) = r
            alert = alert or "CLEAR"
            alert_col = _ALERT_COLOR.get(alert, _COL["muted"])
            card["rate"].setText(f"{rate:.1f}%" if rate is not None else "—%")
            card["rate"].setStyleSheet(f"color:{alert_col};font-size:18px;font-weight:bold;")
            delta_txt = f"{delta:+.1f}%p" if delta is not None else "최초 실행"
            card["detail"].setText(f"임계값 {threshold:.2f} / n={n} / δ {delta_txt}")
            card["alert"].setText(alert)
            card["alert"].setStyleSheet(f"color:{alert_col};font-size:10px;font-weight:bold;")

        # 이력 테이블
        self._tbl.setRowCount(len(rows))
        for row_idx, r in enumerate(rows):
            (d, key, threshold, rate, n, prev, delta, alert) = r
            alert = alert or "CLEAR"
            alert_col = _ALERT_COLOR.get(alert, _COL["muted"])
            label = self._target_labels.get(key, key)
            items = [
                (d or "—", _COL["muted"]),
                (label, _COL["text"]),
                (f"{threshold:.2f}" if threshold is not None else "—", _COL["muted"]),
                (f"{rate:.1f}" if rate is not None else "—", _COL["cyan"]),
                (f"{prev:.1f}" if prev is not None else "—", _COL["muted"]),
                ((f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}") if delta is not None else "—",
                 _COL["red"] if abs(delta or 0) >= 8 else _COL["muted"]),
                (alert, alert_col),
            ]
            for col_idx, (text, color) in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setForeground(QColor(color))
                item.setTextAlignment(Qt.AlignCenter)
                self._tbl.setItem(row_idx, col_idx, item)
