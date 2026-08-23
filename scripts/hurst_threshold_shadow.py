# scripts/hurst_threshold_shadow.py
"""[MW0601 434차, 캠페인 46] HurstGate 임계 위치 A/B — 읽기 전용 오프라인 스윕.

무엇을 묻는가
--------------
`HURST_RANGE_THRESHOLD = 0.45`가 이 추정량의 **판별 경계로 적절한 위치인가**를 묻는다.

    hurst 무조건부 분포 (ensemble_decisions.features, 14,185 사이클)
      min 0.000  p25 0.351  중앙 0.452  p75 0.500  p95 0.614  max 0.716

**임계가 중앙값(0.452)과 거의 같다.** 레짐 분류기의 임계가 추정량 분포의 중앙에 있으면
시장 상태와 무관하게 구조적으로 절반을 "횡보"로 라벨링한다(실측 발동률 49.4%).
이건 알려진 추정량 편향이다 — `settings.py`가 "진짜 랜덤워크 H=0.5가 평균 0.446으로
찍히는 문제"라고 이미 명시하고 있다.

왜 지금인가 / 무엇이 새로운가
------------------------------
- 317차는 추정량 **파라미터**(N 60→90, max_lag 20→9)를 재보정하면서 임계는
  "이 파라미터 그대로 검증됐으므로 변경하지 않음"으로 **명시적으로 손대지 않았다.**
  즉 임계는 이 추정량의 실제 분포에 대해 **한 번도 보정된 적이 없다.** 그게 공백이다.
- 431차가 곱셈 체인을 min() 합성으로 바꾸면서 이 게이트의 실효 영향이 올라갔다
  (no-op 비율 95% → 71%, `hurst_softblock_noop_analysis.py` 실측).

⚠ 이미 반증된 방향 — 재시도 금지
--------------------------------
**추정량 편향보정은 하지 않는다.** 317차가 상수이동과 선형 de-shrinkage를 둘 다 시도했고
60거래일 실측에서 **FalsePass가 14.4% → 30~33%로 악화**돼 폐기했다
(`HURST_DESHRINK_TABLE`은 REFERENCE ONLY로 남아 있을 뿐 라이브 미참조).
이 채널이 묻는 것은 **추정량을 고치는 것이 아니라 임계를 어디에 둘 것인가**다.

절대임계 vs 분위임계
--------------------
분위(quantile) 후보를 함께 재는 이유는 **371차 선례**다 — RegimeFingerprint PSI가
균등폭 bin이 실제 분포와 안 맞아 상시 CRITICAL에 고착했고, 분위 기반 비닝으로 해소됐다.
분위 임계는 절대값을 쓰지 않으므로 추정량이 얼마나 편향돼 있든 무관해진다.
분위는 **직전 N거래일 롤링**으로 계산한다(당일 미포함 — 룩어헤드 없음).

무엇을 결론으로 삼을 수 있나 / 없나
-----------------------------------
- ⚠⚠ **사전등록 정직성 고지 (반드시 함께 읽을 것)**: 후보 임계 목록은 2026-08-05
  일일점검에서 **이미 1회 스윕한 뒤에** 고른 것이다. 따라서 전체표본 결과는
  **가설을 세운 그 기간의 in-sample**이며 그 자체로는 판정 근거가 아니다.
  이 채널의 사전등록 가치는 `oos_start` 이후 신규 발생분에 있다 — [23]과 같은 구조.
- 313차 원칙: min_days 미달이면 판정하지 않는다. 단일일로 임계를 바꾸지 않는다.
- ⚠ **372차 함정**: PSI 임계 재보정 시도에서 손익 기반 근거가 이상치 2건에 좌우돼
  결국 **기존값 유지**로 끝났다. 여기도 표본이 얇다 — drop-max와 일자단위를 반드시
  함께 볼 것. 누적 pt만 보고 판단하면 같은 함정에 빠진다.

왜 손익 카운터팩추얼이 아니라 "분리도"인가 (설계 핵심)
------------------------------------------------------
HurstGate는 333차 후속부터 **차단이 아니라 사이징 ×0.5**다. 임계를 바꾸면 진입/청산이
아니라 **수량**이 바뀌므로, 손익 카운터팩추얼을 내려면 수량을 재시뮬해야 하고 그러면
게이트 체인 전체(min 합성·안전군·상한)를 다시 돌려야 한다 — 재현 오차가 측정하려는
효과보다 커진다.

그래서 이 채널은 **계약당 pt의 분리도**를 잰다:

    sep(t) = mean_pt_per_contract(hurst >= t) - mean_pt_per_contract(hurst < t)

계약당으로 정규화하므로 **사이징과 무관**하고(417차 교훈 — `quantity`는 청산레그 수량),
"축소해야 할 구간이 실제로 더 나쁜가"라는 질문에 직접 답한다. sep가 클수록 그 임계가
좋은 신호와 나쁜 신호를 잘 가른다는 뜻이다.

한계
----
- 진입이 실제로 발생한 포지션만 대상이다. 게이트가 진입 자체를 막은 신호는 여기 없다
  (그건 [3-6] `hurst_gate_shadow`의 질문이다 — 서로 다른 모집단).
- pt는 수수료·슬리피지 차감 전이다. 분리도는 차분이라 상수 비용이 상쇄된다.
- 표본이 얇다(전체 n≈176 / 32거래일). 확정 결론 금지 구간이다.

실행:
    py310_64\\python.exe scripts/hurst_threshold_shadow.py [--since 2026-06-10]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sqlite3
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import (  # noqa: E402
    TRADES_DB, PREDICTIONS_DB, VALIDATION_CAMPAIGN, HURST_RANGE_THRESHOLD,
)

_CR = VALIDATION_CAMPAIGN.get("hurst_threshold_shadow", {})


def _load_hurst(since: str) -> dict:
    """분(minute) → hurst. 게이트 발동 여부와 무관한 무조건부 모집단이다.

    ⚠ SIGNAL 로그의 `[HurstGate]` 줄에서 뽑으면 **게이트가 발동한 사이클만** 남아
    hurst < 임계인 표본만 모인다(선택편향). 0805 점검에서 실제로 그 오독이 나왔다.
    반드시 `ensemble_decisions.features`에서 읽을 것.
    """
    out = {}
    with sqlite3.connect(PREDICTIONS_DB) as c:
        for ts, feat in c.execute(
            "SELECT ts, features FROM ensemble_decisions "
            "WHERE ts >= ? AND features IS NOT NULL", (since,)
        ):
            try:
                v = json.loads(feat).get("hurst")
            except (ValueError, TypeError):
                continue
            if v is not None:
                out[ts[:16]] = float(v)
    return out


def _load_positions(since: str) -> list:
    """부분청산 레그를 진입 단위로 병합 — 417차 교훈(레그 단위 집계 금지)."""
    with sqlite3.connect(TRADES_DB) as c:
        c.row_factory = sqlite3.Row
        rows = [dict(r) for r in c.execute(
            "SELECT entry_ts, direction, entry_qty, pnl_pts, net_pnl_krw "
            "FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL "
            "AND (entry_source IS NULL OR entry_source != 'OPERATOR_MANUAL') "
            "ORDER BY entry_ts", (since,))]
    agg = collections.OrderedDict()
    for r in rows:
        agg.setdefault((r["entry_ts"], r["direction"]), []).append(r)
    out = []
    for (ets, _d), legs in agg.items():
        qty = int(legs[0]["entry_qty"] or 1) or 1
        pts = sum(float(x["pnl_pts"] or 0) for x in legs)
        out.append({
            "ts": ets, "day": ets[:10], "qty": qty,
            # 계약당 pt — 사이징과 무관한 신호 품질 지표
            "pt_pc": pts / qty,
            "krw": sum(float(x["net_pnl_krw"] or 0) for x in legs),
        })
    return out


def _rolling_quantile_thresholds(hurst_map: dict, q: float, lookback_days: int) -> dict:
    """일자 → 그 날 적용할 분위 임계. 직전 lookback_days만 사용(당일 미포함).

    당일을 넣으면 룩어헤드다 — 그 날의 hurst 분포를 알아야 그 날 임계가 정해지므로
    실시간으로 재현 불가능한 값이 된다.
    """
    by_day = collections.defaultdict(list)
    for k, v in hurst_map.items():
        by_day[k[:10]].append(v)
    days = sorted(by_day)
    out = {}
    for i, d in enumerate(days):
        prev = days[max(0, i - lookback_days):i]
        pool = [v for p in prev for v in by_day[p]]
        if len(pool) < 100:      # 표본이 너무 적으면 그 날은 판정 제외
            continue
        pool.sort()
        out[d] = pool[min(len(pool) - 1, int(len(pool) * q))]
    return out


def _stats(gated: list, passed: list) -> dict:
    """분리도 + 판정보조. gated/passed는 pt_pc 리스트."""
    if not gated or not passed:
        return {}
    mg, mp = statistics.mean(gated), statistics.mean(passed)
    d = {
        "n_gated": len(gated), "n_passed": len(passed),
        "gate_rate": round(len(gated) / float(len(gated) + len(passed)), 4),
        "mean_gated_pt": round(mg, 4), "mean_passed_pt": round(mp, 4),
        "separation_pt": round(mp - mg, 4),
        "wr_gated": round(sum(1 for x in gated if x > 0) / float(len(gated)), 4),
        "wr_passed": round(sum(1 for x in passed if x > 0) / float(len(passed)), 4),
        "sum_gated_pt": round(sum(gated), 4),
        "gated_sign_negative": bool(mg < 0),
    }
    # 판정보조 ① drop-max — 차단구간에서 가장 나쁜 1건을 빼도 분리도가 유지되는가.
    # (분리도를 만드는 게 이상치 1건이면 그 임계는 근거가 아니다 — 372차 함정)
    if len(gated) > 1:
        g2 = sorted(gated)[1:]          # 최악 1건 제거
        d["separation_drop_worst"] = round(mp - statistics.mean(g2), 4)
    else:
        d["separation_drop_worst"] = None
    return d


def compute(since: str = "2026-06-10") -> dict:
    hurst = _load_hurst(since)
    pos = _load_positions(since)
    lookback = int(_CR.get("quantile_lookback_days", 10))

    matched = []
    for p in pos:
        h = hurst.get(p["ts"][:16])
        if h is None:
            continue
        p = dict(p); p["hurst"] = h
        matched.append(p)

    abs_cands = list(_CR.get("abs_candidates", [0.30, 0.36, 0.39, 0.42, 0.45]))
    q_cands = list(_CR.get("quantile_candidates", [0.10, 0.20, 0.30]))
    qmaps = {q: _rolling_quantile_thresholds(hurst, q, lookback) for q in q_cands}

    oos_start = str(_CR.get("oos_start", "")) or None

    def run(subset):
        res = {}
        for t in abs_cands:
            g = [x["pt_pc"] for x in subset if x["hurst"] < t]
            pss = [x["pt_pc"] for x in subset if x["hurst"] >= t]
            s = _stats(g, pss)
            if s:
                s["threshold"] = t
                res["abs_%.2f" % t] = s
        for q in q_cands:
            qm = qmaps[q]
            g, pss, skipped = [], [], 0
            for x in subset:
                th = qm.get(x["day"])
                if th is None:
                    skipped += 1
                    continue
                (g if x["hurst"] < th else pss).append(x["pt_pc"])
            s = _stats(g, pss)
            if s:
                s["quantile"] = q
                s["n_skipped_warmup"] = skipped
                res["q%02d" % int(q * 100)] = s
        return res

    full = run(matched)
    oos_rows = [x for x in matched if x["day"] >= oos_start] if oos_start else []
    oos = run(oos_rows) if oos_start else {}

    # ── [MW0601 489차 / B-1] 판정보조 ③ — OOS 기간 2분할 재현 ────────────────
    # 종전 ③은 "MW0601 × MW0602 교차"였는데 2026-08-23 멀티PC 정책 폐기로
    # **충족 불가능한 관문**이 됐다. 교차검증의 취지(우연한 표본 구성에 기댄
    # 우위를 걸러낸다)를 단일 갈래에서 살린다 — OOS 거래일을 전·후반으로 갈라
    # 같은 후보가 **양쪽에서** 현행을 초과하는지 본다.
    # ⚠ 표본을 절반으로 쪼갠다 — 통과해도 "약한 증거"다(313차).
    split = {}
    if _CR.get("split_half_check") and oos_rows:
        _days = sorted(set(x["day"] for x in oos_rows))
        _mid = len(_days) // 2          # 홀수면 후반이 하루 더 갖는다(고정 규약)
        _d1, _d2 = set(_days[:_mid]), set(_days[_mid:])
        _h1 = [x for x in oos_rows if x["day"] in _d1]
        _h2 = [x for x in oos_rows if x["day"] in _d2]
        split = {
            "n_half1": len(_h1), "n_half2": len(_h2),
            "days_half1": sorted(_d1), "days_half2": sorted(_d2),
            "min_per_half": int(_CR.get("split_half_min_per_half", 20)),
            "per_variant_half1": run(_h1),
            "per_variant_half2": run(_h2),
        }

    return {
        "since": since, "n_positions": len(pos), "n_matched": len(matched),
        "n_days": len(set(x["day"] for x in matched)),
        "n_days_oos": len(set(x["day"] for x in matched if oos_start and x["day"] >= oos_start)),
        "n_oos": sum(1 for x in matched if oos_start and x["day"] >= oos_start),
        "live_threshold": float(HURST_RANGE_THRESHOLD),
        "quantile_lookback_days": lookback,
        "oos_start": oos_start,
        "per_variant": full, "per_variant_oos": oos,
        "split_half": split,
        # 일자단위(313차) — 저hurst 진입 비중과 그날 손익의 부호 일관성
        "by_day": _by_day(matched),
    }


def _by_day(matched: list) -> dict:
    dd = collections.defaultdict(lambda: {"n": 0, "n_low": 0, "pt": 0.0})
    for x in matched:
        d = dd[x["day"]]
        d["n"] += 1
        d["pt"] += x["pt_pc"]
        if x["hurst"] < HURST_RANGE_THRESHOLD:
            d["n_low"] += 1
    return {k: {"n": v["n"], "low_share": round(v["n_low"] / float(v["n"]), 4),
                "pt": round(v["pt"], 4)} for k, v in sorted(dd.items())}


def summarize(out: dict) -> dict:
    """판정 — 사전등록 기준 그대로. 기준을 여기서 바꾸지 말 것(§9).

    PASS(현행 0.45 유지):
        OOS에서 어떤 후보도 현행 대비 분리도 우위 + drop-max 생존을 동시에 못 만족.
    FAIL(변경 검토):
        위를 만족하는 후보 존재 → 즉시 적용 아님, 주간회의 수동 결정.
    """
    min_n = int(_CR.get("min_samples", 40))
    min_d = int(_CR.get("min_days", 10))
    pv_oos = out.get("per_variant_oos") or {}
    n_oos, d_oos = out.get("n_oos", 0), out.get("n_days_oos", 0)
    cur_key = "abs_%.2f" % out["live_threshold"]

    # 리포트가 표를 그리려면 계산부 산출물이 함께 있어야 한다 — 다른 오프라인 채널
    # (tp1_geometry_shadow 등)과 동일 규약: summarize()가 렌더링에 필요한 전부를 낸다.
    base_payload = {
        "cur_key": cur_key, "min_samples": min_n, "min_days": min_d,
        "n_oos": n_oos, "n_days_oos": d_oos,
        "n_matched": out.get("n_matched", 0), "n_days": out.get("n_days", 0),
        "n_positions": out.get("n_positions", 0),
        "live_threshold": out.get("live_threshold"),
        "oos_start": out.get("oos_start"),
        "quantile_lookback_days": out.get("quantile_lookback_days"),
        "per_variant": out.get("per_variant") or {},
        "per_variant_oos": pv_oos,
        "split_half": out.get("split_half") or {},
        "by_day": out.get("by_day") or {},
    }

    def done(verdict, reason, beats):
        d = dict(base_payload)
        d.update({"verdict": verdict, "reason": reason, "beats": beats})
        return d

    if n_oos < min_n or d_oos < min_d:
        return done("INSUFFICIENT",
                    ("OOS 표본 부족 (n=%d<%d 또는 거래일=%d<%d). 전체표본 결과는 "
                     "가설 수립 기간의 in-sample이라 판정 근거가 아니다"
                     % (n_oos, min_n, d_oos, min_d)), [])
    base = pv_oos.get(cur_key)
    if not base:
        return done("INSUFFICIENT",
                    "OOS에서 현행 임계(%s) 기준선 산출 불가" % cur_key, [])
    beats = []
    for k, v in pv_oos.items():
        if k == cur_key:
            continue
        # 사전등록 조건: 분리도 우위 **그리고** drop-worst 생존(둘 다 현행 분리도 초과).
        # drop-worst를 같은 기준선과 비교하는 이유는, 차단구간 최악 1건을 빼고도
        # 현행보다 나아야 "이상치가 만든 우위"를 배제할 수 있기 때문이다(372차 함정).
        if (v.get("separation_pt") or 0) > (base.get("separation_pt") or 0) and \
           (v.get("separation_drop_worst") or 0) > (base.get("separation_pt") or 0):
            beats.append(k)
    # ── [MW0601 489차] 판정보조 ③ — 2분할 양쪽에서 살아남는 후보만 표기 ──────
    # ⚠ **verdict 를 바꾸지 않는다**(§9-4). `beats` 는 사전등록 그대로이고,
    #   여기서 내는 것은 "그중 어느 것이 2분할까지 통과했는가"라는 보조 표기다.
    _sp = out.get("split_half") or {}
    if _sp and beats:
        _need = int(_sp.get("min_per_half", 20))
        if _sp.get("n_half1", 0) < _need or _sp.get("n_half2", 0) < _need:
            base_payload["split_half_verdict"] = "INSUFFICIENT"
            base_payload["split_half_reason"] = (
                "반쪽 표본 부족 (전반 %d / 후반 %d, 각 %d 필요) — 2분할 판정 보류"
                % (_sp.get("n_half1", 0), _sp.get("n_half2", 0), _need))
            base_payload["split_half_survivors"] = []
        else:
            _surv = []
            for _k in beats:
                _ok = True
                for _half in ("per_variant_half1", "per_variant_half2"):
                    _pv = _sp.get(_half) or {}
                    _b, _v = _pv.get(cur_key), _pv.get(_k)
                    if not _b or not _v:
                        _ok = False
                        break
                    if (_v.get("separation_pt") or 0) <= (_b.get("separation_pt") or 0):
                        _ok = False
                        break
                if _ok:
                    _surv.append(_k)
            base_payload["split_half_verdict"] = "PASS" if _surv else "FAIL"
            base_payload["split_half_survivors"] = _surv
            base_payload["split_half_reason"] = (
                ("2분할 양쪽에서 현행 초과: %s" % ", ".join(_surv)) if _surv else
                "OOS 전체에서 현행을 초과한 후보 중 2분할 양쪽을 통과한 것이 없다 "
                "— 우연한 표본 구성일 가능성")

    return done("FAIL" if beats else "PASS",
                ("현행 초과 후보(분리도 + drop-worst 동시 우위): %s" % ", ".join(beats))
                if beats else "어떤 후보도 현행 대비 분리도·drop-worst 동시 우위를 못 만들었다",
                beats)


def _print_table(title, pv, live_key):
    print(title)
    if not pv:
        print("  (표본 없음)")
        return
    print("  %-10s %7s %7s %9s %9s %10s %10s %8s %8s"
          % ("후보", "차단n", "발동률", "차단평균", "통과평균", "분리도", "drop-worst",
             "차단승률", "통과승률"))
    for k in sorted(pv, key=lambda x: (x.startswith("q"), x)):
        v = pv[k]
        mark = " ← 현행" if k == live_key else ""
        print("  %-10s %7d %6.1f%% %+9.3f %+9.3f %+10.3f %+10s %7.1f%% %7.1f%%%s"
              % (k, v["n_gated"], v["gate_rate"] * 100, v["mean_gated_pt"],
                 v["mean_passed_pt"], v["separation_pt"],
                 ("%.3f" % v["separation_drop_worst"]) if v.get("separation_drop_worst") is not None else "—",
                 v["wr_gated"] * 100, v["wr_passed"] * 100, mark))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-06-10")
    args = ap.parse_args()
    out = compute(args.since)
    s = summarize(out)

    print("=" * 100)
    print("[46] HurstGate 임계 위치 A/B   기간 %s~   현행 임계 %.2f"
          % (args.since, out["live_threshold"]))
    print("사전등록 기준: config/settings.py VALIDATION_CAMPAIGN['hurst_threshold_shadow']")
    print("=" * 100)
    print("포지션 %d건 중 hurst 매칭 %d건 / %d거래일   분위 룩백 %d거래일"
          % (out["n_positions"], out["n_matched"], out["n_days"],
             out["quantile_lookback_days"]))
    print("지표: 분리도 = 통과구간 계약당평균pt − 차단구간 계약당평균pt (사이징 무관)")
    print()
    _print_table("── 전체표본 (⚠ in-sample — 판정 근거 아님) ─────────────────────",
                 out["per_variant"], s["cur_key"])
    print()
    _print_table("── OOS (%s 이후 — 판정 대상) ──────────────────────────"
                 % (out["oos_start"] or "미설정"), out["per_variant_oos"], s["cur_key"])
    print()
    print("판정: %s — %s" % (s["verdict"], s["reason"]))
    print()
    print("⚠ 후보 목록은 0805 점검에서 이미 1회 스윕한 뒤 고른 것이다 — 전체표본은")
    print("  가설을 세운 그 기간의 in-sample이며 그 자체로는 근거가 아니다([23]과 동일 구조).")
    print("⚠ 317차가 추정량 편향보정(상수이동·de-shrinkage)을 이미 반증했다")
    print("  (FalsePass 14.4%→30~33%). 이 채널은 추정량이 아니라 임계 위치만 묻는다.")
    print("⚠ 372차 함정: 누적 pt만 보면 이상치 소수에 끌려간다. drop-worst와 아래")
    print("  일자단위를 반드시 함께 읽을 것.")
    print("§9: 이 스크립트는 판정을 자동 적용하지 않는다. 적용은 주간회의 수동 결정.")


if __name__ == "__main__":
    main()
