# dashboard/panels/scaler_monitor_panel.py
"""
Scaler monitor dashboard panel.

- 실시간: 호라이즌별 scaler age / max z 상태
- 상단: 오늘 refresh 이벤트
- 하단 전체폭: 오늘 누적 extreme 피처 Top5
- 맨 아래: scaler_daily 최근 20거래일 이력
"""
import datetime
import json
import logging
import os
import sqlite3

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger("SYSTEM")

_HORIZONS = ["1m", "3m", "5m", "10m", "15m", "30m"]

_COL = {
    "bg": "#0d1117",
    "bg2": "#161b22",
    "border": "#30363d",
    "text": "#e6edf3",
    "muted": "#8b949e",
    "green": "#3fb950",
    "yellow": "#e3b341",
    "orange": "#d29922",
    "red": "#f85149",
    "blue": "#58a6ff",
    "cyan": "#39d3bb",
}

_AGE_WARN = 90
_AGE_CAUTION = 30

_TBL_STYLE = (
    "QTableWidget{background:%s;color:%s;"
    "gridline-color:%s;border:none;font-size:11px;}"
    "QHeaderView::section{background:%s;color:%s;"
    "border:1px solid %s;padding:2px;}"
    "QTableWidget::item:alternate{background:#1c2128;}"
) % (
    _COL["bg2"],
    _COL["text"],
    _COL["border"],
    _COL["bg"],
    _COL["muted"],
    _COL["border"],
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
    """오늘 scaler_events 에서 호라이즌별 최신 1행."""
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
        logger.debug("[ScalerMonitorPanel] realtime load failed: %s", e)
        return {}

    seen = {}
    for horizon, ts, age, mz, mzf, extreme_count in rows:
        if horizon not in seen:
            seen[horizon] = {
                "ts": ts,
                "age": age,
                "max_z": mz,
                "max_z_feat": mzf,
                "extreme_count": extreme_count,
            }
    return seen


def _load_last_refresh(today):
    """오늘 마지막 refresh 이벤트."""
    path = _db_path()
    if not os.path.exists(path):
        return None
    try:
        with sqlite3.connect(path, timeout=5) as c:
            return c.execute(
                "SELECT ts, refresh_type, refresh_reason "
                "FROM scaler_events WHERE date=? AND refresh_type IS NOT NULL "
                "ORDER BY ts DESC LIMIT 1",
                (today,),
            ).fetchone()
    except Exception as e:
        logger.debug("[ScalerMonitorPanel] last_refresh load failed: %s", e)
        return None


def _load_top5_extreme(today):
    """오늘 누적 extreme 피처 Top5.
    반환: (feature, cnt, max_abs_z, ts, horizon, age_minutes,
            max_z, raw_value, pre_value, scaler_mean, scaler_std, refresh_type)
    """
    path = _db_path()
    if not os.path.exists(path):
        return []
    _Q = """
WITH agg AS (
    SELECT max_z_feature,
           COUNT(*)          AS cnt,
           MAX(ABS(max_z))   AS max_abs_z,
           MAX(ts)           AS latest_ts
    FROM scaler_events
    WHERE date = ?
      AND extreme_count > 0
      AND max_z_feature IS NOT NULL
      AND max_z_feature != ''
    GROUP BY max_z_feature
    ORDER BY cnt DESC, max_abs_z DESC
    LIMIT 5
)
SELECT a.max_z_feature, a.cnt, a.max_abs_z,
       e.ts, e.horizon, e.age_minutes, e.max_z,
       e.raw_value, e.pre_value, e.scaler_mean, e.scaler_std, e.refresh_type
FROM agg a
JOIN scaler_events e ON e.max_z_feature = a.max_z_feature
                     AND e.ts = a.latest_ts
                     AND e.date = ?
GROUP BY a.max_z_feature
ORDER BY a.cnt DESC, a.max_abs_z DESC
"""
    try:
        with sqlite3.connect(path, timeout=5) as c:
            return c.execute(_Q, (today, today)).fetchall()
    except Exception as e:
        logger.debug("[ScalerMonitorPanel] top5 load failed: %s", e)
        return []


def _load_refresh_events(today):
    """오늘 refresh 이벤트 목록 (중복 ts 제거)."""
    path = _db_path()
    if not os.path.exists(path):
        return []
    try:
        with sqlite3.connect(path, timeout=5) as c:
            return c.execute(
                "SELECT ts, refresh_type, refresh_reason "
                "FROM scaler_events "
                "WHERE date=? AND refresh_type IS NOT NULL "
                "GROUP BY ts ORDER BY ts DESC",
                (today,),
            ).fetchall()
    except Exception as e:
        logger.debug("[ScalerMonitorPanel] refresh_events load failed: %s", e)
        return []


def _load_daily_history(limit=20):
    """scaler_daily 최근 N거래일."""
    path = _db_path()
    if not os.path.exists(path):
        return []
    try:
        with sqlite3.connect(path, timeout=5) as c:
            return c.execute(
                "SELECT date, max_age_minutes, total_extreme, top_extreme_feat, "
                "refresh_count, refresh_types, grade_x_minutes, cb3_triggered "
                "FROM scaler_daily ORDER BY date DESC LIMIT ?",
                (limit,),
            ).fetchall()
    except Exception as e:
        logger.debug("[ScalerMonitorPanel] daily_history load failed: %s", e)
        return []


class ScalerMonitorPanel(QWidget):
    """스케일러 상태 모니터 패널."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(60_000)
        self.refresh()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        hdr = QHBoxLayout()
        title = QLabel("스케일러 상태 모니터")
        title.setStyleSheet(
            "color:%s;font-size:13px;font-weight:bold;" % _COL["text"]
        )
        self._lbl_refresh_ts = QLabel("갱신: --")
        self._lbl_refresh_ts.setStyleSheet(
            "color:%s;font-size:10px;" % _COL["muted"]
        )
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self._lbl_refresh_ts)
        root.addLayout(hdr)

        top = QHBoxLayout()
        top.setSpacing(8)

        left_grp = QGroupBox("실시간 호라이즌별 상태")
        left_grp.setStyleSheet(_GRP_STYLE)
        left_lay = QVBoxLayout(left_grp)
        left_lay.setContentsMargins(4, 8, 4, 4)
        left_lay.setSpacing(4)

        self._tbl_rt = QTableWidget()
        self._tbl_rt.setColumnCount(4)
        self._tbl_rt.setHorizontalHeaderLabels(
            ["호라이즌", "노후(분)", "상태", "max_z(피처)"]
        )
        self._tbl_rt.setRowCount(len(_HORIZONS))
        self._tbl_rt.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl_rt.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl_rt.setSelectionMode(QTableWidget.NoSelection)
        self._tbl_rt.setAlternatingRowColors(True)
        self._tbl_rt.setStyleSheet(_TBL_STYLE)
        self._tbl_rt.setMaximumHeight(200)
        for i, horizon in enumerate(_HORIZONS):
            item = QTableWidgetItem(horizon)
            item.setForeground(QColor(_COL["muted"]))
            item.setTextAlignment(Qt.AlignCenter)
            self._tbl_rt.setItem(i, 0, item)
        left_lay.addWidget(self._tbl_rt)

        self._lbl_last_refresh = QLabel("마지막 refresh: --")
        self._lbl_last_refresh.setStyleSheet(
            "color:%s;font-size:10px;padding:2px;" % _COL["muted"]
        )
        self._lbl_last_trigger = QLabel("트리거: --")
        self._lbl_last_trigger.setStyleSheet(
            "color:%s;font-size:10px;padding:2px;" % _COL["cyan"]
        )
        left_lay.addWidget(self._lbl_last_refresh)
        left_lay.addWidget(self._lbl_last_trigger)
        left_lay.addStretch()
        top.addWidget(left_grp, 5)

        event_grp = QGroupBox("오늘 refresh 이벤트")
        event_grp.setStyleSheet(_GRP_STYLE)
        event_grp.setToolTip(
            "<b>스케일러 Refresh 트리거 종류</b><br>"
            "<table cellspacing='4'>"
            "<tr><td><b>A_WARMUP</b></td><td>시스템 최초 기동 시 워밍업 (1회)</td></tr>"
            "<tr><td><b>B_OPEN</b></td><td>장 시작 후 30분 이내 — 15분마다 정기 갱신</td></tr>"
            "<tr><td><b>C_PERIODIC</b></td><td>장중 — 60분마다 정기 갱신</td></tr>"
            "<tr><td><b style='color:#58a6ff;'>D_FORCE</b></td>"
            "<td><b style='color:#58a6ff;'>이상값 탐지 시 즉시 강제 갱신</b></td></tr>"
            "</table>"
            "<hr>"
            "<b style='color:#58a6ff;'>D_FORCE 발동 조건 (둘 중 하나)</b><br>"
            "① 동일 피처 |z|&gt;4 연속 <b>3분</b> 유지 → <code>consec=3</code><br>"
            "② 최근 2봉 내 동일 피처 |z|&gt;4 <b>2회</b> 반복 → <code>repeat=2회</code><br>"
            "<br>"
            "<b>발동 후 동작</b><br>"
            "· GBM 모델은 유지 (트리 기반 → 스케일 불변)<br>"
            "· SGD·앙상블 정규화 기준을 최근 500봉으로 재적합<br>"
            "· 이후 <b>5분 쿨다운</b> (중복 발동 방지)<br>"
            "<br>"
            "<b>D_FORCE 반복 발동 원인</b><br>"
            "피처 분포 자체가 역사 평균과 구조적으로 다를 때<br>"
            "(예: opt_pcr_slope_norm 이 하루 종일 극단값 유지)<br>"
            "→ 재적합 후에도 동일 이상값 지속 → 쿨다운 소진 후 재발동"
        )
        event_lay = QVBoxLayout(event_grp)
        event_lay.setContentsMargins(4, 8, 4, 4)

        self._txt_events = QTextEdit()
        self._txt_events.setReadOnly(True)
        self._txt_events.setMaximumHeight(100)
        self._txt_events.setStyleSheet(
            "QTextEdit{background:%s;color:%s;border:none;"
            "font-size:11px;font-family:monospace;}" % (_COL["bg2"], _COL["text"])
        )
        event_lay.addWidget(self._txt_events)
        top.addWidget(event_grp, 6)

        root.addLayout(top)

        top5_grp = QGroupBox("오늘 누적 대표 extreme 피처 Top5")
        top5_grp.setStyleSheet(_GRP_STYLE)
        top5_grp.setToolTip(
            "각 분봉/호라이즌에서 max|z|를 기록한 대표 피처 기준 집계\n"
            "raw→pre: 전처리 전→후 값 (파랑=전처리 영향 있음)\n"
            "μ/σ: 스케일러 기준값/표준편차 (노랑=σ<0.1 협소 분산)\n"
            "최근: 최신 발생 시각·호라이즌 (D=D_FORCE 강제 갱신)"
        )
        top5_lay = QVBoxLayout(top5_grp)
        top5_lay.setContentsMargins(4, 8, 4, 4)

        self._tbl_top5 = QTableWidget()
        self._tbl_top5.setColumnCount(6)
        self._tbl_top5.setHorizontalHeaderLabels(
            ["피처명", "발생수", "max|z|", "입력값 raw→pre", "기준 μ/σ", "최근"]
        )
        _top5_hdr = self._tbl_top5.horizontalHeader()
        _top5_hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        _top5_hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        _top5_hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        _top5_hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        _top5_hdr.setSectionResizeMode(4, QHeaderView.Stretch)
        _top5_hdr.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self._tbl_top5.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl_top5.setSelectionMode(QTableWidget.NoSelection)
        self._tbl_top5.setAlternatingRowColors(True)
        self._tbl_top5.setStyleSheet(_TBL_STYLE)
        self._tbl_top5.setMinimumHeight(160)
        self._tbl_top5.setMaximumHeight(250)
        top5_lay.addWidget(self._tbl_top5)
        root.addWidget(top5_grp)

        hist_grp = QGroupBox("일별 이력 · 최근 20거래일")
        hist_grp.setStyleSheet(_GRP_STYLE)
        hist_lay = QVBoxLayout(hist_grp)
        hist_lay.setContentsMargins(4, 8, 4, 4)

        self._tbl_hist = QTableWidget()
        self._tbl_hist.setColumnCount(7)
        self._tbl_hist.setHorizontalHeaderLabels(
            ["날짜", "최대노후(분)", "extreme건", "폭발피처", "refresh수", "grade_X분", "CB③"]
        )
        self._tbl_hist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl_hist.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl_hist.setSelectionMode(QTableWidget.NoSelection)
        self._tbl_hist.setAlternatingRowColors(True)
        self._tbl_hist.setStyleSheet(_TBL_STYLE)
        hist_lay.addWidget(self._tbl_hist)
        root.addWidget(hist_grp)

    def refresh(self):
        import time as _t, logging as _log
        _t0 = _t.monotonic()
        today = _today()
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        self._lbl_refresh_ts.setText("갱신: " + now_str)
        self._refresh_realtime(today)
        self._refresh_top5(today)
        self._refresh_events(today)
        self._refresh_history()
        _ms = (_t.monotonic() - _t0) * 1000
        if _ms > 200:
            _log.getLogger("SYSTEM").warning("[LiveDBG] ScalerMonitorPanel.refresh slow %.0fms", _ms)

    def _refresh_realtime(self, today):
        rt = _load_realtime(today)
        last_refresh = _load_last_refresh(today)

        for i, horizon in enumerate(_HORIZONS):
            data = rt.get(horizon)
            age = data["age"] if data else None
            mz = data["max_z"] if data else None
            mzf = data["max_z_feat"] if data else ""
            extreme_count = data["extreme_count"] if data else 0

            age_str = ("%.0f" % age) if age is not None else "--"
            age_col = _age_color(age)

            dot_col = _COL["orange"] if extreme_count and extreme_count > 0 else age_col
            dot_str = "●"

            mz_str = ""
            if mz is not None:
                sign = "+" if mz >= 0 else ""
                mz_str = sign + ("%.2f" % mz)
                if mzf:
                    mz_str = mz_str + " (" + mzf + ")"

            cells = [
                (horizon, _COL["muted"]),
                (age_str, age_col),
                (dot_str, dot_col),
                (mz_str, _COL["orange"] if extreme_count and extreme_count > 0 else _COL["muted"]),
            ]
            for j, (txt, col) in enumerate(cells):
                item = QTableWidgetItem(txt)
                item.setForeground(QColor(col))
                item.setTextAlignment(Qt.AlignCenter)
                if j == 0:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self._tbl_rt.setItem(i, j, item)

        if last_refresh:
            ts, refresh_type, refresh_reason = last_refresh
            ts_short = ts[11:16] if ts else "--"
            self._lbl_last_refresh.setText("마지막 refresh: " + ts_short)
            trig_col = _COL["blue"] if refresh_type == "D_FORCE" else _COL["cyan"]
            label = refresh_type or "--"
            reason = refresh_reason or ""
            reason_short = (reason[:30] + "...") if len(reason) > 30 else reason
            self._lbl_last_trigger.setStyleSheet(
                "color:%s;font-size:10px;padding:2px;" % trig_col
            )
            self._lbl_last_trigger.setText("트리거 " + label + "  " + reason_short)
        else:
            self._lbl_last_refresh.setText("마지막 refresh: --")
            self._lbl_last_trigger.setText("트리거: --")

    def _refresh_top5(self, today):
        rows = _load_top5_extreme(today)
        self._tbl_top5.clearContents()
        self._tbl_top5.setRowCount(max(len(rows), 1))
        if not rows:
            item = QTableWidgetItem("데이터 없음")
            item.setForeground(QColor(_COL["muted"]))
            item.setTextAlignment(Qt.AlignCenter)
            self._tbl_top5.setItem(0, 0, item)
            return

        for i, r in enumerate(rows):
            feat, cnt, max_abs_z, ts, horizon, age_min, max_z, raw, pre, sc_mean, sc_std, ref_type = r

            # 피처명 / max|z| 색상
            if max_abs_z is not None and max_abs_z >= 8.0:
                feat_col = _COL["red"]
            elif max_abs_z is not None and max_abs_z >= 4.0:
                feat_col = _COL["orange"]
            else:
                feat_col = _COL["text"]

            # 입력값 raw→pre
            if raw is not None and pre is not None:
                raw_pre_str = "%.3f→%.3f" % (raw, pre)
                raw_pre_col = _COL["cyan"] if abs(raw - pre) > 0.001 else _COL["text"]
            else:
                raw_pre_str = "--"
                raw_pre_col = _COL["muted"]

            # 기준 μ/σ
            if sc_mean is not None and sc_std is not None:
                mean_std_str = "%.3f/%.3f" % (sc_mean, sc_std)
                mean_std_col = _COL["yellow"] if sc_std < 0.1 else _COL["text"]
            else:
                mean_std_str = "--"
                mean_std_col = _COL["muted"]

            # 최근 (시각 호라이즌 [D])
            if ts:
                force_mark = " D" if ref_type == "D_FORCE" else ""
                latest_str = "%s %s%s" % (ts[11:16], horizon or "--", force_mark)
                latest_col = _COL["blue"] if ref_type == "D_FORCE" else _COL["muted"]
            else:
                latest_str = "--"
                latest_col = _COL["muted"]

            mz_str = ("%.2f" % max_abs_z) if max_abs_z is not None else "--"

            cells = [
                (feat or "--",  feat_col),
                (str(cnt),      _COL["text"]),
                (mz_str,        feat_col),
                (raw_pre_str,   raw_pre_col),
                (mean_std_str,  mean_std_col),
                (latest_str,    latest_col),
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
        for ts, refresh_type, refresh_reason in events[:6]:
            ts_short = ts[11:16] if ts else "--"
            label = refresh_type or "--"
            reason = refresh_reason or ""
            reason_short = (reason[:48] + "...") if len(reason) > 48 else reason
            lines.append(ts_short + "  " + label + "  " + reason_short)
        self._txt_events.setPlainText("\n".join(lines))

    def _refresh_history(self):
        rows = _load_daily_history(limit=20)
        self._tbl_hist.setRowCount(len(rows))
        for i, row in enumerate(rows):
            date, max_age, total_ext, top_feat, ref_cnt, ref_types, grade_x, cb3 = row

            age_col = _age_color(max_age)
            ext_col = _COL["orange"] if total_ext and total_ext > 10 else _COL["text"]
            cb3_col = _COL["red"] if cb3 else _COL["muted"]
            cb3_str = "Y" if cb3 else "--"

            try:
                rt_list = json.loads(ref_types or "[]")
                _ = ", ".join(rt_list) if rt_list else "--"
            except Exception:
                _ = ref_types or "--"

            cells = [
                (date or "--", _COL["muted"]),
                ("%.0f" % max_age if max_age is not None else "--", age_col),
                (str(total_ext) if total_ext is not None else "--", ext_col),
                (top_feat or "--", _COL["text"]),
                (str(ref_cnt) if ref_cnt is not None else "--", _COL["cyan"]),
                (str(grade_x) if grade_x is not None else "--", _COL["muted"]),
                (cb3_str, cb3_col),
            ]
            for j, (txt, col) in enumerate(cells):
                item = QTableWidgetItem(txt)
                item.setForeground(QColor(col))
                item.setTextAlignment(Qt.AlignCenter)
                if cb3 and j == 6:
                    item.setBackground(QColor("#3d0000"))
                self._tbl_hist.setItem(i, j, item)
