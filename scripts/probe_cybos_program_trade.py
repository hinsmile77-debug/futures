from __future__ import annotations

import argparse
import gc
import json
import platform
import struct
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from ensure_cybos_login import ensure_cybos_login


QUERY_TARGETS: List[Tuple[str, List[Tuple[int, Any]]]] = [
    ("Dscbo1.CpSvr8111", []),
    ("Dscbo1.CpSvr8111S", []),
    ("Dscbo1.CpSvr8111KS", []),
    ("Dscbo1.CpSvr8119", []),
    ("Dscbo1.CpSvrNew8119", []),
]

REALTIME_TARGETS: List[str] = [
    "CpSysDib.CpSvr8119S",
]


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    try:
        return str(value).strip()
    except Exception:
        return ""


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        text = _safe_str(value).replace(",", "")
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def _contains_unsupported_function(text: str) -> bool:
    lowered = text.lower()
    return (
        "지원하지 않는 함수" in text
        or "지웒하지" in text
        or "does not support" in lowered
        or "-2147418113" in text
    )


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("CYBOS COM requires 32-bit Python")


def _header_dump(obj: Any, limit: int) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for idx in range(limit):
        try:
            value = obj.GetHeaderValue(idx)
        except Exception:
            break
        text = _safe_str(value)
        if text:
            out[str(idx)] = text
    return out


def _data_dump(obj: Any, row_limit: int, field_limit: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for row_idx in range(row_limit):
        row: Dict[str, Any] = {}
        saw_any = False
        for field_idx in range(field_limit):
            try:
                value = obj.GetDataValue(field_idx, row_idx)
            except Exception:
                break
            text = _safe_str(value)
            if text:
                row[str(field_idx)] = text
                saw_any = True
        if not saw_any:
            break
        rows.append(row)
    return rows


def _probe_query_object(dispatch: Any, progid: str, inputs: List[Tuple[int, Any]], header_limit: int, row_limit: int, field_limit: int) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "progid": progid,
        "kind": "query",
        "inputs": [{"index": idx, "value": value} for idx, value in inputs],
    }
    try:
        obj = dispatch(progid)
    except Exception as exc:
        result["dispatch_error"] = str(exc)
        return result

    for idx, value in inputs:
        try:
            obj.SetInputValue(idx, value)
        except Exception as exc:
            result.setdefault("set_input_errors", []).append(
                {"index": idx, "value": value, "error": str(exc)}
            )

    try:
        ret = obj.BlockRequest()
        result["block_request_ret"] = ret
    except Exception as exc:
        result["block_request_error"] = str(exc)
        return result

    try:
        result["dib_status"] = obj.GetDibStatus()
    except Exception as exc:
        result["dib_status_error"] = str(exc)
    try:
        result["dib_msg1"] = _safe_str(obj.GetDibMsg1())
    except Exception as exc:
        result["dib_msg1_error"] = str(exc)

    result["headers"] = _header_dump(obj, header_limit)
    result["rows"] = _data_dump(obj, row_limit, field_limit)

    headers = result["headers"]
    result["summary"] = {
        "header_count": len(headers),
        "row_count": len(result["rows"]),
        "nonzero_header_count": sum(1 for value in headers.values() if value not in ("0", "0.0")),
        "arb_guess": _safe_int(headers.get("2", "0")),
        "nonarb_guess": _safe_int(headers.get("5", "0")),
    }
    return result


class _RealtimeEvent:
    def __init__(self) -> None:
        self.events: List[Dict[str, Any]] = []

    def Received(self) -> None:
        event: Dict[str, Any] = {"ts": time.time()}
        try:
            event["headers"] = {
                str(idx): _safe_str(self.obj.GetHeaderValue(idx))
                for idx in range(13)
            }
        except Exception as exc:
            event["header_error"] = str(exc)
        self.events.append(event)


def _probe_realtime_object(dispatch: Any, with_events: Any, pythoncom: Any, progid: str, code: str, wait_seconds: float) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "progid": progid,
        "kind": "realtime",
        "code": code,
        "wait_seconds": wait_seconds,
    }
    try:
        obj = dispatch(progid)
    except Exception as exc:
        result["dispatch_error"] = str(exc)
        return result

    try:
        obj.SetInputValue(0, code)
        result["set_input"] = "ok"
    except Exception as exc:
        result["set_input_error"] = str(exc)
        return result

    try:
        sink = with_events(obj, _RealtimeEvent)
        result["with_events"] = "ok"
    except Exception as exc:
        result["with_events_error"] = str(exc)
        return result

    try:
        obj.Subscribe()
        result["subscribe"] = "ok"
    except Exception as exc:
        result["subscribe_error"] = str(exc)
        return result

    deadline = time.time() + max(wait_seconds, 0.0)
    try:
        while time.time() < deadline:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.05)
    finally:
        try:
            obj.Unsubscribe()
            result["unsubscribe"] = "ok"
        except Exception as exc:
            result["unsubscribe_error"] = str(exc)

    result["event_count"] = len(sink.events)
    result["events"] = sink.events[:5]
    return result


def _classify_query_result(item: Dict[str, Any]) -> Dict[str, Any]:
    if "dispatch_error" in item:
        return {"progid": item["progid"], "classification": "dispatch_failed"}
    if "block_request_error" in item:
        error_text = _safe_str(item["block_request_error"])
        classification = "blockrequest_unsupported" if _contains_unsupported_function(error_text) else "blockrequest_failed"
        return {
            "progid": item["progid"],
            "classification": classification,
            "detail": error_text,
        }

    status = _safe_int(item.get("dib_status", 0))
    summary = item.get("summary") or {}
    row_count = _safe_int(summary.get("row_count", 0))
    nonzero_headers = _safe_int(summary.get("nonzero_header_count", 0))
    rows = item.get("rows") or []
    nonzero_cells = 0
    for row in rows:
        for value in row.values():
            if _safe_str(value) not in ("", "0", "0.0"):
                nonzero_cells += 1
    if status != 0:
        return {
            "progid": item["progid"],
            "classification": "dib_status_error",
            "status": status,
            "detail": _safe_str(item.get("dib_msg1", "")),
        }
    if row_count == 0 and nonzero_headers == 0:
        return {
            "progid": item["progid"],
            "classification": "zero_payload",
            "detail": _safe_str(item.get("dib_msg1", "")),
        }
    if row_count > 0 and nonzero_headers == 0 and nonzero_cells == 0:
        return {
            "progid": item["progid"],
            "classification": "zero_payload",
            "detail": _safe_str(item.get("dib_msg1", "")),
        }
    return {
        "progid": item["progid"],
        "classification": "payload_present",
        "row_count": row_count,
        "nonzero_header_count": nonzero_headers,
        "nonzero_cell_count": nonzero_cells,
    }


def _classify_realtime_result(item: Dict[str, Any]) -> Dict[str, Any]:
    if "dispatch_error" in item:
        return {"progid": item["progid"], "classification": "dispatch_failed"}
    if "set_input_error" in item:
        return {"progid": item["progid"], "classification": "input_failed", "detail": _safe_str(item["set_input_error"])}
    if "subscribe_error" in item:
        return {"progid": item["progid"], "classification": "subscribe_failed", "detail": _safe_str(item["subscribe_error"])}
    if _safe_int(item.get("event_count", 0)) <= 0:
        return {
            "progid": item["progid"],
            "classification": "no_event_during_window",
            "detail": "Subscribed successfully but no realtime event arrived during wait window.",
        }
    return {
        "progid": item["progid"],
        "classification": "realtime_event_received",
        "event_count": _safe_int(item.get("event_count", 0)),
    }


def _build_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    query_analysis = [_classify_query_result(item) for item in payload.get("query_targets", [])]
    realtime_analysis = [_classify_realtime_result(item) for item in payload.get("realtime_targets", [])]

    recommendations: List[str] = []
    if any(item.get("classification") == "dib_status_error" and item.get("progid") == "Dscbo1.CpSvr8111" for item in query_analysis):
        recommendations.append("`Dscbo1.CpSvr8111` is reachable but returned non-zero DIB status, so treat it as a live candidate with no usable payload rather than as a missing ProgID.")
    if any(item.get("classification") == "blockrequest_unsupported" for item in query_analysis):
        recommendations.append("Objects classified as `blockrequest_unsupported` should not stay in the minute snapshot query path.")
    if any(item.get("classification") == "zero_payload" and item.get("progid") in ("Dscbo1.CpSvr8119", "Dscbo1.CpSvrNew8119") for item in query_analysis):
        recommendations.append("`8119` query objects exist but currently return all-zero payload, so log them separately from true mapping failures.")
    if any(item.get("classification") == "no_event_during_window" for item in realtime_analysis):
        recommendations.append("If `8119S` shows no event, retry with a longer wait window during an actively traded stock and compare several symbols before ruling realtime out.")

    return {
        "query": query_analysis,
        "realtime": realtime_analysis,
        "recommendations": recommendations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe CYBOS program-trading query/realtime objects.")
    parser.add_argument("--code", default="A005930", help="Stock code for 8119S realtime probe")
    parser.add_argument("--realtime-seconds", type=float, default=5.0, help="How long to wait for realtime events")
    parser.add_argument("--header-limit", type=int, default=40, help="Max query headers to sample")
    parser.add_argument("--row-limit", type=int, default=10, help="Max query rows to sample")
    parser.add_argument("--field-limit", type=int, default=10, help="Max query fields per row")
    parser.add_argument("--ensure-login", action="store_true", help="Try autologin if CYBOS is disconnected")
    args = parser.parse_args()

    _ensure_runtime()

    try:
        import pythoncom
        from win32com.client import Dispatch, WithEvents
    except Exception as exc:
        raise RuntimeError("pywin32 import failed") from exc

    pythoncom.CoInitialize()
    try:
        if args.ensure_login:
            ok = ensure_cybos_login(require_trade_init=False)
            if not ok:
                raise RuntimeError("ensure_cybos_login() failed")

        cp = Dispatch("CpUtil.CpCybos")
        connected = bool(cp.IsConnect)
        payload: Dict[str, Any] = {
            "connected": connected,
            "query_targets": [],
            "realtime_targets": [],
        }

        if not connected:
            payload["error"] = "Cybos is not connected"
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            cp = None
            gc.collect()
            return 0

        for progid, inputs in QUERY_TARGETS:
            payload["query_targets"].append(
                _probe_query_object(
                    Dispatch,
                    progid,
                    inputs,
                    header_limit=args.header_limit,
                    row_limit=args.row_limit,
                    field_limit=args.field_limit,
                )
            )

        for progid in REALTIME_TARGETS:
            payload["realtime_targets"].append(
                _probe_realtime_object(
                    Dispatch,
                    WithEvents,
                    pythoncom,
                    progid,
                    args.code,
                    args.realtime_seconds,
                )
            )

        payload["analysis"] = _build_analysis(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        cp = None
        gc.collect()
        return 0
    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    sys.exit(main())
