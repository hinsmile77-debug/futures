# -*- coding: utf-8 -*-
"""[MW0602 548차 후속] 0909 리포트 고도화 3건(G-1·G-2·G-3)의 관측 채널 회귀 고정.

세 채널 모두 **관측 전용**이다 — 일일 점검 증거 수집기(`collect_evidence.py`)의
§12 고착 지표에만 붙고, 매매 엔진·게이트·수량·주문 경로에는 닿지 않는다.

고정하려는 것은 "표가 그려진다"가 아니라, 이 프로젝트가 반복해서 당한
**세 가지 거짓 안심**을 각 채널이 구조적으로 못 만들게 하는 것이다:

  ① **스로틀된 로그를 분모로 쓰기** (G-1·G-2)
     `[Model] … 극단 z-score N개 피처 감지` 는 호라이즌별 600초 스로틀이다
     (`model/multi_horizon_model.py`). 0909 실측으로 `scaler_events` 는 호라이즌당
     37분을 기록했는데 로그에 남은 것은 3분뿐이었다. 과소집계 방향이 항상
     "덜 튀었다" 쪽이라, 로그로 세면 진짜 미격리가 조용히 정상으로 분류된다.

  ② **폴백을 정상값으로 채우기** (G-3)
     `meta_gate_horizon` 은 457차가 잡아낸 영구 폴백('1m' 370/370)이었다.
     NULL 을 '1m' 으로 coalesce 하면 그 폴백이 되살아나 **엉뚱한 호라이즌의
     예측과 비교**하게 된다(계측 4원칙 ④).

  ③ **미측정을 0/정상으로 세기** (G-2)
     DB 에 못 붙은 날을 `무발생` 으로 세면, 계측이 배선되기도 전에 안심이 만들어진다
     (FP-CRITICAL 이 2개월간 PSI=0.0 이었던 그 형태 — 계측 4원칙 ②).
"""
import datetime
import importlib.util
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ⚠ conftest 는 pytest 경로만 덮는다. `python tests/test_x.py` 직접 실행 대비 두 겹 방어
#   (tests/conftest.py 규약 — 새 테스트에 함께 넣을 것).
from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

# 🔴 이 파일은 `sys.stdout` 을 다시 묶지 않는다 — 의도된 것이다.
#    28개 테스트 파일이 import 시점에 `sys.stdout = io.TextIOWrapper(...)` 로
#    pytest 의 캡처 스트림을 감싸고 있고, 그 탓에 **전체 스위트 실행이 통째로
#    불가능**하다(`ValueError: I/O operation on closed file` — 한 파일씩은 통과).
#    새 파일이 그 관행을 따라가면 안 된다. 상세는 0909 자동조치 보고 `O-77`.

_SCRIPT = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check",
                       "scripts", "collect_evidence.py")

_G1 = "개장첫5분_극단피처"
_G2 = "극단z_격리대조"
_G3 = "앙상블_단일호라이즌_방향대조"


def _load():
    """수집기를 모듈로 적재한다 (scripts/ 는 패키지가 아니다)."""
    spec = importlib.util.spec_from_file_location("_ce_548", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ce():
    if not os.path.exists(_SCRIPT):
        pytest.skip("수집기 없음: %s" % _SCRIPT)
    return _load()


# ── T1. 세 채널이 등록돼 있는가 ─────────────────────────────────────────────
def test_t1_channels_registered(ce):
    dbs = ce.DEFAULT_CONFIG["db_indicators"]["sources"]
    dvs = ce.DEFAULT_CONFIG["derived_indicators"]["indicators"]
    assert _G1 in dbs, "G-1 채널이 db_indicators 에서 사라졌다"
    assert _G3 in dbs, "G-3(O-76) 채널이 db_indicators 에서 사라졌다"
    assert _G2 in dvs, "G-2 채널이 derived_indicators 에서 사라졌다"
    # `why` 는 렌더에 그대로 실린다 — 비면 다음 세션이 근거 없이 읽는다.
    for spec in (dbs[_G1], dbs[_G3], dvs[_G2]):
        assert (spec.get("why") or "").strip(), "why 가 비었다"
        assert spec.get("measured_since"), "measured_since 가 없다(계측 4원칙 ②)"


# ── T2. G-3: `meta_gate_horizon` 폴백을 되살리지 마라 (계측 4원칙 ④) ────────
def test_t2_g3_must_not_coalesce_meta_gate_horizon(ce):
    """NULL→'1m' 로 채우면 457차가 잡아낸 영구 폴백이 그대로 되살아난다."""
    sql = ce.DEFAULT_CONFIG["db_indicators"]["sources"][_G3]["sql"]
    flat = " ".join(sql.split()).lower()
    assert "coalesce" not in flat and "ifnull" not in flat, (
        "meta_gate_horizon 을 coalesce/ifnull 로 채우면 폴백이 정상값으로 위장한다. "
        "NULL 은 `미측정(hz없음)` 으로 분리해 남길 것")
    assert "미측정(hz없음)" in sql, "NULL 호라이즌을 미측정으로 분리하는 분기가 사라졌다"
    assert "미측정(예측없음)" in sql, "예측 행 부재를 미측정으로 분리하는 분기가 사라졌다"


def test_t2b_g3_measured_since_is_fallback_release_date(ce):
    """2026-08-12 = `meta_gate_horizon` 이 '1m' 아닌 값을 처음 낸 날(DB 실측).

    이 날짜를 앞당기면 폴백 구간이 표본에 섞여 **엉뚱한 호라이즌과 대조**한다.
    """
    spec = ce.DEFAULT_CONFIG["db_indicators"]["sources"][_G3]
    assert spec["measured_since"] == "2026-08-12"


def test_t2c_g3_counts_entries_not_exit_legs(ce):
    """표본 단위는 **진입 1건**이다(청산 레그 아님 — 계측 4원칙 ①, 417차)."""
    sql = " ".join(
        ce.DEFAULT_CONFIG["db_indicators"]["sources"][_G3]["sql"].split()).lower()
    assert "entry_executed = 1" in sql or "entry_executed=1" in sql
    assert "trades" not in sql, "trades(청산 레그) 를 세면 단위가 뒤섞인다"


# ── T3. G-1: 분당 호라이즌 6행을 접었는가 (계측 4원칙 ①) ────────────────────
def test_t3_g1_dedups_horizon_rows_per_minute(ce):
    """접지 않으면 한 사건이 6표본이 된다 — 레그/포지션 함정과 같은 형태."""
    spec = ce.DEFAULT_CONFIG["db_indicators"]["sources"][_G1]
    flat = " ".join(spec["sql"].split()).lower()
    assert "group by ts" in flat, "group by ts 가 빠지면 분당 6표본으로 부풀려진다"
    assert "scaler_events" in flat, "원천이 scaler_events 가 아니다"
    # 🔴 로그가 아니라 DB 여야 한다 — 로그는 600초 스로틀이다.
    assert spec["db"].endswith("scaler_monitor.db")
    # benign 이 붙으면 "한 피처 100% 고착"이 적신호에서 빠진다 = 찾으려던 것을 놓친다.
    assert not spec.get("benign"), "G-1 은 고착 자체가 발견이라 benign 을 두면 안 된다"


def test_t3b_g1_scoped_to_opening_window(ce):
    """G-1 의 질문은 「**개장 첫 5분**에 항상 튀는 피처가 있나」 다."""
    flat = " ".join(
        ce.DEFAULT_CONFIG["db_indicators"]["sources"][_G1]["sql"].split())
    assert "'09:00'" in flat and "'09:04'" in flat


# ── T4. 새 SQL 은 전부 읽기 전용이어야 한다 ─────────────────────────────────
def test_t4_new_sql_is_read_only(ce):
    """수집기는 증거를 **읽기만** 한다. 쓰기 구문이 섞이면 라이브 DB가 위험하다."""
    banned = ("insert", "update ", "delete", "drop", "alter", "create",
              "replace into", "attach", "pragma ")
    for name in (_G1, _G3):
        flat = " ".join(
            ce.DEFAULT_CONFIG["db_indicators"]["sources"][name]["sql"].split()).lower()
        assert flat.lstrip().startswith("select"), "%s: SELECT 로 시작하지 않는다" % name
        for kw in banned:
            assert kw not in flat, "%s: 쓰기 구문 %r" % (name, kw)


# ── T5. G-2 kind 가 배선돼 있는가 ───────────────────────────────────────────
def test_t5_g2_kind_is_wired(ce):
    """`kind` 오타는 조용히 `무기록` 행이 되어 늑대소년을 만든다."""
    assert ce.DEFAULT_CONFIG["derived_indicators"]["indicators"][_G2]["kind"] \
        == "automask_coverage"
    src = io.open(_SCRIPT, encoding="utf-8").read()
    assert '"automask_coverage": _kind_automask_coverage' in src, \
        "_KINDS 에 등록되지 않았다 — 등록 없이는 `무기록` 만 찍힌다"


# ── G-2 동작 시험용 합성 환경 ───────────────────────────────────────────────
def _mk_root(tmp_path, log_lines_by_day):
    """logs/<YYYYMMDD>_SIGNAL.log 만 있는 최소 리포 루트."""
    root = str(tmp_path)
    os.makedirs(os.path.join(root, "logs"))
    for day, lines in log_lines_by_day.items():
        p = os.path.join(root, "logs", "%s_SIGNAL.log" % day)
        with io.open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    return root


def _cfg_g2_only(ce):
    import copy
    cfg = copy.deepcopy(ce.DEFAULT_CONFIG)
    only = cfg["derived_indicators"]["indicators"][_G2]
    cfg["derived_indicators"]["indicators"] = {_G2: only}
    # 합성 표본은 3일뿐이라 판정 문턱을 낮춘다(값 자체가 아니라 분류를 본다).
    cfg["derived_indicators"]["min_samples"] = 1
    cfg["derived_indicators"]["min_days"] = 1
    return cfg


def _run_g2(ce, root, cfg, day, db_stub):
    """`db_rows` 를 합성 응답으로 갈아끼우고 G-2 한 채널만 돌린다."""
    orig = ce.db_rows
    ce.db_rows = db_stub
    try:
        rows = ce.scan_derived_indicators(root, cfg, day)
    finally:
        ce.db_rows = orig
    return {r["name"]: r for r in rows}[_G2]


def _stub(spikes, ran_days):
    """spikes: [(date, HH, MM, extreme_count)] / ran_days: [date]"""
    def _db_rows(root, rel, sql, params=(), timeout=3.0):
        if "distinct date" in sql:
            return [(d,) for d in ran_days]
        return spikes
    return _db_rows


# ── T6. G-2: DB 미접속은 `무발생` 이 아니라 미측정이다 (계측 4원칙 ②) ───────
def test_t6_g2_db_failure_is_unmeasured_not_clean(ce, tmp_path):
    day = datetime.date(2026, 9, 9)
    root = _mk_root(tmp_path, {"20260909": ["2026-09-09 09:00:00 [INFO] SIGNAL: hi"]})

    def _fail(*a, **k):
        return None

    row = _run_g2(ce, root, _cfg_g2_only(ce), day, _fail)
    assert row["n"] == 0, "DB 미접속인데 표본이 잡혔다 — 미측정이 값으로 샜다"
    assert all(v != "무발생" for v, _ in row["dist"]), \
        "DB 미접속을 `무발생` 으로 세면 거짓 안심이 된다"


# ── T7. G-2: N≥3 인데 격리 안 된 분이 있으면 확인대상으로 올라온다 ──────────
def test_t7_g2_flags_unmasked_spike_minute(ce, tmp_path):
    """이 채널이 실제로 **판별**하는지 — 늘 `격리` 만 내면 죽은 게이트다."""
    day = datetime.date(2026, 9, 9)
    root = _mk_root(tmp_path, {"20260909": [
        "2026-09-09 09:00:57 [WARNING] SIGNAL: [Model] 1m 극단 z-score 3개 피처 감지",
        # `[AutoMasked]` 없음 — 튀었는데 격리되지 않았다
    ]})
    stub = _stub([("2026-09-09", "09", "00", 3)], ["2026-09-09"])
    row = _run_g2(ce, root, _cfg_g2_only(ce), day, stub)
    assert row["dist"] == [("비격리(N≥3·확인대상)", 1)], row["dist"]


def test_t8_g2_same_minute_mask_counts_as_isolated(ce, tmp_path):
    day = datetime.date(2026, 9, 9)
    root = _mk_root(tmp_path, {"20260909": [
        "2026-09-09 09:00:57 [INFO] SIGNAL: [AutoMasked] 이상값 3개 즉시 격리 예측 "
        "(CORE 제외): ['institution_futures_net']",
    ]})
    stub = _stub([("2026-09-09", "09", "00", 3)], ["2026-09-09"])
    row = _run_g2(ce, root, _cfg_g2_only(ce), day, stub)
    assert row["dist"] == [("격리", 1)], row["dist"]


def test_t9_g2_next_minute_mask_still_counts(ce, tmp_path):
    """로그는 `09:00:57`, DB 는 `09:00:00` — +1분 허용이 사라지면 오탐이 쏟아진다."""
    day = datetime.date(2026, 9, 9)
    root = _mk_root(tmp_path, {"20260909": [
        "2026-09-09 09:01:03 [INFO] SIGNAL: [AutoMasked] 이상값 3개 즉시 격리 예측",
    ]})
    stub = _stub([("2026-09-09", "09", "00", 3)], ["2026-09-09"])
    row = _run_g2(ce, root, _cfg_g2_only(ce), day, stub)
    assert row["dist"] == [("격리", 1)], row["dist"]


# ── T10. G-2: 가동했으나 극단 0건인 날은 `무발생`(값)이다 ───────────────────
def test_t10_g2_ran_but_no_spike_is_a_value(ce, tmp_path):
    """가동일인데 극단 0건 = `무발생`. 미가동일(휴장)과 구분돼야 한다."""
    day = datetime.date(2026, 9, 9)
    root = _mk_root(tmp_path, {"20260909": ["2026-09-09 09:00:00 [INFO] SIGNAL: hi"]})
    stub = _stub([], ["2026-09-09"])          # 가동했고, 극단은 0건
    row = _run_g2(ce, root, _cfg_g2_only(ce), day, stub)
    assert row["dist"] == [("무발생", 1)], row["dist"]


def test_t11_g2_non_running_day_is_not_a_sample(ce, tmp_path):
    """scaler_events 가 아예 안 돈 날은 표본이 아니다(미측정)."""
    day = datetime.date(2026, 9, 9)
    root = _mk_root(tmp_path, {"20260909": ["2026-09-09 09:00:00 [INFO] SIGNAL: hi"]})
    stub = _stub([], [])                       # 가동 기록 자체가 없다
    row = _run_g2(ce, root, _cfg_g2_only(ce), day, stub)
    assert row["n"] == 0, "미가동일이 표본으로 세어졌다"


# ── T12. G-2: 다른 날 로그의 `[AutoMasked]` 가 오늘 격리로 새지 않는가 ──────
def test_t12_g2_does_not_borrow_other_days_mask(ce, tmp_path):
    day = datetime.date(2026, 9, 9)
    root = _mk_root(tmp_path, {"20260909": [
        # 파일은 09-09 자인데 줄의 날짜는 09-08 — 날짜 대조가 없으면 격리로 샌다
        "2026-09-08 09:00:57 [INFO] SIGNAL: [AutoMasked] 이상값 3개 즉시 격리 예측",
    ]})
    stub = _stub([("2026-09-09", "09", "00", 3)], ["2026-09-09"])
    row = _run_g2(ce, root, _cfg_g2_only(ce), day, stub)
    assert row["dist"] == [("비격리(N≥3·확인대상)", 1)], row["dist"]


# ── T14. G-2: N<3 미격리는 확인대상이 아니다 (늑대소년 방지) ────────────────
def test_t14_g2_sub_threshold_spike_is_not_actionable(ce, tmp_path):
    """AutoMask 는 union ≥ 3 에서만 돈다 — N<3 미격리는 **구조상 정상**이다.

    이것을 확인대상으로 올리면 튀기만 하면 매일 적신호가 떠서 채널이 무시된다.
    """
    day = datetime.date(2026, 9, 9)
    root = _mk_root(tmp_path, {"20260909": [
        "2026-09-09 09:11:57 [WARNING] SIGNAL: [Model] 1m 극단 z-score 2개 피처 감지",
    ]})
    stub = _stub([("2026-09-09", "09", "11", 2)], ["2026-09-09"])
    row = _run_g2(ce, root, _cfg_g2_only(ce), day, stub)
    assert row["dist"] == [("비격리(N<3)", 1)], row["dist"]


def test_t15_g2_worst_minute_decides_the_day(ce, tmp_path):
    """하루 값은 **가장 나쁜 분**이 정한다.

    "그날 `[AutoMasked]` 가 한 번이라도 찍혔나"로 보면, 스무 분이 튀었는데 한 분만
    격리된 날도 `격리` 가 된다 — 이 프로젝트가 반복해서 당한 거짓 안심의 형태다.
    """
    day = datetime.date(2026, 9, 9)
    root = _mk_root(tmp_path, {"20260909": [
        "2026-09-09 09:00:57 [INFO] SIGNAL: [AutoMasked] 이상값 3개 즉시 격리 예측",
        # 09:30 은 N=4 로 튀었는데 격리 줄이 없다
    ]})
    stub = _stub([("2026-09-09", "09", "00", 3),
                  ("2026-09-09", "09", "30", 4)], ["2026-09-09"])
    row = _run_g2(ce, root, _cfg_g2_only(ce), day, stub)
    assert row["dist"] == [("비격리(N≥3·확인대상)", 1)], row["dist"]


# ── T13. G-2 benign 목록 — `확인대상` 만 적신호로 남는다 ────────────────────
def test_t13_g2_benign_keeps_only_the_actionable_class(ce):
    benign = ce.DEFAULT_CONFIG["derived_indicators"]["indicators"][_G2]["benign"]
    assert "비격리(N≥3·확인대상)" not in benign, \
        "확인대상이 benign 이면 이 채널은 아무것도 올리지 못한다"
    for expected in ("무발생", "격리", "비격리(N<3)"):
        assert expected in benign, "%s 이 benign 에서 빠지면 매일 적신호가 뜬다" % expected
