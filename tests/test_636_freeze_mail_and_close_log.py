# -*- coding: utf-8 -*-
"""[MW0602 636차] F-1009 동결 경보 메일 · G-1i closeEvent 진입/결과 로그.

## F-1009 — 고정하는 규약
1. 제목 형식 `[긴급이상][<PC>] …` / `[이상해소][<PC>] …` (사용자 지정, 신동 일일리포트 형식).
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
    assert s.startswith("[긴급이상][MW0602] ")
    assert "동결" in s and "5분" in s and "10:32" in s
    assert "15:10" in b and "HTS" in b          # 사람이 할 일이 본문에 있다
    assert "SYSTEM.log 400s 전 — 정체" in b      # 판정 근거가 그대로 실린다


def test_2_회복_제목_형식과_지속시간():
    s, b = FS.build_recovery_mail("MW0602", _NOW, _NOW + datetime.timedelta(minutes=9))
    assert s.startswith("[이상해소][MW0602] ")
    assert "10:41" in s and "(9분간)" in s
    s2, _ = FS.build_recovery_mail("MW0602", None, _NOW)
    assert "분간" not in s2                      # 경보 시각 미측정이면 지어내지 않는다


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
                        lambda root, day, s, b, sender=None: sent.append(s))
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
                        lambda root, day, s, b, sender=None: sent.append(s))
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


def test_6_수동_once_는_메일을_보내지_않는다():
    src = io.open(FS.__file__, encoding="utf-8").read()
    once = src.split("if args.once or args.at_time:", 1)[1].split("log_armed(", 1)[0]
    assert "send_mail_async" not in once


def test_7_설정_기본값():
    from config import settings as st
    assert st.FREEZE_SENTINEL_MAIL_ENABLED is True
    assert st.FREEZE_SENTINEL_KILL_ENABLED is False   # 메일 추가가 하드 종료 승격이 아니다


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
