# -*- coding: utf-8 -*-
"""[MW0602 494차] F-4 · F-10 회귀 — 크래시 서명 영속화 + BlockRequest 재진입 계측.

**왜 이 테스트가 필요한가.**

F-10 은 *"회전으로 사라지는 크래시 증거를 남긴다"* 는 계측이다. 계측이 조용히 죽는
것이 이 저장소가 반복해서 겪은 사고다 — FP-CRITICAL 은 학습분포 저장 함수가 한 번도
호출되지 않아 2개월간 PSI=0.0 고정이었고, TOX-SEVERE-SPREAD 는 `spread_extreme_shadow`
를 매분 계산하면서 **아무 데도 남기지 않아** 한 달 넘게 죽은 섀도였다.
그래서 여기서 고정하는 불변식은 두 가지다:

  ① **회전이 삭제하기 전에** 서명이 추출된다 (순서가 뒤집히면 증거가 먼저 지워진다)
  ② **같은 블록을 두 번 세지 않고, 진짜 반복은 접지 않는다**
     (내용 해시만으로 접으면 "얼마나 자주 있는 일인가"를 잃는다 — 그것이 이 파일의 존재 이유다)

F-4③ 은 뜨거운 COM 경로에 붙는 계측이라 **깊이 되돌리기**가 불변식이다. 타임아웃·예외
경로에서 깊이를 되돌리지 않으면 이후 모든 호출이 `reentrant=True` 로 오탐된다.

실행:
    py37_32\\python.exe -m pytest tests/test_494_crash_signature_and_blockreq.py -q
    py310_64\\python.exe -m pytest tests/test_494_crash_signature_and_blockreq.py -q
"""
import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ─────────────────────────────────────────────────────────── main.py 헬퍼 추출
def _load_main_helpers():
    """main.py 를 통째로 import 하지 않고 크래시 로그 헬퍼 2종만 얻는다.

    main.py 는 Cybos COM 을 임포트하므로 통째 로드가 불가능하다(test_436 과 같은 관례).
    함수 **소스 텍스트 그대로** 컴파일하므로 배포 코드와 동일한 것을 검증한다.
    """
    with io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        lines = f.readlines()

    def _grab(name):
        start = None
        for i, ln in enumerate(lines):
            if ln.startswith("def %s(" % name):
                start = i
                break
        assert start is not None, "main.py에서 %s를 찾지 못했다" % name
        end = start + 1
        while end < len(lines) and not lines[end].startswith("def "):
            end += 1
        return "".join(lines[start:end])

    class _Log(object):
        def __init__(self):
            self.lines = []

        def _rec(self, fmt, *a):
            try:
                self.lines.append(fmt % a if a else fmt)
            except Exception:
                self.lines.append(str(fmt))

        info = warning = debug = error = _rec

    class _Settings(object):
        CRASH_LOG_ROTATE_MB = 1
        CRASH_LOG_KEEP_GENERATIONS = 3

    log = _Log()
    ns = {"os": os, "logger": log, "runtime_settings": _Settings()}
    # 모듈 상수도 **소스에서** 가져온다 — 테스트가 값을 자체 정의하면 배포 코드의
    # 상수가 바뀌어도 테스트는 계속 통과한다(그 순간 이 테스트가 죽는다).
    consts = [ln for ln in lines if ln.startswith(("CRASH_SIG_", "_CRASH_SIG_"))]
    assert consts, "main.py에서 CRASH_SIG_* 상수를 찾지 못했다"
    exec(compile("".join(consts), "main.py:const", "exec"), ns)
    exec(compile(_grab("_persist_crash_signatures"), "main.py:sig", "exec"), ns)
    exec(compile(_grab("_rotate_crash_log"), "main.py:rot", "exec"), ns)
    return ns["_persist_crash_signatures"], ns["_rotate_crash_log"], log


_BLOCK = (
    "Windows fatal exception: access violation\n"
    "\n"
    "Current thread 0x0000412c (most recent call first):\n"
    '  File "C:\\x\\dashboard\\main_dashboard.py", line 7536 in _insert_html_left\n'
    '  File "C:\\x\\dashboard\\main_dashboard.py", line 7583 in append\n'
    '  File "C:\\x\\main.py", line 659 in <lambda>\n'
    '  File "C:\\x\\lib\\threading.py", line 890 in _bootstrap\n'
    "\n"
    "Thread 0x0000411c (most recent call first):\n"
    '  File "C:\\x\\lib\\queue.py", line 179 in get\n'
)


def _write(path, n_blocks, pad_lines=0, tag="x"):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("[START] 2026-08-25T09:00:00  PID=1  Python 3.7.9 32bit\n")
        for _ in range(pad_lines):
            f.write("Timeout (0:00:30)! %s\n" % tag)
        for _ in range(n_blocks):
            f.write(_BLOCK)


# ────────────────────────────────────────────────────────────────── F-10 검증
def test_signatures_extracted_and_deduped():
    """블록을 뽑고, 재실행해도 중복 append 하지 않는다."""
    persist, _, _log = _load_main_helpers()
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "crash_fault.log")
        out = os.path.join(d, "crash_signatures.log")
        _write(base, 2)

        assert persist(base, 3, out) == 2
        body = io.open(out, encoding="utf-8").read()
        assert body.count("[SIG] ") == 2
        assert "exc=access violation" in body
        assert "_insert_html_left" in body
        # 최상단 3프레임만 남긴다 — 4번째(_bootstrap)는 잘라낸다
        assert "_bootstrap" not in body

        # 같은 파일을 다시 훑어도 새로 붙지 않는다
        assert persist(base, 3, out) == 0
        assert io.open(out, encoding="utf-8").read() == body


def test_repeat_crashes_are_not_collapsed():
    """같은 내용의 크래시가 2번 나면 2건으로 남는다 — 빈도가 이 파일의 목적이다."""
    persist, _, _ = _load_main_helpers()
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "crash_fault.log")
        out = os.path.join(d, "crash_signatures.log")
        _write(base, 3)
        assert persist(base, 3, out) == 3


def test_rotation_preserves_oldest_generation_signatures():
    """🔴 핵심 불변식 — 회전이 **지우기 전에** 추출한다."""
    persist, rotate, _ = _load_main_helpers()
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "crash_fault.log")
        out = os.path.join(d, "crash_signatures.log")
        # keep=3 이므로 `.log.3` 이 이번 회전에서 삭제된다. 그 안에 블록 2개를 둔다.
        _write(base + ".3", 2, tag="oldest")
        _write(base, 0, pad_lines=90000)   # 회전 임계(1MB) 초과용 패딩

        assert os.path.getsize(base) > 1 * 1024 * 1024
        n = rotate(base, rotate_mb=1, keep=3)
        assert n > 0, "회전이 일어나야 한다"
        assert not os.path.exists(base + ".3") or os.path.getsize(base + ".3") > 0

        # 회전 시 호출되는 경로는 기본 out_path(logs 동급 디렉터리)를 쓰므로
        # 여기서는 삭제 전에 추출됐는지를 같은 디렉터리 산출물로 확인한다.
        default_out = os.path.join(d, "crash_signatures.log")
        assert os.path.exists(default_out), "회전 경로가 서명을 남기지 않았다"
        body = io.open(default_out, encoding="utf-8").read()
        assert body.count("[SIG] ") == 2, body
        assert out == default_out


def test_persist_never_raises_on_missing_files():
    """원본이 없어도 예외를 올리지 않는다 — 로그 위생이 기동을 막을 수 없다."""
    persist, _, _ = _load_main_helpers()
    with tempfile.TemporaryDirectory() as d:
        assert persist(os.path.join(d, "nope.log"), 3,
                       os.path.join(d, "sig.log")) == 0


# ────────────────────────────────────────────────────────────────── F-4③ 검증
def _blockreq_mod():
    """COM 의존 없이 api_connector 의 재진입 계측 3종만 뽑아 컴파일한다."""
    import logging
    import threading
    import time

    with io.open(os.path.join(_ROOT, "collection", "cybos", "api_connector.py"),
                 encoding="utf-8") as f:
        lines = f.readlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("BLOCK_REQ_SAMPLE_SEC"):
            start = i
            break
    assert start is not None
    end = start
    while end < len(lines) and not lines[end].startswith("def _run_block_request("):
        end += 1
    ns = {"threading": threading, "time": time, "logging": logging}
    exec(compile("".join(lines[start:end]), "api_connector:blockreq", "exec"), ns)
    return ns


def test_reentrancy_detected_and_depth_restored():
    mod = _blockreq_mod()
    enter, leave = mod["_blockreq_enter"], mod["_blockreq_exit"]
    st = mod["_blockreq_state"]

    r1, d1 = enter("A")
    assert (r1, d1) == (False, 1)
    r2, d2 = enter("B")          # 겹쳐 들어옴
    assert (r2, d2) == (True, 2)
    leave(1.0)
    leave(1.0)
    assert st["depth"] == 0, "깊이가 되돌아오지 않으면 이후 전부 오탐이 된다"
    assert st["reentrant"] == 1
    assert st["max_depth"] == 2


def test_sample_line_is_unconditional():
    """재진입이 0이어도 창이 만료되면 집계 1줄이 나온다 — 분모가 남아야 한다.

    조건부 로그(재진입 시에만 출력)로 만들면 100% 고착이 구조적으로 보장돼
    §12 고착 감시 대상이 될 수 없다(CLAUDE.md 468차 G-2 규약).
    """
    import time

    mod = _blockreq_mod()
    enter, leave = mod["_blockreq_enter"], mod["_blockreq_exit"]
    st = mod["_blockreq_state"]

    captured = []

    class _Obs(object):
        def info(self, fmt, *a):
            captured.append(fmt % a if a else fmt)

        def warning(self, *a, **k):
            pass

    mod["_obs"] = _Obs()
    mod["BLOCK_REQ_SAMPLE_SEC"] = 0.0     # 창을 즉시 만료시킨다

    enter("A")
    st["window_t0"] = time.time() - 1.0
    leave(12.0)

    assert captured, "재진입 0 이어도 SAMPLE 줄이 나와야 한다"
    line = captured[0]
    assert "state=SAMPLE" in line
    assert "calls=1" in line and "reentrant=0" in line
    assert st["window_t0"] is None, "창이 리셋돼야 다음 창이 겹치지 않는다"


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _failures = []
    for _fn in (test_signatures_extracted_and_deduped,
                test_repeat_crashes_are_not_collapsed,
                test_rotation_preserves_oldest_generation_signatures,
                test_persist_never_raises_on_missing_files,
                test_reentrancy_detected_and_depth_restored,
                test_sample_line_is_unconditional):
        try:
            _fn()
            print("[ok]   %s" % _fn.__name__)
        except Exception as _e:
            print("[FAIL] %s: %r" % (_fn.__name__, _e))
            _failures.append(_fn.__name__)
    print("-" * 60)
    print("전부 통과" if not _failures else "실패 %d건: %s" % (len(_failures), _failures))
    sys.exit(1 if _failures else 0)
