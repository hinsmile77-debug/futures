# dashboard/panels/scaler_monitor_panel.py — 섹션 9 스케일러 상태 모니터 패널
"""
ScalerMonitorPanel:
  - 실시간: 호라이즌별 스케일러 노후도 / 극단 z 상태
  - 오늘 누적: extreme 피처 Top5 + refresh 이벤트 이력
  - 일별: scaler_daily 최근 20거래일 이력

60초 주기 자동 갱신. scaler_monitor.db 직접 조회.
"""
import json
import logging
import os
import sqlite3
import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QScrollArea, QSizePolicy,
    QTextEdit,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

logger = logging.getLogger("SYSTEM")

_HORIZONS = ["1m", "3m", "5m", "10m", "15m", "30m"]

_COL = {
    "bg":     "#0d1117",
    "bg2":    "#161b22",
    "border": "#30363d",
    "text":   "#e6edf3",
    "muted":  "#8b949e",
    "green":  "#3fb950",
    "yellow": "#e3b341",
    "orange": "#d29922",
    "red":    "#f85149",
    "blue":   "#58a6ff",
    "cyan":   "#39d3bb",
}

# 노후도 임계 (settings 미import — 패널은 독립 실행 가능해야 함)
_AGE_WARN   = 90    # 분: 빨강
_AGE_CAUTION = 30   # 분: 노랑

_TBL_STYLE = (
    "QTableWidget{background:%s;color:%s;"
    "gridline-color:%s;border:none;font-size:11px;}"
    "QHeaderView::section{background:%s;color:%s;"
    "border:1px solid %s;padding:2px;}"
    "QTableWidget::item:alternate{background:#1c2128;}"
) % (
    _COL["bg2"], _COL["text"], _COL["border"],
    _COL["bg"],  _COL["muted"], _COL["border"],
)

_GRP_STYLE = (
    "QGroupBox{color:%s;border:1px solid %s;"
    "margin-top:6px;font-size:11px;}"
    "QGroupBox::title{subcontrol-origin:margin;left:8px;padding:0 4px;}"
) % (_COL["muted"], _COL["border"])


def _db_path():
    from config.settings import SCALER_MONITOR_DB
    return SCALER_MONITOR_DB


def _today():
    return datetime.date.today().isoformat()


def _age_color(age):
    if age is None:
        return _COL["muted"]
    if age > _AGE_WARN:
        return _COL["red"]
    if age > _AGE_CAUTION:
        return _COL["yellow"]
    return _COL["green"]


def _load_realtime(today):
    """오늘의 scaler_events — 호라이즌별 최신 1행."""
    path = _db_path()
    if not os.path.exists(path):
        return {}
    try:
        with sqlite3.connect(path, timeout=5) as c:
            rows = c.execute(
                "SELECT horizon, ts, age_minutes, max_z, max_z_feature, extreme_count "
                "FROM scaler_events WHERE date=? ORDER BY ts DESC",
                (today,),
            ).fetchall()
    except Exception as e:
        logger.debug("[ScalerMonitorPanel] realtime 로드 실패: %s", e)
        return {}
    seen = {}
    for h, ts, age, mz, mzf, ec in rows:
        if h not in seen:
            seen[h] = {"ts": ts, "age": age, "max_z": mz,
                       "max_z_feat": mzf, "extreme_count": ec}
    return seen


def _load_last_refresh(today):
    """오늘 마지막 refresh 이벤트 (ts, type, reason)."""
    path = _db_path()
    if not os.path.exists(path):
        return None
    try:
        with sqlite3.connect(path, timeout=5) as c:
            row = c.execute(
                "SELECT ts, refresh_type, refresh_reason "
                "FROM scaler_events WHERE date=? AND refresh_type IS NOT NULL "
                "ORDER BY ts DESC LIMIT 1",
                (today,),
            ).fetchone()
        return row
    except Exception as e:
        logger.debug("[ScalerMonitorPanel] last_refresh 로드 실패: %s", e)
        return None


def _load_top5_extreme(today):
    """오늘 extreme 피처 Top5 (feature, count, max_abs_z)."""
    path = _db_path()
    if not os.path.exists(path):
        return []
    try:
        with sqlite3.connect(path, timeout=5) as c:
            rows = c.execute(
                "SELECT max_z_feature, COUNT(*) AS cnt, MAX(ABS(max_z)) AS mz "
                "FROM scaler_events "
                "WHERE date=? AND extreme_count > 0 "
                "GROUP BY max_z_feature ORDER BY cnt DESC LIMIT 5",
                (today,),
            ).fetchall()
        return rows
    except Exception as e:
        logger.debug("[ScalerMonitorPanel] top5 로드 실패: %s", e)
        return []


def _load_refresh_events(today):
    """오늘 refresh 이벤트 목록 (ts, type, reason), 중복 ts 제거."""
    path = _db_path()
    if not os.path.exists(path):
        return []
    try:
        with sqlite3.connect(path, timeout=5) as c:
            rows = c.execute(
                "SELECT ts, refresh_type, refresh_reason "
                "FROM scaler_events "
                "WHERE date=? AND refresh_type IS NOT NULL "
                "GROUP BY ts ORDER BY ts",
                (today,),
            ).fetchall()
        return rows
    except Exception as e:
        logger.debug("[ScalerMonitorPanel] refresh_events 로드 실패: %s", e)
        return []


def _load_daily_history(limit=20):
    """scaler_daily 최근 N거래일."""
    path = _db_path()
    if not os.path.exists(path):
        return []
    try:
        with sqlite3.connect(path, timeout=5) as c:
            rows = c.execute(
                "SELECT date, max_age_minutes, total_extreme, top_extreme_feat, "
                "       refresh_count, refresh_types, grade_x_minutes, cb3_triggered "
                "FROM scaler_daily ORDER BY date DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return rows
    except Exception as e:
        logger.debug("[ScalerMonitorPanel] daily_history 로드 실패: %s", e)
        return []


# ─────────────────────────────────────────────────────────────────────────────
class ScalerMonitorPanel(QWidget):
    """스케일러 상태 모니터 패널 (60초 자동 갱신)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(60_000)
        self.refresh()

    # ── 레이아웃 ──────────────────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # ── 헤더 ─────────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title = QLabel("스케일러 상태 모니터")
        title.setStyleSheet(
            "color:%s;font-size:13px;font-weight:bold;" % _COL["text"]
        )
        self._lbl_refresh_ts = QLabel("갱신: —")
        self._lbl_refresh_ts.setStyleSheet(
            "color:%s;font-size:10px;" % _COL["muted"]
        )
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self._lbl_refresh_ts)
        root.addLayout(hdr)

        # ── 중단 2열 ─────────────────────────────────────────────────────────
        mid = QHBoxLayout()
        mid.setSpacing(8)

        # ── 왼쪽: 실시간 호라이즌 테이블 + 마지막 refresh ────────────────────
        left_grp = QGroupBox("실시간 — 호라이즌별")
        left_grp.setStyleSheet(_GRP_STYLE)
        left_lay = QVBoxLayout(left_grp)
        left_lay.setContentsMargins(4, 8, 4, 4)
        left_lay.setSpacing(4)

        self._tbl_rt = QTableWidget()
        self._tbl_rt.setColumnCount(4)
        self._tbl_rt.setHorizontalHeaderLabels(["호라이즌", "노후(분)", "상태", "max_z(피처)"])
        self._tbl_rt.setRowCount(len(_HORIZONS))
        self._tbl_rt.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl_rt.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl_rt.setSelectionMode(QTableWidget.NoSelection)
        self._tbl_rt.setAlternatingRowColors(True)
        self._tbl_rt.setStyleSheet(_TBL_STYLE)
        self._tbl_rt.setMaximumHeight(200)
        for i, h in enumerate(_HORIZONS):
            item = QTableWidgetItem(h)
            item.setForeground(QColor(_COL["muted"]))
            item.setTextAlignment(Qt.AlignCenter)
            self._tbl_rt.setItem(i, 0, item)
        left_lay.addWidget(self._tbl_rt)

        self._lbl_last_refresh = QLabel("마지막 refresh: —")
        self._lbl_last_refresh.setStyleSheet(
            "color:%s;font-size:10px;padding:2px;" % _COL["muted"]
        )
        self._lbl_last_trigger = QLabel("트리거: —")
        self._lbl_last_trigger.setStyleSheet(
            "color:%s;font-size:10px;padding:2px;" % _COL["cyan"]
        )
        left_lay.addWidget(self._lbl_last_refresh)
        left_lay.addWidget(self._lbl_last_trigger)
        left_lay.addStretch()
        mid.addWidget(left_grp, 5)

        # ── 오른쪽: Top5 extreme + refresh 이벤트 ───────────────────────────
        right_vlay = QVBoxLayout()
        right_vlay.setSpacing(6)

        top5_grp = QGroupBox("오늘 누적 extreme 피처 Top5")
        top5_grp.setStyleSheet(_GRP_STYLE)
        top5_lay = QVBoxLayout(top5_grp)
        top5_lay.setContentsMargins(4, 8, 4, 4)

        self._tbl_top5 = QTableWidget()
        self._tbl_top5.setColumnCount(3)
        self._tbl_top5.setHorizontalHeaderLabels(["피처명", "발생 수", "max|z|"])
        self._tbl_top5.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl_top5.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl_top5.setSelectionMode(QTableWidget.NoSelection)
        self._tbl_top5.setAlternatingRowColors(True)
        self._tbl_top5.setStyleSheet(_TBL_STYLE)
        self._tbl_top5.setMaximumHeight(160)
        top5_lay.addWidget(self._tbl_top5)
        right_vlay.addWidget(top5_grp)

        event_grp = QGroupBox("오늘 refresh 이벤트")
        event_grp.setStyleSheet(_GRP_STYLE)
        event_lay = QVBoxLayout(event_grp)
        event_lay.setContentsMargins(4, 8, 4, 4)

        self._txt_events = QTextEdit()
        self._txt_events.setReadOnly(True)
        self._txt_events.setMaximumHeight(90)
        self._txt_events.setStyleSheet(
            "QTextEdit{background:%s;color:%s;border:none;"
            "font-size:11px;font-family:monospace;}" % (_COL["bg2"], _COL["text"])
        )
        event_lay.addWidget(self._txt_events)
        right_vlay.addWidget(event_grp)

        mid_right = QWidget()
        mid_right.setLayout(right_vlay)
        mid.addWidget(mid_right, 6)

        root.addLayout(mid)

        # ── 하단: 일별 이력 ──────────────────────────────────────────────────
        hist_grp = QGroupBox("일별 이력 — 최근 20거래일")
        hist_grp.setStyleSheet(_GRP_STYLE)
        hist_lay = QVBoxLayout(hist_grp)
        hist_lay.setContentsMargins(4, 8, 4, 4)

        self._tbl_hist = QTableWidget()
        self._tbl_hist.setColumnCount(7)
        self._tbl_hist.setHorizontalHeaderLabels([
            "날짜", "최대노후(분)", "extreme건", "폭발피처", "refresh수", "grade_X분", "CB③",
        ])
        self._tbl_hist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl_hist.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl_hist.setSelectionMode(QTableWidget.NoSelection)
        self._tbl_hist.setAlternatingRowColors(True)
        self._tbl_hist.setStyleSheet(_TBL_STYLE)
        hist_lay.addWidget(self._tbl_hist)

        root.addWidget(hist_grp)

    # ── 갱신 ──────────────────────────────────────────────────────────────────
    def refresh(self):
        today = _today()
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        self._lbl_refresh_ts.setText("갱신: " + now_str)

        self._refresh_realtime(today)
        self._refresh_top5(today)
        self._refresh_events(today)
        self._refresh_history()

    def _refresh_realtime(self, today):
        rt = _load_realtime(today)
        last_refresh = _load_last_refresh(today)

        for i, h in enumerate(_HORIZONS):
            data = rt.get(h)
            age    = data["age"] if data else None
            mz     = data["max_z"] if data else None
            mzf    = data["max_z_feat"] if data else ""
            ec     = data["extreme_count"] if data else 0

            age_str  = ("%.0f" % age) if age is not None else "—"
            age_col  = _age_color(age)

            # 상태 표시: ● 색상으로 구분
            dot_col = _COL["orange"] if ec and ec > 0 else age_col
            dot_str  = "●"

            mz_str = ""
            if mz is not None:
                sign = "+" if mz >= 0 else ""
                mz_str = sign + ("%.2f" % mz)
                if mzf:
                    mz_str = mz_str + " (" + mzf + ")"

            cells = [
                (h,       _COL["muted"]),
                (age_str, age_col),
                (dot_str, dot_col),
                (mz_str,  _COL["orange"] if ec and ec > 0 else _COL["muted"]),
            ]
            for j, (txt, col) in enumerate(cells):
                item = self._tbl_rt.item(i, j) or QTableWidgetItem()
                item.setText(txt)
                item.setForeground(QColor(col))
                item.setTextAlignment(Qt.AlignCenter)
                if j == 0:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self._tbl_rt.setItem(i, j, item)

        if last_refresh:
            ts, rt_type, rt_reason = last_refresh
            ts_short = ts[11:16] if ts else "—"
            self._lbl_last_refresh.setText("마지막 refresh: " + ts_short)
            trig_col = _COL["blue"] if rt_type == "D_FORCE" else _COL["cyan"]
            rt_label = rt_type or "—"
            reason_short = (rt_reason[:30] + "...") if rt_reason and len(rt_reason) > 30 else (rt_reason or "")
            self._lbl_last_trigger.setStyleSheet(
                "color:%s;font-size:10px;padding:2px;" % trig_col
            )
            self._lbl_last_trigger.setText("트리거: " + rt_label + "  " + reason_short)
        else:
            self._lbl_last_refresh.setText("마지막 refresh: —")
            self._lbl_last_trigger.setText("트리거: —")

    def _refresh_top5(self, today):
        rows = _load_top5_extreme(today)
        self._tbl_top5.setRowCount(max(len(rows), 1))
        if not rows:
            item = QTableWidgetItem("데이터 없음")
            item.setForeground(QColor(_COL["muted"]))
            self._tbl_top5.setItem(0, 0, item)
            return
        for i, (feat, cnt, mz) in enumerate(rows):
            feat_col = _COL["orange"] if mz and mz > 4.0 else _COL["text"]
            sign = "+" if (mz or 0) >= 0 else ""
            mz_str = sign + ("%.2f" % mz) if mz is not None else "—"
            cells = [
                (feat or "—", feat_col),
                (str(cnt),    _COL["text"]),
                (mz_str,      feat_col),
            ]
            for j, (txt, col) in enumerate(cells):
                item = QTableWidgetItem(txt)
                item.setForeground(QColor(col))
                item.setTextAlignment(Qt.AlignCenter)
                self._tbl_top5.setItem(i, j, item)

    def _refresh_events(self, today):
        events = _load_refresh_events(today)
        if not events:
            self._txt_events.setPlainText("(오늘 refresh 없음)")
            return
        lines = []
        for ts, rt, rr in events:
            ts_short = ts[11:16] if ts else "—"
            rt_label = rt or "—"
            rr_short = (rr[:40] + "...") if rr and len(rr) > 40 else (rr or "")
            lines.append(ts_short + "  " + rt_label + "  " + rr_short)
        self._txt_events.setPlainText("\n".join(lines))

    def _refresh_history(self):
        rows = _load_daily_history(limit=20)
        self._tbl_hist.setRowCount(len(rows))
        for i, row in enumerate(rows):
            date, max_age, total_ext, top_feat, ref_cnt, ref_types, grade_x, cb3 = row

            age_col = _age_color(max_age)
            ext_col = _COL["orange"] if total_ext and total_ext > 10 else _COL["text"]
            cb3_col = _COL["red"] if cb3 else _COL["muted"]
            cb3_str = "Y" if cb3 else "—"

            # refresh_types JSON -> 짧은 표시
            rt_display = ""
            try:
                rt_list = json.loads(ref_types or "[]")
                rt_display = ", ".join(rt_list) if rt_list else "—"
            except Exception:
                rt_display = ref_types or "—"

            cells = [
                (date or "—",                                       _COL["muted"]),
                ("%.0f" % max_age if max_age is not None else "—",  age_col),
                (str(total_ext) if total_ext is not None else "—",  ext_col),
                (top_feat or "—",                                   _COL["text"]),
                (str(ref_cnt) if ref_cnt is not None else "—",      _COL["cyan"]),
                (str(grade_x) if grade_x is not None else "—",      _COL["muted"]),
                (cb3_str,                                            cb3_col),
            ]
            for j, (txt, col) in enumerate(cells):
                item = QTableWidgetItem(txt)
                item.setForeground(QColor(col))
                item.setTextAlignment(Qt.AlignCenter)
                if cb3 and j == 6:
                    item.setBackground(QColor("#3d0000"))
                self._tbl_hist.setItem(i, j, item)
