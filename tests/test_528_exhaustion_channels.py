# -*- coding: utf-8 -*-
"""[MW0602 526차 후속8] 탈진 계열 채널 회귀 고정 — [18-U] · [59] · 정리 3건 · 활성화 잠금.

배경 (2026-09-03 탈진 레짐 조사보고)
-----------------------------------
「탈진」은 이름이 셋이고 서로 다른 것을 가리킨다 — ⓐ 미시레짐(전 기간 **0건**) ·
ⓑ `[18]` 진입 섀도 게이트(119건 발동) · ⓒ 챌린저 전문가 풀(챔피언 None).
사용자 결정(2026-09-03)으로 **세 축 모두 현행 유지**하되, "재검토하기로 했는데 안 함"이
되지 않도록 판정을 사람이 아니라 채널이 하게 옮겼다.

이 파일이 고정하는 불변식 5군
-----------------------------
1. **활성화 잠금(사용자 결정 ③)** — `REGIME_EXHAUSTION_GATE_ENABLED=False` ·
   `EXHAUSTION_RESTORE_MODE="shadow"`. 이 커밋은 어느 것도 켜지 않았다.
   누가 켜면 이 테스트가 막고, 켜려면 주간회의 결정과 함께 이 테스트를 고쳐야 한다.
2. **[59] 사전등록 상수** — 판정 창·표본·호라이즌 **단일 10분**(다중검정 회피)·
   MR 자격 한정·2주 연속. 사후 변경 금지(§9-4 검증 시계).
3. **[59] 기대방향 매핑** — `bull_exhaustion`(상승압력 소진)→**SHORT** /
   `bear_exhaustion`(하락압력 소진)→**LONG**. 뒤집히면 부호가 통째로 반대가 된다.
4. **[18] 본판정 불변 · [18-U] 임계 위임** — 분해는 OBSERVE이고 `te` 임계는
   `[57]` 사전등록값을 **읽어온다**(하드코딩하면 두 채널 기준이 조용히 갈린다).
5. **정리 3건(P-4)** — `REGIME_EXHAUSTION_PARAMS` 사본 제거·원본 유지 주석 ·
   챌린저 순환 잠금 주석 · 게이트 플래그 3계보 주석.

실행:
    "C:\\Users\\pc1\\anaconda3\\envs\\py37_32\\python.exe" tests/test_528_exhaustion_channels.py
    (pytest는 두 conda env 모두에 없다 — 파일 하단 러너로 돌린다)
"""
import inspect
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GEN = os.path.join(_ROOT, "scripts", "generate_validation_campaign_report.py")


def _R():
    import scripts.generate_validation_campaign_report as R
    return R


def _src(path=None):
    with io.open(path or _GEN, encoding="utf-8") as f:
        return f.read()


# ── 1. 활성화 잠금 (사용자 결정 ③) ──────────────────────────────────────────

def test_1_activation_locked():
    """세 축 모두 켜지 않았다 — 이 커밋은 계측만 추가했다.

    켜는 것은 각각 별개의 정책 결정이다:
      · `[18]` 활성화 → `faststop_discovery`(2026-08-03) 부분 철회 필요
      · live 전환    → 394차 조건 ⓐⓑⓒ + 주간회의
    """
    from config.settings import (REGIME_EXHAUSTION_GATE_ENABLED,
                                 EXHAUSTION_RESTORE_MODE,
                                 REGIME_EXHAUSTION_DEMOTE_TO)
    assert REGIME_EXHAUSTION_GATE_ENABLED is False, (
        "[18] 게이트가 켜졌다 — 2026-08-08 주간회의 보류 결정과 충돌한다")
    assert EXHAUSTION_RESTORE_MODE == "shadow", (
        "소진 피처가 live로 전환됐다 — 394차 조건 ⓐⓑⓒ 확인 없이는 금지")
    assert REGIME_EXHAUSTION_DEMOTE_TO == "C", (
        "강등 목표가 바뀌었다 — 317차 FalseBlock 교훈상 하드차단 금지")


def test_2_micro_regime_thresholds_frozen():
    """미시레짐 「탈진」 판정 3조건의 상수 — 83차 재설계값이다."""
    from collection.macro.micro_regime import MicroRegimeClassifier as M, REGIME_EXHAUSTION
    assert REGIME_EXHAUSTION == "탈진"
    assert M.ATR_EXHAUSTION_MIN == 1.2, (
        "83차가 급변장(1.5)과 겹치지 않게 신설한 하한이다 — 겹치면 dead code로 되돌아간다")
    assert M.ATR_VOLATILE_MULT == 1.5
    assert M.ATR_EXHAUSTION_MIN < M.ATR_VOLATILE_MULT, (
        "탈진 구간이 급변장에 삼켜진다 — 83차가 고친 바로 그 버그")
    assert M.VWAP_EXHAUSTION_MIN == 1.5


# ── 2. [59] 사전등록 ────────────────────────────────────────────────────────

def test_3_channel59_preregistered_constants():
    """판정 창·표본·호라이즌·모집단은 사후 변경 금지 대상이다."""
    from config.settings import VALIDATION_CAMPAIGN as V
    c = V["exhaustion_restore_watch"]
    assert c["start_date"] == "2026-09-04", (
        "판정 창이 바뀌었다 — 그 이전은 채널 설계를 정하며 이미 본 구간이다")
    assert c["min_samples"] == 20 and c["min_days"] == 10 and c["alpha"] == 0.05
    assert c["judgment_horizon_min"] == 10, (
        "판정 호라이즌은 **단일**이다 — 여러 개를 판정에 쓰면 다중검정이 된다")
    assert 10 not in tuple(c["aux_horizons_min"]), (
        "참고 호라이즌이 판정 호라이즌과 겹친다 — 같은 검정을 두 번 세게 된다")
    assert c["require_mr_eligible"] is True, (
        "판정 모집단이 전체 발화로 넓어졌다 — 거래되지 않을 분까지 세어 ⓐ를 잘못 통과시킨다")
    assert c["drop_worst_day"] is True
    assert c["consecutive_weeks_required"] == 2, "단주 관측으로 live 안건이 열린다"
    assert tuple(c["strength_tiers"]) == (0.60, 0.70)


def test_4_channel59_tiers_match_mr_constants():
    """층 경계는 checklist MR 분기의 실제 상수와 같아야 한다 — 갈리면 다른 것을 잰다."""
    from config.settings import (VALIDATION_CAMPAIGN as V,
                                 MR_EXHAUSTION_MIN, MR_EXHAUSTION_MIN_WEAK)
    t = tuple(V["exhaustion_restore_watch"]["strength_tiers"])
    assert t[0] == MR_EXHAUSTION_MIN_WEAK, (
        "약한 MR 하한이 checklist(%s)와 다르다" % MR_EXHAUSTION_MIN_WEAK)
    assert t[-1] == MR_EXHAUSTION_MIN, (
        "강한 MR 하한이 checklist(%s)와 다르다" % MR_EXHAUSTION_MIN)


# ── 3. [59] 기대방향 · 자격 판정 ────────────────────────────────────────────

def test_5_expected_direction_mapping():
    """bull(상승압력 소진)→SHORT · bear(하락압력 소진)→LONG. 뒤집히면 부호가 반대가 된다."""
    src = inspect.getsource(_R()._exhaustion_shadow_firings)
    assert "side = -1 if bull >= bear else 1" in src, (
        "기대방향 매핑이 바뀌었다 — checklist MR 분기(bull→SHORT LONG→bear)와 대응해야 한다")
    assert "vp > 1.5 if side == -1 else vp < -1.5" in src, (
        "MR 자격의 vwap 조건이 바뀌었다 — checklist 3_vwap 분기와 같아야 한다")


def test_6_firings_invariants_on_live_db():
    """실 DB에서 발화 행의 불변식 — side·자격이 서로 모순되지 않는다."""
    R = _R()
    rows, dropped = R._exhaustion_shadow_firings(R._campaign_start())
    for k in ("scanned", "bad_json", "no_vwap"):
        assert k in dropped, "탈락 카운터 누락: %s (계측 4원칙 ③)" % k
    if not rows:
        print("    (SKIP: 발화 0건 — 교정 섀도 미배포 세대일 수 있다)")
        return
    for r in rows:
        assert r["side"] in (-1, 1)
        assert r["strength"] > 0, "발화인데 강도가 0 이하다"
        if r["mr_eligible"]:
            assert r["strength"] >= 0.60
            assert (r["vwap_position"] > 1.5) if r["side"] == -1 else (r["vwap_position"] < -1.5)


def test_7_channel59_verdict_requires_three_conditions():
    """조건ⓐ는 3검 AND다 — 하나라도 빠지면 이상치 1일로 통과한다."""
    src = inspect.getsource(_R().eval_exhaustion_restore_watch)
    assert "if sig and pos and ex_worst_ok:" in src, (
        "조건ⓐ 결합이 바뀌었다 — 유의·평균양·drop-worst 셋 다 필요하다")
    assert "SUPPORTS_LIVE" in src and "REJECTS_LIVE" in src
    assert "require_mr_eligible" in src, "MR 자격 한정이 사라졌다"
    assert "judgment_horizon_min" in src, "판정 호라이즌 단일 고정이 사라졌다"


def test_8_channel59_does_not_flip_the_switch():
    """채널은 판정만 한다 — `EXHAUSTION_RESTORE_MODE`에 쓰지 않는다."""
    src = inspect.getsource(_R().eval_exhaustion_restore_watch)
    assert "EXHAUSTION_RESTORE_MODE =" not in src, "채널이 모드를 직접 바꾼다 — §9 위반"
    assert "runtime_settings" not in src, "채널이 런타임 설정을 건드린다"


# ── 4. [18-U] ──────────────────────────────────────────────────────────────

def test_9_channel18u_reads_te_threshold_from_57():
    """te 임계는 `[57]` 사전등록값을 읽어온다 — 하드코딩하면 두 채널 기준이 갈린다."""
    src = inspect.getsource(_R().eval_regime_exhaustion_unique_split)
    assert "trend_efficiency_entry_gate" in src, "[57] 사전등록값을 참조하지 않는다"
    assert 'get("threshold", 0.32)' in src, "임계를 채널에서 읽지 않고 박아 넣었다"
    assert src.count("0.32") == 1, (
        "0.32 리터럴이 폴백 외에 또 있다 — [57]이 임계를 바꾸면 갈린다")


def test_10_channel18_judgment_untouched():
    """[18] 본판정에 분해가 섞이면 안 된다 — 분해는 OBSERVE 별 함수다."""
    R = _R()
    src = inspect.getsource(R.resolve_and_eval_regime_exhaustion)
    for bad in ("unique_split", "trend_efficiency", "te_ge", "te_lt"):
        assert bad not in src, "[18] 판정 함수가 분해를 참조한다(%s) — 판정 무영향 원칙 위반" % bad
    from config.settings import VALIDATION_CAMPAIGN as V
    c = V["regime_exhaustion_watch"]
    assert c["min_samples"] == 20 and c["cf_window_min"] == 30, "[18] 사전등록값이 바뀌었다"
    assert R.eval_regime_exhaustion_unique_split.__doc__ and \
        "OBSERVE" in R.eval_regime_exhaustion_unique_split.__doc__


# ── 5. 정리 3건 (P-4) · 렌더 위생 ──────────────────────────────────────────

def test_11_duplicate_params_removed_original_kept():
    """`REGIME_EXHAUSTION_PARAMS`는 `micro_regime.py` 한 곳에만 남는다."""
    import config.settings as S
    assert not hasattr(S, "REGIME_EXHAUSTION_PARAMS"), (
        "settings 사본이 되살아났다 — 정의는 micro_regime.py 하나여야 한다")
    from collection.macro.micro_regime import REGIME_EXHAUSTION_PARAMS as P
    assert P["hurst_override"] is True and P["min_confidence"] == 0.56
    micro = _src(os.path.join(_ROOT, "collection", "macro", "micro_regime.py"))
    assert "어디서도 읽히지 않는다" in micro, (
        "원본에 '사문화' 주석이 없다 — 다음 사람이 값을 고치면 라이브가 바뀔 거라 오해한다")


def test_12_cleanup_comments_present():
    """순환 잠금·3계보 주석이 살아 있는가(다음 세션의 오독 방지 장치)."""
    reg = _src(os.path.join(_ROOT, "challenger", "challenger_registry.py"))
    assert "순환 잠금" in reg and "min_regime_trades" in reg, (
        "챌린저 순환 잠금 설명이 사라졌다 — 승격 시계가 시작된 적 없다는 사실이 묻힌다")
    st = _src(os.path.join(_ROOT, "config", "settings.py"))
    assert "이 게이트는 미시레짐 「탈진」·챌린저 탈진 전문가 풀과 별개다" in st, (
        "3계보 구분 주석이 사라졌다 — '탈진이 N번 작동했다'는 오독이 재발한다")


def test_13_render_and_vocabulary_wired():
    """요약행·판정 어휘·채널 번호 유일성."""
    src = _src()
    assert "_row_462(59," in src, "[59] 요약행이 없다"
    assert '"SUPPORTS_LIVE": ' in src and '"REJECTS_LIVE": ' in src, (
        "판정 어휘 미등록 — _fmt_verdict가 INSUFFICIENT로 조용히 폴백한다")
    assert _R()._fmt_verdict("SUPPORTS_LIVE").startswith("🔶")
    assert "[18-U]" in src and "## [59]" in src, "상세 절이 없다"
    nums = re.findall(r'L\.append\("\| \[(\d+)\]', src)
    nums += re.findall(r"_row_462\((\d+),", src)
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    assert not dupes, "요약표 채널 번호 중복: %s" % dupes


if __name__ == "__main__":
    fns = [(n, f) for n, f in sorted(globals().items())
           if n.startswith("test_") and callable(f)]
    ok = fail = 0
    for name, fn in fns:
        try:
            fn()
            print("  PASS %s" % name)
            ok += 1
        except Exception as e:
            print("  FAIL %s -> %s: %s" % (name, type(e).__name__, e))
            fail += 1
    print("\n%d passed, %d failed (of %d)" % (ok, fail, len(fns)))
    sys.exit(1 if fail else 0)
