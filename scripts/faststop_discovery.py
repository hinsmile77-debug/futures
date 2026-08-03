"""[MW0601 421차 후속9 / Phase A] 급행 풀스톱 판별자 **발굴** 하네스 — 읽기 전용.

무엇을 하는 스크립트인가
------------------------
급행 풀스톱(FAST: TP1 미도달 + 보유 ≤150초)을 진입 **시점** 정보만으로 가려낼 수
있는 후보 지표를 넓게 훑는다. **발굴(discovery) 전용이며 판정하지 않는다.**

왜 발굴과 확증을 분리하나
-------------------------
2026-08-03 세션에서 표본 구성(모집단·거래일·호라이즌)을 확인하기 전에 결론을 낸
과잉해석이 3회 나왔다(DECISION_LOG 421차 후속5). 같은 표본에서 그물을 치고 그
표본으로 판정까지 내리면 그 실수가 제도화된다. 그래서:

    Phase A(이 스크립트) : 넓게 훑어 **후보 랭킹만** 출력
    → 사람이 top-K(<=5)를 골라 방향·효과크기와 함께 사전등록
    Phase B/C            : 등록일 **이후 신규 데이터**로만 확증

이 스크립트는 후보를 자동 등록하지 않는다(§9).

왜 "일자 내 순열검정"인가 — 이 스크립트의 핵심
---------------------------------------------
FAST 20건 중 15건이 단 3개 거래일에 몰려 있다(07-22 6, 08-03 6, 07-23 3).
단순 t검정을 돌리면 **"그날은 변동성이 컸다"** 류의 날짜 효과가 판별자로 위장된다
— ATR·스프레드·toxicity 같은 피처는 전부 그렇게 통과해버린다.

그래서 라벨(FAST/OK)을 **각 거래일 내부에서만** 셔플해 귀무분포를 만든다. 질문이
"FAST가 많은 날은 어떤 날인가"가 아니라 **"같은 날 안에서 FAST와 OK를 가르는 것은
무엇인가"** 로 바뀐다. 날짜 수준 교란은 구조적으로 제거된다.

부작용으로 **유효 표본이 줄어든다** — FAST와 OK가 둘 다 있는 날만 정보를 낸다.
그것이 정직한 표본이며, 줄어든 수치를 그대로 출력한다.

한계 (반드시 함께 읽을 것)
--------------------------
- 발굴 결과의 p값은 **탐색적**이다. 같은 표본에서 확증하면 안 된다.
- 라벨 경계 150초는 [15] fast_reversal_watch 정의를 그대로 쓴다. 경계 민감도는
  --sweep 으로 ±60초를 함께 보되, **경계 튜닝 결과를 확증에 반입하지 말 것.**
- 결측이 많은 피처는 유효 표본이 더 작다. n_used를 함께 출력한다.
- 판별자가 **존재하지 않을 가능성**이 낮지 않다(가격기반 4지표·InstabilityGate가
  이미 실패). 전멸도 유효한 결과이며 그 경우 자원을 청산기하·집행 축으로 옮긴다.

사용법
------
    python scripts/faststop_discovery.py
    python scripts/faststop_discovery.py --since 2026-06-01 --perm 20000
    python scripts/faststop_discovery.py --out docs/정기점검/금요일점검/0803_faststop_discovery_후보표.md
    python scripts/faststop_discovery.py --sweep        # 라벨 경계 90/150/210초 비교
"""
from __future__ import annotations

import argparse
import datetime
import io
import json
import math
import os
import random
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 단독 실행 시 콘솔이 cp949로 잡혀 죽는 것 방지 — 캠페인 스크립트 공통 패턴.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from config.settings import VALIDATION_CAMPAIGN

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADES_DB = os.path.join(_ROOT, "data", "db", "trades.db")
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")
PRED_DB = os.path.join(_ROOT, "data", "db", "predictions.db")

# [15] fast_reversal_watch의 정의를 그대로 재사용한다 — 여기서 새로 만들지 않는다.
FAST_MAX_SEC = float(
    (VALIDATION_CAMPAIGN.get("fast_reversal_watch") or {}).get("fast_exit_max_sec", 150)
)
FDR_Q = 0.10          # 발굴 단계 — 관대하게
MIN_USED = 12         # 이보다 적은 유효표본 피처는 랭킹에서 제외
DEFAULT_PERM = 10000


# ──────────────────────────────────────────────────────────────────────────
# 데이터 로드
# ──────────────────────────────────────────────────────────────────────────
def _conn(path):
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c


def load_positions(since: str, fast_max_sec: float):
    """포지션 단위(entry_ts 그룹)로 병합하고 FAST/OK 라벨을 붙인다."""
    with _conn(TRADES_DB) as c:
        tp1 = {r[0] for r in c.execute("SELECT entry_ts FROM synthetic_partial_exits")}
        rows = [dict(r) for r in c.execute(
            "SELECT entry_ts, exit_ts, direction, entry_horizon, hurst_bucket, grade, "
            "       quantity, net_pnl_krw "
            "  FROM trades WHERE entry_ts >= ? AND entry_source='SYSTEM_AUTO' "
            " ORDER BY entry_ts", (since,))]

    pos = {}
    for r in rows:
        k = r["entry_ts"]
        p = pos.setdefault(k, {
            "entry_ts": k, "day": k[:10], "exit_ts": r["exit_ts"],
            "direction": r["direction"], "horizon": r["entry_horizon"],
            "hurst": r["hurst_bucket"], "grade": r["grade"], "net": 0.0, "qty": 0,
        })
        p["net"] += float(r["net_pnl_krw"] or 0.0)
        p["qty"] += int(r["quantity"] or 0)
        if r["exit_ts"] > p["exit_ts"]:
            p["exit_ts"] = r["exit_ts"]

    fmt = "%Y-%m-%d %H:%M:%S"
    out = []
    for p in pos.values():
        hold = (datetime.datetime.strptime(p["exit_ts"], fmt)
                - datetime.datetime.strptime(p["entry_ts"], fmt)).total_seconds()
        p["hold_sec"] = hold
        p["reached_tp1"] = p["entry_ts"] in tp1
        p["label"] = 0 if (not p["reached_tp1"] and hold <= fast_max_sec) else 1  # 0=FAST, 1=OK
        out.append(p)
    out.sort(key=lambda x: x["entry_ts"])
    return out


def _minute(ts: str) -> str:
    return ts[:16] + ":00"


def load_features(positions):
    """진입 분봉 기준으로 그물 5축을 조인한다. 전부 기존 저장분 — 라이브 무접촉."""
    minutes = {_minute(p["entry_ts"]) for p in positions}
    prev_minutes = set()
    for m in minutes:
        dt = datetime.datetime.strptime(m, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(minutes=1)
        prev_minutes.add(dt.strftime("%Y-%m-%d %H:%M:%S"))

    # A/B: raw_features (진입 분 + 직전 분)
    raw = {}
    with _conn(RAW_DB) as c:
        for ts, fj in c.execute(
                "SELECT ts, features FROM raw_features WHERE ts >= ?",
                (min(minutes | prev_minutes),)):
            if ts in minutes or ts in prev_minutes:
                try:
                    raw[ts] = json.loads(fj)
                except Exception:
                    pass

    # C/D: ensemble_decisions
    ed = {}
    with _conn(PRED_DB) as c:
        cols = {r[1] for r in c.execute("PRAGMA table_info(ensemble_decisions)")}
        for r in c.execute("SELECT * FROM ensemble_decisions WHERE ts >= ?",
                           (min(minutes),)):
            if r["ts"] in minutes:
                ed[r["ts"]] = dict(r)

    _SKIP_ED = {"id", "ts", "created_at", "detail", "features", "gate_signals",
                "entry_gate_json", "regime", "micro_regime", "gate_reason",
                "meta_reason", "toxicity_reason", "entry_mode", "entry_block_reason",
                "checklist_reason", "meta_gate_horizon", "grade",
                # [누출 방지] 아래는 "진입 시점 상태"가 아니라 **진입 결정의 결과**를
                # 기술하는 필드다. 판별자로 뽑히면 동어반복이 된다. 초판에서
                # ed.auto_entry가 상위 12위로 올라와(68/11 분포) 걸러낸다.
                "auto_entry", "entry_executed", "entry_final_ok"}

    for p in positions:
        m = _minute(p["entry_ts"])
        pm = (datetime.datetime.strptime(m, "%Y-%m-%d %H:%M:%S")
              - datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
        f = {}

        cur, prv = raw.get(m) or {}, raw.get(pm) or {}
        for k, v in cur.items():
            if isinstance(v, bool):
                f["rf.%s" % k] = 1.0 if v else 0.0
            elif isinstance(v, (int, float)):
                f["rf.%s" % k] = float(v)
                pv = prv.get(k)
                if isinstance(pv, (int, float)) and not isinstance(pv, bool):
                    f["d1.%s" % k] = float(v) - float(pv)

        d = ed.get(m) or {}
        for k, v in d.items():
            if k in _SKIP_ED:
                continue
            if isinstance(v, bool):
                f["ed.%s" % k] = 1.0 if v else 0.0
            elif isinstance(v, (int, float)):
                f["ed.%s" % k] = float(v)
        gj = d.get("entry_gate_json")
        if gj:
            try:
                for k, v in json.loads(gj).items():
                    if isinstance(v, bool):
                        f["gate.%s" % k] = 1.0 if v else 0.0
            except Exception:
                pass

        # E: 컨텍스트
        hh = int(p["entry_ts"][11:13])
        f["ctx.hour"] = float(hh)
        f["ctx.is_morning"] = 1.0 if hh < 12 else 0.0
        f["ctx.dir_long"] = 1.0 if p["direction"] == "LONG" else 0.0
        f["ctx.qty"] = float(p["qty"])
        for h in ("1m", "3m", "5m"):
            f["ctx.hz_%s" % h] = 1.0 if p["horizon"] == h else 0.0
        for b in ("trend", "neutral", "mean-revert"):
            f["ctx.hurst_%s" % b] = 1.0 if p["hurst"] == b else 0.0

        p["feat"] = f
    return positions


# ──────────────────────────────────────────────────────────────────────────
# 통계 — 일자 층화 평균차 + 일자 내 라벨 순열검정
# ──────────────────────────────────────────────────────────────────────────
def _strat_stat(groups):
    """일자 층화 평균차. groups = [(fast_vals, ok_vals), ...] (거래일별).

    가중치는 조화평균 n_f*n_o/(n_f+n_o) — 층화 평균차의 표준 가중이며, 한쪽이
    비면 0이 되어 그 날은 자동으로 정보를 내지 않는다.
    """
    num = den = 0.0
    for fv, ov in groups:
        if not fv or not ov:
            continue
        w = len(fv) * len(ov) / float(len(fv) + len(ov))
        num += w * (sum(fv) / len(fv) - sum(ov) / len(ov))
        den += w
    return (num / den) if den > 0 else None


def analyze_feature(by_day, n_perm, rng):
    """by_day = {day: [(label, value), ...]}  label 0=FAST 1=OK"""
    groups, n_f, n_o, days_used = [], 0, 0, 0
    for day, items in by_day.items():
        fv = [v for l, v in items if l == 0]
        ov = [v for l, v in items if l == 1]
        if fv and ov:
            groups.append((fv, ov))
            n_f += len(fv); n_o += len(ov); days_used += 1
    if days_used == 0:
        return None
    obs = _strat_stat(groups)
    if obs is None:
        return None

    # 산포 정규화 — 피처 스케일이 제각각이라 효과크기 비교용
    allv = [v for fv, ov in groups for v in (fv + ov)]
    mu = sum(allv) / len(allv)
    sd = math.sqrt(sum((x - mu) ** 2 for x in allv) / max(len(allv) - 1, 1))
    if sd <= 0:
        return None  # 상수 피처

    # 일자 내 라벨 셔플 — 날짜 수준 교란을 구조적으로 제거
    flat = [(day, [l for l, _ in items], [v for _, v in items])
            for day, items in by_day.items()]
    hit = 0
    for _ in range(n_perm):
        gs = []
        for _day, labs, vals in flat:
            if len(set(labs)) < 2:
                continue
            perm = labs[:]
            rng.shuffle(perm)
            fv = [v for l, v in zip(perm, vals) if l == 0]
            ov = [v for l, v in zip(perm, vals) if l == 1]
            if fv and ov:
                gs.append((fv, ov))
        s = _strat_stat(gs)
        if s is not None and abs(s) >= abs(obs) - 1e-15:
            hit += 1
    p = (hit + 1) / float(n_perm + 1)   # add-one (순열검정 관례)

    # 강건성: leave-one-day-out
    signs, l1o = [], []
    for i in range(len(groups)):
        sub = groups[:i] + groups[i + 1:]
        s = _strat_stat(sub)
        if s is not None:
            l1o.append(s)
            signs.append(1 if s * obs > 0 else 0)
    return {
        "effect": obs, "effect_sd": obs / sd, "p": p,
        "n_fast": n_f, "n_ok": n_o, "n_used": n_f + n_o, "days": days_used,
        "sign_keep": sum(signs), "sign_total": len(signs),
        "l1o_min": min(l1o) if l1o else None, "l1o_max": max(l1o) if l1o else None,
    }


def bh_fdr(results, q):
    """Benjamini-Hochberg — 통과한 항목에 rank/threshold를 표시한다."""
    ordered = sorted(results, key=lambda r: r["p"])
    m = len(ordered)
    k_max = 0
    for i, r in enumerate(ordered, 1):
        if r["p"] <= q * i / m:
            k_max = i
    for i, r in enumerate(ordered, 1):
        r["bh_rank"] = i
        r["bh_thr"] = q * i / m
        r["bh_pass"] = i <= k_max
    return ordered, k_max


# ──────────────────────────────────────────────────────────────────────────
def run(since, n_perm, fast_max_sec, seed=20260803):
    pos = load_positions(since, fast_max_sec)
    if not pos:
        return None
    load_features(pos)
    rng = random.Random(seed)

    keys = set()
    for p in pos:
        keys |= set(p["feat"].keys())

    results = []
    for k in sorted(keys):
        by_day = {}
        for p in pos:
            v = p["feat"].get(k)
            if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
                continue
            by_day.setdefault(p["day"], []).append((p["label"], v))
        r = analyze_feature(by_day, n_perm, rng)
        if r and r["n_used"] >= MIN_USED:
            r["feature"] = k
            results.append(r)

    ordered, k_max = bh_fdr(results, FDR_Q)
    n_fast = sum(1 for p in pos if p["label"] == 0)
    return {
        "positions": pos, "results": ordered, "n_signif": k_max,
        "n_fast": n_fast, "n_ok": len(pos) - n_fast,
        "days": len({p["day"] for p in pos}),
        "n_tested": len(results), "fast_max_sec": fast_max_sec,
    }


def _fmt(out, since, n_perm):
    L = []
    A = L.append
    A("# 급행 풀스톱 판별자 **발굴** 결과 (Phase A)")
    A("")
    A("- 생성: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    A("- 기간: %s~ / 포지션 **%d**건(FAST %d · OK %d) / 거래일 %d일"
      % (since, len(out["positions"]), out["n_fast"], out["n_ok"], out["days"]))
    A("- 라벨: FAST = TP1 미도달 ∧ 보유 ≤ **%.0f초** ([15] fast_reversal_watch 정의 재사용)"
      % out["fast_max_sec"])
    A("- 검정: **일자 내 라벨 순열** %d회 (날짜 수준 교란 제거) / BH FDR %.0f%%"
      % (n_perm, FDR_Q * 100))
    A("- 검정 피처 수: %d" % out["n_tested"])
    A("")
    A("> ⚠ **이 결과는 탐색적이다. 같은 표본으로 확증하지 말 것.**")
    A("> 여기서 고른 후보는 방향·효과크기와 함께 사전등록한 뒤 **등록일 이후 신규**")
    A("> 데이터로만 확증한다(Phase B/C). 이 스크립트는 자동 등록하지 않는다(§9).")
    A("")
    if out["n_signif"] == 0:
        A("## 결과: **BH FDR %.0f%% 통과 피처 없음**" % (FDR_Q * 100))
        A("")
        _pmin = out["results"][0]["p"] if out["results"] else float("nan")
        A("가장 강한 후보의 p = **%.4f**인데, 검정 %d개에서 순수 노이즈가 만들어내는"
          % (_pmin, out["n_tested"]))
        A("최소 p의 기대치가 ≈ 1/%d = **%.4f**다. 즉 **최강 후보조차 노이즈 기대치와"
          % (out["n_tested"], 1.0 / max(out["n_tested"], 1)))
        A("구별되지 않는다.**")
        A("")
        A("일자 내 변동으로는 FAST를 가르는 축이 발견되지 않았다. 이는 유효한 결과이며,")
        A("가격기반 4지표·InstabilityGate가 이미 실패한 것과 같은 방향이다.")
        A("계획서 §1 항목4의 부정적 verdict(진입측 판별 불가) 후보 근거로 쓸 수 있다 —")
        A("단 **확증창을 거치기 전에는 확정이 아니다.**")
        A("")
    else:
        A("## BH 통과 **%d개**" % out["n_signif"])
        A("")
    A("## 상위 25개 (p 오름차순)")
    A("")
    A("| # | 피처 | 방향 | 효과(원단위) | 효과(SD) | p | BH | 유효n | FAST/OK | 일수 | 부호유지 |")
    A("|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(out["results"][:25], 1):
        A("| %d | `%s` | %s | %+.4g | %+.3f | %.4f | %s | %d | %d/%d | %d | %d/%d |" % (
            i, r["feature"], "FAST↑" if r["effect"] > 0 else "FAST↓",
            r["effect"], r["effect_sd"], r["p"],
            "✅" if r["bh_pass"] else "—",
            r["n_used"], r["n_fast"], r["n_ok"], r["days"],
            r["sign_keep"], r["sign_total"]))
    A("")
    A("- **방향**: `FAST↑` = 급행 풀스톱에서 값이 더 큼")
    A("- **효과(SD)**: 전체 산포로 나눈 표준화 효과크기 — 피처 간 비교용")
    A("- **부호유지**: leave-one-day-out에서 부호가 유지된 일수 / 전체 일수.")
    A("  이 값이 낮으면 특정 하루가 만든 효과다(372차 이상치 분해와 같은 취지)")
    A("")
    A("> ⚠ **부호유지 지표는 현재 표본에서 판별력이 거의 없다** — 거래일이 7일뿐이라")
    A("> 하루를 빼도 층화 추정치의 부호가 좀처럼 뒤집히지 않는다(상위 20개가 전부 7/7).")
    A("> 거래일이 15일 이상 쌓이기 전에는 이 열을 근거로 쓰지 말 것.")
    A("")
    A("> ⚠ **상위 항목은 서로 독립이 아니다.** 초판 상위 7개 중 5개가 `opt_pcr_*`")
    A("> 계열이었고 `opt_pcr_norm`↔`opt_pcr_extreme_signed`는 **r=+1.000**(같은 변수),")
    A("> 나머지도 |r|=0.55~0.94였다. 즉 실질 독립 검정 수는 표기된 피처 수보다 훨씬")
    A("> 적다 — BH가 그만큼 보수적으로 작동한다는 뜻이며, 동시에 \"여러 지표가 함께")
    A("> 나왔다\"를 독립 증거로 읽으면 안 된다는 뜻이다.")
    A("")
    A("## 다음 단계")
    A("")
    A("1. 위 표에서 **top-K ≤ 5**를 사람이 고른다 (자동 선택 금지)")
    A("2. 방향·효과크기·부호유지를 **사전등록 문안**에 그대로 박는다")
    A("3. `VALIDATION_CAMPAIGN[\"faststop_discriminant_watch\"]` 신설 (Phase B)")
    A("4. 등록일 이후 신규 데이터로만 확증 (Phase C, 4주+)")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-06-01")
    ap.add_argument("--perm", type=int, default=DEFAULT_PERM)
    ap.add_argument("--out", default=None)
    ap.add_argument("--sweep", action="store_true", help="라벨 경계 90/150/210초 비교")
    a = ap.parse_args()

    out = run(a.since, a.perm, FAST_MAX_SEC)
    if not out:
        print("포지션 없음")
        return 1

    print("=" * 92)
    print("급행 풀스톱 판별자 발굴 (Phase A) — 탐색적, 판정 아님")
    print("=" * 92)
    print("기간 %s~ / 포지션 %d (FAST %d · OK %d) / 거래일 %d / 피처 %d / 순열 %d회"
          % (a.since, len(out["positions"]), out["n_fast"], out["n_ok"],
             out["days"], out["n_tested"], a.perm))
    print("라벨 경계 %.0f초 · BH FDR %.0f%%  →  통과 %d개"
          % (out["fast_max_sec"], FDR_Q * 100, out["n_signif"]))
    print()
    print("%-34s %-6s %9s %8s %7s %3s %6s %6s" %
          ("피처", "방향", "효과SD", "p", "BH", "일", "n", "부호"))
    print("-" * 92)
    for r in out["results"][:20]:
        print("%-34s %-6s %+9.3f %8.4f %7s %3d %6d %4d/%d" % (
            r["feature"][:34], "FAST↑" if r["effect"] > 0 else "FAST↓",
            r["effect_sd"], r["p"], "PASS" if r["bh_pass"] else "-",
            r["days"], r["n_used"], r["sign_keep"], r["sign_total"]))
    print()
    if out["n_signif"] == 0:
        print("→ BH 통과 0개. 일자 내 변동으로는 FAST를 가르는 축이 발견되지 않았다.")
        print("  이는 유효한 결과다 — 계획서 §1 항목4 부정적 verdict의 후보 근거.")
        print("  단 확증창을 거치기 전에는 확정이 아니다.")
    else:
        print("→ 상위 후보 중 top-K(≤5)를 **사람이** 골라 사전등록할 것. 자동 등록 없음(§9).")

    if a.sweep:
        print()
        print("=== 라벨 경계 민감도 (경계 튜닝 결과를 확증에 반입하지 말 것) ===")
        for sec in (90.0, 150.0, 210.0):
            o = run(a.since, max(a.perm // 5, 1000), sec)
            print("  %5.0f초 → FAST %2d / OK %2d / BH통과 %d"
                  % (sec, o["n_fast"], o["n_ok"], o["n_signif"]))

    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        with io.open(a.out, "w", encoding="utf-8") as f:
            f.write(_fmt(out, a.since, a.perm))
        print()
        print("후보표 저장: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
