# -*- coding: utf-8 -*-
"""[MW0602 673차 후속6] 신동 R1(수급 타이머 봉 마감 정렬) · R2(기준분 미달 1회 재시도) · R4(청산 슬립 계측).

근거: docs/정기점검/매일점검/MW0602-20261029-청산슬립-딥다이브.md — 손절 갱신이 타이머 위상(:33~35)만큼 늦어
10/29 청산 −2.66pt 중 −2.32pt 가 「낡은 손절」 몫이었다.

main.py 는 PyQt5 를 끌어오므로(이 테스트 환경에 없을 수 있다) R1·R2 는 소스 불변식으로 고정하고,
R4 는 순수 함수로 값까지 고정한다.
"""
import os
import re
import sys
import types

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest  # noqa: E402

from strategy.shindong import daily_report as DR, exec_recon as XR  # noqa: E402

_MAIN = os.path.join(_ROOT, "main.py")
_BRS = os.path.join(_ROOT, "strategy", "runtime", "broker_runtime_service.py")


def _src(p):
    return open(p, encoding="utf-8").read()


def _body(src, name):
    return src.split("def %s" % name, 1)[1].split("\n    def ", 1)[0]


# ── R1 ──────────────────────────────────────────────────────────────────────
def test_r1_settings_defaults():
    s = _src(os.path.join(_ROOT, "config", "settings.py"))
    for k, v in (("SHINDONG_TIMER_ALIGN_ENABLED", "True"), ("SHINDONG_TIMER_ALIGN_SEC", "2"),
                 ("SHINDONG_TIMER_ALIGN_DRIFT_SEC", "5"), ("SHINDONG_FLOW_RETRY_ENABLED", "True"),
                 ("SHINDONG_FLOW_RETRY_SEC", "8")):
        assert re.search(r"^%s = %s\b" % (k, v), s, re.M), k


def test_r1_both_timer_creators_use_wire_and_begin():
    m, b = _src(_MAIN), _src(_BRS)
    # 기동 설정 · 브로커 연결 두 곳 모두 같은 정렬 경로
    assert "self._investor_timer_wire()" in m and 'self._investor_timer_begin("기동")' in m
    assert "system._investor_timer_wire()" in b and "system._investor_timer_begin(reason)" in b
    # 정렬 모드에선 타이머가 수집 함수에 직접 붙지 않는다(위상 감시 슬롯 경유)
    w = _body(m, "_investor_timer_wire")
    assert "Qt.PreciseTimer" in w and "self._investor_timer_tick" in w
    # 정렬 예약 중 중복 예약 금지 · 브로커 경로는 예약 중이면 손대지 않는다
    assert "if self._investor_align_pending:" in _body(m, "_investor_timer_align")
    assert '_investor_align_pending", False' in b


def test_r1_tick_realigns_only_after_two_drifts_and_skips_that_tick():
    t = _body(_src(_MAIN), "_investor_timer_tick")
    assert "self._investor_drift_n >= 2" in t
    i_stop, i_ret, i_fetch = t.index("self._investor_timer.stop()"), t.index("return"), t.index("self._fetch_investor_data()")
    assert i_stop < i_ret < i_fetch           # 재정렬 틱은 수집하지 않는다(55초 가드 충돌 회피)


def test_r1_begin_does_not_fetch_immediately_when_aligned():
    b = _body(_src(_MAIN), "_investor_timer_begin")
    assert "_fetch_investor_data" not in b.split('"""', 2)[2]


def test_r1_drift_math():
    def d(sec, us, align=2):
        return ((sec + us / 1e6) - align + 30.0) % 60.0 - 30.0
    assert d(2, 0) == 0 and d(7, 500000) == pytest.approx(5.5) and d(59, 0) == pytest.approx(-3.0)
    assert d(33, 0) == pytest.approx(-29.0) or d(33, 0) == pytest.approx(31.0 - 60.0)


# ── R2 ──────────────────────────────────────────────────────────────────────
def test_r2_retry_once_per_minute_and_keeps_55s_guard():
    m = _src(_MAIN)
    may = _body(m, "_shindong_flow_retry_maybe")
    assert "self._sd_flow_retry_minute == minute" in may and "hz >= cur" in may
    body = _body(m, "_shindong_flow_retry(self")
    assert "self._wof_last_ts =" not in body            # 갱신하면 다음 정렬 틱이 55초 가드에 걸린다
    assert "self._run_shindong(now, retry=True)" in body
    assert "_defer_if_pump_busy" in body                # 펌프 중첩 금지(622차)
    assert "self._shindong_flow_retry_maybe(now)" in _body(m, "_fetch_weekly_option_flow")


def test_r2_r4_state_initialized_in_init():
    init = _src(_MAIN).split("def __init__", 1)[1][:200000]
    for a in ("self._investor_align_pending = False", "self._investor_drift_n = 0",
              "self._sd_flow_retry_minute = None", "self._sd_cadence = None"):
        assert a in init


def test_r4_cadence_note_wired_and_retry_separated():
    m = _src(_MAIN)
    assert "self._sd_cadence_note(now, retry)" in _body(m, "_run_shindong")
    note = _body(m, "_sd_cadence_note")
    assert '"retries"' in note and "shindong_cadence.json" in note


# ── R4 순수 함수 ──────────────────────────────────────────────────────────────
def _item(side, rep_px, reason, real_px, exit_ts, why="하드스톱(틱)[TP1미도달]", qty=1):
    return dict(kind="MATCH", key="K",
                real=dict(qty=qty, side=side, entry_px=0.0, net=0.0, exit_ts=exit_ts,
                          legs=[(exit_ts[11:16], real_px, why)]),
                replay=dict(side=side, entry_px=0.0, net=0.0, entry_ts="10:00",
                            legs=[("10:00", rep_px, reason), ("10:00", rep_px, reason)]))


def _rc_1029():
    # 10/29 실측(청산슬립 딥다이브 §2) — 위상 :33
    return {"items": [
        _item(1, 961.36, "TR", 961.06, "2026-10-29 09:28:10"),
        _item(-1, 944.32, "BE", 946.14, "2026-10-29 10:07:33"),
        _item(-1, 939.18, "TR", 939.54, "2026-10-29 10:15:27"),
        _item(-1, 932.08, "TR", 932.26, "2026-10-29 10:25:51"),
        _item(1, 885.48, "TIME", 883.24, "2026-10-29 14:49:47", why="수동 전량청산"),
    ], "phase_sec": 34}


def test_r4_exit_slips_sign_window_manual():
    sl = XR.exit_slips(_rc_1029(), 34)
    assert [round(x["slip_pt"], 2) for x in sl] == [0.30, 1.82, 0.36, 0.18, 2.24]
    assert [x["window"] for x in sl[:4]] == ["in", "in", "in", "out"]
    assert sl[4]["manual"] and sl[4]["window"] is None          # 시간·수동은 창 판정 없음
    assert XR.exit_slips(_rc_1029(), None)[0]["window"] is None  # 위상 미측정 ≠ 창 밖
    assert XR.exit_slips(None) is None


def test_r4_exit_slip_line():
    line = DR._exit_slip_line(_rc_1029(), None)
    assert "오늘 4건 평균 +0.66pt" in line and "최악 +1.82pt" in line
    assert "갱신창(:00~:34) 안 3건 평균 +0.83 / 밖 1건 평균 +0.18" in line
    assert "그날 갱신 위상 :34" in line and "수동 청산 1건 제외" in line and line.endswith("누적 미측정")
    rc = _rc_1029()
    rc["phase_sec"] = None
    assert "갱신 위상 미측정 — 창 판정 불가" in DR._exit_slip_line(rc)


def test_r4_cadence_phase_mode(monkeypatch):
    fake = types.ModuleType("strategy.runtime.trade_principal")
    fake.read_json = lambda day, name, default=None: {"date": day, "sec_hist": {"2": 300, "34": 5, "10": 2}}
    pkg = types.ModuleType("strategy.runtime")
    pkg.trade_principal = fake
    monkeypatch.setitem(sys.modules, "strategy.runtime", pkg)
    monkeypatch.setitem(sys.modules, "strategy.runtime.trade_principal", fake)
    assert XR.cadence_phase("2026-10-30") == 2
    fake.read_json = lambda day, name, default=None: default
    assert XR.cadence_phase("2026-10-30") is None
