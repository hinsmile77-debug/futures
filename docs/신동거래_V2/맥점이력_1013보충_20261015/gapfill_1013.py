# -*- coding: utf-8 -*-
"""🔴 [2026-10-15 06:01 되돌림] 기록 보존용 — **다시 실행하지 말 것.**
`raw_candles` 에 행을 더하는 것은 533차 원칙 위반이다(`utils/bar_gap.py` 「메우지 않는다」).
이 스크립트로 넣은 109행은 같은 날 삭제했고, 맥점 이력은 `levels_store.load_sessions()` 의
`session_bars` 보완(메모리 전용)으로 대체됐다. 경위: `신동_8일_종합평가_변형비교_MW0602-20261014.md` §5-1·§5-2.

10/13 raw_candles 결측(12:51~14:06 · 14:11~14:41) 을 session_bars(chart_backfill/rt) OHLCV 로 보충.
- 기존 행은 건드리지 않는다(INSERT 만, ts 가 이미 있으면 건너뜀).
- OHLCV 외 열은 미계측 → NULL (buy_vol/sell_vol 도 DEFAULT 0 을 쓰지 않고 명시적 NULL — 계측 4원칙 ②).
- bar_recovered = 1 (열화 복구봉 표시).
사용: python gapfill_1013.py [--apply]
"""
import sqlite3, sys, datetime
DB = sys.argv[1]
APPLY = "--apply" in sys.argv
DAY = "2026-10-13"
con = sqlite3.connect(DB)
have = set(r[0] for r in con.execute("SELECT ts FROM raw_candles WHERE ts LIKE ?", (DAY + "%",)))
sb = con.execute("SELECT ts, open, high, low, close, volume, source, session FROM session_bars "
                 "WHERE ts >= ? AND ts <= ? AND session = 'REGULAR' ORDER BY ts",
                 (DAY + " 08:45:00", DAY + " 15:08:00")).fetchall()
# raw_candles 의 그날 범위(08:45~15:08) 안에서 빠진 분만
t, end = datetime.datetime(2026, 10, 13, 8, 45), datetime.datetime(2026, 10, 13, 15, 8)
want = []
while t <= end:
    want.append(t.strftime("%Y-%m-%d %H:%M:%S")); t += datetime.timedelta(minutes=1)
missing = [x for x in want if x not in have]
sbm = dict((r[0], r) for r in sb)
fill = [sbm[x] for x in missing if x in sbm]
nofill = [x for x in missing if x not in sbm]
print("raw rows", len(have), "| missing", len(missing), "| fillable", len(fill), "| unfillable", nofill[:10])
print("sources", sorted(set(r[6] for r in fill)))
print("first/last", fill[0][:6] if fill else None, fill[-1][:6] if fill else None)
# 경계 연속성: 결측 직전/직후 raw 봉 종가 vs 보충 첫/끝 봉 시가
for a, b in (("12:50", "12:51"), ("14:06", "14:07"), ("14:10", "14:11"), ("14:41", "14:42")):
    ra = con.execute("SELECT close FROM raw_candles WHERE ts=?", (DAY + " %s:00" % a,)).fetchone()
    rb = con.execute("SELECT open FROM raw_candles WHERE ts=?", (DAY + " %s:00" % b,)).fetchone()
    fa = sbm.get(DAY + " %s:00" % a); fb = sbm.get(DAY + " %s:00" % b)
    print(" boundary %s→%s raw(c/o)=%s/%s sb(c/o)=%s/%s" % (a, b, ra and ra[0], rb and rb[0],
          fa and fa[4], fb and fb[1]))
if APPLY and fill:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with con:
        n = 0
        for ts, o, h, l, c, v, _src, _ses in fill:
            cur = con.execute(
                "INSERT OR IGNORE INTO raw_candles (ts, open, high, low, close, volume, bid1, ask1, oi, created_at, "
                "buy_vol, sell_vol, anchor_buy, anchor_sell, buy_vol_flag, sell_vol_flag, bar_recovered, "
                "book_bid_tot, book_ask_tot, book_bid_avg, book_ask_avg, book_snaps, unk_vol, book_bid_max, book_ask_max) "
                "VALUES (?,?,?,?,?,?,NULL,NULL,NULL,?,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)",
                (ts, o, h, l, c, int(v), now))
            n += cur.rowcount
    print("INSERTED", n)
    print("after", con.execute("SELECT count(*), sum(bar_recovered=1) FROM raw_candles WHERE ts LIKE ?", (DAY + "%",)).fetchone())
