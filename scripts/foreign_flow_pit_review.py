# -*- coding: utf-8 -*-
"""[MW0601 662차 후속] 신동2 — 외인 수급 시점별(PIT) 방향·진입·손절·청산 제안 + 장후 채점.

진행자 이름 「신동2」(사용자 명명 2026-10-06). 「신동」(strategy/shindong, 개인 위클리 흐름)과 별개 주체다.

무엇을 하나
-----------
그날 08:55–09:55(기본) 10분마다, **그 시각 이전에 찍힌 데이터만으로** 고정 규칙을 돌려
당일 방향 · 진입가 · 손절가 · 청산가를 낸다. 그 뒤 장 마감 1분봉으로 각 제안을 채점한다.
마지막에 장 마감 데이터 전체로 같은 규칙을 한 번 더 돌려 **다음 날 계획**의 재료를 낸다.

🔴 미래 참조 금지 — 원천별 컷오프(시각 T 의 제안)
  · 1분봉(regular_candles A056A)     봉 시각 < T            (봉은 시작 시각 표기 → T 직전 봉까지 완결)
  · 선물 투자자(7221 raw_investor_futures)  ts < T          (ts = 조회 시각 분 내림, 실제 +8초)
  · 옵션·현물 투자자(7222 option_flow)       bar_time < T
  · 9842 시점 파일(data/db/option_hts)       파일 mtime ≤ T  (이름 HHMM 이 아니라 **저장 시각**)
  · 맥점(premarket_levels)                    08:50 단계 → 08:51 부터, 09:30 단계 → 09:31 부터
  · 행사가 OI 벽·베이시스(option_book_snap)  스냅샷 시각 ≤ T. 베이시스도 T 까지의 중앙값만
    (사다리 books() 는 하루 전체 중앙값을 쓴다 — 여기서는 쓰지 않는다)
  7222 는 장후 백필로 다시 받은 값이지만 값 자체는 장중 라이브와 같다(10/6 09:30 대조 일치).

규칙 (사전 고정 — 결과를 보고 바꾸면 그 사실을 리포트에 남길 것)
  점수 = Σ 가중 × 부호, 각 항은 T 직전 10분 변화(Δ10) 또는 수준
    F1 선물 외인 Δ10            ×2   (|Δ|<50계약이면 0)
    F2 선물 외인 누계 수준      ×1   (|x|<300 이면 0)
    O1 먼스리 외인 (콜−풋) Δ10   ×1   (|Δ|<100 이면 0)   콜 매수·풋 매도 = 상방
    O2 위클리 외인 (콜−풋) Δ10   ×1   (|Δ|<200 이면 0)
    S1 현물 외인 Δ10            ×1   (|Δ|<100 이면 0)   7222 kospi_spot
    P1 가격 Δ10                 ×1   (|Δ|<1.0pt 이면 0)
  방향: 점수 ≥ +3 → 매수, ≤ −3 → 매도, 그 외 관망
  가격:
    기준가 = T 직전 봉 종가, ATR = 직전 14봉 TR 평균(최소 1.0pt)
    진입  = 매도면 기준가 위 3pt 안의 가장 가까운 저항(맥점·콜벽)에 지정가, 없으면 기준가(다음 봉 시가 시장가)
            매수는 대칭(아래 3pt 안 지지·풋벽)
    손절  = 진입 너머 가장 가까운 맥점 +1pt, 단 거리 [1.5×ATR, 8pt] 로 자름(없으면 1.5×ATR)
    청산  = 진입에서 손절거리 ×1.5 이상 떨어진 가장 가까운 맥점, 없으면 손절거리 ×2
  채점:
    지정가는 T 이후 30분 안에 닿아야 체결(못 닿으면 「미체결」). 시장가는 T 봉 시가.
    체결 뒤 손절·청산 중 먼저 닿는 쪽. 같은 봉에서 둘 다 닿으면 **손절**(보수).
    둘 다 없으면 15:10 강제청산(절대원칙 §1) — 15:09 봉 종가.
    방향 적중 = sign(15:09 종가 − 기준가) 가 방향과 같은가(관망은 채점 제외).

산출물: docs/미륵이고도화3/미래예측/ — 시점별 제안·채점·레슨런·익일 계획 문서는 전부 이 폴더에 둔다
      (첫 문서: 외인수급_시점별_방향제안_PIT복기_MW0601-20261006.md).

실행 (장 마감 후 전용 — 456차):
    python scripts/foreign_flow_pit_review.py --date 2026-10-06
    python scripts/foreign_flow_pit_review.py --date 2026-10-06 --start 08:55 --end 09:55 --step 10 --json out.json
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "maekjeom_ladder"))

from utils.analysis_db import guard_intraday   # noqa: E402
import ladder_data as L                          # noqa: E402

DB = os.path.join(ROOT, "data", "db")

# ── 사전 고정 파라미터 ────────────────────────────────────────────────────
W = dict(F1=2, F2=1, O1=1, O2=1, S1=1, P1=1)
DEAD = dict(F1=50, F2=300, O1=100, O2=200, S1=100, P1=1.0)
SCORE_GO = 3
LOOK = 10            # Δ 창(분)
NEAR_ENTRY = 3.0     # 진입 지정가 탐색 폭(pt)
FILL_WIN = 30        # 지정가 유효(분)
STOP_ATR = 1.5
STOP_MAX = 8.0
RR_MIN = 1.5
RR_DEF = 2.0
FORCE_EXIT = "15:10"
BASIS_MIN_SNAPS = 3


def _ro(name):
    return sqlite3.connect("file:%s?mode=ro" % os.path.join(DB, name).replace("\\", "/"), uri=True, timeout=5.0)


def _hm(t):
    return int(t[:2]) * 60 + int(t[3:5])


def _fmt(m):
    return "%02d:%02d" % (m // 60, m % 60)


# ── 원천 적재(하루치 한 번) ────────────────────────────────────────────────
def load(day, cs=None, fut=None):
    """cs·fut 를 넘기면 그 원천은 다시 읽지 않는다 — 사다리 서버가 장중에 이미 받은 봉·7221 캐시를 넘긴다(456차)."""
    if cs is None:
        con = _ro("regular_candles.db")
        # 2자리 반올림 — DB 가 float32 라 1108.300048… 처럼 저장된다. 사다리(ladder_data)와 같은 값으로 맞춰야
        # 「종가가 레벨을 넘었나」 판정이 두 경로에서 같다(10/2 13:04 vs 13:10 불일치 실측).
        cs = [[t, round(o, 2), round(h, 2), round(l, 2), round(c, 2)] for t, o, h, l, c in con.execute(
            "SELECT substr(ts,12,5), open, high, low, close FROM regular_candles WHERE code=? AND trade_date=?"
            " AND substr(ts,12,5) BETWEEN '08:45' AND '15:45' ORDER BY ts", (L.MINI_CODE, day))]
        con.close()

    if fut is None:
        con = _ro("raw_data.db")
        fut = []
        for ts, fj in con.execute("SELECT ts, fields FROM raw_investor_futures WHERE ts >= ? AND ts <= ? ORDER BY ts",
                                  (day + " 08:45:00", day + " 15:59:59")):
            f = json.loads(fj)
            fut.append((ts[11:16], f.get("foreign_net_qty"), f.get("institution_net_qty"), f.get("retail_net_qty")))
        con.close()

    con = _ro("option_flow.db")
    flow = {}
    for t, p, i, q in con.execute("SELECT bar_time, product, investor, net_qty FROM option_investor_flow"
                                  " WHERE trade_date=?", (day,)):
        flow.setdefault((p, i), []).append((t, q))
    con.close()
    for k in flow:
        flow[k].sort()

    lv, _bands = L.levels(day)

    snaps = []
    for db in ("option_book.db", "option_book_fuo.db"):
        if not os.path.exists(os.path.join(DB, db)):
            continue
        con = _ro(db)
        rows = con.execute("SELECT substr(ts,12,5), book, spot, call_wall, put_wall, n_valid FROM option_book_snap"
                           " WHERE ts LIKE ? AND book='monthly' ORDER BY ts", (day + "%",)).fetchall()
        con.close()
        if rows:
            snaps = [r for r in rows if (r[5] or 0) > 0]
            break

    snaps9842 = []
    yymmdd = day[2:4] + day[5:7] + day[8:10]
    for f in L._list_9842_files():
        if f["date"] == day and f["mode"] == "D":
            p = os.path.join(L.DOCS_9842, f["fn"])
            mt = _dt.datetime.fromtimestamp(os.path.getmtime(p))
            if mt.date().isoformat() == day:            # 그날 저장된 파일만 시점 정보로 쓴다
                snaps9842.append((mt.strftime("%H:%M"), f["fn"], p))
    snaps9842.sort()
    return dict(cs=cs, fut=fut, flow=flow, lv=lv, snaps=snaps, s9842=snaps9842, yymmdd=yymmdd)


# ── 시점 T 의 관측(엄격 컷오프) ────────────────────────────────────────────
def _last_before(series, T, back=0):
    """series=[(hm, v)] 에서 hm < T−back 인 마지막 값."""
    lim = _hm(T) - back
    v = None
    for t, x in series:
        if _hm(t) < lim and x is not None:
            v = x
        elif _hm(t) >= lim:
            break
    return v


def _d(series, T):
    a, b = _last_before(series, T), _last_before(series, T, LOOK)
    if a is None:
        return None, None
    return a, (a - b if b is not None else None)


def observe(S, T):
    cs = [c for c in S["cs"] if _hm(c[0]) < _hm(T)]
    o = dict(T=T, n_bars=len(cs))
    if not cs:
        return o
    o["px"] = round(cs[-1][4], 2)
    o["open"] = round(cs[0][1], 2)          # 그날 첫 봉 시가(08:45)
    prev = [c for c in cs if _hm(c[0]) < _hm(T) - LOOK]
    o["dpx"] = round(o["px"] - prev[-1][4], 2) if prev else None
    trs = []
    for i, c in enumerate(cs):
        pc = cs[i - 1][4] if i else c[1]
        trs.append(max(c[2] - c[3], abs(c[2] - pc), abs(c[3] - pc)))
    o["atr"] = max(1.0, round(sum(trs[-14:]) / len(trs[-14:]), 2))
    o["hi"], o["lo"] = round(max(c[2] for c in cs), 2), round(min(c[3] for c in cs), 2)

    fser = [(t, f) for t, f, _, _ in S["fut"]]
    o["fut_for"], o["fut_for_d"] = _d(fser, T)
    o["fut_ins"] = _last_before([(t, i) for t, _, i, _ in S["fut"]], T)

    def ocd(prod):
        c, cd = _d(S["flow"].get((prod + "_call", "foreign"), []), T)
        p, pd = _d(S["flow"].get((prod + "_put", "foreign"), []), T)
        if c is None or p is None:
            return None, None, None, None
        return c, p, c - p, (cd - pd if cd is not None and pd is not None else None)
    o["mon_c"], o["mon_p"], o["mon_cp"], o["mon_cp_d"] = ocd("mon")
    o["wk_c"], o["wk_p"], o["wk_cp"], o["wk_cp_d"] = ocd("wk_mon")
    o["spot"], o["spot_d"] = _d(S["flow"].get(("kospi_spot", "foreign"), []), T)

    sn = [s for s in S["snaps"] if _hm(s[0]) <= _hm(T)]
    cmap = {c[0]: c[4] for c in cs}
    bas = sorted(cmap[s[0]] - s[2] for s in sn if s[2] and s[0] in cmap)
    # 스냅샷 3개 미만이면 미측정 — 10/6 09:05 첫 스냅샷 하나로 −3.37 이 나와 벽이 4pt 어긋났다(계측 4원칙 ②)
    o["basis"] = round(bas[len(bas) // 2], 2) if len(bas) >= BASIS_MIN_SNAPS else None
    o["call_wall"] = sn[-1][3] if sn else None
    o["put_wall"] = sn[-1][4] if sn else None

    o["levels"] = sorted({round(x["price"], 2) for x in S["lv"] if _hm(x["start"]) <= _hm(T)})
    walls = []
    if o["basis"] is not None:
        if o["call_wall"]:
            walls.append(("콜벽", round(o["call_wall"] + o["basis"], 2)))
        if o["put_wall"]:
            walls.append(("풋벽", round(o["put_wall"] + o["basis"], 2)))
    o["walls"] = walls
    o["s9842"] = [hm + " " + fn for hm, fn, _ in S["s9842"] if _hm(hm) <= _hm(T)]
    return o


# ── 규칙 ────────────────────────────────────────────────────────────────
def _sg(v, dead):
    if v is None or abs(v) < dead:
        return 0
    return 1 if v > 0 else -1


def decide(o):
    if "px" not in o:
        return dict(dir="관망", score=0, terms={}, why="1분봉 없음")
    terms = dict(F1=_sg(o.get("fut_for_d"), DEAD["F1"]), F2=_sg(o.get("fut_for"), DEAD["F2"]),
                 O1=_sg(o.get("mon_cp_d"), DEAD["O1"]), O2=_sg(o.get("wk_cp_d"), DEAD["O2"]),
                 S1=_sg(o.get("spot_d"), DEAD["S1"]), P1=_sg(o.get("dpx"), DEAD["P1"]))
    sc = sum(W[k] * v for k, v in terms.items())
    d = "매수" if sc >= SCORE_GO else "매도" if sc <= -SCORE_GO else "관망"
    r = dict(dir=d, score=sc, terms=terms)
    if d == "관망":
        return r
    px, atr = o["px"], o["atr"]
    sgn = 1 if d == "매수" else -1
    lvls = [(p, "맥점") for p in o["levels"]] + [(p, n) for n, p in o["walls"]]
    # 진입: 유리한 쪽 3pt 안의 가장 가까운 레벨(매도=위, 매수=아래)
    cand = [(abs(p - px), p, n) for p, n in lvls if 0 < (px - p) * sgn <= NEAR_ENTRY]
    if cand:
        _, entry, en = min(cand)
        r["entry_type"], r["entry_src"] = "지정가", en
    else:
        entry, r["entry_type"], r["entry_src"] = px, "시장가", "기준가"
    r["entry"] = round(entry, 2)
    # 손절: 진입 너머 가장 가까운 맥점 +1pt, [1.5ATR, 8pt]
    beyond = sorted(((p - entry) * -sgn, p) for p, _ in lvls if (p - entry) * -sgn > 0)
    dist = (beyond[0][0] + 1.0) if beyond else STOP_ATR * atr
    dist = min(max(dist, STOP_ATR * atr), STOP_MAX)
    r["stop"] = round(entry - sgn * dist, 2)
    # 청산: 손절거리×1.5 이상 떨어진 가장 가까운 레벨, 없으면 ×2
    tg = sorted(((p - entry) * sgn, p) for p, _ in lvls if (p - entry) * sgn >= RR_MIN * dist)
    r["target"] = round(tg[0][1] if tg else entry + sgn * RR_DEF * dist, 2)
    r["risk"] = round(dist, 2)
    return r


# ── 채점 ────────────────────────────────────────────────────────────────
def grade(S, T, o, r, live=False):
    """live=True(장중): 아직 안 끝난 거래를 15:10 강제청산으로 치지 않는다 — 「보유 중」·「대기」로 둔다."""
    if r["dir"] == "관망" or "px" not in o:
        return dict(result="관망")
    sgn = 1 if r["dir"] == "매수" else -1
    after = [c for c in S["cs"] if _hm(c[0]) >= _hm(T) and _hm(c[0]) < _hm(FORCE_EXIT)]
    if not after:
        return dict(result="데이터 없음")
    close_ref = round(after[-1][4], 2)
    ongoing = live and _hm(after[-1][0]) < _hm(FORCE_EXIT) - 1        # 15:09 봉이 아직 없다
    g = dict(dir_hit=None if ongoing else (close_ref - o["px"]) * sgn > 0, close_1509=None if ongoing else close_ref)
    i0 = None
    if r["entry_type"] == "시장가":
        i0, fill = 0, after[0][1]
    else:
        for i, c in enumerate(after):
            if _hm(c[0]) >= _hm(T) + FILL_WIN:
                break
            if c[3] <= r["entry"] <= c[2]:
                i0, fill = i, r["entry"]
                break
    if i0 is None:
        if ongoing and _hm(after[-1][0]) < _hm(T) + FILL_WIN:
            g.update(result="대기", pnl=None)
        else:
            g.update(result="미체결", pnl=0.0)
        return g
    g["fill_t"], g["fill"] = after[i0][0], fill
    mfe = mae = 0.0
    for c in after[i0:]:
        fav = (c[2] - fill) if sgn > 0 else (fill - c[3])
        adv = (fill - c[3]) if sgn > 0 else (c[2] - fill)
        mfe, mae = max(mfe, fav), max(mae, adv)
        hit_stop = (c[3] <= r["stop"]) if sgn > 0 else (c[2] >= r["stop"])
        hit_tgt = (c[2] >= r["target"]) if sgn > 0 else (c[3] <= r["target"])
        if hit_stop:
            g.update(result="손절", exit_t=c[0], exit=r["stop"], pnl=round((r["stop"] - fill) * sgn, 2))
            break
        if hit_tgt:
            g.update(result="청산(목표)", exit_t=c[0], exit=r["target"], pnl=round((r["target"] - fill) * sgn, 2))
            break
    else:
        if ongoing:
            g.update(result="보유 중", mark_t=after[-1][0], mark=close_ref, pnl=round((close_ref - fill) * sgn, 2))
        else:
            g.update(result="15:10 강제청산", exit_t=after[-1][0], exit=close_ref, pnl=round((close_ref - fill) * sgn, 2))
    g["mfe"], g["mae"] = round(mfe, 2), round(mae, 2)
    return g


# ── 신동2-P (피터식 보유) — 섀도 변형, 사전등록 SD2P-2026-10-06-v1 ─────────────
# 규격 문서: docs/미륵이고도화3/미래예측/신동2-P_사전등록_MW0601-20261006.md
# 근거: 피터 누적 49건(8/4–10/6) — 손실 −3 – −6 고정, 손익비 2.46, 손절 후 같은 방향 재진입 16 대 반대 3.
# ⚠ 아래 값은 10/6 결과를 본 뒤 정했다 — 10/6 은 드라이런이며 채점에서 제외한다(채점 시작 10/7).
P_VER = "SD2P-2026-10-06-v1"
P_CHECKS = ("09:05", "09:15", "09:25", "09:35", "09:45", "09:55")   # 세팅 판정 시각(10분)
P_BIAS = dict(O1L=1000, F2=300, O2L=1000, PX=3.0)                     # 수준 항 데드밴드 — Δ10 은 쓰지 않는다
P_BIAS_GO = 2            # |B| ≥ 2 면 세팅
P_STOP = 4.0             # 고정 손절(pt), 하한 1.5×ATR, 상한 P_STOP_MAX — 보유 중 넓히지 않는다
P_STOP_MAX = 5.0
P_HALF_R = 1.5           # 절반 청산 손익비 → 나머지는 본전 손절
P_FAR_R = 3.0            # 최종 목표 = 진입 시 보이는 가장 먼 맥점이 3R 이상이면 그것, 아니면 15:10
P_NEAR = 3.0             # 되돌림 지정가 탐색 폭
P_WINDOWS = (("09:00", "10:30"), ("13:00", "14:30"))   # 신규·재진입 허용 시간대
P_REARM = ("13:00",)     # 오후 창 시작 — 세팅이 있고 무포지션이면 그 시각 데이터로 다시 대기
P_MAX_ENTRIES = 3
P_DAY_STOP_N = 3         # 손절 3회 → 당일 종료
P_DAY_STOP_PT = -12.0    # 누적 −12pt → 당일 종료


def p_bias(o):
    """수준 항만 쓴 세팅 점수 — 피터 「외인 수급으로 상방 하방 예측 못한다」(8/7) → Δ10 제외."""
    if "px" not in o:
        return 0, {}
    t = dict(O1L=_sg(o.get("mon_cp"), P_BIAS["O1L"]), F2=_sg(o.get("fut_for"), P_BIAS["F2"]),
             O2L=_sg(o.get("wk_cp"), P_BIAS["O2L"]),
             PX=_sg((o["px"] - o["open"]) if o.get("open") is not None else None, P_BIAS["PX"]))
    return sum(t.values()), t


def _in_win(hm):
    return any(_hm(a) <= _hm(hm) < _hm(b) for a, b in P_WINDOWS)


def run_p(S, live=False):
    """분 단위로 앞으로만 진행하는 시뮬레이션. 각 시점의 판단은 그 시각 이전 데이터만 쓴다."""
    cs = [c for c in S["cs"] if _hm(c[0]) < _hm(FORCE_EXIT)]
    log, trades = [], []
    side = None            # +1 매수 / −1 매도
    set_t = None
    flips = 0
    pend = None            # 대기 주문 dict(kind, px, level)
    pos = None
    stops = 0
    cum = 0.0
    done = False
    ck = list(P_CHECKS)
    last_entry_level = None
    for i, c in enumerate(cs):
        t = c[0]
        # ① 세팅 판정(체크포인트 시각에, 그 시각 이전 데이터로) · 오후 재대기
        T = None
        if ck and _hm(t) >= _hm(ck[0]):
            T = ck.pop(0)
        elif t in P_REARM and side and pos is None and not done:
            T, pend = t, None
        if T:
            o = observe(S, T)
            b, terms = p_bias(o)
            want = 1 if b >= P_BIAS_GO else -1 if b <= -P_BIAS_GO else 0
            if T in P_REARM:
                want = 0                                # 오후는 세팅을 다시 정하지 않는다
            if side is None and want:
                side, set_t = want, T
                log.append("%s 세팅 %s (B=%+d %s)" % (T, "매수" if want > 0 else "매도", b, terms))
            elif side and want == -side and pos is None and flips == 0 and stops >= 1:
                side, flips = want, flips + 1          # 세팅 변경: 손절을 겪고, 수준 점수가 반대로 |B|≥2
                pend, last_entry_level = None, None
                log.append("%s 세팅 변경 → %s (B=%+d)" % (T, "매수" if want > 0 else "매도", b))
            if side and pos is None and pend is None and not done and _in_win(T):
                lv = [p for p in o.get("levels", [])] + [p for _, p in o.get("walls", [])]
                px = o["px"]
                near = [p for p in lv if 0 < (px - p) * side <= P_NEAR]          # 매도=위 저항, 매수=아래 지지
                brk = [p for p in lv if 0 < (p - px) * side <= 10.0]              # 매도=아래 지지 돌파
                pend = dict(armed=T, limit=(min(near, key=lambda p: abs(p - px)) if near else None),
                            brk=(min(brk, key=lambda p: abs(p - px)) if brk else None), lv=lv, atr=o["atr"])
                if last_entry_level is not None:          # 재진입은 직전 진입 레벨 재돌파만
                    pend.update(limit=None, brk=last_entry_level)
                log.append("%s 대기 — 지정가 %s · 돌파 %s" % (T, pend["limit"] if pend["limit"] is not None else "없음",
                                                           pend["brk"] if pend["brk"] is not None else "없음"))
        if done:
            continue
        # ② 대기 주문 체결(이 봉 안에서)
        if pos is None and pend is not None and _in_win(t) and _hm(t) >= _hm(pend["armed"]):
            fill = None
            if pend["limit"] is not None and c[3] <= pend["limit"] <= c[2]:
                fill, how = pend["limit"], "되돌림 지정가"
            elif pend["brk"] is not None and (c[4] - pend["brk"]) * side > 0 and \
                    (cs[i - 1][4] - pend["brk"]) * side <= 0:
                fill, how = c[4], "돌파 확인(종가)"
            if fill is not None:
                dist = min(max(P_STOP, 1.5 * pend["atr"]), P_STOP_MAX)
                far = [p for p in pend["lv"] if (p - fill) * side >= P_FAR_R * dist]
                pos = dict(t=t, fill=round(fill, 2), how=how, stop=round(fill - side * dist, 2), r=dist,
                           half=round(fill + side * P_HALF_R * dist, 2),
                           far=(max(far, key=lambda p: (p - fill) * side) if far else None),
                           half_done=False, legs=[])
                pos["stop0"] = pos["stop"]
                last_entry_level = pend["limit"] if how.startswith("되돌림") else pend["brk"]
                pend = None
                log.append("%s 진입 %s @%.2f (%s) 손절 %.2f · 절반 %.2f · 최종 %s" % (
                    t, "매수" if side > 0 else "매도", pos["fill"], how, pos["stop"], pos["half"],
                    pos["far"] if pos["far"] is not None else "없음(15:10)"))
                if how.startswith("돌파"):
                    continue      # 종가 체결 — 그 봉은 끝났다
                # 지정가는 봉 중간 체결 — 같은 봉의 반대쪽 극값이 손절에 닿았으면 손절로 본다(보수)
        # ③ 보유 관리
        if pos is not None:
            hs = (c[3] <= pos["stop"]) if side > 0 else (c[2] >= pos["stop"])
            fill_bar = pos["t"] == t                   # 지정가 체결 봉 — 봉 안 순서를 모르므로 손절만 본다
            hh = (not fill_bar) and (not pos["half_done"]) and ((c[2] >= pos["half"]) if side > 0 else (c[3] <= pos["half"]))
            hf = (not fill_bar) and pos["far"] is not None and ((c[2] >= pos["far"]) if side > 0 else (c[3] <= pos["far"]))
            exit_all = None
            if hs:                                     # 같은 봉이면 손절 우선(보수)
                exit_all = (pos["stop"], "본전 손절" if pos["half_done"] else "손절")
            else:
                if hh:
                    pos["legs"].append(((pos["half"] - pos["fill"]) * side, "절반 청산", t))
                    pos["half_done"], pos["stop"] = True, pos["fill"]
                if hf:
                    exit_all = (pos["far"], "최종 목표")
            if exit_all:
                px, why = exit_all
                n_left = 1 if pos["half_done"] else 2
                for _ in range(n_left):
                    pos["legs"].append(((px - pos["fill"]) * side, why, t))
            if exit_all:
                pnl = sum(x[0] for x in pos["legs"]) / 2.0
                trades.append(dict(entry_t=pos["t"], side="매수" if side > 0 else "매도", fill=pos["fill"], how=pos["how"],
                                   exit_t=t, exit_px=exit_all[0], why=exit_all[1], stop=pos["stop0"], half=pos["half"], far=pos["far"],
                                   legs=[(round(a, 2), b, tt) for a, b, tt in pos["legs"]], pnl=round(pnl, 2)))
                cum += pnl
                if exit_all[1] == "손절":
                    stops += 1
                log.append("%s 청산 %s → %+.2fpt (누적 %+.2f)" % (t, exit_all[1], pnl, cum))
                pos = None
                if len(trades) >= P_MAX_ENTRIES or stops >= P_DAY_STOP_N or cum <= P_DAY_STOP_PT:
                    done = True
                    log.append("%s 당일 종료 (진입 %d · 손절 %d · 누적 %+.2f)" % (t, len(trades), stops, cum))
                elif exit_all[1] == "손절" and _in_win(t):
                    pend = dict(armed=t, limit=None, brk=last_entry_level, lv=[], atr=1.0)   # 같은 방향 재진입 대기
                    o = observe(S, _fmt(_hm(t) + 1))
                    pend.update(lv=o.get("levels", []) + [p for _, p in o.get("walls", [])], atr=o.get("atr", 1.0))
                    log.append("%s 재진입 대기 — %.2f 재돌파" % (t, last_entry_level))
    if pos is not None and live and cs and _hm(cs[-1][0]) < _hm(FORCE_EXIT) - 1:   # 장중 — 아직 보유 중
        px = cs[-1][4]
        legs = pos["legs"] + [((px - pos["fill"]) * side, "평가", cs[-1][0])] * (1 if pos["half_done"] else 2)
        trades.append(dict(entry_t=pos["t"], side="매수" if side > 0 else "매도", fill=pos["fill"], how=pos["how"],
                           exit_t=None, open=True, stop=pos["stop0"], stop_now=pos["stop"], half=pos["half"], far=pos["far"],
                           legs=[(round(a, 2), b, tt) for a, b, tt in legs], pnl=round(sum(x[0] for x in legs) / 2.0, 2)))
        log.append("%s 보유 중 — 평가 %+.2fpt" % (cs[-1][0], trades[-1]["pnl"]))
        pos = None
    if pos is not None:                                # 15:10 강제청산 — 15:09 봉 종가
        px = cs[-1][4]
        n_left = 1 if pos["half_done"] else 2
        for _ in range(n_left):
            pos["legs"].append(((px - pos["fill"]) * side, "15:10 강제청산", cs[-1][0]))
        pnl = sum(x[0] for x in pos["legs"]) / 2.0
        trades.append(dict(entry_t=pos["t"], side="매수" if side > 0 else "매도", fill=pos["fill"], how=pos["how"],
                           exit_t=cs[-1][0], exit_px=round(px, 2), why="15:10 강제청산", stop=pos["stop0"], half=pos["half"], far=pos["far"],
                           legs=[(round(a, 2), b, tt) for a, b, tt in pos["legs"]], pnl=round(pnl, 2)))
        cum += pnl
        log.append("%s 15:10 강제청산 @%.2f → %+.2fpt (누적 %+.2f)" % (cs[-1][0], px, pnl, cum))
    return dict(ver=P_VER, set_t=set_t, side=("매수" if side and side > 0 else "매도" if side else "관망"),
                trades=trades, pnl=round(cum, 2), log=log)


# ── 피터 대조 (peter_levels.db 붙여넣기 원문의 거래 줄) ─────────────────────────
def peter_trades(day):
    import re
    try:
        con = _ro("peter_levels.db")
        r = con.execute("SELECT offset, raw_tr FROM peter_paste WHERE date=?", (day,)).fetchone()
        con.close()
    except Exception:
        return None
    if not r or not (r[1] or "").strip():
        return dict(offset=(r[0] if r else None), trades=[], pnl=0.0, measured=bool(r))
    off, out = r[0] or 0.0, []
    for line in r[1].splitlines():
        m = re.match(r"\s*(\d{1,2}:\d\d)\s+([LS])\s+([\d.]+)\s*/\s*(\d{1,2}:\d\d)\s+X\s+([\d.]+)", line)
        if not m:
            continue
        t0, s, e, t1, x = m.groups()
        sg = 1 if s == "L" else -1
        e, x = float(e), float(x)
        out.append(dict(entry_t=t0.zfill(5), side="매수" if sg > 0 else "매도", entry=e, exit_t=t1.zfill(5), exit=x,
                        entry_mini=round(e + off, 2), exit_mini=round(x + off, 2), pnl=round((x - e) * sg, 2)))
    return dict(offset=off, trades=out, pnl=round(sum(t["pnl"] for t in out), 2), measured=True)


def analyze(S, live=False, start="08:55", end="09:55", step=10):
    """사다리 서버·CLI 공용 — 시점별 제안(기본) + 신동2-P + 피터. 장중이면 아직 오지 않은 시점은 만들지 않는다."""
    last = S["cs"][-1][0] if S["cs"] else None
    pts = []
    t = _hm(start)
    while t <= _hm(end):
        T = _fmt(t)
        if live and (last is None or _hm(T) > _hm(last) + 1):
            break                                   # T 직전 봉이 아직 없다 — 미래 시점
        o = observe(S, T)
        r = decide(o)
        pts.append(dict(obs={k: v for k, v in o.items() if k != "levels"}, rule=r, grade=grade(S, T, o, r, live=live)))
        t += step
    P = run_p(S, live=live)
    done = [p["grade"].get("pnl") for p in pts if isinstance(p["grade"].get("pnl"), (int, float))]
    return dict(ver=P_VER, live=live, last_bar=last, points=pts, p=P,
                params=dict(W=W, DEAD=DEAD, SCORE_GO=SCORE_GO, LOOK=LOOK, STOP_ATR=STOP_ATR, STOP_MAX=STOP_MAX,
                            RR_MIN=RR_MIN, FILL_WIN=FILL_WIN, P_STOP=P_STOP, P_HALF_R=P_HALF_R),
                summary=dict(base=round(sum(done), 2), base_n=len(done), p=P["pnl"]))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--start", default="08:55")
    ap.add_argument("--end", default="09:55")
    ap.add_argument("--step", type=int, default=10)
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    guard_intraday("foreign_flow_pit_review")
    S = load(a.date)
    out = []
    t = _hm(a.start)
    while t <= _hm(a.end):
        T = _fmt(t)
        o = observe(S, T)
        r = decide(o)
        g = grade(S, T, o, r)
        out.append(dict(obs=o, rule=r, grade=g))
        t += a.step
    eod = observe(S, "15:46")
    out_eod = dict(obs=eod, rule=decide(eod))

    print("| T | 기준가 | 선물외인(Δ10) | 먼스리 콜−풋(Δ10) | 위클리 콜−풋(Δ10) | 현물외인(Δ10) | 가격Δ10 | 점수 | 방향 | 진입 | 손절 | 청산 | 결과 | 손익pt |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    f = lambda v: "—" if v is None else ("%+d" % v if isinstance(v, int) else "%+.1f" % v)
    for x in out:
        o, r, g = x["obs"], x["rule"], x["grade"]
        print("| %s | %s | %s (%s) | %s (%s) | %s (%s) | %s (%s) | %s | %+d | %s | %s | %s | %s | %s | %s |" % (
            o["T"], ("%.2f" % o["px"]) if "px" in o else "—", f(o.get("fut_for")), f(o.get("fut_for_d")), f(o.get("mon_cp")), f(o.get("mon_cp_d")),
            f(o.get("wk_cp")), f(o.get("wk_cp_d")), f(o.get("spot")), f(o.get("spot_d")), f(o.get("dpx")), r["score"], r["dir"],
            ("%s %s" % (r.get("entry"), r.get("entry_type", ""))) if r["dir"] != "관망" else "—",
            r.get("stop", "—"), r.get("target", "—"), g.get("result"), g.get("pnl", "—")))
    print("\n장 마감 관측:", json.dumps({k: v for k, v in eod.items() if k != "levels"}, ensure_ascii=False))
    print("장 마감 규칙:", json.dumps(out_eod["rule"], ensure_ascii=False))

    P = run_p(S)
    print("\n## 신동2-P (%s) — 세팅 %s %s, 합계 %+.2fpt (1계약 환산, 2분할 평균)" % (P["ver"], P["set_t"] or "—", P["side"], P["pnl"]))
    print("| 진입 | 방향 | 체결 | 방식 | 청산 | 레그 | 손익pt |")
    print("|---|---|---|---|---|---|---|")
    for x in P["trades"]:
        print("| %s | %s | %.2f | %s | %s | %s | %+.2f |" % (x["entry_t"], x["side"], x["fill"], x["how"], x["exit_t"],
              " / ".join("%s %+.2f@%s" % (b_, a_, t_) for a_, b_, t_ in x["legs"]), x["pnl"]))
    for line in P["log"]:
        print("  ·", line)

    PT = peter_trades(a.date)
    print("\n## 피터 대조 (트윗 기준 · 정규선물 pt · 미니 환산 = 원문 %s)" % (("%+.2f" % PT["offset"]) if PT and PT["offset"] is not None else "—"))
    if not PT or not PT["measured"]:
        print("  피터 원문 없음 — 미측정(0 이 아니다)")
    else:
        for x in PT["trades"]:
            print("  %s %s %.1f(미니 %.2f) → %s %.1f(미니 %.2f)  %+.1fpt" % (x["entry_t"], x["side"], x["entry"], x["entry_mini"],
                  x["exit_t"], x["exit"], x["exit_mini"], x["pnl"]))
    base = sum(x["grade"].get("pnl", 0) or 0 for x in out if x["grade"].get("result") not in ("관망", None))
    print("\n## 요약  신동2(기본) %+.2f · 신동2-P %+.2f · 피터 %s" % (base, P["pnl"],
          ("%+.1f" % PT["pnl"]) if PT and PT["measured"] else "미측정"))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fp:
            json.dump(dict(date=a.date, params=dict(W=W, DEAD=DEAD, SCORE_GO=SCORE_GO, LOOK=LOOK), points=out, eod=out_eod,
                           shindong2_p=P, peter=PT, summary=dict(base=round(base, 2), p=P["pnl"],
                                                                  peter=(PT["pnl"] if PT and PT["measured"] else None))),
                      fp, ensure_ascii=False, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
