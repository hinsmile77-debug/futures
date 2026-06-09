import json
import math
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import PREDICTIONS_DB
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT


REPORT_PATH  = ROOT / "calibration_report.md"
METRICS_PATH = ROOT / "calibration_metrics.json"

# Platt 보정기 도입일 (110차, 2026-06-04). 이 날 이후 데이터가 calibrated conf 기반.
PLATT_SINCE = "2026-06-04 00:00:00"
# 최근 N일 단기 분석 창 (오늘 기준)
RECENT_DAYS = 30


def safe_probs(row):
    up   = max(float(row["up_prob"]   or 0.0), 0.0)
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
        idx  = min(int(conf * bins), bins - 1)
        bucketed[idx].append(row)
    details   = []
    total_n   = len(rows)
    ece       = 0.0
    for idx in sorted(bucketed):
        bucket   = bucketed[idx]
        avg_conf = sum(float(r["confidence"] or 0.0) for r in bucket) / len(bucket)
        acc      = sum(float(r["correct"]    or 0)   for r in bucket) / len(bucket)
        gap      = abs(avg_conf - acc)
        ece     += (len(bucket) / total_n) * gap
        details.append({
            "bin":            idx,
            "count":          len(bucket),
            "avg_confidence": round(avg_conf, 4),
            "accuracy":       round(acc, 4),
            "gap":            round(gap, 4),
        })
    return round(ece, 6), details


def summarize(rows):
    if not rows:
        return {
            "count": 0, "accuracy": 0.0, "brier": 0.0,
            "log_loss": 0.0, "ece": 0.0, "bins": [],
        }
    brier_terms = []
    log_terms   = []
    for row in rows:
        up, down, flat = safe_probs(row)
        p_actual = max(actual_prob(int(row["actual"]), up, down, flat), 1e-9)
        y_up   = 1.0 if int(row["actual"]) == DIRECTION_UP   else 0.0
        y_down = 1.0 if int(row["actual"]) == DIRECTION_DOWN else 0.0
        y_flat = 1.0 if int(row["actual"]) == DIRECTION_FLAT else 0.0
        brier_terms.append(
            ((up - y_up) ** 2 + (down - y_down) ** 2 + (flat - y_flat) ** 2) / 3.0
        )
        log_terms.append(-math.log(p_actual))

    ece, bins = ece_from_rows(rows)
    return {
        "count":    len(rows),
        "accuracy": round(sum(float(r["correct"] or 0) for r in rows) / len(rows), 4),
        "brier":    round(sum(brier_terms) / len(brier_terms), 6),
        "log_loss": round(sum(log_terms)   / len(log_terms),   6),
        "ece":      ece,
        "bins":     bins,
    }


def _worst_bins_text(bins, n=7):
    worst = sorted(bins, key=lambda x: x["gap"], reverse=True)[:n]
    lines = []
    for item in worst:
        lo = item["bin"] * 0.1
        hi = lo + 0.1
        lines.append(
            f"- {lo:.1f}~{hi:.1f}: n={item['count']} avg_conf={item['avg_confidence']:.4f} "
            f"acc={item['accuracy']:.4f} gap={item['gap']:.4f}"
        )
    return lines


def build_report(metrics):
    lines = [
        "# Calibration Report",
        "",
        f"- Generated at: {metrics['generated_at']}",
        f"- Platt 보정기 도입 이후(since {PLATT_SINCE[:10]}) 검증 예측: "
        f"{metrics['recent']['overall']['count']}건",
        f"- 전체 누적 검증 예측: {metrics['all']['overall']['count']}건",
        "",
        "## 최근 (Platt 보정 이후) — 현재 모델 성능 기준",
        "",
        f"- Accuracy: {metrics['recent']['overall']['accuracy']:.2%}",
        f"- Brier score: {metrics['recent']['overall']['brier']:.6f}",
        f"- Log-loss: {metrics['recent']['overall']['log_loss']:.6f}",
        f"- ECE: {metrics['recent']['overall']['ece']:.6f}",
        "",
        "### 호라이즌별 (최근)",
        "",
    ]
    for horizon, stat in metrics["recent"]["by_horizon"].items():
        lines.extend([
            f"#### {horizon}",
            f"- Count: {stat['count']}  Accuracy: {stat['accuracy']:.2%}  "
            f"Brier: {stat['brier']:.6f}  ECE: {stat['ece']:.6f}",
            "",
        ])
    lines += ["### Worst Confidence Bins (최근)", ""]
    lines += _worst_bins_text(metrics["recent"]["overall"]["bins"])
    lines += [
        "",
        "---",
        "",
        "## 전체 누적 (참고용 — Platt 보정 이전 raw conf 포함)",
        "",
        f"- Accuracy: {metrics['all']['overall']['accuracy']:.2%}",
        f"- Brier score: {metrics['all']['overall']['brier']:.6f}",
        f"- Log-loss: {metrics['all']['overall']['log_loss']:.6f}",
        f"- ECE: {metrics['all']['overall']['ece']:.6f}",
        "",
        "### Worst Confidence Bins (전체)", "",
    ]
    lines += _worst_bins_text(metrics["all"]["overall"]["bins"])
    return "\n".join(lines) + "\n"


def _fetch(conn, since_ts=None):
    if since_ts:
        rows = conn.execute(
            """
            SELECT horizon, confidence, up_prob, down_prob, flat_prob, actual, correct
            FROM predictions
            WHERE actual IS NOT NULL AND ts >= ?
            ORDER BY id ASC
            """,
            (since_ts,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT horizon, confidence, up_prob, down_prob, flat_prob, actual, correct
            FROM predictions
            WHERE actual IS NOT NULL
            ORDER BY id ASC
            """
        ).fetchall()
    return rows


def main():
    with sqlite3.connect(PREDICTIONS_DB) as conn:
        conn.row_factory = sqlite3.Row
        all_rows    = _fetch(conn)
        recent_rows = _fetch(conn, since_ts=PLATT_SINCE)

    def split_by_horizon(rows):
        bh = defaultdict(list)
        for r in rows:
            bh[r["horizon"]].append(r)
        return bh

    all_bh    = split_by_horizon(all_rows)
    recent_bh = split_by_horizon(recent_rows)

    metrics = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "platt_since":  PLATT_SINCE,
        "recent": {
            "overall":    summarize(recent_rows),
            "by_horizon": {h: summarize(r) for h, r in sorted(recent_bh.items())},
        },
        "all": {
            "overall":    summarize(all_rows),
            "by_horizon": {h: summarize(r) for h, r in sorted(all_bh.items())},
        },
        # 하위 호환: 기존 키(overall/by_horizon) 유지 — 대시보드 파싱 유지
        "overall":    summarize(recent_rows),
        "by_horizon": {h: summarize(r) for h, r in sorted(recent_bh.items())},
    }

    REPORT_PATH.write_text(build_report(metrics), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"saved_report={REPORT_PATH}")
    print(f"saved_metrics={METRICS_PATH}")
    print(f"recent_count={metrics['recent']['overall']['count']}")
    print(f"recent_ece={metrics['recent']['overall']['ece']}")
    print(f"all_count={metrics['all']['overall']['count']}")
    print(f"all_ece={metrics['all']['overall']['ece']}")


if __name__ == "__main__":
    main()
