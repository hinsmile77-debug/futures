# -*- coding: utf-8 -*-
"""보관한 원본 -> 그날의 사료(① 지시 원문)와 오프셋 -> peter_paste 적재.

이 스크립트가 하는 일은 **옮겨 적기와 재기**뿐이다.
    ⛔ 레벨을 만들지 않는다 — 그가 쓴 숫자를 옮길 뿐이다(§6-1).
    ⛔ 거래(② `_tr.txt`)를 **자동으로 채우지 않는다.** 체결 시각이 트윗에 없는 날이
      있다(실측 08-04). 없는 시각을 지어내면 화면이 조용히 거짓말을 한다 —
      비워 두고 사람에게 알린다(계측 4원칙 ②: 미측정 != 0건).
    ⛔ 오프셋을 추정하지 않는다. 그 PC 의 캔들로 **오전 창 실측**만 한다(596차).
      못 재면 저장하지 않고 이유를 말한다.

① `_lv.txt` 초안은 원본에서 **매매로 읽히는 트윗만** 골라 만든다. 잡담까지 넣으면
   미분류가 화면 상태줄을 덮는다. 고르는 기준은 아래 `LOOKS_TRADE` 하나뿐이고,
   빠뜨린 것은 `_raw` 에 그대로 남아 있으므로 **잃는 것은 없다.**

실행
    python tools/peter_build_day.py --date 2026-09-17            # 초안+적재
    python tools/peter_build_day.py --date 2026-09-17 --dry      # 저장 안 함
    python tools/peter_build_day.py --rebuild-all                # 전 기간 DB 재생성
"""
import argparse
import datetime
import io
import json
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.join(_ROOT, 'tools')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import peter_capture as pc                                        # noqa: E402
import peter_feed as pf                                           # noqa: E402

FEED_DIR = os.path.join(_ROOT, 'data', 'peter_feed')
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# 매매로 읽히는 트윗 — 숫자(3~4자리)나 매매 낱말이 있으면 가져온다.
#   넓게 잡는다: 빠뜨리면 화면에서 사라지지만, 넘치면 미분류로 남을 뿐이다.
LOOKS_TRADE = re.compile(r'\d{3,4}|매수|매도|손절|청산|체결|돌파|맥점|익절|목표|이탈')


def stamp(date, hhmm):
    y, m, d = [int(x) for x in date.split('-')]
    h, mi = [int(x) for x in hhmm.split(':')]
    ap = 'AM' if h < 12 else 'PM'
    h12 = h if 1 <= h <= 12 else (h - 12 if h > 12 else 12)
    return '%d:%02d %s · %s %d, %d' % (h12, mi, ap, MON[m - 1], d, y)


def build_lv(date):
    """원본 -> ① 지시 원문 초안. (텍스트, 고른수, 전체수)"""
    have, existed = pc.load(date)
    if not existed:
        return None, 0, 0
    rows = sorted(have.values(), key=lambda r: r.get('dt') or '')
    out, kept = [], 0
    for r in rows:
        txt = (r.get('text') or '').strip()
        if not txt or not LOOKS_TRADE.search(txt):
            continue
        # 🔴 트윗 **본문 안의 빈 줄**은 접는다. 파서는 빈 줄에서 블록을 닫으므로
        #   그대로 두면 한 트윗이 두 덩이로 쪼개지고 앞 덩이가 시각을 잃는다
        #   (실측 09-16 08:58).
        body = ' '.join(x.strip() for x in txt.splitlines() if x.strip())
        out.append('%s\n%s\n' % (body, stamp(date, pc.kst(r.get('dt') or ''))))
        kept += 1
    return '\n'.join(out), kept, len(rows)


def save_day(date, dry=False, force=False):
    lv, kept, total = build_lv(date)
    if lv is None:
        print('%s  원본 없음 — tools/peter_capture.py 로 먼저 받아 적어라.' % date)
        return False
    if kept == 0:
        print('%s  원본 %d건 중 매매로 읽히는 트윗 0건 — 매매 없는 날로 본다.' % (date, total))
        return False

    lv_p = os.path.join(FEED_DIR, '%s_lv.txt' % date)
    tr_p = os.path.join(FEED_DIR, '%s_tr.txt' % date)
    if os.path.exists(lv_p) and not force and not dry:
        # 사람이 손본 사료를 말없이 덮지 않는다.
        cur = io.open(lv_p, encoding='utf-8').read()
        if cur.strip() != lv.strip():
            print('%s  ⚠ 기존 _lv.txt 와 다르다 — 덮지 않았다. 확인 후 --force.' % date)
            return False

    # 오프셋 — 그 PC 의 캔들로 오전 창 실측. 못 재면 저장하지 않는다.
    try:
        from dashboard.main_dashboard import peter_offset_measure   # noqa
        import sqlite3
        cand = []
        with sqlite3.connect('file:%s?mode=ro' % os.path.join(
                _ROOT, 'data', 'db', 'raw_data.db').replace('\\', '/'), uri=True) as c:
            cand = [{'ts': r[0], 'close': r[1]} for r in
                    c.execute("SELECT ts, close FROM raw_candles WHERE ts LIKE ?", (date + '%',))]
        off, n, why, info = peter_offset_measure(date, cand)
    except Exception as e:                                          # PyQt 없는 환경
        off, n, why, info = _offset_fallback(date)
    if off is None:
        print('%s  ⚠ 오프셋 실측 불가: %s — 저장하지 않았다.' % (date, why))
        return False

    if not os.path.exists(tr_p) and not dry:
        io.open(tr_p, 'w', encoding='utf-8').write('')
    tr = io.open(tr_p, encoding='utf-8').read() if os.path.exists(tr_p) else ''

    print('%s  트윗 %d건 중 %d건 채택 · 오프셋 %+.2f (오전 %d봉)%s'
          % (date, total, kept, off, n,
             ('  · 전일정 %+.2f' % info['full']) if info.get('full') is not None else ''))
    P = pf._load_parsers()
    s = pf.verify(date, off, lv, tr, P)
    if not tr.strip():
        print('  ⚠ 거래(②) 비어 있음 — 체결 시각을 사람이 넣어야 한다: %s'
              % os.path.relpath(tr_p, _ROOT))
    if dry:
        print('  [dry] 저장하지 않았다.')
        return True
    io.open(lv_p, 'w', encoding='utf-8').write(lv)
    pf.db_save(date, off, lv, tr)
    print('  저장 완료 -> peter_paste(%s)' % date)
    return True


def _offset_fallback(date):
    """PyQt 없는 환경용 — 같은 식(오전 09:00~11:30 중앙값)을 그대로 쓴다."""
    import sqlite3
    def med(v):
        v = sorted(v); n = len(v)
        return None if not n else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0)
    info = {'full': None, 'n_full': 0, 'lo': None, 'hi': None, 'window': '09:00–11:30'}
    db = os.path.join(_ROOT, 'data', 'db')
    try:
        rc = sqlite3.connect('file:%s?mode=ro' % os.path.join(db, 'regular_candles.db').replace('\\', '/'), uri=True)
        rd = sqlite3.connect('file:%s?mode=ro' % os.path.join(db, 'raw_data.db').replace('\\', '/'), uri=True)
    except Exception:
        return None, 0, 'DB 열기 실패', info
    reg = {r[0][:16]: r[1] for r in rc.execute(
        "SELECT ts,close FROM regular_candles WHERE code='10100' AND trade_date=?", (date,)) if r[1] is not None}
    if not reg:
        return None, 0, '정규 10100 미수집 — scripts/collect_regular_futures.py --today', info
    raw = {r[0][:16]: r[1] for r in rd.execute(
        "SELECT ts,close FROM raw_candles WHERE ts LIKE ?", (date + '%',)) if r[1] is not None}
    pairs = [(k, raw[k] - reg[k]) for k in raw if k in reg]
    if not pairs:
        return None, 0, '겹치는 분봉 없음', info
    full = [v for _, v in pairs]
    info['n_full'] = len(full); info['full'] = round(med(full), 2)
    am = [v for k, v in pairs if '09:00' <= k[11:16] < '11:30']
    if len(am) < 30:
        return None, len(am), '오전 겹치는 분봉 %d개 — 너무 적다' % len(am), info
    return round(med(am), 2), len(am), '', info


def rebuild_all():
    """`_lv/_tr` 텍스트만으로 DB 를 통째로 다시 만든다 — MW0602 합류용.

    🔴 오프셋은 **가져오지 않는다.** 이 PC 의 캔들로 다시 잰다(596차).
    """
    import glob
    ok = skip = 0
    for f in sorted(glob.glob(os.path.join(FEED_DIR, '*_lv.txt'))):
        d = os.path.basename(f)[:10]
        lv = io.open(f, encoding='utf-8').read()
        trf = f.replace('_lv.txt', '_tr.txt')
        tr = io.open(trf, encoding='utf-8').read() if os.path.exists(trf) else ''
        off, n, why, _ = _offset_fallback(d)
        if off is None:
            print('%s  건너뜀 — %s' % (d, why)); skip += 1; continue
        pf.db_save(d, off, lv, tr)
        print('%s  오프셋 %+.2f (오전 %d봉)' % (d, off, n)); ok += 1
    print('\n재생성 %d일 · 건너뜀 %d일' % (ok, skip))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date')
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--rebuild-all', action='store_true')
    a = ap.parse_args()
    if a.rebuild_all:
        rebuild_all(); return
    if not a.date:
        raise SystemExit('--date 또는 --rebuild-all')
    save_day(a.date, dry=a.dry, force=a.force)


if __name__ == '__main__':
    main()
