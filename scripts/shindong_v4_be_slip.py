# -*- coding: utf-8 -*-
"""[MW0602 657차] 신동 V4 본전청산 실측 슬립 누적 — 사전등록 V4 §3-2 되돌림 조건 판정. 읽기 전용.

조건(결과 보기 전 고정 — `spec.V4_BE_SLIP_REVIEW_PT`·`V4_BE_SLIP_MIN_N`):
  [673차 후속7 · 사용자 결정 2026-10-29] 표본을 R1(수급 타이머 정렬) 전/후로 나눠 **구간마다** 같은 문턱을 적용한다.
  판정 기준 구간은 「정렬 후」. 두 구간을 합치지 않는다(spec.V4_BE_SLIP_SPLIT_BY_ALIGN 주석).
  본전청산 실측 슬립 **평균 > 0.8pt** 이고 표본 **20건 이상** → 「BE3 단독 우위가 사라졌다」 → 재검토(자동 조치 없음).
표본 = 채점 시작(`spec.SCORING_START`)부터, 재생 MAIN(v4 규격 행) 중 청산 사유 BE 이고 실거래와 짝지어진(MATCH) 거래.
슬립 = side × (본전가 − 실청산 평균가), + = 불리. 계산은 `exec_recon.be_exit_slips` 와 같다.

사용: python scripts/shindong_v4_be_slip.py [--since YYYY-MM-DD] [--until YYYY-MM-DD]
"""
import argparse
import datetime as _dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from config.settings import SHINDONG_DB, TRADES_DB          # noqa: E402
from strategy.shindong import exec_recon as XR, spec as S   # noqa: E402


def _main_rows(sd_db, day):
    return XR.stored_main_rows(sd_db, day, S.SPEC_VERSION)     # v4 규격 행만(그 전 규격은 다른 규칙)


def collect(since, until, sd_db=SHINDONG_DB, trades_db=TRADES_DB):
    """→ ({"pre": [...], "post": [...]}, 대사 원천 없는 날). [673차 후속7] R1 정렬 전/후로 나눈다(spec 주석)."""
    recons, unmeasured = XR.collect_recons(sd_db, trades_db, since, until, S.SPEC_VERSION)
    return XR.be_slips_by_align(recons), unmeasured


_SEG = (("post", "정렬 후(R1 · 판정 기준 구간)"), ("pre", "정렬 전(참고 — 판정에 합치지 않음)"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=S.SCORING_START)
    ap.add_argument("--until", default=_dt.date.today().isoformat())
    a = ap.parse_args()
    segs, um = collect(a.since, a.until)
    print("신동 V4 본전청산 실측 슬립 (%s ~ %s, 규격 %s) — R1 정렬 전/후 구간별 판정"
          % (a.since, a.until, S.SPEC_VERSION))
    if um:
        print("  대사 원천 없음(미측정) %d일: %s" % (len(um), ", ".join(um)))
    for seg, label in _SEG:
        xs = segs[seg]
        v = XR.be_slip_verdict([x["slip_pt"] for x in xs])
        print("")
        print("[%s]" % label)
        for x in xs:
            print("  %s %s %s 본전가 %.2f → 실청산 %.2f · 슬립 %+.2fpt" % (
                x["day"], x["key"], "매수" if x["side"] > 0 else "매도", x["be_px"], x["real_exit_px"], x["slip_pt"]))
        if not v["n"]:
            print("  판정: 대기 — 표본 0건 (필요 %d건)" % S.V4_BE_SLIP_MIN_N)
            continue
        print("  표본 %d건 · 평균 %+.3fpt · 최악 %+.2fpt" % (v["n"], v["mean"], v["worst"]))
        if v["state"] == "대기":
            print("  판정: 대기 — %d/%d건" % (v["n"], S.V4_BE_SLIP_MIN_N))
        elif v["state"] == "재검토":
            print("  판정: **재검토** — 평균 %.3f > %.1fpt (사전등록 V4 §3-2. 자동 조치 없음)" % (v["mean"], S.V4_BE_SLIP_REVIEW_PT))
        else:
            print("  판정: 유지 — 평균 %.3f ≤ %.1fpt" % (v["mean"], S.V4_BE_SLIP_REVIEW_PT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
