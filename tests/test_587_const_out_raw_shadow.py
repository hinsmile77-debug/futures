# -*- coding: utf-8 -*-
"""[MW0601 587차 / P1-1] ConstOut raw 기준 판정 — 섀도 배선 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (전문: docs/정기점검/매일점검/MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md §10)
────────────────────────────────────────────────────────────────────────────
ConstOut 은 "GBM 이 붕괴했는가" 를 묻는데, 읽는 값은
`GBM → SGD 블렌드 → RF 블렌드 → BAR_CACHE_DECAY → bias fallback → Platt` 을
전부 통과한 뒤의 것이다. 2026-09-15 10:59 에 그 결과가 실측됐다 — 564차 P0-1
억제를 통과한 유일한 건이 **또 오탐**이었다:

    flat(=conf) 0.3603 0.3602 0.3601 0.3601 0.3598 0.3597   → range=0.0000
    up:down      1.12   1.10   0.89   0.86   1.12   0.87    → 방향이 뒤집힌다

최댓값 채널만 상수이고 방향 채널은 살아 있었다. 감지 정의가 `(direction, max_prob)`
1차원이라, `dir=0` 구간에서 `max_prob = flat = cal_conf`(Platt 출력) 하나만 멈추면
up/down 이 무엇을 하든 "붕괴" 로 읽힌다.

587차는 **보정 전 GBM raw 로 같은 규칙을 한 번 더 돌려** 불일치를 재고
(`CONST_OUT_RAW_SHADOW_ENABLED`), 임계 재보정 후에 전환한다
(`CONST_OUT_RAW_BASED_ENABLED`). 계측 → 재보정 → 전환 (317차 Hurst 전례).

지키는 불변식:
  T1  raw 계열이 `detail[hz]` 에 실린다 — 재보정의 원천 데이터다.
  T2  🔴 raw 가 없으면 **키를 넣지 않는다**. `null`/`0` 으로 채우면 "GBM 이 0 을
      냈다" 와 구분되지 않는다(계측 4원칙 ②).
  T3  🔴 10:59 재현 — live 는 STUCK 인데 raw 는 아니다. 이게 P1-1 의 존재 이유다.
  T4  반대 방향도 잡는다 — raw 가 상수면 raw 판정이 STUCK 이다(감지력 보존).
  T5  기본값에서 **live 판정이 바뀌지 않는다**(`_BASED_ENABLED=False`).
  T6  플래그를 켜면 raw 기준으로 바뀐다.
  T7  🔴 raw 미측정 호라이즌은 플래그를 켜도 **live 판정을 유지**한다.
      미측정을 "정상" 으로 읽으면 GBM 미준비 구간에 감지가 통째로 사라진다.
  T8  `const_output_horizons_live` 는 플래그와 무관하게 항상 현행 규칙 결과다
      — 전환 후에도 앞뒤를 같은 잣대로 잇기 위해서다(461차 `mdd_pct` 교훈).
  T9  main.py 가 raw 스냅샷을 **매분 비운다**(계측 4원칙 ④ 폴백 가시화).
  T10 main.py 가 raw 를 **곁채널**로 넘긴다 — `horizon_proba` 는 네 번 재생성되므로
      키를 얹으면 한 곳만 빠뜨려도 조용히 사라진다.
  T11 재보정 스크립트가 사전등록 상수를 갖고 `guard_intraday` 를 부른다.

실행: conda run -n py37_32 python -m pytest tests/test_587_const_out_raw_shadow.py
"""

import importlib
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from config import settings as S  # noqa: E402
from model.ensemble_decision import EnsembleDecision  # noqa: E402

_N = EnsembleDecision._CONST_OUT_N


def _drive(live_confs, raw_confs, live_dir=0, raw_dir=1, hz="3m"):
    """live/raw conf 계열을 순서대로 먹이고 마지막 decision 을 돌려준다.

    raw_confs 의 원소가 None 이면 그 분은 **raw 미측정**이다.
    """
    ed = EnsembleDecision()
    out = None
    for i, lc in enumerate(live_confs):
        hp = {hz: {"up": 0.30, "down": 0.34, "flat": round(lc, 4),
                   "direction": live_dir, "confidence": round(lc, 4)}}
        rc = raw_confs[i] if i < len(raw_confs) else None
        raw = ({hz: {"confidence": rc, "direction": raw_dir}}
               if rc is not None else {})
        out = ed.compute(hp, active_horizons=[hz], gbm_raw=raw)
    return out


# ══════════════════════════════════════════════════════════════════════════
# T1~T2 — 원천 데이터 적재
# ══════════════════════════════════════════════════════════════════════════

def test_t1_raw_series_lands_in_detail():
    d = _drive([0.360] * _N, [0.41] * _N)
    det = d["detail"]["3m"]
    assert det["gbm_raw_conf"] == 0.41, "재보정 원천이 detail 에 실리지 않는다"
    assert det["gbm_raw_dir"] == 1


def test_t2_missing_raw_is_absent_not_zero():
    """🔴 미측정 ≠ 0 — 키 자체가 없어야 한다."""
    d = _drive([0.360] * _N, [None] * _N)
    det = d["detail"]["3m"]
    assert "gbm_raw_conf" not in det, (
        "raw 가 없는데 키를 넣으면 'GBM 이 그 값을 냈다' 와 구분되지 않는다"
    )
    assert d["const_output_raw_measured"] == [], "미측정인데 관측으로 집계됐다"


# ══════════════════════════════════════════════════════════════════════════
# T3~T4 — 섀도 판정
# ══════════════════════════════════════════════════════════════════════════

def test_t3_reproduces_20260915_false_positive():
    """🔴 live 는 STUCK, raw 는 아님 — P1-1 의 존재 이유."""
    live = [0.3603, 0.3602, 0.3601, 0.3601, 0.3598, 0.3597]   # 실측
    raw = [0.40, 0.41, 0.42, 0.43, 0.44, 0.45]                # 변동 중
    d = _drive(live, raw)
    assert d["const_output_horizons"] == ["3m"], "현행 규칙이라면 오탐이 나야 한다"
    assert d["const_output_horizons_raw"] == [], (
        "raw 가 명백히 변동 중인데 섀도까지 STUCK 이면 P1-1 이 무의미하다"
    )
    assert d["const_output_raw_measured"] == ["3m"]


def test_t4_raw_constant_is_detected():
    """감지력 보존 — raw 가 진짜 상수면 섀도가 잡아야 한다."""
    d = _drive([0.360] * _N, [0.4123] * _N)
    assert d["const_output_horizons_raw"] == ["3m"]


# ══════════════════════════════════════════════════════════════════════════
# T5~T8 — 전환 스위치
# ══════════════════════════════════════════════════════════════════════════

def _with_flag(value, fn):
    old = getattr(S, "CONST_OUT_RAW_BASED_ENABLED", False)
    S.CONST_OUT_RAW_BASED_ENABLED = value
    try:
        return fn()
    finally:
        S.CONST_OUT_RAW_BASED_ENABLED = old


def test_t5_default_does_not_change_live_verdict():
    assert S.CONST_OUT_RAW_BASED_ENABLED is False, (
        "섀도가 끝나기 전에 전환 플래그가 켜져 있다 — settings 주석의 전환 3조건 확인"
    )
    d = _drive([0.3603, 0.3602, 0.3601, 0.3601, 0.3598, 0.3597],
               [0.40, 0.41, 0.42, 0.43, 0.44, 0.45])
    assert d["const_output_horizons"] == ["3m"], "기본값에서 동작이 바뀌었다"


def test_t6_flag_switches_verdict_to_raw():
    d = _with_flag(True, lambda: _drive(
        [0.3603, 0.3602, 0.3601, 0.3601, 0.3598, 0.3597],
        [0.40, 0.41, 0.42, 0.43, 0.44, 0.45]))
    assert d["const_output_horizons"] == [], "전환했는데 live 판정이 남아 있다"
    assert d["const_output_horizons_live"] == ["3m"], "현행 규칙 결과가 보존돼야 한다"


def test_t7_unmeasured_horizon_keeps_live_verdict_even_when_switched():
    """🔴 미측정을 '정상' 으로 읽으면 GBM 미준비 구간에 감지가 사라진다."""
    d = _with_flag(True, lambda: _drive([0.360] * _N, [None] * _N))
    assert d["const_output_horizons"] == ["3m"], (
        "raw 를 관측하지 못한 호라이즌까지 전환 대상으로 삼았다 — 계측 4원칙 ② 위반"
    )


def test_t8_live_axis_is_always_current_rule():
    for flag in (False, True):
        d = _with_flag(flag, lambda: _drive([0.360] * _N, [0.40, 0.41, 0.42, 0.43, 0.44]))
        assert d["const_output_horizons_live"] == ["3m"], (
            "flag=%s 에서 live 축이 오염됐다 — 전환 전후 비교가 불가능해진다" % flag
        )


# ══════════════════════════════════════════════════════════════════════════
# T9~T11 — 배선 불변식 (소스 수준)
# ══════════════════════════════════════════════════════════════════════════

def _main_src(name):
    import main
    return inspect.getsource(getattr(main.TradingSystem, name))


def test_t9_raw_snapshot_is_cleared_every_minute():
    src = _main_src("run_minute_pipeline")
    assert "self._gbm_raw_conf_last[_h_rr] = None" in src, (
        "매분 비우지 않으면 GBM 미준비·비배포 분에 지난 분 값이 남아 "
        "'이번 분에 GBM 이 그 값을 냈다' 로 읽힌다 (계측 4원칙 ④)"
    )
    i_clear = src.index("self._gbm_raw_conf_last[_h_rr] = None")
    i_set = src.index("self._gbm_raw_conf_last[h_name] = float(_gbm_raw_conf)")
    assert i_clear < i_set, "비우기가 채우기보다 뒤에 있으면 매분 지워진다"


def test_t10_raw_is_passed_as_side_channel():
    src = _main_src("run_minute_pipeline")
    # ⚠ 느슨하게 `gbm_raw={` 만 찾으면 안 된다 — 기존 [CONF⚠] 로그가
    #   `f"gbm_raw={_gbm_raw_conf:.4f} ..."` 로 그 문자열을 이미 갖고 있어
    #   **변경 전 코드에서도 통과한다**(가드가 헛돈다). 실제 전달 형태를 못박는다.
    assert '_h_gr: {"confidence": self._gbm_raw_conf_last[_h_gr]' in src, (
        "ensemble.compute() 에 raw 가 곁채널로 전달되지 않는다"
    )
    # horizon_proba 에 얹지 않았는지 — 얹으면 4곳의 재생성에서 조용히 사라진다
    assert 'horizon_proba[h_name]["gbm_raw_conf"]' not in src, (
        "horizon_proba 에 키를 얹었다. 그 dict 는 블렌드·bias 폴백·배포필터·보정에서 "
        "재생성되므로 한 곳만 빠뜨려도 미측정이 아니라 오측정이 된다"
    )
    assert "self._gbm_raw_dir_last[h_name] = int(" in src, "raw 방향이 기록되지 않는다"


def test_t11_recalibration_script_preregisters_criteria():
    mod = importlib.import_module("scripts.const_out_raw_recalibration")
    for c in ("MIN_DAYS", "MIN_MINUTES", "EXPLAIN_MULT", "STABILITY_PCT", "CANDIDATES"):
        assert hasattr(mod, c), "사전등록 상수 %s 누락" % c
    assert mod.CONST_OUT_N == EnsembleDecision._CONST_OUT_N, (
        "재보정이 감지기와 다른 규칙을 쓰면 나온 임계를 그대로 쓸 수 없다"
    )
    src = inspect.getsource(mod)
    assert "guard_intraday" in src, "장중 라이브 DB 분석 금지 가드 누락 (456차)"
    assert "connect_ro" in src, "읽기전용 연결을 쓰지 않는다"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
