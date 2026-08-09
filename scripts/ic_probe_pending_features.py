# -*- coding: utf-8 -*-
"""P2-1/P2-4 재검증 — basis_pt 등 include_pending_validation 피처의 최신 구간 IC 재측정.

읽기 전용(raw_data.db만 읽음). 07-13 딥다이브 보고서(§1 방법)와 동일한 방법론:
Spearman IC(전방수익률 대비) + 반분(전반/후반) 안정성. 다중검정 보정 없이 명목 p만
표시 — 최종 채택 근거로 쓰지 말고 "다음 단계 검증에 올릴 후보 선별"용으로만 사용
(275차·311차 후속4 원칙, docs/미륵이고도화2/무스킬_피처셋_딥다이브_보고서_2026-07-13.md).
"""
import json
import os
import sqlite3
import sys

# [455차] scripts 패키지 import(노이즈 벤치마크)용 — 프로젝트 루트를 경로에 보장
_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# [448차 패턴/455차] BLAS DLL 경로 보장 — conda 미활성 직접 실행 시 scipy·numpy의
# MKL 지연로드가 0xC06D007F로 즉사한다 (454차 spearmanr 크래시와 동일 뿌리).
from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402
ensure_conda_dll_path()

import numpy as np
import pandas as pd
from scipy import stats

RAW_DATA_DB = "data/db/raw_data.db"
HORIZONS = {"1m": 1, "3m": 3, "5m": 5, "10m": 10, "15m": 15}
TARGET_FEATURES = [
    "basis_pt", "basis_change_pt", "program_arb_net", "program_non_arb_net",
    "prev_day_same_hour_ret", "vkospi",
]


MAX_ROWS = 15000  # 32-bit 런타임 메모리 방어 (basis_pt 계열은 07-14부터만 존재하므로 충분)


def load():
    con = sqlite3.connect(RAW_DATA_DB)
    rf = pd.read_sql(
        "SELECT ts, features FROM raw_features ORDER BY ts DESC LIMIT %d" % MAX_ROWS, con
    ).iloc[::-1].reset_index(drop=True)
    rc = pd.read_sql(
        "SELECT ts, close FROM raw_candles ORDER BY ts DESC LIMIT %d" % (MAX_ROWS + 60), con
    ).iloc[::-1].reset_index(drop=True)
    con.close()
    # 타깃 피처만 우선 파싱해 메모리 절약(전체 130키 DataFrame화 회피)
    keep_keys = set(TARGET_FEATURES)
    records = []
    for s in rf["features"]:
        d = json.loads(s)
        records.append({k: d.get(k) for k in keep_keys})
    feat = pd.DataFrame(records)
    feat.index = pd.to_datetime(rf["ts"].values)
    feat = feat.apply(pd.to_numeric, errors="coerce")
    close = pd.Series(rc["close"].astype(float).values, index=pd.to_datetime(rc["ts"].values))
    return feat, close


def fwd_ret(close, ts_index, h_min):
    future_ts = ts_index + pd.to_timedelta(h_min, unit="m")
    aligned = close.reindex(future_ts)
    aligned.index = ts_index
    cur = close.reindex(ts_index)
    return (aligned - cur) / cur


def ic_report(x, y):
    mask = x.notna() & y.notna()
    n = int(mask.sum())
    if n < 30:
        return n, None, None
    rho, p = stats.spearmanr(x[mask], y[mask])
    return n, rho, p


def main():
    import argparse
    ap = argparse.ArgumentParser(description="pending 피처 IC 프로브 (1차 스크리닝, 읽기 전용)")
    ap.add_argument("--no-noise", action="store_true",
                    help="[455차 N3] 노이즈 벤치마크 비활성 (기본: 5개 삽입)")
    args = ap.parse_args()

    feat, close = load()
    print("전체 raw_features 표본:", len(feat), "| 기간:", feat.index.min(), "~", feat.index.max())
    print()

    probe_names = list(TARGET_FEATURES)
    if not args.no_noise:
        # [MW0601 455차 / N3] 노이즈 벤치마크 — 실피처를 템플릿으로 셔플 3 + 위상무작위 2.
        # 시드 = 관찰창 마지막 날짜(재현 가능). 하한선 규칙은 noise_benchmark.py 헤더 참조.
        from scripts.noise_benchmark import make_noise_features, noise_floor, is_noise_name
        templates = {c: feat[c].values.astype(float) for c in feat.columns
                     if feat[c].notna().sum() >= 30}
        seed = int(feat.index.max().strftime("%Y%m%d")) if len(feat) else 20260101
        noise = make_noise_features(templates, seed=seed)
        for nm, arr in noise.items():
            feat[nm] = arr
        probe_names += list(noise.keys())
        print(f"[N3] 노이즈 벤치마크 {len(noise)}개 삽입 (seed={seed}) — "
              "실피처가 노이즈 최고 |IC|보다 약하면 후보 자격 없음")
        print()

    results = []  # (name, hz, n, rho, p)
    for name in probe_names:
        if name not in feat.columns:
            print(f"[{name}] raw_features에 키 없음 — 스킵")
            continue
        col = feat[name]
        n_present = col.notna().sum()
        n_nonzero = (col.fillna(0) != 0).sum()
        first_ts = col[col.notna() & (col != 0)].index.min() if n_nonzero else None
        print(f"=== {name} === present={n_present} nonzero={n_nonzero} first_nonzero_ts={first_ts}")
        for hz, h_min in HORIZONS.items():
            y = fwd_ret(close, feat.index, h_min)
            n, rho, p = ic_report(col, y)
            if rho is None:
                print(f"   {hz}: n={n} (표본부족, IC 계산 스킵)")
                continue
            # 반분 안정성
            valid = col.notna() & y.notna()
            idx_valid = feat.index[valid]
            if len(idx_valid) >= 60:
                mid = idx_valid[len(idx_valid) // 2]
                first_half = valid & (feat.index <= mid)
                second_half = valid & (feat.index > mid)
                # [455차 수정] 종전 `_, rho1 = spearmanr(...)`는 (rho, p) 반환 순서상
                # p값을 rho로 출력하던 버그 — 반분 안정성 표시가 IC가 아니라 p였다.
                rho1, _ = stats.spearmanr(col[first_half], y[first_half]) if first_half.sum() > 20 else (None, None)
                rho2, _ = stats.spearmanr(col[second_half], y[second_half]) if second_half.sum() > 20 else (None, None)
                half_str = f"반분(전{rho1:+.3f}/후{rho2:+.3f})" if rho1 is not None and rho2 is not None else "반분 표본부족"
            else:
                half_str = "반분 표본부족"
            sig = "*" if p < 0.05 else " "
            print(f"   {hz}: n={n:5d} IC={rho:+.4f}{sig} p={p:.4f} {half_str}")
            results.append({"name": name, "hz": hz, "n": n, "ic": rho, "p": p})
        print()

    # [MW0601 455차 / N3] 호라이즌별 노이즈 하한선 요약
    if not args.no_noise and results:
        from scripts.noise_benchmark import noise_floor, is_noise_name
        print("=" * 72)
        print("[N3] 노이즈 하한선 (호라이즌별 노이즈 max |IC|) — 이보다 약하면 후보 자격 없음")
        for hz in HORIZONS:
            hz_rows = [r for r in results if r["hz"] == hz]
            floor, floor_name = noise_floor(hz_rows, stat_key="ic")
            if floor_name is None:
                continue
            losers = [r["name"] for r in hz_rows
                      if not is_noise_name(r["name"]) and abs(r["ic"]) <= floor]
            alarm = [r["name"] for r in hz_rows
                     if is_noise_name(r["name"]) and r["p"] is not None and r["p"] < 0.05]
            print(f"   {hz}: floor |IC|={floor:.4f} ({floor_name})"
                  + (f" | 하한선 미달 실피처: {', '.join(losers)}" if losers else " | 미달 없음")
                  + (f" | ⚠ 노이즈가 명목 유의: {', '.join(alarm)} — 이 회차 스크리닝 전체 의심"
                     if alarm else ""))
        print("   ※ 명목 p 기준 1차 스크리닝 — 채택 근거 아님(헤더 원칙). 정식 검정은"
              " core_feature_discovery(Bonferroni)로.")


if __name__ == "__main__":
    main()
