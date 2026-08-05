# scripts/entry_context_shadow.py
"""[MW0601 436차, 캠페인 47] 진입 맥락(context)별 손익 — 읽기 전용 오프라인 재생.

무엇을 묻는가
--------------
0805 일일점검이 사후 슬라이스로 발견한 "나빠 보이는 진입 맥락" 3종이 **진짜 효과인지
포킹 패스 인공물인지**를 OOS로 판정한다.

    S1  09시대 진입
    S2  직전 청산 후 **반대방향** 재진입
    S3  직전 청산 후 **동일방향 5분 이내** 재진입

⚠⚠ 이 채널의 존재 이유 자체가 "그 관찰을 믿지 말자"다 — 아래를 반드시 먼저 읽을 것.

왜 그대로 쓰면 안 되는가 (등록 근거)
------------------------------------
**① 사후 슬라이스 + 다중비교.** 0805 점검에서 진입 맥락을 여러 축(재진입 간격 4구간,
동일/반대 방향, 직전 승/패, 시간대 6구간)으로 갈라본 뒤 **나빠 보이는 것만 골라**
보고했다. 가지 수를 세면 최소 15갈래 이상이고, 그중 셋을 고른 것이므로 개별 p-value를
그대로 읽으면 안 된다(garden of forking paths).

**② 관측 창을 바꾸면 부호가 뒤집힌다** — 실측:

    슬라이스        2026-07-01~(원 보고)   2026-06-10~
    S1 09시대            -23.90pt            **+31.99pt**
    S2 반대방향          -45.18pt              -34.35pt
    S3 동일<=5분         -15.78pt            **+37.29pt**

**③ 지표를 계약당으로 바꿔도 크기가 달라진다.** 원 보고는 포지션합 pt였는데 그건
계약수가 섞인 값이다(417차 교훈 — 대형 계약수 구간 06-10~07-10이 통째로 들어간다).
계약당으로 정규화하면 S2는 -0.000(보완 +0.743)로 **효과가 사실상 사라진다.**

**④ 원 보고의 해석 하나가 창 의존이었다.** "S2는 승률이 평균 이상인데 손실만 크다 —
방향이 아니라 페이오프 문제"라고 적었으나, 06-10~ 기준으로는 승률 51.5% vs 보완
57.3%로 **오히려 낮다.** 그 해석은 07-01~ 창에서만 성립한다.

→ 그래서 이 채널은 **주 지표를 계약당 pt로 고정**하고, **방향 축(승률)과 페이오프 축을
   분리 계측**하며, **다중비교 보정 후에만** 판정한다. 창 민감도는 항상 병기한다.

무엇을 결론으로 삼을 수 있나 / 없나
-----------------------------------
- ⚠⚠ **사전등록 정직성 고지**: 슬라이스 3종은 0805에 **이미 관측한 뒤** 고른 것이다.
  전체표본 결과는 정의상 in-sample이며 **그 자체로는 판정 근거가 아니다.**
  이 채널의 가치는 `oos_start` 이후 신규분에 있다([23]·[46]과 동일 구조).
- 313차 원칙: min_days 미달이면 판정하지 않는다.
- ⚠ **FAIL이 나와도 "진입 차단"은 처방이 아니다.** 두 가지 이유다 —
  (a) 427·428차가 방향 축이 무작위와 구분되지 않음을 확정했으므로 진입 필터의
      기대값은 보장되지 않는다(430차 [44] 주석과 동일 논리),
  (b) 감사 §2-2 ③ "차단형 게이트는 이미 충분히 많다".
  처방은 **사이징 또는 집행(청산) 축**에서 찾을 것 — 425차·417차와 같은 방향이다.

통계 설계
---------
- 주 지표: **계약당 pt**(`sum(pnl_pts) / entry_qty`) — 사이징 무관.
- 검정: 슬라이스 vs 보완집합 평균 차이의 **순열검정**(permutation test).
  표본이 얇고 꼬리가 두꺼워 정규 근사가 위험하고, scipy 의존도 피한다.
  ⚠ numpy BLAS는 이 PC에서 파손 상태라(432차 후속) 행렬연산을 쓰지 않는다 — 순수 파이썬.
- 다중비교: **Bonferroni**(alpha / 슬라이스 수). 등록 슬라이스는 3개지만 실제 탐색
  가지는 그보다 많았으므로 이 보정은 **하한**이다 — 통과해도 "약한 증거"로 읽을 것.
- 판정보조: drop-worst(최악 1건 제거) · 일자단위 부호 일관성 · 창 민감도.

실행:
    py310_64\\python.exe scripts/entry_context_shadow.py [--since 2026-06-10]
"""
from __future__ import annotations

import argparse
import collections
import datetime
import os
import random
import statistics
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import TRADES_DB, VALIDATION_CAMPAIGN  # noqa: E402

_CR = VALIDATION_CAMPAIGN.get("entry_context_shadow", {})
_TS_FMT = "%Y-%m-%d %H:%M:%S"


def _load_positions(since: str) -> list:
    """부분청산 레그를 진입 단위로 병합하고 재진입 맥락을 붙인다(417차 교훈)."""
    with sqlite3.connect(TRADES_DB) as c:
        c.row_factory = sqlite3.Row
        rows = [dict(r) for r in c.execute(
            "SELECT entry_ts, exit_ts, direction, entry_qty, pnl_pts "
            "FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL "
            "AND (entry_source IS NULL OR entry_source != 'OPERATOR_MANUAL') "
            "ORDER BY entry_ts", (since,))]
    agg = collections.OrderedDict()
    for r in rows:
        agg.setdefault((r["entry_ts"], r["direction"]), []).append(r)

    P = []
    for (ets, dirn), legs in agg.items():
        qty = int(legs[0]["entry_qty"] or 1) or 1
        P.append({
            "ets": ets, "day": ets[:10], "hour": ets[11:13], "dirn": dirn,
            "qty": qty, "xts": max(x["exit_ts"] for x in legs),
            "pt_pc": sum(float(x["pnl_pts"] or 0) for x in legs) / qty,
        })

    def _t(s):
        return datetime.datetime.strptime(str(s)[:19], _TS_FMT)

    for i, p in enumerate(P):
        p["gap_min"], p["same_dir"] = None, None
        if i > 0 and P[i - 1]["day"] == p["day"]:
            try:
                p["gap_min"] = (_t(p["ets"]) - _t(P[i - 1]["xts"])).total_seconds() / 60.0
            except ValueError:
                continue
            p["same_dir"] = (P[i - 1]["dirn"] == p["dirn"])
    return P


# ── 슬라이스 정의 (사전등록 — 관측 후 정의를 바꾸지 말 것) ───────────────
def _slice_members(name: str, P: list) -> list:
    if name == "S1_hour09":
        return [x for x in P if x["hour"] == "09"]
    if name == "S2_reverse_reentry":
        return [x for x in P if x["same_dir"] is False]
    if name == "S3_same_dir_le5min":
        return [x for x in P if x["same_dir"] is True
                and x["gap_min"] is not None and x["gap_min"] <= 5]
    raise ValueError("unknown slice: %s" % name)


def _perm_p(a: list, b: list, iters: int, seed: int) -> float:
    """평균 차이(a-b)의 양측 순열검정 p-value. 순수 파이썬(BLAS 미사용)."""
    if len(a) < 2 or len(b) < 2:
        return 1.0
    obs = abs(statistics.mean(a) - statistics.mean(b))
    pool = list(a) + list(b)
    na = len(a)
    rnd = random.Random(seed)
    hit = 0
    for _ in range(iters):
        rnd.shuffle(pool)
        d = abs(statistics.mean(pool[:na]) - statistics.mean(pool[na:]))
        if d >= obs - 1e-12:
            hit += 1
    return (hit + 1.0) / (iters + 1.0)


def _describe(v: list) -> dict:
    if not v:
        return {}
    pts = [x["pt_pc"] for x in v]
    wins = [p for p in pts if p > 0]
    loss = [p for p in pts if p <= 0]
    wm = statistics.mean(wins) if wins else 0.0
    lm = statistics.mean(loss) if loss else 0.0
    return {
        "n": len(pts), "n_days": len(set(x["day"] for x in v)),
        "win_rate": round(len(wins) / float(len(pts)), 4),
        "mean_pt": round(statistics.mean(pts), 4),
        "sum_pt": round(sum(pts), 4),
        "win_mean_pt": round(wm, 4), "loss_mean_pt": round(lm, 4),
        # 페이오프 축 — 사용자가 제기한 "방향이 아니라 페이오프" 가설의 계측지점
        "payoff_ratio": round(wm / abs(lm), 4) if lm else None,
    }


def _eval_slice(name: str, P: list, iters: int, seed: int) -> dict:
    S = _slice_members(name, P)
    ids = set(id(x) for x in S)
    C = [x for x in P if id(x) not in ids]
    if not S or not C:
        return {"name": name, "insufficient": True, "n": len(S)}
    a = [x["pt_pc"] for x in S]
    b = [x["pt_pc"] for x in C]
    out = {"name": name, "slice": _describe(S), "complement": _describe(C)}
    out["delta_mean_pt"] = round(statistics.mean(a) - statistics.mean(b), 4)
    out["delta_win_rate"] = round(out["slice"]["win_rate"] - out["complement"]["win_rate"], 4)
    _ps, _pc = out["slice"].get("payoff_ratio"), out["complement"].get("payoff_ratio")
    out["delta_payoff"] = (round(_ps - _pc, 4) if (_ps is not None and _pc is not None) else None)
    out["p_perm"] = round(_perm_p(a, b, iters, seed), 5)
    # 판정보조 ① drop-worst — 슬라이스 최악 1건을 빼도 차이가 유지되는가
    if len(a) > 1:
        a2 = sorted(a)[1:]
        out["delta_mean_drop_worst"] = round(statistics.mean(a2) - statistics.mean(b), 4)
    else:
        out["delta_mean_drop_worst"] = None
    # 판정보조 ② 일자단위 — 슬라이스 포함일의 계약당 합이 음수인 날 비율
    dd = collections.defaultdict(float)
    for x in S:
        dd[x["day"]] += x["pt_pc"]
    neg = sum(1 for v in dd.values() if v < 0)
    out["days"] = len(dd)
    out["neg_day_share"] = round(neg / float(len(dd)), 4) if dd else None
    return out


def compute(since: str = "2026-06-10") -> dict:
    P = _load_positions(since)
    names = list(_CR.get("slices", []))
    iters = int(_CR.get("perm_iters", 20000))
    seed = int(_CR.get("perm_seed", 20260805))
    oos_start = str(_CR.get("oos_start", "")) or None

    full = {n: _eval_slice(n, P, iters, seed) for n in names}
    P_oos = [x for x in P if oos_start and x["day"] >= oos_start]
    oos = {n: _eval_slice(n, P_oos, iters, seed) for n in names} if P_oos else {}

    # 창 민감도 — 이 채널의 존재 이유(부호가 창에 따라 뒤집혔다)를 항상 보이게 한다.
    sens = {}
    for alt in list(_CR.get("sensitivity_windows", [])):
        Pa = [x for x in P if x["day"] >= alt]
        if not Pa:
            continue
        sens[alt] = {n: (_eval_slice(n, Pa, 2000, seed).get("delta_mean_pt")) for n in names}

    return {
        "since": since, "n_positions": len(P),
        "n_days": len(set(x["day"] for x in P)),
        "n_oos": len(P_oos), "n_days_oos": len(set(x["day"] for x in P_oos)),
        "oos_start": oos_start, "slices": names,
        "perm_iters": iters, "per_slice": full, "per_slice_oos": oos,
        "sensitivity": sens,
    }


def summarize(out: dict) -> dict:
    """판정 — 사전등록 기준 그대로. 여기서 기준을 바꾸지 말 것(§9).

    PASS(조치 불요): OOS에서 Bonferroni 보정 후 유의한 슬라이스가 없다.
    FAIL(처방 검토): 보정 후 유의 + drop-worst 생존(부호 유지) + 일자단위 과반 음수.
      → 즉시 조치 아님, 주간회의 수동 결정. **진입 차단은 처방 후보가 아니다**(위 참조).
    """
    min_n = int(_CR.get("min_samples", 25))
    min_d = int(_CR.get("min_days", 10))
    alpha = float(_CR.get("alpha", 0.05))
    names = out.get("slices", [])
    k = max(1, len(names))
    alpha_adj = alpha / k

    base = {
        "min_samples": min_n, "min_days": min_d,
        "alpha": alpha, "alpha_bonferroni": round(alpha_adj, 5), "family_size": k,
        "n_oos": out.get("n_oos", 0), "n_days_oos": out.get("n_days_oos", 0),
        "n_positions": out.get("n_positions", 0), "n_days": out.get("n_days", 0),
        "oos_start": out.get("oos_start"), "slices": names,
        "per_slice": out.get("per_slice") or {},
        "per_slice_oos": out.get("per_slice_oos") or {},
        "sensitivity": out.get("sensitivity") or {},
        "perm_iters": out.get("perm_iters"),
    }

    def done(v, r, flagged):
        d = dict(base)
        d.update({"verdict": v, "reason": r, "flagged": flagged})
        return d

    pv = out.get("per_slice_oos") or {}
    if not pv:
        return done("INSUFFICIENT", "OOS 표본 없음 (%s 이후 진입 0건)"
                    % (out.get("oos_start") or "미설정"), [])

    ready = [n for n in names
             if pv.get(n, {}).get("slice", {}).get("n", 0) >= min_n
             and pv.get(n, {}).get("days", 0) >= min_d]
    if not ready:
        return done("INSUFFICIENT",
                    "OOS 표본 부족 — 슬라이스별 n>=%d 및 거래일>=%d를 만족하는 것이 없다 "
                    "(전체표본 결과는 사후 슬라이스라 판정 근거가 아니다)" % (min_n, min_d),
                    [])

    flagged = []
    for n in ready:
        v = pv[n]
        if (v.get("p_perm", 1.0) <= alpha_adj
                and (v.get("delta_mean_pt") or 0) < 0
                and (v.get("delta_mean_drop_worst") or 0) < 0
                and (v.get("neg_day_share") or 0) > 0.5):
            flagged.append(n)
    return done("FAIL" if flagged else "PASS",
                ("보정 후 유의 + drop-worst 생존 + 일자 과반 음수: %s" % ", ".join(flagged))
                if flagged else
                ("판정 가능 슬라이스 %d개 중 Bonferroni(α=%.5f) 통과 없음"
                 % (len(ready), alpha_adj)),
                flagged)


def _tbl(title, pv, names):
    print(title)
    if not pv:
        print("  (표본 없음)")
        return
    print("  %-22s %5s %6s %9s %9s %9s %9s %8s %8s"
          % ("슬라이스", "n", "거래일", "승률Δ", "평균ptΔ", "drop-worst", "페이오프Δ",
             "p(순열)", "음수일%"))
    for n in names:
        v = pv.get(n) or {}
        if v.get("insufficient") or not v.get("slice"):
            print("  %-22s (표본 없음)" % n)
            continue
        s = v["slice"]
        print("  %-22s %5d %6d %+8.1f%% %+9.3f %+9s %+9s %8.4f %7.0f%%"
              % (n, s["n"], v.get("days", 0), v["delta_win_rate"] * 100 if v.get("delta_win_rate") is not None else 0,
                 v.get("delta_mean_pt", 0),
                 ("%.3f" % v["delta_mean_drop_worst"]) if v.get("delta_mean_drop_worst") is not None else "—",
                 ("%.2f" % v["delta_payoff"]) if v.get("delta_payoff") is not None else "—",
                 v.get("p_perm", 1.0), (v.get("neg_day_share") or 0) * 100))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-06-10")
    args = ap.parse_args()
    out = compute(args.since)
    s = summarize(out)

    print("=" * 104)
    print("[47] 진입 맥락별 손익   기간 %s~   순열 %d회" % (args.since, out["perm_iters"]))
    print("사전등록 기준: config/settings.py VALIDATION_CAMPAIGN['entry_context_shadow']")
    print("=" * 104)
    print("포지션 %d건 / %d거래일   주 지표 = 계약당 pt (사이징 무관)"
          % (out["n_positions"], out["n_days"]))
    print("Bonferroni: α=%.2f / %d슬라이스 = %.5f" % (s["alpha"], s["family_size"], s["alpha_bonferroni"]))
    print()
    _tbl("── 전체표본 (⚠ 사후 슬라이스 — 판정 근거 아님) ──────────────────",
         out["per_slice"], out["slices"])
    print()
    _tbl("── OOS (%s 이후 — 판정 대상) ─────────────────────────"
         % (out["oos_start"] or "미설정"), out["per_slice_oos"], out["slices"])

    if out.get("sensitivity"):
        print()
        print("── 창 민감도 (평균ptΔ) — 부호가 창에 따라 뒤집히는지 ───────────")
        print("  %-22s %s" % ("슬라이스", "  ".join("%-11s" % w for w in sorted(out["sensitivity"]))))
        for n in out["slices"]:
            vals = []
            for w in sorted(out["sensitivity"]):
                v = out["sensitivity"][w].get(n)
                vals.append("%-11s" % (("%+.3f" % v) if v is not None else "—"))
            print("  %-22s %s" % (n, "  ".join(vals)))

    print()
    print("판정: %s — %s" % (s["verdict"], s["reason"]))
    print()
    print("⚠ 슬라이스 3종은 0805에 **이미 관측한 뒤** 고른 것이다 — 전체표본은 정의상")
    print("  in-sample이며 판정 근거가 아니다. 사전등록 가치는 OOS에 있다.")
    print("⚠ Bonferroni는 등록 슬라이스 3개 기준이나 실제 탐색 가지는 더 많았다 —")
    print("  이 보정은 **하한**이다. 통과해도 '약한 증거'로 읽을 것.")
    print("⚠ FAIL이어도 **진입 차단은 처방이 아니다** — 방향 축은 무작위로 확정됐고")
    print("  (427·428차) 차단형 게이트는 이미 충분히 많다. 사이징/집행 축에서 찾을 것.")
    print("§9: 이 스크립트는 판정을 자동 적용하지 않는다. 적용은 주간회의 수동 결정.")


if __name__ == "__main__":
    main()
