# -*- coding: utf-8 -*-
"""[MW0601 500차] 미해결 KNOWN 가시성 회귀 테스트 — §2-d.

────────────────────────────────────────────────────────────────────────────
무엇을 막는 테스트인가
────────────────────────────────────────────────────────────────────────────
`feature_health_report.KNOWN` 등재는 그 피처를 **8곳의 경보에서 뺀다**
(§1 `실이상` 열 · §2-b · §2-c · "신규 이상" 줄 · 유령 신규 카운트 · EOD 요약 …).
등급 자체는 남지만 "봐야 할 새 이상" 목록에서 사라진다.

그런데 KNOWN 부패 점검이 잡는 것은 ① 데이터에 없음 ② 등급이 OK로 해소, 둘뿐이다.
**"등재됐고, 여전히 아프고, 아무도 안 고친다"** 는 상태는 어디에도 안 잡혔다 —
오히려 DEAD/CRITICAL로 남아 있는 한 영원히 조용하다.

2026-08-30 실측: KNOWN 13건 중 **11건이 미결**, 전부 등재 33일째 그대로.
`cvd`의 등재 사유가 문자 그대로 "미해결 등록"인데도 억제는 100% 작동했다.
FP-CRITICAL 죽은 게이트(2개월 PSI=0.0)·TOX 죽은 섀도(한 달 무배선)와 같은 계열이며,
CB②·CB③-P4의 "재검토하기로 했는데 안 함"과도 같은 형태다.

§2-d가 그 사각지대를 덮는다. 이 테스트는 §2-d가 **다시 죽지 않게** 고정한다.

  R1 `known_registered_dates()`가 `git blame`을 쓰지 않는다
       ← blame은 그 줄을 마지막으로 손댄 커밋을 가리켜, **사유 문자열만 고쳐도
         방치 시계가 0으로 리셋**된다. 재려는 것이 "얼마나 방치됐나"인데
         "주석만 만지면 깨끗해지는" 정반대 유인이 된다. 실측 차이도 있었다 —
         `program_*` 2종이 blame 21일 vs 최초등재 33일.
  R2 EOD 요약 줄에 KNOWN 미결 건수가 들어간다 (체인 stdout tail로 로그에 남는 경로)
  R3 분류 누락 0 — unresolved+resolved+gone == len(KNOWN)   [계측 4원칙 ③ 탈락 가시화]
  R4 미결 항목은 §2-d 본문에 **이름으로** 나타난다            ← 핵심 불변식
  R5 억제는 그대로 — 미결 항목은 §2-b(system_bad)·§1(real_bad)에서 계속 빠진다
  R6 `max_age_days`가 미결 항목의 실제 최댓값과 일치 (요약 줄 숫자의 근거)

R3~R6은 `raw_data.db`가 있어야 실행된다. 없으면 ⏳로 **명시**하고 넘어간다 —
조용히 통과시키면 402차 후속3(자기모순 조건으로 3개월 0건 방치)과 같은 사고가 된다.

실행: python tests/test_500_known_unresolved_visible.py   (COM/브로커 불필요)
            또는 pytest tests/test_500_known_unresolved_visible.py

🔴 [MW0602 O-77-C 배포] **스크립트형 → pytest 전환.**

검사 문구와 조건은 **원문 그대로**다. `# ── Rn ──` 배너를 경계로 블록을 함수로
감싸 그룹별 테스트에서 부른다. 모듈 최상위 계산(소스 읽기)은 지연 생성으로 바꿨다
— 모듈 최상위에 남기면 `O-77` 2차층(수집 중 중단)이 재발한다.

⚠ **DB 부재 시 `pytest.skip` 을 쓰지 않는다.** 이 파일은 이미 자체 `skip()` 으로
  「⏳ 통과가 아니라 미실행」을 출력·집계한다. 바꾸면 그 문구가 사라져 검사 이름
  집합이 달라진다. 미실행은 종전대로 `SKIPPED` 에 남는다.
"""

import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()


# ⚠ `utf8_console()` 은 import 시점에 부르지 않는다 — CLI 러너에서만.

import scripts.generate_featureset_health_report as R  # noqa: E402
from scripts.feature_health_report import (  # noqa: E402
    KNOWN, DEAD_LEVEL, CRIT_LEVEL, WARN_LEVEL,
)

FAILURES = []
SKIPPED = []


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("OK" if cond else "FAIL", name,
                         ("  — %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)
    return cond


def skip(name, why):
    print("[ ⏳ ] %s — %s (통과가 아니라 미실행)" % (name, why))
    SKIPPED.append(name)


def _assert_group(fn):
    """블록을 실행하고 **그 안에서 난 실패만** 모아 단언한다.

    `skip()` 은 `SKIPPED` 로 가므로 여기서 실패로 세지 않는다 — 종전 동작과 같다.
    """
    before = len(FAILURES)
    fn()
    new = FAILURES[before:]
    assert not new, "실패 %d건 — %s" % (len(new), " / ".join(new))


_SRC_CACHE = {}


def _src_text():
    """`generate_featureset_health_report.py` 원문 — R1·R2 가 정적으로 검사한다."""
    if "t" not in _SRC_CACHE:
        SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "scripts", "generate_featureset_health_report.py")
        src_text = io.open(SRC, encoding="utf-8").read()
        _SRC_CACHE["t"] = src_text
    return _SRC_CACHE["t"]


# ──────────────────────────────────────────────────────────────
# R1·R2 — 정적 검사 (DB 불필요)
# ──────────────────────────────────────────────────────────────

def _r1_r2():
    src_text = _src_text()
    # R1 — 등재일 산출이 blame이면 방치 시계가 리셋된다.
    #     docstring에는 "blame을 쓰지 않는다"는 설명이 있으므로, 함수 본문만 잘라서 본다.
    _fn = re.search(r"def known_registered_dates\(\).*?(?=\ndef )", src_text, re.S)
    _body = _fn.group(0) if _fn else ""
    _code = re.sub(r'"""".*?"""|"""(.|\n)*?"""', "", _body)   # docstring 제거
    check("R1 known_registered_dates()가 git blame을 쓰지 않는다",
          bool(_body) and '"blame"' not in _code and "'blame'" not in _code,
          "blame은 마지막 수정 커밋을 가리켜 사유 문구만 고쳐도 방치일이 0으로 리셋된다")
    check("R1b 최초 등재 커밋을 찾는다 (git log -S --reverse)",
          '"-S"' in _code and '"--reverse"' in _code)

    # R2 — EOD 로그 경로. 체인(campaign_steps)이 이 스텝 stdout의 tail을 로그에 찍으므로,
    #      요약 줄에 들어 있으면 별도 체인 스텝 없이 EOD 로그에서 grep 된다.
    check("R2 EOD 요약 줄에 'KNOWN 미결'이 포함된다",
          "KNOWN 미결 %s" in src_text and 'known_status' in src_text)


def test_R1_R2_static_checks():
    """등재일 산출이 blame 이 아니고, EOD 요약에 「KNOWN 미결」이 실리는가."""
    _assert_group(_r1_r2)


# ──────────────────────────────────────────────────────────────
# R3~R6 — 실제 리포트 생성 (raw_data.db 필요)
# ──────────────────────────────────────────────────────────────

def _r3_r6():
    if not os.path.exists(R.RAW_DB):
        for n in ("R3 분류 누락 0", "R4 미결 항목이 §2-d에 보인다",
                  "R5 억제 보존", "R6 max_age_days 일치"):
            skip(n, "raw_data.db 없음")
    else:
        md, metrics = R.build_report(days=20, pool_days=60)
        ks = metrics.get("known_status") or {}
        unresolved = ks.get("unresolved") or []
        resolved = ks.get("resolved") or []
        gone = ks.get("gone") or []

        # R3 — 어느 갈래로도 안 센 KNOWN 항목이 있으면 그 항목은 다시 사각지대다.
        total = len(unresolved) + len(resolved) + len(gone)
        check("R3 분류 누락 0 (unresolved+resolved+gone == len(KNOWN))",
              total == len(KNOWN),
              "%d != %d — 어느 갈래에도 안 잡힌 KNOWN 항목이 있다" % (total, len(KNOWN)))

        # R4 — 핵심. 억제된 항목이 §2-d 본문에 이름으로 나와야 한다.
        _sec = ""
        if "### 2-d." in md:
            _tail = md[md.index("### 2-d."):]
            _sec = _tail.split("## 3.")[0]
        check("R4a §2-d 절이 리포트에 존재한다", bool(_sec))
        missing = [r["feature"] for r in unresolved
                   if "`%s`" % r["feature"] not in _sec]
        check("R4b 미결 %d건이 전부 §2-d에 이름으로 보인다" % len(unresolved),
              not missing, "누락: %s" % ", ".join(missing))
        if unresolved:
            check("R4c 등급이 실제로 나쁜 것만 미결로 센다",
                  all(r["level"] in (DEAD_LEVEL, CRIT_LEVEL, WARN_LEVEL)
                      for r in unresolved),
                  "미결 목록에 OK/미계측이 섞였다")

        # R5 — 억제를 되돌리면 경보 피로가 재발한다(0802 계획 Phase A 확정사항 4번).
        #      §2-d는 "보이게" 할 뿐 "경보로 올리지" 않는다.
        sys_bad = set(metrics.get("system_bad") or [])
        unk_bad = set(metrics.get("unknown_bad") or [])
        leaked = [r["feature"] for r in unresolved
                  if r["feature"] in sys_bad or r["feature"] in unk_bad]
        check("R5 억제 보존 — 미결 항목이 §2-b·§1 실이상에 새지 않는다",
              not leaked, "누출: %s" % ", ".join(leaked))

        # R6 — 요약 줄의 "(최장 N일)"이 표와 다른 수를 말하면 안 된다.
        ages = [r["age_days"] for r in unresolved if r.get("age_days") is not None]
        check("R6 max_age_days가 미결 항목 실제 최댓값과 일치",
              ks.get("max_age_days") == (max(ages) if ages else None),
              "요약 %s vs 실제 %s" % (ks.get("max_age_days"),
                                      max(ages) if ages else None))

        print("\n  (참고) KNOWN %d건 = 미결 %d · 해소 %d · 소멸 %d · 최장방치 %s"
              % (len(KNOWN), len(unresolved), len(resolved), len(gone),
                 ks.get("max_age_days")))



def test_R3_R6_report_generation():
    """실제 리포트 생성 경로 — DB 부재 시 ⏳ 로 명시하고 넘어간다(조용한 통과 금지)."""
    _assert_group(_r3_r6)


if __name__ == "__main__":
    from utils.analysis_db import utf8_console

    utf8_console()
    fns = [(n, f) for n, f in sorted(globals().items())
           if n.startswith("test_") and callable(f)]
    ok = fail = 0
    for name, fn in fns:
        try:
            fn()
            print("  PASS %s" % name)
            ok += 1
        except Exception as e:
            print("  FAIL %s -> %s: %s" % (name, type(e).__name__, e))
            fail += 1
    print("")
    if SKIPPED:
        print("⏳ 미실행 %d건: %s" % (len(SKIPPED), ", ".join(SKIPPED)))
    print("%d passed, %d failed (of %d)" % (ok, fail, len(fns)))
    sys.exit(1 if fail else 0)
