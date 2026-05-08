import json
import re
import sqlite3
import sys
from pathlib import Path


MICRO_MINUTE_RE = re.compile(
    r"\[MICRO-MINUTE\] #\d+ ts=(.+?) close=([0-9.]+) mp=([\-0-9.]+) bias=([\-0-9.]+) "
    r"slope=([\-0-9.]+) depth_bias=([\-0-9.]+) mlofi_norm=([\-0-9.]+) mlofi_pressure=([\-0-9.]+) "
    r"mlofi_slope=([\-0-9.]+) queue_signal=([\-0-9.]+) queue_ma=([\-0-9.]+) queue_momentum=([\-0-9.]+) "
    r"depletion=([\-0-9.]+) refill=([\-0-9.]+) imbalance_slope=([\-0-9.]+) cancel_add=([\-0-9.]+)"
)

FIELDS = [
    ("microprice", 3),
    ("microprice_bias", 4),
    ("microprice_slope", 5),
    ("microprice_depth_bias", 6),
    ("mlofi_norm", 7),
    ("mlofi_pressure", 8),
    ("mlofi_slope", 9),
    ("queue_signal", 10),
    ("queue_signal_ma", 11),
    ("queue_momentum", 12),
    ("queue_depletion_speed", 13),
    ("queue_refill_rate", 14),
    ("imbalance_slope", 15),
    ("cancel_add_ratio", 16),
]


def load_micro_minutes(path: Path, after_last_probe: bool = True):
    rows = {}
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if after_last_probe:
        last_probe_idx = -1
        for idx, line in enumerate(lines):
            if "probe micro line" in line:
                last_probe_idx = idx
        if last_probe_idx >= 0:
            lines = lines[last_probe_idx + 1 :]

    for line in lines:
            m = MICRO_MINUTE_RE.search(line)
            if not m:
                continue
            ts = m.group(1).strip()
            row = {}
            for name, group_idx in FIELDS:
                row[name] = float(m.group(group_idx))
            rows[ts] = row
    return rows


def load_raw_features(db_path: Path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = {}
    for row in cur.execute("SELECT ts, features FROM raw_features ORDER BY ts ASC"):
        feat = json.loads(row["features"])
        rows[row["ts"]] = {name: float(feat.get(name, 0.0)) for name, _ in FIELDS}
    conn.close()
    return rows


def main() -> int:
    if len(sys.argv) not in (3, 4, 5):
        print("usage: python scripts/compare_micro_vs_raw_features.py <MICRO.log> <raw_data.db> [tolerance] [after_last_probe:true|false]")
        return 2

    micro_path = Path(sys.argv[1])
    db_path = Path(sys.argv[2])
    tolerance = float(sys.argv[3]) if len(sys.argv) >= 4 else 1e-6
    after_last_probe = True
    if len(sys.argv) == 5:
        after_last_probe = sys.argv[4].lower() != "false"

    if not micro_path.exists():
        print(f"missing MICRO log: {micro_path}")
        return 2
    if not db_path.exists():
        print(f"missing db: {db_path}")
        return 2

    micro_rows = load_micro_minutes(micro_path, after_last_probe=after_last_probe)
    db_rows = load_raw_features(db_path)
    shared_ts = sorted(set(micro_rows) & set(db_rows))

    print(f"micro_minutes={len(micro_rows)}")
    print(f"raw_feature_rows={len(db_rows)}")
    print(f"shared_timestamps={len(shared_ts)}")
    print(f"tolerance={tolerance}")
    print(f"after_last_probe={after_last_probe}")

    if not shared_ts:
        print("validation=FAIL (no shared timestamps)")
        return 1

    mismatches = []
    for ts in shared_ts:
        for field, _ in FIELDS:
            a = micro_rows[ts][field]
            b = db_rows[ts][field]
            if abs(a - b) > tolerance:
                mismatches.append((ts, field, a, b, abs(a - b)))

    if mismatches:
        print(f"mismatch_count={len(mismatches)}")
        for ts, field, a, b, diff in mismatches[:20]:
            print(f"mismatch ts={ts} field={field} micro={a} db={b} diff={diff}")
        print("validation=FAIL (micro log and raw_features diverge)")
        return 1

    print("validation=PASS (micro log matches raw_features)")
    if shared_ts:
        print(f"sample_ts={shared_ts[-1]}")
        print({field: micro_rows[shared_ts[-1]][field] for field, _ in FIELDS})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
