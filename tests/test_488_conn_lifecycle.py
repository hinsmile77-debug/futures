# -*- coding: utf-8 -*-
"""[MW0602 488차 후속2] 캠페인 리포트 DB 연결 수명 불변식.

무엇을 막는가
-------------
`scripts/generate_validation_campaign_report.py:_conn()` 은 raw `sqlite3.Connection`
을 돌려줬고, 호출부 **90곳**이 `with _conn(x) as conn:` 으로 썼다. 그런데 sqlite3 에서
`with conn:` 은 **트랜잭션** 컨텍스트일 뿐 `close()` 가 아니다 — 리포트 1회 생성마다
연결 90개가 샜다.

두 갈래로 나타났다.
  · 운영 — 핸들이 프로세스 끝까지 남는다. EOD 1회성이라 실피해는 작지만 WAL 경합
    진단을 어렵게 만든다.
  · 테스트 — **Windows 는 열린 파일을 지울 수 없다.** 임시 DB 를 만들어 판정을 돌리고
    `os.unlink()` 하는 테스트 **8개**가 전부 `PermissionError [WinError 32]` 로 실패했다
    (`tests/test_439_p2_slippage_judgment.py`). 원인이 테스트가 아니라 프로덕션 누수라,
    테스트를 고치는 것은 증상 억제였을 것이다.

고친 뒤의 위험은 **반대쪽**이다 — 닫기만 하고 commit 을 잃으면 섀도 테이블 `UPDATE`
(예: `tp1_trail_shadow` · `hurst_gate_shadow` 등 여러 곳)가 **조용히 사라진다.**
그래서 이 파일은 두 성질을 **함께** 고정한다.

불변식
------
① `with _conn(p) as c:` 블록을 나오면 연결이 **닫혀 있다**(파일 삭제 가능)
② 블록 안의 쓰기가 **커밋된다**(종전 `with conn:` 의미 보존)
③ 블록 안에서 예외가 나면 **롤백**되고, 그래도 연결은 닫힌다
④ `row_factory` 가 `sqlite3.Row` 로 유지된다(호출부가 컬럼명 접근을 쓴다)

실행:
    python tests/test_488_conn_lifecycle.py
"""
import os
import sqlite3
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ.setdefault("MIREUK_TEST_MODE", "1")

from scripts.generate_validation_campaign_report import _conn  # noqa: E402


def _mkdb():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    c = sqlite3.connect(path)
    c.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    c.execute("INSERT INTO t (id, v) VALUES (1, 'before')")
    c.commit()
    c.close()
    return path


def test_connection_is_closed_so_file_can_be_deleted():
    """① 블록을 나오면 닫힌다 — Windows 에서 삭제가 되는 것이 그 증거다."""
    path = _mkdb()
    with _conn(path) as c:
        c.execute("SELECT 1").fetchone()
    # 닫히지 않았다면 Windows 에서 여기서 PermissionError 가 난다.
    os.unlink(path)
    assert not os.path.exists(path)


def test_writes_are_committed():
    """② 커밋 의미 보존 — 이걸 잃으면 섀도 테이블 UPDATE 가 조용히 사라진다."""
    path = _mkdb()
    try:
        with _conn(path) as c:
            c.execute("UPDATE t SET v='after' WHERE id=1")
        chk = sqlite3.connect(path)
        try:
            got = chk.execute("SELECT v FROM t WHERE id=1").fetchone()[0]
        finally:
            chk.close()
        assert got == "after", (
            "블록을 나온 뒤 쓰기가 남지 않았다 — commit 이 사라졌다. "
            "이 파일에는 섀도 테이블 UPDATE 가 여러 곳 있어 조용히 기록이 유실된다")
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_exception_rolls_back_and_still_closes():
    """③ 예외 시 롤백 + 그래도 닫힌다."""
    path = _mkdb()
    try:
        try:
            with _conn(path) as c:
                c.execute("UPDATE t SET v='dirty' WHERE id=1")
                raise RuntimeError("의도한 실패")
        except RuntimeError:
            pass
        chk = sqlite3.connect(path)
        try:
            got = chk.execute("SELECT v FROM t WHERE id=1").fetchone()[0]
        finally:
            chk.close()
        assert got == "before", "예외가 났는데 롤백되지 않았다: %r" % got
    finally:
        # 닫혔다면 지워진다(①과 같은 근거).
        os.unlink(path)
        assert not os.path.exists(path)


def test_row_factory_is_preserved():
    """④ `sqlite3.Row` 유지 — 호출부가 `r["col"]` 로 읽는다."""
    path = _mkdb()
    try:
        with _conn(path) as c:
            row = c.execute("SELECT v FROM t WHERE id=1").fetchone()
            assert row["v"] == "before", "컬럼명 접근이 깨졌다 — row_factory 확인"
    finally:
        os.unlink(path)


def test_all_call_sites_use_with():
    """⑤ `_conn()` 은 **반드시 `with`** 로만 쓴다.

    컨텍스트 매니저로 바꾼 뒤로는 `conn = _conn(p)` 처럼 쓰면 연결이 아니라
    컨텍스트 객체가 잡혀 조용히 오작동한다. 정의 1곳을 뺀 전부가 `with` 여야 한다.
    """
    import io
    import re
    src = io.open(os.path.join(_ROOT, "scripts",
                               "generate_validation_campaign_report.py"),
                  encoding="utf-8").read()
    uses = [m for m in re.finditer(r"(?<![\w.])_conn\(", src)]
    withs = len(re.findall(r"with _conn\(", src))
    defs = len(re.findall(r"def _conn\(", src))
    assert defs == 1, defs
    assert len(uses) - defs == withs, (
        "`with` 없이 `_conn()` 을 부르는 곳이 있다 — 컨텍스트 객체가 연결로 오인된다 "
        "(총 %d · def %d · with %d)" % (len(uses), defs, withs))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _fails = 0
    for _name, _fn in sorted(globals().items()):
        if not _name.startswith("test_") or not callable(_fn):
            continue
        try:
            _fn()
            print("PASS %s" % _name)
        except AssertionError as _e:
            _fails += 1
            print("FAIL %s\n  %s" % (_name, _e))
    print("-" * 60)
    print("%s (%d fail)" % ("ALL PASS" if not _fails else "FAILED", _fails))
    sys.exit(1 if _fails else 0)
