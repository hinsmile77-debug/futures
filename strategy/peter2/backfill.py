# -*- coding: utf-8 -*-
"""[MW0601 677차] 피터2 백필 — 실거래 개시(`PETER2_BACKFILL_UNTIL`) **이전** 손익.

사용자 지시(2026-10-09)
    10/12 이전 손익추이는 1분봉 차트의 거래실적(「거래피터」)으로 손익을 산출해 올린다.
    · 원천 A — `peter_paste.raw_tr`(차트가 그리는 확정본) → **표의 값**
    · 원천 B — `tools/peter2_replay.py`(추종 규칙 재생) → **비교 열**
    · 기록 없는 날은 사용자가 「미측정」으로 적는다(장부 `PETER2_BACKFILL_UNMEASURED`).
    · 손익추이(CYBOS 요율)와 손익추이2(CREON 요율 반사실) 둘 다에 올린다 — 실거래는 CREON 예정.

무엇인가 / 무엇이 아닌가
    A 는 「피터 원거래를 미니 1계약으로 환산한 값」이다. 피터2 가 실제로 벌었을 돈이 아니다
    (지연·추격 한도·체결 실패가 없다). B 는 그 규칙을 봉 경로로 재생한 값이지만 슬리피지 0 ·
    봉 안 순서 가정이라 **낙관**이다(2026-10-09 실측: 8/3–10/8 추종 효율 1.33 — 원본보다 더 번다).
    🔴 둘 다 **가상**이다. `trades` 에 넣지 않는다(브로커 대사·전환기준 ①·CB·켈리).

A 환산 규칙 (피터2 실집행이 넘을 수 없는 엔진 제약만 적용)
    · pt     = 그의 가격 차 그대로(정규·미니 같은 지수라 오프셋과 무관)
    · 15:10  = 그가 15:10 이후 청산했거나 미청산이면 **15:10 강제청산 가격**으로 다시 잰다
               (절대원칙 §1). 미니 1분봉에서 15:10 봉 시가, 없으면 그 직전 봉 종가.
               이때만 오프셋이 필요하다(진입가를 미니가로 옮긴다).
    · 14:50  = 신규진입 마감(`NEW_ENTRY_CUTOFF`) 이후 진입은 **제외**한다 — 피터2 가 못 들어간다.
    · 원화   = 1계약 × 50,000원/pt. 수수료는 패널이 **탭 요율로** 뗀다(엔진과 같은 식:
               진입가 × 승수 × 요율 × 2). 그래서 여기에는 gross 와 진입 약정(notional)만 둔다.
    · 슬리피지 0 — 가정이다.
    ⚠ 만기 직후 오프셋 가드(live 의 offset_safe)·수집기 하트비트·미륵이 보유 중 건너뜀은
      재현하지 않는다(A 는 규칙 재생이 아니다 — 그건 B 의 몫).

일자 상태 (계측 4원칙 ② — 「0건」과 「모른다」를 가른다)
    TRADED      사료 있음 · A 거래 1건 이상
    NO_TRADE    사료 있음 · 거래줄 0 — 그날 그는 거래하지 않았다(확정 0건)
    UNMEASURED  사용자가 장부에 「미측정」으로 적은 날 — 값 없음
    UNRESOLVED  사료도 장부도 없다 — **사용자 기록 대기**(0원으로 세지 않는다)
    LIVE        `trades` 에 PETER2 실거래가 있다 — 백필하지 않는다(이중계상 방지)
"""
import datetime as _dt
import io
import os
import re
import sqlite3

#: 차트 거래줄 정규식 — `dashboard/main_dashboard.py:_PT_TRADE` 와 **같아야 한다**
#: (Qt 를 끌어오지 않으려고 사본을 둔다. 갈리면 tests/test_677_peter2_backfill.py 가 깨진다).
TRADE_RE = re.compile(
    r'^\s*(\d{1,2}:\d{2})\s+([LS])\s+(\d{3,4}(?:\.\d{1,2})?)\s*/\s*'
    r'(?:(\d{1,2}:\d{2})\s+X\s+(\d{3,4}(?:\.\d{1,2})?)|(-))\s*(.*)$')

FORCE_EXIT_HM = "15:10"
NEW_ENTRY_CUTOFF_HM = "14:50"
SRC_A = "A"      # 거래피터(peter_paste.raw_tr) — 표의 값
SRC_B = "B"      # 재생(peter2_replay) — 비교 열

ST_TRADED, ST_NO_TRADE = "TRADED", "NO_TRADE"
ST_UNMEASURED, ST_UNRESOLVED, ST_LIVE = "UNMEASURED", "UNRESOLVED", "LIVE"

DDL = """
CREATE TABLE IF NOT EXISTS bf_trades (
    src          TEXT NOT NULL,          -- 'A' | 'B'
    trade_date   TEXT NOT NULL,
    seq          INTEGER NOT NULL,
    side         TEXT NOT NULL,          -- 'LONG' | 'SHORT'
    entry_ts     TEXT NOT NULL,
    exit_ts      TEXT NOT NULL,
    entry_px     REAL,                   -- 미니가(A: 그의 가격 + 오프셋 / B: 재생 체결가)
    exit_px      REAL,
    pnl_pts      REAL NOT NULL,
    qty          INTEGER NOT NULL DEFAULT 1,
    gross_krw    REAL NOT NULL,          -- 수수료 차감 전
    notional_krw REAL NOT NULL,          -- 진입가 × 승수 × 수량 — 수수료 = notional × 요율 × 2
    exit_reason  TEXT,
    clipped      INTEGER NOT NULL DEFAULT 0,   -- 1 = 15:10 강제청산으로 다시 잼
    note         TEXT,
    PRIMARY KEY (src, trade_date, seq)
);
CREATE TABLE IF NOT EXISTS bf_days (
    trade_date   TEXT PRIMARY KEY,
    status       TEXT NOT NULL,          -- TRADED | NO_TRADE | UNMEASURED | UNRESOLVED | LIVE
    a_n          INTEGER,                -- NULL = 미측정(0 이 아니다)
    a_pts        REAL,
    b_status     TEXT,                   -- OK | NO_RAW | NO_BARS | NO_OFFSET | ERROR:… | SKIP
    b_n          INTEGER,
    b_pts        REAL,
    offset       REAL,
    note         TEXT
);
CREATE TABLE IF NOT EXISTS bf_meta (k TEXT PRIMARY KEY, v TEXT);
"""


# ── 파싱 ─────────────────────────────────────────────────────────────
def _hm(s):
    """'9:39' → '09:39'. 시각 문자열 비교가 성립하도록 0 을 채운다."""
    h, m = s.split(':')
    return '%02d:%s' % (int(h), m)


def parse_tr(text):
    """거래줄 → (trades, errors). 못 맞춘 줄은 버리지 않고 errors 로 돌려준다(원칙 ③)."""
    out, err = [], []
    for ln in (text or '').splitlines():
        if not ln.strip():
            continue
        m = TRADE_RE.match(ln)
        if not m:
            err.append(ln.strip())
            continue
        i, d, ep, x, xp, opn, why = m.groups()
        out.append({'entry_hm': _hm(i), 'side': 'LONG' if d == 'L' else 'SHORT',
                    'entry': float(ep), 'exit_hm': _hm(x) if x else None,
                    'exit': float(xp) if xp else None, 'open': bool(opn),
                    'why': (why or '').strip()})
    return out, err


def force_exit_price(bars):
    """(가격, 근거). bars = [(ts, open, high, low, close)] 미니 1분봉(오름차순).

    15:10 봉이 있으면 그 시가, 없으면 15:10 직전 마지막 봉 종가.
    🔴 미륵이 raw_candles 는 마지막 저장 ts 가 15:08 인 날이 있다(time_utils 주석) —
      그래서 「직전 봉 종가」 폴백이 정상 경로다. 못 찾으면 (None, 이유).
    """
    last = None
    for ts, o, _h, _l, c in bars or []:
        hm = str(ts)[11:16]
        if hm >= FORCE_EXIT_HM:
            return float(o), '%s 시가' % hm
        last = (float(c), '%s 종가' % hm)
    if last is None:
        return None, '분봉 없음'
    return last


# ── A: 거래피터 → 미니 1계약 ──────────────────────────────────────────
def build_a_day(date, raw_tr, offset, bars, pt_value):
    """(trades, notes). trades 는 bf_trades 행(src='A') 형태."""
    parsed, errs = parse_tr(raw_tr)
    notes = ['파싱 실패: %s' % e for e in errs]
    off = float(offset) if offset is not None else None
    out = []
    for t in parsed:
        if t['entry_hm'] >= NEW_ENTRY_CUTOFF_HM:
            notes.append('제외(%s 진입 — 신규진입 마감 %s 이후)' % (t['entry_hm'], NEW_ENTRY_CUTOFF_HM))
            continue
        sgn = 1.0 if t['side'] == 'LONG' else -1.0
        entry_m = t['entry'] + (off or 0.0)
        clipped, note, reason = 0, '', t['why']
        late = t['open'] or (t['exit_hm'] is not None and t['exit_hm'] >= FORCE_EXIT_HM)
        if late:
            px, src = force_exit_price(bars)
            if px is None or off is None:
                # 다시 잴 수 없다 — 그의 청산가를 쓰되 그 사실을 남긴다(원칙 ④)
                exit_m = (t['exit'] + (off or 0.0)) if t['exit'] is not None else None
                note = '15:10 재측정 불가(%s · offset %s) — 그의 청산가' % (
                    src, 'None' if off is None else off)
                if exit_m is None:
                    notes.append('제외(%s 미청산 · 15:10 가격 없음)' % t['entry_hm'])
                    continue
                exit_hm = t['exit_hm']
            else:
                exit_m, exit_hm, clipped = px, FORCE_EXIT_HM, 1
                note = '그의 청산 %s %s → 15:10 강제청산(%s)' % (
                    t['exit_hm'] or '미청산', t['exit'] if t['exit'] is not None else '-', src)
                reason = '15:10 강제청산'
        else:
            exit_m, exit_hm = t['exit'] + (off or 0.0), t['exit_hm']
        pts = round(sgn * (exit_m - entry_m), 2)
        out.append({
            'src': SRC_A, 'trade_date': date, 'seq': len(out) + 1, 'side': t['side'],
            'entry_ts': '%s %s:00' % (date, t['entry_hm']),
            'exit_ts': '%s %s:00' % (date, exit_hm),
            'entry_px': round(entry_m, 2), 'exit_px': round(exit_m, 2),
            'pnl_pts': pts, 'qty': 1,
            'gross_krw': round(pts * pt_value, 0),
            'notional_krw': round(entry_m * pt_value, 0),
            'exit_reason': reason, 'clipped': clipped,
            'note': note + ('' if off is not None else ' · offset 없음(약정=그의 가격)'),
        })
    return out, notes


def b_trades_from_replay(date, res, pt_value):
    """replay_day() 결과 → bf_trades 행(src='B'). 재생 가격은 이미 미니가다."""
    out = []
    for t in res.get('trades') or []:
        pts = float(t['pnl'])
        ent = float(t['entry'])
        out.append({
            'src': SRC_B, 'trade_date': date, 'seq': len(out) + 1, 'side': t['side'],
            'entry_ts': '%s %s' % (date, t['entry_t']), 'exit_ts': '%s %s' % (date, t['exit_t']),
            'entry_px': ent, 'exit_px': float(t['exit']),
            'pnl_pts': round(pts, 2), 'qty': 1,
            'gross_krw': round(pts * pt_value, 0),
            'notional_krw': round(ent * pt_value, 0),
            'exit_reason': t.get('why') or '', 'clipped': 1 if t.get('why') == '15:10 강제청산' else 0,
            'note': '',
        })
    return out


# ── 일자 상태 ────────────────────────────────────────────────────────
def classify_day(has_paste, a_trades, unmeasured, live):
    """우선순위: LIVE > UNMEASURED(사용자 기록) > 사료 유무."""
    if live:
        return ST_LIVE
    if unmeasured:
        return ST_UNMEASURED
    if not has_paste:
        return ST_UNRESOLVED
    return ST_TRADED if a_trades else ST_NO_TRADE


# ── 미측정 장부 ──────────────────────────────────────────────────────
def read_unmeasured(path):
    """{date: 사유}. 파일이 없으면 빈 dict(아직 아무도 적지 않았다)."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    with io.open(path, encoding='utf-8') as f:
        for ln in f:
            s = ln.strip()
            if not s or s.startswith('#'):
                continue
            parts = s.split(None, 1)
            try:
                _dt.date.fromisoformat(parts[0])
            except ValueError:
                continue
            out[parts[0]] = parts[1].strip() if len(parts) > 1 else ''
    return out


def mark_unmeasured(path, dates, reason):
    """장부에 덧붙인다(이미 있는 날은 건너뛴다). 반환: 새로 적은 날짜."""
    have = read_unmeasured(path)
    new = []
    for d in dates:
        _dt.date.fromisoformat(d)          # 형식 오류는 예외로 — 조용히 넘기지 않는다
        if d not in have:
            new.append(d)
    if not new:
        return []
    os.makedirs(os.path.dirname(path), exist_ok=True)
    first = not os.path.exists(path)
    with io.open(path, 'a', encoding='utf-8') as f:
        if first:
            f.write('# [677차] 피터2 백필 — 사용자가 「미측정」으로 적은 날(사료 없음).\n'
                    '# 한 줄 = YYYY-MM-DD 사유. 지우면 다음 빌드에서 다시 「미판정」이 된다.\n')
        for d in new:
            f.write('%s %s\n' % (d, reason or '사료 없음 — 사용자 기록'))
    return new


# ── 저장 / 조회 ──────────────────────────────────────────────────────
def connect(db_path):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.executescript(DDL)
    return con


def save(db_path, trades, days, meta):
    """전량 교체 — 백필은 원천에서 언제나 다시 만들 수 있는 파생물이다."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = connect(db_path)
    try:
        with con:
            con.execute('DELETE FROM bf_trades')
            con.execute('DELETE FROM bf_days')
            con.execute('DELETE FROM bf_meta')
            con.executemany(
                'INSERT INTO bf_trades(src,trade_date,seq,side,entry_ts,exit_ts,entry_px,exit_px,'
                'pnl_pts,qty,gross_krw,notional_krw,exit_reason,clipped,note) VALUES '
                '(:src,:trade_date,:seq,:side,:entry_ts,:exit_ts,:entry_px,:exit_px,:pnl_pts,'
                ':qty,:gross_krw,:notional_krw,:exit_reason,:clipped,:note)', trades)
            con.executemany(
                'INSERT INTO bf_days(trade_date,status,a_n,a_pts,b_status,b_n,b_pts,offset,note)'
                ' VALUES (:trade_date,:status,:a_n,:a_pts,:b_status,:b_n,:b_pts,:offset,:note)',
                days)
            con.executemany('INSERT INTO bf_meta(k,v) VALUES (?,?)',
                            [(k, str(v)) for k, v in meta.items()])
    finally:
        con.close()


def load_for_pnl(db_path, limit_days=90, today=None):
    """손익추이 패널용 묶음. DB 가 없으면 None — 「미배선」이지 「0건」이 아니다(원칙 ②).

    반환: {'a': [...], 'b': [...], 'days': [...], 'meta': {...}} — 전부 dict.
    """
    if not os.path.exists(db_path):
        return None
    since = ((today or _dt.date.today()) - _dt.timedelta(days=int(limit_days))).isoformat()
    con = sqlite3.connect('file:%s?mode=ro' % db_path.replace('\\', '/'), uri=True)
    con.row_factory = sqlite3.Row
    try:
        tr = [dict(r) for r in con.execute(
            'SELECT * FROM bf_trades WHERE trade_date>=? ORDER BY trade_date, src, seq', (since,))]
        days = [dict(r) for r in con.execute(
            'SELECT * FROM bf_days WHERE trade_date>=? ORDER BY trade_date', (since,))]
        meta = {r['k']: r['v'] for r in con.execute('SELECT k, v FROM bf_meta')}
    finally:
        con.close()
    return {'a': [t for t in tr if t['src'] == SRC_A],
            'b': [t for t in tr if t['src'] == SRC_B],
            'days': days, 'meta': meta}
