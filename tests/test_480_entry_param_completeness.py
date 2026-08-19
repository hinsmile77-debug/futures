# -*- coding: utf-8 -*-
"""[MW0601 480차 / F-5①·② · G-3 선행] 진입 위험 파라미터 완전성 회귀 고정.

## 무엇을 지키는가

2026-08-19 09:49:01, Chejan 체결 콜백이 `BlockRequest()`가 COM 이벤트를 pump하는
동안 **먼저** 도착해 `apply_entry_fill()`이 포지션을 열었고, 뒤늦게 도착한
`open_position()`은 *"이미 포지션 보유 중"* 으로 실패했다. 그 결과 위험 파라미터
5종이 조용히 기본값으로 갔다:

    entry_horizon = None  →  TP1 배수 1.0  (3m 설계값 0.5의 **정확히 2배**)
    hurst_bucket  = None  →  레짐 조건부 배수 미적용
    extra_stop_mult = 1.0 →  급변장 스톱확대 미적용
    checklist_pass_count = None → 사후 분석 표본에서 탈락
    trades.entry_horizon = '' → 호라이즌별 성과 집계에서 이 포지션이 통째로 빠진다

**아무 로그도 남지 않았다.** 장후에 실현가를 역산(1018.3667 → 1020.5 = ×0.958)해서야
드러났다 — 계측 4원칙 ④(폴백 가시화)가 정확히 금지하는 형태다.

희귀 사고가 아니다: `trades` 실측 2026-07-14~08-19 기준 `entry_horizon` 공란이
**5레그 / 3포지션**(SYSTEM_AUTO만 4레그)이다. 대략 9거래일에 한 번, 그 포지션은
설계의 2배로 벌어진 TP1/손절 기하로 집행된다.

이 테스트가 고정하는 불변식은 셋이다:

  ① 레이스 경로(`pending` 승계)로 열려도 TP1 배수가 호라이즌 설계값일 것
  ② pending을 쓰는 모든 `apply_entry_fill` 호출부가 위험 파라미터를 넘길 것 (AST)
  ③ 그래도 파라미터가 비면 **경고가 남을 것** (조용한 폴백 금지)
"""
import ast
import datetime
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.settings import (  # noqa: E402
    ATR_HORIZON_TP1_MULT, ATR_TP1_MULT,
)
from strategy.position.position_tracker import PositionTracker  # noqa: E402

ATR = 2.0
PRICE = 1000.0


def _flat_tracker(tmp_path=None):
    """운영 상태파일을 건드리지 않는 트래커 (test_entry_qty_invariant.py 관례)."""
    import strategy.position.position_tracker as pt_mod
    import tempfile
    pt_mod._STATE_FILE = os.path.join(tempfile.mkdtemp(), "position_state.json")
    return PositionTracker()


# ── ① 레이스 경로도 호라이즌 설계값을 쓴다 ────────────────────────────────

@pytest.mark.parametrize("hz,expect", [("1m", 0.3), ("3m", 0.5), ("5m", 0.7)])
def test_레이스_경로_TP1_배수가_호라이즌_설계값이다(hz, expect):
    p = _flat_tracker()
    p.apply_entry_fill(
        direction="LONG", price=PRICE, quantity=1, atr=ATR,
        grade="A", regime="NEUTRAL", filled_at=datetime.datetime.now(),
        raw_direction="LONG", reverse_entry_enabled=False,
        entry_horizon=hz,
    )
    assert p.entry_horizon == hz
    assert p.tp1_price == pytest.approx(PRICE + ATR * expect)


def test_호라이즌이_없으면_2배로_벌어진다_이것이_08_19_사고다():
    """회귀 방지용 반례 고정 — 이 값이 '정상'으로 보이면 안 된다."""
    p = _flat_tracker()
    p.apply_entry_fill(
        direction="LONG", price=PRICE, quantity=1, atr=ATR,
        grade="A", regime="NEUTRAL", filled_at=datetime.datetime.now(),
        raw_direction="LONG",
    )
    assert p.tp1_price == pytest.approx(PRICE + ATR * ATR_TP1_MULT)
    assert ATR_TP1_MULT == pytest.approx(ATR_HORIZON_TP1_MULT["3m"] * 2)


def test_레이스_경로가_나머지_파라미터도_받는다():
    p = _flat_tracker()
    p.apply_entry_fill(
        direction="SHORT", price=PRICE, quantity=2, atr=ATR,
        grade="B", regime="NEUTRAL", filled_at=datetime.datetime.now(),
        raw_direction="SHORT", entry_horizon="3m",
        hurst_bucket="trend", extra_stop_mult=1.4, checklist_pass_count=8,
    )
    assert p.entry_hurst_bucket == "trend"
    assert p.entry_extra_stop_mult == pytest.approx(1.4)
    assert p.checklist_pass_count == 8


def test_증액_경로는_진입_시점_파라미터를_덮어쓰지_않는다():
    """포지션 중간에 손절폭이 바뀌면 리스크 관리가 무너진다 — None 기본값의 의미."""
    p = _flat_tracker()
    now = datetime.datetime.now()
    p.apply_entry_fill(direction="LONG", price=PRICE, quantity=1, atr=ATR,
                       grade="A", regime="NEUTRAL", filled_at=now,
                       raw_direction="LONG", entry_horizon="1m",
                       hurst_bucket="trend", extra_stop_mult=1.4)
    p.apply_entry_fill(direction="LONG", price=PRICE + 1, quantity=1, atr=ATR,
                       grade="A", regime="NEUTRAL", filled_at=now,
                       raw_direction="LONG")     # 증액 — 파라미터 미전달
    assert p.entry_hurst_bucket == "trend"
    assert p.entry_extra_stop_mult == pytest.approx(1.4)


# ── ② 배선 (AST) ──────────────────────────────────────────────────────────

def _calls(src, name):
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr == name:
                out.append({k.arg for k in node.keywords if k.arg})
    return out


def test_pending을_쓰는_모든_체결진입_호출부가_위험_파라미터를_넘긴다():
    """`raw_direction=`을 넘긴다 = pending(자동 진입 주문)을 아는 호출부다.

    외부 유입 체결(GHOST_PENDING_MISS) 경로는 pending이 없어 호라이즌을 알 수 없으므로
    대상이 아니다 — 그쪽까지 강제하면 알 수 없는 값을 지어내게 된다.
    """
    with open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        src = f.read()
    pending_calls = [kw for kw in _calls(src, "apply_entry_fill") if "raw_direction" in kw]
    assert len(pending_calls) >= 2, "레이스 경로/범용 경로 두 호출부를 못 찾았다"
    for kw in pending_calls:
        for need in ("entry_horizon", "hurst_bucket", "extra_stop_mult",
                     "checklist_pass_count"):
            assert need in kw, "apply_entry_fill 호출부에 %s 누락 (F-5 회귀)" % need


def test_낙관적_오픈_호출부는_5종을_전부_넘긴다():
    with open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        src = f.read()
    opens = [kw for kw in _calls(src, "open_position") if kw]
    assert opens, "open_position 키워드 호출부를 못 찾았다"
    best = max(opens, key=len)
    for need in ("entry_horizon", "hurst_bucket", "extra_stop_mult",
                 "checklist_pass_count"):
        assert need in best


def test_pending에_위험_파라미터가_실린다():
    """승계원이 비면 승계 코드가 있어도 값이 None으로 흐른다."""
    with open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        src = f.read()
    for key in ("hurst_bucket", "extra_stop_mult", "checklist_pass_count",
                "entry_horizon"):
        assert '_pending_order["%s"]' % key in src, "pending에 %s 미적재" % key


# ── ③ 조용한 폴백 금지 ────────────────────────────────────────────────────

def test_호라이즌_없이_열리면_경고가_남는다(caplog):
    p = _flat_tracker()
    with caplog.at_level("WARNING", logger="TRADE"):
        p.apply_entry_fill(
            direction="LONG", price=PRICE, quantity=1, atr=ATR,
            grade="A", regime="NEUTRAL", filled_at=datetime.datetime.now(),
            raw_direction="LONG",
        )
    assert any("PositionFallback" in r.message or "PositionFallback" in r.getMessage()
               for r in caplog.records), "TP1 폴백이 조용히 적용됐다 (계측 4원칙 ④)"


def test_경고는_포지션당_1회다():
    """재계산은 체결보정·브로커동기화마다 일어난다 — 매번 찍으면 로그가 잠긴다."""
    p = _flat_tracker()
    p.apply_entry_fill(direction="LONG", price=PRICE, quantity=1, atr=ATR,
                       grade="A", regime="NEUTRAL",
                       filled_at=datetime.datetime.now(), raw_direction="LONG")
    key_before = p._tp1_fallback_warned_for
    p._recalculate_levels(ATR)
    p._recalculate_levels(ATR)
    assert p._tp1_fallback_warned_for == key_before
