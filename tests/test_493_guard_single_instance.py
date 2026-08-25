# -*- coding: utf-8 -*-
"""[MW0601 493차 후속7 / F-U] 단일 인스턴스 가드 — 종료코드 3분류와 안전 정책.

왜 필요한가
-----------
종전 가드는 판정 근거 **세 갈래가 전부 막혀** 있었다:

  (a) 종료코드 — 파이썬은 예외로 죽어도 exit 1 이라 「크래시」와 「N개 발견」이 겹쳤다
  (b) 표준오류 — `2>NUL` 이 traceback 을 통째로 버렸다
  (c) 표준출력 — 프로브의 `print` 가 콘솔로만 가고 로그에 안 들어갔다

그래서 넉 달간 매일 거짓 「감지됨」을 찍었고, 런처 로그 11개 전수에서
`기존 main.py 없음` 이 **0번** 나왔다. `terminate()` 줄도 같은 결함이라
한 번도 실행된 적이 없는데 「종료 완료」는 무조건 찍혔다.

이 파일이 고정하는 불변식:
① 종료코드 3분류 — `0`=없음 / `1`=발견 / **`3`=프로브 실패**
② 실패는 「없음」으로 흘러가지 않고 traceback 이 **stdout** 에 남는다
③ WORKDIR **밖** 프로세스는 죽이지 않는다(남의 프로그램을 죽이는 것은 권한 밖)
④ 명령줄 **판독불가**는 「불일치」가 아니라 미측정으로 집계·표기된다
⑤ 절대경로 판정(strict)은 **섀도** — 종료 대상은 당분간 옛 판정(legacy)
⑥ 종료 후 **재확인** — 「완료」는 검증된 문장일 때만 출력
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scripts.guard_single_instance as G  # noqa: E402

WORKDIR = r"C:\Users\82108\PycharmProjects\futures"
OTHER = r"C:\Users\82108\PycharmProjects\options"


class _FakeProc(object):
    """psutil.Process 대역 — 필요한 표면만 흉내낸다."""

    def __init__(self, pid, name="python.exe", cmdline=None, cwd=WORKDIR,
                 cwd_raises=False):
        self.info = {"pid": pid, "name": name, "cmdline": cmdline}
        self.pid = pid
        self._cwd = cwd
        self._cwd_raises = cwd_raises
        self.terminated = False

    def cwd(self):
        if self._cwd_raises:
            raise OSError("access denied")
        return self._cwd

    def create_time(self):
        return 1_700_000_000.0

    def terminate(self):
        self.terminated = True


def _install(monkeypatch, procs, iter_raises=False):
    """가짜 psutil 을 모듈에 심는다. `scan()` 이 함수 안에서 import 하므로 가능."""
    import types

    fake = types.ModuleType("psutil")
    registry = {p.pid: p for p in procs}

    def process_iter(attrs=None):
        if iter_raises:
            raise RuntimeError("psutil 폭발")
        return list(procs)

    fake.process_iter = process_iter
    fake.Process = lambda pid: registry[pid]
    monkeypatch.setitem(sys.modules, "psutil", fake)
    return registry


# ── ① 종료코드 3분류 ────────────────────────────────────────────────────────
def test_probe_returns_0_when_none(monkeypatch, capsys):
    _install(monkeypatch, [])
    rc = G.main(["--probe", "--workdir", WORKDIR])
    assert rc == G.RC_NONE == 0
    out = capsys.readouterr().out
    assert "[GUARD] 실행 중 main.py: 0" in out, (
        "판정 근거가 stdout 에 없다 — 배치가 로그에 넣을 것이 없어진다")


def test_probe_returns_1_when_found(monkeypatch, capsys):
    _install(monkeypatch, [
        _FakeProc(1234, cmdline=["python.exe", os.path.join(WORKDIR, "main.py")]),
    ])
    rc = G.main(["--probe", "--workdir", WORKDIR])
    assert rc == G.RC_FOUND == 1
    out = capsys.readouterr().out
    assert "PID=1234" in out
    assert "started=" in out and "cwd=" in out, "사후에 무엇을 봤는지 남아야 한다"


def test_probe_returns_3_on_failure(monkeypatch, capsys):
    """🔴 핵심 — 실패가 「없음」(0)이나 「발견」(1)으로 흘러가지 않는다."""
    _install(monkeypatch, [], iter_raises=True)
    rc = G.main(["--probe", "--workdir", WORKDIR])
    assert rc == G.RC_PROBE_FAILED == 3
    out = capsys.readouterr().out
    assert "프로브 실패" in out
    assert "psutil 폭발" in out, (
        "traceback 이 stdout 에 없다 — 종전 `2>NUL` 이 버리던 그 정보다")


def test_three_exit_codes_are_distinct():
    assert len({G.RC_NONE, G.RC_FOUND, G.RC_PROBE_FAILED}) == 3


# ── ③ WORKDIR 밖 보호 ───────────────────────────────────────────────────────
def test_foreign_project_is_not_terminated(monkeypatch, capsys):
    """🚫 다른 프로젝트의 `main.py` 를 죽이지 않는다.

    종전 판정식은 부분문자열 `'main.py' in c` 라 편집기 실행구성까지 잡았고,
    그 다음 줄이 `terminate()` 였다.
    """
    other = _FakeProc(999, cmdline=["python.exe", os.path.join(OTHER, "main.py")],
                      cwd=OTHER)
    _install(monkeypatch, [other])
    rc = G.main(["--terminate", "--workdir", WORKDIR, "--settle-sec", "0"])
    out = capsys.readouterr().out
    assert other.terminated is False, "🔴 남의 프로젝트를 죽였다"
    assert "대상 아님(타 프로젝트)" in out or "보호(종료 안 함)" in out
    assert rc == G.RC_NONE


def test_own_project_is_terminated(monkeypatch, capsys):
    mine = _FakeProc(1234, cmdline=["python.exe", os.path.join(WORKDIR, "main.py")],
                     cwd=WORKDIR)
    reg = _install(monkeypatch, [mine])

    calls = {"n": 0}
    real_scan = G.scan

    def scan_then_empty(workdir, self_pid=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return real_scan(workdir, self_pid)
        return {"matched": [], "strict": [], "foreign": [], "unreadable": []}

    monkeypatch.setattr(G, "scan", scan_then_empty)
    rc = G.main(["--terminate", "--workdir", WORKDIR, "--settle-sec", "0"])
    out = capsys.readouterr().out
    assert reg[1234].terminated is True
    assert "종료예정 PID=1234" in out, "죽이기 **전에** 목록이 남아야 한다"
    assert "잔여=0" in out
    assert rc == G.RC_NONE


def test_remaining_after_terminate_is_an_error(monkeypatch, capsys):
    """⑥ 「완료」는 검증된 문장일 때만 — 잔여가 있으면 ERROR."""
    mine = _FakeProc(1234, cmdline=["python.exe", os.path.join(WORKDIR, "main.py")])
    _install(monkeypatch, [mine])
    rc = G.main(["--terminate", "--workdir", WORKDIR, "--settle-sec", "0"])
    out = capsys.readouterr().out
    assert "잔여" in out and "수동 확인 필요" in out
    assert "잔여=0" not in out, "죽지 않았는데 완료를 찍었다 — 종전 결함의 재발"
    assert rc == G.RC_FOUND


# ── ④ 판독불가 = 미측정 ─────────────────────────────────────────────────────
def test_unreadable_cmdline_is_counted_not_ignored(monkeypatch, capsys):
    """🔴 32비트 프로브는 64비트 프로세스의 명령줄을 못 읽는다.

    `psutil` 이 `None` 을 주는데 종전 코드는 `(… or [])` 로 받아 **조용히
    「불일치」** 로 만들었다 — 진짜 중복 인스턴스를 아예 못 보는 미탐이다.
    """
    _install(monkeypatch, [_FakeProc(777, cmdline=None)])
    rc = G.main(["--probe", "--workdir", WORKDIR])
    out = capsys.readouterr().out
    assert "판독불가 PID=777" in out
    assert "단일 인스턴스 미확정" in out, (
        "판독불가가 있으면 「없음」을 단언하면 안 된다(계측 4원칙 ②)")
    # 판독불가는 「발견」이 아니다 — 종료 대상으로 삼지 않는다.
    assert rc == G.RC_NONE


def test_non_python_process_ignored(monkeypatch):
    _install(monkeypatch, [_FakeProc(1, name="notepad.exe",
                                     cmdline=["notepad.exe", "main.py"])])
    assert G.main(["--probe", "--workdir", WORKDIR]) == G.RC_NONE


def test_self_pid_excluded(monkeypatch):
    """자기 자신을 잡으면 가드가 스스로를 죽인다."""
    me = _FakeProc(os.getpid(),
                   cmdline=["python.exe", os.path.join(WORKDIR, "main.py")])
    _install(monkeypatch, [me])
    assert G.main(["--probe", "--workdir", WORKDIR]) == G.RC_NONE


# ── ⑤ strict 는 섀도 ────────────────────────────────────────────────────────
def test_strict_is_shadow_only(monkeypatch, capsys):
    """신 판정(절대경로)은 **병기만** 한다 — 좁히면 진짜 잔류를 놓칠 수 있다.

    승격은 10거래일 대조 후(스킬 규약 — 게이트 신설은 섀도를 거친다).
    """
    # legacy 에는 걸리고 strict 에는 안 걸리는 형태(상대경로 + WORKDIR 하위 cwd)
    p = _FakeProc(555, cmdline=["python.exe", "..\\other\\main.py"], cwd=WORKDIR)
    _install(monkeypatch, [p])
    rc = G.main(["--probe", "--workdir", WORKDIR])
    out = capsys.readouterr().out
    assert "판정대조 legacy=" in out and "strict=" in out
    assert "섀도" in out, "strict 가 종료 대상이 아님을 로그가 말해야 한다"
    assert rc == G.RC_FOUND, "실제 판정은 legacy 를 따라야 한다"


def test_cwd_unreadable_falls_back_to_legacy(monkeypatch, capsys):
    """`cwd()` 를 못 읽으면 **보호 쪽이 아니라 legacy 대상**으로 남는다.

    미륵이 자신이 잔류한 경우를 놓치지 않기 위해서다 — 가드가 조용해지는 것이
    더 나쁘다. (다만 그 사실이 로그의 `cwd=None` 으로 드러난다.)
    """
    p = _FakeProc(321, cmdline=["python.exe", os.path.join(WORKDIR, "main.py")],
                  cwd_raises=True)
    _install(monkeypatch, [p])
    rc = G.main(["--probe", "--workdir", WORKDIR])
    out = capsys.readouterr().out
    assert rc == G.RC_FOUND
    assert "cwd=None" in out


# ── 경로 헬퍼 ───────────────────────────────────────────────────────────────
@pytest.mark.parametrize("child,parent,expected", [
    (WORKDIR, WORKDIR, True),
    (os.path.join(WORKDIR, "scripts"), WORKDIR, True),
    (OTHER, WORKDIR, False),
    (WORKDIR + "_backup", WORKDIR, False),      # 접두사만 같은 형제 폴더
    ("", WORKDIR, False),
    (WORKDIR, "", False),
])
def test_under_path_boundaries(child, parent, expected):
    assert G._under(G._norm(child), G._norm(parent)) is expected
