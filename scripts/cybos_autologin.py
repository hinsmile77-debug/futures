# -*- coding: utf-8 -*-
"""
CybosPlus 자동 로그인 스크립트
- Windows Credential Manager에서 비밀번호를 읽어 로그인 창을 자동 조작
- 사전 준비: cmdkey /add:cybosplus /user:아이디 /pass:비밀번호 (1회)
- 의존: pywinauto, pywin32, psutil

시작 순서:
  1. _ncStarter_.exe 실행
  2. "CYBOS" 보안프로그램 다이얼로그 -> "사용안함" 클릭 (자동)
  3. "CYBOS Starter" 로그인 창 -> 비밀번호 입력 + 로그인
  4. "모의투자 선택" 창 -> "모의투자 접속" 클릭 (MOCK_MODE=True)

보안 다이얼로그 탐지 전략 (3단계):
  1. SetWinEventHook(EVENT_OBJECT_SHOW) -- 창이 나타나는 순간 실시간 캐치
  2. FindWindow 200ms 폴링 -- 표준 Win32 탐색
  3. 블라인드 클릭 -- 12~17초 구간, 가장 왼쪽 모니터 추정 좌표 클릭
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

# -- 설정 -----------------------------------------------------------------------
CYBOS_EXE        = r"C:\DAISHIN\STARTER\ncStarter.exe"
CYBOS_ARGS       = "/prj:cp"
CRED_TARGET      = "cybosplus"   # cmdkey /add: 에서 지정한 이름
MOCK_MODE        = True          # True=모의투자, False=실투자
CONNECT_TIMEOUT  = 90            # 로그인 후 연결 대기 최대 초
MOCK_POPUP_MIN_WAIT = 20         # 로그인 클릭 후 모의투자 선택 팝업 최소 대기 초
# 로그인 자동화 순서:
# 1. 비밀번호 입력칸 클릭
# 2. 비밀번호 입력
# 3. Enter key
# 4. 모의투자 접속 버튼 클릭
PASSWORD_FIELD_POS = (971, 695)
PASSWORD_OVERRIDE = u"amazin16"  # 임시 비밀번호 우선 사용
MOCK_ACCESS_BUTTON_POS = (1416, 645)

# 보조 팝업 처리용 좌표
PASSWORD_CONFIRM_BUTTON_POS = (1280, 732)

# kill 대상 (ncStarter 먼저, CpStart 나중 -- 순서 중요)
CYBOS_PROC_NAMES = ["_ncstarter_.exe", "cpstart.exe"]
SECURITY_BUTTON_TEXTS = {u"사용안함", u"사용 안함"}
LOGIN_WINDOW_TITLES   = {u"CYBOS Starter", u"CYBOS Plus"}
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


def _physical_click(x, y):
    """절대 화면 좌표 (x, y) 에 실제 마우스 클릭"""
    import win32api, win32con
    print("[DBG] _physical_click(%d, %d)" % (x, y))
    ctypes.windll.user32.SetCursorPos(x, y)
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.2)


def _force_foreground(hwnd):
    """AttachThreadInput 트릭으로 창을 강제 포그라운드"""
    import win32gui, win32con
    try:
        cur_tid = ctypes.windll.kernel32.GetCurrentThreadId()
        tgt_tid = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
        ctypes.windll.user32.AttachThreadInput(cur_tid, tgt_tid, True)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.BringWindowToTop(hwnd)
        ctypes.windll.user32.AttachThreadInput(cur_tid, tgt_tid, False)
    except Exception as e:
        print("[DBG] _force_foreground 실패: %s" % e)


def _dump_children(parent_hwnd):
    """parent_hwnd의 모든 자식을 열거해서 출력 (디버그용)"""
    import win32gui
    rows = []

    def _cb(child, _):
        try:
            text = win32gui.GetWindowText(child)
            cls  = win32gui.GetClassName(child)
            rect = win32gui.GetWindowRect(child)
            vis  = win32gui.IsWindowVisible(child)
            rows.append((child, cls, repr(text), rect, vis))
        except Exception:
            pass

    try:
        win32gui.EnumChildWindows(parent_hwnd, _cb, None)
    except Exception:
        pass
    for child_hwnd, cls, text_repr, rect, vis in rows:
        print("  hwnd=%-8d vis=%d cls=%-22s text=%-25s rect=%s"
              % (child_hwnd, vis, cls, text_repr, rect))
    return rows


def _normalize_title(text):
    return (text or u"").replace(" ", "").upper()


def _find_window_by_keywords(keywords, require_visible=True):
    import win32gui

    normalized_keywords = tuple(_normalize_title(keyword) for keyword in keywords)
    found = []

    def _enum(hwnd, _):
        try:
            if require_visible and not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd).strip()
            if not title:
                return
            normalized = _normalize_title(title)
            if any(keyword in normalized for keyword in normalized_keywords):
                found.append((hwnd, title))
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_enum, None)
    except Exception:
        pass

    return found


def _click_absolute(x, y):
    import win32api
    import win32con

    win32api.SetCursorPos((x, y))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.2)


def _handle_password_confirm_dialog(timeout=10):
    """비밀번호 확인 팝업이 뜨면 확인 버튼을 누른다."""
    keywords = [u"비밀번호", u"확인", u"주시기 바랍니다", u"CYBOS"]
    print("[INFO] 비밀번호 확인 팝업 대기 중...")
    for tick in range(timeout):
        candidates = _find_window_by_keywords(keywords, require_visible=True)
        for hwnd, title in candidates:
            text = (title or u"").strip()
            if not text:
                continue
            x, y = PASSWORD_CONFIRM_BUTTON_POS
            print("[INFO] 비밀번호 확인 팝업 감지: '%s' -> 확인 클릭 (%d,%d)" % (text, x, y))
            _click_absolute(x, y)
            return True
        time.sleep(1)
        if tick % 5 == 4:
            print("[INFO] 비밀번호 확인 팝업 대기... %d/%d초" % (tick + 1, timeout))
    print("[INFO] 비밀번호 확인 팝업 없음")
    return False


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
    import win32gui, win32con
    dismissed = 0
    for title in ["CpStart", "CPUTIL"]:
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
    import win32gui
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
    """보안 다이얼로그(hwnd)에서 '사용안함' 버튼을 물리 클릭"""
    import win32gui
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

    dlg_rect = win32gui.GetWindowRect(hwnd)
    print("[DBG] 보안창 자식 덤프 (hwnd=%d rect=%s):" % (hwnd, dlg_rect))
    _dump_children(hwnd)
    _force_foreground(hwnd)
    time.sleep(0.3)

    if btn_hwnd[0]:
        l, t, r, b = win32gui.GetWindowRect(btn_hwnd[0])
        cx, cy = (l + r) // 2, (t + b) // 2
        print("[INFO] '사용안함' 버튼 클릭 -> (%d, %d)" % (cx, cy))
    else:
        l, t, r, b = dlg_rect
        cx = l + int((r - l) * 0.75)
        cy = t + int((b - t) * 0.85)
        print("[INFO] '사용안함' 좌표 추정 클릭 -> (%d, %d)" % (cx, cy))

    _physical_click(cx, cy)
    return True


def _handle_mock_select_dialog(timeout=45, min_wait=0):
    """모의투자 선택 창을 제목 변형까지 포함해 찾아 '모의투자 접속'을 누른다."""
    import win32gui
    import win32con

    btn_texts = {"紐⑥쓽?ъ옄\r\n?묒냽", "紐⑥쓽?ъ옄\n?묒냽", "紐⑥쓽?ъ옄?묒냽", "紐⑥쓽?ъ옄 ?묒냽", "?묒냽"}
    dialog_keywords = ["紐⑥쓽?ъ옄 ?좏깮", "紐⑥쓽?ъ옄?좏깮", "紐⑥쓽?ъ옄", "?묒냽"]

    print("[INFO] 모의투자 선택 창 대기 중...")
    if min_wait > 0:
        print("[INFO] 모의투자 선택 팝업 대기 보장... %d초" % min_wait)
        for waited in range(min_wait):
            if _is_connected():
                print("[INFO] 이미 연결되어 있어 모의투자 선택 창 처리를 생략합니다.")
                return True
            time.sleep(1)
            if (waited + 1) % 5 == 0:
                print("[INFO] 모의투자 팝업 최소 대기... %d/%d초" % (waited + 1, min_wait))
        send_keys("{ENTER}")
        print("[INFO] 모의투자 팝업 대기 후 Enter 입력")
        time.sleep(0.8)
        if _is_connected():
            return True

    for tick in range(timeout):
        if _is_connected():
            print("[INFO] 이미 연결되어 있어 모의투자 선택 창 처리를 생략합니다.")
            return True

        candidates = _find_window_by_keywords(dialog_keywords, require_visible=True)
        for hwnd, title in candidates:
            if not win32gui.IsWindowVisible(hwnd):
                continue

            time.sleep(0.5)
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
            time.sleep(0.3)

            try:
                _force_foreground(hwnd)
            except Exception:
                pass
            time.sleep(0.2)
            send_keys("{ENTER}")
            print("[INFO] 모의투자 선택 창에서 Enter 입력 title='%s'" % title)
            time.sleep(0.8)
            if _is_connected():
                return True

            btn_rect = [None]

            def _find_btn(child, _):
                if btn_rect[0]:
                    return
                try:
                    text = win32gui.GetWindowText(child).strip()
                    if text in btn_texts:
                        btn_rect[0] = _get_window_rect_safe(child) or win32gui.GetWindowRect(child)
                except Exception:
                    pass

            try:
                win32gui.EnumChildWindows(hwnd, _find_btn, None)
            except Exception:
                pass

            if btn_rect[0]:
                l, t, r, b = btn_rect[0]
                cx, cy = (l + r) // 2, (t + b) // 2
                _physical_click(cx, cy)
                print("[INFO] '모의투자 접속' 클릭 완료 (%d,%d) title='%s'" % (cx, cy, title))
            else:
                rect = _get_window_rect_safe(hwnd)
                if not _is_valid_rect(rect):
                    continue
                l, t, r, b = rect
                cx = l + int((r - l) * 0.80)
                cy = t + int((b - t) * 0.38)
                _physical_click(cx, cy)
                print("[INFO] '모의투자 접속' 좌표 fallback 클릭 (%d,%d) title='%s'" % (cx, cy, title))

            return True

        if tick % 5 == 4:
            titles = [title for _, title in candidates[:6]]
            print("[INFO] 모의투자 선택 창 대기... %d/%d초 candidates=%s" % (tick + 1, timeout, titles))
        time.sleep(1)

    print("[WARN] 모의투자 선택 창이 나타나지 않음 — 건너뜀")
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
    FindWindow 실패 시 타이밍 기반 블라인드 클릭.
    가장 왼쪽 모니터(보안 다이얼로그 위치) 중앙 하단부 클릭.
    '사용안함'은 우측 버튼이므로 중앙보다 약간 오른쪽을 클릭.
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
    _physical_click(cx, cy)
    return True


# -- 핵심 대기 루프 -------------------------------------------------------------

def _wait_for_login_clicking_security(timeout=120):
    """
    ncStarter 시작 후 보안 다이얼로그와 로그인 창을 200ms 간격으로 동시 탐지.

    탐지 전략 (우선순위 순):
      1. SetWinEventHook(EVENT_OBJECT_SHOW) -- 창이 나타나는 순간 즉시 캐치
      2. FindWindowW / FindWindow 폴링
      3. 12~17초 구간 블라인드 클릭 (모니터 3 추정 좌표)

    로그인 창 발견 시 hwnd 반환, timeout 초과 시 None 반환.
    """
    import win32gui

    SECURITY_EXACT = u"CYBOS"
    security_clicked = False
    blind_clicked = False
    hook_handle = None
    hook_found = [None]

    def _win_event_cb(hHook, event, hwnd, idObj, idChild, tid, ms):
        if hwnd and not hook_found[0]:
            try:
                buf = ctypes.create_unicode_buffer(256)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
                if buf.value == SECURITY_EXACT:
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
                    sec_hwnd = ctypes.windll.user32.FindWindowW(None, SECURITY_EXACT)
                if not sec_hwnd:
                    sec_hwnd = win32gui.FindWindow(None, str(SECURITY_EXACT))
                if not sec_hwnd:
                    sec_hwnd = win32gui.FindWindow("#32770", str(SECURITY_EXACT))

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


# -- 모의투자 선택 창 -----------------------------------------------------------

def _handle_mock_select_dialog(timeout=45, min_wait=0):
    """모의투자 선택 창을 제목 변형까지 포함해 찾아 '모의투자 접속'을 누른다."""
    import win32gui
    import win32con

    btn_texts = {u"모의투자\r\n접속", u"모의투자\n접속", u"모의투자접속",
                 u"모의투자 접속", u"접속"}
    dialog_keywords = [u"모의투자 선택", u"모의투자선택", u"모의투자", u"접속"]

    print("[INFO] 모의투자 선택 창 대기 중...")
    if min_wait > 0:
        print("[INFO] 모의투자 선택 팝업 대기 보장... %d초" % min_wait)
        for waited in range(min_wait):
            if _is_connected():
                print("[INFO] 이미 연결되어 있어 모의투자 선택 창 처리를 생략합니다.")
                return True
            time.sleep(1)
            if (waited + 1) % 5 == 0:
                print("[INFO] 모의투자 팝업 최소 대기... %d/%d초" % (waited + 1, min_wait))
        send_keys("{ENTER}")
        print("[INFO] 모의투자 팝업 최소 대기 후 Enter 입력")
        time.sleep(3)
        print("[INFO] 3초 대기 완료 — 연결 대기로 진행")
        return True

    for tick in range(timeout):
        if _is_connected():
            print("[INFO] 이미 연결되어 있어 모의투자 선택 창 처리를 생략합니다.")
            return True

        candidates = _find_window_by_keywords(dialog_keywords, require_visible=True)
        for hwnd, title in candidates:
            if not win32gui.IsWindowVisible(hwnd):
                continue

            time.sleep(0.5)
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
            time.sleep(0.3)

            btn_rect = [None]

            def _find_btn(child, _):
                if btn_rect[0]:
                    return
                try:
                    text = win32gui.GetWindowText(child).strip()
                    if text in btn_texts:
                        btn_rect[0] = _get_window_rect_safe(child) or win32gui.GetWindowRect(child)
                except Exception:
                    pass

            try:
                win32gui.EnumChildWindows(hwnd, _find_btn, None)
            except Exception:
                pass

            if btn_rect[0]:
                l, t, r, b = btn_rect[0]
                cx, cy = (l + r) // 2, (t + b) // 2
                print("[INFO] '모의투자 접속' 클릭 (%d,%d) title='%s'" % (cx, cy, title))
            else:
                cx, cy = MOCK_ACCESS_BUTTON_POS
                print("[INFO] '모의투자 접속' 절대좌표 클릭 (%d,%d) title='%s'" % (cx, cy, title))

            _physical_click(cx, cy)
            return True

        if tick % 5 == 4:
            titles = [title for _, title in candidates[:6]]
            print("[INFO] 모의투자 선택 창 대기... %d/%d초 candidates=%s" % (tick + 1, timeout, titles))
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

    import win32api, win32con
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

    # STEP 3: 비밀번호 입력 + 로그인
    try:
        import win32gui, win32api, win32con

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)

        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        w = right - left
        h = bottom - top

        def _click(rx, ry):
            x = left + int(w * rx)
            y = top  + int(h * ry)
            _click_absolute(x, y)

        pw_x, pw_y = PASSWORD_FIELD_POS
        _click_absolute(pw_x, pw_y)
        time.sleep(0.3)
        send_keys("^a")
        send_keys("{BACKSPACE}")
        time.sleep(0.1)
        send_keys(password)
        print("[INFO] 비밀번호 직접 입력 완료")

        time.sleep(0.3)
        send_keys("{ENTER}")
        print("[INFO] Enter 입력으로 로그인 진행 (%s)" % ("모의투자" if MOCK_MODE else "실투자"))

    except Exception as e:
        print("[ERROR] UI 자동화 실패: %s" % e)
        sys.exit(1)

    # STEP 4: 모의투자 선택 창
    if MOCK_MODE:
        _handle_mock_select_dialog(timeout=45, min_wait=MOCK_POPUP_MIN_WAIT)

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
