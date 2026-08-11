"""[MW0602 459차 F2] SHS CORE 통과율 — 미측정 분리 회귀 테스트.

지키려는 불변식 — **CORE 통과율은 체크리스트가 실제로 돈 분에만 SHS를
감점한다.** 종전에는 신호가 없거나 포지션 보유 중이라 체크리스트가 아예
돌지 않은 분(`_cr is None`)에 통과율 0.0이 들어가 매분 -25점 전액 감점됐다.
측정 안 함 ≠ 전부 탈락.

함께 지키는 것:
  - 체크리스트가 돈 분의 SHS는 종전 값과 **완전히 동일**해야 한다(회귀 금지).
  - StartupWarmup의 `_cr`은 `checks={}`이라 None과 별개 경로였다 — 이것도 미측정.
  - EKS는 안전장치라 **발동 조건을 바꾸지 않는다** — 미측정 봉은 계측(분모)만
    분리하고 `core_pass_count == 0` 판정은 종전 그대로여야 한다.

실행: python tests/test_459_shs_core_measured.py   (COM/브로커 불필요)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

from safety.system_health import SystemHealthScore

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def test_unmeasured_does_not_penalize():
    """미측정(None) 분에는 CORE 감점이 없어야 한다 — F2 핵심."""
    sh = SystemHealthScore()
    sh.update_core_pass(None)
    check("미측정만 있으면 SHS=100 (종전 75)", sh.shs == 100.0)
    check("미측정 플래그 False", sh.to_dict()["core_pass_measured"] is False)


def test_measured_penalty_unchanged():
    """측정된 분의 감점은 종전과 완전히 동일 (회귀 금지)."""
    for rate, expected in ((0.0, 75.0), (1 / 3.0, 100.0 - (2 / 3.0) * 25.0),
                           (2 / 3.0, 100.0 - (1 / 3.0) * 25.0), (1.0, 100.0)):
        sh = SystemHealthScore()
        sh.update_core_pass(rate)
        check("통과율 %.2f → SHS %.2f (종전 공식 유지)" % (rate, expected),
              abs(sh.shs - expected) < 1e-9)


def test_measured_value_survives_unmeasured_minute():
    """미측정 분이 와도 마지막 측정값은 표시용으로 남되 감점은 사라진다."""
    sh = SystemHealthScore()
    sh.update_core_pass(0.0)
    check("측정 분: SHS 75", abs(sh.shs - 75.0) < 1e-9)
    sh.update_core_pass(None)
    d = sh.to_dict()
    check("다음 분 미측정: 감점 해제 → SHS 100", sh.shs == 100.0)
    check("표시용 마지막 측정값 0.0 보존", d["core_pass_rate"] == 0.0)
    check("measured=False로 '이 값은 과거치'임을 표기", d["core_pass_measured"] is False)
    sh.update_core_pass(1 / 3.0)
    check("다시 측정되면 감점 재개", abs(sh.shs - (100.0 - (2 / 3.0) * 25.0)) < 1e-9)


def test_other_components_unaffected():
    """restart·z_warn·s2 감점은 CORE 미측정과 무관하게 그대로 동작."""
    sh = SystemHealthScore()
    sh.update_core_pass(None)
    sh.update_restart(2)          # -16
    sh.update_z_warn(4)           # -10
    sh.update_s2_latency(2.0)     # -5
    check("미측정이어도 타 항목 감점은 유지 (100-16-10-5=69)",
          abs(sh.shs - 69.0) < 1e-9)
    check("SHS<60 아니므로 경고 아님", sh.is_entry_blocked() is False)


def test_entry_blocked_threshold_unchanged():
    """표시 전용이 된 것과 별개로 임계 판정 자체는 종전과 동일."""
    sh = SystemHealthScore()
    sh.update_restart(5)          # -40
    sh.update_core_pass(0.0)      # -25 → 35
    check("SHS 35 → entry_blocked True (배지 경고)", sh.is_entry_blocked() is True)
    check("EKS kill switch와는 무관 (여전히 False)",
          sh.kill_switch_active is False)


def test_eks_firing_condition_unchanged():
    """EKS 발동 조건 불변 — 미측정 봉 계측 분리가 발동/미발동을 바꾸면 안 된다."""
    # (a) CORE 미측정 봉만 + 낮은 conf → 종전과 동일하게 발동
    sh = SystemHealthScore()
    for _ in range(5):
        sh.record_gap_open_bar(conf=0.30, core_all_passed=False, core_measured=False)
    fired = sh.evaluate_early_kill_switch(gap_open_mc=0.40)
    d = sh.to_dict()
    check("미측정 봉만: 종전대로 발동 (조건 불변)", fired is True)
    check("계측 분리: 5봉 중 측정 0봉으로 기록", d["gap_open_core_measured"] == 0
          and d["gap_open_bars"] == 5)

    # (b) CORE 통과 봉이 하나라도 있으면 미발동 (종전 동일)
    sh2 = SystemHealthScore()
    sh2.record_gap_open_bar(conf=0.30, core_all_passed=True, core_measured=True)
    for _ in range(4):
        sh2.record_gap_open_bar(conf=0.30, core_all_passed=False, core_measured=False)
    check("CORE 통과 1봉 있으면 미발동", sh2.evaluate_early_kill_switch(gap_open_mc=0.40) is False)
    check("측정 봉 수 1로 기록", sh2.to_dict()["gap_open_core_measured"] == 1)

    # (c) conf 충분하면 미발동 (종전 동일)
    sh3 = SystemHealthScore()
    for _ in range(5):
        sh3.record_gap_open_bar(conf=0.50, core_all_passed=False, core_measured=False)
    check("conf 충분하면 미발동", sh3.evaluate_early_kill_switch(gap_open_mc=0.40) is False)


def test_record_gap_open_bar_default_is_measured():
    """core_measured 기본값 True — 인자를 안 넘기는 기존 호출부 동작 보존."""
    sh = SystemHealthScore()
    sh.record_gap_open_bar(conf=0.30, core_all_passed=False)
    check("기본 호출은 측정으로 집계", sh.to_dict()["gap_open_core_measured"] == 1)


def test_reset_daily_clears_measured_count():
    sh = SystemHealthScore()
    sh.record_gap_open_bar(conf=0.3, core_all_passed=True, core_measured=True)
    sh.reset_daily()
    check("일일 리셋 시 측정 봉 수 초기화",
          sh.to_dict()["gap_open_core_measured"] == 0)


def test_alert_message_matches_reality():
    """알림 문구가 실제 동작과 일치 — '진입 차단' 단정 금지, 반올림 자기모순 제거."""
    import utils.notify as _notify

    captured = []
    orig = _notify.notify
    try:
        _notify.notify = lambda msg, level="INFO": captured.append((msg, level))
        _notify.notify_shs_alert(
            shs=59.6,
            components={"restart_count": 1, "z_warn_count": 2,
                        "core_pass_rate": 0.0, "core_pass_measured": False,
                        "s2_latency_sec": 0.5},
        )
    finally:
        _notify.notify = orig

    msg = captured[0][0] if captured else ""
    check("'진입 차단' 단정 문구 제거", "→ 진입 차단" not in msg)
    check("차단되지 않음을 명시", "차단되지 않음" in msg)
    check("반올림 자기모순 제거 — 59.6 그대로 표기", "59.6" in msg)
    check("CORE 미측정은 % 대신 '미측정' 표기", "미측정" in msg)


if __name__ == "__main__":
    test_unmeasured_does_not_penalize()
    test_measured_penalty_unchanged()
    test_measured_value_survives_unmeasured_minute()
    test_other_components_unaffected()
    test_entry_blocked_threshold_unchanged()
    test_eks_firing_condition_unchanged()
    test_record_gap_open_bar_default_is_measured()
    test_reset_daily_clears_measured_count()
    test_alert_message_matches_reality()

    print()
    if FAILURES:
        print("FAILED %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  -", f)
        sys.exit(1)
    print("전부 통과 — SHS CORE 미측정 분리 + EKS 발동조건 불변")
