# -*- coding: utf-8 -*-
"""[MW0602 596차 후속] 모의계좌 만료(2026-09-29) 후속 3건 회귀 가드.

1. 자동로그인이 브라우저 창을 브로커 팝업으로 오인하지 않는다.
   (재신청 페이지 '크레온-모의투자 - Chrome' 에 120초간 Enter 가 반복 전송됐다)
2. 런처 3종이 preflight 출력(CHECK 4/4 계좌목록)을 로그 파일에도 남긴다.
   (exit 4 로 멈춘 날 로그의 HINT 가 가리키는 계좌목록이 어디에도 없었다)
3. 체인 진단이 알려진 계좌 교체일을 불연속·종료코드에서 빼되 계속 표시한다.
"""
import io
import json
import os
import re
import sys
import contextlib

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_ROOT, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)


# ── 1. 브라우저 창 제외 ────────────────────────────────────────────────────
# cybos_autologin 은 import 만으로 진단 로그에 기록하고 stdout 을 가로채며 64-bit 면
# sys.exit 한다 — 그래서 import 하지 않고 필요한 정의만 AST 로 떼어 가짜 win32gui 로 돌린다.
_AL_NAMES = {"_normalize_title", "_BROWSER_EXES", "_is_browser_window",
             "_find_window_by_keywords", "_BROWSER_SKIP_LOGGED", "_log_browser_skips",
             "MOCK_DIALOG_KEYWORDS"}


def _load_autologin_subset(win32gui, proc_names):
    import ast
    src = open(os.path.join(_SCRIPTS, "cybos_autologin.py"), "rb").read().decode("utf-8")
    tree = ast.parse(src)
    keep = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in _AL_NAMES:
            keep.append(node)
        elif isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) in _AL_NAMES for t in node.targets):
            keep.append(node)
    mod = ast.Module(body=keep, type_ignores=[])
    ns = {"win32gui": win32gui,
          "_window_process_name": lambda h: proc_names.get(h)}
    exec(compile(mod, "cybos_autologin_subset", "exec"), ns)
    assert _AL_NAMES <= set(ns), "정의가 사라졌다: %s" % (_AL_NAMES - set(ns))
    return ns


class _FakeWin32Gui(object):
    def __init__(self, wins):
        self.wins = wins

    def EnumWindows(self, cb, extra):
        for h in self.wins:
            cb(h, extra)

    def IsWindowVisible(self, h):
        return True

    def GetWindowText(self, h):
        return self.wins[h]


def test_1_keyword_finder_skips_browser_windows(capsys):
    wins = {
        101: u"크레온-모의투자 - Chrome",
        102: u"모의투자 선택",
        103: u"모의투자 안내 - Microsoft Edge",
        104: u"CREON 모의투자 접속",
    }
    procs = {101: "chrome.exe", 102: "costarter.exe", 103: "msedge.exe",
             104: None}   # 조회 실패(권한) → 브라우저로 보지 않는다(보수적으로 후보 유지)
    ns = _load_autologin_subset(_FakeWin32Gui(wins), procs)

    found = dict(ns["_find_window_by_keywords"](ns["MOCK_DIALOG_KEYWORDS"]))
    assert 101 not in found and 103 not in found
    assert 102 in found and 104 in found

    # 제외는 기록하되 제목당 1회 (매초 루프 스팸 방지)
    ns["_find_window_by_keywords"](ns["MOCK_DIALOG_KEYWORDS"])
    out = capsys.readouterr().out
    assert out.count(u"크레온-모의투자 - Chrome") == 1


def test_1b_browser_exe_list_covers_common_browsers():
    ns = _load_autologin_subset(_FakeWin32Gui({}), {})
    for exe in ("chrome.exe", "msedge.exe", "firefox.exe", "whale.exe"):
        assert exe in ns["_BROWSER_EXES"]


def test_1c_small_popup_scan_also_filters_browsers():
    src = open(os.path.join(_SCRIPTS, "cybos_autologin.py"), "rb").read().decode("utf-8")
    i = src.index(u'if u"모의투자" in t or u"선택" in t:')
    assert "_is_browser_window(h)" in src[i:i + 300]


# ── 2. 런처 preflight 출력 캡처 ─────────────────────────────────────────────
@pytest.mark.parametrize("bat,logvar", [
    ("start_mireuk.bat", "_BLOG"),
    ("start_mireuk_CREON.bat", "_BLOG"),
    ("LAUNCH_API.bat", "LOG"),
])
def test_2_launcher_tees_preflight_output(bat, logvar):
    text = open(os.path.join(_ROOT, bat), "rb").read().decode("utf-8")
    call = re.search(r'^\s*\S+ "!WORKDIR!\\scripts\\cybos_plus_preflight\.py"(.*)$',
                     text, re.M)
    assert call, "preflight 호출을 못 찾음"
    assert '> "!_PF_OUT!" 2>&1' in call.group(1), "preflight 출력이 파일로 가지 않는다"
    after = text[call.end():call.end() + 600]
    assert "SET \"PREFLIGHT_ERR=!ERRORLEVEL!\"" in after
    assert 'TYPE "!_PF_OUT!" >> "!%s!"' % logvar in after
    # 이 호출에만 UTF-8 을 강제하고 복원한다
    assert 'SET "PYTHONIOENCODING=!_PF_OLDENC!"' in after


# ── 3. 체인 진단: 알려진 계좌 교체 ──────────────────────────────────────────
def test_3_known_account_switch_excluded_but_shown(monkeypatch):
    import broker_net_chain_audit as m
    rows = {
        "2026-09-26": (29600000.0, 29559527.0, -40473.0, 0.0),
        "2026-09-28": (29559527.0, 29521102.0, -38425.0, 0.0),
        "2026-09-29": (30000000.0, 30010000.0, 10000.0, 12000.0),
    }
    monkeypatch.setattr(m, "_db_rows", lambda: rows)
    monkeypatch.setattr(m, "_traded_dates", lambda: set())
    monkeypatch.setattr(m, "_iter_log_days", lambda: iter(()))
    monkeypatch.setattr(m, "KNOWN_ACCOUNT_SWITCHES", {"2026-09-29": "테스트 교체"})

    monkeypatch.setattr(sys, "argv", ["x", "--json"])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.main()
    j = json.loads(buf.getvalue())
    assert j["chain_breaks"] == []
    assert [s["date"] for s in j["known_account_switches"]] == ["2026-09-29"]
    assert rc == 0

    # 텍스트 출력은 로그 표본이 있어야 D2 까지 간다 — 하루치 가짜 로그를 준다
    monkeypatch.setattr(m, "_iter_log_days", lambda: iter([("20260929", ["x"])]))
    monkeypatch.setattr(m, "_parse_day", lambda lines: ([("09:01:56", 0, 30000000.0,
                                                           30010000.0)], 0))
    monkeypatch.setattr(m, "_split_rollover", lambda rows: (rows, []))
    monkeypatch.setattr(m, "_guard_present", lambda: True)
    monkeypatch.setattr(sys, "argv", ["x"])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        m.main()
    out = buf.getvalue()
    assert "알려진 계좌 교체 1건" in out and "테스트 교체" in out


def test_3b_unregistered_break_still_red(monkeypatch):
    import broker_net_chain_audit as m
    rows = {
        "2026-09-28": (29559527.0, 29521102.0, -38425.0, 0.0),
        "2026-09-29": (30000000.0, 30010000.0, 10000.0, 12000.0),
    }
    monkeypatch.setattr(m, "_db_rows", lambda: rows)
    monkeypatch.setattr(m, "_traded_dates", lambda: set())
    monkeypatch.setattr(m, "_iter_log_days", lambda: iter(()))
    monkeypatch.setattr(m, "KNOWN_ACCOUNT_SWITCHES", {})
    monkeypatch.setattr(sys, "argv", ["x", "--json"])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.main()
    assert len(json.loads(buf.getvalue())["chain_breaks"]) == 1
    assert rc == 1
