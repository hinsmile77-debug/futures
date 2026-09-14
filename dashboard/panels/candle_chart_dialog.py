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
from dashboard.stack_state import (
    compute_states, STATE_KO, STATE_COLOR, STATE_NA_KO, STATE_NA_COLOR, STATE_W,
)

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

# ── 포지션 스냅샷 ────────────────────────────────────────────
# 포지션은 **DB에 없다** — main.py → DashboardAPI.update_position 으로만 흐른다.
# 배너는 별도 프로세스가 아니라 같은 프로세스의 다이얼로그이므로,
# 그 흐름을 여기에 한 번 떨궈두고 읽는다(단방향·읽기 전용).
#
# 🔴 계측 4원칙 ② — **미측정 ≠ 0건**.
#   스냅샷이 한 번도 안 왔으면 「무포지션」이 아니라 「포지션 미연결」이다.
#   왔다가 끊기면 「갱신 끊김」이다. 둘 다 FLAT 으로 뭉개지 않는다.
_POS_STALE_SEC = 60.0
_POS_SNAPSHOT: Dict[str, object] = {"data": None, "mono": 0.0}


def publish_position(pos_data: Optional[dict]) -> None:
    """대시보드가 받은 포지션을 배너가 읽을 수 있게 떨군다. 부작용 없음."""
    import time as _t
    _POS_SNAPSHOT["data"] = dict(pos_data) if pos_data else None
    _POS_SNAPSHOT["mono"] = _t.monotonic()


def read_position() -> tuple:
    """반환: (상태문자열, pos_data|None)
      "none"  — 스냅샷 한 번도 없음 (미연결)
      "stale" — 왔지만 60초 넘게 갱신 없음
      "live"  — 유효
    """
    import time as _t
    if not _POS_SNAPSHOT["mono"]:
        return "none", None
    age = _t.monotonic() - float(_POS_SNAPSHOT["mono"])
    return ("stale" if age > _POS_STALE_SEC else "live"), _POS_SNAPSHOT["data"]


def _today_range(today: str):
    """오늘 날짜의 ts 범위 반환 — substr() 대신 range로 idx_ts 인덱스 활용."""
    tomorrow = (datetime.date.fromisoformat(today) + datetime.timedelta(days=1)).isoformat()
    return today, tomorrow


class _FetchWorker(QThread):
    """DB 조회를 백그라운드 스레드에서 실행 — Qt 메인스레드 블로킹 방지."""

    # candles, ensemble, hz_dirs, candle_decisions, state
    done = pyqtSignal(list, object, dict, dict, object)

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
        state            = self._fetch_state(ts_from, ts_to)
        self.done.emit(candles, ensemble, hz_dirs, candle_decisions, state)

    def _fetch_state(self, ts_from: str, ts_to: str) -> Optional[dict]:
        """현재 봉의 4상태 — **당일 전체**를 읽어야 한다.

        당일 중앙값 디바이어스와 50% 분위 문턱이 하루 전체를 쓰기 때문에,
        차트에 보이는 최근 N봉만으로는 계산할 수 없다(§3-2).
        반환: {"state": STATE|None, "ts": 마지막 봉 ts, "n": 사용 봉수}
        """
        try:
            uri = "file:" + RAW_DATA_DB.replace("\\", "/") + "?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=3)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT ts, buy_vol, sell_vol, volume, oi FROM raw_candles "
                "WHERE ts >= ? AND ts < ? ORDER BY ts",
                (ts_from, ts_to),
            ).fetchall()
            conn.close()
            bars = [dict(r) for r in rows]
            if not bars:
                return None
            res = compute_states(bars)
            last_ts = bars[-1]["ts"]
            return {
                "state": res["state_map"].get(last_ts),
                "ts":    last_ts,
                "close": None,
                "n":     len([b for b in bars if (b.get("oi") or 0) > 0]),
            }
        except Exception:
            return None

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

        # ── 좌측 중단 — 상태 / 현재가 / 포지션 (배너 ↔ 캔버스 사이) ──
        # 시안 의도: **보유 여부에 따라 답하는 질문이 바뀐다.**
        #   무포지션 → 「들어가도 되나」  → 상태 배지가 답한다
        #   보유 중  → 「손절이 어디고 얼마 벌고 있나」 → 손절·미실현이 답한다
        # 같은 자리, 같은 높이. 눈이 옮겨 다닐 필요가 없다.
        mid_frame = QFrame()
        mid_frame.setStyleSheet(
            "QFrame { background:#161b22; border-bottom:1px solid #30363d; }"
        )
        mid_lay = QVBoxLayout(mid_frame)
        mid_lay.setContentsMargins(12, 5, 12, 4)
        mid_lay.setSpacing(4)

        row = QHBoxLayout()
        row.setSpacing(10)

        # ① 4상태 배지 — 「상방 쌓기」 등
        self._lbl_state = QLabel("상태 —")
        self._lbl_state.setFont(QFont("Arial", 10, QFont.Bold))
        self._lbl_state.setAlignment(Qt.AlignCenter)
        self._lbl_state.setMinimumWidth(88)
        self._style_state_badge(STATE_NA_COLOR, "상태 —")
        self._lbl_state.setToolTip(
            "봉별 4상태 — 공격자 방향 × ΔOI 부호 (30봉 창, 당일 중앙값 디바이어스)\n"
            "  상방 쌓기   : 매수가 때리며 미결제 증가 (신규 롱)\n"
            "  기계적 매수 : 매수가 때리며 미결제 감소 (숏커버)\n"
            "  하방 쌓기   : 매도가 때리며 미결제 증가 (신규 숏)\n"
            "  기계적 매도 : 매도가 때리며 미결제 감소 (롱커버)\n"
            "  문턱 미달   : 활성 문턱(|공격자| · |ΔOI| 각각 당일 50%분위) 미달 — 「중립」이 아니다\n"
            "  상태 —      : 30봉 워밍업 미달 또는 원천 미수집\n\n"
            "⭐ 검증된 진술은 하나다 — 「기계적 매수 구간에서 롱을 잡지 마라」\n"
            "   (OOS −13.5bp, 95%CI [−18.6,−9.0], P=0.000, 4/4 fold)\n"
            "   나머지 3상태는 워크포워드를 통과하지 못했다 — 표시만 한다."
        )
        row.addWidget(self._lbl_state, 0, Qt.AlignVCenter)

        # ② 현재가 — 화면에서 가장 큼
        self._lbl_price = QLabel("————")
        self._lbl_price.setFont(QFont("Consolas", 21, QFont.Bold))
        self._lbl_price.setStyleSheet("color:#e6edf3;")
        row.addWidget(self._lbl_price, 0, Qt.AlignVCenter)

        self._lbl_price_src = QLabel("")
        self._lbl_price_src.setFont(QFont("Arial", 8))
        self._lbl_price_src.setStyleSheet("color:%s;" % _MUTED)
        row.addWidget(self._lbl_price_src, 0, Qt.AlignBottom)

        # ③ 포지션 — 무포지션 / 보유 중에 따라 내용이 바뀐다
        self._lbl_pos = QLabel("포지션 미연결")
        self._lbl_pos.setFont(QFont("Consolas", 11, QFont.Bold))
        self._lbl_pos.setStyleSheet("color:%s;" % _MUTED)
        row.addWidget(self._lbl_pos, 0, Qt.AlignVCenter)

        # 🔴 손절과 손익을 **한 라벨에 섞지 않는다**.
        #   손익 부호로 전체를 칠하면 「손절 1044.00」이 초록으로 찍혀
        #   안심 신호처럼 읽힌다 — 손절은 언제나 손절 색이다.
        self._lbl_stop = QLabel("")
        self._lbl_stop.setFont(QFont("Consolas", 11, QFont.Bold))
        self._lbl_stop.setStyleSheet("color:%s;" % _FG["dn"])
        row.addWidget(self._lbl_stop, 0, Qt.AlignVCenter)

        self._lbl_pnl = QLabel("")
        self._lbl_pnl.setFont(QFont("Consolas", 13, QFont.Bold))
        self._lbl_pnl.setStyleSheet("color:%s;" % _MUTED)
        row.addWidget(self._lbl_pnl, 0, Qt.AlignVCenter)

        self._lbl_pos_q = QLabel("")
        self._lbl_pos_q.setFont(QFont("Arial", 8))
        self._lbl_pos_q.setStyleSheet("color:#586069;")
        row.addWidget(self._lbl_pos_q, 0, Qt.AlignVCenter)

        row.addStretch(1)

        self._lbl_span = QLabel("최근 %d봉" % self.N_CANDLES)
        self._lbl_span.setFont(QFont("Arial", 9))
        self._lbl_span.setStyleSheet("color:%s;" % _MUTED)
        row.addWidget(self._lbl_span, 0, Qt.AlignVCenter)

        mid_lay.addLayout(row)

        # conf 인디케이터 — 값은 배너에 있고, 여기엔 막대와 mc 만 남긴다
        conf_row = QHBoxLayout()
        conf_row.setSpacing(8)
        self._conf_bar = QProgressBar()
        self._conf_bar.setFixedHeight(5)
        self._conf_bar.setTextVisible(False)
        self._conf_bar.setRange(0, 1000)
        self._conf_bar.setStyleSheet(_STYLE_BAR.format(color=_MUTED))
        conf_row.addWidget(self._conf_bar, 1)

        self._lbl_conf_text = QLabel("conf —  mc —  ±—")
        self._lbl_conf_text.setFont(QFont("Consolas", 8))
        self._lbl_conf_text.setStyleSheet("color:%s;" % _MUTED)
        conf_row.addWidget(self._lbl_conf_text, 0)
        mid_lay.addLayout(conf_row)

        root.addWidget(mid_frame)

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

    # ── 좌측 중단 ────────────────────────────────────────────────

    def _style_state_badge(self, color: str, text: str):
        self._lbl_state.setText(text)
        self._lbl_state.setStyleSheet(
            "background:%s; color:#0d1117; border-radius:3px;"
            " padding:2px 8px; font-weight:bold;" % color
        )

    def _update_mid_row(self, candles: List[dict], state: Optional[dict]):
        """상태 배지 · 현재가 · 포지션 — 시안 좌측 중단.

        🔴 계측 4원칙 ②·④ — 없는 값을 그럴듯하게 채우지 않는다.
          포지션 스냅샷이 없으면 「무포지션」이 아니라 「포지션 미연결」,
          상태가 안 붙었으면 「중립」이 아니라 「문턱 미달」이다.
        """
        # ① 상태 배지
        if state is None:
            self._style_state_badge(STATE_NA_COLOR, "상태 —")
        elif state.get("n", 0) <= STATE_W:
            self._style_state_badge(STATE_NA_COLOR, "워밍업 %d/%d"
                                    % (state.get("n", 0), STATE_W + 1))
        else:
            st = state.get("state")
            if st:
                self._style_state_badge(STATE_COLOR[st], STATE_KO[st])
            else:
                self._style_state_badge(STATE_NA_COLOR, STATE_NA_KO)

        # ② 포지션 — 현재가 출처도 여기서 갈린다
        pos_state, pos = read_position()
        bar_close = None
        if candles:
            try:
                bar_close = float(candles[-1]["close"])
            except (TypeError, ValueError, KeyError):
                bar_close = None

        status = ""
        if pos_state == "live" and pos:
            status = str(pos.get("status", "") or "").strip().upper()

        live_px = None
        if pos_state == "live" and pos:
            try:
                _c = float(pos.get("current") or 0.0)
                live_px = _c if _c > 0 else None
            except (TypeError, ValueError):
                live_px = None

        px = live_px if live_px is not None else bar_close
        if px is None:
            self._lbl_price.setText("————")
            self._lbl_price.setStyleSheet("color:%s;" % _MUTED)
            self._lbl_price_src.setText("미수집")
        else:
            self._lbl_price.setText("%.2f" % px)
            self._lbl_price.setStyleSheet("color:#e6edf3;")
            self._lbl_price_src.setText("실시간" if live_px is not None else "종가")

        self._lbl_stop.setText("")
        self._lbl_pnl.setText("")

        if pos_state == "none":
            # 한 번도 안 왔다 — 「무포지션」과 다르다
            self._lbl_pos.setText("포지션 미연결")
            self._lbl_pos.setStyleSheet("color:%s;" % _MUTED)
            self._lbl_pos.setToolTip(
                "포지션은 DB에 없다 — main.py 의 실시간 흐름에서만 온다.\n"
                "이 배너를 대시보드 없이 단독으로 띄웠거나, 아직 첫 갱신 전이다.\n"
                "「무포지션」이라는 뜻이 **아니다**."
            )
            self._lbl_pos_q.setText("")
            return
        if pos_state == "stale":
            self._lbl_pos.setText("포지션 갱신 끊김")
            self._lbl_pos.setStyleSheet("color:#D29922;")
            self._lbl_pos.setToolTip(
                "마지막 포지션 갱신이 %d초를 넘었다 — 지금 상태를 모른다.\n"
                "표시된 값은 마지막으로 받은 값이다." % int(_POS_STALE_SEC)
            )
            self._lbl_pos_q.setText("")
            return

        if status in ("LONG", "SHORT"):
            mult = 1 if status == "LONG" else -1
            side = "L" if status == "LONG" else "S"
            try:
                entry = float(pos.get("entry") or 0.0)
            except (TypeError, ValueError):
                entry = 0.0
            try:
                stop = float(pos.get("stop") or 0.0)
            except (TypeError, ValueError):
                stop = 0.0
            try:
                qty = int(float(pos.get("qty") or 0))
            except (TypeError, ValueError):
                qty = 0
            cur = px if px is not None else entry
            pnl = (cur - entry) * mult if entry > 0 and cur is not None else None

            self._lbl_pos.setText(
                "%s  진입 %s" % ("%s×%d" % (side, qty) if qty else side,
                                 "%.2f" % entry if entry > 0 else "——")
            )
            self._lbl_pos.setStyleSheet("color:#e6edf3;")
            self._lbl_pos.setToolTip(
                "보유 중 — 이 줄이 답하는 질문은 「손절이 어디고 얼마 벌고 있나」다.\n"
                "손절은 현재 트레일링 스톱(PositionTracker.stop_price)이다.\n"
                "손익은 미실현 포인트 — 수수료 전이다."
            )
            # 손절 — 부호와 무관하게 항상 손절 색
            self._lbl_stop.setText("손절 %s" % ("%.2f" % stop if stop > 0 else "——"))
            self._lbl_stop.setToolTip(
                "현재 트레일링 스톱. 진입 시 고정값이 아니라 **움직인다**."
            )
            # 손익 — 여기만 부호로 칠한다
            if pnl is None:
                self._lbl_pnl.setText("손익 ——")
                self._lbl_pnl.setStyleSheet("color:%s;" % _MUTED)
            else:
                self._lbl_pnl.setText("%+.2fp" % pnl)
                self._lbl_pnl.setStyleSheet(
                    "color:%s;" % (_FG["up"] if pnl > 0 else
                                   _FG["dn"] if pnl < 0 else _MUTED)
                )
                self._lbl_pnl.setToolTip("미실현 포인트 — 수수료 전이다.")
            self._lbl_pos_q.setText("")
        elif status == "FLAT":
            self._lbl_pos.setText("무포지션")
            self._lbl_pos.setStyleSheet("color:%s;" % _MUTED)
            self._lbl_pos.setToolTip(
                "측정된 무포지션이다 — 갱신이 살아 있고 status=FLAT 이다.\n"
                "이 줄이 답하는 질문은 「들어가도 되나」다 — 왼쪽 상태 배지를 본다."
            )
            self._lbl_pos_q.setText("· 들어가도 되나")
        else:
            self._lbl_pos.setText("포지션 %s" % (status or "—"))
            self._lbl_pos.setStyleSheet("color:%s;" % _MUTED)
            self._lbl_pos_q.setText("")

    def _apply(
        self,
        candles:          List[dict],
        ensemble:         Optional[dict],
        hz_dirs:          Dict[str, int],
        candle_decisions: Dict[str, dict],
        state:            Optional[dict] = None,
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

        # ── 좌측 중단 (상태 · 현재가 · 포지션) ────────────────────
        try:
            self._update_mid_row(candles, state)
            # 빈 라벨은 간격만 먹는다 — 숨긴다
            for _w in (self._lbl_stop, self._lbl_pnl,
                       self._lbl_pos_q, self._lbl_price_src):
                _w.setVisible(bool(_w.text()))
        except Exception:
            # 배너 한 줄 때문에 차트를 죽이지 않는다
            pass

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
