# scripts/bar_stop_path_watch.py
"""[MW0602 435차, 캠페인 48] 봉중 하드스톱 경로 건전성 — 읽기 전용. **시뮬레이터 무관.**

무엇을 묻는가
--------------
청산 체결가 산정이 **경로에 따라 편향돼 있는가.**

432차 후속2 실측(`exit_fill_slippage` 68건, 07-27~08-05):

    경로                 n   합계pt    평균     유리비율   부호검정 p
    봉중 하드스톱        13  -24.51  -1.885    13/13     0.00024
    틱 하드스톱          42   +2.12  +0.050    17/42     0.280
    목표(TP1/TP2/기타)   13   -0.38  -0.029     7/13     1.000
    (음수 = 유리)  봉중 vs 틱 Mann-Whitney p < 1e-6

**틱 경로는 대칭이고(정직) 봉중 경로만 전건 유리하다.**

메커니즘 — 두 겹이다 (main.py:12278 부근)
------------------------------------------
    _effective_stop = stop_price if _close_stop_hit else _prev_stop_price
    exit_price = min(_effective_stop, bar_high)     # SHORT
    price_hint = exit_price ; hint_source = "stop_intrabar"  → 시장가 주문

  (a) **계측**: `price_hint`가 봉 고저가에서 유도한 **허구의 스톱가**다. 주문은
      시장가로 나가므로 손익은 hint와 무관한데, 슬리피지 지표만 오염된다.
  (b) **발동조건**: 유령 하드스톱은 "그 봉의 극값이 스톱 조임보다 **먼저** 발생"할
      때 생기고, 스톱 조임은 TP1 도달이 전제다 → **이익 중인 포지션에서만 발동**한다.
      그래서 유리 편향이 선택효과가 아니라 **결정론적**으로 나온다.

실례(08-04 12:04): 12:03:52 진입 SHORT@976.50 → 12:04:26 TP1로 보호스톱 976.50(본전)
→ 12:04:52 봉마감 점검이 `bar_high ≥ 976.50`으로 히트 판정(그 고가는 12:04:26
**이전**에 발생) → 12:04:53 시장가 973.12 체결 **+3.38pt**. 보호스톱이 본전이라
정상이면 0.00pt여야 하고, 기록된 이익은 유리 체결분과 소수점까지 일치한다.

⚠ 손익 영향은 작다 — 이 채널은 손익이 아니라 **경로 건전성**을 본다
-------------------------------------------------------------------
1분봉 반사실 재생 결과 유령의 순기여는 9건 통산 **≈+3.0pt**뿐이다
(08-04 유령 4건 +3.36 / 08-05 억제 5건은 **억제가 오히려 +0.38pt 유리**).
→ **"424차 억제가 흑자를 없앤다"는 우려는 반증됐다.** 억제는 옳고 손익은 중립이다.

판정 (사전등록: config/settings.py VALIDATION_CAMPAIGN["bar_stop_path_watch"])
------------------------------------------------------------------------------
  PASS : 봉중 경로 유리비율이 `fav_rate_band` 안 (틱 경로처럼 대칭)
  FAIL : 밴드 밖 **그리고** 부호검정 p < `sign_test_alpha`
         → 체결가 산정이 시장을 반영하지 않는다 = (a) 계측 결함 잔존
  INSUFFICIENT : 표본 미달

⚠ **사전등록 정직성 고지**
--------------------------
첫 관측치(봉중 13/13, p=0.00024)는 이 채널 신설 **전에** 이미 봤다(432차 후속2).
[25]의 `breakeven` 변형과 같은 취급 — **재확인용이지 사전등록된 검증이 아니다.**
이 채널의 사전등록 가치는 **424차 억제 배포 후의 회복 판정**에 있다
(억제 후 표본은 08-05 단 1건이라 지금은 판정 불가).

⚠ 판정 모집단 — `hint_source` 태깅은 423차부터다
------------------------------------------------
그 이전 행은 NULL이라 `reason`으로 재분류한다(`하드스톱`=봉중 / `하드스톱(틱)`=틱).
재분류 건수를 별도로 노출하니 해석 시 감안할 것.

⚠ **`price_hint`를 지금 고치지 않는 이유** (435차 판단, 재론 시 근거 필요)
--------------------------------------------------------------------------
"봉중 hint가 허구니 전송 시점 현재가로 바꾸자"가 자연스러운 처방으로 보이지만
**지금은 하지 않는다.** 세 가지 이유다:

1. **§9 위반이 된다.** 이 채널이 사전등록으로 재려는 바로 그 지표를, 관측 직후
   정의만 바꿔 PASS로 만드는 꼴이다([25] 클램프와 다르다 — 그건 *체결 불가능한
   가격*을 계상하던 물리적 오류였고, 이건 *유효한 정의 선택*의 문제다).
2. **손익이 안 바뀐다.** 주문은 `_send_broker_exit_order()`의 **시장가**다
   (main.py:9209). hint는 주문에 전달되지 않는다 — 고쳐도 체결은 그대로다.
3. **순수 계측값이 아니다.** `price_hint`는 Chejan 콜백 유실 시 평균가 폴백으로도
   쓰인다(main.py:2823 `_flush_pending_exit_agg`). 드물지만 라이브 복구 경로라
   "계측 전용이니 안전하다"고 단정할 수 없다.

→ **진짜 처방은 424차 억제(발동 차단)이고 이미 배포됐다.** 이 채널은 그 억제가
   실제로 듣는지를 **부호 대칭성 회복**으로 검증한다. 억제 후에도 봉중이 편향돼
   있으면 그때 hint 정의를 손대고, 그 변경은 [25] 클램프처럼 **전/후 수치를 함께
   기록**해야 한다.

실행:
    py310_64\python.exe scripts/bar_stop_path_watch.py [--since 2026-07-05]
"""
from __future__ import annotations

import argparse
import math
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

_CR = VALIDATION_CAMPAIGN.get("bar_stop_path_watch", {})

BAR = "봉중 하드스톱"          # stop_intrabar — hint가 허구(봉 고저가 유도)
CLOSE = "종가 하드스톱"        # stop_close   — hint 유효(현재가가 실제로 스톱을 넘음)
TICK = "틱 하드스톱"           # stop_tick    — hint 유효(틱이 스톱을 넘음) = 대조군
TARGET = "목표(TP1/TP2/기타)"


def _path_of(hint_source, reason) -> tuple:
    """경로 분류. 반환 (경로, 재분류여부).

    `hint_source`가 있으면 그것이 정본. 없으면(423차 이전 행) `reason`으로 재분류한다.

    ⚠ **`stop_close`를 BAR와 분리한다** — 둘 다 봉 단위 점검에서 나오지만 hint의
    성질이 정반대다. 종가 히트는 "현재가가 실제로 스톱을 넘었다"라 hint가 유효하고,
    봉중 히트는 "그 봉 어딘가에서 넘었다"를 고저가로 유도한 값이라 **체결 시점에는
    존재하지 않던 가격**이다(main.py:12278 주석이 그 구분을 이미 명시한다).
    섞으면 판정이 희석된다. 현재 데이터에 `stop_close`는 0건이지만 구조로 갈라 둔다.
    """
    hs = (hint_source or "").strip()
    rs = (reason or "").strip()
    if hs == "stop_intrabar":
        return BAR, False
    if hs == "stop_close":
        return CLOSE, False
    if hs in ("stop_tick", "stop_tier1_qty1"):
        return TICK, False
    if hs:
        return TARGET, False
    # 태깅 이전 행(423차 이전) — reason으로 재분류.
    # ⚠ `하드스톱`(비틱)은 stop_close/stop_intrabar 둘 다일 수 있어 **구분 불가**다.
    #    보수적으로 BAR에 넣고 재분류 건수를 노출한다 — 해석 시 감안할 것.
    if rs == "하드스톱":
        return BAR, True
    if "틱" in rs:
        return TICK, True
    return TARGET, True


def _comb(n: int, k: int) -> int:
    """[439차 P3] `math.comb`는 Python 3.8+다 — py37_32에서 AttributeError로 죽는다.

    이 모듈은 py310_64 전용으로 쓰여 왔지만(모듈 docstring의 실행 예시),
    `_binom_two_sided`의 주석은 "scipy 없이도 돌게 직접 계산한다"라고 이식성을
    의도하고 있었다. 회귀 테스트를 2환경에서 돌리려면 이 한 겹이 필요하다.
    동작은 3.8+에서 `math.comb`와 완전히 동일하다(정수 정확 연산).
    """
    _c = getattr(math, "comb", None)
    if _c is not None:
        return _c(n, k)
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    num = 1
    for i in range(k):
        num = num * (n - i) // (i + 1)
    return num


def _binom_two_sided(k: int, n: int) -> float:
    """부호검정 p (정확 이항, 양측). scipy 없이도 돌게 직접 계산한다."""
    if n <= 0:
        return 1.0
    def pmf(i):
        return _comb(n, i) * 0.5 ** n
    obs = pmf(k)
    return min(1.0, sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs + 1e-15))


def compute(since: str = "2026-07-05") -> dict:
    with sqlite3.connect(TRADES_DB) as c:
        try:
            rows = c.execute(
                "SELECT ts, reason, hint_source, slippage_pts FROM exit_fill_slippage "
                "WHERE ts >= ? ORDER BY ts", (since,)).fetchall()
        except sqlite3.OperationalError as e:
            return {"error": str(e), "groups": {}}

    groups, reclass, days = {}, 0, {}
    by_day = {}          # {날짜: {경로: [slip, ...]}} — 발생 추이(439차 P3)
    all_days = set()
    for ts, reason, hs, sp in rows:
        path, was_re = _path_of(hs, reason)
        d = ts[:10]
        groups.setdefault(path, []).append(float(sp or 0.0))
        days.setdefault(path, set()).add(d)
        by_day.setdefault(d, {}).setdefault(path, []).append(float(sp or 0.0))
        all_days.add(d)
        if was_re:
            reclass += 1
    return {"since": since, "groups": groups, "n_reclassified": reclass,
            "days": {k: len(v) for k, v in days.items()},
            "by_day": by_day, "all_days": sorted(all_days),
            "n_total": len(rows), "error": None}


def _bar_guard_split(out: dict) -> dict:
    """[439차 P3] 봉중 표본을 **423차 가드 배포 경계**로 pre/post 분리 — 관찰 전용.

    왜: 이 채널은 스스로 "가치는 424차 억제 배포 후의 **회복 판정**에 있다"고 적어
    두고도 `start_date` 이후를 통째로 풀링해 판정한다. 실측하면 pre-guard가 과반이라
    n이 min_samples에 도달해도 그 판정은 "억제 후 회복"이 아니라 **혼합**이다.

    ⚠ **verdict를 바꾸지 않는다.** 사전등록 판정식은 그대로 두고(§9, 313차), 여기서는
    분해와 경고만 만든다 — 사후 데이터로 합격선을 움직이는 것이 313차 위반이기 때문.
    """
    gld = str(_CR.get("guard_live_date", "2026-08-04"))
    warn_at = float(_CR.get("pre_guard_contamination_warn", 0.50))
    by_day = out.get("by_day") or {}
    res = {"guard_live_date": gld, "bar_by_day": {}, "path_by_day": {}}

    pre_n = post_n = 0
    pre_days, post_days = set(), set()
    pre_tot = post_tot = 0.0
    for d in out.get("all_days", []):
        paths = by_day.get(d) or {}
        res["path_by_day"][d] = {k: len(v) for k, v in paths.items()}
        bar = paths.get(BAR) or []
        res["bar_by_day"][d] = len(bar)
        if not bar:
            continue
        if d < gld:
            pre_n += len(bar); pre_days.add(d); pre_tot += sum(bar)
        else:
            post_n += len(bar); post_days.add(d); post_tot += sum(bar)

    res["pre_guard"] = {"n": pre_n, "days": len(pre_days), "total": round(pre_tot, 4)}
    res["post_guard"] = {"n": post_n, "days": len(post_days), "total": round(post_tot, 4)}
    total = pre_n + post_n
    res["pre_guard_share"] = round(pre_n / total, 4) if total else 0.0
    res["prereg_contaminated"] = bool(total and res["pre_guard_share"] > warn_at)
    if res["prereg_contaminated"]:
        res["contamination_reason"] = (
            "봉중 표본 %d건 중 **%d건(%.1f%%)이 가드 배포 이전**(%s 이전)이다. "
            "이 채널이 재려는 것은 '억제 후 회복'인데 판정은 pre/post를 풀링해 "
            "계산되므로, n이 min_samples에 도달해도 그 판정은 회복 판정이 아니라 "
            "**혼합 판정**이다. 억제 후 표본은 %d건 / %d거래일뿐이다."
            % (total, pre_n, 100 * res["pre_guard_share"], gld,
               post_n, len(post_days)))
    # 최근 거래일 발생 추이 — "지금도 쌓이고 있는가"를 판정과 무관하게 보여 준다.
    # ⚠ 합계 하나로 내면 **가드 이전 날이 섞여 오독된다**(최근 5일 합 13건인데
    #    그중 8건이 08-03 = 가드 이전이다). 그래서 일자별 시퀀스로 낸다.
    recent = out.get("all_days", [])[-5:]
    res["recent_days"] = recent
    res["bar_recent_seq"] = [res["bar_by_day"].get(d, 0) for d in recent]
    # 마지막으로 봉중이 발생한 날 이후 무발생 거래일 수 — 가장 정직한 "고갈" 지표
    _since_last = 0
    for d in reversed(out.get("all_days", [])):
        if res["bar_by_day"].get(d, 0):
            break
        _since_last += 1
    res["bar_dry_days"] = _since_last
    return res


def summarize(out: dict) -> dict:
    if out.get("error"):
        return {"verdict": "INSUFFICIENT", "reason": "소스 없음 — %s" % out["error"],
                "no_data": True}
    g = out.get("groups") or {}
    stat = {}
    for k, v in g.items():
        if not v:
            continue
        fav = sum(1 for x in v if x < 0)       # 음수 = 유리
        stat[k] = {"n": len(v), "total": round(sum(v), 4),
                   "mean": round(statistics.mean(v), 4),
                   "median": round(statistics.median(v), 4),
                   "fav": fav, "fav_rate": fav / len(v),
                   "sign_p": round(_binom_two_sided(fav, len(v)), 6),
                   "days": out.get("days", {}).get(k, 0)}
    base = {"per_path": stat, "n_reclassified": out.get("n_reclassified", 0),
            "n_total": out.get("n_total", 0)}
    base.update(_bar_guard_split(out))

    b = stat.get(BAR)
    min_n = int(_CR.get("min_samples", 25))
    min_d = int(_CR.get("min_days", 8))
    if not b or b["n"] < min_n or b["days"] < min_d:
        base.update(verdict="INSUFFICIENT",
                    reason=("봉중 경로 표본 부족 (n=%s<%d 또는 거래일=%s<%d)"
                            % ((b or {}).get("n", 0), min_n,
                               (b or {}).get("days", 0), min_d)))
        return base

    lo, hi = _CR.get("fav_rate_band", [0.35, 0.65])
    alpha = float(_CR.get("sign_test_alpha", 0.01))
    out_of_band = not (float(lo) <= b["fav_rate"] <= float(hi))
    sig = b["sign_p"] < alpha
    t = stat.get(TICK) or {}
    if out_of_band and sig:
        base.update(verdict="FAIL",
                    reason=("봉중 경로 유리비율 %.0f%% (%d/%d, 부호검정 p=%.5f) — "
                            "밴드 [%.2f, %.2f] 밖. 대조군 틱 경로는 %.0f%% (%d/%d). "
                            "체결가 산정이 시장을 반영하지 않는다"
                            % (100 * b["fav_rate"], b["fav"], b["n"], b["sign_p"],
                               float(lo), float(hi),
                               100 * t.get("fav_rate", 0), t.get("fav", 0), t.get("n", 0))))
    else:
        base.update(verdict="PASS",
                    reason=("봉중 경로 유리비율 %.0f%% (%d/%d, p=%.3f) — 밴드 안 또는 미유의"
                            % (100 * b["fav_rate"], b["fav"], b["n"], b["sign_p"])))
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None)
    args = ap.parse_args()
    since = args.since or VALIDATION_CAMPAIGN.get("start_date", "2026-07-05")
    s = summarize(compute(since))

    print("=" * 92)
    print("[48] 봉중 하드스톱 경로 건전성   기간 %s~   (시뮬레이터 무관 · 라이브 실측)" % since)
    print("사전등록: config/settings.py VALIDATION_CAMPAIGN['bar_stop_path_watch']")
    print("=" * 92)
    if s.get("no_data"):
        print(s["reason"])
        return
    print("총 %d건 (그중 hint_source 미태깅 재분류 %d건 — 423차 이전 행)"
          % (s["n_total"], s["n_reclassified"]))
    print()
    print("%-20s %5s %9s %9s %10s %12s %7s"
          % ("경로", "n", "합계pt", "평균", "유리비율", "부호검정 p", "거래일"))
    print("-" * 82)
    for k in (BAR, CLOSE, TICK, TARGET):
        d = s["per_path"].get(k)
        if not d:
            print("%-20s (표본 없음)" % k)
            continue
        print("%-20s %5d %+9.2f %+9.3f %6d/%-3d %12.5f %7d"
              % (k, d["n"], d["total"], d["mean"], d["fav"], d["n"], d["sign_p"], d["days"]))
    print()
    print("(음수 = 유리) 판정: %s" % s["verdict"])
    print("사유: %s" % s["reason"])

    # ── [439차 P3] 발생 추이 + 가드 경계 pre/post 분해 ──────────────────────
    print()
    print("[발생 추이] 경로별 건수 (가드 배포 경계 %s)" % s.get("guard_live_date"))
    print("%-12s %6s %6s %6s   %s" % ("날짜", "봉중", "틱", "목표", ""))
    print("-" * 52)
    for d in sorted(s.get("path_by_day", {})):
        p = s["path_by_day"][d]
        mark = "  <- 가드 배포" if d == s.get("guard_live_date") else ""
        print("%-12s %6d %6d %6d %s"
              % (d, p.get(BAR, 0), p.get(TICK, 0), p.get(TARGET, 0), mark))
    pre, post = s.get("pre_guard", {}), s.get("post_guard", {})
    print()
    print("가드 이전 : n=%-3s %s거래일  합계 %+.2fpt"
          % (pre.get("n", 0), pre.get("days", 0), pre.get("total", 0.0)))
    print("가드 이후 : n=%-3s %s거래일  합계 %+.2fpt"
          % (post.get("n", 0), post.get("days", 0), post.get("total", 0.0)))
    print("최근 %d거래일 봉중 발생: %s   (마지막 발생 이후 무발생 %d거래일)"
          % (len(s.get("recent_days", [])),
             " / ".join(str(x) for x in s.get("bar_recent_seq", [])),
             s.get("bar_dry_days", 0)))
    if s.get("prereg_contaminated"):
        print()
        print("[!] 사전등록 오염 — %s" % s.get("contamination_reason", ""))
        print("    판정 시 pre/post를 반드시 분리해 읽을 것. 위 verdict는 풀링값이다.")

    print()
    print("⚠ 사전등록 정직성: 첫 관측치(봉중 13/13, p=0.00024)는 신설 전에 이미 봤다.")
    print("  재확인용이지 사전등록된 검증이 아니다 — 가치는 424차 억제 후 회복 판정에 있다.")
    print()
    print("⚠ **합계pt는 손익이 아니다** — `price_hint`가 봉 고저가에서 유도한 허구의")
    print("  스톱가라 주문(시장가)과 무관하고, 슬리피지 지표만 오염시킨다.")
    print("  봉중 -24.51pt를 원화로 환산해 '유리했다'고 읽으면 안 된다.")
    print("  실제 손익 기여 추정은 두 개가 있고 **서로 3배 이상 어긋난 채 미해결**이다:")
    print("    424차: 08-04 qty>=2 3건 실현 +8.76pt(+433,609원) vs 반사실 0pt")
    print("    435차: 1분봉 반사실 재생 9건 통산 ≈+3.0pt, 08-05 억제 5건은 억제가 +0.38pt 유리")
    print("  → 어느 쪽도 이 채널의 사전등록 판정이 아니다. 라이브 재판정 경로는")
    print("    [35-M] 미러 서브표본(439차)뿐이다.")


if __name__ == "__main__":
    main()
