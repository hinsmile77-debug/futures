# -*- coding: utf-8 -*-
"""[MW0601 2026-10-27] 신동AI 「피터의 방법」 섹션 — P층(반발·공방·먼스리 벽) · 시가범위 상자 · 피터 관점 · 봉 신선도.

`shindong2_live.py` 가 부른다(snapshot 블록 · 이벤트 · record 신선도 · 피터판단 · 장후 `pmethod`). 주문 없음(절대원칙 §6).

🔴 지위 = **섀도 + 참고 레벨**. 사전등록 `PM-2026-10-27-v1` 백필 판정이 H-P1·H-B1·H-B2 모두 FAIL 이었다
   (`docs/미륵이고도화3/피터2/피터방법_백필검증_MW0601-20261027.md`). 그래서 이 층은 판단 근거가 아니라
   **채점·관찰 대상**이다 — 시나리오 근거로 쓰려면 라이브 섀도 표본이 v2 재등록을 정당화해야 한다(문턱은 낮추지 않는다).
🔴 신동 MAIN 의 입력(premarket_levels)과 PETER 실거래 해석기(parse.py)를 건드리지 않는다.
🔴 456차 — 장중에는 하루치 ts 조회만. P층은 하루 1회 계산해 캐시한다.

저장
    data/shindong2_live/YYYYMMDD/p_levels.json   P층 캐시(벽이 생기면 1회 갱신)
                                 box.json        T(09:10·09:30) 상자 — 한 번 고정하면 고치지 않는다
문서 (커밋 대상, 피터2 폴더)
    docs/미륵이고도화3/피터2/피터방법_라이브채점_<PC>.jsonl   장후 `pmethod` 하루 1줄
    docs/미륵이고도화3/피터2/피터방법_추이_<PC>.md            누적 표
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

PDOC_DIR = os.environ.get("PMETHOD_DOC_DIR") or os.path.join(ROOT, "docs", "미륵이고도화3", "피터2")
RAW_DIR = os.path.join(ROOT, "data", "peter_feed", "_raw")
P2_LIVE = os.path.join(ROOT, "data", "peter2_live")
STATUS = "섀도(백필 FAIL — 참고 레벨)"


def _pc():
    from strategy.shindong2_ai import levels_p as P
    return P.pc()


def trend_path():
    return os.path.join(PDOC_DIR, "피터방법_추이_%s.md" % _pc())


def _hm(t):
    return int(t[:2]) * 60 + int(t[3:5])


def _rj(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _wj(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


# ── 피터 관점 ─────────────────────────────────────────────────────────────
def peter_offset(day):
    """피터가 → 미니가 오프셋. (값, 출처) — 없으면 (None, '미측정')."""
    o = _rj(os.path.join(P2_LIVE, day, "offset_live.json"))
    if o and o.get("safe") and o.get("value") is not None:
        return float(o["value"]), "live:%s" % o.get("measured_at")
    if o and o.get("prev_day") is not None:
        return float(o["prev_day"]), "%s(폴백)" % (o.get("prev_src") or "prev_day")
    return None, "미측정"


def peter_views(day, upto_hm=None):
    """그날 수신된 피터 트윗 중 매매 지시가 아닌 관점(VIEW). upto_hm 이후 수신분은 뺀다(미래 참조 금지)."""
    from strategy.peter2.parse import parse_tweet
    from strategy.peter2.view import parse_view, to_mini
    path = os.path.join(RAW_DIR, "%s.jsonl" % day)
    out = []
    if not os.path.exists(path):
        return out, False
    off, osrc = peter_offset(day)
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                t = json.loads(line)
            except ValueError:
                continue
            txt = t.get("text") or ""
            try:
                kst = _dt.datetime.strptime(t["dt"][:19], "%Y-%m-%dT%H:%M:%S") + _dt.timedelta(hours=9)
            except (KeyError, ValueError):
                continue
            seen = (t.get("seen_at") or "")[11:16]
            if upto_hm and seen and seen > upto_hm:
                continue
            r = parse_tweet(txt)
            v = parse_view(txt)
            kind = "trade" if (not r.get("ignore") and r["facts"]) else v["kind"]
            if kind in ("none", "report") or (r.get("ignore") and kind != "trade" and v["kind"] in ("none", "report")):
                continue
            lag = None
            try:
                lag = int((_dt.datetime.fromisoformat(t["seen_at"]).replace(tzinfo=None) - kst).total_seconds())
            except (KeyError, ValueError, TypeError):
                pass
            out.append(dict(id=str(t.get("id")), hm=kst.strftime("%H:%M"), seen=seen, lag_s=lag, kind=kind,
                            box=v["box"], bias=v["bias"], bias_level=v["bias_level"], levels=v["levels"][:6],
                            mini=to_mini(v, off), offset=off, offset_src=osrc,
                            raw=txt.replace("\n", " / ")[:100]))
    return out, True


# ── P층 · 상자 ────────────────────────────────────────────────────────────
def p_layer_levels(day, books, day_dir):
    """P층 레벨(캐시). 벽이 처음 생기면 1회 다시 계산한다."""
    from strategy.shindong2_ai import levels_p as P
    path = os.path.join(day_dir, "p_levels.json")
    cfg = P.prereg()
    walls, _ = P.walls_from_books(books, cfg)
    cache = _rj(path)
    if cache and (cache.get("walls_n") or not walls):
        return cache
    hist = P.load_sessions(day, cfg["p_level"]["lookback_sessions"])
    lv = P.p_levels_from(hist, walls, cfg)
    pin = P.weekly_pin(books, day)
    obj = dict(prereg=cfg["id"], computed_at=_dt.datetime.now().isoformat(timespec="seconds"),
               sessions=[d for d, _ in hist], walls_n=len(walls), levels=lv, pin=pin, anchors=P.anchors(lv))
    os.makedirs(day_dir, exist_ok=True)
    _wj(path, obj)
    return obj


def fixed_boxes(day, bars, anchors, day_dir, last_hm):
    """T 마다 한 번 상자를 고정한다(T 직전 봉까지 완결된 뒤). 고정된 상자는 고치지 않는다."""
    from strategy.shindong2_ai import levels_p as P, box as B
    cfg = P.prereg()
    path = os.path.join(day_dir, "box.json")
    st = _rj(path, {}) or {}
    changed = False
    for T in cfg["box"]["T"]:
        if T in st or not last_hm or _hm(last_hm) < _hm(T) - 1:
            continue
        bx = B.make_boxes(bars, T, anchors, cfg)
        if bx:
            bx["fixed_at"] = _dt.datetime.now().isoformat(timespec="seconds")
            st[T] = bx
            changed = True
    if changed:
        _wj(path, st)
    return st


def box_status(bars, boxes):
    """고정 상자의 지금 상태 — 위치·첫 이탈(B2)."""
    from strategy.shindong2_ai import levels_p as P, box as B
    cfg = P.prereg()
    px = bars[-1][4] if bars else None
    out = {}
    for T, bx in sorted(boxes.items()):
        s = B.score_box(bars, bx["B2"], T, cfg, end=bars[-1][0]) if bars else None
        out[T] = dict(B1=bx["B1"], B2=bx["B2"], B0=bx["B0"], or_lo=bx["or_lo"], or_hi=bx["or_hi"],
                      pos=B.box_position(px, bx["B2"]), break_side=s and s["break_side"], break_t=s and s["break_t"])
    return out


def build(day, d, bars, last_hm, day_dir, live):
    """snapshot 의 st["p_layer"]."""
    lv = p_layer_levels(day, d.get("books") or {}, day_dir)
    px = bars[-1][4] if bars else None
    boxes = fixed_boxes(day, bars, lv.get("anchors") or [], day_dir, last_hm) if bars else {}
    views, have = peter_views(day, last_hm if live else None)
    return dict(status=STATUS, levels=lv.get("levels") or [], pin=lv.get("pin"), walls_n=lv.get("walls_n"),
                sessions=lv.get("sessions"), px=px, boxes=box_status(bars, boxes), views=views, views_source=have)


def render(pl):
    """snapshot 블록."""
    if not pl:
        return []
    if pl.get("why"):
        return ["", "### 피터의 방법 — 계산 실패: %s (미측정)" % pl["why"]]
    L = ["", "### 피터의 방법 (P층 · %s)" % pl.get("status", STATUS)]
    px = pl.get("px")
    lv = [x for x in pl.get("levels") or [] if x.get("kind") in ("반발", "공방", "벽")]

    def lab(x):
        m = (" ·합류 " + "/".join(x["merged"])) if x.get("merged") else ""
        return "%.1f[%s%s]" % (x["price"], x.get("label") or x.get("kind"), m)
    if px is not None:
        up = sorted([x for x in lv if x["price"] > px], key=lambda x: x["price"])[:3]
        dn = sorted([x for x in lv if x["price"] <= px], key=lambda x: -x["price"])[:3]
        L.append("P맥점 위 %s" % (" · ".join(lab(x) for x in up) or "없음"))
        L.append("P맥점 아래 %s" % (" · ".join(lab(x) for x in dn) or "없음"))
    else:
        L.append("P맥점 %s" % " · ".join(lab(x) for x in lv[:6]))
    if not pl.get("walls_n"):
        L.append("먼스리 벽 미측정(옵션북 첫 스냅 전)")
    if pl.get("pin"):
        L.append("위클리 피닝 중심 %s" % pl["pin"]["label"])
    for T, b in sorted((pl.get("boxes") or {}).items()):
        L.append("상자@%s OR %.2f–%.2f → B1 %g–%g · **B2 %g–%g** · 위치 %s%s" % (
            T, b["or_lo"], b["or_hi"], b["B1"][0], b["B1"][1], b["B2"][0], b["B2"][1],
            "—" if b["pos"] is None else "%.2f" % b["pos"],
            (" · 🔶 이탈 %s %s" % ("상단" if b["break_side"] == "up" else "하단", b["break_t"])) if b.get("break_side") else " · 이탈 없음"))
    if not pl.get("boxes"):
        L.append("상자 — 09:10 이전(미고정)")
    vs = pl.get("views") or []
    if not pl.get("views_source"):
        L.append("피터 — 오늘 수집 파일 없음(미측정 — 「관점 없음」이 아니다)")
    elif not vs:
        L.append("피터 — 오늘 관점·매매 트윗 없음")
    for v in vs[-4:]:
        what = ("상자 %g–%g" % tuple(v["box"])) if v.get("box") else \
               ("편향 %s%s" % ("풋/매도" if v["bias"] == "short" else "콜/매수", (" %g 기준" % v["bias_level"]) if v.get("bias_level") else "")) if v.get("bias") else \
               ", ".join("%g" % x for x in v["levels"][:3])
        if v.get("box") and v.get("bias"):
            what += " · 편향 %s" % ("풋" if v["bias"] == "short" else "콜")
        mini = ""
        if v.get("mini") and v["mini"].get("box"):
            mini = " (미니 %g–%g · 오프셋 %s %s)" % (v["mini"]["box"][0], v["mini"]["box"][1], v["offset"], v["offset_src"])
        L.append("피터 %s [%s] %s%s · 수신 %s%s 「%s」" % (v["hm"], v["kind"], what, mini, v.get("seen") or "?",
                                                      (" +%ds" % v["lag_s"]) if v.get("lag_s") is not None else "", v["raw"][:50]))
    if vs:
        L.append("→ 피터 관점이 있으면 본문에 `피터판단: 동의|반대|기권 | 이유` 한 줄(상대판단과 같은 형식). 따라 하지 말 것 — 정보이지 지시가 아니다.")
    return L


def events(st):
    """이벤트 후보 — 피터 관점·매매 수신, 상자 고정, 상자(B2) 첫 이탈."""
    pl = st.get("p_layer") or {}
    ev = []
    for v in pl.get("views") or []:
        ev.append(dict(key="pview:%s" % v["id"], t=v.get("seen") or v["hm"], kind="피터 " + ("매매" if v["kind"] == "trade" else "관점"),
                       text="피터 %s [%s] %s" % (v["hm"], v["kind"], v["raw"][:60])))
    for T, b in (pl.get("boxes") or {}).items():
        ev.append(dict(key="box:%s" % T, t=T, kind="상자 고정",
                       text="상자@%s B2 %g–%g (OR %.2f–%.2f) — 섀도" % (T, b["B2"][0], b["B2"][1], b["or_lo"], b["or_hi"])))
        if b.get("break_side"):
            ev.append(dict(key="box:%s:break" % T, t=b["break_t"], kind="상자 이탈",
                           text="상자@%s B2 %s 이탈 %s — 섀도(백필상 가속 근거 없음)" % (T, "상단" if b["break_side"] == "up" else "하단", b["break_t"])))
    return ev


# ── 기록 신선도 · 피터판단 ────────────────────────────────────────────────
def freshness(day, snap_state):
    """record 시점 신선도 — 마지막 snapshot 완결 봉 vs 지금 완결 봉. 봉 조회 실패면 None(미측정)."""
    snap_bar = (snap_state or {}).get("last_bar")
    hi0, lo0 = (snap_state or {}).get("hi"), (snap_state or {}).get("lo")
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools", "maekjeom_ladder"))
        import ladder_data as L
        live = L.is_live(day)
        cs, _src = L.candles(day, live)
        bars = cs[:-1] if live and cs else cs
    except Exception as e:                                   # noqa: BLE001
        return dict(snap_bar=snap_bar, rec_bar=None, why="봉 조회 실패: %s" % type(e).__name__)
    if not bars:
        return dict(snap_bar=snap_bar, rec_bar=None, why="봉 없음")
    rec_bar = bars[-1][0]
    out = dict(snap_bar=snap_bar, rec_bar=rec_bar,
               lag_bars=(_hm(rec_bar) - _hm(snap_bar)) if snap_bar else None)
    if snap_bar and hi0 is not None:
        after = [b for b in bars if _hm(b[0]) > _hm(snap_bar)]
        nh = max((b[2] for b in after), default=None)
        nl = min((b[3] for b in after), default=None)
        out["new_hi"] = round(nh, 2) if nh is not None and nh > hi0 else None
        out["new_lo"] = round(nl, 2) if nl is not None and nl < lo0 else None
    out["stale"] = bool((out.get("lag_bars") or 0) >= 2 or out.get("new_hi") or out.get("new_lo"))
    return out


def freshness_line(fr):
    if not fr:
        return None
    if fr.get("rec_bar") is None:
        return "⚪ 봉 신선도 미측정 — %s" % fr.get("why")
    if not fr.get("stale"):
        return None
    bits = []
    if fr.get("new_hi"):
        bits.append("고 %.2f 갱신" % fr["new_hi"])
    if fr.get("new_lo"):
        bits.append("저 %.2f 갱신" % fr["new_lo"])
    return "🔴 봉 신선도 — snapshot 완결 봉 %s · 기록 시점 완결 봉 %s(%s봉 뒤)%s — 이 기록은 그 사이 봉을 반영하지 않았을 수 있다" % (
        fr.get("snap_bar"), fr["rec_bar"], fr.get("lag_bars"), (" · " + " · ".join(bits)) if bits else "")


VS_PARSE = {"동의": "agree", "반대": "disagree", "기권": "abstain", "agree": "agree", "disagree": "disagree", "abstain": "abstain"}


def parse_vs_peter_line(comment):
    for line in (comment or "").splitlines():
        s = line.strip()
        if s.startswith("피터판단:"):
            head, _, why = s[len("피터판단:"):].strip().partition("|")
            return VS_PARSE.get(head.strip()), (why.strip() or None)
    return None, None


# ── 장전 브리핑 ───────────────────────────────────────────────────────────
def brief_lines(day):
    """brief 절 — 직전 장후 채점 1줄 · 직전 거래일 장후(15:10–) 피터 관점 · 오늘 장전 피터 관점."""
    L = ["## 피터의 방법 (섀도 · 참고 레벨 — 레슨 L26)"]
    jl = os.path.join(PDOC_DIR, "피터방법_라이브채점_%s.jsonl" % _pc())
    rows = []
    if os.path.exists(jl):
        with open(jl, encoding="utf-8") as f:
            rows = [json.loads(x) for x in f if x.strip()]
    prev = [r for r in rows if r["date"] < day]
    if prev:
        r = prev[-1]
        bx = " · ".join("@%s B2 %g–%g %s" % (T, b["B2"]["box"][0], b["B2"]["box"][1], "유지" if b["B2"]["held"] else "이탈")
                        for T, b in sorted((r.get("box") or {}).items()))
        pv = " · ".join("%s %s" % (x["hm"], x["result"]) for x in r.get("peter_views") or []) or "없음"
        L.append("- 직전 채점 %s — 상자 %s · 피터 관점 %s · 신선도 위반 %s/%s" % (
            r["date"], bx or "—", pv, (r.get("fresh") or {}).get("stale", 0), (r.get("fresh") or {}).get("n", 0)))
    else:
        L.append("- 직전 채점 없음 — 장후 `pmethod` 가 아직 돌지 않았다(미기록 ≠ 문제없음)")
    pdays = sorted(f[:10] for f in os.listdir(RAW_DIR) if f.endswith(".jsonl") and f[:10] < day) if os.path.isdir(RAW_DIR) else []
    for dd, cut in ((pdays[-1] if pdays else None, "15:10"), (day, None)):
        if not dd:
            continue
        vs, have = peter_views(dd)
        if cut:
            vs = [v for v in vs if v["hm"] >= cut]
        for v in vs:
            if v["kind"] in ("trade",):
                continue
            L.append("- 피터 %s %s [%s] %s" % (dd[5:], v["hm"], v["kind"], v["raw"][:90]))
    L.append("- 오늘: 09:10·09:30 상자는 snapshot 이 자동 고정한다(섀도). 피터 관점이 뜨면 `피터판단:` 한 줄. "
             "상자·P맥점은 시나리오 레벨 후보로만 — 확률을 얹지 않는다(백필 FAIL).")
    return L


# ── 장후 채점 ─────────────────────────────────────────────────────────────
def postmarket(day, now=None):
    """하루 채점 → 라이브채점 jsonl 1줄 + 추이 md. 장후 전용."""
    from strategy.shindong2_ai import levels_p as P, box as B
    sys.path.insert(0, os.path.join(ROOT, "tools", "maekjeom_ladder"))
    import ladder_data as L
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import shindong2_live as SL
    cfg = P.prereg()
    now = now or _dt.datetime.now()
    dd = SL.day_dir(day)
    cs, _ = L.candles(day, False)
    row = dict(date=day, prereg=cfg["id"], at=now.isoformat(timespec="seconds"), bars=len(cs))
    pl = _rj(os.path.join(dd, "p_levels.json"))
    if pl is None:
        d = L.build_day(day, now=now)
        pl = p_layer_levels(day, d.get("books") or {}, dd)
    boxes = _rj(os.path.join(dd, "box.json"))
    if not boxes and cs:                                         # 라이브 고정이 없던 날(도입 전·중단) — 장후 재구성, 표기
        boxes = {T: B.make_boxes(cs, T, pl.get("anchors") or [], cfg) for T in cfg["box"]["T"]}
        boxes = {k: v for k, v in boxes.items() if v}
        row["box_reconstructed"] = True
    row["box"] = {}
    for T, bx in (boxes or {}).items():
        r = {}
        for v in ("B0", "B1", "B2"):
            s = B.score_box(cs, bx[v], T, cfg)
            r[v] = dict(box=bx[v], held=s and s["held"], brk=s and s["break_side"], brk_t=s and s["break_t"],
                        ext=s and s["ext"], mae=s and s["mae"])
        row["box"][T] = r
    reb = []
    for x in pl.get("levels") or []:
        if x.get("kind") == "반발":
            res = B.level_reaction(cs, x["price"], cfg)
            if res:
                reb.append(dict(price=x["price"], **res))
    row["p_reaction"] = reb
    # 피터 관점 채점(정규 10100 — 피터와 같은 단위)
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import peter_method_backfill as PB
    by = PB.load_all(PB.CODE, day, day)
    views, have = peter_views(day)
    from strategy.peter2.view import parse_view
    row["peter_views"] = []
    for v in views:
        if v["kind"] in ("box", "bias"):
            kst = _dt.datetime.fromisoformat("%sT%s:00" % (day, v["hm"]))
            sv = PB.score_view(dict(kind=v["kind"], box=v["box"], bias=v["bias"], bias_level=v["bias_level"],
                                    levels=v["levels"]), kst, by, cfg, v["id"], v["raw"])
            row["peter_views"].append(sv)
    row["peter_source"] = have
    # 신동AI 기록 신선도 · 피터판단
    log = SL.load_ai_log(day)
    live = [r for r in log if (r.get("variant") or "live") == "live"]
    row["fresh"] = dict(n=sum(1 for r in live if r.get("fresh")), stale=sum(1 for r in live if (r.get("fresh") or {}).get("stale")),
                        unmeasured=sum(1 for r in live if "fresh" not in r))
    vp = [r.get("vs_peter") for r in live if r.get("vs_peter")]
    row["vs_peter"] = dict(agree=vp.count("agree"), disagree=vp.count("disagree"), abstain=vp.count("abstain"))
    os.makedirs(PDOC_DIR, exist_ok=True)
    jl = os.path.join(PDOC_DIR, "피터방법_라이브채점_%s.jsonl" % _pc())
    rows = [json.loads(x) for x in open(jl, encoding="utf-8")] if os.path.exists(jl) else []
    rows = [r for r in rows if r.get("date") != day] + [row]       # 같은 날 재실행은 교체(하루 1줄)
    rows.sort(key=lambda r: r["date"])
    with open(jl, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(trend_path(), "w", encoding="utf-8") as f:
        f.write(render_trend(rows, cfg))
    return row


def _pct(a, n):
    return "—" if not n else "%.0f%% (%d/%d)" % (100.0 * a / n, a, n)


def render_trend(rows, cfg):
    L = ["# 피터의 방법 — 라이브 섀도 추이 (%s)" % _pc(), "",
         "> 장후 `shindong2_live.py pmethod` 가 하루 1줄씩 쌓는다. 사전등록 `%s` · 지위 **%s**." % (cfg["id"], STATUS),
         "> 백필 판정: `피터방법_백필검증_%s-*.md`(MW0601 초회 2026-10-27: H-P1·H-B1·H-B2 FAIL)." % _pc() + " 이 표는 v2 재등록 여부를 가를 **라이브 표본**이다 — 문턱은 바꾸지 않는다.", "",
         "## 누적", ""]
    for T in cfg["box"]["T"]:
        sub = [r["box"][T] for r in rows if T in (r.get("box") or {})]
        n = len(sub)
        L.append("- 상자@%s 유지 — B2 %s · B1 %s · B0 %s" % (T, _pct(sum(1 for s in sub if s["B2"]["held"]), n),
                                                           _pct(sum(1 for s in sub if s["B1"]["held"]), n),
                                                           _pct(sum(1 for s in sub if s["B0"]["held"]), n)))
        br = [s["B2"] for s in sub if s["B2"]["brk"] and s["B2"]["ext"] is not None]
        L.append("  · B2 이탈 %d건 중 60분 MFE>MAE %d" % (len(br), sum(1 for b in br if b["ext"] > b["mae"])))
    pr = [x for r in rows for x in r.get("p_reaction") or []]
    L.append("- 반발형 P맥점 첫 터치 — 되돌림 %d · 관통 %d · 무결말 %d" % (
        sum(1 for x in pr if x["ok"]), sum(1 for x in pr if x["ok"] is False), sum(1 for x in pr if x["ok"] is None)))
    pv = [x for r in rows for x in r.get("peter_views") or []]
    L.append("- 피터 관점 — 상자 %s 유지 · 편향 %s 적중" % (
        _pct(sum(1 for x in pv if x["kind"] == "box" and x.get("held")), sum(1 for x in pv if x["kind"] == "box" and "held" in x)),
        _pct(sum(1 for x in pv if x.get("bias") and x["kind"] != "box" and x["result"] == "적중"),
             sum(1 for x in pv if x.get("bias") and x["kind"] != "box" and x["result"] in ("적중", "빗나감")))))
    va = sum((r.get("vs_peter") or {}).get("agree", 0) for r in rows)
    vd = sum((r.get("vs_peter") or {}).get("disagree", 0) for r in rows)
    L.append("- 피터판단 — 동의 %d · 반대 %d · 동의율 %s%s" % (
        va, vd, _pct(va, va + vd),
        " · 🔴 80%% 초과 — 이 창의 「피터 대비 능가」 판정은 무효(복사본)" if va + vd and va > 0.8 * (va + vd) else ""))
    fr = [r.get("fresh") or {} for r in rows]
    L.append("- 신동AI 기록 신선도 위반 %d / 측정 %d (미측정 %d)" % (sum(x.get("stale", 0) for x in fr), sum(x.get("n", 0) for x in fr),
                                                         sum(x.get("unmeasured", 0) for x in fr)))
    L += ["", "## 일별", "", "| 날짜 | 상자@09:10 B2 | 유지 | 상자@09:30 B2 | 유지 | P맥점 반응 | 피터 관점 | 신선도 위반 | 피터판단 동/반/기 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        cells = []
        for T in cfg["box"]["T"]:
            b = (r.get("box") or {}).get(T)
            if b:
                cells += ["%g–%g%s" % (b["B2"]["box"][0], b["B2"]["box"][1], "(재구성)" if r.get("box_reconstructed") else ""),
                          ("유지" if b["B2"]["held"] else "이탈 %s %s" % (b["B2"]["brk"] or "", b["B2"]["brk_t"] or "")).strip()]
            else:
                cells += ["—", "—"]
        pr = r.get("p_reaction") or []
        cells.append(" ".join("%g%s" % (x["price"], "✓" if x["ok"] else "✗" if x["ok"] is False else "…") for x in pr) or "—")
        cells.append(" ".join("%s %s" % (x["hm"], x["result"]) for x in r.get("peter_views") or []) or
                     ("—" if r.get("peter_source") else "미측정"))
        f = r.get("fresh") or {}
        cells.append("%d/%d" % (f.get("stale", 0), f.get("n", 0)))
        v = r.get("vs_peter") or {}
        cells.append("%d/%d/%d" % (v.get("agree", 0), v.get("disagree", 0), v.get("abstain", 0)))
        L.append("| %s | %s |" % (r["date"], " | ".join(cells)))
    L.append("")
    return "\n".join(L)
