import re
import sys
from collections import Counter
from pathlib import Path


LINE_RE = re.compile(r"active_levels=(\d+)/(\d+)")
LEVEL_RE = re.compile(r"L(\d+): bid=([0-9.]+)/(\d+) ask=([0-9.]+)/(\d+)")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/validate_hoga_log.py <HOGA.log>")
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"missing log file: {path}")
        return 2

    total = 0
    active_counter = Counter()
    level_seen = Counter()
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if "[HOGA]" not in line:
                continue
            total += 1
            m = LINE_RE.search(line)
            if m:
                active_counter[int(m.group(1))] += 1
            for lm in LEVEL_RE.finditer(line):
                level = int(lm.group(1))
                bid_p = float(lm.group(2))
                bid_q = int(lm.group(3))
                ask_p = float(lm.group(4))
                ask_q = int(lm.group(5))
                if any(v > 0 for v in (bid_p, bid_q, ask_p, ask_q)):
                    level_seen[level] += 1

    print(f"log={path}")
    print(f"hoga_lines={total}")
    print(f"active_level_distribution={dict(sorted(active_counter.items()))}")
    print(f"level_seen={dict(sorted(level_seen.items()))}")

    max_level = max(level_seen.keys(), default=0)
    if max_level >= 5:
        print("validation=PASS (5 levels observed)")
        return 0
    if max_level > 0:
        print(f"validation=PARTIAL (observed up to level {max_level})")
        return 1

    print("validation=FAIL (no usable hoga levels observed)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
