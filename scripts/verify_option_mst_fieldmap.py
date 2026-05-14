from __future__ import annotations

"""OptionMst HeaderValue 필드맵 교차 검증 스크립트.

복수의 옵션 종목코드(Call/Put, ATM/OTM)에 대해 OptionMst 모든 HeaderValue를
덤프하고 상호 비교하여 문서상 필드맵이 실제와 일치하는지 검증한다.

사용법:
    python scripts/verify_option_mst_fieldmap.py --ensure-login ^
        --codes 201VA355 301VA355 201VA380 301VA380
"""

import argparse
import json
import platform
import struct
import sys
import time
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
        raise RuntimeError("32-bit Python required")


# ── 알려진 필드맵 (문서 기준) ────────────────────────────────────
KNOWN_FIELD_MAP = {
    6:   "행사가 (strike)",
    13:  "잔존일수",
    15:  "콜/풋 구분코드 (51=콜, 50=풋)",
    36:  "CD금리 (무위험 이자율)",
    37:  "전일 미결제약정",
    53:  "내재변동성 (증거금용)",
    93:  "현재가",
    97:  "누적체결수량",
    99:  "현재 미결제약정",
    100: "OI 구분 (0=전일확정/1=당일잠정/2=당일확정)",
    108: "내재변동성 (종목별)",
    109: "Delta (백분율, ÷100)",
    110: "Gamma (백분율, ÷100)",
    111: "Theta",
    112: "Vega",
    113: "Rho",
    114: "이론가 (추정)",
    115: "변동성 (고정 참조값)",
}


def _dump_all_headers(obj, limit: int = 140) -> Dict[int, Any]:
    """모든 HeaderValue 인덱스 덤프."""
    headers: Dict[int, Any] = {}
    for idx in range(limit):
        try:
            value = obj.GetHeaderValue(idx)
            headers[idx] = value
        except Exception:
            pass
    return headers


def _collect_snapshots(codes: List[str], header_limit: int = 140) -> Dict[str, Any]:
    """여러 종목코드에 대해 OptionMst 스냅샷 수집."""
    from win32com.client import Dispatch

    mst = Dispatch("Dscbo1.OptionMst")
    results: Dict[str, Any] = {}

    for i, code in enumerate(codes):
        print(f"  [{i+1}/{len(codes)}] {code} ...", end=" ", flush=True)
        try:
            mst.SetInputValue(0, code)
            mst.BlockRequest()

            status = _safe_str(mst.GetDibStatus())
            if status != "0":
                msg = _safe_str(mst.GetDibMsg1())
                print(f"DibStatus={status} msg={msg}")
                results[code] = {"code": code, "error": f"DibStatus={status}", "msg": msg}
                continue

            headers = _dump_all_headers(mst, header_limit)
            results[code] = {
                "code": code,
                "status": status,
                "headers": headers,
            }
            print(f"OK ({len(headers)} 필드)")
        except Exception as exc:
            print(f"ERR: {exc}")
            results[code] = {"code": code, "error": str(exc)}

        if i < len(codes) - 1:
            time.sleep(0.05)

    return results


def _validate_greeks(snapshots: Dict[str, Any], chain_path: str = "data/option_chain.json") -> List[str]:
    """그릭스 필드 검증:
    - Gamma(110): 항상 > 0 (long position 기준)
    - Delta(109): 콜이면 > 0, 풋이면 < 0 (콜/풋은 체인 캐시에서 조회)
    - 체인 캐시 없으면 delta 부호만으로 추정
    """
    # 체인 캐시 로드 시도
    call_put_map: Dict[str, str] = {}
    try:
        with open(chain_path, "r", encoding="utf-8") as f:
            chain_data = json.load(f)
        for r in chain_data.get("chain", []):
            call_put_map[r["code"]] = str(r.get("call_put", ""))
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    issues: List[str] = []

    for code, snap in snapshots.items():
        if snap.get("error"):
            continue
        h = snap["headers"]

        gamma_110 = _safe_float(h.get(110, 0))
        delta_109 = _safe_float(h.get(109, 0))
        price_93  = _safe_float(h.get(93, 0))

        if price_93 <= 0:
            issues.append(f"{code}: 현재가(93)={price_93} — 비정상 (0 이하)")
            continue

        # 콜/풋 판별
        cp = call_put_map.get(code, "")
        is_call = "콜" in cp
        is_put  = "풋" in cp

        if not is_call and not is_put:
            # delta 부호로 추정
            if delta_109 > 0.05:
                is_call = True
            elif delta_109 < -0.05:
                is_put = True

        # Gamma 검증
        if gamma_110 <= 0:
            issues.append(f"{code}: Gamma(110)={gamma_110:.6f} — 비정상 (≤0)")

        # Delta 검증
        if is_call and delta_109 <= -0.01:
            issues.append(f"{code}: [콜] Delta(109)={delta_109:.4f} — 콜인데 음수")
        elif is_put and delta_109 >= 0.01:
            issues.append(f"{code}: [풋] Delta(109)={delta_109:.4f} — 풋인데 양수")

    return issues


def _validate_oi_fields(snapshots: Dict[str, Any]) -> List[str]:
    """OI 필드 검증: oi ≥ oi_prev (장중 당연), oi_state ∈ {0,1,2}"""
    issues: List[str] = []
    for code, snap in snapshots.items():
        if snap.get("error"):
            continue
        h = snap["headers"]
        oi       = _safe_int(h.get(99, 0))
        oi_prev  = _safe_int(h.get(37, 0))
        oi_state = _safe_str(h.get(100, ""))

        if oi > 0 and oi_prev > 0 and oi < oi_prev:
            # 장중 OI는 전일보다 클 수 있지만, 반드시 그런 것은 아님 (감소 가능)
            # 경고만
            issues.append(f"{code}: OI(99)={oi} < 전일OI(37)={oi_prev} (OI 감소)")

        if oi_state and oi_state not in ("0", "1", "2"):
            issues.append(f"{code}: OI구분(100)={oi_state!r} — 예상밖 값 (0/1/2 아님)")

    return issues


def _compare_cross_section(snapshots: Dict[str, Any]) -> Dict[str, Any]:
    """콜/풋 간 교차 비교: 필드별로 콜/풋 차이가 의미 있는지 확인."""
    # 체인 캐시에서 콜/풋 구분 로드
    call_put_map: Dict[str, str] = {}
    try:
        with open("data/option_chain.json", "r", encoding="utf-8") as f:
            chain_data = json.load(f)
        for r in chain_data.get("chain", []):
            call_put_map[r["code"]] = str(r.get("call_put", ""))
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    calls = {c: s for c, s in snapshots.items()
             if not s.get("error") and "콜" in call_put_map.get(c, "")}
    puts  = {c: s for c, s in snapshots.items()
             if not s.get("error") and "풋" in call_put_map.get(c, "")}

    # 체인 캐시로 구분 안 되면 delta 부호로 추정
    if not calls and not puts:
        for c, s in snapshots.items():
            if s.get("error"):
                continue
            delta = _safe_float(s["headers"].get(109, 0))
            if delta > 0.05:
                calls[c] = s
            elif delta < -0.05:
                puts[c] = s

    if not calls or not puts:
        return {"error": "콜/풋 스냅샷 부족"}

    # 모든 콜/풋에서 공통으로 존재하는 HeaderValue 인덱스
    call_keys = set()
    put_keys  = set()
    for s in calls.values():
        call_keys.update(s["headers"].keys())
    for s in puts.values():
        put_keys.update(s["headers"].keys())
    common = sorted(call_keys & put_keys)

    field_analysis: Dict[int, Dict[str, Any]] = {}
    for idx in common:
        call_vals = [_safe_float(s["headers"].get(idx, 0)) for s in calls.values()]
        put_vals  = [_safe_float(s["headers"].get(idx, 0)) for s in puts.values()]

        call_avg = sum(call_vals) / len(call_vals) if call_vals else 0
        put_avg  = sum(put_vals) / len(put_vals) if put_vals else 0
        diff     = call_avg - put_avg

        # 유의미한 차이만 기록
        if abs(diff) > 0.0001:
            known = KNOWN_FIELD_MAP.get(idx, "???")
            field_analysis[idx] = {
                "known": known,
                "call_avg": round(call_avg, 6),
                "put_avg": round(put_avg, 6),
                "diff": round(diff, 6),
            }

    return field_analysis


def _suggest_field_mapping(snapshots: Dict[str, Any]) -> List[str]:
    """HeaderValue 인덱스 중 알려지지 않았지만 유의미한 값이 있는 필드 제안."""
    suggestions: List[str] = []

    # 모든 스냅샷에서 공통으로 존재하는 키
    all_keys: Optional[set] = None
    for snap in snapshots.values():
        if snap.get("error"):
            continue
        keys = set(snap["headers"].keys())
        if all_keys is None:
            all_keys = keys
        else:
            all_keys &= keys

    if not all_keys:
        return suggestions

    for idx in sorted(all_keys):
        if idx in KNOWN_FIELD_MAP:
            continue

        # 값의 다양성 확인 (모든 종목에서 동일하면 상수/공통값, 다르면 종목별 값)
        vals = []
        for snap in snapshots.values():
            if snap.get("error"):
                continue
            v = snap["headers"].get(idx)
            if v is not None:
                vals.append(_safe_float(v))

        if not vals:
            continue

        unique = len(set(vals))
        if unique > 1:
            # 종목마다 다른 값 — 의미 있는 필드 가능성
            suggestions.append(
                f"  HeaderValue({idx:>3d}): range={min(vals)}~{max(vals)} "
                f"(unique={unique}/{len(vals)}) — 종목별 상이, 필드 확인 필요"
            )

    return suggestions


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OptionMst HeaderValue 필드맵 교차 검증"
    )
    parser.add_argument("--ensure-login", action="store_true",
                        help="Cybos 자동 로그인 먼저 실행")
    parser.add_argument("--codes", nargs="+", required=True,
                        help="검증할 옵션 종목코드 (최소 콜 1개 + 풋 1개, ATM/OTM 다양하게)")
    parser.add_argument("--header-limit", type=int, default=140,
                        help="HeaderValue 덤프 최대 인덱스 (기본 140)")
    parser.add_argument("--output-json", type=str, default="",
                        help="결과 저장할 JSON 경로")
    args = parser.parse_args()

    if len(args.codes) < 2:
        print("[ERROR] 최소 2개 종목코드 필요 (콜+풋 비교용)")
        return 1

    _ensure_runtime()

    try:
        import pythoncom
        from win32com.client import Dispatch
    except ImportError:
        raise RuntimeError("pywin32 import failed")

    pythoncom.CoInitialize()
    cp_cybos = None
    try:
        if args.ensure_login:
            print("[INFO] Cybos 로그인 중...")
            if not ensure_cybos_login(require_trade_init=False):
                raise RuntimeError("Cybos 로그인 실패")

        cp_cybos = Dispatch("CpUtil.CpCybos")
        if not bool(cp_cybos.IsConnect):
            raise RuntimeError("Cybos 미연결")

        print(f"[INFO] {len(args.codes)}개 종목코드 OptionMst 스냅샷 수집...")
        snapshots = _collect_snapshots(args.codes, args.header_limit)

        # ── 검증 결과 ────────────────────────────────────────────
        print(f"\n{'='*60}")
        print(f"  OptionMst 필드맵 검증 결과")
        print(f"{'='*60}")

        # 1. 그릭스 검증
        print(f"\n── 그릭스 검증 (Delta/Gamma) ──")
        greek_issues = _validate_greeks(snapshots)
        if greek_issues:
            for issue in greek_issues:
                print(f"  ⚠ {issue}")
            print(f"  → {len(greek_issues)}건 경고/오류")
        else:
            print(f"  ✅ Delta(109), Gamma(110) 정상 (콜=양/풋=음 부호 일치)")

        # 2. OI 필드 검증
        print(f"\n── OI 필드 검증 ──")
        oi_issues = _validate_oi_fields(snapshots)
        if oi_issues:
            for issue in oi_issues:
                print(f"  ⚠ {issue}")
        else:
            print(f"  ✅ OI(99), 전일OI(37), OI구분(100) 정상")

        # 3. 콜/풋 교차 비교
        print(f"\n── 콜/풋 교차 비교 (유의미한 차이 필드) ──")
        cross = _compare_cross_section(snapshots)
        if "error" in cross:
            print(f"  ⚠ {cross['error']}")
        else:
            for idx, info in sorted(cross.items()):
                print(f"  HV({idx:>3d}) {info['known']:16s}  "
                      f"call={info['call_avg']:>12.6f}  put={info['put_avg']:>12.6f}  "
                      f"Δ={info['diff']:+.6f}")

        # 4. 미식별 필드 제안
        print(f"\n── 미식별 유의미 필드 제안 ──")
        suggestions = _suggest_field_mapping(snapshots)
        if suggestions:
            for s in suggestions:
                print(s)
        else:
            print(f"  (모든 공통 필드가 알려진 맵에 포함됨)")

        # 5. 종목별 요약
        print(f"\n── 종목별 요약 ──")
        print(f"  {'코드':12s} {'현재가(93)':>10s} {'OI(99)':>8s} "
              f"{'Delta(109)':>10s} {'Gamma(110)':>12s} {'Vol(115)':>8s} "
              f"{'잔존일(13)':>8s} {'ATM(15)':>6s} {'기초(17)':>10s}")
        print(f"  {'-'*12} {'-'*10} {'-'*8} {'-'*10} {'-'*12} {'-'*8} {'-'*8} {'-'*6} {'-'*10}")
        for code, snap in snapshots.items():
            if snap.get("error"):
                print(f"  {code:12s} [ERROR] {snap['error'][:50]}")
                continue
            h = snap["headers"]
            print(f"  {code:12s} "
                  f"{_safe_float(h.get(93,0)):>10.2f} "
                  f"{_safe_int(h.get(99,0)):>8d} "
                  f"{_safe_float(h.get(109,0)):>10.4f} "
                  f"{_safe_float(h.get(110,0)):>12.6f} "
                  f"{_safe_float(h.get(115,0)):>8.2f} "
                  f"{_safe_int(h.get(13,0)):>8d} "
                  f"{_safe_int(h.get(15,0)):>6d} "
                  f"{_safe_float(h.get(17,0)):>10.2f}")

        # ── JSON 저장 ────────────────────────────────────────────
        if args.output_json:
            output = {
                "snapshots": {c: {"code": s["code"], "headers": s.get("headers", {}),
                                  "error": s.get("error")}
                              for c, s in snapshots.items()},
                "greek_issues": greek_issues,
                "oi_issues": oi_issues,
                "cross_section": cross,
                "suggestions": [s.strip() for s in suggestions],
            }
            try:
                import os
                os.makedirs(os.path.dirname(args.output_json) or ".", exist_ok=True)
                with open(args.output_json, "w", encoding="utf-8") as f:
                    json.dump(output, f, ensure_ascii=False, indent=2, default=str)
                print(f"\n[INFO] 저장 완료: {args.output_json}")
            except Exception as exc:
                print(f"\n[ERROR] 저장 실패: {exc}")

        print(f"\n{'='*60}")
        return 0 if not greek_issues else 1

    finally:
        cp_cybos = None
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
