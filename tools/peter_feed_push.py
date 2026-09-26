# -*- coding: utf-8 -*-
"""피터 사료를 `peter-feed` 브랜치에 올린다 — **코드 브랜치를 건드리지 않고.**

왜 별도 브랜치인가
    두 PC 의 코드 브랜치가 다르다(MW0601=v9-dev · MW0602=dev). 사료는 **매일**
    쌓이는데 그것을 코드 브랜치에 실어 나르면 CLAUDE.md 가 요구하는 체리픽 기록
    (원 커밋 sha·원 PC·가져온 이유)이 **사료 체리픽으로 뒤덮인다.**
    사료는 코드와 다른 길로 보낸다.

왜 고아(orphan) 브랜치인가
    부모가 코드 히스토리에 닿아 있으면 실수로 머지했을 때 코드가 건너간다.
    이 브랜치는 `data/peter_feed/` 만 들고 코드 이력과 **한 점도 닿지 않는다.**

무엇을 올리나
    `data/peter_feed/**` 만. 🔴 `peter_levels.db` 와 `offset` 은 **올리지 않는다** —
    「내 계약과의 차이」라 PC 의 속성이다. 옮기면 받는 쪽이 조용히 틀린 가격을
    그린다(596차). 받는 쪽은 이 텍스트로 자기 DB 를 만든다:
        python tools/peter_build_day.py --rebuild-all

어떻게
    체크아웃을 **바꾸지 않는다.** 임시 인덱스에 그 폴더만 담아 트리를 만들고
    (`write-tree`), 그 트리로 커밋을 떠서(`commit-tree`) ref 를 옮긴다.
    작업 중이던 브랜치·작업본은 그대로다.

실행
    python tools/peter_feed_push.py            # 로컬 브랜치만 갱신
    python tools/peter_feed_push.py --push     # origin 에도 올린다
"""
import argparse
import datetime
import os
import subprocess
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH = 'peter-feed'
SUBDIR = 'data/peter_feed'


def git(*args, **kw):
    env = dict(os.environ)
    env.update(kw.pop('env', {}))
    # 🔴 마운트 경유에서 CRLF/LF 가 엇갈리지 않게 Windows 쪽과 같은 눈으로 본다.
    cmd = ['git', '--no-optional-locks', '-c', 'core.autocrlf=true'] + list(args)
    p = subprocess.Popen(cmd, cwd=_ROOT, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out.decode('utf-8', 'replace').strip(), err.decode('utf-8', 'replace')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--push', action='store_true')
    ap.add_argument('--remote', default='origin')
    a = ap.parse_args()

    if not os.path.isdir(os.path.join(_ROOT, SUBDIR)):
        raise SystemExit('%s 가 없다 — 올릴 사료가 없다.' % SUBDIR)

    fd, idx = tempfile.mkstemp(prefix='peterfeed-idx-')
    os.close(fd); os.remove(idx)                      # git 이 새로 만들게 둔다
    env = {'GIT_INDEX_FILE': idx}
    try:
        # [MW0601 631차] -f: data/peter_feed/ 는 .gitignore 로 무시된다(코드 브랜치 미추적 목록 정리).
        # -f 가 없으면 무시된 파일이 빠져 빈 트리가 올라가고 원격 사료가 통째로 지워진다.
        rc, _, err = git('add', '-A', '-f', '--', SUBDIR, env=env)
        if rc:
            raise SystemExit('인덱스 구성 실패: %s' % err)
        rc, tree, err = git('write-tree', env=env)
        if rc:
            raise SystemExit('트리 생성 실패: %s' % err)
    finally:
        if os.path.exists(idx):
            os.remove(idx)

    rc, parent, _ = git('rev-parse', '--verify', '--quiet', 'refs/heads/%s' % BRANCH)
    parent = parent if rc == 0 and parent else None

    if parent:
        rc, ptree, _ = git('rev-parse', '%s^{tree}' % parent)
        if rc == 0 and ptree == tree:
            print('변경 없음 — 새 커밋을 만들지 않았다.')
            if not _maybe_push(a, parent):
                raise SystemExit(1)
            return

    n = len([f for f in os.listdir(os.path.join(_ROOT, SUBDIR))
             if f.endswith('.txt')])
    msg = ('[peter-feed] 사료 갱신 %s (lv/tr %d파일)\n\n'
           'data/peter_feed/ 만 담은 고아 브랜치다. 코드 이력과 닿지 않는다.\n'
           'peter_levels.db 와 offset 은 PC 의 속성이라 올리지 않는다 — 받는 쪽은\n'
           '`python tools/peter_build_day.py --rebuild-all` 로 자기 DB 를 만든다.'
           % (datetime.date.today().isoformat(), n))
    args = ['commit-tree', tree, '-m', msg] + (['-p', parent] if parent else [])
    rc, commit, err = git(*args)
    if rc:
        raise SystemExit('커밋 생성 실패: %s' % err)
    rc, _, err = git('update-ref', 'refs/heads/%s' % BRANCH, commit,
                     *( [parent] if parent else [] ))
    if rc:
        raise SystemExit('ref 갱신 실패: %s' % err)
    print('%s %s  (%s)' % (BRANCH, commit[:9], '갱신' if parent else '새로 만듦'))
    if not _maybe_push(a, commit):
        raise SystemExit(1)


def _maybe_push(a, commit):
    """올린다. **성공하면 True.**

    🔴 예전에는 실패해도 메시지만 찍고 0 으로 끝났다. 그러면 작업 스케줄러가
      「성공」으로 기록하고, 로컬 ref 만 앞서 간 채 MW0602 는 어제에 멈춘다 —
      아무도 에러를 못 보는 종류의 고장이다. 그래서 실패는 종료코드로 낸다.
    """
    if not a.push:
        print('로컬만 갱신했다. 올리려면 --push (또는 `git push %s %s`).' % (a.remote, BRANCH))
        return True
    rc, out, err = git('push', a.remote, '%s:refs/heads/%s' % (BRANCH, BRANCH))
    if rc:
        e = err.strip()
        print('푸시 실패 — Windows 에서 `git push %s %s` 로 올려라.\n%s'
              % (a.remote, BRANCH, e[:400]))
        if 'could not read Username' in e or 'Authentication failed' in e:
            print('  ↑ 자격증명이 없는 환경이다(Cowork 마운트 등). 푸시는 Windows 가 한다:')
            print('    scripts\\peter_feed_push_MW0601.bat  (작업 「피터 사료 송신」)')
        return False
    # 올라간 것을 origin 에 되물어 확인한다 — 「푸시 완료」를 믿지 않는다.
    rc, ls, _ = git('ls-remote', a.remote, 'refs/heads/%s' % BRANCH)
    remote_sha = ls.split()[0] if rc == 0 and ls.strip() else '?'
    if remote_sha != commit:
        print('푸시했다는데 origin 이 %s 다 (로컬 %s) — 확인이 필요하다.'
              % (remote_sha[:9], commit[:9]))
        return False
    print('푸시 완료 -> %s/%s @ %s' % (a.remote, BRANCH, remote_sha[:9]))
    return True


if __name__ == '__main__':
    main()
