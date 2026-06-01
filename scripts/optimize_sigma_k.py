# scripts/optimize_sigma_k.py — 호라이즌별 최적 σ_k 탐색 (P5)
"""
현재 SIGMA_K=0.41(전 호라이즌 공통)을 호라이즌별로 최적화한다.

목표 지표:
  1) FLAT 비율 30~35% (너무 많으면 UP/DOWN 학습 부족, 너무 적으면 FLAT 과소)
  2) UP / DOWN 비율 균형 (|up_rate - down_rate| 최소화)
  3) 위 두 지표의 합산 score 최소 k 선택

사용법:
  python scripts/optimize_sigma_k.py               # 탐색 결과 출력
  python scripts/optimize_sigma_k.py --apply       # settings.py SIGMA_K_PER_HORIZON 자동 업데이트
  python scripts/optimize_sigma_k.py --weeks 26    # 26주 데이터 사용 (기본: 전체)

Python 3.7 32-bit 호환
"""
import argparse
import datetime
import math
import os
import re
import sqlite3
import sys
from collections import deque

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.settings import (
    RAW_DATA_DB, HORIZONS, SIGMA_W, SIGMA_W_MIN,
    SIGMA_K as _CURRENT_K,
)

K_RANGE  = [0.28, 0.30, 0.33, 0.35, 0.38, 0.41, 0.44, 0.47, 0.50, 0.55, 0.60]
FLAT_TARGET  = 0.33   # 목표 FLAT 비율
FLAT_BAND    = 0.05   # ±5% 이내면 허용 (30~38%)


def _build_labels(close_map, ts_list, h_min, k):
    """주어진 k로 호라이즌 레이블을 생성하고 UP/DOWN/FLAT 카운트 반환."""
    _sigma_buf = deque(maxlen=SIGMA_W)
    up = dn = fl = 0

    for ts in ts_list:
        # rolling sigma 업데이트
        t_prev = (
            datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            - datetime.timedelta(minutes=1)
        ).strftime("%Y-%m-%d %H:%M:%S")
        c0    = close_map.get(ts)
        c_prev = close_map.get(t_prev)
        if c0 and c_prev and c_prev > 0:
            _sigma_buf.append((c0 - c_prev) / c_prev * 100.0)

        n = len(_sigma_buf)
        if n >= SIGMA_W_MIN and n > 1:
            _v = list(_sigma_buf)
            _m = sum(_v) / n
            _sig = math.sqrt(sum((x - _m) ** 2 for x in _v) / (n - 1))
            threshold = _sig / 100.0 * k * math.sqrt(h_min)
        else:
            threshold = 0.0003   # fallback

        # 미래 가격
        future_ts = (
            datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            + datetime.timedelta(minutes=h_min)
        ).strftime("%Y-%m-%d %H:%M:%S")
        c_now    = close_map.get(ts)
        c_future = close_map.get(future_ts)
        if not (c_now and c_future and threshold > 0):
            fl += 1
            continue

        ret = (c_future - c_now) / c_now
        if ret > threshold:
            up += 1
        elif ret < -threshold:
            dn += 1
        else:
            fl += 1

    total = up + dn + fl
    if total == 0:
        return 0.0, 0.0, 1.0
    return up / total, dn / total, fl / total


def _score(up_r, dn_r, fl_r):
    """FLAT 이탈 + UP/DOWN 불균형의 합산 페널티 (낮을수록 좋음)."""
    flat_penalty = abs(fl_r - FLAT_TARGET)
    balance_pen  = abs(up_r - dn_r)
    return flat_penalty + balance_pen * 0.5


def run(weeks_back=None, apply=False):
    if not os.path.exists(RAW_DATA_DB):
        print(f"[ERROR] raw_data.db 없음: {RAW_DATA_DB}")
        sys.exit(1)

    with sqlite3.connect(RAW_DATA_DB, timeout=20) as conn:
        conn.row_factory = sqlite3.Row

        cutoff_clause = ""
        params = ()
        if weeks_back:
            cutoff = (
                datetime.datetime.now() - datetime.timedelta(weeks=weeks_back)
            ).strftime("%Y-%m-%d %H:%M:%S")
            cutoff_clause = "WHERE ts >= ?"
            params = (cutoff,)

        ts_list = [
            r["ts"] for r in conn.execute(
                f"SELECT ts FROM raw_features {cutoff_clause} ORDER BY ts",
                params,
            ).fetchall()
        ]
        close_map = {
            r["ts"]: float(r["close"]) for r in conn.execute(
                f"SELECT ts, close FROM raw_candles {cutoff_clause} ORDER BY ts",
                params,
            ).fetchall()
        }

    if not ts_list:
        print("[ERROR] raw_features 데이터 없음")
        sys.exit(1)

    print(f"데이터 기간: {ts_list[0][:10]} ~ {ts_list[-1][:10]}  ({len(ts_list):,}봉)")
    print(f"현재 SIGMA_K = {_CURRENT_K}  (전 호라이즌 공통)")
    print()

    results = {}
    for hz, h_min in HORIZONS.items():
        best_k     = None
        best_score = float("inf")
        row_data   = []

        for k in K_RANGE:
            up_r, dn_r, fl_r = _build_labels(close_map, ts_list, h_min, k)
            sc = _score(up_r, dn_r, fl_r)
            row_data.append((k, up_r, dn_r, fl_r, sc))
            if sc < best_score:
                best_score = sc
                best_k     = k

        results[hz] = best_k
        print(f"[{hz:>3}]  최적 k={best_k:.2f}  (score={best_score:.4f})")
        for k, up_r, dn_r, fl_r, sc in row_data:
            marker = " ◀" if k == best_k else ""
            print(f"       k={k:.2f}  UP={up_r:.1%}  DN={dn_r:.1%}  FL={fl_r:.1%}  score={sc:.4f}{marker}")
        print()

    print("=== 최적 k 요약 ===")
    for hz in HORIZONS:
        print(f"  {hz:>3}: {results[hz]:.2f}  (현재 공통 {_CURRENT_K})")

    if apply:
        _update_settings(results)
        print("\n[APPLY] settings.py SIGMA_K_PER_HORIZON 업데이트 완료")

    return results


def _update_settings(k_dict):
    """settings.py에 SIGMA_K_PER_HORIZON 딕셔너리를 추가·교체."""
    settings_path = os.path.join(BASE_DIR, "config", "settings.py")
    with open(settings_path, "r", encoding="utf-8") as f:
        src = f.read()

    new_block = (
        "\n# 호라이즌별 최적 σ_k (scripts/optimize_sigma_k.py 탐색 결과 — P5)\n"
        "# batch_retrainer._load_from_db()에서 USE_ROLLING_SIGMA_THRESHOLD=True 시 사용\n"
        "SIGMA_K_PER_HORIZON = {\n"
    )
    for hz in ("1m", "3m", "5m", "10m", "15m", "30m"):
        new_block += f'    "{hz}": {k_dict.get(hz, 0.41):.2f},\n'
    new_block += "}\n"

    pattern = r"\n# 호라이즌별 최적 σ_k.*?SIGMA_K_PER_HORIZON\s*=\s*\{.*?\}\n"
    if re.search(pattern, src, re.DOTALL):
        src = re.sub(pattern, new_block, src, flags=re.DOTALL)
    else:
        # SIGMA_K 줄 뒤에 삽입
        src = src.replace(
            f"SIGMA_K:   float = {_CURRENT_K}",
            f"SIGMA_K:   float = {_CURRENT_K}" + new_block,
        )

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(src)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="호라이즌별 최적 σ_k 탐색")
    parser.add_argument("--apply",    action="store_true",
                        help="탐색 결과를 settings.py에 자동 기록")
    parser.add_argument("--weeks",    type=int, default=None,
                        metavar="N",  help="최근 N주 데이터만 사용 (기본: 전체)")
    args = parser.parse_args()

    run(weeks_back=args.weeks, apply=args.apply)
