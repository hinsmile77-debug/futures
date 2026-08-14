"""[MW0601 471차 F-1·F-2] 15:10 강제청산 1차 경로 도달성 + 안전망 하트비트 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: docs/정기점검/매일점검/MW0601-20260814-점검리포트-post.md P1-1)
────────────────────────────────────────────────────────────────────────────
15:10 강제청산의 1차 집행자는 STEP 8(분봉 구동)이고 453차 D2 스케줄러 안전망
(15:11, ERROR + 🚨 알림)이 2차 방어선이다. 그런데 1차가 실행될 시각 창이
**존재하지 않았다**:
  ① `_on_candle_closed`가 `is_force_exit_time` 가드로 조기 반환하고
  ② 15:09 봉의 마감 콜백은 정확히 15:10:00에 도착하며(2026-08-14 실측)
  ③ 워치독·복구 패스도 같은 가드로 막혀 있다.
그래서 2차 안전망이 상시 1차가 됐고(단일 실패점화), 정상 마감이 매번 ERROR +
🚨 알림으로 보고될 참이었다. 실거래 표본은 전부 15:10 전에 닫혀 6개월간
1차·2차 어느 쪽도 실행된 적이 없다 — 실측 반증이 없으므로 이 테스트가 유일한 방어다.

지키는 불변식:
  F-1 (T1~T5)  15:10 이후 분봉 마감 → 청산 전용 패스가 STEP 8을 1회 평가한다.
               예측·저장·시계(_last_real_pipeline_dt·notify_pipeline_ran)는 불변.
               FLAT·pending·가격없음은 평가하지 않는다.
  F-2 (T6~T7)  FLAT이어도 안전망이 당일 1회 하트비트를 남긴다(30s마다가 아니라).
               하트비트에 `bar_pass=N회`가 실려 1차 경로 도달성을 증명한다.
  회귀   (T8)  `_on_candle_closed`의 강제청산 가드가 청산 전용 패스를 호출한다
               (호출이 빠지면 P1-1이 그대로 재발한다 — 소스 수준으로 못 박는다).

실행: python tests/test_471_force_exit_reachability.py   (COM/브로커 불필요)
"""

import datetime
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402  (~5s — 스텁 self로 _ts_* 모듈 함수를 직접 구동한다)

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


# ── 공용 스텁 ────────────────────────────────────────────────────────────────

class _StubPosition(object):
    def __init__(self, status="FLAT", quantity=0):
        self.status = status
        self.quantity = quantity
        self.entry_price = 1089.85


class _StubSelf(object):
    """TradingSystem 대역 — _ts_* 모듈 함수가 실제로 만지는 속성만 갖는다.

    dashboard 속성을 **일부러 두지 않는다** — 청산 전용 패스가 시계를 건드리면
    (notify_pipeline_ran) AttributeError로 즉사해 T4가 잡아낸다.
    """

    def __init__(self, status="FLAT", pending=False, broker_qty=0,
                 last_price=0.0, maint_ctx=None, quantity=2):
        self.position = _StubPosition(status=status, quantity=quantity)
        self._pending = pending
        self._integrity_broker_qty = broker_qty
        self._last_pipeline_price = last_price
        if maint_ctx is not None:
            self._maint_ctx = maint_ctx
        self._last_real_pipeline_dt = "SENTINEL"      # 바뀌면 T4 실패
        self._maint_ctx_sentinel = None
        # 471차 명시 초기화 3종 (계측 4원칙 ④ — getattr 폴백으로 읽지 않는다)
        self._force_exit_pass_evals = 0
        self._force_exit_pass_date = None
        self._sched_force_exit_heartbeat_date = None
        self.exit_calls = []                           # _check_exit_triggers 기록

    def _has_pending_order(self):
        return self._pending

    def _check_exit_triggers(self, price, features, decision, bar=None):
        self.exit_calls.append((price, features, decision, bar))


class _LogRecorder(object):
    """main.log_manager 대역 — system() 호출만 기록한다."""

    def __init__(self):
        self.lines = []

    def system(self, msg, level="INFO"):
        self.lines.append((level, msg))

    def signal(self, msg, *a, **k):
        pass

    def trade(self, msg, *a, **k):
        pass


def _with_recorded_log(fn):
    orig = main.log_manager
    rec = _LogRecorder()
    main.log_manager = rec
    try:
        fn(rec)
    finally:
        main.log_manager = orig


# 2026-08-14(금)은 실거래일 — 로그·DB에 데이터가 존재하는 날짜를 쓴다.
_D = datetime.datetime(2026, 8, 14)

# 2026-08-14 15:09 봉 실측값 (SYSTEM.log:5284 — 마감 콜백이 15:10:00에 도착한 그 봉)
_CANDLE = {
    "ts": "2026-08-14 15:09:00", "open": 1096.58, "high": 1097.08,
    "low": 1096.12, "close": 1097.08, "volume": 94,
}


# ── F-1: 청산 전용 패스 ─────────────────────────────────────────────────────

def test_t1_position_open_evaluates_step8():
    def body(rec):
        feats = {"atr": 1.23}
        dec = {"direction": -1, "confidence": 0.61, "min_conf": 0.5}
        stub = _StubSelf(status="SHORT", maint_ctx=(feats, dec, "2026-08-14 15:08:00"))
        main._ts_run_force_exit_pass(stub, _CANDLE)

        check("T1: STEP 8 청산 감시 1회 호출", len(stub.exit_calls) == 1)
        price, f, d, bar = stub.exit_calls[0]
        check("T1: 가격 = 방금 마감한 봉의 종가 (정규 STEP 8과 동일 입력)",
              price == 1097.08)
        check("T1: 캐시된 features 재사용", f is feats)
        check("T1: 캐시된 decision 재사용", d is dec)
        check("T1: bar에 high/low 승계 (봉중 스톱 판정용)",
              bar["high"] == 1097.08 and bar["low"] == 1096.12)
        check("T1: 호출 카운터 증가", stub._force_exit_pass_evals == 1)
    _with_recorded_log(body)


def test_t2_flat_skips_but_still_counts():
    def body(rec):
        stub = _StubSelf(status="FLAT", quantity=0)
        main._ts_run_force_exit_pass(stub, _CANDLE)
        check("T2: FLAT+무pending+잔량0 → STEP 8 미호출", len(stub.exit_calls) == 0)
        # 🔴 카운터는 그래도 올라야 한다 — 이것이 "1차 경로가 살아 있다"의 유일한 증거
        check("T2: FLAT이어도 호출 카운터는 증가(도달성 증거)",
              stub._force_exit_pass_evals == 1)
        check("T2: FLAT은 로그를 남기지 않는다(하트비트는 F-2 담당)",
              len(rec.lines) == 0)

        # 내부 FLAT이지만 브로커 잔량 캐시 > 0 (유령 잔량) → 평가한다
        stub2 = _StubSelf(status="FLAT", quantity=0, broker_qty=2)
        main._ts_run_force_exit_pass(stub2, _CANDLE)
        check("T2: FLAT+브로커잔량2 → STEP 8 호출 (유령 잔량 케이스)",
              len(stub2.exit_calls) == 1)
    _with_recorded_log(body)


def test_t3_pending_and_no_price_are_skipped():
    def body(rec):
        stub = _StubSelf(status="SHORT", pending=True)
        main._ts_run_force_exit_pass(stub, _CANDLE)
        check("T3: pending 주문 대기 중 → STEP 8 미호출(이중 주문 방지)",
              len(stub.exit_calls) == 0)
        check("T3: pending 스킵은 로그를 남긴다(계측 4원칙 ③)",
              any("[ForceExitPass]" in m and "pending" in m for _l, m in rec.lines))

        # 봉도 비고 틱 캐시도 없음 → 스킵 (D2 안전망에 위임)
        stub2 = _StubSelf(status="SHORT", last_price=0.0)
        main._ts_run_force_exit_pass(stub2, {"ts": "2026-08-14 15:09:00"})
        check("T3: 가격 힌트 없음 → 스킵", len(stub2.exit_calls) == 0)

        # 봉이 비었지만 틱 캐시는 살아 있음 → 폴백해서 평가
        stub3 = _StubSelf(status="SHORT", last_price=1096.50)
        main._ts_run_force_exit_pass(stub3, {"ts": "2026-08-14 15:09:00"})
        check("T3: 봉 종가 없음 → 틱 캐시 폴백",
              len(stub3.exit_calls) == 1 and stub3.exit_calls[0][0] == 1096.50)
    _with_recorded_log(body)


def test_t4_clocks_untouched():
    """🔴 핵심 — 청산 전용 패스는 시계 2개를 절대 건드리지 않는다 (453차 D1 규약).

    _StubSelf에는 dashboard가 없다 — notify_pipeline_ran()을 시도하면
    AttributeError로 즉사한다. _last_real_pipeline_dt는 센티넬 비교.
    """
    def body(rec):
        stub = _StubSelf(status="SHORT", maint_ctx=({}, {}, "2026-08-14 15:08:00"))
        main._ts_run_force_exit_pass(stub, _CANDLE)   # dashboard 없이 통과해야 함
        check("T4: _last_real_pipeline_dt 불변", stub._last_real_pipeline_dt == "SENTINEL")
        check("T4: dashboard 미접촉 (AttributeError 없이 완주)", True)
        check("T4: _maint_ctx 불변 (재실행이 아니므로 갱신하지 않는다)",
              stub._maint_ctx[2] == "2026-08-14 15:08:00")
    _with_recorded_log(body)


def test_t5_repeated_calls_are_safe():
    """15:10~장마감 사이 매 분봉마다 호출된다 — 멱등해야 한다."""
    def body(rec):
        stub = _StubSelf(status="SHORT", maint_ctx=({}, {}, ""))
        for _ in range(5):
            main._ts_run_force_exit_pass(stub, _CANDLE)
        check("T5: 5회 호출 → STEP 8 5회 평가 (pending 가드는 STEP 8 내부 책임)",
              len(stub.exit_calls) == 5)
        check("T5: 카운터 5", stub._force_exit_pass_evals == 5)

        # pending이 걸린 뒤로는 더 이상 평가하지 않는다
        stub._pending = True
        main._ts_run_force_exit_pass(stub, _CANDLE)
        check("T5: pending 등록 후 추가 평가 없음", len(stub.exit_calls) == 5)
    _with_recorded_log(body)


# ── F-2: 안전망 하트비트 ────────────────────────────────────────────────────

def test_t6_heartbeat_once_a_day_when_flat():
    def body(rec):
        stub = _StubSelf(status="FLAT", quantity=0)
        stub._force_exit_pass_evals = 3        # 1차 경로가 3번 돌았다고 가정
        for sec in (0, 30, 60, 90):
            main._ts_scheduler_force_exit_net(
                stub, _D.replace(hour=15, minute=11) + datetime.timedelta(seconds=sec))
        beats = [m for _l, m in rec.lines if "[SchedForceExit]" in m]
        check("T6: 30초 틱 4회 → 하트비트는 1건만 (로그 폭주 방지)", len(beats) == 1)
        check("T6: 하트비트에 '청산 대상 없음(정상)' 명시",
              beats and "청산 대상 없음(정상)" in beats[0])
        check("T6: 하트비트에 bar_pass 실림 (1차 경로 도달성 증거)",
              beats and "bar_pass=3회" in beats[0])
        check("T6: 하트비트는 INFO — 정상 마감을 사고로 보고하지 않는다",
              rec.lines and rec.lines[0][0] == "INFO")
        check("T6: 하트비트 날짜 기록", stub._sched_force_exit_heartbeat_date == _D.date())
    _with_recorded_log(body)


def test_t7_heartbeat_does_not_fire_when_position_open():
    def body(rec):
        # 포지션이 있으면 하트비트가 아니라 실제 안전망 경로로 가야 한다
        orig = main._ts_broker_direct_force_exit
        calls = []
        main._ts_broker_direct_force_exit = (
            lambda s, price, reason="강제청산": calls.append((price, reason)) or True)
        try:
            stub = _StubSelf(status="LONG", last_price=1097.0)
            main._ts_scheduler_force_exit_net(stub, _D.replace(hour=15, minute=11))
        finally:
            main._ts_broker_direct_force_exit = orig
        check("T7: 포지션 보유 시 하트비트 아님 — 실청산 시도",
              len(calls) == 1 and not any("청산 대상 없음" in m for _l, m in rec.lines))
        # 유예 구간(15:10:30)에는 하트비트도 실청산도 없다
        _n_before = len(rec.lines)
        stub2 = _StubSelf(status="FLAT", quantity=0)
        main._ts_scheduler_force_exit_net(
            stub2, _D.replace(hour=15, minute=10, second=30))
        check("T7: 15:11 이전(유예 중) → 하트비트 미출력",
              len(rec.lines) == _n_before
              and stub2._sched_force_exit_heartbeat_date is None)
    _with_recorded_log(body)


# ── 회귀 가드 ───────────────────────────────────────────────────────────────

def test_t8_bar_close_guard_calls_force_exit_pass():
    """🔴 P1-1 재발 방지 — 가드가 청산 전용 패스 없이 return하면 즉시 실패한다."""
    src = inspect.getsource(main.TradingSystem._on_candle_closed)
    idx = src.find("is_force_exit_time(now)")
    check("T8: _on_candle_closed에 강제청산 가드 존재", idx > 0)
    tail = src[idx:idx + 900]
    check("T8: 가드 안에서 _ts_run_force_exit_pass 호출",
          "_ts_run_force_exit_pass(self, candle)" in tail)
    check("T8: 호출이 return보다 먼저 (조기 반환 전에 STEP 8 평가)",
          "_ts_run_force_exit_pass" in tail
          and tail.index("_ts_run_force_exit_pass") < tail.index("return"))


if __name__ == "__main__":
    _fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in _fns:
        try:
            fn()
        except Exception as e:
            FAILURES.append("%s: %r" % (fn.__name__, e))
            print("[FAIL] %s: %r" % (fn.__name__, e))
    print("-" * 60)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")
