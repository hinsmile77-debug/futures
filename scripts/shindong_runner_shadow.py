# -*- coding: utf-8 -*-
"""[MW0601 629차] 신동 조건부 러너 섀도 — 백필 · 채점 · 사전등록 판정.

장후 마감(`main.py:daily_close`)이 매일 한 번 기록한다. 이 스크립트는
① 마감이 건너뛰어진 날을 채우고(`--backfill`) ② 누적 채점과 판정을 보인다.

사전등록: `docs/신동거래/조건부러너_섀도_사전등록_20260924.md`
⚠ 채점 시작(2026-09-28) 이전 백필 행은 **복기 전용**이다 — 판정 표본에 넣지 않는다.

사용:
    python scripts/shindong_runner_shadow.py                       # 채점 + 판정
    python scripts/shindong_runner_shadow.py --backfill 2026-09-28 2026-09-29
    python scripts/shindong_runner_shadow.py --backfill --from 2026-09-28 --to 2026-10-02
    python scripts/shindong_runner_shadow.py --out docs/신동거래/러너섀도_채점_20261023.md
"""
import argparse
import datetime as _dt
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.settings import (PREMARKET_LEVELS_DB, RAW_DATA_DB, SHINDONG_DB,  # noqa: E402
                             TRADES_DB, WEEKLY_OPTION_FLOW_DB)
from strategy.shindong import mireuk_runner as R  # noqa: E402


def _flow_db():
    return WEEKLY_OPTION_FLOW_DB if os.path.isabs(WEEKLY_OPTION_FLOW_DB) \
        else os.path.join(ROOT, WEEKLY_OPTION_FLOW_DB)


def _dates(args):
    if args.dates:
        return list(args.dates)
    d0 = _dt.date.fromisoformat(args.date_from)
    d1 = _dt.date.fromisoformat(args.date_to)
    out = []
    while d0 <= d1:
        if d0.weekday() < 5:
            out.append(d0.isoformat())
        d0 += _dt.timedelta(days=1)
    return out


def _won(x):
    return format(float(x), "+,.0f")


def report(until=None):
    v = R.verdict(SHINDONG_DB, until=until)
    L = ["# 신동 조건부 러너 섀도 채점 (`%s`, CREON 편도 %.4f%%)" % (
        R.RUNNER_VERSION, R.COMMISSION_RATE * 100), ""]
    if v["status"] == "NO_DB":
        L.append("`shindong.db` 없음 — 미배선(0건이 아니다)")
        return "\n".join(L), v
    L += ["| 항목 | 값 |", "|---|---|",
          "| 판정 | **%s** |" % v["status"],
          "| 흐름 측정일(채점 시작 %s 이후) | %d / %d |" % (R.SCORING_START, v["flow_days"],
                                                     R.JUDGE_AFTER_FLOW_DAYS),
          "| 판정 창 포지션 | %d (러너 적용 %d, 최소 %d) |" % (v["positions"], v["applied"],
                                                       R.MIN_APPLIED),
          "| 실제 → 섀도 | %s → %s원 |" % (_won(v["act_krw"]), _won(v["shadow_krw"])),
          "| ① 누적 차이 > 0 | %s원 %s |" % (_won(v["diff_krw"]), "✅" if v["c1_total_pos"] else "❌"),
          "| ② 상위 %d일 제외 차이 ≥ 0 | %s원 %s |" % (R.EXCLUDE_TOP_DAYS, _won(v["diff_ex_top_krw"]),
                                                "✅" if v["c2_ex_top_nonneg"] else "❌"),
          "| ③ 최악일 악화 ≤ %s원 | 실제 %s / 섀도 %s %s |" % (
              format(v["worst_tol"], ",.0f"), _won(v["worst_day_act"]),
              _won(v["worst_day_shadow"]), "✅" if v["c3_worst_ok"] else "❌"), ""]
    if v["status"] == "WAITING":
        L.append("⚠ 판정 전이다 — 위 ①–③ 은 **중간 집계**이며 판정이 아니다.")
    elif v["status"] == "INSUFFICIENT":
        L.append("⚠ 러너 적용 표본 부족 — 「판정 불가」다. 통과가 아니다.")
    L.append("")
    # [629차 후속] 진입 필터 B — 신동이 같은 방향으로 보유 중일 때만 진입, 청산은 미륵이 그대로
    b = R.verdict_filter_b(SHINDONG_DB, until=until)
    L += ["## 진입 필터 B (`%s`) — 신동 동방향 보유 중일 때만 진입 · 청산은 미륵이 그대로" % (
        R.FILTER_VERSION), "",
          "| 항목 | 값 |", "|---|---|",
          "| 판정 | **%s** |" % b["status"],
          "| 판정 창 포지션 | %d (측정 %d · 통과 %d · **제외 %d**, 최소 제외 %d) |" % (
              b["positions"], b["measured"], b["passed"], b["excluded"], R.FILTER_MIN_EXCLUDED),
          "| 실제 → 필터 B | %s → %s원 |" % (_won(b["act_krw"]), _won(b["alt_krw"])),
          "| ① 누적 차이 > 0 | %s원 %s |" % (_won(b["diff_krw"]), "✅" if b["c1_total_pos"] else "❌"),
          "| ② 상위 %d일 제외 차이 ≥ 0 | %s원 %s |" % (R.EXCLUDE_TOP_DAYS, _won(b["diff_ex_top_krw"]),
                                                "✅" if b["c2_ex_top_nonneg"] else "❌"),
          "| ③ 최악일 악화 ≤ %s원 | 실제 %s / 필터 %s %s |" % (
              format(b["worst_tol"], ",.0f"), _won(b["worst_day_act"]),
              _won(b["worst_day_alt"]), "✅" if b["c3_worst_ok"] else "❌"), ""]
    if b["status"] == "WAITING":
        L.append("⚠ 판정 전이다 — 위 ①–③ 은 **중간 집계**이며 판정이 아니다.")
    elif b["status"] == "INSUFFICIENT":
        L.append("⚠ 필터가 걸러낸 포지션이 적다 — 「판정 불가」다. 통과가 아니다.")
    L.append("")
    # 전 기록(복기 포함) 일별
    con = R.connect(SHINDONG_DB)
    try:
        rows = [dict(r) for r in con.execute(
            "SELECT * FROM shindong_mireuk_runner WHERE runner_version=? ORDER BY entry_ts",
            (R.RUNNER_VERSION,))]
    finally:
        con.close()
    by = defaultdict(list)
    for r in rows:
        by[r["trade_date"]].append(r)
    L += ["## 일별 (채점 시작 전 = 복기 전용)", "",
          "| 날짜 | 구분 | 신동방향 | 포지션 | 적용 | 실제 | 러너 섀도 | 차이 | 필터B 통과/제외 | 필터B | 미적용 사유 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for d in sorted(by):
        rs = by[d]
        bias = rs[0]["sd_bias"]
        reasons = defaultdict(int)
        for r in rs:
            if not r["applied"]:
                reasons[r["skip_reason"]] += 1
        bm = [r for r in rs if r.get("filt_b_pass") is not None]
        L.append("| %s | %s | %s | %d | %d | %s | %s | %s | %s | %s | %s |" % (
            d, "채점" if d >= R.SCORING_START else "복기",
            {None: "미측정", -1: "하방", 0: "보류", 1: "상방"}.get(bias, "?"), len(rs),
            sum(r["applied"] for r in rs), _won(sum(r["act_net_krw"] for r in rs)),
            _won(sum(r["shadow_net_krw"] for r in rs)), _won(sum(r["diff_krw"] for r in rs)),
            ("%d/%d" % (sum(r["filt_b_pass"] for r in bm), len(bm) - sum(r["filt_b_pass"] for r in bm)))
            if bm else "미측정",
            _won(sum(r["filt_b_net_krw"] for r in bm)) if bm else "-",
            " · ".join("%s %d" % kv for kv in sorted(reasons.items())) or "-"))
    return "\n".join(L), v


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("dates", nargs="*")
    ap.add_argument("--from", dest="date_from")
    ap.add_argument("--to", dest="date_to")
    ap.add_argument("--until", help="판정 기준일(기본: 전체)")
    ap.add_argument("--out", help="채점 결과를 .md 로 저장")
    args = ap.parse_args(argv)
    if args.backfill:
        if not args.dates and not (args.date_from and args.date_to):
            ap.error("--backfill 은 날짜 또는 --from/--to 가 필요하다")
        for d in _dates(args):
            res = R.run_for_date(d, TRADES_DB, RAW_DATA_DB, _flow_db(), PREMARKET_LEVELS_DB,
                                 SHINDONG_DB, source="backfill")
            print("%s  포지션 %d(보유중 제외 %d) · 적용 %d · 신동방향 %s · 실제 %s → 섀도 %s" % (
                d, res["n"], res["n_open_skipped"], res["applied"],
                {None: "미측정", -1: "하방", 0: "보류", 1: "상방"}.get(res["bias"], "?"),
                _won(res["act"]), _won(res["shadow"])))
    text, _v = report(until=args.until)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
