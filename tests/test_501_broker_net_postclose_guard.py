# -*- coding: utf-8 -*-
"""[MW0602 501차] 브로커 net 수집 결함 3종 회귀 고정.

2026-08-30 조사에서 `daily_broker_pnl.broker_net_krw`(전환기준 ① 판정 원천)에
독립된 결함 3개가 겹쳐 있는 것이 확인됐다. 각각 다른 지점이라 테스트도 3개다.

**D1 — 파서가 롤오버(장후 정산) 판독을 채택한다.**
`CpTd6197` 두 필드는 정산 전후로 의미가 바뀐다:

    장중     예탁현금 = 당일 시가(고정) · 익일가 = 시가 + gross − 수수료
             → `익일가 − 예탁` = 그날 net              ✅
    장후정산 예탁현금 = (시가 + gross)로 롤오버 · 익일가 = 거기서 수수료만 차감
             → `익일가 − 예탁` = −수수료               ❌

`_scan_lines`가 마지막 줄을 무조건 쓰는 바람에 거래일 저녁에 세션이 살아 있던
4일(2026-06-30 · 07-01 · 07-14 · 08-06)의 net이 −수수료로 기록됐다. 08-06은
−360,142가 −43,142로 남아 8월 손실 6위가 순위에서 사라졌다.

**D2 — 라이브 저장부에 같은 가드가 없다.** `main.py`의 잔고 push는 FLAT이기만
하면 `upsert_broker_net`을 부른다. 거래일 저녁에 프로세스가 살아 있으면 그날
실측이 수수료로 덮어써진다(D1과 같은 사고를 라이브에서 재현한다).

**D3 — `is_krx_trading_date`가 음성을 영구 캐시한다.** 이 함수의 첫 호출은
장전 **08:41 잔고 push**이고 그 시점엔 당일 `predictions` 첫 행(09:00)이 아직
없다. 그래서 `False`가 세션 내내 굳어, 493차 F-2가 배선한 `upsert_broker_net`이
**2026-08-25 이후 한 번도 성공하지 못했다**(0827 로그 실측: `SKIP_NON_TRADING`
35건 전부). `pnl_krw`만 멀쩡했던 건 그쪽은 `_yesterday` 경로로 **다음 날**
저장돼 그때는 새 프로세스라 캐시가 비어 있었기 때문이다.

판별 규칙은 **「예탁현금은 당일 시가 고정」 불변식**이다 — 그날 첫 판독과
달라지면 롤오버. 전 로그(49거래일 · 2,164줄) 검증에서 오탐 0 · 미탐 0.
⚠ 「실현손익 0 && 예탁≠익일가」로는 안 된다 — 미실현이 익일가를 움직이는 장중
초반 줄이 걸려 33일이 오탐된다(설계 중 실제로 밟은 실패다. 아래 D1-c가 고정).
"""
import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── D1. 파서 ────────────────────────────────────────────────────────────────
def _line(ts, dep, nxt, gross):
    return ("%s [INFO] SYSTEM: [CybosDailyPnl] account=X summary="
            "{'총매매': %d, '총평가수익률': %d, '실현손익': %d}\n"
            % (ts, dep, nxt, gross))


def _scan():
    from scripts.commission_rate_recon import _scan_lines
    return _scan_lines


def test_d1a_rollover_line_is_not_adopted():
    """2026-08-06 실측 재현 — 20:06 롤오버 줄이 14:48 장중 확정치를 덮으면 안 된다."""
    lines = [
        _line("2026-08-06 08:41:07", 30180776, 30180776, 0),
        _line("2026-08-06 14:48:25", 30180776, 29820634, -317000),
        _line("2026-08-06 20:06:51", 29820658, 29777516, 0),   # 롤오버
    ]
    gross, dep, nxt = _scan()(lines)
    assert (dep, nxt) == (30180776, 29820634), "장중 마지막 판독을 써야 한다"
    assert nxt - dep == pytest.approx(-360142), "그날 net은 -360,142다(-43,142가 아니다)"
    assert gross == -317000


def test_d1b_normal_day_still_uses_last_line():
    """정상일은 동작이 바뀌면 안 된다 — 예탁현금이 고정이면 마지막 줄 그대로."""
    lines = [
        _line("2026-08-05 08:41:06", 30630362, 30630362, 0),
        _line("2026-08-05 11:19:36", 30630362, 30239563, -377000),
        _line("2026-08-05 14:50:51", 30630362, 30180760, -416000),
    ]
    gross, dep, nxt = _scan()(lines)
    assert (gross, dep, nxt) == (-416000, 30630362, 30180760)
    assert nxt - dep == pytest.approx(-449602)


def test_d1c_unrealized_early_line_is_not_mistaken_for_rollover():
    """오탐 방지 — 실현 0인데 익일가가 움직인 장중 초반 줄은 롤오버가 아니다.

    미실현 손익이 익일가예탁현금에 반영되면 이 조합이 나온다. 이걸 롤오버로
    보는 규칙(실현0 && 예탁≠익일가)은 실측 33일을 오탐했다.
    """
    lines = [
        _line("2026-08-06 08:41:07", 30180776, 30180776, 0),
        _line("2026-08-06 09:41:49", 30180776, 30174821, 0),   # 미실현 −5,955
        _line("2026-08-06 14:48:25", 30180776, 29820634, -317000),
    ]
    gross, dep, nxt = _scan()(lines)
    assert (dep, nxt) == (30180776, 29820634)


def test_d1d_blank_tr_line_does_not_become_the_baseline():
    """빈 TR(예탁 0)이 기준점이 되면 이후 정상 줄이 전부 롤오버로 버려진다."""
    lines = [
        _line("2026-08-06 08:40:00", 0, 0, 0),                 # 빈 TR
        _line("2026-08-06 08:41:07", 30180776, 30180776, 0),
        _line("2026-08-06 14:48:25", 30180776, 29820634, -317000),
    ]
    gross, dep, nxt = _scan()(lines)
    assert (dep, nxt) == (30180776, 29820634)


# ── D2. 라이브 저장부 가드 ──────────────────────────────────────────────────
def test_d2_live_path_has_rollover_guard():
    """`main.py` 잔고 push가 롤오버 판독을 저장하지 않는지 소스로 고정한다.

    실행 경로 전체를 띄우지 않고 **불변식의 존재**만 본다 — 이 가드가 사라지면
    거래일 저녁 세션이 그날 net을 수수료로 덮어쓴다.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = open(os.path.join(root, "main.py"), encoding="utf-8").read()
    assert "_broker_dep_base_today" in src, "예탁현금 기준점 속성이 없다"
    assert "SKIP_ROLLOVER" in src, "롤오버 스킵을 로그로 남겨야 한다(500차 F-5)"
    # 계측 4원칙 ④ — 런타임 상태는 명시 초기화하고 getattr 폴백으로 읽지 않는다.
    assert src.count("self._broker_dep_base_today = None") >= 2, (
        "__init__ 과 daily_close 두 곳에서 None으로 초기화해야 한다 "
        "(리셋을 빠뜨리면 다음 날 전 판독이 롤오버로 오탐된다)")
    assert 'getattr(self, "_broker_dep_base_today"' not in src


# ── D3. 거래일 판정 캐시 ────────────────────────────────────────────────────
def test_d3_negative_result_for_today_is_not_cached():
    """오늘 날짜의 False는 '아직 아니다'이지 '아니다'가 아니다.

    장전 08:41 호출이 False를 굳히면 그날 `upsert_broker_net`이 종일 스킵된다.
    """
    from utils import db_utils

    today = datetime.date.today().isoformat()
    db_utils._trading_date_cache.pop(today, None)
    calls = {"n": 0}
    real = db_utils.fetchone

    def fake(db, sql, params=()):
        if params and params[0] == today:
            calls["n"] += 1
            return None                     # 아직 predictions/trades 없음
        return real(db, sql, params)

    db_utils.fetchone = fake
    try:
        assert db_utils.is_krx_trading_date(today) is False
        assert today not in db_utils._trading_date_cache, (
            "오늘의 음성을 캐시하면 장중에 값이 생겨도 영영 False다")
        before = calls["n"]
        db_utils.is_krx_trading_date(today)
        assert calls["n"] > before, "캐시에 걸리지 않고 재조회해야 한다"
    finally:
        db_utils.fetchone = real
        db_utils._trading_date_cache.pop(today, None)


def test_d3_past_negative_is_cached():
    """지난 날짜의 음성은 확정이다 — 매번 재조회하면 낭비다."""
    from utils import db_utils

    past = "2020-01-01"                     # 데이터가 있을 수 없는 과거
    db_utils._trading_date_cache.pop(past, None)
    assert db_utils.is_krx_trading_date(past) is False
    assert db_utils._trading_date_cache.get(past) is False
    db_utils._trading_date_cache.pop(past, None)


def test_d3_positive_is_cached():
    """양성은 영구 캐시 — 과거 거래일 판정은 바뀌지 않는다."""
    from utils import db_utils

    d = "2026-08-06"
    db_utils._trading_date_cache.pop(d, None)
    if not db_utils.is_krx_trading_date(d):
        pytest.skip("이 PC에 2026-08-06 예측/거래 데이터가 없다")
    assert db_utils._trading_date_cache.get(d) is True
