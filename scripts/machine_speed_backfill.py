# -*- coding: utf-8 -*-
"""[MW0601 2026-10-27] 「기계 속도」(I9) 백필 판정 — 사전등록 KS-2026-10-27-v1 의 H-K1 · H-K1s · H-K2.

장외 전용(456차). 읽기전용. 표준 라이브러리만.
사전등록: docs/미륵이고도화3/피터2/기계속도_사전등록_<PC>.json (PC 자동 인식 — levels_p.pc()) (여기서 문턱을 바꾸지 않는다 — 값은 json 에서 읽는다).
산출:   docs/미륵이고도화3/피터2/기계속도_백필검증_<PC>-<날짜>.md · .json

    python scripts/machine_speed_backfill.py
"""
import datetime as _dt
import json
import os
import random
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "scripts"), os.path.join(ROOT, "tools", "maekjeom_ladder")):
    if p not in sys.path:
        sys.path.insert(0, p)
from strategy.shindong2_ai.indicators import i9_machine_speed as K     # noqa: E402
import peter_method_backfill as PB                                     # noqa: E402  (통계 함수 재사용)

PDOC = os.path.join(ROOT, "docs", "미륵이고도화3", "피터2")
from strategy.shindong2_ai import levels_p as _LP                      # noqa: E402  (PC 자동 인식)
PC = _LP.pc()
PREREG = os.environ.get("KS_PREREG") or os.path.join(PDOC, "기계속도_사전등록_%s.json" % PC)
WIN_START, WIN_END = "2026-08-10", "2026-10-26"


def _hm(t):
    return int(t[:2]) * 60 + int(t[3:5])


def _fmt(m):
    return "%02d:%02d" % divmod(m, 60)


def program_days(exclude):
    con = sqlite3.connect("file:%s?mode=ro" % K.DB.replace("\\", "/"), uri=True)
    try:
        ds = [r[0] for r in con.execute("SELECT DISTINCT substr(ts,1,10) FROM raw_program_trade WHERE market='1' "
                                        "AND ts>=? AND ts<=? ORDER BY 1", (WIN_START, WIN_END + " 23:59"))]
    finally:
        con.close()
    return [d for d in ds if d not in exclude]


def mini_bars(day):
    import ladder_data as LD
    con = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "data", "db", "regular_candles.db").replace("\\", "/"), uri=True)
    try:
        code = LD.mini_code_for(con, day)
        if not code:
            return {}
        rows = con.execute("SELECT substr(ts,12,5), high, low, close FROM regular_candles WHERE code=? AND trade_date=? "
                           "AND substr(ts,12,5) BETWEEN '08:45' AND '15:45' ORDER BY ts", (code, day)).fetchall()
    finally:
        con.close()
    return {t: (h, l, c) for t, h, l, c in rows}


def close_at(bars, t):
    ks = [k for k in bars if k <= t]
    return bars[max(ks)][2] if ks else None


# ── H-K1s ────────────────────────────────────────────────────────────────
def hk1s(days, cfg):
    h = cfg["hypotheses"]["H-K1s"]
    grid = [_fmt(m) for m in range(_hm("09:30"), _hm("14:30") + 1, 30)]
    by_day = {}
    for d in days:
        s, b = K.load_series(d), mini_bars(d)
        for t in grid:
            v = K.speed(s, t)
            if v is None or abs(v) < h["min_abs_value"]:
                continue
            c0, c1 = close_at(b, t), close_at(b, _fmt(_hm(t) + 30))
            if c0 is None or c1 is None or abs(c1 - c0) <= h["flat_pt"]:
                continue
            by_day.setdefault(d, []).append(1 if (v > 0) == (c1 > c0) else 0)
    hits = [x for v in by_day.values() for x in v]
    n = len(hits)
    rate = sum(hits) / float(n) if n else None
    rng = random.Random(20261027)
    keys = list(by_day)
    boots = []
    for _ in range(1000):
        smp = [x for k in (rng.choice(keys) for _ in keys) for x in by_day[k]]
        if smp:
            boots.append(sum(smp) / float(len(smp)))
    boots.sort()
    lo = boots[int(0.025 * len(boots))] if boots else None
    ps = h["pass"]
    verdict = "INSUFFICIENT" if n < ps["min_n"] else ("PASS" if rate >= ps["hit_min"] and lo is not None and lo > 0.5 else "FAIL")
    return dict(n=n, days=len(by_day), hit_rate=rate, boot_lo95=lo, verdict=verdict)


# ── H-K2 ─────────────────────────────────────────────────────────────────
def _outcome(bars, t, up_extreme):
    """매수→매도 전환(up_extreme=True): 60분 최고가 − t 종가 ≤ 2.0 이고 t+60 종가 < t 종가. 대칭."""
    c0 = close_at(bars, t)
    end = _fmt(_hm(t) + 60)
    fut = [v for k, v in bars.items() if _hm(t) < _hm(k) <= _hm(end)]
    c1 = close_at(bars, end)
    if c0 is None or c1 is None or not fut:
        return None
    if up_extreme:
        return int(max(v[0] for v in fut) - c0 <= 2.0 and c1 < c0)
    return int(c0 - min(v[1] for v in fut) <= 2.0 and c1 > c0)


def hk2(days, X, Y):
    ev, nl, ev_rows = [], [], []
    for d in days:
        s, b = K.load_series(d), mini_bars(d)
        seen = set()
        for m in range(_hm("09:42"), _hm("14:30") + 1):
            t = _fmt(m)
            i9 = K.speed(s, t)
            a, z = K.value_at(s, _fmt(m - 10)), K.value_at(s, _fmt(m - 40))
            if i9 is None or a is None or z is None:
                continue
            b30 = (a - z) / 100.0
            for direction, cond_b, flip in (("buy_to_sell", b30 >= X, i9 <= -Y), ("sell_to_buy", b30 <= -X, i9 >= Y)):
                if not cond_b:
                    continue
                o = _outcome(b, t, direction == "buy_to_sell")
                if o is None:
                    continue
                if flip and direction not in seen:
                    seen.add(direction)
                    ev.append(o)
                    ev_rows.append(dict(day=d, t=t, dir=direction, b30=round(b30), i9=i9, hit=o))
                elif not flip:
                    nl.append(o)
    n1, n0 = len(ev), len(nl)
    r1 = sum(ev) / float(n1) if n1 else None
    r0 = sum(nl) / float(n0) if n0 else None
    p = PB._two_prop_p(sum(ev), n1, sum(nl), n0) if n1 and n0 else None
    return dict(X=X, Y=Y, events=n1, rate=r1, null_n=n0, null_rate=r0,
                edge_pp=(r1 - r0) * 100 if r1 is not None and r0 is not None else None, p=p, rows=ev_rows)


def judge_hk2(res, cfg):
    ps = cfg["hypotheses"]["H-K2"]["pass"]
    if res["events"] < ps["min_events"]:
        return "INSUFFICIENT"
    return "PASS" if res["edge_pp"] is not None and res["edge_pp"] >= ps["min_edge_pp"] and res["p"] is not None and res["p"] < ps["max_p"] else "FAIL"


# ── 리포트 ───────────────────────────────────────────────────────────────
def _f(x, nd=1):
    return "—" if x is None else ("%.*f" % (nd, x) if isinstance(x, float) else str(x))


def render(cfg, days, k1, k1s, k2, sens):
    L = ["# 「기계 속도」(I9) — 백필 검증 (%s · %s)" % (PC, _dt.date.today().isoformat()), "",
         "> 사전등록 `%s`(`%s`, 확정 %s) 문턱 그대로. 생성 `scripts/machine_speed_backfill.py`." % (cfg["id"], os.path.basename(PREREG), cfg.get("registered_at")),
         "> 표본 창 %s – %s · 프로그램 원천 있는 거래일 %d일 · **2026-10-27(설계일) 제외**. 가격 = 미니 근월물 정규봉." % (WIN_START, WIN_END, len(days)), "",
         "## 판정 요약", "", "| 가설 | 표본 | 결과 | 기준 | 판정 |", "|---|---|---|---|---|"]
    for at, r in k1:
        rec = r["result"]
        lim = 0.05 if at == "10:00" else 0.05 / 3
        v = rec["verdict"]
        if at != "10:00" and v == "PASS" and not (rec["p_binom"] < lim and rec["p_perm"] < lim):
            v = "FAIL(본페로니)"
        L.append("| H-K1 @%s%s | n=%s | 적중 %s (이항 p=%s) · IC %s (순열 p=%s · 노이즈95 %s) | 적중 ≥0.55 · p<%s · IC>0 | **%s** |" % (
            at, " 주" if at == "10:00" else " 보조", rec["n"], _f(rec["hit_rate"], 3), _f(rec["p_binom"], 4), _f(rec["ic"], 3),
            _f(rec["p_perm"], 3), _f(rec["noise_95"], 3), "%.4f" % lim, v))
    L.append("| H-K1s 30분 격자 | n=%d (%d일) | 적중 %s · 블록 부트스트랩 95%% 하한 %s | n≥60 · 적중 ≥0.55 · 하한 >0.50 | **%s** |" % (
        k1s["n"], k1s["days"], _f(k1s["hit_rate"], 3), _f(k1s["boot_lo95"], 3), k1s["verdict"]))
    L.append("| H-K2 기계 전환 (X=%d · Y=%d) | 이벤트 %d · 대조 %d분 | 전환 %s%% vs 지속 %s%% · 차이 %s%%p | 이벤트 ≥15 · +15%%p · p<0.05 | **%s** (p=%s) |" % (
        k2["X"], k2["Y"], k2["events"], k2["null_n"], _f(k2["rate"] * 100 if k2["rate"] is not None else None),
        _f(k2["null_rate"] * 100 if k2["null_rate"] is not None else None), _f(k2["edge_pp"]), k2["verdict"], _f(k2["p"], 4)))
    L += ["", "## H-K2 민감도 (보고 전용 — 판정은 X=500 · Y=150 하나)", "", "| X | Y | 이벤트 | 전환 적중 | 지속 적중 | 차이 %p | p |", "|---|---|---|---|---|---|---|"]
    for s in sens:
        L.append("| %d | %d | %d | %s%% | %s%% | %s | %s |" % (s["X"], s["Y"], s["events"], _f(s["rate"] * 100 if s["rate"] is not None else None),
                                                          _f(s["null_rate"] * 100 if s["null_rate"] is not None else None), _f(s["edge_pp"]), _f(s["p"], 4)))
    L += ["", "## H-K2 이벤트 목록 (주 문턱)", "", "| 날짜 | 시각 | 방향 | 직전 30분 | I9 | 극값 근접 |", "|---|---|---|---|---|---|"]
    for r in k2["rows"]:
        L.append("| %s | %s | %s | %+d | %+.0f | %s |" % (r["day"], r["t"], "매수→매도" if r["dir"] == "buy_to_sell" else "매도→매수",
                                                     r["b30"], r["i9"], "✓" if r["hit"] else "✗"))
    L += ["", "## K-OBS", "", "- 전진 확인 전용 — 2026-10-28 이후 새 20거래일에서 잰다(이번 백필 대상 아님).", ""]
    return "\n".join(L)


def main():
    from utils.analysis_db import guard_intraday
    guard_intraday("machine_speed_backfill")
    with open(PREREG, encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["status"].startswith("확정"), "사전등록이 확정되지 않았다"
    excl = set(cfg["hypotheses"]["H-K1"]["exclude_days"])
    days = program_days(excl)
    import shindong2_research as RS
    k1 = []
    for at in [cfg["hypotheses"]["H-K1"]["primary_at"]] + cfg["hypotheses"]["H-K1"]["secondary_at"]:
        k1.append((at, RS.verify("I9", days=60, at_hm=at, until=WIN_END, save=True)))
    k1s = hk1s(days, cfg)
    h2 = cfg["hypotheses"]["H-K2"]
    k2 = hk2(days, h2["X_eok"], h2["Y_eok"])
    k2["verdict"] = judge_hk2(k2, cfg)
    sens = [hk2(days, X, Y) for X in (250, 500, 750) for Y in (75, 150, 225)]
    stamp = _dt.date.today().strftime("%Y%m%d")
    md = os.path.join(PDOC, "기계속도_백필검증_%s-%s.md" % (PC, stamp))
    with open(md, "w", encoding="utf-8") as f:
        f.write(render(cfg, days, k1, k1s, k2, sens))
    with open(md[:-3] + ".json", "w", encoding="utf-8") as f:
        json.dump(dict(prereg=cfg["id"], days=days, hk1=[(a, r["result"], r["rows"]) for a, r in k1], hk1s=k1s, hk2=k2,
                       sensitivity=[{k: v for k, v in s.items() if k != "rows"} for s in sens]), f, ensure_ascii=False, indent=1, default=str)
    for at, r in k1:
        print("H-K1@%s" % at, r["result"]["n"], r["result"]["verdict"], r["result"]["why"])
    print("H-K1s", k1s)
    print("H-K2", {k: v for k, v in k2.items() if k != "rows"})
    print("→", md)


if __name__ == "__main__":
    main()
