"""[MW0601 472차] Phase 5 전환 게이트 배지 판정기 — 3상태 분리·자동판정·깜빡임 정책.

무엇을 지키려는가
-----------------
좌상단 배지가 **다시 화석이 되지 않게** 하는 것이 이 파일의 목적이다.

교체 전 배지는 `"Phase 3 예정"`이라는 하드코딩 문자열이었고, 툴팁이 예고한 3개 항목 중
①Platt Scaling은 458차에, ②anti_signal 역신호 채널은 457차에 각각 **기각**됐는데도
800ms마다 계속 깜빡였다. 문자열이라 아무도 갱신하지 않았고, 갱신되지 않았다는 사실이
어디에도 드러나지 않았다.

그래서 세 가지를 불변식으로 못박는다.

1. **미측정 ≠ 미충족** (계측 4원칙 ②) — ①③④처럼 trades.db·WFA 실측이 필요한 게이트를
   "미충족"으로 세면 재보지도 않은 것을 재봤다고 말하는 셈이다. 배지 분자(N/9)는
   **확인된 충족만** 센다.
2. **자동 판정은 설정값을 진짜로 읽는다** — 상수를 바꾸면 배지가 따라 바뀌어야 한다.
   이 테스트가 깨지면 배지가 다시 설정과 무관해진 것이다.
3. **깜빡임은 기한 있는 게이트에만** — 상시 깜빡임은 경보 피로로 신호 가치를 0으로 만든다.

실행:
    pytest tests/test_472_phase5_gate_badge.py
    python tests/test_472_phase5_gate_badge.py
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"

from strategy.ops import phase5_gate_status as P5  # noqa: E402


class _FakeSettings(object):
    """게이트 판정에 쓰이는 상수만 담은 가짜 설정 모듈."""

    def __init__(self, **kw):
        self.CB_CONSEC_STOP_LIMIT = 9999
        self.CB3_P4_GRADE_BLOCK_ENABLED = False
        self.FP_CRITICAL_GRADE_BLOCK_ENABLED = False
        self.TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED = False
        self.SIZING_TARGET_CAPITAL_ENABLED = True
        self.SIZING_TARGET_CAPITAL_KRW = 50_000_000
        self.MAX_CONTRACTS = 3
        self.PHASE5_GATE_DECISIONS = {}
        for k, v in kw.items():
            setattr(self, k, v)


_TODAY = dt.date(2026, 8, 17)


def _by_num(gates):
    return {g.num: g for g in gates}


# ── 1. 3상태 분리 (계측 4원칙 ②) ──────────────────────────────────────────

def test_unmeasured_is_not_counted_as_open():
    """③④는 '미충족'이 아니라 '미측정'이다 — 자동으로 판정할 수단이 없다.

    ↩️ **[MW0602 488차 후속2] ①을 이 목록에서 뺐다 — 모듈 설계와 어긋나 있었다.**
    `_chk_paper_pnl()` 은 처음부터 **반증 전용**으로 설계됐다(자기 docstring:
    *"합이 0 이하면 미충족이 확실하다 … 양수라고 해서 ①이 끝난 것은 아니다"*).
    즉 20거래일이 모이고 통산이 **0 이하이면 `OPEN` 이 정답**이다.

    테스트는 그 분기를 몰랐고, 표본이 20거래일에 못 미치는 동안에만 우연히 통과했다.
    2026-08-23 실측이 그 조건을 넘겼다 — **최근 20거래일 통산 −178,004원(양수일 8/20)**
    → ① `open`. 테스트를 고치지 않고 코드를 되돌렸다면 **실전 전환 기준 ①이
    미충족이라는 사실을 도구가 말하지 못하게** 만드는 것이었다.

    ⚠ 대신 **더 강한 것**을 단언한다: ①은 어떤 경우에도 `MET` 이 될 수 없다.
      "양수 = 충족"으로 자동 확정하는 순간 롤링 창의 하루짜리 흑자가 전환 기준을
      통과시킨다 — 그 방향의 자동 확정만이 위험하다.
    """
    g = _by_num(P5.evaluate(settings=_FakeSettings(), today=_TODAY))
    for num in (3, 4):
        assert g[num].status == P5.UNMEASURED, (
            "게이트 %d가 %s로 판정됐다 — 실측 수단이 없는 게이트를 미충족으로 세면 "
            "재보지도 않은 것을 재봤다고 말하는 셈이다" % (num, g[num].status))

    # `source` 는 게이트마다 다르고 **그래야 한다** — 종전에는 ③④ 둘 다
    # `SRC_PENDING` 을 요구했으나 그것은 두 가지 다른 상태를 뭉갠 것이다:
    #   ③ = 아예 안 본다(WFA 26주 실측 필요)               → `pending`
    #   ④ = **보긴 본다**(trades.db 로 평균·표준편차를 낸다). 다만 **합격선이 정의된
    #        적이 없어** 판정을 못 한다                      → `auto` + `UNMEASURED`
    # 후자를 `pending` 이라 부르면 "재료조차 없다"로 읽혀, ④의 합격선을 만들 때
    # 쓸 수 있는 실측이 이미 있다는 사실이 가려진다.
    assert g[3].source == P5.SRC_PENDING, g[3].source
    assert g[4].source == P5.SRC_AUTO, (
        "④가 %s — trades.db 재료 산출이 끊겼는지 확인할 것" % g[4].source)

    # ①은 반증 전용 — 미측정이거나 미충족이며, **자동으로 충족이 되지는 않는다.**
    assert g[1].status in (P5.UNMEASURED, P5.OPEN), g[1].status
    assert g[1].status != P5.MET, (
        "①이 자동으로 '충족'이 됐다 — 롤링 창의 일시적 흑자가 실전 전환 기준을 "
        "통과시킨다. 충족 확정은 `PHASE5_GATE_DECISIONS` 수동 기록의 몫이다")


def test_numerator_counts_only_confirmed_met():
    """배지 분자는 확인된 충족만 센다. 미측정이 분자로 새면 안 된다."""
    st = _FakeSettings()
    gates = P5.evaluate(settings=st, today=_TODAY)
    c = P5.summarize(gates)
    text, _level, _tip, _urgent = P5.badge(settings=st, today=_TODAY)

    assert c[P5.MET] + c[P5.OPEN] + c[P5.UNMEASURED] == P5.TOTAL_GATES
    assert ("%d/%d" % (c[P5.MET], P5.TOTAL_GATES)) in text
    assert c[P5.UNMEASURED] > 0, "미측정 게이트가 0이면 이 테스트의 전제가 사라진 것이다"


def test_tooltip_states_the_unmeasured_distinction():
    """툴팁이 '미측정 ≠ 미충족'을 말하지 않으면 운영자가 0/9를 오독한다."""
    tip = P5.build_tooltip(P5.evaluate(settings=_FakeSettings(), today=_TODAY))
    assert "미측정" in tip and "미충족" in tip
    assert "충족 " in tip.splitlines()[0], "첫 줄에 상태별 개수 요약이 있어야 한다"


# ── 2. 자동 판정이 설정값을 진짜로 읽는가 ─────────────────────────────────

def test_cb2_open_while_suspended():
    """⑤ CB② — 9999는 '재봤더니 미충족'이다(미측정이 아니다)."""
    g = _by_num(P5.evaluate(settings=_FakeSettings(), today=_TODAY))[5]
    assert g.status == P5.OPEN
    assert g.source == P5.SRC_AUTO
    assert "9999" in g.detail


def test_cb2_restored_value_alone_is_not_enough():
    """값만 2~3으로 되돌려도 충족이 아니다 — v9 계획 §0-1이 '발동 1회 확인'을 함께 요구한다.

    설정값은 위반을 반증할 수는 있어도 충족을 입증하지는 못한다. 그래서 UNMEASURED다.
    """
    st = _FakeSettings(CB_CONSEC_STOP_LIMIT=3)
    g = _by_num(P5.evaluate(settings=st, today=_TODAY))[5]
    assert g.status == P5.UNMEASURED, "값 복원만으로 충족 처리하면 게이트가 헐거워진다"
    assert "발동" in g.detail


def test_flag_gates_follow_settings():
    """⑥⑦⑨ — 플래그를 True로 바꾸면 배지가 따라와야 한다."""
    off = _by_num(P5.evaluate(settings=_FakeSettings(), today=_TODAY))
    on = _by_num(P5.evaluate(settings=_FakeSettings(
        CB3_P4_GRADE_BLOCK_ENABLED=True,
        FP_CRITICAL_GRADE_BLOCK_ENABLED=True,
        TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED=True,
    ), today=_TODAY))
    for num in (6, 7, 9):
        assert off[num].status == P5.OPEN
        assert on[num].status == P5.MET, "게이트 %d가 설정 변경을 따라오지 않았다" % num


def test_sizing_gate_detects_simulation_default():
    """⑧ — 목표자본이 모의 기본값(5천만원) 그대로면 조건1 미충족이다."""
    g = _by_num(P5.evaluate(settings=_FakeSettings(), today=_TODAY))[8]
    assert g.status == P5.OPEN
    assert "50,000,000" in g.detail


def test_sizing_gate_does_not_auto_pass_on_change():
    """값이 바뀌었다고 자동 충족 처리하면 안 된다 — MAX_CONTRACTS 재산출 여부를 코드가 모른다.

    ⚠ ENABLED를 끄기만 하는 것도 충족이 아니다. CLAUDE.md ⑧이 경고하듯 그것만 하면
    MAX_CONTRACTS 아래에서 2026-07-10 이전 손실 구간이 되살아난다.
    """
    for st in (_FakeSettings(SIZING_TARGET_CAPITAL_KRW=300_000_000),
               _FakeSettings(SIZING_TARGET_CAPITAL_ENABLED=False)):
        g = _by_num(P5.evaluate(settings=st, today=_TODAY))[8]
        assert g.status == P5.UNMEASURED, "설정 변경만으로 ⑧을 통과시키면 안 된다"
        assert "MAX_CONTRACTS" in g.detail


def test_missing_constant_is_unmeasured_not_met():
    """상수가 사라지면 '미측정'이다 — 폴백으로 통과시키면 게이트가 조용히 열린다."""
    st = _FakeSettings()
    del st.CB_CONSEC_STOP_LIMIT
    del st.TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED
    g = _by_num(P5.evaluate(settings=st, today=_TODAY))
    assert g[5].status == P5.UNMEASURED
    assert g[9].status == P5.UNMEASURED


# ── 3. 수동 기록(레지스트리) ──────────────────────────────────────────────

def test_manual_record_overrides_and_shows_provenance():
    """수동 기록은 자동 판정을 덮되, 출처가 반드시 드러나야 한다(계측 4원칙 ④)."""
    st = _FakeSettings(PHASE5_GATE_DECISIONS={
        2: {"status": P5.MET, "date": "2026-08-20", "note": "F-1R 리허설 완료"},
    })
    g = _by_num(P5.evaluate(settings=st, today=_TODAY))[2]
    assert g.status == P5.MET
    assert g.source == P5.SRC_MANUAL
    assert "2026-08-20" in g.detail
    assert "[수동]" in P5.build_tooltip(P5.evaluate(settings=st, today=_TODAY))


def test_invalid_manual_status_falls_back_to_auto():
    """레지스트리에 오타가 나면 자동 판정을 유지한다 — 조용히 충족 처리하지 않는다."""
    st = _FakeSettings(PHASE5_GATE_DECISIONS={5: {"status": "MET"}})  # 대문자 = 오타
    g = _by_num(P5.evaluate(settings=st, today=_TODAY))[5]
    assert g.status == P5.OPEN
    assert g.source == P5.SRC_AUTO


def test_all_met_gives_ok_level():
    """9개가 전부 충족이면 배지가 초록(ok)으로 바뀐다."""
    st = _FakeSettings(PHASE5_GATE_DECISIONS={
        n: {"status": P5.MET, "date": "2026-09-01"} for n in range(1, 10)})
    text, level, _tip, urgent = P5.badge(settings=st, today=_TODAY)
    assert level == "ok" and not urgent
    assert "9/9" in text


# ── 4. 깜빡임 정책 — 기한 있는 게이트만, D-7 경계 ────────────────────────

def test_no_blink_without_imminent_deadline():
    """평상시에는 깜빡이지 않는다. 상시 깜빡임이 교체 전 배지의 실패 원인이었다."""
    _text, level, _tip, urgent = P5.badge(settings=_FakeSettings(), today=_TODAY)
    assert not urgent
    assert level == "warn"


def test_blink_turns_on_inside_the_window_and_stays_on_past_due():
    """D-8은 조용, D-7부터 깜빡이고, 기한이 지나도 계속 깜빡인다."""
    st = _FakeSettings(PHASE5_GATE_DECISIONS={5: {"due": "2026-08-29"}})
    d = dt.date(2026, 8, 29)

    quiet = P5.badge(settings=st, today=d - dt.timedelta(days=P5.URGENT_WITHIN_DAYS + 1))
    edge = P5.badge(settings=st, today=d - dt.timedelta(days=P5.URGENT_WITHIN_DAYS))
    past = P5.badge(settings=st, today=d + dt.timedelta(days=3))

    assert quiet[3] is False, "D-8에 깜빡이면 창이 너무 넓다"
    assert edge[3] is True, "D-%d 경계에서 깜빡여야 한다" % P5.URGENT_WITHIN_DAYS
    assert past[3] is True, "기한이 지나면 더 깜빡여야 한다 — 조용해지면 안 된다"
    assert edge[1] == "urgent"
    assert "D-%d" % P5.URGENT_WITHIN_DAYS in edge[0]
    assert "경과" in past[0]


def test_met_gate_does_not_blink_even_when_due_passes():
    """충족된 게이트의 기한은 깜빡일 이유가 없다."""
    st = _FakeSettings(PHASE5_GATE_DECISIONS={
        5: {"due": "2026-08-29", "status": P5.MET, "date": "2026-08-20"}})
    _text, level, _tip, urgent = P5.badge(settings=st, today=dt.date(2026, 9, 10))
    assert not urgent and level == "warn"


def test_broken_due_date_does_not_crash():
    """날짜 형식이 깨져도 배지는 떠야 한다 — 대시보드 기동 경로다."""
    st = _FakeSettings(PHASE5_GATE_DECISIONS={5: {"due": "2026/08/29"}})
    g = _by_num(P5.evaluate(settings=st, today=_TODAY))[5]
    assert g.days_left is None and g.due_text() == ""


# ── 5. 실제 settings.py 연동 ──────────────────────────────────────────────

def test_real_settings_produce_a_badge():
    """운영 설정으로도 예외 없이 배지가 나온다(대시보드 기동 경로 종단)."""
    text, level, tip, urgent = P5.badge(today=_TODAY)
    assert text.startswith("Phase 5 게이트") or text.startswith("●")
    assert level in ("ok", "warn", "urgent")
    assert isinstance(urgent, bool)
    assert len(tip.splitlines()) >= 10


def test_real_registry_covers_all_nine_gates():
    """레지스트리에 9개 게이트가 모두 있어야 근거가 툴팁에 뜬다."""
    from config import settings
    reg = settings.PHASE5_GATE_DECISIONS
    missing = [n for n in range(1, 10) if not (reg.get(n) or {}).get("note")]
    assert not missing, "근거(note)가 비어 있는 게이트: %s" % missing


def test_tooltip_lines_fit_on_screen():
    """툴팁이 화면 세로를 넘지 않게 — 폭·줄수 상한.

    QToolTip은 평문을 자동 줄바꿈하지 않는다. 근거를 그대로 흘리면 화면 밖으로 뻗는다.
    """
    tip = P5.build_tooltip(P5.evaluate(today=_TODAY))
    lines = tip.splitlines()
    assert len(lines) <= 60, "툴팁이 %d줄 — 화면을 넘긴다" % len(lines)
    widest = max(P5._disp_width(x) for x in lines)
    assert widest <= P5._WRAP_COLS + 12, "툴팁 최대 표시폭 %d — 접기가 듣지 않았다" % widest


def test_truncation_is_visible():
    """근거를 줄였으면 줄였다고 말한다(계측 4원칙 ③ — 절단 가시화)."""
    long_note = "가" * 400
    st = _FakeSettings(PHASE5_GATE_DECISIONS={5: {"note": long_note}})
    tip = P5.build_tooltip(P5.evaluate(settings=st, today=_TODAY))
    assert "…" in tip
    assert "PHASE5_GATE_DECISIONS" in tip, "전문 위치를 안내해야 한다"


def _run_all():
    fns = [(k, v) for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in fns:
        try:
            fn()
            print("  [OK]   %s" % name)
        except Exception as e:
            failed += 1
            print("  [FAIL] %s -> %s: %s" % (name, type(e).__name__, e))
    print("\n%d/%d 통과" % (len(fns) - failed, len(fns)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
