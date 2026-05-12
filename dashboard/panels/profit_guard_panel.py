# dashboard/panels/profit_guard_panel.py — 수익 보존 가드 패널 (PyQt5)
"""
💰 수익 보존 가드 패널 — 4개 섹션

┌─────────────────────────────────────────────────────────────────┐
│ [A] 가드 현황 — 실시간 레이어별 상태 + PnL DNA 바               │
├────────────────────────┬────────────────────────────────────────┤
│ [B] 파라미터 설정       │ [C] 적용 전/후 비교 테이블              │
│   · 피크 트레일 슬라이더│   Champion(현행) vs Challenger(가드 적용)│
│   · 등급 게이트 설정    │                                        │
│   · 오후 리스크 모드    │ [D] 챌린저 승급 제안                   │
│   · 연속 손실 CB        │   + 황금 시간대 / 가드 차단 로그        │
└────────────────────────┴────────────────────────────────────────┘
"""
import datetime
import json
import logging
import os
from typing import Optional, List, TYPE_CHECKING

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QScrollArea, QFrame, QGridLayout, QProgressBar, QTextEdit,
    QFormLayout, QComboBox,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QBrush, QPainter, QPen, QLinearGradient

if TYPE_CHECKING:
    from strategy.profit_guard import ProfitGuard, ProfitGuardConfig

logger = logging.getLogger("SYSTEM")

_PROFIT_GUARD_PREFS_FILE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "profit_guard_prefs.json")
)

# ── 색상 팔레트 ───────────────────────────────────────────────────
C = {
    "bg":     "#0D1117", "bg2": "#161B22", "bg3": "#21262D",
    "border": "#30363D", "text": "#E6EDF3", "text2": "#8B949E",
    "green":  "#3FB950", "red":  "#F85149", "blue":  "#58A6FF",
    "orange": "#D29922", "purple": "#A371F7", "cyan": "#39D3BB",
    "yellow": "#E3B341", "gold": "#FFD700",
}

TIER_COLORS = ["#39D3BB", "#58A6FF", "#D29922", "#F85149", "#8B0000"]
TIER_LABELS = ["Tier 0 정상", "Tier 1 B급↑", "Tier 2 A급↑", "Tier 3 A+전용", "Tier 4 거래중단"]


def _lbl(text, color=None, bold=False, size=None):
    l = QLabel(text)
    style = f"background:transparent; color:{color or C['text']};"
    if bold:
        style += "font-weight:bold;"
    if size:
        style += f"font-size:{size}px;"
    l.setStyleSheet(style)
    return l


def _box(title):
    g = QGroupBox(title)
    g.setStyleSheet(f"""
        QGroupBox {{
            color:{C['text']}; border:1px solid {C['border']};
            border-radius:6px; margin-top:8px; padding:6px;
            font-weight:bold;
        }}
        QGroupBox::title {{ subcontrol-origin:margin; left:10px; }}
    """)
    return g


def _btn(text, color=C["blue"]):
    b = QPushButton(text)
    b.setStyleSheet(f"""
        QPushButton {{
            background:{color}22; color:{color};
            border:1px solid {color}; border-radius:4px;
            padding:4px 10px; font-weight:bold;
        }}
        QPushButton:hover {{ background:{color}44; }}
        QPushButton:pressed {{ background:{color}66; }}
    """)
    return b


# ── PnL DNA 바 위젯 ──────────────────────────────────────────────
class PnlDnaBar(QWidget):
    """
    당일 누적 PnL 흐름을 수평 바로 시각화.
    피크, 보호선(Trail Floor), 현재값, 티어 경계를 표시한다.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._trades: List[dict] = []   # [{"pnl": int, "time": "HH:MM"}, ...]
        self._trail_floor: Optional[float] = None
        self._peak: float = 0.0
        self._tiers: List[float] = [1_000_000, 2_000_000, 3_000_000, 4_000_000]
        self.setMinimumHeight(70)
        self.setMaximumHeight(90)

    def set_data(self, trades, trail_floor, peak, tiers):
        self._trades      = trades or []
        self._trail_floor = trail_floor
        self._peak        = peak
        self._tiers       = tiers
        self.update()

    def paintEvent(self, event):
        if not self._trades:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        pad_x, pad_y = 8, 10

        # 누적 PnL 시리즈
        cumulative = []
        c = 0.0
        for t in self._trades:
            c += t.get("pnl", 0)
            cumulative.append(c)

        all_vals = cumulative + [self._peak or 0, self._trail_floor or 0]
        mn = min(all_vals + [0])
        mx = max(all_vals + [0])
        span = mx - mn if mx != mn else 1

        def to_x(i):
            return pad_x + (w - 2 * pad_x) * i / max(len(cumulative) - 1, 1)

        def to_y(v):
            return pad_y + (h - 2 * pad_y) * (1 - (v - mn) / span)

        # 배경 영역 (양수=초록, 음수=빨강)
        zero_y = to_y(0)
        for i in range(len(cumulative)):
            x1 = to_x(i)
            x2 = to_x(i + 1) if i + 1 < len(cumulative) else x1 + 2
            val = cumulative[i]
            col = QColor(C["green"] if val >= 0 else C["red"])
            col.setAlpha(30)
            painter.fillRect(int(x1), int(min(to_y(val), zero_y)),
                             int(x2 - x1 + 1), int(abs(to_y(val) - zero_y)), col)

        # PnL 라인
        pen = QPen(QColor(C["cyan"]), 2)
        painter.setPen(pen)
        for i in range(1, len(cumulative)):
            painter.drawLine(
                int(to_x(i - 1)), int(to_y(cumulative[i - 1])),
                int(to_x(i)), int(to_y(cumulative[i]))
            )

        # 피크 수평선 (골드)
        if self._peak > 0:
            ypeak = to_y(self._peak)
            pen_peak = QPen(QColor(C["gold"]), 1, Qt.DashLine)
            painter.setPen(pen_peak)
            painter.drawLine(pad_x, int(ypeak), w - pad_x, int(ypeak))

        # 보호선 수평선 (주황)
        if self._trail_floor is not None:
            yfloor = to_y(self._trail_floor)
            pen_floor = QPen(QColor(C["orange"]), 1, Qt.DashDotLine)
            painter.setPen(pen_floor)
            painter.drawLine(pad_x, int(yfloor), w - pad_x, int(yfloor))

        # 제로선
        pen_zero = QPen(QColor(C["border"]), 1)
        painter.setPen(pen_zero)
        painter.drawLine(pad_x, int(zero_y), w - pad_x, int(zero_y))

        painter.end()


# ── 섹션 A: 가드 현황 ────────────────────────────────────────────
class _StatusSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup()

    def _setup(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 왼쪽: 레이어별 상태
        left = _box("⚡ 가드 레이어 현황")
        ll = QGridLayout(left)
        ll.setSpacing(4)

        labels = ["L1 트레일", "L2 등급티어", "L3 오후제한", "L4 수익CB"]
        self._layer_badges = []
        for i, lbl in enumerate(labels):
            ll.addWidget(_lbl(lbl, C["text2"]), i, 0)
            badge = _lbl("대기", C["text2"])
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedWidth(80)
            badge.setStyleSheet(
                f"background:{C['bg3']}; color:{C['text2']}; border-radius:4px;"
                "padding:2px 6px; font-weight:bold;"
            )
            ll.addWidget(badge, i, 1)
            self._layer_badges.append(badge)

        layout.addWidget(left, 3)

        # 중앙: 핵심 수치
        mid = _box("📊 당일 수익 현황")
        ml = QFormLayout(mid)
        ml.setSpacing(4)

        self._lbl_cur   = _lbl("0원", C["text"], bold=True, size=13)
        self._lbl_peak  = _lbl("0원", C["gold"], bold=True)
        self._lbl_floor = _lbl("미발동", C["orange"])
        self._lbl_tier  = _lbl("Tier 0", TIER_COLORS[0], bold=True)
        self._lbl_blk   = _lbl("0회", C["red"])

        ml.addRow(_lbl("현재 누적:", C["text2"]), self._lbl_cur)
        ml.addRow(_lbl("당일 피크:", C["text2"]), self._lbl_peak)
        ml.addRow(_lbl("보호선:", C["text2"]),    self._lbl_floor)
        ml.addRow(_lbl("등급 티어:", C["text2"]), self._lbl_tier)
        ml.addRow(_lbl("금일 차단:", C["text2"]), self._lbl_blk)

        layout.addWidget(mid, 2)

        # 오른쪽: PnL DNA 바
        right = _box("📈 PnL DNA (금일 누적)")
        rl = QVBoxLayout(right)
        self._dna_bar = PnlDnaBar()
        rl.addWidget(self._dna_bar)

        legend = QHBoxLayout()
        for color, text in [(C["cyan"], "PnL"), (C["gold"], "피크"), (C["orange"], "보호선")]:
            legend.addWidget(_lbl(f"▬ {text}", color))
        rl.addLayout(legend)
        layout.addWidget(right, 5)

    def refresh(self, status: dict, daily_pnl: float, trades: list, cfg=None):
        cur = daily_pnl
        peak = status.get("peak_pnl", 0.0)
        floor = status.get("trail_floor")
        tier  = status.get("current_tier", 0)
        blk   = status.get("blocked_today", 0)

        color = C["green"] if cur >= 0 else C["red"]
        self._lbl_cur.setText(f"{cur:+,.0f}원")
        self._lbl_cur.setStyleSheet(
            f"background:transparent; color:{color}; font-weight:bold; font-size:13px;"
        )
        self._lbl_peak.setText(f"{peak:+,.0f}원")
        self._lbl_floor.setText(
            f"{floor:+,.0f}원" if floor is not None else "미발동"
        )
        tier_c = TIER_COLORS[min(tier, len(TIER_COLORS) - 1)]
        tier_l = TIER_LABELS[min(tier, len(TIER_LABELS) - 1)]
        self._lbl_tier.setText(tier_l)
        self._lbl_tier.setStyleSheet(
            f"background:transparent; color:{tier_c}; font-weight:bold;"
        )
        self._lbl_blk.setText(f"{blk}회")

        # 레이어 배지 업데이트
        states = [
            ("발동" if status.get("trail_halted") else "정상",
             C["red"] if status.get("trail_halted") else C["green"]),
            (tier_l.split(" ")[0],
             tier_c),
            (f"{status.get('afternoon_count', 0)}회",
             C["orange"] if status.get("afternoon_count", 0) >= 2 else C["green"]),
            ("발동" if status.get("pcb_halted") else f"{status.get('pcb_consec', 0)}/2",
             C["red"] if status.get("pcb_halted") else C["green"]),
        ]
        for badge, (txt, clr) in zip(self._layer_badges, states):
            badge.setText(txt)
            badge.setStyleSheet(
                f"background:{clr}22; color:{clr}; border-radius:4px;"
                "padding:2px 6px; font-weight:bold;"
            )

        # PnL DNA 업데이트
        tiers_thresh = []
        if cfg:
            tiers_thresh = [t[0] for t in cfg.profit_tiers if t[0] > 0]
        self._dna_bar.set_data(
            [{"pnl": t.get("pnl_krw", 0)} for t in trades],
            floor, peak, tiers_thresh
        )


# ── 섹션 B: 파라미터 설정 ────────────────────────────────────────
class _SettingsSection(QWidget):
    config_changed = pyqtSignal(object)   # ProfitGuardConfig

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # L1: 트레일링 가드
        g1 = _box("L1  피크 트레일링 가드")
        fl1 = QFormLayout(g1)
        fl1.setSpacing(4)

        self._trail_act = QSpinBox()
        self._trail_act.setRange(50, 2000)
        self._trail_act.setSingleStep(50)
        self._trail_act.setSuffix(" 만원")
        self._trail_act.setValue(200)
        self._trail_act.setStyleSheet(self._spin_style())

        self._trail_ratio = QSlider(Qt.Horizontal)
        self._trail_ratio.setRange(15, 60)
        self._trail_ratio.setValue(35)
        self._trail_ratio_lbl = _lbl("35%", C["orange"], bold=True)
        self._trail_ratio.valueChanged.connect(
            lambda v: self._trail_ratio_lbl.setText(f"{v}%")
        )
        row_trail = QHBoxLayout()
        row_trail.addWidget(self._trail_ratio)
        row_trail.addWidget(self._trail_ratio_lbl)

        fl1.addRow(_lbl("발동 임계값:", C["text2"]), self._trail_act)
        fl1.addRow(_lbl("하락 허용율:", C["text2"]), row_trail)
        layout.addWidget(g1)

        # L2: 등급 게이트
        g2 = _box("L2  수익 구간별 등급 게이트")
        fl2 = QFormLayout(g2)
        fl2.setSpacing(3)

        self._tier_spins = []
        tier_defs = [(100, "C급 이상"), (200, "B급 이상"), (300, "A급 이상"), (400, "거래중단")]
        for krw, label in tier_defs:
            sp = QSpinBox()
            sp.setRange(50, 2000)
            sp.setSingleStep(50)
            sp.setSuffix(" 만원")
            sp.setValue(krw)
            sp.setStyleSheet(self._spin_style())
            fl2.addRow(_lbl(f"{label} 임계:", C["text2"]), sp)
            self._tier_spins.append(sp)
        layout.addWidget(g2)

        # L3: 오후 리스크
        g3 = _box("L3  오후 리스크 압축")
        fl3 = QFormLayout(g3)
        fl3.setSpacing(4)

        self._aft_enabled = QCheckBox("활성화")
        self._aft_enabled.setChecked(True)
        self._aft_enabled.setStyleSheet(f"color:{C['text']};")

        self._aft_hour = QSpinBox()
        self._aft_hour.setRange(11, 15)
        self._aft_hour.setValue(13)
        self._aft_hour.setSuffix(" 시")
        self._aft_hour.setStyleSheet(self._spin_style())

        self._aft_max = QSpinBox()
        self._aft_max.setRange(1, 10)
        self._aft_max.setValue(3)
        self._aft_max.setSuffix(" 회")
        self._aft_max.setStyleSheet(self._spin_style())

        self._aft_min_pnl = QSpinBox()
        self._aft_min_pnl.setRange(50, 1000)
        self._aft_min_pnl.setSingleStep(50)
        self._aft_min_pnl.setValue(100)
        self._aft_min_pnl.setSuffix(" 만원")
        self._aft_min_pnl.setStyleSheet(self._spin_style())

        fl3.addRow(self._aft_enabled)
        fl3.addRow(_lbl("제한 시작:", C["text2"]), self._aft_hour)
        fl3.addRow(_lbl("최대 진입:", C["text2"]), self._aft_max)
        fl3.addRow(_lbl("발동 최소수익:", C["text2"]), self._aft_min_pnl)
        layout.addWidget(g3)

        # L4: 연속 손실 CB
        g4 = _box("L4  수익 보존 연속 손실 CB")
        fl4 = QFormLayout(g4)
        fl4.setSpacing(4)

        self._pcb_enabled = QCheckBox("활성화")
        self._pcb_enabled.setChecked(True)
        self._pcb_enabled.setStyleSheet(f"color:{C['text']};")

        self._pcb_min_pnl = QSpinBox()
        self._pcb_min_pnl.setRange(50, 1000)
        self._pcb_min_pnl.setSingleStep(50)
        self._pcb_min_pnl.setValue(150)
        self._pcb_min_pnl.setSuffix(" 만원")
        self._pcb_min_pnl.setStyleSheet(self._spin_style())

        self._pcb_consec = QSpinBox()
        self._pcb_consec.setRange(1, 5)
        self._pcb_consec.setValue(2)
        self._pcb_consec.setSuffix(" 연속")
        self._pcb_consec.setStyleSheet(self._spin_style())

        fl4.addRow(self._pcb_enabled)
        fl4.addRow(_lbl("발동 최소수익:", C["text2"]), self._pcb_min_pnl)
        fl4.addRow(_lbl("연속 손실 기준:", C["text2"]), self._pcb_consec)
        layout.addWidget(g4)

        # 적용 버튼
        btn_row = QHBoxLayout()
        self._btn_apply = _btn("✅ 적용", C["green"])
        self._btn_reset = _btn("↩ 기본값", C["text2"])
        self._btn_apply.clicked.connect(self._on_apply)
        self._btn_reset.clicked.connect(self._on_reset)
        btn_row.addWidget(self._btn_apply)
        btn_row.addWidget(self._btn_reset)
        layout.addLayout(btn_row)
        layout.addStretch()

    def _spin_style(self):
        return (
            f"QSpinBox {{ background:{C['bg3']}; color:{C['text']}; "
            f"border:1px solid {C['border']}; border-radius:3px; padding:2px; }}"
        )

    def _on_apply(self):
        from strategy.profit_guard import ProfitGuardConfig
        cfg = ProfitGuardConfig()
        cfg.trail_activation_krw  = self._trail_act.value() * 10_000
        cfg.trail_ratio           = self._trail_ratio.value() / 100.0
        cfg.afternoon_enabled     = self._aft_enabled.isChecked()
        cfg.afternoon_cutoff_hour = self._aft_hour.value()
        cfg.afternoon_max_trades  = self._aft_max.value()
        cfg.afternoon_min_pnl_krw = self._aft_min_pnl.value() * 10_000
        cfg.profit_cb_enabled     = self._pcb_enabled.isChecked()
        cfg.profit_cb_min_pnl_krw = self._pcb_min_pnl.value() * 10_000
        cfg.profit_cb_consec_loss = self._pcb_consec.value()

        # 티어 설정
        tier_mults = [0.6, 1.0, 1.2, 1.5]
        tiers = [(0, 0.6, None)]
        for i, sp in enumerate(self._tier_spins):
            val = sp.value() * 10_000
            if i < len(tier_mults):
                mult = tier_mults[i]
                max_qty = 0 if i == 3 else None
                tiers.append((val, mult, max_qty))
        cfg.profit_tiers = sorted(tiers, key=lambda x: x[0])
        self.config_changed.emit(cfg)

    def _on_reset(self):
        self._trail_act.setValue(200)
        self._trail_ratio.setValue(35)
        self._aft_enabled.setChecked(True)
        self._aft_hour.setValue(13)
        self._aft_max.setValue(3)
        self._aft_min_pnl.setValue(100)
        self._pcb_enabled.setChecked(True)
        self._pcb_min_pnl.setValue(150)
        self._pcb_consec.setValue(2)
        for sp, v in zip(self._tier_spins, [100, 200, 300, 400]):
            sp.setValue(v)
        self._on_apply()

    def get_config(self):
        self._on_apply()

    def load_config(self, cfg):
        """현재 config 값을 UI에 반영."""
        self._trail_act.setValue(int(cfg.trail_activation_krw // 10_000))
        self._trail_ratio.setValue(int(cfg.trail_ratio * 100))
        self._aft_enabled.setChecked(cfg.afternoon_enabled)
        self._aft_hour.setValue(cfg.afternoon_cutoff_hour)
        self._aft_max.setValue(cfg.afternoon_max_trades)
        self._aft_min_pnl.setValue(int(cfg.afternoon_min_pnl_krw // 10_000))
        self._pcb_enabled.setChecked(cfg.profit_cb_enabled)
        self._pcb_min_pnl.setValue(int(cfg.profit_cb_min_pnl_krw // 10_000))
        self._pcb_consec.setValue(cfg.profit_cb_consec_loss)
        tier_vals = [int(t[0] // 10_000) for t in cfg.profit_tiers if t[0] > 0]
        for sp, v in zip(self._tier_spins, tier_vals):
            sp.setValue(v)


# ── 섹션 C: 챔피언 vs 챌린저 비교 테이블 ────────────────────────
class _CompareSection(QWidget):
    simulate_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.addWidget(_lbl("⚔ 챔피언(현행) vs 챌린저(가드 적용)", C["text"], bold=True))
        header.addStretch()
        self._btn_sim = _btn("🔄 금일 시뮬", C["cyan"])
        self._btn_sim.setFixedWidth(110)
        self._btn_sim.clicked.connect(self.simulate_requested.emit)
        header.addWidget(self._btn_sim)
        layout.addLayout(header)

        # 비교 테이블
        cols = ["지표", "👑 챔피언 (현행)", "⚔ 챌린저 (가드)", "개선도"]
        self._table = QTableWidget(0, len(cols))
        self._table.setHorizontalHeaderLabels(cols)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.NoSelection)
        self._table.setMaximumHeight(230)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background:{C['bg2']}; color:{C['text']};
                border:1px solid {C['border']}; gridline-color:{C['border']};
            }}
            QHeaderView::section {{
                background:{C['bg3']}; color:{C['text2']};
                border:0; padding:4px; font-weight:bold;
            }}
        """)
        layout.addWidget(self._table)

        # 차단 거래 목록
        layout.addWidget(_lbl("🚫 가드 적용 시 차단되는 거래", C["text2"]))
        self._blocked_list = QTextEdit()
        self._blocked_list.setReadOnly(True)
        self._blocked_list.setMaximumHeight(90)
        self._blocked_list.setStyleSheet(
            f"background:{C['bg2']}; color:{C['text2']}; "
            f"border:1px solid {C['border']}; font-size:11px;"
        )
        layout.addWidget(self._blocked_list)

    def update_comparison(self, champ: dict, chall: dict, blocked_trades: list):
        """비교 결과를 테이블에 채운다."""
        rows = [
            ("총 손익",
             f"{champ.get('total_pnl', 0):+,.0f}원",
             f"{chall.get('total_pnl', 0):+,.0f}원",
             chall.get('total_pnl', 0) - champ.get('total_pnl', 0)),
            ("거래 수",
             f"{champ.get('trade_count', 0)}회",
             f"{chall.get('trade_count', 0)}회",
             chall.get('trade_count', 0) - champ.get('trade_count', 0)),
            ("승률",
             f"{champ.get('win_rate', 0):.1%}",
             f"{chall.get('win_rate', 0):.1%}",
             (chall.get('win_rate', 0) - champ.get('win_rate', 0)) * 100),
            ("최대 피크",
             f"{champ.get('peak_pnl', 0):+,.0f}원",
             f"{chall.get('peak_pnl', 0):+,.0f}원",
             chall.get('peak_pnl', 0) - champ.get('peak_pnl', 0)),
            ("최대 낙폭(MDD)",
             f"{champ.get('mdd', 0):,.0f}원",
             f"{chall.get('mdd', 0):,.0f}원",
             champ.get('mdd', 0) - chall.get('mdd', 0)),   # MDD는 줄어들수록 좋음
            ("차단 거래수",
             "—",
             f"{chall.get('blocked_count', 0)}회",
             None),
        ]

        self._table.setRowCount(len(rows))
        for r, (label, cv, chv, delta) in enumerate(rows):
            self._table.setItem(r, 0, self._cell(label, C["text2"]))
            self._table.setItem(r, 1, self._cell(cv, C["text"]))
            self._table.setItem(r, 2, self._cell(chv, C["text"]))

            if delta is None:
                self._table.setItem(r, 3, self._cell("—", C["text2"]))
            elif isinstance(delta, float) and abs(delta) < 0.01:
                self._table.setItem(r, 3, self._cell("±0", C["text2"]))
            else:
                good = delta > 0
                if label == "최대 낙폭(MDD)":
                    good = delta > 0   # MDD 차이 = champ - chall > 0 이면 개선
                sign = "+" if delta > 0 else ""
                if isinstance(delta, float) and label == "승률":
                    txt = f"{sign}{delta:.1f}%p"
                elif abs(delta) >= 10000:
                    txt = f"{sign}{delta:,.0f}원"
                else:
                    txt = f"{sign}{delta}"
                clr = C["green"] if good else C["red"]
                item = self._cell(txt, clr)
                self._table.setItem(r, 3, item)

        # 차단 거래 목록
        if blocked_trades:
            lines = []
            for t in blocked_trades[:10]:
                lines.append(
                    f"  {t.get('exit_time','?')} | "
                    f"PnL {t.get('pnl_krw', 0):+,.0f}원 | "
                    f"차단 시 누적 {t.get('cum_pnl_at_block', 0):+,.0f}원"
                )
            self._blocked_list.setPlainText("\n".join(lines))
        else:
            self._blocked_list.setPlainText("  (차단 거래 없음)")

    def _cell(self, text, color=None):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignCenter)
        if color:
            item.setForeground(QBrush(QColor(color)))
        return item

    def show_no_data(self):
        self._table.setRowCount(1)
        msg = self._cell("금일 거래 데이터 없음 — 장 중 시뮬 버튼 클릭", C["text2"])
        self._table.setItem(0, 0, msg)
        self._table.setSpan(0, 0, 1, 4)
        self._blocked_list.setPlainText("")


# ── 섹션 D: 챌린저 승급 제안 + 황금 시간대 + 차단 로그 ──────────
class _ProposalSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # 챌린저 승급 제안
        promo_box = _box("🏆 챌린저 승급 제안")
        pl = QVBoxLayout(promo_box)

        self._promo_table = QTableWidget(0, 4)
        self._promo_table.setHorizontalHeaderLabels(["구성", "관찰일", "가상수익", "제안"])
        self._promo_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._promo_table.verticalHeader().setVisible(False)
        self._promo_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._promo_table.setSelectionMode(QTableWidget.SingleSelection)
        self._promo_table.setMaximumHeight(100)
        self._promo_table.setStyleSheet(f"""
            QTableWidget {{
                background:{C['bg2']}; color:{C['text']};
                border:1px solid {C['border']}; gridline-color:{C['border']};
            }}
            QHeaderView::section {{
                background:{C['bg3']}; color:{C['text2']};
                border:0; padding:3px; font-weight:bold;
            }}
        """)
        pl.addWidget(self._promo_table)

        self._btn_promote = _btn("⬆ 선택 구성으로 승급 적용", C["purple"])
        self._btn_promote.clicked.connect(self._on_promote)
        pl.addWidget(self._btn_promote)
        layout.addWidget(promo_box)

        # 황금 시간대 + 피로도 지수 (창의적 기능)
        gold_box = _box("🌟 황금 시간대 분석 (피로도 가중)")
        gl = QVBoxLayout(gold_box)

        self._gold_tip = _lbl(
            "금일 데이터 없음 — 장 중 자동 갱신됩니다",
            C["text2"]
        )
        self._gold_tip.setWordWrap(True)
        gl.addWidget(self._gold_tip)

        # 시간대별 성과 바
        self._hour_bars = {}
        hour_layout = QHBoxLayout()
        for h in range(9, 16):
            col = QVBoxLayout()
            bar = QProgressBar()
            bar.setOrientation(Qt.Vertical)
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedWidth(22)
            bar.setFixedHeight(50)
            bar.setStyleSheet(
                "QProgressBar { background:#1a1a2e; border:1px solid #30363D; border-radius:3px; }"
                "QProgressBar::chunk { background:#58A6FF; border-radius:2px; }"
            )
            col.addWidget(bar, alignment=Qt.AlignHCenter)
            col.addWidget(_lbl(f"{h}시", C["text2"]), alignment=Qt.AlignHCenter)
            hour_layout.addLayout(col)
            self._hour_bars[h] = bar
        gl.addLayout(hour_layout)
        layout.addWidget(gold_box)

        # 가드 차단 로그
        log_box = _box("📋 가드 차단 로그 (금일)")
        ll = QVBoxLayout(log_box)
        self._block_log = QTextEdit()
        self._block_log.setReadOnly(True)
        self._block_log.setMaximumHeight(80)
        self._block_log.setStyleSheet(
            f"background:{C['bg2']}; color:{C['text2']}; "
            f"border:1px solid {C['border']}; font-size:10px; font-family:Consolas;"
        )
        ll.addWidget(self._block_log)
        layout.addWidget(log_box)

    def refresh_proposals(self, sim_variants: list):
        """
        sim_variants: [{"label": str, "obs_days": int,
                         "virtual_pnl": float, "score": float}, ...]
        """
        self._promo_table.setRowCount(len(sim_variants))
        for r, v in enumerate(sim_variants):
            score = v.get("score", 0.0)
            suggest = "승급 권장" if score >= 1.5 else ("관찰 중" if score >= 0.8 else "유보")
            clr = C["green"] if score >= 1.5 else (C["yellow"] if score >= 0.8 else C["red"])

            for c, (txt, tc) in enumerate([
                (v.get("label", ""), C["text"]),
                (f"{v.get('obs_days', 0)}일", C["text2"]),
                (f"{v.get('virtual_pnl', 0):+,.0f}원", C["cyan"]),
                (suggest, clr),
            ]):
                item = QTableWidgetItem(txt)
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QBrush(QColor(tc)))
                self._promo_table.setItem(r, c, item)

    def refresh_golden_hours(self, hour_scores: dict):
        """hour_scores: {9: 72.5, 10: 85.0, 11: 40.0, ...} (0~100 점수)"""
        best_h = max(hour_scores, key=hour_scores.get) if hour_scores else None
        for h, bar in self._hour_bars.items():
            score = int(hour_scores.get(h, 0))
            bar.setValue(score)
            if score >= 70:
                clr = "#3FB950"
            elif score >= 40:
                clr = "#D29922"
            else:
                clr = "#F85149"
            bar.setStyleSheet(
                f"QProgressBar {{ background:#1a1a2e; border:1px solid #30363D; border-radius:3px; }}"
                f"QProgressBar::chunk {{ background:{clr}; border-radius:2px; }}"
            )
        if best_h is not None:
            self._gold_tip.setText(
                f"🥇 황금 시간대: {best_h}시 (점수 {hour_scores[best_h]:.0f})  "
                f"| 해당 시간대 외 수익 확보 후 보수적 모드 권장"
            )
            self._gold_tip.setStyleSheet(
                f"background:transparent; color:{C['gold']};"
            )

    def refresh_block_log(self, block_log: list):
        lines = []
        for ts, layer, reason in reversed(block_log[-15:]):
            lines.append(f"[{ts}] [{layer}] {reason}")
        self._block_log.setPlainText("\n".join(lines) if lines else "  (금일 차단 없음)")

    def _on_promote(self):
        row = self._promo_table.currentRow()
        if row < 0:
            return
        item = self._promo_table.item(row, 0)
        if item:
            logger.info(f"[ProfitGuard] 챌린저 승급 요청: {item.text()}")


# ── 메인 패널 ────────────────────────────────────────────────────
class ProfitGuardPanel(QWidget):
    """
    수익 보존 가드 통합 패널.
    main_dashboard.py에서 mid_tabs에 추가한다.

    연결:
        panel.set_profit_guard(guard_instance)
        # 매분 파이프라인 후:
        panel.refresh(daily_pnl_krw, today_trades)
        # 거래 체결 후:
        panel.on_trade_close(pnl_krw, daily_pnl_krw)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._guard: Optional["ProfitGuard"] = None
        self._today_trades: list = []
        self._setup()
        self._restore_settings_ui_from_disk()
        self._start_timer()

    def _setup(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # ── 상단: 가드 현황 ──
        self._status = _StatusSection()
        root.addWidget(self._status)

        # ── 하단: 설정 / 비교 / 제안 (3열 스플리터) ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #30363D; }")

        # 왼쪽: 설정
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setStyleSheet(f"background:{self._bg()}; border:none;")
        self._settings = _SettingsSection()
        self._settings.config_changed.connect(self._on_config_changed)
        left_scroll.setWidget(self._settings)
        splitter.addWidget(left_scroll)

        # 중앙: 비교 테이블
        self._compare = _CompareSection()
        self._compare.simulate_requested.connect(self._run_simulation)
        splitter.addWidget(self._compare)

        # 오른쪽: 제안 + 황금 시간대 + 로그
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet(f"background:{self._bg()}; border:none;")
        self._proposal = _ProposalSection()
        right_scroll.setWidget(self._proposal)
        splitter.addWidget(right_scroll)

        splitter.setSizes([280, 380, 300])
        root.addWidget(splitter)

        self.setStyleSheet(f"background:{self._bg()}; color:{C['text']};")

    def _bg(self):
        return C["bg"]

    def _start_timer(self):
        self._timer = QTimer(self)
        self._timer.setInterval(30_000)   # 30초마다 자동 갱신
        self._timer.timeout.connect(self._auto_refresh)
        self._timer.start()

    # ── 외부 연결 ─────────────────────────────────────────────────
    def set_profit_guard(self, guard):
        self._guard = guard
        if not guard:
            return

        cfg = self._load_cfg_from_disk()
        if cfg is None:
            cfg = guard.cfg
        else:
            guard.update_config(cfg)

        self._settings.load_config(cfg)

    @staticmethod
    def _rows_to_dicts(rows) -> list:
        """sqlite3.Row / 혼합 리스트를 dict 리스트로 변환."""
        result = []
        for r in (rows or []):
            try:
                result.append(dict(r) if not isinstance(r, dict) else r)
            except Exception:
                pass
        return result

    # ── 갱신 ─────────────────────────────────────────────────────
    def refresh(self, daily_pnl_krw: float, today_trades: list):
        """매분 파이프라인 완료 후 호출."""
        self._today_trades = self._rows_to_dicts(today_trades)
        if self._guard is None:
            return
        status = self._guard.status_dict(daily_pnl_krw)
        self._status.refresh(status, daily_pnl_krw, self._today_trades, self._guard.cfg)
        self._proposal.refresh_block_log(status.get("block_log", []))
        self._refresh_golden_hours()

    def on_trade_close(self, pnl_krw: float, daily_pnl_krw: float):
        if self._guard:
            self._guard.on_trade_close(pnl_krw, daily_pnl_krw)

    def _auto_refresh(self):
        """타이머 주기 자동 갱신 — 가드 인스턴스 없으면 스킵."""
        if self._guard is None:
            return
        try:
            from utils.db_utils import fetch_today_trades
            trades = self._rows_to_dicts(fetch_today_trades())
            daily_pnl = sum(t.get("pnl_krw", 0) for t in trades)
            self.refresh(daily_pnl, trades)
        except Exception:
            pass

    def _on_config_changed(self, cfg):
        try:
            if self._guard:
                self._guard.update_config(cfg)
            self._save_cfg_to_disk(cfg)
            self._run_simulation()
        except Exception as e:
            logger.warning("[ProfitGuardPanel] 설정 적용 오류: %s", e)

    def _save_cfg_to_disk(self, cfg):
        try:
            os.makedirs(os.path.dirname(_PROFIT_GUARD_PREFS_FILE), exist_ok=True)
            payload = {
                "version": 1,
                "config": cfg.to_dict(),
            }
            with open(_PROFIT_GUARD_PREFS_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning("[ProfitGuardPanel] 설정 저장 실패: %s", e)

    def _load_cfg_from_disk(self):
        try:
            if not os.path.exists(_PROFIT_GUARD_PREFS_FILE):
                return None

            with open(_PROFIT_GUARD_PREFS_FILE, "r", encoding="utf-8") as f:
                payload = json.load(f)

            raw_cfg = payload.get("config", payload)
            from strategy.profit_guard import ProfitGuardConfig

            cfg = ProfitGuardConfig()
            cfg.trail_activation_krw = float(raw_cfg.get("trail_activation_krw", cfg.trail_activation_krw))
            cfg.trail_ratio = float(raw_cfg.get("trail_ratio", cfg.trail_ratio))
            cfg.afternoon_enabled = bool(raw_cfg.get("afternoon_enabled", cfg.afternoon_enabled))
            cfg.afternoon_cutoff_hour = int(raw_cfg.get("afternoon_cutoff_hour", cfg.afternoon_cutoff_hour))
            cfg.afternoon_min_pnl_krw = float(raw_cfg.get("afternoon_min_pnl_krw", cfg.afternoon_min_pnl_krw))
            cfg.afternoon_max_trades = int(raw_cfg.get("afternoon_max_trades", cfg.afternoon_max_trades))
            cfg.afternoon_min_rr = float(raw_cfg.get("afternoon_min_rr", cfg.afternoon_min_rr))
            cfg.profit_cb_enabled = bool(raw_cfg.get("profit_cb_enabled", cfg.profit_cb_enabled))
            cfg.profit_cb_min_pnl_krw = float(raw_cfg.get("profit_cb_min_pnl_krw", cfg.profit_cb_min_pnl_krw))
            cfg.profit_cb_consec_loss = int(raw_cfg.get("profit_cb_consec_loss", cfg.profit_cb_consec_loss))

            parsed_tiers = []
            for tier in raw_cfg.get("profit_tiers", []):
                if not isinstance(tier, (list, tuple)) or len(tier) < 3:
                    continue
                threshold = float(tier[0])
                min_mult = None if tier[1] is None else float(tier[1])
                max_qty = None if tier[2] is None else int(tier[2])
                parsed_tiers.append((threshold, min_mult, max_qty))
            if parsed_tiers:
                cfg.profit_tiers = parsed_tiers

            return cfg
        except Exception as e:
            logger.warning("[ProfitGuardPanel] 설정 복원 실패: %s", e)
            return None

    def _restore_settings_ui_from_disk(self):
        cfg = self._load_cfg_from_disk()
        if cfg is not None:
            self._settings.load_config(cfg)

    def _run_simulation(self):
        """금일 거래에 현재 설정을 소급 시뮬레이션."""
        try:
            self._run_simulation_inner()
        except Exception as e:
            logger.warning("[ProfitGuardPanel] 시뮬레이션 오류: %s", e)
            self._compare.show_no_data()

    def _run_simulation_inner(self):
        from strategy.profit_guard import ProfitGuard
        if not self._today_trades:
            try:
                from utils.db_utils import fetch_today_trades
                self._today_trades = self._rows_to_dicts(fetch_today_trades())
            except Exception:
                self._compare.show_no_data()
                return

        if not self._today_trades:
            self._compare.show_no_data()
            return

        # 챔피언 (가드 없음)
        champ = {
            "total_pnl":   sum(t.get("pnl_krw", 0) for t in self._today_trades),
            "trade_count": len(self._today_trades),
            "wins":        sum(1 for t in self._today_trades if t.get("pnl_krw", 0) >= 0),
            "win_rate":    sum(1 for t in self._today_trades if t.get("pnl_krw", 0) >= 0)
                           / max(len(self._today_trades), 1),
            "peak_pnl":    self._calc_peak(self._today_trades),
            "mdd":         self._calc_mdd(self._today_trades),
        }

        # 챌린저 (가드 적용)
        cfg = self._guard.cfg if self._guard else None
        if cfg is None:
            from strategy.profit_guard import ProfitGuardConfig
            cfg = ProfitGuardConfig()

        # 시각 정보 보강
        enriched = self._enrich_trades(self._today_trades)
        chall = ProfitGuard.simulate(enriched, cfg)
        self._compare.update_comparison(champ, chall, chall.get("blocked_trades", []))

        # 챌린저 승급 제안 계산 (파라미터 변형 3종 비교)
        self._update_proposals(enriched)

    def _enrich_trades(self, trades: list) -> list:
        """거래 목록에 hour/minute/size_mult 추가."""
        enriched = []
        for t in trades:
            exit_time = t.get("exit_time") or t.get("closed_at") or "10:00"
            if len(str(exit_time)) >= 5:
                try:
                    h, m = int(str(exit_time)[:2]), int(str(exit_time)[3:5])
                except Exception:
                    h, m = 10, 0
            else:
                h, m = 10, 0
            enriched.append({
                **t,
                "hour": h, "minute": m,
                "exit_time": f"{h:02d}:{m:02d}",
                "size_mult": t.get("size_mult", 1.0),
            })
        return enriched

    def _update_proposals(self, enriched: list):
        from strategy.profit_guard import ProfitGuard, ProfitGuardConfig

        variants = []
        for label, trail_r, trail_a, pcb_l in [
            ("공격형 (Trail 40%)", 0.40, 2_000_000, 2),
            ("표준형 (Trail 35%)", 0.35, 2_000_000, 2),
            ("보수형 (Trail 25%)", 0.25, 1_500_000, 1),
        ]:
            cfg_v = ProfitGuardConfig()
            cfg_v.trail_ratio = trail_r
            cfg_v.trail_activation_krw = trail_a
            cfg_v.profit_cb_consec_loss = pcb_l
            result = ProfitGuard.simulate(enriched, cfg_v)
            pnl = result["total_pnl"]
            trades_n = result["trade_count"]
            wr = result["win_rate"]
            mdd = result["mdd"]
            score = (wr * 100 - 50) / 10 if trades_n > 0 else 0.0
            variants.append({
                "label": label,
                "obs_days": 1,
                "virtual_pnl": pnl,
                "score": score,
            })
        self._proposal.refresh_proposals(variants)

    def _refresh_golden_hours(self):
        """시간대별 성과를 집계해 황금 시간대 바를 업데이트."""
        if not self._today_trades:
            return
        hour_pnl = {}
        hour_cnt = {}
        for t in self._today_trades:
            et = t.get("exit_time") or t.get("closed_at") or ""
            try:
                h = int(str(et)[:2])
            except Exception:
                h = 10
            pnl = t.get("pnl_krw", 0)
            hour_pnl[h] = hour_pnl.get(h, 0) + pnl
            hour_cnt[h] = hour_cnt.get(h, 0) + 1

        # 점수: 시간대 평균 PnL을 0~100으로 정규화
        scores = {}
        all_avg = [hour_pnl[h] / max(hour_cnt[h], 1) for h in hour_pnl]
        mn, mx = (min(all_avg), max(all_avg)) if all_avg else (0, 1)
        span = mx - mn if mx != mn else 1
        for h in range(9, 16):
            avg = hour_pnl.get(h, 0) / max(hour_cnt.get(h, 1), 1)
            scores[h] = max(0, min(100, int((avg - mn) / span * 100)))

        self._proposal.refresh_golden_hours(scores)

    @staticmethod
    def _calc_peak(trades: list) -> float:
        c, peak = 0.0, 0.0
        for t in trades:
            c += t.get("pnl_krw", 0)
            peak = max(peak, c)
        return peak

    @staticmethod
    def _calc_mdd(trades: list) -> float:
        c, peak, mdd = 0.0, 0.0, 0.0
        for t in trades:
            c += t.get("pnl_krw", 0)
            peak = max(peak, c)
            mdd = max(mdd, peak - c)
        return mdd
