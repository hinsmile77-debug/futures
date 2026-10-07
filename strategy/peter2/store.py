# -*- coding: utf-8 -*-
"""피터2 파일 입출력 — 경로·오프셋 조회·기록. 미륵이 라이브 DB 는 건드리지 않는다.

어디에 무엇이 남나
    data/peter_feed/_raw/<날짜>.jsonl          트윗 원본(append-only, 기존 사료 체계와 공유)
    data/peter2_live/<날짜>/collector.json      수집기 하트비트(수신기가 쓴다)
    data/peter2_live/<날짜>/signals.jsonl       해석·집행 이벤트 전부(기계용)
    data/peter2_live/<날짜>/state.json          재기동 생존 상태(집행한 지시 id·일일 카운터)
    data/peter2_live/<날짜>/feed.json           당일 1분봉 차트용 실시간 사료(① 지시 원문 · ② 거래줄)
    docs/미륵이고도화3/피터2/live/피터2_실시간_<PC>-<YYYYMMDD>.md   사람이 읽는 장중 기록

🔴 offset 은 「내 미니 계약 − 그의 일반선물」이라 **이 PC 의 속성**이다(596차).
   peter_levels.db 의 가장 최근 실측일 값을 쓴다 — 장중엔 정규 10100 이 없어서 그날 것을 못 잰다.
"""
import datetime
import io
import json
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(_ROOT, 'data', 'peter_feed', '_raw')
LIVE_DIR = os.path.join(_ROOT, 'data', 'peter2_live')
DOC_DIR = os.path.join(_ROOT, 'docs', '미륵이고도화3', '피터2')
PETER_DB = os.path.join(_ROOT, 'data', 'db', 'peter_levels.db')

KST = datetime.timezone(datetime.timedelta(hours=9))


def _pc():
    try:
        from utils.db_utils import pc_id
        return pc_id() or 'PC'
    except Exception:
        return 'PC'


def raw_path(date):
    return os.path.join(RAW_DIR, '%s.jsonl' % date)


def day_dir(date):
    d = os.path.join(LIVE_DIR, date)
    if not os.path.isdir(d):
        os.makedirs(d)
    return d


def doc_live_path(date):
    d = os.path.join(DOC_DIR, 'live')
    if not os.path.isdir(d):
        os.makedirs(d)
    return os.path.join(d, '피터2_실시간_%s-%s.md' % (_pc(), date.replace('-', '')))


def tweet_kst(dt_iso):
    """X 의 UTC ISO → KST datetime(naive). 실패 시 None."""
    try:
        t = datetime.datetime.strptime((dt_iso or '')[:19], '%Y-%m-%dT%H:%M:%S')
        return t + datetime.timedelta(hours=9)
    except Exception:
        return None


# ── 원본 읽기(증분) ─────────────────────────────────────────────
class RawTail(object):
    """`_raw/<날짜>.jsonl` 을 바이트 오프셋으로 따라 읽는다 — 새 줄만 돌려준다."""

    def __init__(self, date):
        self.date = date
        self.pos = 0

    def read_new(self):
        p = raw_path(self.date)
        if not os.path.exists(p):
            return []
        size = os.path.getsize(p)
        if size < self.pos:          # 파일이 바뀌었다(재생성) — 처음부터
            self.pos = 0
        if size == self.pos:
            return []
        out = []
        with io.open(p, 'rb') as f:
            f.seek(self.pos)
            chunk = f.read()
        # 마지막 줄이 쓰는 중일 수 있다 — 개행으로 끝난 데까지만 소비한다
        cut = chunk.rfind(b'\n')
        if cut < 0:
            return []
        self.pos += cut + 1
        for ln in chunk[:cut + 1].decode('utf-8', 'replace').splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get('id'):
                out.append(r)
        return out


# ── 오프셋 ────────────────────────────────────────────────────
def _second_thursday(y, m):
    d = datetime.date(y, m, 1)
    first_thu = d + datetime.timedelta(days=(3 - d.weekday()) % 7)
    return first_thu + datetime.timedelta(days=7)


def last_expiry_before(date_str):
    """date 보다 **앞선** 가장 최근 둘째 목요일(미니 월물·정규 분기물 만기)."""
    d = datetime.date.fromisoformat(date_str)
    y, m = d.year, d.month
    for _ in range(3):
        e = _second_thursday(y, m)
        if e < d:
            return e
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return None


def load_offset(date_str):
    """(offset, src, safe). 장중에는 그날 실측이 없으므로 **직전 실측일** 값을 쓴다.

    safe=False — 직전 실측일이 만기(둘째 목요일) 이전이다. 그 사이에 미니 월물 또는 정규
    분기물이 바뀌어 오프셋이 약 2pt 점프한다. 그 날은 진입을 막는다(섀도만).
    """
    try:
        if not os.path.exists(PETER_DB):
            return None, 'no_db', False
        con = sqlite3.connect('file:%s?mode=ro' % PETER_DB.replace('\\', '/'), uri=True)
        try:
            r = con.execute("SELECT date, offset FROM peter_paste WHERE date < ? "
                            "AND offset IS NOT NULL ORDER BY date DESC LIMIT 1",
                            (date_str,)).fetchone()
        finally:
            con.close()
        if not r:
            return None, 'no_row', False
        od, off = r[0], float(r[1])
        exp = last_expiry_before(date_str)
        safe = not (exp is not None and datetime.date.fromisoformat(od) <= exp)
        return off, 'prev_day:%s' % od, safe
    except Exception as e:
        return None, 'error:%s' % e, False


# ── 하트비트 ──────────────────────────────────────────────────
def collector_heartbeat(date):
    """(age_sec, info). 파일이 없으면 (None, None) — 「수집기 미기동」이지 「0초」가 아니다."""
    p = os.path.join(LIVE_DIR, date, 'collector.json')
    if not os.path.exists(p):
        return None, None
    try:
        with io.open(p, encoding='utf-8') as f:
            info = json.load(f)
        last = datetime.datetime.fromisoformat(info.get('last_post', '')[:19])
        return (datetime.datetime.now() - last).total_seconds(), info
    except Exception:
        return None, None


# ── 기록 ──────────────────────────────────────────────────────
def append_signal(date, rec):
    p = os.path.join(day_dir(date), 'signals.jsonl')
    rec = dict(rec)
    rec.setdefault('at', datetime.datetime.now().isoformat(timespec='seconds'))
    with io.open(p, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def read_signals(date):
    p = os.path.join(LIVE_DIR, date, 'signals.jsonl')
    out = []
    if not os.path.exists(p):
        return out
    with io.open(p, encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def _atomic_json(path, obj):
    tmp = path + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def load_state(date):
    p = os.path.join(LIVE_DIR, date, 'state.json')
    try:
        with io.open(p, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(date, state):
    _atomic_json(os.path.join(day_dir(date), 'state.json'), state)


def write_feed(date, feed):
    _atomic_json(os.path.join(day_dir(date), 'feed.json'), feed)


def load_feed(date):
    p = os.path.join(LIVE_DIR, date, 'feed.json')
    try:
        with io.open(p, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def append_doc(date, line):
    """사람이 읽는 장중 기록. 첫 줄이면 머리말을 단다."""
    p = doc_live_path(date)
    head = not os.path.exists(p)
    with io.open(p, 'a', encoding='utf-8') as f:
        if head:
            f.write('# 피터2 실시간 기록 — %s (%s)\n\n' % (date, _pc()))
            f.write('> 장중 자동 기록. 피터리 트윗 → 해석 → 집행의 순서 그대로 남긴다.\n'
                    '> 가격 표기: `피터가(정규)` → `미니가`(= 정규 + 오프셋). '
                    '장후 확정본은 `일일/피터2_일일_%s_%s.md`.\n\n'
                    % (_pc(), date.replace('-', '')))
            f.write('| 시각 | 구분 | 내용 |\n|---|---|---|\n')
        f.write(line.rstrip('\n') + '\n')


# ── 실시간 사료(차트용) ─────────────────────────────────────────
def build_live_lv(rows, date):
    """원본 → ① 지시 원문(피터 사료 형식). 장후 `peter_build_day.build_lv` 와 **같은 함수**를 쓴다."""
    tools = os.path.join(_ROOT, 'tools')
    if tools not in sys.path:
        sys.path.insert(0, tools)
    try:
        from peter_build_day import stamp, LOOKS_TRADE      # noqa
    except Exception:
        return ''
    out = []
    for r in sorted(rows, key=lambda x: x.get('dt') or ''):
        txt = (r.get('text') or '').strip()
        if not txt or not LOOKS_TRADE.search(txt):
            continue
        t = tweet_kst(r.get('dt'))
        if t is None or t.date().isoformat() != date:
            continue
        body = ' '.join(x.strip() for x in txt.splitlines() if x.strip())
        out.append('%s\n%s\n' % (body, stamp(date, t.strftime('%H:%M'))))
    return '\n'.join(out)


# ── 사람이 읽는 한 줄(장중 md) ───────────────────────────────────
_KO = {'TWEET': '트윗', 'ARM': '대기', 'ENTER': '진입', 'SET_STOP': '손절가', 'SET_TARGET': '청산가',
       'EXIT': '청산주문', 'CLOSED': '청산완료', 'REJECT': '기각', 'DISARM': '대기해제',
       'EXPIRE': '만료', 'HALT': '정지', 'CONFIRM': '체결확인', 'SHADOW': '섀도',
       'EXIT_FAIL': '청산실패', 'FILL_OFFSET': '오프셋검산', 'IGNORE': '무시', 'SKIP': '건너뜀',
       'KEEP': '유지'}
_QUIET = {'IGNORE', 'SKIP', 'KEEP'}


def _f(v):
    return ('%.2f' % v) if isinstance(v, (int, float)) else ('-' if v is None else str(v))


def event_md(e):
    k = e.get('kind')
    if not k or k in _QUIET:
        return None
    hm = e.get('hm') or '--:--'
    if k == 'TWEET':
        body = (e.get('raw') or '').replace('|', '／')
        facts = ', '.join('%s%s' % (f.get('type'), ('=' + _f(f.get('level'))) if f.get('level') is not None else '')
                          for f in (e.get('facts') or []))
        txt = '「%s」 → %s' % (body, facts or '-')
    elif k == 'ARM':
        txt = '%s %s 피터 %s → 미니 %s (오프셋 %s)' % (e.get('side'), e.get('mode'), _f(e.get('peter')),
                                              _f(e.get('mini')), _f(e.get('offset')))
    elif k == 'ENTER':
        txt = '**%s @%s** 손절 %s 목표 %s — %s' % (e.get('side'), _f(e.get('price')), _f(e.get('stop')),
                                              _f(e.get('target')), e.get('why') or '')
    elif k in ('SET_STOP', 'SET_TARGET'):
        txt = '%s → %s (%s)' % (_f(e.get('old')), _f(e.get('new')), e.get('why') or '')
    elif k == 'EXIT':
        txt = '**%s** @%s (%s)' % (e.get('reason'), _f(e.get('price')), e.get('why') or '')
    elif k == 'CLOSED':
        txt = '**%+.2fpt** (%s원) %s' % (float(e.get('pnl_pts') or 0), _f(e.get('pnl_krw')),
                                        e.get('reason') or '')
    elif k == 'FILL_OFFSET':
        txt = '그의 체결가로 역산한 오프셋 %s (사용 중 %s)' % (_f(e.get('implied')), _f(e.get('used')))
    else:
        rest = {x: y for x, y in e.items() if x not in ('kind', 'hm', 'facts', 'raw', 'at')}
        txt = ', '.join('%s=%s' % (x, _f(y)) for x, y in rest.items())
    return '| %s | %s | %s |' % (hm, _KO.get(k, k), txt.replace('\n', ' '))
