# -*- coding: utf-8 -*-
"""[MW0601 457차 / A3] 회전 비용 엣지 섀도 — **읽기 전용·계측 전용**.

## 이 스크립트가 답하는 질문

> 진입 시점에 **미리** 알 수 있는 정보로, 이 거래가 왕복 수수료를 넘길지
> 구분할 수 있는가?

## 🔴 먼저 정정 — 0811 점검리포트 §2 A3의 전제는 틀렸다

그 문서는 *"TP1 33% 부분청산이 레그를 2배로 만들어 수수료를 2배화한다"* 고 썼다.
**거짓이다.** 수수료는 `entry_price × quantity × pt_value × RATE × 2`
(utils/db_utils.py:101)로 **레그 수가 아니라 계약수에만 비례**한다.

    2026-08-11 실측 6레그        = 8,760원
    부분청산 없이 3레그(qty=2)   = 8,760원      → 차이 **0원**

부분청산은 비용 축에서 무해하다. 그러므로 이 채널은 부분청산을 재지 않는다.

## 진짜 문제 — 회전율 대비 엣지 부족

    왕복 손익분기 = 진입가 × RATE × 2 ≈ 966 × 0.000015 × 2 = 0.0290 pt/계약

2026-08-11은 gross +0.10pt를 6계약-청산으로 나눠 **0.017pt/계약** — 손익분기
미만이었다. 그래서 승률 66.7%(2승1패)인데 순손익 **-3,760원**이 됐다. 같은
패턴이 반복된다(08-10 8승2패 -244,067원 / 08-03 15승9패 -730,619원).

현행 게이트 어디에도 *"이 진입의 기대 이동폭이 왕복 비용을 넘는가"* 를 묻는 축이
없다. 그런데 `quantile_expected_pt`(MetaGate 분위회귀)는 **이미 기대 이동폭을 pt로
내고 있다** — 계산은 하는데 비용과 대조하지 않는다.

## 두 축

    축1 비용 커버율   포지션별 gross_pt/계약 > 왕복비용 인 비율  (사후 서술)
    축2 사전 예측력   진입 시점 quantile_expected_pt 가 축1을 예측하는가  ← **핵심**

축2가 없으면 축1은 "비용이 크더라"는 감상에 그친다. 게이트로 승격하려면 **진입
전에** 알 수 있어야 한다. 축2가 무정보(rho≈0)면 처방은 게이트 신설이 아니라
**분위회귀 재설계**다.

## 방법론

- **포지션 단위**로 집계한다(417차: `trades.quantity`는 청산 레그별 수량이라
  레그 단위 집계는 "계약수가 클수록 진다"는 인과 없는 상관을 만든다).
- **일자단위 독립관측**으로 검정한다(372차: 신호단위 n은 독립이 아니다).
- 실체결가만 쓴다 — 봉 재생·시뮬레이터를 쓰지 않으므로 [47] SUSPEND 대상이 아니다.

⚠ **계측 전용이다.** 사전등록 합격선은
`config/settings.py:VALIDATION_CAMPAIGN["cost_edge_watch"]`에 **수집 시작 전** 고정돼
있다. 사후 기준 변경 금지(캠페인 §9). 조치는 주간회의 승인을 거친다.

읽기 전용: trades.db · predictions.db. 출력: stdout + data/cost_edge/*.{json,md}
(런타임 산출물 — 커밋 금지).

실행:
    python scripts/cost_edge_shadow.py --days 30
"""
from __future__ import print_function

import argparse
import datetime
import json
import math
import os
import sys
from collections import OrderedDict, defaultdict

_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _utf8_console():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


from config.settings import (  # noqa: E402
    TRADES_DB, PREDICTIONS_DB, VALIDATION_CAMPAIGN, FUTURES_COMMISSION_RATE,
)

_CFG = VALIDATION_CAMPAIGN.get("cost_edge_watch", {})
MIN_SAMPLES = int(_CFG.get("min_samples", 40))
MIN_DAYS = int(_CFG.get("min_days", 10))
RHO_TH = float(_CFG.get("rho_threshold", 0.20))
T_TH = float(_CFG.get("t_threshold", 2.26))
GAP_SUPPORTS = float(_CFG.get("tercile_gap_pp_supports", 15.0))
GAP_REJECTS = float(_CFG.get("tercile_gap_pp_rejects", 5.0))
ENTRY_SOURCE = _CFG.get("entry_source", "SYSTEM_AUTO")

OUT_DIR = os.path.join(_ROOT, "data", "cost_edge")


# ── 통계 헬퍼 (scipy 비의존 — py37_32/py310_64 공용) ────────────────────────

def mean(xs):
    return sum(xs) / float(len(xs)) if xs else float("nan")


def stdev(xs):
    n = len(xs)
    if n < 2:
        return float("nan")
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def rankdata(xs):
    """동률은 평균 순위 (456차 Wave 4에서 고친 _spearman 동률 버그와 동일 규약)."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs, ys):
    if len(xs) < 3:
        return float("nan")
    rx, ry = rankdata(xs), rankdata(ys)
    mx, my = mean(rx), mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return num / (dx * dy) if dx > 0 and dy > 0 else float("nan")


def ttest_1samp(xs, mu=0.0):
    n = len(xs)
    if n < 2:
        return float("nan")
    sd = stdev(xs)
    if not sd or sd <= 0:
        return float("nan")
    return (mean(xs) - mu) / (sd / math.sqrt(n))


# ── 데이터 로드 — 포지션 단위 집계 ─────────────────────────────────────────

def load_positions(days):
    """trades.db 레그를 **포지션 단위**로 접는다.

    417차 교훈: `trades.quantity`는 청산 레그별 수량이다. 이익 포지션은 TP1/TP2/TP3로
    쪼개져 작은 수량 여러 행이 되고, 손실 포지션은 하드스톱 전량청산이라 큰 수량 한
    행이 된다 — 레그 단위로 세면 인과 없는 상관이 만들어진다.

    Returns: [ {date, entry_ts, direction, qty, gross_krw, commission_krw,
                net_krw, gross_pt_per_ct, breakeven_pt, covers_cost}, ... ]
    """
    from utils.analysis_db import connect_ro
    con = connect_ro(TRADES_DB)
    cur = con.cursor()
    cur.execute(
        "SELECT DISTINCT substr(entry_ts,1,10) d FROM trades "
        "WHERE entry_ts IS NOT NULL ORDER BY d DESC LIMIT ?", (int(days),)
    )
    dates = sorted(r[0] for r in cur.fetchall())
    if not dates:
        con.close()
        return [], []
    qmarks = ",".join("?" * len(dates))
    cur.execute(
        "SELECT entry_ts, direction, quantity, entry_price, pnl_pts, "
        "       gross_pnl_krw, commission_krw, net_pnl_krw, entry_source "
        "FROM trades WHERE substr(entry_ts,1,10) IN (%s)" % qmarks,
        tuple(dates),
    )
    legs = cur.fetchall()
    con.close()

    grouped = defaultdict(list)
    for r in legs:
        # entry_source 필터 — 수동 진입은 시스템 판단을 재는 표본이 아니다
        if ENTRY_SOURCE and r[8] and r[8] != ENTRY_SOURCE:
            continue
        grouped[(r[0], r[1])].append(r)

    out = []
    for (entry_ts, direction), rs in grouped.items():
        qty = sum(int(r[2] or 0) for r in rs)
        if qty <= 0:
            continue
        gross = sum(float(r[5] or 0.0) for r in rs)
        comm = sum(float(r[6] or 0.0) for r in rs)
        net = sum(float(r[7] or 0.0) for r in rs)
        # 계약 가중 평균 진입가 — 왕복 손익분기 산출용
        wsum = sum(float(r[3] or 0.0) * int(r[2] or 0) for r in rs)
        entry_px = wsum / qty if qty else 0.0
        gross_pt_per_ct = sum(float(r[4] or 0.0) * int(r[2] or 0) for r in rs) / float(qty)
        breakeven_pt = entry_px * FUTURES_COMMISSION_RATE * 2.0
        out.append({
            "date": entry_ts[:10], "entry_ts": entry_ts, "direction": direction,
            "qty": qty, "n_legs": len(rs),
            "gross_krw": gross, "commission_krw": comm, "net_krw": net,
            "entry_price": entry_px,
            "gross_pt_per_ct": gross_pt_per_ct,
            "breakeven_pt": breakeven_pt,
            "covers_cost": 1 if gross_pt_per_ct > breakeven_pt else 0,
        })
    out.sort(key=lambda d: d["entry_ts"])
    return out, dates


def attach_expected_pt(positions):
    """진입 분(minute)의 `quantile_expected_pt`를 붙인다 (축2 입력).

    ⚠ 진입 시점에 **이미 계산돼 있던** 값만 쓴다 — 사후 정보 없음.
    """
    if not positions:
        return 0
    from utils.analysis_db import connect_ro
    con = connect_ro(PREDICTIONS_DB)
    cur = con.cursor()
    minutes = sorted({p["entry_ts"][:16] for p in positions})
    got = {}
    CH = 400   # SQLite 변수 상한 회피
    for i in range(0, len(minutes), CH):
        chunk = minutes[i:i + CH]
        cur.execute(
            "SELECT substr(ts,1,16), quantile_expected_pt, meta_size_mult, grade "
            "FROM ensemble_decisions WHERE substr(ts,1,16) IN (%s)"
            % ",".join("?" * len(chunk)), tuple(chunk))
        for m, q, sz, g in cur.fetchall():
            got[m] = (q, sz, g)
    con.close()
    n_ok = 0
    for p in positions:
        q, sz, g = got.get(p["entry_ts"][:16], (None, None, None))
        p["expected_pt"] = None if q is None else float(q)
        p["meta_size_mult"] = None if sz is None else float(sz)
        p["grade"] = g
        if p["expected_pt"] is not None:
            n_ok += 1
    return n_ok


# ── 축1 · 축2 ─────────────────────────────────────────────────────────────

def axis1_coverage(positions):
    by_day = defaultdict(list)
    for p in positions:
        by_day[p["date"]].append(p)
    day_cov = []
    for d, ps in sorted(by_day.items()):
        day_cov.append((d, mean([p["covers_cost"] for p in ps]), len(ps)))
    return {
        "n_positions": len(positions),
        "n_days": len(by_day),
        "coverage_overall": mean([p["covers_cost"] for p in positions]),
        "coverage_by_day_mean": mean([c for _, c, _ in day_cov]),
        "gross_pt_median": (sorted(p["gross_pt_per_ct"] for p in positions)
                            [len(positions) // 2] if positions else float("nan")),
        "breakeven_pt_mean": mean([p["breakeven_pt"] for p in positions]),
        "net_krw_total": sum(p["net_krw"] for p in positions),
        "commission_krw_total": sum(p["commission_krw"] for p in positions),
        "gross_krw_total": sum(p["gross_krw"] for p in positions),
        "by_day": [{"date": d, "coverage": c, "n": n} for d, c, n in day_cov],
    }


def axis2_predictive(positions):
    """일자단위 스피어만 + 상·하위 3분위 커버율 격차."""
    usable = [p for p in positions if p.get("expected_pt") is not None]
    by_day = defaultdict(list)
    for p in usable:
        by_day[p["date"]].append(p)

    # 일자단위 rho — 하루 안에서 expected_pt ↔ covers_cost 순위상관
    day_rhos = []
    for d, ps in sorted(by_day.items()):
        if len(ps) < 3:
            continue
        r = spearman([p["expected_pt"] for p in ps], [p["covers_cost"] for p in ps])
        if r == r:
            day_rhos.append(r)

    # 3분위 격차 — 전 표본 기준(층화 없음. 층화는 표본 확보 후 별도)
    gap_pp = float("nan")
    lo_cov = hi_cov = float("nan")
    if len(usable) >= 6:
        srt = sorted(usable, key=lambda p: p["expected_pt"])
        k = len(srt) // 3
        lo, hi = srt[:k], srt[-k:]
        lo_cov = mean([p["covers_cost"] for p in lo]) * 100.0
        hi_cov = mean([p["covers_cost"] for p in hi]) * 100.0
        gap_pp = hi_cov - lo_cov

    return {
        "n_usable": len(usable),
        "n_days": len(day_rhos),
        "rho_mean": mean(day_rhos) if day_rhos else float("nan"),
        "rho_sd": stdev(day_rhos) if len(day_rhos) > 1 else float("nan"),
        "t": ttest_1samp(day_rhos, 0.0) if day_rhos else float("nan"),
        "tercile_low_coverage_pct": lo_cov,
        "tercile_high_coverage_pct": hi_cov,
        "tercile_gap_pp": gap_pp,
    }


def verdict(a1, a2, backfill=False):
    """사전등록 합격선으로 판정. **여기서 기준을 바꾸지 말 것** (캠페인 §9).

    `backfill=True`는 `data_start`(2026-08-12) **이전** 데이터를 포함한 실행이다.
    합격선은 이 스크립트를 쓰기 전에 settings.py에 먼저 박았지만, 그 순서를 제3자가
    검증할 수는 없다. 그래서 소급 구간의 결과는 **판정으로 승격하지 않고**
    BACKFILL_ADVISORY로 낮춰 표기한다 — 사전등록의 요점은 "결과를 보고 기준을
    고치지 않는 것"이고, 소급 실행을 판정으로 부르는 순간 그 보증이 사라진다.
    """
    if backfill:
        base_v, base_r = verdict(a1, a2, backfill=False)
        return "BACKFILL_ADVISORY", (
            "소급 구간 포함(data_start=%s 이전) — 참고용. 사전등록 판정은 %s 이후 "
            "데이터로만 낸다. [소급 산출: %s — %s]"
            % (_CFG.get("data_start", "?"), _CFG.get("data_start", "?"), base_v, base_r))
    if a1["n_positions"] < MIN_SAMPLES or a1["n_days"] < MIN_DAYS:
        return "INSUFFICIENT", (
            "표본 미달 — 포지션 %d/%d · 일수 %d/%d"
            % (a1["n_positions"], MIN_SAMPLES, a1["n_days"], MIN_DAYS))
    rho, t, gap = a2["rho_mean"], a2["t"], a2["tercile_gap_pp"]
    if rho != rho or t != t or gap != gap:
        return "INSUFFICIENT", "축2 산출 불가 (quantile_expected_pt 결측 또는 일수 부족)"
    if rho > RHO_TH and abs(t) > T_TH and gap > GAP_SUPPORTS:
        return "SUPPORTS_HYP", (
            "rho=%.3f>%.2f · |t|=%.2f>%.2f · 격차=%.1f%%p>%.1f — cost_edge 게이트를 "
            "주간회의 안건으로" % (rho, RHO_TH, abs(t), T_TH, gap, GAP_SUPPORTS))
    if abs(t) <= T_TH and gap < GAP_REJECTS:
        return "REJECTS_HYP", (
            "rho=%.3f (|t|=%.2f, 0 배제 실패) · 격차=%.1f%%p<%.1f — quantile_expected_pt는 "
            "비용 커버를 예측하지 못한다. 처방은 게이트 신설이 아니라 **분위회귀 재설계**"
            % (rho, abs(t), gap, GAP_REJECTS))
    return "PASS", (
        "rho=%.3f |t|=%.2f 격차=%.1f%%p — 어느 쪽 문턱도 넘지 않음. 현행 유지, 관측 계속"
        % (rho, abs(t), gap))


# ── 리포트 ────────────────────────────────────────────────────────────────

def render(dates, a1, a2, v, reason):
    L = []
    W = L.append
    W("# 회전 비용 엣지 섀도 (457차 A3)\n")
    W("- 구간: %s ~ %s (%d거래일)" % (dates[0], dates[-1], len(dates)))
    W("- 사전등록: `VALIDATION_CAMPAIGN[\"cost_edge_watch\"]` "
      "(min_samples=%d, min_days=%d, rho>%.2f, |t|>%.2f, 격차>%.1f%%p)"
      % (MIN_SAMPLES, MIN_DAYS, RHO_TH, T_TH, GAP_SUPPORTS))
    W("- 포지션 단위 집계(417차) · 일자단위 독립관측(372차) · 실체결가만 사용\n")
    W("> 🔴 **정정**: 0811 리포트 §2 A3의 *\"부분청산이 수수료를 2배화한다\"* 는 거짓이다. "
      "수수료는 계약수에만 비례하며 레그 분할과 무관하다(실측 차이 0원). "
      "이 채널은 부분청산이 아니라 **회전율 대비 엣지**를 잰다.\n")

    W("## 축1 — 비용 커버율 (사후 서술)\n")
    W("| 항목 | 값 |")
    W("|---|---|")
    W("| 포지션 수 | %d |" % a1["n_positions"])
    W("| 거래일 | %d |" % a1["n_days"])
    W("| 왕복 손익분기 (평균) | %.4f pt/계약 |" % a1["breakeven_pt_mean"])
    W("| gross 중앙값 | %.4f pt/계약 |" % a1["gross_pt_median"])
    W("| **비용 커버율** | **%.1f%%** (일자평균 %.1f%%) |"
      % (a1["coverage_overall"] * 100.0, a1["coverage_by_day_mean"] * 100.0))
    # ⚠ %-포맷은 천단위 쉼표를 지원하지 않는다 — str.format을 쓴다
    W("| gross 합계 | {:+,.0f}원 |".format(a1["gross_krw_total"]))
    W("| 수수료 합계 | {:,.0f}원 |".format(a1["commission_krw_total"]))
    W("| **순손익 합계** | **{:+,.0f}원** |".format(a1["net_krw_total"]))
    W("")

    W("## 축2 — 사전 예측력 (`quantile_expected_pt`) ← 핵심\n")
    W("| 항목 | 값 |")
    W("|---|---|")
    W("| 사용 가능 포지션 | %d / %d |" % (a2["n_usable"], a1["n_positions"]))
    W("| 일자단위 rho 평균 | %.4f (sd %.4f, %d일) |"
      % (a2["rho_mean"], a2["rho_sd"], a2["n_days"]))
    W("| t (rho=0 대비) | %.2f |" % a2["t"])
    W("| 하위 3분위 커버율 | %.1f%% |" % a2["tercile_low_coverage_pct"])
    W("| 상위 3분위 커버율 | %.1f%% |" % a2["tercile_high_coverage_pct"])
    W("| **격차** | **%.1f%%p** |" % a2["tercile_gap_pp"])
    W("")

    W("## 판정\n")
    W("**%s** — %s\n" % (v, reason))
    W("> ⚠ 계측 전용. 사전등록 합격선은 수집 전 고정됐고 사후 변경 금지(캠페인 §9). "
      "조치는 주간회의 승인을 거친다.")
    return "\n".join(L)


def main():
    _utf8_console()
    ap = argparse.ArgumentParser(
        description="회전 비용 엣지 섀도 (457차 A3, 읽기 전용·계측 전용)")
    ap.add_argument("--days", type=int, default=30, help="최근 N거래일 (기본 30)")
    ap.add_argument("--backfill", action="store_true",
                    help="data_start 이전 구간도 포함 (판정은 BACKFILL_ADVISORY로 강등)")
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args()

    from utils.analysis_db import guard_intraday
    guard_intraday("cost_edge_shadow")

    positions, dates = load_positions(args.days)
    if not positions:
        print("포지션이 없다 — trades.db 확인 필요")
        return 1

    # 사전등록 구간 필터 — 기본은 data_start 이후만 판정한다(캠페인 §9).
    _ds = _CFG.get("data_start") or ""
    _backfill = False
    if _ds and not args.backfill:
        _before = len(positions)
        positions = [p for p in positions if p["date"] >= _ds]
        dates = [d for d in dates if d >= _ds]
        if _before != len(positions):
            print("사전등록 구간 필터: %d → %d포지션 (data_start=%s 이후만)"
                  % (_before, len(positions), _ds))
        if not positions:
            print("사전등록 구간(%s 이후) 표본 0 — 아직 수집 전이다. "
                  "소급 참고치가 필요하면 --backfill" % _ds)
            return 0
    elif _ds and args.backfill:
        _backfill = any(d < _ds for d in dates)

    n_q = attach_expected_pt(positions)
    print("포지션 %d건, %d거래일 (%s ~ %s) · quantile_expected_pt 확보 %d건"
          % (len(positions), len(dates), dates[0], dates[-1], n_q))

    a1 = axis1_coverage(positions)
    a2 = axis2_predictive(positions)
    v, reason = verdict(a1, a2, backfill=_backfill)

    md = render(dates, a1, a2, v, reason)
    print()
    print(md)

    if not args.no_save:
        stamp = datetime.date.today().strftime("%Y%m%d")
        try:
            os.makedirs(OUT_DIR)
        except OSError:
            pass
        base = os.path.join(OUT_DIR, "cost_edge_%s" % stamp)
        with open(base + ".md", "w", encoding="utf-8") as fh:
            fh.write(md)
        with open(base + ".json", "w", encoding="utf-8") as fh:
            json.dump({"dates": dates, "axis1": a1, "axis2": a2,
                       "verdict": v, "reason": reason}, fh,
                      ensure_ascii=False, indent=2)
        print("\n저장: %s.{md,json}" % base)
    return 0


if __name__ == "__main__":
    sys.exit(main())
