import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime
from glob import glob
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import PREDICTIONS_DB, TIME_ZONES, TRADES_DB


METRICS_PATH = ROOT / "baseline_metrics.json"
REPORT_PATH = ROOT / "baseline_ensemble_report.md"
CHECKLIST_RE = re.compile(r"\[Checklist\] 통과 (\d+)/9 → 등급 ([A-Z])")


def fetch_rows(db_path: str, sql: str, params=()):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(sql, params).fetchall()


def get_trade_rows(limit: int = 20):
    return fetch_rows(
        TRADES_DB,
        """
        SELECT entry_ts, exit_ts, direction, entry_price, exit_price, quantity,
               pnl_pts, pnl_krw, exit_reason, grade, regime
        FROM trades
        WHERE exit_ts IS NOT NULL
        ORDER BY entry_ts DESC
        LIMIT ?
        """,
        (limit,),
    )


def get_prediction_rows():
    return fetch_rows(
        PREDICTIONS_DB,
        """
        SELECT ts, horizon, direction, confidence, actual, correct
        FROM predictions
        WHERE actual IS NOT NULL
        ORDER BY ts DESC
        """,
    )


def assign_time_zone(ts_text: str) -> str:
    dt = datetime.strptime(ts_text, "%Y-%m-%d %H:%M:%S")
    hm = dt.strftime("%H:%M")
    for zone, (start, end) in TIME_ZONES.items():
        if start <= hm < end:
            return zone
    return "OTHER"


def summarize_trades(rows):
    rows = list(rows)
    pnl_pts = [float(r["pnl_pts"] or 0.0) for r in rows]
    pnl_krw = [float(r["pnl_krw"] or 0.0) for r in rows]
    wins = sum(1 for x in pnl_pts if x > 0)
    zones = defaultdict(list)
    for row in rows:
        zones[assign_time_zone(row["entry_ts"])].append(float(row["pnl_pts"] or 0.0))

    zone_stats = {}
    for zone, values in zones.items():
        zone_stats[zone] = {
            "count": len(values),
            "win_rate": round(sum(1 for v in values if v > 0) / len(values), 4),
            "avg_pnl_pts": round(mean(values), 4),
        }

    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for value in reversed(pnl_pts):
        cumulative += value
        peak = max(peak, cumulative)
        max_drawdown = min(max_drawdown, cumulative - peak)

    return {
        "count": len(rows),
        "wins": wins,
        "win_rate": round(wins / len(rows), 4) if rows else 0.0,
        "avg_pnl_pts": round(mean(pnl_pts), 4) if pnl_pts else 0.0,
        "total_pnl_pts": round(sum(pnl_pts), 4),
        "total_pnl_krw": round(sum(pnl_krw), 0),
        "profit_factor": round(
            sum(x for x in pnl_pts if x > 0) / abs(sum(x for x in pnl_pts if x < 0)),
            4,
        ) if any(x < 0 for x in pnl_pts) else None,
        "max_drawdown_pts": round(max_drawdown, 4),
        "time_zone_stats": zone_stats,
    }


def summarize_predictions(rows):
    per_horizon = defaultdict(list)
    calibration_bins = defaultdict(list)
    for row in rows:
        per_horizon[row["horizon"]].append(row)
        conf = float(row["confidence"] or 0.0)
        bucket = int(conf * 20) * 5
        calibration_bins[bucket].append(int(row["correct"] or 0))

    horizon_stats = {}
    for horizon, items in sorted(per_horizon.items()):
        horizon_stats[horizon] = {
            "count": len(items),
            "accuracy": round(mean([int(x["correct"]) for x in items]), 4),
            "avg_confidence": round(mean([float(x["confidence"] or 0.0) for x in items]), 4),
        }

    calibration = []
    for bucket in sorted(calibration_bins):
        values = calibration_bins[bucket]
        calibration.append({
            "conf_bin": bucket,
            "count": len(values),
            "accuracy": round(mean(values), 4),
        })

    return {
        "count": len(rows),
        "per_horizon": horizon_stats,
        "calibration": calibration,
    }


def summarize_checklist_logs():
    counts = Counter()
    grades = Counter()
    for path in sorted(glob(str(ROOT / "logs" / "*_SIGNAL.log"))):
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                m = CHECKLIST_RE.search(line)
                if not m:
                    continue
                counts[int(m.group(1))] += 1
                grades[m.group(2)] += 1
    return {
        "pass_count_distribution": dict(sorted(counts.items())),
        "grade_distribution": dict(sorted(grades.items())),
    }


def to_plain_rows(rows):
    return [{k: row[k] for k in row.keys()} for row in rows]


def build_report(metrics):
    trade_rows = metrics["last_20_trades"]
    horizon_stats = metrics["prediction_summary"]["per_horizon"]
    calibration = metrics["prediction_summary"]["calibration"]
    checklist = metrics["checklist_summary"]
    trade_summary = metrics["trade_summary"]

    lines = [
        "# Baseline Ensemble Report",
        "",
        f"- Generated at: {metrics['generated_at']}",
        f"- Source trade sample: last {trade_summary['count']} closed trades",
        f"- Verified predictions: {metrics['prediction_summary']['count']}",
        "",
        "## Trade Summary",
        "",
        f"- Win rate: {trade_summary['win_rate']:.2%}",
        f"- Avg PnL: {trade_summary['avg_pnl_pts']:.4f} pt",
        f"- Total PnL: {trade_summary['total_pnl_pts']:.4f} pt / {trade_summary['total_pnl_krw']:.0f} KRW",
        f"- Profit factor: {trade_summary['profit_factor']}",
        f"- Max drawdown (sample): {trade_summary['max_drawdown_pts']:.4f} pt",
        "",
        "## Horizon Accuracy",
        "",
    ]

    for horizon, stats in horizon_stats.items():
        lines.append(
            f"- {horizon}: acc={stats['accuracy']:.2%}, avg_conf={stats['avg_confidence']:.2%}, n={stats['count']}"
        )

    lines += [
        "",
        "## Calibration",
        "",
    ]
    for item in calibration:
        lines.append(
            f"- {item['conf_bin']:02d}-{item['conf_bin'] + 4:02d}%: acc={item['accuracy']:.2%}, n={item['count']}"
        )

    lines += [
        "",
        "## Time Zone Stats",
        "",
    ]
    for zone, stats in sorted(trade_summary["time_zone_stats"].items()):
        lines.append(
            f"- {zone}: win_rate={stats['win_rate']:.2%}, avg_pnl={stats['avg_pnl_pts']:.4f} pt, n={stats['count']}"
        )

    lines += [
        "",
        "## Checklist Distribution",
        "",
        f"- Pass counts: {json.dumps(checklist['pass_count_distribution'], ensure_ascii=False)}",
        f"- Grades: {json.dumps(checklist['grade_distribution'], ensure_ascii=False)}",
        "",
        "## Last 20 Trades",
        "",
    ]

    for row in trade_rows:
        lines.append(
            f"- {row['entry_ts']} {row['direction']} grade={row['grade']} pnl={row['pnl_pts']} pt reason={row['exit_reason']}"
        )

    return "\n".join(lines) + "\n"


def main():
    trade_rows = get_trade_rows(limit=20)
    prediction_rows = get_prediction_rows()
    metrics = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "trade_summary": summarize_trades(trade_rows),
        "prediction_summary": summarize_predictions(prediction_rows),
        "checklist_summary": summarize_checklist_logs(),
        "last_20_trades": to_plain_rows(trade_rows),
    }

    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(build_report(metrics), encoding="utf-8")
    print(f"Wrote {METRICS_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
