# -*- coding: utf-8 -*-
"""[MW0602 526차 후속 / G-1] 회귀 — 수집기 §11 「미판정 관측의 나이」.

**무엇이 문제였나.** `O-47` 은 507차(2026-08-31)가 *"F-7 배포 후 첫 GUARD 발화일에
판정한다"* 로 사전등록했는데, 실제 첫 발화일(09-01)과 그 다음날(09-02) 점검 세션이
**둘 다 그냥 지나갔다.** 판정 규칙 자체는 정확했다 — *언제 판정해야 하는지* 를
상기시키는 장치가 없었을 뿐이다(0903 리포트 `G-1`).

🔴 **이 기능의 최대 위험은 오탐이다.** `dev_memory/NEXT_TODO.md` 는 19,000줄 누적
로그라 `- [ ]` 를 통째로 세면 수백 건이 나오고, 494차 F-7 의 관측 ID 대조 초안은
첫 실행에서 오탐 15건을 내고 폐기됐다. 그래서 아래 불변식은 **탐지력만큼 억제력을**
고정한다.

여기서 고정하는 불변식:

① **여러 줄 항목을 한 항목으로 읽는다** — 판정 기준 로그는 대개 머리줄이 아니라
   이어지는 들여쓴 줄(표 포함)에 있다. `O-47` 이 정확히 그 형태였고, 머리줄만
   읽으면 이 기능은 만든 날부터 0건을 낸다.
② **해소된 항목(`- [x]`)은 올리지 않는다** — 같은 라벨이 매 세션 다시 실리는
   문서라 **최종 상태**로 판정해야 한다.
③ **판정 기준 로그가 오늘 자에 없으면 올리지 않는다** — 추론하지 않는다.
④ **창(窓)은 거래일 축이다** — 세션 **개수**로 자르면 하루 3~4블록이라 8블록이
   약 2거래일밖에 안 되고, 정작 잡으려던 3거래일 방치가 창 밖으로 밀린다.
⑤ **미측정과 0건을 구분한다** — 오늘 자 로그가 없으면 `measured=False` 다
   (계측 4원칙 ②).
⑥ **탈락을 가시화한다** — 태그를 못 뽑은 항목·반복 관측 제외 건수를 남긴다
   (계측 4원칙 ③).
⑦ **판정·매매에 관여하지 않는다** — 수집기는 로그를 읽어 리포트를 쓸 뿐이다.

실행:
    py37_32\\python.exe tests/test_526_pending_obs_age.py
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
DAY = datetime.date(2026, 9, 3)


def _cfg():
    """수집기 기본 설정만 쓴다 — 저장소 사용자 설정에 의존하면 PC 별로 갈린다."""
    import json
    return json.loads(json.dumps(ce.DEFAULT_CONFIG))


# 창은 **최근 5거래일**이다. `O-47` 은 08-31 등록이고 판정 시점이 09-03 이므로,
# 그 사이 거래일이 5개 이내여야 창 안에 남는다 — 실제 달력이 그렇다(08-29 토요일).
_LOG_DAYS = ("20260827", "20260828", "20260831",
             "20260901", "20260902", "20260903")


def _fixture(todo_body, log_days=_LOG_DAYS,
             log_text="[GUARD] running-probe count=0 probe=ok\n"):
    """스크래치 저장소를 만든다.

    ⚠ 실 저장소를 읽지 않는다 — `NEXT_TODO.md` 는 매일 바뀌므로 그것을 입력으로
      쓰면 이 테스트는 내일 다른 것을 재게 된다(고정 입력이 회귀 테스트의 조건).
    """
    root = tempfile.mkdtemp(prefix="t526_")
    os.makedirs(os.path.join(root, "dev_memory"))
    os.makedirs(os.path.join(root, "logs"))
    with io.open(os.path.join(root, "dev_memory", "NEXT_TODO.md"),
                 "w", encoding="utf-8") as f:
        f.write(todo_body)
    for d in log_days:
        with io.open(os.path.join(root, "logs", "%s_SYSTEM.log" % d),
                     "w", encoding="utf-8") as f:
            f.write(log_text)
    return root


# `O-47` 의 실제 형태 — 머리줄에 태그가 없고 **이어지는 표**에 `[GUARD]` 가 있다.
TODO_O47 = u"""# NEXT TODO

## 2026-08-31 (MW0602 507차 후속 — 장후 자동조치 2회차)

- [ ] **`O-47`** `F-7` 배포 **후** 첫 GUARD 발화일에 판정한다. **새 판정식**:

      `[GUARD] running-probe count=N probe=ok` 와 `[GUARD] running-probe decide=…` 가
      **둘 다 로그에 있어야 한다.** 없으면 F-7 배선 실패(P1).

## 2026-09-02 (MW0602 515차 — 일일 점검: 장후 종합)

- [ ] **`O-65`**(신규) 09-03 이후 `vkospi` 가 정상범위(`[8,45]`) 유지되는지 확인.
"""


def test_multiline_item_is_read_as_one_item():
    """① 이어지는 들여쓴 줄의 로그 태그를 항목의 판정 기준으로 읽는다."""
    root = _fixture(TODO_O47)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        ids = [x["id"] for x in r["rows"]]
        assert r["measured"] is True, r
        assert "O-47" in ids, (
            "머리줄에 태그가 없는 `O-47` 을 못 잡았다 — 여러 줄 파싱이 죽었다: %r" % r)
        hit = [x for x in r["rows"] if x["id"] == "O-47"][0]
        assert "[GUARD]" in hit["tags"], hit
        assert hit["age_days"] >= 1, hit
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_range_bracket_is_not_a_log_tag():
    """③ 보조 — `[8,45]` 같은 값 범위를 로그 태그로 오인하지 않는다."""
    root = _fixture(TODO_O47)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert "O-65" not in [x["id"] for x in r["rows"]], (
            "`[8,45]` 를 로그 태그로 읽었다 — 숫자 대괄호는 태그가 아니다: %r" % r)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_resolved_item_is_not_reported():
    """② 최종 상태가 `- [x]` 면 올리지 않는다."""
    body = TODO_O47 + u"""
## 2026-09-03 (MW0602 526차 — 일일 점검: 장전)

- [x] **`O-47`** 판정 완료 — `[GUARD] running-probe` 3거래일 대조로 종결.
"""
    root = _fixture(body)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert "O-47" not in [x["id"] for x in r["rows"]], (
            "해소 처리된 항목이 계속 올라온다 — 매일 같은 적신호가 뜬다: %r" % r)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_absent_log_tag_is_not_reported():
    """③ 판정 기준 로그가 오늘 자에 없으면 올리지 않는다(추론 금지)."""
    root = _fixture(TODO_O47, log_text=u"[Health] latency=12ms\n")
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert r["measured"] is True, r
        assert r["rows"] == [], (
            "오늘 자 로그에 없는 태그로 판정 가능하다고 올렸다: %r" % r)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_window_is_counted_in_trading_days_not_sessions():
    """④ 하루에 세션 블록이 여러 개여도 창이 거래일 기준으로 유지된다.

    🔴 이것이 실측으로 확인된 실패 모드다 — 세션 8개로 자르면 약 2거래일이 되어
      `O-47`(3거래일 방치)이 판정 시점에 창 밖으로 밀린다.
    """
    noise = u"".join(
        u"\n## 2026-09-0%d (MW0602 %d차 — 일일 점검: %s)\n\n- [ ] **`P-9`** 잡음 항목.\n"
        % (d, 500 + d * 3 + k, ph)
        for d in (1, 2, 3)
        for k, ph in enumerate((u"장전", u"장중", u"장후")))
    root = _fixture(TODO_O47 + noise)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert r["scanned_sessions"] >= 4, (
            "세션 블록이 하루 3개씩 쌓이자 창이 좁아졌다: %r" % r)
        assert "O-47" in [x["id"] for x in r["rows"]], (
            "세션 개수 축으로 잘려 `O-47` 이 창 밖으로 밀렸다 — G-1 이 잡으려던 "
            "바로 그 사고를 못 잡는다: %r" % r)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_no_logs_today_is_unmeasured_not_zero():
    """⑤ 오늘 자 로그가 없으면 `measured=False` — 「0건」이 아니다(계측 4원칙 ②)."""
    root = _fixture(TODO_O47, log_days=("20260901",))  # 오늘(09-03) 자 없음
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert r["measured"] is False, (
            "오늘 자 로그가 없는데 측정했다고 보고했다 — 미측정과 0건이 섞인다: %r" % r)
        assert r["rows"] == [], r
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_dropped_items_are_counted():
    """⑥ 태그를 못 뽑은 항목·반복 관측을 **세어서** 남긴다(계측 4원칙 ③)."""
    body = TODO_O47 + u"""
- [ ] **`O-70`** 사용자 결정 여부만 관찰한다(로그 태그 없음).
- [ ] **`O-71` (매 장후)** `[GUARD]` 발화 연속일. 단일일 판정 금지.
"""
    root = _fixture(body)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert r["skipped_no_tag"] >= 1, (
            "판정 태그를 못 뽑은 항목을 조용히 버렸다: %r" % r)
        assert r["skipped_recurring"] >= 1, (
            "세션이 스스로 「매 장후」로 적은 반복 관측을 세지 않았다: %r" % r)
        assert "O-71" not in [x["id"] for x in r["rows"]], (
            "반복 관측이 매일 적신호로 뜬다 — 곧 무시되는 경보가 된다: %r" % r)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_missing_todo_is_an_error_not_silence():
    """⑤ 보조 — 파일 자체가 없으면 `error` 로 드러낸다(조용한 0건 금지)."""
    root = tempfile.mkdtemp(prefix="t526_")
    try:
        os.makedirs(os.path.join(root, "logs"))
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        assert r.get("error"), "NEXT_TODO.md 부재가 조용히 0건으로 통과했다: %r" % r
        assert r["measured"] is False, r
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_scanner_is_read_only():
    """⑦ 스캐너는 저장소를 쓰지 않는다 — 수집기는 읽기 전용이다(SKILL.md §2)."""
    root = _fixture(TODO_O47)
    try:
        before = {}
        for dirpath, _dn, fns in os.walk(root):
            for fn in fns:
                p = os.path.join(dirpath, fn)
                before[p] = (os.stat(p).st_size, os.stat(p).st_mtime)
        ce.scan_pending_observations(root, _cfg(), DAY)
        after = {}
        for dirpath, _dn, fns in os.walk(root):
            for fn in fns:
                p = os.path.join(dirpath, fn)
                after[p] = (os.stat(p).st_size, os.stat(p).st_mtime)
        assert before == after, (
            "스캐너가 파일을 만들거나 고쳤다 — 수집기는 읽기 전용이다:\n%r\n%r"
            % (sorted(set(after) - set(before)), sorted(set(before) - set(after))))
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    for fn in (test_multiline_item_is_read_as_one_item,
               test_range_bracket_is_not_a_log_tag,
               test_resolved_item_is_not_reported,
               test_absent_log_tag_is_not_reported,
               test_window_is_counted_in_trading_days_not_sessions,
               test_no_logs_today_is_unmeasured_not_zero,
               test_dropped_items_are_counted,
               test_missing_todo_is_an_error_not_silence,
               test_scanner_is_read_only):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
