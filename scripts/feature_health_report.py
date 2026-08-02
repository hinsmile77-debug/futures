# -*- coding: utf-8 -*-
"""피처 건강도 리포트 — 죽은 피처(상수·영값 고착) 상시 감시.

왜 필요한가: 소진 6종·macro_nasdaq_chg 등이 **2개월 넘게 값이 전부 0인 채로**
방치됐고, 아무도 알아채지 못했다(Phase 0에서 발견). 원인은 제각각이었지만 공통점은
"조용히 죽어도 아무 신호가 없었다"는 것이다. 이 스크립트는 그 부류의 결함이 다시
장기 방치되지 않도록 zero-rate·상수화·점질량을 일괄 점검한다.

판정 등급:
  DEAD     — 전 구간 동일값(분산 0). 사실상 죽은 피처.
  CRITICAL — zero-rate ≥ 95% 또는 최빈값 비중 ≥ 95%. 거의 정보 없음.
  WARN     — zero-rate ≥ 80% 또는 최빈값 비중 ≥ 80%. 점질량 의심.
  OK       — 그 외.

읽기 전용 — raw_data.db(raw_features)만 SELECT 한다.

실행:
  python scripts/feature_health_report.py                 # 최근 20거래일
  python scripts/feature_health_report.py --days 60 --all # 전 피처 출력
  python scripts/feature_health_report.py --json out.json # 기계판독용
"""
from __future__ import print_function

import argparse
import json
import os
import sqlite3
import sys
from collections import Counter, defaultdict

# [MW0601 410차] Windows 기본 콘솔(cp949)에서 리포트 본문의 '—'(U+2014) 출력이
# UnicodeEncodeError로 죽어 이 도구를 수동 실행할 수 없던 결함 수정. 리다이렉트
# 없이도 돌아가야 한다 — 다른 리포트 스크립트들과 동일한 가드.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

DEAD_LEVEL = "DEAD"
CRIT_LEVEL = "CRITICAL"
WARN_LEVEL = "WARN"
OK_LEVEL = "OK"

CRIT_RATE = 0.95
WARN_RATE = 0.80
MIN_SAMPLES = 200

# 이미 원인이 규명돼 별도 관리 중인 피처 — 리포트에는 남기되 사유를 병기한다.
KNOWN = {
    "program_institution_net_krw": "원천 TR(CpSvr8111) 미제공 — 복구불가, 폐기예정(Phase 0 §2-4)",
    "program_individual_net_krw":  "원천 TR(CpSvr8111) 미제공 — 복구불가, 폐기예정(Phase 0 §2-4)",
    "macro_event_flag":            "EVENT_DATES 빈 dict — 캘린더 미입력(Phase 0 §2-3)",
    "bear_exhaustion":             "394차 섀도 복구 중 — EXHAUSTION_RESTORE_MODE 참조",
    "bull_exhaustion":             "394차 섀도 복구 중 — EXHAUSTION_RESTORE_MODE 참조",
    "bear_exhaustion_signal":      "394차 섀도 복구 중",
    "bull_exhaustion_signal":      "394차 섀도 복구 중",
    "cvd_exhaustion":              "bear_exhaustion 별칭(deprecated)",
    "cvd_exhaustion_signal":       "bear_exhaustion_signal 별칭(deprecated)",
    "cvd":                         "CVD 포화(+1.0 고착) — buy_vol 편향 파생, 미해결 등록",
    "cvd_direction":               "CVD 포화 파생 — 미해결 등록",
}

# 상태·품질 플래그는 "거의 항상 같은 값"이 오히려 정상이다(예: quality_*_available=1,
# is_monthly_witching=0). 이들까지 경보로 올리면 경보 피로로 진짜 이상이 묻히므로
# 별도 분류한다 — 표에는 그대로 나오되 "신규 이상" 목록에서는 제외한다.
_BENIGN_PREFIX = ("quality_", "macro_quality_", "opt_available", "opt_chain_available",
                  "is_", "hurst_ready", "basis_ready", "vkospi_ready",
                  "rv_iv_spread_ready", "feature_degraded", "entry_ok")


def is_benign_flag(name):
    return name.startswith(_BENIGN_PREFIX)


def collect(days):
    con = sqlite3.connect(RAW_DB)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT substr(ts,1,10) d FROM raw_features ORDER BY d DESC LIMIT ?", (days,))
    dates = sorted(r[0] for r in cur.fetchall())
    if not dates:
        return {}, 0, None, None
    cur.execute("SELECT features FROM raw_features WHERE substr(ts,1,10) >= ?", (dates[0],))
    vals = defaultdict(list)
    n = 0
    for (fj,) in cur.fetchall():
        try:
            f = json.loads(fj)
        except Exception:
            continue
        n += 1
        for k, v in f.items():
            if isinstance(v, bool):
                v = 1.0 if v else 0.0
            if isinstance(v, (int, float)):
                vals[k].append(float(v))
    con.close()
    return vals, n, dates[0], dates[-1]


def classify(v):
    n = len(v)
    zero = sum(1 for x in v if x == 0.0) / float(n)
    c = Counter(round(x, 6) for x in v)
    mode_val, mode_cnt = c.most_common(1)[0]
    mode_rate = mode_cnt / float(n)
    if len(c) == 1:
        level = DEAD_LEVEL
    elif zero >= CRIT_RATE or mode_rate >= CRIT_RATE:
        level = CRIT_LEVEL
    elif zero >= WARN_RATE or mode_rate >= WARN_RATE:
        level = WARN_LEVEL
    else:
        level = OK_LEVEL
    return {
        "n": n, "zero_rate": zero, "mode_value": mode_val,
        "mode_rate": mode_rate, "distinct": len(c), "level": level,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=20)
    ap.add_argument("--all", action="store_true", help="OK 등급도 전부 출력")
    ap.add_argument("--json", default="", help="결과를 JSON으로 저장할 경로")
    args = ap.parse_args()

    if not os.path.exists(RAW_DB):
        print("raw_data.db 없음: %s" % RAW_DB)
        return 1

    vals, n_rows, d_from, d_to = collect(args.days)
    if not vals:
        print("raw_features 데이터 없음")
        return 1

    print("피처 건강도 리포트 — %s ~ %s (%d행, %d개 피처)"
          % (d_from, d_to, n_rows, len(vals)))
    print("판정: DEAD=분산0 / CRITICAL=zero·최빈 95%+ / WARN=80%+ / OK=그 외")

    report = {}
    for k, v in vals.items():
        if len(v) < MIN_SAMPLES:
            continue
        report[k] = classify(v)

    order = {DEAD_LEVEL: 0, CRIT_LEVEL: 1, WARN_LEVEL: 2, OK_LEVEL: 3}
    rows = sorted(report.items(), key=lambda kv: (order[kv[1]["level"]], -kv[1]["mode_rate"]))

    counts = Counter(r["level"] for r in report.values())
    print()
    print("요약: DEAD=%d  CRITICAL=%d  WARN=%d  OK=%d"
          % (counts[DEAD_LEVEL], counts[CRIT_LEVEL], counts[WARN_LEVEL], counts[OK_LEVEL]))
    print()
    print("  %-9s %-30s %8s %8s %9s %8s  %s"
          % ("등급", "피처", "n", "zero%", "최빈비중", "고유값", "비고"))
    shown = 0
    for k, r in rows:
        if r["level"] == OK_LEVEL and not args.all:
            continue
        shown += 1
        note = KNOWN.get(k) or ("상태플래그(상수 정상)" if is_benign_flag(k) else "")
        print("  %-9s %-30s %8d %7.1f%% %8.1f%% %8d  %s"
              % (r["level"], k, r["n"], 100.0 * r["zero_rate"], 100.0 * r["mode_rate"],
                 r["distinct"], note))
    if not shown:
        print("  (해당 없음 — 모든 피처 OK)")

    unknown_bad = [k for k, r in rows
                   if r["level"] in (DEAD_LEVEL, CRIT_LEVEL)
                   and k not in KNOWN and not is_benign_flag(k)]
    print()
    if unknown_bad:
        print("!! 신규 이상 피처 %d개 — 원인 조사 필요: %s"
              % (len(unknown_bad), ", ".join(unknown_bad)))
    else:
        print("신규 이상 피처 없음 (DEAD/CRITICAL은 전부 원인 규명·관리 중이거나 상태플래그)")

    if args.json:
        with open(args.json, "w") as fp:
            json.dump({"from": d_from, "to": d_to, "rows": n_rows, "features": report},
                      fp, indent=2)
        print("JSON 저장: %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
