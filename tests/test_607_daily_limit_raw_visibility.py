# -*- coding: utf-8 -*-
"""[MW0602 607차 후속 / F-607-1] 가격제한 원값이 파일 레이어(SYSTEM)에 남는가.

배경: 2026-10-02 장후 점검이 `[DailyLimit]` 로그 22거래일 0건을 "상·하한이 0으로만
들어온다"로 해석했으나, 그 로그는 `collection.cybos.realtime_data` 로거로 나가
파일에 도달하지 않는다. 그래서 원값을 SYSTEM 레이어에 샘플링한다.

불변식(라이브 반영 0): 반환값은 종전과 같다 — 로그만 추가됐다.
"""
import logging

import pytest

import collection.cybos.api_connector as ac


class _ListHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.records = []

    def emit(self, record):
        self.records.append(record)


@pytest.fixture
def sys_records():
    h = _ListHandler()
    lg = logging.getLogger("SYSTEM")
    old_level = lg.level
    lg.setLevel(logging.DEBUG)
    lg.addHandler(h)
    ac._OPT_IDX_FAIL_WARNED.clear()
    ac._THROTTLED_INFO_TS.pop("futures_snapshot_daily_limit_raw", None)
    try:
        yield h.records
    finally:
        lg.removeHandler(h)
        lg.setLevel(old_level)
        ac._OPT_IDX_FAIL_WARNED.clear()
        ac._THROTTLED_INFO_TS.pop("futures_snapshot_daily_limit_raw", None)


class _RaisingObj(object):
    def GetHeaderValue(self, idx):
        raise RuntimeError("boom %d" % idx)


class _HeaderObj(object):
    def __init__(self, values):
        self.values = values

    def GetHeaderValue(self, idx):
        return self.values.get(idx, 0)


def _msgs(records, level=None):
    # `_system_info/_warning` 은 SYSTEM 로거 + log_manager 로 두 번 내보낸다 —
    # api_connector 발신분만 센다.
    return [r.getMessage() for r in records
            if r.pathname.replace("\\", "/").endswith("collection/cybos/api_connector.py")
            and (level is None or r.levelno == level)]


def test_1_read_failure_returns_zero_and_warns_once_per_idx(sys_records):
    obj = _RaisingObj()
    assert ac._read_opt_idx(obj, 17) == 0.0
    assert ac._read_opt_idx(obj, 17) == 0.0
    assert ac._read_opt_idx(obj, 18) == 0.0
    warns = [m for m in _msgs(sys_records, logging.WARNING) if "[DailyLimit]" in m]
    assert len(warns) == 2
    assert "17" in warns[0] and "18" in warns[1]


def test_2_none_idx_is_silent(sys_records):
    assert ac._read_opt_idx(_RaisingObj(), None) == 0.0
    assert not [m for m in _msgs(sys_records) if "[DailyLimit]" in m]


def test_3_successful_read_unchanged_and_silent(sys_records):
    assert ac._read_opt_idx(_HeaderObj({13: "1,086.44"}), 13) == pytest.approx(1086.44)
    assert not [m for m in _msgs(sys_records) if "[DailyLimit]" in m]


def _fake_block(data):
    def _run(progid, input_pairs, data_reader):
        return 0, 0, "", data
    return _run


def test_4_snapshot_raw_sample_logged_and_return_unchanged(sys_records, monkeypatch):
    data = {"code": "A056A", "price": 1098.68, "upper_limit": 1173.34,
            "lower_limit": 999.54, "base_price": 1086.44}
    monkeypatch.setattr(ac, "_run_block_request", _fake_block(dict(data)))
    api = ac.CybosAPI.__new__(ac.CybosAPI)
    out = api.request_futures_snapshot("A056A")
    assert out == data                     # 라이브 반영 0 — 반환값 동일
    raws = [m for m in _msgs(sys_records, logging.INFO) if "[DailyLimit-RAW]" in m]
    assert len(raws) == 1
    assert "upper=1173.34" in raws[0] and "base=1086.44" in raws[0]


def test_5_zero_values_are_still_logged(sys_records, monkeypatch):
    # 미측정 ≠ 0 — 0 이어도 남겨야 "0 으로 들어온다"를 파일로 판정할 수 있다.
    monkeypatch.setattr(ac, "_run_block_request", _fake_block(
        {"price": 1098.68, "upper_limit": 0.0, "lower_limit": 0.0, "base_price": 0.0}))
    api = ac.CybosAPI.__new__(ac.CybosAPI)
    api.request_futures_snapshot("A056A")
    raws = [m for m in _msgs(sys_records, logging.INFO) if "[DailyLimit-RAW]" in m]
    assert len(raws) == 1 and "upper=0.00" in raws[0]


def test_6_raw_sample_throttled(sys_records, monkeypatch):
    monkeypatch.setattr(ac, "_run_block_request", _fake_block({"price": 1.0}))
    api = ac.CybosAPI.__new__(ac.CybosAPI)
    api.request_futures_snapshot("A056A")
    api.request_futures_snapshot("A056A")
    raws = [m for m in _msgs(sys_records) if "[DailyLimit-RAW]" in m]
    assert len(raws) == 1


def test_7_failed_request_returns_empty_without_raw(sys_records, monkeypatch):
    def _run(progid, input_pairs, data_reader):
        return 0, 1, "fail", None
    monkeypatch.setattr(ac, "_run_block_request", _run)
    api = ac.CybosAPI.__new__(ac.CybosAPI)
    assert api.request_futures_snapshot("A056A") == {}
    assert not [m for m in _msgs(sys_records) if "[DailyLimit-RAW]" in m]
