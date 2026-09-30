# -*- coding: utf-8 -*-
"""[MW0601 645차 / G-2] 브랜치·HEAD·상태를 **git 호출 한 번**으로 뽑는 점검용 유틸.

## 왜 있는가

2026-09-30 하루에 `.git/index.lock` 이 세 번 생겼는데, 전부 점검 세션이
`branch` · `status` · `log` 를 **연달아** 치던 시점이었다. 어느 하위명령이 원인인지는
아직 특정되지 않았다(F-4 진단 로깅이 그 일을 한다). 원인과 무관하게 **호출 횟수를
줄이는 것**은 확실히 노출을 줄인다.

`git status --porcelain=v2 --branch` 한 번이 브랜치명·HEAD sha·upstream·앞섬/뒤짐·
변경 목록을 **모두** 준다. `branch --show-current` + `rev-parse` + `status` 세 번을
이 한 번으로 대체한다. 최근 커밋이 필요하면 `--log N` 으로 **한 번만** 더 부른다.

모든 호출은 `--no-optional-locks` + `GIT_OPTIONAL_LOCKS=0` (SKILL.md 「git 호출
규약」, 641차 이중 방어). 호출 전후로 `.git/index.lock` 유무를 비교해 **이 유틸이
락을 남겼는지** 스스로 적는다 — 남겼다면 그 자체가 F-4 의 증거다.

    python scripts/git_snapshot.py
    python scripts/git_snapshot.py --log 5
    python scripts/git_snapshot.py --json

⚠ 선택적 도구다 — 기존 명령을 대체하도록 강제하지 않는다. 판정·게이트와 무관.
⚠ py3.7 호환 · 의존성 없음.
"""

from __future__ import print_function

import argparse
import json
import os
import subprocess
import sys


def _run(repo, args, timeout=25):
    """(rc, stdout, stderr). 타임아웃이면 자식을 죽이고 rc=None."""
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    p = subprocess.Popen(["git", "--no-optional-locks"] + list(args), cwd=repo,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        p.communicate()
        return None, "", "timeout %ss" % timeout
    dec = lambda b: b.decode("utf-8", "replace")
    return p.returncode, dec(out), dec(err)


def parse_porcelain_v2(text):
    """`status --porcelain=v2 --branch` 출력 → dict. 순수 함수(테스트 대상)."""
    snap = {
        "head_oid": None, "branch": None, "upstream": None,
        "ahead": None, "behind": None,
        "changed": 0, "unmerged": 0, "untracked": 0, "ignored": 0,
        "paths": [],
    }
    for line in text.splitlines():
        if line.startswith("# branch.oid "):
            snap["head_oid"] = line.split(" ", 2)[2].strip()
        elif line.startswith("# branch.head "):
            snap["branch"] = line.split(" ", 2)[2].strip()
        elif line.startswith("# branch.upstream "):
            snap["upstream"] = line.split(" ", 2)[2].strip()
        elif line.startswith("# branch.ab "):
            parts = line.split()
            try:
                snap["ahead"] = int(parts[2].lstrip("+"))
                snap["behind"] = int(parts[3].lstrip("-"))
            except (IndexError, ValueError):
                pass
        elif line.startswith("1 ") or line.startswith("2 "):
            snap["changed"] += 1
            # 1: 8번째 필드 뒤가 경로 / 2: 9번째 필드 뒤가 "경로\t원경로"
            n = 8 if line.startswith("1 ") else 9
            parts = line.split(" ", n)
            if len(parts) > n:
                snap["paths"].append(parts[n].split("\t", 1)[0])
        elif line.startswith("u "):
            snap["unmerged"] += 1
        elif line.startswith("? "):
            snap["untracked"] += 1
            snap["paths"].append(line[2:])
        elif line.startswith("! "):
            snap["ignored"] += 1
    return snap


def snapshot(repo, log_n=0):
    lock = os.path.join(repo, ".git", "index.lock")
    lock_before = os.path.exists(lock)
    rc, out, err = _run(repo, ["status", "--porcelain=v2", "--branch"])
    if rc != 0:
        snap = {"measured": False, "fail": "status rc=%s %s" % (rc, err.strip()[:200])}
    else:
        snap = parse_porcelain_v2(out)
        snap["measured"] = True
    snap["git_calls"] = 1
    if log_n > 0:
        rc2, out2, err2 = _run(repo, ["log", "-n", str(int(log_n)), "--format=%ci %h %s"])
        snap["git_calls"] += 1
        snap["log"] = out2.strip().splitlines() if rc2 == 0 else None
        if rc2 != 0:
            snap["log_fail"] = "log rc=%s %s" % (rc2, err2.strip()[:200])
    lock_after = os.path.exists(lock)
    snap["lock_before"] = lock_before
    snap["lock_after"] = lock_after
    snap["left_lock"] = (not lock_before) and lock_after
    return snap


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try:
            if hasattr(s, "reconfigure"):
                s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="git 상태 1회 호출 스냅샷")
    ap.add_argument("--repo", default=os.getcwd())
    ap.add_argument("--log", type=int, default=0, metavar="N", help="최근 커밋 N개(호출 +1)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    snap = snapshot(a.repo, log_n=a.log)
    if a.json:
        print(json.dumps(snap, ensure_ascii=False, indent=2))
    else:
        if not snap["measured"]:
            print("상태 **미측정** - %s" % snap["fail"])
        else:
            ab = ("+%s/-%s" % (snap["ahead"], snap["behind"])) if snap["ahead"] is not None else "upstream 없음"
            print("브랜치 %s · HEAD %s · %s %s" % (
                snap["branch"], (snap["head_oid"] or "")[:7], snap["upstream"] or "-", ab))
            print("변경 %d · 미추적 %d · 충돌 %d" % (
                snap["changed"], snap["untracked"], snap["unmerged"]))
        for ln in snap.get("log") or []:
            print("  " + ln)
        print("git 호출 %d회 · 락 %s" % (
            snap["git_calls"],
            "**이 유틸이 남겼다** - git_lock_guard.py --check 로 주인 진단할 것" if snap["left_lock"]
            else ("호출 전부터 있었다" if snap["lock_before"] else "없음")))
    return 2 if snap["left_lock"] else (0 if snap["measured"] else 1)


if __name__ == "__main__":
    sys.exit(main())
