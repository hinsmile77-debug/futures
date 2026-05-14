from __future__ import annotations

"""Cybos 기반 KOSPI200 옵션 지표 수집 스크립트.

PCR(OI 기준), ATM OI, GEX(Gamma Exposure)를 계산한다.

사용법 (Windows Cybos Plus 환경):
    python scripts/collect_option_metrics.py --ensure-login --output-json data/option_metrics.json
    python scripts/collect_option_metrics.py --ensure-login --ym-filter 202606
"""

import argparse
import json
import platform
import struct
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from ensure_cybos_login import ensure_cybos_login

# ── 상수 ─────────────────────────────────────────────────────────
FUTURES_PT_VALUE = 250_000       # 1pt = 250,000원 (KOSPI200 옵션)
OPTION_MULTIPLIER = 250_000      # KOSPI200 옵션 승수
SPOT_SCALE = 1.0                 # GEX 스케일 (운영 정의 필요시 조정)

# OptionMst GetHeaderValue 인덱스 맵 (2026-05-13 검증 완료)
HV_PRICE       = 93   # 현재가 ✅
HV_VOLUME      = 97   # 누적체결수량 ✅
HV_OI          = 99   # 현재 미결제약정 ✅
HV_OI_PREV     = 37   # 전일 미결제약정 ✅
HV_OI_STATE    = 100  # OI 구분 (미검증, 0=전일확정/1=당일잠정/2=당일확정)
HV_DELTA       = 109  # Delta ✅ (백분율, ÷100)
HV_GAMMA       = 110  # Gamma ✅ (백분율, ÷100)
HV_THETA       = 111  # Theta ✅
HV_VEGA        = 112  # Vega (미검증)
HV_RHO         = 113  # Rho ✅
HV_VOL         = 115  # 변동성 (고정 참조값, 모든 종목 동일)
HV_IV          = 108  # 내재변동성 (종목별 상이, 추정)
HV_THEO_PRICE  = 114  # 이론가 (추정, 종목별 상이)
HV_DTE         = 13   # 잔존일수 ✅
HV_RF_RATE     = 36   # CD금리 (미검증)
HV_CP_FLAG     = 15   # 콜/풋 구분코드 (51=콜, 50=풋 — ATM 구분 아님)
# HV(17) = 날짜값 — 기초자산가 아님. spot은 외부에서 주입.


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


# ═════════════════════════════════════════════════════════════════
# STEP 1: 옵션 체인 수집 (CpOptionCode)
# ═════════════════════════════════════════════════════════════════

def fetch_option_chain(option_code_obj) -> List[Dict[str, Any]]:
    """CpOptionCode.GetCount() + GetData(type, index) 순회.

    Returns:
        List[dict]: 각 원소 = {code, call_put, ym, strike}
    """
    count = option_code_obj.GetCount()
    chain: List[Dict[str, Any]] = []
    for idx in range(count):
        try:
            code   = _safe_str(option_code_obj.GetData(0, idx))
            cp     = _safe_str(option_code_obj.GetData(2, idx))
            ym     = _safe_str(option_code_obj.GetData(3, idx))
            strike = _safe_float(option_code_obj.GetData(4, idx), default=0.0)
            chain.append({
                "index": idx,
                "code": code,
                "call_put": cp.upper() if cp else "",
                "ym": ym,
                "strike": strike,
            })
        except Exception as exc:
            # 인덱스 초과 등은 무시
            pass
    return chain


def filter_front_month(chain: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """가장 가까운 행사월(yyyymm) 종목만 필터."""
    if not chain:
        return []
    yms = sorted(set(r["ym"] for r in chain if r.get("ym")))
    if not yms:
        return chain
    front_ym = yms[0]
    return [r for r in chain if r.get("ym") == front_ym]


def filter_by_ym(chain: List[Dict[str, Any]], ym: str) -> List[Dict[str, Any]]:
    """특정 행사월(yyyymm) 종목만 필터."""
    return [r for r in chain if r.get("ym") == ym]


def filter_atm_range(
    chain: List[Dict[str, Any]],
    spot: float,
    window_pt: float = 30.0,
) -> List[Dict[str, Any]]:
    """기초자산가 ±window_pt 범위의 행사가만 필터.

    KOSPI200 옵션은 2.5pt 간격으로 행사가가 존재하므로,
    ATM ±30pt = 약 24개 행사가 (콜+풋 합쳐 48종목).
    """
    lo = spot - window_pt
    hi = spot + window_pt
    return [r for r in chain if lo <= r.get("strike", 0) <= hi]


# ═════════════════════════════════════════════════════════════════
# STEP 2: 종목별 OptionMst 스냅샷 수집
# ═════════════════════════════════════════════════════════════════

def fetch_option_mst_snapshot(option_mst_obj, code: str) -> Dict[str, Any]:
    """OptionMst.SetInputValue(0, code) → BlockRequest() → GetHeaderValue().

    Returns:
        dict: 수집된 필드값
    """
    snapshot: Dict[str, Any] = {"code": code}
    try:
        option_mst_obj.SetInputValue(0, code)
        option_mst_obj.BlockRequest()

        status = _safe_str(option_mst_obj.GetDibStatus())
        snapshot["dib_status"] = status
        if status != "0":
            snapshot["dib_msg"] = _safe_str(option_mst_obj.GetDibMsg1())
            snapshot["error"] = f"DibStatus={status}"
            return snapshot

        snapshot["price"]      = _safe_float(option_mst_obj.GetHeaderValue(HV_PRICE))
        snapshot["volume"]     = _safe_int(option_mst_obj.GetHeaderValue(HV_VOLUME))
        snapshot["oi"]         = _safe_int(option_mst_obj.GetHeaderValue(HV_OI))
        snapshot["oi_prev"]    = _safe_int(option_mst_obj.GetHeaderValue(HV_OI_PREV))
        snapshot["oi_state"]   = _safe_str(option_mst_obj.GetHeaderValue(HV_OI_STATE))
        snapshot["delta"]      = _safe_float(option_mst_obj.GetHeaderValue(HV_DELTA))
        snapshot["gamma"]      = _safe_float(option_mst_obj.GetHeaderValue(HV_GAMMA))
        snapshot["theta"]      = _safe_float(option_mst_obj.GetHeaderValue(HV_THETA))
        snapshot["vega"]       = _safe_float(option_mst_obj.GetHeaderValue(HV_VEGA))
        snapshot["rho"]        = _safe_float(option_mst_obj.GetHeaderValue(HV_RHO))
        snapshot["vol"]        = _safe_float(option_mst_obj.GetHeaderValue(HV_VOL))
        snapshot["iv"]         = _safe_float(option_mst_obj.GetHeaderValue(HV_IV))
        snapshot["theo_price"] = _safe_float(option_mst_obj.GetHeaderValue(HV_THEO_PRICE))
        snapshot["dte"]        = _safe_int(option_mst_obj.GetHeaderValue(HV_DTE))
        snapshot["rf_rate"]    = _safe_float(option_mst_obj.GetHeaderValue(HV_RF_RATE))

    except Exception as exc:
        snapshot["error"] = str(exc)

    return snapshot


def collect_chain_snapshots(
    option_mst_obj,
    chain: List[Dict[str, Any]],
    pause_ms: int = 50,
) -> List[Dict[str, Any]]:
    """전체 체인에 대해 OptionMst 스냅샷 수집.

    Args:
        pause_ms: 각 종목 사이 대기 (ms, Cybos 부하 방지)
    """
    snapshots: List[Dict[str, Any]] = []
    total = len(chain)
    for i, row in enumerate(chain):
        code = row["code"]
        snap = fetch_option_mst_snapshot(option_mst_obj, code)
        # 체인 정보 병합
        snap["call_put"] = row.get("call_put", "")
        snap["ym"]       = row.get("ym", "")
        snap["strike"]   = row.get("strike", 0.0)
        snapshots.append(snap)

        if (i + 1) % 10 == 0 or i == total - 1:
            print(f"  [{i+1}/{total}] {code} price={snap.get('price', 0):.1f} "
                  f"oi={snap.get('oi', 0)} gamma={snap.get('gamma', 0):.4f}",
                  flush=True)
        if pause_ms > 0 and i < total - 1:
            time.sleep(pause_ms / 1000.0)

    return snapshots


# ═════════════════════════════════════════════════════════════════
# STEP 3: 지표 계산
# ═════════════════════════════════════════════════════════════════

def _is_call(row: Dict[str, Any]) -> bool:
    cp = str(row.get("call_put", ""))
    return "콜" in cp or cp.upper().startswith("C")


def _is_put(row: Dict[str, Any]) -> bool:
    cp = str(row.get("call_put", ""))
    return "풋" in cp or cp.upper().startswith("P")


def compute_pcr_oi(snapshots: List[Dict[str, Any]]) -> float:
    """PCR (Put/Call Ratio) — OI 기준.

    PCR_OI = Sum(Put_OI) / Sum(Call_OI)
    분모가 0이면 0.0 반환.
    """
    call_oi = sum(r["oi"] for r in snapshots if _is_call(r) and not r.get("error"))
    put_oi  = sum(r["oi"] for r in snapshots if _is_put(r) and not r.get("error"))
    if call_oi == 0:
        return 0.0
    return put_oi / call_oi


def find_atm_row(snapshots: List[Dict[str, Any]], spot: float) -> Tuple[Optional[Dict], Optional[Dict]]:
    """ATM 종목 찾기 (기초자산가에 가장 가까운 행사가).

    spot은 외부에서 주입 (KOSPI200 선물 현재가).
    OptionMst는 기초자산가를 제공하지 않음.

    Returns:
        (atm_call, atm_put) — 각각 None 일 수 있음
    """
    calls = [r for r in snapshots if _is_call(r) and not r.get("error") and r.get("oi", 0) > 0]
    puts  = [r for r in snapshots if _is_put(r) and not r.get("error") and r.get("oi", 0) > 0]

    atm_call = None
    atm_put  = None

    if spot > 0:
        if calls:
            calls_sorted = sorted(calls, key=lambda r: abs(r["strike"] - spot))
            atm_call = calls_sorted[0]
        if puts:
            puts_sorted = sorted(puts, key=lambda r: abs(r["strike"] - spot))
            atm_put = puts_sorted[0]

    return atm_call, atm_put


def compute_atm_oi(snapshots: List[Dict[str, Any]], spot: float) -> Dict[str, Any]:
    """ATM OI 및 ATM PCR 계산."""
    atm_call, atm_put = find_atm_row(snapshots, spot)
    atm_call_oi = atm_call["oi"] if atm_call else 0
    atm_put_oi  = atm_put["oi"] if atm_put else 0
    atm_pcr_oi  = atm_put_oi / atm_call_oi if atm_call_oi > 0 else 0.0

    return {
        "atm_call_oi": atm_call_oi,
        "atm_put_oi": atm_put_oi,
        "atm_pcr_oi": round(atm_pcr_oi, 6),
        "atm_strike": atm_call["strike"] if atm_call else None,
        "atm_spot": spot,
    }


def compute_gex(
    snapshots: List[Dict[str, Any]],
    spot: Optional[float] = None,
    multiplier: float = OPTION_MULTIPLIER,
    scale: float = SPOT_SCALE,
) -> Dict[str, Any]:
    """GEX (Gamma Exposure) 계산.

    UnitGEX_i = gamma_i * OI_i * multiplier * spot * scale
    TotalGEX  = Sum(Call_GEX) - Sum(Put_GEX)

    scale 은 spot 가격의 영향을 조정 — 일반적으로 1.0 사용.
    GEX 단위는 KRW (gamma * OI * 승수 * 기초자산가).
    결과가 너무 크면 1e9(십억) 단위로 나누어 표시.

    Returns:
        dict: {total_gex, call_gex, put_gex, total_gex_bn, ...}
    """
    if spot is None:
        spot_candidates = [r["spot"] for r in snapshots if r.get("spot", 0) > 0]
        spot = spot_candidates[0] if spot_candidates else 0.0

    call_gex = 0.0
    put_gex  = 0.0

    for r in snapshots:
        if r.get("error"):
            continue
        oi    = r.get("oi", 0)
        gamma = r.get("gamma", 0.0)
        if oi <= 0:
            continue

        unit_gex = gamma * oi * multiplier * spot * scale
        if _is_call(r):
            call_gex += unit_gex
        elif _is_put(r):
            put_gex += unit_gex

    total_gex = call_gex - put_gex

    return {
        "total_gex": total_gex,
        "call_gex": call_gex,
        "put_gex": put_gex,
        "total_gex_bn": round(total_gex / 1e9, 6) if total_gex != 0 else 0.0,
        "spot_used": spot,
        "multiplier": multiplier,
        "scale": scale,
    }


def assess_oi_quality(snapshots: List[Dict[str, Any]]) -> str:
    """OI 품질 평가.

    - '1': 당일 잠정 (신뢰도 하향)
    - '2': 당일 확정 (신뢰도 양호)
    - '0': 전일 확정
    """
    if not snapshots:
        return "no_data"

    states = [str(r.get("oi_state", "")).strip() for r in snapshots if not r.get("error")]
    if not states:
        return "unknown"

    if all(s == "2" or s == "0" for s in states if s):
        return "confirmed"
    if all(s == "1" for s in states):
        return "provisional"
    return "mixed"


# ═════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="KOSPI200 옵션 지표 수집 (Cybos): PCR / ATM OI / GEX"
    )
    parser.add_argument("--ensure-login", action="store_true",
                        help="Cybos 자동 로그인 먼저 실행")
    parser.add_argument("--ym-filter", type=str, default="",
                        help="특정 행사월만 (예: 202606, 미지정시 근월물)")
    parser.add_argument("--skip-chain-cache", action="store_true",
                        help="체인 캐시 파일 무시하고 새로 수집 (data/option_chain.json)")
    parser.add_argument("--output-json", type=str, default="",
                        help="결과 저장할 JSON 경로")
    parser.add_argument("--pause-ms", type=int, default=50,
                        help="종목 간 대기 시간 (ms, 기본 50)")
    parser.add_argument("--spot-override", type=float, default=0.0,
                        help="KOSPI200 지수 수동 지정 (ATM/GEX 계산, 0=자동추정)")
    parser.add_argument("--full-scan", action="store_true",
                        help="근월물 외 전체 종목 스캔 (시간 소요)")
    parser.add_argument("--atm-window", type=float, default=30.0,
                        help="ATM ±N pt 범위만 수집 (기본 30, 0=전체 근월물)")
    args = parser.parse_args()

    _ensure_runtime()

    try:
        import pythoncom
        from win32com.client import Dispatch
    except ImportError as exc:
        raise RuntimeError("pywin32 import failed") from exc

    pythoncom.CoInitialize()
    cp_cybos    = None
    chain_obj   = None
    mst_obj     = None

    try:
        # ── Cybos 연결 ──────────────────────────────────────────
        if args.ensure_login:
            print("[INFO] Cybos 로그인 중...")
            if not ensure_cybos_login(require_trade_init=False):
                raise RuntimeError("Cybos 로그인 실패")

        cp_cybos = Dispatch("CpUtil.CpCybos")
        if not bool(cp_cybos.IsConnect):
            raise RuntimeError("Cybos 미연결")

        # ── 체인 수집 (CpOptionCode) ─────────────────────────────
        chain_path = "data/option_chain.json"  # BASE_DIR 기준 상대경로
        chain_raw: List[Dict[str, Any]] = []

        if not args.skip_chain_cache:
            try:
                with open(chain_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                chain_raw = saved.get("chain", [])
                if chain_raw:
                    print(f"[INFO] 체인 캐시 로드: {len(chain_raw)} 종목 ({chain_path})")
            except (FileNotFoundError, json.JSONDecodeError):
                pass

        if not chain_raw:
            print("[INFO] CpOptionCode 체인 조회 중...")
            chain_obj = Dispatch("CpUtil.CpOptionCode")
            chain_raw = fetch_option_chain(chain_obj)
            print(f"[INFO] 체인 수집 완료: {len(chain_raw)} 종목")

            # 체인 캐시 저장
            yms = sorted(set(r["ym"] for r in chain_raw if r.get("ym")))
            summary = {
                "asof": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(chain_raw),
                "yms": yms,
            }
            cache = {"summary": summary, "chain": chain_raw}
            try:
                import os
                os.makedirs(os.path.dirname(chain_path) or ".", exist_ok=True)
                with open(chain_path, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2, default=str)
                print(f"[INFO] 체인 캐시 저장: {chain_path}")
            except Exception as exc:
                print(f"[WARN] 체인 캐시 저장 실패: {exc}")

        # ── 대상 종목 선별 ───────────────────────────────────────
        if args.full_scan:
            target = chain_raw
        elif args.ym_filter:
            target = filter_by_ym(chain_raw, args.ym_filter)
        else:
            target = filter_front_month(chain_raw)

        # ── ATM 윈도우 필터 ──────────────────────────────────────
        if args.atm_window > 0 and target:
            spot_for_filter = args.spot_override
            if spot_for_filter <= 0:
                # 체인에서 대략적인 ATM 추정 (행사가 중간값)
                strikes = sorted(set(r["strike"] for r in target if r.get("strike", 0) > 0))
                if strikes:
                    spot_for_filter = strikes[len(strikes) // 2]
            if spot_for_filter > 0:
                before = len(target)
                target = filter_atm_range(target, spot_for_filter, args.atm_window)
                print(f"[INFO] ATM 윈도우 적용: spot≈{spot_for_filter:.1f} ±{args.atm_window}pt "
                      f"→ {len(target)}/{before} 종목")

        print(f"[INFO] 대상 종목: {len(target)}개")

        if not target:
            print("[ERROR] 대상 종목이 없습니다.")
            return 1

        # ── OptionMst 일괄 스냅샷 ─────────────────────────────────
        print(f"[INFO] OptionMst 스냅샷 수집 시작 (pause={args.pause_ms}ms)...")
        mst_obj = Dispatch("Dscbo1.OptionMst")
        t0 = time.time()
        snapshots = collect_chain_snapshots(mst_obj, target, pause_ms=args.pause_ms)
        elapsed = time.time() - t0
        print(f"[INFO] 스냅샷 수집 완료: {len(snapshots)}종목 / {elapsed:.1f}초")

        error_count = sum(1 for s in snapshots if s.get("error"))
        if error_count > 0:
            print(f"[WARN] 오류 발생: {error_count}/{len(snapshots)} 종목")
            for s in snapshots:
                if s.get("error"):
                    print(f"  - {s['code']}: {s['error']}")

        # ── 기초자산가(spot) 결정 ─────────────────────────────────
        spot = args.spot_override
        if spot <= 0:
            # spot 미지정 시: 콜 delta가 50%에 가장 가까운 행사가로 추정
            calls_with_delta = [(r["strike"], abs(r.get("delta", 0) - 50.0))
                               for r in snapshots if _is_call(r) and not r.get("error")]
            if calls_with_delta:
                spot = min(calls_with_delta, key=lambda x: x[1])[0]
                print(f"[INFO] spot 미지정 → delta 50% 근접 행사가로 추정: {spot:.1f}")

        # ── 지표 계산 ────────────────────────────────────────────
        pcr_oi     = compute_pcr_oi(snapshots)
        atm        = compute_atm_oi(snapshots, spot)
        gex        = compute_gex(snapshots, spot=spot if spot > 0 else None)
        quality    = assess_oi_quality(snapshots)

        # ── 결과 출력 ────────────────────────────────────────────
        result = {
            "asof": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target_ym": args.ym_filter or (target[0]["ym"] if target else ""),
            "snapshot_count": len(snapshots),
            "error_count": error_count,
            "pcr_oi": round(pcr_oi, 6),
            "atm": atm,
            "gex": gex,
            "oi_quality": quality,
        }

        print(f"\n{'='*60}")
        print(f"  옵션 지표 수집 결과")
        print(f"{'='*60}")
        print(f"  수집시각: {result['asof']}")
        print(f"  대상 행사월: {result['target_ym']}")
        print(f"  종목 수: {result['snapshot_count']} (오류: {result['error_count']})")
        print(f"  OI 품질: {result['oi_quality']}")
        print()
        print(f"  ── PCR ──")
        print(f"  PCR (OI): {result['pcr_oi']:.4f}")
        print()
        print(f"  ── ATM ──")
        print(f"  ATM 행사가: {atm['atm_strike']}  (기초자산가: {atm['atm_spot']})")
        print(f"  ATM 콜 OI: {atm['atm_call_oi']:,}")
        print(f"  ATM 풋 OI: {atm['atm_put_oi']:,}")
        print(f"  ATM PCR:   {atm['atm_pcr_oi']:.4f}")
        print()
        print(f"  ── GEX ──")
        print(f"  Call GEX:  {gex['call_gex']:,.0f}")
        print(f"  Put GEX:   {gex['put_gex']:,.0f}")
        print(f"  Total GEX: {gex['total_gex']:,.0f}  ({gex['total_gex_bn']:.2f}B)")
        print(f"  기초자산가: {gex['spot_used']:.2f}")
        print(f"  승수: {gex['multiplier']:,}")

        # ── PCR / GEX 해석 ──────────────────────────────────────
        print(f"\n  ── 해석 ──")
        if pcr_oi > 1.0:
            print(f"  PCR > 1.0: 풋 OI 우위 → 하락 베팅 우세 (약세 시그널)")
        elif pcr_oi < 0.7:
            print(f"  PCR < 0.7: 콜 OI 우위 → 상승 베팅 우세 (강세 시그널)")
        else:
            print(f"  PCR 중립 구간 (0.7~1.0)")

        if gex["total_gex"] > 0:
            print(f"  GEX > 0: 시장 감마 롱 → 딜러 헤징이 변동성 억제 방향")
        else:
            print(f"  GEX < 0: 시장 감마 숏 → 딜러 헤징이 변동성 증폭 방향")
        print(f"{'='*60}")

        # ── JSON 저장 ────────────────────────────────────────────
        if args.output_json:
            output = {
                "result": result,
                "snapshots": snapshots,
            }
            try:
                import os
                os.makedirs(os.path.dirname(args.output_json) or ".", exist_ok=True)
                with open(args.output_json, "w", encoding="utf-8") as f:
                    json.dump(output, f, ensure_ascii=False, indent=2, default=str)
                print(f"\n[INFO] 결과 저장 완료: {args.output_json}")
            except Exception as exc:
                print(f"\n[ERROR] 저장 실패: {exc}")

        return 0

    finally:
        mst_obj   = None
        chain_obj = None
        cp_cybos   = None
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
