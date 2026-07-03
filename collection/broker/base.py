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
