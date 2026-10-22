# -*- coding: utf-8 -*-
"""[MW0601 708차] 신동 철회 섀도 — 「철회 시 본전 이상이면 청산 → 새 신호 수용」 계측.

고정하는 것
-----------
1. snapshot: 미실현 ≥ be_pts → EXIT, 미만 → HOLD. 가격·진입가 없으면 미측정(0 으로 채우지 않는다).
2. evaluate: 10/22 09:32 매도 철회 재현 — ALL 은 09:37 매수 재생을 받아 Δ 양수, BE(본전)는 청산 안 함 → Δ 0.
3. 철회 시각에 이미 청산된 포지션은 NOT_HELD — 섀도 대상이 아니다.
4. 탐지 허용(max_age)을 넘긴 재생 신호는 받지 않는다.
5. 로그 소급 파서가 철회 시각·가격을 읽는다.
6. 라이브 훅은 철회 분기에 배선되고 **주문을 내지 않는다**.

실행:
    conda run -n py37_32 python -m pytest tests/test_708b_shindong_retract_shadow.py -q
"""
import inspect
import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest  # noqa: E402

from strategy.shindong import retract_shadow as RS  # noqa: E402

D = "2026-10-22"


def test_snapshot_be_boundary():
    s = RS.snapshot(-1, 881.93, 881.93, 2, be_pts=0.0)
    assert s["measured"] and s["unreal_pts"] == 0.0 and s["decision"] == "EXIT"
    s = RS.snapshot(-1, 881.93, 882.30, 2, be_pts=0.0)
    assert s["unreal_pts"] == pytest.approx(-0.37) and s["decision"] == "HOLD"
    s = RS.snapshot(1, 875.42, 873.18, 2, be_pts=-3.0)
    assert s["decision"] == "EXIT"


def test_snapshot_unmeasured_is_not_zero():
    s = RS.snapshot(-1, 881.93, None, 2)
    assert s["measured"] is False and s["unreal_pts"] is None and s["decision"] is None


def _pos(entry_ts, exit_ts, side, px, net, qty=2):
    return dict(entry_ts=entry_ts, exit_ts=exit_ts, direction="LONG" if side > 0 else "SHORT", side=side,
                qty=qty, entry_px=px, net=net, legs=[(exit_ts[11:16], 0.0, "하드스톱")])


_POS = [_pos(D + " 09:33:05", D + " 09:41:20", -1, 881.93, -384_351.0),
        _pos(D + " 09:52:05", D + " 10:07:27", -1, 888.29, 273_624.0)]
_EV = [{"kind": "ENTER", "trade_key": "R3|09:32|-1", "side": -1, "entered_at": D + "T09:33:05"},
       {"kind": "RETRACTED", "trade_key": "R3|09:32|-1", "ts": D + "T09:38:05"}]
_REPLAY = [{"key": "R3|09:37|+1", "entry_ts": "09:37", "exit_ts": "09:47", "net": 950_593.0},
           {"key": "R3|09:51|-1", "entry_ts": "09:51", "exit_ts": "10:07", "net": 284_595.0}]
_COST = {(D + " 09:33:05", "SHORT"): 3_351.0}


def _eval(price=882.30, src="log", be=0.0, replay=_REPLAY, ev=_EV):
    ev = list(ev)
    logp = {}
    if src == "log":
        logp = {"R3|09:32|-1": {"ts": D + " 09:38:05", "price": price}}
    else:
        ev.append(dict(RS.snapshot(-1, 881.93, price, 2, be), kind="RETRACT_SHADOW", trade_key="R3|09:32|-1"))
    return RS.evaluate(D, replay, _POS, ev, logp=logp, costs=_COST, max_age_min=2, be_pts=be)


def test_1022_case_all_takes_missed_signal_be_holds():
    rs = _eval()
    it = rs["items"][0]
    assert it["status"] == "OK" and it["decision"] == "HOLD"
    assert [k for k, _ in it["taken"]] == ["R3|09:37|+1"]          # 09:51 은 창(~09:47) 밖
    exit_net = (-0.37 - RS.EXIT_SLIP_PTS) * 2 * 50_000 - 3_351.0
    assert it["delta_all"] == pytest.approx(exit_net + 950_593.0 - (-384_351.0))
    assert it["delta_be"] == 0.0 and rs["n_be_exit"] == 0


def test_live_snapshot_wins_over_log_and_be_exit_counts():
    rs = _eval(price=881.50, src="live")                           # 매도 진입 881.93 → +0.43pt
    it = rs["items"][0]
    assert it["src"] == "live" and it["decision"] == "EXIT"
    assert it["delta_be"] == pytest.approx(it["delta_all"]) and rs["n_be_exit"] == 1


def test_retract_after_exit_is_not_held():
    ev = [_EV[0], {"kind": "RETRACTED", "trade_key": "R3|09:32|-1", "ts": D + "T09:42:05"}]
    rs = RS.evaluate(D, _REPLAY, _POS, ev, logp={"R3|09:32|-1": {"ts": D + " 09:42:05", "price": 882.3}})
    assert rs["items"][0]["status"] == "NOT_HELD" and rs["n"] == 0


def test_stale_signal_is_not_taken():
    replay = [{"key": "R3|09:33|+1", "entry_ts": "09:33", "exit_ts": "09:40", "net": 999_999.0}]
    it = _eval(replay=replay)["items"][0]
    assert it["taken"] == []                                       # 09:34 + 2분 < 09:38:05


def test_no_price_is_unmeasured():
    rs = RS.evaluate(D, _REPLAY, _POS, _EV)
    assert rs["items"][0]["status"] == "UNMEASURED" and rs["n_unmeasured"] == 1


def test_positions_none_is_unmeasured_not_empty():
    assert RS.evaluate(D, _REPLAY, None, _EV) is None
    assert "미측정" in RS.section(None)[0]


def test_log_prices_parser(tmp_path):
    line = ("2026-10-22 09:38:05 [INFO] SYSTEM: [Shindong] R3 매도 RETRACTED 진입 881.26(09:32) | 철회 전 상태 OPEN"
            " · 현재가 882.30 · 기준분 09:37 | 원천 흐름 재수신으로 신호 소멸 — 채점 표본 제외\n")
    with io.open(str(tmp_path / "20261022_SYSTEM.log"), "w", encoding="utf-8") as f:
        f.write(line)
    assert RS.log_prices(D, str(tmp_path)) == {"R3|09:32|-1": {"ts": D + " 09:38:05", "price": 882.30}}


def test_live_hook_is_wired_and_sends_no_order():
    src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    # 가상 장부(_shindong_virtual_apply)에도 같은 분기가 있다 — 실집행 쪽만 본다
    i = src.index('if kind == "retracted":', src.index("def _shindong_apply("))
    branch = src[i:src.index("return", i)]
    assert "self._shindong_retract_shadow(rec, day, price)" in branch
    j = src.index("def _shindong_retract_shadow(")
    body = src[j:src.index("\n    def ", j + 10)]
    for banned in ("_send_broker_exit_order", "_set_pending_order", "set_external_levels", "_sd_exec_save"):
        assert banned not in body, banned
    assert '"RETRACT_SHADOW"' in body


def test_daily_report_has_section():
    from strategy.shindong import daily_report as DR
    assert "2-2. 철회 섀도" in inspect.getsource(DR.build)
