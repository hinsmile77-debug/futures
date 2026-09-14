"""보조 모니터 배너 좌측 중단 — 상태 · 현재가 · 포지션 한 줄.

시안 「② 보조 모니터 배너」의 중단 행. 두 배너가 **같은 위젯을 공유**한다:
  · `DirectionIndicatorWidget` (방향 인디케이터) — 대시보드 임베드 + AOT 팝업
  · `CandleChartDialog`        (봉차트 인디케이터)

설계 의도 — **보유 여부에 따라 답하는 질문이 바뀐다.**
  무포지션 → 「들어가도 되나」            → 4상태 배지가 답한다
  보유 중  → 「손절이 어디고 얼마 벌고 있나」 → 손절·미실현이 답한다
같은 자리, 같은 높이. 눈이 옮겨 다닐 필요가 없다.

🔴 계측 4원칙 ②·④ — **미측정 ≠ 0건**, 그럴듯한 값으로 채우지 않는다.
  포지션 스냅샷이 한 번도 안 왔으면 「무포지션」이 아니라 「포지션 미연결」,
  60초 넘게 끊기면 「갱신 끊김」이다. 상태가 안 붙은 봉은 「중립」이 아니라
  「문턱 미달」, 30봉 미만이면 「워밍업 n/31」이다. FLAT/0 으로 뭉개지 않는다.
"""
import sqlite3
import time
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel

from config.settings import RAW_DATA_DB
from dashboard.stack_state import (
    compute_states, STATE_KO, STATE_COLOR, STATE_NA_KO, STATE_NA_COLOR, STATE_W,
)

_MUTED = "#8b949e"
_UP    = "#3fb950"
_DN    = "#f85149"
_WARN  = "#d29922"

# ── 포지션 스냅샷 ────────────────────────────────────────────────
# 포지션은 **DB에 없다** — main.py → DashboardAPI.update_position 으로만 흐른다.
# 배너는 같은 프로세스의 위젯이므로, 그 흐름을 여기 한 번 떨궈두고 읽는다
# (단방향·읽기 전용).
_POS_STALE_SEC = 60.0
_POS_SNAPSHOT: Dict[str, object] = {"data": None, "mono": 0.0}


def publish_position(pos_data: Optional[dict]) -> None:
    """대시보드가 받은 포지션을 배너가 읽을 수 있게 떨군다. 부작용 없음."""
    _POS_SNAPSHOT["data"] = dict(pos_data) if pos_data else None
    _POS_SNAPSHOT["mono"] = time.monotonic()


def read_position() -> Tuple[str, Optional[dict]]:
    """반환: (상태문자열, pos_data|None)
      "none"  — 스냅샷 한 번도 없음 (미연결)
      "stale" — 왔지만 60초 넘게 갱신 없음
      "live"  — 유효
    """
    if not _POS_SNAPSHOT["mono"]:
        return "none", None
    age = time.monotonic() - float(_POS_SNAPSHOT["mono"])
    return ("stale" if age > _POS_STALE_SEC else "live"), _POS_SNAPSHOT["data"]


# ── 당일 상태 조회 ───────────────────────────────────────────────
# 🔴 당일 중앙값 디바이어스와 50% 분위 문턱은 **하루 전체**를 쓴다.
#   화면의 최근 N봉만으로는 계산할 수 없다(§3-2).
_STATE_CACHE: Dict[str, object] = {"key": None, "val": None}


def fetch_day_state(ts_from: str, ts_to: str) -> Optional[dict]:
    """반환: {"state": STATE|None, "ts": 마지막 봉 ts, "n": 상태계산 사용 봉수}

    마지막 봉 ts 가 그대로면 재계산하지 않는다 — 폴링은 10초, 봉은 1분이다.

    ⚠ 실측 37ms(조회 4.6 + 계산 33). **GUI 스레드에서 직접 부르지 마라** —
      `MidStatusRow.tick()` 이 워커 스레드로 돌린다.
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
        if not rows:
            return None
        last_ts = rows[-1]["ts"]
        key = "%s|%d" % (last_ts, len(rows))
        if _STATE_CACHE["key"] == key:
            return _STATE_CACHE["val"]
        bars = [dict(r) for r in rows]
        res = compute_states(bars)
        val = {
            "state": res["state_map"].get(last_ts),
            "ts":    last_ts,
            "n":     len([b for b in bars if (b.get("oi") or 0) > 0]),
        }
        _STATE_CACHE["key"], _STATE_CACHE["val"] = key, val
        return val
    except Exception:
        return None


# ── 보유 중 레벨선 ───────────────────────────────────────────────
# 시안 「보유 중」 차트: 진입 · 하드스톱 · TP1/2/3 · 트레일링을 가로선으로.
# 값은 전부 `pos_data` 에 이미 들어 있다 — 만들지 않고 **받아 그린다**.
#
# 🔴 트레일링은 **현재 값 하나뿐**이다. 시안의 계단식 궤적은 스톱 이동 이력이
#   있어야 그릴 수 있는데 그런 테이블이 없다(`tp1_trail_shadow`·
#   `phantom_stop_shadow` 는 별건 섀도우다). 없는 궤적을 그럴듯하게
#   그리지 않는다(계측 4원칙 ④) — 현재 수준만 수평선으로 긋는다.
# 라벨은 (한글, ASCII 대체) 쌍이다 — 아래 `_ko_font()` 설명 참고.
_LEVEL_SPEC = (
    ("stop",  ("하드스톱", "STOP"),  "#F85149", 1.3, "-"),
    ("entry", ("진입",     "ENTRY"), "#E6EDF3", 1.5, "-"),
    ("tp1",   ("TP1",      "TP1"),   "#3FB950", 1.0, "-"),
    ("tp2",   ("TP2",      "TP2"),   "#3FB950", 1.0, "-"),
    ("tp3",   ("TP3",      "TP3"),   "#3FB950", 1.0, "-"),
    ("trail", ("트레일링", "TRAIL"), "#D29922", 1.1, "--"),
)

# 🔴 matplotlib 기본 폰트에는 한글 글리프가 **없다** — 그냥 쓰면 「진입」이
#   두부(□□)로 찍힌다(실측). Qt 라벨은 멀쩡한데 차트만 깨지므로 놓치기 쉽다.
#   설치된 폰트에서 한글 가능한 것을 찾아 쓰고, **하나도 없으면 두부 대신
#   ASCII 라벨로 떨어뜨린다**. 읽을 수 없는 글자를 그리느니 영문이 낫다.
_KO_FONTS = ("Malgun Gothic", "NanumGothic", "Noto Sans CJK KR",
             "Noto Sans CJK JP", "Noto Sans KR", "AppleGothic",
             "Gulim", "Batang", "Droid Sans Fallback")
_ko_font_cache: Optional[str] = None


def _has_hangul(name: str) -> bool:
    """그 폰트가 한글 글리프를 **실제로 가지고 있는가**.

    🔴 이름만 보고 고르면 안 된다. `Droid Sans Fallback` 은 폰트 목록에
      있었지만 findfont 가 내준 파일에는 한글이 없었고, fontname 으로 강제한
      순간 숫자까지 전부 두부가 됐다(실측). cmap 을 직접 뒤진다.
    """
    try:
        from matplotlib import font_manager as fm
        from matplotlib.ft2font import FT2Font
        path = fm.findfont(fm.FontProperties(family=name),
                           fallback_to_default=False)
        f = FT2Font(path)
        return bool(f.get_char_index(ord("진")) and f.get_char_index(ord("0")))
    except Exception:
        return False


def _ko_font() -> str:
    """쓸 수 있는 한글 폰트 이름. 없으면 빈 문자열(→ ASCII 라벨)."""
    global _ko_font_cache
    if _ko_font_cache is not None:
        return _ko_font_cache
    _ko_font_cache = ""
    for name in _KO_FONTS:                       # ① 흔한 후보 먼저 (빠름)
        if _has_hangul(name):
            _ko_font_cache = name
            return _ko_font_cache
    try:                                         # ② 없으면 설치된 폰트 전수 조사
        from matplotlib import font_manager as fm
        for name in sorted({f.name for f in fm.fontManager.ttflist}):
            if _has_hangul(name):
                _ko_font_cache = name
                break
    except Exception:
        pass
    return _ko_font_cache


def position_levels() -> List[tuple]:
    """보유 중이면 [(label, value, color, lw, ls)], 아니면 [].

    값이 없거나 0 이하인 항목은 **거른다** — 0.0 을 선으로 그으면
    「손절이 0」 이라는 거짓말이 된다.
    """
    state, pos = read_position()
    if state != "live" or not pos:
        return []
    if str(pos.get("status", "") or "").strip().upper() not in ("LONG", "SHORT"):
        return []
    raw = {
        "stop":  _f(pos.get("stop")),
        "entry": _f(pos.get("entry")),
        "tp1":   _f(pos.get("tp1")),
        "tp2":   _f(pos.get("tp2")),
        "tp3":   _f(pos.get("tp3")),
        "trail": _f(pos.get("trail_basis")),
    }
    out = []
    _ko = bool(_ko_font())
    for key, labels, color, lw, ls in _LEVEL_SPEC:
        v = raw.get(key, 0.0)
        if v <= 0:
            continue
        # 트레일링이 하드스톱과 사실상 같으면 선을 겹쳐 긋지 않는다
        if key == "trail" and abs(v - raw.get("stop", 0.0)) < 0.01:
            continue
        out.append((labels[0] if _ko else labels[1], v, color, lw, ls))
    return out


def draw_position_levels(ax, x_right: float) -> List[float]:
    """matplotlib 축에 레벨선 + 우측 라벨. 반환: 그린 값들(축 범위 확장용).

    두 배너(방향 인디케이터 · 봉차트)가 같이 쓴다.
    """
    vals = []
    for label, v, color, lw, ls in position_levels():
        ax.axhline(y=v, color=color, linewidth=lw, linestyle=ls,
                   alpha=0.95, zorder=3)
        _kw = {"fontname": _ko_font()} if _ko_font() else {}
        ax.text(x_right, v, "%s %.1f" % (label, v),
                color=color, fontsize=7.5, fontweight="bold",
                ha="right", va="bottom", zorder=6, **_kw)
        vals.append(v)
    return vals


class _StateWorker(QThread):
    """당일 상태 계산 — **GUI 스레드 밖에서** 돈다.

    실측 37ms(조회 4.6 + 계산 33). 대시보드 페인트 경보선이 30ms 인데
    10초마다 이걸 GUI 스레드에서 돌리면 그 자체가 끊김이 된다.
    """

    done = pyqtSignal(object)

    def __init__(self, ts_from: str, ts_to: str):
        super().__init__()
        self._f, self._t = ts_from, ts_to

    def run(self):
        try:
            self.done.emit(fetch_day_state(self._f, self._t))
        except Exception:
            self.done.emit(None)


class MidStatusRow(QFrame):
    """[상태 배지]  현재가  포지션 …………………  최근 N봉"""

    def __init__(self, span_text: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "QFrame { background:#161b22; border-top:1px solid #30363d;"
            " border-bottom:1px solid #30363d; }"
        )
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 4, 12, 4)
        row.setSpacing(10)

        # ① 4상태 배지
        self._lbl_state = QLabel("상태 —")
        self._lbl_state.setFont(QFont("Arial", 10, QFont.Bold))
        self._lbl_state.setAlignment(Qt.AlignCenter)
        self._lbl_state.setMinimumWidth(88)
        self._style_badge(STATE_NA_COLOR, "상태 —")
        self._lbl_state.setToolTip(
            "봉별 4상태 — 공격자 방향 × ΔOI 부호 (30봉 창, 당일 중앙값 디바이어스)\n"
            "  상방 쌓기   : 매수가 때리며 미결제 증가 (신규 롱)\n"
            "  기계적 매수 : 매수가 때리며 미결제 감소 (숏커버)\n"
            "  하방 쌓기   : 매도가 때리며 미결제 증가 (신규 숏)\n"
            "  기계적 매도 : 매도가 때리며 미결제 감소 (롱커버)\n"
            "  문턱 미달   : 활성 문턱(|공격자|·|ΔOI| 각각 당일 50%분위) 미달\n"
            "                — 「중립」이 아니다\n"
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

        self._lbl_src = QLabel("")
        self._lbl_src.setFont(QFont("Arial", 8))
        self._lbl_src.setStyleSheet("color:%s;" % _MUTED)
        row.addWidget(self._lbl_src, 0, Qt.AlignBottom)

        # ③ 포지션
        self._lbl_pos = QLabel("포지션 미연결")
        self._lbl_pos.setFont(QFont("Consolas", 11, QFont.Bold))
        self._lbl_pos.setStyleSheet("color:%s;" % _MUTED)
        row.addWidget(self._lbl_pos, 0, Qt.AlignVCenter)

        # 🔴 손절과 손익을 **한 라벨에 섞지 않는다**. 손익 부호로 전체를 칠하면
        #   「손절 1044.00」이 초록으로 찍혀 안심 신호처럼 읽힌다.
        self._lbl_stop = QLabel("")
        self._lbl_stop.setFont(QFont("Consolas", 11, QFont.Bold))
        self._lbl_stop.setStyleSheet("color:%s;" % _DN)
        self._lbl_stop.setToolTip(
            "현재 트레일링 스톱. 진입 시 고정값이 아니라 **움직인다**."
        )
        row.addWidget(self._lbl_stop, 0, Qt.AlignVCenter)

        self._lbl_pnl = QLabel("")
        self._lbl_pnl.setFont(QFont("Consolas", 13, QFont.Bold))
        self._lbl_pnl.setStyleSheet("color:%s;" % _MUTED)
        self._lbl_pnl.setToolTip("미실현 포인트 — 수수료 전이다.")
        row.addWidget(self._lbl_pnl, 0, Qt.AlignVCenter)

        self._lbl_hint = QLabel("")
        self._lbl_hint.setFont(QFont("Arial", 8))
        self._lbl_hint.setStyleSheet("color:#586069;")
        row.addWidget(self._lbl_hint, 0, Qt.AlignVCenter)

        row.addStretch(1)

        self._lbl_span = QLabel(span_text)
        self._lbl_span.setFont(QFont("Arial", 9))
        self._lbl_span.setStyleSheet("color:%s;" % _MUTED)
        row.addWidget(self._lbl_span, 0, Qt.AlignVCenter)

        for _w in (self._lbl_stop, self._lbl_pnl, self._lbl_hint, self._lbl_src):
            _w.setVisible(False)

        self._last_candles: List[dict] = []
        self._state: Optional[dict] = None   # 마지막으로 계산된 상태
        self._state_key = ""                 # 재계산 판단용 (분 단위)
        self._worker: Optional[_StateWorker] = None

    # ── 갱신 ────────────────────────────────────────────────────

    def _style_badge(self, color: str, text: str):
        self._lbl_state.setText(text)
        self._lbl_state.setStyleSheet(
            "background:%s; color:#0d1117; border-radius:3px;"
            " padding:2px 8px; font-weight:bold; border:none;" % color
        )

    def tick(self, candles: List[dict], ts_from: str, ts_to: str):
        """즉시 그리고, **분이 바뀐 경우에만** 상태를 워커로 다시 센다.

        봉은 1분에 하나뿐인데 폴링은 10초다 — 같은 분 안에서 다시 셀 이유가 없다.
        첫 계산이 끝나기 전에는 「상태 —」로 남는다. 없는 값을 채우지 않는다.
        """
        self.update_row(candles, self._state)
        key = time.strftime("%Y-%m-%d %H:%M")
        if key == self._state_key:
            return
        if self._worker is not None and self._worker.isRunning():
            return
        self._state_key = key
        self._worker = _StateWorker(ts_from, ts_to)
        self._worker.done.connect(self._on_state)
        self._worker.start()

    def _on_state(self, state):
        self._state = state
        self.update_row(self._last_candles, state)

    def update_row(self, candles: List[dict], state: Optional[dict]):
        self._last_candles = candles or []
        # ① 상태 배지
        if state is None:
            self._style_badge(STATE_NA_COLOR, "상태 —")
        elif state.get("n", 0) <= STATE_W:
            self._style_badge(STATE_NA_COLOR,
                              "워밍업 %d/%d" % (state.get("n", 0), STATE_W + 1))
        else:
            st = state.get("state")
            if st:
                self._style_badge(STATE_COLOR[st], STATE_KO[st])
            else:
                self._style_badge(STATE_NA_COLOR, STATE_NA_KO)

        # ② 포지션 — 현재가 출처도 여기서 갈린다
        pos_state, pos = read_position()
        bar_close = None
        if candles:
            try:
                bar_close = float(candles[-1]["close"])
            except (TypeError, ValueError, KeyError):
                bar_close = None

        live_px = None
        status = ""
        if pos_state == "live" and pos:
            status = str(pos.get("status", "") or "").strip().upper()
            try:
                _c = float(pos.get("current") or 0.0)
                live_px = _c if _c > 0 else None
            except (TypeError, ValueError):
                live_px = None

        px = live_px if live_px is not None else bar_close
        if px is None:
            self._lbl_price.setText("————")
            self._lbl_price.setStyleSheet("color:%s;" % _MUTED)
            self._lbl_src.setText("미수집")
        else:
            self._lbl_price.setText("%.2f" % px)
            self._lbl_price.setStyleSheet("color:#e6edf3;")
            self._lbl_src.setText("실시간" if live_px is not None else "종가")

        self._lbl_stop.setText("")
        self._lbl_pnl.setText("")
        self._lbl_hint.setText("")

        if pos_state == "none":
            # 한 번도 안 왔다 — 「무포지션」과 다르다
            self._lbl_pos.setText("포지션 미연결")
            self._lbl_pos.setStyleSheet("color:%s;" % _MUTED)
            self._lbl_pos.setToolTip(
                "포지션은 DB에 없다 — main.py 의 실시간 흐름에서만 온다.\n"
                "대시보드 없이 단독으로 띄웠거나, 아직 첫 갱신 전이다.\n"
                "「무포지션」이라는 뜻이 **아니다**."
            )
        elif pos_state == "stale":
            self._lbl_pos.setText("포지션 갱신 끊김")
            self._lbl_pos.setStyleSheet("color:%s;" % _WARN)
            self._lbl_pos.setToolTip(
                "마지막 포지션 갱신이 %d초를 넘었다 — 지금 상태를 모른다."
                % int(_POS_STALE_SEC)
            )
        elif status in ("LONG", "SHORT"):
            mult = 1 if status == "LONG" else -1
            side = "L" if status == "LONG" else "S"
            entry = _f(pos.get("entry"))
            stop  = _f(pos.get("stop"))
            try:
                qty = int(float(pos.get("qty") or 0))
            except (TypeError, ValueError):
                qty = 0
            cur = px if px is not None else entry
            pnl = (cur - entry) * mult if (entry and entry > 0 and cur) else None

            self._lbl_pos.setText(
                "%s  진입 %s" % ("%s×%d" % (side, qty) if qty else side,
                                 "%.2f" % entry if entry else "——")
            )
            self._lbl_pos.setStyleSheet("color:#e6edf3;")
            self._lbl_pos.setToolTip(
                "보유 중 — 이 줄이 답하는 질문은 「손절이 어디고 얼마 벌고 있나」다.\n"
                "손절은 현재 트레일링 스톱(PositionTracker.stop_price)이다.\n"
                "손익은 미실현 포인트 — 수수료 전이다."
            )
            self._lbl_stop.setText("손절 %s" % ("%.2f" % stop if stop else "——"))
            if pnl is None:
                self._lbl_pnl.setText("손익 ——")
                self._lbl_pnl.setStyleSheet("color:%s;" % _MUTED)
            else:
                self._lbl_pnl.setText("%+.2fp" % pnl)
                self._lbl_pnl.setStyleSheet(
                    "color:%s;" % (_UP if pnl > 0 else _DN if pnl < 0 else _MUTED)
                )
        elif status == "FLAT":
            self._lbl_pos.setText("무포지션")
            self._lbl_pos.setStyleSheet("color:%s;" % _MUTED)
            self._lbl_pos.setToolTip(
                "측정된 무포지션이다 — 갱신이 살아 있고 status=FLAT 이다.\n"
                "이 줄이 답하는 질문은 「들어가도 되나」다 — 왼쪽 상태 배지를 본다."
            )
            self._lbl_hint.setText("· 들어가도 되나")
        else:
            self._lbl_pos.setText("포지션 %s" % (status or "—"))
            self._lbl_pos.setStyleSheet("color:%s;" % _MUTED)

        # 빈 라벨은 간격만 먹는다
        for _w in (self._lbl_stop, self._lbl_pnl, self._lbl_hint, self._lbl_src):
            _w.setVisible(bool(_w.text()))

    def set_span_text(self, text: str):
        self._lbl_span.setText(text)


def _f(v) -> float:
    try:
        return float(v or 0.0)
    except (TypeError, ValueError):
        return 0.0
