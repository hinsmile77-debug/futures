# -*- coding: utf-8 -*-
"""[MW0602 2026-10-24 사용자 결정] 동결 시 강제 재기동 + 기동 직후 손절 재판정.

배경: Cybos/CREON Plus API 에 서버 측 스톱이 없다 — 프로세스가 얼어붙으면 손절이 나가지 않는다
(`docs/신동거래_V4/서버측_스톱주문_지원여부_조사_MW0602-20261024.md`).

고정하는 불변식
  센티넬(`scripts/freeze_sentinel.py`)
  · 끊는 것은 **보유 중 · 장중 창 · FZ-1 스레드 신호 2종(하트비트 · [TS]) 둘 다 정체** 일 때뿐
  · 무포지션 · 포지션 미측정 · 신호 하나라도 신선 · 마감 마커 · 창 밖 · 하루 상한 · 쿨다운 → 안 끊는다
  · 대상은 하트비트 pid — 살아 있는 이 저장소 main.py 이고 하트비트보다 먼저 생긴 프로세스만
  · `--once`(수동 진단)는 판정만 하고 절대 끊지 않는다
  · 기록(`data/freeze_kill_<date>.json`)은 끊기 **전에** 남긴다
  · 루프: 끊으면 메일 1통(강제 재기동) · 같은 동결로 1단계 메일이 또 가지 않는다 · 회복 메일 1통
  main(`_ts_restart_stop_check_tick`)
  · 복원 포지션 + 첫 장중 실시간가가 손절선 밖 → 틱 하드스톱과 같은 `_process_tick_stop` 예약(1회)
  · 이미 청산 진행 중 · CB HALT → 추가 주문 없음
  · 손절선 안 → 주문 없이 판정 종료
  · 장중 가격 미수신 RESTART_STOP_CHECK_NOPRICE_SEC → S-08 · 가격이 오면 해소
"""
import datetime
import io
import json
import os
import sys
import time
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from scripts import freeze_sentinel as FS  # noqa: E402

NOW = datetime.datetime(2026, 10, 26, 10, 30, 0)
STALE = {FS.SIG_HEARTBEAT: 200.0, FS.SIG_TS: 210.0, FS.SIG_SYSLOG: 230.0}
HOLD = {"status": "SHORT", "quantity": 3, "entry_source": "SHINDONG", "stop_price": 880.0}
W = ("09:00", "15:05")


def _dec(ages=STALE, now=NOW, pos=HOLD, hist=(), **kw):
    return FS.kill_decision(ages, now, 180.0, W, pos, list(hist), **kw)


# ── 판정(순수 함수) ─────────────────────────────────────────────────────────

def test_1_보유중_스레드신호_둘다_정체면_끊는다():
    d = _dec()
    assert d["kill"] is True, d["reason"]
    assert "SHORT 3계약" in d["reason"]


@pytest.mark.parametrize("label,kw", [
    ("무포지션", dict(pos={"status": "FLAT", "quantity": 0})),
    ("포지션 미측정", dict(pos=None)),
    ("SYSTEM.log 신선", dict(ages=dict(STALE, **{FS.SIG_SYSLOG: 20.0}))),
    ("하트비트 미측정", dict(ages=dict(STALE, **{FS.SIG_HEARTBEAT: None}))),
    ("[TS] 신선", dict(ages=dict(STALE, **{FS.SIG_TS: 25.0}))),
    ("정체 180초 미만", dict(ages={FS.SIG_HEARTBEAT: 150.0, FS.SIG_TS: 160.0, FS.SIG_SYSLOG: 170.0})),
    ("15:06 창 밖", dict(now=NOW.replace(hour=15, minute=6))),
    ("08:59 창 밖", dict(now=NOW.replace(hour=8, minute=59))),
    ("하루 상한", dict(hist=[{"at": "2026-10-26 09:10:00"}, {"at": "2026-10-26 09:40:00"}])),
    ("쿨다운", dict(hist=[{"at": "2026-10-26 10:25:00"}])),
    ("마감 마커가 신호보다 뒤", dict(close_done_age=100.0)),
    ("종료 마커가 신호보다 뒤", dict(shutdown_age=150.0)),
])
def test_2_조건_하나라도_빠지면_안_끊는다(label, kw):
    d = _dec(**kw)
    assert d["kill"] is False, label
    assert d["reason"], label


def test_3_쿨다운_지나면_다시_끊는다():
    assert _dec(hist=[{"at": "2026-10-26 10:15:00"}])["kill"] is True


# ── 대상 확인(가짜 psutil) ─────────────────────────────────────────────────

class _FakeProc(object):
    killed = []

    def __init__(self, pid, procs):
        if pid not in procs:
            raise OSError("no such process")
        self.pid = pid
        self._d = procs[pid]

    def name(self):
        return self._d["name"]

    def cmdline(self):
        return self._d["cmd"]

    def cwd(self):
        return self._d.get("cwd", "")

    def create_time(self):
        return self._d["created"]

    def kill(self):
        _FakeProc.killed.append(self.pid)

    def wait(self, timeout=None):
        return 0


def _fake_psutil(procs):
    m = types.ModuleType("psutil")
    m.Process = lambda pid: _FakeProc(pid, procs)
    return m


def _write_hb(root, pid, written):
    d = os.path.join(root, "data")
    os.makedirs(d, exist_ok=True)
    with io.open(os.path.join(d, "heartbeat_MW0602_%s.json" % written.strftime("%Y%m%d")), "w",
                 encoding="utf-8") as f:
        json.dump({"pid": pid, "written_at": written.isoformat(timespec="seconds")}, f)


def _ts(dt):
    return time.mktime(dt.timetuple())


def test_4_대상은_하트비트_pid의_이_저장소_main_py뿐(tmp_path):
    root = str(tmp_path)
    hb_at = NOW - datetime.timedelta(seconds=200)
    _write_hb(root, 4242, hb_at)
    main_py = os.path.join(root, "main.py")
    ok = {4242: {"name": "python.exe", "cmd": ["python.exe", main_py],
                 "created": _ts(NOW.replace(hour=8, minute=41))}}
    t = FS.resolve_target(root, NOW.date(), pc="MW0602", psutil_mod=_fake_psutil(ok))
    assert t["ok"] is True and t["pid"] == 4242, t
    # 상대 경로 main.py + cwd 도 같은 저장소로 인식
    rel = {4242: dict(ok[4242], cmd=["python.exe", "main.py"], cwd=root)}
    assert FS.resolve_target(root, NOW.date(), "MW0602", _fake_psutil(rel))["ok"] is True
    bad = [
        ("다른 저장소", {4242: dict(ok[4242], cmd=["python.exe", r"D:\other\main.py"])}),
        ("python 아님", {4242: dict(ok[4242], name="chrome.exe")}),
        ("PID 재사용", {4242: dict(ok[4242], created=_ts(NOW))}),
        ("프로세스 없음", {}),
    ]
    for label, procs in bad:
        t = FS.resolve_target(root, NOW.date(), "MW0602", _fake_psutil(procs))
        assert t["ok"] is False, label
    os.remove(os.path.join(root, "data", "heartbeat_MW0602_%s.json" % NOW.strftime("%Y%m%d")))
    assert FS.resolve_target(root, NOW.date(), "MW0602", _fake_psutil(ok))["ok"] is False


def _setup_root(tmp_path, status="SHORT", qty=3):
    root = str(tmp_path)
    _write_hb(root, 4242, NOW - datetime.timedelta(seconds=200))
    with io.open(os.path.join(root, "data", "position_state.json"), "w", encoding="utf-8") as f:
        json.dump({"status": status, "quantity": qty, "entry_source": "SHINDONG", "stop_price": 880.0,
                   "saved_at": (NOW - datetime.timedelta(minutes=5)).isoformat()}, f)
    procs = {4242: {"name": "python.exe", "cmd": ["python.exe", os.path.join(root, "main.py")],
                    "created": _ts(NOW.replace(hour=8, minute=41))}}
    return root, _fake_psutil(procs)


KCFG = {"stall": 180.0, "window": W, "max_per_day": 2, "cooldown": 600.0}


def test_5_수동진단은_절대_끊지_않는다(tmp_path):
    root, ps = _setup_root(tmp_path)
    _FakeProc.killed = []
    out = FS.try_kill(root, NOW, STALE, KCFG, {}, "MW0602", psutil_mod=ps, execute=False)
    assert out["decision"]["kill"] is True and out["done"] is False
    assert _FakeProc.killed == []
    assert FS.load_kill_history(root, NOW.date()) == []


def test_6_실행하면_기록을_먼저_남기고_한번_끊는다(tmp_path):
    root, ps = _setup_root(tmp_path)
    _FakeProc.killed = []
    out = FS.try_kill(root, NOW, STALE, KCFG, {}, "MW0602", psutil_mod=ps)
    assert out["done"] and out["ok"] and _FakeProc.killed == [4242], out
    hist = FS.load_kill_history(root, NOW.date())
    assert len(hist) == 1 and hist[0]["pid"] == 4242 and hist[0]["position"]["status"] == "SHORT"
    # 같은 동결의 다음 주기 — 쿨다운으로 다시 안 끊는다
    out2 = FS.try_kill(root, NOW + datetime.timedelta(seconds=60), STALE, KCFG, {}, "MW0602", psutil_mod=ps)
    assert out2["done"] is False and _FakeProc.killed == [4242]


def test_7_무포지션이면_대상확인도_하지_않는다(tmp_path):
    root, ps = _setup_root(tmp_path, status="FLAT", qty=0)
    _FakeProc.killed = []
    out = FS.try_kill(root, NOW, STALE, KCFG, {}, "MW0602", psutil_mod=ps)
    assert out["done"] is False and out["target"] is None and _FakeProc.killed == []


def test_8_어제_포지션파일은_미측정(tmp_path):
    root, ps = _setup_root(tmp_path)
    p = os.path.join(root, "data", "position_state.json")
    st = json.load(io.open(p, encoding="utf-8"))
    st["saved_at"] = (NOW - datetime.timedelta(days=1)).isoformat()
    json.dump(st, io.open(p, "w", encoding="utf-8"))
    assert FS.position_state(root, NOW) is None


def test_9_메일_본문():
    s, b = FS.build_kill_mail({"reason": "보유 중 동결", "verdict": {"details": ["a"]}},
                              {"why": "pid 4242 main.py"}, True, "pid 4242 종료 요청 완료",
                              "MW0602", NOW, HOLD)
    assert s.startswith("[긴급이상][MW0602][S-04] ") and "강제 재기동 실행" in s
    assert "SHORT 3계약" in b and "손절을 즉시 재판정" in b and "HTS" in b


# ── 감시 루프 통합 ─────────────────────────────────────────────────────────

class _Stop(Exception):
    pass


def test_10_루프_끊으면_메일1통_같은동결_재경보없음_회복1통(monkeypatch, tmp_path):
    frozen = {"level": "CRITICAL", "rc": FS.RC_FROZEN, "state": "FROZEN", "headline": "동결",
              "details": [], "stale": [FS.SIG_HEARTBEAT, FS.SIG_TS, FS.SIG_SYSLOG], "unmeasured": []}
    ok = {"level": "OK", "rc": FS.RC_OK, "state": "WATCHING", "headline": "정상",
          "details": [], "stale": [], "unmeasured": []}
    seq = iter([frozen, frozen, ok])
    kills = iter([True, False, False])
    sent = []
    monkeypatch.setattr(FS, "judge", lambda *a, **k: next(seq))
    monkeypatch.setattr(FS, "collect", lambda *a, **k: {})
    monkeypatch.setattr(FS, "_in_window", lambda now, w: True)
    monkeypatch.setattr(FS, "_pc_id", lambda: "MW0602")
    monkeypatch.setattr(FS, "_popup", lambda v: None)
    monkeypatch.setattr(FS.PremarketWatch, "tick", lambda self, now: "OK")

    def _try(root, now, ages, kcfg, flags, pc, psutil_mod=None, execute=True):
        k = next(kills)
        return {"done": k, "ok": k, "msg": "pid 4242 종료 요청 완료" if k else "",
                "decision": {"kill": k, "reason": "보유 중 동결" if k else "쿨다운", "verdict": frozen},
                "target": {"ok": True, "pid": 4242, "why": "pid 4242"} if k else None,
                "position": HOLD}
    monkeypatch.setattr(FS, "try_kill", _try)
    monkeypatch.setattr(FS, "send_mail_async",
                        lambda root, day, s, b, sender=None, **k: sent.append(s))
    cfg = {"FREEZE_SENTINEL_ENABLED": True, "FREEZE_SENTINEL_MAIL_ENABLED": True,
           "FREEZE_SENTINEL_MAIL_RECOVERY": True, "FREEZE_SENTINEL_KILL_ENABLED": True,
           "FREEZE_SENTINEL_POPUP": False}
    monkeypatch.setattr(FS, "_cfg", lambda n, d: cfg.get(n, d))
    import utils.time_utils as tu
    monkeypatch.setattr(tu, "is_trading_day", lambda now: True)
    calls = {"n": 0}

    def _sleep(_):
        calls["n"] += 1
        if calls["n"] >= 3:
            raise _Stop()
    monkeypatch.setattr(FS.time, "sleep", _sleep)
    with pytest.raises(_Stop):
        FS.main(["--root", str(tmp_path), "--no-popup"])
    assert len(sent) == 2, sent
    assert "강제 재기동 실행" in sent[0] and sent[0].startswith("[긴급이상][MW0602][S-04] ")
    assert sent[1].startswith("[이상해소][MW0602][S-04] ")
    log = io.open(os.path.join(str(tmp_path), "logs", "freeze_sentinel_%s.log"
                               % datetime.date.today().strftime("%Y%m%d")), encoding="utf-8").read()
    assert "강제 재기동 실행" in log and "보유 중 동결 강제 재기동 ON" in log


# ── main: 재기동 직후 손절 재판정 ──────────────────────────────────────────

import main  # noqa: E402
from utils import alert_mail as AM  # noqa: E402


@pytest.fixture
def mail(tmp_path):
    mails = []
    clk = lambda: datetime.datetime(2026, 10, 26, 10, 30)  # noqa: E731
    AM.configure(state_dir=str(tmp_path), pc="MW0602", sender=lambda s, b: mails.append((s, b)) or ["x"],
                 slack=lambda m, lv: None, enabled=True, daily_cap=30, clock=clk, threaded=False)
    yield mails
    AM.configure(state_dir=str(tmp_path / "after"), enabled=False, threaded=False)


class _Pos(object):
    def __init__(self, status="SHORT", stop=880.0):
        self.status, self.quantity, self.entry_price = status, 3, 870.0
        self.entry_source = "SHINDONG"
        self.stop_price = stop

    def is_stop_hit(self, px):
        return px <= self.stop_price if self.status == "LONG" else px >= self.stop_price


class _CB(object):
    state = "NORMAL"


class _Me(object):
    def __init__(self, px=None, stop=880.0):
        self.position = _Pos(stop=stop)
        self.circuit_breaker = _CB()
        self._pending_order = None
        self._tick_stop_triggered = False
        self._tick_stop_price = 0.0
        self._px = px
        self._alert_server_label = "Cybos 실서버(실계좌)"
        self._restart_stop_check = {"since": NOW, "kill": {"at": "2026-10-26 10:29:00", "pid": 4242},
                                    "noprice_alerted": False}

    def _peter2_last_price(self):
        return self._px

    def _process_tick_stop(self):
        pass


@pytest.fixture
def qt(monkeypatch):
    shots = []
    monkeypatch.setattr(main, "QTimer", types.SimpleNamespace(singleShot=lambda ms, fn: shots.append(fn)))
    monkeypatch.setattr(main, "is_market_open", lambda now: True)
    return shots


def test_11_손절선_밖이면_틱하드스톱_경로를_한번_예약(qt, mail):
    me = _Me(px=881.5)
    main._ts_restart_stop_check_tick(me, NOW + datetime.timedelta(seconds=40))
    assert len(qt) == 1 and me._tick_stop_triggered is True and me._tick_stop_price == 881.5
    assert me._restart_stop_check is None
    main._ts_restart_stop_check_tick(me, NOW + datetime.timedelta(seconds=42))
    assert len(qt) == 1, "판정은 1회다"


def test_12_손절선_안이면_주문없이_종료(qt, mail):
    me = _Me(px=875.0)
    main._ts_restart_stop_check_tick(me, NOW + datetime.timedelta(seconds=40))
    assert qt == [] and me._tick_stop_triggered is False and me._restart_stop_check is None


@pytest.mark.parametrize("label", ["triggered", "pending", "halted"])
def test_13_이미_청산중이거나_CB_HALT면_추가주문없음(qt, mail, label):
    me = _Me(px=881.5)
    if label == "triggered":
        me._tick_stop_triggered = True
    elif label == "pending":
        me._pending_order = {"kind": "EXIT_FULL", "qty": 3}
    else:
        me.circuit_breaker.state = main.CB_STATE_HALTED
    main._ts_restart_stop_check_tick(me, NOW + datetime.timedelta(seconds=40))
    assert qt == [] and me._restart_stop_check is None


def test_14_가격_미수신이면_S08_그리고_가격오면_해소_재판정(qt, mail):
    me = _Me(px=None)
    main._ts_restart_stop_check_tick(me, NOW + datetime.timedelta(seconds=30))
    assert mail == []
    main._ts_restart_stop_check_tick(me, NOW + datetime.timedelta(seconds=95))
    main._ts_restart_stop_check_tick(me, NOW + datetime.timedelta(seconds=120))
    assert len(mail) == 1 and mail[0][0].startswith("[긴급이상][MW0602][S-08] "), [s for s, _ in mail]
    assert "2026-10-26 10:29:00" in mail[0][1]
    me._px = 882.0
    main._ts_restart_stop_check_tick(me, NOW + datetime.timedelta(seconds=130))
    assert len(qt) == 1
    assert len(mail) == 2 and mail[1][0].startswith("[이상해소][MW0602][S-08] ")


def test_15_장밖에서는_기다리고_FLAT이면_종료(qt, mail, monkeypatch):
    me = _Me(px=None)
    monkeypatch.setattr(main, "is_market_open", lambda now: False)
    main._ts_restart_stop_check_tick(me, NOW + datetime.timedelta(seconds=300))
    assert mail == [] and me._restart_stop_check is not None
    me.position.status = "FLAT"
    main._ts_restart_stop_check_tick(me, NOW + datetime.timedelta(seconds=310))
    assert me._restart_stop_check is None and qt == []


def test_16_재판정_예외가_2초판정의_나머지를_막지_않는다(mail, monkeypatch):
    monkeypatch.setattr(main, "_ts_restart_stop_check_tick", lambda self, now: 1 / 0)
    called = []
    monkeypatch.setattr(main, "_ts_alert_stop_breach_tick", lambda self, now: called.append(1))
    me = _Me(px=870.0)
    me._exchange_cb_mode = False
    me._exit_reject_episode_at = None
    me._exit_limit_mode_reason = None
    main._ts_alert_state_tick(me, NOW)
    assert called == [1]
