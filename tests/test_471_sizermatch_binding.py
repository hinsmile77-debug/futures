"""[MW0601 471차 F-3] `[SizerMatch]` 축소원인 오귀속 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: docs/정기점검/매일점검/MW0601-20260814-점검리포트-post.md P1-2)
────────────────────────────────────────────────────────────────────────────
2026-08-14 11:48:00 유일한 진입에서 같은 초 세 줄이 서로 모순됐다:
  [MetaGate]   size_mult=0.50  size_mult_sizing=1.00(무정보폴백→중립)
  [HurstGate]  size_mult=0.50  quality_min=0.50
  [SizerMatch] sizer=3 → actual=2 | kelly=0.60 meta=0.50 tox=1.00 exec=1.00
`[SizerMatch]`가 지목한 원인(meta=0.50)은 **같은 초에 중립화됐다고 기록된 값**
이고, 실제로 min()을 지배한 게이트(hurst)는 출력 문자열에 **존재조차 하지 않았다**.
즉 값이 틀린 게 아니라 필드가 누락된 것이라, 실전 전환 기준 ⑧의 근거 채널
[28]이 참조할 로그가 MetaGate 탓으로 오염돼 있었다.

지키는 불변식:
  T1  `round(sizer × quality_min) == actual` 항등 (431차 min() 합성의 정의)
  T2  binding 게이트 = 품질군 argmin  — 2026-08-14 실측 조합이면 hurst
  T3  출력 문자열이 품질군 전량을 담고, 사이징 실투입값(meta_sizing)을 쓴다
  T4  품질군이 비었는데 수량이 줄면 "없음(안전군·상한·증거금 경로)"으로 표기
      (0.00으로 위장하지 않는다 — 계측 4원칙 ②)

실행: python tests/test_471_sizermatch_binding.py   (COM/브로커 불필요)
"""

import inspect
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


# 2026-08-14 11:48:00 실측 조합 — meta는 무정보폴백으로 사이징 경로만 1.00 중립화됨
_QM_20260814 = {"meta": 1.00, "hurst": 0.50}
_SIZER_RAW_20260814 = 3
_ACTUAL_20260814 = 2


def _binding(quality_mults):
    """main.py `[SizerMatch]` 블록과 같은 argmin 규칙 (동률이면 먼저 등록된 키)."""
    if not quality_mults:
        return None
    return min(quality_mults, key=lambda k: quality_mults[k])


def test_t1_compose_identity():
    got = main._compose_quality_qty(_SIZER_RAW_20260814, _QM_20260814)
    check("T1: round(3 × min(1.00, 0.50)) = 2 — 2026-08-14 실측 재현",
          got == _ACTUAL_20260814)
    # 1.00만 있으면 축소가 없다 (meta 단독으로는 2계약이 나오지 않는다 = 오귀속의 증거)
    check("T1: meta(중립 1.00) 단독이면 축소 없음 → 3계약",
          main._compose_quality_qty(3, {"meta": 1.00}) == 3)
    check("T1: 품질군 없으면 그대로", main._compose_quality_qty(3, {}) == 3)
    check("T1: 최소 1계약 하한", main._compose_quality_qty(1, {"hurst": 0.50}) == 1)


def test_t2_binding_is_argmin():
    check("T2: binding = hurst (2026-08-14 실측 조합)",
          _binding(_QM_20260814) == "hurst")
    check("T2: 더 강한 배수가 들어오면 binding이 그쪽으로 이동",
          _binding({"meta": 1.00, "hurst": 0.50, "tox": 0.35}) == "tox")
    check("T2: 품질군 없음 → binding 없음", _binding({}) is None)


def _sizermatch_src():
    src = inspect.getsource(main.TradingSystem.run_minute_pipeline)
    i = src.find("[SizerMatch]")
    check("소스 블록 탐색", i > 0)
    return src[max(0, i - 2000):i + 5000]


def test_t3_output_uses_quality_mults_and_sizing_value():
    blk = _sizermatch_src()
    check("T3: 품질군 딕셔너리를 전량 순회한다(고정 4종 리스트 아님)",
          "_quality_mults" in blk and "sorted(_sm_q.items()" in blk)
    check("T3: binding= 키를 명시 출력", "binding={_sm_bind_txt}" in blk)
    check("T3: meta는 사이징 실투입값(_meta_size_sizing)을 쓴다",
          "_meta_size_sizing" in blk)
    # 🔴 오귀속 재발 방지 — meta 원값을 라벨 없이 그대로 찍던 종전 포맷 금지
    check("T3: 종전 오귀속 포맷(meta={_meta_size:.2f}) 잔존 0",
          "meta={_meta_size:.2f}" not in blk)
    check("T3: 원값이 갈리면 (raw…) 병기 (431차 [MetaGate] 관례)",
          "raw%.2f" in blk)


def test_t4_empty_quality_group_is_named_not_zero():
    blk = _sizermatch_src()
    check("T4: 품질군 공집합은 '없음(…)'으로 표기 — 0.00 위장 금지",
          "없음(안전군·상한·증거금 경로)" in blk)
    # 포맷 문자열이 %.2f로 None을 찍으려다 죽지 않는지 (공집합 분기에 숫자 포맷 없음)
    m = re.search(r"_sm_bind_txt = \"없음[^\"]*\"", blk)
    check("T4: 공집합 분기에 숫자 포맷 없음", m is not None)


if __name__ == "__main__":
    _fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in _fns:
        try:
            fn()
        except Exception as e:
            FAILURES.append("%s: %r" % (fn.__name__, e))
            print("[FAIL] %s: %r" % (fn.__name__, e))
    print("-" * 60)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")
