# -*- coding: utf-8 -*-
"""[MW0602 577차 후속 / F-3] 조용한 종료의 "원인"을 남긴다 — 회귀 가드.

2026-09-17 12:21:43 에 본체가 원인 로그 한 줄 없이 멈췄다. 크래시가 아니었다 —
`[CLEAN EXIT]` 마커가 정상으로 찍혔다. 즉 **누군가 정상 종료를 요청했는데 그
"누군가"를 적는 자리가 없었다.**

이 테스트가 고정하는 것은 두 가지다.

1. **배선이 살아 있는가.** 최초 구현은 `_record_shutdown_reason` /
   `_shutdown_reason_summary` 를 **정의만 하고 아무 데서도 부르지 않았다** —
   CLAUDE.md 계측 4원칙 ④ 가 경고하는 죽은 계측 그 자체였다. 정의가 남아 있어도
   호출부가 사라지면 같은 상태로 되돌아가므로 호출부를 명시적으로 센다.
2. **훅이 실제로 기록하는가.** 정적 검사만으로는 Qt 시그널이 연결됐는지 알 수
   없다. offscreen 으로 진짜 `QApplication` 을 띄워 `quit()` 을 부르고, 파일에
   사유가 남는지 본다([[feedback_pyqt_offscreen_testing]]).

⚠ `main.py` 는 모듈 임포트가 불가능하다(모듈 최상단에서 QApplication 생성·COM
  접촉). 그래서 이 리포의 관례대로 **소스에서 해당 정의만 떼어 exec** 한다.
"""
import ast
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN = os.path.join(_ROOT, "main.py")

_WANT_FUNCS = (
    "_record_shutdown_reason",
    "_shutdown_reason_summary",
    "_install_shutdown_reason_hooks",
)
_WANT_GLOBALS = ("_SHUTDOWN_REASONS", "_SHUTDOWN_REASON_PATH")


def _main_source():
    with io.open(_MAIN, encoding="utf-8") as f:
        return f.read()


def _load_f3_namespace(tmp_path):
    """main.py 에서 F-3 정의만 떼어 독립 네임스페이스로 exec 한다.

    로그 경로는 tmp 로 돌려 실거래 `logs/` 를 건드리지 않는다
    ([[feedback_isolate_stateful_verification]] — 검증 스크립트가 실앱과 파일을
    공유하면 안 된다).
    """
    src = _main_source()
    tree = ast.parse(src)
    lines = src.splitlines(True)

    chunks = []
    for node in tree.body:
        name = None
        if isinstance(node, ast.FunctionDef):
            name = node.name if node.name in _WANT_FUNCS else None
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in _WANT_GLOBALS:
                    name = t.id
        if name:
            seg = "".join(lines[node.lineno - 1:node.end_lineno])
            chunks.append((node.lineno, seg))

    found = len(chunks)
    assert found == len(_WANT_FUNCS) + len(_WANT_GLOBALS), (
        "F-3 정의 %d/%d 만 찾았다 — 이름이 바뀌었거나 삭제됐다"
        % (found, len(_WANT_FUNCS) + len(_WANT_GLOBALS))
    )

    ns = {"os": os}
    exec(compile("".join(s for _, s in sorted(chunks)), "<f3>", "exec"), ns)
    ns["_SHUTDOWN_REASON_PATH"] = str(tmp_path / "shutdown_reason.log")
    return ns


# ══════════════════════════════════════════════════════════════════════
# 1. 배선 — 정의만 있고 호출부가 없으면 죽은 계측이다
# ══════════════════════════════════════════════════════════════════════

def test_1_every_f3_symbol_has_a_call_site():
    src = _main_source()
    for name in _WANT_FUNCS:
        # 정의 1회를 뺀 나머지가 호출부다
        uses = src.count(name) - 1
        assert uses >= 1, (
            "%s 이 정의만 있고 호출부가 없다 — 최초 구현이 이 상태였다"
            " (계측 4원칙 ④ 죽은 계측)" % name
        )


def test_2_clean_exit_line_carries_the_reason():
    src = _main_source()
    assert "reason={_shutdown_reason_summary()}" in src, (
        "[CLEAN EXIT] 줄에 reason= 이 붙어 있지 않다 —"
        " 사유를 기록해도 읽는 자리가 없으면 아무도 안 본다"
    )


def test_3_hooks_are_installed_next_to_the_atexit_marker():
    src = _main_source()
    assert "_install_shutdown_reason_hooks(_qt_app)" in src, (
        "훅 설치 호출이 없다 — Qt 경로(aboutToQuit)가 통째로 죽는다"
    )
    assert "[ShutdownReason]" in src, "설치 결과를 로그로 남기지 않는다(계측 4원칙 ③)"


def test_4_no_signal_handler_was_added():
    """F-3 은 **기록만** 한다 — 종료 동작을 바꾸면 전제를 벗어난다.

    ⚠ 문자열·주석이 아니라 **실행되는 코드**만 본다. 함수 docstring 이
      "시그널 핸들러(SIGTERM 등)는 일부러 넣지 않았다"라고 적고 있어서,
      소스를 문자열로 훑으면 그 설명문 자체에 걸려 오탐한다.
    """
    tree = ast.parse(_main_source())
    fn = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef)
        and n.name == "_install_shutdown_reason_hooks"
    )
    for node in ast.walk(fn):
        if isinstance(node, ast.Attribute) and node.attr == "signal":
            pytest.fail(
                "시그널 핸들러가 들어왔다 — 기본 종료 동작을 바꾸는 일이라"
                " 「로깅만」이라는 F-3 전제를 벗어난다"
            )
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names]
            assert "signal" not in names, "signal 모듈을 들여온다 — 위와 같은 이유"


# ══════════════════════════════════════════════════════════════════════
# 2. 동작 — 실제로 기록되는가
# ══════════════════════════════════════════════════════════════════════

def test_5_empty_state_reads_as_unrecorded_not_blank(tmp_path):
    """미측정 != 0 (계측 4원칙 ②). 공란이면 "원인 없음"으로 오독된다."""
    ns = _load_f3_namespace(tmp_path)
    assert ns["_shutdown_reason_summary"]() == "미기록"


def test_6_record_writes_a_single_line_and_survives_garbage(tmp_path):
    ns = _load_f3_namespace(tmp_path)
    rec = ns["_record_shutdown_reason"]

    rec("qt:aboutToQuit", "File \"main.py\", line 1\n  스택 둘째 줄")
    rec("excepthook", "ValueError: 폭 " + "x" * 2000)

    with io.open(ns["_SHUTDOWN_REASON_PATH"], encoding="utf-8") as f:
        body = f.read()
    written = [l for l in body.splitlines() if l.strip()]
    assert len(written) == 2, "한 사건은 한 줄이어야 한다(개행이 새면 파싱이 깨진다)"
    assert "절단" in written[1], "긴 사유를 자를 때 잘랐다는 사실을 남겨야 한다(계측 4원칙 ③)"

    summary = ns["_shutdown_reason_summary"]()
    assert summary.startswith("qt:aboutToQuit"), "첫 원인이 진짜 원인이다"
    assert "외 1건" in summary


def test_7_record_never_raises(tmp_path):
    """종료 경로 안에서 불린다 — 여기서 예외가 나면 종료를 망가뜨린다."""
    ns = _load_f3_namespace(tmp_path)
    ns["_SHUTDOWN_REASON_PATH"] = os.path.join(
        str(tmp_path), "없는폴더", "깊이", "x.log"
    )
    ns["_record_shutdown_reason"]("qt:test", "경로가 없어도 죽지 않는다")
    assert ns["_SHUTDOWN_REASONS"], "파일이 안 돼도 메모리 기록은 남아야 한다"


def test_8_excepthook_records_then_delegates(tmp_path):
    ns = _load_f3_namespace(tmp_path)
    called = []
    prev = sys.excepthook
    sys.excepthook = lambda *a: called.append(a)
    try:
        installed = ns["_install_shutdown_reason_hooks"](None)
        assert "excepthook" in installed
        try:
            raise ValueError("의도적 예외")
        except ValueError:
            sys.excepthook(*sys.exc_info())
    finally:
        sys.excepthook = prev

    assert called, "원래 excepthook 에 위임하지 않았다 — 기존 동작을 삼켰다"
    summary = ns["_shutdown_reason_summary"]()
    assert "ValueError" in summary and "의도적 예외" in summary


def test_9_qt_quit_is_actually_recorded(tmp_path):
    """offscreen 으로 진짜 이벤트 루프를 돌린다 — connect 가 됐는지는
    정적 검사로 알 수 없다."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    QtWidgets = pytest.importorskip("PyQt5.QtWidgets")
    QtCore = pytest.importorskip("PyQt5.QtCore")

    ns = _load_f3_namespace(tmp_path)
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])

    installed = ns["_install_shutdown_reason_hooks"](app)
    assert "qt:aboutToQuit" in installed, "aboutToQuit 연결 실패 — %r" % (installed,)

    QtCore.QTimer.singleShot(0, app.quit)
    app.exec_()

    summary = ns["_shutdown_reason_summary"]()
    assert summary.startswith("qt:aboutToQuit"), summary
    assert "line" in summary, "파이썬 스택이 안 붙었다 — 호출부 판별이 불가능해진다"
    sys.excepthook = sys.__excepthook__
