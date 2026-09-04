# -*- coding: utf-8 -*-
"""[MW0601 532차 후속 / 장후 자동조치] G-1 · G-2 · G-3 회귀 고정.

세 항목 모두 **관측 축만** 바꾼다. 주문·수량·게이트·청산 트리거·진입 판정·임계는
한 줄도 바뀌지 않으며, §4가 그 사실을 코드로 고정한다.

- **G-1** `main.py:_write_session_state()` 가 쓰기 전후의 완료 마커
  (`p8_last_success_date`·`eod_retrain_ok_date`)를 대조해, 이 쓰기가 마커를 지웠으면
  **호출부(파일:행)까지** 로그로 남긴다. 2026-09-03·09-04 이틀 연속 아침에 두 키가
  사라졌는데(0904 리포트 이상점 1-1), 이 함수가 dict 를 통째로 덮어쓰는 구조라
  `_read_session_state()` 없이 만든 dict 를 넘긴 호출부가 있으면 조용히 증발한다.
- **G-2** `[Health]` 경보에 `exceptions_10m` 의 **태그별 소계**를 동봉한다.
  2026-09-04 장중 실측에서 그 값이 0→44 로 올랐는데, 숫자만 남아 무엇을 세는지
  로그만으로 특정할 수 없었다.
- **G-3** EOD 마감 로그에 그날의 자동진입 하한(`min_conf`) 요약을 한 줄 남긴다.
  `mc_history.db` 는 변화폭 0.5%p 이상일 때만 행을 쓰므로, "오늘 임계가 얼마였나"를
  사후에 되짚을 수 없었다(이상점 1-3 판정 유보의 직접 원인).

⚠ F-2(정체불명 외부 진입 발생원)는 여기 없다 — 리포트가 "코드 변경 없음·조사 전용"
  이라 적었고, 확정 수단은 사용자 확인이다.
⚠ F-10(청산 라벨 수정)도 없다 — 청산 트리거 경로 변경이라 사용자·주간회의 결정 사항이다.
"""
from __future__ import annotations

import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_MAIN_SRC_PATH = os.path.join(_ROOT, "main.py")
_ROUTER_SRC_PATH = os.path.join(_ROOT, "strategy", "entry", "time_strategy_router.py")


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def main_src():
    return _read(_MAIN_SRC_PATH)


@pytest.fixture(scope="module")
def router_src():
    return _read(_ROUTER_SRC_PATH)


# ─────────────────────────────────────────────────────────────────────────────
# §1. G-1 — session_state 완료 마커 쓰기 계측
#
# main.py 는 PyQt·Cybos COM 을 최상단에서 적재하므로 테스트에서 import 할 수 없다.
# 이 프로젝트의 관례(test_523 등)대로 소스 텍스트 불변식으로 고정한다.
# ─────────────────────────────────────────────────────────────────────────────

def test_g1_marker_keys_are_exactly_the_two_completion_markers(main_src):
    assert '_SESSION_STATE_MARKER_KEYS = ("p8_last_success_date", "eod_retrain_ok_date")' in main_src, (
        "G-1 이 감시하는 키는 EOD 재학습·P8 스케일러 재적합 완료 마커 두 개다"
    )


def test_g1_pre_snapshot_is_taken_before_the_write(main_src):
    """쓰기 **전** 스냅샷이 실제 파일 쓰기보다 앞서야 소실 판정이 성립한다."""
    i_pre = main_src.find("_pre_markers = None")
    i_write = main_src.find('with open(state_path, "w", encoding="utf-8") as f:')
    assert i_pre != -1 and i_write != -1
    assert i_pre < i_write, "쓰기 뒤에 스냅샷을 잡으면 항상 '소실 0건'이 된다"


def test_g1_unmeasured_is_not_the_same_as_no_markers(main_src):
    """계측 4원칙 ② — 못 읽은 것과 마커가 없는 것을 같은 값으로 표현하지 않는다."""
    assert "if pre_markers is None:" in main_src
    assert "소실 판정 생략" in main_src, "미측정이면 소실 판정을 내리지 않고 그 사실을 남긴다"


def test_g1_logs_only_through_module_logger_not_log_manager(main_src):
    """WARNING 을 log_manager 로 내면 exceptions_10m 에 합산돼 헬스 degraded 를
    자체 유발한다(F-17 전례). 계측이 새 사고를 만들면 안 된다."""
    start = main_src.find("def _log_session_state_write(")
    end = main_src.find("def _restore_auto_shutdown_state(", start)
    assert start != -1 and end > start
    body = main_src[start:end]
    # 주석·독스트링은 log_manager 를 **언급**한다(왜 쓰지 않는지 설명). 금지 대상은 호출이다.
    for call in ("log_manager.system(", "log_manager.health(", "log_manager.log(",
                 "log_manager.trade(", "log_manager.learning("):
        assert call not in body, (
            "G-1 계측은 모듈 로거(logger)로만 남긴다 — log_manager 는 예외밀도에 합산된다: %s"
            % call
        )
    assert "[SessionStateDrop]" in body
    assert "logger.warning(" in body


def test_g1_identifies_the_calling_frame(main_src):
    """기대효과가 '어느 호출(파일:행)이 지웠는지 특정'이므로 호출부 프레임이 필요하다.

    frame 0 = _log_session_state_write, 1 = _write_session_state, 2 = 그 호출부.
    """
    assert "sys._getframe(2)" in main_src
    assert "_fr.f_code.co_filename" in main_src and "_fr.f_lineno" in main_src


def test_g1_instrumentation_runs_only_after_a_successful_write(main_src):
    """저장이 실패했는데 '썼다'고 계측하면 안 된다 — try/except 의 else 절이어야 한다."""
    start = main_src.find("def _write_session_state(")
    end = main_src.find("def _log_session_state_write(", start)
    body = main_src[start:end]
    assert 'logger.warning("[SessionState] save failed: %s", exc)\n        else:\n' in body, (
        "예외가 없었을 때만(else) 계측한다"
    )


def test_g1_never_lets_instrumentation_break_persistence(main_src):
    """계측이 예외를 밖으로 내보내면 세션 상태 저장 경로가 깨진다."""
    start = main_src.find("def _log_session_state_write(")
    end = main_src.find("def _restore_auto_shutdown_state(", start)
    body = main_src[start:end]
    assert 'logger.debug("[SessionState] 쓰기 계측 실패(무해): %s", _log_e)' in body


# ─────────────────────────────────────────────────────────────────────────────
# §2. G-2 — 예외밀도 태그 소계 (실동작 테스트)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def lm():
    from logging_system.log_manager import LogManager
    return LogManager()


def test_g2_tag_subtotals_reconcile_with_level_counts(lm):
    """계측 4원칙 ⑤ — 태그 소계의 총합은 예외밀도(WARNING+ERROR+CRITICAL)와 같다.

    어긋나면 둘 중 하나가 다른 창·다른 제외규칙을 보고 있다는 뜻이다.
    """
    lm.system("[Alpha] 하나", "WARNING")
    lm.system("[Alpha] 둘", "ERROR")
    lm.system("[Beta] 셋", "CRITICAL")
    lm.system("[Beta] 넷", "INFO")          # INFO 는 예외밀도에 안 들어간다
    lm.system("태그없는 경고", "WARNING")

    counts = lm.get_level_counts(since_sec=600, layer="SYSTEM")
    density = counts["WARNING"] + counts["ERROR"] + counts["CRITICAL"]
    tags = lm.get_exception_tag_counts(since_sec=600, layer="SYSTEM")

    assert density == 4
    assert sum(tags.values()) == density
    assert tags["[Alpha]"] == 2
    assert tags["[Beta]"] == 1
    assert tags[lm.NO_TAG_BUCKET] == 1, "태그 없는 메시지를 버리면 합이 어긋난다(계측 4원칙 ③)"


def test_g2_honours_the_same_exclude_prefixes_as_level_counts(lm):
    """제외 태그 규칙이 두 함수에서 갈리면 대사가 무너진다."""
    lm.system("[PipePerf] 느림", "WARNING")
    lm.system("[Alpha] 진짜", "WARNING")

    excl = ["[PipePerf]"]
    counts = lm.get_level_counts(since_sec=600, layer="SYSTEM", exclude_prefixes=excl)
    tags = lm.get_exception_tag_counts(since_sec=600, layer="SYSTEM", exclude_prefixes=excl)

    assert counts["WARNING"] == 1
    assert tags == {"[Alpha]": 1}
    assert "[PipePerf]" not in tags


def test_g2_info_level_never_enters_the_tag_subtotals(lm):
    lm.system("[Gamma] 정보", "INFO")
    assert lm.get_exception_tag_counts(since_sec=600, layer="SYSTEM") == {}


def test_g2_warn_alias_counts_as_warning(lm):
    """get_level_counts 가 WARN→WARNING 으로 정규화하므로 소계도 같아야 한다."""
    lm.system("[Delta] 약칭", "WARN")
    counts = lm.get_level_counts(since_sec=600, layer="SYSTEM")
    tags = lm.get_exception_tag_counts(since_sec=600, layer="SYSTEM")
    assert counts["WARNING"] == 1
    assert tags == {"[Delta]": 1}


def test_g2_window_is_respected(lm):
    """창 밖의 오래된 항목은 세지 않는다 — get_level_counts 와 같은 커트오프 규칙.

    벽시계 해상도에 기대지 않도록 버퍼 항목의 created_at 을 직접 과거로 옮긴다.
    """
    import datetime as _dt
    lm.system("[Eps] 옛날", "ERROR")
    lm.system("[Eps] 지금", "ERROR")
    lm._buffers["SYSTEM"][0].created_at = (
        _dt.datetime.now() - _dt.timedelta(seconds=1200)
    )
    counts = lm.get_level_counts(since_sec=600, layer="SYSTEM")
    tags = lm.get_exception_tag_counts(since_sec=600, layer="SYSTEM")
    assert counts["ERROR"] == 1
    assert tags == {"[Eps]": 1}


def test_g2_malformed_tag_falls_into_the_no_tag_bucket(lm):
    """'['로 시작하지만 닫히지 않는 메시지도 버리지 않는다."""
    lm.system("[닫히지않음 경고", "ERROR")
    tags = lm.get_exception_tag_counts(since_sec=600, layer="SYSTEM")
    assert tags == {lm.NO_TAG_BUCKET: 1}


def test_g2_health_line_carries_the_breakdown(main_src):
    assert "exception_tags_10m = log_manager.get_exception_tag_counts(" in main_src
    assert "exc_tags=" in main_src
    assert "외 %d종" in main_src, "잘라낼 거면 남은 종수를 명시한다(계측 4원칙 ③)"
    assert "exc_tags=미측정" in main_src, "미측정과 0종을 같은 문구로 쓰지 않는다(계측 4원칙 ②)"


# ─────────────────────────────────────────────────────────────────────────────
# §3. G-3 — 일별 min_conf 요약
# ─────────────────────────────────────────────────────────────────────────────

def test_g3_snapshot_returns_every_zone_threshold():
    from strategy.entry.time_strategy_router import (
        _ZONE_PARAMS, get_zone_min_conf_snapshot,
    )
    snap = get_zone_min_conf_snapshot()
    assert set(snap) == set(_ZONE_PARAMS)
    for zone, value in snap.items():
        assert value == pytest.approx(float(_ZONE_PARAMS[zone]["min_confidence"]))


def test_g3_snapshot_is_a_copy_and_cannot_mutate_live_thresholds():
    """읽기 전용이어야 한다 — 계측이 라이브 임계를 바꾸면 그건 매매 정책 변경이다."""
    from strategy.entry.time_strategy_router import (
        _ZONE_PARAMS, get_zone_min_conf_snapshot,
    )
    before = float(_ZONE_PARAMS["STABLE_TREND"]["min_confidence"])
    snap = get_zone_min_conf_snapshot()
    snap["STABLE_TREND"] = 0.999
    assert float(_ZONE_PARAMS["STABLE_TREND"]["min_confidence"]) == pytest.approx(before)


def test_g3_eod_line_is_emitted_from_daily_close(main_src):
    assert "[DynMCDaily]" in main_src
    i_line = main_src.find("[DynMCDaily] %s %s | 종가 zone_min_conf:")
    i_close = main_src.find("def daily_close(self):")
    i_next_def = main_src.find("\n    def ", i_close + 10)
    assert i_close != -1 and i_line != -1
    assert i_close < i_line < i_next_def, "요약은 daily_close() 안에서 나가야 한다"


def test_g3_zero_rows_is_not_reported_as_zero_threshold(main_src):
    """계측 4원칙 ② — 'mc_history 행 0건'은 'base_mc 를 못 쟀다'와 다르다."""
    assert "갱신 0행" in main_src
    assert "base_mc 산출 여부는 이 표에서 미측정" in main_src


def test_g3_router_accessor_documents_read_only(router_src):
    assert "def get_zone_min_conf_snapshot()" in router_src
    assert "읽기 전용" in router_src


# ─────────────────────────────────────────────────────────────────────────────
# §4. 「라이브 반영 0」 불변식 — 세 항목 전부 관측 축만 바꿨는가
# ─────────────────────────────────────────────────────────────────────────────

def test_no_live_effect_health_verdict_inputs_unchanged(main_src):
    """G-2 의 태그 소계는 헬스 판정에 **넘어가지 않는다.**

    넘어가는 순간 계측이 Degraded Mode 를 통해 자동진입 임계를 움직인다.
    """
    call_start = main_src.find("health_level = self._classify_health_level(")
    assert call_start != -1
    call = main_src[call_start:main_src.find(")", call_start)]
    assert "exception_tags_10m" not in call

    sig_start = main_src.find("    def _classify_health_level(")
    assert sig_start != -1
    sig = main_src[sig_start:main_src.find("->", sig_start)]
    assert "exception_tags_10m" not in sig, "판정 함수 시그니처가 바뀌면 계측이 아니다"


def test_no_live_effect_marker_instrumentation_does_not_mutate_state(main_src):
    """G-1 은 저장될 dict 를 건드리지 않는다 — 읽기만 한다."""
    start = main_src.find("def _log_session_state_write(")
    end = main_src.find("def _restore_auto_shutdown_state(", start)
    body = main_src[start:end]
    for forbidden in ("data[", "data.pop", "data.update", "data.setdefault"):
        assert forbidden not in body, "계측이 세션 상태를 수정하면 안 된다: %s" % forbidden


def test_no_live_effect_dynmc_daily_only_reads(main_src):
    """G-3 은 mc_history 를 읽고 zone 스냅샷을 읽을 뿐, 갱신 함수를 부르지 않는다."""
    start = main_src.find("[MW0601 532차 후속 / G-3]")
    end = main_src.find("── STEP 3 재학습 완료 대기", start)
    assert start != -1 and end > start
    block = main_src[start:end]
    assert "get_today_history" in block and "get_zone_min_conf_snapshot" in block
    for forbidden in ("update_dynamic_mc", "insert_mc_change", "min_confidence\"] ="):
        assert forbidden not in block, "G-3 은 읽기 전용이다: %s" % forbidden


def test_no_live_effect_no_order_or_exit_path_touched():
    """이번 변경 3건이 주문·청산·사이징 모듈을 건드리지 않았음을 파일 단위로 고정한다.

    C등급(주문·청산 실행 경로)은 자동조치 대상이 아니다 — 지시문 §2-B.
    """
    import subprocess
    out = subprocess.check_output(
        ["git", "--no-optional-locks", "diff", "--name-only", "HEAD", "--",
         "strategy/entry", "strategy/exit", "strategy/risk", "broker",
         "config/settings.py"],
        cwd=_ROOT,
    ).decode("utf-8", "replace").split()
    # time_strategy_router 는 **읽기 전용 접근자 추가**만 허용한다.
    allowed = {"strategy/entry/time_strategy_router.py"}
    unexpected = [p for p in out if p not in allowed]
    assert not unexpected, "주문·청산·사이징·설정 경로가 변경됐다: %s" % unexpected
