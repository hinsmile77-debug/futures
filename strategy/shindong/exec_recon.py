# -*- coding: utf-8 -*-
"""[MW0601 705차] 신동 실거래 대사 — 실제 체결(trades.db) vs 재생 MAIN(engine.run_day).

왜 필요한가
-----------
신동 일일 리포트의 MAIN 손익은 **장후 재생**이다 — 그날 마지막 흐름 데이터로 하루를 다시 돌린 값.
실거래는 **장중 그 시점 재생이 낸 신호로 친 수**다. 7222 는 매분 최근 18행을 다시 받아 덮어쓰므로
과거 분의 흐름이 정정되고, 신호가 생겼다 사라진다(RETRACTED). 그래서 둘은 구조적으로 갈린다.

2026-10-22 실측: 리포트 MAIN +259.9만 vs 실거래 +112.7만(브로커 net +112.7만) — 차 147.2만.
  · 실거래에만 3건(−30.0만) — 전부 진입 뒤 재생에서 철회된 신호
  · 재생에만 3건(+120.1만) — 늦게 알아챔 1 · 보유 중 2
  · 일치 6건 — 실거래 +3.1만(체결가·요율)
리포트가 실거래를 한 줄도 싣지 않아 「패널과 안 맞는다」로만 드러났다(계측 4원칙 ⑤).

분류
----
- MATCH            실거래 ↔ 재생 MAIN 같은 신호(trade_key)
- EXEC_RETRACTED   실거래가 있는데 그 신호가 최종 재생에 없다(철회)
- EXEC_UNKEYED     실거래가 있는데 집행 기록(ENTER)과 못 짝지었다(수동·복원 등) — 숨기지 않는다
- REPLAY_ONLY      재생 MAIN 에만 있다. 사유는 집행 이벤트에서: SKIP_STALE(늦게 알아챔) ·
                   SKIP_HOLDING(보유 중) · REJECT(기각 사유) · 기록 없음(미측정)

⚠ 읽기 전용. 주문·기록을 바꾸지 않는다.
⚠ 사전등록 채점(MAIN 재생, RETRACTED 제외)은 이 모듈이 바꾸지 않는다 — 실집행 누적은 **참고 행**이다.
"""
import datetime as _dt
import math
import os
import sqlite3
from typing import Any, Dict, List, Optional

SOURCE = "SHINDONG"
# 실거래 진입 시각과 ENTER 이벤트 시각이 같은 초가 아닐 때 허용하는 차(초) — 같은 방향만.
MATCH_TOL_SEC = 90


def _ts(s: Any) -> Optional[_dt.datetime]:
    if not s:
        return None
    s = str(s).replace("T", " ")[:19]
    try:
        return _dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _ro(db: str) -> Optional[sqlite3.Connection]:
    if not db or not os.path.exists(db):
        return None
    return sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)


def real_positions(trades_db: str, trade_date: str, source: str = SOURCE) -> Optional[List[Dict[str, Any]]]:
    """그날 청산된 실거래를 **포지션 단위**로 묶는다(계측 4원칙 ① — 레그 단위로 세지 않는다).

    묶음 키 = (entry_ts, direction). 반환 None = DB 없음(미측정 — 빈 리스트와 다르다).
    """
    con = _ro(trades_db)
    if con is None:
        return None
    try:
        rows = con.execute(
            "SELECT entry_ts, exit_ts, direction, quantity, entry_price, exit_price, "
            "       COALESCE(net_pnl_krw, pnl_krw), exit_reason "
            "FROM trades WHERE entry_source=? AND substr(exit_ts,1,10)=? ORDER BY entry_ts, exit_ts",
            (source, trade_date)).fetchall()
    finally:
        con.close()
    pos: Dict[tuple, Dict[str, Any]] = {}
    for ets, xts, dr, q, epx, xpx, net, why in rows:
        k = (str(ets)[:19], dr)
        p = pos.setdefault(k, dict(entry_ts=str(ets)[:19], direction=dr,
                                   side=1 if str(dr).upper() == "LONG" else -1,
                                   qty=0, entry_px=float(epx or 0), net=0.0, legs=[], exit_ts=None))
        p["qty"] += int(q or 0)
        p["net"] += float(net or 0)
        p["legs"].append((str(xts)[11:16], float(xpx or 0), why))
        p["exit_ts"] = str(xts)[:19]
    return sorted(pos.values(), key=lambda p: p["entry_ts"])


def other_sources(trades_db: str, trade_date: str, source: str = SOURCE) -> Optional[Dict[str, Any]]:
    """같은 날 신동 아닌 출처의 청산 — 브로커 net(계좌 전체)과 비교할 때 섞이는 몫."""
    con = _ro(trades_db)
    if con is None:
        return None
    try:
        r = con.execute(
            "SELECT COUNT(*), COALESCE(SUM(COALESCE(net_pnl_krw, pnl_krw)),0) FROM trades "
            "WHERE COALESCE(entry_source,'')<>? AND substr(exit_ts,1,10)=?", (source, trade_date)).fetchone()
    finally:
        con.close()
    return {"legs": int(r[0]), "net": float(r[1])}


def broker_net(trades_db: str, trade_date: str) -> Optional[Dict[str, Any]]:
    """`daily_broker_pnl.broker_net_krw`(계좌 전체 실측). 없으면 None — 0 으로 두지 않는다."""
    con = _ro(trades_db)
    if con is None:
        return None
    try:
        # [MW0602] dev 의 daily_broker_pnl 에는 broker_net_source 컬럼이 없다(v9-dev 전용).
        # 그 컬럼을 무조건 SELECT 하면 OperationalError → 실측 net 이 있어도 「미기록」으로 떨어진다.
        cols = {c[1] for c in con.execute("PRAGMA table_info(daily_broker_pnl)")}
        src = "broker_net_source" if "broker_net_source" in cols else "NULL"
        r = con.execute("SELECT broker_net_krw, %s FROM daily_broker_pnl WHERE date=?" % src,
                        (trade_date,)).fetchone()
    except sqlite3.OperationalError:
        r = None
    finally:
        con.close()
    if not r or r[0] is None:
        return None
    return {"net": float(r[0]), "source": r[1]}


def reconcile(main_rows: List[Dict[str, Any]], positions: List[Dict[str, Any]],
              events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """실거래 포지션 ↔ 재생 MAIN 행을 짝짓는다.

    main_rows: daily_report.trade_rows(MAIN) — key·side·entry_ts(HH:MM)·entry_px·net·legs
    events:    shindong_exec.jsonl — kind ∈ ENTER/RETRACTED/SKIP_STALE/SKIP_HOLDING/REJECT/…
    """
    by_key = {r["key"]: r for r in main_rows}
    enters = [e for e in events if e.get("kind") == "ENTER" and e.get("trade_key")]
    skip: Dict[str, str] = {}
    for e in events:
        k, kind = e.get("trade_key"), e.get("kind")
        if not k:
            continue
        if kind == "SKIP_STALE":
            skip.setdefault(k, "늦게 알아챔")
        elif kind == "SKIP_HOLDING":
            skip.setdefault(k, "보유 중(%s)" % (e.get("holding") or "?"))
        elif kind == "REJECT":
            skip.setdefault(k, "기각 — %s" % (e.get("why") or "?"))
    retracted = {e["trade_key"] for e in events if e.get("kind") == "RETRACTED" and e.get("trade_key")}

    used_enter = set()
    items: List[Dict[str, Any]] = []
    executed_keys = set()
    for p in positions:
        pt = _ts(p["entry_ts"])
        best, best_dt = None, None
        for i, e in enumerate(enters):
            if i in used_enter or int(e.get("side") or 0) not in (p["side"], 0):
                continue
            et = _ts(e.get("entered_at") or e.get("ts"))
            if pt is None or et is None:
                continue
            dt = abs((pt - et).total_seconds())
            if dt <= MATCH_TOL_SEC and (best_dt is None or dt < best_dt):
                best, best_dt = i, dt
        if best is None:
            items.append(dict(kind="EXEC_UNKEYED", key=None, real=p, replay=None))
            continue
        used_enter.add(best)
        k = enters[best]["trade_key"]
        executed_keys.add(k)
        r = by_key.get(k)
        if r is not None:
            items.append(dict(kind="MATCH", key=k, real=p, replay=r))
        else:
            items.append(dict(kind="EXEC_RETRACTED", key=k, real=p, replay=None,
                              note="철회 이벤트 있음" if k in retracted else "최종 재생에 없음"))
    for r in main_rows:
        if r["key"] in executed_keys:
            continue
        items.append(dict(kind="REPLAY_ONLY", key=r["key"], real=None, replay=r,
                          note=skip.get(r["key"], "집행 기록 없음(미측정)")))

    def _sum(kind, side):
        xs = [it[side] for it in items if it["kind"] == kind and it[side] is not None]
        return sum(float(x["net"] or 0) for x in xs), len(xs)

    tot = {}
    for kind in ("MATCH", "EXEC_RETRACTED", "EXEC_UNKEYED", "REPLAY_ONLY"):
        tot[kind] = {"real": _sum(kind, "real"), "replay": _sum(kind, "replay")}
    real_total = sum(float(p["net"]) for p in positions)
    replay_total = sum(float(r["net"] or 0) for r in main_rows if r.get("net") is not None)
    items.sort(key=lambda it: (it["real"] or {}).get("entry_ts", "")[11:16] or (it["replay"] or {}).get("entry_ts", ""))
    return {"items": items, "totals": tot, "real_total": real_total, "replay_total": replay_total,
            "n_real": len(positions)}


def be_exit_slips(rc: Optional[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """[MW0602 657차 · 신동 V4] 본전청산 실측 슬립 — 사전등록 V4 §3-2 되돌림 조건의 계측.

    대상 = MATCH 중 재생 MAIN 청산 사유가 본전(BE)인 거래. 본전 손절가 = 재생 진입가(규칙가 —
    실집행 손절도 이 값에 걸린다). 슬립 = side × (본전가 − 실청산 평균가) pt, **+ = 불리**.
    실청산가는 그 포지션 청산 레그 가격의 단순 평균(레그별 수량 미기록 — 본전 청산은 보통 1레그).
    None = 대사 원천 없음(미측정) · [] = 본전청산 일치 거래 없음.
    """
    if rc is None:
        return None
    out: List[Dict[str, Any]] = []
    for it in rc.get("items") or []:
        p, r = it.get("real"), it.get("replay")
        if it.get("kind") != "MATCH" or not p or not r:
            continue
        rs = [g[2] for g in (r.get("legs") or []) if g and len(g) > 2]
        if not rs or rs[0] != "BE":
            continue
        px = [float(g[1]) for g in (p.get("legs") or []) if g and g[1]]
        if not px:
            continue
        xp = sum(px) / len(px)
        out.append({"key": it.get("key"), "side": int(r["side"]), "be_px": float(r["entry_px"]),
                    "real_exit_px": xp, "slip_pt": int(r["side"]) * (float(r["entry_px"]) - xp)})
    return out


def entry_slips(rc: Optional[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """[MW0602 673차 후속3] 실거래 진입 슬립 — 「탐지 지연」 계측의 대체.

    대상 = MATCH 전부. 규칙가 = 재생 진입가(**진입봉 종가** — 봉 마감 = 다음 분 :00 에 확정).
    실주문은 그 뒤 수 초에 시장가로 나간다(60초 수급 타이머 위상). 슬립 = side × (실진입 평균가 − 규칙가) pt,
    **+ = 불리**(be_exit_slips 와 같은 부호).
    None = 대사 원천 없음(미측정) · [] = 일치 거래 없음.

    ⚠ 종전 `detect_px`(store) 는 「처음 본 시점의 마지막 완결 봉 종가」라 진입봉 종가와 **구조적으로 같다** —
      19개 일일 리포트 전부 +0 이었다(딥다이브 MW0602-20261029). 실현가능가로 쓰지 말 것.
    """
    if rc is None:
        return None
    out: List[Dict[str, Any]] = []
    for it in rc.get("items") or []:
        p, r = it.get("real"), it.get("replay")
        if it.get("kind") != "MATCH" or not p or not r or not p.get("entry_px") or r.get("entry_px") is None:
            continue
        side = int(r["side"])
        out.append({"key": it.get("key"), "side": side, "rule_px": float(r["entry_px"]),
                    "real_px": float(p["entry_px"]), "qty": int(p.get("qty") or 0),
                    "slip_pt": side * (float(p["entry_px"]) - float(r["entry_px"]))})
    return out


_STOP_REASONS = ("TR", "BE", "SL")
_MANUAL_MARK = ("수동", "manual", "exit_full")


def cadence_phase(day: str) -> Optional[int]:
    """[673차 후속6 · R4] 그날 신동 재생이 가장 자주 돈 초(秒) = 손절 갱신 위상. None = 기록 없음(미측정).

    원천: main `_sd_cadence_note` 가 쓰는 `shindong_cadence.json` {"sec_hist": {초: 횟수}}. 재시도(R2)는 제외돼 있다.
    """
    try:
        from strategy.runtime import trade_principal as TP
        c = TP.read_json(day, "shindong_cadence.json", None)
    except Exception:
        return None
    h = (c or {}).get("sec_hist") if isinstance(c, dict) else None
    if not h:
        return None
    return int(max(h.items(), key=lambda kv: (int(kv[1]), -int(kv[0])))[0])


def cadence_aligned(day: str) -> Optional[bool]:
    """[673차 후속7] 그날 신동 재생이 R1(봉 마감 정렬) 아래 돌았는가. None = 기록 없음(R1 이전 날 포함)."""
    try:
        from strategy.runtime import trade_principal as TP
        c = TP.read_json(day, "shindong_cadence.json", None)
    except Exception:
        return None
    if not isinstance(c, dict) or "align" not in c:
        return None
    return bool(c["align"])


def be_slip_verdict(xs: List[float]) -> Dict[str, Any]:
    """사전등록 V4 §3-2 판정(한 구간). state ∈ 대기 · 재검토 · 유지. 문턱은 spec 단일 출처."""
    from strategy.shindong import spec as S
    n = len(xs)
    m = (math.fsum(xs) / n) if n else None    # fsum — 문턱 경계(0.8×20)가 파이썬 버전 합산 방식에 따라 갈리지 않게
    if n < S.V4_BE_SLIP_MIN_N:
        state = "대기"
    elif m > S.V4_BE_SLIP_REVIEW_PT:
        state = "재검토"
    else:
        state = "유지"
    return {"n": n, "mean": m, "worst": (max(xs) if n else None), "state": state}


def be_slips_by_align(recons) -> Dict[str, List[Dict[str, Any]]]:
    """collect_recons 결과 → {"post": 정렬 후 표본, "pre": 정렬 전 표본}. 표본에 day 를 붙인다."""
    out: Dict[str, List[Dict[str, Any]]] = {"pre": [], "post": []}
    for day, rc in recons:
        seg = "post" if rc.get("aligned") is True else "pre"
        for x in be_exit_slips(rc) or []:
            out[seg].append(dict(x, day=day))
    return out


def exit_slips(rc: Optional[Dict[str, Any]], phase_sec: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
    """[673차 후속6 · R4] 실거래 청산 슬립 — 재생 청산가 대비. + = 불리.

    대상 = MATCH 중 재생·실거래 둘 다 닫힌 거래. **수동 청산은 제외**(집행 품질이 아니라 사람의 결정 — 따로 센다).
    슬립 = side × (재생 청산가 − 실청산 평균가). kind = stop(TR·BE·SL) · target(TP) · time(TIME).
    window(손절 청산만) = 실청산 초 < 그날 갱신 위상이면 "in"(실포지션이 아직 직전 분 손절을 쓰던 구간), 아니면 "out".
    위상 미측정이면 None. 근거: docs/정기점검/매일점검/MW0602-20261029-청산슬립-딥다이브.md.
    None = 대사 원천 없음 · [] = 해당 거래 없음.
    """
    if rc is None:
        return None
    out: List[Dict[str, Any]] = []
    for it in rc.get("items") or []:
        p, r = it.get("real"), it.get("replay")
        if it.get("kind") != "MATCH" or not p or not r:
            continue
        rl = [g for g in (r.get("legs") or []) if g and len(g) > 2 and g[1] is not None]
        pl = [g for g in (p.get("legs") or []) if g and g[1]]
        if not rl or not pl:
            continue
        why = " ".join(str(g[2] or "") for g in pl).lower()
        manual = any(m in why for m in _MANUAL_MARK)
        reason = str(rl[0][2] or "")
        kind = "stop" if reason in _STOP_REASONS else ("target" if reason.startswith("TP") else
                                                         ("time" if reason == "TIME" else "other"))
        xp = sum(float(g[1]) for g in pl) / len(pl)
        side = int(r["side"])
        win = None
        xs = str(p.get("exit_ts") or "")
        if kind == "stop" and phase_sec is not None and len(xs) >= 19:
            win = "in" if int(xs[17:19]) < int(phase_sec) else "out"
        out.append({"key": it.get("key"), "side": side, "reason": reason, "kind": kind,
                    "replay_px": float(rl[0][1]), "real_px": xp, "exit_ts": xs, "manual": manual,
                    "window": win, "qty": int(p.get("qty") or 0),
                    "slip_pt": side * (float(rl[0][1]) - xp)})
    return out


def slip_stats(xs: List[float]) -> Optional[Dict[str, float]]:
    """n · 평균 · 표준편차 · t(평균/표준오차) · 최악(최대 불리). 빈 목록 = None(미측정 — 0 이 아니다)."""
    n = len(xs)
    if not n:
        return None
    m = math.fsum(xs) / n                      # 버전 무관 정확 합(3.12 미만 sum 은 누적 오차)
    sd = (sum((x - m) ** 2 for x in xs) / (n - 1)) ** 0.5 if n > 1 else None
    t = (m / (sd / n ** 0.5)) if (sd and sd > 0) else None
    return {"n": n, "mean": m, "sd": sd, "t": t, "worst": max(xs)}


def stored_main_rows(sd_db: str, day: str, spec_version: Optional[str] = None) -> List[Dict[str, Any]]:
    """shindong.db 에 저장된 그날 MAIN 재생 행 → reconcile() 입력. spec_version 을 주면 그 규격 행만."""
    from strategy.shindong import store
    rows = []
    for t in store.load_trades(sd_db, day, "MAIN"):
        if spec_version is not None and t.get("spec_version") != spec_version:
            continue
        rows.append(dict(key=t["trade_key"], side=int(t["side"]), entry_ts=str(t["entry_ts"])[11:16],
                         entry_px=float(t["entry_px"]), net=t.get("net_krw"),
                         legs=[(t.get("leg1_exit_ts"), t.get("leg1_exit_px"), t.get("leg1_reason")),
                               (t.get("leg2_exit_ts"), t.get("leg2_exit_px"), t.get("leg2_reason"))]))
    return rows


def collect_recons(sd_db: str, trades_db: str, since: str, until: str,
                   spec_version: Optional[str] = None):
    """since~until 각 거래일의 reconcile 결과 → ([(day, rc)], 대사 원천 없는 날 목록)."""
    from strategy.runtime import trade_principal as TP
    out, unmeasured = [], []
    d, end = _dt.date.fromisoformat(since), _dt.date.fromisoformat(until)
    while d <= end:
        day = d.isoformat()
        d += _dt.timedelta(days=1)
        main_rows = stored_main_rows(sd_db, day, spec_version)
        if not main_rows:
            continue
        pos = real_positions(trades_db, day)
        if pos is None:
            unmeasured.append(day)
            continue
        ev = TP.read_jsonl(day, "shindong_exec.jsonl") or events_from_exec_json(
            TP.read_json(day, "shindong_exec.json", {}))
        rc = reconcile(main_rows, pos, ev)
        rc["phase_sec"] = cadence_phase(day)       # [R4] 청산 갱신창 판정용 — None = 미측정
        rc["aligned"] = cadence_aligned(day)       # [673차 후속7] 본전청산 슬립 구간(R1 정렬 전/후)
        out.append((day, rc))
    return out, unmeasured


def events_from_exec_json(d: Any) -> List[Dict[str, Any]]:
    """`shindong_exec.json`(신호별 상태 dict) → reconcile() 이 읽는 이벤트 목록.

    두 갈래의 집행 기록 형식이 다르다:
      · v9-dev(MW0601) — `shindong_exec.jsonl` 사건 로그(ENTER·RETRACTED·SKIP_*·REJECT)가 1차 원천.
      · dev(MW0602)   — 사건 로그가 없고 `shindong_exec.json` 에 {trade_key: {status, side, at, filled,
                        retracted, why}} 만 있다. status ∈ OPEN·CLOSED·NOT_FILLED·SKIP_STALE·REJECT.
    jsonl 이 비었을 때 이 함수로 json 을 같은 모양으로 바꾼다. 미체결(NOT_FILLED)은 진입으로 세지 않는다.
    """
    out: List[Dict[str, Any]] = []
    if not isinstance(d, dict):
        return out
    for k, r in d.items():
        if not isinstance(r, dict):
            continue
        st = str(r.get("status") or "")
        side = r.get("side")
        filled = r.get("filled")
        if st in ("OPEN", "CLOSED") or (not st and filled):
            if filled is False and st != "CLOSED":
                continue
            out.append({"kind": "ENTER", "trade_key": k, "side": side,
                        "entered_at": r.get("entered_at") or r.get("at")})
        elif st == "SKIP_STALE":
            out.append({"kind": "SKIP_STALE", "trade_key": k})
        elif st == "SKIP_HOLDING":
            out.append({"kind": "SKIP_HOLDING", "trade_key": k, "holding": r.get("holding")})
        elif st == "REJECT":
            out.append({"kind": "REJECT", "trade_key": k, "why": r.get("why")})
        if r.get("retracted"):
            out.append({"kind": "RETRACTED", "trade_key": k})
    return out


def cumulative_exec(trades_db: str, start: str, until: str, source: str = SOURCE) -> Optional[Dict[str, Any]]:
    """[C] 실집행 누적 — 채점 시작일부터, 포지션 단위. 참고 행(사전등록 판정 기준 아님)."""
    con = _ro(trades_db)
    if con is None:
        return None
    try:
        rows = con.execute(
            "SELECT substr(exit_ts,1,10), entry_ts, direction, COALESCE(net_pnl_krw, pnl_krw) FROM trades "
            "WHERE entry_source=? AND substr(exit_ts,1,10)>=? AND substr(exit_ts,1,10)<=?",
            (source, start, until)).fetchall()
    finally:
        con.close()
    pos: Dict[tuple, Dict[str, Any]] = {}
    for d, ets, dr, net in rows:
        p = pos.setdefault((str(ets)[:19], dr), {"day": d, "net": 0.0})
        p["net"] += float(net or 0)
    by_day: Dict[str, float] = {}
    for p in pos.values():
        by_day[p["day"]] = by_day.get(p["day"], 0.0) + p["net"]
    n = len(pos)
    return dict(start=start, days=len(by_day), n=n, win=sum(1 for p in pos.values() if p["net"] > 0),
                net=sum(by_day.values()), worst_day=min(by_day.values()) if by_day else None)
