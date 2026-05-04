# collection/kiwoom/investor_data.py — 투자자별 수급 수집
"""
외인·기관·개인 선물/옵션 매매 수급 실시간 수집

수집 항목:
  opt10059 — 선물 투자자별 매매 (외인/기관/개인/증권/투신/연기금 등)
  opt50014 — 옵션 투자자별 매매 (콜/풋 구분)
  opt10060 — 프로그램 매매 (차익/비차익)

수집 방법:
  main.py _investor_timer(QTimer 60s)에서 request_tr() 사용 — COM 콜백 외부
  COM 콜백 체인(run_minute_pipeline)에서는 get_features()로 캐시만 읽음

출력:
  features/supply_demand 피처 계산에 사용
"""
import logging
import datetime
from typing import Optional, Dict, TYPE_CHECKING

from config.constants import (
    TR_INVESTOR_FUTURES, TR_INVESTOR_OPTIONS, TR_PROGRAM_TRADE,
)
from utils.logger import LAYER_DATA

if TYPE_CHECKING:
    from collection.kiwoom.api_connector import KiwoomAPI

logger = logging.getLogger(LAYER_DATA)

# 투자자 구분 코드 (키움 opt10059/opt50014 응답 행 순서)
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
        inv.fetch_all()          # _investor_timer에서 호출 (COM 콜백 외부)
        feats = inv.get_features()  # 파이프라인에서 캐시 읽기
    """

    def __init__(self, kiwoom_api=None):
        self._api = kiwoom_api

        # 당일 누적 수급 (캐시)
        self._futures: Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._call:    Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._put:     Dict[str, int] = {k: 0 for k in INVESTOR_KEYS}
        self._program_arb     = 0
        self._program_nonarb  = 0

        self._last_fetch: Optional[datetime.datetime] = None
        self._fetch_count = 0

    # ── 데이터 수집 ───────────────────────────────────────────────
    def fetch_all(self) -> bool:
        """선물 + 옵션 + 프로그램 전체 조회.

        반드시 COM 콜백 외부(QTimer)에서 호출할 것.
        request_tr()이 QEventLoop 블로킹을 사용하므로 COM 콜백 체인에서 호출 시
        스택 오버런(0xC0000409) 위험.
        """
        ok1 = self.fetch_futures()
        ok2 = self.fetch_options()
        ok3 = self.fetch_program()
        self._last_fetch = datetime.datetime.now()
        self._fetch_count += 1
        ts = self._last_fetch.strftime("%H:%M:%S")
        logger.info(
            "[Investor] #%d 갱신 완료 %s | 선물=%s 옵션=%s 프로그램=%s",
            self._fetch_count, ts, ok1, ok2, ok3,
        )
        return ok1

    def fetch_futures(self) -> bool:
        """선물 투자자별 매매 TR 조회 (opt10059)."""
        if self._api is None:
            return self._fill_dummy_futures()
        try:
            result = self._api.request_tr(
                tr_code=TR_INVESTOR_FUTURES,
                rq_name="investor_futures",
                inputs={
                    "일자":   datetime.date.today().strftime("%Y%m%d"),
                    "종목코드": "101Q9000",
                },
                screen_no="2010",
            )
            if result and result.get("rows"):
                self._parse_futures_tr(result["rows"])
                logger.debug(
                    "[Investor] 선물 수급 rows=%d | 외인=%+d 개인=%+d",
                    len(result["rows"]),
                    self._futures.get("foreign", 0),
                    self._futures.get("individual", 0),
                )
                return True
            logger.warning("[Investor] 선물 TR 응답 없음 (rows=0 또는 타임아웃)")
            return False
        except Exception as e:
            logger.warning("[Investor] 선물 수급 조회 오류: %s", e)
            return False

    def fetch_options(self) -> bool:
        """옵션 투자자별 매매 조회 (opt50008 후보 — KOA Studio 필드명 확인 필요)."""
        if self._api is None:
            return self._fill_dummy_options()
        try:
            result = self._api.request_tr(
                tr_code=TR_INVESTOR_OPTIONS,
                rq_name="investor_options",
                inputs={
                    "일자": datetime.date.today().strftime("%Y%m%d"),
                },
                screen_no="2011",
            )
            if result and result.get("rows"):
                self._parse_options_tr(result["rows"])
                logger.debug(
                    "[Investor] 옵션 수급 rows=%d | 외인콜=%+d 풋=%+d 개인콜=%+d 풋=%+d",
                    len(result["rows"]),
                    self._call.get("foreign", 0),
                    self._put.get("foreign", 0),
                    self._call.get("individual", 0),
                    self._put.get("individual", 0),
                )
                return True
            logger.warning("[Investor] 옵션 TR 응답 없음 (rows=0 또는 타임아웃)")
            return False
        except Exception as e:
            logger.warning("[Investor] 옵션 수급 조회 오류: %s", e)
            return False

    def fetch_program(self) -> bool:
        """프로그램 매매 조회 (opt10060)."""
        if self._api is None:
            return True
        try:
            result = self._api.request_tr(
                tr_code=TR_PROGRAM_TRADE,
                rq_name="investor_program",
                inputs={
                    "일자": datetime.date.today().strftime("%Y%m%d"),
                },
                screen_no="2012",
            )
            if result and result.get("rows"):
                self._parse_program_tr(result["rows"])
                logger.debug(
                    "[Investor] 프로그램 차익=%+d 비차익=%+d",
                    self._program_arb, self._program_nonarb,
                )
            return True
        except Exception as e:
            logger.warning("[Investor] 프로그램 조회 오류: %s", e)
            return False

    # ── TR 파싱 ───────────────────────────────────────────────────
    def _parse_futures_tr(self, rows: list):
        """opt10059 파싱 — 행 순서: INVESTOR_KEYS와 동일."""
        for i, key in enumerate(INVESTOR_KEYS):
            if i < len(rows):
                try:
                    self._futures[key] = int(
                        rows[i].get("순매수", "0").replace(",", "").replace("+", "")
                    )
                except (ValueError, AttributeError):
                    pass

    def _parse_options_tr(self, rows: list):
        """opt50008 파싱 — 행 순서: INVESTOR_KEYS와 동일.
        필드명은 KOA Studio 확인 후 수정 필요. TR-DISCOVER 로그 참조.
        """
        _CALL_CANDIDATES = ["콜순매수", "콜순매수수량"]
        _PUT_CANDIDATES  = ["풋순매수", "풋순매수수량"]

        for i, key in enumerate(INVESTOR_KEYS):
            if i >= len(rows):
                break
            row = rows[i]
            for fname in _CALL_CANDIDATES:
                raw = row.get(fname, "")
                if raw:
                    try:
                        self._call[key] = int(raw.replace(",", "").replace("+", ""))
                    except ValueError:
                        pass
                    break
            for fname in _PUT_CANDIDATES:
                raw = row.get(fname, "")
                if raw:
                    try:
                        self._put[key] = int(raw.replace(",", "").replace("+", ""))
                    except ValueError:
                        pass
                    break

    def _parse_program_tr(self, rows: list):
        if rows:
            try:
                self._program_arb = int(
                    rows[0].get("차익순매수", "0").replace(",", "").replace("+", "")
                )
                self._program_nonarb = int(
                    rows[0].get("비차익순매수", "0").replace(",", "").replace("+", "")
                )
            except (ValueError, AttributeError):
                pass

    # ── 피처 계산 ─────────────────────────────────────────────────
    def get_features(self) -> Dict[str, float]:
        """수급 → 트레이딩 피처 변환 (파이프라인에서 캐시 읽기용)."""
        foreign_fut  = self._futures.get("foreign", 0)
        retail_fut   = self._futures.get("individual", 0)
        inst_fut     = self._futures.get("institution", 0)

        foreign_call = self._call.get("foreign", 0)
        foreign_put  = self._put.get("foreign", 0)
        retail_call  = self._call.get("individual", 0)
        retail_put   = self._put.get("individual", 0)

        fr_divergence = float(foreign_fut - retail_fut)

        return {
            "foreign_futures_net":       float(foreign_fut),
            "foreign_call_net":          float(foreign_call),
            "foreign_put_net":           float(foreign_put),
            "retail_futures_net":        float(retail_fut),
            "institution_futures_net":   float(inst_fut),
            "program_arb_net":           float(self._program_arb),
            "program_non_arb_net":       float(self._program_nonarb),
            "foreign_retail_divergence": fr_divergence,
        }

    def get_zone_data(self) -> Dict[str, Dict[str, int]]:
        """옵션 구간별 투자자 비율 (ATM = 현재 수집 데이터, ITM/OTM은 추후 구현).

        Returns:
            {"ITM": {"외인": pct, "개인": pct, "기관": pct},
             "ATM": {...},
             "OTM": {...}}
        """
        fi_abs   = abs(self._call.get("foreign", 0)) + abs(self._put.get("foreign", 0))
        rt_abs   = abs(self._call.get("individual", 0)) + abs(self._put.get("individual", 0))
        inst_abs = abs(self._call.get("institution", 0)) + abs(self._put.get("institution", 0))
        total    = max(fi_abs + rt_abs + inst_abs, 1)

        return {
            "ITM": {"외인": 0, "개인": 0, "기관": 0},
            "ATM": {
                "외인": round(fi_abs * 100 / total),
                "개인": round(rt_abs * 100 / total),
                "기관": round(inst_abs * 100 / total),
            },
            "OTM": {"외인": 0, "개인": 0, "기관": 0},
        }

    # ── 더미 (API 미연결 시) ──────────────────────────────────────
    def _fill_dummy_futures(self) -> bool:
        import random
        base = random.randint(-500, 500)
        self._futures["foreign"]     = base
        self._futures["individual"]  = -base + random.randint(-100, 100)
        self._futures["institution"] = random.randint(-200, 200)
        self._futures["pension"]     = random.randint(0, 100)
        return True

    def _fill_dummy_options(self) -> bool:
        import random
        self._call["foreign"]     = random.randint(-200, 200)
        self._put["foreign"]      = random.randint(-200, 200)
        self._call["individual"]  = random.randint(-300, 300)
        self._put["individual"]   = random.randint(-300, 300)
        self._call["institution"] = random.randint(-100, 100)
        self._put["institution"]  = random.randint(-100, 100)
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
            "fetch_count": self._fetch_count,
            "last_fetch":  self._last_fetch.strftime("%H:%M:%S") if self._last_fetch else "",
            "foreign_net": self._futures.get("foreign", 0),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    inv = InvestorData(kiwoom_api=None)
    inv.fetch_all()
    print(inv.get_features())
    print(inv.get_zone_data())
