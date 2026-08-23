# -*- coding: utf-8 -*-
"""[MW0602 489차 / 0823 주간회의 D2] CB② 복원 반사실 — 상시 계측.

캠페인 채널 **[56]**. 사전등록 기준은
`config/settings.py:VALIDATION_CAMPAIGN["cb2_restore_shadow"]`.

이 스크립트가 존재하는 이유
---------------------------
절대원칙 §2의 CB②(`CB_CONSEC_STOP_LIMIT`)는 2026-07-05부터 `9999`(사실상 비활성)이고,
복원 재검토 기한이 2026-08-29였다. **그 기한은 2026-08-01에 이미 한 번 4주 연기된
것이다.** 날짜를 또 미루면 CB③-P4·FP-CRITICAL이 걸어간 길("재검토하기로 했는데 안 함")과
같아진다 — 절대원칙 §2가 스스로 경고하는 그 경로다.

0823 주간회의 결정(D2)은 **기한을 날짜가 아니라 사건에 묶는 것**이다:

    ① `CB_CONSEC_STOP_LIMIT = 9999` 유지
    ② 복원 시점 = 실전 전환 기준 ⑧(실전 자본 재설정) 해제와 **동일 커밋**
    ③ 그 사이 이 채널이 매주 반사실을 자동 재계산한다

②가 핵심이다. ⑧이 열리는 순간이 노출이 커지는 순간이고 CB②가 실제로 필요해지는
순간이므로, "재검토 날짜"가 아니라 **선행조건**이 되어 잊힐 수 없다. 그리고 ③이
그때 쓸 판정 근거를 매주 쌓는다 — 292·303·371차가 반복 확인한 *"계측 먼저,
그다음 배선"* 이다.

무엇을 재는가
-------------
    "CB②가 살아 있었다면 그날 몇 시에 멈췄고, 그 뒤 진입분의 손익은 얼마였나."

제거된 손익이 **음수**면 CB②는 손실을 막았을 것이고(복원이 유리),
**양수**면 수익을 막았을 것이다(복원이 불리).

🔴 집계 단위는 포지션이다 — 레그가 아니다 (470차 C1)
-----------------------------------------------------
라이브 규칙은 최종 청산 1회당 승/패를 판정한다:

    main.py:_post_exit          pnl_pts > 0 → record_win() / else record_stop_loss()
    circuit_breaker.record_stop_loss(is_partial_leg=True) → 카운터 **미증가**
    circuit_breaker.record_win(is_partial_leg=True)       → 리셋 **안 함**

⚠ **로그 문자열 `[CB] 연속 손절 N회` 로 과거를 세면 안 된다.** 2026-08-14 이전
  기록은 **레그 단위 시절**의 값이라 과대계상된다. 실측 대조(2026-08-14):
  라이브 로그 max=3 vs 포지션 재구성 max=2 — 470차 C1이 문서화한 바로 그 괴리다.
  그래서 이 채널은 로그가 아니라 `trades.db` 에서 **현행 규칙으로 재구성**한다.
  재구성 검증(470차 이후 날짜): 08-18 max=3 · 08-19 max=2 · 08-20 max=2 —
  라이브 로그와 **전부 일치**한다.

방법론 (313차 5원칙)
--------------------
① **일자단위 1차 판정** — 정지는 하루에 최대 1회이므로 일자가 자연스러운 관측 단위다.
② **이상치 분해** — 최악 1일 제거 후에도 부호가 유지되는지 본다.
③ **사전등록** — 합격선은 settings에 먼저 박혔다. 이 스크립트는 읽기만 한다.
④ **판정 창 분리** — `start_date` 이후만 판정한다. 그 이전은 `posthoc_seed`로
   표시만 하고 **판정에 넣지 않는다**(가설을 만든 구간이다).
⑤ **후보 둘을 다 센다** — 절대원칙 §2의 복원 목표는 "2~3"이고, 2026-08-23
   사후탐색에서 **두 값이 서로 반대 방향**임이 드러났다. 한쪽만 세면 그 사실이 숨는다.

⚠ 이 반사실은 **진입 제거만** 모형화한다. 실제 HALT는 `_trigger_halt()`가
  emergency_exit까지 부르므로 **보유 포지션의 청산 시점도 바뀐다** — 그 2차 효과는
  재현하지 않는다. 따라서 이 수치는 **하한 추정**이고, 정확한 손익 예측이 아니라
  **방향(부호) 판정용**이다.
⚠ 단위는 **원(₩)** 이다. `[1계약·TP1상한·미실현 시뮬]` 배지가 붙은 pt 채널과
  직접 더하거나 비교하지 말 것.

실행:
    python scripts/cb2_restore_shadow.py
    python scripts/cb2_restore_shadow.py --json
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
    TRADES_DB,
    CB_CONSEC_STOP_LIMIT,
)

CFG = VALIDATION_CAMPAIGN["cb2_restore_shadow"]


def _conn(path):
    c = sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def _sign_test_p(pos: int, neg: int) -> float:
    """양측 이항 부호검정 — `[55]`·리포터 `_sign_test_p()` 와 **같은 정의**.

    ⚠ `math.comb`을 쓰지 않는다 — **Python 3.8+ 전용**인데 이 시스템의 런타임은
      py37_32다. 표본이 min_samples에 닿기 전에는 이 함수가 호출되지 않으므로,
      `comb`을 쓰면 몇 달 뒤 표본이 찬 **바로 그날 처음 터진다**(지연 폭발).
    """
    n = pos + neg
    if n == 0:
        return 1.0
    k = min(pos, neg)
    total, c = 0.0, 1.0
    for i in range(0, k + 1):
        if i:
            c = c * (n - i + 1) / i
        total += c
    return min(1.0, 2.0 * total * (0.5 ** n))


def _krw(x) -> str:
    """원(₩) 표기. ⚠ `%`-포매팅에는 콤마 플래그가 없다 — `format()`을 쓴다."""
    try:
        return "{:+,.0f}원".format(float(x))
    except (TypeError, ValueError):
        return "—"


# ──────────────────────────────────────────────────────────────────────────
# 재구성
# ──────────────────────────────────────────────────────────────────────────
def _load_positions(since: str) -> list:
    """포지션 단위로 접는다 — 470차 C1 규칙.

    한 포지션(`entry_ts` 동일)의 레그를 청산 시각 순으로 정렬해
    **마지막 레그의 `pnl_pts`** 로 승/패를 판정한다(`_post_exit` 과 동일).
    손익은 포지션 전체 레그의 `net_pnl_krw` 합이다(417차 포지션 단위 집계).
    """
    src = str(CFG.get("entry_source", "SYSTEM_AUTO"))
    with _conn(TRADES_DB) as c:
        rows = c.execute(
            """SELECT entry_ts, exit_ts, pnl_pts, net_pnl_krw
                 FROM trades
                WHERE entry_source = ? AND date(entry_ts) >= ?
                ORDER BY exit_ts""", (src, since[:10])).fetchall()
    legs = defaultdict(list)
    for r in rows:
        legs[r["entry_ts"]].append(r)
    out = []
    for entry_ts, v in legs.items():
        v.sort(key=lambda r: r["exit_ts"] or "")
        out.append({
            "entry_ts": entry_ts,
            "exit_ts": v[-1]["exit_ts"],
            "final_pts": float(v[-1]["pnl_pts"] or 0.0),   # 승/패 판정 (라이브와 동일)
            "krw": sum(float(x["net_pnl_krw"] or 0.0) for x in v),
            "day": str(entry_ts)[:10],
            "n_legs": len(v),
        })
    return out


def _simulate(positions: list, limit: int) -> dict:
    """CB②=limit 였다면 각 거래일에 언제 멈췄고 무엇이 제거됐는가."""
    byday = defaultdict(list)
    for p in positions:
        byday[p["day"]].append(p)

    halts = []
    for d in sorted(byday):
        day = byday[d]
        # 카운터는 **청산** 순서로 오르고, 진입은 **진입** 시각으로 막힌다.
        cnt, halt_ts = 0, None
        for p in sorted(day, key=lambda x: x["exit_ts"] or ""):
            if p["final_pts"] > 0:
                cnt = 0
            else:
                cnt += 1
                if cnt >= limit:
                    halt_ts = p["exit_ts"]
                    break
        if not halt_ts:
            continue
        removed = [p for p in day if (p["entry_ts"] or "") > halt_ts]
        halts.append({
            "day": d,
            "halt_ts": halt_ts,
            "n_removed": len(removed),
            "krw_removed": round(sum(p["krw"] for p in removed), 1),
        })
    return {
        "limit": limit,
        "halt_days": halts,
        "n_halt_days": len(halts),
        "n_removed": sum(h["n_removed"] for h in halts),
        "krw_removed": round(sum(h["krw_removed"] for h in halts), 1),
    }


def compute(since: str = "2026-07-14") -> dict:
    positions = _load_positions(since)
    start = str(CFG.get("start_date") or "")
    judged = [p for p in positions if p["day"] >= start] if start else positions
    seed = [p for p in positions if p["day"] < start] if start else []

    live = int(CB_CONSEC_STOP_LIMIT)
    out = {
        "since": since,
        "start_date": start,
        "live_limit": live,
        "live_limit_active": live < 100,   # 9999 = 사실상 비활성
        "n_positions_all": len(positions),
        "n_positions_judged": len(judged),
        "n_days_judged": len(set(p["day"] for p in judged)),
        "n_positions_seed": len(seed),
        "n_days_seed": len(set(p["day"] for p in seed)),
        "judged": {}, "seed": {},
    }
    for lim in CFG.get("candidates", [2, 3]):
        out["judged"][str(lim)] = _simulate(judged, int(lim))
        if seed:
            out["seed"][str(lim)] = _simulate(seed, int(lim))
    return out


# ──────────────────────────────────────────────────────────────────────────
# 판정 — 사전등록 기준 그대로. 여기서 기준을 바꾸지 말 것(§9).
# ──────────────────────────────────────────────────────────────────────────
def _judge_one(sim: dict) -> dict:
    """후보 하나에 대한 판정. 관문은 전부 settings 사전등록값이다."""
    min_n = int(CFG.get("min_samples", 20))
    min_d = int(CFG.get("min_days", 6))
    alpha = float(CFG.get("alpha", 0.05))
    dropw = int(CFG.get("drop_worst_days", 1))

    d = dict(sim)
    halts = sim.get("halt_days") or []
    # 제거분이 있는 날만 정보를 낸다 — 정지했는데 그 뒤 진입이 0건이면 무정보다.
    eff = [h for h in halts if h["n_removed"] > 0]
    d["n_effective_days"] = len(eff)

    if sim["n_removed"] < min_n or len(eff) < min_d:
        d["verdict"] = "INSUFFICIENT"
        d["reason"] = ("표본 부족 (제거 %d건<%d 또는 유효 정지일 %d<%d)"
                       % (sim["n_removed"], min_n, len(eff), min_d))
        return d

    pos = sum(1 for h in eff if h["krw_removed"] > 0)
    neg = sum(1 for h in eff if h["krw_removed"] < 0)
    p = _sign_test_p(pos, neg)
    d.update({"day_pos": pos, "day_neg": neg, "day_sign_p": round(p, 4)})

    # 이상치 분해 — |제거손익| 최대인 날을 빼도 부호가 유지되는가 (313차 ②)
    worst = sorted(eff, key=lambda h: abs(h["krw_removed"]))[-dropw:] if dropw else []
    rest = round(sim["krw_removed"] - sum(h["krw_removed"] for h in worst), 1)
    d["drop_worst_days_excluded"] = [h["day"] for h in worst]
    d["krw_removed_drop_worst"] = rest
    sign_holds = (rest * sim["krw_removed"]) > 0
    d["drop_worst_sign_holds"] = bool(sign_holds)

    gates = {
        "일자 부호검정 p < %.2f" % alpha: p < alpha,
        "drop-worst 부호 유지": bool(sign_holds),
    }
    d["gates"] = gates
    if not all(gates.values()):
        d["verdict"] = "NO_EVIDENCE"
        d["reason"] = ("표본은 찼으나 관문 미충족 (%s)"
                       % ", ".join(k for k, v in gates.items() if not v))
        return d

    if sim["krw_removed"] < 0:
        d["verdict"] = "RESTORE_FAVORS_CB2"
        d["reason"] = ("제거 손익 %s (<0) — CB②가 손실을 막았을 것"
                       % _krw(sim["krw_removed"]))
    else:
        d["verdict"] = "RESTORE_COSTS"
        d["reason"] = ("제거 손익 %s (>0) — CB②가 수익을 막았을 것"
                       % _krw(sim["krw_removed"]))
    return d


def summarize(out: dict) -> dict:
    """채널 판정.

    ⚠ PASS/FAIL을 쓰지 않는다 — 묻는 것이 "성능이 기준을 넘었는가"가 아니라
      "복원이 어느 방향인가"이기 때문이다(spread_extreme_watch·[55]와 같은 근거).
    """
    res = dict(out)
    per = {}
    for lim, sim in (out.get("judged") or {}).items():
        per[lim] = _judge_one(sim)
    res["per_limit"] = per

    decided = {k: v for k, v in per.items()
               if v["verdict"] in ("RESTORE_FAVORS_CB2", "RESTORE_COSTS")}
    if not decided:
        # 전부 미달이면 그중 표본이 가장 많이 찬 쪽의 사유를 대표로 싣는다.
        reasons = sorted(per.items(), key=lambda kv: -(kv[1].get("n_removed") or 0))
        res["verdict"] = (reasons[0][1]["verdict"] if reasons else "INSUFFICIENT")
        res["reason"] = ("limit=%s: %s" % (reasons[0][0], reasons[0][1]["reason"])
                         if reasons else "표본 없음")
    else:
        dirs = set(v["verdict"] for v in decided.values())
        if len(dirs) > 1:
            res["verdict"] = "SPLIT_BY_LIMIT"
            res["reason"] = ("복원값에 따라 방향이 갈린다 — "
                             + " / ".join("limit=%s %s" % (k, v["verdict"])
                                          for k, v in sorted(decided.items())))
        else:
            res["verdict"] = dirs.pop()
            res["reason"] = " / ".join("limit=%s %s" % (k, v["reason"])
                                       for k, v in sorted(decided.items()))

    res["headline"] = res["reason"] + (
        " · 판정창 %s~ %s포지션/%s일 · 라이브 CB②=%s(%s)"
        % (out.get("start_date", "—"), out.get("n_positions_judged", 0),
           out.get("n_days_judged", 0), out.get("live_limit"),
           "활성" if out.get("live_limit_active") else "비활성"))
    return res


# ──────────────────────────────────────────────────────────────────────────
def render(res: dict) -> str:
    L = ["[56] CB② 복원 반사실 — 사전등록 판정 (포지션 단위, 470차 C1 규칙)", ""]
    L.append("  라이브 CB_CONSEC_STOP_LIMIT = %s (%s)"
             % (res.get("live_limit"), "활성" if res.get("live_limit_active") else "비활성"))
    L.append("  판정창 %s~ : %s포지션 / %s거래일"
             % (res.get("start_date"), res.get("n_positions_judged"),
                res.get("n_days_judged")))
    L.append("")
    for lim, d in sorted((res.get("per_limit") or {}).items()):
        L.append("  --- limit=%s ---" % lim)
        L.append("    판정      : %s — %s" % (d.get("verdict"), d.get("reason")))
        L.append("    정지일    : %s (유효 %s)"
                 % (d.get("n_halt_days"), d.get("n_effective_days", "—")))
        L.append("    제거      : %s포지션 / %s"
                 % (d.get("n_removed", 0), _krw(d.get("krw_removed", 0.0))))
        if d.get("krw_removed_drop_worst") is not None:
            L.append("    drop-worst: %s 제외 → %s (부호유지 %s)"
                     % (",".join(d.get("drop_worst_days_excluded") or []),
                        _krw(d["krw_removed_drop_worst"]),
                        d.get("drop_worst_sign_holds")))
        for h in (d.get("halt_days") or [])[-10:]:
            L.append("      %s  정지 %s  제거 %d포지션  %s"
                     % (h["day"], str(h["halt_ts"])[11:], h["n_removed"],
                        _krw(h["krw_removed"])))
        L.append("")
    seed = res.get("seed") or {}
    if seed:
        L.append("  --- 사후탐색 씨앗 (%s 이전, **판정 미반영**) ---"
                 % res.get("start_date"))
        for lim, s in sorted(seed.items()):
            L.append("    limit=%s : %s일 정지 / %s포지션 제거 / %s"
                     % (lim, s["n_halt_days"], s["n_removed"], _krw(s["krw_removed"])))
        L.append("    ⚠ 이 값으로 복원값을 고르지 말 것 (313차 원칙 ④).")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--since", default="2026-07-14")
    a = ap.parse_args()
    res = summarize(compute(a.since))
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render(res))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
