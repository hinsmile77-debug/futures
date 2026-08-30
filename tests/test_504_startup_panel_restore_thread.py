# -*- coding: utf-8 -*-
"""[MW0601 504차 후속] 기동 시 패널 복원 4단계 체인이 **실제로 실행되는가**.

## 무엇이 있었나 (2026-08-31 실측)

`_restore_panels_bg()`가 `threading.Thread`로 띄운 **워커 스레드**에서
`QTimer.singleShot(0, _stage1)`을 예약하고 있었다. 타이머는 **호출한 스레드에
붙는데** 그 스레드에는 Qt 이벤트 루프가 없다 — 그래서 `_stage1`이 **한 번도
발화하지 않았다.**

지문이 로그에 그대로 남아 있었다:

```
[LiveDBG] _apply 시작 (4단계 체인)          ← 매 기동마다 찍힌다
[LiveDBG] _apply update_learning …ms        ← 전 기간 로그에 단 한 줄도 없다
[LiveDBG] _apply update_efficacy …ms        ← 없다
[LiveDBG] _apply update_trend …ms           ← 없다
[LiveDBG] _apply pnl_history …ms            ← 없다
```

⇒ 기동 시 패널 4종(자가학습·효과검증·추이·**손익 추이**)이 복원된 적이 없다.
거래일에는 이후 이벤트 구동 갱신(`_record_trade_result`·`daily_close` 등)이
채워줘서 드러나지 않았고, **거래가 없는 날에만** 빈 화면으로 보였다.
게다가 각 단계의 예외는 `logger.debug`로 삼켜져 흔적도 남지 않는다.

## 지키려는 불변식

워커 스레드에서 `_restore_panels_worker()`를 돌려도 **네 단계가 전부 실행된다.**
GUI 갱신은 반드시 메인 스레드에서 일어나야 하므로(304차 access violation ·
490차 데드락), 통로는 `system._dashboard_call()`을 쓴다 — 새 기전을 만들지 않는다.

실행:
    pytest tests/test_504_startup_panel_restore_thread.py
    python tests/test_504_startup_panel_restore_thread.py
"""
import io
import os
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QObject, Qt, QThread, QTimer, pyqtSignal  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

_APP = None


def _app():
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


class _MainThreadSignal(QObject):
    """`main._DailyCloseUiSignal`의 최소 재현 — QueuedConnection 통로."""
    request = pyqtSignal(object)


class _FakeSystem(object):
    """`_restore_panels_worker`가 건드리는 표면만 흉내낸다."""

    def __init__(self, sig):
        self.ran = []
        self.threads = {}
        self._sig = sig
        outer = self

        class _Dash(object):
            def update_learning(self, v):
                outer._note("stage1_learning")

            def update_efficacy(self, v):
                outer._note("stage2_efficacy")

            def update_trend(self, v):
                outer._note("stage3_trend")

        self.dashboard = _Dash()

    def _note(self, name):
        self.ran.append(name)
        self.threads[name] = QThread.currentThread()

    # main.py:_dashboard_call 과 같은 규약 — 메인이면 즉시, 아니면 큐 경유.
    def _dashboard_call(self, fn):
        app = QApplication.instance()
        on_main = app is not None and QThread.currentThread() is app.thread()
        if on_main:
            fn()
        else:
            self._sig.request.emit(fn)

    def _gather_learning_stats(self):
        return {"a": 1}

    def _gather_efficacy_stats(self):
        return {"b": 1}

    def _gather_trend_stats(self):
        return {"c": 1}

    def _refresh_pnl_history(self):
        self._note("stage4_pnl_history")


def _run_worker_and_pump(timeout_ms=2000):
    """워커 스레드에서 복원을 시작하고 메인 이벤트 루프를 돌린다."""
    app = _app()
    sig = _MainThreadSignal()
    sig.request.connect(lambda fn: fn(), Qt.QueuedConnection)
    sysobj = _FakeSystem(sig)

    from strategy.runtime.session_recovery_service import SessionRecoveryService
    svc = SessionRecoveryService()
    threading.Thread(target=svc._restore_panels_worker,
                     args=(sysobj,), daemon=True).start()
    QTimer.singleShot(timeout_ms, app.quit)
    app.exec_()
    return sysobj


def test_all_four_stages_run_from_worker_thread():
    """🔴 핵심 회귀 — 워커 스레드에서 시작해도 4단계가 전부 실행돼야 한다.

    깨지면 기동 시 패널 4종이 다시 빈 채로 남는다(거래 없는 날에 그대로 보인다).
    """
    s = _run_worker_and_pump()
    for stage in ("stage1_learning", "stage2_efficacy",
                  "stage3_trend", "stage4_pnl_history"):
        assert stage in s.ran, "%s 미실행 — 실행된 것: %s" % (stage, s.ran)


def test_stages_run_in_order():
    """단계 순서가 유지돼야 한다 — 각 단계가 다음 단계를 예약하는 구조다."""
    s = _run_worker_and_pump()
    assert s.ran == ["stage1_learning", "stage2_efficacy",
                     "stage3_trend", "stage4_pnl_history"], s.ran


def test_gui_updates_happen_on_main_thread():
    """🔴 GUI 갱신은 **메인 스레드**여야 한다.

    워커 스레드에서 위젯을 만지면 304차는 access violation, 490차는 데드락이 났다.
    """
    app = _app()
    s = _run_worker_and_pump()
    for stage, th in s.threads.items():
        assert th is app.thread(), "%s 가 워커 스레드에서 실행됐다" % stage


def test_worker_does_not_schedule_timer_on_itself():
    """워커 스레드에서 `QTimer.singleShot`으로 체인을 시작하면 안 된다.

    그 타이머는 호출한 스레드에 붙고, 그 스레드에는 이벤트 루프가 없어 영영
    발화하지 않는다. 소스에 그 형태가 되살아나면 이 테스트가 깨진다.
    """
    import inspect
    from strategy.runtime.session_recovery_service import SessionRecoveryService
    src = inspect.getsource(SessionRecoveryService._restore_panels_worker)
    code = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
    tail = code.split("def _stage1", 1)[-1]
    kick = tail.split("_QTimer.singleShot(10, _stage2)", 1)[-1]
    assert "_QTimer.singleShot" not in kick, \
        "체인 시작이 다시 워커 스레드 타이머로 돌아갔다"
    assert "_dashboard_call" in kick, "메인 스레드 통로를 쓰지 않는다"


def test_singleshot_from_worker_thread_never_fires():
    """이 결함의 전제 자체를 고정한다 — 환경이 바뀌면 알 수 있어야 한다.

    PyQt 동작이 바뀌어 워커 타이머가 발화하게 되면 이 테스트가 깨지고,
    위 주석·DECISION_LOG의 설명이 낡았다는 신호가 된다.
    """
    app = _app()
    fired = {"main": False, "worker": False}
    QTimer.singleShot(0, lambda: fired.__setitem__("main", True))

    def worker():
        QTimer.singleShot(0, lambda: fired.__setitem__("worker", True))

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(1.0)
    QTimer.singleShot(500, app.quit)
    app.exec_()
    assert fired["main"] is True, "메인 스레드 타이머가 안 돈다 — 테스트 환경 문제"
    assert fired["worker"] is False, \
        "워커 스레드 타이머가 발화한다 — 이 결함의 전제가 바뀌었다"


# ── [MW0602 체리픽 추가] ────────────────────────────────────────────────────
def test_real_trading_system_has_dashboard_call():
    """🔴 스텁이 아니라 **실제 `TradingSystem`** 에 `_dashboard_call` 이 있어야 한다.

    위 테스트들은 `system` 을 스텁으로 넣기 때문에, 진짜 클래스에 그 메서드가
    없어도 전부 통과한다. 실제로 이 브랜치가 그 상태였다 — `_dashboard_call` 은
    v9-dev 의 490차 F-L 이 만든 것이고 여기엔 없었다. 504차 후속 fix 만 체리픽
    했다면 런타임에 AttributeError 로 기동 패널 복원이 통째로 죽었을 것이다
    (원 버그보다 나쁘다 — 원 버그는 조용히 안 도는 것이고 이건 예외다).

    소스 텍스트로 검사한다 — `import main` 은 COM/Qt 초기화를 끌고 오고,
    main.py 는 `__main__` 으로 실행되는 엔트리라 재import 가 안전하지 않다.
    """
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    assert "def _dashboard_call(self, fn)" in src, (
        "TradingSystem._dashboard_call 이 없다 — "
        "session_recovery_service 가 부르는데 없으면 AttributeError 다")
    # 통로가 실제 큐 경유인지(새 기전을 만들지 않았는지)까지 고정한다.
    _i = src.index("def _dashboard_call(self, fn)")
    _body = src[_i:_i + 2500]
    assert "_daily_close_ui_sig.request.emit(fn)" in _body,         "메인 스레드가 아닐 때 304차 후속 통로(_daily_close_ui_sig)를 쓰지 않는다"
    assert "QThread.currentThread()" in _body,         "메인 스레드 판정이 없다 — 워커에서 fn() 을 직접 부르면 데드락 계열이 된다"


if __name__ == "__main__":
    print("기동 패널 복원 체인 테스트 — QT_QPA_PLATFORM=%s"
          % os.environ.get("QT_QPA_PLATFORM"))
    _fails = 0
    _tests = [(k, v) for k, v in sorted(globals().items())
              if k.startswith("test_") and callable(v)]
    for _name, _fn in _tests:
        try:
            _fn()
            print("  [OK]   %s" % _name)
        except Exception as _e:
            _fails += 1
            print("  [FAIL] %s — %s" % (_name, _e))
    print("\n%d/%d 통과" % (len(_tests) - _fails, len(_tests)))
    sys.exit(1 if _fails else 0)
