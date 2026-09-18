# -*- coding: utf-8 -*-
"""[MW0601 606차 후속] 장후 자동조치 — G-3(점검 보고서 양식 고정 문구)의 회귀 고정.

무엇을 고쳤나
-------------
* **G-3** 장후 점검이 `.git/index.lock` 을 STALE 로 확정해도, 그 조치를
  「사용자 조치」 절에 적는 문장을 **매번 세션이 새로 지어내고 있었다.**
  리눅스 샌드박스(코웍) 세션은 마운트 경유 `unlink` 가 `EPERM` 으로 거부돼
  **락을 회수할 권한이 원천적으로 없으므로**(SKILL.md §0), 이 조치는 구조적으로
  항상 사용자 몫이다. 구조적으로 고정된 항목이면 문구도 고정돼야 한다 —
  `references/report_template.md` §9p-3 에 고정 블록을 넣었다.

왜 테스트가 필요한가 — **문서가 도구의 종료코드를 인용한다**
------------------------------------------------------------
고정 문구는 `--check` 의 종료코드 의미(**STALE=2 · 판정보류(HOLD)=3**)를 인용한다.
`scripts/git_lock_guard.py` 가 그 값을 바꾸면 **문서만 조용히 거짓이 된다** —
크래시도 경고도 없이, 다음 점검 세션이 HOLD 상태의 락을 지우도록 안내할 수 있다.
그 조합은 실행 중인 git 의 인덱스를 깨뜨린다. 그래서 이 파일은 문구의 존재뿐
아니라 **문구와 도구의 정합성**을 함께 건다(SKILL.md §0 함정① 정합성 게이트).

라이브 반영 0
-------------
G-3 은 점검 보고서 **양식 문서 한 곳**만 고친다. 매매 판단·주문·청산·사이징
경로에 닿지 않는다. 아래 `TestNoLiveImpact` 가 그 사실을 고정한다.

실행:
    conda run -n py37_32 python -m pytest tests/test_606_postmarket_autofix.py
"""
import io
import os
import re
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

import pytest  # noqa: E402

_TEMPLATE = os.path.join(
    _ROOT, ".claude", "skills", "mireuk-daily-check", "references", "report_template.md"
)
_LOCK_GUARD = os.path.join(_ROOT, "scripts", "git_lock_guard.py")


def _read(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


# ------------------------------------------------------------------ G-3
class TestG3LockReclaimFixedPhrase(object):
    u"""락 회수 고정 문구가 §9p-3 에 살아 있어야 한다."""

    def test_template_exists(self):
        assert os.path.exists(_TEMPLATE), u"보고서 양식 정본이 없다: %s" % _TEMPLATE

    def test_fixed_phrase_present(self):
        src = _read(_TEMPLATE)
        assert u"git_lock_guard.py --reclaim" in src, (
            u"G-3 회귀 — 락 회수 고정 문구가 report_template.md 에서 사라졌다. "
            u"사라지면 매번 세션이 문장을 새로 지어내던 상태로 되돌아간다"
        )
        assert u".git/index.lock" in src

    def test_phrase_lives_in_user_action_section(self):
        u"""고정 문구는 반드시 §9p-3(사용자 조치) 안에 있어야 한다.

        다른 절로 옮겨가면 §5-0 규칙 5(사용자 할 일은 맨 끝 한 절에 모은다)가
        깨진다 — 사용자가 훑는 자리에 없으면 고정한 의미가 없다.
        """
        src = _read(_TEMPLATE).replace(u"\r\n", u"\n")
        head = src.find(u"### 9p-3.")
        assert head != -1, u"§9p-3 제목이 사라졌다"
        tail = src.find(u"\n---", head)
        section = src[head:] if tail == -1 else src[head:tail]
        assert u"git_lock_guard.py --reclaim" in section, (
            u"G-3 회귀 — 고정 문구가 §9p-3 밖으로 밀려났다"
        )

    def test_hold_guard_present(self):
        u"""판정보류면 넣지 말라는 경고가 함께 있어야 한다.

        이 경고 없이 회수 안내만 남으면, 문구가 오히려 사고를 유발한다 —
        실행 중인 git 의 인덱스를 깨뜨리는 쪽으로 사용자를 밀게 된다.
        """
        src = _read(_TEMPLATE)
        assert u"판정보류" in src and u"STALE" in src, (
            u"G-3 회귀 — STALE/판정보류 구분 경고가 사라졌다. "
            u"회수 안내만 남으면 문구가 사고를 유발한다"
        )

    def test_windows_only_note_present(self):
        u"""회수는 Windows PC 몫이라는 단서가 남아 있어야 한다."""
        src = _read(_TEMPLATE)
        assert u"Windows" in src and u"EPERM" in src, (
            u"G-3 회귀 — '샌드박스는 권한이 없다'는 근거가 사라졌다. "
            u"근거가 빠지면 다음 세션이 자기가 지우면 된다고 판단한다"
        )


# --------------------------------------------------- 문구 ↔ 도구 정합성
class TestPhraseMatchesTool(object):
    u"""고정 문구가 인용한 종료코드가 실제 도구와 같아야 한다."""

    def test_lock_guard_exists(self):
        assert os.path.exists(_LOCK_GUARD), u"git_lock_guard.py 가 없다"

    def test_flags_still_supported(self):
        u"""문구가 쓰는 `--check`·`--reclaim` 플래그가 살아 있는가."""
        src = _read(_LOCK_GUARD)
        for flag in (u'"--check"', u'"--reclaim"'):
            assert flag in src, (
                u"고정 문구가 %s 를 안내하는데 도구에 그 플래그가 없다" % flag
            )

    def test_exit_codes_match_document(self):
        u"""STALE=2 · 판정보류(HOLD)=3 — 문서가 인용한 값과 코드가 같은가.

        둘이 어긋나면 문서만 조용히 거짓이 된다(크래시 없음).
        """
        src = _read(_LOCK_GUARD).replace(u"\r\n", u"\n")
        m = re.search(
            r"if\s+n_stale\s*:\s*\n\s*return\s+(\d+)\s*\n"
            r"\s*if\s+n_hold\s*:\s*\n\s*return\s+(\d+)",
            src,
        )
        assert m is not None, (
            u"git_lock_guard.py 의 종료코드 분기 형태가 바뀌었다 — "
            u"report_template.md 의 'STALE(종료코드 2)'/'HOLD · 종료코드 3' "
            u"문구를 함께 확인할 것"
        )
        stale_rc, hold_rc = int(m.group(1)), int(m.group(2))
        assert stale_rc == 2, u"STALE 종료코드가 %d 로 바뀌었다 (문서는 2)" % stale_rc
        assert hold_rc == 3, u"판정보류 종료코드가 %d 로 바뀌었다 (문서는 3)" % hold_rc

        doc = _read(_TEMPLATE)
        assert u"종료코드 2" in doc and u"종료코드 3" in doc, (
            u"양식 문서에서 종료코드 인용이 사라졌다"
        )

    def test_check_runs_clean_here(self):
        u"""이 저장소에서 `--check` 가 실제로 돌고 0/2/3 중 하나를 준다."""
        proc = subprocess.Popen(
            [sys.executable, _LOCK_GUARD, "--check"],
            cwd=_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.communicate()
        assert proc.returncode in (0, 2, 3), (
            u"--check 가 예상 밖 종료코드 %d 를 돌려줬다" % proc.returncode
        )


# ------------------------------------------------------- 라이브 반영 0
class TestNoLiveImpact(object):
    u"""G-3 은 점검 양식 문서만 고친다 — 매매 경로에 닿지 않는다."""

    def test_template_is_documentation_only(self):
        u"""양식 파일은 실행되지 않는 마크다운이다."""
        assert _TEMPLATE.endswith(u".md")

    def test_template_not_imported_by_runtime(self):
        u"""런타임 코드가 이 양식 파일을 읽지 않는다.

        읽는 곳이 생기면 '문서'가 아니라 '설정'이 된 것이므로, 그때는
        이 테스트가 깨져서 재분류를 강제한다.
        """
        suspects = []
        skip_dirs = {".git", "tests", "docs", "logs", "data", "__pycache__", ".claude"}
        for dirpath, dirnames, filenames in os.walk(_ROOT):
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            for name in filenames:
                if not name.endswith(".py"):
                    continue
                full = os.path.join(dirpath, name)
                try:
                    body = _read(full)
                except (IOError, OSError, UnicodeDecodeError):
                    continue
                if u"report_template" in body:
                    suspects.append(os.path.relpath(full, _ROOT))
        assert not suspects, (
            u"런타임 코드가 보고서 양식을 읽는다 — 문서가 아니라 설정이 됐다: %s"
            % u", ".join(suspects)
        )
