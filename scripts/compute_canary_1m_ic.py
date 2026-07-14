# -*- coding: utf-8 -*-
"""1m 활용방안 C — 신규 알파 카나리아 호라이즌 IC 계측.

배경: 1m은 331차 후속2로 앙상블 방향투표에서 퇴역했으나(역스킬 확정), 다중 호라이즌
알파 감쇠 곡선 문헌(Kolm et al. 2023 등)에 따르면 진짜 마이크로구조 알파가 존재한다면
가장 먼저(가장 강하게) 1m에서 신호가 보인다. `DYNAMIC_FEATURES_POOL`(config/constants.py)에
등록된 신규 피처 후보들(vpin·kyle_lambda·trend_efficiency·rv_iv_spread·
multi_timeframe_5m/15m·round_number_distance·hurst_ready·opt_gex_sign·opt_atm_pcr 등)의
1m 예측력을 주기적으로 재는 진단 도구 — 결과는 `canary_1m_ic_scores`(SHAP_DB)에 누적만
될 뿐, 학습 피처셋·게이트 어디에도 자동 반영되지 않는다(자동 통합 금지 원칙, CLAUDE.md §6).

실행: main.py의 EffectReports 주기 워커(_start_effect_report_worker)가 하루 1회 자동
호출한다(main.py 참조). 수동 실행도 가능: python scripts/compute_canary_1m_ic.py

읽기 전용: raw_data.db만 읽고 SHAP_DB(canary_1m_ic_scores)에만 쓴다. 모델·설정·
학습 파이프라인 어디에도 관여하지 않는다.
"""
import datetime
import json
import math
import os
import sqlite3
import sys

import numpy as np
import pandas as pd

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from config.settings import RAW_DATA_DB, SHAP_DB  # noqa: E402
from config.constants import DYNAMIC_FEATURES_POOL  # noqa: E402
from utils.db_utils import execute, init_shap_db  # noqa: E402

WINDOW_DAYS = 28  # 4주 롤링 창
HORIZON_MIN = 1   # 카나리아 대상 = 1m


def _spearman(a: np.ndarray, b: np.ndarray):
    """rank + pearson — scipy 없이 순수 pandas/numpy로 계산 (32bit DLL 충돌 회피)."""
    a = pd.Series(a, dtype="float64")
    b = pd.Series(b, dtype="float64")
    ra, rb = a.rank(), b.rank()
    da, db = ra - ra.mean(), rb - rb.mean()
    denom = math.sqrt(float((da * da).sum()) * float((db * db).sum()))
    if denom <= 0:
        return float("nan"), float("nan")
    r = float((da * db).sum()) / denom
    n = len(a)
    if n < 10:
        return r, float("nan")
    z = abs(r) * math.sqrt(n - 1)
    p = math.erfc(z / math.sqrt(2.0))
    return r, p


def load_recent(window_days: int = WINDOW_DAYS):
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=window_days)).strftime("%Y-%m-%d")
    con = sqlite3.connect(RAW_DATA_DB)
    rf = pd.read_sql(
        "SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts", con, params=(cutoff,)
    )
    rc = pd.read_sql(
        "SELECT ts, close FROM raw_candles WHERE ts >= ? ORDER BY ts", con, params=(cutoff,)
    )
    con.close()
    feat = pd.DataFrame([json.loads(s) for s in rf["features"]])
    feat.index = pd.to_datetime(rf["ts"].values)
    feat = feat.apply(pd.to_numeric, errors="coerce")
    px = rc.set_index(pd.to_datetime(rc["ts"]))["close"]
    px = px[~px.index.duplicated()]
    return feat, px


def compute_canary_ic(feat: pd.DataFrame, px: pd.Series, candidates):
    day = pd.Series(px.index.date, index=px.index)
    fwd = (px.shift(-HORIZON_MIN) / px - 1.0).where(day.shift(-HORIZON_MIN) == day)

    feat = feat.loc[feat.index.intersection(px.index)]
    fwd = fwd.reindex(feat.index)

    results = []
    for name in candidates:
        if name not in feat.columns:
            results.append({"feature": name, "ic": None, "p_value": None, "n_samples": 0, "coverage": 0.0})
            continue
        x = feat[name]
        coverage = float(x.notna().mean())
        m = x.notna() & fwd.notna()
        n = int(m.sum())
        if n < 200 or x[m].nunique() < 2:
            results.append({"feature": name, "ic": None, "p_value": None, "n_samples": n, "coverage": round(coverage, 4)})
            continue
        r, p = _spearman(x[m].to_numpy(), fwd[m].to_numpy())
        results.append({
            "feature": name,
            "ic": round(r, 5) if r == r else None,
            "p_value": round(p, 5) if p == p else None,
            "n_samples": n,
            "coverage": round(coverage, 4),
        })
    return results


def main():
    init_shap_db()  # canary_1m_ic_scores 테이블이 없으면 생성 (idempotent)
    feat, px = load_recent()
    if feat.empty or px.empty:
        print("[Canary1mIC] 데이터 부족 — 스킵")
        return
    results = compute_canary_ic(feat, px, DYNAMIC_FEATURES_POOL)

    run_date = datetime.date.today().isoformat()
    rows = [
        (run_date, r["feature"], r["ic"], r["p_value"], r["n_samples"], r["coverage"])
        for r in results
    ]
    for row in rows:
        execute(
            SHAP_DB,
            """INSERT INTO canary_1m_ic_scores
               (run_date, feature, ic, p_value, n_samples, coverage)
               VALUES (?, ?, ?, ?, ?, ?)""",
            row,
        )

    ranked = sorted(
        [r for r in results if r["ic"] is not None],
        key=lambda r: abs(r["ic"]), reverse=True,
    )
    print("[Canary1mIC] run_date=%s 후보=%d개 (유효=%d)" % (run_date, len(results), len(ranked)))
    for r in ranked:
        sig = "*" if (r["p_value"] is not None and r["p_value"] < 0.05) else " "
        print("  %-28s IC=%+.4f%s p=%s n=%d coverage=%.2f" % (
            r["feature"], r["ic"], sig,
            "%.4f" % r["p_value"] if r["p_value"] is not None else "N/A",
            r["n_samples"], r["coverage"],
        ))


if __name__ == "__main__":
    main()
