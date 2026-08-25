# -*- coding: utf-8 -*-
"""[MW0602 494차] F-6 · F-7 · F-9 · F-2 · G-1 · G-2 회귀 — 관측 위생.

여섯 건 모두 **계측이 조용히 죽는 것**을 막는 작업이라 한 파일에 묶는다.
고정하는 불변식:

  F-6 도전자 섀도가 파일에 남는가 + **무조건 상태 샘플**인가
      (종전 `>5ms` 조건부는 100% `SLOW` 고착이 구조적으로 보장돼 §12 감시가 불가능하다)
      + 🔴 그 WARNING 이 `exceptions_10m` 을 밀어 **Degraded Mode 를 오발동시키지
      않는가** — 304·307·402차가 세 번 겪은 사고이며, 계측이 매매를 막으면 안 된다.
  F-7 관측 ID 채번 — git 대조로 **오탐 없이** 충돌만 잡는가
  F-9 크래시 계수의 분자 — 정상 종료를 세지 않는가
  F-2 런처 GUARD 발화의 **부재**를 셀 수 있는가(줄 단위 스캐너로는 불가)
  G-1 장전 축퇴가 개장에 풀렸는가(두 시점 대비)
  G-2 보정기 폴백의 **사유 축**

실행:
    python tests/test_494_observability_hygiene.py
"""
import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL = os.path.join(".claude", "skills", "mireuk-daily-check")
_COLLECTOR = os.path.join(_SKILL, "scripts", "collect_evidence.py")
FAILURES = []


def _read(rel):
    with io.open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _collector():
    """수집기를 모듈로 로드한다(표준 라이브러리만 쓰므로 어느 env 에서든 뜬다)."""
    import importlib.util
    p = os.path.join(_ROOT, _COLLECTOR)
    spec = importlib.util.spec_from_file_location("collect_evidence_494", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ─────────────────────────────────────────────────────────────────────── F-6
def test_challenger_logs_reach_a_file_layer():
    """`getLogger("CHALLENGER")` 는 어떤 파일 핸들러에도 붙어 있지 않다 —
    관측용 출력은 레이어 로거로 나가야 한다."""
    src = _read(os.path.join("challenger", "challenger_engine.py"))
    assert '_obs = logging.getLogger("SYSTEM")' in src
    for must in ('_obs.info(\n                "[Engine] shadow state=%s',
                 '_obs.warning("[Engine] run_shadow %.1fms',
                 '_obs.error("[Engine] run_shadow 예외'):
        assert must in src, must

    from utils.logger import _ALL_LAYERS
    assert "CHALLENGER" not in _ALL_LAYERS, \
        "CHALLENGER 가 레이어가 됐다면 이 우회는 불필요해진다 — 주석을 갱신할 것"
    assert "SYSTEM" in _ALL_LAYERS


def test_shadow_state_sample_is_unconditional():
    """상태 토큰은 `if elapsed_ms >` **밖**에 있어야 한다."""
    src = _read(os.path.join("challenger", "challenger_engine.py"))
    i_state = src.find('"[Engine] shadow state=%s')
    i_guard = src.find("if elapsed_ms > SHADOW_WARN_MS:", src.find("finally:"))
    assert i_state > 0 and i_guard > 0
    assert i_state < i_guard, "상태 샘플이 조건문 안으로 들어갔다 — SLOW 고착이 보장된다"


def test_engine_tag_excluded_from_exception_density():
    """🔴 계측을 켜는 것이 매매를 막아서는 안 된다.

    SYSTEM 레이어의 WARNING 이상은 `exceptions_10m` 로 집계돼 Degraded Mode
    (자동진입 conf 62% 요구)를 발동시킨다. `[Engine]` 경보는 0825 실측 369건/일
    (약 1분당 1건)이라 10분 창에 ~10건이 더해져 임계 12를 상시 압박한다.
    """
    from config.settings import HEALTH_EXCEPTION_EXCLUDE_TAGS
    assert "[Engine]" in HEALTH_EXCEPTION_EXCLUDE_TAGS


def test_blockreq_reentrant_is_info_not_warning():
    """같은 이유로 BlockRequest 재진입 통지도 INFO 다 — 빈도는 SAMPLE 줄이 나른다."""
    src = _read(os.path.join("collection", "cybos", "api_connector.py"))
    i = src.find("if _br_reentrant:")
    block = src[i:i + 900]
    assert "_obs.info(" in block, "재진입 통지가 WARNING 이면 Degraded 오발동 위험"
    assert "_obs.warning(" not in block


# ─────────────────────────────────────────────────────────────────────── F-7
def test_obs_label_lint_has_no_false_positives_on_live_file():
    """🔴 이 린트의 첫 초안은 실파일에서 오탐 15건을 냈다.

    `NEXT_TODO.md` 는 같은 관측을 매일 다른 문구로 다시 싣는 누적 로그다 —
    문구 차이가 곧 대상 차이가 아니다. 지금 구현은 **git 대조**만 쓴다.
    """
    m = _collector()
    out = m.scan_obs_labels(_ROOT)
    assert out.get("max") and out.get("next") == out["max"] + 1
    assert out["collisions"] == [], "실파일에서 충돌 오탐: %r" % (out["collisions"],)


def test_obs_label_lint_detects_a_real_collision():
    """직전 커밋 최댓값 이하 번호가 새로 등장하면 잡는다."""
    m = _collector()
    prev = "- [ ] **O-5** 어떤 관측\n- [ ] **O-23** 다른 관측\n"
    cur = prev + "- [ ] **O-16(493차)** 새로 발급한 번호\n"
    prev_ids, now_ids = m._obs_ids(prev), m._obs_ids(cur)
    new = sorted(now_ids - prev_ids)
    assert new == [16]
    assert [n for n in new if n <= max(prev_ids)] == [16], "충돌이 잡혀야 한다"

    cur_ok = prev + "- [ ] **O-24(494차)** 규칙대로 발급\n"
    new_ok = sorted(m._obs_ids(cur_ok) - prev_ids)
    assert [n for n in new_ok if n <= max(prev_ids)] == []


def test_whitelist_keeps_issued_three():
    """이미 발급된 3건은 재부여하지 않는다(소급 재라벨 = 미측정 구간 생성)."""
    m = _collector()
    assert set(m.OBS_LABEL_WHITELIST) == {"O-16", "O-17", "O-18"}


def test_numbering_rule_is_written_in_template():
    t = _read(os.path.join(_SKILL, "references", "report_template.md"))
    assert "관측 ID 채번 규칙" in t
    assert "현행 최댓값 다음 번호부터 발급한다" in t
    assert "재부여하지 않는다" in t


# ─────────────────────────────────────────────────────────────────────── F-9
def test_crash_numerator_is_pinned_and_false_source_is_banned():
    ev = _read(os.path.join(_SKILL, "references", "evidence_map.md"))
    assert "오탐 주의" in ev
    assert "일시적 크래시" in ev and "분자로 쓰지 말 것" in ev
    assert "정상 종료 감지" in ev

    src = _read(_COLLECTOR)
    i = src.find('"crash_signature"')
    assert i > 0
    block = src[i:i + 1400]
    assert "crash_signatures" in block
    assert "일시적 크래시" in block, "금지 원천이 왜 안 되는지 지표 자신이 알고 있어야 한다"


def test_missing_signature_file_is_unmeasured_not_zero():
    """🔴 파일이 없으면 `0(무사고)` 가 아니라 표본 없음이다."""
    m = _collector()
    src = _read(_COLLECTOR)
    i = src.find("def _kind_crash_signature")
    block = src[i:i + 1800]
    assert "__missing__" in block and "return None" in block
    assert "미측정" in block

    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "logs"))
        cfg = {"scan_dirs": ["logs"], "scan_depth": 2,
               "derived_indicators": {"lookback_days": 5, "indicators": {
                   "crash_signature": {"kind": "crash_signature",
                                       "benign": ["0(무사고)"]}}}}
        import datetime as _dt
        rows = m.scan_derived_indicators(d, cfg, _dt.date(2026, 8, 25))
        for r in rows:
            assert r["n"] == 0, "산출 파일이 없는데 표본이 생겼다: %r" % (r,)


# ────────────────────────────────────────────────────────────────── F-2 · G-1
def test_derived_indicators_registered():
    src = _read(_COLLECTOR)
    for name in ('"CORE축퇴_개장해소"', '"launcher_guard"', '"crash_signature"'):
        assert name in src, name
    i = src.find('"launcher_guard"')
    block = src[i:i + 1800]
    # 사전등록 임계 — 달력 기준이며 관측값 역산이 아니다(313차 ④)
    assert "5거래일 연속" in block and "10거래일" in block
    assert "benign 아님" in block


def test_core_degen_open_axis_distinguishes_resolved_and_not():
    """0824(해소) vs 0825(미해소) 를 실제로 가르는가 — 이 축을 만든 이유다."""
    import datetime as _dt
    m = _collector()
    cfg = {"scan_dirs": ["logs"], "scan_depth": 2, "exclude_patterns": [],
           "never_digest_patterns": [],
           "derived_indicators": {"lookback_days": 5, "min_samples": 1, "min_days": 1,
                                  "indicators": {"CORE축퇴_개장해소": {
                                      "kind": "core_degen_open",
                                      "files": ["_learning"],
                                      "benign": ["해소", "무축퇴"]}}}}
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "logs"))

        def _mk(day, warm, open_):
            p = os.path.join(d, "logs", "%s_LEARNING.log" % day)
            with io.open(p, "w", encoding="utf-8") as f:
                for n in warm:
                    f.write("2026-08-24 08:55:00 [INFO] LEARNING: "
                            "[CORE준비도] trigger=A_WARMUP 축퇴 %d/6 — x\n" % n)
                for n in open_:
                    f.write("2026-08-24 09:05:00 [INFO] LEARNING: "
                            "[CORE준비도] trigger=B_OPEN 축퇴 %d/6 — x\n" % n)

        _mk("20260824", [1], [0])      # 장전 축퇴 → 개장에 풀림
        _mk("20260825", [1], [1])      # 안 풀림
        _mk("20260821", [0], [0])      # 애초에 축퇴 없음
        rows = m.scan_derived_indicators(d, cfg, _dt.date(2026, 8, 25))
        dist = dict(rows[0]["dist"])
        assert dist == {"해소": 1, "미해소": 1, "무축퇴": 1}, dist


# ─────────────────────────────────────────────────────────────────────── G-2
def test_calibration_reason_axis_registered():
    src = _read(_COLLECTOR)
    i = src.find('"Calib_폴백사유"')
    assert i > 0
    block = src[i:i + 1600]
    for token in ("축퇴 감지", "축퇴 해소", "하한 도달불가", "도달불가 해소"):
        assert token in block, token
    # 🔴 임계 변경 금지선이 지표 자신에 적혀 있어야 한다
    assert "conf_floor" in block and "금지선" in block


def test_no_threshold_was_changed():
    """이 커밋 전체가 관측 전용 — 매매에 닿는 상수는 하나도 안 바꿨다."""
    s = _read(os.path.join("config", "settings.py"))
    assert "CB_CONSEC_STOP_LIMIT = 9999" in s
    assert "CB3_P4_GRADE_BLOCK_ENABLED = False" in s
    assert "FP_CRITICAL_GRADE_BLOCK_ENABLED = False" in s
    assert "TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED = False" in s
    assert "MAX_CONTRACTS = 3" in s
    c = _read(os.path.join("challenger", "challenger_engine.py"))
    assert "SHADOW_WARN_MS  = 5.0" in c, "경보 임계를 건드리면 시계열이 끊긴다"


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_challenger_logs_reach_a_file_layer,
               test_shadow_state_sample_is_unconditional,
               test_engine_tag_excluded_from_exception_density,
               test_blockreq_reentrant_is_info_not_warning,
               test_obs_label_lint_has_no_false_positives_on_live_file,
               test_obs_label_lint_detects_a_real_collision,
               test_whitelist_keeps_issued_three,
               test_numbering_rule_is_written_in_template,
               test_crash_numerator_is_pinned_and_false_source_is_banned,
               test_missing_signature_file_is_unmeasured_not_zero,
               test_derived_indicators_registered,
               test_core_degen_open_axis_distinguishes_resolved_and_not,
               test_calibration_reason_axis_registered,
               test_no_threshold_was_changed):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
