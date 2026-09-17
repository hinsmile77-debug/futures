"""[MW0601 599차 / F-4·F-5] EKS GAP_OPEN 계측 보강 회귀 가드.

이 테스트가 지키는 **단 하나의 불변식**:

    599차 F-4·F-5 는 로그와 집계만 바꾼다. **EKS 발동/미발동 판정은 한 비트도
    바뀌지 않는다.**

그래서 핵심은 `test_verdict_unchanged_on_8_real_days` 다 — 2026-09-08~09-17
**실측 8거래일**의 GAP_OPEN 입력(delayed/policy/conf/core 조합)을 그대로 넣어
판정이 라이브에서 관측된 것과 100% 일치하는지 본다. 이 8일은 우연히도
**발동 3일 · 미발동 5일**로 양쪽 분기를 다 덮는다.

배경(2026-09-17 장중 점검 이상점 1-4):
  · 09-15·16·17 EKS 3일 연속 발동, `conf_max=34.4%` 가 소수점까지 동일.
  · 그 값은 시장이 아니라 **보정기 출력상한**(0.3479, 9월 내내 불변)에 갇힌 값이고,
    발동선(mc−0.02≈0.40)보다 낮아 **09:00 봉이 셈에 들어가면 발동은 항등적으로 참**.
  · 유일한 갈림점은 `main.py` 의 `_gap_pipe_delayed` 1000ms 경계 —
    미발동 5일 ≥1,075ms / 발동 3일 ≤928ms 로 완전 분리.
  · `HORIZON_TIME_POLICY[(900,905)]=[]` 이라 09:01~09:04 네 봉은 매일 policy_blocked.
    ⇒ conf_max 의 원천은 **09:00 한 봉뿐**이다.

근거: `docs/정기점검/매일점검/MW0601-20260917-점검리포트.md` 「장중(intra)」 절.
"""

from utils.dll_bootstrap import ensure_conda_dll_path   # 448차
ensure_conda_dll_path()

import datetime
import inspect

import pytest

from safety import system_health as SH
from safety.system_health import SystemHealthScore


# ──────────────────────────────────────────────────────────────────────
# 실측 8거래일 — 2026-09-08 ~ 09-17
#
# 각 날의 GAP_OPEN 5봉을 (conf, core_all_passed, delayed, policy_blocked,
# core_measured) 로 표현한다. 라이브 로그에서 직접 읽은 값이다:
#   · delayed/policy 카운트 → `[SHS-EKS] EKS 미발동 — cold-start (…)` 로그
#   · conf 34.4% → 같은 분 `[Ensemble] … conf=34.4%`
#   · core 측정 0봉 → 발동 로그 `core_pass=0/5봉(측정 0봉)`
#   · mc → 발동 로그 `mc=XX.X%`
#
# 09-08 은 GAP_OPEN 봉이 0개라(`판정 유예 — GAP_OPEN 봉 부족(0봉)`) 별도 케이스다.
# ──────────────────────────────────────────────────────────────────────

_GAP_CONF = 0.344          # 보정기 상한에 갇힌 값 — 8일 내내 동일

# 09:01~09:04 네 봉: `HORIZON_TIME_POLICY[(900,905)]=[]` 로 매일 정책차단.
_BLOCKED = (0.0, False, False, True, False)

# 09:00 봉(= 08:59 분봉을 처리하는 실행)은 앙상블이 실제 결정을 내므로
# `active_horizons_blocked=False` 다 — 09-14 에도 `[Ensemble] conf=34.4%` 가 찍혔다.
# 이 봉이 제외되는 유일한 경로가 `_gap_pipe_delayed`(1000ms)이며, 그것이
# 발동/미발동을 가른 유일한 변수다. delayed 가 policy 보다 **우선**하므로
# (`if pipeline_delayed: … elif horizon_policy_blocked:`) 느린 날에는 delayed 로 계상된다.
def _open_bar(delayed: bool):
    return (_GAP_CONF, False, delayed, False, False)


def _day(first_bar_delayed: bool, extra_delayed: int = 0):
    """GAP_OPEN 5봉 생성.

    extra_delayed: 09:01~09:04 중 지연으로도 걸린 봉 수(09-11 은 delayed=2).
    delayed 가 우선순위를 가지므로 그 봉은 policy 가 아니라 delayed 로 계상된다.
    """
    bars = [_open_bar(first_bar_delayed)]
    for i in range(4):
        if i < extra_delayed:
            bars.append((0.0, False, True, True, False))
        else:
            bars.append(_BLOCKED)
    return bars


# (날짜, mc, 09:00 봉 delayed 여부, 추가 delayed 봉 수, 라이브 관측 발동 여부)
# delayed/policy 카운트는 cold-start 미발동 로그에서 그대로 읽었다.
REAL_DAYS = [
    ("2026-09-09", 0.399, True,  0, False),   # ~1,330ms · delayed=1 policy=4
    ("2026-09-10", 0.429, True,  0, False),   # ~1,703ms · delayed=1 policy=4
    ("2026-09-11", 0.429, True,  1, False),   # ~1,783ms · delayed=2 policy=3
    ("2026-09-14", 0.424, True,  0, False),   # ~1,144ms · delayed=1 policy=4
    ("2026-09-15", 0.419, False, 0, True),    # ~772ms  → 발동
    ("2026-09-16", 0.431, False, 0, True),    # ~831ms  → 발동
    ("2026-09-17", 0.421, False, 0, True),    # ~928ms  → 발동
]


def _run_day(mc, first_bar_delayed, extra_delayed=0, **eval_kwargs):
    shs = SystemHealthScore()
    for conf, core_ok, delayed, policy, core_meas in _day(first_bar_delayed, extra_delayed):
        shs.record_gap_open_bar(
            conf=conf,
            core_all_passed=core_ok,
            pipeline_delayed=delayed,
            horizon_policy_blocked=policy,
            core_measured=core_meas,
        )
    fired = shs.evaluate_early_kill_switch(gap_open_mc=mc, **eval_kwargs)
    return shs, fired


# ── 1. 핵심 불변식 — 판정이 바뀌지 않는다 ────────────────────────────

@pytest.mark.parametrize("date,mc,delayed,extra,expected_fired", REAL_DAYS)
def test_verdict_unchanged_on_8_real_days(date, mc, delayed, extra, expected_fired):
    """실측 7거래일(+09-08 별도)의 판정이 라이브 관측과 일치한다.

    ⚠ 이 테스트가 깨지면 599차가 **판정을 바꿔버린 것**이다. 로그만 바꾸기로 한
    약속이 깨진 것이므로, 로그 포맷을 고치는 대신 판정 경로를 되돌려라.
    """
    _shs, fired = _run_day(mc, delayed, extra)
    assert fired is expected_fired, (
        "%s: 발동 판정이 라이브 관측과 다르다 (기대 %s, 실제 %s). "
        "599차는 판정을 바꾸지 않기로 했다." % (date, expected_fired, fired)
    )


def test_verdict_unchanged_when_calib_context_passed():
    """F-4 의 새 인자를 **넘겨도** 판정이 같다 — 로그 전용임을 고정."""
    for date, mc, delayed, extra, expected in REAL_DAYS:
        _s1, without = _run_day(mc, delayed, extra)
        _s2, with_ctx = _run_day(
            mc, delayed, extra,
            conf_floor_state="unreachable",
            calib_output_max=0.3479,
            calib_auc=0.550,
        )
        assert without is with_ctx is expected, (
            "%s: 보정기 인자 전달이 판정을 바꿨다 — F-4 는 로그 전용이어야 한다" % date
        )


def test_gap_open_bars_short_is_still_deferred():
    """09-08 재현 — GAP_OPEN 봉 0개면 종전대로 미발동(판정 유예/확정)."""
    shs = SystemHealthScore()
    fired = shs.evaluate_early_kill_switch(gap_open_mc=0.42)
    assert fired is False


# ── 2. F-5 — conf 측정 분모가 실제를 반영한다 ────────────────────────

def test_conf_measured_counts_only_included_bars():
    """delayed/policy 로 제외된 봉은 conf 분모에 들어가지 않는다."""
    shs, _ = _run_day(0.421, first_bar_delayed=False)   # 09-17형: 1봉만 산입
    d = shs.to_dict()
    assert d["gap_open_bars"] == 5
    assert d["gap_open_conf_measured"] == 1, "09:00 한 봉만 conf_max 에 반영돼야 한다"
    assert d["gap_open_policy_blocked"] == 4
    assert d["gap_open_delayed"] == 0


def test_conf_measured_zero_distinguishes_unmeasured_from_zero():
    """599차 F-5 의 존재 이유 — **미측정 ≠ 0** (계측 4원칙 ②).

    두 경우 모두 `conf_max == 0.0` 이지만 분모가 다르다:
      ⓐ 한 봉도 산입 안 됨 (재지 않았다)        → conf측정 0
      ⓑ 산입됐는데 conf 가 정확히 0.0 (재보니 0) → conf측정 > 0

    ⚠ 현재 `_is_cold_start` 는 여전히 `conf_max == 0.0` 만 보므로 **판정은 같다.**
      그것이 의도다 — 먼저 세고, 표본이 쌓인 뒤에 판정식을 논한다.
      이 테스트는 "분모가 둘을 구분한다"만 고정한다.
    """
    # ⓐ 전 봉 제외
    a = SystemHealthScore()
    for conf, core_ok, delayed, policy, cm in _day(first_bar_delayed=True):
        a.record_gap_open_bar(conf=conf, core_all_passed=core_ok,
                              pipeline_delayed=delayed,
                              horizon_policy_blocked=policy, core_measured=cm)
    # ⓑ 산입됐으나 conf 가 0.0
    b = SystemHealthScore()
    for _ in range(5):
        b.record_gap_open_bar(conf=0.0, core_all_passed=False,
                              pipeline_delayed=False,
                              horizon_policy_blocked=False, core_measured=False)

    assert a.to_dict()["gap_open_conf_max"] == 0.0
    assert b.to_dict()["gap_open_conf_max"] == 0.0
    assert a.to_dict()["gap_open_conf_measured"] == 0, "ⓐ 는 미측정이어야 한다"
    assert b.to_dict()["gap_open_conf_measured"] == 5, "ⓑ 는 측정된 0.0 이어야 한다"


def test_reset_daily_clears_conf_measured():
    """일일 리셋에서 새 카운터가 빠지면 다음날로 이월된다(459차 reset 누락 계열)."""
    shs, _ = _run_day(0.421, first_bar_delayed=False)
    assert shs.to_dict()["gap_open_conf_measured"] == 1
    shs.reset_daily()
    assert shs.to_dict()["gap_open_conf_measured"] == 0


@pytest.mark.parametrize("date,mc,delayed,extra,expected_fired", REAL_DAYS)
def test_fixture_reproduces_logged_counts(date, mc, delayed, extra, expected_fired):
    """픽스처가 라이브 로그의 delayed/policy 카운트를 그대로 재현하는지 확인한다.

    이게 없으면 위 판정 테스트는 "내가 지어낸 입력으로 내 코드를 통과시킨 것"이
    된다. 미발동 3일은 cold-start 로그가 카운트를 직접 찍어 줬으므로 대조 가능하다:
        09-09/10/14 → delayed=1 policy_blocked=4
        09-11       → delayed=2 policy_blocked=3
    발동 3일은 종전 로그가 카운트를 안 찍었다(그 결손이 바로 F-4 가 고친 것) —
    대신 `conf_max=34.4%` 가 관측됐다는 사실에서 **conf 산입 봉이 1개 이상**임을
    역산해 고정한다.
    """
    shs, _ = _run_day(mc, delayed, extra)
    d = shs.to_dict()
    assert d["gap_open_bars"] == 5
    if expected_fired:
        assert d["gap_open_conf_measured"] >= 1, (
            "%s: conf_max=34.4%% 가 관측됐으므로 산입 봉이 있어야 한다" % date
        )
        assert abs(d["gap_open_conf_max"] - _GAP_CONF) < 1e-9
    else:
        expected_delayed = 1 + extra
        assert d["gap_open_delayed"] == expected_delayed, date
        assert d["gap_open_policy_blocked"] == 4 - extra, date
        assert d["gap_open_conf_measured"] == 0, (
            "%s: cold-start 로그가 conf_max=0%% 라고 찍었으므로 산입 봉이 없어야 한다" % date
        )
        assert d["gap_open_conf_max"] == 0.0


def test_to_dict_exposes_delayed():
    """F-4 — delayed 가 노출된 적이 없어 대시보드·알림이 제외 사유의 한쪽만 봤다."""
    shs, _ = _run_day(0.424, first_bar_delayed=True)
    assert shs.to_dict()["gap_open_delayed"] == 1


# ── 3. F-4 — 보정기 문맥 문자열 ──────────────────────────────────────

def test_calib_context_marks_structurally_unreachable():
    """상한 < 발동선이면 '구조적 도달불가'로 표기된다 (2026-09-17 실측값)."""
    txt = SystemHealthScore._format_calib_context("unreachable", 0.3479, 0.550, 0.421)
    assert "구조적 도달불가" in txt
    assert "34.8%" in txt
    assert "0.550" in txt


def test_calib_context_marks_reachable():
    txt = SystemHealthScore._format_calib_context("reachable", 0.3853, 0.617, 0.371)
    assert "도달가능" in txt
    assert "구조적 도달불가" not in txt


def test_calib_context_distinguishes_three_absence_kinds():
    """계측 4원칙 ② — '미전달'·'미측정'·실제값을 서로 다른 문자열로 쓴다."""
    assert SystemHealthScore._format_calib_context(None, None, None, 0.42) == "보정기=미전달"
    txt = SystemHealthScore._format_calib_context("unmeasured:calibrator_unfitted",
                                                 None, None, 0.42)
    assert "상한=미측정" in txt and "auc=미측정" in txt
    assert "0" not in txt.split("state=")[0].replace("상한=미측정", "").replace("auc=미측정", "")


def test_calib_context_never_raises_on_odd_input():
    """계측이 판정 경로를 깨뜨리지 않는다 — 어떤 입력에도 예외 없이 문자열을 낸다."""
    for args in [
        (None, 0.0, None, 0.0),
        ("x", 1.0, 1.0, 1.0),
        ("", 0.5, None, 0.42),
    ]:
        assert isinstance(SystemHealthScore._format_calib_context(*args), str)


# ── 4. G-2 — 자동 재개 마감 상태 (표시 전용) ────────────────────────

def _fired_shs():
    shs, fired = _run_day(0.421, first_bar_delayed=False)   # 2026-09-17형
    assert fired is True
    return shs


def test_recovery_closed_is_false_before_deadline():
    shs = _fired_shs()
    before = datetime.datetime(2026, 9, 17, 11, 29, 0)
    assert shs.is_eks_recovery_closed(before) is False


def test_recovery_closed_is_true_after_deadline():
    """2026-09-17 재현 — 11:29 시도 #5 실패 후 11:30 마감."""
    shs = _fired_shs()
    assert shs.is_eks_recovery_closed(datetime.datetime(2026, 9, 17, 11, 30, 0)) is True
    assert shs.is_eks_recovery_closed(datetime.datetime(2026, 9, 17, 14, 0, 0)) is True


def test_recovery_closed_is_false_when_eks_not_active():
    """EKS 가 안 켜진 날은 마감 이후라도 '오늘 종료'가 아니다 — 평시 오표시 방지."""
    shs, fired = _run_day(0.424, first_bar_delayed=True)    # 2026-09-14형(미발동)
    assert fired is False
    assert shs.is_eks_recovery_closed(datetime.datetime(2026, 9, 14, 14, 0, 0)) is False


def test_recovery_closed_agrees_with_can_attempt_recovery():
    """배지와 실제 회복 스케줄러가 **같은 상수**를 본다는 불변식.

    대시보드가 11:30 을 따로 하드코딩하면 둘이 어긋나는 순간이 생긴다
    (461차 `mdd_pct` 처럼 같은 이름이 두 분모를 갖는 계열). 단일 출처를 고정한다.
    """
    shs = _fired_shs()
    for hh, mm in [(11, 29), (11, 30), (11, 31), (13, 0)]:
        now = datetime.datetime(2026, 9, 17, hh, mm, 0)
        closed = shs.is_eks_recovery_closed(now)
        can = shs.can_attempt_recovery(now)
        assert closed != can or (not closed and not can), (
            "%02d:%02d — 배지(closed=%s)와 스케줄러(can=%s)가 어긋났다" % (hh, mm, closed, can)
        )
        if closed:
            assert can is False, "마감으로 표시하면서 재시도가 가능하면 안 된다"


def test_to_dict_exposes_recovery_closed():
    shs = _fired_shs()
    assert "eks_recovery_closed" in shs.to_dict()


def test_dashboard_badge_does_not_duplicate_deadline_constant():
    """대시보드가 11:30 판정을 **자기 안에서** 다시 만들지 않는지 확인한다.

    G-2 는 표시만 가르는 변경이므로, 시각 비교는 system_health 한 곳에만 있어야 한다.
    """
    import io, os
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "dashboard", "main_dashboard.py")
    src = io.open(p, encoding="utf-8", errors="replace").read()
    i = src.find("def update_shs_badge")
    assert i > 0
    # 주석은 제외한다 — 이 변경의 **근거**를 주석으로 남기는 것은 권장 사항이고,
    # 금지하려는 것은 "코드가 마감을 다시 계산하는 것"이다.
    body = "\n".join(
        ln.split("#", 1)[0] for ln in src[i:i + 4000].splitlines()
    )
    for bad in ("EKS_RECOVERY_DEADLINE", "time(11, 30)", "datetime.now()"):
        assert bad not in body, (
            "update_shs_badge 가 마감 판정을 자체 계산한다(%s) — "
            "`recovery_closed` 인자를 그대로 쓰라" % bad
        )
    assert "recovery_closed" in body, "배지가 전달받은 마감 상태를 쓰지 않는다"


# ── 4-B. 로그가 실제로 렌더링되는가 ─────────────────────────────────

# 판정 4분기 × (mc, 첫봉 delayed, extra) — 각 분기를 한 번씩 태운다.
_LOG_CASES = [
    ("발동",            0.421, False, 0, 5),
    ("cold-start 미발동", 0.424, True,  0, 5),
    ("마진 내 근소 미달",  0.350, False, 0, 5),
    ("일반 미발동",       0.200, False, 0, 5),
]


def _capture_eks_logs(mc, delayed, extra):
    """`SH.logger` 에 직접 핸들러를 달아 렌더링된 메시지를 모은다.

    ⚠ `caplog` 는 못 쓴다 — 이 프로젝트 로거는 루트로 **전파되지 않아**
    pytest 의 기본 캡처가 빈 목록을 돌려준다(2026-09-17 실측). 그 상태로
    `assert not records` 류를 쓰면 **항상 통과하는 가짜 테스트**가 된다.
    """
    import logging
    msgs = []

    class _Grab(logging.Handler):
        def emit(self, record):
            msgs.append(record.getMessage())   # 인자 불일치면 여기서 TypeError

    h = _Grab()
    h.setLevel(logging.DEBUG)
    _prev = SH.logger.level
    SH.logger.setLevel(logging.DEBUG)
    SH.logger.addHandler(h)
    try:
        _run_day(mc, delayed, extra,
                 conf_floor_state="unreachable",
                 calib_output_max=0.3479, calib_auc=0.550)
    finally:
        SH.logger.removeHandler(h)
        SH.logger.setLevel(_prev)
    return msgs


def test_capture_helper_actually_captures():
    """위 헬퍼가 정말 잡는지 먼저 확인한다 — 안 잡히면 아래 테스트가 전부 위증이 된다."""
    assert _capture_eks_logs(0.421, False, 0), "핸들러가 아무것도 못 잡았다"


@pytest.mark.parametrize("label,mc,delayed,extra,bars", _LOG_CASES)
def test_every_branch_log_renders(label, mc, delayed, extra, bars):
    """`%` 인자 개수가 어긋나도 logging 은 **예외를 삼키고** 조용히 넘어간다.

    그러면 계측을 늘리려던 변경이 오히려 그 줄을 통째로 없애 버린다
    (523차가 `[ConfFloorGuard]` auc 에서 같은 위험을 지적했다 — "관측을 하나 더
    붙이려다 가드의 눈을 감기는 형태"). 그래서 **렌더링 결과를 직접 확인**한다.
    """
    eks_lines = [m for m in _capture_eks_logs(mc, delayed, extra) if "SHS-EKS" in m]
    assert eks_lines, "%s: EKS 판정 로그가 아예 안 나왔다" % label
    for msg in eks_lines:
        assert "%d" not in msg and "%s" not in msg and "%.1f" not in msg, (
            "%s: 포맷 지정자가 치환되지 않은 채 남았다 → %r" % (label, msg)
        )
        assert "conf측정=" in msg and "delayed=" in msg, (
            "%s: F-4 가 추가한 제외 사유 분해가 빠졌다 → %r" % (label, msg)
        )
        assert "보정기" in msg, "%s: F-4 보정기 문맥이 빠졌다 → %r" % (label, msg)


def test_fired_branch_log_names_the_structural_cause():
    """발동 로그만 보고 '이건 시장이 아니라 보정기'라는 것이 읽혀야 한다.

    이 한 줄이 2026-09-17 조사(8일치 `[PipePerf]` 교차대조)를 대체한다.
    """
    import logging
    caplog_msgs = []

    class _Grab(logging.Handler):
        def emit(self, record):
            caplog_msgs.append(record.getMessage())

    h = _Grab()
    SH.logger.addHandler(h)
    try:
        _run_day(0.421, False, 0,
                 conf_floor_state="unreachable", calib_output_max=0.3479, calib_auc=0.550)
    finally:
        SH.logger.removeHandler(h)

    fired = [m for m in caplog_msgs if "Early Kill Switch 발동" in m]
    assert fired, "발동 로그가 없다"
    m = fired[0]
    assert "구조적 도달불가" in m
    assert "conf측정=1" in m, "conf_max 의 분모가 로그에 있어야 한다"
    assert "delayed=0" in m and "policy=4" in m, "제외 사유 두 갈래가 다 보여야 한다"


# ── 5. 판정식이 여전히 손대지 않은 상태인지 ──────────────────────────

def test_cold_start_formula_untouched():
    """`_is_cold_start` 가 아직 `conf_max == 0.0` 을 본다는 사실을 고정한다.

    ⚠ 이것을 `conf_measured` 로 바꾸는 것은 **별도 결정**이다(표본 필요).
    바꿀 때 이 테스트가 깨지면서 "의도한 변경인가"를 되묻게 만드는 것이 목적이다.
    459차가 발동 조건을 그대로 둔 것과 같은 보수적 순서.
    """
    src = inspect.getsource(SystemHealthScore.evaluate_early_kill_switch)
    assert "self._gap_open_conf_max == 0.0" in src, (
        "cold-start 판정식이 바뀌었다. 599차 범위 밖의 변경이므로, "
        "표본 근거와 함께 NEXT_TODO 459차 항목을 갱신하고 이 테스트를 수정하라."
    )


def test_recovery_deadline_and_constants_untouched():
    """599차가 매매 정책 상수를 건드리지 않았음을 고정 (G-4 는 주간회의 안건)."""
    assert SH.EKS_RECOVERY_DEADLINE == datetime.time(11, 30)
    assert SH.EKS_RECOVERY_INTERVAL_MIN == 30
    assert SH.EKS_RECOVERY_CONF_MIN_HITS == 3
    assert SH.EKS_TRIGGER_MARGIN == 0.02
    assert SH.EKS_MIN_BARS == 3
