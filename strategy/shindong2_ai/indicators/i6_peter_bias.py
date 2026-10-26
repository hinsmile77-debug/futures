# -*- coding: utf-8 -*-
"""I6 — 피터의 그날 최신 관점 편향(풋·매도 −1 / 콜·매수 +1). 수신 시각(seen_at)이 upto 이하인 것만.

원천: `data/peter_feed/_raw/<날짜>.jsonl`(피터2 실시간 수집) → `strategy/peter2/view.py` parse_view 의 bias.
매매 지시 트윗은 PETER 실거래가 따로 다루므로 여기서는 **관점** 트윗만 본다. 관점이 없으면 None(신호 없음).
"""
from __future__ import annotations

import os
import sys
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for p in (ROOT, os.path.join(ROOT, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

META = dict(id="I6", title="피터 최신 관점 편향",
            source="내부: data/peter_feed/_raw (피터리 트윗 실시간 수집) — 10-26 「870 아래서 풋만」",
            hypothesis="피터가 장중에 밝힌 방향 편향은 이후 방향을 맞힌다(10-13 매수 단타만 ✗ · 09-30 1105 밑 풋 보합 — 표본 극소)",
            inputs=["peter_feed"], unit="방향(±1)", sign="follow",
            prereg=dict(min_days=20, hit_min=0.55, p_max=0.05))


def compute(day: str, upto_hm: Optional[str]) -> Optional[float]:
    import shindong2_pmethod as PM
    views, have = PM.peter_views(day, upto_hm)
    if not have:
        return None
    b = [v for v in views if v.get("bias") and v["kind"] not in ("recap", "trade")]
    if not b:
        return None
    return -1.0 if b[-1]["bias"] == "short" else 1.0
