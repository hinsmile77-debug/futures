from __future__ import annotations

from typing import Optional

from config.settings import BROKER_BACKEND

from collection.broker.base import BrokerAPI
from collection.broker.cybos_broker import CybosBroker
from collection.broker.kiwoom_broker import KiwoomBroker


def create_broker(name: Optional[str] = None) -> BrokerAPI:
    backend = (name or BROKER_BACKEND or "cybos").strip().lower()
    if backend == "kiwoom":
        return KiwoomBroker()
    if backend == "cybos":
        return CybosBroker()
    raise ValueError(f"Unsupported broker backend: {backend}")
