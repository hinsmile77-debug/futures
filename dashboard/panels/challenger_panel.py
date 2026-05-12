# dashboard/panels/challenger_panel.py — 도전자 모니터 패널 (PyQt5)
"""
ChallengerPanel:
  상단 — 레짐별 전문가 승위표 (⚔ 레짐 전문가)
  하단 — 전체 도전자 성과 테이블 + 승격 관리

레짐 전문가 WARNING 표시:
  탈진 레짐 전문가 풀의 Shadow 1위가 변경되면
  해당 행이 점멸 배경으로 강조 + "[1위 변경]" 배지 표시.
"""
import logging
import traceback
from typing import Optional, TYPE_CHECKING

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QMessageBox, QDialog, QDialogButtonBox,
    QTextEdit, QSplitter, QFrame,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QBrush

if TYPE_CHECKING:
    from challenger.challenger_engine import ChallengerEngine
    from challenger.promotion_manager import PromotionManager

logger = logging.getLogger("CHALLENGER")

# ── 색상 팔레트 ───────────────────────────────────────────────
C_CHAMPION  = QColor("#3a3000")
C_PROMOTE   = QColor("#003a00")
C_RANK1     = QColor("#002a3a")   # Shadow 1위 (파란 계열)
C_RANK1_NEW = QColor("#1a0030")   # 1위 변경 직후 강조 (보라)
C_UP        = QColor("#00c878")
C_DOWN      = QColor("#ff4444")
C_WARN      = QColor("#f0c060")

# ── 레짐 전문가 테이블 컬럼 ───────────────────────────────────
REGIME_COLS = [
    ("레짐",      70),
    ("전문가",    130),
    ("거래수",     55),
    ("승률",       65),
    ("수익(pt)",   70),
    ("Sharpe",     65),
    ("챔피언",     90),
    ("알림",       70),
]

# ── 전체 도전자 테이블 컬럼 ───────────────────────────────────
CHALLENGER_COLS = [
    ("도전자",   120),
    ("관찰일",    50),
    ("거래수",    50),
    ("승률",      65),
    ("수익(pt)",  70),
    ("MDD(pt)",   70),
    ("Sharpe",    65),
    ("상태",      70),
]

PROMOTION_CRITERIA = {
    "min_obs_days":    20,
    "min_trades":      30,
    "win_rate_delta": +2.0,
    "mdd_ratio":       0.90,
    "sharpe_min":      1.50,
    "return_delta":   +0.00,
}

# 레짐별 표시명
REGIME_LABEL = {
    "추세장": "추세장",
    "횡보장": "횡보장",
    "혼합":   "혼합",
    "급변장": "급변장",
    "탈진":   "탈진⚡",
}
NAME_MAP = {
    "A_CVD_EXHAUSTION":    "A CVD탈진",
    "B_OFI_REVERSAL":      "B OFI반전",
    "C_VWAP_REVERSAL":     "C VWAP반전",
    "D_EXHAUSTION_REGIME": "D 탈진레짐",
    "E_ABSORPTION":        "E 흡수감지",
    "CHAMPION_BASELINE":   "★ 챔피언기준",
}


class ChallengerPanel(QWidget):
    """도전자 모니터 패널"""

    def __init__(self, challenger_engine=None, promotion_manager=None, parent=None):
        super(ChallengerPanel, self).__init__(parent)
        self._engine  = challenger_engine
        self._promo   = promotion_manager
        self._selected_cid    = None
        self._selected_regime = None
        self._rank_change_flash = {}   # regime → flash countdown

        self._build_ui()

        self._timer = QTimer(self)
        self._timer.setInterval(30_000)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()

        self.refresh()

    # ── UI 구성 ──────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)
        self.setStyleSheet("background:#121212; color:#cccccc;")

        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(4)
        splitter.setStyleSheet("QSplitter::handle{background:#333;}")

        # ── 상단: 레짐별 전문가 승위표 ──────────────────────────
        top_box = QGroupBox("⚔  레짐 전문가 승위표")
        top_box.setStyleSheet(
            "QGroupBox{color:#f0c060; border:1px solid #444; margin-top:6px; padding:4px;}"
            "QGroupBox::title{subcontrol-origin:margin; left:8px; color:#f0c060;}"
        )
        top_lay = QVBoxLayout(top_box)
        top_lay.setContentsMargins(4, 8, 4, 4)

        # 현재 미시 레짐 상태 바
        self._lbl_cur_regime = QLabel("현재 레짐: — | ADX: — | ATR비: — | 지속: —")
        self._lbl_cur_regime.setStyleSheet(
            "background:#1a1a2a; color:#9C27B0; border:1px solid #444;"
            "border-radius:3px; padding:3px 8px; font-weight:bold;"
        )
        top_lay.addWidget(self._lbl_cur_regime)

        self._regime_table = QTableWidget(0, len(REGIME_COLS))
        self._regime_table.setHorizontalHeaderLabels([c[0] for c in REGIME_COLS])
        self._regime_table.verticalHeader().setVisible(False)
        self._regime_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._regime_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._regime_table.setMaximumHeight(200)
        self._regime_table.setStyleSheet(
            "QTableWidget{background:#1a1a1a; gridline-color:#333;}"
            "QHeaderView::section{background:#252525; color:#aaa; padding:3px;}"
            "QTableWidget::item{padding:2px;}"
            "QTableWidget::item:selected{background:#2a3a4a;}"
        )
        for i, (_, w) in enumerate(REGIME_COLS):
            self._regime_table.setColumnWidth(i, w)
        self._regime_table.itemSelectionChanged.connect(self._on_regime_row_selected)
        top_lay.addWidget(self._regime_table)

        # 레짐 전문가 승격 버튼
        regime_btn_lay = QHBoxLayout()
        self._btn_regime_promote  = QPushButton("▶ 레짐 전문가 승격")
        self._btn_regime_rollback = QPushButton("🔄 레짐 롤백")
        for btn, color in [
            (self._btn_regime_promote,  "#1a4a1a"),
            (self._btn_regime_rollback, "#4a1a1a"),
        ]:
            btn.setStyleSheet(
                "QPushButton{background:%s; color:#ddd; border:1px solid #555; "
                "padding:4px 10px; border-radius:3px;}" % color
            )
            regime_btn_lay.addWidget(btn)
        regime_btn_lay.addStretch()
        self._btn_regime_promote.clicked.connect(self._on_regime_promote_clicked)
        self._btn_regime_rollback.clicked.connect(self._on_regime_rollback_clicked)
        top_lay.addLayout(regime_btn_lay)
        splitter.addWidget(top_box)

        # ── 하단: 전체 도전자 성과 ───────────────────────────────
        bot_box = QGroupBox("전체 도전자 성과")
        bot_box.setStyleSheet(
            "QGroupBox{color:#aaa; border:1px solid #333; margin-top:6px; padding:4px;}"
            "QGroupBox::title{subcontrol-origin:margin; left:8px;}"
        )
        bot_lay = QVBoxLayout(bot_box)
        bot_lay.setContentsMargins(4, 8, 4, 4)

        self._champion_lbl = QLabel("챔피언: —")
        self._champion_lbl.setStyleSheet(
            "font-size:11px; font-weight:bold; color:#f0c060; padding:2px;"
        )
        bot_lay.addWidget(self._champion_lbl)

        self._table = QTableWidget(0, len(CHALLENGER_COLS))
        self._table.setHorizontalHeaderLabels([c[0] for c in CHALLENGER_COLS])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setStyleSheet(
            "QTableWidget{background:#1a1a1a; gridline-color:#333;}"
            "QHeaderView::section{background:#222; color:#aaa; padding:3px;}"
            "QTableWidget::item{padding:2px;}"
            "QTableWidget::item:selected{background:#2a4a6a;}"
        )
        for i, (_, w) in enumerate(CHALLENGER_COLS):
            self._table.setColumnWidth(i, w)
        self._table.itemSelectionChanged.connect(self._on_row_selected)
        bot_lay.addWidget(self._table, 2)

        # 승격 조건 체크
        crit_box = QGroupBox("선택 도전자 승격 조건")
        crit_box.setStyleSheet(
            "QGroupBox{color:#888; border:1px solid #2a2a2a; margin-top:4px; padding:2px;}"
            "QGroupBox::title{subcontrol-origin:margin; left:8px;}"
        )
        crit_lay = QVBoxLayout(crit_box)
        crit_lay.setSpacing(1)
        self._crit_labels = {}
        for key, name, desc in [
            ("obs_days",  "관찰 기간",  "최소 20일"),
            ("trades",    "거래 횟수",  "최소 30건"),
            ("win_rate",  "승률 델타",  "챔피언 +2%"),
            ("mdd_ratio", "MDD 비율",   "챔피언 90%"),
            ("sharpe",    "Sharpe",     "1.5 이상"),
            ("return",    "수익 델타",  "챔피언 이상"),
        ]:
            lbl = QLabel("— %s: %s" % (name, desc))
            lbl.setStyleSheet("font-size:10px; padding:1px 4px;")
            crit_lay.addWidget(lbl)
            self._crit_labels[key] = lbl
        bot_lay.addWidget(crit_box)

        # 스파크라인
        self._spark_lbl = QTextEdit()
        self._spark_lbl.setReadOnly(True)
        self._spark_lbl.setMaximumHeight(50)
        self._spark_lbl.setStyleSheet(
            "background:#0a0a0a; color:#66bb6a; font-size:10px; "
            "font-family:Consolas,monospace; border:1px solid #333;"
        )
        bot_lay.addWidget(self._spark_lbl)

        # 전체 버튼
        btn_lay = QHBoxLayout()
        self._btn_promote  = QPushButton("▶ 전역 승격")
        self._btn_pause    = QPushButton("⏸ 관찰 중단")
        self._btn_report   = QPushButton("📋 리포트")
        self._btn_rollback = QPushButton("🔄 전역 롤백")
        for btn, color in [
            (self._btn_promote,  "#1a5c1a"),
            (self._btn_pause,    "#3a3a00"),
            (self._btn_report,   "#1a3a5c"),
            (self._btn_rollback, "#5c1a1a"),
        ]:
            btn.setStyleSheet(
                "QPushButton{background:%s; color:#ddd; border:1px solid #555; "
                "padding:4px 8px; border-radius:3px;}" % color
            )
            btn_lay.addWidget(btn)
        self._btn_promote.clicked.connect(self._on_promote_clicked)
        self._btn_pause.clicked.connect(self._on_pause_clicked)
        self._btn_report.clicked.connect(self._on_report_clicked)
        self._btn_rollback.clicked.connect(self._on_rollback_clicked)
        bot_lay.addLayout(btn_lay)

        splitter.addWidget(bot_box)
        splitter.setSizes([220, 420])
        root.addWidget(splitter)

    # ── 외부 호출 API ────────────────────────────────────────────

    def update_micro_regime(self, regime, adx=0.0, atr_ratio=1.0, duration=0):
        # type: (str, float, float, int) -> None
        """매분 미시 레짐 상태 갱신 (main.py → dashboard → here)"""
        _COL = {
            "추세장": "#00c878",
            "횡보장": "#4488ff",
            "급변장": "#ff4444",
            "혼합":   "#f0c060",
            "탈진":   "#ce93d8",
        }
        label = REGIME_LABEL.get(regime, regime)
        col   = _COL.get(regime, "#aaaaaa")
        self._lbl_cur_regime.setText(
            "현재 레짐: %s  |  ADX: %.1f  |  ATR비: %.2f  |  지속: %d분"
            % (label, adx, atr_ratio, duration)
        )
        self._lbl_cur_regime.setStyleSheet(
            "background:#1a1a2a; color:%s; border:1px solid #444;"
            "border-radius:3px; padding:3px 8px; font-weight:bold;" % col
        )

    # ── 데이터 갱신 ──────────────────────────────────────────────

    def refresh(self):
        try:
            self._refresh_inner()
        except Exception:
            logger.warning("[ChallengerPanel] refresh 예외:\n%s", traceback.format_exc())

    def _refresh_inner(self):
        if self._engine is None:
            return
        self._refresh_regime_table()
        self._refresh_challenger_table()
        self._update_criteria_panel(None)

    # ── 레짐 전문가 승위표 ────────────────────────────────────────

    def _refresh_regime_table(self):
        from challenger.challenger_registry import REGIME_POOLS
        db  = self._engine.db
        reg = self._engine.registry

        rows = []
        for regime, pool in REGIME_POOLS.items():
            if not pool:
                rows.append({
                    "regime": regime, "rank": [], "champion": None,
                    "rank1_changed": False,
                })
                continue
            ranking      = db.get_regime_ranking(regime, pool)
            champion_id  = reg.get_regime_champion(regime)
            shadow_rank1 = reg.get_regime_shadow_rank1(regime)
            # 1위 변경 여부는 rank_history에서
            hist = db.get_latest_regime_rank(regime)
            rank1_changed = bool(hist and hist["changed"]) if hist else False
            rows.append({
                "regime":        regime,
                "ranking":       ranking,
                "champion_id":   champion_id,
                "shadow_rank1":  shadow_rank1,
                "rank1_changed": rank1_changed,
            })

        self._regime_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            regime      = row["regime"]
            ranking     = row.get("ranking", [])
            champion_id = row.get("champion_id")
            shadow_r1   = row.get("shadow_rank1")
            changed     = row.get("rank1_changed", False)

            # 1위 정보
            rank1 = ranking[0] if ranking else {}
            rank1_id = rank1.get("challenger_id", "—")
            rank1_wr = rank1.get("win_rate", 0.0)
            rank1_tc = rank1.get("trade_count", 0)
            rank1_sh = rank1.get("sharpe", 0.0)
            rank1_pnl = rank1.get("total_pnl_pt", 0.0)

            cells = [
                REGIME_LABEL.get(regime, regime),
                NAME_MAP.get(rank1_id, rank1_id),
                str(rank1_tc),
                "%.1f%%" % rank1_wr if rank1_tc > 0 else "—",
                "%+.1f" % rank1_pnl if rank1_tc > 0 else "—",
                "%.2f" % rank1_sh if rank1_tc > 0 else "—",
                NAME_MAP.get(champion_id or "", "없음"),
                "🔴 변경!" if changed else "—",
            ]

            bg = C_RANK1_NEW if changed else (C_RANK1 if rank1_id == shadow_r1 else None)

            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, regime)
                if bg:
                    item.setBackground(QBrush(bg))
                if c == 7 and changed:
                    item.setForeground(QBrush(C_WARN))
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                self._regime_table.setItem(r, c, item)

    # ── 전체 도전자 테이블 ────────────────────────────────────────

    def _refresh_challenger_table(self):
        db       = self._engine.db
        registry = self._engine.registry
        champ_id = registry.get_champion_id()
        champ_m  = db.get_metrics_summary(champ_id)

        self._champion_lbl.setText(
            "챔피언: %s | 거래 %d건 | 승률 %.1f%% | 누적 %.1fpt | Sharpe %.2f" % (
                champ_id,
                champ_m.get("trade_count", 0),
                champ_m.get("win_rate", 0.0),
                champ_m.get("cum_pnl_pt", 0.0),
                champ_m.get("sharpe", 0.0),
            )
        )

        all_ids = [champ_id] + [c.challenger_id for c in registry.active_challengers()
                                if c.challenger_id != champ_id]
        self._table.setRowCount(len(all_ids))
        for r, cid in enumerate(all_ids):
            c_obj    = registry.get(cid)
            name     = NAME_MAP.get(cid, cid)
            m        = db.get_metrics_summary(cid)
            is_champ = (cid == champ_id)
            promo_ok = (not is_champ) and self._check_promotion_ready(m, champ_m)

            status = "챔피언" if is_champ else ("승격가능" if promo_ok else "관찰중")
            if c_obj and not c_obj.active:
                status = "중단"

            cells = [
                ("★ " if is_champ else "  ") + name,
                str(m["obs_days"]),
                str(m["trade_count"]),
                "%.1f%%" % m["win_rate"],
                "%+.1f" % m["cum_pnl_pt"],
                "%.1f" % m["cum_mdd_pt"],
                "%.2f" % m["sharpe"] if m["sharpe"] else "—",
                status,
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, cid)
                if is_champ:
                    item.setBackground(QBrush(C_CHAMPION))
                elif promo_ok:
                    item.setBackground(QBrush(C_PROMOTE))
                if not is_champ:
                    if c == 3:
                        if m["win_rate"] > champ_m.get("win_rate", 0) + 0.1:
                            item.setForeground(QBrush(C_UP))
                            item.setText("%.1f%%▲" % m["win_rate"])
                        elif m["win_rate"] < champ_m.get("win_rate", 0) - 2.0:
                            item.setForeground(QBrush(C_DOWN))
                            item.setText("%.1f%%▼" % m["win_rate"])
                self._table.setItem(r, c, item)

    # ── 승격 조건 체크 ────────────────────────────────────────────

    def _check_promotion_ready(self, m, champ_m):
        cr = PROMOTION_CRITERIA
        return all([
            m["obs_days"]    >= cr["min_obs_days"],
            m["trade_count"] >= cr["min_trades"],
            (m["win_rate"] - champ_m.get("win_rate", 0)) >= cr["win_rate_delta"],
            (champ_m.get("cum_mdd_pt", 0) == 0 or
             abs(m["cum_mdd_pt"]) <= abs(champ_m.get("cum_mdd_pt", 0)) * cr["mdd_ratio"]),
            m["sharpe"] >= cr["sharpe_min"],
            m["cum_pnl_pt"] >= champ_m.get("cum_pnl_pt", 0) + cr["return_delta"],
        ])

    def _update_criteria_panel(self, champ_summary=None):
        if self._selected_cid is None or self._engine is None:
            for lbl in self._crit_labels.values():
                lbl.setStyleSheet("font-size:10px; padding:1px 4px; color:#555;")
            return
        db = self._engine.db
        m  = db.get_metrics_summary(self._selected_cid)
        cs = champ_summary or db.get_metrics_summary(self._engine.registry.get_champion_id())
        cr = PROMOTION_CRITERIA

        checks = {
            "obs_days":  m["obs_days"]    >= cr["min_obs_days"],
            "trades":    m["trade_count"] >= cr["min_trades"],
            "win_rate":  (m["win_rate"] - cs.get("win_rate", 0)) >= cr["win_rate_delta"],
            "mdd_ratio": (cs.get("cum_mdd_pt", 0) == 0 or
                          abs(m["cum_mdd_pt"]) <= abs(cs.get("cum_mdd_pt", 0)) * cr["mdd_ratio"]),
            "sharpe":    m["sharpe"] >= cr["sharpe_min"],
            "return":    m["cum_pnl_pt"] >= cs.get("cum_pnl_pt", 0) + cr["return_delta"],
        }
        label_defs = [
            ("obs_days",  "관찰 기간",  "%d/%d일"   % (m["obs_days"], cr["min_obs_days"])),
            ("trades",    "거래 횟수",  "%d/%d건"   % (m["trade_count"], cr["min_trades"])),
            ("win_rate",  "승률 델타",  "%+.1f%%"  % (m["win_rate"] - cs.get("win_rate", 0))),
            ("mdd_ratio", "MDD 비율",   "%.1f/%.1fpt" % (abs(m["cum_mdd_pt"]), abs(cs.get("cum_mdd_pt", 0)))),
            ("sharpe",    "Sharpe",     "%.2f/%.2f"  % (m["sharpe"], cr["sharpe_min"])),
            ("return",    "수익 델타",  "%+.1fpt"  % (m["cum_pnl_pt"] - cs.get("cum_pnl_pt", 0))),
        ]
        for key, name, val in label_defs:
            ok  = checks[key]
            lbl = self._crit_labels.get(key)
            if lbl:
                icon  = "✅" if ok else "❌"
                color = "#00c878" if ok else "#ff6666"
                lbl.setText("%s %s: %s" % (icon, name, val))
                lbl.setStyleSheet("font-size:10px; padding:1px 4px; color:%s;" % color)
        self._update_sparkline()

    def _update_sparkline(self):
        if self._engine is None or self._selected_cid is None:
            return
        rows = self._engine.db.get_daily_metrics_list(self._selected_cid, limit=30)
        if not rows:
            self._spark_lbl.setPlainText("(데이터 없음)")
            return
        vals = [r["cum_pnl_pt"] or 0.0 for r in rows]
        self._spark_lbl.setPlainText(self._ascii_spark(vals, self._selected_cid))

    @staticmethod
    def _ascii_spark(values, label=""):
        if not values:
            return ""
        lo, hi = min(values), max(values)
        span   = hi - lo or 1.0
        blocks = " ▁▂▃▄▅▆▇█"
        line   = "".join(blocks[int((v - lo) / span * 8)] for v in values)
        return "%s | %s | %.1f→%.1f pt" % (label[:14], line, values[0], values[-1])

    # ── 이벤트 핸들러 ─────────────────────────────────────────────

    def _on_regime_row_selected(self):
        rows = self._regime_table.selectedItems()
        if rows:
            self._selected_regime = rows[0].data(Qt.UserRole)

    def _on_row_selected(self):
        rows = self._table.selectedItems()
        if rows:
            self._selected_cid = rows[0].data(Qt.UserRole)
            self._update_criteria_panel()

    # ── 레짐 전문가 승격/롤백 ─────────────────────────────────────

    def _on_regime_promote_clicked(self):
        if self._selected_regime is None:
            QMessageBox.warning(self, "레짐 승격", "레짐 전문가 테이블에서 레짐을 선택하세요.")
            return
        if self._engine is None or self._promo is None:
            return

        regime  = self._selected_regime
        ranking = self._promo.get_regime_ranking(regime)
        if not ranking:
            QMessageBox.information(self, "레짐 승격", "[%s] 전문가 풀에 데이터가 없습니다." % regime)
            return

        rank1_id = ranking[0]["challenger_id"]
        result   = self._promo.evaluate_regime_specialist(rank1_id, regime)

        if result.status != "READY":
            failed = "\n".join("❌ %s" % f for f in result.failed)
            QMessageBox.warning(self, "레짐 승격 불가",
                                "[%s] %s 조건 미충족:\n%s" % (regime, rank1_id, failed))
            return

        dlg = _RegimePromotionDialog(rank1_id, regime, result, self)
        if dlg.exec_() == QDialog.Accepted:
            self._promo.promote_regime_specialist(rank1_id, regime)
            QMessageBox.information(self, "레짐 승격 완료",
                                    "[%s] %s 전문가 승격 완료." % (regime, rank1_id))
            self.refresh()

    def _on_regime_rollback_clicked(self):
        if self._selected_regime is None:
            QMessageBox.warning(self, "레짐 롤백", "레짐을 먼저 선택하세요.")
            return
        if self._promo is None:
            return
        reply = QMessageBox.question(
            self, "레짐 롤백",
            "[%s] 레짐 전문가를 이전으로 복구합니까?" % self._selected_regime,
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            ok, msg = self._promo.rollback_regime_specialist(self._selected_regime)
            if ok:
                QMessageBox.information(self, "완료", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "실패", msg)

    # ── 전역 승격/롤백 ────────────────────────────────────────────

    def _on_promote_clicked(self):
        if self._selected_cid is None:
            QMessageBox.warning(self, "전역 승격", "도전자를 먼저 선택하세요.")
            return
        if self._promo is None:
            return
        result = self._promo.evaluate_for_promotion(self._selected_cid)
        if result.status != "READY":
            failed = "\n".join("❌ %s" % f for f in result.failed)
            QMessageBox.warning(self, "전역 승격 불가", "조건 미충족:\n" + failed)
            return
        dlg = _PromotionDialog(self._selected_cid, result, self)
        if dlg.exec_() == QDialog.Accepted:
            self._promo.promote(self._selected_cid)
            QMessageBox.information(self, "전역 승격 완료",
                                    "%s 전역 챔피언 승격 완료." % self._selected_cid)
            self.refresh()

    def _on_pause_clicked(self):
        if self._selected_cid is None:
            QMessageBox.warning(self, "관찰 중단", "도전자를 선택하세요.")
            return
        reply = QMessageBox.question(
            self, "관찰 중단",
            "%s 의 관찰을 중단합니까?" % self._selected_cid,
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes and self._engine:
            self._engine.registry.set_active(self._selected_cid, False)
            self.refresh()

    def _on_report_clicked(self):
        if self._selected_cid is None or self._engine is None:
            return
        m = self._engine.db.get_metrics_summary(self._selected_cid)
        lines = [
            "=== %s 상세 리포트 ===" % self._selected_cid,
            "관찰 일수:  %d일" % m["obs_days"],
            "총 거래:    %d건" % m["trade_count"],
            "승률:       %.1f%%" % m["win_rate"],
            "누적 수익:  %+.2fpt" % m["cum_pnl_pt"],
            "누적 MDD:   %.2fpt" % m["cum_mdd_pt"],
            "Sharpe:     %.2f"   % m["sharpe"],
        ]
        dlg = QDialog(self)
        dlg.setWindowTitle("상세 리포트")
        lay = QVBoxLayout(dlg)
        te  = QTextEdit()
        te.setReadOnly(True)
        te.setPlainText("\n".join(lines))
        lay.addWidget(te)
        btn = QPushButton("닫기")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)
        dlg.resize(380, 280)
        dlg.exec_()

    def _on_rollback_clicked(self):
        if self._promo is None:
            return
        reply = QMessageBox.question(
            self, "전역 롤백",
            "직전 전역 챔피언으로 복구합니까?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            ok, msg = self._promo.rollback()
            QMessageBox.information(self, "완료" if ok else "실패", msg)
            if ok:
                self.refresh()


# ── 다이얼로그 ────────────────────────────────────────────────

class _RegimePromotionDialog(QDialog):
    def __init__(self, cid, regime, result, parent=None):
        super(_RegimePromotionDialog, self).__init__(parent)
        self.setWindowTitle("[%s] 레짐 전문가 승격 확인" % regime)
        self.resize(380, 260)
        lay = QVBoxLayout(self)

        lbl = QLabel("<b>[%s] %s</b> 를 레짐 전문가로 승격합니까?" % (regime, cid))
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)

        for key, ok in result.checks.items():
            icon  = "✅" if ok else "❌"
            color = "#00c878" if ok else "#ff6666"
            row   = QLabel("%s  %s" % (icon, key))
            row.setStyleSheet("color:%s; font-size:11px;" % color)
            lay.addWidget(row)

        warn = QLabel("⚠ 승격 후 해당 레짐 진입은 이 전문가가 실거래를 담당합니다.")
        warn.setStyleSheet("color:#f0c060; font-size:10px; margin-top:6px;")
        warn.setWordWrap(True)
        lay.addWidget(warn)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)


class _PromotionDialog(QDialog):
    def __init__(self, cid, result, parent=None):
        super(_PromotionDialog, self).__init__(parent)
        self.setWindowTitle("전역 챔피언 승격 확인")
        self.resize(380, 260)
        lay = QVBoxLayout(self)

        lbl = QLabel("<b>%s</b> 를 전역 챔피언으로 승격합니까?" % cid)
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)

        for key, ok in result.checks.items():
            icon  = "✅" if ok else "❌"
            color = "#00c878" if ok else "#ff6666"
            row   = QLabel("%s  %s" % (icon, key))
            row.setStyleSheet("color:%s; font-size:11px;" % color)
            lay.addWidget(row)

        warn = QLabel("⚠ 승격 직후 1~2일은 포지션 사이즈 70% 권장.")
        warn.setStyleSheet("color:#f0c060; font-size:10px; margin-top:6px;")
        warn.setWordWrap(True)
        lay.addWidget(warn)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)
