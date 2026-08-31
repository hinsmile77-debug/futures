# -*- coding: utf-8 -*-
"""[MW0601 507차 후속 / F-7 · F-12 · G-4] PSI 기준선 키 불일치 · 미측정 표기.

**이 사고의 지문을 회귀로 박는다.**

2026-08-31: `data/regime_fingerprint.json` 은 08-28에 저장된 구세대 CORE
(`cvd_divergence` / `vwap_position` / `ofi_norm`)를 담고 있었고, 코드 상수는
500차 CORE 통합으로 (`cvd_delta_norm` / `vwap_position` / `ofi_pressure`)였다.
`update_live()` 가 `self._live_buf[feat]` 에서 KeyError 로 죽었고, 호출부가 그
예외를 5분 스로틀 WARNING 으로만 삼켜 **하루 종일 PSI 가 없는데도** EOD 패널은
`PSI : 0.000 (CLEAR)` 를 찍었다 — 가장 조용한 정상처럼 보였다.

F-7 = 읽는 쪽에서 흡수 / F-12 = 미측정을 0.000 으로 렌더링하지 않음 /
G-4 = 기동 시 세대 대사 1회.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from strategy.regime_fingerprint import (          # noqa: E402
    RegimeFingerprint, _CORE_FEATURES, _N_BINS,
)

# ── 08-28자 실제 파일의 키 구성(값은 합성) — 이 사고의 지문 ──────────────────
LEGACY_KEYS = ("cvd_divergence", "vwap_position", "ofi_norm")


def _fake_feature_block(lo=0.0, hi=1.0):
    step = (hi - lo) / _N_BINS
    edges = [lo + step * i for i in range(_N_BINS + 1)]
    props = [1.0 / _N_BINS] * _N_BINS
    return {"edges": edges, "props": props}


def _write_baseline(path, keys, saved_at="2026-08-28 15:47:30", core=None):
    payload = {"saved_at": saved_at,
               "features": {k: _fake_feature_block() for k in keys}}
    if core is not None:
        payload["core_features"] = list(core)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)


@pytest.fixture()
def legacy_fp(tmp_path):
    p = str(tmp_path / "regime_fingerprint.json")
    _write_baseline(p, LEGACY_KEYS)
    return RegimeFingerprint(fp_path=p)


# ── F-7 ──────────────────────────────────────────────────────────────────────
def test_a_legacy_keys_are_dropped_on_load(legacy_fp):
    """ⓐ 코드 CORE 에 없는 키는 로드 단계에서 버려진다.

    `vwap_position` 만 두 세대에 공통이므로 살아남는다.
    """
    loaded = set(legacy_fp._training.keys())
    assert loaded <= set(_CORE_FEATURES), "코드 CORE 밖의 키가 살아남았다"
    assert "cvd_divergence" not in loaded
    assert "ofi_norm" not in loaded


def test_b_update_live_survives_key_mismatch(legacy_fp):
    """ⓑ 구세대 기준선을 물고도 `update_live()` 가 **예외 없이** 돈다.

    이것이 08-31에 하루치 PSI 를 통째로 날린 KeyError 다.
    """
    feats = {f: 0.5 for f in _CORE_FEATURES}
    for _ in range(_N_BINS * 5 + 5):
        legacy_fp.update_live(feats)      # 터지면 그 자체가 실패다


def test_c_psi_is_none_when_nothing_measurable(tmp_path):
    """ⓒ 필터로 기준선이 통째로 비면 `get_psi() is None` — 0.0 이 아니다."""
    p = str(tmp_path / "fp.json")
    _write_baseline(p, ("cvd_divergence", "ofi_norm"))   # 공통 키 없음
    fp = RegimeFingerprint(fp_path=p)
    assert fp._training == {}
    fp._training = {}          # 부트스트랩이 끼어들지 못하게 고정
    assert fp.get_psi() is None
    assert fp.psi_measured() is False
    assert fp.get_per_feature_psi() == {}


# ── F-12 ─────────────────────────────────────────────────────────────────────
def test_d_fresh_instance_starts_unmeasured(tmp_path):
    """ⓓ 기준선 파일이 없는 새 인스턴스는 **미측정**으로 시작한다(0.0 아님)."""
    fp = RegimeFingerprint(fp_path=str(tmp_path / "none.json"))
    assert fp.get_psi() is None
    assert fp.psi_measured() is False


def test_e_update_live_returns_none_without_baseline(tmp_path):
    """ⓔ 기준선도 표본도 없으면 `update_live()` 가 `None` 을 돌려준다."""
    fp = RegimeFingerprint(fp_path=str(tmp_path / "none.json"))
    assert fp.update_live({f: 0.5 for f in _CORE_FEATURES}) is None


def test_f_measured_psi_is_float(tmp_path):
    """ⓕ 정상 계산 후에는 종전과 같이 float 를 돌려준다(회귀)."""
    p = str(tmp_path / "fp.json")
    _write_baseline(p, _CORE_FEATURES, core=_CORE_FEATURES)
    fp = RegimeFingerprint(fp_path=p)
    assert set(fp._training.keys()) == set(_CORE_FEATURES)
    val = None
    for i in range(_N_BINS * 5 + 5):
        val = fp.update_live({f: 0.5 + 0.001 * (i % 7) for f in _CORE_FEATURES})
    assert isinstance(val, float)
    assert fp.psi_measured() is True
    assert isinstance(fp.get_psi(), float)


def test_g_exporter_never_prints_zero_clear_when_unmeasured(tmp_path, monkeypatch):
    """ⓖ 미측정일 때 EOD 패널 문자열에 `0.000` 도 `CLEAR` 도 나오지 않는다.

    08-31에 사람을 속인 것은 계산이 아니라 **이 한 줄**이었다.
    """
    import strategy.ops.daily_exporter as de
    fp = RegimeFingerprint(fp_path=str(tmp_path / "none.json"))
    monkeypatch.setattr("strategy.regime_fingerprint.get_fingerprint", lambda: fp)

    lines = []

    class _Probe(object):
        """`daily_exporter` 의 PSI 블록만 떼어 재현한다 — 파일 전체를 돌리면
        Registry·DB 등 무관한 의존이 붙는다."""

        @staticmethod
        def render():
            from strategy.regime_fingerprint import get_fingerprint
            f = get_fingerprint()
            psi = f.get_psi()
            if psi is None:
                lines.append("  PSI     : 미측정 (오늘 update_live 성공 0회 — 0.000이 아니다)")
            else:
                lines.append("  PSI     : %.3f" % psi)
            fpf = f.get_per_feature_psi()
            lines.append("  PSI/feat: " + ("미측정" if not fpf else "…"))

    _Probe.render()
    body = "\n".join(lines)
    assert "미측정" in body
    # 값 자리에 숫자가 오면 안 된다 — `0.000이 아니다` 라는 **설명문**은 허용한다.
    import re as _re
    assert _re.search(r"PSI\s+:\s*\d", body) is None, "미측정인데 숫자를 찍었다"
    assert "(CLEAR)" not in body, "미측정을 CLEAR 로 라벨링했다"
    # 실물 소스에도 같은 규약이 박혀 있는지 확인 — 위 재현이 낡지 않게 한다.
    src = open(de.__file__.replace(".pyc", ".py"), encoding="utf-8").read()
    assert "미측정 (오늘 update_live 성공 0회" in src


# ── G-4 ──────────────────────────────────────────────────────────────────────
def test_h_state_recon_reports_generation_gap(legacy_fp):
    """ⓗ 기동 대사가 「파일에만 / 코드에만」을 각각 이름으로 보고한다."""
    r = legacy_fp.baseline_key_recon()
    assert r["file_exists"] is True
    assert r["saved_at"] == "2026-08-28 15:47:30"
    assert set(r["extra"]) == {"cvd_divergence", "ofi_norm"}
    assert set(r["missing"]) == set(_CORE_FEATURES) - {"vwap_position"}
    assert r["loaded"] == ["vwap_position"]


def test_i_state_recon_clean_when_generations_match(tmp_path):
    """ⓘ 세대가 맞으면 불일치 0 — 경보를 만들지 않는다(오탐 방지)."""
    p = str(tmp_path / "fp.json")
    _write_baseline(p, _CORE_FEATURES, core=_CORE_FEATURES)
    r = RegimeFingerprint(fp_path=p).baseline_key_recon()
    assert r["missing"] == [] and r["extra"] == []


def test_j_state_recon_handles_missing_file(tmp_path):
    """ⓙ 파일이 없으면 「기준선 미보유」로 보고한다 — 예외로 죽지 않는다."""
    r = RegimeFingerprint(fp_path=str(tmp_path / "nope.json")).baseline_key_recon()
    assert r["file_exists"] is False
    assert set(r["missing"]) == set(_CORE_FEATURES)


def test_k_saved_baseline_carries_core_features(tmp_path):
    """ⓚ 새로 저장하는 기준선에는 저장 당시 코드 CORE 가 함께 박힌다."""
    p = str(tmp_path / "fp.json")
    fp = RegimeFingerprint(fp_path=p)
    fp._training = {f: (_fake_feature_block()["edges"],
                        _fake_feature_block()["props"]) for f in _CORE_FEATURES}
    fp._save_fingerprint()
    with open(p, encoding="utf-8") as f:
        payload = json.load(f)
    assert payload["core_features"] == list(_CORE_FEATURES)
