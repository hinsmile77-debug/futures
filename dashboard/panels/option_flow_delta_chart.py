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

[621차] 봉별 증감 · 콜↔풋 상대강도 · 독립 창 — 사용자 지시 2026-09-23
------------------------------------------------------------------------
사용자가 이 차트에서 가장 먼저 읽는 것은 **「전봉 대비 이번 봉이 늘었나 줄었나」**다.
강세·약세 판단은 하지 않는다 — 증감만 본다(사용자 명시).

· **증감은 색이 아니라 채움으로 표시한다.** 막대 색은 이미 「상품 종류」를 뜻한다
  (콜 초록·풋 빨강). 여기에 증가=초록/감소=빨강을 또 얹으면 풋 행에서 둘이 겹쳐
  읽을 수 없다. 그래서 색은 그대로 두고 **꽉 찬 막대 = 증가 / 속 빈 막대 = 감소 /
  가는 회색 선 = 변화 없음**으로 한다 — 콜이든 풋이든 한 가지 규칙으로 읽힌다.
  분당 픽셀이 `_RECT_MIN_PPM` 보다 좁으면(탭 속 「전체」 보기) 속 빈 막대가 안 보이므로
  **진하게 / 옅게**로 바꾼다.
· **작은 변화는 「변화 없음」이다.** |Δ| ≤ 그 행 하루치 |Δ| 중앙값 × `_DEADBAND_FRAC`.
  없으면 1계약 흔들림마다 채움이 깜박여 오히려 안 읽힌다.
· **전봉 = 직전에 존재하는 봉**이다. 결측 분을 0 으로 채워 비교하지 않는다(계측 4원칙 ②).
· **콜↔풋 상대강도 행**(월·목 위클리 그룹 바로 아래). 막대 = 이번 봉 `Δ콜 − Δ풋`,
  위로 = 콜 쪽(콜색) / 아래로 = 풋 쪽(풋색). 점선 = 누적 `콜 − 풋`(두 누계가 이미
  시초 0 기준이라 곧 그 차이다). 같은 만기·같은 단위(계약)라 정규화하지 않는다.
  ⚠ 「풋이 줄면 콜 쪽 막대」다 — 어느 쪽이 **더 늘었나**만 본다.
  ⚠ 막대와 점선은 **축이 다르다**(오른쪽 `막대 ±A · 선 ±B`).
· **봉폭은 창 크기가 아니라 x 축 설계가 정한다.** 08:45~15:35(410분)를 폭에 다 맞추면
  탭 폭 약 300px 에서 봉 하나가 0.25px 였다. 그래서 「최근 N분」 확대를 두고
  (독립 창 기본 60분 — 621차 후속8), 하루 전체는 위쪽 미니맵이 맡는다. 미니맵 클릭·휠로 과거를 보고,
  「실시간 ▶」로 최신 봉 따라가기에 복귀한다.
· 🔴 **이 위젯은 매매 파이프라인과 같은 메인(Qt) 스레드에서 그린다.**
  ① DB 를 열지 않는다 — 수집 타이머가 조회한 payload 를 탭 차트가 받아 독립 창으로
    **그대로 넘긴다**(`add_mirror`). ② 막대는 데이터가 올 때만 캐시 이미지로 그리고,
    크로스헤어는 그 위에 선만 덧그린다(마우스 이동마다 전 행을 다시 그리지 않는다).
  ③ 그리기가 `_PAINT_SLOW_MS` 를 넘으면 5분 스로틀 WARNING 을 남긴다.
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import QPoint, QRectF, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import (QColor, QFont, QFontMetrics, QKeySequence, QPainter,
                         QPen, QPixmap)
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                             QHBoxLayout, QLabel, QPushButton, QShortcut,
                             QSizePolicy, QVBoxLayout, QWidget)

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

# (키, 라벨, 그룹) — 데이터 행. 그룹은 공통 스케일 묶음이자 구분선 위치다.
_ALL_ROWS: Tuple[Tuple[str, str, str], ...] = tuple(
    [(k, lab, "opt") for k, lab in _ROWS]
    + [(k, lab, "fut") for k, lab in _FUT_ROWS]
)

# [621차] 콜↔풋 상대강도 행 — (행 키, 콜 키, 풋 키, 라벨). 풋 행 바로 아래에 붙는다.
_RS_PAIRS: Tuple[Tuple[str, str, str, str], ...] = (
    ("rs_mon", "wk_mon_call", "wk_mon_put", "콜↔풋"),
    ("rs_thu", "wk_thu_call", "wk_thu_put", "콜↔풋"),
    # [621차 후속3] 먼스리도 같은 형식으로(사용자 지시 2026-09-23). 거래가 적어
    #   「행 없음」 분이 많다 — 두 멤버가 **둘 다 있는 분**만 잰다(`_rs_points`).
    ("rs_mm", "mon_call", "mon_put", "콜↔풋"),
)
_RS_WEIGHT = 0.6     # 상대강도 행 높이 = 데이터 행의 60% — 위 두 행에 딸린 행임을 드러낸다


def _build_layout() -> Tuple[Tuple[str, str, str, str, float], ...]:
    """화면 배치 — (종류 data|rs, 키, 라벨, 그룹, 높이 가중)."""
    after_put = {put: (rk, lab) for rk, _c, put, lab in _RS_PAIRS}
    out = []
    for key, label, group in _ALL_ROWS:
        out.append(("data", key, label, group, 1.0))
        if key in after_put:
            rk, lab = after_put[key]
            out.append(("rs", rk, lab, group, _RS_WEIGHT))
    return tuple(out)


_LAYOUT = _build_layout()
_RS_BY_KEY = {rk: (c, p) for rk, c, p, _lab in _RS_PAIRS}

# 확대 구간 선택지 — None = 세션 전체(08:45~15:35)
_WINDOW_CHOICES: Tuple[Tuple[str, Optional[int]], ...] = (
    ("60분", 60), ("90분", 90), ("120분", 120), ("전체", None))
_DEADBAND_FRAC = 0.2      # |Δ| ≤ 하루치 |Δ| 중앙값 × 이것 → 「변화 없음」
_RECT_MIN_PPM = 4.0       # 분당 픽셀이 이보다 작으면 채움/속빈 → 진하게/옅게
_PAINT_SLOW_MS = 50.0     # 그리기가 이보다 길면 WARNING (메인 스레드 공유)
_GAP_BREAK_MIN = 5        # 누적 점선은 이 분을 넘는 공백을 잇지 않는다
# [621차 후속] 원천 간 동기화 — 한 원천이 이보다 오래 멈추면 기다리지 않는다.
# (옵션 수집기가 죽었다고 선물 4행까지 얼어붙으면 안 된다. 신선도 칩이 멈춤을 알린다)
_SYNC_STALE_MIN = 3

# [621차 후속2] 이 차트의 **유일한** 툴팁 — 좌상단 타이틀에만 건다(사용자 지시 2026-09-23).
# 종전에는 차트 본체·칩·콤보·체크박스마다 툴팁이 떠서 막대를 보려고 마우스를 올릴 때마다
# 설명이 가렸다. 필요한 설명은 전부 여기로 모은다.
_TITLE_TIP = (
    "개인 옵션 순매수 계약수 + 선물 수급 4종 — 당일 첫 바를 0 으로 놓은 증감.\n"
    "원천: 옵션 CpSvrNew7222(611차) · 선물 CpSvrNew7221/CpSvr8111(613차).\n"
    "\n"
    "■ 꽉 찬 막대 = 전봉 대비 증가 / □ 속 빈 막대 = 감소 / │ 회색 선 = 변화 없음\n"
    "  (좁을 때는 진하게 = 증가 / 옅게 = 감소) · 0선 위 점 = 그 분 원천 행 없음\n"
    "콜↔풋 행: 위 = 이번 봉 콜이 더 늘었다 / 아래 = 풋이 더 늘었다 · 점선 = 누적 콜−풋\n"
    "  (막대와 점선은 축이 다르다 — 오른쪽 「막대 ±A · 선 ±B」)\n"
    "오른쪽: ▲n = n봉 연속 증가 · 이번 봉 Δ / 시초 대비 / 누계 · 행 축\n"
    "\n"
    "맨 위 띠 = 하루 전체(08:45~15:35). 주황 틀 = 지금 보는 구간 — 클릭·휠로 이동.\n"
    "그 아래 상태 줄: ● LIVE(08:45~15:35) · 브로커 시각 · 다음 분봉.\n"
    "  다음 분봉 막대는 **이 차트에 새 봉 열이 실제로 열린 순간**부터 차오른다(분 경계 아님).\n"
    "  숫자 = 열린 뒤 경과 초(0부터). 막대가 다 차는 지점 = 최근 실제 열림 간격의 중앙값.\n"
    "  그 간격을 넘기면 색이 바뀌고 「지연 +N초」가 붙는다.\n"
    "  브로커 시각 = PC 시각 + (체결시각 − 수신시각) 최근 60초 최댓값. 체결이 없으면\n"
    "  PC 시각을 쓰고 「PC」라고 표기한다 — 장외·끊김은 브로커 시각을 모른다.\n"
    "그 아래 시각 = 지금 보는 구간의 눈금. 마우스를 올리면 그 분 시각·값이 뜬다.\n"
    "구간: 최근 N분 확대(봉이 넓어진다) / 전체. 「실시간 ▶」 = 최신 봉 따라가기 복귀.\n"
    "공통 스케일: 꺼짐(기본) = 행마다 자기 최댓값 — 행 사이 높이 비교 금지(오른쪽 ±N 이 축).\n"
    "  켜짐 = 그룹(옵션·선물) 안에서만 같은 눈금 — 단위가 다른 그룹끼리는 공유하지 않는다.\n"
    "수급 N초 전: 180초 넘으면 주황, 600초 넘으면 빨강 — 원천 실패 시 직전값이 유지된다.\n"
    "맨 오른쪽 열은 **마감된 분**까지만, 옵션·선물이 **둘 다 도착한 뒤** 함께 열린다.\n"
    "⚠ 단위가 섞여 있다 — 라벨의 (계약)/(백만원)을 볼 것."
)


def _trim_product(d: Dict[str, Any], cutoff: int) -> Optional[Dict[str, Any]]:
    """cutoff 분까지만 남긴 사본. 남는 봉이 없으면 None.

    「시초」·「누계」 배지도 **화면의 마지막 봉**과 맞춰 다시 계산한다 —
    막대는 10:56 까지인데 숫자는 10:57 이면 그것 자체가 또 하나의 어긋남이다.
    """
    ser = [(t, v) for t, v in (d.get("series") or ())
           if (_hhmm_to_min(t) or 0) <= cutoff]
    if not ser:
        return None
    out = dict(d)
    last_t, last_v = ser[-1]
    out["series"] = ser
    out["delta"] = int(last_v)
    out["value"] = int(d.get("baseline", 0)) + int(last_v)
    out["last_time"] = last_t
    out["n"] = len(ser)
    return out


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


def _median(xs: List[float]) -> float:
    s = sorted(xs)
    n = len(s)
    if not n:
        return 0.0
    m = n // 2
    return float(s[m]) if n % 2 else (s[m - 1] + s[m]) / 2.0


def _series_minutes(series) -> List[Tuple[int, int]]:
    """(HH:MM, 값) → (분, 값). 세션 창 밖·파싱 불가 행은 버린다."""
    out = []
    for t, v in series or ():
        tm = _hhmm_to_min(t)
        if tm is None or tm < _T0_MIN or tm > _T1_MIN:
            continue
        out.append((tm, int(v)))
    return out


def _deadband(deltas: List[int]) -> float:
    return _DEADBAND_FRAC * _median([abs(d) for d in deltas])


def _bar_states(pts: List[Tuple[int, int]], thr: float
                ) -> List[Tuple[int, int, Optional[int], int]]:
    """(분, 값, 전봉 대비 Δ, 상태) — 상태 +1 증가 / -1 감소 / 0 변화 없음.

    전봉 = **직전에 존재하는 봉**. 결측 분을 0 으로 채워 비교하지 않는다.
    첫 봉은 Δ 가 없다(None, 상태 0).
    """
    out: List[Tuple[int, int, Optional[int], int]] = []
    prev = None
    for tm, v in pts:
        if prev is None:
            out.append((tm, v, None, 0))
        else:
            d = v - prev
            st = 0 if abs(d) <= thr else (1 if d > 0 else -1)
            out.append((tm, v, d, st))
        prev = v
    return out


def _streak(states: List[int]) -> Tuple[int, int]:
    """마지막 상태와 그 연속 횟수."""
    if not states:
        return 0, 0
    last = states[-1]
    n = 0
    for st in reversed(states):
        if st != last:
            break
        n += 1
    return last, n


def _rs_points(call_pts: List[Tuple[int, int]], put_pts: List[Tuple[int, int]]
               ) -> List[Tuple[int, int, int]]:
    """(분, 이번 봉 Δ콜 − Δ풋, 누적 콜 − 풋) — 두 멤버가 **둘 다 있는 분**만.

    한쪽이 빠진 분은 건너뛰고, 다음 공통 분의 Δ 는 직전 공통 분 대비로 잰다.
    """
    pm = dict(put_pts)
    out: List[Tuple[int, int, int]] = []
    prev = None
    for tm, c in call_pts:
        p = pm.get(tm)
        if p is None:
            continue
        if prev is not None:
            out.append((tm, (c - prev[0]) - (p - prev[1]), c - p))
        prev = (c, p)
    return out


# ── [621차 후속11] Qt 진입점 가드 ─────────────────────────────────────────
# 🔴 PyQt5 는 Qt 가 부른 파이썬 코드(슬롯·이벤트 처리기)에서 새어나온 예외를 `qFatal()` 로
#   처리한다 — **트레이스백도 로그도 없이 엔진 프로세스가 죽는다**(2026-09-22 09:41:56 실사고,
#   617차 래칫의 계기). 래칫은 QTimer 슬롯만 세지만 원리는 모든 진입점에 같다.
#   그래서 이 모듈의 진입점은 본문 전체를 단일 try 로 감싸고 여기로 보낸다.
#   삼키지 않는다 — 태그별 5분에 한 번 WARNING(마우스 이벤트는 초당 수십 번 온다).
#   ⚠ 표시 계층 전용이다. 엔진 슬롯을 이렇게 삼키면 주문 실패가 조용히 사라진다(617차 주석).
_QT_GUARD_TS = {}


def _qt_guard_fail(tag, exc):
    import time as _t
    _now = _t.time()
    if _now - _QT_GUARD_TS.get(tag, 0.0) >= 300.0:
        _QT_GUARD_TS[tag] = _now
        logger.warning("[QtGuard] %s 예외 — 이번 이벤트만 건너뛴다(5분 스로틀): %s",
                       tag, exc, exc_info=True)


def _text_w(fm: QFontMetrics, s: str) -> int:
    try:
        return fm.horizontalAdvance(s)
    except AttributeError:               # Qt < 5.11
        return fm.width(s)


class _Plot(QWidget):
    """13행(데이터 10 + 상대강도 3) 소형 다중 차트 본체."""

    LABEL_W = 96
    VALUE_W = 118
    # [613차] 고정 ROW_H → 하한. 실제 높이는 가용 세로에서 계산한다.
    MIN_ROW_H = 26
    # 🔴 상한이 낮으면 **비운 공간이 차트 아래 빈칸으로 남는다.**
    # 614차 라이브 화면 실측(2026-09-21): 가용 세로가 행당 약 103px 인데 상한
    # 64 가 640px 에서 잘라 **아래 약 390px 이 빈 채로** 남았다. 아래에서 걷어낸
    # 세로를 시인성으로 돌리는 것이 613·615차 지시의 요점이므로 상한을 푼다.
    # (그래도 상한은 둔다 — 대형 모니터에서 한 행이 화면을 다 먹지 않게)
    MAX_ROW_H = 160
    PAD_V = 5
    AXIS_H = 18
    MINIMAP_H = 24
    STATUS_H = 24            # [621차 후속8] 상태 줄(LIVE · 브로커 시각 · 다음 분봉) — 독립 창만

    view_changed = pyqtSignal()          # 따라가기 해제·복귀 → 헤더 버튼 갱신

    def __init__(self, parent=None, minimap: bool = False, status: bool = False):
        super().__init__(parent)
        self._products: Dict[str, Any] = {}
        self._shared = False
        self._window_min: Optional[int] = None     # None = 세션 전체
        self._anchor: Optional[int] = None         # None = 최신 봉 따라가기
        self._minimap = bool(minimap)
        # [621차 후속8] 상태 줄 — 캐시 밖(오버레이)에서 500ms 마다 그린다. 캐시는 무효화하지 않는다.
        self._status = bool(status)
        self._clock_provider = None     # () → 브로커−PC 오프셋(초) | None(모름)
        # [621차 후속9] 차트에 **새 봉 열이 실제로 열린** 시각(monotonic)과 추정 간격(초).
        #   None = 아직 한 번도 안 열렸다(「대기」로 그린다 — 0초가 아니다, 계측 4원칙 ②).
        self._bar_opened_mono = None
        self._bar_interval_s = 60.0
        self._bar_interval_measured = False
        self._blink = False
        self._status_timer = None
        # [621차 후속 / MW0602] 슬롯 가드의 1회 로그 플래그. `getattr` 폴백으로 읽지
        #   않는다 — 명시 초기화가 규약이다(계측 4원칙 ④).
        self._status_tick_failed = False
        if self._status:
            self._status_timer = QTimer(self)
            self._status_timer.setInterval(500)
            self._status_timer.timeout.connect(self._on_status_tick)
        self._cache: Optional[QPixmap] = None
        self._cache_size: Tuple[int, int] = (0, 0)
        self._dirty = True
        self._painted_once = False
        self._hover_min: Optional[int] = None
        # 마지막 그리기의 좌표계 — 크로스헤어·마우스가 캐시를 다시 그리지 않고 쓴다.
        self._geo: Dict[str, Any] = {}
        self._rows_geo: List[Tuple[int, Dict[int, str]]] = []
        self.setMouseTracking(True)
        self.setMinimumHeight(int(self.MIN_ROW_H * self.layout_units())
                              + self.AXIS_H + 2 * self.PAD_V)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # [621차 후속2] 툴팁은 타이틀에만 둔다(사용자 지시) — `_TITLE_TIP` 참조.

    # ── 외부 설정 ─────────────────────────────────────────────────────────
    def set_data(self, products: Dict[str, Any], shared: bool) -> None:
        self._products = products or {}
        self._shared = bool(shared)
        self._invalidate()

    def set_window(self, minutes: Optional[int]) -> None:
        self._window_min = minutes
        self._invalidate()
        self.view_changed.emit()

    def set_anchor(self, end_min: Optional[int]) -> None:
        """확대 구간의 끝 분. 최신 봉 이상이면 따라가기로 돌아간다."""
        latest = self._latest_min()
        if end_min is not None and latest is not None and end_min >= latest:
            end_min = None
        if end_min is not None:
            end_min = max(_T0_MIN, min(_T1_MIN, int(end_min)))
        if end_min != self._anchor:
            self._anchor = end_min
            self._invalidate()
            self.view_changed.emit()

    def is_following(self) -> bool:
        return self._anchor is None

    def is_zoomed(self) -> bool:
        return self._window_min is not None

    def _invalidate(self) -> None:
        self._dirty = True
        self.update()             # 숨은 창이면 Qt 가 그리지 않는다 — 비용 0

    # ── 배치 ──────────────────────────────────────────────────────────────
    @staticmethod
    def layout_units() -> float:
        return sum(w for _k, _key, _l, _g, w in _LAYOUT)

    def _status_h(self) -> int:
        return self.STATUS_H if self._status else 0

    def set_clock_provider(self, provider) -> None:
        self._clock_provider = provider

    def set_bar_clock(self, opened_mono, interval_s: float, measured: bool) -> None:
        self._bar_opened_mono = opened_mono
        self._bar_interval_s = float(interval_s)
        self._bar_interval_measured = bool(measured)

    def _on_status_tick(self) -> None:
        """QTimer 슬롯 — 예외를 밖으로 내지 않는다.

        🔴 PyQt5 는 슬롯에서 새어나온 예외를 `qFatal()` 로 처리한다. 트레이스백도
           로그도 없이 **엔진 프로세스가 죽는다** — 2026-09-22 09:41:56 실사고가
           그것이었고, 617차가 그래서 `scripts/audit_qtimer_slot_guards.py` 와
           래칫 테스트를 만들었다.

        이 슬롯은 500ms 주기라 실패가 나면 로그가 폭주한다 — **첫 1회만** 남긴다.
        """
        try:
            self._blink = not self._blink
            self.update()       # 캐시 복사 + 오버레이만 — `_invalidate` 가 아니다
        except Exception:       # noqa: BLE001 — 최후 방어선
            if not self._status_tick_failed:
                self._status_tick_failed = True
                logger.exception(
                    "[OptionFlowWindow] _on_status_tick 예외 — 이후 로그 억제")

    def showEvent(self, ev):             # noqa: N802 (Qt) — 보일 때만 시계를 돌린다
        try:
            if self._status_timer is not None:
                self._status_timer.start()
            super().showEvent(ev)
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('_Plot.showEvent', _qe)

    def hideEvent(self, ev):             # noqa: N802 (Qt)
        try:
            if self._status_timer is not None:
                self._status_timer.stop()
            super().hideEvent(ev)
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('_Plot.hideEvent', _qe)

    def broker_now(self):
        """(지금 시각, 브로커 여부, 오프셋초). 공급자가 None 을 주면 PC 시각이고 False 다."""
        import datetime as _dtm
        off = None
        try:
            off = self._clock_provider() if self._clock_provider is not None else None
        except Exception:
            off = None
        now = _dtm.datetime.now()
        if off is None:
            return now, False, None
        return now + _dtm.timedelta(seconds=float(off)), True, float(off)

    def _minimap_h(self) -> int:
        return self.MINIMAP_H if (self._minimap and self._window_min) else 0

    def row_height(self) -> int:
        """가용 세로에서 행 높이를 정한다 — 아래에서 비운 공간이 여기로 흘러온다."""
        avail = (self.height() - self.AXIS_H - 2 * self.PAD_V - self._minimap_h()
                 - self._status_h())
        h = int(avail // max(1.0, self.layout_units()))
        return max(self.MIN_ROW_H, min(self.MAX_ROW_H, h))

    def row_spans(self, row_h: int) -> List[Tuple[int, int]]:
        """행별 (위 y, 높이)."""
        # [621차 후속2] 시간 눈금 띠(AXIS_H)가 행 **위**에 있다 — 아래 눈금은 없앴다.
        top = self.PAD_V + self._minimap_h() + self._status_h() + self.AXIS_H
        out = []
        for _k, _key, _l, _g, w in _LAYOUT:
            hh = max(12, int(round(row_h * w)))
            out.append((top, hh))
            top += hh
        return out

    def _latest_min(self) -> Optional[int]:
        m = None
        for d in self._products.values():
            ser = (d or {}).get("series") or ()
            if ser:
                tm = _hhmm_to_min(ser[-1][0])
                if tm is not None:
                    m = tm if m is None else max(m, tm)
        return m

    def view_range(self) -> Tuple[int, int]:
        """보이는 구간 [v0, v1) 분."""
        if not self._window_min:
            return _T0_MIN, _T1_MIN + 1
        n = int(self._window_min)
        end = self._anchor if self._anchor is not None else self._latest_min()
        if end is None:
            end = _T0_MIN + n - 1
        v1 = min(end + 1, _T1_MIN + 1)
        v0 = max(_T0_MIN, v1 - n)
        return v0, v0 + n

    # ── 그리기 ────────────────────────────────────────────────────────────
    # 예외 스로틀 — `getattr(self,"_x",기본값)` 금지(계측 4원칙 ④)라 클래스 속성.
    _paint_err_ts = 0.0
    _paint_slow_ts = 0.0

    def paintEvent(self, ev):            # noqa: N802 (Qt)
        try:
            size = (self.width(), self.height())
            if self._dirty or self._cache is None or self._cache_size != size:
                self._paint()
            p = QPainter(self)
            try:
                if self._cache is not None:
                    p.drawPixmap(0, 0, self._cache)
                self._draw_status_strip(p)
                self._draw_overlay(p)
            finally:
                p.end()
        except Exception as exc:
            # 표시 계층 예외가 대시보드를 죽이지 않게 삼키되, **조용히 삼키지는
            # 않는다.** 구현 중 `_fmt_qty` 의 포맷 오류로 6행 중 1행만 그려졌는데
            # debug 로그라 파일에 안 남아 화면을 눈으로 보고서야 알았다
            # (계측 4원칙 ④ — 폴백이 쓰였으면 그 사실을 남겨라).
            _now = time.time()
            if _now - _Plot._paint_err_ts >= 300.0:
                _Plot._paint_err_ts = _now
                logger.warning(
                    "[OptionFlowChart] paint 실패 (5분 스로틀) — 일부 행이 "
                    "안 그려질 수 있다: %s", exc, exc_info=True,
                )

    def _group_max(self, group: str, v0: int = _T0_MIN, v1: int = _T1_MIN + 1) -> int:
        """공통 스케일용 — **그룹 안에서만** 최댓값을 공유한다(보이는 구간 기준).

        옵션(계약)과 프로그램(백만원)을 한 눈금에 올리면 그 자체가 오독이다.
        """
        m = 1
        for key, _lab, grp in _ALL_ROWS:
            if grp != group:
                continue
            d = self._products.get(key)
            if not d:
                continue
            for tm, v in _series_minutes(d.get("series")):
                if v0 <= tm < v1:
                    m = max(m, abs(int(v)))
        return m

    def _paint(self) -> None:
        """막대 전체를 캐시 이미지에 그린다 — 데이터가 바뀌거나 크기가 바뀔 때만."""
        t0 = time.perf_counter()
        w, h = max(1, self.width()), max(1, self.height())
        try:
            dpr = float(self.devicePixelRatioF())
        except Exception:
            dpr = 1.0
        pm = QPixmap(max(1, int(w * dpr)), max(1, int(h * dpr)))
        pm.setDevicePixelRatio(dpr)
        p = QPainter(pm)
        try:
            p.setRenderHint(QPainter.Antialiasing, False)
            self._draw(p, w, h)
        finally:
            p.end()
        self._cache = pm
        self._cache_size = (w, h)
        self._dirty = False
        ms = (time.perf_counter() - t0) * 1000.0
        # 첫 그리기는 글꼴 적재가 섞여 느리다(실측 71ms vs 이후 평균 25ms) — 경보에서 뺀다.
        first, self._painted_once = not self._painted_once, True
        if ms > _PAINT_SLOW_MS and not first:
            _now = time.time()
            if _now - _Plot._paint_slow_ts >= 300.0:
                _Plot._paint_slow_ts = _now
                logger.warning(
                    "[OptionFlowChart] 그리기 %.1fms > %.0fms (5분 스로틀) — "
                    "메인 스레드를 매매 파이프라인과 공유한다. 크기 %dx%d",
                    ms, _PAINT_SLOW_MS, w, h)

    def _draw(self, p: QPainter, w: int, h: int) -> None:
        p.fillRect(0, 0, w, h, QColor(_COL["bg2"]))

        x0 = self.LABEL_W
        x1 = max(x0 + 40, w - self.VALUE_W)
        v0, v1 = self.view_range()
        ppm = (x1 - x0) / float(max(1, v1 - v0))
        rect_mode = ppm >= _RECT_MIN_PPM
        bw = max(1, int(ppm * 0.72)) if rect_mode else 1
        row_h = self.row_height()
        spans = self.row_spans(row_h)
        top0 = spans[0][0]
        ybase = spans[-1][0] + spans[-1][1]

        def xm(tm: int) -> int:
            return int(x0 + (tm - v0) * ppm + (ppm - bw) / 2.0) if rect_mode \
                else int(x0 + (tm - v0) * ppm)

        self._geo = {"x0": x0, "x1": x1, "v0": v0, "v1": v1, "ppm": ppm,
                     "top": top0, "bottom": ybase}
        self._rows_geo = []

        fonts = {
            "lab": QFont(), "val": QFont(), "sub": QFont(),
        }
        fonts["lab"].setPointSize(8)
        fonts["val"].setPointSize(8)
        fonts["val"].setBold(True)
        fonts["sub"].setPointSize(7)

        pts = {k: _series_minutes((d or {}).get("series"))
               for k, d in self._products.items()}
        shared_max = {"opt": self._group_max("opt", v0, v1),
                      "fut": self._group_max("fut", v0, v1)}

        prev = None                       # (종류, 그룹)
        for (kind, key, label, group, _wt), (top, rh) in zip(_LAYOUT, spans):
            mid = top + rh // 2
            # 구분선 — 단위가 바뀌는 자리(그룹 경계)와 콜/풋 쌍이 끝나는 자리는 진하게,
            # 같은 쌍 안은 옅게. 상대강도 행은 위 두 행에 붙여 선을 긋지 않는다.
            # (행이 커지면 인접 행의 막대가 서로 붙어 보여 어느 행 것인지 헷갈린다 — 615차)
            if prev is not None and kind != "rs":
                strong = group != prev[1] or prev[0] == "rs"
                p.setPen(QPen(QColor(_COL["border"] if strong else _COL["bg3"]), 1))
                p.drawLine(2, top - 1, w - 2, top - 1)
            prev = (kind, group)

            if kind == "rs":
                self._draw_rs_row(p, key, label, top, rh, mid, pts, fonts,
                                  x0, x1, v0, v1, ppm, bw, xm)
            else:
                self._draw_data_row(p, key, label, group, top, rh, mid, pts,
                                    fonts, x0, x1, v0, v1, rect_mode, bw, xm,
                                    shared_max)

        self._draw_axis(p, fonts, x0, x1, v0, v1, ppm, top0, ybase)
        if self._minimap_h():
            self._draw_minimap(p, fonts, x0, x1, v0, v1)

    def _draw_label(self, p, fonts, mid, label, unit, rs=False) -> None:
        # 🔴 위치를 **행 비율이 아니라 0선(mid) 기준**으로 잡는다.
        #    비율로 두면 행이 커질수록 라벨이 0선에서 멀어져 어느 행의
        #    것인지 눈으로 잇기 어려워진다(행 103px 실측에서 확인).
        p.setPen(QPen(QColor(_COL["muted"])))
        if rs:
            p.setFont(fonts["sub"])
            p.drawText(QRectF(2, mid - 13, self.LABEL_W - 6, 13),
                       Qt.AlignBottom | Qt.AlignRight, "└ " + label)
            p.drawText(QRectF(2, mid, self.LABEL_W - 6, 12),
                       Qt.AlignTop | Qt.AlignRight, "(콜−풋 증감차)")
            return
        p.setFont(fonts["lab"])
        p.drawText(QRectF(2, mid - 17, self.LABEL_W - 6, 16),
                   Qt.AlignBottom | Qt.AlignRight, label)
        if unit:
            p.setFont(fonts["sub"])
            p.drawText(QRectF(2, mid + 1, self.LABEL_W - 6, 13),
                       Qt.AlignTop | Qt.AlignRight, "(%s)" % unit)

    def _draw_badge(self, p, fonts, x1, mid, rh, lines) -> None:
        """오른쪽 칸 — lines = [(글자, 색, 굵게여부)]. 행이 낮으면 앞 2줄만."""
        if rh < 40:
            lines = lines[:2]
        lh = 13
        y = mid - (len(lines) * lh) // 2 - 1
        for txt, col, bold in lines:
            p.setFont(fonts["val"] if bold else fonts["sub"])
            p.setPen(QPen(QColor(col)))
            p.drawText(QRectF(x1 + 4, y, self.VALUE_W - 6, lh),
                       Qt.AlignVCenter | Qt.AlignLeft, txt)
            y += lh

    def _draw_data_row(self, p, key, label, group, top, rh, mid, pts, fonts,
                       x0, x1, v0, v1, rect_mode, bw, xm, shared_max) -> None:
        d = self._products.get(key)
        # 라벨 + 단위 (계측 4원칙 ① — 단위는 섹션이 아니라 행마다 박는다)
        self._draw_label(p, fonts, mid, label, (d or {}).get("unit"))
        p.setPen(QPen(QColor(_COL["zero"]), 1))
        p.drawLine(x0, mid, x1, mid)

        tips: Dict[int, str] = {}
        self._rows_geo.append((mid, tips))
        P = pts.get(key) or []
        if not d or not P:
            # 미수집 — 0 으로 그리지 않고 그렇게 적는다(계측 4원칙 ②).
            p.setFont(fonts["lab"])
            p.setPen(QPen(QColor(_COL["muted"])))
            p.drawText(QRectF(x0, mid - 8, x1 - x0, 16), Qt.AlignCenter, "미수집")
            return

        thr = _deadband([b - a for (_t, a), (_u, b) in zip(P, P[1:])])
        states = _bar_states(P, thr)
        vis = [s for s in states if v0 <= s[0] < v1]
        if self._shared:
            scale_max = shared_max.get(group, 1)
        else:
            scale_max = max([1] + [abs(v) for _t, v, _d, _s in vis])
        # 막대 진폭. 여백을 2px 만 남긴다 — 행이 작을 때(MIN_ROW_H=26) 체감이 다르다.
        half = rh // 2 - 2

        col = QColor(_ROW_COLOR.get(key, _COL["blue"]))
        dim = QColor(col)
        dim.setAlpha(70)
        flat = QColor(_COL["muted"])
        hollow_bg = QColor(_COL["bg"])
        glyph = {1: "▲", -1: "▼", 0: "─"}
        # [621차 후속] **그 분에 행이 없는 칸**을 비워 두지 않고 0선 위 점으로 찍는다.
        #   비워 두면 「아직 안 왔다」와 「그 분엔 원천 행이 없다」가 구분되지 않아
        #   맨 오른쪽 열이 행마다 들쭉날쭉해 보인다(사용자 보고 2026-09-23).
        #   0 으로 잇지는 않는다 — 점은 「값 없음」이지 「변화 0」이 아니다(계측 4원칙 ②).
        #   실측: 옵션 원천(7222)은 **체결이 없는 분에 행을 주지 않는다**
        #   (2026-09-23 10:00~10:56 wk_mon_call 57행 중 누락 0, 하루 124행 vs 132행).
        if rect_mode and P:
            have = set(tm for tm, _v in P)
            end = min(self._latest_min() or P[-1][0], v1 - 1)
            miss_col = QColor(_COL["muted"])
            for tm in range(max(P[0][0], v0), end + 1):
                if tm not in have:
                    p.fillRect(xm(tm) + bw // 2 - 1, mid - 1, 3, 3, miss_col)
                    tips[tm] = "행 없음"
        for tm, v, dl, st in vis:
            tips[tm] = "시작" if dl is None else "%s %s" % (glyph[st], _fmt_qty(dl))
            px = int(max(-1.0, min(1.0, v / float(scale_max))) * half)
            # 0 이 아닌 값은 반올림으로 사라지지 않게 최소 1px 을 준다 —
            # "값이 0" 과 "너무 작아 안 보임"은 화면에서 구분돼야 한다.
            if v and px == 0:
                px = 1 if v > 0 else -1
            if not px:
                continue
            y = min(mid, mid - px)
            hh = abs(px)
            x = xm(tm)
            if rect_mode:
                if st > 0:                                    # 증가 — 꽉 찬 막대
                    p.fillRect(x, y, bw, hh, col)
                elif st < 0:                                  # 감소 — 속 빈 막대
                    p.fillRect(x, y, bw, hh, hollow_bg)
                    p.setPen(QPen(col, 1))
                    p.drawRect(x, y, max(0, bw - 1), max(0, hh - 1))
                else:                                         # 변화 없음 — 가는 선
                    p.fillRect(x + bw // 2, y, 1, hh, flat)
            else:
                p.fillRect(x, y, 1, hh, col if st > 0 else (dim if st < 0 else flat))

        # 오른쪽 배지 — 이번 봉 증감·연속 / 시초 대비 / 누계 + 행 축.
        # 🔴 누계를 함께 싣는 이유: 걷어낸 6카드가 보여주던 값이 그것이다.
        #    증감만 남기면 미결제 62,767 같은 절대 수준이 화면에서 사라진다.
        st_last, n = _streak([s for _t, _v, dl, s in states if dl is not None])
        last_d = states[-1][2]
        head = ("%s%d  %s" % (glyph[st_last], n, _fmt_qty(last_d))
                if last_d is not None else "— 첫 봉")
        cur = int(d.get("delta", 0))
        sub = "누계 %s" % format(int(d.get("value", 0)), ",")
        if not self._shared:
            # 행마다 눈금이 다르다는 사실을 화면에 박는다.
            # (공통 스케일일 때는 그룹 안이 같으므로 표기하지 않는다)
            sub += " · ±%s" % format(int(scale_max), ",")
        self._draw_badge(p, fonts, x1, mid, rh, [
            (head, col.name() if st_last else _COL["muted"], True),
            ("시초 %s" % _fmt_qty(cur), _COL["text"] if cur else _COL["muted"], False),
            (sub, _COL["muted"], False),
        ])

    def _draw_rs_row(self, p, key, label, top, rh, mid, pts, fonts,
                     x0, x1, v0, v1, ppm, bw, xm) -> None:
        call_k, put_k = _RS_BY_KEY[key]
        self._draw_label(p, fonts, mid, label, None, rs=True)
        p.setPen(QPen(QColor(_COL["zero"]), 1))
        p.drawLine(x0, mid, x1, mid)

        tips: Dict[int, str] = {}
        self._rows_geo.append((mid, tips))
        c_pts, p_pts = pts.get(call_k) or [], pts.get(put_k) or []
        if not c_pts or not p_pts:
            p.setFont(fonts["sub"])
            p.setPen(QPen(QColor(_COL["muted"])))
            p.drawText(QRectF(x0, mid - 7, x1 - x0, 14), Qt.AlignCenter,
                       "미수집 — 콜·풋이 모두 있어야 잰다")
            return

        R = _rs_points(c_pts, p_pts)
        thr = _deadband([r for _t, r, _c in R])
        vis = [x for x in R if v0 <= x[0] < v1]
        smax = max([1] + [abs(r) for _t, r, _c in vis])
        cmax = max([1] + [abs(c) for _t, _r, c in vis])
        half = max(2, rh // 2 - 2)
        c_col = QColor(_ROW_COLOR[call_k])
        p_col = QColor(_ROW_COLOR[put_k])
        flat = QColor(_COL["muted"])

        for tm, r, _cum in vis:
            x = xm(tm)
            if abs(r) <= thr:                     # 균형 — 중앙선 위 짧은 눈금
                p.fillRect(x, mid - 1, bw, 3, flat)
                tips[tm] = "균형 %s" % _fmt_qty(r)
                continue
            px = max(1, int(min(1.0, abs(r) / float(smax)) * half))
            if r > 0:
                p.fillRect(x, mid - px, bw, px, c_col)
                tips[tm] = "콜 우위 %s" % _fmt_qty(r)
            else:
                p.fillRect(x, mid, bw, px, p_col)
                tips[tm] = "풋 우위 %s" % _fmt_qty(r)

        # 누적 콜−풋 점선 — 막대와 **축이 다르다**(배지에 둘 다 적는다).
        pen_col = QColor(_COL["text"])
        pen_col.setAlpha(170)
        p.setPen(QPen(pen_col, 1, Qt.DashLine))
        prev_pt, prev_tm = None, None
        for tm, _r, cum in vis:
            pt = QPoint(int(x0 + (tm - v0) * ppm + ppm / 2.0),
                        mid - int(max(-1.0, min(1.0, cum / float(cmax))) * half))
            if prev_pt is not None and tm - prev_tm <= _GAP_BREAK_MIN:
                p.drawLine(prev_pt, pt)
            prev_pt, prev_tm = pt, tm

        states = [0 if abs(r) <= thr else (1 if r > 0 else -1) for _t, r, _c in R]
        st_last, n = _streak(states)
        if not R:
            head, hcol = "— 표본 없음", _COL["muted"]
        elif st_last > 0:
            head, hcol = "콜 우위 %d연속" % n, c_col.name()
        elif st_last < 0:
            head, hcol = "풋 우위 %d연속" % n, p_col.name()
        else:
            head, hcol = "균형 %d" % n, _COL["muted"]
        last_r = R[-1][1] if R else 0
        last_c = R[-1][2] if R else 0
        self._draw_badge(p, fonts, x1, mid, rh, [
            (head, hcol, True),
            ("%s · 누적 %s" % (_fmt_qty(last_r), _fmt_qty(last_c)),
             _COL["text"], False),
            ("막대 ±%s · 선 ±%s" % (format(smax, ","), format(cmax, ",")),
             _COL["muted"], False),
        ])

    def _draw_axis(self, p, fonts, x0, x1, v0, v1, ppm, top0, ybase) -> None:
        p.setFont(fonts["lab"])
        if not self._window_min:
            # 시간당 픽셀이 좁으면 2시간 간격 — 좁은 탭에서 「9101112…」로 붙는다(621차 렌더)
            ticks = [hh * 60 for hh in range(9, 16, 1 if ppm * 60 >= 24 else 2)]
            fmt = lambda tm: "%d" % (tm // 60)             # noqa: E731
        else:
            step = 5 if ppm * 5 >= 36 else (10 if ppm * 10 >= 36 else 30)
            first = ((v0 + step - 1) // step) * step
            ticks = list(range(first, v1, step))
            fmt = lambda tm: "%d:%02d" % divmod(tm, 60)    # noqa: E731
        for tm in ticks:
            if tm < v0 or tm >= v1:
                continue
            x = int(x0 + (tm - v0) * ppm)
            p.setPen(QPen(QColor(_COL["border"]), 1))
            p.drawLine(x, top0, x, ybase)
            p.setPen(QPen(QColor(_COL["muted"])))
            p.drawText(QRectF(x - 22, top0 - self.AXIS_H, 44, self.AXIS_H - 2),
                       Qt.AlignCenter, fmt(tm))

    def _draw_minimap(self, p, fonts, x0, x1, v0, v1) -> None:
        """세션 전체 띠 — 데이터가 있는 구간과 지금 보는 구간(주황 틀)."""
        my = self.PAD_V
        mh = self.MINIMAP_H - 8
        span = float(_T1_MIN + 1 - _T0_MIN)

        def mx(tm: int) -> int:
            return int(x0 + (tm - _T0_MIN) * (x1 - x0) / span)

        p.fillRect(x0, my, x1 - x0, mh, QColor(_COL["bg3"]))
        firsts = [ps[0][0] for ps in (
            _series_minutes((d or {}).get("series")) for d in self._products.values()) if ps]
        latest = self._latest_min()
        if firsts and latest is not None:
            band = QColor(_COL["blue"])
            band.setAlpha(60)
            p.fillRect(mx(min(firsts)), my + 3, max(1, mx(latest) - mx(min(firsts))),
                       mh - 6, band)
        # [621차 후속2] 띠 안의 「9 10 11 …」 숫자는 아래 시간 눈금과 헷갈렸다(사용자 질문
        #   「상단 9 10 11 의미는?」). 숫자를 지우고 정시 자리엔 옅은 눈금만, 대신
        #   주황 틀 **안에** 지금 보는 구간을 시각으로 적는다 — 띠가 무엇인지 스스로 말한다.
        for hh in range(9, 16):
            x = mx(hh * 60)
            p.setPen(QPen(QColor(_COL["border"]), 1))
            p.drawLine(x, my + mh - 4, x, my + mh)
        p.setPen(QPen(QColor(_COL["orange"]), 1))
        bx, bw_ = mx(v0), max(2, mx(v1) - mx(v0))
        p.drawRect(bx, my, bw_, mh - 1)
        p.setFont(fonts["sub"])
        p.drawText(QRectF(bx, my, max(bw_, 80), mh), Qt.AlignCenter,
                   "%02d:%02d ~ %02d:%02d" % (divmod(v0, 60) + divmod(v1 - 1, 60)))
        p.setPen(QPen(QColor(_COL["muted"])))
        p.drawText(QRectF(2, my, self.LABEL_W - 6, mh),
                   Qt.AlignVCenter | Qt.AlignRight, "하루 전체")
        self._geo["mini"] = (x0, x1, my, mh + 2)

    def _draw_status_strip(self, p: QPainter) -> None:
        """[621차 후속8] ● LIVE · 브로커 시각 · 다음 분봉 ▷ [바] N초 — 하루 전체 띠와 시간 눈금 사이.

        대시보드 상단 상태 바와 같은 문법(색 경계 15초·5초)을 쓴다 — 눈이 옮겨가기 쉽게.
        🔴 시각은 **브로커 기준**이다. 모르면 PC 시각을 쓰되 「PC」라고 적는다(계측 4원칙 ④).
        """
        if not self._status:
            return
        g = self._geo
        x0 = g.get("x0", 96) if g else 96
        x1 = g.get("x1", self.width() - 118) if g else self.width() - 118
        y = self.PAD_V + self._minimap_h()
        h = self.STATUS_H - 4
        now, is_broker, off = self.broker_now()
        tm = now.hour * 60 + now.minute
        live = _T0_MIN <= tm <= _T1_MIN
        p.fillRect(QRectF(x0, y, x1 - x0, h), QColor(_COL["bg3"]))
        mid = y + h / 2.0
        x = x0 + 8

        f_b = QFont("Consolas")
        f_b.setPointSize(10)
        f_b.setBold(True)
        f_s = QFont()
        f_s.setPointSize(8)
        f_sb = QFont()
        f_sb.setPointSize(8)
        f_sb.setBold(True)

        def text(t, font, col, pad=6):
            nonlocal x
            p.setFont(font)
            p.setPen(QPen(QColor(col)))
            w = _text_w(QFontMetrics(font), t)
            # [621차 후속9] 폭을 넉넉히 + 자르지 않는다 — 실화면에서 「브로커 -0.0:」로 잘렸다
            #   (계산 폭과 실제 렌더 폭이 화면 배율에서 어긋난다).
            p.drawText(QRectF(x, y, w + 12, h),
                       Qt.AlignVCenter | Qt.AlignLeft | Qt.TextDontClip, t)
            x += w + pad

        def sep():
            nonlocal x
            p.setPen(QPen(QColor(_COL["border"]), 1))
            p.drawLine(int(x), int(y + 4), int(x), int(y + h - 4))
            x += 10

        # ① LIVE (08:45~15:35) — 점이 깜빡인다
        if live:
            dot = QColor(_COL["green"] if self._blink else _COL["bg"])
            p.setPen(Qt.NoPen)
            p.setBrush(dot)
            p.drawEllipse(QRectF(x, mid - 4, 8, 8))
            p.setBrush(Qt.NoBrush)
            x += 13
            text("LIVE", f_sb, _COL["green"], 10)
        else:
            p.setPen(QPen(QColor(_COL["muted"]), 1))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QRectF(x, mid - 4, 8, 8))
            x += 13
            text("장외", f_sb, _COL["muted"], 10)
        sep()
        # ② 시각 — 브로커 / PC
        text(now.strftime("%H:%M:%S"), f_b, _COL["text"], 8)
        # [621차 후속9] 브로커 칸은 **고정 폭**(값이 바뀌어도 뒤 항목이 흔들리지 않게)
        _slot0 = x
        if is_broker:
            _o = round(off, 1)
            text("브로커 " + ("±0.0s" if _o == 0 else "%+.1fs" % _o), f_s, _COL["muted"], 10)
        else:
            text("PC", f_sb, _COL["orange"], 10)
        x = max(x, _slot0 + 96)
        sep()
        # ③ 다음 분봉 — [621차 후속9] **이 차트에 새 봉 열이 실제로 열린 순간**부터 차오른다.
        #   분 경계(시스템 시계)가 아니다(사용자 지시). 옵션·선물 두 원천이 다 와야 열이
        #   열리므로(후속 동기화 규칙) 실제 열림은 매분 :02~:05 쯤이다 — 그 순간이 0 이다.
        #   간격은 최근 실측 열림 간격의 중앙값(없으면 60초 가정 — 「추정」이라 적는다).
        import time as _tm
        text("다음 분봉 ▷", f_s, _COL["muted"], 6)
        bw, bh = 110, 7
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(_COL["bg"]))
        p.drawRoundedRect(QRectF(x, mid - bh / 2.0, bw, bh), 3, 3)
        if self._bar_opened_mono is None:
            p.setBrush(Qt.NoBrush)
            x += bw + 8
            text("갱신 대기", f_sb, _COL["muted"], 6)
            return
        iv = max(10.0, self._bar_interval_s)
        el = max(0.0, _tm.monotonic() - self._bar_opened_mono)
        rem = iv - el
        if rem > 5:
            col = _COL["cyan"]
        elif rem > -15:
            col = _COL["yellow"]            # 곧 / 약간 늦음
        else:
            col = _COL["red"]               # 15초 넘게 안 온다 — 원천이 멈췄을 수 있다
        p.setBrush(QColor(col))
        p.drawRoundedRect(QRectF(x, mid - bh / 2.0, max(bh, bw * min(1.0, el / iv)), bh), 3, 3)
        p.setBrush(Qt.NoBrush)
        x += bw + 8
        # [621차 후속10] 숫자도 막대와 같은 방향 — 열린 뒤 **경과 초(0부터 증가)**(사용자 지시).
        #   예상 간격을 넘기면 색이 바뀌고 옆에 지연 초를 따로 적는다.
        text("%d초" % int(el), f_b, col, 6)
        if rem <= 0:
            text("지연 +%d초" % int(-rem), f_sb, col, 6)
        if not self._bar_interval_measured:
            text("(간격 60초 가정)", f_s, _COL["muted"], 6)

    def _draw_overlay(self, p: QPainter) -> None:
        """크로스헤어 — 캐시 위에 세로선과 행별 값만 덧그린다."""
        g = self._geo
        tm = self._hover_min
        if tm is None or not g or not (g["v0"] <= tm < g["v1"]):
            return
        ppm = g["ppm"]
        x = int(g["x0"] + (tm - g["v0"]) * ppm + ppm / 2.0)
        lc = QColor(_COL["orange"])
        lc.setAlpha(170)
        p.setPen(QPen(lc, 1, Qt.DashLine))
        p.drawLine(x, g["top"], x, g["bottom"])
        f = QFont()
        f.setPointSize(7)
        p.setFont(f)
        fm = QFontMetrics(f)
        box_bg = QColor(_COL["bg"])
        box_bg.setAlpha(225)
        # 시각 태그 — 행 위 시간 눈금 띠에, 주황 바탕 굵은 글씨로 눈금을 덮는다
        # ([621차 후속2] 사용자 지시: 크로스헤어 시각이 한눈에 보이게).
        ft = QFont()
        ft.setPointSize(9)
        ft.setBold(True)
        ts = "%02d:%02d" % divmod(tm, 60)
        tw = _text_w(QFontMetrics(ft), ts) + 14
        tx = max(g["x0"], min(x - tw / 2.0, g["x1"] - tw))
        r = QRectF(tx, g["top"] - self.AXIS_H, tw, self.AXIS_H)
        p.fillRect(r, QColor(_COL["orange"]))
        p.setFont(ft)
        p.setPen(QPen(QColor(_COL["bg"])))
        p.drawText(r, Qt.AlignCenter, ts)
        p.setFont(f)
        for mid, tips in self._rows_geo:
            s = tips.get(tm)
            if not s:
                continue
            tw = _text_w(fm, s) + 8
            bx = x + 4 if x + 4 + tw <= g["x1"] else x - 4 - tw
            r = QRectF(bx, mid - 7, tw, 14)
            p.fillRect(r, box_bg)
            p.setPen(QPen(QColor(_COL["text"])))
            p.drawText(r, Qt.AlignCenter, s)

    # ── 마우스 ────────────────────────────────────────────────────────────
    def _min_at(self, x: int) -> Optional[int]:
        g = self._geo
        if not g or not (g["x0"] <= x < g["x1"]):
            return None
        return g["v0"] + int((x - g["x0"]) / g["ppm"])

    def mouseMoveEvent(self, ev):        # noqa: N802 (Qt)
        try:
            g = self._geo
            tm = self._min_at(ev.pos().x()) if g and ev.pos().y() >= g["top"] else None
            if tm != self._hover_min:        # 분이 바뀔 때만 — 캐시 복사 + 선 하나
                self._hover_min = tm
                self.update()
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('_Plot.mouseMoveEvent', _qe)

    def leaveEvent(self, ev):            # noqa: N802 (Qt)
        try:
            if self._hover_min is not None:
                self._hover_min = None
                self.update()
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('_Plot.leaveEvent', _qe)

    def mousePressEvent(self, ev):       # noqa: N802 (Qt)
        try:
            mini = self._geo.get("mini") if self._geo else None
            if not mini or not self._window_min:
                return
            mx0, mx1, my, mh = mini
            pos = ev.pos()
            if not (mx0 <= pos.x() <= mx1 and my <= pos.y() <= my + mh):
                return
            tm = _T0_MIN + (pos.x() - mx0) * (_T1_MIN + 1 - _T0_MIN) / float(max(1, mx1 - mx0))
            # 클릭한 시각이 구간 가운데에 오게 한다
            self.set_anchor(int(tm + self._window_min // 2))
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('_Plot.mousePressEvent', _qe)

    def wheelEvent(self, ev):            # noqa: N802 (Qt)
        try:
            if not self._window_min:
                return
            notches = ev.angleDelta().y() / 120.0
            if not notches:
                return
            _v0, v1 = self.view_range()
            # 위로 굴리면 과거로 5분씩
            self.set_anchor(int(v1 - 1 - notches * 5))
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('_Plot.wheelEvent', _qe)


class OptionFlowDeltaChart(QWidget):
    """헤더(기준·갱신·구간·스케일) + 13행 차트.

    갱신 경로가 **둘**이다 — 옵션은 `update_flow()`, 선물은 `update_futures_flow()`.
    각 payload 를 따로 보관하고 그릴 때 합친다. 🔴 한쪽 조회가 실패했을 때
    다른 쪽 행까지 지워지면 안 된다(612차 후속5 와 같은 계열의 사고 방지).

    [621차] `window_mode=True` 는 독립 창용이다 — 기본 60분 확대(후속8) + 미니맵 + 상태 줄 +
    「실시간 ▶」. 탭 속 차트는 기본 「전체」 + 「⤢ 크게」 버튼(`popout_requested`).
    탭 차트가 받은 payload 는 `add_mirror()` 로 등록한 차트에 **그대로** 넘긴다 —
    독립 창이 DB 를 따로 조회하지 않게 하는 장치다.
    """

    popout_requested = pyqtSignal()

    def __init__(self, parent=None, window_mode: bool = False):
        super().__init__(parent)
        self._window_mode = bool(window_mode)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        self._lbl_title = QLabel("옵션·선물 수급 — 시초 대비 증감")
        self._lbl_title.setStyleSheet(
            "color:%s;font-size:%dpx;font-weight:bold;"
            % (_COL["blue"], 13 if self._window_mode else 11))
        self._lbl_title.setToolTip(_TITLE_TIP)
        hdr.addWidget(self._lbl_title)
        hdr.addStretch()
        # [613차] 수급 신선도 칩 — 걷어낸 「선물 투자자 수급」 헤더에 있던 것을
        # 여기로 옮겼다. 그 섹션의 카드가 전부 이 차트로 들어왔기 때문이다.
        self._lbl_age = QLabel("수급 ——")
        self._lbl_age.setStyleSheet("color:%s;font-size:9px;" % _COL["muted"])
        hdr.addWidget(self._lbl_age)
        self._lbl_meta = QLabel("——")
        self._lbl_meta.setStyleSheet("color:%s;font-size:9px;" % _COL["muted"])
        # 좁은 탭에서 긴 메타 문구가 최소 폭을 정하지 않게 — 잘릴지언정 차트를 밀어내지 않는다.
        self._lbl_meta.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self._lbl_meta.setMinimumWidth(0)
        hdr.addWidget(self._lbl_meta, 1)

        small = "color:%s;font-size:9px;" % _COL["muted"]
        # 탭 속에서는 조작부를 둘째 줄로 내린다 — 한 줄에 다 두면 헤더 최소 폭이
        # 좁은 탭을 밀어내 오른쪽 배지가 잘린다(621차 렌더 확인).
        ctl = hdr if self._window_mode else QHBoxLayout()
        if ctl is not hdr:
            ctl.setSpacing(6)
            ctl.addStretch()
        self._cmb_win = QComboBox()
        for lab, _n in _WINDOW_CHOICES:
            self._cmb_win.addItem(lab)
        self._cmb_win.setStyleSheet("font-size:9px;")
        ctl.addWidget(self._cmb_win)

        self._btn_live = QPushButton("실시간 ▶")
        self._btn_live.setStyleSheet(
            "color:%s;font-size:9px;padding:1px 6px;" % _COL["orange"])
        self._btn_live.setVisible(False)
        self._btn_live.clicked.connect(self._on_live_clicked)   # 람다는 가드를 못 단다
        ctl.addWidget(self._btn_live)

        self._chk_shared = QCheckBox("공통 스케일")
        self._chk_shared.setChecked(False)
        self._chk_shared.setStyleSheet(small)
        self._chk_shared.toggled.connect(self._on_toggle)
        ctl.addWidget(self._chk_shared)

        if not self._window_mode:
            self._btn_pop = QPushButton("⤢ 크게")
            self._btn_pop.setStyleSheet(
                "color:%s;font-size:9px;padding:1px 6px;" % _COL["blue"])
            self._btn_pop.clicked.connect(self.popout_requested.emit)
            ctl.addWidget(self._btn_pop)
        lay.addLayout(hdr)
        if ctl is not hdr:
            lay.addLayout(ctl)

        if self._window_mode:
            legend = QLabel(
                "■ 꽉 참 = 전봉 대비 증가   □ 속 빔 = 감소   │ 회색 = 변화 없음"
                "   ·   콜↔풋: 위 = 이번 봉 콜이 더 늘음 / 아래 = 풋이 더 늘음 / 점선 = 누적 콜−풋"
                "   ·   0선 위 점 = 그 분 원천 행 없음"
                "   ·   미니맵 클릭·휠 = 과거 보기")
            legend.setStyleSheet(small)
            lay.addWidget(legend)

        self._plot = _Plot(minimap=self._window_mode, status=self._window_mode)
        self._plot.view_changed.connect(self._sync_live_btn)
        lay.addWidget(self._plot, 1)

        self._payload: Dict[str, Any] = {}          # 옵션 6종
        self._fut_payload: Dict[str, Any] = {}      # 선물 4종
        self._age: Tuple[str, str] = ("수급 ——", "ok")
        self._mirrors: List["OptionFlowDeltaChart"] = []
        # [621차 후속] 원천별 「마감된 마지막 분」 — 받은 시각 기준. None = 자르지 않음(복기).
        self._horizon: Dict[str, Optional[int]] = {"opt": None, "fut": None}
        # [621차 후속9] 새 봉 열 감지 — 마지막으로 본 최신 열(분)·열린 시각·열림 간격들
        self._last_col: Optional[int] = None
        self._col_opened_mono: Optional[float] = None
        self._col_intervals: List[float] = []

        # [621차 후속8] 독립 창 기본 90 → 60분(사용자 지시 2026-09-23)
        default_label = "60분" if self._window_mode else "전체"
        self._cmb_win.setCurrentIndex(
            [lab for lab, _n in _WINDOW_CHOICES].index(default_label))
        self._plot.set_window(dict(_WINDOW_CHOICES)[default_label])
        self._cmb_win.currentIndexChanged.connect(self._on_window)

    # ── 내부 ──────────────────────────────────────────────────────────────
    def _merged(self) -> Dict[str, Any]:
        prods = dict(self._payload.get("products") or {})
        prods.update(self._fut_payload.get("products") or {})
        cut = self.display_cutoff()
        if cut is None:
            return prods
        out = {}
        for k, d in prods.items():
            t = _trim_product(d, cut)
            if t is not None:
                out[k] = t
        return out

    # ── [621차 후속] 맨 오른쪽 열 동기화 ─────────────────────────────────
    # 🔴 사용자 보고(2026-09-23 10:56): 「최우측란에 해당 봉이 동시에 올라오지 않는다」.
    #   원인 셋이 겹쳐 있었다 — 전부 표시 계층에서 푼다(수집은 건드리지 않는다).
    #   ① **진행 중인 분이 섞였다.** 수급 타이머는 매분 약 :02 초에 돈다. 그때
    #      옵션 7222 는 그 2초 사이 체결이 있었던 상품만 그 분 행을 준다(실측 10:57:02
    #      수집 — mon_put·wk_thu_* 는 10:57 있음, wk_mon_* 는 10:56 까지).
    #      외인·프로그램은 저장 시각을 분으로 내려 그 분 이름을 달고, 미결제약정은
    #      **마감된 캔들**(직전 분)이다. → 원천마다 마지막 열이 다르다.
    #   ② **두 번에 나눠 그린다.** 한 틱 안에서 선물 4종을 먼저 밀고, 옵션 7222 조회가
    #      끝난 뒤 옵션 6종을 민다. 그 사이 몇 초 동안 선물 행만 한 칸 앞서 있다.
    #   ③ 체결이 없는 분은 옵션 원천에 행이 없어 그 칸이 빈다.
    #   대책: ① 각 원천이 **받은 시각의 직전 분까지만**(마감된 분) 인정하고
    #   ② 화면은 두 원천 중 **늦은 쪽**에 맞춘다 — 옵션이 도착해야 새 열이 한꺼번에
    #   열린다. ③ 은 행 없음 점으로 칸을 채운다(`_draw_data_row`).
    #   ⚠ 한 원천이 `_SYNC_STALE_MIN` 분 넘게 멈추면 기다리지 않는다.
    @staticmethod
    def _complete_horizon(payload: Dict[str, Any],
                          now: Optional[datetime.datetime] = None) -> Optional[int]:
        """이 payload 를 받은 지금 기준 **마감된 마지막 분**. 오늘이 아니면(복기) None."""
        now = now or datetime.datetime.now()
        td = (payload or {}).get("trade_date")
        if td and td != now.date().isoformat():
            return None
        return now.hour * 60 + now.minute - 1

    def display_cutoff(self) -> Optional[int]:
        hs = [h for h in self._horizon.values() if h is not None]
        if not hs:
            return None
        top = max(hs)
        return min(h for h in hs if top - h <= _SYNC_STALE_MIN)

    def _redraw(self) -> None:
        self._plot.set_data(self._merged(), self._chk_shared.isChecked())

    def _on_toggle(self, _checked: bool) -> None:
        try:
            self._redraw()
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('OptionFlowDeltaChart._on_toggle', _qe)

    def _on_window(self, idx: int) -> None:
        try:
            if 0 <= idx < len(_WINDOW_CHOICES):
                self._plot.set_window(_WINDOW_CHOICES[idx][1])
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('OptionFlowDeltaChart._on_window', _qe)

    def _on_live_clicked(self, _checked: bool = False) -> None:
        try:
            self._plot.set_anchor(None)
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('OptionFlowDeltaChart._on_live_clicked', _qe)

    def _sync_live_btn(self) -> None:
        try:
            self._btn_live.setVisible(self._plot.is_zoomed()
                                      and not self._plot.is_following())
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('OptionFlowDeltaChart._sync_live_btn', _qe)

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
        cut = self.display_cutoff()
        if cut is not None:
            # 원천의 최신 봉보다 화면이 짧을 수 있다 — 그 사실을 적는다(계측 4원칙 ④).
            parts.append("표시 ~%02d:%02d" % divmod(cut, 60))
        self._lbl_meta.setText(" · ".join(parts))

    # 미러 예외 스로틀 — 클래스 속성(계측 4원칙 ④)
    _mirror_err_ts = 0.0

    def _each_mirror(self, fn_name: str, *args) -> None:
        """등록된 미러에 같은 호출을 넘긴다. 미러 실패가 이 차트를 막지 않는다."""
        for m in self._mirrors:
            try:
                getattr(m, fn_name)(*args)
            except Exception as exc:
                _now = time.time()
                if _now - OptionFlowDeltaChart._mirror_err_ts >= 300.0:
                    OptionFlowDeltaChart._mirror_err_ts = _now
                    logger.warning(
                        "[OptionFlowChart] 독립 창 전달 실패 (5분 스로틀) — "
                        "독립 창이 낡은 값을 보일 수 있다: %s", exc)

    # ── 외부 주입 ─────────────────────────────────────────────────────────
    def add_mirror(self, other: "OptionFlowDeltaChart") -> None:
        """[621차] 받은 payload 를 그대로 넘길 차트(독립 창)를 등록한다.

        등록 즉시 지금까지 받은 값을 넘긴다 — 창을 나중에 붙여도 빈 화면이 아니다.
        """
        if other is self or other in self._mirrors:
            return
        self._mirrors.append(other)
        if self._payload:
            other.update_flow(self._payload)
        if self._fut_payload:
            other.update_futures_flow(self._fut_payload)
        other.set_age_text(*self._age)

    def _note_bar_clock(self) -> None:
        """[621차 후속9] 화면의 최신 열이 바뀌었으면 그 순간을 「봉 갱신」으로 기록한다.

        payload 도착이 아니라 **열이 실제로 열린 순간**이다 — 한쪽 원천만 와서 열이 안
        열렸으면(동기화 대기) 갱신이 아니다. 간격 표본은 20~180초만 쓴다(재기동·장 시작
        공백을 간격으로 세지 않는다).
        """
        import time as _tm
        col = self._plot._latest_min()
        if col is None or col == self._last_col:
            return
        if self._last_col is None:
            # 첫 적재(기동·창 열기)는 「새 열이 열린 순간」이 아니다 — 그 시각을 0 으로
            #   세면 첫 분 카운트다운이 거짓이다. 다음 실제 열림까지 「갱신 대기」로 둔다.
            self._last_col = col
            return
        now = _tm.monotonic()
        if self._col_opened_mono is not None and self._last_col is not None:
            dt = now - self._col_opened_mono
            if 20.0 <= dt <= 180.0:
                self._col_intervals = (self._col_intervals + [dt])[-10:]
        self._last_col = col
        self._col_opened_mono = now
        iv = sorted(self._col_intervals)
        med = iv[len(iv) // 2] if iv else 60.0
        self._plot.set_bar_clock(now, med, bool(len(iv) >= 2))

    def update_flow(self, payload: Dict[str, Any]) -> None:
        """`WeeklyOptionFlow.get_individual_session_delta()` 결과를 그린다."""
        self._payload = payload or {}
        self._horizon["opt"] = self._complete_horizon(self._payload)
        self._redraw()
        self._note_bar_clock()
        self._render_meta()
        self._each_mirror("update_flow", payload)

    def update_futures_flow(self, payload: Dict[str, Any]) -> None:
        """[613차] `futures_flow_series.get_futures_session_delta()` 결과를 그린다."""
        self._fut_payload = payload or {}
        self._horizon["fut"] = self._complete_horizon(self._fut_payload)
        self._redraw()
        self._note_bar_clock()
        self._render_meta()
        self._each_mirror("update_futures_flow", payload)

    def set_clock_provider(self, provider) -> None:
        """[621차 후속8] 브로커 시계 오프셋 공급자 — 상태 줄(독립 창)이 쓴다."""
        self._plot.set_clock_provider(provider)

    def set_age_text(self, text: str, level: str = "ok") -> None:
        """[613차] 수급 신선도 칩 — 패널이 계산한 문자열·등급을 그대로 받는다.

        level: ok | warn(180초 초과) | stop(600초 초과).
        🔴 3단계를 2단계로 줄이지 말 것 — 「그냥 좀 낡음」과 「멈춤」을 색으로
           가르는 것이 612차 후속5 의 요점이었다.
        """
        self._age = (text, level)
        col = {"stop": _COL["red"], "warn": _COL["orange"]}.get(level, _COL["muted"])
        self._lbl_age.setText(text)
        self._lbl_age.setStyleSheet(
            "color:%s;font-size:9px;%s"
            % (col, "font-weight:bold;" if level != "ok" else ""))
        self._each_mirror("set_age_text", text, level)


class OptionFlowDeltaWindow(QDialog):
    """[621차] 옵션·선물 수급 증감 독립 창 (Ctrl+Shift+F).

    탭 속 차트는 봉 하나가 0.25px 라 증감을 못 읽는다. 이 창은 보조 모니터에
    띄워 두는 용도다 — 모달이 아니고, 닫아도 파괴하지 않고 숨긴다.
    ⚠ 데이터는 탭 차트의 `add_mirror()` 로만 받는다. 이 창이 DB 를 열지 않는다.
    """

    SHORTCUT_TEXT = "Ctrl+Shift+F"
    PREFS_KEY = "option_flow_window_geometry"
    # 32-bit GDI 보호 — 기본 배치 상한. 저장·복원 상한은 `window_utils.dib_safe_size`
    # (모니터 배율 기준 예산 — 1분봉 창과 같은 규칙, 621차 후속5).
    MAX_W, MAX_H = 1920, 1060

    def __init__(self, parent=None, prefs_path: Optional[str] = None):
        super().__init__(parent)
        self.setModal(False)
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint
                            | Qt.WindowCloseButtonHint)
        self.setWindowTitle("옵션·선물 수급 — 봉별 증감 (%s)" % self.SHORTCUT_TEXT)
        self.setStyleSheet("QDialog{background:%s;}" % _COL["bg2"])
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)
        self.chart = OptionFlowDeltaChart(window_mode=True)
        lay.addWidget(self.chart)
        # 🔴 None 이면 저장하지 않는다 — 테스트가 사용자의 ui_prefs.json 을 건드리면 안 된다.
        self._prefs_path = prefs_path
        self._geo_restored = False
        self._close_sc = QShortcut(QKeySequence(self.SHORTCUT_TEXT), self)
        self._close_sc.activated.connect(self.close)

    def toggle(self) -> None:
        try:
            if self.isVisible() and not self.isMinimized():
                self.close()
                return
            if not self._geo_restored:
                # show() 전에 위치를 잡아야 보조 모니터 DPI 로 HWND 가 생긴다
                # (1분봉 차트 창의 WM_DPICHANGED 크기 뒤죽박죽 사고와 같은 대책).
                self._restore_geometry()
                self._geo_restored = True
                # [621차 후속4] 작업표시줄 단추 — 없으면 최소화한 창이 화면 왼쪽 아래
                #   작은 막대로만 남는다(소유 창). 위치를 잡은 뒤, 처음 보이기 전에.
                from dashboard.window_utils import force_taskbar_button
                force_taskbar_button(self)
            self.showNormal()
            self.raise_()
            self.activateWindow()
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('OptionFlowDeltaWindow.toggle', _qe)

    # ── 위치 기억 ─────────────────────────────────────────────────────────
    def _read_prefs(self) -> Dict[str, Any]:
        if not self._prefs_path or not os.path.exists(self._prefs_path):
            return {}
        try:
            with open(self._prefs_path, "r", encoding="utf-8") as f:
                return json.load(f) or {}
        except Exception:
            return {}

    def _default_geometry(self) -> None:
        primary = QApplication.primaryScreen()
        others = [s for s in QApplication.screens() if s is not primary]
        scr = others[0] if others else primary
        if scr is None:
            self.resize(1100, 860)
            return
        sg = scr.availableGeometry()
        w = min(1100, sg.width() - 40, self.MAX_W)
        h = min(900, sg.height() - 40, self.MAX_H)
        self.setGeometry(sg.x() + (sg.width() - w) // 2,
                         max(sg.y(), sg.y() + (sg.height() - h) // 2), w, h)

    def _restore_geometry(self) -> None:
        try:
            geo = self._read_prefs().get(self.PREFS_KEY)
            if not geo:
                self._default_geometry()
                return
            x, y = int(geo["x"]), int(geo["y"])
            w, h = int(geo["w"]), int(geo["h"])
            scr = QApplication.screenAt(QPoint(x + w // 2, y + h // 2))
            if scr is None:               # 모니터 분리 등 — 저장 좌표가 어느 화면에도 없다
                self._default_geometry()
                return
            # [621차 후속5] 모니터 배율 기준 DIB 예산(1분봉 창과 같은 규칙)
            from dashboard.window_utils import dib_safe_size, fits_desktop
            # [621차 후속7] 여러 모니터에 걸친 창은 **그대로** 복원한다 — 중심 모니터
            #   하나로 자르면 걸쳐 둔 창이 그 모니터 폭으로 준다.
            if fits_desktop(x, y, w, h):
                w, h, _clip = dib_safe_size(scr, w, h, clip_to_screen=False)
                self.setGeometry(x, y, w, h)
                return
            w, h, _clip = dib_safe_size(scr, w, h)
            av = scr.availableGeometry()
            x = max(av.left(), min(x, av.right() - w))
            y = max(av.top(), min(y, av.bottom() - h))
            self.setGeometry(x, y, w, h)
        except Exception as exc:
            logger.warning("[OptionFlowWindow] 위치 복원 실패 — 기본 배치: %s", exc)
            self._default_geometry()

    def _save_geometry(self) -> None:
        if not self._prefs_path:
            return
        try:
            # [621차 후속5] 최대화·최소화 중에도 되돌아갈 보통 크기를 저장한다.
            g = (self.normalGeometry()
                 if (self.isMinimized() or self.isMaximized()) else self.geometry())
            if g.width() <= 0 or g.height() <= 0:
                return
            from dashboard.window_utils import dib_safe_size
            scr = QApplication.screenAt(g.center()) or QApplication.primaryScreen()
            # [621차 후속7] 저장은 모니터 폭으로 자르지 않는다(걸친 창) — 예산만 적용
            w, h, clipped = dib_safe_size(scr, g.width(), g.height(), clip_to_screen=False)
            if clipped:
                logger.warning("[OptionFlowWindow] 창 크기 저장 축소 %dx%d → %dx%d "
                               "(32-bit DIB 예산)", g.width(), g.height(), w, h)
            prefs = self._read_prefs()      # 다른 키는 병합 — 덮어쓰기 금지
            prefs[self.PREFS_KEY] = {"x": g.x(), "y": g.y(), "w": w, "h": h}
            with open(self._prefs_path, "w", encoding="utf-8") as f:
                json.dump(prefs, f, ensure_ascii=False)
        except Exception as exc:
            logger.warning("[OptionFlowWindow] 위치 저장 실패: %s", exc)

    def hideEvent(self, ev):             # noqa: N802 (Qt) — 닫기·Esc 모두 여기로 온다
        try:
            if not ev.spontaneous():         # 최소화(OS 발)는 닫기가 아니다
                self._save_geometry()
            super().hideEvent(ev)
        except Exception as _qe:  # noqa: BLE001 — Qt 진입점 최후 방어선(621차 후속11)
            _qt_guard_fail('OptionFlowDeltaWindow.hideEvent', _qe)
