# -*- coding: utf-8 -*-
"""[MW0602 2026-10-24 / 집행 장치 A2·A3 · 재알림] 청산 지정가 단계 상향 · 장기 미해소 재알림.

고정하는 불변식
  지정가 단계 상향
  · 미체결 취소 확인마다 25 → 50 → 100 → 200틱 → 가격제한폭(매수청산 = 상한 · 매도청산 = 하한)
  · 거부 에피소드 60초 경과면 단계와 무관하게 가격제한폭
  · 모든 단계 가격은 지금 유효한 가격제한폭 안(범위 밖 지정가 = 거부)
  · 가격제한폭 미확보면 마지막 틱 단계에 머물고 그 사실을 기준 문자열에 남긴다
  · 새 포지션은 첫 단계부터
  재알림
  · S등급 열린 에피소드만 · 5·15·30·60·120·180분 · 최대 6회 · 해소되면 멈춘다
  · 때가 아니면 아무것도 보내지 않는다 · 재알림은 하루 상한에 함께 센다
  · 동결 센티넬도 같은 일정
"""
import datetime
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402
from utils import alert_mail as AM  # noqa: E402
from scripts import freeze_sentinel as FS  # noqa: E402

TODAY = datetime.datetime.now().strftime("%Y-%m-%d")


class _RD(object):
    def __init__(self, base=855.88, upper=924.34, lower=787.42, bars=None):
        self._last_bid1, self._last_ask1 = 862.90, 863.00
        self.daily_limits = {"base": base, "upper": upper, "lower": lower}
        self.candles = bars if bars is not None else [
            {"ts": TODAY + " 09:01:00", "high": 866.0, "low": 860.0}]
        self.current_bar = None


class _Pos(object):
    def __init__(self, status="SHORT", entry=869.70):
        self.status, self.entry_price, self.quantity = status, entry, 1
        self.entry_time = datetime.datetime(2026, 10, 26, 10, 0)


class _Me(object):
    def __init__(self, rd=None):
        self.realtime_data = rd if rd is not None else _RD()
        self.position = _Pos()
        self._exit_reject_episode_at = None
        self._exit_limit_step = 0
        self._exit_limit_step_key = None

    def _peter2_last_price(self):
        return 863.18


TICK = 0.02


def _px(me, side="BUY"):
    return main._ts_exit_limit_price(me, side, "A056B")


# ── 지정가 단계 상향 ──────────────────────────────────────────────────────

def test_1_단계마다_폭이_넓어지고_마지막은_가격제한폭():
    me = _Me()
    want = [round(863.00 + t * TICK, 2) for t in (25, 50, 100, 200)]
    got = []
    for i in range(4):
        p, src = _px(me)
        got.append(p)
        assert "단계 %d/5" % (i + 1) in src, src
        me._exit_limit_step += 1                  # 미체결 취소 확인
    assert got == want, got
    p, src = _px(me)
    assert p == 924.34 and "가격제한폭(상한" in src, (p, src)
    me._exit_limit_step += 3                      # 그 위로는 올라가지 않는다
    assert _px(me)[0] == 924.34


def test_2_매도청산은_하한쪽():
    me = _Me()
    me._exit_limit_step = 4
    p, src = _px(me, "SELL")
    assert p == 787.42 and "하한" in src, (p, src)
    me._exit_limit_step = 1
    assert _px(me, "SELL")[0] == round(862.90 - 50 * TICK, 2)


def test_3_거부_60초_지나면_곧바로_가격제한폭():
    me = _Me()
    me._exit_reject_episode_at = datetime.datetime.now() - datetime.timedelta(seconds=30)
    assert "+25틱" in _px(me)[1]
    me._exit_reject_episode_at = datetime.datetime.now() - datetime.timedelta(seconds=61)
    assert _px(me)[0] == 924.34


def test_4_틱단계도_가격제한폭_안으로_자른다():
    me = _Me(_RD(base=800.0, upper=0.0, lower=0.0, bars=[]))   # 상한 = 800×1.08 = 864.00
    me._exit_limit_step = 2                                     # +100틱 = 865.00 → 범위 밖
    p, src = _px(me)
    assert p <= 864.0 and "상한" in src and "자름" in src, (p, src)


def test_5_가격제한폭_미확보면_마지막_틱단계():
    me = _Me(_RD(base=0.0, upper=0.0, lower=0.0))
    me._exit_limit_step = 9
    p, src = _px(me)
    assert p == round(863.00 + 200 * TICK, 2) and "미확보" in src, (p, src)


def test_6_장중_확대단계를_세션고가로_따라간다():
    # 기준 855.88 · 세션 고가가 1단계 상한(924.35)을 넘었다 → 2단계(+15% = 984.26)
    bars = [{"ts": TODAY + " 10:00:00", "high": 925.0, "low": 900.0},
            {"ts": "2026-01-02 10:00:00", "high": 999.0, "low": 700.0}]   # 다른 날 봉은 무시
    me = _Me(_RD(bars=bars))
    me._exit_limit_step = 4
    p, _src = _px(me)
    assert 984.0 <= p <= 984.26, p
    assert _px(me, "SELL")[0] == 787.42, "하한은 한 방향 확대 규정상 1단계 유지"


def test_7_새_포지션은_첫_단계부터():
    me = _Me()
    _px(me)
    me._exit_limit_step = 3
    assert "+200틱" in _px(me)[1]
    me.position = _Pos(status="LONG", entry=850.0)
    assert "+25틱" in _px(me)[1] and me._exit_limit_step == 0


def test_8_끄면_종전_고정_25틱(monkeypatch):
    monkeypatch.setattr(main, "EXIT_LIMIT_ESCALATION_ENABLED", False)
    me = _Me()
    me._exit_limit_step = 3
    p, src = _px(me)
    assert p == round(863.00 + 25 * TICK, 2) and "+25틱" in src


def test_9_설정_첫단계는_종전_고정폭과_같다():
    from config import settings as st
    assert st.EXIT_LIMIT_ESCALATION_TICKS[0] == st.EXIT_LIMIT_SLIP_TICKS
    assert list(st.EXIT_LIMIT_ESCALATION_TICKS) == sorted(st.EXIT_LIMIT_ESCALATION_TICKS)


# ── 재알림 ────────────────────────────────────────────────────────────────

class _Clock(object):
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture
def mailer(tmp_path):
    mails = []
    clk = _Clock(datetime.datetime(2026, 10, 26, 10, 0, 0))
    m = AM.AlertMailer(state_dir=str(tmp_path), pc="MW0602", sender=lambda s, b: mails.append((s, b)) or ["x"],
                       slack=lambda s, lv: None, daily_cap=30, enabled=True, clock=clk, threaded=False)
    m.slack_too = False
    return m, mails, clk


def test_10_일정대로_재알림하고_해소되면_멈춘다(mailer):
    m, mails, clk = mailer
    assert m.raise_alert("S-01", "SHORT 2계약 미청산", ["사유 0707"])
    t0 = clk.t
    sent_at = []
    for minute in range(0, 200):
        clk.t = t0 + datetime.timedelta(minutes=minute)
        if m.remind_due(lambda: {"position": "SHORT 2계약"}):
            sent_at.append(minute)
    assert sent_at == [5, 15, 30, 60, 120, 180], sent_at
    rem = [s for s, _ in mails if "재알림" in s]
    assert rem[0].startswith("[긴급이상][MW0602][S-01] 재알림 1 — ") and "미해소 5분" in rem[0]
    body = [b for s, b in mails if "재알림 2" in s][0]
    assert "지금 포지션 SHORT 2계약" in body and "사유 0707" in body and "할 일" in body
    m.resolve("S-01", note="청산 체결")
    clk.t = t0 + datetime.timedelta(minutes=500)
    assert m.remind_due() == []


def test_11_때가_아니거나_A등급이면_보내지_않는다(mailer):
    m, mails, clk = mailer
    m.raise_alert("A-03", "미륵 CB HALTED", key="HALTED")
    m.raise_alert("S-07", "손절선 통과")
    n0 = len(mails)
    clk.t = clk.t + datetime.timedelta(minutes=4)
    assert m.remind_due() == [] and len(mails) == n0
    clk.t = clk.t + datetime.timedelta(minutes=2)
    assert m.remind_due() == ["S-07"]


def test_12_재알림도_하루_상한에_센다(tmp_path):
    mails = []
    clk = _Clock(datetime.datetime(2026, 10, 26, 10, 0))
    m = AM.AlertMailer(state_dir=str(tmp_path), pc="MW0602", sender=lambda s, b: mails.append(s) or ["x"],
                       daily_cap=2, enabled=True, clock=clk, threaded=False)
    m.slack_too = False
    m.raise_alert("S-01", "x")
    clk.t += datetime.timedelta(minutes=5)
    m.remind_due()
    clk.t += datetime.timedelta(minutes=10)
    m.remind_due()
    assert len([s for s in mails if "재알림" in s]) == 1 and any("[CAP]" in s for s in mails), mails


def test_13_재알림_상태는_재기동해도_이어진다(mailer, tmp_path):
    m, mails, clk = mailer
    m.raise_alert("S-02", "15:12 이후 보유")
    clk.t += datetime.timedelta(minutes=6)
    m.remind_due()
    m2 = AM.AlertMailer(state_dir=str(tmp_path), pc="MW0602", sender=lambda s, b: mails.append((s, b)) or ["x"],
                        daily_cap=30, enabled=True, clock=clk, threaded=False)
    m2.slack_too = False
    assert m2.remind_due() == [], "같은 재알림을 다시 보내지 않는다"


def test_14_임계_계산():
    assert [AM.remind_threshold_min((5, 15, 30, 60), n) for n in range(7)] == [5, 15, 30, 60, 120, 180, 240]
    assert AM.remind_threshold_min((), 0) == float("inf")


def test_15_main_2초판정이_재알림을_부르고_예외를_가둔다(monkeypatch):
    called = []
    monkeypatch.setattr(AM, "remind_due", lambda fn=None: called.append(fn) or [])
    monkeypatch.setattr(main, "_ts_restart_stop_check_tick", lambda self, now: None)
    monkeypatch.setattr(main, "_ts_alert_stop_breach_tick", lambda self, now: None)

    class _CB(object):
        state = "NORMAL"

    class _S(object):
        position = _Pos(status="FLAT")
        circuit_breaker = _CB()
        _exchange_cb_mode = False
    main._ts_alert_state_tick(_S(), datetime.datetime(2026, 10, 26, 10, 0))
    assert len(called) == 1
    monkeypatch.setattr(AM, "remind_due", lambda fn=None: 1 / 0)
    main._ts_alert_state_tick(_S(), datetime.datetime(2026, 10, 26, 10, 0))   # 예외가 새지 않는다


def test_16_센티넬_동결_재알림_일정(monkeypatch):
    monkeypatch.setattr(FS, "_cfg", lambda n, d: d)
    t0 = datetime.datetime(2026, 10, 26, 10, 0)
    sent, n = [], 0
    for minute in range(0, 200):
        r = FS.remind_due_n(t0, t0 + datetime.timedelta(minutes=minute), n)
        if r is not None:
            n = r
            sent.append(minute)
    assert sent == [5, 15, 30, 60, 120, 180]
    v = {"headline": "동결", "details": ["a"]}
    s, b = FS.build_remind_mail(v, "MW0602", t0 + datetime.timedelta(minutes=15), t0, 2)
    assert s.startswith("[긴급이상][MW0602][S-04] 재알림 2 — ") and "15분째" in b
    assert FS.remind_due_n(None, t0, 0) is None
