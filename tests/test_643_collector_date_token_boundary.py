# -*- coding: utf-8 -*-
"""[MW0602 643차 후속 F-1 · G-1] 수집기 날짜 토큰 경계 + mtime 의심 표기.

무엇을 막는가
-------------
2026-10-21 장전 점검(이상점 1-1): `logs/retrain_intraday_20260707_102159.log` 의
시각 `102159` 가 `md` 토큰 `1021` 에 부분일치해 **7월 로그가 10-21 「오늘 파일」로**
인벤토리에 묶였다. 사람이 mtime 을 우연히 보고서야 알았다. 40일 역산 실측에서
같은 오탐이 거의 매일 1~3건씩 있었다(전부 `retrain_*` 시각 토큰).

이 파일이 고정하는 불변식
------------------------
① 숫자에 붙은 토큰(`_102159`)은 날짜로 인정하지 않는다
② `_`·`-`·`.`·영문 경계의 정상 파일명은 그대로 잡힌다(회귀 없음)
③ 그룹키 치환도 같은 경계를 쓴다
④ G-1: 판정일보다 2일 이상 **먼저** 기록된 파일만 의심으로 표기(뒤 기록 = 백필은 제외)
⑤ G-1 은 표시만 한다 — 의심 파일을 인벤토리에서 빼지 않는다

실행:
    python -m pytest tests/test_643_collector_date_token_boundary.py
"""
import os
import sys
import shutil
import tempfile
import time
from datetime import date, datetime

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts"))

import collect_evidence as CE

DAY = date(2026, 10, 21)
CFG = {"scan_dirs": ["logs"], "scan_depth": 2, "exclude_patterns": [],
       "max_files_per_group": 5}


def _mk(root, name, mtime_day=DAY):
    p = os.path.join(root, "logs", name)
    with open(p, "w") as f:
        f.write("x\n")
    ts = time.mktime(datetime(mtime_day.year, mtime_day.month, mtime_day.day, 12, 0).timetuple())
    os.utime(p, (ts, ts))
    return p


def _discover(names_with_mtime):
    root = tempfile.mkdtemp(prefix="t643_")
    try:
        os.makedirs(os.path.join(root, "logs"))
        for n, md in names_with_mtime:
            _mk(root, n, md)
        return dict((e["name"], e) for e in CE.discover_files(root, CFG, DAY))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_1_digit_adjacent_md_token_is_rejected():
    """① 2026-10-21 실제 오탐 파일명."""
    got = _discover([("retrain_intraday_20260707_102159.log", date(2026, 7, 7)),
                     ("retrain_stderr_20260702_100857.log", date(2026, 7, 2))])
    assert "retrain_intraday_20260707_102159.log" not in got, got.keys()


def test_2_legit_names_still_match():
    """② 정상 패턴 — 날짜 뒤 `_`·`.`·`-`, 앞 영문/구분자."""
    names = ["20261021_SYSTEM.log", "heartbeat_MW0602_20261021.json",
             "2026-10-21.jsonl", "shindong2_261021.log", "peter_1021.txt",
             "MW0602-20261021-x.log"]
    got = _discover([(n, DAY) for n in names])
    for n in names:
        assert n in got, (n, sorted(got))
    assert got["20261021_SYSTEM.log"]["token"] == "ymd"
    assert got["2026-10-21.jsonl"]["token"] == "y_m_d"


def test_3_group_key_uses_same_boundary():
    """③ 날짜 토큰만 {DATE} 로 바뀌고 숫자열 속 부분은 보존된다."""
    got = _discover([("retrain_intraday_20261021_102159.log", DAY)])
    e = got["retrain_intraday_20261021_102159.log"]
    assert e["group"] == "retrain_intraday_{DATE}_102159.log", e["group"]


def test_4_mtime_suspect_only_when_written_before():
    """④ 앞선 기록만 의심, 백필(뒤 기록)·당일은 아니다."""
    got = _discover([("old_20261021.log", date(2026, 10, 10)),
                     ("backfill_20261021.log", date(2026, 10, 30)),
                     ("today_20261021.log", DAY),
                     ("yday_20261021.log", date(2026, 10, 20))])
    lines = CE.date_token_suspect_lines(list(got.values()))
    body = "\n".join(lines)
    assert "old_20261021.log" in body
    assert "backfill_20261021.log" not in body
    assert "today_20261021.log" not in body
    assert "yday_20261021.log" not in body          # 1일 차는 임계(2) 미만
    assert "의심 1건" in body


def test_5_suspect_is_display_only():
    """⑤ 의심 파일도 인벤토리에 남는다(그룹핑 무관여)."""
    got = _discover([("old_20261021.log", date(2026, 9, 1))])
    assert "old_20261021.log" in got
    assert got["old_20261021.log"]["mtime_before_days"] >= CE.DATE_TOKEN_MTIME_SUSPECT_DAYS


def test_6_no_suspects_renders_nothing():
    assert CE.date_token_suspect_lines([]) == []


if __name__ == "__main__":
    for _k, _f in sorted(globals().items()):
        if _k.startswith("test_") and callable(_f):
            _f()
            print("PASS", _k)
