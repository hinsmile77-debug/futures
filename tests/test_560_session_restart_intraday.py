# -*- coding: utf-8 -*-
"""[MW0602 560차 후속] 0910 리포트 G-1i — 장중 엔진 재기동 감시 채널 회귀 고정.

**관측 전용**이다. 일일 점검 증거 수집기(`collect_evidence.py`)의 §12 파생 지표에만
붙고, 매매 엔진·게이트·수량·주문 경로에는 닿지 않는다. 재기동을 막지도 않는다.

고정하려는 것은 "표에 한 줄이 늘었다"가 아니라, 이 채널이 **조용히 죽는 네 가지
경로**를 각각 막고 있다는 사실이다:

  ① **안 돈 날을 깨끗한 날로 세기** (계측 4원칙 ②)
     재기동 줄이 하나도 없는 날은 휴장·미기동이다. `0(무재기동)` 으로 세면 표본이
     희석되고, 희석되는 방향이 항상 "재기동이 드물다" 쪽이다.
     FP-CRITICAL 이 2개월간 PSI=0.0 이었던 그 형태다.

  ② **바쁜 날만 골라 놓치기**
     `_lines` 기본 상한은 8MB 인데 `_SYSTEM` 로그는 20MB 를 넘는 날이 있다
     (0909 실측 18.3MB). 기본값으로 두면 **재기동이 잦은 날일수록** 미측정이 된다.

  ③ **`변동` 판정에 묻히기**
     §11 적신호는 `고착`·`무기록`·`분기편향`만 올린다. 재기동은 가끔 나는 사건이라
     판정이 `변동` 이 되고, 그러면 신설한 채널이 정작 사건 당일에 침묵한다.

  ④ **늑대소년이 되어 무시당하기**
     0906(20:42)·0907(22:02)·0908(16:20) 실측처럼 장 끝난 뒤 재기동한 날까지 매번
     적신호를 올리면 아무도 안 본다. 값에는 남기되(계측 4원칙 ③) 적신호는
     **장중(09:00~15:10)** 에만 올린다.

근거: `docs/정기점검/매일점검/MW0602-20260910-점검리포트.md` `# 장중(intra)` 1-2 / G-1i.
"""
import datetime
import importlib.util
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ⚠ conftest 는 pytest 경로만 덮는다. `python tests/test_x.py` 직접 실행 대비 두 겹 방어.
from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

# 🔴 이 파일은 `sys.stdout` 을 다시 묶지 않는다 — 의도된 것이다(0909 자동조치 `O-77`).
#    28개 테스트 파일이 import 시점에 `sys.stdout` 을 감싸고 있어 전체 스위트 실행이
#    통째로 불가능하다. 새 파일이 그 관행을 따라가면 안 된다.

_SCRIPT = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check",
                       "scripts", "collect_evidence.py")

_CH = "session_restart_intraday"
_DAY = datetime.date(2026, 9, 10)
_TOK = "20260910"


def _load():
    spec = importlib.util.spec_from_file_location("_ce_560", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ce():
    if not os.path.exists(_SCRIPT):
        pytest.skip("수집기 없음: %s" % _SCRIPT)
    return _load()


# ── 합성 환경 ───────────────────────────────────────────────────────────────
def _line(hhmmss, cause="STARTUP", day="2026-09-10"):
    return ("%s %s [INFO] SYSTEM: [Session] 재기동 #1 | cause=%s"
            % (day, hhmmss, cause))


def _mk_root(tmp_path, lines_by_day, pad_bytes=0):
    """`logs/<YYYYMMDD>_SYSTEM.log` 만 있는 최소 리포 루트."""
    root = str(tmp_path)
    os.makedirs(os.path.join(root, "logs"))
    for day, lines in lines_by_day.items():
        p = os.path.join(root, "logs", "%s_SYSTEM.log" % day)
        with io.open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
            if pad_bytes:
                # 재기동과 무관한 줄로 파일을 부풀린다 — 크기 상한만 시험한다.
                filler = ("%s 09:00:00 [INFO] SYSTEM: [Heartbeat] noise\n" % day[:4]) * 1
                f.write(filler * (pad_bytes // len(filler) + 1))
    return root


def _cfg(ce, **override):
    import copy
    cfg = copy.deepcopy(ce.DEFAULT_CONFIG)
    spec = cfg["derived_indicators"]["indicators"][_CH]
    spec.update(override)
    cfg["derived_indicators"]["indicators"] = {_CH: spec}
    # 합성 표본은 1~2일뿐이라 판정 문턱을 낮춘다(값 자체가 아니라 분류를 본다).
    cfg["derived_indicators"]["min_samples"] = 1
    cfg["derived_indicators"]["min_days"] = 1
    return cfg


def _run(ce, root, cfg, day=_DAY):
    return {r["name"]: r for r in ce.scan_derived_indicators(root, cfg, day)}[_CH]


# ── T1. 채널이 등록돼 있는가 ────────────────────────────────────────────────
def test_t1_channel_registered(ce):
    spec = ce.DEFAULT_CONFIG["derived_indicators"]["indicators"][_CH]
    assert spec["kind"] == "session_restart_intraday"
    assert (spec.get("why") or "").strip(), "why 가 비었다 — 렌더에 근거 없이 실린다"
    assert spec.get("measured_since"), "measured_since 가 없다(계측 4원칙 ②)"
    src = io.open(_SCRIPT, encoding="utf-8").read()
    assert '"session_restart_intraday": _kind_session_restart_intraday' in src, \
        "kind 가 _KINDS 에서 풀렸다 — 설정만 남으면 `무기록` 으로 조용히 굳는다"


# ── T2. 재기동 줄이 없는 날 = 미측정 (계측 4원칙 ②) ────────────────────────
def test_t2_day_without_any_restart_line_is_unmeasured(ce, tmp_path):
    """휴장·미기동을 `0(무재기동)` 으로 세면 표본이 조용히 희석된다."""
    root = _mk_root(tmp_path, {_TOK: [
        "2026-09-10 09:00:00 [INFO] SYSTEM: [Heartbeat] 엔진 줄은 있으나 기동 줄이 없다",
    ]})
    row = _run(ce, root, _cfg(ce))
    assert row["n"] == 0, "기동 기록이 없는 날이 표본으로 잡혔다"
    assert row["today"] is None, "미측정인데 당일값이 생겼다"
    assert all(v != "0(무재기동)" for v, _ in row["dist"]), \
        "안 돈 날을 `0(무재기동)` 으로 세면 거짓 안심이 된다"


# ── T3. 정상일 = 개장 전 기동 1건뿐 ────────────────────────────────────────
def test_t3_premarket_startup_only_is_benign(ce, tmp_path):
    root = _mk_root(tmp_path, {_TOK: [_line("08:41:17")]})
    row = _run(ce, root, _cfg(ce))
    assert row["today"] == "0(무재기동)"
    assert row["today_alert"] is None, "정상일에 적신호가 떴다 — 늑대소년이 된다"
    assert row["verdict"] == "정상고착", row["verdict"]


# ── T4. 장중·장후를 나눠 센다 (계측 4원칙 ③) ──────────────────────────────
def test_t4_splits_intraday_and_after_close(ce, tmp_path):
    root = _mk_root(tmp_path, {_TOK: [
        _line("08:41:17"),          # 개장 전 — 세지 않는다
        _line("09:14:15"),          # 장중
        _line("14:41:03"),          # 장중
        _line("16:20:30"),          # 장 마감 후
    ]})
    row = _run(ce, root, _cfg(ce))
    assert row["today"] == "3건(장중2)", row["today"]


# ── T5. 장후 재기동만 있는 날은 값에는 남되 적신호는 아니다 ────────────────
def test_t5_after_close_restart_is_recorded_but_not_flagged(ce, tmp_path):
    """0906·0907·0908 실측 형태. 값에서 지우면 「장후 재기동은 없었다」가 된다."""
    root = _mk_root(tmp_path, {_TOK: [_line("08:41:17"), _line("22:02:15")]})
    row = _run(ce, root, _cfg(ce))
    assert row["today"] == "1건(장중0)", row["today"]
    assert row["today_alert"] is None, \
        "장 끝난 뒤 재기동까지 적신호를 올리면 채널이 무시당한다"


# ── T6. 장중 재기동은 판정이 `변동` 이어도 적신호로 올라온다 ───────────────
def test_t6_intraday_restart_flags_even_when_verdict_is_variable(ce, tmp_path):
    """§11 은 고착·무기록·분기편향만 올린다 — 사건형 지표는 거기서 묻힌다."""
    root = _mk_root(tmp_path, {
        "20260909": [_line("08:41:17", day="2026-09-09")],      # `0(무재기동)`
        _TOK: [_line("08:41:17"), _line("09:14:15")],           # `1건(장중1)`
    })
    row = _run(ce, root, _cfg(ce))
    assert row["verdict"] == "변동", row["verdict"]
    assert row["today_alert"], "장중 재기동이 있었는데 적신호가 없다"
    assert "1건(장중1)" in row["today_alert"]


# ── T7. 구간 경계 ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("hhmmss,expect", [
    ("08:59:59", "0(무재기동)"),   # 개장 전
    ("09:00:00", "1건(장중1)"),    # 개장 첫 초
    ("15:09:59", "1건(장중1)"),    # 15:10 직전 — 아직 장중
    ("15:10:00", "1건(장중0)"),    # 강제청산 시각 — 장후로 센다
])
def test_t7_window_boundaries(ce, tmp_path, hhmmss, expect):
    root = _mk_root(tmp_path, {_TOK: [_line("08:41:17"), _line(hhmmss)]})
    assert _run(ce, root, _cfg(ce))["today"] == expect


# ── T8. 의도치 않은 재기동(연결 끊김)은 접미로 구분된다 ────────────────────
def test_t8_auto_disconnect_is_marked(ce, tmp_path):
    """사람이 배포하려고 끈 것과 연결이 끊겨 죽은 것은 성격이 다르다."""
    root = _mk_root(tmp_path, {_TOK: [
        _line("08:41:17"),
        _line("10:05:00", cause="AUTO_DISCONNECT"),
        _line("11:00:00", cause="MANUAL"),
    ]})
    row = _run(ce, root, _cfg(ce))
    assert row["today"] == "2건(장중2)·의도외1", row["today"]


# ── T9. 8MB 를 넘는 날을 조용히 놓치지 않는다 ──────────────────────────────
def test_t9_large_system_log_is_still_read(ce, tmp_path):
    """0909 `_SYSTEM` 로그는 18.3MB 였다. 기본 상한(8MB)이면 바쁜 날만 미측정이 된다."""
    root = _mk_root(tmp_path, {_TOK: [_line("08:41:17"), _line("09:14:15")]},
                    pad_bytes=9 * 1024 * 1024)
    size = os.path.getsize(os.path.join(root, "logs", "%s_SYSTEM.log" % _TOK))
    assert size > 8 * 1024 * 1024, "시험 전제가 깨졌다 — 파일이 8MB 를 넘지 않는다"
    assert _run(ce, root, _cfg(ce))["today"] == "1건(장중1)", \
        "8MB 초과 로그가 통째로 빠졌다 — 재기동이 잦은 날일수록 놓친다"


def test_t9b_over_limit_is_unmeasured_not_clean(ce, tmp_path):
    """상한을 넘겨도 `0(무재기동)` 이 되어선 안 된다 — 미측정이어야 한다."""
    root = _mk_root(tmp_path, {_TOK: [_line("08:41:17"), _line("09:14:15")]},
                    pad_bytes=2 * 1024 * 1024)
    row = _run(ce, root, _cfg(ce, max_file_mb=1))
    assert row["today"] is None, "읽지 못한 날이 `0(무재기동)` 으로 둔갑했다"


# ── T10. 다른 날짜 줄을 빌려오지 않는다 ────────────────────────────────────
def test_t10_does_not_borrow_other_days(ce, tmp_path):
    """파일명 토큰과 줄 안의 날짜가 어긋나면 세지 않는다."""
    root = _mk_root(tmp_path, {_TOK: [
        _line("08:41:17"),
        _line("09:14:15", day="2026-09-09"),     # 다른 날짜 줄이 섞여 들어옴
    ]})
    assert _run(ce, root, _cfg(ce))["today"] == "0(무재기동)"


# ── T11. 같은 사건을 두 번 세지 않는다 ─────────────────────────────────────
def test_t11_duplicate_line_counts_once(ce, tmp_path):
    """같은 파일이 두 스캔 경로에 잡혀도 한 사건은 한 번이다."""
    root = _mk_root(tmp_path, {_TOK: [
        _line("08:41:17"), _line("09:14:15"), _line("09:14:15"),
    ]})
    assert _run(ce, root, _cfg(ce))["today"] == "1건(장중1)"


# ── T12. benign 은 무재기동 하나뿐 ─────────────────────────────────────────
def test_t12_benign_holds_only_the_clean_class(ce):
    benign = ce.DEFAULT_CONFIG["derived_indicators"]["indicators"][_CH]["benign"]
    assert list(benign) == ["0(무재기동)"], \
        "재기동이 있는 값을 benign 에 넣으면 그날이 정상으로 분류된다"


# ── T13. 라이브 반영 0 — 이 채널은 읽기만 한다 ─────────────────────────────
def test_t13_channel_is_read_only(ce):
    """관측 전용 불변식. 수집기가 쓰기·주문 경로로 새면 여기서 깨진다."""
    src = io.open(_SCRIPT, encoding="utf-8").read()
    start = src.index("def _kind_session_restart_intraday")
    body = src[start:src.index("    _KINDS = {", start)]
    for bad in ("open(", "sqlite3", "execute", "commit", "os.remove", "shutil"):
        assert bad not in body, "새 kind 안에 부작용 호출이 있다: %s" % bad
    spec = ce.DEFAULT_CONFIG["derived_indicators"]["indicators"][_CH]
    assert "sql" not in spec, "파생 지표인데 DB 질의가 붙었다"


# ── T14. §11 적신호 배선이 살아 있는가 ─────────────────────────────────────
def test_t14_flag_is_wired_into_section_11(ce):
    """행에 `today_alert` 를 만들어놓고 §11 이 안 읽으면 채널은 침묵한다.

    T6 은 **행**까지만 본다 — 렌더 함수는 통짜라 단위시험이 어려워, 배선 자체를
    소스 수준으로 못박는다(T1 의 `_KINDS` 고정과 같은 성격).
    """
    src = io.open(_SCRIPT, encoding="utf-8").read()
    loop = src[src.index("    for r in stuck_rows:"):]
    loop = loop[:loop.index("    # [MW0602 476차 G-4]")]
    assert 'r.get("today_alert")' in loop and 'flags.append(r["today_alert"])' in loop, \
        "§11 이 당일 적신호를 더 이상 올리지 않는다 — 채널이 조용해진다"
