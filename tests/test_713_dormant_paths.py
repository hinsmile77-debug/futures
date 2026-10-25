# -*- coding: utf-8 -*-
"""[MW0601 713차 / 신동 주체 전환 P3] 미륵 휴면 — 기동·장전·장후·재학습·신동 EOD 경로 회귀.

지키는 불변식
  D1  엔진 스위치는 __init__ 맨 앞에서 읽는다 — RF 로드·보정기 사전학습·앙상블 보정기 복원보다 먼저.
  D2  재학습 서브프로세스는 휴면이면 띄우지 않는다(Popen 은 한 곳뿐, 그 입구에서 막는다).
  D3  장전 준비는 휴면이면 현재가 스냅샷 뒤 반환한다(Canary·ScalerWarmup·PreRetrain 생략).
  D4  08:45 휴면 분기는 스케일러 재적합 없이 **실시간 선행 구독을 한다** — 프리장 봉·08:50 맥점의 원천.
  D5  장후 마감: 학습 상태 파일 저장(보정기·MetaConf)·재보정·CUSUM·Registry·Phase5 는 휴면 게이트 안,
      브로커 net 확정·대사·신동 리포트·가상 장부·일일 리셋은 게이트 밖이다.
  D6  scripts/shindong_eod.py 종료코드 규약(0 정상 · 1 신선도 결손 · 2 캐시 갱신 실패) · 완료 마커 · 장중 거부.
"""
import ast
import io
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()


def _methods():
    tree = ast.parse(SRC)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "TradingSystem":
            return [n for n in node.body if isinstance(n, ast.FunctionDef)]
    raise AssertionError


def _body(name):
    ms = _methods()
    for i, n in enumerate(ms):
        if n.name == name:
            end = ms[i + 1].lineno - 1 if i + 1 < len(ms) else None
            return "\n".join(SRC.splitlines()[n.lineno - 1:end])
    raise AssertionError(name)


def test_D1_engine_read_first_in_init():
    b = _body("__init__")
    i_eng = b.index("self._mireuk_engine = _me_raw")
    for later in ("self.broker        = create_broker()", "self.rf_model.load_all()",
                  "self._preload_horizon_calibration()", "self._restore_ensemble_calibrator()"):
        assert i_eng < b.index(later), later
    assert b.count("self._mireuk_engine = _me_raw") == 1
    # 세 로드가 모두 휴면 조건 아래에 있다
    for call in ("self.rf_model.load_all()", "self._preload_horizon_calibration()",
                 "self._restore_ensemble_calibrator()", "self._ensure_shap_tracker()"):
        seg = b[:b.index(call)]
        assert seg.rstrip().endswith("if self._mireuk_on():"), call


def test_D2_retrain_spawn_blocked_at_entry():
    b = _body("_start_gbm_retrain_subprocess")
    assert b.index("if not self._mireuk_on():") < b.index("subprocess.Popen(")
    assert SRC.count("subprocess.Popen(") == 1          # 재학습 spawn 은 이 한 곳뿐이어야 게이트가 충분하다


def test_D2b_warmup_retrain_not_scheduled_when_dormant():
    i = SRC.index("[WarmupRetrain] 세션 재시작 감지 — 미륵 휴면이라 재학습 예약 안 함")
    seg = SRC[i - 600:i]
    assert "if self._mireuk_on():" in seg and "self._warmup_retrain_pending = True" in seg


def test_D3_premarket_setup_returns_after_snapshot():
    b = _body("pre_market_setup")
    i_snap = b.index("_rd._prime_from_snapshot()")
    i_off = b.index("if not self._mireuk_on():", i_snap)
    i_ret = b.index("return", i_off)
    i_canary = b.index("# ── Warm Scaler Canary")
    assert i_snap < i_off < i_ret < i_canary
    assert b.index("self.meta_gate.learner.load(") > b.index("if self._mireuk_on():")


def test_D4_dormant_early_warmup_subscribes_without_refit():
    i = SRC.index('"[EarlyWarmup] 미륵 휴면 — 스케일러 재적합 생략')
    seg = SRC[SRC.rindex("if (", 0, i):SRC.index("if (", i)]
    assert "and not self._mireuk_on()" in seg
    assert "_rd_ew.start(load_history=True)" in seg
    assert "refit_scalers_only" not in seg and "self._scaler_refresh_running = True" not in seg
    # 휴면 분기가 종전 분기보다 앞이다 — 같은 틱에 종전 분기가 먼저 _early_warmup_started 를 세우지 않게
    assert i < SRC.index('f"[EarlyWarmup] scaler 노후=')


def test_D4b_dormant_skips_intraday_and_ecb_scaler_refit():
    assert "[StartupWarmup] 미륵 휴면 — 장중 재기동 스케일러 재적합 생략" in SRC
    b = _body("_post_exchange_cb_resume")
    assert b.index("if not self._mireuk_on():") < b.index("def _ecb_scaler_worker")


def _gated(body, needle):
    """needle 이 `if self._mireuk_on():` 블록(들여쓰기 12칸 이상) 안에 있는가."""
    i = body.index(needle)
    line = body[body.rindex("\n", 0, i) + 1: body.index("\n", i)]
    indent = len(line) - len(line.lstrip())
    gate = body.rindex("        if self._mireuk_on():", 0, i)
    between = body[gate:i].splitlines()[1:-1]
    # 게이트 이후 needle 까지 들여쓰기 8칸 이하의 비어 있지 않은 줄이 없어야 같은 블록이다
    return indent >= 12 and all((len(l) - len(l.lstrip()) > 8) or not l.strip() for l in between)


@pytest.mark.parametrize("needle", [
    "self.meta_gate.learner.save(META_CONF_STATE_PATH)",
    "if _cal.save(ENSEMBLE_CALIBRATOR_PATH):",
    "self._gbm_retrain_done_event.wait(timeout=20 * 60)",
    "self.daily_consolidator.consolidate()",
    "_ext_fit = self.extremity_corrector.fit_all()",
    "insert_daily(",
    "_reg_now.record_live_snapshot(",
    "_exp.save(_report)",
    "self._load_shadow_candidate()",
])
def test_D5_mireuk_only_items_gated(needle):
    assert _gated(_body("daily_close"), needle), needle


@pytest.mark.parametrize("needle", [
    "self.position.reset_daily()",
    "self.circuit_breaker.reset_daily()",
    "self.profit_guard.reset_daily()",
    "self._sys_daily_net_krw = 0.0",
    "self.online_learner.reset_daily()",
    '"sgd_accuracy":   _today_accuracy,',
])
def test_D5_shared_items_not_gated(needle):
    b = _body("daily_close")
    i = b.index(needle)
    line = b[b.rindex("\n", 0, i) + 1: b.index("\n", i)]
    assert len(line) - len(line.lstrip()) <= 12, needle


def test_D5_accuracy_read_outside_gate():
    b = _body("daily_close")
    i = b.index("_today_accuracy = self.online_learner.recent_accuracy()")
    line = b[b.rindex("\n", 0, i) + 1: b.index("\n", i)]
    assert line.startswith("        _today") and not line.startswith("            ")


# ── D6 신동 EOD ─────────────────────────────────────────────────────────────
from scripts import shindong_eod as SE  # noqa: E402


class _Log(object):
    def __init__(self):
        self.lines = []

    def info(self, *a):
        self.lines.append(("I", a))

    def warning(self, *a):
        self.lines.append(("W", a))

    def error(self, *a):
        self.lines.append(("E", a))


@pytest.fixture()
def eod(tmp_path, monkeypatch):
    monkeypatch.setattr(SE, "_ROOT", str(tmp_path))
    (tmp_path / "data").mkdir()
    return tmp_path


def _steps(levels, reg="ok", of="ok"):
    return {"levels": lambda: levels,
            "regular": lambda: {"status": reg, "line": "[RegularFresh] %s" % reg},
            "option_flow": lambda: {"status": of, "line": "[OptionFlowFresh] %s" % of}}


def test_D6_all_ok_exit0_and_marker(eod):
    out = SE.run("2026-10-26", wait=False, log=_Log(),
                 steps=_steps({"refreshed": {"last_date": "2026-10-26", "sessions": 120}}))
    assert out["exit_code"] == 0
    assert (eod / "data" / "shindong_eod_done_20261026.txt").exists()


def test_D6_stale_cache_or_freshness_gap_exit1(eod):
    assert SE.run("2026-10-26", wait=False, log=_Log(),
                  steps=_steps({"refreshed": {"last_date": "2026-10-23"}}))["exit_code"] == 1
    assert SE.run("2026-10-26", wait=False, log=_Log(),
                  steps=_steps({"refreshed": {"last_date": "2026-10-26"}}, of="stale"))["exit_code"] == 1


def test_D6_cache_refresh_failure_exit2(eod):
    assert SE.run("2026-10-26", wait=False, log=_Log(), steps=_steps({}))["exit_code"] == 2

    def boom():
        raise RuntimeError("db locked")
    st = _steps(None)
    st["levels"] = boom
    assert SE.run("2026-10-26", wait=False, log=_Log(), steps=st)["exit_code"] == 2


def test_D6_refuses_intraday(monkeypatch):
    import datetime as _dt

    class _Now(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 10, 26, 10, 0)
    monkeypatch.setattr(SE.datetime, "datetime", _Now)
    assert SE.main([]) == 2


def test_D6_task_files_are_ascii_crlf():
    for rel in ("TASK_SHINDONG_EOD_INSTALL.bat", os.path.join("scripts", "shindong_eod_task.ps1")):
        b = io.open(os.path.join(ROOT, rel), "rb").read()
        assert all(c < 128 for c in bytearray(b)), rel
        assert b.count(b"\r\n") == b.count(b"\n"), rel
    ps = io.open(os.path.join(ROOT, "scripts", "shindong_eod_task.ps1"), encoding="ascii").read()
    assert "'MireukiEODRetrain'" in ps                 # MW0601 재학습 작업 이름
    assert "LastTaskResult -ne 0" in ps                # 신동 EOD 성공 전 재학습 비활성 거부
