# -*- coding: utf-8 -*-
"""
CybosPlus 자동 로그인 스크립트 (윈도우 컨트롤 기반)
- 절대 마우스 좌표를 전혀 사용하지 않고, 대상 창의 자식 컨트롤을 찾아 조작
- 다른 창이 떠 있거나 모니터 해상도가 달라도 관계없이 동작
- Windows Credential Manager에서 비밀번호를 읽어 로그인 창을 자동 조작
- 사전 준비: cmdkey /add:cybosplus /user:아이디 /pass:비밀번호 (1회)
- 의존: pywinauto, pywin32, psutil

시작 순서:
  1. _ncStarter_.exe 실행
  2. "CYBOS" 보안프로그램 다이얼로그 -> "사용안함" 클릭 (자동)
  3. "CYBOS Starter" 로그인 창 -> Edit 컨트롤 찾아 비밀번호 입력 + Button 찾아 로그인
  4. "모의투자 선택" 창 -> "모의투자 접속" 버튼 컨트롤 클릭 (MOCK_MODE=True)
"""
import sys
import struct
import time
import subprocess
import os
import ctypes
import ctypes.wintypes

# 32-bit Python 필수 (Cybos COM은 32-bit 전용)
if struct.calcsize("P") != 4:
    print("[ERROR] 32-bit Python 필요 -- 현재 %d-bit" % (struct.calcsize("P") * 8))
    print("[ERROR] 'conda activate py37_32' 후 재실행하세요.")
    sys.exit(1)

try:
    from pywinauto.keyboard import send_keys
except ImportError:
    print("[ERROR] pywinauto 미설치 -- 'pip install pywinauto' 실행 후 재시도")
    sys.exit(1)

import win32cred
import win32com.client
import win32gui
import win32con
import win32api

# -- 설정 -----------------------------------------------------------------------
CYBOS_EXE        = r"C:\DAISHIN\STARTER\ncStarter.exe"
CYBOS_ARGS       = "/prj:cp"
CRED_TARGET      = "cybosplus"   # cmdkey /add: 에서 지정한 이름
MOCK_MODE        = True          # True=모의투자, False=실투자
CONNECT_TIMEOUT  = 90            # 로그인 후 연결 대기 최대 초
MOCK_POPUP_MIN_WAIT = 20         # 로그인 클릭 후 모의투자 선택 팝업 최소 대기 초
PASSWORD_OVERRIDE = u"amazin16"  # 임시 비밀번호 우선 사용

# kill 대상 (ncStarter 먼저, CpStart 나중 -- 순서 중요)
CYBOS_PROC_NAMES = ["_ncstarter_.exe", "cpstart.exe"]
SECURITY_BUTTON_TEXTS = {u"사용안함", u"사용 안함"}
LOGIN_WINDOW_TITLES   = {u"CYBOS Starter", u"CYBOS Plus"}
LOGIN_BUTTON_TEXTS    = {u"로그인", u"확 인", u"확인", u"ENTER", u"enter"}
PASSWORD_DIALOG_CONFIRM_TEXTS = {u"확인", u"예", u"Yes", u"OK"}
MOCK_ACCESS_BUTTON_TEXTS = {
    u"모의투자\r\n접속", u"모의투자\n접속", u"모의투자접속",
    u"모의투자 접속", u"접속",
}
MOCK_DIALOG_KEYWORDS = [u"모의투자 선택", u"모의투자선택", u"모의투자", u"접속"]
SECURITY_DIALOG_EXACT = u"CYBOS"
# -------------------------------------------------------------------------------

# WinEventHook 타입 정의 (콜백 GC 방지용 모듈 레벨 유지)
_WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD,
)
_EVENT_OBJECT_SHOW       = 0x8002
_WINEVENT_OUTOFCONTEXT   = 0x0000
_WINEVENT_SKIPOWNPROCESS = 0x0002

# -- 컨트롤 탐색 유틸 -----------------------------------------------------------

def _enum_children(parent_hwnd):
    """parent_hwnd의 모든 직계 자식 hwnd를 반환"""
    children = []

    def _cb(child, _):
        children.append(child)

    try:
        win32gui.EnumChildWindows(parent_hwnd, _cb, None)
    except Exception:
        pass
    return children


def _find_child_by_class(parent_hwnd, class_name, visible_only=True):
    """특정 클래스의 자식 컨트롤들을 반환"""
    results = []
    for child in _enum_children(parent_hwnd):
        try:
            if win32gui.GetClassName(child) == class_name:
                if not visible_only or win32gui.IsWindowVisible(child):
                    results.append(child)
        except Exception:
            pass
    return results


def _find_child_by_exact_text(parent_hwnd, texts, class_name=None):
    """정확한 텍스트 매치로 자식 컨트롤 검색"""
    results = []
    if isinstance(texts, str):
        texts = {texts}

    for child in _enum_children(parent_hwnd):
        try:
            if class_name and win32gui.GetClassName(child) != class_name:
                continue
            child_text = win32gui.GetWindowText(child).strip()
            if child_text in texts:
                results.append((child, child_text))
        except Exception:
            pass
    return results


def _find_child_by_text_contains(parent_hwnd, keywords, class_name=None):
    """부분 텍스트 매치로 자식 컨트롤 검색"""
    results = []
    if isinstance(keywords, str):
        keywords = [keywords]

    for child in _enum_children(parent_hwnd):
        try:
            if class_name and win32gui.GetClassName(child) != class_name:
                continue
            child_text = win32gui.GetWindowText(child).strip()
            for kw in keywords:
                if kw in child_text:
                    results.append((child, child_text))
                    break
        except Exception:
            pass
    return results


def _get_window_rect_safe(hwnd):
    """안전하게 창의 rect를 반환 (None 반환 가능)"""
    try:
        return win32gui.GetWindowRect(hwnd)
    except Exception:
        return None


def _is_control_enabled(hwnd):
    """컨트롤이 활성화(enable) 상태인지"""
    try:
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        return not (style & win32con.WS_DISABLED)
    except Exception:
        return False


# -- 컨트롤 조작 유틸 -----------------------------------------------------------

def _post_button_click(btn_hwnd):
    """BM_CLICK 메시지로 버튼 클릭 — 마우스/좌표 불필요"""
    try:
        win32gui.PostMessage(btn_hwnd, win32con.BM_CLICK, 0, 0)
        print("  [CTRL] BM_CLICK → hwnd=%d text='%s'" % (btn_hwnd, win32gui.GetWindowText(btn_hwnd)))
        return True
    except Exception as e:
        print("  [WARN] BM_CLICK 실패 hwnd=%d: %s" % (btn_hwnd, e))
        return False


def _set_edit_text(edit_hwnd, text):
    """WM_SETTEXT로 Edit 컨트롤에 텍스트 설정"""
    try:
        ctypes.windll.user32.SendMessageW(edit_hwnd, win32con.WM_SETTEXT, 0, text)
        print("  [CTRL] WM_SETTEXT → hwnd=%d text='%s'" % (edit_hwnd, "*" * len(text)))
        return True
    except Exception as e:
        print("  [WARN] WM_SETTEXT 실패 hwnd=%d: %s" % (edit_hwnd, e))
        return False


def _focus_control(hwnd):
    """컨트롤에 포커스 설정"""
    try:
        win32gui.SetFocus(hwnd)
        time.sleep(0.05)
    except Exception:
        pass


# -- 비밀번호 Edit 컨트롤 탐지 ---------------------------------------------------

_PASSWORD_HEURISTIC_CACHE = {}  # {window_title_hash: edit_index}


def _find_password_edit(parent_hwnd):
    """로그인 창에서 비밀번호 입력 Edit 컨트롤을 찾는다.

    휴리스틱 (우선순위):
      1. 자식 중 가장 큰 Edit (높이 기준) — Cybos Starter 전형적 패턴
      2. 마지막에 위치한 Edit (y 좌표 기준) — ID 필드 다음에 비밀번호 필드
      3. Edit 클래스 중 하나 — fallback
    """
    edits = [c for c in _enum_children(parent_hwnd)
             if win32gui.GetClassName(c) == "Edit" and win32gui.IsWindowVisible(c)]

    if not edits:
        # Cybos 로그인 창은 커스텀 윈도우일 수 있음 — AfxWnd/PopupEdit 등 다양한 클래스 탐색
        custom_edits = [c for c in _enum_children(parent_hwnd)
                        if win32gui.IsWindowVisible(c)]
        for c in custom_edits:
            try:
                cn = win32gui.GetClassName(c) or ""
                if any(kw in cn.upper() for kw in ("EDIT", "RICHEDIT", "TEXTBOX")):
                    edits.append(c)
            except Exception:
                pass

    if not edits:
        return None

    # 우선순위 1: 가장 큰 Edit (높이 기준)
    sorted_by_height = sorted(edits, key=lambda h: _get_window_rect_safe(h) or (0, 0, 0, 0),
                              reverse=True)
    largest = sorted_by_height[0]
    lr = _get_window_rect_safe(largest)
    largest_h = (lr[3] - lr[1]) if lr else 0

    # 패스워드 필드는 보통 폭이 넓고 높이가 20~35px
    if 15 <= largest_h <= 50:
        return largest

    # 우선순위 2: 가장 아래쪽에 있는 Edit (비밀번호는 ID 밑)
    sorted_by_y = sorted(edits, key=lambda h: _get_window_rect_safe(h) or (0, 999999, 0, 0))
    # Edit가 2개 이상이면 두 번째 것 (ID, PW 순서), 아니면 마지막
    if len(edits) >= 2:
        return sorted_by_y[-1]

    # 우선순위 3: 아무 Edit나 반환
    return edits[0]


def _activate_and_wait_for_window(hwnd, title_hint=""):
    """창을 활성화하고 안정화를 기다림"""
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.15)
        _force_foreground(hwnd)
        time.sleep(0.25)
    except Exception as e:
        print("  [WARN] 창 활성화 실패: %s" % e)


def _force_foreground(hwnd):
    """AttachThreadInput 트릭으로 창을 강제 포그라운드"""
    try:
        cur_tid = ctypes.windll.kernel32.GetCurrentThreadId()
        tgt_tid = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
        ctypes.windll.user32.AttachThreadInput(cur_tid, tgt_tid, True)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.BringWindowToTop(hwnd)
        ctypes.windll.user32.AttachThreadInput(cur_tid, tgt_tid, False)
        return True
    except Exception:
        return False


# -- 기본 유틸 ------------------------------------------------------------------

def _is_connected():
    try:
        cp = win32com.client.Dispatch("CpUtil.CpCybos")
        return cp.IsConnect == 1
    except Exception:
        return False


def _load_credential():
    """Windows Credential Manager에서 ID/PW 읽기"""
    if PASSWORD_OVERRIDE:
        return "", PASSWORD_OVERRIDE

    try:
        all_creds = win32cred.CredEnumerate(None, 0) or []
        for cred in all_creds:
            if cred.get("TargetName") == CRED_TARGET:
                username = cred["UserName"]
                blob = cred.get("CredentialBlob", b"")
                password = blob.decode("utf-16-le") if blob else ""
                return username, password
    except Exception as e:
        print("[DEBUG] CredEnumerate 오류: %s" % e)
    print("[ERROR] 자격증명 없음 -- PowerShell에서 아래 명령 실행 후 재시도:")
    print("  cmdkey /add:%s /user:아이디 /pass:비밀번호" % CRED_TARGET)
    sys.exit(1)


def _normalize_title(text):
    return (text or u"").replace(" ", "").upper()


def _find_window_by_keywords(keywords, require_visible=True):
    normalized_keywords = tuple(_normalize_title(kw) for kw in keywords)
    found = []

    def _enum(hwnd, _):
        try:
            if require_visible and not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd).strip()
            if not title:
                return
            normalized = _normalize_title(title)
            if any(kw in normalized for kw in normalized_keywords):
                found.append((hwnd, title))
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_enum, None)
    except Exception:
        pass
    return found


def _dump_children(parent_hwnd, label=""):
    """디버그용: 자식 컨트롤 덤프"""
    rows = []
    for child in _enum_children(parent_hwnd):
        try:
            text = win32gui.GetWindowText(child)
            cls  = win32gui.GetClassName(child)
            rect = win32gui.GetWindowRect(child)
            vis  = win32gui.IsWindowVisible(child)
            ena  = _is_control_enabled(child)
            rows.append((child, cls, repr(text), rect, vis, ena))
        except Exception:
            pass

    prefix = ("[%s] " % label) if label else ""
    print("%s자식 컨트롤 %d개:" % (prefix, len(rows)))
    for child_hwnd, cls, text, rect, vis, ena in rows:
        w = rect[2] - rect[0] if rect else 0
        h = rect[3] - rect[1] if rect else 0
        print("  hwnd=%-8d %s%s cls=%-22s %s %dx%d" % (
            child_hwnd, "V" if vis else " ", "E" if ena else " ",
            cls, text, w, h))


# -- 프로세스 관리 --------------------------------------------------------------

def _kill_cybos_procs():
    """기존 Cybos 프로세스 종료 (ncStarter 먼저, CpStart 나중)"""
    import psutil
    names = set(CYBOS_PROC_NAMES)

    def _get():
        return [p for p in psutil.process_iter(["name", "pid"])
                if p.info["name"] and p.info["name"].lower() in names]

    procs = _get()
    if not procs:
        return

    print("[INFO] 기존 Cybos 프로세스 종료 중...")
    for priority in CYBOS_PROC_NAMES:
        for p in procs:
            if p.info["name"] and p.info["name"].lower() == priority:
                try:
                    p.kill()
                    time.sleep(0.3)
                except Exception as e:
                    print("[WARN] kill 실패: %s" % e)

    deadline = time.time() + 8
    while time.time() < deadline:
        remaining = _get()
        if not remaining:
            break
        for p in remaining:
            try:
                p.kill()
            except Exception:
                pass
        time.sleep(0.5)

    time.sleep(2)


def _dismiss_error_dialogs():
    """CpStart/CPUTIL 에러 다이얼로그 자동 닫기"""
    dismissed = 0
    for title in ["CpStart", "CPUTIL", "공지사항"]:
        hwnd = win32gui.FindWindow(None, title)
        if not hwnd or not win32gui.IsWindowVisible(hwnd):
            continue
        found = [None]

        def _find_ok(child, _):
            if found[0]:
                return
            try:
                if win32gui.GetWindowText(child).strip() in {"확인", "OK", "예", "Yes"}:
                    found[0] = child
            except Exception:
                pass

        win32gui.EnumChildWindows(hwnd, _find_ok, None)
        if found[0]:
            win32gui.PostMessage(found[0], win32con.BM_CLICK, 0, 0)
        else:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        dismissed += 1
        print("[INFO] 에러 다이얼로그 닫음: %s" % title)
        time.sleep(0.8)
    return dismissed


# -- 창 탐지 --------------------------------------------------------------------

def _find_login_window_once():
    """정확한 제목 일치로 로그인 창 탐지"""
    SKIP_CLASSES = {"Shell_TrayWnd", "CabinetWClass", "ExploreWClass", "ShellTabWindowClass"}
    result = [None]

    def _enum(hwnd, _):
        if result[0]:
            return
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            if win32gui.GetClassName(hwnd) in SKIP_CLASSES:
                return
            if win32gui.GetWindowText(hwnd) in LOGIN_WINDOW_TITLES:
                result[0] = hwnd
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_enum, None)
    except Exception:
        pass
    return result[0]


# -- 보안 다이얼로그 클릭 -------------------------------------------------------

def _try_click_security(hwnd):
    """보안 다이얼로그(hwnd)에서 '사용안함' 버튼을 컨트롤 탐색으로 클릭"""
    btn_hwnd = [None]

    def _find(child, _):
        if btn_hwnd[0]:
            return
        try:
            if win32gui.GetWindowText(child).strip() in SECURITY_BUTTON_TEXTS:
                btn_hwnd[0] = child
        except Exception:
            pass

    try:
        win32gui.EnumChildWindows(hwnd, _find, None)
    except Exception:
        pass

    _force_foreground(hwnd)
    time.sleep(0.2)

    if btn_hwnd[0]:
        text = win32gui.GetWindowText(btn_hwnd[0])
        print("[INFO] '사용안함' 버튼 발견: '%s' hwnd=%d" % (text, btn_hwnd[0]))
        _post_button_click(btn_hwnd[0])
        return True
    else:
        # 자식 컨트롤에서 못 찾으면, 다이얼로그의 모든 Button을 찾아 가장 오른쪽 하단 버튼 클릭
        btns = _find_child_by_class(hwnd, "Button", visible_only=True)
        if btns:
            # 가장 오른쪽 버튼 = "사용안함" 가능성 높음
            btn = max(btns, key=lambda b: (_get_window_rect_safe(b) or (0, 0, 0, 0))[2])
            print("[INFO] '사용안함' 추정 버튼 (오른쪽): hwnd=%d text='%s'"
                  % (btn, win32gui.GetWindowText(btn)))
            _post_button_click(btn)
            return True

        print("[WARN] 보안 다이얼로그에서 버튼을 찾지 못함")
        _dump_children(hwnd, "보안 다이얼로그")
        return False


def _get_all_monitor_rects():
    """EnumDisplayMonitors로 모든 모니터 rect 반환 (left x 기준 정렬)"""
    monitors = []
    MonitorEnumProc = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.wintypes.HMONITOR,
        ctypes.wintypes.HDC,
        ctypes.POINTER(ctypes.wintypes.RECT),
        ctypes.wintypes.LPARAM,
    )

    def _cb(hMon, hDC, lpRect, lParam):
        r = lpRect.contents
        monitors.append((r.left, r.top, r.right, r.bottom))
        return True

    cb = MonitorEnumProc(_cb)
    ctypes.windll.user32.EnumDisplayMonitors(None, None, cb, 0)
    monitors.sort(key=lambda m: m[0])
    return monitors


def _blind_click_security_dialog():
    """
    최후의 수단: 타이밍 기반 블라인드 클릭.
    가장 왼쪽 모니터(보안 다이얼로그 위치) 하단부 우측 클릭.
    """
    monitors = _get_all_monitor_rects()
    print("[DBG] 모니터 목록: %s" % monitors)
    if not monitors:
        print("[WARN] 모니터 열거 실패 -- 블라인드 클릭 불가")
        return False

    l, t, r, b = monitors[0]
    cx = (l + r) // 2 + (r - l) // 8
    cy = t + int((b - t) * 0.55)
    print("[INFO] 블라인드 클릭 -> 모니터(x:%d~%d, y:%d~%d) 지점 (%d,%d)"
          % (l, r, t, b, cx, cy))

    win32api.SetCursorPos((cx, cy))
    time.sleep(0.15)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.2)
    return True


# -- 핵심 대기 루프 -------------------------------------------------------------

def _wait_for_login_clicking_security(timeout=120):
    """
    ncStarter 시작 후 보안 다이얼로그와 로그인 창을 200ms 간격으로 동시 탐지.

    탐지 전략 (우선순위 순):
      1. SetWinEventHook(EVENT_OBJECT_SHOW) -- 창이 나타나는 순간 즉시 캐치
      2. FindWindowW / FindWindow 폴링
      3. 12~17초 구간 블라인드 클릭 (보안 다이얼로그 최후 수단)

    로그인 창 발견 시 hwnd 반환, timeout 초과 시 None 반환.
    """
    security_clicked = False
    blind_clicked = False
    hook_handle = None
    hook_found = [None]

    def _win_event_cb(hHook, event, hwnd, idObj, idChild, tid, ms):
        if hwnd and not hook_found[0]:
            try:
                buf = ctypes.create_unicode_buffer(256)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
                if buf.value == SECURITY_DIALOG_EXACT:
                    hook_found[0] = hwnd
            except Exception:
                pass

    _cb_ref = _WinEventProcType(_win_event_cb)
    hook_handle = ctypes.windll.user32.SetWinEventHook(
        _EVENT_OBJECT_SHOW, _EVENT_OBJECT_SHOW,
        0, _cb_ref, 0, 0,
        _WINEVENT_OUTOFCONTEXT | _WINEVENT_SKIPOWNPROCESS,
    )
    if hook_handle:
        print("[INFO] WinEventHook 설치 완료 (보안 다이얼로그 실시간 감지)")
    else:
        print("[WARN] WinEventHook 설치 실패 -- 폴링만 사용")

    print("[INFO] ncStarter 초기화 대기 중 (보안 다이얼로그 + 로그인 창 탐지)...")
    start = time.time()
    msg = ctypes.wintypes.MSG()

    try:
        iterations = timeout * 5
        for tick in range(iterations):
            elapsed = time.time() - start

            while ctypes.windll.user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

            if not security_clicked:
                sec_hwnd = hook_found[0]
                if not sec_hwnd:
                    sec_hwnd = ctypes.windll.user32.FindWindowW(None, SECURITY_DIALOG_EXACT)
                if not sec_hwnd:
                    sec_hwnd = win32gui.FindWindow(None, SECURITY_DIALOG_EXACT)
                if not sec_hwnd:
                    sec_hwnd = win32gui.FindWindow("#32770", SECURITY_DIALOG_EXACT)

                if sec_hwnd:
                    try:
                        vis = win32gui.IsWindowVisible(sec_hwnd)
                    except Exception:
                        vis = "?"
                    print("[INFO] 보안 다이얼로그 발견 hwnd=%d visible=%s (%.1fs)"
                          % (sec_hwnd, vis, elapsed))
                    _try_click_security(sec_hwnd)
                    security_clicked = True

                elif 12.0 <= elapsed <= 17.0 and not blind_clicked:
                    print("[INFO] 보안창 미탐지 -- 블라인드 클릭 시도 (%.1fs)" % elapsed)
                    _blind_click_security_dialog()
                    blind_clicked = True

            login_hwnd = _find_login_window_once()
            if login_hwnd:
                try:
                    title = win32gui.GetWindowText(login_hwnd)
                except Exception:
                    title = "?"
                print("[INFO] 로그인 창 발견: '%s' hwnd=%d (%.1fs)"
                      % (title, login_hwnd, elapsed))
                return login_hwnd

            if tick % 50 == 49:
                print("[INFO] 대기 중... %.0f/%ds  보안클릭=%s 블라인드=%s"
                      % (elapsed, timeout, security_clicked, blind_clicked))

            time.sleep(0.2)

    finally:
        if hook_handle:
            ctypes.windll.user32.UnhookWinEvent(hook_handle)
            print("[INFO] WinEventHook 해제")

    return None


# -- 로그인 수행 ----------------------------------------------------------------

def _perform_login(hwnd, password):
    """
    로그인 창에서 컨트롤 기반으로:
      1. 비밀번호 Edit 컨트롤을 찾아 WM_SETTEXT + send_keys 입력
      2. 로그인 Button 컨트롤을 찾아 BM_CLICK

    절대 좌표 전혀 사용하지 않음.
    """
    _activate_and_wait_for_window(hwnd, "CYBOS Starter")

    # 디버그: 컨트롤 덤프
    title = win32gui.GetWindowText(hwnd)
    _dump_children(hwnd, "로그인 창 '%s'" % title)

    # ── STEP 1: 비밀번호 Edit 찾아 텍스트 입력 ──
    pw_edit = _find_password_edit(hwnd)
    if pw_edit:
        print("[INFO] 비밀번호 Edit 컨트롤 발견: hwnd=%d" % pw_edit)
        # 먼저 WM_SETTEXT로 시도 (백그라운드에서도 동작)
        if _set_edit_text(pw_edit, password):
            # WM_SETTEXT 성공 시 바로 확인
            pass
        else:
            # WM_SETTEXT 실패: 포커스 + send_keys fallback
            _focus_control(pw_edit)
            time.sleep(0.15)
            send_keys("^a")
            send_keys("{BACKSPACE}")
            time.sleep(0.1)
            send_keys(password)
            print("[INFO] send_keys로 비밀번호 입력 완료")
    else:
        # Edit 못 찾음 → 활성화 후 Tab으로 포커스 이동 시도
        print("[WARN] 비밀번호 Edit 컨트롤 미발견 — Tab 탐색 시도")
        send_keys("{TAB}")
        time.sleep(0.15)
        send_keys("{TAB}")
        time.sleep(0.15)
        send_keys("^a")
        send_keys("{BACKSPACE}")
        time.sleep(0.1)
        send_keys(password)
        print("[INFO] Tab 탐색으로 비밀번호 입력 시도 완료")

    time.sleep(0.3)

    # ── STEP 2: Enter 전송 (TextCtrl에 Enter가 login 역할 할 수 있음) ──
    send_keys("{ENTER}")
    print("[INFO] Enter 전송 → 로그인 시도 (%s)" % ("모의투자" if MOCK_MODE else "실투자"))
    time.sleep(0.5)

    # ── STEP 3: 로그인 버튼 찾아 BM_CLICK ──
    # Enter가 실패했을 수도 있으므로 버튼 클릭도 시도
    login_btns = _find_child_by_exact_text(hwnd, LOGIN_BUTTON_TEXTS, class_name="Button")
    if not login_btns:
        # Button 클래스가 아닌 경우도 탐색 (AfxWnd 등)
        login_btns = _find_child_by_text_contains(hwnd, list(LOGIN_BUTTON_TEXTS))

    if login_btns:
        for btn_hwnd, btn_text in login_btns:
            if _is_control_enabled(btn_hwnd):
                print("[INFO] 로그인 버튼 발견: '%s' hwnd=%d → BM_CLICK" % (btn_text, btn_hwnd))
                _post_button_click(btn_hwnd)
                break
        else:
            # enable 상태인 버튼이 없으면 첫 번째 버튼에 BM_CLICK 시도
            if login_btns:
                btn_hwnd, btn_text = login_btns[0]
                print("[INFO] 로그인 버튼 (disabled?) '%s' hwnd=%d → BM_CLICK" % (btn_text, btn_hwnd))
                _post_button_click(btn_hwnd)
    else:
        print("[INFO] 로그인 버튼 컨트롤 없음 — Enter로 충분할 수 있음")

    return True


# -- 비밀번호 확인 팝업 ---------------------------------------------------------

def _handle_password_confirm_dialog(timeout=10):
    """비밀번호 확인 팝업이 뜨면 컨트롤 기반으로 확인 버튼 클릭"""
    keywords = [u"비밀번호", u"확인", u"주시기 바랍니다", u"CYBOS"]
    print("[INFO] 비밀번호 확인 팝업 대기 중...")

    for tick in range(timeout):
        candidates = _find_window_by_keywords(keywords, require_visible=True)
        for hwnd, title in candidates:
            text = (title or u"").strip()
            if not text:
                continue

            # 확인 버튼 찾기
            ok_btns = _find_child_by_exact_text(hwnd, PASSWORD_DIALOG_CONFIRM_TEXTS, class_name="Button")
            if ok_btns:
                for btn_hwnd, btn_text in ok_btns:
                    if _is_control_enabled(btn_hwnd):
                        print("[INFO] 비밀번호 팝업 '%s': '%s' BM_CLICK" % (text, btn_text))
                        _post_button_click(btn_hwnd)
                        return True

            # 버튼 컨트롤을 못 찾았지만 창이 있으면 Enter 시도
            _force_foreground(hwnd)
            time.sleep(0.2)
            send_keys("{ENTER}")
            print("[INFO] 비밀번호 팝업 '%s': Enter 전송" % text)
            return True

        time.sleep(1)
        if tick % 5 == 4:
            print("[INFO] 비밀번호 확인 팝업 대기... %d/%d초" % (tick + 1, timeout))

    print("[INFO] 비밀번호 확인 팝업 없음")
    return False


# -- 모의투자 선택 창 -----------------------------------------------------------

def _find_mock_dialog_hwnd():
    """모의투자 선택 창을 여러 방법으로 탐지해 (hwnd, title) 반환.

    탐지 우선순위:
      1. FindWindow — 정확한 제목, 최상위 창 직접 탐색
      2. EnumWindows — 키워드 매칭
      3. #32770 다이얼로그 클래스 키워드 매칭
      4. 모든 창의 자식 Button에서 '모의투자 접속' 텍스트 탐색 (자식 창일 때 보완)
    """
    # 1차: 정확한 제목 FindWindow
    for exact_title in [u"모의투자 선택", u"모의투자선택"]:
        hwnd = win32gui.FindWindow(None, exact_title)
        if hwnd and win32gui.IsWindowVisible(hwnd):
            return hwnd, exact_title

    # 2차: EnumWindows + 키워드 매칭
    candidates = _find_window_by_keywords(MOCK_DIALOG_KEYWORDS, require_visible=True)
    if candidates:
        return candidates[0]

    # 3차: #32770(표준 다이얼로그) 클래스 + 키워드 매칭
    normalized_kws = [_normalize_title(kw) for kw in MOCK_DIALOG_KEYWORDS]
    found_hwnd = [0]
    found_title = [u""]

    def _enum_dlg(hwnd, _):
        if found_hwnd[0]:
            return
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            if win32gui.GetClassName(hwnd) != "#32770":
                return
            title = win32gui.GetWindowText(hwnd).strip()
            if title and any(kw in _normalize_title(title) for kw in normalized_kws):
                found_hwnd[0] = hwnd
                found_title[0] = title
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_enum_dlg, None)
    except Exception:
        pass

    if found_hwnd[0]:
        return found_hwnd[0], found_title[0]

    # 4차: 모든 최상위 창의 자식 전수 탐색 (EnumChildWindows 재귀)
    # Cybos가 다이얼로그를 자식 창으로 생성할 때를 대비.
    # '모의투자 접속' 버튼을 발견하면 그 직접 부모(다이얼로그)를 반환.
    btn_found = [0]

    def _find_access_btn(child, _):
        if btn_found[0]:
            return
        try:
            child_text = win32gui.GetWindowText(child).strip()
            # 정확한 텍스트 세트에 포함되거나, '모의투자'+'접속' 둘 다 포함된 버튼
            if child_text in MOCK_ACCESS_BUTTON_TEXTS or (
                u"모의투자" in child_text and u"접속" in child_text and
                win32gui.GetClassName(child) in ("Button", "AfxWnd42", "AfxWnd42u")
            ):
                btn_found[0] = child
        except Exception:
            pass

    def _scan_top_level(tlwnd, _):
        if btn_found[0]:
            return
        try:
            if not win32gui.IsWindowVisible(tlwnd):
                return
            win32gui.EnumChildWindows(tlwnd, _find_access_btn, None)
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_scan_top_level, None)
    except Exception:
        pass

    if btn_found[0]:
        # 버튼의 직접 부모 = 다이얼로그 창
        dlg = ctypes.windll.user32.GetParent(btn_found[0])
        if dlg and win32gui.IsWindowVisible(dlg):
            dlg_title = win32gui.GetWindowText(dlg).strip()
            print("[INFO] 4차 탐지: 자식 창에서 '모의투자 접속' 버튼 발견 "
                  "dlg=%d title='%s'" % (dlg, dlg_title))
            return dlg, dlg_title or u"모의투자 선택"

    return None, None


def _close_dialog_window(hwnd):
    """다이얼로그 창을 닫기 버튼(BM_CLICK) 또는 WM_CLOSE로 닫는다."""
    CLOSE_TEXTS = {u"닫기", u"확인", u"OK", u"예", u"Yes", u"Close", u"close"}
    close_btns = _find_child_by_exact_text(hwnd, CLOSE_TEXTS, class_name="Button")
    if close_btns:
        btn_hwnd, btn_text = close_btns[0]
        print("[INFO] 닫기 버튼: '%s' hwnd=%d → BM_CLICK" % (btn_text, btn_hwnd))
        _post_button_click(btn_hwnd)
    else:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print("[INFO] WM_CLOSE → hwnd=%d '%s'" % (hwnd, win32gui.GetWindowText(hwnd)))
    time.sleep(0.5)


def _click_mock_access_in_window(hwnd, title):
    """주어진 hwnd에서 '모의투자 접속' 버튼을 클릭. 성공 시 True 반환."""
    _activate_and_wait_for_window(hwnd, title)
    _dump_children(hwnd, u"모의투자 선택 '%s'" % title)

    # 1차: 정확한 텍스트의 Button 컨트롤
    found_btns = _find_child_by_exact_text(hwnd, MOCK_ACCESS_BUTTON_TEXTS, class_name="Button")
    if not found_btns:
        # 2차: 부분 텍스트 매치
        found_btns = _find_child_by_text_contains(hwnd, [u"접속", u"모의"])
    if not found_btns:
        # 3차: 모든 Button 중 가장 아래쪽 버튼
        all_btns = _find_child_by_class(hwnd, "Button")
        if all_btns:
            btn = max(all_btns,
                      key=lambda b: (_get_window_rect_safe(b) or (0, 9999, 0, 0))[1])
            found_btns = [(btn, win32gui.GetWindowText(btn))]

    if found_btns:
        btn_hwnd, btn_text = found_btns[0]
        print("[INFO] '모의투자 접속' 버튼: '%s' hwnd=%d → BM_CLICK" % (btn_text, btn_hwnd))
        _post_button_click(btn_hwnd)
        time.sleep(0.5)
        return True

    # 버튼 미발견 → 포그라운드로 올리고 Enter 전송
    print("[INFO] 접속 버튼 컨트롤 미발견 → 포그라운드 + Enter 시도")
    _dump_children(hwnd, u"모의투자 창 (버튼 못찾음)")
    _force_foreground(hwnd)
    time.sleep(0.3)
    send_keys("{ENTER}")
    time.sleep(0.5)
    return True


def _dismiss_notice_popups(timeout=10):
    """모의투자 접속 후 뜨는 공지사항 팝업을 닫는다.

    '공지사항', '알림', 'Cybos공지' 등 키워드로 창을 탐지하고
    닫기/확인 버튼 클릭 또는 WM_CLOSE로 처리한다.
    """
    NOTICE_KEYWORDS = [u"공지사항", u"오늘의공지", u"Cybos공지", u"공지"]
    # 메인 창 제목 패턴 — 공지 팝업과 혼동 방지
    MAIN_WIN_SKIP = {u"CYBOS Starter", u"CYBOS Plus", u"CybosPlus",
                     u"대신증권", u"Daishin"}

    print("[INFO] 공지사항 팝업 확인 중 (최대 %d초)..." % timeout)
    for tick in range(timeout):
        dismissed = 0

        # FindWindow 직접 탐색
        for kw in NOTICE_KEYWORDS:
            hwnd = win32gui.FindWindow(None, kw)
            if hwnd and win32gui.IsWindowVisible(hwnd):
                print("[INFO] 공지사항 팝업 발견 '%s' hwnd=%d → 닫기" % (kw, hwnd))
                _close_dialog_window(hwnd)
                dismissed += 1

        # EnumWindows 키워드 탐색
        candidates = _find_window_by_keywords(NOTICE_KEYWORDS, require_visible=True)
        for hwnd, title in candidates:
            if any(skip in title for skip in MAIN_WIN_SKIP):
                continue
            print("[INFO] 공지사항 팝업 감지: '%s' hwnd=%d → 닫기" % (title, hwnd))
            _close_dialog_window(hwnd)
            dismissed += 1

        if dismissed:
            print("[INFO] 공지사항 팝업 %d건 닫음" % dismissed)
            return dismissed

        time.sleep(1)

    print("[INFO] 공지사항 팝업 없음 — 계속 진행")
    return 0


def _handle_mock_select_dialog(timeout=45, min_wait=0):
    """모의투자 선택 창을 찾아 '모의투자 접속' 버튼을 BM_CLICK"""
    print("[INFO] 모의투자 선택 창 대기 중...")

    # min_wait 구간: 매초 다이얼로그를 탐지해 나타나는 즉시 클릭
    if min_wait > 0:
        print("[INFO] 모의투자 선택 팝업 대기 보장... %d초" % min_wait)
        for waited in range(min_wait):
            if _is_connected():
                print("[INFO] 이미 연결되어 있어 모의투자 선택 창 처리를 생략합니다.")
                return True

            hwnd, title = _find_mock_dialog_hwnd()
            if hwnd:
                print("[INFO] min_wait 중 모의투자 선택 창 감지: '%s' hwnd=%d (%d초 경과)"
                      % (title, hwnd, waited))
                _click_mock_access_in_window(hwnd, title)
                return True

            time.sleep(1)
            if (waited + 1) % 5 == 0:
                print("[INFO] 모의투자 팝업 최소 대기... %d/%d초" % (waited + 1, min_wait))

        # min_wait 경과 후에도 창이 없으면 Enter로 기본 선택 강제
        send_keys("{ENTER}")
        print("[INFO] 모의투자 팝업 최소 대기 후 Enter 입력")
        time.sleep(3)
        print("[INFO] 3초 대기 완료 — 연결 대기 확인 진행")

    # 이후 폴링 루프
    for tick in range(timeout):
        if _is_connected():
            print("[INFO] 이미 연결되어 있어 모의투자 선택 창 처리를 생략합니다.")
            return True

        hwnd, title = _find_mock_dialog_hwnd()
        if hwnd:
            print("[INFO] 모의투자 선택 창 발견: '%s' hwnd=%d" % (title, hwnd))
            _click_mock_access_in_window(hwnd, title)
            return True

        if tick % 5 == 4:
            print("[INFO] 모의투자 선택 창 대기... %d/%d초" % (tick + 1, timeout))
        time.sleep(1)

    print("[WARN] 모의투자 선택 창이 나타나지 않음 -- 건너뜀")
    return False


# -- 메인 -----------------------------------------------------------------------

def autologin():
    if _is_connected():
        print("[INFO] CybosPlus 이미 연결됨 -- 로그인 생략")
        return True

    user_id, password = _load_credential()

    if not os.path.exists(CYBOS_EXE):
        print("[ERROR] HTS 실행 파일 없음: %s" % CYBOS_EXE)
        sys.exit(1)

    import psutil
    names = set(CYBOS_PROC_NAMES)
    already_running = any(
        p.info["name"] and p.info["name"].lower() in names
        for p in psutil.process_iter(["name"])
        if p.info["name"]
    )

    if already_running:
        print("[INFO] 기존 Cybos 프로세스 발견 -- 재시작합니다.")
        _kill_cybos_procs()

    exe_dir = os.path.dirname(CYBOS_EXE)
    try:
        win32api.ShellExecute(0, "open", CYBOS_EXE, CYBOS_ARGS, exe_dir, win32con.SW_SHOW)
        print("[INFO] %s %s 시작됨" % (os.path.basename(CYBOS_EXE), CYBOS_ARGS))
    except Exception as e:
        print("[WARN] ShellExecute 실패(%s) -- Popen 재시도" % e)
        subprocess.Popen([CYBOS_EXE, CYBOS_ARGS], cwd=exe_dir)

    # STEP 1+2: 보안 다이얼로그 자동 클릭 + 로그인 창 대기 (통합 루프)
    hwnd = _wait_for_login_clicking_security(timeout=120)
    if hwnd is None:
        print("[ERROR] 로그인 창을 찾지 못했습니다 (120초 초과).")
        print("[HINT]  _ncStarter_.exe -> '사용안함' -> 'CYBOS Starter' 창을 확인하세요.")
        sys.exit(1)

    for _ in range(5):
        if _dismiss_error_dialogs() == 0:
            break
        time.sleep(0.5)
    time.sleep(1.5)

    # STEP 3: 컨트롤 기반 비밀번호 입력 + 로그인
    try:
        _perform_login(hwnd, password)
        # 비밀번호 갱신 확인 다이얼로그 등 팝업 처리
        _handle_password_confirm_dialog(timeout=5)
    except Exception as e:
        print("[ERROR] UI 자동화 실패: %s" % e)
        sys.exit(1)

    # STEP 4: 모의투자 선택 창
    if MOCK_MODE:
        _handle_mock_select_dialog(timeout=45, min_wait=MOCK_POPUP_MIN_WAIT)
        # 모의투자 접속 후 공지사항 팝업 처리
        _dismiss_notice_popups(timeout=10)

    # STEP 5: 연결 완료 대기
    print("[INFO] 연결 대기 중 (최대 %d초)..." % CONNECT_TIMEOUT)
    for i in range(CONNECT_TIMEOUT):
        _dismiss_error_dialogs()
        if _is_connected():
            cp = win32com.client.Dispatch("CpUtil.CpCybos")
            print("[OK] CybosPlus 연결 성공 (ServerType=%s)" % cp.ServerType)
            return True
        time.sleep(1)
        if i % 10 == 9:
            print("  ... %d초 경과" % (i + 1))

    print("[ERROR] 연결 타임아웃")
    return False


if __name__ == "__main__":
    success = autologin()
    sys.exit(0 if success else 1)