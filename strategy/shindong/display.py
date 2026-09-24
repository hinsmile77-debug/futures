# -*- coding: utf-8 -*-
"""[MW0602 590차] 신동 가상거래 → 화면용 행 변환 — 순수 함수. Qt·DB 를 모른다.

두 소비자
---------
· 1분봉 차트 신동 레이어  : `chart_rows()`  — 진입 1개 + 청산 다리(1차·최종) 최대 2개
· 손익 추이 패널 「신동」 : `pnl_rows()`    — 거래 1건 = 1행, 순손익을 **크레온 요율**로 재환산

🔴 요율 재환산은 **표시 계층에서만** 한다.
  `shindong.db` 의 `leg*_net` 은 사전등록 규격(`spec.COMMISSION_RATE` = CYBOS 편도)으로
  계산된 값이고, 그 규격은 결과를 보고 바꾸지 않는다(`spec.py` 머리말 — 검증 시계).
  MW0602 는 CREON 채널(0.0019%)이라 화면에서는 사용자 지시(2026-09-24)대로 CREON 으로 본다.
  그래서 DB 를 고치지 않고, 다리마다 수수료 차이만 되돌려 더한다:

      net_creon = net_spec + (진입가 + 청산가) × 승수 × (요율_spec − 요율_creon)

  `engine.leg_net` 의 수수료 항이 정확히 `(e + x) × 승수 × 요율` 이므로 이 보정은
  원 단위까지 정확하다. 슬리피지 항은 요율과 무관해 그대로 남는다.
"""
from typing import Any, Dict, List, Optional

from strategy.shindong import spec as S


def creon_rate() -> float:
    """CREON 편도 요율. 🔴 채널 **감지값이 아니라 CREON 고정**이다(사용자 지시)."""
    from config.constants import BROKER_CHANNEL_SPECS
    return float(BROKER_CHANNEL_SPECS["CREON"]["one_way_commission_rate"])


def leg_net_at_rate(net_spec: Optional[float], entry_px: float, exit_px: float,
                    rate: float) -> Optional[float]:
    """규격 요율로 계산된 다리 순손익을 `rate` 로 재환산. 미청산(None)은 None 그대로."""
    if net_spec is None:
        return None
    return (float(net_spec)
            + (float(entry_px) + float(exit_px)) * S.PT_VALUE_KRW
            * (S.COMMISSION_RATE - float(rate)))


def _legs(t: Dict[str, Any]):
    for i in (1, 2):
        ts = t.get("leg%d_exit_ts" % i)
        px = t.get("leg%d_exit_px" % i)
        if ts and px is not None:
            yield i, ts, float(px), t.get("leg%d_pts" % i), t.get("leg%d_net" % i), \
                t.get("leg%d_reason" % i)


def chart_rows(trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """`store.load_trades()` 행 → 차트 마커 행.

    반환 행: entry_ts · entry_price · direction_txt(LONG/SHORT) · rule · status ·
             exits=[{leg, ts, price, pts, reason}] (닫힌 다리만, 시각순)
    `status == "OPEN"` 이고 닫힌 다리가 둘 다 없지 않으면 「보유 중」이 남아 있는 것이다.
    """
    out = []
    for t in trades or []:
        if str(t.get("status")) == "RETRACTED":
            continue
        if not t.get("entry_ts") or t.get("entry_px") is None:
            continue
        exits = [{"leg": i, "ts": ts, "price": px,
                  "pts": (float(pts) if pts is not None else None), "reason": rs}
                 for i, ts, px, pts, _n, rs in _legs(t)]
        out.append({
            "entry_ts": t["entry_ts"],
            "entry_price": float(t["entry_px"]),
            "direction_txt": "LONG" if int(t.get("side") or 0) > 0 else "SHORT",
            "rule": t.get("rule") or "",
            "status": t.get("status") or "",
            "exits": exits,
            "open": len(exits) < S.LEGS,
        })
    return out


def pnl_rows(trades: List[Dict[str, Any]], rate: Optional[float] = None) -> List[Dict[str, Any]]:
    """`store.load_closed_for_pnl()` 행(청산 완료) → 손익 패널 행.

    패널의 미륵 행과 **같은 키**를 쓴다(`entry_ts`·`pnl_pts`·`pnl_krw`·`quantity` …).
    · `entry_ts` 는 **마지막 다리 청산 시각** — 미륵 행이 `exit_ts` 로 날짜를 잡는 것과 같다.
    · `pnl_pts` 는 두 다리 pt 합(다리 = 1계약), `quantity=1` 로 두어 패널의
      `pts × quantity` 가 그대로 합이 되게 한다.
    · `pnl_krw` 는 CREON 요율 재환산 순손익(2계약 합).
    """
    r = creon_rate() if rate is None else float(rate)
    out = []
    for t in trades or []:
        if str(t.get("status")) != "CLOSED":
            continue
        legs = list(_legs(t))
        if not legs:
            continue
        pts = sum(float(p or 0.0) for _i, _ts, _px, p, _n, _rs in legs)
        krw = sum(leg_net_at_rate(n, t["entry_px"], px, r) or 0.0
                  for _i, _ts, px, _p, n, _rs in legs)
        last_ts = max(ts for _i, ts, _px, _p, _n, _rs in legs)
        out.append({
            "entry_ts": str(last_ts),
            "pnl_pts": round(pts, 4),
            "pnl_krw": round(krw, 0),
            "forward_pnl_pts": round(pts, 4),
            "forward_pnl_krw": round(krw, 0),
            "quantity": 1,
            "reverse_entry_enabled": 0,
            "rule": t.get("rule") or "",
        })
    return out
