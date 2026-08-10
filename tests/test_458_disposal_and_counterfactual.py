# tests/test_458_disposal_and_counterfactual.py — 458차 3-A·3-B·3-C 회귀 테스트
"""세 스크립트의 순수 로직을 검증한다. DB·로그는 건드리지 않는다
([[feedback_isolate_stateful_verification]]).

실행:  <py310_64 또는 py37_32> tests/test_458_disposal_and_counterfactual.py
"""
from __future__ import annotations

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("MIREUK_TEST_MODE", "1")

FAIL = []


def check(name, got, want):
    if got == want:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s\n       got  = %r\n       want = %r" % (name, got, want))
        FAIL.append(name)


# ─────────────────────────────────────────────────────────────────────────
# 3-B [49] — 진입 로그 정규식 · 연속 재생
# ─────────────────────────────────────────────────────────────────────────
def test_entry_regex():
    print("[3-B] 진입 로그 파싱")
    from scripts.early_trail_exit_counterfactual import _ENTRY_RE

    # 2026-08-10 실로그 원문
    line = ("2026-08-10 14:19:01 [INFO] TRADE: [Position] 진입 SHORT 2계약 @ 978.9 | "
            "손절=981.85 1차=977.92(×0.60) 2차=975.95 horizon=3m hurst=trend")
    m = _ENTRY_RE.search(line)
    check("실로그 매치", bool(m), True)
    if m:
        check("필드 추출",
              (m.group(2), float(m.group(3)), float(m.group(4)),
               float(m.group(6)), m.group(7)),
              ("SHORT", 978.9, 981.85, 975.95, "3m"))
    # horizon 표기가 없는 구형 줄도 죽지 않는다
    old = ("2026-07-14 11:15:54 [INFO] TRADE: [Position] 진입 SHORT 1계약 @ 1066.78 | "
           "손절=1075.62 1차=1062.66(×0.84) 2차=1057.94")
    m2 = _ENTRY_RE.search(old)
    check("구형 줄(호라이즌 없음) 매치", bool(m2), True)


def test_continuation():
    print("[3-B] 연속 재생 (원 사다리)")
    from scripts.early_trail_exit_counterfactual import continuation

    # SHORT: 진입 100, 원 스톱 103, TP2 96. 청산 10:00.
    def bars(seq):
        # seq: [(분, high, low, close)]
        return {"2026-08-10 10:%02d:00" % mn: (h, l, c) for mn, h, l, c in seq}

    # ① TP2 먼저 → (96-100)×(-1) = +4
    b = bars([(1, 100.5, 99.0, 99.5), (2, 99.5, 95.8, 96.0)])
    check("TP2 도달 +4pt",
          continuation("2026-08-10 10:00:30", 100.0, 103.0, 96.0, -1, b), 4.0)
    # ② 스톱 먼저 → (103-100)×(-1) = -3
    b = bars([(1, 103.2, 100.0, 102.0)])
    check("원 스톱 재노출 -3pt",
          continuation("2026-08-10 10:00:30", 100.0, 103.0, 96.0, -1, b), -3.0)
    # ③ 같은 봉 동시 히트 → 스톱 우선(보수)
    b = bars([(1, 103.5, 95.5, 99.0)])
    check("동시 히트 → 스톱 우선",
          continuation("2026-08-10 10:00:30", 100.0, 103.0, 96.0, -1, b), -3.0)
    # ④ 아무것도 안 닿음 → 마지막 종가
    b = bars([(1, 101.0, 99.0, 99.2), (2, 100.0, 98.5, 98.8)])
    check("종가 청산 +1.2pt",
          round(continuation("2026-08-10 10:00:30", 100.0, 103.0, 96.0, -1, b), 4), 1.2)
    # ⑤ breakeven 팔: 스톱=진입가 → 되돌림에 0으로 청산
    b = bars([(1, 100.2, 99.0, 99.5)])
    check("본전 강등 팔 0pt",
          continuation("2026-08-10 10:00:30", 100.0, 100.0, 96.0, -1, b), 0.0)
    # ⑥ 청산 후 봉 없음 → None (측정 불가 — 0으로 오인 금지)
    check("봉 없음 → None",
          continuation("2026-08-10 15:09:30", 100.0, 103.0, 96.0, -1, {}), None)


# ─────────────────────────────────────────────────────────────────────────
# 3-A [40-B] — 처분 분기
# ─────────────────────────────────────────────────────────────────────────
def disposal_verdict(n, days, p_t, sign_p, mean, cr):
    """run_inverse의 판정 분기와 동일 규칙."""
    alpha = cr["alpha"]
    if n < cr["min_entries"] or days < cr["min_days"]:
        return "INSUFFICIENT"
    if p_t < alpha and sign_p < alpha and mean > 0:
        return "INVERSE_SIGNAL"
    if p_t < alpha and sign_p < alpha and mean < 0:
        return "ACTUAL_SIGNAL"
    return "NO_INFORMATION"


def test_disposal():
    print("[3-A] 처분 분기")
    cr = {"min_entries": 300, "min_days": 35, "alpha": 0.05}
    check("표본 미달 → INSUFFICIENT",
          disposal_verdict(160, 20, 0.01, 0.01, 0.5, cr), "INSUFFICIENT")
    check("현재 실측(비유의) → NO_INFORMATION",
          disposal_verdict(300, 35, 0.20, 0.82, 0.64, cr), "NO_INFORMATION")
    check("t만 유의, 일자 비유의 → NO_INFORMATION (보수)",
          disposal_verdict(300, 35, 0.01, 0.30, 0.64, cr), "NO_INFORMATION")
    check("둘 다 유의 + 양 → INVERSE_SIGNAL",
          disposal_verdict(300, 35, 0.01, 0.01, 0.64, cr), "INVERSE_SIGNAL")
    check("둘 다 유의 + 음 → ACTUAL_SIGNAL",
          disposal_verdict(300, 35, 0.01, 0.01, -0.4, cr), "ACTUAL_SIGNAL")


# ─────────────────────────────────────────────────────────────────────────
# [49] 판정 분기 — evaluate()와 동일 규칙
# ─────────────────────────────────────────────────────────────────────────
def cf_verdict(n, days, mean, sign_p, cr):
    if n < cr["min_samples"] or days < cr["min_days"]:
        return "INSUFFICIENT"
    if mean > cr["roundtrip_cost_pt"] and sign_p < 0.05:
        return "FAIL"
    return "PASS"


def test_cf_verdict():
    print("[3-B] [49] 판정 분기")
    cr = {"min_samples": 60, "min_days": 10, "roundtrip_cost_pt": 0.0716}
    check("현재 실측(56건) → INSUFFICIENT", cf_verdict(56, 13, -1.056, 0.267, cr),
          "INSUFFICIENT")
    check("개선 음수 → PASS(현행 유지)", cf_verdict(80, 12, -1.0, 0.01, cr), "PASS")
    check("개선 있으나 비유의 → PASS", cf_verdict(80, 12, 0.5, 0.30, cr), "PASS")
    check("개선 + 유의 → FAIL(회수 검토)", cf_verdict(80, 12, 0.5, 0.01, cr), "FAIL")
    check("개선이 비용 이하 → PASS", cf_verdict(80, 12, 0.05, 0.01, cr), "PASS")


# ─────────────────────────────────────────────────────────────────────────
# 사전등록 키 존재 (settings 등기 확인)
# ─────────────────────────────────────────────────────────────────────────
def test_registration():
    print("[등기] VALIDATION_CAMPAIGN 사전등록")
    from config.settings import VALIDATION_CAMPAIGN as VC
    a = VC.get("direction_disposal_watch") or {}
    b = VC.get("early_trail_exit_watch") or {}
    check("[40-B] 등록 + 판정선",
          (a.get("min_entries"), a.get("min_days"), a.get("alpha")), (300, 35, 0.05))
    check("[49] 등록 + 판정선",
          (b.get("min_samples"), b.get("min_days"), b.get("primary_arm")),
          (60, 10, "orig"))
    check("[49] 왕복비용 = 정본 0.0716", b.get("roundtrip_cost_pt"), 0.0716)


if __name__ == "__main__":
    test_entry_regex()
    print()
    test_continuation()
    print()
    test_disposal()
    print()
    test_cf_verdict()
    print()
    test_registration()
    print()
    if FAIL:
        print("실패 %d건: %s" % (len(FAIL), ", ".join(FAIL)))
        sys.exit(1)
    print("전체 통과")
