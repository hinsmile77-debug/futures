"""[MW0602 신동 주체 리뉴얼] 3·4단계 회귀 — 기동·장후 휴면 · 신동 전용 EOD · 흐름 신선도 · 수집 실패 시간청산.

  E1  재학습 서브프로세스 진입점이 휴면이면 띄우지 않는다(모든 트리거가 이 한 곳을 지난다)
  E2  장전 준비: 휴면이면 현재가 스냅샷까지만 — Canary·워밍업·사전 재학습 앞에서 끝난다
  E3  daily_close: 미륵 전용 항목은 `if self._mireuk_on():` 아래 · 신동·계좌 항목은 그 밖
  E4  scripts/shindong_eod.py — 세 단계 독립 · 종료코드 · 완료 마커 · 장중 실행 거부 · 대기 타임아웃
  E5  설치기 — 순수 ASCII·CRLF · 미륵 재학습은 **비활성**(삭제 아님) · 신동 EOD 성공 전에는 거부
  F1  흐름 신선도: 지연 분 계산 · shadow 는 진입 무변경 · live 는 기각 사유 · off 는 미측정
  F2  같은 지연 구간은 한 번만 경고하고 해소 시 한 줄
  F3  7222 수집 실패 분에도 신동 포지션의 15:05 시간청산이 나간다(그 전·FLAT·타 주체는 무동작)
"""
import datetime
import inspect
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402
from scripts import shindong_eod as SE  # noqa: E402

TS = main.TradingSystem
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _LM(object):
    def __init__(self):
        self.lines = []

    def system(self, msg, level="INFO"):
        self.lines.append((level, msg))

    def trade(self, *a, **k):
        pass

    def signal(self, *a, **k):
        pass


def _with_log(fn):
    orig = main.log_manager
    rec = _LM()
    main.log_manager = rec
    try:
        fn(rec)
    finally:
        main.log_manager = orig
    return rec


# ── E1 · E2 · E3 ─────────────────────────────────────────────────────────────

def test_E1_retrain_subprocess_refuses_when_dormant():
    class _S(object):
        def _mireuk_on(self):
            return False

    def run(rec):
        assert TS._start_gbm_retrain_subprocess(_S(), force=True, reason="t", is_warmup=False) is False
        assert any("미륵 휴면 — 재학습 생략" in m for _, m in rec.lines)

    _with_log(run)
    src = inspect.getsource(TS._start_gbm_retrain_subprocess)
    assert src.index("if not self._mireuk_on():") < src.index("_gbm_retrain_running")


def test_E2_pre_market_setup_stops_before_canary():
    src = inspect.getsource(TS.pre_market_setup)
    i_snap = src.index("_rd._prime_from_snapshot()")
    i_off = src.index("if not self._mireuk_on():\n            log_manager.system(\"[PreOpen] 미륵 휴면")
    i_can = src.index("canary_stale_age_hours()")
    i_pre = src.index('reason="08:55 PreRetrain"')
    assert i_snap < i_off < i_can < i_pre
    assert "if self._mireuk_on():\n                from config.settings import META_CONF_STATE_PATH" in src


def _enclosing_top(src_lines, idx, indent=8):
    """idx 줄을 감싸는 들여쓰기 `indent` 의 문장(위로 첫 줄)."""
    for j in range(idx, -1, -1):
        ln = src_lines[j]
        if ln.strip() and (len(ln) - len(ln.lstrip(" "))) == indent and not ln.strip().startswith("#"):
            return ln.strip()
    return ""


def test_E3_daily_close_guards_mireuk_only_items():
    src = inspect.getsource(TS.daily_close)
    lines = src.splitlines()

    def top_of(needle):
        i = next(k for k, ln in enumerate(lines) if needle in ln)
        return _enclosing_top(lines, i)

    guarded = ["ENSEMBLE_CALIBRATOR_PATH", "self.meta_gate.learner.save(META_CONF_STATE_PATH)",
               "self.drift_adjuster.record_accuracy(", "self.threshold_recalibrator.run_if_due(",
               "self.atr_ceiling_recalibrator.run_if_due(", "self.entry_horizon_recalibrator.run_if_due(",
               "self.atr_multiple_recalibrator.run_if_due(", "self._gbm_retrain_done_event.wait(",
               "record_live_snapshot(", "from model.scaler_monitor_db import aggregate_daily",
               "get_drift_detector as _get_dd()", "_exp.save(_report)", "self._load_shadow_candidate()",
               "self.challenger_engine.update_daily_metrics(", "check_champion_heartbeat()"]
    for g in guarded:
        if g == "get_drift_detector as _get_dd()":
            g = "from strategy.param_drift_detector import get_drift_detector as _get_dd\n"
            g = g.strip()
        t = top_of(g)
        assert "_mireuk_on()" in t, (g, t)
    kept = ["update_daily_broker_pnl_net(", "reconcile_daily_net(", "daily_report as _sddr",
            "self.circuit_breaker.reset_daily()", "self.profit_guard.reset_daily()",
            "self._premarket_levels_0850_done    = False", "save_daily_stats(today_str,"]
    for k in kept:
        t = top_of(k)
        assert "_mireuk_on()" not in t, (k, t)
    # 휴면이면 Phase5 extra_stats 가 참조하는 변수가 정의돼 있다(NameError 방지)
    assert "_ccf_today, _mc_gap_today, _mc_gap_avg = 0, 0, 0.0" in src


# ── E4 신동 전용 EOD ─────────────────────────────────────────────────────────

class _Log(object):
    def __init__(self):
        self.lines = []

    def info(self, fmt, *a):
        self.lines.append(("INFO", fmt % a if a else fmt))

    def warning(self, fmt, *a):
        self.lines.append(("WARNING", fmt % a if a else fmt))

    def error(self, fmt, *a):
        self.lines.append(("ERROR", fmt % a if a else fmt))


def _steps(levels=None, reg=None, of=None):
    return {"levels": levels or (lambda: {"refreshed": {"last_date": "2026-10-26", "sessions": 256}}),
            "regular": reg or (lambda: {"status": "ok", "line": "[RegularFresh] ok"}),
            "option_flow": of or (lambda: {"status": "ok", "line": "[OptionFlowFresh] ok"})}


def test_E4_all_ok_exit0_and_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(SE, "_ROOT", str(tmp_path))
    os.makedirs(str(tmp_path / "data"))
    out = SE.run("2026-10-26", wait=False, log=_Log(), steps=_steps())
    assert out["exit_code"] == 0
    mk = tmp_path / "data" / "shindong_eod_done_20261026.txt"
    assert mk.exists() and "exit=0" in mk.read_text(encoding="utf-8")


def test_E4_cache_failure_is_exit2_and_others_still_run(tmp_path, monkeypatch):
    monkeypatch.setattr(SE, "_ROOT", str(tmp_path))
    os.makedirs(str(tmp_path / "data"))
    called = []

    def boom():
        raise RuntimeError("x")

    def reg():
        called.append("reg")
        return {"status": "ok", "line": "ok"}

    out = SE.run("2026-10-26", wait=False, log=_Log(), steps=_steps(levels=boom, reg=reg))
    assert out["exit_code"] == 2 and called == ["reg"]


def test_E4_stale_cache_date_and_freshness_gap_are_exit1(tmp_path, monkeypatch):
    monkeypatch.setattr(SE, "_ROOT", str(tmp_path))
    os.makedirs(str(tmp_path / "data"))
    lg = _Log()
    out = SE.run("2026-10-26", wait=False, log=lg, steps=_steps(
        levels=lambda: {"refreshed": {"last_date": "2026-10-23", "sessions": 255}},
        of=lambda: {"status": "missing", "line": "[OptionFlowFresh] 결손"}))
    assert out["exit_code"] == 1
    assert any("≠ 오늘" in m for _, m in lg.lines)


def test_E4_unmeasured_freshness_is_not_ok(tmp_path, monkeypatch):
    monkeypatch.setattr(SE, "_ROOT", str(tmp_path))
    os.makedirs(str(tmp_path / "data"))

    def boom():
        raise OSError("db")

    out = SE.run("2026-10-26", wait=False, log=_Log(), steps=_steps(reg=boom))
    assert out["exit_code"] == 1


def test_E4_wait_times_out_without_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(SE, "_ROOT", str(tmp_path))
    t = [datetime.datetime(2026, 10, 26, 15, 55)]

    def now():
        return t[0]

    def sleep(sec):
        t[0] = t[0] + datetime.timedelta(seconds=sec)

    assert SE.wait_for_daily_close(_Log(), "20261026", max_wait_min=2, poll_sec=30, sleep=sleep, now=now) is False
    os.makedirs(str(tmp_path / "data"))
    (tmp_path / "data" / "daily_close_done_20261026.txt").write_text("x", encoding="utf-8")
    assert SE.wait_for_daily_close(_Log(), "20261026", max_wait_min=2, sleep=sleep, now=now) is True


def test_E4_script_calls_dll_bootstrap_first():
    src = io.open(os.path.join(ROOT, "scripts", "shindong_eod.py"), encoding="utf-8").read()
    assert src.index("ensure_conda_dll_path()") < src.index("def run(")
    assert "guard" in src.lower() or "장중 실행 금지" in src


# ── E5 설치기 ────────────────────────────────────────────────────────────────

def test_E5_installers_ascii_crlf_and_safe_toggle():
    for rel in ("TASK_SHINDONG_EOD_INSTALL.bat", "scripts/shindong_eod_task.ps1"):
        b = open(os.path.join(ROOT, rel), "rb").read()
        b.decode("ascii")                                 # PS 5.1 이 BOM 없는 파일을 ANSI 로 읽는다
        assert b"\r\n" in b and b.count(b"\n") == b.count(b"\r\n"), rel
    ps = open(os.path.join(ROOT, "scripts/shindong_eod_task.ps1"), encoding="ascii").read()
    assert "Disable-ScheduledTask" in ps and "Unregister-ScheduledTask -TaskName $t.TaskName" not in ps
    assert "LastTaskResult -ne 0" in ps                   # 신동 EOD 성공 전에는 미륵 재학습을 끄지 않는다
    assert "MireukiEODRetrain" in ps and "shindong_eod.py" in ps


# ── F1 · F2 흐름 신선도 ──────────────────────────────────────────────────────

class _FS(object):
    _shindong_flow_stale_check = TS._shindong_flow_stale_check
    _shindong_flow_stale_block = TS._shindong_flow_stale_block

    def __init__(self):
        self._sd_flow_lag = None
        self._sd_flow_stale_since = None


def _set_mode(monkeypatch, mode, lim=3):
    monkeypatch.setattr(main.runtime_settings, "SHINDONG_FLOW_STALE_GUARD", mode, raising=False)
    monkeypatch.setattr(main.runtime_settings, "SHINDONG_FLOW_STALE_MIN", lim, raising=False)


def test_F1_lag_and_modes(monkeypatch):
    now = datetime.datetime(2026, 10, 26, 10, 30, 2)
    for mode, blocked in (("shadow", None), ("live", "flow_stale")):
        _set_mode(monkeypatch, mode)
        s = _FS()
        _with_log(lambda rec: s._shindong_flow_stale_check({"horizon": "10:25"}, now))
        assert s._sd_flow_lag == 4                         # 직전 분 10:29 − 10:25
        b = s._shindong_flow_stale_block()
        assert (b is None) if blocked is None else b.startswith(blocked)
    _set_mode(monkeypatch, "off")
    s = _FS()
    _with_log(lambda rec: s._shindong_flow_stale_check({"horizon": "10:00"}, now))
    assert s._sd_flow_lag is None and s._shindong_flow_stale_block() is None
    _set_mode(monkeypatch, "live")
    s = _FS()
    _with_log(lambda rec: s._shindong_flow_stale_check({"horizon": None}, now))
    assert s._sd_flow_lag is None                          # 미측정 — 0 이 아니다


def test_F2_one_warning_per_episode(monkeypatch):
    _set_mode(monkeypatch, "shadow")
    s = _FS()
    t0 = datetime.datetime(2026, 10, 26, 10, 30, 2)

    def run(rec):
        s._shindong_flow_stale_check({"horizon": "10:20"}, t0)
        s._shindong_flow_stale_check({"horizon": "10:20"}, t0 + datetime.timedelta(minutes=1))
        s._shindong_flow_stale_check({"horizon": "10:31"}, t0 + datetime.timedelta(minutes=3))
        w = [m for lv, m in rec.lines if lv == "WARNING"]
        i = [m for lv, m in rec.lines if "해소" in m]
        assert len(w) == 1 and "계측만" in w[0] and len(i) == 1

    _with_log(run)


# ── F3 수집 실패 시 시간청산 ─────────────────────────────────────────────────

class _Pos(object):
    def __init__(self, ext, qty=2):
        self._ext = ext
        self.quantity = qty

    def is_external_of(self, src):
        return self._ext == src


class _FF(object):
    _shindong_fetch_fail_guard = TS._shindong_fetch_fail_guard

    def __init__(self, ext):
        self.position = _Pos(ext)
        self._sd_fetch_fail_exit_logged = None
        self.exits = []

    def _shindong_exit(self, reason, why=""):
        self.exits.append((reason, why))


def test_F3_time_exit_when_fetch_fails():
    s = _FF(main.SHINDONG_ENTRY_SOURCE)
    rec = _with_log(lambda r: s._shindong_fetch_fail_guard(datetime.datetime(2026, 10, 26, 15, 5, 3)))
    assert s.exits and s.exits[0][0] == "신동시간청산"
    assert any("7222 수집 실패 중" in m for _, m in rec.lines)
    # 같은 날 반복 호출은 로그 1회(청산 시도는 계속 — pending 가드는 _shindong_exit 가 갖는다)
    rec2 = _with_log(lambda r: s._shindong_fetch_fail_guard(datetime.datetime(2026, 10, 26, 15, 6, 3)))
    assert len(s.exits) == 2 and not rec2.lines


def test_F3_no_action_before_time_or_other_owner():
    s = _FF(main.SHINDONG_ENTRY_SOURCE)
    _with_log(lambda r: s._shindong_fetch_fail_guard(datetime.datetime(2026, 10, 26, 15, 4, 59)))
    assert not s.exits
    s2 = _FF("PETER2")
    _with_log(lambda r: s2._shindong_fetch_fail_guard(datetime.datetime(2026, 10, 26, 15, 6)))
    assert not s2.exits


def test_F3_wired_into_fetch_failure_branch():
    src = inspect.getsource(TS._fetch_weekly_option_flow)
    i_exc = src.rindex("except Exception as e:")
    assert "self._shindong_fetch_fail_guard(now)" in src[i_exc:]
    gsrc = inspect.getsource(TS._shindong_entry_block_reason)
    assert "self._shindong_flow_stale_block()" in gsrc
    rsrc = inspect.getsource(TS._run_shindong)
    assert rsrc.index("self._shindong_flow_stale_check(payload, now)") < rsrc.index("self._shindong_exec_step(payload, now)")
