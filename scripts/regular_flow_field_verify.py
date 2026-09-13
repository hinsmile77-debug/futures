# -*- coding: utf-8 -*-
"""[MW0601 559차 / P0-1] 정규 분봉 **필드10 = 누적 체결매수** 라벨의 누적 검증기.

무엇을 재는가
-------------
`regular_candles.db` 의 `cum_sell` 컬럼(= `CpSysDib.FutOptChart` **필드 10**)의
**분봉 증분**이, 미륵이 실시간이 받는 서버 정답지
`raw_data.db:raw_candles.anchor_buy`(= `Dscbo1.FutureCurOnly` 헤더 **23 누적체결매수**)와
같은가.

같다면 두 가지가 동시에 성립한다.
  1. 컬럼 이름 `cum_sell` 은 **틀렸고** 그 값은 누적 **매수** 다.
  2. 정규 시리즈(10100, 2024-07~ 533거래일)에 **편향 없는 체결 방향 원천**이 있다.
     미니 틱 원본이 없어 영구 편향인 2026-06-02~08-09 구간의 **연구용 대체 원천**이
     될 수 있다(대체 사용 여부는 별건 — 주간회의 안건, 이 스크립트는 판정하지 않는다).

⚠ 이것은 **알파 판정기가 아니다.** 손익도 IC 도 보지 않는다. 두 계열이 같은 수를
  세고 있는가만 본다.

왜 하루짜리 확인으로 끝내면 안 되는가
--------------------------------------
초회 실측(2026-09-11)은 383봉 전량 일치였지만 **거래일 1개**다. 미니 당월물이
교체되면 비교 대상 종목이 바뀌므로, 병행 거래일이 쌓이는 대로 다시 돌려 누적
표본을 늘려야 한다. 그래서 임계를 스크립트 상단에 **사전등록**해 둔다.

비교 대상 종목 선택
-------------------
미륵이는 **미니 당월물**을 본다. `regular_candles.db` 에는 연결선물(10100)과
미니(A05xxx)가 함께 있는데, 미니도 근월물이 되기 전에는 체결이 드물다.
그래서 종목을 이름으로 고르지 않고 **그날 거래량이 미륵이와 일치하는 종목**으로
고른다(계측 4원칙 3 — 못 고른 날은 제외 사유를 남긴다).

실행
----
    python scripts/regular_flow_field_verify.py
    python scripts/regular_flow_field_verify.py --json
    python scripts/regular_flow_field_verify.py --code A056A

⚠ 장 마감 후 전용(456차 — 장중 라이브 DB 전수 스캔이 CB⑤를 자가유발했다).
종료코드: 0 = 정상 출력(판정 결과와 무관) · 2 = 장중 차단.
"""
from __future__ import print_function

# 🔴 numpy import 보다 먼저 — 537차. conda 미활성 실행 시 BLAS delay-load 즉사 방지.
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402

ensure_conda_dll_path()

import argparse  # noqa: E402
import json as _json  # noqa: E402
from collections import OrderedDict  # noqa: E402

from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402

CHANNEL = "regular_flow_field_verify"
REG_DB = os.path.join(_ROOT, "data", "db", "regular_candles.db")
RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

# ── 사전등록 임계 (여기서만 바꾼다 — 결과를 보고 고치면 검증이 아니다) ──────────
SAME_CONTRACT_MIN = 0.95   # 같은 종목으로 인정할 거래량 일치 비율
EXACT_MATCH_MIN = 0.99     # 그 날을 "검증됨"으로 볼 증분 정확일치 비율
TOL = 2                    # ±허용(참고 출력용). 판정은 정확일치로 한다
MIN_BARS = 100             # 하루 최소 비교 봉수


def _load_anchor_days(con):
    """raw_candles 에서 앵커가 계측된 봉만 뽑는다 — {날짜: {ts: (buy, sell, vol)}}."""
    days = {}
    for ts, ab, asell, vol in con.execute(
            "SELECT ts, anchor_buy, anchor_sell, volume FROM raw_candles"
            " WHERE anchor_buy IS NOT NULL AND anchor_sell IS NOT NULL"):
        days.setdefault(ts[:10], {})[ts] = (ab, asell, vol)
    return days


def _codes(con):
    return [r[0] for r in con.execute(
        "SELECT DISTINCT code FROM regular_candles ORDER BY code")]


def verify(only_code=None):
    rawcon, regcon = connect_ro(RAW_DB), connect_ro(REG_DB)
    anchors = _load_anchor_days(rawcon)
    codes = [only_code] if only_code else _codes(regcon)

    per_day = OrderedDict()
    for day in sorted(anchors):
        amap = anchors[day]
        best = None
        for code in codes:
            rows = regcon.execute(
                "SELECT ts, volume, cum_sell FROM regular_candles"
                " WHERE code=? AND trade_date=? ORDER BY ts", (code, day)).fetchall()
            if len(rows) < MIN_BARS:
                continue
            n = same = exact = near = 0
            prev = None
            for ts, vol, f10 in rows:
                if prev is not None and ts in amap and f10 is not None:
                    ab, asell, avol = amap[ts]
                    d10 = f10 - prev
                    n += 1
                    if vol == avol:
                        same += 1
                    if d10 == ab and (vol - d10) == asell:
                        exact += 1
                    if abs(d10 - ab) <= TOL:
                        near += 1
                prev = f10
            if n < MIN_BARS:
                continue
            cand = (same / float(n), code, n, same, exact, near)
            if best is None or cand > best:
                best = cand
        if best is None:
            per_day[day] = {"code": None, "reason": "비교 가능한 종목 없음(봉수 부족)"}
            continue
        same_r, code, n, same, exact, near = best
        if same_r < SAME_CONTRACT_MIN:
            per_day[day] = {"code": code, "n": n, "same_ratio": round(same_r, 4),
                            "reason": "거래량 불일치 — 미륵이가 다른 종목을 봤다(차월물 구간)"}
            continue
        per_day[day] = {"code": code, "n": n, "same_ratio": round(same_r, 4),
                        "exact": exact, "near": near,
                        "exact_ratio": round(exact / float(n), 4),
                        "verified": (exact / float(n)) >= EXACT_MATCH_MIN}
    return per_day


def main():
    ap = argparse.ArgumentParser(description="정규 분봉 필드10 = 누적 체결매수 검증 (559차 P0-1)")
    ap.add_argument("--json", action="store_true", help="JSON 으로 출력")
    ap.add_argument("--code", default=None, help="비교 종목 고정 (기본: 자동 선택)")
    args = ap.parse_args()

    guard_intraday(CHANNEL)

    if not (os.path.exists(REG_DB) and os.path.exists(RAW_DB)):
        print("[%s] DB 없음 — REG=%s RAW=%s" % (CHANNEL, os.path.exists(REG_DB),
                                                os.path.exists(RAW_DB)))
        return 0

    per_day = verify(args.code)
    ok = [d for d, v in per_day.items() if v.get("verified")]
    bad = [d for d, v in per_day.items() if v.get("verified") is False]
    skipped = [d for d, v in per_day.items() if "verified" not in v]

    if args.json:
        print(_json.dumps({"channel": CHANNEL, "verified_days": ok,
                           "failed_days": bad, "skipped_days": len(skipped),
                           "prereg": {"same_contract_min": SAME_CONTRACT_MIN,
                                      "exact_match_min": EXACT_MATCH_MIN,
                                      "min_bars": MIN_BARS},
                           "per_day": per_day}, ensure_ascii=False, indent=2))
        return 0

    print("=" * 72)
    print("[%s] 필드10(cum_sell 컬럼) = 누적 체결매수 인가 — 앵커 대조" % CHANNEL)
    print("=" * 72)
    print("사전등록  : 같은종목 거래량일치>=%.0f%% · 증분 정확일치>=%.0f%% · 최소 %d봉"
          % (SAME_CONTRACT_MIN * 100, EXACT_MATCH_MIN * 100, MIN_BARS))
    print("-" * 72)
    for day, v in per_day.items():
        if "verified" not in v:
            print("  %s  제외 — %s%s" % (day, v["reason"],
                                        "" if v.get("code") is None
                                        else " (%s, 일치 %.0f%%)" % (v["code"], v["same_ratio"] * 100)))
            continue
        print("  %s  %-6s  정확일치 %3d/%3d (%5.1f%%)  ±%d 이내 %3d  -> %s"
              % (day, v["code"], v["exact"], v["n"], v["exact_ratio"] * 100,
                 TOL, v["near"], "검증" if v["verified"] else "불일치"))
    print("-" * 72)
    print("검증된 거래일 %d · 불일치 %d · 제외 %d" % (len(ok), len(bad), len(skipped)))
    if bad:
        print("🔴 불일치가 있다 — 원천 필드 배치가 바뀌었을 수 있다.")
        print("   collect_regular_futures.py 의 FIELD10_SEMANTICS 부터 다시 잴 것.")
    elif ok:
        print("판정: 필드10 = 누적 체결매수 (검증 %d거래일). 컬럼명 cum_sell 은 오기다." % len(ok))
    else:
        print("판정: 표본 없음 — 미니 당월물 병행 거래일이 아직 없다.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
