# -*- coding: utf-8 -*-
"""[MW0601 2026-10-27] 신동2AI 「피터의 방법」 P층 레벨 — 반발형 극값 군집 · 공방형 체류 · 먼스리 벽.

🔴 이 모듈은 신동2AI 전용이다. `features/levels/premarket_levels.py`(구조 맥점)를 **바꾸지 않는다** —
   그 테이블은 신동 MAIN 이 직접 읽는다(`strategy/shindong/runner.py`). 여기 레벨은 옆에 **표기**만 한다.

왜 필요한가 (10-26 실측)
  구조 맥점은 매물대(체류시간)·갭·**전일** 고저·VWAP 뿐이라, 오래 머물지 않고 튕겨 나가는 바닥을 원리상 놓친다.
  10-26 의 850 은 7세션 체류 43분(최소권)인데 일중 극값 근접 3일(최다) — 10-15 848.00 · 10-20 850.60 · 10-22 852.05.
  사다리 08:51 구조 맥점은 854 아래가 바로 842 였다.

정의 = `docs/미륵이고도화3/피터2/피터방법_사전등록_<PC>.json` 의 p_level · walls (여기서 상수로 복제하지 않는다).

순수 함수(`cluster_extremes` · `dwell_levels` · `merge_walls` · `p_levels_from`)와
로더(`load_sessions` · `load_walls`)를 나눈다 — 백필은 순수 함수만 재사용한다(미래 참조 금지는 호출 쪽 책임:
`load_sessions(day)` 는 **day 이전** 세션만 돌려준다).
"""
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(ROOT, "data", "db")
PDOC = os.path.join(ROOT, "docs", "미륵이고도화3", "피터2")


def pc():
    """PC명(MW0601/MW0602) — 사전등록·산출물 파일명이 PC 를 따른다. 환경변수 SHINDONG2_PC 가 우선.

    이식(MW0602 Sindong-V4)용: 그 PC 는 **자기 사전등록 파일**(`피터방법_사전등록_MW0602.json`)이 없으면
    prereg() 가 실패하고 snapshot 블록이 「계산 실패(미측정)」로 뜬다 — 남의 PC 기준을 조용히 쓰지 않는다."""
    import platform
    import re
    v = os.environ.get("SHINDONG2_PC")
    if v:
        return v
    m = re.search(r"(MW\d{4})", platform.node() or "", re.IGNORECASE)
    return m.group(1).upper() if m else "UNKNOWN"


def prereg_path():
    return os.environ.get("PMETHOD_PREREG") or os.path.join(PDOC, "피터방법_사전등록_%s.json" % pc())


def prereg(path=None):
    with open(path or prereg_path(), encoding="utf-8") as f:
        return json.load(f)


def _ro(name):
    return sqlite3.connect("file:%s?mode=ro" % os.path.join(DB, name), uri=True)


# ── 순수 함수 ──────────────────────────────────────────────────────────────
def cluster_extremes(extremes, tol, min_hits, round_to=0.5):
    """extremes = [(날짜, 'H'|'L', 가격)] → 반발 군집 [{price, hits, members}].

    가격순으로 훑으며 군집 첫 값에서 2·tol 폭 안을 한 군집으로 묶는다(연쇄 확장 금지 — 폭이 무한히 늘지 않게).
    같은 군집에 같은 날 고·저가 다 들어가면 1회로 센다(하루 변동폭이 tol 보다 좁은 날의 이중 계수 방지)."""
    xs = sorted(extremes, key=lambda x: x[2])
    out, i = [], 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1][2] - xs[i][2] <= 2 * tol:
            j += 1
        grp = xs[i:j + 1]
        days = {d for d, _, _ in grp}
        if len(days) >= min_hits:
            px = sum(p for _, _, p in grp) / len(grp)
            out.append(dict(price=round(round(px / round_to) * round_to, 2), hits=len(days),
                            members=[[d, k, round(p, 2)] for d, k, p in grp]))
            i = j + 1
        else:
            i += 1
    return out


def dwell_levels(bars_by_day, grid, band, top_n):
    """5pt 격자 레벨 ±band 체류분 상위 top_n → [{price, minutes, days}]."""
    dwell, days = {}, {}
    for d, bars in bars_by_day:
        for b in bars:
            h, l = b[2], b[3]
            k = int((l - band) // grid) * grid
            while k <= h + band:
                if k >= l - band and k <= h + band:
                    dwell[k] = dwell.get(k, 0) + 1
                    days.setdefault(k, set()).add(d)
                k += grid
    top = sorted(dwell.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]
    return [dict(price=float(k), minutes=m, days=len(days[k])) for k, m in top]


def merge_walls(levels, walls, tol):
    """레벨에 ±tol 안 벽을 「합류」로 붙인다. 벽 자체도 kind='벽' 레벨로 돌려준다."""
    for lv in levels:
        lv.setdefault("merged", [])
        for w in walls:
            if abs(w["price"] - lv["price"]) <= tol:
                lv["merged"].append(w["label"])
    return levels + [dict(price=w["price"], kind="벽", label=w["label"], merged=[]) for w in walls]


def p_levels_from(bars_by_day, walls=None, cfg=None):
    """직전 세션 봉([(날짜, [[hm,o,h,l,c],…]), …] — 오래된 → 최근) → P층 레벨 목록."""
    cfg = cfg or prereg()
    pl = cfg["p_level"]
    hist = list(bars_by_day)[-pl["lookback_sessions"]:]
    ext = []
    for d, bars in hist:
        if bars:
            ext.append((d, "H", max(b[2] for b in bars)))
            ext.append((d, "L", min(b[3] for b in bars)))
    out = []
    for c in cluster_extremes(ext, pl["cluster_tol_pt"], pl["min_hits"], pl.get("round_to", 0.5)):
        out.append(dict(price=c["price"], kind="반발", label="반발%d회" % c["hits"], hits=c["hits"],
                        members=c["members"]))
    for v in dwell_levels(hist, pl["dwell_grid_pt"], pl["dwell_band_pt"], pl["dwell_top_n"]):
        out.append(dict(price=v["price"], kind="공방", label="공방%d분/%d일" % (v["minutes"], v["days"]),
                        minutes=v["minutes"], days=v["days"]))
    if walls:
        out = merge_walls(out, walls, cfg["walls"]["merge_tol_pt"])
    return sorted(out, key=lambda x: x["price"])


def anchors(levels):
    """상자 스냅 앵커 = 반발·공방·벽 가격(위클리 피닝 제외)."""
    return sorted({lv["price"] for lv in levels if lv.get("kind") in ("반발", "공방", "벽")})


# ── 로더 ──────────────────────────────────────────────────────────────────
def load_sessions(day, n, code=None):
    """day **이전** n 세션의 봉. code 가 없으면 날마다 미니 근월물(사다리 규칙 `mini_code_for`)."""
    con = _ro("regular_candles.db")
    try:
        if code:
            days = [r[0] for r in con.execute(
                "SELECT DISTINCT trade_date FROM regular_candles WHERE code=? AND trade_date<? "
                "ORDER BY trade_date DESC LIMIT ?", (code, day, n))]
        else:
            days = [r[0] for r in con.execute(
                "SELECT DISTINCT trade_date FROM regular_candles WHERE code LIKE 'A05%' AND trade_date<? "
                "ORDER BY trade_date DESC LIMIT ?", (day, n))]
        out = []
        for d in sorted(days):
            c = code or con.execute("SELECT MIN(code) FROM regular_candles WHERE trade_date=? AND code LIKE 'A05%'",
                                    (d,)).fetchone()[0]
            rows = con.execute(
                "SELECT substr(ts,12,5), open, high, low, close FROM regular_candles WHERE code=? AND trade_date=? "
                "AND substr(ts,12,5) BETWEEN '08:45' AND '15:45' ORDER BY ts", (c, d)).fetchall()
            out.append((d, [list(r) for r in rows]))
        return out
    finally:
        con.close()


def walls_from_books(books, cfg=None):
    """사다리 `books`(build_day) → 먼스리 벽 목록 [{price, label}] + 위클리 피닝 중심(그날 만기 북).

    벽 = wall_open 콜·풋 + 각 측 OI 상위 top_n(그날 첫 스냅). 없으면 ([], None) — 미측정."""
    cfg = cfg or prereg()
    n = cfg["walls"]["top_n_per_side"]
    walls, pin = [], None
    mb = (books or {}).get("monthly") or {}
    if mb and not mb.get("absent") and mb.get("strikes"):
        st = mb["strikes"]
        wo = mb.get("wall_open") or [None, None]
        if wo[0] is not None:
            walls.append(dict(price=float(wo[0]), label="먼스리콜벽%g" % wo[0]))
        if wo[1] is not None:
            walls.append(dict(price=float(wo[1]), label="먼스리풋벽%g" % wo[1]))
        for side, key, nm in (("call", "call", "콜"), ("put", "put", "풋")):
            col = []
            for j, s in enumerate(st):
                arr = (mb.get(key) or [])[j] if j < len(mb.get(key) or []) else None
                v = next((x for x in (arr or []) if x is not None), None)
                if v is not None:
                    col.append((v, s))
            for v, s in sorted(col, reverse=True)[:n]:
                if not any(abs(w["price"] - s) < 1e-6 for w in walls):
                    walls.append(dict(price=float(s), label="먼스리%sOI%g(%d)" % (nm, s, v)))
    return walls, pin


def weekly_pin(books, day):
    """그날 만기 위클리 북의 콜+풋 OI 최대 행사가. 없으면 None."""
    for k, b in (books or {}).items():
        if not k.startswith("weekly") or not b or b.get("absent") or b.get("expiry") != day:
            continue
        best = None
        for j, s in enumerate(b.get("strikes") or []):
            c = next((x for x in ((b.get("call") or [])[j] or []) if x is not None), 0) if j < len(b.get("call") or []) else 0
            p = next((x for x in ((b.get("put") or [])[j] or []) if x is not None), 0) if j < len(b.get("put") or []) else 0
            if best is None or c + p > best[0]:
                best = (c + p, s)
        if best:
            return dict(price=float(best[1]), label="위클리피닝%g(%s만기)" % (best[1], k), oi=best[0])
    return None
