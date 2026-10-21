"""[MW0601 701차] 연구용 장후 사본 — 「원천을 따라가되 잃지 않는다」 규칙 고정."""
import os
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from scripts import research_snapshot as rs  # noqa: E402

CUTOFF = "2026-12-31"


def _src(path, rows, extra_col=False):
    con = sqlite3.connect(path)
    cols = "id INTEGER PRIMARY KEY, ts TEXT NOT NULL, micro_regime TEXT"
    if extra_col:
        cols += ", spread_ticks REAL"
    con.execute("DROP TABLE IF EXISTS ensemble_decisions")
    con.execute("CREATE TABLE ensemble_decisions (%s)" % cols)
    for i, (ts, mr) in enumerate(rows, 1):
        if extra_col:
            con.execute("INSERT INTO ensemble_decisions VALUES (?,?,?,?)", (i, ts, mr, 1.5))
        else:
            con.execute("INSERT INTO ensemble_decisions VALUES (?,?,?)", (i, ts, mr))
    con.commit()
    con.close()


def _run(src, arc, cutoff=CUTOFF):
    con = sqlite3.connect("file:%s" % arc.replace("\\", "/"), uri=True)
    rs._ensure_meta(con)
    con.execute("ATTACH DATABASE ? AS src", (rs._ro_uri(src),))
    ok = rs.snapshot_table(con, "ensemble_decisions", "predictions.db", "ts", cutoff, "t")
    con.close()
    return ok


def _days(arc):
    con = sqlite3.connect(arc)
    r = dict(con.execute("SELECT substr(ts,1,10), COUNT(*) FROM ensemble_decisions GROUP BY 1"))
    con.close()
    return r


def test_add_refresh_and_never_delete(tmp_path):
    src, arc = str(tmp_path / "p.db"), str(tmp_path / "a.db")
    _src(src, [("2026-10-01 09:00:00", "추세"), ("2026-10-02 09:00:00", "횡보")])
    assert _run(src, arc)
    assert _days(arc) == {"2026-10-01": 1, "2026-10-02": 1}

    # 늦게 들어온 행 → 그 날만 갱신
    _src(src, [("2026-10-01 09:00:00", "추세"), ("2026-10-02 09:00:00", "횡보"),
               ("2026-10-02 09:01:00", "횡보")])
    assert _run(src, arc)
    assert _days(arc) == {"2026-10-01": 1, "2026-10-02": 2}

    # 원천이 정리돼 10-01 이 사라지고 10-02 가 줄어도 사본은 그대로다
    _src(src, [("2026-10-02 09:00:00", "횡보")])
    assert _run(src, arc)
    assert _days(arc) == {"2026-10-01": 1, "2026-10-02": 2}


def test_open_day_is_not_copied(tmp_path):
    src, arc = str(tmp_path / "p.db"), str(tmp_path / "a.db")
    _src(src, [("2026-10-01 09:00:00", "추세"), ("2026-10-21 09:00:00", "추세")])
    assert _run(src, arc, cutoff="2026-10-21")      # 10-21 은 아직 마감 전
    assert _days(arc) == {"2026-10-01": 1}


def test_schema_follows_source(tmp_path):
    src, arc = str(tmp_path / "p.db"), str(tmp_path / "a.db")
    _src(src, [("2026-10-01 09:00:00", "추세")])
    assert _run(src, arc)
    _src(src, [("2026-10-01 09:00:00", "추세"), ("2026-10-02 09:00:00", "횡보")], extra_col=True)
    assert _run(src, arc)
    con = sqlite3.connect(arc)
    cols = [r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")]
    new = con.execute("SELECT new_columns FROM snapshot_runs ORDER BY rowid DESC LIMIT 1").fetchone()[0]
    val = con.execute("SELECT spread_ticks FROM ensemble_decisions WHERE ts LIKE '2026-10-02%'").fetchone()[0]
    con.close()
    assert "spread_ticks" in cols and new == "spread_ticks" and val == 1.5


def test_closed_cutoff_boundary():
    import datetime as dt
    assert rs._closed_cutoff(dt.datetime(2026, 10, 21, 15, 34)) == "2026-10-21"
    assert rs._closed_cutoff(dt.datetime(2026, 10, 21, 15, 35)) == "2026-10-22"


def test_wired_into_campaign_chain_before_monthly_cleanup():
    src = open(os.path.join(_ROOT, "scripts", "campaign_steps.py"), encoding="utf-8").read()
    i = src.index('"research_snapshot.py"')
    assert i < src.index("if monthly_cleanup_due(base_dir):")
