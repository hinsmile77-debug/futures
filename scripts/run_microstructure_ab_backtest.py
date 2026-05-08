import json
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import ENSEMBLE_WEIGHTS, PREDICTIONS_DB, RAW_DATA_DB
from config.constants import DIRECTION_DOWN, DIRECTION_FLAT, DIRECTION_UP
from model.ensemble_decision import EnsembleDecision


REPORT_PATH = ROOT / "microstructure_ab_report.md"
METRICS_PATH = ROOT / "microstructure_ab_metrics.json"
HORIZON_MINUTES = {"1m": 1, "3m": 3, "5m": 5, "10m": 10, "15m": 15, "30m": 30}


def fetch_predictions():
    with sqlite3.connect(PREDICTIONS_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT ts, horizon, direction, confidence, up_prob, down_prob, flat_prob, actual, features
            FROM predictions
            WHERE actual IS NOT NULL
            ORDER BY ts ASC, horizon ASC
            """
        ).fetchall()
    grouped = defaultdict(dict)
    for row in rows:
        grouped[row["ts"]][row["horizon"]] = dict(row)
    return grouped


def fetch_close_map():
    with sqlite3.connect(RAW_DATA_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT ts, close FROM raw_candles ORDER BY ts ASC").fetchall()
    return {row["ts"]: float(row["close"]) for row in rows}


def reconstruct_prob(direction: int, confidence: float, up_prob=None, down_prob=None, flat_prob=None):
    if up_prob is not None and down_prob is not None and flat_prob is not None:
        try:
            up = max(float(up_prob), 0.0)
            down = max(float(down_prob), 0.0)
            flat = max(float(flat_prob), 0.0)
            total = up + down + flat
            if total > 0:
                up, down, flat = up / total, down / total, flat / total
                best_dir = max(((up, DIRECTION_UP), (down, DIRECTION_DOWN), (flat, DIRECTION_FLAT)), key=lambda x: x[0])[1]
                return {
                    "up": round(up, 6),
                    "down": round(down, 6),
                    "flat": round(flat, 6),
                    "direction": best_dir,
                    "confidence": round(max(up, down, flat), 6),
                }
        except (TypeError, ValueError):
            pass

    confidence = min(max(float(confidence or (1 / 3)), 1 / 3), 1.0)
    side = max(0.0, 1.0 - confidence) / 2.0
    if direction == DIRECTION_UP:
        return {"up": confidence, "down": side, "flat": side, "direction": direction, "confidence": confidence}
    if direction == DIRECTION_DOWN:
        return {"up": side, "down": confidence, "flat": side, "direction": direction, "confidence": confidence}
    return {"up": side, "down": side, "flat": confidence, "direction": direction, "confidence": confidence}


def next_ts(ts: str, horizon: str) -> str:
    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    return (dt + timedelta(minutes=HORIZON_MINUTES[horizon])).strftime("%Y-%m-%d %H:%M:%S")


def compute_trade_pnl(direction: int, entry_close: float, exit_close: float) -> float:
    if direction == DIRECTION_UP:
        return exit_close - entry_close
    if direction == DIRECTION_DOWN:
        return entry_close - exit_close
    return 0.0


def evaluate(samples):
    active = [s for s in samples if s["decision"]["direction"] != DIRECTION_FLAT]
    pnl_pts = [s["pnl_pts"] for s in active]
    wins = sum(1 for s in active if s["pnl_pts"] > 0)
    correct = sum(1 for s in active if s["decision"]["direction"] == s["actual"])
    return {
        "samples": len(samples),
        "entries": len(active),
        "coverage": round(len(active) / len(samples), 4) if samples else 0.0,
        "directional_accuracy": round(correct / len(active), 4) if active else 0.0,
        "win_rate": round(wins / len(active), 4) if active else 0.0,
        "avg_pnl_pts": round(mean(pnl_pts), 4) if pnl_pts else 0.0,
        "total_pnl_pts": round(sum(pnl_pts), 4),
        "avg_confidence": round(mean([s["decision"]["confidence"] for s in active]), 4) if active else 0.0,
    }


def build_report(metrics):
    base = metrics["baseline"]
    enh = metrics["enhanced"]
    lines = [
        "# Microstructure A/B Backtest",
        "",
        f"- Generated at: {metrics['generated_at']}",
        f"- Eval horizon: {metrics['eval_horizon']}",
        f"- Samples: {base['samples']}",
        "",
        "## Baseline",
        "",
        f"- Entries: {base['entries']} ({base['coverage']:.2%})",
        f"- Directional accuracy: {base['directional_accuracy']:.2%}",
        f"- Win rate: {base['win_rate']:.2%}",
        f"- Avg PnL: {base['avg_pnl_pts']:.4f} pt",
        f"- Total PnL: {base['total_pnl_pts']:.4f} pt",
        "",
        "## Enhanced",
        "",
        f"- Entries: {enh['entries']} ({enh['coverage']:.2%})",
        f"- Directional accuracy: {enh['directional_accuracy']:.2%}",
        f"- Win rate: {enh['win_rate']:.2%}",
        f"- Avg PnL: {enh['avg_pnl_pts']:.4f} pt",
        f"- Total PnL: {enh['total_pnl_pts']:.4f} pt",
        f"- Changed vs baseline: {metrics['changed_count']}",
        f"- Flat conversions: {metrics['flat_conversions']}",
        f"- Gater blocks: {metrics['blocked_count']}",
        "",
        "## Delta",
        "",
        f"- Entries delta: {enh['entries'] - base['entries']}",
        f"- Accuracy delta: {enh['directional_accuracy'] - base['directional_accuracy']:+.4f}",
        f"- Win rate delta: {enh['win_rate'] - base['win_rate']:+.4f}",
        f"- Avg PnL delta: {enh['avg_pnl_pts'] - base['avg_pnl_pts']:+.4f} pt",
        f"- Total PnL delta: {enh['total_pnl_pts'] - base['total_pnl_pts']:+.4f} pt",
        "",
        "## Sample Changes",
        "",
    ]
    for row in metrics["changed_examples"][:15]:
        lines.append(
            f"- {row['ts']}: base={row['baseline_direction']}({row['baseline_confidence']:.2%}) "
            f"-> enhanced={row['enhanced_direction']}({row['enhanced_confidence']:.2%}) "
            f"actual={row['actual']} pnl={row['enhanced_pnl_pts']:.4f} "
            f"gate={row['gate_reason']} strength={row['gate_strength']:.4f}"
        )
    return "\n".join(lines) + "\n"


def main():
    eval_horizon = sys.argv[1] if len(sys.argv) >= 2 else "5m"
    if eval_horizon not in HORIZON_MINUTES:
        raise SystemExit(f"unsupported eval horizon: {eval_horizon}")

    grouped = fetch_predictions()
    close_map = fetch_close_map()
    ensemble = EnsembleDecision()
    baseline_samples = []
    enhanced_samples = []
    changed_examples = []
    changed_count = 0
    flat_conversions = 0
    blocked_count = 0

    for ts, rows in grouped.items():
        if any(h not in rows for h in ENSEMBLE_WEIGHTS):
            continue
        if rows[eval_horizon]["actual"] is None:
            continue

        exit_ts = next_ts(ts, eval_horizon)
        if ts not in close_map or exit_ts not in close_map:
            continue

        try:
            features = json.loads(rows[eval_horizon]["features"] or "{}")
        except (TypeError, ValueError):
            features = {}

        horizon_proba = {
            h: reconstruct_prob(
                rows[h]["direction"],
                rows[h]["confidence"],
                rows[h].get("up_prob"),
                rows[h].get("down_prob"),
                rows[h].get("flat_prob"),
            )
            for h in ENSEMBLE_WEIGHTS
        }
        baseline = ensemble.compute(horizon_proba, "NEUTRAL", adaptive_gating=False)
        enhanced = ensemble.compute(horizon_proba, "NEUTRAL", features=features, adaptive_gating=True)

        actual = int(rows[eval_horizon]["actual"])
        entry_close = close_map[ts]
        exit_close = close_map[exit_ts]
        base_pnl = compute_trade_pnl(baseline["direction"], entry_close, exit_close)
        enh_pnl = compute_trade_pnl(enhanced["direction"], entry_close, exit_close)

        baseline_samples.append({"ts": ts, "actual": actual, "decision": baseline, "pnl_pts": base_pnl})
        enhanced_samples.append({"ts": ts, "actual": actual, "decision": enhanced, "pnl_pts": enh_pnl})

        changed = (
            baseline["direction"] != enhanced["direction"]
            or abs(float(baseline["confidence"]) - float(enhanced["confidence"])) > 1e-9
        )
        if changed:
            changed_count += 1
            if baseline["direction"] != DIRECTION_FLAT and enhanced["direction"] == DIRECTION_FLAT:
                flat_conversions += 1
            changed_examples.append({
                "ts": ts,
                "baseline_direction": baseline["direction"],
                "baseline_confidence": baseline["confidence"],
                "enhanced_direction": enhanced["direction"],
                "enhanced_confidence": enhanced["confidence"],
                "actual": actual,
                "enhanced_pnl_pts": enh_pnl,
                "gate_reason": enhanced.get("gating", {}).get("reason"),
                "gate_strength": enhanced.get("gating", {}).get("gate_strength", 0.0),
            })
        if enhanced.get("gating", {}).get("blocked"):
            blocked_count += 1

    metrics = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "eval_horizon": eval_horizon,
        "baseline": evaluate(baseline_samples),
        "enhanced": evaluate(enhanced_samples),
        "changed_count": changed_count,
        "flat_conversions": flat_conversions,
        "blocked_count": blocked_count,
        "changed_examples": changed_examples,
    }
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(build_report(metrics), encoding="utf-8")
    print(f"Wrote {METRICS_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
