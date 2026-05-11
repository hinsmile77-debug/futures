from __future__ import annotations

import datetime
import logging
from typing import Any, Dict, Optional

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
        self._program_investor: Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._open_interest = 0

        self._futures_supported = False
        self._program_supported = False
        self._option_flow_supported = False
        self._futures_source = "unavailable"
        self._program_source = "unavailable"
        self._option_flow_source = "unavailable"
        self._futures_reason = "not fetched"
        self._program_reason = "not fetched"
        self._option_flow_reason = "Cybos option investor-flow mapping pending"

    def fetch_all(self) -> bool:
        futures_ok = self.fetch_futures_investor()
        program_ok = self.fetch_program_investor()
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
        for key in INVESTOR_KEYS:
            self._futures[key] = _to_int(nets.get(key, self._futures.get(key, 0)))

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
        nets = result.get("nets") or {}
        for key in INVESTOR_KEYS:
            self._program_investor[key] = _to_int(nets.get(key, self._program_investor.get(key, 0)))

        # 차익/비차익 순매수 (raw 에서 직접 추출)
        raw = result.get("raw") or {}
        self._program_arb    = _to_int(raw.get("arb_net",    self._program_arb))
        self._program_nonarb = _to_int(raw.get("nonarb_net", self._program_nonarb))

        self._program_supported = bool(result.get("supported", False))
        self._program_source = str(result.get("source", "unknown"))
        self._program_reason = str(result.get("reason", ""))
        logger.info(
            "[CybosInvestor] program supported=%s source=%s "
            "foreign=%+d individual=%+d institution=%+d "
            "arb=%+d nonarb=%+d reason=%s",
            self._program_supported,
            self._program_source,
            self._program_investor.get("foreign", 0),
            self._program_investor.get("individual", 0),
            self._program_investor.get("institution", 0),
            self._program_arb,
            self._program_nonarb,
            self._program_reason,
        )
        return self._program_supported

    def get_features(self) -> Dict[str, float]:
        foreign_fut = self._futures.get("foreign", 0)
        retail_fut = self._futures.get("individual", 0)
        inst_fut = self._futures.get("institution", 0)

        return {
            "foreign_futures_net": float(foreign_fut),
            "foreign_call_net": float(self._call.get("foreign", 0)),
            "foreign_put_net": float(self._put.get("foreign", 0)),
            "retail_futures_net": float(retail_fut),
            "institution_futures_net": float(inst_fut),
            "program_arb_net": float(self._program_arb),
            "program_non_arb_net": float(self._program_nonarb),
            "foreign_retail_divergence": float(foreign_fut - retail_fut),
            "program_foreign_net_krw": float(self._program_investor.get("foreign", 0)),
            "program_institution_net_krw": float(self._program_investor.get("institution", 0)),
            "program_individual_net_krw": float(self._program_investor.get("individual", 0)),
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
            status_text = "Cybos futures investor flow live; program/option flow pending"
        elif self._program_supported:
            panel_status = "partial"
            status_text = "Cybos program investor flow live; futures/option flow pending"
        else:
            panel_status = "unavailable"
            status_text = "Cybos investor-flow mapping pending; showing availability state only"

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
            "rt_strd": 0,
            "fi_call": fi_call,
            "fi_put": fi_put,
            "fi_strangle": 0,
            "contrarian": contrarian,
            "div_score": float(divergence),
            "zones": self.get_zone_data(),
            # 선물 투자자별 순매수 (계약수)
            "foreign_futures_net": foreign_fut,
            "retail_futures_net": retail_fut,
            "institution_futures_net": inst_fut,
            # 프로그램 매매
            "program_arb_net": self._program_arb,
            "program_nonarb_net": self._program_nonarb,
            "program_foreign_net_krw": int(features["program_foreign_net_krw"]),
            "program_individual_net_krw": int(features["program_individual_net_krw"]),
            "program_institution_net_krw": int(features["program_institution_net_krw"]),
            # 미결제약정 (FutureMst 또는 선물 투자자 TR 응답)
            "open_interest": self._open_interest,
        }
        logger.info(
            "[DivergencePanel] source=cybos status=%s div=%+d "
            "futures(fi=%+d rt=%+d inst=%+d) "
            "call(fi=%+d rt=%+d) put(fi=%+d rt=%+d) "
            "bias(fi=%.2f rt=%.2f) program(fi=%+d rt=%+d inst=%+d)",
            panel_status,
            divergence,
            foreign_fut, retail_fut, inst_fut,
            fi_call, rt_call,
            fi_put, rt_put,
            fi_bias, rt_bias,
            panel["program_foreign_net_krw"],
            panel["program_individual_net_krw"],
            panel["program_institution_net_krw"],
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
        self._program_investor = {k: 0 for k in INVESTOR_KEYS}
        self._open_interest = 0
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
        return {
            "fetch_count": self._fetch_count,
            "last_fetch": self._last_fetch.strftime("%H:%M:%S") if self._last_fetch else "",
            "foreign_net": self._futures.get("foreign", 0),
            "prog_fi_krw": self._program_investor.get("foreign", 0),
            "futures_supported": self._futures_supported,
            "program_supported": self._program_supported,
            "option_supported": self._option_flow_supported,
        }
