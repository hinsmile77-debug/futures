# -*- coding: utf-8 -*-
"""[MW0601 564차 / P0-1·P0-3·P2-1] ConstOut ↔ BiasReset 되먹임 루프 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (전문: docs/정기점검/매일점검/MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md)
────────────────────────────────────────────────────────────────────────────
`[ConstOut] 3m 상수 출력` 은 GBM 붕괴가 아니라 **다른 안전장치가 만든 부산물**이었다.

  ① `[BiasReset]` 이 편향 호라이즌 출력을 `{1/3,1/3,1/3}, dir=0` 로 덮어쓴다(20분)
  ② `_apply_horizon_calibration()` 의 동률 tie-break 가 그것을 `dir=+1, conf=0.3333`
     **상수**로 바꾼다 (`up == down` → `max()` 가 리스트 첫 원소를 고른다)
  ③ ConstOut 이 그 상수를 읽고 "스케일러 노후" 로 오진 → 스케일러 재적합 + GBM 재학습
  ④ 재학습 완료가 `_bias_override_horizons.clear()` → ①의 20분 쿨다운을 6~8분에 끊음
  ⑤ → ① 로 복귀

실측(10거래일, 2026-09-01~09-14): ConstOut 58건 중 **57건(98.3%)이 `range=0.0000`**
이고 전부 `[BiasReset]` 이 6~12분 앞섰다. 진성은 1건(`range=0.0040`)뿐.
그 오진이 부른 재학습은 40,818행 CV 검증본을 4,800행 무검증본으로 바꾸고(매일 ~6시간),
CB③ 표본을 60건 버리고, BiasReset 쿨다운을 무력화했다.

지키는 불변식:
  T1  ConstOut 감지는 **정확히 5개의 배포 표본**으로 확정된다 (`_CONST_OUT_N`).
  T2  상수 출력이면 `range == 0.0` 으로 보고된다 — 아티팩트의 지문이다.
  T3  값이 변하면 감지되지 않는다 (살아 있는 GBM 은 걸리지 않는다).
  T4  🔴 재학습 트리거는 `_bias_override_horizons` 를 **제외한 뒤** 판단한다.
      이게 빠지면 ③이 그대로 재발한다.
  T5  억제분은 **버리지 않고** 별도 축으로 센다 (계측 4원칙 ③ 탈락 가시화) —
      증가 · 스냅샷 · 일일 리셋 세 곳 모두.
  T6  🔴 `_mh_const_out_*`(앙상블 제외 시간)은 **필터하지 않는다**. 억제는 재학습
      트리거만 막는 것이지 "제외된 적 없다" 가 아니다 — 필터하면 471차 G-2 채널
      (`const_out_horizon_watch`)의 시계열이 조용히 끊긴다.
  T7  🔴 재학습 후 BiasReset 초기화는 **교체된 호라이즌(scope)만** 건드린다.
      전역 초기화는 3m 전용 재학습이 1m·15m 쿨다운까지 지운다(2026-09-14 11:17 실측).
  T8  `_retrain_subproc_scope` 는 `__init__` 에서 명시 초기화되고 재학습 시작 시
      할당된다 (계측 4원칙 ④ — `getattr(self, ..., 기본값)` 폴백 금지).
  T9  ConstOut 확정 로그에 `gbm_raw` 가 병기된다 (P2-1). 이 정보가 없어서
      2026-09-14 진단이 코드 역추적으로만 가능했다.

실행: conda run -n py37_32 python -m pytest tests/test_564_constout_bias_artifact.py
      (COM/브로커 불필요)
"""

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402
from model.ensemble_decision import EnsembleDecision  # noqa: E402


# ══════════════════════════════════════════════════════════════════════════
# T1~T3 — 감지기 의미론 (행동 테스트)
# ══════════════════════════════════════════════════════════════════════════

_UNIFORM = {"up": 1 / 3, "down": 1 / 3, "flat": 1 / 3,
            "direction": 1, "confidence": 1 / 3}


def _feed(ed, hz, samples):
    """호라이즌 hz 에 samples(conf 리스트)를 순서대로 먹이고, 매 스텝의
    (감지여부, range) 를 돌려준다. ConstOut 감지 루프와 동일한 계산을 쓴다."""
    out = []
    for conf in samples:
        ed._hz_conf_hist[hz].append((1, round(float(conf), 3)))
        hist = ed._hz_conf_hist[hz]
        stuck = False
        rng = None
        if len(hist) >= ed._CONST_OUT_N:
            dirs = [x[0] for x in hist]
            confs = [x[1] for x in hist]
            rng = max(confs) - min(confs)
            stuck = (len(set(dirs)) == 1 and rng < ed._CONST_OUT_RANGE)
        out.append((stuck, rng))
    return out


def test_t1_detects_after_exactly_five_deployed_samples():
    ed = EnsembleDecision()
    res = _feed(ed, "3m", [1 / 3] * 6)
    assert [r[0] for r in res] == [False, False, False, False, True, True], (
        "ConstOut 은 배포 표본 5개(_CONST_OUT_N)로 확정돼야 한다 — "
        "벽시계 5분이 아니다. 실제 경과 시간은 배포 정책(HZ_DEPLOY_POLICY)에 달렸고, "
        "3m 은 3분 중 2분 배포라 약 7분이 걸린다. 이 산수가 '왜 항상 3m인가'의 답이다."
    )


def test_t2_uniform_fallback_reports_range_zero():
    """🔴 아티팩트의 지문: range 가 '작다'가 아니라 **정확히 0** 이다."""
    ed = EnsembleDecision()
    res = _feed(ed, "3m", [1 / 3] * 5)
    stuck, rng = res[-1]
    assert stuck is True
    assert rng == 0.0, (
        "uniform fallback 은 매분 완전히 동일한 값을 낸다 → range=0.0000. "
        "살아 있는 GBM 은 이 값을 낼 수 없다(실측 10거래일 58건 중 57건이 0.0000). "
        "range 를 진성/아티팩트 판별에 쓸 수 있는 근거다."
    )


def test_t3_live_model_output_is_not_detected():
    """살아 있는 GBM(변동하는 conf)은 걸리지 않는다 — 오탐 방지 회귀."""
    ed = EnsembleDecision()
    # 2026-09-14 12:50~13:09 실측 3m conf 궤적 (bias-override 구간 밖)
    live = [0.49, 0.47, 0.43, 0.43, 0.54, 0.53, 0.63, 0.61, 0.58, 0.54]
    res = _feed(ed, "3m", live)
    assert not any(r[0] for r in res), (
        "정상 변동 구간이 ConstOut 으로 잡히면 P0-1 억제가 진성까지 삼킨다"
    )


# ══════════════════════════════════════════════════════════════════════════
# T4~T9 — 배선 불변식 (소스 수준)
#
# ConstOut 트리거는 `run_minute_pipeline()` 안에 인라인돼 있어 스텁 self 로
# 구동할 수 없다. 대신 **그 함수의 소스**를 직접 읽어 배선을 못 박는다
# (tests/test_425_*, test_457_daily_fixes.py 와 같은 방식).
# ══════════════════════════════════════════════════════════════════════════

def _src(fn):
    return inspect.getsource(fn)


_PIPELINE_SRC = _src(main.TradingSystem.run_minute_pipeline)
_RESET_SRC    = _src(main.TradingSystem._reset_model_health_counters)
_SNAP_SRC     = _src(main.TradingSystem._model_health_snapshot)
_DONE_SRC     = _src(main.TradingSystem._on_gbm_retrain_done)
_START_SRC    = _src(main.TradingSystem._start_gbm_retrain_subprocess)
_INIT_SRC     = _src(main.TradingSystem.__init__)


def test_t4_retrain_trigger_excludes_bias_override():
    """🔴 P0-1 본체 — 이게 빠지면 되먹임 루프가 그대로 재발한다."""
    assert "_bias_override_horizons" in _PIPELINE_SRC, (
        "ConstOut 트리거가 bias_override 를 전혀 모른다 — P0-1 미배선"
    )
    # 필터가 _const_hz 를 실제로 좁히는가
    assert "_const_hz = [h for h in _const_hz if h not in self._bias_override_horizons]" \
        in _PIPELINE_SRC, (
            "억제가 로그만 남기고 _const_hz 를 좁히지 않으면 재학습은 그대로 돈다"
        )
    # 좁히기가 재학습 트리거보다 **앞**에 있는가
    i_filter = _PIPELINE_SRC.index("if h not in self._bias_override_horizons")
    i_trig = _PIPELINE_SRC.index("상수 출력 확정")
    assert i_filter < i_trig, "억제가 트리거보다 뒤에 있으면 아무것도 막지 못한다"


def test_t5_suppressed_events_are_counted_not_discarded():
    """계측 4원칙 ③ — 절단했으면 잔여를 명시한다. 억제도 같다."""
    assert "_mh_const_out_suppressed_events" in _INIT_SRC, "__init__ 명시 초기화 없음"
    assert "self._mh_const_out_suppressed_events += 1" in _PIPELINE_SRC, "증가 없음"
    assert "const_out_suppressed_events" in _SNAP_SRC, "일일 스냅샷에 안 실림"
    assert "_mh_const_out_suppressed_events = 0" in _RESET_SRC, "일일 리셋 누락"


def test_t6_exclusion_metrics_are_not_filtered():
    """🔴 억제해도 '앙상블에서 빠져 있던 시간'은 그대로 센다.

    여기를 같이 필터하면 471차 G-2 채널(`const_out_horizon_watch`)이 보는
    `scaler_daily.const_out_by_horizon` 시계열이 P0-1 배포일에 조용히 끊긴다 —
    461차 `mdd_pct` 와 같은 유형의 사고다.
    """
    i_count = _PIPELINE_SRC.index("self._mh_const_out_minutes += 1")
    i_filter = _PIPELINE_SRC.index("if h not in self._bias_override_horizons")
    assert i_count < i_filter, (
        "제외시간 계측이 억제 필터 **뒤로** 옮겨졌다 — 억제된 분이 "
        "'제외된 적 없음'으로 기록되어 채널 시계열이 끊긴다"
    )


def test_t7_bias_reset_clearing_is_scope_limited():
    """🔴 P0-3 — 3m 전용 재학습이 1m·15m 쿨다운까지 지우면 안 된다."""
    assert "_bias_override_horizons.clear()" not in _DONE_SRC, (
        "전역 clear() 가 남아 있다 — 457차가 학습 스코프를 좁힌 의미가 사라진다"
    )
    assert "_bias_scope" in _DONE_SRC, "스코프 변수 없음 — P0-3 미배선"
    assert "self._retrain_subproc_scope or list(HORIZONS)" in _DONE_SRC, (
        "스코프가 비었을 때 전 호라이즌으로 떨어지지 않으면 EOD 전체 재학습 후 "
        "편향 상태가 남는다(457차 이전 동작을 보존해야 한다)"
    )
    assert "self._bias_override_horizons.discard(_bh)" in _DONE_SRC


def test_t8_retrain_scope_has_no_silent_fallback():
    """계측 4원칙 ④ — 런타임 상태를 getattr 기본값으로 읽지 않는다."""
    assert "self._retrain_subproc_scope: list = []" in _INIT_SRC, (
        "__init__ 명시 초기화가 없으면 첫 EOD 재학습에서 AttributeError 또는 "
        "조용한 폴백이 된다"
    )
    assert "self._retrain_subproc_scope       = [str(h) for h in (horizons or [])]" \
        in _START_SRC, "재학습 시작 시 스코프가 기록되지 않는다"
    assert 'getattr(self, "_retrain_subproc_scope"' not in _DONE_SRC, (
        "getattr 폴백으로 읽으면 미설정과 빈 스코프를 구분할 수 없다"
    )


def test_t9_constout_log_carries_gbm_raw():
    """P2-1 — 로그 한 줄로 'GBM 이 상수인가, 뒷단이 상수인가'를 가를 수 있어야 한다."""
    assert "_gbm_raw_conf_last" in _INIT_SRC, "__init__ 명시 초기화 없음"
    # ⚠ 느슨하게 "gbm_raw" 만 찾으면 안 된다 — 기존 [CONF⚠] 로그가 이미 그 문자열을
    #   갖고 있어 **변경 전 코드에서도 통과한다**(가드가 헛돈다). 확정 로그의
    #   실제 포맷 문자열을 못 박는다.
    assert "bias_override=N gbm_raw(" in _PIPELINE_SRC, (
        "ConstOut 확정 로그에 bias_override/gbm_raw 병기가 없다 — P2-1 미배선"
    )
    assert "self._gbm_raw_conf_last[h_name] = float(_gbm_raw_conf)" in _PIPELINE_SRC, (
        "보정 전 GBM conf 가 기록되지 않으면 로그에 실을 값이 없다"
    )
    # 미측정을 0 으로 위장하지 않는다 (계측 4원칙 ②)
    assert "미측정" in _PIPELINE_SRC, (
        "raw conf 가 없을 때 0.0000 으로 찍으면 '측정했더니 0'과 구분되지 않는다"
    )


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
