# -*- coding: utf-8 -*-
"""맥점 × 옵션 사다리 — 날짜별 데이터 생성 (읽기전용).

[MW0601 656차 / 2026-10-04] 로컬 서버(`server.py`)가 이 모듈로 하루치 JSON 을 만든다.
표준 라이브러리만 쓴다(numpy·pandas 없음 → BLAS delay-load 즉사 경로와 무관).

원천 (전부 `mode=ro`)
  · 1분봉     regular_candles.db (A056A, 08:45–15:45 · 장후 15:52 적재)
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
MINI_CODE = "A056A"

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
        mark(con.execute("SELECT DISTINCT trade_date FROM regular_candles WHERE code=?", (MINI_CODE,)), "candles"); con.close()
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
    today = _dt.date.today().isoformat()
    out.setdefault(today, {})["today"] = True
    return {"dates": out, "today": today}


# ── 1분봉 ─────────────────────────────────────────────────────────────────
_live_cache = {"date": None, "rows": [], "last_ts": None}
_live_lock = threading.Lock()


def _candles_regular(day):
    con = _ro("regular_candles.db")
    try:
        rows = con.execute(
            "SELECT substr(ts,12,5), open, high, low, close FROM regular_candles"
            " WHERE code=? AND trade_date=? AND substr(ts,12,5) BETWEEN '08:45' AND '15:45' ORDER BY ts",
            (MINI_CODE, day)).fetchall()
    finally:
        con.close()
    return [[t, round(o, 2), round(h, 2), round(l, 2), round(c, 2)] for t, o, h, l, c in rows]


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
            rows = _candles_regular(day)
            if rows:
                return rows, "regular_candles(A056A)"
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
    mins = ["%02d:%02d" % (h, m) for h in range(8, 17) for m in range(60)]
    mins = [m for m in mins if "08:45" <= m <= "16:10"]
    con = _ro("option_flow.db")
    try:
        rows = con.execute("SELECT bar_time, product, investor, net_qty FROM option_investor_flow WHERE trade_date=?",
                           (day,)).fetchall()
    finally:
        con.close()
    g = {}
    for t, p, i, q in rows:
        g.setdefault((p, i), {})[t] = q
    out = {}
    for p in FLOW_PRODUCTS:
        out[p] = {}
        for i in ("foreign", "individual", "institution"):
            d = g.get((p, i))
            if not d:
                out[p][i] = None
                continue
            last, arr = None, []
            for m in mins:
                if m in d:
                    last = d[m]
                arr.append(last)
            out[p][i] = arr
    last_bar = max((t for t, *_ in rows), default=None)
    return mins, out, last_bar


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


def hts9842(day):
    """그날의 당일 순매수(D) 파일과, 그날 이전 가장 최근의 기간 보유(P) 파일.

    당일 순매수 고르는 순서: 시각 없는 YYMMDD_D(마감본·P 차분본) → 없으면 가장 늦은 시점 파일.
    시점 파일(YYMMDD_HHMM_D)은 flow_snaps 로 따로 돌려준다 — 화면이 직전 시점 대비 증감과
    행사가 × 시각 칸을 그린다. 읽기 실패한 시점은 빼고 flow_snaps_err 에 남긴다(메우지 않는다).
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
    flow_pick = daily[-1] if daily else (snap_ok[-1] if snap_ok else None)
    if hold_f:
        res["hold_date"] = hold_f[-1]["date"]
        res["hold_is_prev"] = _is_prev_trading_day(hold_f[-1]["date"], day)
    for key, f in (("flow", flow_pick), ("hold", hold_f[-1] if hold_f else None)):
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
def is_live(day, now=None):
    now = now or _dt.datetime.now()
    if day != now.date().isoformat():
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
        mins, f1m, flow_last = flow1m(day)
    except Exception as e:
        mins, f1m, flow_last = [], {}, None
        warn.append("7222 흐름 읽기 실패: %s" % e)
    h = hts9842(day)
    warn += ["9842 시점 파일 읽기 실패 — %s" % e for e in h["flow_snaps_err"]]
    actual = dict(high=max((c[2] for c in cs), default=None), low=min((c[3] for c in cs), default=None))
    return dict(date=day, live=live, generated_at=now.isoformat(timespec="seconds"),
                candles=cs, candle_src=csrc, levels=lv, bands=bands, basis=basis if basis is not None else 0.0,
                basis_measured=basis is not None, times=times, books=bk, mins=mins, flow1m=f1m, flow_last=flow_last,
                hold=h["hold"], flow=h["flow"], hold_src=h["hold_src"], flow_src=h["flow_src"],
                hold_unit=h["hold_unit"], flow_unit=h["flow_unit"],
                hold_date=h["hold_date"], hold_is_prev=h["hold_is_prev"],
                flow_snaps=h["flow_snaps"], flow_snaps_err=h["flow_snaps_err"],
                peter=pt, actual=actual, warnings=warn)
