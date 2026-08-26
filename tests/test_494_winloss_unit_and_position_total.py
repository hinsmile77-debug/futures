# -*- coding: utf-8 -*-
"""[MW0601 494차 후속 / F-AE·F-AF] 청산 마감 줄의 단위와 승패 판정 축.

왜 필요한가 (2026-08-26 실측, 사용자 제보)
------------------------------------------
`[청산 완료]` 로그가 포지션이 **이겼는데 졌다고** 말했다:

    로그   [청산 완료] PnL=-0.03pt (-11,928원)     ← 손실로 읽힌다
    브로커 총손익 +21 (천원)                        ← 이익이다

**부호가 반대다.** 손익 계산은 맞았고(브로커와 6원 차) **표기와 분류**가 틀렸다.

원인: `[청산 완료]` 가 찍는 값은 `_ts_build_agg_exit_result()` 의 결과이고 그
집계 범위는 **주문 하나**다. 한 주문의 분할체결은 합쳐지지만 **다른 주문은
합쳐지지 않는다.** 그래서 같은 로그 줄이 날마다 다른 것을 뜻했다:

    2026-08-25 ①  하드스톱 1주문 2계약   -24,108  = 포지션 총합  ✅ (우연히 맞음)
    2026-08-25 ②  TP1 → 스톱 2주문       +11,936  ≠ 총합 +56,872 ❌
    2026-08-26     TP1 → 스톱 2주문       -11,928  ≠ 총합 +21,144 ❌ (부호 반대)

계측 4원칙 ①(단위 명시)의 전형 — 같은 이름이 두 분모를 가진다.

🔴 **더 심각한 것**: 승패 **분류**도 레그 단위다. 오늘 포지션은 이겼는데
Kelly 에 1승 1패로 들어가고, 최종 레그가 음수라 `record_stop_loss()` 까지 불려
**이익 포지션이 손절로 카운트**됐다. 앙상블 게이터도 오답으로 학습했다.
`daily_stats` 는 459차 F1 이 이미 포지션 단위로 고쳐 **통계는 맞았고**, 그래서
학습 계층만 레그 단위로 남은 것을 아무도 의심하지 않았다.

이 파일이 고정하는 불변식
① 포지션 누계가 레그 합과 일치한다 (F-AE 누적기).
② 누계는 **리셋 전에** result 로 나온다 — 457차 C5 「리셋 뒤에 읽기」 함정 방지.
③ `[청산 완료]` 는 **앞부분 포맷을 바꾸지 않고 뒤에만** 병기한다 (수집기 정규식 보호).
④ 재기동 복원으로 앞 레그를 못 본 경우 「총합」이라 말하지 않는다 (4원칙 ②).
⑤ F-AF 섀도가 네 지점 전부에 배선돼 있고 **기록 동작을 바꾸지 않는다**.
⑥ 오늘 케이스에서 `불일치=Y` 가 실제로 잡힌다.
"""
import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from config.constants import POSITION_SHORT  # noqa: E402
from strategy.position.position_tracker import PositionTracker  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2026-08-26 09:39 실측 (logs/20260826_TRADE.log + 브로커 [6197] 패널)
ENTRY = 1062.93          # 체결진입보정 평균
TP1_FILL = 1062.06
STOP_FILL = 1062.96      # 브로커 매수약정 106,251천원에서 역산
ATR = 3.54 / 1.5
EXPECT_TP1 = 33_072
EXPECT_STOP = -11_928
EXPECT_POSITION = 21_144   # 브로커 예탁 차이 +21,150 과 6원 차


def _today_position():
    pt = PositionTracker(pt_value=50_000)
    pt.open_position(direction=POSITION_SHORT, price=ENTRY, quantity=2,
                     atr=ATR, grade="A", regime="NEUTRAL")
    leg1 = pt.partial_close(exit_price=TP1_FILL, qty=1, reason="TP1 부분청산 33%")
    leg2 = pt.close_position(exit_price=STOP_FILL, reason="하드스톱(틱)")
    return pt, leg1, leg2


# ── ① 누계가 레그 합과 일치 ─────────────────────────────────────────────────
def test_position_total_equals_leg_sum():
    _, leg1, leg2 = _today_position()
    assert leg1["pnl_krw"] == pytest.approx(EXPECT_TP1, abs=2)
    assert leg2["pnl_krw"] == pytest.approx(EXPECT_STOP, abs=2)
    total = leg2["pos_realized_pnl_krw"]
    assert total == pytest.approx(leg1["pnl_krw"] + leg2["pnl_krw"], abs=2)
    assert total == pytest.approx(EXPECT_POSITION, abs=2)
    assert leg2["pos_realized_leg_count"] == 2


def test_the_sign_actually_flips():
    """🔴 재현의 핵심 — 마지막 레그는 **음수**인데 포지션은 **양수**다.

    이 관계가 성립하지 않으면 이 테스트는 아무것도 검증하지 않는다.
    """
    _, _, leg2 = _today_position()
    assert leg2["pnl_krw"] < 0, "마지막 레그가 손실이어야 재현이다"
    assert leg2["pos_realized_pnl_krw"] > 0, "포지션은 이익이어야 재현이다"


def test_single_order_close_still_matches():
    """한 주문으로 닫힌 포지션은 종전에도 맞았다 — 그대로 맞아야 한다(회귀)."""
    pt = PositionTracker(pt_value=50_000)
    pt.open_position(direction=POSITION_SHORT, price=ENTRY, quantity=1,
                     atr=ATR, grade="A", regime="NEUTRAL")
    leg = pt.close_position(exit_price=ENTRY - 1.0, reason="하드스톱")
    assert leg["pos_realized_pnl_krw"] == pytest.approx(leg["pnl_krw"], abs=2)
    assert leg["pos_realized_leg_count"] == 1


# ── ② 리셋 전에 실려 나오는가 ───────────────────────────────────────────────
def test_total_survives_position_reset():
    """🔴 `close_position()` 은 반환 직전에 `_reset_position()` 을 부른다.

    트래커 속성을 직접 읽으면 **항상 0** 이다 — 457차 C5(`verified_count` 가
    8거래일 연속 0)·483차 P1-A 와 같은 함정이며 **개발 중 실제로 밟았다**.
    값은 리셋 전에 result 로 나와야 한다.
    """
    pt, _, leg2 = _today_position()
    assert pt._pos_realized_pnl_krw == 0.0, "리셋이 안 됐다면 다음 포지션이 오염된다"
    assert leg2["pos_realized_pnl_krw"] == pytest.approx(EXPECT_POSITION, abs=2), (
        "리셋 뒤 값을 실었다 — result 조립이 리셋보다 뒤로 밀렸는가")


def test_accumulator_resets_between_positions():
    pt, _, _ = _today_position()
    pt.open_position(direction=POSITION_SHORT, price=1000.0, quantity=1,
                     atr=ATR, grade="A", regime="NEUTRAL")
    leg = pt.close_position(exit_price=999.0, reason="하드스톱")
    assert leg["pos_realized_leg_count"] == 1, "이전 포지션 레그가 이월됐다"
    assert leg["pos_realized_pnl_krw"] == pytest.approx(leg["pnl_krw"], abs=2)


# ── ③ 앞부분 포맷 불변 ──────────────────────────────────────────────────────
def _main_src():
    return io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()


def test_closing_log_prefix_is_unchanged():
    """🔴 수집기 `pos_done` 정규식이 앞부분에 걸려 있다 — 뒤에만 붙인다.

    457차 G5 관례: 종전 줄의 포맷을 바꾸면 로그 파서·점검 스크립트가 조용히 깨진다.
    """
    src = _main_src()
    assert 'f"[청산 완료] PnL={pnl:+.2f}pt ({result[\'pnl_krw\']:+,.0f}원)"' in src, (
        "[청산 완료] 앞부분 포맷이 바뀌었다 — collect_evidence 의 pos_done 이 깨진다")

    collector = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                             "scripts", "collect_evidence.py")
    if os.path.exists(collector):
        pat_src = io.open(collector, encoding="utf-8").read()
        m = re.search(r'"pos_done":\s*r"([^"]+)"', pat_src)
        assert m, "수집기에서 pos_done 패턴을 못 찾았다"
        rendered = "[청산 완료] PnL=-0.03pt (-11,928원) | 포지션 합계 +21,144원 (레그 2)"
        assert re.search(m.group(1), rendered), (
            "병기 후 문자열이 수집기 정규식에 안 걸린다 — 앞부분을 건드렸는가")


def test_closing_log_appends_position_total():
    src = _main_src()
    assert "포지션 합계" in src
    assert "_fae_txt" in src
    # ⚠ `%` 서식 콤마 금지(F-Y) — format() 을 써야 한다.
    assert 'format(_fae_krw, "+,.0f")' in src, "콤마 서식을 % 연산자에 쓰면 죽는다"


# ── ④ 미측정 표기 ───────────────────────────────────────────────────────────
def test_restart_restore_is_marked_unmeasured():
    """상태 파일에 원 단위 누계가 없으면 「총합」이라 말하지 않는다(4원칙 ②)."""
    pt = PositionTracker(pt_value=50_000)
    pt.restore_state({
        "status": POSITION_SHORT, "entry_price": ENTRY, "quantity": 1,
        "stop_price": ENTRY + 3.0, "tp1_price": ENTRY - 1.0, "tp2_price": ENTRY - 2.0,
        "pos_realized_pnl_pts": -0.5,
    }) if hasattr(pt, "restore_state") else None
    # restore 경로 이름이 다르면 속성만 직접 확인한다(구조 회귀 방지 목적).
    src = io.open(os.path.join(ROOT, "strategy", "position",
                               "position_tracker.py"), encoding="utf-8").read()
    assert "_pos_realized_krw_measured = _prk is not None" in src, (
        "복원 시 미측정 플래그를 세우지 않는다 — 0 이 총합으로 위장된다")
    assert '"pos_realized_pnl_krw": self._pos_realized_pnl_krw' in src, (
        "누계가 영속화되지 않는다 — 장중 재기동 후 총합이 부분합이 된다")


def test_main_does_not_read_tracker_attribute_directly():
    """`_post_exit` 이 트래커 속성을 직접 읽으면 리셋 뒤 값(0)을 찍는다."""
    src = _main_src()
    i = src.index("[청산 완료]")
    window = src[max(0, i - 2500): i + 200]
    assert "self.position._pos_realized_pnl_krw" not in window, (
        "리셋 뒤에 읽고 있다 — result 에서 읽을 것(457차 C5 함정)")


# ── ⑤⑥ F-AF 섀도 ───────────────────────────────────────────────────────────
_SITES = ("post_partial_exit", "post_loss_tier1_exit",
          "post_exit", "record_nonfinal_exit")


def test_shadow_is_wired_at_all_four_sites():
    """승패 기록 지점 4곳 전부에 섀도가 붙어 있는가.

    489차 주석이 그 4곳을 명시했다. 하나라도 빠지면 그 경로의 불일치가 안 보인다.
    """
    src = _main_src()
    for site in _SITES:
        assert 'log_winloss_unit_shadow(self.position, result, "%s")' % site in src, (
            "%s 에 F-AF 섀도가 없다" % site)
    assert src.count("log_winloss_unit_shadow(self.position") == 4


def test_shadow_does_not_change_recording():
    """🚫 섀도는 **기록 동작을 바꾸지 않는다** — 승격은 F-AG(주간회의)다.

    ⚠ 텍스트 검색으로 하면 **독스트링의 설명 문구까지 잡는다**(개발 중 실제로
    밟았다 — "왜 record_stop_loss 가 불렸는가"를 적은 문장이 위반으로 판정됐다).
    AST 로 **실제 호출**만 본다.
    """
    import ast

    tree = ast.parse(_main_src())
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "log_winloss_unit_shadow")
    called = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            f = node.func
            called.add(getattr(f, "attr", None) or getattr(f, "id", None))
    for forbidden in ("record_win", "record_stop_loss", "record",
                      "record_trade_outcome"):
        assert forbidden not in called, (
            "섀도 헬퍼가 %s 를 호출한다 — 계측이 판정을 건드리면 안 된다" % forbidden)


def test_shadow_detects_todays_mismatch(monkeypatch):
    """🔴 오늘 케이스에서 `불일치=Y` 가 실제로 찍히는가."""
    import main as M

    lines = []
    monkeypatch.setattr(M.log_manager, "system",
                        lambda msg, lvl=None: lines.append(msg))
    _, _, leg2 = _today_position()
    M.log_winloss_unit_shadow(None, leg2, "post_exit")

    assert lines, "섀도 로그가 안 나왔다"
    msg = lines[-1]
    assert "[WinLossUnit]" in msg
    assert "레그판정=L" in msg and "포지션판정=W" in msg
    assert "불일치=Y" in msg, "이 결함의 지문이 안 잡힌다: %s" % msg
    assert "site=post_exit" in msg


def test_shadow_marks_unmeasured_when_total_absent(monkeypatch):
    """포지션 누계가 없는 result 에서 「불일치 없음」으로 위장하지 않는가."""
    import main as M

    lines = []
    monkeypatch.setattr(M.log_manager, "system",
                        lambda msg, lvl=None: lines.append(msg))
    M.log_winloss_unit_shadow(None, {"pnl_pts": -0.03, "pnl_krw": -11928.0},
                              "record_nonfinal_exit")
    msg = lines[-1]
    assert "pos=미측정" in msg
    assert "불일치=?" in msg, "미측정을 N(일치)으로 읽으면 결함이 숨는다"


def test_shadow_survives_bad_input(monkeypatch):
    """계측 실패가 청산 후처리를 끊으면 안 된다."""
    import main as M
    monkeypatch.setattr(M.log_manager, "system",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    M.log_winloss_unit_shadow(None, {"pnl_pts": 1.0, "pnl_krw": 1.0}, "post_exit")
