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
  │  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■□        │  ← 방향예측 레인
  ├────────────────────────────────────────────────────┤
  │  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■□        │  ← 레짐 레인
  ├────────────────────────────────────────────────────┤
  │  09:05  09:15  09:25  09:35  09:45                 │  ← X축 레이블
  ├────────────────────────────────────────────────────┤
  │  1m ▼  3m —  5m ▲  10m ▲  15m ▲  30m ▲           │
  │  합의 ██████████████░░░  5/6                       │
  └────────────────────────────────────────────────────┘

인디케이터 규칙:
  방향예측 레인 — 닫힌 봉(인덱스 0~N-2)에 ensemble_decisions.direction 색상 기록
                  현재봉(N-1)은 빈칸 — 기존 삼각형 마커가 예측을 표시 중
  레짐 레인     — 닫힌 봉에 ensemble_decisions.micro_regime 색상 기록
                  현재봉(N-1)은 빈칸

QTimer 10초 DB 폴링. 방향 변경 시 배너가 즉시 변색.
"""
import datetime
import sqlite3
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QDialog, QFrame, QHBoxLayout, QLabel,
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

# ── X축 인디케이터 색상 ──────────────────────────────────────────────
# 방향예측 레인: direction 값 → 색상
_DIR_COLOR: Dict[int, str] = {
    1:  "#3fb950",   # UP   (녹색)
    -1: "#f85149",   # DOWN (적색)
    0:  "#444c56",   # FLAT (회색)
}
# 레짐 레인: micro_regime 문자열 → 색상 (main_dashboard._REGIME_BAR_COLOR와 동일)
_MR_COLOR: Dict[str, str] = {
    "추세장": "#00c878",   # 녹색
    "횡보장": "#ffee58",   # 노랑
    "급변장": "#ff4444",   # 빨강
    "혼합":   "#8888ff",   # 청보라
    "탈진":   "#ce93d8",   # 보라
}
_LANE_EMPTY = "#1c1c1c"   # 데이터 없는 칸 (어두운 배경)


def _today_range(today: str):
    """오늘 날짜의 ts 범위 반환 — substr() 대신 range로 idx_ts 인덱스 활용."""
    tomorrow = (datetime.date.fromisoformat(today) + datetime.timedelta(days=1)).isoformat()
    return today, tomorrow


class _FetchWorker(QThread):
    """DB 조회를 백그라운드 스레드에서 실행 — Qt 메인스레드 블로킹 방지."""

    # candles, ensemble, hz_dirs, candle_decisions
    done = pyqtSignal(list, object, dict, dict)

    def __init__(self, n_candles: int):
        super().__init__()
        self._n_candles = n_candles

    def run(self):
        today = datetime.date.today().isoformat()
        ts_from, ts_to = _today_range(today)
        candles          = self._fetch_candles(ts_from, ts_to)
        ensemble         = self._fetch_ensemble(ts_from, ts_to)
        hz_dirs          = self._fetch_hz_dirs(ts_from, ts_to)
        candle_decisions = self._fetch_candle_decisions(ts_from, ts_to)
        self.done.emit(candles, ensemble, hz_dirs, candle_decisions)

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

    def _fetch_candle_decisions(self, ts_from: str, ts_to: str) -> Dict[str, dict]:
        """봉별 방향예측·레짐 이력 조회.

        반환: {ts_str: {"direction": int, "micro_regime": str}}
        ensemble_decisions.ts == raw_candles.ts (분 단위 정각) 이므로 직접 매칭.
        """
        result: Dict[str, dict] = {}
        try:
            conn = sqlite3.connect(PREDICTIONS_DB, timeout=3)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT ts, direction, micro_regime "
                "FROM ensemble_decisions "
                "WHERE ts >= ? AND ts < ? ORDER BY ts",
                (ts_from, ts_to),
            ).fetchall()
            conn.close()
            for r in rows:
                result[r["ts"]] = {
                    "direction":    int(r["direction"] or 0),
                    "micro_regime": r["micro_regime"] or "",
                }
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
        self.setStyleSheet("background:%s; color:#e6edf3;" % _DARK)

        self._build_ui()
        self._worker: Optional[_FetchWorker] = None   # 중복 실행 방지
        self._positioned = False  # showEvent 첫 1회에만 위치 적용

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._refresh)
        self._poll_timer.start(self.POLL_MS)

        self._refresh()

    # ── 화면 배치 ────────────────────────────────────────────────

    def _position_on_second_screen(self):
        """제2모니터 중앙에 최적 크기로 배치. 모니터 1대면 주모니터 중앙."""
        app = QApplication.instance()
        if app is None:
            return
        screens = app.screens()
        screen = screens[1] if len(screens) >= 2 else screens[0]
        sg = screen.availableGeometry()

        # 화면의 62% 폭 / 78% 높이를 목표로, 상·하한 클램프
        w = max(700, min(round(sg.width()  * 0.62), 1200))
        h = max(540, min(round(sg.height() * 0.78),  900))

        # 수평 · 수직 중앙
        x = sg.x() + (sg.width()  - w) // 2
        y = sg.y() + (sg.height() - h) // 2
        self.setGeometry(x, y, w, h)

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

        # matplotlib 캔버스 — 캔들 + 방향예측 레인 + 레짐 레인 3단 구성
        #
        # figure 내부 비율 (bottom → top):
        #   0.00 ~ 0.08 : X축 레이블 공간
        #   0.08 ~ 0.14 : 레짐 레인   (micro_regime)
        #   0.14 ~ 0.16 : 레인 간 여백
        #   0.16 ~ 0.22 : 방향예측 레인 (direction)
        #   0.22 ~ 0.24 : 레인 간 여백
        #   0.24 ~ 0.97 : 캔들차트
        #   0.97 ~ 1.00 : 상단 여백
        self._fig    = Figure(facecolor=_DARK, tight_layout=False)
        self._ax     = self._fig.add_axes([0.04, 0.24, 0.86, 0.73])  # 캔들
        self._ax_dir = self._fig.add_axes([0.04, 0.16, 0.86, 0.06])  # 방향예측
        self._ax_reg = self._fig.add_axes([0.04, 0.08, 0.86, 0.06])  # 레짐

        for _a in (self._ax, self._ax_dir, self._ax_reg):
            _a.set_facecolor(_AX_BG)
            for sp in _a.spines.values():
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
        candles:          List[dict],
        ensemble:         Optional[dict],
        hz_dirs:          Dict[str, int],
        candle_decisions: Dict[str, dict],
    ):
        d     = int(ensemble["direction"])         if ensemble else 0
        conf  = float(ensemble["confidence"])      if ensemble else 0.0
        mc    = float(ensemble["min_conf"] or 0.57) if ensemble else 0.57
        grade = str(ensemble["grade"] or "")       if ensemble else ""
        ts    = str(ensemble["ts"] or "")          if ensemble else ""
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

        # ── 봉차트 + 인디케이터 레인 그리기 ──────────────────────
        self._draw_chart(candles, d, fg, candle_decisions)

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

    # ── 봉차트 + 인디케이터 레인 렌더링 ──────────────────────────

    def _draw_chart(
        self,
        candles:          List[dict],
        direction:        int,
        dir_fg:           str,
        candle_decisions: Dict[str, dict],
    ):
        ax      = self._ax
        ax_dir  = self._ax_dir
        ax_reg  = self._ax_reg

        # ── 전체 axes 클리어 + 공통 스타일 ──────────────────────
        for a in (ax, ax_dir, ax_reg):
            a.cla()
            a.set_facecolor(_AX_BG)
            for sp in a.spines.values():
                sp.set_edgecolor("#30363d")

        # ── 데이터 없음 처리 ─────────────────────────────────────
        if not candles:
            ax.text(
                0.5, 0.5, "데이터 없음  (장 시작 후 수집)",
                transform=ax.transAxes,
                color=_MUTED, ha="center", va="center", fontsize=11,
            )
            for a in (ax, ax_dir, ax_reg):
                a.set_xticks([])
                a.set_yticks([])
            self._canvas.draw_idle()
            return

        n          = len(candles)
        last_close = float(candles[-1]["close"])
        last_x     = n - 1
        xlim       = (-0.8, n + 2.2)

        prices_lo = [float(r["low"])  for r in candles]
        prices_hi = [float(r["high"]) for r in candles]
        p_range    = max(max(prices_hi) - min(prices_lo), 1.0)

        # ── 캔들차트 ─────────────────────────────────────────────
        ax.tick_params(
            colors=_MUTED, labelsize=7.5, length=3,
            labelbottom=False,   # X 레이블은 레짐 레인 ax_reg에 표시
        )
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        ax.grid(axis="y", color=_GRID, linewidth=0.5, linestyle="--", alpha=0.7)

        for i, row in enumerate(candles):
            o = float(row["open"])
            h = float(row["high"])
            l = float(row["low"])
            c = float(row["close"])
            up    = c >= o
            color = _FG["up"] if up else _FG["dn"]

            # 꼬리 (위아래)
            ax.plot([i, i], [l, h], color=color, linewidth=0.8,
                    zorder=1, solid_capstyle="round")
            # 몸통
            body_h = max(abs(c - o), p_range * 0.003)
            ax.add_patch(Rectangle(
                (i - 0.38, min(o, c)), 0.76, body_h,
                facecolor=color, edgecolor=color, linewidth=0.4, zorder=2,
            ))

        # 현재봉 구분선
        ax.axvline(x=last_x + 0.5, color="#30363d", linewidth=0.8,
                   linestyle="--", alpha=0.6, zorder=0)

        # 현재봉 방향 삼각형 + 점선 (예측 주석)
        if direction != 0:
            offset = p_range * 0.045
            is_up  = direction > 0
            marker = "^" if is_up else "v"
            y_tip  = last_close + (offset if is_up else -offset)

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
            ax.plot(
                last_x + 1.6, y_tip,
                marker=marker, markersize=13,
                color=dir_fg, markeredgewidth=0,
                zorder=5, alpha=0.95,
            )
            ax.axhline(
                y=last_close, xmin=0, xmax=1,
                color=dir_fg, linewidth=0.6,
                linestyle=":", alpha=0.35, zorder=0,
            )

        ax.set_xlim(*xlim)
        y_lo = min(prices_lo) - p_range * 0.04
        y_hi = max(prices_hi) + p_range * 0.08
        ax.set_ylim(y_lo, y_hi)

        # ── 방향예측 레인 ────────────────────────────────────────
        # 닫힌 봉(0 ~ N-2)에만 색상 칸 표시. 현재봉(N-1)은 빈칸.
        ax_dir.set_xlim(*xlim)
        ax_dir.set_ylim(0, 1)
        ax_dir.set_yticks([])
        ax_dir.set_xticks([])
        ax_dir.tick_params(bottom=False, left=False, right=False, top=False)
        ax_dir.spines["top"].set_visible(False)

        for i in range(n - 1):
            dec   = candle_decisions.get(candles[i]["ts"])
            if dec is None:
                color = _LANE_EMPTY
            else:
                d_val = dec.get("direction")
                color = _DIR_COLOR.get(
                    int(d_val) if d_val is not None else 0,
                    _LANE_EMPTY,
                )
            ax_dir.add_patch(Rectangle(
                (i - 0.5, 0.08), 1.0, 0.84,
                facecolor=color, edgecolor="none", alpha=0.85,
            ))

        # ── 레짐 레인 ────────────────────────────────────────────
        # 닫힌 봉(0 ~ N-2)에만 색상 칸 표시. 현재봉(N-1)은 빈칸.
        # X축 레이블(HH:MM)은 이 레인 하단에 표시.
        ax_reg.set_xlim(*xlim)
        ax_reg.set_ylim(0, 1)
        ax_reg.set_yticks([])
        ax_reg.tick_params(
            colors=_MUTED, labelsize=7, length=2,
            left=False, right=False, top=False,
        )
        ax_reg.spines["top"].set_visible(False)

        step    = max(1, n // 9)
        xticks  = list(range(0, n, step))
        xlabels = [candles[i]["ts"][11:16] for i in xticks]
        ax_reg.set_xticks(xticks)
        ax_reg.set_xticklabels(xlabels, color=_MUTED, fontsize=7)

        for i in range(n - 1):
            dec = candle_decisions.get(candles[i]["ts"])
            if dec is None:
                color = _LANE_EMPTY
            else:
                mr    = dec.get("micro_regime") or ""
                color = _MR_COLOR.get(mr, _LANE_EMPTY)
            ax_reg.add_patch(Rectangle(
                (i - 0.5, 0.08), 1.0, 0.84,
                facecolor=color, edgecolor="none", alpha=0.82,
            ))

        self._canvas.draw_idle()

    # ── 표시/닫힘 이벤트 ──────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        if not self._positioned:
            self._positioned = True
            # singleShot(0): Windows WM의 SW_SHOW 배치가 끝난 뒤
            # 다음 이벤트 루프 틱에서 setGeometry 재적용 — 덮어쓰기 방지
            QTimer.singleShot(0, self._position_on_second_screen)
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
