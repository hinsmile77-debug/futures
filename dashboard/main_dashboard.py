# dashboard/main_dashboard.py — 5창 실시간 모니터링 대시보드
"""
PyQt5 기반 5개 패널 통합 대시보드

패널 구성:
  Panel 1 (좌상) — 실시간 시세 + 포지션 현황
  Panel 2 (우상) — 앙상블 신호 + 신뢰도 + 체크리스트
  Panel 3 (중앙) — 분봉 캔들 + 지표 차트
  Panel 4 (좌하) — 거래 로그 (진입/청산/손익)
  Panel 5 (우하) — 시스템 상태 (CB·레짐·수급·매크로)

Python 3.7 32-bit + PyQt5 호환
키움 OpenAPI+와 동일 프로세스에서 실행
"""
import sys
import logging
import datetime
from typing import Optional, Dict, List
from collections import deque

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QGridLayout,
        QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QFrame,
        QSplitter, QPushButton, QGroupBox,
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QColor, QPalette, QFont
    _QT_OK = True
except ImportError:
    _QT_OK = False

logger = logging.getLogger("DASHBOARD")

# ── 색상 팔레트 (다크 테마) ──────────────────────────────────────
_BG     = "#1a1a2e"
_BG2    = "#16213e"
_BG3    = "#0f3460"
_GREEN  = "#00ff87"
_RED    = "#ff4757"
_YELLOW = "#ffa502"
_WHITE  = "#e8e8e8"
_GRAY   = "#808080"
_BLUE   = "#2196f3"

_BASE_STYLE = f"""
    QMainWindow, QWidget {{ background-color: {_BG}; color: {_WHITE}; }}
    QGroupBox {{
        border: 1px solid {_BG3};
        border-radius: 4px;
        margin-top: 8px;
        font-weight: bold;
        color: {_YELLOW};
    }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 8px; }}
    QLabel {{ color: {_WHITE}; }}
    QTextEdit {{
        background-color: {_BG2};
        color: {_WHITE};
        border: 1px solid {_BG3};
        font-family: Consolas, monospace;
        font-size: 11px;
    }}
    QPushButton {{
        background-color: {_BG3};
        color: {_WHITE};
        border: 1px solid {_BLUE};
        border-radius: 3px;
        padding: 4px 10px;
    }}
    QPushButton:hover {{ background-color: {_BLUE}; }}
"""


class _ValueLabel(QLabel if _QT_OK else object):
    """수치 표시 레이블 — 색상 자동 변환"""
    def set_value(self, text: str, color: str = _WHITE):
        if _QT_OK:
            self.setText(text)
            self.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px;")

    def set_pnl(self, value: float, suffix: str = "pt"):
        color = _GREEN if value > 0 else (_RED if value < 0 else _WHITE)
        self.set_value(f"{value:+.2f}{suffix}", color)


class MainDashboard(QMainWindow if _QT_OK else object):
    """
    5창 통합 대시보드

    사용:
        app  = QApplication(sys.argv)
        dash = MainDashboard()
        dash.show()

    업데이트:
        dash.update_price(380.0, volume=1500)
        dash.update_signal(direction=1, confidence=0.72, grade="B")
        dash.update_position(status="LONG", qty=2, entry=379.5, pnl=0.5)
        dash.append_trade_log("14:02 [LONG] 2계약 @ 379.50 진입")
        dash.update_system_status(cb_state="NORMAL", regime="추세장", ...)
    """

    def __init__(self, parent=None):
        if not _QT_OK:
            logger.warning("[Dashboard] PyQt5 미설치 — 텍스트 모드로 동작")
            return

        super().__init__(parent)
        self.setWindowTitle("미륵이 — KOSPI 200 선물 자동매매 v7.0")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(_BASE_STYLE)

        self._build_ui()
        self._start_clock()

    # ── UI 구성 ───────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout  = QGridLayout(central)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        # Panel 1: 시세 + 포지션
        self._panel_price    = self._build_panel1()
        # Panel 2: 신호
        self._panel_signal   = self._build_panel2()
        # Panel 3: 로그
        self._panel_trade    = self._build_panel3()
        # Panel 4: 시스템 상태
        self._panel_system   = self._build_panel4()
        # Panel 5: 수급 + 매크로
        self._panel_macro    = self._build_panel5()

        layout.addWidget(self._panel_price,  0, 0, 1, 1)
        layout.addWidget(self._panel_signal, 0, 1, 1, 1)
        layout.addWidget(self._panel_macro,  0, 2, 1, 1)
        layout.addWidget(self._panel_trade,  1, 0, 1, 2)
        layout.addWidget(self._panel_system, 1, 2, 1, 1)

        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)

    # ── Panel 1: 시세 + 포지션 ────────────────────────────────────
    def _build_panel1(self) -> QGroupBox:
        box = QGroupBox("📊 실시간 시세 / 포지션")
        v   = QVBoxLayout(box)

        # 현재가
        row = QHBoxLayout()
        row.addWidget(QLabel("현재가"))
        self.lbl_price = _ValueLabel("—")
        self.lbl_price.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {_WHITE};")
        row.addWidget(self.lbl_price)
        row.addStretch()
        v.addLayout(row)

        # 거래량
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("거래량"))
        self.lbl_volume = _ValueLabel("—")
        row2.addWidget(self.lbl_volume)
        row2.addStretch()
        v.addLayout(row2)

        v.addWidget(self._hline())

        # 포지션
        for attr, label in [
            ("lbl_pos_status", "포지션"),
            ("lbl_pos_qty",    "계약 수"),
            ("lbl_pos_entry",  "진입가"),
            ("lbl_pos_pnl",    "미실현 손익"),
            ("lbl_pos_stop",   "손절가"),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            lbl = _ValueLabel("—")
            setattr(self, attr, lbl)
            row.addWidget(lbl)
            row.addStretch()
            v.addLayout(row)

        v.addStretch()
        return box

    # ── Panel 2: 신호 + 체크리스트 ───────────────────────────────
    def _build_panel2(self) -> QGroupBox:
        box = QGroupBox("🎯 앙상블 신호 / 체크리스트")
        v   = QVBoxLayout(box)

        for attr, label in [
            ("lbl_direction",   "방향"),
            ("lbl_confidence",  "신뢰도"),
            ("lbl_grade",       "등급"),
            ("lbl_zone",        "시간대"),
            ("lbl_hurst",       "Hurst"),
            ("lbl_micro",       "미시 레짐"),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{label:<10}"))
            lbl = _ValueLabel("—")
            setattr(self, attr, lbl)
            row.addWidget(lbl)
            row.addStretch()
            v.addLayout(row)

        v.addWidget(self._hline())
        v.addWidget(QLabel("체크리스트"))
        self.lbl_checklist = QLabel("—")
        self.lbl_checklist.setWordWrap(True)
        self.lbl_checklist.setStyleSheet(f"color: {_GRAY}; font-size: 10px;")
        v.addWidget(self.lbl_checklist)
        v.addStretch()
        return box

    # ── Panel 3: 거래 로그 ────────────────────────────────────────
    def _build_panel3(self) -> QGroupBox:
        box = QGroupBox("📋 거래 로그")
        v   = QVBoxLayout(box)
        self.txt_trade_log = QTextEdit()
        self.txt_trade_log.setReadOnly(True)
        self.txt_trade_log.setMaximumHeight(300)
        v.addWidget(self.txt_trade_log)

        # 일일 통계
        row = QHBoxLayout()
        for attr, label in [
            ("lbl_stat_trades", "거래"),
            ("lbl_stat_wr",     "승률"),
            ("lbl_stat_pnl",    "일 손익"),
        ]:
            row.addWidget(QLabel(label))
            lbl = _ValueLabel("—")
            setattr(self, attr, lbl)
            row.addWidget(lbl)
            row.addSpacing(20)
        v.addLayout(row)
        return box

    # ── Panel 4: 시스템 상태 ──────────────────────────────────────
    def _build_panel4(self) -> QGroupBox:
        box = QGroupBox("⚙️ 시스템 상태")
        v   = QVBoxLayout(box)

        for attr, label in [
            ("lbl_cb_state",   "Circuit Breaker"),
            ("lbl_latency",    "API 지연"),
            ("lbl_cb_count",   "CB 트리거 횟수"),
            ("lbl_model_acc",  "30분 모델 정확도"),
            ("lbl_last_train", "최근 재학습"),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{label:<15}"))
            lbl = _ValueLabel("—")
            setattr(self, attr, lbl)
            row.addWidget(lbl)
            row.addStretch()
            v.addLayout(row)

        v.addWidget(self._hline())

        # 긴급 정지 버튼
        self.btn_kill = QPushButton("🛑  긴급 정지  (Ctrl+Alt+K)")
        self.btn_kill.setStyleSheet(
            f"background-color: {_RED}; color: white; "
            f"font-weight: bold; font-size: 13px; padding: 8px;"
        )
        v.addWidget(self.btn_kill)

        # 시스템 로그
        self.txt_sys_log = QTextEdit()
        self.txt_sys_log.setReadOnly(True)
        v.addWidget(self.txt_sys_log)
        return box

    # ── Panel 5: 수급 + 매크로 ────────────────────────────────────
    def _build_panel5(self) -> QGroupBox:
        box = QGroupBox("🌐 수급 / 매크로")
        v   = QVBoxLayout(box)

        for attr, label in [
            ("lbl_foreign_fut",  "외인 선물"),
            ("lbl_retail_fut",   "개인 선물"),
            ("lbl_inst_fut",     "기관 선물"),
            ("lbl_vix",          "VIX"),
            ("lbl_usdkrw",       "USD/KRW"),
            ("lbl_sp500",        "S&P500"),
            ("lbl_pcr",          "P/C Ratio"),
            ("lbl_regime",       "매크로 레짐"),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{label:<12}"))
            lbl = _ValueLabel("—")
            setattr(self, attr, lbl)
            row.addWidget(lbl)
            row.addStretch()
            v.addLayout(row)

        v.addStretch()
        return box

    # ── 업데이트 메서드 ───────────────────────────────────────────
    def update_price(self, price: float, volume: int = 0, chg: float = 0.0):
        if not _QT_OK:
            return
        color = _GREEN if chg >= 0 else _RED
        self.lbl_price.set_value(f"{price:.2f}", color)
        self.lbl_volume.set_value(f"{volume:,}", _GRAY)

    def update_signal(
        self,
        direction:  int,
        confidence: float,
        grade:      str,
        zone:       str = "",
        hurst:      float = 0.5,
        micro:      str = "",
        checks:     dict = None,
    ):
        if not _QT_OK:
            return
        dir_str   = "▲ 상승" if direction > 0 else ("▼ 하락" if direction < 0 else "━ 중립")
        dir_color = _GREEN  if direction > 0 else (_RED    if direction < 0 else _GRAY)
        self.lbl_direction.set_value(dir_str, dir_color)
        self.lbl_confidence.set_value(f"{confidence:.1%}", _YELLOW if confidence > 0.65 else _WHITE)
        grade_color = {
            "A": _GREEN, "B": _YELLOW, "C": _GRAY, "X": _RED
        }.get(grade, _WHITE)
        self.lbl_grade.set_value(f"  {grade}급", grade_color)
        self.lbl_zone.set_value(zone, _GRAY)
        hurst_color = _GREEN if hurst > 0.55 else (_RED if hurst < 0.45 else _YELLOW)
        self.lbl_hurst.set_value(f"{hurst:.3f}", hurst_color)
        self.lbl_micro.set_value(micro, _YELLOW)

        if checks:
            passed = [k for k, v in checks.items() if v]
            failed = [k for k, v in checks.items() if not v]
            self.lbl_checklist.setText(
                f"✅ {', '.join(passed)}\n"
                f"❌ {', '.join(failed)}"
            )

    def update_position(
        self,
        status:     str,
        qty:        int,
        entry:      float,
        pnl:        float,
        stop:       float,
    ):
        if not _QT_OK:
            return
        status_color = _GREEN if status == "LONG" else (_RED if status == "SHORT" else _GRAY)
        self.lbl_pos_status.set_value(status, status_color)
        self.lbl_pos_qty.set_value(f"{qty}계약", _WHITE)
        self.lbl_pos_entry.set_value(f"{entry:.2f}", _WHITE)
        self.lbl_pos_pnl.set_pnl(pnl)
        self.lbl_pos_stop.set_value(f"{stop:.2f}", _RED)

    def append_trade_log(self, line: str, color: str = _WHITE):
        if not _QT_OK:
            logger.info(f"[TRADE LOG] {line}")
            return
        ts  = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_trade_log.append(f'<span style="color:{color}">[{ts}] {line}</span>')
        self.txt_trade_log.verticalScrollBar().setValue(
            self.txt_trade_log.verticalScrollBar().maximum()
        )

    def update_system_status(
        self,
        cb_state:   str  = "NORMAL",
        latency_ms: float = 0.0,
        cb_count:   int  = 0,
        model_acc:  float = 0.0,
        last_train: str  = "",
    ):
        if not _QT_OK:
            return
        cb_color = _GREEN if cb_state == "NORMAL" else (_YELLOW if cb_state == "PAUSED" else _RED)
        self.lbl_cb_state.set_value(cb_state, cb_color)
        lat_color = _GREEN if latency_ms < 300 else (_YELLOW if latency_ms < 1000 else _RED)
        self.lbl_latency.set_value(f"{latency_ms:.0f}ms", lat_color)
        self.lbl_cb_count.set_value(str(cb_count), _YELLOW if cb_count > 0 else _WHITE)
        self.lbl_model_acc.set_value(f"{model_acc:.1%}", _GREEN if model_acc > 0.6 else _WHITE)
        self.lbl_last_train.set_value(last_train, _GRAY)

    def update_supply_macro(
        self,
        foreign_fut: int = 0,
        retail_fut:  int = 0,
        inst_fut:    int = 0,
        vix:         float = 20.0,
        usd_krw:     float = 1380.0,
        sp500_chg:   float = 0.0,
        pcr:         float = 1.0,
        regime:      str   = "NEUTRAL",
    ):
        if not _QT_OK:
            return
        for lbl, val in [
            (self.lbl_foreign_fut, foreign_fut),
            (self.lbl_retail_fut,  retail_fut),
            (self.lbl_inst_fut,    inst_fut),
        ]:
            color = _GREEN if val > 0 else (_RED if val < 0 else _GRAY)
            lbl.set_value(f"{val:+,}계약", color)
        vix_color = _GREEN if vix < 20 else (_YELLOW if vix < 30 else _RED)
        self.lbl_vix.set_value(f"{vix:.1f}", vix_color)
        self.lbl_usdkrw.set_value(f"{usd_krw:,.1f}", _WHITE)
        sp_color = _GREEN if sp500_chg >= 0 else _RED
        self.lbl_sp500.set_value(f"{sp500_chg:+.2%}", sp_color)
        self.lbl_pcr.set_value(f"{pcr:.2f}", _YELLOW if pcr > 1.2 else _WHITE)
        regime_color = {"RISK_ON": _GREEN, "NEUTRAL": _WHITE, "RISK_OFF": _RED}.get(regime, _WHITE)
        self.lbl_regime.set_value(regime, regime_color)

    def append_sys_log(self, line: str):
        if not _QT_OK:
            logger.info(f"[SYS] {line}")
            return
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_sys_log.append(f"[{ts}] {line}")
        self.txt_sys_log.verticalScrollBar().setValue(
            self.txt_sys_log.verticalScrollBar().maximum()
        )

    def update_daily_stats(self, trades: int, win_rate: float, pnl_pts: float):
        if not _QT_OK:
            return
        self.lbl_stat_trades.set_value(f"{trades}건", _WHITE)
        wr_color = _GREEN if win_rate >= 0.55 else (_YELLOW if win_rate >= 0.45 else _RED)
        self.lbl_stat_wr.set_value(f"{win_rate:.1%}", wr_color)
        self.lbl_stat_pnl.set_pnl(pnl_pts)

    # ── 헬퍼 ─────────────────────────────────────────────────────
    def _hline(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {_BG3};")
        return line

    def _start_clock(self):
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._tick_clock)
        self._clock_timer.start(1000)

    def _tick_clock(self):
        now = datetime.datetime.now()
        self.setWindowTitle(
            f"미륵이 v7.0  |  {now.strftime('%Y-%m-%d %H:%M:%S')}"
        )


# ── 텍스트 전용 대시보드 (PyQt5 없을 때) ─────────────────────────
class TextDashboard:
    """PyQt5 없을 때 로그 기반 간이 대시보드"""

    def __init__(self):
        logger.info("[Dashboard] 텍스트 모드 (PyQt5 미설치)")

    def update_price(self, price, volume=0, chg=0.0):
        logger.info(f"[PRICE] {price:.2f} vol={volume} chg={chg:+.4f}")

    def update_signal(self, direction, confidence, grade, **kwargs):
        dir_s = "UP" if direction > 0 else ("DOWN" if direction < 0 else "FLAT")
        logger.info(f"[SIGNAL] {dir_s} conf={confidence:.2f} grade={grade}")

    def update_position(self, status, qty, entry, pnl, stop):
        logger.info(f"[POS] {status} {qty}계약 @ {entry:.2f} PnL={pnl:+.2f}pt stop={stop:.2f}")

    def append_trade_log(self, line, color=None):
        logger.info(f"[TRADE] {line}")

    def update_system_status(self, **kwargs):
        logger.info(f"[SYS] {kwargs}")

    def update_supply_macro(self, **kwargs):
        logger.info(f"[MACRO] {kwargs}")

    def append_sys_log(self, line):
        logger.info(f"[SYS] {line}")

    def update_daily_stats(self, trades, win_rate, pnl_pts):
        logger.info(f"[STATS] 거래={trades} 승률={win_rate:.1%} PnL={pnl_pts:+.2f}pt")

    def show(self):
        pass


def create_dashboard():
    """환경에 따라 적절한 대시보드 반환"""
    if _QT_OK:
        return MainDashboard()
    return TextDashboard()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if _QT_OK:
        app  = QApplication(sys.argv)
        dash = MainDashboard()
        dash.update_price(380.25, volume=1523, chg=0.0025)
        dash.update_signal(direction=1, confidence=0.72, grade="B",
                           zone="STABLE_TREND", hurst=0.58, micro="추세장")
        dash.update_position(status="LONG", qty=2, entry=379.50, pnl=0.75, stop=378.75)
        dash.update_system_status(cb_state="NORMAL", latency_ms=45.0,
                                   cb_count=0, model_acc=0.67)
        dash.update_supply_macro(foreign_fut=350, retail_fut=-200,
                                  vix=18.5, usd_krw=1375.0, sp500_chg=0.003, pcr=0.85)
        dash.append_trade_log("LONG 2계약 @ 379.50 진입 (B급, 1차)", color=_GREEN)
        dash.show()
        sys.exit(app.exec_())
    else:
        dash = TextDashboard()
        dash.update_price(380.25, volume=1523)
        dash.update_signal(1, 0.72, "B")
        print("PyQt5 없음 — 텍스트 대시보드 동작 확인")
