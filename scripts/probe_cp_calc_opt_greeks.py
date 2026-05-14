from __future__ import annotations

import argparse
import platform
import struct
import sys
from typing import Any

from ensure_cybos_login import ensure_cybos_login


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        text = _safe_str(value).replace(",", "")
        if not text:
            return default
        return float(text)
    except Exception:
        return default


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("32-bit Python required")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Cybos CpCalcOptGreeks (옵션 그릭스 계산)")
    parser.add_argument("--ensure-login", action="store_true",
                        help="Cybos 자동 로그인 먼저 실행")
    parser.add_argument("--call-put", type=int, required=True,
                        help="콜=1, 풋=2")
    parser.add_argument("--option-price", type=float, required=True,
                        help="옵션 시장가")
    parser.add_argument("--spot", type=float, required=True,
                        help="기초자산가 (KOSPI200)")
    parser.add_argument("--strike", type=float, required=True,
                        help="행사가")
    parser.add_argument("--vol", type=float, required=True,
                        help="변동성 (% 단위, 예: 18.5)")
    parser.add_argument("--dte", type=int, required=True,
                        help="잔존일수")
    parser.add_argument("--rf-rate", type=float, default=3.5,
                        help="무위험 이자율 (% 단위, 기본 3.5)")
    parser.add_argument("--dividend", type=float, default=0.0,
                        help="배당률 (% 단위, 기본 0)")
    args = parser.parse_args()

    _ensure_runtime()

    try:
        import pythoncom
        from win32com.client import Dispatch
    except ImportError as exc:
        raise RuntimeError("pywin32 import failed") from exc

    pythoncom.CoInitialize()
    cp_cybos = None
    obj = None
    try:
        if args.ensure_login:
            print("[INFO] ensure_cybos_login() start")
            if not ensure_cybos_login(require_trade_init=False):
                raise RuntimeError("Cybos 로그인 실패")

        cp_cybos = Dispatch("CpUtil.CpCybos")
        if not bool(cp_cybos.IsConnect):
            raise RuntimeError("Cybos 미연결")

        # ── CpCalcOptGreeks Dispatch ──────────────────────────────
        try:
            obj = Dispatch("CpUtil.CpCalcOptGreeks")
        except Exception as exc:
            raise RuntimeError(
                "CpCalcOptGreeks Dispatch 실패.\n"
                "CpUtil.CpCalcOptGreeks COM 객체 등록 여부를 확인하세요."
            ) from exc

        # ── enum 상수 탐색 ────────────────────────────────────────
        # OT_CALL, OT_PUT, VT_HISTORY, VT_IMPLIED
        OT_CALL = 0
        OT_PUT  = 1
        VT_IMPLIED = 1
        try:
            from win32com.client import constants as _cc
            OT_CALL = int(_cc.OT_CALL)
            OT_PUT  = int(_cc.OT_PUT)
            VT_IMPLIED = int(_cc.VT_IMPLIED)
        except Exception:
            pass

        call_put_type = OT_CALL if args.call_put == 1 else OT_PUT
        print(f"[INFO] OT_CALL={OT_CALL} OT_PUT={OT_PUT} → CallPutType={call_put_type}")

        # ── 속성 입력 (Property assignment) ───────────────────────
        # Cybos 도움말 기준 — SetInputValue()가 아닌 속성 직접 할당
        # CallPutType: OT_CALL(콜) / OT_PUT(풋)
        obj.CallPutType = call_put_type
        obj.Price       = args.option_price
        obj.UnderPrice  = args.spot
        obj.ExerPrice   = args.strike
        obj.VolatilityType = VT_IMPLIED   # 기본: 내재변동성
        obj.Volatility  = args.vol
        obj.ExpirDays   = float(args.dte)
        obj.RFInterRate = args.rf_rate
        obj.DividRate   = args.dividend

        # ── Calculate() ───────────────────────────────────────────
        obj.Calculate()

        # ── 결과 읽기 (Property read) ─────────────────────────────
        print(f"\n=== 입력 ===")
        print(f"  콜/풋: {'콜' if args.call_put == 1 else '풋'} (Constant={call_put_type})")
        print(f"  옵션가: {args.option_price:.2f}")
        print(f"  기초자산가: {args.spot:.2f}")
        print(f"  행사가: {args.strike:.2f}")
        print(f"  변동성: {args.vol:.2f}% (내재변동성)")
        print(f"  잔존일수: {args.dte}")
        print(f"  무위험 이자율: {args.rf_rate:.2f}%")
        print(f"  배당: {args.dividend:.2f}%")

        print(f"\n=== 그릭스 결과 ===")
        greek_labels = [
            ("TV",    "이론가"),
            ("Delta", "델타"),
            ("Gamma", "감마"),
            ("Theta", "세타"),
            ("Vega",  "베가"),
            ("Rho",   "로"),
            ("IV",    "내재변동성"),
        ]
        for prop_name, label in greek_labels:
            try:
                value = getattr(obj, prop_name)
                print(f"  {prop_name:>6s} = {value:>12.6f}  ← {label}")
            except Exception as exc:
                print(f"  {prop_name:>6s} = {'ERR':>12}  ← {label} ({exc})")

        return 0
    finally:
        obj = None
        cp_cybos = None
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
