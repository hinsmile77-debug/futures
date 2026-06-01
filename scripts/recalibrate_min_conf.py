# scripts/recalibrate_min_conf.py — GBM 재학습 후 min_conf 자동 재보정
"""
재학습된 GBM으로 오늘 실 피처를 예측하여 conf 분포를 측정,
80th percentile 기준으로 time_strategy_router.py의 min_confidence를 업데이트한다.

사용법:
  python scripts/recalibrate_min_conf.py             # 분포 측정 + 출력
  python scripts/recalibrate_min_conf.py --apply     # settings 자동 업데이트

Python 3.7 32-bit 호환
"""
import argparse
import datetime
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import numpy as np
import sqlite3
import json

from config.settings import RAW_DATA_DB, HORIZONS
from model.multi_horizon_model import MultiHorizonModel, apply_robust_preprocess

PCTILE_ENTRY = 80   # 상위 20% conf만 진입 허용
ABS_FLOOR    = 0.38 # 절대 하한 — 이 이하는 아무리 상대적으로 높아도 차단


def load_today_features():
    """오늘 raw_features + raw_candles 로드 → feature 행렬 반환."""
    today = datetime.date.today().isoformat()
    conn  = sqlite3.connect(RAW_DATA_DB, timeout=15)
    conn.row_factory = sqlite3.Row

    feat_rows = conn.execute(
        "SELECT ts, features FROM raw_features WHERE substr(ts,1,10)=? ORDER BY ts",
        (today,),
    ).fetchall()
    conn.close()

    if not feat_rows:
        print("[ERROR] 오늘(%s) raw_features 없음" % today)
        sys.exit(1)

    # 피처 행렬 구성
    records  = []
    feat_names = None
    feat_count = 0
    for r in feat_rows:
        try:
            fd = json.loads(r["features"])
        except Exception:
            continue
        keys = list(fd.keys())
        if feat_names is None or len(keys) >= feat_count:
            feat_names = keys
            feat_count = len(keys)
        records.append((r["ts"], fd))

    print("오늘 피처 행 수: %d  피처 수: %d" % (len(records), len(feat_names)))
    return records, feat_names


def measure_conf_distribution(model, records, feat_names):
    """각 분봉 피처로 6 호라이즌 예측 → conf 분포 반환."""
    confs = {h: [] for h in HORIZONS}
    X_all = np.array(
        [[rec[1].get(f, 0.0) for f in feat_names] for rec in records],
        dtype=np.float32,
    )
    X_proc = apply_robust_preprocess(X_all, feat_names)

    for i in range(len(records)):
        x = X_proc[i]
        proba = model.predict_proba(x)
        for h, res in proba.items():
            confs[h].append(float(res.get("confidence", 1/3)))

    return confs


def compute_new_min_confs(confs_dict):
    """각 호라이즌별 80th percentile 기반 + zone별 조정."""
    per_hz = {}
    for h, cs in confs_dict.items():
        sorted_cs = sorted(cs)
        p80 = sorted_cs[int(len(sorted_cs) * PCTILE_ENTRY / 100)]
        per_hz[h] = max(round(p80, 3), ABS_FLOOR)

    # 전체 호라이즌 공통 대표값 (median)
    p80_values = sorted(per_hz.values())
    median_p80 = p80_values[len(p80_values)//2]

    zone_confs = {
        "OPEN_VOLATILE":  max(median_p80 + 0.03, ABS_FLOOR + 0.03),
        "STABLE_TREND":   median_p80,
        "LUNCH_RECOVERY": max(median_p80 - 0.01, ABS_FLOOR),
        "CLOSE_VOLATILE": max(median_p80 - 0.02, ABS_FLOOR),
    }
    return per_hz, zone_confs, median_p80


def print_report(confs_dict, per_hz, zone_confs, median_p80):
    import statistics
    print()
    print("=== 재학습 후 conf 분포 ===")
    for h, cs in sorted(confs_dict.items()):
        p80 = sorted(cs)[int(len(cs)*0.80)]
        print("  %3s  avg=%.3f  p50=%.3f  p80=%.3f  max=%.3f  new_min=%.3f" % (
            h,
            statistics.mean(cs),
            sorted(cs)[len(cs)//2],
            p80,
            max(cs),
            per_hz[h],
        ))

    print()
    print("=== 새 min_conf 시간대별 ===")
    print("  median_p80 = %.3f" % median_p80)
    for zone, mc in zone_confs.items():
        print("  %s: %.3f" % (zone, mc))


def apply_to_settings(zone_confs):
    """time_strategy_router.py _ZONE_PARAMS min_confidence 업데이트."""
    router_path = os.path.join(BASE_DIR, "strategy", "entry", "time_strategy_router.py")
    with open(router_path, "r", encoding="utf-8") as f:
        src = f.read()

    import re
    for zone, mc in zone_confs.items():
        # "OPEN_VOLATILE": { "min_confidence": 0.60, 패턴 교체
        pattern = r'("%s"\s*:\s*\{[^}]*?"min_confidence"\s*:\s*)([0-9.]+)' % zone
        new_val = r'\g<1>%.2f' % mc
        src, n = re.subn(pattern, new_val, src, flags=re.DOTALL)
        if n:
            print("  %s min_confidence -> %.2f" % (zone, mc))
        else:
            print("  [WARN] %s 패턴 미발견 — 수동 확인 필요" % zone)

    with open(router_path, "w", encoding="utf-8") as f:
        f.write(src)
    print("[APPLY] time_strategy_router.py 업데이트 완료")


def run(apply=False):
    print("[%s] conf 분포 측정 시작" % datetime.datetime.now().strftime("%H:%M:%S"))

    # 모델 로드
    model = MultiHorizonModel()
    model._load_all()
    if not model.is_ready():
        print("[ERROR] 모델 미학습 상태 — 재학습 완료 후 실행하세요")
        sys.exit(1)
    print("피처 수: %d" % len(model.feature_names or []))

    # 오늘 피처 로드
    records, feat_names = load_today_features()

    # 공통 피처만 사용 (모델 feature_names 기준)
    model_feats = list(model.feature_names or feat_names)
    avail = set(feat_names)
    used  = [f for f in model_feats if f in avail]
    miss  = [f for f in model_feats if f not in avail]
    if miss:
        print("[WARN] 모델 피처 중 오늘 raw_features에 없는 것: %d개" % len(miss))
        print("  예시:", miss[:5])

    # conf 분포 측정
    confs = measure_conf_distribution(model, records, model_feats)

    # 새 min_conf 계산
    per_hz, zone_confs, median_p80 = compute_new_min_confs(confs)
    print_report(confs, per_hz, zone_confs, median_p80)

    if apply:
        print()
        print("[APPLY] time_strategy_router.py 업데이트...")
        apply_to_settings(zone_confs)
    else:
        print()
        print("-- dry-run. --apply 옵션으로 실제 업데이트 가능.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="time_strategy_router.py min_confidence 자동 업데이트")
    args = parser.parse_args()
    run(apply=args.apply)
