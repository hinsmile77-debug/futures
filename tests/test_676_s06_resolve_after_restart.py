# -*- coding: utf-8 -*-
"""[MW0602 2026-10-30 676차 후속 / F-SD-7] S-06(브로커 연결 끊김) 경보가 프로세스 재기동을 넘겨 해소된다.

사건: 12:59 S-06 열림 → 13:23 재기동(새 프로세스, `_alert_broker_lost_at=None`)으로 실제 복구됐는데
해소 조건이 인메모리 값만 봐서 해소가 안 불렸고, 재알림이 13:29·13:59·14:59 에 계속 나갔다.

고정하는 불변식
  · 재기동 뒤(인메모리 None) 연결돼 있고 영속 상태에 S-06 이 열려 있으면 해소된다
  · 같은 프로세스 안의 종전 경로(끊김 겪음 → 재연결)도 그대로 해소된다
  · 연결이 끊긴 동안에는 해소하지 않는다
  · 열린 에피소드가 없으면 해소 메일을 보내지 않는다(매 tick 호출되므로 스팸 금지)
  · 스케줄러는 이 헬퍼를 부른다(인라인 조건으로 되돌아가지 않는다)
"""
import datetime
import io
import os
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
    mails = []
    clk = _Clock(datetime.datetime(2026, 10, 30, 12, 59, 3))
    AM.configure(state_dir=str(tmp_path), pc="MW0602", sender=lambda s, b: mails.append((s, b)) or ["x"],
                 slack=lambda m, lv: None, enabled=True, daily_cap=30, clock=clk, threaded=False)
    yield mails, clk, tmp_path
    AM.configure(state_dir=str(tmp_path / "after"), enabled=False, threaded=False)


class _Broker(object):
    def __init__(self, connected):
        self.is_connected = connected


class _Self(object):
    def __init__(self, connected, lost_at=None):
        self.broker = _Broker(connected)
        self._alert_broker_lost_at = lost_at


def _open_s06():
    AM.raise_alert("S-06", "12:57:33~ 연결 끊김 지속", ["자동 재연결 시도 중"], "", {})
    assert AM.is_open("S-06")


def test_1_resolves_after_restart_from_persistent_state(mail):
    mails, clk, tmp = mail
    _open_s06()
    # 재기동: 영속 상태를 새로 읽는 새 메일러(같은 상태 폴더) + 인메모리 None
    AM.configure(state_dir=str(tmp), pc="MW0602", sender=lambda s, b: mails.append((s, b)) or ["x"],
                 slack=lambda m, lv: None, enabled=True, daily_cap=30, clock=clk, threaded=False)
    assert AM.is_open("S-06"), "재기동 뒤에도 영속 상태에서 열림이 보여야 한다"
    clk.t = datetime.datetime(2026, 10, 30, 13, 23, 30)
    n0 = len(mails)
    main._ts_alert_broker_resolve(_Self(connected=True, lost_at=None))
    assert not AM.is_open("S-06")
    assert len(mails) == n0 + 1


def test_2_in_process_reconnect_still_resolves(mail):
    _open_s06()
    s = _Self(connected=True, lost_at=datetime.datetime(2026, 10, 30, 12, 57, 33))
    main._ts_alert_broker_resolve(s)
    assert not AM.is_open("S-06")
    assert s._alert_broker_lost_at is None


def test_3_no_resolve_while_disconnected(mail):
    _open_s06()
    lost = datetime.datetime(2026, 10, 30, 12, 57, 33)
    s = _Self(connected=False, lost_at=lost)
    main._ts_alert_broker_resolve(s)
    assert AM.is_open("S-06")
    assert s._alert_broker_lost_at == lost, "끊긴 동안 끊김 시각을 지우면 S-06 지속 판정이 깨진다"


def test_4_no_mail_when_nothing_open(mail):
    mails, _, _ = mail
    for _ in range(5):
        main._ts_alert_broker_resolve(_Self(connected=True, lost_at=None))
    assert mails == []


def test_5_scheduler_calls_helper():
    with io.open(os.path.join(_ROOT, "main.py"), "r", encoding="utf-8") as f:
        src = f.read()
    assert "        _ts_alert_broker_resolve(self)\n" in src
    assert "if self.broker.is_connected and self._alert_broker_lost_at is not None:" not in src
