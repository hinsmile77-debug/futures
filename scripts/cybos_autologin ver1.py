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
PASSWORD_OVERRIDE = None         # 배포형에서는 Credential Manager만 사용
WAIT_RESULT_CONNECTED = 0        # 기존 연결 재사용으로 로그인 창 없이 연결 완료된 경우
WAIT_RESULT_STARTED = -1         # CYBOS Starter는 떴지만 아직 로그인 입력 전인 경우
WAIT_RESULT_NOTICE = -2          # 공지사항 창이 떠서 API 연결 성공으로 볼 수 있는 경우

# kill 대상 (ncStarter 먼저, CpStart 나중 -- 순서 중요)
CYBOS_PROC_NAMES = ["_ncstarter_.exe", "cpstart.exe"]
SECURITY_BUTTON_TEXTS = {u"사용안함", u"사용 안함"}
LOGIN_WINDOW_TITLES   = {u"CYBOS Starter", u"CYBOS Plus"}
LOGIN_WINDOW_EXCLUDE_KEYWORDS = [u"MIREUK", u"LAUNCHER", u"PYCHARM", u"VISUAL STUDIO CODE", u"VSCODE"]
LOGIN_BUTTON_TEXTS    = {u"로그인", u"확 인", u"확인", u"ENTER", u"enter"}
PASSWORD_DIALOG_CONFIRM_TEXTS = {u"확인", u"예", u"Yes", u"OK"}
EXISTING_CONNECTION_DIALOG_KEYWORDS = [u"기존 연결 선택", u"기존연결선택", u"기존 연결"]
EXISTING_CONNECTION_BUTTON_TEXTS = {u"기존 연결로 접속", u"기존연결로접속"}
MOCK_ACCESS_BUTTON_TEXTS = {
    u"모의투자\r\n접속", u"모의투자\n접속", u"모의투자접속",
    u"모의투자 접속", u"접속",
}
MOCK_DIALOG_KEYWORDS = [u"모의투자 선택", u"모의투자선택", u"모의투자", u"접속"]
SECURITY_DIALOG_EXACT = u"CYBOS"
CYBOS_WINDOW_DEBUG_KEYWORDS = [u"CYBOS", u"DAISHIN", u"STARTER", u"NOTICE", u"모의투자", u"공지사항"]
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


def _find_login_edits(parent_hwnd):
    """로그인 창의 가시 Edit 후보들을 위에서 아래 순으로 반환"""
    edits = [c for c in _enum_children(parent_hwnd)
             if win32gui.GetClassName(c) == "Edit" and win32gui.IsWindowVisible(c)]

    if not edits:
        custom_edits = [c for c in _enum_children(parent_hwnd)
                        if win32gui.IsWindowVisible(c)]
        for c in custom_edits:
            try:
                cn = win32gui.GetClassName(c)
                if any(kw in cn.upper() for kw in ("EDIT", "RICHEDIT", "TEXTBOX")):
                    edits.append(c)
            except Exception:
                pass

    unique = []
    seen = set()
    for edit in edits:
        if edit not in seen:
            unique.append(edit)
            seen.add(edit)

    unique.sort(key=lambda h: _get_window_rect_safe(h) or (0, 999999, 0, 0))
    return unique


def _find_id_edit(parent_hwnd):
    """로그인 창의 ID Edit 컨트롤을 찾는다."""
    edits = _find_login_edits(parent_hwnd)
    if len(edits) >= 2:
        return edits[0]
    return edits[0] if edits else None


def _find_password_edit(parent_hwnd):
    """로그인 창에서 비밀번호 입력 Edit 컨트롤을 찾는다.

    휴리스틱 (우선순위):
      1. 자식 중 가장 큰 Edit (높이 기준) — Cybos Starter 전형적 패턴
      2. 마지막에 위치한 Edit (y 좌표 기준) — ID 필드 다음에 비밀번호 필드
      3. Edit 클래스 중 하나 — fallback
    """
    edits = _find_login_edits(parent_hwnd)

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


def _is_login_window_ready(hwnd):
    """실제 로그인 입력이 가능한 창인지 확인"""
    if not hwnd:
        return False

    try:
        if not win32gui.IsWindow(hwnd):
            return False
        if win32gui.GetWindowText(hwnd) not in LOGIN_WINDOW_TITLES:
            return False
    except Exception:
        return False

    try:
        if _find_password_edit(hwnd):
            return True
    except Exception:
        pass

    try:
        login_btns = _find_child_by_exact_text(hwnd, LOGIN_BUTTON_TEXTS, class_name="Button")
        if login_btns:
            return True
        login_btns = _find_child_by_text_contains(hwnd, list(LOGIN_BUTTON_TEXTS))
        return bool(login_btns)
    except Exception:
        return False


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


def _is_foreground_window(hwnd):
    try:
        return win32gui.GetForegroundWindow() == hwnd
    except Exception:
        return False


def _send_keys_to_window(hwnd, keys, label):
    _activate_and_wait_for_window(hwnd)
    if not _is_foreground_window(hwnd):
        print("[WARN] %s 실패 -- 대상 창을 foreground로 만들지 못함" % label)
        return False

    send_keys(keys)
    print("[INFO] %s 전송: %s" % (label, keys))
    return True


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
        print("[WARN] PASSWORD_OVERRIDE가 설정되어 Credential Manager를 건너뜁니다.")
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


def _load_credential_checked():
    """Credential Manager에서 ID/PW를 안정적으로 읽고 비어 있으면 실패 처리."""

    def _decode_credential_blob(blob):
        if blob is None:
            return ""
        if isinstance(blob, str):
            return blob.strip("\x00").strip()
        if not blob:
            return ""
        for encoding in ("utf-16-le", "utf-8", "cp949"):
            try:
                return blob.decode(encoding).rstrip("\x00").strip()
            except Exception:
                pass
        return ""

    def _extract_credential(cred):
        user_id = (cred.get("UserName") or "").strip()
        password = _decode_credential_blob(cred.get("CredentialBlob"))
        return user_id, password

    if PASSWORD_OVERRIDE:
        return "", PASSWORD_OVERRIDE

    try:
        cred = win32cred.CredRead(CRED_TARGET, win32cred.CRED_TYPE_GENERIC, 0)
        user_id, password = _extract_credential(cred)
        print("[INFO] Credential loaded via CredRead: target=%s user_len=%d password_len=%d"
              % (CRED_TARGET, len(user_id), len(password)))
        if user_id and password:
            return user_id, password
    except Exception as e:
        print("[DEBUG] CredRead 오류: %s" % e)

    try:
        all_creds = win32cred.CredEnumerate(None, 0) or []
        for cred in all_creds:
            target_name = (cred.get("TargetName") or "").strip()
            if target_name.lower() == CRED_TARGET.lower():
                user_id, password = _extract_credential(cred)
                print("[INFO] Credential loaded via CredEnumerate: target=%s user_len=%d password_len=%d"
                      % (target_name, len(user_id), len(password)))
                if user_id and password:
                    return user_id, password
    except Exception as e:
        print("[DEBUG] CredEnumerate fallback 오류: %s" % e)

    print("[ERROR] 자격 증명을 찾았지만 ID 또는 비밀번호가 비어 있습니다.")
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


def _find_window_by_title_contains(keywords, require_visible=True):
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


def _log_cybos_window_candidates(label):
    candidates = _find_window_by_title_contains(CYBOS_WINDOW_DEBUG_KEYWORDS, require_visible=True)
    if not candidates:
        print("[INFO] %s: CYBOS 계열 창 후보 없음" % label)
        return

    rows = []
    for hwnd, title in candidates[:10]:
        try:
            cls = win32gui.GetClassName(hwnd)
            child_count = len(_enum_children(hwnd))
        except Exception:
            cls = "?"
            child_count = -1
        rows.append("%s(hwnd=%d cls=%s children=%d)" % (title, hwnd, cls, child_count))
    print("[INFO] %s: CYBOS 계열 창 후보=%s" % (label, rows))


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


def _close_notice_windows():
    """연결 후 뒤늦게 뜨는 공지사항 창을 닫기"""
    dismissed = 0
    candidates = _find_window_by_keywords([u"공지사항"], require_visible=True)
    for hwnd, title in candidates:
        try:
            if not win32gui.IsWindowVisible(hwnd):
                continue
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            dismissed += 1
            print("[INFO] 공지사항 창 닫음: '%s' hwnd=%d" % (title, hwnd))
            time.sleep(0.3)
        except Exception as e:
            print("[WARN] 공지사항 창 닫기 실패 '%s' hwnd=%d: %s" % (title, hwnd, e))
    return dismissed


def _has_notice_window():
    """공지사항 창이 떠 있는지 확인"""
    candidates = _find_window_by_keywords([u"공지사항"], require_visible=True)
    return bool(candidates)


# -- 창 탐지 --------------------------------------------------------------------

def _find_login_window_once():
    """정확한 제목 일치로 로그인 창 탐지"""
    SKIP_CLASSES = {"Shell_TrayWnd", "CabinetWClass", "ExploreWClass", "ShellTabWindowClass"}
    found = []

    def _enum(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            if win32gui.GetClassName(hwnd) in SKIP_CLASSES:
                return
            title = win32gui.GetWindowText(hwnd).strip()
            if title in LOGIN_WINDOW_TITLES:
                child_count = len(_enum_children(hwnd))
                score = child_count + 1000
                found.append((score, hwnd))
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_enum, None)
    except Exception:
        pass
    if not found:
        return None
    found.sort(key=lambda item: item[0], reverse=True)
    return found[0][1]


def _resolve_login_window(hwnd, timeout=8.0):
    """로그인 창 핸들을 재검증하고, 컨트롤이 붙은 새 hwnd가 있으면 교체"""
    deadline = time.time() + timeout
    last_seen = hwnd

    while time.time() < deadline:
        candidates = []
        current = _find_login_window_once()
        if current:
            candidates.append(current)
        if hwnd and hwnd not in candidates:
            candidates.append(hwnd)
        if last_seen and last_seen not in candidates:
            candidates.append(last_seen)

        for candidate in candidates:
            if not candidate:
                continue
            try:
                if not win32gui.IsWindow(candidate):
                    continue
                title = win32gui.GetWindowText(candidate)
                children = _enum_children(candidate)
                if title in LOGIN_WINDOW_TITLES and _is_login_window_ready(candidate):
                    print("[INFO] 로그인 창 재확인: hwnd=%d title='%s' children=%d ready=True"
                          % (candidate, title, len(children)))
                    return candidate
                last_seen = candidate
            except Exception:
                pass

        time.sleep(0.3)

    return last_seen


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


def _find_security_dialog_once():
    candidates = _find_window_by_title_contains([SECURITY_DIALOG_EXACT], require_visible=True)
    for hwnd, title in candidates:
        try:
            child_buttons = _find_child_by_exact_text(hwnd, SECURITY_BUTTON_TEXTS, class_name="Button")
            if child_buttons:
                return hwnd
            all_buttons = _find_child_by_class(hwnd, "Button", visible_only=True)
            if all_buttons and len(all_buttons) >= 2:
                return hwnd
        except Exception:
            pass
    return None


def _handle_existing_connection_dialog():
    """'기존 연결 선택' 팝업이 있으면 처리하고, 없으면 즉시 False 반환"""
    candidates = _find_window_by_keywords(EXISTING_CONNECTION_DIALOG_KEYWORDS, require_visible=True)
    if not candidates:
        return False

    print("[INFO] 기존 연결 선택 팝업 발견")

    for hwnd, title in candidates:
        if not win32gui.IsWindowVisible(hwnd):
            continue

        print("[INFO] 기존 연결 선택 창 발견: '%s' hwnd=%d" % (title, hwnd))
        _activate_and_wait_for_window(hwnd, title)
        _dump_children(hwnd, "기존 연결 선택 '%s'" % title)

        # 리스트가 있으면 첫 행이 선택되도록 대상 창에만 키 입력 보조
        list_views = _find_child_by_class(hwnd, "SysListView32", visible_only=True)
        if list_views:
            list_hwnd = list_views[0]
            _focus_control(list_hwnd)
            time.sleep(0.1)
            _send_keys_to_window(hwnd, "{HOME}", "기존 연결 목록 첫 행 선택")

        btns = _find_child_by_exact_text(hwnd, EXISTING_CONNECTION_BUTTON_TEXTS, class_name="Button")
        if not btns:
            btns = _find_child_by_text_contains(hwnd, [u"기존 연결"], class_name="Button")

        if btns:
            for btn_hwnd, btn_text in btns:
                if _is_control_enabled(btn_hwnd):
                    print("[INFO] 기존 연결 버튼 클릭: '%s' hwnd=%d" % (btn_text, btn_hwnd))
                    _post_button_click(btn_hwnd)
                    return True

            btn_hwnd, btn_text = btns[0]
            print("[INFO] 기존 연결 버튼(비활성 추정) 클릭 시도: '%s' hwnd=%d" % (btn_text, btn_hwnd))
            _post_button_click(btn_hwnd)
            return True

        print("[WARN] 기존 연결 버튼을 찾지 못함")
        _dump_children(hwnd, "기존 연결 선택(버튼 못찾음)")
        return False

    return False


# -- 핵심 대기 루프 -------------------------------------------------------------

def _wait_for_login_clicking_security(timeout=120):
    """
    ncStarter 시작 후 보안 다이얼로그와 로그인 창을 200ms 간격으로 동시 탐지.

    탐지 전략 (우선순위 순):
      1. SetWinEventHook(EVENT_OBJECT_SHOW) -- 창이 나타나는 순간 즉시 캐치
      2. FindWindowW / FindWindow 폴링
    로그인 창이 실제 입력 가능한 상태로 준비되면 hwnd 반환.
    기존 연결 재사용으로 이미 연결되면 WAIT_RESULT_CONNECTED 반환.
    공지사항 창이 뜨면 WAIT_RESULT_NOTICE 반환.
    timeout 초과 시 None 반환.
    """
    security_clicked = False
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
    existing_connection_handled = False
    last_login_wait_log = 0.0

    try:
        iterations = timeout * 5
        for tick in range(iterations):
            elapsed = time.time() - start

            while ctypes.windll.user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

            if not existing_connection_handled:
                if _handle_existing_connection_dialog():
                    existing_connection_handled = True
                    time.sleep(1.0)
                    continue

            if existing_connection_handled and _is_connected():
                print("[INFO] 기존 연결 재사용으로 CybosPlus 연결 확인 (%.1fs)" % elapsed)
                return WAIT_RESULT_CONNECTED

            if _has_notice_window():
                print("[INFO] 공지사항 창 감지 -- API 연결 성공으로 간주 (%.1fs)" % elapsed)
                return WAIT_RESULT_NOTICE

            if not security_clicked:
                sec_hwnd = hook_found[0]
                if not sec_hwnd:
                    sec_hwnd = ctypes.windll.user32.FindWindowW(None, SECURITY_DIALOG_EXACT)
                if not sec_hwnd:
                    sec_hwnd = win32gui.FindWindow(None, SECURITY_DIALOG_EXACT)
                if not sec_hwnd:
                    sec_hwnd = win32gui.FindWindow("#32770", SECURITY_DIALOG_EXACT)
                if not sec_hwnd:
                    sec_hwnd = _find_security_dialog_once()

                if sec_hwnd:
                    try:
                        vis = win32gui.IsWindowVisible(sec_hwnd)
                    except Exception:
                        vis = "?"
                    print("[INFO] 보안 다이얼로그 발견 hwnd=%d visible=%s (%.1fs)"
                          % (sec_hwnd, vis, elapsed))
                    _try_click_security(sec_hwnd)
                    security_clicked = True


            login_hwnd = _find_login_window_once()
            if login_hwnd:
                try:
                    title = win32gui.GetWindowText(login_hwnd)
                    ready = _is_login_window_ready(login_hwnd)
                    child_count = len(_enum_children(login_hwnd))
                except Exception:
                    title = "?"
                    ready = False
                    child_count = -1

                if ready:
                    print("[INFO] 로그인 창 발견: '%s' hwnd=%d children=%d ready=True (%.1fs)"
                          % (title, login_hwnd, child_count, elapsed))
                    return login_hwnd

                if elapsed - last_login_wait_log >= 3.0:
                    print("[INFO] 로그인 창 발견, 아직 입력 준비 안됨: '%s' hwnd=%d children=%d (%.1fs)"
                          % (title, login_hwnd, child_count, elapsed))
                    last_login_wait_log = elapsed

            if tick % 50 == 49:
                _log_cybos_window_candidates("대기 중 창 스캔")
                print("[INFO] 대기 중... %.0f/%ds  보안클릭=%s 기존연결처리=%s starter_seen=%s notice=%s"
                      % (elapsed, timeout, security_clicked, existing_connection_handled, bool(login_hwnd), _has_notice_window()))

            time.sleep(0.2)

    finally:
        if hook_handle:
            ctypes.windll.user32.UnhookWinEvent(hook_handle)
            print("[INFO] WinEventHook 해제")

    return None


# -- 로그인 수행 ----------------------------------------------------------------

def _perform_login(hwnd, user_id, password):
    """
    로그인 창에서 컨트롤 기반으로:
      1. ID / 비밀번호 Edit 컨트롤을 찾아 WM_SETTEXT 입력
      2. 로그인 Button 컨트롤을 찾아 BM_CLICK 또는 Enter

    절대 좌표 전혀 사용하지 않음.
    """
    hwnd = _resolve_login_window(hwnd, timeout=10.0)
    if not hwnd or not win32gui.IsWindow(hwnd):
        print("[ERROR] 로그인 창 hwnd 재확인 실패")
        return False

    _activate_and_wait_for_window(hwnd, "CYBOS Starter")
    time.sleep(0.5)

    # 자식 컨트롤이 늦게 붙는 환경을 고려해 짧게 한 번 더 재확인
    if not _enum_children(hwnd):
        hwnd = _resolve_login_window(hwnd, timeout=5.0)
        _activate_and_wait_for_window(hwnd, "CYBOS Starter")

    # 디버그: 컨트롤 덤프
    title = win32gui.GetWindowText(hwnd)
    children = _enum_children(hwnd)
    print("[INFO] 로그인 창 최종 확인: hwnd=%d title='%s' children=%d"
          % (hwnd, title, len(children)))
    _dump_children(hwnd, "로그인 창 '%s'" % title)

    # ── STEP 1: ID / 비밀번호 Edit 찾아 텍스트 입력 ──
    id_edit = _find_id_edit(hwnd)
    pw_edit = _find_password_edit(hwnd)
    if id_edit and pw_edit:
        print("[INFO] 아이디 Edit 컨트롤 발견: hwnd=%d" % id_edit)
        print("[INFO] 비밀번호 Edit 컨트롤 발견: hwnd=%d" % pw_edit)
        if user_id:
            if not _set_edit_text(id_edit, user_id):
                _focus_control(id_edit)
                time.sleep(0.15)
                if not _send_keys_to_window(hwnd, "^a{BACKSPACE}" + user_id, "아이디 send_keys fallback"):
                    print("[ERROR] 아이디 입력 실패 -- 안전하지 않은 전역 입력은 중단합니다.")
                    return False
        else:
            print("[ERROR] 로그인용 아이디가 비어 있습니다.")
            return False

        # 먼저 WM_SETTEXT로 시도 (백그라운드에서도 동작)
        if _set_edit_text(pw_edit, password):
            # WM_SETTEXT 성공 시 바로 확인
            pass
        else:
            # WM_SETTEXT 실패: 대상 창이 foreground일 때만 제한적으로 fallback
            _focus_control(pw_edit)
            time.sleep(0.15)
            if not _send_keys_to_window(hwnd, "^a{BACKSPACE}" + password, "비밀번호 send_keys fallback"):
                print("[ERROR] 비밀번호 입력 실패 -- 안전하지 않은 전역 입력은 중단합니다.")
                return False
    else:
        print("[ERROR] 아이디/비밀번호 Edit 컨트롤 미발견 -- 배포형에서는 Tab 탐색을 사용하지 않습니다.")
        return False

    time.sleep(0.3)

    # ── STEP 2: 로그인 버튼 찾아 BM_CLICK ──
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
        print("[WARN] 로그인 버튼 컨트롤 미발견 -- 대상 로그인창에 Enter fallback 시도")
        if not _send_keys_to_window(hwnd, "{ENTER}", "로그인 Enter fallback"):
            print("[ERROR] 로그인 버튼 컨트롤 미발견 및 Enter fallback 실패")
            return False

    return True


# -- 비밀번호 확인 팝업 ---------------------------------------------------------

def _find_password_confirm_dialog():
    """실제 CYBOS 로그인 실패 팝업 1개를 찾는다."""
    message_keywords = [u"아이디", u"비밀번호", u"확인해 주시기 바랍니다", u"확인해주시기 바랍니다"]
    matches = []

    def _enum(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd).strip()
            if title != u"CYBOS":
                return
            child_texts = _collect_child_texts(hwnd)
            joined = u" ".join(child_texts)
            if any(kw in joined for kw in message_keywords):
                matches.append((hwnd, title, child_texts))
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_enum, None)
    except Exception:
        pass
    return matches[0] if matches else None


def _handle_password_confirm_dialog(timeout=10):
    """실제 CYBOS 로그인 실패/확인 팝업만 탐지해서 닫는다."""
    message_keywords = [u"아이디", u"비밀번호", u"확인해 주시기 바랍니다", u"확인해주시기 바랍니다"]
    print("[INFO] 비밀번호 확인 팝업 대기 중...")

    for tick in range(timeout):
        matches = []

        def _enum(hwnd, _):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return
                title = win32gui.GetWindowText(hwnd).strip()
                if title != u"CYBOS":
                    return
                child_texts = _collect_child_texts(hwnd)
                joined = u" ".join(child_texts)
                if any(kw in joined for kw in message_keywords):
                    matches.append((hwnd, title, child_texts))
            except Exception:
                pass

        try:
            win32gui.EnumWindows(_enum, None)
        except Exception:
            pass

        for hwnd, title, child_texts in matches:
            ok_btns = _find_child_by_exact_text(hwnd, PASSWORD_DIALOG_CONFIRM_TEXTS, class_name="Button")
            if ok_btns:
                for btn_hwnd, btn_text in ok_btns:
                    if _is_control_enabled(btn_hwnd):
                        print("[ERROR] 로그인 실패 팝업 감지: '%s' text=%s" % (title, child_texts))
                        _post_button_click(btn_hwnd)
                        return True

            print("[ERROR] 로그인 실패 팝업 감지됐지만 확인 버튼을 찾지 못함: '%s' text=%s" % (title, child_texts))
            _dump_children(hwnd, "비밀번호 확인 팝업")
            return True

        time.sleep(1)
        if tick % 5 == 4:
            print("[INFO] 비밀번호 확인 팝업 대기... %d/%d초" % (tick + 1, timeout))

    print("[INFO] 비밀번호 확인 팝업 없음")
    return False


# -- 모의투자 선택 창 -----------------------------------------------------------

def _handle_mock_select_dialog(timeout=45, min_wait=0):
    """모의투자 선택 창을 찾아 '모의투자 접속' 버튼을 BM_CLICK"""
    print("[INFO] 모의투자 선택 창 대기 중...")

    if min_wait > 0:
        print("[INFO] 모의투자 선택 팝업 대기 보장... %d초" % min_wait)
        for waited in range(min_wait):
            if _find_password_confirm_dialog():
                print("[ERROR] 로그인 실패 팝업 감지 -- 모의투자 선택 대기를 중단합니다.")
                _handle_password_confirm_dialog(timeout=1)
                return "login_failed"
            if _is_connected():
                print("[INFO] 이미 연결되어 있어 모의투자 선택 창 처리를 생략합니다.")
                return True
            time.sleep(1)
            if (waited + 1) % 5 == 0:
                print("[INFO] 모의투자 팝업 최소 대기... %d/%d초" % (waited + 1, min_wait))
    for tick in range(timeout):
        if _find_password_confirm_dialog():
            print("[ERROR] 로그인 실패 팝업 감지 -- 모의투자 선택 대기를 중단합니다.")
            _handle_password_confirm_dialog(timeout=1)
            return "login_failed"
        if _is_connected():
            print("[INFO] 이미 연결되어 있어 모의투자 선택 창 처리를 생략합니다.")
            return True

        candidates = _find_window_by_keywords(MOCK_DIALOG_KEYWORDS, require_visible=True)
        for hwnd, title in candidates:
            if not win32gui.IsWindowVisible(hwnd):
                continue

            print("[INFO] 모의투자 선택 창 발견: '%s' hwnd=%d" % (title, hwnd))
            _activate_and_wait_for_window(hwnd, title)
            _dump_children(hwnd, "모의투자 선택 '%s'" % title)

            # 0차: 실제 UI 형태 확인 (콤보박스 + '모의투자 접속' 버튼)
            combo_boxes = _find_child_by_class(hwnd, "ComboBox", visible_only=True)
            direct_btns = _find_child_by_exact_text(
                hwnd,
                {u"모의투자\r\n접속", u"모의투자\n접속", u"모의투자 접속", u"모의투자접속"},
                class_name="Button",
            )
            if combo_boxes and direct_btns:
                btn_hwnd, btn_text = direct_btns[0]
                print("[INFO] 모의투자 선택 UI 확인: combo=%d, 접속버튼='%s' hwnd=%d"
                      % (len(combo_boxes), btn_text, btn_hwnd))
                _post_button_click(btn_hwnd)
                return True

            # 1차: 정확한 텍스트의 Button 컨트롤
            found_btns = _find_child_by_exact_text(hwnd, MOCK_ACCESS_BUTTON_TEXTS, class_name="Button")
            if not found_btns:
                # 2차: 부분 텍스트 매치
                found_btns = _find_child_by_text_contains(hwnd, [u"접속", u"모의"])
            if not found_btns:
                all_btns = _find_child_by_class(hwnd, "Button")
                found_btns = [
                    (btn, win32gui.GetWindowText(btn))
                    for btn in all_btns
                    if _is_control_enabled(btn) and u"접속" in win32gui.GetWindowText(btn)
                ]

            if found_btns:
                btn_hwnd, btn_text = found_btns[0]
                print("[INFO] '모의투자 접속' 버튼: '%s' hwnd=%d → BM_CLICK"
                      % (btn_text, btn_hwnd))
                _post_button_click(btn_hwnd)
                return True
            else:
                print("[WARN] 접속 버튼 컨트롤 미발견 -- 대상 창 Enter fallback 시도")
                _dump_children(hwnd, "모의투자 창 (버튼 못찾음)")
                return _send_keys_to_window(hwnd, "{ENTER}", "모의투자 선택 Enter fallback")

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

    user_id, password = _load_credential_checked()
    if not user_id or not password:
        print("[ERROR] 로그인용 자격 증명이 비어 있습니다. user_len=%d password_len=%d"
              % (len(user_id or ""), len(password or "")))
        return False

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
    login_attempted = False
    mock_select_handled = False
    if hwnd not in (WAIT_RESULT_CONNECTED, WAIT_RESULT_NOTICE):
        try:
            if not _perform_login(hwnd, user_id, password):
                print("[ERROR] 로그인 컨트롤 기반 자동화 실패 -- 배포형 안전 모드로 중단합니다.")
                sys.exit(1)
            login_attempted = True
            # 비밀번호 갱신 확인 다이얼로그 등 팝업 처리
            if _handle_password_confirm_dialog(timeout=5):
                print("[ERROR] CYBOS 로그인 실패 팝업 감지 -- 아이디/비밀번호를 확인하세요.")
                sys.exit(1)
        except Exception as e:
            print("[ERROR] UI 자동화 실패: %s" % e)
            sys.exit(1)
    elif hwnd == WAIT_RESULT_NOTICE:
        print("[INFO] 공지사항 창이 떠서 API 연결 성공으로 판단했습니다.")
    else:
        print("[INFO] 로그인 창 없이 기존 연결 재사용 경로로 진행합니다.")

    # STEP 4: 모의투자 선택 창
    if MOCK_MODE and (login_attempted or hwnd in (WAIT_RESULT_CONNECTED, WAIT_RESULT_NOTICE)):
        mock_result = _handle_mock_select_dialog(timeout=45, min_wait=MOCK_POPUP_MIN_WAIT)
        mock_select_handled = True
        if mock_result == "login_failed":
            print("[ERROR] CYBOS 로그인 실패 팝업 감지 -- 아이디/비밀번호를 확인하세요.")
            return False

    # STEP 5: 연결 완료 대기
    print("[INFO] 연결 대기 중 (최대 %d초)..." % CONNECT_TIMEOUT)
    for i in range(CONNECT_TIMEOUT):
        _dismiss_error_dialogs()
        if _find_password_confirm_dialog():
            _handle_password_confirm_dialog(timeout=1)
            print("[ERROR] CYBOS 로그인 실패 팝업 감지 -- 연결 대기를 중단합니다.")
            return False
        if _has_notice_window():
            for _ in range(5):
                if _close_notice_windows() == 0:
                    break
                time.sleep(0.5)
            print("[INFO] 공지사항 창 처리 완료 -- 미륵이 로딩 진행")
            return True
        if _is_connected():
            for _ in range(5):
                if _close_notice_windows() == 0:
                    break
                time.sleep(0.5)
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
