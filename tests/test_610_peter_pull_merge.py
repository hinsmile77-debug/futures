# -*- coding: utf-8 -*-
"""[MW0602 610차] peter_pull — `_raw/*.jsonl` 은 덮지 않고 트윗 id 로 병합한다.

피터2 수신기가 이 PC 의 `_raw` 에 `src=live`·`seen_at` 으로 적는다. 종전 checkout 은 그 파일을
백업 없이 MW0601 판으로 바꿨다(수신 지연·삭제 탐지 원천이 조용히 바뀜). 불변식:
  · 이 PC 기록은 바이트 그대로 앞에(엔진 RawTail 오프셋 보존)
  · 받은 것 중 없는 id 만 뒤에 — src='pull', 원래 값은 src_origin
  · checkout 이 덮은 뒤에도 스냅샷으로 복원 · 멱등
  · 자체 확정은 도착 판정 뒤에 돈다
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import peter_pull as pp   # noqa: E402

D = "2026-10-08"
PATH = pp.RAW_PREFIX + D + ".jsonl"


def _j(**kw):
    return json.dumps(kw, ensure_ascii=False)


MINE = (_j(id="a", dt="2026-10-08T00:05:00", text="1096 하방 돌파시 매도", src="live",
           seen_at="2026-10-08T09:05:21") + "\n"
        + _j(id="b", dt="2026-10-08T00:05:30", text="1096 매도 체결.", src="live",
             seen_at="2026-10-08T09:05:44") + "\n").encode("utf-8")
PULLED = "\n".join([
    _j(id="b", dt="2026-10-08T00:05:30", text="1096 매도 체결.", src="live",
       seen_at="2026-10-08T09:05:39"),                     # MW0601 수신 시각 — 쓰면 안 된다
    _j(id="c", dt="2026-10-08T06:10:00", text="결산", src="eod"),
]) + "\n"


def _setup(tmp_path, monkeypatch, mine=MINE):
    raw = tmp_path / pp.RAW_PREFIX.replace("/", os.sep)
    raw.mkdir(parents=True)
    if mine is not None:
        (raw / (D + ".jsonl")).write_bytes(mine)
    (raw / (D + ".eod_ids.json")).write_text("[]", encoding="utf-8")
    monkeypatch.setattr(pp, "_ROOT", str(tmp_path))
    monkeypatch.setattr(pp, "_blob", lambda ref, p: PULLED if p == PATH else None)
    return raw / (D + ".jsonl")


def _rows(f):
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def test_1_local_bytes_kept_and_new_ids_appended_as_pull(tmp_path, monkeypatch):
    f = _setup(tmp_path, monkeypatch)
    pp._merge_raw("ref", {PATH: "x"}, pp._snapshot_raw())
    b = f.read_bytes()
    assert b.startswith(MINE)                                 # 바이트 그대로(RawTail 오프셋)
    rows = _rows(f)
    assert [r["id"] for r in rows] == ["a", "b", "c"]
    assert rows[1]["seen_at"] == "2026-10-08T09:05:44"        # 이 PC 의 수신 시각 유지
    assert rows[2]["src"] == "pull" and rows[2]["src_origin"] == "eod"


def test_2_restores_after_checkout_overwrite(tmp_path, monkeypatch):
    f = _setup(tmp_path, monkeypatch)
    snap = pp._snapshot_raw()
    f.write_text(PULLED, encoding="utf-8")                    # checkout 이 덮은 상태
    pp._merge_raw("ref", {PATH: "x"}, snap)
    assert f.read_bytes().startswith(MINE)
    assert [r["src"] for r in _rows(f)] == ["live", "live", "pull"]


def test_3_idempotent(tmp_path, monkeypatch):
    f = _setup(tmp_path, monkeypatch)
    pp._merge_raw("ref", {PATH: "x"}, pp._snapshot_raw())
    once = f.read_bytes()
    pp._merge_raw("ref", {PATH: "x"}, pp._snapshot_raw())
    assert f.read_bytes() == once


def test_4_day_without_local_file_is_all_pull(tmp_path, monkeypatch):
    f = _setup(tmp_path, monkeypatch, mine=None)
    pp._merge_raw("ref", {PATH: "x"}, pp._snapshot_raw())
    rows = _rows(f)
    assert [r["id"] for r in rows] == ["b", "c"]
    assert all(r["src"] == "pull" for r in rows)              # MW0601 의 live 를 이 PC live 로 세지 않는다
    assert rows[0]["src_origin"] == "live"


def test_5_dry_writes_nothing(tmp_path, monkeypatch):
    f = _setup(tmp_path, monkeypatch)
    pp._merge_raw("ref", {PATH: "x"}, pp._snapshot_raw(), dry=True)
    assert f.read_bytes() == MINE


def test_6_raw_scope():
    assert pp._is_raw(PATH)
    assert not pp._is_raw(pp.RAW_PREFIX + D + ".eod_ids.json")  # 삭제 판정 목록은 받는다
    assert not pp._is_raw(pp.SUBDIR + "/" + D + "_tr.txt")      # 검증본 거래줄도 받는다


def test_7_self_build_runs_after_arrival_check():
    s = io.open(os.path.join(ROOT, "tools", "peter_pull.py"), encoding="utf-8").read()
    body = s[s.index("def main():"):]
    assert body.index("_check_today(") < body.index("_self_build()")
    sb = s[s.index("def _self_build():"):s.index("def _rebuild():")]
    assert sb.index("peter2_eod.py") < sb.index("peter_build_day.py")   # _tr 초안 → 적재 순서
