import re
import sys
from collections import Counter
from pathlib import Path


MINUTE_RE = re.compile(
    r"\[MICRO-MINUTE\] #(\d+) ts=(.+?) close=([0-9.]+) mp=([\-0-9.]+) bias=([\-0-9.]+) "
    r"slope=([\-0-9.]+) depth_bias=([\-0-9.]+) mlofi_norm=([\-0-9.]+) mlofi_pressure=([\-0-9.]+) "
    r"mlofi_slope=([\-0-9.]+) queue_signal=([\-0-9.]+) queue_ma=([\-0-9.]+) queue_momentum=([\-0-9.]+) "
    r"depletion=([\-0-9.]+) refill=([\-0-9.]+) imbalance_slope=([\-0-9.]+) cancel_add=([\-0-9.]+)"
)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/validate_micro_log.py <MICRO.log>")
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"missing log file: {path}")
        return 2

    tick_count = 0
    minute_count = 0
    minute_nonzero = Counter()
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if "[MICRO-TICK]" in line:
                tick_count += 1
            mm = MINUTE_RE.search(line)
            if not mm:
                continue
            minute_count += 1
            names = [
                "mp", "bias", "slope", "depth_bias", "mlofi_norm", "mlofi_pressure",
                "mlofi_slope", "queue_signal", "queue_ma", "queue_momentum",
                "depletion", "refill", "imbalance_slope", "cancel_add",
            ]
            values = [float(mm.group(i)) for i in range(4, 18)]
            for name, value in zip(names, values):
                if value != 0.0:
                    minute_nonzero[name] += 1

    print(f"log={path}")
    print(f"micro_tick_lines={tick_count}")
    print(f"micro_minute_lines={minute_count}")
    print(f"nonzero_minute_fields={dict(sorted(minute_nonzero.items()))}")

    if tick_count > 0 and minute_count > 0:
        print("validation=PASS (tick/minute microstructure logs observed)")
        return 0
    if tick_count > 0:
        print("validation=PARTIAL (tick logs only; wait for minute flush)")
        return 1

    print("validation=FAIL (no usable microstructure logs observed)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
