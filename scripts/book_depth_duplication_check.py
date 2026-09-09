# -*- coding: utf-8 -*-
"""[MW0601 552차 후속 / Phase 3-0] 호가깊이 신규 파생의 **중복 축약 판정기**.

이것은 알파 판정기가 **아니다.**
--------------------------------
손익도 IC 도 보지 않는다. 보는 것은 하나뿐이다 —
**`book_net_ratio` 가 이미 라이브인 `microprice_depth_bias` 와 같은 것을 재고 있는가.**

손익을 함께 보면 사전등록이 오염된다(SOP `docs/Spec for feature/
피처_재검증_및_호라이즌배정_원칙.md`, 458차 D6). 그래서 이 스크립트는 **정제 단계**에
속하고, 통과 후에야 Phase 3(사전등록 검증)으로 넘어간다.

왜 필요한가
-----------
552차 초판 Phase 3 은 신규 파생으로 다음을 등록했다:

    book_net_ratio = (book_bid_tot - book_ask_tot) / (book_bid_tot + book_ask_tot)

그런데 같은 정의의 축이 **이미 라이브**다 —
`features/technical/microprice.py:MicropriceCalculator(max_levels=5)` 가 매 호가
이벤트마다 산출하는

    microprice_depth_bias = (bid_depth - ask_depth) / (bid_depth + ask_depth)

두 식은 **같은 5단**을 쓰고 **가중만 다르다**(균등 1,1,1,1,1 vs 조화 1,1/2,1/3,1/4,1/5).

🔴 이 프로젝트는 같은 판단을 이미 내렸다. `config/constants.py` (321·326차):

    `lob_imbalance_decay` 제거 — ... 그 계산 공식(호가 레벨 1/(i+1) 가중 매수/매도
    잔량 비율)이 이미 활성 피처인 `microprice_depth_bias` 와 수학적으로 사실상
    동일 ... 신규 구현 실익 없음으로 판단

즉 초판은 **326차가 중복으로 기각한 바로 그 양**을 신규 축으로 재등록하려 했다.
500차 OFI 3종(`ofi_imbalance = ofi_norm/3` · `ofi_pressure = sign(ofi_norm)`)을
독립 신호 3개로 세면 Bonferroni 분모가 틀리고 계열 검정의 유효 자유도가 무너지는
것과 **같은 계열**이다.

방법론
------
1. **거래일 단위** 1차 판정 — 분봉 풀링 상관은 자기상관 때문에 부풀려진다
   (372차: 신호단위 n=29,089 유의 -> 일자단위 58일 r=-0.099 로 소멸).
   분봉 단위도 함께 출력하되 **판정에는 쓰지 않는다**.
2. **Spearman(순위)** — 두 축은 가중만 다르므로 단조 관계가 본질이다. Pearson 은
   참고로만 출력한다.
3. **양쪽 유효행만** — `book_snaps > 0` 이고 `microprice_depth_bias` 가 비영인 분.
   `depth_bias` 는 2026-06 이전 전량 0.0 이라(호가 스트림 부재) 섞으면 상관이 0 으로
   희석된다 — 계측 4원칙 2(미측정 != 0).
4. **전·후반 부호 일관성** — 한쪽 구간의 우연이 아닌지 본다.

실행
----
    python scripts/book_depth_duplication_check.py
    python scripts/book_depth_duplication_check.py --json
    python scripts/book_depth_duplication_check.py --table session_bars

⚠ 장 마감 후 전용(456차 — 장중 라이브 DB 전수 스캔이 CB(5)를 자가유발했다).
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
import json  # noqa: E402
from collections import defaultdict  # noqa: E402

from utils.analysis_db import guard_intraday, connect_ro  # noqa: E402

CHANNEL = "book_depth_duplication_check"

# ── 사전등록 판정 기준 (데이터를 보기 전에 고정한다 — SOP / 458차 D6) ───────────────
#
# 🔴 이 값들을 실측을 본 뒤에 조정하지 말 것. 조정해야 한다면 그 사실과 이유를
#    `dev_memory/DECISION_LOG.md` 와 552차 계획서 Phase 3-0 표에 **함께** 남긴다
#    (461차 `mdd_pct` 교훈 — 정의를 바꾸면 시계열이 불연속이 된다).
DUP_THRESHOLD = 0.90          # |rho| >= 0.90  -> DUPLICATE (신규 축 등록 금지)
PARTIAL_THRESHOLD = 0.70      # 0.70 <= |rho| < 0.90 -> PARTIAL (잔차만 후보)
MIN_DAYS = 20                 # 거래일 표본 하한. 미달이면 INSUFFICIENT
SIGN_CONSISTENCY_REQUIRED = True   # 전·후반 부호가 같아야 판정을 신뢰한다

_LIVE_KEY = "microprice_depth_bias"


def _rank(xs):
    """평균순위(동률 보정). scipy 없이도 Spearman 을 낸다."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / float(n)
    my = sum(ys) / float(n)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / ((sxx ** 0.5) * (syy ** 0.5))


def _spearman(xs, ys):
    if len(xs) < 3:
        return None
    return _pearson(_rank(xs), _rank(ys))


def collect(table="raw_candles", db_path=None):
    """봉 단위 (ts, book_net_ratio, depth_bias) 를 모은다.

    양쪽이 **실측된** 분만 쓴다:
      - `book_snaps > 0`      — 552차 규약상 미수신 봉은 4열 NULL 이다
      - `depth_bias != 0.0`   — 2026-06 이전은 전량 0.0(호가 스트림 부재)이라
                                 섞으면 상관이 0 으로 희석된다(계측 4원칙 2)
    """
    if db_path is None:
        from config.settings import RAW_DATA_DB
        db_path = RAW_DATA_DB
    con = connect_ro(db_path)
    try:
        cols = set(r[1] for r in con.execute("PRAGMA table_info(%s)" % table))
        if "book_snaps" not in cols:
            return None, "테이블 %s 에 book_* 열이 없다 — 552차 마이그레이션 미적용" % table
        rows = con.execute(
            "SELECT ts, book_bid_tot, book_ask_tot FROM %s "
            "WHERE book_snaps IS NOT NULL AND book_snaps > 0 "
            "  AND book_bid_tot IS NOT NULL AND book_ask_tot IS NOT NULL "
            "ORDER BY ts" % table
        ).fetchall()
        if not rows:
            return [], None
        book = {}
        for ts, b, a in rows:
            tot = float(b) + float(a)
            if tot <= 0:
                continue                      # 정의되지 않는다 — 0 으로 채우지 않는다
            book[str(ts)] = (float(b) - float(a)) / tot
        if not book:
            return [], None
        lo, hi = min(book), max(book)
        out = []
        for ts, fj in con.execute(
            "SELECT ts, features FROM raw_features WHERE ts BETWEEN ? AND ? ORDER BY ts",
            (lo, hi),
        ):
            ts = str(ts)
            if ts not in book:
                continue
            if _LIVE_KEY not in fj:
                continue
            try:
                v = json.loads(fj).get(_LIVE_KEY)
            except Exception:
                continue
            if v is None or float(v) == 0.0:
                continue
            out.append((ts, book[ts], float(v)))
        return out, None
    finally:
        try:
            con.close()
        except Exception:
            pass


def _daily(pairs):
    """거래일 평균으로 접는다 — 1차 판정 단위(372차 교훈)."""
    acc = defaultdict(lambda: [0.0, 0.0, 0])
    for ts, bn, db in pairs:
        a = acc[ts[:10]]
        a[0] += bn
        a[1] += db
        a[2] += 1
    days = sorted(acc)
    return (days,
            [acc[d][0] / acc[d][2] for d in days],
            [acc[d][1] / acc[d][2] for d in days])


def judge(pairs):
    days, bx, dy = _daily(pairs)
    res = {
        "channel": CHANNEL,
        "n_bars": len(pairs),
        "n_days": len(days),
        "first_day": days[0] if days else None,
        "last_day": days[-1] if days else None,
        "thresholds": {"duplicate": DUP_THRESHOLD, "partial": PARTIAL_THRESHOLD,
                       "min_days": MIN_DAYS},
        "rho_daily": None,
        "pearson_daily": None,
        "rho_bar_reference_only": _spearman([p[1] for p in pairs], [p[2] for p in pairs]),
        "rho_first_half": None,
        "rho_second_half": None,
        "sign_consistent": None,
        "verdict": "INSUFFICIENT",
        "reason": "",
    }
    if len(days) < MIN_DAYS:
        res["reason"] = ("거래일 %d < min_days %d — 적립 대기. "
                         "문턱을 낮춰 판정하지 말 것(458차 D6)." % (len(days), MIN_DAYS))
        return res

    rho = _spearman(bx, dy)
    res["rho_daily"] = rho
    res["pearson_daily"] = _pearson(bx, dy)
    h = len(days) // 2
    r1 = _spearman(bx[:h], dy[:h])
    r2 = _spearman(bx[h:], dy[h:])
    res["rho_first_half"], res["rho_second_half"] = r1, r2
    res["sign_consistent"] = (
        None if (r1 is None or r2 is None) else ((r1 >= 0) == (r2 >= 0))
    )

    if rho is None:
        res["reason"] = "상관 계산 불가(분산 0) — 한쪽 축이 상수다. 원인 규명 먼저."
        return res

    a = abs(rho)
    if a >= DUP_THRESHOLD:
        res["verdict"] = "DUPLICATE"
        res["reason"] = (
            "|rho|=%.3f >= %.2f — `book_net_ratio` 는 `%s` 의 재가중이다. "
            "신규 축으로 등록하지 말 것(326차가 같은 이유로 lob_imbalance 를 기각했다). "
            "Phase 3 은 `book_rel` 만으로 진행한다." % (a, DUP_THRESHOLD, _LIVE_KEY))
    elif a >= PARTIAL_THRESHOLD:
        res["verdict"] = "PARTIAL"
        res["reason"] = (
            "|rho|=%.3f — 원축이 아니라 **잔차**(book_net_ratio 직교화)만 후보로 올릴 것. "
            "둘을 독립 신호 2개로 세면 Bonferroni 분모가 틀린다(500차)." % a)
    else:
        res["verdict"] = "INDEPENDENT"
        res["reason"] = (
            "|rho|=%.3f < %.2f — 균등가중이 조화가중과 다른 것을 재고 있다. "
            "Phase 3 사전등록으로 진행 가능." % (a, PARTIAL_THRESHOLD))

    if SIGN_CONSISTENCY_REQUIRED and res["sign_consistent"] is False:
        res["verdict"] = "INSUFFICIENT"
        res["reason"] = (
            "전반 rho=%s / 후반 rho=%s — 부호가 뒤집힌다. 한 구간의 우연일 수 있으므로 "
            "판정을 보류하고 표본을 더 쌓는다." % (r1, r2))
    return res


def main():
    ap = argparse.ArgumentParser(description="호가깊이 신규 파생 중복 축약 판정 (Phase 3-0)")
    ap.add_argument("--table", default="raw_candles",
                    choices=("raw_candles", "session_bars"))
    ap.add_argument("--json", action="store_true", help="기계 판독용 JSON 출력")
    args = ap.parse_args()

    guard_intraday(CHANNEL)

    pairs, err = collect(args.table)
    if err:
        print("[%s] %s" % (CHANNEL, err))
        return 1
    if not pairs:
        out = {"channel": CHANNEL, "verdict": "INSUFFICIENT", "n_bars": 0, "n_days": 0,
               "reason": ("book_* 실측 행이 아직 없다(552차 적재는 2026-09-10 거래일부터). "
                          "이것은 실패가 아니라 대기다 — 미측정과 0 을 구분한다.")}
        if args.json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            print("[%s] %s" % (CHANNEL, out["reason"]))
        return 0

    res = judge(pairs)
    res["table"] = args.table
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    def _f(v):
        return "n/a" if v is None else "%+.4f" % v

    print("=" * 72)
    print("[%s] Phase 3-0 중복 축약 — 알파 판정 아님(손익·IC 미사용)" % CHANNEL)
    print("=" * 72)
    print("표본      : %s ~ %s · %d거래일 · %d봉 (%s)"
          % (res["first_day"], res["last_day"], res["n_days"], res["n_bars"], args.table))
    print("사전등록  : DUPLICATE |rho|>=%.2f / PARTIAL >=%.2f / min_days=%d"
          % (DUP_THRESHOLD, PARTIAL_THRESHOLD, MIN_DAYS))
    print("-" * 72)
    print("rho  (거래일, Spearman) : %s   <- 판정 근거" % _f(res["rho_daily"]))
    print("pearson (거래일)        : %s" % _f(res["pearson_daily"]))
    print("rho  (분봉)             : %s   <- 참고용, 판정 미사용(372차)"
          % _f(res["rho_bar_reference_only"]))
    print("전반 / 후반             : %s / %s  (부호일치=%s)"
          % (_f(res["rho_first_half"]), _f(res["rho_second_half"]),
             res["sign_consistent"]))
    print("-" * 72)
    print("판정: %s" % res["verdict"])
    print("      %s" % res["reason"])
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
