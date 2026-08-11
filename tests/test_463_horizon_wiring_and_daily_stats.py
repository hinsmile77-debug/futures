"""[MW0602 463차 C3/C4/C5] 미할당 속성 배선 + daily_stats 리셋 순서 회귀 테스트.

지키려는 불변식 — **진입 판단은 바뀌지 않는다.**
C3(`_entry_horizon_pre`)가 배선되면 MetaGate 스코어링 호라이즌이 실제 진입
호라이즌을 따르지만, 그 인자가 닿는 두 값(entry_quality_prob·quantile_estimate)은
로깅 전용이라 action/size_multiplier에 관여하지 않는다. 체크리스트도 불변이다 —
select_entry_horizon()은 1m/3m/5m만 반환하고 셋 다 CORE 그룹 "short"다.

세부:
  C3  `self._entry_horizon_pre`가 두 read 지점보다 **앞에서** 할당된다.
      1m/3m/5m → 전부 "short" (체크리스트 결과 불변 보장).
      horizon이 meta_gate 내부에서 로깅 전용 2값에만 닿는다.
  C4  `self._entry_horizon`이 STEP6 말미에 할당된다(대시보드 표시 전용).
  C5  SGD 지표를 리셋 **전에** 캡처하고 save_daily_stats가 그 캡처값을 쓴다.
  배치3 META_SCORING_HORIZON_BREAKS 등록 + [2] 결정에 재측정 표시.

실행: python tests/test_463_horizon_wiring_and_daily_stats.py   (COM/브로커/DB 불필요)
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

import config.settings as S

FAILURES = []
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _read(rel):
    with io.open(os.path.join(BASE, rel), encoding="utf-8") as f:
        return f.read()


def _lineno(src, needle, start=0):
    """needle을 포함하는 첫 **코드** 줄 번호(1-base). 없으면 -1.

    ⚠ 주석 줄은 건너뛴다 — 463차 초안 테스트가 자기가 쓴 설명 주석
    (`# ... self._verified_today = 0을 먼저 실행하고 ...`)을 실호출로 잡아
    순서 검사가 거짓 실패했다. 이 파일의 검사는 전부 "실행 순서"에 관한 것이라
    주석을 세면 검사 자체가 무의미해진다.
    """
    for i, line in enumerate(src.splitlines()[start:], start + 1):
        if needle in line and not line.strip().startswith("#"):
            return i
    return -1


MAIN = _read("main.py")


# ══════════════════════════════════════════════════════════════
# C3 — _entry_horizon_pre 배선
# ══════════════════════════════════════════════════════════════
def test_c3_assigned_before_reads():
    """할당이 두 read 지점보다 앞에 있어야 실제로 반영된다."""
    a = _lineno(MAIN, "self._entry_horizon_pre = select_entry_horizon(")
    r1 = _lineno(MAIN, 'entry_horizon      = getattr(self, "_entry_horizon_pre"')
    r2 = _lineno(MAIN, 'horizon=getattr(self, "_entry_horizon_pre"')
    check("_entry_horizon_pre 할당부 존재", a > 0)
    check("체크리스트 선행평가 read 존재", r1 > 0)
    check("MetaGate read 존재", r2 > 0)
    check("할당(%d) < 체크리스트 read(%d)" % (a, r1), 0 < a < r1)
    check("할당(%d) < MetaGate read(%d)" % (a, r2), 0 < a < r2)


def test_c3_uses_threshold_feasibility_and_falls_back():
    """말미 확정값과 같은 입력·같은 함수를 쓰고, None이면 '1m' 폴백."""
    m = re.search(
        r'self\._entry_horizon_pre = select_entry_horizon\(\s*'
        r'float\(features\.get\("threshold_feasibility", 1\.0\)\), 1\.0\s*\)\s*or "1m"',
        MAIN)
    check("threshold_feasibility 입력 + '1m' 폴백", m is not None)
    # 말미 확정부와 동일 함수·동일 인자 형태여야 두 값이 항상 일치한다
    check("말미 확정부도 select_entry_horizon(_tf, 1.0)",
          "_entry_horizon = select_entry_horizon(_tf, 1.0)" in MAIN)


def test_c3_does_not_duplicate_low_vol_block():
    """저변동성 차단은 말미 1곳뿐 — pre에서 중복 차단하면 차단 시점이 앞당겨진다."""
    # pre 할당 직후 블록에 direction=0 을 세우는 코드가 없어야 한다
    a = _lineno(MAIN, "self._entry_horizon_pre = select_entry_horizon(")
    window = "\n".join(MAIN.splitlines()[a:a + 6])
    check("pre 경로에 direction=0 중복 차단 없음", "direction = 0" not in window)
    check("저변동성 차단 로그는 여전히 1곳", MAIN.count("→ 저변동성 진입 차단") == 1)


def test_c3_checklist_result_is_invariant():
    """1m/3m/5m가 전부 같은 CORE 그룹이라야 체크리스트 결과가 불변이다.

    이 불변식이 깨지면 C3 배선이 **진입 판단을 바꾸는 변경**으로 승격된다 —
    그때는 섀도·플래그 게이트가 필요하다.
    """
    from model.ensemble_decision import select_entry_horizon
    grp = S.HORIZON_CORE_GROUP
    outs = set()
    for tf in (0.0, 0.5, 0.79, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0, 50.0):
        outs.add(select_entry_horizon(tf, 1.0))
    check("select_entry_horizon 출력이 {None,1m,3m,5m} 뿐",
          outs <= {None, "1m", "3m", "5m"})
    groups = {grp.get(h) for h in ("1m", "3m", "5m")}
    check("1m/3m/5m가 전부 동일 CORE 그룹(short)", groups == {"short"})
    check("checklist는 entry_horizon을 CORE 그룹 결정에만 사용",
          _read("strategy/entry/checklist.py").count("entry_horizon") == 3)


def test_c3_horizon_touches_logging_only_values():
    """meta_gate 내부에서 horizon이 닿는 곳이 로깅 전용 2값 + 반환 키뿐이어야 한다.

    action/size_multiplier 계산에 끼어들면 C3는 진입 판단 변경이 된다.
    """
    mg = _read("strategy/entry/meta_gate.py")
    body = mg.split("entry_quality_prob = self._eq_scorer.score(horizon, features)")[1]
    # action/size 계산 구간(반환 dict 이전)에서 두 값이 쓰이면 안 된다
    calc = body.split('"action":')[0]
    check("action 계산 전 구간에서 entry_quality_prob 미사용",
          "entry_quality_prob" not in calc.replace(
              "entry_quality_prob = self._eq_scorer", ""))
    check("meta_gate가 로깅 전용임을 주석으로 명시",
          "action/size_multiplier 결정에는 관여하지 않는다" in mg)
    # main.py 소비처도 기록 전용
    check("main.py quantile_estimate 소비가 기록 전용",
          "리스크 판단 무관여" in MAIN)


# ══════════════════════════════════════════════════════════════
# C4 — self._entry_horizon 배선
# ══════════════════════════════════════════════════════════════
def test_c4_assigned():
    a = _lineno(MAIN, 'self._entry_horizon = _entry_horizon or "1m"')
    r = _lineno(MAIN, 'entry_horizon=getattr(self, "_entry_horizon", "1m")')
    check("self._entry_horizon 할당부 존재", a > 0)
    check("update_shap read 존재", r > 0)
    # read는 별도 메서드(_refresh_shap)라 줄 순서는 무의미 — 할당 존재만 본다
    check("할당이 STEP6 말미(_entry_horizon 확정) 뒤",
          a > _lineno(MAIN, "_entry_horizon = select_entry_horizon(_tf, 1.0)"))


# ══════════════════════════════════════════════════════════════
# C5 — daily_stats 리셋 순서
# ══════════════════════════════════════════════════════════════
def test_c5_capture_before_reset_before_save():
    cap = _lineno(MAIN, "_sgd_acc_eod = self.online_learner.recent_accuracy()")
    rst1 = _lineno(MAIN, "self.online_learner.reset_daily()")
    rst2 = _lineno(MAIN, "self._verified_today = 0")
    sav = _lineno(MAIN, '"sgd_accuracy":   _sgd_acc_eod,')
    check("캡처부 존재", cap > 0)
    check("저장부가 캡처값을 사용", sav > 0)
    check("캡처(%d) < online_learner.reset_daily(%d)" % (cap, rst1), 0 < cap < rst1)
    check("캡처(%d) < _verified_today=0 (%d)" % (cap, rst2), 0 < cap < rst2)
    check("리셋(%d) < 저장(%d)" % (rst2, sav), rst2 < sav)
    check("저장부에 라이브 재조회가 남아있지 않음",
          '"sgd_accuracy":   self.online_learner.recent_accuracy()' not in MAIN)
    check("verified_count도 캡처값 사용", '"verified_count": _verified_eod,' in MAIN)


def test_c5_capture_is_same_place_as_forward_stats():
    """forward_stats와 같은 지점 — 그쪽은 원래 되어 있었고 이 둘만 빠져 있었다."""
    fs = _lineno(MAIN, "forward_stats = self.position.daily_forward_stats()")
    cap = _lineno(MAIN, "_sgd_acc_eod = self.online_learner.recent_accuracy()")
    check("forward_stats 캡처 직후에 위치 (5줄 이내)", 0 < cap - fs <= 12)


# ══════════════════════════════════════════════════════════════
# 배치3 — 불연속 레지스트리 + [2] 재측정 표시
# ══════════════════════════════════════════════════════════════
def test_break_registry():
    brk = getattr(S, "META_SCORING_HORIZON_BREAKS", None)
    check("META_SCORING_HORIZON_BREAKS 등록", bool(brk))
    if not brk:
        return
    e = brk[0]
    check("경계일 2026-08-12", e.get("date") == "2026-08-12")
    for k in ("label", "cause", "affected_columns", "evidence", "caveat"):
        check("항목에 %s 존재" % k, bool(e.get(k)))
    check("영향 컬럼에 meta_gate_horizon 명시",
          any("meta_gate_horizon" in c for c in e["affected_columns"]))
    check("caveat이 [2] 채널 교락을 지목", "meta_gate" in e["caveat"])


def test_meta_gate_decision_marked_for_remeasure():
    d = S.VALIDATION_CAMPAIGN_DECISIONS.get("meta_gate", {})
    check("[2] 결정 항목 존재", bool(d))
    check("결정 자체는 유지 (탈락 확정)", "탈락 확정" in d.get("decision", ""))
    check("재측정 대상 표시", "재측정" in d.get("decision", ""))
    note = d.get("note", "")
    check("교락 근거(88.9% 불일치) 기재", "88.9" in note)
    check("재개 조건 명시", "재개 조건" in note)
    check("경계 혼용 금지 명시", "META_SCORING_HORIZON_BREAKS" in note)


def test_report_break_badge_wired():
    rep = _read("scripts/generate_validation_campaign_report.py")
    check("META_SCORING_HORIZON_BREAKS import", "META_SCORING_HORIZON_BREAKS" in rep)
    check("scoring_break_caveat 산출", "scoring_break_caveat" in rep)
    check("요약표 배지 배선", "스코어러 경계" in rep)
    check("판정식 무관여 주석", "판정식을 바꾸면 합격선 변경" in rep)
    # 합격선·판정식이 종전 그대로인지 — §9-4 검증시계 리셋 방지
    check("verdict 계산식 무변경",
          'passed = (top_ev > cr["top_ev_min_pt"]) and \\' in rep)


if __name__ == "__main__":
    for fn in sorted(
        [v for k, v in list(globals().items()) if k.startswith("test_")],
        key=lambda f: f.__code__.co_firstlineno,
    ):
        print("\n── %s" % fn.__name__)
        fn()
    print("\n" + "=" * 60)
    if FAILURES:
        print("실패 %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  - %s" % f)
        sys.exit(1)
    print("463차 회귀 테스트 전부 통과")
