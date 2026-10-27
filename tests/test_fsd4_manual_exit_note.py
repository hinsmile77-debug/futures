"""[F-SD-4 · MW0602 666차 후속2 → Sindong2-V4 이식] 수동청산 사유 캡처 (사용자 승인 2026-10-27).

2026-10-27 14:49 `R60|10:50|+1` 수동 전량청산이 사유 없이 남아 장후 점검이 원인을 알 수 없었다
(사후 확인: 「버튼점검」). 대시보드 사유 칸 → `[ManualExit] 사유=…` 로그 + trades.db manual_exit_notes.

  N1  정규화 — 줄바꿈·연속공백 접기, 200자 상한, 공백뿐이면 None
  N2  DB 기록 — 입력은 note_given=1, 미입력은 note=''·note_given=0 (미측정≠0)
  N3  사유는 exit_reason 에 섞지 않는다 — reason 문자열 원형 유지(소스 단언)
  H1  핸들러: 사유가 있으면 로그·DB 에 남고, 주문 수량·kind·reason 은 사유와 무관하다
  H2  핸들러: 사유 칸 읽기가 예외를 내도 청산 주문은 나간다(게이트 아님)
  H3  핸들러: 미체결 보류로 청산이 안 나가면 사유 칸을 소비하지 않는다
  D1  대시보드 ExitPanel 사유 칸 — take 는 값을 돌려주고 비운다(offscreen, PyQt5 없으면 skip)
"""
import ast
import io
import os
import sqlite3
import sys
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils import db_utils as DU  # noqa: E402


def test_N1_normalize():
    assert DU.normalize_manual_exit_note(None) is None
    assert DU.normalize_manual_exit_note("   \n ") is None
    assert DU.normalize_manual_exit_note(" 버튼\n점검 ") == "버튼 점검"
    assert len(DU.normalize_manual_exit_note("가" * 500)) == DU.MANUAL_EXIT_NOTE_MAX_LEN


def test_N2_record(tmp_path):
    db = str(tmp_path / "t.db")
    DU.record_manual_exit_note(100, "EXIT_FULL", "LONG", 1, "버튼점검", order_ret=0, db_path=db)
    DU.record_manual_exit_note(50, "EXIT_MANUAL_PARTIAL", "SHORT", 1, None, db_path=db)
    rows = sqlite3.connect(db).execute(
        "SELECT percent, kind, direction, send_qty, path, order_ret, note, note_given "
        "FROM manual_exit_notes ORDER BY id").fetchall()
    assert rows[0] == (100, "EXIT_FULL", "LONG", 1, "button", 0, "버튼점검", 1)
    assert rows[1] == (50, "EXIT_MANUAL_PARTIAL", "SHORT", 1, "button", None, "", 0)


def test_N3_note_never_reaches_exit_reason():
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    assert 'reason = "수동 전량청산" if percent >= 100 else f"수동 청산 {percent}%→전량"' in src
    assert 'reason = f"수동 부분청산 {percent}%"' in src
    fn = _method_src("_on_manual_exit_requested")
    assert "_note" not in "".join(l for l in fn.splitlines() if l.strip().startswith("reason ="))


# ------------------------------------------------------------- 핸들러 실행(AST 추출)
_NAMES = ("_take_manual_exit_note", "_record_manual_exit_note", "_on_manual_exit_requested")


def _method_src(name):
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node)
    raise AssertionError(name)


def _harness(tmp_path, note="버튼점검", note_raises=False, pending=False, qty=1):
    import textwrap
    logs, orders, pend = [], [], {}
    db = str(tmp_path / "h.db")

    class _Log:
        @staticmethod
        def system(msg, level="INFO"):
            logs.append(msg)

        @staticmethod
        def trade(msg):
            logs.append(msg)

    real_record = DU.record_manual_exit_note
    fake_du = types.ModuleType("utils.db_utils")
    fake_du.normalize_manual_exit_note = DU.normalize_manual_exit_note
    fake_du.record_manual_exit_note = lambda **kw: real_record(db_path=db, **kw)
    ns = {"log_manager": _Log, "CB_STATE_HALTED": "HALTED",
          "_ts_operator_exit_external": lambda *a, **k: None,
          "_ts_on_exit_order_reject": lambda *a, **k: None}
    body = "class T:\n" + "".join(textwrap.indent(textwrap.dedent(_method_src(n)), "    ") + "\n"
                                  for n in _NAMES)
    taken = []

    class _Dash:
        def take_manual_exit_note(self):
            if note_raises:
                raise RuntimeError("panel gone")
            taken.append(note)
            return note

    class _Pos:
        status, quantity, entry_price = "LONG", qty, 894.9

        def resolve_stage_for_exit_qty(self, q, full_close):
            return 3

    saved = sys.modules.get("utils.db_utils")
    sys.modules["utils.db_utils"] = fake_du
    try:
        exec(compile(body, "main_extract", "exec"), ns)
        t = ns["T"]()
        t.position, t.dashboard, t._external_watch = _Pos(), _Dash(), False
        t._last_pipeline_price = 883.2
        t.circuit_breaker = types.SimpleNamespace(state="NORMAL")
        t._pending_order = {"kind": "ENTRY"}
        t._has_pending_order = lambda: pending
        t._set_pending_order = lambda **kw: pend.update(kw)
        t._clear_pending_order = lambda: None
        t._send_broker_exit_order = lambda q: orders.append(q) or 0
        t._on_manual_exit_requested(100)
    finally:
        sys.modules["utils.db_utils"] = saved
    rows = (sqlite3.connect(db).execute("SELECT note, note_given, kind, send_qty FROM manual_exit_notes")
            .fetchall() if os.path.exists(db) else [])
    return logs, orders, pend, rows, taken


def test_H1_note_logged_and_order_unchanged(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    logs, orders, pend, rows, _ = _harness(tmp_path / "a", note="하드스톱 테스트")
    _, orders0, pend0, _, _ = _harness(tmp_path / "b", note=None)
    assert orders == orders0 == [1]
    assert pend["reason"] == "수동 전량청산" and pend["kind"] == "EXIT_FULL" and pend["qty"] == 1
    assert any("[ManualExit] 사유='하드스톱 테스트'" in m for m in logs)
    assert rows[0] == ("하드스톱 테스트", 1, "EXIT_FULL", 1)
    assert pend0["reason"] == pend["reason"]


def test_H2_note_failure_does_not_block_exit(tmp_path):
    logs, orders, pend, rows, _ = _harness(tmp_path, note_raises=True)
    assert orders == [1]
    assert any("사유 입력칸 읽기 실패" in m for m in logs)
    assert any("[ManualExit] 사유=미입력" in m for m in logs)
    assert rows == [("", 0, "EXIT_FULL", 1)]


def test_H3_held_exit_keeps_note(tmp_path):
    logs, orders, pend, rows, taken = _harness(tmp_path, pending=True)
    assert orders == [] and taken == [] and rows == []


# ------------------------------------------------------------- 대시보드
def test_D1_exit_panel_note_field():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    QtWidgets = pytest.importorskip("PyQt5.QtWidgets")
    try:
        import dashboard.main_dashboard as MD
    except Exception as e:  # 대시보드 의존성(win32 등) 미설치 환경
        pytest.skip("main_dashboard import 불가: %s" % e)
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    p = MD.ExitPanel()
    p.manual_exit_note.setText("  버튼점검 ")
    assert p.take_manual_exit_note() == "버튼점검"
    assert p.manual_exit_note.text() == ""
    assert p.take_manual_exit_note() is None
    p.show()
    app.processEvents()
