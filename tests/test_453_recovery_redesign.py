"""[MW0601 453차] 복구 봉 이중 처리 해소(D1~D4) 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: docs/미륵이고도화3/복구봉_이중처리_딥다이브_및_설계제안_2026-08-09.md)
────────────────────────────────────────────────────────────────────────────
~452차의 복구는 raw_candles 마지막 봉으로 run_minute_pipeline()을 통째로
재실행했다. 완주 42회 실측 기준:
  ① BarAggregator 격자를 회당 1분씩 영구로 밀었고 (08-04 30m 경계 최대 7분)
  ② predictions (ts,horizon) 중복 423그룹·고아 800행을 만들었고
  ③ 90s+ 묵은 데이터로 STEP 7 실주문이 구조적으로 가능했고
  ④ 완주가 워치독·ExchangeCB 시계 2개를 되감아 감지를 ~90s 늦췄다.
또한 완전 피드 스톨이 15:10을 관통하면 청산 주체가 아무도 없었다(절대원칙 §1 구멍).

지키는 불변식:
  D2 (T1~T3)  시간 청산 안전망 — 15:11+ & 미청산 → 브로커 직접 청산.
              유예 중·pending·FLAT·장마감엔 발화하지 않는다.
  D1 (T4~T6)  유지보수 패스 — 청산 감시만 수행. 시계 2개(_last_real_pipeline_dt·
              notify_pipeline_ran)를 절대 건드리지 않는다.
  D3 (T7~T8)  중복 정리(채점 행 생존 + 아카이브) → UNIQUE 인덱스 → OR IGNORE.
  D4 (T9)     BarAggregator 동일 ts 재push → 버퍼·age·격자 불변.

실행: python tests/test_453_recovery_redesign.py   (COM/브로커 불필요)
"""

import datetime
import os
import sqlite3
import sys
import tempfile

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
    def __init__(self, status="FLAT", quantity=0, entry_price=0.0):
        self.status = status
        self.quantity = quantity
        self.entry_price = entry_price


class _StubSelf(object):
    """TradingSystem 대역 — _ts_* 모듈 함수가 실제로 만지는 속성만 갖는다.

    dashboard 속성을 **일부러 두지 않는다** — 유지보수 패스가 시계를 건드리면
    AttributeError로 즉사해 T5가 잡아낸다.
    """

    def __init__(self, status="FLAT", pending=False, broker_qty=0,
                 last_price=0.0, maint_ctx=None):
        self.position = _StubPosition(status=status, quantity=2, entry_price=970.0)
        self._pending = pending
        self._integrity_broker_qty = broker_qty
        self._last_pipeline_price = last_price
        if maint_ctx is not None:
            self._maint_ctx = maint_ctx
        self._last_real_pipeline_dt = "SENTINEL"      # 바뀌면 T5 실패
        self.exit_calls = []                           # _check_exit_triggers 기록

    def _has_pending_order(self):
        return self._pending

    def _check_exit_triggers(self, price, features, decision, bar=None):
        self.exit_calls.append((price, features, decision, bar))


# ── D2: 시간 청산 피드 독립 안전망 ──────────────────────────────────────────

class _ExitRecorder(object):
    def __init__(self, ret=True):
        self.calls = []
        self._ret = ret

    def __call__(self, self_arg, price, reason="강제청산"):
        self.calls.append((price, reason))
        return self._ret


def _with_recorded_exit(fn):
    """main._ts_broker_direct_force_exit를 레코더로 갈아끼우고 실행."""
    orig = main._ts_broker_direct_force_exit
    rec = _ExitRecorder()
    main._ts_broker_direct_force_exit = rec
    try:
        fn(rec)
    finally:
        main._ts_broker_direct_force_exit = orig


# 2026-08-07(금)은 실거래일 — 로그·DB에 데이터가 존재하는 날짜를 쓴다.
_D = datetime.datetime(2026, 8, 7)


def test_t1_fires_after_grace_with_position():
    def body(rec):
        stub = _StubSelf(status="LONG", last_price=971.5)
        sent = main._ts_scheduler_force_exit_net(stub, _D.replace(hour=15, minute=11))
        check("T1: 15:11 + LONG → 청산 주문 전송", sent is True and len(rec.calls) == 1)
        check("T1: 가격 힌트 = _last_pipeline_price", rec.calls[0][0] == 971.5)
        check("T1: 시도 카운터 증가", stub._sched_force_exit_attempts == 1)
    _with_recorded_exit(body)


def test_t2_grace_period_and_before():
    def body(rec):
        stub = _StubSelf(status="LONG", last_price=971.5)
        # 15:09 — 강제청산 시각 전
        main._ts_scheduler_force_exit_net(stub, _D.replace(hour=15, minute=9))
        # 15:10:30 — 유예 중 (정규 STEP 8의 기회)
        main._ts_scheduler_force_exit_net(stub, _D.replace(hour=15, minute=10, second=30))
        check("T2: 15:09·15:10:30(유예) → 미발화", len(rec.calls) == 0)
    _with_recorded_exit(body)


def test_t3_blockers():
    def body(rec):
        # pending 대기 중 → 스킵
        stub = _StubSelf(status="LONG", pending=True, last_price=971.5)
        main._ts_scheduler_force_exit_net(stub, _D.replace(hour=15, minute=12))
        check("T3: pending 존재 → 미발화", len(rec.calls) == 0)

        # FLAT + 브로커 잔량 0 → 스킵
        stub2 = _StubSelf(status="FLAT", broker_qty=0)
        main._ts_scheduler_force_exit_net(stub2, _D.replace(hour=15, minute=12))
        check("T3: FLAT+잔량0 → 미발화", len(rec.calls) == 0)

        # FLAT이지만 브로커 잔량 캐시 > 0 (유령 잔량) → 발화
        stub3 = _StubSelf(status="FLAT", broker_qty=2, last_price=971.5)
        main._ts_scheduler_force_exit_net(stub3, _D.replace(hour=15, minute=12))
        check("T3: FLAT+브로커잔량2 → 발화 (유령 잔량 케이스)", len(rec.calls) == 1)

        # 장 마감 후 (15:36 > 15:35) → 미발화
        stub4 = _StubSelf(status="LONG", last_price=971.5)
        main._ts_scheduler_force_exit_net(stub4, _D.replace(hour=15, minute=36))
        check("T3: 장 마감 후 → 미발화", len(rec.calls) == 1)  # 직전 1건 그대로

        # 휴장일(일요일) → 미발화
        stub5 = _StubSelf(status="LONG", last_price=971.5)
        main._ts_scheduler_force_exit_net(
            stub5, datetime.datetime(2026, 8, 9, 15, 12))
        check("T3: 휴장일 → 미발화", len(rec.calls) == 1)
    _with_recorded_exit(body)


# ── D1: 유지보수 패스 ───────────────────────────────────────────────────────

_ROW = {
    "ts": "2026-08-07 14:04:00", "open": 967.72, "high": 970.28, "low": 967.72,
    "close": 969.24, "volume": 308, "bid1": 969.82, "ask1": 969.98, "oi": 93197,
    "buy_vol": 193, "sell_vol": 115, "created_at": "2026-08-07 14:04:50",
}


def test_t4_exit_triggers_with_cached_ctx_and_fresh_price():
    feats = {"atr": 1.23}
    dec = {"direction": -1, "confidence": 0.61, "min_conf": 0.5}
    stub = _StubSelf(status="LONG", last_price=971.5,
                     maint_ctx=(feats, dec, "2026-08-07 14:03:00"))
    main._ts_run_maintenance_pass(stub, _ROW)

    check("T4: exit triggers 1회 호출", len(stub.exit_calls) == 1)
    price, f, d, bar = stub.exit_calls[0]
    check("T4: 가격 = _last_pipeline_price(틱이 더 신선)", price == 971.5)
    check("T4: 캐시된 features 사용", f is feats)
    check("T4: 캐시된 decision 사용", d is dec)
    check("T4: bar에 high/low 승계 (봉중 스톱 판정용)",
          bar["high"] == 970.28 and bar["low"] == 967.72)

    # 틱 가격이 없으면 row 종가 폴백
    stub2 = _StubSelf(status="LONG", last_price=0.0,
                      maint_ctx=(feats, dec, "2026-08-07 14:03:00"))
    main._ts_run_maintenance_pass(stub2, _ROW)
    check("T4: 틱 가격 없음 → row 종가 폴백", stub2.exit_calls[0][0] == 969.24)


def test_t5_clocks_untouched():
    """🔴 핵심 — 유지보수 패스는 시계 2개를 절대 건드리지 않는다.

    _StubSelf에는 dashboard가 없다 — notify_pipeline_ran()을 시도하면
    AttributeError로 즉사한다. _last_real_pipeline_dt는 센티넬 비교.
    """
    stub = _StubSelf(status="LONG", last_price=971.5,
                     maint_ctx=({}, {}, "2026-08-07 14:03:00"))
    main._ts_run_maintenance_pass(stub, _ROW)   # dashboard 없이 통과해야 함
    check("T5: _last_real_pipeline_dt 불변", stub._last_real_pipeline_dt == "SENTINEL")
    check("T5: dashboard 미접촉 (AttributeError 없이 완주)", True)


def test_t6_flat_skips_and_ctx_missing_is_safe():
    # FLAT + pending 없음 + 잔량 0 → 청산 점검 자체를 안 함
    stub = _StubSelf(status="FLAT")
    main._ts_run_maintenance_pass(stub, _ROW)
    check("T6: FLAT+무pending+잔량0 → exit triggers 미호출", len(stub.exit_calls) == 0)

    # _maint_ctx 자체가 없어도(기동 직후 스톨) 빈 dict로 동작
    stub2 = _StubSelf(status="LONG", last_price=971.5)   # maint_ctx 미설정
    main._ts_run_maintenance_pass(stub2, _ROW)
    check("T6: ctx 없음 → 빈 dict로 exit triggers 호출",
          len(stub2.exit_calls) == 1 and stub2.exit_calls[0][1] == {})


# ── D3: 멱등 저장 ───────────────────────────────────────────────────────────

def test_t7_t8_dedupe_and_or_ignore():
    import utils.db_utils as dbu

    tmp = tempfile.mkdtemp(prefix="qdq_453_")
    db_path = os.path.join(tmp, "predictions.db")
    _orig = dbu.PREDICTIONS_DB
    try:
        dbu.PREDICTIONS_DB = db_path
        dbu.init_predictions_db()          # 빈 DB — 스키마 + UNIQUE 인덱스 생성

        # 452차 이전 상황 재현: UNIQUE 인덱스를 지우고 중복을 심는다
        con = sqlite3.connect(db_path)
        con.execute("DROP INDEX ux_pred_ts_hz")
        con.execute("DROP INDEX ux_ens_ts")
        rows = [
            # (t1,'1m') — id1 채점됨 / id2 미채점 고아  → 채점 행이 살아야 한다
            ("2026-08-04 12:06:00", "1m", 1, 0.61, 1, 1),
            ("2026-08-04 12:06:00", "1m", -1, 0.55, None, None),
            # (t2,'3m') — 둘 다 미채점 → 최소 id 생존
            ("2026-08-04 12:06:00", "3m", 1, 0.52, None, None),
            ("2026-08-04 12:06:00", "3m", 1, 0.53, None, None),
            # 단독 행 — 건드리면 안 된다
            ("2026-08-04 12:07:00", "1m", -1, 0.58, 0, 1),
        ]
        con.executemany(
            "INSERT INTO predictions (ts,horizon,direction,confidence,actual,correct)"
            " VALUES (?,?,?,?,?,?)", rows)
        con.execute("INSERT INTO ensemble_decisions (ts,direction,confidence)"
                    " VALUES ('2026-08-04 12:06:00',1,0.6)")
        con.execute("INSERT INTO ensemble_decisions (ts,direction,confidence)"
                    " VALUES ('2026-08-04 12:06:00',-1,0.5)")
        con.commit(); con.close()

        dbu.init_predictions_db()          # 인덱스 생성 실패 → 정리 → 재생성 경로

        con = sqlite3.connect(db_path)
        # T7: 그룹당 1행 + 채점 행 생존
        got = con.execute(
            "SELECT direction, actual FROM predictions "
            "WHERE ts='2026-08-04 12:06:00' AND horizon='1m'").fetchall()
        check("T7: (t1,1m) 1행만 생존", len(got) == 1)
        check("T7: 생존자는 채점된 행(actual=1)", got[0] == (1, 1))
        got3 = con.execute(
            "SELECT confidence FROM predictions "
            "WHERE ts='2026-08-04 12:06:00' AND horizon='3m'").fetchall()
        check("T7: (t1,3m) 최소 id 생존 (conf=0.52)",
              len(got3) == 1 and abs(got3[0][0] - 0.52) < 1e-9)
        check("T7: 단독 행 무변화",
              con.execute("SELECT COUNT(*) FROM predictions "
                          "WHERE ts='2026-08-04 12:07:00'").fetchone()[0] == 1)
        check("T7: victims 아카이브 보존 (2행)",
              con.execute("SELECT COUNT(*) FROM predictions_dup_archive")
              .fetchone()[0] == 2)
        check("T7: ensemble 1행 + 아카이브 1행",
              con.execute("SELECT COUNT(*) FROM ensemble_decisions").fetchone()[0] == 1
              and con.execute("SELECT COUNT(*) FROM ensemble_dup_archive")
              .fetchone()[0] == 1)
        check("T7: UNIQUE 인덱스 재생성됨",
              con.execute("SELECT COUNT(*) FROM sqlite_master WHERE name IN "
                          "('ux_pred_ts_hz','ux_ens_ts')").fetchone()[0] == 2)

        # T8: OR IGNORE — 재삽입이 기존(채점된) 행을 건드리지 못한다
        from learning.prediction_buffer import PredictionBuffer
        import learning.prediction_buffer as pb
        _orig_pb = pb.PREDICTIONS_DB
        try:
            pb.PREDICTIONS_DB = db_path
            PredictionBuffer().save_prediction(
                ts="2026-08-04 12:06:00", horizon="1m",
                direction=-1, confidence=0.99)
        finally:
            pb.PREDICTIONS_DB = _orig_pb
        after = con.execute(
            "SELECT direction, actual, confidence FROM predictions "
            "WHERE ts='2026-08-04 12:06:00' AND horizon='1m'").fetchall()
        check("T8: OR IGNORE — 행 수 불변·채점 라벨 보존",
              len(after) == 1 and after[0][0] == 1 and after[0][1] == 1)
        con.close()

        # T8b: 쓰기 4곳 전부 OR IGNORE로 전환됐는지 소스 수준 확인
        # (plain INSERT로 회귀하면 UNIQUE 인덱스 아래에서 IntegrityError로 죽는다)
        import inspect
        src = inspect.getsource(pb)
        check("T8b: predictions plain INSERT 잔존 0",
              "INSERT INTO predictions" not in src)
        check("T8b: ensemble plain INSERT 잔존 0",
              "INSERT INTO ensemble_decisions" not in src)
    finally:
        dbu.PREDICTIONS_DB = _orig


# ── D4: BarAggregator 격자 가드 ────────────────────────────────────────────

def test_t9_aggregator_duplicate_push_guard():
    from features.bar_aggregator import BarAggregator

    agg = BarAggregator()
    bar = lambda m, v: {"ts": "2026-08-07 09:%02d:00" % m, "open": 1, "high": 2,
                        "low": 0, "close": 1, "volume": v,
                        "buy_vol": v, "sell_vol": 0, "bid1": 1.0, "ask1": 1.1}
    agg.push(bar(0, 10))
    agg.push(bar(1, 20))
    # 09:01 중복 재주입 (~452차 복구가 하던 것)
    dup = agg.push(bar(1, 20))
    check("T9: 중복 push → 완성봉 없음",
          all(dup[h] is None for h in (3, 5, 10, 15, 30)))
    check("T9: 3m 버퍼 불변 (2봉 유지 — 격자 안 밀림)", len(agg._bufs[3]) == 2)

    r3 = agg.push(bar(2, 30))
    check("T9: 다음 정상 봉에서 3m 완성 (정시 경계)", r3[3] is not None)
    check("T9: 3m 거래량 = 10+20+30 (이중 합산 없음)", r3[3]["volume"] == 60)

    # reset_daily 후 같은 ts 재사용 가능 (익일 재기동 시나리오)
    agg.reset_daily()
    check("T9: reset 후 추적 ts 초기화", agg._last_push_ts is None)


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
