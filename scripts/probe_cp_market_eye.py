"""[293차 진단] CpSysDib.MarketEye로 지수(K2G01P/O2901P) 조회 가능 여부 확인용 1회성 프로브.

dscbo1.StockMst는 개별 종목 전용 TR로 확인됨(공식 문서에 지수 코드 언급 없음,
실측 결과 K2G01P/O2901P/U180 전부 "71103 조회결과가 없습니다"). 반면
CpSysDib.MarketEye는 주식/지수/선물옵션을 한 번에 조회하도록 설계된 TR로,
문서상 "해외지수와 환율은 심볼코드 입력" 예시가 명시돼 있어 국내지수도
지원할 가능성이 높음.

MarketEye는 StockMst와 인터페이스가 다르다 (헤더 1개 종목이 아니라 최대
200종목 배열 + 필드타입 배열을 넣고 행(row) 단위로 결과를 받는다):
    SetInputValue(0, field_type_list)   # 요청할 필드타입 배열
    SetInputValue(1, code_list)         # 조회할 종목코드 배열 (최대 200개)
    BlockRequest()
    GetHeaderValue(0)                   # 반환된 종목 수
    GetDataValue(field_position, row)   # row행의 field_position번째 요청 필드 값

main.py의 라이브 프로세스는 건드리지 않고 별도 COM 클라이언트로 접속한다
(probe_cp_stock_mst.py와 동일 안전 패턴).

사용례:
    python scripts/probe_cp_market_eye.py
    python scripts/probe_cp_market_eye.py --codes K2G01P,O2901P,A005930,U180
"""
from __future__ import annotations

import argparse
import json
import platform
import struct
import sys
from typing import Any, Dict, List

from ensure_cybos_login import ensure_cybos_login

# 문서에서 확인된 필드타입 (0=종목코드, 1=시간, 2=대비부호, 3=전일대비,
# 4=현재가, 5=시가, 6=고가, 7=저가, 8=매도호가, 9=매수호가, 10=거래량,
# 11=거래대금). 17=종목명으로 언급된 예제도 있어 0~20 범위를 폭넓게 요청한다.
DEFAULT_FIELDS = list(range(0, 21))


def _dump_rows(obj, field_ids: List[int], row_count: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in range(row_count):
        row_values: Dict[str, Any] = {"row": row}
        for pos, field_id in enumerate(field_ids):
            key = f"field{field_id}"
            try:
                row_values[key] = obj.GetDataValue(pos, row)
            except Exception as exc:
                row_values[key] = f"<ERR {exc}>"
        out.append(row_values)
    return out


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("MarketEye COM requires 32-bit Python (py37_32)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Cybos CpSysDib.MarketEye payload")
    parser.add_argument(
        "--codes", default="K2G01P,O2901P,A005930",
        help="콤마로 구분된 조회 코드 목록 (기본: KOSPI200지수,VKOSPI,삼성전자(대조군))",
    )
    parser.add_argument("--progid", default="CpSysDib.MarketEye")
    parser.add_argument(
        "--fields", default=",".join(str(f) for f in DEFAULT_FIELDS),
        help="콤마로 구분된 요청 필드타입 목록",
    )
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

    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    field_ids = [int(f.strip()) for f in args.fields.split(",") if f.strip()]

    pythoncom.CoInitialize()
    try:
        if args.ensure_login:
            print("[INFO] ensure_cybos_login() start")
            if not ensure_cybos_login(require_trade_init=False):
                raise RuntimeError("Cybos login/session bootstrap failed")

        cp_cybos = Dispatch("CpUtil.CpCybos")
        if not bool(cp_cybos.IsConnect):
            raise RuntimeError(
                "Cybos is not connected — 관리자 권한 셸에서 실행했는지 확인할 것."
            )

        obj = Dispatch(args.progid)
        obj.SetInputValue(0, field_ids)
        obj.SetInputValue(1, codes)
        ret = obj.BlockRequest()

        try:
            status = obj.GetDibStatus()
        except Exception as exc:
            status = f"<ERR {exc}>"
        try:
            msg = obj.GetDibMsg1()
        except Exception as exc:
            msg = f"<ERR {exc}>"
        try:
            row_count = int(obj.GetHeaderValue(0))
        except Exception as exc:
            row_count = 0
            print(f"[WARN] GetHeaderValue(0) 실패: {exc}")

        rows = _dump_rows(obj, field_ids, max(row_count, len(codes)))

        print(f"progid={args.progid}")
        print(f"input_codes={codes}")
        print(f"input_fields={field_ids}")
        print(f"block_request_ret={ret}")
        print(f"dib_status={status}")
        print(f"dib_msg={msg}")
        print(f"row_count(header0)={row_count}")
        print("\n=== rows (row: {field_id: value}) ===")
        print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
        return 0
    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
