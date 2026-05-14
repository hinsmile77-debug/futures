from __future__ import annotations

import argparse
import json
import platform
import struct
import sys
from typing import Any, Dict, List, Optional

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


def _dump_chain(obj, count: int) -> List[Dict[str, Any]]:
    """CpOptionCode.GetData(type, index) 순회.

    type=0: 옵션코드
    type=2: 콜/풋 구분 (문자열, 'C' / 'P' 또는 한글)
    type=3: 행사월 (YYYYMM)
    type=4: 행사가
    """
    chain: List[Dict[str, Any]] = []
    for idx in range(count):
        try:
            code = _safe_str(obj.GetData(0, idx))
            cp   = _safe_str(obj.GetData(2, idx))
            ym   = _safe_str(obj.GetData(3, idx))
            strike_raw = obj.GetData(4, idx)
            strike = _safe_float(strike_raw, default=0.0)
            chain.append({
                "index": idx,
                "code": code,
                "call_put": cp,
                "ym": ym,
                "strike": strike,
            })
        except Exception as exc:
            chain.append({
                "index": idx,
                "error": str(exc),
            })
    return chain


def _summarize_chain(chain: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid = [r for r in chain if "error" not in r]
    calls = [r for r in valid if "콜" in str(r.get("call_put", ""))]
    puts  = [r for r in valid if "풋" in str(r.get("call_put", ""))]
    yms = sorted(set(r["ym"] for r in valid if r.get("ym")))
    strikes = sorted(set(r["strike"] for r in valid if r.get("strike", 0) > 0))

    return {
        "total_count": len(chain),
        "valid_count": len(valid),
        "error_count": len(chain) - len(valid),
        "call_count": len(calls),
        "put_count": len(puts),
        "yms": yms,
        "strike_count": len(strikes),
        "strike_min": min(strikes) if strikes else None,
        "strike_max": max(strikes) if strikes else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Cybos CpOptionCode (옵션 체인)")
    parser.add_argument("--ensure-login", action="store_true",
                        help="Cybos 자동 로그인 먼저 실행")
    parser.add_argument("--dump-all", action="store_true",
                        help="체인 전체를 JSON으로 덤프 (많으면 큼)")
    parser.add_argument("--ym-filter", type=str, default="",
                        help="특정 행사월만 필터 (예: 202606)")
    parser.add_argument("--output-json", type=str, default="",
                        help="JSON 파일로 저장할 경로")
    args = parser.parse_args()

    _ensure_runtime()

    try:
        import pythoncom
        from win32com.client import Dispatch
    except ImportError as exc:
        raise RuntimeError("pywin32 import failed") from exc

    pythoncom.CoInitialize()
    obj = None
    cp_cybos = None
    try:
        if args.ensure_login:
            print("[INFO] ensure_cybos_login() start")
            if not ensure_cybos_login(require_trade_init=False):
                raise RuntimeError("Cybos 로그인 실패")

        cp_cybos = Dispatch("CpUtil.CpCybos")
        if not bool(cp_cybos.IsConnect):
            raise RuntimeError("Cybos 미연결")

        try:
            obj = Dispatch("CpUtil.CpOptionCode")
        except Exception as exc:
            raise RuntimeError(
                "CpOptionCode Dispatch 실패. "
                "ProgID=CpUtil.CpOptionCode 가 등록되어 있는지 확인하세요."
            ) from exc

        count = obj.GetCount()
        print(f"[INFO] 옵션 종목 총 개수: {count}")

        chain = _dump_chain(obj, count)
        summary = _summarize_chain(chain)

        print(f"\n=== 체인 요약 ===")
        print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))

        # 행사월별 분포
        ym_dist: Dict[str, int] = {}
        valid = [r for r in chain if "error" not in r]
        for r in valid:
            ym = r.get("ym", "?")
            ym_dist[ym] = ym_dist.get(ym, 0) + 1
        print(f"\n=== 행사월 분포 ===")
        for ym in sorted(ym_dist.keys()):
            label = f"근월물 ★" if ym == (sorted(ym_dist.keys()) or [ym])[0] else ""
            print(f"  {ym}: {ym_dist[ym]} 종목 {label}")

        # ATM 근사 찾기 (기초자산가 없으므로 행사가 기준으로만)
        # 추후 OptionMst에서 기초자산가를 얻으면 정확한 ATM 식별 가능
        if summary["strike_min"] is not None:
            print(f"\n=== 행사가 범위 ===")
            print(f"  최저: {summary['strike_min']:.1f}  최고: {summary['strike_max']:.1f}")
            print(f"  전체 행사가 수: {summary['strike_count']}")

        # 샘플 출력 (처음 5개, 끝 5개)
        print(f"\n=== 체인 샘플 (처음 5 + 마지막 5) ===")
        sample = valid[:5] + valid[-5:] if len(valid) > 10 else valid
        for r in sample:
            print(f"  [{r['index']:4d}] {r['code']:12s} {r['call_put']:4s} "
                  f"YM={r['ym']}  strike={r['strike']:7.1f}")

        # ym_filter 적용
        if args.ym_filter:
            filtered = [r for r in valid if r.get("ym") == args.ym_filter]
            print(f"\n=== 필터: YM={args.ym_filter} → {len(filtered)} 종목 ===")
            for r in filtered:
                print(f"  [{r['index']:4d}] {r['code']:12s} {r['call_put']:4s} "
                      f"strike={r['strike']:7.1f}")

        # 전체 덤프
        if args.dump_all:
            print(f"\n=== 체인 전체 ({len(valid)} 종목) ===")
            print(json.dumps(valid, ensure_ascii=False, indent=2, default=str))

        # 파일 저장
        if args.output_json:
            output = {
                "summary": summary,
                "ym_distribution": ym_dist,
                "chain": valid,
            }
            with open(args.output_json, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n[INFO] 저장 완료: {args.output_json}")

        return 0
    finally:
        obj = None
        cp_cybos = None
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
