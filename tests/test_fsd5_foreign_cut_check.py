# -*- coding: utf-8 -*-
"""[F-SD-5] 외인 선물 마감 누계 반영 여부 — 경고가 없을 때도 장 마감 뒤 매 회 1줄.

MW0602 671차 장후 리포트 제안(등급 A, 동작 무변경). V-1028-3 류를 DB 쿼리 없이 로그 1줄로 판정한다.
실행: conda run -n py37_32 python -m pytest tests/test_fsd5_foreign_cut_check.py -v
"""
import datetime as dt
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
sys.path.insert(0, os.path.join(_ROOT, "tools", "maekjeom_ladder"))
import shindong2_live as M  # noqa: E402

POST = dt.datetime(2026, 10, 28, 15, 55, 3)


def _st(**fp):
    return dict(date="2026-10-28", foreign=fp)


def test_ok_when_full_close_read():
    line = M.foreign_cut_check(_st(t_cut=None, db_last="15:34"), POST)
    assert line == "[ForeignCutCheck] 15:55:03 t_cut=마감 db_last=15:34 반영=OK"


def test_missing_when_cut_before_db_last():
    line = M.foreign_cut_check(_st(t_cut="15:07", db_last="15:34"), POST)
    assert line.endswith("t_cut=15:07 db_last=15:34 반영=누락")
    assert any("마감 누계 미반영" in w for w in M.source_warnings(dict(_st(t_cut="15:07", db_last="15:34")), POST))


def test_unmeasured_is_not_ok():
    assert M.foreign_cut_check(_st(t_cut=None, db_last=None), POST).endswith("db_last=- 반영=미측정")


def test_silent_before_close_and_on_empty():
    assert M.foreign_cut_check(_st(t_cut="10:30", db_last="10:31"), dt.datetime(2026, 10, 28, 10, 31)) is None
    assert M.foreign_cut_check(dict(empty=True), POST) is None
    assert M.foreign_cut_check(_st(t_cut=None, db_last="15:34"), None) is None


def test_summary_and_log_file_carry_line(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "LIVE_DIR", str(tmp_path))
    line = "[ForeignCutCheck] 15:55:03 t_cut=마감 db_last=15:34 반영=OK"
    st = dict(date="2026-10-28", empty=True, foreign_cut_check=line)
    monkeypatch.setattr(M, "build_state", lambda day, now: (st, {}))
    monkeypatch.setattr(M, "save_new_events", lambda day, ev, now: [])
    monkeypatch.setattr(M, "events_since_record", lambda day, use_ack=False: (None, []))
    monkeypatch.setattr(M, "detect_events", lambda st, t=None: [])
    M.cmd_snapshot("2026-10-28", now=POST)
    M.cmd_snapshot("2026-10-28", now=POST)
    log = open(os.path.join(M.day_dir("2026-10-28"), "foreign_cut_check.log"), encoding="utf-8").read()
    assert log.count("[ForeignCutCheck]") == 2                         # 회차마다 누적 — state.json 처럼 덮이지 않는다
    src = open(os.path.join(_ROOT, "scripts", "shindong2_live.py"), encoding="utf-8").read()
    assert 'L.append(st["foreign_cut_check"])' in src                   # 요약 출력에도 같은 줄
