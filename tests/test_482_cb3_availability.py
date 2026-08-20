# -*- coding: utf-8 -*-
"""[MW0601 482차 / F-1·G-1·G-2] CB③ 가용성 계측 — 계측 4원칙 ②·④ 회귀 방지.

## 무엇을 잡는가

1) **"표본 없음"과 "적중 0%"가 같은 값으로 나오는 것** (원칙 ②·④)
   `status_dict()["accuracy_30m"]` 은 분모가 `max(len,1)` 이라 빈 버퍼에서 조용히
   `0.0` 을 돌려준다. 하위호환 때문에 반환 타입은 유지하되 `accuracy_30m_measured`
   가 **반드시 동반**돼야 한다. 그게 없으면 2026-08-20처럼 `acc30m=0.0%` 가 종일
   107분 찍히는데 그것이 무슨 뜻인지 아무도 모른다.

2) **CB③이 판정 가능한 시간을 셀 수 있는가** (G-1)
   `record_accuracy()` 의 평가 분기는 `len(buf) >= CB_ACC30M_MIN_SAMPLES` 를 전제로
   한다. 그 아래면 acc30m 이 임계 미만이어도 CB③은 아무 판정도 하지 않는다.
   2026-08-20: `acc30m < 0.28` 236분(64.0%)인데 HALT 0회 — 로그로 화해 불가였다.

3) **재적합이 CB③ 표본을 얼마나 되감는가** (G-2)
   스케일러 재적합 → `reset_acc30m_buffer()` → 표본 0. 재적합이 잦을수록 CB③은
   판정 불가 상태로 머문다. 두 계측이 서로를 침식하는 관계를 수치로 남긴다.

4) **EOD 저장이 리셋보다 늦어 죽은 값이 박히는 것** (원칙 ④)
   457차 C5(`verified_count` 8거래일 연속 0)와 같은 함정. `daily_close()` 는
   `circuit_breaker.reset_daily()` **전에** 스냅샷을 잡아 넘겨야 한다.

5) **`scaler_daily.cb3_triggered` 사망** — `getattr(cb, "_daily_halt", False)` 는
   실재하지 않는 속성이라 항상 False 였다(실제 이름 `_daily_halt_count`).
   51행 전량 0. CB③ HALT 가 비활성이라 값이 우연히 맞아 보였을 뿐이다.
"""
import io
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.settings import CB_ACC30M_MIN_SAMPLES          # noqa: E402
from safety.circuit_breaker import CircuitBreaker          # noqa: E402


def _fill(cb, n, correct_every=3):
    for i in range(n):
        cb.record_accuracy(i % correct_every == 0, confidence=0.5)


# ---------------------------------------------------------------- 원칙 ②·④
def test_empty_buffer_is_not_reported_as_zero_accuracy():
    cb = CircuitBreaker()
    d = cb.status_dict()
    assert d["cb3_samples"] == 0
    assert d["accuracy_30m_measured"] is False, \
        "빈 버퍼인데 measured=True — '표본 없음'과 '적중 0%'가 다시 섞였다"
    assert d["cb3_ready"] is False


def test_measured_flag_flips_on_first_sample():
    cb = CircuitBreaker()
    cb.record_accuracy(True, confidence=0.5)
    d = cb.status_dict()
    assert d["accuracy_30m_measured"] is True
    assert d["cb3_samples"] == 1
    assert d["cb3_ready"] is False, "표본 1건으로 판정 가능이면 안 된다"


def test_status_dict_carries_every_field_the_log_needs():
    """`[DBG-CB]` 포맷이 소비하는 키가 전부 있어야 한다 — 하나라도 빠지면 로그가 터진다."""
    cb = CircuitBreaker()
    d = cb.status_dict()
    for k in ("accuracy_30m", "accuracy_30m_measured", "cb3_samples",
              "cb3_min_samples", "cb3_ready", "cb3_resets_today",
              "cb3_samples_dropped", "state", "consec_stops", "last_latency"):
        assert k in d, "status_dict 에 %s 가 없다" % k


# ------------------------------------------------------------------- G-1
def test_ready_threshold_matches_the_evaluation_branch():
    """`cb3_ready` 는 `record_accuracy()` 평가 분기의 조건과 같아야 한다."""
    cb = CircuitBreaker()
    _fill(cb, CB_ACC30M_MIN_SAMPLES - 1)
    assert cb.cb3_ready is False
    cb.record_accuracy(True, confidence=0.5)
    assert cb.cb3_samples == CB_ACC30M_MIN_SAMPLES
    assert cb.cb3_ready is True


def test_reset_cooldown_never_binds_above_min_samples():
    """`cb3_ready` 가 쿨다운을 무시해도 되는 전제(쿨다운 15 < 최소표본 30)를 고정한다.

    두 상수의 대소가 뒤집히면 `cb3_ready` 가 거짓 True 를 낸다.
    """
    cb = CircuitBreaker()
    _fill(cb, CB_ACC30M_MIN_SAMPLES)
    cb.reset_acc30m_buffer()
    assert cb._cb3_reset_cooldown_samples < CB_ACC30M_MIN_SAMPLES, \
        "리셋 쿨다운이 최소표본 이상이면 cb3_ready 의 전제가 깨진다"


# ------------------------------------------------------------------- G-2
def test_reset_counts_are_recorded_before_clearing():
    cb = CircuitBreaker()
    _fill(cb, CB_ACC30M_MIN_SAMPLES)
    assert cb.reset_acc30m_buffer() is True
    av = cb.cb3_availability
    assert av["resets_today"] == 1
    assert av["samples_dropped"] == CB_ACC30M_MIN_SAMPLES, \
        "리셋 전에 세지 않으면 0이 기록된다"
    assert av["samples"] == 0 and av["ready"] is False


def test_skipped_reset_is_not_counted():
    """표본 부족으로 스킵된 리셋(277차 기아 방지)은 리셋이 아니다."""
    cb = CircuitBreaker()
    _fill(cb, 5)
    assert cb.reset_acc30m_buffer() is False
    av = cb.cb3_availability
    assert av["resets_today"] == 0
    assert av["samples_dropped"] == 0
    assert av["samples"] == 5, "스킵인데 표본이 사라졌다"


def test_daily_reset_clears_availability_counters():
    cb = CircuitBreaker()
    _fill(cb, CB_ACC30M_MIN_SAMPLES)
    cb.reset_acc30m_buffer()
    cb.reset_daily()
    av = cb.cb3_availability
    assert av["resets_today"] == 0 and av["samples_dropped"] == 0


# --------------------------------------------------- 원칙 ④ (EOD 저장 순서)
def test_daily_close_snapshots_cb3_before_reset():
    """`circuit_breaker.reset_daily()` 가 스냅샷보다 **뒤에** 와야 한다.

    457차 C5 와 같은 함정 — 소스 순서를 직접 본다. 런타임으로 재현하려면
    daily_close() 전체를 띄워야 해서 정적 검사로 고정한다.
    """
    src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i_snap = src.find("_cb3_avail_eod = self.circuit_breaker.cb3_availability")
    i_reset = src.find("self.circuit_breaker.reset_daily()")
    i_use = src.find("cb3_avail=_cb3_avail_eod")
    assert i_snap > 0 and i_reset > 0 and i_use > 0
    assert i_snap < i_reset, "CB③ 스냅샷이 reset_daily() 뒤에 있다 — 죽은 값이 기록된다"
    assert i_reset < i_use, "스냅샷을 쓰는 곳이 리셋보다 앞이면 순서 전제가 틀렸다"


def test_cb3_triggered_no_longer_reads_a_nonexistent_attribute():
    """`_daily_halt` 는 CircuitBreaker 에 없다 — getattr 폴백이 되살아나면 실패."""
    cb = CircuitBreaker()
    assert not hasattr(cb, "_daily_halt"), \
        "속성이 생겼다면 이 테스트의 전제를 다시 볼 것"
    assert hasattr(cb, "_daily_halt_count")
    # 주석은 제외한다 — 이 결함의 경위가 코드 옆에 인용문으로 남아 있다.
    code = [ln for ln in io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8")
            if not ln.lstrip().startswith("#")]
    needle = 'getattr(self.circuit_breaker, "_daily_halt"'
    hit = [ln for ln in code if needle in ln]
    assert not hit, (
        "사망한 getattr 폴백이 되살아났다 — cb3_triggered 가 다시 죽는다: %r" % hit)


# ------------------------------------------------------------- EOD 영속화
def test_scaler_daily_new_columns_default_to_null_not_zero():
    """`ALTER TABLE ... DEFAULT 0` 이면 과거 행이 'ready 0분'으로 위장된다(원칙 ②)."""
    from model import scaler_monitor_db as smd
    for col, typedef in smd._HEALTH_COLS:
        if col.startswith("cb3_"):
            assert "DEFAULT" not in typedef.upper(), \
                "%s 에 DEFAULT 가 붙으면 미측정 과거 행이 0으로 채워진다" % col


def test_insert_daily_writes_null_when_health_absent():
    """구버전 호출부(health=None)는 0이 아니라 NULL 을 남겨야 한다."""
    from model import scaler_monitor_db as smd
    assert smd._int_or_none(None) is None
    assert smd._int_or_none(0) == 0
    assert smd._int_or_none(141) == 141


def test_model_health_line_keeps_legacy_prefix():
    """기존 로그 파서 보호 — CB③ 필드는 **뒤에만** 붙는다(457차 G5 규약)."""
    src = io.open(os.path.join(_ROOT, "model", "scaler_monitor_db.py"),
                  encoding="utf-8").read()
    m = re.search(r'"\[ModelHealth\] date=%s 앙상블유효가동률=%s \| 파이프라인 %d분 \| "', src)
    assert m, "[ModelHealth] 앞머리 포맷이 바뀌었다 — 기존 파서가 깨진다"
    assert '"ConstOut %d회/%d분%s | WeightCollapse %d분 | 장중재학습 %d회%s"' in src
