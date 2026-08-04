# -*- coding: utf-8 -*-
"""[MW0602 428차 / A-1] 무작위 진입 대조 — "우리 돈은 어디서 오는가".

무엇을 하는 스크립트인가
------------------------
**같은 진입 시각·같은 청산 기하**에서 시스템의 실제 방향 선택과 **동전던지기**를
비교한다. 두 팔 모두 동일한 시뮬레이터를 통과하므로, 차이가 있다면 그것은 오직
**방향 선택의 기여분**이다.

왜 필요한가
-----------
2026-08-04 점검에서 방향 축의 무력함이 세 갈래로 확인됐다:

  · 전 호라이즌 15거래일 적중률 33% 근방 (랜덤과 구분 안 됨)
  · confidence 판별력 승/패 격차 -0.0008 ([39] REJECTS_HYP)
  · 그런데 승률 63%, 캠페인 손익 양수

즉 **돈이 방향에서 오지 않는데 어디서 오는지 아무도 재본 적이 없다.** 이 스크립트가
그 질문에 직접 답한다. 그리고 그 답은 연구 우선순위 전체를 좌우한다 —
`docs/미륵이고도화3` 로드맵의 이월 D·E·G는 전부 **방향 피처 재배치**다.

⚠ 절대 수준을 인용하지 말 것
-----------------------------
시뮬레이터는 단순화돼 있다: TP1(33% 부분익절) + 본전이동 + TP2 + 하드스톱 + 종가청산.
**트레일링 계단·틱 청산·손절계단화·ProfitGuard·수수료/슬리피지가 전부 없다.**
따라서 실제 손익을 재현하지 못한다.

**유효한 것은 두 팔의 비교뿐이며, 같은 시뮬이므로 그 비교는 공정하다.**
비용을 빼지 않은 것도 의도적이다 — 양쪽에 동일하게 작용해 비교에서 상쇄된다.

사용
----
    python scripts/random_entry_control.py
    python scripts/random_entry_control.py --since 2026-07-14 --trials 1000
    python scripts/random_entry_control.py --json      # 기계 판독용

읽기 전용이다. DB에 아무것도 쓰지 않는다.
"""
import argparse
import collections
import datetime
import io
import json
import os
import random
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("MIREUK_TEST_MODE", "1")  # 프로덕션 로그·Slack 오염 차단

from config.settings import (  # noqa: E402
    TRADES_DB, PREDICTIONS_DB, RAW_DATA_DB,
    ATR_STOP_MULT, ATR_TP1_MULT, ATR_TP2_MULT,
    PARTIAL_EXIT_RATIOS, VALIDATION_CAMPAIGN,
)

_TS = "%Y-%m-%d %H:%M:%S"
_SESSION_LAST = "15:09"     # 15:10 강제청산 직전 마지막 완성 분봉
_SYSTEM_AUTO_SQL = (
    "(COALESCE(entry_source,'') = 'SYSTEM_AUTO' "
    " OR (entry_source IS NULL AND COALESCE(grade,'') <> 'MANUAL'))"
)


def _conn(path):
    c = sqlite3.connect(path, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def load_inputs(since):
    """진입 목록 · ATR 맵 · 일자별 분봉을 읽는다 (전부 읽기 전용)."""
    with _conn(TRADES_DB) as c:
        entries = [dict(r) for r in c.execute(
            "SELECT entry_ts, MIN(direction) AS direction, MIN(entry_price) AS px "
            "  FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND %s "
            " GROUP BY entry_ts ORDER BY entry_ts" % _SYSTEM_AUTO_SQL, (since,))]

    # ATR은 결정 시점 피처에서 온다. 체결이 분 경계를 넘으면 결정은 T-1분이므로
    # (427차 후속 실측: 19%가 그렇다) T → T-1 순으로 찾는다.
    atr = {}
    with _conn(PREDICTIONS_DB) as c:
        for r in c.execute("SELECT ts, features FROM ensemble_decisions WHERE ts >= ?",
                           (since,)):
            try:
                a = float((json.loads(r["features"]) or {}).get("atr") or 0.0)
            except (ValueError, TypeError):
                a = 0.0
            if a > 0:
                atr[str(r["ts"])[:16]] = a

    bars = collections.defaultdict(list)
    with _conn(RAW_DATA_DB) as c:
        for r in c.execute("SELECT ts, high, low, close FROM raw_candles WHERE ts >= ?",
                           (since,)):
            bars[str(r["ts"])[:10]].append(
                (str(r["ts"]), float(r["high"]), float(r["low"]), float(r["close"])))
    for d in bars:
        bars[d].sort()
    return entries, atr, bars


def _atr_for(ets, atr):
    k = ets[:16]
    if k in atr:
        return atr[k]
    try:
        prev = (datetime.datetime.strptime(ets, _TS).replace(second=0)
                - datetime.timedelta(minutes=1)).strftime(_TS)[:16]
    except ValueError:
        return None
    return atr.get(prev)


def simulate(ets, px, sign, a, bars):
    """단순화된 청산 기하 1회 시뮬. 반환은 계약 1개 기준 pt.

    순서는 라이브 STEP8과 같다 — 하드스톱 → TP2 → TP1. 같은 봉에서 스톱과 목표가
    동시에 닿으면 **스톱을 우선**한다(보수적, 낙관 편향 방지).
    TP1 도달 시 `PARTIAL_EXIT_RATIOS[0]`만큼 확정하고 스톱을 진입가로 올린다
    (라이브 `tp1_breakeven`과 동일).
    """
    day = ets[:10]
    stop = px - sign * a * ATR_STOP_MULT
    tp1 = px + sign * a * ATR_TP1_MULT
    tp2 = px + sign * a * ATR_TP2_MULT
    r1 = float(PARTIAL_EXIT_RATIOS[0])
    booked, rest, tp1_done = 0.0, 1.0, False

    for ts, hi, lo, cl in bars.get(day, ()):
        if ts[:16] <= ets[:16] or ts[11:16] > _SESSION_LAST:
            continue
        hit_stop = (lo <= stop) if sign > 0 else (hi >= stop)
        hit_tp2 = (hi >= tp2) if sign > 0 else (lo <= tp2)
        hit_tp1 = (hi >= tp1) if sign > 0 else (lo <= tp1)
        if hit_stop:
            return booked + (stop - px) * sign * rest
        if hit_tp2:
            return booked + (tp2 - px) * sign * rest
        if hit_tp1 and not tp1_done:
            tp1_done = True
            booked += (tp1 - px) * sign * r1
            rest -= r1
            stop = px        # 본전 이동
    day_bars = bars.get(day) or ()
    last = day_bars[-1][3] if day_bars else px
    return booked + (last - px) * sign * rest


def run(since, trials, seed):
    entries, atr, bars = load_inputs(since)
    usable = []
    for e in entries:
        a = _atr_for(str(e["entry_ts"]), atr)
        if a:
            usable.append((str(e["entry_ts"]), float(e["px"]),
                           1 if str(e["direction"]) == "LONG" else -1, a))
    out = {
        "since": since, "trials": trials, "seed": seed,
        "n_entries": len(entries), "n_usable": len(usable),
        "n_days": len({e[0][:10] for e in usable}),
    }
    if not usable:
        out["error"] = "시뮬 가능한 진입이 없다 (ATR 미확보)"
        return out

    actual = [(ets[:10], simulate(ets, px, sg, a, bars)) for ets, px, sg, a in usable]
    A = sum(v for _, v in actual)
    out["actual_pt"] = round(A, 4)
    out["actual_win_rate"] = round(
        sum(1 for _, v in actual if v > 0) / float(len(actual)), 4)

    rnd = random.Random(seed)
    totals, wins = [], []
    for _ in range(trials):
        s, w = 0.0, 0
        for ets, px, _sg, a in usable:
            v = simulate(ets, px, rnd.choice((1, -1)), a, bars)
            s += v
            w += 1 if v > 0 else 0
        totals.append(s)
        wins.append(w / float(len(usable)))
    totals.sort()
    n = len(totals)
    out["random_median_pt"] = round(totals[n // 2], 4)
    out["random_p05_pt"] = round(totals[int(n * 0.05)], 4)
    out["random_p95_pt"] = round(totals[int(n * 0.95)], 4)
    out["random_mean_win_rate"] = round(sum(wins) / float(len(wins)), 4)
    # 단측 p — "실제가 무작위보다 좋다"는 대립가설. (+1)/(n+1)은 순열검정 관례.
    out["p_one_sided"] = round((sum(1 for x in totals if x >= A) + 1) / float(n + 1), 4)
    out["beats_random_share"] = round(sum(1 for x in totals if x < A) / float(n), 4)

    # 일자단위(313차) — 하루 단위 실제 합이 그날 무작위 중앙값을 넘는 날 수
    by_day_actual = collections.defaultdict(float)
    for d, v in actual:
        by_day_actual[d] += v
    day_beats = 0
    for d in sorted(by_day_actual):
        sub = [u for u in usable if u[0][:10] == d]
        sims = []
        for _ in range(max(50, trials // 8)):
            sims.append(sum(simulate(e, p, rnd.choice((1, -1)), a, bars)
                            for e, p, _s, a in sub))
        sims.sort()
        if by_day_actual[d] > sims[len(sims) // 2]:
            day_beats += 1
    out["days_beating_random"] = day_beats
    out["days_evaluated"] = len(by_day_actual)
    return out


def run_three_arm(since, trials, seed, entry_window=("09:05", "14:49")):
    """[MW0602 429차 / A-2 확장] 3팔 비교 — **타점(진입 시각)의 가치를 격리**한다.

        A) 실제 시각 + 실제 방향     — 현행 시스템
        B) 실제 시각 + 무작위 방향   — 방향만 제거 (= run()의 무작위 팔)
        C) 무작위 시각 + 무작위 방향 — 방향과 **타점을 함께** 제거

    `B − C`가 곧 **체크리스트/게이트가 고른 타점의 기여분**이다. `run()`은
    A vs B만 봐서 방향 축만 격리했고, 타점 축은 재지 않았다.

    **짝지은 검정을 쓴다.** 같은 시행 인덱스에서 B와 C를 뽑아 `B_i − C_i`의 부호를
    센다 — 두 팔이 같은 시장 데이터를 공유해 양의 상관을 갖기 때문에, 독립 표본
    비교로 다루면 p가 낙관적으로 나온다.

    C의 후보 분봉은 `entry_window` 안에서 ATR이 있는 분으로 제한한다 —
    라이브도 14:50부터 신규 진입 금지(345차)라 그 밖은 애초에 진입할 수 없다.
    각 거래일에 **실제와 같은 건수**를 뽑아 일자별 진입 빈도를 보존한다.
    """
    entries, atr, bars = load_inputs(since)
    usable = []
    for e in entries:
        a = _atr_for(str(e["entry_ts"]), atr)
        if a:
            usable.append((str(e["entry_ts"]), float(e["px"]),
                           1 if str(e["direction"]) == "LONG" else -1, a))
    out = {"since": since, "trials": trials, "seed": seed,
           "n_usable": len(usable),
           "n_days": len({u[0][:10] for u in usable}),
           "entry_window": list(entry_window)}
    if not usable:
        out["error"] = "시뮬 가능한 진입이 없다 (ATR 미확보)"
        return out

    per_day = collections.Counter(u[0][:10] for u in usable)
    cand = collections.defaultdict(list)
    for d, blist in bars.items():
        if d not in per_day:
            continue
        for ts, hi, lo, cl in blist:
            if entry_window[0] <= ts[11:16] <= entry_window[1]:
                a = atr.get(ts[:16])
                if a:
                    cand[d].append((ts, cl, a))
    out["n_candidate_bars"] = sum(len(v) for v in cand.values())

    out["arm_a_pt"] = round(sum(simulate(e, p, s, a, bars)
                                for e, p, s, a in usable), 4)
    rnd = random.Random(seed)
    B, C, diff = [], [], []
    for _ in range(trials):
        b = sum(simulate(e, p, rnd.choice((1, -1)), a, bars)
                for e, p, _s, a in usable)
        c = 0.0
        for d, k in per_day.items():
            pool = cand.get(d) or []
            if not pool:
                continue
            for ts, cl, a in rnd.sample(pool, min(k, len(pool))):
                c += simulate(ts, cl, rnd.choice((1, -1)), a, bars)
        B.append(b)
        C.append(c)
        diff.append(b - c)
    Bs, Cs = sorted(B), sorted(C)
    n = len(Bs)
    out["arm_b_median_pt"] = round(Bs[n // 2], 4)
    out["arm_b_p05_pt"] = round(Bs[int(n * 0.05)], 4)
    out["arm_b_p95_pt"] = round(Bs[int(n * 0.95)], 4)
    out["arm_c_median_pt"] = round(Cs[n // 2], 4)
    out["arm_c_p05_pt"] = round(Cs[int(n * 0.05)], 4)
    out["arm_c_p95_pt"] = round(Cs[int(n * 0.95)], 4)
    out["timing_gain_pt"] = round(out["arm_b_median_pt"] - out["arm_c_median_pt"], 4)
    pos = sum(1 for x in diff if x > 0)
    out["trials_b_over_c"] = pos
    out["b_over_c_share"] = round(pos / float(n), 4)
    # 짝지은 부호검정(양측). p0=0.5 — 타점에 정보가 없으면 B와 C가 반반이다.
    out["sign_p"] = round(_binom_two_sided(min(pos, n - pos), n), 6)
    return out


def _binom_two_sided(k, n):
    """양측 이항검정 p (p0=0.5). trials가 커도 로그공간으로 안전하게 계산한다."""
    if n <= 0:
        return 1.0
    import math
    lg = math.lgamma
    tail = 0.0
    for i in range(0, min(k, n - k) + 1):
        tail += math.exp(lg(n + 1) - lg(i + 1) - lg(n - i + 1) - n * math.log(2.0))
    return min(1.0, 2.0 * tail)


def _utf8_stdout():
    """cp949 콘솔에서 em-dash 등이 UnicodeEncodeError를 내는 것을 막는다."""
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                      errors="replace")
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", default=None,
                    help="시작일(YYYY-MM-DD). 기본은 캠페인 시작일")
    ap.add_argument("--trials", type=int, default=400, help="무작위 시행 횟수")
    ap.add_argument("--seed", type=int, default=428, help="난수 시드(재현성)")
    ap.add_argument("--json", action="store_true", help="JSON만 출력")
    args = ap.parse_args()
    _utf8_stdout()

    since = (args.since or VALIDATION_CAMPAIGN.get("start_date", "2026-07-05"))
    if len(since) == 10:
        since += " 00:00:00"

    res = run(since, args.trials, args.seed)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    if res.get("error"):
        print("오류: %s" % res["error"])
        return
    print("=" * 66)
    print("무작위 진입 대조 — 방향 선택의 기여분 격리")
    print("=" * 66)
    print("표본: 진입 %d건 중 %d건 시뮬 가능 / %d거래일 (%s 이후)"
          % (res["n_entries"], res["n_usable"], res["n_days"], since[:10]))
    print()
    print("  실제 방향   : %+.2fpt   승률 %.1f%%"
          % (res["actual_pt"], res["actual_win_rate"] * 100))
    print("  무작위 %d회 : 중앙 %+.2fpt   5~95%% [%+.2f, %+.2f]   평균승률 %.1f%%"
          % (res["trials"], res["random_median_pt"], res["random_p05_pt"],
             res["random_p95_pt"], res["random_mean_win_rate"] * 100))
    print()
    print("  실제가 무작위를 상회한 비율 %.1f%%  →  단측 p = %.3f"
          % (res["beats_random_share"] * 100, res["p_one_sided"]))
    print("  일자단위: %d/%d일에서 그날 무작위 중앙값 상회"
          % (res["days_beating_random"], res["days_evaluated"]))
    print()
    print("※ 절대 수준은 인용 금지 — 단순화 시뮬(트레일링·틱청산·계단화·비용 없음).")
    print("  유효한 것은 두 팔의 비교뿐이며, 같은 시뮬이라 그 비교는 공정하다.")


if __name__ == "__main__":
    main()
