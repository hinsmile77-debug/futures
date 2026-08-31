# -*- coding: utf-8 -*-
"""[MW0602 507차 후속] F-11 회귀 — PSI 기준선 정의가 바뀌면 **저장하는 쪽이 스스로 신고**한다.

**무엇이 문제였나.** 2026-08-31 15:47:39 EOD 가 PSI 감시 피처를 통째로 갈았다
(`cvd_divergence,vwap_position,ofi_norm` → `cvd_delta_norm,ofi_pressure,vwap_position`,
500차 3단계 「PSI 가 실집행 CORE 를 잰다」). 그런데 그 사실이 어디에도 마커로 남지
않아, 26주 WFA 재검증·372차 임계 재보정·전략 리포트 배너 **세 곳이** 그날 앞뒤 PSI 를
이어 붙여 읽게 돼 있었다. 461차가 `mdd_pct` 분모 혼동으로 **잘못된 전략 교체 권고**를
낸 것과 같은 계열이며, 이 시스템이 불연속 마커를 **사후에** 붙인 것이 이번이 네 번째다
(461차 분모 · 493차 요율 · 501차 후속 `broker_net_krw` · 이번 PSI).

여기서 고정하는 불변식:

① **집합이 같으면 아무것도 남기지 않는다** — 무조건 발행이면 매 EOD 마커가 쌓여
   그 자체가 노이즈가 되고, 진짜 불연속이 묻힌다.
② **피처 집합이 바뀌면 `METRIC_REDEFINITION` 1행** — 그리고 원인이
   `CORE_DEF_CHANGE`(정의 변경)인지 `SAMPLE_COVERAGE`(그날 샘플 부족 스킵)인지
   구분해서 남긴다. 둘은 처분이 다르다(계측 4원칙 ②).
③ **최초 저장은 불연속이 아니다** — 비교 대상이 없다.
④ **저장본이 `core_def` 를 들고 다닌다** — 그것이 없으면 「정의가 바뀌었다」와
   「샘플이 부족해 한 피처가 빠졌다」를 영원히 구분할 수 없다.
⑤ 🔴 **PSI 계산·임계·차단은 무변경** — 이것은 기록 조치이지 전환기준 ⑦
   (`FP_CRITICAL_GRADE_BLOCK_ENABLED`) 의 해제가 아니다.

실행:
    py37_32\\python.exe tests/test_507_psi_baseline_redefinition_marker.py
"""
import json
import io
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import strategy.regime_fingerprint as rf  # noqa: E402

FAILURES = []


class _Recorder(object):
    """`StrategyRegistry.log_event` 대역 — 발행된 마커를 모은다."""

    def __init__(self):
        self.events = []

    def log_event(self, event_type="", message="", note="", version=None):
        self.events.append({"event_type": event_type, "message": message,
                            "note": note, "version": version})


class _Harness(object):
    """실제 DB·실제 설정을 건드리지 않고 `_save_fingerprint()` 만 돌린다."""

    def __init__(self):
        self.tmp = tempfile.mkdtemp(prefix="fp507_")
        self.path = os.path.join(self.tmp, "regime_fingerprint.json")
        self.rec = _Recorder()

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def save(self, feats, core_def):
        """`core_def` 를 그 시점 정의로 갈아끼운 뒤 저장 1회."""
        fp = rf.RegimeFingerprint.__new__(rf.RegimeFingerprint)
        fp._fp_path = self.path
        fp._training = dict((f, ([0.0, 1.0], [1.0])) for f in feats)

        old_core = rf._CORE_FEATURES
        rf._CORE_FEATURES = tuple(core_def)
        emit = fp._emit_redefinition_if_changed
        try:
            # 레지스트리 대역 주입 — 실제 strategy_registry.db 를 쓰지 않는다.
            def _patched(prev_feats, prev_core, new_feats, new_core, _e=emit):
                import config.strategy_registry as sr
                real = sr.StrategyRegistry
                sr.StrategyRegistry = lambda *a, **k: self.rec
                try:
                    return _e(prev_feats, prev_core, new_feats, new_core)
                finally:
                    sr.StrategyRegistry = real
            fp._emit_redefinition_if_changed = _patched
            fp._save_fingerprint()
        finally:
            rf._CORE_FEATURES = old_core

    def payload(self):
        return json.load(io.open(self.path, encoding="utf-8"))


_A = ["cvd_divergence", "ofi_norm", "vwap_position"]
_B = ["cvd_delta_norm", "ofi_pressure", "vwap_position"]


def _markers(rec):
    return [e for e in rec.events if e["event_type"] == "METRIC_REDEFINITION"]


# ── ③ 최초 저장은 불연속이 아니다 ───────────────────────────────────────────
def test_first_save_emits_no_marker():
    h = _Harness()
    try:
        h.save(_A, _A)
        assert _markers(h.rec) == [], \
            "최초 저장에 마커가 났다 — 비교 대상이 없는데 불연속이라고 말하고 있다"
    finally:
        h.close()


# ── ① 같으면 침묵한다 ───────────────────────────────────────────────────────
def test_unchanged_feature_set_stays_silent():
    h = _Harness()
    try:
        h.save(_A, _A)
        h.save(_A, _A)
        h.save(_A, _A)
        assert _markers(h.rec) == [], (
            "집합이 그대로인데 마커가 %d건 났다 — 무조건 발행은 노이즈다"
            % len(_markers(h.rec)))
    finally:
        h.close()


# ── ② 바뀌면 정확히 1행, 원인 분류가 붙는다 ─────────────────────────────────
def test_core_definition_change_emits_one_marker():
    h = _Harness()
    try:
        h.save(_A, _A)
        h.save(_B, _B)          # 2026-08-31 15:47 에 실제로 일어난 교체
        m = _markers(h.rec)
        assert len(m) == 1, "마커가 %d건 (1건이어야 한다)" % len(m)
        msg = m[0]["message"]
        assert "CORE_DEF_CHANGE" in msg, "원인 분류가 없다: %s" % msg
        for feat in _A + _B:
            assert feat in msg, "%s 가 마커에 없다 — 무엇이 무엇으로 바뀌었는지 남아야 한다" % feat
        assert "직접 비교 금지" in msg, "재인용 경고 문구가 없다"
        assert "effective_date=" in msg, "발생일이 없다"
    finally:
        h.close()


def test_sample_shortage_is_not_labelled_as_definition_change():
    """정의는 그대로인데 한 피처가 빠진 날 — 이것도 불연속이지만 원인이 다르다."""
    h = _Harness()
    try:
        h.save(_B, _B)
        h.save(_B[:2], _B)      # ofi_pressure 가 샘플 부족으로 스킵된 상황
        m = _markers(h.rec)
        assert len(m) == 1, "마커가 %d건" % len(m)
        assert "SAMPLE_COVERAGE" in m[0]["message"], \
            "샘플 부족 스킵이 정의 변경으로 기록됐다: %s" % m[0]["message"]
    finally:
        h.close()


def test_repeated_change_does_not_re_emit():
    """바뀐 뒤 같은 상태로 다시 저장하면 조용해야 한다 — 한 사건은 한 번만 센다."""
    h = _Harness()
    try:
        h.save(_A, _A)
        h.save(_B, _B)
        h.save(_B, _B)
        assert len(_markers(h.rec)) == 1, \
            "같은 교체가 %d번 기록됐다" % len(_markers(h.rec))
    finally:
        h.close()


# ── ④ 저장본이 정의를 들고 다닌다 ───────────────────────────────────────────
def test_payload_carries_core_def():
    h = _Harness()
    try:
        h.save(_B, _B)
        p = h.payload()
        assert p.get("core_def") == _B, \
            "core_def 가 저장되지 않았다 — 다음 세대가 원인을 구분할 수 없다: %r" % (p.get("core_def"),)
        assert sorted(p.get("features", {}).keys()) == sorted(_B)
    finally:
        h.close()


def test_legacy_payload_migration_is_silent():
    """구 저장본(`core_def` 없음) → 신 저장본으로의 **형식 이행 자체는 불연속이 아니다.**

    🔴 이것은 「미측정을 동일로 위장」(계측 4원칙 ②)이 아니다. 배포 시점 실물
    (`data/regime_fingerprint.json`, saved_at 2026-08-31 15:47:39)이 정확히 이 상태 —
    `core_def` 없음 + 피처는 **이미 새 집합** — 인데, 그 교체 사건은 **소급 1행으로
    이미 등록돼 있다**(`strategy_events` id=88). 여기서 또 발행하면 같은 사건이
    두 번 세어지고, 불변식 ①(같으면 침묵)도 깨진다.

    미측정이 감춰지지 않는다는 것은 **바로 아래 테스트**가 고정한다 — 구 저장본에서
    피처가 실제로 달라지면 `CORE_DEF_UNKNOWN` 으로 명시된다.
    """
    h = _Harness()
    try:
        h.save(_B, _B)
        p = h.payload()
        p.pop("core_def")
        with io.open(h.path, "w", encoding="utf-8") as f:
            f.write(json.dumps(p, ensure_ascii=False))
        h.save(_B, _B)          # 피처 키는 같고 core_def 만 없다
        assert _markers(h.rec) == [], \
            "형식 이행만으로 마커가 났다 — 소급 1행(id=88)과 중복된다: %r" % (h.rec.events,)
    finally:
        h.close()


def test_legacy_payload_with_changed_features_is_flagged_unknown():
    """구 저장본에서 피처가 실제로 달라지면 원인을 「모른다」로 명시한다(계측 4원칙 ②)."""
    h = _Harness()
    try:
        h.save(_A, _A)
        p = h.payload()
        p.pop("core_def")
        with io.open(h.path, "w", encoding="utf-8") as f:
            f.write(json.dumps(p, ensure_ascii=False))
        h.save(_B, _B)
        m = _markers(h.rec)
        assert len(m) == 1, "마커가 %d건" % len(m)
        assert "CORE_DEF_UNKNOWN" in m[0]["message"], (
            "직전 정의가 미기록인데 원인을 단정했다 — 「모른다」와 「정의가 바뀌었다」는 "
            "다르다: %s" % m[0]["message"])
    finally:
        h.close()


# ── ⑤ 차단·임계 무변경 ─────────────────────────────────────────────────────
def test_thresholds_and_block_flag_untouched():
    assert (rf._PSI_WATCH, rf._PSI_ALARM, rf._PSI_CRIT) == (0.10, 0.20, 0.30), \
        "PSI 임계가 바뀌었다 — F-11 은 기록 조치이지 임계 재설계가 아니다"
    from config import settings
    assert getattr(settings, "FP_CRITICAL_GRADE_BLOCK_ENABLED") is False, \
        "전환기준 ⑦ 한시예외가 풀렸다 — F-11 의 범위가 아니다(CLAUDE.md 절대원칙 §2)"


def test_marker_failure_is_logged_not_swallowed():
    """DB 가 죽어도 PSI 저장은 살아야 하고, 마커 실패는 조용히 넘어가면 안 된다."""
    h = _Harness()
    try:
        h.save(_A, _A)
        fp = rf.RegimeFingerprint.__new__(rf.RegimeFingerprint)
        fp._fp_path = h.path
        fp._training = dict((f, ([0.0, 1.0], [1.0])) for f in _B)
        old_core = rf._CORE_FEATURES
        rf._CORE_FEATURES = tuple(_B)
        import config.strategy_registry as sr
        real = sr.StrategyRegistry

        def _boom(*a, **k):
            raise RuntimeError("db down")
        sr.StrategyRegistry = _boom
        try:
            fp._save_fingerprint()          # 예외가 밖으로 새면 EOD 가 죽는다
        finally:
            sr.StrategyRegistry = real
            rf._CORE_FEATURES = old_core
        p = json.load(io.open(h.path, encoding="utf-8"))
        assert sorted(p["features"].keys()) == sorted(_B), \
            "마커 실패가 기준선 저장까지 말아먹었다"
    finally:
        h.close()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_first_save_emits_no_marker,
               test_unchanged_feature_set_stays_silent,
               test_core_definition_change_emits_one_marker,
               test_sample_shortage_is_not_labelled_as_definition_change,
               test_repeated_change_does_not_re_emit,
               test_payload_carries_core_def,
               test_legacy_payload_migration_is_silent,
               test_legacy_payload_with_changed_features_is_flagged_unknown,
               test_thresholds_and_block_flag_untouched,
               test_marker_failure_is_logged_not_swallowed):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
