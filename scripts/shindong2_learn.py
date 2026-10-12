# -*- coding: utf-8 -*-
"""[MW0601 672차] 신동2 학습 사이클 — 예측 평가 · 피드백 로그 · 레슨런 레지스트리 · 워크포워드 추이.

`shindong2_live.py` 의 하위명령(evaluate · feedback · lesson · trend · brief)이 이 모듈을 부른다.
사이클: 예측 → 실행 → 평가·반성 → 레슨런 기록 → (레슨 반영) 개선 예측 → … 을 **기록으로** 돌린다.

    evaluate  그날의 계획(전날 장후 익일계획 · 당일 장전계획, 각각 live/legacy 변형)을 1분봉에 **단독**으로 대 본다.
              방향 적중 · 체결 · 손익 · MFE/MAE · 포착률(손익 ÷ 당일 고저폭) · 진입품질 · 목표/손절 여유.
    feedback  평가 표 + Claude 의 평가·반성(잘한 점 / 잘못한 점 / 개선점 / 레슨)을 그날 피드백 문서에 남기고,
              적용·적중·실패 레슨의 집계를 갱신한다.
    lesson    레슨런 레지스트리(후보 → 적용중 → 검증 / 폐기 / 딥다이브). 값의 단일 출처 = lessons.json.
    trend     워크포워드 추이 — 날짜별 행 + 최근 5/10/20일 창. 「개선(live) − 기존(legacy)」 이 0 이하로 머물면 🔴 딥다이브.
    brief     장전 브리핑 — 활성 레슨 · 전일 피드백 · 추이 판정 한 화면(예약작업이 한 번에 읽는다).

저장
    data/shindong2_live/YYYYMMDD/eval.json · feedback.jsonl · feedback.json   (런타임 — gitignore)
    data/shindong2_live/trend.json
    docs/미륵이고도화3/신동2/학습/피드백_MW0601-YYYYMMDD.md       (커밋 대상 — 그날 반성)
    docs/미륵이고도화3/신동2/학습/lessons.json · 레슨런_레지스트리.md (커밋 대상 — 레슨 단일 출처 + 렌더)
    docs/미륵이고도화3/신동2/학습/추이_MW0601.md                  (커밋 대상 — 파생 뷰, 매번 다시 쓴다)

🔴 미래 참조 차단은 live.py 와 같다 — 평가는 기록 시각 이후 봉만 쓰고, 기록은 벽시계다.
🔴 「미측정 ≠ 0」(계측 4원칙 ②) — legacy 섀도가 없는 날의 개선폭은 None 이지 0 이 아니다.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import shindong2_live as SL  # noqa: E402

ROOT = SL.ROOT
LEARN_DIR = os.environ.get("SHINDONG2_LEARN_DIR") or os.path.join(ROOT, "docs", "미륵이고도화3", "신동2", "학습")
LESSONS_JSON = "lessons.json"
DIR_DEADBAND = 2.0          # pt — |종가 − 시가| 가 이 안이면 「보합」
STATUSES = ("후보", "적용중", "검증", "폐기", "딥다이브")
ACTIVE = ("적용중", "검증")
VARIANTS = ("live", "legacy")   # live = 개선방식(실제 채점) · legacy = 기존방식(섀도 — 개선폭 측정용)
WINDOWS = (5, 10, 20)
PROMOTE_MIN_APPLIED = 3     # 후보 → 승격 검토를 알리는 적용 횟수


def _learn_dir():
    os.makedirs(LEARN_DIR, exist_ok=True)
    return LEARN_DIR


def _hm(t):
    return SL._hm(t)


def _r2(x):
    return None if x is None else round(x, 2)


# ── 단일 계획 시뮬레이션 ──────────────────────────────────────────────────
def ohlc(bars):
    if not bars:
        return None
    hi, lo = max(c[2] for c in bars), min(c[3] for c in bars)
    return dict(open=_r2(bars[0][1]), high=_r2(hi), low=_r2(lo), close=_r2(bars[-1][4]), range=_r2(hi - lo), last_bar=bars[-1][0])


def actual_direction(o, c, dead=DIR_DEADBAND):
    d = c - o
    return "매수" if d >= dead else "매도" if d <= -dead else "보합"


def dir_hit(pred, actual):
    """관망은 방향을 내지 않은 것 — 적중률 분모에서 뺀다(None). 보합일에는 매수·매도 모두 실패."""
    if pred not in ("매수", "매도"):
        return None
    return pred == actual


def effective_time(rec, day):
    ts = _dt.datetime.fromisoformat(rec["ts"])
    if ts.date().isoformat() < day or ts.strftime("%H:%M") < "08:45":
        return "08:45"
    return SL._fmt(_hm(ts.strftime("%H:%M")) + 1)


def simulate_plan(bars, plan, eff="08:45", live=False):
    """계획 하나를 그날 봉에 단독으로 대 본다(다른 기록 무시). 규약은 simulate_ai 와 같다 —
    효력은 eff 봉부터, 지정가는 봉 고저 포함 시 체결, 같은 봉 손절 우선, 15:00 이후 미체결 소멸, 15:10 강제청산."""
    sgn = 1 if plan.get("dir") == "매수" else -1 if plan.get("dir") == "매도" else 0
    if sgn == 0 or plan.get("action") == "stand":
        return dict(kind="관망", filled=False, pnl=0.0)
    entry, stop, target = plan.get("entry"), plan.get("stop"), plan.get("target")
    out = dict(kind="계획", side=plan.get("dir"), entry=entry, stop=stop, target=target, filled=False, pnl=0.0,
               mfe=None, mae=None, entry_t=None, fill=None, how=None, exit_t=None, exit_px=None, why=None, open=False)
    pos = None
    fbars = [c for c in bars if _hm(c[0]) < _hm(SL.FORCE_EXIT)]
    for c in fbars:
        t = c[0]
        if _hm(t) < _hm(eff):
            continue
        if pos is None:
            if _hm(t) > _hm(SL.PLAN_EXPIRE):
                break
            if entry is None:
                pos = dict(fill=c[1], how="시장가")
            elif c[3] <= entry <= c[2]:
                pos = dict(fill=entry, how="지정가")
            else:
                continue
            out.update(filled=True, entry_t=t, fill=_r2(pos["fill"]), how=pos["how"], mfe=0.0, mae=0.0)
        fill = pos["fill"]
        fav = (c[2] - fill) if sgn > 0 else (fill - c[3])
        adv = (fill - c[3]) if sgn > 0 else (c[2] - fill)
        out["mfe"] = max(out["mfe"], fav)
        out["mae"] = max(out["mae"], adv)
        hs = stop is not None and ((c[3] <= stop) if sgn > 0 else (c[2] >= stop))
        ht = target is not None and ((c[2] >= target) if sgn > 0 else (c[3] <= target))
        if hs or ht:
            px, why = (stop, "손절") if hs else (target, "목표 청산")
            out.update(exit_t=t, exit_px=px, why=why, pnl=_r2((px - fill) * sgn))
            pos = None
            break
    if pos is not None:
        px = fbars[-1][4]
        if live and fbars and _hm(fbars[-1][0]) < _hm(SL.FORCE_EXIT) - 1:
            out.update(open=True, why="보유 중(평가)", pnl=_r2((px - pos["fill"]) * sgn))
        else:
            out.update(exit_t=fbars[-1][0], exit_px=_r2(px), why="15:10 강제청산", pnl=_r2((px - pos["fill"]) * sgn))
    out["mfe"], out["mae"] = _r2(out["mfe"]), _r2(out["mae"])
    return out


def plan_quality(sim, oh):
    """타점 품질 — 「최고의 진입·청산 타점」 목표를 수치로 둔다.
    capture   = 손익 ÷ 당일 고저폭 (1.0 이면 그날 전 구간을 먹은 것)
    entry_q   = 1 − (진입가와 그 방향 최악 극단의 거리 ÷ 고저폭)  (매도면 고점에 가까울수록 1)
    target_margin = 매도: 목표 − 저가 / 매수: 고가 − 목표  (≥0 이면 그날 도달 가능했던 목표, <0 은 미도달 거리)
    stop_margin   = 매도: 손절 − 고가 / 매수: 저가 − 손절  (≥0 이면 그날 어느 때도 안 닿는 손절 — 당일 전체 기준)
    entry_miss    = 미체결일 때 진입가와 그날 극단의 거리(매도: 진입 − 고가, 매수: 저가 − 진입)."""
    if sim.get("kind") != "계획" or not oh or not oh.get("range"):
        return {}
    rng = oh["range"]
    short = sim["side"] == "매도"
    q = {}
    if sim.get("filled"):
        q["capture"] = _r2(sim["pnl"] / rng)
        q["entry_q"] = _r2(1 - ((oh["high"] - sim["fill"]) if short else (sim["fill"] - oh["low"])) / rng)
    elif sim.get("entry") is not None:
        q["entry_miss"] = _r2((sim["entry"] - oh["high"]) if short else (oh["low"] - sim["entry"]))
    if sim.get("target") is not None:
        q["target_margin"] = _r2((sim["target"] - oh["low"]) if short else (oh["high"] - sim["target"]))
    if sim.get("stop") is not None:
        q["stop_margin"] = _r2((sim["stop"] - oh["high"]) if short else (oh["low"] - sim["stop"]))
    if sim.get("entry") is not None and sim.get("stop") is not None:
        risk = abs(sim["entry"] - sim["stop"])
        q["risk"] = _r2(risk)
        if sim.get("target") is not None and risk > 0:
            q["rr"] = _r2(abs(sim["target"] - sim["entry"]) / risk)
    return q


# ── 하루 평가 ──────────────────────────────────────────────────────────────
def _last_per_variant(recs):
    out = {}
    for r in recs:
        out[r.get("variant") or "live"] = r
    return out


def evaluate_day(day, now=None, bars=None, st=None, log=None, save=True):
    """그날 계획을 평가한다. bars/st/log 를 주면 DB 를 읽지 않는다(시험용)."""
    live = False
    if bars is None:
        st, d = SL.build_state(day, now)
        if st.get("empty"):
            return dict(date=day, empty=True)
        live = bool(st.get("live"))
        bars = d["candles"][:-1] if live else d["candles"]
    if log is None:
        log = SL.load_ai_log(day)
    oh = ohlc(bars)
    actual = actual_direction(oh["open"], oh["close"])
    prev_close = ((st or {}).get("prev") or {}).get("close")

    def ev(rec):
        sim = simulate_plan(bars, rec, eff=effective_time(rec, day), live=live)
        return dict(id=rec.get("id"), ts=rec.get("ts"), variant=rec.get("variant") or "live", action=rec.get("action"),
                    dir=rec.get("dir"), entry=rec.get("entry"), stop=rec.get("stop"), target=rec.get("target"),
                    lessons=rec.get("lessons") or [], dir_hit=dir_hit(rec.get("dir"), actual), sim=sim, q=plan_quality(sim, oh))
    on = _last_per_variant([r for r in log if r.get("phase") == "overnight" and r.get("action") in ("plan", "stand")])
    pm = _last_per_variant([r for r in log if r.get("phase") == "premarket" and r.get("action") in ("plan", "stand")
                            and str(r.get("ts", ""))[11:16] < "09:00"])
    ai = SL.simulate_ai(day, bars, log, live=live)
    applied = sorted({l for r in log for l in (r.get("lessons") or []) if (r.get("variant") or "live") == "live"})
    out = dict(date=day, live=live, evaluated_at=(now or _dt.datetime.now()).isoformat(timespec="seconds"),
               ohlc=oh, prev_close=prev_close, actual_dir=actual,
               overnight={k: ev(v) for k, v in on.items()}, premarket={k: ev(v) for k, v in pm.items()},
               live_ai=dict(pnl=ai["pnl"], n=len(ai["trades"]),
                            trades=[dict(entry_t=t["entry_t"], side=t["side"], fill=t["fill"], exit_t=t.get("exit_t"),
                                         why=t.get("why"), pnl=t["pnl"]) for t in ai["trades"]]),
               rules=((st or {}).get("sd2") or {}).get("summary"), lessons_applied=applied)
    if save:
        SL._atomic_json(os.path.join(SL.day_dir(day), "eval.json"), out)
    return out


def _fmtp(x, d=2):
    return "—" if x is None else ("%+.*f" % (d, x))


def _fmtq(x):
    return "—" if x is None else "%.2f" % x


def _plan_row(label, e):
    s, q = e["sim"], e.get("q") or {}
    hit = e["dir_hit"]
    hit_s = "—(관망)" if hit is None else ("✅" if hit else "❌")
    if s.get("kind") == "관망":
        return "| %s | 관망 | %s | — | — | — | — | — | — | — | — |" % (label, hit_s)
    if s.get("filled"):
        fill = "%s %s @%.2f" % (s["entry_t"], s["how"], s["fill"])
        res = "%s %s" % (s.get("exit_t") or "", s.get("why") or "")
    else:
        fill = "미체결" + ("(극단까지 %.2f)" % q["entry_miss"] if q.get("entry_miss") is not None else "")
        res = "—"
    return "| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s/%s | %s · 진입품질 %s |" % (
        label, e["dir"], hit_s, e["entry"] if e["entry"] is not None else "시장가", e["stop"], e["target"], fill, res.strip(),
        _fmtp(s["pnl"]) if s.get("filled") else "0.00",
        _fmtq(s.get("mfe")), _fmtq(s.get("mae")),
        ("포착률 " + _fmtq(q["capture"])) if q.get("capture") is not None else "포착률 —",
        _fmtq(q.get("entry_q")))


def render_eval(out):
    if out.get("empty"):
        return "봉 없음 — %s 는 평가할 수 없다(장 시작 전이거나 수집 전)" % out["date"]
    oh = out["ohlc"]
    L = ["### 기계 평가 — %s%s" % (out["date"], " (장중 잠정)" if out.get("live") else " (확정)"),
         "",
         "- 당일 시 %.2f · 고 %.2f · 저 %.2f · 종 %.2f (폭 %.2f) · 전일 종 %s → **실제 방향 %s**(종가−시가, ±%.1fpt 보합)" % (
             oh["open"], oh["high"], oh["low"], oh["close"], oh["range"], out.get("prev_close"), out["actual_dir"], DIR_DEADBAND),
         "- 재량 실현(신동2-AI) %s pt · 거래 %d · 규칙 %s" % (_fmtp(out["live_ai"]["pnl"]), out["live_ai"]["n"], out.get("rules")),
         "- 적용 레슨: %s" % (", ".join(out["lessons_applied"]) if out["lessons_applied"] else "없음(기록에 --lessons 미표기)"),
         "",
         "| 계획 | 방향 | 적중 | 진입 | 손절 | 청산 | 체결 | 결과 | 손익 | MFE/MAE | 타점 품질 |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for ph, key, nm in (("overnight", "익일계획(전날 장후)", "overnight"), ("premarket", "장전계획", "premarket")):
        d = out.get(ph) or {}
        if not d:
            L.append("| %s | (기록 없음) | | | | | | | | | |" % key)
        for v in VARIANTS:
            if v in d:
                L.append(_plan_row("%s · %s" % (key, "개선(live)" if v == "live" else "기존(legacy 섀도)"), d[v]))
    on, pm = out.get("overnight") or {}, out.get("premarket") or {}
    if "live" in on and "legacy" in on:
        L.append("")
        L.append("- 익일계획 개선 − 기존 = **%s pt**" % _fmtp(on["live"]["sim"]["pnl"] - on["legacy"]["sim"]["pnl"]))
    if "live" in pm and "legacy" in pm:
        L.append("- 장전계획 개선 − 기존 = **%s pt**" % _fmtp(pm["live"]["sim"]["pnl"] - pm["legacy"]["sim"]["pnl"]))
    L.append("")
    L.append("타점 품질: 포착률 = 손익 ÷ 당일 고저폭 · 진입품질 = 1 − (진입가와 그 방향 최악 극단의 거리 ÷ 고저폭). "
             "목표/손절 여유는 eval.json 의 target_margin / stop_margin.")
    return "\n".join(L)


# ── 레슨런 레지스트리 ──────────────────────────────────────────────────────
def _lessons_path():
    return os.path.join(_learn_dir(), LESSONS_JSON)


def load_lessons():
    p = _lessons_path()
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_lessons(ls):
    SL._atomic_json(_lessons_path(), ls)
    with open(os.path.join(_learn_dir(), "레슨런_레지스트리.md"), "w", encoding="utf-8") as f:
        f.write(render_lessons(ls))


def _find(ls, lid):
    for l in ls:
        if l["id"] == lid:
            return l
    return None


def lesson_add(lid, title, rule, trigger="", status="후보", origin=None, evidence=None, note="", now=None):
    if status not in STATUSES:
        raise SystemExit("status 는 %s 중 하나" % (STATUSES,))
    ls = load_lessons()
    if _find(ls, lid):
        raise SystemExit("이미 있는 레슨 %s — set/tally 로 갱신할 것(기록은 고치지 않는다)" % lid)
    now = now or _dt.datetime.now()
    l = dict(id=lid, title=title, rule=rule, trigger=trigger, status=status, origin=origin or now.date().isoformat(),
             evidence=sorted(set(evidence or [])), applied=[], hit=[], miss=[], note=note,
             history=[dict(ts=now.isoformat(timespec="seconds"), status=status, why="신설")])
    ls.append(l)
    save_lessons(ls)
    return l


def lesson_set(lid, status=None, note=None, rule=None, why="", now=None):
    ls = load_lessons()
    l = _find(ls, lid)
    if not l:
        raise SystemExit("없는 레슨 %s" % lid)
    now = now or _dt.datetime.now()
    if status:
        if status not in STATUSES:
            raise SystemExit("status 는 %s 중 하나" % (STATUSES,))
        l["status"] = status
        l["history"].append(dict(ts=now.isoformat(timespec="seconds"), status=status, why=why))
    if note is not None:
        l["note"] = note
    if rule is not None:
        l["rule"] = rule
    save_lessons(ls)
    return l


def lesson_tally(lid, day, hit=None, applied=False):
    ls = load_lessons()
    l = _find(ls, lid)
    if not l:
        raise SystemExit("없는 레슨 %s" % lid)
    if applied and day not in l["applied"]:
        l["applied"].append(day)
    if hit is True and day not in l["hit"]:
        l["hit"].append(day)
    if hit is False and day not in l["miss"]:
        l["miss"].append(day)
    save_lessons(ls)
    return l


def lesson_suggestion(l):
    n, h, m = len(l["applied"]), len(l["hit"]), len(l["miss"])
    if l["status"] == "후보" and n >= PROMOTE_MIN_APPLIED and h > m:
        return "적용 %d회(적중 %d/실패 %d) → 「적용중」 승격 검토" % (n, h, m)
    if l["status"] in ACTIVE and n >= PROMOTE_MIN_APPLIED and m > h:
        return "적용 %d회(적중 %d/실패 %d) → 실패 우세 — 딥다이브/폐기 검토" % (n, h, m)
    return ""


def render_lessons(ls):
    L = ["# 신동2 레슨런 레지스트리 (MW0601)", "",
         "> 값의 단일 출처는 같은 폴더 `lessons.json` — 이 파일은 렌더다(손으로 고치지 말 것).",
         "> 상태: 후보 → 적용중 → 검증 / 폐기 / 딥다이브. 적용·적중·실패는 **날짜 목록**이라 횟수가 곧 표본 수다.",
         "> 🔴 하루를 보고 만든 레슨은 그 하루에 다시 대 보면 당연히 좋아 보인다(과적합) — 적용은 **다음 거래일부터** 센다.",
         "", "| ID | 상태 | 레슨 | 적용 규칙 | 발동 조건 | 기원 | 적용/적중/실패 | 비고 |", "|---|---|---|---|---|---|---|---|"]
    for l in ls:
        sug = lesson_suggestion(l)
        L.append("| %s | %s | **%s** | %s | %s | %s | %d/%d/%d | %s |" % (
            l["id"], l["status"], l["title"], l["rule"], l.get("trigger") or "—", l["origin"],
            len(l["applied"]), len(l["hit"]), len(l["miss"]), (l.get("note") or "") + ((" ⚠ " + sug) if sug else "")))
    L += ["", "## 이력", ""]
    for l in ls:
        hist = " → ".join("%s %s%s" % (h["ts"][:10], h["status"], ("(%s)" % h["why"]) if h.get("why") else "") for h in l["history"])
        L.append("- **%s** %s · 근거일 %s · 적용 %s · 적중 %s · 실패 %s" % (
            l["id"], hist, ", ".join(l["evidence"]) or "—", ", ".join(l["applied"]) or "—", ", ".join(l["hit"]) or "—", ", ".join(l["miss"]) or "—"))
    return "\n".join(L) + "\n"


def lessons_text(active_only=False):
    ls = load_lessons()
    if active_only:
        ls = [l for l in ls if l["status"] in ACTIVE]
    if not ls:
        return "레슨 없음" + ("(활성)" if active_only else "")
    L = []
    for l in ls:
        sug = lesson_suggestion(l)
        L.append("- %s [%s] %s — %s%s (적용 %d · 적중 %d · 실패 %d)%s" % (
            l["id"], l["status"], l["title"], l["rule"], (" · 조건: " + l["trigger"]) if l.get("trigger") else "",
            len(l["applied"]), len(l["hit"]), len(l["miss"]), (" ⚠ " + sug) if sug else ""))
    return "\n".join(L)


# ── 피드백 ────────────────────────────────────────────────────────────────
def _fb_doc_path(day):
    return os.path.join(_learn_dir(), "피드백_MW0601-%s.md" % day.replace("-", ""))


def feedback(day, comment, applied=(), hits=(), misses=(), now=None):
    now = now or _dt.datetime.now()
    out = evaluate_day(day, now)
    if out.get("empty"):
        raise SystemExit("봉 없음 — %s 는 아직 평가할 수 없다" % day)
    applied = sorted(set(applied) | set(hits) | set(misses) | set(out.get("lessons_applied") or []))
    ls = load_lessons()
    unknown = [l for l in applied if not _find(ls, l)]
    if unknown:
        raise SystemExit("레지스트리에 없는 레슨 %s — 먼저 lesson add" % unknown)
    for l in applied:
        lesson_tally(l, day, applied=True)
    for l in hits:
        lesson_tally(l, day, hit=True)
    for l in misses:
        lesson_tally(l, day, hit=False)
    rec = dict(ts=now.isoformat(timespec="seconds"), date=day, eval_live=out["live"], applied=applied, hits=sorted(hits),
               misses=sorted(misses), comment=(comment or "").strip(), actual_dir=out["actual_dir"], ai_pnl=out["live_ai"]["pnl"])
    dd = SL.day_dir(day)
    SL._append_jsonl(os.path.join(dd, "feedback.jsonl"), rec)
    SL._atomic_json(os.path.join(dd, "feedback.json"), rec)
    p = _fb_doc_path(day)
    new = not os.path.exists(p) or os.path.getsize(p) == 0
    with open(p, "a", encoding="utf-8") as f:
        if new:
            f.write("# 신동2 피드백 — %s (MW0601)\n\n> 예측 → 실행 → 평가·반성 → 레슨 기록 사이클의 그날 기록. append-only · 시각은 벽시계.\n"
                    "> 기계 평가는 `scripts/shindong2_live.py evaluate`, 본문은 Claude 의 반성. 레슨은 `학습/레슨런_레지스트리.md`.\n\n" % day)
        f.write("## %s 피드백%s\n\n%s\n\n### 평가·반성\n\n적용 레슨 %s · 적중 %s · 실패 %s\n\n%s\n\n" % (
            now.strftime("%Y-%m-%d %H:%M"), " (장중 잠정)" if out["live"] else "", render_eval(out),
            ", ".join(applied) or "—", ", ".join(sorted(hits)) or "—", ", ".join(sorted(misses)) or "—", rec["comment"]))
    return rec, out, p


def latest_feedback_before(day):
    try:
        days = sorted(d for d in os.listdir(SL.LIVE_DIR) if d.isdigit() and len(d) == 8 and d < day.replace("-", ""))
    except OSError:
        return None
    for d in reversed(days):
        p = os.path.join(SL.LIVE_DIR, d, "feedback.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    return None


# ── 워크포워드 추이 ────────────────────────────────────────────────────────
def _plan_cell(e):
    if not e:
        return None
    return dict(dir=e["dir"], hit=e["dir_hit"], pnl=e["sim"]["pnl"] if e["sim"].get("kind") == "계획" else 0.0,
                filled=bool(e["sim"].get("filled")), capture=(e.get("q") or {}).get("capture"))


def trend_rows(today=None, now=None):
    """날짜별 한 행. 확정 eval.json 은 그대로 쓰고, 없거나 잠정이면 다시 평가한다(DB 를 읽는다 — 장후 전용)."""
    key = (today or _dt.date.today().isoformat()).replace("-", "")
    try:
        days = sorted(d for d in os.listdir(SL.LIVE_DIR) if d.isdigit() and len(d) == 8 and d <= key)
    except OSError:
        return []
    rows = []
    for d in days:
        dd = os.path.join(SL.LIVE_DIR, d)
        if not os.path.exists(os.path.join(dd, "ai_log.jsonl")):
            continue
        day = "%s-%s-%s" % (d[:4], d[4:6], d[6:])
        ev = None
        p = os.path.join(dd, "eval.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                ev = json.load(f)
            if ev.get("live"):
                ev = None
        if ev is None:
            try:
                ev = evaluate_day(day, now)
            except Exception as e:                       # 그날 봉을 못 읽으면 행을 비운 채 사유를 남긴다(미측정 ≠ 0)
                rows.append(dict(date=day, error=str(e)))
                continue
        if ev.get("empty"):
            continue
        fb = None
        fp = os.path.join(dd, "feedback.json")
        if os.path.exists(fp):
            with open(fp, encoding="utf-8") as f:
                fb = json.load(f)
        on, pm = ev.get("overnight") or {}, ev.get("premarket") or {}
        rows.append(dict(date=day, live=ev.get("live"), actual=ev["actual_dir"], range=ev["ohlc"]["range"],
                         on_live=_plan_cell(on.get("live")), on_legacy=_plan_cell(on.get("legacy")),
                         pm_live=_plan_cell(pm.get("live")), pm_legacy=_plan_cell(pm.get("legacy")),
                         ai_pnl=ev["live_ai"]["pnl"], ai_n=ev["live_ai"]["n"],
                         rules_base=(ev.get("rules") or {}).get("base"), rules_p=(ev.get("rules") or {}).get("p"),
                         lessons=ev.get("lessons_applied") or (fb or {}).get("applied") or [], feedback=bool(fb),
                         fb_hits=(fb or {}).get("hits") or [], fb_misses=(fb or {}).get("misses") or []))
    return rows


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return (round(sum(xs) / len(xs), 2) if xs else None), len(xs)


def _rate(bs):
    bs = [b for b in bs if b is not None]
    return (round(sum(1 for b in bs if b) / len(bs), 2) if bs else None), len(bs)


def trend_windows(rows):
    rows = [r for r in rows if not r.get("error")]
    out = {}
    for w in WINDOWS:
        sub = rows[-w:]
        if not sub:
            continue
        g = lambda k, f: [f(r[k]) if r.get(k) else None for r in sub]
        pairs_on = [(r["on_live"]["pnl"], r["on_legacy"]["pnl"]) for r in sub if r.get("on_live") and r.get("on_legacy")]
        pairs_pm = [(r["pm_live"]["pnl"], r["pm_legacy"]["pnl"]) for r in sub if r.get("pm_live") and r.get("pm_legacy")]
        imp_on, n_on = _mean([a - b for a, b in pairs_on])
        imp_pm, n_pm = _mean([a - b for a, b in pairs_pm])
        out[w] = dict(n=len(sub), first=sub[0]["date"], last=sub[-1]["date"],
                      on_hit=_rate(g("on_live", lambda c: c["hit"])), pm_hit=_rate(g("pm_live", lambda c: c["hit"])),
                      on_pnl=_mean(g("on_live", lambda c: c["pnl"])), pm_pnl=_mean(g("pm_live", lambda c: c["pnl"])),
                      on_legacy_pnl=_mean(g("on_legacy", lambda c: c["pnl"])), pm_legacy_pnl=_mean(g("pm_legacy", lambda c: c["pnl"])),
                      improve_on=(imp_on, n_on), improve_pm=(imp_pm, n_pm),
                      ai_pnl=round(sum(r["ai_pnl"] or 0 for r in sub), 2), ai_days_pos=sum(1 for r in sub if (r["ai_pnl"] or 0) > 0),
                      rules_base=round(sum(r["rules_base"] or 0 for r in sub), 2),
                      lessons_days=sum(1 for r in sub if r["lessons"]), feedback_days=sum(1 for r in sub if r["feedback"]))
    return out


def trend_verdict(rows, win):
    """판정 — 개선(live) 이 기존(legacy) 을 이기고 있는가. 표본이 없으면 「미측정」이지 「개선 없음」이 아니다."""
    rows = [r for r in rows if not r.get("error")]
    w5 = win.get(5) or {}
    imp, n = w5.get("improve_on") or (None, 0)
    imp_pm, n_pm = w5.get("improve_pm") or (None, 0)
    msgs, flag = [], "ok"
    paired = n + n_pm
    if paired < 3:
        flag = "unmeasured"
        msgs.append("개선 효과 미측정 — 기존(legacy) 섀도와 짝지어진 계획이 %d건(최소 3건). 장후·장전마다 `--variant legacy` 를 함께 남길 것." % paired)
    else:
        worst = min(x for x in (imp, imp_pm) if x is not None)
        if worst <= 0:
            flag = "deepdive"
            msgs.append("🔴 딥다이브 필요 — 최근 5일 개선−기존: 익일계획 %s(n=%d) · 장전 %s(n=%d). 개선방식이 기존을 못 이긴다." % (
                _fmtp(imp), n, _fmtp(imp_pm), n_pm))
        else:
            msgs.append("✅ 개선 중 — 최근 5일 개선−기존: 익일계획 %s(n=%d) · 장전 %s(n=%d)." % (_fmtp(imp), n, _fmtp(imp_pm), n_pm))
    # 재량 자체의 건강 — 방향은 맞는데 돈을 못 버는가, 방향부터 틀리는가
    if w5:
        hit, hn = w5["on_hit"]
        if hn >= 3 and hit is not None and hit < 0.5:
            flag = "deepdive" if flag != "unmeasured" else flag
            msgs.append("🔴 익일계획 방향 적중 %.0f%%(n=%d) < 50%% — 방향 근거(수급 축 선택)부터 딥다이브." % (hit * 100, hn))
        if w5["n"] >= 3 and w5["ai_pnl"] < 0 and hit is not None and hit >= 0.5:
            msgs.append("⚠ 방향은 맞는데(적중 %.0f%%) 재량 실현 %s pt 적자 — 타점(진입·손절·청산) 설계가 병목." % (hit * 100, _fmtp(w5["ai_pnl"])))
    streak = 0
    for r in reversed(rows):
        a, b = r.get("on_live"), r.get("on_legacy")
        if a and b:
            if a["pnl"] - b["pnl"] <= 0:
                streak += 1
            else:
                break
    if streak >= 3:
        flag = "deepdive"
        msgs.append("🔴 익일계획 개선−기존 ≤ 0 이 %d일 연속." % streak)
    return dict(flag=flag, messages=msgs, streak_nonimprove=streak)


def _ai(r):
    """재량 실현 — 거래 0건이면 「미참여」(0 이 아니다)."""
    return "—(미참여)" if not r.get("ai_n") else _fmtp(r["ai_pnl"])


def _cell(c):
    if not c:
        return "—"
    h = "" if c["hit"] is None else ("✅" if c["hit"] else "❌")
    return "%s%s %s%s" % (c["dir"], h, _fmtp(c["pnl"]), "" if c["filled"] else "(미체결)")


def render_trend(rows, win, verdict):
    L = ["# 신동2 워크포워드 추이 (MW0601)", "",
         "> `scripts/shindong2_live.py trend` 가 매번 다시 쓴다(파생 뷰). 원천은 날짜별 `eval.json`·`feedback.json`.",
         "> 계획 손익은 그 계획을 **단독**으로 1분봉에 대 본 값(실제 재량 실현과 다르다). 개선(live) − 기존(legacy) 이 핵심 지표.",
         "> 「—」 는 미측정이다(계측 4원칙 ② — 0 이 아니다).", "",
         "## 판정", ""] + ["- " + m for m in verdict["messages"]] + ["", "## 창", "",
         "| 창 | 기간 | 익일계획 적중 | 장전 적중 | 익일계획 평균pt (개선/기존) | 장전 평균pt (개선/기존) | 개선−기존 (익일/장전) | 재량 실현 합 | 규칙 기본 합 | 레슨 적용일 | 피드백일 |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for w in WINDOWS:
        v = win.get(w)
        if not v:
            continue
        r = lambda t: "—" if t[0] is None else "%.0f%% (n=%d)" % (t[0] * 100, t[1])
        m = lambda t: "—" if t[0] is None else "%s (n=%d)" % (_fmtp(t[0]), t[1])
        L.append("| 최근 %d일 | %s–%s (n=%d) | %s | %s | %s / %s | %s / %s | %s / %s | %s | %s | %d | %d |" % (
            w, v["first"], v["last"], v["n"], r(v["on_hit"]), r(v["pm_hit"]), m(v["on_pnl"]), m(v["on_legacy_pnl"]),
            m(v["pm_pnl"]), m(v["pm_legacy_pnl"]), m(v["improve_on"]), m(v["improve_pm"]), _fmtp(v["ai_pnl"]), _fmtp(v["rules_base"]),
            v["lessons_days"], v["feedback_days"]))
    L += ["", "## 날짜별", "",
          "| 날짜 | 실제 | 폭 | 익일계획 개선 | 익일계획 기존 | 장전 개선 | 장전 기존 | 재량 실현 | 규칙 기본 | 규칙 P | 적용 레슨 | 레슨 적중/실패 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("error"):
            L.append("| %s | (평가 실패: %s) | | | | | | | | | | |" % (r["date"], r["error"][:60]))
            continue
        L.append("| %s%s | %s | %.2f | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s |" % (
            r["date"], "(잠정)" if r.get("live") else "", r["actual"], r["range"] or 0, _cell(r["on_live"]), _cell(r["on_legacy"]),
            _cell(r["pm_live"]), _cell(r["pm_legacy"]), _ai(r), _fmtp(r["rules_base"]), _fmtp(r["rules_p"]),
            ", ".join(r["lessons"]) or "—", ", ".join(r["fb_hits"]) or "—", ", ".join(r["fb_misses"]) or "—"))
    return "\n".join(L) + "\n"


def trend(today=None, now=None, write=True):
    rows = trend_rows(today, now)
    win = trend_windows(rows)
    verdict = trend_verdict(rows, win)
    out = dict(generated_at=(now or _dt.datetime.now()).isoformat(timespec="seconds"), rows=rows, windows=win, verdict=verdict)
    if write:
        SL._atomic_json(os.path.join(SL.LIVE_DIR, "trend.json"), out)
        with open(os.path.join(_learn_dir(), "추이_MW0601.md"), "w", encoding="utf-8") as f:
            f.write(render_trend(rows, win, verdict))
    return out


def trend_text(out, last=5):
    L = ["## 워크포워드 추이 (%d일 기록)" % len(out["rows"])] + ["- " + m for m in out["verdict"]["messages"]]
    for r in out["rows"][-last:]:
        if r.get("error"):
            L.append("  %s 평가 실패 %s" % (r["date"], r["error"][:60]))
            continue
        L.append("  %s 실제 %s · 익일계획 %s / 기존 %s · 장전 %s / 기존 %s · 재량 %s · 기본 %s · 레슨 %s" % (
            r["date"], r["actual"], _cell(r["on_live"]), _cell(r["on_legacy"]), _cell(r["pm_live"]), _cell(r["pm_legacy"]),
            _ai(r), _fmtp(r["rules_base"]), ",".join(r["lessons"]) or "—"))
    return "\n".join(L)


# ── 장전 브리핑 ────────────────────────────────────────────────────────────
def brief(day, now=None):
    L = ["# 신동2 학습 브리핑 — %s" % day, "", "## 활성 레슨(계획에 적용하고 `--lessons` 로 표기할 것)", lessons_text(active_only=True), "",
         "## 후보·딥다이브 레슨(관찰만 — 승격은 표본 뒤)",
         "\n".join(l for l in lessons_text().split("\n") if "[후보]" in l or "[딥다이브]" in l) or "없음", ""]
    fb = latest_feedback_before(day)
    if fb:
        L += ["## 전일 피드백 (%s · 실제 %s · 재량 %s)" % (fb["date"], fb.get("actual_dir"), _fmtp(fb.get("ai_pnl"))),
              "적용 %s · 적중 %s · 실패 %s" % (", ".join(fb["applied"]) or "—", ", ".join(fb["hits"]) or "—", ", ".join(fb["misses"]) or "—"),
              "\n".join(fb["comment"].split("\n")[:30]), ""]
    else:
        L += ["## 전일 피드백", "없음 — 전날 장후 `feedback` 이 돌지 않았다(미기록 ≠ 문제없음)", ""]
    p = os.path.join(SL.LIVE_DIR, "trend.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            t = json.load(f)
        L.append(trend_text(t))
    else:
        L.append("## 워크포워드 추이 — 아직 없음(`trend` 미실행)")
    # 오늘 익일계획(전날 장후 작성) 변형
    on = _last_per_variant([r for r in SL.load_ai_log(day) if r.get("phase") == "overnight" and r.get("action") in ("plan", "stand")])
    if on:
        L += ["", "## 오늘 익일계획(전날 장후 작성)"]
        for v in VARIANTS:
            r = on.get(v)
            if r:
                L.append("- %s: %s %s 진입 %s 손절 %s 청산 %s · 레슨 %s" % (
                    "개선(live)" if v == "live" else "기존(legacy)", r["action"], r["dir"], r.get("entry") or "시장가",
                    r.get("stop"), r.get("target"), ",".join(r.get("lessons") or []) or "—"))
    return "\n".join(L)
