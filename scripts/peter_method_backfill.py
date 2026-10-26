# -*- coding: utf-8 -*-
"""[MW0601 2026-10-27] 신동2AI 「피터의 방법」 백필 검증 — 사전등록 문턱으로 H-P1 · H-B1 · H-B2 · H-V1 판정.

장후·장외 전용(456차 — guard_intraday). 읽기전용. numpy·scipy 없음(표준 라이브러리만 — BLAS 경로 무관).
사전등록: docs/미륵이고도화3/피터2/피터방법_사전등록_<PC>.json (여기서 문턱을 바꾸지 않는다).
산출:   docs/미륵이고도화3/피터2/피터방법_백필검증_<PC>-<날짜>.md · .json

    python scripts/peter_method_backfill.py [--since 2024-07-04] [--until 2026-10-26]
"""
import argparse
import datetime as _dt
import json
import math
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from strategy.shindong2_ai import levels_p as P      # noqa: E402
from strategy.shindong2_ai import box as B           # noqa: E402

OUT_DIR = os.path.join(ROOT, "docs", "미륵이고도화3", "피터2")
CODE = "10100"


# ── 통계(표준 라이브러리) ──────────────────────────────────────────────────
def _binom_sf(k, n, p=0.5):
    """P(X ≥ k), X~Bin(n,p) — 단측."""
    if n <= 0:
        return None
    lg = lambda a: math.lgamma(a + 1)
    s = 0.0
    for i in range(k, n + 1):
        s += math.exp(lg(n) - lg(i) - lg(n - i) + i * math.log(p) + (n - i) * math.log(1 - p))
    return min(1.0, s)


def _two_prop_p(x1, n1, x2, n2):
    """단측 p (p1 > p2) — 정규 근사."""
    if not n1 or not n2:
        return None
    p = (x1 + x2) / float(n1 + n2)
    se = math.sqrt(p * (1 - p) * (1.0 / n1 + 1.0 / n2)) if 0 < p < 1 else 0
    if se == 0:
        return None
    z = (x1 / float(n1) - x2 / float(n2)) / se
    return 0.5 * math.erfc(z / math.sqrt(2))


def _mcnemar_p(b, c):
    """짝지은 비교 단측 p — b = 실험만 성공, c = 대조만 성공. 정확 이항."""
    return _binom_sf(b, b + c) if b + c else None


# ── 데이터 ────────────────────────────────────────────────────────────────
def _ro(name):
    return sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "data", "db", name), uri=True)


def load_all(code, since, until):
    con = _ro("regular_candles.db")
    try:
        rows = con.execute(
            "SELECT trade_date, substr(ts,12,5), open, high, low, close FROM regular_candles WHERE code=? "
            "AND trade_date BETWEEN ? AND ? AND substr(ts,12,5) BETWEEN '08:45' AND '15:45' ORDER BY ts",
            (code, since, until)).fetchall()
    finally:
        con.close()
    by = {}
    for d, hm, o, h, l, c in rows:
        by.setdefault(d, []).append([hm, o, h, l, c])
    return by


def quarterly_roll_days(days):
    """분기 만기(3·6·9·12월 둘째 목요일) 다음 거래일."""
    out = set()
    ds = sorted(days)
    for y in range(2024, 2028):
        for m in (3, 6, 9, 12):
            d = _dt.date(y, m, 1)
            th = [d + _dt.timedelta(days=i) for i in range(14) if (d + _dt.timedelta(days=i)).weekday() == 3]
            exp = th[1].isoformat()
            nxt = next((x for x in ds if x > exp), None)
            if nxt:
                out.add(nxt)
    return out


def load_walls(day):
    """그날 첫 먼스리 스냅의 벽(option_book) — 없으면 [](미측정)."""
    con = _ro("option_book.db")
    try:
        r = con.execute("SELECT ts, call_wall, put_wall FROM option_book_snap WHERE book='monthly' AND ts LIKE ? "
                        "ORDER BY ts LIMIT 1", (day + "%",)).fetchone()
        if not r:
            return []
        ts, cw, pw = r
        walls = []
        if cw is not None:
            walls.append(dict(price=float(cw), label="먼스리콜벽%g" % cw))
        if pw is not None:
            walls.append(dict(price=float(pw), label="먼스리풋벽%g" % pw))
        rows = con.execute("SELECT strike, call_oi, put_oi FROM option_book_strike WHERE ts=? AND book='monthly'",
                           (ts,)).fetchall()
        for idx, nm in ((1, "콜"), (2, "풋")):
            for row in sorted([x for x in rows if x[idx] is not None], key=lambda x: -x[idx])[:2]:
                if not any(abs(w["price"] - row[0]) < 1e-6 for w in walls):
                    walls.append(dict(price=float(row[0]), label="먼스리%sOI%g(%d)" % (nm, row[0], row[idx])))
        return walls
    finally:
        con.close()


# ── 판정 ──────────────────────────────────────────────────────────────────
def run(since, until):
    cfg = P.prereg()
    by = load_all(CODE, since, until)
    days = sorted(by)
    rolls = quarterly_roll_days(days)
    N = cfg["p_level"]["lookback_sessions"]
    excl_roll = set()
    for r in rolls:
        if r in days:
            i = days.index(r)
            excl_roll.update(days[i:i + cfg["data"]["roll_exclude_sessions"]])
    hp1 = dict(p=[0, 0, 0], n=[0, 0, 0])          # [ok, fail, timeout] — P맥점 / 정수 레벨
    rp, rn = [0, 0, 0], [0, 0, 0]
    box_rows, per_day = [], []
    for i, d in enumerate(days):
        if i < N or d in excl_roll:
            continue
        hist = [(x, by[x]) for x in days[i - N:i]]
        bars = by[d]
        walls = load_walls(d)
        lv = P.p_levels_from(hist, walls, cfg)
        rebound = [x["price"] for x in lv if x["kind"] == "반발"]
        lo_d, hi_d = min(b[3] for b in bars), max(b[2] for b in bars)
        # H-P1 — 반발형 P맥점 vs 같은 날 5pt 정수 레벨(P맥점 ±2.5 제외)
        for L in rebound:
            res = B.level_reaction(bars, L, cfg)
            if res:
                rp[0 if res["ok"] else 1 if res["ok"] is False else 2] += 1
        k = int(math.floor((lo_d - 5) / 5.0)) * 5
        while k <= hi_d + 5:
            if not any(abs(k - L) <= 2.5 for L in rebound):
                res = B.level_reaction(bars, float(k), cfg)
                if res:
                    rn[0 if res["ok"] else 1 if res["ok"] is False else 2] += 1
            k += 5
        # H-B1 · H-B2
        for T in cfg["box"]["T"]:
            bx = B.make_boxes(bars, T, P.anchors(lv), cfg)
            if not bx:
                continue
            row = dict(day=d, T=T, walls=bool(walls), or_lo=bx["or_lo"], or_hi=bx["or_hi"])
            for v in ("B0", "B1", "B2"):
                s = B.score_box(bars, bx[v], T, cfg)
                row[v] = bx[v]
                row[v + "_held"] = s["held"] if s else None
                if v == "B2" and s:
                    row.update(B2_break=s["break_side"], B2_break_t=s["break_t"], B2_ext=s["ext"], B2_mae=s["mae"])
            box_rows.append(row)
    hp1 = dict(p_ok=rp[0], p_fail=rp[1], p_to=rp[2], n_ok=rn[0], n_fail=rn[1], n_to=rn[2])
    return cfg, days, excl_roll, hp1, box_rows


def judge(cfg, hp1, box_rows):
    H = cfg["hypotheses"]
    out = {}
    # H-P1 — 시간초과는 실패로 센다(보수적, 사전등록 문구 「먼저 온다」)
    pn, nn = sum(hp1[k] for k in ("p_ok", "p_fail", "p_to")), sum(hp1[k] for k in ("n_ok", "n_fail", "n_to"))
    pr = hp1["p_ok"] / float(pn) if pn else None
    nr = hp1["n_ok"] / float(nn) if nn else None
    pp = _two_prop_p(hp1["p_ok"], pn, hp1["n_ok"], nn)
    ps = H["H-P1"]["pass"]
    edge = (pr - nr) * 100 if pr is not None and nr is not None else None
    out["H-P1"] = dict(n=pn, rate=pr, null_n=nn, null_rate=nr, edge_pp=edge, p=pp,
                       verdict="INSUFFICIENT" if pn < ps["min_n"] else
                       ("PASS" if edge >= ps["min_edge_pp"] and pp is not None and pp < ps["max_p"] else "FAIL"))
    for T in cfg["box"]["T"]:
        rows = [r for r in box_rows if r["T"] == T and r.get("B2_held") is not None and r.get("B0_held") is not None]
        n = len(rows)
        h2 = sum(1 for r in rows if r["B2_held"])
        h1 = sum(1 for r in rows if r["B1_held"])
        h0 = sum(1 for r in rows if r["B0_held"])
        b = sum(1 for r in rows if r["B2_held"] and not r["B0_held"])
        c = sum(1 for r in rows if r["B0_held"] and not r["B2_held"])
        p = _mcnemar_p(b, c)
        ed = (h2 - h0) * 100.0 / n if n else None
        ps = H["H-B1"]["pass"]
        out["H-B1@" + T] = dict(n=n, B2=h2, B1=h1, B0=h0, edge_pp=ed, mcnemar_b=b, mcnemar_c=c, p=p,
                                widths_med=_median([r["B2"][1] - r["B2"][0] for r in rows]),
                                verdict="INSUFFICIENT" if n < ps["min_n"] else
                                ("PASS" if ed >= ps["min_edge_pp"] and p is not None and p < ps["max_p"] else "FAIL"))
        br = [r for r in rows if r.get("B2_break") and r.get("B2_ext") is not None]
        pos = sum(1 for r in br if r["B2_ext"] - r["B2_mae"] > 0)
        nz = sum(1 for r in br if r["B2_ext"] - r["B2_mae"] != 0)
        p2 = _binom_sf(pos, nz) if nz else None
        ps = H["H-B2"]["pass"]
        out["H-B2@" + T] = dict(n=len(br), pos=pos, nonzero=nz, p=p2,
                                med_ext=_median([r["B2_ext"] for r in br]), med_mae=_median([r["B2_mae"] for r in br]),
                                verdict="INSUFFICIENT" if len(br) < ps["min_n"] else
                                ("PASS" if p2 is not None and p2 < ps["max_p"] else "FAIL"))
    return out


def _median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else round((xs[m - 1] + xs[m]) / 2.0, 2)


# ── H-V1 피터 관점 채점 ──────────────────────────────────────────────────
def score_views(cfg, by):
    from strategy.peter2.view import parse_view, SCORABLE
    from strategy.peter2.parse import parse_tweet
    raw_dir = os.path.join(ROOT, "data", "peter_feed", "_raw")
    rows = []
    for fn in sorted(os.listdir(raw_dir)):
        if not fn.endswith(".jsonl"):
            continue
        with open(os.path.join(raw_dir, fn), encoding="utf-8") as f:
            for line in f:
                try:
                    t = json.loads(line)
                except ValueError:
                    continue
                txt = t.get("text") or ""
                r = parse_tweet(txt)
                if r.get("ignore") or r["facts"]:
                    continue
                v = parse_view(txt)
                if v["kind"] not in SCORABLE:
                    continue
                kst = _dt.datetime.strptime(t["dt"][:19], "%Y-%m-%dT%H:%M:%S") + _dt.timedelta(hours=9)
                rows.append(score_view(v, kst, by, cfg, t.get("id"), txt))
    return rows


def score_view(v, kst, by, cfg, tid=None, txt=""):
    """관점 1건 채점(정규 10100, 피터와 같은 단위). 장 전 발언은 09:00 부터 센다."""
    d = kst.date().isoformat()
    hm = max(kst.strftime("%H:%M"), "09:00")
    bars = by.get(d)
    row = dict(id=tid, day=d, hm=kst.strftime("%H:%M"), kind=v["kind"], box=v["box"], bias=v["bias"],
               bias_level=v["bias_level"], levels=v["levels"], raw=txt.replace("\n", " / ")[:90], result=None)
    if not bars or hm > "15:10":
        row["result"] = "미측정(봉 없음·장후)"
        return row
    post = [b for b in bars if hm <= b[0] <= "15:10"]
    if not post:
        row["result"] = "미측정"
        return row
    if v["kind"] == "box" and v["box"]:
        lo, hi = v["box"]
        row["held"] = all(b[2] <= hi + 1 and b[3] >= lo - 1 for b in post)
        row["post_hi"], row["post_lo"] = max(b[2] for b in post), min(b[3] for b in post)
        row["result"] = "적중(상자 유지)" if row["held"] else "이탈"
    elif v["bias"]:
        p0 = post[0][1]
        end = [b for b in post if b[0] <= _hm_add(post[0][0], 60)][-1][4]
        mv = end - p0
        sgn = -1 if v["bias"] == "short" else 1
        row["move60"] = round(mv, 2)
        row["result"] = "보합" if abs(mv) <= 1 else ("적중" if mv * sgn > 0 else "빗나감")
    else:
        row["result"] = "표시만(판정 정의 v2)"
    return row


def _hm_add(hm, m):
    t = int(hm[:2]) * 60 + int(hm[3:]) + m
    return "%02d:%02d" % (t // 60, t % 60)


# ── 리포트 ────────────────────────────────────────────────────────────────
def _f(x, nd=1):
    return "—" if x is None else ("%.*f" % (nd, x) if isinstance(x, float) else str(x))


def render(cfg, days, excl, hp1, J, box_rows, views, since, until):
    L = ["# 피터의 방법 — 백필 검증 (%s · %s)" % (P.pc(), _dt.date.today().isoformat()), "",
         "> 사전등록 `%s` (`%s`) 문턱 그대로. 생성 `scripts/peter_method_backfill.py`." % (cfg["id"], os.path.basename(P.prereg_path())),
         "> 가격 = 정규 근월 10100(피터와 같은 단위) · 기간 %s – %s · 거래일 %d · 분기 롤 제외 %d일 · 첫 %d일은 이력 부족으로 제외." % (
             since, until, len(days), len(excl), cfg["p_level"]["lookback_sessions"]),
         "> 먼스리 벽은 option_book 이 있는 날(2026-09-23–)만 앵커에 들어간다. 그 이전 B2 는 P맥점 앵커만이다.", "",
         "## 판정 요약", "", "| 가설 | n | 결과 | 대조 | 차이 | p | 판정 |", "|---|---|---|---|---|---|---|"]
    h = J["H-P1"]
    L.append("| H-P1 반발형 P맥점 첫 터치 → 되돌림 먼저 | %d | %s%% | 정수 레벨 %s%% (n=%d) | %s%%p | %s | **%s** |" % (
        h["n"], _f(h["rate"] * 100 if h["rate"] is not None else None), _f(h["null_rate"] * 100 if h["null_rate"] is not None else None),
        h["null_n"], _f(h["edge_pp"]), _f(h["p"], 4), h["verdict"]))
    for T in cfg["box"]["T"]:
        h = J["H-B1@" + T]
        n = h["n"] or 1
        L.append("| H-B1 상자 유지 @%s | %d | B2 %s%% · B1 %s%% | B0 %s%% | %s%%p | %s (McNemar b=%d c=%d) | **%s** |" % (
            T, h["n"], _f(h["B2"] * 100.0 / n), _f(h["B1"] * 100.0 / n), _f(h["B0"] * 100.0 / n), _f(h["edge_pp"]),
            _f(h["p"], 4), h["mcnemar_b"], h["mcnemar_c"], h["verdict"]))
        h = J["H-B2@" + T]
        L.append("| H-B2 이탈 가속 @%s | %d | MFE>MAE %d/%d · 중앙 MFE %s · MAE %s | 부호 50%% | — | %s | **%s** |" % (
            T, h["n"], h["pos"], h["nonzero"], _f(h["med_ext"]), _f(h["med_mae"]), _f(h["p"], 4), h["verdict"]))
    L += ["", "H-P1 세부: P맥점 되돌림 %d · 관통 %d · 30분 무결말 %d / 정수 레벨 %d · %d · %d (무결말은 실패로 셈 — 사전등록 「먼저 온다」)." % (
        hp1["p_ok"], hp1["p_fail"], hp1["p_to"], hp1["n_ok"], hp1["n_fail"], hp1["n_to"]), ""]
    vs = [v for v in views if v["result"] and not v["result"].startswith("미측정")]
    L += ["## H-V1 피터 관점 채점 (채점만 — 판정 보류 n≥20)", "",
          "| 날짜 | 시각 | 유형 | 관점 | 결과 | 원문 |", "|---|---|---|---|---|---|"]
    for v in views:
        what = ("상자 %s–%s" % (_f(v["box"][0], 0), _f(v["box"][1], 0))) if v.get("box") else \
               ("편향 %s%s" % ("풋" if v.get("bias") == "short" else "콜", (" %s" % _f(v["bias_level"], 0)) if v.get("bias_level") else "")) if v.get("bias") else \
               ", ".join(_f(x, 0) for x in v["levels"][:3])
        L.append("| %s | %s | %s | %s | %s | %s |" % (v["day"], v["hm"], v["kind"], what, v["result"],
                                                    v["raw"].replace("|", "／")))
    nb = [v for v in vs if v["kind"] == "box"]
    nbi = [v for v in vs if v.get("bias") and v["kind"] != "box"]
    L += ["", "- 상자 관점 %d건 중 유지 %d · 편향 관점 %d건 중 적중 %d · 보합 %d." % (
        len(nb), sum(1 for v in nb if v.get("held")), len(nbi), sum(1 for v in nbi if v["result"] == "적중"),
        sum(1 for v in nbi if v["result"] == "보합")), ""]
    L += ["## 해석 규칙", "",
          "- PASS 여도 자동 장착 없음 — 레슨은 다음 거래일부터 적용 3회·적중 우세 뒤 승격, 지표는 verify PASS + 사용자 확인.",
          "- FAIL 이면 섀도 채점만 유지하고 해설에서는 「참고 레벨」로만 쓴다. 문턱을 낮추지 않는다(458차 D6).",
          "- B0 는 같은 폭 상자를 T 직전 종가 중심에 둔 대조군이다 — 「상자 폭이 넓어서 유지된 것」을 걸러낸다.", ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2024-07-04")
    ap.add_argument("--until", default=(_dt.date.today() - _dt.timedelta(days=1)).isoformat())
    ap.add_argument("--no-guard", action="store_true")
    a = ap.parse_args(argv)
    if not a.no_guard:
        from utils.analysis_db import guard_intraday
        guard_intraday("peter_method_backfill")
    cfg, days, excl, hp1, box_rows = run(a.since, a.until)
    J = judge(cfg, hp1, box_rows)
    views = score_views(cfg, load_all(CODE, "2026-08-01", a.until))
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = _dt.date.today().strftime("%Y%m%d")
    md = os.path.join(OUT_DIR, "피터방법_백필검증_%s-%s.md" % (P.pc(), stamp))
    with open(md, "w", encoding="utf-8") as f:
        f.write(render(cfg, days, excl, hp1, J, box_rows, views, a.since, a.until))
    with open(md[:-3] + ".json", "w", encoding="utf-8") as f:
        json.dump(dict(prereg=cfg["id"], since=a.since, until=a.until, judge=J, hp1=hp1, views=views,
                       box_rows=box_rows), f, ensure_ascii=False, indent=1)
    for k, v in J.items():
        print(k, v.get("n"), v.get("verdict"), "edge=%s p=%s" % (v.get("edge_pp"), v.get("p")))
    print("→", md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
