# -*- coding: utf-8 -*-
"""[MW0601 546차] ProfitGuard 판정 손익 = 시스템 자동매매 한정 — 회귀 가드.

계기 — 사용자 지시 「판정에서 외부매매 손익 분리하고 시스템 자동 매매에만
적용하도록 코드개선해」(2026-09-08).

**시스템이 벌지 않은 돈으로 시스템이 멈춘 날을 재현한다.** 2026-09-08 실측:
09:04:58 장 시작 전 브로커 실현손익이 이미 +446,000원(엔진 0원)이었고,
09:18~09:20 외부(수동) 매매가 634,000원까지 밀어올려 09:21 `L2-Tier4`
(중단 임계 500,000원)가 당일 영구 중단으로 래치됐다. 그날 시스템 자동진입은
**0건**이다.

고정하는 사실:
① 집계기가 `entry_source` 로만 가른다 — `SYSTEM_AUTO` 외에는 전부 제외이고
   NULL 은 **미측정이지 시스템진입이 아니다**(423차 실측: 이 구간 6건이 A급
   30일 합계의 부호를 뒤집었다).
② 레그 단위 합산이다(계측 4원칙 ①) — TP1/TP2/TP3 3레그의 합이 포지션 손익.
③ **미측정 ≠ 0** — 시스템 청산 0레그를 `legs=0`으로 구분해 돌려준다.
④ 2026-09-08 시나리오 재현 — 같은 임계·같은 판정식에서 **새 축이면 래치가
   일어나지 않는다**. 반대로 시스템이 스스로 그만큼 벌면 **여전히 래치된다**
   (게이트를 약화시킨 것이 아니라 대상을 좁힌 것임을 고정).
⑤ `fetch_today_trades` 는 컬럼만 늘었다 — 기존 컬럼·행 필터 무변경.
⑥ 설정 플래그를 끄면 종전 경로로 복귀한다.
"""
import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import sum_today_system_net_krw  # noqa: E402
from strategy.profit_guard import ProfitGuard, ProfitGuardConfig, _PNL_SRC_LABEL  # noqa: E402
import config.settings as S  # noqa: E402


LIVE_0908_TIERS = [
    (0, 0.6, None),
    (500_000, 0.6, None),
    (500_000, 1.0, None),
    (500_000, 1.2, None),
    (500_000, 1.5, 0),
]


class _Row(dict):
    """`sqlite3.Row` 흉내 — 집계기가 `keys()`/`[]` 만 쓴다."""
    def keys(self):
        return list(super(_Row, self).keys())


def _leg(pnl, src="SYSTEM_AUTO"):
    return _Row({"pnl_krw": pnl, "entry_source": src})


# ── ① entry_source 로만 가른다 ─────────────────────────────────────────
def test_only_system_auto_counts():
    rows = [
        _leg(+100_000, "SYSTEM_AUTO"),
        _leg(+165_994, "GHOST_PENDING_MISS"),   # 2026-09-08 외부진입 경로
        _leg(+67_012,  "OPERATOR_MANUAL"),
        _leg(-50_000,  "BROKER_SYNC_RECOVERY"),
        _leg(+10_000,  "OPERATOR_RESTORE"),
    ]
    r = sum_today_system_net_krw(rows)
    assert r["net_krw"] == 100_000
    assert r["legs"] == 1
    assert r["other_net_krw"] == 165_994 + 67_012 - 50_000 + 10_000
    assert r["other_legs"] == 4
    assert r["unknown_legs"] == 0


def test_null_entry_source_is_not_system():
    """311차 이전 구간 — 미측정이지 시스템진입이 아니다."""
    rows = [_leg(+500_000, None), _leg(+1_000, "SYSTEM_AUTO")]
    r = sum_today_system_net_krw(rows)
    assert r["net_krw"] == 1_000
    assert r["legs"] == 1
    assert r["unknown_legs"] == 1
    assert r["other_net_krw"] == 500_000


def test_missing_column_is_treated_as_unknown():
    """구버전 행(entry_source 컬럼 없음)도 시스템으로 승격하지 않는다."""
    rows = [_Row({"pnl_krw": 999_999})]
    r = sum_today_system_net_krw(rows)
    assert r["legs"] == 0 and r["unknown_legs"] == 1


# ── ② 레그 단위 합산 ───────────────────────────────────────────────────
def test_legs_sum_to_position():
    """TP1/TP2/TP3 3레그 = 포지션 1건. `legs` 는 거래 건수가 아니다."""
    rows = [_leg(+81_497), _leg(+84_497), _leg(-1_000)]
    r = sum_today_system_net_krw(rows)
    assert r["net_krw"] == 164_994
    assert r["legs"] == 3           # 레그 수이지 포지션 수가 아니다


# ── ③ 미측정 ≠ 0 ──────────────────────────────────────────────────────
def test_no_system_legs_is_distinguishable():
    r = sum_today_system_net_krw([_leg(+600_000, "GHOST_PENDING_MISS")])
    assert r["net_krw"] == 0 and r["legs"] == 0        # 값과 표본을 따로 준다
    assert r["other_legs"] == 1


def test_empty_rows():
    r = sum_today_system_net_krw([])
    assert r == {"net_krw": 0, "legs": 0, "other_net_krw": 0,
                 "other_legs": 0, "unknown_legs": 0}


# ── ④ 2026-09-08 재현 ─────────────────────────────────────────────────
def _guard():
    cfg = ProfitGuardConfig()
    cfg.profit_tiers = LIVE_0908_TIERS
    cfg.trail_activation_krw = 300_000
    cfg.trail_ratio = 0.10
    return ProfitGuard(cfg)


# 그날 TRADE 로그 실측 — 전부 외부(pending_miss) 경로였다.
ROWS_0908 = [
    _leg(+81_497,  "GHOST_PENDING_MISS"),
    _leg(+84_497,  "GHOST_PENDING_MISS"),
    _leg(-6_022,   "GHOST_PENDING_MISS"),
    _leg(+5_980,   "GHOST_PENDING_MISS"),
    _leg(-5_024,   "GHOST_PENDING_MISS"),
    _leg(+67_012,  "GHOST_PENDING_MISS"),
    _leg(-159_973, "GHOST_PENDING_MISS"),
]


def test_0908_no_longer_latches_on_external_pnl():
    """🔴 이 지시의 핵심 — 외부 매매만으로는 더 이상 시스템이 멈추지 않는다."""
    r = sum_today_system_net_krw(ROWS_0908)
    assert r["legs"] == 0                      # 그날 시스템 청산 0건
    g = _guard()
    now = datetime.datetime(2026, 9, 8, 9, 21)
    ok, why = g.is_entry_allowed(r["net_krw"], 1.0, now,
                                 pnl_source="engine_system_only")
    assert ok is True and why == ""
    st = g.guard_status(r["net_krw"], 1.0, now)
    assert st["halted"] is False and st["blocking"] is False

    # 종전 축(계좌 전체 +513,967원)이면 같은 설정에서 래치된다 — 대조군.
    g2 = _guard()
    ok2, why2 = g2.is_entry_allowed(513_967, 1.0, now, pnl_source="broker_net_est")
    assert ok2 is False and why2.startswith("[L2-Tier4]")


def test_gate_still_fires_when_system_itself_earns_it():
    """게이트를 약화시킨 것이 아니다 — 대상을 좁혔을 뿐이다."""
    rows = ROWS_0908 + [_leg(+520_000, "SYSTEM_AUTO")]
    r = sum_today_system_net_krw(rows)
    assert r["legs"] == 1 and r["net_krw"] == 520_000
    g = _guard()
    ok, why = g.is_entry_allowed(r["net_krw"], 1.0,
                                 datetime.datetime(2026, 9, 8, 13, 0),
                                 pnl_source="engine_system_only")
    assert ok is False and why.startswith("[L2-Tier4]")


def test_l1_trailing_uses_the_same_narrowed_axis():
    """L1 피크도 시스템 축으로만 오른다 — 외부 이익이 보호선을 밀어올리지 않는다."""
    g = _guard()
    now = datetime.datetime(2026, 9, 8, 10, 0)
    # 시스템 실현 +350,000 → 발동금액(300,000) 돌파, 보호선 315,000
    g.is_entry_allowed(350_000, 1.0, now, pnl_source="engine_system_only")
    st = g.guard_status(350_000, 1.0, now)
    assert st["layers"]["L1"]["state"] == "armed"
    assert st["trail_floor"] == pytest.approx(315_000.0)
    # 외부 손익이 아무리 커도 이 축에는 들어오지 않는다(호출부가 안 넘긴다).
    assert st["peak_pnl"] == 350_000


# ── ⑤ 손익 원천 토큰 ───────────────────────────────────────────────────
def test_pnl_source_label_registered():
    """모든 차단 줄이 어느 축으로 판정됐는지 스스로 말해야 한다(477차 GR-3)."""
    assert "engine_system_only" in _PNL_SRC_LABEL
    assert "시스템진입만" in _PNL_SRC_LABEL["engine_system_only"]


def test_block_log_carries_axis_token(capsys):
    g = _guard()
    g.is_entry_allowed(600_000, 1.0, datetime.datetime(2026, 9, 8, 13, 0),
                       pnl_source="engine_system_only")
    assert g._pnl_source == "engine_system_only"


# ── ⑥ 설정 ────────────────────────────────────────────────────────────
def test_settings_flag_and_sources():
    assert S.PROFIT_GUARD_SYSTEM_ONLY_PNL is True
    assert S.PROFIT_GUARD_SYSTEM_SOURCES == ("SYSTEM_AUTO",)
    # 제외 대상이 실수로 시스템에 포함되지 않았는지 — 이름으로 고정한다.
    for bad in ("OPERATOR_MANUAL", "GHOST_PENDING_MISS",
                "BROKER_SYNC_RECOVERY", "OPERATOR_RESTORE"):
        assert bad not in S.PROFIT_GUARD_SYSTEM_SOURCES


def test_sources_override_is_honored():
    rows = [_leg(+10_000, "SYSTEM_AUTO"), _leg(+20_000, "OPERATOR_MANUAL")]
    r = sum_today_system_net_krw(rows, sources=("SYSTEM_AUTO", "OPERATOR_MANUAL"))
    assert r["net_krw"] == 30_000 and r["legs"] == 2


# ── ⑦ fetch_today_trades 는 컬럼만 늘었다 ──────────────────────────────
def test_fetch_today_trades_query_shape():
    """행 필터·정렬·기존 컬럼 무변경 — 컬럼 하나만 추가됐다."""
    import inspect
    from utils import db_utils
    src = inspect.getsource(db_utils.fetch_today_trades)
    assert "entry_source" in src
    assert "WHERE exit_ts LIKE ?" in src          # 행 필터 무변경
    assert "ORDER BY exit_ts ASC" in src          # 정렬 무변경
    for col in ("entry_price", "exit_price", "quantity", "pnl_pts",
                "exit_reason", "grade", "entry_ts", "exit_ts"):
        assert col in src


# ── ⑧ 호출부 배선 ─────────────────────────────────────────────────────
def test_main_wires_the_narrowed_axis():
    """ProfitGuard 호출·배지·패널이 **같은 축**을 보는지 소스로 고정한다.

    셋이 갈리면 "배지가 말하는 손익"과 "실제로 막은 손익"이 어긋난다 —
    2026-09-08 배지 사건과 같은 계열의 결함이 된다.
    """
    import io
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = io.open(os.path.join(base, "main.py"), encoding="utf-8").read()
    # 판정 호출이 좁힌 축을 쓴다
    assert "self.profit_guard.is_entry_allowed(\r\n            _pg_pnl_now," in src \
        or "self.profit_guard.is_entry_allowed(\n            _pg_pnl_now," in src
    assert "pnl_source=_pg_pnl_source," in src
    # 배지도 같은 축
    assert "guard_status(\r\n                _pg_pnl_now," in src \
        or "guard_status(\n                _pg_pnl_now," in src
    # 누적기가 __init__ 에서 명시 초기화된다(계측 4원칙 ④)
    assert "self._sys_daily_net_krw:   float = 0.0" in src
    assert "self._sys_daily_legs:      int   = 0" in src
    # daily_close 에서 리셋된다
    assert "self._sys_daily_net_krw = 0.0" in src


def test_session_recovery_restores_accumulator():
    import io
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = io.open(os.path.join(base, "strategy", "runtime",
                               "session_recovery_service.py"), encoding="utf-8").read()
    assert "sum_today_system_net_krw" in src
    assert "system._sys_daily_net_krw" in src
    assert "system._sys_daily_legs" in src


# ── ⑨ 패널도 같은 축을 본다 ────────────────────────────────────────────
def test_panel_rows_to_dicts_filters_system_only():
    """패널 시뮬레이션이 계좌 전체를 쓰면 화면이 제안하는 임계와 실제로 발동하는
    임계가 달라진다 — `_rows_to_dicts` 한 곳이 그 깔때기다."""
    _p = pytest.importorskip("dashboard.panels.profit_guard_panel")
    P = _p.ProfitGuardPanel
    rows = [
        {"pnl_krw": 100_000, "entry_source": "SYSTEM_AUTO"},
        {"pnl_krw": 500_000, "entry_source": "GHOST_PENDING_MISS"},
        {"pnl_krw": 300_000},                      # entry_source 없음 → 제외
        {"pnl_krw": 7_000, "entry_source": None},  # NULL → 제외
    ]
    out = P._rows_to_dicts(rows)
    assert [t["pnl_krw"] for t in out] == [100_000]
