# -*- coding: utf-8 -*-
"""[MW0602 597차] 런처 GUARD — **이 WORKDIR 의 main.py 만** 대상으로 삼는다.

2026-09-29 09:01 GUARD 가 다른 프로젝트(`auto_trader_kiwoom` 「한량투자」,
명령줄 `python main.py`)를 `kill-target` 으로 잡았다. 종료 줄이 500차 `!=` 결함으로
죽어 있어 살아남았을 뿐이다 — 결함을 고치는 순간 남의 매매 프로그램을 죽인다.

판정: 프로세스의 `*main.py` 인자를 풀어(상대경로면 그 프로세스 cwd 기준)
`WORKDIR\\main.py` 와 같을 때만 대상. cwd 를 못 읽으면 상대경로는 **대상 아님**
(프로브가 `skip-not-this-workdir` 로 남긴다). 런처는 항상 절대경로로 띄운다.
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAUNCHERS = tuple(n for n in ("start_mireuk.bat", "start_mireuk_CREON.bat")
                  if os.path.exists(os.path.join(ROOT, n)))


def _guard_lines(name):
    lines = io.open(os.path.join(ROOT, name), "rb").read().decode("utf-8").split("\r\n")
    return [l for l in lines if l.startswith('"!PY32!"') and "main.py" in l
            and "psutil.process_iter" in l]


class _P(object):
    def __init__(self, cmdline, cwd):
        self.info = {"cmdline": cmdline, "cwd": cwd}


def _own_fn(line, workdir):
    body = line[line.index('-c "') + 4:]
    m = re.search(r"(tgt=.*?own=lambda p: tgt in res\(p\);)", body)
    assert m, "own() 정의가 없다: %s" % line[:120]
    cwd0 = os.getcwd
    ns = {"os": os}
    try:
        os.getcwd = lambda: workdir
        exec(m.group(1), ns)
    finally:
        os.getcwd = cwd0
    return ns["own"]


def test_every_guard_line_is_scoped_to_workdir():
    assert LAUNCHERS
    for name in LAUNCHERS:
        lines = _guard_lines(name)
        assert len(lines) == 4, "%s: GUARD 줄 %d개" % (name, len(lines))
        for l in lines:
            assert "own(p)" in l or "own(p)]" in l or "if own(p)" in l, l[:120]


def test_own_selects_only_this_project():
    wd = r"C:\Users\pc1\PycharmProjects\futures"
    other = r"C:\Users\pc1\PycharmProjects\auto_trader_kiwoom"
    for name in LAUNCHERS:
        for l in _guard_lines(name):
            own = _own_fn(l, wd)
            # 런처가 띄운 미륵이 — 절대경로, cwd 못 읽어도 대상
            assert own(_P(["python.exe", wd + r"\main.py"], None))
            # 수동 실행 미륵이 — 상대경로 + cwd 읽힘
            assert own(_P(["python", "main.py"], wd))
            # 한량투자 — 상대경로 + 다른 cwd / cwd 못 읽음 → 둘 다 대상 아님
            assert not own(_P(["python", "main.py"], other))
            assert not own(_P(["python", "main.py"], None))
            assert not own(_P(["python.exe", other + r"\main.py"], None))
            # 재학습 서브프로세스 등 main.py 가 아닌 것
            assert not own(_P(["python.exe", wd + r"\retrain_intraday.py"], wd))


def test_probes_record_skipped_processes():
    """제외도 남긴다 — 계측 4원칙 ③ 탈락 가시화."""
    for name in LAUNCHERS:
        for l in _guard_lines(name):
            if "running-probe" in l or "kill-target" in l:
                assert "skip-not-this-workdir" in l and "skipped={}" in l
