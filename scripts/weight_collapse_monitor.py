# -*- coding: utf-8 -*-
"""[402차 후속] BAR_ONLY_RELAX 수용/롤백 판정 모니터 — 읽기 전용.

배경
----
401차가 `BAR_ONLY_RELAX_ENABLED`를 콜드스타트 30분 한정에서 **상시 적용·기본 True**로
확장했다(2026-07-29 장 마감 후 커밋 → 발효는 2026-07-30 세션부터). 이 변경은
Q3(2026-06-25)가 bar_only로 막으려던 "학습/추론 분포 불일치"를 상시 재도입하는
트레이드오프를 지므로, 효과와 부작용을 함께 봐야 한다.

그런데 `weight_collapsed`(398차 신설 컬럼)는 DB에 저장만 되고 **소비처가 하나도 없었다**
— 캠페인 채널도, 대시보드 패널도, EOD 요약도 없어서 확인하려면 매번 수동 SQL을 쳐야 했다.
이 스크립트가 그 공백을 메운다(주간 자동 판정은 `generate_validation_campaign_report.py`
[20] 채널이 담당 — 이 스크립트는 그보다 빠른 일 단위 확인용).

읽기 전용 — DB에 쓰지 않는다. 정책 적용/롤백은 사람이 결정한다(§2 사전등록 원칙).

기준선의 한계 (중요)
--------------------
`weight_collapsed`는 398차(2026-07-28 저녁 배포)부터 기록되므로 **완화 전 기준선은
2026-07-29 하루(44.8%)뿐**이다. 그 이전 날짜는 컬럼이 NULL이라 "collapse 0건"이
아니라 "미계측"이며, 이 스크립트는 NULL 일자를 집계에서 제외한다. 즉 기준선은
단일일 표본이므로, 완화 후 수치가 기준선과 조금 다르다고 해서 그것만으로 결론을
내면 안 된다(313차 원칙) — 그래서 판정에 `min_days`(기본 3거래일)를 둔다.

사용
----
    python scripts/weight_collapse_monitor.py
    python scripts/weight_collapse_monitor.py --days 14 --relax-date 2026-07-30
"""
from __future__ import print_function

import argparse
import datetime
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import PREDICTIONS_DB, TRADES_DB, VALIDATION_CAMPAIGN  # noqa: E402

# BAR_ONLY_RELAX 발효일 — 401차 커밋(2026-07-29 16:26, 장 마감 후)이라 다음 세션부터.
DEFAULT_RELAX_DATE = "2026-07-30"

_CFG = VALIDATION_CAMPAIGN.get("weight_collapse_watch", {})
BASELINE_RATIO = float(_CFG.get("baseline_ratio", 0.448))
TARGET_RATIO = float(_CFG.get("target_ratio", 0.20))
TARGET_TOL = float(_CFG.get("target_tolerance", 0.07))
INEFFECTIVE_MIN = float(_CFG.get("ineffective_ratio_min", 0.40))
OVERRELAX_MAX = float(_CFG.get("overrelax_ratio_max", 0.05))
HZ_ACC_FLOOR = dict(_CFG.get("hz_acc_floor", {"3m": 0.30, "5m": 0.28}))
REGRESSION_STREAK = int(_CFG.get("regression_streak_days", 3))
MIN_DAYS = int(_CFG.get("min_days", 3))


def _conn(path):
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c


def collect(days):
    """일자별 collapse 비율 / 호라이즌 적중률 / 진입 체결 건수."""
    since = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    rows = {}

    with _conn(PREDICTIONS_DB) as c:
        # weight_collapsed 가 NULL 인 날은 "미계측"이므로 제외한다 (collapse 0 아님)
        for r in c.execute(
            """SELECT substr(ts,1,10) d,
                      COUNT(*) n,
                      SUM(CASE WHEN weight_collapsed IS NULL THEN 1 ELSE 0 END) n_null,
                      SUM(COALESCE(weight_collapsed,0)) n_wc,
                      SUM(CASE WHEN grade <> 'X' THEN 1 ELSE 0 END) n_signal
                 FROM ensemble_decisions
                WHERE substr(ts,1,10) >= ?
                GROUP BY d ORDER BY d""", (since,)
        ):
            rows[r["d"]] = {
                "n": r["n"], "n_null": r["n_null"], "n_wc": r["n_wc"],
                "n_signal": r["n_signal"], "acc": {}, "entries": 0,
            }
        for r in c.execute(
            """SELECT substr(ts,1,10) d, horizon,
                      COUNT(*) n, AVG(CAST(correct AS FLOAT)) acc
                 FROM predictions
                WHERE substr(ts,1,10) >= ? AND correct IS NOT NULL
                  AND horizon IN ('3m','5m')
                GROUP BY d, horizon""", (since,)
        ):
            if r["d"] in rows:
                rows[r["d"]]["acc"][r["horizon"]] = (r["acc"], r["n"])

    with _conn(TRADES_DB) as c:
        for r in c.execute(
            """SELECT substr(entry_ts,1,10) d, COUNT(*) n
                 FROM trades WHERE substr(entry_ts,1,10) >= ?
                GROUP BY d""", (since,)
        ):
            if r["d"] in rows:
                rows[r["d"]]["entries"] = r["n"]
    return rows


def judge(rows, relax_date):
    """수용/롤백 판정. (verdict, 사유줄 리스트) 반환."""
    measured = {d: v for d, v in rows.items() if v["n"] and v["n_null"] < v["n"]}
    pre = {d: v for d, v in measured.items() if d < relax_date}
    post = {d: v for d, v in measured.items() if d >= relax_date}
    notes = []

    def ratio(v):
        n_meas = v["n"] - v["n_null"]
        return (float(v["n_wc"]) / n_meas) if n_meas else None

    if len(post) < MIN_DAYS:
        notes.append("완화 후 계측일 %d일 < 최소 %d일 — 판정 보류 (313차 원칙: 단일일 판정 금지)"
                     % (len(post), MIN_DAYS))
        return "INSUFFICIENT", notes, pre, post

    post_ratios = [ratio(v) for v in post.values() if ratio(v) is not None]
    mean_post = sum(post_ratios) / len(post_ratios)
    notes.append("완화 후 %d일 평균 collapse=%.1f%% (기준선 %.1f%%, 목표 %.1f%%±%.1f%%p)"
                 % (len(post_ratios), mean_post * 100, BASELINE_RATIO * 100,
                    TARGET_RATIO * 100, TARGET_TOL * 100))

    # ── 효과 판정 ──
    if mean_post >= INEFFECTIVE_MIN:
        effect = "INEFFECTIVE"
        notes.append("→ 완화가 듣지 않음(%.1f%% ≥ %.1f%%). 원인이 bar age가 아닐 가능성 —"
                     " 재조사 필요(롤백보다 원인 규명 우선)."
                     % (mean_post * 100, INEFFECTIVE_MIN * 100))
    elif mean_post <= OVERRELAX_MAX:
        effect = "OVER_RELAXED"
        notes.append("→ 예상 밖 과다완화(%.1f%% ≤ %.1f%%). 다른 경로가 함께 열렸는지 확인 필요."
                     % (mean_post * 100, OVERRELAX_MAX * 100))
    elif abs(mean_post - TARGET_RATIO) <= TARGET_TOL:
        effect = "ON_TARGET"
        notes.append("→ 목표 구간 진입 — 효과 지표는 수용 조건 충족.")
    else:
        effect = "OFF_TARGET"
        notes.append("→ 목표 구간을 벗어났으나 극단(미작동/과다완화)은 아님 — 관찰 계속.")

    # ── 회귀(부작용) 판정: Q3 학습/추론 분포 불일치 감시 ──
    regressed = []
    for hz, floor in sorted(HZ_ACC_FLOOR.items()):
        streak = 0
        worst = 0
        for d in sorted(post):
            a = post[d]["acc"].get(hz)
            if a is None:
                streak = 0
                continue
            if a[0] < floor:
                streak += 1
                worst = max(worst, streak)
            else:
                streak = 0
        if worst >= REGRESSION_STREAK:
            regressed.append("%s 적중률 %d거래일 연속 <%.0f%%" % (hz, worst, floor * 100))
    if regressed:
        notes.append("→ **회귀 감지**: " + " / ".join(regressed)
                     + " — Q3 분포 불일치 부작용 의심, 롤백 검토 대상.")

    if regressed:
        return "ROLLBACK_REVIEW", notes, pre, post
    if effect == "ON_TARGET":
        return "ACCEPT", notes, pre, post
    if effect == "INEFFECTIVE":
        return "INVESTIGATE", notes, pre, post
    return "OBSERVE", notes, pre, post


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=14, help="조회 창(일). 기본 14")
    ap.add_argument("--relax-date", default=DEFAULT_RELAX_DATE,
                    help="BAR_ONLY_RELAX 발효일(YYYY-MM-DD). 기본 %s" % DEFAULT_RELAX_DATE)
    args = ap.parse_args()

    rows = collect(args.days)
    if not rows:
        print("데이터 없음 (조회 창 %d일)" % args.days)
        return

    print("=" * 86)
    print("BAR_ONLY_RELAX 수용/롤백 모니터   (발효일 %s, 조회 %d일)" % (args.relax_date, args.days))
    print("=" * 86)
    print("%-12s %7s %7s %9s %10s %10s %7s  %s"
          % ("일자", "분봉수", "collapse", "collapse%", "3m적중", "5m적중", "진입", "구분"))
    for d in sorted(rows):
        v = rows[d]
        n_meas = v["n"] - v["n_null"]
        if n_meas <= 0:
            print("%-12s %7d %7s %9s %10s %10s %7d  %s"
                  % (d, v["n"], "—", "미계측", "—", "—", v["entries"], "(398차 배포 전)"))
            continue
        pct = 100.0 * v["n_wc"] / n_meas
        a3 = v["acc"].get("3m")
        a5 = v["acc"].get("5m")
        print("%-12s %7d %7d %8.1f%% %9s %10s %7d  %s"
              % (d, n_meas, v["n_wc"], pct,
                 ("%.1f%%(%d)" % (a3[0] * 100, a3[1])) if a3 else "—",
                 ("%.1f%%(%d)" % (a5[0] * 100, a5[1])) if a5 else "—",
                 v["entries"],
                 "완화후" if d >= args.relax_date else "완화전"))

    verdict, notes, pre, post = judge(rows, args.relax_date)
    print()
    print("-" * 86)
    print("판정: %s" % verdict)
    for n in notes:
        print("  - %s" % n)
    print("-" * 86)
    print("기준선 주의: weight_collapsed는 398차(2026-07-28 저녁) 배포분부터 기록되므로")
    print("  완화 전 계측일은 %d일뿐이다. '미계측' 행은 collapse 0건이 아니라 컬럼 NULL이다." % len(pre))
    print("롤백 방법: config/settings.py:BAR_ONLY_RELAX_ENABLED = False (1줄, 즉시 가역)")
    print("판정 기준 출처: config/settings.py:VALIDATION_CAMPAIGN['weight_collapse_watch']")
    print("  (사전등록 — 관측 후 기준을 고치면 검증이 무의미해진다. §2 사전등록 원칙)")


if __name__ == "__main__":
    main()
