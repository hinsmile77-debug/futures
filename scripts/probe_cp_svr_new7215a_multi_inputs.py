from __future__ import annotations

import argparse
import itertools
import json
import platform
import struct
import sys
from typing import Any, Dict, Iterable, List

from ensure_cybos_login import ensure_cybos_login


DEFAULT_INPUT0 = [0, 1, 2, 49, 50]
DEFAULT_INPUT1 = [0, 1, 2, 49, 50, 20260513]
DEFAULT_INPUT2 = [0, 1, 2, 49, 50]


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("CpSvrNew7215A COM requires 32-bit Python")


def _parse_values(raw: str) -> List[Any]:
    values: List[Any] = []
    for part in raw.split(","):
        text = part.strip()
        if not text:
            continue
        if text.startswith(("'", '"')) and text.endswith(("'", '"')) and len(text) >= 2:
            values.append(text[1:-1])
            continue
        if text.lstrip("-").isdigit():
            try:
                values.append(int(text))
                continue
            except Exception:
                pass
        values.append(text)
    return values


def _summarize_headers(obj, indexes: Iterable[int]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for idx in indexes:
        try:
            out[str(idx)] = obj.GetHeaderValue(idx)
        except Exception as exc:
            out[str(idx)] = f"<ERR {exc}>"
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sweep input0/input1/input2 combinations for CpSysDib.CpSvrNew7215A"
    )
    parser.add_argument(
        "--progid",
        default="CpSysDib.CpSvrNew7215A",
        help="COM ProgID to dispatch (default: CpSysDib.CpSvrNew7215A)",
    )
    parser.add_argument(
        "--input0-values",
        help="Comma-separated candidates for input0. Bare digits become int.",
    )
    parser.add_argument(
        "--input1-values",
        help="Comma-separated candidates for input1. Bare digits become int.",
    )
    parser.add_argument(
        "--input2-values",
        help="Comma-separated candidates for input2. Bare digits become int.",
    )
    parser.add_argument(
        "--header-indexes",
        default="0,1,2,3,4,5,6,7,8,9",
        help="Header indexes to sample after successful BlockRequest",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional max combination count to evaluate (0 means all)",
    )
    parser.add_argument(
        "--only-success",
        action="store_true",
        help="Print only combinations where BlockRequest succeeded",
    )
    parser.add_argument(
        "--ensure-login",
        action="store_true",
        help="Run Cybos autologin first if the API session is not connected",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=1,
        help="Print progress every N combinations (default: 1)",
    )
    parser.add_argument(
        "--stream-results",
        action="store_true",
        help="Print each combination result immediately instead of waiting for the final JSON dump",
    )
    args = parser.parse_args()

    _ensure_runtime()

    try:
        import pythoncom
        from win32com.client import Dispatch
    except Exception as exc:
        raise RuntimeError("pywin32 import failed") from exc

    input0_values = _parse_values(args.input0_values) if args.input0_values else list(DEFAULT_INPUT0)
    input1_values = _parse_values(args.input1_values) if args.input1_values else list(DEFAULT_INPUT1)
    input2_values = _parse_values(args.input2_values) if args.input2_values else list(DEFAULT_INPUT2)
    header_indexes = [int(part.strip()) for part in args.header_indexes.split(",") if part.strip()]

    combos = itertools.product(input0_values, input1_values, input2_values)

    pythoncom.CoInitialize()
    cp_cybos = None
    results: List[Dict[str, Any]] = []
    try:
        if args.ensure_login:
            print("[INFO] ensure_cybos_login() start")
            if not ensure_cybos_login(require_trade_init=False):
                raise RuntimeError("Cybos login/session bootstrap failed")
            print("[INFO] ensure_cybos_login() done")

        cp_cybos = Dispatch("CpUtil.CpCybos")
        if not bool(cp_cybos.IsConnect):
            raise RuntimeError("Cybos is not connected")
        print("[INFO] CpUtil.CpCybos.IsConnect=1")

        for idx, (value0, value1, value2) in enumerate(combos):
            if args.limit and idx >= args.limit:
                break

            if args.progress_every > 0 and idx % args.progress_every == 0:
                print(
                    f"[PROGRESS] combo_index={idx} input0={value0!r} input1={value1!r} input2={value2!r}",
                    flush=True,
                )

            row: Dict[str, Any] = {
                "combo_index": idx,
                "input0": value0,
                "input1": value1,
                "input2": value2,
            }
            obj = None
            try:
                obj = Dispatch(args.progid)

                try:
                    obj.SetInputValue(0, value0)
                    obj.SetInputValue(1, value1)
                    obj.SetInputValue(2, value2)
                    row["set_input"] = "ok"
                except Exception as exc:
                    row["set_input"] = "error"
                    row["set_input_error"] = str(exc)
                    if not args.only_success:
                        results.append(row)
                        if args.stream_results:
                            print(json.dumps(row, ensure_ascii=False, default=str), flush=True)
                    continue

                try:
                    obj.BlockRequest()
                    row["block_request"] = "ok"
                except Exception as exc:
                    row["block_request"] = "error"
                    row["block_request_error"] = str(exc)
                    if not args.only_success:
                        results.append(row)
                        if args.stream_results:
                            print(json.dumps(row, ensure_ascii=False, default=str), flush=True)
                    continue

                try:
                    row["dib_status"] = obj.GetDibStatus()
                except Exception as exc:
                    row["dib_status"] = f"<ERR {exc}>"

                try:
                    row["dib_msg"] = obj.GetDibMsg1()
                except Exception as exc:
                    row["dib_msg"] = f"<ERR {exc}>"

                row["headers"] = _summarize_headers(obj, header_indexes)

                if args.only_success and row.get("block_request") != "ok":
                    continue
                results.append(row)
                if args.stream_results:
                    print(json.dumps(row, ensure_ascii=False, default=str), flush=True)
            finally:
                obj = None

        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
        return 0
    finally:
        cp_cybos = None
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
