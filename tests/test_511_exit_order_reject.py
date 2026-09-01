"""[MW0601 511차 F-17·F-19·F-21·F-22·G-6] 청산 주문 "브로커 거부" 대응 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: docs/정기점검/매일점검/MW0601-20260901-점검리포트.md 제2부-B)
────────────────────────────────────────────────────────────────────────────
2026-09-01 13:28:09~13:30:33, 하드스톱(틱) 전량청산(LONG 2계약·매도)이 브로커에서
**163회 연속 거부**됐다 — `[CybosOrder] 주문 실패 ret=0 status=-1
msg=94025모의투자 주문가능금액이 부족합니다.` 142건 + `ret=4 status=0` 21건.
그 144초 동안 손절이 실제로 작동하지 못했고, 포지션을 닫은 것은 엔진이 아니라
13:26:41에 계좌에 접수돼 있던 **외부 미체결 주문**이 13:30:50에 뒤늦게 체결된
것이었다. 즉 그 포지션은 설계된 통제가 아니라 **우연히** 닫혔다.

두 가지가 동시에 문제였다:
  ① 실패가 TRADE 로그에 한 줄도 안 남았다 — `→ 주문 전송` 167줄 중 163건 실패가
     은닉(97.6%). 계측 4원칙 ③(탈락 가시화)·④(폴백 가시화).
  ② 재시도에 상한·백오프가 없어 144초에 163회(1.13회/초)를 쐈고, 그 폭주가
     13:29:05부터 `ret=4` 21건을 **2차로** 유발했다 — 안전장치의 재시도가
     안전장치 자신의 통로를 막았다.

지키는 불변식:
  T1     거부는 TRADE 채널에 `[주문실패]`로 남는다 (F-19 — 이 사건의 핵심 결손).
  T2     연속 거부마다 백오프가 늘고, **상한이 있으며 영구 차단은 없다** (F-21).
  T3     자체 보류(-98)는 거부로 세지 않는다 — 세면 백오프가 자기 자신을 키운다.
  T4     연속 상한 도달 시 경보는 **정확히 1회** (스팸을 내면 아무도 안 본다).
  T5     조용한 시간이 창을 넘기면 연속 카운터가 리셋된다.
  T6     정상 전송 1회로 거부 연쇄가 끊긴다.
  T7     `closable_qty`는 "미측정"과 "0"을 구분한다 (계측 4원칙 ② — G-6).
  T8     ret 의미 매핑은 **로그 전용**이고 미검증 코드에 「⚠미검증」이 붙어 있다 (F-22).
  T9~T12 소스 수준 회귀 — 새 청산 경로가 훅 없이 추가되는 것을 막는다.

⚠ 이 테스트는 **주문을 내지 않는다.** 수량 축소 재시도(F-17 ②)는 아직 섀도이고,
   미체결 주문 자동 취소(F-18)는 자동조치 C등급이라 주간회의 승인 전까지 미배선이다.

실행: python tests/test_511_exit_order_reject.py   (COM/브로커 불필요)
"""

import datetime
import inspect
import io as _io
import os
import re
import sys

# 콘솔 코드페이지(cp949)에서 판정 문구의 U+2014 등이 UnicodeEncodeError를 내
# 통과한 검사에서도 죽는다 — 판정과 무관한 출력 문제이므로 여기서 못 박는다.
try:
    sys.stdout = _io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="backslashreplace", line_buffering=True
    )
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402  (~5s — 스텁 self로 _ts_* 모듈 함수를 직접 구동한다)

FAILURES = []


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("OK" if cond else "FAIL", name,
                         ("" if cond else "  ← " + str(detail))))
    if not cond:
        FAILURES.append(name)


# ── 스텁 ─────────────────────────────────────────────────────────────────────

class _StubBroker(object):
    def __init__(self, msg="94025모의투자 주문가능금액이 부족합니다."):
        self._msg = msg

    def get_last_order_error(self):
        return {"msg": self._msg, "ret": -1, "status": -1}


class _StubSelf(object):
    """TradingSystem 대역 — 거부 처리 경로가 실제로 만지는 속성만 갖는다."""

    def __init__(self):
        self.broker = _StubBroker()
        # main.TradingSystem.__init__와 같은 초기값 (계측 4원칙 ④ — getattr 폴백 금지)
        self._exit_reject_streak = 0
        self._exit_reject_kind = ""
        self._exit_reject_last_at = None
        self._exit_reject_alerted = False
        self._exit_retry_block_until = None
        self._broker_closable_qty = None
        self._broker_closable_qty_at = None


class _LogSpy(object):
    def __init__(self):
        self.trade = []
        self.system = []

    def install(self):
        self._orig = (main.log_manager.trade, main.log_manager.system)
        main.log_manager.trade = lambda m, *a, **k: self.trade.append(str(m))
        main.log_manager.system = lambda m, lv="INFO", *a, **k: self.system.append(
            (str(lv), str(m))
        )
        return self

    def restore(self):
        main.log_manager.trade, main.log_manager.system = self._orig


def _reject(s, ret=-1, kind="하드스톱(틱)", qty=2):
    main._ts_on_exit_order_reject(
        s, kind=kind, direction="LONG", qty=qty, ret=ret
    )


# ── T1. 거부가 TRADE 채널에 남는다 (F-19) ────────────────────────────────────

spy = _LogSpy().install()
try:
    s = _StubSelf()
    _reject(s)
    _hits = [m for m in spy.trade if m.startswith("[주문실패]")]
    check("T1 거부가 TRADE에 `[주문실패]`로 남는다", len(_hits) == 1, spy.trade)
    check("T1b 거부 사유 원문이 실려 있다",
          bool(_hits) and "94025" in _hits[0], _hits)
    check("T1c ret 의미가 병기된다",
          bool(_hits) and "브로커 거부" in _hits[0], _hits)
    check("T1d 청산가능수량이 '미측정'으로 표기된다(0으로 위장하지 않는다)",
          bool(_hits) and "청산가능=미측정" in _hits[0], _hits)
finally:
    spy.restore()

# ── T2. 백오프 — 늘어나되 상한이 있고 영구 차단은 없다 (F-21) ────────────────

spy = _LogSpy().install()
try:
    s = _StubSelf()
    _seen = []
    for _ in range(len(main.EXIT_REJECT_BACKOFF_SEC) + 3):
        _reject(s)
        _seen.append(round(main._ts_exit_retry_block_remaining(s), 1))
    check("T2 연속 거부가 카운트된다",
          s._exit_reject_streak == len(main.EXIT_REJECT_BACKOFF_SEC) + 3,
          s._exit_reject_streak)
    check("T2b 백오프가 단조 증가하다 상한에서 멈춘다",
          _seen == sorted(_seen) and max(_seen) <= max(main.EXIT_REJECT_BACKOFF_SEC),
          _seen)
    check("T2c 영구 차단이 아니다 — 상한이 유한하다",
          max(main.EXIT_REJECT_BACKOFF_SEC) <= 30.0,
          main.EXIT_REJECT_BACKOFF_SEC)
    # 시간이 지나면 스스로 풀린다
    s._exit_retry_block_until = datetime.datetime.now() - datetime.timedelta(seconds=1)
    check("T2d 만료되면 0을 돌려준다", main._ts_exit_retry_block_remaining(s) == 0.0)
finally:
    spy.restore()

# ── T3. 자체 보류(-98)는 거부로 세지 않는다 ──────────────────────────────────

spy = _LogSpy().install()
try:
    s = _StubSelf()
    _reject(s, ret=main.EXIT_RET_THROTTLED)
    check("T3 자체 보류는 연속 카운터를 올리지 않는다", s._exit_reject_streak == 0)
    check("T3b 자체 보류는 TRADE에 중복 기록하지 않는다",
          not [m for m in spy.trade if m.startswith("[주문실패]")], spy.trade)
finally:
    spy.restore()

# ── T4. 경보는 정확히 1회 ────────────────────────────────────────────────────

spy = _LogSpy().install()
try:
    s = _StubSelf()
    for _ in range(main.EXIT_REJECT_ALERT_STREAK + 5):
        _reject(s)
    _alerts = [m for lv, m in spy.system if m.startswith("[ExitRejectAlert]")]
    check("T4 연속 상한 도달 시 경보 1회", len(_alerts) == 1, len(_alerts))
    check("T4b 경보가 ERROR 레벨이다",
          any(lv == "ERROR" and m.startswith("[ExitRejectAlert]")
              for lv, m in spy.system))
    check("T4c 경보가 15:10 강제청산 위험을 명시한다",
          bool(_alerts) and "15:10" in _alerts[0], _alerts)
    check("T4d TRADE에도 사람이 볼 경보가 간다",
          len([m for m in spy.trade if m.startswith("[청산경보]")]) == 1, spy.trade)
    # 섀도는 에피소드당 1줄 — WARNING이면 exceptions_10m을 밀어 올려
    # 헬스 degraded를 자체 유발한다(오늘 09시대에 실제로 그 경로로 19분 차단).
    _shadow = [(lv, m) for lv, m in spy.system if m.startswith("[ExitRejectShadow]")]
    check("T4e 수량축소 섀도는 에피소드당 1줄", len(_shadow) == 1, len(_shadow))
    check("T4f 섀도는 INFO — exceptions_10m을 밀어 올리지 않는다",
          bool(_shadow) and _shadow[0][0] == "INFO", _shadow)
finally:
    spy.restore()

# ── T5. 창을 넘긴 조용한 시간 뒤에는 카운터가 리셋된다 ──────────────────────

spy = _LogSpy().install()
try:
    s = _StubSelf()
    _reject(s); _reject(s)
    s._exit_reject_last_at = (
        datetime.datetime.now()
        - datetime.timedelta(seconds=main.EXIT_REJECT_WINDOW_SEC + 5)
    )
    _reject(s)
    check("T5 창 경과 후 연속 카운터 리셋", s._exit_reject_streak == 1,
          s._exit_reject_streak)
    check("T5b 리셋되면 경보도 다시 무장된다", s._exit_reject_alerted is False)
finally:
    spy.restore()

# 다른 종류의 청산이 오면 그 연쇄는 별개다
spy = _LogSpy().install()
try:
    s = _StubSelf()
    _reject(s, kind="하드스톱(틱)"); _reject(s, kind="하드스톱(틱)")
    _reject(s, kind="15:10 강제청산")
    check("T5c 청산 종류가 바뀌면 연쇄가 새로 시작된다", s._exit_reject_streak == 1,
          s._exit_reject_streak)
finally:
    spy.restore()

# ── T6. 정상 전송 1회로 연쇄가 끊긴다 ────────────────────────────────────────

spy = _LogSpy().install()
try:
    s = _StubSelf()
    for _ in range(4):
        _reject(s)
    main._ts_reset_exit_reject_state(s, reason="테스트")
    check("T6 정상 전송이 연속 카운터를 0으로 되돌린다", s._exit_reject_streak == 0)
    check("T6b 백오프도 함께 해제된다", s._exit_retry_block_until is None)
    check("T6c 회복 사실이 TRADE에 남는다",
          any(m.startswith("[주문실패복구]") for m in spy.trade), spy.trade)
    # 회복 로그는 거부가 있었을 때만 — 평시 성공마다 찍으면 소음이 된다
    spy.trade[:] = []
    main._ts_reset_exit_reject_state(s)
    check("T6d 거부가 없었으면 회복 로그를 찍지 않는다", not spy.trade, spy.trade)
finally:
    spy.restore()

# ── T7. closable_qty — "미측정"과 "0"을 구분한다 (계측 4원칙 ② · G-6) ────────

s = _StubSelf()
check("T7 미측정이면 (None, None)", main._ts_closable_qty_snapshot(s) == (None, None))

s._broker_closable_qty = 0
s._broker_closable_qty_at = datetime.datetime.now()
_q, _age = main._ts_closable_qty_snapshot(s)
check("T7b 0은 0으로 보고된다 (미측정과 다르다)", _q == 0, _q)

s._broker_closable_qty = 2
s._broker_closable_qty_at = (
    datetime.datetime.now()
    - datetime.timedelta(seconds=main.EXIT_CLOSABLE_QTY_FRESH_SEC + 5)
)
_q, _age = main._ts_closable_qty_snapshot(s)
check("T7c 낡은 값은 미측정으로 떨어진다", _q is None, _q)
check("T7d 낡음은 경과시간을 함께 보고한다", _age is not None and _age > 0, _age)

# ── T8. ret 의미 매핑은 로그 전용이고 미검증 표기가 있다 (F-22) ──────────────

check("T8 저장소가 정의한 음수 코드는 확정 표기",
      "⚠미검증" not in main.EXIT_ORDER_RET_MEANING[-1]
      and "⚠미검증" not in main.EXIT_ORDER_RET_MEANING[-99])
check("T8b 근거 없는 양수 코드(1~4)에는 ⚠미검증이 붙어 있다",
      all("⚠미검증" in main.EXIT_ORDER_RET_MEANING[c] for c in (1, 2, 3, 4)),
      {c: main.EXIT_ORDER_RET_MEANING[c] for c in (1, 2, 3, 4)})
_src_all = inspect.getsource(main)
check("T8c ret 의미 매핑이 제어 흐름에 쓰이지 않는다 (로그 전용)",
      len(re.findall(r"EXIT_ORDER_RET_MEANING", _src_all)) == 2,
      re.findall(r".*EXIT_ORDER_RET_MEANING.*", _src_all))

# ── T9~T12. 소스 수준 회귀 — 훅 없는 청산 경로가 새로 생기는 것을 막는다 ────

_send_src = inspect.getsource(main.TradingSystem._send_broker_exit_order)
check("T9 _send_broker_exit_order에 throttle 스위치가 있다",
      "throttle: bool = True" in _send_src, _send_src[:200])
check("T9b 보류 시 브로커로 나가지 않고 -98을 돌려준다",
      "return EXIT_RET_THROTTLED" in _send_src)
check("T9c 정상 전송이 거부 상태를 리셋한다",
      "_ts_reset_exit_reject_state" in _send_src)

_tick_src = inspect.getsource(main.TradingSystem._process_tick_stop)
_gate_at = _tick_src.find("_ts_exit_retry_block_remaining")
_pend_at = _tick_src.find("_set_pending_order")
check("T10 틱 하드스톱에 백오프 게이트가 있다", _gate_at >= 0)
check("T10b 게이트가 pending 등록보다 **앞**이다 "
      "(뒤면 호출자 ERROR가 exceptions_10m을 밀어 올린다)",
      0 <= _gate_at < _pend_at, (_gate_at, _pend_at))

_force_src = inspect.getsource(main._ts_check_exit_triggers)
check("T11 15:10 시간청산은 자체 백오프를 **면제**받는다 (절대원칙 §1)",
      "self._send_broker_exit_order(_force_qty, throttle=False)" in _force_src)
check("T11b 시간청산 실패도 거부 훅을 탄다",
      'kind="15:10 강제청산"' in _force_src)

# 실패를 SYSTEM에만 남기고 TRADE에 안 남기던 것이 이 사건의 핵심 결손이었다.
# 청산 주문 실패를 로깅하는 모든 지점이 거부 훅을 함께 부르는지 소스로 못 박는다.
_fail_sites = re.findall(
    r"log_manager\.system\(\s*\n?\s*f?\"\[(?:Exit|ManualExit)\][^\"]*주문 실패[^\"]*\"",
    _src_all,
)
_hook_calls = len(re.findall(r"_ts_on_exit_order_reject\(\s*\n?\s*self,", _src_all))
check("T12 청산 실패 로깅 지점이 7곳 그대로다 (새 경로가 생기면 이 테스트가 깨진다)",
      len(_fail_sites) == 7, len(_fail_sites))
check("T12b 거부 훅 호출이 그 이상이다 (BrokerDirectExit 포함 8곳)",
      _hook_calls >= 8, _hook_calls)

# ── T13. 런타임 스모크 — 모듈 전역 조회가 실제로 걸린다 ──────────────────────
# T9~T12는 소스 문자열만 본다. 헬퍼가 클래스 정의보다 **뒤에** 있으므로
# "이름은 있는데 런타임에 NameError"가 나는 실수는 소스 검사로 안 잡힌다.
# 백오프 게이트를 실제로 태워서 확인한다(주문은 나가지 않는다).

class _SmokeSelf(_StubSelf):
    def __init__(self):
        _StubSelf.__init__(self)
        self._tick_stop_triggered = True
        self._tick_stop_price = 1073.00
        self._set_pending_called = []

    def _set_pending_order(self, **kw):      # 여기까지 오면 게이트가 안 걸린 것
        self._set_pending_called.append(kw)


_sm = _SmokeSelf()
_sm._exit_retry_block_until = datetime.datetime.now() + datetime.timedelta(seconds=5)
try:
    main.TradingSystem._process_tick_stop(_sm)
    _smoke_ok, _smoke_err = True, ""
except Exception as _e:                       # NameError 등
    _smoke_ok, _smoke_err = False, repr(_e)
check("T13 백오프 중 틱 하드스톱이 예외 없이 보류된다", _smoke_ok, _smoke_err)
check("T13b 보류 시 pending을 등록하지 않는다 (주문이 나가지 않는다)",
      _sm._set_pending_called == [], _sm._set_pending_called)
check("T13c 보류해도 트리거 플래그는 해제된다 (멱등 계약 유지)",
      _sm._tick_stop_triggered is False)

print("")
if FAILURES:
    print("FAILED %d: %s" % (len(FAILURES), FAILURES))
    sys.exit(1)
print("ALL PASS (%s)" % os.path.basename(__file__))
