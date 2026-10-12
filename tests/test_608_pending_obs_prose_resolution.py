# -*- coding: utf-8 -*-
"""[MW0602 608차 후속2 / 장후 자동조치 G-609] 회귀 — 「본문엔 해소, 체크박스는 열림」.

**무엇이 문제였나.** `O-93`(신동 PDF·메일 라이브 검증)은 606차(2026-10-01)가 세션
요약 목록에 `- O-93(…): ✅ 해소 — 15:40:10 [ShindongMail] 발송 완료` 로 결론을
적었지만, 원 체크박스 `- [ ] O-93 …` 은 열린 채 남았다. 수집기 §11 「미판정 관측
스캔」(526차 G-1)은 체크박스 **최종 상태**만 읽으므로, 판정 태그 `[ShindongMail]` 이
매일 찍히는 한 「판정 조건 충족 — 오늘 판정할 것」을 4거래일 연속 다시 올렸다.

⚠ 리포트(1006 §3q G-609 ②)는 이것을 *"체크박스 상태도 함께 보도록"* 이라 적었지만
  **체크박스는 이미 보고 있었다**(526차 불변식 ②). 빠진 축은 **본문 결론**이다 —
  함정 ①(이미 있는 것을 또 구현) 확인 후 제안을 그 형태로 고쳐 구현했다.

여기서 고정하는 불변식:

① 체크박스 `[ ]` **뒤에** `✅ … 해소` 본문 줄이 있으면 판정 대조(rows)에서 빠지고
   `prose_resolved` 로 따로 남는다 — 조용히 사라지지 않는다(계측 4원칙 ③).
② 본문 해소 줄이 체크박스보다 **앞에** 있으면(재개된 항목) 빼지 않는다.
③ `미해소`·`예정` 이 든 줄, `✅` 없는 줄은 해소로 읽지 않는다 — 그쪽으로 틀리면
   진짜 미판정 항목이 조용히 사라진다.
④ 접두가 같은 다른 번호(`O-930`)를 `O-93` 으로 읽지 않는다.
⑤ 판정·매매에 관여하지 않는다 — 수집기는 리포트용 읽기 전용이다.

실행:
    py37_32\\python.exe tests/test_608_pending_obs_prose_resolution.py
"""
import io
import os
import shutil
import sys
import tempfile
import datetime

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, ".claude", "skills",
                                "mireuk-daily-check", "scripts"))

import collect_evidence as ce  # noqa: E402

FAILURES = []
DAY = datetime.date(2026, 10, 6)
_LOG_DAYS = ("20260929", "20260930", "20261001", "20261002", "20261006")


def _cfg():
    import json
    return json.loads(json.dumps(ce.DEFAULT_CONFIG))


def _fixture(todo_body):
    root = tempfile.mkdtemp(prefix="t608_")
    os.makedirs(os.path.join(root, "dev_memory"))
    os.makedirs(os.path.join(root, "logs"))
    with io.open(os.path.join(root, "dev_memory", "NEXT_TODO.md"),
                 "w", encoding="utf-8") as f:
        f.write(todo_body)
    for d in _LOG_DAYS:
        with io.open(os.path.join(root, "logs", "%s_SYSTEM.log" % d),
                     "w", encoding="utf-8") as f:
            f.write(u"15:40:10 [ShindongMail] 발송 완료\n")
    return root


# 실제 형태(축약) — 체크박스 등록 → 다음 세션 요약 목록에 결론.
HEAD = u"""# NEXT TODO

## 2026-09-30 (MW0602 605차 — 일일 점검: 장후)

- [ ] O-93(신규, 다음 거래일 장후 판정) 다음 EOD `[ShindongMail]` 로그 재확인 — 성공하면 해소.
"""


def _ids(rows):
    return [x["id"] for x in rows]


def test_prose_resolution_moves_item_out_of_rows():
    """① 본문 해소 줄이 뒤에 있으면 rows 에서 빠지고 prose_resolved 로 남는다."""
    body = HEAD + u"""
## 2026-10-01 (MW0602 606차 — 일일 점검: 장후)

- O-93(신동 PDF·메일 Fix F-1 라이브 검증): ✅ 해소 — 15:40:10 `[ShindongMail] 발송 완료` 확인.
"""
    root = _fixture(body)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert r["measured"] is True, r
        assert "O-93" not in _ids(r["rows"]), (
            "본문에 해소 기록이 있는데 「오늘 판정할 것」으로 또 올렸다 — "
            "O-93 재포착 재발: %r" % r)
        pr = r.get("prose_resolved") or []
        assert _ids(pr) == ["O-93"], (
            "해소 기록 항목이 조용히 사라졌다 — 체크박스를 닫으라는 신호가 없다: %r" % r)
        assert pr[0]["date"] == "2026-10-01", pr
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_without_prose_the_old_behavior_holds():
    """기준선 — 본문 해소가 없으면 종전대로 rows 에 오른다(526차 동작 보존)."""
    root = _fixture(HEAD)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert "O-93" in _ids(r["rows"]), (
            "본문 해소가 없는데도 미판정 항목이 사라졌다 — 526차 탐지력 훼손: %r" % r)
        assert (r.get("prose_resolved") or []) == [], r
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_reopened_item_is_not_suppressed():
    """② 해소 줄이 체크박스보다 앞이면(그 뒤에 재등록) 빼지 않는다."""
    body = u"""# NEXT TODO

## 2026-09-30 (MW0602 605차 — 일일 점검: 장후)

- O-93(검증): ✅ 해소 — `[ShindongMail]` 1차 확인.

## 2026-10-02 (MW0602 607차 — 일일 점검: 장후)

- [ ] O-93(재개) 재발 — 다음 EOD `[ShindongMail]` 로그 재확인.
"""
    root = _fixture(body)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert "O-93" in _ids(r["rows"]), (
            "재개된 항목을 과거 해소 줄 때문에 지웠다: %r" % r)
        assert (r.get("prose_resolved") or []) == [], r
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_non_conclusion_lines_are_not_resolution():
    """③ `미해소`·`예정`·`✅` 없음은 해소가 아니다."""
    for line in (u"- O-93: ✅ 확인했으나 미해소 — `[ShindongMail]` 실패 지속.",
                 u"- O-93: ✅ 해소 예정 — 오늘 EOD 에서 판정.",
                 u"- O-93: 지난 606차에서 이미 해소 처리됨 — 변경 없음."):
        root = _fixture(HEAD + u"\n## 2026-10-01 (MW0602 606차 — 장후)\n\n" + line + u"\n")
        try:
            r = ce.scan_pending_observations(root, _cfg(), DAY)
            assert "O-93" in _ids(r["rows"]), (
                "결론이 아닌 줄을 해소로 읽어 미판정 항목을 지웠다: %r / %r" % (line, r))
        finally:
            shutil.rmtree(root, ignore_errors=True)


def test_prefix_id_is_not_confused():
    """④ `O-930` 의 해소 줄이 `O-93` 을 지우지 않는다."""
    body = HEAD + u"""
## 2026-10-01 (MW0602 606차 — 장후)

- O-930(다른 항목): ✅ 해소 — 확인 완료.
"""
    root = _fixture(body)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert "O-93" in _ids(r["rows"]), (
            "접두가 같은 다른 번호의 해소 줄로 O-93 을 지웠다: %r" % r)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_scanner_stays_read_only():
    """⑤ 읽기 전용 — 고정 입력 파일을 고치지 않는다."""
    body = HEAD + u"\n## 2026-10-01 (606차)\n\n- O-93: ✅ 해소 — 완료.\n"
    root = _fixture(body)
    try:
        p = os.path.join(root, "dev_memory", "NEXT_TODO.md")
        before = io.open(p, encoding="utf-8").read()
        ce.scan_pending_observations(root, _cfg(), DAY)
        assert io.open(p, encoding="utf-8").read() == before, \
            "스캐너가 NEXT_TODO.md 를 고쳤다 — 체크박스를 닫는 것은 사람/세션 몫이다"
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    for fn in (test_prose_resolution_moves_item_out_of_rows,
               test_without_prose_the_old_behavior_holds,
               test_reopened_item_is_not_suppressed,
               test_non_conclusion_lines_are_not_resolution,
               test_prefix_id_is_not_confused,
               test_scanner_stays_read_only):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
