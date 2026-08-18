# -*- coding: utf-8 -*-
"""tests/test_475_decision_registry_visibility.py
    — [MW0602 475차 후속3] 일일 다이제스트 §13 확정 결정 레지스트리 노출 회귀

────────────────────────────────────────────────────────────────────────────
무엇을 지키는가
────────────────────────────────────────────────────────────────────────────
2026-08-18 장후 리포트 §5 R-1 이 "TP1 보호트레일 protect_offset 감도 섀도 계측"을
신규 제안했다. 그 질문은 캠페인 [25] `tp1_protect_offset_shadow` 가 이미 더 강한
형태(소급 counterfactual, 95훅/16일)로 측정했고, 판정(FAIL)을 지나 **주간회의 확정
결정(2026-08-08 "미적용 유지")** 까지 끝나 있었다 — 리포트 전문에서 `[25]` 언급 0건.

CLAUDE.md 캠페인 절이 경고한 사고 그대로다: *"일부러 적용하지 않기로 한 FAIL 을
다음 세션이 보고 적용을 재시도할 위험."* 레지스트리는 있었지만 주간 리포트(docs/)에만
렌더되고 수집기 scan_dirs(logs·data)에 안 잡혀 **일일 세션의 시야에 없었다.**
§13 이 그 통로다.

불변식:
  (1) 레지스트리 섹션의 `### \`key\` — 결정 *(날짜)*` 헤딩이 추출된다
  (2) 레지스트리 **밖**의 ### 헤딩은 섞이지 않는다
  (3) 리포트가 없으면 None — **미측정이지 "결정 없음"이 아니다**(계측 4원칙 ②)
  (4) 여러 날짜본 중 **최신**을 읽는다 (덮어쓰기 금지 규약의 소비 측)
  (5) 결정문 내부의 — 는 구분자로 오인되지 않는다
"""
from __future__ import print_function

import io
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".claude", "skills", "mireuk-daily-check", "scripts"))

import collect_evidence as ce                                        # noqa: E402

_fails = []


def check(label, cond):
    print("%s %s" % ("[OK]  " if cond else "[FAIL]", label))
    if not cond:
        _fails.append(label)


_REPORT = u"""# 검증 캠페인 리포트

## 요약

### `이건_레지스트리가_아니다` — 섞이면 안 된다 *(2026-01-01)*

본문.

## 확정 결정 레지스트리 (주간회의 수동 결정 이력)

### `tp1_protect_offset_shadow` — 미적용 유지 — 주간회의 확정 (atr_lock_0.75만 감시 후보로 승격) *(2026-08-08)*

상세 설명 문단.

### `sizing_prescription_axis` — **재개(reopened)** — 근거가 417차에 무효화됨 *(2026-08-05)*

### `날짜없는_항목` — 보류

## 다음 섹션

### `이것도_아니다` — 레지스트리 종료 후 *(2026-08-09)*
"""


def _make(root, pcid, files):
    d = os.path.join(root, "docs", "정기점검", "금요일점검", pcid)
    os.makedirs(d)
    for fn, body in files:
        with io.open(os.path.join(d, fn), "w", encoding="utf-8") as f:
            f.write(body)
    return d


# ══════════════════════════════════════════════════════════════════
def test_extracts_registry_headings_only():
    root = tempfile.mkdtemp(prefix="mireuk_reg_")
    try:
        _make(root, "MW0602",
              [("validation_campaign_report_20260814.md", _REPORT)])
        dec = ce.scan_campaign_decisions(root, "MW0602")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    keys = [k for k, _d, _t in dec["entries"]]
    check("(1) 레지스트리 항목 3건 추출 — %s" % keys, len(dec["entries"]) == 3)
    check("(1) R-1 을 막았을 키가 있다", "tp1_protect_offset_shadow" in keys)
    check("(2) 레지스트리 밖 헤딩(앞)은 제외", "이건_레지스트리가_아니다" not in keys)
    check("(2) 레지스트리 밖 헤딩(뒤)은 제외", "이것도_아니다" not in keys)
    by = {k: (d, t) for k, d, t in dec["entries"]}
    check("(1) 결정·날짜 분리", by["tp1_protect_offset_shadow"][1] == "2026-08-08")
    check("(5) 결정문 내부 — 보존",
          "주간회의 확정" in by["tp1_protect_offset_shadow"][0]
          and "미적용 유지" in by["tp1_protect_offset_shadow"][0])
    check("(5) 날짜 없는 항목도 살아남는다 (date='')",
          by["날짜없는_항목"] == ("보류", ""))


def test_missing_report_is_none_not_empty():
    root = tempfile.mkdtemp(prefix="mireuk_reg_")
    try:
        os.makedirs(os.path.join(root, "docs"))
        dec = ce.scan_campaign_decisions(root, "MW0602")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    check("(3) 리포트 부재는 None — '결정 없음'으로 위장하지 않는다", dec is None)


def test_latest_dated_report_wins():
    old = _REPORT.replace("tp1_protect_offset_shadow", "옛날_키")
    root = tempfile.mkdtemp(prefix="mireuk_reg_")
    try:
        _make(root, "MW0602",
              [("validation_campaign_report_20260807.md", old),
               ("validation_campaign_report_20260814.md", _REPORT),
               ("validation_campaign_report_20260801_pre405.md", old)])  # 수동 스냅샷 — 제외
        dec = ce.scan_campaign_decisions(root, "MW0602")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    keys = [k for k, _d, _t in dec["entries"]]
    check("(4) 최신 날짜본을 읽는다", "tp1_protect_offset_shadow" in keys
          and "옛날_키" not in keys)
    check("(4) 원천 파일명이 최신본이다", "20260814" in dec["file"])


if __name__ == "__main__":
    for fn in sorted(
        [v for k, v in list(globals().items()) if k.startswith("test_")],
        key=lambda f: f.__code__.co_firstlineno,
    ):
        print("\n── %s" % fn.__name__)
        fn()
    print("\n" + "=" * 60)
    if _fails:
        print("결정 레지스트리 노출 회귀 실패 %d건" % len(_fails))
        for f in _fails:
            print("  - %s" % f)
        sys.exit(1)
    print("결정 레지스트리 노출 회귀 전부 통과")
