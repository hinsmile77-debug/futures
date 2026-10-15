# -*- coding: utf-8 -*-
"""CREON 「종합계좌 비밀번호 확인 입력」 창 자동 처리 — API+(cybos_autologin) · HTS(creon_start) 공용.

[MW0601 2026-10-15] 배경
    로그인 창의 「주문/조회 계좌비밀번호 자동입력」을 처음 쓰거나, 비밀번호 변경·신규등록
    뒤에는 로그인 도중 이 창이 뜬다. 2026-10-15 13:45 HTS(Smart1na, 783293269)와
    14:xx API+ 에서 실제로 떴고, 둘 다 사람이 손으로 비밀번호를 넣고 Enter 를 쳐야
    진행됐다. 언제 뜨는지 예측이 안 되므로(사용자 확인) 로그인 대기 루프가 매 주기
    이 창을 찾아 처리한다.

    창 구성(2026-10-15 화면): 제목 「종합계좌 비밀번호 확인 입력」, 본문에
    「종합계좌번호 : 783293269」, 비밀번호 입력란 1개, 버튼 「입력완료」 / 「취 소」.

비밀번호 출처 (우선순위)
    1. Windows 자격 증명(일반) ``CREON_ACCTPW_<계좌번호>`` — 계좌마다 하나.
       등록: ``cmdkey /generic:CREON_ACCTPW_783293269 /user:783293269 /pass:<비번>``
    2. 창의 계좌가 ``config/secrets.py`` 의 ``ACCOUNT_NO`` 와 같으면 ``ACCOUNT_PWD``.
    둘 다 없으면 입력하지 않고 ERROR 로 남긴다(사람이 처리).

안전장치
    · 창 소유 프로세스가 ``C:\\CREON\\`` 또는 ``C:\\DAISHIN\\`` 아래 실행파일일 때만 입력한다.
    · 같은 창(hwnd)에는 **한 번만** 입력한다 — 틀린 비밀번호 반복은 계좌 잠김으로 이어진다.
    · 비밀번호 값은 어디에도 출력하지 않는다(길이만).

CLI (creon_start.ps1 이 HTS 로그인 동안 백그라운드로 돌린다)
    python creon_acct_pw_dialog.py --watch 600 [--log 경로]
"""
from __future__ import print_function

import argparse
import datetime
import os
import re
import sys
import time

TITLE_KEY = u"종합계좌 비밀번호 확인"
SUBMIT_TEXTS = (u"입력완료", u"입력 완료", u"확인")
CRED_PREFIX = "CREON_ACCTPW_"
ALLOWED_EXE_ROOTS = ("c:\\creon\\", "c:\\daishin\\")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HANDLED = set()          # 이미 입력을 시도한 창 hwnd — 다시 입력하지 않는다
_REPORTED_NO_PW = set()   # 비밀번호 없음을 이미 보고한 (hwnd)


def _log(msg, log_path=None):
    # 콘솔에는 시각을 붙이지 않는다 — 호출자(cybos_autologin 진단 로그)가 이미 붙인다.
    line = "[AcctPw] %s" % msg
    # cp949 콘솔은 em dash(—) 등을 못 쓴다 — 출력 실패로 처리기가 죽으면 창이 그대로
    # 남는다(force_flat_guard 478차 후속 §8-2 와 같은 함정). 콘솔은 대체 문자로, 파일은 UTF-8 원문으로.
    try:
        print(line)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(line.encode(enc, "replace").decode(enc, "replace"))
    try:
        sys.stdout.flush()
    except Exception:
        pass
    if log_path:
        try:
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + line + "\n")
        except Exception:
            pass


# ── 창 탐지 ──────────────────────────────────────────────────────────────────

def _children(hwnd):
    import win32gui
    out = []
    try:
        win32gui.EnumChildWindows(hwnd, lambda h, _: out.append(h) or True, None)
    except Exception:
        pass
    return out


def _owner_exe(hwnd):
    import win32process
    import psutil
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid, (psutil.Process(pid).exe() or "")
    except Exception:
        return None, ""


def parse_account(texts):
    """창 안 문구들에서 계좌번호를 뽑는다. 「종합계좌번호 : 783293269」 형태."""
    joined = u" ".join(t for t in texts if t)
    m = re.search(u"종합계좌번호\\s*[:：]?\\s*([0-9][0-9\\-]{6,14})", joined)
    if not m:
        m = re.search(u"\\b([0-9]{8,11})\\b", joined)
    return re.sub(u"[^0-9]", u"", m.group(1)) if m else None


def find_dialogs():
    """보이는 「종합계좌 비밀번호 확인 입력」 창 목록 — [(hwnd, account, edit, submit_btn, pid, exe)]."""
    import win32gui
    found = []

    def _enum(h, _):
        try:
            if not win32gui.IsWindowVisible(h):
                return True
            if TITLE_KEY not in (win32gui.GetWindowText(h) or u""):
                return True
            kids = _children(h)
            texts = [win32gui.GetWindowText(k) for k in kids]
            edits = [k for k in kids if win32gui.GetClassName(k).lower() == "edit"
                     and win32gui.IsWindowVisible(k)]
            btns = [k for k in kids if win32gui.GetClassName(k) == "Button"
                    and (win32gui.GetWindowText(k) or u"").replace(u"&", u"").strip() in SUBMIT_TEXTS]
            pid, exe = _owner_exe(h)
            found.append((h, parse_account(texts), edits[0] if edits else None,
                          btns[0] if btns else None, pid, exe))
        except Exception:
            pass
        return True
    try:
        win32gui.EnumWindows(_enum, None)
    except Exception:
        pass
    return found


# ── 비밀번호 출처 ────────────────────────────────────────────────────────────

def _cred_password(account):
    try:
        import win32cred
        c = win32cred.CredRead(CRED_PREFIX + account, win32cred.CRED_TYPE_GENERIC)
        blob = c.get("CredentialBlob") or b""
        try:
            return blob.decode("utf-16-le")
        except Exception:
            return blob.decode("utf-8", "ignore")
    except Exception:
        return None


def _secrets_password(account):
    try:
        if _ROOT not in sys.path:
            sys.path.insert(0, _ROOT)
        from config import secrets as _s
        acc = re.sub(r"[^0-9]", "", str(getattr(_s, "ACCOUNT_NO", "") or ""))
        pw = getattr(_s, "ACCOUNT_PWD", "") or ""
        if acc and acc == account and pw:
            return pw
    except Exception:
        pass
    return None


def password_for(account):
    """(비밀번호, 출처이름) — 없으면 (None, None)."""
    if not account:
        return None, None
    pw = _cred_password(account)
    if pw:
        return pw, "자격증명 %s%s" % (CRED_PREFIX, account)
    pw = _secrets_password(account)
    if pw:
        return pw, "secrets.ACCOUNT_PWD"
    return None, None


# ── 입력 ─────────────────────────────────────────────────────────────────────

def _type_into(edit, text):
    """WM_SETTEXT 로 넣고, 보호 입력란이라 안 들어갔으면 포커스 + 키 입력으로 넣는다."""
    import win32api
    import win32con
    import win32gui
    win32gui.SendMessage(edit, win32con.WM_SETTEXT, 0, text)
    if win32gui.SendMessage(edit, win32con.WM_GETTEXTLENGTH, 0, 0) == len(text):
        return "WM_SETTEXT"
    top = win32gui.GetAncestor(edit, win32con.GA_ROOT)
    try:
        win32gui.SetForegroundWindow(top)
    except Exception:
        pass
    win32gui.SendMessage(edit, win32con.WM_SETFOCUS, 0, 0)
    for ch in text:
        win32gui.SendMessage(edit, win32con.WM_CHAR, ord(ch), 0)
        time.sleep(0.03)
    return "WM_CHAR"


def _submit(dlg, edit, btn):
    import win32con
    import win32gui
    if btn:
        win32gui.PostMessage(btn, win32con.BM_CLICK, 0, 0)
        return "입력완료 버튼"
    win32gui.PostMessage(edit, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32gui.PostMessage(edit, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    return "Enter"


def handle_once(log_path=None, wait_close=6.0):
    """보이는 창을 한 번 훑어 처리한다. 반환: 이번에 비밀번호를 입력한 창 수."""
    import win32gui
    n = 0
    for dlg, acct, edit, btn, pid, exe in find_dialogs():
        if dlg in _HANDLED:
            continue
        if not exe.lower().startswith(ALLOWED_EXE_ROOTS):
            _HANDLED.add(dlg)
            _log("[ERROR] 비밀번호 창 소유 프로세스가 CREON/DAISHIN 이 아니다(pid=%s exe=%s) — 입력 안 함"
                 % (pid, exe or "?"), log_path)
            continue
        if not acct or edit is None:
            _HANDLED.add(dlg)
            _log("[ERROR] 비밀번호 창 구성 판독 실패(계좌=%s, 입력란=%s) — 사람이 처리"
                 % (acct, "있음" if edit else "없음"), log_path)
            continue
        pw, src = password_for(acct)
        if not pw:
            if dlg not in _REPORTED_NO_PW:
                _REPORTED_NO_PW.add(dlg)
                _log("[ERROR] 계좌 %s 비밀번호 출처 없음 — 등록: cmdkey /generic:%s%s /user:%s /pass:<비번> "
                     "(창은 그대로 둔다)" % (acct, CRED_PREFIX, acct, acct), log_path)
            continue
        _HANDLED.add(dlg)   # 입력 전에 표시 — 실패해도 같은 창에 다시 넣지 않는다
        how = _type_into(edit, pw)
        time.sleep(0.2)
        sub = _submit(dlg, edit, btn)
        _log("계좌 %s 비밀번호 확인 창 처리: 출처=%s 길이=%d 입력=%s 제출=%s (pid=%s %s)"
             % (acct, src, len(pw), how, sub, pid, os.path.basename(exe)), log_path)
        n += 1
        end = time.time() + wait_close
        while time.time() < end and win32gui.IsWindow(dlg) and win32gui.IsWindowVisible(dlg):
            time.sleep(0.3)
        if win32gui.IsWindow(dlg) and win32gui.IsWindowVisible(dlg):
            _log("[ERROR] 제출 후 %.0f초가 지나도 창이 남아 있다 — 비밀번호 불일치 가능. "
                 "재입력하지 않는다(계좌 잠김 방지)" % wait_close, log_path)
        else:
            _log("계좌 %s 비밀번호 확인 창 닫힘 — 로그인 계속" % acct, log_path)
    return n


def watch(seconds, log_path=None, interval=1.0):
    end = time.time() + seconds
    total = 0
    while time.time() < end:
        total += handle_once(log_path)
        time.sleep(interval)
    return total


def main(argv=None):
    ap = argparse.ArgumentParser(description="CREON 종합계좌 비밀번호 확인 창 자동 처리")
    ap.add_argument("--watch", type=float, default=0, help="이 시간(초) 동안 감시. 0이면 1회만")
    ap.add_argument("--log", default=None, help="처리 결과를 덧붙일 로그 파일")
    args = ap.parse_args(argv)
    if args.watch > 0:
        n = watch(args.watch, args.log)
    else:
        n = handle_once(args.log)
    return 0 if n >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
