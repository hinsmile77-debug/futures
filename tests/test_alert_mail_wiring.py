# -*- coding: utf-8 -*-
"""[MW0602 2026-10-17] 긴급 알림 메일 배선 — main / 동결 센티넬 / EOD 재학습.

고정하는 불변식
  · 카탈로그의 모든 코드가 **어딘가에서 발송**된다(죽은 코드 금지) — 보내는 주체가 맞다
      main: S-01 S-02 S-03 S-06 A-01 A-02 A-03 A-04 B-02 B-03 B-04
      동결 센티넬: S-04 S-05 (main 이 죽었거나 안 떴으면 main 은 보낼 수 없다)
      EOD 재학습: B-01
  · 상태형(S-02 · A-01 · A-03)은 한 함수에서 발생과 해소를 같이 판정한다 — 해소 누락 방지
  · A-04 기준: 거래 1건 순손실 75만원 · 당일 실현 순손실 자본의 5%
  · 본문 문맥(포지션 평가손익)이 포맷 예외로 사라지지 않는다 — `%+,.0f` 는 printf 포맷이
    아니라 ValueError 다(초안이 그렇게 써서 A-04 가 조용히 안 나갈 뻔했다)
  · 거래소 CB 날은 B-03(분봉 결손) 메일을 보내지 않는다 — 결손이 아니라 거래 중단이다
  · 알림 배선은 예외를 호출부로 내보내지 않는다
"""
import datetime
import io
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402
from utils import alert_mail as AM  # noqa: E402


class _Clock(object):
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture
def mail(tmp_path):
    mails, slacks = [], []
    clk = _Clock(datetime.datetime(2026, 10, 15, 15, 13))
    AM.configure(state_dir=str(tmp_path), pc="MW0602", sender=lambda s, b: mails.append((s, b)) or ["x"],
                 slack=lambda m, lv: slacks.append(m), enabled=True, daily_cap=30, clock=clk,
                 threaded=False)
    yield mails, clk
    AM.configure(state_dir=str(tmp_path / "after"), enabled=False, threaded=False)


class _Pos(object):
    def __init__(self, status="SHORT", qty=1, entry=869.70):
        self.status, self.quantity, self.entry_price = status, qty, entry
        self.entry_source = "SHINDONG"

    def unrealized_pnl_pts(self, px):
        return (self.entry_price - px) if self.status == "SHORT" else (px - self.entry_price)


class _CB(object):
    state = "NORMAL"
    _halt_cause = ""


class _Self(object):
    def __init__(self):
        self.position = _Pos()
        self.circuit_breaker = _CB()
        self._alert_server_label = "Cybos 실서버(실계좌)"
        self._alert_day = None
        self._alert_day_net = 0.0
        self._broker_dep_base_today = None   # [707차] A-04 기준 = min(고정값, 당일 시가 예탁금) — 미측정이면 고정값
        self._exchange_cb_mode = False
        self._exchange_cb_start = None
        self._exit_reject_episode_at = None
        self._exit_limit_mode_reason = None
        self._pt_value = 50000

    def _peter2_last_price(self):
        return 863.00


def _subjects(mails):
    return [s for s, _ in mails]


# ── 카탈로그 전 코드가 발송된다 ─────────────────────────────────────────────

def _src(rel):
    return io.open(os.path.join(_ROOT, rel), encoding="utf-8").read()


def test_1_every_catalog_code_has_a_sender():
    main_src = _src("main.py")
    sent_by_main = set(re.findall(r'_ts_alert\(self, "([SAB]-\d\d)"', main_src))
    # S-05 는 센티넬(오늘 SYSTEM.log 없음)과 main(브로커 로그인 실패로 기동 중단) 둘이 나눠 맡는다
    assert sent_by_main == {"S-01", "S-02", "S-03", "S-05", "S-06", "A-01", "A-02", "A-03", "A-04",
                            "B-02", "B-03", "B-04"}, sent_by_main
    fs = _src(os.path.join("scripts", "freeze_sentinel.py"))
    assert 'ALERT_CODE_FREEZE = "S-04"' in fs and 'ALERT_CODE_NOT_STARTED = "S-05"' in fs
    assert '"B-01"' in _src("retrain_eod.py")
    assert set(AM.CATALOG) == sent_by_main | {"S-04", "S-05", "B-01"}


def test_2_resolvers_exist_for_episodes():
    s = _src("main.py")
    for code in ("S-01", "S-02", "S-03", "S-06", "A-01", "A-03"):
        assert '_ts_alert_resolve(self, "%s"' % code in s, code


# ── 상태형 판정 ───────────────────────────────────────────────────────────

def test_3_s02_raise_once_then_resolve_on_flat(mail, monkeypatch):
    mails, clk = mail
    monkeypatch.setattr(main, "is_trading_day", lambda now: True)
    me = _Self()
    main._ts_alert_state_tick(me, datetime.datetime(2026, 10, 15, 15, 11))
    assert mails == [], "15:12 전에는 보내지 않는다"
    main._ts_alert_state_tick(me, datetime.datetime(2026, 10, 15, 15, 13))
    main._ts_alert_state_tick(me, datetime.datetime(2026, 10, 15, 15, 14))
    assert len(mails) == 1 and mails[0][0].startswith("[긴급이상][MW0602][S-02] ")
    body = mails[0][1]
    assert "Cybos 실서버(실계좌)" in body and "SHORT 1계약 @869.70" in body
    assert "평가 +6.70pt(+335,000원)" in body, body     # 포맷 예외로 문맥이 사라지지 않는다
    me.position.status = "FLAT"
    clk.t = datetime.datetime(2026, 10, 15, 15, 20)
    main._ts_alert_state_tick(me, clk.t)
    assert mails[1][0] == "[이상해소][MW0602][S-02] 15:10 강제청산 실패 — 오버나이트 위험 해소 — 지속 7분"


def test_4_a01_exchange_cb_and_a03_mireuk_cb(mail, monkeypatch):
    mails, _ = mail
    monkeypatch.setattr(main, "is_trading_day", lambda now: True)
    me = _Self()
    me.position.status = "FLAT"
    t = datetime.datetime(2026, 10, 15, 12, 45)
    me._exchange_cb_mode = True
    me._exchange_cb_start = datetime.datetime(2026, 10, 15, 12, 39)
    main._ts_alert_state_tick(me, t)
    main._ts_alert_state_tick(me, t)
    me._exchange_cb_mode = False
    main._ts_alert_state_tick(me, t)
    subj = _subjects(mails)
    assert len(subj) == 2, subj
    assert subj[0].startswith("[긴급이상][MW0602][A-01] ") and subj[1].startswith("[이상해소][MW0602][A-01] ")
    assert "12:39~" in mails[0][0]
    me.circuit_breaker.state = "PAUSED"
    main._ts_alert_state_tick(me, t)
    main._ts_alert_state_tick(me, t)
    me.circuit_breaker.state = "NORMAL"
    main._ts_alert_state_tick(me, t)
    assert sum("[A-03]" in s for s in _subjects(mails)) == 2


# ── A-04 큰 손실 ─────────────────────────────────────────────────────────

def test_5_a04_trade_threshold(mail, monkeypatch):
    mails, _ = mail
    monkeypatch.setattr(main, "ALERT_LOSS_CAPITAL_KRW", 15_000_000)
    me = _Self()
    main._ts_alert_trade_loss(me, {"pnl_net_krw": -749_999, "exit_ts": "10:00:00"})
    assert mails == []
    main._ts_alert_trade_loss(me, {"pnl_net_krw": -750_000, "exit_ts": "10:05:00", "direction": "SHORT",
                                   "quantity": 1, "entry_price": 869.7, "exit_price": 884.7,
                                   "exit_reason": "하드스톱"})
    subj = _subjects(mails)
    assert any(s.startswith("[긴급이상][MW0602][A-04] 큰 손실 — 거래 1건 -750,000원") for s in subj), subj
    assert any("당일 실현 -1,499,999원" in s for s in subj), "당일 누적 5%(75만) 초과도 같이"


def test_6_a04_daily_cumulative_once(mail, monkeypatch):
    mails, _ = mail
    monkeypatch.setattr(main, "ALERT_LOSS_CAPITAL_KRW", 15_000_000)
    me = _Self()
    for i in range(5):
        main._ts_alert_trade_loss(me, {"pnl_net_krw": -300_000, "exit_ts": "1%d:00:00" % i})
    subj = _subjects(mails)
    assert len(subj) == 1 and "당일 실현 -900,000원" in subj[0], subj


def test_7_wiring_never_raises(mail):
    class _Bad(object):
        def __getattr__(self, n):
            raise RuntimeError(n)
    main._ts_alert_state_tick(_Bad(), datetime.datetime(2026, 10, 15, 15, 13))
    main._ts_alert_trade_loss(_Bad(), {"pnl_net_krw": "x"})
    main._ts_alert(_Bad(), "S-01", "x")
    main._ts_alert_resolve(_Bad(), "S-01")


# ── B-03 거래소 CB 날 억제 · B-04 ─────────────────────────────────────────

def test_8_b03_suppressed_on_exchange_cb_day():
    s = _src("main.py")
    i = s.index('"B-03", "분봉 영구 결손')
    head = s[max(0, i - 600):i]
    assert 'happened_today("A-01")' in head


def test_9_happened_today_includes_resolved(mail):
    mails, _ = mail
    AM.raise_alert("A-01", "x")
    AM.resolve("A-01")
    assert AM.happened_today("A-01")
    assert not AM.happened_today("S-01")


def test_10_settings_defaults():
    from config import settings as st
    assert st.ALERT_MAIL_ENABLED is True and st.ALERT_MAIL_SLACK_TOO is True
    assert st.ALERT_MAIL_DAILY_CAP == 30
    assert st.ALERT_LOSS_TRADE_KRW == 750_000 and st.ALERT_LOSS_DAY_PCT == 0.05
    # [2026-10-17 사용자 결정] A-04 당일 기준은 사이징 자본이 아니라 1,500만원 고정 — 두 PC 동일
    assert st.ALERT_LOSS_CAPITAL_KRW == 15_000_000
    assert st.ALERT_FORCE_EXIT_CHECK_HM == "15:12" and st.ALERT_PREMARKET_START_HM == "08:52"


def test_11_no_printf_comma_format_in_alert_code():
    for rel in ("main.py", os.path.join("utils", "alert_mail.py"),
                os.path.join("scripts", "freeze_sentinel.py"), "retrain_eod.py"):
        code = [ln for ln in _src(rel).splitlines() if not ln.strip().startswith("#")]
        bad = [ln for ln in code if re.search(r'"[^"]*%[+\-0 #]*,\.?\d*f', ln)]
        assert not bad, (rel, bad[:3])
