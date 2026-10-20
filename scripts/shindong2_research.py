# -*- coding: utf-8 -*-
"""[MW0602 640차 ④] 신동2 AI 지표 연구 통로 — 레지스트리(I-n) · PIT 검증 러너 · 장착 지표 값.

    python scripts/shindong2_research.py list
    python scripts/shindong2_research.py add --id I4 --title "…" --source "https://…" --hypothesis "…" [--formula "…"] [--inputs a,b]
                                                        # 후보 등록(코드 없이도 된다 — 헤드리스 research 단계가 쓴다. 상태 「후보·미구현」)
    python scripts/shindong2_research.py set --id I1 --status 장착 --why "검증 PASS 2026-11-15"   # 상태 전이는 사람/대화 세션이 명시적으로
    python scripts/shindong2_research.py verify --id I1 --days 60 [--at 10:00] [--perm 200]       # PIT 검증(장후·주말 전용) → 레지스트리에 기록
    python scripts/shindong2_research.py values [--date D] [--upto HH:MM]                          # 장착 지표 값(snapshot 이 부른다)

흐름(④): 리서치(웹·내부) → 후보 등록(출처·가설·공식) → 플러그인 구현(`strategy/shindong2_ai/indicators/i*.py`, 대화 세션) → verify →
         PASS 면 `set --status 장착` → snapshot 「AI 지표」 블록 → AI 전략 S-n 의 축 → 20거래일 뒤 기여 없으면 폐기.

🔴 사전등록 — 검증 문턱은 플러그인 META.prereg 에 고정(기본 min_days 20 · 부호 적중 ≥ 0.55 · 이항 p < 0.05 · 순열 p < 0.05).
   결과를 보고 문턱을 낮추지 않는다(458차 D6). 미달이면 FAIL 이지 「거의 통과」가 아니다.
🔴 장중 금지 — `verify` 는 전수 재생(N 거래일 × 분)이라 `guard_intraday` 가 막는다(456차). `values` 는 하루치라 장중 허용.
🔴 자동 장착 없음 — verify 는 기록만 한다. 상태 전이는 `set` 으로만(절대원칙 §6 과 같은 취지).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import os
import random
import sqlite3
import sys
from typing import Any, Dict, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import shindong2_live as SL  # noqa: E402  (PC · 경로 · _atomic_json)

def _pc_fallback():
    """v9-dev(MW0601) 의 shindong2_live 에는 PC 상수가 없다(파일명이 MW0601 하드코딩) — 호스트명에서 뽑는다."""
    import platform as _pf
    import re as _re
    m = _re.search(r"(MW\d{4})", _pf.node() or "", _re.IGNORECASE)
    return m.group(1).upper() if m else ((_pf.node() or "UNKNOWN")[:32])


PC = os.environ.get("SHINDONG2_PC") or getattr(SL, "PC", None) or _pc_fallback()
LEARN_DIR = os.environ.get("SHINDONG2_LEARN_DIR") or os.path.join(ROOT, "docs", "미륵이고도화3", "신동2", "학습")
REG_JSON = "indicators_%s.json" % PC
REG_MD = "지표_레지스트리_%s.md" % PC
STATUSES = ("후보", "검증", "장착", "폐기")
DEFAULT_PREREG = dict(min_days=20, hit_min=0.55, p_max=0.05)
REG_DB = os.path.join(ROOT, "data", "db", "regular_candles.db")


def _reg_path():
    os.makedirs(LEARN_DIR, exist_ok=True)
    return os.path.join(LEARN_DIR, REG_JSON)


def load_registry() -> List[Dict[str, Any]]:
    p = _reg_path()
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_registry(reg):
    SL._atomic_json(_reg_path(), reg)
    with open(os.path.join(LEARN_DIR, REG_MD), "w", encoding="utf-8") as f:
        f.write(render_registry(reg))


def _find(reg, iid):
    for r in reg:
        if r["id"] == iid:
            return r
    return None


def plugins():
    from strategy.shindong2_ai import indicators as IND
    return IND.discover()


def add(iid, title, source, hypothesis, formula="", inputs=(), status="후보", now=None):
    """후보 등록. 출처 없이는 등록 불가(사용자 규칙). 플러그인이 있으면 META 로 보강한다."""
    if not (source or "").strip():
        raise SystemExit("--source 필수 — 출처 없는 지표는 장착 불가(웹이면 URL, 내부면 '내부: 원천')")
    if status not in STATUSES:
        raise SystemExit("status 는 %s 중 하나" % (STATUSES,))
    reg = load_registry()
    if _find(reg, iid):
        raise SystemExit("이미 있는 지표 %s — set 으로 갱신" % iid)
    now = now or _dt.datetime.now()
    pl = plugins()
    mod = pl.get(iid)
    r = dict(id=iid, title=title, source=source, hypothesis=hypothesis, formula=formula, inputs=sorted(inputs or []),
             status=status, implemented=bool(mod), sign=(mod.META["sign"] if mod else None),
             prereg=(dict(DEFAULT_PREREG, **mod.META.get("prereg", {})) if mod else dict(DEFAULT_PREREG)),
             origin=now.date().isoformat(), verifications=[], mounted_at=None,
             history=[dict(ts=now.isoformat(timespec="seconds"), status=status, why="신설%s" % ("" if mod else " — 플러그인 미구현(후보 메모)"))])
    reg.append(r)
    save_registry(reg)
    return r


def set_status(iid, status=None, note=None, why="", now=None):
    reg = load_registry()
    r = _find(reg, iid)
    if not r:
        raise SystemExit("없는 지표 %s" % iid)
    now = now or _dt.datetime.now()
    if status:
        if status not in STATUSES:
            raise SystemExit("status 는 %s 중 하나" % (STATUSES,))
        if status == "장착":
            if not plugins().get(iid):
                raise SystemExit("플러그인이 없는 지표는 장착할 수 없다 — strategy/shindong2_ai/indicators/ 에 구현부터")
            passed = [v for v in r.get("verifications", []) if v.get("verdict") == "PASS"]
            if not passed:
                raise SystemExit("verify PASS 기록이 없다 — 검증 없이 장착 불가(사전등록)")
            r["mounted_at"] = now.isoformat(timespec="seconds")
        r["status"] = status
        r["history"].append(dict(ts=now.isoformat(timespec="seconds"), status=status, why=why))
    if note is not None:
        r["note"] = note
    r["implemented"] = bool(plugins().get(iid))
    save_registry(reg)
    return r


# ── 통계(의존성 없음) ────────────────────────────────────────────────────
def _rank(xs: List[float]) -> List[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(x: List[float], y: List[float]) -> Optional[float]:
    n = len(x)
    if n < 5:
        return None
    rx, ry = _rank(x), _rank(y)
    mx, my = sum(rx) / n, sum(ry) / n
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx <= 0 or vy <= 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / math.sqrt(vx * vy)


def binom_two_sided(k: int, n: int, p: float = 0.5) -> float:
    """정확 이항 양측 p — 관측 확률 이하인 결과들의 합."""
    if n == 0:
        return 1.0
    # math.comb 는 3.8+ — 테스트는 py37_32 로 돈다(CLAUDE.md 규약). 운영(py310_64)과 같은 값.
    comb = getattr(math, "comb", None) or (lambda a, b: math.factorial(a) // (math.factorial(b) * math.factorial(a - b)))
    pk = [comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    obs = pk[k]
    return min(1.0, sum(v for v in pk if v <= obs + 1e-12))


def evaluate_pairs(vals: List[float], fwd: List[float], sign: str, prereg: Dict[str, Any], perm: int = 200,
                   seed: int = 20261020) -> Dict[str, Any]:
    """부호 적중률 · 스피어만 IC · 순열 널(노이즈 하한선) · 사전등록 판정. 0 값·None 은 제외한다(미측정 ≠ 0)."""
    pairs = [(v, f) for v, f in zip(vals, fwd) if v is not None and f is not None and v != 0]
    n = len(pairs)
    out: Dict[str, Any] = dict(n=n, n_all=len(vals), prereg=prereg, hit=None, hit_rate=None, p_binom=None, ic=None,
                               p_perm=None, noise_95=None, verdict="UNMEASURED", why="")
    if n < prereg["min_days"]:
        out["why"] = "표본 %d < %d" % (n, prereg["min_days"])
        return out
    x = [v if sign == "follow" else -v for v, _ in pairs]
    y = [f for _, f in pairs]
    hit = sum(1 for a, b in zip(x, y) if (a > 0) == (b > 0) and b != 0)
    nz = sum(1 for b in y if b != 0)
    out["hit"], out["hit_rate"] = hit, (round(hit / nz, 3) if nz else None)
    out["p_binom"] = round(binom_two_sided(hit, nz), 4) if nz else None
    ic = spearman(x, y)
    out["ic"] = None if ic is None else round(ic, 3)
    if ic is not None and perm > 0:
        rng = random.Random(seed)
        null = []
        yy = list(y)
        for _ in range(perm):
            rng.shuffle(yy)
            r = spearman(x, yy)
            if r is not None:
                null.append(abs(r))
        if null:
            null.sort()
            out["p_perm"] = round(sum(1 for r in null if r >= abs(ic)) / len(null), 3)
            out["noise_95"] = round(null[min(len(null) - 1, int(0.95 * len(null)))], 3)
    ok = (out["hit_rate"] is not None and out["hit_rate"] >= prereg["hit_min"] and out["p_binom"] is not None
          and out["p_binom"] < prereg["p_max"] and out["p_perm"] is not None and out["p_perm"] < prereg["p_max"] and ic > 0)
    out["verdict"] = "PASS" if ok else "FAIL"
    out["why"] = "적중 %s (p=%s) · IC %s (순열 p=%s, 노이즈95 %s)" % (out["hit_rate"], out["p_binom"], out["ic"], out["p_perm"], out["noise_95"])
    return out


# ── PIT 검증 러너 ─────────────────────────────────────────────────────────
def trading_days(n_days: int, until: Optional[str] = None, db: str = REG_DB) -> List[str]:
    """regular_candles(A056A) 에 봉이 있는 거래일 — 최근 n_days. DB 없으면 빈 목록."""
    if not os.path.exists(db):
        return []
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True, timeout=5.0)
    try:
        q = "SELECT DISTINCT trade_date FROM regular_candles WHERE code='A056A'" + (" AND trade_date<=?" if until else "") + " ORDER BY trade_date DESC LIMIT ?"
        rows = con.execute(q, ((until, n_days) if until else (n_days,))).fetchall()
    finally:
        con.close()
    return sorted(r[0] for r in rows)


def forward_return(day: str, at_hm: str, db: str = REG_DB) -> Optional[float]:
    """at_hm 의 종가 → 15:10 직전 마지막 종가. 미니 A056A 정규봉."""
    if not os.path.exists(db):
        return None
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True, timeout=5.0)
    try:
        a = con.execute("SELECT close FROM regular_candles WHERE code='A056A' AND trade_date=? AND substr(ts,12,5)<=? ORDER BY ts DESC LIMIT 1",
                        (day, at_hm)).fetchone()
        b = con.execute("SELECT close FROM regular_candles WHERE code='A056A' AND trade_date=? AND substr(ts,12,5)<='15:09' ORDER BY ts DESC LIMIT 1",
                        (day,)).fetchone()
    finally:
        con.close()
    if not a or not b:
        return None
    return round(float(b[0]) - float(a[0]), 2)


def guard_intraday(now: Optional[_dt.datetime] = None, force: bool = False):
    now = now or _dt.datetime.now()
    if force:
        return
    if now.weekday() < 5 and "08:50" <= now.strftime("%H:%M") <= "15:40":
        raise SystemExit("장중이다(456차) — verify 는 장후·주말 전용. 정말 필요하면 --force")


def verify(iid: str, days: int = 60, at_hm: str = "10:00", perm: int = 200, until: Optional[str] = None,
           now: Optional[_dt.datetime] = None, force: bool = False, save: bool = True) -> Dict[str, Any]:
    guard_intraday(now, force)
    pl = plugins()
    mod = pl.get(iid)
    if not mod:
        raise SystemExit("플러그인 없음 %s — 구현된 지표: %s · 오류: %s" % (iid, [k for k in pl if k != "__errors__"], pl["__errors__"]))
    reg = load_registry()
    r = _find(reg, iid)
    prereg = dict(DEFAULT_PREREG, **mod.META.get("prereg", {}))
    dl = trading_days(days, until)
    vals, fwd, rows = [], [], []
    for d in dl:
        v = mod.compute(d, at_hm)
        f = forward_return(d, at_hm)
        vals.append(v)
        fwd.append(f)
        rows.append(dict(date=d, value=v, fwd=f))
    res = evaluate_pairs(vals, fwd, mod.META["sign"], prereg, perm=perm)
    rec = dict(ts=(now or _dt.datetime.now()).isoformat(timespec="seconds"), days=days, at=at_hm, perm=perm, first=dl[0] if dl else None,
               last=dl[-1] if dl else None, **{k: res[k] for k in ("n", "n_all", "hit_rate", "p_binom", "ic", "p_perm", "noise_95", "verdict", "why")})
    if save:
        if r is None:                                   # 플러그인은 있는데 레지스트리에 없으면 META 로 등록해 둔다
            r = add(iid, mod.META["title"], mod.META["source"], mod.META["hypothesis"], inputs=mod.META.get("inputs", ()), now=now)
            reg = load_registry()
            r = _find(reg, iid)
        r.setdefault("verifications", []).append(rec)
        r["implemented"] = True
        if r["status"] == "후보":
            r["status"] = "검증"
            r["history"].append(dict(ts=rec["ts"], status="검증", why="verify 실행 — %s" % res["verdict"]))
        save_registry(reg)
    return dict(id=iid, rows=rows, result=res, record=rec)


def mounted_values(day: str, upto_hm: Optional[str]) -> List[Dict[str, Any]]:
    """장착 지표의 값 — snapshot 이 부른다. 레지스트리에 「장착」이 없으면 빈 목록(블록 생략)."""
    from strategy.shindong2_ai import indicators as IND
    reg = [r for r in load_registry() if r["status"] == "장착"]
    if not reg:
        return []
    pl = plugins()
    out = []
    for r in reg:
        mod = pl.get(r["id"])
        if not mod:
            out.append(dict(id=r["id"], title=r["title"], value=None, lean=None, why="플러그인 없음(장착 상태인데 코드 없음 — 레지스트리 오염)"))
            continue
        v = IND.compute_one(mod, day, upto_hm)
        out.append(dict(id=r["id"], title=r["title"], unit=mod.META.get("unit"), hypothesis=r["hypothesis"], **v))
    return out


def values_lines(vals: List[Dict[str, Any]]) -> List[str]:
    if not vals:
        return []
    L = ["### AI 지표(장착) — 상대와 다른 입력에서 다른 결론을 낼 수 있는가"]
    for v in vals:
        L.append("  · %s %s: %s%s%s" % (v["id"], v["title"], "미측정" if v["value"] is None else v["value"],
                                       (" " + v["unit"]) if v.get("unit") and v["value"] is not None else "",
                                       (" → 가설 " + v["lean"]) if v.get("lean") else ((" — " + v["why"]) if v.get("why") else "")))
    return L


def render_registry(reg) -> str:
    L = ["# 신동2 AI 지표 레지스트리 (%s)" % PC, "",
         "> 값의 단일 출처는 같은 폴더 `%s` — 이 파일은 렌더다." % REG_JSON,
         "> 상태: 후보(출처·가설만) → 검증(verify 기록 있음) → 장착(PASS 뒤 `set --status 장착`) / 폐기. **자동 장착 없음.**",
         "> 검증 = `scripts/shindong2_research.py verify` — 부호 적중(이항 p) · 스피어만 IC · 순열 널 200회(노이즈 하한선). 문턱은 플러그인 META.prereg(사전등록).",
         "", "| ID | 상태 | 지표 | 가설 | 출처 | 구현 | 최근 검증 | 비고 |", "|---|---|---|---|---|---|---|---|"]
    for r in reg:
        v = (r.get("verifications") or [None])[-1]
        vs = "—" if not v else "%s %s (n=%s · %s)" % (v["ts"][:10], v["verdict"], v["n"], v["why"])
        L.append("| %s | %s | **%s** | %s | %s | %s | %s | %s |" % (
            r["id"], r["status"], r["title"], r["hypothesis"], r["source"], "✅" if r.get("implemented") else "미구현", vs, r.get("note") or ""))
    L += ["", "## 이력", ""]
    for r in reg:
        hist = " → ".join("%s %s%s" % (h["ts"][:10], h["status"], ("(%s)" % h["why"]) if h.get("why") else "") for h in r["history"])
        L.append("- **%s** %s" % (r["id"], hist))
        for v in r.get("verifications") or []:
            L.append("  - 검증 %s: %d일(%s~%s) at %s · %s · n=%d/%d" % (v["ts"][:16], v["days"], v["first"], v["last"], v["at"], v["why"], v["n"], v["n_all"]))
    return "\n".join(L) + "\n"


def registry_text() -> str:
    reg = load_registry()
    pl = plugins()
    L = ["구현된 플러그인: %s" % ", ".join(k for k in pl if k != "__errors__") or "없음"]
    if pl["__errors__"]:
        L.append("⚠ 계약 위반 플러그인: %s" % pl["__errors__"])
    for r in reg:
        v = (r.get("verifications") or [None])[-1]
        L.append("- %s [%s%s] %s — %s · 출처 %s%s" % (r["id"], r["status"], "" if r.get("implemented") else "·미구현", r["title"], r["hypothesis"],
                                                     r["source"], (" · 최근 검증 %s %s" % (v["verdict"], v["why"])) if v else ""))
    return "\n".join(L) if reg or pl else "지표 없음"


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    a_ = sub.add_parser("add")
    a_.add_argument("--id", required=True)
    a_.add_argument("--title", required=True)
    a_.add_argument("--source", required=True)
    a_.add_argument("--hypothesis", required=True)
    a_.add_argument("--formula", default="")
    a_.add_argument("--inputs", default="")
    s_ = sub.add_parser("set")
    s_.add_argument("--id", required=True)
    s_.add_argument("--status")
    s_.add_argument("--note")
    s_.add_argument("--why", default="")
    v_ = sub.add_parser("verify")
    v_.add_argument("--id", required=True)
    v_.add_argument("--days", type=int, default=60)
    v_.add_argument("--at", default="10:00")
    v_.add_argument("--perm", type=int, default=200)
    v_.add_argument("--until")
    v_.add_argument("--force", action="store_true")
    m_ = sub.add_parser("values")
    m_.add_argument("--date", default=_dt.date.today().isoformat())
    m_.add_argument("--upto")
    a = ap.parse_args(argv)
    if a.cmd == "list":
        print(registry_text())
    elif a.cmd == "add":
        r = add(a.id, a.title, a.source, a.hypothesis, formula=a.formula, inputs=[x.strip() for x in a.inputs.split(",") if x.strip()])
        print("지표 등록 %s [%s%s] %s" % (r["id"], r["status"], "" if r["implemented"] else "·미구현", r["title"]))
    elif a.cmd == "set":
        r = set_status(a.id, status=a.status, note=a.note, why=a.why)
        print("지표 갱신 %s [%s] %s" % (r["id"], r["status"], r["title"]))
    elif a.cmd == "verify":
        out = verify(a.id, days=a.days, at_hm=a.at, perm=a.perm, until=a.until, force=a.force)
        res = out["result"]
        print("검증 %s — %s일 at %s · n=%d · **%s** · %s" % (a.id, a.days, a.at, res["n"], res["verdict"], res["why"]))
        return 0 if res["verdict"] == "PASS" else 2
    elif a.cmd == "values":
        print("\n".join(values_lines(mounted_values(a.date, a.upto))) or "장착 지표 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
