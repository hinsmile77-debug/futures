# scripts/build_triple_barrier_labels.py — v9 처방 P1 검증
"""
트리플 배리어 라벨(model/triple_barrier_label.py)을 raw_candles 최근 N일에 적용하고,
기존 운영 라벨(learning/batch_retrainer._path_conditioned_label — HORIZON_THRESHOLDS +
PATH_LABEL_RATIO_BY_HZ 기반)과 병렬 비교한다.

이 스크립트는 운영 파이프라인을 건드리지 않는다 (오프라인 비교 전용, W1 Phase 0).
비교 결과가 기대대로(손절/익절 구조 반영, FLAT 과다 완화 등)면 W2~3에서
batch_retrainer 학습 경로 편입을 검토한다.

출력: triple_barrier_label_report.md, triple_barrier_label_metrics.json (ROOT)
      + raw_data.db.triple_barrier_labels 테이블 저장
"""
import json
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import RAW_DATA_DB, HORIZONS, HORIZON_THRESHOLDS
from learning.batch_retrainer import _path_conditioned_label, PATH_LABEL_RATIO_BY_HZ
from model.triple_barrier_label import (
    build_triple_barrier_labels_for_horizon,
    DEFAULT_STOP_MULT, DEFAULT_PROFIT_MULT,
)
from utils.db_utils import init_raw_data_db, save_triple_barrier_labels

REPORT_PATH = ROOT / "triple_barrier_label_report.md"
METRICS_PATH = ROOT / "triple_barrier_label_metrics.json"

LOOKBACK_DAYS = 30
LABEL_NAMES = {1: "UP", -1: "DOWN", 0: "FLAT"}


def _load_candles(since_ts: str):
    with sqlite3.connect(RAW_DATA_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT ts, high, low, close FROM raw_candles WHERE ts >= ? ORDER BY ts",
            (since_ts,),
        ).fetchall()
    return [dict(r) for r in rows]


def _pct(counter: Counter, total: int) -> dict:
    if total == 0:
        return {}
    return {k: round(v / total, 4) for k, v in counter.items()}


def _compare_horizon(candles, close_map, h_name, h_min):
    threshold = HORIZON_THRESHOLDS.get(h_name, 0.0003)
    path_ratio = PATH_LABEL_RATIO_BY_HZ.get(h_name, 0.55)

    tb_labels = build_triple_barrier_labels_for_horizon(
        candles, h_min, stop_mult=DEFAULT_STOP_MULT, profit_mult=DEFAULT_PROFIT_MULT,
    )
    tb_by_ts = {lbl["ts"]: lbl for lbl in tb_labels}

    tb_counter = Counter()
    touch_counter = Counter()
    old_counter = Counter()
    agree = 0
    compared = 0
    ret_by_label = {1: [], -1: [], 0: []}

    for ts, lbl in tb_by_ts.items():
        tb_counter[lbl["label"]] += 1
        touch_counter[lbl["touch_type"]] += 1
        ret_by_label[lbl["label"]].append(lbl["realized_ret"])

        old_label = _path_conditioned_label(close_map, ts, h_min, threshold, path_ratio)
        old_counter[old_label] += 1
        compared += 1
        if old_label == lbl["label"]:
            agree += 1

    n = len(tb_labels)
    return {
        "horizon": h_name,
        "n": n,
        "triple_barrier_dist": {LABEL_NAMES[k]: v for k, v in _pct(tb_counter, n).items()},
        "path_conditioned_dist": {LABEL_NAMES[k]: v for k, v in _pct(old_counter, compared).items()},
        "touch_type_dist": _pct(touch_counter, n),
        "agreement_rate": round(agree / compared, 4) if compared else None,
        "mean_realized_ret_by_label": {
            LABEL_NAMES[k]: round(sum(v) / len(v), 6) if v else None
            for k, v in ret_by_label.items()
        },
        "stop_mult": DEFAULT_STOP_MULT,
        "profit_mult": DEFAULT_PROFIT_MULT,
    }, tb_labels


def build_report(metrics: dict) -> str:
    lines = [
        "# Triple-Barrier Label Report (v9 처방 P1)",
        "",
        f"- Generated at: {metrics['generated_at']}",
        f"- 조회 구간: 최근 {metrics['lookback_days']}일 ({metrics['since_ts']} ~)",
        f"- 배리어: stop={DEFAULT_STOP_MULT}×ATR, profit={DEFAULT_PROFIT_MULT}×ATR "
        f"(손익비 목표 {DEFAULT_PROFIT_MULT / DEFAULT_STOP_MULT:.1f})",
        "",
        "## 호라이즌별 비교 (트리플 배리어 vs 기존 path-conditioned 라벨)",
        "",
    ]
    for h in metrics["by_horizon"]:
        lines += [
            f"### {h['horizon']}  (n={h['n']})",
            f"- 트리플배리어 분포: {h['triple_barrier_dist']}",
            f"- 기존 라벨 분포:     {h['path_conditioned_dist']}",
            f"- 터치 유형 분포(upper/lower/time): {h['touch_type_dist']}",
            f"- 두 라벨 일치율: {h['agreement_rate']}",
            f"- 라벨별 평균 실현 수익률: {h['mean_realized_ret_by_label']}",
            "",
        ]
    lines += [
        "---",
        "",
        "## 해석 가이드",
        "",
        "- `touch_type_dist`의 `time` 비율이 높을수록 배리어가 거의 닿지 않아 두 라벨링 방식의 차이가 작다는 뜻.",
        "- `agreement_rate`가 낮을수록(특히 장기 호라이즌) 기존 라벨이 실제 손절/익절 구조와 괴리되어 왔다는 근거가 강해짐.",
        "- 다음 단계(W2~3): 이 트리플 배리어 라벨로 병렬 재학습 후 walk-forward 손익비 비교.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    init_raw_data_db()  # triple_barrier_labels 테이블 최초 실행 시 생성
    since_ts = (datetime.now() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d 00:00:00")
    candles = _load_candles(since_ts)
    if not candles:
        print("validation=FAIL (no raw_candles rows in lookback window)")
        return 1

    close_map = {c["ts"]: c["close"] for c in candles}

    by_horizon = []
    for h_name, h_min in HORIZONS.items():
        stat, tb_labels = _compare_horizon(candles, close_map, h_name, h_min)
        by_horizon.append(stat)
        save_triple_barrier_labels(h_name, tb_labels, DEFAULT_STOP_MULT, DEFAULT_PROFIT_MULT)

    metrics = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lookback_days": LOOKBACK_DAYS,
        "since_ts": since_ts,
        "candle_count": len(candles),
        "by_horizon": by_horizon,
    }

    REPORT_PATH.write_text(build_report(metrics), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"saved_report={REPORT_PATH}")
    print(f"saved_metrics={METRICS_PATH}")
    print(f"candle_count={len(candles)}")
    for h in by_horizon:
        print(
            f"{h['horizon']}: n={h['n']} agreement={h['agreement_rate']} "
            f"tb_dist={h['triple_barrier_dist']} touch={h['touch_type_dist']}"
        )
    print("validation=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
