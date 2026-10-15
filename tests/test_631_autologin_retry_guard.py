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


def test_creon_real_loop_checks_session_before_killing():
    """[MW0601 2026-10-13] CREON 실거래 명령줄 로그인도 같은 불변식을 지킨다 —
    실서버 세션이 이미 붙어 있으면 죽이지 않고 성공, 연결 후 ServerType 이 실서버가 아니면 실패."""
    fn = _SRC[_SRC.index("def _creon_real_cmdline_login"):_SRC.index("def _autologin_impl")]
    loop = fn[fn.index("for real_attempt in range(MAX_LOGIN_ATTEMPTS):"):]
    i_check = loop.index("_session_probe()")
    i_kill = loop.index("_kill_cybos_procs(_REAL_KILL_NAMES)")
    assert i_check < i_kill
    assert "return True" in loop[i_check:i_kill]
    assert "_good(" in loop[i_check:i_kill], "이미 연결된 세션도 실서버·기대 계좌를 대조해야 한다"
    good = fn[fn.index("def _good"):fn.index("for real_attempt")]
    assert "CYBOS_SERVER_TYPE_REAL" in good and "want in accs" in good
    assert "/pwd:***" in fn, "로그에 비밀번호를 찍으면 안 된다"


def test_creon_real_login_closes_plus_notice_by_owner():
    """[MW0601 2026-10-13] 로그인 후 「공지사항」 창은 좌표 클릭이 아니라 WM_CLOSE 로,
    cpstart.exe 소유 창만 닫는다."""
    fn = _SRC[_SRC.index("def _close_plus_notice"):_SRC.index("def _updater_running")]
    assert "WM_CLOSE" in fn and '"cpstart.exe"' in fn and "SetCursorPos" not in fn
    real = _SRC[_SRC.index("def _creon_real_cmdline_login"):_SRC.index("def _autologin_impl")]
    assert real.count("_close_plus_notice(") >= 2, "성공·동의미비 두 경로 모두 닫아야 한다"


def test_trading_mode_defaults_to_mock():
    seg = _SRC[_SRC.index("TRADING_MODE = ("):_SRC.index("MOCK_MODE = TRADING_MODE")]
    assert 'or "mock"' in seg


def test_kill_reports_survivors():
    fn = _SRC[_SRC.index("def _kill_cybos_procs"):_SRC.index("def _dismiss_error_dialogs")]
    assert "종료 실패" in fn
    assert "except Exception:\n                pass" not in fn, "종료 예외를 다시 삼키고 있다"


def test_creon_real_relogin_spares_hts_main():
    """[MW0601 2026-10-15] 실거래 재로그인은 CREON HTS 본체(coMain)를 죽이지 않는다.
    MW0601 은 HTS(Smart1na)와 API(smart7na)를 함께 쓰는 구성이다 — 08:47 재로그인이
    HTS coMain 종료를 시도한 기록이 있었다."""
    real = _SRC[_SRC.index("def _creon_real_cmdline_login"):_SRC.index("def _autologin_impl")]
    assert "_kill_cybos_procs(_REAL_KILL_NAMES)" in real
    assert "_kill_cybos_procs()" not in real, "실거래 경로가 기본 목록(coMain 포함)으로 죽이면 안 된다"
    decl = _SRC[_SRC.index("_REAL_KILL_NAMES ="):]
    decl = decl.splitlines()[0]
    assert '"comain.exe"' in decl and "!=" in decl


def test_kill_tries_plus_disconnect_first():
    """[MW0601 2026-10-15 F-E1] 관리자 셸 kill 이 무효였던 CpStart 가 PlusDisconnect 로 내려갔다.
    kill 루프보다 정상 종료 요청이 먼저 와야 한다."""
    fn = _SRC[_SRC.index("def _kill_cybos_procs"):_SRC.index("def _dismiss_error_dialogs")]
    assert fn.index("_plus_disconnect()") < fn.index("p.kill()")
    pd = _SRC[_SRC.index("def _plus_disconnect"):_SRC.index("def _kill_cybos_procs")]
    assert "timeout=" in pd, "PlusDisconnect 판독 프로세스가 영원히 멈추면 안 된다(TradeInit 모달 전례)"
    assert "PlusDisconnect()" in _SRC
