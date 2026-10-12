# -*- coding: utf-8 -*-
"""[MW0602 599차 / 0929 장후 자동조치] 일일 점검 수집기 보강 2건 회귀 고정.

**관측 전용**이다. `collect_evidence.py`(점검 도구)만 바뀌고 매매 엔진·게이트·
수량·주문 경로에는 닿지 않는다.

  G-3  장중 재기동에 **재기동 직전 포지션** 축을 붙인다.
       `[BrokerSync] startup sync begin … before=X` 가 재기동 줄보다 0~2초 먼저 찍힌다.
       값(`N건(장중M)`)·판정은 **그대로** 두고 당일 부가정보(`today_detail`)와
       적신호 문구에만 붙인다 — 분포·판정·기존 적신호 정규식이 그 문자열에 걸려 있다.
       짝이 없는 재기동은 `무보유`가 아니라 **미상**이다(계측 4원칙 ②).

  G-4  신동 리포트·메일 실패 WARNING 을 always-quote + §11 표본으로 올린다.
       0929 1-6 은 로그를 전수로 훑은 세션만 발견했다.

근거: `docs/정기점검/매일점검/MW0602-20260929-점검리포트.md` 장중 §4 G-3 · 장후 §4 G-4.
"""
import copy
import datetime
import importlib.util
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

_SCRIPT = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check",
                       "scripts", "collect_evidence.py")
_MAIN = os.path.join(_ROOT, "main.py")

_CH = "session_restart_intraday"
_DAY = datetime.date(2026, 9, 29)
_TOK = "20260929"
_SHINDONG = ("[ShindongReport] 일일 리포트 생성 실패", "[ShindongMail] PDF·메일 실패")


@pytest.fixture(scope="module")
def ce():
    if not os.path.exists(_SCRIPT):
        pytest.skip("수집기 없음: %s" % _SCRIPT)
    spec = importlib.util.spec_from_file_location("_ce_599", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _restart(hhmmss, day="2026-09-29"):
    return "%s %s [INFO] SYSTEM: [Session] 재기동 #1 | cause=STARTUP" % (day, hhmmss)


def _sync(hhmmss, before="FLAT", day="2026-09-29"):
    return ("%s %s [INFO] SYSTEM: [BrokerSync] startup sync begin account=1 code=056A "
            "before=%s" % (day, hhmmss, before))


def _mk_root(tmp_path, lines):
    root = str(tmp_path)
    os.makedirs(os.path.join(root, "logs"))
    with io.open(os.path.join(root, "logs", "%s_SYSTEM.log" % _TOK), "w",
                 encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return root


def _run(ce, root):
    cfg = copy.deepcopy(ce.DEFAULT_CONFIG)
    spec = cfg["derived_indicators"]["indicators"][_CH]
    cfg["derived_indicators"]["indicators"] = {_CH: spec}
    cfg["derived_indicators"]["min_samples"] = 1
    cfg["derived_indicators"]["min_days"] = 1
    return {r["name"]: r for r in ce.scan_derived_indicators(root, cfg, _DAY)}[_CH]


# ── G-3 ────────────────────────────────────────────────────────────────────
def test_g3_real_0929_shape_flat(ce, tmp_path):
    """0929 실측 모양: sync 가 재기동보다 1초 먼저, before=FLAT."""
    root = _mk_root(tmp_path, [_sync("08:41:10"), _restart("08:41:11"),
                               _sync("09:37:46"), _restart("09:37:47")])
    row = _run(ce, root)
    assert row["today"] == "1건(장중1)", "값 문자열이 바뀌었다 — 판정·분포가 흔들린다"
    assert row["today_detail"] == "직전 포지션: 보유 0 · 무보유 1 · 미상 0"
    assert row["today_alert"] and "무보유 1" in row["today_alert"]


def test_g3_held_position_is_counted(ce, tmp_path):
    root = _mk_root(tmp_path, [_sync("08:41:10"), _restart("08:41:11"),
                               _sync("10:15:00", "LONG 2계약 @ 1085.00"),
                               _restart("10:15:02")])
    assert _run(ce, root)["today_detail"] == "직전 포지션: 보유 1 · 무보유 0 · 미상 0"


def test_g3_unpaired_is_unknown_not_flat(ce, tmp_path):
    """계측 4원칙 ②: 짝 없는 재기동을 `무보유`로 세지 않는다."""
    root = _mk_root(tmp_path, [_sync("08:41:10"), _restart("08:41:11"),
                               _restart("11:00:00"),
                               _sync("11:05:00")])      # 창(-60s,+5s) 밖
    assert _run(ce, root)["today_detail"] == "직전 포지션: 보유 0 · 무보유 0 · 미상 1"


def test_g3_after_close_restart_has_no_detail(ce, tmp_path):
    """장후 재기동만 있는 날은 부가정보도 적신호도 없다(기존 동작 보존)."""
    root = _mk_root(tmp_path, [_sync("08:41:10"), _restart("08:41:11"),
                               _sync("15:47:43"), _restart("15:47:43")])
    row = _run(ce, root)
    assert row["today"] == "1건(장중0)"
    assert row["today_detail"] is None and row["today_alert"] is None


def test_g3_detail_does_not_leak_to_other_indicators(ce):
    """부가정보 저장소는 (kind, 날짜) 키 — 다른 파생 지표 행에 새지 않는다."""
    src = io.open(_SCRIPT, encoding="utf-8").read()
    assert '_today_detail[(spec.get("kind"), d)]' in src
    assert '_today_detail.get((spec.get("kind"), today_tok))' in src


# ── G-4 ────────────────────────────────────────────────────────────────────
def test_g4_patterns_registered_and_flagged(ce):
    pats = ce.DEFAULT_CONFIG["always_quote_patterns"]
    src = io.open(_SCRIPT, encoding="utf-8").read()
    flag_block = src[src.index('for pat in ("[Brier] 과신"'):]
    flag_block = flag_block[:flag_block.index("):")]
    for p in _SHINDONG:
        assert p in pats, "always_quote 미등록: %s" % p
        assert p in flag_block, "§11 표본 미배선: %s" % p


def test_g4_patterns_still_match_main_py(ce):
    """main.py 문구가 바뀌면 패턴이 조용히 죽는다 — 원문과 대조."""
    if not os.path.exists(_MAIN):
        pytest.skip("main.py 없음")
    src = io.open(_MAIN, encoding="utf-8").read()
    for p in _SHINDONG:
        assert p in src, "main.py 에서 로그 문구가 사라졌다: %s" % p


def test_g4_digest_quotes_the_line(ce):
    entry = {"rel": "logs/%s_SYSTEM.log" % _TOK, "size": 0, "mtime": 0}
    dg = ce.LogDigest(entry, ce.DEFAULT_CONFIG, _DAY)
    dg._ingest("2026-09-29 15:41:02 [WARNING] SYSTEM: [ShindongReport] 일일 리포트 생성 "
               "실패 (스킵 — 스크립트로 재생성): KeyError('09:00')")
    assert _SHINDONG[0] in dg.quoted


# ── 라이브 반영 0 ─────────────────────────────────────────────────────────
def test_read_only(ce):
    src = io.open(_SCRIPT, encoding="utf-8").read()
    start = src.index("def _kind_session_restart_intraday")
    body = src[start:src.index("    _KINDS = {", start)]
    for bad in ("open(", "sqlite3", "execute", "commit", "os.remove", "shutil"):
        assert bad not in body, "kind 안에 부작용 호출: %s" % bad
