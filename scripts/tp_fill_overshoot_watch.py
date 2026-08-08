# scripts/tp_fill_overshoot_watch.py
"""[MW0601 441차, 캠페인 47-B] TP 체결 오버슈트 감시 — 읽기 전용·관찰 전용.

무엇을 묻는가
--------------
"재생기가 TP 체결가를 **목표가**로 적는 것이 맞는가?"

441차가 [47] 게이트를 파고들다 발견한 것: `tp_trigger="close"` 세대(~2026-08-02)는
TP 판정이 **분봉 종가**였는데 재생기는 체결을 **목표가**로 계상하고 있었다. 트리거
조건 자체가 "종가가 목표가를 넘었다"이므로 넘어선 만큼(이익 방향 오버슈트)이 통째로
사라졌고, 그 하나가 [47] 재현 격차의 **-21.56pt**였다(TP2 완주 22건이 목표거리를
**전건 초과**, 합 +18.19pt).

그 결함은 고쳤다(`exit_replay.py`). 이 채널은 **같은 종류의 결함이 다시 생기는지**를
상시 감시한다 — 체결 모델은 코드 세대가 바뀔 때마다 조용히 어긋날 수 있고,
441차 이전에는 그것을 볼 계기가 게이트 SUSPEND 딥다이브밖에 없었다.

무엇을 재나
------------
실제 TP 청산 레그마다:

    오버슈트(pt) = (실제 체결거리) − (재생기 목표거리)
      실제 체결거리 = 이익방향 부호 × (체결가 − 진입가)
      재생기 목표거리 = exit_replay.geometry()의 해당 단계 거리

`envelope` 세대(틱 TP)에서는 틱이 목표가를 스치는 즉시 나가므로 오버슈트가 **0 근처**
여야 정상이다. `close` 세대에서는 종가까지 간 만큼 **양수**가 정상이다 — 그래서
세대별로 갈라서 본다. 세대 경계는 이미 사전등록된 `replay_regime`을 그대로 쓴다.

⚠ **판정하지 않는다 (OBSERVE 전용).**
-------------------------------------
합격선을 두지 않는 이유는 두 가지다.
  - 정상 오버슈트의 크기는 세대·틱경로 구현에 따라 달라지는 값이고, 지금 그 기준을
    만들면 **관측을 본 뒤 기준을 세우는 것**(313차 위반)이 된다.
  - post 세대 표본이 아직 얇다(441차 시점 4건). 여기서 임계를 정하면 소수 이상치로
    정당화하는 꼴이 된다 — 372차가 PSI 임계에서 정확히 그 함정을 피했다.
표본이 쌓여 정상 분포가 드러나면 **그때 §9 주간회의에서 사전등록**할 것.

⚠ [47] 게이트의 `targets`에 넣지 않는다 — 이 채널은 게이트가 쓰는 재생기 자체를
   감시하므로, 게이트가 이것을 정지시키면 순환이 된다.

무엇을 결론으로 삼을 수 있나 / 없나
-----------------------------------
- 이 채널은 **재생기 체결 모델의 타당성**만 본다. 손익이 아니다 — 오버슈트는
  이미 실현된 실제 손익의 일부이지 "더 벌 수 있었다"가 아니다.
- [17] `exit_fill_slippage`(스톱 쪽 체결)와 대칭을 이룬다. 그쪽이 스톱 경로를,
  이쪽이 TP 경로를 본다.

실행:
    py310_64\python.exe scripts/tp_fill_overshoot_watch.py [--since 2026-07-05]
"""
from __future__ import annotations

import argparse
import os
import re
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

from config.settings import TRADES_DB, VALIDATION_CAMPAIGN  # noqa: E402

_CR = VALIDATION_CAMPAIGN.get("tp_fill_overshoot_watch", {})
_TP_RE = re.compile(r"TP\s*([123])")


def _stage_of(reason):
    """청산 사유 → TP 단계(1/2/3). TP가 아니면 None."""
    m = _TP_RE.search(str(reason or ""))
    return int(m.group(1)) if m else None


def compute(since: str = "2026-07-05") -> dict:
    """실제 TP 레그의 체결 오버슈트를 세대·단계별로 집계한다."""
    from scripts.tp1_geometry_shadow import _load_atr_map
    from scripts.exit_replay import geometry, regime_for

    src = _CR.get("entry_source", "SYSTEM_AUTO")
    out = {"since": since, "rows": [], "n_skipped_atr": 0, "error": None}
    try:
        atr_map = _load_atr_map(since)
        with sqlite3.connect(TRADES_DB) as c:
            c.row_factory = sqlite3.Row
            legs = [dict(r) for r in c.execute(
                "SELECT entry_ts, exit_ts, direction, entry_price, exit_price, "
                "       quantity, exit_reason, entry_horizon, hurst_bucket "
                "FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL "
                "  AND entry_source = ? ORDER BY entry_ts, exit_ts",
                (since, src)).fetchall()]
    except Exception as e:
        out["error"] = "%s: %s" % (type(e).__name__, e)
        return out

    for lg in legs:
        stage = _stage_of(lg["exit_reason"])
        if stage is None:
            continue
        ets = lg["entry_ts"]
        atr = atr_map.get(ets[:17] + "00") or atr_map.get(ets)
        if not atr:
            out["n_skipped_atr"] += 1
            continue
        dists = geometry(lg["entry_horizon"], lg["hurst_bucket"], float(atr))
        target = dists[stage]          # (stop, tp1, tp2, tp3) — stage 그대로가 인덱스
        if not target or target <= 0:
            continue
        sgn = 1.0 if str(lg["direction"]).upper() == "LONG" else -1.0
        actual = sgn * (float(lg["exit_price"]) - float(lg["entry_price"]))
        out["rows"].append({
            "ts": ets, "day": ets[:10], "stage": stage,
            "era": regime_for(ets).get("tp_trigger", "?"),
            "target_pt": round(target, 4),
            "actual_pt": round(actual, 4),
            "overshoot_pt": round(actual - target, 4),
            # ATR로 정규화 — 변동성 큰 날이 지표를 지배하지 않게 한다([47]의 R 정규화와 같은 취지)
            "overshoot_atr": round((actual - target) / float(atr), 4),
            "qty": int(lg["quantity"] or 1),
        })
    return out


def _agg(rows):
    if not rows:
        return None
    ov = [r["overshoot_pt"] for r in rows]
    oa = [r["overshoot_atr"] for r in rows]
    return {
        "n": len(rows),
        "n_days": len({r["day"] for r in rows}),
        "median_pt": round(statistics.median(ov), 4),
        "mean_pt": round(statistics.mean(ov), 4),
        "total_pt": round(sum(ov), 4),
        "median_atr": round(statistics.median(oa), 4),
        "max_pt": round(max(ov), 4),
        "min_pt": round(min(ov), 4),
        "pos_share": round(sum(1 for v in ov if v > 0) / float(len(ov)), 4),
    }


def summarize(out: dict) -> dict:
    """OBSERVE 전용 — 합격선이 없으므로 verdict는 판정이 아니라 표본 상태 표시다."""
    if out.get("error"):
        return {"verdict": "INSUFFICIENT", "reason": "실행 실패 — %s" % out["error"],
                "error": out["error"]}
    rows = out.get("rows") or []
    min_n = int(_CR.get("min_samples", 20))

    by_era, by_stage = {}, {}
    for r in rows:
        by_era.setdefault(r["era"], []).append(r)
        by_stage.setdefault(r["stage"], []).append(r)

    res = {
        "overall": _agg(rows),
        "by_era": {k: _agg(v) for k, v in sorted(by_era.items())},
        "by_stage": {("TP%d" % k): _agg(v) for k, v in sorted(by_stage.items())},
        "n": len(rows),
        "n_days": len({r["day"] for r in rows}),
        "n_skipped_atr": out.get("n_skipped_atr", 0),
        "min_samples": min_n,
    }
    if len(rows) < min_n:
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = ("TP 레그 표본 부족 (%d < %d) — 관찰만 계속한다"
                         % (len(rows), min_n))
    else:
        res["verdict"] = "OBSERVE"
        _env = res["by_era"].get("envelope")
        _cls = res["by_era"].get("close")
        bits = []
        if _cls:
            bits.append("close세대 중앙 %+.3fpt (n=%d)" % (_cls["median_pt"], _cls["n"]))
        if _env:
            bits.append("envelope세대 중앙 %+.3fpt (n=%d)" % (_env["median_pt"], _env["n"]))
        res["reason"] = " · ".join(bits) if bits else "세대 구분 없음"
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None)
    args = ap.parse_args()
    since = args.since or VALIDATION_CAMPAIGN.get("start_date", "2026-07-05")
    s = summarize(compute(since))

    print("=" * 88)
    print("[47-B] TP 체결 오버슈트 감시   기간 %s~" % since)
    print("사전등록: config/settings.py VALIDATION_CAMPAIGN['tp_fill_overshoot_watch']")
    print("=" * 88)
    if s.get("error"):
        print("실행 실패: %s" % s["error"])
        return
    print("TP 레그 %d건 / %d거래일  (ATR 결측 제외 %d건)"
          % (s["n"], s["n_days"], s["n_skipped_atr"]))
    print()
    print("%-14s %5s %5s %10s %10s %10s %9s"
          % ("구분", "n", "일수", "중앙(pt)", "평균(pt)", "중앙(ATR)", "양수비율"))
    for label, a in ([("전체", s["overall"])]
                     + [("세대 " + k, v) for k, v in s["by_era"].items()]
                     + [(k, v) for k, v in s["by_stage"].items()]):
        if not a:
            continue
        print("%-14s %5d %5d %+10.3f %+10.3f %+10.3f %8.0f%%"
              % (label, a["n"], a["n_days"], a["median_pt"], a["mean_pt"],
                 a["median_atr"], 100 * a["pos_share"]))
    print()
    print("판정: %s — %s" % (s["verdict"], s.get("reason", "")))
    print()
    print("⚠ 이 채널은 **판정하지 않는다**(OBSERVE). 정상 오버슈트 크기의 기준을 지금")
    print("  만들면 관측을 본 뒤 기준을 세우는 것이 된다(313차). 표본이 쌓여 분포가")
    print("  드러나면 §9 주간회의에서 사전등록할 것.")
    print("⚠ 오버슈트는 **이미 실현된 실제 손익의 일부**다 — '더 벌 수 있었다'가 아니다.")


if __name__ == "__main__":
    main()
