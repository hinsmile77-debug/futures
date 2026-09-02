# -*- coding: utf-8 -*-
"""[MW0602 523차 / Phase 0] FZ-2 센티넬의 **이 브랜치 전용 보정**을 고정한다.

원본(v9-dev `scripts/freeze_sentinel.py`)은 3신호 교차검증을 전제로 설계됐다.
이 브랜치는 FZ-1(L1)이 **보류**(522차 사용자 결정)라 그 산출물 2종이 없어
**SYSTEM.log 단독 판정**으로 축퇴한다 — 그래서 두 상수를 원본과 다르게 잡았다.

이 테스트는 그 보정이 **근거 없이 되돌려지는 것**을 막는다. 되돌리려면
FZ-1을 먼저 도입해 3신호를 살려야 한다(그때는 이 테스트가 그 사실을 알려준다).

실행: python tests/test_523_phase0_sentinel_calibration.py   (pytest 도 가능)
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FAILURES = []


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("OK" if cond else "FAIL", name,
                         ("\n         -> %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def _fz1_present():
    """FZ-1(L1)이 도입됐는가 — 3신호(하트비트·[TS])가 살아났는지의 판정."""
    return os.path.exists(os.path.join(ROOT, "utils", "freeze_watchdog.py"))


def _shutdown_marker_wired():
    """🔴 [524차 정정] 감시 창은 FZ-1 이 아니라 **종료 마커**에 달려 있다.

    523차는 창 검사를 `_fz1_present()` 로 완화하게 짰는데 **그것이 틀렸다.**
    정상 종료 뒤에는 3신호가 **전부** 낡으므로 신호 개수는 도움이 되지 않는다 —
    필요한 것은 「스스로 종료했다」를 말해 주는 마커이고, 그것이 마지막 신호보다
    **뒤**여야 한다. `_exit_normally` 는 런처가 지우고 `daily_close_done` 은 마감
    중에 찍혀 늦지 않다. 그래서 판정 근거는 `shutdown_normal` 마커 하나다.
    """
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    return "shutdown_normal_%s.txt" in src or "shutdown_normal_{" in src


def test_sentinel_is_alert_only():
    """🔴 하드 종료 금지 — Phase 0의 전제다(주간회의 승인 전)."""
    from config.settings import FREEZE_SENTINEL_KILL_ENABLED
    assert FREEZE_SENTINEL_KILL_ENABLED is False, \
        "FZ-2는 알림 전용이다. 하드 종료 승격은 주간회의 안건이다"


def test_stall_threshold_has_margin_over_measured_quiet_gap():
    """임계가 이 PC 실측 최대 무신호(271초)보다 충분히 크다.

    단일신호로 축퇴한 상태에서 300초(원본)를 쓰면 여유가 29초(10.7%)뿐이라
    가짜 동결이 난다. 가짜 경보가 쌓이면 진짜 동결도 무시하게 된다
    (MW0601 493차 「43회 가짜 경보」 전례).
    """
    from config.settings import FREEZE_SENTINEL_STALL_SEC as S
    MEASURED_MAX_QUIET_SEC = 271.0   # MW0602 실측(9거래일 · 09:00~15:45)
    if _fz1_present():
        # 3신호가 살아나면 교차검증이 여유를 대신하므로 완화해도 된다.
        assert S >= MEASURED_MAX_QUIET_SEC, "임계가 실측 무신호보다 작다"
        return
    assert S >= MEASURED_MAX_QUIET_SEC * 2.0, (
        "FZ-1 미도입(단일신호) 상태에서 임계 %.0f초는 실측 최대 무신호 %.0f초 대비 "
        "여유가 부족하다 — 매일 가짜 동결이 난다. 2배 이상으로 두거나 FZ-1을 먼저 "
        "도입할 것" % (S, MEASURED_MAX_QUIET_SEC))


def test_window_ends_before_daily_close_tail():
    """🔴 감시 창이 15:40 마감 꼬리를 넘지 않는다.

    이 브랜치는 정상 종료 판별 마커 3종을 쓸 수 없다:
      `_exit_normally` 미측정 · `shutdown_normal` 코드 부재(513차 미이관) ·
      `daily_close_done` 은 존재하나 mtime 이 마지막 SYSTEM.log 줄보다 이르다.
    그래서 창을 16:30 으로 두면 **매 거래일 15:50~16:30 에 가짜 CRITICAL + 팝업**이
    뜬다(2026-09-02 `--at-time` 재생으로 확인: 16:00·16:29 둘 다 CRITICAL).
    """
    from config.settings import FREEZE_SENTINEL_WINDOW as W
    end = str(W[1])
    hh, mm = [int(x) for x in end.split(":")]
    if _shutdown_marker_wired():
        # 마커가 있으면 마감 뒤 정지를 정상 종료로 가릴 수 있다 → 창을 넓혀도 된다.
        # 오히려 **좁으면** 15:40 마감 자체의 동결을 놓치므로 하한을 요구한다.
        assert (hh * 60 + mm) >= (16 * 60), (
            "종료 마커가 배선됐는데 창이 %s 에서 끝난다 — 15:40 마감 동결과 EOD "
            "인계 구간을 놓친다(MW0601 test_490 과 같은 요구)" % end)
        return
    assert (hh * 60 + mm) <= (15 * 60 + 45), (
        "감시 창 종료가 %s 다. 정상종료 마커 없이 15:45 를 넘기면 마감 뒤 정지를 "
        "동결로 오판한다 — 15:45 이하로 두거나 마커를 먼저 도입할 것" % end)
    # 절대원칙 §1 핵심 구간(15:10 강제청산 · 15:18 안전망)은 창 안에 있어야 한다.
    assert (hh * 60 + mm) >= (15 * 60 + 20), (
        "감시 창이 너무 이르다 — 15:10 강제청산·15:18 안전망 구간을 덮지 못한다")


def test_start_time_covers_open():
    from config.settings import FREEZE_SENTINEL_WINDOW as W
    hh, mm = [int(x) for x in str(W[0]).split(":")]
    assert (hh * 60 + mm) <= 9 * 60, "감시 창이 개장(09:00) 이후에 시작한다"


def test_sentinel_script_present_and_importable():
    p = os.path.join(ROOT, "scripts", "freeze_sentinel.py")
    assert os.path.exists(p), "scripts/freeze_sentinel.py 가 없다"
    src = io.open(p, encoding="utf-8").read()
    # 하드 종료가 코드로 들어오지 않았는지(문서상 미구현) 확인
    assert "os._exit(" not in src, \
        "센티넬에 하드 종료가 들어왔다 — 알림 전용 계약 위반"


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                check(name, True)
            except Exception as e:
                check(name, False, str(e))
    if FAILURES:
        print("\nFAILED: %s" % ", ".join(FAILURES))
        sys.exit(1)
    print("\nALL PASS (test_523_phase0_sentinel_calibration.py)")


if __name__ == "__main__":
    main()
