# -*- coding: utf-8 -*-
"""[MW0602 640차 ④] 지표 플러그인 로더 — 이 폴더의 `i*.py` 를 찾아 계약을 검사하고 돌려준다.

플러그인 계약
    META = dict(id="I1", title="…", source="URL 또는 '내부: …'", hypothesis="+ 면 이후 상승(순추종) …",
                inputs=["raw_investor_futures"], unit="계약", sign="follow|contra",
                prereg=dict(min_days=20, hit_min=0.55, p_max=0.05))
    def compute(day: str, upto_hm: str | None) -> float | None     # upto_hm 이하 데이터만. 미측정 None.

새 지표를 붙일 때 snapshot·검증 러너 본문은 고치지 않는다 — 파일을 하나 놓으면 `discover()` 가 찾는다.
"""
from __future__ import annotations

import importlib
import os
import pkgutil
from typing import Any, Dict, Optional

REQUIRED_META = ("id", "title", "source", "hypothesis", "inputs", "sign", "prereg")
SIGNS = ("follow", "contra")          # follow: 값 > 0 → 이후 상승 가설 · contra: 값 > 0 → 이후 하락 가설


def discover() -> Dict[str, Any]:
    """{id: module}. 계약을 어긴 파일은 `errors` 키 아래 사유와 함께 남긴다(조용히 버리지 않는다 — 계측 4원칙 ③)."""
    out: Dict[str, Any] = {}
    errors: Dict[str, str] = {}
    pkg = os.path.dirname(os.path.abspath(__file__))
    for m in pkgutil.iter_modules([pkg]):
        if not m.name.startswith("i"):
            continue
        try:
            mod = importlib.import_module("%s.%s" % (__name__, m.name))
            meta = getattr(mod, "META", None)
            if not isinstance(meta, dict) or any(k not in meta for k in REQUIRED_META):
                errors[m.name] = "META 누락 — 필요 %s" % (REQUIRED_META,)
                continue
            if meta["sign"] not in SIGNS or not callable(getattr(mod, "compute", None)):
                errors[m.name] = "sign 은 %s · compute(day, upto_hm) 필요" % (SIGNS,)
                continue
            if meta["id"] in out:
                errors[m.name] = "id 중복 %s" % meta["id"]
                continue
            out[meta["id"]] = mod
        except Exception as e:                      # 한 플러그인의 import 오류가 전체를 죽이지 않게
            errors[m.name] = "import 실패: %s" % e
    out["__errors__"] = errors                       # 호출자가 반드시 본다
    return out


def compute_one(mod, day: str, upto_hm: Optional[str]) -> Dict[str, Any]:
    """값 + 가설 방향. 예외는 미측정으로 바꾸고 사유를 남긴다."""
    meta = mod.META
    try:
        v = mod.compute(day, upto_hm)
    except Exception as e:
        return dict(id=meta["id"], value=None, why="계산 실패: %s" % str(e)[:120], lean=None)
    lean = None
    if v is not None and v != 0:
        up = (v > 0) if meta["sign"] == "follow" else (v < 0)
        lean = "매수" if up else "매도"
    return dict(id=meta["id"], value=v, lean=lean, why=None if v is not None else "미측정(원천 없음)")
