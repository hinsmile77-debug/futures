# -*- coding: utf-8 -*-
"""[MW0601 725차 후속6] 신동2 poll 라우팅 — 무보유 position 헛호출 · 같은 이벤트 재발화 회귀 고정.

2026-10-28 13:50 — AI 거래 0 · 대기 없음인데 피터 관점 2건으로 `/shindong2 position` 호출(rc 10).
          14:00 — snapshot 은 「새 이벤트 0건」인데 기준점(마지막 재량 기록 13:32)이 그대로라 같은 2건으로 또 호출.
7거래일(10-20–10-28) poll→Claude 24회 중 6회가 무보유·비재량 이벤트였다.
"""
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import shindong2_live as M  # noqa: E402

DAY = "2026-10-28"
_NO_AI = dict(trades=[], pending=None, pnl=0)


def _ev(key, kind, at):
    return dict(key=key, t=at[11:16], kind=kind, text=key, detected_at=at)


@pytest.fixture()
def live(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "LIVE_DIR", str(tmp_path / "live"))
    d = M.day_dir(DAY)

    def put(events, records):
        with open(os.path.join(d, "events.jsonl"), "w", encoding="utf-8") as f:
            for e in events:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        with open(os.path.join(d, "ai_log.jsonl"), "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return put


def test_1028_peter_views_without_holding_defer_then_no_refire(live):
    live([_ev("pview:1", "피터 관점", "2026-10-28T13:50:06"), _ev("pview:2", "피터 관점", "2026-10-28T13:50:06")],
         [dict(ts="2026-10-28T13:32:47")])
    base, fresh = M.events_since_record(DAY)
    rc, _ = M.poll_route(fresh, _NO_AI)
    assert len(fresh) == 2 and rc == M.POLL_DEFER          # 종전 10 (position 헛호출)
    M.poll_stage(DAY, fresh)
    assert M.poll_ack(DAY) == "2026-10-28T13:50:06"
    _, fresh2 = M.events_since_record(DAY)                 # 14:00 — 같은 2건으로 다시 깨우지 않는다
    assert fresh2 == [] and M.poll_route(fresh2, _NO_AI)[0] == 0


def test_carry_ignores_ack_so_next_intraday_still_sees_deferred(live):
    live([_ev("pview:1", "피터 관점", "2026-10-28T13:50:06"), _ev("p:entry:09:42", "진입", "2026-10-28T13:50:06")],
         [dict(ts="2026-10-28T13:32:47")])
    _, fresh = M.events_since_record(DAY)
    M.poll_stage(DAY, fresh)
    M.poll_ack(DAY)
    _, carry = M.events_since_record(DAY, use_ack=False)
    assert {e["key"] for e in carry} == {"pview:1", "p:entry:09:42"}   # 사료 제외는 snapshot(cmd_snapshot)에서


def test_pending_or_open_position_still_calls_position():
    ev = [_ev("p:exit:09:42", "청산", "2026-10-23T10:20:07")]   # 10-23 10:20 — 대기 계획 + 사료 청산 (정당 호출 보존)
    pend = dict(trades=[], pending=dict(sgn=-1, entry=850.6, stop=853.2, target=844.0), pnl=0)
    assert M.poll_route(ev, pend)[0] == M.POLL_POSITION
    hold = dict(trades=[dict(entry_t="10:00", open=True, pnl=1.0)], pending=None, pnl=0)
    assert M.poll_route([_ev("box:09:30:break", "상자 이탈", "2026-10-27T10:20:07")], hold)[0] == M.POLL_POSITION


def test_ai_fill_event_calls_position_even_if_closed_already():
    closed = dict(trades=[dict(entry_t="10:00", exit_t="10:05", pnl=1.0)], pending=None, pnl=1.0)
    assert M.poll_route([_ev("ai:exit:10:00", "재량 청산", "2026-10-20T10:50:07")], closed)[0] == M.POLL_POSITION


def test_relic_only_events_do_not_wake_claude():
    ev = [_ev("p:entry:13:10", "진입", "2026-10-21T13:20:08"), _ev("base:13:15", "기본 제안", "2026-10-21T13:20:08")]
    rc, why = M.poll_route(ev, dict(trades=[dict(entry_t="10:00", exit_t="10:30", pnl=0.7)], pending=None, pnl=0.7))
    assert rc == M.POLL_DEFER and "사료" in why          # 10-21 13:20·13:50·14:20 헛호출


def test_ack_without_stage_is_noop_and_failure_keeps_events(live):
    live([_ev("pview:1", "피터 관점", "2026-10-28T13:50:06")], [dict(ts="2026-10-28T13:32:47")])
    assert M.poll_ack(DAY) == ""                         # 후보 없음 — 기준점 불변
    _, fresh = M.events_since_record(DAY)
    M.poll_stage(DAY, fresh)                             # Claude 실패 → runner 가 ack 안 함
    assert len(M.events_since_record(DAY)[1]) == 1      # 다음 poll 이 다시 시도


def test_runner_wires_defer_and_ack():
    with open(os.path.join(_ROOT, "scripts", "shindong2_run.ps1"), "rb") as f:
        s = f.read().decode("ascii")
    assert "if ($p -eq 11)" in s and s.count("Run-Live @('poll-ack')") == 2
    assert "$Phase -eq 'poll' -and $rc -eq 0" in s       # position 성공 뒤에만 ack
    assert "if (-not $DryRun) { $null = Run-Live @('poll-ack') }" in s


# ── [725차 후속7] 상대(MAIN) 진입·청산 이벤트 ─────────────────────────────────
def _rv(*trades):
    return dict(present=True, main=dict(trades=list(trades)))


def _mt(status="CLOSED", exit_t="10:11", net=5.37, stop_now=None):
    return dict(rule="R3", side=1, side_ko="매수", entry_t="09:46", entry_px=919.86, stop_init=916.16, stop_now=stop_now,
                status=status, exit_t=exit_t, reason_ko="1차/트레일" if exit_t else None,
                net_pt=net if status == "CLOSED" else None, key="R3|09:46|+1")


def test_main_trade_becomes_entry_and_exit_events_keyed_once():
    ev = M.main_events(_rv(_mt()))                       # 2026-10-28 MAIN R3 09:46 → 10:11 +5.37 (종전엔 이벤트 0건)
    assert [(e["kind"], e["key"]) for e in ev] == [("상대 진입", "main:entry:R3|09:46|+1"), ("상대 청산", "main:exit:R3|09:46|+1")]
    assert "@919.86" in ev[0]["text"] and "+5.37pt" in ev[1]["text"]


def test_main_open_with_first_leg_out_is_partial_and_open_has_entry_only():
    part = M.main_events(_rv(_mt(status="OPEN", exit_t="09:49", stop_now=920.56)))
    assert [e["kind"] for e in part] == ["상대 진입", "상대 1차 청산"] and "920.56" in part[1]["text"]
    assert [e["kind"] for e in M.main_events(_rv(_mt(status="OPEN", exit_t=None)))] == ["상대 진입"]


def test_main_unmeasured_gives_no_events_and_net_none_is_not_zero():
    assert M.main_events(None) == [] and M.main_events(dict(present=False, why="x")) == []
    ev = M.main_events(_rv(_mt(net=None)))
    assert "손익 미측정" in ev[1]["text"]                 # 계측 4원칙 ② — 미측정 ≠ 0


def test_main_events_route_position_when_engaged_else_defer():
    ev = M.main_events(_rv(_mt()))
    hold = dict(trades=[dict(entry_t="09:50", open=True, pnl=1.0)], pending=None, pnl=0)
    assert M.poll_route(ev, hold)[0] == M.POLL_POSITION
    rc, why = M.poll_route(ev, _NO_AI)
    assert rc == M.POLL_DEFER and "MAIN" in why


def test_main_events_from_real_shindong_db_1028():
    import shindong2_rival as RV
    if not os.path.exists(RV.SD_DB):
        pytest.skip("shindong.db 없음(다른 PC)")
    rv = RV.read_day("2026-10-28")
    if not rv.get("present"):
        pytest.skip("10-28 MAIN 행 없음")
    keys = [e["key"] for e in M.main_events(rv)]
    assert "main:entry:R3|09:46|+1" in keys and "main:exit:R3|09:46|+1" in keys


# ── [725차 후속8] 장중 슬롯 양보 — poll 이 intraday 와 같은 초에 시작해 잠금을 먼저 잡던 문제 ─────────
def _ps_text(name):
    with open(os.path.join(_ROOT, "scripts", name), "rb") as f:
        return f.read().decode("ascii")


def _yield_minutes():
    import re
    s = _ps_text("shindong2_run.ps1")
    m = re.search(r"\$slotFirst = (\d+) \* 60 \+ (\d+); \$slotStep = (\d+); \$slotLast = (\d+) \* 60 \+ (\d+)", s)
    assert m, "슬롯 상수 줄을 찾지 못했다"
    first, step, last = int(m[1]) * 60 + int(m[2]), int(m[3]), int(m[4]) * 60 + int(m[5])
    # runner 판정식 그대로: first ≤ t ≤ last+1 그리고 (t−first) % step ≤ 1
    return {t for t in range(24 * 60) if first <= t <= last + 1 and (t - first) % step <= 1}


def test_poll_yield_slots_match_scheduled_intraday_trigger():
    import re
    m = re.search(r"New-WeekdayRepeat '(\d\d):(\d\d)' (\d+) (\d+)\)\) \}", _ps_text("shindong2_tasks.ps1"))
    assert m, "Intraday 30분 트리거를 찾지 못했다"
    start, every, dur = int(m[1]) * 60 + int(m[2]), int(m[3]), int(m[4])
    slots = {start + k * every for k in range(dur // every + 1) if k * every < dur}
    assert sorted(slots)[0] == 10 * 60 + 30 and sorted(slots)[-1] == 14 * 60 + 30 and len(slots) == 9
    assert _yield_minutes() == slots | {t + 1 for t in slots}      # 시작 지연 +1분까지만 — 그 밖(:10·:20·:40·:50)은 poll 정상


def test_poll_yield_examples_and_wiring():
    y = _yield_minutes()
    hm = lambda s: int(s[:2]) * 60 + int(s[3:])
    for t in ("10:30", "12:30", "14:00", "14:31"):               # 10-26 12:30 (114s) · 10-28 14:00 (63s) 충돌 지점
        assert hm(t) in y, t
    for t in ("10:10", "10:20", "13:50", "14:40", "15:00", "10:29", "14:32"):
        assert hm(t) not in y, t
    s = _ps_text("shindong2_run.ps1")
    i = s.index("intraday slot -> poll yields")
    blk = s[s.rindex("if ($Phase -eq 'poll')", 0, i):s.index("exit 0", i)]
    assert "poll-ack" not in blk                                  # 양보는 ack 하지 않는다 — intraday 실패 시 다음 poll 이 재시도
    assert i < s.index("Run-Live @('gate')") < s.index("Try-Lock)")   # 거래일 확인·잠금 전에 빠진다(6s 대기도 없앤다)
