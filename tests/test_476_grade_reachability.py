# -*- coding: utf-8 -*-
"""[MW0602 476차 / F-6 Phase A] 앙상블 등급 A·B의 **도달 가능성** 불변식.

무엇을 발견했나 (2026-08-19, 리포트 1-9)
----------------------------------------
앙상블 등급식(`model/ensemble_decision.py`)은 `confidence >= 0.70 → A` /
`>= 0.60 → B`인데, **방향성 신호(`direction != 0`)의 confidence 가 2026-06-01 이후
0.60에 한 번도 닿지 않았다**(최근 30거래일 p100 0.5970. `conf≥0.70`은 전 기간
473건 전부 2026-05-08~05-19). 그 결과:

  ① 09:20~09:29 "앙상블 A등급만 허용" 게이트(`main.py`)는 실질 전면 진입 금지
  ② HCGuard(conf≥0.70 롤링 가드)·CRASH 레짐 A등급 숏 예외는 발동 자체가 불가
  ③ `trades.raw_grade` 기록 시작(2026-07-30) 이래 앙상블 `'A'` 0건

471차 F-1(15:10 1차 경로) · 474차(중기/장기 CORE 그룹)와 같은 계열의 구조 결함이며,
약 3개월간 어떤 계측에도 걸리지 않았다.

이 파일이 하는 일 (474차 `test_473_core_group_reachability.py` 방식)
--------------------------------------------------------------------
**이 상태를 "정상"이라고 주장하지 않는다.** 임계 재설계는 주간회의(2026-08-22)
안건이고 CLAUDE.md 「확률 판단 기준」 각주가 사실을 병기한다. 여기서는 현재 정의를
**명시적으로 고정**해, 등급식·임계가 바뀌면 테스트가 깨져 문서 갱신을 강제한다.

G-5 규약: 라이브 **분포**에 의존하는 단언은 CI에서 불안정하므로 점검 도구(수집기
§12b 임계-분포 대조, G-4)가 매일 재고, 여기서는 **정의 대조**만 한다. DB 확인
테스트는 DB가 없거나 잠겨 있으면 skip 한다.

실행:
    pytest tests/test_476_grade_reachability.py
"""
import io
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ.setdefault("MIREUK_TEST_MODE", "1")

#: 2026-08-19 실측으로 고정한 앙상블 등급 임계. 여기가 바뀌면
#: CLAUDE.md 「확률 판단 기준」 각주와 main.py 09:20~09:29 게이트 로그 문구,
#: 수집기 threshold_reachability 쌍(§12b)도 함께 바뀌어야 한다.
_DECLARED_GRADE_A_THR = 0.70
_DECLARED_GRADE_B_THR = 0.60

#: 도달 불가로 **확인된** 등급. 비어 있지 않다는 것 자체가 미해결 안건이다
#: (주간회의 2026-08-22 — 임계 재설계 vs 09:20~09:29 금지 존 재정의).
_DECLARED_UNREACHABLE_GRADES = {"A", "B"}

_ENSEMBLE_SRC = os.path.join(_ROOT, "model", "ensemble_decision.py")


def _src():
    with io.open(_ENSEMBLE_SRC, encoding="utf-8") as f:
        return f.read()


def test_grade_thresholds_pinned_in_source():
    """등급식의 A/B 임계가 선언값과 같은가 — 소스 대조.

    실패하면 임계가 바뀐 것이다. 그 자체는 좋은 변화일 수 있으나(주간회의 결정),
    CLAUDE.md 「확률 판단 기준」 각주 · main.py 게이트 로그 문구 · 수집기 §12b
    임계쌍 · 이 파일의 선언을 **함께** 갱신해야 한다.
    """
    src = _src()
    m_a = re.search(r"elif confidence >= (0\.\d+):\s*\n\s*# Grade A", src)
    assert m_a, ("앙상블 등급식에서 A 임계 분기(`elif confidence >= X:` + Grade A 주석)를 "
                 "찾지 못했다 — 등급식 구조가 바뀌었다. 이 테스트와 CLAUDE.md 각주를 갱신할 것.")
    assert float(m_a.group(1)) == _DECLARED_GRADE_A_THR, (
        "앙상블 A 임계가 바뀌었다: %s (선언: %s). CLAUDE.md 「확률 판단 기준」 각주와 "
        "main.py 09:20~09:29 게이트 문구, 수집기 §12b 임계쌍을 함께 갱신할 것."
        % (m_a.group(1), _DECLARED_GRADE_A_THR))

    m_b = re.search(r"elif confidence >= (0\.\d+):\s*\n\s*grade = \"B\"", src)
    assert m_b, "앙상블 등급식에서 B 임계 분기를 찾지 못했다 — 이 테스트를 갱신할 것."
    assert float(m_b.group(1)) == _DECLARED_GRADE_B_THR, (
        "앙상블 B 임계가 바뀌었다: %s (선언: %s). 같은 문서들을 함께 갱신할 것."
        % (m_b.group(1), _DECLARED_GRADE_B_THR))


def test_entry_grades_still_declared():
    """ENTRY_GRADE 에 A/B가 여전히 존재하는가.

    존재하는데 도달 불가라는 것이 1-9의 핵심이다 — A/B를 설정에서 지우는 것(처분 안)도,
    임계를 내려 되살리는 것도 이 테스트를 깨고 문서 갱신을 강제한다.
    """
    from config.settings import ENTRY_GRADE
    for g in _DECLARED_UNREACHABLE_GRADES:
        assert g in ENTRY_GRADE, (
            "ENTRY_GRADE 에서 %r 이 사라졌다 — 1-9 처분이 결정된 것이므로 "
            "CLAUDE.md 각주·이 파일의 선언을 갱신할 것." % g)


def test_entry_gate_log_carries_the_fact():
    """main.py 09:20~09:29 게이트 로그가 실측 사실을 병기하는가 (F-6 Phase A).

    이 문구가 사라지면 — 게이트가 재설계됐거나(좋은 변화) 문구만 되돌아간 것이다.
    어느 쪽이든 CLAUDE.md 각주와 함께 갱신해야 한다.
    """
    with io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        src = f.read()
    assert "앙상블 A등급만 허용" in src and "실질 전면 금지(1-9)" in src, (
        "09:20~09:29 게이트 로그의 사실 병기(476차 F-6 Phase A)가 사라졌다 — "
        "임계가 재설계됐다면 CLAUDE.md 「확률 판단 기준」 각주와 이 테스트를 함께 갱신할 것.")


def test_directional_confidence_still_below_B():
    """방향성 conf 가 여전히 B 임계(0.60) 미만인지 — 1-9 안건이 살아 있음을 확인한다.

    ⚠ 이 테스트가 **통과하는 것은 좋은 상태가 아니다.** 통과 = A/B 도달 불가가
      그대로라는 뜻이다. 실패(=도달 가능해짐)하면 1-9가 해소된 것이므로
      `_DECLARED_UNREACHABLE_GRADES` 와 CLAUDE.md 각주를 갱신할 것.
    ⚠ 라이브 분포 의존 — DB가 없거나 잠겨 있으면 skip (G-5: 분포 감시는 §12b의 몫).
    """
    import sqlite3
    import pytest

    db = os.path.join(_ROOT, "data", "db", "predictions.db")
    if not os.path.exists(db):
        pytest.skip("predictions.db 없음 — 이 PC에서는 분포 확인 불가")
    uri = "file:%s?mode=ro" % db.replace("\\", "/")
    try:
        con = sqlite3.connect(uri, uri=True, timeout=3.0)
        try:
            row = con.execute(
                "select max(confidence), count(*) from ensemble_decisions "
                " where direction != 0 and ts >= date('now', '-30 day')").fetchone()
        finally:
            con.close()
    except Exception as e:
        pytest.skip("predictions.db 접근 실패(%s) — 분포 확인 불가" % e)

    mx, n = row or (None, 0)
    if not n:
        pytest.skip("최근 30일 방향성 신호 0건 — 판정 보류")
    assert mx < _DECLARED_GRADE_B_THR, (
        "방향성 conf 최대 %.4f ≥ %.2f — 앙상블 B(나아가 A)가 도달 가능해졌다. "
        "1-9 가 해소된 것이므로 이 파일의 선언과 CLAUDE.md 「확률 판단 기준」 각주를 "
        "갱신할 것." % (mx, _DECLARED_GRADE_B_THR))
