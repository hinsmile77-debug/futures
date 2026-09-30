# -*- coding: utf-8 -*-
"""[MW0601 645차 / F-4] `.git/index.lock` 의 「주인」 진단 — 판정 도구의 보조.

## 왜 별도 파일인가

판정 정본 `scripts/git_lock_guard.py` 는 형제 저장소(fuoption)에 **바이트 단위로 같은
사본**이 있고 `tests/test_483` 이 그 일치를 강제한다. 진단을 거기에 넣으면 이 저장소만
고쳐져 사본이 갈라진다. 그래서 판정은 정본에 두고, 진단은 여기서 정본을 불러 **덧붙이기만**
한다. 🔴 **HOLD/STALE 판정·회수는 여기서 하지 않는다.**

## 왜 있는가

2026-09-30 하루에 `.git/index.lock` 이 세 번(장전·장중·장후) 생겼다. 두 번은 STALE
(회수 필요), 한 번은 다시 보니 **없어져 있었다**(자연소멸). 정본은 git 프로세스
**개수**만 남겨 두 갈래를 가르지 못했다:

    갈래 1  쥔 프로세스가 없다            → 중단·강제종료된 명령의 잔재(진짜 스테일 후보)
    갈래 2  락보다 먼저 시작한 git 이 산다 → 그 명령이 지금 쥐고 있다(곧 풀리거나 방치)

락이 있을 때만 git 프로세스의 pid·시작시각·명령줄을 찍고 락 mtime 과 비교해 갈래를
표기한다. `--recheck SEC` 는 판정보류 락을 SEC초 뒤 한 번 더 봐서 자연소멸 여부를 적는다.

    python scripts/git_lock_diag.py
    python scripts/git_lock_diag.py --recheck 30
    python scripts/git_lock_diag.py --json

종료코드: 0 락 없음(또는 재관측 때 소멸) · 3 락 있음 · 1 실행 오류. 판정 종료코드
(2=스테일)는 정본 `git_lock_guard.py --check` 가 낸다.

⚠ py3.7 호환 · 의존성 없음(정본 외).
"""

from __future__ import print_function

import argparse
import json
import os
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import git_lock_guard as _glg  # noqa: E402  판정 정본

#: 프로세스 시작시각과 락 mtime 비교의 허용 오차(초). mtime 해상도·CIM 반올림 흡수.
ORIGIN_SLACK_SEC = 2.0

_PS_SNAPSHOT = (
    "Get-CimInstance Win32_Process -Filter \"Name='git.exe'\" | ForEach-Object { "
    "'{0}`t{1}`t{2}' -f $_.ProcessId, "
    "[int64](($_.CreationDate.ToUniversalTime() - [datetime]'1970-01-01').TotalSeconds), "
    "$_.CommandLine }"
)


def git_process_snapshot():
    """실행 중 git 프로세스 [{pid, started_epoch, cmd}]. 못 세면 None(미측정).

    빈 리스트(=0개 확인)와 None(=못 셌다)을 구분한다 — 계측 4원칙 ②.
    """
    if os.name == "nt":
        try:
            p = subprocess.Popen(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS_SNAPSHOT],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, _ = p.communicate(timeout=20)
            if p.returncode != 0:
                return None
            rows = []
            for line in out.decode("utf-8", "replace").splitlines():
                parts = line.rstrip("\r").split("\t", 2)
                if len(parts) < 2 or not parts[0].strip().isdigit():
                    continue
                try:
                    started = float(parts[1])
                except ValueError:
                    started = None
                rows.append({"pid": int(parts[0]), "started_epoch": started,
                             "cmd": parts[2] if len(parts) > 2 else ""})
            return rows
        except Exception:
            return None
    try:  # POSIX (코웍 리눅스 샌드박스)
        p = subprocess.Popen(["ps", "-eo", "pid=,etimes=,args="],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = p.communicate(timeout=10)
        if p.returncode != 0:
            return None
        now = time.time()
        rows = []
        for line in out.decode("utf-8", "replace").splitlines():
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            argv0 = os.path.basename(parts[2].split(" ", 1)[0])
            if argv0 != "git" and not argv0.startswith("git-"):
                continue
            try:
                rows.append({"pid": int(parts[0]), "started_epoch": now - float(parts[1]),
                             "cmd": parts[2]})
            except ValueError:
                continue
        return rows
    except Exception:
        return None


def classify_lock_origin(lock_mtime, procs, slack_sec=ORIGIN_SLACK_SEC):
    """(code, text). 판정에는 쓰지 않는다 — 사람이 갈래를 읽기 위한 표기다.

    UNMEASURED 프로세스 목록 미측정 · ORPHAN git 0개(갈래 1) ·
    HELD 락보다 먼저 시작한 git 생존(갈래 2) · UNRELATED 도는 git 은 전부 락 이후 시작 ·
    UNKNOWN 시작시각 미측정뿐
    """
    if procs is None:
        return "UNMEASURED", "git 프로세스 목록 **미측정** - 주인 판별 불가"
    if not procs:
        return "ORPHAN", "쥔 git 프로세스 없음 - 중단/강제종료된 명령의 잔재(갈래 1)"
    known = [p for p in procs if p.get("started_epoch") is not None]
    older = [p for p in known if p["started_epoch"] <= lock_mtime + slack_sec]
    if older:
        return "HELD", "락보다 먼저 시작한 git %d개 실행 중 - 그 명령이 쥐고 있을 수 있다(갈래 2)" % len(older)
    if known:
        return "UNRELATED", "도는 git %d개는 전부 락 이후 시작 - 락 주인은 이미 사라졌다(갈래 1에 가깝다)" % len(known)
    return "UNKNOWN", "git %d개 실행 중이나 시작시각 미측정" % len(procs)


def diagnose_lock(repo, procs_fn=None):
    """락이 있으면 주인 진단 dict, 없으면 None. 읽기만 한다."""
    lock = os.path.join(repo, ".git", "index.lock")
    try:
        mtime = os.stat(lock).st_mtime
    except OSError:
        return None
    procs = (procs_fn or git_process_snapshot)()
    code, text = classify_lock_origin(mtime, procs)
    return {
        "lock_mtime": mtime,
        "lock_mtime_txt": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
        "procs": procs,
        "origin": code,
        "origin_text": text,
    }


def inspect_with_diag(repo, **kw):
    """정본 `inspect()` 결과에 `diag` 만 덧붙인다. 판정 필드는 손대지 않는다."""
    info = _glg.inspect(repo, **kw)
    if info.get("present"):
        info["diag"] = diagnose_lock(repo)
    return info


def main(argv=None, sleep=time.sleep):
    for s in (sys.stdout, sys.stderr):
        try:
            if hasattr(s, "reconfigure"):
                s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="`.git/index.lock` 주인 진단(판정은 git_lock_guard)")
    ap.add_argument("--repo", default=os.getcwd())
    ap.add_argument("--recheck", type=int, default=0, metavar="SEC",
                    help="판정보류 락이면 SEC초 뒤 재관측해 자연소멸 여부를 적는다")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    info = inspect_with_diag(a.repo)
    # 스테일 확정 락은 기다려도 안 풀린다 — 판정보류 락만 재관측한다.
    if a.recheck > 0 and info.get("present") and not info.get("stale"):
        sleep(a.recheck)
        still = os.path.exists(os.path.join(a.repo, ".git", "index.lock"))
        info["recheck"] = {"after_sec": a.recheck, "present": still}

    if a.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print(_glg._fmt(info))
        dg = info.get("diag")
        if dg:
            print("    주인 진단 [%s] %s (락 mtime %s)" % (
                dg["origin"], dg["origin_text"], dg["lock_mtime_txt"]))
            procs = dg["procs"] or []
            for pr in procs[:5]:
                st = pr.get("started_epoch")
                print("      pid=%s 시작=%s  %s" % (
                    pr["pid"], time.strftime("%H:%M:%S", time.localtime(st)) if st else "미측정",
                    (pr.get("cmd") or "")[:160]))
            if len(procs) > 5:
                print("      … 외 %d개" % (len(procs) - 5))
        rc = info.get("recheck")
        if rc:
            print("    재관측(%d초 뒤): %s" % (
                rc["after_sec"], "여전히 있음" if rc["present"] else "자연소멸 - 갈래 2(짧게 쥐었다 놓음)"))
    if not info.get("present"):
        return 0
    if info.get("recheck") and not info["recheck"]["present"]:
        return 0
    return 3


if __name__ == "__main__":
    sys.exit(main())
