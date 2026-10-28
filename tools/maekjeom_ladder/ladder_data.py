# -*- coding: utf-8 -*-
"""맥점 × 옵션 사다리 — 날짜별 데이터 생성 (읽기전용).

[MW0601 656차 / 2026-10-04] 로컬 서버(`server.py`)가 이 모듈로 하루치 JSON 을 만든다.
표준 라이브러리만 쓴다(numpy·pandas 없음 → BLAS delay-load 즉사 경로와 무관).

원천 (전부 `mode=ro`)
  · 1분봉     regular_candles.db (미니 근월물 — 날짜마다 `mini_code(day)`, 08:45–15:45 · 장후 15:52 적재)
              → 오늘이거나 그날 적재 전이면 raw_data.db raw_candles(라이브)
  · 맥점      premarket_levels.db (08:50 · 09:30) · peter_levels.db(피터, 대시보드 파서 재사용)
  · 행사가 OI option_book.db (5분)
  · 주체 흐름 option_flow.db (7222, 1분)
  · 행사가×주체 HTS [9842] 내보내기 파일 (data/db/option_hts, YYMMDD_D·YYMMDD_P, 하루 1장씩)

🔴 456차(장중 라이브 DB 분석 금지) 준수
  장중에 raw_data.db(468MB)에 닿는 것은 **오늘 봉의 ts 범위 조회 하나**뿐이고, 그마저
  마지막으로 받은 ts 이후만 증분으로 읽는다(PK 인덱스). 전수 스캔·집계 쿼리는 없다.
  나머지 DB 는 수 MB – 수십 MB 다.
"""
from __future__ import annotations

import ast
import datetime as _dt
import json
import os
import re
import sqlite3
import threading
import zipfile
from html.parser import HTMLParser
from xml.etree import ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(ROOT, "data", "db")
# [2026-10-04 사용자 지정] 저장소 안 data/db/option_hts — .gitignore(data/*) 대상이라 커밋되지 않는다.
#   종전 위치 ~/Documents/옵션 은 더 읽지 않는다.
DOCS_9842 = os.path.join(DB, "option_hts")
MINI_CODE = "A056A"   # 🔴 [MW0602 641차] 하위호환 이름만 남긴다 — 조회에 쓰지 말 것. 근월물은 `mini_code(day)` 로 날짜마다 정한다.
MINI_PREFIX = "A05"   # 미니 KOSPI200 선물 종목코드 접두(A05 + 연도 1자리 + 월 1자리: 1–9·A·B·C). 예 A056A=2026-10, A056B=2026-11


def mini_code_for(con, day):
    """[MW0602 641차] 그날의 미니 **근월물** 코드 — 그날 봉이 있는 A05* 중 **만기가 가장 가까운 것**(문자열 최소).

    🔴 2026-10-08(10월물 만기) 이후 `code='A056A'` 하드코딩이 조용히 낡았다. 수집기(`collect_regular_futures.py`)는
       롤을 따라 A056B 를 매일 적재했지만, 읽는 쪽 네 곳(사다리·신동2 전일 참조·PIT 복기·지표 검증)이 A056A 만 찾아
       「10/08 에서 적재가 멈췄다」로 보였다. 원인 딥다이브: `docs/맥점x옵션사다리개선/09_정규봉적재중단_딥다이브_MW0602-20261020.md`.
    규칙 근거(실측 2026-10-06–10-12, 미륵이 raw_candles 와 종가 대조): 만기일 당일(10/08)까지 미륵이는 A056A 를 거래했다
       (오차 0.000 · A056B 는 2.747). 거래량은 10/08 에 이미 A056B 가 컸으므로 **거래량 최대로 고르면 틀린다.**
    코드 문자열 정렬 = 만기 순서: 연도 자리(6 → 7)가 월 자리보다 앞이고, 월 자리는 '1'–'9' < 'A'–'C'(ASCII).
       ⚠ 2030년(연도 자리 '0')에는 이 정렬이 깨진다 — 그때 고칠 것.
    없으면 None(미측정 — 0 으로 메우지 않는다)."""
    r = con.execute("SELECT MIN(code) FROM regular_candles WHERE trade_date=? AND code LIKE ?",
                    (day, MINI_PREFIX + "%")).fetchone()
    return r[0] if r and r[0] else None


_MONTH_CH = {**{str(i): i for i in range(1, 10)}, "A": 10, "B": 11, "C": 12}


def mini_expiry(code):
    """A05 + 연도 + 월 → 그 월물의 만기일(둘째 목요일, 휴장이면 앞당김 — utils.time_utils). 해석 불가면 None."""
    try:
        y = 2020 + int(code[3])
        m = _MONTH_CH[code[4].upper()]
    except (IndexError, KeyError, ValueError, TypeError):
        return None
    try:
        import sys as _s
        if ROOT not in _s.path:
            _s.path.insert(0, ROOT)
        from utils.time_utils import get_monthly_expiry_date
        e = get_monthly_expiry_date(y, m)
        return e.date() if hasattr(e, "date") else e
    except Exception:                                    # 폴백 — 둘째 목요일(휴장 보정 없음)
        d = _dt.date(y, m, 1)
        d += _dt.timedelta(days=(3 - d.weekday()) % 7 + 7)
        return d


def mini_code_continuing(con, prev_day, day):
    """[641차] prev_day 의 미니 봉 가운데 **day 에도 살아 있는 월물**(만기 ≥ day) — 전일 고저종을 오늘 가격과 같은 월물로 비교한다.
    롤 다음 날(예 10/12 의 전일 10/08)에 만기 월물(A056A)을 쓰면 월물 간 격차(~3pt)만큼 전일 레벨이 틀린다.
    그런 월물이 없으면 prev_day 근월물(`mini_code_for`)."""
    codes = [r[0] for r in con.execute("SELECT DISTINCT code FROM regular_candles WHERE trade_date=? AND code LIKE ? ORDER BY code",
                                       (prev_day, MINI_PREFIX + "%"))]
    d = _dt.date.fromisoformat(day)
    for c in codes:
        e = mini_expiry(c)
        if e is not None and e >= d:
            return c
    return codes[0] if codes else None


def mini_code(day):
    """`mini_code_for` 를 DB 를 열어 부르는 편의 함수. DB 가 없거나 그날 미니 봉이 없으면 None."""
    try:
        con = _ro("regular_candles.db")
    except Exception:
        return None
    try:
        return mini_code_for(con, day)
    finally:
        con.close()


# 9842 파일 모드 — 파일 안에 「당일/기간」 표시가 없다(2026-10-02 실측).
#   새 파일은 이름 끝에 _D(당일 순매수) / _P(기간 보유)를 붙인다.
#   그 규칙 전 파일은 `옵션_전일보유_맥점되돌림_MW0601-20261002.md` §0-1 판독을 그대로 쓴다.
LEGACY_9842_MODE = {"260928": "P", "260929": "P", "260930": "P", "261001": "P", "261002": "D"}

# 터치 판정 규칙(사전 고정 — 기존 사다리와 동일)
TOUCH_X = 3.0       # 되돌림·돌파 폭(pt)
TOUCH_WIN = 15      # 판정 창(봉)
MERGE_PT = 1.5      # 구조·거리 합류 판정 폭


def _ro(name):
    path = os.path.join(DB, name).replace("\\", "/")
    return sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=5.0)


def _hm_next(hm):
    h, m = int(hm[:2]), int(hm[3:]) + 1
    return "%02d:%02d" % (h + m // 60, m % 60)


# ── 날짜 목록 ──────────────────────────────────────────────────────────────
def list_dates():
    """복기 가능한 날짜와 원천별 가용 여부. 달력이 이걸로 칸을 칠한다."""
    out = {}

    def mark(rows, key):
        for (d,) in rows:
            if d:
                out.setdefault(d, {})[key] = True

    try:
        con = _ro("premarket_levels.db")
        mark(con.execute("SELECT DISTINCT date FROM premarket_levels"), "levels"); con.close()
    except Exception:
        pass
    try:
        con = _ro("regular_candles.db")
        mark(con.execute("SELECT DISTINCT trade_date FROM regular_candles WHERE code LIKE ?", (MINI_PREFIX + "%",)), "candles"); con.close()
    except Exception:
        pass
    for _db in ("option_book.db", "option_book_fuo.db"):
        try:
            con = _ro(_db)
            mark(con.execute("SELECT DISTINCT substr(ts,1,10) FROM option_book_snap WHERE n_valid>0"), "book"); con.close()
        except Exception:
            pass
    try:
        con = _ro("option_flow.db")
        mark(con.execute("SELECT DISTINCT trade_date FROM option_investor_flow"), "flow"); con.close()
    except Exception:
        pass
    try:
        con = _ro("peter_levels.db")
        mark(con.execute("SELECT date FROM peter_paste"), "peter"); con.close()
    except Exception:
        pass
    for f in _list_9842_files():
        out.setdefault(f["date"], {})["hts9842"] = True
    try:
        for d in db9842_dates():                     # [710차] API 수집본도 같은 표식
            out.setdefault(d, {})["hts9842"] = True
    except Exception:
        pass
    today = _dt.date.today().isoformat()
    out.setdefault(today, {})["today"] = True
    return {"dates": out, "today": today}


# ── 1분봉 ─────────────────────────────────────────────────────────────────
_live_cache = {"date": None, "rows": [], "last_ts": None}
_live_lock = threading.Lock()


def _candles_regular(day):
    """(봉, 코드). 그날 근월물(`mini_code_for`)의 정규 봉. 없으면 ([], None)."""
    con = _ro("regular_candles.db")
    try:
        code = mini_code_for(con, day)
        rows = con.execute(
            "SELECT substr(ts,12,5), open, high, low, close FROM regular_candles"
            " WHERE code=? AND trade_date=? AND substr(ts,12,5) BETWEEN '08:45' AND '15:45' ORDER BY ts",
            (code, day)).fetchall() if code else []
    finally:
        con.close()
    return [[t, round(o, 2), round(h, 2), round(l, 2), round(c, 2)] for t, o, h, l, c in rows], code


def _candles_live(day):
    """raw_data.db 오늘 봉 — 마지막으로 받은 ts 이후만 증분으로 읽는다(456차)."""
    with _live_lock:
        if _live_cache["date"] != day:
            _live_cache.update(date=day, rows=[], last_ts=None)
        lo = _live_cache["last_ts"] or (day + " 08:45:00")
        con = _ro("raw_data.db")
        try:
            new = con.execute(
                "SELECT ts, open, high, low, close FROM raw_candles WHERE ts >= ? AND ts <= ? ORDER BY ts",
                (lo, day + " 15:45:00")).fetchall()
        finally:
            con.close()
        rows = {r[0]: r for r in _live_cache["rows"]}      # 캐시 행의 r[0] 은 이미 'HH:MM'
        for ts, o, h, l, c in new:          # 마지막 봉은 다시 받아 덮어쓴다(덜 찬 봉 갱신)
            rows[ts[11:16]] = [ts[11:16], round(o, 2), round(h, 2), round(l, 2), round(c, 2)]
        _live_cache["rows"] = [rows[k] for k in sorted(rows)]
        if new:
            _live_cache["last_ts"] = new[-1][0]
        return list(_live_cache["rows"]), "raw_candles(live)"


def candles(day, live):
    if not live:
        try:
            rows, code = _candles_regular(day)
            if rows:
                return rows, "regular_candles(%s)" % code
        except Exception:
            pass
    return _candles_live(day)


# ── 맥점 ──────────────────────────────────────────────────────────────────
def levels(day):
    con = _ro("premarket_levels.db")
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute("SELECT * FROM premarket_levels WHERE date=?", (day,)).fetchall()
    finally:
        con.close()
    lv, bands = [], []
    for r in rows:
        st = r["stage"]
        start = "08:51" if st == "0850" else "09:31"
        for side, col in (("up", "struct_up"), ("down", "struct_down")):
            try:
                for price, labs in json.loads(r[col] or "[]"):
                    lv.append(dict(stage=st, start=start, kind="구조", price=float(price), label=" · ".join(labs), side=side))
            except Exception:
                pass
        for side, col in (("up", "dist_high"), ("down", "dist_low")):
            if r[col] is not None:
                lv.append(dict(stage=st, start=start, kind="거리", price=round(r[col], 2), label=col, side=side))
        for nm in ("high50", "high80", "low50", "low80"):
            if r[nm + "_lo"] is not None and r[nm + "_hi"] is not None:
                bands.append(dict(stage=st, name=nm, lo=round(r[nm + "_lo"], 2), hi=round(r[nm + "_hi"], 2)))
    for a in lv:
        a["merge"] = any(b is not a and b["kind"] != a["kind"] and b["stage"] == a["stage"]
                         and abs(b["price"] - a["price"]) <= MERGE_PT for b in lv)
    return lv, bands


def judge_touches(lv, cs):
    """첫 터치 → 되돌림/돌파/정거장 (사전 고정 규칙). 진행 중이면 '진행중'."""
    T = [c[0] for c in cs]
    for L in lv:
        L.update(touch=None, approach=None, outcome=None, resolve=None, stay=None)
        idx0 = [i for i, t in enumerate(T) if t >= L["start"]]
        if not idx0 or idx0[0] == 0:
            continue
        for i in range(idx0[0], len(cs)):
            lo_, hi_ = cs[i][3], cs[i][2]
            if not (lo_ <= L["price"] <= hi_):
                continue
            prev = cs[i - 1][4]
            if abs(prev - L["price"]) < 1e-9:
                continue
            ap = "▲" if prev < L["price"] else "▼"
            s = 1 if ap == "▲" else -1
            L.update(touch=T[i], approach=ap)
            out = res = None
            end = min(len(cs), i + TOUCH_WIN + 1)
            for j in range(i, end):
                beyond = (cs[j][2] - L["price"]) if s > 0 else (L["price"] - cs[j][3])
                back = (L["price"] - cs[j][3]) if s > 0 else (cs[j][2] - L["price"])
                if beyond >= TOUCH_X and back >= TOUCH_X:
                    out = "돌파" if s * (cs[j][4] - L["price"]) > 0 else "되돌림"; res = T[j]; break
                if beyond >= TOUCH_X:
                    out, res = "돌파", T[j]; break
                if back >= TOUCH_X:
                    out, res = "되돌림", T[j]; break
            if out is None:
                out = "정거장" if end - i == TOUCH_WIN + 1 else "진행중"
            L.update(outcome=out, resolve=res,
                     stay=sum(1 for j in range(i, end) if abs(cs[j][4] - L["price"]) <= TOUCH_X))
            break
    return lv


# ── 피터 — 대시보드 파서를 그대로 재사용(소스에서 정의만 뽑아 실행) ──────────
_peter_ns = None


def _peter_parser():
    global _peter_ns
    if _peter_ns is not None:
        return _peter_ns
    src_path = os.path.join(ROOT, "dashboard", "main_dashboard.py")
    src = open(src_path, encoding="utf-8").read()
    tree = ast.parse(src)
    want = {"parse_peter_text", "_pt_tweet_time", "parse_peter_orders", "parse_peter_trades"}
    chunks = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name in want:
            chunks.append(ast.get_source_segment(src, n))
        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
            tg = n.targets if isinstance(n, ast.Assign) else [n.target]
            if any(isinstance(t, ast.Name) and t.id.startswith(("PETER_", "_PT_")) for t in tg):
                chunks.append(ast.get_source_segment(src, n))
    ns = {"re": re}
    exec("\n\n".join(chunks), ns)
    _peter_ns = ns
    return ns


def peter(day, lv):
    out = dict(offset=None, trades=[], excluded=[], notes=[], available=False)
    try:
        con = _ro("peter_levels.db")
        row = con.execute("SELECT offset, raw_lv, raw_tr FROM peter_paste WHERE date=?", (day,)).fetchone()
        con.close()
    except Exception:
        row = None
    if not row:
        return out
    off, raw_lv, raw_tr = row
    ns = _peter_parser()
    orders, results, aux, unknown = ns["parse_peter_orders"](raw_lv or "", off, day)
    trades, _err = ns["parse_peter_trades"](raw_tr or "", off, day)
    KO = {"entry_sell": "매도 진입", "entry_buy": "매수 진입", "stop": "손절", "target": "청산가"}
    seen = set()
    out.update(offset=off, available=True)

    def add(kind, adj, raw_px, hm, raw, tag, parsed=True):
        if not hm:
            return
        if "코스닥" in raw or not (adj and 900 <= adj <= 1400):
            out["excluded"].append(dict(hm=hm, raw=raw, why="코스닥150 등 다른 상품" if "코스닥" in raw else "가격 범위 밖"))
            return
        key = (kind, round(adj, 2))
        if key in seen:
            return
        seen.add(key)
        lv.append(dict(stage="peter", start=_hm_next(hm), kind="피터", price=round(adj, 2), raw_px=raw_px, hm=hm, tag=tag,
                       pkind=KO.get(kind, kind), parsed=parsed, side=None, merge=False, src=raw,
                       label="%s %g (%s%s)" % (KO.get(kind, kind), raw_px, hm, " " + tag if tag else "")))

    for o in orders:
        add(o["kind"], o["entry"], o["entry_raw"], o["hm"], o["raw"], o["tag"])
        if o["stop"] is not None:
            add("stop", o["stop"], o["stop"] - off, o["hm"], o["raw"], o["tag"])
        if o["target"] is not None:
            add("target", o["target"], o["target"] - off, o["hm"], o["raw"], o["tag"])
    for a in aux:
        for mk in a["marks"]:
            add(mk["kind"], mk["level_adj"], mk["level"], a["hm"], a["raw"], a["tag"])
    for u in unknown:
        m = re.search(r"손절가[^\d]{0,12}(\d{4})\s*$", u["raw"])
        if m:
            add("stop", float(m.group(1)) + off, float(m.group(1)), u["hm"], u["raw"], "미분류", parsed=False)
        if "막혀" in u["raw"] or "뚫" in u["raw"]:
            out["notes"].append(dict(hm=u["hm"], raw=u["raw"]))
    for p in [L for L in lv if L["kind"] == "피터"]:
        p["near"] = sorted({"%s %s" % (b["kind"], b["price"]) for b in lv
                            if b["kind"] in ("구조", "거리") and abs(b["price"] - p["price"]) <= MERGE_PT})
    out["trades"] = [dict(t, entry_ts=str(t.get("entry_ts")), exit_ts=str(t.get("exit_ts"))) for t in trades]
    return out


# ── 행사가 OI · 베이시스 ──────────────────────────────────────────────────
BOOK_MIN_SNAPS = 20      # 미륵이 option_book 유효 스냅샷이 이보다 적으면 메시아 체인으로 대신한다
_BOOK_KO = {"monthly": "먼스리", "weekly_mon": "월위클리", "weekly_thu": "목위클리"}


def _load_book(dbname, day):
    """→ (snaps[(hm, book, spot, call_wall, put_wall, n_valid, expiry)], strikes[(hm, book, k, call_oi, put_oi)])."""
    if not os.path.exists(os.path.join(DB, dbname)):
        return [], []
    con = _ro(dbname)
    try:
        snaps = con.execute(
            "SELECT substr(ts,12,5), book, spot, call_wall, put_wall, n_valid, expiry FROM option_book_snap"
            " WHERE ts LIKE ? ORDER BY ts", (day + "%",)).fetchall()
        strikes = con.execute(
            "SELECT substr(ts,12,5), book, strike, call_oi, put_oi FROM option_book_strike WHERE ts LIKE ?",
            (day + "%",)).fetchall()
    finally:
        con.close()
    return snaps, strikes


def _grid(rows, sn, times):
    ks = sorted({r[2] for r in rows})
    grid = {(r[0], r[2]): (r[3], r[4]) for r in rows}
    call, put = [], []
    for k in ks:
        lc = lp = 0
        rc, rp = [], []
        for t in times:
            v = grid.get((t, k))
            if v is not None:
                lc, lp = int(v[0] or 0), int(v[1] or 0)
            rc.append(lc); rp.append(lp)
        first = next((i for i, t in enumerate(times) if (t, k) in grid), None)   # 첫 관측 전은 첫 값으로(bfill)
        if first:
            rc[:first] = [rc[first]] * first; rp[:first] = [rp[first]] * first
        call.append(rc); put.append(rp)
    sv = [s for s in sn if (s[5] or 0) > 0]
    return dict(strikes=ks, call=call, put=put, times=times, expiry=sv[-1][6] if sv else None,
                wall_open=[sv[0][3], sv[0][4]] if sv else None, wall_close=[sv[-1][3], sv[-1][4]] if sv else None)


def books(day, cs):
    """상품별로 원천을 고른다 — 미륵이 option_book(2026-09-23 14:34~) 우선, 부족하면 메시아 체인.

    상품마다 스냅샷 시각이 다르므로(미륵이 :01·:06… / 메시아 5분 칸) 각자 `times` 를 갖는다.
    """
    srcs = {"option_book.db": "미륵이 option_book", "option_book_fuo.db": "메시아 KIS 체인"}
    loaded = {db: _load_book(db, day) for db in srcs}
    cmap = {c[0]: c[4] for c in cs}
    out, used = {}, {}
    for bk in ("monthly", "weekly_mon", "weekly_thu"):
        pick = None
        for db in srcs:
            sn = [x for x in loaded[db][0] if x[1] == bk]
            valid_t = {x[0] for x in sn if (x[5] or 0) > 0}
            rows = [r for r in loaded[db][1] if r[1] == bk]
            if rows and valid_t:
                cand = (db, sn, rows, len(valid_t))
                if len(valid_t) >= BOOK_MIN_SNAPS:
                    pick = cand; break
                if pick is None or cand[3] > pick[3]:
                    pick = cand
        if pick is None:
            out[bk] = dict(strikes=[], call=[], put=[], times=[], wall_open=None, wall_close=None, expiry=None,
                           absent=True, src=None, absent_reason="이 날 상장·수집된 %s 종목이 없다" % _BOOK_KO[bk])
            continue
        db, sn, rows, nvt = pick
        times = sorted({r[0] for r in rows})
        out[bk] = _grid(rows, sn, times)
        out[bk]["src"] = "%s (%d스냅샷)" % (srcs[db], nvt)
        used[bk] = sn
    # 베이시스 = 선물 − KOSPI200, 먼스리 원천 우선
    for bk in ("monthly", "weekly_mon", "weekly_thu"):
        bas = sorted(cmap[x[0]] - x[2] for x in used.get(bk, []) if x[0] in cmap and x[2])
        if bas:
            return out, out["monthly"].get("times", []), round(bas[len(bas) // 2], 2)
    return out, out["monthly"].get("times", []), None


# ── 7222 주체 흐름 ────────────────────────────────────────────────────────
FLOW_PRODUCTS = ("mon_call", "mon_put", "wk_mon_call", "wk_mon_put", "wk_thu_call", "wk_thu_put")


def flow1m(day):
    """7222 주체별 누적 순매수 — (mins, 계약수, 마지막 바, 금액).
    [678차 후속] 금액(`net_amt`, 백만원)도 함께 낸다 — 화면 옵션 수급 띠의 계약수/금액 토글용.
    신동2 v2 규칙은 금액으로 판정하므로, 계약수만 보이면 화면과 규칙이 다른 값을 보게 된다."""
    mins = ["%02d:%02d" % (h, m) for h in range(8, 17) for m in range(60)]
    mins = [m for m in mins if "08:45" <= m <= "16:10"]
    con = _ro("option_flow.db")
    try:
        rows = con.execute("SELECT bar_time, product, investor, net_qty, net_amt FROM option_investor_flow WHERE trade_date=?",
                           (day,)).fetchall()
    finally:
        con.close()
    gq, ga = {}, {}
    for t, p, i, q, a in rows:
        gq.setdefault((p, i), {})[t] = q
        ga.setdefault((p, i), {})[t] = a
    last_bar = max((r[0] for r in rows), default=None)

    def series(g):
        out = {}
        for p in FLOW_PRODUCTS:
            out[p] = {}
            for i in ("foreign", "individual", "institution"):
                d = g.get((p, i))
                if not d:
                    out[p][i] = None
                    continue
                # 누적값이라 수신 사이 빈 분은 앞 값을 잇는다. 단 그날 마지막 수신분(last_bar) 뒤는
                # 받지 않은 미래다 — 이어 붙이면 장중 띠가 16:10 까지 평평하게 뻗는다(계측 4원칙 ④).
                last, arr = None, []
                for m in mins:
                    if m in d:
                        last = d[m]
                    arr.append(last if last_bar is not None and m <= last_bar else None)
                out[p][i] = arr if any(v is not None for v in arr) else None   # 전부 결측 = 미측정(0 아님)
        return out
    return mins, series(gq), last_bar, series(ga)


# ── 선물 투자자 순매수 (7221, raw_investor_futures) ─────────────────────────
# [656차 후속4 / 2026-10-06] 옵션 흐름과 같은 시간축에 「선물 외인 누적」 띠를 그린다.
#   값은 일중 누계(계약, 정규 K200 선물 · 승수 25만)이며 09:02 부터 매분(09:00–01 은 의도적 스킵).
#   7222 흐름(flow1m)과 달리 **앞 값을 이어 붙이지 않는다** — 받지 않은 분은 None(계측 4원칙 ②).
#   장중에는 마지막으로 받은 ts 이후만 PK 범위로 증분 조회한다(456차, 하루 약 390행).
FUT_INV = (("foreign", "foreign_net_qty"), ("institution", "institution_net_qty"), ("individual", "retail_net_qty"))
_fut_cache = {}           # day -> {"rows": {hm: {inv: qty}}, "src": set(), "last_ts": str|None}
_fut_lock = threading.Lock()


def futflow(day, mins):
    """→ (series {inv: [qty|None] × mins}, last_hm, src) — 행이 없으면 ({}, None, None)."""
    with _fut_lock:
        c = _fut_cache.setdefault(day, {"rows": {}, "src": set(), "last_ts": None})
        lo = c["last_ts"] or (day + " 08:45:00")
        con = _ro("raw_data.db")
        try:
            new = con.execute(
                "SELECT ts, fields, src FROM raw_investor_futures WHERE ts >= ? AND ts <= ? ORDER BY ts",
                (lo, day + " 15:35:59")).fetchall()
        finally:
            con.close()
        for ts, fj, src in new:
            try:
                f = json.loads(fj)
            except Exception:
                continue
            c["rows"][ts[11:16]] = {inv: f.get(k) for inv, k in FUT_INV}
            c["src"].add(src or "live")
        if new:
            c["last_ts"] = new[-1][0]
        rows, srcs = c["rows"], sorted(c["src"])
    if not rows:
        return {}, None, None
    series = {}
    for inv, _ in FUT_INV:
        arr = [rows[m][inv] if m in rows else None for m in mins]
        if any(v is not None for v in arr):
            series[inv] = arr
    return series, max(rows), "+".join(srcs)


# ── 신동2 시점별 제안 (scripts/foreign_flow_pit_review.py) ─────────────────────
# [662차 후속 / 2026-10-06] 규칙·채점은 스크립트가 단일 출처다 — 여기서는 원천을 넘기고 결과만 싣는다.
#   장중에는 **완결된 봉만** 넘긴다(덜 찬 마지막 봉의 종가로 돌파 체결을 판정하면 다음 갱신에 뒤집힌다).
#   7221 은 futflow 캐시를 그대로 쓴다 — raw_data.db 를 다시 읽지 않는다(456차).
_SD2 = None


def _sd2_mod():
    global _SD2
    if _SD2 is None:
        import importlib.util
        p = os.path.join(ROOT, "scripts", "foreign_flow_pit_review.py")
        spec = importlib.util.spec_from_file_location("foreign_flow_pit_review", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _SD2 = m
    return _SD2


_SD2L = None


def _sd2_live_mod():
    global _SD2L
    if _SD2L is None:
        import importlib.util
        p = os.path.join(ROOT, "scripts", "shindong2_live.py")
        spec = importlib.util.spec_from_file_location("shindong2_live", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _SD2L = m
    return _SD2L


def shindong2_ai(day, cs, live):
    """「신동2 해설」 패널 — Claude 재량 기록(ai_log)·최신 해설·이벤트·재량 채점. 파일이 없으면 None(미기록 ≠ 0)."""
    M = _sd2_live_mod()
    d = os.path.join(M.LIVE_DIR, day.replace("-", ""))
    if not os.path.isdir(d):
        return None
    log = M._read_jsonl(os.path.join(d, "ai_log.jsonl"))
    ev = M._read_jsonl(os.path.join(d, "events.jsonl"))
    # [MW0602 614차 후속2] legacy(기존방식 섀도)는 최신 해설이 아니다 — `_next_plan` 과 같은 거름.
    # 종전 `log[-1]` 은 장후에 섀도를 마지막에 남기면(SKILL 절차대로) 패널이 섀도를 최신으로 띄웠다(10/12 실측).
    _live = [r for r in log if (r.get("variant") or "live") == "live"]
    latest = _live[-1] if _live else None
    bars = [list(c) for c in (cs[:-1] if live else cs)]
    sim = M.simulate_ai(day, bars, log, live=live) if (log and bars) else None
    # [683차] 확률 시나리오 — 그날 live 기록에 달린 세트의 실현·무효·진행(장중 잠정). 실패해도 패널은 그린다.
    scen, scen_err = [], None
    if log and bars and hasattr(M, "scenario_sets"):
        try:
            scen = M.scenario_sets(day, bars, log, final=not live)
        except Exception as e:                       # 미측정 ≠ 0 — 사유를 남긴다
            scen_err = str(e)[:200]
    st = _state_json(d)
    return dict(latest=latest, log=log, events=ev[-40:], events_n=len(ev), sim=sim, next_plan=_next_plan(M, day),
                learning=_learning(M, d), scen=scen, scen_err=scen_err,
                source_warnings=(st or {}).get("source_warnings") or [], state_at=(st or {}).get("generated_at"),   # [640차 ⑤]
                plain=plain_lines(day, cs, live, st, latest, sim))


def _state_json(d):
    try:
        with open(os.path.join(d, "state.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def plain_lines(day, cs, live, st, latest, sim):
    """[640차 ⑤] 중학생 설명 층 — 「지금 시장은 / 상대(MAIN)는 지금 / AI 생각은」 세 문장. 숫자는 사다리 봉·state.json·shindong.db 에서만.
    없는 것은 「모른다」고 쓴다(미측정 ≠ 0)."""
    bars = [list(c) for c in (cs[:-1] if live else cs)]
    out = dict(market=None, rival=None, ai=None)
    if bars:
        o, px = bars[0][1], bars[-1][4]
        hi, lo = max(c[2] for c in bars), min(c[3] for c in bars)
        d = px - o
        where = "시가보다 %.2f 위" % d if d > 0 else "시가보다 %.2f 아래" % -d if d < 0 else "시가 자리"
        pv = (st or {}).get("prev") or {}
        pvs = ""
        stale = any("전일 참조 고착" in w for w in (st or {}).get("source_warnings") or [])
        if pv.get("close") and stale:
            pvs = " 전날 값은 낡아서(%s) 비교하지 않는다." % pv.get("date")
        elif pv.get("close"):
            pvs = " 전날 마감(%.2f)보다 %s." % (pv["close"], "높다" if px > pv["close"] else "낮다" if px < pv["close"] else "같다")
        f = (st or {}).get("flow") or {}
        ff = f.get("fut_foreign")
        fs = ""
        if ff is not None:
            fs = " 외국인은 선물을 오늘 %s계약 %s." % (format(abs(int(ff)), ","), "사 모았다(매수)" if ff > 0 else "팔았다(매도)" if ff < 0 else "순매수 0")
        out["market"] = "%s 현재 %.2f — %s(시가 %.2f · 오늘 범위 %.2f–%.2f).%s%s" % (bars[-1][0], px, where, o, lo, hi, pvs, fs)
    rv = (st or {}).get("rival") or {}
    if rv.get("present"):
        m = rv["main"]
        n = m["n"]
        if n == 0:
            core = "MAIN(기본 규칙)은 오늘 아직 거래하지 않았다"
        else:
            t0 = m["trades"][0]
            core = "MAIN(기본 규칙)은 %s에 %s로 들어가 지금까지 %d번 거래해 %s%.2fpt" % (
                t0["entry_t"], t0["side_ko"], n, "+" if (m["pnl_pt"] or 0) >= 0 else "", m["pnl_pt"] or 0)
        op = m.get("open")
        hold = (" · 지금 %s 포지션 보유(평가 %+.2fpt)" % (op["side_ko"], op["eval_pt"])) if op and op.get("eval_pt") is not None else " · 지금 포지션 없음"
        sg = rv.get("signals") or {}
        see = ""
        fc = sg.get("flowc")
        if fc:
            see = " 상대가 보는 것: 개인이 위클리 옵션에서 콜을 %s(09:00 대비 %+.0f백만, 문턱 ±%d → %s)." % (
                "더 샀다" if fc["dv"] > 0 else "덜 샀다(풋 우위)" if fc["dv"] < 0 else "비슷하게", fc["dv"], fc["k"],
                ("MAIN 은 " + fc["side"] + " 쪽") if fc["side"] else "아직 신호 없음")
        out["rival"] = core + hold + "." + see
    if latest:
        vs = {"agree": "상대와 같은 생각", "disagree": "상대와 반대", "abstain": "판단 보류"}.get(latest.get("vs_main"))
        dirk = latest.get("dir") or "관망"
        plan = ""
        if dirk in ("매수", "매도"):
            plan = " %s — 진입 %s · 손절 %s · 목표 %s" % (dirk, latest.get("entry") if latest.get("entry") is not None else "시장가", latest.get("stop"), latest.get("target"))
        else:
            plan = " 관망(들어가지 않는다)"
        first = ((latest.get("comment") or "").strip().splitlines() or [""])[0][:140]
        fr = latest.get("fresh") or {}
        stale = ""                                   # [670차 후속 P3] 판단 근거가 기록 시점에 이미 낡았으면 그 사실을 같이 보인다
        if fr.get("grade") == "moved" or (not fr.get("grade") and (fr.get("new_hi") or fr.get("new_lo"))):
            bits = [s for s in (("고 %.2f" % fr["new_hi"]) if fr.get("new_hi") else "", ("저 %.2f" % fr["new_lo"]) if fr.get("new_lo") else "",
                                ("레벨 " + ", ".join(fr["level_hit"])) if fr.get("level_hit") else "") if s]
            stale = " ⏱ 이 판단은 %s 봉을 보고 썼다 — 기록 때(%s)는 이미 %s" % (fr.get("snap_bar"), fr.get("rec_bar"), " · ".join(bits))
        out["ai"] = "AI 는 %s 기준으로%s%s. 한 줄 이유: %s%s%s" % (
            latest["ts"][11:16], plan, (" · " + vs + ((" — " + latest["vs_why"]) if latest.get("vs_why") else "")) if vs else "", first,
            (" · 오늘 AI 재량 %+.2fpt" % sim["pnl"]) if sim else "", stale)
    return out


def _learning(M, d):
    """[672차] 학습 사이클 — 그날 계획 평가(eval.json)·피드백(feedback.json)·워크포워드 추이(trend.json)·활성 레슨 수.
    파일이 없으면 키를 비운다(미기록 ≠ 0)."""
    out = {}

    def _j(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None
    e = _j(os.path.join(d, "eval.json"))
    if e:
        out["eval"] = e
    fb = _j(os.path.join(d, "feedback.json"))
    if fb:
        out["feedback"] = dict(ts=fb.get("ts"), applied=fb.get("applied"), hits=fb.get("hits"), misses=fb.get("misses"),
                               comment=fb.get("comment", ""))
    t = _j(os.path.join(M.LIVE_DIR, "trend.json"))
    if t:
        out["trend"] = dict(generated_at=t.get("generated_at"), verdict=t.get("verdict"), windows=t.get("windows"))
    learn_dir = os.environ.get("SHINDONG2_LEARN_DIR") or os.path.join(ROOT, "docs", "미륵이고도화3", "신동2", "학습")
    ls = _j(os.path.join(learn_dir, "lessons_%s.json" % _pc_id()))   # [MW0602 614차 후속] PC별 레지스트리
    if ls is not None:
        out["lessons_active"] = sum(1 for l in ls if l.get("status") in ("적용중", "검증"))
        out["lessons_n"] = len(ls)
    return out or None


def _next_plan(M, day):
    """그날 장후에 다음 거래일 파일로 미리 적은 계획(phase=overnight) — 그날 화면에도 보여 준다.

    기록은 설계대로 다음 날 폴더(--for-date)에 있다. 다음 날 폴더 중 가장 가까운 것에서
    **그날 작성된** overnight 기록만 고른다(다음 날 장중 기록은 섞지 않는다).
    """
    key = day.replace("-", "")
    try:
        later = sorted(d for d in os.listdir(M.LIVE_DIR) if d.isdigit() and len(d) == 8 and d > key)
    except OSError:
        return None
    for d in later:
        recs = [r for r in M._read_jsonl(os.path.join(M.LIVE_DIR, d, "ai_log.jsonl"))
                if r.get("phase") == "overnight" and str(r.get("ts", ""))[:10] == day
                and (r.get("variant") or "live") == "live"]            # 672차 — legacy 섀도는 패널에 안 올린다
        if recs:
            # [683차] 계획 칸은 마지막 plan/stand 를 보여 준다 — 뒤에 붙은 시나리오 note 가 계획을 「관망」으로 가리지 않게.
            plans = [r for r in recs if r.get("action") in ("plan", "stand")]
            sc = [r for r in recs if r.get("scenarios")]
            return dict(for_date="%s-%s-%s" % (d[:4], d[4:6], d[6:]), latest=(plans or recs)[-1], n=len(recs),
                        scen=sc[-1] if sc else None)
    return None


def _pc_id():
    """이 PC 식별자 — `utils/db_utils.py:pc_id()` 가 호스트명에서 뽑는다.

    🔴 종전에는 `ladder.html` 에 `MW0601` 이 **하드코딩**돼 있어 MW0602 에서도
       MW0601 로 찍혔다. 2026-10-06 에 실제로 사고가 났다 — 세션이 브라우저로 사다리를
       보며 「이 PC 화면」이라고 판단했는데 그것이 다른 PC 의 사다리였고, 같은 날짜의
       손익이 `10.87`(저쪽) vs `5.28`(이쪽)로 갈린 것을 **같은 서버의 비결정성으로
       오진**했다. 화면에 PC 가 박혀 있었으면 첫 화면에서 끝났을 혼선이다.

    `pc_id()` 의 독스트링도 「config 상수로 두지 않는 이유는 PC별로 다른 값을 git 에
    커밋할 수 없기 때문」이라고 못박고 있다 — 그 함수를 그대로 쓴다. 실패하면
    호스트명, 그마저 안 되면 "UNKNOWN" 이다(미측정을 0 으로 위장하지 않는다).
    """
    try:
        import sys as _s, os as _o
        _r = _o.path.dirname(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))))
        if _r not in _s.path:
            _s.path.insert(0, _r)
        from utils.db_utils import pc_id as _f
        return _f()
    except Exception:
        try:
            import platform as _pf
            return (_pf.node() or "UNKNOWN")[:32]
        except Exception:
            return "UNKNOWN"


def rival(day, cs, live):
    """[MW0602 640차] 「상대의 수」 — 신동 v3 MAIN·섀도 5종(shindong.db 하루치). 사다리 패널·차트 마커가 읽는다.
    DB/행이 없으면 present=False 와 사유(미기록 ≠ 0). 456차 — PK 조회 두 개뿐."""
    M = _sd2_live_mod()                                   # scripts/ 경로가 sys.path 에 실린다
    import importlib.util
    p = os.path.join(ROOT, "scripts", "shindong2_rival.py")
    spec = importlib.util.spec_from_file_location("shindong2_rival", p)
    RV = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(RV)
    bars = [list(c) for c in (cs[:-1] if live else cs)]
    return RV.read_day(day, last_close=bars[-1][4] if bars else None, live=live)


def shindong2(day, cs, live):
    R = _sd2_mod()
    bars = [list(c) for c in (cs[:-1] if live else cs)]
    c = _fut_cache.get(day) or {"rows": {}}
    fut = [(hm, v.get("foreign"), v.get("institution"), v.get("individual")) for hm, v in sorted(c["rows"].items())]
    S = R.load(day, cs=bars, fut=fut)
    out = R.analyze(S, live=live)
    out["peter"] = R.peter_trades(day)
    return out


# ── [9842] 내보내기 파일 (표준 라이브러리 파서) ─────────────────────────────
_9842_COLS = ["c_inv_trust", "c_fin", "c_for", "c_ind", "c_px", "k", "p_px", "p_ind", "p_for", "p_fin", "p_inv_trust"]


def _list_9842_files():
    """option_hts 폴더의 [9842] 내보내기 목록.

    이름 규칙: YYMMDD[_HHMM][_D|_P].xls(x)
      YYMMDD_D   — 그날 당일 순매수(마감본 또는 P 차분 생성본)
      YYMMDD_P   — 기간 보유(누적)
      YYMMDD_HHMM_D — 장중 HH:MM 에 내보낸 당일 순매수 **시점 파일**(656차 후속, 30분 모니터용)
    hm 은 시점 파일이면 'HH:MM', 아니면 None.
    """
    out = []
    if not os.path.isdir(DOCS_9842):
        return out
    for fn in os.listdir(DOCS_9842):
        m = re.match(r"^(\d{6})(?:_(\d{4}))?(?:_([DP]))?\.(xlsx|xls)$", fn)
        if not m:
            continue
        yymmdd, hhmm, mode, ext = m.groups()
        if hhmm and not (hhmm[:2] <= "23" and hhmm[2:] <= "59"):
            continue
        if hhmm:                          # 시점 파일은 당일 순매수만 뜻이 있다 — _D 를 빠뜨려도 D, _P 면 버린다
            if mode == "P":
                continue
            mode = "D"
        else:
            mode = mode or LEGACY_9842_MODE.get(yymmdd)
        out.append(dict(fn=fn, yymmdd=yymmdd, date="20%s-%s-%s" % (yymmdd[:2], yymmdd[2:4], yymmdd[4:]),
                        mode=mode, ext=ext, hm=("%s:%s" % (hhmm[:2], hhmm[2:]) if hhmm else None)))
    return out


def _read_xlsx(path):
    z = zipfile.ZipFile(path)
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])))
    sheet = sorted(n for n in z.namelist() if n.startswith("xl/worksheets/sheet"))[0]
    rows = []
    for r in ET.fromstring(z.read(sheet)).iter("{%s}row" % ns["m"]):
        vals = {}
        for c in r.findall("m:c", ns):
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            v = c.find("m:v", ns)
            txt = None
            if c.get("t") == "s" and v is not None:
                txt = shared[int(v.text)]
            elif c.get("t") == "inlineStr":
                txt = "".join(t.text or "" for t in c.iter("{%s}t" % ns["m"]))
            elif v is not None:
                txt = v.text
            ci = 0
            for ch in col:
                ci = ci * 26 + (ord(ch) - 64)
            vals[ci - 1] = txt
        rows.append([vals.get(i) for i in range(max(vals) + 1)] if vals else [])
    return rows


class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self._row, self._cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = ""

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._row is not None and self._cell is not None:
            self._row.append(self._cell.strip()); self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row); self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell += data


def _read_xls_html(path):
    p = _TableParser()
    p.feed(open(path, "rb").read().decode("euc-kr", errors="replace"))
    return p.rows


def _num(x):
    try:
        return float(str(x).replace(",", ""))
    except Exception:
        return None


# 머리행 이름 → 주체 키. HTS 화면 열 구성이 바뀌어도(2026-10-02 투신 → 2026-10-04 기관계)
# **위치가 아니라 이름으로** 찾는다 — 위치로 읽으면 기관계가 투신 칸에 들어가 금투와 이중으로 더해진다.
_9842_NAME = {"기관계": "ins", "투신": "inv_trust", "금융투자": "fin", "외국인": "for", "개인": "ind", "현재가": "px"}


def read_9842_meta(path):
    """→ (rows: {strike(str): {c_for, c_ind, c_fin, c_ins, p_*, …}}, unit, note)

    unit: 'contract'(계약 — 값이 전부 정수) | 'krw_eok'(금액 — 십만원 ÷ 1000 = 억원, 단위 추정).
    파일 안에 단위 표시가 없다. 2026-10-02 실측: 금액 내보내기는 소수점(891.25)이 섞이고
    계약 내보내기는 전부 정수다. 그래서 **소수점이 하나라도 있으면 금액**으로 본다.
    """
    rows = _read_xlsx(path) if path.endswith(".xlsx") else _read_xls_html(path)
    head = [str(h or "").strip() for h in rows[0][:11]] if rows else []
    if len(head) < 11 or head[5] != "행사가":
        raise ValueError("머리행이 [9842] 배치가 아니다: %s" % head)
    left = [_9842_NAME.get(h) for h in head[:5]]          # 콜 쪽(왼쪽 → 행사가)
    right = [_9842_NAME.get(h) for h in head[6:11]]       # 풋 쪽(행사가 → 오른쪽)
    unknown = [h for h, k in zip(head[:5] + head[6:11], left + right) if k is None]
    if unknown:
        raise ValueError("모르는 열 이름: %s" % unknown)
    raw = []
    for r in rows[1:]:
        if len(r) < 11 or _num(r[5]) is None:
            continue
        c = {"c_" + k: _num(x) for k, x in zip(left, r[:5])}
        c.update({"p_" + k: _num(x) for k, x in zip(right, r[6:11])})
        raw.append((_num(r[5]), c))
    vals = [v for _, c in raw for k, v in c.items() if not k.endswith("_px") and v is not None]
    unit = "contract" if vals and all(float(v).is_integer() for v in vals) else "krw_eok"
    scale = 1.0 if unit == "contract" else 1 / 1000.0
    out = {}
    for k, c in raw:
        d = {}
        for side in ("c", "p"):
            for who in ("for", "ind", "fin", "ins", "inv_trust"):
                v = c.get("%s_%s" % (side, who))
                if v is not None:
                    d["%s_%s" % (side, who)] = round(v * scale, 3)
            if "%s_ins" % side not in d:          # 기관계 열이 없던 옛 배치 — 금투+투신으로 근사
                d["%s_ins" % side] = round(d.get("%s_fin" % side, 0.0) + d.get("%s_inv_trust" % side, 0.0), 3)
        out[str(float(k))] = d
    note = "기관 = 기관계" if "ins" in left else "기관 ≈ 금융투자+투신(기관계 열 없음)"
    return out, unit, note


def read_9842(path):
    """하위호환 — 값 dict 만."""
    return read_9842_meta(path)[0]


_9842_cache = {}          # path → ((mtime, size), result) — 시점 파일을 매분 다시 파싱하지 않는다
_SNAP_KEYS = ("c_for", "p_for", "c_ind", "p_ind", "c_ins", "p_ins")


def _read_9842_cached(path):
    st = os.stat(path)
    sig = (st.st_mtime, st.st_size)
    hit = _9842_cache.get(path)
    if hit and hit[0] == sig:
        return hit[1]
    res = read_9842_meta(path)
    _9842_cache[path] = (sig, res)
    return res


def _is_prev_trading_day(hold_day, day):
    """hold_day 가 day 의 **직전 거래일**인가 — 그래야 보유(P) + 당일(D) = 현재 보유가 정확하다.

    사이에 거래일이 끼면(그날 _P 를 못 받음) 합은 그 날들의 순매수를 빠뜨린다.
    KRX 달력(utils.time_utils)을 못 읽으면 None(미측정) — 거짓 True 로 두지 않는다.
    """
    try:
        import sys
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        from utils.time_utils import is_trading_day
    except Exception:
        return None
    a = _dt.date.fromisoformat(hold_day); b = _dt.date.fromisoformat(day)
    x = a + _dt.timedelta(days=1)
    while x < b:
        if is_trading_day(_dt.datetime.combine(x, _dt.time(12))):
            return False
        x += _dt.timedelta(days=1)
    return a < b


# ── [9842] API 수집본 (CpSvr9842 → strike_investor.db) ──────────────────────
# [MW0601 710차] HTS 수동 저장을 대신한다. API = HTS 같은 원천이다(704차 기간 모드 콜·풋 1,372/1,372칸 일치).
#   · 기간 보유(_P)  ← strike_investor_hold (장후 16:25 예약작업 — 15:45 종가 단일가 반영)
#   · 당일 순매수(_D) ← strike_investor_flow (장중 매분 「바뀐 행만」 — 재구성 규칙은 수집기 docstring)
# 둘 다 먼스리 최근월('1')만, 단위는 계약. 파일은 지우지 않는다 — 고르는 규칙은 hts9842() 참조.
STRIKE_DB = os.path.join(DB, "strike_investor.db")
# API 투자자 인덱스(collection/cybos/strike_investor_flow.INVESTORS) → 사다리 주체 키. 증권 = HTS 「금융투자」.
_API_WHO = (("ind", 0), ("for", 1), ("ins", 2), ("fin", 3), ("inv_trust", 5))
_DB_SNAP_MIN = 30          # 시점 칸 간격 — HTS 시점 파일(30분 모니터)과 같은 밀도
_db9842_cache = {}         # day → (sig, result) — 매분 다시 재구성하지 않는다


def _strike_ro():
    """없으면 None — 미러 PC(MW0602)에는 이 DB 가 없다."""
    if not os.path.exists(STRIKE_DB):
        return None
    return _ro(STRIKE_DB)                    # 절대경로라 DB 와 join 해도 그대로다


def _api_cells(cp, qty, keys=None):
    side = "c" if cp == "C" else "p"
    out = {}
    for who, i in _API_WHO:
        k = "%s_%s" % (side, who)
        if i < len(qty) and (keys is None or k in keys):
            out[k] = float(qty[i])
    return out


def _api_rows(items, keys=None):
    """[(cp, strike, qty)] → {str(strike): {c_for, …, p_for, …}}. 행사가 미매핑(None)은 빼고 개수를 돌려준다."""
    out, unmapped = {}, 0
    for cp, k, qty in items:
        if k is None:
            unmapped += 1
            continue
        out.setdefault(str(float(k)), {}).update(_api_cells(cp, qty, keys))
    return out, unmapped


def db9842_hold(day):
    """그날 이전 가장 최근 기간 보유. → dict(date, rows, unmapped) 또는 None(없음)."""
    con = _strike_ro()
    if con is None:
        return None
    try:
        r = con.execute("SELECT MAX(trade_date) FROM strike_investor_hold WHERE trade_date<? AND month='1'",
                        (day,)).fetchone()
        if not r or not r[0]:
            return None
        hd = r[0]
        items = [(cp, k, json.loads(q)) for cp, k, q in con.execute(
            "SELECT cp, strike, qty FROM strike_investor_hold WHERE trade_date=? AND month='1'", (hd,))]
    finally:
        con.close()
    # 콜·풋이 둘 다 있어야 한 장이다 — 한쪽만 있으면 반쪽 화면이 「다른 쪽 0」으로 읽힌다.
    if {cp for cp, _, _ in items} != {"C", "P"}:
        return None
    rows, unmapped = _api_rows(items)
    return dict(date=hd, rows=rows, unmapped=unmapped)


def _bucket_end(hm):
    """'09:31' → '10:00' — 그 분이 속한 30분 칸의 끝."""
    t = int(hm[:2]) * 60 + int(hm[3:])
    e = -(-t // _DB_SNAP_MIN) * _DB_SNAP_MIN
    return "%02d:%02d" % (e // 60, e % 60)


def db9842_flow(day):
    """그날 장중 당일 순매수 재구성. → dict(snaps=[{hm, rows}], last=dict(hm, rows), unmapped) 또는 None.

    측정된 시각만 쓴다 — 콜·풋 **둘 다** ok=1 이고, 그 시각 이전에 둘 다 전체 저장(full=1)이 있는 분.
    한도 부족으로 건너뛴 분(SKIP_QUOTA)·실패 분은 칸을 만들지 않는다(메우지 않는다 — 계측 4원칙 ②).
    시점 칸 = 30분 칸마다 마지막 측정 분 + 진행 중인 칸은 최신 측정 분. 이름표는 실제 수집 분이다.
    """
    con = _strike_ro()
    if con is None:
        return None
    try:
        st = con.execute("SELECT snap_hm, cp, full FROM strike_investor_flow_status "
                         "WHERE trade_date=? AND month='1' AND ok=1 ORDER BY snap_hm", (day,)).fetchall()
        if not st:
            return None
        sig = (len(st), st[-1][0])
        hit = _db9842_cache.get(day)
        if hit and hit[0] == sig:
            return hit[1]
        by_hm, base = {}, {}
        for hm, cp, full in st:
            by_hm.setdefault(hm, set()).add(cp)
            if full and cp not in base:
                base[cp] = hm
        if set(base) != {"C", "P"}:
            _db9842_cache[day] = (sig, None)
            return None
        start = max(base.values())
        good = [hm for hm in sorted(by_hm) if hm >= start and by_hm[hm] == {"C", "P"}]
        last_in = {}
        for hm in good:
            last_in[_bucket_end(hm)] = hm
        targets = sorted(last_in.values())
        rows = con.execute("SELECT snap_hm, cp, code, strike, qty FROM strike_investor_flow "
                           "WHERE trade_date=? AND month='1' AND snap_hm<=? ORDER BY snap_hm",
                           (day, targets[-1] if targets else "")).fetchall()
    finally:
        con.close()
    cur, snaps, i = {}, [], 0
    for t in targets:
        while i < len(rows) and rows[i][0] <= t:
            _, cp, code, k, q = rows[i]
            cur[(cp, code)] = (cp, k, q)
            i += 1
        items = [(cp, k, json.loads(q)) for cp, k, q in cur.values()]
        snaps.append(dict(hm=t, items=items))
    res = None
    if snaps:
        full_rows, unmapped = _api_rows(snaps[-1]["items"])
        res = dict(snaps=[dict(hm=s["hm"], rows=_api_rows(s["items"], _SNAP_KEYS)[0]) for s in snaps],
                   last=dict(hm=snaps[-1]["hm"], rows=full_rows), unmapped=unmapped)
    _db9842_cache[day] = (sig, res)
    return res


def db9842_dates():
    """API 수집본이 있는 날짜 — 날짜 목록의 9842 표식용. 없으면 빈 집합."""
    con = _strike_ro()
    if con is None:
        return set()
    try:
        a = {r[0] for r in con.execute("SELECT DISTINCT trade_date FROM strike_investor_flow_status WHERE ok=1")}
        b = {r[0] for r in con.execute("SELECT DISTINCT trade_date FROM strike_investor_hold")}
    finally:
        con.close()
    return a | b


def hts9842(day):
    """그날의 당일 순매수(D) 파일과, 그날 이전 가장 최근의 기간 보유(P) 파일.

    당일 순매수 고르는 순서: 시각 없는 YYMMDD_D(마감본·P 차분본) → 없으면 가장 늦은 시점 파일.
    시점 파일(YYMMDD_HHMM_D)은 flow_snaps 로 따로 돌려준다 — 화면이 직전 시점 대비 증감과
    행사가 × 시각 칸을 그린다. 읽기 실패한 시점은 빼고 flow_snaps_err 에 남긴다(메우지 않는다).

    [710차] API 수집본(strike_investor.db)을 함께 본다 — HTS 수동 저장이 없어도 화면이 선다.
      · 기간 보유: 파일 날짜와 DB 날짜 중 **늦은 쪽**, 같으면 **DB**. DB 는 16:25(종가 단일가 뒤)에 받고,
        파일은 15:45 전에 저장되는 날이 있다(2026-10-22 실측 34칸 차이 — 틀린 쪽은 파일).
      · 당일 순매수: 마감본 파일(YYMMDD_D)이 있으면 그것. 없으면 최신 시점 파일과 DB 최신 측정 분 중 늦은 쪽.
      · 시점 칸: 파일 시점 + DB 30분 칸(같은 분은 파일). 파일 시점이 금액 단위면 섞지 않는다(단위가 다르면
        화면이 증감을 못 그린다).
    """
    files = _list_9842_files()
    day_d = [f for f in files if f["date"] == day and f["mode"] == "D"]
    daily = [f for f in day_d if f["hm"] is None]
    snaps = sorted([f for f in day_d if f["hm"]], key=lambda f: f["hm"])
    hold_f = sorted([f for f in files if f["date"] < day and f["mode"] == "P"], key=lambda f: f["date"])
    res = dict(hold={}, flow={}, hold_src=None, flow_src=None, hold_unit=None, flow_unit=None,
               hold_date=None, hold_is_prev=None,
               flow_snaps=[], flow_snaps_err=[])
    derived = _derived_manifest()
    snap_ok = []
    for f in snaps:
        try:
            rows, unit, _ = _read_9842_cached(os.path.join(DOCS_9842, f["fn"]))
        except Exception as e:                       # HTS 가 아직 쓰는 중이거나 깨진 파일
            res["flow_snaps_err"].append("%s: %s" % (f["fn"], e))
            continue
        if not rows:
            res["flow_snaps_err"].append("%s: 행 없음" % f["fn"])
            continue
        snap_ok.append(f)
        res["flow_snaps"].append(dict(hm=f["hm"], fn=f["fn"], unit=unit,
                                      rows={k: {x: v[x] for x in _SNAP_KEYS if x in v} for k, v in rows.items()}))
    dbh = dbf = None
    try:
        dbh = db9842_hold(day)
    except Exception as e:
        res["flow_snaps_err"].append("strike_investor.db 기간 보유 읽기 실패: %s" % e)
    try:
        dbf = db9842_flow(day)
    except Exception as e:
        res["flow_snaps_err"].append("strike_investor.db 당일 순매수 읽기 실패: %s" % e)
    db_src = lambda what, hm, unmapped: "strike_investor.db (%s · 계약 · 기관 = 기관계 · API %s%s)" % (
        what, hm, (" · 행사가 미매핑 %d행 제외" % unmapped) if unmapped else "")

    if dbf:
        f_units = {s["unit"] for s in res["flow_snaps"]}
        if f_units - {"contract"}:
            res["flow_snaps_err"].append("API 시점 %d개 생략 — 시점 파일이 금액 단위라 섞지 않는다" % len(dbf["snaps"]))
        else:
            have = {s["hm"] for s in res["flow_snaps"]}
            res["flow_snaps"] += [dict(hm=s["hm"], fn="strike_investor.db", unit="contract", rows=s["rows"])
                                  for s in dbf["snaps"] if s["hm"] not in have]
            res["flow_snaps"].sort(key=lambda s: s["hm"])

    flow_pick = daily[-1] if daily else (snap_ok[-1] if snap_ok else None)
    flow_from_db = bool(dbf) and not daily and (flow_pick is None or dbf["last"]["hm"] > flow_pick["hm"])
    if flow_from_db:
        flow_pick = None
        res["flow"], res["flow_unit"] = dbf["last"]["rows"], "contract"
        res["flow_src"] = db_src("당일 순매수", dbf["last"]["hm"] + " 수집", dbf["unmapped"])

    hold_pick = hold_f[-1] if hold_f else None
    hold_from_db = bool(dbh) and (hold_pick is None or dbh["date"] >= hold_pick["date"])
    if hold_from_db:
        hold_pick = None
        res["hold"], res["hold_unit"] = dbh["rows"], "contract"
        res["hold_src"] = db_src("기간 보유", "%s 장후" % dbh["date"], dbh["unmapped"])
        res["hold_date"] = dbh["date"]
        res["hold_is_prev"] = _is_prev_trading_day(dbh["date"], day)
    elif hold_f:
        res["hold_date"] = hold_f[-1]["date"]
        res["hold_is_prev"] = _is_prev_trading_day(hold_f[-1]["date"], day)
    for key, f in (("flow", flow_pick), ("hold", hold_pick)):
        if f:
            try:
                res[key], res[key + "_unit"], note = _read_9842_cached(os.path.join(DOCS_9842, f["fn"]))
                tag = " · P 차분 생성" if f["fn"] in derived else (" · %s 시점" % f["hm"] if f.get("hm") else "")
                res[key + "_src"] = "%s (%s · %s · %s%s)" % (
                    f["fn"], "기간 보유" if f["mode"] == "P" else "당일 순매수",
                    "계약" if res[key + "_unit"] == "contract" else "억원(추정)", note, tag)
            except Exception as e:
                res[key + "_src"] = "%s 읽기 실패: %s" % (f["fn"], e)
    return res


def _derived_manifest():
    try:
        with open(os.path.join(DOCS_9842, "_derived_D.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


# ── 하루치 조립 ───────────────────────────────────────────────────────────
_final_days = set()       # 정규봉 적재가 확인된 날 — 한 번 확정이면 다시 묻지 않는다


def regular_final(day):
    """[MW0601 723차 이식] 그날 정규봉(15:10 이후 · 종가 단일가 포함)이 적재됐는가 — 장후 「확정」의 데이터 판정.

    `collect_regular_futures.py` 는 장 마감 뒤(15:52)에만 적재하므로 행이 있으면 그날은 끝난 것이다.
    15:15 이후 봉을 요구하는 이유: 만기일은 15:20 마감이라 15:44 를 기준으로 삼으면 영원히 확정이 안 된다."""
    if day in _final_days:
        return True
    try:
        con = _ro("regular_candles.db")
        try:
            code = mini_code_for(con, day)
            r = con.execute("SELECT 1 FROM regular_candles WHERE code=? AND trade_date=? AND ts >= ? LIMIT 1",
                            (code, day, day + " 15:15:00")).fetchone() if code else None
        finally:
            con.close()
    except Exception:
        return False
    if r:
        _final_days.add(day)
    return bool(r)


def is_live(day, now=None):
    """장중이면 True — 덜 찬 마지막 봉을 빼고, 외인 경로를 완결 봉에서 자른다.

    🔴 [MW0601 723차 이식] 시계(16:15)만으로 판정하면 15:55 장후 실행이 「장중」으로 읽혀
       raw_candles(15:08 끝) − 덜 찬 봉 = **15:07** 에서 하루를 잘랐다. 7221 외인 선물은 15:34 까지,
       정규봉은 15:44 까지 적재돼 있었는데 읽지 않았다(MW0601 실측 10-12–10-27 매 거래일 · 10-15·10-19 외인 부호 반전).
       15:15 이후 정규봉이 적재됐으면 시각과 무관하게 확정이다."""
    now = now or _dt.datetime.now()
    if day != now.date().isoformat():
        return False
    if now.strftime("%H:%M") >= "15:15" and regular_final(day):
        return False
    try:
        import sys
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        from utils.time_utils import is_trading_day
        if not is_trading_day(now):
            return False
    except Exception:
        if now.weekday() >= 5:
            return False
    return "08:40" <= now.strftime("%H:%M") <= "16:15"


def build_day(day, now=None):
    now = now or _dt.datetime.now()
    live = is_live(day, now)
    warn = []
    try:
        cs, csrc = candles(day, live)
    except Exception as e:
        cs, csrc = [], "실패: %s" % e
    if not cs:
        warn.append("1분봉 없음 (%s)" % csrc)
    # [MW0601 723차 이식] 장 마감 뒤인데 정규봉이 없다 — 봉은 15:08, 외인 경로는 완결 봉에서 잘린 채다(계측 4원칙 ④)
    if day == now.date().isoformat() and now.strftime("%H:%M") >= "15:35" and not str(csrc).startswith("regular"):
        warn.append("정규봉 미적재(%s) — 봉 15:08·외인 선물 경로가 마감(15:34) 전에서 잘렸다. "
                    "마감 수치로 읽지 말 것(collect_regular_futures 15:52 확인)" % csrc)
    try:
        lv, bands = levels(day)
    except Exception as e:
        lv, bands = [], []
        warn.append("맥점 읽기 실패: %s" % e)
    try:
        pt = peter(day, lv)
    except Exception as e:
        pt = dict(offset=None, trades=[], excluded=[], notes=[], available=False)
        warn.append("피터 파싱 실패: %s" % e)
    judge_touches(lv, cs)
    try:
        bk, times, basis = books(day, cs)
    except Exception as e:
        bk, times, basis = {}, [], None
        warn.append("행사가 OI 읽기 실패: %s" % e)
    try:
        mins, f1m, flow_last, f1m_amt = flow1m(day)
    except Exception as e:
        mins, f1m, flow_last, f1m_amt = [], {}, None, {}
        warn.append("7222 흐름 읽기 실패: %s" % e)
    try:
        fut, fut_last, fut_src = futflow(day, mins)
    except Exception as e:
        fut, fut_last, fut_src = {}, None, None
        warn.append("선물 투자자 순매수 읽기 실패: %s" % e)
    if fut_src and fut_src != "live":
        warn.append("선물 투자자 순매수 원천 = %s (사후 역변환 백필 — 15:08 종료, 실측 아님)" % fut_src)
    try:
        sd2 = shindong2(day, cs, live) if cs else None
    except Exception as e:
        sd2 = None
        warn.append("신동2 계산 실패: %s" % e)
    try:
        sd2ai = shindong2_ai(day, cs, live)
    except Exception as e:
        sd2ai = None
        warn.append("신동2 해설 읽기 실패: %s" % e)
    try:
        rv = rival(day, cs, live)                             # [640차] 상대의 수 — 신동 v3 MAIN·섀도
    except Exception as e:
        rv = dict(present=False, why="읽기 실패: %s" % e, variants={})
        warn.append("신동 v3 MAIN·섀도 읽기 실패: %s" % e)
    h = hts9842(day)
    warn += ["9842 시점 파일 읽기 실패 — %s" % e for e in h["flow_snaps_err"]]
    actual = dict(high=max((c[2] for c in cs), default=None), low=min((c[3] for c in cs), default=None))
    return dict(date=day, live=live, generated_at=now.isoformat(timespec="seconds"),
                pc=_pc_id(),
                candles=cs, candle_src=csrc, levels=lv, bands=bands, basis=basis if basis is not None else 0.0,
                basis_measured=basis is not None, times=times, books=bk, mins=mins, flow1m=f1m, flow1m_amt=f1m_amt, flow_last=flow_last,
                fut=fut, fut_last=fut_last, fut_src=fut_src, shindong2=sd2, sd2ai=sd2ai, rival=rv,
                hold=h["hold"], flow=h["flow"], hold_src=h["hold_src"], flow_src=h["flow_src"],
                hold_unit=h["hold_unit"], flow_unit=h["flow_unit"],
                hold_date=h["hold_date"], hold_is_prev=h["hold_is_prev"],
                flow_snaps=h["flow_snaps"], flow_snaps_err=h["flow_snaps_err"],
                peter=pt, actual=actual, warnings=warn)
