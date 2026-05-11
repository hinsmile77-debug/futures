from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Dict, List, Tuple


DEFAULT_DATA_FIELDS = "0,1,2,3,4,5,6,7,8,9"
DEFAULT_HEADER_LIMIT = 40
DEFAULT_ROW_LIMIT = 12


PRESETS: Dict[str, Dict[str, Any]] = {
    "futures_balance_ref": {
        "description": "Known-good futures balance reference payload.",
        "progid": "CpTrade.CpTd0723",
        "inputs": ["0={account}", "1=50", "2=1", "3=", "4=20"],
        "header_limit": 20,
        "data_fields": "0,1,2,3,4,5,6,7,8,9,10",
        "row_limit": 5,
    },
    "daily_pnl_ref": {
        "description": "Known-good daily pnl/account summary reference payload.",
        "progid": "CpTrade.CpTd6197",
        "inputs": ["0={account}", "1={today}", "2=50", "3=10"],
        "header_limit": 24,
        "data_fields": DEFAULT_DATA_FIELDS,
        "row_limit": 5,
    },
    "candidate_account_today": {
        "description": "Generic account+today query pattern.",
        "progid": "CpTrade.CpTd0000",
        "inputs": ["0={account}", "1={today}"],
        "header_limit": DEFAULT_HEADER_LIMIT,
        "data_fields": DEFAULT_DATA_FIELDS,
        "row_limit": DEFAULT_ROW_LIMIT,
    },
    "candidate_account_goods_today": {
        "description": "Generic account+goods+today query pattern for futures/options.",
        "progid": "CpTrade.CpTd0000",
        "inputs": ["0={account}", "1=50", "2={today}"],
        "header_limit": DEFAULT_HEADER_LIMIT,
        "data_fields": DEFAULT_DATA_FIELDS,
        "row_limit": DEFAULT_ROW_LIMIT,
    },
    "candidate_account_code_today": {
        "description": "Generic account+nearest_code+today query pattern.",
        "progid": "CpTrade.CpTd0000",
        "inputs": ["0={account}", "1={nearest_code}", "2={today}"],
        "header_limit": DEFAULT_HEADER_LIMIT,
        "data_fields": DEFAULT_DATA_FIELDS,
        "row_limit": DEFAULT_ROW_LIMIT,
    },
}


CANDIDATE_GROUPS: List[Dict[str, str]] = [
    {
        "priority": "P0",
        "name": "CpTrade account+today family",
        "pattern": "CpTrade.CpTd****",
        "target": "Futures investor flow / program investor flow TR candidates",
        "inputs": "{account}, {today}",
        "note": "Best first pass for same-day account-scoped investor/program payloads.",
    },
    {
        "priority": "P0",
        "name": "CpTrade account+goods+today family",
        "pattern": "CpTrade.CpTd****",
        "target": "Futures goods(50) investor/program TR candidates",
        "inputs": "{account}, 50, {today}",
        "note": "Good when the object requires explicit futures goods code.",
    },
    {
        "priority": "P1",
        "name": "CpTrade account+code+today family",
        "pattern": "CpTrade.CpTd****",
        "target": "Nearest-month instrument-scoped investor TR candidates",
        "inputs": "{account}, {nearest_code}, {today}",
        "note": "Useful if the object is bound to the active futures contract code.",
    },
    {
        "priority": "P1",
        "name": "Program realtime reference",
        "pattern": "code=P00101 / type=program trading",
        "target": "Realtime program-trading FID interpretation",
        "inputs": "realtime probe",
        "note": "Prior logs exposed FID 202/204/210/212/928/929 as program-flow candidates.",
    },
    {
        "priority": "P2",
        "name": "Investor ticker realtime",
        "pattern": "type=investor ticker",
        "target": "Realtime investor-flow support check",
        "inputs": "realtime probe",
        "note": "Mock looked unsupported; keep for later real-server verification.",
    },
    {
        "priority": "P2",
        "name": "CpSysDib / Dscbo1 side channels",
        "pattern": "CpSysDib.* / Dscbo1.*",
        "target": "Auxiliary market-data or program-data channels",
        "inputs": "{nearest_code} or no input",
        "note": "Fallback family if investor/program data lives outside CpTrade.",
    },
]


HYPOTHESES: List[Dict[str, str]] = [
    {
        "id": "ref_0723_balance",
        "priority": "R",
        "category": "reference",
        "progid": "CpTrade.CpTd0723",
        "preset": "futures_balance_ref",
        "rationale": "Validated futures balance reference used to confirm probe wiring and field dumping.",
    },
    {
        "id": "ref_6197_daily_pnl",
        "priority": "R",
        "category": "reference",
        "progid": "CpTrade.CpTd6197",
        "preset": "daily_pnl_ref",
        "rationale": "Validated account summary reference used to compare a known good CpTrade payload.",
    },
    {
        "id": "hyp_0724_futures_investor",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpTrade.CpTd0724",
        "preset": "candidate_account_goods_today",
        "rationale": "Nearest numeric neighbor above validated futures balance; plausible same family inquiry object.",
    },
    {
        "id": "hyp_0725_futures_investor",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpTrade.CpTd0725",
        "preset": "candidate_account_goods_today",
        "rationale": "Continues the validated 0723 futures block; worth checking for investor-grid style rows.",
    },
    {
        "id": "hyp_0726_futures_investor",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpTrade.CpTd0726",
        "preset": "candidate_account_goods_today",
        "rationale": "Same futures-centric numeric neighborhood as 0723 balance.",
    },
    {
        "id": "hyp_0727_futures_investor",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpTrade.CpTd0727",
        "preset": "candidate_account_goods_today",
        "rationale": "Another adjacent futures family candidate; probe for row counts around investor groups.",
    },
    {
        "id": "hyp_0728_futures_investor",
        "priority": "P0",
        "category": "futures_investor",
        "progid": "CpTrade.CpTd0728",
        "preset": "candidate_account_goods_today",
        "rationale": "Same hypothesis block; useful to test for account+goods+today acceptance.",
    },
    {
        "id": "hyp_6198_program_investor",
        "priority": "P1",
        "category": "program_investor",
        "progid": "CpTrade.CpTd6198",
        "preset": "candidate_account_today",
        "rationale": "Nearest numeric neighbor above validated 6197 account-summary block; plausible program/account derivative.",
    },
    {
        "id": "hyp_6199_program_investor",
        "priority": "P1",
        "category": "program_investor",
        "progid": "CpTrade.CpTd6199",
        "preset": "candidate_account_goods_today",
        "rationale": "Same 6197 neighborhood with explicit futures goods code for program-flow possibility.",
    },
    {
        "id": "hyp_6200_program_investor",
        "priority": "P1",
        "category": "program_investor",
        "progid": "CpTrade.CpTd6200",
        "preset": "candidate_account_goods_today",
        "rationale": "Continuation of the 6197 account-summary block; probe for signed KRW-style program data.",
    },
]


def safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = safe_str(value).replace(",", "")
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        text = safe_str(value).replace(",", "")
        if not text:
            return default
        return float(text)
    except Exception:
        return default


def resolve_nearest_code(future_code) -> Tuple[str, str]:
    future_count = safe_int(future_code.GetCount())
    nearest_code = ""
    nearest_name = ""
    for idx in range(future_count):
        code = safe_str(future_code.GetData(0, idx))
        name = safe_str(future_code.GetData(1, idx))
        if code.startswith("A") and "F" in name:
            nearest_code = code
            nearest_name = name
            break
    if not nearest_code and future_count > 0:
        nearest_code = safe_str(future_code.GetData(0, 0))
        nearest_name = safe_str(future_code.GetData(1, 0))
    return nearest_code, nearest_name


def parse_input_pairs(values: List[str]) -> List[Tuple[int, str]]:
    pairs: List[Tuple[int, str]] = []
    for raw in values:
        if "=" not in raw:
            raise ValueError("input must be in idx=value form: {0}".format(raw))
        idx_text, value = raw.split("=", 1)
        pairs.append((int(idx_text), value))
    return pairs


def normalize_value(value: str, account_no: str, nearest_code: str, today_yyMMdd: str) -> Any:
    mapping = {
        "{account}": account_no,
        "{nearest_code}": nearest_code,
        "{today}": today_yyMMdd,
    }
    rendered = mapping.get(value, value)
    if rendered.isdigit():
        try:
            return int(rendered)
        except Exception:
            return rendered
    return rendered


def dump_headers(obj, header_limit: int) -> Dict[int, str]:
    headers: Dict[int, str] = {}
    for idx in range(header_limit):
        try:
            headers[idx] = safe_str(obj.GetHeaderValue(idx))
        except Exception:
            headers[idx] = "<ERR>"
    return headers


def dump_rows(obj, data_fields: List[int], row_limit: int) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for row_idx in range(row_limit):
        row: Dict[str, str] = {}
        any_value = False
        for field_idx in data_fields:
            try:
                value = safe_str(obj.GetDataValue(field_idx, row_idx))
            except Exception:
                value = "<ERR>"
            row[str(field_idx)] = value
            if value not in ("", "<ERR>"):
                any_value = True
        if not any_value and row_idx > 0:
            break
        rows.append(row)
    return rows


def evaluate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    headers = payload.get("headers", {})
    rows = payload.get("rows", [])

    header_nonempty = sum(1 for value in headers.values() if value not in ("", "<ERR>"))
    row_nonempty_cells = 0
    nonzero_numeric_cells = 0
    signed_cells = 0

    for row in rows:
        for value in row.values():
            if value in ("", "<ERR>"):
                continue
            row_nonempty_cells += 1
            normalized = value.replace(",", "")
            try:
                num = float(normalized)
            except Exception:
                continue
            if num != 0:
                nonzero_numeric_cells += 1
            if normalized.startswith("+") or normalized.startswith("-"):
                signed_cells += 1

    row_count = len(rows)
    score = (
        row_count * 5
        + row_nonempty_cells
        + nonzero_numeric_cells * 2
        + signed_cells * 3
        + header_nonempty
    )

    if 3 <= row_count <= 12:
        score += 10
    if signed_cells >= 3:
        score += 10

    if row_count >= 3 and signed_cells >= 3:
        verdict = "likely_investor_grid"
    elif nonzero_numeric_cells >= 3:
        verdict = "possibly_useful"
    elif header_nonempty > 0 or row_nonempty_cells > 0:
        verdict = "weak_signal"
    else:
        verdict = "empty"

    return {
        "header_nonempty": header_nonempty,
        "row_count": row_count,
        "row_nonempty_cells": row_nonempty_cells,
        "nonzero_numeric_cells": nonzero_numeric_cells,
        "signed_cells": signed_cells,
        "score": score,
        "verdict": verdict,
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description="Probe raw Cybos investor/program TR candidate objects and dump headers/data."
    )
    parser.add_argument("--account-no", required=True, help="Signed-on Cybos account number")
    parser.add_argument("--preset", default="", help="Preset name from --list-presets")
    parser.add_argument("--hypothesis", default="", help="Hypothesis id from --list-hypotheses")
    parser.add_argument("--list-presets", action="store_true", help="Print presets and exit")
    parser.add_argument("--list-candidates", action="store_true", help="Print candidate groups and exit")
    parser.add_argument("--list-hypotheses", action="store_true", help="Print 10 first-pass hypotheses and exit")
    parser.add_argument("--progid", default="", help="Exact COM ProgID to probe")
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        help="SetInputValue pair in idx=value form. Tokens: {account}, {nearest_code}, {today}",
    )
    parser.add_argument("--header-limit", type=int, default=DEFAULT_HEADER_LIMIT, help="Header dump width")
    parser.add_argument("--data-fields", default=DEFAULT_DATA_FIELDS, help="Comma-separated GetDataValue fields")
    parser.add_argument("--row-limit", type=int, default=DEFAULT_ROW_LIMIT, help="Maximum rows to dump")
    parser.add_argument("--sleep-ms", type=int, default=0, help="Optional sleep before BlockRequest")
    return parser


def print_presets() -> None:
    print("[PRESETS]")
    for name, spec in PRESETS.items():
        print(
            "- {0}: progid={1} inputs={2} | {3}".format(
                name,
                spec.get("progid", ""),
                spec.get("inputs", []),
                spec.get("description", ""),
            )
        )


def print_candidates() -> None:
    print("[CANDIDATE_GROUPS]")
    for item in CANDIDATE_GROUPS:
        print(
            "- {priority} | {name} | pattern={pattern} | target={target} | inputs={inputs} | note={note}".format(
                **item
            )
        )


def print_hypotheses() -> None:
    print("[HYPOTHESES]")
    for item in HYPOTHESES:
        print(
            "- {id} | {priority} | {category} | progid={progid} | preset={preset} | {rationale}".format(
                **item
            )
        )


def resolve_preset_and_hypothesis(args) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    preset = {}
    hypothesis = {}

    if args.preset:
        preset = PRESETS.get(args.preset, {})
        if not preset:
            raise ValueError("Unknown preset: {0}".format(args.preset))

    if args.hypothesis:
        matches = [item for item in HYPOTHESES if item["id"] == args.hypothesis]
        if not matches:
            raise ValueError("Unknown hypothesis: {0}".format(args.hypothesis))
        hypothesis = matches[0]
        if not preset:
            preset = PRESETS.get(hypothesis.get("preset", ""), {})

    return preset, hypothesis


def run_probe(
    *,
    account_no: str,
    progid: str,
    input_specs: List[str],
    header_limit: int,
    data_fields_text: str,
    row_limit: int,
    sleep_ms: int = 0,
    hypothesis: str = "",
    preset: str = "",
) -> Dict[str, Any]:
    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        raise RuntimeError("pywin32 import error: {0}".format(exc))

    pythoncom.CoInitialize()

    cp = win32com.client.Dispatch("CpUtil.CpCybos")
    if cp.IsConnect != 1:
        raise RuntimeError("Cybos Plus API is not connected.")

    trade = win32com.client.Dispatch("CpTrade.CpTdUtil")
    trade_init = trade.TradeInit(0)
    if trade_init not in (0, None):
        raise RuntimeError("TradeInit failed with ret={0}".format(trade_init))

    accounts = list(trade.AccountNumber)
    if account_no not in accounts:
        raise RuntimeError("Account not available in this session: {0}".format(account_no))

    future_code = win32com.client.Dispatch("CpUtil.CpFutureCode")
    nearest_code, nearest_name = resolve_nearest_code(future_code)
    today_yyMMdd = time.strftime("%y%m%d")

    input_pairs = parse_input_pairs(input_specs)
    data_fields = [int(x.strip()) for x in data_fields_text.split(",") if x.strip()]
    obj = win32com.client.Dispatch(progid)

    normalized_inputs: List[Tuple[int, Any]] = []
    for idx, raw_value in input_pairs:
        value = normalize_value(raw_value, account_no, nearest_code, today_yyMMdd)
        normalized_inputs.append((idx, value))
        obj.SetInputValue(idx, value)

    if sleep_ms > 0:
        time.sleep(max(0, sleep_ms) / 1000.0)

    ret = obj.BlockRequest()
    status = safe_int(getattr(obj, "GetDibStatus", lambda: 0)())
    msg = safe_str(getattr(obj, "GetDibMsg1", lambda: "")())
    headers = dump_headers(obj, header_limit)
    rows = dump_rows(obj, data_fields, row_limit)

    payload = {
        "preset": preset,
        "hypothesis": hypothesis,
        "progid": progid,
        "inputs": normalized_inputs,
        "ret": ret,
        "dib_status": status,
        "dib_msg1": msg,
        "nearest_code": nearest_code,
        "nearest_name": nearest_name,
        "headers": headers,
        "rows": rows,
    }
    payload["analysis"] = evaluate_payload(payload)
    return payload


def main():
    args = build_parser().parse_args()

    if args.list_presets:
        print_presets()
        return 0
    if args.list_candidates:
        print_candidates()
        return 0
    if args.list_hypotheses:
        print_hypotheses()
        return 0

    try:
        preset, hypothesis = resolve_preset_and_hypothesis(args)
    except ValueError as exc:
        print("[FAIL]", exc)
        return 2

    effective_progid = args.progid or hypothesis.get("progid", "") or preset.get("progid", "")
    if not effective_progid:
        print("[FAIL] --progid is required when preset/hypothesis does not define one.")
        return 3

    effective_inputs = list(preset.get("inputs", [])) + list(args.input)
    effective_header_limit = (
        args.header_limit if args.header_limit != DEFAULT_HEADER_LIMIT else int(preset.get("header_limit", DEFAULT_HEADER_LIMIT))
    )
    effective_data_fields = (
        args.data_fields if args.data_fields != DEFAULT_DATA_FIELDS else str(preset.get("data_fields", DEFAULT_DATA_FIELDS))
    )
    effective_row_limit = (
        args.row_limit if args.row_limit != DEFAULT_ROW_LIMIT else int(preset.get("row_limit", DEFAULT_ROW_LIMIT))
    )

    try:
        payload = run_probe(
            account_no=args.account_no,
            progid=effective_progid,
            input_specs=effective_inputs,
            header_limit=effective_header_limit,
            data_fields_text=effective_data_fields,
            row_limit=effective_row_limit,
            sleep_ms=args.sleep_ms,
            hypothesis=hypothesis.get("id", ""),
            preset=args.preset or hypothesis.get("preset", ""),
        )
    except Exception as exc:
        print("[FAIL]", exc)
        return 4

    print("[RESULT] hypothesis =", payload.get("hypothesis", ""))
    print("[RESULT] progid =", payload["progid"])
    print("[RESULT] ret =", payload["ret"])
    print("[RESULT] DibStatus =", payload["dib_status"])
    print("[RESULT] DibMsg1 =", payload["dib_msg1"])
    print("[RESULT] analysis =", payload["analysis"])
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
