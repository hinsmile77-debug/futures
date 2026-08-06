# -*- coding: utf-8 -*-
"""[MW0602 436차] crash_fault.log 로테이션 회귀 테스트.

왜 이 테스트가 필요한가 — 로테이션은 **삭제를 하는** 코드다. 세대를 미는 순서가
뒤집히면(`.1`→`.2` 전에 `.2`→`.3`를 안 하면) `.1`이 `.2`를 덮어써 조용히 세대가
사라진다. 크래시 조사용 로그가 조용히 사라지는 것은 로그가 큰 것보다 나쁘다.

실행:
    py37_32\\python.exe -m pytest tests/test_436_crash_log_rotation.py -q
    py310_64\\python.exe -m pytest tests/test_436_crash_log_rotation.py -q
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _rot():
    """main.py를 통째로 import하지 않고 헬퍼만 얻는다(COM 의존 회피)."""
    import importlib.util
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "main.py")
    # main.py는 Cybos COM을 임포트하므로 통째 로드가 불가능하다. 함수 소스만 뽑아
    # 독립 네임스페이스에서 컴파일한다 — 실제 배포 코드와 **같은 텍스트**를 검증한다.
    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("def _rotate_crash_log("):
            start = i
            break
    assert start is not None, "main.py에서 _rotate_crash_log를 찾지 못했다"
    end = start + 1
    while end < len(lines) and not lines[end].startswith("def "):
        end += 1
    body = "".join(lines[start:end])

    class _Log(object):
        def info(self, *a, **k):
            pass

        def warning(self, *a, **k):
            pass

    class _Settings(object):
        CRASH_LOG_ROTATE_MB = 8
        CRASH_LOG_KEEP_GENERATIONS = 4

    ns = {"os": os, "logger": _Log(), "runtime_settings": _Settings()}
    exec(compile(body, "main.py:_rotate_crash_log", "exec"), ns)
    return ns["_rotate_crash_log"]


def _mk(path, mb, tag):
    with open(path, "wb") as f:
        f.write(tag.encode("ascii") * (mb * 1024 * 1024 // len(tag)))


def test_under_threshold_does_not_rotate():
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "crash_fault.log")
        _mk(p, 1, "AAAA")
        assert _rot()(p, rotate_mb=8, keep=4) == 0
        assert os.path.exists(p) and not os.path.exists(p + ".1")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_rotation_preserves_generation_order():
    """핵심 — 세대가 밀리기만 하고 덮어써지지 않는지."""
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "crash_fault.log")
        _mk(p, 9, "BASE")          # 임계 초과
        for g, tag in ((1, "GEN1"), (2, "GEN2"), (3, "GEN3")):
            _mk("%s.%d" % (p, g), 1, tag)
        assert _rot()(p, rotate_mb=8, keep=4) > 0
        # base는 사라지고(다시 열릴 것), 세대가 하나씩 밀렸어야 한다
        assert not os.path.exists(p), "회전 후 base가 남아 있으면 안 된다"
        for g, tag in ((1, "BASE"), (2, "GEN1"), (3, "GEN2"), (4, "GEN3")):
            f = "%s.%d" % (p, g)
            assert os.path.exists(f), "%s 세대가 사라졌다" % f
            with open(f, "rb") as fh:
                assert fh.read(4) == tag.encode("ascii"), \
                    "%s 내용이 %s가 아니다 — 세대 순서가 뒤집혔다" % (f, tag)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_oldest_generation_is_dropped():
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "crash_fault.log")
        _mk(p, 9, "BASE")
        for g in range(1, 5):
            _mk("%s.%d" % (p, g), 1, "GEN%d" % g)
        _rot()(p, rotate_mb=8, keep=4)
        assert not os.path.exists("%s.5" % p), "keep을 넘는 세대가 생기면 안 된다"
        with open("%s.4" % p, "rb") as fh:
            assert fh.read(4) == b"GEN3", "가장 오래된 GEN4가 밀려나지 않았다"
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_killswitch_disables_rotation():
    """0 이하 = 230차 원래 동작(무한 append)."""
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "crash_fault.log")
        _mk(p, 9, "BASE")
        assert _rot()(p, rotate_mb=0, keep=4) == 0
        assert _rot()(p, rotate_mb=8, keep=0) == 0
        assert os.path.exists(p) and not os.path.exists(p + ".1")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_missing_file_is_safe():
    d = tempfile.mkdtemp()
    try:
        assert _rot()(os.path.join(d, "nope.log"), rotate_mb=8, keep=4) == 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    for fn in (test_under_threshold_does_not_rotate,
               test_rotation_preserves_generation_order,
               test_oldest_generation_is_dropped,
               test_killswitch_disables_rotation,
               test_missing_file_is_safe):
        fn()
        print("OK  %s" % fn.__name__)
    print("전부 통과")
