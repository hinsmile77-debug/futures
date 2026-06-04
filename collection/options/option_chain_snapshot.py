"""
OptionChainSnapshot — 옵션 체인 스냅샷 정기 수집

N분마다 OptionMst BlockRequest 폴링으로 ATM ±window_pt 종목들의
PCR(OI) / ATM OI / GEX 를 계산하고 feature_builder.build(option_data=...) 형식으로 반환.

collect_option_metrics.py 의 핵심 로직을 매분 파이프라인에서 사용 가능한 클래스로 래핑.

사용:
    snap = OptionChainSnapshot()
    snap.initialize()                   # connect_broker() 완료 후 1회

    # STEP 4 (매분 파이프라인):
    snap.refresh(spot=close_price)      # 5분마다 실제 폴링, 간격 미도달 시 즉시 반환
    chain_feats = snap.get_features()   # 최신 피처 (미갱신 시 이전 값)
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("OPTIONS")
system_logger = logging.getLogger("SYSTEM")

# ── OptionMst GetHeaderValue 인덱스 (2026-05-13 검증) ─────────────
_HV_OI    = 99   # 현재 미결제약정 ✅
_HV_DELTA = 109  # Delta (백분율, ÷100) ✅
_HV_GAMMA = 110  # Gamma (백분율, ÷100) ✅

_OPTION_MULTIPLIER = 250_000   # KOSPI200 옵션 승수
_GEX_BN = 1e9                  # GEX 단위 변환: 십억 원


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


class OptionChainSnapshot:
    """
    매N분마다 OptionMst 폴링으로 PCR(OI) / ATM OI / GEX 를 수집.

    반환 피처 키 (feature_builder.build 의 option_data 에 병합):
      opt_chain_pcr       — 체인 전체 PCR (풋/콜 OI 비율)
      opt_atm_pcr         — ATM 행사가 기준 PCR
      opt_atm_call_oi     — ATM 콜 미결제약정
      opt_atm_put_oi      — ATM 풋 미결제약정
      opt_gex_bn          — 총 GEX (십억 원, 양수=딜러 감마롱)
      opt_gex_sign        — GEX 부호 (+1.0 / -1.0 / 0.0)
      opt_chain_available — 1.0 if 실데이터 수집 완료
    """

    def __init__(
        self,
        chain_cache_path: str = "data/option_chain.json",
        refresh_interval_min: int = 5,
        atm_window_pt: float = 30.0,
        pause_ms: int = 50,
    ) -> None:
        self._cache_path = chain_cache_path
        self._interval_sec = refresh_interval_min * 60
        self._atm_window = atm_window_pt
        self._pause_ms = pause_ms

        self._mst_obj = None
        self._chain_raw: List[Dict] = []
        self._last_refresh: float = 0.0
        self._last_features: Dict[str, float] = self._empty()
        self._ready = False

    # ── 기동 시 1회 ────────────────────────────────────────────────

    def initialize(self) -> None:
        """COM 객체 생성 + 체인 캐시 로드. connect_broker() 완료 후 호출."""
        try:
            from win32com.client import Dispatch
            self._mst_obj = Dispatch("Dscbo1.OptionMst")
            self._ready = True
        except Exception as exc:
            system_logger.warning("[OptionChain] COM 초기화 실패 (Dscbo1.OptionMst): %s", exc)
            return

        self._chain_raw = self._load_chain_cache()
        if self._chain_raw:
            system_logger.info("[OptionChain] 초기화 완료: 체인 캐시 %d 종목", len(self._chain_raw))
        else:
            system_logger.info("[OptionChain] 초기화 완료: 체인 캐시 없음 — 첫 refresh 시 CpOptionCode 수집 예정")

    # ── 매분 파이프라인 STEP 4 ─────────────────────────────────────

    def refresh(self, spot: float) -> bool:
        """
        N분 간격으로 ATM 체인 폴링.

        Args:
            spot: KOSPI200 선물 현재가 (ATM 기준점)

        Returns:
            True = 실제 폴링 수행 / False = 간격 미도달 또는 조건 불충족 → 스킵
        """
        if not self._ready or self._mst_obj is None:
            return False
        if spot <= 0:
            return False
        if time.time() - self._last_refresh < self._interval_sec:
            return False

        t0 = time.time()
        try:
            feats = self._poll(spot)
            self._last_features = feats
            self._last_refresh = time.time()
            avail = bool(feats.get("opt_chain_available"))
            system_logger.info(
                "[OptionChain] 갱신 %.1fs | PCR=%.3f ATM_PCR=%.3f GEX=%.2fB avail=%s",
                time.time() - t0,
                feats.get("opt_chain_pcr", 0),
                feats.get("opt_atm_pcr", 0),
                feats.get("opt_gex_bn", 0),
                avail,
            )
            if not avail:
                system_logger.warning(
                    "[OptionChain] 데이터 수집 실패 — 체인 수집 또는 ATM 필터링 문제"
                )
            return True
        except Exception as exc:
            system_logger.warning("[OptionChain] refresh 실패: %s", exc)
            return False

    def get_features(self) -> Dict[str, float]:
        return dict(self._last_features)

    def reset_daily(self) -> None:
        self._last_refresh = 0.0
        self._last_features = self._empty()
        logger.info("[OptionChain] 일일 리셋")

    # ── 내부 ───────────────────────────────────────────────────────

    def _poll(self, spot: float) -> Dict[str, float]:
        if not self._chain_raw:
            self._chain_raw = self._fetch_and_cache_chain()
            if not self._chain_raw:
                return self._empty()

        front = self._filter_front_month(self._chain_raw)
        target = self._filter_atm(front, spot, self._atm_window)
        if not target:
            # 캐시가 현재 spot 범위를 벗어남 (stale) → 강제 재로드
            system_logger.warning(
                "[OptionChain] ATM 대상 없음 spot=%.1f window=%.0f — 체인 캐시 stale, 재로드",
                spot, self._atm_window,
            )
            self._chain_raw = self._fetch_and_cache_chain()
            if not self._chain_raw:
                return self._empty()
            front = self._filter_front_month(self._chain_raw)
            target = self._filter_atm(front, spot, self._atm_window)
            if not target:
                system_logger.warning(
                    "[OptionChain] 재로드 후에도 ATM 대상 없음 spot=%.1f — 옵션 체인 수집 불가",
                    spot,
                )
                return self._empty()

        snapshots = self._collect_snapshots(target)
        valid = [s for s in snapshots if not s.get("error")]
        if not valid:
            errors = [s.get("error", "?") for s in snapshots[:3]]
            system_logger.warning(
                "[OptionChain] 스냅샷 전체 실패 target=%d errors=%s — 코드 만료 가능성",
                len(target), errors,
            )
            # 체인 코드 만료 가능성 → 다음 refresh 시 강제 재로드
            self._chain_raw = []
            return self._empty()

        pcr_oi = self._compute_pcr(snapshots)
        atm_c_oi, atm_p_oi, atm_pcr = self._compute_atm_oi(snapshots, spot)
        gex_bn, gex_sign = self._compute_gex(snapshots, spot)

        return {
            "opt_chain_pcr":       round(pcr_oi, 4),
            "opt_atm_pcr":         round(atm_pcr, 4),
            "opt_atm_call_oi":     float(atm_c_oi),
            "opt_atm_put_oi":      float(atm_p_oi),
            "opt_gex_bn":          round(gex_bn, 4),
            "opt_gex_sign":        float(gex_sign),
            "opt_chain_available": 1.0,
        }

    def _fetch_and_cache_chain(self) -> List[Dict]:
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
            logger.info("[OptionChain] CpOptionCode 수집 완료: %d 종목", len(chain))
            self._save_chain_cache(chain)
            return chain
        except Exception as exc:
            logger.warning("[OptionChain] 체인 수집 실패: %s", exc)
            return []

    def _load_chain_cache(self) -> List[Dict]:
        try:
            with open(self._cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("chain", [])
        except Exception:
            return []

    def _save_chain_cache(self, chain: List[Dict]) -> None:
        try:
            os.makedirs(os.path.dirname(self._cache_path) or ".", exist_ok=True)
            with open(self._cache_path, "w", encoding="utf-8") as f:
                json.dump({"chain": chain}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _filter_front_month(self, chain: List[Dict]) -> List[Dict]:
        import datetime as _dt
        today = _dt.date.today()
        yms = sorted(set(r["ym"] for r in chain if r.get("ym")))
        # KOSPI200 options expire on 2nd Thursday of each month — skip expired months
        for ym in yms:
            try:
                year = 2000 + int(ym[:2])
                month = int(ym[2:])
                expiry = self._option_expiry(year, month)
                if today <= expiry:
                    logger.debug("[OptionChain] front month=%s (만기=%s)", ym, expiry)
                    return [r for r in chain if r.get("ym") == ym]
            except Exception:
                pass
        # fallback
        return [r for r in chain if r.get("ym") == yms[0]] if yms else chain

    @staticmethod
    def _option_expiry(year: int, month: int):
        """KOSPI200 옵션 만기일 = 해당 월의 2번째 목요일."""
        import datetime as _dt
        d = _dt.date(year, month, 1)
        days_to_thu = (3 - d.weekday()) % 7   # 목요일(weekday=3)까지 남은 일수
        first_thu = d + _dt.timedelta(days=days_to_thu)
        return first_thu + _dt.timedelta(weeks=1)

    def _filter_atm(self, chain: List[Dict], spot: float, window: float) -> List[Dict]:
        lo, hi = spot - window, spot + window
        return [r for r in chain if lo <= r.get("strike", 0) <= hi]

    def _collect_snapshots(self, target: List[Dict]) -> List[Dict]:
        out: List[Dict] = []
        obj = self._mst_obj
        for row in target:
            code = row["code"]
            snap: Dict[str, Any] = {
                "code":     code,
                "call_put": row.get("call_put", ""),
                "strike":   row.get("strike", 0.0),
            }
            try:
                obj.SetInputValue(0, code)
                obj.BlockRequest()
                if _i(obj.GetDibStatus()) != 0:
                    snap["error"] = f"dib_status={_i(obj.GetDibStatus())}"
                else:
                    snap["oi"]    = _i(obj.GetHeaderValue(_HV_OI))
                    snap["gamma"] = _f(obj.GetHeaderValue(_HV_GAMMA))
            except Exception as exc:
                snap["error"] = str(exc)
            out.append(snap)
            if self._pause_ms > 0:
                time.sleep(self._pause_ms / 1000.0)
        return out

    def _compute_pcr(self, snapshots: List[Dict]) -> float:
        call_oi = sum(s.get("oi", 0) for s in snapshots if _is_call(s) and not s.get("error"))
        put_oi  = sum(s.get("oi", 0) for s in snapshots if _is_put(s)  and not s.get("error"))
        return put_oi / call_oi if call_oi > 0 else 1.0

    def _compute_atm_oi(self, snapshots: List[Dict], spot: float) -> Tuple[int, int, float]:
        calls = [s for s in snapshots if _is_call(s) and not s.get("error")]
        puts  = [s for s in snapshots if _is_put(s)  and not s.get("error")]
        atm_c = min(calls, key=lambda s: abs(s["strike"] - spot)) if calls else None
        atm_p = min(puts,  key=lambda s: abs(s["strike"] - spot)) if puts else None
        c_oi  = atm_c.get("oi", 0) if atm_c else 0
        p_oi  = atm_p.get("oi", 0) if atm_p else 0
        pcr   = p_oi / c_oi if c_oi > 0 else 1.0
        return c_oi, p_oi, pcr

    def _compute_gex(self, snapshots: List[Dict], spot: float) -> Tuple[float, float]:
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

    @staticmethod
    def _empty() -> Dict[str, float]:
        return {
            "opt_chain_pcr":       0.0,
            "opt_atm_pcr":         0.0,
            "opt_atm_call_oi":     0.0,
            "opt_atm_put_oi":      0.0,
            "opt_gex_bn":          0.0,
            "opt_gex_sign":        0.0,
            "opt_chain_available": 0.0,
        }
