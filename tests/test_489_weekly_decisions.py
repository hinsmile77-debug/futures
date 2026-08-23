# -*- coding: utf-8 -*-
"""[MW0602 489차] 2026-08-23 주간회의 결정 9건(D1~D9)의 불변식.

이 파일이 지키는 것
-------------------
주간회의 결정은 **문서에만 적으면 다음 세션이 모른다.** 실제로 그 사고가 반복됐다 —
[6] Hurst 완화 권고는 2026-07-15에 배포됐는데 리포트가 3주째 같은 권고를 찍어
0801 결산 초안이 신규 안건으로 잘못 올렸다(코드 확인 후 철회). `VALIDATION_CAMPAIGN_DECISIONS`
레지스트리가 그 재발 방지책이고, 이 테스트는 **그 레지스트리와 사전등록이 실재하는지**를 고정한다.

무엇을 덮고 무엇을 안 덮나
--------------------------
- 덮는다: 결정이 레지스트리에 있는가 · 사전등록 문턱이 관측값에서 역산되지 않았는가 ·
  라이브 스위치가 결정대로 **무변경**인가 · 새 채널이 계약(compute/summarize)을 지키는가.
- 안 덮는다: 판정 결과의 옳음. 그것은 표본이 차야 알 수 있고, 이 테스트의 일이 아니다.

⚠ 이 파일이 깨지면 **결정이 조용히 뒤집힌 것**이다. 고치기 전에 왜 바뀌었는지부터 확인할 것.
"""
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

from config.settings import (  # noqa: E402
    VALIDATION_CAMPAIGN,
    VALIDATION_CAMPAIGN_DECISIONS,
    CB_CONSEC_STOP_LIMIT,
    TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED,
    ATR_MAX_ENTRY,
)

_CLAUDE_MD = os.path.join(_ROOT, "CLAUDE.md")


def _claude_md():
    with open(_CLAUDE_MD, encoding="utf-8") as f:
        return f.read()


# ──────────────────────────────────────────────────────────────────────────
# D1 — [2] Meta-Gate 최종 탈락 확정
# ──────────────────────────────────────────────────────────────────────────
def test_d1_meta_gate_final_rejection_recorded():
    """재개 조건이 소진됐다는 사실이 레지스트리에 남아 있어야 한다.

    0801 결정문은 재개 조건을 *"경계 이후 데이터로만 분위당 n≥300을 채운 뒤 재측정"*
    이라 적었고, 489차가 그것을 충족해 재측정했다(분위당 411, 분리도 −0.0136).
    ⇒ 이 조건을 근거로 **다시 재개하려는 시도**를 막는다.
    """
    d = VALIDATION_CAMPAIGN_DECISIONS["meta_gate"]
    assert d["date"] == "2026-08-23", "489차 D1 갱신이 사라졌다"
    assert "최종 탈락 확정" in d["decision"]
    # 재측정 실측치가 남아 있어야 근거를 되짚을 수 있다
    assert "1,233" in d["note"] or "1233" in d["note"]
    assert "411" in d["note"]
    assert "0.0136" in d["note"]


# ──────────────────────────────────────────────────────────────────────────
# D2 — CB② 복원: 날짜 기한 → 사건 기한 + 채널 [56]
# ──────────────────────────────────────────────────────────────────────────
def test_d2_cb2_limit_unchanged():
    """결정은 '유지'다. 이 테스트가 깨지면 누군가 라이브 CB②를 건드린 것이다.

    ⚠ 복원 자체는 금지가 아니다 — 다만 **⑧ 해제와 같은 커밋**이어야 한다(D2).
      그 커밋이라면 이 테스트도 함께 고치는 것이 맞다.
    """
    assert CB_CONSEC_STOP_LIMIT == 9999


def test_d2_cb2_shadow_channel_preregistered():
    cfg = VALIDATION_CAMPAIGN["cb2_restore_shadow"]
    assert cfg["enabled"] is True
    # 절대원칙 §2의 복원 목표 "2~3" 양쪽을 다 센다 — 한쪽만 세면 방향이 갈리는 사실이 숨는다
    assert sorted(cfg["candidates"]) == [2, 3]
    # 판정 창이 사후탐색 구간과 분리돼 있어야 한다 (313차 ④)
    assert cfg["start_date"] == "2026-08-24"
    # 집계 단위 — 470차 C1. 레그로 되돌리면 2026-08-14 이전 로그와 같은 과대계상이 된다
    assert cfg["unit"] == "position"
    assert cfg["win_field"] == "pnl_pts"
    for k in ("min_samples", "min_days", "alpha", "drop_worst_days"):
        assert k in cfg, "사전등록 관문 %s 누락" % k


def test_d2_cb2_shadow_script_contract():
    """오프라인 채널 규약 — 리포터가 `summarize(compute(start))`로만 부른다."""
    import scripts.cb2_restore_shadow as m
    assert hasattr(m, "compute") and hasattr(m, "summarize")
    res = m.summarize(m.compute("2026-07-14"))
    assert "verdict" in res and "per_limit" in res
    # 판정 창이 미래(또는 오늘)라 아직 표본이 없다 — INSUFFICIENT가 정상이다.
    # ⚠ 표본이 차서 이 단언이 깨지면 그때가 **판정할 시점**이다(테스트를 고칠 시점이기도 하다).
    assert set(res["per_limit"]) == {"2", "3"}


def test_d2_cb2_shadow_avoids_math_comb():
    """`math.comb`은 Python 3.8+ 전용인데 런타임은 py37_32다.

    표본이 `min_samples`에 닿기 전에는 부호검정이 호출되지 않으므로, `comb`을 쓰면
    **몇 달 뒤 표본이 찬 바로 그날 처음 터진다**(지연 폭발). 소스로 고정한다.
    """
    path = os.path.join(_ROOT, "scripts", "cb2_restore_shadow.py")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    assert "from math import comb" not in src and "math.comb(" not in src


def test_d2_deadline_moved_from_date_to_event():
    """CLAUDE.md에서 '재검토 2026-08-29'가 **효력 종료**로 표기돼야 한다.

    날짜만 지우면 다음 세션이 "기한이 없어졌다 = 무기한 유예"로 읽는다. 그래서
    ⑧ 해제와 묶였다는 사실이 같이 있어야 한다.
    """
    md = _claude_md()
    assert "효력 종료" in md and "2026-08-29" in md, "폐기 사실과 원 날짜가 함께 남아야 한다"
    assert "cb2_restore_shadow" in md, "대체 계측(채널 [56])이 문서에 없다"


# ──────────────────────────────────────────────────────────────────────────
# D3 — [46] Hurst 임계: 미적용 + 감시 승격
# ──────────────────────────────────────────────────────────────────────────
def test_d3_hurst_promotion_watch_preregistered():
    pw = VALIDATION_CAMPAIGN["hurst_threshold_shadow"]["promotion_watch"]
    assert pw["enabled"] is True
    assert pw["candidate"] == "abs_0.39"
    assert pw["start_date"] == "2026-08-24"
    # 🔴 문턱이 관측값에서 역산되지 않았음을 고정한다.
    #    marginal_cost_mult=1.0 은 **손익분기(왕복비용) 그 자체**이지 0821 실측
    #    (+0.64pt/11일)을 보고 정한 값이 아니다. 1.0이 아닌 값으로 바뀌면
    #    "관측 후 문턱 조정"을 의심할 것(313차 ④).
    assert pw["marginal_cost_mult"] == 1.0
    assert pw["min_marginal_samples"] == 20     # 캠페인 공통값
    assert pw["drop_worst_days"] == 1           # 372차 함정 방어
    assert pw["require_separation_hold"] is True


def test_d3_candidate_is_an_existing_sweep_option():
    """후보가 본 채널의 스윕 목록 안에 있어야 한다 — 새 값을 지어내면 사전등록이 무의미하다."""
    cfg = VALIDATION_CAMPAIGN["hurst_threshold_shadow"]
    assert 0.39 in cfg["abs_candidates"]


def test_d3_decision_registered():
    d = VALIDATION_CAMPAIGN_DECISIONS["hurst_threshold_shadow"]
    assert d["date"] == "2026-08-23"
    assert "미적용" in d["decision"]
    # 매주 재출력되는 FAIL을 미조치로 오독하지 말라는 경고가 남아 있어야 한다
    assert "재출력" in d["note"] or "미조치" in d["note"]


# ──────────────────────────────────────────────────────────────────────────
# D5 — [44] DynMC: 보류 사유 교체 (침묵을 승인으로 읽지 않게)
# ──────────────────────────────────────────────────────────────────────────
def test_d5_dynmc_hold_reason_replaced():
    """0816 보류 사유('MW0601 판정 대기')는 487차 정책 폐기로 **소멸**했다.

    사유가 사라졌는데 새 사유를 안 적으면 다음 세션이 "보류 근거가 없어졌으니 적용"으로
    읽는다. 그 공백을 막는 것이 이 항목의 존재 이유다.
    """
    d = VALIDATION_CAMPAIGN_DECISIONS["dynmc_collapse_feed_watch"]
    assert d["date"] == "2026-08-23"
    assert "보류" in d["decision"]
    assert "소멸" in d["note"], "종전 사유가 왜 없어졌는지가 남아야 한다"
    assert "재개 조건" in d["note"], "무엇이 충족되면 다시 여는지가 없다"


# ──────────────────────────────────────────────────────────────────────────
# D6 — 전환기준 ①·④ 미충족 기록 + ⑧ 동결
# ──────────────────────────────────────────────────────────────────────────
def test_d6_criterion_8_has_precondition_on_criterion_1():
    """⑧의 남은 관문이 '사용자 결정' 하나뿐이라 **명시적 잠금**이 없으면 오늘이라도 열린다."""
    md = _claude_md()
    assert "① 충족되기 전에는 ⑧을 해제하지 않는다" in md or \
           "①이 충족되기 전에는 ⑧을 해제하지 않는다" in md, \
           "⑧ 선행조건(D6)이 CLAUDE.md에서 사라졌다"


def test_d6_criteria_1_and_4_marked_unmet():
    md = _claude_md()
    assert "−178,004원" in md, "① 실측(최근 20거래일)이 없다"
    assert "415,784원" in md, "④ 실측(일손익 표준편차)이 없다"


# ──────────────────────────────────────────────────────────────────────────
# D7 — ⑨ TOX-SEVERE-SPREAD: 26주 WFA 이관 (라이브 무변경)
# ──────────────────────────────────────────────────────────────────────────
def test_d7_live_switch_unchanged():
    """이관은 **거버넌스 결정**이지 라이브 변경이 아니다."""
    assert TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED is False


def test_d7_transferred_and_registered_in_wfa_list():
    """461차가 이 항목을 등재한 이유가 '복원 조건이 없어 누락되던 것'이었다.

    이관이 그 상태를 재현하면 안 되므로, 26주 목록에 **명시 등재**돼 있어야 한다.
    """
    md = _claude_md()
    assert "26주 WFA 재검증 항목으로\n   이관됨" in md or "26주 WFA 재검증 항목으로 이관" in md
    head = md.index("## 주기적 재검증 항목")
    assert "TOX-SEVERE-SPREAD" in md[head:], "26주 목록에 등재되지 않았다 — 이관 조건 1 미충족"


# ──────────────────────────────────────────────────────────────────────────
# D8 — [55] (E)안 사전등록 (사후탐색 문턱 방지)
# ──────────────────────────────────────────────────────────────────────────
def test_d8_vol_condition_prereg_exists():
    pr = VALIDATION_CAMPAIGN["early_window_gate_shadow"]["vol_condition_prereg"]
    assert pr["enabled"] is True
    assert pr["start_date"] == "2026-08-24"
    assert pr["keep_size_half"] is True, "size×0.5 분리 존치는 노출 완충 장치다"


def test_d8_threshold_is_anchored_not_posthoc():
    """🔴 **이 테스트가 이 파일에서 가장 중요하다.**

    486차 B-4의 ATR 3분위 경계(저 <4.242 / 고 ≥5.297)는 **사후탐색**이다. 그 값을
    문턱으로 쓰면 사후 데이터로 기준을 만드는 것이라 313차 원칙 ④ 위반이다.
    그래서 (E)안은 이 채널과 무관하게 이미 존재하던 시스템 상수 `ATR_MAX_ENTRY`에
    앵커했다 — 3.5는 4.242도 5.297도 아니다.
    """
    pr = VALIDATION_CAMPAIGN["early_window_gate_shadow"]["vol_condition_prereg"]
    assert pr["atr_ceiling_source"] == "ATR_MAX_ENTRY"
    # 하드코딩된 숫자를 두지 않는다 — 앵커가 바뀌면 함께 움직여야 한다
    assert "atr_ceiling" not in pr, "임계를 하드코딩하지 말 것 (앵커 상수를 쓴다)"
    # 사후탐색 경계와 우연히라도 같아지면 즉시 잡는다
    assert abs(float(ATR_MAX_ENTRY) - 4.242) > 1e-6
    assert abs(float(ATR_MAX_ENTRY) - 5.297) > 1e-6


# ──────────────────────────────────────────────────────────────────────────
# D9 — 458차 만성도 계측: 소비부 제거 (양방향 잠금)
# ──────────────────────────────────────────────────────────────────────────
def test_d9_consumer_removed_together():
    """소비부는 **둘 다** 지워져야 한다. 한쪽만 남기면 다음 이관 때 함정이 재생된다."""
    assert not os.path.exists(
        os.path.join(_ROOT, "tests", "test_473_state_file_isolation.py"))
    with open(os.path.join(_ROOT, "tests", "conftest.py"), encoding="utf-8") as f:
        src = f.read()
    assert "def _isolate_feature_exclusion_state" not in src


def test_d9_producer_still_absent_on_this_branch():
    """🔴 **양방향 잠금** — 생산부가 이 브랜치에 들어오면 이 테스트가 깨진다.

    그때 해야 할 일은 이 단언을 지우는 게 아니라 **격리를 되살리는 것**이다
    (`.claude/skills/mireuk-daily-check/references/invariants.md` §0-C).
    """
    import features.horizon_feature_registry as reg
    if hasattr(reg, "_chronic_suffix") or hasattr(reg, "_CHRONIC_PATH"):
        pytest.fail(
            "458차 만성도 계측 생산부가 이 브랜치에 들어왔다 — D9로 지운 격리를 "
            "되살릴 것: tests/conftest.py autouse fixture + "
            "tests/test_473_state_file_isolation.py (invariants.md §0-C 참조)")


def test_d9_restoration_condition_is_documented():
    inv = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check",
                       "references", "invariants.md")
    with open(inv, encoding="utf-8") as f:
        src = f.read()
    assert "0-C" in src and "_isolate_feature_exclusion_state" in src


# ──────────────────────────────────────────────────────────────────────────
# 횡단 — 리포트 어휘 등록 누락 방지
# ──────────────────────────────────────────────────────────────────────────
def test_new_verdicts_are_registered_in_report_vocabulary():
    """리포터 `_fmt_verdict()` 주석이 스스로 경고한다 —

        "이 표에 없는 verdict는 조용히 INSUFFICIENT로 표시된다"

    486차가 [55] 어휘를 빠뜨렸으면 **채널이 살아 있는데 표본 미달처럼 보였을 것**이다.
    같은 함정을 [56]에 대해 고정한다.
    """
    path = os.path.join(_ROOT, "scripts", "generate_validation_campaign_report.py")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    for v in ("RESTORE_FAVORS_CB2", "RESTORE_COSTS", "SPLIT_BY_LIMIT", "NO_EVIDENCE"):
        assert '"%s":' % v in src, "[56] 판정 어휘 %s 가 리포터에 등록되지 않았다" % v


def test_channel_decision_strings_have_no_nested_bold():
    """`_dm()`이 결정 문자열을 `**...**`로 감싼다 — 안에 또 `**`가 있으면 요약표가 깨진다.

    ⚠ **채널 키인 결정만** 대상이다. `sizing_prescription_axis`처럼 특정 채널에 붙지 않는
      **횡단 결정**은 `_dm()`을 타지 않고 레지스트리 섹션에만 렌더링되므로 볼드가 허용된다
      (431차가 실제로 그렇게 쓰고 있다). 그 차이를 모르고 전부 금지하면 무관한 항목을 건드리게 된다.
    """
    for key, d in VALIDATION_CAMPAIGN_DECISIONS.items():
        if key not in VALIDATION_CAMPAIGN:
            continue  # 횡단 결정 — 요약표 행이 없다
        assert "**" not in d["decision"], \
            "%s: 채널 결정 문자열에 볼드 마크업 금지(_dm이 감싼다)" % key
