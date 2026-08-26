# -*- coding: utf-8 -*-
"""[MW0602 498차 후속] 인덱스락 2점 샘플(A-1) + 지침서 정본↔사본 대조(B-1·B-2).

배경(2026-08-26): 점검 지침서 앱 사본이 6일 낡은 채 돌아 ① 2026-08-23 신설
git 호출 규약을 모른 채 맨손 `git status` 를 쳐 `.git/index.lock` 을 남겼고
② 그 사본에 장후 제4·5부가 통째로 없었다. 그리고 그 사고를 고친 커밋
`c308a99` 자신이 **정본만** 갱신해 드리프트를 당일 재발시켰다(0826 `1-16`).

이 테스트가 고정하는 것은 **라이브가 거의 밟지 않는 분기**다 —
락 존재/미측정, `rev:` 미갱신, 사본 불일치. 평상시 실행은 전부 「없음·정합」
경로만 지나가므로, 나머지 분기는 여기서만 검증된다.

🔴 **실 저장소의 `.git` 을 절대 건드리지 않는다** — 전부 `tempfile.mkdtemp()`.

실행: python tests/test_498_lock_and_skill_rev.py   (pytest 불필요)
"""
import io
import os
import shutil
import sys
import tempfile
import time
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check")
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))

import collect_evidence as CE  # noqa: E402

FAILURES = []

# 콘솔이 cp949 여도 진단 문구(이모지 포함)가 깨지지 않게 한다.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _safe(s):
    try:
        return str(s)
    except Exception:
        return repr(s)


def check(name, fn):
    try:
        fn()
        print("PASS %s" % name)
    except AssertionError as e:
        FAILURES.append(name)
        print("FAIL %s: %s" % (name, _safe(e)))
    except Exception as e:  # 예외도 실패로 센다 - 조용히 통과시키지 않는다
        FAILURES.append(name)
        print("FAIL %s: 예외 %r" % (name, e))


def _mklock(root, age_sec=0.0, size=0):
    d = os.path.join(root, ".git")
    if not os.path.isdir(d):
        os.makedirs(d)
    p = os.path.join(d, "index.lock")
    with io.open(p, "wb") as f:
        f.write(b"x" * size)
    if age_sec:
        old = time.time() - age_sec
        os.utime(p, (old, old))
    return p


# ── A-1 인덱스락 ─────────────────────────────────────────────────────────────
def t1_lock_absent_is_two_point():
    """둘 다 없음 -> 「없음」 + 적신호 0. 2점 확인 문구가 붙는다."""
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, ".git"))
        st = CE.git_lock_state(tmp)
        assert st["measured"] is True and st["exists"] is False, st
        lines, flags = CE.lock_report(st, CE.git_lock_state(tmp))
        assert not flags, "락이 없는데 적신호가 났다: %s" % flags
        assert "없음" in lines[0] and "2점" in lines[0], lines
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t2_lock_preexisting_is_not_blamed_on_collector():
    """시작부터 있었으면 「이 실행이 만든 것이 아니다」로 귀속하고 나이를 낸다.

    0821 사고(53.5시간)가 이 분기다. **나이가 문구에 실려야** 스테일 판단이 된다.
    """
    tmp = tempfile.mkdtemp()
    try:
        _mklock(tmp, age_sec=53.5 * 3600, size=0)
        start = CE.git_lock_state(tmp)
        assert start["exists"] is True and start["size"] == 0
        lines, flags = CE.lock_report(start, CE.git_lock_state(tmp))
        body = "\n".join(lines)
        assert "실행 전부터" in body, body
        assert "아니다" in body, "수집기 소행으로 오귀속됐다: %s" % body
        assert "53.5시간" in body, "나이가 문구에 없다 - 스테일 판단 불가: %s" % body
        assert flags and "실행 전부터" in flags[0], flags
        # 계측은 읽기 전용이다 - 파일이 지워지지 않았는지 확인
        assert os.path.isfile(os.path.join(tmp, ".git", "index.lock")), \
            "계측이 락을 지웠다 - 읽기 전용 규약 위반"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t3_lock_created_during_run_is_blamed_on_collector():
    """시작에 없다가 생겼으면 이 실행 소행으로 올린다(규약 위반 신호)."""
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, ".git"))
        start = CE.git_lock_state(tmp)
        _mklock(tmp)
        lines, flags = CE.lock_report(start, CE.git_lock_state(tmp))
        body = "\n".join(lines)
        assert "이 수집 실행이 남겼다" in body, body
        assert "no-optional-locks" in body, "원인 지목이 없다: %s" % body
        assert flags and "남겼다" in flags[0], flags
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t4_unmeasured_is_not_absent():
    """🔴 계측 4원칙 ② - stat 실패는 「없음」이 아니라 「미측정」이고 적신호다."""
    lines, flags = CE.lock_report(
        {"measured": False, "why": "Operation not permitted"},
        {"measured": False, "why": "Operation not permitted"})
    body = "\n".join(lines)
    assert "미측정" in body, body
    assert "「락 없음」이 아니다" in body, "미측정을 없음과 구분하지 않았다: %s" % body
    assert flags, "미측정인데 적신호가 없다 - 조용히 지나간다"


def t5_start_snapshot_none_degrades_to_unmeasured():
    """시작 스냅샷이 없으면(직접 build 호출 등) 「일치」가 아니라 「미측정」이다."""
    lines, flags = CE.lock_report(None, {"measured": True, "exists": False})
    assert "미측정" in "\n".join(lines)
    assert flags


def t6_fmt_age_units():
    assert CE.fmt_age(30) == "30초"
    assert CE.fmt_age(600) == "10분"
    assert CE.fmt_age(3 * 3600 + 21 * 60) == "3시간 21분"   # 0824 사고
    assert CE.fmt_age(None) == "?"


# ── B-1 / B-2 지침서 세대 ────────────────────────────────────────────────────
def t7_rev_marker_parsed_with_suffix():
    """같은 날 여러 세대를 접미사로 구분한다(`2026-08-26b`)."""
    m = CE._REV_RX.search("<!-- rev: 2026-08-26b (494차 + 498차) -->")
    assert m and m.group(1) == "2026-08-26b", m
    assert CE._rev_date("2026-08-26b") == "2026-08-26"
    assert CE._rev_date(None) is None


def t8_live_repo_declared_rev_is_consistent():
    """실 저장소 정본이 지금 정합인가 - 읽기 전용.

    🔴 이 검사가 깨지면 `rev:` 를 안 올린 것이다. B-2(사본 대조)가 「일치」를
    찍어도 내용이 다를 수 있으므로 **먼저** 고쳐야 한다.
    """
    CE._SKILL_REV_CLAIM = None
    st = CE.skill_rev_state(ROOT, date.today())
    assert st["exists"], "정본을 찾지 못했다: %s" % st["path"]
    assert st["declared"], "정본에 `rev:` 마커가 없다"
    body = "\n".join(st["verdicts"])
    assert "rev 미갱신" not in body and "미갱신**" not in body, \
        "정본 rev 미갱신 - 사본 대조가 무력화된다: %s" % body
    assert len(st["refs"]) == 5, "참조 파일 5종을 다 훑지 않았다: %s" % st["refs"]


def t9_missing_claim_is_unmeasured_not_match():
    """🔴 미제출을 「일치」로 치지 않는다 - 계측 4원칙 ②."""
    CE._SKILL_REV_CLAIM = None
    st = CE.skill_rev_state(ROOT, date.today())
    body = "\n".join(st["verdicts"])
    assert "미제출" in body, body
    assert "미측정 ≠ 일치" in body, "미제출과 일치를 구분하는 문구가 없다: %s" % body
    assert "일치**" not in body.split("미제출")[0][-200:], "미제출인데 일치를 찍었다"
    assert not any("드리프트" in f for f in st["flags"]), \
        "미제출을 드리프트로 오판했다 - 모르는 것과 틀린 것은 다르다"


def t10_stale_claim_is_flagged_and_escalated():
    """사본이 낡으면 §2 판정 + §11 적신호 **둘 다** 나온다."""
    CE._SKILL_REV_CLAIM = "2026-08-20"
    try:
        st = CE.skill_rev_state(ROOT, date.today())
        body = "\n".join(st["verdicts"])
        assert "사본 드리프트" in body, body
        assert "정본을 따를 것" in body, "처분 지시가 없다: %s" % body
        assert st["flags"] and "드리프트" in st["flags"][0], \
            "§2 에만 찍고 §11 로 올리지 않았다 - 읽는 사람이 놓친다"
    finally:
        CE._SKILL_REV_CLAIM = None


def t11_matching_claim_passes():
    CE._SKILL_REV_CLAIM = None
    declared = CE.skill_rev_state(ROOT, date.today())["declared"]
    CE._SKILL_REV_CLAIM = declared
    try:
        st = CE.skill_rev_state(ROOT, date.today())
        assert "일치" in "\n".join(st["verdicts"])
        assert not st["flags"], st["flags"]
    finally:
        CE._SKILL_REV_CLAIM = None


def t12_cli_exposes_skill_rev_with_copy_warning():
    """`--skill-rev` 가 CLI 에 있고, 도움말이 **정본 복사 금지**를 경고한다.

    이 경고가 빠지면 세션이 정본에서 값을 복사해 검사가 영구히 「일치」가 된다 -
    검사가 있는데 거짓 안심을 주는, 가장 나쁜 상태다.
    """
    src = io.open(os.path.join(SKILL_DIR, "scripts", "collect_evidence.py"),
                  encoding="utf-8").read()
    assert '"--skill-rev"' in src, "CLI 인자가 없다"
    i = src.find('"--skill-rev"')
    seg = src[i:i + 700]
    assert "정본에서 복사하지 말 것" in seg, "복사 금지 경고가 도움말에 없다"
    assert "미제출" in seg, "미제출 의미가 도움말에 없다"


def t13_start_snapshot_taken_before_other_git_calls():
    """시작 스냅샷이 `find_repo_root` 직후 - 다른 git 호출보다 **먼저** 잡히는가.

    순서가 뒤집히면 수집기 자신이 만든 락을 「원래 있었다」로 오귀속한다.
    """
    src = io.open(os.path.join(SKILL_DIR, "scripts", "collect_evidence.py"),
                  encoding="utf-8").read()
    i_main = src.find("def main(")
    seg = src[i_main:]
    i_root = seg.find("root = find_repo_root(start)")
    i_snap = seg.find("_LOCK_AT_START = git_lock_state(root)")
    i_build = seg.find("text = build(")
    assert i_root >= 0 and i_snap >= 0 and i_build >= 0, "배선을 찾지 못했다"
    assert i_root < i_snap < i_build, \
        "스냅샷이 root 확정 직후·build 이전이 아니다 (root=%d snap=%d build=%d)" % (
            i_root, i_snap, i_build)


def main():
    check("T1  락 없음 = 2점 확인", t1_lock_absent_is_two_point)
    check("T2  락 선존재 = 수집기 소행 아님 + 나이", t2_lock_preexisting_is_not_blamed_on_collector)
    check("T3  실행 중 생성 = 수집기 소행", t3_lock_created_during_run_is_blamed_on_collector)
    check("T4  미측정 ≠ 없음 (계측 4원칙 ②)", t4_unmeasured_is_not_absent)
    check("T5  시작 스냅샷 없음 -> 미측정", t5_start_snapshot_none_degrades_to_unmeasured)
    check("T6  나이 단위 표기", t6_fmt_age_units)
    check("T7  rev 접미사 파싱", t7_rev_marker_parsed_with_suffix)
    check("T8  실 저장소 정본 rev 정합(β2)", t8_live_repo_declared_rev_is_consistent)
    check("T9  미제출 ≠ 일치", t9_missing_claim_is_unmeasured_not_match)
    check("T10 사본 드리프트 §2+§11", t10_stale_claim_is_flagged_and_escalated)
    check("T11 사본 일치", t11_matching_claim_passes)
    check("T12 CLI 복사금지 경고", t12_cli_exposes_skill_rev_with_copy_warning)
    check("T13 스냅샷 선취 순서", t13_start_snapshot_taken_before_other_git_calls)
    if FAILURES:
        print("FAILED: %s" % ", ".join(FAILURES))
        sys.exit(1)
    print("ALL PASS (13/13)")


if __name__ == "__main__":
    main()
