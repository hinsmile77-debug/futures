# -*- coding: utf-8 -*-
"""[MW0602 / v9-dev 702차 F-10 이식] 하드스톱 분할체결이 `tp1_reached` 를 오염시키지 않는다.

## 사고 (dev 실측 2026-10-13 · 10-21)

2계약 하드스톱이 거래소에서 1+1 로 분할 체결되면 첫 체결이 `apply_exit_fill()` 비최종
분기에서 `_sync_partial_progress()` 를 타고, 누적 청산수량(1) ≥ TP1 목표(1)라
`partial_1_done=True` 가 섰다. 결과 dict 가 그 플래그를 `tp1_reached=1` 로 읽어
`classify_exit()` 이 최종 레그를 `보호트레일`(이익 보호)로 기록했다 — 실제로는 최초 손절이다.
dev 로그 실측 6포지션(10-13 4 · 10-21 2), 전부 `[Position] 체결부분청산 … 하드스톱` 뒤
`[TP1보호]` 이고 그 사이 TP1 사건이 없다.

## 수정 방식 — 매매 경로 무변경

`partial_1_done` 은 TP1 재발동 가드(`is_tp1_hit`)이므로 **그대로 둔다**(ⓓ가 고정).
라벨 전용 축 `tp1_protect_armed` 를 분리해, 사유가 TP 계열일 때만 True 가 된다.
원 수정: v9-dev `7a4f6387` (dev 에는 `exit_stage` 가 없어 `tp1_reached`/`exit_trigger` 축으로 단언).
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
    return PositionTracker()


def _open(pt, direction="LONG", price=900.0, qty=2):
    pt.open_position(direction=direction, price=price, quantity=qty, atr=1.0)


def _axes(r):
    return r["tp1_reached"], r["exit_trigger"]


# ⓐ 사고 재현 — 분할 하드스톱 최종 레그는 tp1_reached=0 / 하드스톱
@pytest.mark.parametrize("qty,legs", [(2, [1, 1]), (4, [1, 2, 1]), (3, [1, 1, 1])])
def test_분할_하드스톱_최종레그는_하드스톱(pt, qty, legs):
    _open(pt, qty=qty)
    stop = pt.stop_price
    results = [pt.apply_exit_fill(exit_price=stop, quantity=q, reason="하드스톱(틱)")
               for q in legs]
    assert [_axes(r) for r in results] == [(0, "하드스톱")] * len(legs)


# ⓑ TP1 을 실제로 거친 포지션은 보호트레일 보존
def test_TP1_경유_후_스톱은_보호트레일(pt):
    _open(pt, qty=2)
    r1 = pt.apply_exit_fill(exit_price=pt.tp1_price, quantity=1, reason="TP1 부분청산 33%")
    r2 = pt.apply_exit_fill(exit_price=pt.entry_price, quantity=1, reason="하드스톱(틱)")
    assert r1["exit_trigger"] == "TP1"
    assert _axes(r2) == (1, "보호트레일")


def test_1계약_TP1_보호전환_후_스톱은_보호트레일(pt):
    _open(pt, qty=1)
    pt.arm_tp1_single_contract_with_mode(pt.tp1_price, 1.0, mode="breakeven")
    r = pt.apply_exit_fill(exit_price=pt.entry_price, quantity=1, reason="하드스톱(틱)")
    assert _axes(r) == (1, "보호트레일")


def test_손절1차_후_잔여1계약_보호전환은_보호트레일(pt):
    """dev 08-18 10:15 경로 — 손절1차 조기축소 뒤 잔여 1계약이 실제로 TP1 보호전환을 거쳤다.
    메모 4절 쿼리가 이것을 후보로 잡지만 **정상 라벨**이다(뒤집히면 안 된다)."""
    _open(pt, direction="SHORT", price=1132.35, qty=2)
    r0 = pt.apply_exit_fill(exit_price=pt.entry_price + 1.37, quantity=1,
                            reason="손절1차 조기축소", shrink_initial=True)
    assert r0["exit_trigger"] == "손절1차"
    pt.arm_tp1_single_contract_with_mode(pt.tp1_price, 1.0, mode="atr_profit")
    r = pt.apply_exit_fill(exit_price=pt.entry_price - 0.37, quantity=1, reason="하드스톱(틱)")
    assert _axes(r) == (1, "보호트레일")


def test_손절1차_비축소_후_스톱은_하드스톱(pt):
    """shrink 없이 손절 사유로 진행률이 차도 TP1 보호로 승격하지 않는다."""
    _open(pt, qty=2)
    pt.apply_exit_fill(exit_price=pt.stop_price, quantity=1, reason="손절1차 조기축소")
    r = pt.apply_exit_fill(exit_price=pt.stop_price, quantity=1, reason="하드스톱(틱)")
    assert _axes(r) == (0, "하드스톱")


def test_partial_close_경로도_같은_규약(pt, tmp_path, monkeypatch):
    _open(pt, qty=2)
    pt.partial_close(pt.tp1_price, 1, "TP1 partial")
    assert pt.tp1_protect_armed is True
    pt2 = PositionTracker()
    _open(pt2, qty=2)
    pt2.partial_close(pt2.stop_price, 1, "하드스톱(틱)")
    assert pt2.tp1_protect_armed is False and pt2.partial_1_done is True


# ⓒ 2026-10-21 dev 신동 실측 픽스처(09:35 · 11:06) — 2계약 1+1 손절이 뒤집힌다
@pytest.mark.parametrize("entry,stop_px", [(888.51, 893.69), (900.27, 902.36)])
def test_1021_신동_분할손절_뒤집힘(pt, entry, stop_px):
    _open(pt, price=entry, qty=2)
    pt.apply_exit_fill(exit_price=stop_px, quantity=1, reason="하드스톱(틱)")
    r = pt.apply_exit_fill(exit_price=stop_px, quantity=1, reason="하드스톱(틱)")
    assert _axes(r) == (0, "하드스톱")       # 종전 (1, 보호트레일)


def test_대조군_단일체결(pt):
    _open(pt, qty=2)
    r = pt.apply_exit_fill(exit_price=pt.stop_price, quantity=2, reason="하드스톱(틱)")
    assert _axes(r) == (0, "하드스톱")


# ⓓ 매매 경로 무변경 — partial_1_done 은 종전처럼 서고 TP1 재발동이 없다
def test_재발동_가드_무변경(pt):
    _open(pt, qty=2)
    pt.apply_exit_fill(exit_price=pt.stop_price, quantity=1, reason="하드스톱(틱)")
    assert pt.partial_1_done is True            # 종전과 동일
    assert pt.is_tp1_hit(pt.tp1_price + 5.0) is False
    assert pt.tp1_protect_armed is False


# ⓔ 계측 4원칙 ② — 사유 미상 진행률 승격은 tp1_reached=None → 하드스톱?
def test_사유미상_진행률_승격은_미상(pt):
    _open(pt, qty=2)
    pt.quantity = 1                              # 브로커 동기화처럼 사유 없이 감소
    pt._sync_partial_progress()
    assert pt.tp1_protect_armed is None
    r = pt.apply_exit_fill(exit_price=pt.stop_price, quantity=1, reason="하드스톱(틱)")
    assert _axes(r) == (None, "하드스톱?")


# ⓕ 상태파일 왕복
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
