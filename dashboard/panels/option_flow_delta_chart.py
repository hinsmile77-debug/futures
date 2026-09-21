# dashboard/panels/option_flow_delta_chart.py
"""개인 옵션 6종 — 시초 대비 계약수 증감 시계열 (612차 후속3).

「투자자 포지션 매트릭스」를 대체한다. 종전 매트릭스는 `CpSvrNew7221` 의
**금액 축 월물 콜/풋**이었는데, 611차 실측이 개인의 옵션 거래는 **위클리에
집중**돼 있음을 보였다(계약수 기준 월위클리 5,575 vs 먼스리 273, 20.4배).
2026-09-21 장중 실측은 격차가 더 크다 — 월위클리 콜 +9,491 vs 먼스리 콜 −147.

원천: `option_flow.db:option_investor_flow` (611차 `CpSvrNew7222` 수집기).
값: `net_qty` = **일중 누적 순매수 계약**. 첫 바가 0 이 아니므로
(프리장 단일가가 실려 있다) **당일 첫 바를 0 으로 놓은 차분**을 그린다
— 사용자 결정 2026-09-21.

설계 메모
---------
· **소형 다중 차트(small multiples).** 6종을 한 축에 겹치면 위클리가 나머지를
  덮는다(실측 격차 약 790배). 행을 나누면 각자의 추이가 보인다.
· **기본은 행별 독립 스케일이다.** 처음엔 공통 스케일을 기본으로 잡았다가
  구현 중 실측으로 뒤집었다 — 2026-09-21 14:5x 기준 공통 스케일로 그리면
  **6행 중 4행이 0px 로 뭉개진다**(행 최댓값: 월위클콜 9,656 · 월위클풋 12,135 vs
  목위클콜 198 · 목위클풋 1,041 · 먼스리콜 244 · 먼스리풋 248 → 각각 11·15·**0·1·0·0**px).
  "작은 게 작게 보이는 것"과 "아예 안 보이는 것"은 다르고, 이 패널의 요구는
  **6종 각각의 추이를 읽는 것**이다.
  ⚠ 그 대신 **행 사이 높이를 비교하면 안 된다.** 행마다 자기 최댓값(±N)을 축에
  적어 그 사실을 드러내고, 진짜 격차를 보고 싶으면 「공통 스케일」을 켠다.
· **결측을 0 으로 잇지 않는다.** 원천에 빠진 분이 있다(오늘 `wk_thu_call` 323바
  vs 나머지 356바). 그 분에는 막대를 찍지 않고, 5분을 넘는 공백은 눈에 띄게 둔다.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

logger = logging.getLogger("SYSTEM")

_COL = {
    "bg": "#0d1117", "bg2": "#161b22", "bg3": "#1c2128",
    "border": "#30363d", "text": "#e6edf3", "muted": "#8b949e",
    "green": "#3fb950", "red": "#f85149", "blue": "#58a6ff",
    "yellow": "#e3b341", "zero": "#3d444d",
}

# 세션 창 — 지시받은 표시 범위(사용자 2026-09-21).
# ⚠ 원천 첫 바는 실측 08:55 다. 08:45~08:54 는 데이터가 없어 빈칸으로 남는다 —
#   그것을 0 으로 채우면 "거래가 없었다"로 읽힌다(계측 4원칙 ②).
_T0_MIN = 8 * 60 + 45      # 08:45
_T1_MIN = 15 * 60 + 35     # 15:35

# 행 순서 — 사용자 지정 순서 그대로.
_ROWS: Tuple[Tuple[str, str], ...] = (
    ("wk_mon_call", "(월)위클리 콜"),
    ("wk_mon_put",  "(월)위클리 풋"),
    ("wk_thu_call", "(목)위클리 콜"),
    ("wk_thu_put",  "(목)위클리 풋"),
    ("mon_call",    "먼스리 콜"),
    ("mon_put",     "먼스리 풋"),
)
# 콜=초록 / 풋=빨강. 부호는 0선 위아래가 이미 말해주므로 색은 **상품 종류**를 쓴다.
_ROW_COLOR = {
    "wk_mon_call": _COL["green"], "wk_thu_call": _COL["green"],
    "mon_call": _COL["green"],
    "wk_mon_put": _COL["red"], "wk_thu_put": _COL["red"], "mon_put": _COL["red"],
}


def _hhmm_to_min(t: str) -> Optional[int]:
    try:
        h, m = t.split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return None


def _fmt_qty(v: int) -> str:
    # ⚠ `"%+,d" % v` 는 유효한 printf 포맷이 아니다(ValueError). 구현 중 실제로
    #   이걸 써서 paintEvent 가 1행만 그리고 죽었다 — `format()` 을 쓴다.
    return format(int(v), "+,d") if v else "0"


class _Plot(QWidget):
    """6행 소형 다중 차트 본체 (paintEvent 전용)."""

    LABEL_W = 96
    VALUE_W = 86
    ROW_H = 42
    PAD_V = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._products: Dict[str, Any] = {}
        self._shared = False
        self.setMinimumHeight(self.ROW_H * len(_ROWS) + 22)
        self.setToolTip(
            "개인 투자자의 옵션 순매수 계약수 — 당일 첫 바를 0 으로 놓은 증감.\n"
            "원천 CpSvrNew7222 (611차 수집기), 값은 일중 누적 순매수라\n"
            "여기 그려지는 것은 곧 '시초 이후 포지션 변화'다.\n"
            "⚠ 08:45~08:54 는 원천이 주지 않아 비어 있다(0 이 아니다).\n"
            "⚠ 결측 분에는 막대를 찍지 않는다 — 0 으로 잇지 않는다."
        )

    def set_data(self, products: Dict[str, Any], shared: bool) -> None:
        self._products = products or {}
        self._shared = bool(shared)
        self.update()

    # ── 그리기 ────────────────────────────────────────────────────────────
    # 예외 스로틀 — `getattr(self,"_x",기본값)` 금지(계측 4원칙 ④)라 클래스 속성.
    _paint_err_ts = 0.0

    def paintEvent(self, ev):            # noqa: N802 (Qt)
        try:
            self._paint()
        except Exception as exc:
            # 표시 계층 예외가 대시보드를 죽이지 않게 삼키되, **조용히 삼키지는
            # 않는다.** 구현 중 `_fmt_qty` 의 포맷 오류로 6행 중 1행만 그려졌는데
            # debug 로그라 파일에 안 남아 화면을 눈으로 보고서야 알았다
            # (계측 4원칙 ④ — 폴백이 쓰였으면 그 사실을 남겨라).
            import time as _t
            _now = _t.time()
            if _now - _Plot._paint_err_ts >= 300.0:
                _Plot._paint_err_ts = _now
                logger.warning(
                    "[OptionFlowChart] paint 실패 (5분 스로틀) — 일부 행이 "
                    "안 그려질 수 있다: %s", exc, exc_info=True,
                )

    def _paint(self) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor(_COL["bg2"]))

        x0 = self.LABEL_W
        x1 = max(x0 + 40, w - self.VALUE_W)
        span = max(1, _T1_MIN - _T0_MIN)

        f_lab = QFont(); f_lab.setPointSize(8)
        f_val = QFont(); f_val.setPointSize(8); f_val.setBold(True)

        # 공통 스케일이면 6종 전체의 |증감| 최댓값 하나를 쓴다.
        shared_max = 1
        for key, _ in _ROWS:
            d = self._products.get(key)
            if not d:
                continue
            for _t, v in d.get("series", ()):
                shared_max = max(shared_max, abs(int(v)))

        for i, (key, label) in enumerate(_ROWS):
            top = self.PAD_V + i * self.ROW_H
            mid = top + self.ROW_H // 2
            d = self._products.get(key)

            # 라벨
            p.setFont(f_lab)
            p.setPen(QPen(QColor(_COL["muted"])))
            p.drawText(QRectF(2, top, self.LABEL_W - 6, self.ROW_H),
                       Qt.AlignVCenter | Qt.AlignRight, label)

            # 0선
            p.setPen(QPen(QColor(_COL["zero"]), 1))
            p.drawLine(x0, mid, x1, mid)

            if not d or not d.get("series"):
                # 미수집 — 0 으로 그리지 않고 그렇게 적는다(계측 4원칙 ②).
                p.setFont(f_lab)
                p.setPen(QPen(QColor(_COL["muted"])))
                p.drawText(QRectF(x0, top, x1 - x0, self.ROW_H),
                           Qt.AlignCenter, "미수집")
                continue

            series: List[Tuple[str, int]] = d["series"]
            scale_max = shared_max if self._shared else max(
                1, max(abs(int(v)) for _t, v in series))
            half = self.ROW_H // 2 - 4

            col = QColor(_ROW_COLOR.get(key, _COL["blue"]))
            p.setPen(QPen(col, 1))
            for t, v in series:
                tm = _hhmm_to_min(t)
                if tm is None or tm < _T0_MIN or tm > _T1_MIN:
                    continue
                x = x0 + int((tm - _T0_MIN) * (x1 - x0) / float(span))
                px = int(max(-1.0, min(1.0, v / float(scale_max))) * half)
                # 0 이 아닌 값은 반올림으로 사라지지 않게 최소 1px 을 준다 —
                # "값이 0" 과 "너무 작아 안 보임"은 화면에서 구분돼야 한다.
                if v and px == 0:
                    px = 1 if v > 0 else -1
                if px:
                    p.drawLine(x, mid, x, mid - px)

            # 현재값
            p.setFont(f_val)
            cur = int(d.get("delta", 0))
            p.setPen(QPen(QColor(col if cur else _COL["muted"])))
            p.drawText(QRectF(x1 + 2, top - 6, self.VALUE_W - 4, self.ROW_H),
                       Qt.AlignVCenter | Qt.AlignRight, _fmt_qty(cur))
            # 이 행의 축 — 행마다 눈금이 다르다는 사실을 화면에 박는다.
            # (공통 스케일일 때는 6행이 같으므로 표기하지 않는다)
            if not self._shared:
                f_ax = QFont(); f_ax.setPointSize(7)
                p.setFont(f_ax)
                p.setPen(QPen(QColor(_COL["muted"])))
                p.drawText(QRectF(x1 + 2, top + self.ROW_H // 2, self.VALUE_W - 4,
                                  self.ROW_H // 2),
                           Qt.AlignVCenter | Qt.AlignRight,
                           "축 ±%s" % format(int(scale_max), ","))

        # x축 눈금 (09 ~ 15시)
        p.setFont(f_lab)
        p.setPen(QPen(QColor(_COL["muted"])))
        ybase = self.PAD_V + len(_ROWS) * self.ROW_H
        for hh in range(9, 16):
            tm = hh * 60
            if tm < _T0_MIN or tm > _T1_MIN:
                continue
            x = x0 + int((tm - _T0_MIN) * (x1 - x0) / float(span))
            p.setPen(QPen(QColor(_COL["border"]), 1))
            p.drawLine(x, self.PAD_V, x, ybase)
            p.setPen(QPen(QColor(_COL["muted"])))
            p.drawText(QRectF(x - 12, ybase, 24, 14), Qt.AlignCenter, "%d" % hh)
        p.end()


class OptionFlowDeltaChart(QWidget):
    """헤더(기준·갱신·스케일 토글) + 6행 차트."""

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        self._lbl_title = QLabel("개인 옵션 — 시초 대비 증감 (계약)")
        self._lbl_title.setStyleSheet(
            "color:%s;font-size:11px;font-weight:bold;" % _COL["blue"])
        hdr.addWidget(self._lbl_title)
        hdr.addStretch()
        self._lbl_meta = QLabel("——")
        self._lbl_meta.setStyleSheet("color:%s;font-size:9px;" % _COL["muted"])
        hdr.addWidget(self._lbl_meta)
        self._chk_shared = QCheckBox("공통 스케일")
        self._chk_shared.setChecked(False)
        self._chk_shared.setToolTip(
            "꺼짐(기본): 행마다 자기 최댓값으로 — 6종 각각의 추이를 읽는다.\n"
            "  ⚠ 행 사이 높이를 비교하면 안 된다. 오른쪽 ±N 이 그 행의 축이다.\n"
            "켜짐: 6종을 같은 눈금으로 — 위클리와 먼스리의 실제 격차가 보인다.\n"
            "  ⚠ 이때 작은 행은 0px 로 뭉개진다(실측 먼스리 244 vs 월위클리 12,135)."
        )
        self._chk_shared.setStyleSheet(
            "color:%s;font-size:9px;" % _COL["muted"])
        self._chk_shared.toggled.connect(self._on_toggle)
        hdr.addWidget(self._chk_shared)
        lay.addLayout(hdr)

        self._plot = _Plot()
        lay.addWidget(self._plot)

        self._payload: Dict[str, Any] = {}

    def _on_toggle(self, _checked: bool) -> None:
        self._plot.set_data(self._payload.get("products") or {},
                            self._chk_shared.isChecked())

    def update_flow(self, payload: Dict[str, Any]) -> None:
        """`WeeklyOptionFlow.get_individual_session_delta()` 결과를 그린다."""
        self._payload = payload or {}
        prods = self._payload.get("products") or {}
        self._plot.set_data(prods, self._chk_shared.isChecked())

        if not prods:
            # 09:02 이전이거나 수집 실패. "0" 이 아니라 "아직 없음"이라고 적는다.
            self._lbl_meta.setText("미수집 — 09:02 첫 수집 예정")
            self._lbl_meta.setStyleSheet(
                "color:%s;font-size:9px;" % _COL["muted"])
            return
        base_t = min((d.get("baseline_time") or "—") for d in prods.values())
        last_t = self._payload.get("last_time") or "—"
        self._lbl_meta.setText("기준 %s · 갱신 %s · %d종"
                               % (base_t, last_t, len(prods)))
        self._lbl_meta.setStyleSheet(
            "color:%s;font-size:9px;" % _COL["muted"])
