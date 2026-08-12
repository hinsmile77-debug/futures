# tests/test_458_p0_quiet_window.py
"""[MW0601 458차] P0 모델 선로드 조용한 창 + P3 경과시간 축.

**P0 배경**: 457차 B1은 절반만 성공했다. 참조 스왑은 559ms → 41~84ms로 해결됐지만
워커가 **파이프라인이 도는 그 분에** 떠서 언피클(2.1~2.5초)이 GIL을 물고 있는 동안
메인 스레드가 굶었다. 2026-08-12 실측에서 선로드 분의 S0=1,714~1,904ms이고
S1·S4·S5·S6가 **동시에** 3~8배로 뛰었다(= 자원 경합). CB⑤ 경고 5건 +
Degraded 선제차단 3건(cause=S0). 457차 G9 규칙이 이 경로를 재조사로 지정했다.

**P3 배경**: 조기축소 3건이 전부 진입 후 11~47초였고 2건은 직후 반등했다.
축만 만들고 판정은 하지 않는다 — 표본 3건으로 트리거를 손대면 313차 위반이다.
"""

import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (  # noqa: E402
    MODEL_RELOAD_QUIET_WINDOW,
    VALIDATION_CAMPAIGN,
)

_CFG = dict(MODEL_RELOAD_QUIET_WINDOW)


def _delay(sec, cfg=None):
    """`TradingSystem._model_reload_quiet_delay`를 import 없이 호출.

    main.py는 Qt·Cybos를 끌어와 단위테스트에서 무겁다. 정적 메서드라 소스에서
    떼어 실행하는 대신, 동일 구현을 참조하도록 main 모듈을 lazy import한다.
    """
    import main
    return main.TradingSystem._model_reload_quiet_delay(sec, cfg or _CFG)


# ── P0 핵심: 파이프라인 창을 피하는가 ────────────────────────────────────────

def test_delay_moves_load_off_pipeline_window():
    """워커가 뜨는 전형적 시각(:59~:02)에서 목표 :15로 밀려나는가.

    파이프라인은 매분 :59~:02에 돌고 평상시 233ms에 끝난다. 실측상 워커는 바로
    그 구간에 떴다(11:02:01 스폰 → 11:02:03 완료, 같은 분 S0=1,714ms).
    """
    for spawn_sec in (0.0, 1.0, 2.0):
        d = _delay(spawn_sec)
        start = spawn_sec + d
        assert abs(start - 15.0) < 0.01, \
            ":%05.2f초 스폰 → 시작 :%05.2f초 (목표 :15가 아님)" % (spawn_sec, start)


def test_load_finishes_before_next_pipeline():
    """:15에 시작해 최악의 언피클(실측 최장 2.5초)을 써도 :59 파이프라인 전에 끝난다."""
    start = 0.0 + _delay(0.0)
    worst_load_sec = 2.5
    assert start + worst_load_sec < 55.0, \
        "언피클이 다음 파이프라인 창(:59)에 닿는다: 종료 :%.1f초" % (start + worst_load_sec)


def test_no_wait_when_already_quiet():
    """이미 조용한 구간(목표~latest)이면 기다리지 않는다 — 불필요한 지연 금지."""
    for sec in (15.0, 20.0, 30.0, 44.0):
        assert _delay(sec) == 0.0, ":%.0f초에서 불필요하게 대기한다" % sec


def test_late_spawn_defers_to_next_minute():
    """latest_start(:45)를 지나 떴으면 다음 분 :15로 미룬다(:59 파이프라인 회피)."""
    d = _delay(50.0)
    assert d > 0, ":50초 스폰인데 즉시 로드 — :59 파이프라인과 겹친다"
    landing = (50.0 + d) % 60.0
    assert abs(landing - 15.0) < 0.01, "착지점이 :15가 아니다: :%.2f" % landing


# ── P0 안전장치 ──────────────────────────────────────────────────────────────

def test_delay_never_exceeds_max_wait():
    """어떤 초에서도 max_wait를 넘지 않는다 — 스왑이 영영 밀리면 안 된다."""
    mx = float(_CFG["max_wait_sec"])
    sec = 0.0
    while sec < 60.0:
        assert _delay(sec) <= mx + 1e-9, ":%.1f초에서 상한 초과" % sec
        sec += 0.5


def test_delay_never_negative():
    sec = 0.0
    while sec < 60.0:
        assert _delay(sec) >= 0.0, ":%.1f초에서 음수 대기" % sec
        sec += 0.5


def test_disabled_config_is_immediate_rollback():
    """enabled=False면 즉시 로드 — 457차 동작으로 되돌아간다(롤백 경로)."""
    cfg = dict(_CFG, enabled=False)
    for sec in (0.0, 15.0, 30.0, 50.0):
        assert _delay(sec, cfg) == 0.0, "롤백 설정인데 대기가 발생한다"


def test_swap_latency_unchanged_by_design():
    """대기가 스왑을 지연시키지 않는다는 설계 전제의 회귀 가드.

    종전에도 워커 완료는 *다음 분* S0 drain이 받아갔다(11:02:03 완료 →
    11:02:59 스왑). :15 + 2.5초 = :17.5에 끝나면 같은 분 :59 drain이 그대로
    받으므로 교체 시점이 밀리지 않는다. 이 여유가 사라지면 전제가 깨진다.
    """
    finish = 0.0 + _delay(0.0) + 2.5
    assert finish < 59.0, "선로드가 같은 분 drain(:59)을 놓친다 — 스왑이 1분 밀린다"


def test_config_has_rollback_switch():
    for k in ("enabled", "target_sec", "latest_start_sec", "max_wait_sec"):
        assert k in MODEL_RELOAD_QUIET_WINDOW, "%s 키가 없다" % k
    assert MODEL_RELOAD_QUIET_WINDOW["target_sec"] < \
        MODEL_RELOAD_QUIET_WINDOW["latest_start_sec"], "target > latest 는 모순이다"


# ── P3 경과시간 축 ───────────────────────────────────────────────────────────

class _Pos(object):
    def __init__(self, entry_time):
        self.entry_time = entry_time


def test_elapsed_sec_measures_from_entry():
    import main
    p = _Pos(datetime.datetime.now() - datetime.timedelta(seconds=42))
    v = main._position_elapsed_sec(p)
    assert v is not None and 41.0 <= v <= 44.0, "경과초 계산이 틀렸다: %r" % v


def test_elapsed_sec_none_when_entry_time_missing():
    """미상은 None — 0.0으로 채우면 '즉시 발동' 구간이 오염된다(계측 4원칙 ②)."""
    import main
    assert main._position_elapsed_sec(_Pos(None)) is None
    assert main._position_elapsed_sec(object()) is None


def test_elapsed_sec_never_negative():
    """시계 역행/미래 entry_time에도 음수를 남기지 않는다."""
    import main
    p = _Pos(datetime.datetime.now() + datetime.timedelta(seconds=30))
    assert main._position_elapsed_sec(p) == 0.0


def test_elapsed_watch_is_registered_without_threshold():
    """축은 사전등록하되 **판정 문턱은 없어야** 한다 — 있으면 사후적합 위험."""
    ch = VALIDATION_CAMPAIGN.get("loss_tier1_elapsed_watch")
    assert ch is not None, "경과시간 채널이 사전등록되지 않았다"
    assert ch["min_samples"] >= 20 and ch["min_days"] >= 6
    for banned in ("threshold_sec", "cut_sec", "min_hold_sec", "pass_if"):
        assert banned not in ch, \
            "판정 문턱(%s)이 미리 박혔다 — 데이터를 보기 전에 정하면 안 된다" % banned


def test_elapsed_columns_exist_on_both_channels():
    """tier1·tier2 양쪽에 컬럼이 실제로 생성되는가(마이그레이션 실행 확인)."""
    import sqlite3
    from config.settings import TRADES_DB
    from utils.db_utils import init_all_dbs
    init_all_dbs()
    con = sqlite3.connect(TRADES_DB)
    try:
        for t in ("loss_tier1_qty1_shadow", "loss_tier2_remainder_shadow"):
            cols = {r[1] for r in con.execute("PRAGMA table_info(%s)" % t)}
            assert "elapsed_sec" in cols, "%s에 elapsed_sec가 없다" % t
    finally:
        con.close()


def test_tier2_timestamp_keeps_seconds():
    """[458차 P3] tier2 ts가 분으로 절단되지 않는가 — 425차 수정의 tier1 대칭.

    같은 분 안의 tier1↔tier2 발동 순서가 이 채널 짝의 핵심 관측이다.
    """
    import inspect
    import main
    src = inspect.getsource(main._ts_record_loss_tier2_shadow)
    assert '%H:%M:00' not in src, "tier2 ts가 여전히 분 단위로 절단된다"
    assert '%H:%M:%S' in src


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
