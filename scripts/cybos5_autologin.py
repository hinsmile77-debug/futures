# -*- coding: utf-8 -*-
"""
CYBOS5 launcher flow.

Primary expected flow:
  1. Launch ncStarter.exe
  2. Wait for "CYBOS Starter" login window
  3. Fill ID / password
  4. Send Enter to try login
  5. Wait for "모의투자 선택" popup and send Enter
  6. Wait for COM connection

Fallback flow:
  - If "기존 연결 선택" appears instead of the login window, click
    "기존 연결로 접속" and then wait for COM connection.
"""
import ctypes
import ctypes.wintypes
import os
import struct
import subprocess
import sys
import time

if struct.calcsize("P") != 4:
    print("[ERROR] 32-bit Python is required, current=%d-bit" % (struct.calcsize("P") * 8))
    sys.exit(1)

try:
    from pywinauto.keyboard import send_keys
except ImportError:
    print("[ERROR] pywinauto is required.")
    sys.exit(1)

import win32api
import win32com.client
import win32con
import win32cred
import win32gui
import win32process


CYBOS_EXE = r"C:\DAISHIN\STARTER\ncStarter.exe"
CYBOS_ARGS = None
CRED_TARGET = "cybosplus"
CONNECT_TIMEOUT = 90
LOGIN_WAIT_TIMEOUT = 120
MOCK_POPUP_MIN_WAIT = 20
MOCK_POPUP_TIMEOUT = 45
PASSWORD_OVERRIDE = None
MAIN_WINDOW_TIMEOUT = 30

LOGIN_WINDOW_TITLES = {u"CYBOS Starter", u"CYBOS Plus"}
CYBOS_MENU_EXACT_TEXTS = {u"CYBOS"}
CYBOS_MENU_CANDIDATE_TEXTS = {
    u"CYBOS",
    u"CYBOS Trader",
    u"CYBOS Plus",
    u"CYBOS I",
    u"CYBOS Oneclick",
}
EXISTING_CONNECTION_DIALOG_KEYWORDS = [
    u"기존 연결 선택",
    u"기존연결선택",
    u"기존 연결",
]
EXISTING_CONNECTION_BUTTON_TEXTS = {
    u"기존 연결로 접속",
    u"기존연결로접속",
}
MOCK_DIALOG_KEYWORDS = [
    u"모의투자 선택",
    u"모의투자선택",
    u"모의투자",
]
MOCK_ACCESS_BUTTON_TEXTS = {
    u"모의투자 접속",
    u"모의투자\r\n접속",
    u"모의투자\n접속",
    u"모의투자접속",
    u"접속",
}
LOGIN_BUTTON_TEXTS = {
    u"로그인",
    u"모의투자 로그인",
    u"모의투자로그인",
    u"확인",
    u"ENTER",
    u"enter",
}
PASSWORD_DIALOG_CONFIRM_TEXTS = {u"확인", u"예", u"Yes", u"OK"}
SECURITY_DIALOG_EXACT = u"CYBOS"
SECURITY_BUTTON_TEXTS = {u"사용안함", u"사용 안함"}


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
_EVENT_OBJECT_SHOW = 0x8002
_WINEVENT_OUTOFCONTEXT = 0x0000
_WINEVENT_SKIPOWNPROCESS = 0x0002

MAIN_WINDOW_KEYWORDS = [
    u"CYBOS 5",
    u"CYBOS5",
    u"DAISHIN",
]
MAIN_WINDOW_EXCLUDE_KEYWORDS = [
    u"STARTER",
    u"MIREUK",
    u"SESSION LAUNCHER",
    u"VISUAL STUDIO",  # VS Code / VS IDE title contains "CYBOS5.bat"
    u"PYCHARM",
    u".BAT",           # any bat file open in an editor
    u"NOTEPAD",
]
ALREADY_RUNNING_DIALOG_KEYWORDS = [
    u"BOS.EXE",
]
ALREADY_RUNNING_CONFIRM_TEXTS = {
    u"예(&Y)",
    u"예",
    u"Yes",
    u"&Yes",
}


def _normalize(text):
    return (text or u"").replace(" ", "").replace("\r", "").replace("\n", "").upper()


def _enum_children(parent_hwnd):
    children = []

    def _cb(child, _):
        children.append(child)

    try:
        win32gui.EnumChildWindows(parent_hwnd, _cb, None)
    except Exception:
        pass
    return children


def _find_child_by_class(parent_hwnd, class_name, visible_only=True):
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
    results = []
    if isinstance(texts, str):
        texts = {texts}
    targets = {_normalize(text) for text in texts}

    for child in _enum_children(parent_hwnd):
        try:
            if class_name and win32gui.GetClassName(child) != class_name:
                continue
            child_text = win32gui.GetWindowText(child).strip()
            if _normalize(child_text) in targets:
                results.append((child, child_text))
        except Exception:
            pass
    return results


def _find_child_by_text_contains(parent_hwnd, keywords, class_name=None):
    results = []
    normalized_keywords = [_normalize(keyword) for keyword in keywords]

    for child in _enum_children(parent_hwnd):
        try:
            if class_name and win32gui.GetClassName(child) != class_name:
                continue
            child_text = win32gui.GetWindowText(child).strip()
            normalized = _normalize(child_text)
            if any(keyword in normalized for keyword in normalized_keywords):
                results.append((child, child_text))
        except Exception:
            pass
    return results


def _dump_children(parent_hwnd, label):
    rows = []
    for child in _enum_children(parent_hwnd):
        try:
            rows.append((
                child,
                win32gui.GetClassName(child),
                win32gui.GetWindowText(child),
                win32gui.GetWindowRect(child),
                win32gui.IsWindowVisible(child),
                _is_control_enabled(child),
            ))
        except Exception:
            pass

    print("[INFO] Child dump for %s (%d controls)" % (label, len(rows)))
    for child_hwnd, cls, text, rect, visible, enabled in rows:
        print("  hwnd=%d cls=%s visible=%s enabled=%s text=%r rect=%s" % (
            child_hwnd, cls, visible, enabled, text, rect
        ))


def _collect_child_texts(parent_hwnd):
    texts = []
    for child in _enum_children(parent_hwnd):
        try:
            text = win32gui.GetWindowText(child).strip()
            if text:
                texts.append(text)
        except Exception:
            pass
    return texts


def _physical_click_hwnd(hwnd):
    rect = _get_window_rect_safe(hwnd)
    if not rect:
        return False
    left, top, right, bottom = rect
    cx = int((left + right) / 2)
    cy = int((top + bottom) / 2)
    try:
        win32api.SetCursorPos((cx, cy))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.2)
        print("[INFO] Physical click sent: hwnd=%d text='%s'" % (hwnd, win32gui.GetWindowText(hwnd)))
        return True
    except Exception as exc:
        print("[WARN] Physical click failed hwnd=%d: %s" % (hwnd, exc))
        return False


def _physical_click_point(x, y, label=""):
    try:
        win32api.SetCursorPos((int(x), int(y)))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.25)
        if label:
            print("[INFO] Physical click sent at (%d, %d): %s" % (int(x), int(y), label))
        else:
            print("[INFO] Physical click sent at (%d, %d)" % (int(x), int(y)))
        return True
    except Exception as exc:
        print("[WARN] Physical click failed at (%d, %d): %s" % (int(x), int(y), exc))
        return False


def _find_top_left_text_control(parent_hwnd, candidate_texts):
    targets = {_normalize(text) for text in candidate_texts}
    candidates = []
    for child in _enum_children(parent_hwnd):
        try:
            if not win32gui.IsWindowVisible(child):
                continue
            text = win32gui.GetWindowText(child).strip()
            if _normalize(text) in targets:
                rect = _get_window_rect_safe(child) or (99999, 99999, 99999, 99999)
                candidates.append((child, text, rect))
        except Exception:
            pass
    if not candidates:
        return None, None
    candidates.sort(key=lambda item: (item[2][1], item[2][0]))
    child, text, _rect = candidates[0]
    return child, text


def _ensure_cybos_menu_selected(hwnd):
    print("[INFO] Verifying left-top product menu is set to CYBOS...")
    _activate_window(hwnd)

    exact_hwnd, exact_text = _find_top_left_text_control(hwnd, CYBOS_MENU_EXACT_TEXTS)
    if exact_hwnd:
        print("[INFO] CYBOS menu already selected: '%s' hwnd=%d" % (exact_text, exact_hwnd))
        return True

    opener_hwnd, opener_text = _find_top_left_text_control(hwnd, CYBOS_MENU_CANDIDATE_TEXTS)
    if opener_hwnd:
        print("[INFO] Product menu control found: '%s' hwnd=%d" % (opener_text, opener_hwnd))
        _physical_click_hwnd(opener_hwnd)
        time.sleep(0.4)

        popup_matches = _find_window_by_keywords([u"CYBOS"], require_visible=True)
        for popup_hwnd, popup_title in popup_matches:
            menu_hwnd, menu_text = _find_top_left_text_control(popup_hwnd, CYBOS_MENU_EXACT_TEXTS)
            if menu_hwnd:
                print("[INFO] CYBOS menu item found in popup: '%s' hwnd=%d" % (menu_text, menu_hwnd))
                _physical_click_hwnd(menu_hwnd)
                time.sleep(0.4)
                break

        exact_hwnd, exact_text = _find_top_left_text_control(hwnd, CYBOS_MENU_EXACT_TEXTS)
        if exact_hwnd:
            print("[INFO] CYBOS menu confirmed after click: '%s' hwnd=%d" % (exact_text, exact_hwnd))
            return True

        send_keys("{HOME}{ENTER}")
        print("[INFO] Sent HOME+ENTER fallback for CYBOS menu selection.")
        time.sleep(0.4)

        exact_hwnd, exact_text = _find_top_left_text_control(hwnd, CYBOS_MENU_EXACT_TEXTS)
        if exact_hwnd:
            print("[INFO] CYBOS menu confirmed after keyboard fallback: '%s' hwnd=%d" % (exact_text, exact_hwnd))
            return True

    print("[WARN] Could not explicitly confirm CYBOS menu selection.")
    _dump_children(hwnd, "CYBOS Starter - menu verify failed")
    return False


def _get_window_rect_safe(hwnd):
    try:
        return win32gui.GetWindowRect(hwnd)
    except Exception:
        return None


def _is_control_enabled(hwnd):
    try:
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        return not (style & win32con.WS_DISABLED)
    except Exception:
        return False


def _post_button_click(btn_hwnd):
    try:
        win32gui.PostMessage(btn_hwnd, win32con.BM_CLICK, 0, 0)
        print("[INFO] BM_CLICK sent: hwnd=%d text='%s'" % (btn_hwnd, win32gui.GetWindowText(btn_hwnd)))
        return True
    except Exception as exc:
        print("[WARN] BM_CLICK failed hwnd=%d: %s" % (btn_hwnd, exc))
        return False


def _set_edit_text(edit_hwnd, text):
    try:
        ctypes.windll.user32.SendMessageW(edit_hwnd, win32con.WM_SETTEXT, 0, text)
        return True
    except Exception as exc:
        print("[WARN] WM_SETTEXT failed hwnd=%d: %s" % (edit_hwnd, exc))
        return False


def _force_foreground(hwnd):
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


def _activate_window(hwnd):
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.15)
        _force_foreground(hwnd)
        time.sleep(0.25)
    except Exception:
        pass


def _is_connected():
    try:
        cp = win32com.client.Dispatch("CpUtil.CpCybos")
        return cp.IsConnect == 1
    except Exception:
        return False


def _load_credential():
    """Windows Credential Manager에서 ID/PW 읽기.

    CredEnumerate(flags=0)는 CRED_TYPE_GENERIC을 빠뜨리는 경우가 있으므로
    CredRead로 타입을 명시해서 순서대로 시도한다.
      1. CRED_TYPE_GENERIC (1)  -- cmdkey /add 기본값
      2. CRED_TYPE_DOMAIN_PASSWORD (2)  -- 도메인 자격증명 (blob 비어있을 수 있음)
    """
    if PASSWORD_OVERRIDE:
        return "", PASSWORD_OVERRIDE

    CRED_TYPE_GENERIC         = 1
    CRED_TYPE_DOMAIN_PASSWORD = 2

    for cred_type in (CRED_TYPE_GENERIC, CRED_TYPE_DOMAIN_PASSWORD):
        try:
            cred = win32cred.CredRead(CRED_TARGET, cred_type, 0)
            username = cred.get("UserName", "")
            blob = cred.get("CredentialBlob", b"")
            if not blob:
                print("[DEBUG] blob empty, skipping: Target=%s Type=%d User=%s"
                      % (CRED_TARGET, cred_type, username))
                continue
            password = blob.decode("utf-16-le")
            print("[DEBUG] Credential loaded: Target=%s Type=%d User=%s"
                  % (CRED_TARGET, cred_type, username))
            return username, password
        except Exception as exc:
            print("[DEBUG] CredRead(Type=%d) failed: %s" % (cred_type, exc))

    print("[ERROR] Credential not found. Register it with:")
    print("  cmdkey /add:%s /user:YOUR_ID /pass:YOUR_PASSWORD" % CRED_TARGET)
    sys.exit(1)


def _find_window_by_keywords(keywords, require_visible=True):
    normalized_keywords = tuple(_normalize(keyword) for keyword in keywords)
    found = []

    def _enum(hwnd, _):
        try:
            if require_visible and not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd).strip()
            if not title:
                return
            normalized = _normalize(title)
            if any(keyword in normalized for keyword in normalized_keywords):
                found.append((hwnd, title))
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_enum, None)
    except Exception:
        pass
    return found


def _find_login_window_once():
    result = [None]

    def _enum(hwnd, _):
        if result[0]:
            return
        try:
            if not win32gui.IsWindowVisible(hwnd):
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


def _find_main_window_once():
    matches = _find_window_by_keywords(MAIN_WINDOW_KEYWORDS, require_visible=True)
    filtered = []
    normalized_excludes = [_normalize(keyword) for keyword in MAIN_WINDOW_EXCLUDE_KEYWORDS]

    for hwnd, title in matches:
        normalized = _normalize(title)
        if any(keyword in normalized for keyword in normalized_excludes):
            continue
        filtered.append((hwnd, title))

    if not filtered:
        return None

    def _area(hwnd):
        rect = _get_window_rect_safe(hwnd) or (0, 0, 0, 0)
        return max(0, rect[2] - rect[0]) * max(0, rect[3] - rect[1])

    filtered.sort(key=lambda item: _area(item[0]), reverse=True)
    return filtered[0]


def _wait_for_main_window(timeout=MAIN_WINDOW_TIMEOUT):
    print("[INFO] Waiting for Cybos5 main window...")
    for tick in range(timeout):
        found = _find_main_window_once()
        if found:
            hwnd, title = found
            print("[INFO] Cybos5 main window found: '%s' hwnd=%d" % (title, hwnd))
            return hwnd, title
        time.sleep(1)
        if tick % 5 == 4:
            print("[INFO] Waiting for Cybos5 main window... %d/%ds" % (tick + 1, timeout))
    return None, None


def _is_minimized(hwnd):
    try:
        return win32gui.GetWindowPlacement(hwnd)[1] == win32con.SW_SHOWMINIMIZED
    except Exception:
        return False


_SC_RESTORE = 0xF120  # WM_SYSCOMMAND SC_RESTORE


def _restore_to_previous_size(hwnd, title):
    """Cybos 창을 이전 크기로 복원 (최대화/최소화 → 이전 크기, SW_RESTORE)."""
    time.sleep(0.3)

    # Method 1: WM_SYSCOMMAND SC_RESTORE
    try:
        win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, _SC_RESTORE, 0)
        time.sleep(0.4)
        show_cmd = win32gui.GetWindowPlacement(hwnd)[1]
        if show_cmd == win32con.SW_SHOWNORMAL:
            print("[INFO] Cybos5 restored via WM_SYSCOMMAND: '%s' hwnd=%d" % (title, hwnd))
            return True
    except Exception as exc:
        print("[WARN] WM_SYSCOMMAND SC_RESTORE failed: %s" % exc)

    # Method 2: ShowWindow SW_RESTORE
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.4)
        show_cmd = win32gui.GetWindowPlacement(hwnd)[1]
        if show_cmd == win32con.SW_SHOWNORMAL:
            print("[INFO] Cybos5 restored via ShowWindow SW_RESTORE: '%s' hwnd=%d" % (title, hwnd))
            return True
        print("[WARN] Restore attempted but show_cmd=%d: '%s' hwnd=%d" % (show_cmd, title, hwnd))
    except Exception as exc:
        print("[WARN] ShowWindow SW_RESTORE failed: %s" % exc)

    return False


def _restore_main_window(hwnd, title):
    try:
        placement = win32gui.GetWindowPlacement(hwnd)
        show_cmd = placement[1]
    except Exception as exc:
        print("[WARN] Failed to read main window placement for '%s': %s" % (title, exc))
        return False

    print("[INFO] Cybos5 main window state before adjust: show_cmd=%s title='%s' hwnd=%d" % (show_cmd, title, hwnd))
    rect = _get_window_rect_safe(hwnd)
    if not rect:
        print("[WARN] Failed to read main window rect for '%s'" % title)
        return False

    left, top, right, bottom = rect
    width = max(0, right - left)
    height = max(0, bottom - top)

    try:
        _force_foreground(hwnd)

        # Expect the middle title-bar button at the top-right cluster:
        # minimize | restore | close
        button_width = max(28, min(52, int(width * 0.03)))
        button_height = max(20, min(36, int(height * 0.03)))
        restore_x = right - int(button_width * 1.5)
        restore_y = top + int(button_height * 0.6)

        print("[INFO] Clicking Cybos restore button at top-right middle: (%d, %d)" % (restore_x, restore_y))
        clicked = _physical_click_point(restore_x, restore_y, "Cybos restore button")
        if clicked:
            time.sleep(0.7)
            _force_foreground(hwnd)
            print("[INFO] Cybos5 main window adjusted via restore-button click: '%s' hwnd=%d" % (title, hwnd))
            return True

        print("[WARN] Restore-button click did not succeed; falling back to SW_RESTORE.")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.7)
        _force_foreground(hwnd)
        print("[INFO] Cybos5 main window adjusted via SW_RESTORE fallback: '%s' hwnd=%d" % (title, hwnd))
        return True
    except Exception as exc:
        print("[WARN] Restore-button flow failed for '%s': %s" % (title, exc))
        return False


def _collect_edits(parent_hwnd):
    edits = [
        child for child in _enum_children(parent_hwnd)
        if win32gui.GetClassName(child) == "Edit" and win32gui.IsWindowVisible(child)
    ]
    edits.sort(key=lambda hwnd: (_get_window_rect_safe(hwnd) or (0, 9999, 0, 0))[1])
    return edits


def _find_id_password_edits(parent_hwnd):
    edits = _collect_edits(parent_hwnd)
    if not edits:
        return None, None
    return edits[0], edits[-1] if len(edits) >= 2 else None


def _find_password_confirm_dialog():
    keywords = [u"비밀번호", u"확인", u"CYBOS"]
    matches = _find_window_by_keywords(keywords, require_visible=True)
    return matches[0][0] if matches else None


def _handle_password_confirm_dialog(timeout=5):
    print("[INFO] Waiting for password-confirm popup...")
    for _ in range(timeout):
        hwnd = _find_password_confirm_dialog()
        if hwnd:
            ok_btns = _find_child_by_exact_text(hwnd, PASSWORD_DIALOG_CONFIRM_TEXTS, class_name="Button")
            if ok_btns:
                _post_button_click(ok_btns[0][0])
            else:
                _activate_window(hwnd)
                send_keys("{ENTER}")
            return True
        time.sleep(1)
    return False


def _try_click_security(hwnd):
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

    _activate_window(hwnd)
    if btn_hwnd[0]:
        return _post_button_click(btn_hwnd[0])
    return False


def _handle_existing_connection_dialog(hwnd):
    print("[INFO] Existing-connection dialog found.")
    _activate_window(hwnd)
    found_btns = _find_child_by_exact_text(hwnd, EXISTING_CONNECTION_BUTTON_TEXTS, class_name="Button")
    if not found_btns:
        found_btns = _find_child_by_text_contains(hwnd, [u"기존", u"접속"], class_name="Button")
    if found_btns:
        return _post_button_click(found_btns[0][0])

    print("[WARN] Existing-connection button not found, sending Enter fallback.")
    send_keys("{ENTER}")
    return True


def _handle_already_running_dialog(hwnd):
    child_texts = _collect_child_texts(hwnd)
    joined = u" ".join(child_texts)
    normalized = _normalize(joined)
    if not any(_normalize(keyword) in normalized for keyword in ALREADY_RUNNING_DIALOG_KEYWORDS):
        return False

    print("[INFO] Already-running confirmation dialog detected.")
    _dump_children(hwnd, "Already Running Dialog")
    _activate_window(hwnd)

    found_btns = _find_child_by_exact_text(hwnd, ALREADY_RUNNING_CONFIRM_TEXTS, class_name="Button")
    if not found_btns:
        found_btns = _find_child_by_text_contains(hwnd, [u"예", u"YES"], class_name="Button")

    if found_btns:
        btn_hwnd, btn_text = found_btns[0]
        print("[INFO] Clicking already-running confirmation: '%s' hwnd=%d" % (btn_text, btn_hwnd))
        _post_button_click(btn_hwnd)
    else:
        print("[WARN] Confirmation button not found; sending Enter fallback.")
        send_keys("{ENTER}")

    time.sleep(1.0)
    return True


def _wait_for_login_or_existing_connection(timeout=LOGIN_WAIT_TIMEOUT):
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

    cb_ref = _WinEventProcType(_win_event_cb)
    hook_handle = ctypes.windll.user32.SetWinEventHook(
        _EVENT_OBJECT_SHOW, _EVENT_OBJECT_SHOW,
        0, cb_ref, 0, 0,
        _WINEVENT_OUTOFCONTEXT | _WINEVENT_SKIPOWNPROCESS,
    )

    print("[INFO] Waiting for security dialog, login window, or existing-connection dialog...")
    start = time.time()
    msg = ctypes.wintypes.MSG()

    try:
        iterations = timeout * 5
        for tick in range(iterations):
            elapsed = time.time() - start

            while ctypes.windll.user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

            sec_hwnd = hook_found[0]
            if sec_hwnd:
                _try_click_security(sec_hwnd)
                hook_found[0] = None

            login_hwnd = _find_login_window_once()
            if login_hwnd:
                title = win32gui.GetWindowText(login_hwnd)
                if _handle_already_running_dialog(login_hwnd):
                    continue
                print("[INFO] Login window found: '%s' hwnd=%d" % (title, login_hwnd))
                return ("login", login_hwnd)

            existing = _find_window_by_keywords(EXISTING_CONNECTION_DIALOG_KEYWORDS, require_visible=True)
            if existing:
                hwnd, title = existing[0]
                print("[INFO] Existing-connection dialog found: '%s' hwnd=%d" % (title, hwnd))
                return ("existing", hwnd)

            if tick % 50 == 49:
                print("[INFO] Waiting... %.0f/%ds" % (elapsed, timeout))

            time.sleep(0.2)
    finally:
        if hook_handle:
            ctypes.windll.user32.UnhookWinEvent(hook_handle)

    return (None, None)


def _perform_login(hwnd, user_id, password):
    _activate_window(hwnd)
    _dump_children(hwnd, "CYBOS Starter")
    _ensure_cybos_menu_selected(hwnd)
    id_edit, pw_edit = _find_id_password_edits(hwnd)
    if not id_edit or not pw_edit:
        print("[ERROR] Could not find login Edit controls.")
        return False

    print("[INFO] Filling login credentials...")
    if user_id:
        if not _set_edit_text(id_edit, user_id):
            _activate_window(hwnd)
            send_keys("^a{BACKSPACE}")
            send_keys(user_id)

    if not _set_edit_text(pw_edit, password):
        _activate_window(hwnd)
        send_keys("{TAB}")
        time.sleep(0.1)
        send_keys("^a{BACKSPACE}")
        send_keys(password)

    time.sleep(0.3)
    _activate_window(hwnd)
    send_keys("{ENTER}")
    print("[INFO] Enter sent to login window.")
    time.sleep(0.5)

    login_btns = _find_child_by_exact_text(hwnd, LOGIN_BUTTON_TEXTS, class_name="Button")
    if not login_btns:
        login_btns = _find_child_by_text_contains(hwnd, [u"로그인", u"모의"], class_name="Button")
    if login_btns:
        btn_hwnd, btn_text = login_btns[0]
        print("[INFO] Login button found: '%s' hwnd=%d" % (btn_text, btn_hwnd))
        _post_button_click(btn_hwnd)
        time.sleep(0.5)
    else:
        all_buttons = [
            btn for btn in _find_child_by_class(hwnd, "Button", visible_only=True)
            if _is_control_enabled(btn)
        ]
        if all_buttons:
            all_buttons.sort(
                key=lambda btn: (
                    ((_get_window_rect_safe(btn) or (0, 0, 0, 0))[2] - (_get_window_rect_safe(btn) or (0, 0, 0, 0))[0]) *
                    ((_get_window_rect_safe(btn) or (0, 0, 0, 0))[3] - (_get_window_rect_safe(btn) or (0, 0, 0, 0))[1])
                ),
                reverse=True,
            )
            btn_hwnd = all_buttons[0]
            btn_text = win32gui.GetWindowText(btn_hwnd)
            print("[INFO] Login button fallback selected: '%s' hwnd=%d" % (btn_text, btn_hwnd))
            _post_button_click(btn_hwnd)
            time.sleep(0.5)
        else:
            print("[WARN] Login button not found after Enter; keeping Enter-only path.")
            _dump_children(hwnd, "CYBOS Starter - no login button found")
    return True


def _handle_mock_select_dialog(timeout=MOCK_POPUP_TIMEOUT, min_wait=MOCK_POPUP_MIN_WAIT):
    print("[INFO] Waiting for mock-investment popup...")

    if min_wait > 0:
        for waited in range(min_wait):
            if _is_connected():
                print("[INFO] Connected before mock popup handling.")
                return True
            time.sleep(1)
            if (waited + 1) % 5 == 0:
                print("[INFO] Mock popup minimum wait... %d/%ds" % (waited + 1, min_wait))
        send_keys("{ENTER}")
        print("[INFO] Sent Enter after minimum wait for mock popup.")
        time.sleep(3)

    for tick in range(timeout):
        if _is_connected():
            print("[INFO] Already connected during mock popup wait.")
            return True

        candidates = _find_window_by_keywords(MOCK_DIALOG_KEYWORDS, require_visible=True)
        for hwnd, title in candidates:
            print("[INFO] Mock popup found: '%s' hwnd=%d" % (title, hwnd))
            _activate_window(hwnd)
            _dump_children(hwnd, "Mock Select")

            found_btns = _find_child_by_exact_text(hwnd, MOCK_ACCESS_BUTTON_TEXTS, class_name="Button")
            if not found_btns:
                found_btns = _find_child_by_text_contains(hwnd, [u"모의", u"접속"], class_name="Button")

            if found_btns:
                _post_button_click(found_btns[0][0])
                return True

            print("[WARN] Mock popup button not found, sending Enter fallback.")
            _dump_children(hwnd, "Mock Select - no button found")
            send_keys("{ENTER}")
            return True

        if tick % 5 == 4:
            print("[INFO] Waiting for mock popup... %d/%ds" % (tick + 1, timeout))
        time.sleep(1)

    print("[WARN] Mock popup did not appear within timeout.")
    return False


def _find_cpstart_main_windows():
    """CpStart.exe 소유 StSdkMainWndCN 창 목록 반환 (vis=0 포함, 면적 내림차순)."""
    try:
        import psutil
        cpstart_pids = {p.pid for p in psutil.process_iter(['pid', 'name'])
                        if (p.info.get('name') or '').lower() == 'cpstart.exe'}
    except Exception:
        cpstart_pids = set()

    results = []

    def _cb(hwnd, _):
        try:
            if win32gui.GetClassName(hwnd) != u'StSdkMainWndCN':
                return
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if cpstart_pids and pid not in cpstart_pids:
                    return
            except Exception:
                pass
            rect = _get_window_rect_safe(hwnd) or (0, 0, 0, 0)
            w, h = rect[2] - rect[0], rect[3] - rect[1]
            title = win32gui.GetWindowText(hwnd) or u'(StSdkMainWndCN)'
            results.append((hwnd, title, w * h))
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_cb, None)
    except Exception:
        pass
    results.sort(key=lambda x: -x[2])
    return results


def _minimize_cpstart_windows():
    """StSdkMainWndCN (CpStart.exe) 창 전체 최소화 — vis=0 창에도 동작."""
    wins = _find_cpstart_main_windows()
    if not wins:
        print("[INFO] No StSdkMainWndCN windows found to minimize.")
        return False

    minimized = 0
    for hwnd, title, area in wins:
        print("[INFO] Minimizing StSdkMainWndCN hwnd=%d area=%d title=%r" % (hwnd, area, title))
        try:
            win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0)
            time.sleep(0.2)
        except Exception as exc:
            print("[WARN] PostMessage SC_MINIMIZE failed hwnd=%d: %s" % (hwnd, exc))
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            time.sleep(0.2)
        except Exception as exc:
            print("[WARN] ShowWindow SW_MINIMIZE failed hwnd=%d: %s" % (hwnd, exc))
        try:
            show_cmd = win32gui.GetWindowPlacement(hwnd)[1]
            if show_cmd == win32con.SW_SHOWMINIMIZED:
                print("[INFO] StSdkMainWndCN minimized OK: hwnd=%d" % hwnd)
                minimized += 1
            else:
                print("[WARN] StSdkMainWndCN not minimized (show_cmd=%d): hwnd=%d" % (show_cmd, hwnd))
        except Exception:
            pass

    return minimized > 0


def _find_bos_main_windows():
    """Bos.exe 소유 대형 가시창 탐색 (실제 Cybos5 HTS 화면)."""
    try:
        import psutil
        bos_pids = {p.pid for p in psutil.process_iter(['pid', 'name'])
                    if (p.info.get('name') or '').lower() == 'bos.exe'}
    except Exception:
        bos_pids = set()

    results = []

    def _cb(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if bos_pids and pid not in bos_pids:
                    return
            except Exception:
                pass
            rect = _get_window_rect_safe(hwnd) or (0, 0, 0, 0)
            w, h = rect[2] - rect[0], rect[3] - rect[1]
            if w * h < 200000:
                return
            title = win32gui.GetWindowText(hwnd)
            results.append((hwnd, title, w * h))
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_cb, None)
    except Exception:
        pass
    results.sort(key=lambda x: -x[2])
    return results


def _restore_bos_windows():
    """Bos.exe HTS 메인 창을 이전 크기로 복원 (최대화 → 이전 크기, SW_RESTORE)."""
    wins = _find_bos_main_windows()
    if not wins:
        print("[INFO] No Bos.exe HTS windows found to restore.")
        return False

    restored = 0
    for hwnd, title, area in wins:
        print("[INFO] Restoring Bos.exe hwnd=%d area=%d title=%r" % (hwnd, area, title[:50]))
        # Method 1: WM_SYSCOMMAND SC_RESTORE
        try:
            win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, _SC_RESTORE, 0)
            time.sleep(0.4)
        except Exception as exc:
            print("[WARN] PostMessage SC_RESTORE failed hwnd=%d: %s" % (hwnd, exc))
        # Method 2: ShowWindow SW_RESTORE (MAXIMIZED/MINIMIZED → 이전 크기)
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.4)
        except Exception as exc:
            print("[WARN] ShowWindow SW_RESTORE failed hwnd=%d: %s" % (hwnd, exc))
        # 검증
        try:
            show_cmd = win32gui.GetWindowPlacement(hwnd)[1]
            if show_cmd == win32con.SW_SHOWNORMAL:
                print("[INFO] Bos.exe HTS restored OK (SW_SHOWNORMAL): hwnd=%d" % hwnd)
                restored += 1
            else:
                print("[WARN] Bos.exe restore result show_cmd=%d: hwnd=%d" % (show_cmd, hwnd))
        except Exception:
            pass

    return restored > 0


def _launch_ncstarter():
    if not os.path.exists(CYBOS_EXE):
        print("[ERROR] Starter executable not found: %s" % CYBOS_EXE)
        return False

    exe_dir = os.path.dirname(CYBOS_EXE)
    try:
        win32api.ShellExecute(0, "open", CYBOS_EXE, CYBOS_ARGS, exe_dir, win32con.SW_SHOW)
        print("[INFO] ncStarter launched.")
    except Exception as exc:
        print("[WARN] ShellExecute failed (%s); trying subprocess." % exc)
        try:
            if CYBOS_ARGS:
                subprocess.Popen([CYBOS_EXE, CYBOS_ARGS], cwd=exe_dir)
            else:
                subprocess.Popen([CYBOS_EXE], cwd=exe_dir)
        except Exception as exc2:
            print("[ERROR] Failed to launch starter: %s" % exc2)
            return False
    return True


def autologin():
    user_id, password = _load_credential()
    if not password:
        print("[ERROR] Password is empty.")
        return False

    if not _launch_ncstarter():
        return False

    flow_kind, hwnd = _wait_for_login_or_existing_connection(timeout=LOGIN_WAIT_TIMEOUT)
    if flow_kind == "login":
        if not _perform_login(hwnd, user_id, password):
            return False
        _handle_password_confirm_dialog(timeout=5)
        _handle_mock_select_dialog(timeout=MOCK_POPUP_TIMEOUT, min_wait=MOCK_POPUP_MIN_WAIT)
    elif flow_kind == "existing":
        _handle_existing_connection_dialog(hwnd)
    else:
        print("[ERROR] Neither login window nor existing-connection dialog appeared.")
        return False

    preconnect_hwnd, preconnect_title = _wait_for_main_window(timeout=MAIN_WINDOW_TIMEOUT)
    if preconnect_hwnd:
        _restore_main_window(preconnect_hwnd, preconnect_title)
    else:
        print("[WARN] Cybos5 main window was not found before COM connection wait.")

    print("[INFO] Waiting for COM connection...")
    for i in range(CONNECT_TIMEOUT):
        if _is_connected():
            cp = win32com.client.Dispatch("CpUtil.CpCybos")
            time.sleep(1)  # 창 안정화 대기

            # ── 이전 크기 복원 3단계 ──────────────────────────────────
            # Step 1: Bos.exe HTS 메인 창 → 이전 크기 복원 (최우선)
            bos_ok = _restore_bos_windows()

            # Step 2: StSdkMainWndCN 배경창 최소화 (CpStart.exe, vis=0 포함)
            _minimize_cpstart_windows()

            # Step 3: 키워드 기반 fallback (Bos.exe 미감지 시, 30초 대기)
            if not bos_ok:
                print("[INFO] Bos.exe not found; falling back to keyword window search...")
                hwnd, title = _wait_for_main_window(timeout=MAIN_WINDOW_TIMEOUT)
                if hwnd:
                    _restore_to_previous_size(hwnd, title)
                else:
                    print("[WARN] Cybos5 HTS window could not be restored via any method.")
            # ──────────────────────────────────────────────────────────

            print("[OK] Connected (ServerType=%s)" % cp.ServerType)
            return True
        time.sleep(1)
        if i % 10 == 9:
            print("[INFO] Still waiting for COM connection... %ds" % (i + 1))

    print("[ERROR] COM connection timed out.")
    return False


if __name__ == "__main__":
    success = autologin()
    sys.exit(0 if success else 1)
