# -*- coding: utf-8 -*-
"""[MW0601 561차] 호가깊이 **추정량** 회귀 가드.

무엇을 고정하는가
-----------------
`book_bid_tot`/`book_ask_tot` 은 봉당 수백 개 스냅샷 중 **마지막 1개**다.
「봉의 깊이」가 아니라 임의의 한 시점이며, 봉 전환이 체결 틱으로 일어나므로
그 1개는 봉 마감 시점조차 아니다.

실측(2026-09-10~09-14, 958봉):

    rho(tot, avg)                = +0.288   ← 같은 양의 두 추정량이 이만큼밖에 안 맞는다
    tot 기반 vs microprice_depth_bias = +0.178  → INDEPENDENT 로 읽힌다
    avg 기반 vs microprice_depth_bias = +0.902  → DUPLICATE
    tot >= 40 인 봉 1·6·3 (일자별)  vs  avg >= 40 인 봉 0·0·0

즉 Phase 3-0 판정기가 `_tot` 을 읽으면 **표집 잡음을 「새 정보」로 오판**해
326차가 이미 기각한 축을 통과시킨다. 561차가 입력을 `_avg` 로 개정했다.

이 파일이 깨지면 그 개정이 되돌려진 것이다. 수치를 고치기 전에
`docs/미륵이고도화3/호가깊이/호가잔량_유효성_딥다이브_MW0601-20260914.md` 를 먼저 읽을 것.
"""
from __future__ import print_function

import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _read(rel):
    with io.open(os.path.join(_ROOT, *rel.split("/")), encoding="utf-8") as f:
        return f.read()


# ───────────────────────── 판정기 입력 ─────────────────────────
def test_judge_reads_bar_mean_not_point_sample():
    """Phase 3-0 판정기가 `_avg` 로 비율을 만든다 — `_tot` 이면 중복을 놓친다."""
    src = _read("scripts/book_depth_duplication_check.py")
    q = src.split("rows = con.execute(", 1)[1].split(").fetchall()", 1)[0]
    assert "book_bid_avg" in q and "book_ask_avg" in q, (
        "판정기가 봉평균을 안 읽는다 — 561차 개정이 되돌려졌다")
    # 판정 비율을 만드는 식이 avg 기반이어야 한다
    assert "(float(bavg) - float(aavg)) / den" in src, "판정 비율이 avg 기반이 아니다"
    assert "book[str(ts)] = (float(b) - float(a)) / tot" not in src, (
        "종전 tot 기반 비율 식이 남아 있다")


def test_judge_keeps_preregistered_thresholds():
    """임계·판정문은 개정 대상이 **아니다** — 입력 추정량만 바꿨다(458차 D6)."""
    import importlib
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    m = importlib.import_module("book_depth_duplication_check")
    assert m.DUP_THRESHOLD == 0.90
    assert m.PARTIAL_THRESHOLD == 0.70
    assert m.MIN_DAYS == 20


def test_judge_reports_both_estimators():
    """두 추정량을 나란히 찍는다 — 「바꾸면 뒤집힌다」가 리포트에 남아야 한다."""
    src = _read("scripts/book_depth_duplication_check.py")
    for k in ("rho_bar_tot_estimator", "rho_bar_tot_vs_avg"):
        assert k in src, "%s 가 없다 — 추정량 대조가 사라졌다" % k
    assert "판정에 쓰지 않는다" in src


def test_amendment_is_recorded_with_disclosure():
    """사전등록 개정 사실과 **결과를 이미 봤다는 고지**가 함께 남아 있어야 한다."""
    src = _read("scripts/book_depth_duplication_check.py")
    assert "사전등록 개정" in src
    assert "이미 3거래일 참고치를 이미 봤다" in src or "참고치를 이미 봤다" in src, (
        "결과를 먼저 본 사실 고지가 사라졌다 — 그게 빠지면 사전등록 개정이 아니라 "
        "결과 맞춤으로 읽힌다")


# ───────────────────────── 컬럼 의미 ─────────────────────────
def test_point_sample_semantics_documented_at_every_site():
    """정의가 있는 세 곳 모두에 「1점 표본」이 적혀 있어야 한다(계측 4원칙 ①)."""
    for rel, hint in (
        ("utils/db_utils.py", "스키마"),
        ("collection/cybos/realtime_data.py", "수집"),
    ):
        src = _read(rel)
        assert "561차" in src and ("점표본" in src or "1스냅샷" in src), (
            "%s(%s)에 tot 의 점표본 성격이 안 적혀 있다" % (rel, hint))


def test_new_derivation_guidance_present():
    """신규 파생 지침 — 불균형 금지 · 절대깊이만 · `_avg` 로."""
    src = _read("config/constants.py")
    assert "561차" in src, "constants 에 561차 지침이 없다"
    assert "절대 깊이" in src
    assert "microprice_depth_bias" in src


def test_daily_checker_observes_representativeness():
    """일일 점검기가 tot/avg 괴리를 매일 센다 — 안 보면 다시 숨는다."""
    src = _read("scripts/defect3_collection_check.py")
    assert "BOOK_TOT_DEV_WARN" in src
    assert "tot 대표성" in src


# ───────────────────────── 산술 불변식 ─────────────────────────
def test_estimator_divergence_arithmetic():
    """`_avg` 는 평균이고 `_tot` 은 표본 하나 — 평균이 항상 덜 튄다는 성질 자체를 고정."""
    # 봉 하나를 흉내낸다: 대부분 8, 마지막에 100 이 한 번.
    snaps = [8] * 499 + [100]
    avg = sum(snaps) / float(len(snaps))
    tot = snaps[-1]                      # 552차 구현이 저장하는 값
    assert abs(tot - avg) / avg > 4.0, "이 예시가 괴리를 못 만든다 — 테스트가 무의미"
    assert avg < 10.0, "평균은 대표값에 가깝다"
    assert tot == 100, "tot 은 마지막 한 장면이다"
