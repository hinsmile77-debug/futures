# -*- coding: utf-8 -*-
"""피터 트윗 원본 보관 — 받아 적기만 한다.

왜 있나
    그는 트윗을 **지운다**(본인 표현: "지금은 지웠음"). 실측 2026-08: 13 매매일 중
    08-18 장중 전체와 08-11 10:17 이전이 X 에서 사라졌다 — 둘 다 손실이 컸던 날이다.
    장 마감 후에만 긁으면 그 날들은 **영구히 못 건진다.**
    그래서 본 적 있는 트윗을 id 기준으로 여기에 append 해 둔다. 지워져도 남는다.

무엇을 하지 않나
    ⛔ **해석하지 않는다.** 레벨도 거래도 여기서 뽑지 않는다 — 받아 적기다.
    ⛔ **미륵이 DB 를 건드리지 않는다.** 장중에 도는 것이 전제라 append-only 파일만
      쓴다(마흐디 배치의 "미륵 장중 스캔 금지" 규약과 같은 선).
    ⛔ 같은 id 를 두 번 쓰지 않는다 — 몇 번을 돌려도 결과가 같다(멱등).

입력
    Claude 가 브라우저에서 긁은 배열을 stdin 또는 --json 으로 준다:
      [{"id": "...", "dt": "2026-09-17T00:06:00.000Z", "text": "..."}]
    `dt` 는 X 가 주는 UTC ISO 문자열 그대로. KST 변환은 읽는 쪽이 한다.

실행
    python tools/peter_capture.py --date 2026-09-17 < tweets.json
    python tools/peter_capture.py --date 2026-09-17 --stats
"""
import argparse
import datetime
import io
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(_ROOT, 'data', 'peter_feed', '_raw')


def raw_path(date):
    return os.path.join(RAW_DIR, '%s.jsonl' % date)


def load(date):
    """{id: rec}. 파일이 없으면 빈 것 — 「없음」이지 「0건 확인」이 아니다."""
    p = raw_path(date)
    out = {}
    if not os.path.exists(p):
        return out, False
    with io.open(p, encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get('id'):
                out[r['id']] = r
    return out, True


def append(date, tweets):
    """새 id 만 덧붙인다. (추가수, 중복수, 총계)"""
    have, _ = load(date)
    now = datetime.datetime.now().isoformat(timespec='seconds')
    new, dup = [], 0
    for t in tweets:
        tid = str(t.get('id') or '').strip()
        if not tid:
            continue
        if tid in have:
            dup += 1
            continue
        new.append({'id': tid, 'dt': t.get('dt'), 'text': t.get('text') or '',
                    'seen_at': now})
        have[tid] = new[-1]
    if new:
        if not os.path.isdir(RAW_DIR):
            os.makedirs(RAW_DIR)
        with io.open(raw_path(date), 'a', encoding='utf-8') as f:
            for r in new:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return len(new), dup, len(have)


def kst(dt_iso):
    try:
        t = datetime.datetime.strptime(dt_iso[:19], '%Y-%m-%dT%H:%M:%S')
        return (t + datetime.timedelta(hours=9)).strftime('%H:%M')
    except Exception:
        return '--:--'


def stats(date):
    have, existed = load(date)
    if not existed:
        print('%s  파일 없음 — 아직 한 번도 캡처하지 않았다(0건과 다르다).' % date)
        return
    rows = sorted(have.values(), key=lambda r: r.get('dt') or '')
    print('%s  %d건  %s ~ %s' % (date, len(rows),
                                 kst(rows[0].get('dt') or '') if rows else '--:--',
                                 kst(rows[-1].get('dt') or '') if rows else '--:--'))
    for r in rows:
        print('  %s  %s' % (kst(r.get('dt') or ''),
                            (r.get('text') or '').replace('\n', ' / ')[:90]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', required=True, help='YYYY-MM-DD (KST 기준 장 날짜)')
    ap.add_argument('--json', help='트윗 배열 파일. 없으면 stdin')
    ap.add_argument('--stats', action='store_true')
    a = ap.parse_args()
    if a.stats:
        stats(a.date)
        return
    src = io.open(a.json, encoding='utf-8').read() if a.json else sys.stdin.read()
    try:
        tweets = json.loads(src)
    except ValueError as e:
        raise SystemExit('입력이 JSON 배열이 아니다: %s' % e)
    if not isinstance(tweets, list):
        raise SystemExit('입력은 배열이어야 한다.')
    n, dup, total = append(a.date, tweets)
    print('%s  신규 %d · 중복 %d · 누적 %d  -> %s'
          % (a.date, n, dup, total, os.path.relpath(raw_path(a.date), _ROOT)))


if __name__ == '__main__':
    main()
