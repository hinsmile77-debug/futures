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

별도 축 — PHANTOM(유령):
  DEAD/CRITICAL이면서 **가용성 게이트가 켜져 있는** 피처. "수집 실패라 0"이 아니라
  "수집 성공이라 보고하면서 0"이라는 모순이며, 원천에 없는 필드를 스키마 폴백이
  채워낸 경우가 전형이다(451차 program_* 사고). 아래 gate_for() 주석 참조.

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
    "program_institution_net_krw": "원천 TR(CpSvr8111) 미제공 — 451차 폐기 집행. 과거 행 잔재",
    "program_individual_net_krw":  "원천 TR(CpSvr8111) 미제공 — 451차 폐기 집행. 과거 행 잔재",
    "program_foreign_net_krw":     "전체 프로그램 순매수 오라벨 — 451차 폐기 집행. 과거 행 잔재",
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


# ── 유령(PHANTOM) 피처 검출 ──────────────────────────────────────────────
#
# 왜 등급만으로는 부족한가 — 2026-08-09(451차) 사고:
#   `program_individual_net_krw` / `program_institution_net_krw`는 원천 TR
#   (`Dscbo1.CpSvr8111`)에 아예 없는 필드인데, 소비 계층의 `.get(key, 0)` 스키마
#   폴백이 상수 0을 매분 emit하면서 **동시에**
#   `quality_investor_program_supported = 1`을 보고했다. 바깥에서 보면
#   "수집 성공 + 값 0"이라 조용한 장세와 구분되지 않아 2개월 넘게 방치됐다.
#
# 이 표의 DEAD/CRITICAL 등급만으로는 그 둘을 못 가른다. 진짜 신호는 **모순**이다:
#   "가용하다고 보고하는 게이트가 켜져 있는데 정작 값이 상수다."
# 그 조합을 PHANTOM으로 따로 뽑아 KNOWN 등재 이전에 자동으로 드러낸다.
#
# 반대로 게이트가 꺼져 있는데 값이 0인 것은 **정직한 미수집**이다(예: 2026-08-04
# `opt_available=0` + `opt_pcr_*=0`). 그건 여기서 경보하지 않는다 — 원인이 이미
# 게이트에 정확히 표시돼 있기 때문이다.
_GATE_EXACT = {
    "foreign_futures_net":         "quality_investor_futures_supported",
    "retail_futures_net":          "quality_investor_futures_supported",
    "institution_futures_net":     "quality_investor_futures_supported",
    "foreign_retail_divergence":   "quality_investor_futures_supported",
    "foreign_call_net":            "quality_investor_option_supported",
    "foreign_put_net":             "quality_investor_option_supported",
}
# ⚠ 옵션은 게이트가 둘이고 출처가 다르다 — 섞으면 오검출한다.
#   `opt_pcr_*`  ← PCRStore(투자자 콜/풋 순매수)      게이트 `opt_available`
#   그 외 opt_*  ← OptionChainSnapshot(옵션체인 OI)  게이트 `opt_chain_available`
_GATE_PREFIX = (
    ("program_",     "quality_investor_program_supported"),
    ("opt_pcr_",     "opt_available"),
    ("opt_",         "opt_chain_available"),
    ("macro_",       "quality_macro_available"),
)

# 게이트가 이 비율 이상 켜져 있었으면 "가용하다고 보고했다"로 본다.
GATE_ON_MIN = 0.50


def gate_for(name):
    """이 피처의 가용성을 주장하는 품질 플래그 이름 (없으면 None)."""
    if name in _GATE_EXACT:
        return _GATE_EXACT[name]
    for prefix, gate in _GATE_PREFIX:
        if name.startswith(prefix):
            return gate
    return None


def gate_on_rate(rows, feature, gate):
    """`feature`가 존재하는 행에 한정해, 게이트가 켜져(≥0.5) 있던 비중.

    공존 행이 MIN_SAMPLES 미만이면 판정하지 않는다(None) — 소표본에서 우연히
    맞아떨어진 모순으로 경보를 내면 이 검출기 자체가 신뢰를 잃는다.
    """
    paired = [r[gate] for r in rows if feature in r and gate in r]
    if len(paired) < MIN_SAMPLES:
        return None
    return sum(1 for x in paired if x >= 0.5) / float(len(paired))


def collect(days):
    """행 단위 리스트를 반환한다.

    [451차] 이전에는 키별 값 리스트만 모았는데, 그러면 **행 정렬이 깨진다**. 실제로
    `macro_vix_abs` 같은 백필 전용 키는 7,533행 중 710행에만 존재하는데, 게이트
    비중을 전체 7,533행에서 재면 "게이트는 87% 켜졌는데 값은 상수"라는 가짜 모순이
    만들어져 유령으로 오검출된다. 게이트는 반드시 **그 피처가 존재하는 행에서만**
    재야 한다.
    """
    con = sqlite3.connect(RAW_DB)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT substr(ts,1,10) d FROM raw_features ORDER BY d DESC LIMIT ?", (days,))
    dates = sorted(r[0] for r in cur.fetchall())
    if not dates:
        return [], 0, None, None
    cur.execute("SELECT features FROM raw_features WHERE substr(ts,1,10) >= ?", (dates[0],))
    rows = []
    for (fj,) in cur.fetchall():
        try:
            f = json.loads(fj)
        except Exception:
            continue
        row = {}
        for k, v in f.items():
            if isinstance(v, bool):
                v = 1.0 if v else 0.0
            if isinstance(v, (int, float)):
                row[k] = float(v)
        rows.append(row)
    con.close()
    return rows, len(rows), dates[0], dates[-1]


def series_of(rows, key):
    return [r[key] for r in rows if key in r]


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

    data_rows, n_rows, d_from, d_to = collect(args.days)
    if not data_rows:
        print("raw_features 데이터 없음")
        return 1

    all_keys = set()
    for r in data_rows:
        all_keys.update(r.keys())

    print("피처 건강도 리포트 — %s ~ %s (%d행, %d개 피처)"
          % (d_from, d_to, n_rows, len(all_keys)))
    print("판정: DEAD=분산0 / CRITICAL=zero·최빈 95%+ / WARN=80%+ / OK=그 외")

    report = {}
    for k in all_keys:
        v = series_of(data_rows, k)
        if len(v) < MIN_SAMPLES:
            continue
        report[k] = classify(v)

    # 유령 판정 — "가용하다고 보고했는데 값이 상수"인 모순 조합
    for k, r in report.items():
        r["gate"] = None
        r["gate_on_rate"] = None
        r["phantom"] = False
        if is_benign_flag(k) or r["level"] not in (DEAD_LEVEL, CRIT_LEVEL):
            continue
        gate = gate_for(k)
        if not gate or gate == k:
            continue
        rate = gate_on_rate(data_rows, k, gate)
        if rate is None:
            continue
        r["gate"] = gate
        r["gate_on_rate"] = rate
        r["phantom"] = rate >= GATE_ON_MIN

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
        if r.get("phantom"):
            note = ("유령? " + note).strip()
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

    # ── 유령 피처 ──────────────────────────────────────────────
    phantoms = [(k, r) for k, r in rows if r.get("phantom")]
    print()
    if phantoms:
        new_phantoms = [k for k, _ in phantoms if k not in KNOWN]
        print("🔴 유령 피처 %d개 — '가용' 보고와 상수값이 모순 (신규 %d개)"
              % (len(phantoms), len(new_phantoms)))
        print("   원천이 실제로 그 필드를 주는지 먼저 확인할 것. 스키마 폴백"
              "(.get(key, 0))이 상수를 만들어내고 있을 가능성이 높다.")
        for k, r in phantoms:
            print("   - %-28s %s=%.0f%% 켜짐인데 %s (고유값 %d, 최빈 %.1f%%)%s"
                  % (k, r["gate"], 100.0 * r["gate_on_rate"], r["level"],
                     r["distinct"], 100.0 * r["mode_rate"],
                     "  [기록됨: %s]" % KNOWN[k] if k in KNOWN else ""))
    else:
        print("유령 피처 없음 (가용 보고와 상수값이 모순되는 조합 없음)")

    # ── KNOWN 목록 부패 점검 ────────────────────────────────────
    # 원인이 해소됐는데 KNOWN에 남아 있으면, 그 항목이 앞으로의 진짜 이상을 조용히
    # 삼킨다. 451차처럼 폐기를 집행하면 해당 피처는 표에서 사라지므로 정리 시점을
    # 여기서 알려준다.
    stale_known = [k for k in KNOWN if k not in report]
    # OK만 '해소'로 본다 — WARN은 여전히 점질량 의심 구간이라, 이걸 정리 대상으로
    # 올리면 아직 살아 있는 문제(cvd 포화 등)의 기록을 지우게 된다.
    resolved_known = [k for k in KNOWN
                      if k in report and report[k]["level"] == OK_LEVEL]
    if stale_known or resolved_known:
        print()
        if stale_known:
            print("ℹ KNOWN 정리 가능(데이터에 없음, 폐기·표본미달): %s"
                  % ", ".join(sorted(stale_known)))
        if resolved_known:
            print("ℹ KNOWN 정리 가능(등급 해소됨): %s" % ", ".join(sorted(resolved_known)))

    if args.json:
        with open(args.json, "w") as fp:
            json.dump({"from": d_from, "to": d_to, "rows": n_rows, "features": report},
                      fp, indent=2)
        print("JSON 저장: %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
