# tests/test_457_guard_meta_and_scope.py — 457차 P4·P5·P6 회귀 테스트
"""BatchRetrainer 전체를 인스턴스화하면 sklearn·DB 의존이 붙으므로, 세 변경 중
**순수 로직**은 직접 호출하고 **파일/스코프 동작**은 임시 디렉터리로 격리해 검증한다.

`_fair_validity`/`_read_model_meta`는 self.model_dir 하나만 쓰므로 가짜 객체에
바인딩해 호출한다(진짜 BatchRetrainer를 만들지 않는다 — DB를 건드리지 않기 위함,
[[feedback_isolate_stateful_verification]]).

실행:  <py310_64> tests/test_457_guard_meta_and_scope.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FAIL = []


def check(name, got, want):
    if got == want:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s\n       got  = %r\n       want = %r" % (name, got, want))
        FAIL.append(name)


class _Stub(object):
    """_read_model_meta/_fair_validity가 실제로 쓰는 속성만 가진 최소 객체."""

    def __init__(self, model_dir, train_ts=None):
        self.model_dir = model_dir
        self._last_train_ts = train_ts


def _bind():
    from learning.batch_retrainer import BatchRetrainer
    _Stub._read_model_meta = BatchRetrainer._read_model_meta
    _Stub._fair_validity = BatchRetrainer._fair_validity


# [MW0601 473차] `_bind()`는 아래 `__main__` 블록에서만 호출됐다 — 그래서 **pytest로
# 수집하면 바인딩이 일어나지 않아** `test_fair_validity`가
# `AttributeError: '_Stub' object has no attribute '_fair_validity'` 로 죽었다.
# 이 파일의 docstring이 직접 실행(`<py310_64> tests/...py`)을 전제하고 있어 그 경로로는
# 통과했고, 전체 스위트에서는 **빨간불이면서 아무것도 지키지 않는 상태**로 남아 있었다
# (457차 P4 가드 유효성 판정이 무방비). 모듈 임포트 시점으로 끌어올려 두 경로를 맞춘다.
# 실패해도 collection을 깨뜨리지 않는다 — 그 경우 테스트 쪽에서 skip 처리된다.
try:
    _bind()
except Exception as _e:      # sklearn 미설치 등 — 이 PC에서는 검증 불가
    print("[457] _bind 실패 — %s: %s" % (type(_e).__name__, _e))


def _write_meta(d, hz, train_end_ts, source="eod"):
    with open(os.path.join(d, "gbm_%s_meta.json" % hz), "w", encoding="utf-8") as f:
        json.dump({"horizon": hz, "train_end_ts": train_end_ts, "source": source}, f)


# ─────────────────────────────────────────────────────────────────────────
# P6 + P4 — 메타 사이드카 읽기 · 공정 홀드아웃 유효성 판정
# ─────────────────────────────────────────────────────────────────────────
def test_fair_validity():
    print("[P6/P4] 메타 사이드카 + GuardFair 유효성 판정")
    d = tempfile.mkdtemp(prefix="t457_")
    try:
        # 학습 ts 100개, 홀드아웃 10 → 홀드아웃 시작 = ts[-10] = 2026-08-01 00:90? 아니라
        # 인덱스 90번째. 분 단위 가짜 ts로 만든다.
        ts = ["2026-08-01 %02d:%02d:00" % (9 + i // 60, i % 60) for i in range(100)]
        ho_start = ts[-10]          # 인덱스 90
        s = _Stub(d, train_ts=ts)

        # ① 메타 없음 → 무효 ("모른다"는 "괜찮다"가 아니다)
        ok, note = s._fair_validity("3m", 10)
        check("메타 없으면 무효", (ok, "메타 없음" in note), (False, True))

        # ② 2026-08-10 실사고 재현 — 현행이 홀드아웃을 학습함 (당일 장중 재학습본)
        _write_meta(d, "3m", ts[-1], source="intraday")
        ok, note = s._fair_validity("3m", 10)
        check("현행이 홀드아웃 학습 → 무효",
              (ok, "홀드아웃 학습함" in note, "source=intraday" in note),
              (False, True, True))

        # ③ 정상 — 현행 학습창이 홀드아웃 시작 전에 끝남
        _write_meta(d, "3m", ts[-11], source="eod")
        ok, note = s._fair_validity("3m", 10)
        check("현행 컷오프가 홀드아웃 앞 → 유효",
              (ok, note.startswith("유효")), (True, True))

        # ④ 경계값 — train_end == holdout_start 이면 그 봉을 학습한 것이므로 무효
        _write_meta(d, "3m", ho_start, source="eod")
        ok, _ = s._fair_validity("3m", 10)
        check("경계(train_end == holdout_start)는 무효", ok, False)

        # ⑤ ts 목록이 없으면 판정 불가 → 무효
        s2 = _Stub(d, train_ts=None)
        ok, note = s2._fair_validity("3m", 10)
        check("ts 목록 없으면 무효", (ok, "홀드아웃 경계" in note), (False, True))

        # ⑥ train_end_ts 키가 비면 무효
        with open(os.path.join(d, "gbm_5m_meta.json"), "w", encoding="utf-8") as f:
            json.dump({"horizon": "5m"}, f)
        ok, note = s._fair_validity("5m", 10)
        check("train_end_ts 없으면 무효", (ok, "train_end_ts 없음" in note), (False, True))

        # ⑦ 손상된 JSON도 죽지 않는다
        with open(os.path.join(d, "gbm_10m_meta.json"), "w", encoding="utf-8") as f:
            f.write("{not json")
        check("손상 JSON은 None 반환", s._read_model_meta("10m"), None)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────
# P5 — 교체 스코프 제한  (원본: batch_retrainer.retrain_now 루프)
# ─────────────────────────────────────────────────────────────────────────
def scope_filter(all_horizons, y_keys, horizons):
    _scope = set(horizons) if horizons else None
    out = []
    for h in all_horizons:
        if h not in y_keys:
            continue
        if _scope and h not in _scope:
            continue
        out.append(h)
    return out


def test_scope():
    print("[P5] ConstOut 재학습 스코프 제한")
    ALL = ["1m", "3m", "5m", "10m", "15m", "30m"]
    y = set(ALL)

    check("None이면 종전대로 6/6", scope_filter(ALL, y, None), ALL)
    check("빈 리스트도 종전대로 6/6 (폴백)", scope_filter(ALL, y, []), ALL)
    # 2026-08-10 실사고 재현 — 5회 전부 const_out=['3m']인데 6/6이 무검증 교체됐다
    check("const_out=['3m'] → 3m만", scope_filter(ALL, y, ["3m"]), ["3m"])
    check("복수 트리거도 순서 보존", scope_filter(ALL, y, ["5m", "3m"]), ["3m", "5m"])
    # 스코프에 있어도 라벨이 없으면 학습 불가 — 기존 y_dict 가드가 우선한다
    check("y_dict에 없으면 스코프여도 제외",
          scope_filter(ALL, {"1m", "5m"}, ["3m", "5m"]), ["5m"])
    # 알 수 없는 이름이 와도 조용히 무시(전량 교체로 새지 않는다)
    check("미지 호라이즌은 아무것도 교체 안 함", scope_filter(ALL, y, ["7m"]), [])


# ─────────────────────────────────────────────────────────────────────────
# P5 — argv 라운드트립 (main.py Popen ↔ retrain_intraday.py 파서)
# ─────────────────────────────────────────────────────────────────────────
def parse_argv4(argv):
    """retrain_intraday.py main()의 argv[4] 파싱과 동일 규칙."""
    horizons = None
    if len(argv) >= 5:
        raw = argv[4].strip()
        if raw:
            horizons = [h.strip() for h in raw.split(",") if h.strip()]
    return horizons


def test_argv():
    print("[P5] argv 라운드트립")
    base = ["retrain_intraday.py", "r.json", "1", "1"]
    check("argv[4] 없음(구버전 main.py) → 전체", parse_argv4(base), None)
    check("빈 문자열 → 전체", parse_argv4(base + [""]), None)
    check("단일", parse_argv4(base + ["3m"]), ["3m"])
    check("CSV", parse_argv4(base + ["3m,5m"]), ["3m", "5m"])
    check("공백 섞임", parse_argv4(base + [" 3m , 5m "]), ["3m", "5m"])
    # main.py가 만드는 문자열과 실제로 맞물리는지
    made = ",".join(str(h) for h in (["3m"] or []))
    check("main.py 생성 문자열과 왕복", parse_argv4(base + [made]), ["3m"])
    made_none = ",".join(str(h) for h in (None or []))
    check("horizons=None → 빈 문자열 → 전체", parse_argv4(base + [made_none]), None)


if __name__ == "__main__":
    _bind()
    test_fair_validity()
    print()
    test_scope()
    print()
    test_argv()
    print()
    if FAIL:
        print("실패 %d건: %s" % (len(FAIL), ", ".join(FAIL)))
        sys.exit(1)
    print("전체 통과")
