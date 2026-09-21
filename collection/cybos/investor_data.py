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

# [MW0601 612차] 「역발상 신호」 데드밴드 (계약수).
#
# 종전엔 `retail_fut > 0 / < 0` 순수 부호 판정이라 개인 선물 순매수가 0 근처를
# 배회하는 동안 카드가 계속 뒤집혔다 — 실측 부호 전환 09-18 **14회** / 09-14 8회 /
# 09-21 3회. 표시 전용 임계이며 매매 판단에는 쓰이지 않는다.
#
# ⚠ 절대 계약수 고정 임계다. 미결제약정·거래량 체제가 바뀌면 함께 드리프트한다
#   (539차 `ATR_MIN_ENTRY` 와 같은 계열). 26주 WFA 때 재확인 대상.
CONTRARIAN_DEADBAND_CONTRACTS = 200


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
        # [MW0601 612차 후속2] 선물 순매수 **금액**(백만원) — 7221 열 30/31/32.
        # 계약수와 별개 축이며 **원천이 직접 준다**(우리가 환산하지 않는다).
        self._futures_amt: Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._futures_amt_seen: set = set()
        self._call: Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._put: Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._program_arb = 0
        self._program_nonarb = 0
        # 차익+비차익 합계(KRW). 투자자별 분해가 아니다 — 이름으로 그것을 못 박는다.
        self._program_total = 0
        # [451차 Phase 1-1] CpSvr8111 원천 56필드. **해석하지 않고 그대로 보관만** 한다 —
        # 저장은 main._fetch_investor_data가 한다(수집 클래스는 DB를 모른다).
        self._program_fields: Dict[str, int] = {}
        self._open_interest = 0

        # [MW0601 559차 / P1'-1] **오늘 원천이 실제로 준 키**. 이월 폴백(`_futures` 는
        # 직전값을 유지한다)과 프리장 초기 0 을 구분하는 유일한 근거다.
        # 🔴 이게 없으면 「프리장이라 아직 안 왔다」와 「실측 순매수 0계약」이 DB 에서
        #    같은 0.0 으로 보인다 — 계측 4원칙 ②. 481차 F-1 항목.
        self._futures_seen: set = set()

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
        self._option_flow_reason = "옵션 수급 TR 매핑 대기"

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
            # [451차 Phase 1-1] 프로그램 조회를 건너뛰었으면 원천 필드도 비운다.
            # 안 비우면 직전 성공분이 남아, 나중에 누가 "현재 시각 + 옛 값"으로 저장할 수
            # 있다 — 이번 세션 내내 다룬 "안 온 것을 온 것처럼" 패턴 그 자체다.
            # (현재 유일한 저장 경로 main._fetch_investor_data는 항상 include_program=True로
            #  먼저 갱신하므로 실제 사고는 없지만, 그 전제가 깨지는 순간 조용히 오염된다.)
            self._program_fields = {}
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
        # [559차 P1'-1] 이번 조회가 실제로 준 키만 적립한다. 값이 0 이어도 "왔다"는 사실이다.
        self._futures_seen.update(k for k in nets.keys() if k in INVESTOR_KEYS)
        for key in INVESTOR_KEYS:
            self._futures[key] = _to_int(nets.get(key, self._futures.get(key, 0)))

        # [612차 후속2] 금액 축 — 계약수와 **따로** 측정여부를 센다.
        # 7221 이외 후보(FutureTrader 등)는 이 열을 주지 않으므로, 계약수는 왔는데
        # 금액은 안 온 상태가 성립한다. 한 플래그로 뭉뚱그리면 안 된다(계측 4원칙 ②).
        net_amounts = result.get("net_amounts") or {}
        self._futures_amt_seen.update(
            k for k in net_amounts.keys() if k in INVESTOR_KEYS)
        for key in INVESTOR_KEYS:
            self._futures_amt[key] = _to_int(
                net_amounts.get(key, self._futures_amt.get(key, 0)))
        self._futures_prov.maybe_warn(
            logger, _EMITTED_INVESTOR_KEYS, bool(result.get("supported", False))
        )

        # call_nets / put_nets — CpSvrNew7221 옵션콜·풋 행 제공 시 option_flow도 갱신
        call_nets = result.get("call_nets") or {}
        put_nets  = result.get("put_nets")  or {}
        if call_nets or put_nets:
            for key in INVESTOR_KEYS:
                self._call[key] = _to_int(call_nets.get(key, self._call.get(key, 0)))
                self._put[key]  = _to_int(put_nets.get(key,  self._put.get(key, 0)))
            self._option_flow_supported = True
            self._option_flow_source    = result.get("source", "unknown")
            self._option_flow_reason    = "콜/풋 순매수 제공 (CpSvrNew7221)"

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

        # [451차 Phase 1-1] 원천 56필드 보관. **조회 성공일 때만** 갱신한다 —
        # 실패 시 직전값을 남겨두면 그 시각에 실제로 수신한 것처럼 저장돼
        # 451차가 폐기한 "안 온 것을 온 것처럼" 패턴이 그대로 재현된다.
        if self._program_supported:
            self._program_fields = dict(result.get("fields") or {})
        else:
            self._program_fields = {}

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

    def get_program_raw_fields(self) -> Dict[str, int]:
        """[451차 Phase 1-1] 직전 **성공** 조회의 CpSvr8111 56필드 (보존 저장용).

        조회 실패·미지원이면 **빈 dict**를 반환한다 — 호출부는 빈 dict를 저장하지 말 것
        (`utils/db_utils.save_program_trade_raw`가 한 번 더 막는다).
        필드 의미: `docs/CyBos ref/CYBOS_프로그램매매_투자자별_TR_명세.md` §1-1.
        """
        return dict(self._program_fields)

    # [MW0601 612차 후속2] 정규 KOSPI200 선물 승수(원/pt).
    # 🔴 **우리 매매 종목(미니 A05·50,000)의 승수가 아니다.** 7221 선물 행은
    #    시장 전체 수급이라 정규 계약 기준이다. `active_contract_spec()` 으로
    #    "고치면" 5배 틀린다(settings.py §승수 단일원천 주석과 충돌하지 않는다 —
    #    그 규약은 *우리 포지션*의 승수에 대한 것이다).
    _REGULAR_FUT_PT_VALUE = 250_000
    # 대사 허용 오차 — 열 매핑이 바뀌면 이 비율이 깨진다.
    _AMT_RECON_TOL = 0.20

    def check_amount_consistency(self, ref_price: float) -> Optional[float]:
        """[612차 후속2] 금액 ÷ 계약수 가 `지수 × 250,000` 과 맞는지 대사한다.

        계측 4원칙 ⑤ — 파생값을 쓰려면 구성요소를 각각 걸어라. 여기서는 원천이
        주는 **두 축(계약·금액)이 서로 정합한지**를 매번 확인해, 열 30/31/32 의
        의미가 바뀌거나 행 레이아웃이 밀리면 조용히 틀린 억원이 나가지 않게 한다.

        근거: RAW 덤프 11개/5거래일/33개 비율에서 `금액÷계약` 이 259~279 백만원이고
        지수 수준을 따라갔다(0.5% 이내로 `지수 × 250,000` 과 일치).

        Returns: 실측 배수(백만원/계약). 대사 불가면 None.
        """
        if not ref_price or ref_price <= 0:
            return None
        expected_mn = ref_price * self._REGULAR_FUT_PT_VALUE / 1e6
        # 계약수가 충분히 큰 투자자로만 잰다 — 소수 계약은 반올림 오차가 크다.
        best_key, best_qty = None, 0
        for k in _EMITTED_INVESTOR_KEYS:
            q = abs(self._futures.get(k, 0))
            if q > best_qty:
                best_key, best_qty = k, q
        if best_key is None or best_qty < 50:
            return None
        amt = self._futures_amt.get(best_key, 0)
        if not amt:
            return None
        actual_mn = abs(float(amt)) / float(best_qty)
        if abs(actual_mn - expected_mn) / expected_mn > self._AMT_RECON_TOL:
            logger.warning(
                "[CybosInvestor] 선물 금액축 대사 실패 — %s 실측 %.1f 백만원/계약 vs "
                "기대 %.1f (지수 %.2f × %d). 7221 열 30/31/32 매핑이 바뀌었을 수 있다. "
                "억원 표시를 신뢰하지 말 것(612차 후속2)",
                best_key, actual_mn, expected_mn, ref_price,
                self._REGULAR_FUT_PT_VALUE,
            )
        return actual_mn

    def _is_measured(self, key: str) -> bool:
        """[559차 P1'-1] 이 키를 오늘 원천에서 **실제로 받은 적이 있는가**.

        `self._futures[key]` 는 이월 폴백 때문에 항상 값이 있다 — 그 값이 관측인지
        초기 0 인지는 여기서만 알 수 있다. 프리장(08:45~08:59)에는 전부 False 다.
        """
        return bool(self._futures_supported) and key in self._futures_seen

    def _is_amt_measured(self, key: str) -> bool:
        """[612차 후속2] 금액 축을 오늘 원천에서 실제로 받았는가.

        계약수와 **따로** 센다 — 7221 이외 후보는 열 30/31/32 를 주지 않으므로
        "계약은 왔는데 금액은 안 왔다"가 성립한다.
        """
        return bool(self._futures_supported) and key in self._futures_amt_seen

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
            # ── [MW0601 559차 / P1'-1] 피처별 미측정 플래그 (481차 F-1) ──────────
            # 1.0 = 오늘 원천이 이 키를 실제로 줬다 / 0.0 = 아직 안 왔다(값 0 은 폴백).
            # 값 자체는 하위호환으로 그대로 0.0 을 내보낸다 — 하류가 플래그를 보고
            # 판단하게 하고, 값의 의미를 조용히 바꾸지 않는다.
            "foreign_futures_net_measured": 1.0 if self._is_measured("foreign") else 0.0,
            "retail_futures_net_measured": 1.0 if self._is_measured("individual") else 0.0,
            "institution_futures_net_measured": 1.0 if self._is_measured("institution") else 0.0,
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
            status_text = "선물·프로그램 수급 수신 중 (옵션 수급 대기)"
        elif self._futures_supported:
            panel_status = "partial"
            status_text = "선물 수급 수신 중 · {0} · 옵션 수급 대기".format(
                self._program_status_text(self._program_source, self._program_reason)
            )
        elif self._program_supported:
            panel_status = "partial"
            status_text = "프로그램 수급만 수신 중 (선물·옵션 수급 대기)"
        else:
            panel_status = "unavailable"
            status_text = "수급 수신 불가 · {0}".format(
                self._program_status_text(self._program_source, self._program_reason)
            )

        if self._futures_supported:
            # [MW0601 612차] 데드밴드 도입. 종전엔 순수 부호 판정이라 0 근방에서
            # 카드가 하루 종일 뒤집혔다 — 실측 부호 전환 09-18 **14회** / 09-14 8회.
            # 개인 선물 순매수는 일중 누계라 0 근처를 오래 배회하는 구간이 있다.
            if retail_fut > CONTRARIAN_DEADBAND_CONTRACTS:
                contrarian = "개인 매수 우위"
            elif retail_fut < -CONTRARIAN_DEADBAND_CONTRACTS:
                contrarian = "개인 매도 우위"
            else:
                contrarian = "중립"
        else:
            contrarian = "대기"

        # 콜/풋 순매수 — CpSvrNew7221 옵션콜·풋 행 제공 시 실제값, 미제공 시 0
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
                status_text = "선물·프로그램·옵션 수급 정상 수신 중"
            elif self._futures_supported:
                status_text = "선물·옵션 수급 수신 중 (프로그램 수급 대기)"
            else:
                status_text = "옵션 수급만 수신 중 (선물·프로그램 수급 대기)"

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
            # 선물 투자자별 순매수 (계약수) — `div_score` 등 기존 소비처가 쓴다
            "foreign_futures_net": foreign_fut,
            "retail_futures_net": retail_fut,
            "institution_futures_net": inst_fut,
            # [MW0601 612차 후속2] 선물 투자자별 순매수 **금액(백만원)** —
            # 7221 열 30/31/32 원값. 패널은 이것을 억원으로 나눠 표시한다.
            # 계약수와 다른 축이므로 키 이름에 단위를 박는다(계측 4원칙 ①).
            "foreign_futures_amt_mn": self._futures_amt.get("foreign", 0),
            "retail_futures_amt_mn": self._futures_amt.get("individual", 0),
            "institution_futures_amt_mn": self._futures_amt.get("institution", 0),
            "foreign_futures_amt_measured": bool(self._is_amt_measured("foreign")),
            "retail_futures_amt_measured": bool(self._is_amt_measured("individual")),
            "institution_futures_amt_measured":
                bool(self._is_amt_measured("institution")),
            # 프로그램 매매 — 원천이 주는 차익/비차익만. 투자자별 분해는 없다(451차).
            "program_arb_net": self._program_arb,
            "program_nonarb_net": self._program_nonarb,
            "program_total_net_krw": self._program_total,
            # 미결제약정 (FutureMst 또는 선물 투자자 TR 응답)
            "open_interest": self._open_interest,
            # ── [MW0601 612차] 신선도·측정여부 ────────────────────────────────
            # 🔴 종전에 패널은 이 두 축을 **하나도 받지 못했다.** TR 이 실패하면
            #    `_futures` 가 직전값을 유지하므로 **멈춘 값이 살아 있는 값처럼**
            #    보였다(계측 4원칙 ④). `get_features()` 는 이미 만들고 있던 값인데
            #    `get_panel_data()` 가 싣지 않아 화면까지 오지 않았을 뿐이다.
            "age_sec": float(features["quality_investor_age_sec"]),
            "stale": bool(features["quality_investor_stale"]),
            # [612차 후속5] **절대 시각**도 함께 준다.
            # `age_sec` 만 주면 패널이 그 숫자를 화면에 박아두므로, 갱신이 끊기면
            # 신선도 칩 자체가 함께 얼어 「수급 15초 전」이 영원히 남는다 —
            # 낡음을 알리려던 표시가 낡음을 감춘다(2026-09-21 15:09 실측).
            # 패널이 스스로 나이를 다시 계산할 수 있게 원점을 넘긴다.
            "last_fetch_epoch": (
                float(self._last_fetch.timestamp()) if self._last_fetch else None),
            # 559차 `*_measured` — "아직 안 왔다"와 "실측 0계약"을 구분한다.
            # `futures_supported`(= TR 응답 여부)로는 구분되지 않는다.
            "foreign_futures_net_measured":
                bool(features["foreign_futures_net_measured"]),
            "retail_futures_net_measured":
                bool(features["retail_futures_net_measured"]),
            "institution_futures_net_measured":
                bool(features["institution_futures_net_measured"]),
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
        self._futures_seen = set()          # [559차 P1'-1] 하루 단위로 다시 센다
        self._futures = {k: 0 for k in INVESTOR_KEYS}
        # [612차 후속2] 금액 축도 함께 리셋 — 안 하면 어제 금액이 오늘 화면에 남는다
        self._futures_amt = {k: 0 for k in INVESTOR_KEYS}
        self._futures_amt_seen = set()
        self._call = {k: 0 for k in INVESTOR_KEYS}
        self._put = {k: 0 for k in INVESTOR_KEYS}
        self._program_arb = 0
        self._program_nonarb = 0
        self._program_total = 0
        self._program_fields = {}
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
        self._option_flow_reason = "옵션 수급 TR 매핑 대기"

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
            return "프로그램 수급 응답은 오나 서버 status 가 0 이 아님"
        if state == "zero_response":
            return "프로그램 수급 응답이 전부 0"
        if state == "api_missing":
            return "프로그램 수급 helper 없음"
        if state == "mapping_pending":
            return "프로그램 수급 TR 매핑 대기"
        if state == "live":
            return "프로그램 수급 정상"
        return "프로그램 수급 상태 불명"
