# -*- coding: utf-8 -*-
"""[MW0601 493차 후속5 / F-Q] 장전 스케일러 재적합 궤적을 한 줄로 남긴다.

왜 필요한가 (2026-08-25 실측)
-----------------------------
장 열기 전에 스케일러를 **네 번** 다시 맞췄는데 개장 첫 분에 또 어긋났다
(`[AutoMasked]` 4~5개 · `conf=0.000` 이 첫 4분 중 2분).

그런데 지금 로그로는 그것이 **나빠지는 중인지 원래 그런지** 구분할 수 없다.
단계별 z경고가 다섯 줄에 흩어져 있고, 각 줄은 자기 구간만 말한다:

    08:48 P1  18→11
    08:50 P2  12→6
    08:55 P3  10→6
    08:57 P4  13→4

🔴 **매 단계의 시작값이 직전 단계 종료값보다 크다**(11→12, 6→10, 6→13).
창이 바뀌며 재측정되기 때문인데, 이 사실이 눈에 띄지 않는다 — 한 줄로 모으고
**재증가폭**을 명시하면 *"줄이고 있다"* 와 *"못 따라가고 있다"* 가 갈린다.
그 값이 매일 크면 문제는 재적합 **횟수**가 아니라 **창 선택(30봉 고정)** 이다.

⚠ 이 fix는 **계측만** 한다. 값을 새로 계산하지 않고 이미 찍힌 것을 모은다.
⚠ F-Q ②(08:59 확인 사격)도 **재측정만** 하고 재적합하지 않는다 — 개장 1분 전에
  스케일러를 바꾸면 첫 분 예측이 어제까지와 다른 공간에서 나온다
  (332차·337차 shape mismatch 계열). 승격은 10거래일 섀도 뒤 주간회의 안건이다.
"""
import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from main import format_premarket_scaler_trace as fmt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: 2026-08-25 실측 궤적.
TRACE_0825 = [("08:48 P1", 18, 11), ("08:50 P2", 12, 6),
              ("08:55 P3", 10, 6), ("08:57 P4", 13, 4)]


def test_all_stages_appear_in_one_line():
    out = fmt(TRACE_0825, canary_z=13)
    assert out.count("\n") == 0, "한 줄이어야 한다 — 흩어지면 이 fix의 목적이 사라진다"
    for label in ("08:48 P1", "08:50 P2", "08:55 P3", "08:57 P4"):
        assert label in out
    assert "18" in out and "11" in out


def test_regrowth_is_surfaced():
    """🔴 핵심 — 재증가폭이 보여야 한다.

    11→12(+1), 6→10(+4), 6→13(+7). 이것이 안 보이면 종전 다섯 줄과 다를 바 없다.
    """
    out = fmt(TRACE_0825, canary_z=13)
    assert "(+1)" in out and "(+4)" in out and "(+7)" in out
    assert "재증가 누계 +12" in out, "누계가 없으면 하루치 크기를 못 잰다"


def test_no_regrowth_marker_when_continuous():
    """이어지는 구간(직전 종료 == 이번 시작)에는 표시를 붙이지 않는다 — 노이즈 억제."""
    out = fmt([("P1", 10, 6), ("P2", 6, 3)], canary_z=3)
    assert "(+0)" not in out
    assert "재증가 누계 +0" in out


def test_regression_is_not_counted_as_regrowth():
    """시작값이 오히려 **줄어든** 구간은 누계에 더하지 않는다(음수 상쇄 금지).

    상쇄를 허용하면 "크게 튀었다가 크게 줄었다"가 0으로 보인다.
    """
    out = fmt([("P1", 10, 8), ("P2", 5, 4)], canary_z=4)
    assert "(-3)" in out, "감소도 표시는 한다(관측 사실이다)"
    assert "재증가 누계 +0" in out


def test_canary_gap_is_separate():
    """Canary는 창(60봉)이 달라 마지막 after와 다를 수 있다 — 뭉개지 않는다."""
    out = fmt(TRACE_0825, canary_z=13)
    assert "canary(60봉)=13" in out
    assert "(+9)" in out, "마지막 단계(4) 대비 격차가 드러나야 한다"


def test_empty_trace_says_so():
    """단계가 없으면 **없다고 말한다** — 빈 줄이나 0으로 위장하지 않는다."""
    out = fmt([])
    assert "단계 없음" in out
    assert "기동하지 않았다" in out


def test_canary_omitted_is_not_zero():
    """`canary_z=None` 이면 그 항목을 아예 안 쓴다(0으로 쓰면 거짓말이 된다)."""
    out = fmt([("P1", 5, 3)])
    assert "canary" not in out


# ── 배선 확인 (정적) ────────────────────────────────────────────────────────
def _main_src():
    return io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()


def test_trace_is_emitted_once_per_day():
    """하루 1회 제한이 실제로 걸려 있는가 — 매 Canary마다 찍으면 노이즈다."""
    src = _main_src()
    assert "_pm_trace_emitted" in src
    assert "self._pm_trace_emitted = True" in src


def test_shadow_does_not_refit():
    """🚫 F-Q ② 는 **재측정만** 한다 — 08:59 재적합이 섞이면 안 된다."""
    src = _main_src()
    idx = src.index("[CanaryShadow]")
    block = src[max(0, idx - 2000): idx + 1200]
    assert "refit_scalers_only" not in block, (
        "08:59 섀도 블록에 재적합 호출이 있다 — 개장 1분 전 추론 공간 이동 위험")
    assert "재적합 없음" in block, "로그가 '재측정만'임을 말해야 한다"


def test_shadow_runs_once():
    src = _main_src()
    assert "_pm_canary_shadow_done" in src
    assert "self._pm_canary_shadow_done = True" in src


def test_shadow_distinguishes_unmeasured_baseline():
    """08:55 단계가 없으면 **미측정**이라고 쓴다 — 0개로 쓰지 않는다(4원칙 ②)."""
    src = _main_src()
    idx = src.index("[CanaryShadow]")
    block = src[idx: idx + 900]
    assert "미측정" in block and "비교불가" in block


def test_state_is_explicitly_initialized():
    """`getattr(self, "_x", 기본값)` 폴백으로 읽지 않는가(계측 4원칙 ④)."""
    src = _main_src()
    for name in ("_pm_scaler_trace", "_pm_trace_emitted", "_pm_canary_shadow_done"):
        assert re.search(r"self\.%s\s*=" % name, src), "%s 명시 초기화가 없다" % name
        assert not re.search(r'getattr\(self,\s*["\']%s["\']' % name, src), (
            "%s 를 getattr 폴백으로 읽는다 — 457차 사고 패턴" % name)
