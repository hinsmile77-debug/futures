import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import PREDICTIONS_DB


REPORT_PATH = ROOT / "rollout_readiness_report.md"
METRICS_PATH = ROOT / "rollout_readiness_metrics.json"
CALIBRATION_PATH = ROOT / "calibration_metrics.json"
AB_PATH = ROOT / "microstructure_ab_metrics.json"
META_TUNE_PATH = ROOT / "meta_gate_tuning_metrics.json"


def load_json(path: Path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def fetch_gate_stats():
    with sqlite3.connect(PREDICTIONS_DB) as conn:
        conn.row_factory = sqlite3.Row
        ensemble_cnt = conn.execute("SELECT COUNT(*) AS cnt FROM ensemble_decisions").fetchone()["cnt"]
        meta_cnt = conn.execute("SELECT COUNT(*) AS cnt FROM meta_labels").fetchone()["cnt"]
        pred_cnt = conn.execute("SELECT COUNT(*) AS cnt FROM predictions WHERE actual IS NOT NULL").fetchone()["cnt"]
        return {
            "ensemble_decisions": ensemble_cnt,
            "meta_labels": meta_cnt,
            "verified_predictions": pred_cnt,
        }


def decide_stage(calib, ab, gate_stats):
    ece = float(calib.get("overall", {}).get("ece", 1.0) or 1.0)
    pnl_delta = float(ab.get("enhanced", {}).get("total_pnl_pts", 0.0) or 0.0) - float(ab.get("baseline", {}).get("total_pnl_pts", 0.0) or 0.0)
    meta_samples = int(gate_stats.get("meta_labels", 0) or 0)

    if pnl_delta > 0 and ece < 0.20 and meta_samples >= 100:
        return "small_size", "A/B 개선 확인 + calibration 양호 + meta 표본 충분"
    if pnl_delta > 0 and meta_samples >= 20:
        return "alert_only", "A/B 개선 확인, 다만 calibration 또는 meta 표본 추가 필요"
    return "shadow", "실거래 확대 전 shadow/alert 단계 유지 권장"


def build_report(metrics):
    lines = [
        "# Rollout Readiness Report",
        "",
        f"- Generated at: {metrics['generated_at']}",
        f"- Recommended stage: {metrics['recommended_stage']}",
        f"- Reason: {metrics['recommended_reason']}",
        "",
        "## Metrics",
        "",
        f"- Verified predictions: {metrics['gate_stats']['verified_predictions']}",
        f"- Ensemble decisions: {metrics['gate_stats']['ensemble_decisions']}",
        f"- Meta labels: {metrics['gate_stats']['meta_labels']}",
        f"- Overall ECE: {metrics['ece']:.6f}",
        f"- Enhanced vs baseline total PnL delta: {metrics['pnl_delta']:+.4f} pt",
        "",
        "## Checklist",
        "",
        f"- Shadow telemetry present: {'yes' if metrics['gate_stats']['ensemble_decisions'] > 0 else 'no'}",
        f"- Meta-label dataset ready: {'yes' if metrics['gate_stats']['meta_labels'] >= 20 else 'not yet'}",
        f"- Calibration report generated: {'yes' if metrics['has_calibration'] else 'no'}",
        f"- Meta tuning report generated: {'yes' if metrics['has_meta_tuning'] else 'no'}",
        "",
        "## Stage Criteria",
        "",
        "- `shadow`: telemetry/labels insufficient or calibration weak",
        "- `alert_only`: A/B improvement exists but execution evidence still limited",
        "- `small_size`: A/B positive, calibration acceptable, meta labels sufficiently accumulated",
        "- `full`: only after repeated `small_size` validation and stable drawdown control",
    ]
    return "\n".join(lines) + "\n"


def main():
    calib = load_json(CALIBRATION_PATH)
    ab = load_json(AB_PATH)
    meta = load_json(META_TUNE_PATH)
    gate_stats = fetch_gate_stats()
    recommended_stage, reason = decide_stage(calib, ab, gate_stats)
    ece = float(calib.get("overall", {}).get("ece", 1.0) or 1.0)
    pnl_delta = float(ab.get("enhanced", {}).get("total_pnl_pts", 0.0) or 0.0) - float(ab.get("baseline", {}).get("total_pnl_pts", 0.0) or 0.0)
    metrics = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recommended_stage": recommended_stage,
        "recommended_reason": reason,
        "gate_stats": gate_stats,
        "ece": ece,
        "pnl_delta": round(pnl_delta, 6),
        "has_calibration": bool(calib),
        "has_meta_tuning": bool(meta),
    }
    REPORT_PATH.write_text(build_report(metrics), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved_report={REPORT_PATH}")
    print(f"saved_metrics={METRICS_PATH}")
    print(f"recommended_stage={recommended_stage}")
    print(f"reason={reason}")


if __name__ == "__main__":
    main()
