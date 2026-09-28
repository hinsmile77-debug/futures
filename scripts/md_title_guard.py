# -*- coding: utf-8 -*-
"""[MW0601 636차 / 2026-09-28 고도화 방안 2] 미커밋 마크다운의 **제목 줄 손상** 경고.

## 왜 있는가

2026-09-28 장전 점검이 `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md`
의 1행이 이렇게 바뀐 채 미커밋으로 남아 있는 것을 **`git diff`를 직접 열어 보고서야**
찾았다(이상점 1-1):

    - # 재시작 종료사유 분류 · 봉 결손 대응 구현계획 — 2026-09-22 (MW0601)
    +
    + 시작 종료사유 분류 · 봉 결손 대응 구현계획 — 2026-09-22 (MW0601)

빈 줄이 끼고 `# 재` 세 글자가 사라졌다. 문서는 열리고 본문도 멀쩡해 아무 계측에도
안 걸린다 — 커밋되면 제목 없는 문서로 굳는다.

## 판정

HEAD 판의 첫 비어있지 않은 줄이 `# ` 로 시작했는데, 작업본의 첫 비어있지 않은 줄이
`#` 로 시작하지 않으면 **손상 의심**. 제목 **문구** 변경(`# A` -> `# B`)은 정상 편집이라
잡지 않는다 — 제목 **기호**가 사라진 경우만 본다.

## 쓰는 법 (커밋 전 프리플라이트 — `git_lock_guard.py --check` 옆에서)

    python scripts/md_title_guard.py
    python scripts/md_title_guard.py --json

종료코드: 0 의심 없음 · 2 의심 발견 · 1 실행 오류.
**아무것도 막거나 고치지 않는다** — 경고만 한다. 의도한 편집일 수 있으므로 되돌릴지는
사람이 정한다. git hook 이 아니다.

⚠ 모든 git 호출에 `--no-optional-locks` (읽기 전용이어도 인덱스를 다시 써 락을 남긴다).
⚠ py3.7 호환 · 의존성 없는 단일 파일.
"""

from __future__ import print_function

import argparse
import json
import os
import subprocess
import sys


def _first_nonblank(text):
    for line in text.splitlines():
        s = line.strip().lstrip(u"﻿")
        if s:
            return s
    return u""


def title_damaged(old_text, new_text):
    """HEAD 판에 있던 `# ` 제목 기호가 작업본에서 사라졌는가."""
    old = _first_nonblank(old_text)
    if not old.startswith(u"# "):
        return False
    new = _first_nonblank(new_text)
    if not new:
        return False  # 내용을 다 지운 것은 이 도구의 관할이 아니다
    return not new.startswith(u"#")


def _git(repo, args):
    p = subprocess.Popen(
        ["git", "--no-optional-locks", "-c", "core.quotepath=false"] + args,
        cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    out, err = p.communicate()
    if p.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (" ".join(args), p.returncode,
                                                err.decode("utf-8", "replace").strip()))
    return out.decode("utf-8", "replace")


def scan(repo):
    """(suspects, n_checked). suspects 는 {path, old, new} 목록."""
    names = [n for n in _git(repo, ["diff", "--name-only", "--diff-filter=M", "HEAD"]).splitlines()
             if n.lower().endswith(".md")]
    suspects = []
    for rel in names:
        try:
            old = _git(repo, ["show", "HEAD:" + rel])
        except RuntimeError:
            continue
        path = os.path.join(repo, rel)
        try:
            with open(path, "rb") as f:
                new = f.read().decode("utf-8", "replace")
        except (IOError, OSError):
            continue
        if title_damaged(old, new):
            suspects.append({"path": rel, "old": _first_nonblank(old), "new": _first_nonblank(new)})
    return suspects, len(names)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="미커밋 .md 의 제목 기호(# ) 손상 경고")
    ap.add_argument("--repo", default=os.getcwd())
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        suspects, n = scan(a.repo)
    except Exception as e:
        print("실행 오류: %s" % e, file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps({"checked": n, "suspects": suspects}, ensure_ascii=False, indent=2))
    else:
        print("변경된 .md %d개 검사 - 제목 손상 의심 %d개" % (n, len(suspects)))
        for s in suspects:
            print("  [!] %s" % s["path"])
            print("      HEAD : %s" % s["old"])
            print("      작업본: %s" % s["new"])
        if suspects:
            print("")
            print("의도한 편집이 아니면 `git checkout -- <경로>` 로 되돌린다. 이 도구는 고치지 않는다.")
    return 2 if suspects else 0


if __name__ == "__main__":
    sys.exit(main())
