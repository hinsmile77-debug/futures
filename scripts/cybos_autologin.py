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


class _TeeStream(object):
    """stdout을 콘솔과 파일에 동시 기록 (진단 로그)"""
    def __init__(self, original, log_path):
        self._orig = original
        try:
            log_dir = os.path.dirname(log_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            self._f = io.open(log_path, "a", encoding="utf-8", errors="replace")
        except Exception:
            self._f = None

    def write(self, data):
        try:
            self._orig.write(data)
            self._orig.flush()
        except Exception:
            pass
        if self._f:
            try:
                self._f.write(data)
                self._f.flush()
            except Exception:
                pass

    def flush(self):
        try:
            self._orig.flush()
        except Exception:
            pass
        if self._f:
            try:
                self._f.flush()
            except Exception:
                pass

    def __getattr__(self, name):
        return getattr(self._orig, name)


_DIAG_LOG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "logs", "creon_autologin_diag.log"
)
try:
    import datetime as _dt
    _log_dir = os.path.dirname(_DIAG_LOG)
    if not os.path.exists(_log_dir):
        os.makedirs(_log_dir)
    with io.open(_DIAG_LOG, "a", encoding="utf-8") as _lf:
        _lf.write("\n=== autologin start: %s ===\n" % _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
except Exception:
    pass
sys.stdout = _TeeStream(sys.stdout, _DIAG_LOG)
sys.stderr = _TeeStream(sys.stderr, _DIAG_LOG)

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
    CYBOS_PROC_NAMES = ["comain.exe", "costarter.exe", "cpstart.exe"]
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
    """로그인 창의 Edit 컨트롤 목록을 y 좌표 오름차순으로 반환.

    1차: 가시(IsWindowVisible=True) + 클래스명 "Edit" 정확 매치
    2차: 가시 + 클래스명 EDIT/RICHEDIT/TEXTBOX 포함 (AfxWnd 계열 대응)
    3차: 비가시(IsWindowVisible=False) + "Edit" 클래스 + width>50 + height>10
         → CREON Plus 모드에서 "아이디" 탭 미선택 시 사용 (WM_SETTEXT 직접 주입)
    """
    edits = [c for c in _enum_children(parent_hwnd)
             if win32gui.GetClassName(c) == "Edit" and win32gui.IsWindowVisible(c)]

    if not edits:
        for c in _enum_children(parent_hwnd):
            if not win32gui.IsWindowVisible(c):
                continue
            try:
                cn = win32gui.GetClassName(c)
                if cn and any(kw in cn.upper() for kw in ("EDIT", "RICHEDIT", "TEXTBOX")):
                    edits.append(c)
            except Exception:
                pass

    if not edits:
        # CREON Plus 모드 폴백: 비가시 Edit에 직접 WM_SETTEXT 주입
        invisible_edits = []
        for c in _enum_children(parent_hwnd):
            if win32gui.IsWindowVisible(c):
                continue
            try:
                cn = win32gui.GetClassName(c)
                if cn == "Edit":
                    r = _get_window_rect_safe(c) or (0, 0, 0, 0)
                    if (r[2] - r[0]) > 50 and (r[3] - r[1]) > 10:
                        invisible_edits.append(c)
                        print("[DEBUG] 비가시 Edit 폴백: hwnd=%d rect=%s" % (c, r))
            except Exception:
                pass
        edits = invisible_edits

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

    2D 그리드 스캔:
    - x_offsets × y_offsets 조합으로 패널 전체 탐색
    - 각 클릭 후 Edit 가시화 확인 → 성공 즉시 반환
    - SetCursorPos + mouse_event 사용 필수 (PostMessage만으로는 탭 전환 안 됨)
    """
    # Afx 패널 전체 위치 로깅 (진단)
    afx_all = []
    def _cb_all(ch, _):
        try:
            if "Afx" in win32gui.GetClassName(ch) and win32gui.IsWindowVisible(ch):
                r = win32gui.GetWindowRect(ch)
                afx_all.append((ch, r))
        except Exception:
            pass
    try:
        win32gui.EnumChildWindows(hwnd, _cb_all, None)
    except Exception:
        pass
    afx_all.sort(key=lambda x: x[1][0])
    for _ah, _ar in afx_all:
        print("[DEBUG] Afx패널 hwnd=%d rect=%s sz=%dx%d" % (
            _ah, _ar, _ar[2]-_ar[0], _ar[3]-_ar[1]))

    # 실증 절대좌표: (890, 422) @ 창위치(599,209) → 창 상대: wx+291, wy+213
    win_rect = _get_window_rect_safe(hwnd)
    if not win_rect:
        print("[WARN] 창 rect 탐색 실패 -- '아이디' 탭 클릭 생략")
        return
    wx, wy = win_rect[0], win_rect[1]

    # 창 포커스 확보
    _force_foreground(hwnd)
    time.sleep(0.15)

    # 정확 좌표로 직접 클릭 (3회 시도, ±5px 미세 보정)
    _tab_candidates = [
        (wx + 291, wy + 213),  # 실증 좌표 (890, 422)
        (wx + 286, wy + 210),  # -5px 보정
        (wx + 296, wy + 216),  # +5px 보정
        (wx + 280, wy + 213),  # x만 -11px
    ]

    for _ti, (tab_x, tab_y) in enumerate(_tab_candidates):
        print("[INFO] '아이디' 탭 클릭 시도%d: screen(%d,%d)" % (_ti, tab_x, tab_y))
        try:
            win32api.SetCursorPos((tab_x, tab_y))
            time.sleep(0.12)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.08)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        except Exception as e:
            print("[WARN] SetCursorPos 실패 시도%d: %s" % (_ti, e))
            _post_nclbclick(hwnd, tab_x, tab_y)

        for _t in range(3):
            time.sleep(0.20)
            _edits = _collect_wide_edits_visibility(hwnd)
            if _edits and any(v for _, _, v in _edits):
                print("[INFO] '아이디' 탭 클릭 성공: screen(%d,%d) → Edit 가시화" % (tab_x, tab_y))
                return

    print("[WARN] '아이디' 탭 4회 시도 후 Edit 비가시 -- 계속 진행 (비가시 Edit WM_SETTEXT 폴백)")


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

    # 실증 절대좌표: (770, 614) @ 창위치(599,209) → 창 상대: wx+171, wy+405
    btn_x = wx + 171
    btn_y = wy + 405

    print("[INFO] CREON 모의투자로그인 버튼 클릭: screen(%d,%d)" % (btn_x, btn_y))
    _force_foreground(hwnd)
    time.sleep(0.20)
    _click_at_screen(hwnd, btn_x, btn_y)
    time.sleep(0.30)


def _click_creon_mock_access(hwnd):
    """
    CREON '모의투자 선택' 팝업의 '모의투자 접속' 버튼 클릭.

    순서:
    1. 자식 Button BM_CLICK (텍스트 매칭)
    2. 자식창 덤프 (진단용 -- 팝업 구조 파악)
    3. 좌표 다중 시도 (wy+75, +90, +100, +115, +130, +150)

    hwnd: 모의투자 선택 팝업 hwnd or CREON 메인 창 hwnd
    """
    try:
        if not win32gui.IsWindowVisible(hwnd):
            return
        win_rect = win32gui.GetWindowRect(hwnd)
    except Exception:
        return

    wx, wy = win_rect[0], win_rect[1]
    ww = win_rect[2] - win_rect[0]
    wh = win_rect[3] - win_rect[1]

    # 자식창 덤프 (진단 -- 버튼 위치 파악)
    children_info = []
    try:
        def _dump_child(c, _):
            try:
                r = win32gui.GetWindowRect(c)
                children_info.append((c, win32gui.GetClassName(c),
                                      win32gui.GetWindowText(c), r))
            except Exception:
                pass
        win32gui.EnumChildWindows(hwnd, _dump_child, None)
    except Exception:
        pass
    if children_info:
        print("[DEBUG] 모의투자팝업 hwnd=%d 자식창(%d개):" % (hwnd, len(children_info)))
        for c, cn, ct, r in children_info:
            print("  hwnd=%d cls='%s' txt='%s' sz=%dx%d pos=(%d,%d)" % (
                c, cn, ct[:30], r[2]-r[0], r[3]-r[1], r[0], r[1]))

    # 먼저 버튼 BM_CLICK 시도
    found_btns = _find_child_by_exact_text(hwnd, MOCK_ACCESS_BUTTON_TEXTS, class_name="Button")
    if not found_btns:
        found_btns = _find_child_by_text_contains(hwnd, [u"접속"], class_name="Button")
    if found_btns:
        btn_hwnd, btn_text = found_btns[0]
        print("[INFO] CREON 모의투자 접속 BM_CLICK: hwnd=%d text='%s'" % (btn_hwnd, btn_text))
        _post_button_click(btn_hwnd)
        time.sleep(0.30)
        return

    # Button 미발견 (오너드로) → 좌표 다중 시도
    _force_foreground(hwnd)
    time.sleep(0.20)

    if ww < 800:
        # 팝업 hwnd -- 실증 절대좌표: (962,509) @ popup위치(wy=262) → wy+247
        # 기존 wy+130=392 는 버튼 위치보다 117px 위로 오클릭이었음
        btn_x = wx + ww // 2
        y_offsets = (247, 230, 260, 215, 280)
        print("[INFO] CREON 모의투자 접속 좌표 다중시도: x=%d, wy=%d, offsets=%s" % (btn_x, wy, y_offsets))
        for _oy in y_offsets:
            btn_y = wy + _oy
            _click_at_screen(hwnd, btn_x, btn_y)
            time.sleep(0.20)
    else:
        # 메인 창 hwnd
        btn_x = wx + ww // 2
        btn_y = wy + 400
        print("[INFO] CREON 모의투자 접속 메인창 클릭: screen(%d,%d)" % (btn_x, btn_y))
        _click_at_screen(hwnd, btn_x, btn_y)
        time.sleep(0.30)


def _collect_wide_edits_visibility(parent_hwnd):
    """
    parent_hwnd 하위 모든 Edit-류 컨트롤(width>50) 가시 여부 목록 반환.

    "Edit" 정확 매치 외에 "EDIT"/"RICHEDIT"/"TEXTBOX" 포함 클래스명도 탐색
    (CREON Afx 커스텀 Edit 클래스 대응).
    반환: [(hwnd, class_name, is_visible), ...]
    """
    results = []
    def _ev(ch, _):
        try:
            cn = win32gui.GetClassName(ch)
            is_edit = (cn == "Edit") or any(
                kw in cn.upper() for kw in ("EDIT", "RICHEDIT", "TEXTBOX")
            )
            if is_edit:
                r = win32gui.GetWindowRect(ch)
                if (r[2] - r[0]) > 50:
                    results.append((ch, cn, win32gui.IsWindowVisible(ch)))
        except Exception:
            pass
    try:
        win32gui.EnumChildWindows(parent_hwnd, _ev, None)
    except Exception:
        pass
    return results


def _get_afx_panel(hwnd):
    """로그인 창 좌측 Afx 패널 (width>200, height>400)의 화면 좌표 (px, py) 반환."""
    afx_list = []
    def _cb(ch, _):
        try:
            if "Afx" in win32gui.GetClassName(ch) and win32gui.IsWindowVisible(ch):
                r = win32gui.GetWindowRect(ch)
                if (r[2]-r[0]) > 200 and (r[3]-r[1]) > 400:
                    afx_list.append((ch, r))
        except Exception:
            pass
    try:
        win32gui.EnumChildWindows(hwnd, _cb, None)
    except Exception:
        pass
    if not afx_list:
        return None, None
    afx_list.sort(key=lambda x: x[1][0])
    r = afx_list[0][1]
    return r[0], r[1]  # screen x, y of leftmost large Afx panel


def _select_creon_plus_by_coordinate(hwnd):
    """
    CREON 로그인 창 좌상단 드롭다운에서 'CREON Plus' 를 좌표 기반으로 선택.

    실증 분석 결과:
    - 좌측 Afx 패널: HTRANSPARENT → 모든 마우스가 부모(login_hwnd)로 전달
    - login_hwnd 전체: HTCAPTION (커스텀 타이틀바)
    - 드롭다운 열기:    패널 (+90, +15) 클릭
    - CREON Plus 항목: 패널 (+65, +85) [hover 300 ms 후 클릭]
    - ESC 전송 금지: 창이 닫힘
    - _force_foreground 금지: 드롭다운이 닫힘
    """
    px, py = _get_afx_panel(hwnd)
    if px is None:
        print("[WARN] CREON 패널 탐색 실패 -- CREON Plus 선택 생략, 로그인 계속")
        return True

    print("[DEBUG] Afx 패널 좌상단: screen(%d,%d)  창hwnd=%d" % (px, py, hwnd))

    # ── 사전 검증: Edit 가시 상태 안정화 대기 (최대 2s) ──────────────────────
    # 창이 막 열린 직후에는 Edit 컨트롤이 아직 렌더링되지 않아 invisible일 수 있음.
    # CREON Plus 이미 선택 여부와 구별하려면 충분히 기다린 후 판단해야 함.
    initial_edits = []
    for _init_t in range(8):  # 0.25s × 8 = 2s
        initial_edits = _collect_wide_edits_visibility(hwnd)
        if initial_edits and any(v for _, _, v in initial_edits):
            break  # 적어도 1개 visible → 창 초기화 완료
        time.sleep(0.25)
    print("[DEBUG] 초기 Edit 상태 (%d개, %.2fs 안정화): %s" % (
        len(initial_edits),
        _init_t * 0.25,
        [(cn, v) for _, cn, v in initial_edits]
    ))

    # 2s 후에도 Edit 모두 비가시 → CREON Plus 이미 선택된 것으로 판단
    if initial_edits and all(not v for _, _, v in initial_edits):
        print("[INFO] CREON Plus 이미 선택됨 (2s 안정화 후 Edit 모두 비가시) -- 선택 생략")
        return True

    win_before = _get_window_rect_safe(hwnd)

    # CREON Plus 선택 -- 최대 3회 재시도 + 선택 검증
    for _retry in range(3):
        if _retry > 0:
            print("[INFO] CREON Plus 선택 재시도 %d/3..." % (_retry + 1))
            time.sleep(0.8)
            # Afx 패널 좌표 재계산 (창 이동 대비) -- 창 좌표가 아닌 Afx 패널 좌표로
            new_px, new_py = _get_afx_panel(hwnd)
            if new_px is not None:
                print("[DEBUG] Afx 패널 좌표 갱신: (%d,%d) → (%d,%d)" % (px, py, new_px, new_py))
                px, py = new_px, new_py
            win_before = _get_window_rect_safe(hwnd)

        # ── 헤더 클릭 → 드롭다운 열기 ───────────────────────────────────────
        # 실증 절대좌표: (662, 233) @ 창위치(599,209) → 창 상대: wx+63, wy+24
        hdr_x, hdr_y = win_before[0] + 63, win_before[1] + 24
        print("[INFO] CREON Plus 드롭다운 열기: screen(%d,%d)" % (hdr_x, hdr_y))
        _post_nclbclick(hwnd, hdr_x, hdr_y, hover_ms=0)
        time.sleep(0.15)
        try:
            win32api.SetCursorPos((hdr_x, hdr_y))
            time.sleep(0.10)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.08)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        except Exception as e:
            print("[WARN] 헤더 SetCursorPos 실패: %s" % e)
        time.sleep(0.80)  # 드롭다운 팝업 렌더링 대기

        # ── 드롭다운 팝업 hwnd 탐색 (메인창 근처의 새 팝업) ─────────────────
        main_rect = _get_window_rect_safe(hwnd) or (0, 0, 0, 0)
        dropdown_hwnd = None
        _dd_candidates = []
        def _find_dd_popup(h, _):
            if h == hwnd or not win32gui.IsWindowVisible(h):
                return
            try:
                r = win32gui.GetWindowRect(h)
                # 메인 창 근처(±200px) 이고 작은 창(폭<500) 인 경우
                near_x = abs(r[0] - main_rect[0]) < 200
                near_y = abs(r[1] - main_rect[1]) < 200
                small = (r[2] - r[0]) < 500
                if near_x and near_y and small:
                    _dd_candidates.append((h, r, win32gui.GetClassName(h),
                                           win32gui.GetWindowText(h)))
            except Exception:
                pass
        try:
            win32gui.EnumWindows(_find_dd_popup, None)
        except Exception:
            pass
        if _dd_candidates:
            print("[DEBUG] 드롭다운 팝업 후보: %s" % [
                (h, r, cn, ct) for h, r, cn, ct in _dd_candidates])
            # 첫 번째 후보를 드롭다운으로 사용
            dropdown_hwnd, _dd_rect = _dd_candidates[0][0], _dd_candidates[0][1]
            print("[INFO] 드롭다운 hwnd=%d rect=%s" % (dropdown_hwnd, _dd_rect))
        else:
            print("[DEBUG] 드롭다운 팝업 미탐지 -- 헤더클릭이 드롭다운을 열지 않음?")

        # 창 이동 보정
        win_after = _get_window_rect_safe(hwnd)
        dx = (win_after[0] - win_before[0]) if (win_before and win_after) else 0
        dy = (win_after[1] - win_before[1]) if (win_before and win_after) else 0

        # ── CREON Plus 항목 클릭 ─────────────────────────────────────────────
        # PostMessage(WM_NCLBUTTONDOWN) to 메인창 금지: 드롭다운 팝업을 닫음
        # SetCursorPos + mouse_event 단독 사용
        if dropdown_hwnd:
            # 드롭다운 팝업 기준 ONE 클릭 per retry
            # - 팝업 첫 클릭으로 팝업이 닫힘 → 같은 retry에서 여러 y 시도 불가
            # - 팝업 높이 70px 기준 3항목 × 23px: CREON=offset~34, CREON Plus=offset~58
            # - retry 인덱스로 y 오프셋을 달리해 CREON Plus를 탐색
            _dd_r = _dd_candidates[0][1]
            cp_x = (_dd_r[0] + _dd_r[2]) // 2
            # 실증 절대좌표: CREON Plus 항목 y=298 @ popup_top=246 → offset=52
            _per_retry_offsets = (52, 42, 62, 35, 72)  # retry별 ONE 클릭
            _oy = _per_retry_offsets[min(_retry, len(_per_retry_offsets) - 1)]
            cp_y = _dd_r[1] + _oy
            print("[INFO] 드롭다운 팝업 기준 CREON Plus 항목 클릭: retry%d y_offset=%d screen(%d,%d)" % (
                _retry, _oy, cp_x, cp_y))
            try:
                win32api.SetCursorPos((cp_x, cp_y))
                time.sleep(0.20)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.10)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                print("[INFO] 드롭다운 아이템 클릭 완료")
            except Exception as e:
                print("[WARN] 드롭다운 아이템 클릭 실패: %s" % e)
        else:
            # 드롭다운 미탐지: 기존 고정 좌표 방식 fallback
            cp_x = px + 65 + dx
            cp_y = py + 85 + dy
            print("[INFO] CREON Plus 항목 고정좌표 클릭: screen(%d,%d) [SetCursorPos]" % (cp_x, cp_y))
            try:
                win32api.SetCursorPos((cp_x, cp_y))
                time.sleep(0.18)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.08)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                print("[INFO] CREON Plus 고정좌표 클릭 완료")
            except Exception as e:
                print("[WARN] SetCursorPos 실패 -- PostMessage fallback: %s" % e)
                _post_nclbclick(hwnd, cp_x, cp_y, hover_ms=300)

        time.sleep(0.5)

        # ── 선택 검증 ────────────────────────────────────────────────────────
        # CREON Plus 선택 후: 넓은 Edit 컨트롤(ID/PW)이 비가시(invisible)로 전환됨
        # CREON(일반) 선택 유지 시: Edit 컨트롤 계속 visible → 재시도 필요
        verify_edits = _collect_wide_edits_visibility(hwnd)
        print("[DEBUG] CREON Plus 선택 검증 (%d개): %s" % (
            len(verify_edits),
            [(cn, v) for _, cn, v in verify_edits]
        ))

        if verify_edits:
            all_invisible = all(not v for _, _, v in verify_edits)
            if all_invisible:
                print("[INFO] CREON Plus 선택 완료 (검증 통과 -- Edit 모두 비가시)")
                return True
            print("[INFO] CREON Plus 선택 검증 실패 (Edit 여전히 가시) -- 재시도")
        else:
            # Edit 컨트롤 미탐지: 아직 상태 확인 불가 -- 마지막 시도에서만 통과 처리
            if _retry == 2:
                print("[WARN] CREON Plus 선택 검증: Edit 미탐지 (3회 완료) -- 완료로 간주")
                return True
            print("[INFO] Edit 컨트롤 미탐지 -- 상태 불확실, 재시도 %d/3" % (_retry + 1))

    print("[WARN] CREON Plus 선택 3회 재시도 후에도 검증 실패 -- 계속 진행")
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
    """정확한 제목 일치로 로그인 창 탐지.

    주의: 'CREON Starter' 제목의 COMAIN.EXE 실행중 다이얼로그가 같은 제목을 가짐.
    이 경우 Afx 패널이 없고 '예(Y)'/'아니요(N)' 버튼만 존재 → 감지 후 '예' 클릭하고 None 반환.
    """
    SKIP_CLASSES = {"Shell_TrayWnd", "CabinetWClass", "ExploreWClass", "ShellTabWindowClass"}
    result = [None]
    comain_hwnd = [None]

    def _enum(hwnd, _):
        if result[0]:
            return
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            if win32gui.GetClassName(hwnd) in SKIP_CLASSES:
                return
            if win32gui.GetWindowText(hwnd) not in LOGIN_WINDOW_TITLES:
                return
            # 자식 컨트롤 열거해서 COMAIN 다이얼로그인지 판별
            children = []
            def _ec(c, __):
                children.append(c)
            try:
                win32gui.EnumChildWindows(hwnd, _ec, None)
            except Exception:
                pass
            has_afx = any("Afx" in (win32gui.GetClassName(c) or "") for c in children)
            has_comain = any(
                "COMAIN" in (win32gui.GetWindowText(c) or "").upper()
                for c in children
            )
            if has_comain and not has_afx:
                # COMAIN.EXE "이미 실행중" 다이얼로그 - 로그인 창 아님
                comain_hwnd[0] = hwnd
                return
            result[0] = hwnd
        except Exception:
            pass

    try:
        win32gui.EnumWindows(_enum, None)
    except Exception:
        pass

    # COMAIN.EXE 다이얼로그 감지 시 '예(Y)' 버튼 클릭
    if comain_hwnd[0] and not result[0]:
        _chw = comain_hwnd[0]
        print("[INFO] COMAIN.EXE 실행중 다이얼로그 감지 hwnd=%d -- '예(&Y)' 클릭" % _chw)
        yes_found = [False]
        def _click_yes(c, __):
            if yes_found[0]:
                return
            try:
                t = win32gui.GetWindowText(c)
                cn = win32gui.GetClassName(c)
                if cn == "Button" and "예" in t:
                    win32gui.PostMessage(c, win32con.BM_CLICK, 0, 0)
                    yes_found[0] = True
                    print("[INFO] COMAIN.EXE 다이얼로그 '예' 클릭 완료")
            except Exception:
                pass
        try:
            win32gui.EnumChildWindows(_chw, _click_yes, None)
        except Exception:
            pass
        if not yes_found[0]:
            # fallback: WM_CLOSE
            try:
                win32gui.PostMessage(_chw, win32con.WM_CLOSE, 0, 0)
                print("[INFO] COMAIN.EXE 다이얼로그 WM_CLOSE 전송")
            except Exception:
                pass
        time.sleep(0.8)

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
        """물리 클릭 → EM_SETSEL(전체선택) → WM_CLEAR → WM_SETTEXT (CREON/CYBOS 공통)
        비가시 Edit의 경우: 물리 클릭 생략 → WM_SETTEXT 직접 주입 (CREON Plus 모드)
        """
        is_visible = win32gui.IsWindowVisible(edit_hwnd)
        rect = _get_window_rect_safe(edit_hwnd)
        if not is_visible:
            # CREON Plus 모드: Edit가 비가시 → 물리 클릭 금지 (다른 컨트롤 클릭됨)
            # WM_SETTEXT 직접 주입으로 텍스트 설정 (클릭 없이 동작)
            print("[INFO] 비가시 Edit %s hwnd=%d -- 물리클릭 생략, WM_SETTEXT 직접 주입" % (label, edit_hwnd))
        elif rect:
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
            if is_visible:
                send_keys("^a{BACKSPACE}")
                send_keys(text)
                print("[INFO] send_keys로 %s 입력 완료" % label)
            else:
                # 비가시 Edit에서 send_keys는 다른 창에 전달될 수 있어 금지
                print("[WARN] 비가시 Edit WM_SETTEXT 실패 -- 입력 불가")
        print("[INFO] %s 입력 완료 (visible=%s → cleared → set)" % (label, is_visible))
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
    '모의투자 선택' 창을 세 가지 방법으로 탐색:
      1. FindWindow 직접 탐색 (최우선 — 정확한 타이틀 매치)
      2. 키워드 기반 EnumWindows (단, CREON/CYBOS 메인 데스크 창은 제외)
      3. CREON 메인 창 자식 다이얼로그 탐색 (child #32770 검색)
    중복 hwnd를 제거하며, 정확한 매치를 항상 앞에 반환한다.

    **제외 패턴**: '금융지원센터' 포함 제목은 CREON 메인 데스크이므로 무조건 제외.
    """
    seen = set()
    exact_cands = []   # "모의투자 선택" 정확 매치 -- 앞에 배치
    fuzzy_cands = []   # 키워드 부분 매치 -- 뒤에 배치

    # ── ① FindWindow 직접 탐색 (최우선) ─────────────────────────────────────
    for title_exact in (u"모의투자 선택", u"모의투자선택"):
        try:
            direct_hwnd = win32gui.FindWindow(None, title_exact)
            if direct_hwnd and direct_hwnd not in seen and win32gui.IsWindowVisible(direct_hwnd):
                exact_cands.append((direct_hwnd, title_exact))
                seen.add(direct_hwnd)
        except Exception:
            pass

    # ── ② 키워드 기반 EnumWindows (메인 데스크 제외) ────────────────────────
    # "금융지원센터" = CREON 메인 데스크 창 고유 마커 → 제외
    _DESKTOP_MARKERS = [u"금융지원센터", u"크레온 데스크", u"CREON Desktop", u"CYBOS Desktop"]
    raw = _find_window_by_keywords(MOCK_DIALOG_KEYWORDS, require_visible=True)
    for hwnd, title in raw:
        if hwnd in seen:
            continue
        if any(m in title for m in _DESKTOP_MARKERS):
            continue  # 메인 CREON 데스크 창은 "모의투자" 포함이지만 팝업 아님
        if title.strip() in (u"모의투자 선택", u"모의투자선택"):
            exact_cands.append((hwnd, title))
        else:
            fuzzy_cands.append((hwnd, title))
        seen.add(hwnd)

    # ── ③ CREON 메인 창 자식 다이얼로그 탐색 ────────────────────────────────
    # "모의투자 선택"이 CREON Desktop의 child dialog인 경우를 커버
    if BROKER_TYPE == "creon":
        creon_desk_hwnd = [None]
        def _desk_cb(h, _):
            try:
                if win32gui.IsWindowVisible(h) and u"금융지원센터" in win32gui.GetWindowText(h):
                    creon_desk_hwnd[0] = h
            except Exception:
                pass
        try:
            win32gui.EnumWindows(_desk_cb, None)
        except Exception:
            pass

        if creon_desk_hwnd[0]:
            def _child_cb(ch, _):
                try:
                    if ch in seen:
                        return
                    if not win32gui.IsWindowVisible(ch):
                        return
                    ch_title = win32gui.GetWindowText(ch).strip()
                    if ch_title in (u"모의투자 선택", u"모의투자선택"):
                        exact_cands.append((ch, ch_title))
                        seen.add(ch)
                except Exception:
                    pass
            try:
                win32gui.EnumChildWindows(creon_desk_hwnd[0], _child_cb, None)
            except Exception:
                pass

    return exact_cands + fuzzy_cands


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

        # ④ CREON: 모의투자 선택 팝업 좌표 클릭 fallback
        # 우선순위:
        #   (a) FindWindow "모의투자 선택" → _click_creon_mock_access(popup_hwnd)
        #   (b) EnumWindows에서 소형 팝업(ww<800) 탐색 → 동일
        #   (c) 실증 절대좌표 (962, 509) 직접 클릭 (팝업 미탐지 시 폴백)
        if BROKER_TYPE == "creon" and not popup_handled:
            if (time.time() - last_blind) >= BLIND_INTERVAL and elapsed >= 3:
                try:
                    _mock_hwnd = None
                    # (a) 타이틀 직접 탐색
                    for _t in (u"모의투자 선택", u"모의투자선택"):
                        _h = win32gui.FindWindow(None, _t)
                        if _h and win32gui.IsWindowVisible(_h):
                            _mock_hwnd = _h
                            break
                    # (b) EnumWindows 소형 팝업(ww<800) 탐색
                    if not _mock_hwnd:
                        _small_popup_ref = [None]
                        def _sp(h, _):
                            if _small_popup_ref[0]:
                                return
                            try:
                                if not win32gui.IsWindowVisible(h):
                                    return
                                r = win32gui.GetWindowRect(h)
                                ww_ = r[2] - r[0]
                                if 100 < ww_ < 800:
                                    t = win32gui.GetWindowText(h)
                                    if u"모의투자" in t or u"선택" in t:
                                        _small_popup_ref[0] = h
                            except Exception:
                                pass
                        win32gui.EnumWindows(_sp, None)
                        _mock_hwnd = _small_popup_ref[0]

                    if _mock_hwnd and win32gui.IsWindowVisible(_mock_hwnd):
                        _click_creon_mock_access(_mock_hwnd)
                        last_blind = time.time()
                    else:
                        # (c) 절대좌표 폴백: (962,509) -- 실증 확인된 "모의투자 접속" 버튼
                        # ※ MW0601 PC 전용 (1920×1080, 팝업 top≈262).
                        # 타 PC 배포 시 Mouse.py F11로 팝업 버튼 좌표 재실측 후 수정.
                        print("[INFO] CREON 모의투자팝업 미탐지 -- 실증좌표 (962,509) 직접 클릭")
                        try:
                            win32api.SetCursorPos((962, 509))
                            time.sleep(0.12)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            time.sleep(0.10)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        except Exception as _ec:
                            print("[WARN] 좌표 폴백 클릭 실패: %s" % _ec)
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
            # 연결 직후 공지사항 등 잔여 다이얼로그 마무리
            time.sleep(2)
            for _ in range(6):
                if _dismiss_error_dialogs() == 0:
                    break
                time.sleep(0.8)
            # 공지사항 테이블 닫기: 실증 절대좌표 (1448,161) = CREON 데스크 공지사항 X 버튼
            if BROKER_TYPE == "creon":
                time.sleep(1)
                # ※ MW0601 PC 전용 좌표 (1920×1080, CREON 데스크 고정 위치).
                # 타 PC 배포 시 Mouse.py F11로 공지사항 X 버튼 좌표 재실측 후 수정.
                for _nt in range(3):
                    try:
                        win32api.SetCursorPos((1448, 161))
                        time.sleep(0.10)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        time.sleep(0.08)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        print("[INFO] 공지사항 닫기 클릭: screen(1448,161) %d/3" % (_nt + 1))
                    except Exception as _e:
                        print("[WARN] 공지사항 닫기 실패: %s" % _e)
                    time.sleep(0.5)
            return True

        print("[WARN] 시도 %d/%d 연결 실패" % (attempt + 1, MAX_LOGIN_ATTEMPTS))

    print("[ERROR] Auto-login failed.")
    return False


if __name__ == "__main__":
    success = autologin()
    sys.exit(0 if success else 1)
