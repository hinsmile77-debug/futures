# dashboard/strategy_dashboard_tab.py — 🧭 전략 운용현황 패널
"""
전략 버전 운용현황 관제 탭 (PyQt5).

구성:
  ┌──────────────────────────────────────────────────────────────────────┐
  │ [헤더] 현재 전략 카드 / 버전·상태 배지 / CUSUM 드리프트 경보         │
  ├────────────────┬──────────────────────────────┬──────────────────────┤
  │ 단계별 성과    │ 현재 vs 이전 비교 델타        │ 레짐×시간대 매트릭스 │
  │ BT/WFA/SIM/Live│ Sharpe·MDD·WR·PF 변화량      │ 기대값 히트맵        │
  ├────────────────┴──────────────────────────────┴──────────────────────┤
  │ 파라미터 변경 이력 테이블                                             │
  ├──────────────────────────────────────────────────────────────────────┤
  │ 전략 평가 로그 (버전 교체 근거·결정·메모)                             │
  └──────────────────────────────────────────────────────────────────────┘

의존성:
  config/strategy_registry.py  — StrategyRegistry (데이터 레이어)
  strategy/param_drift_detector.py — DriftLevel (경보 수준 상수)
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QScrollArea, QSizePolicy, QSplitter, QTableWidget,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
)

try:
    from config.strategy_registry import (
        StrategyRegistry, get_registry,
        VERDICT_OUTPERFORM, VERDICT_NORMAL, VERDICT_UNDERPERFORM,
    )
    from strategy.param_drift_detector import DriftLevel, get_drift_detector
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False

logger = logging.getLogger(__name__)


# ── 색상 팔레트 (main_dashboard.py 의 C 딕셔너리와 동일) ────────────────
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
    "lime":     "#7EE787",
}


# ── 판정·레짐 색상 매핑 ──────────────────────────────────────────────────
_VERDICT_COLOR = {
    VERDICT_OUTPERFORM:   C["cyan"],
    VERDICT_NORMAL:       C["blue"],
    VERDICT_UNDERPERFORM: C["red"],
    "INSUFFICIENT":       C["text2"],
}
_VERDICT_KOR = {
    VERDICT_OUTPERFORM:   "▲ 기대값 상회",
    VERDICT_NORMAL:       "● 기대값 부합",
    VERDICT_UNDERPERFORM: "▼ 기대값 하회",
    "INSUFFICIENT":       "⏳ 데이터 부족",
}

# 레짐×시간대 매트릭스 레이블
_REGIMES    = ["RISK_ON", "NEUTRAL", "RISK_OFF"]
_TIME_SLOTS = ["OPEN_VOL", "STABLE_TREND", "LUNCH", "CLOSE_VOL"]
_TS_KOR     = {
    "OPEN_VOL":     "시가 변동",
    "STABLE_TREND": "안정 추세",
    "LUNCH":        "점심 회복",
    "CLOSE_VOL":    "마감 변동",
}
_REGIME_KOR = {
    "RISK_ON":  "위험선호",
    "NEUTRAL":  "중립",
    "RISK_OFF": "위험회피",
}


# ─────────────────────────────────────────────────────────────────────────
# 헬퍼 위젯 팩토리
# ─────────────────────────────────────────────────────────────────────────
def _S(px: int) -> int:
    """스크린 스케일 적용 — main_dashboard 의 S.p() 대용 (임포트 없이 동작)."""
    try:
        from dashboard.main_dashboard import S
        return S.p(px)
    except ImportError:
        return px


def _lbl(text: str, color: str = C["text"], size: int = 12,
         bold: bool = False, align=Qt.AlignLeft) -> QLabel:
    w = QLabel(text)
    w.setAlignment(align)
    weight = "bold" if bold else "normal"
    w.setStyleSheet(
        f"color:{color};font-size:{size}px;font-weight:{weight};"
        "font-family:Consolas,D2Coding,monospace;"
    )
    return w


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"color:{C['border']};")
    return f


def _card(title: str, child: QWidget, title_color: str = C["text2"]) -> QFrame:
    outer = QFrame()
    outer.setStyleSheet(
        f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};"
        "border-radius:6px;}}"
    )
    lay = QVBoxLayout(outer)
    lay.setContentsMargins(_S(8), _S(6), _S(8), _S(8))
    lay.setSpacing(_S(4))

    hdr = QLabel(title)
    hdr.setStyleSheet(
        f"color:{title_color};font-size:11px;font-weight:bold;"
        "font-family:Consolas,D2Coding,monospace;"
        f"border-bottom:1px solid {C['border']};padding-bottom:3px;"
    )
    lay.addWidget(hdr)
    lay.addWidget(child)
    return outer


def _badge(text: str, color: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(
        f"color:{C['bg']};background:{color};border-radius:3px;"
        f"padding:2px 6px;font-size:11px;font-weight:bold;"
        "font-family:Consolas,D2Coding,monospace;"
    )
    lbl.setFixedHeight(_S(22))
    return lbl


# ─────────────────────────────────────────────────────────────────────────
# 헤더 카드: 현재 전략 상태 + CUSUM 경보
# ─────────────────────────────────────────────────────────────────────────
class _HeaderCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"QFrame{{background:{C['bg3']};border:1px solid {C['border']};"
            "border-radius:8px;}}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(_S(12), _S(10), _S(12), _S(10))
        lay.setSpacing(_S(20))

        # 좌: 버전명 + 승격일 + 액션 배지 + 모니터링 배너
        left = QVBoxLayout()
        self._lbl_ver     = _lbl("v—", C["cyan"], 22, bold=True)
        self._lbl_prev    = _lbl("이전: —", C["text2"], 11)
        self._lbl_date    = _lbl("승격: —", C["text2"], 11)
        self._lbl_note    = _lbl("", C["text2"], 10)
        self._badge_action  = _badge("● KEEP", C["green"])     # KEEP/WATCH/REPLACE/ROLLBACK
        self._lbl_monitor   = _lbl("", C["yellow"], 10)         # 교체 직후 모니터링 배너
        left.addWidget(self._lbl_ver)
        left.addWidget(self._lbl_prev)
        left.addWidget(self._lbl_date)
        left.addWidget(self._lbl_note)
        left.addWidget(self._badge_action)
        left.addWidget(self._lbl_monitor)
        left.addStretch()
        lay.addLayout(left)

        lay.addWidget(_sep_v())

        # 중: 실전 성과 요약 (Sharpe · MDD · 승률 · PF)
        mid = QGridLayout()
        mid.setSpacing(_S(6))
        metrics = [
            ("Sharpe", "_mv_sharpe"),
            ("MDD",    "_mv_mdd"),
            ("승률",   "_mv_wr"),
            ("PF",     "_mv_pf"),
        ]
        for col, (lbl_text, attr) in enumerate(metrics):
            mid.addWidget(_lbl(lbl_text, C["text2"], 10, align=Qt.AlignCenter), 0, col)
            val_lbl = _lbl("—", C["blue"], 18, bold=True, align=Qt.AlignCenter)
            setattr(self, attr, val_lbl)
            mid.addWidget(val_lbl, 1, col)
        lay.addLayout(mid)

        lay.addWidget(_sep_v())

        # 우: 판정 배지 + CUSUM 드리프트 배지 + PSI 배지 + 실전 일수
        right = QVBoxLayout()
        right.setSpacing(_S(5))
        self._badge_verdict = _badge("——", C["text2"])
        self._badge_drift   = _badge("● CLEAR", C["green"])
        self._badge_psi     = _badge("◆ PSI OK", C["green"])
        self._lbl_live_days = _lbl("실전 0일차", C["text2"], 10, align=Qt.AlignCenter)
        right.addStretch()
        right.addWidget(self._badge_verdict)
        right.addWidget(self._badge_drift)
        right.addWidget(self._badge_psi)
        right.addWidget(self._lbl_live_days)
        right.addStretch()
        lay.addLayout(right)

    def refresh(
        self,
        ver_info:    Optional[Dict[str, Any]],
        drift_level: int   = 0,
        psi_val:     float = 0.0,
        psi_level:   int   = 0,
    ) -> None:
        if not ver_info:
            return

        self._lbl_ver.setText(ver_info.get("version", "—"))
        prev = ver_info.get("previous_version", "")
        self._lbl_prev.setText("이전: %s" % (prev or "없음"))
        activated = ver_info.get("activated_at", "")
        if activated:
            self._lbl_date.setText("승격: %s" % activated[:16])
        note = ver_info.get("note", "")
        self._lbl_note.setText(note[:60] if note else "")

        # 실전 성과 지표
        live = ver_info.get("live_snapshot") or {}
        stages = ver_info.get("stages", {})
        src = live if live.get("sharpe") is not None else stages.get("WFA", {})

        def _fmt(key, fmt_str, suffix=""):
            v = src.get(key)
            return ("%s%s" % (fmt_str % v, suffix)) if v is not None else "—"

        sharpe_val = src.get("sharpe")
        self._mv_sharpe.setText(_fmt("sharpe", "%.2f"))
        self._mv_sharpe.setStyleSheet(
            _metric_color_style(sharpe_val, 1.5, 1.2, 18)
        )
        self._mv_mdd.setText(_fmt("mdd_pct", "%.1f%%", ""))
        mdd_raw = src.get("mdd_pct")
        if mdd_raw is not None:
            self._mv_mdd.setText("%.1f%%" % (abs(mdd_raw) * 100))
        self._mv_mdd.setStyleSheet(
            _mdd_color_style(abs(mdd_raw) * 100 if mdd_raw else None, 18)
        )
        wr = src.get("win_rate")
        self._mv_wr.setText("%.1f%%" % (wr * 100) if wr is not None else "—")
        self._mv_wr.setStyleSheet(_metric_color_style(wr, 0.56, 0.53, 18))

        pf = src.get("profit_factor")
        self._mv_pf.setText("%.2f" % pf if pf is not None else "—")
        self._mv_pf.setStyleSheet(_metric_color_style(pf, 1.3, 1.1, 18))

        # 판정 배지
        verdict = ver_info.get("verdict", "INSUFFICIENT")
        vcol = _VERDICT_COLOR.get(verdict, C["text2"])
        vkor = _VERDICT_KOR.get(verdict, "—")
        self._badge_verdict.setText(vkor)
        self._badge_verdict.setStyleSheet(
            f"color:{C['bg']};background:{vcol};border-radius:3px;"
            f"padding:2px 8px;font-size:11px;font-weight:bold;"
            "font-family:Consolas,D2Coding,monospace;"
        )

        # CUSUM 드리프트 배지
        drift_col  = DriftLevel.color(drift_level) if _DEPS_OK else C["green"]
        drift_name = DriftLevel.name(drift_level) if _DEPS_OK else "—"
        drift_icon = "● " if drift_level == 0 else ("⚠ " if drift_level < 3 else "⛔ ")
        self._badge_drift.setText("%s%s" % (drift_icon, drift_name))
        self._badge_drift.setStyleSheet(
            f"color:{C['bg']};background:{drift_col};border-radius:3px;"
            f"padding:2px 8px;font-size:11px;font-weight:bold;"
            "font-family:Consolas,D2Coding,monospace;"
        )

        live_days = ver_info.get("live_days", 0)
        self._lbl_live_days.setText("실전 %d일차" % live_days)

        # 권고 액션 배지 (verdict_engine)
        try:
            from strategy.ops.verdict_engine import (
                compute_action, ACTION_KOR, ACTION_COLORS,
            )
            _action, _reason = compute_action(
                verdict     = verdict,
                drift_level = drift_level,
                days_active = live_days,
                psi_level   = psi_level,
            )
            _acol = ACTION_COLORS.get(_action, C["text2"])
            _akor = ACTION_KOR.get(_action, _action)
            self._badge_action.setText(_akor)
            self._badge_action.setStyleSheet(
                f"color:{C['bg']};background:{_acol};border-radius:3px;"
                "padding:2px 6px;font-size:10px;font-weight:bold;"
                "font-family:Consolas,D2Coding,monospace;"
            )
            # 교체 직후 2주 모니터링 배너
            if 0 < live_days <= 14:
                self._lbl_monitor.setText(
                    "⏱ 교체 직후 모니터링 중 (%d/14일)" % live_days
                )
            else:
                self._lbl_monitor.setText("")
        except Exception:
            pass

        # RegimeFingerprint PSI 배지
        _PSI_COLORS = {0: C["green"], 1: C["yellow"], 2: C["orange"], 3: C["red"]}
        _PSI_ICONS  = {0: "◆ PSI OK", 1: "⚠ PSI WATCH", 2: "⚠ PSI ALARM", 3: "⛔ PSI CRIT"}
        psi_txt = "%s  %.3f" % (_PSI_ICONS.get(psi_level, "◆ PSI ?"), psi_val) if psi_val > 0 else _PSI_ICONS.get(psi_level, "◆ PSI OK")
        psi_col = _PSI_COLORS.get(psi_level, C["green"])
        self._badge_psi.setText(psi_txt)
        self._badge_psi.setStyleSheet(
            f"color:{C['bg']};background:{psi_col};border-radius:3px;"
            f"padding:2px 6px;font-size:10px;font-weight:bold;"
            "font-family:Consolas,D2Coding,monospace;"
        )


def _sep_v() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.VLine)
    f.setStyleSheet(f"color:{C['border']};max-width:1px;")
    return f


def _metric_color_style(val, good_thresh, warn_thresh, size=12) -> str:
    if val is None:
        return f"color:{C['text2']};font-size:{size}px;font-weight:bold;font-family:Consolas,D2Coding,monospace;"
    col = C["green"] if val >= good_thresh else (C["yellow"] if val >= warn_thresh else C["red"])
    return f"color:{col};font-size:{size}px;font-weight:bold;font-family:Consolas,D2Coding,monospace;"


def _mdd_color_style(pct, size=12) -> str:
    if pct is None:
        return f"color:{C['text2']};font-size:{size}px;font-weight:bold;font-family:Consolas,D2Coding,monospace;"
    col = C["green"] if pct <= 10 else (C["yellow"] if pct <= 15 else C["red"])
    return f"color:{col};font-size:{size}px;font-weight:bold;font-family:Consolas,D2Coding,monospace;"


# ─────────────────────────────────────────────────────────────────────────
# 단계별 성과 매트릭스 (BT / WFA / SIM / LIVE)
# ─────────────────────────────────────────────────────────────────────────
class _StageMatrix(QWidget):
    _STAGES   = ["BACKTEST", "WFA", "SIM", "LIVE"]
    _STAGE_KOR = {"BACKTEST": "백테스트", "WFA": "WFA", "SIM": "시뮬", "LIVE": "실전"}
    _METRICS   = [
        ("Sharpe", "sharpe",        "%.2f",  False),
        ("MDD",    "mdd_pct",       "%.1f%%", True),   # True = lower is better
        ("승률",   "win_rate",      "%.1f%%", False),
        ("PF",     "profit_factor", "%.2f",  False),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        self._tbl = QTableWidget(len(self._STAGES), len(self._METRICS) + 1)
        self._tbl.setHorizontalHeader(self._tbl.horizontalHeader())
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl.setSelectionMode(QTableWidget.NoSelection)
        self._tbl.setStyleSheet(
            f"QTableWidget{{background:{C['bg2']};color:{C['text']};"
            f"gridline-color:{C['border']};border:none;font-size:11px;"
            "font-family:Consolas,D2Coding,monospace;}"
            f"QHeaderView::section{{background:{C['bg3']};color:{C['text2']};"
            "font-size:10px;padding:3px;border:none;}}"
        )
        self._tbl.setFixedHeight(_S(140))

        headers = ["단계"] + [m[0] for m in self._METRICS]
        self._tbl.setHorizontalHeaderLabels(headers)

        # 단계 행 초기화
        for r, stage in enumerate(self._STAGES):
            item = QTableWidgetItem(self._STAGE_KOR[stage])
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QColor(C["blue"]))
            self._tbl.setItem(r, 0, item)
            for c in range(1, len(self._METRICS) + 1):
                itm = QTableWidgetItem("—")
                itm.setTextAlignment(Qt.AlignCenter)
                self._tbl.setItem(r, c, itm)

        lay.addWidget(self._tbl)

    def refresh(self, stages: Dict[str, Dict[str, Any]],
                live_snap: Optional[Dict[str, Any]]) -> None:
        data_map = dict(stages)
        if live_snap and live_snap.get("sharpe") is not None:
            data_map["LIVE"] = live_snap

        wfa_ref = stages.get("WFA", {})

        for r, stage in enumerate(self._STAGES):
            metrics = data_map.get(stage, {})
            for c, (_, key, fmt, lower_better) in enumerate(self._METRICS):
                val = metrics.get(key)
                if val is None:
                    txt = "—"
                    col = C["text2"]
                else:
                    if key == "mdd_pct":
                        txt = fmt % (abs(val) * 100)
                        col = _mdd_pct_color(abs(val) * 100)
                    elif key == "win_rate":
                        txt = fmt % (val * 100)
                        col = C["green"] if val >= 0.56 else (C["yellow"] if val >= 0.53 else C["red"])
                    else:
                        txt = fmt % val
                        # LIVE vs WFA 비교 색상
                        if stage == "LIVE" and wfa_ref.get(key) is not None:
                            delta = val - wfa_ref[key]
                            if lower_better:
                                col = C["green"] if delta < 0 else (C["yellow"] if delta < 0.02 else C["red"])
                            else:
                                col = C["green"] if delta >= 0.1 else (C["yellow"] if delta >= -0.2 else C["red"])
                        else:
                            col = C["text"]

                itm = QTableWidgetItem(txt)
                itm.setTextAlignment(Qt.AlignCenter)
                itm.setForeground(QColor(col))
                self._tbl.setItem(r, c + 1, itm)


def _mdd_pct_color(pct: float) -> str:
    return C["green"] if pct <= 10 else (C["yellow"] if pct <= 15 else C["red"])


# ─────────────────────────────────────────────────────────────────────────
# 이전 vs 현재 비교 델타 카드
# ─────────────────────────────────────────────────────────────────────────
class _VersionCompareDelta(QWidget):
    _KEYS = [
        ("Sharpe",   "sharpe_delta",   False, "%.2f"),
        ("MDD",      "mdd_pct_delta",  True,  "%.2f%%"),
        ("승률",     "win_rate_delta", False, "%.1f%%"),
        ("PF",       "pf_delta",       False, "%.2f"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(_S(4))

        self._rows: List[Dict[str, QLabel]] = []

        lay.addWidget(_lbl("지표",    C["text2"], 10, align=Qt.AlignCenter), 0, 0)
        lay.addWidget(_lbl("이전",    C["text2"], 10, align=Qt.AlignCenter), 0, 1)
        lay.addWidget(_lbl("→ 현재",  C["text2"], 10, align=Qt.AlignCenter), 0, 2)
        lay.addWidget(_lbl("변화",    C["text2"], 10, align=Qt.AlignCenter), 0, 3)

        for r, (name, _, _, _) in enumerate(self._KEYS, 1):
            lbl_name  = _lbl(name, C["text2"], 11)
            lbl_from  = _lbl("—", C["text"], 11, align=Qt.AlignCenter)
            lbl_to    = _lbl("—", C["text"], 11, align=Qt.AlignCenter)
            lbl_delta = _lbl("—", C["text2"], 11, bold=True, align=Qt.AlignCenter)
            lay.addWidget(lbl_name,  r, 0)
            lay.addWidget(lbl_from,  r, 1)
            lay.addWidget(lbl_to,    r, 2)
            lay.addWidget(lbl_delta, r, 3)
            self._rows.append({"from": lbl_from, "to": lbl_to, "delta": lbl_delta})

    def refresh(
        self,
        prev_info: Optional[Dict[str, Any]],
        curr_info: Optional[Dict[str, Any]],
        compare:   Optional[Dict[str, Any]] = None,
    ) -> None:
        def _extract(info):
            if not info:
                return {}
            live = info.get("live_snapshot") or {}
            if live.get("sharpe") is not None:
                return live
            return (info.get("stages") or {}).get("WFA", {})

        prev_m = _extract(prev_info)
        curr_m = _extract(curr_info)

        for i, (_, key_delta, lower_better, fmt) in enumerate(self._KEYS):
            key_raw = key_delta.replace("_delta", "")
            if key_raw == "mdd_pct":
                pv = abs(prev_m.get(key_raw, 0) or 0) * 100
                cv = abs(curr_m.get(key_raw, 0) or 0) * 100
                delta = cv - pv
            elif key_raw == "win_rate":
                pv = (prev_m.get(key_raw) or 0) * 100
                cv = (curr_m.get(key_raw) or 0) * 100
                delta = cv - pv
                fmt_val = "%.1f%%"
            else:
                pv = prev_m.get(key_raw)
                cv = curr_m.get(key_raw)
                delta = (cv - pv) if (pv is not None and cv is not None) else None
                fmt_val = fmt

            pv_txt = (fmt % pv) if pv is not None else "—"
            cv_txt = (fmt % cv) if cv is not None else "—"
            self._rows[i]["from"].setText(pv_txt)
            self._rows[i]["to"].setText(cv_txt)

            if delta is not None:
                sign   = "▲" if delta > 0 else ("▼" if delta < 0 else "●")
                d_txt  = "%s %.2f" % (sign, abs(delta))
                # 색상: MDD는 lower_better=True이므로 반전
                if lower_better:
                    col = C["green"] if delta < 0 else (C["yellow"] if delta < 0.02 else C["red"])
                else:
                    col = C["green"] if delta > 0 else (C["yellow"] if delta > -0.1 else C["red"])
                self._rows[i]["delta"].setText(d_txt)
                self._rows[i]["delta"].setStyleSheet(
                    f"color:{col};font-size:11px;font-weight:bold;"
                    "font-family:Consolas,D2Coding,monospace;"
                )
            else:
                self._rows[i]["delta"].setText("—")


# ─────────────────────────────────────────────────────────────────────────
# 레짐 × 시간대 기대값 매트릭스 (히트맵)
# ─────────────────────────────────────────────────────────────────────────
class _RegimeTimeMatrix(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        # 헤더 행
        lay.addWidget(_lbl("", C["text2"], 9), 0, 0)
        for c, ts in enumerate(_TIME_SLOTS, 1):
            lay.addWidget(
                _lbl(_TS_KOR[ts], C["text2"], 9, align=Qt.AlignCenter),
                0, c,
            )

        # 데이터 셀
        self._cells: Dict[tuple, QLabel] = {}
        for r, regime in enumerate(_REGIMES, 1):
            lay.addWidget(
                _lbl(_REGIME_KOR[regime], C["text2"], 9, bold=True),
                r, 0,
            )
            for c, ts in enumerate(_TIME_SLOTS, 1):
                cell = _lbl("—", C["text2"], 9, align=Qt.AlignCenter)
                cell.setFixedSize(_S(72), _S(36))
                cell.setStyleSheet(
                    f"background:{C['bg3']};border:1px solid {C['border']};"
                    f"border-radius:3px;color:{C['text2']};font-size:9px;"
                    "font-family:Consolas,D2Coding,monospace;"
                )
                lay.addWidget(cell, r, c)
                self._cells[(regime, ts)] = cell

    def refresh(self, matrix_rows: List[Dict[str, Any]]) -> None:
        # 초기화
        for cell in self._cells.values():
            cell.setText("—")
            cell.setStyleSheet(
                f"background:{C['bg3']};border:1px solid {C['border']};"
                f"border-radius:3px;color:{C['text2']};font-size:9px;"
                "font-family:Consolas,D2Coding,monospace;"
            )

        for row in matrix_rows:
            regime   = row.get("regime", "")
            ts_key   = row.get("time_slot", "")
            # time_slot 키 정규화 (OPEN_VOLATILE → OPEN_VOL 등)
            ts_short = _normalize_ts(ts_key)
            key      = (regime, ts_short)
            if key not in self._cells:
                continue

            cell     = self._cells[key]
            expectancy = row.get("expectancy", 0) or 0
            wr       = row.get("win_rate", 0) or 0
            n        = row.get("trade_count", 0) or 0

            # 기대값 등급 색상
            if expectancy >= 3000:
                bg_col = "#1A3A1A"   # 진한 초록
                tx_col = C["lime"]
            elif expectancy >= 1000:
                bg_col = "#1A2D1A"
                tx_col = C["green"]
            elif expectancy >= 0:
                bg_col = "#2D2A1A"
                tx_col = C["yellow"]
            elif expectancy >= -1000:
                bg_col = "#2D1E1A"
                tx_col = C["orange"]
            else:
                bg_col = "#2D1A1A"
                tx_col = C["red"]

            cell.setText("%.1f%%  %+.0f\n%d건" % (wr * 100, expectancy, n))
            cell.setStyleSheet(
                f"background:{bg_col};border:1px solid {C['border']};"
                f"border-radius:3px;color:{tx_col};font-size:9px;"
                "font-family:Consolas,D2Coding,monospace;"
            )


def _normalize_ts(ts: str) -> str:
    """time_slot 문자열을 _TIME_SLOTS 키로 정규화."""
    ts = ts.upper()
    if "OPEN" in ts:
        return "OPEN_VOL"
    if "STABLE" in ts or "TREND" in ts:
        return "STABLE_TREND"
    if "LUNCH" in ts or "RECOVERY" in ts:
        return "LUNCH"
    if "CLOSE" in ts:
        return "CLOSE_VOL"
    return ts


# ─────────────────────────────────────────────────────────────────────────
# 파라미터 변경 이력 테이블
# ─────────────────────────────────────────────────────────────────────────
class _ParamChangeTable(QWidget):
    _COLS = ["버전", "파라미터", "이전값", "→ 신규값", "변화량"]

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self._tbl = QTableWidget(0, len(self._COLS))
        self._tbl.setHorizontalHeaderLabels(self._COLS)
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl.setSelectionMode(QTableWidget.SingleSelection)
        self._tbl.setStyleSheet(
            f"QTableWidget{{background:{C['bg2']};color:{C['text']};"
            f"gridline-color:{C['border']};border:none;font-size:10px;"
            "font-family:Consolas,D2Coding,monospace;}"
            f"QHeaderView::section{{background:{C['bg3']};color:{C['text2']};"
            "font-size:10px;padding:2px;border:none;}}"
            f"QTableWidget::item:selected{{background:{C['bg3']};}}"
        )
        self._tbl.setFixedHeight(_S(180))
        lay.addWidget(self._tbl)

    def refresh(self, all_versions: List[Dict[str, Any]]) -> None:
        rows = []
        for ver_info in all_versions:
            ver = ver_info.get("version", "—")
            for chg in ver_info.get("changed_params", []):
                rows.append((
                    ver,
                    chg.get("param", ""),
                    chg.get("from", ""),
                    chg.get("to", ""),
                ))

        self._tbl.setRowCount(len(rows))
        for r, (ver, param, from_val, to_val) in enumerate(rows):
            try:
                fv = float(from_val)
                tv = float(to_val)
                delta_txt = "%+.4g" % (tv - fv)
                delta_col = C["green"] if tv > fv else C["red"]
            except (ValueError, TypeError):
                delta_txt = "—"
                delta_col = C["text2"]

            for c, (txt, col) in enumerate([
                (ver,       C["blue"]),
                (param,     C["text"]),
                (from_val,  C["text2"]),
                (to_val,    C["cyan"]),
                (delta_txt, delta_col),
            ]):
                itm = QTableWidgetItem(str(txt))
                itm.setTextAlignment(Qt.AlignCenter)
                itm.setForeground(QColor(col))
                self._tbl.setItem(r, c, itm)


# ─────────────────────────────────────────────────────────────────────────
# 전략 평가 로그 패널
# ─────────────────────────────────────────────────────────────────────────
class _StrategyLog(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFixedHeight(_S(150))
        self.setStyleSheet(
            f"background:{C['bg']};color:{C['text']};"
            "border:none;font-family:Consolas,D2Coding,monospace;font-size:10px;"
        )

    # event_type → 한국어 레이블
    _EVENT_KOR = {
        "VERSION_REGISTERED":  "버전 등록",
        "SHADOW_START":        "섀도우 시작",
        "HOTSWAP_APPROVED":    "Hot-Swap 승인",
        "HOTSWAP_DENIED":      "Hot-Swap 거부",
        "ROLLBACK":            "롤백",
        "REPLACE_CANDIDATE":   "교체 후보",
        "WATCH":               "모니터링 강화",
    }
    # event_type → 색상 (HTML)
    _EVENT_COLOR = {
        "VERSION_REGISTERED":  "#3FB950",
        "SHADOW_START":        "#79C0FF",
        "HOTSWAP_APPROVED":    "#3FB950",
        "HOTSWAP_DENIED":      "#E3B341",
        "ROLLBACK":            "#F85149",
        "REPLACE_CANDIDATE":   "#D29922",
        "WATCH":               "#E3B341",
    }

    def refresh(
        self,
        all_versions: List[Dict[str, Any]],
        event_log:    Optional[List[Dict]] = None,
    ) -> None:
        """
        전략 평가 로그 패널 갱신.

        event_log 가 제공되면 strategy_events 테이블 기반으로 표시.
        없으면 all_versions 기반 폴백.
        """
        if event_log:
            self._render_event_log(event_log)
        else:
            self._render_version_fallback(all_versions)

        sb = self.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())

    def _render_event_log(self, event_log: List[Dict]) -> None:
        lines = []
        for ev in event_log:
            at      = (ev.get("event_at") or "")[:16]
            etype   = ev.get("event_type", "")
            ver     = ev.get("version") or "—"
            msg     = ev.get("message") or ""
            note    = ev.get("note") or ""
            label   = self._EVENT_KOR.get(etype, etype)
            lines.append("[%s] %-16s  (%s)  %s%s" % (
                at, label, ver, msg[:60],
                ("  ※ " + note[:30]) if note else "",
            ))
        self.setPlainText("\n".join(lines) if lines else "— 이벤트 없음 —")

    def _render_version_fallback(self, all_versions: List[Dict]) -> None:
        lines = []
        for ver_info in reversed(all_versions):
            ver    = ver_info.get("version", "—")
            at     = (ver_info.get("activated_at") or "")[:16]
            note   = ver_info.get("note") or ""
            stages = ver_info.get("stages", {})
            wfa    = stages.get("WFA", {})
            live   = ver_info.get("live_snapshot") or {}

            lines.append("=" * 55)
            lines.append("[%s] %s 승격  %s" % (at, ver, note[:40]))

            chg_list = ver_info.get("changed_params", [])
            if chg_list:
                lines.append("  변경: " + ", ".join(
                    "%s %s→%s" % (c["param"], c["from"], c["to"])
                    for c in chg_list[:6]
                ))

            if wfa.get("sharpe") is not None:
                lines.append(
                    "  WFA: Sharpe=%.2f  MDD=%.1f%%  WR=%.1f%%  PF=%.2f" % (
                        wfa.get("sharpe", 0),
                        abs(wfa.get("mdd_pct") or 0) * 100,
                        (wfa.get("win_rate") or 0) * 100,
                        wfa.get("profit_factor") or 0,
                    )
                )
            if live.get("sharpe") is not None:
                verdict = ver_info.get("verdict", "")
                lines.append(
                    "  Live: Sharpe=%.2f  MDD=%.1f%%  WR=%.1f%%  판정=%s" % (
                        live.get("sharpe", 0),
                        abs(live.get("mdd_pct") or 0) * 100,
                        (live.get("win_rate") or 0) * 100,
                        verdict,
                    )
                )

        self.setPlainText("\n".join(lines) if lines else "— 기록 없음 —")


# ─────────────────────────────────────────────────────────────────────────
# CUSUM 드리프트 히스토리 미니 차트 (QLabel 기반 텍스트 시각화)
# ─────────────────────────────────────────────────────────────────────────
class _CusumMiniChart(QLabel):
    """최근 20일 CUSUM 값을 ASCII 바 차트로 표시."""

    _WIDTH  = 20
    _HEIGHT = 6   # 문자 행 높이

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"color:{C['cyan']};background:{C['bg3']};"
            "font-family:Consolas,monospace;font-size:10px;"
            "padding:4px;border-radius:3px;"
        )
        self.setText("— CUSUM 데이터 없음 —")
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    def refresh(self, history: list) -> None:
        """
        history: [(date, pnl, cusum_neg, level), ...]
        """
        if not history:
            self.setText("— 데이터 없음 —")
            return

        cusum_vals = [h[2] for h in history[-self._WIDTH:]]
        max_val    = max(cusum_vals) if cusum_vals else 1.0
        max_val    = max_val if max_val > 0 else 1.0

        # 임계값 라인
        h_watch = 2.0
        h_alarm = 4.0

        lines = []
        # 상단 레이블
        lines.append("  CUSUM (하방·성과저하 감지)  최근 %d일" % len(cusum_vals))
        lines.append("  ┤ h_crit=6 " + "─" * (self._WIDTH - 2))

        # 바 차트 (높은 값 = 위험)
        bar_rows = self._HEIGHT
        for row in range(bar_rows, 0, -1):
            threshold = max_val * row / bar_rows
            bar_line  = "  │"
            for val in cusum_vals:
                if val >= threshold:
                    # 레벨별 색 문자
                    if val >= 6.0:
                        bar_line += "█"
                    elif val >= h_alarm:
                        bar_line += "▓"
                    elif val >= h_watch:
                        bar_line += "▒"
                    else:
                        bar_line += "░"
                else:
                    bar_line += " "
            lines.append(bar_line)

        # 날짜 x축
        dates = [h[0][-5:] for h in history[-self._WIDTH:]]  # MM-DD
        if dates:
            step  = max(1, len(dates) // 4)
            x_row = "  └" + "".join(
                d[3:5] if i % step == 0 else " "
                for i, d in enumerate(dates)
            )
            lines.append(x_row)

        lines.append("  │ CLEAR<2  WATCH<4  ALARM<6  CRIT>=6")
        self.setText("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────
# 실전 일별 PnL 스파크라인 (롤링 성과 시각화)
# ─────────────────────────────────────────────────────────────────────────
class _LivePnlSparkline(QLabel):
    """최근 N일 일별 PnL 막대 차트 + 롤링 지표 요약."""

    _WIDTH  = 20
    _HEIGHT = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"color:{C['text2']};background:{C['bg3']};"
            "font-family:Consolas,monospace;font-size:10px;"
            "padding:4px;border-radius:3px;"
        )
        self.setText("— PnL 데이터 없음 —")
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    def refresh(self, rolling: Dict[str, Any]) -> None:
        """
        rolling: get_rolling_metrics() 반환값
          {daily_pnl_list, cum_pnl, sharpe, mdd_pct, win_rate, profit_factor, days, ...}
        """
        pnls = rolling.get("daily_pnl_list", [])
        if not pnls:
            self.setText("— PnL 데이터 없음 —")
            self.setStyleSheet(
                f"color:{C['text2']};background:{C['bg3']};"
                "font-family:Consolas,monospace;font-size:10px;"
                "padding:4px;border-radius:3px;"
            )
            return

        recent = pnls[-self._WIDTH:]
        n = len(recent)
        cum_pnl = sum(recent)
        max_abs = max(abs(p) for p in recent) if recent else 1.0

        lines = []
        # 헤더
        n_days = rolling.get("days", n)
        lines.append("  실전 PnL (%dd)   누적: %+.0f원" % (n_days, cum_pnl))

        # 막대 차트 (양수=녹색 블록, 음수=적색 블록)
        for row in range(self._HEIGHT, 0, -1):
            threshold = max_abs * row / self._HEIGHT
            bar = "  │"
            for p in recent:
                if abs(p) >= threshold:
                    bar += "█" if p > 0 else "▄"
                else:
                    bar += " "
            lines.append(bar)
        lines.append("  └" + "─" * n)

        # 일별 방향 라인 (▲=수익일, ▼=손실일)
        dir_line = "   "
        for p in recent:
            dir_line += "▲" if p > 0 else ("▼" if p < 0 else "─")
        lines.append(dir_line)

        # 지표 요약
        parts = []
        sh = rolling.get("sharpe")
        md = rolling.get("mdd_pct")
        wr = rolling.get("win_rate")
        pf = rolling.get("profit_factor")
        if sh is not None:
            parts.append("Sh:%.2f" % sh)
        if md is not None:
            parts.append("MDD:%.1f%%" % (md * 100))
        if wr is not None:
            parts.append("WR:%.0f%%" % (wr * 100))
        if pf is not None:
            parts.append("PF:%.2f" % (pf if pf < 100 else 99.9))
        if parts:
            lines.append("  " + "  ".join(parts))

        # 색상: 누적 PnL 방향으로 결정
        color = C["green"] if cum_pnl >= 0 else C["red"]
        self.setStyleSheet(
            f"color:{color};background:{C['bg3']};"
            "font-family:Consolas,monospace;font-size:10px;"
            "padding:4px;border-radius:3px;"
        )
        self.setText("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────
# 버전별 성과 추이 차트 (§10-8) — ASCII 텍스트 멀티라인 테이블
# ─────────────────────────────────────────────────────────────────────────
class _VersionTrendChart(QLabel):
    """
    전략 버전별 누적 Sharpe·MDD·승률·PF 추이를 ASCII 텍스트로 표시.
    최대 8개 버전을 가로로 나열하고, 지표별로 행을 구성한다.
    """

    _MAX_VER = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setStyleSheet(
            f"color:{C['cyan']};background:{C['bg3']};"
            "font-family:Consolas,monospace;font-size:10px;"
            "padding:6px;border-radius:3px;"
        )
        self.setText("— 버전 이력 없음 —")

    def refresh(self, all_versions: List[Dict[str, Any]]) -> None:
        if not all_versions:
            self.setText("— 버전 이력 없음 —")
            return

        versions = all_versions[-self._MAX_VER:]
        col_w = 9  # 각 버전 컬럼 폭

        def _extract_m(v: dict) -> dict:
            live = (v.get("live_snapshot") or {})
            if live.get("sharpe") is not None:
                return live
            return (v.get("stages") or {}).get("WFA", {})

        # 헤더 행 — 버전명
        hdr = "%-8s" % "버전"
        for v in versions:
            vn = v.get("version", "—")[-col_w:]
            hdr += ("%-*s" % (col_w, vn))

        rows = [hdr, "─" * (8 + col_w * len(versions))]

        metrics_def = [
            ("Sharpe", "sharpe",        lambda x: "%.2f" % x),
            ("MDD %",  "mdd_pct",       lambda x: "%.1f%%" % (abs(x) * 100)),
            ("승률 %", "win_rate",      lambda x: "%.1f%%" % (x * 100)),
            ("PF",     "profit_factor", lambda x: "%.2f" % x),
        ]

        prev_vals: Dict[str, Optional[float]] = {k: None for _, k, _ in metrics_def}

        for label, key, fmt in metrics_def:
            row = "%-8s" % label
            for v in versions:
                m   = _extract_m(v)
                val = m.get(key)
                if val is None:
                    cell = "—"
                else:
                    cell = fmt(val)
                    prev = prev_vals.get(key)
                    if prev is not None:
                        if key == "mdd_pct":
                            cell += "↓" if abs(val) < abs(prev) else ("↑" if abs(val) > abs(prev) else "=")
                        else:
                            cell += "↑" if val > prev else ("↓" if val < prev else "=")
                    prev_vals[key] = val
                row += ("%-*s" % (col_w, cell[:col_w]))
            rows.append(row)

        # verdict 행
        row = "%-8s" % "판정"
        for v in versions:
            vd = v.get("verdict", "—")
            vd_short = {"OUTPERFORM": "상회▲", "NORMAL": "부합●", "UNDERPERFORM": "하회▼",
                        "INSUFFICIENT": "부족⏳"}.get(vd, vd[:5])
            row += ("%-*s" % (col_w, vd_short))
        rows.append(row)

        self.setText("\n".join(rows))


# ─────────────────────────────────────────────────────────────────────────
# 파라미터 변경 영향 Heatmap (§10-9 / §17)
# ─────────────────────────────────────────────────────────────────────────
class _ParamHeatmap(QWidget):
    """
    버전×핵심파라미터 변경 히트맵.
    셀: 초록=상향 조정, 빨강=하향, 회색=변경없음
    우측: Sharpe Δ, MDD Δ, PF Δ
    """

    _KEY_PARAMS = [
        ("conf\nneutral", "entry_conf_neutral"),
        ("conf\nrisk_on",  "entry_conf_risk_on"),
        ("tp2\nmult",      "atr_tp2_mult"),
        ("stop\nmult",     "atr_stop_mult"),
        ("hurst\ntrend",   "hurst_trend_threshold"),
        ("kelly\nhalf",    "kelly_half_factor"),
    ]
    _DELTA_COLS = [("Sh Δ", "sharpe"), ("MDD Δ", "mdd_pct"), ("PF Δ", "profit_factor")]

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        n_cols = len(self._KEY_PARAMS) + len(self._DELTA_COLS) + 1   # +1 for version col
        self._tbl = QTableWidget(0, n_cols)
        headers = ["버전"] + [kp[0] for kp in self._KEY_PARAMS] + [dc[0] for dc in self._DELTA_COLS]
        self._tbl.setHorizontalHeaderLabels(headers)
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl.setSelectionMode(QTableWidget.NoSelection)
        self._tbl.setStyleSheet(
            f"QTableWidget{{background:{C['bg2']};color:{C['text']};"
            f"gridline-color:{C['border']};border:none;font-size:9px;"
            "font-family:Consolas,D2Coding,monospace;}"
            f"QHeaderView::section{{background:{C['bg3']};color:{C['text2']};"
            "font-size:9px;padding:2px;border:none;}}"
        )
        self._tbl.setFixedHeight(_S(160))
        lay.addWidget(self._tbl)

    def refresh(self, all_versions: List[Dict[str, Any]]) -> None:
        if not all_versions:
            self._tbl.setRowCount(0)
            return

        def _extract_m(v: dict) -> dict:
            live = (v.get("live_snapshot") or {})
            if live.get("sharpe") is not None:
                return live
            return (v.get("stages") or {}).get("WFA", {})

        # 버전별 changed_params 를 {param_name: (from, to)} 로 인덱싱
        rows_data = []
        for idx, ver_info in enumerate(all_versions):
            ver = ver_info.get("version", "—")
            chg_list = ver_info.get("changed_params", [])
            chg_map  = {c["param"]: (c.get("from"), c.get("to")) for c in chg_list}

            curr_m = _extract_m(ver_info)
            prev_m = _extract_m(all_versions[idx - 1]) if idx > 0 else {}

            deltas: Dict[str, Optional[float]] = {}
            for _, metric_key in self._DELTA_COLS:
                cv = curr_m.get(metric_key)
                pv = prev_m.get(metric_key)
                if cv is not None and pv is not None:
                    if metric_key == "mdd_pct":
                        deltas[metric_key] = (abs(cv) - abs(pv)) * 100   # % points
                    elif metric_key == "win_rate":
                        deltas[metric_key] = (cv - pv) * 100
                    else:
                        deltas[metric_key] = cv - pv
                else:
                    deltas[metric_key] = None

            rows_data.append({"ver": ver, "chg_map": chg_map, "deltas": deltas})

        self._tbl.setRowCount(len(rows_data))

        for r, row in enumerate(rows_data):
            # 버전 셀
            itm = QTableWidgetItem(row["ver"])
            itm.setTextAlignment(Qt.AlignCenter)
            itm.setForeground(QColor(C["blue"]))
            self._tbl.setItem(r, 0, itm)

            # 파라미터 셀
            for c, (_, param_key) in enumerate(self._KEY_PARAMS, 1):
                change = row["chg_map"].get(param_key)
                if change is None:
                    txt    = ""
                    bg_col = C["bg2"]
                    fg_col = C["text2"]
                else:
                    fv, tv = change
                    try:
                        diff = float(tv) - float(fv)
                        txt    = "%+.4g" % diff
                        bg_col = "#1A3A1A" if diff > 0 else "#3A1A1A"
                        fg_col = C["lime"] if diff > 0 else C["red"]
                    except (TypeError, ValueError):
                        txt    = "chg"
                        bg_col = "#2A2A1A"
                        fg_col = C["yellow"]

                itm = QTableWidgetItem(txt)
                itm.setTextAlignment(Qt.AlignCenter)
                itm.setForeground(QColor(fg_col))
                itm.setBackground(QColor(bg_col))
                self._tbl.setItem(r, c, itm)

            # 델타 셀
            offset = len(self._KEY_PARAMS) + 1
            for c2, (_, metric_key) in enumerate(self._DELTA_COLS):
                dv = row["deltas"].get(metric_key)
                if dv is None:
                    txt    = "—"
                    fg_col = C["text2"]
                else:
                    txt    = "%+.2f" % dv
                    # MDD: 음수가 good (낮아짐 = 개선)
                    if metric_key == "mdd_pct":
                        fg_col = C["green"] if dv < 0 else (C["yellow"] if dv < 2 else C["red"])
                    else:
                        fg_col = C["green"] if dv > 0 else (C["yellow"] if dv > -0.1 else C["red"])

                itm = QTableWidgetItem(txt)
                itm.setTextAlignment(Qt.AlignCenter)
                itm.setForeground(QColor(fg_col))
                self._tbl.setItem(r, offset + c2, itm)


# ─────────────────────────────────────────────────────────────────────────
# 메인 StrategyPanel
# ─────────────────────────────────────────────────────────────────────────
class StrategyPanel(QWidget):
    """
    🧭 전략 운용현황 탭 메인 패널.

    main_dashboard.py 에서:
        self.strategy_panel = StrategyPanel()
        mid_tabs.addTab(self._wrap(self.strategy_panel), "🧭 전략 운용현황")
    """

    REFRESH_INTERVAL_MS = 60_000   # 1분마다 자동 갱신

    def __init__(self, parent=None):
        super().__init__(parent)
        self._registry: Optional[StrategyRegistry] = None
        self._drift_level: int   = 0
        self._psi_val:     float = 0.0
        self._psi_level:   int   = 0

        if _DEPS_OK:
            try:
                self._registry = get_registry()
            except Exception as e:
                logger.warning("[StrategyPanel] Registry 초기화 실패: %s", e)

        self._build_ui()
        self._setup_timer()
        self.refresh()

    # ── UI 구성 ──────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(_S(8), _S(6), _S(8), _S(8))
        root.setSpacing(_S(6))

        # ① 헤더 카드
        self._header = _HeaderCard()
        root.addWidget(self._header)

        # ② 중단: 좌 [단계 성과 + 비교] | 중 [레짐 매트릭스] | 우 [CUSUM]
        mid_row = QHBoxLayout()
        mid_row.setSpacing(_S(6))

        # 좌: 단계 성과 + 이전 비교
        left_col = QVBoxLayout()
        left_col.setSpacing(_S(4))
        self._stage_matrix = _StageMatrix()
        left_col.addWidget(_card("단계별 성과", self._stage_matrix, C["blue"]))

        self._delta_card = _VersionCompareDelta()
        left_col.addWidget(_card("이전 vs 현재 비교", self._delta_card, C["cyan"]))
        left_col.addStretch()

        left_w = QWidget()
        left_w.setLayout(left_col)
        mid_row.addWidget(left_w, 3)

        # 중: 레짐×시간대 매트릭스
        self._regime_matrix = _RegimeTimeMatrix()
        mid_row.addWidget(
            _card("레짐 × 시간대 기대값 매트릭스", self._regime_matrix, C["orange"]),
            3,
        )

        # 우: CUSUM 드리프트 + 실전 PnL 스파크라인 (수직 적층)
        right_col = QVBoxLayout()
        right_col.setSpacing(_S(4))

        self._cusum_chart = _CusumMiniChart()
        right_col.addWidget(
            _card("성과 드리프트 감지 (CUSUM)", self._cusum_chart, C["purple"])
        )

        self._pnl_sparkline = _LivePnlSparkline()
        right_col.addWidget(
            _card("실전 PnL 추이 (롤링 20일)", self._pnl_sparkline, C["green"])
        )

        right_w = QWidget()
        right_w.setLayout(right_col)
        mid_row.addWidget(right_w, 2)

        root.addLayout(mid_row)

        # ③ 버전 추이 차트 + 파라미터 Heatmap (§10-8 / §10-9)
        trend_row = QHBoxLayout()
        trend_row.setSpacing(_S(6))

        self._version_trend = _VersionTrendChart()
        trend_row.addWidget(
            _card("버전별 성과 추이 (§10-8)", self._version_trend, C["cyan"]), 4
        )

        self._param_heatmap = _ParamHeatmap()
        trend_row.addWidget(
            _card("파라미터 변경 Heatmap (§10-9)", self._param_heatmap, C["yellow"]), 5
        )
        root.addLayout(trend_row)

        # ④ 파라미터 변경 이력
        self._param_table = _ParamChangeTable()
        root.addWidget(_card("파라미터 변경 이력", self._param_table, C["yellow"]))

        # ⑤ 전략 평가 로그
        self._log_panel = _StrategyLog()
        root.addWidget(_card("전략 평가 로그", self._log_panel, C["text2"]))

        # 하단: 최근 갱신 시각
        bot = QHBoxLayout()
        self._lbl_updated = _lbl("갱신: —", C["text2"], 10)
        self._lbl_status  = _lbl("● DB 연결됨" if self._registry else "⚠ DB 미연결",
                                  C["green"] if self._registry else C["red"], 10)
        bot.addWidget(self._lbl_updated)
        bot.addStretch()
        bot.addWidget(self._lbl_status)
        root.addLayout(bot)

    # ── 타이머 ────────────────────────────────────────────────────────────
    def _setup_timer(self) -> None:
        self._timer = QTimer(self)
        self._timer.setInterval(self.REFRESH_INTERVAL_MS)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()

    # ── 갱신 진입점 ──────────────────────────────────────────────────────
    def refresh(self) -> None:
        """레지스트리에서 최신 데이터 읽어 전체 UI 갱신."""
        if not self._registry:
            return

        try:
            all_versions  = self._registry.get_all_versions()
            curr_info     = self._registry.get_current_version()
            prev_info     = None
            if curr_info and curr_info.get("previous_version"):
                prev_info = self._registry.get_version(curr_info["previous_version"])

            # 드리프트 수준
            if _DEPS_OK:
                try:
                    det = get_drift_detector()
                    _lvs = det.get_levels() if hasattr(det, "get_levels") else {}
                    self._drift_level = max(_lvs.values()) if _lvs else 0
                    cusum_hist = []
                    for sub_det in det.detectors.values():
                        if hasattr(sub_det, "get_history"):
                            cusum_hist = sub_det.get_history()
                            break
                except Exception:
                    self._drift_level = 0
                    cusum_hist = []
            else:
                cusum_hist = []

            # 각 하위 컴포넌트 갱신
            self._header.refresh(
                curr_info, self._drift_level,
                psi_val=self._psi_val, psi_level=self._psi_level,
            )

            if curr_info:
                self._stage_matrix.refresh(
                    curr_info.get("stages", {}),
                    curr_info.get("live_snapshot"),
                )
                self._delta_card.refresh(prev_info, curr_info)

                regime_data = self._registry.get_regime_matrix(
                    curr_info["version"]
                )
                self._regime_matrix.refresh(regime_data)

            self._cusum_chart.refresh(cusum_hist)

            # 롤링 PnL 스파크라인 갱신
            rolling_data = {}
            if curr_info:
                live_snap = curr_info.get("live_snapshot") or {}
                if live_snap.get("daily_pnl_list"):
                    rolling_data = live_snap
                elif self._registry:
                    try:
                        rolling_data = self._registry.get_rolling_metrics(
                            curr_info["version"]
                        )
                    except Exception:
                        pass
            self._pnl_sparkline.refresh(rolling_data)

            self._version_trend.refresh(all_versions)
            self._param_heatmap.refresh(all_versions)
            self._param_table.refresh(all_versions)

            # 이벤트 로그 (strategy_events 우선, 없으면 버전 폴백)
            _ev_log = None
            if self._registry:
                try:
                    _ev_log = self._registry.get_event_log(limit=40)
                except Exception:
                    pass
            self._log_panel.refresh(all_versions, event_log=_ev_log)

            self._lbl_updated.setText(
                "갱신: %s" % datetime.now().strftime("%H:%M:%S")
            )

        except Exception as e:
            logger.warning("[StrategyPanel] 갱신 오류: %s", e)

    def set_drift_level(self, level: int) -> None:
        """외부(main.py)에서 드리프트 수준 직접 주입."""
        self._drift_level = level
        curr_info = None
        if self._registry:
            curr_info = self._registry.get_current_version()
        self._header.refresh(
            curr_info, self._drift_level,
            psi_val=self._psi_val, psi_level=self._psi_level,
        )

    def set_fingerprint_level(self, psi_val: float, psi_level: int) -> None:
        """RegimeFingerprint PSI 수준을 헤더 배지에 실시간 반영."""
        self._psi_val   = psi_val
        self._psi_level = psi_level
        curr_info = None
        if self._registry:
            curr_info = self._registry.get_current_version()
        self._header.refresh(
            curr_info, self._drift_level,
            psi_val=psi_val, psi_level=psi_level,
        )
