# dashboard/panels/regime_panel.py — 레짐 실시간 모니터 패널
"""
RegimePanel:
  상단 — Layer 1 (Overnight Macro) + Layer 2 (Intraday Tactical) + Micro 레짐 배지
  중단 — Layer 2 진입 정책 요약 (롱 허용/금지, 숏 허용/금지, 사이즈배율)
  하단 — 레짐 변경 이력 로그 (최근 20건)

main.py → update_intraday(status_dict) 매분 호출
       → update_layer1(regime, description) 장 전 1회 호출
       → update_micro(regime, adx, atr_ratio) 매분 호출
"""
import datetime
import logging

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QTextEdit, QSizePolicy, QFrame, QGridLayout,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

logger = logging.getLogger("SYSTEM")

# ── 색상 테이블 ────────────────────────────────────────────────────
_LAYER1_COLOR = {
    "RISK_ON":  ("#0a2a0a", "#00c878"),
    "NEUTRAL":  ("#1a1a2a", "#8888ff"),
    "RISK_OFF": ("#3a0a0a", "#ff6644"),
}
_LAYER2_COLOR = {
    "NORMAL":       ("#0a1a0a", "#66bb6a"),
    "DAY_RISK_OFF": ("#2a1a00", "#ffb300"),
    "CRASH":        ("#3a0000", "#ff4444"),
}
_MICRO_COLOR = {
    "추세장": ("#0a2a0a", "#00c878"),
    "횡보장": ("#1a1a0a", "#ffee58"),
    "급변장": ("#3a0a0a", "#ff4444"),
    "혼합":   ("#1a1a2a", "#8888ff"),
    "탈진":   ("#2a0a2a", "#ce93d8"),
}


def _badge(parent, bg, fg, text, font_size=14, bold=True):
    lbl = QLabel(text, parent)
    f = QFont("Consolas", font_size)
    f.setBold(bold)
    lbl.setFont(f)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(
        f"background:{bg}; color:{fg}; border-radius:4px; padding:4px 10px;"
    )
    lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    return lbl


def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet("color:#333;")
    return f


class RegimePanel(QWidget):
    """3계층 레짐 실시간 모니터"""

    def __init__(self, parent=None):
        super(RegimePanel, self).__init__(parent)
        self._layer1_regime = "NEUTRAL"
        self._layer1_desc   = ""
        self._layer2_data:  dict = {}
        self._micro_regime  = "혼합"
        self._micro_adx     = 0.0
        self._micro_atr     = 0.0
        self._log_lines: list = []   # (ts_str, msg)

        self._build_ui()

        self._timer = QTimer(self)
        self._timer.setInterval(60_000)
        self._timer.timeout.connect(self._refresh)
        self._timer.start()

    # ── UI 구성 ──────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # ─ 상단: 3개 배지 행 ────────────────────────────────────
        badge_row = QHBoxLayout()

        # Layer 1
        l1_box = QGroupBox("Layer 1 — Overnight Macro")
        l1_box.setStyleSheet("QGroupBox{color:#888; font-size:10px;}")
        l1_lay = QVBoxLayout(l1_box)
        l1_lay.setContentsMargins(4, 12, 4, 4)
        self._lbl_l1 = _badge(self, "#1a1a2a", "#8888ff", "NEUTRAL")
        self._lbl_l1_desc = QLabel("--")
        self._lbl_l1_desc.setStyleSheet("color:#666; font-size:10px;")
        self._lbl_l1_desc.setWordWrap(True)
        l1_lay.addWidget(self._lbl_l1)
        l1_lay.addWidget(self._lbl_l1_desc)
        badge_row.addWidget(l1_box, 2)

        # Layer 2
        l2_box = QGroupBox("Layer 2 — Intraday Tactical")
        l2_box.setStyleSheet("QGroupBox{color:#888; font-size:10px;}")
        l2_lay = QVBoxLayout(l2_box)
        l2_lay.setContentsMargins(4, 12, 4, 4)
        self._lbl_l2 = _badge(self, "#0a1a0a", "#66bb6a", "NORMAL")
        self._lbl_l2_since = QLabel("since --:--")
        self._lbl_l2_since.setStyleSheet("color:#666; font-size:10px;")
        self._lbl_l2_since.setAlignment(Qt.AlignCenter)
        l2_lay.addWidget(self._lbl_l2)
        l2_lay.addWidget(self._lbl_l2_since)
        badge_row.addWidget(l2_box, 2)

        # Micro
        mc_box = QGroupBox("Micro Regime")
        mc_box.setStyleSheet("QGroupBox{color:#888; font-size:10px;}")
        mc_lay = QVBoxLayout(mc_box)
        mc_lay.setContentsMargins(4, 12, 4, 4)
        self._lbl_mc = _badge(self, "#1a1a2a", "#8888ff", "혼합", font_size=13)
        self._lbl_mc_detail = QLabel("ADX=-- ATR=--")
        self._lbl_mc_detail.setStyleSheet("color:#666; font-size:10px;")
        self._lbl_mc_detail.setAlignment(Qt.AlignCenter)
        mc_lay.addWidget(self._lbl_mc)
        mc_lay.addWidget(self._lbl_mc_detail)
        badge_row.addWidget(mc_box, 1)

        root.addLayout(badge_row)
        root.addWidget(_sep())

        # ─ 중단: Layer 2 진입 정책 ──────────────────────────────
        policy_box = QGroupBox("진입 정책 (Layer 2 기준)")
        policy_box.setStyleSheet("QGroupBox{color:#888; font-size:10px;}")
        pg = QGridLayout(policy_box)
        pg.setContentsMargins(6, 14, 6, 6)

        pg.addWidget(QLabel("롱 허용"), 0, 0, Qt.AlignRight)
        self._lbl_long  = QLabel("O")
        self._lbl_long.setStyleSheet("color:#00c878; font-weight:bold;")
        pg.addWidget(self._lbl_long, 0, 1)

        pg.addWidget(QLabel("숏 허용"), 0, 2, Qt.AlignRight)
        self._lbl_short = QLabel("O")
        self._lbl_short.setStyleSheet("color:#00c878; font-weight:bold;")
        pg.addWidget(self._lbl_short, 0, 3)

        pg.addWidget(QLabel("사이즈"), 1, 0, Qt.AlignRight)
        self._lbl_size  = QLabel("×1.0")
        self._lbl_size.setStyleSheet("color:#aaaaaa; font-weight:bold;")
        pg.addWidget(self._lbl_size, 1, 1)

        pg.addWidget(QLabel("신뢰도 보정"), 1, 2, Qt.AlignRight)
        self._lbl_conf_adj = QLabel("+0%p")
        self._lbl_conf_adj.setStyleSheet("color:#aaaaaa; font-weight:bold;")
        pg.addWidget(self._lbl_conf_adj, 1, 3)

        pg.addWidget(QLabel("당일수익률"), 2, 0, Qt.AlignRight)
        self._lbl_day_ret = QLabel("--")
        self._lbl_day_ret.setStyleSheet("color:#aaaaaa;")
        pg.addWidget(self._lbl_day_ret, 2, 1)

        pg.addWidget(QLabel("ATR비율"), 2, 2, Qt.AlignRight)
        self._lbl_atr_r = QLabel("--")
        self._lbl_atr_r.setStyleSheet("color:#aaaaaa;")
        pg.addWidget(self._lbl_atr_r, 2, 3)

        for col in (0, 2):
            lbl = pg.itemAtPosition(0, col)
            if lbl:
                lbl.widget().setStyleSheet("color:#888; font-size:10px;")
        for row in range(3):
            for col in (0, 2):
                item = pg.itemAtPosition(row, col)
                if item:
                    item.widget().setStyleSheet("color:#666; font-size:10px;")

        root.addWidget(policy_box)
        root.addWidget(_sep())

        # ─ 하단: 레짐 변경 로그 ─────────────────────────────────
        log_box = QGroupBox("레짐 이력")
        log_box.setStyleSheet("QGroupBox{color:#888; font-size:10px;}")
        lb = QVBoxLayout(log_box)
        lb.setContentsMargins(4, 12, 4, 4)
        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setStyleSheet(
            "background:#0d0d0d; color:#aaaaaa; font-family:Consolas; font-size:10px;"
            "border:1px solid #333;"
        )
        self._log_view.setMaximumHeight(160)
        lb.addWidget(self._log_view)
        root.addWidget(log_box)
        root.addStretch()

    # ── 외부 업데이트 API ───────────────────────────────────────

    def update_layer1(self, regime: str, description: str = ""):
        self._layer1_regime = regime
        self._layer1_desc   = description
        bg, fg = _LAYER1_COLOR.get(regime, ("#1a1a2a", "#8888ff"))
        self._lbl_l1.setText(regime)
        self._lbl_l1.setStyleSheet(
            f"background:{bg}; color:{fg}; border-radius:4px; padding:4px 10px;"
            "font-weight:bold;"
        )
        self._lbl_l1_desc.setText(description[:80] if description else "--")
        self._append_log(f"L1→{regime} | {description[:60]}")

    def update_intraday(self, status: dict):
        """IntradayTacticalRegime.status_dict() 수신"""
        self._layer2_data = status
        regime  = status.get("regime", "NORMAL")
        since   = status.get("since", "--:--")
        policy  = status.get("policy", {})
        factors = status.get("factors", {})

        bg, fg = _LAYER2_COLOR.get(regime, ("#0a1a0a", "#66bb6a"))
        self._lbl_l2.setText(regime)
        self._lbl_l2.setStyleSheet(
            f"background:{bg}; color:{fg}; border-radius:4px; padding:4px 10px;"
            "font-weight:bold;"
        )
        self._lbl_l2_since.setText(f"since {since}")

        # 정책
        long_ok  = policy.get("allow_long",  True)
        short_ok = policy.get("allow_short", True)
        size_m   = policy.get("size_mult",   1.0)
        conf_adj = policy.get("min_conf_adjust", 0.0)

        self._lbl_long.setText("허용" if long_ok else "금지")
        self._lbl_long.setStyleSheet(
            f"color:{'#00c878' if long_ok else '#ff4444'}; font-weight:bold;"
        )
        self._lbl_short.setText("허용" if short_ok else "금지")
        self._lbl_short.setStyleSheet(
            f"color:{'#00c878' if short_ok else '#ff4444'}; font-weight:bold;"
        )
        self._lbl_size.setText(f"×{size_m:.1f}")
        self._lbl_conf_adj.setText(f"+{conf_adj:.0f}%p" if conf_adj else "+0%p")

        # 팩터
        day_ret = factors.get("day_ret", 0.0) * 100
        atr_r   = factors.get("atr_ratio", 0.0)
        z_warn  = factors.get("z_warn_count", 0)
        self._lbl_day_ret.setText(f"{day_ret:+.2f}%")
        clr_day = "#ff4444" if day_ret < -1.0 else "#ffb300" if day_ret < -0.5 else "#aaaaaa"
        self._lbl_day_ret.setStyleSheet(f"color:{clr_day};")
        self._lbl_atr_r.setText(f"{atr_r:.2f} (z={z_warn})")

        # 이력 (regime 변경 시만 기록)
        prev = (self._log_lines[-1][1] if self._log_lines else "")
        new_msg = f"[L2] {regime} day={day_ret:+.2f}% z={z_warn}"
        if regime not in prev:
            self._append_log(new_msg)

    def update_micro(self, regime: str, adx: float = 0.0, atr_ratio: float = 0.0):
        self._micro_regime = regime
        self._micro_adx    = adx
        self._micro_atr    = atr_ratio
        bg, fg = _MICRO_COLOR.get(regime, ("#1a1a2a", "#8888ff"))
        self._lbl_mc.setText(regime)
        self._lbl_mc.setStyleSheet(
            f"background:{bg}; color:{fg}; border-radius:4px; padding:4px 10px;"
            "font-weight:bold;"
        )
        self._lbl_mc_detail.setText(f"ADX={adx:.1f}  ATR비={atr_ratio:.2f}")

    # ── 내부 ──────────────────────────────────────────────────────

    def _append_log(self, msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._log_lines.append((ts, msg))
        if len(self._log_lines) > 60:
            self._log_lines = self._log_lines[-60:]
        self._refresh_log()

    def _refresh_log(self):
        lines = [f"{ts}  {m}" for ts, m in self._log_lines[-20:]]
        self._log_view.setPlainText("\n".join(reversed(lines)))

    def _refresh(self):
        pass   # 타이머 콜백 (필요 시 확장)
