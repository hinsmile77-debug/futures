# -*- coding: utf-8 -*-
"""[MW0602 485차] 방향 무효화 관측성 — 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: dev_memory/DECISION_LOG.md 2026-08-23 485차)
────────────────────────────────────────────────────────────────────────────
STEP6 이후 게이트 6종(RegimeOverride·FP-CRITICAL·RegimeChampGate·σ미수집·
조건부구간·ATR저변동)이 로컬 `direction`을 0으로 지우면, 사유 체인과 축 루프의
바깥 가드(`if direction != 0 and FLAT:`)가 거짓이 되어 **기록 계층 자체가 도달
불가**가 된다. 그 결과 entry_block_reason="" · entry_block_axes="" 로 저장돼
퍼널 분류기 3곳이 "차단없음"으로 오집계했다(2026-06-02~ 실측 544건 — 출처는
checklist_reason 에만 남아 1등 사유 컬럼과 갈렸다).

지키는 불변식:
  T1  `_direction_zeroed_by = ""` 초기화가 **6개 대입 지점 전부보다 앞**에 있다
      (400차 UnboundLocalError 유형 방지 — 조건분기 밖 초기화).
  T2  무효화 지점 6곳 모두 first-wins(`or`) 대입이 붙어 있다.
  T3  사유 체인 뒤 보강 분기가 존재하고, **원신호 조건**
      (`decision.get("direction")!= 0`)을 포함한다 — 원래 무신호는 계속 "" 다
      (336차 "진입 성공 분 오탐"과 같은 유형을 만들지 않는다).
  T4  축 루프의 기존 가드는 무변경이고(미정의 변수 참조 위험 0 원칙),
      join 앞에 `direction_zeroed` 단독 축 보강이 존재한다.
  T5  entry_gate_json 에 `direction_zeroed_by` 관측 필드가 있고 `qty_ok` 의
      정의는 무변경이다(시계열 연속성).
  T6  신설 문구가 db_utils 분류기에서 "방향무효화(신호소거)" 로 분류된다.
  T7  신설 문구가 gate_blocking_report 분류기에서도 미분류로 새지 않는다.
  T8  신설 needle 이 기존 분류를 가로채지 않는다(JointGateBlock·게이트강등 등).

실행: python tests/test_485_direction_zeroed_visibility.py   (COM/브로커 불필요)
"""

import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


_MAIN = io.open(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py"),
    encoding="utf-8",
).read()

_KEYS = (
    "REGIME_OVERRIDE", "FP_CRITICAL", "REGIME_CHAMP_NONE",
    "SIGMA_WARMUP_0920", "OPEN_A_ONLY_0920_0929", "ATR_LOW_TF",
)


def test_t1_init_before_all_assignments():
    init = _MAIN.find('_direction_zeroed_by = ""')
    check("T1: 초기화 존재", init > 0)
    for k in _KEYS:
        pos = _MAIN.find('_direction_zeroed_by or "%s"' % k)
        check("T1: 초기화가 %s 대입보다 앞" % k, 0 < init < pos)


def test_t2_first_wins_at_all_six():
    for k in _KEYS:
        pat = '_direction_zeroed_by = _direction_zeroed_by or "%s"' % k
        check("T2: first-wins 대입 존재 — %s" % k, pat in _MAIN)
    # first-wins 가 아닌 무조건 대입(재대입으로 출처가 덮이는 형태)이 없는가
    bad = re.findall(r'_direction_zeroed_by = "(?!")', _MAIN)
    check("T2: 무조건 대입 없음(초기화 제외)", len(bad) == 0)


def test_t3_reason_backfill():
    m = re.search(
        r'if \(not _entry_block_reason\) and _direction_zeroed_by.*?'
        r'int\(decision\.get\("direction", 0\) or 0\) != 0.*?'
        r'\[차단\] 방향 무효화',
        _MAIN, re.S)
    check("T3: 체인 뒤 보강 분기 존재(원신호 조건 포함)", m is not None)
    # FLAT 조건도 있는가 — 포지션 보유 중 재평가 생략 분과 섞이지 않도록
    seg = m.group(0) if m else ""
    check("T3: FLAT 조건 포함", 'self.position.status == "FLAT"' in seg)


def test_t4_axes_guard_unchanged_and_backfill():
    # 축 루프의 기존 가드 원형 유지
    check("T4: 축 루프 가드 무변경",
          'if direction != 0 and self.position.status == "FLAT":' in _MAIN)
    m = re.search(
        r'if _direction_zeroed_by and not _block_axes.*?'
        r'_block_axes\.append\("direction_zeroed"\)',
        _MAIN, re.S)
    check("T4: join 앞 direction_zeroed 보강 존재", m is not None)


def test_t5_gate_json_field():
    check("T5: gate_json 관측 필드 존재",
          '"direction_zeroed_by": _direction_zeroed_by or None' in _MAIN)
    check("T5: qty_ok 정의 무변경",
          '"qty_ok":           _qty_display > 0,' in _MAIN)


def test_t6_db_utils_classifier():
    from utils.db_utils import _categorize_block_reason
    got = _categorize_block_reason(
        "[차단] 방향 무효화 — SIGMA_WARMUP_0920 (원신호 dir=-1)", "")
    check("T6: db_utils 분류 = 방향무효화(신호소거) (got=%r)" % got,
          got == "방향무효화(신호소거)")


def test_t7_report_classifier():
    from scripts.generate_gate_blocking_report import _classify_block_reason
    got = _classify_block_reason(
        "[차단] 방향 무효화 — REGIME_OVERRIDE (원신호 dir=+1)")
    check("T7: 리포트 분류 미분류 아님 (got=%r)" % got, got != "미분류")


def test_t8_no_hijack():
    from utils.db_utils import _categorize_block_reason
    keep = [
        ("JointGateBlock — meta 0.44", "JointGateBlock"),
        ("[차단] 게이트 강등 X — ToxicityGate", "게이트강등(Toxicity)"),
    ]
    for reason, want in keep:
        got = _categorize_block_reason(reason, "")
        check("T8: 기존 분류 유지 — %s (got=%r)" % (want, got), got == want)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_t1_init_before_all_assignments, test_t2_first_wins_at_all_six,
               test_t3_reason_backfill, test_t4_axes_guard_unchanged_and_backfill,
               test_t5_gate_json_field, test_t6_db_utils_classifier,
               test_t7_report_classifier, test_t8_no_hijack):
        try:
            fn()
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
