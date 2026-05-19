# dashboard/panels/experiment_gate_panel.py — 실험 게이트 모니터 패널 [6순위]
"""
ExperimentGatePanel:
  상단 — Shadow Session 상태 카드 (SHADOW / LIVE / BLOCKED)
  하단 — Contrarian Mode 상태 카드 (WATCHING / ARMED / ACTIVE / CLEARED)

30초 주기 자동 갱신.
main.py로부터 update_shadow() / update_contrarian() 로 데이터 주입.
"""
import logging
import traceback

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QProgressBar, QSizePolicy, QFrame,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

logger = logging.getLogger("SYSTEM")

# ── 상태 색상 ─────────────────────────────────────────────────────
_C = {
    "SHADOW":   ("#1a2a3a", "#4488ff"),
    "LIVE":     ("#0a2a0a", "#00c878"),
    "BLOCKED":  ("#3a0a0a", "#ff4444"),
    "WATCHING": ("#1a1a1a", "#888888"),
    "ARMED":    ("#2a2000", "#f0c060"),
    "ACTIVE":   ("#1a0a2a", "#ce93d8"),
    "CLEARED":  ("#0a1a0a", "#66bb6a"),
}


def _state_colors(state: str):
    return _C.get(state, ("#1a1a1a", "#aaaaaa"))


class ExperimentGatePanel(QWidget):
    """Shadow Session + Contrarian Mode 실험 모니터"""

    def __init__(self, parent=None):
        super(ExperimentGatePanel, self).__init__(parent)
        self._shadow_data: dict   = {}
        self._contra_data: dict   = {}
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.setInterval(30_000)
        self._timer.timeout.connect(self._refresh_display)
        self._timer.start()

    # ── UI 구성 ──────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)
        self.setStyleSheet("background:#0e0e0e; color:#cccccc;")

        # ─ 상단: Shadow Session ─────────────────────────────────
        shadow_box = QGroupBox("🌑  Shadow Session  (모의투자 검증 게이트)")
        shadow_box.setStyleSheet(
            "QGroupBox{color:#4488ff; border:1px solid #2a3a5a; "
            "margin-top:6px; padding:6px;}"
            "QGroupBox::title{subcontrol-origin:margin; left:8px; color:#4488ff;}"
        )
        s_lay = QVBoxLayout(shadow_box)
        s_lay.setSpacing(4)

        # 상태 배지
        self._s_state_lbl = QLabel("SHADOW")
        self._s_state_lbl.setAlignment(Qt.AlignCenter)
        self._s_state_lbl.setFixedHeight(28)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self._s_state_lbl.setFont(font)
        s_lay.addWidget(self._s_state_lbl)

        # 가상 PnL / 타임스탬프
        self._s_info_lbl = QLabel("가상 PnL: — | 전환: — | 가상 정확도: —")
        self._s_info_lbl.setStyleSheet("font-size:10px; color:#888;")
        s_lay.addWidget(self._s_info_lbl)

        # 게이트 조건 3가지
        self._s_gates = {}
        gate_defs = [
            ("acc30m",      "acc30m ≥ 40%"),
            ("core_health", "CORE 건강 ≥ 70점"),
            ("zscore",      "z-score 경고 < 2회"),
        ]
        for key, label in gate_defs:
            row = QHBoxLayout()
            icon = QLabel("—")
            icon.setFixedWidth(18)
            icon.setAlignment(Qt.AlignCenter)
            name = QLabel(label)
            name.setStyleSheet("font-size:10px;")
            bar = QProgressBar()
            bar.setRange(0, 1)
            bar.setValue(0)
            bar.setFixedHeight(10)
            bar.setTextVisible(False)
            bar.setStyleSheet(
                "QProgressBar{background:#1a1a1a; border:1px solid #333; border-radius:3px;}"
                "QProgressBar::chunk{background:#4488ff; border-radius:2px;}"
            )
            row.addWidget(icon)
            row.addWidget(name)
            row.addWidget(bar, 1)
            s_lay.addLayout(row)
            self._s_gates[key] = (icon, bar)

        root.addWidget(shadow_box)

        # 구분선
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#333;")
        root.addWidget(sep)

        # ─ 하단: Contrarian Mode ────────────────────────────────
        contra_box = QGroupBox("⚡  Contrarian Mode  (역모델 스위치)")
        contra_box.setStyleSheet(
            "QGroupBox{color:#f0c060; border:1px solid #3a3000; "
            "margin-top:6px; padding:6px;}"
            "QGroupBox::title{subcontrol-origin:margin; left:8px; color:#f0c060;}"
        )
        c_lay = QVBoxLayout(contra_box)
        c_lay.setSpacing(4)

        # 상태 배지
        self._c_state_lbl = QLabel("WATCHING")
        self._c_state_lbl.setAlignment(Qt.AlignCenter)
        self._c_state_lbl.setFixedHeight(28)
        self._c_state_lbl.setFont(font)
        c_lay.addWidget(self._c_state_lbl)

        # 발동 정보
        self._c_info_lbl = QLabel("가상 PnL: — | 거래: — | 승률: —")
        self._c_info_lbl.setStyleSheet("font-size:10px; color:#888;")
        c_lay.addWidget(self._c_info_lbl)

        # 발동 조건 3가지
        self._c_conds = {}
        cond_defs = [
            ("acc30m_low",     "acc30m < 25%"),
            ("same_dir",       "동방향 10연속"),
            ("neutral_regime", "NEUTRAL 레짐"),
        ]
        for key, label in cond_defs:
            row = QHBoxLayout()
            icon = QLabel("—")
            icon.setFixedWidth(18)
            icon.setAlignment(Qt.AlignCenter)
            name = QLabel(label)
            name.setStyleSheet("font-size:10px;")
            streak_lbl = QLabel("")
            streak_lbl.setStyleSheet("font-size:10px; color:#f0c060; min-width:50px;")
            streak_lbl.setAlignment(Qt.AlignRight)
            row.addWidget(icon)
            row.addWidget(name)
            row.addStretch()
            row.addWidget(streak_lbl)
            c_lay.addLayout(row)
            self._c_conds[key] = (icon, streak_lbl)

        # 역베팅 방향 + 조건 충족 수
        self._c_detail_lbl = QLabel("조건: 0/3  |  역베팅 방향: —  |  사이즈: —")
        self._c_detail_lbl.setStyleSheet("font-size:10px; color:#ce93d8; margin-top:4px;")
        c_lay.addWidget(self._c_detail_lbl)

        root.addWidget(contra_box)
        root.addStretch()

    # ── 외부 주입 API ─────────────────────────────────────────────

    def update_shadow(self, data: dict) -> None:
        """main.py → shadow_session.status_dict() 결과 주입."""
        self._shadow_data = data or {}
        self._refresh_display()

    def update_contrarian(self, data: dict) -> None:
        """main.py → contrarian_mode.status_dict() 결과 주입."""
        self._contra_data = data or {}
        self._refresh_display()

    # ── 화면 갱신 ─────────────────────────────────────────────────

    def _refresh_display(self):
        try:
            self._refresh_shadow()
            self._refresh_contra()
        except Exception:
            logger.warning("[ExperimentGatePanel] refresh 예외:\n%s", traceback.format_exc())

    def _refresh_shadow(self):
        d = self._shadow_data
        if not d:
            return
        state = d.get("state", "SHADOW")
        bg, fg = _state_colors(state)
        self._s_state_lbl.setText(state)
        self._s_state_lbl.setStyleSheet(
            f"background:{bg}; color:{fg}; border-radius:4px; padding:2px;"
        )

        vpnl   = d.get("virtual_pnl", 0.0)
        vacc   = d.get("virtual_accuracy", 0.0)
        t_time = d.get("transition_time") or "—"
        self._s_info_lbl.setText(
            f"가상 PnL: {vpnl:+.1f}pt  |  전환: {t_time}  |  가상 정확도: {vacc:.1%}"
        )

        gates = d.get("gate_checks", {})
        for key, (icon, bar) in self._s_gates.items():
            ok = bool(gates.get(key, False))
            icon.setText("✅" if ok else "❌")
            bar.setValue(1 if ok else 0)
            bar.setStyleSheet(
                "QProgressBar{background:#1a1a1a; border:1px solid #333; border-radius:3px;}"
                f"QProgressBar::chunk{{background:{'#00c878' if ok else '#ff4444'}; border-radius:2px;}}"
            )

    def _refresh_contra(self):
        d = self._contra_data
        if not d:
            return
        state = d.get("state", "WATCHING")
        bg, fg = _state_colors(state)
        self._c_state_lbl.setText(state)
        self._c_state_lbl.setStyleSheet(
            f"background:{bg}; color:{fg}; border-radius:4px; padding:2px;"
        )

        vpnl  = d.get("virtual_pnl", 0.0)
        vtrd  = d.get("virtual_trades", 0)
        vwr   = d.get("virtual_win_rate", 0.0)
        self._c_info_lbl.setText(
            f"가상 PnL: {vpnl:+.1f}pt  |  거래: {vtrd}건  |  승률: {vwr:.1%}"
        )

        conds  = d.get("conditions", {})
        streak = d.get("same_dir_streak", 0)
        for key, (icon, streak_lbl) in self._c_conds.items():
            ok = bool(conds.get(key, False))
            icon.setText("✅" if ok else "❌")
            if key == "same_dir":
                streak_lbl.setText(f"{streak}/10연속")
                streak_lbl.setStyleSheet(
                    f"font-size:10px; color:{'#f0c060' if ok else '#555'}; min-width:50px;"
                )

        cond_count = sum(1 for v in conds.values() if v)
        c_dir = d.get("contra_direction")
        dir_str = "LONG" if c_dir == 1 else ("SHORT" if c_dir == -1 else "—")
        size_str = "1~2계약 (모의)" if state == "ACTIVE" else "—"
        self._c_detail_lbl.setText(
            f"조건: {cond_count}/3  |  역베팅 방향: {dir_str}  |  사이즈: {size_str}"
        )
