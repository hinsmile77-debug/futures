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
import io
import struct
import time
import subprocess
import os
import ctypes
import ctypes.wintypes

# CP949 터미널에서 em-dash 등 특수문자 인코딩 오류 방지
# CREON_PLUS.bat에 PYTHONIOENCODING=utf-8이 있지만 직접 실행 시 보장
if hasattr(sys.stdout, "buffer") and getattr(sys.stdout, "encoding", "").lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer") and getattr(sys.stderr, "encoding", "").lower() not in ("utf-8", "utf-8-sig"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

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
CRED_TARGET       = "cybosplus"  # CYBOS 기본값; CREON은 아래에서 "creon"으로 재설정
MOCK_MODE         = True         # True=모의투자, False=실투자
CONNECT_TIMEOUT   = 120          # 통합 루프(모의투자 팝업 + 연결 대기) 타임아웃 (초)
MAX_LOGIN_ATTEMPTS = 3           # 연결 실패 시 전체 재시도 횟수
MOCK_POPUP_MIN_WAIT = 8          # 구버전 호환용 상수 -- _wait_for_connection_and_mock 에서 미사용
PASSWORD_OVERRIDE = None         # Windows 자격증명 관리자(cybosplus)에서 읽음

# ── 브로커 지정: --broker creon|cybos 인수 우선, 없으면 exe 존재 여부로 자동 감지 ──
# CYBOS_PLUS.bat → --broker cybos
# CREON_PLUS.bat → --broker creon
_CREON_EXE_PATH = r"C:\CREON\STARTER\coStarter.exe"
_CYBOS_EXE_PATH = r"C:\DAISHIN\STARTER\ncStarter.exe"

_broker_override = None
for _i, _arg in enumerate(sys.argv[1:]):
    if _arg == "--broker" and _i + 2 <= len(sys.argv[1:]):
        _broker_override = sys.argv[_i + 2].lower()
        break
    elif _arg.startswith("--broker="):
        _broker_override = _arg.split("=", 1)[1].lower()
        break

_use_creon = (_broker_override == "creon") or (
    _broker_override is None and os.path.exists(_CREON_EXE_PATH)
)
_use_cybos = (_broker_override == "cybos") or (
    _broker_override is None and not _use_creon and os.path.exists(_CYBOS_EXE_PATH)
)

if _use_creon:
    BROKER_TYPE      = "creon"
    CYBOS_EXE        = _CREON_EXE_PATH
    CYBOS_ARGS       = ""
    CYBOS_PROC_NAMES = ["costarter.exe", "cpstart.exe"]
    CRED_TARGET      = "creonplus"  # CREON 전용 자격증명 (win32cred TargetName=creonplus)
elif _use_cybos:
    BROKER_TYPE      = "cybos"
    CYBOS_EXE        = _CYBOS_EXE_PATH
    CYBOS_ARGS       = "/prj:cp"
    CYBOS_PROC_NAMES = ["_ncstarter_.exe", "cpstart.exe"]
else:
    BROKER_TYPE      = "cybos"          # 파일 없으면 실행 시 오류
    CYBOS_EXE        = _CYBOS_EXE_PATH
    CYBOS_ARGS       = "/prj:cp"
    CYBOS_PROC_NAMES = ["_ncstarter_.exe", "cpstart.exe"]

# 보안 다이얼로그는 CYBOS 전용 -- CREON 흐름에는 없음
HAS_SECURITY_DIALOG   = BROKER_TYPE == "cybos"
SECURITY_DIALOG_EXACT = u"CYBOS"

# CREON 로그인 창 hwnd (autologin에서 설정 → _wait_for_connection_and_mock에서 사용)
_creon_starter_hwnd = None

SECURITY_BUTTON_TEXTS = {u"사용안함", u"사용 안함"}
LOGIN_WINDOW_TITLES   = {u"CYBOS Starter", u"CYBOS Plus", u"CREON Starter", u"CREON Plus"}
CYBOS_PLUS_MENU_EXACT_TEXTS = {u"CYBOS PLUS", u"CYBOS Plus", u"CREON PLUS", u"CREON Plus"}
CYBOS_PLUS_MENU_CANDIDATE_TEXTS = {
    u"CYBOS PLUS", u"CYBOS Plus", u"CYBOS", u"CYBOS Trader", u"CYBOS I", u"CYBOS Oneclick",
    u"CREON PLUS", u"CREON Plus", u"CREON", u"CREON Trader",
}
LOGIN_BUTTON_TEXTS    = {u"로그인", u"모의투자 로그인", u"모의투자로그인", u"확 인", u"확인", u"ENTER", u"enter"}
PASSWORD_DIALOG_CONFIRM_TEXTS = {u"확인", u"예", u"Yes", u"OK"}
MOCK_ACCESS_BUTTON_TEXTS = {
    u"모의투자\r\n접속", u"모의투자\n접속", u"모의투자접속",
    u"모의투자 접속", u"접속",
}
MOCK_DIALOG_KEYWORDS = [u"모의투자 선택", u"모의투자선택", u"모의투자", u"접속"]
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


def _looks_like_login_form(parent_hwnd):
    """owner-drawn 로그인 UI라도 폼 형태인지 대략 판별한다."""
    edit_count = 0
    for child in _enum_children(parent_hwnd):
        try:
            if win32gui.GetClassName(child) != "Edit":
                continue
            if win32gui.IsWindowVisible(child):
                edit_count += 1
            elif _is_control_enabled(child):
                # Cybos Starter: Afx 컨테이너 내부 Edit는 IsWindowVisible=False이지만
                # rect 크기가 있으면 실제 입력 필드임 (owner-drawn UI)
                rect = _get_window_rect_safe(child)
                if rect and (rect[2] - rect[0]) > 0 and (rect[3] - rect[1]) > 0:
                    edit_count += 1
        except Exception:
            pass
    login_btns = _find_child_by_exact_text(parent_hwnd, LOGIN_BUTTON_TEXTS, class_name="Button")
    if not login_btns:
        login_btns = _find_child_by_text_contains(parent_hwnd, [u"로그인", u"모의"], class_name="Button")
    return edit_count >= 2 or bool(login_btns)


def _physical_click_hwnd(hwnd):
    """대상 컨트롤 중앙에 클릭을 보낸다. PostMessage 1차 → SetCursorPos 2차."""
    rect = _get_window_rect_safe(hwnd)
    if not rect:
        return False

    left, top, right, bottom = rect
    cx = int((left + right) / 2)
    cy = int((top + bottom) / 2)
    # 부모 창 찾아 WM_NCLBUTTONDOWN 전달 시도
    parent = win32gui.GetParent(hwnd) or hwnd
    ok = _click_at_screen(parent, cx, cy)
    if ok:
        print("[INFO] Click sent: hwnd=%d text='%s'" % (hwnd, win32gui.GetWindowText(hwnd)))
        time.sleep(0.2)
    return ok


def _find_top_left_text_control(parent_hwnd, candidate_texts):
    """좌상단에 있는 후보 텍스트 컨트롤 하나를 찾는다."""
    targets = {_normalize_title(text) for text in candidate_texts}
    candidates = []

    for child in _enum_children(parent_hwnd):
        try:
            if not win32gui.IsWindowVisible(child):
                continue
            text = win32gui.GetWindowText(child).strip()
            if _normalize_title(text) in targets:
                rect = _get_window_rect_safe(child) or (99999, 99999, 99999, 99999)
                candidates.append((child, text, rect))
        except Exception:
            pass

    if not candidates:
        return None, None

    candidates.sort(key=lambda item: (item[2][1], item[2][0]))
    child, text, _rect = candidates[0]
    return child, text


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
    """BM_CLICK 메시지로 버튼 클릭 -- 마우스/좌표 불필요"""
    try:
        win32gui.PostMessage(btn_hwnd, win32con.BM_CLICK, 0, 0)
        print("  [CTRL] BM_CLICK → hwnd=%d text='%s'" % (btn_hwnd, win32gui.GetWindowText(btn_hwnd)))
        return True
    except Exception as e:
        print("  [WARN] BM_CLICK 실패 hwnd=%d: %s" % (btn_hwnd, e))
        return False


def _post_nclbclick(hwnd, screen_x, screen_y, hover_ms=0, after_ms=100):
    """
    PostMessage(WM_NCLBUTTONDOWN)으로 좌표 클릭 -- SetCursorPos 대체.

    SetCursorPos + mouse_event는 UAC 상위 프로세스(coStarter.exe) 또는
    UIAccess 정책 차이로 ERROR_ACCESS_DENIED(5) 실패 가능.
    PostMessage는 메시지 큐 직접 삽입이므로 해당 제한을 우회한다.

    CREON Starter 창 전체가 HTCAPTION(owner-drawn 타이틀바) 구조이므로
    물리 마우스는 WM_NCLBUTTONDOWN으로 전달됨 → 동일 메시지 사용.
    lParam = 화면 좌표 (WM_NCLBUTTONDOWN 규약: screen coords in lParam).
    """
    try:
        lp = ((screen_y & 0xFFFF) << 16) | (screen_x & 0xFFFF)
        if hover_ms > 0:
            win32gui.PostMessage(hwnd, win32con.WM_NCMOUSEMOVE, win32con.HTCAPTION, lp)
            time.sleep(hover_ms / 1000.0)
        win32gui.PostMessage(hwnd, win32con.WM_NCLBUTTONDOWN, win32con.HTCAPTION, lp)
        time.sleep(after_ms / 1000.0)
        win32gui.PostMessage(hwnd, win32con.WM_NCLBUTTONUP, win32con.HTCAPTION, lp)
        return True
    except Exception as e:
        print("[WARN] _post_nclbclick 실패 hwnd=%d screen(%d,%d): %s" % (hwnd, screen_x, screen_y, e))
        return False


def _click_at_screen(hwnd, screen_x, screen_y, hover_ms=0, after_ms=100):
    """
    CREON 좌표 클릭 공통 진입점.
    1차: PostMessage(WM_NCLBUTTONDOWN) -- UAC/UIAccess 차이 우회
    2차: SetCursorPos + mouse_event -- 표준 물리 클릭 (SetCursorPos 허용 환경)
    """
    ok = _post_nclbclick(hwnd, screen_x, screen_y, hover_ms=hover_ms, after_ms=after_ms)
    if not ok:
        try:
            if hover_ms > 0:
                win32api.SetCursorPos((screen_x, screen_y))
                time.sleep(hover_ms / 1000.0)
            win32api.SetCursorPos((screen_x, screen_y))
            time.sleep(0.10)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(after_ms / 1000.0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        except Exception as e:
            print("[WARN] _click_at_screen SetCursorPos 실패 screen(%d,%d): %s" % (screen_x, screen_y, e))
            return False
    return True


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


# -- Edit 컨트롤 탐지 -----------------------------------------------------------

def _collect_edits(parent_hwnd):
    """로그인 창의 Edit 컨트롤 목록을 y 좌표 오름차순으로 반환"""
    edits = [c for c in _enum_children(parent_hwnd)
             if win32gui.GetClassName(c) == "Edit" and win32gui.IsWindowVisible(c)]

    if not edits:
        # Cybos 로그인 창은 커스텀 윈도우일 수 있음 -- AfxWnd/PopupEdit 등 다양한 클래스 탐색
        for c in _enum_children(parent_hwnd):
            if not win32gui.IsWindowVisible(c):
                continue
            try:
                cn = win32gui.GetClassName(c)
                if cn and any(kw in cn.upper() for kw in ("EDIT", "RICHEDIT", "TEXTBOX")):
                    edits.append(c)
            except Exception:
                pass

    # y 좌표 기준 오름차순 (위→아래: ID → PW)
    edits.sort(key=lambda h: (_get_window_rect_safe(h) or (0, 9999, 0, 0))[1])
    return edits


def _find_id_password_edits(parent_hwnd):
    """(id_edit, pw_edit) 쌍 반환. y 좌표 기준 첫 번째=ID, 마지막=PW"""
    edits = _collect_edits(parent_hwnd)
    if not edits:
        return None, None
    id_edit = edits[0]
    pw_edit = edits[-1] if len(edits) >= 2 else None
    return id_edit, pw_edit


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
    """Windows Credential Manager에서 ID/PW 읽기.

    CredEnumerate(flags=0)는 CRED_TYPE_GENERIC을 빠뜨리는 경우가 있으므로
    CredRead로 타입을 명시해서 순서대로 시도한다.
      1. CRED_TYPE_GENERIC (1)  -- cmdkey /add 기본값
      2. CRED_TYPE_DOMAIN_PASSWORD (2)  -- 도메인 자격증명 (blob 비어있을 수 있음)
    """
    if PASSWORD_OVERRIDE:
        return "", PASSWORD_OVERRIDE

    CRED_TYPE_GENERIC          = 1
    CRED_TYPE_DOMAIN_PASSWORD  = 2

    for cred_type in (CRED_TYPE_GENERIC, CRED_TYPE_DOMAIN_PASSWORD):
        try:
            cred = win32cred.CredRead(CRED_TARGET, cred_type, 0)
            username = cred.get("UserName", "")
            blob = cred.get("CredentialBlob", b"")
            if not blob:
                print("[DEBUG] blob 비어있음 건너뜀: Target=%s Type=%d User=%s"
                      % (CRED_TARGET, cred_type, username))
                continue
            password = blob.decode("utf-16-le")
            print("[DEBUG] 자격증명 로드 성공: Target=%s Type=%d User=%s"
                  % (CRED_TARGET, cred_type, username))
            return username, password
        except Exception as e:
            print("[DEBUG] CredRead(Type=%d) 실패: %s" % (cred_type, e))

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


def _click_creon_id_tab(hwnd):
    """
    CREON 로그인 창의 '아이디' 탭 클릭.
    CREON Plus 선택 직후 Edit 컨트롤이 비가시 상태 -- '아이디' 탭을 클릭해야 visible=True.

    실증 좌표: 패널 좌상단 + (295, 215) [3번째 탭, '아이디']
    """
    afx_ctrls = []
    def _cb(ch, _):
        try:
            if "Afx" in win32gui.GetClassName(ch) and win32gui.IsWindowVisible(ch):
                r = win32gui.GetWindowRect(ch)
                if (r[2]-r[0]) > 200 and (r[3]-r[1]) > 400:
                    afx_ctrls.append((ch, r))
        except Exception:
            pass
    win32gui.EnumChildWindows(hwnd, _cb, None)
    if not afx_ctrls:
        return
    afx_ctrls.sort(key=lambda x: x[1][0])
    px, py = afx_ctrls[0][1][0], afx_ctrls[0][1][1]

    tab_x = px + 295
    tab_y = py + 215
    print("[INFO] CREON '아이디' 탭 클릭: screen(%d,%d)" % (tab_x, tab_y))
    _click_at_screen(hwnd, tab_x, tab_y)
    time.sleep(0.40)  # 탭 전환 후 Edit 가시화 대기


def _click_creon_login_button(hwnd):
    """
    CREON '모의투자로그인' 버튼 좌표 기반 클릭.
    버튼이 owner-drawn (HTCAPTION 영역)이므로 BM_CLICK 탐지 불가.

    실증 좌표:
    - PW Edit 하단(screen y ≈ 708) + 72px → 버튼 center y ≈ 780
    - 패널 중앙 x: 창 left + 182
    """
    edits = []
    def _eb(ch, _):
        try:
            if win32gui.GetClassName(ch) == "Edit" and win32gui.IsWindowVisible(ch):
                r = win32gui.GetWindowRect(ch)
                if r[2] - r[0] > 50:
                    edits.append(r)
        except Exception:
            pass
    win32gui.EnumChildWindows(hwnd, _eb, None)
    edits.sort(key=lambda r: r[1])

    win_rect = _get_window_rect_safe(hwnd)
    if not win_rect:
        return
    wx, wy = win_rect[0], win_rect[1]

    if edits:
        pw_bottom = edits[-1][3]
        btn_x = wx + 182
        btn_y = pw_bottom + 72
    else:
        btn_x = wx + 182
        btn_y = wy + 391

    print("[INFO] CREON 모의투자로그인 버튼 클릭: screen(%d,%d)" % (btn_x, btn_y))
    _force_foreground(hwnd)
    time.sleep(0.20)
    _click_at_screen(hwnd, btn_x, btn_y)
    time.sleep(0.30)


def _click_creon_mock_access(hwnd):
    """
    CREON '모의투자 선택' 팝업의 '모의투자 접속' 버튼 좌표 클릭.
    팝업이 in-window GDI 오버레이라 EnumWindows/FindWindow 불가.

    실증 좌표: 창 origin + (365, 317)
    """
    try:
        win_rect = win32gui.GetWindowRect(hwnd)
        if not win32gui.IsWindowVisible(hwnd):
            return
    except Exception:
        return
    wx, wy = win_rect[0], win_rect[1]
    btn_x = wx + 365
    btn_y = wy + 317
    print("[INFO] CREON 모의투자 접속 클릭: screen(%d,%d)" % (btn_x, btn_y))
    _force_foreground(hwnd)
    time.sleep(0.20)
    _click_at_screen(hwnd, btn_x, btn_y)
    time.sleep(0.30)


def _select_creon_plus_by_coordinate(hwnd):
    """
    CREON 로그인 창 좌상단 드롭다운에서 'CREON Plus' 를 좌표 기반으로 선택.

    실증 분석 결과:
    - 좌측 Afx 패널: HTRANSPARENT → 모든 마우스가 부모(login_hwnd)로 전달
    - login_hwnd 전체: HTCAPTION (커스텀 타이틀바)
    - 드롭다운 열기:    패널 (+90, +15) 클릭
    - CREON Plus 항목: 패널 (+65, +85) [hover 400 ms 후 클릭]
    - ESC 전송 금지: 창이 닫힘
    """
    afx_ctrls = []
    def _cb(ch, _):
        try:
            if "Afx" in win32gui.GetClassName(ch) and win32gui.IsWindowVisible(ch):
                r = win32gui.GetWindowRect(ch)
                if (r[2]-r[0]) > 200 and (r[3]-r[1]) > 400:
                    afx_ctrls.append((ch, r))
        except Exception:
            pass
    win32gui.EnumChildWindows(hwnd, _cb, None)
    if not afx_ctrls:
        print("[WARN] CREON 패널 탐색 실패 -- CREON Plus 선택 생략, 로그인 계속")
        return True
    afx_ctrls.sort(key=lambda x: x[1][0])
    px, py = afx_ctrls[0][1][0], afx_ctrls[0][1][1]

    win_before = _get_window_rect_safe(hwnd)

    # 헤더 클릭 → 드롭다운 열기 (단 한 번)
    hdr_x, hdr_y = px + 90, py + 15
    print("[INFO] CREON Plus 드롭다운 열기: screen(%d,%d)" % (hdr_x, hdr_y))
    _click_at_screen(hwnd, hdr_x, hdr_y)
    time.sleep(1.0)

    # 창 이동 보정
    win_after = _get_window_rect_safe(hwnd)
    dx = (win_after[0] - win_before[0]) if (win_before and win_after) else 0
    dy = (win_after[1] - win_before[1]) if (win_before and win_after) else 0

    # CREON Plus 항목 클릭: hover 후 클릭
    cp_x = px + 65 + dx
    cp_y = py + 85 + dy
    print("[INFO] CREON Plus 항목 클릭: screen(%d,%d) [hover 400ms → click]" % (cp_x, cp_y))
    _click_at_screen(hwnd, cp_x, cp_y, hover_ms=400)
    time.sleep(0.60)

    print("[INFO] CREON Plus 선택 완료")
    return True


def _ensure_cybos_plus_menu_selected(hwnd):
    """로그인 창 좌상단 상품 메뉴가 CREON Plus / CYBOS Plus인지 확인하고 필요 시 선택한다."""
    broker_plus    = u"CREON Plus" if BROKER_TYPE == "creon" else u"CYBOS Plus"
    broker_kw      = u"CREON"      if BROKER_TYPE == "creon" else u"CYBOS"
    plus_keywords  = ([u"CREON Plus", u"CREON PLUS"] if BROKER_TYPE == "creon"
                      else [u"CYBOS Plus", u"CYBOS PLUS"])

    # CREON: 전체 UI가 owner-drawn (HTRANSPARENT Afx + HTCAPTION 부모)
    # 텍스트 컨트롤 탐색 불가 → 좌표 기반 드롭다운 선택으로 직행
    if BROKER_TYPE == "creon":
        return _select_creon_plus_by_coordinate(hwnd)

    print("[INFO] Verifying left-top product menu is set to %s..." % broker_plus)
    _activate_and_wait_for_window(hwnd, "%s menu" % broker_plus)

    # ── ① exact match ─────────────────────────────────────────────────────────
    exact_hwnd, exact_text = _find_top_left_text_control(hwnd, CYBOS_PLUS_MENU_EXACT_TEXTS)
    if exact_hwnd:
        print("[INFO] %s menu already selected: '%s' hwnd=%d" % (broker_plus, exact_text, exact_hwnd))
        return True

    # ── ② partial match ─ 드롭다운 화살표(∨ 등)가 텍스트에 포함된 경우 대응 ──
    partial = _find_child_by_text_contains(hwnd, plus_keywords)
    for p_hwnd, p_text in partial:
        if win32gui.IsWindowVisible(p_hwnd):
            print("[INFO] %s menu already selected (partial): '%s' hwnd=%d" % (broker_plus, p_text, p_hwnd))
            return True

    # ── ③ opener 탐색 (현재 선택 항목 표시 드롭다운 버튼) ─────────────────────
    opener_hwnd, opener_text = _find_top_left_text_control(hwnd, CYBOS_PLUS_MENU_CANDIDATE_TEXTS)
    if not opener_hwnd:
        # 화살표 포함 텍스트 대응: broker 키워드 부분일치
        for p_hwnd, p_text in _find_child_by_text_contains(hwnd, [broker_kw]):
            if win32gui.IsWindowVisible(p_hwnd):
                opener_hwnd, opener_text = p_hwnd, p_text
                break

    if not opener_hwnd:
        if _looks_like_login_form(hwnd):
            print("[WARN] Product menu control not found. Login form detected -- skipping menu verify.")
            _dump_children(hwnd, "%s menu verify skipped" % broker_plus)
            return True
        print("[WARN] Product menu control was not found and login form not detected.")
        _dump_children(hwnd, "%s menu verify failed" % broker_plus)
        return False

    print("[INFO] Product menu opener found: '%s' hwnd=%d" % (opener_text, opener_hwnd))
    if not _physical_click_hwnd(opener_hwnd):
        print("[WARN] Failed to open the product menu.")
        return False
    time.sleep(0.4)

    # ── ④ 팝업 탐색 -- CREON / CYBOS 모두 탐색 ───────────────────────────────
    popup_matches = _find_window_by_keywords([u"CYBOS", u"CREON"], require_visible=True)
    for popup_hwnd, popup_title in popup_matches:
        menu_hwnd, menu_text = _find_top_left_text_control(popup_hwnd, CYBOS_PLUS_MENU_EXACT_TEXTS)
        if menu_hwnd:
            print("[INFO] %s menu item found in popup: '%s' hwnd=%d" % (broker_plus, menu_text, menu_hwnd))
            _physical_click_hwnd(menu_hwnd)
            time.sleep(0.4)
            break
        # partial match in popup (팝업 내 아이템에도 화살표 포함 가능성)
        for p_hwnd, p_text in _find_child_by_text_contains(popup_hwnd, plus_keywords):
            print("[INFO] %s menu item found in popup (partial): '%s' hwnd=%d" % (broker_plus, p_text, p_hwnd))
            _physical_click_hwnd(p_hwnd)
            time.sleep(0.4)
            break

    # ── ⑤ 선택 후 재확인 ──────────────────────────────────────────────────────
    exact_hwnd, exact_text = _find_top_left_text_control(hwnd, CYBOS_PLUS_MENU_EXACT_TEXTS)
    if exact_hwnd:
        print("[INFO] %s menu confirmed: '%s' hwnd=%d" % (broker_plus, exact_text, exact_hwnd))
        return True

    for p_hwnd, p_text in _find_child_by_text_contains(hwnd, plus_keywords):
        if win32gui.IsWindowVisible(p_hwnd):
            print("[INFO] %s menu confirmed (partial): '%s' hwnd=%d" % (broker_plus, p_text, p_hwnd))
            return True

    if _looks_like_login_form(hwnd):
        print("[WARN] Could not confirm %s menu selection from control text." % broker_plus)
        print("[WARN] Continuing because the owner-drawn login form is visible.")
        _dump_children(hwnd, "%s menu verify inconclusive" % broker_plus)
        return True

    print("[WARN] Could not confirm %s menu selection." % broker_plus)
    _dump_children(hwnd, "%s menu verify failed" % broker_plus)
    return False


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

    try:
        win32api.SetCursorPos((cx, cy))
        time.sleep(0.15)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.08)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    except Exception as e:
        print("[WARN] 블라인드 클릭 SetCursorPos 실패(%s) -- ctypes 직접 호출 시도" % e)
        try:
            import ctypes
            ctypes.windll.user32.SetCursorPos(cx, cy)
            time.sleep(0.15)
            ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
            time.sleep(0.08)
            ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
        except Exception as e2:
            print("[WARN] ctypes 블라인드 클릭도 실패: %s" % e2)
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

    _sec_hint = " + 보안 다이얼로그" if HAS_SECURITY_DIALOG else ""
    print("[INFO] %s 초기화 대기 중 (로그인 창 탐지%s)..." % (os.path.basename(CYBOS_EXE), _sec_hint))
    start = time.time()
    msg = ctypes.wintypes.MSG()

    try:
        iterations = timeout * 5
        for tick in range(iterations):
            elapsed = time.time() - start

            while ctypes.windll.user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

            if HAS_SECURITY_DIALOG and not security_clicked:
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

def _perform_login(hwnd, user_id, password):
    """
    로그인 창에서 컨트롤 기반으로:
      1. 아이디 Edit (y 좌표 첫 번째) → WM_SETTEXT
      2. 비밀번호 Edit (y 좌표 마지막) → WM_SETTEXT
      3. Enter 전송 → 로그인

    절대 좌표 전혀 사용하지 않음.
    """
    _activate_and_wait_for_window(hwnd, "CYBOS Starter")

    title = win32gui.GetWindowText(hwnd)
    _dump_children(hwnd, "로그인 창 '%s'" % title)

    if not _ensure_cybos_plus_menu_selected(hwnd):
        print("[ERROR] %s menu is not selected in the login window." % ("CREON Plus" if BROKER_TYPE == "creon" else "CYBOS Plus"))
        return False

    # CREON: "아이디" 탭 클릭 -- CREON Plus 선택 후 Edit 컨트롤이 비가시 상태일 수 있음
    # "아이디" 탭을 클릭해야 ID/PW Edit가 visible=True가 됨
    if BROKER_TYPE == "creon":
        _click_creon_id_tab(hwnd)

    id_edit, pw_edit = _find_id_password_edits(hwnd)

    EM_SETSEL = 0x00B1  # 전체 선택용 (0, -1)

    def _clear_and_input(edit_hwnd, text, label):
        """물리 클릭 → EM_SETSEL(전체선택) → WM_CLEAR → WM_SETTEXT (CREON/CYBOS 공통)"""
        rect = _get_window_rect_safe(edit_hwnd)
        if rect:
            cx = (rect[0] + rect[2]) // 2
            cy = (rect[1] + rect[3]) // 2
            win32api.SetCursorPos((cx, cy))
            time.sleep(0.08)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.10)
        else:
            _focus_control(edit_hwnd)
            time.sleep(0.10)
        win32gui.SendMessage(edit_hwnd, EM_SETSEL, 0, -1)
        time.sleep(0.05)
        win32gui.SendMessage(edit_hwnd, win32con.WM_CLEAR, 0, 0)
        time.sleep(0.05)
        result = _set_edit_text(edit_hwnd, text)
        if not result:
            send_keys("^a{BACKSPACE}")
            send_keys(text)
            print("[INFO] send_keys로 %s 입력 완료" % label)
        print("[INFO] %s 입력 완료 (clicked → cleared → set)" % label)
        time.sleep(0.10)

    # ── STEP 1: 아이디 입력 ──
    if id_edit and user_id:
        print("[INFO] 아이디 Edit 발견: hwnd=%d → '%s'" % (id_edit, user_id))
        _clear_and_input(id_edit, user_id, "아이디")
    else:
        print("[WARN] 아이디 Edit 미발견 또는 user_id 없음 -- 건너뜀")

    time.sleep(0.15)

    # ── STEP 2: 비밀번호 입력 ──
    if pw_edit:
        print("[INFO] 비밀번호 Edit 발견: hwnd=%d" % pw_edit)
        _clear_and_input(pw_edit, password, "비밀번호")
    elif id_edit:
        # Edit가 1개뿐(커스텀 창) -- 포커스 이동 후 비밀번호 입력
        print("[WARN] 비밀번호 Edit 미발견 -- Tab으로 이동 후 입력 시도")
        send_keys("{TAB}")
        time.sleep(0.15)
        send_keys("^a{BACKSPACE}")
        send_keys(password)
    else:
        print("[WARN] Edit 컨트롤 전혀 없음 -- Tab 탐색 시도")
        send_keys("{TAB}{TAB}")
        time.sleep(0.15)
        send_keys("^a{BACKSPACE}")
        send_keys(password)

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
        print("[INFO] 로그인 버튼 컨트롤 없음 -- Enter로 충분할 수 있음")

    # CREON: 버튼이 owner-drawn이라 BM_CLICK 탐지 불가 → 좌표 클릭 추가
    if BROKER_TYPE == "creon":
        time.sleep(0.3)
        _click_creon_login_button(hwnd)

    return True


# -- 비밀번호 확인 팝업 ---------------------------------------------------------

def _find_password_confirm_dialog():
    """실제 로그인 실패 팝업만 탐지한다."""
    matches = []

    def _enum(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd).strip()
            if title != u"CYBOS":
                return

            child_texts = []
            for child in _enum_children(hwnd):
                try:
                    text = win32gui.GetWindowText(child).strip()
                    if text:
                        child_texts.append(text)
                except Exception:
                    pass

            joined = u" ".join(child_texts)
            if (u"아이디" in joined or u"비밀번호" in joined) and u"확인" in joined:
                matches.append((hwnd, title, child_texts))
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_enum, None)
    except Exception:
        pass

    return matches[0] if matches else None


def _handle_password_confirm_dialog(timeout=10):
    """실제 로그인 실패 팝업만 닫고 실패로 간주한다."""
    print("[INFO] 비밀번호 확인 팝업 대기 중...")

    for tick in range(timeout):
        found = _find_password_confirm_dialog()
        if found:
            hwnd, title, child_texts = found
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

def _find_mock_dialog_candidates():
    """
    '모의투자 선택' 창을 두 가지 방법으로 탐색:
      1. 키워드 기반 EnumWindows
      2. FindWindow 직접 탐색 (키워드 탐색 실패 시 보험)
    중복 hwnd를 제거하여 반환한다.
    """
    candidates = _find_window_by_keywords(MOCK_DIALOG_KEYWORDS, require_visible=True)
    seen = {hwnd for hwnd, _ in candidates}

    # FindWindow 직접 탐색 -- 키워드 정규화 오류나 인코딩 차이 대응
    for title_exact in (u"모의투자 선택", u"모의투자선택"):
        try:
            direct_hwnd = win32gui.FindWindow(None, title_exact)
            if direct_hwnd and direct_hwnd not in seen and win32gui.IsWindowVisible(direct_hwnd):
                candidates.append((direct_hwnd, title_exact))
                seen.add(direct_hwnd)
        except Exception:
            pass
    return candidates


def _click_mock_access_button(hwnd):
    """
    '모의투자 접속' 버튼을 다음 순서로 모두 시도한다:
      1. 버튼 탐색 (정확한 텍스트 → 부분 텍스트 → 가장 오른쪽 Button)
      2. BM_CLICK  (표준 버튼 동작)
      3. 물리 클릭 (owner-drawn/커스텀 버튼 대응 -- 키움과 동일 패턴)
      4. Enter 전송 (기본 버튼 fallback)
    클릭 후 창이 닫혔으면 True 반환, 아직 열려 있으면 False 반환.
    """
    _dump_children(hwnd, "모의투자 선택")

    # ── 버튼 탐색 ────────────────────────────────────────────────────────
    found_btns = _find_child_by_exact_text(hwnd, MOCK_ACCESS_BUTTON_TEXTS, class_name="Button")
    if not found_btns:
        # "접속" 포함 -- 단, "참가신청"은 걸러 내기 위해 "접속"만 검색
        found_btns = _find_child_by_text_contains(hwnd, [u"접속"])
    if not found_btns:
        # 최후 수단: 모든 Button 중 가장 오른쪽 버튼 (우상단 = "모의투자 접속")
        # "모의투자 참가신청"은 하단 중앙 → right 좌표가 더 작음
        all_btns = _find_child_by_class(hwnd, "Button")
        if all_btns:
            btn = max(all_btns,
                      key=lambda b: (_get_window_rect_safe(b) or (0, 0, 0, 0))[2])
            found_btns = [(btn, win32gui.GetWindowText(btn))]

    if found_btns:
        btn_hwnd, btn_text = found_btns[0]
        print("[INFO] '모의투자 접속' 버튼 발견: '%s' hwnd=%d" % (btn_text, btn_hwnd))

        # Method 1: BM_CLICK (표준 버튼)
        _post_button_click(btn_hwnd)
        time.sleep(0.25)

        # Method 2: 물리 클릭 (owner-drawn 버튼 대응 -- BM_CLICK 불응 시 필수)
        _force_foreground(hwnd)
        _physical_click_hwnd(btn_hwnd)
        time.sleep(0.25)

        # Method 3: Enter (기본 버튼 fallback)
        _force_foreground(hwnd)
        send_keys("{ENTER}")
        print("[INFO] BM_CLICK + 물리클릭 + ENTER 전송 완료")
    else:
        # 버튼 탐색 자체 실패 -- Enter만
        print("[WARN] 접속 버튼 컨트롤 미발견 → Enter 폴백")
        _dump_children(hwnd, "모의투자 창 (버튼 못찾음)")
        _force_foreground(hwnd)
        send_keys("{ENTER}")

    # 클릭 반영 대기 후 창이 닫혔는지 확인
    time.sleep(0.8)
    try:
        still_visible = win32gui.IsWindowVisible(hwnd)
    except Exception:
        still_visible = False  # hwnd 무효 → 닫힌 것으로 간주

    if not still_visible:
        print("[INFO] 모의투자 선택 창이 닫혔습니다 -- 처리 완료.")
        return True

    print("[WARN] 모의투자 선택 창이 아직 열려 있음 -- 재시도 예정")
    return False


def _handle_mock_select_dialog(timeout=45, min_wait=0):
    """
    '모의투자 선택' 창을 찾아 '모의투자 접속' 버튼을 처리한다.

    개선 사항:
      - min_wait 중에 팝업이 먼저 나타나면 즉시 처리 (20초 불필요 대기 제거)
      - blind Enter 전송 시 팝업에 포커스를 맞춘 후 전송 (엉뚱한 창 방지)
      - 버튼 클릭 순서: BM_CLICK → 물리클릭 → Enter (owner-drawn 완전 대응)
      - 클릭 후 창이 닫혔는지 검증 -- 안 닫히면 루프 계속
      - FindWindow 직접 탐색으로 키워드 탐색 실패 보완
    """
    print("[INFO] 모의투자 선택 창 대기 중...")

    if min_wait > 0:
        print("[INFO] 모의투자 선택 팝업 최소 대기... %d초" % min_wait)
        for waited in range(min_wait):
            if _is_connected():
                print("[INFO] 이미 연결됨 -- 모의투자 선택 창 처리 생략")
                return True
            # 팝업이 min_wait 중에 먼저 나타나면 즉시 처리
            early = _find_mock_dialog_candidates()
            if early:
                print("[INFO] 모의투자 팝업 조기 발견 (대기 %d초) -- 즉시 처리" % (waited + 1))
                for hwnd, title in early:
                    if win32gui.IsWindowVisible(hwnd):
                        _activate_and_wait_for_window(hwnd, title)
                        if _click_mock_access_button(hwnd):
                            return True
                break  # 팝업 발견했으나 클릭 실패 → 아래 메인 루프로 이어서 처리
            time.sleep(1)
            if (waited + 1) % 5 == 0:
                print("[INFO] 모의투자 팝업 최소 대기... %d/%d초" % (waited + 1, min_wait))
        else:
            # min_wait를 모두 소진한 경우 -- 팝업에 포커스 맞춘 뒤 Enter
            blind_cands = _find_mock_dialog_candidates()
            if blind_cands:
                hwnd, _ = blind_cands[0]
                _force_foreground(hwnd)
                time.sleep(0.2)
            send_keys("{ENTER}")
            print("[INFO] 모의투자 팝업 최소 대기 후 Enter 입력 (팝업 포커스 시도 후)")
            time.sleep(3)

    # ── 메인 탐지·클릭 루프 ─────────────────────────────────────────────
    for tick in range(timeout):
        if _is_connected():
            print("[INFO] 이미 연결됨 -- 모의투자 선택 창 처리 생략")
            return True

        candidates = _find_mock_dialog_candidates()
        for hwnd, title in candidates:
            if not win32gui.IsWindowVisible(hwnd):
                continue
            print("[INFO] 모의투자 선택 창 발견: '%s' hwnd=%d" % (title, hwnd))
            _activate_and_wait_for_window(hwnd, title)
            if _click_mock_access_button(hwnd):
                return True
            # 클릭했지만 창이 안 닫힌 경우 -- 다음 tick에서 재시도
            break

        if tick % 5 == 4:
            titles = [t for _, t in candidates[:6]]
            print("[INFO] 모의투자 선택 창 대기... %d/%d초 visible=%s" % (tick + 1, timeout, titles))
        time.sleep(1)

    print("[WARN] 모의투자 선택 창이 나타나지 않음 -- 건너뜀")
    return False


# -- 통합 연결 대기 루프 ---------------------------------------------------------

def _wait_for_connection_and_mock(total_timeout=120):
    """
    모의투자 팝업 처리 + 연결 대기를 하나의 루프로 통합 (race condition 근절).

    매 1초:
      ① IsConnect=1 → True 즉시 반환
      ② 에러·공지사항 다이얼로그 닫기
      ③ 모의투자 팝업 탐지 → BM_CLICK + 물리클릭 + Enter 순차 시도
      ④ 팝업 미탐지 시 5초마다 blind Enter
         (팝업이 타이틀 인식 실패·숨김 상태여도 포커스된 창에 전달)
      ⑤ 로그인 실패 팝업 → False 반환 (자격증명 오류)
    """
    BLIND_INTERVAL = 5
    print("[INFO] 연결+모의투자 통합 대기 (최대 %ds)..." % total_timeout)

    start = time.time()
    deadline = start + total_timeout
    last_blind = start - BLIND_INTERVAL  # 즉시 첫 blind Enter 허용
    last_10s_mark = -1

    while time.time() < deadline:
        elapsed = int(time.time() - start)

        # ① 연결 확인
        if _is_connected():
            return True

        # ② 에러·공지사항 다이얼로그
        _dismiss_error_dialogs()

        # ③ 모의투자 팝업 탐지 + 클릭
        candidates = _find_mock_dialog_candidates()
        popup_handled = False
        for hwnd, title in candidates:
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    continue
            except Exception:
                continue
            print("[INFO] 모의투자 팝업 발견: '%s' hwnd=%d (%ds)" % (title, hwnd, elapsed))
            _activate_and_wait_for_window(hwnd, title)
            _click_mock_access_button(hwnd)
            last_blind = time.time()
            popup_handled = True
            break

        # ④ CREON: in-window 모의투자 선택 팝업 좌표 클릭 (EnumWindows 탐지 불가)
        if BROKER_TYPE == "creon" and not popup_handled:
            if _creon_starter_hwnd and (time.time() - last_blind) >= BLIND_INTERVAL and elapsed >= 3:
                try:
                    if win32gui.IsWindowVisible(_creon_starter_hwnd):
                        _click_creon_mock_access(_creon_starter_hwnd)
                        last_blind = time.time()
                except Exception:
                    pass

        # ④ Blind Enter -- 팝업이 감지되지 않아도 주기적으로 전송 (CREON은 생략)
        if BROKER_TYPE != "creon" and not popup_handled and (time.time() - last_blind) >= BLIND_INTERVAL:
            print("[INFO] Blind Enter 전송 (%ds 경과)" % elapsed)
            send_keys("{ENTER}")
            last_blind = time.time()

        # ⑤ 로그인 실패 팝업 (내부 sleep 없이 직접 체크)
        fail = _find_password_confirm_dialog()
        if fail:
            hwnd, title, child_texts = fail
            ok_btns = _find_child_by_exact_text(hwnd, PASSWORD_DIALOG_CONFIRM_TEXTS, class_name="Button")
            for btn_hwnd, _btn_text in ok_btns:
                if _is_control_enabled(btn_hwnd):
                    print("[ERROR] 로그인 실패 팝업 감지: %s" % child_texts)
                    _post_button_click(btn_hwnd)
                    return False
            return False

        mark = elapsed // 10
        if mark > last_10s_mark:
            last_10s_mark = mark
            print("  ... %ds 경과" % elapsed)

        time.sleep(1)

    print("[ERROR] 연결 타임아웃 (%ds)" % total_timeout)
    return False


def _wait_for_connection_realmode(total_timeout=120):
    """실투자 모드: 에러 다이얼로그 처리 + 연결 대기"""
    print("[INFO] 연결 대기 중 (최대 %ds)..." % total_timeout)
    start = time.time()
    last_10s_mark = -1

    for _ in range(total_timeout):
        elapsed = int(time.time() - start)
        if _is_connected():
            return True
        _dismiss_error_dialogs()
        fail = _find_password_confirm_dialog()
        if fail:
            return False
        mark = elapsed // 10
        if mark > last_10s_mark:
            last_10s_mark = mark
            print("  ... %ds 경과" % elapsed)
        time.sleep(1)

    print("[ERROR] 연결 타임아웃 (%ds)" % total_timeout)
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

    for attempt in range(MAX_LOGIN_ATTEMPTS):
        if attempt > 0:
            print("\n[INFO] ===  재시도 %d/%d  ===" % (attempt + 1, MAX_LOGIN_ATTEMPTS))

        # 기존 Cybos 프로세스 정리
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

        # STEP 1+2: 보안 다이얼로그 자동 클릭 + 로그인 창 대기
        hwnd = _wait_for_login_clicking_security(timeout=120)
        if hwnd is None:
            print("[WARN] 로그인 창 미발견 (120초 초과) -- 재시도...")
            continue

        # CREON: 로그인 창 hwnd 저장 (모의투자 팝업 좌표 클릭에 사용)
        if BROKER_TYPE == "creon":
            global _creon_starter_hwnd
            _creon_starter_hwnd = hwnd

        for _ in range(5):
            if _dismiss_error_dialogs() == 0:
                break
            time.sleep(0.5)
        time.sleep(1.5)

        # STEP 3: 자격증명 입력 + 로그인
        try:
            if not _perform_login(hwnd, user_id, password):
                print("[WARN] 로그인 자동화 실패 -- 재시도...")
                continue
            if _handle_password_confirm_dialog(timeout=5):
                # 아이디/비밀번호 오류 -- 재시도해도 동일하므로 즉시 종료
                print("[ERROR] CYBOS 로그인 실패 팝업 -- 아이디/비밀번호를 확인하세요.")
                sys.exit(1)
        except Exception as e:
            print("[WARN] UI 자동화 예외: %s -- 재시도..." % e)
            continue

        # STEP 4+5 통합: 모의투자 팝업 처리 + 연결 완료 대기 (단일 루프)
        wait_fn = _wait_for_connection_and_mock if MOCK_MODE else _wait_for_connection_realmode
        if wait_fn(total_timeout=CONNECT_TIMEOUT):
            cp = win32com.client.Dispatch("CpUtil.CpCybos")
            print("[OK] CybosPlus 연결 성공 (ServerType=%s)" % cp.ServerType)
            # 연결 직후 공지사항 등 잔여 다이얼로그 마무리 (연결 확인 즉시 루프 탈출 시 놓칠 수 있음)
            time.sleep(2)
            for _ in range(6):
                if _dismiss_error_dialogs() == 0:
                    break
                time.sleep(0.8)
            return True

        print("[WARN] 시도 %d/%d 연결 실패" % (attempt + 1, MAX_LOGIN_ATTEMPTS))

    print("[ERROR] Auto-login failed.")
    return False


if __name__ == "__main__":
    success = autologin()
    sys.exit(0 if success else 1)
