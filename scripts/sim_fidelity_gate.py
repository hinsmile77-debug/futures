# scripts/sim_fidelity_gate.py
"""[MW0602 435차, 캠페인 47] 시뮬레이터 재현충실도 게이트 — 읽기 전용 메타 채널.

무엇을 묻는가
--------------
기하 A/B 채널들([3-B]/[23-B]/[25]/[25-B]/[46])은 전부 **같은 재생기 가정**을 공유한다:

    ① 1분봉 고저가만 본다 (봉내 도달순서 불명 → 스톱 우선의 보수 관례)
    ② TP2에 닿으면 거기서 종료한다
    ③ TP3·4단계 트레일링·신호소멸청산을 모델링하지 않는다

이 가정들이 실제를 얼마나 왜곡하는지는 **한 번도 측정된 적이 없었다.** 각 채널은
`current` 변형을 기준선으로 삼아 `delta_vs_current`로 판정하는데, 그 기준선 자체가
실제 실현손익과 어긋나면 **delta의 부호까지 뒤집힐 수 있다.**

이 채널은 그 기준선을 실측과 대조한다. 어긋나면 하위 채널의 verdict를
`SUSPENDED`로 덮어 **리포트가 FAIL을 찍지 않게** 한다.

왜 삭제가 아니라 정지인가
--------------------------
- 소스 데이터(`trades`·`synthetic_partial_exits`·`raw_candles`)는 전부 **main.py가
  기록**한다. 채널을 지워도 데이터는 계속 쌓이고 나중에 소급 재실행이 된다.
- 그러나 사전등록 이력(§9)은 캠페인의 핵심 자산이고, **결과를 본 뒤 채널을 지우면
  "불리한 결과를 묻었다"로 읽힌다.** 정지는 그 둘을 모두 지킨다.
- 재현이 회복되면 게이트가 자동으로 PASS로 바뀌어 **하위 채널이 스스로 깨어난다** —
  사람이 "재검토하기로 했는데 안 함" 상태로 방치할 여지가 없다(CB②·CB③-P4·
  FP-CRITICAL이 전부 그 패턴이었다, CLAUDE.md 절대원칙 §2).

무엇을 측정하나
----------------
[23-B] `tp1_geometry_shadow`의 `current` 변형을 **정본 재생기**로 삼는다. 이유:
  - 그 채널만 `rows_ts`(entry_ts 평행 리스트)를 내보내 **포지션 단위 조인**이 된다.
  - 모집단이 "전 진입"이라 가장 넓고, 위 ①②③ 가정을 전부 포함한다.
  - 다른 채널은 같은 세 가정을 공유하므로, 정본이 재현에 실패하면 그들도 실패한다.

지표 2종 (사전등록, config/settings.py VALIDATION_CAMPAIGN["sim_fidelity_gate"]):
  repro_bias_R  = median( (sim_pt − actual_pt) / R )   R = 그 진입의 하드스톱 거리
  sign_match    = sign(Σ sim) == sign(Σ actual)

  ⚠ **중앙값을 쓴다** — 372차 원칙. 평균은 고변동일 소수 건에 끌려간다.
  ⚠ **R로 정규화한다** — pt 그대로 더하면 ATR이 큰 날이 지표를 지배한다.

판정
-----
  PASS      : |repro_bias_R| <= repro_bias_R_max  AND  sign_match
              → 하위 채널 verdict 그대로 출력
  SUSPEND   : 그 외
              → 하위 채널 verdict를 SUSPENDED로 대체 (데이터·사전등록은 보존)
  INSUFFICIENT : 표본 미달 (min_samples / min_days) — 313차 원칙

⚠ 사전등록 정직성 고지
-----------------------
이 채널의 첫 관측치는 **신설 전에 이미 측정됐다**(432차 후속2: 시뮬 −18.42pt vs
실제 +19.05pt, 109포지션/15일 → 부호 불일치). 따라서 최초 SUSPEND 판정은
**사전등록된 검증이 아니라 이미 본 결과의 코드화**다. [25]의 `breakeven` 변형과
같은 취급으로 읽을 것. 이 채널의 사전등록 가치는 **앞으로의 회복 판정**
(TP3·트레일링 편입 후 PASS로 돌아오는가)에 있다.

한계
-----
- 정본으로 [23-B]를 쓰므로, [23-B]의 모집단(SYSTEM_AUTO 진입, atr 확보분)에
  없는 채널 고유 표본은 직접 검증되지 않는다. 공유 가정 ①②③을 통한 **간접
  추론**이다 — 그 사실을 리포트가 함께 찍는다.
- 실제 실현손익 자체도 완전무결하지 않다(432차 후속2: 봉중 하드스톱 경로의
  유리 체결 계측 오염). 그쪽은 [48] `bar_stop_path_watch`가 따로 본다.

실행:
    py310_64\python.exe scripts/sim_fidelity_gate.py [--since 2026-07-05]
"""
from __future__ import annotations

import argparse
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

from config.settings import TRADES_DB, VALIDATION_CAMPAIGN  # noqa: E402
from config.constants import MINI_FUTURES_PT_VALUE  # noqa: E402

_CR = VALIDATION_CAMPAIGN.get("sim_fidelity_gate", {})


def _actual_by_entry(since: str) -> dict:
    """entry_ts → 실제 실현손익(pt). **포지션 단위로 병합한다.**

    ⚠ 417차 교훈: `trades` 한 행은 **청산 레그**다(TP1 부분청산/잔량이 별도 행).
    레그 단위로 세면 이익 포지션이 여러 행으로 쪼개져 지표가 왜곡된다.
    [23-B]의 `_load_trades()`와 동일한 GROUP BY 규약을 쓴다.
    """
    src = _CR.get("entry_source", "SYSTEM_AUTO")
    with sqlite3.connect(TRADES_DB) as c:
        rows = c.execute(
            "SELECT entry_ts, SUM(pnl_pts) FROM trades "
            "WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND entry_source = ? "
            "GROUP BY entry_ts", (since, src)).fetchall()
    return {r[0]: float(r[1] or 0.0) for r in rows}


def _actual_krw_by_entry(since: str) -> dict:
    """[MW0601 440차 신설] entry_ts → 실제 실현손익(pt, **계약가중**).

    ⚠ 위 `_actual_by_entry()`의 `SUM(pnl_pts)`는 **레그별 계약당 pt의 단순합**이라
    계약가중이 아니다. 예: 3계약 포지션이 (1계약 +0.69) + (2계약 +1.35)로 나가면
    SUM(pnl_pts)=2.04 지만 실제 실현은 0.69×1 + 1.35×2 = **3.39pt·계약**이다.

    이 함수는 진단 표기용으로만 쓴다 — **판정식 입력은 바꾸지 않았다.** 사전등록된
    합격선의 입력을 사후에 교체하면 그 자체로 §9 위반이라, 단위 불일치는 리포트가
    양쪽 수치를 나란히 찍어 **주간회의가 결정**하게 한다(440차 판단).
    """
    src = _CR.get("entry_source", "SYSTEM_AUTO")
    with sqlite3.connect(TRADES_DB) as c:
        rows = c.execute(
            "SELECT entry_ts, SUM(COALESCE(net_pnl_krw, pnl_krw)) FROM trades "
            "WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND entry_source = ? "
            "GROUP BY entry_ts", (since, src)).fetchall()
    return {r[0]: float(r[1] or 0.0) / float(MINI_FUTURES_PT_VALUE) for r in rows}


def compute(since: str = "2026-07-05", engine: str = None) -> dict:
    """정본 재생기([23-B] current)와 실제 실현손익을 포지션 단위로 대조.

    engine: None이면 사전등록된 현행 엔진(settings sim_fidelity_gate["engine"]).
            "v1"/"v2"를 명시하면 그 엔진으로 계산한다 — 리포트가 개선폭을 감사할 수
            있도록 양쪽을 각각 부른다(440차).
    """
    try:
        from scripts.tp1_geometry_shadow import (
            compute as _geo_compute, _load_atr_map, _geometry,
        )
    except Exception as e:  # 정본 채널이 죽으면 게이트는 판정하지 않는다(막지도 않는다)
        return {"error": "%s: %s" % (type(e).__name__, e), "pairs": []}

    out = _geo_compute(since, engine=engine)
    rows = (out.get("rows") or {}).get("current") or []
    ts_list = (out.get("rows_ts") or {}).get("current") or []
    qty_list = (out.get("rows_qty") or {}).get("current") or []
    if len(rows) != len(ts_list):
        return {"error": "rows/rows_ts 길이 불일치 (%d/%d)" % (len(rows), len(ts_list)),
                "pairs": []}
    if len(qty_list) != len(rows):
        qty_list = [1] * len(rows)

    actual = _actual_by_entry(since)
    actual_krw = _actual_krw_by_entry(since)
    atr_map = _load_atr_map(since)

    # 진입별 hurst/horizon — R(하드스톱 거리) 산출에 필요하다.
    src = _CR.get("entry_source", "SYSTEM_AUTO")
    with sqlite3.connect(TRADES_DB) as c:
        meta = {r[0]: (r[1], r[2]) for r in c.execute(
            "SELECT entry_ts, entry_horizon, hurst_bucket FROM trades "
            "WHERE entry_ts >= ? AND entry_source = ? GROUP BY entry_ts",
            (since, src)).fetchall()}

    pairs, days = [], set()
    for (outcome, sim_pt), ets, q in zip(rows, ts_list, qty_list):
        act = actual.get(ets)
        if act is None:
            continue
        atr = atr_map.get(ets[:17] + "00") or atr_map.get(ets)
        if not atr:
            continue
        hz, hb = meta.get(ets, (None, None))
        R = _geometry(hz, hb, float(atr), None, None)[0]   # 현행 기하의 스톱 거리
        if not R or R <= 0:
            continue
        q = int(q or 1) or 1
        pairs.append({"ts": ets, "sim": float(sim_pt), "actual": act,
                      "R": float(R), "bias_R": (float(sim_pt) - act) / float(R),
                      # 440차 진단 전용 — 판정식은 위 두 필드만 쓴다.
                      "qty": q,
                      "sim_w": float(sim_pt) * q,
                      "actual_w": actual_krw.get(ets, 0.0)})
        days.add(ets[:10])

    return {"since": since, "pairs": pairs, "n_days": len(days),
            "engine": out.get("engine"),
            "n_geo_trades": out.get("n_trades"), "error": None}


def summarize(out: dict) -> dict:
    if out.get("error"):
        return {"verdict": "INSUFFICIENT", "reason": "정본 채널 실행 실패 — %s" % out["error"],
                "gate": "OPEN", "error": out["error"]}
    pairs = out.get("pairs") or []
    min_n = int(_CR.get("min_samples", 40))
    min_d = int(_CR.get("min_days", 8))
    n, nd = len(pairs), int(out.get("n_days") or 0)

    if n < min_n or nd < min_d:
        # 표본 미달이면 **게이트를 열어 둔다** — 근거 없이 하위 채널을 막지 않는다(313차).
        return {"verdict": "INSUFFICIENT", "gate": "OPEN",
                "reason": "표본 부족 (n=%d<%d 또는 거래일=%d<%d) — 게이트 미적용"
                          % (n, min_n, nd, min_d),
                "n": n, "n_days": nd}

    bias = statistics.median(p["bias_R"] for p in pairs)      # 372차: 중앙값
    bias_mean = statistics.mean(p["bias_R"] for p in pairs)
    sim_tot = sum(p["sim"] for p in pairs)
    act_tot = sum(p["actual"] for p in pairs)
    sign_ok = (sim_tot >= 0) == (act_tot >= 0)
    lim = float(_CR.get("repro_bias_R_max", 0.10))
    need_sign = bool(_CR.get("require_sign_match", True))

    ok = (abs(bias) <= lim) and (sign_ok or not need_sign)
    verdict = "PASS" if ok else "SUSPEND"
    if ok:
        reason = ("재현 양호 — bias(중앙) %+.3fR ≤ %.2fR, 부호 일치 "
                  "(시뮬 %+.2f / 실제 %+.2f pt, n=%d/%d일)"
                  % (bias, lim, sim_tot, act_tot, n, nd))
    else:
        why = []
        if abs(bias) > lim:
            why.append("bias(중앙) %+.3fR > %.2fR" % (bias, lim))
        if need_sign and not sign_ok:
            why.append("총합 부호 불일치 (시뮬 %+.2f vs 실제 %+.2f pt)" % (sim_tot, act_tot))
        reason = ("재현 실패 — %s (n=%d/%d일) → 하위 채널 판정 정지"
                  % (" · ".join(why), n, nd))

    # ── [MW0601 440차] 진단 지표 — **판정에 관여하지 않는다** ────────────────────
    # (a) MAE: 모델이 개별 포지션을 얼마나 맞히는가. 총합은 오차가 상쇄되면
    #     좋아 보일 수 있어(v1이 정확히 그랬다) 모델 품질의 지표로 부적합하다.
    # (b) 계약가중 총합: `_actual_by_entry()`가 레그 pt 단순합이라 계약가중이
    #     아니다(그 함수 주석 참조). 단위를 맞춘 값을 나란히 찍는다.
    # (c) 부호판정 안정성: Σactual이 분산 대비 0에 가까우면 sign_match는
    #     아주 작은 편향으로도 뒤집힌다. "부호 불일치"가 재현 실패를 뜻하는지
    #     아니면 기준의 불안정을 뜻하는지 구분할 근거를 남긴다.
    mae = statistics.mean(abs(p["bias_R"]) for p in pairs)
    sim_w = sum(p.get("sim_w", p["sim"]) for p in pairs)
    act_w = sum(p.get("actual_w", p["actual"]) for p in pairs)
    try:
        disp = statistics.pstdev([p["actual"] for p in pairs]) * (n ** 0.5)
    except statistics.StatisticsError:
        disp = 0.0
    sign_margin = (abs(act_tot) / disp) if disp else None

    return {"verdict": verdict, "gate": ("OPEN" if ok else "SUSPEND"),
            "reason": reason, "n": n, "n_days": nd,
            "engine": out.get("engine"),
            "repro_bias_R": round(bias, 4), "repro_bias_R_mean": round(bias_mean, 4),
            "sim_total_pt": round(sim_tot, 4), "actual_total_pt": round(act_tot, 4),
            "sign_match": sign_ok, "targets": list(_CR.get("targets", [])),
            # 진단 전용 (440차)
            "mae_R": round(mae, 4),
            "sim_total_pt_wq": round(sim_w, 4), "actual_total_pt_wq": round(act_w, 4),
            "sign_margin_sd": (round(sign_margin, 3) if sign_margin is not None else None)}


def compare_engines(since: str) -> dict:
    """[MW0601 440차] v1/v2 재현 지표를 나란히 계산 — 리포트 감사용.

    "재생기를 고쳤다"는 주장은 개선폭이 보여야 검증된다. 판정은 사전등록된
    현행 엔진(settings `engine`) 결과만 쓴다 — 이 함수는 표기용이다.
    """
    outs = {}
    for eng in ("v1", "v2"):
        try:
            s = summarize(compute(since, engine=eng))
        except Exception as e:                      # 한쪽이 죽어도 나머지는 찍는다
            s = {"verdict": "ERROR", "reason": "%s: %s" % (type(e).__name__, e)}
        outs[eng] = s
    return outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None)
    args = ap.parse_args()
    since = args.since or VALIDATION_CAMPAIGN.get("start_date", "2026-07-05")
    s = summarize(compute(since))

    print("=" * 88)
    print("[47] 시뮬레이터 재현충실도 게이트   기간 %s~" % since)
    print("사전등록: config/settings.py VALIDATION_CAMPAIGN['sim_fidelity_gate']")
    print("=" * 88)
    if s.get("error"):
        print("정본 채널 실행 실패: %s" % s["error"])
        return
    print("표본: %s포지션 / %s거래일" % (s.get("n"), s.get("n_days")))
    if "repro_bias_R" in s:
        print("재현 편향(중앙) %+.3fR   (평균 %+.3fR)"
              % (s["repro_bias_R"], s["repro_bias_R_mean"]))
        print("총합           시뮬 %+.2f pt  vs  실제 %+.2f pt   부호일치=%s"
              % (s["sim_total_pt"], s["actual_total_pt"], s["sign_match"]))
    print()
    print("판정: %s  (게이트 %s)" % (s["verdict"], s["gate"]))
    print("사유: %s" % s["reason"])
    if s["gate"] == "SUSPEND":
        print()
        print("→ 다음 채널의 verdict가 SUSPENDED로 대체된다(데이터·사전등록은 보존):")
        for t in s.get("targets", []):
            print("   · %s" % t)
        print("→ 해제 조건: 재생기에 TP3·4단계 트레일링을 편입해 재현이 회복되면 자동 PASS.")
    print()
    print("⚠ 사전등록 정직성: 최초 SUSPEND는 432차 후속2에서 **이미 본 결과**의 코드화다.")
    print("  이 채널의 사전등록 가치는 앞으로의 회복 판정에 있다.")


if __name__ == "__main__":
    main()
