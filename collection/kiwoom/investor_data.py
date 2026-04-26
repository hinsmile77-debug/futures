# collection/kiwoom/investor_data.py — 투자자별 수급 수집
"""
외인·기관·개인 선물/옵션 매매 수급 실시간 수집

수집 항목:
  opt10059 — 선물 투자자별 매매 (외인/기관/개인/증권/투신/연기금 등)
  opt50014 — 옵션 투자자별 매매 (콜/풋 구분)
  opt10060 — 프로그램 매매 (차익/비차익)

수집 방법:
  장 중 1분마다 TR 조회 → 누적 수급 업데이트
  실시간 데이터 없음 (키움 옵션) → TR 폴링 방식

출력:
  features/supply_demand 피처 계산에 사용
"""
import logging
import datetime
from typing import Optional, Dict, TYPE_CHECKING

from config.constants import (
    TR_INVESTOR_FUTURES, TR_INVESTOR_OPTIONS, TR_PROGRAM_TRADE,
)

if TYPE_CHECKING:
    from collection.kiwoom.api_connector import KiwoomAPI

logger = logging.getLogger("DATA")

# 투자자 구분 코드 (키움 opt10059 순서)
INVESTOR_KEYS = [
    "individual",   # 개인
    "foreign",      # 외국인
    "institution",  # 기관계
    "financial",    # 금융투자(증권)
    "insurance",    # 보험
    "trust",        # 투신
    "bank",         # 은행
    "pension",      # 연기금
    "etc_corp",     # 기타법인
    "nation",       # 국가/지자체
]


class InvestorData:
    """
    투자자별 수급 수집 및 집계

    사용:
        inv = InvestorData(kiwoom_api)
        inv.fetch_futures()      # 선물 수급 조회
        feats = inv.get_features()  # 피처 딕셔너리 반환
    """

    def __init__(self, kiwoom_api=None):
        self._api = kiwoom_api

        # 현재 수급 데이터 (당일 누적)
        self._futures: Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._call:    Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._put:     Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._program_arb     = 0
        self._program_nonarb  = 0

        self._last_fetch: Optional[datetime.datetime] = None
        self._fetch_count = 0

    # ── 데이터 수집 ───────────────────────────────────────────────
    def fetch_all(self) -> bool:
        """선물 + 옵션 + 프로그램 전체 조회"""
        ok1 = self.fetch_futures()
        ok2 = self.fetch_options()
        ok3 = self.fetch_program()
        self._last_fetch = datetime.datetime.now()
        self._fetch_count += 1
        return ok1

    def fetch_futures(self) -> bool:
        """선물 투자자별 매매 TR 조회 (opt10059)"""
        if self._api is None:
            return self._fill_dummy_futures()

        try:
            self._api.set_input_value("일자", datetime.date.today().strftime("%Y%m%d"))
            self._api.set_input_value("종목코드", "101Q9000")
            self._api.comm_rq_data(TR_INVESTOR_FUTURES, TR_INVESTOR_FUTURES, 0, "2001")
            return True
        except Exception as e:
            logger.warning(f"[Investor] 선물 수급 조회 오류: {e}")
            return False

    def fetch_options(self) -> bool:
        """옵션 투자자별 매매 조회 (opt50014)"""
        if self._api is None:
            return self._fill_dummy_options()
        try:
            self._api.set_input_value("일자", datetime.date.today().strftime("%Y%m%d"))
            self._api.comm_rq_data(TR_INVESTOR_OPTIONS, TR_INVESTOR_OPTIONS, 0, "2002")
            return True
        except Exception as e:
            logger.warning(f"[Investor] 옵션 수급 조회 오류: {e}")
            return False

    def fetch_program(self) -> bool:
        """프로그램 매매 조회 (opt10060)"""
        if self._api is None:
            return True
        try:
            self._api.comm_rq_data(TR_PROGRAM_TRADE, TR_PROGRAM_TRADE, 0, "2003")
            return True
        except Exception as e:
            logger.warning(f"[Investor] 프로그램 조회 오류: {e}")
            return False

    # ── TR 수신 콜백 (api_connector에서 호출) ─────────────────────
    def on_receive_trdata(self, trcode: str, rqname: str, data_rows: list):
        """
        키움 API TR 수신 콜백

        api_connector.py의 OnReceiveTrData 이벤트에서 호출
        data_rows: TR 응답 데이터 rows
        """
        if trcode == TR_INVESTOR_FUTURES:
            self._parse_futures_tr(data_rows)
        elif trcode == TR_INVESTOR_OPTIONS:
            self._parse_options_tr(data_rows)
        elif trcode == TR_PROGRAM_TRADE:
            self._parse_program_tr(data_rows)

    def _parse_futures_tr(self, rows: list):
        """opt10059 파싱 — 투자자별 선물 순매수"""
        for i, key in enumerate(INVESTOR_KEYS):
            if i < len(rows):
                try:
                    self._futures[key] = int(rows[i].get("순매수", "0").replace(",", ""))
                except (ValueError, AttributeError):
                    pass

    def _parse_options_tr(self, rows: list):
        """opt50014 파싱 — 투자자별 콜/풋 순매수"""
        for i, key in enumerate(INVESTOR_KEYS):
            if i < len(rows):
                try:
                    self._call[key] = int(rows[i].get("콜순매수", "0").replace(",", ""))
                    self._put[key]  = int(rows[i].get("풋순매수", "0").replace(",", ""))
                except (ValueError, AttributeError):
                    pass

    def _parse_program_tr(self, rows: list):
        if rows:
            try:
                self._program_arb    = int(rows[0].get("차익순매수", "0").replace(",", ""))
                self._program_nonarb = int(rows[0].get("비차익순매수", "0").replace(",", ""))
            except (ValueError, AttributeError):
                pass

    # ── 피처 계산 ─────────────────────────────────────────────────
    def get_features(self) -> Dict[str, float]:
        """
        수급 → 트레이딩 피처 변환

        Returns:
            constants.py SUPPLY_DEMAND_FEATURES 형식의 딕셔너리
        """
        foreign_fut  = self._futures.get("foreign", 0)
        retail_fut   = self._futures.get("individual", 0)
        inst_fut     = self._futures.get("institution", 0)
        pension      = self._futures.get("pension", 0)

        foreign_call = self._call.get("foreign", 0)
        foreign_put  = self._put.get("foreign", 0)
        retail_call  = self._call.get("individual", 0)
        retail_put   = self._put.get("individual", 0)

        # 외인-개인 괴리 (역발상 신호)
        fr_divergence = float(foreign_fut - retail_fut)

        # 소매 OTM 역발상 (개인이 OTM 콜 사면 → 하락 신호)
        retail_otm_contrarian = float(-retail_call + retail_put) if retail_call > 0 else 0.0

        return {
            "foreign_futures_net":      float(foreign_fut),
            "foreign_call_net":         float(foreign_call),
            "foreign_put_net":          float(foreign_put),
            "retail_futures_net":       float(retail_fut),
            "institution_futures_net":  float(inst_fut),
            "program_arb_net":          float(self._program_arb),
            "program_non_arb_net":      float(self._program_nonarb),
            "foreign_retail_divergence": fr_divergence,
        }

    # ── 더미 (시뮬레이션) ─────────────────────────────────────────
    def _fill_dummy_futures(self) -> bool:
        import random
        base = random.randint(-500, 500)
        self._futures["foreign"]    = base
        self._futures["individual"] = -base + random.randint(-100, 100)
        self._futures["institution"] = random.randint(-200, 200)
        self._futures["pension"]     = random.randint(0, 100)
        return True

    def _fill_dummy_options(self) -> bool:
        import random
        self._call["foreign"] = random.randint(-200, 200)
        self._put["foreign"]  = random.randint(-200, 200)
        return True

    def reset_daily(self):
        self._futures = {k: 0 for k in INVESTOR_KEYS}
        self._call    = {k: 0 for k in INVESTOR_KEYS}
        self._put     = {k: 0 for k in INVESTOR_KEYS}
        self._program_arb    = 0
        self._program_nonarb = 0
        self._fetch_count = 0

    def get_stats(self) -> dict:
        return {
            "fetch_count":  self._fetch_count,
            "last_fetch":   self._last_fetch.strftime("%H:%M:%S") if self._last_fetch else "",
            "foreign_net":  self._futures.get("foreign", 0),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    inv = InvestorData(kiwoom_api=None)
    inv.fetch_all()
    print(inv.get_features())
