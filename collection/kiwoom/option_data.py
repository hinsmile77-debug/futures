# collection/kiwoom/option_data.py — 옵션 데이터 수집
"""
KOSPI 200 옵션 데이터 수집 및 옵션 피처 계산

수집 항목:
  - ATM/ITM/OTM 콜·풋 미결제약정 및 거래량
  - P/C Ratio (Put-Call Ratio)
  - 기준가 대비 베이시스
  - 위클리 만기 잔여일 가중치
  - 감마 노출도 (GEX 근사)

수집 방법:
  opt50004 — 옵션 현재가 (TR)
  실시간 FID 조회 (OI, 이론가)

Python 3.7 32-bit 호환
"""
import logging
import datetime
import math
from typing import Optional, Dict, List, TYPE_CHECKING

from config.constants import FID_OI

if TYPE_CHECKING:
    from collection.kiwoom.api_connector import KiwoomAPI

logger = logging.getLogger("DATA")

# 옵션 ATM 기준 범위 (±n 스트라이크)
ATM_RANGE  = 2
OTM_RANGE  = 5
ITM_RANGE  = 2

# 위클리 만기 요일 (목요일=3)
WEEKLY_EXPIRY_DOW = 3


class OptionData:
    """
    KOSPI 200 옵션 데이터 수집 및 파생 피처 계산

    사용:
        opt = OptionData(kiwoom_api)
        opt.fetch(futures_price=380.0)
        feats = opt.get_features()
    """

    def __init__(self, kiwoom_api=None):
        self._api = kiwoom_api

        # 옵션 데이터 저장소
        # {strike: {"call_oi": int, "put_oi": int, "call_vol": int, "put_vol": int}}
        self._strikes: Dict[float, dict] = {}
        self._futures_price: float = 0.0
        self._basis:         float = 0.0

        self._last_fetch: Optional[datetime.datetime] = None

    # ── 데이터 수집 ───────────────────────────────────────────────
    def fetch(self, futures_price: float) -> bool:
        """
        현재 선물 가격 기준으로 옵션 데이터 수집

        Args:
            futures_price: 현재 선물 지수 (ATM 계산 기준)
        """
        self._futures_price = futures_price

        if self._api is None:
            return self._fill_dummy(futures_price)

        try:
            # ATM 스트라이크 계산 (2.5pt 단위 반올림)
            atm_strike = round(futures_price / 2.5) * 2.5
            strikes    = [atm_strike + i * 2.5 for i in range(-OTM_RANGE, OTM_RANGE + 1)]

            for strike in strikes:
                self._fetch_strike(strike)

            self._last_fetch = datetime.datetime.now()
            return True
        except Exception as e:
            logger.warning(f"[Option] 수집 오류: {e}")
            return False

    def _fetch_strike(self, strike: float):
        """개별 스트라이크 데이터 조회"""
        try:
            call_code = self._get_option_code("C", strike)
            put_code  = self._get_option_code("P", strike)

            call_oi  = self._api.get_comm_real_data(call_code, FID_OI)
            put_oi   = self._api.get_comm_real_data(put_code,  FID_OI)

            self._strikes[strike] = {
                "call_oi":  int(call_oi)  if call_oi  else 0,
                "put_oi":   int(put_oi)   if put_oi   else 0,
                "call_vol": 0,
                "put_vol":  0,
            }
        except Exception:
            pass

    @staticmethod
    def _get_option_code(cp: str, strike: float) -> str:
        """옵션 종목코드 생성 (근사 — 실제는 만기월 포함)"""
        strike_str = f"{int(strike * 100):05d}"
        return f"2{cp}{strike_str}000"

    # ── 더미 데이터 ───────────────────────────────────────────────
    def _fill_dummy(self, futures_price: float) -> bool:
        import random
        atm = round(futures_price / 2.5) * 2.5
        for i in range(-OTM_RANGE, OTM_RANGE + 1):
            strike = atm + i * 2.5
            # ATM 근처 OI 높음, OTM으로 갈수록 낮아짐
            base = max(100, 1000 - abs(i) * 150)
            self._strikes[strike] = {
                "call_oi":  base + random.randint(-50, 50),
                "put_oi":   base + random.randint(-50, 50),
                "call_vol": base // 10 + random.randint(0, 20),
                "put_vol":  base // 10 + random.randint(0, 20),
            }
        self._basis        = random.uniform(-0.5, 0.5)
        self._last_fetch   = datetime.datetime.now()
        return True

    # ── 피처 계산 ─────────────────────────────────────────────────
    def get_features(self) -> Dict[str, float]:
        """
        옵션 데이터 → 트레이딩 피처 계산

        Returns:
            constants.py OPTION_FEATURES 형식의 딕셔너리
        """
        if not self._strikes:
            return self._empty_features()

        price = self._futures_price
        atm   = round(price / 2.5) * 2.5

        # ── ATM / ITM / OTM 분류 ─────────────────────────────────
        atm_strikes = [atm + i * 2.5 for i in range(-ATM_RANGE, ATM_RANGE + 1)]
        itm_call_strikes = [atm + i * 2.5 for i in range(-ITM_RANGE, 0)]  # 콜 ITM
        itm_put_strikes  = [atm + i * 2.5 for i in range(1, ITM_RANGE + 1)]  # 풋 ITM
        otm_call_strikes = [atm + i * 2.5 for i in range(1, OTM_RANGE + 1)]
        otm_put_strikes  = [atm + i * 2.5 for i in range(-OTM_RANGE, 0)]

        def sum_oi(strikes, side):
            return sum(self._strikes.get(s, {}).get(side, 0) for s in strikes)

        atm_call_oi  = sum_oi(atm_strikes, "call_oi")
        atm_put_oi   = sum_oi(atm_strikes, "put_oi")
        itm_call_oi  = sum_oi(itm_call_strikes, "call_oi")
        itm_put_oi   = sum_oi(itm_put_strikes,  "put_oi")
        otm_call_oi  = sum_oi(otm_call_strikes, "call_oi")
        otm_put_oi   = sum_oi(otm_put_strikes,  "put_oi")

        total_call_oi = sum(v.get("call_oi", 0) for v in self._strikes.values())
        total_put_oi  = sum(v.get("put_oi",  0) for v in self._strikes.values())

        # P/C Ratio
        pcr = total_put_oi / max(total_call_oi, 1)

        # OI 변화 (근사 — 전회 대비)
        oi_change = float(total_call_oi + total_put_oi)

        # 감마 노출도 근사 (ATM 옵션 OI 합계)
        gex = float(atm_call_oi - atm_put_oi)

        # 위클리 만기 가중치
        expiry_weight = self._calc_expiry_weight()

        # 소매 역발상 (OTM 콜 OI 높으면 → 역발상 하락 신호)
        retail_contrarian = float(otm_call_oi - otm_put_oi) / max(otm_call_oi + otm_put_oi, 1)

        return {
            "itm_foreign_call":      float(itm_call_oi),
            "itm_foreign_put":       float(itm_put_oi),
            "atm_foreign_call":      float(atm_call_oi),
            "atm_foreign_put":       float(atm_put_oi),
            "otm_foreign_call":      float(otm_call_oi),
            "otm_foreign_put":       float(otm_put_oi),
            "retail_otm_contrarian": retail_contrarian,
            "pcr":                   round(pcr, 4),
            "basis":                 round(self._basis, 4),
            "weekly_expiry_weight":  round(expiry_weight, 4),
            "gamma_exposure":        round(gex / max(total_call_oi + total_put_oi, 1), 4),
            "open_interest_change":  round(oi_change, 0),
        }

    def _calc_expiry_weight(self) -> float:
        """위클리 만기까지 잔여일 기반 가중치 (만기일 가까울수록 1.0에 가까워짐)"""
        today   = datetime.date.today()
        dow     = today.weekday()  # 0=월 ~ 6=일
        days_to = (WEEKLY_EXPIRY_DOW - dow) % 7
        if days_to == 0:
            days_to = 7   # 이번 주 목요일은 다음 주로
        weight  = 1.0 - days_to / 7.0
        return round(weight, 3)

    @staticmethod
    def _empty_features() -> Dict[str, float]:
        return {
            "itm_foreign_call": 0.0, "itm_foreign_put": 0.0,
            "atm_foreign_call": 0.0, "atm_foreign_put": 0.0,
            "otm_foreign_call": 0.0, "otm_foreign_put": 0.0,
            "retail_otm_contrarian": 0.0, "pcr": 1.0,
            "basis": 0.0, "weekly_expiry_weight": 0.5,
            "gamma_exposure": 0.0, "open_interest_change": 0.0,
        }

    def reset_daily(self):
        self._strikes.clear()
        self._basis = 0.0

    def get_stats(self) -> dict:
        return {
            "strike_count": len(self._strikes),
            "last_fetch":   self._last_fetch.strftime("%H:%M:%S") if self._last_fetch else "",
            "futures_price": self._futures_price,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    opt = OptionData(kiwoom_api=None)
    opt.fetch(futures_price=380.0)
    feats = opt.get_features()
    for k, v in feats.items():
        print(f"  {k:<30} {v}")
