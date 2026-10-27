# -*- coding: utf-8 -*-
"""[MW0601 724차 → Sindong-V4 이식] main.py 단일 인스턴스 보장 — Windows 이름 있는 뮤텍스.

## 왜 있는가 — 2026-10-27 MW0601 이중 기동
08:40:00 에 `\\Sindong`(start_Sindong2.bat)과 `\\미륵이`(start_mireuk.bat)가 **같은 초에** 떴다
(10-26 17:05:56 `\\미륵이` 가 다시 「사용」으로 바뀐 것이 계기 — 작업 스케줄러 이벤트 140).
두 런처의 GUARD(`scripts/guard_single_instance.py --probe`)는 08:40:33–35 에 「기존 main.py 없음」을
확인했고 main.py 는 08:40:37 · 08:40:38 에 떴다 — **확인과 기동 사이 몇 초**에 서로를 못 봤다(TOCTOU).
두 프로세스 모두 같은 settings 로 신동 실주문 3계약 구성이었고, 09:02:57 첫 신동 진입은
한쪽을 끈 지 약 25초 뒤라 우연히 1벌만 나갔다. 막은 것은 설계가 아니라 타이밍이다.

GUARD 는 「이미 떠 있는 프로세스」만 볼 수 있어 이 틈을 구조적으로 못 닫는다. 그래서 **main.py 안에서**
OS 가 원자적으로 판정하는 뮤텍스를 잡는다 — 경로(스케줄러·수동 더블클릭·다른 배치)와 무관하다.

## 성질
- 이름은 작업 폴더 경로에서 만든다 → 다른 리포의 main.py 와 충돌하지 않는다(GUARD `--workdir` 와 같은 범위).
- `Local\\` 네임스페이스 — 런처·수동 기동 모두 같은 대화형 세션이다. `Global\\` 은 비승격 프로세스가
  생성 권한(SeCreateGlobalPrivilege)이 없어 실패할 수 있다.
- 승격(예약작업 RunLevel Highest) 프로세스가 만든 뮤텍스를 비승격 프로세스가 열면 `ERROR_ACCESS_DENIED`
  가 난다 — 이것도 **「이미 있음」**으로 본다(없는데 권한 오류가 날 수는 없다).
- 프로세스가 크래시로 죽어도 OS 가 핸들을 닫아 뮤텍스가 사라진다 — 락 파일과 달리 낡은 잠금이 없다.
- 판정할 수 없으면(비 Windows · ctypes 실패) **막지 않는다** — 단, `measured=False` 로 그 사실을 남긴다
  (계측 4원칙 ②: 미측정 ≠ 없음). 기동을 막으면 그날 거래가 0 이 된다.

## 런처 계약
main.py 출력은 powershell 파이프를 거쳐 종료코드가 런처에 닿지 않는다. 그래서 중복으로 물러날 때
`data/_exit_duplicate` 에 사유를 쓰고, 런처는 그 파일이 있으면 **재시작하지 않는다**.
`_exit_normally` 를 재사용하지 않는 이유: 살아 있는 쪽의 동결 센티넬이 그 파일 나이로 「종료됨」을
판정하므로(scripts/freeze_sentinel.py) 중복 쪽이 쓰면 살아 있는 인스턴스의 감시가 꺼진다.
"""
import datetime
import hashlib
import os

ERROR_ALREADY_EXISTS = 183
ERROR_ACCESS_DENIED = 5
DUPLICATE_EXIT_CODE = 17
DUPLICATE_FLAG_NAME = "_exit_duplicate"

# 프로세스 수명 동안 핸들을 쥔다 — GC 로 닫히면 뮤텍스가 풀린다.
_HANDLE = None


def mutex_name(base_dir):
    """작업 폴더 → 뮤텍스 이름. 대소문자·구분자·끝 슬래시를 정규화한다."""
    norm = os.path.normcase(os.path.normpath(os.path.abspath(base_dir)))
    digest = hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]
    return "Local\\MireukFuturesMain_" + digest


def acquire(base_dir):
    """뮤텍스 획득 시도 → (acquired, measured, detail).

    acquired=False · measured=True  : 다른 인스턴스가 이미 쥐고 있다(물러나야 한다)
    acquired=True  · measured=True  : 이 프로세스가 유일한 인스턴스다
    acquired=True  · measured=False : 판정 불가 — 막지 않되 미측정으로 남긴다
    """
    global _HANDLE
    if os.name != "nt":
        return True, False, "비 Windows — 단일 인스턴스 미측정"
    name = mutex_name(base_dir)
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateMutexW.argtypes = (ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR)
        k32.CreateMutexW.restype = wintypes.HANDLE
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        ctypes.set_last_error(0)
        h = k32.CreateMutexW(None, False, name)
        err = ctypes.get_last_error()
    except Exception as e:  # 판정 실패를 「유일함」으로 위장하지 않는다
        return True, False, "뮤텍스 판정 실패(%s: %s) — 단일 인스턴스 미측정" % (type(e).__name__, e)

    if not h:
        if err == ERROR_ACCESS_DENIED:
            return False, True, "%s 이미 존재(권한 다른 인스턴스 · err=5)" % name
        return True, False, "CreateMutexW 실패 err=%d — 단일 인스턴스 미측정" % err
    if err == ERROR_ALREADY_EXISTS:
        k32.CloseHandle(h)
        return False, True, "%s 이미 존재(err=183)" % name
    _HANDLE = h
    return True, True, name


def write_duplicate_flag(base_dir):
    """런처가 읽고 재시작을 멈추는 플래그. 실패해도 예외를 올리지 않는다(물러나는 길을 막지 않는다).

    내용은 ASCII 한 줄 — 런처가 `SET /P` 로 읽어 로그에 그대로 찍는다.
    """
    path = os.path.join(base_dir, "data", DUPLICATE_FLAG_NAME)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="ascii") as f:
            f.write("duplicate_instance pid=%d at=%s\n" % (
                os.getpid(), datetime.datetime.now().isoformat(timespec="seconds")))
        return path
    except Exception:
        return None
