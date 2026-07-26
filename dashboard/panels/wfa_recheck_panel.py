# dashboard/panels/wfa_recheck_panel.py — 26주 Walk-Forward 재검증 주기 알림 패널
"""
WFARecheckPanel:
  CLAUDE.md "주기적 재검증 항목"(실전전환기준 ③ 26주 Walk-Forward 편입)에 등록된
  파라미터들이 "재검토하기로 했는데 안 함" 상태로 방치되지 않도록, 마지막 재검증일
  + 26주 경과 여부만 추적하는 가벼운 캘린더 알림.

  다른 3개 재보정 모니터(threshold/atr_ceiling/entry_horizon)와 달리 매주 시장
  데이터를 재계산하지 않는다 — 대상(Hurst/PSI)의 실제 재검증은 스크립트를 사람이
  수동 실행해야 하는 별도 분석 작업(hurst_oos_validation.py 등)이라, 이 패널은
  "언제 마지막으로 했고 다음은 언제 해야 하는지"만 상기시킨다.

  config/settings.py:WFA_RECHECK_ITEMS 의 last_check 를 실제 재검증 완료 후
  사람이 오늘 날짜로 수동 갱신하면 카운트다운이 리셋된다.
"""
import logging
import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QFrame, QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer

logger = logging.getLogger("SYSTEM")

_COL = {
    "bg":        "#0d1117",
    "bg2":       "#161b22",
    "border":    "#30363d",
    "text":      "#e6edf3",
    "muted":     "#8b949e",
    "green":     "#3fb950",
    "yellow":    "#e3b341",
    "red":       "#f85149",
}

_WATCH_DAYS_BEFORE = 28  # 마감 4주 전부터 WATCHLIST


class WFARecheckPanel(QWidget):
    """26주 Walk-Forward 재검증 주기 알림 패널 (5분 자동 갱신, DB 미사용)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(300_000)  # 5분
        self.refresh()

    # ── 레이아웃 ─────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        info = QLabel(
            "CLAUDE.md \"주기적 재검증 항목\"(실전전환기준 ③) 등록 파라미터 — "
            "26주(약 6개월)마다 시장 실측치 기준 여전히 유효한지 재검증 필요"
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{_COL['muted']};font-size:10px;")
        root.addWidget(info)

        grp = QGroupBox("재검증 대상")
        grp.setStyleSheet(
            f"QGroupBox{{color:{_COL['muted']};border:1px solid {_COL['border']};"
            f"margin-top:6px;font-size:11px;}}"
            f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;}}"
        )
        self._grp_lay = QVBoxLayout(grp)
        self._grp_lay.setSpacing(6)
        self._item_cards = {}

        from config.settings import WFA_RECHECK_ITEMS
        for key, cfg in WFA_RECHECK_ITEMS.items():
            card = self._item_card(cfg["label"], cfg.get("note", ""))
            self._item_cards[key] = card
            self._grp_lay.addWidget(card["frame"])

        root.addWidget(grp)
        root.addStretch()

    def _item_card(self, label: str, note: str) -> dict:
        frame = QFrame()
        frame.setStyleSheet(
            f"background:{_COL['bg2']};border:1px solid {_COL['border']};border-radius:4px;"
        )
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(3)

        top = QHBoxLayout()
        lbl_label = QLabel(label)
        lbl_label.setStyleSheet(f"color:{_COL['text']};font-size:12px;font-weight:bold;")
        lbl_alert = QLabel("CLEAR")
        lbl_alert.setStyleSheet(
            f"color:{_COL['green']};background:{_COL['bg']};"
            f"border:1px solid {_COL['green']};border-radius:4px;padding:1px 8px;font-size:10px;font-weight:bold;"
        )
        top.addWidget(lbl_label)
        top.addStretch()
        top.addWidget(lbl_alert)
        lay.addLayout(top)

        lbl_detail = QLabel("마지막 재검증: — / 다음 재검증: —")
        lbl_detail.setStyleSheet(f"color:{_COL['muted']};font-size:10px;")
        lay.addWidget(lbl_detail)

        if note:
            lbl_note = QLabel(f"재검증 방법: {note}")
            lbl_note.setWordWrap(True)
            lbl_note.setStyleSheet(f"color:{_COL['muted']};font-size:9px;")
            lay.addWidget(lbl_note)

        return {"frame": frame, "alert": lbl_alert, "detail": lbl_detail}

    # ── 갱신 ─────────────────────────────────────────────────────
    def refresh(self):
        from config.settings import WFA_RECHECK_ITEMS, WFA_RECHECK_CYCLE_WEEKS
        today = datetime.date.today()

        for key, cfg in WFA_RECHECK_ITEMS.items():
            card = self._item_cards.get(key)
            if not card:
                continue
            try:
                last_dt = datetime.date.fromisoformat(cfg["last_check"])
            except Exception:
                continue
            next_dt = last_dt + datetime.timedelta(weeks=WFA_RECHECK_CYCLE_WEEKS)
            remain = (next_dt - today).days

            if remain <= 0:
                alert, col = "UPDATE", _COL["red"]
                remain_txt = f"기한 {abs(remain)}일 초과"
            elif remain <= _WATCH_DAYS_BEFORE:
                alert, col = "WATCHLIST", _COL["yellow"]
                remain_txt = f"{remain}일 남음"
            else:
                alert, col = "CLEAR", _COL["green"]
                remain_txt = f"{remain}일 남음"

            card["alert"].setText(alert)
            card["alert"].setStyleSheet(
                f"color:{col};background:{_COL['bg']};"
                f"border:1px solid {col};border-radius:4px;padding:1px 8px;font-size:10px;font-weight:bold;"
            )
            card["detail"].setText(
                f"마지막 재검증: {last_dt.isoformat()}  →  "
                f"다음 재검증: {next_dt.isoformat()} ({remain_txt})"
            )
