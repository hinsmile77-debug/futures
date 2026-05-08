import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import PREDICTIONS_DB


def main() -> int:
    limit = int(sys.argv[1]) if len(sys.argv) >= 2 else 300
    with sqlite3.connect(PREDICTIONS_DB) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT ts, regime, micro_regime, direction, confidence, grade,
                   gate_reason, gate_strength, gate_delta, gate_blocked, gate_signals,
                   meta_action, meta_confidence, meta_size_mult,
                   toxicity_action, toxicity_score, toxicity_score_ma, toxicity_size_mult
            FROM ensemble_decisions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    print(f"rows={len(rows)}")
    if not rows:
        print("validation=FAIL (no ensemble_decisions rows)")
        return 1

    reason_counter = Counter()
    blocked = 0
    strengths = []
    micro_counter = Counter()
    toxicity_counter = Counter()
    for row in rows:
        reason_counter[row["gate_reason"] or ""] += 1
        micro_counter[row["micro_regime"] or ""] += 1
        toxicity_counter[row["toxicity_action"] or ""] += 1
        blocked += int(row["gate_blocked"] or 0)
        strengths.append(float(row["gate_strength"] or 0.0))

    print(f"gate_reasons={dict(reason_counter)}")
    print(f"micro_regimes={dict(micro_counter)}")
    print(f"toxicity_actions={dict(toxicity_counter)}")
    print(f"blocked={blocked}")
    print(f"avg_gate_strength={round(mean(strengths), 6)}")
    print(f"max_abs_gate_strength={round(max(abs(x) for x in strengths), 6)}")
    print("latest_rows=")
    for row in rows[:5]:
        print({
            "ts": row["ts"],
            "regime": row["regime"],
            "micro_regime": row["micro_regime"],
            "direction": row["direction"],
            "confidence": row["confidence"],
            "grade": row["grade"],
            "gate_reason": row["gate_reason"],
            "gate_strength": row["gate_strength"],
            "gate_delta": row["gate_delta"],
            "gate_blocked": row["gate_blocked"],
            "meta_action": row["meta_action"],
            "meta_confidence": row["meta_confidence"],
            "meta_size_mult": row["meta_size_mult"],
            "toxicity_action": row["toxicity_action"],
            "toxicity_score": row["toxicity_score"],
            "toxicity_score_ma": row["toxicity_score_ma"],
            "toxicity_size_mult": row["toxicity_size_mult"],
            "signals": json.loads(row["gate_signals"] or "{}"),
        })
    print("validation=PASS (ensemble gating telemetry observed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
