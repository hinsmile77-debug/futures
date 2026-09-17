# -*- coding: utf-8 -*-
"""[MW0601 602차] 돌파 매도 진입 · 레벨이 트윗 경계를 넘지 않는가.

둘 다 2026-09-17 사료를 처음 넣어 보다가 드러났다. 8월 13일치로도 안 보였다 -
그 달에는 (1) 돌파 매도가 08-26/08-31 딱 이틀이었고 그 이틀이 <지시 0건>으로
조용히 비어 있었으며, (2) 경계 누수는 레벨 하나가 더 그려질 뿐이라 세어 보기
전에는 눈에 안 띄었다.

① 돌파 매도
    `entry_brk` 는 <돌파 시 (매수|재매수)> 로 **매수 전용**이었다. 그런데 그는
    하방을 같은 어법으로 말한다 - <1062 돌파시 매도> <1085하향 돌파시 매도>
    <1050 하방돌파할때 매도>. 진입이 통째로 빠져 손절선만 남았다.
    [!] 매도는 새 kind 를 만들지 않고 `entry_sell` 로 낸다. 새 kind 는 side 판정
      (<"S" if kind == "entry_sell">)·색·라벨을 전부 따라 고쳐야 하고, 하나라도
      빠뜨리면 **매도가 매수로 그려진다.** 방향이 틀리는 것이 제일 나쁘다.

② 줄 경계 누수
    `parse_peter_text` 가 원문 전체를 통째로 정규식에 넣어, 패턴 안의 `\\s*` 가
    줄바꿈을 먹고 **두 트윗을 이어붙였다.** 실측 09-17:
        <1052 청산가>(09:46) + <1065 돌파시 다시 매도>(10:10)
    가 `청산가\\s*(\\d{3,4})` 에 걸려 **있지도 않은 <목표 1065>** 를 만들었다.
    호출부가 블록을 개행으로 잇고 블록 자체는 한 줄이므로, 줄 단위로 끊으면
    블록 경계와 정확히 일치한다.

실행:
    $env:PYTHONIOENCODING="utf-8"
    ...\\py37_32\\python.exe -m pytest tests/test_602_breakout_sell_and_line_bleed.py -v
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

from dashboard.main_dashboard import (  # noqa: E402
    parse_peter_orders, parse_peter_text)

_APP = QApplication.instance() or QApplication(sys.argv)


def _kinds(text):
    return [(h["kind"], h["level"]) for h in parse_peter_text(text, 0.0)]


# ── (1) 돌파 매도 - 전부 실측 원문이다 ──────────────────────────────────────

@pytest.mark.parametrize("line, level", [
    ("1062 돌파시 매도. 손절 1066", 1062.0),          # 09-17 09:16
    ("1065 돌파시 다시 매도. 손절가 1068", 1065.0),    # 09-17 10:10
    ("1068 돌파시 재매도. 손절가 1072", 1068.0),       # 09-17 13:43
    ("1085하향 돌파시 매도. 손절가 1089", 1085.0),     # 08-26 12:48
    ("1050 하방돌파할때 매도. 손절가 1055", 1050.0),   # 08-31 09:31
])
def test_breakout_sell_is_an_entry(line, level):
    assert ("entry_sell", level) in _kinds(line), (
        "<%s> 의 진입이 안 잡힌다 - 손절선만 남고 깃발이 사라진다." % line)


@pytest.mark.parametrize("line, level", [
    ("1039 돌파시 매수 손절가 1036", 1039.0),          # 09-16 09:00
    ("1092돌파시 매수. 손절 1088", 1092.0),            # 08-14 10:34
    ("1041돌파시 매수. 손절가 1036", 1041.0),          # 08-20 09:06
])
def test_breakout_buy_still_works(line, level):
    """반대편 - 매도를 넣으면서 매수를 깨지 않았는가."""
    assert ("entry_brk", level) in _kinds(line)


def test_sell_entry_draws_as_a_sell():
    """방향이 제일 중요하다. kind 를 새로 만들지 않은 이유가 이것이다."""
    od, rs, ax, uk = parse_peter_orders(
        "1062 돌파시 매도. 손절 1066\n9:16 AM · Sep 17, 2026\n", 0.0, "2026-09-17")
    assert len(od) == 1
    assert od[0]["side"] == "S", "매도 지시가 매수로 그려진다."
    assert od[0]["entry"] == 1062.0 and od[0]["stop"] == 1066.0


# ── (2) 줄 경계 누수 ────────────────────────────────────────────────────────

def test_levels_do_not_bleed_across_tweets():
    """실측 재현 - 두 트윗이 이어붙어 없는 목표를 만들었다."""
    bled = "1052 청산가\n1065 돌파시 다시 매도. 손절가 1068"
    got = _kinds(bled)
    assert ("target", 1065.0) not in got, (
        "<목표 1065> 는 그가 한 말이 아니다 - 줄 경계를 넘어 지어낸 값이다.")
    assert ("target", 1052.0) in got and ("entry_sell", 1065.0) in got


def test_each_line_is_still_parsed_whole():
    """대조군 - 경계를 막으면서 한 줄 안의 패턴까지 끊지는 않았는가."""
    got = _kinds("1081 청산가.\n1039 돌파시 매수 손절가 1036")
    assert ("target", 1081.0) in got
    assert ("entry_brk", 1039.0) in got and ("stop", 1036.0) in got


def test_0917_day_classification():
    """그날 전체 - 지시 4건(매수1 매도3)이 나와야 한다."""
    txt = ("코스피 시작후 1067 밑으로 떨어지면 올라올때 1067에서 매수. 손절가 1062. 그냥 날라가면 관망.\n"
           "8:55 AM · Sep 17, 2026\n\n"
           "1062 돌파시 매도. 손절 1066\n9:16 AM · Sep 17, 2026\n\n"
           "1065 돌파시 다시 매도. 손절가 1068\n10:10 AM · Sep 17, 2026\n\n"
           "1068 돌파시 재매도. 손절가 1072\n1:43 PM · Sep 17, 2026\n")
    od, rs, ax, uk = parse_peter_orders(txt, 0.0, "2026-09-17")
    assert len(od) == 4, [o["raw"][:20] for o in od]
    assert [o["side"] for o in od] == ["L", "S", "S", "S"]
