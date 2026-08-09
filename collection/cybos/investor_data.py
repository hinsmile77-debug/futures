from __future__ import annotations

import datetime
import logging
from typing import Any, Dict, Optional

from collection.provenance import ProvenanceTracker
from utils.logger import LAYER_DATA

logger = logging.getLogger(LAYER_DATA)

INVESTOR_KEYS = [
    "individual",
    "foreign",
    "institution",
    "financial",
    "insurance",
    "trust",
    "bank",
    "pension",
    "etc_corp",
    "nation",
]

ZONE_LABELS = {
    "foreign": "외인",
    "individual": "개인",
    "institution": "기관",
}

# 이 클래스가 실제로 피처로 내보내는 투자자 키 — 원천이 이것만 채우면 충분하다.
# (INVESTOR_KEYS 전체는 키움 시절 스키마 잔재로, 나머지 7종은 emit 대상이 아니다.)
_EMITTED_INVESTOR_KEYS = ("foreign", "individual", "institution")


def _to_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).replace(",", "").strip()
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


class CybosInvestorData:
    """
    Cybos investor-flow cache for the divergence panel.

    Notes:
    - Cybos futures/program investor TR mapping is still being discovered.
    - Until broker-native mappings land, this class should expose explicit
      partial/unavailable states instead of silently presenting fake zeros as
      if they were validated market data.

    [MW0601 451차] 위 Notes의 취지를 실제로 어기고 있던 경로를 제거했다.
    `Dscbo1.CpSvr8111`은 투자자별 분해를 제공하지 않는데도 `nets.get(key, 기존값)`
    폴백이 `program_individual/institution_net_krw`를 상수 0으로 매분 emit하면서
    `quality_investor_program_supported=1`을 함께 보고했다 — 정확히 "fake zeros as
    validated market data"였다. 이제 프로그램매매는 원천이 실제 주는 차익/비차익만
    보유하고, 원천이 채운 키는 ProvenanceTracker로 감시한다.
    """

    def __init__(self, cybos_api=None):
        self._api = cybos_api
        self._last_fetch: Optional[datetime.datetime] = None
        self._fetch_count = 0

        self._futures: Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._call: Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._put: Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._program_arb = 0
        self._program_nonarb = 0
        # 차익+비차익 합계(KRW). 투자자별 분해가 아니다 — 이름으로 그것을 못 박는다.
        self._program_total = 0
        self._open_interest = 0

        # 원천이 실제로 채운 키 감시 — 유령 필드 조기 경보(451차)
        self._futures_prov = ProvenanceTracker("CybosFuturesInvestor", warn_after=10)
        self._program_prov = ProvenanceTracker("CybosProgramInvestor", warn_after=10)

        self._futures_supported = False
        self._program_supported = False
        self._option_flow_supported = False
        self._futures_source = "unavailable"
        self._program_source = "unavailable"
        self._option_flow_source = "unavailable"
        self._futures_reason = "not fetched"
        self._program_reason = "not fetched"
        self._option_flow_reason = "Cybos option investor-flow mapping pending"

    def set_futures_code(self, code: str) -> None:
        """매매 종목코드 갱신 — Cybos는 API 내부에서 코드를 관리하므로 현재 no-op."""
        pass

    def fetch_all(self, include_program: bool = True) -> bool:
        futures_ok = self.fetch_futures_investor()
        if include_program:
            program_ok = self.fetch_program_investor()
        else:
            program_ok = False
            self._program_supported = False
            self._program_source = "runtime_disabled"
            self._program_reason = "program probe loop disabled in live timer"
        self._last_fetch = datetime.datetime.now()
        self._fetch_count += 1
        logger.info(
            "[CybosInvestor] fetch#%d futures_supported=%s program_supported=%s "
            "option_supported=%s futures_source=%s program_source=%s",
            self._fetch_count,
            self._futures_supported,
            self._program_supported,
            self._option_flow_supported,
            self._futures_source,
            self._program_source,
        )
        return futures_ok or program_ok

    def fetch_futures_investor(self) -> bool:
        if self._api is None or not hasattr(self._api, "request_investor_futures"):
            self._futures_supported = False
            self._futures_source = "api_missing"
            self._futures_reason = "Cybos investor API helper missing"
            return False

        result = self._api.request_investor_futures()
        nets = result.get("nets") or {}
        # 폴백은 "이번 조회에 값이 안 왔을 때 직전값 유지"라는 연속성 목적으로만 남긴다.
        # "한 번도 온 적 없는 키"는 그 폴백에 가려 보이지 않으므로 따로 감시한다(451차).
        self._futures_prov.observe(nets.keys())
        for key in INVESTOR_KEYS:
            self._futures[key] = _to_int(nets.get(key, self._futures.get(key, 0)))
        self._futures_prov.maybe_warn(
            logger, _EMITTED_INVESTOR_KEYS, bool(result.get("supported", False))
        )

        # call_nets / put_nets — CpSyrNew7212 제공 시 option_flow도 갱신
        call_nets = result.get("call_nets") or {}
        put_nets  = result.get("put_nets")  or {}
        if call_nets or put_nets:
            for key in INVESTOR_KEYS:
                self._call[key] = _to_int(call_nets.get(key, self._call.get(key, 0)))
                self._put[key]  = _to_int(put_nets.get(key,  self._put.get(key, 0)))
            self._option_flow_supported = True
            self._option_flow_source    = result.get("source", "unknown")
            self._option_flow_reason    = "콜/풋 순매수 제공 (CpSvrNew7212)"

        # 미결제약정: TR 미발견 시 FutureMst fallback 값 수신
        raw = result.get("raw") or {}
        oi = _to_int(raw.get("open_interest", 0))
        if oi > 0:
            self._open_interest = oi

        self._futures_supported = bool(result.get("supported", False))
        self._futures_source = str(result.get("source", "unknown"))
        self._futures_reason = str(result.get("reason", ""))
        logger.info(
            "[CybosInvestor] futures supported=%s source=%s "
            "foreign=%+d individual=%+d institution=%+d oi=%d "
            "call_foreign=%+d put_foreign=%+d option_supported=%s reason=%s",
            self._futures_supported,
            self._futures_source,
            self._futures.get("foreign", 0),
            self._futures.get("individual", 0),
            self._futures.get("institution", 0),
            self._open_interest,
            self._call.get("foreign", 0),
            self._put.get("foreign", 0),
            self._option_flow_supported,
            self._futures_reason,
        )
        return self._futures_supported

    def fetch_program_investor(self) -> bool:
        if self._api is None or not hasattr(self._api, "request_program_investor"):
            self._program_supported = False
            self._program_source = "api_missing"
            self._program_reason = "Cybos program investor API helper missing"
            return False

        result = self._api.request_program_investor()
        # CpSvr8111은 투자자별 분해를 제공하지 않는다 — `nets`는 빈 dict가 정상이며
        # 여기서 그 모양을 채우지 않는다(451차). 여기서 필요한 감시는 경보가 아니라
        # 그 반대다: 다른 TR로 교체해 투자자별 키가 실제로 오기 시작하면 INFO로 알려
        # 폐기했던 피처를 되살릴 시점을 놓치지 않게 한다.
        self._program_prov.notice_new(logger, (result.get("nets") or {}).keys())

        # 차익/비차익 순매수 (raw 에서 직접 추출)
        raw = result.get("raw") or {}
        self._program_arb    = _to_int(raw.get("arb_net",    self._program_arb))
        self._program_nonarb = _to_int(raw.get("nonarb_net", self._program_nonarb))
        self._program_total  = _to_int(
            raw.get("total_net", self._program_arb + self._program_nonarb)
        )

        self._program_supported = bool(result.get("supported", False))
        self._program_source = str(result.get("source", "unknown"))
        self._program_reason = str(result.get("reason", ""))
        program_state = self._program_status_label(self._program_source, self._program_reason)
        logger.info(
            "[CybosInvestor] program supported=%s state=%s source=%s "
            "arb=%+d nonarb=%+d total=%+d reason=%s",
            self._program_supported,
            program_state,
            self._program_source,
            self._program_arb,
            self._program_nonarb,
            self._program_total,
            self._program_reason,
        )
        return self._program_supported

    def get_features(self) -> Dict[str, float]:
        foreign_fut = self._futures.get("foreign", 0)
        retail_fut = self._futures.get("individual", 0)
        inst_fut = self._futures.get("institution", 0)
        now = datetime.datetime.now()
        age_sec = (now - self._last_fetch).total_seconds() if self._last_fetch else 9999.0
        is_stale = age_sec > 180.0
        runtime_supported = self._futures_supported or self._program_supported

        return {
            "foreign_futures_net": float(foreign_fut),
            "foreign_call_net": float(self._call.get("foreign", 0)),
            "foreign_put_net": float(self._put.get("foreign", 0)),
            "retail_futures_net": float(retail_fut),
            "institution_futures_net": float(inst_fut),
            "program_arb_net": float(self._program_arb),
            "program_non_arb_net": float(self._program_nonarb),
            "foreign_retail_divergence": float(foreign_fut - retail_fut),
            # [MW0601 451차 폐기] program_foreign/individual/institution_net_krw 3종 제거.
            #   - individual/institution: 원천(CpSvr8111)에 없는 필드 → 상수 0이었다.
            #   - foreign: 값은 있었으나 외국인이 아니라 **전체 프로그램 순매수**를
            #     오라벨한 것이었고, 위 program_arb_net + program_non_arb_net의
            #     정확한 합이라 정보가 100% 중복이다.
            # 3종 모두 horizon_feature_sets.json:excluded_from_all_horizons 등재 상태여서
            # 학습·추론 영향은 이미 0이었다(과거 DB 행 보호를 위해 그 등재는 유지한다).
            # Day 8 quality flags (수치형: FeatureBuilder가 float 캐스팅 가능해야 함)
            "quality_investor_supported": 1.0 if runtime_supported else 0.0,
            "quality_investor_futures_supported": 1.0 if self._futures_supported else 0.0,
            "quality_investor_program_supported": 1.0 if self._program_supported else 0.0,
            "quality_investor_option_supported": 1.0 if self._option_flow_supported else 0.0,
            "quality_investor_stale": 1.0 if is_stale else 0.0,
            "quality_investor_age_sec": float(max(age_sec, 0.0)),
            # clip 60→5: 소급 데이터 99.9%가 0이어서 스케일러 평균≈0 → 60이면 z=+8 폭발
            # 5 이상은 모두 "충분히 수집됨"으로 처리 — GBM에 필요한 정보는 0 vs 1~5
            "quality_investor_fetch_count": float(min(self._fetch_count, 5)),
            "quality_investor_source_code": float(self._source_code(self._futures_source, self._program_source)),
            "quality_investor_reason_code": float(self._reason_code(self._futures_reason, self._program_reason)),
        }

    def get_zone_data(self) -> Dict[str, Dict[str, int]]:
        if not self._option_flow_supported:
            return {}

        fi_abs = abs(self._call.get("foreign", 0)) + abs(self._put.get("foreign", 0))
        rt_abs = abs(self._call.get("individual", 0)) + abs(self._put.get("individual", 0))
        inst_abs = abs(self._call.get("institution", 0)) + abs(self._put.get("institution", 0))
        total = max(fi_abs + rt_abs + inst_abs, 1)

        return {
            "ITM": {label: 0 for label in ZONE_LABELS.values()},
            "ATM": {
                ZONE_LABELS["foreign"]: round(fi_abs * 100 / total),
                ZONE_LABELS["individual"]: round(rt_abs * 100 / total),
                ZONE_LABELS["institution"]: round(inst_abs * 100 / total),
            },
            "OTM": {label: 0 for label in ZONE_LABELS.values()},
        }

    def get_panel_data(self) -> Dict[str, Any]:
        features = self.get_features()
        foreign_fut = int(features["foreign_futures_net"])
        retail_fut = int(features["retail_futures_net"])
        inst_fut = int(features["institution_futures_net"])
        divergence = int(features["foreign_retail_divergence"])

        if self._futures_supported and self._program_supported:
            panel_status = "partial"
            status_text = "Cybos futures/program investor flow live; option flow pending"
        elif self._futures_supported:
            panel_status = "partial"
            status_text = "Cybos futures investor flow live; {0}; option flow pending".format(
                self._program_status_text(self._program_source, self._program_reason)
            )
        elif self._program_supported:
            panel_status = "partial"
            status_text = "Cybos program investor flow live; futures/option flow pending"
        else:
            panel_status = "unavailable"
            status_text = "Cybos investor-flow unavailable; {0}".format(
                self._program_status_text(self._program_source, self._program_reason)
            )

        if self._futures_supported:
            if retail_fut > 0:
                contrarian = "개인 매수 우위"
            elif retail_fut < 0:
                contrarian = "개인 매도 우위"
            else:
                contrarian = "중립"
        else:
            contrarian = "대기"

        # 콜/풋 순매수 — CpSvrNew7212 제공 시 실제값, 미제공 시 0
        fi_call = self._call.get("foreign", 0)
        fi_put  = self._put.get("foreign", 0)
        rt_call = self._call.get("individual", 0)
        rt_put  = self._put.get("individual", 0)

        fi_abs = abs(fi_call) + abs(fi_put)
        rt_abs = abs(rt_call) + abs(rt_put)
        fi_bias = float(fi_call - fi_put) / max(fi_abs, 1) if fi_abs else 0.0
        rt_bias = float(rt_call - rt_put) / max(rt_abs, 1) if rt_abs else 0.0

        # 상태 텍스트: option_flow_supported 반영
        if self._option_flow_supported:
            if self._futures_supported and self._program_supported:
                status_text = "Cybos futures/program/option investor flow live"
            elif self._futures_supported:
                status_text = "Cybos futures/option investor flow live; program flow pending"
            else:
                status_text = "Cybos option investor flow live; futures/program flow pending"

        panel = {
            "panel_status": panel_status,
            "panel_status_text": status_text,
            "futures_supported": self._futures_supported,
            "program_supported": self._program_supported,
            "option_flow_supported": self._option_flow_supported,
            "option_flow_status": "pending_mapping" if not self._option_flow_supported else "live",
            "option_flow_reason": self._option_flow_reason,
            "rt_bias": rt_bias,
            "fi_bias": fi_bias,
            "rt_call": rt_call,
            "rt_put": rt_put,
            "rt_strd": rt_abs,
            "fi_call": fi_call,
            "fi_put": fi_put,
            "fi_strangle": fi_abs,
            "contrarian": contrarian,
            "div_score": float(divergence),
            "zones": self.get_zone_data(),
            # 선물 투자자별 순매수 (계약수)
            "foreign_futures_net": foreign_fut,
            "retail_futures_net": retail_fut,
            "institution_futures_net": inst_fut,
            # 프로그램 매매 — 원천이 주는 차익/비차익만. 투자자별 분해는 없다(451차).
            "program_arb_net": self._program_arb,
            "program_nonarb_net": self._program_nonarb,
            "program_total_net_krw": self._program_total,
            # 미결제약정 (FutureMst 또는 선물 투자자 TR 응답)
            "open_interest": self._open_interest,
        }
        logger.info(
            "[DivergencePanel] source=cybos status=%s div=%+d "
            "futures(fi=%+d rt=%+d inst=%+d) "
            "call(fi=%+d rt=%+d) put(fi=%+d rt=%+d) "
            "bias(fi=%.2f rt=%.2f) program(arb=%+d nonarb=%+d total=%+d)",
            panel_status,
            divergence,
            foreign_fut, retail_fut, inst_fut,
            fi_call, rt_call,
            fi_put, rt_put,
            fi_bias, rt_bias,
            self._program_arb,
            self._program_nonarb,
            self._program_total,
        )
        return panel

    def reset_daily(self) -> None:
        self._last_fetch = None
        self._fetch_count = 0
        self._futures = {k: 0 for k in INVESTOR_KEYS}
        self._call = {k: 0 for k in INVESTOR_KEYS}
        self._put = {k: 0 for k in INVESTOR_KEYS}
        self._program_arb = 0
        self._program_nonarb = 0
        self._program_total = 0
        self._open_interest = 0
        # 관측 횟수만 리셋 — '본 적 있음' 이력은 유지한다(provenance.py:reset 참조).
        self._futures_prov.reset()
        self._program_prov.reset()
        self._futures_supported = False
        self._program_supported = False
        self._option_flow_supported = False
        self._futures_source = "unavailable"
        self._program_source = "unavailable"
        self._option_flow_source = "unavailable"
        self._futures_reason = "reset"
        self._program_reason = "reset"
        self._option_flow_reason = "Cybos option investor-flow mapping pending"

    def get_stats(self) -> dict:
        age_sec = (
            (datetime.datetime.now() - self._last_fetch).total_seconds()
            if self._last_fetch else 9999.0
        )
        return {
            "fetch_count": self._fetch_count,
            "last_fetch": self._last_fetch.strftime("%H:%M:%S") if self._last_fetch else "",
            "foreign_net": self._futures.get("foreign", 0),
            # 451차: prog_fi_krw(=외국인 오라벨) → prog_total_krw(차익+비차익 합계)
            "prog_total_krw": self._program_total,
            "futures_supported": self._futures_supported,
            "program_supported": self._program_supported,
            "option_supported": self._option_flow_supported,
            "quality_age_sec": round(age_sec, 1),
            "quality_stale": age_sec > 180.0,
            "program_source": self._program_source,
            "program_reason": self._program_reason,
            "quality_source_code": self._source_code(self._futures_source, self._program_source),
            "quality_reason_code": self._reason_code(self._futures_reason, self._program_reason),
        }

    @staticmethod
    def _source_code(futures_source: str, program_source: str) -> int:
        src = f"{futures_source}|{program_source}".lower()
        if "api_missing" in src or "unavailable" in src:
            return 0
        if "cp" in src or "tr" in src or "futuremst" in src:
            return 2
        return 1

    @staticmethod
    def _reason_code(futures_reason: str, program_reason: str) -> int:
        text = f"{futures_reason}|{program_reason}".lower()
        if "missing" in text or "pending" in text:
            return 0
        if "live" in text or "제공" in text:
            return 2
        if "status nonzero" in text or "all-zero payload" in text or "zero-response" in text:
            return 3
        return 1

    @staticmethod
    def _program_status_label(program_source: str, program_reason: str) -> str:
        source = (program_source or "").lower()
        reason = (program_reason or "").lower()
        if "status nonzero" in reason:
            return "status_error"
        if "all-zero payload" in reason or "zero-response" in reason:
            return "zero_response"
        if "missing" in source or "api_missing" in source:
            return "api_missing"
        if "pending" in source or "pending" in reason or "unavailable" in reason:
            return "mapping_pending"
        if "probe ok" in reason or "live" in reason:
            return "live"
        return "unknown"

    @classmethod
    def _program_status_text(cls, program_source: str, program_reason: str) -> str:
        state = cls._program_status_label(program_source, program_reason)
        if state == "status_error":
            return "program flow reachable but server returned nonzero status"
        if state == "zero_response":
            return "program flow object reachable but payload is all zero"
        if state == "api_missing":
            return "program flow helper missing"
        if state == "mapping_pending":
            return "program flow mapping pending"
        if state == "live":
            return "program flow live"
        return "program flow state unknown"
