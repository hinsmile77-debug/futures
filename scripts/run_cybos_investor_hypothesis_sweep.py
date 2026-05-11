from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List

from scripts.check_cybos_investor_candidates import HYPOTHESES, PRESETS, run_probe


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run a cyclic sweep over Cybos investor/program ProgID hypotheses and rank interesting payloads."
    )
    parser.add_argument("--account-no", required=True, help="Signed-on Cybos account number")
    parser.add_argument(
        "--hypothesis-ids",
        nargs="*",
        default=[],
        help="Optional explicit hypothesis ids. Default runs all first-pass hypotheses.",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of sweep cycles to run",
    )
    parser.add_argument(
        "--delay-ms",
        type=int,
        default=300,
        help="Delay between probes in milliseconds",
    )
    parser.add_argument(
        "--out",
        default="logs/cybos_investor_hypothesis_sweep.json",
        help="Output JSON path",
    )
    return parser


def select_hypotheses(requested_ids: List[str]) -> List[Dict[str, str]]:
    if not requested_ids:
        return list(HYPOTHESES)
    selected = []
    for hypothesis_id in requested_ids:
        match = next((item for item in HYPOTHESES if item["id"] == hypothesis_id), None)
        if not match:
            raise ValueError("Unknown hypothesis id: {0}".format(hypothesis_id))
        selected.append(match)
    return selected


def rank_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        results,
        key=lambda item: (
            item.get("ok", False),
            item.get("analysis", {}).get("score", -1),
            item.get("analysis", {}).get("row_count", -1),
        ),
        reverse=True,
    )


def main():
    args = build_parser().parse_args()

    try:
        hypotheses = select_hypotheses(args.hypothesis_ids)
    except ValueError as exc:
        print("[FAIL]", exc)
        return 2

    all_results: List[Dict[str, Any]] = []

    for cycle_idx in range(args.cycles):
        print("[SWEEP] cycle={0}/{1}".format(cycle_idx + 1, args.cycles))
        for item in hypotheses:
            preset = PRESETS[item["preset"]]
            print(
                "[PROBE] hypothesis={0} progid={1} preset={2}".format(
                    item["id"], item["progid"], item["preset"]
                )
            )
            try:
                payload = run_probe(
                    account_no=args.account_no,
                    progid=item["progid"],
                    input_specs=list(preset.get("inputs", [])),
                    header_limit=int(preset.get("header_limit", 40)),
                    data_fields_text=str(preset.get("data_fields", "0,1,2,3,4,5,6,7,8,9")),
                    row_limit=int(preset.get("row_limit", 12)),
                    sleep_ms=0,
                    hypothesis=item["id"],
                    preset=item["preset"],
                )
                result = {
                    "ok": True,
                    "hypothesis": item,
                    "analysis": payload.get("analysis", {}),
                    "payload": payload,
                }
                print("[RESULT] ok score={0} verdict={1}".format(
                    result["analysis"].get("score"),
                    result["analysis"].get("verdict"),
                ))
            except Exception as exc:
                result = {
                    "ok": False,
                    "hypothesis": item,
                    "error": str(exc),
                    "analysis": {
                        "score": -1,
                        "verdict": "error",
                    },
                }
                print("[RESULT] fail error={0}".format(exc))

            all_results.append(result)
            if args.delay_ms > 0:
                time.sleep(max(0, args.delay_ms) / 1000.0)

    ranked = rank_results(all_results)
    summary = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "account_no": args.account_no,
        "cycles": args.cycles,
        "delay_ms": args.delay_ms,
        "top_hits": ranked[:10],
        "all_results": ranked,
    }

    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(summary, fp, ensure_ascii=False, indent=2)

    print("[DONE] wrote", out_path)
    print("[TOP]")
    for item in ranked[:10]:
        hyp = item.get("hypothesis", {})
        analysis = item.get("analysis", {})
        print(
            "- {0} | progid={1} | ok={2} | score={3} | verdict={4}".format(
                hyp.get("id", ""),
                hyp.get("progid", ""),
                item.get("ok", False),
                analysis.get("score"),
                analysis.get("verdict"),
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
