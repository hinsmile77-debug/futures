# -*- coding: utf-8 -*-
"""[MW0602 486차 / 1-9] 09:20~09:29 "앙상블 A등급만 허용" 게이트 — 소급 판정.

캠페인 채널 **[55]**. 사전등록 기준은
`config/settings.py:VALIDATION_CAMPAIGN["early_window_gate_shadow"]`.

이 스크립트가 존재하는 이유
---------------------------
`main.py`의 09:20~09:29 분기는 앙상블 등급 A만 통과시킨다. 그런데 앙상블 A는
conf>=0.70 요구이고, 방향성 conf(`direction != 0`)는 2026-06-01 이후 0.60에도 닿은
적이 없다(0819 리포트 1-9). ⇒ 그 10분은 **문서상 "조건부 허용", 실제로는 전면 금지**로
동작해 왔다.

476차 F-6 Phase A는 로그·문서에 사실을 병기했을 뿐 **분기 동작은 그대로 뒀다** —
임계·존 재설계는 매매 정책 변경이라 주간회의 소관이기 때문이다. 이 스크립트는 그
주간회의에 실측 근거를 넣는다. 묻는 것은 하나다:

    "그 10분에 차단된 신호들은 실제로 손실 방향이었는가?"

왜 표본을 기다릴 필요가 없는가
------------------------------
차단된 신호는 `ensemble_decisions.checklist_reason='조건부구간'`으로 **이미 전량 남아
있다**. 섀도 테이블 신설도, 라이브 배선도, **노출 증가도 필요 없다** — 473차 F-8
`spread_extreme_watch.py`와 같은 소급 판정 경로다.

방법론 (313차 5원칙)
--------------------
① **일자단위 1차 판정** — 같은 날 09:20~09:29 신호들은 같은 레짐·같은 모델 스냅샷을
   공유해 독립 관측치가 아니다. 372차가 신호단위 유의(p=0.0005)가 일자단위에서
   소멸(r=-0.099)하는 것을 실측했다.
② **overlap** — 창이 10분뿐이라 같은 날 최대 10건이 겹친다. 일자단위 집계로 흡수한다.
③ **이상치 분해** — 최악 1일 제거 후에도 부호가 유지되는지 본다.
④ **사전등록** — 합격선은 settings에 먼저 박혔다. 이 스크립트는 읽기만 한다.
⑤ **부호 일관성** — 전반부/후반부로 갈라 부호가 뒤집히지 않는지 확인한다.

🔴 **σ 성숙도 축 (이 채널 고유)**
   09:20은 sigma_20봉 미수집 금지가 막 풀린 직후이고, 원 코드 주석은 게이트 근거를
   conf가 아니라 *"방법3 sigma 안정화 기준"*이라 적고 있다. 즉 "conf 판별력이 약하니
   게이트도 무의미하다"는 논증은 이 축을 건드리지 못한다. 창이 정확히 09:20~09:29라
   **분(minute)이 곧 σ 표본수의 대리변수**이므로 전반/후반 5분으로 층화해 함께 낸다.
   **두 층의 부호가 갈리면 그 자체가 판정 보류 사유다.**

청산 시뮬 관례 — 라이브와 같은 산식을 쓴다
------------------------------------------
진입가 = 신호 분봉의 `close` (라이브 `hurst_gate_shadow` 기록 관례와 동일).
스톱/TP1 거리 = `scripts/exit_replay.py:geometry()` **재사용**
(`ATR_STOP_MULT` · `ATR_HORIZON_TP1_MULT` · `HURST_REGIME_ATR_MULT`).
**새 산식을 만들지 않는다.** 창 안에서 first-touch, 동시 터치 시 STOP 우선
(signal_decay·TB 레이블·hurst_gate_shadow 공통 관례), 미터치 시 마지막 종가.
15:10 이후로는 넘어가지 않는다(절대원칙 §1).

⚠ 산출되는 `hyp_pnl_pts`는 **1계약·TP1상한·미실현 시뮬**이다. 실현손익이 아니며
  원(₩) 단위 채널과 직접 더하거나 비교하지 말 것.
⚠ 이 수는 "체크리스트 **이전**까지 살아남은 신호"를 센다. 체크리스트(CORE `vwap`
  강제 X)·ToxicityGate·Hurst·JointGate는 이 분기 **뒤**라 미평가 = **미측정**이지
  통과가 아니다(계측 4원칙 ②). 실제 진입 전환율은 이보다 낮다.

실행:
    python scripts/early_window_gate_shadow.py
    python scripts/early_window_gate_shadow.py --json    # 기계 판독용
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from collections import defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.settings import (  # noqa: E402
    VALIDATION_CAMPAIGN,
    PREDICTIONS_DB,
    RAW_DATA_DB,
    TRADES_DB,
    ENTRY_HORIZON_LOW_BLOCK,
    ENTRY_HORIZON_B1,
    ENTRY_HORIZON_B2,
    FUTURES_COMMISSION_RATE,
    TICK_SIZE,
)
from scripts.exit_replay import geometry  # noqa: E402

_TS_FMT = "%Y-%m-%d %H:%M:%S"
_FORCE_HHMM = "15:10"          # 절대원칙 §1 — 오버나이트 금지
CFG = VALIDATION_CAMPAIGN["early_window_gate_shadow"]


# ──────────────────────────────────────────────────────────────────────────
# 공용 소도구
# ──────────────────────────────────────────────────────────────────────────
def _conn(path):
    c = sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def _hurst_bucket(h):
    """라이브 `_entry_hurst_bucket` 과 같은 경계 (0.45 / 0.55)."""
    try:
        h = float(h)
    except (TypeError, ValueError):
        return "neutral"
    if h >= 0.55:
        return "trend"
    if h < 0.45:
        return "mean-revert"
    return "neutral"


def _entry_horizon(atr, thr1m):
    """`model/ensemble_decision.py:select_entry_horizon()` 과 같은 경계."""
    try:
        feas = float(atr) / (float(thr1m) + 1e-9)
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    if feas < ENTRY_HORIZON_LOW_BLOCK:
        return None
    if feas < ENTRY_HORIZON_B1:
        return "1m"
    if feas < ENTRY_HORIZON_B2:
        return "3m"
    return "5m"


def _roundtrip_cost_pt(avg_price):
    """왕복 비용(pt) — `generate_validation_campaign_report.py:_roundtrip_cost_pt()` 와
    **같은 산식**을 쓴다(새 숫자를 만들지 않는다, 471차 G-2 규율).
        = 수수료 2×price×rate + 슬리피지 2×틱
    """
    slip = float(VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))
    return 2.0 * float(avg_price) * FUTURES_COMMISSION_RATE + 2.0 * slip * TICK_SIZE


def _sign_test_p(n_pos, n_neg):
    """양측 이항 부호검정 — `generate_validation_campaign_report.py:_sign_test_p()` 와 동일 정의."""
    n = n_pos + n_neg
    if n == 0:
        return 1.0
    k = min(n_pos, n_neg)
    # sum_{i=0..k} C(n,i) * 0.5^n * 2
    total = 0.0
    c = 1.0
    for i in range(0, k + 1):
        if i:
            c = c * (n - i + 1) / i
        total += c
    p = 2.0 * total * (0.5 ** n)
    return min(1.0, p)


# ──────────────────────────────────────────────────────────────────────────
# 자료 수집
# ──────────────────────────────────────────────────────────────────────────
def load_blocked():
    """차단 신호 전량 — data_start 이후, 창 안, 마커 일치."""
    out = []
    with _conn(PREDICTIONS_DB) as c:
        rows = c.execute(
            "SELECT ts, direction, confidence, min_conf, grade, features, "
            "       coherence_blocked, gate_blocked, meta_action "
            "  FROM ensemble_decisions "
            " WHERE checklist_reason = ? AND substr(ts,1,10) >= ? "
            " ORDER BY ts",
            (CFG["block_reason"], CFG["data_start"]),
        ).fetchall()
    ws, we = CFG["window_start_hm"], CFG["window_end_hm"]
    for r in rows:
        hm = r["ts"][11:16]
        if not (ws <= hm <= we):
            continue
        try:
            f = json.loads(r["features"] or "{}")
        except Exception:
            f = {}
        atr = f.get("atr")
        if not atr:
            continue                      # ATR 없으면 기하를 못 만든다 → 미측정
        out.append({
            "ts": r["ts"],
            "day": r["ts"][:10],
            "hm": hm,
            "direction": int(r["direction"] or 0),
            "conf": float(r["confidence"] or 0.0),
            "min_conf": (float(r["min_conf"]) if r["min_conf"] is not None else None),
            "grade": r["grade"],
            "atr": float(atr),
            "hurst": f.get("hurst"),
            "thr1m": f.get("threshold_1m") or f.get("threshold_move_1m"),
            "feas": f.get("threshold_feasibility"),
            "coh_blocked": int(r["coherence_blocked"] or 0),
            "gate_blocked": int(r["gate_blocked"] or 0),
            "meta_action": r["meta_action"],
        })
    return out


def load_bars(days):
    """일자별 {ts: (high, low, close)} — raw_candles."""
    if not days:
        return {}
    lo, hi = min(days) + " 09:00:00", max(days) + " 15:10:00"
    bars = {}
    with _conn(RAW_DATA_DB) as c:
        for r in c.execute(
            "SELECT ts, high, low, close FROM raw_candles "
            " WHERE ts >= ? AND ts <= ? ORDER BY ts", (lo, hi)
        ):
            bars[r["ts"]] = (r["high"], r["low"], r["close"])
    return bars


def baseline_win_rate():
    """대조 승률 — 같은 기간 실체결 포지션 단위 승률."""
    try:
        with _conn(TRADES_DB) as c:
            r = c.execute(
                "SELECT AVG(w) FROM (SELECT CASE WHEN SUM(COALESCE(net_pnl_krw,pnl_krw)) > 0 "
                "  THEN 1.0 ELSE 0.0 END AS w FROM trades "
                " WHERE exit_ts IS NOT NULL AND exit_ts >= ? GROUP BY entry_ts)",
                (CFG["data_start"],),
            ).fetchone()
        return float(r[0]) if r and r[0] is not None else None
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────────────────
# counterfactual 시뮬
# ──────────────────────────────────────────────────────────────────────────
def simulate(sig, bars):
    """차단 신호 1건 → (outcome, hyp_pnl_pts). 라이브 관례와 같은 산식."""
    import datetime as _dt

    base = _dt.datetime.strptime(sig["ts"][:16] + ":00", _TS_FMT)
    entry_px = bars.get(sig["ts"][:17] + "00", (None, None, None))[2]
    if entry_px is None:
        return None, None, None
    hz = _entry_horizon(sig["atr"], sig["thr1m"]) if sig["thr1m"] else None
    if hz is None and sig.get("feas") is not None:
        # threshold_1m 이 features 에 없을 때 — feasibility 원값에서 역산
        feas = float(sig["feas"])
        hz = (None if feas < ENTRY_HORIZON_LOW_BLOCK
              else "1m" if feas < ENTRY_HORIZON_B1
              else "3m" if feas < ENTRY_HORIZON_B2 else "5m")
    if hz is None:
        return None, None, None          # 저변동성 → 라이브도 진입 안 했다
    sig["entry_px"] = float(entry_px)
    bucket = _hurst_bucket(sig["hurst"])
    stop_pts, tp1_pts, _, _ = geometry(hz, bucket, sig["atr"])
    is_long = sig["direction"] > 0
    stop_p = entry_px - stop_pts if is_long else entry_px + stop_pts
    tp1_p = entry_px + tp1_pts if is_long else entry_px - tp1_pts

    outcome, exit_px, last_close = "NEITHER", None, None
    for m in range(1, int(CFG["cf_window_min"]) + 1):
        mid = base + _dt.timedelta(minutes=m)
        if mid.strftime("%H:%M") > _FORCE_HHMM:
            break
        b = bars.get(mid.strftime(_TS_FMT))
        if not b:
            continue
        hi, lo, cl = b
        if hi is None or lo is None:
            continue
        last_close = cl if cl is not None else last_close
        hit_stop = (lo <= stop_p) if is_long else (hi >= stop_p)
        hit_tp = (hi >= tp1_p) if is_long else (lo <= tp1_p)
        if hit_stop:                      # 동시 터치 → STOP 우선(보수적, 공통 관례)
            outcome, exit_px = "STOP", stop_p
            break
        if hit_tp:
            outcome, exit_px = "TP1", tp1_p
            break
    if exit_px is None:
        if last_close is None:
            return None, None, None
        exit_px = last_close
    # (+) = 차단이 이득을 놓쳤다(차단 부당 근거) / (-) = 차단이 손실을 회피했다
    hyp = (exit_px - entry_px) if is_long else (entry_px - exit_px)
    return outcome, round(hyp, 4), hz


# ──────────────────────────────────────────────────────────────────────────
# 판정
# ──────────────────────────────────────────────────────────────────────────
def evaluate():
    out = {"verdict": "INSUFFICIENT", "channel": "[55]",
           "badge": "[1계약·TP1상한·미실현 시뮬]"}
    sigs = load_blocked()
    if not sigs:
        out["reason"] = ("차단 표본 0건 — 마커('%s')가 바뀌었거나 아직 발생하지 않았다"
                         % CFG["block_reason"])
        return out, []
    bars = load_bars(sorted({s["day"] for s in sigs}))

    resolved = []
    for s in sigs:
        oc, hyp, hz = simulate(s, bars)
        if hyp is None:
            continue
        s.update({"outcome": oc, "hyp": hyp, "hz": hz})
        resolved.append(s)

    n = len(resolved)
    days = sorted({s["day"] for s in resolved})
    avg_px = (sum(s["entry_px"] for s in resolved) / float(n)) if n else 0.0
    out.update({
        "n_blocked_raw": len(sigs),
        "n_resolved": n,
        "n_days": len(days),
        "day_first": days[0] if days else None,
        "day_last": days[-1] if days else None,
        "avg_entry_px": round(avg_px, 2),
        "cost_pt": (round(_roundtrip_cost_pt(avg_px), 4) if n else None),
    })
    if not n:
        out["reason"] = "분봉 부족으로 재구성 0건"
        return out, resolved

    total = sum(s["hyp"] for s in resolved)
    n_win = sum(1 for s in resolved if s["hyp"] > 0)
    by_day = defaultdict(float)
    for s in resolved:
        by_day[s["day"]] += s["hyp"]
    d_pos = sum(1 for v in by_day.values() if v > 0)
    d_neg = sum(1 for v in by_day.values() if v < 0)
    base_wr = baseline_win_rate()

    out.update({
        "total_hyp_pnl_pts": round(total, 4),
        "win_rate": round(n_win / float(n), 4),
        "baseline_win_rate": (round(base_wr, 4) if base_wr is not None else None),
        "day_pos": d_pos, "day_neg": d_neg,
        "day_sign_p": round(_sign_test_p(d_pos, d_neg), 4),
        "outcome_mix": {k: sum(1 for s in resolved if s["outcome"] == k)
                        for k in ("STOP", "TP1", "NEITHER")},
        "horizon_mix": {k: sum(1 for s in resolved if s["hz"] == k)
                        for k in ("1m", "3m", "5m")},
    })

    # ③ 이상치 분해 — 최악(가장 큰 기여) 1일 제거 후 부호 유지
    k = int(CFG["drop_worst_days"])
    worst = sorted(by_day.items(), key=lambda kv: abs(kv[1]), reverse=True)[:k]
    drop_total = total - sum(v for _, v in worst)
    out["drop_worst_days"] = [d for d, _ in worst]
    out["drop_worst_total_pt"] = round(drop_total, 4)
    out["drop_worst_sign_kept"] = bool(
        (total > 0 and drop_total > 0) or (total <= 0 and drop_total <= 0))

    # ⑤ 부호 일관성 — 전반부/후반부
    half = len(days) // 2
    h1 = sum(v for d, v in by_day.items() if d in set(days[:half]))
    h2 = sum(v for d, v in by_day.items() if d in set(days[half:]))
    out["half_split_pt"] = [round(h1, 4), round(h2, 4)]
    out["half_sign_consistent"] = bool((h1 > 0) == (h2 > 0))

    # 🔴 σ 성숙도 층화 — 이 채널 고유
    sp = CFG["sigma_split_hm"]
    e = [s for s in resolved if s["hm"] < sp]
    l = [s for s in resolved if s["hm"] >= sp]
    se, sl = sum(s["hyp"] for s in e), sum(s["hyp"] for s in l)
    out["sigma_split"] = {
        "early_%s~%s" % (CFG["window_start_hm"], sp):
            {"n": len(e), "hyp_pt": round(se, 4)},
        "late_%s~%s" % (sp, CFG["window_end_hm"]):
            {"n": len(l), "hyp_pt": round(sl, 4)},
        "sign_consistent": bool(len(e) == 0 or len(l) == 0 or (se > 0) == (sl > 0)),
    }

    # ── 사전등록 판정 ────────────────────────────────────────────
    if n < int(CFG["min_samples"]) or len(days) < int(CFG["min_days"]):
        out["reason"] = ("표본 미달 (n=%d<%d 또는 거래일=%d<%d) — 판정 보류"
                         % (n, CFG["min_samples"], len(days), CFG["min_days"]))
        return out, resolved

    gates = {
        "hyp > 왕복비용×%.1f" % CFG["cost_mult"]:
            total > out["cost_pt"] * float(CFG["cost_mult"]),
        "승률 > 기준선": (base_wr is not None and out["win_rate"] > base_wr),
        "일자 부호검정 p < %.2f" % CFG["alpha"]:
            out["day_sign_p"] < float(CFG["alpha"]),
        "drop-worst 부호 유지": out["drop_worst_sign_kept"],
        "전후반 부호 일관": out["half_sign_consistent"],
        "σ 층 부호 일관": out["sigma_split"]["sign_consistent"],
    }
    out["gates"] = gates
    out["verdict"] = ("BLOCK_UNJUSTIFIED" if all(gates.values())
                      else "BLOCK_JUSTIFIED")

    # ── 관찰 전용 부록 — 🔴 판정에 관여하지 않는다 ────────────────────────
    # 아래 두 블록은 **사후탐색(post-hoc)** 이다. 313차 ④ — *"사후 데이터로 기준을
    # 움직이지 않는다"* 에 따라 **어떤 기준도 여기서 만들지 않는다.** 다음 안건의
    # 가설 후보로만 쓰고, 쓰려면 **사전등록 후 신규 표본**으로 판정할 것.
    out["_posthoc_warning"] = (
        "아래 by_day/atr_tercile 은 사후탐색이다 — 판정 근거로 쓰지 말 것(313차 ④). "
        "가설로 채택하려면 사전등록 후 신규 표본으로 재판정한다."
    )
    out["by_day"] = {d: round(v, 4) for d, v in sorted(by_day.items())}
    atrs = sorted(s["atr"] for s in resolved)
    t1, t2 = atrs[len(atrs) // 3], atrs[2 * len(atrs) // 3]
    terc = {}
    for lo, hi, lab in ((None, t1, "low"), (t1, t2, "mid"), (t2, None, "high")):
        v = [s for s in resolved
             if (lo is None or s["atr"] >= lo) and (hi is None or s["atr"] < hi)]
        if not v:
            continue
        terc[lab] = {
            "atr_range": [round(lo, 3) if lo is not None else None,
                          round(hi, 3) if hi is not None else None],
            "n": len(v), "days": len({s["day"] for s in v}),
            "hyp_pt": round(sum(s["hyp"] for s in v), 4),
            "stop": sum(1 for s in v if s["outcome"] == "STOP"),
        }
    out["atr_tercile"] = terc
    out["direction_mix"] = {
        "LONG": sum(1 for s in resolved if s["direction"] > 0),
        "SHORT": sum(1 for s in resolved if s["direction"] < 0),
    }
    out["recommendation"] = (
        "09:20~09:29 특별분기 제거((D)안) **상정 가능** — ⚠ 상정 자격일 뿐 집행은 "
        "주간회의 결정. 제거 시 같은 분기의 `size×0.5`는 분리 존치 권고."
        if out["verdict"] == "BLOCK_UNJUSTIFIED" else
        "현행 유지. 미충족 관문: %s"
        % ", ".join(k for k, v in gates.items() if not v)
    )
    return out, resolved


def render(out):
    L = []
    A = L.append
    A("=" * 72)
    A("[55] 09:20~09:29 '앙상블 A등급만 허용' 게이트 — 소급 판정  %s" % out["badge"])
    A("=" * 72)
    A("  판정      : %s" % out["verdict"])
    if out.get("reason"):
        A("  사유      : %s" % out["reason"])
    A("  표본      : 차단 %s건 → 재구성 %s건 / %s거래일 (%s ~ %s)"
      % (out.get("n_blocked_raw"), out.get("n_resolved"), out.get("n_days"),
         out.get("day_first"), out.get("day_last")))
    if out.get("n_resolved"):
        A("  누적 hyp  : %+.4f pt   (왕복비용 %.4f pt)"
          % (out["total_hyp_pnl_pts"], out["cost_pt"]))
        A("  승률      : %.1f%%   (기준선 %s)"
          % (100 * out["win_rate"],
             ("%.1f%%" % (100 * out["baseline_win_rate"]))
             if out["baseline_win_rate"] is not None else "n/a"))
        A("  일자      : +%d / -%d  · 부호검정 p=%.4f"
          % (out["day_pos"], out["day_neg"], out["day_sign_p"]))
        A("  drop-worst: %s 제거 → %+.4f pt (부호유지 %s)"
          % (out["drop_worst_days"], out["drop_worst_total_pt"],
             out["drop_worst_sign_kept"]))
        A("  전후반    : %s (일관 %s)"
          % (out["half_split_pt"], out["half_sign_consistent"]))
        A("  청산분포  : %s" % out["outcome_mix"])
        A("  호라이즌  : %s" % out["horizon_mix"])
        A("  σ 층화    : %s" % json.dumps(out["sigma_split"], ensure_ascii=False))
    if out.get("gates"):
        A("  " + "-" * 68)
        for k, v in out["gates"].items():
            A("  %s %s" % ("PASS" if v else "FAIL", k))
    if out.get("recommendation"):
        A("  " + "-" * 68)
        A("  권고      : %s" % out["recommendation"])
    if out.get("by_day"):
        A("  " + "-" * 68)
        A("  🔴 아래는 **사후탐색** — 판정 근거로 쓰지 말 것(313차 ④)")
        A("  일자별   :")
        for d, v in out["by_day"].items():
            A("     %s  %+9.3f pt%s" % (d, v, "  ← 최대기여" if d in out.get("drop_worst_days", []) else ""))
        A("  ATR 3분위: (사전등록 아님 — 다음 안건의 가설 후보)")
        for lab in ("low", "mid", "high"):
            t = (out.get("atr_tercile") or {}).get(lab)
            if t:
                A("     %-4s ATR[%s,%s)  n=%2d %2d일  hyp=%+8.3f  STOP=%d/%d"
                  % (lab, t["atr_range"][0], t["atr_range"][1], t["n"], t["days"],
                     t["hyp_pt"], t["stop"], t["n"]))
        A("  방향분포 : %s" % out.get("direction_mix"))
    A("=" * 72)
    A("  ⚠ hyp는 1계약·TP1상한·미실현 시뮬이다 — 실현손익이 아니고 원(₩) 채널과")
    A("    직접 비교하지 말 것. 체크리스트·Tox·Hurst·JointGate는 이 분기 뒤라 미평가")
    A("    (미측정이지 통과가 아니다).")
    A("  ⚠ 판정은 상정 자격일 뿐 집행이 아니다 — 정책 변경은 주간회의 소관(§9).")
    A("=" * 72)
    return "\n".join(L)


# ──────────────────────────────────────────────────────────────────────────
# 캠페인 리포트 연결부 — `_safe_channel()` 규약 (compute/summarize)
# ──────────────────────────────────────────────────────────────────────────
def compute(start_date=None):
    """`generate_validation_campaign_report.py:_safe_channel()` 규약.

    ⚠ `start_date` 인자는 규약상 받지만 **쓰지 않는다.** 이 채널의 시작일은
      사전등록된 `data_start`(차단 마커가 기록되기 시작한 날)이며, 캠페인 시작일로
      바꾸면 마커가 없던 구간이 분모에 섞인다(계측 4원칙 ② — 미측정 ≠ 0).
    """
    out, _ = evaluate()
    return out


def summarize(res):
    """요약표 1행용. verdict + 핵심 수치."""
    if not res:
        return {"verdict": "INSUFFICIENT", "reason": "[55] 결과 없음"}
    n = res.get("n_resolved") or 0
    if not n:
        return res
    res = dict(res)
    res["headline"] = (
        "차단 %d건/%d일 · 누적 hyp %+.2fpt(비용 %.3f) · 승률 %.1f%%(기준선 %s) · "
        "일자 +%d/-%d p=%.3f"
        % (n, res.get("n_days", 0), res.get("total_hyp_pnl_pts", 0.0),
           res.get("cost_pt") or 0.0, 100 * (res.get("win_rate") or 0.0),
           ("%.1f%%" % (100 * res["baseline_win_rate"]))
           if res.get("baseline_win_rate") is not None else "n/a",
           res.get("day_pos", 0), res.get("day_neg", 0),
           res.get("day_sign_p", 1.0))
    )
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    out, _ = evaluate()
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(render(out))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
