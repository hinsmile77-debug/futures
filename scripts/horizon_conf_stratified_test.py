# -*- coding: utf-8 -*-
"""[MW0601 455차 / 07-30 실행계획 1단계 L4] 호라이즌별 conf-층화 z-test — 311차 후속5 방법론 코드화.

배경: 1m 퇴역 결정의 직접 근거였던 conf-층화 검정이 세션 스크래치패드 산출물로만 남아
매번 손으로 재작성해야 했다(07-30 실행계획 §2-3). 이 스크립트가 그 방법론을 그대로
고정한다 — **새 방법론을 발명하지 않는다.**

방법론(전부 관측 전 고정 — `VALIDATION_CAMPAIGN["horizon_direction_watch"]` 사전등록):
  · 표본: predictions에서 direction != 0 AND actual IS NOT NULL AND actual != 0 (방향성 표본만)
  · 적중: direction == actual (correct 열을 재신뢰하지 않고 직접 재계산 — 스키마 드리프트 방어)
  · 층화: confidence < 0.55 vs >= 0.55 (경계 0.55 — 311차 계승, 사후 변경 금지)
  · 검정: two-proportion z-test, Bonferroni(÷ 동시검정 호라이즌 수), α=0.05
  · 판정: 보정 후 유의+음 → ANTI_CALIBRATION / 비유의 → NO_SKILL / 유의+양 → OK /
          고conf n < 100 또는 유효일 < 10 → INSUFFICIENT
  · 부가: conf 버킷(0.50/0.55/0.60/0.65/0.70+) 단조성, dir_acc_floor(0.45) 미달 표시
          (floor 미달 자체는 경보 표시일 뿐 — 퇴역은 주간회의 수동 결정, 자동 조치 없음)

출력:
  ① stdout 표
  ② data/horizon_conf_stratified_latest.json — 08-02 피처셋 주기점검 계획의 "L4 입력 계약"
     스키마 그대로. `generate_featureset_health_report.py`가 이 파일을 읽어 L4 칸을 채운다
     (없으면 "⚠ 미배선" 표시 — 이 파일이 생기는 순간 자동 해소, 그쪽 코드는 무수정).

읽기 전용: predictions.db만 읽고 DB·모델·설정 어디에도 쓰지 않는다(JSON 출력 파일 제외).
실행: 주간 금요일 EOD 체인(campaign_steps.py, py310_64) + 수동. py37_32 호환 문법.
"""
from __future__ import print_function

import argparse
import datetime
import io
import json
import math
import os
import sqlite3
import sys

_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Windows 기본 콘솔(cp949)에서 U+2014 등으로 죽지 않게 — 410차 feature_health_report 선례
def _utf8_console():
    """cp949 콘솔 인코딩 가드 — CLI 실행 시에만 (import 시 래핑하면 중첩 래퍼로 출력 유실)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config.settings import PREDICTIONS_DB, VALIDATION_CAMPAIGN  # noqa: E402

_CFG = VALIDATION_CAMPAIGN.get("horizon_direction_watch", {})
HORIZONS = list(_CFG.get("horizons", ["3m", "5m", "10m", "15m"]))
CONF_EDGE = float(_CFG.get("conf_bucket_edge", 0.55))
MIN_HIGH_N = int(_CFG.get("min_samples_high_conf", 100))
MIN_DAYS = int(_CFG.get("min_days", 10))
ALPHA = float(_CFG.get("alpha", 0.05))
DIR_ACC_FLOOR = float(_CFG.get("dir_acc_floor", 0.45))

# conf 버킷 경계(단조성 관찰용 — 311차 후속5의 "5m식 단조하락 vs 30m식 tail만 튐" 구분)
BUCKET_EDGES = [0.50, 0.55, 0.60, 0.65, 0.70]

DEFAULT_OUT = os.path.join(_ROOT, "data", "horizon_conf_stratified_latest.json")


def norm_sf(z):
    """표준정규 생존함수 P(Z > z) — scipy 없이 (454차 MKL 크래시 회피 선례)."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def two_prop_z(x1, n1, x2, n2):
    """two-proportion z (p2 - p1 방향). 반환 (z, p_two_sided). 표본 0이면 (nan, nan)."""
    if n1 <= 0 or n2 <= 0:
        return float("nan"), float("nan")
    p1, p2 = x1 / float(n1), x2 / float(n2)
    pool = (x1 + x2) / float(n1 + n2)
    denom = pool * (1.0 - pool) * (1.0 / n1 + 1.0 / n2)
    if denom <= 0:
        return float("nan"), float("nan")
    z = (p2 - p1) / math.sqrt(denom)
    return z, 2.0 * norm_sf(abs(z))


def load_rows(db_path, days):
    """최근 `days` 거래일의 방향성 표본 (ts, horizon, direction, confidence, actual)."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        "SELECT DISTINCT substr(ts,1,10) d FROM predictions "
        "WHERE direction != 0 AND actual IS NOT NULL AND actual != 0 "
        "ORDER BY d DESC LIMIT ?", (days,))
    dates = sorted(r[0] for r in cur.fetchall())
    if not dates:
        con.close()
        return [], []
    cur.execute(
        "SELECT substr(ts,1,10), horizon, direction, confidence, actual FROM predictions "
        "WHERE substr(ts,1,10) >= ? AND direction != 0 AND actual IS NOT NULL AND actual != 0",
        (dates[0],))
    rows = cur.fetchall()
    con.close()
    return rows, dates


def analyze(rows, dates):
    """호라이즌별 층화 검정 + 버킷 분해. 반환 {hz: {...}}."""
    n_tests = max(len(HORIZONS), 1)
    alpha_adj = ALPHA / n_tests
    out = {}
    for hz in HORIZONS:
        sub = [(d, dr, cf if cf is not None else 0.0, ac)
               for (d, h, dr, cf, ac) in rows if h == hz]
        day_set = sorted(set(d for d, _, _, _ in sub))
        lo_n = lo_x = hi_n = hi_x = 0
        buckets = [[0, 0] for _ in range(len(BUCKET_EDGES))]  # [n, x] per bucket
        tot_n = tot_x = 0
        for _, dr, cf, ac in sub:
            hit = 1 if int(dr) == int(ac) else 0
            tot_n += 1
            tot_x += hit
            if cf < CONF_EDGE:
                lo_n += 1
                lo_x += hit
            else:
                hi_n += 1
                hi_x += hit
            # 버킷: [0.50,0.55) ... [0.70, inf). 0.50 미만은 버킷 0에 합산(방향성 표본 하한)
            bi = 0
            for k in range(len(BUCKET_EDGES) - 1, -1, -1):
                if cf >= BUCKET_EDGES[k]:
                    bi = k
                    break
            buckets[bi][0] += 1
            buckets[bi][1] += hit
        z, p = two_prop_z(lo_x, lo_n, hi_x, hi_n)
        acc_low = lo_x / float(lo_n) if lo_n else float("nan")
        acc_high = hi_x / float(hi_n) if hi_n else float("nan")
        acc_all = tot_x / float(tot_n) if tot_n else float("nan")
        if hi_n < MIN_HIGH_N or len(day_set) < MIN_DAYS:
            verdict = "INSUFFICIENT"
        elif not math.isnan(p) and p < alpha_adj:
            verdict = "ANTI_CALIBRATION" if z < 0 else "OK"
        else:
            verdict = "NO_SKILL"
        out[hz] = {
            "acc_low": round(acc_low, 4) if not math.isnan(acc_low) else None,
            "n_low": lo_n,
            "acc_high": round(acc_high, 4) if not math.isnan(acc_high) else None,
            "n_high": hi_n,
            "z": round(z, 3) if not math.isnan(z) else None,
            "p": round(p, 6) if not math.isnan(p) else None,
            "verdict": verdict,
            # 계약 스키마 밖 부가 필드(무해 — 소비자는 필요한 키만 읽는다)
            "days": len(day_set),
            "acc_all": round(acc_all, 4) if not math.isnan(acc_all) else None,
            "below_floor": bool(not math.isnan(acc_all) and acc_all < DIR_ACC_FLOOR),
            "buckets": [
                {"edge": BUCKET_EDGES[k], "n": buckets[k][0],
                 "acc": round(buckets[k][1] / float(buckets[k][0]), 4) if buckets[k][0] else None}
                for k in range(len(BUCKET_EDGES))
            ],
        }
    return out, alpha_adj


def main():
    ap = argparse.ArgumentParser(description="호라이즌 conf-층화 z-test (L4, 읽기 전용)")
    ap.add_argument("--days", type=int, default=20)
    ap.add_argument("--db", default=PREDICTIONS_DB)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    rows, dates = load_rows(args.db, args.days)
    if not dates:
        print("[L4] 방향성 표본 없음 — predictions DB 확인")
        return 1
    res, alpha_adj = analyze(rows, dates)

    print("=" * 96)
    print("호라이즌 conf-층화 z-test (L4) — %d거래일 (%s ~ %s), 경계 %.2f, "
          "Bonferroni α=%.3g(÷%d)" % (len(dates), dates[0], dates[-1], CONF_EDGE,
                                      alpha_adj, max(len(HORIZONS), 1)))
    print("=" * 96)
    print("%-5s %10s %8s %10s %8s %8s %10s %-18s %s"
          % ("hz", "acc<%.2f" % CONF_EDGE, "n_low", "acc>=%.2f" % CONF_EDGE,
             "n_high", "z", "p", "판정", "전체acc(floor %.2f)" % DIR_ACC_FLOOR))
    for hz in HORIZONS:
        r = res[hz]
        floor_mark = " ⚠floor미달" if r["below_floor"] else ""
        print("%-5s %10s %8d %10s %8d %8s %10s %-18s %s%s"
              % (hz,
                 "%.4f" % r["acc_low"] if r["acc_low"] is not None else "-", r["n_low"],
                 "%.4f" % r["acc_high"] if r["acc_high"] is not None else "-", r["n_high"],
                 "%.2f" % r["z"] if r["z"] is not None else "-",
                 "%.4g" % r["p"] if r["p"] is not None else "-",
                 r["verdict"],
                 "%.4f" % r["acc_all"] if r["acc_all"] is not None else "-", floor_mark))
    print()
    print("conf 버킷 단조성 (0.50/0.55/0.60/0.65/0.70+) — acc(n):")
    for hz in HORIZONS:
        cells = []
        for b in res[hz]["buckets"]:
            cells.append("%.2f+: %s(%d)" % (b["edge"],
                                            "%.3f" % b["acc"] if b["acc"] is not None else "-",
                                            b["n"]))
        print("  %-5s %s" % (hz, " | ".join(cells)))
    print()
    print("※ 관찰 계열 — 이 판정은 자동으로 어떤 호라이즌도 퇴역시키지 않는다"
          "(퇴역은 주간회의 수동 결정). floor 미달 %d주 연속 시 딥다이브 착수 권고"
          " (regression_streak_weeks=%s — 추적은 주간 리포트 대조로 수행)."
          % (int(_CFG.get("regression_streak_weeks", 3)),
             _CFG.get("regression_streak_weeks", 3)))

    # L4 입력 계약 JSON (08-02 계획 §Phase A) — 원자적 교체
    payload = {
        "generated": datetime.date.today().isoformat(),
        "days": len(dates),
        "window": [dates[0], dates[-1]],
        "conf_bucket_edge": CONF_EDGE,
        "alpha_adjusted": alpha_adj,
        "horizons": {hz: res[hz] for hz in HORIZONS},
    }
    out_dir = os.path.dirname(args.out)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    tmp = args.out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=2))
    os.replace(tmp, args.out)
    print("JSON: %s" % args.out)
    return 0


if __name__ == "__main__":
    _utf8_console()
    sys.exit(main())
