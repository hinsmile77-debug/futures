# -*- coding: utf-8 -*-
"""[MW0602 476차 F-1·F-3] EOD 사이드카 `label_scheme` 유실 수정의 회귀 테스트.

무엇이 문제였나 (0819 P1-1)
---------------------------
468차 G-1이 넣은 retrain_now() 가드는 "호출자가 X/y를 직접 넘기면 레이블 규칙을
모른다"며 무조건 None으로 지웠다. 그런데 프로덕션 호출자(retrain_eod.py)는
**같은 인스턴스의 _load_from_db() 반환값**을 되먹인다 — 가드가 그 경우를 구분하지
못해 유효한 규칙을 지웠고, 사이드카 6/6이 `label_scheme=null`로 3거래일 연속
기록됐다(G-1 상태 게이트가 영구 무력화될 뻔했다).

지키려는 불변식:
  1. **아는 X는 지우지 않는다.** _load_from_db()가 방금 만든 X(표식 id+shape 일치)를
     되먹이면 레이블 규칙이 보존된다 — retrain_eod.py 프로덕션 경로.
  2. **모르는 X는 여전히 지운다.** 표식 없음 / id 불일치 / shape 불일치 → None.
     468차의 보수 원칙("모르면 사이즈 제한 유지")은 그대로다.
  3. **실패한 로드는 표식을 남기지 않는다.** _load_from_db() 재호출 시 서두에서
     표식을 지우므로, 직전 성공분의 표식이 이번 실패분에 붙지 않는다.
  4. (F-3) read_label_state()가 "키 없음(진짜 구버전)" / "null(기록경로 결함)" /
     "빈값"을 **다른 문구**로 구분한다 — 셋 다 False(모른다)인 것은 그대로.

실행: python tests/test_476_eod_label_scheme_roundtrip.py   (COM/PyQt/DB 불필요)
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

os.environ.setdefault("MIREUK_TEST_MODE", "1")

import numpy as np  # noqa: E402

_FAILS = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        _FAILS.append(name)


def _mk_retrainer():
    from learning.batch_retrainer import BatchRetrainer
    d = tempfile.mkdtemp(prefix="t476_")
    # model_dir/scaler_dir 격리 — 346차 스케일러 유출 사고 재발 방지 규약
    return BatchRetrainer(model_dir=os.path.join(d, "m"),
                          scaler_dir=os.path.join(d, "s")), d


def _load_db_marker(rt, X, scheme="fixed", params=None):
    """_load_from_db()가 성공 반환 직전에 남기는 상태를 그대로 재현한다."""
    rt._last_label_scheme = scheme
    rt._last_label_params = dict(params or {"1m": 0.00075})
    rt._label_state_from_load_db = (
        id(X), getattr(X, "shape", None),
        rt._last_label_scheme, dict(rt._last_label_params),
    )


def test_known_x_preserves_scheme():
    print("\n-- test_known_x_preserves_scheme  (불변식 1 — 프로덕션 경로)")
    rt, d = _mk_retrainer()
    try:
        X = np.zeros((10, 5), dtype=np.float32)
        _load_db_marker(rt, X, "fixed", {"1m": 0.00075, "3m": 0.00136})
        rt._resolve_external_label_state(X)
        check("표식 일치 → scheme 보존", rt._last_label_scheme == "fixed")
        check("표식 일치 → params 보존", rt._last_label_params.get("3m") == 0.00136)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_unknown_x_still_wipes():
    print("\n-- test_unknown_x_still_wipes  (불변식 2 — 468차 보수 원칙 유지)")
    rt, d = _mk_retrainer()
    try:
        # (a) 표식 자체가 없다 — 외부에서 만든 X
        rt._last_label_scheme = "fixed"
        rt._last_label_params = {"1m": 0.00075}
        X_ext = np.zeros((10, 5), dtype=np.float32)
        rt._resolve_external_label_state(X_ext)
        check("표식 없음 → None", rt._last_label_scheme is None)
        check("표식 없음 → params 비움", rt._last_label_params == {})

        # (b) 표식은 있으나 다른 X — id 불일치
        X_a = np.zeros((10, 5), dtype=np.float32)
        X_b = np.zeros((10, 5), dtype=np.float32)   # 같은 shape, 다른 객체
        _load_db_marker(rt, X_a)
        rt._resolve_external_label_state(X_b)
        check("id 불일치(같은 shape) → None", rt._last_label_scheme is None)

        # (c) shape 불일치 — id()가 우연히 재사용돼도 shape가 다르면 지운다
        X_c = np.zeros((10, 5), dtype=np.float32)
        _load_db_marker(rt, X_c)
        rt._label_state_from_load_db = (
            id(X_c), (999, 5),                       # shape만 어긋난 표식
            rt._last_label_scheme, dict(rt._last_label_params),
        )
        rt._resolve_external_label_state(X_c)
        check("shape 불일치 → None", rt._last_label_scheme is None)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_marker_cleared_on_reload():
    print("\n-- test_marker_cleared_on_reload  (불변식 3 — 표식 수명)")
    rt, d = _mk_retrainer()
    try:
        X = np.zeros((10, 5), dtype=np.float32)
        _load_db_marker(rt, X)
        # _load_from_db() 서두의 리셋을 재현 — 실패 경로에서는 표식이 새로 안 생긴다
        rt._label_state_from_load_db = None
        rt._resolve_external_label_state(X)
        check("리셋 후 되먹임 → None (직전 성공분 표식이 안 붙는다)",
              rt._last_label_scheme is None)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_f3_message_distinction():
    print("\n-- test_f3_message_distinction  (불변식 4 — 진단 문구 3분화)")
    from learning.model_meta import read_label_state
    HZ = ["1m"]

    def _dir_with(meta):
        d = tempfile.mkdtemp(prefix="t476_meta_")
        with io.open(os.path.join(d, "gbm_1m_meta.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False))
        return d

    cases = [
        ({"horizon": "1m"},                            "구버전", "키 없음 → 구버전(키없음)"),
        ({"horizon": "1m", "label_scheme": None},      "null(기록경로 결함)", "null → 기록경로 결함"),
        ({"horizon": "1m", "label_scheme": ""},        "빈값", "빈 문자열 → 빈값"),
    ]
    for meta, token, name in cases:
        d = _dir_with(meta)
        try:
            ok, why = read_label_state(d, HZ, "fixed", None)
            check("%s (%s)" % (name, why), ok is False and token in why)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # 정상 케이스는 여전히 True — 문구 분화가 판정을 못 바꾼다
    d = _dir_with({"horizon": "1m", "label_scheme": "fixed", "label_param": 0.00075})
    try:
        ok, why = read_label_state(d, HZ, "fixed", lambda hz: 0.00075)
        check("정상 사이드카 → True (%s)" % why, ok is True)
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    test_known_x_preserves_scheme()
    test_unknown_x_still_wipes()
    test_marker_cleared_on_reload()
    test_f3_message_distinction()
    print("\n%s — 실패 %d건" % ("PASS" if not _FAILS else "FAIL", len(_FAILS)))
    sys.exit(1 if _FAILS else 0)
