"""
봉차트 방향 인디케이터 다이얼로그 (배너 오버레이)

레이아웃:
  ┌────────────────────────────────────────────────────┐
  │  ▲  LONG  [A]  68.2%  +0.072  09:38               │  ← 배너 (배경색 변경)
  ├────────────────────────────────────────────────────┤
  │                                                    │
  │   matplotlib 1분봉 캔들차트 (최근 N봉)              │
  │   마지막봉 우측 → 방향 삼각형 + 점선               │
  │                                                    │
  ├────────────────────────────────────────────────────┤
  │  1m ▼  3m —  5m ▲  10m ▲  15m ▲  30m ▲           │
  │  합의 ██████████████░░░  5/6                       │
  └────────────────────────────────────────────────────┘

QTimer 10초 DB 폴링. 방향 변경 시 배너가 즉시 변색.
"""
import datetime
import sqlite3
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel,
    QProgressBar, QSizePolicy, QVBoxLayout, QWidget,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from config.settings import PREDICTIONS_DB, RAW_DATA_DB

_HORIZONS = ["1m", "3m", "5m", "10m", "15m", "30m"]

_BG  = {"up": "#0d2e1a", "dn": "#2e0d0d", "flat": "#181818"}
_FG  = {"up": "#3fb950", "dn": "#f85149",  "flat": "#8b949e"}
_BORDER = {"up": "#1a5c34", "dn": "#5c1a1a", "flat": "#30363d"}
_DARK   = "#0d1117"
_AX_BG  = "#161b22"
_GRID   = "#21262d"
_MUTED  = "#8b949e"

_STYLE_BAR = (
    "QProgressBar {{ background:#30363d; border-radius:3px; border:none; }}"
    "QProgressBar::chunk {{ background:{color}; border-radius:3px; }}"
)


def _today_range(today: str):
    """오늘 날짜의 ts 범위 반환 — substr() 대신 range로 idx_ts 인덱스 활용."""
    tomorrow = (datetime.date.fromisoformat(today) + datetime.timedelta(days=1)).isoformat()
    return today, tomorrow


class _FetchWorker(QThread):
    """DB 조회를 백그라운드 스레드에서 실행 — Qt 메인스레드 블로킹 방지."""

    done = pyqtSignal(list, object, dict)   # candles, ensemble, hz_dirs

    def __init__(self, n_candles: int):
        super().__init__()
        self._n_candles = n_candles

    def run(self):
        today = datetime.date.today().isoformat()
        ts_from, ts_to = _today_range(today)
        candles  = self._fetch_candles(ts_from, ts_to)
        ensemble = self._fetch_ensemble(ts_from, ts_to)
        hz_dirs  = self._fetch_hz_dirs(ts_from, ts_to)
        self.done.emit(candles, ensemble, hz_dirs)

    def _fetch_candles(self, ts_from: str, ts_to: str) -> List[dict]:
        try:
            conn = sqlite3.connect(RAW_DATA_DB, timeout=3)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT ts, open, high, low, close, volume "
                "FROM raw_candles "
                "WHERE ts >= ? AND ts < ? ORDER BY ts DESC LIMIT ?",
                (ts_from, ts_to, self._n_candles),
            ).fetchall()
            conn.close()
            return [dict(r) for r in reversed(rows)]
        except Exception:
            return []

    def _fetch_ensemble(self, ts_from: str, ts_to: str) -> Optional[dict]:
        try:
            conn = sqlite3.connect(PREDICTIONS_DB, timeout=3)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT ts, direction, confidence, grade, min_conf "
                "FROM ensemble_decisions "
                "WHERE ts >= ? AND ts < ? ORDER BY ts DESC LIMIT 1",
                (ts_from, ts_to),
            ).fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception:
            return None

    def _fetch_hz_dirs(self, ts_from: str, ts_to: str) -> Dict[str, int]:
        result: Dict[str, int] = {}
        try:
            conn = sqlite3.connect(PREDICTIONS_DB, timeout=3)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT p.horizon, p.direction
                FROM predictions p
                INNER JOIN (
                    SELECT horizon, MAX(ts) AS max_ts
                    FROM predictions
                    WHERE ts >= ? AND ts < ?
                    GROUP BY horizon
                ) latest
                  ON p.horizon = latest.horizon AND p.ts = latest.max_ts
                """,
                (ts_from, ts_to),
            ).fetchall()
            conn.close()
            for r in rows:
                result[r["horizon"]] = int(r["direction"] or 0)
        except Exception:
            pass
        return result


class CandleChartDialog(QDialog):
    """봉차트 방향 인디케이터 다이얼로그."""

    POLL_MS   = 10_000
    N_CANDLES = 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("봉차트 방향 인디케이터")
        self.setWindowFlags(
            Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint
        )
        self.resize(560, 430)
        self.setStyleSheet("background:%s; color:#e6edf3;" % _DARK)

        self._build_ui()
        self._worker: Optional[_FetchWorker] = None   # 중복 실행 방지

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._refresh)
        self._poll_timer.start(self.POLL_MS)

        self._refresh()

    # ── UI 구성 ─────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # 상단 배너
        self._banner = QLabel("  —  대기")
        self._banner.setFixedHeight(50)
        self._banner.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self._banner.setFont(QFont("Arial", 17, QFont.Bold))
        self._banner.setContentsMargins(14, 0, 14, 0)
        self._banner.setStyleSheet(
            "background:%s; color:%s; border-bottom:2px solid #30363d;"
            % (_BG["flat"], _FG["flat"])
        )
        root.addWidget(self._banner)

        # conf 인디케이터 (배너 ↔ 캔버스 사이)
        conf_frame = QFrame()
        conf_frame.setStyleSheet(
            "QFrame { background:#161b22; border-bottom:1px solid #30363d; }"
        )
        conf_lay = QVBoxLayout(conf_frame)
        conf_lay.setContentsMargins(12, 5, 12, 5)
        conf_lay.setSpacing(3)

        self._conf_bar = QProgressBar()
        self._conf_bar.setFixedHeight(8)
        self._conf_bar.setTextVisible(False)
        self._conf_bar.setRange(0, 1000)
        self._conf_bar.setStyleSheet(_STYLE_BAR.format(color=_MUTED))
        conf_lay.addWidget(self._conf_bar)

        self._lbl_conf_text = QLabel("conf —  mc —  ±—")
        self._lbl_conf_text.setFont(QFont("Consolas", 9))
        self._lbl_conf_text.setStyleSheet("color:%s;" % _MUTED)
        conf_lay.addWidget(self._lbl_conf_text)

        root.addWidget(conf_frame)

        # matplotlib 캔버스
        self._fig = Figure(facecolor=_DARK, tight_layout=False)
        self._ax  = self._fig.add_axes([0.04, 0.08, 0.86, 0.88])
        self._ax.set_facecolor(_AX_BG)
        for sp in self._ax.spines.values():
            sp.set_edgecolor("#30363d")
        self._canvas = FigureCanvasQTAgg(self._fig)
        self._canvas.setMinimumHeight(270)
        root.addWidget(self._canvas)

        # 하단 호라이즌 스트립
        root.addWidget(self._build_hz_strip())

    def _build_hz_strip(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background:#161b22; border-top:1px solid #30363d; }"
        )
        lay = QVBoxLayout(frame)
        lay.setSpacing(3)
        lay.setContentsMargins(12, 5, 12, 6)

        icon_row = QHBoxLayout()
        icon_row.setSpacing(0)
        self._hz_icons: Dict[str, QLabel] = {}

        for h in _HORIZONS:
            col = QVBoxLayout()
            col.setSpacing(0)
            lbl_h = QLabel(h)
            lbl_h.setFont(QFont("Arial", 8))
            lbl_h.setStyleSheet("color:%s;" % _MUTED)
            lbl_h.setAlignment(Qt.AlignCenter)
            lbl_icon = QLabel("—")
            lbl_icon.setFont(QFont("Arial", 16, QFont.Bold))
            lbl_icon.setAlignment(Qt.AlignCenter)
            lbl_icon.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            col.addWidget(lbl_h)
            col.addWidget(lbl_icon)
            icon_row.addLayout(col)
            self._hz_icons[h] = lbl_icon

        lay.addLayout(icon_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#30363d; margin:1px 0;")
        lay.addWidget(sep)

        cns_row = QHBoxLayout()
        cns_row.setSpacing(6)
        lbl_c = QLabel("합의")
        lbl_c.setFont(QFont("Arial", 8))
        lbl_c.setStyleSheet("color:%s;" % _MUTED)
        lbl_c.setFixedWidth(28)
        cns_row.addWidget(lbl_c)
        self._cns_bar = QProgressBar()
        self._cns_bar.setFixedHeight(5)
        self._cns_bar.setTextVisible(False)
        self._cns_bar.setRange(0, 6)
        cns_row.addWidget(self._cns_bar)
        self._lbl_cns = QLabel("0/6")
        self._lbl_cns.setFont(QFont("Consolas", 8))
        self._lbl_cns.setStyleSheet("color:%s;" % _MUTED)
        self._lbl_cns.setFixedWidth(26)
        cns_row.addWidget(self._lbl_cns)
        lay.addLayout(cns_row)

        return frame

    # ── 갱신 (비동기) ─────────────────────────────────────────────

    def _refresh(self):
        # 이전 worker가 아직 실행 중이면 중복 실행 방지
        if self._worker is not None and self._worker.isRunning():
            return
        self._worker = _FetchWorker(self.N_CANDLES)
        self._worker.done.connect(self._apply)
        self._worker.start()

    def _apply(
        self,
        candles:  List[dict],
        ensemble: Optional[dict],
        hz_dirs:  Dict[str, int],
    ):
        d     = int(ensemble["direction"])  if ensemble else 0
        conf  = float(ensemble["confidence"])  if ensemble else 0.0
        mc    = float(ensemble["min_conf"] or 0.57) if ensemble else 0.57
        grade = str(ensemble["grade"] or "")    if ensemble else ""
        ts    = str(ensemble["ts"] or "")       if ensemble else ""
        ts_hm = ts[11:16] if len(ts) >= 16 else "--:--"

        key   = "up" if d > 0 else ("dn" if d < 0 else "flat")
        arrow = "▲" if d > 0 else ("▼" if d < 0 else "—")
        label = "LONG"  if d > 0 else ("SHORT" if d < 0 else "FLAT")
        fg    = _FG[key]
        delta = conf - mc

        # ── 배너 업데이트 ────────────────────────────────────────
        self._banner.setText(
            "  %s  %s   [%s]  %.1f%%  %+.3f  %s"
            % (arrow, label, grade, conf * 100, delta, ts_hm)
        )
        self._banner.setStyleSheet(
            "background:%s; color:%s; font-weight:bold; font-size:17px;"
            " padding-left:12px; border-bottom:2px solid %s;"
            % (_BG[key], fg, _BORDER[key])
        )

        # ── conf 인디케이터 업데이트 ──────────────────────────────
        self._conf_bar.setValue(int(conf * 1000))
        bar_color = _FG["up"] if delta >= 0 else _FG["dn"]
        self._conf_bar.setStyleSheet(_STYLE_BAR.format(color=bar_color))
        self._lbl_conf_text.setText(
            "conf %.3f  mc %.3f  %+.3f" % (conf, mc, delta)
        )

        # ── 봉차트 그리기 ─────────────────────────────────────────
        self._draw_chart(candles, d, fg)

        # ── 호라이즌 스트립 ──────────────────────────────────────
        agree = 0
        for h in _HORIZONS:
            hd = hz_dirs.get(h, 0)
            if hd > 0:
                icon, hfg = "▲", _FG["up"]
            elif hd < 0:
                icon, hfg = "▼", _FG["dn"]
            else:
                icon, hfg = "—", _MUTED
            self._hz_icons[h].setText(icon)
            self._hz_icons[h].setStyleSheet("color:%s;" % hfg)
            if d != 0 and hd == d:
                agree += 1

        self._cns_bar.setValue(agree)
        cbg = _FG["up"] if agree >= 5 else (_FG["dn"] if agree <= 2 else "#e3b341")
        self._cns_bar.setStyleSheet(_STYLE_BAR.format(color=cbg))
        self._lbl_cns.setText("%d/6" % agree)
        self._lbl_cns.setStyleSheet("color:%s;" % cbg)

    # ── 봉차트 렌더링 ────────────────────────────────────────────

    def _draw_chart(self, candles: List[dict], direction: int, dir_fg: str):
        ax = self._ax
        ax.cla()
        ax.set_facecolor(_AX_BG)
        ax.tick_params(colors=_MUTED, labelsize=7.5, length=3)
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        for sp in ax.spines.values():
            sp.set_edgecolor("#30363d")
        ax.grid(axis="y", color=_GRID, linewidth=0.5, linestyle="--", alpha=0.7)

        if not candles:
            ax.text(
                0.5, 0.5, "데이터 없음  (장 시작 후 수집)",
                transform=ax.transAxes,
                color=_MUTED, ha="center", va="center", fontsize=11,
            )
            self._canvas.draw_idle()
            return

        prices_lo = [float(r["low"])  for r in candles]
        prices_hi = [float(r["high"]) for r in candles]
        p_range    = max(max(prices_hi) - min(prices_lo), 1.0)

        for i, row in enumerate(candles):
            o = float(row["open"])
            h = float(row["high"])
            l = float(row["low"])
            c = float(row["close"])
            up    = c >= o
            color = _FG["up"] if up else _FG["dn"]

            # 꼬리 (위아래)
            ax.plot([i, i], [l, h], color=color, linewidth=0.8, zorder=1, solid_capstyle="round")

            # 몸통
            body_h = max(abs(c - o), p_range * 0.003)
            rect = Rectangle(
                (i - 0.38, min(o, c)), 0.76, body_h,
                facecolor=color, edgecolor=color, linewidth=0.4, zorder=2,
            )
            ax.add_patch(rect)

        n = len(candles)
        last_close = float(candles[-1]["close"])
        last_x     = n - 1

        # 현재봉 구분선
        ax.axvline(x=last_x + 0.5, color="#30363d", linewidth=0.8,
                   linestyle="--", alpha=0.6, zorder=0)

        # 방향 삼각형 + 점선 (예측 주석)
        if direction != 0:
            offset = p_range * 0.045
            is_up  = direction > 0
            marker = "^" if is_up else "v"
            y_tip  = last_close + (offset if is_up else -offset)

            # 점선 연결
            ax.annotate(
                "",
                xy=(last_x + 1.6, y_tip),
                xytext=(last_x + 0.6, last_close),
                arrowprops=dict(
                    arrowstyle="-",
                    color=dir_fg,
                    lw=1.3,
                    linestyle="dotted",
                    alpha=0.8,
                ),
                zorder=4,
            )
            # 삼각형 마커
            ax.plot(
                last_x + 1.6, y_tip,
                marker=marker, markersize=13,
                color=dir_fg, markeredgewidth=0,
                zorder=5, alpha=0.95,
            )
            # 현재 Close 수평선 (점선)
            ax.axhline(
                y=last_close, xmin=0, xmax=1,
                color=dir_fg, linewidth=0.6,
                linestyle=":", alpha=0.35, zorder=0,
            )

        # x축 레이블 (HH:MM, 8~10개)
        step    = max(1, n // 9)
        xticks  = list(range(0, n, step))
        xlabels = [candles[i]["ts"][11:16] for i in xticks]
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels, color=_MUTED, fontsize=7)
        ax.set_xlim(-0.8, n + 2.2)

        # y축: 최소 틱 간격 보정
        y_lo = min(prices_lo) - p_range * 0.04
        y_hi = max(prices_hi) + p_range * 0.08
        ax.set_ylim(y_lo, y_hi)

        self._canvas.draw_idle()

    # ── 표시/닫힘 이벤트 ──────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        # __init__에서 이미 _refresh() 1회 실행 → worker 실행 중이면 skip
        self._refresh()

    def closeEvent(self, event):
        self._poll_timer.stop()
        if self._worker is not None:
            try:
                self._worker.done.disconnect()
            except RuntimeError:
                pass
            self._worker.wait(300)
        super().closeEvent(event)
