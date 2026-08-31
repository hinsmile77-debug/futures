# -*- coding: utf-8 -*-
"""[MW0601 506차 F-6] Restart Armistice 해제 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
이 사고의 지문을 회귀로 박는다 (2026-08-31)
────────────────────────────────────────────────────────────────────────────
금요일 이월 LONG 4계약 때문에 기동 시 브로커 잔고가 non-blank(`all_blank_rows=False`)
였다. `_restart_armistice_sync_count` 를 올리는 경로는 그때 실질 2개뿐이었고,

  · `= 2`  — `_ts_sync_position_from_broker()` blank-as-flat 확정.
             **잔고가 비어 있을 때만** 실행 → 이날 미진입.
  · `+= 1` — `_ts_manual_position_restore()`. 대시보드 **수동** 복원 전용,
             자동 호출자 없음 → 이날 미실행.

둘 다 도달하지 못해 카운터가 **0에 고정**됐고, `_armistice_sync_ok = (0 >= 2)` 가
영원히 False라 09:21~15:08 **47분 전 구간** 자동진입이 막혔다. 그날 비X 등급
후보 16분이 **16/16** `armistice_ok=False` 였고, 그중 5분(13:22·14:03·14:11·
14:13·14:14)은 Armistice가 **단독** 차단 사유였다. 08:45 하드스톱으로 FLAT이
된 뒤에도 startup sync는 기동 시 1회뿐이라 재평가 기회가 없었다.

증상이 조용했던 것도 핵심이다 — `[차단] Restart Armistice` **INFO** 한 줄뿐이라
하루를 통째로 잃고도 경보가 없었다(계측 4원칙 ④).

대조군: 08-25~08-28 4거래일은 매일 `armistice cleared` 1건 · 차단 0건.
이 4일은 기동 시 잔고가 비어 있어 blank-as-flat 경로를 탔다.

지키는 불변식:
  T1  브로커 sync 검증 완료 + 90초 경과  → 해제 (정방향)
  T2  브로커 sync 미검증                → 시간이 지나도 **미해제** (역방향)
  T3  🔴 90초 시간 조건 AND 유지 — sync가 좋아도 90초 전에는 해제되지 않는다.
      이게 풀리면 P1-a 원목적(재시작 직후 브로커 상태 미확인 진입 차단)이 죽는다.
  T4  2026-08-31 재현 — non-blank 기동(카운터 0)이어도 해제된다.
      종전 코드였으면 종일 True.
  T5  개장 30분 초과 고착 시 ERROR 발화 + 5분 스로틀
  T6  승격 WARNING은 세션당 1회
  T7  `block_new_entries=True` 면 승격하지 않는다(브로커가 나쁠 때 문을 열지 않는다)
  T8  소스 불변식 — 승격 조건에서 `time_ok` 가 빠지면 즉시 실패

실행: python tests/test_506_armistice_release.py   (COM/브로커 불필요)
"""

import datetime
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402  (~5s — 스텁 self로 _ts_evaluate_armistice()를 직접 구동한다)

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


# ── 스텁 ─────────────────────────────────────────────────────────────────────

class _StubSelf(object):
    """TradingSystem 대역 — _ts_evaluate_armistice()가 실제로 만지는 속성만 갖는다.

    ⚠ `getattr(self, "_x", 기본값)` 로 읽지 않는다 — 속성이 빠지면 AttributeError로
      터져야 한다(계측 4원칙 ④: 조용한 폴백 금지). 이름이 바뀌면 이 테스트가 깨진다.
    """

    def __init__(self, started_at, sync_count=0,
                 verified=False, block_new_entries=True):
        # __init__ 이 now+90s 로 세우는 값을 시각으로 고정
        self._restart_armistice_until = started_at + datetime.timedelta(seconds=90)
        self._restart_armistice_sync_count = sync_count
        self._armistice_promoted_logged = False
        self._armistice_stuck_last_log = None
        self._broker_sync_verified = verified
        self._broker_sync_block_new_entries = block_new_entries


class _LogSpy(object):
    """log_manager.system 대역 — (메시지, 레벨) 수집."""

    def __init__(self):
        self.records = []

    def system(self, msg, level="INFO", **_kw):
        self.records.append((msg, level))

    def levels(self, level):
        return [m for m, lv in self.records if lv == level]


def _run(stub, now_dt, spy=None):
    """log_manager를 스파이로 갈아끼우고 1분 평가."""
    spy = spy or _LogSpy()
    orig = main.log_manager
    main.log_manager = spy
    try:
        time_ok, in_armistice = main._ts_evaluate_armistice(stub, now_dt)
    finally:
        main.log_manager = orig
    return time_ok, in_armistice, spy


_OPEN = datetime.datetime(2026, 8, 31, 8, 40, 57)   # 실제 기동 시각(08-31 마지막 재기동)


# ── T1: 정방향 ───────────────────────────────────────────────────────────────

def test_t1_release_after_90s_when_sync_verified():
    stub = _StubSelf(_OPEN, sync_count=0, verified=True, block_new_entries=False)
    time_ok, in_arm, spy = _run(stub, _OPEN + datetime.timedelta(seconds=91))
    check("T1: 90초 경과 → time_ok", time_ok is True)
    check("T1: 브로커 sync 정상 → 유예 해제", in_arm is False)
    check("T1: 카운터 2로 승격", stub._restart_armistice_sync_count == 2)
    warns = spy.levels("WARNING")
    check("T1: 승격 WARNING 1회", len(warns) == 1)
    check("T1: WARNING에 승격 근거 명시(계측 4원칙 ④)",
          warns and "sync 0→2 승격" in warns[0])


# ── T2: 역방향 — sync 미검증이면 시간이 지나도 안 풀린다 ──────────────────────

def test_t2_no_release_when_sync_unverified():
    # verified=False (기본 초기값) — 브로커 응답을 아직 못 믿는 상태
    stub = _StubSelf(_OPEN, sync_count=0, verified=False, block_new_entries=True)
    _, in_arm, _ = _run(stub, _OPEN + datetime.timedelta(hours=3))
    check("T2: sync 미검증이면 3시간 지나도 미해제", in_arm is True)
    check("T2: 카운터 승격 안 됨", stub._restart_armistice_sync_count == 0)


# ── T3: 🔴 90초 시간 조건은 AND로 유지된다 ───────────────────────────────────

def test_t3_time_condition_is_and_not_or():
    """이게 깨지면 P1-a 원목적이 죽는다 — 재시작 직후 브로커 상태 미확인 진입 차단."""
    stub = _StubSelf(_OPEN, sync_count=0, verified=True, block_new_entries=False)
    time_ok, in_arm, spy = _run(stub, _OPEN + datetime.timedelta(seconds=30))
    check("T3: 30초 시점 → time_ok False", time_ok is False)
    check("T3: sync가 좋아도 90초 전에는 유예 유지", in_arm is True)
    check("T3: 90초 전에는 승격도 하지 않는다",
          stub._restart_armistice_sync_count == 0)
    check("T3: 90초 전 승격 WARNING 없음", spy.levels("WARNING") == [])

    # 그리고 90초를 넘기면 그제서야 풀린다
    _, in_arm2, _ = _run(stub, _OPEN + datetime.timedelta(seconds=120))
    check("T3: 120초 시점에는 해제", in_arm2 is False)


# ── T4: 2026-08-31 사고 재현 ─────────────────────────────────────────────────

def test_t4_incident_20260831_nonblank_startup_releases():
    """이월 포지션 때문에 blank-as-flat 경로를 못 탄 기동 — 종전엔 종일 차단.

    실제 로그: 08:41:05 `[BrokerSync] startup sync raw rows=1 nonempty_rows=1
    all_blank_rows=False` → `= 2` 미실행, `[PositionRestore]` 0건 → `+= 1` 미실행.
    그래서 sync_count=0. 그런데 같은 시각 `[BrokerSync] status verified=True
    block_new_entries=False reason=synced LONG 4 @ 1068.47` 은 찍혀 있었다 —
    **승격에 필요한 정보는 처음부터 다 있었고 아무도 안 봤다.**
    """
    stub = _StubSelf(_OPEN, sync_count=0,          # blank-as-flat 미진입
                     verified=True,                # 실제 로그 그대로
                     block_new_entries=False)
    # 그날 첫 차단이 찍힌 시각
    _, in_arm, _ = _run(stub, datetime.datetime(2026, 8, 31, 9, 21, 0))
    check("T4: non-blank 기동이어도 09:21에는 해제돼 있어야 한다", in_arm is False)

    # 그날 Armistice 단독 차단 5분 — 전부 진입 가능해야 한다
    blocked_minutes = [(13, 22), (14, 3), (14, 11), (14, 13), (14, 14)]
    still_blocked = []
    for hh, mm in blocked_minutes:
        _, ia, _ = _run(stub, datetime.datetime(2026, 8, 31, hh, mm, 0))
        if ia:
            still_blocked.append("%02d:%02d" % (hh, mm))
    check("T4: 단독 차단 5분이 모두 열린다 (막힌 분: %s)" % (still_blocked or "없음"),
          not still_blocked)


# ── T5: 고착 경보 + 스로틀 ───────────────────────────────────────────────────

def test_t5_stuck_error_after_open_plus_30min():
    # sync 미검증 → 계속 고착되는 상태
    stub = _StubSelf(_OPEN, sync_count=0, verified=False, block_new_entries=True)

    # 09:29 — 아직 임계(09:30) 전이면 ERROR 없음
    _, _, spy = _run(stub, datetime.datetime(2026, 8, 31, 9, 29, 0))
    check("T5: 09:29에는 ERROR 없음(임계 전)", spy.levels("ERROR") == [])

    # 09:31 — 첫 ERROR
    _, in_arm, spy = _run(stub, datetime.datetime(2026, 8, 31, 9, 31, 0))
    check("T5: 여전히 고착", in_arm is True)
    errs = spy.levels("ERROR")
    check("T5: 09:31 ERROR 1회 발화", len(errs) == 1)
    check("T5: ERROR에 진단 축이 실린다",
          errs and "sync=0/2" in errs[0] and "broker_verified=False" in errs[0])

    # 09:33 — 5분 스로틀 안이라 침묵
    _, _, spy = _run(stub, datetime.datetime(2026, 8, 31, 9, 33, 0))
    check("T5: 2분 뒤는 스로틀로 침묵", spy.levels("ERROR") == [])

    # 09:36 — 스로틀 경과 → 재발화
    _, _, spy = _run(stub, datetime.datetime(2026, 8, 31, 9, 36, 0))
    check("T5: 5분 경과 후 재발화", len(spy.levels("ERROR")) == 1)


def test_t5b_no_stuck_error_when_released():
    """해제된 세션은 09:30 이후에도 조용해야 한다 — 오탐이 나면 아무도 안 본다."""
    stub = _StubSelf(_OPEN, sync_count=0, verified=True, block_new_entries=False)
    _, in_arm, spy = _run(stub, datetime.datetime(2026, 8, 31, 11, 0, 0))
    check("T5b: 해제 상태", in_arm is False)
    check("T5b: 고착 ERROR 없음", spy.levels("ERROR") == [])


# ── T6: 승격 로그 1회 ────────────────────────────────────────────────────────

def test_t6_promotion_logged_once_per_session():
    stub = _StubSelf(_OPEN, sync_count=0, verified=True, block_new_entries=False)
    spy = _LogSpy()
    for i in range(5):
        _run(stub, _OPEN + datetime.timedelta(seconds=100 + i * 60), spy=spy)
    check("T6: 5분 반복 평가에도 승격 WARNING 1회", len(spy.levels("WARNING")) == 1)

    # 외부에서 카운터를 되돌려도 로그는 다시 찍지 않는다(폭주 방지)
    stub._restart_armistice_sync_count = 0
    spy2 = _LogSpy()
    _run(stub, _OPEN + datetime.timedelta(seconds=500), spy=spy2)
    check("T6: 카운터 되돌림 후 재승격되지만 로그는 침묵",
          stub._restart_armistice_sync_count == 2
          and spy2.levels("WARNING") == [])


# ── T7: 브로커가 나쁘면 문을 열지 않는다 ─────────────────────────────────────

def test_t7_no_promotion_when_block_new_entries():
    stub = _StubSelf(_OPEN, sync_count=0,
                     verified=True,             # 검증은 됐지만
                     block_new_entries=True)    # 진입은 막힌 상태(계좌 불일치 등)
    _, in_arm, _ = _run(stub, _OPEN + datetime.timedelta(hours=2))
    check("T7: block_new_entries=True면 승격 안 함",
          stub._restart_armistice_sync_count == 0)
    check("T7: 유예 유지", in_arm is True)


# ── T8: 소스 불변식 ──────────────────────────────────────────────────────────

def test_t8_source_invariants():
    """🔴 조건이 조용히 느슨해지는 것을 막는다."""
    src = inspect.getsource(main._ts_evaluate_armistice)

    check("T8: 승격 조건에 time_ok 포함", "and time_ok" in src)
    check("T8: 승격 조건에 _broker_sync_verified is True 포함",
          "self._broker_sync_verified is True" in src)
    check("T8: 승격 조건에 _broker_sync_block_new_entries is False 포함",
          "self._broker_sync_block_new_entries is False" in src)
    check("T8: 판정은 time_ok AND sync_ok",
          "not (time_ok and sync_ok)" in src)

    # 호출부가 살아 있는가 — 함수만 남고 배선이 빠지면 아무 의미가 없다
    caller = inspect.getsource(main.TradingSystem)
    check("T8: 파이프라인이 _ts_evaluate_armistice를 호출",
          "_ts_evaluate_armistice(self, _now_dt)" in caller)

    # __init__ 이 상태변수를 명시 초기화하는가 (계측 4원칙 ④ — getattr 폴백 금지)
    init_src = inspect.getsource(main.TradingSystem.__init__)
    check("T8: __init__ 이 _armistice_promoted_logged 초기화",
          "self._armistice_promoted_logged" in init_src)
    check("T8: __init__ 이 _armistice_stuck_last_log 초기화",
          "self._armistice_stuck_last_log" in init_src)


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
