# -*- coding: utf-8 -*-
"""[MW0601 529차] 레그 위치(탈진 위치) 진입 채널 3종 판정기.

무엇을 묻는가
-------------
"이미 크게 달린 레그의 끝(극단 근처)에서 그 방향으로 들어가는 진입"이 손익을 깎는가.
2026-09-03 C1~C4가 전부 이 형태였고(528차), 사용자가 "탈진 위치에서 추세 방향 진입"으로 지목했다.

세 채널
-------
[A] `leg_exhaustion_entry_watch` — 레그 끝 순방향 진입. 판정 → 소프트 승격 안건(감점/사이즈½).
[C] `streak_leg_end_watch`       — TrendGate 지속 모드 완화 × 레그 끝 **결합**. 판정 → 결합 시 완화 미적용.
[E] `leg_entry_early_watch`      — 레그 초입 진입(거울상). **관측 전용**, 판정도 승격도 없다.

두 축의 정의(방향은 소비자가 곱한다 — 피처는 방향 무관)
    run  = 매수면 `dist_to_low_60m_atr`,  매도면 `dist_to_high_60m_atr`   (레그가 달린 거리)
    dist = 매수면 `dist_to_high_60m_atr`, 매도면 `dist_to_low_60m_atr`    (극단까지 거리)

값의 원천 2단
-------------
529차 스윙 피처 배선(`feature_wired_date`) 이후 분은 `ensemble_decisions.features`의 키를 읽고,
그 이전 분은 `raw_candles`로 **같은 산식을 재계산**한다(`source="replay_proxy"`). 사본이 아니라
원본 봉에서 다시 재는 것이라 오차가 없고, 두 원천이 겹치는 구간에서는 매 실행마다 대조한다
(`source_crosscheck`) — 배선이 옳은지 확인하는 유일한 수단이다(473차 `spread_extreme_watch` 규약).

방법론 (313차 5원칙)
--------------------
① 일자단위 부호검정이 1차 판정(신호단위 유의는 372차가 겪은 함정) ② 포지션은 `entry_ts`로 병합
(레그 단위 금지 — 계측 4원칙 ①) ③ 최악 N일 제거 후 부호 유지 ④ 합격선은 settings에서만 온다
⑤ [A]는 거울상 보존(`require_early_group_better`)까지 통과해야 한다 — 처리군을 누르는 조치가
레그 초입 승리군을 함께 누르면 순이익이 사라지기 때문이다.

⚠ 이 스크립트는 **판정만 한다.** 게이트를 켜지 않고, 임계를 제안하지 않는다.

실행:
    python scripts/leg_position_watch.py
    python scripts/leg_position_watch.py --json
    python scripts/leg_position_watch.py --channel A
"""
from __future__ import annotations

import collections
import datetime
import glob
import json
import math
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402

CH_A = "leg_exhaustion_entry_watch"
CH_C = "streak_leg_end_watch"
CH_E = "leg_entry_early_watch"


def _cfg(name):
    from config.settings import VALIDATION_CAMPAIGN
    return VALIDATION_CAMPAIGN.get(name) or {}


# ── 공통 유틸 ───────────────────────────────────────────────────────────────

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
    """🔴 `%`-포매팅 콤마 플래그는 py3.7에서 ValueError — `str.format`만 쓴다."""
    if v is None:
        return "N/A"
    return ("{:+,.0f}" if sign else "{:,.0f}").format(v)


def _mean(xs):
    return (sum(xs) / float(len(xs))) if xs else None


def _prev_min(ts):
    """진입 시각 → 결정 분봉(파이프라인은 HH:MM 봉을 HH:MM+1 에 처리해 진입한다)."""
    t = datetime.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M") - datetime.timedelta(minutes=1)
    return t.strftime("%Y-%m-%d %H:%M")


# ── 표본 ────────────────────────────────────────────────────────────────────

def _positions(cfg):
    """entry_ts 단위 포지션 — 수량 합, net 합(계측 4원칙 ①)."""
    from config.settings import TRADES_DB
    src = cfg.get("entry_source", "SYSTEM_AUTO")
    con = connect_ro(TRADES_DB)
    merged = collections.OrderedDict()
    try:
        cols = {r[1] for r in con.execute("PRAGMA table_info(trades)")}
        sel = "entry_ts, direction, COALESCE(net_pnl_krw, pnl_krw), quantity"
        if "entry_qty" in cols:
            sel += ", entry_qty"
        rows = con.execute(
            "SELECT %s FROM trades WHERE exit_ts IS NOT NULL AND entry_ts >= ? "
            "AND COALESCE(entry_source,'') = ? ORDER BY entry_ts"
            % sel, (cfg.get("data_start", "2026-07-14"), src)).fetchall()
    finally:
        con.close()
    for r in rows:
        m = merged.setdefault(r[0], {"entry_ts": r[0], "day": r[0][:10],
                                     "dir": 1 if r[1] == "LONG" else -1,
                                     "net": 0.0, "qty": 0, "qty_recorded": None})
        m["net"] += float(r[2] or 0.0)
        m["qty"] += int(r[3] or 1)
        if len(r) > 4 and m["qty_recorded"] is None:
            try:
                eq = int(r[4] or 0)
            except (TypeError, ValueError):
                eq = 0
            if eq > 0:
                m["qty_recorded"] = eq
    for m in merged.values():
        m["qty_final"] = m["qty_recorded"] or m["qty"]
    return list(merged.values())


def _db_swing(cfg):
    """결정 분 → 스윙 키 딕트. 529차 배선 이후 분에만 존재한다."""
    from config.settings import PREDICTIONS_DB
    n = int(cfg.get("lookback_min", 60))
    keys = ("dist_to_high_%dm_atr" % n, "dist_to_low_%dm_atr" % n,
            "bars_since_high_%dm" % n, "bars_since_low_%dm" % n, "swing_ready_%dm" % n)
    out = {}
    con = connect_ro(PREDICTIONS_DB)
    try:
        for ts, feats in con.execute(
                "SELECT ts, features FROM ensemble_decisions WHERE features IS NOT NULL "
                "AND date(ts) >= ? ORDER BY ts", (cfg.get("data_start", "2026-07-14"),)):
            if not feats or keys[0] not in feats:      # 문자열 사전검사 — JSON 파싱 비용 절감
                continue
            try:
                d = json.loads(feats)
            except (ValueError, TypeError):
                continue
            if keys[0] not in d:
                continue
            out[ts[:16]] = {k: d.get(k) for k in keys}
    finally:
        con.close()
    return out


def _candles(cfg):
    from config.settings import RAW_DATA_DB
    con = connect_ro(RAW_DATA_DB)
    by_day = collections.defaultdict(list)
    try:
        for ts, h, l, c in con.execute(
                "SELECT ts, high, low, close FROM raw_candles WHERE ts >= ? "
                "AND substr(ts,12,5) >= '08:45' ORDER BY ts",
                (cfg.get("data_start", "2026-07-14"),)):
            by_day[ts[:10]].append((ts[:16], float(h), float(l), float(c)))
    finally:
        con.close()
    return by_day


def _replay_swing(rows, i, n):
    """`compute_swing_features`와 같은 산식을 봉 배열에서 재계산(배선 전 구간용)."""
    if i < 15:
        return None
    trs = [max(rows[k][1] - rows[k][2], abs(rows[k][1] - rows[k - 1][3]),
               abs(rows[k][2] - rows[k - 1][3])) for k in range(max(1, i - 13), i + 1)]
    atr = (sum(trs) / len(trs)) if trs else 0.0
    if atr <= 1e-6:
        return None
    seg = rows[max(0, i - n + 1):i + 1]
    close = rows[i][3]
    hi = max(r[1] for r in seg)
    lo = min(r[2] for r in seg)
    return {
        "dist_to_high_%dm_atr" % n: min(max((hi - close) / atr, 0.0), 20.0),
        "dist_to_low_%dm_atr" % n: min(max((close - lo) / atr, 0.0), 20.0),
        "bars_since_high_%dm" % n: (len(seg) - 1) - max(k for k, r in enumerate(seg) if r[1] == hi),
        "bars_since_low_%dm" % n: (len(seg) - 1) - max(k for k, r in enumerate(seg) if r[2] == lo),
        "swing_ready_%dm" % n: len(seg) >= n,
    }


def _attach_leg(cfg, positions):
    """각 포지션에 run/dist/ready/source 를 붙인다. 반환 (attached, stats)."""
    n = int(cfg.get("lookback_min", 60))
    dbmap = _db_swing(cfg)
    cand = _candles(cfg)
    prepped = {}
    stats = collections.Counter()
    cross = {"compared": 0, "run_mismatch": 0, "dist_mismatch": 0}
    out = []
    for p in positions:
        dm = _prev_min(p["entry_ts"])
        d = p["dir"]
        db = dbmap.get(dm) or dbmap.get(p["entry_ts"][:16])
        day = p["day"]
        if day not in prepped:
            rows = cand.get(day) or []
            prepped[day] = (rows, {r[0]: i for i, r in enumerate(rows)})
        rows, idx = prepped[day]
        rp = _replay_swing(rows, idx[dm], n) if dm in idx else None

        def _rd(src):
            if src is None:
                return None
            run = src.get("dist_to_low_%dm_atr" % n) if d == 1 else src.get("dist_to_high_%dm_atr" % n)
            dist = src.get("dist_to_high_%dm_atr" % n) if d == 1 else src.get("dist_to_low_%dm_atr" % n)
            if run is None or dist is None:
                return None
            return float(run), float(dist), bool(src.get("swing_ready_%dm" % n))

        a, b = _rd(db), _rd(rp)
        if a is not None and b is not None:
            cross["compared"] += 1
            if abs(a[0] - b[0]) > 0.05:
                cross["run_mismatch"] += 1
            if abs(a[1] - b[1]) > 0.05:
                cross["dist_mismatch"] += 1
        use, src_name = (a, "db") if a is not None else ((b, "replay_proxy") if b is not None else (None, None))
        if use is None:
            stats["unmeasured"] += 1
            continue
        q = dict(p)
        q["run"], q["dist"], q["ready"] = use
        q["source"] = src_name
        stats[src_name] += 1
        out.append(q)
    return out, {"n_positions": len(positions), "n_measured": len(out),
                 "unmeasured": stats["unmeasured"], "by_source": {"db": stats["db"],
                 "replay_proxy": stats["replay_proxy"]}, "source_crosscheck": cross}


def _trendgate_minutes(cfg):
    """[C] `[TrendGate] UP|DN 지속 모드 ON/OFF` 전이 → (day, 'UP'|'DN') 활성 구간.

    ⚠ DB에 상태가 없어 로그가 유일 원천이다(529차 확인). 로그 보관 기간이 표본 상한.
    """
    pat = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}):\d{2} .*\[TrendGate\] (UP|DN) 추세 지속 모드 (ON|OFF)")
    trans = collections.defaultdict(list)
    start = cfg.get("data_start", "2026-07-14").replace("-", "")
    files = sorted(glob.glob(os.path.join(_ROOT, "logs", "2026*_SIGNAL.log")))
    for f in files:
        if os.path.basename(f)[:8] < start:
            continue
        try:
            fh = open(f, encoding="utf-8", errors="ignore")
        except IOError:
            continue
        with fh:
            for line in fh:
                m = pat.match(line)
                if m:
                    trans[(m.group(1), m.group(3))].append((m.group(2), m.group(4)))
    return trans, len(files)


def _streak_active(trans, day, hhmm, direction):
    side = "UP" if direction == 1 else "DN"
    act = False
    for t, onoff in sorted(trans.get((day, side), [])):
        if t > hhmm:
            break
        act = (onoff == "ON")
    return act


# ── 판정 공통 ───────────────────────────────────────────────────────────────

def _paired_day_diffs(treat, control):
    """같은 날 (처리군 평균 − 대조군 평균). 음수 = 처리군이 그날 열세."""
    a, b = collections.defaultdict(list), collections.defaultdict(list)
    for r in treat:
        a[r["day"]].append(r["net"])
    for r in control:
        b[r["day"]].append(r["net"])
    days = sorted(set(a) & set(b))
    return [(d, _mean(a[d]) - _mean(b[d])) for d in days]


def _group_stat(rows):
    if not rows:
        return {"n": 0, "days": 0, "net": 0.0, "avg": None, "win_rate": None}
    return {"n": len(rows), "days": len({r["day"] for r in rows}),
            "net": sum(r["net"] for r in rows), "avg": _mean([r["net"] for r in rows]),
            "win_rate": sum(1 for r in rows if r["net"] > 0) / float(len(rows))}


# ── [A] leg_exhaustion_entry_watch ──────────────────────────────────────────

def compute_a():
    cfg = _cfg(CH_A)
    if not cfg.get("enabled", False):
        return {"channel": CH_A, "available": False, "reason": "채널 비활성"}
    pos = _positions(cfg)
    if not pos:
        return {"channel": CH_A, "available": False, "reason": "포지션 0건"}
    rows, meta = _attach_leg(cfg, pos)
    run_min = float(cfg["run_atr_min"])
    dist_max = float(cfg["dist_atr_max"])
    treat = [r for r in rows if r["ready"] and r["run"] >= run_min and r["dist"] <= dist_max]
    control = [r for r in rows if r not in treat]
    early = [r for r in rows if r["ready"] and r["run"] < run_min]

    res = {"channel": CH_A, "available": True, "cut": {"run_atr_min": run_min, "dist_atr_max": dist_max},
           "meta": meta, "treat": _group_stat(treat), "control": _group_stat(control),
           "early": _group_stat(early),
           "promotion_order": cfg.get("promotion_order"),
           "hard_block_forbidden": cfg.get("hard_block_forbidden", True)}

    if res["treat"]["n"] < int(cfg.get("min_samples", 40)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = "처리군 %d < min_samples %d" % (res["treat"]["n"], cfg.get("min_samples"))
        return res
    if res["treat"]["days"] < int(cfg.get("min_days", 25)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = "처리군 거래일 %d < min_days %d" % (res["treat"]["days"], cfg.get("min_days"))
        return res

    paired = _paired_day_diffs(treat, control)
    res["paired_days"] = len(paired)
    if len(paired) < int(cfg.get("min_days", 25)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = "두 군이 함께 있는 거래일 %d < min_days %d" % (len(paired), cfg.get("min_days"))
        return res
    diffs = [v for _, v in paired]
    p, n_pos, n_neg = _sign_test_p(diffs)
    res["sign_test_p"] = p
    res["days_treat_worse"] = n_neg     # diff < 0 = 처리군 열세
    res["days_treat_better"] = n_pos
    res["day_mean_diff_krw"] = _mean(diffs)

    k = int(cfg.get("drop_worst_days", 3))
    trimmed = sorted(diffs)[k:] if k and len(diffs) > k else diffs   # 처리군에 가장 불리한 날 제거
    res["day_mean_diff_drop_worst_krw"] = _mean(trimmed)

    early_better = (res["early"]["avg"] is not None and res["treat"]["avg"] is not None
                    and res["early"]["avg"] > res["treat"]["avg"])
    res["early_group_better"] = early_better

    alpha = float(cfg.get("alpha", 0.05))
    cond_sig = p is not None and p < alpha
    cond_dir = n_neg > n_pos
    cond_drop = (res["day_mean_diff_drop_worst_krw"] is not None
                 and res["day_mean_diff_drop_worst_krw"] < 0)
    cond_early = early_better if cfg.get("require_early_group_better", True) else True
    if cond_sig and cond_dir and cond_drop and cond_early:
        res["verdict"] = "SOFT_DEMOTE_CANDIDATE"
        res["reason"] = ("처리군이 일자단위로 유의하게 열세 — 승격 순서 %s 로 주간회의 안건"
                         "(하드차단 금지)" % cfg.get("promotion_order"))
    else:
        why = []
        if not cond_sig:
            why.append("일자 p=%s ≥ α=%.2f" % ("N/A" if p is None else "%.3f" % p, alpha))
        if not cond_dir:
            why.append("열세일 %d ≤ 우세일 %d" % (n_neg, n_pos))
        if not cond_drop:
            why.append("최악 %d일 제거 후 평균차 %s (부호 미유지)" % (k, _krw(res["day_mean_diff_drop_worst_krw"], True)))
        if not cond_early:
            why.append("거울상 미충족 — 초입군 평균(%s)이 처리군(%s) 이하" % (_krw(res["early"]["avg"], True), _krw(res["treat"]["avg"], True)))
        res["verdict"] = "NO_CHANGE"
        res["reason"] = "조치 근거 없음 — " + " · ".join(why)
    return res


# ── [C] streak_leg_end_watch ────────────────────────────────────────────────

def compute_c():
    cfg = _cfg(CH_C)
    if not cfg.get("enabled", False):
        return {"channel": CH_C, "available": False, "reason": "채널 비활성"}
    acfg = dict(_cfg(CH_A))
    acfg.update({"data_start": cfg.get("data_start"), "entry_source": cfg.get("entry_source")})
    pos = _positions(cfg)
    rows, meta = _attach_leg(acfg, pos)
    trans, n_files = _trendgate_minutes(cfg)
    if not trans:
        return {"channel": CH_C, "available": False,
                "reason": "TrendGate 전이 로그 0건 — 로그 보관 기간 확인(원천이 로그뿐이다)",
                "log_files_scanned": n_files}
    run_min = float(cfg["run_atr_min"])
    dist_max = float(cfg["dist_atr_max"])
    for r in rows:
        r["streak"] = _streak_active(trans, r["day"], r["entry_ts"][11:16], r["dir"])
    on = [r for r in rows if r["streak"]]
    treat = [r for r in on if r["ready"] and r["run"] >= run_min and r["dist"] <= dist_max]
    control = [r for r in on if r not in treat]

    res = {"channel": CH_C, "available": True, "log_files_scanned": n_files,
           "meta": meta, "streak_on": _group_stat(on), "treat": _group_stat(treat),
           "control": _group_stat(control), "promotion_order": cfg.get("promotion_order")}
    if res["treat"]["n"] < int(cfg.get("min_samples", 20)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = "처리군 %d < min_samples %d" % (res["treat"]["n"], cfg.get("min_samples"))
        return res
    if res["treat"]["days"] < int(cfg.get("min_days", 10)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = "처리군 거래일 %d < min_days %d" % (res["treat"]["days"], cfg.get("min_days"))
        return res
    paired = _paired_day_diffs(treat, control)
    res["paired_days"] = len(paired)
    if len(paired) < int(cfg.get("min_days", 10)):
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = "두 군이 함께 있는 거래일 %d < min_days %d" % (len(paired), cfg.get("min_days"))
        return res
    diffs = [v for _, v in paired]
    p, n_pos, n_neg = _sign_test_p(diffs)
    k = int(cfg.get("drop_worst_days", 1))
    trimmed = sorted(diffs)[k:] if k and len(diffs) > k else diffs
    res.update({"sign_test_p": p, "days_treat_worse": n_neg, "days_treat_better": n_pos,
                "day_mean_diff_krw": _mean(diffs),
                "day_mean_diff_drop_worst_krw": _mean(trimmed)})
    alpha = float(cfg.get("alpha", 0.05))
    ok = (p is not None and p < alpha and n_neg > n_pos
          and res["day_mean_diff_drop_worst_krw"] is not None
          and res["day_mean_diff_drop_worst_krw"] < 0)
    res["verdict"] = "SKIP_RELAX_CANDIDATE" if ok else "NO_CHANGE"
    res["reason"] = ("결합(지속모드 완화 × 레그 끝)이 일자단위로 유의하게 열세 — "
                     "**완화 미적용**만 안건(완화 자체는 유지)" if ok else
                     "조치 근거 없음 — 일자 p=%s, 열세일 %d/우세일 %d"
                     % ("N/A" if p is None else "%.3f" % p, n_neg, n_pos))
    return res


# ── [E] leg_entry_early_watch (관측 전용) ───────────────────────────────────

def compute_e():
    cfg = _cfg(CH_E)
    if not cfg.get("enabled", False):
        return {"channel": CH_E, "available": False, "reason": "채널 비활성"}
    acfg = dict(_cfg(CH_A))
    acfg.update({"data_start": cfg.get("data_start"), "entry_source": cfg.get("entry_source")})
    rows, meta = _attach_leg(acfg, _positions(cfg))
    cut = float(cfg.get("run_atr_max", 2.0))
    early = [r for r in rows if r["ready"] and r["run"] <= cut]
    rest = [r for r in rows if r not in early]
    return {"channel": CH_E, "available": True, "observe_only": True, "cut_run_atr_max": cut,
            "meta": meta, "early": _group_stat(early), "rest": _group_stat(rest),
            "sample_reached": len(early) >= int(cfg.get("min_samples", 20)),
            "verdict": "OBSERVE",
            "reason": "관측 전용 — 가점·승격 없음(진입을 늘리는 방향이라 faststop_discovery 결정과 충돌). "
                      "[A]의 거울상 보존 판정 입력으로 쓴다"}


# ── 렌더 ────────────────────────────────────────────────────────────────────

def _g(label, s):
    if not s or not s.get("n"):
        return "  %-8s n=0" % label
    return ("  %-8s n=%3d(%2d일) net=%11s avg=%10s 승률=%3.0f%%"
            % (label, s["n"], s["days"], _krw(s["net"], True), _krw(s["avg"], True),
               100 * (s["win_rate"] or 0)))


def render(res):
    ch = res.get("channel")
    out = ["[%s]" % ch]
    if not res.get("available"):
        out.append("  판정 불가: %s" % res.get("reason"))
        return "\n".join(out)
    m = res.get("meta") or {}
    if m:
        cc = m.get("source_crosscheck") or {}
        out.append("  표본: 포지션 %d → 계측 %d (db %d / replay_proxy %d · 미계측 %d)"
                   % (m.get("n_positions", 0), m.get("n_measured", 0),
                      (m.get("by_source") or {}).get("db", 0),
                      (m.get("by_source") or {}).get("replay_proxy", 0), m.get("unmeasured", 0)))
        if cc.get("compared"):
            out.append("  원천 대조: %d건 비교 · run 불일치 %d · dist 불일치 %d %s"
                       % (cc["compared"], cc["run_mismatch"], cc["dist_mismatch"],
                          "(일치)" if not (cc["run_mismatch"] or cc["dist_mismatch"]) else "← 배선 점검 필요"))
    if ch == CH_A:
        out.append("  컷(고정): run >= %.1f ATR 且 극단까지 <= %.1f ATR"
                   % (res["cut"]["run_atr_min"], res["cut"]["dist_atr_max"]))
        out.append(_g("처리군", res["treat"]))
        out.append(_g("대조군", res["control"]))
        out.append(_g("초입군", res["early"]))
    elif ch == CH_C:
        out.append(_g("streakON", res["streak_on"]))
        out.append(_g("처리군", res["treat"]))
        out.append(_g("대조군", res["control"]))
    elif ch == CH_E:
        out.append("  컷: run <= %.1f ATR" % res["cut_run_atr_max"])
        out.append(_g("초입군", res["early"]))
        out.append(_g("나머지", res["rest"]))
        out.append("  표본 도달: %s" % ("예" if res.get("sample_reached") else "아니오"))
    if "sign_test_p" in res:
        out.append("  일자쌍 %d: 처리군 열세 %d / 우세 %d · p=%s · 평균차 %s · 최악일 제거 후 %s"
                   % (res.get("paired_days", 0), res.get("days_treat_worse", 0),
                      res.get("days_treat_better", 0),
                      "N/A" if res.get("sign_test_p") is None else "%.3f" % res["sign_test_p"],
                      _krw(res.get("day_mean_diff_krw"), True),
                      _krw(res.get("day_mean_diff_drop_worst_krw"), True)))
    if ch == CH_A and "early_group_better" in res:
        out.append("  거울상 보존(초입군 > 처리군): %s" % ("충족" if res["early_group_better"] else "미충족"))
    out.append("  판정: %s — %s" % (res.get("verdict"), res.get("reason")))
    if res.get("hard_block_forbidden"):
        out.append("  ⚠ 하드차단 금지(317차 FalseBlock) — 승격은 감점/사이즈 축소까지만")
    return "\n".join(out)


def compute_all():
    return [compute_a(), compute_c(), compute_e()]


if __name__ == "__main__":
    guard_intraday("leg_position_watch")
    sel = None
    if "--channel" in sys.argv:
        sel = sys.argv[sys.argv.index("--channel") + 1].upper()
    fns = {"A": compute_a, "C": compute_c, "E": compute_e}
    results = [fns[sel]()] if sel in fns else compute_all()
    if "--json" in sys.argv:
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    else:
        for r in results:
            print(render(r))
            print()
