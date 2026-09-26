# -*- coding: utf-8 -*-
"""[MW0601 631차] 자동로그인 — F-6(살아 있는 세션 보호) · F-7(종료 실패 가시화) · F-8(줄별 시각).

모듈을 import 하면 stdout 을 진단 로그로 돌리고 win32 를 요구하므로, 소스에서
필요한 부분만 떼어 검사한다.
"""
import io
import os
import tempfile

_SRC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "scripts", "cybos_autologin.py")
_SRC = io.open(_SRC_PATH, encoding="utf-8").read()


def _tee_class():
    seg = _SRC[_SRC.index("class _TeeStream"):_SRC.index("_DIAG_LOG = os.path.join")]
    ns = {"io": io, "os": os}
    exec(seg, ns)
    return ns["_TeeStream"]


class _Null(object):
    def write(self, d):
        pass

    def flush(self):
        pass


def test_diag_lines_are_timestamped_even_across_partial_writes():
    p = os.path.join(tempfile.mkdtemp(), "d.log")
    t = _tee_class()(_Null(), p)
    t.write("[INFO] a\n")
    t.write("part1 ")
    t.write("part2\nline3\n")
    t._f.close()
    lines = io.open(p, encoding="utf-8").read().splitlines()
    assert len(lines) == 3
    for ln in lines:
        assert ln[2] == ":" and ln[5] == ":" and ln[8] == " ", ln
    assert lines[1].endswith("part1 part2"), "부분 쓰기 중간에 시각이 끼면 안 된다"


def test_retry_checks_connection_before_killing():
    loop = _SRC[_SRC.index("for attempt in range(MAX_LOGIN_ATTEMPTS):"):]
    i_check = loop.index("if _is_connected():")
    i_kill = loop.index("_kill_cybos_procs()")
    assert i_check < i_kill, "재시도가 연결 여부를 보기 전에 Cybos 를 죽이면 살아 있는 세션을 끊는다"
    assert "return True" in loop[i_check:i_kill]


def test_kill_reports_survivors():
    fn = _SRC[_SRC.index("def _kill_cybos_procs"):_SRC.index("def _dismiss_error_dialogs")]
    assert "종료 실패" in fn
    assert "except Exception:\n                pass" not in fn, "종료 예외를 다시 삼키고 있다"
