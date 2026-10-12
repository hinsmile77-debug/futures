# -*- coding: utf-8 -*-
"""686차 — option_hts 단방향 미러(scripts/sync_option_hts.py) 회귀 가드.

핵심 불변식은 **mtime 보존**이다. foreign_flow_pit_review.py 가 파일 mtime 으로
「그 시점에 존재했나」를 판정하므로, 복사가 mtime 을 바꾸면 PIT 가 조용히 틀어진다.
"""
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import sync_option_hts as S  # noqa: E402

NOW = 2_000_000_000.0


def _mk(d, name, mtime, data=b"x"):
    p = os.path.join(d, name)
    with open(p, "wb") as fh:
        fh.write(data)
    os.utime(p, (mtime, mtime))
    return p


def test_copy_preserves_mtime_and_writes_marker_and_arrivals(tmp_path):
    src, dst = str(tmp_path / "src"), str(tmp_path / "dst")
    os.makedirs(src)
    _mk(src, "261012_1030_D.xls", NOW - 600)
    _mk(src, "_derived_D.json", NOW - 600, b"{}")
    r = S.sync_once(src, dst, now=NOW)
    assert sorted(r["copied"]) == ["261012_1030_D.xls", "_derived_D.json"]
    assert abs(os.path.getmtime(os.path.join(dst, "261012_1030_D.xls")) - (NOW - 600)) < 0.01
    assert any(fn.startswith(S.MARKER_PREFIX) for fn in os.listdir(dst))
    arr = json.load(open(os.path.join(dst, S.ARRIVALS), encoding="utf-8"))
    assert arr["261012_1030_D.xls"]["src_mtime"] == round(NOW - 600, 3)
    assert not [fn for fn in os.listdir(dst) if fn.endswith(".part")]


def test_settling_file_is_skipped_then_copied(tmp_path):
    src, dst = str(tmp_path / "src"), str(tmp_path / "dst")
    os.makedirs(src)
    _mk(src, "261012_D.xls", NOW - 2)
    r = S.sync_once(src, dst, settle=5, now=NOW)
    assert r["settling"] == ["261012_D.xls"] and not r["copied"]
    r = S.sync_once(src, dst, settle=5, now=NOW + 10)
    assert r["copied"] == ["261012_D.xls"]


def test_unchanged_not_recopied_and_changed_recopied(tmp_path):
    src, dst = str(tmp_path / "src"), str(tmp_path / "dst")
    os.makedirs(src)
    p = _mk(src, "261012_P.xls", NOW - 600)
    S.sync_once(src, dst, now=NOW)
    r = S.sync_once(src, dst, now=NOW)
    assert r["unchanged"] == 1 and not r["copied"]
    _mk(src, "261012_P.xls", NOW - 100, b"xy")       # 장후 재내보내기
    r = S.sync_once(src, dst, now=NOW)
    assert r["copied"] == ["261012_P.xls"]
    assert open(os.path.join(dst, "261012_P.xls"), "rb").read() == b"xy"
    assert os.path.exists(p)


def test_deletion_not_propagated_and_foreign_names_ignored(tmp_path):
    src, dst = str(tmp_path / "src"), str(tmp_path / "dst")
    os.makedirs(src)
    p = _mk(src, "261008_D.xls", NOW - 600)
    _mk(src, "~$261008_D.xls", NOW - 600)
    _mk(src, "261008_D.xls.tmp", NOW - 600)
    r = S.sync_once(src, dst, now=NOW)
    assert r["copied"] == ["261008_D.xls"] and r["ignored"] == 2
    os.remove(p)
    S.sync_once(src, dst, now=NOW)
    assert os.path.exists(os.path.join(dst, "261008_D.xls"))


def test_self_source_refused():
    assert S.is_self_source(r"\\DeskTop-MW0601\option_hts", hostname="DESKTOP-MW0601")
    assert S.is_self_source(r"\\desktop-mw0601.local\option_hts", hostname="DeskTop-MW0601")
    assert not S.is_self_source(r"\\DeskTop-MW0601\option_hts", hostname="DeskTop-MW0602")
    assert not S.is_self_source(r"C:\some\local\dir", hostname="DeskTop-MW0602")


def test_unreachable_source_returns_3(tmp_path):
    rc = S.main(["--src", str(tmp_path / "nope"), "--dst", str(tmp_path / "dst")])
    assert rc == 3


def test_derive_refuses_on_mirror_folder():
    """derive_9842_daily 는 _MIRROR_OF_* 표식이 있는 폴더에 쓰지 않는다(단일 기록자)."""
    src = open(os.path.join(_ROOT, "tools", "maekjeom_ladder", "derive_9842_daily.py"), encoding="utf-8").read()
    i_guard = src.find('startswith("_MIRROR_OF_")')
    i_list = src.find("files = L._list_9842_files()")
    assert i_guard != -1 and i_list != -1 and i_guard < i_list
    assert S.MARKER_PREFIX == "_MIRROR_OF_"
