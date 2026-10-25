"""[MW0602 Sindong-V4] 미륵 휴면 기동 최적화 회귀 테스트 (2026-10-25).

계기: start_Sindong.bat 론치 로그(launcher_20261025_112319) — 휴면인데도 기동 때 보정기 사전학습
18,000건(≈14초)·RF 로드·SHAP/지문 복원이 돌았고, 08:45 EarlyWarmup·장중 StartupWarmup·
거래소 CB 해제가 미륵 상태 파일(scaler_*.pkl)을 다시 쓰고 있었다(휴면 원칙 위반).

지키는 불변식
  D1  엔진 스위치는 __init__ 맨 앞에서 읽힌다 — GBM·RF·보정기 로드보다 앞.
  D2  휴면이면 RF 로드·보정기 사전학습·앙상블 보정기 복원을 부르지 않는다(full 은 그대로 부른다).
  D3  휴면 `_restore_analysis_buffers` 는 VP 버퍼만 채우고 raw_features 를 읽지 않는다.
  D4  08:45 휴면 분기는 실시간 선행 구독을 **하고** 스케일러 재적합은 **하지 않는다**.
      그 분기는 full 분기보다 앞이며 `_early_warmup_started` 를 세워 full 분기를 막는다.
  D5  장중 재기동 StartupWarmup·거래소 CB 해제의 스케일러 재적합은 휴면이면 생략된다.
  D6  표기 — 휴면이면 초기화·시작 배너·기동 알림이 신동으로 찍힌다(`[Engine] 미륵 엔진=off` 는 수집기가 읽어 무변경).
  D7  DynMC 기동 복원은 휴면에서도 값은 복원하되 로그는 요약 1줄이다.

실행: python -m pytest tests/test_sindong_v4_dormant_startup.py -q   (COM/브로커 불필요)
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402

TS = main.TradingSystem


def _init_src():
    return inspect.getsource(TS.__init__)


def _guarded(src, call):
    """call 줄 바로 앞 줄이 `if self._mireuk_on():` 인가."""
    lines = src.splitlines()
    idx = [i for i, l in enumerate(lines) if call in l and not l.strip().startswith("#")]
    assert idx, call
    return all(lines[i - 1].strip() == "if self._mireuk_on():" for i in idx)


# ── D1·D2 ──────────────────────────────────────────────────────────────────────

def test_D1_engine_read_before_model_loads():
    src = _init_src()
    i_eng = src.index("self._mireuk_engine = _me_raw")
    for later in ("MultiHorizonModel()", "RFHorizonModel()", "self._preload_horizon_calibration()",
                  "self._restore_ensemble_calibrator()"):
        assert i_eng < src.index(later), later
    assert src.count("self._mireuk_engine = _me_raw") == 1


def test_D2_learning_loads_guarded():
    src = _init_src()
    for call in ("self.rf_model.load_all()", "self._preload_horizon_calibration()",
                 "self._restore_ensemble_calibrator()"):
        assert _guarded(src, call), call


def test_D2b_shap_tracker_init_guarded():
    src = inspect.getsource(TS)
    i = src.index("        self._restore_analysis_buffers()\n")
    tail = src[i:i + 400]
    assert "if self._mireuk_on():\n            self._ensure_shap_tracker()" in tail


# ── D3 ─────────────────────────────────────────────────────────────────────────

class _FakeRestore(object):
    def __init__(self):
        self.vp_calls = 0

    def _mireuk_on(self):
        return False

    def _restore_vp_buffer(self):
        self.vp_calls += 1
        return 60


def test_D3_dormant_restore_only_vp(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("휴면인데 raw_features 를 읽었다")
    monkeypatch.setattr(main, "fetch_recent_raw_features", _boom)
    fake = _FakeRestore()
    TS._restore_analysis_buffers(fake)
    assert fake.vp_calls == 1


# ── D4·D5 ──────────────────────────────────────────────────────────────────────

def _sched_src():
    return inspect.getsource(TS._scheduler_tick)


def test_D4_early_warmup_dormant_branch_subscribes_without_refit():
    src = _sched_src()
    i = src.index("and not self._mireuk_on()\n        ):\n            self._early_warmup_started = True")
    j = src.index("        if (", i)
    block = src[i:j]
    assert "_rd_ew.start(load_history=True)" in block
    assert "refit_scalers_only" not in block
    assert "load_features_for_warmup" not in block
    # 휴면 분기가 full 분기(스케일러 재적합)보다 앞
    assert i < src.index("self.model.refit_scalers_only(_X_ew, _fn_ew)")


def test_D5_startup_warmup_dormant_guard_precedes_refit():
    src = _sched_src()
    g = src.index('logger.info("[StartupWarmup] 미륵 휴면')
    assert g < src.index('trigger_type="B_INTRADAY"')
    pre = src[max(0, g - 300):g]
    assert "not self._mireuk_on()" in pre and "self._intraday_startup_warmup_done = True" in pre


def test_D5b_exchange_cb_scaler_refit_dormant_skip():
    src = inspect.getsource(TS._post_exchange_cb_resume)
    i = src.index("if not self._mireuk_on():")
    assert i < src.index("elif not self._scaler_refresh_running:") < src.index("refit_scalers_only(")


# ── D6 ─────────────────────────────────────────────────────────────────────────

def test_D6_banners_follow_engine():
    src = _init_src()
    assert "신동 주체 초기화 (미륵 엔진 off)" in src
    run_src = inspect.getsource(TS.run)
    assert "신동 — KOSPI 200 미니선물 자동매매 시작" in run_src
    assert 'engine_label="미륵이" if self._mireuk_on() else "신동(미륵 엔진 off)"' in run_src
    # 점검 수집기(collect_shindong_evidence.py)가 이 문구를 센다 — 바꾸지 말 것
    assert "[Engine] 미륵 엔진=off" in src


def test_D6b_notify_startup_label(monkeypatch):
    import utils.notify as nt
    sent = []
    monkeypatch.setattr(nt, "_send", lambda m: sent.append(m))
    nt.notify_startup("A056B", "Cybos 실서버", engine_label="신동(미륵 엔진 off)")
    nt.notify_startup("A056B", "Cybos 실서버")
    assert "신동(미륵 엔진 off) 기동 완료" in sent[0]
    assert "미륵이 기동 완료" in sent[1]


# ── D7 ─────────────────────────────────────────────────────────────────────────

def test_D7_dynmc_restore_summarised_when_dormant():
    import strategy.entry.time_strategy_router as tsr
    src = inspect.getsource(tsr._restore_mc_from_history)
    assert "_log = logger.debug if _dorm else logger.info" in src
    assert 'logger.info("[DynMC] 기동 복원:' not in src          # 구간별 줄은 _log 경유
    assert "_ZONE_PARAMS[zone][\"min_confidence\"] = new_mc" in src   # 값 복원은 유지
