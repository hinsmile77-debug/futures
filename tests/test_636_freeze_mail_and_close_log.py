# -*- coding: utf-8 -*-
"""[MW0602 636차] F-1009 동결 경보 메일 · G-1i closeEvent 진입/결과 로그.

## F-1009 — 고정하는 규약
1. 제목 형식 `[긴급이상][<PC>][S-04] …` / `[이상해소][<PC>][S-04] … — 지속 N분`
   (사용자 지정, 신동 일일리포트 형식 · 2026-10-17 긴급 알림 카탈로그 코드 S-04 부착).
5. [2026-10-17] 메일과 Slack 을 함께 보낸다(`slack_too`). [메일] 꺼짐은 실패로 알리지 않는다.
6. [2026-10-17 / S-05] 장전 미기동 — 판정 시각 이후 **오늘 SYSTEM.log 없음** 이면 1통,
   생기면 해소 1통. 그 에피소드가 열린 동안은 동결(S-04) 메일을 따로 보내지 않는다.
2. **동결 1회당 1통** — 같은 동결의 반복 주기에는 보내지 않는다(팝업과 같은 경보 피로 규칙).
   회복 시 1통. 수동 `--once` 진단은 보내지 않는다.
3. 발송 실패가 센티넬을 멈추지 않고, 실패는 로그 한 줄로 남는다(계측 4원칙 ④).
4. 메일은 **알림 전용**이다 — 판정(`judge`) 결과를 바꾸지 않는다.

## G-1i — 고정하는 규약
1. `closeEvent` 가 확인창(`exec_`) **전에** 진입 줄을, **후에** 결과 줄을 남긴다.
2. 두 로깅은 try 로 감싼다 — Qt 가상 메서드 안 예외는 프로세스를 죽인다(557차 후속3).
3. 모듈 상단에 `import time` 이 없으므로 closeEvent 안에서 맨 `time.` 을 쓰면 안 된다
   (실제로 초안이 그렇게 썼다 — NameError 가 곧 대시보드 즉사였다).
"""
import ast
import datetime
import io
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.join(_ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import freeze_sentinel as FS  # noqa: E402

_NOW = datetime.datetime(2026, 10, 19, 10, 32, 5)
_FROZEN = {"level": "CRITICAL", "rc": FS.RC_FROZEN, "state": "FROZEN",
           "headline": "라이브 프로세스 동결", "details": ["SYSTEM.log 400s 전 — 정체"],
           "stale": ["SYSTEM.log"], "unmeasured": []}
_OK = {"level": "OK", "rc": FS.RC_OK, "state": "WATCHING", "headline": "정상",
       "details": [], "stale": [], "unmeasured": []}


# ── F-1009 순수 함수 ───────────────────────────────────────────────────────

def test_1_경보_제목_형식():
    s, b = FS.build_alert_mail(_FROZEN, "MW0602", _NOW, 300.0)
    assert s.startswith("[긴급이상][MW0602][S-04] ")
    assert "동결" in s and "5분" in s and "10:32" in s
    assert "15:10" in b and "HTS" in b          # 사람이 할 일이 본문에 있다
    assert "SYSTEM.log 400s 전 — 정체" in b      # 판정 근거가 그대로 실린다


def test_2_회복_제목_형식과_지속시간():
    s, b = FS.build_recovery_mail("MW0602", _NOW, _NOW + datetime.timedelta(minutes=9))
    assert s.startswith("[이상해소][MW0602][S-04] ")
    assert "10:41" in s and s.endswith("— 지속 9분") and "(9분간)" in b
    s2, b2 = FS.build_recovery_mail("MW0602", None, _NOW)
    assert "지속" not in s2 and "분간" not in b2   # 경보 시각 미측정이면 지어내지 않는다


def test_3_발송_성공과_실패가_로그에_남고_예외가_새지_않는다(tmp_path):
    day = _NOW.date()
    FS.send_mail_async(str(tmp_path), day, "S1", "B", sender=lambda s, b: ["x@y"]).join(5)

    def _boom(s, b):
        raise RuntimeError("SMTP 미설정: MIREUK_SMTP_USER")
    FS.send_mail_async(str(tmp_path), day, "S2", "B", sender=_boom).join(5)
    log = io.open(os.path.join(str(tmp_path), "logs",
                               "freeze_sentinel_%s.log" % day.strftime("%Y%m%d")),
                  encoding="utf-8").read()
    assert "메일 발송 성공 → x@y | S1" in log
    assert "메일 발송 실패(RuntimeError" in log and "| S2" in log


# ── F-1009 감시 루프: 동결 1회당 1통 + 회복 1통 ─────────────────────────────

class _Stop(Exception):
    pass


def test_4_루프는_동결당_한_통_회복당_한_통(monkeypatch, tmp_path):
    seq = [_FROZEN, _FROZEN, _FROZEN, _OK, _OK, _FROZEN]
    it = iter(seq)
    sent = []

    monkeypatch.setattr(FS, "judge", lambda *a, **k: next(it))
    monkeypatch.setattr(FS, "collect", lambda *a, **k: {})
    monkeypatch.setattr(FS, "_in_window", lambda now, w: True)
    # v9-dev 의 상주 센티넬 단일 인스턴스 잠금 — 테스트가 실제 뮤텍스를 잡지 않게(dev 엔 없음)
    monkeypatch.setattr(FS, "_acquire_single_instance", lambda: True, raising=False)
    monkeypatch.setattr(FS, "_pc_id", lambda: "MW0602")
    monkeypatch.setattr(FS, "_popup", lambda v: None)
    monkeypatch.setattr(FS, "send_mail_async",
                        lambda root, day, s, b, sender=None, **k: sent.append(s))
    # [S-05] 장전 감시는 이 테스트 대상이 아니다 — 실제 상태 파일·발송을 건드리지 않게
    monkeypatch.setattr(FS.PremarketWatch, "tick", lambda self, now: "OK")
    cfg = {"FREEZE_SENTINEL_ENABLED": True, "FREEZE_SENTINEL_MAIL_ENABLED": True,
           "FREEZE_SENTINEL_MAIL_RECOVERY": True, "FREEZE_SENTINEL_KILL_ENABLED": False,
           "FREEZE_SENTINEL_POPUP": False}
    monkeypatch.setattr(FS, "_cfg", lambda n, d: cfg.get(n, d))
    import utils.time_utils as tu
    monkeypatch.setattr(tu, "is_trading_day", lambda now: True)
    calls = {"n": 0}

    def _sleep(_):
        calls["n"] += 1
        if calls["n"] >= len(seq):
            raise _Stop()
    monkeypatch.setattr(FS.time, "sleep", _sleep)

    with pytest.raises(_Stop):
        FS.main(["--root", str(tmp_path), "--no-popup"])
    tags = [s.split("]")[0] + "]" for s in sent]
    assert all("[MW0602][S-04] " in s for s in sent), sent
    assert tags == ["[긴급이상]", "[이상해소]", "[긴급이상]"], sent


def test_5_메일_꺼지면_보내지_않는다(monkeypatch, tmp_path):
    it = iter([_FROZEN, _OK])
    sent = []
    monkeypatch.setattr(FS, "judge", lambda *a, **k: next(it))
    monkeypatch.setattr(FS, "collect", lambda *a, **k: {})
    monkeypatch.setattr(FS, "_in_window", lambda now, w: True)
    # v9-dev 의 상주 센티넬 단일 인스턴스 잠금 — 테스트가 실제 뮤텍스를 잡지 않게(dev 엔 없음)
    monkeypatch.setattr(FS, "_acquire_single_instance", lambda: True, raising=False)
    monkeypatch.setattr(FS, "send_mail_async",
                        lambda root, day, s, b, sender=None, **k: sent.append(s))
    # [S-05] 장전 감시는 이 테스트 대상이 아니다 — 실제 상태 파일·발송을 건드리지 않게
    monkeypatch.setattr(FS.PremarketWatch, "tick", lambda self, now: "OK")
    cfg = {"FREEZE_SENTINEL_MAIL_ENABLED": False, "FREEZE_SENTINEL_POPUP": False}
    monkeypatch.setattr(FS, "_cfg", lambda n, d: cfg.get(n, d))
    import utils.time_utils as tu
    monkeypatch.setattr(tu, "is_trading_day", lambda now: True)
    calls = {"n": 0}

    def _sleep(_):
        calls["n"] += 1
        if calls["n"] >= 2:
            raise _Stop()
    monkeypatch.setattr(FS.time, "sleep", _sleep)
    with pytest.raises(_Stop):
        FS.main(["--root", str(tmp_path), "--no-popup"])
    assert sent == []


def test_3b_슬랙_병행과_메일실패_슬랙통보(tmp_path):
    day = _NOW.date()
    sl = []
    FS.send_mail_async(str(tmp_path), day, "[긴급이상][P][S-04] x", "B",
                       sender=lambda s, b: ["x@y"], slack_too=True,
                       slack=lambda t, lv: sl.append((t, lv))).join(5)
    assert sl == [("[긴급이상][P][S-04] x", "CRITICAL")]

    class MailDisabled(RuntimeError):
        pass

    def _off(s, b):
        raise MailDisabled("off")

    def _boom(s, b):
        raise OSError("smtp down")
    sl2 = []
    FS.send_mail_async(str(tmp_path), day, "[이상해소][P][S-04] y", "B", sender=_off,
                       slack_too=True, slack=lambda t, lv: sl2.append((t, lv))).join(5)
    assert sl2 == [("[이상해소][P][S-04] y", "INFO")], "[메일] 꺼짐은 실패 통보 없음"
    sl3 = []
    FS.send_mail_async(str(tmp_path), day, "[긴급이상][P][S-04] z", "B", sender=_boom,
                       slack_too=True, slack=lambda t, lv: sl3.append((t, lv))).join(5)
    assert len(sl3) == 2 and "메일 발송 실패(OSError)" in sl3[1][0]
    sl4 = []
    FS.send_mail_async(str(tmp_path), day, "S", "B", sender=lambda s, b: [],
                       slack=lambda t, lv: sl4.append(t)).join(5)
    assert sl4 == [], "slack_too 가 꺼져 있으면 Slack 없음"


# ── S-05 장전 미기동 ───────────────────────────────────────────────────────

def _pm(tmp_path):
    from utils import alert_mail as AM
    mails = []
    m = AM.AlertMailer(state_dir=str(tmp_path / "st"), pc="MW0602",
                       sender=lambda s, b: mails.append(s) or ["x@y"],
                       slack=lambda *a: None, enabled=True, threaded=False, proc="sentinel")
    return FS.PremarketWatch(str(tmp_path), datetime.time(8, 52), mailer=m), m, mails


def test_10_장전_미기동은_한통_기동되면_해소_한통(tmp_path):
    w, m, mails = _pm(tmp_path)
    t0 = datetime.datetime(2026, 10, 19, 8, 50)
    assert w.tick(t0) == "BEFORE"
    t1 = datetime.datetime(2026, 10, 19, 8, 55)
    m._clock = lambda: t1
    assert w.tick(t1) == "RAISED"
    assert w.tick(t1) == "OPEN" and len(mails) == 1
    assert mails[0].startswith("[긴급이상][MW0602][S-05] ")
    os.makedirs(os.path.join(str(tmp_path), "logs"))
    io.open(os.path.join(str(tmp_path), "logs", "20261019_SYSTEM.log"), "w").close()
    t2 = datetime.datetime(2026, 10, 19, 9, 7)
    m._clock = lambda: t2
    assert w.tick(t2) == "RESOLVED"
    assert mails[1].startswith("[이상해소][MW0602][S-05] ") and mails[1].endswith("지속 12분")
    assert w.tick(t2) == "OK" and len(mails) == 2


def test_11_어제_로그는_기동으로_보지_않는다(tmp_path):
    w, m, mails = _pm(tmp_path)
    os.makedirs(os.path.join(str(tmp_path), "logs"))
    io.open(os.path.join(str(tmp_path), "logs", "20261016_SYSTEM.log"), "w").close()
    t = datetime.datetime(2026, 10, 19, 8, 56)
    m._clock = lambda: t
    assert w.not_started(t) and w.tick(t) == "RAISED"


def test_12_미기동_에피소드_중에는_동결메일을_따로_보내지_않는다(monkeypatch, tmp_path):
    it = iter([_FROZEN, _FROZEN])
    sent = []
    monkeypatch.setattr(FS, "judge", lambda *a, **k: next(it))
    monkeypatch.setattr(FS, "collect", lambda *a, **k: {})
    monkeypatch.setattr(FS, "_in_window", lambda now, w: True)
    monkeypatch.setattr(FS, "_acquire_single_instance", lambda: True, raising=False)
    monkeypatch.setattr(FS, "_pc_id", lambda: "MW0602")
    monkeypatch.setattr(FS, "_popup", lambda v: None)
    monkeypatch.setattr(FS, "send_mail_async",
                        lambda root, day, s, b, sender=None, **k: sent.append(s))
    monkeypatch.setattr(FS.PremarketWatch, "tick", lambda self, now: "OPEN")
    cfg = {"FREEZE_SENTINEL_ENABLED": True, "FREEZE_SENTINEL_MAIL_ENABLED": True,
           "FREEZE_SENTINEL_POPUP": False}
    monkeypatch.setattr(FS, "_cfg", lambda n, d: cfg.get(n, d))
    import utils.time_utils as tu
    monkeypatch.setattr(tu, "is_trading_day", lambda now: True)
    calls = {"n": 0}

    def _sleep(_):
        calls["n"] += 1
        if calls["n"] >= 2:
            raise _Stop()
    monkeypatch.setattr(FS.time, "sleep", _sleep)
    with pytest.raises(_Stop):
        FS.main(["--root", str(tmp_path), "--no-popup"])
    assert sent == []


def test_6_수동_once_는_메일을_보내지_않는다():
    src = io.open(FS.__file__, encoding="utf-8").read()
    once = src.split("if args.once or args.at_time:", 1)[1].split("log_armed(", 1)[0]
    assert "send_mail_async" not in once


def test_7_설정_기본값():
    from config import settings as st
    assert st.FREEZE_SENTINEL_MAIL_ENABLED is True
    # [MW0602 2026-10-24] 2단계(보유 중 동결 강제 재기동)는 사용자 결정으로 별도 승격됐다 —
    #   메일 설정과 무관하다(tests/test_mw0602_freeze_kill_restart.py 가 고정).
    assert st.FREEZE_SENTINEL_KILL_ENABLED is True


# ── G-1i closeEvent ────────────────────────────────────────────────────────

def _close_event_src():
    path = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
    src = io.open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "MireukDashboard":
            for fn in node.body:
                if isinstance(fn, ast.FunctionDef) and fn.name == "closeEvent":
                    lines = src.splitlines()
                    return "\n".join(lines[fn.lineno - 1:fn.body[-1].end_lineno]) \
                        if hasattr(fn.body[-1], "end_lineno") else \
                        src[src.index("    def closeEvent(self, event):\n        \"\"\"메인 윈도우"):]
    raise AssertionError("MireukDashboard.closeEvent 를 찾지 못했다")


def test_8_진입줄은_확인창_전_결과줄은_후():
    s = _close_event_src()
    i_enter = s.index("[CloseEvent] 진입")
    i_exec = s.index("_dlg.exec_()")
    i_result = s.index("[CloseEvent] 확인창 결과=")
    assert i_enter < i_exec < i_result
    assert "spontaneous" in s                     # 사람(X 버튼)·코드(close()) 구분 비트


def test_9_closeEvent_로깅은_감싸져_있고_맨_time_을_쓰지_않는다():
    s = _close_event_src()
    # 모듈 상단에 import time 이 없다 — 맨 `time.` 은 NameError → 대시보드 즉사
    assert not re.search(r"(?<![\w.])time\.time\(", s), "closeEvent 안 맨 time.time()"
    for tag in ("[CloseEvent] 진입", "[CloseEvent] 확인창 결과="):
        head = s[:s.index(tag)]
        assert head.rstrip().split("\n")[-1].strip().startswith(("try:", "logger.info(")), tag
        assert head.rfind("try:") > head.rfind("except Exception:"), tag + " 가 try 밖이다"
