# -*- coding: utf-8 -*-
"""[MW0601 566차 / F2-3ⓑ] EOD 폴백이 **건너뛴 호라이즌**을 드러내는지 — 회귀 가드.

무엇을 막는가
-------------
563차 후속이 Phase 1 미달 시 Phase 2 폴백을 넣어 **EOD 전멸**은 막았다.
그러나 그것을 「EOD 복구 완료」로 읽으면 틀린다 — 실측 2026-09-14:

    3m·5m·10m·15m·30m  pkl/meta = 2026-09-14 17:09~17:15   ✅ 교체됨
    1m                 pkl/meta = **2026-09-11 15:50**      ❌ 3일째 그대로

🔴 원인은 표본 부족이 아니라 **테이블 설계**다. Phase 2 는
`raw_features_horizon WHERE horizon=?` 를 읽는데 그 테이블에 `1m` 행은 **사상 0개**다
(2026-03-30 이래 전 기간 0). 1m 은 기본 분봉이라 `raw_features` 에만 있고,
`batch_retrainer.py` 자신이 그렇게 적고 있다.
⇒ 폴백이 걸린 날마다 **1m 모델이 하루씩 늙는다.**

종전에는 그 사실이 `[Retrain-P2] 1m 데이터 부족 0 < 15000` **한 줄**로만 남았다.
그 줄은 "표본이 조금 모자랐다"로 읽히지 "이 호라이즌은 이 경로로 **영원히** 갱신되지
않는다"로는 읽히지 않는다. 계측 4원칙 ④ — 폴백이 쓰였으면 그 사실을 남긴다.

⚠ **동작을 바꾸지 않는다.** 경고 한 줄이고 임계는 그대로다(458차 D6).
"""
from __future__ import print_function

import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_SRC = os.path.join(_ROOT, "retrain_eod.py")


def _read():
    with io.open(_SRC, encoding="utf-8") as f:
        return f.read()


# ─────────────────── ① 미교체 가시화 ───────────────────
def test_fallback_lists_skipped_horizons():
    """폴백이면 **미교체 호라이즌 목록**을 남긴다 — 침묵하지 않는다."""
    src = _read()
    assert "미교체** 호라이즌" in src, "폴백이 건너뛴 호라이즌을 안 남긴다"
    # guard_rejected(346차 모델가드)와 구분해야 한다 — 성격이 전혀 다르다
    assert 'not r.get("guard_rejected")' in src, (
        "가드보류와 구조적 미교체를 같이 세면 경고가 무의미해진다")


def test_one_minute_gets_its_own_structural_warning():
    """1m 은 **구조**라 별도 경고다 — 「표본 부족」으로 읽히면 안 된다."""
    src = _read()
    i = src.find('if "1m" in _hz_res')
    assert i != -1, "1m 전용 경고가 없다"
    block = src[i:i + 900]
    assert "표본 부족이 " in block and "구조" in block, (
        "원인이 구조라는 것이 경고문에 없다 — 다음 사람이 임계를 낮추려 한다")
    assert "raw_features_horizon" in block, "어느 테이블이 비어 있는지 안 적혀 있다"
    assert "458차 D6" in block, "임계를 낮추지 말라는 금지가 빠졌다"


def test_warning_carries_model_age():
    """「갱신 안 됨」만으론 부족하다 — **얼마나 낡았는지**를 함께 찍는다."""
    src = _read()
    assert "_describe_model_age(\"1m\")" in src, "경고가 모델 나이를 안 싣는다"
    assert "def _describe_model_age(" in src


def test_model_age_reads_sidecar_not_acc_txt():
    """나이는 사이드카에서 읽는다 — `acc.txt` 는 교체 시에만 쓰여 유령일 수 있다."""
    src = _read()
    i = src.find("def _describe_model_age(")
    body = src[i:i + 1400]
    assert "_meta.json" in body, "사이드카를 안 읽는다"
    assert "gbm_%s_acc.txt" not in body, "acc.txt 를 읽는다 — 유령 기준선일 수 있다"
    assert "456차" in body, "왜 acc.txt 가 아닌지 근거가 없다"


def test_model_age_failure_is_stated_not_silent():
    """읽기 실패를 조용히 넘기지 않는다 — 미측정과 0을 같게 적지 않는다."""
    src = _read()
    i = src.find("def _describe_model_age(")
    body = src[i:i + 1400]
    assert "학습시각 미상" in body and "학습시각 미기록" in body, (
        "실패를 문자열로 드러내지 않는다 — 계측 4원칙 ②")


# ─────────────────── ② 범위 불변 ───────────────────
def test_behavior_is_unchanged():
    """경고만 추가했다 — 임계·경로는 그대로다."""
    import importlib
    m = importlib.import_module("learning.batch_retrainer")
    assert m.MIN_TRAIN_BARS == 15000
    assert m.MIN_TRAIN_BARS_PER_HORIZON["1m"] == 15000
    src = _read()
    # 563차 후속의 폴백 배선이 살아 있어야 이 경고가 의미를 갖는다
    assert "_phase2_fallback = X is None" in src
    assert "use_horizon_features=True" in src


def test_phase2_really_has_no_1m_rows_by_design():
    """전제 고정 — Phase 2 가 1m 을 못 읽는 것은 **설계 명시**다."""
    with io.open(os.path.join(_ROOT, "learning", "batch_retrainer.py"),
                 encoding="utf-8") as f:
        src = f.read()
    assert "1m은 설계상 raw_features_horizon에 기록되지 않음" in src, (
        "이 전제가 사라졌다면 566차 경고문도 다시 봐야 한다")
