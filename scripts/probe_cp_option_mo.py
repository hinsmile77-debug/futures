from __future__ import annotations

import argparse
import json
import platform
import struct
import sys
import time
from typing import Any, Optional

from ensure_cybos_login import ensure_cybos_login


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


class _OptionMoEvents:
    """OptionMo 실시간 이벤트 핸들러.

    Cybos OptionMo는 실시간으로 OI 변화를 통지합니다.
    콜백 시그니처는 Cybos 도움말 기준:
      OnReceiveData(str code, int oi, int oi_change, int oi_state)
    """
    def __init__(self, watch_sec: float = 5.0):
        self.events: list = []
        self._watch_sec = watch_sec
        self._start = time.time()

    def OnReceiveData(self, code: str, oi: int, oi_change: int, oi_state: int):
        elapsed = time.time() - self._start
        self.events.append({
            "elapsed": round(elapsed, 3),
            "code": _safe_str(code),
            "oi": oi,
            "oi_change": oi_change,
            "oi_state": oi_state,
        })
        print(f"  [OptionMo] {elapsed:.1f}s | {code} OI={oi} Δ={oi_change:+d} state={oi_state}")


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("32-bit Python required")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Cybos OptionMo (실시간 OI)")
    parser.add_argument("--code", required=True,
                        help="옵션 종목코드 (예: 201VA355)")
    parser.add_argument("--ensure-login", action="store_true",
                        help="Cybos 자동 로그인 먼저 실행")
    parser.add_argument("--watch-sec", type=float, default=10.0,
                        help="실시간 이벤트 수신 대기 시간 (초, 기본 10)")
    args = parser.parse_args()

    _ensure_runtime()

    try:
        import pythoncom
        from win32com.client import Dispatch, DispatchWithEvents
    except ImportError as exc:
        raise RuntimeError("pywin32 import failed") from exc

    pythoncom.CoInitialize()
    cp_cybos = None
    ev = None
    try:
        if args.ensure_login:
            print("[INFO] ensure_cybos_login() start")
            if not ensure_cybos_login(require_trade_init=False):
                raise RuntimeError("Cybos 로그인 실패")

        cp_cybos = Dispatch("CpUtil.CpCybos")
        if not bool(cp_cybos.IsConnect):
            raise RuntimeError("Cybos 미연결")

        # ── OptionMo Dispatch (실시간 이벤트) ─────────────────────
        try:
            ev = _OptionMoEvents(watch_sec=args.watch_sec)
            option_mo = DispatchWithEvents("Dscbo1.OptionMo", ev)
        except Exception as exc:
            raise RuntimeError(
                "Dscbo1.OptionMo DispatchWithEvents 실패.\n"
                "OptionMo COM 객체가 등록되어 있는지 확인하세요.\n"
                f"원본 오류: {exc}"
            ) from exc

        # ── Subscribe ─────────────────────────────────────────────
        try:
            option_mo.Subscribe(args.code)
            print(f"[INFO] OptionMo.Subscribe({args.code}) 성공")
            print(f"[INFO] {args.watch_sec:.0f}초 동안 실시간 OI 이벤트 대기 중...")
        except Exception as exc:
            raise RuntimeError(
                f"OptionMo.Subscribe({args.code}) 실패.\n"
                f"종목코드 형식이나 COM 인터페이스를 확인하세요.\n"
                f"원본 오류: {exc}"
            ) from exc

        # ── 이벤트 루프 (메시지 펌프) ──────────────────────────────
        deadline = time.time() + args.watch_sec
        while time.time() < deadline:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.05)

        # ── Unsubscribe ───────────────────────────────────────────
        try:
            option_mo.Unsubscribe(args.code)
            print(f"[INFO] OptionMo.Unsubscribe({args.code}) 완료")
        except Exception as exc:
            print(f"[WARN] Unsubscribe 실패: {exc}")

        # ── 결과 출력 ─────────────────────────────────────────────
        print(f"\n=== 실시간 OI 수신 결과 ===")
        print(f"코드: {args.code}")
        print(f"수신 이벤트: {len(ev.events)}건")

        if ev.events:
            # OI 변화 추이
            oi_values = [e["oi"] for e in ev.events if e["oi"] > 0]
            oi_changes = [e["oi_change"] for e in ev.events]
            print(f"OI 값: {oi_values}")
            print(f"OI 변화: {oi_changes}")
            print(f"OI 상태: {[e['oi_state'] for e in ev.events]}")
            print(f"\n=== 상세 로그 ===")
            print(json.dumps(ev.events, ensure_ascii=False, indent=2, default=str))
        else:
            print("[WARN] 수신된 OI 이벤트가 없습니다.")
            print("가능한 원인:")
            print("  1. 장 마감 시간 (9:00~15:30에 실행 권장)")
            print("  2. 해당 종목의 OI 변화가 없음")
            print("  3. OptionMo COM 인터페이스가 다름 (이벤트 시그니처 확인 필요)")

        return 0
    finally:
        ev = None
        cp_cybos = None
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
