"""[MW0602 신동 주체 리뉴얼] PRINCIPAL_LOCK — 거래주체 고정 회귀 테스트.

  K1 유효한 고정값이면 파일과 무관하게 그 주체 · locked=True
  K2 알 수 없는 고정값은 고정하지 않는다(파일 선택) — 오타로 엉뚱한 주체가 고정되지 않게
  K3 save() 의 이력 prev 는 파일 기준(load_file) — 고정 중 기록이 고정값으로 오염되지 않는다
  K4 main 전환 처리기가 고정 중 전환을 거부하고 파일을 바꾸지 않는다(소스 수준)
  K5 고정이 없을 때 load() 는 종전과 같은 키 + locked=False
"""
import inspect
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from strategy.runtime import trade_principal as TP  # noqa: E402


def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(TP, "STATE_PATH", str(tmp_path / "trade_principal.json"))
    monkeypatch.setattr(TP, "LOG_PATH", str(tmp_path / "trade_principal_log.jsonl"))


def test_K1_lock_overrides_file(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    TP.save(TP.MIREUK, reason="t")
    d = TP.load(lock="shindong")
    assert d["principal"] == TP.SHINDONG and d["locked"] is True and d["measured"] is True
    assert TP.load_file()["principal"] == TP.MIREUK            # 파일은 그대로


def test_K2_unknown_lock_is_ignored(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    TP.save(TP.PETER, reason="t")
    assert TP.locked_principal("SHINDONGG") is None
    d = TP.load(lock="SHINDONGG")
    assert d["principal"] == TP.PETER and d["locked"] is False


def test_K3_save_prev_uses_file(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    monkeypatch.setattr(TP, "locked_principal", lambda lock=None: TP.SHINDONG)
    TP.save(TP.MIREUK, reason="a")
    TP.save(TP.PETER, reason="b")
    lines = [json.loads(x) for x in io.open(TP.LOG_PATH, encoding="utf-8")]
    assert lines[-1]["prev"] == TP.MIREUK                      # 고정값(SHINDONG)이 아니다


def test_K4_main_rejects_switch_when_locked():
    import main
    src = inspect.getsource(main.TradingSystem._on_principal_change_requested)
    i_lock = src.index('if self._principal_state.get("locked"):')
    i_save = src.index("principal_mod.save(")
    assert i_lock < i_save
    assert "PRINCIPAL_LOCK" in src[i_lock:i_save]
    lsrc = inspect.getsource(main.TradingSystem._principal_locked)
    assert 'self._principal_state.get("locked")' in lsrc


def test_K5_no_lock_keeps_legacy_shape(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    monkeypatch.setattr(TP, "locked_principal", lambda lock=None: None)
    d = TP.load()
    assert d == {"principal": TP.DEFAULT, "set_at": None, "reason": "default(파일 없음)",
                 "measured": False, "locked": False}


def test_settings_defaults_are_conservative():
    from config import settings as S
    # [2026-10-25 사용자 결정] Sindong-V4 브랜치 = 신동 주체 · 미륵 휴면(CLAUDE.md 「브랜치 역할」).
    # 머지 시점(full/None)은 dev 브랜치에 그대로 남아 있다 — 미륵 부활은 그쪽에서 한다.
    assert S.MIREUK_ENGINE == "off"
    assert S.PRINCIPAL_LOCK == "SHINDONG"
    assert S.LIGHT_PASS_DRY_RUN is False      # off 에서는 의미 없음(full 전용)
    assert S.SHINDONG_FLOW_STALE_GUARD in ("off", "shadow", "live")
