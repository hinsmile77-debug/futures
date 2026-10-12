# -*- coding: utf-8 -*-
"""[MW0602 609차 후속 / G-1] 옵션체인 「성공 기준」 신선도 노출 — 계측 전용.

2026-10-07 `OptionChainWorker` 가 10:33:38 이후 장 마감까지 한 번도 끝나지 않았다.
예외가 0건이라 어떤 계측에도 안 걸렸고, `[OptionChain] 이전 워커 실행 중 — 스킵`
69건에서 정체 길이를 사람이 줄마다 시각을 빼서 추론해야 했다.

여기서 고정하는 것:
  ① 미성공은 None(미측정) — 0 이나 inf 로 위장하지 않는다(계측 4원칙 ②)
  ② 성공(`opt_chain_available=1`)일 때만 갱신, 실패는 직전 성공 시각을 유지
  ③ 일일 리셋이 성공 시각도 비운다
  ④ 하트비트 부가 필드는 생존 판정 키를 덮지 않고, 공급자 실패가 하트비트를 막지 않는다
  ⑤ 라이브 반영 0 — 폴링 주기(is_due)·피처(get_features)·워치독 발화 판정이 무변경
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collection.options.option_chain_snapshot import OptionChainSnapshot  # noqa: E402
from utils.freeze_watchdog import FreezeWatchdog  # noqa: E402

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OK = {"opt_chain_pcr": 0.449, "opt_chain_available": 1.0}
_FAIL = {"opt_chain_pcr": 0.0, "opt_chain_available": 0.0}


def _snap(tmp_path):
    s = OptionChainSnapshot(chain_cache_path=str(tmp_path / "chain.json"))
    s.initialize()
    return s


def test_1_never_succeeded_is_unmeasured_not_zero(tmp_path):
    s = _snap(tmp_path)
    assert s.seconds_since_success() is None
    hb = s.heartbeat_fields()
    assert hb["option_chain_last_success_ts"] is None
    assert hb["option_chain_stale_sec"] is None
    assert hb["option_chain_stale_measured"] is False


def test_2_success_updates_failure_keeps_previous(tmp_path):
    s = _snap(tmp_path)
    s.on_worker_done(dict(_OK), [])
    first_ts = s.heartbeat_fields()["option_chain_last_success_ts"]
    assert first_ts is not None
    assert s.heartbeat_fields()["option_chain_stale_measured"] is True
    assert 0.0 <= s.seconds_since_success() < 5.0

    s.on_worker_done(dict(_FAIL), [])          # 실패는 성공 시각을 갱신하지 않는다
    assert s.heartbeat_fields()["option_chain_last_success_ts"] == first_ts
    s.on_worker_done({}, [])                   # 결과 없음도 마찬가지
    assert s.heartbeat_fields()["option_chain_last_success_ts"] == first_ts


def test_3_stale_grows_while_no_success(tmp_path):
    s = _snap(tmp_path)
    s.on_worker_done(dict(_OK), [])
    s._last_success_mono = time.monotonic() - 18000.0   # 5시간 전 성공을 재현
    assert s.seconds_since_success() >= 18000.0
    assert s.heartbeat_fields()["option_chain_stale_sec"] >= 18000.0


def test_4_reset_daily_clears_success(tmp_path):
    s = _snap(tmp_path)
    s.on_worker_done(dict(_OK), [])
    s.reset_daily()
    assert s.seconds_since_success() is None
    assert s.heartbeat_fields()["option_chain_stale_measured"] is False


def test_5_live_invariance_snapshot(tmp_path):
    """라이브 반영 0: 성공 시각이 폴링 주기·피처에 영향을 주지 않는다."""
    a, b = _snap(tmp_path), _snap(tmp_path)
    for s in (a, b):
        s.mark_refresh_started()
        s.on_worker_done(dict(_OK), [])
    b._last_success_mono = time.monotonic() - 99999.0   # b만 극단적으로 낡음
    assert a.is_due(1100.0) == b.is_due(1100.0)
    assert a.get_features() == b.get_features()
    a._last_refresh = b._last_refresh = time.monotonic() - 400.0
    assert a.is_due(1100.0) is True and b.is_due(1100.0) is True


def _wd(tmp_path, extra_fn, beat):
    return FreezeWatchdog(
        beat_fn=lambda: beat,
        on_fire=lambda: None,
        check_sec=30.0, stall_sec=180.0, strikes=2,
        window=("00:00", "23:59"),
        fault_log_path=str(tmp_path / "fault.log"),
        ts_heartbeat=False,
        heartbeat_path=str(tmp_path / "hb.json"),
        extra_fn=extra_fn,
    )


def _read(tmp_path):
    with open(str(tmp_path / "hb.json"), encoding="utf-8") as f:
        return json.load(f)


def test_6_heartbeat_carries_extra_fields(tmp_path):
    s = _snap(tmp_path)
    s.on_worker_done(dict(_OK), [])
    wd = _wd(tmp_path, s.heartbeat_fields, time.time())
    wd.check_once()
    p = _read(tmp_path)
    assert p["option_chain_stale_measured"] is True
    assert p["option_chain_last_success_ts"]
    assert "beat_age_sec" in p and p["pid"] == os.getpid()


def test_7_extra_cannot_override_core_keys_and_failure_is_visible(tmp_path):
    wd = _wd(tmp_path, lambda: {"pid": -1, "fired": True, "x": 1}, time.time())
    wd.check_once()
    p = _read(tmp_path)
    assert p["pid"] == os.getpid() and p["fired"] is False and p["x"] == 1

    def _boom():
        raise RuntimeError("공급자 실패")
    wd2 = _wd(tmp_path, _boom, time.time())
    wd2.check_once()
    p2 = _read(tmp_path)
    assert "공급자 실패" in p2["extra_error"]
    assert "beat_age_sec" in p2


def test_8_live_invariance_watchdog_fire_decision(tmp_path):
    """라이브 반영 0: extra_fn 유무·실패가 발화 판정을 바꾸지 않는다."""
    stale_beat = time.time() - 1000.0

    def _boom():
        raise RuntimeError("x")
    results = []
    for extra in (None, lambda: {"a": 1}, _boom):
        wd = _wd(tmp_path, extra, stale_beat)
        results.append((wd.check_once(), wd.check_once(), wd.fired))
    assert results[0] == results[1] == results[2] == (False, True, True)


def test_9_main_wiring_is_log_and_heartbeat_only():
    with open(os.path.join(_ROOT, "main.py"), encoding="utf-8") as f:
        src = f.read()
    body = src.split("def _poll_option_chain", 1)[1].split("\n    def ", 1)[0]
    assert "seconds_since_success()" in body
    # QTimer 슬롯 안 계측은 try 로 감싸야 한다(PyQt5 슬롯 예외 → 프로세스 종료)
    seg = body.split("seconds_since_success()", 1)[0]
    assert "try:" in seg[-400:]
    assert "extra_fn=lambda: self.option_chain_snap.heartbeat_fields()" in src
    # 판정·게이트 경로에서는 쓰지 않는다
    assert src.count("seconds_since_success(") == 1
    assert src.count("heartbeat_fields()") == 2
