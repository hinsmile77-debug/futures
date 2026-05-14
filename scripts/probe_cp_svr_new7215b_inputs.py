from __future__ import annotations

import argparse
import json
import platform
import struct
import sys
from typing import Any, Dict, List

from ensure_cybos_login import ensure_cybos_login


DEFAULT_VALUES = [
    0,
    1,
    2,
    3,
    4,
    10,
    20,
    49,
    50,
    100,
    20260513,
    "0",
    "1",
    "2",
    "49",
    "50",
    "B0165A01",
    "B0165A07",
    "A0565",
]


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("CpSvrNew7215B COM requires 32-bit Python")


def _summarize_headers(obj, indexes: List[int]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for idx in indexes:
        try:
            out[str(idx)] = obj.GetHeaderValue(idx)
        except Exception as exc:
            out[str(idx)] = f"<ERR {exc}>"
    return out


def _parse_custom_values(raw: str) -> List[Any]:
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Sweep input candidates for CpSysDib.CpSvrNew7215B SetInputValue(0, ...)")
    parser.add_argument(
        "--progid",
        default="CpSysDib.CpSvrNew7215B",
        help="COM ProgID to dispatch (default: CpSysDib.CpSvrNew7215B)",
    )
    parser.add_argument(
        "--values",
        help="Comma-separated custom candidates. Bare digits become int; quoted values stay string.",
    )
    parser.add_argument(
        "--header-indexes",
        default="0,1,2,3,4,5,6,7,8,9",
        help="Header indexes to sample after successful BlockRequest",
    )
    parser.add_argument(
        "--ensure-login",
        action="store_true",
        help="Run Cybos autologin first if the API session is not connected",
    )
    args = parser.parse_args()

    _ensure_runtime()

    try:
        import pythoncom
        from win32com.client import Dispatch
    except Exception as exc:
        raise RuntimeError("pywin32 import failed") from exc

    values = _parse_custom_values(args.values) if args.values else list(DEFAULT_VALUES)
    header_indexes = [int(part.strip()) for part in args.header_indexes.split(",") if part.strip()]

    pythoncom.CoInitialize()
    cp_cybos = None
    results: List[Dict[str, Any]] = []
    try:
        if args.ensure_login:
            print("[INFO] ensure_cybos_login() start")
            if not ensure_cybos_login(require_trade_init=False):
                raise RuntimeError("Cybos login/session bootstrap failed")

        cp_cybos = Dispatch("CpUtil.CpCybos")
        if not bool(cp_cybos.IsConnect):
            raise RuntimeError("Cybos is not connected")

        for candidate in values:
            row: Dict[str, Any] = {
                "candidate_repr": repr(candidate),
                "candidate_type": type(candidate).__name__,
            }
            obj = None
            try:
                obj = Dispatch(args.progid)
                try:
                    obj.SetInputValue(0, candidate)
                    row["set_input"] = "ok"
                except Exception as exc:
                    row["set_input"] = "error"
                    row["set_input_error"] = str(exc)
                    results.append(row)
                    continue

                try:
                    obj.BlockRequest()
                    row["block_request"] = "ok"
                except Exception as exc:
                    row["block_request"] = "error"
                    row["block_request_error"] = str(exc)
                    results.append(row)
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
                results.append(row)
            finally:
                obj = None

        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
        return 0
    finally:
        cp_cybos = None
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
