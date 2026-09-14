# -*- coding: utf-8 -*-
"""[MW0601 563차 후속] EOD 재학습 — Phase 2 폴백 + 완료 마커 회귀 가드.

무엇을 고정하는가
-----------------
**① Phase 1 이 짧으면 죽지 말고 Phase 2 로 내려간다.**

`retrain_eod.py` 는 `_load_from_db`(Phase 1, `MIN_TRAIN_BARS`=15,000 단일 게이트)를
직접 부른다. 559차 필터 2종이 백필 오염행을 걷어내자 그 게이트가 처음 구속했고,
2026-09-14 15:50 EOD 가 **모델 한 개도 못 바꾸고** 죽었다:

    45,601 → 백필 -27,718 → 17,883 → 단위 -1,446 → 16,437
           → 미래가격 -1,882 → 14,555 < 15,000 → None → RuntimeError

⚠ **임계를 낮추는 것은 해법이 아니다**(458차 D6). Phase 1 은 전 호라이즌이 같은 X 를
쓰는 전부-아니면-전무 경로라 15,000 은 실제로 1m 이 요구하는 값이다. 대신
호라이즌별 게이트를 가진 Phase 2(`MIN_TRAIN_BARS_PER_HORIZON`)로 내려간다.

**② 완료 마커를 「있으면 성공」으로 읽지 않는다.**

종전 `os.path.exists()` 검사는 실패한 실행이 남긴 **0바이트 마커**를 완료로 읽었다.
⚠ 정직하게 적는다 — 그 0바이트 파일은 **이 수정을 검증하던 테스트 실행이 만든 것**이고
   15:50 프로덕션 실패는 마커 쓰기 전에 죽어 파일을 남기지 않았다. 그래도 결함은
   실재한다: `open(...,"w")` 가 truncate 한 뒤 f-string 평가 중 죽으면 언제든 재현된다.
   그리고 `main.py` 가 **전날 마커를 보고 08:55 PreRetrain 을 건너뛰므로**, 크래시가
   조용히 「어제 EOD 성공」으로 둔갑한다.
"""
from __future__ import print_function

import io
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_SRC = os.path.join(_ROOT, "retrain_eod.py")


def _read():
    with io.open(_SRC, encoding="utf-8") as f:
        return f.read()


# ─────────────────────── ① Phase 2 폴백 ───────────────────────
def test_phase1_shortfall_falls_back_not_raises():
    """`X is None` 에 곧장 raise 하지 않는다 — 그게 2026-09-14 전면 실패의 형태였다."""
    src = _read()
    assert "_phase2_fallback = X is None" in src, "폴백 판정이 없다"
    assert 'raise RuntimeError("DB 데이터 없음' not in src, (
        "Phase 1 미달에 즉시 raise 하는 옛 경로가 살아 있다 — EOD 가 다시 전멸한다")
    assert "[EODFallback]" in src, "폴백 사실을 로그로 남기지 않는다"


def test_fallback_uses_horizon_gated_path():
    """폴백은 반드시 Phase 2(호라이즌별 게이트)여야 한다 — X 를 넘기면 안 된다."""
    src = _read()
    # `if _phase2_fallback:` 은 두 번 나온다(로깅·재학습) — 재학습 쪽을 집는다.
    i = src.find("t2 = time.perf_counter()")
    assert i != -1, "재학습 구간을 못 찾았다"
    i = src.find("if _phase2_fallback:", i)
    j = src.find("        else:", i)
    assert i != -1 and j != -1
    branch = src[i:j]
    assert "use_horizon_features=True" in branch, "폴백이 Phase 2 로 안 간다"
    assert "X=X" not in branch, "폴백인데 전역 X 를 넘긴다 — None 이라 깨진다"


def test_thresholds_untouched():
    """임계는 개정 대상이 아니다 — 경로만 바꿨다(458차 D6)."""
    import importlib
    m = importlib.import_module("learning.batch_retrainer")
    assert m.MIN_TRAIN_BARS == 15000, "Phase 1 임계가 바뀌었다 — 이번 수정 범위가 아니다"
    assert m.MIN_TRAIN_BARS_PER_HORIZON["1m"] == 15000
    assert m.MIN_TRAIN_BARS_PER_HORIZON["3m"] == 5000


# ─────────────────────── ② 완료 마커 ───────────────────────
def test_marker_existence_check_reads_content():
    """`os.path.exists` 만으로 완료 판정하지 않는다."""
    src = _read()
    i = src.find("if os.path.exists(_MARKER_PATH):")
    assert i != -1, "마커 검사 지점이 사라졌다"
    tail = src[i:i + 1200]
    assert "completed:" in tail, "마커 내용을 검사하지 않는다 — 0바이트도 완료로 읽힌다"
    assert "[EODMarker]" in tail, "손상 마커를 만났을 때 사유를 안 남긴다"


def test_marker_write_is_atomic():
    """문자열을 먼저 완성하고 tmp → replace. 열자마자 f-string 을 평가하지 않는다."""
    src = _read()
    assert "_marker_body = (" in src, "마커 본문을 미리 만들지 않는다"
    assert "os.replace(_mk_tmp, _MARKER_PATH)" in src, "원자적 교체가 없다"
    # 옛 형태(열고 그 자리에서 평가)가 남아 있으면 안 된다
    assert 'with open(_MARKER_PATH, "w", encoding="utf-8") as f:\n            f.write(' not in src


def test_marker_records_fallback_not_zero():
    """폴백이면 rows 를 0 으로 적지 않는다 — 미측정과 0 을 구분한다(계측 4원칙 ②)."""
    src = _read()
    assert "phase2_fallback: {'true' if _phase2_fallback else 'false'}" in src
    assert "n/a(phase2_fallback)" in src, "폴백 시 rows/cols 를 숫자로 지어낸다"


# ─────────────────────── ③ 폴백의 부작용 가시화 ───────────────────────
def test_fingerprint_skip_states_its_reason():
    """폴백이면 PSI 학습분포가 안 갱신된다 — 그 사실이 「무해」로 삼켜지면 안 된다."""
    src = _read()
    i = src.find("Phase 2 폴백 — 전역 X 없음")
    assert i != -1, "PSI 스킵 사유가 없다 — AttributeError 가 조용히 삼켜진다"
    assert "FP-CRITICAL" in src[i:i + 400], "매매 영향 유무가 안 적혀 있다"


def test_io_imported_for_marker_read():
    """마커 내용 검사·원자 쓰기가 `io` 를 쓴다 — 임포트 누락 시 런타임에만 터진다."""
    src = _read()
    assert re.search(r"^import io$", src, re.M), "io 임포트가 없다"
