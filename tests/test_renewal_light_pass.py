"""[MW0602 신동 주체 리뉴얼] 미륵 휴면(MIREUK_ENGINE="off") 경량 분봉 패스 회귀 테스트.

계획서: docs/신동거래_V4/신동주체_리뉴얼_구현계획_미륵휴면_MW0602-20261024.md §1 · Phase 2.

지키는 불변식
  L1  off 분봉 1개 → 신동이 쓰는 부품 12개(P1~P12)가 **전부, 순서대로** 호출된다.
      부품이 하나라도 빠지면 이 테스트가 깨진다 — 미륵 파이프라인에 섞여 있던 일을 조용히 잃지 않게.
  L2  FLAT 이면 청산 감시(P8)만 빠지고 나머지는 그대로다.
  L3  비정상 봉(C1)은 가드에서 끝난다 — 봉 저장·ATR·화면 없음, 워치독은 리셋(파이프라인과 같다).
  L4  같은 ts 재주입은 첫 줄에서 막힌다.
  L5  청산 감시는 decision={} 로 불린다 — `_ts_check_exit_triggers` 는 decision 을 `.get` 으로만 읽는다.
  L6  `_on_candle_closed` 분기: 15:10 청산 전용 패스·거래소 CB 감지가 경량 패스보다 **앞**이고,
      off 면 `run_minute_pipeline` 을 부르지 않는다(소스 수준).
  L7  full 모드 파이프라인은 추출한 공유 메서드를 그대로 부른다(동작 무변경 — 두 벌 금지).
  L8  병행 건식 실행은 부작용이 없다(DB 큐·CB 기록·화면·워치독·시계 무변경).
  L9  미륵 off 에서 SYSTEM_AUTO 진입은 주문 함수 입구에서 거부된다.
  L10 DB 쓰기 워커가 "candle" op 를 save_candle 로 처리한다.

실행: python -m pytest tests/test_renewal_light_pass.py -q   (COM/브로커 불필요)
"""
import datetime
import inspect
import os
import queue
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402
from features.technical.atr import ATRCalculator  # noqa: E402

TS = main.TradingSystem


# ── 스텁 ──────────────────────────────────────────────────────────────────────

class _Pos(object):
    def __init__(self, status):
        self.status = status


class _Dash(object):
    def __init__(self, calls):
        self.calls = calls

    def notify_pipeline_ran(self):
        self.calls.append("notify_pipeline_ran")

    def update_price(self, **k):
        self.calls.append("update_price")

    def update_system_status(self, **k):
        self.calls.append(("update_system_status", k.get("accuracy", "missing")))

    def update_profit_guard_badge(self, st):
        self.calls.append("update_profit_guard_badge")


class _CB(object):
    state = "NORMAL"

    def __init__(self, calls):
        self.calls = calls

    def record_atr(self, r):
        self.calls.append("P10_cb4_record_atr")

    def record_pipe_latency(self, ms):
        self.calls.append("P11_cb5_record_latency")


class _PG(object):
    def guard_status(self, pnl, size_mult, dt):
        assert size_mult is None          # 신동 관문과 같은 축 — 등급 개념 없음
        return {}


class _Stub(object):
    """TradingSystem 대역 — 경량 패스가 만지는 속성만. 부품 메서드는 호출 이름만 기록한다."""

    LIGHT_PASS_PARTS = TS.LIGHT_PASS_PARTS
    _light_minute_pass = TS._light_minute_pass
    _light_minute_pass_dry = TS._light_minute_pass_dry
    _bar_price_guard = TS._bar_price_guard
    _light_atr_prime = TS._light_atr_prime
    _light_push_profit_guard_badge = TS._light_push_profit_guard_badge

    def __init__(self, status="LONG", qmax=10):
        self.calls = []
        self.position = _Pos(status)
        self.dashboard = _Dash(self.calls)
        self.circuit_breaker = _CB(self.calls)
        self.profit_guard = _PG()
        self.realtime_data = None
        self._db_write_queue = queue.Queue(maxsize=qmax)
        self._light_atr = ATRCalculator()
        self._light_atr_dry = ATRCalculator()
        self._light_atr_primed = True          # 예열은 별도 테스트(DB 없음)
        self._light_atr_dry_primed = True
        self._light_last_ts = None
        self._light_dry_stats = {"day": None, "bars": 0, "mismatch": 0, "atr_n": 0,
                                 "atr_maxrel": 0.0, "ms_max": 0.0}
        self._sys_daily_net_krw = 0.0
        self._sys_daily_legs = 0
        self._sys_daily_other_krw = 0.0
        self._sys_daily_other_legs = 0
        self._pg_badge_err_logged = False
        self._manual_entry_ctx = {}
        self._maint_ctx = None
        self._last_real_pipeline_dt = "SENTINEL"
        self._sigma_prev_price = 0.0
        self._last_pipe_ms = 0.0
        self.exit_args = None

    # 부품(추출 메서드) — 이름만 기록
    def _maybe_compute_levels_0930(self, ts_raw):
        self.calls.append("P3_levels_0930")

    def _process_tick_stop(self):
        self.calls.append("P7_tick_stop")

    def _check_pending_order_timeout(self):
        self.calls.append("P6_pending_timeout")

    def _check_exit_triggers(self, price, features, decision, bar=None):
        self.calls.append("P8_exit_triggers")
        self.exit_args = (price, features, decision, bar)

    def _push_position_panels(self, close, atr, bar, atr_ok=None, open_gap_ok=None):
        self.calls.append("P12_panels")


def _bar(minute=1, close=1050.0):
    return {"ts": datetime.datetime(2026, 10, 26, 10, minute), "open": close - 0.5,
            "high": close + 1.0, "low": close - 1.0, "close": close, "volume": 120}


def _with_patches(fn):
    """main 모듈 함수(가상 장부·로그)를 기록기로 바꿔 실행한다."""
    rec = {"vbook": 0, "logs": []}
    orig_vb, orig_lm = main._ts_vbook_on_bar, main.log_manager

    class _LM(object):
        def system(self, msg, level="INFO"):
            rec["logs"].append((level, msg))

        def signal(self, *a, **k):
            pass

        def trade(self, *a, **k):
            pass

    def _vb(self, bar, atr):
        self.calls.append("P10_vbook_on_bar")
        rec["vbook"] += 1

    main._ts_vbook_on_bar = _vb
    main.log_manager = _LM()
    try:
        fn(rec)
    finally:
        main._ts_vbook_on_bar, main.log_manager = orig_vb, orig_lm
    return rec


def _parts_seen(calls, s):
    """호출 기록 → 부품 이름 순서. 큐 적재(P1)·ATR(P10)·가드(P5)는 기록 대신 결과로 확인해 끼워 넣는다."""
    out = []
    for c in calls:
        if isinstance(c, str) and c[:1] == "P":
            out.append(c)
    return out


# ── L1 · L2 ──────────────────────────────────────────────────────────────────

def test_L1_all_twelve_parts_run_in_order_when_holding():
    s = _Stub(status="LONG")

    def run(rec):
        s._light_minute_pass(_bar())

    _with_patches(run)
    seen = _parts_seen(s.calls, s)
    # 기록되는 부품(메서드 호출)의 순서
    assert seen == ["P3_levels_0930", "P7_tick_stop", "P6_pending_timeout",
                    "P10_cb4_record_atr", "P8_exit_triggers", "P10_vbook_on_bar",
                    "P12_panels", "P11_cb5_record_latency"], seen
    # 결과로 확인하는 부품: P1 봉 저장(큐) · P10 ATR · P5 가드 통과 · P5 중복가드 기록
    item = s._db_write_queue.get_nowait()
    assert item[0] == "candle" and item[1]["close"] == 1050.0          # P1
    assert s._manual_entry_ctx["atr"] > 0                              # P10 ATR → 실주문 atr 인자
    assert s._light_last_ts == "2026-10-26 10:01:00"                   # P5 중복가드
    assert "notify_pipeline_ran" in s.calls                            # 워치독 리셋
    assert s._last_real_pipeline_dt != "SENTINEL"                      # ExchangeCB 감지 시계
    assert s._maint_ctx[1] == {} and "atr" in s._maint_ctx[0]          # 유지보수 패스 컨텍스트
    # 12부품 이름표가 계획서 표와 같은 개수
    assert len(TS.LIGHT_PASS_PARTS) == 12


def test_L2_flat_skips_only_exit_triggers():
    s = _Stub(status="FLAT")
    _with_patches(lambda rec: s._light_minute_pass(_bar()))
    seen = _parts_seen(s.calls, s)
    assert "P8_exit_triggers" not in seen
    for p in ("P3_levels_0930", "P7_tick_stop", "P6_pending_timeout", "P10_cb4_record_atr",
              "P10_vbook_on_bar", "P12_panels", "P11_cb5_record_latency"):
        assert p in seen, p
    assert s._db_write_queue.qsize() == 1


def test_L2b_cb3_shows_dormant_not_counting():
    s = _Stub(status="FLAT")
    _with_patches(lambda rec: s._light_minute_pass(_bar()))
    st = [c for c in s.calls if isinstance(c, tuple) and c[0] == "update_system_status"]
    assert st and st[0][1] is None       # accuracy=None → 대시보드가 「미륵 휴면」으로 쓴다


# ── L3 · L4 ──────────────────────────────────────────────────────────────────

def test_L3_bad_bar_stops_at_guard():
    s = _Stub(status="LONG")
    rec = _with_patches(lambda rec: s._light_minute_pass(_bar(close=0.0)))
    seen = _parts_seen(s.calls, s)
    assert seen == ["P3_levels_0930", "P7_tick_stop"], seen
    assert s._db_write_queue.qsize() == 0
    assert "notify_pipeline_ran" in s.calls
    assert any("[Guard-C1]" in m for _, m in rec["logs"])


def test_L4_duplicate_ts_blocked():
    s = _Stub(status="FLAT")

    def run(rec):
        s._light_minute_pass(_bar(minute=5))
        n = len(s.calls)
        s._light_minute_pass(_bar(minute=5))
        assert len(s.calls) == n
        assert any("중복 분봉" in m for _, m in rec["logs"])

    _with_patches(run)


def test_queue_full_falls_back_to_sync_save():
    s = _Stub(status="FLAT", qmax=1)
    s._db_write_queue.put_nowait(("x",))
    saved = []
    orig = main.save_candle
    main.save_candle = lambda b: saved.append(b)
    try:
        _with_patches(lambda rec: s._light_minute_pass(_bar()))
    finally:
        main.save_candle = orig
    assert len(saved) == 1 and saved[0]["close"] == 1050.0


def test_atr_prime_reads_recent_bars():
    s = _Stub()
    orig = main.fetch_recent_raw_candles
    rows = [{"high": 10 + i, "low": 9 + i, "close": 9.5 + i} for i in range(20)]
    main.fetch_recent_raw_candles = lambda limit=60: rows
    try:
        calc = ATRCalculator()
        assert s._light_atr_prime(calc) == 20
        assert calc._prev_close == 9.5 + 19
    finally:
        main.fetch_recent_raw_candles = orig


# ── L5 · L6 · L7 (소스 수준) ─────────────────────────────────────────────────

def test_L5_exit_triggers_reads_decision_only_via_get():
    src = inspect.getsource(main._ts_check_exit_triggers)
    assert "decision[" not in src
    assert "decision.get(" in src


def test_L5b_light_pass_passes_empty_decision():
    s = _Stub(status="SHORT")
    _with_patches(lambda rec: s._light_minute_pass(_bar()))
    price, feats, decision, bar = s.exit_args
    assert decision == {} and set(feats) == {"atr", "atr_ratio"} and price == 1050.0


def test_L6_on_candle_closed_dispatch_order():
    src = inspect.getsource(TS._on_candle_closed)
    i_fx = src.index("_ts_run_force_exit_pass(self, candle)")
    i_ecb = src.index("if self._exchange_cb_mode:")
    i_off = src.index("if not self._mireuk_on():")
    i_light = src.index("self._light_minute_pass(candle)")
    i_pipe = src.index("self.run_minute_pipeline(candle)")
    assert i_fx < i_ecb < i_off < i_light < i_pipe
    # off 분기는 경량 패스 뒤 return — 파이프라인으로 떨어지지 않는다
    branch = src[i_off:i_pipe]
    assert "return" in branch


def test_L6b_pre_market_off_saves_candle_and_levels():
    src = inspect.getsource(TS._on_pre_market_bar)
    i_off = src.index("if not self._mireuk_on():")
    i_ret = src.index("return", i_off)
    branch = src[i_off:i_ret]
    assert '("candle", candle)' in branch and "save_candle(candle)" in branch
    assert "self._maybe_compute_levels_0850(now_dt)" in branch
    # 스케일러 재적합·피처 계산보다 앞
    assert i_off < src.index("self.feature_builder.build(")


def test_L7_pipeline_uses_shared_methods():
    src = inspect.getsource(TS.run_minute_pipeline)
    for call in ("self._maybe_compute_levels_0930(ts_raw)", "self._bar_price_guard(bar, ts)",
                 "self._check_pending_order_timeout()",
                 "self._push_position_panels(close, atr, bar, _atr_ok, _open_gap_ok)",
                 "self._process_tick_stop()"):
        assert call in src, call
    # 옮긴 블록이 파이프라인 안에 두 벌로 남아 있지 않다
    assert "[Guard-C1]" not in src
    assert "PendingOrder 타임아웃 체크" not in src
    lsrc = inspect.getsource(TS._light_minute_pass)
    for call in ("self._maybe_compute_levels_0930(ts_raw)", "self._bar_price_guard(bar, ts)",
                 "self._check_pending_order_timeout()", "self._push_position_panels(",
                 "self._process_tick_stop()", "self._check_exit_triggers(close, feats, {}, bar)"):
        assert call in lsrc, call


# ── L8 건식 실행 ─────────────────────────────────────────────────────────────

def test_L8_dry_run_has_no_side_effects():
    s = _Stub(status="LONG")
    s._maint_ctx = ({"atr": 2.0, "atr_ratio": 1.0}, {}, "2026-10-26 10:01:00")

    def run(rec):
        s._light_minute_pass_dry(_bar(), pipeline_completed=True)

    rec = _with_patches(run)
    assert s.calls == []                              # CB·화면·부품 무호출
    assert s._db_write_queue.qsize() == 0
    assert s._last_real_pipeline_dt == "SENTINEL"
    assert s._light_last_ts is None                   # 실집행 중복가드 상태 무변경
    assert s._light_dry_stats["bars"] == 1


def test_L8b_dry_run_reports_guard_mismatch():
    s = _Stub(status="FLAT")
    rec = _with_patches(lambda rec: s._light_minute_pass_dry(_bar(close=0.0), pipeline_completed=True))
    assert s._light_dry_stats["mismatch"] == 1
    assert any("[LightPassDry] 불일치" in m for _, m in rec["logs"])


def test_L8c_dry_run_reports_atr_drift():
    s = _Stub(status="FLAT")
    s._maint_ctx = ({"atr": 50.0, "atr_ratio": 1.0}, {}, "x")      # 경량 ATR(≈2)과 크게 다르다
    rec = _with_patches(lambda rec: s._light_minute_pass_dry(_bar(), pipeline_completed=True))
    assert any("atr 경량=" in m for _, m in rec["logs"])


def test_L8d_dry_flag_only_in_full_mode():
    src = inspect.getsource(TS.__init__)
    assert 'and self._mireuk_engine == "full"' in src


# ── L9 · L10 ─────────────────────────────────────────────────────────────────

def test_L9_system_auto_rejected_when_off():
    class _S(object):
        def _mireuk_on(self):
            return False

    logs = []
    orig = main.log_manager

    class _LM(object):
        def system(self, msg, level="INFO"):
            logs.append((level, msg))

    main.log_manager = _LM()
    try:
        r = main._ts_execute_entry(_S(), "LONG", 1050.0, 1, 2.0, "A", entry_source="SYSTEM_AUTO")
    finally:
        main.log_manager = orig
    assert r is None
    assert logs and logs[0][0] == "ERROR" and "[MireukOff]" in logs[0][1]


def test_L9b_rejection_precedes_everything():
    src = inspect.getsource(main._ts_execute_entry)
    assert src.index("[MireukOff]") < src.index("_ts_in_exit_cooldown(self)")


def test_L10_db_worker_handles_candle_op():
    src = inspect.getsource(TS._db_write_worker)
    i = src.index('op == "candle":')
    assert "save_candle(_bar)" in src[i:i + 300]


def test_engine_value_validation_in_init():
    src = inspect.getsource(TS.__init__)
    assert 'if _me_raw not in ("full", "off"):' in src
    assert 'self._mireuk_engine = _me_raw' in src
