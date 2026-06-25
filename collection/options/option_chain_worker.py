"""
OptionChainWorker — 옵션 체인 BlockRequest를 QThread에서 실행.

Cybos Plus 메시지 라우팅 특성:
  BlockRequest 응답이 메인 스레드의 Windows 메시지 큐를 경유한다.
  메인 스레드(Qt 이벤트 루프)가 블록되지 않아야 응답이 전달된다.
  QThread 분리 후 Qt 이벤트 루프가 정상 동작하므로 응답 수신 보장.
  (api_connector.py _run_block_request 주석 참조 — done.wait() 금지 이유)

COM STA 규칙:
  Dscbo1.OptionMst 객체를 워커 스레드 내부에서 생성·사용.
  메인 스레드의 COM 객체와 공유하지 않는다.
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import time
from typing import Any, Dict, List, Tuple

from PyQt5.QtCore import QThread, pyqtSignal

logger = logging.getLogger("OPTIONS")
system_logger = logging.getLogger("SYSTEM")

_HV_OI    = 99   # OptionMst GetHeaderValue 인덱스 — 미결제약정
_HV_GAMMA = 110  # Gamma (백분율, ÷100)

_OPTION_MULTIPLIER = 250_000
_GEX_BN = 1e9


# ── 타입 헬퍼 ──────────────────────────────────────────────────────

def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _f(v: Any, d: float = 0.0) -> float:
    try:
        t = _s(v).replace(",", "")
        return float(t) if t else d
    except Exception:
        return d


def _i(v: Any, d: int = 0) -> int:
    try:
        t = _s(v).replace(",", "")
        return int(float(t)) if t else d
    except Exception:
        return d


def _is_call(row: Dict) -> bool:
    cp = _s(row.get("call_put", ""))
    return "콜" in cp or cp.upper().startswith("C")


def _is_put(row: Dict) -> bool:
    cp = _s(row.get("call_put", ""))
    return "풋" in cp or cp.upper().startswith("P")


# ── 순수 Python 헬퍼 (COM 없음, 모듈 레벨 함수) ──────────────────────

def _filter_front_month(chain: List[Dict]) -> List[Dict]:
    today = _dt.date.today()
    yms = sorted(set(r["ym"] for r in chain if r.get("ym")))
    for ym in yms:
        try:
            year  = 2000 + int(ym[:2])
            month = int(ym[2:])
            expiry = _option_expiry(year, month)
            if today <= expiry:
                return [r for r in chain if r.get("ym") == ym]
        except Exception:
            pass
    return [r for r in chain if r.get("ym") == yms[0]] if yms else chain


def _option_expiry(year: int, month: int) -> _dt.date:
    """KOSPI200 옵션 만기일 = 해당 월 2번째 목요일."""
    d = _dt.date(year, month, 1)
    days_to_thu = (3 - d.weekday()) % 7
    first_thu = d + _dt.timedelta(days=days_to_thu)
    return first_thu + _dt.timedelta(weeks=1)


def _filter_atm(chain: List[Dict], spot: float, window: float) -> List[Dict]:
    lo, hi = spot - window, spot + window
    return [r for r in chain if lo <= r.get("strike", 0) <= hi]


def _compute(snapshots: List[Dict], spot: float) -> Dict[str, float]:
    pcr_oi = _compute_pcr(snapshots)
    atm_c_oi, atm_p_oi, atm_pcr = _compute_atm_oi(snapshots, spot)
    gex_bn, gex_sign = _compute_gex(snapshots, spot)
    return {
        "opt_chain_pcr":       round(pcr_oi, 4),
        "opt_atm_pcr":         round(atm_pcr, 4),
        "opt_atm_call_oi":     float(atm_c_oi),
        "opt_atm_put_oi":      float(atm_p_oi),
        "opt_gex_bn":          round(gex_bn, 4),
        "opt_gex_sign":        float(gex_sign),
        "opt_chain_available": 1.0,
    }


def _compute_pcr(snapshots: List[Dict]) -> float:
    call_oi = sum(s.get("oi", 0) for s in snapshots if _is_call(s) and not s.get("error"))
    put_oi  = sum(s.get("oi", 0) for s in snapshots if _is_put(s)  and not s.get("error"))
    return put_oi / call_oi if call_oi > 0 else 1.0


def _compute_atm_oi(snapshots: List[Dict], spot: float) -> Tuple[int, int, float]:
    calls = [s for s in snapshots if _is_call(s) and not s.get("error")]
    puts  = [s for s in snapshots if _is_put(s)  and not s.get("error")]
    atm_c = min(calls, key=lambda s: abs(s["strike"] - spot)) if calls else None
    atm_p = min(puts,  key=lambda s: abs(s["strike"] - spot)) if puts else None
    c_oi  = atm_c.get("oi", 0) if atm_c else 0
    p_oi  = atm_p.get("oi", 0) if atm_p else 0
    pcr   = p_oi / c_oi if c_oi > 0 else 1.0
    return c_oi, p_oi, pcr


def _compute_gex(snapshots: List[Dict], spot: float) -> Tuple[float, float]:
    call_gex = put_gex = 0.0
    for s in snapshots:
        if s.get("error") or s.get("oi", 0) <= 0:
            continue
        unit = s.get("gamma", 0.0) * s["oi"] * _OPTION_MULTIPLIER * spot
        if _is_call(s):
            call_gex += unit
        elif _is_put(s):
            put_gex += unit
    total = call_gex - put_gex
    gex_bn = total / _GEX_BN
    sign = 1.0 if total > 0 else (-1.0 if total < 0 else 0.0)
    return gex_bn, sign


# ── OptionChainWorker ───────────────────────────────────────────────

class OptionChainWorker(QThread):
    """
    ATM 옵션 BlockRequest 루프를 메인 스레드에서 분리.

    result_ready(feats, chain_raw):
      feats     — 계산된 피처 dict. 실패 시 빈 dict.
      chain_raw — 수집·갱신된 체인 목록. stale 재로드 없으면 입력 그대로.
                  빈 list → 다음 워커 기동 시 CpOptionCode 재수집 지시.
    """

    result_ready = pyqtSignal(object, object)   # (dict, list) — PyQt_PyObject 사용

    def __init__(
        self,
        chain_raw: List[Dict],
        spot: float,
        cache_path: str,
        atm_window_pt: float = 30.0,
        pause_ms: int = 50,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._chain_raw   = list(chain_raw)   # 복사본 — 메인 스레드와 공유 없음
        self._spot        = spot
        self._cache_path  = cache_path
        self._atm_window  = atm_window_pt
        self._pause_ms    = pause_ms

    # ── QThread 진입점 ─────────────────────────────────────────────

    def run(self) -> None:
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception as exc:
            system_logger.warning("[OptionChain][Worker] CoInitialize 실패: %s", exc)
            self.result_ready.emit({}, self._chain_raw)
            return

        feats: Dict[str, float] = {}
        chain_raw: List[Dict] = self._chain_raw
        try:
            feats, chain_raw = self._execute()
        except Exception as exc:
            system_logger.warning(
                "[OptionChain][Worker] 예외: %s", exc, exc_info=True,
            )
        finally:
            try:
                import pythoncom as _pc
                _pc.CoUninitialize()
            except Exception:
                pass

        self.result_ready.emit(feats, chain_raw)

    # ── 핵심 실행 (워커 스레드) ────────────────────────────────────

    def _execute(self) -> Tuple[Dict[str, float], List[Dict]]:
        t0 = time.perf_counter()

        chain_raw = self._chain_raw

        if not chain_raw:
            chain_raw = self._fetch_chain()
            if not chain_raw:
                return {}, []

        front  = _filter_front_month(chain_raw)
        target = _filter_atm(front, self._spot, self._atm_window)

        if not target:
            system_logger.warning(
                "[OptionChain][Worker] ATM 대상 없음 spot=%.1f window=%.0f — stale, 재로드",
                self._spot, self._atm_window,
            )
            chain_raw = self._fetch_chain()
            if not chain_raw:
                return {}, []
            front  = _filter_front_month(chain_raw)
            target = _filter_atm(front, self._spot, self._atm_window)
            if not target:
                system_logger.warning(
                    "[OptionChain][Worker] 재로드 후에도 ATM 대상 없음 spot=%.1f — 수집 불가",
                    self._spot,
                )
                return {}, chain_raw

        from win32com.client import Dispatch
        mst_obj = Dispatch("Dscbo1.OptionMst")
        snapshots = self._collect_snapshots(mst_obj, target)

        valid = [s for s in snapshots if not s.get("error")]
        if not valid:
            errors = [s.get("error", "?") for s in snapshots[:3]]
            system_logger.warning(
                "[OptionChain][Worker] 스냅샷 전체 실패 target=%d errors=%s — 코드 만료 가능성",
                len(target), errors,
            )
            # 빈 list 반환 → Snapshot이 _chain_raw를 갱신하지 않음
            # → 다음 워커에서 CpOptionCode 재수집
            return {}, []

        feats = _compute(snapshots, self._spot)
        elapsed = (time.perf_counter() - t0) * 1000
        system_logger.info(
            "[OptionChain][Worker] 완료 %.0fms | target=%d valid=%d "
            "PCR=%.3f ATM_PCR=%.3f GEX=%.2fB",
            elapsed, len(target), len(valid),
            feats.get("opt_chain_pcr", 0),
            feats.get("opt_atm_pcr", 0),
            feats.get("opt_gex_bn", 0),
        )
        return feats, chain_raw

    def _collect_snapshots(self, mst_obj: Any, target: List[Dict]) -> List[Dict]:
        """OptionMst BlockRequest 루프 — 워커 스레드 전용."""
        out: List[Dict] = []
        for row in target:
            code = row["code"]
            snap: Dict[str, Any] = {
                "code":     code,
                "call_put": row.get("call_put", ""),
                "strike":   row.get("strike", 0.0),
            }
            try:
                mst_obj.SetInputValue(0, code)
                mst_obj.BlockRequest()
                if _i(mst_obj.GetDibStatus()) != 0:
                    snap["error"] = f"dib_status={_i(mst_obj.GetDibStatus())}"
                else:
                    snap["oi"]    = _i(mst_obj.GetHeaderValue(_HV_OI))
                    snap["gamma"] = _f(mst_obj.GetHeaderValue(_HV_GAMMA))
            except Exception as exc:
                snap["error"] = str(exc)
            out.append(snap)
            if self._pause_ms > 0:
                time.sleep(self._pause_ms / 1000.0)
        return out

    def _fetch_chain(self) -> List[Dict]:
        """CpOptionCode로 옵션 코드 목록 수집 후 캐시 저장."""
        try:
            from win32com.client import Dispatch
            chain_obj = Dispatch("CpUtil.CpOptionCode")
            count = chain_obj.GetCount()
            chain: List[Dict] = []
            for idx in range(count):
                try:
                    chain.append({
                        "code":     _s(chain_obj.GetData(0, idx)),
                        "call_put": _s(chain_obj.GetData(2, idx)).upper(),
                        "ym":       _s(chain_obj.GetData(3, idx)),
                        "strike":   _f(chain_obj.GetData(4, idx)),
                    })
                except Exception:
                    pass
            logger.info("[OptionChain][Worker] CpOptionCode 수집 완료: %d 종목", len(chain))
            self._save_chain_cache(chain)
            return chain
        except Exception as exc:
            logger.warning("[OptionChain][Worker] 체인 수집 실패: %s", exc)
            return []

    def _save_chain_cache(self, chain: List[Dict]) -> None:
        try:
            dir_ = os.path.dirname(self._cache_path)
            if dir_:
                os.makedirs(dir_, exist_ok=True)
            with open(self._cache_path, "w", encoding="utf-8") as f:
                json.dump({"chain": chain}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
