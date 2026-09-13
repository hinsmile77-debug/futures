# -*- coding: utf-8 -*-
"""[MW0601 559차] 데이터 결함 3건 구현계획 — 회귀 가드.

무엇을 고정하는가
-----------------
P0-1  정규 분봉 **필드10 = 누적 체결매수** 라벨 (컬럼명 `cum_sell` 은 오기)
P0-2  수급 로그압축 **역변환 가드** — 압축 이전 4일에 걸면 1.0686e+16 포화
P0-4  「98.6%」가 두 지표에 쓰인다는 문서 정정의 존속
P1-4  체결 방향 **미분류 버킷** — 판정 불가 볼륨을 매수로 폴백하지 않는다
P1-5  N분봉 집계가 섀도·앵커 열을 **전달**한다
P1'-1 수급 **미측정 플래그** — 프리장 0 과 실측 0 을 구분한다

이 파일이 깨지면 위 결론 중 하나가 코드에서 사라진 것이다. 수치를 고치기 전에
`docs/Spec for feature/Feature integrity/데이터결함3건_상태파악_및_수집구현계획_MW0601-20260913.md`
를 먼저 읽을 것.
"""
from __future__ import print_function

import io
import os
import sqlite3
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_ANALYSIS = os.path.join(_ROOT, "docs", "미륵이고도화3", "Golden power", "analysis")


def _read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def _load_guard():
    """경로에 공백·한글이 있어 일반 import 가 안 된다 — 파일 경로로 직접 적재."""
    path = os.path.join(_ANALYSIS, "inv_unit_guard.py")
    if not os.path.exists(path):
        pytest.skip("inv_unit_guard.py 없음")
    if sys.version_info[0] >= 3:
        import importlib.util
        spec = importlib.util.spec_from_file_location("inv_unit_guard_t", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    import imp                                          # noqa
    return imp.load_source("inv_unit_guard_t", path)


# ─────────────────────────── P0-1 ───────────────────────────
def test_p0_1_field10_semantics_recorded():
    """필드10 의미가 코드에 상수로 남아 있고, 오기 경고가 붙어 있다."""
    src = _read(os.path.join(_ROOT, "scripts", "collect_regular_futures.py"))
    assert "FIELD10_SEMANTICS" in src
    assert "FIELD11_SEMANTICS" in src
    assert "누적 체결매수" in src, "필드10 의미가 코드에서 사라졌다"
    assert "regular_flow_1m" in src, "오용 방지 뷰가 사라졌다"
    # 뷰는 필드11(cum_buy 컬럼)을 노출하면 안 된다 — 노출하면 우회가 무의미하다
    view = src.split("CREATE VIEW IF NOT EXISTS regular_flow_1m")[1].split('"""')[0]
    assert "cum_sell AS cum_buy_verified" in view
    assert "cum_buy," not in view, "뷰가 의미 미상 필드11 을 노출한다"


def test_p0_1_monotonicity_check_flags_broken_label():
    """단조증가가 깨지면 라벨 재확인 경고가 떠야 한다."""
    import importlib
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    mod = importlib.import_module("collect_regular_futures")
    con = sqlite3.connect(":memory:")
    con.executescript(mod.DDL)
    rows = [("X", "2026-09-11 09:%02d:00" % i, "2026-09-11", 1.0, 1.0, 1.0, 1.0,
             10, 0, cs, 0, "t", "t") for i, cs in enumerate([10, 20, 30, 25, 40])]
    con.executemany("INSERT INTO regular_candles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    out = []
    orig, mod.P = mod.P, lambda m: out.append(m)
    try:
        mod._flow_semantics_check(con, "X")
    finally:
        mod.P = orig
    joined = "\n".join(out)
    assert "비단조 1건" in joined, joined
    assert "라벨 재확인 필요" in joined, joined


# ─────────────────────────── P0-2 ───────────────────────────
def test_p0_2_guard_blocks_precompression_days():
    """압축 이전 단위(4일)는 날짜 규칙으로 빠지고, 포화 상수는 절대 안 나온다."""
    import numpy as np
    g = _load_guard()
    # 압축 이전 원단위: 작은 계약수라 크기 임계로는 못 거른다 — 날짜가 걸러야 한다
    out = g.invert_investor_log1p([12.0, -541664.0], [1.0, 1.0],
                                  ["2026-06-08 10:00:00", "2026-06-02 10:00:00"],
                                  verbose=False)
    assert np.all(np.isnan(out)), out
    # 정상 압축값은 통과하고 계약수로 복원된다
    ok = g.invert_investor_log1p([1.4651055415441803], [1.0],
                                 ["2026-07-14 11:00:00"], verbose=False)
    assert abs(ok[0] - (np.expm1(1.4651055415441803) * 1000.0)) < 1e-6
    # 미측정은 값이 있어도 NaN
    uns = g.invert_investor_log1p([1.2], [0.0], ["2026-09-11 10:00:00"], verbose=False)
    assert np.isnan(uns[0])
    # 안전망: 압축 이후인데 |v|>=30 이면 단위 불일치로 본다
    big = g.invert_investor_log1p([31.0], [1.0], ["2026-09-11 10:00:00"], verbose=False)
    assert np.isnan(big[0])


def test_p0_2_saturation_constant_never_returned():
    import numpy as np
    g = _load_guard()
    sat = g._EXPM1_SATURATION
    assert abs(sat - 1.06865e16) / sat < 1e-3, sat        # 1.07e16 의 정체
    vals = [0.5, 5.0, 29.9, 30.0, 30.1, 1e6, -1e6]
    out = g.invert_investor_log1p(vals, [1.0] * len(vals),
                                  ["2026-09-11 10:00:00"] * len(vals), verbose=False)
    fin = out[np.isfinite(out)]
    assert not np.any(np.isclose(np.abs(fin), sat)), out


def test_p0_2_analysis_scripts_use_the_guard():
    """세 분석 스크립트가 로컬 역변환을 버리고 가드를 쓴다."""
    for rel in ("rules_backtest.py", "whipsaw/rebuild_panel.py", "whipsaw/ws_analysis.py"):
        path = os.path.join(_ANALYSIS, *rel.split("/"))
        if not os.path.exists(path):
            pytest.skip("%s 없음" % rel)
        src = _read(path)
        assert "invert_investor_log1p" in src, rel
        assert "def inv(v)" not in src, "%s 에 로컬 역변환이 남아 있다" % rel


# ─────────────────────────── P0-4 ───────────────────────────
def test_p0_4_metric_disambiguation_documented():
    src = _read(os.path.join(_ROOT, "CLAUDE.md"))
    assert "559차" in src and "매수>매도 봉 비율" in src, "98.6% 구분 문단이 사라졌다"
    assert "64.53%" in src and "49.88%" in src, "체결량 비중 대조가 사라졌다"


# ─────────────────────────── P1-4 / P1-5 ───────────────────────────
def test_p1_4_unknown_side_not_folded_into_buy():
    """판정 불가 틱은 매수로 폴백하지 않고 미분류로 남는다."""
    src = _read(os.path.join(_ROOT, "collection", "cybos", "realtime_data.py"))
    assert "unk_vol" in src, "미분류 버킷이 없다 — 판정 불가가 매수로 접힌다"
    assert "_UNKNOWN_SIDE" in src or "side is None" in src


def test_p1_5_aggregator_forwards_shadow_columns():
    """N분봉 집계가 섀도·앵커를 올린다 — 안 올리면 전환해도 legacy 를 본다."""
    from features.bar_aggregator import BarAggregator                     # noqa
    src = _read(os.path.join(_ROOT, "features", "bar_aggregator.py"))
    for col in ("buy_vol_flag", "sell_vol_flag", "anchor_buy", "anchor_sell"):
        assert col in src, "bar_aggregator 가 %s 를 전달하지 않는다" % col


# ─────────────────────────── P1'-1 ───────────────────────────
def test_p1p_1_investor_measured_flags_exist():
    """수급 미측정 플래그 — 값 0 과 미측정을 구분한다(계측 4원칙 ②)."""
    src = _read(os.path.join(_ROOT, "collection", "cybos", "investor_data.py"))
    for k in ("foreign_futures_net_measured", "retail_futures_net_measured",
              "institution_futures_net_measured"):
        assert k in src, "%s 가 없다" % k


def test_p1p_1_measured_flag_semantics():
    """프리장 0 과 실측 0 이 구분되고, 일일 리셋으로 되돌아간다."""
    from collection.cybos.investor_data import CybosInvestorData
    c = CybosInvestorData(None)
    f = c.get_features()
    assert f["foreign_futures_net_measured"] == 0.0, "프리장인데 측정됐다고 나온다"
    c._futures_supported = True
    c._futures_seen = {"foreign"}
    f2 = c.get_features()
    assert f2["foreign_futures_net_measured"] == 1.0
    assert f2["retail_futures_net_measured"] == 0.0, "안 온 키까지 측정으로 샌다"
    c.reset_daily()
    assert c.get_features()["foreign_futures_net_measured"] == 0.0


# ─────────────────────────── P1-3 / P1-6 ───────────────────────────
def test_p1_3_flow_source_defaults_to_legacy():
    """전환 스위치는 기본이 legacy 여야 한다 — 소비 0."""
    from config.settings import CVD_FLOW_SOURCE_MODE, CVD_SHADOW_EPOCH
    assert CVD_FLOW_SOURCE_MODE == "legacy", (
        "체결 방향 원천이 바뀌어 있다. Phase 3 은 별도 승인 사항이다")
    assert CVD_SHADOW_EPOCH == "2026-08-10"


def test_p1_3_flow_source_provenance_emitted():
    """무엇을 원천으로 썼는지·폴백했는지 피처로 남는다(계측 4원칙 ④)."""
    src = _read(os.path.join(_ROOT, "features", "feature_builder.py"))
    assert "cvd_flow_source" in src and "cvd_flow_fallback" in src


def test_p1_6_epoch_mask_is_observation_only_by_default():
    from config.settings import FEATURE_EPOCH_MASK_ENABLED
    from learning.feature_epoch_mask import (epoch_gated_features, apply_epoch_window,
                                             report_epoch_loss)
    assert FEATURE_EPOCH_MASK_ENABLED is False
    names = ["cvd_norm", "cvd_slope", "vwap_position"]
    assert epoch_gated_features(names) == [], "legacy 인데 세대 경계가 생겼다"
    assert epoch_gated_features(names, mode="shadow") == ["cvd_norm", "cvd_slope"]
    ts = ["2026-07-01 10:00", "2026-08-20 10:00"]
    idx, applied = apply_epoch_window(ts, names)
    assert applied is False and idx == [0, 1], "기본값에서 표본이 잘렸다"
    rep = report_epoch_loss(ts, names)
    assert rep["rows"] == 2 and rep["rows_after_epoch"] == 1


# ─────────────────────────── P1'-2 / P1'-3 ───────────────────────────
def test_p1p_2_unit_mismatch_days_excluded_by_default():
    """압축 이전 단위 4거래일은 기본으로 학습에서 빠진다 — 섀도가 아니다."""
    from config.settings import INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED
    from learning.feature_epoch_mask import (filter_unit_mismatch_rows,
                                             INVESTOR_UNIT_MISMATCH_DAYS)
    assert INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED is True, (
        "이 플래그는 섀도가 아니다 — 끄면 수급 8키 스케일러 std 가 5.7만 배로 뛴다")
    assert INVESTOR_UNIT_MISMATCH_DAYS == frozenset(
        ("2026-06-02", "2026-06-04", "2026-06-05", "2026-06-08"))
    rows = [("2026-06-02 10:00:00", "{}"), ("2026-09-11 10:00:00", "{}")]
    kept = filter_unit_mismatch_rows(rows, ts_getter=lambda r: r[0])
    assert [r[0] for r in kept] == ["2026-09-11 10:00:00"]


def test_p1p_3_backfill_filter_wired_into_all_training_loaders():
    """418차 결정 1 이 섀도 TB 한 곳이 아니라 학습 로더 전부에 걸려 있다."""
    for rel in ("learning/batch_retrainer.py", "learning/quantile_regressor.py"):
        src = _read(os.path.join(_ROOT, *rel.split("/")))
        assert "filter_backfill_rows" in src, "%s 에 백필 제외가 없다" % rel
    from learning.feature_epoch_mask import is_live_row
    assert is_live_row('{"feature_quality_score": 0.3}') is False
    assert is_live_row('{"feature_quality_score": 1.0}') is True
    assert is_live_row("깨진 JSON") is True, "파싱 실패를 제외 사유로 삼지 말 것"


def test_p1p_2_unit_mismatch_wired_into_production_path():
    """운영 경로(Phase 2)에서 X 를 만들기 전에 걸려야 한다 — 뒤면 소용없다."""
    src = _read(os.path.join(_ROOT, "learning", "batch_retrainer.py"))
    i_filter = src.find("filter_unit_mismatch_rows as _fum")
    i_x = src.find("[[rec[1].get(f, 0.0) for f in use_feat_names]")
    assert i_filter != -1 and i_x != -1
    assert i_filter < i_x, "단위 불일치 제외가 X_hz 구성보다 뒤에 있다"


# ─────────────────────────── P1-4 리포트 항등식 ───────────────────────────
def test_p1_4_identity_i4_in_anchor_report():
    src = _read(os.path.join(_ROOT, "scripts", "generate_cvd_anchor_report.py"))
    assert "i4_n" in src and "unk_vol" in src, "I4 항등식이 리포트에 없다"
    assert "i4_absent" in src, "559차 이전 봉의 미측정을 0 과 섞고 있다"
