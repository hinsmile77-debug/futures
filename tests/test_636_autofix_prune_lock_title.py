# -*- coding: utf-8 -*-
"""[MW0601 636차 / 2026-09-28 장후 자동조치] 고도화 방안 2·3·4 회귀 고정.

A. `prune_raw_data_db()` — 반환값은 **실제 반영된** 삭제 행수여야 한다.
   2026-09-28 EOD 로그에 「DB pruning 실패: database table is locked」와
   「[GBM] DB pruning: 22,860행 삭제」가 같은 초에 찍혔다. 실측 결과 삭제는
   전량 롤백됐고 22,860 은 롤백된 **시도** 행수였다. 이 테스트는 「반환값 ==
   실제 줄어든 행수」 불변식을 고정한다 — 체크포인트 순서를 고쳐 삭제가 실제로
   반영되게 되더라도(NEXT_TODO 636-2) 그대로 통과해야 한다.
B. `git_lock_guard.reclaim()` — 삭제가 권한으로 막히면 이름변경으로 우회.
   단 **스테일 확정 뒤에만**, 그리고 `.git` 바로 아래 파일에만.
C. `md_title_guard.title_damaged()` — 2026-09-28 이상점 1-1 실물 재현.
"""
import os
import sqlite3
import subprocess
import sys
import time

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.join(_ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import git_lock_guard as G  # noqa: E402
import md_title_guard as T  # noqa: E402


# ── A. prune ────────────────────────────────────────────────────────

def _make_raw_db(path):
    c = sqlite3.connect(path)
    c.execute("PRAGMA journal_mode=wal")
    for t in ("raw_features", "raw_candles"):
        c.execute("create table %s(ts text)" % t)
        c.executemany("insert into %s values(?)" % t,
                      [("2020-01-01 09:00:00",)] * 30 + [("2099-01-01 09:00:00",)] * 5)
    c.commit()
    c.close()


def _count(path):
    c = sqlite3.connect(path)
    try:
        return sum(c.execute("select count(*) from %s" % t).fetchone()[0]
                   for t in ("raw_features", "raw_candles"))
    finally:
        c.close()


def test_prune_return_equals_rows_actually_removed(tmpdir, monkeypatch):
    import config.settings as S
    from learning.batch_retrainer import BatchRetrainer

    db = os.path.join(str(tmpdir), "raw_data.db")
    _make_raw_db(db)
    monkeypatch.setattr(S, "RAW_DATA_DB", db)
    before = _count(db)
    ret = BatchRetrainer.prune_raw_data_db(None, keep_weeks=52)  # self 미사용
    after = _count(db)
    assert ret == before - after, (
        "반환값(%d)이 실제로 줄어든 행수(%d)와 다르다 — 롤백된 시도 행수를 "
        "삭제 성공처럼 보고하면 main.py 가 거짓 `[GBM] DB pruning: N행 삭제`를 찍는다"
        % (ret, before - after))


def test_prune_failure_log_says_rollback(tmpdir, monkeypatch):
    import config.settings as S
    import learning.batch_retrainer as BR

    db = os.path.join(str(tmpdir), "raw_data.db")
    _make_raw_db(db)
    monkeypatch.setattr(S, "RAW_DATA_DB", db)
    # caplog 는 전체 스위트에서 다른 테스트가 로깅 설정을 바꾸면 비어 버린다 — 직접 가로챈다.
    msgs = []
    monkeypatch.setattr(BR.logger, "warning", lambda m, *a, **k: msgs.append(m % a if a else m))
    ret = BR.BatchRetrainer.prune_raw_data_db(None, keep_weeks=52)
    fails = [m for m in msgs if "DB pruning 실패" in m]
    if ret == 0 and _count(db) == 70:
        # 현행: 자기 트랜잭션 안 체크포인트 -> 롤백. 로그가 그 사실을 말해야 한다.
        assert fails and "롤백" in fails[0] and "반영 0행" in fails[0], fails


# ── B. git_lock_guard 이름변경 우회 ─────────────────────────────────

def _lock_repo(tmpdir, name="index.lock", sub="", age_sec=54 * 3600):
    root = str(tmpdir)
    d = os.path.join(root, ".git", sub) if sub else os.path.join(root, ".git")
    if not os.path.isdir(d):
        os.makedirs(d)
    lock = os.path.join(d, name)
    open(lock, "wb").close()
    t = time.time() - age_sec
    os.utime(lock, (t, t))
    return root, lock


def _deny_remove(monkeypatch):
    def boom(path):
        raise PermissionError(1, "Operation not permitted")
    monkeypatch.setattr(G, "_force_remove", boom)


def test_reclaim_sidelines_when_delete_denied(tmpdir, monkeypatch):
    root, lock = _lock_repo(tmpdir)
    _deny_remove(monkeypatch)
    removed, info = G.reclaim(root, git_procs=0)
    assert removed is True
    assert not os.path.exists(lock), "이름변경 후 index.lock 이 남아 있으면 커밋이 계속 막힌다"
    dst = info["sidelined_to"]
    assert os.path.exists(dst) and ".lock.stale_" in os.path.basename(dst)
    assert "이름변경" in info["verdict"]
    # 남은 파일은 T2 부스러기로 잡혀 나중에 치워진다
    _t1, t2 = G.scan_extra(root)
    assert dst in t2


def test_reclaim_never_sidelines_held_lock(tmpdir, monkeypatch):
    """판정보류(실행 중일 수 있는 git)면 이름도 바꾸지 않는다 — 인덱스 파손 방지."""
    root, lock = _lock_repo(tmpdir, age_sec=30)
    _deny_remove(monkeypatch)
    removed, info = G.reclaim(root, git_procs=0)
    assert removed is False
    assert os.path.exists(lock)
    assert "sidelined_to" not in info


def test_reclaim_reports_failure_when_rename_also_fails(tmpdir, monkeypatch):
    root, lock = _lock_repo(tmpdir)
    _deny_remove(monkeypatch)

    def no_rename(a, b):
        raise PermissionError(1, "rename denied")
    monkeypatch.setattr(G.os, "rename", no_rename)
    removed, info = G.reclaim(root, git_procs=0)
    assert removed is False
    assert "회수 실패" in info["verdict"]
    assert os.path.exists(lock)


def test_sweep_does_not_sideline_ref_locks(tmpdir, monkeypatch):
    """refs/heads/x.lock -> x.lock.stale_… 는 유효한 ref 이름이 된다. 절대 금지."""
    root, lock = _lock_repo(tmpdir, name="main.lock", sub=os.path.join("refs", "heads"))
    _deny_remove(monkeypatch)
    rows, n_stale, _h, n_removed = G.sweep_extra(root, git_procs=0, reclaim_it=True)
    assert n_removed == 0
    assert os.path.exists(lock)
    assert os.listdir(os.path.dirname(lock)) == ["main.lock"]


def test_sweep_sidelines_top_level_head_lock(tmpdir, monkeypatch):
    root, lock = _lock_repo(tmpdir, name="HEAD.lock")
    _deny_remove(monkeypatch)
    rows, _s, _h, n_removed = G.sweep_extra(root, git_procs=0, reclaim_it=True)
    assert n_removed == 1
    assert not os.path.exists(lock)


# ── C. md_title_guard ───────────────────────────────────────────────

_OLD = u"# 재시작 종료사유 분류 · 봉 결손 대응 구현계획 — 2026-09-22 (MW0601)\n\n> 본문\n"
_NEW = u"\n시작 종료사유 분류 · 봉 결손 대응 구현계획 — 2026-09-22 (MW0601)\n\n> 본문\n"


def test_title_damage_0928_reproduced():
    assert T.title_damaged(_OLD, _NEW) is True


def test_title_wording_change_is_not_damage():
    assert T.title_damaged(_OLD, u"# 다른 제목\n\n> 본문\n") is False


def test_no_title_in_head_is_out_of_scope():
    assert T.title_damaged(u"본문만\n", u"다른 본문\n") is False


def test_scan_on_temp_repo(tmpdir):
    root = str(tmpdir)
    try:
        subprocess.check_call(["git", "init", "-q", root])
    except Exception:
        pytest.skip("git 없음")
    p = os.path.join(root, "a.md")
    with open(p, "wb") as f:
        f.write(_OLD.encode("utf-8"))
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    subprocess.check_call(["git", "-C", root, "add", "a.md"], env=env)
    subprocess.check_call(["git", "-C", root, "commit", "-q", "-m", "x"], env=env)
    with open(p, "wb") as f:
        f.write(_NEW.encode("utf-8"))
    suspects, n = T.scan(root)
    assert n == 1 and [s["path"] for s in suspects] == ["a.md"]
    assert T.main(["--repo", root]) == 2
