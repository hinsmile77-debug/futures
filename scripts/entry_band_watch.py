# -*- coding: utf-8 -*-
"""[MW0601 474차 / D9-B] 진입 호라이즌 라우팅 밴드 성과 — 사전등록 감시 채널.

사전등록 기준은 `config/settings.py:VALIDATION_CAMPAIGN["entry_band_watch"]`.

이 채널이 묻는 것
-----------------
`select_entry_horizon()`이 `threshold_feasibility`(tf)를 세 경계로 잘라 1m/3m/5m을
배정한다. **그 경계가 옳은가**를 묻는다 — 특정 밴드만 유독 열위이면 경계가 잘못
그어져 있다는 신호다.

D9 딥다이브가 이 채널을 만든 계기는 "닫힌 문"이 아니라 **열린 문의 경계**였다.
중기·장기 CORE 그룹이 도달 불가인 것은 태생이고(절대원칙 §3 주석) 손익 피해 증거는
없었는데, 대신 `4.4-6.0` 밴드가 유일하게 승률 50% 아래로 나왔다(n=21, 38.1%).
`_B2 = 4.4`는 387차가 4.0 → 4.4로 마지막 조정한 값이다.

⚠ 그 관측은 **근거가 아니라 계기다**
------------------------------------
여러 경계 후보 중 눈에 띄는 하나를 사후에 고른 것이므로 그대로 결론 내면 313차
원칙 ④ 위반이다. 그래서 합격선을 settings에 **먼저** 고정했고, 이 스크립트는 그것을
읽기만 한다. 표본이 문턱에 닿기 전에는 `INSUFFICIENT`를 낸다 — 그것이 결론이다.

⚠ **처방 채널이 아니다**
------------------------
`BAND_ANOMALY`가 나와도 그것은 "B2 경계를 재검토하라"는 **입력**이지 자동 조정이
아니다. 경계 변경은 매매 정책 변경이고 주간회의 안건이다. 316~318차 HurstGate가
파라미터를 성급히 움직였을 때 무슨 일이 생기는지 보여준 선례가 있다.

방법론 (313차 5원칙)
--------------------
① 일자단위 판정 ② 포지션(entry_ts) 병합 — 레그 금지(계측 4원칙 ①)
③ 최악 1일 제거 후 부호 유지 ④ 사전등록(합격선은 settings) ⑤ 전·후반 부호 일관성

실행:
    python scripts/entry_band_watch.py
    python scripts/entry_band_watch.py --json
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402

CHANNEL = "entry_band_watch"


def _cfg():
    from config.settings import VALIDATION_CAMPAIGN
    return VALIDATION_CAMPAIGN.get(CHANNEL) or {}


# ── 표본 ────────────────────────────────────────────────────────────────────

def _tf_map(cfg):
    """진입 후보 분봉의 `threshold_feasibility` — {ts: tf}.

    전용 컬럼이 없어 `ensemble_decisions.features`(141키 JSON)에서 읽는다.
    """
    from config.settings import PREDICTIONS_DB
    out = {}
    con = connect_ro(PREDICTIONS_DB)
    try:
        cur = con.execute(
            "SELECT ts, features FROM ensemble_decisions "
            "WHERE features IS NOT NULL AND date(ts) >= ?",
            (cfg.get("data_start", "2026-06-02"),),
        )
        for ts, feats in cur:
            try:
                d = json.loads(feats)
            except (ValueError, TypeError):
                continue
            v = d.get("threshold_feasibility")
            if v is None:
                continue
            try:
                out[ts] = float(v)
            except (TypeError, ValueError):
                continue
    finally:
        con.close()
    return out


def _merged_positions(cfg):
    """entry_ts 단위 포지션. 병합 규칙은 캠페인 공통과 동일(sum, entry_qty 우선).

    ⚠ `trades.quantity`는 **청산 레그별 계약수**다. max로 세면 이익 포지션이
      분할청산으로 과소 계상돼 편향된다(417차 ①, 409차 `ef3ee59`).
    """
    from config.settings import TRADES_DB
    src = cfg.get("entry_source", "SYSTEM_AUTO")
    con = connect_ro(TRADES_DB)
    try:
        cols = {r[1] for r in con.execute("PRAGMA table_info(trades)")}
        sel = "entry_ts, quantity, COALESCE(net_pnl_krw, pnl_krw) AS pnl"
        if "entry_qty" in cols:
            sel += ", entry_qty"
        rows = con.execute(
            "SELECT %s FROM trades WHERE exit_ts IS NOT NULL AND "
            "(COALESCE(entry_source,'') = ? "
            " OR (entry_source IS NULL AND COALESCE(grade,'') <> 'MANUAL'))"
            % sel, (src,)
        ).fetchall()
    finally:
        con.close()

    has_eq = "entry_qty" in cols
    merged = {}
    for r in rows:
        k = r[0]
        m = merged.setdefault(k, {"entry_ts": k, "pnl": 0.0, "qty": 0, "eq": None})
        m["pnl"] += float(r[2] or 0.0)
        m["qty"] += int(r[1] or 1)
        if has_eq and m["eq"] is None:
            try:
                eq = int(r[3] or 0)
            except (TypeError, ValueError):
                eq = 0
            if eq > 0:
                m["eq"] = eq
    for m in merged.values():
        m["qty_final"] = m["eq"] or m["qty"]
    return list(merged.values())


# ── 밴드 ────────────────────────────────────────────────────────────────────

def band_of(tf, edges):
    """tf → 밴드 이름과 정렬키. 경계는 사전등록 목록에서만 온다."""
    if tf < edges[0]:
        return "<%g" % edges[0], -1.0
    for i in range(len(edges) - 1):
        if tf < edges[i + 1]:
            return "%g-%g" % (edges[i], edges[i + 1]), edges[i]
    return ">=%g" % edges[-1], edges[-1]


def all_band_names(edges):
    """경계로부터 생성되는 밴드 이름 전체 — `focus_band` 검증에 쓴다."""
    names = ["<%g" % edges[0]]
    for i in range(len(edges) - 1):
        names.append("%g-%g" % (edges[i], edges[i + 1]))
    names.append(">=%g" % edges[-1])
    return names


def resolve_focus(focus, edges):
    """설정의 `focus_band` 문자열을 실제 밴드 이름으로 정규화한다.

    🔴 **조용히 실패하면 안 된다.** `"4.4-6.0"`은 `%g` 표기(`"4.4-6"`)와 문자열이
      달라 그대로 비교하면 **감시밴드 표본이 0으로 잡히고 INSUFFICIENT가 뜬다** —
      "표본이 안 쌓였다"와 "이름이 안 맞는다"가 같은 출력으로 보이는 것이 위험하다
      (계측 4원칙 ②의 문자열판). 매칭 실패는 `None`을 돌려 호출부가 사유를 남긴다.
    """
    names = all_band_names(edges)
    if focus in names:
        return focus
    # `4.4-6.0` ↔ `4.4-6` 같은 표기 차이를 숫자로 흡수한다.
    try:
        parts = [float(x) for x in str(focus).replace(">=", "").replace("<", "").split("-")]
    except (ValueError, TypeError):
        return None
    for nm in names:
        try:
            cand = [float(x) for x in nm.replace(">=", "").replace("<", "").split("-")]
        except ValueError:
            continue
        if len(cand) == len(parts) and all(abs(a - b) < 1e-9 for a, b in zip(cand, parts)):
            return nm
    return None


# ── 통계 ────────────────────────────────────────────────────────────────────

def _sign_test_p(diffs):
    """일자단위 부호검정(양측). 0은 표본에서 제외.

    ⚠ `math.comb`은 Python 3.8+ 전용이고 런타임은 py37_32다 — `factorial`로 센다
      (473차에 같은 함정을 한 번 밟았다).
    """
    pos = sum(1 for d in diffs if d > 0)
    neg = sum(1 for d in diffs if d < 0)
    n = pos + neg
    if n == 0:
        return None, 0, 0
    import math
    k = min(pos, neg)
    if n > 300:
        mu, sd = n / 2.0, math.sqrt(n / 4.0)
        z = (abs(k - mu) - 0.5) / sd if sd > 0 else 0.0
        return min(1.0, math.erfc(z / math.sqrt(2.0))), pos, neg
    tail = sum(math.factorial(n) // (math.factorial(i) * math.factorial(n - i))
               for i in range(0, k + 1))
    return min(1.0, 2.0 * tail / float(2 ** n)), pos, neg


def _mean(xs):
    return (sum(xs) / len(xs)) if xs else None


def _krw(v, sign=False):
    """천단위 콤마 포맷.

    🔴 `%`-포매팅의 콤마 플래그(`"%,.0f" % v`)는 **py3.7에서 ValueError**다
      (`str.format`/f-string 전용 기능). 런타임이 py37_32이므로 여기서 막는다.
      게다가 이런 줄은 **표본이 사전등록 문턱을 넘은 뒤에야 실행**되므로, 그대로
      두면 몇 달 뒤 판정이 처음 나오는 그날 터진다 — 473차 `math.comb`과 같은
      지연 폭발 패턴이고, 431차 대시보드 `%` 사고와도 같은 클래스다.
    """
    if v is None:
        return "N/A"
    return ("{:+,.0f}" if sign else "{:,.0f}").format(v)


# ── 판정 ────────────────────────────────────────────────────────────────────

def compute():
    cfg = _cfg()
    if not cfg.get("enabled", False):
        return {"available": False, "reason": "채널 비활성"}

    edges = [float(x) for x in (cfg.get("band_edges") or [])]
    if len(edges) < 2:
        return {"available": False, "reason": "band_edges 사전등록 누락"}
    raw_focus = str(cfg.get("focus_band") or "")
    focus = resolve_focus(raw_focus, edges)
    if focus is None:
        # 큰 소리로 실패한다 — 표본 미달과 구분되지 않으면 몇 주를 헛본다.
        return {"available": False,
                "reason": ("focus_band %r 가 band_edges %s에서 생성되는 밴드 %s 중 어느 것과도 "
                           "맞지 않는다 — 사전등록 불일치"
                           % (raw_focus, edges, all_band_names(edges)))}

    tf = _tf_map(cfg)
    if not tf:
        return {"available": False,
                "reason": "ensemble_decisions.features에서 threshold_feasibility를 얻지 못함"}
    positions = _merged_positions(cfg)
    if not positions:
        return {"available": False, "reason": "병합 포지션 0건"}

    unmatched = 0
    for p in positions:
        v = tf.get(p["entry_ts"]) or tf.get(p["entry_ts"][:16] + ":00")
        if v is None:
            p["band"] = None
            unmatched += 1
            continue
        p["tf"] = v
        p["band"], p["order"] = band_of(v, edges)
        p["day"] = p["entry_ts"][:10]
        p["ppc"] = p["pnl"] / max(p["qty_final"], 1)

    live = [p for p in positions if p.get("band")]
    agg = defaultdict(lambda: {"ppc": [], "days": set(), "order": 0.0})
    for p in live:
        a = agg[p["band"]]
        a["ppc"].append(p["ppc"])
        a["days"].add(p["day"])
        a["order"] = p["order"]

    bands = []
    for name in sorted(agg, key=lambda n: agg[n]["order"]):
        v = agg[name]["ppc"]
        bands.append({
            "band": name, "n": len(v), "days": len(agg[name]["days"]),
            "mean_krw": _mean(v),
            "win_rate": (sum(1 for x in v if x > 0) / len(v)) if v else None,
        })

    res = {
        "available": True,
        "band_edges": edges,
        "focus_band": focus,
        "n_positions": len(live),
        "unmatched_positions": unmatched,
        "bands": bands,
    }

    # ── 사전등록 표본 관문 (감시 밴드 기준) ──────────────────────────────────
    tgt = [p for p in live if p["band"] == focus]
    rest = [p for p in live if p["band"] != focus]
    res["n_focus"] = len(tgt)
    res["days_focus"] = len({p["day"] for p in tgt})

    if len(tgt) < int(cfg.get("min_samples", 20)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = ("감시밴드(%s) 포지션 %d < min_samples %d"
                         % (focus, len(tgt), cfg.get("min_samples")))
        res["accrual"] = _accrual(tgt, tf, cfg)
        return res
    if res["days_focus"] < int(cfg.get("min_days", 6)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = ("감시밴드(%s) 거래일 %d < min_days %d"
                         % (focus, res["days_focus"], cfg.get("min_days")))
        res["accrual"] = _accrual(tgt, tf, cfg)
        return res

    # ── 일자단위 대조 (①②) ─────────────────────────────────────────────────
    by_t, by_r = defaultdict(list), defaultdict(list)
    for p in tgt:
        by_t[p["day"]].append(p["ppc"])
    for p in rest:
        by_r[p["day"]].append(p["ppc"])
    paired = [(d, _mean(by_t[d]) - _mean(by_r[d]))
              for d in sorted(set(by_t) & set(by_r))]
    res["paired_days"] = len(paired)
    if len(paired) < int(cfg.get("min_days", 6)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = ("두 군 공존 거래일 %d < min_days %d — 일자단위 대조 불가"
                         % (len(paired), cfg.get("min_days")))
        return res

    diffs = [d for _, d in paired]
    p_val, n_pos, n_neg = _sign_test_p(diffs)
    res["day_mean_diff_krw"] = _mean(diffs)
    res["sign_test_p"] = p_val
    res["days_focus_better"], res["days_focus_worse"] = n_pos, n_neg

    fb = next((b for b in bands if b["band"] == focus), None)
    rest_ppc = [p["ppc"] for p in rest]
    res["focus_win_rate"] = fb["win_rate"] if fb else None
    res["rest_win_rate"] = ((sum(1 for x in rest_ppc if x > 0) / len(rest_ppc))
                            if rest_ppc else None)
    res["win_rate_gap_pp"] = (
        100.0 * (res["rest_win_rate"] - res["focus_win_rate"])
        if (res["focus_win_rate"] is not None and res["rest_win_rate"] is not None)
        else None)

    # ── 이상치 분해 (③) ─────────────────────────────────────────────────────
    k = int(cfg.get("drop_worst_days", 1))
    ordered = sorted(paired, key=lambda x: abs(x[1]), reverse=True)
    res["dropped_days"] = [d for d, _ in ordered[:k]]
    tvals = [d for _, d in ordered[k:]]
    res["day_mean_diff_trimmed_krw"] = _mean(tvals)

    # ── 부호 일관성 (⑤) ─────────────────────────────────────────────────────
    half = len(paired) // 2
    res["first_half_diff_krw"] = _mean([d for _, d in paired[:half]]) if half else None
    res["second_half_diff_krw"] = _mean([d for _, d in paired[half:]]) if half else None

    # ── 사전등록 판정 ───────────────────────────────────────────────────────
    gap_thr = float(cfg.get("pnl_gap_krw", 200_000))
    wr_thr = float(cfg.get("win_rate_gap_pp", 15.0))
    alpha = float(cfg.get("alpha", 0.05))
    md, td = res["day_mean_diff_krw"], res["day_mean_diff_trimmed_krw"]

    worse = md is not None and md < 0
    big = md is not None and abs(md) >= gap_thr
    wr_big = res["win_rate_gap_pp"] is not None and res["win_rate_gap_pp"] >= wr_thr
    sig = p_val is not None and p_val < alpha
    holds = (td is not None and md is not None and (td < 0) == (md < 0))

    reasons = []
    if worse and big and wr_big and sig and holds:
        res["verdict"] = "BAND_ANOMALY"
        reasons.append("일자평균 격차 %s원(>=%s) · 승률격차 %.1f%%p(>=%.1f) · "
                       "p=%.4f<%.2f · 최악 %d일 제거 후 부호 유지"
                       % (_krw(md, sign=True), _krw(gap_thr),
                          res["win_rate_gap_pp"], wr_thr, p_val, alpha, k))
        reasons.append("→ B2 경계 재검토를 주간회의에 상정할 것 (자동 조정 아님)")
    else:
        res["verdict"] = "BAND_UNIFORM"
        if not worse:
            reasons.append("감시밴드가 열위가 아니다")
        if not big:
            reasons.append("|손익격차| %s < %s" % (_krw(abs(md or 0)), _krw(gap_thr)))
        if not wr_big:
            reasons.append("승률격차 %s < %.1f%%p"
                           % (("%.1f" % res["win_rate_gap_pp"])
                              if res["win_rate_gap_pp"] is not None else "N/A", wr_thr))
        if not sig:
            reasons.append("부호검정 p=%s >= %.2f"
                           % (("%.4f" % p_val) if p_val is not None else "N/A", alpha))
        if not holds:
            reasons.append("최악 %d일 제거 시 부호 반전 — 이상치 의존" % k)
    res["reason"] = " / ".join(reasons)

    # 검정력 주석 — **판정을 바꾸지 않는다.** 사전등록 기준은 그대로 적용하되,
    # `BAND_UNIFORM`이 "이상 없음이 입증됐다"로 읽히는 것을 막는다.
    # 표본이 문턱을 겨우 넘긴 구간에서는 진짜 효과도 놓칠 수 있다(2종 오류).
    if res["verdict"] == "BAND_UNIFORM" and len(tgt) < 2 * int(cfg.get("min_samples", 20)):
        res["low_power"] = True
        res["power_note"] = (
            "⚠ 표본 %d(문턱 %d의 %.1f배) — 검정력이 낮다. BAND_UNIFORM은 "
            "'사전등록 기준에서 이상이 잡히지 않았다'이지 '이상이 없다'가 아니다. "
            "표본이 더 쌓이면 재판정할 것."
            % (len(tgt), cfg.get("min_samples"), len(tgt) / float(cfg.get("min_samples", 20))))
    else:
        res["low_power"] = False
    return res


def _accrual(tgt, tf, cfg):
    """감시밴드 표본 적립 속도와 도달 ETA — "쌓이면 본다"를 검증 가능하게 만든다."""
    need = int(cfg.get("min_samples", 20))
    days = len({ts[:10] for ts in tf})
    n = len(tgt)
    if days <= 0:
        return {"trading_days_observed": 0}
    rate = n / float(days)
    remain = max(0, need - n)
    eta = int(round(remain / rate)) if rate > 0 else None
    return {"trading_days_observed": days, "focus_per_trading_day": rate,
            "need_more": remain, "eta_trading_days": eta,
            "eta_months_approx": (round(eta / 21.0, 1) if eta is not None else None)}


def summarize(res):
    if not res.get("available"):
        return "[D9-B 라우팅밴드] 판정 불가 — %s" % res.get("reason", "?")
    return ("[D9-B 라우팅밴드] %s | 감시밴드 %s %d포지션/%d일 | %s"
            % (res["verdict"], res.get("focus_band"), res.get("n_focus", 0),
               res.get("days_focus", 0), res.get("reason", "")))


def main():
    guard_intraday("entry_band_watch")
    res = compute()
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    cfg = _cfg()
    print("=" * 74)
    print("D9-B — 진입 호라이즌 라우팅 밴드 성과")
    print("사전등록: VALIDATION_CAMPAIGN['%s'] (474차, 표본 도달 전 고정)" % CHANNEL)
    print("=" * 74)
    if not res.get("available"):
        print("판정 불가 — %s" % res.get("reason"))
        return 1

    print("밴드별 성과 (포지션 단위 · 계약당 순손익)   경계=%s" % res["band_edges"])
    for b in res["bands"]:
        mark = "  ← 감시" if b["band"] == res["focus_band"] else ""
        print("  %-10s n=%3d  일수=%2d  승률 %5.1f%%  평균 %12s원%s"
              % (b["band"], b["n"], b["days"],
                 100.0 * (b["win_rate"] or 0), "{:,.0f}".format(b["mean_krw"] or 0), mark))
    print("  (tf 미매칭 %d 포지션은 제외 — 미측정)" % res["unmatched_positions"])

    acc = res.get("accrual") or {}
    if acc.get("eta_trading_days") is not None:
        print()
        print("표본 적립: %.3f건/거래일 · %d건 더 필요 · ETA ≈ %d거래일(약 %s개월)"
              % (acc["focus_per_trading_day"], acc["need_more"],
                 acc["eta_trading_days"], acc["eta_months_approx"]))

    if res["verdict"] != "INSUFFICIENT":
        print()
        print("일자단위 (1차 판정축)")
        print("  일평균 격차 %s원 · p=%s (감시우세 %d일 / 열위 %d일)"
              % (_krw(res["day_mean_diff_krw"], sign=True),
                 ("%.4f" % res["sign_test_p"]) if res.get("sign_test_p") is not None else "N/A",
                 res.get("days_focus_better", 0), res.get("days_focus_worse", 0)))
        print("  승률: 감시 %.1f%% vs 나머지 %.1f%% (격차 %.1f%%p)"
              % (100 * res["focus_win_rate"], 100 * res["rest_win_rate"],
                 res["win_rate_gap_pp"]))
        print("  최악 %s 제거 후 격차 %s원"
              % (res.get("dropped_days"),
                 _krw(res["day_mean_diff_trimmed_krw"] or 0, sign=True)))
        print("  전반 %s / 후반 %s"
              % (_krw(res.get("first_half_diff_krw") or 0, sign=True),
                 _krw(res.get("second_half_diff_krw") or 0, sign=True)))
    print()
    print("-" * 74)
    print("판정: %s" % res["verdict"])
    print("사유: %s" % res.get("reason", ""))
    if res.get("power_note"):
        print(res["power_note"])
    print("⚠ 처방 채널이 아니다 — 경계 변경은 매매 정책 변경이며 주간회의 안건이다.")
    print("-" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
