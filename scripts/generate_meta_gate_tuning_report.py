import json
import sqlite3
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import PREDICTIONS_DB
from config.constants import DIRECTION_FLAT


REPORT_PATH = ROOT / "meta_gate_tuning_report.md"
METRICS_PATH = ROOT / "meta_gate_tuning_metrics.json"
DEFAULT_HORIZON = "5m"


def fetch_samples(horizon: str):
    with sqlite3.connect(PREDICTIONS_DB) as conn:
        conn.row_factory = sqlite3.Row
        meta_cnt = conn.execute("SELECT COUNT(*) AS cnt FROM meta_labels").fetchone()["cnt"]
        if meta_cnt > 0:
            rows = conn.execute(
                """
                SELECT ml.ts, ml.horizon, ml.meta_action AS realized_action, ml.meta_score,
                       p.correct, p.confidence, p.features
                FROM meta_labels ml
                JOIN predictions p
                  ON p.ts = ml.ts AND p.horizon = ml.horizon
                WHERE ml.horizon = ?
                ORDER BY ml.id ASC
                """,
                (horizon,),
            ).fetchall()
            return rows, "meta_labels"

        rows = conn.execute(
            """
            SELECT ed.ts, p.horizon, p.correct, p.confidence, p.features,
                   ed.meta_action, ed.meta_confidence, ed.meta_size_mult, ed.meta_reason
            FROM ensemble_decisions ed
            JOIN predictions p
              ON p.ts = ed.ts AND p.horizon = ?
            WHERE p.actual IS NOT NULL
            ORDER BY ed.id ASC
            """,
            (horizon,),
        ).fetchall()
        return rows, "ensemble_fallback"


def parse_json(text):
    try:
        return json.loads(text or "{}")
    except (TypeError, ValueError):
        return {}


def derive_proposed_action(meta_conf: float):
    if meta_conf >= 0.67:
        return "take"
    if meta_conf >= 0.56:
        return "reduce"
    return "skip"


def build_metrics(rows, source: str):
    samples = []
    for row in rows:
        features = parse_json(row["features"])
        meta_conf = float(row["meta_confidence"]) if "meta_confidence" in row.keys() and row["meta_confidence"] is not None else float(row["confidence"] or 0.0)
        if source == "meta_labels":
            realized_action = row["realized_action"]
        else:
            correct = int(row["correct"] or 0)
            conf = float(row["confidence"] or 0.0)
            if correct and conf >= 0.67:
                realized_action = "take"
            elif correct:
                realized_action = "reduce"
            else:
                realized_action = "skip"
        samples.append({
            "ts": row["ts"],
            "meta_confidence": round(meta_conf, 4),
            "realized_action": realized_action,
            "correct": int(row["correct"] or 0),
            "mlofi_norm": round(float(features.get("mlofi_norm", 0.0) or 0.0), 4),
            "microprice_bias": round(float(features.get("microprice_bias", 0.0) or 0.0), 4),
            "queue_signal": round(float(features.get("queue_signal", 0.0) or 0.0), 4),
            "cancel_add_ratio": round(float(features.get("cancel_add_ratio", 0.0) or 0.0), 4),
        })

    proposals = []
    grids = [
        (0.65, 0.54),
        (0.67, 0.56),
        (0.69, 0.58),
        (0.71, 0.60),
    ]
    for take_th, reduce_th in grids:
        matches = 0
        take_count = 0
        reduce_count = 0
        skip_count = 0
        for item in samples:
            mc = item["meta_confidence"]
            if mc >= take_th:
                action = "take"
                take_count += 1
            elif mc >= reduce_th:
                action = "reduce"
                reduce_count += 1
            else:
                action = "skip"
                skip_count += 1
            matches += int(action == item["realized_action"])
        proposals.append({
            "take_threshold": take_th,
            "reduce_threshold": reduce_th,
            "match_rate": round(matches / len(samples), 4) if samples else 0.0,
            "take_count": take_count,
            "reduce_count": reduce_count,
            "skip_count": skip_count,
        })

    action_counter = Counter(item["realized_action"] for item in samples)
    best_grid = max(proposals, key=lambda x: x["match_rate"], default={})
    return {
        "source": source,
        "count": len(samples),
        "realized_actions": dict(action_counter),
        "avg_meta_confidence": round(sum(x["meta_confidence"] for x in samples) / len(samples), 4) if samples else 0.0,
        "grid_search": proposals,
        "best_grid": best_grid,
        "latest_samples": samples[-20:],
    }


def build_report(metrics, horizon):
    lines = [
        "# Meta Gate Tuning Report",
        "",
        f"- Generated at: {metrics['generated_at']}",
        f"- Horizon: {horizon}",
        f"- Source: {metrics['source']}",
        f"- Samples: {metrics['count']}",
        "",
        "## Distribution",
        "",
        f"- Realized actions: {metrics['realized_actions']}",
        f"- Avg meta confidence: {metrics['avg_meta_confidence']:.4f}",
        "",
        "## Threshold Grid",
        "",
    ]
    for item in metrics["grid_search"]:
        lines.append(
            f"- take>={item['take_threshold']:.2f}, reduce>={item['reduce_threshold']:.2f}: "
            f"match={item['match_rate']:.2%}, take={item['take_count']}, "
            f"reduce={item['reduce_count']}, skip={item['skip_count']}"
        )
    lines.extend([
        "",
        "## Recommendation",
        "",
        f"- Best grid: take>={metrics['best_grid'].get('take_threshold', 0):.2f}, "
        f"reduce>={metrics['best_grid'].get('reduce_threshold', 0):.2f}",
        f"- Best match rate: {metrics['best_grid'].get('match_rate', 0.0):.2%}",
        "",
        "## Latest Samples",
        "",
    ])
    for item in metrics["latest_samples"][-10:]:
        lines.append(
            f"- {item['ts']}: meta_conf={item['meta_confidence']:.4f} "
            f"realized={item['realized_action']} correct={item['correct']} "
            f"mlofi={item['mlofi_norm']:.4f} mp_bias={item['microprice_bias']:.4f} "
            f"queue={item['queue_signal']:.4f} cancel_add={item['cancel_add_ratio']:.4f}"
        )
    return "\n".join(lines) + "\n"


def main():
    horizon = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HORIZON
    rows, source = fetch_samples(horizon)
    metrics = build_metrics(rows, source)
    metrics["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    REPORT_PATH.write_text(build_report(metrics, horizon), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved_report={REPORT_PATH}")
    print(f"saved_metrics={METRICS_PATH}")
    print(f"samples={metrics['count']}")
    print(f"source={source}")
    print(f"best_grid={metrics['best_grid']}")


if __name__ == "__main__":
    main()
