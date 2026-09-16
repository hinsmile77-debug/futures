# -*- coding: utf-8 -*-
# scripts/mark_roll_and_halts.py — 롤 당일·거래정지(CB) 라벨 산출
"""미륵이 `raw_candles`(미니 당월물)와 `regular_candles`(정규 연결 10100)를 대조해
**계약 교체로 생긴 가짜 갭**과 **서킷브레이커 추정 구간**을 표로 만든다.

왜 필요한가
-----------
미륵이는 미니 **당월물**을 본다. 정규는 **분기물**이라 두 시계열의 만기 격차가
0 → 1개월 → 2개월 → 0 으로 순환하고, 그 격차가 그대로 가격차가 된다.
실측(261거래일): 중앙 +0.31p, 75%% +2.04p, 최대 +11.28p.
미니가 월물을 갈아탈 때마다 **시장이 움직이지 않아도** 전일종가 대비 시가가 튄다.
`features/levels/premarket_levels.py` 의 `gap = (s.o - p.c) / s.atr` 가 이걸
시장 변동으로 학습한다. 저변동 국면(ATR<20)에서는 갭의 **36%%** 가 가짜였다.

산출물 (regular_candles.db 안에만 쓴다 — raw_data.db 는 열지 않는다)
    roll_days(trade_date, spread_prev, spread, jump, gap_pt, gap_adj_pt, atr, note)
    cb_halts(trade_date, start_hm, end_hm, minutes, day_range_pct, note)

실행:  python scripts/mark_roll_and_halts.py            (32비트 불필요, COM 불필요)
       python scripts/mark_roll_and_halts.py --show
"""
from __future__ import print_function
import argparse, datetime as _dt, os, sqlite3, sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG_DB = os.path.join(_ROOT, "data", "db", "regular_candles.db")
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")
REGULAR_CODE = "10100"
SESSION_OPEN = "08:45"        # collect_regular_futures 의 보정 후 기준과 같아야 한다
JUMP_THRESHOLD = 1.0          # 일별 스프레드 변화가 이 이상이면 계약 교체로 본다(p)
# ── 미륵이 raw_candles 시각 규약 전환 ─────────────────────────────────────────
# `raw_candles` 의 봉 시각 라벨이 2026-05-04 경계로 **1분 당겨졌다**(풀타임 수집 전환).
#   · 2026-05-04 이전: 일별 첫 봉 09:00, 사이보스 원본 라벨과 같은 축(= 종료시각)
#   · 2026-05-04 이후: 일별 첫 봉 08:45(개장), 시작시각 축
#   근거: 1분 수익률 상관 일별 전수 — 이전 구간 lag=+1, 이후 구간 lag=0 (0.97~0.999)
# `regular_candles` 는 시작시각 축으로 통일돼 있으므로(collect 시 -1분),
# **전환 이전 구간은 raw 쪽을 1분 당겨서** 조인해야 맞는다.
MINI_TS_EPOCH = "2026-05-04"  # 이 날짜 이전의 raw_candles 는 조인 시 -1분
OUTLIER_JUMP = 20.0           # 이보다 크면 계약 교체가 아니라 원천 데이터 이상치로 본다
FULL_BARS = 411

DDL = """
CREATE TABLE IF NOT EXISTS roll_days (
    trade_date TEXT PRIMARY KEY, spread_prev REAL, spread REAL, jump REAL,
    gap_pt REAL, gap_adj_pt REAL, atr REAL, note TEXT, computed_at TEXT);
CREATE TABLE IF NOT EXISTS cb_halts (
    trade_date TEXT, start_hm TEXT, end_hm TEXT, minutes INTEGER,
    day_range_pct REAL, note TEXT, computed_at TEXT,
    PRIMARY KEY (trade_date, start_hm));
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true", help="산출 결과만 출력")
    ap.add_argument("--reg-db", default=REG_DB, help="regular_candles.db 경로")
    ap.add_argument("--raw-db", default=RAW_DB, help="raw_data.db 경로(읽기 전용)")
    a = ap.parse_args()
    return run(a.reg_db, a.raw_db, show_only=a.show)


def run(reg_db=None, raw_db=None, show_only=False, quiet=False):
    """라벨 재계산. `collect_regular_futures` 가 수집 직후 직접 호출한다.

    배치 파일에서 별도 프로세스로 부르던 것을 함수 호출로 바꿨다 —
    cmd 조건문·ERRORLEVEL 전파에 의존하면 실패가 조용히 묻힌다(2026-09-11 3회 실측).
    """
    reg_db = reg_db or REG_DB
    raw_db = raw_db or RAW_DB
    if not os.path.exists(reg_db):
        raise RuntimeError("%s 없음 — 먼저 수집할 것" % reg_db)

    con = sqlite3.connect(reg_db)
    con.executescript(DDL); con.commit()
    if show_only:
        _show(con); return 0

    # raw_data.db 는 **읽기 전용 별도 연결**로 읽어 TEMP 테이블에 옮긴다.
    # (ATTACH 에 URI 를 쓰면 Windows/py37 sqlite 빌드에서 조용히 실패한다 — 2026-09-11 실측)
    try:
        rcon = sqlite3.connect("file:%s?mode=ro" % raw_db.replace("\\", "/"), uri=True, timeout=5.0)
    except Exception:
        rcon = sqlite3.connect(raw_db, timeout=5.0)
    try:
        rows_raw = rcon.execute("SELECT ts, open, high, low, close FROM raw_candles").fetchall()
    finally:
        rcon.close()
    con.execute("CREATE TEMP TABLE mini (ts TEXT PRIMARY KEY, open REAL, high REAL, low REAL, close REAL)")
    con.executemany("INSERT OR REPLACE INTO mini VALUES (?,?,?,?,?)", rows_raw)
    print("  [raw] raw_candles %d행 로드(읽기 전용)" % len(rows_raw))
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 라벨은 매번 **전량 재계산**한다 — 시각 규약이 바뀌면 옛 행이 유령으로 남는다
    # (실제로 2026-09-11 ts 정렬 마이그레이션 뒤 cb_halts 가 1분씩 어긋나 이중 적재됐다).
    con.execute("DELETE FROM roll_days")
    con.execute("DELETE FROM cb_halts")

    # ── 일별 스프레드(정규 − 미니) 중앙값 → 변화량이 임계 이상이면 롤 ──────────
    rows = con.execute("""
        SELECT r.trade_date, AVG(r.close - m.close)
        FROM regular_candles r
        JOIN mini m
          ON m.ts = CASE WHEN r.trade_date < ?
                         THEN strftime('%Y-%m-%d %H:%M:00', datetime(r.ts, '+1 minutes'))
                         ELSE r.ts END
        WHERE r.code=? GROUP BY r.trade_date ORDER BY r.trade_date""",
        (MINI_TS_EPOCH, REGULAR_CODE)).fetchall()
    # 미니 일별 OHLC + ATR14
    md = con.execute("""
        SELECT substr(ts,1,10) d, MIN(ts), MAX(ts) FROM mini GROUP BY d ORDER BY d""").fetchall()
    ohlc = {}
    for d, t0, t1 in md:
        o = con.execute("SELECT open FROM mini WHERE ts=?", (t0,)).fetchone()[0]
        c = con.execute("SELECT close FROM mini WHERE ts=?", (t1,)).fetchone()[0]
        hi, lo = con.execute("SELECT MAX(high), MIN(low) FROM mini"
                             " WHERE substr(ts,1,10)=?", (d,)).fetchone()
        ohlc[d] = (o, hi, lo, c)
    days = sorted(ohlc)
    trs, atr = [], {}
    for i, d in enumerate(days):
        o, hi, lo, c = ohlc[d]
        pc = ohlc[days[i - 1]][3] if i else None
        tr = (hi - lo) if pc is None else max(hi - lo, abs(hi - pc), abs(lo - pc))
        trs.append(tr)
        if len(trs) >= 14:
            atr[d] = sum(trs[-14:]) / 14.0

    sp = dict(rows)
    keys = sorted(sp)
    n = 0
    for i in range(1, len(keys)):
        d, pd_ = keys[i], keys[i - 1]
        jump = sp[d] - sp[pd_]
        if abs(jump) < JUMP_THRESHOLD:
            continue
        prev_day = [x for x in days if x < d]
        gap = (ohlc[d][0] - ohlc[prev_day[-1]][3]) if prev_day and d in ohlc else None
        con.execute("INSERT OR REPLACE INTO roll_days VALUES (?,?,?,?,?,?,?,?,?)",
                    (d, sp[pd_], sp[d], jump, gap,
                     (gap + jump) if gap is not None else None, atr.get(d),
                     ("스프레드 점프 %+.2fp — 미니 당월물 교체 추정" % jump) if abs(jump) < OUTLIER_JUMP
                     else ("스프레드 점프 %+.2fp — 원천 데이터 이상치 의심(계약 교체 아님). "
                           "학습 제외 권장" % jump), now))
        n += 1

    # ── 장중결손(첫 봉 정상 + 봉 수 부족) → CB/매매정지 추정 ──────────────────
    ref = [r[0] for r in con.execute(
        "SELECT substr(ts,12,5) FROM regular_candles WHERE code=? AND trade_date="
        "(SELECT trade_date FROM regular_candles WHERE code=? GROUP BY trade_date"
        " HAVING COUNT(*)>=? ORDER BY trade_date DESC LIMIT 1) ORDER BY ts",
        (REGULAR_CODE, REGULAR_CODE, FULL_BARS))]
    bad = con.execute(
        "SELECT trade_date, COUNT(*) FROM regular_candles WHERE code=? GROUP BY trade_date"
        " HAVING COUNT(*) < ? AND MIN(substr(ts,12,5))=?", (REGULAR_CODE, FULL_BARS, SESSION_OPEN)).fetchall()
    h = 0
    for d, cnt in bad:
        got = set(x[0] for x in con.execute(
            "SELECT substr(ts,12,5) FROM regular_candles WHERE code=? AND trade_date=?", (REGULAR_CODE, d)))
        miss = [t for t in ref if t not in got]
        rng = con.execute("SELECT 100.0*(MAX(high)-MIN(low))/MIN(low) FROM regular_candles"
                          " WHERE code=? AND trade_date=?", (REGULAR_CODE, d)).fetchone()[0]
        s = p = None
        for t in miss + [None]:
            if t is not None and s is None:
                s = p = t; continue
            if t is not None and ref.index(t) == ref.index(p) + 1:
                p = t; continue
            if s is not None and ref.index(p) - ref.index(s) + 1 >= 10:
                con.execute("INSERT OR REPLACE INTO cb_halts VALUES (?,?,?,?,?,?,?)",
                            (d, s, p, ref.index(p) - ref.index(s) + 1, rng,
                             "1분봉 연속 결손 — 서킷브레이커/매매정지 추정", now))
                h += 1
            s = p = t
    con.commit()
    print("[DONE] roll_days %d건 / cb_halts %d건 적재 → %s" % (n, h, reg_db))
    if not quiet:
        _show(con)
    con.close()
    return 0


def _show(con):
    print("\n=== roll_days (계약 교체 추정) ===")
    print(" 일자         스프레드 점프   원본갭(p)  롤보정갭(p)   ATR   가짜비중")
    for d, jp, gap, adj, at in con.execute(
            "SELECT trade_date, jump, gap_pt, gap_adj_pt, atr FROM roll_days ORDER BY trade_date"):
        share = (abs(jp) / abs(gap) * 100) if gap else float("nan")
        mark = " ⚠이상치" if abs(jp) >= OUTLIER_JUMP else ""
        print("  %s   %+7.2f   %+9.2f   %+9.2f %7.2f   %5.0f%%%s"
              % (d, jp, gap or 0, adj or 0, at or 0, min(share, 999), mark))
    print("\n=== cb_halts (거래정지 추정) ===")
    print(" 일자         구간            분   일중변동")
    for d, s, e, m, rng in con.execute(
            "SELECT trade_date, start_hm, end_hm, minutes, day_range_pct FROM cb_halts ORDER BY trade_date"):
        print("  %s   %s~%s   %2d   %6.2f%%" % (d, s, e, m, rng))


if __name__ == "__main__":
    sys.exit(main())
