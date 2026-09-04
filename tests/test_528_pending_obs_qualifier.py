# -*- coding: utf-8 -*-
"""[MW0602 528차 후속 / 장후 자동조치] 회귀 — 수집기 §11 미판정 관측의 **부분일치 오탐**.

**무엇이 문제였나.** 526차 후속3이 만든 `scan_pending_observations()` 는 항목의
백틱 안에서 로그 태그 `[Tag]` 만 뽑아, 그 리터럴이 **오늘 자 로그 파일 어딘가에**
있으면 「판정 조건 충족」으로 §11 적신호에 올렸다. 그러자 2026-09-04 장후 점검에서
`O-58` 이 그대로 걸렸다 — 판정 대상은 EOD DB 정리 `[Retrain] DB pruning` 인데,
매일 찍히는 호라이즌별 재학습 `[Retrain] 3m 교체 보류` 의 `[Retrain]` 에 걸린 것이다.
사람이 직접 로그를 열어보고서야 오탐임을 규명했다(0904 리포트 §2 「확인 필요」).

🔴 **반대 방향의 고장을 같이 막아야 한다.** "그러면 한정어를 전부 요구하자"가
자연스러운 반응이지만, 실측상 한정어의 상당수는 `[IntradayRegime] NORMAL → CRASH |
day=-0.09% atr=1.00 z=5` 처럼 **등록 당시 사건의 예시**라 두 번 다시 나오지 않는다.
전부 강제하면 이 기능은 조용히 0건을 내고, 그것이 곧 FP-CRITICAL(2개월 PSI=0.0)·
TOX 죽은 섀도(한 달)와 같은 「만든 날부터 죽은 계측」이다.

→ 그래서 문턱을 올리는 대신 **일치 강도를 등급으로 나눴다.** 아래 불변식은 그
   양쪽을 함께 고정한다.

여기서 고정하는 불변식:

① **한정어가 있는데 같은 줄에서 안 맞으면 `weak`** — 「충족」으로 올리지 않는다.
   (`O-58` 오탐 그 자체)
② **한정어까지 한 줄에서 맞으면 `strong`** — 진짜 충족은 계속 올라온다.
③ **한정어가 안 맞아도 행을 지우지는 않는다** — 억제가 아니라 가시화다.
   `missing` 에 무엇이 없었는지 남긴다(계측 4원칙 ③).
④ **줄 경계를 넘어 조립하지 않는다** — 태그가 A줄, 한정어가 B줄에 있으면 `strong`
   이 아니다. 파일 전체 substring 대조가 오탐의 직접 원인이었다.
⑤ **자리표시자는 요구에서 뺀다** — `count=N` 의 `N` 을 요구하면 맞는 줄도 못 찾는다.
⑥ **한정어가 없는 항목은 종전대로 태그만으로 뜬다** — 526차 탐지력을 깎지 않는다.
⑦ **판정·매매에 관여하지 않는다** — 수집기는 로그를 읽어 리포트를 쓸 뿐이다.

실행:
    py37_32\\python.exe tests/test_528_pending_obs_qualifier.py
"""
import io
import os
import json
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
DAY = datetime.date(2026, 9, 4)
_LOG_DAYS = ("20260901", "20260902", "20260903", "20260904")

# `O-58` 의 실제 형태 — 판정 조건이 **태그 + 한정어**다(태그만으로는 매일 맞는다).
TODO_O58 = u"""# NEXT TODO

## 2026-09-01 (MW0602 511차 — 일일 점검: 장후)

- [ ] **O-58** EOD DB pruning 재시도 — **2026-09-07(다음 월요일) EOD**.
      통과: `[Retrain] DB pruning` 성공(`반환>0행`) 또는 삭제 대상 없음 정상 종료.
"""

# 오늘 자 로그 — **호라이즌별 재학습만** 있다. `[Retrain]` 은 있고 `DB pruning` 은 없다.
LOG_RETRAIN_ONLY = (
    u"15:45:33 [WARNING] [Retrain] 1m 교체 보류(EOD 모델가드) - acc 하락 0.0271\n"
    u"15:45:36 [WARNING] [Retrain] 3m 교체 보류(EOD 모델가드) - acc 하락 0.0485\n")
LOG_WITH_PRUNING = LOG_RETRAIN_ONLY + \
    u"15:47:01 [Retrain] DB pruning 완료 - 반환 1,204행\n"
# ④ 태그와 한정어가 **다른 줄**에 흩어진 경우.
LOG_SPLIT_LINES = LOG_RETRAIN_ONLY + \
    u"15:47:01 [DBQueue] DB pruning 후보 집계 완료\n"


def _cfg():
    """수집기 기본 설정만 쓴다 — 저장소 사용자 설정에 의존하면 PC 별로 갈린다."""
    return json.loads(json.dumps(ce.DEFAULT_CONFIG))


def _fixture(todo_body, log_text, log_days=_LOG_DAYS):
    """스크래치 저장소를 만든다 — 실 저장소를 입력으로 쓰지 않는다(고정 입력)."""
    root = tempfile.mkdtemp(prefix="t528_")
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


def _row(res, oid):
    hits = [r for r in res["rows"] if r["id"] == oid]
    return hits[0] if hits else None


def test_tag_only_match_is_not_reported_as_satisfied():
    """① `O-58` 오탐 그 자체 — 태그만 맞으면 「충족」이 아니다."""
    root = _fixture(TODO_O58, LOG_RETRAIN_ONLY)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        row = _row(r, "O-58")
        assert row is not None, (
            "행 자체가 사라졌다 — 억제가 아니라 가시화여야 한다: %r" % r)
        assert row["match"] == "weak", (
            "`[Retrain] DB pruning` 이 `[Retrain] 3m 교체 보류` 에 걸려 「충족」으로 "
            "올라왔다 — 0904 O-58 오탐 재발: %r" % row)
        assert r.get("strong") == 0 and r.get("weak") == 1, r
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_qualifier_match_on_one_line_is_strong():
    """② 진짜 충족은 계속 올라온다 — 탐지력을 깎지 않았다."""
    root = _fixture(TODO_O58, LOG_WITH_PRUNING)
    try:
        r = ce.scan_pending_observations(root, _cfg(), DAY)
        row = _row(r, "O-58")
        assert row is not None and row["match"] == "strong", (
            "한정어까지 있는데도 못 올렸다 — 526차 G-1 의 탐지력이 죽었다: %r" % r)
        assert r.get("strong") == 1, r
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_weak_row_names_what_was_missing():
    """③ 무엇이 없어서 약한 일치인지 남긴다(계측 4원칙 ③ 탈락 가시화)."""
    root = _fixture(TODO_O58, LOG_RETRAIN_ONLY)
    try:
        row = _row(ce.scan_pending_observations(root, _cfg(), DAY), "O-58")
        assert row and row.get("missing"), (
            "약한 일치인데 무엇이 빠졌는지 안 남겼다 — 사람이 다시 로그를 뒤져야 "
            "한다: %r" % row)
        assert any(u"pruning" in m for m in row["missing"]), row
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_qualifier_must_match_on_the_same_line():
    """④ 태그와 한정어가 **다른 줄**에 흩어져 있으면 `strong` 이 아니다.

    파일 전체 substring 대조가 528차 이전 오탐의 직접 원인이었다.
    """
    root = _fixture(TODO_O58, LOG_SPLIT_LINES)
    try:
        row = _row(ce.scan_pending_observations(root, _cfg(), DAY), "O-58")
        assert row is not None and row["match"] == "weak", (
            "`[Retrain]` 과 `DB pruning` 이 서로 다른 줄에 있는데 충족으로 읽었다 — "
            "줄 경계를 넘어 조립하면 안 된다: %r" % row)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_placeholder_tokens_are_not_required():
    """⑤ `count=N` 의 `N` 은 자리표시자다 — 요구에 넣으면 맞는 줄도 못 찾는다."""
    todo = u"""# NEXT TODO

## 2026-09-01 (MW0602 511차 — 일일 점검: 장후)

- [ ] **O-47** 판정식: `[GUARD] running-probe count=N probe=ok` 가 로그에 있어야 한다.
"""
    root = _fixture(todo, u"08:40:02 [GUARD] running-probe count=0 probe=ok\n")
    try:
        row = _row(ce.scan_pending_observations(root, _cfg(), DAY), "O-47")
        assert row is not None and row["match"] == "strong", (
            "자리표시자 `N` 을 리터럴로 요구해 실제 발화(`count=0`)를 놓쳤다 — "
            "한정어 강제가 반대 방향으로 고장난 형태다: %r" % row)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_bare_tag_item_still_reported():
    """⑥ 한정어가 없는 항목은 종전대로 태그만으로 뜬다(526차 동작 보존)."""
    todo = u"""# NEXT TODO

## 2026-09-01 (MW0602 511차 — 일일 점검: 장후)

- [ ] **O-55** 판정 분모 고정 — `[SizerMatch]` 건수가 아니라 DB 행으로 센다.
"""
    root = _fixture(todo, u"09:53:54 [SizerMatch] qty=2 binding=hurst\n")
    try:
        row = _row(ce.scan_pending_observations(root, _cfg(), DAY), "O-55")
        assert row is not None and row["match"] == "strong", (
            "한정어 없는 항목까지 약한 일치로 강등됐다 — 526차 탐지력이 깎였다: %r" % row)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_scanner_is_read_only():
    """⑦ 스캐너는 저장소를 쓰지 않는다 — 수집기는 읽기 전용이다(SKILL.md §2)."""
    root = _fixture(TODO_O58, LOG_RETRAIN_ONLY)
    try:
        def snap():
            out = {}
            for dirpath, _dn, fns in os.walk(root):
                for fn in fns:
                    p = os.path.join(dirpath, fn)
                    out[p] = (os.stat(p).st_size, os.stat(p).st_mtime)
            return out
        before = snap()
        ce.scan_pending_observations(root, _cfg(), DAY)
        assert before == snap(), (
            "스캐너가 파일을 만들거나 고쳤다 — 수집기는 읽기 전용이다")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    for fn in (test_tag_only_match_is_not_reported_as_satisfied,
               test_qualifier_match_on_one_line_is_strong,
               test_weak_row_names_what_was_missing,
               test_qualifier_must_match_on_the_same_line,
               test_placeholder_tokens_are_not_required,
               test_bare_tag_item_still_reported,
               test_scanner_is_read_only):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print(u"전부 통과" if not FAILURES
          else u"실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
