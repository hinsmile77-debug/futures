# -*- coding: utf-8 -*-
"""[MW0601 632차 후속] 신동 일일 리포트 — 장후 1회, 한 장으로 「거래 흐름 + 손익 vs 섀도 흐름 + 손익」.

무엇을 내나
-----------
`docs/신동거래/일일/신동_일일_<PC>_YYYYMMDD.md` + 같은 이름 `.svg`(차트). PC = `utils.db_utils.pc_id()`(예: MW0601)
— 두 PC 리포트가 한 폴더·메일함에 섞여도 출처가 파일명과 제목에서 바로 보인다.

  0. 한눈에      — 시장 · R1 · 변형별 순손익 · 오늘의 한 줄
  1. 차트        — 변형마다 한 줄: 가격 + 진입·청산 + 맥점 / 맨 아래 개인 콜−풋
  2. 거래 흐름   — MAIN 타임라인(누적 손익 포함)
  3. 섀도 흐름   — 섀도별 타임라인 + **MAIN 과 무엇이 달랐나**(차단·시점 이동·청산 차이)
  4. 누적 채점   — 채점 시작 이후 변형별 · 판정 진행(D-n) · R1 적중률
  5. 러너 섀도   — 미륵이 × 신동(장후 기록)
  6. 개선 방향   — 자동 관찰(판정 아님)

원칙
----
- **계산은 엔진 재생**이다(`engine.run_day`, 하루 전체). 라이브 기록(`shindong.db`)이 있으면
  탐지 시각·실현가능가만 붙인다. 라이브 기록이 없는 변형은 「재계산」으로 표시한다(계측 4원칙 ④).
- 주문·설정·기록을 바꾸지 않는다 — 읽기만 하고 파일 두 개를 쓴다.
- 판정 전 집계를 판정처럼 쓰지 않는다. 「개선 방향」은 관찰이며 규격 변경은 사전등록 §6 절차로만.
- 장중(15:35 전)에 돌리면 가격·흐름이 아직 끝나지 않았다 — 호출자가 장후에 부른다.
"""
import datetime as _dt
import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from strategy.shindong import engine as E
from strategy.shindong import runner as RN
from strategy.shindong import spec as S
from strategy.shindong.calendar import select_flow_product

VLABEL = {"MAIN": "MAIN(본안)", "SHADOW_E2F2": "E2F2(흐름순응)",
          "SHADOW_X4NF": "X4NF(가까운목표·flip금지)", "SHADOW_TR44": "TR44(R3 트레일 4/4)",
          "SHADOW_X4NFA": "X4NFA(X4NF+깨진맥점금지)"}
REASON = {"TP1": "1차", "TP2": "최종", "SL": "손절", "BE": "본전", "TIME": "시간", "TR": "트레일"}


def report_stem(trade_date: str, pc: Optional[str] = None) -> str:
    """파일명 줄기 — 신동_일일_<PC>_YYYYMMDD. 리포트·PDF·메일이 모두 이 함수로 이름을 만든다."""
    if pc is None:
        from utils.db_utils import pc_id
        pc = pc_id()
    return "신동_일일_%s_%s" % (pc, trade_date.replace("-", ""))


def _won(x: Optional[float]) -> str:
    return "-" if x is None else format(float(x), "+,.0f")


def _man(x: Optional[float]) -> str:
    return "-" if x is None else "%+.1f만" % (float(x) / 1e4)


def _side(s: int) -> str:
    return "매수" if s > 0 else "매도"


def _key(tr: Dict[str, Any]) -> str:
    return "%s|%s|%+d" % (tr["rule"], tr["entry_ts"], tr["side"])


# ── 입력 ────────────────────────────────────────────────────────────────
def load_day(trade_date: str, raw_db: str, flow_db: str, levels_db: str) -> Dict[str, Any]:
    product, _exp, note = select_flow_product(_dt.date.fromisoformat(trade_date))
    candles, flow, lvrows = RN.load_inputs(trade_date, product, raw_db, flow_db, levels_db)
    out = {"product": product, "product_note": note, "ok": False, "results": {}}
    if not candles or "0850" not in lvrows:
        out["why"] = "봉 없음" if not candles else "08:50 맥점 없음"
        return out
    L = E.prepare_levels(lvrows)
    d = E.DayFrame(candles, flow)
    out.update(ok=True, L=L, d=d)
    for v in S.VARIANTS:
        out["results"][v] = E.run_day(d, L, v)
    return out


def _stored(sd_db: str, trade_date: str) -> Tuple[set, Dict[Tuple[str, str], Dict[str, Any]]]:
    """(라이브 판정 행이 있는 변형들, {(변형, trade_key): 행})."""
    if not sd_db or not os.path.exists(sd_db):
        return set(), {}
    con = sqlite3.connect("file:%s?mode=ro" % sd_db.replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    try:
        vs = {r[0] for r in con.execute("SELECT variant FROM shindong_day WHERE trade_date=?", (trade_date,))}
        rows = {(r["variant"], r["trade_key"]): dict(r) for r in con.execute(
            "SELECT * FROM shindong_trades WHERE trade_date=?", (trade_date,))}
        return vs, rows
    finally:
        con.close()


# ── 가공 ────────────────────────────────────────────────────────────────
def trade_rows(d: "E.DayFrame", res: Dict[str, Any], stored: Dict, variant: str) -> List[Dict[str, Any]]:
    out, cum = [], 0.0
    for tr in sorted(res["trades"], key=lambda t: t["entry_ts"]):
        net = E.trade_net(tr) if tr["status"] == "CLOSED" else None
        cum += net or 0.0
        span = [k for k in d.idx if tr["entry_ts"] < k <= (tr["exit_ts"] or S.TIME_EXIT)]
        side, e = tr["side"], tr["entry_px"]
        mfe = max([side * ((d.h[k] if side > 0 else d.l[k]) - e) for k in span] or [0.0])
        st = stored.get((variant, _key(tr))) or {}
        out.append(dict(
            key=_key(tr), rule=tr["rule"], side=side, entry_ts=tr["entry_ts"], entry_px=e,
            level=tr.get("touch_level"), stop=tr["stop_init"], t1=tr["t1"], t2=tr["t2"],
            legs=[(g.get("ts"), g.get("px"), g.get("reason")) for g in tr["legs"]],
            exit_ts=tr["exit_ts"], status=tr["status"], net=net, cum=cum, mfe=mfe,
            detected_at=(str(st.get("detected_at"))[11:16] if st.get("detected_at") else None),
            detect_px=st.get("detect_px")))
    return out


def attribute(main: List[Dict], sh: List[Dict], variant: str, d: "E.DayFrame") -> List[str]:
    """MAIN 과 섀도가 어디서 갈렸나 — 차단 · 새 진입 · 청산 차이."""
    mk = {r["key"]: r for r in main}
    sk = {r["key"]: r for r in sh}
    out = []
    sp0 = d.sp.get(S.CONF_BASE)
    for k, r in mk.items():
        if k in sk:
            s = sk[k]
            if abs((s["net"] or 0) - (r["net"] or 0)) >= 1:
                ra = "/".join(REASON.get(x[2], x[2] or "보유") for x in r["legs"])
                sa = "/".join(REASON.get(x[2], x[2] or "보유") for x in s["legs"])
                if ra == sa:
                    why = "목표가 차이 — 1차 %s → %s" % (
                        ("%.2f" % r["t1"]) if r["t1"] else "-", ("%.2f" % s["t1"]) if s["t1"] else "-")
                else:
                    why = "청산 차이 — MAIN %s → %s" % (ra, sa)
                out.append("%s %s %s: %s (%s → %s, 차 %s)" % (
                    r["entry_ts"], r["rule"], _side(r["side"]), why, _man(r["net"]), _man(s["net"]),
                    _man((s["net"] or 0) - (r["net"] or 0))))
            continue
        why = "진입 없음"
        if r["rule"] == "R3":
            if variant == "SHADOW_E2F2" and sp0 is not None and r["entry_ts"] in d.sp:
                trend = -1 if d.sp[r["entry_ts"]] - sp0 > 0 else 1
                if trend != r["side"]:
                    why = "F2 차단(당일 흐름 역방향)"
            if variant in ("SHADOW_X4NF", "SHADOW_X4NFA"):
                prev = [x for x in main if x["rule"] == "R3" and x["level"] == r["level"]
                        and x["entry_ts"] < r["entry_ts"]]
                if prev and prev[-1]["side"] != r["side"]:
                    why = "flip 금지(같은 맥점 %.1f 반대 방향)" % r["level"]
            # [598차] 깨진 맥점 — 진입가가 이미 맥점 반대편(flip 과 겹치면 flip 을 먼저 적는다)
            if variant == "SHADOW_X4NFA" and why == "진입 없음" and is_broken_level(r):
                why = "깨진 맥점 차단(진입 %.2f · 맥점 %.1f)" % (r["entry_px"], r["level"])
            if why == "진입 없음":
                why = "앞 거래 보유 중/시점 이동"
        out.append("%s %s %s: MAIN 진입 %s → **%s** (MAIN 손익 %s 제외)" % (
            r["entry_ts"], r["rule"], _side(r["side"]), "%.2f" % r["entry_px"], why, _man(r["net"])))
    for k, s in sk.items():
        if k not in mk:
            out.append("%s %s %s: **섀도만 진입** %.2f (앞 거래가 없어 신호가 살아남) → %s" % (
                s["entry_ts"], s["rule"], _side(s["side"]), s["entry_px"], _man(s["net"])))
    return out


def is_broken_level(r: Dict[str, Any]) -> bool:
    """[598차] R3 진입가가 터치 맥점을 이미 반대로 넘어가 있는가(매도인데 맥점 위 · 매수인데 맥점 아래).

    SHADOW_X4NFA 가 막는 진입이다. R2·맥점 없는 행은 False.
    """
    if r.get("rule") != "R3" or r.get("level") is None:
        return False
    return r["side"] * (r["entry_px"] - r["level"]) <= 0


def summarize(rows: List[Dict]) -> Dict[str, Any]:
    closed = [r for r in rows if r["net"] is not None]
    net = sum(r["net"] for r in closed)
    return dict(n=len(rows), win=sum(1 for r in closed if r["net"] > 0), net=net,
                worst=min([r["net"] for r in closed] or [0.0]),
                r2=sum(r["net"] for r in closed if r["rule"] == "R2"),
                r3=sum(r["net"] for r in closed if r["rule"] == "R3"),
                open=len(rows) - len(closed))


def cumulative(sd_db: str, until: str) -> Dict[str, Dict[str, Any]]:
    """채점 시작 이후 라이브 기록 누적(변형별 시작일 적용, RETRACTED 제외)."""
    out = {}
    if not sd_db or not os.path.exists(sd_db):
        return out
    con = sqlite3.connect("file:%s?mode=ro" % sd_db.replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    try:
        for v in S.VARIANTS:
            st = S.LATE_SHADOW_START.get(v, S.SCORING_START)
            days = [r[0] for r in con.execute(
                "SELECT trade_date FROM shindong_day WHERE variant=? AND trade_date>=? AND trade_date<=? "
                "AND COALESCE(spec_version, ?)=? ORDER BY trade_date",
                (v, st, until, S.SPEC_VERSION, S.SPEC_VERSION))]     # v2 개정 — 다른 버전 합산 금지
            trs = [dict(r) for r in con.execute(
                "SELECT trade_date, rule, net_krw FROM shindong_trades WHERE variant=? AND trade_date>=? "
                "AND trade_date<=? AND status='CLOSED' AND COALESCE(spec_version, ?)=?",
                (v, st, until, S.SPEC_VERSION, S.SPEC_VERSION))]
            by = {d: 0.0 for d in days}
            for t in trs:
                by[t["trade_date"]] = by.get(t["trade_date"], 0.0) + float(t["net_krw"] or 0)
            r3 = [t for t in trs if t["rule"] == "R3"]
            out[v] = dict(start=st, days=len(days), n=len(trs),
                          win=sum(1 for t in trs if float(t["net_krw"] or 0) > 0),
                          net=sum(by.values()), worst_day=min(by.values()) if by else None,
                          r3n=len(r3), r3net=sum(float(t["net_krw"] or 0) for t in r3),
                          r3win=sum(1 for t in r3 if float(t["net_krw"] or 0) > 0))
    finally:
        con.close()
    return out


def r1_hit(d: "E.DayFrame", bias: Optional[int]) -> Optional[bool]:
    a, b = d.c.get(S.R1_HIT_FROM), d.c.get(d.last_at_or_before(S.R1_HIT_TO) or "")
    if not bias or a is None or b is None or a == b:
        return None
    return bias * (b - a) > 0


def runner_rows(sd_db: str, trade_date: str) -> Optional[List[Dict[str, Any]]]:
    if not sd_db or not os.path.exists(sd_db):
        return None
    con = sqlite3.connect("file:%s?mode=ro" % sd_db.replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    try:
        try:
            return [dict(r) for r in con.execute(
                "SELECT * FROM shindong_mireuk_runner WHERE trade_date=? ORDER BY entry_ts", (trade_date,))]
        except sqlite3.OperationalError:
            return None
    finally:
        con.close()


def observations(day: Dict[str, Any], rows: Dict[str, List[Dict]], sums: Dict[str, Dict]) -> List[str]:
    """자동 관찰 — 판정 아님. 무엇을 봐야 하는지 가리킨다."""
    obs = []
    main = rows["MAIN"]
    losers = [r for r in main if r["net"] is not None and r["net"] < 0]
    if losers:
        shallow = [r for r in losers if r["mfe"] < S.TR44_ACT]
        deep = [r for r in losers if r["mfe"] >= S.TR44_ACT]
        if shallow:
            obs.append("**진입 품질** — MAIN 손실 %d건 중 %d건은 유리한 쪽으로 %.0fpt 도 못 갔다(MFE %s). "
                       "청산을 바꿔서는 못 막는 손실이다 → 진입 필터(E2F2·X4NF·X4NFA) 쪽 관찰 대상."
                       % (len(losers), len(shallow), S.TR44_ACT,
                          ", ".join("%.1f" % r["mfe"] for r in shallow)))
        if deep:
            obs.append("**청산** — MAIN 손실 %d건은 %.0fpt 이상 유리하게 갔다가 손절됐다(MFE %s) → "
                       "트레일(TR44) 쪽 관찰 대상." % (len(deep), S.TR44_ACT, ", ".join("%.1f" % r["mfe"] for r in deep)))
    lv = {}
    for r in main:
        if r["rule"] == "R3":
            lv.setdefault(r["level"], []).append(r)
    for L0, xs in lv.items():
        sides = {x["side"] for x in xs}
        if len(xs) >= 3 or len(sides) > 1:
            obs.append("**맥점 반복** — %.1f 에서 R3 %d회(%s) · 합 %s. 박스권에서 같은 맥점을 %s."
                       % (L0, len(xs), "→".join(_side(x["side"]) for x in xs),
                          _man(sum(x["net"] or 0 for x in xs)),
                          "양쪽으로 번갈아 잡았다" if len(sides) > 1 else "반복해서 잡았다"))
    broken = [r for r in main if is_broken_level(r)]
    if broken:
        obs.append("**깨진 맥점 진입 %d건** — 흐름 반전을 기다리는 사이 가격이 맥점을 다시 넘어간 뒤 들어갔다(%s) "
                   "· 합 %s → X4NFA 가 막는 진입이다."
                   % (len(broken), ", ".join("%s %s %.2f/맥점 %.1f %s" % (
                       r["entry_ts"], _side(r["side"]), r["entry_px"], r["level"], _man(r["net"])) for r in broken),
                      _man(sum(r["net"] or 0 for r in broken))))
    notgt = [r for r in main if r["t1"] is None]
    if notgt:
        obs.append("**목표 없는 진입 %d건** — 가격이 08:50 맥점 범위 밖이라 손절·15:05 로만 끝날 수 있었다(%s)."
                   % (len(notgt), ", ".join("%s %s" % (r["entry_ts"], _man(r["net"])) for r in notgt)))
    lag = [r for r in main if r["detect_px"] is not None and r["detected_at"]]
    if lag:
        cost = sum(r["side"] * (r["entry_px"] - float(r["detect_px"])) * S.PT_VALUE_KRW * S.LEGS for r in lag)
        obs.append("**탐지 지연** — 라이브 진입 %d건, 규칙가 대비 실현가능가 차 %s(음수 = 늦게 알아채 손해)."
                   % (len(lag), _won(cost)))
    best = max(sums, key=lambda v: sums[v]["net"])
    if best != "MAIN":
        obs.append("**오늘 최선은 %s** (%s, MAIN 대비 %s). 하루 결과다 — 판정은 사전등록 창(10거래일)으로만."
                   % (VLABEL[best], _man(sums[best]["net"]), _man(sums[best]["net"] - sums["MAIN"]["net"])))
    else:
        obs.append("**오늘은 MAIN 이 최선** (%s)." % _man(sums["MAIN"]["net"]))
    obs.append("⚠ 규격 변경은 사전등록 §6(새 버전 · 재채점)으로만. 이 절은 관찰이다.")
    return obs


# ── 차트(SVG, 외부 라이브러리 없음) ───────────────────────────────────────
def svg_chart(day: Dict[str, Any], rows: Dict[str, List[Dict]], title: str) -> str:
    d, L = day["d"], day["L"]
    idx = [k for k in d.idx if "08:45" <= k <= "15:10" and k in d.c]
    if not idx:
        return ""
    W, left, right, top = 1100, 64, 150, 36
    ph, gap, fh = 150, 26, 110
    vs = list(S.VARIANTS)
    H = top + len(vs) * (ph + gap) + fh + 58
    pw = W - left - right
    lo = min(d.l[k] for k in idx)
    hi = max(d.h[k] for k in idx)
    pad = (hi - lo) * 0.06 or 1.0
    lo, hi = lo - pad, hi + pad

    def xm(hm):
        m = int(hm[:2]) * 60 + int(hm[3:5])
        return left + pw * (m - (8 * 60 + 45)) / float(15 * 60 + 10 - (8 * 60 + 45))

    def yp(p, y0):
        return y0 + ph * (hi - p) / (hi - lo)

    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="Malgun Gothic, Apple SD Gothic Neo, sans-serif" font-size="11">' % (W, H, W, H),
         '<rect width="100%" height="100%" fill="#ffffff"/>',
         '<text x="%d" y="22" font-size="15" font-weight="bold" fill="#222">%s</text>' % (left, title)]
    struct = sorted(set(L["0850"]["S"]))
    ticks = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]
    for i, v in enumerate(vs):
        y0 = top + i * (ph + gap) + 14
        o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#fafafa" stroke="#e3e3e3"/>' % (left, y0, pw, ph))
        for t in ticks:
            o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#eee"/>' % (xm(t), y0, xm(t), y0 + ph))
        for s_ in struct:
            if lo < s_ < hi:
                o.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#c9b37a" stroke-dasharray="3,3" '
                         'stroke-width="0.8"/>' % (left, yp(s_, y0), left + pw, yp(s_, y0)))
                if i == 0:
                    o.append('<text x="%d" y="%.1f" fill="#9c8446" font-size="9">%.0f</text>'
                             % (left - 30, yp(s_, y0) + 3, s_))
        pts = " ".join("%.1f,%.1f" % (xm(k), yp(d.c[k], y0)) for k in idx)
        o.append('<polyline points="%s" fill="none" stroke="#8a8f98" stroke-width="1.1"/>' % pts)
        tot = sum(r["net"] or 0 for r in rows[v])
        o.append('<text x="%d" y="%d" font-weight="bold" fill="#333">%s</text>' % (left, y0 - 4, VLABEL[v]))
        o.append('<text x="%d" y="%d" font-size="14" font-weight="bold" fill="%s">%s</text>' % (
            left + pw + 10, y0 + 22, "#1a7f37" if tot >= 0 else "#cf222e", _man(tot)))
        o.append('<text x="%d" y="%d" fill="#666">%d거래 %d승</text>' % (
            left + pw + 10, y0 + 40, len(rows[v]), sum(1 for r in rows[v] if (r["net"] or 0) > 0)))
        for n, r in enumerate(rows[v], 1):
            col = "#1a7f37" if (r["net"] or 0) >= 0 else "#cf222e"
            ex = [g for g in r["legs"] if g[0]]
            xe, ye = xm(r["entry_ts"]), yp(r["entry_px"], y0)
            for g in ex:
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" '
                         'opacity="0.75"/>' % (xe, ye, xm(g[0]), yp(g[1], y0), col))
                o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12" text-anchor="middle">×</text>'
                         % (xm(g[0]), yp(g[1], y0) + 4, col))
            tri = ("%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (xe, ye - 7, xe - 5, ye + 2, xe + 5, ye + 2) if r["side"] > 0
                   else "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (xe, ye + 7, xe - 5, ye - 2, xe + 5, ye - 2))
            o.append('<polygon points="%s" fill="%s"/>' % (tri, "#1a7f37" if r["side"] > 0 else "#cf222e"))
            o.append('<text x="%.1f" y="%.1f" font-size="10" fill="#333" text-anchor="middle">%d</text>'
                     % (xe, ye + (-10 if r["side"] > 0 else 17), n))
            if n <= 6:                          # 패널 높이 안 — 넘치면 잔여 개수만(계측 4원칙 ③)
                o.append('<text x="%d" y="%d" fill="%s">%d %s%s %s</text>' % (
                    left + pw + 10, y0 + 58 + 14 * (n - 1), col, n, r["rule"], "▲" if r["side"] > 0 else "▼",
                    _man(r["net"])))
            elif n == 7:
                o.append('<text x="%d" y="%d" fill="#666">… 외 %d건</text>' % (
                    left + pw + 10, y0 + 58 + 14 * 6, len(rows[v]) - 6))
    # 흐름
    y0 = top + len(vs) * (ph + gap) + 14
    fl = [k for k in idx if k in d.sp]
    o.append('<text x="%d" y="%d" font-weight="bold" fill="#333">개인 위클리 콜−풋(백만원) — 양수 = 하방 방향</text>'
             % (left, y0 - 4))
    o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#fafafa" stroke="#e3e3e3"/>' % (left, y0, pw, fh))
    if fl:
        a, b = min(d.sp[k] for k in fl + [fl[0]]), max(d.sp[k] for k in fl)
        a, b = min(a, 0.0), max(b, 0.0)
        span = (b - a) or 1.0
        yf = lambda v_: y0 + fh * (b - v_) / span
        o.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#bbb"/>' % (left, yf(0), left + pw, yf(0)))
        o.append('<polyline points="%s" fill="none" stroke="#6f42c1" stroke-width="1.2"/>'
                 % " ".join("%.1f,%.1f" % (xm(k), yf(d.sp[k])) for k in fl))
        o.append('<text x="%d" y="%.1f" fill="#6f42c1" font-size="10">%+.0f</text>' % (left + pw + 6, yf(d.sp[fl[-1]]) + 3, d.sp[fl[-1]]))
    else:
        o.append('<text x="%d" y="%d" fill="#999">흐름 미수집</text>' % (left + 10, y0 + 20))
    for t in ticks:
        o.append('<text x="%.1f" y="%d" fill="#777" text-anchor="middle">%s</text>' % (xm(t), y0 + fh + 14, t))
    o.append('<text x="%d" y="%d" fill="#999" font-size="10">▲매수 ▼매도 진입 · × 청산(다리별) · 금색 점선 = 08:50 구조맥점 · '
             '선 색 = 거래 손익</text>' % (left, H - 8))
    o.append("</svg>")
    return "\n".join(o)


# ── 조립 ────────────────────────────────────────────────────────────────
def _timeline(rows: List[Dict], live: bool) -> List[str]:
    out = ["| # | 규칙 | 방향 | 진입 | 맥점 | 손절 | 1차 · 최종 | 청산(다리별) | MFE | 손익 | 누적 |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, r in enumerate(rows, 1):
        legs = " · ".join("%s %s %.2f" % (REASON.get(g[2], g[2]), g[0], g[1]) if g[0] else "보유" for g in r["legs"])
        ent = "%s %.2f" % (r["entry_ts"], r["entry_px"])
        if live and r["detected_at"]:
            ent += " (탐지 %s)" % r["detected_at"]
        out.append("| %d | %s | %s | %s | %s | %.2f | %s · %s | %s | %.1f | **%s** | %s |" % (
            n, r["rule"], _side(r["side"]), ent, ("%.1f" % r["level"]) if r["level"] else "-", r["stop"],
            ("%.2f" % r["t1"]) if r["t1"] else "-", ("%.2f" % r["t2"]) if r["t2"] else "-", legs,
            r["mfe"], _man(r["net"]), _man(r["cum"])))
    if not rows:
        out.append("| - | 거래 없음 | | | | | | | | | |")
    return out


def build(trade_date: str, raw_db: str, flow_db: str, levels_db: str, sd_db: str,
          out_dir: Optional[str] = None, now: Optional[_dt.datetime] = None,
          pc: Optional[str] = None) -> Dict[str, Any]:
    now = now or _dt.datetime.now()
    if pc is None:
        from utils.db_utils import pc_id
        pc = pc_id()
    stem = report_stem(trade_date, pc)
    day = load_day(trade_date, raw_db, flow_db, levels_db)
    ymd = trade_date.replace("-", "")
    lines: List[str] = []
    w = lines.append
    w("# [%s] 신동 일일 리포트 — %s" % (pc, trade_date))
    w("")
    w("> **%s 리포트** · 생성 %s · 규격 `%s` · 상품 `%s` (%s)" % (pc, now.strftime("%Y-%m-%d %H:%M"), S.SPEC_VERSION,
                                             day["product"], day["product_note"]))
    w("> 가상거래다 — 주문 없음(절대원칙 §6). 손익은 미니선물 2계약 · CYBOS 요율 · 1틱 슬리피지 기준.")
    w("")
    if not day["ok"]:
        w("**판정 불가 — %s.**" % day["why"])
        # 휴장일·봉 결측일은 파일을 만들지 않는다(빈 리포트가 쌓이면 「그날 거래 0건」으로 오독된다)
        return _write(lines, None, stem, None, {"ok": False, "why": day["why"], "pc": pc})
    d, L = day["d"], day["L"]
    live_vs, stored = _stored(sd_db, trade_date)
    rows = {v: trade_rows(d, day["results"][v], stored, v) for v in S.VARIANTS}
    sums = {v: summarize(rows[v]) for v in S.VARIANTS}
    dec = day["results"]["MAIN"]["decision"]
    bias = dec.get("bias")
    hit = r1_hit(d, bias)
    o9, c15 = d.c.get("09:00"), d.c.get(d.last_at_or_before(S.TIME_EXIT) or "")
    # [MW0602 598차] 봉 있는 분만 — 09:00 1분봉 결손일(2026-09-29)에 KeyError 로 리포트·메일이 통째로 빠졌다
    hi = max(d.h[k] for k in d.idx if "09:00" <= k <= "15:05" and k in d.h)
    lo = min(d.l[k] for k in d.idx if "09:00" <= k <= "15:05" and k in d.l)

    # 0. 한눈에
    w("## 0. 한눈에")
    w("")
    w("| 시장 | R1 장전 | R2 개장확정 | R1 적중(09:00→15:05) |")
    w("|---|---|---|---|")
    w("| %s → %s (%s) · 고 %.2f · 저 %.2f · 폭 %.1fpt | 콜−풋 %s → **%s** | %s | %s |" % (
        ("%.2f" % o9) if o9 else "09:00봉 결손", ("%.2f" % c15) if c15 else "-",
        ("%+.2f" % (c15 - o9)) if (o9 and c15) else "-", hi, lo, hi - lo,
        ("%+.0f" % dec["pm_sp"]) if dec.get("pm_sp") is not None else "미수집",
        {-1: "하방", 0: "보류", 1: "상방"}.get(bias, "?"),
        (dec.get("r2") or "-") + ((" " + dec["r2_ts"]) if dec.get("r2_ts") else ""),
        {True: "✅ 적중", False: "❌ 불적중", None: "미측정/보류"}[hit]))
    w("")
    w("| 변형 | 거래 | 승 | R2 | R3 | **순손익** | 최악 거래 | MAIN 대비 | 기록 |")
    w("|---|---|---|---|---|---|---|---|---|")
    for v in S.VARIANTS:
        s = sums[v]
        w("| %s | %d | %d | %s | %s | **%s** | %s | %s | %s |" % (
            VLABEL[v], s["n"], s["win"], _man(s["r2"]), _man(s["r3"]), _man(s["net"]), _man(s["worst"]),
            "—" if v == "MAIN" else _man(s["net"] - sums["MAIN"]["net"]),
            "라이브" if v in live_vs else "재계산"))
    best = max(S.VARIANTS, key=lambda v: sums[v]["net"])
    w("")
    w("**오늘의 한 줄** — MAIN %s(%d거래 %d승)%s." % (
        _man(sums["MAIN"]["net"]), sums["MAIN"]["n"], sums["MAIN"]["win"],
        "" if best == "MAIN" else ", 최선은 %s %s(MAIN 대비 %s)" % (
            VLABEL[best], _man(sums[best]["net"]), _man(sums[best]["net"] - sums["MAIN"]["net"]))))
    if any(v not in live_vs for v in S.VARIANTS):
        w("")
        w("> 「재계산」 = 그날 라이브 기록이 없어 엔진으로 다시 돌린 값(같은 엔진·같은 입력). 탐지 시각은 없다.")
    w("")

    # 1. 차트
    svg = svg_chart(day, rows, "[%s] 신동 %s — 변형별 거래 흐름" % (pc, trade_date))
    w("## 1. 차트")
    w("")
    w("![신동 %s](%s.svg)" % (trade_date, stem))
    w("")

    # 2. 거래 흐름
    w("## 2. 거래 흐름 — MAIN")
    w("")
    lines.extend(_timeline(rows["MAIN"], True))
    w("")

    # 3. 섀도 흐름
    w("## 3. 섀도 흐름 — MAIN 과 무엇이 달랐나")
    w("")
    for v in S.VARIANTS[1:]:
        w("### %s — %s (MAIN 대비 %s)" % (VLABEL[v], _man(sums[v]["net"]), _man(sums[v]["net"] - sums["MAIN"]["net"])))
        w("")
        diff = attribute(rows["MAIN"], rows[v], v, d)
        if diff:
            for x in diff:
                w("- " + x)
        else:
            w("- MAIN 과 같다")
        w("")
        lines.extend(_timeline(rows[v], v in live_vs))
        w("")

    # 4. 누적
    cum = cumulative(sd_db, trade_date)
    w("## 4. 누적 채점 (라이브 기록 · 판정 창)")
    w("")
    if cum:
        w("| 변형 | 채점 시작 | 거래일 | 거래 | 승률 | 순손익 | 최악일 | R3 (건 · 승률 · 순) | 판정 |")
        w("|---|---|---|---|---|---|---|---|---|")
        for v in S.VARIANTS:
            c = cum.get(v) or {}
            if not c.get("days"):
                w("| %s | %s | 0 | - | - | - | - | - | 기록 전 |" % (VLABEL[v], c.get("start", "-")))
                continue
            if v == "MAIN":
                jd = "R3 중단 판정 %d/%d일" % (c["days"], S.R3_KILL_AFTER_DAYS)
            elif v in S.LATE_SHADOW_START:
                jd = "MAIN 비교 %d/%d일" % (c["days"], S.X4NF_JUDGE_AFTER_DAYS)
            else:
                jd = "MAIN 비교 %d/%d일" % (c["days"], S.R3_KILL_AFTER_DAYS)
            w("| %s | %s | %d | %d | %s | **%s** | %s | %d · %s · %s | %s |" % (
                VLABEL[v], c["start"], c["days"], c["n"],
                ("%.0f%%" % (100.0 * c["win"] / c["n"])) if c["n"] else "-", _man(c["net"]), _man(c["worst_day"]),
                c["r3n"], ("%.0f%%" % (100.0 * c["r3win"] / c["r3n"])) if c["r3n"] else "-", _man(c["r3net"]), jd))
        w("")
        w("> 판정 전 집계다 — 인용·규격 변경 근거로 쓰지 말 것. R3 중단 기준: 순손익 < 0 **그리고** 승률 < %.0f%%."
          % (100 * S.R3_KILL_WINRATE_MAX))
    else:
        w("- 기록 DB 없음(미배선 — 0건이 아니다)")
    w("")

    # 5. 러너
    rr = runner_rows(sd_db, trade_date)
    w("## 5. 러너 섀도 — 미륵이 × 신동 (CREON 요율)")
    w("")
    if rr is None:
        w("- 기록 테이블 없음(미배선)")
    elif not rr:
        w("- 오늘 기록 없음 — 미륵이 시스템 진입이 없었거나 장후 기록 전이다")
    else:
        w("| 미륵이 진입 | 방향 | 조건 | 러너 | 실제 | 러너 적용 | 차이 | 필터 B |")
        w("|---|---|---|---|---|---|---|---|")
        for r in rr:
            w("| %s %.2f ×%d | %s | %s | %s | %s | %s | **%s** | %s |" % (
                str(r["entry_ts"])[11:16], r["entry_px"], r["qty"], _side(r["side"]),
                {1: "충족", 0: "불충족", None: "미측정"}.get(r["cond_met"]),
                ("%s %s" % (r.get("runner_reason") or "-", r.get("runner_exit_ts") or "")) if r["applied"]
                else (r.get("skip_reason") or "-"),
                _man(r["act_net_krw"]), _man(r["shadow_net_krw"]), _man(r["diff_krw"]),
                {1: "통과", 0: "제외", None: "미측정"}.get(r.get("filt_b_pass"))))
        w("")
        w("- 합: 실제 %s → 러너 %s (차 %s)" % (
            _man(sum(r["act_net_krw"] for r in rr)), _man(sum(r["shadow_net_krw"] for r in rr)),
            _man(sum(r["diff_krw"] for r in rr))))
    w("")

    # 6. 개선 방향
    w("## 6. 개선 방향 (자동 관찰 — 판정 아님)")
    w("")
    for x in observations(day, rows, sums):
        w("- " + x)
    w("")
    w("---")
    w("재생성: `python scripts/shindong_daily_report.py %s`" % trade_date)
    return _write(lines, svg, stem, out_dir, {"ok": True, "sums": sums, "best": best, "hit": hit, "pc": pc})


def _write(lines, svg, stem, out_dir, meta):
    md = "\n".join(lines) + "\n"
    meta = dict(meta, md=md, svg=svg)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        p = os.path.join(out_dir, stem + ".md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(md)
        meta["md_path"] = p
        if svg:
            q = os.path.join(out_dir, stem + ".svg")
            with open(q, "w", encoding="utf-8") as f:
                f.write(svg)
            meta["svg_path"] = q
    return meta
