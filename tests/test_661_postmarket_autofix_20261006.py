# -*- coding: utf-8 -*-
"""[MW0601 661차] 2026-10-06 장후 자동조치 — F-1 · F-3 · F-6 · G-3 · A-3.

F-1 — 수집기 `git_change_profile` 이 첫 `git diff --numstat` 실패(대개 타임아웃) 뒤에도
  비슷하게 무거운 `-w --ignore-cr-at-eol` 변형을 또 불렀다. 그날 인덱스락 3회 재발이
  모두 이 연속 호출 구간이었다 → 첫 실패면 두 번째를 부르지 않는다.
F-3 — CLAUDE.md 의 joblib 표기가 requirements.txt 고정값과 어긋났다(1.1.1 vs 1.1.0).
F-6 — `[Retrain] DB 로드 오류: ` 뒤가 빈 문자열(str(e) == "")이라 원인을 몰랐다.
G-3 — 같은 날 런처 재시작 2회 이상을 §11 적신호로 올린다.
A-3 — 리눅스 샌드박스에서 `--out "C:\\Users\\…"` 가 저장소 루트에 파일 하나로 써졌다.
"""

from __future__ import annotations

import importlib.util
import io
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_COLLECTOR = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                          "scripts", "collect_evidence.py")


def _load_collector():
    spec = importlib.util.spec_from_file_location("collect_evidence_661", _COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── F-1 ──────────────────────────────────────────────────────────────────

def test_f1_second_diff_skipped_after_first_timeout(monkeypatch):
    ce = _load_collector()
    calls = []

    def fake_run_git(root, args, timeout=25):
        calls.append(list(args))
        if args[:1] == ["status"]:
            return " M a.py\n?? b.md"
        if args[:2] == ["diff", "--numstat"]:
            return "(git 타임아웃 25s — 자식 종료함) git " + " ".join(args)
        return ""

    monkeypatch.setattr(ce, "run_git", fake_run_git)
    out = ce.git_change_profile("ignored")
    diff_calls = [c for c in calls if c[:1] == ["diff"]]
    assert diff_calls == [["diff", "--numstat"]], "첫 diff 실패 뒤 두 번째 변형을 부르면 안 된다"
    assert out["measured"] is False
    assert out["real"] is None, "미측정을 0 으로 위장하면 안 된다"
    assert out.get("second_diff_skipped") is True
    assert "생략" in out["fail_reason"] and "타임아웃" in out["fail_reason"]


def test_f1_success_path_unchanged(monkeypatch):
    ce = _load_collector()
    calls = []

    def fake_run_git(root, args, timeout=25):
        calls.append(list(args))
        if args[:1] == ["status"]:
            return " M a.py\n M b.md"
        if args == ["diff", "--numstat"]:
            return "1\t1\ta.py\n2\t2\tb.md"
        if args[:2] == ["diff", "--numstat"]:
            return "1\t1\ta.py"
        if args[:1] == ["config"]:
            return "true"
        return ""

    monkeypatch.setattr(ce, "run_git", fake_run_git)
    out = ce.git_change_profile("ignored")
    assert len([c for c in calls if c[:1] == ["diff"]]) == 2
    assert out["measured"] is True
    assert (out["tracked_changed"], out["real"], out["code"], out["eol"]) == (2, 1, 1, 1)
    assert "second_diff_skipped" not in out


# ── F-3 ──────────────────────────────────────────────────────────────────

def test_f3_claude_md_joblib_matches_requirements():
    req = io.open(os.path.join(ROOT, "requirements.txt"), encoding="utf-8").read()
    pinned = re.search(r"^joblib==([\d.]+)", req, re.M).group(1)
    md = io.open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").read()
    row = re.search(r"\| scikit-learn \|[^\n]*joblib ([\d.]+)", md)
    assert row, "CLAUDE.md 운영 환경 표에서 joblib 행을 못 찾았다"
    assert row.group(1) == pinned


# ── F-6 ──────────────────────────────────────────────────────────────────

def test_f6_retrain_db_load_error_keeps_type_and_stack():
    src = io.open(os.path.join(ROOT, "learning", "batch_retrainer.py"), encoding="utf-8").read()
    lines = [l for l in src.splitlines() if "[Retrain] DB 로드 오류" in l]
    assert len(lines) == 1
    assert "{e!r}" in lines[0], "빈 str(e) 예외도 타입이 남아야 한다"
    assert "exc_info=True" in lines[0]


# ── G-3 ──────────────────────────────────────────────────────────────────

_LAUNCHER = (
    "[AUTO-RESTART] main.py 가 132분 실행됨 -- 일시적 크래시, 카운터 초기화.\n"
    "[AUTO-RESTART] #1 시도 (시각=1052) -- 10초 후 재시작...\n"
    "[AUTO-RESTART] main.py 재시작...\n"
    "[AUTO-RESTART] main.py 가 67분 실행됨 -- 일시적 크래시, 카운터 초기화.\n"
    "[AUTO-RESTART] #1 시도 (시각=1159) -- 10초 후 재시작...\n"
)


def test_g3_section_carries_launcher_restarts(tmp_path, monkeypatch):
    import datetime
    import utils.wer_crash as wc
    monkeypatch.setattr(wc, "wer_app_faults",
                        lambda day: {"measured": False, "reason": "test", "events": []})
    (tmp_path / "logs" / "Mireuk_batch").mkdir(parents=True)
    (tmp_path / "logs" / "Mireuk_batch" / "launcher_20261006_084000_1.log").write_text(
        _LAUNCHER, encoding="utf-8")
    ce = _load_collector()
    out = []
    fau = ce.wer_crash_section(str(tmp_path), {}, datetime.date(2026, 10, 6), out)
    assert isinstance(fau, dict)
    assert [r["at"] for r in fau["launcher_restarts"]] == ["10:52", "11:59"]


def test_g3_launcher_unmeasured_is_none_not_zero(tmp_path, monkeypatch):
    import datetime
    import utils.wer_crash as wc
    monkeypatch.setattr(wc, "wer_app_faults",
                        lambda day: {"measured": False, "reason": "test", "events": []})
    (tmp_path / "logs").mkdir()
    ce = _load_collector()
    fau = ce.wer_crash_section(str(tmp_path), {}, datetime.date(2026, 10, 6), [])
    assert fau["launcher_restarts"] is None


def test_g3_flag_wired_in_section_11():
    src = io.open(_COLLECTOR, encoding="utf-8").read()
    i11 = src.index("# ---- 11. 자동 적신호 ----")
    assert "launcher_restarts" in src[i11:], "§11 이 재시작 횟수를 읽지 않는다"
    assert "len(_rst) >= 2" in src[i11:]


# ── A-3 ──────────────────────────────────────────────────────────────────

def _load_month_report():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    spec = importlib.util.spec_from_file_location(
        "peter_month_report_661", os.path.join(ROOT, "tools", "peter_month_report.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("out,bad", [
    ("C:\\Users\\82108\\PycharmProjects\\Peter\\x.md", os.sep != "\\"),  # 리눅스에선 이름 하나
    ("C:Users82108PycharmProjectsPeterx.md", True),                       # bash 가 \ 를 먹은 꼴
    ("CUsers82108PycharmProjectsPeterx.md", True),
    ("C:/Users/82108/PycharmProjects/Peter/x.md", False),
    ("report.md", False),
    ("docs/peter/x.md", False),
])
def test_a3_mangled_out_path(out, bad):
    assert _load_month_report().mangled_out_path(out) is bad


def test_a3_main_refuses_without_writing(tmp_path, monkeypatch):
    mr = _load_month_report()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mr, "build", lambda m, db: pytest.fail("build 까지 가면 안 된다"))
    monkeypatch.setattr(sys, "argv", ["peter_month_report.py", "2026-10",
                                      "--out", "CUsers82108PycharmProjectsPeterx.md"])
    with pytest.raises(SystemExit) as ei:
        mr.main()
    assert ei.value.code == 2
    assert os.listdir(str(tmp_path)) == []
