# -*- coding: utf-8 -*-
"""[MW0601 708차] 신동 철회 섀도 — 「철회되면 청산하고 새 신호를 받는다」를 **계측만** 한다.

왜 필요한가
-----------
신동 실집행은 진입한 신호가 재생에서 철회(RETRACTED)돼도 손절·목표로 끝까지 관리한다
(`live_legs.py` — 철회는 청산 사유가 아니다). 그동안 새 MAIN 신호는 「보유 중」으로 못 친다.
2026-10-22 실측: 재생 MAIN +259.9만 vs 실거래 +112.7만. 차이의 본체가 이 연쇄였다 —
철회 신호 포지션을 들고 있는 동안 09:37 매수(+95.1만)·13:51 매도(+54.1만)를 놓쳤다.

규칙 후보 두 가지를 나란히 잰다(사용자 지시 2026-10-23 — 본전 이상 규칙이 본안):
  BE   철회 시점 미실현 ≥ `be_pts`(기본 0 = 본전)일 때만 청산 → 새 신호 수용
  ALL  철회되면 무조건 청산 → 새 신호 수용(비교용 상한)

섀도 손익(창 단위)
------------------
  창 = [철회된 포지션 진입, E). E = 실거래 그 포지션 청산 시각에서 시작해, 섀도가 받은 재생
       거래가 그 뒤까지 이어지면 그 청산 시각까지 늘린다.
  실거래 = 창 안에 진입한 신동 실거래 포지션 순손익 합(trades.db).
  섀도   = 철회 시각 가격으로 청산한 손익(1틱 슬리피지 + 그 포지션 실제 수수료)
           + 철회 뒤 받을 수 있었던 재생 MAIN 거래 순손익(한 번에 하나, 탐지 허용 `max_age_min`).
  Δ = 섀도 − 실거래. 양수면 그 규칙이 이 창에서 더 벌었다.

⚠ 근사다 — 받은 신호의 손익은 **재생 값**(신호분 가격 · CYBOS 요율)이지 체결가가 아니다.
  CREON 실거래 요율이 CYBOS 의 1/5 이라 재생 쪽 비용이 과대하다(섀도에 불리한 방향).
⚠ 창 밖 연쇄(섀도가 E 뒤에 다른 신호를 놓치거나 더 받는 효과)는 세지 않는다.
⚠ 판정·주문에 쓰지 않는다. 표본이 쌓인 뒤 규격 개정(사전등록 §6) 여부를 사람이 정한다.
"""
import datetime as _dt
import io
import os
import re
import sqlite3
from typing import Any, Dict, List, Optional

from strategy.shindong import spec as S
from strategy.shindong.exec_recon import MATCH_TOL_SEC, _ts

#: 철회 시각 가격으로 청산할 때 붙이는 슬리피지(pt) — 재생의 손절·시간 청산과 같은 1틱.
EXIT_SLIP_PTS = S.SLIP_TICK


def snapshot(side: int, entry_px: Optional[float], price: Optional[float], qty: int,
             be_pts: float = 0.0) -> Dict[str, Any]:
    """철회 순간의 섀도 판단 — 라이브 이벤트 `RETRACT_SHADOW` 본문.

    가격·진입가가 없으면 `measured=False` · `decision=None` 이다(0 으로 채우지 않는다 — 원칙 ②).
    """
    out = {"side": int(side or 0), "entry_px": entry_px, "price": price, "qty": int(qty or 0),
           "be_pts": float(be_pts), "measured": False, "unreal_pts": None, "decision": None}
    if not side or not entry_px or not price:
        return out
    u = round((float(price) - float(entry_px)) * side, 2)
    out.update(measured=True, unreal_pts=u, decision="EXIT" if u >= be_pts else "HOLD")
    return out


_LOG_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) .*\[Shindong\] (\S+) (매수|매도) RETRACTED "
                     r"진입 [\d.]+\((\d{2}:\d{2})\) \| 철회 전 상태 (\w+) · 현재가 ([\d.]+)")


def log_prices(trade_date: str, log_dir: str) -> Dict[str, Dict[str, Any]]:
    """소급용 — SYSTEM 로그의 `[Shindong] … RETRACTED … 현재가 P` 줄에서 철회 시각·가격을 읽는다.

    708차 이전 날짜에는 `RETRACT_SHADOW` 이벤트가 없다. 그 가격은 재생의 **분봉 종가**라
    라이브 틱과 다를 수 있다(src="log" 로 표시한다). 파일이 없으면 빈 dict.
    """
    p = os.path.join(log_dir, "%s_SYSTEM.log" % trade_date.replace("-", ""))
    out: Dict[str, Dict[str, Any]] = {}
    if not os.path.exists(p):
        return out
    with io.open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            if "RETRACTED" not in line or "[Shindong]" not in line:
                continue
            m = _LOG_RE.search(line)
            if not m:
                continue
            ts, rule, sw, hm, _st, px = m.groups()
            key = "%s|%s|%s" % (rule, hm, "+1" if sw == "매수" else "-1")
            out.setdefault(key, {"ts": ts, "price": float(px)})
    return out


def position_costs(trades_db: str, trade_date: str, source: str = "SHINDONG") -> Dict[tuple, float]:
    """(entry_ts, direction) → 그 포지션 실제 수수료 합. 섀도 청산 비용으로 쓴다(같은 수량 왕복)."""
    if not trades_db or not os.path.exists(trades_db):
        return {}
    con = sqlite3.connect("file:%s?mode=ro" % trades_db.replace("\\", "/"), uri=True)
    try:
        rows = con.execute(
            "SELECT entry_ts, direction, COALESCE(SUM(commission_krw),0) FROM trades "
            "WHERE entry_source=? AND substr(exit_ts,1,10)=? GROUP BY entry_ts, direction",
            (source, trade_date)).fetchall()
    finally:
        con.close()
    return {(str(e)[:19], d): float(c or 0) for e, d, c in rows}


def _at(day: str, hm: Optional[str]) -> Optional[_dt.datetime]:
    if not hm:
        return None
    hm = str(hm)
    return _ts(hm if len(hm) > 8 else "%s %s:00" % (day, hm[:5]))


def _chain(day: str, replay: List[Dict[str, Any]], t: _dt.datetime, end: _dt.datetime,
           max_age_min: float) -> (List[Dict[str, Any]], _dt.datetime):
    """철회 시각 t 부터 받을 수 있었던 재생 거래 — 한 번에 하나, 탐지 허용 안의 것만."""
    taken: List[Dict[str, Any]] = []
    free_at, e = t, end
    for r in sorted(replay, key=lambda r: str(r["entry_ts"])):
        if r.get("net") is None:
            continue
        ent, ext = _at(day, r["entry_ts"]), _at(day, r.get("exit_ts"))
        if ent is None or ext is None:
            continue
        if ent >= e:
            break
        ready = ent + _dt.timedelta(minutes=1)          # 진입봉이 끝나야 신호가 보인다
        deadline = ready + _dt.timedelta(minutes=max_age_min)
        go = max(ready, free_at)
        if go > deadline:
            continue                                    # 철회 전에 지나간 신호 · 보유 중 지나간 신호
        taken.append(r)
        free_at = ext
        if ext > e:
            e = ext
    return taken, e


def evaluate(trade_date: str, replay: List[Dict[str, Any]], positions: Optional[List[Dict[str, Any]]],
             events: List[Dict[str, Any]], logp: Optional[Dict[str, Dict[str, Any]]] = None,
             costs: Optional[Dict[tuple, float]] = None, max_age_min: float = 2.0,
             be_pts: float = 0.0) -> Optional[Dict[str, Any]]:
    """그날 철회된 **보유 포지션**마다 BE·ALL 섀도 Δ 를 낸다. positions None = 미측정.

    replay   : 재생 MAIN 거래 — key · entry_ts(HH:MM 또는 전체) · exit_ts · net
    positions: exec_recon.real_positions()
    events   : shindong_exec.jsonl (ENTER · RETRACTED · RETRACT_SHADOW)
    """
    if positions is None:
        return None
    logp, costs = logp or {}, costs or {}
    enters = {e["trade_key"]: e for e in events if e.get("kind") == "ENTER" and e.get("trade_key")}
    shadows = {e["trade_key"]: e for e in events if e.get("kind") == "RETRACT_SHADOW" and e.get("trade_key")}
    retracted = [e for e in events if e.get("kind") == "RETRACTED" and e.get("trade_key")]
    items: List[Dict[str, Any]] = []
    for ev in retracted:
        k = ev["trade_key"]
        it: Dict[str, Any] = {"key": k, "t": str(ev.get("ts") or "").replace("T", " ")[:19]}
        en = enters.get(k)
        pos = None
        if en is not None:
            et = _ts(en.get("entered_at") or en.get("ts"))
            side = int(en.get("side") or 0)
            for p in positions:
                pt = _ts(p["entry_ts"])
                if pt and et and p["side"] == side and abs((pt - et).total_seconds()) <= MATCH_TOL_SEC:
                    pos = p
                    break
        if pos is None:
            it.update(status="UNMATCHED", why="실거래 포지션과 못 짝지었다")
            items.append(it)
            continue
        sh = shadows.get(k)
        if sh is not None and sh.get("measured"):
            price, src = float(sh["price"]), "live"
        elif k in logp:
            price, src = float(logp[k]["price"]), "log"
        else:
            it.update(status="UNMEASURED", why="철회 시각 가격 없음", real=pos)
            items.append(it)
            continue
        t = _ts(it["t"]) or _ts(logp.get(k, {}).get("ts"))
        x = _ts(pos["exit_ts"])
        if t is None or x is None or t >= x:
            it.update(status="NOT_HELD", why="철회 시각에 이미 청산돼 있었다", real=pos)
            items.append(it)
            continue
        qty = int(pos["qty"] if pos.get("qty") else 0)
        # 레그 분할 포지션은 qty 가 레그 합이다 — 철회 시점 잔량은 1차 청산 여부에 따른다
        legs_before = [g for g in pos.get("legs", []) if _at(trade_date, g[0]) and _at(trade_date, g[0]) <= t]
        open_qty = max(1, qty - len(legs_before)) if legs_before else qty
        u = round((price - pos["entry_px"]) * pos["side"], 2)
        cost = costs.get((pos["entry_ts"], pos["direction"]), 0.0)
        exit_net = (u - EXIT_SLIP_PTS) * open_qty * S.PT_VALUE_KRW - cost
        realized_before = 0.0
        if legs_before:
            # 1차 레그는 이미 실현 — 실거래와 같은 값을 섀도에도 그대로 둔다(레그별 원화가 없어 pt 로 환산)
            realized_before = sum((g[1] - pos["entry_px"]) * pos["side"] for g in legs_before) * S.PT_VALUE_KRW
        taken, e = _chain(trade_date, replay, t, x, max_age_min)
        win_real = [p for p in positions
                    if pos["entry_ts"] <= p["entry_ts"] and _ts(p["entry_ts"]) < e]
        real_net = sum(float(p["net"]) for p in win_real)
        shadow_all = exit_net + realized_before + sum(float(r["net"]) for r in taken)
        exit_be = u >= be_pts
        it.update(status="OK", src=src, price=price, entry_px=pos["entry_px"], side=pos["side"],
                  qty=open_qty, unreal_pts=u, decision="EXIT" if exit_be else "HOLD", real=pos,
                  window_end=e.strftime("%H:%M"), real_net=real_net, n_real=len(win_real),
                  taken=[(r["key"], r["net"]) for r in taken], exit_net=exit_net + realized_before,
                  shadow_all=shadow_all, delta_all=shadow_all - real_net,
                  delta_be=(shadow_all - real_net) if exit_be else 0.0)
        items.append(it)
    ok = [i for i in items if i["status"] == "OK"]
    return {"items": items, "n": len(ok), "n_be_exit": sum(1 for i in ok if i["decision"] == "EXIT"),
            "delta_be": sum(i["delta_be"] for i in ok), "delta_all": sum(i["delta_all"] for i in ok),
            "n_unmeasured": sum(1 for i in items if i["status"] != "OK"), "be_pts": be_pts,
            "max_age_min": max_age_min}


def replay_from_db(sd_db: str, trade_date: str, variant: str = "MAIN") -> Optional[List[Dict[str, Any]]]:
    """shindong.db 의 그날 재생 거래(청산 완료) → evaluate() 의 replay 모양. DB 없음 = None."""
    if not sd_db or not os.path.exists(sd_db):
        return None
    con = sqlite3.connect("file:%s?mode=ro" % sd_db.replace("\\", "/"), uri=True)
    try:
        rows = con.execute(
            "SELECT trade_key, entry_ts, leg1_exit_ts, leg2_exit_ts, net_krw FROM shindong_trades "
            "WHERE variant=? AND trade_date=? AND status='CLOSED' ORDER BY entry_ts",
            (variant, trade_date)).fetchall()
    finally:
        con.close()
    out = []
    for k, ent, x1, x2, net in rows:
        ext = max([str(v) for v in (x1, x2) if v] or [None]) if (x1 or x2) else None
        out.append({"key": k, "entry_ts": str(ent)[11:16], "exit_ts": str(ext)[11:16] if ext else None,
                    "net": float(net) if net is not None else None})
    return out


def _man(x: float) -> str:
    return "%+.1f만" % (x / 10000.0)


def section(rs: Optional[Dict[str, Any]]) -> List[str]:
    """일일 리포트 §2-2 본문."""
    if rs is None:
        return ["- 원천 없음(trades_db 미지정·DB 없음) — 실거래 0 이 아니라 **미측정**이다."]
    if not rs["items"]:
        return ["- 오늘 보유 중 철회 0건 — 섀도 대상 없음."]
    out = ["| 신호 | 철회 | 가격(원천) | 미실현 | BE 판단 | 섀도가 받은 재생 | 창 | 실거래 | 섀도(ALL) | Δ ALL | Δ BE |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for it in rs["items"]:
        key = "`%s`" % it["key"].replace("|", "\\|")
        if it["status"] != "OK":
            out.append("| %s | %s | - | - | - | - | - | - | - | - | %s |" % (key, it["t"][11:16], it["why"]))
            continue
        tk = ", ".join("%s %s" % (k.split("|")[1] + ("↑" if k.endswith("+1") else "↓"), _man(n))
                       for k, n in it["taken"]) or "없음"
        out.append("| %s | %s | %.2f(%s) | %+.2fpt | %s | %s | ~%s | %s (%d) | %s | **%s** | **%s** |" % (
            key, it["t"][11:16], it["price"], it["src"], it["unreal_pts"],
            "청산" if it["decision"] == "EXIT" else "보유", tk, it["window_end"],
            _man(it["real_net"]), it["n_real"], _man(it["shadow_all"]), _man(it["delta_all"]),
            _man(it["delta_be"])))
    out.append("")
    out.append("- 합계 — 측정 %d건 · BE 청산 %d건 · **Δ BE %s · Δ ALL %s**%s" % (
        rs["n"], rs["n_be_exit"], _man(rs["delta_be"]), _man(rs["delta_all"]),
        "" if not rs["n_unmeasured"] else " · 미측정 %d건" % rs["n_unmeasured"]))
    out.append("- BE = 미실현 ≥ %+.2fpt 일 때만 청산(본안) · ALL = 무조건 청산(비교 상한). 받은 재생 손익은 재생 값"
               "(CYBOS 요율 — CREON 실비용보다 크다) · 창 밖 연쇄 미반영. **섀도 — 주문·판정 무관.**" % rs["be_pts"])
    return out
