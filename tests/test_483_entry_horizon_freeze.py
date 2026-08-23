# -*- coding: utf-8 -*-
"""[MW0601 483차 후속5] 2026-08-23 주간회의 결정 3건을 고정한다.

## 무엇을 지키는가

| 결정 | 내용 |
|---|---|
| 1 | `ENTRY_HORIZON_B1=3.2` / `_B2=4.4` **동결** — 5주 연속 UPDATE 경보에도 현행 유지 |
| 2 | `EntryHorizonRecalibrator` 경보는 **참고용**이고 판정은 `entry_band_watch` 가 한다 |
| 3 | `entry_band_watch.py` 를 **캠페인 스텝에 편입** — 474차 사전등록에 발화 지점이 없었다 |

## 왜 테스트로 고정하는가

경보는 매주 계속 뜬다. **경보가 뜨는 것과 미조치인 것은 다르다** — 이 구분이 코드에
남아 있지 않으면 다음 점검이 같은 안건을 여섯 번째로 올린다(그것이 이 결정이 나온
직접적 계기다). 상수를 누가 조용히 5.72/8.57 로 바꾸면 이 테스트가 깨져서,
**결정을 되돌린다는 사실을 사람이 인지한 채로** 바꾸게 된다.

⚠ 이 테스트는 "3.2/4.4 가 최적"이라고 주장하지 않는다. 사전등록 판정은
`BAND_UNIFORM`("사전등록 기준에서 이상이 잡히지 않았다")이지 "이상이 없다"가 아니며,
표본 24는 문턱 20의 1.2배로 검정력이 낮다. 지키는 것은 **결정의 존재와 그 근거의
추적 가능성**이다. 재개 조건은 레지스트리 `note` 에 있다.
"""
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ── 결정 1: 경계 동결 ───────────────────────────────────────────────

def test_entry_horizon_boundaries_frozen():
    from config.settings import (ENTRY_HORIZON_LOW_BLOCK, ENTRY_HORIZON_B1,
                                 ENTRY_HORIZON_B2)
    assert (ENTRY_HORIZON_LOW_BLOCK, ENTRY_HORIZON_B1, ENTRY_HORIZON_B2) == (0.8, 3.2, 4.4), (
        "진입 호라이즌 경계가 바뀌었다. 2026-08-23 주간회의가 **동결**을 확정했고, "
        "08-21 권고(5.72/8.57)를 적용하면 실제 진입 220 포지션 중 79.5%가 재배정되며 "
        "그중 142건은 유일한 흑자 구간(3m, 계약당 +17,538원)이 적자 구간(1m, -20,018원)의 "
        "설정으로 내려간다. 바꾸려면 레지스트리 재개 조건을 먼저 충족할 것 — "
        "VALIDATION_CAMPAIGN_DECISIONS['entry_band_watch']")


def test_freeze_decision_is_registered():
    """결정이 레지스트리에 있어야 주간 리포트가 📌 마커로 렌더한다."""
    from config.settings import VALIDATION_CAMPAIGN_DECISIONS as D
    d = D.get("entry_band_watch")
    assert d, "동결 결정이 레지스트리에 없다 — 리포트가 이 안건을 매주 신규로 올린다"
    assert d.get("date") == "2026-08-23"
    assert "동결" in d.get("decision", "")
    # 재개 조건이 적혀 있지 않으면 '영구 동결'이 되어버린다
    assert "재개 조건" in d.get("note", ""), \
        "재개 조건이 없는 동결은 무기한 유예다(CB② 전례)"


def test_constants_carry_the_rationale():
    """상수를 고치러 온 사람이 그 자리에서 근거를 봐야 한다."""
    src = io.open(os.path.join(_ROOT, "config", "settings.py"), encoding="utf-8").read()
    i = src.index("ENTRY_HORIZON_B1")
    block = src[i:i + 3000]
    assert "동결" in block, "상수 옆에 동결 사실이 없다"
    assert "entry_band_watch" in block, "판정 주체가 명시돼 있지 않다"
    assert "다시 열 조건" in block, "경계를 다시 열 조건이 없다"


# ── 결정 2: 경보는 참고용 ───────────────────────────────────────────

def test_recalibrator_alert_is_advisory_not_actionable():
    """문구가 '수동 검토 필요'로 되돌아가면 다음 세션이 또 조치 대상으로 읽는다."""
    src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i = src.index("[EntryHorizonRecal] {_eh_recal['alert']}")
    block = src[i:i + 800]
    assert "참고용 경보(판정 아님)" in block, \
        "경보 문구가 판정처럼 읽힌다 — 2026-08-23 결정 2(a)는 '참고용'이다"
    assert "수동 검토 필요" not in block


def test_recalibrator_alarm_not_disabled():
    """경보 자체는 끄지 않는다 — 374차형 고착(한 버킷 99%) 재발 감시가 원래 목적이다."""
    src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    assert "self.entry_horizon_recalibrator.run_if_due(" in src, \
        "재보정기 호출이 사라졌다 — 참고용으로 강등한 것이지 폐기한 것이 아니다"


# ── 결정 3: 캠페인 스텝 편입 ────────────────────────────────────────

def test_entry_band_watch_has_a_firing_point():
    """사전등록만 하고 발화 지점이 없으면 판정이 영원히 안 나온다.

    474차가 채널을 켜둔 채 스케줄에 연결하지 않아, 2026-08-23 에 사람이 손으로
    돌리기 전까지 **한 번도 판정이 나온 적이 없었다.** `monthly_cleanup.py` 와 같은
    결함이다(2026-05 신설, 발화 지점 없어 미실행).
    """
    src = io.open(os.path.join(_ROOT, "scripts", "campaign_steps.py"), encoding="utf-8").read()
    assert '"entry_band_watch.py"' in src, \
        "entry_band_watch.py 가 캠페인 스텝에 없다 — 사전등록 채널이 죽은 채로 남는다"


def test_channel_enabled_and_thresholds_intact():
    """스텝에 넣어도 사전등록 문턱을 낮추면 무효다(458차 D6)."""
    from config.settings import VALIDATION_CAMPAIGN as V
    c = V.get("entry_band_watch") or {}
    assert c.get("enabled") is True
    assert c.get("min_samples") == 20, "사전등록 문턱을 바꾸면 판정이 무효다"
    assert c.get("band_edges") == [0.8, 3.2, 4.4, 6.0], \
        "band_edges 를 데이터를 본 뒤 바꾸면 사전등록이 무효다"


def test_step_runs_before_the_verdict_report():
    """읽기 전용 채널은 판정 리포트 **앞**에 둔다(캠페인 순서 규약)."""
    src = io.open(os.path.join(_ROOT, "scripts", "campaign_steps.py"), encoding="utf-8").read()
    i_band = src.index('"entry_band_watch.py"')
    # 재학습 스텝보다 **반드시 앞**이어야 한다 — 재학습이 표본·모델을 갱신한 뒤에 재면
    # "이번 주 내내 라이브였던 상태"가 아니라 갱신 후 상태를 재게 된다(410차 규약).
    i_retrain = src.index('"run_shadow_triple_barrier_retrain.py"')
    assert i_band < i_retrain, "재학습보다 뒤에 있으면 이번 주 상태가 아니라 갱신 후 상태를 잰다"
