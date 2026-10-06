# -*- coding: utf-8 -*-
"""[MW0601 662차 후속4] 신동2 라이브 — 상태 스냅샷 · 이벤트 감지 · 재량(AI) 제안 기록 · 장후 채점.

`shindong2` 스킬(.claude/skills/shindong2/SKILL.md)이 부르는 도구다. 주문은 하지 않는다(절대원칙 §6).

    python scripts/shindong2_live.py snapshot [--date D]     # 지금 상태 + 새 이벤트 → 요약 출력
    python scripts/shindong2_live.py poll [--date D]         # snapshot 후, 마지막 AI 기록 뒤 새 이벤트가 있으면 exit 10
    python scripts/shindong2_live.py record --phase intraday --action plan --dir 매도 \\
           --entry 1104 --stop 1108.5 --target 1098.2 --comment-file c.md   # 재량 제안 기록(시각 = 지금)
    python scripts/shindong2_live.py score [--date D]        # 재량 제안 채점(장중이면 잠정)

저장 (gitignore — 런타임 산출물)
    data/shindong2_live/YYYYMMDD/state.json      마지막 스냅샷
                                 events.jsonl    이벤트(키 단위 1회)
                                 ai_log.jsonl    재량 기록(append-only — 고치지 않는다)
                                 ai_latest.json  사다리 「신동2 해설」 패널이 읽는 최신 해설
                                 ai_score.json   채점 결과
문서 (커밋 대상)
    docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-YYYYMMDD.md   기록마다 덧붙인다

🔴 미래 참조 차단
  · 기록 시각은 **벽시계**다. 지정할 수 없다(`--asof` 없음). 효력은 기록 시각 **다음 분 봉부터**.
  · `--for-date` 는 장전 계획을 다음 거래일 앞으로 미리 적는 용도 — 그날 08:45 이전 기록은 개장부터 유효.
🔴 456차 — 장중에는 사다리와 같은 가벼운 경로(ladder_data.build_day: ts 범위 조회)만 쓴다.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "maekjeom_ladder"))

# 환경변수로 바꿀 수 있다 — 시험·화면 확인용 샌드박스(실제 기록을 오염시키지 않기 위해)
LIVE_DIR = os.environ.get("SHINDONG2_LIVE_DIR") or os.path.join(ROOT, "data", "shindong2_live")
DOC_DIR = os.environ.get("SHINDONG2_DOC_DIR") or os.path.join(ROOT, "docs", "미륵이고도화3", "신동2", "live")
FORCE_EXIT = "15:10"
PLAN_EXPIRE = "15:00"        # 미체결 재량 진입 계획의 마지막 유효 봉
PHASES = ("premarket", "intraday", "position", "postmarket", "overnight")
ACTIONS = ("plan", "manage", "exit", "stand", "note")
PHASE_KO = dict(premarket="장전", intraday="장중", position="보유", postmarket="장후", overnight="익일 계획")


def _hm(t):
    h, m = t.split(":")[:2]
    return int(h) * 60 + int(m[:2])


def _fmt(m):
    return "%02d:%02d" % (m // 60, m % 60)


def day_dir(day):
    d = os.path.join(LIVE_DIR, day.replace("-", ""))
    os.makedirs(d, exist_ok=True)
    return d


def _read_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out


def _append_jsonl(path, rec):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")


def _atomic_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, path)


# ── 데이터 ─────────────────────────────────────────────────────────────────
def _prev_day_mini(day):
    import sqlite3
    p = os.path.join(ROOT, "data", "db", "regular_candles.db").replace("\\", "/")
    con = sqlite3.connect("file:%s?mode=ro" % p, uri=True, timeout=5.0)
    try:
        r = con.execute("SELECT MAX(trade_date) FROM regular_candles WHERE code='A056A' AND trade_date<?", (day,)).fetchone()
        if not r or not r[0]:
            return None
        rows = con.execute("SELECT open, high, low, close FROM regular_candles WHERE code='A056A' AND trade_date=?"
                           " AND substr(ts,12,5) BETWEEN '08:45' AND '15:45' ORDER BY ts", (r[0],)).fetchall()
    finally:
        con.close()
    if not rows:
        return None
    return dict(date=r[0], open=round(rows[0][0], 2), high=round(max(x[1] for x in rows), 2),
                low=round(min(x[2] for x in rows), 2), close=round(rows[-1][3], 2))


def _spot_foreign(day, t):
    """현물(KOSPI) 외인 누계 — 7222 kospi_spot. 사다리 flow1m 에는 없는 상품이라 직접 읽는다(작은 DB)."""
    import sqlite3
    p = os.path.join(ROOT, "data", "db", "option_flow.db").replace("\\", "/")
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p, uri=True, timeout=5.0)
        r = con.execute("SELECT net_qty FROM option_investor_flow WHERE trade_date=? AND product='kospi_spot' AND investor='foreign'"
                        " AND bar_time<=? ORDER BY bar_time DESC LIMIT 1", (day, t)).fetchone()
        con.close()
        return r[0] if r else None
    except Exception:
        return None


def build_state(day, now=None):
    """사다리 데이터 계층으로 지금 상태를 만든다. 장중이면 완결 봉까지만 의미가 있다."""
    import ladder_data as L
    now = now or _dt.datetime.now()
    d = L.build_day(day, now=now)
    cs = d["candles"]
    live = d["live"]
    bars = cs[:-1] if live and cs else cs           # 장중 — 덜 찬 마지막 봉 제외
    st = dict(date=day, live=live, generated_at=now.isoformat(timespec="seconds"), warnings=d.get("warnings", []))
    if not bars:
        st["empty"] = True
        return st, d
    last = bars[-1]
    st.update(last_bar=last[0], px=last[4], open=bars[0][1],
              hi=max(c[2] for c in bars), lo=min(c[3] for c in bars))
    st["prev"] = pv = _prev_day_mini(day)
    if pv:
        st["prev_low_break_t"] = next((c[0] for c in bars if c[3] < pv["low"]), None)
        st["prev_high_break_t"] = next((c[0] for c in bars if c[2] > pv["high"]), None)
        st["gap"] = "상승" if bars[0][1] > pv["high"] else "하락" if bars[0][1] < pv["low"] else None
    # 수급 — 완결 봉 시각 기준 최신 · 10분 전
    mins = d.get("mins", [])

    def at(arr, t):
        """t 이전(포함) 마지막 측정값 — 그 분에 값이 없으면 직전 값. 없으면 None(미측정)."""
        if not arr or t not in mins:
            return None
        for v in reversed(arr[:mins.index(t) + 1]):
            if v is not None:
                return v
        return None
    t0, t10 = last[0], _fmt(_hm(last[0]) - 10)
    fut = d.get("fut") or {}
    st["flow"] = dict(
        fut_foreign=at(fut.get("foreign"), t0), fut_foreign_10=at(fut.get("foreign"), t10),
        fut_inst=at(fut.get("institution"), t0),
        mon_call=at((d["flow1m"].get("mon_call") or {}).get("foreign"), t0),
        mon_put=at((d["flow1m"].get("mon_put") or {}).get("foreign"), t0),
        wk_call=at((d["flow1m"].get("wk_mon_call") or {}).get("foreign"), t0),
        wk_put=at((d["flow1m"].get("wk_mon_put") or {}).get("foreign"), t0),
        spot=_spot_foreign(day, t0),
        mon_call_10=at((d["flow1m"].get("mon_call") or {}).get("foreign"), t10),
        mon_put_10=at((d["flow1m"].get("mon_put") or {}).get("foreign"), t10))
    # 맥점 — 지금 보이는 것만(생성 시각 이후)
    lv = [x for x in d.get("levels", []) if x.get("kind") != "피터" and _hm(x["start"]) <= _hm(last[0]) + 1]
    above = sorted({round(x["price"], 2) for x in lv if x["price"] > last[4]})[:4]
    below = sorted({round(x["price"], 2) for x in lv if x["price"] < last[4]}, reverse=True)[:4]
    st["levels"] = dict(above=above, below=below)
    st["walls"] = {k: (v.get("wall_close") if v and not v.get("absent") else None) for k, v in (d.get("books") or {}).items()}
    sd2 = d.get("shindong2") or {}
    st["sd2"] = dict(summary=sd2.get("summary"),
                     points=[dict(T=p["obs"]["T"], dir=p["rule"]["dir"], score=p["rule"]["score"], entry=p["rule"].get("entry"),
                                  stop=p["rule"].get("stop"), target=p["rule"].get("target"), result=p["grade"].get("result"),
                                  pnl=p["grade"].get("pnl")) for p in sd2.get("points", [])],
                     variants={k: dict(set_t=(sd2.get(k) or {}).get("set_t"), side=(sd2.get(k) or {}).get("side"),
                                       trades=(sd2.get(k) or {}).get("trades", []), pnl=(sd2.get(k) or {}).get("pnl"))
                               for k in ("p", "p2", "p3") if sd2.get(k)})
    st["peter"] = dict(trades=(d.get("peter") or {}).get("trades", []), available=(d.get("peter") or {}).get("available"))
    st["bars_n"] = len(bars)
    return st, d


# ── 이벤트 ─────────────────────────────────────────────────────────────────
def detect_events(st, ai_trades=None):
    """상태에서 이벤트 후보를 만든다. 키가 같으면 같은 이벤트 — 저장 시 한 번만 남는다."""
    ev = []
    if st.get("empty"):
        return ev
    for p in st["sd2"]["points"]:
        if p["dir"] != "관망":
            ev.append(dict(key="base:%s" % p["T"], t=p["T"], kind="기본 제안",
                           text="신동2 기본 %s %s 점수 %+d · 진입 %s 손절 %s 청산 %s" % (p["T"], p["dir"], p["score"], p["entry"], p["stop"], p["target"])))
    for k, v in st["sd2"]["variants"].items():
        nm = {"p": "P", "p2": "P2", "p3": "P3"}[k]
        if v["set_t"]:
            ev.append(dict(key="%s:set" % k, t=v["set_t"], kind="세팅", text="신동2-%s 세팅 %s (%s)" % (nm, v["side"], v["set_t"])))
        for tr in v["trades"]:
            ev.append(dict(key="%s:entry:%s" % (k, tr["entry_t"]), t=tr["entry_t"], kind="진입",
                           text="신동2-%s %s 진입 %s @%.2f · 손절 %s" % (nm, tr["side"], tr["entry_t"], tr["fill"], tr["stop"])))
            for pnl, why, tt in tr.get("legs", []):
                if why == "절반 청산":
                    ev.append(dict(key="%s:half:%s" % (k, tr["entry_t"]), t=tt, kind="절반 청산",
                                   text="신동2-%s 절반 청산 %s %+.2f → 나머지 본전 손절" % (nm, tt, pnl)))
            if tr.get("exit_t"):
                ev.append(dict(key="%s:exit:%s" % (k, tr["entry_t"]), t=tr["exit_t"], kind="청산",
                               text="신동2-%s 청산 %s %s %+.2fpt" % (nm, tr["exit_t"], tr.get("why"), tr["pnl"])))
    pv = st.get("prev")
    if pv:
        if st.get("prev_low_break_t"):
            txt = ("갭 하락 — 시가 %.2f 가 전일 저점 %.2f 아래" % (st["open"], pv["low"])) if st.get("gap") == "하락" else                   "전일 저점 %.2f 이탈 %s" % (pv["low"], st["prev_low_break_t"])
            ev.append(dict(key="prev_low_break", t=st["prev_low_break_t"], kind="구조", text=txt))
        if st.get("prev_high_break_t"):
            txt = ("갭 상승 — 시가 %.2f 가 전일 고점 %.2f 위" % (st["open"], pv["high"])) if st.get("gap") == "상승" else                   "전일 고점 %.2f 돌파 %s" % (pv["high"], st["prev_high_break_t"])
            ev.append(dict(key="prev_high_break", t=st["prev_high_break_t"], kind="구조", text=txt))
    for tr in ai_trades or []:
        ev.append(dict(key="ai:entry:%s" % tr["entry_t"], t=tr["entry_t"], kind="재량 진입",
                       text="신동2-AI %s 진입 %s @%.2f" % (tr["side"], tr["entry_t"], tr["fill"])))
        if tr.get("exit_t"):
            ev.append(dict(key="ai:exit:%s" % tr["entry_t"], t=tr["exit_t"], kind="재량 청산",
                           text="신동2-AI 청산 %s %s %+.2fpt" % (tr["exit_t"], tr["why"], tr["pnl"])))
    return ev


def save_new_events(day, ev, now):
    path = os.path.join(day_dir(day), "events.jsonl")
    seen = {e["key"] for e in _read_jsonl(path)}
    new = []
    for e in ev:
        if e["key"] in seen:
            continue
        e = dict(e, detected_at=now.isoformat(timespec="seconds"))
        _append_jsonl(path, e)
        seen.add(e["key"])
        new.append(e)
    return new


# ── 재량 기록 · 채점 ──────────────────────────────────────────────────────
def load_ai_log(day):
    return _read_jsonl(os.path.join(day_dir(day), "ai_log.jsonl"))


def simulate_ai(day, cs, records, live=False):
    """재량 기록을 1분봉에 대 본다. 1계약 · 같은 봉 손절 우선 · 15:10 강제청산. 효력은 기록 다음 분 봉부터."""
    recs = []
    for r in records:
        if r.get("backfill"):
            continue
        ts = _dt.datetime.fromisoformat(r["ts"])
        eff = "08:45" if ts.date().isoformat() < day or ts.strftime("%H:%M") < "08:45" else _fmt(_hm(ts.strftime("%H:%M")) + 1)
        recs.append((eff, r))
    recs.sort(key=lambda x: (x[0], x[1]["ts"]))
    bars = [c for c in cs if _hm(c[0]) < _hm(FORCE_EXIT)]
    pend = pos = None
    trades, j = [], 0
    for c in bars:
        t = c[0]
        while j < len(recs) and _hm(recs[j][0]) <= _hm(t):
            eff, r = recs[j]
            j += 1
            act = r.get("action", "plan")
            sgn = 1 if r.get("dir") == "매수" else -1 if r.get("dir") == "매도" else 0
            if act == "plan" and sgn:
                if pos is None:
                    pend = dict(sgn=sgn, entry=r.get("entry"), stop=r.get("stop"), target=r.get("target"), rid=r["id"], t=eff)
                elif pos["sgn"] == sgn:
                    pos.update(stop=r.get("stop", pos["stop"]), target=r.get("target", pos["target"]))
            elif act == "manage":
                tgt = pos or pend
                if tgt is not None:
                    if r.get("stop") is not None:
                        tgt["stop"] = r["stop"]
                    if r.get("target") is not None:
                        tgt["target"] = r["target"]
            elif act == "exit" and pos is not None:
                pos["exit_now"] = (r["id"], t)
            elif act in ("stand", "exit"):
                pend = None
        if pos is not None and pos.get("exit_now"):
            px = c[1]
            trades.append(dict(pos["tr"], exit_t=t, exit_px=round(px, 2), why="재량 청산", pnl=round((px - pos["fill"]) * pos["sgn"], 2)))
            pos = None
        if pos is None and pend is not None:
            if _hm(t) > _hm(PLAN_EXPIRE):
                pend = None
            elif pend["entry"] is None:
                pos = dict(sgn=pend["sgn"], fill=c[1], stop=pend["stop"], target=pend["target"],
                           tr=dict(entry_t=t, side="매수" if pend["sgn"] > 0 else "매도", fill=round(c[1], 2), how="시장가", rid=pend["rid"]))
                pend = None
            elif c[3] <= pend["entry"] <= c[2]:
                pos = dict(sgn=pend["sgn"], fill=pend["entry"], stop=pend["stop"], target=pend["target"],
                           tr=dict(entry_t=t, side="매수" if pend["sgn"] > 0 else "매도", fill=pend["entry"], how="지정가", rid=pend["rid"]))
                pend = None
        if pos is not None:
            s = pos["sgn"]
            hs = pos["stop"] is not None and ((c[3] <= pos["stop"]) if s > 0 else (c[2] >= pos["stop"]))
            ht = pos["target"] is not None and ((c[2] >= pos["target"]) if s > 0 else (c[3] <= pos["target"]))
            if hs or ht:
                px, why = (pos["stop"], "손절") if hs else (pos["target"], "목표 청산")
                trades.append(dict(pos["tr"], exit_t=t, exit_px=px, why=why, stop=pos["stop"], target=pos["target"],
                                   pnl=round((px - pos["fill"]) * s, 2)))
                pos = None
    if pos is not None:
        px = bars[-1][4] if bars else pos["fill"]
        if live and bars and _hm(bars[-1][0]) < _hm(FORCE_EXIT) - 1:
            trades.append(dict(pos["tr"], exit_t=None, open=True, stop=pos["stop"], target=pos["target"],
                               pnl=round((px - pos["fill"]) * pos["sgn"], 2)))
        else:
            trades.append(dict(pos["tr"], exit_t=bars[-1][0], exit_px=round(px, 2), why="15:10 강제청산", stop=pos["stop"],
                               target=pos["target"], pnl=round((px - pos["fill"]) * pos["sgn"], 2)))
    pending = dict(pend, entry_t=None) if pend else None
    return dict(trades=trades, pending=pending, pnl=round(sum(t["pnl"] for t in trades if not t.get("open")), 2))


def _doc_path(day):
    os.makedirs(DOC_DIR, exist_ok=True)
    return os.path.join(DOC_DIR, "신동2_해설_MW0601-%s.md" % day.replace("-", ""))


def record(day, phase, action, direction, entry, stop, target, comment, now=None):
    now = now or _dt.datetime.now()
    if phase not in PHASES or action not in ACTIONS:
        raise SystemExit("phase/action 이 잘못됐다: %s / %s" % (phase, action))
    if action == "plan" and direction in ("매수", "매도") and (stop is None or target is None):
        raise SystemExit("plan 은 손절·청산을 함께 적어야 한다(채점 불가 기록 금지)")
    log = load_ai_log(day)
    rid = "%s-%02d" % (now.strftime("%H%M%S"), len(log) + 1)
    rec = dict(id=rid, ts=now.isoformat(timespec="seconds"), date=day, phase=phase, action=action, dir=direction,
               entry=entry, stop=stop, target=target, comment=comment)
    _append_jsonl(os.path.join(day_dir(day), "ai_log.jsonl"), rec)
    _atomic_json(os.path.join(day_dir(day), "ai_latest.json"), rec)
    with open(_doc_path(day), "a", encoding="utf-8") as f:
        if os.path.getsize(_doc_path(day)) == 0:
            f.write("# 신동2 해설 — %s (MW0601)\n\n> Claude 재량 제안 기록. append-only · 시각은 벽시계 · 채점은 `scripts/shindong2_live.py score`.\n"
                    "> 주문 없음(절대원칙 §6). 사전등록 규칙(기본·P·P2·P3)과 별개 주체 「신동2-AI」.\n\n" % day)
        plan = ""
        if direction in ("매수", "매도") or entry is not None or stop is not None or target is not None:
            plan = " · **%s** 진입 %s · 손절 %s · 청산 %s" % (direction or "—", entry if entry is not None else "시장가", stop, target)
        f.write("## %s %s — %s%s\n\n%s\n\n" % (now.strftime("%H:%M"), PHASE_KO[phase], action, plan, (comment or "").strip()))
    return rec


# ── CLI ───────────────────────────────────────────────────────────────────
def _summary(st, new, ai):
    if st.get("empty"):
        return "봉 없음 — 장 시작 전이거나 수집 전"
    f = st["flow"]
    d10 = lambda a, b: "—" if a is None or b is None else "%+d" % (a - b)
    L = ["## 신동2 스냅샷 %s %s (완결 봉 %s)" % (st["date"], "장중" if st["live"] else "확정", st["last_bar"]),
         "가격 %.2f · 시가 %.2f · 고 %.2f · 저 %.2f" % (st["px"], st["open"], st["hi"], st["lo"])]
    if st.get("prev"):
        p = st["prev"]
        L.append("전일(%s) 고 %.2f · 저 %.2f · 종 %.2f" % (p["date"], p["high"], p["low"], p["close"]))
    L.append("선물 외인 %s (Δ10 %s) · 기관 %s" % (f["fut_foreign"], d10(f["fut_foreign"], f["fut_foreign_10"]), f["fut_inst"]))
    cp = lambda a, b: None if a is None or b is None else a - b
    L.append("먼스리 외인 콜 %s 풋 %s (콜−풋 %s, Δ10 %s) · 위클리 콜 %s 풋 %s · 현물 외인 %s" % (
        f["mon_call"], f["mon_put"], cp(f["mon_call"], f["mon_put"]),
        d10(cp(f["mon_call"], f["mon_put"]), cp(f["mon_call_10"], f["mon_put_10"])), f["wk_call"], f["wk_put"], f["spot"]))
    L.append("맥점 위 %s · 아래 %s · 벽 %s" % (st["levels"]["above"], st["levels"]["below"], st["walls"]))
    sm = st["sd2"]["summary"] or {}
    L.append("규칙 손익 — 기본 %s · P %s · P2 %s · P3 %s" % (sm.get("base"), sm.get("p"), sm.get("p2"), sm.get("p3")))
    for k, v in st["sd2"]["variants"].items():
        op = [t for t in v["trades"] if t.get("open")]
        L.append("  %s: 세팅 %s %s · 거래 %d · %s" % (k.upper(), v["set_t"] or "—", v["side"], len(v["trades"]),
                                                  ("보유 중 %s @%.2f 평가 %+.2f" % (op[0]["side"], op[0]["fill"], op[0]["pnl"])) if op else "무포지션"))
    if ai:
        L.append("재량(AI) — 손익 %s · 거래 %d · 대기 %s" % (ai["pnl"], len(ai["trades"]),
                 ("%s 진입 %s 손절 %s 청산 %s" % ("매수" if ai["pending"]["sgn"] > 0 else "매도", ai["pending"]["entry"] or "시장가",
                                            ai["pending"]["stop"], ai["pending"]["target"])) if ai.get("pending") else "없음"))
        for t in ai["trades"]:
            L.append("  AI %s %s @%.2f → %s %s %+.2f" % (t["entry_t"], t["side"], t["fill"], t.get("exit_t") or "보유 중", t.get("why", "평가"), t["pnl"]))
    L.append("새 이벤트 %d건" % len(new))
    for e in new:
        L.append("  · [%s] %s" % (e["kind"], e["text"]))
    if st.get("warnings"):
        L.append("경고: " + " · ".join(st["warnings"]))
    return "\n".join(L)


def cmd_snapshot(day, now=None):
    now = now or _dt.datetime.now()
    st, d = build_state(day, now)
    ai = None
    if not st.get("empty"):
        bars = d["candles"][:-1] if st["live"] else d["candles"]
        ai = simulate_ai(day, bars, load_ai_log(day), live=st["live"])
        st["ai"] = ai
    new = save_new_events(day, detect_events(st, ai["trades"] if ai else None), now)
    _atomic_json(os.path.join(day_dir(day), "state.json"), st)
    return st, new, ai


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gate", help="거래일이면 exit 0, 휴장일이면 exit 3 (예약작업 래퍼용)")
    g.add_argument("--date", default=_dt.date.today().isoformat())
    for c in ("snapshot", "poll", "score"):
        s = sub.add_parser(c)
        s.add_argument("--date", default=_dt.date.today().isoformat())
    r = sub.add_parser("record")
    r.add_argument("--date", default=_dt.date.today().isoformat())
    r.add_argument("--for-date", help="장후에 다음 거래일 계획을 그 날짜 파일로 미리 적는다")
    r.add_argument("--phase", required=True, choices=PHASES)
    r.add_argument("--action", default="plan", choices=ACTIONS)
    r.add_argument("--dir", default="관망", choices=("매수", "매도", "관망"))
    r.add_argument("--entry", type=float)
    r.add_argument("--stop", type=float)
    r.add_argument("--target", type=float)
    r.add_argument("--comment", default="")
    r.add_argument("--comment-file")
    a = ap.parse_args(argv)
    if a.cmd == "gate":
        try:
            from utils.time_utils import is_trading_day
            ok = is_trading_day(_dt.datetime.combine(_dt.date.fromisoformat(a.date), _dt.time(12)))
        except Exception as e:                       # 달력을 못 읽으면 주말만 거른다 — 그 사실을 남긴다
            ok = _dt.date.fromisoformat(a.date).weekday() < 5
            print("달력 읽기 실패(%s) — 주말만 판정" % e)
        print("%s %s" % (a.date, "거래일" if ok else "휴장일"))
        return 0 if ok else 3
    if a.cmd == "record":
        comment = a.comment
        if a.comment_file == "-":                    # 표준입력 — 예약작업(파일 쓰기 권한 없음)은 heredoc 으로 넘긴다
            data = sys.stdin.buffer.read()
            comment = data.decode("utf-8", errors="replace")
        elif a.comment_file:
            with open(a.comment_file, encoding="utf-8") as f:
                comment = f.read()
        day = a.for_date or a.date
        rec = record(day, a.phase, a.action, a.dir, a.entry, a.stop, a.target, comment)
        print("기록 %s %s %s %s · 문서 %s" % (rec["id"], rec["phase"], rec["action"], rec["dir"], _doc_path(day)))
        return 0
    st, new, ai = cmd_snapshot(a.date)
    if a.cmd == "score":
        out = dict(date=a.date, live=st.get("live"), ai=ai, rules=(st.get("sd2") or {}).get("summary"),
                   peter=[dict(entry_t=t.get("entry_hm"), side=t.get("direction"), pnl=t.get("pnl")) for t in (st.get("peter") or {}).get("trades", [])])
        _atomic_json(os.path.join(day_dir(a.date), "ai_score.json"), out)
        print(_summary(st, [], ai))
        print("\n채점 %s — 재량 %s · 규칙 %s" % ("잠정(장중)" if st.get("live") else "확정", ai and ai["pnl"], out["rules"]))
        return 0
    print(_summary(st, new, ai))
    if a.cmd == "poll":
        log = load_ai_log(a.date)
        last = max((r["ts"] for r in log), default="")
        ev = _read_jsonl(os.path.join(day_dir(a.date), "events.jsonl"))
        fresh = [e for e in ev if e.get("detected_at", "") > last]
        print("\n마지막 재량 기록 %s 이후 이벤트 %d건 → %s" % (last or "없음", len(fresh), "Claude 호출 필요" if fresh else "호출 불필요"))
        return 10 if fresh else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
