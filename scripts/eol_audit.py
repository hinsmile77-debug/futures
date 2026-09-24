# -*- coding: utf-8 -*-
"""[MW0601 630차] 줄끝·BOM 진단/교정 — 형제 저장소 전수. 의존성 없는 단일 파일(py3.7+).

## 왜 있는가

`core.autocrlf=true` 가 **시스템 gitconfig** 에만 있으면 Windows git 은 CRLF 를 LF 로 환산해
「깨끗하다」고 하고, 코웍 마운트 git(미설정)은 같은 파일을 「수정됨」이라 한다(2026-09-24
futures 617개). 반대로 **스케줄러가 돌리는 LF `.bat` 은 Windows 에서 깨끗하게 보인다.**
이 도구는 두 관점을 한 번에 잰다. 전말: `docs/MW0602_적용가이드_git줄끝잠금_20260924.md`.

## 쓰는 법

    python scripts/eol_audit.py --all              진단만(기본) — 아무것도 안 바꾼다
    python scripts/eol_audit.py --repo . --fix     작업 트리 줄끝 교정 + stat 갱신
    python scripts/eol_audit.py --all --fix-bom    한글 든 BOM 없는 .ps1 에 BOM 추가(커밋 필요)

진단 항목 (저장소별):
    gattr       `.gitattributes` 유무
    bat_lf      attr eol=crlf 인데 LF 줄이 있는 파일(.bat/.cmd/.ps1) — **cmd 가 goto 레이블을 놓칠 수 있다**
    mixed       attr eol=lf 인데 CRLF·LF 가 섞인 파일
    ps1_nobom   한글 등 비ASCII 가 든 UTF-8 .ps1 인데 BOM 없음 — PowerShell 5.1 이 CP949 로 읽는다
    mount_noise 마운트 git(autocrlf 미설정) 관점에서 줄끝만으로 「수정됨」인 수

`--fix` 는 줄끝만 바꾸고 내용은 건드리지 않는다. 🔴 실행 중인 `.bat` 이 있으면 거부한다 —
cmd 는 배치를 바이트 오프셋으로 읽으므로 실행 중에 줄끝이 바뀌면 엉뚱한 줄로 튄다.

종료코드: 0 문제 없음 · 2 문제 발견(교정 후 재진단 기준) · 1 실행 오류/거부.
"""

from __future__ import print_function

import argparse
import os
import subprocess
import sys

DEFAULT_SCAN_ROOT = os.path.join(os.path.expanduser("~"), "PycharmProjects")
SHELL_EXT = (".bat", ".cmd", ".ps1")
BOM = b"\xef\xbb\xbf"


def _ensure_utf8_console():
    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _git(repo, *args, **kw):
    p = subprocess.Popen(["git", "-C", repo] + list(args), stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate(kw.get("input"))
    return out


def _tracked(repo):
    return [p for p in _git(repo, "ls-files", "-z").decode("utf-8").split("\0") if p]


def _eol_attrs(repo, paths):
    out = _git(repo, "check-attr", "-z", "--stdin", "eol",
               input="\0".join(paths).encode("utf-8")).decode("utf-8").split("\0")
    return dict((out[i], out[i + 2]) for i in range(0, len(out) - 2, 3))


def _classify(b):
    crlf = b.count(b"\r\n")
    return crlf, b.count(b"\n") - crlf


def scan(repo):
    paths = _tracked(repo)
    eol = _eol_attrs(repo, paths)
    r = {"repo": repo, "gattr": os.path.isfile(os.path.join(repo, ".gitattributes")),
         "bat_lf": [], "mixed": [], "ps1_nobom": []}
    for p in paths:
        fp = os.path.join(repo, p)
        if not os.path.isfile(fp):
            continue
        with open(fp, "rb") as f:
            b = f.read()
        if b"\0" in b[:8000]:
            continue
        crlf, lf = _classify(b)
        want = eol.get(p)
        low = p.lower()
        if lf and (want == "crlf" or (want in (None, "unspecified") and low.endswith(SHELL_EXT))):
            r["bat_lf"].append(p)
        elif crlf and lf:
            r["mixed"].append(p)
        if low.endswith(".ps1") and not b.startswith(BOM) and any(c > 127 for c in bytearray(b)):
            try:
                b.decode("utf-8")
                r["ps1_nobom"].append(p)
            except UnicodeDecodeError:
                pass  # CP949 로 저장된 파일 — PowerShell 5.1 이 제대로 읽는다
    r["mount_noise"] = mount_noise(repo)
    return r


def mount_noise(repo):
    """autocrlf 미설정 git 이 줄끝만으로 「수정됨」이라 할 파일 수.

    `git -c core.autocrlf=false status` 로는 재현되지 않는다(stat 캐시가 재해시를 건너뛴다).
    그래서 작업 트리를 직접 해시해 인덱스 sha 와 비교하고, 진짜 수정은 뺀다.
    """
    ents = []
    for e in _git(repo, "ls-files", "-s", "-z").split(b"\0"):
        if not e:
            continue
        meta, path = e.split(b"\t", 1)
        mode, sha = meta.split()[:2]
        if mode != b"160000" and os.path.isfile(os.path.join(repo, path.decode("utf-8"))):
            ents.append((path, sha.decode()))
    if not ents:
        return 0
    hashed = _git(repo, "-c", "core.autocrlf=false", "hash-object", "--stdin-paths",
                  input=b"\n".join(p for p, _ in ents) + b"\n").decode().split()
    real = set(_git(repo, "diff", "--name-only", "-z").decode("utf-8").split("\0"))
    return sum(1 for (p, s), h in zip(ents, hashed) if s != h and p.decode("utf-8") not in real)


def running_scripts(repo):
    """이 저장소의 .bat/.cmd/.ps1 을 실행 중인 프로세스. 셀 수 없으면 None(미측정)."""
    cmd = ("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine } | "
           "ForEach-Object { $_.ProcessId.ToString() + ' ' + $_.CommandLine }")
    try:
        p = subprocess.Popen(["powershell", "-NoProfile", "-Command", cmd],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.communicate(timeout=60)[0].decode("utf-8", "replace")
    except Exception:
        return None
    root = os.path.abspath(repo).lower()
    return [ln for ln in out.splitlines()
            if root in ln.lower() and any(x in ln.lower() for x in SHELL_EXT)]


def fix(repo, r):
    """줄끝 교정 + 내용이 같은데 stat 만 바뀐 항목의 인덱스 갱신."""
    n = 0
    for p in r["bat_lf"] + r["mixed"]:
        fp = os.path.join(repo, p)
        with open(fp, "rb") as f:
            b = f.read()
        norm = b.replace(b"\r\n", b"\n")
        new = norm.replace(b"\n", b"\r\n") if p in r["bat_lf"] else norm
        if new != b:
            with open(fp, "wb") as f:
                f.write(new)
            n += 1
            print("    교정 %-6s %s" % ("CRLF" if p in r["bat_lf"] else "LF", p))
    # 줄끝만 바뀐 파일은 `git diff` 는 비어 있는데 `status` 에 M 으로 남는다 — 인덱스 stat 만 갱신한다.
    for e in _git(repo, "status", "--porcelain", "-z", "-uno").decode("utf-8").split("\0"):
        if e[:2] == " M" and not _git(repo, "diff", "--", e[3:]).strip():
            _git(repo, "add", "--", e[3:])
    return n


def fix_bom(repo, r):
    for p in r["ps1_nobom"]:
        fp = os.path.join(repo, p)
        with open(fp, "rb") as f:
            b = f.read()
        with open(fp, "wb") as f:
            f.write(BOM + b)
        print("    BOM 추가 %s  (커밋 필요)" % p)
    return len(r["ps1_nobom"])


def _report(r):
    name = os.path.basename(r["repo"]) or r["repo"]
    bad = len(r["bat_lf"]) + len(r["mixed"]) + len(r["ps1_nobom"]) + r["mount_noise"]
    print("%-22s %s gattr=%s bat_lf=%d mixed=%d ps1_nobom=%d mount_noise=%d" % (
        name, "OK  " if bad == 0 and r["gattr"] else "WARN", "Y" if r["gattr"] else "-",
        len(r["bat_lf"]), len(r["mixed"]), len(r["ps1_nobom"]), r["mount_noise"]))
    for k in ("bat_lf", "mixed", "ps1_nobom"):
        for p in r[k]:
            print("    %-9s %s" % (k, p))
    return bad or (0 if r["gattr"] else 1)


def main(argv=None):
    _ensure_utf8_console()
    ap = argparse.ArgumentParser(description="줄끝·BOM 진단/교정 (기본: 진단만)")
    ap.add_argument("--repo", action="append", default=[])
    ap.add_argument("--all", action="store_true", help="--scan-root 아래 형제 저장소 전수")
    ap.add_argument("--scan-root", default=DEFAULT_SCAN_ROOT)
    ap.add_argument("--fix", action="store_true", help="작업 트리 줄끝 교정(.gitattributes 필요)")
    ap.add_argument("--fix-bom", action="store_true", help="한글 든 BOM 없는 UTF-8 .ps1 에 BOM 추가")
    a = ap.parse_args(argv)

    repos = [os.path.abspath(x) for x in a.repo]
    if a.all:
        for n in sorted(os.listdir(a.scan_root)):
            p = os.path.join(a.scan_root, n)
            if os.path.isdir(os.path.join(p, ".git")) and p not in repos:
                repos.append(p)
    if not repos:
        repos = [os.getcwd()]

    worst = 0
    for repo in repos:
        r = scan(repo)
        if a.fix and not r["gattr"] and (r["bat_lf"] or r["mixed"]):
            print("%s: .gitattributes 가 없어 --fix 를 건너뛴다 — 규칙부터 넣을 것" % repo)
        elif a.fix and (r["bat_lf"] or r["mixed"]):
            busy = running_scripts(repo)
            if busy is None:
                print("%s: 실행 중 스크립트 **미측정** — 교정 거부" % repo)
                return 1
            if busy:
                print("%s: 실행 중인 스크립트가 있어 교정 거부:\n  %s" % (repo, "\n  ".join(busy)))
                return 1
            fix(repo, r)
        if a.fix_bom and r["ps1_nobom"]:
            fix_bom(repo, r)
        if a.fix or a.fix_bom:
            r = scan(repo)
        worst = max(worst, 2 if _report(r) else 0)
    return worst


if __name__ == "__main__":
    sys.exit(main())
