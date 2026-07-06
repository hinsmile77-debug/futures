"""[292차 진단] dscbo1.StockMst 종목명 검증 실패(K2G01P/O2901P) 원인 조사용 1회성 프로브.

main.py의 라이브 프로세스는 건드리지 않고, 같은 Cybos Plus 로그인 세션에
별도 COM 클라이언트로 접속해 헤더 전체를 덤프한다 (probe_cp_option_mst.py와
동일 패턴). --ensure-login 없이 실행하면 이미 연결된 세션의 IsConnect만
확인하고 재로그인은 시도하지 않는다 — 라이브 세션에 영향 없음.

사용례:
    python scripts/probe_cp_stock_mst.py --code K2G01P
    python scripts/probe_cp_stock_mst.py --code O2901P
    python scripts/probe_cp_stock_mst.py --code A0567   (대조군: 정상 작동 중인 선물 코드)
"""
from __future__ import annotations

import argparse
import json
import platform
import struct
import sys
from typing import Any, Dict, List

from ensure_cybos_login import ensure_cybos_login


def _dump_headers(obj, limit: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for idx in range(limit):
        try:
            value = obj.GetHeaderValue(idx)
            out.append({"index": idx, "value": value, "type": type(value).__name__})
        except Exception as exc:
            out.append({"index": idx, "error": str(exc)})
    return out


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("StockMst COM requires 32-bit Python (py37_32)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Cybos dscbo1.StockMst payload")
    parser.add_argument("--code", required=True, help="조회할 종목/지수 코드, 예: K2G01P")
    parser.add_argument("--progid", default="dscbo1.StockMst")
    parser.add_argument("--header-limit", type=int, default=40)
    parser.add_argument(
        "--ensure-login", action="store_true",
        help="세션 미연결 시에만 autologin 시도 (이미 연결돼 있으면 아무 것도 안 함)",
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
            raise RuntimeError(
                "Cybos is not connected — 라이브 main.py가 실행 중이면 이미 연결돼 "
                "있어야 함. --ensure-login 없이는 재로그인을 시도하지 않음."
            )

        obj = Dispatch(args.progid)
        obj.SetInputValue(0, args.code)
        ret = obj.BlockRequest()

        try:
            status = obj.GetDibStatus()
        except Exception as exc:
            status = f"<ERR {exc}>"
        try:
            msg = obj.GetDibMsg1()
        except Exception as exc:
            msg = f"<ERR {exc}>"

        header_dump = _dump_headers(obj, args.header_limit)

        print(f"progid={args.progid}")
        print(f"input_code={args.code}")
        print(f"block_request_ret={ret}")
        print(f"dib_status={status}")
        print(f"dib_msg={msg}")
        print("\n=== headers (index: value) ===")
        print(json.dumps(header_dump, ensure_ascii=False, indent=2, default=str))
        return 0
    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
