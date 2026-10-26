# -*- coding: utf-8 -*-
"""I7 — 「피터의 방법」 09:10 시가범위 상자(B2) 안 위치 − 0.5. 상단 근처(+)면 이후 하락(되돌림) 가설.

원천: 1분봉(미니 근월물 — 사다리 `ladder_data.candles`) · P층 앵커(`levels_p`, 직전 7세션 극값 군집·체류) ·
      먼스리 벽(option_book, 있는 날만). 정의 = `docs/미륵이고도화3/피터2/피터방법_사전등록_MW0601.json` box(B2).
⚠ 백필 H-B1 FAIL(상자 유지율이 같은 폭 대조군보다 낮다) — 이 지표는 그 위에서 **위치 신호**만 따로 검증하는 후보다.
"""
from __future__ import annotations

import os
import sys
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for p in (ROOT, os.path.join(ROOT, "tools", "maekjeom_ladder"), os.path.join(ROOT, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)
T_BOX = "09:10"

META = dict(id="I7", title="피터 상자(B2@09:10) 안 위치",
            source="내부: 1분봉 OR + P층 앵커 — docs/미륵이고도화3/피터2/피터_870-850_장초판단근거_딥다이브_MW0601-20261026.md",
            hypothesis="상자 상단(+)에서는 되돌림 하락, 하단(−)에서는 반등 — 피터 「870 아래서 풋」 류. 이탈(|값|>0.5)도 같은 부호로 본다",
            inputs=["regular_candles", "option_book"], unit="상자폭 비율", sign="contra",
            prereg=dict(min_days=20, hit_min=0.55, p_max=0.05))


def _bars(day, upto_hm):
    import ladder_data as L
    cs, _ = L.candles(day, L.is_live(day))
    return [b for b in cs if upto_hm is None or b[0] <= upto_hm]


def compute(day: str, upto_hm: Optional[str]) -> Optional[float]:
    from strategy.shindong2_ai import levels_p as P, box as B
    if upto_hm is not None and upto_hm < T_BOX:
        return None
    bars = _bars(day, upto_hm)
    if not bars:
        return None
    cfg = P.prereg()
    import peter_method_backfill as PB
    lv = P.p_levels_from(P.load_sessions(day, cfg["p_level"]["lookback_sessions"]), PB.load_walls(day), cfg)
    bx = B.make_boxes(bars, T_BOX, P.anchors(lv), cfg)
    if not bx:
        return None
    pos = B.box_position(bars[-1][4], bx["B2"])
    return None if pos is None else round(pos - 0.5, 3)
