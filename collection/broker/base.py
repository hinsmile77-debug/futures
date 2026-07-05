from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class BrokerAPI(ABC):
    """Broker-neutral runtime surface used by the trading system."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def api(self) -> Any:
        ...

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        ...

    @abstractmethod
    def connect(self) -> bool:
        ...

    @abstractmethod
    def get_login_info(self, tag: str) -> str:
        ...

    @abstractmethod
    def get_account_list(self) -> List[str]:
        ...

    @abstractmethod
    def get_nearest_futures_code(self) -> str:
        ...

    def get_nearest_mini_futures_code(self) -> str:
        """근월물 프로브 미지원 브로커는 빈 문자열 — 호출부가 UI/CpFutureCode fallback 처리."""
        return ""

    def get_nearest_normal_futures_code(self) -> str:
        """근월물 프로브 미지원 브로커는 빈 문자열 — 호출부가 UI/CpFutureCode fallback 처리."""
        return ""

    @abstractmethod
    def register_fill_callback(self, callback) -> None:
        ...

    @abstractmethod
    def register_msg_callback(self, callback) -> None:
        ...

    @abstractmethod
    def create_latency_sync(self) -> Any:
        ...

    @abstractmethod
    def create_realtime_data(
        self,
        *,
        code: str,
        screen_no: str,
        on_candle_closed,
        on_tick,
        on_hoga,
        realtime_code: Optional[str] = None,
        is_mock_server: bool = False,
    ) -> Any:
        ...

    @abstractmethod
    def create_investor_data(self) -> Any:
        ...

    @abstractmethod
    def request_futures_balance(self, account_no: str) -> dict:
        ...

    @abstractmethod
    def send_market_order(
        self,
        *,
        account_no: str,
        code: str,
        side: str,
        qty: int,
        rqname: str,
        screen_no: str,
    ) -> int:
        ...

    @abstractmethod
    def probe_investor_ticker(self, extra_codes: Optional[List[str]] = None) -> None:
        ...

    def get_last_order_error(self) -> Optional[dict]:
        """가장 최근 실패한 주문의 상세(ret/status/msg). 브로커가 미지원이면 None."""
        return None

    def send_limit_order(
        self,
        *,
        account_no: str,
        code: str,
        side: str,
        qty: int,
        price: float,
        rqname: str,
        screen_no: str,
    ) -> dict:
        """[260704 감사 P1] 지정가 신규주문. 브로커가 미지원이면 실패 반환(ret=-1).

        Returns: {"ret": int, "order_no": str}
        """
        return {"ret": -1, "order_no": ""}

    def cancel_order(
        self,
        *,
        account_no: str,
        order_no: str,
        code: str,
        qty: int,
    ) -> int:
        """[260704 감사 P1] 미체결 주문 취소. 브로커가 미지원이면 -1 반환."""
        return -1

    def get_index_price(self, code: str = "", name_contains: str = "200") -> Optional[float]:
        """[260704 감사 P2] 지수 현재가 조회 (베이시스/VKOSPI 계산용).

        code 생략 시 브로커 기본 지수(Cybos: KOSPI200)를 사용. 미지원 브로커는 None.
        """
        return None

    def get_order_available_qty(self, account_no: str, code: str, price: float) -> Optional[dict]:
        """증거금 반영 신규주문가능수량 {sell_new_qty, buy_new_qty}. 브로커가 미지원이면 None."""
        return None
