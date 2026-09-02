# -*- coding: utf-8 -*-
"""[MW0602 519차 체리픽 / §2] 메인 스레드 정지 ALERT → 대시보드 「2 경보」 탭.

원 커밋 `d03b629`(v9-dev / MW0601)의 §2 검사만 가져왔다.
· §1(CB② 복원)  → **미도입**. dev 는 절대원칙 §2 · 489차 D2 에 따라
  `CB_CONSEC_STOP_LIMIT = 9999` 를 유지하고, 복원 시점을 전환기준 ⑧ 해제와
  같은 커밋으로 묶어 두었다. 그 규정을 지키는지는 아래 T0 가 고정한다.
· §3(마감 잔여 **자동청산**) → **미도입**(경보만). 사용자 결정.

실행: python tests/test_519_mainstall_alert_tab.py   (pytest 도 가능)
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


def _dash_src():
    return io.open(os.path.join(ROOT, "dashboard", "main_dashboard.py"),
                   encoding="utf-8").read()


def test_cb2_exception_still_held():
    """T0 — CB② 유예가 유지된다. 519차 §1 을 실수로 끌어오면 여기서 깨진다.

    dev 의 CLAUDE.md 절대원칙 §2(2026-08-23 주간회의 D2 / 489차)는 복원 시점을
    **전환기준 ⑧ 해제와 동일 커밋**으로 재지정했다. MW0601 이 근거로 삼은
    "재검토 기한 2026-08-29" 는 이 브랜치에서 이미 폐기된 기한이다.
    """
    from config.settings import CB_CONSEC_STOP_LIMIT, SIZING_TARGET_CAPITAL_ENABLED
    if CB_CONSEC_STOP_LIMIT != 9999:
        # 복원했다면 ⑧ 이 함께 해제돼 있어야 한다(같은 커밋 규정).
        assert not SIZING_TARGET_CAPITAL_ENABLED, (
            "CB② 를 복원했는데 ⑧(SIZING_TARGET_CAPITAL_ENABLED)이 아직 True 다 — "
            "489차 D2 는 둘을 같은 커밋으로 묶었다")
    return CB_CONSEC_STOP_LIMIT


def test_stall_alert_routed_to_alert_tab():
    src = _dash_src()
    assert "[MainStall] 🔴 미륵이 화면·판단이" in src
    idx = src.index("[MainStall] 🔴 미륵이 화면·판단이")
    head = src[idx - 1200:idx]
    assert "self.log_panel.append(" in head
    assert '"all", "ERROR"' in head, "ERROR 태그가 아니면 「2 경보」 탭 라우팅을 못 탄다"


def test_stall_alert_gated_on_alert_band_only():
    """WARN(5~15초)은 올리지 않는다 — 올리면 경보 탭이 잡음으로 덮인다."""
    src = _dash_src()
    idx = src.index("ALERT 밴드를 「2 경보」 탭으로")
    block = src[idx:idx + 4600]
    assert "if _gap_ms >= _MT_ALERT_MS:" in block
    assert "_MT_WARN_MS" not in block.split("self.log_panel.append")[0], \
        "WARN 밴드가 경보 탭 조건에 섞였다"


def test_stall_alert_threshold_unchanged():
    """임계 자체는 바꾸지 않았다 — 재보정은 26주 WFA 항목이다."""
    from config.settings import (
        MAIN_THREAD_STALL_ALERT_MS, MAIN_THREAD_STALL_WARN_MS,
        MAIN_THREAD_STALL_DETECT_MS,
    )
    assert MAIN_THREAD_STALL_ALERT_MS == 15_000
    assert MAIN_THREAD_STALL_WARN_MS == 5_000
    assert MAIN_THREAD_STALL_DETECT_MS == 2_000


def test_stall_alert_has_daily_cap_and_says_when_capped():
    """상한이 있고, 상한에 닿았다는 사실을 남긴다(계측 4원칙 ③ 탈락 가시화)."""
    from config.settings import MAIN_THREAD_STALL_ALERT_TAB_DAILY_MAX as CAP
    src = _dash_src()
    assert CAP > 0
    assert "_MT_ALERT_TAB_DAILY_MAX" in src
    assert "일일 상한" in src


def test_stall_alert_state_explicitly_initialised():
    """`getattr(self, "_x", 기본값)` 으로 런타임 상태를 읽지 않는다(계측 4원칙 ④)."""
    src = _dash_src()
    assert 'self._stall_alert_day = ""' in src
    assert "self._stall_alert_count = 0" in src
    assert 'getattr(self, "_stall_alert_day"' not in src
    assert 'getattr(self, "_stall_alert_count"' not in src


def test_no_dangling_traceback_file_promise():
    """🔴 [MW0602 조정] 없는 파일을 가리키는 안내를 넣지 않는다.

    원문 경보는 "원인 스택은 logs/mainstall_traceback_*.log 참조" 로 끝나는데
    그 덤프 기능은 이 브랜치에 없다. 없는 산출물을 안내하면 경보 자체를
    신뢰할 수 없게 된다(계측 4원칙 ④와 같은 취지).
    """
    src = _dash_src()
    # 주석에서 "왜 뺐는지" 설명하는 것은 정상이다 — **경보 문구 자체**만 본다.
    idx = src.index("[MainStall] 🔴 미륵이 화면·판단이")
    msg = src[idx:idx + 700]
    assert "mainstall_traceback" not in msg, (
        "경보 문구가 mainstall_traceback 을 안내하는데 그 덤프를 만드는 코드가 "
        "이 브랜치에 없다 — 없는 산출물을 가리키면 경보를 신뢰할 수 없게 된다")


def main():
    limit = test_cb2_exception_still_held()
    check("T0 CB② 유예 유지 (519차 §1 미도입) — 현재값 %s" % limit, True)
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and name != "test_cb2_exception_still_held":
            try:
                fn()
                check(name, True)
            except Exception as e:
                check(name, False, str(e))
    if FAILURES:
        print("\nFAILED: %s" % ", ".join(FAILURES))
        sys.exit(1)
    print("\nALL PASS (test_519_mainstall_alert_tab.py)")


if __name__ == "__main__":
    main()
