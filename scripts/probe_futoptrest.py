from __future__ import annotations

import argparse
import datetime
import json
import platform
import struct
import sys
from typing import Any, Dict, List, Optional

from ensure_cybos_login import ensure_cybos_login

DATA_FIELD_NAMES = [
    "시간", "현재가", "대비", "거래량",
    "1차 매도호가", "1차 매수호가", "1차 매도잔량", "1차 매수잔량", "1차 매도건수", "1차 매수건수",
    "2차 매도호가", "2차 매수호가", "2차 매도잔량", "2차 매수잔량", "2차 매도건수", "2차 매수건수",
    "3차 매도호가", "3차 매수호가", "3차 매도잔량", "3차 매수잔량", "3차 매도건수", "3차 매수건수",
    "4차 매도호가", "4차 매수호가", "4차 매도잔량", "4차 매수잔량", "4차 매도건수", "4차 매수건수",
    "5차 매도호가", "5차 매수호가", "5차 매도잔량", "5차 매수잔량", "5차 매도건수", "5차 매수건수",
    "총 매도잔량", "총 매수잔량", "총 매도건수", "총 매수건수",
    "매도잔량증감", "매수잔량증감", "매도건수증감", "매수건수증감",
    "주기별누적체결매도수량", "주기별누적체결매수수량", "누적체결매도수량", "누적체결매수수량",
]
HEADER_FIELD_NAMES = ["Count", "체결매도합", "체결매수합"]


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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("Cybos COM requires 32-bit Python (py37_32)")


def _guess_nearest_mini_futures_code(dispatch) -> Optional[str]:
    """A05xxx 미니선물 근월물 코드 — FutureMst price>0 으로 검증."""
    today = datetime.date.today()
    for delta in range(7):
        month = today.month + delta
        year = today.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        code = "A05{0}{1}".format(str(year)[-1], format(month, "X"))
        try:
            obj = dispatch("Dscbo1.FutureMst")
            obj.SetInputValue(0, code)
            obj.BlockRequest()
            price = _safe_float(obj.GetHeaderValue(71))
        except Exception:
            continue
        if price and price > 0:
            print(f"[INFO] 근월물 코드 확정: {code} (price={price})")
            return code
    return None


def _dump_headers(obj, names: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for idx, name in enumerate(names):
        try:
            value = obj.GetHeaderValue(idx)
            out.append({"index": idx, "name": name, "value": value})
        except Exception as exc:
            out.append({"index": idx, "name": name, "error": str(exc)})
    return out


def _dump_rows(obj, names: List[str], row_limit: int, inferred_row_count: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    limit = row_limit
    if inferred_row_count > 0:
        limit = min(limit, inferred_row_count)
    for row in range(limit):
        row_values: Dict[str, Any] = {"row": row}
        had_any = False
        for idx, name in enumerate(names):
            try:
                value = obj.GetDataValue(idx, row)
                row_values[name] = value
                had_any = True
            except Exception as exc:
                row_values[name] = f"<ERR {exc}>"
        if had_any:
            out.append(row_values)
    return out


def _print_section(title: str, payload: Any) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Cybos Dscbo1.FutOptRest payload (cancel_ratio 재조사용)")
    parser.add_argument("--code", help="종목코드 (미지정 시 A05xxx 미니선물 근월물 자동탐색)")
    parser.add_argument("--period", default="0", help="조회주기(분:초단위, 틱:0) — 기본 0(틱)")
    parser.add_argument("--level", default="T", help="호가잔량설정('1'~'5','T') — 기본 T")
    parser.add_argument("--row-limit", type=int, default=30, help="Max rows to dump")
    parser.add_argument(
        "--ensure-login",
        action="store_true",
        help="Cybos 세션 미연결 시 autologin 먼저 시도",
    )
    args = parser.parse_args()

    _ensure_runtime()

    try:
        import pythoncom
        from win32com.client import Dispatch
    except Exception as exc:
        raise RuntimeError("pywin32 import failed") from exc

    pythoncom.CoInitialize()
    try:
        if args.ensure_login:
            print("[INFO] ensure_cybos_login() start")
            if not ensure_cybos_login(require_trade_init=False):
                raise RuntimeError("Cybos login/session bootstrap failed")

        cp_cybos = Dispatch("CpUtil.CpCybos")
        if not bool(cp_cybos.IsConnect):
            raise RuntimeError("Cybos is not connected")

        code = args.code
        if not code:
            code = _guess_nearest_mini_futures_code(Dispatch)
            if not code:
                raise RuntimeError("근월물 코드 자동탐색 실패 — --code 로 직접 지정 필요")

        obj = Dispatch("Dscbo1.FutOptRest")
        print(f"[INFO] SetInputValue(0, {code!r})  # 종목코드")
        obj.SetInputValue(0, code)
        print(f"[INFO] SetInputValue(1, {args.period!r})  # 조회주기")
        obj.SetInputValue(1, args.period)
        print(f"[INFO] SetInputValue(2, {args.level!r})  # 호가잔량설정")
        obj.SetInputValue(2, args.level)

        obj.BlockRequest()

        try:
            status = obj.GetDibStatus()
        except Exception as exc:
            status = f"<ERR {exc}>"
        try:
            msg1 = obj.GetDibMsg1()
        except Exception as exc:
            msg1 = f"<ERR {exc}>"

        header_dump = _dump_headers(obj, HEADER_FIELD_NAMES)
        inferred_row_count = _safe_int(header_dump[0].get("value"), default=0) if header_dump else 0
        rows_dump = _dump_rows(obj, DATA_FIELD_NAMES, args.row_limit, inferred_row_count)

        print(f"code={code}")
        print(f"dib_status={status}")
        print(f"dib_msg1={msg1}")
        print(f"inferred_row_count(Count)={inferred_row_count}")
        _print_section("headers", header_dump)
        _print_section("rows", rows_dump)
        return 0
    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
