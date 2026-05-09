from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class TickEvent:
    code: str
    price: float
    volume: int
    timestamp: Optional[datetime] = None
    open_interest: int = 0


@dataclass
class OrderBookEvent:
    code: str
    bid1: float
    ask1: float
    bid_qty: int
    ask_qty: int
    bid_prices: List[float] = field(default_factory=list)
    ask_prices: List[float] = field(default_factory=list)
    bid_qtys: List[int] = field(default_factory=list)
    ask_qtys: List[int] = field(default_factory=list)
    timestamp: Optional[datetime] = None


@dataclass
class OrderRequest:
    account_no: str
    code: str
    side: str
    qty: int
    order_type: str = "market"
    price: float = 0.0
    rqname: str = ""


@dataclass
class OrderAck:
    accepted: bool
    broker_order_no: str = ""
    message: str = ""
    raw: Optional[dict] = None


@dataclass
class FillEvent:
    code: str
    side: str
    filled_qty: int
    fill_price: float
    order_no: str = ""
    timestamp: Optional[datetime] = None
    raw: Optional[dict] = None


@dataclass
class PositionSnapshot:
    code: str
    side: str
    qty: int
    avg_price: float
    unrealized_pnl: float = 0.0


@dataclass
class BalanceSnapshot:
    account_no: str
    equity: float = 0.0
    available_cash: float = 0.0
    margin_used: float = 0.0
    raw: Optional[dict] = None
