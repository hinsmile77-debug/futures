"""
Cybos Plus 투자자 수급 / 프로그램 매매 TR 일괄 탐색 스크립트
장 중 Cybos Plus 연결 상태에서 실행.

사용법:
    python scripts/run_cybos_investor_discovery.py --account-no <계좌번호>
    python scripts/run_cybos_investor_discovery.py --account-no <계좌번호> --category futures_investor
    python scripts/run_cybos_investor_discovery.py --account-no <계좌번호> --dry-run

출력:
    scripts/discovery_results_YYYYMMDD_HHMMSS.json  (전체 raw 결과)
    콘솔: verdict별 요약 + likely_investor_grid / possibly_useful 상세
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
import datetime
import os
from typing import Any, Dict, List, Optional

# Windows cp949 터미널에서 한글 깨짐 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "mbcs"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() in ("cp949", "mbcs"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 32-bit 체크 — CpSysDib.* / Dscbo1.* 은 32-bit COM 전용
import struct as _struct
_IS_32BIT = _struct.calcsize("P") == 4
if not _IS_32BIT:
    print(
        "[경고] 현재 Python이 64-bit입니다.\n"
        "       CpSysDib.* / Dscbo1.* COM 객체는 32-bit 전용이므로 CLASSNOTREG 오류가 발생합니다.\n"
        "       아래 명령으로 py37_32 환경에서 재실행하세요:\n\n"
        "  C:\\Users\\82108\\anaconda3\\envs\\py37_32\\python.exe -X utf8 "
        + " ".join(sys.argv)
        + "\n"
    )

# check_cybos_investor_candidates.py 의 공통 유틸 재사용
sys.path.insert(0, os.path.dirname(__file__))
from check_cybos_investor_candidates import (
    run_probe,
    evaluate_payload,
    resolve_nearest_code,
    safe_str,
    safe_int,
    HYPOTHESES,
)

# ──────────────────────────────────────────────────────────────
# 추가 후보 — CpSysDib / Dscbo1 계열 (기존 HYPOTHESES에 없는 것)
# ──────────────────────────────────────────────────────────────
EXTRA_CANDIDATES: List[Dict[str, Any]] = [
    # ── 선물 투자자 수급 후보 ──────────────────────────
    # ────────────────────────────────────────────────────────
    # 레지스트리 실측 기반 후보 (추측 제거 후 실제 등록 ProgID만)
    # ────────────────────────────────────────────────────────

    # ── 선물/옵션 투자자 수급 — CpSysDib.CpSvr72xx 계열 ──
    {
        "id": "reg_7210T_noinput",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvr7210T",
        "inputs": [],
        "rationale": "레지스트리 확인. 7210=투자자별 선물/옵션 매매통계, T=당일(no input)",
    },
    {
        "id": "reg_7210T_code",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvr7210T",
        "inputs": [("0", "{nearest_code}")],
        "rationale": "7210T: 선물코드 입력 패턴 시도",
    },
    {
        "id": "reg_7210d_noinput",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvr7210d",
        "inputs": [],
        "rationale": "레지스트리 확인. 7210d=투자자별 선물/옵션 매매통계 일별(d=daily)",
    },
    {
        "id": "reg_7210d_code",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvr7210d",
        "inputs": [("0", "{nearest_code}")],
        "rationale": "7210d: 선물코드 입력 패턴 시도",
    },
    {
        "id": "reg_New7212_noinput",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvrNew7212",
        "inputs": [],
        "rationale": "레지스트리 확인. New7212: 선물/옵션 투자자 관련 신규 TR",
    },
    {
        "id": "reg_New7215A_noinput",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvrNew7215A",
        "inputs": [],
        "rationale": "레지스트리 확인. New7215A: 선물/옵션 투자자 A타입",
    },
    {
        "id": "reg_New7215B_noinput",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvrNew7215B",
        "inputs": [],
        "rationale": "레지스트리 확인. New7215B: 선물/옵션 투자자 B타입",
    },
    {
        "id": "reg_New7216_noinput",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvrNew7216",
        "inputs": [],
        "rationale": "레지스트리 확인. New7216: 선물/옵션 투자자 관련",
    },
    {
        "id": "reg_New7221_noinput",
        "priority": "P1",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvrNew7221",
        "inputs": [],
        "rationale": "레지스트리 확인. New7221: 선물/옵션 투자자 또는 프로그램",
    },
    {
        "id": "reg_New7221S_noinput",
        "priority": "P1",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvrNew7221S",
        "inputs": [],
        "rationale": "레지스트리 확인. New7221S",
    },
    {
        "id": "reg_New7222_noinput",
        "priority": "P1",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvrNew7222",
        "inputs": [],
        "rationale": "레지스트리 확인. New7222",
    },
    {
        "id": "reg_New7224_noinput",
        "priority": "P1",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvrNew7224",
        "inputs": [],
        "rationale": "레지스트리 확인. New7224",
    },
    {
        "id": "reg_New7244S_noinput",
        "priority": "P1",
        "category": "futures_investor",
        "progid": "CpSysDib.CpSvrNew7244S",
        "inputs": [],
        "rationale": "레지스트리 확인. New7244S",
    },
    {
        "id": "reg_DsCbo1_7244_noinput",
        "priority": "P1",
        "category": "futures_investor",
        "progid": "DsCbo1.CpSvr7244",
        "inputs": [],
        "rationale": "레지스트리 확인. DsCbo1.7244: 선물/옵션 투자자 관련",
    },
    {
        "id": "reg_DsCbo1_7246_noinput",
        "priority": "P1",
        "category": "futures_investor",
        "progid": "DsCbo1.CpSvr7246",
        "inputs": [],
        "rationale": "레지스트리 확인. DsCbo1.7246",
    },
    # ── 선물/옵션 통계 (투자자 포함 가능성) ───────────────
    {
        "id": "reg_FutureOptionStat_code",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "Dscbo1.FutureOptionStat",
        "inputs": [("0", "{nearest_code}")],
        "rationale": "레지스트리 확인. 선물/옵션 통계 — 투자자별 행 포함 가능",
    },
    {
        "id": "reg_FutureOptionStat_noinput",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "Dscbo1.FutureOptionStat",
        "inputs": [],
        "rationale": "FutureOptionStat: 입력 없는 패턴",
    },
    {
        "id": "reg_FutureOptionStatPB_code",
        "priority": "P1",
        "category": "futures_investor",
        "progid": "Dscbo1.FutureOptionStatPB",
        "inputs": [("0", "{nearest_code}")],
        "rationale": "레지스트리 확인. FutureOptionStatPB (PB=기간별?)",
    },
    # ── 주식 투자자 참조 (필드 구조 기준) ─────────────────
    {
        "id": "reg_InvestorsbyStock_ref",
        "priority": "R",
        "category": "reference",
        "progid": "CpSysDib.InvestorsbyStock",
        "inputs": [("0", "005930")],
        "rationale": "레지스트리 확인. 주식 투자자별 매매 — 헤더/행 구조 기준선으로 사용",
    },
    {
        "id": "reg_Dscbo1_8412_ref",
        "priority": "R",
        "category": "reference",
        "progid": "Dscbo1.CpSvr8412",
        "inputs": [],
        "rationale": "레지스트리 확인. 8412=투자자별 매매동향 (주식 시장 전체), 구조 기준",
    },
    # ── 프로그램 매매 — CpSvr8119 계열 ───────────────────
    {
        "id": "reg_8119_noinput",
        "priority": "P0",
        "category": "program_investor",
        "progid": "Dscbo1.CpSvr8119",
        "inputs": [],
        "rationale": "레지스트리 확인. 8119=프로그램 매매 동향 (Cybos 대표 TR)",
    },
    {
        "id": "reg_New8119_noinput",
        "priority": "P0",
        "category": "program_investor",
        "progid": "Dscbo1.CpSvrNew8119",
        "inputs": [],
        "rationale": "레지스트리 확인. 신규 8119 프로그램 매매 TR",
    },
    {
        "id": "reg_New8119Chart_noinput",
        "priority": "P1",
        "category": "program_investor",
        "progid": "Dscbo1.CpSvrNew8119Chart",
        "inputs": [],
        "rationale": "레지스트리 확인. 8119 차트 버전",
    },
    {
        "id": "reg_DsCbo1_New8119Day_noinput",
        "priority": "P0",
        "category": "program_investor",
        "progid": "DsCbo1.CpSvrNew8119Day",
        "inputs": [],
        "rationale": "레지스트리 확인. 8119 일별 버전 (DsCbo1 네임스페이스)",
    },
    # ── 프로그램 매매 — CpSvr72xx 계열 ───────────────────
    {
        "id": "reg_7236_noinput",
        "priority": "P1",
        "category": "program_investor",
        "progid": "CpSysDib.CpSvr7236",
        "inputs": [],
        "rationale": "레지스트리 확인. 7236: 프로그램/투자자 관련 가능성",
    },
    {
        "id": "reg_7238_noinput",
        "priority": "P1",
        "category": "program_investor",
        "progid": "CpSysDib.CpSvr7238",
        "inputs": [],
        "rationale": "레지스트리 확인. 7238",
    },
    {
        "id": "reg_7240_noinput",
        "priority": "P1",
        "category": "program_investor",
        "progid": "CpSysDib.CpSvr7240",
        "inputs": [],
        "rationale": "레지스트리 확인. 7240",
    },
    {
        "id": "reg_New8300_noinput",
        "priority": "P1",
        "category": "program_investor",
        "progid": "CpSysDib.CpSvrNew8300",
        "inputs": [],
        "rationale": "레지스트리 확인. New8300: 프로그램 또는 시장 통계",
    },
    {
        "id": "reg_Dscbo1_8300_noinput",
        "priority": "P1",
        "category": "program_investor",
        "progid": "Dscbo1.CpSvr8300",
        "inputs": [],
        "rationale": "레지스트리 확인. 8300 (Dscbo1)",
    },
    # ── CpTrade 실제 등록 번호 중 미탐색 후보 ─────────────
    {
        "id": "reg_td0732",
        "priority": "P1",
        "category": "futures_investor",
        "progid": "CpTrade.CpTd0732",
        "inputs": [("0", "{account}"), ("1", "50"), ("2", "{today}")],
        "rationale": "레지스트리 확인. 0732: 0723 인접 선물 계열",
    },
    {
        "id": "reg_td0721F",
        "priority": "P1",
        "category": "futures_investor",
        "progid": "CpTrade.CpTd0721F",
        "inputs": [("0", "{account}"), ("1", "50"), ("2", "{today}")],
        "rationale": "레지스트리 확인. 0721F: F=선물(Futures) 한정 TR 가능성",
    },
    {
        "id": "reg_td6722",
        "priority": "P1",
        "category": "program_investor",
        "progid": "CpTrade.CpTd6722",
        "inputs": [("0", "{account}"), ("1", "{today}")],
        "rationale": "레지스트리 확인. 6722: 6197 인접 계열, 프로그램 매매 후보",
    },
    {
        "id": "reg_td6033",
        "priority": "P1",
        "category": "program_investor",
        "progid": "CpTrade.CpTd6033",
        "inputs": [("0", "{account}"), ("1", "{today}")],
        "rationale": "레지스트리 확인. 6033: 투자자/프로그램 조회 후보",
    },
]

VERDICT_ORDER = ["likely_investor_grid", "possibly_useful", "weak_signal", "empty"]
VERDICT_COLOR = {
    "likely_investor_grid": "★★★",
    "possibly_useful":      "★★ ",
    "weak_signal":          "★  ",
    "empty":                "   ",
}


def build_input_specs(
    raw_inputs: List[tuple],
    account_no: str,
    nearest_code: str,
    today_yyMMdd: str,
) -> List[str]:
    """extra candidates 의 ("idx_str", "{token}") 형식을 run_probe 용 "idx=value" 리스트로 변환."""
    mapping = {
        "{account}": account_no,
        "{nearest_code}": nearest_code,
        "{today}": today_yyMMdd,
    }
    result = []
    for idx_str, val in raw_inputs:
        rendered = mapping.get(val, val)
        result.append(f"{idx_str}={rendered}")
    return result


def run_all(
    account_no: str,
    category_filter: Optional[str],
    sleep_between_ms: int,
    dry_run: bool,
) -> List[Dict[str, Any]]:
    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        print(f"[FAIL] pywin32 import 실패: {exc}")
        sys.exit(1)

    if not dry_run:
        pythoncom.CoInitialize()
        cp = win32com.client.Dispatch("CpUtil.CpCybos")
        if cp.IsConnect != 1:
            print("[FAIL] Cybos Plus API 미연결 — HTS 로그인 후 재실행")
            sys.exit(1)

        trade = win32com.client.Dispatch("CpTrade.CpTdUtil")
        trade.TradeInit(0)

        future_code_obj = win32com.client.Dispatch("CpUtil.CpFutureCode")
        nearest_code, nearest_name = resolve_nearest_code(future_code_obj)
    else:
        nearest_code = "A301M6"
        nearest_name = "KOSPI200F (dry-run)"

    today_yyMMdd = time.strftime("%y%m%d")

    print(f"\n{'='*64}")
    print(f"  Cybos Plus 투자자 TR 탐색  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"  계좌: {account_no}  최근월 선물: {nearest_code} ({nearest_name})")
    print(f"  today={today_yyMMdd}  dry_run={dry_run}")
    print(f"{'='*64}\n")

    # 모든 후보 조합 (기존 HYPOTHESES + EXTRA_CANDIDATES)
    all_candidates = []

    for hyp in HYPOTHESES:
        if category_filter and hyp["category"] != category_filter:
            continue
        all_candidates.append({
            "id": hyp["id"],
            "priority": hyp["priority"],
            "category": hyp["category"],
            "progid": hyp["progid"],
            "source": "hypothesis",
            "preset": hyp.get("preset", ""),
            "rationale": hyp["rationale"],
        })

    for ex in EXTRA_CANDIDATES:
        if category_filter and ex["category"] != category_filter:
            continue
        all_candidates.append({
            "id": ex["id"],
            "priority": ex["priority"],
            "category": ex["category"],
            "progid": ex["progid"],
            "source": "extra",
            "inputs_raw": ex["inputs"],
            "rationale": ex["rationale"],
        })

    results = []
    total = len(all_candidates)

    for i, cand in enumerate(all_candidates, 1):
        progid = cand["progid"]
        cid    = cand["id"]
        cat    = cand["category"]
        pri    = cand["priority"]
        src    = cand["source"]

        print(f"[{i:02d}/{total}] {pri} {cat:20s} {progid}")

        if dry_run:
            result = {
                "id": cid,
                "progid": progid,
                "category": cat,
                "priority": pri,
                "source": src,
                "dry_run": True,
                "analysis": {"verdict": "skipped"},
            }
            results.append(result)
            continue

        # input specs 준비
        if src == "hypothesis":
            from check_cybos_investor_candidates import (
                PRESETS, resolve_preset_and_hypothesis,
            )
            preset_name = cand.get("preset", "")
            preset = PRESETS.get(preset_name, {})
            input_specs = list(preset.get("inputs", []))
            # 토큰 치환
            input_specs = [
                s.replace("{account}", account_no)
                 .replace("{nearest_code}", nearest_code)
                 .replace("{today}", today_yyMMdd)
                for s in input_specs
            ]
            header_limit = int(preset.get("header_limit", 40))
            data_fields  = str(preset.get("data_fields", "0,1,2,3,4,5,6,7,8,9"))
            row_limit    = int(preset.get("row_limit", 12))
        else:
            raw_inputs = cand.get("inputs_raw", [])
            input_specs = build_input_specs(
                raw_inputs, account_no, nearest_code, today_yyMMdd
            )
            header_limit = 40
            data_fields  = "0,1,2,3,4,5,6,7,8,9"
            row_limit    = 12

        try:
            payload = run_probe(
                account_no=account_no,
                progid=progid,
                input_specs=input_specs,
                header_limit=header_limit,
                data_fields_text=data_fields,
                row_limit=row_limit,
                sleep_ms=0,
                hypothesis=cid,
                preset=cand.get("preset", ""),
            )
            verdict = payload["analysis"]["verdict"]
            score   = payload["analysis"]["score"]
            rows    = payload["analysis"]["row_count"]
            signed  = payload["analysis"]["signed_cells"]
            star    = VERDICT_COLOR.get(verdict, "   ")
            print(f"         {star} verdict={verdict}  score={score}  rows={rows}  signed={signed}")
            result = {
                "id": cid,
                "progid": progid,
                "category": cat,
                "priority": pri,
                "source": src,
                "rationale": cand["rationale"],
                **payload,
            }
        except Exception as exc:
            print(f"         [ERR] {exc}")
            result = {
                "id": cid,
                "progid": progid,
                "category": cat,
                "priority": pri,
                "source": src,
                "error": str(exc),
                "analysis": {"verdict": "error"},
            }

        results.append(result)

        if sleep_between_ms > 0:
            time.sleep(sleep_between_ms / 1000.0)

    return results


def print_summary(results: List[Dict[str, Any]]) -> None:
    print(f"\n{'='*64}")
    print("  탐색 결과 요약")
    print(f"{'='*64}")

    by_verdict: Dict[str, List[Dict]] = {v: [] for v in VERDICT_ORDER}
    by_verdict["error"] = []
    by_verdict["skipped"] = []

    for r in results:
        v = r.get("analysis", {}).get("verdict", "error")
        by_verdict.setdefault(v, []).append(r)

    hits = by_verdict["likely_investor_grid"] + by_verdict["possibly_useful"]
    if hits:
        print("\n[유망 후보]")
        for r in hits:
            v    = r["analysis"]["verdict"]
            star = VERDICT_COLOR.get(v, "   ")
            score = r["analysis"].get("score", 0)
            rows  = r["analysis"].get("row_count", 0)
            signed = r["analysis"].get("signed_cells", 0)
            print(
                f"  {star} [{r['category']:20s}] {r['progid']:40s} "
                f"score={score:3d}  rows={rows}  signed={signed}"
            )
            print(f"       → {r['rationale']}")
    else:
        print("\n[유망 후보 없음] - 모든 TR이 empty 또는 error")

    print(f"\n[카테고리별 집계]")
    cats: Dict[str, Dict[str, int]] = {}
    for r in results:
        cat = r.get("category", "?")
        v   = r.get("analysis", {}).get("verdict", "error")
        cats.setdefault(cat, {})
        cats[cat][v] = cats[cat].get(v, 0) + 1
    for cat, vcnt in sorted(cats.items()):
        summary = "  ".join(f"{v}×{n}" for v, n in vcnt.items())
        print(f"  {cat:22s}: {summary}")

    print()


def save_results(results: List[Dict[str, Any]], output_dir: str) -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = os.path.join(output_dir, f"discovery_results_{ts}.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return fname


def enumerate_cybos_registry() -> None:
    """
    Windows 레지스트리에서 등록된 Cybos Plus COM ProgID를 열거한다.
    32-bit Python에서 실행하면 WOW6432Node (32-bit COM) 까지 모두 조회된다.
    """
    try:
        import winreg
    except ImportError:
        print("[SKIP] winreg 없음 (Windows 전용)")
        return

    prefixes = ("CpTrade.", "CpUtil.", "CpSysDib.", "Dscbo1.", "DsCbo1.", "CpFuture.")
    found: List[str] = []

    # HKLM\SOFTWARE\Classes (현재 Python 아키텍처 기준)
    hives = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes"),
    ]
    # 32-bit Python이면 WOW6432Node 도 포함 (실제로는 같은 뷰)
    # 64-bit Python에서 32-bit COM 보려면 KEY_WOW64_32KEY 플래그 필요
    flags_list = [0, winreg.KEY_WOW64_32KEY] if not _IS_32BIT else [0]

    for hive, path in hives:
        for flags in flags_list:
            try:
                key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ | flags)
            except OSError:
                continue
            idx = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, idx)
                    if any(subkey_name.startswith(p) for p in prefixes):
                        tag = " [32-bit view]" if flags == winreg.KEY_WOW64_32KEY else ""
                        entry = subkey_name + tag
                        if entry not in found:
                            found.append(entry)
                    idx += 1
                except OSError:
                    break
            winreg.CloseKey(key)

    if found:
        print(f"\n[레지스트리 등록 Cybos ProgID — {len(found)}개]")
        for f in sorted(found):
            print(f"  {f}")
    else:
        print("\n[레지스트리 등록 없음] Cybos Plus COM 미설치 또는 32-bit 뷰 접근 실패")
    print()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Cybos Plus 투자자/프로그램 TR 일괄 탐색"
    )
    p.add_argument("--account-no", required=True, help="Cybos 계좌번호")
    p.add_argument(
        "--category",
        default="",
        choices=["futures_investor", "program_investor", "reference", ""],
        help="특정 카테고리만 실행 (기본: 전체)",
    )
    p.add_argument(
        "--sleep-ms",
        type=int,
        default=500,
        help="TR 간 대기 ms (기본 500, Cybos TR 쓰로틀 방지용)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Cybos 미연결 상태에서 후보 목록만 출력",
    )
    p.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "logs"),
        help="결과 JSON 저장 폴더 (기본: logs/)",
    )
    p.add_argument(
        "--list-registry",
        action="store_true",
        help="레지스트리에서 등록된 Cybos COM ProgID 열거 후 탐색 계속",
    )
    return p


def main() -> int:
    args = build_parser().parse_args()

    print(f"[Python] {sys.version}  {'32-bit' if _IS_32BIT else '64-bit'}")
    if not _IS_32BIT:
        print("  * CpSysDib.* / Dscbo1.* 결과는 신뢰 불가 — py37_32 에서 재실행 필요\n")

    if args.list_registry:
        enumerate_cybos_registry()

    results = run_all(
        account_no=args.account_no,
        category_filter=args.category or None,
        sleep_between_ms=args.sleep_ms,
        dry_run=args.dry_run,
    )
    print_summary(results)
    if not args.dry_run:
        out = save_results(results, args.output_dir)
        print(f"[저장] {out}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
