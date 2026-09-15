# -*- coding: utf-8 -*-
"""[MW0601 587차 / P1-1] ConstOut raw 기준 임계 재보정 — 읽기 전용 · 장 마감 후 전용.

════════════════════════════════════════════════════════════════════════════
왜 필요한가
════════════════════════════════════════════════════════════════════════════
ConstOut 은 "GBM 이 붕괴했는가" 를 묻는 장치인데, 현행 판정은
`GBM → SGD 블렌드 → RF 블렌드 → BAR_CACHE_DECAY → bias fallback → Platt` 을
전부 통과한 뒤의 값을 읽는다. 587차가 **보정 전 GBM raw** 계열을
`ensemble_decisions.detail` 에 적재하기 시작했고, 이 스크립트가 그 위에서
`CONST_OUT_RAW_RANGE` 를 정한다.

현행 `CONST_OUT_RAW_RANGE = 0.005` 는 **보정된 적이 없다** — post-Platt 분포에
맞춘 `_CONST_OUT_RANGE` 를 그대로 복사해 둔 값이다.

════════════════════════════════════════════════════════════════════════════
사전등록 판정 기준 — 데이터를 보기 **전에** 고정한다 (§9-4, 458차 D6)
════════════════════════════════════════════════════════════════════════════
⚠ 아래 상수를 결과가 마음에 안 든다고 고치면 사전등록 위반이다.
   고쳐야 한다면 **고친 이유를 커밋에 남기고 표본을 처음부터 다시 모은다.**

P1 표본     : ≥ MIN_DAYS 거래일 AND 호라이즌별 raw 관측 ≥ MIN_MINUTES 분
P2 방향     : raw 발화 분 < live 발화 분  (오탐이 줄어야 한다)
              AND raw 발화 분 > 0        (감지 기능이 사라지면 안 된다)
P3 설명력   : live-only 불일치 건의 raw range 중앙값 ≥ 임계 × EXPLAIN_MULT
              — "우연히 못 잡았다" 가 아니라 "명백히 변동 중이었다" 를 보인다
P4 안정성   : 선택 임계의 ±STABILITY_PCT 에서도 P2·P3 유지

선택 규칙   : P2·P3·P4 를 모두 만족하는 후보 중 **가장 큰** 임계.
              (range < 임계 → STUCK 이므로 임계가 클수록 민감하다. 오탐 제약을
               지키는 선에서 민감도를 최대한 남긴다.)

FAIL 시     : `CONST_OUT_RAW_BASED_ENABLED` 를 True 로 바꾸지 않는다.
              표본을 더 모으거나(P1 미달) 감지 정의 자체를 재설계한다(P2/P3 미달).

════════════════════════════════════════════════════════════════════════════
사용법
════════════════════════════════════════════════════════════════════════════
    python scripts/const_out_raw_recalibration.py [--days 60]

exit 0 = PASS(임계 제안) / 2 = FAIL / 3 = 표본 미달(P1) / 1 = 오류
"""
from __future__ import print_function

import argparse
import json
import os
import sqlite3
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402  (448차)

ensure_conda_dll_path()

from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402  (456차)

# ── 사전등록 상수 (고정) ──────────────────────────────────────────────────────
MIN_DAYS        = 10      # P1
MIN_MINUTES     = 1000    # P1 (호라이즌별)
EXPLAIN_MULT    = 3.0     # P3
STABILITY_PCT   = 0.20    # P4
CANDIDATES      = [0.002, 0.003, 0.004, 0.005, 0.007, 0.010, 0.015, 0.020]
HORIZONS_JUDGED = ("3m", "5m")   # 실제로 ConstOut 이 도달 가능한 호라이즌
CONST_OUT_N     = 5       # 감지기와 같아야 한다 (ensemble_decision._CONST_OUT_N)
# ─────────────────────────────────────────────────────────────────────────────


def _median(xs):
    if not xs:
        return None
    ys = sorted(xs)
    n = len(ys)
    return ys[n // 2] if n % 2 else (ys[n // 2 - 1] + ys[n // 2]) / 2.0


def _runs(series, thr):
    """(dir, conf) 시계열에서 ConstOut 규칙을 재현해 STUCK 인 분의 인덱스 집합과
    매 분의 range 를 돌려준다. 감지기와 **같은 규칙**이어야 한다."""
    stuck, ranges = set(), {}
    for i in range(len(series)):
        win = series[max(0, i - CONST_OUT_N + 1): i + 1]
        if len(win) < CONST_OUT_N:
            continue
        dirs = set(d for d, _ in win)
        confs = [c for _, c in win]
        rng = max(confs) - min(confs)
        ranges[i] = rng
        if len(dirs) == 1 and rng < thr:
            stuck.add(i)
    return stuck, ranges


def load(days):
    from config.settings import PREDICTIONS_DB
    con = connect_ro(PREDICTIONS_DB)
    rows = con.execute(
        "SELECT ts, detail FROM ensemble_decisions "
        "WHERE ts >= date('now', ?) AND detail IS NOT NULL ORDER BY ts",
        ("-%d day" % days,),
    ).fetchall()
    con.close()

    live = defaultdict(list)   # hz -> [(dir, round3 conf)]
    raw = defaultdict(list)
    days_seen = set()
    for ts, dj in rows:
        try:
            d = json.loads(dj)
        except Exception:
            continue
        days_seen.add(ts[:10])
        for hz, v in (d or {}).items():
            if not isinstance(v, dict):
                continue
            if v.get("confidence") is None:
                continue
            live[hz].append((int(v.get("direction") or 0), round(float(v["confidence"]), 3)))
            # 키 부재 = 미측정(587차 규약). 있을 때만 raw 계열에 넣는다.
            if v.get("gbm_raw_conf") is not None:
                raw[hz].append((int(v.get("gbm_raw_dir") or 0),
                                round(float(v["gbm_raw_conf"]), 3)))
    return live, raw, sorted(days_seen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=60)
    args = ap.parse_args()

    guard_intraday("const_out_raw_recalibration")

    live, raw, days_seen = load(args.days)
    print("구간: %s ~ %s (%d 거래일)"
          % (days_seen[0] if days_seen else "-",
             days_seen[-1] if days_seen else "-", len(days_seen)))

    # ── P1 표본 ──────────────────────────────────────────────────────────────
    short = [h for h in HORIZONS_JUDGED if len(raw.get(h, [])) < MIN_MINUTES]
    if len(days_seen) < MIN_DAYS or short:
        print("\nP1 미달 — 표본 부족")
        print("  거래일 %d / 필요 %d" % (len(days_seen), MIN_DAYS))
        for h in HORIZONS_JUDGED:
            print("  %-3s raw 관측 %d분 / 필요 %d" % (h, len(raw.get(h, [])), MIN_MINUTES))
        print("\n⚠ 문턱을 낮춰 판정하지 말 것 (458차 D6). 표본을 더 모은다.")
        return 3

    # ── 후보 스윕 ────────────────────────────────────────────────────────────
    from config.settings import ENSEMBLE_WEIGHTS  # noqa: F401  (임포트 가능성 확인)
    live_stuck = {}
    for h in HORIZONS_JUDGED:
        s, _ = _runs(live[h], 0.005)   # 현행 _CONST_OUT_RANGE
        live_stuck[h] = s

    print("\n%-7s %-4s %8s %8s %10s %12s %s"
          % ("임계", "hz", "raw발화", "live발화", "live-only", "설명력중앙", "P2/P3"))
    ok_thr = []
    for thr in CANDIDATES:
        verdicts = []
        for h in HORIZONS_JUDGED:
            rs, rranges = _runs(raw[h], thr)
            ls = live_stuck[h]
            n_raw, n_live = len(rs), len(ls)
            # live-only = live 는 STUCK 인데 raw 는 아닌 분 (오탐 후보)
            # ⚠ 두 계열은 길이가 다를 수 있다(raw 미측정 분 존재) — 인덱스가 아니라
            #   비율로만 비교한다. 설명력은 raw 쪽 range 분포로 본다.
            lo_ranges = [rranges[i] for i in rranges if i not in rs]
            med = _median(lo_ranges)
            p2 = (0 < n_raw < n_live)
            p3 = (med is not None and med >= thr * EXPLAIN_MULT)
            verdicts.append(p2 and p3)
            print("%-7.3f %-4s %8d %8d %10d %12s %s"
                  % (thr, h, n_raw, n_live, len(lo_ranges),
                     ("%.4f" % med) if med is not None else "-",
                     "OK" if (p2 and p3) else ("P2x" if not p2 else "P3x")))
        if all(verdicts):
            ok_thr.append(thr)

    if not ok_thr:
        print("\nFAIL — P2·P3 를 만족하는 후보가 없다.")
        print("  감지 정의 자체를 재설계해야 한다(1차원 max_prob → up/down 포함).")
        return 2

    # ── P4 안정성: 선택 후보의 ±20% 가 후보군 안에 남아 있는가 ─────────────────
    chosen = None
    for thr in sorted(ok_thr, reverse=True):     # 선택 규칙: 가장 큰 것
        lo, hi = thr * (1 - STABILITY_PCT), thr * (1 + STABILITY_PCT)
        if any(lo <= t <= hi for t in ok_thr if t != thr):
            chosen = thr
            break
    if chosen is None:
        print("\nFAIL — P4 미달: 통과 후보가 고립돼 있다(±%d%% 이웃 없음)."
              % int(STABILITY_PCT * 100))
        print("  통과 후보: %s" % ok_thr)
        return 2

    print("\nPASS — 제안 임계 CONST_OUT_RAW_RANGE = %.3f" % chosen)
    print("  통과 후보: %s (선택 규칙: 가장 큰 값)" % ok_thr)
    print("\n전환 절차:")
    print("  1) config/settings.py:CONST_OUT_RAW_RANGE 갱신")
    print("  2) 섀도 불일치표를 주간회의에 보고 → 승인")
    print("  3) CONST_OUT_RAW_BASED_ENABLED = True")
    print("  4) strategy_events 에 METRIC_REDEFINITION 마커 (471차 G-2 채널 불연속)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print("오류: %s" % e)
        sys.exit(1)
