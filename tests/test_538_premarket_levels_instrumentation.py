# -*- coding: utf-8 -*-
"""[MW0602 538차] 당일 맥점 예측 — 계측 결함 5건 수정의 회귀 고정.

2026-09-07(월) 08:50 실산출을 점검하다 나온 것들이다. 산출 **값**은 하나도 바뀌지
않았고(그 불변식을 이 파일이 고정한다), 바뀐 것은 「무엇이 기록되는가」다.

  F-1  구조 채점을 **측면(상방·하방) 단위**로 센다. 534차는 한쪽 후보가 0개면
       반대쪽의 측정된 결과까지 버렸고, 그 조건이 갭 데이를 골라 탈락시켜
       **선택 편향**이 됐다(2026-09-07 실측 120행 중 12행 탈락, 그 안에서
       5적중/7미적중). 2026-09-07 08:50 자신이 그 경로였다(상방 후보 0개).
  F-2  이력 캐시 **신선도 경고**. 534차는 `prepare_params()` 가 `history_last` 를
       돌려주는데 **코드베이스 어디서도 읽지 않았다** — EOD 가 빠지면 전일 종가·
       전일 고저·ATR 이 통째로 하루 낡은 채 조용히 산출된다(계측 4원칙 ④).
  F-3  R̂ **원비·절단·외삽** 기록. 저장값 `rhat_scale` 은 절단 후라, 그날 구간폭을
       회귀가 정했는지 상수가 정했는지 사후에 셀 수 없었다.
  F-4  `RHAT_CAP` 주석의 "검증에서 닿은 적 없음"이 틀렸다(백필 실측 5회 도달).
  F-5  경고를 **변수 먼저 · 상수 마지막** 으로. 534차는 상수 1건이 항상 먼저 와
       「주의」 줄이 121행 전부 같은 문자열이었다(468차 G-2 고착 지표 계열).

Python 3.7.13 32-bit(py37_32)에서 돌아야 한다.
"""

import io
import math
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.levels import premarket_levels as PL
from features.levels import levels_store as LS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_OI_CONST = "옵션 OI 원천 없음(설계상 제외)"


def _iso_db(tmp_path, monkeypatch, name="pml.db"):
    from config import settings
    from utils import db_utils
    db = str(tmp_path / name)
    monkeypatch.setattr(settings, "PREMARKET_LEVELS_DB", db, raising=False)
    monkeypatch.setattr(db_utils, "PREMARKET_LEVELS_DB", db, raising=False)
    db_utils.init_premarket_levels_db()
    return db_utils, db


def _raw_db(tmp_path, days, name="raw.db"):
    """`raw_candles` 최소본 — 신선도 프로브(F-2)가 읽는 것은 `ts` 뿐이다."""
    p = str(tmp_path / name)
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, open REAL, high REAL,"
                " low REAL, close REAL, volume INTEGER)")
    for d in days:
        con.execute("INSERT INTO raw_candles VALUES (?,?,?,?,?,?)",
                    (d + " 08:45:00", 300.0, 300.0, 300.0, 300.0, 1))
    con.commit()
    con.close()
    return p


# ────────────────────────────────────────── F-3 · F-4  R̂ 진단

def _rhat_params():
    return dict(n=60, beta=[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0], med_r=1.0,
                x_lo=[1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                x_hi=[1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                x_names=list(PL.RHAT_X_NAMES))


def test_rhat_scale_value_is_unchanged_by_the_diagnostic_split():
    """🔴 진단을 붙였다고 **스케일 값이 달라지면 안 된다** — 이식의 전제다."""
    p = _rhat_params()
    for v in (-3.0, -0.5, 0.0, 0.3, 0.9, 3.0):
        x = [1.0, v, 0.0, 0.0, 0.0, 0.0, 0.0]
        expected = min(PL.RHAT_CAP, max(PL.RHAT_FLOOR, math.exp(v)))
        assert PL.rhat_scale(p, x) == expected
        assert PL.rhat_diag(p, x)["scale"] == expected


def test_rhat_scale_still_returns_none_without_params():
    assert PL.rhat_scale(None, [1.0]) is None
    assert PL.rhat_scale(_rhat_params(), None) is None
    assert PL.rhat_scale(_rhat_params(), [1.0, 2.0]) is None      # 길이 불일치
    assert PL.rhat_diag(_rhat_params(), [1.0, 2.0]) is None


def test_rhat_diag_reports_floor_cap_and_raw():
    p = _rhat_params()
    d = PL.rhat_diag(p, [1.0, -3.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    assert d["clip"] == "floor" and d["scale"] == PL.RHAT_FLOOR
    assert d["raw"] == pytest.approx(math.exp(-3.0))     # 원비는 절단 전이다
    assert d["raw"] < d["scale"]
    d = PL.rhat_diag(p, [1.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    assert d["clip"] == "cap" and d["scale"] == PL.RHAT_CAP
    d = PL.rhat_diag(p, [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    assert d["clip"] == "none" and d["scale"] == pytest.approx(1.0)


def test_rhat_diag_names_extrapolated_columns():
    """훈련 지지구간 밖이면 **열 이름**으로 남는다 — 2026-09-07 이 log(ATR/O) 였다."""
    p = _rhat_params()
    assert PL.rhat_diag(p, [1.0, 0.5, 0, 0, 0, 0, 0])["extrap"] == []
    assert PL.rhat_diag(p, [1.0, 9.0, 0, 0, 0, 0, 0])["extrap"] == ["log(ATR/O)"]
    assert PL.rhat_diag(p, [1.0, -9.0, 0, 0, 0, 0, 0])["extrap"] == ["log(ATR/O)"]


def test_fit_rhat_carries_its_own_training_support():
    """지지구간이 파라미터에 없으면 외삽 진단은 **조용히 항상 빈 목록**이 된다."""
    sums = _sum_days(["2026-0%d-%02d" % (m, d) for m in (4, 5, 6)
                      for d in range(1, 22)])
    p = PL.fit_rhat(sums, len(sums), with_path=False)
    assert p is not None
    assert len(p["x_lo"]) == len(p["beta"]) == len(p["x_names"])
    assert all(lo <= hi for lo, hi in zip(p["x_lo"], p["x_hi"]))


def test_rhat_x_names_match_x_fixed_arity():
    """이름표와 설계행렬이 어긋나면 외삽 진단이 **엉뚱한 열을 지목한다**."""
    s = PL.SessionSummary(d="d", o=300.0, h=310.0, l=290.0, c=305.0, atr=10.0)
    prev = PL.SessionSummary(d="p", o=300.0, h=308.0, l=292.0, c=302.0, atr=10.0)
    assert len(PL._x_fixed(s, prev, 9.0)) == len(PL.RHAT_X_NAMES)
    assert len(PL.RHAT_X_NAMES_PATH) == len(PL.RHAT_X_NAMES) + 2


def test_rhat_cap_comment_no_longer_claims_it_is_never_reached():
    """F-4 — 문서-코드 괴리 고정. 백필 실측에서 상한에 5회 닿았다."""
    src = io.open(os.path.join(ROOT, "features/levels/premarket_levels.py"),
                  encoding="utf-8").read()
    i = src.index("RHAT_CAP = 2.0")
    line = src[src.rindex("\n", 0, i) + 1:src.index("\n", i)]
    assert "닿은 적 없음" not in line


# ────────────────────────────────────────── F-5  경고 순서

def test_constant_warning_is_last_so_the_notice_line_is_not_stuck():
    """상수는 지우지 않되 **항상 마지막**이다 — 그날 달라진 것이 앞에 와야 한다."""
    out = dict(structure=dict(up=[], down=[(1, ["a"])]),
               rhat=dict(scale=0.85, raw=0.44, clip="floor", extrap=["log(ATR/O)"]))
    w = LS.stage_warnings(out) + ["구조 후보 이력 3세션(6 필요)", _OI_CONST]
    assert w[-1] == _OI_CONST
    assert any("상방 후보 0개" in x for x in w)
    assert any("하한 절단" in x for x in w)
    assert any("외삽" in x for x in w)


def test_stage_warnings_are_silent_when_nothing_is_unusual():
    """경고가 매일 뜨면 아무도 안 읽는다 — 정상일엔 비어야 한다."""
    out = dict(structure=dict(up=[(1, ["a"])], down=[(2, ["b"])]),
               rhat=dict(scale=1.1, raw=1.1, clip="none", extrap=[]))
    assert LS.stage_warnings(out) == []


def test_absent_side_is_reported_as_measured_not_missing():
    """「후보 0개」는 *측정했는데 없다*이다 — 미측정과 섞이면 안 된다(계측 4원칙 ②)."""
    w = LS.stage_warnings(dict(structure=dict(up=[], down=[])))
    assert len(w) == 2
    assert all("측정됨, 미측정 아님" in x for x in w)


# ────────────────────────────────────────── F-2  이력 신선도

def _sum_days(days):
    out = [PL.SessionSummary(d=d, o=300.0, h=310.0, l=290.0, c=305.0) for d in days]
    PL.fill_derived(out)
    return out


def test_freshness_warns_when_raw_candles_is_ahead_of_the_cache(tmp_path):
    """EOD 가 빠지면 다음날 산출이 **하루 낡은 전일**로 조용히 돌아간다 — 그걸 잡는다."""
    raw = _raw_db(tmp_path, ["2026-09-03", "2026-09-04", "2026-09-07"])
    s = _sum_days(["2026-09-03", "2026-09-04"])           # 캐시는 09-04 까지
    msg = LS.history_freshness_warning(s, "2026-09-08", db_path=raw)
    assert msg and "2026-09-04" in msg and "2026-09-07" in msg


def test_freshness_is_silent_when_the_cache_is_current(tmp_path):
    raw = _raw_db(tmp_path, ["2026-09-03", "2026-09-04", "2026-09-07"])
    s = _sum_days(["2026-09-03", "2026-09-04", "2026-09-07"])
    assert LS.history_freshness_warning(s, "2026-09-08", db_path=raw) is None


def test_freshness_ignores_bars_of_the_target_day_itself(tmp_path):
    """산출 시점엔 당일 봉이 이미 있다 — 그걸 「캐시 낡음」으로 읽으면 매일 오탐이다."""
    raw = _raw_db(tmp_path, ["2026-09-04", "2026-09-07"])
    s = _sum_days(["2026-09-03", "2026-09-04"])
    assert LS.history_freshness_warning(s, "2026-09-07", db_path=raw) is None


def test_freshness_does_not_blame_quality_excluded_days(tmp_path):
    """품질 제외일은 캐시가 옳다 — 오탐하면 진짜 경고가 묻힌다."""
    raw = _raw_db(tmp_path, ["2026-09-03", "2026-09-04", "2026-09-07"])
    s = _sum_days(["2026-09-03", "2026-09-04"])
    assert LS.history_freshness_warning(
        s, "2026-09-08", excluded={"2026-09-07": "봉 29개(<300)"}, db_path=raw) is None


def test_freshness_probe_stays_silent_when_it_cannot_read(tmp_path):
    """프로브가 실패하면 **경고하지 않는다** — 없는 사실을 지어내지 않는다."""
    s = _sum_days(["2026-09-03", "2026-09-04"])
    assert LS.history_freshness_warning(
        s, "2026-09-08", db_path=str(tmp_path / "nope.db")) is None


def test_freshness_probe_reads_one_row_not_the_table(tmp_path):
    """🔴 장중 경로다 — 전수 스캔이면 2026-08-10 CB⑤ 자가유발의 재현이다.

    `ts` 가 PRIMARY KEY 라 역방향 LIMIT 1 은 인덱스 seek 이다. 계획에
    "SCAN" 이 뜨면(=B-tree 를 훑으면) 이 테스트가 깨진다.
    """
    raw = _raw_db(tmp_path, ["2026-09-0%d" % i for i in (1, 2, 3, 4)])
    con = sqlite3.connect(raw)
    plan = " ".join(str(r) for r in con.execute(
        "EXPLAIN QUERY PLAN SELECT ts FROM raw_candles WHERE ts < ? "
        "ORDER BY ts DESC LIMIT 1", ("2026-09-05",)).fetchall())
    con.close()
    assert "SEARCH" in plan.upper()
    assert "SCAN" not in plan.upper()


def test_freshness_hop_limit_is_bounded(tmp_path):
    """제외일이 줄줄이여도 되짚기는 유한하다 — 장중에 무한 루프를 만들지 않는다."""
    days = ["2026-08-%02d" % d for d in range(10, 30)]
    raw = _raw_db(tmp_path, days)
    assert LS.latest_session_before("2026-09-01", db_path=raw, hops=3,
                                    skip=tuple(days)) is None


# ────────────────────────────────────────── F-1  측면 단위 구조 채점

def _score_row(**kw):
    r = dict(date="2026-09-07", stage="0850", scored_at="x", actual_high=1.0,
             actual_low=0.0, bars=384, err_high=None, err_low=None,
             in50_high=None, in50_low=None, in80_high=None, in80_low=None,
             in80raw_high=None, in80raw_low=None, rhat_scale=None,
             struct_near_high=None, struct_near_low=None,
             struct_hit_high=None, struct_hit_low=None)
    r.update(kw)
    return r


def _agg_from(rows, monkeypatch):
    from utils import db_utils
    monkeypatch.setattr(db_utils, "fetch_premarket_levels_scores",
                        lambda days=60: rows)
    return LS.cumulative_scores()


def test_one_sided_day_no_longer_discards_the_measured_side(monkeypatch):
    """🔴 F-1 본체 — 2026-09-07 08:50 이 정확히 이 모양이다(상방 0개 · 하방 3개)."""
    rows = [_score_row(date="2026-09-07", err_high=1.0, err_low=-1.0,
                       in50_high=1, in50_low=0, in80_high=1, in80_low=1,
                       struct_near_low=0.2, struct_hit_low=1)]
    a = _agg_from(rows, monkeypatch)["0850"]
    assert a["s_n"] == 1 and a["s_hit"] == 1     # 534차: s_n == 0 (통째 탈락)
    assert a["s_skip"] == 1                      # 못 잰 측면은 분모 밖이다
    assert a["n"] == 2 and a["mae"] == pytest.approx(1.0)


def test_absent_side_never_counts_as_a_miss(monkeypatch):
    """미측정을 분모에 넣으면 '안 맞았다'로 위장된다(계측 4원칙 ②)."""
    rows = [_score_row(err_high=0.0, err_low=0.0,
                       struct_near_high=0.1, struct_hit_high=1)]
    a = _agg_from(rows, monkeypatch)["0850"]
    assert (a["s_hit"], a["s_n"], a["s_skip"]) == (1, 1, 1)
    assert a["s_hit"] / a["s_n"] == 1.0


def test_unmeasured_rows_are_not_counted_as_skipped_sides(monkeypatch):
    """산출 자체가 없던 날(미산출)은 구조 통계와 **무관**하다 — s_skip 도 아니다."""
    a = _agg_from([_score_row()], monkeypatch)["0850"]
    assert (a["s_n"], a["s_skip"], a["days"], a["rows"]) == (0, 0, 0, 1)


def test_structure_only_row_still_counts(monkeypatch):
    """거리 모델이 미산출이어도 구조는 산출됐을 수 있다 — 그 측면은 세야 한다."""
    a = _agg_from([_score_row(struct_near_high=0.4, struct_hit_high=0,
                              struct_near_low=0.1, struct_hit_low=1)],
                  monkeypatch)["0850"]
    assert (a["n"], a["s_n"], a["s_hit"], a["days"]) == (0, 2, 1, 1)


def test_both_sides_present_is_unchanged_from_534(monkeypatch):
    """정상일의 집계는 534차와 같은 수여야 한다 — 재정의가 전면 이동이면 안 된다."""
    rows = [_score_row(err_high=1.0, err_low=1.0,
                       struct_near_high=0.1, struct_hit_high=1,
                       struct_near_low=9.9, struct_hit_low=0)]
    a = _agg_from(rows, monkeypatch)["0850"]
    assert (a["s_hit"], a["s_n"], a["s_skip"]) == (1, 2, 0)


# ────────────────────────────────────────── DB 왕복 · 마이그레이션

def _mk_out():
    return dict(stage="0850", ref=300.0, open=300.0, atr=10.0, date="2026-09-07",
                bars=1, train_n=60, warnings=[_OI_CONST],
                rhat=dict(scale=0.85, raw=0.4438, clip="floor",
                          extrap=["log(ATR/O)"]),
                distance=dict(high=305.0, low=295.0, scale=0.85,
                              high50=(304.0, 306.0), high80=(303.0, 307.0),
                              low50=(294.0, 296.0), low80=(293.0, 297.0),
                              raw=dict(high80=(303.0, 307.0), low80=(293.0, 297.0))),
                structure=dict(up=[], down=[(295, ["매물대295.0(90분/2세션)"])]))


def test_rhat_diagnostic_survives_the_db_roundtrip(tmp_path, monkeypatch):
    db_utils, _ = _iso_db(tmp_path, monkeypatch)
    assert db_utils.save_premarket_levels("2026-09-07", "0850", "08:50:59", _mk_out())
    row = db_utils.fetch_premarket_levels("2026-09-07")["0850"]
    assert row["rhat"]["clip"] == "floor"
    assert row["rhat"]["raw"] == pytest.approx(0.4438)
    assert row["rhat"]["extrap"] == ["log(ATR/O)"]
    assert row["distance"]["scale"] == 0.85      # 실사용 값은 그대로다


def test_pre_536_rows_read_back_as_unmeasured_not_as_no_clip(tmp_path, monkeypatch):
    """🔴 2026-09-07 이전 행은 NULL = **미측정**이다 — 'clip 없음'이 아니다."""
    db_utils, path = _iso_db(tmp_path, monkeypatch, "old.db")
    db_utils.save_premarket_levels("2026-09-04", "0850", "backfill", _mk_out())
    con = sqlite3.connect(path)
    con.execute("UPDATE premarket_levels SET rhat_raw=NULL, rhat_clip=NULL,"
                " rhat_extrap=NULL")
    con.commit()
    con.close()
    assert db_utils.fetch_premarket_levels("2026-09-04")["0850"]["rhat"] is None


def test_unmeasured_row_writes_no_rhat_diagnostic(tmp_path, monkeypatch):
    """미산출 행에 절단 진단이 붙으면 '산출은 됐다'로 오독된다."""
    db_utils, _ = _iso_db(tmp_path, monkeypatch, "note.db")
    db_utils.save_premarket_levels("2026-09-07", "0930", "09:30:02", None,
                                   note="봉 부족 — 미산출", bars=2)
    row = db_utils.fetch_premarket_levels("2026-09-07")["0930"]
    assert row["rhat"] is None and row["distance"] is None


def test_migration_adds_columns_to_a_534_era_table(tmp_path, monkeypatch):
    """구세대 DB 를 지우지 않고 열만 더한다 — 굳힌 행이 사라지면 안 된다."""
    from config import settings
    from utils import db_utils
    path = str(tmp_path / "legacy.db")
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE premarket_levels (date TEXT NOT NULL, stage TEXT NOT NULL,"
                " computed_at TEXT NOT NULL, ref_price REAL, open_price REAL, atr14 REAL,"
                " dist_high REAL, dist_low REAL, high50_lo REAL, high50_hi REAL,"
                " high80_lo REAL, high80_hi REAL, low50_lo REAL, low50_hi REAL,"
                " low80_lo REAL, low80_hi REAL, raw80_hi_lo REAL, raw80_hi_hi REAL,"
                " raw80_lo_lo REAL, raw80_lo_hi REAL, rhat_scale REAL, sofar_high REAL,"
                " sofar_low REAL, train_n INTEGER, struct_up TEXT, struct_down TEXT,"
                " bars INTEGER, note TEXT, warnings TEXT, PRIMARY KEY (date, stage))")
    con.execute("INSERT INTO premarket_levels (date, stage, computed_at, ref_price)"
                " VALUES ('2026-09-04','0850','backfill', 1045.12)")
    con.commit()
    con.close()
    monkeypatch.setattr(settings, "PREMARKET_LEVELS_DB", path, raising=False)
    monkeypatch.setattr(db_utils, "PREMARKET_LEVELS_DB", path, raising=False)
    db_utils.init_premarket_levels_db()
    db_utils.init_premarket_levels_db()          # 멱등 — 두 번 돌아도 같다
    con = sqlite3.connect(path)
    cols = set(r[1] for r in con.execute("PRAGMA table_info(premarket_levels)"))
    kept = con.execute("SELECT ref_price FROM premarket_levels").fetchone()[0]
    con.close()
    assert set(["rhat_raw", "rhat_clip", "rhat_extrap"]) <= cols
    assert kept == 1045.12


def test_stage_warnings_are_not_dropped_on_the_way_to_the_db(tmp_path, monkeypatch):
    """🔴 이 회귀는 **538차 작업 중 실제로 났다**(py37_32 스모크에서 발견).

    `ensure_stage()` 가 `warnings=params["warnings"]` 를 넘기면 그 값이 truthy 라
    `save_premarket_levels()` 의 `warnings or out["warnings"]` 폴백이 안 걸리고
    단계 경고(구조 후보 0개 · R̂ 절단 · 외삽)가 **조용히 사라진다** — 계산은
    맞는데 기록만 없어지는, 이 세션이 잡던 바로 그 형태다.
    """
    db_utils, _ = _iso_db(tmp_path, monkeypatch, "warn.db")
    out = _mk_out()
    out["warnings"] = LS.stage_warnings(out) + [_OI_CONST]
    db_utils.save_premarket_levels(
        "2026-09-07", "0850", "08:50:59", out,
        warnings=out["warnings"] or ["구조 후보 이력 3세션(6 필요)"])
    got = db_utils.fetch_premarket_levels("2026-09-07")["0850"]["warnings"]
    assert any("상방 후보 0개" in w for w in got)
    assert any("하한 절단" in w for w in got)
    assert got[-1] == _OI_CONST


def test_ensure_stage_prefers_the_stage_warnings():
    """호출부가 다시 `params["warnings"]` 로 되돌아가면 위 회귀가 재발한다."""
    src = io.open(os.path.join(ROOT, "features/levels/levels_store.py"),
                  encoding="utf-8").read()
    i = src.index("def ensure_stage(")
    body = src[i:src.index("def _inside(", i)]
    assert 'warnings=(res["out"] or {}).get("warnings") or params.get("warnings")' in body
    assert 'warnings=params.get("warnings")' not in body


# ────────────────────────────────────────── 관측 전용 불변식(534차 계승)

def test_538_additions_stay_out_of_the_decision_paths():
    """🔴 진단을 붙였다고 판단 경로가 맥점을 읽기 시작하면 가이드 §11-1 위반이다."""
    for rel in ("strategy/entry/checklist.py", "model/ensemble_decision.py",
                "strategy/position_sizer.py", "strategy/risk/toxicity_gate.py"):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        src = io.open(p, encoding="utf-8").read()
        for token in ("premarket_levels", "levels_store", "rhat_diag",
                      "stage_warnings"):
            assert token not in src, "%s 가 %s 를 읽는다" % (rel, token)
