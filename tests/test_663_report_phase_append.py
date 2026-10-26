"""[MW0602 663차 후속 · F-SD-1] 리포트 국면 절 append 자체 검증.

2026-10-26 장중 세션이 증거(`evidence_sd_MW0602-20261026_intra.md`)는 만들고 리포트에
`# 장중(intra)` 절을 넣지 않았다 — 장후 점검에서야 발견됐다.

  P1  증거 有·절 無 → 누락 · 증거 無 → 누락 아님(장중은 원래 생략 가능) · 리포트 자체가 없으면 누락
  P2  헤딩은 줄 전체가 정확히 일치해야 한다(본문 속 언급은 절이 아니다)
  V1  --verify-append: 절 있으면 exit 0 · 없으면 exit 1 · 수집(build)을 부르지 않는다
  B1  실 저장소 2026-10-26 장후 다이제스트 §0 에 장중 절 누락 적신호가 뜬다(DB 없으면 skip)
"""
import datetime
import io
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "shindong-daily-check", "scripts"))

import collect_shindong_evidence as CSE  # noqa: E402

DAY = datetime.date(2026, 10, 26)


def _repo(tmp_path, report=None, phases=()):
    d = tmp_path / "docs" / "정기점검" / "매일점검"
    d.mkdir(parents=True)
    for ph in phases:
        (d / ("evidence_sd_MW0602-20261026_%s.md" % ph)).write_text(u"x", encoding="utf-8")
    if report is not None:
        (d / "MW0602-20261026-점검리포트.md").write_text(report, encoding="utf-8")
    return str(tmp_path)


def test_P1_missing_rules(tmp_path):
    root = _repo(tmp_path, u"# 장전(pre)\n본문\n# 장후(post)\n", phases=("pre", "intra", "post"))
    assert CSE.missing_phase_sections(root, DAY, "MW0602", CSE.PHASE_ORDER) == ["intra"]
    st = CSE.report_phase_sections(root, DAY, "MW0602")
    assert st["intra"] == {"evidence": 1, "section": False}


def test_P1_no_evidence_no_flag(tmp_path):
    root = _repo(tmp_path, u"# 장전(pre)\n", phases=("pre",))
    assert CSE.missing_phase_sections(root, DAY, "MW0602", CSE.PHASE_ORDER) == []


def test_P1_report_absent(tmp_path):
    root = _repo(tmp_path, None, phases=("pre",))
    assert CSE.report_phase_sections(root, DAY, "MW0602")["pre"]["section"] is None
    assert CSE.missing_phase_sections(root, DAY, "MW0602", ("pre",)) == ["pre"]


def test_P2_heading_must_be_whole_line(tmp_path):
    root = _repo(tmp_path, u"# 장전(pre)\n- 리포트에 `# 장중(intra)` 절이 없다\n", phases=("pre", "intra"))
    assert CSE.missing_phase_sections(root, DAY, "MW0602", ("pre", "intra")) == ["intra"]


def _run_verify(monkeypatch, root, phase):
    monkeypatch.setattr(CSE.CE, "find_repo_root", lambda *_a, **_k: root)
    monkeypatch.setattr(CSE.CE, "pc_id", lambda: ("MW0602", "MW0602 (test)"))

    def _no_build(*_a, **_k):
        raise AssertionError("verify-append 는 수집하지 않는다")
    monkeypatch.setattr(CSE, "build", _no_build)
    return CSE.main(["--phase", phase, "--date", DAY.isoformat(), "--pc", "MW0602", "--verify-append"])


def test_V1_verify_append(tmp_path, monkeypatch):
    root = _repo(tmp_path, u"# 장전(pre)\n# 장중(intra)\n장중 점검 생략 — 대상 커밋 0건\n", phases=("pre", "intra"))
    assert _run_verify(monkeypatch, root, "intra") == 0
    assert _run_verify(monkeypatch, root, "post") == 1


def test_B1_real_repo_post_flags_missing_intra():
    if not os.path.exists(os.path.join(ROOT, "data", "db", "shindong.db")):
        pytest.skip("이 환경에 shindong.db 없음")
    if CSE.missing_phase_sections(ROOT, DAY, "MW0602", ("intra",)) != ["intra"]:
        pytest.skip("2026-10-26 장중 증거/리포트 상태가 이 PC 와 다르다")
    txt = CSE.build(ROOT, DAY, "post", "MW0602", "MW0602 (test)")
    sec0 = txt.split("## 1. 설정")[0]
    assert "`# 장중(intra)` 절이 없다" in sec0 and "F-SD-1" in sec0
