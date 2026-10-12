# -*- coding: utf-8 -*-
"""[MW0601 683차] 신동2 시나리오 예측 — 확률 + 경로를 **기계가 채점할 수 있는 형태**로 남기고, 매 회차·장후·추이에서 채점한다.

왜: 2026-10-12 장후 분석은 「A 45% · B 35% · C 20%」처럼 확률과 경로로 내일을 말했다. 그런데 그것이 해설 본문에만 있으면
다음 날 아무도 채점하지 않고, 「70%를 준 시나리오가 실제로 몇 번 맞았나」(보정)를 영영 모른다. 학습 사이클
(예측 → 결과 → 반성 → 레슨 → 다음 예측)이 계획 손익만이 아니라 **확률 판단 자체**에도 돌게 하려는 모듈이다.

명세(`record --scenarios`)
    "A|반등 후 1020 저항|45|1020|1030|1012 ; B|하락 재개|35|1000|1012 ; C|숏커버 랠리|20|1030|1012"
    키 | 이름 | 확률(%) | 목표 | 무효 [| 이후]
      · 확률: 정수 5% 단위, 합 100.
      · 목표에 무효보다 **먼저** 닿으면 진행. 「이후」가 없으면 그 순간 실현.
      · 「이후」가 있으면(되돌림형 — 「1020 찍고 재하락」) 목표 뒤에 이후 레벨에 무효보다 먼저 닿아야 실현.
      · 무효에 먼저 닿으면 무효. 시한(15:10)까지 둘 다 없으면 미결 — 채점상 「일어나지 않음(0)」.
    같은 봉에 목표·무효가 함께 걸리면 무효 우선(보수적 — simulate_plan 의 「같은 봉 손절 우선」과 같은 규약).

채점
    brier = 평균 (p − o)²  (o = 실현 1 / 아니면 0)        낮을수록 좋다
    base  = 같은 결과에 균등 확률(1/n)을 준 brier           「아무 생각 없이 나눴을 때」
    bss   = 1 − brier/base                                    > 0 이면 균등보다 낫다 · ≤ 0 이면 확률 판단이 기여하지 못했다
    top_hit = 최고 확률 시나리오가 실현됐나
🔴 미래 참조 차단: 효력은 기록 다음 분(장전 08:45 이전 기록은 개장)부터. 시각은 벽시계(live.py record).
🔴 미측정 ≠ 0: 시나리오가 없는 날의 brier 는 None 이다.
"""
from __future__ import annotations

import datetime as _dt

HORIZON = "15:10"
CAL_BINS = ((0, 25), (25, 45), (45, 65), (65, 101))   # 확률(%) 구간 — 보정표


def _hm(t):
    h, m = t.split(":")[:2]
    return int(h) * 60 + int(m[:2])


def parse_spec(spec):
    """명세 문자열 → 시나리오 목록. 잘못되면 SystemExit(채점 불가 기록 금지)."""
    if not spec or not spec.strip():
        raise SystemExit("시나리오 명세가 비었다")
    items, keys = [], set()
    for chunk in [c for c in spec.split(";") if c.strip()]:
        f = [x.strip() for x in chunk.split("|")]
        if len(f) not in (5, 6):
            raise SystemExit("시나리오 명세는 키|이름|확률|목표|무효[|이후] — 받은 것: %r" % chunk.strip())
        try:
            prob, target, invalid = int(f[2]), float(f[3]), float(f[4])
            then = float(f[5]) if len(f) == 6 and f[5] else None
        except ValueError:
            raise SystemExit("확률은 정수, 목표·무효·이후는 숫자여야 한다: %r" % chunk.strip())
        if f[0] in keys:
            raise SystemExit("시나리오 키 중복: %s" % f[0])
        if prob < 0 or prob > 100 or prob % 5:
            raise SystemExit("확률은 0–100 의 5%% 단위 정수: %s=%d" % (f[0], prob))
        if target == invalid:
            raise SystemExit("목표와 무효가 같다: %s" % f[0])
        if then is not None and (then - target) * (invalid - target) > 0:
            raise SystemExit("「이후」는 목표에서 무효 반대쪽이어야 한다(되돌림): %s" % f[0])
        keys.add(f[0])
        items.append(dict(key=f[0], name=f[1], prob=prob, target=target, invalid=invalid, then=then,
                          kind=("상승" if target > invalid else "하락") if then is None else "되돌림"))
    if len(items) < 2:
        raise SystemExit("시나리오는 2개 이상(대안 없는 전망은 확률이 아니다)")
    s = sum(i["prob"] for i in items)
    if s != 100:
        raise SystemExit("확률 합이 %d%% — 100%% 여야 한다" % s)
    return items


def resolve(item, bars, eff, horizon=HORIZON):
    """한 시나리오의 결말. bars = [(hh:mm, o, h, l, c), …]. 반환 status 실현|무효|진행|미결, t, stage."""
    stage, t_target = "대기", None
    last = None
    # 기준가 = 효력 직전 봉 종가(없으면 첫 효력 봉 시가). 목표·무효에 닿는 방향은 기준가 대비 위/아래로 정한다 —
    # 되돌림형(목표가 기준가와 무효 사이)도 같은 규칙으로 풀린다.
    pre = [c for c in bars if _hm(c[0]) < _hm(eff)]
    post = [c for c in bars if _hm(eff) <= _hm(c[0]) < _hm(horizon)]
    if not post:
        return dict(status="미결", t=None, stage=stage, t_target=None)
    ref = pre[-1][4] if pre else post[0][1]

    def reached(c, px, frm):
        return (c[2] >= px) if px > frm else (c[3] <= px)
    for c in post:
        last = c[0]
        inv = reached(c, item["invalid"], ref)
        if stage == "대기":
            hit = reached(c, item["target"], ref)
            if inv:                                        # 같은 봉이면 무효 우선
                return dict(status="무효", t=c[0], stage=stage)
            if hit:
                t_target = c[0]
                if item.get("then") is None:
                    return dict(status="실현", t=c[0], stage="목표", t_target=t_target)
                stage = "목표"
                continue
        else:                                              # 되돌림형 — 목표 뒤 「이후」 대 무효
            back = reached(c, item["then"], item["target"])
            inv = reached(c, item["invalid"], item["target"])
            if inv:
                return dict(status="무효", t=c[0], stage=stage, t_target=t_target)
            if back:
                return dict(status="실현", t=c[0], stage="이후", t_target=t_target)
    return dict(status="진행" if stage == "목표" else "미결", t=last, stage=stage, t_target=t_target)


def score_set(items, outcomes):
    """outcomes: key → 1/0. brier · 균등 기준 · bss · top_hit."""
    n = len(items)
    if not n:
        return {}
    br = sum((i["prob"] / 100.0 - outcomes[i["key"]]) ** 2 for i in items) / n
    base = sum((1.0 / n - outcomes[i["key"]]) ** 2 for i in items) / n
    top = max(items, key=lambda i: i["prob"])
    tops = [i for i in items if i["prob"] == top["prob"]]
    return dict(brier=round(br, 4), base=round(base, 4), bss=(round(1 - br / base, 3) if base > 0 else None),
                top=top["key"] if len(tops) == 1 else "/".join(i["key"] for i in tops),
                top_hit=(any(outcomes[i["key"]] for i in tops)), realized=[i["key"] for i in items if outcomes[i["key"]]])


def evaluate_sets(recs, bars, eff_fn, final):
    """그날 시나리오가 달린 기록들을 채점. final=False(장중)면 진행·미결은 잠정이라 brier 를 매기지 않는다."""
    out = []
    for r in recs:
        sc = r.get("scenarios") or {}
        items = sc.get("items") or []
        if not items:
            continue
        eff = eff_fn(r)
        res = {i["key"]: resolve(i, bars, eff) for i in items}
        row = dict(id=r.get("id"), ts=r.get("ts"), phase=r.get("phase"), action=r.get("action"), eff=eff,
                   lessons=r.get("lessons") or [], items=items, res=res, final=final)
        open_ = [k for k, v in res.items() if v["status"] in ("진행", "미결")]
        if final or not open_:
            row.update(score_set(items, {k: 1 if v["status"] == "실현" else 0 for k, v in res.items()}))
        out.append(row)
    return out


def day_summary(sets):
    """하루 요약 — 채점된 세트만. 익일계획(overnight) 세트는 따로 본다(내일 예측의 정밀도가 핵심 지표)."""
    sc = [s for s in sets if s.get("brier") is not None]
    if not sc:
        return dict(n=0)
    m = lambda k, xs: round(sum(x[k] for x in xs) / len(xs), 4) if xs else None
    bss = [s for s in sc if s.get("bss") is not None]
    on = [s for s in sc if s["phase"] == "overnight"]
    return dict(n=len(sc), brier=m("brier", sc), bss=m("bss", bss) if bss else None,
                top_hit=round(sum(1 for s in sc if s["top_hit"]) / len(sc), 2),
                on_brier=on[-1]["brier"] if on else None, on_bss=on[-1].get("bss") if on else None,
                on_top_hit=on[-1]["top_hit"] if on else None,
                pairs=[(i["prob"], 1 if s["res"][i["key"]]["status"] == "실현" else 0) for s in sc for i in s["items"]])


def calibration(pairs):
    """[(prob%, o)] → 구간별 평균 확률 · 실현율 · n."""
    rows = []
    for lo, hi in CAL_BINS:
        sub = [(p, o) for p, o in pairs if lo <= p < hi]
        if sub:
            rows.append(dict(bin="%d–%d%%" % (lo, min(hi, 100)), n=len(sub), mean_p=round(sum(p for p, _ in sub) / len(sub), 1),
                             rate=round(100.0 * sum(o for _, o in sub) / len(sub), 1)))
    return rows


def calibration_advice(cal, min_n=5, gap=15.0):
    """보정표 → 다음 예측에 반영할 지침. 표본이 적으면 말하지 않는다(하루로 레슨을 만들지 않는 원칙)."""
    out = []
    for r in cal:
        if r["n"] < min_n:
            continue
        d = r["mean_p"] - r["rate"]
        if d >= gap:
            out.append("과신 — %s 구간 평균 %.0f%% 를 줬는데 실현 %.0f%%(n=%d). 이 구간 확률을 %.0f%%p 낮출 것." % (
                r["bin"], r["mean_p"], r["rate"], r["n"], d))
        elif d <= -gap:
            out.append("과소 — %s 구간 평균 %.0f%% 를 줬는데 실현 %.0f%%(n=%d). 이 구간 확률을 %.0f%%p 올릴 것." % (
                r["bin"], r["mean_p"], r["rate"], r["n"], -d))
    return out


def render_status(sets, limit=3):
    """snapshot 용 — 직전 예측의 지금까지 결과(예측결과 → 반성의 재료)."""
    if not sets:
        return ["", "### 시나리오 채점 — 오늘 기록된 시나리오 없음(장전·장중·익일 기록에 `--scenarios` 필수)"]
    L = ["", "### 시나리오 채점 (직전 예측 → 지금까지 결과)"]
    for s in sets[-limit:]:
        cells = []
        for i in s["items"]:
            r = s["res"][i["key"]]
            cells.append("%s %d%% %s%s" % (i["key"], i["prob"], r["status"], (" " + r["t"]) if r.get("t") and r["status"] in ("실현", "무효") else
                                            (" (목표 %s 도달)" % r.get("t_target") if r["status"] == "진행" else "")))
        sc = (" · brier %.3f · BSS %s · 기본(%s) %s" % (s["brier"], "—" if s.get("bss") is None else "%+.2f" % s["bss"], s["top"],
                                                      "적중" if s["top_hit"] else "실패")) if s.get("brier") is not None else ""
        L.append("- %s %s(%s~): %s%s" % (s["ts"][11:16] if s["ts"][:10] == s.get("date", s["ts"][:10]) else s["ts"][5:16], s["phase"], s["eff"],
                                         " · ".join(cells), sc))
    return L


def render_eval(sets):
    """evaluate/feedback 용 표."""
    if not sets:
        return ["", "#### 시나리오 예측 — 기록 없음(미측정)"]
    L = ["", "#### 시나리오 예측 채점", "",
         "| 기록 | 단계 | 효력 | 시나리오(확률 → 결과) | brier | 균등 | BSS | 기본 시나리오 |", "|---|---|---|---|---|---|---|---|"]
    for s in sets:
        cells = " · ".join("%s %d%%→%s%s" % (i["key"], i["prob"], s["res"][i["key"]]["status"],
                                             ("@" + s["res"][i["key"]]["t"]) if s["res"][i["key"]]["status"] in ("실현", "무효") else "")
                           for i in s["items"])
        if s.get("brier") is None:
            L.append("| %s | %s | %s | %s | 잠정 | | | |" % (s["ts"][5:16], s["phase"], s["eff"], cells))
        else:
            L.append("| %s | %s | %s | %s | %.3f | %.3f | %s | %s %s |" % (
                s["ts"][5:16], s["phase"], s["eff"], cells, s["brier"], s["base"], "—" if s.get("bss") is None else "%+.2f" % s["bss"],
                s["top"], "✅" if s["top_hit"] else "❌"))
    sm = day_summary(sets)
    if sm.get("n"):
        L.append("")
        L.append("- 하루 평균 brier %.3f · BSS %s · 기본 시나리오 적중 %.0f%% (세트 %d) · 익일계획 세트 brier %s" % (
            sm["brier"], "—" if sm["bss"] is None else "%+.2f" % sm["bss"], sm["top_hit"] * 100, sm["n"],
            "—(없음)" if sm["on_brier"] is None else "%.3f" % sm["on_brier"]))
    return L
