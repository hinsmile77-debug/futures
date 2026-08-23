# -*- coding: utf-8 -*-
"""[MW0601 483차 후속3 / P1-3] `.git/index.lock` 스테일 판정·회수 규약 고정.

## 이 테스트가 지키는 것

`scripts/git_lock_guard.py` 는 **파일을 지우는** 도구다. 판정이 느슨해지면 실행 중인
git 의 락을 지워 인덱스를 깨뜨린다 — 안전장치가 새 사고를 만드는 형태다.
그래서 "지운다"보다 **"안 지운다"** 쪽을 더 많이 고정한다.

3중 조건 (전부 충족해야 stale):

    (1) size == 0        인덱스 쓰기 명령이 죽은 지문
    (2) age  > min_age   정상 명령이 10분씩 락을 쥐지 않는다
    (3) git 프로세스 0개  지금 도는 git 이 없다

⚠ (3)을 **못 세면** `None`(미측정)이며 0 으로 간주하지 않는다 — 계측 4원칙 (2).
   "측정하지 않았다"와 "측정했더니 0이다"를 같은 값으로 표현하지 않는다.

배경(2026-08-21 실측): 0바이트 락이 53.5시간 남아 저장소가 커밋 불가였는데
`git status` 는 rc=0 으로 조용히 통과해 어떤 계측에도 안 걸렸다.
전문은 `dev_memory/DECISION_LOG.md` 483차 후속2·후속3.
"""
import os
import sys
import time

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
_SCRIPTS = os.path.join(_ROOT, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import git_lock_guard as G  # noqa: E402


def _repo(tmpdir, size=0, age_sec=54 * 3600):
    """`.git/index.lock` 을 원하는 크기·나이로 만든 가짜 저장소."""
    root = str(tmpdir)
    gd = os.path.join(root, ".git")
    os.makedirs(gd)
    lock = os.path.join(gd, "index.lock")
    with open(lock, "wb") as f:
        f.write(b"x" * size)
    t = time.time() - age_sec
    os.utime(lock, (t, t))
    return root, lock


# ── 판정 ────────────────────────────────────────────────────────────

def test_three_conditions_met_is_stale(tmpdir):
    root, _ = _repo(tmpdir)
    info = G.inspect(root, git_procs=0)
    assert info["stale"] is True
    assert "커밋 불가" in info["verdict"], "판정문이 결과(커밋 불가)를 말해야 한다"


def test_nonzero_size_is_not_stale(tmpdir):
    """0바이트가 아니면 인덱스 쓰기가 진행된 것 — 함부로 지우면 안 된다."""
    root, _ = _repo(tmpdir, size=100)
    info = G.inspect(root, git_procs=0)
    assert info["stale"] is False
    assert "판정보류" in info["verdict"]


def test_young_lock_is_not_stale(tmpdir):
    """지금 도는 git 일 수 있다 — 나이 조건이 가장 흔한 오판 방지선이다."""
    root, _ = _repo(tmpdir, age_sec=60)
    info = G.inspect(root, git_procs=0)
    assert info["stale"] is False


def test_running_git_blocks_stale_verdict(tmpdir):
    root, _ = _repo(tmpdir)
    info = G.inspect(root, git_procs=2)
    assert info["stale"] is False
    assert "실행 중" in info["verdict"]


def test_unmeasured_process_count_is_not_treated_as_zero(tmpdir, monkeypatch):
    """계측 4원칙 (2) — 미측정을 0 으로 위장하면 실행 중인 git 을 지운다."""
    monkeypatch.setattr(G, "_git_process_count", lambda: None)
    root, _ = _repo(tmpdir)
    info = G.inspect(root)                      # git_procs 미지정 → 내부 계수 → None
    assert info["git_procs"] is None
    assert info["stale"] is False
    assert "미측정" in info["verdict"]


def test_no_lock_and_not_a_repo(tmpdir):
    root = str(tmpdir)
    os.makedirs(os.path.join(root, ".git"))
    assert G.inspect(root, git_procs=0)["present"] is False
    plain = str(tmpdir.mkdir("plain"))
    assert G.inspect(plain, git_procs=0)["is_repo"] is False


# ── 회수 ────────────────────────────────────────────────────────────

def test_reclaim_removes_only_when_stale(tmpdir):
    root, lock = _repo(tmpdir)
    removed, info = G.reclaim(root, git_procs=0)
    assert removed is True and not os.path.exists(lock)
    assert "회수 완료" in info["verdict"]


@pytest.mark.parametrize("kw", [{"size": 100}, {"age_sec": 30}])
def test_reclaim_never_removes_on_hold(tmpdir, kw):
    root, lock = _repo(tmpdir, **kw)
    removed, info = G.reclaim(root, git_procs=0)
    assert removed is False, "판정보류인데 지웠다 — 실행 중인 git 의 인덱스를 깨뜨린다"
    assert os.path.exists(lock)


def test_reclaim_rechecks_size_after_verdict(tmpdir, monkeypatch):
    """판정과 삭제 사이의 경합 — 그 틈에 커진 락은 지우지 않는다."""
    root, lock = _repo(tmpdir)
    real_inspect = G.inspect

    def _grow(*a, **k):
        info = real_inspect(*a, **k)
        with open(lock, "wb") as f:      # 판정 직후 다른 git 이 쓰기 시작한 상황
            f.write(b"y" * 64)
        return info

    monkeypatch.setattr(G, "inspect", _grow)
    removed, info = G.reclaim(root, git_procs=0)
    assert removed is False and os.path.exists(lock)
    assert "회수 취소" in info["verdict"]


# ── CLI 계약 ────────────────────────────────────────────────────────

def test_exit_codes(tmpdir, monkeypatch, capsys):
    monkeypatch.setattr(G, "_git_process_count", lambda: 0)
    stale_root, _ = _repo(tmpdir.mkdir("stale"))
    hold_root, _ = _repo(tmpdir.mkdir("hold"), age_sec=30)
    clean_root = str(tmpdir.mkdir("clean"))
    os.makedirs(os.path.join(clean_root, ".git"))

    assert G.main(["--check", "--repo", clean_root]) == 0
    assert G.main(["--check", "--repo", stale_root]) == 2, "스테일은 종료코드 2"
    assert G.main(["--check", "--repo", hold_root]) == 3, "판정보류는 종료코드 3"
    capsys.readouterr()


def test_check_mode_never_deletes(tmpdir, monkeypatch):
    """`--check` 가 파일을 지우면 프리플라이트로 쓸 수 없다."""
    monkeypatch.setattr(G, "_git_process_count", lambda: 0)
    root, lock = _repo(tmpdir)
    G.main(["--check", "--repo", root])
    assert os.path.exists(lock)


def test_py37_compatible_source():
    """py3.7(futures) · py3.10(fuoption) 양쪽에서 도는 단일 파일이어야 한다.

    복사본이 두 저장소에 있으므로 신 문법이 들어가면 한쪽에서만 죽는다.
    """
    import ast
    import io
    src = io.open(os.path.join(_SCRIPTS, "git_lock_guard.py"), encoding="utf-8").read()
    tree = ast.parse(src)

    # 주석·독스트링에 이름이 언급되는 것과 **실제 사용**을 구분한다 — 문자열 검색으로
    # 하면 이 규약을 설명하는 문장 자체에 걸린다(483차에 실제로 걸렸다).
    imported = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imported.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            imported.add(n.module.split(".")[0])
    assert "pathlib" not in imported, "pathlib 금지 — 단일 파일 이식성"
    assert "dataclasses" not in imported

    assert not [n for n in ast.walk(tree) if isinstance(n, ast.JoinedStr)],         "f-string 금지 — 이식성 규약"
    assert not [n for n in ast.walk(tree) if n.__class__.__name__ == "NamedExpr"],         "왈러스 연산자는 py3.7 에서 죽는다"


# ── P2-1 형제 저장소 복사본 드리프트 ────────────────────────────────

_SIBLING_COPIES = [
    # (설명, 경로) — 없으면 skip. 이 PC에만 있는 경로이므로 실패시키지 않는다.
    ("fuoption", os.path.join(os.path.dirname(os.path.dirname(_ROOT)),
                              "PycharmProjects", "fuoption", "scripts",
                              "git_lock_guard.py")),
]


@pytest.mark.parametrize("name,path", _SIBLING_COPIES)
def test_sibling_copy_matches_canonical(name, path):
    """복사본이 갈라지면 한쪽 저장소만 고쳐진 채 남는다 — 2026-08-21 사고의 형태다.

    ⚠ 이 검사는 **경로가 있을 때만** 돈다. 다른 PC·다른 체크아웃에는 형제 저장소가
      없을 수 있고, 그걸 실패로 만들면 테스트가 환경에 종속된다.
      **skip 은 "같다"는 뜻이 아니다** — 계측 4원칙 ②.
    """
    import io
    if not os.path.exists(path):
        pytest.skip("형제 저장소 사본 없음(이 PC에 %s 미체크아웃) — 동일성 **미검증**" % name)
    canon = io.open(os.path.join(_SCRIPTS, "git_lock_guard.py"), "rb").read()
    copy = io.open(path, "rb").read()
    assert canon == copy, (
        "%s 사본이 정본과 다르다 — 판정 로직이 저장소별로 갈라졌다. "
        "정본(futures/scripts/git_lock_guard.py)을 복사해 맞출 것" % name)
