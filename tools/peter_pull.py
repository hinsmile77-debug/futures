# -*- coding: utf-8 -*-
"""피터 사료를 `peter-feed` 브랜치에서 받아 이 PC 의 DB 를 다시 만든다 (MW0602 용).

왜 필요한가
    git 은 우체국이 아니라 **사서함**이다. MW0601 이 푸시해도 이 PC 의 작업 폴더는
    그대로다. 그리고 파일이 와도 미륵이 차트가 읽는 것은 `peter_levels.db` 이지
    `_lv/_tr` 텍스트가 아니다 — **받는 것과 반영하는 것은 다른 일이다.**
    이 스크립트가 그 둘을 한 번에 한다.

무엇을 건드리나
    `data/peter_feed/` **만**. 코드 브랜치·작업본·인덱스의 다른 경로는 안 건드린다.
    🔴 `peter_levels.db` 와 `offset` 은 **받지 않는다.** 오프셋은 「내 계약 − 정규
      10100」이라 PC 의 속성이다. 옮기면 조용히 틀린 가격을 그린다(596차).
      받은 텍스트로 **이 PC 의 캔들을 다시 재서** 자기 DB 를 만든다.

덮어쓰기 전에
    지난번에 받은 커밋(`data/peter_feed/.pulled`)의 내용과 지금 작업본을 대조해
    **이 PC 에서 손댄 파일을 찾아낸다.** 있으면 `_local_backup_<시각>/` 로 옮겨
    두고 로그에 적는다 — 말없이 지우지 않는다.

실행
    python tools/peter_pull.py              # fetch → 받기 → DB 재생성
    python tools/peter_pull.py --dry        # 무엇이 바뀔지만 보여준다
    python tools/peter_pull.py --no-fetch   # 이미 fetch 했을 때
    python tools/peter_pull.py --no-rebuild # 파일만 받고 DB 는 그대로
"""
import argparse
import datetime
import io
import os
import shutil
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBDIR = 'data/peter_feed'
REMOTE = 'origin'
BRANCH = 'peter-feed'
MARK = os.path.join(_ROOT, SUBDIR, '.pulled')


def git(*args, **kw):
    """git 호출. 🔴 core.autocrlf=true — Windows 쪽과 같은 눈으로 본다."""
    cmd = ['git', '--no-optional-locks', '-c', 'core.autocrlf=true'] + list(args)
    p = subprocess.Popen(cmd, cwd=_ROOT, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if kw.get('check') and p.returncode:
        raise SystemExit('git %s 실패(%d): %s'
                         % (' '.join(args), p.returncode,
                            err.decode('utf-8', 'replace').strip()))
    return p.returncode, out.decode('utf-8', 'replace'), err.decode('utf-8', 'replace')


def _norm(s):
    """개행만 맞춘다 — CRLF/LF 차이를 「내용이 달라졌다」로 읽지 않기 위해서다."""
    return (s or '').replace('\r\n', '\n').replace('\r', '\n')


def _blob(ref, path):
    rc, out, _ = git('show', '%s:%s' % (ref, path))
    return None if rc else out


def _tree(ref):
    """{경로: 블롭sha} — 그 커밋이 들고 있는 사료 목록."""
    rc, out, err = git('ls-tree', '-r', ref, '--', SUBDIR)
    if rc:
        return None
    t = {}
    for ln in out.splitlines():
        if not ln.strip():
            continue
        meta, path = ln.split('\t', 1)
        t[path.strip()] = meta.split()[2]
    return t


def _in_progress():
    g = os.path.join(_ROOT, '.git')
    for n in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply'):
        if os.path.exists(os.path.join(g, n)):
            return n
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--no-fetch', action='store_true')
    ap.add_argument('--no-rebuild', action='store_true')
    a = ap.parse_args()

    stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('[peter_pull] %s  repo=%s' % (stamp, _ROOT))

    # ── [603차 후속4] 받기 전에 죽은 잠금·부스러기부터 치운다 ────────────
    #   git 은 임시파일을 만들고 **지우면서** 끝난다. 코웍 마운트는 그 unlink 를
    #   막으므로(EPERM) 정상 동작이 쓰레기를 남긴다 — 2026-09-23 에 잠금 3개와
    #   tmp_obj 40개가 쌓여 있었다. 삭제가 되는 쪽(Windows)에서 도는 이 스크립트가
    #   매일 치운다. 🔴 3중 조건을 통과한 것만 지운다 — 도는 git 은 안 건드린다.
    hy = os.path.join(_ROOT, 'scripts', 'git_lock_guard.py')
    if os.path.exists(hy):
        q = subprocess.Popen([sys.executable, hy, '--reclaim'], cwd=_ROOT,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        o = q.communicate()[0].decode('utf-8', 'replace').strip()
        for ln in o.splitlines():
            print('  [위생] ' + ln)

    busy = _in_progress()
    if busy:
        raise SystemExit('중단: 저장소가 %s 진행 중이다 — 끝내고 다시 돌린다.' % busy)

    if not a.no_fetch:
        rc, _, err = git('fetch', REMOTE, BRANCH)
        if rc:
            raise SystemExit('중단: fetch 실패 — %s' % err.strip())
        print('  fetch %s/%s' % (REMOTE, BRANCH))

    ref = '%s/%s' % (REMOTE, BRANCH)
    new = _tree(ref)
    if not new:
        raise SystemExit('중단: %s 에 %s 가 없다.' % (ref, SUBDIR))
    _, head, _ = git('rev-parse', ref)
    head = head.strip()

    prev = ''
    if os.path.exists(MARK):
        prev = _norm(io.open(MARK, encoding='utf-8').read()).strip()
    if prev == head and not a.dry:
        print('  이미 최신이다 (%s) — 파일은 건드리지 않는다.' % head[:9])
    old = _tree(prev) if prev else None
    if prev and old is None:
        print('  ⚠ 지난 커밋 %s 를 못 읽는다 — 로컬 수정 판별을 건너뛴다.' % prev[:9])

    # ── 이 PC 에서 손댄 파일 찾기 ───────────────────────────────────────
    #   「지난번에 받은 내용」과 지금 작업본이 다르면 이 PC 가 고친 것이다.
    #   기준이 없으면(첫 실행) 판별할 수 없으므로 **건드리지 않고 남겨 둔다.**
    local = []
    if old:
        for path, sha in old.items():
            f = os.path.join(_ROOT, path.replace('/', os.sep))
            if not os.path.exists(f):
                continue
            cur = _norm(io.open(f, encoding='utf-8', errors='replace').read())
            was = _norm(_blob(prev, path))
            if was is not None and cur != was:
                local.append(path)

    changed = [p for p, sha in new.items()
               if not os.path.exists(os.path.join(_ROOT, p.replace('/', os.sep)))
               or _norm(io.open(os.path.join(_ROOT, p.replace('/', os.sep)),
                                encoding='utf-8', errors='replace').read())
               != _norm(_blob(ref, p) or '')]

    print('  %s 파일 %d개 · 이번에 바뀌는 것 %d개 · 이 PC 로컬 수정 %d개'
          % (ref, len(new), len(changed), len(local)))
    for p in changed[:12]:
        print('     + %s' % p)
    if len(changed) > 12:
        print('     + ... 외 %d개' % (len(changed) - 12))
    for p in local:
        print('     ! 로컬 수정: %s' % p)

    if a.dry:
        print('  [dry] 받지 않았다.')
        return 0
    if not changed and prev == head:
        if not a.no_rebuild:
            return _rebuild()
        return 0

    # ── 로컬 수정본은 지우지 않고 옮겨 둔다 ─────────────────────────────
    if local:
        bdir = os.path.join(_ROOT, SUBDIR, '_local_backup_%s'
                            % datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        os.makedirs(bdir)
        for p in local:
            shutil.copy2(os.path.join(_ROOT, p.replace('/', os.sep)),
                         os.path.join(bdir, os.path.basename(p)))
        print('  로컬 수정본 %d개를 보관했다 -> %s'
              % (len(local), os.path.relpath(bdir, _ROOT)))

    # ── 받기 — 이 폴더만. 인덱스에는 남기지 않는다 ──────────────────────
    #   checkout 은 경로를 인덱스에 얹는다. 그대로 두면 다음 커밋에 사료가
    #   섞여 들어간다 — 602차 후속에서 코드와 사료의 길을 나눈 이유가 그거다.
    git('checkout', ref, '--', SUBDIR, check=True)
    git('reset', '-q', '--', SUBDIR)
    io.open(MARK, 'w', encoding='utf-8').write(head + '\n')
    print('  받음: %s (%s)' % (head[:9], SUBDIR))

    if a.no_rebuild:
        print('  [--no-rebuild] DB 는 그대로다 — 차트에는 아직 안 뜬다.')
        return 0
    return _rebuild()


def _rebuild():
    """받은 텍스트로 **이 PC 의 캔들을 다시 재서** DB 를 만든다."""
    print('  DB 재생성 — 오프셋은 이 PC 의 캔들로 다시 잰다')
    p = subprocess.Popen([sys.executable, os.path.join('tools', 'peter_build_day.py'),
                          '--rebuild-all'], cwd=_ROOT)
    p.communicate()
    if p.returncode:
        print('  ⚠ 재생성이 %d 로 끝났다 — 위 출력에서 건너뛴 날을 확인한다.'
              % p.returncode)
    return p.returncode


if __name__ == '__main__':
    sys.exit(main() or 0)
