from __future__ import annotations

import datetime
from typing import Dict, Optional


class CybosInvestorData:
    def __init__(self, cybos_api=None):
        self._api = cybos_api
        self._last_fetch = None
        self._fetch_count = 0
        self._features = {
            "foreign_futures_net": 0.0,
            "foreign_call_net": 0.0,
            "foreign_put_net": 0.0,
            "retail_futures_net": 0.0,
            "institution_futures_net": 0.0,
            "program_arb_net": 0.0,
            "program_non_arb_net": 0.0,
            "foreign_retail_divergence": 0.0,
            "program_foreign_net_krw": 0.0,
            "program_institution_net_krw": 0.0,
            "program_individual_net_krw": 0.0,
        }

    def fetch_all(self) -> bool:
        self._last_fetch = datetime.datetime.now()
        self._fetch_count += 1
        return True

    def get_features(self) -> Dict[str, float]:
        return dict(self._features)

    def get_zone_data(self) -> Dict[str, Dict[str, int]]:
        return {
            "ITM": {"외인": 0, "개인": 0, "기관": 0},
            "ATM": {"외인": 0, "개인": 0, "기관": 0},
            "OTM": {"외인": 0, "개인": 0, "기관": 0},
        }

    def reset_daily(self) -> None:
        self._last_fetch = None
        self._fetch_count = 0

    def get_stats(self) -> dict:
        return {
            "fetch_count": self._fetch_count,
            "last_fetch": self._last_fetch.strftime("%H:%M:%S") if self._last_fetch else "",
            "foreign_net": 0,
            "prog_fi_krw": 0,
        }
