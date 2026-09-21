# dashboard/panels/option_flow_delta_chart.py
"""개인 옵션 6종 + 선물 수급 4종 — 시초 대비 증감 시계열 (612차 후속3 / 613차).

「투자자 포지션 매트릭스」를 대체한다. 종전 매트릭스는 `CpSvrNew7221` 의
**금액 축 월물 콜/풋**이었는데, 611차 실측이 개인의 옵션 거래는 **위클리에
집중**돼 있음을 보였다(계약수 기준 월위클리 5,575 vs 먼스리 273, 20.4배).
2026-09-21 장중 실측은 격차가 더 크다 — 월위클리 콜 +9,491 vs 먼스리 콜 −147.

[613차] 여기에 **선물 수급 4종**이 합류했다. 종전에는 이 넷이 패널 맨 위
카드 6칸에 **현재값 하나씩**만 떠 있었다 — 하루의 흐름을 못 봤다. 사용자 지시로
카드를 걷어내고 같은 시계열 형식으로 옮긴다(개인·기관 선물 순매수 2칸은 지시대로
표시에서 제외 — 수집·저장·피처는 그대로다).

원천
----
· 옵션 6종 — `option_flow.db:option_investor_flow` (611차 `CpSvrNew7222` 수집기)
· 선물 4종 — `collection/cybos/futures_flow_series.py` (613차)

값: 둘 다 **일중 누계**이므로 **당일 첫 바를 0 으로 놓은 차분**을 그린다
— 사용자 결정 2026-09-21.

설계 메모
---------
· **소형 다중 차트(small multiples).** 10종을 한 축에 겹치면 위클리가 나머지를
  덮는다(실측 격차 약 790배). 행을 나누면 각자의 추이가 보인다.
· **기본은 행별 독립 스케일이다.** 처음엔 공통 스케일을 기본으로 잡았다가
  구현 중 실측으로 뒤집었다 — 2026-09-21 14:5x 기준 공통 스케일로 그리면
  **6행 중 4행이 0px 로 뭉개진다**(행 최댓값: 월위클콜 9,656 · 월위클풋 12,135 vs
  목위클콜 198 · 목위클풋 1,041 · 먼스리콜 244 · 먼스리풋 248 → 각각 11·15·**0·1·0·0**px).
  "작은 게 작게 보이는 것"과 "아예 안 보이는 것"은 다르고, 이 패널의 요구는
  **각각의 추이를 읽는 것**이다.
  ⚠ 그 대신 **행 사이 높이를 비교하면 안 된다.** 행마다 자기 최댓값(±N)을 축에
  적어 그 사실을 드러내고, 진짜 격차를 보고 싶으면 「공통 스케일」을 켠다.
· 🔴 [613차] **공통 스케일은 그룹 안에서만 적용한다.** 옵션은 계약, 프로그램은
  백만원이라 한 눈금에 올리면 그 자체가 오독이다(계측 4원칙 ①). 라벨마다 단위를
  박고, 눈금은 옵션끼리·선물끼리만 공유한다.
· **결측을 0 으로 잇지 않는다.** 원천에 빠진 분이 있다(오늘 `wk_thu_call` 323바
  vs 나머지 356바). 그 분에는 막대를 찍지 않고, 5분을 넘는 공백은 눈에 띄게 둔다.
· 🔴 [613차] **행 높이는 가용 세로에 맞춰 신축한다.** 10행을 고정 42px 로 잡으면
  패널이 넘쳐 스크롤이 생기고, 아래에서 비운 공간이 차트로 흘러오지 못한다.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QSizePolicy,
                             QVBoxLayout, QWidget)

logger = logging.getLogger("SYSTEM")

_COL = {
    "bg": "#0d1117", "bg2": "#161b22", "bg3": "#1c2128",
    "border": "#30363d", "text": "#e6edf3", "muted": "#8b949e",
    "green": "#3fb950", "red": "#f85149", "blue": "#58a6ff",
    "cyan": "#39d0d8", "orange": "#d29922", "purple": "#bc8cff",
    "yellow": "#e3b341", "zero": "#3d444d",
}

# 세션 창 — 지시받은 표시 범위(사용자 2026-09-21).
# ⚠ 옵션 원천 첫 바는 실측 08:55 다. 08:45~08:54 는 데이터가 없어 빈칸으로 남는다 —
#   그것을 0 으로 채우면 "거래가 없었다"로 읽힌다(계측 4원칙 ②).
_T0_MIN = 8 * 60 + 45      # 08:45
_T1_MIN = 15 * 60 + 35     # 15:35

# 행 순서 — 사용자 지정 순서 그대로. (612차 지시. 순서는 테스트가 고정한다)
_ROWS: Tuple[Tuple[str, str], ...] = (
    ("wk_mon_call", "(월)위클리 콜"),
    ("wk_mon_put",  "(월)위클리 풋"),
    ("wk_thu_call", "(목)위클리 콜"),
    ("wk_thu_put",  "(목)위클리 풋"),
    ("mon_call",    "먼스리 콜"),
    ("mon_put",     "먼스리 풋"),
)
# [613차] 선물 수급 4종 — 사용자 지정 순서 그대로(미결제·외인·차익·비차익).
_FUT_ROWS: Tuple[Tuple[str, str], ...] = (
    ("open_int",    "미결제약정"),
    ("fut_fi",      "외인 선물"),
    ("prog_arb",    "프로그램 차익"),
    ("prog_nonarb", "프로그램 비차익"),
)

# 콜=초록 / 풋=빨강. 부호는 0선 위아래가 이미 말해주므로 색은 **상품 종류**를 쓴다.
# 선물 4종은 걷어낸 카드의 색을 그대로 물려받는다 — 눈이 옮겨가기 쉽게.
_ROW_COLOR = {
    "wk_mon_call": _COL["green"], "wk_thu_call": _COL["green"],
    "mon_call": _COL["green"],
    "wk_mon_put": _COL["red"], "wk_thu_put": _COL["red"], "mon_put": _COL["red"],
    "open_int": _COL["cyan"], "fut_fi": _COL["blue"],
    "prog_arb": _COL["green"], "prog_nonarb": _COL["orange"],
}

# (키, 라벨, 그룹) — paint 가 도는 순서. 그룹은 공통 스케일 묶음이자 구분선 위치다.
_ALL_ROWS: Tuple[Tuple[str, str, str], ...] = tuple(
    [(k, lab, "opt") for k, lab in _ROWS]
    + [(k, lab, "fut") for k, lab in _FUT_ROWS]
)


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
    """10행 소형 다중 차트 본체 (paintEvent 전용)."""

    LABEL_W = 96
    VALUE_W = 96
    # [613차] 고정 ROW_H → 하한. 실제 높이는 가용 세로에서 계산한다.
    MIN_ROW_H = 26
    # 상한이 낮으면 **비운 공간이 차트 아래 빈칸으로 남는다** — 아래에서 걷어낸
    # 세로를 상단 시인성으로 옮기는 것이 613차 지시의 요점이라 넉넉히 준다.
    # (그래도 상한은 둔다 — 대형 모니터에서 한 행이 화면을 다 먹지 않게)
    MAX_ROW_H = 64
    PAD_V = 5
    AXIS_H = 16

    def __init__(self, parent=None):
        super().__init__(parent)
        self._products: Dict[str, Any] = {}
        self._shared = False
        self.setMinimumHeight(self.MIN_ROW_H * len(_ALL_ROWS) + self.AXIS_H
                              + 2 * self.PAD_V)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setToolTip(
            "개인 옵션 순매수 계약수 + 선물 수급 4종 — 당일 첫 바를 0 으로 놓은 증감.\n"
            "원천: 옵션 CpSvrNew7222(611차) · 선물 CpSvrNew7221/CpSvr8111(613차).\n"
            "값은 일중 누계라, 여기 그려지는 것은 곧 '시초 이후 변화'다.\n"
            "오른쪽 굵은 숫자 = 시초 대비 증감 / 그 아래 = 현재 누계(걷어낸 카드의 값).\n"
            "⚠ 단위가 섞여 있다 — 라벨의 (계약)/(백만원)을 볼 것.\n"
            "⚠ 결측 분에는 막대를 찍지 않는다 — 0 으로 잇지 않는다."
        )

    def set_data(self, products: Dict[str, Any], shared: bool) -> None:
        self._products = products or {}
        self._shared = bool(shared)
        self.update()

    def row_height(self) -> int:
        """가용 세로에서 행 높이를 정한다 — 아래에서 비운 공간이 여기로 흘러온다."""
        avail = self.height() - self.AXIS_H - 2 * self.PAD_V
        h = int(avail // max(1, len(_ALL_ROWS)))
        return max(self.MIN_ROW_H, min(self.MAX_ROW_H, h))

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

    def _group_max(self, group: str) -> int:
        """공통 스케일용 — **그룹 안에서만** 최댓값을 공유한다.

        옵션(계약)과 프로그램(백만원)을 한 눈금에 올리면 그 자체가 오독이다.
        """
        m = 1
        for key, _lab, grp in _ALL_ROWS:
            if grp != group:
                continue
            d = self._products.get(key)
            if not d:
                continue
            for _t, v in d.get("series", ()):
                m = max(m, abs(int(v)))
        return m

    def _paint(self) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor(_COL["bg2"]))

        x0 = self.LABEL_W
        x1 = max(x0 + 40, w - self.VALUE_W)
        span = max(1, _T1_MIN - _T0_MIN)
        row_h = self.row_height()
        f_lab = QFont(); f_lab.setPointSize(8)
        f_val = QFont(); f_val.setPointSize(8); f_val.setBold(True)
        f_sub = QFont(); f_sub.setPointSize(7)

        shared_max = {"opt": self._group_max("opt"), "fut": self._group_max("fut")}
        prev_group = None

        for i, (key, label, group) in enumerate(_ALL_ROWS):
            top = self.PAD_V + i * row_h
            mid = top + row_h // 2
            d = self._products.get(key)

            # 그룹 경계 — 단위가 바뀌는 자리다. 선 하나로 그것을 알린다.
            if prev_group is not None and group != prev_group:
                p.setPen(QPen(QColor(_COL["border"]), 1))
                p.drawLine(2, top - 1, w - 2, top - 1)
            prev_group = group

            # 라벨 + 단위 (계측 4원칙 ① — 단위는 섹션이 아니라 행마다 박는다)
            unit = (d or {}).get("unit")
            p.setFont(f_lab)
            p.setPen(QPen(QColor(_COL["muted"])))
            p.drawText(QRectF(2, top, self.LABEL_W - 6, row_h * 0.62),
                       Qt.AlignBottom | Qt.AlignRight, label)
            if unit:
                p.setFont(f_sub)
                p.drawText(QRectF(2, top + row_h * 0.58, self.LABEL_W - 6,
                                  row_h * 0.42),
                           Qt.AlignTop | Qt.AlignRight, "(%s)" % unit)

            # 0선
            p.setPen(QPen(QColor(_COL["zero"]), 1))
            p.drawLine(x0, mid, x1, mid)

            if not d or not d.get("series"):
                # 미수집 — 0 으로 그리지 않고 그렇게 적는다(계측 4원칙 ②).
                p.setFont(f_lab)
                p.setPen(QPen(QColor(_COL["muted"])))
                p.drawText(QRectF(x0, top, x1 - x0, row_h),
                           Qt.AlignCenter, "미수집")
                continue

            series: List[Tuple[str, int]] = d["series"]
            scale_max = (shared_max.get(group, 1) if self._shared
                         else max(1, max(abs(int(v)) for _t, v in series)))
            half = row_h // 2 - 3

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

            # 오른쪽 — 위: 시초 대비 증감(굵게) / 아래: 현재 누계 + 이 행의 축.
            # 🔴 누계를 함께 싣는 이유: 걷어낸 6카드가 보여주던 값이 그것이다.
            #    증감만 남기면 미결제 62,767 같은 절대 수준이 화면에서 사라진다.
            cur = int(d.get("delta", 0))
            p.setFont(f_val)
            p.setPen(QPen(QColor(col if cur else _COL["muted"])))
            p.drawText(QRectF(x1 + 2, top, self.VALUE_W - 4, row_h * 0.58),
                       Qt.AlignBottom | Qt.AlignRight, _fmt_qty(cur))
            p.setFont(f_sub)
            p.setPen(QPen(QColor(_COL["muted"])))
            sub = "누계 %s" % format(int(d.get("value", 0)), ",")
            if not self._shared:
                # 행마다 눈금이 다르다는 사실을 화면에 박는다.
                # (공통 스케일일 때는 그룹 안이 같으므로 표기하지 않는다)
                sub += " · ±%s" % format(int(scale_max), ",")
            p.drawText(QRectF(x1 + 2, top + row_h * 0.56, self.VALUE_W - 4,
                              row_h * 0.44),
                       Qt.AlignTop | Qt.AlignRight, sub)

        # x축 눈금 (09 ~ 15시)
        p.setFont(f_lab)
        ybase = self.PAD_V + len(_ALL_ROWS) * row_h
        for hh in range(9, 16):
            tm = hh * 60
            if tm < _T0_MIN or tm > _T1_MIN:
                continue
            x = x0 + int((tm - _T0_MIN) * (x1 - x0) / float(span))
            p.setPen(QPen(QColor(_COL["border"]), 1))
            p.drawLine(x, self.PAD_V, x, ybase)
            p.setPen(QPen(QColor(_COL["muted"])))
            p.drawText(QRectF(x - 12, ybase, 24, self.AXIS_H - 2),
                       Qt.AlignCenter, "%d" % hh)
        p.end()


class OptionFlowDeltaChart(QWidget):
    """헤더(기준·갱신·스케일 토글) + 10행 차트.

    갱신 경로가 **둘**이다 — 옵션은 `update_flow()`, 선물은 `update_futures_flow()`.
    각 payload 를 따로 보관하고 그릴 때 합친다. 🔴 한쪽 조회가 실패했을 때
    다른 쪽 행까지 지워지면 안 된다(612차 후속5 와 같은 계열의 사고 방지).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        self._lbl_title = QLabel("옵션·선물 수급 — 시초 대비 증감")
        self._lbl_title.setStyleSheet(
            "color:%s;font-size:11px;font-weight:bold;" % _COL["blue"])
        hdr.addWidget(self._lbl_title)
        hdr.addStretch()
        # [613차] 수급 신선도 칩 — 걷어낸 「선물 투자자 수급」 헤더에 있던 것을
        # 여기로 옮겼다. 그 섹션의 카드가 전부 이 차트로 들어왔기 때문이다.
        self._lbl_age = QLabel("수급 ——")
        self._lbl_age.setStyleSheet("color:%s;font-size:9px;" % _COL["muted"])
        self._lbl_age.setToolTip(
            "마지막 수급 TR 수신 이후 경과.\n"
            "180초를 넘으면 주황 — 화면 숫자가 그만큼 낡았다는 뜻이다.\n"
            "(원천 실패 시 직전값이 유지되므로 값만 봐서는 구분되지 않는다)"
        )
        hdr.addWidget(self._lbl_age)
        self._lbl_meta = QLabel("——")
        self._lbl_meta.setStyleSheet("color:%s;font-size:9px;" % _COL["muted"])
        hdr.addWidget(self._lbl_meta)
        self._chk_shared = QCheckBox("공통 스케일")
        self._chk_shared.setChecked(False)
        self._chk_shared.setToolTip(
            "꺼짐(기본): 행마다 자기 최댓값으로 — 각각의 추이를 읽는다.\n"
            "  ⚠ 행 사이 높이를 비교하면 안 된다. 오른쪽 ±N 이 그 행의 축이다.\n"
            "켜짐: 같은 눈금으로 — 위클리와 먼스리의 실제 격차가 보인다.\n"
            "  ⚠ 이때 작은 행은 0px 로 뭉개진다(실측 먼스리 244 vs 월위클리 12,135).\n"
            "⚠ 눈금 공유는 **그룹 안에서만** 한다 — 옵션(계약)과 프로그램(백만원)을\n"
            "  한 눈금에 올리는 것은 그 자체가 오독이다."
        )
        self._chk_shared.setStyleSheet(
            "color:%s;font-size:9px;" % _COL["muted"])
        self._chk_shared.toggled.connect(self._on_toggle)
        hdr.addWidget(self._chk_shared)
        lay.addLayout(hdr)

        self._plot = _Plot()
        lay.addWidget(self._plot, 1)

        self._payload: Dict[str, Any] = {}          # 옵션 6종
        self._fut_payload: Dict[str, Any] = {}      # 선물 4종

    # ── 내부 ──────────────────────────────────────────────────────────────
    def _merged(self) -> Dict[str, Any]:
        prods = dict(self._payload.get("products") or {})
        prods.update(self._fut_payload.get("products") or {})
        return prods

    def _redraw(self) -> None:
        self._plot.set_data(self._merged(), self._chk_shared.isChecked())

    def _on_toggle(self, _checked: bool) -> None:
        self._redraw()

    def _render_meta(self) -> None:
        opt = self._payload.get("products") or {}
        fut = self._fut_payload.get("products") or {}
        if not opt and not fut:
            # 09:02 이전이거나 수집 실패. "0" 이 아니라 "아직 없음"이라고 적는다.
            self._lbl_meta.setText("미수집 — 09:02 첫 수집 예정")
            return
        parts = []
        if opt:
            base_t = min((d.get("baseline_time") or "—") for d in opt.values())
            parts.append("옵션 %d종 기준 %s" % (len(opt), base_t))
        if fut:
            parts.append("선물 %d종" % len(fut))
        last = max([t for t in (self._payload.get("last_time"),
                                self._fut_payload.get("last_time")) if t] or ["—"])
        parts.append("갱신 %s" % last)
        self._lbl_meta.setText(" · ".join(parts))

    # ── 외부 주입 ─────────────────────────────────────────────────────────
    def update_flow(self, payload: Dict[str, Any]) -> None:
        """`WeeklyOptionFlow.get_individual_session_delta()` 결과를 그린다."""
        self._payload = payload or {}
        self._redraw()
        self._render_meta()

    def update_futures_flow(self, payload: Dict[str, Any]) -> None:
        """[613차] `futures_flow_series.get_futures_session_delta()` 결과를 그린다."""
        self._fut_payload = payload or {}
        self._redraw()
        self._render_meta()

    def set_age_text(self, text: str, level: str = "ok") -> None:
        """[613차] 수급 신선도 칩 — 패널이 계산한 문자열·등급을 그대로 받는다.

        level: ok | warn(180초 초과) | stop(600초 초과).
        🔴 3단계를 2단계로 줄이지 말 것 — 「그냥 좀 낡음」과 「멈춤」을 색으로
           가르는 것이 612차 후속5 의 요점이었다.
        """
        col = {"stop": _COL["red"], "warn": _COL["orange"]}.get(level, _COL["muted"])
        self._lbl_age.setText(text)
        self._lbl_age.setStyleSheet(
            "color:%s;font-size:9px;%s"
            % (col, "font-weight:bold;" if level != "ok" else ""))
