import json
import math
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import PREDICTIONS_DB
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT


REPORT_PATH = ROOT / "calibration_report.md"
METRICS_PATH = ROOT / "calibration_metrics.json"


def safe_probs(row):
    up = max(float(row["up_prob"] or 0.0), 0.0)
    down = max(float(row["down_prob"] or 0.0), 0.0)
    flat = max(float(row["flat_prob"] or 0.0), 0.0)
    total = up + down + flat
    if total <= 0:
        return 1 / 3, 1 / 3, 1 / 3
    return up / total, down / total, flat / total


def actual_prob(actual, up, down, flat):
    if actual == DIRECTION_UP:
        return up
    if actual == DIRECTION_DOWN:
        return down
    return flat


def ece_from_rows(rows, bins=10):
    if not rows:
        return 0.0, []
    bucketed = defaultdict(list)
    for row in rows:
        conf = float(row["confidence"] or 0.0)
        idx = min(int(conf * bins), bins - 1)
        bucketed[idx].append(row)
    details = []
    total_n = len(rows)
    ece = 0.0
    for idx in sorted(bucketed):
        bucket = bucketed[idx]
        avg_conf = sum(float(r["confidence"] or 0.0) for r in bucket) / len(bucket)
        acc = sum(float(r["correct"] or 0) for r in bucket) / len(bucket)
        gap = abs(avg_conf - acc)
        ece += (len(bucket) / total_n) * gap
        details.append({
            "bin": idx,
            "count": len(bucket),
            "avg_confidence": round(avg_conf, 4),
            "accuracy": round(acc, 4),
            "gap": round(gap, 4),
        })
    return round(ece, 6), details


def summarize(rows):
    if not rows:
        return {
            "count": 0,
            "accuracy": 0.0,
            "brier": 0.0,
            "log_loss": 0.0,
            "ece": 0.0,
            "bins": [],
        }

    brier_terms = []
    log_terms = []
    for row in rows:
        up, down, flat = safe_probs(row)
        p_actual = max(actual_prob(int(row["actual"]), up, down, flat), 1e-9)
        y_up = 1.0 if int(row["actual"]) == DIRECTION_UP else 0.0
        y_down = 1.0 if int(row["actual"]) == DIRECTION_DOWN else 0.0
        y_flat = 1.0 if int(row["actual"]) == DIRECTION_FLAT else 0.0
        brier_terms.append(
            ((up - y_up) ** 2 + (down - y_down) ** 2 + (flat - y_flat) ** 2) / 3.0
        )
        log_terms.append(-math.log(p_actual))

    ece, bins = ece_from_rows(rows)
    return {
        "count": len(rows),
        "accuracy": round(sum(float(r["correct"] or 0) for r in rows) / len(rows), 4),
        "brier": round(sum(brier_terms) / len(brier_terms), 6),
        "log_loss": round(sum(log_terms) / len(log_terms), 6),
        "ece": ece,
        "bins": bins,
    }


def build_report(metrics):
    lines = [
        "# Calibration Report",
        "",
        f"- Generated at: {metrics['generated_at']}",
        f"- Total verified predictions: {metrics['overall']['count']}",
        "",
        "## Overall",
        "",
        f"- Accuracy: {metrics['overall']['accuracy']:.2%}",
        f"- Brier score: {metrics['overall']['brier']:.6f}",
        f"- Log-loss: {metrics['overall']['log_loss']:.6f}",
        f"- ECE: {metrics['overall']['ece']:.6f}",
        "",
        "## By Horizon",
        "",
    ]
    for horizon, stat in metrics["by_horizon"].items():
        lines.extend([
            f"### {horizon}",
            "",
            f"- Count: {stat['count']}",
            f"- Accuracy: {stat['accuracy']:.2%}",
            f"- Brier score: {stat['brier']:.6f}",
            f"- Log-loss: {stat['log_loss']:.6f}",
            f"- ECE: {stat['ece']:.6f}",
            "",
        ])
    lines.append("## Worst Confidence Bins")
    lines.append("")
    worst_bins = sorted(metrics["overall"]["bins"], key=lambda x: x["gap"], reverse=True)[:10]
    for item in worst_bins:
        lo = item["bin"] * 0.1
        hi = lo + 0.1
        lines.append(
            f"- {lo:.1f}~{hi:.1f}: n={item['count']} avg_conf={item['avg_confidence']:.4f} "
            f"acc={item['accuracy']:.4f} gap={item['gap']:.4f}"
        )
    return "\n".join(lines) + "\n"


def main():
    with sqlite3.connect(PREDICTIONS_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT horizon, confidence, up_prob, down_prob, flat_prob, actual, correct
            FROM predictions
            WHERE actual IS NOT NULL
            ORDER BY id ASC
            """
        ).fetchall()

    by_horizon_rows = defaultdict(list)
    for row in rows:
        by_horizon_rows[row["horizon"]].append(row)

    metrics = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall": summarize(rows),
        "by_horizon": {h: summarize(h_rows) for h, h_rows in sorted(by_horizon_rows.items())},
    }
    REPORT_PATH.write_text(build_report(metrics), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved_report={REPORT_PATH}")
    print(f"saved_metrics={METRICS_PATH}")
    print(f"overall_count={metrics['overall']['count']}")
    print(f"overall_ece={metrics['overall']['ece']}")


if __name__ == "__main__":
    main()
