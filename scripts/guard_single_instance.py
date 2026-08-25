# -*- coding: utf-8 -*-
"""[MW0601 493차 후속7 / F-U] 단일 인스턴스 가드 — 프로브·종료를 배치 밖으로.

## 왜 있는가 — 넉 달간 거짓 경고를 찍고 있었다

`start_mireuk.bat` 는 프로브를 `python -c "<300자 한 줄>"` 로 실행했다. 그 안에
`p.pid != os.getpid()` 가 있는데, 배치 최상단이 `SETLOCAL EnableDelayedExpansion`
이라 **`cmd.exe` 가 `!=` 의 느낌표를 지연확장 토큰으로 먹는다.** 파이썬에는
`p.pid = os.getpid()` 가 전달되고 **`SyntaxError` 로 죽는다.**

2026-08-25 재현 시험(`scripts/diag_guard_delayedexp.bat`) 실측:

    [A] 지연확장 ON   ->  p.pid = os.getpid()   SyntaxError, EXITCODE=1
    [B] 지연확장 OFF  ->  p.pid != os.getpid()  정상 실행, EXITCODE=0

파이썬은 예외로 죽어도 **exit 1** 이다. 그런데 배치는 `IF !ERRORLEVEL! EQU 0` 하나만
보므로 **「크래시」와 「N개 발견」이 같은 분기로 간다.** 그래서:

  · 런처 로그 11개 전수에서 `[GUARD] 기존 main.py 없음` 이 **0번** 나왔다.
    전날 정상 종료가 로그로 확인되는 날에도, **주말을 사이에 둔 월요일 아침에도**
    "감지됨" 이 떴다 — 살아 있을 수 없는 프로세스를 감지했다는 뜻이다.
  · `2>NUL` 이 traceback 을 버려 **왜 죽었는지가 어디에도 안 남았다.**
  · 프로브의 `print` 출력은 콘솔로만 가고 `CALL :L` 로그에는 안 들어가
    `grep "실행 중 main.py"` 가 로그 11개에서 **0건**이었다.
  · **종료 줄도 같은 결함**이라 `terminate()` 는 한 번도 실행된 적이 없는데
    `[GUARD] 기존 프로세스 종료 완료` 는 무조건 찍혔다.

즉 판정 근거 세 갈래(종료코드·표준오류·표준출력)가 **전부 막혀** 있었다.
계측 4원칙 ④가 역산해낸 「실패와 정상이 같은 값으로 표현된다」의 또 다른 사례다.

## 무엇을 고치나

**파이썬 소스가 `cmd.exe` 지연확장을 통과하지 않게 한다.** `^!` 이스케이프로
때우면 다음 사람이 또 밟는다 — 파일로 빼면 그 등급의 실수가 구조적으로 불가능해지고,
덤으로 유닛 테스트가 붙는다.

## 종료코드 (3분류 — 이 결함의 핵심 해소)

    0  기존 인스턴스 없음
    1  N개 발견
    3  프로브 실패 (traceback 을 stdout 에 남긴다)

⚠ **`1` 과 `3` 을 나누는 것이 요점이다.** "못 찾았다" 와 "실패했다" 가 겹치지 않는다.

## 안전 정책

  · **WORKDIR 밖 프로세스는 죽이지 않는다** (변경 9). 종전 판정식은 부분문자열
    `'main.py' in c` 라 다른 프로젝트·편집기 실행구성까지 잡았고, 그 다음 줄이
    `terminate()` 였다. 남의 프로그램을 죽이는 것은 이 런처의 권한 밖이다.
  · **명령줄 판독 실패를 0으로 위장하지 않는다** (변경 8). 32비트 파이썬은 64비트
    프로세스의 `cmdline` 을 못 읽고 `psutil` 이 `None` 을 준다 — 종전 코드는
    `(… or [])` 로 받아 **무조건 불일치**로 만들었다. 그런 프로세스는
    `unreadable` 로 **집계·로그**하고, 1건이라도 있으면 `단일 인스턴스 미확정`.
  · **절대경로 판정은 섀도로 먼저** 넣는다 (변경 5). 좁히면 진짜 잔류를 놓칠 수
    있으므로, 새 판정과 옛 판정을 **둘 다 계산해 로그에 병기**하고 실제 대상은
    당분간 옛 판정을 쓴다. 10거래일 대조 후 승격(스킬 규약).

사용법:

    python scripts/guard_single_instance.py --probe   --workdir "%WORKDIR%"
    python scripts/guard_single_instance.py --terminate --workdir "%WORKDIR%"

⚠ **`main.py`·`config/settings.py`·매매 로직은 건드리지 않는다.**
근거: `docs/정기점검/매일점검/MW0601-20260825-점검리포트.md` 1-8 / 제1부-C / F-U.
"""
from __future__ import print_function

import argparse
import os
import sys
import time
import traceback

RC_NONE = 0        # 기존 인스턴스 없음
RC_FOUND = 1       # N개 발견
RC_PROBE_FAILED = 3   # 프로브 자체가 실패 — **"없음"이 아니다**

TARGET_BASENAME = "main.py"


def _norm(path):
    """대소문자·구분자·상대경로를 정규화. Windows 경로 비교의 최소 규약."""
    if not path:
        return ""
    try:
        return os.path.normcase(os.path.abspath(path))
    except Exception:
        return ""


def _is_python_proc(info):
    return "python" in (info.get("name") or "").lower()


def _legacy_match(cmdline):
    """종전 판정 — 부분문자열. **넓다**(다른 프로젝트까지 잡는다).

    승격 전까지 실제 종료 대상은 이쪽이다(회귀 위험 관리 — F-U 회귀 위험 절).
    """
    return any(TARGET_BASENAME in (c or "") for c in (cmdline or []))


def _strict_match(cmdline, target_abs):
    """신 판정(섀도) — `WORKDIR/main.py` 절대경로 일치.

    인자가 상대경로(`main.py`)면 프로세스 cwd 기준으로 풀어야 정확하지만,
    여기서는 cwd 를 별도로 확인하므로 **경로 일치 또는 basename 일치**로 본다.
    """
    for c in (cmdline or []):
        if not c:
            continue
        if _norm(c) == target_abs:
            return True
        if os.path.basename(c).lower() == TARGET_BASENAME and _norm(c) == target_abs:
            return True
    return False


def _under(child, parent):
    """child 가 parent 하위인가(같은 경로 포함). 둘 다 정규화된 절대경로."""
    if not child or not parent:
        return False
    if child == parent:
        return True
    return child.startswith(parent.rstrip(os.sep) + os.sep)


def scan(workdir, self_pid=None):
    """프로세스를 훑어 분류한다. **예외를 삼키지 않는다** — 호출부가 rc=3으로 만든다.

    Returns dict:
        matched     [dict]  옛 판정(부분문자열) 일치 — 실제 종료 대상
        strict      [dict]  신 판정(절대경로+cwd) 일치 — **섀도**
        foreign     [dict]  옛 판정에는 걸리나 WORKDIR 밖 — **죽이지 않는다**
        unreadable  [dict]  명령줄을 못 읽은 파이썬 프로세스 — **미측정**
    """
    import psutil

    self_pid = os.getpid() if self_pid is None else self_pid
    wd = _norm(workdir)
    target_abs = _norm(os.path.join(workdir, TARGET_BASENAME)) if workdir else ""

    matched, strict, foreign, unreadable = [], [], [], []
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        info = p.info or {}
        if not _is_python_proc(info):
            continue
        if info.get("pid") == self_pid:
            continue

        cmdline = info.get("cmdline")
        if cmdline is None:
            # 🔴 **미측정이지 불일치가 아니다.** 32비트 프로브가 64비트 프로세스의
            #    명령줄을 읽으면 접근 거부가 나고 psutil 은 None 을 준다.
            #    종전 코드는 `(… or [])` 로 받아 조용히 「불일치」로 만들었다.
            unreadable.append({"pid": info.get("pid"), "name": info.get("name")})
            continue
        if not _legacy_match(cmdline):
            continue

        try:
            cwd = p.cwd()
        except Exception:
            cwd = None            # 권한 없음 — 아래에서 「미확인」으로 다룬다
        rec = {
            "pid": info.get("pid"),
            "cmd": " ".join(c for c in cmdline if c),
            "cwd": cwd,
            "started": None,
        }
        try:
            rec["started"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                           time.localtime(p.create_time()))
        except Exception:
            pass

        in_workdir = _under(_norm(cwd), wd) if (cwd and wd) else False
        if wd and cwd and not in_workdir:
            # 변경 9 — WORKDIR 밖은 **죽이지 않고 경고만** 한다.
            foreign.append(rec)
            continue
        matched.append(rec)
        if _strict_match(cmdline, target_abs) or in_workdir:
            strict.append(rec)
    return {"matched": matched, "strict": strict,
            "foreign": foreign, "unreadable": unreadable}


def render(result, action="probe"):
    """사람이 읽을 줄들. 배치가 이것을 그대로 `CALL :L` 로 로그에 넣는다.

    ⚠ 콘솔에만 찍으면 아무도 안 본다 — 아침 08:40 자동 기동의 콘솔을 사람이
      보고 있을 리 없다(그것이 이 결함이 넉 달 숨은 이유의 하나다).
    """
    lines = []
    n = len(result["matched"])
    lines.append("[GUARD] 실행 중 main.py: %d" % n)
    for r in result["matched"]:
        lines.append("[GUARD]   PID=%s started=%s cwd=%s cmd=%s"
                     % (r["pid"], r["started"], r["cwd"], r["cmd"]))
    for r in result["foreign"]:
        # 변경 5′ — 다른 프로젝트를 말없이 죽이지 않는다.
        lines.append("[GUARD] 대상 아님(타 프로젝트): PID=%s cwd=%s cmd=%s"
                     % (r["pid"], r["cwd"], r["cmd"]))
    for r in result["unreadable"]:
        # 변경 8 — 미측정을 0으로 위장하지 않는다.
        lines.append("[GUARD] 판독불가 PID=%s (%s) — 권한/비트폭"
                     % (r["pid"], r["name"]))
    if result["unreadable"]:
        lines.append("[GUARD][WARN] 단일 인스턴스 미확정 — 명령줄 판독불가 %d건"
                     % len(result["unreadable"]))
    # 변경 5 — 신 판정은 **병기만** 한다(실제 대상은 옛 판정).
    lines.append("[GUARD] 판정대조 legacy=%d strict=%d (strict는 섀도 — 종료 대상 아님)"
                 % (n, len(result["strict"])))
    return lines


def cmd_probe(args):
    result = scan(args.workdir)
    for line in render(result, "probe"):
        print(line)
    return RC_FOUND if result["matched"] else RC_NONE


def cmd_terminate(args):
    import psutil

    result = scan(args.workdir)
    targets = result["matched"]
    # 변경 7 — 죽이기 **전에** 목록을 남긴다. 사후에 "무엇을 죽였는가"가 남아야 한다.
    print("[GUARD] 종료 대상 %d개" % len(targets))
    for r in targets:
        print("[GUARD]   종료예정 PID=%s started=%s cwd=%s cmd=%s"
              % (r["pid"], r["started"], r["cwd"], r["cmd"]))
    for r in result["foreign"]:
        print("[GUARD] 보호(종료 안 함) PID=%s cwd=%s — WORKDIR 밖" % (r["pid"], r["cwd"]))
    if not targets:
        print("[GUARD] 종료 대상 없음")
        return RC_NONE

    killed = 0
    for r in targets:
        try:
            psutil.Process(r["pid"]).terminate()
            killed += 1
        except Exception as exc:
            print("[GUARD][WARN] PID=%s 종료 실패: %s" % (r["pid"], exc))

    # 변경 6 — **재확인.** 무조건 출력되던 "완료"를 검증된 문장으로 바꾼다.
    time.sleep(args.settle_sec)
    remain = scan(args.workdir)["matched"]
    if remain:
        print("[GUARD][ERROR] 잔여 %d개 — 수동 확인 필요" % len(remain))
        for r in remain:
            print("[GUARD]   잔여 PID=%s cmd=%s" % (r["pid"], r["cmd"]))
        return RC_FOUND
    print("[GUARD] 종료 완료 (killed=%d, 잔여=0)" % killed)
    return RC_NONE


def main(argv=None):
    ap = argparse.ArgumentParser(description="미륵이 단일 인스턴스 가드")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--probe", action="store_true", help="탐지만 (0=없음 1=발견 3=실패)")
    g.add_argument("--terminate", action="store_true", help="종료 후 재확인")
    ap.add_argument("--workdir", default=None,
                    help="미륵이 리포 루트. 이 밖의 프로세스는 종료하지 않는다")
    ap.add_argument("--settle-sec", type=float, default=3.0)
    args = ap.parse_args(argv)

    if not args.workdir:
        args.workdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    try:
        return cmd_terminate(args) if args.terminate else cmd_probe(args)
    except Exception:
        # 🔴 **핵심** — 실패를 「없음」으로 흘려보내지 않는다.
        #   traceback 을 stdout 에 남긴다(배치가 `2>NUL` 로 버리던 것이 stderr 였다).
        print("[GUARD][ERROR] 프로브 실패 — 단일 인스턴스 보장 불가")
        traceback.print_exc(file=sys.stdout)
        return RC_PROBE_FAILED


if __name__ == "__main__":
    sys.exit(main())
