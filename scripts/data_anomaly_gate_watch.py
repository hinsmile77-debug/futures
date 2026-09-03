# -*- coding: utf-8 -*-
"""[MW0601 526차 / P5-13] 데이터이상 게이트(DataAnomalyGate)의 손익 — 봉 단위 반사실 판정.

무엇을 묻는가
-------------
급변장 라벨에서 분리한 「스케일러 |z|>4 피처 ≥3 → 신규 진입 차단」(62차 ③ 조건,
526차 F-A로 `DataAnomalyGate`로 독립)이 **돈을 지키는가**. 지키면 `MICRO_REGIME_ZWARN_GATE`
"block" 유지, 못 지키면 "reduce" → "off" 순으로 처분한다(하드 해제 직행 금지).
사전등록 기준은 `config/settings.py:VALIDATION_CAMPAIGN["data_anomaly_gate_watch"]`.

왜 반사실 시뮬인가
-----------------
차단된 신호에는 실거래가 없다. 그래서 `raw_candles`로 다음 봉 시가 진입 · 손절 1.5 ·
TP1 0.5(1/3 청산 후 보호스톱) · TP2 1.5 ATR14 · 최대 30봉을 재생한다(설정 `sim`).
같은 봉에서 손절·익절이 겹치면 **손절 우선**(보수적). 시뮬 보정: 실제 진입 187분
(2026-07-14~09-03)을 같은 시뮬로 돌리면 +28.2pt vs 실측 +55.1pt — 통산으로 낙관이 아니다.
**수수료는 반드시 뺀다** — 526차 소급에서 "풀어주면 번다"를 뒤집은 것이 수수료였다.

배선 전 구간
-----------
`checklist_reason='DataAnomalyGate'`는 F-A 배선(2026-09-04~) 이후에만 존재한다. 그 이전은
대리 지표 `checklist_reason='RegimeOverride'` 且 `features.atr_ratio < 1.25`(legacy_proxy)로
소급하며, 결과에 `source`를 따로 표기한다. 두 구간을 합쳐 판정하되 표에서 가른다.

방법론 (313차 5원칙)
--------------------
① 일자단위 부호검정 ② 비중첩 3분 서브샘플 ③ 최고 N일 제거 후 부호 유지(차단 정당성을
묻는 채널이라 **최고일**을 뺀다 — "풀어주면 번다"가 소수 대박일에 의존하는지 본다)
④ 합격선은 settings에서만 ⑤ 방향(LONG/SHORT)·시간대는 **보고 열**일 뿐 판정에 안 쓴다.

실행:
    python scripts/data_anomaly_gate_watch.py
    python scripts/data_anomaly_gate_watch.py --json
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402

CHANNEL = "data_anomaly_gate_watch"


def _cfg():
    from config.settings import VALIDATION_CAMPAIGN
    return VALIDATION_CAMPAIGN.get(CHANNEL) or {}


# ── 표본 수집 ───────────────────────────────────────────────────────────────

def _blocked_signals(cfg):
    """차단된 방향 신호 — [(ts, direction, source)]. source ∈ {'gate', 'legacy_proxy'}.

    후보 필터(conf ≥ min_conf · grade C · auto_entry)는 여기서 건다 — "풀어줬으면 실제로
    들어갔을 신호"만 센다. 전부 세면 수수료 폭탄(526차 T1 −263만)으로 답이 자명해진다.
    """
    from config.settings import PREDICTIONS_DB
    con = connect_ro(PREDICTIONS_DB)
    out = []
    try:
        cols = {r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")}
        reasons = tuple(cfg.get("reasons") or ("DataAnomalyGate",))
        cf = cfg.get("candidate_filter") or {}
        proxy = cfg.get("legacy_proxy") or {}
        want = set(reasons) | ({proxy.get("reason")} if proxy else set())
        q = ("SELECT ts, direction, confidence, min_conf, grade, auto_entry, "
             "checklist_reason, features FROM ensemble_decisions "
             "WHERE direction != 0 AND COALESCE(entry_executed,0) = 0 "
             "AND checklist_reason IN (%s) AND date(ts) >= ? ORDER BY ts"
             % ",".join("?" * len(want)))
        for ts, d, conf, mc, g, ae, reason, feats in con.execute(
                q, tuple(want) + (cfg.get("data_start", "2026-06-19"),)):
            if cf.get("conf_ge_min_conf") and not (mc and conf is not None and conf >= mc):
                continue
            if cf.get("grade") and g != cf["grade"]:
                continue
            if cf.get("auto_entry") and not ae:
                continue
            if reason in reasons:
                out.append((ts, int(d), "gate"))
            elif proxy and reason == proxy.get("reason"):
                try:
                    ratio = json.loads(feats).get("atr_ratio") if feats else None
                except (ValueError, TypeError):
                    ratio = None
                if ratio is not None and ratio < float(proxy.get("atr_ratio_max", 1.25)):
                    out.append((ts, int(d), "legacy_proxy"))
        has_col = "micro_regime_source" in cols
    finally:
        con.close()
    return out, has_col


def _candles(days):
    from config.settings import RAW_DATA_DB
    con = connect_ro(RAW_DATA_DB)
    by_day = defaultdict(list)
    try:
        lo, hi = min(days), max(days)
        for ts, o, h, l, c in con.execute(
                "SELECT ts, open, high, low, close FROM raw_candles "
                "WHERE date(ts) BETWEEN ? AND ? AND substr(ts,12,5) >= '08:45' ORDER BY ts",
                (lo, hi)):
            by_day[ts[:10]].append((ts[:16], float(o), float(h), float(l), float(c)))
    finally:
        con.close()
    return by_day


def _prep(rows, atr_window):
    idx = {r[0]: i for i, r in enumerate(rows)}
    tr = [0.0]
    for i in range(1, len(rows)):
        h, l, p = rows[i][2], rows[i][3], rows[i - 1][4]
        tr.append(max(h - l, abs(h - p), abs(l - p)))
    atr = [None] * len(rows)
    for i in range(atr_window, len(rows)):
        atr[i] = sum(tr[i - atr_window + 1:i + 1]) / float(atr_window)
    return idx, atr


def simulate(rows, idx, atr, ts_min, d, sim):
    """다음 봉 시가 진입 · 손절/TP1/TP2 ATR 배수 · 손절 우선. 반환 (pt, outcome, entry_price)."""
    k = ts_min[:16]
    if k not in idx:
        return None
    i = idx[k] + 1
    if i >= len(rows) or atr[i - 1] is None:
        return None
    a = atr[i - 1]
    ep = rows[i][1]
    tp1 = ep + d * sim["tp1_atr"] * a
    tp2 = ep + d * sim["tp2_atr"] * a
    sl = ep - d * sim["stop_atr"] * a
    frac = float(sim.get("tp1_fraction", 1 / 3.0))
    rem, pnl, tp1hit = 1.0, 0.0, False
    for j in range(i, min(i + int(sim["max_bars"]), len(rows))):
        _, o, h, l, c = rows[j]
        sl_hit = (l <= sl) if d == 1 else (h >= sl)
        tp1_hit = (h >= tp1) if d == 1 else (l <= tp1)
        tp2_hit = (h >= tp2) if d == 1 else (l <= tp2)
        if not tp1hit:
            if sl_hit:
                return (d * (sl - ep) * rem + pnl, "STOP", ep)
            if tp1_hit:
                pnl += d * (tp1 - ep) * frac
                rem = 1.0 - frac
                tp1hit = True
                sl = ep + d * 0.05          # 보호스톱 = 진입가 + 1틱
                if tp2_hit:
                    return (pnl + d * (tp2 - ep) * rem, "TP2", ep)
                continue
        else:
            if sl_hit:
                return (pnl + d * (sl - ep) * rem, "TRAIL", ep)
            if tp2_hit:
                return (pnl + d * (tp2 - ep) * rem, "TP2", ep)
    c = rows[min(i + int(sim["max_bars"]), len(rows)) - 1][4]
    return (pnl + d * (c - ep) * rem, "TIMEOUT", ep)


# ── 통계 ────────────────────────────────────────────────────────────────────

def _sign_test_p(diffs):
    """일자단위 부호검정(양측). ⚠ `math.comb` 금지 — 런타임 py37_32."""
    pos = sum(1 for x in diffs if x > 0)
    neg = sum(1 for x in diffs if x < 0)
    n = pos + neg
    if n == 0:
        return None, 0, 0
    k = min(pos, neg)
    if n > 300:
        mu, sd = n / 2.0, math.sqrt(n / 4.0)
        z = (abs(k - mu) - 0.5) / sd if sd > 0 else 0.0
        return min(1.0, math.erfc(z / math.sqrt(2.0))), pos, neg
    tail = sum(math.factorial(n) // (math.factorial(i) * math.factorial(n - i))
               for i in range(0, k + 1))
    return min(1.0, 2.0 * tail / float(2 ** n)), pos, neg


def _krw(v, sign=False):
    if v is None:
        return "N/A"
    return ("{:+,.0f}" if sign else "{:,.0f}").format(v)


def _round_trip_commission(entry_price, cfg):
    """왕복 수수료(1계약) — settings 요율 × 약정금액 × 2. 상수 하드코딩 금지(493차·495차)."""
    from config.settings import FUTURES_COMMISSION_RATE
    pt = float(cfg.get("pt_value_krw", 50_000))
    return float(entry_price) * pt * float(FUTURES_COMMISSION_RATE) * 2.0


# ── 판정 ────────────────────────────────────────────────────────────────────

def compute():
    cfg = _cfg()
    if not cfg.get("enabled", False):
        return {"available": False, "reason": "채널 비활성"}
    sim = dict(cfg.get("sim") or {})
    for k, dv in (("stop_atr", 1.5), ("tp1_atr", 0.5), ("tp2_atr", 1.5),
                  ("tp1_fraction", 1 / 3.0), ("max_bars", 30), ("atr_window", 14)):
        sim.setdefault(k, dv)

    signals, has_col = _blocked_signals(cfg)
    if not signals:
        return {"available": False, "reason": "차단 후보 신호 0건", "column_present": has_col}

    days = sorted({ts[:10] for ts, _, _ in signals})
    candles = _candles(days)
    prepped = {}
    gap = int(cfg.get("nonoverlap_min", 3))
    pt = float(cfg.get("pt_value_krw", 50_000))

    # ② 비중첩 서브샘플 + 시뮬
    sample, last_min = [], {}
    dropped_overlap = dropped_nosim = 0
    for ts, d, src in signals:
        day = ts[:10]
        m = int(ts[11:13]) * 60 + int(ts[14:16])
        if day in last_min and m - last_min[day] < gap:
            dropped_overlap += 1
            continue
        if day not in prepped:
            rows = candles.get(day) or []
            prepped[day] = (rows,) + _prep(rows, int(sim["atr_window"]))
        rows, idx, atr = prepped[day]
        r = simulate(rows, idx, atr, ts, d, sim)
        if r is None:
            dropped_nosim += 1
            continue
        last_min[day] = m
        gross = r[0] * pt
        comm = _round_trip_commission(r[2], cfg)
        sample.append({"ts": ts, "day": day, "dir": d, "src": src, "pt": r[0],
                       "outcome": r[1], "gross_krw": gross, "comm_krw": comm,
                       "net_krw": gross - comm})

    res = {
        "available": True, "column_present": has_col,
        "n_signals": len(signals), "n_sample": len(sample),
        "dropped_overlap": dropped_overlap, "dropped_nosim": dropped_nosim,
        "n_gate": sum(1 for s in sample if s["src"] == "gate"),
        "n_legacy_proxy": sum(1 for s in sample if s["src"] == "legacy_proxy"),
        "days": len({s["day"] for s in sample}),
        "gross_krw": sum(s["gross_krw"] for s in sample),
        "commission_krw": sum(s["comm_krw"] for s in sample),
        "net_krw": sum(s["net_krw"] for s in sample),
        "sim_pt": sum(s["pt"] for s in sample),
        "win_rate": (sum(1 for s in sample if s["pt"] > 0) / len(sample)) if sample else None,
        "outcomes": {},
    }
    for s in sample:
        res["outcomes"][s["outcome"]] = res["outcomes"].get(s["outcome"], 0) + 1
    # 보고 열(판정 무관)
    by = defaultdict(lambda: {"n": 0, "net": 0.0})
    for s in sample:
        for key in (("dir", "LONG" if s["dir"] == 1 else "SHORT"), ("src", s["src"]),
                    ("hour", s["ts"][11:13])):
            b = by[key]
            b["n"] += 1
            b["net"] += s["net_krw"]
    res["report_columns"] = {"%s=%s" % k: v for k, v in sorted(by.items())}

    # 표본 관문
    if len(sample) < int(cfg.get("min_samples", 30)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = "비중첩 후보 %d < min_samples %d" % (len(sample), cfg.get("min_samples"))
        return res
    if res["days"] < int(cfg.get("min_days", 10)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = "거래일 %d < min_days %d" % (res["days"], cfg.get("min_days"))
        return res

    # ① 일자단위
    by_day = defaultdict(float)
    for s in sample:
        by_day[s["day"]] += s["net_krw"]
    diffs = list(by_day.values())
    p, pos, neg = _sign_test_p(diffs)
    res["day_net"] = {d: round(v) for d, v in sorted(by_day.items())}
    res["sign_test_p"], res["days_pos"], res["days_neg"] = p, pos, neg
    res["day_median_krw"] = sorted(diffs)[len(diffs) // 2]
    # ③ 최고 N일 제거
    kdrop = int(cfg.get("drop_best_days", 3))
    trimmed = sorted(diffs)[:-kdrop] if kdrop and len(diffs) > kdrop else diffs
    res["net_drop_best_krw"] = sum(trimmed)

    alpha = float(cfg.get("alpha", 0.05))
    cond_sig = p is not None and p < alpha
    cond_net = (res["net_krw"] > 0) if cfg.get("require_net_positive", True) else True
    cond_drop = (res["net_drop_best_krw"] > 0) if kdrop else True
    cond_dir = pos > neg
    if cond_sig and cond_net and cond_drop and cond_dir:
        res["verdict"] = "UNBLOCK_CANDIDATE"
        res["reason"] = ("차단을 풀면 수수료 차감 후에도 이익 — 승격 순서 %s 로 주간회의 안건"
                         % cfg.get("promotion_order"))
    else:
        res["verdict"] = "KEEP_BLOCK"
        why = []
        if not cond_sig:
            why.append("일자 p=%s ≥ α=%.2f" % ("N/A" if p is None else "%.3f" % p, alpha))
        if not cond_net:
            why.append("net %s ≤ 0" % _krw(res["net_krw"], True))
        if not cond_drop:
            why.append("최고 %d일 제거 후 %s" % (kdrop, _krw(res["net_drop_best_krw"], True)))
        if not cond_dir:
            why.append("양의 일수 %d ≤ 음의 일수 %d" % (pos, neg))
        res["reason"] = "풀어줄 근거 없음 — " + " · ".join(why)
    return res


def render(res):
    lines = ["[%s] 데이터이상 게이트 손익 — 봉 단위 반사실(수수료 포함)" % CHANNEL]
    if not res.get("available"):
        lines.append("  판정 불가: %s" % res.get("reason"))
        return "\n".join(lines)
    lines.append("  표본: 신호 %d → 비중첩 %d (gate %d / legacy_proxy %d) · 거래일 %d · 중복제외 %d · 시뮬불가 %d"
                 % (res["n_signals"], res["n_sample"], res["n_gate"], res["n_legacy_proxy"],
                    res["days"], res["dropped_overlap"], res["dropped_nosim"]))
    lines.append("  시뮬 %+.1fpt · gross %s · 수수료 %s · NET %s · 승률 %s · outcome %s"
                 % (res["sim_pt"], _krw(res["gross_krw"], True), _krw(res["commission_krw"]),
                    _krw(res["net_krw"], True),
                    "N/A" if res["win_rate"] is None else "%.0f%%" % (100 * res["win_rate"]),
                    res["outcomes"]))
    if "sign_test_p" in res:
        lines.append("  일자 +%d/−%d p=%s · 일자 중앙값 %s · 최고 %s일 제거 후 %s"
                     % (res["days_pos"], res["days_neg"],
                        "N/A" if res["sign_test_p"] is None else "%.3f" % res["sign_test_p"],
                        _krw(res["day_median_krw"], True), _cfg().get("drop_best_days"),
                        _krw(res["net_drop_best_krw"], True)))
    lines.append("  보고 열(판정 무관): " + ", ".join(
        "%s n=%d net=%s" % (k, v["n"], _krw(v["net"], True))
        for k, v in res["report_columns"].items()))
    lines.append("  판정: %s — %s" % (res.get("verdict"), res.get("reason")))
    if not res.get("column_present"):
        lines.append("  ⚠ ensemble_decisions.micro_regime_source 컬럼 없음 — F-A 배선 전 DB(대리 지표만)")
    return "\n".join(lines)


if __name__ == "__main__":
    guard_intraday("data_anomaly_gate_watch")
    r = compute()
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
    else:
        print(render(r))
