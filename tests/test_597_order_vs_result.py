# -*- coding: utf-8 -*-
"""[MW0601 597차] <끝이 손절로 끝나는 지시>가 결과통으로 빠지지 않는가.

무엇이 무너졌었나
-----------------
`_flush` 는 `_PT_RESULT` 만 보고 결과/지시를 갈랐다. 그런데 그의 지시는 문장 끝이
<...손절>로 끝나는 경우가 아주 많다:

    998 매수 맥점. 993 이탈시 손절
    1094매수 1088 손절

이것들이 전부 **결과로 빠져** 화면에서 통째로 사라졌다. 8월 사료 13일치를 넣고
나서야 드러났다(실측 2026-09-17):

    08-04  지시 0건 · 레벨선 0개   <- 하루 전체가 화면에서 증발
    08-14  결과 7건 · 08-24 결과 9건

가르는 기준
-----------
[!] **그 줄이 앞으로 할 일을 말하는가.** 진입 레벨이 들어 있으면 지시다 -
  끝에 손절이 붙어 있어도 마찬가지다. 진입 레벨이 없을 때만 결과를 따진다.
  체결 보고(<1085-7에서 매수 체결>)는 진입 규칙의 `(?!\\s*체결)` 부정
  전방탐색이 이미 걸러내므로 결과로 남는다.

실행:
    conda run -n py37_32 python -m pytest tests/test_597_order_vs_result.py -v
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

from dashboard.main_dashboard import parse_peter_orders  # noqa: E402

_APP = QApplication.instance() or QApplication(sys.argv)
_DAY = "2026-08-04"


def _one(text, hm="9:06 AM · Aug 4, 2026"):
    return parse_peter_orders("%s\n%s\n" % (text, hm), 0.0, _DAY)


# ── 지시 - 끝이 손절이어도 진입이 있으면 지시다 ─────────────────────────────

@pytest.mark.parametrize("line, entry", [
    ("998 매수 맥점. 993 이탈시 손절", 998.0),      # 실측 08-04 09:06
    ("1094매수 1088 손절", 1094.0),                 # 실측 08-14 09:49
    ("975 맥점 부근 오면 매수. 970 손절.", 975.0),  # 실측 08-04 09:32
    ("1010매수 손절 1006", 1010.0),                 # 실측 08-25 09:20
])
def test_entry_line_ending_in_stop_is_still_an_order(line, entry):
    od, rs, ax, uk = _one(line)
    assert len(od) == 1, "<%s>가 지시로 안 잡힌다 - 화면에서 사라진다." % line
    assert od[0]["entry"] == entry
    assert rs == [], "지시가 결과통으로 빠졌다."


# ── 결과 - 진입이 없으면 결과다 ─────────────────────────────────────────────

@pytest.mark.parametrize("line", [
    "1077 손절.",                      # 실측 08-24 09:19
    "1085 매도 체결",                  # 실측 08-13 09:09
    "1085-7에서 매수 체결. 손절가 1080",  # 실측 08-14 10:29
    "1083 청산체결. 6P 수익 - 5P 손실.",  # 실측 08-24 10:18
    # [597차 후속] 592차가 `_PT_RESULT` 에서 <청산>을 통째로 빼면서 놓쳤던 형태.
    #   <1049 청산가>(예고)를 살리려던 수정이 <1023 청산.>(보고)까지 흘려보냈다.
    "1023 청산.",                        # 실측 08-12 10:12
    "1076 청산. 9P 수익완료.",            # 실측 08-13 13:29
    "1075 청산완료. 추가 4P수익.",         # 실측 08-13 14:24
    "1024 청산. 14P 수익.",               # 실측 08-19 10:04
])
def test_pure_report_is_still_a_result(line):
    od, rs, ax, uk = _one(line)
    assert len(rs) == 1, "<%s>는 이미 일어난 일이다 - 지시로 그리면 안 된다." % line
    assert od == []


# ── <청산>은 낱말로 못 가른다 - 레벨이 나오는가로 가른다 ────────────────────

@pytest.mark.parametrize("line", [
    "1049 청산가",        # 실측 09-16 09:15 - 앞으로 여기서 끊겠다는 예고
    "1081 청산가.",       # 실측 08-20 10:04
    "1023 청산가",        # 실측 08-25 09:22
])
def test_target_line_stays_an_aux_not_a_result(line):
    """같은 <청산>이라도 target 레벨을 낳으면 예고다. 결과통으로 가면 선이 사라진다."""
    od, rs, ax, uk = _one(line)
    assert len(ax) == 1, "<%s>가 예고로 안 잡힌다 - 목표선이 사라진다." % line
    assert rs == [], "<%s>를 결과로 봤다 - 592차가 고친 것이 되돌아왔다." % line


# ── 회귀 - 09-16 판정이 바뀌지 않는다 ───────────────────────────────────────

def test_0916_classification_unchanged():
    """592~594차가 세운 09-16 결과(지시1 · 예고1 · 결과2 · 미분류1)를 고정한다."""
    txt = ("장시작후 1040 밑으로 훅 빠지면 매수 기회니 대기 그냥 날라가면 관망\n"
           "8:58 AM · Sep 16, 2026\n\n"
           "1039 돌파시 매수 손절가 1036\n9:00 AM · Sep 16, 2026\n\n"
           "1039 매수체결\n9:00 AM · Sep 16, 2026\n\n"
           "1049 청산가\n9:15 AM · Sep 16, 2026\n\n"
           "1049 청산체결.\n9:32 AM · Sep 16, 2026\n")
    od, rs, ax, uk = parse_peter_orders(txt, -4.00, "2026-09-16")
    assert (len(od), len(ax), len(rs), len(uk)) == (1, 1, 2, 1)
