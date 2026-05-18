"""
OptionMo OI 변화 관측 프로브.

DispatchWithEvents가 Python 3.7 32-bit + pywin32 환경에서 metaclass conflict를
일으키므로 Subscribe 방식 대신 OptionMst BlockRequest 폴링으로 OI 변화를 관측한다.

장중(09:00~15:30)에만 OI가 변화한다.
"""
from __future__ import annotations

import argparse
import json
import platform
import struct
import sys
import time
from typing import Any, Dict, List, Optional

from ensure_cybos_login import ensure_cybos_login

PROGID_MST = "Dscbo1.OptionMst"


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("32-bit Python required")


def _fetch_oi(obj, code: str) -> Dict[str, Any]:
    obj.SetInputValue(0, code)
    obj.BlockRequest()

    result: Dict[str, Any] = {
        "code": code,
        "ts": round(time.time(), 2),
    }
    try:
        result["dib_status"] = obj.GetDibStatus()
        result["dib_msg"] = obj.GetDibMsg1()
    except Exception as exc:
        result["dib_status"] = -1
        result["dib_msg"] = str(exc)

    try:
        result["oi_current"] = obj.GetHeaderValue(99)   # 현재 미결제약정
        result["oi_prev"] = obj.GetHeaderValue(37)      # 전일 미결제약정
        result["last"] = obj.GetHeaderValue(93)         # 현재가
        result["strike"] = obj.GetHeaderValue(6)        # 행사가
    except Exception as exc:
        result["fetch_error"] = str(exc)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OptionMst 폴링으로 OI 변화 관측 (장중 전용)"
    )
    parser.add_argument("--code", required=True, help="옵션 종목코드 (예: B0166A89)")
    parser.add_argument("--ensure-login", action="store_true")
    parser.add_argument(
        "--watch-sec", type=float, default=15.0, help="총 관측 시간(초)"
    )
    parser.add_argument(
        "--interval", type=float, default=3.0, help="폴링 간격(초, 기본 3)"
    )
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

        obj = Dispatch(PROGID_MST)

        print(f"[INFO] {PROGID_MST} 폴링 OI 관측 시작")
        print(f"[INFO] 코드={args.code}  관측={args.watch_sec:.0f}초  간격={args.interval:.0f}초")
        print("[NOTE] Dscbo1.OptionMo Subscribe는 metaclass conflict로 사용 불가 → 폴링 대체")
        print("[NOTE] 장외에는 OI가 변하지 않습니다 (09:00~15:30 권장)")
        print()

        snapshots: List[Dict[str, Any]] = []
        deadline = time.time() + args.watch_sec

        while time.time() < deadline:
            snap = _fetch_oi(obj, args.code)
            snapshots.append(snap)
            oi = snap.get("oi_current", "?")
            last = snap.get("last", "?")
            strike = snap.get("strike", "?")
            status = snap.get("dib_status", "?")
            print(
                f"  [{len(snapshots):02d}] strike={strike}  OI={oi}"
                f"  현재가={last}  status={status}"
            )
            remaining = deadline - time.time()
            if remaining > 0:
                time.sleep(min(args.interval, remaining))

        # ── 결과 분석 ─────────────────────────────────────────────
        oi_values: List[Any] = [
            s["oi_current"]
            for s in snapshots
            if s.get("oi_current") is not None and s.get("dib_status") == 0
        ]
        oi_changed = len(set(oi_values)) > 1 if oi_values else False

        print(f"\n=== OI 관측 결과 ===")
        print(f"코드:        {args.code}")
        print(f"폴링 횟수:   {len(snapshots)}회")
        print(f"유효 OI 값:  {oi_values}")
        if oi_changed:
            print(f"OI 변화 감지: ✅ YES  범위: {min(oi_values)} ~ {max(oi_values)}")
            print("→ OptionMst 폴링으로 실시간 OI 수집 가능 확인")
        else:
            print("OI 변화 감지: ❌ NO")
            print("→ 장외 실행이거나 해당 종목 거래 없음")

        print(f"\n=== 상세 스냅샷 ===")
        print(json.dumps(snapshots, ensure_ascii=False, indent=2, default=str))
        return 0

    finally:
        obj = None
        cp_cybos = None
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
