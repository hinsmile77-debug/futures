# -*- coding: utf-8 -*-
"""456차 Wave 0 — F8 장중 분석 가드 + F3 L1 스크리닝 커버리지 회귀 테스트.

배경: `docs/정기점검/매일점검/MW0601-20260810-점검리포트.md` §3-2·§3-3,
      `docs/정기점검/매일점검/0810_Fix_고도화_통합구현계획_MW0601.md` Wave 0.
"""
import datetime
import os
import sqlite3
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils import analysis_db as adb                      # noqa: E402
from scripts import core_feature_discovery as cfd         # noqa: E402


# ── F8: 장중 가드 ────────────────────────────────────────────────────────────

@pytest.fixture
def _clean_env(monkeypatch):
    monkeypatch.delenv(adb.ALLOW_ENV, raising=False)


def test_live_window_boundaries():
    """프리장 시작(08:45)·본장 마감(15:35) 경계와 주말."""
    import utils.time_utils as tu
    assert adb.is_live_window(datetime.datetime(2026, 8, 10, 8, 30)) is False   # 프리장 전
    assert adb.is_live_window(datetime.datetime(2026, 8, 10, 8, 50)) is True    # 프리장
    assert adb.is_live_window(datetime.datetime(2026, 8, 10, 13, 47)) is True   # CB⑤ 발생 시각
    assert adb.is_live_window(datetime.datetime(2026, 8, 10, 15, 36)) is False  # 마감 후
    assert adb.is_live_window(datetime.datetime(2026, 8, 8, 11, 0)) is False    # 토요일
    # 단일 진실원 위임 확인 — 자체 시각 정의를 두지 않는다
    assert tu.is_trading_session(datetime.datetime(2026, 8, 10, 13, 47)) is True


def test_guard_blocks_intraday(_clean_env):
    """장중이면 차단, 장외면 통과."""
    assert adb.guard_intraday(
        "t", dt=datetime.datetime(2026, 8, 10, 13, 47), exit_on_block=False) is True
    assert adb.guard_intraday(
        "t", dt=datetime.datetime(2026, 8, 10, 16, 0), exit_on_block=False) is False


def test_guard_env_override(monkeypatch):
    """명시적 환경변수로만 장중 우회 가능."""
    intraday = datetime.datetime(2026, 8, 10, 13, 47)
    monkeypatch.setenv(adb.ALLOW_ENV, "1")
    assert adb.guard_intraday("t", dt=intraday, exit_on_block=False) is False
    # 빈 문자열·0·false 는 우회로 치지 않는다
    for falsy in ("", "0", "false", "False"):
        monkeypatch.setenv(adb.ALLOW_ENV, falsy)
        assert adb.guard_intraday("t", dt=intraday, exit_on_block=False) is True


def test_guard_exits_with_dedicated_code(_clean_env):
    """차단 시 종료코드 2 — 0(정상)·1(예외)과 구분돼야 EOD 체인이 스킵으로 읽는다."""
    with pytest.raises(SystemExit) as ex:
        adb.guard_intraday("t", dt=datetime.datetime(2026, 8, 10, 13, 47))
    assert ex.value.code == adb.EXIT_INTRADAY_BLOCKED == 2


def test_campaign_steps_treats_rc2_as_skip():
    """EOD 체인이 rc=2를 FAIL이 아니라 SKIP으로 집계하는지 (거짓 실패 방지)."""
    from scripts import campaign_steps as cs
    assert cs._EXIT_INTRADAY_BLOCKED == adb.EXIT_INTRADAY_BLOCKED
    src = open(os.path.join(_ROOT, "scripts", "campaign_steps.py"), encoding="utf-8").read()
    assert "SKIP(장중차단)" in src
    # 448차 "조용한 실패 차단"은 _s == "OK" 로 판정하므로 SKIP은 자동으로
    # '경로 안내 안 함'에 걸린다 — 낡은 리포트를 이번 주 것으로 오독하지 않는다.
    assert '_report_step_ok = (_s == "OK")' in src


def test_connect_ro_blocks_writes(tmp_path):
    """읽기전용 커넥션이 실제로 쓰기를 막는가 (라이브 DB 오염 방지)."""
    db = tmp_path / "t.db"
    con = sqlite3.connect(str(db))
    con.execute("create table a(x)")
    con.execute("insert into a values (1)")
    con.commit()
    con.close()

    ro = adb.connect_ro(str(db))
    assert ro.execute("select count(*) from a").fetchone()[0] == 1
    with pytest.raises(sqlite3.OperationalError):
        ro.execute("insert into a values (2)")
    ro.close()


def test_connect_ro_falls_back_when_unopenable(tmp_path, capsys):
    """읽기전용 실패 시 분석이 통째로 막히지 않고 폴백하는가."""
    missing = tmp_path / "nope.db"
    con = adb.connect_ro(str(missing))     # mode=ro 는 없는 파일에서 실패 → 폴백
    assert con is not None
    con.close()
    assert "폴백" in capsys.readouterr().err


# ── F3: L1 스크리닝 커버리지 ─────────────────────────────────────────────────

def _synth(n_days=30, rows_per_day=60):
    """합성 피처행. 관찰창 중간 도입 피처를 재현한다."""
    feats = []
    i = 0
    for d in range(n_days):
        day = (datetime.date(2026, 6, 1) + datetime.timedelta(days=d)).isoformat()
        for r in range(rows_per_day):
            ts = "%s %02d:%02d:00" % (day, 9 + r // 60, r % 60)
            f = {
                # 전 구간 존재 + 고유값 충분 → 통과
                "always_on": float(i) * 0.37,
                # 전 구간 존재하나 결측 과반 → 커버리지 탈락
                "sparse": (float(i) * 0.11 if i % 3 == 0 else None),
                # 상수 → 고유값 탈락
                "flat_const": 0.0,
            }
            if d >= 10:      # 11일차 도입 → 이후 100% (구 방식이면 커버리지 66%로 탈락)
                f["born_midwindow"] = float(i) * 0.53
            if d >= n_days - 5:   # 마지막 5일 도입 → 관찰기간 하한에 걸려야 함
                f["born_yesterday"] = float(i) * 0.29
            feats.append((ts, {k: v for k, v in f.items() if v is not None}))
            i += 1
    return feats


def test_midwindow_feature_is_screened():
    """관찰창 중간 도입 피처가 커버리지 필터에 잘못 걸리지 않는가.

    2026-08-10 실측 회귀: --days 40 이 62개, --days 19 가 82개였다. 20개가
    '도입일이 창 안에 있다'는 이유만으로 사라졌고 그중에 30m CORE(opt_chain_pcr)와
    vkospi 가 있었다.
    """
    names, X, ts = cfd.build_matrix(_synth(), verbose=False)
    assert "always_on" in names
    assert "born_midwindow" in names, "중간 도입 피처가 여전히 탈락한다 — F3 회귀"


def test_too_new_feature_rejected_with_reason():
    """반대편 실패 — 갓 생긴 피처가 커버리지 100%로 통과해선 안 된다."""
    names, _, _ = cfd.build_matrix(_synth(), verbose=False)
    assert "born_yesterday" not in names
    dropped = dict(cfd.LAST_SCREENING_REPORT["dropped"])
    assert "born_yesterday" in dropped
    assert "관찰" in dropped["born_yesterday"]


def test_dropped_features_are_reported_with_reasons():
    """탈락 가시화(G3-A3) — 무엇이 왜 빠졌는지 남는가."""
    cfd.build_matrix(_synth(), verbose=False)
    dropped = dict(cfd.LAST_SCREENING_REPORT["dropped"])
    assert "커버리지" in dropped["sparse"]
    assert "고유값" in dropped["flat_const"]
    assert cfd.LAST_SCREENING_REPORT["kept"], "통과 목록도 함께 남아야 한다"


def test_load_uses_indexed_ts_predicate():
    """substr(ts,..) 술어는 인덱스를 못 타 468MB 전수 스캔이 된다 — 재도입 방지.

    docstring은 옛 술어를 설명으로 인용하므로 **실행되는 SQL 줄만** 검사한다.
    """
    import inspect
    exec_lines = [
        ln for ln in inspect.getsource(cfd.load).splitlines()
        if "cur.execute" in ln
    ]
    assert exec_lines, "load()에서 SQL 실행부를 찾지 못했다"
    scanning = [ln for ln in exec_lines if "WHERE substr(ts" in ln]
    assert not scanning, "인덱스를 못 타는 술어가 재도입됨: %s" % scanning
    assert any("WHERE ts >= ?" in ln for ln in exec_lines)


def test_build_matrix_keeps_3tuple_contract():
    """반환 시그니처 유지 — horizon_signal_tradability·ic_decay_catalog가 이걸 쓴다."""
    out = cfd.build_matrix(_synth(), verbose=False)
    assert isinstance(out, tuple) and len(out) == 3
    names, X, ts_list = out
    assert X.shape[0] == len(ts_list)
    assert X.shape[1] == len(names)
