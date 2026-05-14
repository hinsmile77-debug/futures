from __future__ import annotations

import argparse
import json
import platform
import struct
import sys
from typing import Any, Dict, List

from ensure_cybos_login import ensure_cybos_login


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        text = _safe_str(value).replace(",", "")
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("CpSvrNew7215A COM requires 32-bit Python")


def _dump_headers(obj, limit: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for idx in range(limit):
        try:
            value = obj.GetHeaderValue(idx)
            out.append({"index": idx, "value": value})
        except Exception as exc:
            out.append({"index": idx, "error": str(exc)})
    return out


def _guess_row_count(obj, header_limit: int) -> int:
    candidates = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 20, 21]
    for idx in candidates:
        if idx >= header_limit:
            continue
        try:
            value = obj.GetHeaderValue(idx)
        except Exception:
            continue
        row_count = _safe_int(value, default=-1)
        if 0 <= row_count <= 5000:
            return row_count
    return 0


def _dump_rows(obj, data_fields: List[int], row_limit: int, inferred_row_count: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    limit = row_limit
    if inferred_row_count > 0:
        limit = min(limit, inferred_row_count)
    for row in range(limit):
        row_values: Dict[str, Any] = {"row": row}
        had_any = False
        for field in data_fields:
            key = str(field)
            try:
                value = obj.GetDataValue(field, row)
                row_values[key] = value
                had_any = True
            except Exception as exc:
                row_values[key] = f"<ERR {exc}>"
        if had_any:
            out.append(row_values)
    return out


def _print_section(title: str, payload: Any) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def main() -> int:
    parser = argparse.ArgumentParser(description="Detailed probe for a known-good CpSysDib.CpSvrNew7215A input combination")
    parser.add_argument("--input0", type=int, required=True, help="SetInputValue(0, ...)")
    parser.add_argument("--input1", type=int, required=True, help="SetInputValue(1, ...)")
    parser.add_argument("--input2", type=int, required=True, help="SetInputValue(2, ...)")
    parser.add_argument(
        "--progid",
        default="CpSysDib.CpSvrNew7215A",
        help="COM ProgID to dispatch (default: CpSysDib.CpSvrNew7215A)",
    )
    parser.add_argument("--header-limit", type=int, default=120, help="How many header indexes to dump")
    parser.add_argument(
        "--data-fields",
        default="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19",
        help="Comma-separated GetDataValue field indexes to dump",
    )
    parser.add_argument("--row-limit", type=int, default=40, help="Max rows to dump")
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

    pythoncom.CoInitialize()
    cp_cybos = None
    obj = None
    try:
        if args.ensure_login:
            print("[INFO] ensure_cybos_login() start")
            if not ensure_cybos_login(require_trade_init=False):
                raise RuntimeError("Cybos login/session bootstrap failed")
            print("[INFO] ensure_cybos_login() done")

        cp_cybos = Dispatch("CpUtil.CpCybos")
        if not bool(cp_cybos.IsConnect):
            raise RuntimeError("Cybos is not connected")

        obj = Dispatch(args.progid)
        print(f"[INFO] SetInputValue(0, {args.input0})")
        print(f"[INFO] SetInputValue(1, {args.input1})")
        print(f"[INFO] SetInputValue(2, {args.input2})")
        obj.SetInputValue(0, args.input0)
        obj.SetInputValue(1, args.input1)
        obj.SetInputValue(2, args.input2)
        obj.BlockRequest()

        try:
            status = obj.GetDibStatus()
        except Exception as exc:
            status = f"<ERR {exc}>"

        try:
            msg = obj.GetDibMsg1()
        except Exception as exc:
            msg = f"<ERR {exc}>"

        header_dump = _dump_headers(obj, args.header_limit)
        inferred_row_count = _guess_row_count(obj, args.header_limit)
        data_fields = [int(part.strip()) for part in args.data_fields.split(",") if part.strip()]
        rows_dump = _dump_rows(obj, data_fields, args.row_limit, inferred_row_count)

        print(f"progid={args.progid}")
        print(f"input0={args.input0}")
        print(f"input1={args.input1}")
        print(f"input2={args.input2}")
        print(f"dib_status={status}")
        print(f"dib_msg={msg}")
        print(f"inferred_row_count={inferred_row_count}")
        _print_section("headers", header_dump)
        _print_section("rows", rows_dump)
        return 0
    finally:
        obj = None
        cp_cybos = None
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
