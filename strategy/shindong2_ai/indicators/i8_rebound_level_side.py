# -*- coding: utf-8 -*-
"""I8 — 가장 가까운 반발형 P맥점(직전 7세션 극값 군집)이 현재가 3pt 안 아래면 +1(지지), 위면 −1(저항).

원천: 미니 1분봉 · `levels_p.p_levels_from` 의 kind='반발'. 3pt 밖이면 None(신호 없음 — 0 이 아니다).
⚠ 백필 H-P1 FAIL(첫 터치 되돌림률이 정수 레벨보다 낮다) — 「근접 방향」 지표로 별도 검증하는 후보다.
"""
from __future__ import annotations

import os
import sys
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for p in (ROOT, os.path.join(ROOT, "tools", "maekjeom_ladder")):
    if p not in sys.path:
        sys.path.insert(0, p)
NEAR_PT = 3.0

META = dict(id="I8", title="반발형 P맥점 근접 방향(지지 +1 / 저항 −1)",
            source="내부: regular_candles 직전 7세션 일중 고저 군집 — docs/미륵이고도화3/피터2/피터방법_사전등록_MW0601.json p_level",
            hypothesis="여러 날 튕겨 나간 극값 군집은 다시 반발한다 — 아래 지지 근접이면 상승, 위 저항 근접이면 하락",
            inputs=["regular_candles"], unit="방향(±1)", sign="follow",
            prereg=dict(min_days=20, hit_min=0.55, p_max=0.05))


def compute(day: str, upto_hm: Optional[str]) -> Optional[float]:
    import ladder_data as L
    from strategy.shindong2_ai import levels_p as P
    cs, _ = L.candles(day, L.is_live(day))
    bars = [b for b in cs if upto_hm is None or b[0] <= upto_hm]
    if not bars:
        return None
    cfg = P.prereg()
    lv = [x["price"] for x in P.p_levels_from(P.load_sessions(day, cfg["p_level"]["lookback_sessions"]), None, cfg)
          if x["kind"] == "반발"]
    if not lv:
        return None
    px = bars[-1][4]
    near = min(lv, key=lambda x: abs(x - px))
    if abs(near - px) > NEAR_PT:
        return None
    return 1.0 if near <= px else -1.0
