# dashboard/main_dashboard.py
# 미륵이 v7.0 — 풀 통합 대시보드
# PyQt5 기반 7개 패널 완전 구현
"""
구현 패널:
  1. 멀티 호라이즌 예측 + 파라미터 분석
  2. 다이버전스 지수 + 포지션 매트릭스
  3. 동적 피처 관리 패널 (SHAP)
  4. 청산 관리 패널
  5. 진입 관리 패널
  6. 알파 리서치 봇 패널
  7. 5층 로그 시스템
"""

import os
import subprocess
import sys
import random
import math
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QProgressBar, QTabWidget,
    QTextEdit, QFrame, QSplitter, QScrollArea, QGroupBox,
    QComboBox, QSlider, QCheckBox, QSizePolicy, QDesktopWidget
)
from PyQt5.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QPainter, QBrush, QPen,
    QLinearGradient, QFontDatabase, QIcon
)


# ────────────────────────────────────────────────────────────
# 해상도 감지 + 동적 폰트·여백 스케일링
# ────────────────────────────────────────────────────────────
class ScreenScale:
    """
    화면 해상도를 감지해 폰트/여백을 자동 조정

    기준 해상도: 1920×1080 (FHD)
      HD  ( 768p): scale 0.85 → 15% 축소
      FHD (1080p): scale 1.00 → 기본
      QHD (1440p): scale 1.30 → 30% 확대
      4K  (2160p): scale 1.80 → 80% 확대
    """
    _scale: float = 1.0
    _sw: int = 1920
    _sh: int = 1080

    @classmethod
    def init(cls):
        app = QApplication.instance()
        if app is None:
            return
        screen = app.primaryScreen()
        if screen is None:
            return
        geo     = screen.availableGeometry()
        cls._sw = geo.width()
        cls._sh = geo.height()
        # 세로 해상도 기준 스케일 (울트라와이드 오작동 방지)
        raw     = cls._sh / 1080.0
        cls._scale = max(0.80, min(2.20, raw))
        print(f"[Dashboard] 화면 해상도 {cls._sw}×{cls._sh} — 스케일 {cls._scale:.2f}×")

    @classmethod
    def f(cls, size: int) -> int:
        """폰트 사이즈 스케일 적용 (최소 8px)"""
        return max(8, round(size * cls._scale))

    @classmethod
    def p(cls, px: int) -> int:
        """여백·위젯 크기 스케일 적용 (최소 2px)"""
        return max(2, round(px * cls._scale))

    @classmethod
    def info(cls) -> str:
        return f"{cls._sw}×{cls._sh} (scale={cls._scale:.2f})"


S = ScreenScale   # 짧은 별칭으로 사용


def _get_commit_hash() -> str:
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        h = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root, stderr=subprocess.DEVNULL,
        ).decode().strip()
        return f"#{h}"
    except Exception:
        return "#??????"


COMMIT_HASH: str = _get_commit_hash()

# ── 색상 팔레트 (다크 테마) ──────────────────────────────────
C = {
    "bg":       "#0D1117",
    "bg2":      "#161B22",
    "bg3":      "#21262D",
    "border":   "#30363D",
    "text":     "#E6EDF3",
    "text2":    "#8B949E",
    "green":    "#3FB950",
    "red":      "#F85149",
    "blue":     "#58A6FF",
    "orange":   "#D29922",
    "purple":   "#A371F7",
    "cyan":     "#39D3BB",
    "yellow":   "#E3B341",
}


def make_style() -> str:
    """해상도 감지 후 동적 폰트 사이즈 적용 스타일시트 생성"""
    return f"""
    QMainWindow, QWidget {{
        background-color: {C['bg']};
        color: {C['text']};
        font-family: 'D2Coding', 'Consolas', 'Malgun Gothic', monospace;
        font-size: {S.f(12)}px;
    }}
    QGroupBox {{
        border: 1px solid {C['border']};
        border-radius: {S.p(6)}px;
        margin-top: {S.p(8)}px;
        padding: {S.p(6)}px;
        font-weight: bold;
        color: {C['text2']};
        font-size: {S.f(11)}px;
        letter-spacing: 1px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: {S.p(8)}px;
        padding: 0 {S.p(4)}px;
    }}
    QTabWidget::pane {{
        border: 1px solid {C['border']};
        background: {C['bg2']};
    }}
    QTabBar::tab {{
        background: {C['bg3']};
        color: {C['text2']};
        padding: {S.p(7)}px {S.p(16)}px;
        border: none;
        font-size: {S.f(11)}px;
        letter-spacing: 0.5px;
    }}
    QTabBar::tab:selected {{
        background: {C['bg2']};
        color: {C['text']};
        border-bottom: 2px solid {C['blue']};
    }}
    QTextEdit {{
        background: {C['bg']};
        color: {C['text']};
        border: 1px solid {C['border']};
        border-radius: {S.p(4)}px;
        font-family: 'D2Coding', 'Consolas', monospace;
        font-size: {S.f(11)}px;
    }}
    QPushButton {{
        background: {C['bg3']};
        color: {C['text']};
        border: 1px solid {C['border']};
        border-radius: {S.p(4)}px;
        padding: {S.p(6)}px {S.p(14)}px;
        font-size: {S.f(11)}px;
    }}
    QPushButton:hover {{
        background: {C['border']};
    }}
    QProgressBar {{
        background: {C['bg3']};
        border: none;
        border-radius: {S.p(3)}px;
        height: {S.p(6)}px;
    }}
    QProgressBar::chunk {{
        border-radius: {S.p(3)}px;
    }}
    QScrollBar:vertical {{
        background: {C['bg']};
        width: {S.p(7)}px;
    }}
    QScrollBar::handle:vertical {{
        background: {C['border']};
        border-radius: {S.p(3)}px;
    }}
    QLabel {{
        font-size: {S.f(12)}px;
    }}
"""


# ────────────────────────────────────────────────────────────
# 공통 위젯 헬퍼 (모두 S.f() 로 동적 스케일)
# ────────────────────────────────────────────────────────────
def mk_label(text, color=None, size=12, bold=False, align=Qt.AlignLeft):
    lb = QLabel(text)
    lb.setAlignment(align)
    style = f"font-size:{S.f(size)}px;"
    if color:
        style += f"color:{color};"
    if bold:
        style += "font-weight:bold;"
    lb.setStyleSheet(style)
    return lb


def mk_val_label(text="——", color=C['text'], size=15, bold=True, align=None):
    lb = QLabel(text)
    a  = align if align else (Qt.AlignRight | Qt.AlignVCenter)
    lb.setAlignment(a)
    lb.setStyleSheet(
        f"font-size:{S.f(size)}px;color:{color};"
        f"font-weight:{'bold' if bold else 'normal'};"
    )
    return lb


def mk_badge(text, bg, fg="#ffffff", size=10):
    lb = QLabel(f"  {text}  ")
    lb.setStyleSheet(
        f"background:{bg};color:{fg};border-radius:{S.p(3)}px;"
        f"font-size:{S.f(size)}px;font-weight:bold;"
        f"padding:{S.p(1)}px {S.p(3)}px;"
    )
    return lb


def mk_sep():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color:{C['border']};")
    return line


def mk_prog(color=C['green'], h=6):
    pb = QProgressBar()
    pb.setFixedHeight(S.p(h))
    pb.setTextVisible(False)
    pb.setStyleSheet(f"QProgressBar::chunk{{background:{color};}}")
    return pb


def card(title, widget, color=C['blue']):
    gb = QGroupBox(f"● {title}")
    gb.setStyleSheet(
        f"QGroupBox{{border:1px solid {C['border']};border-radius:{S.p(6)}px;"
        f"margin-top:{S.p(8)}px;padding:{S.p(8)}px;color:{color};"
        f"font-size:{S.f(11)}px;font-weight:bold;letter-spacing:1px;}}"
        f"QGroupBox::title{{subcontrol-origin:margin;"
        f"left:{S.p(8)}px;padding:0 {S.p(4)}px;}}"
    )
    lay = QVBoxLayout(gb)
    lay.setContentsMargins(S.p(4), S.p(14), S.p(4), S.p(4))
    lay.setSpacing(S.p(4))
    lay.addWidget(widget)
    return gb


# ────────────────────────────────────────────────────────────
# 패널 1: 멀티 호라이즌 예측 + 파라미터 분석
# ────────────────────────────────────────────────────────────
class PredictionPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._hz_labels = {}
        self._param_bars = {}
        self._param_vals = {}
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # 상단: 현재가 + 신호
        top = QHBoxLayout()
        self.lbl_price   = mk_val_label("——.——", C['text'], 20)
        self.lbl_signal  = mk_val_label("대기중", C['text2'], 16)
        self.lbl_conf    = mk_label("신뢰도 — %", C['text2'])
        top.addWidget(mk_label("현재가", C['text2']))
        top.addWidget(self.lbl_price, 2)
        top.addWidget(self.lbl_signal, 2)
        top.addWidget(self.lbl_conf, 1)
        lay.addLayout(top)
        lay.addWidget(mk_sep())

        # 멀티 호라이즌 카드 6개
        hz_title = mk_label("멀티 호라이즌 예측 ( 1 · 3 · 5 · 10 · 15 · 30분 )", C['blue'], 10, True)
        lay.addWidget(hz_title)
        hgrid = QGridLayout()
        hgrid.setSpacing(4)
        for i, hname in enumerate(["1분","3분","5분","10분","15분","30분"]):
            frame = QFrame()
            frame.setFixedHeight(72)
            frame.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};"
                f"border-radius:6px;}}"
            )
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(6, 4, 6, 4)
            hl = mk_label(hname, C['text2'], 10, align=Qt.AlignCenter)
            arr = mk_label("—", C['text2'], 22, True, Qt.AlignCenter)
            pct = mk_label("—%", C['text2'], 10, align=Qt.AlignCenter)
            fl.addWidget(hl)
            fl.addWidget(arr)
            fl.addWidget(pct)
            self._hz_labels[hname] = (frame, arr, pct)
            hgrid.addWidget(frame, 0, i)
        lay.addLayout(hgrid)
        lay.addWidget(mk_sep())

        # 파라미터 SHAP 중요도
        param_title = mk_label("파라미터 중요도 (SHAP 실시간)", C['purple'], 10, True)
        lay.addWidget(param_title)
        params = [
            ("CVD 다이버전스", "CORE", C['cyan']),
            ("VWAP 위치",      "CORE", C['cyan']),
            ("OFI 불균형",     "CORE", C['cyan']),
            ("외인 콜순매수",  "SHAP", C['purple']),
            ("다이버전스 지수","SHAP", C['purple']),
            ("프로그램 비차익","SHAP", C['purple']),
        ]
        pgrid = QGridLayout()
        pgrid.setSpacing(3)
        for i, (name, tag, col) in enumerate(params):
            badge = mk_badge(tag, col if tag=="CORE" else C['bg3'],
                             C['bg'] if tag=="CORE" else C['purple'])
            nlab  = mk_label(name, C['text'], 10)
            bar   = mk_prog(col, 8)
            vlab  = mk_val_label("—%", col, 11)
            pgrid.addWidget(badge, i, 0)
            pgrid.addWidget(nlab,  i, 1)
            pgrid.addWidget(bar,   i, 2)
            pgrid.addWidget(vlab,  i, 3)
            self._param_bars[name] = bar
            self._param_vals[name] = vlab
        lay.addLayout(pgrid)

        # 상관계수
        lay.addWidget(mk_sep())
        lay.addWidget(mk_label("파라미터 상관계수", C['orange'], 10, True))
        self.corr_label = mk_label("외인콜+0.74  다이버전스+0.68  프로그램+0.66  OFI+0.62", C['text2'], 9)
        lay.addWidget(self.corr_label)

    def update_data(self, price, preds, params):
        self.lbl_price.setText(f"{price:.2f}")

        # 앙상블 방향
        ups = sum(1 for v in preds.values() if v['signal'] == 1)
        dns = sum(1 for v in preds.values() if v['signal'] == -1)
        if ups >= 4:
            self.lbl_signal.setText("▲ 매수")
            self.lbl_signal.setStyleSheet(f"color:{C['green']};font-size:16px;font-weight:bold;")
        elif dns >= 4:
            self.lbl_signal.setText("▼ 매도")
            self.lbl_signal.setStyleSheet(f"color:{C['red']};font-size:16px;font-weight:bold;")
        else:
            self.lbl_signal.setText("— 관망")
            self.lbl_signal.setStyleSheet(f"color:{C['text2']};font-size:16px;font-weight:bold;")

        # 호라이즌 카드
        for hname, pred in preds.items():
            if hname not in self._hz_labels:
                continue
            frame, arr, pct = self._hz_labels[hname]
            if pred['signal'] == 1:
                col = C['green']
                arr.setText("▲")
                pct.setText(f"{pred['up']*100:.1f}%")
                frame.setStyleSheet(
                    f"QFrame{{background:#0D2818;border:1px solid {C['green']};border-radius:6px;}}")
            elif pred['signal'] == -1:
                col = C['red']
                arr.setText("▼")
                pct.setText(f"{pred['dn']*100:.1f}%")
                frame.setStyleSheet(
                    f"QFrame{{background:#2D0D0D;border:1px solid {C['red']};border-radius:6px;}}")
            else:
                col = C['text2']
                arr.setText("—")
                pct.setText("횡보")
                frame.setStyleSheet(
                    f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};border-radius:6px;}}")
            arr.setStyleSheet(f"color:{col};font-size:22px;font-weight:bold;")
            pct.setStyleSheet(f"color:{col};font-size:10px;")

        # SHAP 바
        for name, val in params.items():
            if name in self._param_bars:
                self._param_bars[name].setValue(int(val * 100))
                self._param_vals[name].setText(f"{val*100:.1f}%")


# ────────────────────────────────────────────────────────────
# 패널 2: 다이버전스 지수 + 포지션 매트릭스
# ────────────────────────────────────────────────────────────
class DivergencePanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lay.addWidget(mk_label("외인-개인 다이버전스 지수 (역발상 핵심 신호)", C['orange'], 10, True))

        # 바이어스 미터
        for label, attr_prefix, lcol, rcol, ltext, rtext in [
            ("개인 방향", "rt", C['green'], C['red'], "풋↑", "콜↑"),
            ("외인 방향", "fi", C['red'],   C['green'], "풋↑", "콜↑"),
        ]:
            row = QHBoxLayout()
            row.addWidget(mk_label(label, C['text2'], 9))
            row.addWidget(mk_label(ltext, lcol, 9))
            bar_l = mk_prog(lcol, 12)
            bar_r = mk_prog(rcol, 12)
            setattr(self, f"{attr_prefix}_put_bar", bar_l)
            setattr(self, f"{attr_prefix}_call_bar", bar_r)
            mid_frame = QFrame()
            mid_lay = QHBoxLayout(mid_frame)
            mid_lay.setContentsMargins(0, 0, 0, 0)
            mid_lay.setSpacing(1)
            mid_lay.addWidget(bar_l)
            mid_lay.addWidget(bar_r)
            row.addWidget(mid_frame, 3)
            row.addWidget(mk_label(rtext, rcol, 9))
            lay.addLayout(row)

        lay.addWidget(mk_sep())

        # 포지션 카드 (2×4 그리드)
        lay.addWidget(mk_label("투자자 포지션 매트릭스", C['blue'], 10, True))
        pos_grid = QGridLayout()
        pos_grid.setSpacing(4)
        positions = [
            ("개인 콜매수",   "rt_call",   C['red']),
            ("개인 풋매수",   "rt_put",    C['green']),
            ("개인 양매수",   "rt_strd",   C['text2']),
            ("역발상 신호",   "contrarian",C['orange']),
            ("외인 콜순매수", "fi_call",   C['green']),
            ("외인 풋순매수", "fi_put",    C['red']),
            ("외인 양매도",   "fi_strangle",C['text2']),
            ("다이버전스",    "div_score", C['orange']),
        ]
        for i, (title, attr, col) in enumerate(positions):
            f = QFrame()
            f.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};"
                f"border-radius:5px;padding:4px;}}"
            )
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6, 4, 6, 4)
            fl.setSpacing(1)
            t = mk_label(title, C['text2'], 9)
            v = mk_val_label("——", col, 13)
            fl.addWidget(t)
            fl.addWidget(v)
            setattr(self, f"pos_{attr}_val", v)
            pos_grid.addWidget(f, i // 4, i % 4)
        lay.addLayout(pos_grid)

        lay.addWidget(mk_sep())
        # 옵션 구간별 거래량
        lay.addWidget(mk_label("옵션 구간별 거래량 — 외인/개인/기관 분리 (ITM·ATM·OTM)", C['cyan'], 10, True))
        zone_lay = QHBoxLayout()
        for zone in ["ITM", "ATM", "OTM"]:
            zf = QFrame()
            zf.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;")
            zfl = QVBoxLayout(zf)
            zfl.setContentsMargins(6, 6, 6, 6)
            zfl.addWidget(mk_label(zone, C['text'], 11, True, Qt.AlignCenter))
            for inv, col in [("외인",C['blue']),("개인",C['red']),("기관",C['purple'])]:
                hr = QHBoxLayout()
                hr.addWidget(mk_label(inv, C['text2'], 9))
                b = mk_prog(col, 7)
                b.setValue(random.randint(20, 80))
                hr.addWidget(b, 2)
                vl = mk_label("—%", col, 9)
                setattr(self, f"oz_{zone}_{inv}", (b, vl))
                hr.addWidget(vl)
                zfl.addLayout(hr)
            zone_lay.addWidget(zf)
        lay.addLayout(zone_lay)

    def update_data(self, div):
        self.rt_put_bar.setValue(int(max(0, -div['rt_bias']) * 50))
        self.rt_call_bar.setValue(int(max(0, div['rt_bias']) * 50))
        self.fi_put_bar.setValue(int(max(0, -div['fi_bias']) * 50))
        self.fi_call_bar.setValue(int(max(0, div['fi_bias']) * 50))

        self.pos_rt_call_val.setText(f"{div.get('rt_call',0):,}")
        self.pos_rt_put_val.setText(f"{div.get('rt_put',0):,}")
        self.pos_rt_strd_val.setText(f"{div.get('rt_strd',0):,}")
        contrarian = div.get('contrarian','중립')
        col = C['red'] if '하락' in contrarian else C['green'] if '상승' in contrarian else C['text2']
        self.pos_contrarian_val.setText(contrarian)
        self.pos_contrarian_val.setStyleSheet(f"color:{col};font-size:12px;font-weight:bold;")

        score = div.get('div_score', 0)
        col2  = C['green'] if score > 10 else C['red'] if score < -10 else C['text2']
        self.pos_div_score_val.setText(f"{score:+.0f}")
        self.pos_div_score_val.setStyleSheet(f"color:{col2};font-size:13px;font-weight:bold;")


# ────────────────────────────────────────────────────────────
# 패널 3: 동적 피처 관리 (SHAP)
# ────────────────────────────────────────────────────────────
class FeaturePanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lay.addWidget(mk_label("채용 파라미터 TOP 6 — SHAP 기여도 실시간", C['purple'], 10, True))

        # 고정 CORE
        lay.addWidget(mk_label("▐ 고정 CORE 3개 — 절대 교체 불가", C['cyan'], 9, True))
        self.core_rows = []
        for i, name in enumerate(["CVD 다이버전스", "VWAP 위치", "OFI 불균형"]):
            row = QHBoxLayout()
            medal_colors = [C['orange'], "#888", "#639922"]
            rank = mk_badge(str(i+1), medal_colors[i], "#fff", 9)
            badge = mk_badge("CORE", C['cyan'], C['bg'], 8)
            nlab  = mk_label(name, C['text'], 10)
            bar   = mk_prog(C['cyan'], 10)
            bar.setValue(random.randint(55, 90))
            vlab  = mk_val_label("—%", C['cyan'], 10)
            slab  = mk_label("안정", C['green'], 9)
            row.addWidget(rank)
            row.addWidget(badge)
            row.addWidget(nlab, 2)
            row.addWidget(bar, 3)
            row.addWidget(vlab)
            row.addWidget(slab)
            lay.addLayout(row)
            self.core_rows.append((bar, vlab))

        lay.addWidget(mk_sep())

        # 동적 SHAP
        lay.addWidget(mk_label("▐ 동적 SHAP TOP 3 — 매일 심사", C['purple'], 9, True))
        # 쿨다운
        cdlay = QHBoxLayout()
        cdlay.addWidget(mk_label("쿨다운:", C['text2'], 9))
        self.cooldown_bar = mk_prog(C['orange'], 6)
        self.cooldown_bar.setValue(0)
        cdlay.addWidget(self.cooldown_bar, 3)
        self.cooldown_lbl = mk_label("없음", C['text2'], 9)
        cdlay.addWidget(self.cooldown_lbl)
        lay.addLayout(cdlay)

        self.dynamic_rows = []
        for i in range(3):
            row = QHBoxLayout()
            rank = mk_badge("—", C['bg3'], C['purple'], 9)
            badge = mk_badge("SHAP", C['bg3'], C['purple'], 8)
            nlab  = mk_label("——", C['text'], 10)
            bar   = mk_prog(C['purple'], 10)
            vlab  = mk_val_label("—%", C['purple'], 10)
            slab  = mk_label("——", C['text2'], 9)
            row.addWidget(rank)
            row.addWidget(badge)
            row.addWidget(nlab, 2)
            row.addWidget(bar, 3)
            row.addWidget(vlab)
            row.addWidget(slab)
            lay.addLayout(row)
            self.dynamic_rows.append((rank, nlab, bar, vlab, slab))

        lay.addWidget(mk_sep())

        # SHAP 전체 가로 차트 (간이)
        lay.addWidget(mk_label("전체 피처 순위 (SHAP 200분 누적)", C['blue'], 9, True))
        self.rank_labels = []
        all_params = [
            ("외인 콜순매수", C['green']),("CVD 다이버전스", C['cyan']),
            ("다이버전스",    C['orange']),("VWAP 위치",      C['cyan']),
            ("프로그램 비차익",C['purple']),("OFI 불균형",    C['cyan']),
        ]
        for name, col in all_params:
            r = QHBoxLayout()
            nl = mk_label(name[:8], C['text2'], 9)
            nl.setFixedWidth(70)
            b  = mk_prog(col, 8)
            b.setValue(random.randint(20, 85))
            vl = mk_val_label("—%", col, 9)
            vl.setFixedWidth(34)
            r.addWidget(nl)
            r.addWidget(b, 3)
            r.addWidget(vl)
            lay.addLayout(r)
            self.rank_labels.append((b, vl))

        lay.addWidget(mk_sep())
        # 교체 이력
        lay.addWidget(mk_label("교체 이력", C['text2'], 9, True))
        self.change_log = QTextEdit()
        self.change_log.setReadOnly(True)
        self.change_log.setFixedHeight(55)
        self.change_log.setStyleSheet(
            f"background:{C['bg']};color:{C['text2']};border:1px solid {C['border']};"
            f"font-size:9px;font-family:Consolas;"
        )
        self.change_log.setText(
            "01-12  교체  베이시스 → 프로그램비차익  +1.4%  [성공]\n"
            "01-09  교체  PCR → 다이버전스지수        +2.1%  [성공]\n"
            "01-05  교체  원달러 → 외인콜순매수       +0.8%  [성공]"
        )
        lay.addWidget(self.change_log)

    def update_shap(self, core_vals, dynamic_items, rank_vals):
        for (bar, vlab), val in zip(self.core_rows, core_vals):
            bar.setValue(int(val*100))
            vlab.setText(f"{val*100:.1f}%")

        for i, (rank, nlab, bar, vlab, slab) in enumerate(self.dynamic_rows):
            if i < len(dynamic_items):
                d = dynamic_items[i]
                rank.setText(str(d.get('rank', i+1)))
                nlab.setText(d.get('name','——'))
                bar.setValue(int(d.get('shap',0)*100))
                vlab.setText(f"{d.get('shap',0)*100:.1f}%")
                slab.setText(d.get('status','유지'))

        for (b, vl), val in zip(self.rank_labels, rank_vals):
            b.setValue(int(val*100))
            vl.setText(f"{val*100:.0f}%")


# ────────────────────────────────────────────────────────────
# 패널 4: 청산 관리 패널
# ────────────────────────────────────────────────────────────
class ExitPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # 상단: 포지션 상태
        lay.addWidget(mk_label("포지션 청산 관리", C['red'], 10, True))
        top = QGridLayout()
        top.setSpacing(6)
        info = [
            ("진입가", "entry_price", "——"),
            ("현재가", "cur_price", "——"),
            ("미실현 손익", "unreal_pnl", "——"),
            ("보유 시간", "hold_time", "——"),
        ]
        for i, (lbl, attr, init) in enumerate(info):
            col = i % 2
            row_i = i // 2
            f = QFrame()
            f.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6, 3, 6, 3)
            fl.addWidget(mk_label(lbl, C['text2'], 9))
            vl = mk_val_label(init, C['text'], 13)
            setattr(self, attr, vl)
            fl.addWidget(vl)
            top.addWidget(f, row_i, col)
        lay.addLayout(top)

        lay.addWidget(mk_sep())

        # 가격 레벨
        lay.addWidget(mk_label("가격 구조 (손절 → 목표)", C['text2'], 9, True))
        levels = [
            ("하드 손절",    "hard_stop",  C['red'],    "●"),
            ("구조적 손절",  "struct_stop",C['red'],    "●"),
            ("트레일링 스톱","trail_stop", C['orange'], "●"),
            ("본전 (진입가)","breakeven",  C['text2'],  "●"),
            ("1차 목표 33%","target1",    C['green'],  "●"),
            ("2차 목표 33%","target2",    C['green'],  "●"),
            ("3차 목표 34%","target3",    "#085041",   "●"),
        ]
        for lbl, attr, col, dot in levels:
            r = QHBoxLayout()
            r.addWidget(mk_label(f"{dot} {lbl}", col, 9))
            vl = mk_val_label("——.——", col, 10)
            setattr(self, f"lv_{attr}", vl)
            r.addWidget(vl)
            lay.addLayout(r)

        lay.addWidget(mk_sep())

        # 청산 트리거 모니터
        lay.addWidget(mk_label("청산 트리거 모니터 (우선순위 감시)", C['orange'], 9, True))
        triggers = [
            ("1", "하드 스톱 초과",     "hard_trig"),
            ("1", "앙상블 반대 신호",   "signal_trig"),
            ("1", "CVD+VWAP 동시 역전", "cvd_trig"),
            ("2", "SHAP 피처 붕괴",     "shap_trig"),
            ("2", "옵션 플로우 역전",   "opt_trig"),
            ("2", "트레일링 스톱",      "trail_trig"),
            ("3", "1차 목표 도달",      "t1_trig"),
            ("3", "시간 청산 (15:10)", "time_trig"),
        ]
        for pri, name, attr in triggers:
            r = QHBoxLayout()
            pri_col = C['red'] if pri == "1" else C['orange'] if pri == "2" else C['blue']
            r.addWidget(mk_badge(pri, pri_col, "#fff", 8))
            r.addWidget(mk_label(name, C['text'], 9), 2)
            st = mk_badge("감시중", C['bg3'], C['text2'], 8)
            setattr(self, f"st_{attr}", st)
            r.addWidget(st)
            lay.addLayout(r)

        lay.addWidget(mk_sep())

        # 부분 청산 진행
        lay.addWidget(mk_label("부분 청산 (33% · 33% · 34%)", C['green'], 9, True))
        self.partial_bars = []
        for i, (lbl, pct) in enumerate([("1차", 33), ("2차", 33), ("3차", 34)]):
            r = QHBoxLayout()
            r.addWidget(mk_label(f"{lbl} ({pct}%)", C['text2'], 9))
            b = mk_prog(C['green'], 8)
            r.addWidget(b, 3)
            st = mk_label("대기", C['text2'], 9)
            r.addWidget(st)
            lay.addLayout(r)
            self.partial_bars.append((b, st))

        # 수동 청산 버튼
        btn_lay = QHBoxLayout()
        for label, pct, col in [("33% 청산", 33, C['green']),
                                  ("50% 청산", 50, C['orange']),
                                  ("전량 청산", 100, C['red'])]:
            btn = QPushButton(label)
            btn.setStyleSheet(
                f"QPushButton{{background:{C['bg3']};color:{col};"
                f"border:1px solid {col};border-radius:4px;padding:4px 8px;}}"
                f"QPushButton:hover{{background:{col};color:#000;}}"
            )
            btn_lay.addWidget(btn)
        lay.addLayout(btn_lay)

    def update_data(self, pos_data):
        if not pos_data:
            return
        entry = pos_data.get('entry', 388.50)
        cur   = pos_data.get('current', 388.50)
        pnl   = (cur - entry) * pos_data.get('qty', 5)
        atr   = pos_data.get('atr', 1.8)

        self.entry_price.setText(f"{entry:.2f}")
        self.cur_price.setText(f"{cur:.2f}")

        col = C['green'] if pnl >= 0 else C['red']
        self.unreal_pnl.setText(f"{pnl:+,.0f}원")
        self.unreal_pnl.setStyleSheet(f"color:{col};font-size:13px;font-weight:bold;")

        # 가격 레벨 업데이트
        self.lv_hard_stop.setText(f"{entry - atr*1.5:.2f}")
        self.lv_struct_stop.setText(f"{entry - atr*1.2:.2f}")
        self.lv_trail_stop.setText(f"{entry:.2f}")
        self.lv_breakeven.setText(f"{entry:.2f}")
        self.lv_target1.setText(f"{entry + atr*1.0:.2f}")
        self.lv_target2.setText(f"{entry + atr*1.5:.2f}")
        self.lv_target3.setText(f"{entry + atr*2.5:.2f}")


# ────────────────────────────────────────────────────────────
# 패널 5: 진입 관리 패널
# ────────────────────────────────────────────────────────────
class EntryPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lay.addWidget(mk_label("진입 관리 패널 — 하이브리드 시스템", C['green'], 10, True))

        # 모드 선택
        mode_lay = QHBoxLayout()
        self.mode_btns = {}
        for mode, label in [("auto","자동 진입"), ("hybrid","하이브리드 (권장)"), ("manual","수동 진입")]:
            btn = QPushButton(label)
            col = C['green'] if mode == "hybrid" else C['text2']
            btn.setStyleSheet(
                f"QPushButton{{background:{C['bg2'] if mode=='hybrid' else C['bg3']};"
                f"color:{col};border:{'2' if mode=='hybrid' else '1'}px solid {col};"
                f"border-radius:4px;padding:5px 8px;font-size:10px;}}"
            )
            btn.clicked.connect(lambda checked, m=mode: self._set_mode(m))
            self.mode_btns[mode] = btn
            mode_lay.addWidget(btn)
        lay.addLayout(mode_lay)

        self.mode_desc = mk_label(
            "하이브리드: 신뢰도 70%+ + 외인 일치 → 자동 / 58~70% → 알림 후 수동",
            C['blue'], 9
        )
        lay.addWidget(self.mode_desc)
        lay.addWidget(mk_sep())

        # 앙상블 + 신뢰도
        info_lay = QGridLayout()
        info_lay.setSpacing(4)
        kv = [("앙상블 신호","signal","——"),("신뢰도","conf","——"),
              ("진입 등급","grade","——"),("산출 수량","qty","——")]
        for i, (lbl, attr, init) in enumerate(kv):
            f = QFrame()
            f.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6,3,6,3)
            fl.addWidget(mk_label(lbl, C['text2'], 9))
            vl = mk_val_label(init, C['text'], 13)
            setattr(self, f"e_{attr}", vl)
            fl.addWidget(vl)
            info_lay.addWidget(f, i//2, i%2)
        lay.addLayout(info_lay)
        lay.addWidget(mk_sep())

        # 9개 체크리스트
        lay.addWidget(mk_label("진입 전 체크리스트 (Pre-flight 9개)", C['orange'], 9, True))
        checks = [
            ("앙상블 신호 방향","signal_chk"),
            ("신뢰도 ≥ 58%",   "conf_chk"),
            ("VWAP 위치 확인", "vwap_chk"),
            ("CVD 방향 일치",  "cvd_chk"),
            ("OFI 압력 확인",  "ofi_chk"),
            ("외인 방향 일치", "fi_chk"),
            ("직전 봉 확인",   "candle_chk"),
            ("시간 필터 통과", "time_chk"),
            ("리스크 한도 여유","risk_chk"),
        ]
        self.check_labels = {}
        for i, (name, attr) in enumerate(checks):
            r = QHBoxLayout()
            icon = mk_badge("—", C['bg3'], C['text2'], 8)
            icon.setFixedWidth(20)
            nl   = mk_label(name, C['text'], 9)
            vl   = mk_val_label("——", C['text2'], 9)
            r.addWidget(icon)
            r.addWidget(nl, 2)
            r.addWidget(vl)
            self.check_labels[attr] = (icon, vl)
            lay.addLayout(r)

        lay.addWidget(mk_sep())

        # 진입 버튼
        lay.addWidget(mk_label("진입 실행", C['text2'], 9, True))
        self.entry_alert = mk_label("신호 대기 중...", C['text2'], 10)
        self.entry_alert.setStyleSheet(
            f"background:{C['bg3']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:5px;color:{C['text2']};font-size:10px;"
        )
        lay.addWidget(self.entry_alert)

        btn_lay = QHBoxLayout()
        self.buy_btn  = QPushButton("▲ 매수 진입 (Long)")
        self.sell_btn = QPushButton("▼ 매도 진입 (Short)")
        self.skip_btn = QPushButton("신호 스킵")

        self.buy_btn.setStyleSheet(
            f"QPushButton{{background:#0D2818;color:{C['green']};"
            f"border:1px solid {C['green']};border-radius:4px;padding:7px;"
            f"font-size:11px;font-weight:bold;}}"
            f"QPushButton:hover{{background:{C['green']};color:#000;}}"
        )
        self.sell_btn.setStyleSheet(
            f"QPushButton{{background:#2D0D0D;color:{C['red']};"
            f"border:1px solid {C['red']};border-radius:4px;padding:7px;"
            f"font-size:11px;font-weight:bold;}}"
            f"QPushButton:hover{{background:{C['red']};color:#000;}}"
        )
        self.skip_btn.setStyleSheet(
            f"QPushButton{{background:{C['bg3']};color:{C['text2']};"
            f"border:1px solid {C['border']};border-radius:4px;padding:7px;}}"
        )
        btn_lay.addWidget(self.buy_btn, 2)
        btn_lay.addWidget(self.sell_btn, 2)
        btn_lay.addWidget(self.skip_btn, 1)
        lay.addLayout(btn_lay)

        # 당일 통계
        lay.addWidget(mk_sep())
        lay.addWidget(mk_label("당일 진입 통계", C['text2'], 9, True))
        self.stat_label = mk_label("진입 0회 | 자동 0 | 수동 0 | 승률 —% | 손익 ——pt", C['text2'], 9)
        lay.addWidget(self.stat_label)

    def _set_mode(self, mode):
        for m, btn in self.mode_btns.items():
            col = C['green'] if m == mode else C['text2']
            bw  = "2px" if m == mode else "1px"
            btn.setStyleSheet(
                f"QPushButton{{background:{C['bg2'] if m==mode else C['bg3']};"
                f"color:{col};border:{bw} solid {col};"
                f"border-radius:4px;padding:5px 8px;font-size:10px;}}"
            )

    def update_data(self, signal, conf, grade, checks):
        col = C['green'] if signal == "매수" else C['red'] if signal == "매도" else C['text2']
        self.e_signal.setText(signal)
        self.e_signal.setStyleSheet(f"color:{col};font-size:13px;font-weight:bold;")
        self.e_conf.setText(f"{conf*100:.1f}%")
        self.e_conf.setStyleSheet(
            f"color:{C['green'] if conf>=0.7 else C['orange'] if conf>=0.58 else C['red']};"
            f"font-size:13px;font-weight:bold;"
        )

        grade_colors = {"A": C['cyan'], "B": C['blue'], "C": C['orange'], "X": C['red']}
        self.e_grade.setText(f"{grade}급")
        self.e_grade.setStyleSheet(f"color:{grade_colors.get(grade,C['text'])};"
                                    f"font-size:13px;font-weight:bold;")

        for attr, (icon, vl) in self.check_labels.items():
            passed = checks.get(attr, False)
            icon.setText("V" if passed else "X")
            icon.setStyleSheet(
                f"background:{C['green'] if passed else C['red']};color:#fff;"
                f"border-radius:3px;font-size:8px;font-weight:bold;padding:1px 4px;"
            )

        if signal == "매수":
            self.entry_alert.setStyleSheet(
                f"background:#0D2818;border:1px solid {C['green']};"
                f"border-radius:4px;padding:5px;color:{C['green']};font-size:10px;"
            )
            self.entry_alert.setText(f"▲ 매수 신호 {grade}급 — {conf*100:.1f}% 신뢰도")
        elif signal == "매도":
            self.entry_alert.setStyleSheet(
                f"background:#2D0D0D;border:1px solid {C['red']};"
                f"border-radius:4px;padding:5px;color:{C['red']};font-size:10px;"
            )
            self.entry_alert.setText(f"▼ 매도 신호 {grade}급 — {conf*100:.1f}% 신뢰도")
        else:
            self.entry_alert.setStyleSheet(
                f"background:{C['bg3']};border:1px solid {C['border']};"
                f"border-radius:4px;padding:5px;color:{C['text2']};font-size:10px;"
            )
            self.entry_alert.setText("— 관망 | 신호 대기 중")


# ────────────────────────────────────────────────────────────
# 패널 6: 알파 리서치 봇
# ────────────────────────────────────────────────────────────
class AlphaPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lay.addWidget(mk_label("알파 리서치 봇 — 자율 진화 시스템", C['yellow'], 10, True))

        # 카운터
        ctr = QHBoxLayout()
        for lbl, val, col in [("검색 논문",147,C['text']),
                               ("고품질 후보",8,C['green']),
                               ("검토 중",3,C['orange']),
                               ("통합 완료",12,C['blue'])]:
            f = QFrame()
            f.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6,3,6,3)
            fl.addWidget(mk_label(lbl, C['text2'], 9, align=Qt.AlignCenter))
            fl.addWidget(mk_val_label(str(val), col, 16, align=Qt.AlignCenter))
            ctr.addWidget(f)
        lay.addLayout(ctr)
        lay.addWidget(mk_sep())

        # 신규 알림 배너
        self.alert_box = QLabel("🔬 [대기] 알파 리서치 봇 활성 — 신규 발견 시 알림")
        self.alert_box.setWordWrap(True)
        self.alert_box.setStyleSheet(
            f"background:{C['bg3']};color:{C['text2']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:6px;font-size:10px;"
        )
        lay.addWidget(self.alert_box)
        lay.addWidget(mk_sep())

        # 논문 TOP 5
        lay.addWidget(mk_label("신규 알파 후보 TOP (AI 평가 순위)", C['blue'], 9, True))
        papers = [
            ("Liquidity-Adjusted OFI for KOSPI",     "JoF",  95, "즉시"),
            ("Transformer Multi-Horizon Forecasting", "arXiv",87, "즉시"),
            ("Retail Investor Herding in Options",    "한국", 82, "즉시"),
            ("PPO Reinforcement Learning Sizing",     "SSRN", 78, "보통"),
            ("Volatility Surface Weekly Expiry",      "arXiv",71, "보통"),
        ]
        for i, (title, src, score, pri) in enumerate(papers):
            f = QFrame()
            f.setStyleSheet(
                f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;"
            )
            fl = QVBoxLayout(f)
            fl.setContentsMargins(8, 5, 8, 5)
            fl.setSpacing(3)
            head = QHBoxLayout()
            rank_col = ["#BA7517","#888","#639922",C['text2'],C['text2']][i]
            head.addWidget(mk_badge(str(i+1), rank_col, "#fff", 8))
            src_map = {"JoF":C['green'],"arXiv":C['orange'],"한국":C['red'],"SSRN":C['purple']}
            head.addWidget(mk_badge(src, src_map.get(src,C['blue']), "#fff", 8))
            head.addWidget(mk_label(title, C['text'], 10), 2)
            sc_col = C['green'] if score >= 90 else C['orange'] if score >= 80 else C['text2']
            head.addWidget(mk_label(f"{score}점", sc_col, 9))
            pri_col = C['red'] if pri == "즉시" else C['orange']
            head.addWidget(mk_badge(pri, pri_col, "#fff", 8))
            fl.addLayout(head)

            sb = mk_prog(sc_col, 5)
            sb.setValue(score)
            fl.addWidget(sb)

            btn_row = QHBoxLayout()
            for blbl, bcol in [("코드생성",C['cyan']),("백테스트",C['blue']),("기각",C['red'])]:
                b = QPushButton(blbl)
                b.setStyleSheet(
                    f"background:{C['bg3']};color:{bcol};border:1px solid {bcol};"
                    f"border-radius:3px;padding:2px 8px;font-size:9px;"
                )
                btn_row.addWidget(b)
            btn_row.addStretch()
            fl.addLayout(btn_row)
            lay.addWidget(f)

        lay.addWidget(mk_sep())

        # 검색 일정
        lay.addWidget(mk_label("검색 일정", C['text2'], 9, True))
        for cycle, time_s, src in [
            ("일간","09:00","헤지펀드 블로그·뉴스"),
            ("주간","월 08:30","arXiv·SSRN"),
            ("월간","1일 08:00","전체 학술지 정밀 평가"),
        ]:
            r = QHBoxLayout()
            r.addWidget(mk_badge(cycle, C['blue'], "#fff", 8))
            r.addWidget(mk_label(time_s, C['text2'], 9))
            r.addWidget(mk_label(src, C['text'], 9), 2)
            lay.addLayout(r)

    def show_alert(self, title, score):
        self.alert_box.setText(
            f"⚡ 긴급 — ★★★★★ 신규 알파 발견 ({score}점)\n"
            f"「{title}」 → 코드 자동 생성 권장"
        )
        self.alert_box.setStyleSheet(
            f"background:#2D0D0D;color:{C['red']};border:1px solid {C['red']};"
            f"border-radius:4px;padding:6px;font-size:10px;font-weight:bold;"
        )


# ────────────────────────────────────────────────────────────
# 패널 7: 5층 로그 시스템
# ────────────────────────────────────────────────────────────
class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.tabs = QTabWidget()
        log_configs = [
            ("1 시스템",  C['blue'],   "all"),
            ("2 경보 ⚠",  C['orange'], "warn"),
            ("3 주문/체결",C['green'],  "order"),
            ("4 손익 PnL", C['cyan'],   "pnl"),
            ("5 모델 AI",  C['purple'], "model"),
        ]
        self.log_boxes = {}
        for title, col, key in log_configs:
            page = QWidget()
            pl   = QVBoxLayout(page)
            pl.setContentsMargins(4, 4, 4, 4)

            # 상단 메트릭 (창3, 4, 5 전용)
            if key == "order":
                mrow = QHBoxLayout()
                for mk_lbl, mk_val in [("평균 슬리피지","1.3틱"),("최대 슬리피지","3.8틱"),
                                        ("체결률","85.7%"),("평균 지연","142ms")]:
                    mf = QFrame()
                    mf.setStyleSheet(f"background:{C['bg3']};border:1px solid {C['border']};border-radius:3px;")
                    mfl = QVBoxLayout(mf); mfl.setContentsMargins(5,2,5,2)
                    mfl.addWidget(mk_label(mk_lbl, C['text2'], 8, align=Qt.AlignCenter))
                    mfl.addWidget(mk_val_label(mk_val, col, 11, align=Qt.AlignCenter))
                    mrow.addWidget(mf)
                pl.addLayout(mrow)

            elif key == "pnl":
                mrow = QHBoxLayout()
                for mk_lbl, mk_val, mc in [("미실현 손익","+12,000원",C['green']),
                                             ("일일 누적","+87,500원",C['green']),
                                             ("VaR 95%","-87,500원",C['orange'])]:
                    mf = QFrame()
                    mf.setStyleSheet(f"background:{C['bg3']};border:1px solid {C['border']};border-radius:3px;")
                    mfl = QVBoxLayout(mf); mfl.setContentsMargins(5,2,5,2)
                    mfl.addWidget(mk_label(mk_lbl, C['text2'], 8, align=Qt.AlignCenter))
                    pb = mk_prog(mc, 4)
                    pb.setValue(60)
                    mfl.addWidget(mk_val_label(mk_val, mc, 11, align=Qt.AlignCenter))
                    mfl.addWidget(pb)
                    mrow.addWidget(mf)
                pl.addLayout(mrow)

            elif key == "model":
                mrow = QHBoxLayout()
                for mk_lbl, mk_val, mc in [("정확도(50분)","61.4%",C['green']),
                                             ("SGD 비중","34%",C['purple']),
                                             ("자가학습","● 활성",C['green'])]:
                    mf = QFrame()
                    mf.setStyleSheet(f"background:{C['bg3']};border:1px solid {C['border']};border-radius:3px;")
                    mfl = QVBoxLayout(mf); mfl.setContentsMargins(5,2,5,2)
                    mfl.addWidget(mk_label(mk_lbl, C['text2'], 8, align=Qt.AlignCenter))
                    mfl.addWidget(mk_val_label(mk_val, mc, 11, align=Qt.AlignCenter))
                    mrow.addWidget(mf)
                pl.addLayout(mrow)

            tb = QTextEdit()
            tb.setReadOnly(True)
            tb.setStyleSheet(
                f"background:{C['bg']};color:{C['text']};border:none;"
                f"font-family:Consolas,D2Coding,monospace;font-size:10px;"
            )
            pl.addWidget(tb)
            self.log_boxes[key] = tb
            self.tabs.addTab(page, title)
            # 탭 색상
            self.tabs.tabBar().setTabTextColor(
                self.tabs.count()-1, QColor(col)
            )

        lay.addWidget(self.tabs)

    def append(self, key, tag, msg, val=""):
        tb = self.log_boxes.get(key)
        if not tb:
            return
        ts  = datetime.now().strftime("%H:%M:%S")
        TAG_COLORS = {
            "INFO":   C['blue'],   "DEBUG": C['text2'], "SYSTEM": C['purple'],
            "WARN":   C['orange'], "ERROR": C['red'],   "CRITICAL": C['red'],
            "TRADE":  C['green'],  "FILL":  C['green'], "PENDING": C['orange'],
            "CANCEL": C['red'],    "PNL":   C['cyan'],  "MODEL":  C['purple'],
            "SHAP":   C['yellow'],
        }
        col = TAG_COLORS.get(tag, C['text2'])
        line = (
            f'<span style="color:{C["text2"]}">[{ts}]</span> '
            f'<span style="color:{col};font-weight:bold">[{tag}]</span> '
            f'<span style="color:{C["text"]}">{msg}</span>'
        )
        if val:
            line += f' <span style="color:{C["text2"]};font-size:9px;">{val}</span>'

        # 경보창에도 WARNING 이상 복사
        if key == "all" and tag in ("WARN", "ERROR", "CRITICAL"):
            self.append("warn", tag, msg, val)

        tb.append(line)
        tb.verticalScrollBar().setValue(tb.verticalScrollBar().maximum())


# ────────────────────────────────────────────────────────────
# 메인 윈도우
# ────────────────────────────────────────────────────────────
class MireukDashboard(QMainWindow):
    """미륵이 v7.0 풀 대시보드"""

    def __init__(self, kiwoom=None):
        super().__init__()
        self.kiwoom = kiwoom
        # ── 해상도 감지 (UI 빌드 전에 반드시 먼저) ──────────────
        S.init()
        self.setWindowTitle("미륵이 v7.0  |  KOSPI 200 선물 예측 시스템")
        self.resize(S.p(1680), S.p(1000))
        self.setStyleSheet(make_style())
        self._build_ui()
        self._sim_timer = None
        if kiwoom is None:
            self._start_sim_timer()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 6, 8, 6)
        root.setSpacing(6)

        # ── 상단 헤더 ──────────────────────────────────────────
        header = QHBoxLayout()
        title = mk_label("⚡ 미륵이  v7.0", C['text'], 16, True)

        # ── 실시간 현재가 (키움 API 연동 핵심) ──────────────────
        self.lbl_realtime_price = mk_label("——.——", C['cyan'], 22, True)
        self.lbl_price_change   = mk_label("——", C['text2'], 14, True)
        self.lbl_futures_code   = mk_label("F202606", C['text2'], 11)

        price_box = QHBoxLayout()
        price_box.setSpacing(S.p(6))
        price_box.addWidget(self.lbl_futures_code)
        price_box.addWidget(self.lbl_realtime_price)
        price_box.addWidget(self.lbl_price_change)

        self.lbl_time   = mk_label("——:——:——", C['text2'], 12)
        self.lbl_regime = mk_badge("NEUTRAL", C['orange'], "#fff", 11)
        self.lbl_cycle  = mk_badge("목위클리 D-2", C['purple'], "#fff", 11)
        self.lbl_gamma  = mk_badge("감마스퀴즈", C['orange'], "#fff", 11)
        self.lbl_pos    = mk_badge("FLAT", C['text2'], "#fff", 11)
        self.lbl_scale  = mk_label(S.info(),    C['text2'], 9, align=Qt.AlignRight)
        self.lbl_commit = mk_label(COMMIT_HASH, C['text2'], 9, align=Qt.AlignRight)
        res_box = QVBoxLayout()
        res_box.setSpacing(0)
        res_box.setContentsMargins(0, 0, 0, 0)
        res_box.addWidget(self.lbl_scale)
        res_box.addWidget(self.lbl_commit)

        header.addWidget(title)
        header.addLayout(price_box)
        header.addStretch()
        for w in [self.lbl_regime, self.lbl_cycle, self.lbl_gamma, self.lbl_pos]:
            header.addWidget(w)
        header.addLayout(res_box)
        header.addWidget(self.lbl_time)
        root.addLayout(header)
        root.addWidget(mk_sep())

        # ── 3열 메인 레이아웃 ──────────────────────────────────
        main_split = QSplitter(Qt.Horizontal)
        main_split.setHandleWidth(3)
        main_split.setStyleSheet(f"QSplitter::handle{{background:{C['border']};}}")

        # 좌측 컬럼
        left = QWidget()
        ll   = QVBoxLayout(left)
        ll.setContentsMargins(0,0,0,0)
        ll.setSpacing(6)
        self.pred_panel = PredictionPanel()
        ll.addWidget(card("멀티 호라이즌 예측 + 파라미터 분석",
                          self.pred_panel, C['blue']))

        # 중앙 컬럼 (탭)
        mid  = QWidget()
        ml   = QVBoxLayout(mid)
        ml.setContentsMargins(0,0,0,0)
        ml.setSpacing(6)
        mid_tabs = QTabWidget()
        mid_tabs.setStyleSheet(f"QTabBar::tab:selected{{border-bottom:2px solid {C['orange']};}}")

        self.div_panel  = DivergencePanel()
        self.feat_panel = FeaturePanel()
        self.exit_panel = ExitPanel()
        self.entry_panel= EntryPanel()
        self.alpha_panel= AlphaPanel()

        mid_tabs.addTab(self._wrap(self.div_panel),  "다이버전스 + 포지션")
        mid_tabs.addTab(self._wrap(self.feat_panel), "동적 피처 (SHAP)")
        mid_tabs.addTab(self._wrap(self.exit_panel), "청산 관리")
        mid_tabs.addTab(self._wrap(self.entry_panel),"진입 관리")
        mid_tabs.addTab(self._wrap(self.alpha_panel),"알파 리서치 봇")
        ml.addWidget(mid_tabs)

        # 우측: 5층 로그
        right = QWidget()
        rl    = QVBoxLayout(right)
        rl.setContentsMargins(0,0,0,0)
        self.log_panel = LogPanel()
        rl.addWidget(card("5층 모니터링 로그", self.log_panel, C['text2']))

        main_split.addWidget(left)
        main_split.addWidget(mid)
        main_split.addWidget(right)
        main_split.setSizes([520, 680, 440])
        root.addWidget(main_split, 1)

    def _wrap(self, widget):
        sc = QScrollArea()
        sc.setWidget(widget)
        sc.setWidgetResizable(True)
        sc.setFrameShape(QFrame.NoFrame)
        widget.setMinimumWidth(S.p(500))
        return sc

    def update_price(self, price: float, change: float = 0.0,
                     code: str = "F202606"):
        """
        키움 API 실시간 현재가 반영
        main.py 의 _on_candle_closed 콜백에서 호출

        Args:
            price:  현재가 (예: 1003.30)
            change: 전일 대비 등락 (예: +3.10)
            code:   선물 코드 (예: F202606, A0166000)
        """
        self._stop_sim_timer()
        self.lbl_realtime_price.setText(f"{price:,.2f}")
        col = C['green'] if change >= 0 else C['red']
        sign = "▲" if change >= 0 else "▼"
        self.lbl_price_change.setText(f"{sign} {abs(change):.2f}")
        self.lbl_price_change.setStyleSheet(
            f"font-size:{S.f(14)}px;color:{col};font-weight:bold;"
        )
        self.lbl_realtime_price.setStyleSheet(
            f"font-size:{S.f(22)}px;color:{col};font-weight:bold;"
        )
        self.lbl_futures_code.setText(code)
        # 예측 패널 현재가도 동기화
        self.pred_panel.lbl_price.setText(f"{price:,.2f}")
        self.pred_panel.lbl_price.setStyleSheet(
            f"font-size:{S.f(20)}px;color:{col};font-weight:bold;"
        )

    # ── 시뮬레이션 타이머 ──────────────────────────────────────
    def _start_sim_timer(self):
        self._tick = 0
        self._price = 388.50
        self._sim_timer = QTimer(self)
        self._sim_timer.timeout.connect(self._sim_tick)
        self._sim_timer.start(3000)
        self._sim_tick()

    def _stop_sim_timer(self):
        if self._sim_timer and self._sim_timer.isActive():
            self._sim_timer.stop()

    def _sim_tick(self):
        self._tick += 1
        self._price += random.gauss(0, 0.15)
        trend = random.choice([0.4, -0.4])

        # 시계
        now = datetime.now().strftime("%H:%M:%S")
        self.lbl_time.setText(now)

        # 예측 데이터
        HORIZONS = ["1분","3분","5분","10분","15분","30분"]
        preds = {}
        for h in HORIZONS:
            up = max(0.05, min(0.92, 0.30 + trend*0.22 + random.gauss(0,0.1)))
            dn = max(0.05, min(0.92, 1-up-0.15+random.gauss(0,0.05)))
            hd = max(0.03, 1-up-dn)
            sig = 1 if up>dn and up>hd else -1 if dn>up and dn>hd else 0
            preds[h] = {"up":up,"dn":dn,"hold":hd,"signal":sig}

        params = {
            "CVD 다이버전스": min(0.99, max(0.1, 0.183 + random.gauss(0,0.02))),
            "VWAP 위치":      min(0.99, max(0.1, 0.167 + random.gauss(0,0.02))),
            "OFI 불균형":     min(0.99, max(0.1, 0.142 + random.gauss(0,0.02))),
            "외인 콜순매수":  min(0.99, max(0.1, 0.128 + random.gauss(0,0.02))),
            "다이버전스 지수":min(0.99, max(0.1, 0.117 + random.gauss(0,0.02))),
            "프로그램 비차익":min(0.99, max(0.1, 0.108 + random.gauss(0,0.02))),
        }
        self.pred_panel.update_data(self._price, preds, params)

        # 다이버전스
        rt_bias = trend * 0.3 + random.gauss(0, 0.1)
        fi_bias = trend * 0.35 + random.gauss(0, 0.08)
        ct = "역발상 하락" if rt_bias > 0.4 else "역발상 상승" if rt_bias < -0.4 else "중립"
        div_data = {
            "rt_bias": rt_bias, "fi_bias": fi_bias,
            "rt_call": random.randint(2000,5000), "rt_put": random.randint(1500,4000),
            "rt_strd": random.randint(200,600),
            "contrarian": ct,
            "div_score":  (fi_bias - rt_bias) * 50,
        }
        self.div_panel.update_data(div_data)

        # 피처 관리
        cv = [random.uniform(0.55, 0.90) for _ in range(3)]
        dy = [
            {"rank":1,"name":"외인 콜순매수","shap":random.uniform(0.10,0.15),"status":"유지"},
            {"rank":2,"name":"다이버전스",   "shap":random.uniform(0.08,0.12),"status":"유지"},
            {"rank":3,"name":"프로그램 비차익","shap":random.uniform(0.07,0.11),"status":"유지"},
        ]
        rv = [random.uniform(0.20, 0.85) for _ in range(6)]
        self.feat_panel.update_shap(cv, dy, rv)

        # 포지션
        self.exit_panel.update_data({
            "entry": 388.50, "current": self._price,
            "qty": 5, "atr": 1.8
        })

        # 진입
        sig_map = {1:"매수", -1:"매도", 0:"관망"}
        ups = sum(1 for v in preds.values() if v['signal']==1)
        dns = sum(1 for v in preds.values() if v['signal']==-1)
        ens_sig = "매수" if ups>=4 else "매도" if dns>=4 else "관망"
        conf = random.uniform(0.55, 0.82)
        grade = "A" if conf>=0.78 else "B" if conf>=0.65 else "C" if conf>=0.58 else "X"
        checks = {attr: random.random()>0.25 for attr in
                  ["signal_chk","conf_chk","vwap_chk","cvd_chk","ofi_chk",
                   "fi_chk","candle_chk","time_chk","risk_chk"]}
        self.entry_panel.update_data(ens_sig, conf, grade, checks)

        # 로그
        tags = ["INFO","DEBUG","SYSTEM","INFO","INFO"]
        msgs = [
            f"1분봉 수신 — 종가 {self._price:.2f}, 거래량 {random.randint(8000,15000):,}",
            f"CVD 다이버전스: {'정상' if trend>0 else '역전'} | OFI: {random.randint(-150,150):+d}",
            f"앙상블 예측: {ens_sig} | 신뢰도 {conf*100:.1f}%",
            f"레짐=NEUTRAL | 포지션=FLAT | 미시레짐=추세장",
            f"피처 생성 완료 25개 | 처리 {random.randint(18,35)}ms",
        ]
        tag = random.choice(tags)
        msg = random.choice(msgs)
        self.log_panel.append("all", tag, msg)

        if random.random() < 0.15:
            wmsg = f"슬리피지 {random.uniform(2,4):.1f}틱 초과 — 변동성 높음"
            self.log_panel.append("all", "WARN", wmsg)

        if self._tick % 3 == 0:
            omsg = (f"{'FILL' if random.random()>0.3 else 'PENDING'} "
                    f"{ens_sig} 5계약 @{self._price:.2f}")
            tag2 = "FILL" if "FILL" in omsg else "PENDING"
            self.log_panel.append("order", tag2, omsg,
                                  f"슬리피지 {random.uniform(0.3,1.5):.1f}틱")
            self.log_panel.append("pnl", "PNL",
                                  f"미실현 {(self._price-388.5)*5*250000:+,.0f}원",
                                  f"{(self._price-388.5):+.2f}pt × 5계약")
            self.log_panel.append("model", "MODEL",
                                  f"SGD 온라인 학습 완료 | 정확도 {random.uniform(58,66):.1f}%")


# ────────────────────────────────────────────────────────────
# main.py 인터페이스 어댑터
# ────────────────────────────────────────────────────────────
class DashboardAdapter:
    """
    main.py 가 사용하는 메서드를 MireukDashboard 에 연결하는 어댑터

    main.py 호출 패턴:
        self.dashboard = create_dashboard()
        self.dashboard.show()
        self.dashboard.append_sys_log(msg)
        self.dashboard.update_supply_macro(vix, sp500_chg, regime)
        self.dashboard.update_system_status(cb_state, latency_ms)
        self.dashboard.btn_kill  (QPushButton 참조)
    """

    def __init__(self):
        app = QApplication.instance() or QApplication(sys.argv)
        app.setStyle("Fusion")
        self._win = MireukDashboard()
        # 긴급 정지 버튼을 외부에서 접근할 수 있도록 노출
        self.btn_kill = self._win._make_kill_btn()

    # ── 필수 메서드 ────────────────────────────────────────────
    def show(self):
        self._win.show()

    def append_sys_log(self, msg: str):
        """창1 시스템 로그에 메시지 추가"""
        self._win.log_panel.append("all", "SYSTEM", msg)

    def update_supply_macro(
        self,
        vix: float = 0.0,
        sp500_chg: float = 0.0,
        usd_krw: float = 0.0,
        regime: str = "NEUTRAL",
    ):
        """수급/매크로 섹션 업데이트"""
        # 헤더 레짐 배지 갱신
        col_map = {
            "RISK_ON":  C['green'],
            "NEUTRAL":  C['orange'],
            "RISK_OFF": C['red'],
        }
        col = col_map.get(regime, C['orange'])
        self._win.lbl_regime.setText(regime)
        self._win.lbl_regime.setStyleSheet(
            f"background:{col};color:#fff;border-radius:3px;"
            f"font-size:9px;font-weight:bold;padding:1px 6px;"
        )
        # 로그에도 기록
        self._win.log_panel.append(
            "all", "INFO",
            f"[Regime] {regime} | VIX={vix:.1f} | SP500={sp500_chg:+.2%} | USD/KRW={usd_krw:+.2f}"
        )

    def update_system_status(
        self,
        cb_state: str = "NORMAL",
        latency_ms: float = 0.0,
        accuracy: float = 0.0,
    ):
        """시스템 상태 (Circuit Breaker, 지연, 정확도) 업데이트"""
        col = C['green'] if cb_state == "NORMAL" else C['red']
        self._win.log_panel.append(
            "model", "SYSTEM",
            f"CB={cb_state} | API지연={latency_ms:.0f}ms | 정확도={accuracy:.1%}"
        )

    def update_position(self, pos_data: dict):
        """청산 패널 포지션 데이터 업데이트"""
        self._win.exit_panel.update_data(pos_data)

    def update_price(self, price: float, change: float = 0.0,
                     code: str = "F202606"):
        """
        키움 실시간 현재가 → 헤더 + 예측 패널 동시 반영

        main.py _on_candle_closed 콜백에서 호출:
            self.dashboard.update_price(
                price  = bar['close'],
                change = bar['close'] - bar.get('prev_close', bar['close']),
                code   = self.realtime_data.code,
            )
        """
        self._win.update_price(price, change, code)

    def stop_sim_timer(self):
        """키움 연결 즉시 시뮬레이션 타이머 중지 — connect_kiwoom() 성공 직후 호출"""
        self._win._stop_sim_timer()

    def update_prediction(self, price: float, preds: dict, params: dict):
        """멀티 호라이즌 예측 패널 업데이트"""
        self._win.pred_panel.update_data(price, preds, params)

    def update_entry(self, signal: str, conf: float, grade: str, checks: dict):
        """진입 관리 패널 업데이트"""
        self._win.entry_panel.update_data(signal, conf, grade, checks)

    def update_divergence(self, div_data: dict):
        """다이버전스 패널 업데이트"""
        self._win.div_panel.update_data(div_data)

    def update_shap(self, core_vals, dynamic_items, rank_vals):
        """SHAP 피처 패널 업데이트"""
        self._win.feat_panel.update_shap(core_vals, dynamic_items, rank_vals)

    def append_trade_log(self, msg: str, val: str = ""):
        """창3 주문/체결 로그"""
        self._win.log_panel.append("order", "TRADE", msg, val)

    def append_pnl_log(self, msg: str, val: str = ""):
        """창4 손익 로그"""
        self._win.log_panel.append("pnl", "PNL", msg, val)

    def append_model_log(self, msg: str):
        """창5 모델 로그"""
        self._win.log_panel.append("model", "MODEL", msg)

    def append_warn_log(self, msg: str):
        """창2 경보 로그"""
        self._win.log_panel.append("all", "WARN", msg)


# ────────────────────────────────────────────────────────────
# MireukDashboard 에 긴급 정지 버튼 생성 메서드 추가
# ────────────────────────────────────────────────────────────
def _make_kill_btn(self):
    """외부(main.py)가 clicked 시그널을 연결할 수 있는 버튼 반환"""
    if not hasattr(self, '_kill_btn'):
        self._kill_btn = QPushButton("⛔ 긴급 정지 (Ctrl+Alt+K)")
        self._kill_btn.setStyleSheet(
            f"QPushButton{{background:#A32D2D;color:#fff;"
            f"border:none;border-radius:4px;padding:8px;"
            f"font-size:11px;font-weight:bold;}}"
            f"QPushButton:hover{{background:#C0392B;}}"
        )
    return self._kill_btn

MireukDashboard._make_kill_btn = _make_kill_btn


# ────────────────────────────────────────────────────────────
# 진입점 함수들
# ────────────────────────────────────────────────────────────
def create_dashboard() -> DashboardAdapter:
    """
    main.py 에서 호출하는 팩토리 함수

    사용법 (main.py):
        self.dashboard = create_dashboard()
        self.dashboard.show()
        self.dashboard.append_sys_log("시스템 시작")
        self.dashboard.btn_kill.clicked.connect(...)
    """
    return DashboardAdapter()


def launch_dashboard(kiwoom=None):
    """단독 실행 또는 테스트용"""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MireukDashboard(kiwoom=kiwoom)
    win.show()
    return app, win


if __name__ == "__main__":
    app, win = launch_dashboard()
    sys.exit(app.exec_())
