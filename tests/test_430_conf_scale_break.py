"""[MW0602 430차] conf 스케일 불연속 마커 · [44] DynMC 붕괴행 잠식 · [45] 가드 플래핑.

────────────────────────────────────────────────────────────────────────────
왜 이 세 개인가 — "앙상블 신뢰도가 좋아졌다"는 관측의 실체
────────────────────────────────────────────────────────────────────────────
2026-08-04 사용자가 "앙상블 신뢰도가 최근 드라마틱하게 좋아졌다"고 관측했다.
딥다이브 결과 **모델은 아무것도 좋아지지 않았다**:

  평균 conf        0.316(07-30) → 0.406(07-31) → 0.491(08-04)   +55%
  confidence_raw   0.491        → 0.506        → 0.515          거의 무변화
  보정 미적용률    2.7%         → 30.8%        → 98.6%          ← 이것이 원인

403차가 2026-07-31 배포한 축퇴 가드(`learning/calibration.py`)가 앙상블 보정기를
사실상 껐고, 눌려 있던 raw 가 그대로 노출된 것이다. 판별력은 그대로 없다 —
raw conf 의 1m 적중 순위 **AUC = 0.489**(0.5 미만 = 역방향)이며 427차 [39]
REJECTS_HYP 와 일치한다.

상승분의 **65%는 `weight_collapsed=1`(판단 불가) 행**이 만든다. 인위적 raw≈1.0 이
보정 없이 0.85 로 클리핑돼 나가기 때문이다(전환 전에는 보정기가 0.33 으로 눌렀다).

────────────────────────────────────────────────────────────────────────────
지키려는 불변식
────────────────────────────────────────────────────────────────────────────
(A) **불연속은 사람 기억이 아니라 코드에 있어야 한다.** 이 경계는 어떤 문서에도
    적혀 있지 않았고, 딥다이브 전에는 세션도 반증 근거가 없었다. CLAUDE.md 가
    기록한 사고 유형(이행된 권고를 신규 안건으로 오인 등)과 같은 계열이다.
    → `CONF_SCALE_BREAKS` 가 있고, 리포트가 창을 걸칠 때 **자동으로** 경고한다.

(B) **경고는 걸칠 때만 떠야 한다.** 늘 떠 있으면 아무도 안 읽는다.

(C) **[44]의 base_mc 재현은 라이브와 같은 식이어야 한다.** 다르면 이 채널이 재는
    것이 라이브와 무관해진다 — `update_dynamic_mc()`와의 패리티를 직접 검증한다.

(D) **위음성이 가장 위험하다** — 427차 §4와 같은 설계다. "잠식 없음"과 "탐지
    불능"은 같은 출력을 낸다. 그래서 합성 데이터로 두 채널이 **실제로 발화하는지**
    확인한다.

(E) **[44]는 배선을 자동으로 바꾸지 않는다.** 붕괴행 제외는 진입을 늘리는데,
    427차가 확정한 대로 min_conf 는 무작위 샘플러라 기대값 부호가 보장되지 않고,
    CLAUDE.md ⑧ 미해제 상태에서는 진입 증가 = 노출 증가다. → 권고문에 그 경고가
    반드시 들어 있어야 한다(문구가 사라지면 다음 세션이 그냥 배선한다).

(F) **[45]는 임계 튜닝을 정당화하지 않는다.** 근본 문제는 임계가 아니라 정보
    부재다. 권고문이 "AUC 임계·함수형 손대지 말 것"을 유지해야 한다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _rep():
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import importlib
    return importlib.import_module("generate_validation_campaign_report")


# ══════════════ (A) 불연속 레지스트리 자체 ══════════════

def test_registry_shape():
    """CONF_SCALE_BREAKS 가 존재하고 07-31 경계를 담고 있는가."""
    from config.settings import CONF_SCALE_BREAKS
    check("레지스트리 비어있지 않음", len(CONF_SCALE_BREAKS) >= 1)
    dates = [b.get("date") for b in CONF_SCALE_BREAKS]
    check("2026-07-31 경계 등재", "2026-07-31" in dates)
    for b in CONF_SCALE_BREAKS:
        for k in ("date", "label", "cause", "evidence"):
            check("항목 %s 에 %s 존재" % (b.get("date"), k), bool(b.get(k)))
    # 근거에 실측 수치가 들어 있어야 한다 — 산문만 남으면 다음 세션이 재확인 못 한다.
    b0 = [b for b in CONF_SCALE_BREAKS if b["date"] == "2026-07-31"][0]
    check("실측 수치 포함(98.6%)", "98.6" in b0["evidence"])
    # ⚠ 이 경계를 "개선"으로 읽는 것을 막는 문장이 반드시 있어야 한다.
    check("판별력 없음 경고 포함", "AUC" in (b0.get("caveat") or ""))


def test_window_detection():
    """(B) 창이 걸칠 때만 경고한다."""
    rep = _rep()
    # 경계 이전에 시작 → 걸친다
    check("07-05 시작 창은 걸침", len(rep._conf_scale_breaks_in("2026-07-05")) == 1)
    # 경계 당일부터 시작 → 창 전체가 전환 후 체제이므로 걸치지 않는다
    check("07-31 시작 창은 안 걸침", len(rep._conf_scale_breaks_in("2026-07-31")) == 0)
    # 경계 이후 시작 → 안 걸린다
    check("08-01 시작 창은 안 걸침", len(rep._conf_scale_breaks_in("2026-08-01")) == 0)
    # 상한이 경계 이전이면 안 걸린다
    check("07-05~07-20 창은 안 걸침",
          len(rep._conf_scale_breaks_in("2026-07-05", "2026-07-20")) == 0)
    # 마크다운 줄도 같은 규칙을 따른다
    check("걸칠 때 경고문 생성", len(rep._conf_scale_break_lines("2026-07-05")) > 0)
    check("안 걸칠 때 경고문 없음", rep._conf_scale_break_lines("2026-08-01") == [])


# ══════════════ (C) [44] base_mc 재현이 라이브와 같은가 ══════════════

def test_base_mc_parity_with_live():
    """리포트의 `_base_mc_from` 이 `update_dynamic_mc()` 와 같은 값을 내는가.

    라이브는 `_ZONE_PARAMS` 를 갱신하는 부작용이 있으므로, 여기서는 **base_mc
    산출부만** 비교한다(STEP_LIMIT 클램프는 과도항이라 리포트가 의도적으로
    재현하지 않는다 — 채널이 묻는 것은 수렴점이다).
    """
    rep = _rep()
    from config.settings import MC_PERCENTILE, MC_ABS_FLOOR, MC_ABS_CEIL

    def live_formula(confs):
        s = sorted(confs)
        p = s[min(int(len(s) * MC_PERCENTILE), len(s) - 1)]
        return max(MC_ABS_FLOOR, min(MC_ABS_CEIL, p))

    cases = [
        [0.30 + 0.001 * i for i in range(200)],              # 균등
        [0.85] * 50 + [0.35] * 150,                          # 붕괴행 다수
        [0.20] * 100,                                        # 전부 하한 아래
        [0.90] * 100,                                        # 전부 상한 위
        [0.33, 0.41, 0.52],                                  # 소표본
    ]
    for i, c in enumerate(cases):
        a, b = rep._base_mc_from(c), live_formula(c)
        check("base_mc 패리티 case%d (%.4f == %.4f)" % (i, a, b), abs(a - b) < 1e-12)
    # 상하한 클램프가 실제로 걸리는지 — 패리티만 보면 둘 다 틀려도 통과한다
    check("MC_ABS_FLOOR 클램프", rep._base_mc_from([0.20] * 100) == MC_ABS_FLOOR)
    check("MC_ABS_CEIL 클램프", rep._base_mc_from([0.90] * 100) == MC_ABS_CEIL)


# ══════════════ (D) 위음성 방지 — 채널이 실제로 발화하는가 ══════════════

def test_channel_44_fires_on_synthetic():
    """합성 데이터로 [44] 판정 성분이 발화하는지 확인.

    평가함수는 DB를 읽으므로 여기서는 **판정 산술**을 같은 식으로 재현해
    "붕괴행이 상단을 점유하면 통과율이 설계에서 이탈한다"가 수치로 성립함을 본다.
    이게 성립하지 않으면 채널은 영원히 REJECTS 에 갇힌다.
    """
    rep = _rep()
    from config.settings import MC_PERCENTILE
    design = 1.0 - MC_PERCENTILE

    # 정상 신호 800행(0.30~0.50 균등) + 붕괴행 200행(0.85 고정) = 20%
    non = [0.30 + 0.20 * (i / 799.0) for i in range(800)]
    col = [0.85] * 200
    mc_cur = rep._base_mc_from(non + col)
    mc_alt = rep._base_mc_from(non)
    pass_cur = sum(1 for c in non if c >= mc_cur) / float(len(non))
    pass_alt = sum(1 for c in non if c >= mc_alt) / float(len(non))
    gap_pp = (design - pass_cur) * 100.0

    check("붕괴행이 base_mc 를 밀어올린다 (%.4f > %.4f)" % (mc_cur, mc_alt),
          mc_cur > mc_alt)
    check("붕괴행 제외 시 통과율이 설계에 근접 (%.3f ≈ %.3f)" % (pass_alt, design),
          abs(pass_alt - design) < 0.02)
    check("현행 통과율이 설계보다 낮다 (%.3f < %.3f)" % (pass_cur, design),
          pass_cur < design)
    from config.settings import VALIDATION_CAMPAIGN
    thr = float(VALIDATION_CAMPAIGN["dynmc_collapse_feed_watch"]["pass_rate_gap_min_pp"])
    check("이탈 %.2f%%p 가 임계 %.1f%%p 를 넘는다 (발화 가능)" % (gap_pp, thr),
          gap_pp >= thr)

    # 대조군 — 붕괴행이 없으면 이탈이 임계 아래여야 한다(오탐 방지)
    mc_n = rep._base_mc_from(non)
    gap_none = (design - sum(1 for c in non if c >= mc_n) / float(len(non))) * 100.0
    check("붕괴행 없으면 이탈이 임계 미만 (%.2f < %.1f)" % (gap_none, thr),
          gap_none < thr)


def test_channel_45_passthru_detection():
    """[45]의 보정 미적용 판정과 전환 카운트가 정확한가.

    규칙: `confidence == min(confidence_raw, 0.85)` → 미적용.
    ⚠ 허용오차는 DB 저장이 `round(x,4)`이기 때문이다 — 424차가 float32 허용오차로
    같은 함정을 밟았으므로 경계값을 명시적으로 시험한다.
    """
    _TOL = 6e-4
    _CLIP = 0.85

    def is_pass(conf, raw):
        return abs(conf - min(raw, _CLIP)) < _TOL

    check("미적용: raw 0.40 → conf 0.40", is_pass(0.40, 0.40))
    check("미적용: raw 0.96 → conf 0.85 (클리핑)", is_pass(0.85, 0.96))
    check("적용: raw 0.96 → conf 0.33", not is_pass(0.33, 0.96))
    check("적용: raw 0.40 → conf 0.3312", not is_pass(0.3312, 0.40))
    # 반올림 경계 — round(x,4) 오차는 미적용으로 읽혀야 한다
    check("반올림 오차 0.00005 는 미적용", is_pass(0.40005, 0.40))
    # 진짜 보정 차이는 미적용으로 읽히면 안 된다
    check("0.001 차이는 적용으로 읽힘", not is_pass(0.401, 0.40))

    def _flips(seq):
        return sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])

    # 전환 카운트 — 시퀀스 [F,F,T,T,F] 는 전환 2회
    check("전환 카운트 2회", _flips([False, False, True, True, False]) == 2)
    check("전환 없는 시퀀스는 0회", _flips([True] * 4) == 0)
    # 매분 뒤집히는 최악 케이스 — 08-04 에 실제로 관측된 패턴이다
    check("교대 시퀀스는 n-1회", _flips([True, False, True, False]) == 3)


# ══════════════ (E)(F) 권고문의 안전장치가 살아 있는가 ══════════════

def test_channel_thresholds_registered():
    """임계가 사전등록돼 있고 근거가 주석에 남아 있는가."""
    from config.settings import VALIDATION_CAMPAIGN
    c44 = VALIDATION_CAMPAIGN.get("dynmc_collapse_feed_watch")
    c45 = VALIDATION_CAMPAIGN.get("cal_guard_flap_watch")
    check("[44] 채널 등록", c44 is not None)
    check("[45] 채널 등록", c45 is not None)
    for k in ("start_date", "min_days", "min_rows",
              "pass_rate_gap_min_pp", "min_day_share", "constout_threshold"):
        check("[44] %s 등록" % k, k in c44)
    for k in ("start_date", "min_days", "flip_per_day_warn", "conf_jump_warn"):
        check("[45] %s 등록" % k, k in c45)
    # 판정 창 방어선 — 10일 롤링이 채워지기 전 판정을 막는다
    check("[44] min_days >= 10 (base_mc 10일 롤링)", int(c44["min_days"]) >= 10)
    # 두 채널 모두 전환 후 데이터만 본다
    check("[44] start_date == 2026-07-31", c44["start_date"] == "2026-07-31")
    check("[45] start_date == 2026-07-31", c45["start_date"] == "2026-07-31")
    # ConstOut 임계는 main.py 와 같아야 한다(표류 방지)
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    check("ConstOut 임계 0.15 가 main.py 와 일치",
          "len(confs) * 0.15" in src and float(c44["constout_threshold"]) == 0.15)


def test_safety_wording_present():
    """(E)(F) 배선을 막는 경고 문구가 코드에 남아 있는가.

    문구가 사라지면 다음 세션이 판정만 보고 그냥 배선한다 — 실제로 이 프로젝트에서
    "이행된 권고를 신규 안건으로 오인"·"일부러 적용 안 한 FAIL 미기록" 사고가
    양방향으로 다 있었다(CLAUDE.md 검증 캠페인 운영 모드).
    """
    rep_src = open(os.path.join(_ROOT, "scripts",
                                "generate_validation_campaign_report.py"),
                   encoding="utf-8").read()
    check("[44] 무작위 샘플러 경고", "무작위 샘플러" in rep_src)
    check("[44] 노출 증가 경고", "노출 증가" in rep_src)
    check("[45] AUC 임계 손대지 말 것", "AUC 임계" in rep_src)
    check("[45] 세 번째 불연속 경고", "세 번째 불연속" in rep_src)

    cal_src = open(os.path.join(_ROOT, "learning", "calibration.py"),
                   encoding="utf-8").read()
    check("calibration.py AND 사문 정정 존재", "사문" in cal_src)
    check("calibration.py 실측 근거(845건) 존재", "845" in cal_src)
    # 값 자체는 바뀌면 안 된다 — 바꾸면 conf 스케일에 세 번째 불연속이 생긴다
    from learning.calibration import PredictionCalibrator
    check("DEGENERATE_AUC_MIN 불변(0.53)",
          PredictionCalibrator.DEGENERATE_AUC_MIN == 0.53)
    check("DEGENERATE_SPAN_MIN 불변(0.02)",
          PredictionCalibrator.DEGENERATE_SPAN_MIN == 0.02)


def test_renders_in_report():
    """리포트 생성기에 두 채널이 배선돼 있는가 (요약표·상세·metrics)."""
    rep = _rep()
    check("[44] 평가함수 존재", hasattr(rep, "eval_dynmc_collapse_feed_watch"))
    check("[45] 평가함수 존재", hasattr(rep, "eval_cal_guard_flap_watch"))
    src = open(os.path.join(_ROOT, "scripts",
                            "generate_validation_campaign_report.py"),
               encoding="utf-8").read()
    check("요약표 [44] 행", "| [44] DynMC 붕괴행 잠식 |" in src)
    check("요약표 [45] 행", "| [45] 축퇴 가드 플래핑 (게이지) |" in src)
    check("상세 [44] 섹션", '"## [44] DynMC 붕괴행 잠식' in src)
    check("상세 [45] 섹션", '"## [45] 축퇴 가드 플래핑' in src)
    check("metrics 등록", '"dynmc_collapse_feed_watch": dcf' in src)
    check("metrics 불연속 기록", '"conf_scale_breaks_in_window"' in src)
    check("[39] 오염 표기 배선", "이 채널에 미치는 영향" in src)


def test_evaluators_run_without_crash():
    """실제 DB로 평가함수가 예외 없이 돈다 (표본 부족이어도 dict 반환)."""
    rep = _rep()
    for name in ("eval_dynmc_collapse_feed_watch", "eval_cal_guard_flap_watch"):
        try:
            out = getattr(rep, name)()
            ok = isinstance(out, dict) and "verdict" in out
            check("%s 정상 반환 (verdict=%s)" % (name, out.get("verdict")), ok)
        except Exception as e:
            check("%s 예외 없음 (%s)" % (name, e), False)
    # 게이지 채널은 판정하지 않는다 — verdict 는 항상 OBSERVE
    out45 = rep.eval_cal_guard_flap_watch()
    check("[45] verdict 는 OBSERVE 고정", out45.get("verdict") == "OBSERVE")


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 430차] conf 스케일 불연속 + [44] DynMC 잠식 + [45] 가드 플래핑")
    print("=" * 72)
    for fn in (
        test_registry_shape,
        test_window_detection,
        test_base_mc_parity_with_live,
        test_channel_44_fires_on_synthetic,
        test_channel_45_passthru_detection,
        test_channel_thresholds_registered,
        test_safety_wording_present,
        test_renders_in_report,
        test_evaluators_run_without_crash,
    ):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if FAILURES:
        print("실패 %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  - %s" % f)
        sys.exit(1)
    print("전부 통과")
