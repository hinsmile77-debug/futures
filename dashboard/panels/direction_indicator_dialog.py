"""
호라이즌 합창판 — 방향 인디케이터

DirectionIndicatorWidget  : 임베드 가능한 QWidget (패널 내 삽입용)
  레이아웃:
    ┌─ _build_lamp() ─────────────────────────────┐
    │  ▼ SHORT  [C] 29.8% 11:34                   │  배경 방향별 변색
    │  ━━━━━━━━━━━━━━━━━━━━━━  conf 바             │
    │  conf 0.298  mc 0.250  +0.048               │
    ├─ _build_chart() ────────────────────────────┤
    │  matplotlib 1분봉 캔들차트 (40봉)            │  방향 삼각형 + 점선
    ├─ _build_hz_strip() ─────────────────────────┤
    │  1m ▼  3m —  5m ▼  10m ▲  15m ▼  30m —    │
    │  합의 ━━━━━━━━━━━━━━░░░░  3/6              │
    └─────────────────────────────────────────────┘

DirectionIndicatorDialog  : AOT 팝업 래퍼 (기존 호환 유지)
"""
import datetime
import sqlite3
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel,
    QProgressBar, QSizePolicy, QVBoxLayout, QWidget,
)

from config.settings import PREDICTIONS_DB, RAW_DATA_DB

_HORIZONS = ["1m", "3m", "5m", "10m", "15m", "30m"]
_N_CANDLES = 40

_BG       = {"up": "#0d2e1a", "dn": "#2e0d0d", "flat": "#1a1a1a"}
_FG       = {"up": "#3fb950", "dn": "#f85149", "flat": "#8b949e"}
_BG_FLASH = {"up": "#1a5c34", "dn": "#5c1a1a", "flat": "#333333"}
_AX_BG    = "#161b22"
_GRID     = "#21262d"
_MUTED    = "#8b949e"
_DARK     = "#0d1117"

_STYLE_BASE = "background:#0d1117; color:#e6edf3;"
_STYLE_HZ   = "QFrame { background:#161b22; border-top:1px solid #30363d; }"
_STYLE_BAR  = (
    "QProgressBar {{ background:#30363d; border-radius:3px; border:none; }}"
    "QProgressBar::chunk {{ background:{color}; border-radius:3px; }}"
)


# ── 핵심 위젯 ─────────────────────────────────────────────────────────────────

class DirectionIndicatorWidget(QWidget):
    """봉차트방향 인디케이터 — 패널 임베드용 QWidget."""

    POLL_MS  = 10_000
    FLASH_MS = 120

    def __init__(self, parent=None):
        super().__init__(parent)
        self._prev_dir: Optional[int] = None
        self._flash_count = 0
        self._flash_key   = "flat"
        self._cur_dir     = 0
        self._cur_fg      = _FG["flat"]

        self._build_ui()

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._refresh)
        self._poll_timer.start(self.POLL_MS)

        self._flash_timer = QTimer(self)
        self._flash_timer.timeout.connect(self._flash_tick)

        self._refresh()

    # ── UI 구성 ──────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._build_lamp())
        root.addWidget(self._build_chart())
        root.addWidget(self._build_hz_strip())

    def _build_lamp(self) -> QFrame:
        self._lamp = QFrame()
        self._lamp.setFixedHeight(130)
        lay = QVBoxLayout(self._lamp)
        lay.setSpacing(5)
        lay.setContentsMargins(16, 12, 16, 10)

        dir_row = QHBoxLayout()
        dir_row.setSpacing(10)

        self._lbl_arrow = QLabel("—")
        self._lbl_arrow.setFont(QFont("Arial", 52, QFont.Bold))
        self._lbl_arrow.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self._lbl_arrow.setFixedWidth(56)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        self._lbl_dir = QLabel("대기")
        self._lbl_dir.setFont(QFont("Arial", 24, QFont.Bold))

        self._lbl_meta = QLabel("")
        self._lbl_meta.setFont(QFont("Arial", 11))
        self._lbl_meta.setStyleSheet("color:#8b949e;")

        info_col.addStretch()
        info_col.addWidget(self._lbl_dir)
        info_col.addWidget(self._lbl_meta)
        info_col.addStretch()

        dir_row.addWidget(self._lbl_arrow)
        dir_row.addLayout(info_col)
        dir_row.addStretch()
        lay.addLayout(dir_row)

        self._conf_bar = QProgressBar()
        self._conf_bar.setFixedHeight(8)
        self._conf_bar.setTextVisible(False)
        self._conf_bar.setRange(0, 1000)
        lay.addWidget(self._conf_bar)

        self._lbl_conf = QLabel("conf —  mc —  ±—")
        self._lbl_conf.setFont(QFont("Consolas", 9))
        self._lbl_conf.setStyleSheet("color:#8b949e;")
        lay.addWidget(self._lbl_conf)

        return self._lamp

    def _build_chart(self) -> QWidget:
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
            from matplotlib.figure import Figure
            self._fig = Figure(facecolor=_DARK, tight_layout=False)
            self._ax  = self._fig.add_axes([0.04, 0.10, 0.84, 0.86])
            self._ax.set_facecolor(_AX_BG)
            for sp in self._ax.spines.values():
                sp.set_edgecolor("#30363d")
            self._canvas = FigureCanvasQTAgg(self._fig)
            self._canvas.setMinimumHeight(180)
            self._canvas.setStyleSheet("background:%s;" % _DARK)
            return self._canvas
        except Exception:
            # matplotlib 미설치 시 빈 프레임으로 대체
            placeholder = QFrame()
            placeholder.setFixedHeight(180)
            placeholder.setStyleSheet(
                "QFrame { background:#161b22; border-top:1px solid #30363d; }"
            )
            lbl = QLabel("봉차트 (matplotlib 필요)")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color:#8b949e; font-size:10px;")
            from PyQt5.QtWidgets import QVBoxLayout as _VL
            _VL(placeholder).addWidget(lbl)
            self._canvas = None
            self._ax     = None
            return placeholder

    def _build_hz_strip(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(_STYLE_HZ)
        lay = QVBoxLayout(frame)
        lay.setSpacing(4)
        lay.setContentsMargins(12, 8, 12, 8)

        icon_row = QHBoxLayout()
        icon_row.setSpacing(0)
        self._hz_icons: Dict[str, QLabel] = {}

        for h in _HORIZONS:
            col = QVBoxLayout()
            col.setSpacing(1)

            lbl_h = QLabel(h)
            lbl_h.setFont(QFont("Arial", 8))
            lbl_h.setStyleSheet("color:#8b949e;")
            lbl_h.setAlignment(Qt.AlignCenter)

            lbl_icon = QLabel("—")
            lbl_icon.setFont(QFont("Arial", 20, QFont.Bold))
            lbl_icon.setAlignment(Qt.AlignCenter)
            lbl_icon.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            col.addWidget(lbl_h)
            col.addWidget(lbl_icon)
            icon_row.addLayout(col)
            self._hz_icons[h] = lbl_icon

        lay.addLayout(icon_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#30363d; margin:2px 0;")
        lay.addWidget(sep)

        consensus_row = QHBoxLayout()
        consensus_row.setSpacing(6)

        lbl_c = QLabel("합의")
        lbl_c.setFont(QFont("Arial", 9))
        lbl_c.setStyleSheet("color:#8b949e;")
        lbl_c.setMinimumWidth(36)
        lbl_c.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        consensus_row.addWidget(lbl_c)

        self._consensus_bar = QProgressBar()
        self._consensus_bar.setFixedHeight(6)
        self._consensus_bar.setTextVisible(False)
        self._consensus_bar.setRange(0, 6)
        self._consensus_bar.setMinimumWidth(40)
        consensus_row.addWidget(self._consensus_bar, 1)

        self._lbl_consensus = QLabel("0/6")
        self._lbl_consensus.setFont(QFont("Consolas", 9))
        self._lbl_consensus.setStyleSheet("color:#8b949e;")
        self._lbl_consensus.setMinimumWidth(38)
        self._lbl_consensus.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        consensus_row.addWidget(self._lbl_consensus)

        lay.addLayout(consensus_row)
        return frame

    # ── 데이터 조회 ──────────────────────────────────────────────

    def _fetch_candles(self, today: str) -> List[dict]:
        try:
            conn = sqlite3.connect(RAW_DATA_DB, timeout=3)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT ts, open, high, low, close, volume "
                "FROM raw_candles "
                "WHERE ts >= ? AND ts < ? ORDER BY ts DESC LIMIT ?",
                (today, today + "Z", _N_CANDLES),
            ).fetchall()
            conn.close()
            return [dict(r) for r in reversed(rows)]
        except Exception:
            return []

    def _fetch_latest_ensemble(self, today: str) -> Optional[dict]:
        try:
            conn = sqlite3.connect(PREDICTIONS_DB, timeout=3)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT ts, direction, confidence, grade, min_conf "
                "FROM ensemble_decisions "
                "WHERE ts >= ? AND ts < ? ORDER BY ts DESC LIMIT 1",
                (today, today + "Z"),
            ).fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception:
            return None

    def _fetch_latest_hz_dirs(self, today: str) -> Dict[str, int]:
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
                ) latest ON p.horizon=latest.horizon AND p.ts=latest.max_ts
                """,
                (today, today + "Z"),
            ).fetchall()
            conn.close()
            for r in rows:
                result[r["horizon"]] = int(r["direction"] or 0)
        except Exception:
            pass
        return result

    # ── 갱신 ─────────────────────────────────────────────────────

    def _refresh(self):
        today    = datetime.date.today().isoformat()
        candles  = self._fetch_candles(today)
        ensemble = self._fetch_latest_ensemble(today)
        hz_dirs  = self._fetch_latest_hz_dirs(today)
        self._apply(ensemble, hz_dirs, candles)

    def push_live(self, decision: dict, ts: str) -> None:
        """파이프라인에서 직접 앙상블 결과 주입 — DB 폴링 지연 없이 즉시 램프 갱신.

        봉차트·hz스트립은 10초 폴링에서 유지된다.
        """
        ens = {
            "ts":         ts,
            "direction":  decision.get("direction", 0),
            "confidence": decision.get("confidence", 0.0),
            "grade":      decision.get("grade", ""),
            "min_conf":   decision.get("min_conf", 0.25),
        }
        self._apply_lamp(ens)

    def _apply(
        self,
        ensemble: Optional[dict],
        hz_dirs:  Dict[str, int],
        candles:  List[dict],
    ):
        if not ensemble:
            self._set_lamp_style("flat")
            self._lbl_arrow.setText("—")
            self._lbl_dir.setText("대기")
            self._lbl_meta.setText("")
            self._lbl_conf.setText("conf —  mc —")
            self._draw_chart(candles, 0, _FG["flat"])
            return

        self._apply_lamp(ensemble)

        # 봉차트
        d  = int(ensemble.get("direction") or 0)
        fg = _FG["up" if d > 0 else ("dn" if d < 0 else "flat")]
        self._draw_chart(candles, d, fg)

        # 호라이즌 스트립
        agree = 0
        for h in _HORIZONS:
            hd = hz_dirs.get(h, 0)
            if hd > 0:
                icon, hfg = "▲", _FG["up"]
            elif hd < 0:
                icon, hfg = "▼", _FG["dn"]
            else:
                icon, hfg = "—", "#8b949e"
            self._hz_icons[h].setText(icon)
            self._hz_icons[h].setStyleSheet(f"color:{hfg};")
            if d != 0 and hd == d:
                agree += 1

        self._consensus_bar.setValue(agree)
        cbg = _FG["up"] if agree >= 5 else ("#e3b341" if agree >= 3 else _FG["dn"])
        self._consensus_bar.setStyleSheet(_STYLE_BAR.format(color=cbg))
        self._lbl_consensus.setText(f"{agree}/6")
        self._lbl_consensus.setStyleSheet(f"color:{cbg};")

    def _apply_lamp(self, ensemble: dict) -> None:
        """램프·바·텍스트만 갱신 (봉차트·hz스트립 불포함). push_live와 _apply 공용."""
        d     = int(ensemble.get("direction") or 0)
        conf  = float(ensemble.get("confidence") or 0.0)
        mc    = float(ensemble.get("min_conf") or 0.57)
        grade = str(ensemble.get("grade") or "")
        ts    = str(ensemble.get("ts") or "")
        ts_hm = ts[11:16] if len(ts) >= 16 else ""

        key   = "up" if d > 0 else ("dn" if d < 0 else "flat")
        arrow = "▲"  if d > 0 else ("▼"  if d < 0 else "—")
        text  = "LONG" if d > 0 else ("SHORT" if d < 0 else "FLAT")

        if self._prev_dir is not None and d != self._prev_dir:
            self._start_flash(key)
        else:
            self._set_lamp_style(key)
        self._prev_dir = d

        fg = _FG[key]
        self._lbl_arrow.setText(arrow)
        self._lbl_arrow.setStyleSheet(f"color:{fg};")
        self._lbl_dir.setText(text)
        self._lbl_dir.setStyleSheet(f"color:{fg};")
        self._lbl_meta.setText(f"[{grade}]  {conf:.1%}  {ts_hm}")

        delta = conf - mc
        self._conf_bar.setValue(int(conf * 1000))
        bar_color = _FG["up"] if delta >= 0 else _FG["dn"]
        self._conf_bar.setStyleSheet(_STYLE_BAR.format(color=bar_color))

        # 2분 이상 갱신 없으면 STALE 경고 표시
        stale_sec = 9999
        if len(ts) >= 19:
            try:
                ts_dt = datetime.datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
                stale_sec = (datetime.datetime.now() - ts_dt).total_seconds()
            except ValueError:
                pass
        if stale_sec > 120:
            stale_min = int(stale_sec // 60)
            self._lbl_conf.setText(
                f"conf {conf:.3f}  mc {mc:.3f}  {delta:+.3f}  ⚠{stale_min}m STALE"
            )
            self._lbl_conf.setStyleSheet("color:#d29922;")  # 황색 경고
        else:
            self._lbl_conf.setText(f"conf {conf:.3f}  mc {mc:.3f}  {delta:+.3f}")
            self._lbl_conf.setStyleSheet("color:#8b949e;")

    # ── 봉차트 렌더링 ─────────────────────────────────────────────

    def _draw_chart(self, candles: List[dict], direction: int, dir_fg: str):
        if self._canvas is None or self._ax is None:
            return
        try:
            from matplotlib.patches import Rectangle
        except ImportError:
            return

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
                color=_MUTED, ha="center", va="center", fontsize=10,
            )
            self._canvas.draw_idle()
            return

        prices_lo = [float(r["low"])  for r in candles]
        prices_hi = [float(r["high"]) for r in candles]
        p_range   = max(max(prices_hi) - min(prices_lo), 1.0)

        for i, row in enumerate(candles):
            o = float(row["open"])
            h = float(row["high"])
            l = float(row["low"])
            c = float(row["close"])
            color = _FG["up"] if c >= o else _FG["dn"]

            ax.plot([i, i], [l, h], color=color, linewidth=0.8,
                    zorder=1, solid_capstyle="round")

            body_h = max(abs(c - o), p_range * 0.003)
            ax.add_patch(Rectangle(
                (i - 0.38, min(o, c)), 0.76, body_h,
                facecolor=color, edgecolor=color, linewidth=0.4, zorder=2,
            ))

        n          = len(candles)
        last_close = float(candles[-1]["close"])
        last_x     = n - 1

        # 현재봉 구분선
        ax.axvline(x=last_x + 0.5, color="#30363d", linewidth=0.8,
                   linestyle="--", alpha=0.6, zorder=0)

        # 방향 삼각형 + 점선
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
                    arrowstyle="-", color=dir_fg, lw=1.3,
                    linestyle="dotted", alpha=0.8,
                ),
                zorder=4,
            )
            ax.plot(
                last_x + 1.6, y_tip,
                marker=marker, markersize=11,
                color=dir_fg, markeredgewidth=0,
                zorder=5, alpha=0.95,
            )
            ax.axhline(
                y=last_close, xmin=0, xmax=1,
                color=dir_fg, linewidth=0.6,
                linestyle=":", alpha=0.35, zorder=0,
            )

        # x축 레이블 (HH:MM, 최대 8개)
        step   = max(1, n // 8)
        xticks = list(range(0, n, step))
        ax.set_xticks(xticks)
        ax.set_xticklabels(
            [candles[i]["ts"][11:16] for i in xticks],
            color=_MUTED, fontsize=7,
        )
        ax.set_xlim(-0.8, n + 2.2)

        y_lo = min(prices_lo) - p_range * 0.04
        y_hi = max(prices_hi) + p_range * 0.08
        ax.set_ylim(y_lo, y_hi)

        self._canvas.draw_idle()

    # ── 램프 스타일 ───────────────────────────────────────────────

    def _set_lamp_style(self, key: str, flash: bool = False):
        bg = _BG_FLASH[key] if flash else _BG[key]
        self._lamp.setStyleSheet(f"QFrame {{ background:{bg}; }}")

    # ── 플래시 효과 ───────────────────────────────────────────────

    def _start_flash(self, key: str):
        self._flash_key   = key
        self._flash_count = 6
        self._flash_timer.start(self.FLASH_MS)
        self._flash_tick()

    def _flash_tick(self):
        if self._flash_count <= 0:
            self._flash_timer.stop()
            self._set_lamp_style(self._flash_key, flash=False)
            return
        self._set_lamp_style(self._flash_key, flash=(self._flash_count % 2 == 0))
        self._flash_count -= 1

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()


# ── 팝업 래퍼 (기존 호환) ──────────────────────────────────────────────────────

class DirectionIndicatorDialog(QDialog):
    """AOT 소형 팝업 — DirectionIndicatorWidget 래퍼."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("방향 인디케이터")
        self.setWindowFlags(
            Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(290)
        self.setStyleSheet(_STYLE_BASE)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self._widget = DirectionIndicatorWidget(self)
        lay.addWidget(self._widget)

    def showEvent(self, event):
        super().showEvent(event)
        self._widget._refresh()
