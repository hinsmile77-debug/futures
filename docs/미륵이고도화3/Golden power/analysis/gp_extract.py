# -*- coding: utf-8 -*-
"""GOLDEN POWER 검증용 데이터 추출 (1회 실행, 장 마감 후 전용).

CLAUDE.md 「장중 라이브 DB 분석 금지」 준수 — utils.analysis_db.guard_intraday 사용.
raw_data.db / predictions.db 전수 스캔이므로 반드시 15:35 이후에 실행한다.

산출물: OUT_DIR 아래 candles.pkl · feats.pkl · trades.pkl
이후 모든 분석은 이 스냅샷만 읽는다(라이브 DB 재접근 없음).
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys

import pandas as pd
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, ROOT)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_snapshot")

# 추출 대상 raw_features 키.
# ── 중복 후보(§3 B-1/B-5): GP가 재는 축을 이미 재고 있는 기존 피처
VOL_AXIS = ["atr", "atr_ratio", "realized_vol_ann", "va_bandwidth", "vkospi"]
POS_AXIS = ["bb_position", "vwap_position", "poc_distance", "in_value_area",
            "ema_cross", "poc_above"]
SWING_529 = ["swing_high_60m", "swing_low_60m", "dist_to_high_60m_atr",
             "dist_to_low_60m_atr", "bars_since_high_60m", "bars_since_low_60m",
             "swing_ready_60m", "price_extension_atr", "price_extension_atr_60m"]
# ── A안 확증 후보(오더플로)
FLOW = ["ofi_norm", "ofi_pressure", "cvd_delta_norm", "cvd_divergence",
        "cvd_slope", "mlofi_norm", "vpin", "vpin_measured", "microprice_bias",
        "queue_signal", "toxicity_score", "spread_ticks", "kyle_lambda"]
# ── 통제·레짐
CTRL = ["ret_1m", "ret_5m", "ret_15m", "time_sin", "time_cos",
        "micro_regime_code", "hurst", "hurst_ready", "trend_efficiency",
        "trend_efficiency_ready", "opt_gex_bn", "feature_degraded",
        "feature_quality_score", "is_open_volatile", "is_close_volatile",
        "avg_volume", "bar_volume"]

KEYS = VOL_AXIS + POS_AXIS + SWING_529 + FLOW + CTRL


def main() -> int:
    from utils.analysis_db import guard_intraday, connect_ro

    guard_intraday("gp_extract")

    os.makedirs(OUT_DIR, exist_ok=True)
    raw = os.path.join(ROOT, "data", "db", "raw_data.db")
    trd = os.path.join(ROOT, "data", "db", "trades.db")

    # ── 1. 분봉 ────────────────────────────────────────────────
    con = connect_ro(raw)
    c = pd.read_sql_query(
        "SELECT ts, open, high, low, close, volume, bar_recovered "
        "FROM raw_candles ORDER BY ts", con)
    print("[extract] raw_candles rows=%d  %s ~ %s" % (len(c), c["ts"].iloc[0], c["ts"].iloc[-1]))
    c.to_pickle(os.path.join(OUT_DIR, "candles.pkl"))

    # ── 2. 피처 (JSON 파싱 — 필요한 키만) ──────────────────────
    rows = []
    n_seen = 0
    cur = con.execute("SELECT ts, features FROM raw_features ORDER BY ts")
    while True:
        chunk = cur.fetchmany(5000)
        if not chunk:
            break
        for ts, blob in chunk:
            n_seen += 1
            try:
                d = json.loads(blob)
            except Exception:
                continue
            r = {"ts": ts}
            for k in KEYS:
                r[k] = d.get(k)          # 없으면 None — 계측 4원칙 ②(0으로 채우지 않는다)
            rows.append(r)
        if n_seen % 50000 == 0:
            print("[extract] raw_features %d ..." % n_seen)
    con.close()
    f = pd.DataFrame(rows)
    print("[extract] raw_features rows=%d (parsed %d)" % (len(f), n_seen))
    f.to_pickle(os.path.join(OUT_DIR, "feats.pkl"))

    # ── 3. 체결 ────────────────────────────────────────────────
    con = sqlite3.connect("file:%s?mode=ro" % trd, uri=True)
    t = pd.read_sql_query("SELECT * FROM trades ORDER BY entry_ts", con)
    con.close()
    print("[extract] trades rows=%d" % len(t))
    t.to_pickle(os.path.join(OUT_DIR, "trades.pkl"))

    print("[extract] done -> %s" % OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
