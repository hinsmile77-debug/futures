# -*- coding: utf-8 -*-
"""[MW0601 2026-10-15] CREON 「종합계좌 비밀번호 확인 입력」 창 자동 처리.

2026-10-15 API+ 와 HTS 로그인 도중 이 창이 떴고 사람이 손으로 비밀번호를 넣어야
진행됐다. scripts/creon_acct_pw_dialog.py 가 그것을 대신한다. 여기서는 실제와 같은
구조의 Win32 창을 만들어 탐지 · 계좌 판독 · 입력 · 안전장치를 고정한다.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import creon_acct_pw_dialog as m  # noqa: E402

win32gui = pytest.importorskip("win32gui")
import win32con  # noqa: E402


@pytest.fixture
def fake_dialog():
    """실제 창과 같은 구성: 제목 · STATIC 「종합계좌번호 : 783293269」 · EDIT · BUTTON 「입력완료」."""
    hinst = win32gui.GetModuleHandle(None)
    top = win32gui.CreateWindowEx(0, "STATIC", u"종합계좌 비밀번호 확인 입력",
                                  win32con.WS_OVERLAPPEDWINDOW | win32con.WS_VISIBLE,
                                  0, 0, 400, 200, 0, 0, hinst, None)
    win32gui.CreateWindowEx(0, "STATIC", u"종합계좌번호 : 783293269",
                            win32con.WS_CHILD | win32con.WS_VISIBLE, 10, 10, 200, 20, top, 0, hinst, None)
    edit = win32gui.CreateWindowEx(0, "EDIT", u"", win32con.WS_CHILD | win32con.WS_VISIBLE,
                                   10, 40, 120, 20, top, 0, hinst, None)
    btn = win32gui.CreateWindowEx(0, "BUTTON", u"입력완료", win32con.WS_CHILD | win32con.WS_VISIBLE,
                                  10, 70, 80, 24, top, 0, hinst, None)
    m._HANDLED.clear()
    m._REPORTED_NO_PW.clear()
    yield top, edit, btn
    # DestroyWindow 는 메시지 루프 없는 STATIC 최상위 창에서 access violation 을 냈다(테스트 산물).
    # 탐지는 보이는 창만 보므로 숨기는 것으로 충분하다 — 프로세스 종료 때 정리된다.
    win32gui.ShowWindow(top, win32con.SW_HIDE)


def test_parse_account_variants():
    assert m.parse_account([u"종합계좌번호 : 783293269"]) == "783293269"
    assert m.parse_account([u"종합계좌번호：783-343908"]) == "783343908"
    assert m.parse_account([u"계좌 없음"]) is None


def test_find_dialog_reads_structure(fake_dialog):
    top, edit, btn = fake_dialog
    hits = [d for d in m.find_dialogs() if d[0] == top]
    assert hits, "실제 구조와 같은 창을 찾지 못했다"
    _, acct, e, b, pid, exe = hits[0]
    assert acct == "783293269" and e == edit and b == btn
    assert pid == os.getpid()


def test_refuses_window_not_owned_by_creon(fake_dialog, monkeypatch, tmp_path):
    """가짜 창(파이썬 프로세스 소유)에는 절대 입력하지 않는다."""
    top, edit, _ = fake_dialog
    monkeypatch.setattr(m, "password_for", lambda a: ("SECRETPW", "test"))
    log = str(tmp_path / "pw.log")
    assert m.handle_once(log_path=log, wait_close=0.1) == 0
    assert win32gui.GetWindowText(edit) == u""
    text = open(log, encoding="utf-8").read()
    assert "CREON/DAISHIN 이 아니다" in text and "SECRETPW" not in text


def test_types_password_once_and_never_logs_it(fake_dialog, monkeypatch, tmp_path):
    top, edit, _ = fake_dialog
    monkeypatch.setattr(m, "ALLOWED_EXE_ROOTS", (sys.executable.lower()[:3],))   # 이 프로세스를 허용
    monkeypatch.setattr(m, "password_for", lambda a: ("PW1234!", "test-src"))
    monkeypatch.setattr(m, "_submit", lambda d, e, b: "test")
    log = str(tmp_path / "pw.log")
    assert m.handle_once(log_path=log, wait_close=0.1) == 1
    assert win32gui.GetWindowText(edit) == u"PW1234!"
    # 같은 창에 두 번 입력하지 않는다 (계좌 잠김 방지)
    win32gui.SetWindowText(edit, u"")
    assert m.handle_once(log_path=log, wait_close=0.1) == 0
    assert win32gui.GetWindowText(edit) == u""
    text = open(log, encoding="utf-8").read()
    assert "PW1234!" not in text and "길이=7" in text and "783293269" in text
    assert "재입력하지 않는다" in text   # 창이 안 닫혔으니 불일치 경고가 남아야 한다


def test_missing_password_leaves_dialog_and_reports_once(fake_dialog, monkeypatch, tmp_path):
    top, edit, _ = fake_dialog
    monkeypatch.setattr(m, "ALLOWED_EXE_ROOTS", (sys.executable.lower()[:3],))
    monkeypatch.setattr(m, "password_for", lambda a: (None, None))
    log = str(tmp_path / "pw.log")
    m.handle_once(log_path=log)
    m.handle_once(log_path=log)
    text = open(log, encoding="utf-8").read()
    assert text.count("비밀번호 출처 없음") == 1
    assert "cmdkey /generic:CREON_ACCTPW_783293269" in text
    assert win32gui.GetWindowText(edit) == u""


def test_password_source_priority(monkeypatch):
    monkeypatch.setattr(m, "_cred_password", lambda a: "CRED" if a == "783293269" else None)
    monkeypatch.setattr(m, "_secrets_password", lambda a: "SEC" if a == "783343908" else None)
    assert m.password_for("783293269") == ("CRED", "자격증명 CREON_ACCTPW_783293269")
    assert m.password_for("783343908") == ("SEC", "secrets.ACCOUNT_PWD")
    assert m.password_for("111") == (None, None)


def test_wired_into_both_login_flows():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auto = open(os.path.join(root, "scripts", "cybos_autologin.py"), encoding="utf-8").read()
    real = auto[auto.index("def _creon_real_cmdline_login"):auto.index("def _autologin_impl")]
    assert "_acct_pw.handle_once()" in real, "API+ 실거래 로그인 대기 루프에 연결돼야 한다"
    ps1 = open(os.path.join(root, "scripts", "creon_autostart", "creon_start.ps1"), encoding="utf-8-sig").read()
    assert "creon_acct_pw_dialog.py" in ps1 and "Start-AcctPwWatcher" in ps1
    assert ps1.index("Start-AcctPwWatcher (") < ps1.index("Start-Process -FilePath $exe")
