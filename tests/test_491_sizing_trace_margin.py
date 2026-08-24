# -*- coding: utf-8 -*-
"""[MW0602 491차 F-5] sizing_trace 증거금 축 + binding_gate 오답 차단 — 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: dev_memory/DECISION_LOG.md 2026-08-24 491차 · 0824 리포트 1-8)
────────────────────────────────────────────────────────────────────────────
`sizing_trace.binding_gate` 는 **품질군 argmin 을 무조건** 답으로 냈다.
그래서 증거금 상한(`_ts_margin_capped_qty`)이 자른 분도 `meta` 같은 품질
게이트가 자른 것으로 기록됐다(0824 5행 추가 → 전구간 15행). 실전 전환 기준
⑧([28] sizing_inversion_watch)이 읽는 근거라 오귀속이 그대로 판정에 들어간다.

지키는 불변식:
  T1  `sizing_trace` 에 `margin_cap_qty` · `margin_binding` 두 필드가 있다.
  T2  NULL 규약 — 미조회 사이클은 두 필드가 **None**(0 아님)이고,
      `self._margin_probe` 가 매 사이클 리셋된다(지난 분 값 이월 금지).
  T3  **오답 차단 불변식** — 품질 배수가 수량을 실제로 깎지 않았으면
      (`qty_display == qty_safety_base`) `binding_gate` 는 품질 게이트 이름이
      될 수 없다. 0824 의 오귀속 3행이 이 테스트를 깬다(회귀 고정).
  T4  품질군이 **실제로** 구속한 경우의 동작은 완전 무변경(argmin 그대로).
  T5  증거금이 구속했고 품질군은 미구속이면 `binding_gate == "margin"`.
  T6  상한 미구속(OK)인데 하류가 깎았으면 **None**(미확정) — 모르는 것에
      이름을 붙이지 않는다(계측 4원칙 ②).
  T7  소비부 2곳이 `margin` 버킷을 인식한다(캠페인 [28] · 수집기 §12).

실행: python tests/test_491_sizing_trace_margin.py   (COM/브로커 불필요)
"""

import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

FAILURES = []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _read(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


_MAIN = _read("main.py")


# ── 판정 규칙 재현 ────────────────────────────────────────────────────
# main.py 의 분기를 그대로 옮긴 것. 코드가 바뀌면 T3~T6 가 아니라 이 함수와
# 코드의 괴리로 드러나야 하므로, 아래 T_SRC 가 원문 존재를 함께 고정한다.
def binding_gate(quality_mults, qty_safety_base, qty_display, qty_auto,
                 margin_state):
    q_argmin = (min(quality_mults, key=lambda k: quality_mults[k])
                if quality_mults else None)
    quality_bound = bool(quality_mults) and int(qty_display) < int(qty_safety_base)
    margin_binding = (None if margin_state is None
                      else bool(margin_state in ("CAP", "BLOCK")))
    if quality_bound:
        return q_argmin
    if int(qty_display) > int(qty_auto):
        return "margin" if margin_binding else None
    return None


def test_t1_fields_exist():
    for f in ('"margin_cap_qty":', '"margin_binding":', '"margin_state":'):
        check("T1: sizing_trace 필드 %s" % f, f in _MAIN)
    check("T1: 종전 argmin 은 별 축으로 보존", '"quality_argmin":' in _MAIN)


def test_t2_null_contract_and_reset():
    check("T2: __init__ 기본값 None", "self._margin_probe = None" in _MAIN)
    # 리셋이 _qty_auto 초기화 직후에 있고, 기록은 _ts_margin_capped_qty 안에 있다
    reset = _MAIN.find("_qty_auto = _qty_display\n        # [MW0602 491차 F-5]")
    write = _MAIN.find('self._margin_probe = {"state": _mc_state')
    check("T2: 매 사이클 리셋 존재", reset > 0)
    check("T2: 리셋이 기록보다 앞(이월 금지)", 0 < reset < write)
    # 미조회 경로는 None 으로 남아야 한다 — 조회 실패 early return 이 기록보다 앞
    fail_ret = _MAIN.find('logger.debug("[MarginQty] 조회 예외')
    check("T2: 조회 실패 경로가 기록에 닿지 않음", 0 < fail_ret < write)
    check("T2: 미조회 시 None 직렬화",
          '"margin_cap_qty":  (int(_mp["margin_qty"]) if _mp else None)' in _MAIN)


def test_t3_misattribution_is_impossible():
    """0824 의 오귀속 3행 형태 — 품질 배수는 있으나 수량을 안 깎았다."""
    got = binding_gate({"meta": 0.5, "tox": 0.7}, qty_safety_base=1,
                       qty_display=1, qty_auto=1, margin_state=None)
    check("T3: 품질 미구속인데 품질 이름이 나오지 않는다 (got=%r)" % got,
          got not in ("meta", "tox"))
    # 증거금이 잘랐던 형태(3 → 2)
    got = binding_gate({"meta": 0.5}, qty_safety_base=3, qty_display=3,
                       qty_auto=2, margin_state="CAP")
    check("T3: 증거금 절단이 meta 로 기록되지 않는다 (got=%r)" % got, got != "meta")


def test_t4_quality_path_unchanged():
    got = binding_gate({"meta": 0.5, "tox": 0.7}, qty_safety_base=4,
                       qty_display=2, qty_auto=2, margin_state="OK")
    check("T4: 품질군 실구속 시 argmin 그대로 (got=%r)" % got, got == "meta")
    got = binding_gate({"exec": 0.9, "hurst": 0.3}, qty_safety_base=10,
                       qty_display=3, qty_auto=3, margin_state=None)
    check("T4: argmin 은 최소 배수 (got=%r)" % got, got == "hurst")


def test_t5_margin_bucket():
    for st in ("CAP", "BLOCK"):
        got = binding_gate({}, 3, 3, 2, st)
        check("T5: %s → margin (got=%r)" % (st, got), got == "margin")


def test_t6_unknown_stays_unknown():
    got = binding_gate({}, 3, 3, 2, "OK")
    check("T6: 증거금 미구속인데 하류가 깎음 → None (got=%r)" % got, got is None)
    got = binding_gate({}, 3, 3, 2, None)
    check("T6: 미조회 → None (got=%r)" % got, got is None)
    got = binding_gate({}, 2, 2, 2, "OK")
    check("T6: 아무것도 안 깎았으면 None (got=%r)" % got, got is None)


def test_t7_consumers_know_margin():
    rep = _read("scripts/generate_validation_campaign_report.py")
    check("T7: [28] margin 버킷 계수", '"n_binding_margin"' in rep)
    check("T7: [28] 증거금 축 measured_since", "margin_measured_since" in rep)
    col = _read(".claude/skills/mireuk-daily-check/scripts/collect_evidence.py")
    check("T7: 수집기 §12 문구", "491차 F-5" in col and "증거금이 구속한 것" in col)


def test_t_src_matches_reproduction():
    """위 재현 함수가 main.py 원문과 같은 분기를 쓰는지 고정."""
    for frag in (
        "_quality_bound = bool(_sz_q) and int(_qty_display) < int(_qty_safety_base)",
        '_binding_gate = "margin" if _margin_binding else None',
        "_binding_gate = _q_argmin",
    ):
        check("T_SRC: 원문 분기 — %s" % frag[:48], frag in _MAIN)
    # 종전 무조건 argmin 대입이 남아 있지 않아야 한다
    bad = re.search(r'"binding_gate":\s+\(min\(_sz_q', _MAIN)
    check("T_SRC: 무조건 argmin 대입 제거", bad is None)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_t1_fields_exist, test_t2_null_contract_and_reset,
               test_t3_misattribution_is_impossible, test_t4_quality_path_unchanged,
               test_t5_margin_bucket, test_t6_unknown_stays_unknown,
               test_t7_consumers_know_margin, test_t_src_matches_reproduction):
        try:
            fn()
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
