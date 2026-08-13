# -*- coding: utf-8 -*-
"""[MW0602 468차 G-1] 사이즈 제한 해제를 "이벤트"→"상태"로 바꾼 것의 회귀 테스트.

지키려는 불변식:
  1. **모르면 해제하지 않는다.** 사이드카 없음 / `label_scheme` 없음(468차 이전) /
     JSON 파손 / 폴더 없음 → 전부 False. "모른다"를 "괜찮다"로 바꾸지 않는다.
  2. **전부 일치해야 True.** 6개 중 1개라도 어긋나면 False(부분 일치 금지).
  3. **임계값까지 본다.** 스키마가 같아도 `HORIZON_THRESHOLDS`가 재보정되면(387차 선례)
     구모델은 낡은 것이므로 False.
  4. 해제는 **켜는 쪽으로만** — 이미 True인 플래그를 되돌리지 않는다.
  5. 킬스위치 `MODEL_LABEL_STATE_UNLOCK_ENABLED=False`면 종전 동작.
  6. 사이드카 기록부(batch_retrainer)가 **두 경로 모두**에서 label_scheme을 남긴다
     (Phase 2 EOD 주경로를 빼먹으면 G-1이 조용히 무력화된다).

실행: python tests/test_468_label_state_unlock.py   (COM/PyQt/DB 불필요)
"""
from __future__ import print_function

import io
import json
import os
import shutil
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from learning.model_meta import read_label_state  # noqa: E402

HZ = ["1m", "3m", "5m", "10m", "15m", "30m"]
THRESH = {"1m": 0.00075, "3m": 0.00136, "5m": 0.00182,
          "10m": 0.00273, "15m": 0.00328, "30m": 0.00476}

_FAILS = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        _FAILS.append(name)


def _want(hz):
    return THRESH[hz]


def _mkdir_with(sidecars):
    """sidecars: {hz: dict|None}  — None이면 파일을 만들지 않는다."""
    d = tempfile.mkdtemp(prefix="g1_meta_")
    for hz, meta in sidecars.items():
        if meta is None:
            continue
        with io.open(os.path.join(d, "gbm_%s_meta.json" % hz), "w", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False))
    return d


def _good(hz):
    return {"horizon": hz, "written_at": "2026-08-14 15:45:00", "source": "eod",
            "acc": 0.43, "acc_kind": "cv",
            "label_scheme": "fixed", "label_param": THRESH[hz]}


def test_all_current():
    print("\n-- test_all_current")
    d = _mkdir_with(dict((h, _good(h)) for h in HZ))
    try:
        ok, why = read_label_state(d, HZ, "fixed", _want)
        check("6/6 현행이면 True (%s)" % why, ok is True)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_unknown_is_false():
    print("\n-- test_unknown_is_false  (불변식 1)")
    # (a) 사이드카 1개 없음
    s = dict((h, _good(h)) for h in HZ)
    s["30m"] = None
    d = _mkdir_with(s)
    try:
        ok, why = read_label_state(d, HZ, "fixed", _want)
        check("사이드카 1개 없음 → False (%s)" % why, ok is False and "사이드카없음" in why)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # (b) 468차 이전 사이드카 (label_scheme 필드 없음)
    s = dict((h, _good(h)) for h in HZ)
    old = dict(_good("5m"))
    del old["label_scheme"]
    del old["label_param"]
    s["5m"] = old
    d = _mkdir_with(s)
    try:
        ok, why = read_label_state(d, HZ, "fixed", _want)
        check("label_scheme 없는 구버전 → False (%s)" % why,
              ok is False and "구버전" in why)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # (c) JSON 파손
    d = _mkdir_with(dict((h, _good(h)) for h in HZ))
    try:
        with io.open(os.path.join(d, "gbm_1m_meta.json"), "w", encoding="utf-8") as f:
            f.write("{not json")
        ok, why = read_label_state(d, HZ, "fixed", _want)
        check("JSON 파손 → False (%s)" % why, ok is False and "판독실패" in why)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # (d) 폴더 자체가 없음 / 인자 누락
    ok, _ = read_label_state(os.path.join(BASE, "__no_such_dir__"), HZ, "fixed", _want)
    check("폴더 없음 → False", ok is False)
    ok, _ = read_label_state(None, HZ, "fixed", _want)
    check("model_dir=None → False", ok is False)
    ok, _ = read_label_state("x", [], "fixed", _want)
    check("horizons 비었음 → False", ok is False)


def test_partial_is_false():
    print("\n-- test_partial_is_false  (불변식 2)")
    s = dict((h, _good(h)) for h in HZ)
    s["10m"] = dict(_good("10m"), label_scheme="rolling_sigma")
    d = _mkdir_with(s)
    try:
        ok, why = read_label_state(d, HZ, "fixed", _want)
        check("1개만 다른 스키마여도 False (%s)" % why, ok is False)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_threshold_drift():
    print("\n-- test_threshold_drift  (불변식 3 — 387차 재보정 선례)")
    s = dict((h, _good(h)) for h in HZ)
    s["3m"] = dict(_good("3m"), label_param=0.00060)   # 재보정 전 값으로 학습된 구모델
    d = _mkdir_with(s)
    try:
        ok, why = read_label_state(d, HZ, "fixed", _want)
        check("스키마 같아도 임계 다르면 False (%s)" % why, ok is False and "임계" in why)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # 파라미터 비교를 끄면(want_param_of=None) 스키마만 본다
    d2 = _mkdir_with(s)
    try:
        ok, _ = read_label_state(d2, HZ, "fixed", None)
        check("want_param_of=None이면 스키마만 비교", ok is True)
    finally:
        shutil.rmtree(d2, ignore_errors=True)

    # label_param 자체가 없으면 "모른다" → False
    s2 = dict((h, _good(h)) for h in HZ)
    m = dict(_good("15m"))
    del m["label_param"]
    s2["15m"] = m
    d3 = _mkdir_with(s2)
    try:
        ok, why = read_label_state(d3, HZ, "fixed", _want)
        check("label_param 없음 → False (%s)" % why, ok is False and "label_param없음" in why)
    finally:
        shutil.rmtree(d3, ignore_errors=True)


def test_wiring():
    print("\n-- test_wiring  (불변식 4·5·6)")
    with io.open(os.path.join(BASE, "main.py"), encoding="utf-8") as f:
        m = f.read()
    check("해제는 켜는 쪽으로만 (이미 True면 조기 반환)",
          'if getattr(self, "_pre_retrain_done", False):\n            return True' in m)
    check("킬스위치를 getattr 기본값과 함께 읽는다",
          'getattr(runtime_settings, "MODEL_LABEL_STATE_UNLOCK_ENABLED", True)' in m)
    check("장전 경로에서 호출", '_refresh_pre_retrain_state("장전")' in m)
    check("장중 첫 확인(재시작 사각지대) 경로에서 호출",
          '_refresh_pre_retrain_state("장중 첫 확인")' in m)
    check("하루 1회 가드가 있다", "_label_state_checked_date" in m)
    check("F-1(마커) 경로를 지우지 않았다",
          "PRE_RETRAIN_DONE_BY_EOD_ENABLED" in m and "eod_retrain_done_" in m)

    with io.open(os.path.join(BASE, "learning", "batch_retrainer.py"), encoding="utf-8") as f:
        b = f.read()
    check("사이드카에 label_scheme 기록", '"label_scheme":' in b)
    check("사이드카에 label_param 기록", '"label_param":' in b)
    # 두 학습 경로 모두에서 남겨야 한다 — Phase 2(EOD 주경로)를 빼먹으면 무력화된다
    check("학습 경로 2곳 모두에서 _last_label_scheme 설정",
          b.count("self._last_label_scheme") >= 3)

    with io.open(os.path.join(BASE, "config", "settings.py"), encoding="utf-8") as f:
        s = f.read()
    check("킬스위치 상수 정의", "MODEL_LABEL_STATE_UNLOCK_ENABLED" in s)


def test_live_sidecars():
    print("\n-- test_live_sidecars (있을 때만 — 라이브 상태 진단)")
    d = os.path.join(BASE, "model", "horizons")
    if not os.path.isdir(d):
        print("[SKIP] model/horizons 없음")
        return
    ok, why = read_label_state(d, HZ, "fixed", _want)
    print("    라이브 판정: %s — %s" % (ok, why))
    print("    (배포 직후 첫 EOD 전이면 `label_scheme없음(구버전)`이 정상이다 — "
          "그 구간은 F-1 마커 경로가 덮는다)")


if __name__ == "__main__":
    test_all_current()
    test_unknown_is_false()
    test_partial_is_false()
    test_threshold_drift()
    test_wiring()
    test_live_sidecars()
    print("\n" + "=" * 60)
    if _FAILS:
        print("실패 %d건:" % len(_FAILS))
        for f in _FAILS:
            print("  - %s" % f)
        sys.exit(1)
    print("468차 G-1 레이블 상태 해제 회귀 테스트 전부 통과")
