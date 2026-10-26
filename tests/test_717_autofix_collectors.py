# -*- coding: utf-8 -*-
"""[MW0601 717차 후속 / 장후 자동조치] 점검 수집기 3건 — 회귀 고정.

· 10-23 F-2 — 미륵 수집기 `entry_source_of()` 에 「신동」 출처. 2026-10-23 신동 실집행
  5건이 `horizon=` 이 없어 전부 「추정」으로 세어졌다.
· 10-26 F-1 — 신동 수집기 날짜를 KST 로. Cowork 샌드박스(UTC) 08:52 KST 실행이
  `evidence_sd_MW0601-20261025_pre.md` 를 만들었다.
· 10-26 G-5 — 신동 수집기에 9842 수집 상태 유형별 분해(`SKIP_QUOTA` 가 안 보였다).

수정 범위는 **점검 수집기(리포트 도구)뿐**이다 — 매매 코드는 한 줄도 안 바뀐다.
"""
from __future__ import annotations

import importlib.util
import os
import re
import sqlite3
from datetime import datetime, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CE_PATH = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check", "scripts", "collect_evidence.py")
SD_PATH = os.path.join(ROOT, ".claude", "skills", "shindong-daily-check", "scripts",
                       "collect_shindong_evidence.py")


def _load(path, name):
    if not os.path.exists(path):
        pytest.skip("수집기 본체 없음 — 스킬 미설치 환경")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ce():
    return _load(CE_PATH, "_collect_evidence_717")


@pytest.fixture(scope="module")
def sd():
    return _load(SD_PATH, "_collect_shindong_evidence_717")


@pytest.fixture(scope="module")
def pats(ce):
    p = ce.DEFAULT_CONFIG["day_summary_patterns"]
    return {k: re.compile(p[k]) for k in ("entry", "shindong_entry", "peter2_entry")}


def _rec(pat, line):
    m = pat.search(line)
    assert m is not None, "미매칭: %s" % line
    d = dict(m.groupdict())
    d["_raw"] = line
    d["hhmm"] = line[11:16]
    return d


# ── 실제 로그 원문 (logs/20261023_TRADE.log · _SYSTEM.log 에서 그대로) ─────────
T = "2026-10-23 %s [INFO] TRADE: "
SDX = T % "09:03:10" + ("[ShindongExec] 진입 R2 SHORT 3계약 @834.22(규칙가 833.94) 손절 844.58 "
                        "1차 812.60 최종 765.62 — R2|09:02|-1")
POS_SD = T % "09:03:11" + "[Position] 진입 SHORT 3계약 @ 834.22 | 손절=844.58 1차=-9165.78(×1.00) 2차=-9165.78"
POS_ENG = T % "10:08:00" + ("[Position] 진입 LONG 1계약 @ 847.06 | 손절=842.01 1차=848.74(×0.50) "
                            "2차=852.11 horizon=3m hurst=neutral")
SYS_REPLAY = ("2026-10-23 09:03:10 [INFO] SYSTEM: [Shindong] R2 매도 OPEN 진입 833.94(09:02) 손절 844.58 "
              "1차 812.60 최종 765.62 | 1차 보유 최종 보유 | 순 +0원 | 상품 wk_mon · 탐지 09:03:10")


# ── 10-23 F-2 ────────────────────────────────────────────────────────────────
def test_f2_shindong_exec_marks_source(ce, pats):
    merged = {"entry": [_rec(pats["entry"], POS_SD), _rec(pats["entry"], POS_ENG)],
              "shindong_entry": [_rec(pats["shindong_entry"], SDX)]}
    assert ce.count_entry_sources(merged) == {"엔진": 1, "피터2": 0, "신동": 1, "가상": 0, "추정": 0}
    positions, _ = ce.assemble_positions(merged)
    assert [q["src"] for q in positions] == ["신동", "엔진"]


def test_f2_without_marker_still_unmeasured(ce, pats):
    """표식이 없으면 종전대로 「추정」 — 신동으로 짐작하지 않는다(4원칙 ②)."""
    assert ce.count_entry_sources({"entry": [_rec(pats["entry"], POS_SD)]})["추정"] == 1


def test_f2_pairing_tolerance(ce, pats):
    far = SDX.replace("09:03:10", "09:03:14")
    merged = {"entry": [_rec(pats["entry"], POS_SD)],
              "shindong_entry": [_rec(pats["shindong_entry"], far)]}
    assert ce.count_entry_sources(merged)["신동"] == 0


def test_f2_replay_status_line_not_matched(pats):
    """SYSTEM 의 재생 상태줄은 매분 반복된다 — 신동 실집행 표식으로 잡으면 안 된다."""
    assert pats["shindong_entry"].search(SYS_REPLAY) is None
    assert _rec(pats["shindong_entry"], SDX)["rule"] == "R2"


# ── 10-26 F-1 ────────────────────────────────────────────────────────────────
class _UtcNight(datetime):
    """컨테이너 시계 = UTC 2026-10-25 23:52 (= KST 10-26 08:52)."""

    @classmethod
    def now(cls, tz=None):
        base = datetime(2026, 10, 25, 23, 52, tzinfo=timezone.utc)
        return base.astimezone(tz) if tz else base.replace(tzinfo=None)


def test_f1_now_kst_on_utc_container(sd, monkeypatch):
    monkeypatch.setattr(sd, "datetime", _UtcNight)
    assert sd.now_kst() == datetime(2026, 10, 26, 8, 52)


def test_f1_main_default_date_is_kst(sd, monkeypatch, tmp_path):
    monkeypatch.setattr(sd, "datetime", _UtcNight)
    seen = {}

    def fake_build(root, day, phase, pcid, pclabel):
        seen["day"] = day
        return "x\n"

    monkeypatch.setattr(sd, "build", fake_build)
    out = tmp_path / "e.md"
    assert sd.main(["--phase", "pre", "--pc", "MW0601", "--out", str(out)]) == 0
    assert seen["day"].isoformat() == "2026-10-26"


def test_f1_explicit_date_untouched(sd, monkeypatch, tmp_path):
    seen = {}
    monkeypatch.setattr(sd, "build", lambda r, d, p, i, l: seen.setdefault("day", d) and "x\n")
    sd.main(["--phase", "post", "--date", "2026-10-23", "--pc", "MW0601", "--out", str(tmp_path / "e.md")])
    assert seen["day"].isoformat() == "2026-10-23"


# ── 10-26 G-5 ────────────────────────────────────────────────────────────────
def _mk_db(root, rows):
    d = root / "data" / "db"
    d.mkdir(parents=True)
    con = sqlite3.connect(str(d / "strike_investor.db"))
    con.execute("CREATE TABLE strike_investor_flow_status (trade_date TEXT, ok INTEGER, msg TEXT)")
    con.executemany("INSERT INTO strike_investor_flow_status VALUES (?,?,?)", rows)
    con.commit()
    con.close()


def test_g5_status_breakdown(sd, tmp_path):
    rows = ([("2026-10-26", 1, None)] * 6 + [("2026-10-26", 0, "SKIP_QUOTA remain=1")] * 3
            + [("2026-10-26", 0, "EMPTY")] + [("2026-10-26", 0, "db: locked")]
            + [("2026-10-23", 0, "BLOCKED x")])
    _mk_db(tmp_path, rows)
    from datetime import date
    assert sd.strike_status(str(tmp_path), date(2026, 10, 26)) == {"ok": 6, "SKIP_QUOTA": 3, "EMPTY": 1, "기타": 1}
    assert sd.strike_status(str(tmp_path), date(2026, 10, 24)) == {}


def test_g5_missing_db_is_unmeasured(sd, tmp_path):
    from datetime import date
    assert sd.strike_status(str(tmp_path), date(2026, 10, 26)) is None
