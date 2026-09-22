# -*- coding: utf-8 -*-
"""[MW0601 620차] 프로세스 종료 3축 대사 회귀 가드.

이 테스트가 고정하는 것은 파싱 정확도가 아니라 **판정의 겸손함**이다.

2026-09-22 장후 F-3 이 「무흔적 종료」의 원인을 못 좁힌 이유는 계측이 없어서가
아니라 **안 걸어본 축이 있어서**였다(계측 4원칙 ⑤). 그 축을 붙이면서 새로 생기는
위험은 정반대다 — WER 에 기록이 없다는 것만 보고 *"크래시가 아니었다"* 로 확정해
버리는 것. 그래서 아래 테스트는

  · 「미측정」과 「0건」이 **같은 값으로 표현되지 않는가** (계측 4원칙 ②)
  · WER 미측정일 때 판정이 **「정상」이 아니라 「판정불가」로 떨어지는가**
  · 이 계측이 **라이브 매매 경로에 0줄도 닿지 않는가**

를 건다. 실제 PowerShell 을 부르지 않는다(`_runner` 주입) — CI·타 PC 에서도 돈다.
"""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.wer_crash import (  # noqa: E402
    crash_fault_events,
    launcher_processes,
    reconcile,
    wer_app_faults,
)

# 2026-09-22 실측 형태 그대로. 미륵이 PID 22668(09:41:56 Qt5Core 크래시) 1건 +
# 미륵이가 아닌 python.exe 3건.
_REAL_OUT = (
    "###OK###\n"
    "09:41:57|python.exe|Qt5Core.dll|c0000409|588c|C:\\py37_32\\python.exe\n"
    "09:28:55|python.exe|ucrtbase.dll|c0000409|6aac|C:\\py37_32\\python.exe\n"
    "07:36:23|python.exe|ucrtbase.dll|c0000409|5ce0|C:\\py37_32\\python.exe\n"
)


# ---------------------------------------------------------------- 파싱

def test_parses_properties_line_and_converts_hex_pid():
    r = wer_app_faults("2026-09-22", _runner=lambda d: _REAL_OUT)
    assert r["measured"] is True
    assert len(r["events"]) == 3
    # 시간 오름차순으로 정렬해 돌려준다.
    assert [e["time"] for e in r["events"]] == ["07:36:23", "09:28:55", "09:41:57"]
    qt = r["events"][-1]
    assert qt["module"] == "Qt5Core.dll"
    assert qt["code"] == "c0000409"
    assert qt["pid"] == 0x588C == 22668, "PID 는 16진 문자열을 10진으로 바꿔야 런처 로그와 맞는다"


def test_zero_events_is_measured_not_unmeasured():
    """🔴 계측 4원칙 ② — 「이벤트 0건」과 「재지 못했다」는 다른 값이다."""
    r = wer_app_faults("2026-09-22", _runner=lambda d: "###OK###\n")
    assert r["measured"] is True, "완료 표식이 왔으면 0건이라도 '측정됨'이다"
    assert r["events"] == []


def test_missing_ok_marker_is_unmeasured():
    """완료 표식이 없으면 조회 자체가 안 돈 것 — 빈 출력과 구분한다(계측 4원칙 ④)."""
    r = wer_app_faults("2026-09-22", _runner=lambda d: "")
    assert r["measured"] is False
    assert r["events"] == []
    assert r["reason"], "미측정에는 반드시 사유가 붙는다"


def test_malformed_lines_are_skipped_not_crashed():
    out = "###OK###\ngarbage\n|||\n09:41:57|python.exe|Qt5Core.dll|c0000409|588c|C:\\p.exe\n"
    r = wer_app_faults("2026-09-22", _runner=lambda d: out)
    assert r["measured"] is True
    assert len(r["events"]) == 1


# ---------------------------------------------------------------- 런처 / crash_fault

_LAUNCHER = (
    "2026-09-22 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\\crash_fault.log"
    " PID=22668 | 행감지=30s all_threads=True\n"
    "[AUTO-RESTART] main.py 가 62분 실행됨 -- 일시적 크래시, 카운터 초기화. \n"
    "[AUTO-RESTART] #1 시도 (시각=0942) -- 10초 후 재시작... \n"
    "2026-09-22 09:42:27 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\\crash_fault.log"
    " PID=27016 | 행감지=30s all_threads=True\n"
)

_CRASH_FAULT = (
    "[START] 2026-09-22T09:42:27  PID=27016  Python 3.7.13 32bit  RSS=178MB\n"
    "[TS] 2026-09-22T15:08:05 beat_age=0s watching=True strikes=0\n"
    "[CLEAN EXIT] 2026-09-22T15:08:08  PID=27016\n"
    "[CLEAN EXIT] 2026-09-21T11:11:11  PID=99999\n"  # 다른 날 — 걸러져야 한다
)


@pytest.fixture
def fake_root(tmp_path):
    d = tmp_path / "logs" / "Mireuk_batch"
    d.mkdir(parents=True)
    (d / "launcher_20260922_084001_14358.log").write_text(_LAUNCHER, encoding="utf-8")
    (tmp_path / "logs" / "crash_fault.log").write_text(_CRASH_FAULT, encoding="utf-8")
    return str(tmp_path)


def test_launcher_processes_extracts_pids_and_restart_kind(fake_root):
    r = launcher_processes(fake_root, "20260922")
    assert r["measured"] is True
    assert [s["pid"] for s in r["starts"]] == [22668, 27016]
    assert r["restarts"] == [{"at": "09:42", "kind": "일시적 크래시"}]


def test_launcher_missing_is_unmeasured(tmp_path):
    r = launcher_processes(str(tmp_path), "20260922")
    assert r["measured"] is False and r["starts"] == []


def test_crash_fault_filters_by_day(fake_root):
    r = crash_fault_events(fake_root, "2026-09-22")
    assert r["measured"] is True
    assert 99999 not in r["by_pid"], "다른 날 행이 섞이면 대사가 조용히 틀어진다"
    assert r["by_pid"][27016]["clean_exit"] == "15:08:08"


# ---------------------------------------------------------------- 대사 판정

def test_reconcile_three_verdicts(fake_root):
    lau = launcher_processes(fake_root, "20260922")
    fau = crash_fault_events(fake_root, "2026-09-22")
    wer = wer_app_faults("2026-09-22", _runner=lambda d: _REAL_OUT)
    rec = reconcile(lau, wer, fau)

    by_pid = dict((r["pid"], r) for r in rec["rows"])

    # 22668 — WER 기록 있음 -> 네이티브 크래시 확정
    assert "네이티브 크래시 확정" in by_pid[22668]["verdict"]
    assert "Qt5Core.dll" in by_pid[22668]["verdict"]

    # 27016 — WER 없음 + CLEAN EXIT 있음 -> 정상 종료 기록을 남긴 종료
    #   (2026-09-22 15:08 이상점 1-7 이 정확히 이 경우다)
    assert by_pid[27016]["wer"] is None
    assert "정상 종료 기록을 남김" in by_pid[27016]["verdict"]
    assert "크래시 확정" not in by_pid[27016]["verdict"]


def test_reconcile_hardkill_when_no_wer_and_no_clean_exit(fake_root):
    """그날 로그가 **있는데** 그 PID 만 종료 기록이 없으면 — 그때가 하드킬이다."""
    lau = launcher_processes(fake_root, "20260922")
    wer = wer_app_faults("2026-09-22", _runner=lambda d: "###OK###\n")
    # 그날 다른 PID 는 기록이 있다 = 로그가 그 구간을 덮고 있다(covered=True).
    fau = {"measured": True, "reason": "", "covered": True,
           "by_pid": {999: {"start": "09:00:00", "clean_exit": "10:00:00"}}}
    rec = reconcile(lau, wer, fau)
    for r in rec["rows"]:
        assert "하드킬/무흔적" in r["verdict"]


def test_rolled_away_crash_fault_day_is_not_called_hardkill(fake_root):
    """🔴 2026-09-17 재생에서 실제로 발생한 오판.

    `crash_fault.log` 는 롤링 파일이라 며칠 지나면 그 날짜 구간이 통째로 사라진다.
    그때 「정상종료 기록 없음」으로 읽으면 **그날 전 프로세스가 하드킬로 둔갑**한다 —
    파일이 짧아진 것을 사건으로 보고하는 것이고, 계측 4원칙 ② 위반이다.
    """
    lau = launcher_processes(fake_root, "20260922")
    wer = wer_app_faults("2026-09-22", _runner=lambda d: "###OK###\n")
    fau = {"measured": True, "reason": "", "covered": False, "by_pid": {}}
    rec = reconcile(lau, wer, fau)
    for r in rec["rows"]:
        assert "미측정" in r["verdict"]
        assert "하드킬" not in r["verdict"]


def test_crash_fault_covered_flag(fake_root):
    assert crash_fault_events(fake_root, "2026-09-22")["covered"] is True
    # 그날 행이 하나도 없는 날 — 파일은 읽혔지만 구간이 없다.
    r = crash_fault_events(fake_root, "2026-01-01")
    assert r["measured"] is True and r["covered"] is False and r["by_pid"] == {}


def test_unmeasured_wer_must_not_read_as_normal(fake_root):
    """🔴 이 테스트가 이 파일의 핵심이다.

    WER 을 못 쟀을 때 판정이 「정상」이나 「크래시 아님」으로 떨어지면,
    그것은 사전등록 확인 수단 하나를 침묵으로 대체하는 것이다
    (SKILL.md §0 함정① 정합성 게이트).
    """
    lau = launcher_processes(fake_root, "20260922")
    fau = crash_fault_events(fake_root, "2026-09-22")
    wer = wer_app_faults("2026-09-22", _runner=lambda d: "")  # 미측정
    rec = reconcile(lau, wer, fau)
    assert rec["rows"], "행 자체는 나와야 한다"
    for r in rec["rows"]:
        assert "판정불가" in r["verdict"]
        assert "미측정" in r["verdict"]
        assert "아님" not in r["verdict"], "미측정을 '예외 아님'으로 단정하면 안 된다"


def test_others_excludes_mireuk_pids(fake_root):
    lau = launcher_processes(fake_root, "20260922")
    fau = crash_fault_events(fake_root, "2026-09-22")
    wer = wer_app_faults("2026-09-22", _runner=lambda d: _REAL_OUT)
    rec = reconcile(lau, wer, fau)
    other_pids = set(e["pid"] for e in rec["others"])
    assert 22668 not in other_pids, "미륵이 프로세스가 '남의 크래시'로 새면 귀속이 뒤집힌다"
    assert other_pids == {0x6AAC, 0x5CE0}


def test_others_empty_when_wer_unmeasured(fake_root):
    """미측정이면 '남의 크래시 0건'도 주장하지 않는다."""
    lau = launcher_processes(fake_root, "20260922")
    fau = crash_fault_events(fake_root, "2026-09-22")
    rec = reconcile(lau, wer_app_faults("x", _runner=lambda d: ""), fau)
    assert rec["others"] == []


# ---------------------------------------------------------------- 배선 / 라이브 무영향

_COLLECTOR = os.path.join(
    ROOT, ".claude", "skills", "mireuk-daily-check", "scripts", "collect_evidence.py"
)


def test_collector_section_is_wired():
    """정의만 하고 build() 에 안 걸면 죽은 계측이 된다(FP-CRITICAL·TOX 섀도 계열)."""
    src = open(_COLLECTOR, encoding="utf-8").read()
    assert "def wer_crash_section(" in src
    assert "wer_crash_section(root, cfg, day, L)" in src, "build() 등록 누락"


def test_no_live_trading_path_imports_this():
    """라이브 반영 0 — 이 계측은 점검 도구 전용이다.

    매매 프로세스가 import 하기 시작하면 '읽기 전용 포렌식' 전제가 깨지고,
    장중에 PowerShell 을 부르는 경로가 생긴다(CB⑤ 지연 5초 위험).
    """
    offenders = []
    for rel in ("main.py", "strategy", "model", "learning", "collection", "execution"):
        p = os.path.join(ROOT, rel)
        files = []
        if os.path.isfile(p):
            files = [p]
        elif os.path.isdir(p):
            for dirpath, _dn, fns in os.walk(p):
                files += [os.path.join(dirpath, f) for f in fns if f.endswith(".py")]
        for f in files:
            try:
                src = open(f, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            if "wer_crash" in src:
                offenders.append(os.path.relpath(f, ROOT))
    assert not offenders, "라이브 경로가 포렌식 모듈을 import 했다: %s" % offenders


def test_module_does_not_write_or_clear_event_log():
    """읽기 전용 불변식 — 이벤트 로그를 지우는 명령이 섞이면 증거가 사라진다."""
    src = open(os.path.join(ROOT, "utils", "wer_crash.py"), encoding="utf-8").read()
    for bad in ("Clear-EventLog", "Remove-EventLog", "wevtutil cl", "Write-EventLog",
                "New-EventLog", "Limit-EventLog"):
        assert bad not in src, "쓰기/삭제 명령 발견: %s" % bad
