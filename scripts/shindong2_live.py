# -*- coding: utf-8 -*-
"""[MW0601 662차 후속4] 신동2 라이브 — 상태 스냅샷 · 이벤트 감지 · 재량(AI) 제안 기록 · 장후 채점.

`shindong2` 스킬(.claude/skills/shindong2/SKILL.md)이 부르는 도구다. 주문은 하지 않는다(절대원칙 §6).

    python scripts/shindong2_live.py snapshot [--date D]     # 지금 상태 + 새 이벤트 → 요약 출력
    python scripts/shindong2_live.py poll [--date D]         # snapshot 후, 마지막 AI 기록 뒤 새 이벤트가 있으면 exit 10
    python scripts/shindong2_live.py record --phase intraday --action plan --dir 매도 \\
           --entry 1104 --stop 1108.5 --target 1098.2 --comment-file c.md   # 재량 제안 기록(시각 = 지금)
    python scripts/shindong2_live.py score [--date D]        # 재량 제안 채점(장중이면 잠정)

[672차 학습 사이클 — scripts/shindong2_learn.py]
    python scripts/shindong2_live.py evaluate [--date D]     # 그날 계획(익일계획·장전계획, live/legacy)을 단독 시뮬 — 적중·손익·MFE/MAE·포착률
    python scripts/shindong2_live.py feedback [--date D] [--applied L1,L9] [--hit L9] [--miss L1] --comment-file -   # 평가·반성 기록
    python scripts/shindong2_live.py lesson add|set|tally|list ...                                                 # 레슨런 레지스트리
    python scripts/shindong2_live.py trend                   # 워크포워드 추이(개선−기존) + 딥다이브 판정
    python scripts/shindong2_live.py brief [--date D]        # 장전 브리핑 — 활성 레슨 · 전일 피드백 · 추이
    record 에 `--variant legacy`(기존방식 섀도 — 채점 비교용, 실제 재량 시뮬에서 제외) · `--lessons L1,L9`(적용 레슨 표기)

저장 (gitignore — 런타임 산출물)
    data/shindong2_live/YYYYMMDD/state.json      마지막 스냅샷
                                 events.jsonl    이벤트(키 단위 1회)
                                 ai_log.jsonl    재량 기록(append-only — 고치지 않는다)
                                 ai_latest.json  사다리 「신동2 해설」 패널이 읽는 최신 해설
                                 ai_score.json   채점 결과
문서 (커밋 대상)
    docs/미륵이고도화3/신동2/live/신동2_해설_<PC>-YYYYMMDD.md   기록마다 덧붙인다

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
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:     # 683차 — shindong2_scenario · shindong2_learn
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 환경변수로 바꿀 수 있다 — 시험·화면 확인용 샌드박스(실제 기록을 오염시키지 않기 위해)
LIVE_DIR = os.environ.get("SHINDONG2_LIVE_DIR") or os.path.join(ROOT, "data", "shindong2_live")
DOC_DIR = os.environ.get("SHINDONG2_DOC_DIR") or os.path.join(ROOT, "docs", "미륵이고도화3", "신동2", "live")
FORCE_EXIT = "15:10"
PLAN_EXPIRE = "15:00"        # 미체결 재량 진입 계획의 마지막 유효 봉
PHASES = ("premarket", "intraday", "position", "postmarket", "overnight")
ACTIONS = ("plan", "manage", "exit", "stand", "note")
VARIANTS = ("live", "legacy")   # 672차 — live 는 실제 재량(개선방식), legacy 는 기존방식 섀도(채점 비교용, 시뮬 제외)
PHASE_KO = dict(premarket="장전", intraday="장중", position="보유", postmarket="장후", overnight="익일 계획")


def _pc_id():
    """[MW0602 613차] 이 PC 식별자 — `utils/db_utils.py:pc_id()` 와 같은 규칙(호스트명의 `MW####`).

    종전에는 문서 파일명·머리글에 `MW0601` 이 하드코딩돼 MW0602 의 기록이 MW0601 이름 파일에 쌓였다
    (2026-10-07 해설은 MW0601 원본 파일 뒤에 MW0602 기록이 덧붙었다). 두 PC 는 별개 계좌·별개 DB 다.
    db_utils 를 import 하지 않는 이유: config 전체를 끌어오는 무거운 경로라 장중 가벼운 명령(snapshot/poll)에
    부담이 된다. 실패하면 호스트명, 그마저 안 되면 "UNKNOWN" — 미측정을 다른 PC 이름으로 위장하지 않는다.
    `SHINDONG2_PC` 로 덮어쓸 수 있다(시험용).
    """
    try:
        import platform as _pf
        import re as _re
        host = _pf.node() or ""
        m = _re.search(r"(MW\d{4})", host, _re.IGNORECASE)
        return m.group(1).upper() if m else (host[:32] or "UNKNOWN")
    except Exception:
        return "UNKNOWN"


PC = os.environ.get("SHINDONG2_PC") or _pc_id()


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


def _opt_amt(day, prod, t):
    """[v2 · 2026-10-10] 7222 외인 콜·풋 누계 **금액(백만원)** — t 이전(포함) 마지막 값. 없으면 None(미측정).
    규칙 엔진(foreign_flow_pit_review.observe)과 같은 단위·같은 상품을 보여 주려고 직접 읽는다 —
    사다리 flow1m 은 계약수(net_qty)라 그대로 쓰면 규칙과 다른 값을 해설하게 된다."""
    import sqlite3
    if not prod:
        return None, None
    p = os.path.join(ROOT, "data", "db", "option_flow.db").replace("\\", "/")
    out = []
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p, uri=True, timeout=5.0)
        for leg in ("call", "put"):
            r = con.execute("SELECT net_amt FROM option_investor_flow WHERE trade_date=? AND product=? AND investor='foreign'"
                            " AND bar_time<=? AND net_amt IS NOT NULL ORDER BY bar_time DESC LIMIT 1",
                            (day, prod + "_" + leg, t)).fetchone()
            out.append(r[0] if r else None)
        con.close()
    except Exception:
        return None, None
    return tuple(out)


FLOW_ANCHORS = ("09:02", "09:30", "10:00", "10:30", "11:00", "12:00", "13:00", "14:00", "14:30", "15:00", "15:20")


def _foreign_profile(day, t_cut, prev_days=3):
    """[MW0601 683차] 외인 동향 블록 — 「무엇이 · 언제 · 누구 반대편으로」 움직였나.

    2026-10-12 장후 수동 분석 형식을 도구로 옮겼다. 그날 화면만 보면 「외인 수급 변화 거의 없음」으로
    읽혔지만 실측은 14:47–15:34 +1,863계약 급반전이었다 — 누계 한 점이 아니라 **경로**를 봐야 한다.
      · 선물(7221 정규 K200, 계약 누계) 외인·기관·개인 시간대 경로 + 미결제약정 변화
      · 직전 거래일 3일 외인 선물 마감 누계(누적 포지션 맥락)
      · 먼스리 콜·풋 외인 **수량 대 금액** — 수량 ≈ 0 인데 금액만 크게 움직이면 행사가 교체(이익실현·롤)
      · 현물 외인·기관 — 선물↑·현물↓ 이면 방향 베팅이 아니라 현선 교체·헤지일 수 있다
    전부 당일 ts 범위(PK) 조회 — 장중에도 사다리와 같은 무게다(456차). 값이 없으면 None(미측정 ≠ 0).
    t_cut: 'HH:MM' 이하만 본다(장중 = 완결 봉). None 이면 마감 누계까지(15:34 적재분 포함)."""
    import sqlite3
    out = dict(t_cut=t_cut)
    p = os.path.join(ROOT, "data", "db", "raw_data.db").replace("\\", "/")
    hi = "%s %s:59" % (day, t_cut) if t_cut else "%s 23:59:59" % day
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p, uri=True, timeout=5.0)
        rows = con.execute("SELECT ts, fields FROM raw_investor_futures WHERE ts >= ? AND ts <= ? ORDER BY ts",
                           (day + " 00:00:00", hi)).fetchall()
        prev, cur = [], day
        for _ in range(prev_days):
            r = con.execute("SELECT ts, fields FROM raw_investor_futures WHERE ts < ? ORDER BY ts DESC LIMIT 1",
                            (cur + " 00:00:00",)).fetchone()
            if not r:
                break
            f = json.loads(r[1])
            prev.append(dict(date=r[0][:10], last=r[0][11:16], foreign=f.get("foreign_net_qty"),
                             inst=f.get("institution_net_qty"), oi=f.get("open_interest")))
            cur = r[0][:10]
        con.close()
    except Exception as e:
        out["error"] = "선물 투자자 읽기 실패: %s" % e
        rows, prev = [], []
    out["prev"] = prev
    pts = [(r[0][11:16], json.loads(r[1])) for r in rows]
    if pts:
        def g(f, k):
            return f.get(k)
        path = []
        for a in FLOW_ANCHORS:
            hit = [x for x in pts if x[0] <= a]
            if hit and hit[-1][0] >= pts[0][0] and (not path or path[-1]["t"] != hit[-1][0]):
                path.append(dict(t=hit[-1][0], foreign=g(hit[-1][1], "foreign_net_qty"),
                                 inst=g(hit[-1][1], "institution_net_qty"), retail=g(hit[-1][1], "retail_net_qty"),
                                 oi=g(hit[-1][1], "open_interest")))
        last = pts[-1]
        if path[-1]["t"] != last[0]:
            path.append(dict(t=last[0], foreign=g(last[1], "foreign_net_qty"), inst=g(last[1], "institution_net_qty"),
                             retail=g(last[1], "retail_net_qty"), oi=g(last[1], "open_interest")))
        out["fut_path"] = path
        fv = [(t, f.get("foreign_net_qty")) for t, f in pts if f.get("foreign_net_qty") is not None]
        if fv:
            lo = min(fv, key=lambda x: x[1])
            hi_ = max(fv, key=lambda x: x[1])
            out["fut_extreme"] = dict(min_t=lo[0], min=lo[1], max_t=hi_[0], max=hi_[1])
            # 최근 45분 변화 — 막판 급반전 감지(10/12: 14:47→15:34 +1,863)
            tl = _hm(fv[-1][0])
            base = [x for x in fv if _hm(x[0]) <= tl - 45]
            if base:
                out["fut_last45"] = dict(t0=base[-1][0], d=fv[-1][1] - base[-1][1])
        out["fut_amt"] = dict(foreign=last[1].get("foreign_amt_mn"), inst=last[1].get("institution_amt_mn"))
    # 옵션·현물 — 수량과 금액을 함께(7222)
    p2 = os.path.join(ROOT, "data", "db", "option_flow.db").replace("\\", "/")
    bt = t_cut or "23:59"
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p2, uri=True, timeout=5.0)
        for prod in ("mon_call", "mon_put", "kospi_spot"):
            for inv in ("foreign", "institution"):
                r = con.execute("SELECT bar_time, net_qty, net_amt FROM option_investor_flow WHERE trade_date=? AND product=?"
                                " AND investor=? AND bar_time<=? ORDER BY bar_time DESC LIMIT 1", (day, prod, inv, bt)).fetchone()
                out["%s_%s" % (prod, inv)] = dict(t=r[0], qty=r[1], amt=r[2]) if r else None
        con.close()
    except Exception as e:
        out["error2"] = "옵션·현물 읽기 실패: %s" % e
    # 해석 플래그 — 판정이 아니라 「확인할 것」 목록. 근거 수치를 함께 남긴다.
    flags = []
    fp = out.get("fut_path") or []
    sf, si = out.get("kospi_spot_foreign"), out.get("kospi_spot_institution")
    if fp and sf and fp[-1]["foreign"] is not None and sf["qty"] is not None:
        ff = fp[-1]["foreign"]
        if ff > 0 > sf["qty"]:
            flags.append("선물 외인 매수(%+d) · 현물 외인 매도(%+d) — 방향 베팅보다 현선 교체·헤지 가능성" % (ff, sf["qty"]))
        elif ff < 0 < sf["qty"]:
            flags.append("선물 외인 매도(%+d) · 현물 외인 매수(%+d) — 현물 헤지 매도 가능성" % (ff, sf["qty"]))
        if si and si["qty"] is not None and fp[-1]["inst"] is not None and (fp[-1]["inst"] > 0) != (si["qty"] > 0) \
                and (fp[-1]["inst"] > 0) != (ff > 0):
            flags.append("기관 선물(%+d)·현물(%+d) 반대 — 외인 선물의 반대편이 차익거래일 수 있다" % (fp[-1]["inst"], si["qty"]))
    if len(fp) >= 2 and fp[0]["oi"] and fp[-1]["oi"]:
        d_oi = fp[-1]["oi"] - fp[0]["oi"]
        flags.append("미결제 %+d (%+.0f%%) — %s" % (d_oi, d_oi * 100.0 / fp[0]["oi"],
                                                 "신규 포지션 유입" if d_oi > 0 else "포지션 청산(커버·정리)"))
    if out.get("fut_last45") and abs(out["fut_last45"]["d"]) >= 1000:
        flags.append("최근 45분 외인 선물 %+d (%s 이후) — 급변. 막판 한 구간으로 방향을 단정하지 말 것"
                     % (out["fut_last45"]["d"], out["fut_last45"]["t0"]))
    for leg, ko in (("mon_call", "콜"), ("mon_put", "풋")):
        x = out.get("%s_foreign" % leg)
        if not (x and x["qty"] is not None and x["amt"] is not None and abs(x["amt"]) >= 3000):
            continue
        # 평균 프리미엄(pt) = 금액(백만원)×1e6 ÷ (수량×승수 25만) = 금액×4÷수량. 부호가 어긋나거나 30pt 를 넘으면
        # 한 방향 매매로는 설명이 안 된다 — 비싼 행사가와 싼 행사가를 반대로 거래한 것(교체·이익실현·롤).
        prem = (x["amt"] * 4.0 / x["qty"]) if x["qty"] else None
        if prem is None or prem < 0 or prem > 30:
            flags.append("먼스리 %s 외인 수량 %+d · 금액 %+d백만(평균 프리미엄 %s) — 비싼 행사가 %s · 싼 행사가 %s(교체·이익실현 의심)"
                         % (ko, x["qty"], x["amt"], "산출불가" if prem is None else "%.0fpt" % prem,
                            "매도" if x["amt"] < 0 else "매수", "매수" if x["amt"] < 0 else "매도"))
    if prev and all(p_["foreign"] is not None for p_ in prev):
        s = sum(p_["foreign"] for p_ in prev)
        flags.append("직전 %d거래일 외인 선물 합 %+d — 오늘 값은 이 누적 포지션 위의 증감이다" % (len(prev), s))
    out["flags"] = flags
    return out


def _render_foreign(fp):
    """_foreign_profile 출력 → 해설에 그대로 옮길 수 있는 표 형식 줄."""
    if not fp:
        return []
    L = ["", "### 외인 동향 (%s)" % ("마감 누계" if not fp.get("t_cut") else "~" + fp["t_cut"])]
    for k in ("error", "error2"):
        if fp.get(k):
            L.append("⚠ " + fp[k])
    if fp.get("prev"):
        L.append("직전 거래일 외인 선물 마감: " + " · ".join("%s %s" % (p["date"][5:], "%+d" % p["foreign"] if p["foreign"] is not None else "미측정")
                                                    for p in reversed(fp["prev"])))
    if fp.get("fut_path"):
        L.append("| 시각 | 외인 | 기관 | 개인 | 미결제 |")
        L.append("|---|---|---|---|---|")
        sg = lambda v: "—" if v is None else "%+d" % v
        for r in fp["fut_path"]:
            L.append("| %s | %s | %s | %s | %s |" % (r["t"], sg(r["foreign"]), sg(r["inst"]), sg(r["retail"]),
                                                     "—" if r["oi"] is None else r["oi"]))
        ex = fp.get("fut_extreme")
        if ex:
            L.append("외인 선물 저점 %s %+d · 고점 %s %+d" % (ex["min_t"], ex["min"], ex["max_t"], ex["max"]))
    else:
        L.append("선물 투자자 경로 미측정")
    cells = []
    for prod, ko in (("mon_call", "먼스리 콜"), ("mon_put", "먼스리 풋"), ("kospi_spot", "현물")):
        for inv, iko in (("foreign", "외인"), ("institution", "기관")):
            x = fp.get("%s_%s" % (prod, inv))
            cells.append("%s %s %s" % (ko, iko, ("수량 %+d · 금액 %+d백만" % (x["qty"], x["amt"])) if x and x["qty"] is not None and x["amt"] is not None else "미측정"))
    L.append("옵션·현물: " + " / ".join(cells))
    if fp.get("flags"):
        L.append("확인할 것:")
        L.extend("  · " + f for f in fp["flags"])
    return L


def source_warnings(st, now=None):
    """[640차 ⑤] 원천 경고 — 사람이 해설에서 뒤늦게 발견하던 결함을 기계가 먼저 띄운다(계측 4원칙 ②④).
    10/20 해설이 손으로 적은 「전일 참조 8거래일 고착」「현물 외인 금액 부호 모순」이 계기. 판정이 아니라 「해석에 쓰지 말 것」 목록이다."""
    W = []
    if st.get("empty"):
        return W
    day = st["date"]
    pv = st.get("prev")
    if pv and pv.get("date"):
        gap = (_dt.date.fromisoformat(day) - _dt.date.fromisoformat(pv["date"])).days
        if gap > 5:
            W.append("전일 참조 고착 — 전일=%s(%d일 전). 정규봉 적재 공백. 전일 고저·종가를 레벨 근거로 쓰지 말 것" % (pv["date"], gap))
    elif not pv:
        W.append("전일 참조 없음 — 정규봉 DB 에 이전 거래일이 없다(미측정)")
    fp = st.get("foreign") or {}
    sf = fp.get("kospi_spot_foreign")
    if sf and sf.get("qty") not in (None, 0) and sf.get("amt") not in (None, 0) and (sf["qty"] > 0) != (sf["amt"] > 0):
        W.append("현물 외인 수량(%+d)·금액(%+d백만) 부호 모순 — 금액 열 스케일/부호 오류 의심. 수량 부호만 쓸 것" % (sf["qty"], sf["amt"]))
    if st.get("live") and fp.get("fut_path"):
        try:
            lag = _hm(st["last_bar"]) - _hm(fp["fut_path"][-1]["t"])
            if lag > 10:
                W.append("7221 선물 투자자 최신 %s — 완결 봉 %s 보다 %d분 늦다(수집 지연). 외인 선물 경로를 현재값으로 읽지 말 것" % (fp["fut_path"][-1]["t"], st["last_bar"], lag))
        except Exception:
            pass
    if st.get("live") and not fp.get("fut_path"):
        W.append("7221 선물 투자자 경로 없음 — 오늘 수집 전이거나 미륵이 미실행(미측정)")
    f = st.get("flow") or {}
    if f.get("mon_call") is None or f.get("mon_put") is None:
        W.append("먼스리 외인 콜/풋 금액 결손 — 콜−풋 수준(L2)을 판단에 쓰지 말 것")
    if f.get("wk_prod") and f["wk_prod"] != "mon" and (f.get("wk_call") is None or f.get("wk_put") is None):
        W.append("위클리[%s] 외인 콜/풋 결손 — 위클리 항 미측정" % f["wk_prod"])
    rv = st.get("rival") or {}
    if not rv.get("present"):
        W.append("상대의 수 미측정 — %s" % (rv.get("why") or "shindong.db 기록 없음"))
    sg = rv.get("signals") or {}
    if rv.get("present") and sg and not sg.get("present"):
        W.append("상대 신호원 미측정 — %s" % sg.get("why"))
    if st.get("live") and now is not None and st.get("last_bar"):
        lag = _hm(now.strftime("%H:%M")) - _hm(st["last_bar"])
        if lag > 3 and now.strftime("%H:%M") < "15:12":
            W.append("완결 봉 %s — 지금보다 %d분 늦다(봉 수집 지연 또는 재기동). 가격·보유 평가가 낡았다" % (st["last_bar"], lag))
    return W


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
    # [v2 · 2026-10-10] 옵션은 금액(백만원) · 위클리 = 만기 최근접(먼스리 만기주는 기권) — 신동2 사전등록 v2
    from strategy.shindong.calendar import select_flow_product
    wk, _wk_exp, wk_why = select_flow_product(_dt.date.fromisoformat(day))
    mc, mp = _opt_amt(day, "mon", t0)
    mc10, mp10 = _opt_amt(day, "mon", t10)
    wc, wp = _opt_amt(day, wk, t0) if wk != "mon" else (None, None)
    st["flow"] = dict(
        fut_foreign=at(fut.get("foreign"), t0), fut_foreign_10=at(fut.get("foreign"), t10),
        fut_inst=at(fut.get("institution"), t0),
        unit="백만원", wk_prod=wk, wk_why=wk_why if wk != "mon" else wk_why + " — 위클리 항 기권(O1 과 같은 원천)",
        mon_call=mc, mon_put=mp, wk_call=wc, wk_put=wp,
        spot=_spot_foreign(day, t0),
        mon_call_10=mc10, mon_put_10=mp10)
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
    st["foreign"] = _foreign_profile(day, last[0] if live else None)   # 683차 — 외인 동향(경로·현선·옵션 수량/금액)
    st["peter"] = dict(trades=(d.get("peter") or {}).get("trades", []), available=(d.get("peter") or {}).get("available"))
    # [MW0602 640차] 상대의 수 — 신동 v3 MAIN·섀도 5종(shindong.db 하루치 PK 조회). 실패해도 상태는 만든다(미측정으로 표시).
    try:
        import shindong2_rival as RV
        st["rival"] = RV.read_day(day, last_close=last[4], live=live)
        st["rival"]["signals"] = RV.signal_state(day, upto=last[0] if live else None)   # ② 상대가 지금 보는 것
    except Exception as e:                                               # 미측정 ≠ 0 — 사유를 남긴다
        st["rival"] = dict(present=False, why="상대의 수 읽기 실패: %s" % e, variants={})
    # [640차 ④] AI 지표(장착) — 레지스트리에 「장착」이 있을 때만. 플러그인은 하루치 조회만 한다(456차).
    try:
        import shindong2_research as RS
        st["ai_indicators"] = RS.mounted_values(day, last[0] if live else None)
    except Exception as e:
        st["ai_indicators"] = [dict(id="?", title="지표 읽기 실패", value=None, lean=None, why=str(e)[:120])]
    st["bars_n"] = len(bars)
    st["source_warnings"] = source_warnings(st, now)            # [640차 ⑤] 원천 경고 — snapshot 끝과 사다리 띠에 같이 뜬다
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
        if r.get("backfill") or (r.get("variant") or "live") != "live":   # 섀도(legacy)는 실제 재량이 아니다
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
    return os.path.join(DOC_DIR, "신동2_해설_%s-%s.md" % (PC, day.replace("-", "")))


SCEN_REQUIRED_PHASES = ("premarket", "intraday", "overnight")   # 683차 — 전망이 있는 단계는 확률 시나리오 필수
SCEN_REQUIRED_ACTIONS = ("plan", "stand", "note")


VS_MAIN = ("agree", "disagree", "abstain")                       # ② 상대의 수에 대한 판단 — 동의 / 반대 / 기권
VS_MAIN_KO = {"agree": "동의", "disagree": "반대", "abstain": "기권"}
VS_MAIN_PARSE = {"동의": "agree", "반대": "disagree", "기권": "abstain", "agree": "agree", "disagree": "disagree", "abstain": "abstain"}
VS_REQUIRED_PHASES = ("premarket", "intraday")                   # 상대의 오늘 수가 보이는 단계 — 익일(overnight)은 상대가 아직 없다


def parse_vs_main_line(comment):
    """본문의 「상대판단: 반대 | 이유」 한 줄 → (vs_main, why). 없으면 (None, None)."""
    for line in (comment or "").splitlines():
        s = line.strip()
        if s.startswith("상대판단:"):
            body = s[len("상대판단:"):].strip()
            head, _, why = body.partition("|")
            vm = VS_MAIN_PARSE.get(head.strip())
            return vm, why.strip() or None
    return None, None


def record(day, phase, action, direction, entry, stop, target, comment, now=None, variant="live", lessons=None, scenarios=None,
           vs_main=None, vs_why=None, strategy=None):
    now = now or _dt.datetime.now()
    if vs_main is not None and vs_main not in VS_MAIN:
        raise SystemExit("--vs-main 은 %s 중 하나" % (VS_MAIN,))
    if phase not in PHASES or action not in ACTIONS:
        raise SystemExit("phase/action 이 잘못됐다: %s / %s" % (phase, action))
    if action == "plan" and direction in ("매수", "매도") and (stop is None or target is None):
        raise SystemExit("plan 은 손절·청산을 함께 적어야 한다(채점 불가 기록 금지)")
    if variant not in VARIANTS:
        raise SystemExit("variant 는 %s 중 하나" % (VARIANTS,))
    if variant == "legacy" and (phase not in ("overnight", "premarket") or action not in ("plan", "stand")):
        raise SystemExit("legacy(기존방식 섀도)는 overnight/premarket 의 plan·stand 만 — 장중 관리는 live 하나다")
    log = load_ai_log(day)
    rid = "%s-%02d" % (now.strftime("%H%M%S"), len(log) + 1)
    rec = dict(id=rid, ts=now.isoformat(timespec="seconds"), date=day, phase=phase, action=action, dir=direction,
               entry=entry, stop=stop, target=target, comment=comment, variant=variant, lessons=sorted(set(lessons or [])))
    if scenarios:                                        # 683차 — 확률·경로 시나리오(채점 대상). 명세 검증은 parse_spec
        import shindong2_scenario as SC
        rec["scenarios"] = dict(spec=scenarios, horizon=SC.HORIZON, items=SC.parse_spec(scenarios))
    # [640차 ②] 상대의 수에 대한 판단 — live 장전·장중 plan/stand/note 에 기록한다. 빠지면 기권으로 저장하되 **빠졌다는 사실**을 남긴다
    #   (계측 4원칙 ④ 폴백 가시화). 기권은 동의율 분모에서 빠진다 — 반대를 피하려고 기권하면 능가의 증거가 안 쌓인다.
    if variant == "live" and action in ("plan", "stand", "note"):
        if vs_main is None:
            vs_main, vs_why = parse_vs_main_line(comment)
        if vs_main is None and phase in VS_REQUIRED_PHASES:
            rec["vs_main"], rec["vs_main_missing"] = "abstain", True
        elif vs_main is not None:
            rec["vs_main"] = vs_main
        if vs_why:
            rec["vs_why"] = vs_why
    if strategy and variant == "live":                   # [640차 ③] 이 계획이 따른 AI 전략(S-n). 존재 검증은 장후 feedback 이 한다(장중 가벼운 경로)
        rec["strategy"] = strategy.strip()
    _append_jsonl(os.path.join(day_dir(day), "ai_log.jsonl"), rec)
    if variant == "live":                                # 섀도는 패널 최신 해설을 덮지 않는다
        _atomic_json(os.path.join(day_dir(day), "ai_latest.json"), rec)
    with open(_doc_path(day), "a", encoding="utf-8") as f:
        if os.path.getsize(_doc_path(day)) == 0:
            f.write("# 신동2 해설 — %s (%s)\n\n> Claude 재량 제안 기록. append-only · 시각은 벽시계 · 채점은 `scripts/shindong2_live.py score`.\n"
                    "> 주문 없음(절대원칙 §6). 별개 주체 「신동2-AI」 — 경쟁자는 신동 v3 MAIN·섀도 5종(「상대의 수」, 640차). "
                    "같은 단위(pt/계약·수수료 포함)로 채점한다.\n\n" % (day, PC))
        plan = ""
        if direction in ("매수", "매도") or entry is not None or stop is not None or target is not None:
            plan = " · **%s** 진입 %s · 손절 %s · 청산 %s" % (direction or "—", entry if entry is not None else "시장가", stop, target)
        tag = " 〔기존방식 섀도 — 채점 비교용〕" if variant == "legacy" else ""
        les = (" · 레슨 " + ", ".join(rec["lessons"])) if rec["lessons"] else ""
        if rec.get("strategy"):
            les += " · 전략 " + rec["strategy"]
        if rec.get("vs_main"):
            les += " · 상대 판단 **%s**%s%s" % (VS_MAIN_KO[rec["vs_main"]], ("(미기재 → 기권)" if rec.get("vs_main_missing") else ""),
                                            (" — " + rec["vs_why"]) if rec.get("vs_why") else "")
        sc = ""
        if rec.get("scenarios"):
            sc = "\n\n> 채점용 시나리오: " + " · ".join("%s %s %d%% (목표 %s · 무효 %s%s)" % (
                i["key"], i["name"], i["prob"], i["target"], i["invalid"], (" · 이후 %s" % i["then"]) if i.get("then") is not None else "")
                for i in rec["scenarios"]["items"])
        f.write("## %s %s — %s%s%s%s\n\n%s%s\n\n" % (now.strftime("%H:%M"), PHASE_KO[phase], action, plan, les, tag,
                                                    (comment or "").strip(), sc))
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
    L.append("옵션 외인(%s) — 먼스리 콜 %s 풋 %s (콜−풋 %s, Δ10 %s) · 위클리[%s] 콜 %s 풋 %s (콜−풋 %s) · 현물 외인 %s" % (
        f.get("unit", "—"), f["mon_call"], f["mon_put"], cp(f["mon_call"], f["mon_put"]),
        d10(cp(f["mon_call"], f["mon_put"]), cp(f["mon_call_10"], f["mon_put_10"])),
        f.get("wk_why", "—"), f["wk_call"], f["wk_put"], cp(f["wk_call"], f["wk_put"]), f["spot"]))
    L.extend(_render_foreign(st.get("foreign")))
    L.append("")
    L.append("맥점 위 %s · 아래 %s · 벽 %s" % (st["levels"]["above"], st["levels"]["below"], st["walls"]))
    # [MW0602 640차] 상대의 수 — 경쟁자(신동 v3 MAIN·섀도)가 오늘 어디서 들어가 어디서 나갔나. 따라 할 신호가 아니다.
    if st.get("rival") is not None:
        import shindong2_rival as RV
        L.append("")
        L.extend(RV.summary_lines(st["rival"]))
        L.extend(RV.signal_lines(st["rival"].get("signals")))
        L.append("→ 새 계획/관망 기록에는 `--vs-main agree|disagree|abstain --vs-why \"…\"`(또는 본문 `상대판단: 반대 | 이유`) 를 넣을 것.")
    if st.get("ai_indicators"):
        import shindong2_research as RS
        L.append("")
        L.extend(RS.values_lines(st["ai_indicators"]))
    sm = st["sd2"]["summary"] or {}
    L.append("(사료) 신동2 기본·P·P2·P3 손익 — 기본 %s · P %s · P2 %s · P3 %s  ※ 2026-10-20 부터 대조군이 아니다(채점 제외)" % (
        sm.get("base"), sm.get("p"), sm.get("p2"), sm.get("p3")))
    if ai:
        L.append("재량(AI) — 손익 %s · 거래 %d · 대기 %s" % (ai["pnl"], len(ai["trades"]),
                 ("%s 진입 %s 손절 %s 청산 %s" % ("매수" if ai["pending"]["sgn"] > 0 else "매도", ai["pending"]["entry"] or "시장가",
                                            ai["pending"]["stop"], ai["pending"]["target"])) if ai.get("pending") else "없음"))
        for t in ai["trades"]:
            L.append("  AI %s %s @%.2f → %s %s %+.2f" % (t["entry_t"], t["side"], t["fill"], t.get("exit_t") or "보유 중", t.get("why", "평가"), t["pnl"]))
    if "scen" in st:
        import shindong2_scenario as SC
        L.extend(SC.render_status(st["scen"]))
        L.append("")
    L.append("새 이벤트 %d건" % len(new))
    for e in new:
        L.append("  · [%s] %s" % (e["kind"], e["text"]))
    if st.get("warnings"):
        L.append("경고: " + " · ".join(st["warnings"]))
    if st.get("source_warnings"):
        L.append("🔴 원천 경고(해석에 쓰지 말 것):")
        L.extend("  · " + w for w in st["source_warnings"])
    return "\n".join(L)


def scenario_sets(day, bars, log, final):
    """683차 — 그날 live 기록 중 시나리오가 달린 것을 채점(장중이면 잠정)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import shindong2_scenario as SC
    import shindong2_learn as LN
    recs = [r for r in log if (r.get("variant") or "live") == "live" and r.get("scenarios")]
    return SC.evaluate_sets(recs, bars, lambda r: LN.effective_time(r, day), final)


def cmd_snapshot(day, now=None):
    now = now or _dt.datetime.now()
    st, d = build_state(day, now)
    ai = None
    if not st.get("empty"):
        bars = d["candles"][:-1] if st["live"] else d["candles"]
        log = load_ai_log(day)
        ai = simulate_ai(day, bars, log, live=st["live"])
        st["ai"] = ai
        st["scen"] = scenario_sets(day, bars, log, final=not st["live"])   # 683차 — 직전 예측 → 지금까지 결과
    new = save_new_events(day, detect_events(st, ai["trades"] if ai else None), now)
    _atomic_json(os.path.join(day_dir(day), "state.json"), st)
    return st, new, ai


def _split(x):
    return [t.strip() for t in (x or "").split(",") if t.strip()]


def _learn_cmd(a):
    """672차 — 학습 사이클 하위명령. 무거운 평가(DB 읽기)는 장후 전용이다(456차)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import shindong2_learn as LN
    if a.cmd == "evaluate":
        out = LN.evaluate_day(a.date)
        print(LN.render_eval(out))
        return 0
    if a.cmd == "feedback":
        comment = a.comment
        if a.comment_file == "-":
            comment = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        elif a.comment_file:
            with open(a.comment_file, encoding="utf-8") as f:
                comment = f.read()
        if not comment.strip():
            raise SystemExit("피드백 본문이 비었다 — 잘한 점·잘못한 점·개선점·레슨을 적을 것")
        rec, out, p = LN.feedback(a.date, comment, applied=_split(a.applied), hits=_split(a.hit), misses=_split(a.miss))
        print(LN.render_eval(out))
        print("\n피드백 기록 %s · 적용 %s · 적중 %s · 실패 %s · 문서 %s" % (rec["ts"], rec["applied"], rec["hits"], rec["misses"], p))
        return 0
    if a.cmd == "strategy":                              # [640차 ③] AI 전략 S-n — 5축 세트
        if a.op == "add":
            if not (a.id and a.title):
                raise SystemExit("strategy add 는 --id --title 와 5축(--dir-rule --entry-rule --stop-rule --exit-rule --prob-rule) 필수")
            rules = {"방향": a.dir_rule or "", "진입": a.entry_rule or "", "손절": a.stop_rule or "", "청산": a.exit_rule or "", "확률": a.prob_rule or ""}
            s = LN.strategy_add(a.id, a.title, rules, lessons=_split(a.lessons), status=a.status or "후보", origin=a.origin, note=a.note or "")
            print("전략 신설 %s [%s] %s" % (s["id"], s["status"], s["title"]))
        elif a.op == "set":
            if not a.id:
                raise SystemExit("--id 필수")
            rules = {k: v for k, v in (("방향", a.dir_rule), ("진입", a.entry_rule), ("손절", a.stop_rule), ("청산", a.exit_rule), ("확률", a.prob_rule)) if v}
            s = LN.strategy_set(a.id, status=a.status, note=a.note, rules=rules, why=a.why)
            print("전략 갱신 %s [%s] %s" % (s["id"], s["status"], s["title"]))
        elif a.op == "tally":
            if not a.id or not (a.hit or a.miss or a.applied):
                raise SystemExit("--id 와 --hit/--miss/--applied 중 하나")
            s = LN.strategy_tally(a.id, a.date, hit=(True if a.hit else False if a.miss else None), applied=True)
            print("전략 집계 %s 적용 %d · 적중 %d · 실패 %d · MAIN우위 %d" % (s["id"], len(s["applied"]), len(s["hit"]), len(s["miss"]), len(s.get("beat_main", []))))
        else:
            print(LN.strategies_text(active_only=a.active))
        return 0
    if a.cmd == "lesson":
        if a.op == "add":
            if not (a.id and a.title and a.rule):
                raise SystemExit("lesson add 는 --id --title --rule 필수")
            l = LN.lesson_add(a.id, a.title, a.rule, trigger=a.trigger, status=a.status or "후보", origin=a.origin,
                              evidence=_split(a.evidence), note=a.note or "", axis=a.axis)
            print("레슨 신설 %s [%s%s] %s" % (l["id"], l["status"], ("·" + l["axis"]) if l.get("axis") else "", l["title"]))
        elif a.op == "set":
            if not a.id:
                raise SystemExit("--id 필수")
            l = LN.lesson_set(a.id, status=a.status, note=a.note, rule=a.rule, why=a.why, axis=a.axis)
            print("레슨 갱신 %s [%s%s] %s" % (l["id"], l["status"], ("·" + l["axis"]) if l.get("axis") else "", l["title"]))
        elif a.op == "tally":
            if not a.id or not (a.hit or a.miss or a.applied):
                raise SystemExit("--id 와 --hit/--miss/--applied 중 하나")
            l = LN.lesson_tally(a.id, a.date, hit=(True if a.hit else False if a.miss else None), applied=True)
            print("레슨 집계 %s 적용 %d · 적중 %d · 실패 %d" % (l["id"], len(l["applied"]), len(l["hit"]), len(l["miss"])))
        else:
            print(LN.lessons_text(active_only=a.active))
        return 0
    if a.cmd == "trend":
        out = LN.trend(a.date)
        print(LN.trend_text(out, last=a.last))
        print("\n문서 %s" % os.path.join(LN.LEARN_DIR, "추이_%s.md" % PC))
        return 0
    if a.cmd == "brief":
        print(LN.brief(a.date))
        return 0
    return 1


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
    r.add_argument("--variant", default="live", choices=VARIANTS, help="legacy = 기존방식 섀도(채점 비교용)")
    r.add_argument("--lessons", default="", help="이 계획에 적용한 레슨 ID, 쉼표 구분(예: L1,L9)")
    r.add_argument("--scenarios", default="", help="확률 시나리오 '키|이름|확률|목표|무효[|이후] ; …' (합 100, 5%% 단위)")
    r.add_argument("--vs-main", default=None, choices=VS_MAIN, help="[640차] 상대(신동 v3 MAIN)의 수에 대한 판단 — 본문 '상대판단: 반대 | 이유' 로도 받는다")
    r.add_argument("--vs-why", default=None, help="동의/반대/기권의 이유 한 줄")
    r.add_argument("--strategy", default=None, help="[640차 ③] 이 계획이 따른 AI 전략 ID(예: S1) — 레지스트리 `strategy list`")
    # ── 672차 학습 사이클 ──
    e = sub.add_parser("evaluate", help="그날 계획(익일계획·장전계획 live/legacy) 단독 시뮬 평가")
    e.add_argument("--date", default=_dt.date.today().isoformat())
    fb = sub.add_parser("feedback", help="기계 평가 + 평가·반성 본문을 피드백 문서에 남기고 레슨 집계 갱신")
    fb.add_argument("--date", default=_dt.date.today().isoformat())
    fb.add_argument("--applied", default="", help="오늘 적용한 레슨 ID(쉼표)")
    fb.add_argument("--hit", default="", help="오늘 적중한 레슨 ID(쉼표)")
    fb.add_argument("--miss", default="", help="오늘 실패한 레슨 ID(쉼표)")
    fb.add_argument("--comment", default="")
    fb.add_argument("--comment-file")
    ls = sub.add_parser("lesson", help="레슨런 레지스트리")
    ls.add_argument("op", choices=("add", "set", "tally", "list"))
    ls.add_argument("--id")
    ls.add_argument("--title")
    ls.add_argument("--rule")
    ls.add_argument("--trigger", default="")
    ls.add_argument("--status")
    ls.add_argument("--origin")
    ls.add_argument("--evidence", default="", help="근거 날짜(쉼표)")
    ls.add_argument("--note")
    ls.add_argument("--why", default="")
    ls.add_argument("--date", default=_dt.date.today().isoformat())
    ls.add_argument("--hit", action="store_true")
    ls.add_argument("--miss", action="store_true")
    ls.add_argument("--applied", action="store_true")
    ls.add_argument("--active", action="store_true")
    ls.add_argument("--axis", default=None, help="[640차 ③] 레슨의 축 — 방향|진입|손절|청산|확률|계측")
    sg = sub.add_parser("strategy", help="[640차 ③] AI 전략 레지스트리 S-n — 방향·진입·손절·청산·확률 5축 세트")
    sg.add_argument("op", choices=("add", "set", "tally", "list"))
    sg.add_argument("--id")
    sg.add_argument("--title")
    sg.add_argument("--dir-rule")
    sg.add_argument("--entry-rule")
    sg.add_argument("--stop-rule")
    sg.add_argument("--exit-rule")
    sg.add_argument("--prob-rule")
    sg.add_argument("--lessons", default="", help="이 전략을 이루는 레슨 ID(쉼표)")
    sg.add_argument("--status")
    sg.add_argument("--origin")
    sg.add_argument("--note")
    sg.add_argument("--why", default="")
    sg.add_argument("--date", default=_dt.date.today().isoformat())
    sg.add_argument("--hit", action="store_true")
    sg.add_argument("--miss", action="store_true")
    sg.add_argument("--applied", action="store_true")
    sg.add_argument("--active", action="store_true")
    tr = sub.add_parser("trend", help="워크포워드 추이 + 딥다이브 판정")
    tr.add_argument("--date", default=_dt.date.today().isoformat())
    tr.add_argument("--last", type=int, default=10)
    br = sub.add_parser("brief", help="장전 브리핑 — 활성 레슨·전일 피드백·추이")
    br.add_argument("--date", default=_dt.date.today().isoformat())
    a = ap.parse_args(argv)
    if a.cmd in ("evaluate", "feedback", "lesson", "strategy", "trend", "brief"):
        return _learn_cmd(a)
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
        lessons = [x.strip() for x in a.lessons.split(",") if x.strip()]
        if not a.scenarios.strip():                  # 본문(heredoc) 안 「시나리오명세: …」 한 줄 — 명령행에 | ; 를 쓰지 않는 경로
            for line in (comment or "").splitlines():
                if line.strip().startswith("시나리오명세:"):
                    a.scenarios = line.strip()[len("시나리오명세:"):].strip()
        if (a.variant == "live" and a.phase in SCEN_REQUIRED_PHASES and a.action in SCEN_REQUIRED_ACTIONS
                and not a.scenarios.strip()):
            raise SystemExit("%s %s 기록에는 --scenarios 가 필수다(확률·경로 시나리오 — 채점·보정 학습의 입력). "
                             "형식 '키|이름|확률|목표|무효[|이후] ; …', 합 100. 확률이 그대로면 직전 명세를 다시 넘길 것." % (a.phase, a.action))
        rec = record(day, a.phase, a.action, a.dir, a.entry, a.stop, a.target, comment, variant=a.variant, lessons=lessons,
                     scenarios=a.scenarios.strip() or None, vs_main=a.vs_main, vs_why=a.vs_why, strategy=a.strategy)
        print("기록 %s %s %s %s%s%s%s%s · 문서 %s" % (rec["id"], rec["phase"], rec["action"], rec["dir"],
                                                     " [legacy 섀도]" if a.variant == "legacy" else "",
                                                     (" 레슨 " + ",".join(lessons)) if lessons else "",
                                                     (" 시나리오 " + "/".join("%s%d" % (i["key"], i["prob"]) for i in rec["scenarios"]["items"]))
                                                     if rec.get("scenarios") else "",
                                                     (" 상대판단 " + VS_MAIN_KO[rec["vs_main"]]) if rec.get("vs_main") else "", _doc_path(day)))
        if rec.get("vs_main_missing"):
            print("⚠ 상대 판단(--vs-main / 본문 「상대판단: …」)이 빠져 기권으로 저장했다 — 동의율 분모에서 빠진다. 다음 기록부터 반드시 넣을 것.")
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
