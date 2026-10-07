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

종료코드
    0  정상        2  오늘 사료가 오지 않았다(공급 측 문제)   그 외  재생성 실패
    🔴 「재생성 N일 · 건너뜀 0일」은 **어제까지의 성공을 세는 것**이다 — 오늘이
      왔는지는 말해 주지 않는다. 2026-09-21 에 MW0601 이 푸시를 빠뜨렸을 때
      이 스크립트는 rc=0 으로 끝났고, 사람이 차트를 보고서야 알았다.
      그래서 마지막에 당일 도착을 따로 확인하고 rc=2 로 경보한다.

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


def _run():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--no-fetch', action='store_true')
    ap.add_argument('--no-rebuild', action='store_true')
    a = ap.parse_args()

    stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('[peter_pull] %s  repo=%s' % (stamp, _ROOT))

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
            if _is_raw(path):
                continue            # [610차] 원본은 덮지 않고 병합한다 — _merge_raw 참조
            f = os.path.join(_ROOT, path.replace('/', os.sep))
            if not os.path.exists(f):
                continue
            cur = _norm(io.open(f, encoding='utf-8', errors='replace').read())
            was = _norm(_blob(prev, path))
            if was is not None and cur != was:
                local.append(path)

    # [610차] 원본(_raw/*.jsonl)은 「바뀌는 것」에서 뺀다 — 이 PC 의 실시간 수집분이 섞여
    #   받은 것과 다른 게 정상이고, 덮지 않고 _merge_raw 로 합친다.
    changed = [p for p, sha in new.items()
               if not _is_raw(p) and (
               not os.path.exists(os.path.join(_ROOT, p.replace('/', os.sep)))
               or _norm(io.open(os.path.join(_ROOT, p.replace('/', os.sep)),
                                encoding='utf-8', errors='replace').read())
               != _norm(_blob(ref, p) or ''))]

    print('  %s 파일 %d개 · 이번에 바뀌는 것 %d개 · 이 PC 로컬 수정 %d개'
          % (ref, len(new), len(changed), len(local)))
    for p in changed[:12]:
        print('     + %s' % p)
    if len(changed) > 12:
        print('     + ... 외 %d개' % (len(changed) - 12))
    for p in local:
        print('     ! 로컬 수정: %s' % p)

    if a.dry:
        _merge_raw(ref, new, _snapshot_raw(), dry=True)
        print('  [dry] 받지 않았다.')
        return 0
    snap = _snapshot_raw()          # [610차] checkout 이 덮기 전에 이 PC 의 원본을 잡아 둔다
    if not changed and prev == head:
        _merge_raw(ref, new, snap)
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
    _merge_raw(ref, new, snap)      # checkout 이 덮은 원본을 이 PC 기록 + 받은 신규분으로 되돌린다

    if a.no_rebuild:
        print('  [--no-rebuild] DB 는 그대로다 — 차트에는 아직 안 뜬다.')
        return 0
    return _rebuild()


RAW_PREFIX = SUBDIR + '/_raw/'


def _is_raw(path):
    return path.startswith(RAW_PREFIX) and path.endswith('.jsonl')


def _snapshot_raw():
    """이 PC 의 `_raw/*.jsonl` 바이트 — {repo 상대경로: bytes}."""
    d = os.path.join(_ROOT, RAW_PREFIX.replace('/', os.sep))
    out = {}
    if os.path.isdir(d):
        for n in os.listdir(d):
            if n.endswith('.jsonl'):
                with io.open(os.path.join(d, n), 'rb') as f:
                    out[RAW_PREFIX + n] = f.read()
    return out


def _ids(blob_bytes):
    import json
    ids = set()
    for ln in blob_bytes.decode('utf-8', 'replace').splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if r.get('id'):
            ids.add(str(r['id']))
    return ids


def _merge_raw(ref, tree, snap, dry=False):
    """[MW0602 610차] 원본(`_raw/<날짜>.jsonl`)은 **덮지 않고 트윗 id 로 합친다.**

    🔴 왜: 피터2 수신기가 장중에 이 PC 의 `_raw` 에 `src=live`·`seen_at` 으로 적는다.
      종전처럼 checkout 으로 덮으면 그 파일은 「지난번에 받은 목록」에 없어 로컬 수정으로도
      안 잡히고 **백업 없이** MW0601 판으로 바뀐다 — 수신 지연(사전등록 ③)과 삭제 탐지의
      원천이 MW0601 수집기 값으로 조용히 바뀐다(계측 4원칙 ④).

    규칙
      · 이 PC 의 기록은 **바이트 그대로** 앞에 둔다(엔진 RawTail 의 바이트 오프셋 보존).
      · 받은 것 중 이 PC 에 없는 id 만 **뒤에 덧붙인다** — `src='pull'`, 원래 src 는
        `src_origin` 에 남긴다. peter2_eod 는 `src=='live'` 만 지연·삭제 계산에 쓰므로
        MW0601 이 본 것을 MW0602 가 본 것으로 세지 않는다.
      · 이 PC 에 파일이 없던 날(수집기 정지·도입 전)도 같은 규칙 — 전부 `src=pull`.
      · 멱등이다 — 이미 있는 id 는 다시 붙이지 않는다.
    """
    import json
    files = days = 0
    for path in sorted(p for p in tree if _is_raw(p)):
        pulled = _blob(ref, path)
        if pulled is None:
            continue
        mine = snap.get(path)
        have = _ids(mine) if mine else set()
        add = []
        for ln in pulled.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            rid = str(r.get('id') or '')
            if not rid or rid in have:
                continue
            have.add(rid)
            if r.get('src') != 'pull':
                r['src_origin'] = r.get('src')
                r['src'] = 'pull'
            add.append(json.dumps(r, ensure_ascii=False))
        f = os.path.join(_ROOT, path.replace('/', os.sep))
        base = mine if mine is not None else b''
        if base and not base.endswith(b'\n'):
            base += b'\n'
        body = base + (('\n'.join(add) + '\n').encode('utf-8') if add else b'')
        cur = io.open(f, 'rb').read() if os.path.exists(f) else None
        if cur == body:
            continue
        files += 1
        if add:
            days += 1
            print('     ~ 원본 병합 %s: 이 PC %d건 + 받은 신규 %d건(src=pull)'
                  % (os.path.basename(path), len(_ids(mine)) if mine else 0, len(add)))
        if not dry:
            with io.open(f, 'wb') as fp:
                fp.write(body)
    print('  원본 병합: %d개 파일 정리 · %d일에 신규 덧붙임%s'
          % (files, days, ' [dry]' if dry else ''))


def _self_build():
    """[MW0602 610차] 오늘 차트를 **이 PC 원본만으로도** 확정한다.

    받기(MW0601 공급)가 없거나 늦은 날에도 확정본이 생기게 하는 자체 경로다.
      1. `peter2_eod` — 일일 복기 md(삭제 탐지는 받은 eod_ids 반영) · `_tr.txt` 가 없으면 초안
      2. `peter_build_day --date 오늘` — `_lv` 초안 + **이 PC 캔들 오프셋 실측** → peter_paste
    🔴 MW0601 사료가 이미 왔으면 그쪽(사람이 검증한 `_lv`/`_tr`)이 이긴다 — build_day 는
      다른 `_lv` 를 덮지 않고, peter2_eod 는 있는 `_tr.txt` 를 덮지 않는다.
    🔴 도착 판정(_check_today) **뒤에** 돈다 — 자체로 만든 `_lv` 를 「MW0601 도착」으로
      읽지 않기 위해서다.
    """
    iso = datetime.date.today().isoformat()
    raw = os.path.join(_ROOT, RAW_PREFIX.replace('/', os.sep), '%s.jsonl' % iso)
    if not os.path.exists(raw):
        print('  자체 확정: 오늘 원본 없음 — 건너뜀(수집기 미가동 또는 휴장).')
        return
    for args in (['tools/peter2_eod.py', '--date', iso],
                 ['tools/peter_build_day.py', '--date', iso]):
        p = subprocess.Popen([sys.executable] + args, cwd=_ROOT)
        p.communicate()
        print('  자체 확정: %s rc=%s' % (os.path.basename(args[0]), p.returncode))


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


RC_STALE = 2


def _feed_lv():
    """받아놓은 _lv 목록 — [(날짜, 바이트수)] 오름차순."""
    d = os.path.join(_ROOT, SUBDIR.replace('/', os.sep))
    out = []
    if os.path.isdir(d):
        for n in os.listdir(d):
            if len(n) == 17 and n.endswith('_lv.txt'):
                out.append((n[:10], os.path.getsize(os.path.join(d, n))))
    return sorted(out)


def _bars(date):
    """이 PC 가 그날 캔들을 갖고 있나 — 휴장일에 헛경보를 울리지 않기 위해서다.
    못 재면 None 을 준다 — 미측정과 0 은 다르다(계측 4원칙 ②)."""
    import sqlite3
    f = os.path.join(_ROOT, 'data', 'db', 'raw_data.db')
    if not os.path.exists(f):
        return None
    try:
        with sqlite3.connect('file:%s?mode=ro' % f.replace(os.sep, '/'),
                             uri=True) as c:
            return c.execute('SELECT COUNT(*) FROM raw_candles WHERE ts LIKE ?',
                             (date + '%',)).fetchone()[0]
    except Exception:
        return None


def _check_today(rc):
    """오늘 사료가 왔나. 안 왔으면 rc=2 — 스케줄러 기록에 실패로 남긴다.

    넣은 이유는 수신기가 조용했기 때문이다. 공급이 며칠 끊겨도 로그는
    「재생성 34일 · 건너뜀 0일」로 건강해 보였다 — 없는 것을 정상으로 읽는 형태다.
    """
    today = datetime.date.today()
    iso = today.isoformat()
    lv = _feed_lv()
    size = dict(lv)
    last = lv[-1][0] if lv else None

    if iso in size:
        if size[iso] == 0:
            print('  오늘(%s) 사료 도착 — 다만 _lv 가 비어 있다(빈 사료).' % iso)
        else:
            print('  오늘(%s) 사료 도착.' % iso)
        return rc

    bars = _bars(iso)
    if bars == 0:
        print('  오늘(%s) 사료 없음 — 이 PC 캔들도 0봉이라 휴장으로 본다. 경보하지 않는다.'
              % iso)
        return rc

    gap = ''
    if last:
        try:
            y, m, d = [int(x) for x in last.split('-')]
            gap = ' (%d일 경과)' % (today - datetime.date(y, m, d)).days
        except ValueError:
            pass
    print('  [미도착] 오늘(%s) 사료가 오지 않았다 — 마지막 수신일 %s%s'
          % (iso, last or '없음', gap))
    if bars is None:
        print('     이 PC 캔들을 확인하지 못했다 — 휴장 여부는 판정 불가.'
              ' 미판정을 정상으로 삼키지 않는다.')
    else:
        print('     이 PC 캔들 %d봉 — 장은 섰는데 공급이 없다.' % bars)
    print('     확인: MW0601 에서 python tools/peter_feed_push.py --push')
    return rc or RC_STALE


def main():
    #  받기/재생성이 성공해도 「오늘이 왔는가」는 별개의 질문이다.
    rc = _check_today(_run() or 0)
    # [610차] 자체 확정은 rc 와 별개다 — 공급이 없었다는 사실(rc=2)은 그대로 남긴다.
    if '--dry' not in sys.argv:
        try:
            _self_build()
        except Exception as e:
            print('  ⚠ 자체 확정 실패: %s' % e)
    return rc


if __name__ == '__main__':
    sys.exit(main() or 0)
