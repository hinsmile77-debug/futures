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
    # ── [MW0601 451차 후속2] HTS 화면 8221(프로그램매매 투자자별 종합) 원천 탐색 ──
    #
    # 배경: 운영 중인 `Dscbo1.CpSvr8111`은 차익/비차익 × 위탁/자기 축만 제공하고
    # 투자자별(개인·기관·외인) 필드가 **없다**. 그걸 모른 채 소비 계층이 스키마를
    # 폴백으로 채워 `program_individual/institution_net_krw`가 상수 0으로 2개월
    # 방치됐다(451차). 사용자가 Creon HTS **화면 8221**에 그 교차 데이터가 실제로
    # 조회됨을 확인해줬다(2026-08-09) — 즉 데이터는 존재한다. 문제는 경로다.
    #
    # 문서 조사 결과 — **공식 Plus API에는 프로그램 × 투자자 교차 객체가 없다**:
    #   · 프로그램 계열(8111 / PgAtime8112 / 8116 / 8119)은 전부 차익·비차익 축만.
    #   · 투자자 계열(7212 / 7221 / 7222 / 7224)은 전부 투자자 축만, 프로그램 구분 없음.
    #   · `CpSvr7225`만 둘을 **나란히** 두지만(프로그램차익·비차익 컬럼 + 외국인·기관
    #     컬럼) 교차는 아니다.
    #
    # 그러나 이 PC 레지스트리에는 **공식 문서에 없는 등록 객체**가 있다(--list-registered
    # 로 재현 가능). HTS 화면 8221이 데이터를 받는 이상 그 뒤에 COM 객체가 존재하며,
    # 미문서 객체 중 하나일 수 있다. 아래는 그 후보다 — 전부 **레지스트리 등록 확인**을
    # 거쳤고(존재하지 않는 ProgID를 찍어보는 게 아니다), 번호가 8221에 가깝거나
    # 투자자·프로그램 계열 이름을 가진 것만 골랐다.
    #
    # ⚠ `scripts/check_cybos_investor_candidates.py`의 CpTd6198~6200은 CpTrade(주문)
    #   네임스페이스의 번호 인접 추측이다 — 후보로 쓰지 말 것.
    #
    # ⚠ 판정 기준은 "응답이 온다"가 아니라 **① 투자자 × 차익/비차익 교차 격자인가
    #   ② 장중에 값이 갱신되는가** 둘 다이다. 거래소가 이 분해를 일별 마감 통계로만
    #   낸다면 응답이 와도 1분봉 피처로는 못 쓴다. 화면 8221을 장중에 두 번(예: 10시,
    #   14시) 조회해 값이 변하는지 **먼저** 눈으로 확인하는 게 가장 싸다.
    ("CpSysDib.CpSvr8241", []),             # 8221에 가장 가까운 8xxx 미문서 객체
    ("CpSysDib.CpSvr8241", [(0, ord("1"))]),
    ("CpSysDib.CpSvr2221", []),             # 뒷 3자리 221 일치, 미문서
    ("CpSysDib.CpSvr8113", []),             # 프로그램 8111~8119 사이 미문서
    ("CpSysDib.CpSvr8113", [(0, ord("1"))]),
    ("Dscbo1.PgAtime8112", [(0, ord("1"))]),  # 화면 8221 '시간대별' 탭 원천(문서: 차익/비차익만)
    ("CpSysDib.CpSvr7210d", []),            # 투자자별 종합(잠정) — 미문서
    ("CpSysDib.CpSvr7210T", []),            # 〃 시간대별 — 미문서
    ("CpSysDib.CpSvr7236", []),             # 72xx 투자자 계열 미문서
    ("CpSysDib.CpSvr7238", []),
    ("CpSysDib.CpSvr7240", []),
    ("Dscbo1.CpSvr7225", [(0, 0)]),         # 시장매매흐름분석(문서화됨). 입력0=최종시간(0=현재)
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


# 레지스트리에 등록된 Cybos COM 오브젝트 접두사
_PROGID_PREFIXES = ("Dscbo1.", "DsCbo1.", "CpSysDib.", "CpSysdib.", "CpUtil.", "CpTrade.")


def list_registered_progids() -> List[str]:
    """이 PC에 **실제로 등록된** Cybos ProgID 목록.

    [MW0601 451차 후속2] 왜 필요한가: 후보 ProgID를 번호 인접으로 추측하면
    존재하지도 않는 이름을 장중에 찍어보게 된다(`check_cybos_investor_candidates.py`의
    CpTd6198~6200이 그랬다). 레지스트리는 **장 연결 없이, 장외에도** 읽을 수 있어
    "존재하는가"를 먼저 공짜로 거를 수 있다.

    실제로 이 조회가 화면 8221 문제를 닫는 데 결정적이었다 — `CpSvr8221`이라는
    ProgID는 등록돼 있지 않고, 프로그램 계열은 8111/8111S/8111KS/8112/8113/8114/
    8116/8119/8119S/8119Day뿐임이 여기서 확인됐다.

    ⚠ **등록됨 ≠ 사용 가능**이다. 공식 문서(cybosplus.github.io)에 없는 객체는 HTS
    내부용일 수 있고, `BlockRequest` 미지원이거나 권한이 없을 수 있다. 등록 여부는
    후보를 **좁히는** 용도이지 사용 가능 판정이 아니다.
    """
    try:
        import winreg
    except ImportError:
        return []
    found = set()
    roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Classes"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes"),
    ]
    for hive, path in roots:
        try:
            key = winreg.OpenKey(hive, path)
        except OSError:
            continue
        try:
            idx = 0
            while True:
                try:
                    name = winreg.EnumKey(key, idx)
                except OSError:
                    break
                idx += 1
                if name.startswith(_PROGID_PREFIXES) and not name.endswith((".1", ".1.1")):
                    found.add(name)
        finally:
            winreg.CloseKey(key)
    return sorted(found)


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
    # [451차] 기본 폭 확대 — 8111은 idx55까지 쓰고(구 기본 40은 잘렸다), 투자자별 격자는
    # 행이 투자자 10종·열이 매도/매수/순매수 3축으로 벌어질 수 있어 10×10으로는 못 본다.
    parser.add_argument("--header-limit", type=int, default=64, help="Max query headers to sample")
    parser.add_argument("--row-limit", type=int, default=20, help="Max query rows to sample")
    parser.add_argument("--field-limit", type=int, default=20, help="Max query fields per row")
    parser.add_argument("--ensure-login", action="store_true", help="Try autologin if CYBOS is disconnected")
    parser.add_argument("--list-registered", action="store_true",
                        help="레지스트리에 등록된 Cybos ProgID만 덤프하고 종료 "
                             "(COM 연결·장중 불필요. --filter로 정규식 필터)")
    parser.add_argument("--filter", default="", help="--list-registered 결과 정규식 필터")
    args = parser.parse_args()

    # 등록 목록 조회는 COM 연결도, 32-bit도 필요 없다 — 런타임 체크보다 먼저 처리한다.
    if args.list_registered:
        import re as _re
        names = list_registered_progids()
        if args.filter:
            pat = _re.compile(args.filter, _re.IGNORECASE)
            names = [n for n in names if pat.search(n)]
        print(json.dumps({"count": len(names), "progids": names},
                         ensure_ascii=False, indent=2))
        return 0

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
