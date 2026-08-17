# -*- coding: utf-8 -*-
"""[MW0601 473차 / F-8 Phase A] 극단 스프레드(>=20틱) 진입의 손익 — 소급 판정.

실전 전환 기준 ⑨(`TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED`)를 닫기 위한 채널.
사전등록 기준은 `config/settings.py:VALIDATION_CAMPAIGN["spread_extreme_watch"]`.

이 스크립트가 존재하는 이유
---------------------------
311차(2026-07-12)가 `spread_ticks >= 20` 차단을 제안하면서 *"실거래 표본 n=8~19라
노이즈가 커서 검증 못 함 — 섀도로 먼저 관찰"* 이라 미뤘고, 그 섀도
(`spread_extreme_shadow`)가 어디에도 저장되지 않아 한 달 넘게 판단이 멈춰 있었다.

그런데 **`spread_ticks` 원값은 처음부터 남아 있었다** — `ensemble_decisions.features`
(141키 JSON)에 매분. 불리언만 없었을 뿐이다. 그래서 배선을 기다릴 필요 없이
지금 판정할 수 있다.

방법론 (313차 5원칙)
--------------------
① **일자단위 판정** — 신호단위 유의는 372차가 이미 겪은 함정이다(신호 n=29,089에서
   유의했던 것이 일자단위 58일에서 r=-0.099로 소멸). 여기서도 1차 판정은 거래일이다.
② **overlap** — 포지션은 `entry_ts`로 병합한다(레그 단위 금지, 계측 4원칙 ①).
   일자단위 집계가 같은 날 겹치는 포지션의 비독립성을 흡수한다.
③ **이상치 분해** — 최악 1일을 뺀 뒤에도 부호가 유지되는지 본다. 372차가 손실의
   91%가 단 2건에서 나온 착시를 잡아낸 그 절차다.
④ **사전등록** — 합격선은 settings에 먼저 박혔다. 이 스크립트는 그것을 읽기만 한다.
⑤ **부호 일관성** — 전반부/후반부로 갈라 부호가 뒤집히지 않는지 확인한다.

⚠ 이 채널은 **차단의 정당성**을 묻는다. PASS/FAIL 어휘를 쓰지 않는 이유는
  settings 주석 참조(HurstGate FalseBlock 전례).

실행:
    python scripts/spread_extreme_watch.py
    python scripts/spread_extreme_watch.py --json    # 기계 판독용
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# 장중 차단 — 라이브 DB 전수 스캔은 파이프라인을 늦춘다(456차 CB⑤ 자가유발 사고).
from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402

CHANNEL = "spread_extreme_watch"


def _cfg():
    from config.settings import VALIDATION_CAMPAIGN
    return VALIDATION_CAMPAIGN.get(CHANNEL) or {}


# ── 표본 수집 ───────────────────────────────────────────────────────────────

def _entry_spread_map(cfg):
    """진입 후보 분봉의 `spread_ticks` — {ts: (spread, auto_entry)}.

    출처는 `ensemble_decisions.features` JSON이다. Phase B에서 전용 컬럼이 생기면
    `spread_source="column"`으로 바꾸고 같은 값이 나오는지 대조한다.
    """
    from config.settings import PREDICTIONS_DB
    out = {}
    con = connect_ro(PREDICTIONS_DB)
    try:
        cur = con.execute(
            "SELECT ts, features, auto_entry FROM ensemble_decisions "
            "WHERE features IS NOT NULL AND date(ts) >= ? ORDER BY ts",
            (cfg.get("data_start", "2026-05-14"),),
        )
        for ts, feats, auto in cur:
            try:
                d = json.loads(feats)
            except (ValueError, TypeError):
                continue
            if not isinstance(d, dict) or "spread_ticks" not in d:
                continue
            try:
                v = float(d["spread_ticks"] or 0.0)
            except (TypeError, ValueError):
                continue
            out[ts] = (v, int(auto or 0))
    finally:
        con.close()
    return out


def _column_crosscheck(cfg, json_map):
    """전용 컬럼(F-8 Phase B)과 `features` JSON이 같은 값을 말하는가.

    배선이 옳은지 확인하는 유일한 수단이다 — 컬럼만 보면 "값이 들어온다"까지만
    알 수 있고 **그 값이 맞는지**는 모른다. 471차 `sizing_trace`는 원본이 없어
    이 대조를 할 수 없었다(그래서 배포 후 적재 0행인 것도 며칠 뒤에야 드러났다).
    여기는 원본이 살아 있으므로 매 실행마다 대조한다.

    반환의 `n_column_rows == 0`은 **배선 실패가 아니라 아직 첫 EOD 전**일 수 있다.
    둘을 구분해 문자열로 남긴다(계측 4원칙 ②·④).
    """
    from config.settings import PREDICTIONS_DB
    con = connect_ro(PREDICTIONS_DB)
    try:
        cols = {r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")}
        if "spread_ticks" not in cols:
            return {"column_present": False,
                    "note": "spread_ticks 컬럼 없음 — F-8 Phase B 미배포 DB"}
        rows = con.execute(
            "SELECT ts, spread_ticks, spread_extreme_shadow FROM ensemble_decisions "
            "WHERE spread_ticks IS NOT NULL"
        ).fetchall()
    finally:
        con.close()

    if not rows:
        return {"column_present": True, "n_column_rows": 0,
                "note": "컬럼은 있으나 적재 0행 — 배포 후 첫 EOD 이전이면 정상. "
                        "다음 거래일에도 0이면 배선이 죽은 것이다."}

    thr = float(cfg.get("block_ticks", 20.0))
    mismatch_val = mismatch_flag = compared = 0
    for ts, v, flag in rows:
        ref = json_map.get(ts)
        if ref is None:
            continue
        compared += 1
        if abs(float(v) - ref[0]) > 1e-6:
            mismatch_val += 1
        if flag is not None and int(flag) != int(ref[0] >= thr):
            mismatch_flag += 1
    return {
        "column_present": True,
        "n_column_rows": len(rows),
        "n_compared": compared,
        "value_mismatch": mismatch_val,
        "flag_mismatch": mismatch_flag,
        "note": ("일치" if compared and not (mismatch_val or mismatch_flag)
                 else "불일치 — 배선 점검 필요" if compared
                 else "대조 가능 행 0 (JSON 측에 해당 ts 없음)"),
    }


def _merged_positions(cfg):
    """entry_ts 단위 포지션. 병합 규칙은 캠페인 공통 `_merged_positions`와 동일.

    수량은 **sum**이고 `entry_qty`가 있으면 그것을 우선한다(417차 ①·②).
    max로 세면 이익 포지션이 분할청산으로 과소 계상돼 큰 계약수 구간에 손실만
    남는 방향으로 편향된다.
    """
    from config.settings import TRADES_DB
    src = cfg.get("entry_source", "SYSTEM_AUTO")
    con = connect_ro(TRADES_DB)
    try:
        cols = {r[1] for r in con.execute("PRAGMA table_info(trades)")}
        sel = "entry_ts, quantity, COALESCE(net_pnl_krw, pnl_krw) AS pnl"
        if "entry_qty" in cols:
            sel += ", entry_qty"
        where = ("exit_ts IS NOT NULL AND "
                 "(COALESCE(entry_source,'') = ? "
                 " OR (entry_source IS NULL AND COALESCE(grade,'') <> 'MANUAL'))")
        rows = con.execute(
            "SELECT %s FROM trades WHERE %s" % (sel, where), (src,)
        ).fetchall()
    finally:
        con.close()

    merged = {}
    has_eq = "entry_qty" in cols
    for r in rows:
        k = r[0]
        m = merged.setdefault(k, {"entry_ts": k, "pnl": 0.0, "qty": 0,
                                  "qty_recorded": None, "legs": 0})
        m["pnl"] += float(r[2] or 0.0)
        m["qty"] += int(r[1] or 1)
        m["legs"] += 1
        if has_eq and m["qty_recorded"] is None:
            try:
                eq = int(r[3] or 0)
            except (TypeError, ValueError):
                eq = 0
            if eq > 0:
                m["qty_recorded"] = eq
    for m in merged.values():
        m["qty_final"] = m["qty_recorded"] or m["qty"]
    return list(merged.values())


# ── 통계 ────────────────────────────────────────────────────────────────────

def _sign_test_p(diffs):
    """일자단위 부호검정(양측). 0은 제외 — 표본에서 뺀다(관례).

    ⚠ `math.comb`을 쓰지 않는다 — **Python 3.8+ 전용**인데 이 시스템의 런타임은
      py37_32다(CLAUDE.md 운영 환경). 표본이 사전등록 문턱에 도달하기 전에는 이
      함수가 호출되지 않으므로, `comb`을 쓰면 몇 달 뒤 표본이 찬 그날 처음 터진다.
      정확히 그런 지연 폭발을 피하려고 `factorial` 기반으로 직접 센다.
    """
    pos = sum(1 for d in diffs if d > 0)
    neg = sum(1 for d in diffs if d < 0)
    n = pos + neg
    if n == 0:
        return None, 0, 0
    import math
    k = min(pos, neg)
    if n > 300:
        # 대표본: 정규근사(연속성 보정). 2**n을 float으로 다루면 넘친다.
        mu = n / 2.0
        sd = math.sqrt(n / 4.0)
        z = (abs(k - mu) - 0.5) / sd if sd > 0 else 0.0
        p = math.erfc(z / math.sqrt(2.0))
        return min(1.0, p), pos, neg
    tail = sum(math.factorial(n) // (math.factorial(i) * math.factorial(n - i))
               for i in range(0, k + 1))
    p = min(1.0, 2.0 * tail / float(2 ** n))
    return p, pos, neg


def _krw(v, sign=False):
    """천단위 콤마 포맷.

    🔴 `%`-포매팅의 콤마 플래그(`"%,.0f" % v`)는 **py3.7에서 ValueError**다
      (`str.format`/f-string 전용). 런타임이 py37_32이므로 여기서 막는다.
      이런 줄은 **표본이 문턱을 넘은 뒤에야 실행**되므로 그대로 두면 몇 달 뒤
      판정이 처음 나오는 그날 터진다 — `math.comb`과 같은 지연 폭발 패턴이다.
    """
    if v is None:
        return "N/A"
    return ("{:+,.0f}" if sign else "{:,.0f}").format(v)


def _mean(xs):
    return (sum(xs) / len(xs)) if xs else None


# ── 진단 (판정 아님 — 왜 못 재는지, 언제 잴 수 있는지) ──────────────────────

#: 진단용 버킷 경계. ⚠ **판정에 쓰지 않는다.**
#   사전등록된 임계는 `block_ticks` 하나뿐이고, 여기서 다른 컷의 손익이 좋아 보인다고
#   그쪽으로 갈아타면 데이터를 본 뒤 기준을 고르는 것(313차 원칙 ④ 위반)이 된다.
#   이 표의 용도는 두 가지다 — ① 표본이 어디에 있는지 보여주기,
#   ② 별도 사전등록이 필요한 질문을 **발견**하기(그 질문은 새 채널로 등록해야 한다).
_DIAG_EDGES = (8.0, 12.0, 20.0)


def _bucket_name(v):
    """구간 이름과 정렬키를 함께 준다 — 이름만으로 정렬하면 `>=20`이 `12-20` 앞에 온다."""
    lo = 0.0
    for e in _DIAG_EDGES:
        if v < e:
            return ("<%g" % e if lo == 0.0 else "%g-%g" % (lo, e)), lo
        lo = e
    return ">=%g" % _DIAG_EDGES[-1], _DIAG_EDGES[-1]


def _buckets(positions):
    """스프레드 구간별 표본·손익 — 진단 전용."""
    agg = {}
    for p in positions:
        name, order = _bucket_name(p["spread"])
        b = agg.setdefault(name, {"pnl": [], "days": set(), "order": order})
        b["pnl"].append(p["pnl_per_contract"])
        b["days"].add(p["day"])
    out = []
    for name in sorted(agg, key=lambda n: agg[n]["order"]):
        v = agg[name]["pnl"]
        out.append({
            "bucket": name, "n": len(v), "days": len(agg[name]["days"]),
            "mean_krw": _mean(v),
            "win_rate": (sum(1 for x in v if x > 0) / len(v)) if v else None,
        })
    return out


def _accrual(hi, spread, cfg):
    """표본 적립 속도와 min_samples 도달 ETA.

    이게 없으면 "표본이 쌓이면 판정한다"가 검증되지 않은 낙관으로 남는다 —
    F-8이 애초에 한 달 넘게 멈춰 있던 이유가 그것이다.
    """
    need = int(cfg.get("min_samples", 20))
    all_days = len({ts[:10] for ts in spread})
    n = len(hi)
    if all_days <= 0:
        return {"trading_days_observed": 0}
    rate = n / float(all_days)          # 거래일당 처리군 진입 건수
    remain = max(0, need - n)
    eta_days = int(round(remain / rate)) if rate > 0 else None
    return {
        "trading_days_observed": all_days,
        "hi_per_trading_day": rate,
        "need_more": remain,
        "eta_trading_days": eta_days,
        "eta_months_approx": (round(eta_days / 21.0, 1)
                              if eta_days is not None else None),
    }


# ── 판정 ────────────────────────────────────────────────────────────────────

def compute():
    cfg = _cfg()
    if not cfg.get("enabled", False):
        return {"available": False, "reason": "채널 비활성"}

    thr = float(cfg.get("block_ticks", 20.0))
    min_valid = float(cfg.get("min_valid_ticks", 0.0001))

    spread = _entry_spread_map(cfg)
    if not spread:
        return {"available": False,
                "reason": "ensemble_decisions.features에서 spread_ticks를 얻지 못함"}

    positions = _merged_positions(cfg)
    if not positions:
        return {"available": False, "reason": "병합 포지션 0건"}

    hi, lo = [], []
    unmatched = 0        # 진입 분봉의 결정행을 못 찾음 = 미측정
    invalid_spread = 0   # 호가 결측 폴백(0.0) — 어느 군에도 넣지 않는다
    for p in positions:
        rec = spread.get(p["entry_ts"])
        if rec is None:
            # 초 단위가 어긋나는 경우가 있어 분 절단으로 한 번 더 시도
            rec = spread.get(p["entry_ts"][:16] + ":00")
        if rec is None:
            unmatched += 1
            continue
        v = rec[0]
        if v < min_valid:
            invalid_spread += 1
            continue
        p["spread"] = v
        p["day"] = p["entry_ts"][:10]
        p["pnl_per_contract"] = p["pnl"] / max(p["qty_final"], 1)
        (hi if v >= thr else lo).append(p)

    res = {
        "available": True,
        "threshold_ticks": thr,
        "n_hi": len(hi), "n_lo": len(lo),
        "unmatched_positions": unmatched,
        "invalid_spread_positions": invalid_spread,
        "days_hi": len({p["day"] for p in hi}),
        "days_lo": len({p["day"] for p in lo}),
        "spread_source": cfg.get("spread_source"),
    }
    res["buckets"] = _buckets(hi + lo)
    res["accrual"] = _accrual(hi, spread, cfg)
    res["column_crosscheck"] = _column_crosscheck(cfg, spread)

    # 사전등록 표본 관문
    if len(hi) < int(cfg.get("min_samples", 20)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = ("처리군 포지션 %d < min_samples %d"
                         % (len(hi), cfg.get("min_samples")))
        return res
    if res["days_hi"] < int(cfg.get("min_days", 6)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = ("처리군 거래일 %d < min_days %d"
                         % (res["days_hi"], cfg.get("min_days")))
        return res

    # ── ① 일자단위: 같은 날 hi 평균 − lo 평균 ────────────────────────────────
    by_day_hi, by_day_lo = defaultdict(list), defaultdict(list)
    for p in hi:
        by_day_hi[p["day"]].append(p["pnl_per_contract"])
    for p in lo:
        by_day_lo[p["day"]].append(p["pnl_per_contract"])

    paired = []   # (day, diff) — 두 군이 모두 있는 날만
    for day in sorted(set(by_day_hi) & set(by_day_lo)):
        paired.append((day, _mean(by_day_hi[day]) - _mean(by_day_lo[day])))
    res["paired_days"] = len(paired)

    res["mean_hi_krw"] = _mean([p["pnl_per_contract"] for p in hi])
    res["mean_lo_krw"] = _mean([p["pnl_per_contract"] for p in lo])
    res["gap_krw"] = res["mean_hi_krw"] - res["mean_lo_krw"]

    if len(paired) < int(cfg.get("min_days", 6)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = ("두 군이 함께 존재하는 거래일 %d < min_days %d "
                         "— 일자단위 대조 불가" % (len(paired), cfg.get("min_days")))
        return res

    diffs = [d for _, d in paired]
    p_val, n_pos, n_neg = _sign_test_p(diffs)
    res["day_mean_diff_krw"] = _mean(diffs)
    res["sign_test_p"] = p_val
    res["days_hi_better"] = n_pos
    res["days_hi_worse"] = n_neg

    # ── ③ 이상치 분해: 최악 |diff| 1일 제거 후 부호 유지 ─────────────────────
    k = int(cfg.get("drop_worst_days", 1))
    trimmed = sorted(paired, key=lambda x: abs(x[1]), reverse=True)[k:]
    res["dropped_days"] = [d for d, _ in
                           sorted(paired, key=lambda x: abs(x[1]), reverse=True)[:k]]
    tvals = [d for _, d in trimmed]
    res["day_mean_diff_trimmed_krw"] = _mean(tvals)
    res["sign_test_p_trimmed"] = _sign_test_p(tvals)[0] if tvals else None

    # ── ⑤ 부호 일관성: 전반/후반 분할 ────────────────────────────────────────
    half = len(paired) // 2
    res["first_half_diff_krw"] = _mean([d for _, d in paired[:half]]) if half else None
    res["second_half_diff_krw"] = _mean([d for _, d in paired[half:]]) if half else None

    # ── 사전등록 판정 ────────────────────────────────────────────────────────
    gap_thr = float(cfg.get("pnl_gap_krw", 200_000))
    alpha = float(cfg.get("alpha", 0.05))
    mean_diff = res["day_mean_diff_krw"]
    trimmed_diff = res["day_mean_diff_trimmed_krw"]

    reasons = []
    worse = mean_diff is not None and mean_diff < 0          # hi가 lo보다 나쁘다
    big = mean_diff is not None and abs(mean_diff) >= gap_thr
    sig = p_val is not None and p_val < alpha
    holds = (trimmed_diff is not None and mean_diff is not None
             and (trimmed_diff < 0) == (mean_diff < 0))

    if worse and big and sig and holds:
        res["verdict"] = "BLOCK_JUSTIFIED"
        reasons.append("일자단위 격차 %s원 (|격차| >= %s) · p=%.4f < %.2f · "
                       "최악 %d일 제거 후 부호 유지"
                       % (_krw(mean_diff, sign=True), _krw(gap_thr), p_val, alpha, k))
    else:
        res["verdict"] = "BLOCK_UNJUSTIFIED"
        if not worse:
            reasons.append("격차 부호가 반대 (극단 스프레드 진입이 더 낫거나 같다)")
        if not big:
            reasons.append("|격차| %s원 < 사전등록 %s원"
                           % (_krw(abs(mean_diff or 0)), _krw(gap_thr)))
        if not sig:
            reasons.append("부호검정 p=%s >= %.2f" % (
                "%.4f" % p_val if p_val is not None else "N/A", alpha))
        if not holds:
            reasons.append("최악 %d일 제거 시 부호가 뒤집힘 — 이상치 의존" % k)
    res["reason"] = " / ".join(reasons)
    return res


def summarize(res):
    if not res.get("available"):
        return "[⑨ 극단스프레드] 판정 불가 — %s" % res.get("reason", "?")
    return ("[⑨ 극단스프레드] %s | 처리군 %d포지션/%d일 vs 대조군 %d포지션 | "
            "일자평균격차 %s원 | %s"
            % (res["verdict"], res["n_hi"], res["days_hi"], res["n_lo"],
               _krw(res["day_mean_diff_krw"], sign=True)
               if res.get("day_mean_diff_krw") is not None else "N/A",
               res.get("reason", "")))


def _fmt(v, unit=""):
    if v is None:
        return "N/A"
    if isinstance(v, float):
        return "%s%s" % (_krw(v, sign=True), unit)
    return "%s%s" % (v, unit)


def main():
    guard_intraday("spread_extreme_watch")
    res = compute()
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    cfg = _cfg()
    print("=" * 74)
    print("F-8 Phase A — 극단 스프레드(>=%.0f틱) 진입 손익 소급 판정" % cfg.get("block_ticks", 20))
    print("사전등록: VALIDATION_CAMPAIGN['%s'] (473차, 손익 축을 열기 전에 고정)" % CHANNEL)
    print("=" * 74)
    if not res.get("available"):
        print("판정 불가 — %s" % res.get("reason"))
        return 1

    print("표본")
    print("  처리군(>=%.0f틱)  %4d 포지션 / %2d 거래일" % (
        res["threshold_ticks"], res["n_hi"], res["days_hi"]))
    print("  대조군(< %.0f틱)  %4d 포지션 / %2d 거래일" % (
        res["threshold_ticks"], res["n_lo"], res["days_lo"]))
    print("  두 군 공존일      %s" % res.get("paired_days", "—"))
    print("  제외: 결정행 미매칭 %d (미측정) · 호가결측 폴백 %d (spread=0.0)"
          % (res["unmatched_positions"], res["invalid_spread_positions"]))
    print()
    print("진단 — 스프레드 구간별 분포  ⚠ 판정 아님(사전등록 임계는 %.0f틱 하나뿐)"
          % res["threshold_ticks"])
    for b in res.get("buckets", []):
        print("  %-8s n=%3d  일수=%2d  계약당평균 %12s원  승률 %s" % (
            b["bucket"], b["n"], b["days"], "{:,.0f}".format(b["mean_krw"] or 0),
            ("%.1f%%" % (100 * b["win_rate"])) if b["win_rate"] is not None else "N/A"))
    acc = res.get("accrual") or {}
    if acc.get("eta_trading_days") is not None:
        print()
        print("표본 적립 속도")
        print("  관측 거래일 %d일 · 처리군 %.3f건/거래일 · 앞으로 %d건 더 필요"
              % (acc["trading_days_observed"], acc["hi_per_trading_day"],
                 acc["need_more"]))
        print("  min_samples 도달 ETA ≈ %d 거래일 (약 %s개월)"
              % (acc["eta_trading_days"], acc["eta_months_approx"]))
    cc = res.get("column_crosscheck") or {}
    if cc:
        print()
        print("F-8 Phase B 컬럼 대조")
        if not cc.get("column_present"):
            print("  %s" % cc.get("note"))
        elif not cc.get("n_column_rows"):
            print("  적재 0행 — %s" % cc.get("note"))
        else:
            print("  적재 %d행 / 대조 %d행 · 값불일치 %d · 플래그불일치 %d → %s"
                  % (cc["n_column_rows"], cc["n_compared"],
                     cc["value_mismatch"], cc["flag_mismatch"], cc["note"]))
    print()
    print("손익 (포지션 단위 · 계약당 순손익)")
    print("  처리군 평균  %s원" % _fmt(res.get("mean_hi_krw")))
    print("  대조군 평균  %s원" % _fmt(res.get("mean_lo_krw")))
    print("  단순 격차    %s원" % _fmt(res.get("gap_krw")))
    print()
    if res["verdict"] != "INSUFFICIENT":
        print("일자단위 (①·② — 1차 판정축)")
        print("  일평균 격차            %s원" % _fmt(res.get("day_mean_diff_krw")))
        print("  부호검정 p             %s  (hi우세 %d일 / hi열위 %d일)" % (
            ("%.4f" % res["sign_test_p"]) if res.get("sign_test_p") is not None else "N/A",
            res.get("days_hi_better", 0), res.get("days_hi_worse", 0)))
        print()
        print("이상치 분해 (③)")
        print("  제거일                 %s" % (res.get("dropped_days") or "—"))
        print("  제거 후 일평균 격차    %s원" % _fmt(res.get("day_mean_diff_trimmed_krw")))
        print("  제거 후 p              %s" % (
            ("%.4f" % res["sign_test_p_trimmed"])
            if res.get("sign_test_p_trimmed") is not None else "N/A"))
        print()
        print("부호 일관성 (⑤)")
        print("  전반부 격차            %s원" % _fmt(res.get("first_half_diff_krw")))
        print("  후반부 격차            %s원" % _fmt(res.get("second_half_diff_krw")))
        print()
    print("-" * 74)
    print("판정: %s" % res["verdict"])
    print("사유: %s" % res.get("reason", ""))
    print("-" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
