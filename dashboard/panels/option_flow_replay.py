# -*- coding: utf-8 -*-
"""[MW0601 627차] 옵션·선물 수급 차트 복기 적재 — **배경 스레드에서만** 부른다.

🔴 수급 차트 위젯(`option_flow_delta_chart.py`)은 매매 파이프라인과 같은 메인(Qt)
  스레드에서 그리므로 DB 에 직접 접근하지 않는다(test_612c::test_15). 과거 날짜는
  차트가 스레드를 띄워 이 모듈을 부르고, 결과를 시그널(QueuedConnection)로 받는다
  — 1분봉 차트 날짜선택 A단계와 같은 관례다.
  실측(2026-09-24): 하루치 옵션 약 21ms · 선물 약 30ms.

`collection.cybos` 는 패키지 import 가 Cybos COM 모듈까지 끌어오므로 **함수 안에서** 늦게 부른다.
"""
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("SYSTEM")


def _flow_db_path() -> str:
    from config import settings as _st
    p = getattr(_st, "WEEKLY_OPTION_FLOW_DB", "data/db/option_flow.db")
    return p if os.path.isabs(p) else os.path.join(_st.BASE_DIR, p)


def load_replay_payloads(date: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """(옵션 payload, 선물 payload) — 라이브 push 와 **같은 함수·같은 모양**이다."""
    from config import settings as _st
    from collection.cybos.futures_flow_series import get_futures_session_delta
    empty = {"trade_date": date, "last_time": None, "products": {}}
    fdb = _flow_db_path()
    if os.path.exists(fdb):
        from collection.cybos.weekly_option_flow import WeeklyOptionFlow
        opt = WeeklyOptionFlow(fdb).get_individual_session_delta(date)
    else:
        opt = dict(empty)        # 원천 없음 — 0 이 아니라 빈 products 로 둔다
    fut = get_futures_session_delta(date, raw_db_path=_st.RAW_DATA_DB)
    return opt, fut


def load_replay_dates() -> Tuple[List[str], Optional[str]]:
    """(옵션 흐름이 있는 날짜들, 선물 수급 첫 날짜). 못 읽으면 ([], None)."""
    import sqlite3
    from config import settings as _st
    dates, first = [], None
    try:
        fdb = _flow_db_path()
        if os.path.exists(fdb):
            con = sqlite3.connect("file:%s?mode=ro" % fdb.replace("\\", "/"), uri=True,
                                  timeout=3.0)
            try:
                dates = [r[0] for r in con.execute(
                    "SELECT DISTINCT trade_date FROM option_investor_flow ORDER BY 1")]
            finally:
                con.close()
        con = sqlite3.connect("file:%s?mode=ro" % _st.RAW_DATA_DB.replace("\\", "/"),
                              uri=True, timeout=3.0)
        try:
            r = con.execute("SELECT min(ts) FROM raw_investor_futures").fetchone()
            first = str(r[0])[:10] if r and r[0] else None
        finally:
            con.close()
    except Exception as exc:                                    # noqa: BLE001
        logger.warning("[OptionFlowChart] 복기 날짜 조회 실패: %s", exc)
    return dates, first
