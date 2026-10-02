# -*- coding: utf-8 -*-
"""[MW0601 654차] 호가 흐름 분해 — 잔량 감소분을 「체결 / 취소 하한 / 신규 하한」으로 나눈다.

왜 필요한가
-----------
`피터리_위로막힘_근거조사_MW0601-20261002.md` §7-3 — 두꺼운 매도벽이 사라진 뒤 가격이
오히려 올랐는데, 그 벽이 **체결로 소화**됐는지 **취소(스푸핑)** 로 사라졌는지 구분할
수단이 없었다. 근거: `docs/미륵이고도화3/호가깊이/주문취소율_수집가능성_조사_MW0601-20261002.md`.

🔴 **이것은 취소의 직접 관측이 아니라 추론이다.**
Cybos 는 주문 단위 메시지(MBO)를 주지 않는다 — 가격대별 집계 호가(MBP)뿐이다.
`cancel_ratio` 「구현불가 확정」(2026-07-14, `config/settings.py` 레지스트리)은 **시장 전체
취소 이벤트 원천이 없다**는 결정이고, 이 모듈은 그 결정을 번복하지 않는다. 같은 가격대의
두 스냅샷 사이 잔량 변화에서 체결을 빼서 **취소의 하한**을 얻을 뿐이다.

항등식 (같은 가격 p, 같은 쪽, 두 스냅샷 모두 p 를 관측할 수 있을 때)
------------------------------------------------------------------
    ΔQ(p) = 신규 − 취소 − 체결(p)
    net    = ΔQ + 체결(p) = 신규 − 취소
    취소 ≥ max(0, −net)   ← `cancel_qty_lb`
    신규 ≥ max(0,  net)   ← `add_qty_lb`
건수까지 있으면: 체결로 제거된 주문 수 ≤ 체결 계약수(주문 1건 ≥ 1계약) 이므로
    취소 건수 ≥ max(0, −ΔN − 체결(p))   ← `cancel_cnt_lb`

「관측 가능」의 정의 — 5단 창 이동 문제(조사 문서 §5-4)
-----------------------------------------------------
매도측 스냅샷의 마지막 유효 단 가격을 `last` 라 하면 **p ≤ last 인 가격은 잔량을 안다**
(창 안이면 표시값, 최우선보다 안쪽이면 0). p > last 는 창 밖이라 모른다. 매수측은 반대.
두 스냅샷 **모두에서** 관측 가능한 가격만 계산한다. 창 밖으로 밀려나 사라진 잔량을
취소로 세지 않기 위해서다. 그 가격에서 난 체결은 `exec_unmatched_qty` 로 남긴다
(계측 4원칙 ③ — 탈락을 숨기지 않는다).

남는 한계 (구현해도 해소되지 않는다)
------------------------------------
1. 스냅샷 사이 상계 — 들어왔다 나간 주문은 안 보인다(그래서 「하한」이다).
2. 정정 = 취소 + 신규로 보인다.
3. 호가·체결은 서로 다른 COM 객체라 이벤트 순서가 근사적이다.

순수 파이썬이다 — COM 을 모른다. `realtime_data.py` 가 콜백 안에서 **상태 저장만** 하는
규약(절대원칙 §4)을 지키도록 emit·dynamicCall 이 없다.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

# 가격 → 정수 키. 미니선물 틱 0.02, 부동소수 비교 오차를 피한다.
_PRICE_SCALE = 100

SIDES = ("ask", "bid")
FLOW_KEYS = ("cancel_qty_lb", "add_qty_lb", "exec_qty", "cancel_cnt_lb")


def _pkey(price):
    # type: (float) -> int
    return int(round(float(price) * _PRICE_SCALE))


def _levels(prices, qtys, cnts):
    # type: (Sequence[float], Sequence[int], Optional[Sequence[int]]) -> Optional[Dict]
    """유효 단(가격>0, 잔량>0)만 {pkey: (qty, cnt|None)} 로. 유효 단이 없으면 None."""
    out = {}
    for i, p in enumerate(prices):
        if p is None or p <= 0:
            continue
        q = qtys[i] if i < len(qtys) else 0
        if q is None or q <= 0:
            continue
        c = None
        if cnts is not None and i < len(cnts):
            c = cnts[i]
        out[_pkey(p)] = (int(q), None if c is None else int(c))
    return out or None


def counts_valid(qtys, cnts):
    # type: (Sequence[int], Optional[Sequence[int]]) -> bool
    """건수 배열이 믿을 만한가 — 유효 단마다 1 ≤ 건수 ≤ 잔량.

    원천이 건수를 0 으로 비워 보내면(필드 미지원·장 상태) 「건수 0」을 사실로 쓰면 안 된다
    (계측 4원칙 ② 미측정 ≠ 0). 한 단이라도 어긋나면 그 스냅샷의 건수 전체를 버린다.
    """
    if cnts is None:
        return False
    seen = False
    for i, q in enumerate(qtys):
        if q is None or q <= 0:
            continue
        if i >= len(cnts) or cnts[i] is None:
            return False
        c = cnts[i]
        if c < 1 or c > q:
            return False
        seen = True
    return seen


class BookSnapshot(object):
    """양변 5단 스냅샷. 건수는 유효할 때만 싣는다(아니면 None)."""

    __slots__ = ("ask", "bid", "has_cnt")

    def __init__(self, ask_prices, ask_qtys, bid_prices, bid_qtys,
                 ask_cnts=None, bid_cnts=None):
        self.has_cnt = counts_valid(ask_qtys, ask_cnts) and counts_valid(bid_qtys, bid_cnts)
        self.ask = _levels(ask_prices, ask_qtys, ask_cnts if self.has_cnt else None)
        self.bid = _levels(bid_prices, bid_qtys, bid_cnts if self.has_cnt else None)

    @property
    def valid(self):
        # type: () -> bool
        return bool(self.ask) and bool(self.bid)

    def mid_key(self):
        # type: () -> float
        return (min(self.ask) + max(self.bid)) / 2.0

    def observable(self, side, k):
        # type: (str, int) -> bool
        if side == "ask":
            return k <= max(self.ask)
        return k >= min(self.bid)

    def level(self, side, k):
        # type: (str, int) -> tuple
        book = self.ask if side == "ask" else self.bid
        return book.get(k, (0, 0 if self.has_cnt else None))


class BookFlowEstimator(object):
    """연속 스냅샷 쌍마다 흐름을 분해한다. 체결은 다음 스냅샷이 올 때까지 쌓아 둔다.

    사용:
        est.on_trade(price, qty, side)          # side: 'BUY' | 'SELL' | None
        inc = est.on_snapshot(BookSnapshot(...)) # 첫 스냅샷·무효 스냅샷이면 None
    """

    def __init__(self):
        self._prev = None            # type: Optional[BookSnapshot]
        self._pending = []           # type: List[tuple]   (pkey, qty, side)
        self.dropped_trade_qty = 0   # 쌍이 없어 귀속 못 하고 버린 체결량 (세션 누계)
        self.broken_chains = 0       # 무효 스냅샷으로 쌍이 끊긴 횟수 (세션 누계)

    def on_trade(self, price, qty, side=None):
        # type: (float, int, Optional[str]) -> None
        if qty is None or qty <= 0 or price is None or price <= 0:
            return
        self._pending.append((_pkey(price), int(qty), side))

    def reset(self):
        # type: () -> None
        """세션 리셋(재접속·월물 교체). 쌓인 체결은 버린 것으로 센다."""
        self.dropped_trade_qty += sum(q for _, q, _ in self._pending)
        self._pending = []
        self._prev = None

    def on_snapshot(self, snap):
        # type: (BookSnapshot) -> Optional[Dict]
        if not snap.valid:
            # 한쪽이 빈 스냅샷 — 쌍을 끊는다. 걸쳐 있던 체결은 귀속 불가로 버린다.
            if self._prev is not None:
                self.broken_chains += 1
            self.reset()
            return None
        prev = self._prev
        trades = self._pending
        self._prev = snap
        self._pending = []
        if prev is None:
            self.dropped_trade_qty += sum(q for _, q, _ in trades)
            return None
        return self._decompose(prev, snap, trades)

    @staticmethod
    def _decompose(prev, cur, trades):
        # type: (BookSnapshot, BookSnapshot, List[tuple]) -> Dict
        cnt_ok = prev.has_cnt and cur.has_cnt
        mid = prev.mid_key()
        ex = {"ask": {}, "bid": {}}           # type: Dict[str, Dict[int, int]]
        trade_qty = 0
        for k, q, side in trades:
            trade_qty += q
            if side == "BUY":
                s = "ask"                     # 공격적 매수는 매도 대기물량을 먹는다
            elif side == "SELL":
                s = "bid"
            else:
                s = "ask" if k >= mid else "bid"
            ex[s][k] = ex[s].get(k, 0) + q

        out = {"trade_qty": trade_qty, "exec_unmatched_qty": 0, "cnt_ok": cnt_ok}
        for s in SIDES:
            acc = dict.fromkeys(FLOW_KEYS, 0)
            keys = set(ex[s])
            keys.update(prev.ask if s == "ask" else prev.bid)
            keys.update(cur.ask if s == "ask" else cur.bid)
            for k in keys:
                e = ex[s].get(k, 0)
                if not (prev.observable(s, k) and cur.observable(s, k)):
                    out["exec_unmatched_qty"] += e
                    continue
                qp, np_ = prev.level(s, k)
                qc, nc = cur.level(s, k)
                if qp == 0 and qc == 0:
                    # 양 스냅샷 모두 이 쪽에 잔량이 없는데 체결이 났다 — 순서 근사의 잔차.
                    out["exec_unmatched_qty"] += e
                    continue
                net = (qc - qp) + e
                if net < 0:
                    acc["cancel_qty_lb"] += -net
                else:
                    acc["add_qty_lb"] += net
                acc["exec_qty"] += e
                if cnt_ok:
                    acc["cancel_cnt_lb"] += max(0, (np_ - nc) - e)
            for key in FLOW_KEYS:
                out["%s_%s" % (s, key)] = acc[key]
        return out
