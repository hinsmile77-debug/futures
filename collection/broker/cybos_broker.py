from __future__ import annotations

from typing import List, Optional

from collection.broker.base import BrokerAPI
from collection.cybos.api_connector import CybosAPI
from collection.cybos.investor_data import CybosInvestorData
from collection.cybos.realtime_data import CybosRealtimeData
from collection.kiwoom.latency_sync import LatencySync


class CybosBroker(BrokerAPI):
    name = "cybos"

    def __init__(self):
        self._api = CybosAPI()

    @property
    def api(self):
        return self._api

    @property
    def is_connected(self) -> bool:
        return bool(self._api.is_connected)

    def connect(self) -> bool:
        return self._api.connect()

    def get_login_info(self, tag: str) -> str:
        return self._api.get_login_info(tag)

    def get_account_list(self) -> List[str]:
        return self._api.get_account_list()

    def get_nearest_futures_code(self) -> str:
        return self._api.get_nearest_futures_code()

    def get_nearest_mini_futures_code(self) -> str:
        return self._api.get_nearest_mini_futures_code()

    def register_fill_callback(self, callback) -> None:
        self._api.register_fill_callback(callback)

    def register_msg_callback(self, callback) -> None:
        self._api.register_msg_callback(callback)

    def create_latency_sync(self):
        return LatencySync()

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
    ):
        return CybosRealtimeData(
            api=self._api,
            code=code,
            screen_no=screen_no,
            on_candle_closed=on_candle_closed,
            on_tick=on_tick,
            on_hoga=on_hoga,
            realtime_code=realtime_code,
            is_mock_server=is_mock_server,
        )

    def create_investor_data(self):
        return CybosInvestorData(cybos_api=self._api)

    def request_futures_balance(self, account_no: str) -> dict:
        return self._api.request_futures_balance(account_no)

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
        return self._api.send_market_order(
            account_no=account_no,
            code=code,
            side=side,
            qty=qty,
            rqname=rqname,
            screen_no=screen_no,
        )

    def probe_investor_ticker(self, extra_codes: Optional[List[str]] = None) -> None:
        self._api.probe_investor_ticker(extra_codes=extra_codes)
