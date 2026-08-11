"""[MW0602 462차 P1~P4] 존 진입금지 섀도 · 실효 min_conf 계측 · 자기유발 지연 차감 회귀 테스트.

지키려는 불변식 — **라이브 진입 경로는 이번 배포에서 바뀌지 않는다.**
새 플래그가 전부 기본값일 때 진입 판정·차단 사유·사이징이 종전과 완전히 동일해야
하고, 추가되는 것은 계측(로그·DB 컬럼)뿐이다.

세부:
  P1-a  `ZONE_ENTRY_BAN_ENFORCE`가 False(기본)면 `_final_entry_ok`가 불변.
        True로 켜야만 금지 존에서 차단되고 그때만 전용 차단사유가 나온다.
  P1-b  `min_conf_effective`가 두 INSERT 컬럼목록·마이그레이션에 모두 등록됐고,
        TrendGate 완화가 있을 때 `min_conf`와 **다른 값**이 기록된다.
  P2    모델 교체 소요시간은 판정용 지연에서 빠지고 원값은 로그에 남는다.
  P3    mc 도달불가 조기경보는 p95 < 실효 mc 일 때만, 당일 1회만, 진입허용 존에서만.
  P4    신설 채널 3종이 등록됐고, [36] C→C 분해가 **판정 게이트보다 앞에서** 계산된다.

실행: python tests/test_462_zone_ban_and_latency.py   (COM/브로커/DB 불필요)
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


# ══════════════════════════════════════════════════════════════
# P1-a — 존 진입금지 섀도/집행
# ══════════════════════════════════════════════════════════════
def test_p1a_defaults_are_live_neutral():
    """기본값에서 라이브 무변경 — 집행 OFF, 섀도 ON."""
    check("ZONE_ENTRY_BAN_ENFORCE 기본 False (라이브 무변경)",
          getattr(S, "ZONE_ENTRY_BAN_ENFORCE", None) is False)
    check("ZONE_ENTRY_BAN_SHADOW_ENABLED 기본 True (계측은 항상)",
          getattr(S, "ZONE_ENTRY_BAN_SHADOW_ENABLED", None) is True)


def test_p1a_zone_flags_intact():
    """존 정의는 이번 배포에서 손대지 않는다 — 집행 결정 전까지 무변경."""
    from strategy.entry.time_strategy_router import _ZONE_PARAMS, is_entry_zone
    for z in ("OTHER", "EXIT_ONLY", "PRE_MARKET"):
        check("%s는 여전히 allow_new_entry=False" % z,
              _ZONE_PARAMS[z]["allow_new_entry"] is False)
    for z in ("STABLE_TREND", "LUNCH_RECOVERY", "OPEN_VOLATILE",
              "GAP_OPEN", "CLOSE_VOLATILE"):
        check("%s는 진입 허용 존" % z, is_entry_zone(z) is True)
    check("미정의 zone은 OTHER 기준(금지)로 폴백",
          is_entry_zone("NO_SUCH_ZONE") is False)


def test_p1a_enforcement_is_flag_gated_in_source():
    """집행이 플래그 뒤에 있고, 차단사유가 우선순위 체인 맨 앞에 있다."""
    src = _read("main.py")
    check("집행이 ZONE_ENTRY_BAN_ENFORCE 게이트 뒤에 있음",
          re.search(r'ZONE_ENTRY_BAN_ENFORCE"?,\s*False\)\s*and not _zone_entry_allowed:\s*\n\s*_final_entry_ok = False', src) is not None)
    check("섀도 위반 로그 [ZoneBanShadow] 존재", "[ZoneBanShadow]" in src)
    check("집행 시 전용 차단사유가 존재", "신규 진입 금지 구간" in src
          and "462차 집행" in src)
    # `_zone_entry_allowed`는 조건분기 밖에서 초기화돼야 UnboundLocalError가 없다(400차 교훈)
    check("_zone_entry_allowed가 무조건 초기화됨",
          re.search(r'^\s{8}_zone_entry_allowed = True$', src, re.M) is not None)


# ══════════════════════════════════════════════════════════════
# P1-b — 실효 min_conf 계측
# ══════════════════════════════════════════════════════════════
def test_p1b_column_registered_everywhere():
    """세 곳(마이그레이션·INSERT×2)에 모두 등록돼야 한다 — 한 곳만 빠지면 조용히 NULL."""
    check('마이그레이션에 "min_conf_effective": "REAL" 등록',
          '"min_conf_effective": "REAL"' in _read("utils/db_utils.py"))
    pb = _read("learning/prediction_buffer.py")
    col_lists = re.findall(r"INSERT OR IGNORE INTO ensemble_decisions \((.*?)\)\s*VALUES",
                           pb, re.S)
    check("min_conf_effective가 두 INSERT 컬럼목록 모두에 있음",
          len(col_lists) == 2 and all("min_conf_effective" in c for c in col_lists))
    # 플레이스홀더 개수 == 컬럼 개수 (461차가 이 짝을 깨뜨릴 뻔한 자리)
    for i, m in enumerate(re.finditer(
            r"INSERT OR IGNORE INTO ensemble_decisions \((.*?)\)\s*VALUES\s*\((.*?)\)",
            pb, re.S)):
        ncol = len([c for c in m.group(1).split(",") if c.strip()])
        nph = m.group(2).count("?")
        check("INSERT#%d 컬럼수(%d) == 플레이스홀더수(%d)" % (i + 1, ncol, nph),
              ncol == nph)


def test_p1b_decision_key_written():
    src = _read("main.py")
    check("decision['min_conf_effective']에 _checklist_min_conf 대입",
          'decision["min_conf_effective"] = float(_checklist_min_conf)' in src)
    check("_checklist_min_conf가 조건분기 밖에서 초기화됨 (400차 교훈)",
          re.search(r'^\s{8}_checklist_min_conf = actual_min_conf$', src, re.M) is not None)


def test_p1b_null_semantics():
    """키 부재는 NULL — 0.0으로 승격하면 '완화 없음'과 '구버전 행'이 섞인다."""
    pb = _read("learning/prediction_buffer.py")
    n = len(re.findall(
        r'None if decision\.get\("min_conf_effective"\) is None', pb))
    check("두 저장 경로 모두 NULL 폴백 사용 (0.0 승격 금지)", n == 2)


# ══════════════════════════════════════════════════════════════
# P2 — 자기유발 지연 차감
# ══════════════════════════════════════════════════════════════
def test_p2_default_and_subtraction():
    check("PIPE_LATENCY_EXCLUDE_MODEL_SWAP 기본 True",
          getattr(S, "PIPE_LATENCY_EXCLUDE_MODEL_SWAP", None) is True)
    src = _read("main.py")
    check("사이클마다 _model_swap_ms를 0으로 리셋 (직전값 누수 방지)",
          re.search(r"^\s+self\._model_swap_ms = 0\.0$", src, re.M) is not None)
    check("모델 교체 구간을 perf_counter로 계측",
          "_swap_t0 = time.perf_counter()" in src
          and "self._model_swap_ms = (time.perf_counter() - _swap_t0) * 1000.0" in src)
    check("판정용 지연에서 차감 (원값은 _pipe_ms_raw로 보존)",
          "_pipe_ms = max(0.0, _pipe_ms_raw - _swap_ms)" in src)
    check("차감분이 로그에 raw와 함께 남음",
          "모델교체" in src and "raw=" in src)


def test_p2_subtraction_math():
    """차감식이 음수로 내려가지 않고, 스왑이 없으면 원값 그대로여야 한다."""
    def adjust(raw, swap, enabled=True):
        if swap > 0.0 and enabled:
            return max(0.0, raw - swap)
        return raw
    check("스왑 없음 → 원값 유지", adjust(3070.0, 0.0) == 3070.0)
    # 2026-08-11 10:00 실측: total 3070ms 중 S0 2817ms가 모델 교체
    check("실측 재현: 3070 - 2817 = 253ms → CB⑤(1000ms) 미발동",
          abs(adjust(3070.0, 2817.0) - 253.0) < 1e-6 and adjust(3070.0, 2817.0) < 1000.0)
    check("차감이 음수로 내려가지 않음", adjust(100.0, 500.0) == 0.0)
    check("플래그 OFF면 차감하지 않음", adjust(3070.0, 2817.0, False) == 3070.0)


# ══════════════════════════════════════════════════════════════
# P3 — mc 도달불가 조기경보
# ══════════════════════════════════════════════════════════════
def test_p3_settings():
    check("MC_UNREACHABLE_ALERT_ENABLED 기본 True",
          getattr(S, "MC_UNREACHABLE_ALERT_ENABLED", None) is True)
    check("경보 시각이 09:30 (EOD 15:40보다 앞)",
          str(getattr(S, "MC_UNREACHABLE_ALERT_AFTER", "")) == "09:30")
    check("min_samples >= 20 (소표본 오경보 방지)",
          int(getattr(S, "MC_UNREACHABLE_MIN_SAMPLES", 0)) >= 20)
    check("분위 0.90~0.99 범위",
          0.90 <= float(getattr(S, "MC_UNREACHABLE_PERCENTILE", 0)) <= 0.99)


def _p95(vals, pct=0.95):
    s = sorted(vals)
    return s[min(len(s) - 1, int(round(pct * (len(s) - 1))))]


def test_p3_judgment_reproduces_0811():
    """0811 실측 재현 — conf 최대 0.4522 vs 실효 mc 0.4464 → 도달불가."""
    # 0811 비붕괴 conf 분포의 성격을 모사 (p95가 mc 아래)
    confs = [0.30 + 0.0007 * i for i in range(200)]     # 0.300~0.4393
    check("p95가 mc 아래면 도달불가 판정", _p95(confs) < 0.4464)
    confs_ok = confs + [0.50, 0.52, 0.55] * 10
    check("p95가 mc 위면 경보 안 냄", _p95(confs_ok) >= 0.4464)


def test_p3_guards_in_source():
    src = _read("main.py")
    check("당일 1회 경보 (매분 반복 방지)", "self._mcu_alerted = True" in src)
    check("진입금지 존은 표본에서 제외 (404차 후속4 오탐 재발 방지)",
          "if not zone_allows_entry:" in src)
    check("붕괴행 제외 (461차 인위값이 p95를 끌어올림)",
          "if not collapsed and confidence is not None:" in src)
    check("실효 mc로 판정 (기록용 min_conf 아님)",
          "_check_mc_unreachable(" in src and "_checklist_min_conf," in src)
    check("자동 조정 없음 — 경보 문구에 명시",
          "mc는 자동 조정하지 않음" in src)


# ══════════════════════════════════════════════════════════════
# P4 — 캠페인 채널
# ══════════════════════════════════════════════════════════════
def test_p4_channels_registered():
    vc = S.VALIDATION_CAMPAIGN
    for key in ("profit_geometry_lowvol_watch", "effective_weight_watch",
                "zone_ban_breach_watch"):
        check("VALIDATION_CAMPAIGN에 %s 등록" % key, key in vc)
    check("[51] min_days >= 10 (313차 일자단위 검정력)",
          int(vc["profit_geometry_lowvol_watch"]["min_days"]) >= 10)
    check("[52] min_days >= 10", int(vc["effective_weight_watch"]["min_days"]) >= 10)
    check("[53] min_days >= 10", int(vc["zone_ban_breach_watch"]["min_days"]) >= 10)
    check("start_date 무변경 (§9-4 검증시계 리셋 금지)",
          vc.get("start_date") == "2026-07-05")


def test_p4_report_wired():
    rep = _read("scripts/generate_validation_campaign_report.py")
    for fn in ("eval_profit_geometry_lowvol_watch", "eval_effective_weight_watch",
               "eval_zone_ban_breach_watch"):
        check("%s 정의됨" % fn, ("def %s(" % fn) in rep)
    for key in ("profit_geometry_lowvol_watch", "effective_weight_watch",
                "zone_ban_breach_watch"):
        check("metrics dict에 %s 포함" % key, ('"%s":' % key) in rep)
    for n in (51, 52, 53):
        check("요약표에 [%d] 행 존재" % n, ("_row_462(%d," % n) in rep)


def test_p4_grade_path_decompose_before_gates():
    """[36] C→C 분해는 판정 게이트보다 **앞**에 있어야 한다.

    뒤에 두면 X→A가 min_samples(20)에 도달할 때까지 영영 계산되지 않는다 —
    462차 초안이 실제로 그 실수를 했고 리포트에 promotion_effect=None으로 찍혔다.
    """
    rep = _read("scripts/generate_validation_campaign_report.py")
    body = rep.split("def eval_grade_x_promotion(")[1].split("\ndef ")[0]
    i_dec = body.find("promotion_effect_krw")
    i_gate = body.find("경로 표본 부족")
    check("C→A/C→C 분해가 함수에 존재", i_dec > 0)
    check("분해가 min_samples 게이트보다 앞에 위치", 0 < i_dec < i_gate)
    check("C→C 표본 없으면 None (0으로 단정 금지)",
          'out["promotion_effect_krw"] = None' in body)


def test_p4_no_duplicate_raw_grade_channel():
    """raw_grade_cohort_watch를 신설하지 않았는지 — [36]과 중복 금지."""
    check("raw_grade_cohort_watch 미신설 ([36]으로 흡수)",
          "raw_grade_cohort_watch" not in S.VALIDATION_CAMPAIGN)


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
    print("462차 회귀 테스트 전부 통과")
