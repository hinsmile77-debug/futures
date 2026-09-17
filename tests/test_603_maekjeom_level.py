# -*- coding: utf-8 -*-
"""[MW0601 603차] 그가 <맥점>이라 쓴 줄이 통째로 빠져 있었다.

2026-09-01 ~ 09-11 백필을 넣어 보다가 드러났다. 그 열흘 중 매매가 있던 날은
09-11 하루뿐이고, 나머지 날 그가 공개한 것은 <맥점> 숫자 하나씩이 전부였다.
그런데 그 한 줄이 파서에 규칙이 없어 <미분류>로 빠져 **레벨선 0개**였다.
즉 9월 초 차트는 피터맥점 레이어가 통째로 비어 있었다.

두 어법이 있다.
    (a) 숫자가 붙어 있다   - <오늘 맥점은 1035>            (09-02 09:31)
    (b) 숫자가 떨어져 있다 - <맥점 잘못 봤네요. 수정합니다. 1057 기준.> (09-01 09:27)

(b) 를 <NNNN 기준> 으로 일반화하면 브리핑의 <기준: 2026년 9월 2일> 에서 연도를
레벨로 읽는다. 그래서 **같은 줄에 맥점이 있을 때만** 잡는다 - 이 제약이
유일한 방벽이다.

[!] <998 매수 맥점> (entry_dip) 은 숫자가 맥점 **앞**에 온다. 새 규칙은 맥점
  뒤만 보므로 부딪히지 않는다 - 이 경계가 깨지면 진입이 레벨공개로 바뀐다.

실행:
    $env:PYTHONIOENCODING="utf-8"
    ...\\py37_32\\python.exe -m pytest tests/test_603_maekjeom_level.py -v
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


# -- (1) 맥점에 숫자가 붙은 어법 - 전부 실측 원문이다 -----------------------

@pytest.mark.parametrize("line, level", [
    ("오늘 맥점은 1035. 여기 위에서 버티면", 1035.0),      # 09-02 09:31
    ("맥점 1057", 1057.0),
    ("오늘 맥점 : 1042", 1042.0),
])
def test_maekjeom_number_is_a_published_level(line, level):
    assert ("level_pub", level) in _kinds(line), (
        "<%s> 에서 맥점 레벨이 안 잡힌다 - 그날 유일한 숫자가 화면에서 사라진다."
        % line)


# -- (2) 숫자가 떨어진 어법 - 맥점이 같은 줄에 있을 때만 --------------------

def test_maekjeom_then_gijun():
    line = "맥점 잘못 봤네요. 수정합니다. 1057 기준. 1054-1060."   # 09-01 09:27
    assert ("level_pub", 1057.0) in _kinds(line)


def test_gijun_without_maekjeom_is_not_a_level():
    """브리핑의 <기준: 2026년 ...> 에서 연도를 레벨로 읽으면 안 된다."""
    line = "[피터리 - 발전주 브리핑] 기준: 2026년 9월 2일 미국시장 종가 및 최근 실적"
    assert [k for k in _kinds(line) if k[0] == "level_pub"] == [], (
        "맥점 없는 줄의 숫자를 레벨로 읽었다 - 연도가 레벨선이 된다.")


def test_far_away_number_is_not_taken():
    """맥점과 숫자가 40자 넘게 떨어지면 잡지 않는다 - 우연을 레벨로 만들지 않는다."""
    line = "맥점" + ("가" * 45) + " 1057 기준"
    assert [k for k in _kinds(line) if k[0] == "level_pub"] == []


# -- (3) 기존 맥점 어법을 깨지 않았는가 ------------------------------------

def test_buy_maekjeom_is_still_an_entry():
    """<998 매수 맥점> - 숫자가 앞에 온다. 진입이지 레벨공개가 아니다."""
    got = _kinds("998 매수 맥점. 993 이탈시 손절")
    assert ("entry_dip", 998.0) in got
    assert [k for k in got if k[0] == "level_pub"] == [], (
        "매수 맥점이 레벨공개로도 새어 나왔다.")


def test_dip_entry_near_maekjeom_is_still_an_entry():
    got = _kinds("1046 맥점 부근 오면 매수")
    assert ("entry_dip", 1046.0) in got
    assert [k for k in got if k[0] == "level_pub"] == []


# -- (4) 블록 분류 - 미분류가 아니라 예고(피터맥점)로 가는가 ---------------

def _aux_levels(raw):
    orders, results, aux, unknown = parse_peter_orders(raw, 0.0, "2026-09-02")
    return orders, aux, unknown


def test_maekjeom_block_becomes_aux_not_unknown():
    raw = "오늘 맥점은 1035. 여기 위에서 버티면 계속 수렴하는거고.\n9:31 AM \xb7 Sep 2, 2026"
    orders, aux, unknown = _aux_levels(raw)
    assert len(aux) == 1, "맥점 블록이 예고로 안 간다 - 피터맥점 레이어가 빈다."
    assert unknown == [], "맥점 블록이 아직 미분류에 남아 있다."
    assert orders == [], "맥점은 진입 지시가 아니다 - 깃발을 꽂으면 안 된다."
