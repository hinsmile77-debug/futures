# -*- coding: utf-8 -*-
"""[MW0601 702차 / F-10] 하드스톱 분할체결이 `exit_stage` 를 `TRAIL_AFTER_TP1` 로 오염시키지 않는다.

## 사고 (2026-08-31 이상점 1-19 · 10-21 신동 6레그 재현)

2계약 하드스톱이 거래소에서 1+1 로 분할 체결되면 첫 체결이 `apply_exit_fill()` 비최종
분기에서 `_sync_partial_progress()` 를 타고, 누적 청산수량(1) ≥ TP1 목표(1)라
`partial_1_done=True` 가 섰다. 라벨러가 그 플래그를 「TP1 보호 발동」으로 읽어 최종
레그가 `TRAIL_AFTER_TP1`(=이익 보호 트레일)로 기록됐다 — 실제로는 최초 손절이다.

## 수정 방식 — 매매 경로 무변경

`partial_1_done` 은 TP1 재발동 가드(`is_tp1_hit`)이므로 **그대로 둔다**(ⓓ가 고정).
라벨 전용 축 `tp1_protect_armed` 를 분리해, 사유가 TP 계열일 때만 True 가 된다.
"""
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from strategy.position.position_tracker import PositionTracker  # noqa: E402


@pytest.fixture
def pt(tmp_path, monkeypatch):
    import strategy.position.position_tracker as m
    monkeypatch.setattr(m, "_STATE_FILE", str(tmp_path / "pos.json"))
    return PositionTracker(pt_value=50_000)


def _open(pt, direction="LONG", price=900.0, qty=2):
    pt.open_position(direction=direction, price=price, quantity=qty, atr=1.0)


# ⓐ 사고 재현 — 분할 하드스톱 최종 레그는 INITIAL_STOP
@pytest.mark.parametrize("qty,legs", [(2, [1, 1]), (4, [1, 2, 1]), (3, [1, 1, 1])])
def test_분할_하드스톱_최종레그는_INITIAL_STOP(pt, qty, legs):
    _open(pt, qty=qty)
    stop = pt.stop_price
    results = [pt.apply_exit_fill(exit_price=stop, quantity=q, reason="하드스톱(틱)")
               for q in legs]
    assert [r["exit_stage"] for r in results] == ["INITIAL_STOP"] * len(legs)


# ⓑ TP1 을 실제로 거친 포지션은 TRAIL_AFTER_TP1 보존
def test_TP1_경유_후_스톱은_TRAIL_AFTER_TP1(pt):
    _open(pt, qty=2)
    r1 = pt.apply_exit_fill(exit_price=pt.tp1_price, quantity=1, reason="TP1 부분청산 50%")
    r2 = pt.apply_exit_fill(exit_price=pt.entry_price, quantity=1, reason="하드스톱(틱)")
    assert (r1["exit_stage"], r2["exit_stage"]) == ("TP1", "TRAIL_AFTER_TP1")


def test_1계약_TP1_보호전환_후_스톱은_TRAIL_AFTER_TP1(pt):
    _open(pt, qty=1)
    pt.arm_tp1_single_contract_with_mode(pt.tp1_price, 1.0, mode="breakeven")
    r = pt.apply_exit_fill(exit_price=pt.entry_price, quantity=1, reason="하드스톱(틱)")
    assert r["exit_stage"] == "TRAIL_AFTER_TP1"


def test_partial_close_경로도_같은_규약(pt):
    _open(pt, qty=2)
    pt.partial_close(pt.tp1_price, 1, "TP1 partial")
    assert pt.tp1_protect_armed is True
    pt2 = PositionTracker(pt_value=50_000)
    _open(pt2, qty=2)
    pt2.partial_close(pt2.stop_price, 1, "하드스톱(틱)")
    assert pt2.tp1_protect_armed is False and pt2.partial_1_done is True


# ⓒ 2026-10-21 신동 실측 픽스처 — 2계약 1+1 손절 4건이 뒤집힌다(대조군 단일체결은 무변화)
@pytest.mark.parametrize("stop_px", [899.86, 896.08, 891.50, 882.50])
def test_1021_신동_분할손절_뒤집힘(pt, stop_px):
    _open(pt, price=stop_px + 2.0, qty=2)
    pt.apply_exit_fill(exit_price=stop_px, quantity=1, reason="하드스톱(틱)")
    r = pt.apply_exit_fill(exit_price=stop_px, quantity=1, reason="하드스톱(틱)")
    assert r["exit_stage"] == "INITIAL_STOP"     # 종전 TRAIL_AFTER_TP1


def test_1021_대조군_단일체결(pt):
    _open(pt, qty=2)
    r = pt.apply_exit_fill(exit_price=pt.stop_price, quantity=2, reason="하드스톱(틱)")
    assert r["exit_stage"] == "INITIAL_STOP"


# ⓓ 매매 경로 무변경 — partial_1_done 은 종전처럼 서고 TP1 재발동이 없다
def test_재발동_가드_무변경(pt):
    _open(pt, qty=2)
    pt.apply_exit_fill(exit_price=pt.stop_price, quantity=1, reason="하드스톱(틱)")
    assert pt.partial_1_done is True            # 종전과 동일
    assert pt.is_tp1_hit(pt.tp1_price + 5.0) is False
    assert pt.tp1_protect_armed is False


# 계측 4원칙 ② — 사유 미상·구버전 상태는 STOP_UNKNOWN
def test_사유미상_진행률_승격은_STOP_UNKNOWN(pt):
    _open(pt, qty=2)
    pt.quantity = 1                              # 브로커 동기화처럼 사유 없이 감소
    pt._sync_partial_progress()
    assert pt.tp1_protect_armed is None
    r = pt.apply_exit_fill(exit_price=pt.stop_price, quantity=1, reason="하드스톱(틱)")
    assert r["exit_stage"] == "STOP_UNKNOWN"


def test_상태파일_왕복_보존(pt, tmp_path):
    _open(pt, qty=2)
    pt.apply_exit_fill(exit_price=pt.stop_price, quantity=1, reason="하드스톱(틱)")
    st = json.load(open(str(tmp_path / "pos.json"), encoding="utf-8"))
    assert st["tp1_protect_armed"] is False and st["partial_1_done"] is True


def test_리셋_후_새_포지션은_False(pt):
    _open(pt, qty=1)
    pt.arm_tp1_single_contract_with_mode(pt.tp1_price, 1.0, mode="breakeven")
    pt.apply_exit_fill(exit_price=pt.entry_price, quantity=1, reason="하드스톱(틱)")
    _open(pt, qty=2)
    assert pt.tp1_protect_armed is False
