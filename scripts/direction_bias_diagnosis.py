# -*- coding: utf-8 -*-
"""[MW0601 457차 / A1] 방향 예측 편향 진단 하네스 — **읽기 전용·진단 전용**.

## 왜 이 스크립트가 필요한가 — 2026-08-11 실측

시장이 964.42 → 992.86(+2.9%) 오른 날, 앙상블은 SHORT를 LONG의 **8배** 냈다
(dir=-1 152회 / dir=+1 19회). 호라이즌별로는 더 선명하다:

    호라이즌   예측 UP:DN      실제 UP:DN     적중률
    1m         115 : 147        115 : 112     32.6%
    3m          33 : 133 (1:4)   78 :  80     39.2%
    5m          17 :  73 (1:4)   52 :  46     39.3%
    10m         11 :  47 (1:4)   22 :  21     35.2%
    30m         22 : 145 (1:6.6) 131 :  68    29.4%   ← 랜덤(33.3%) 이하

그런데 **이 편향을 잡아낸 감시자가 하나도 없었다.** DriftDetector는 pnl/wr/pf
3축만 보고 CLEAR를 냈고, Brier 경고는 확신도만, CB③-P4는 30m 정확도만 본다.
"신호 방향 분포가 실현 방향 분포와 체계적으로 어긋나는가"를 재는 축이 없다.

## 이 스크립트가 하는 일 (진단 3항)

    S1-a  레이블 분포     — 실현 라벨(actual)이 이미 DN 편중인지
    S1-b  확률 절편 편향  — up/down/flat_prob 평균이 구조적으로 치우쳤는지
    S1-c  편향 검정       — 일자단위 독립관측 + Bonferroni, 혼동행렬, 역방향 검정

세 결과의 조합으로 원인 후보가 갈린다:

    S1-a DN편중 & S1-b DN편중   → 레이블/학습창 문제 (임계 비대칭·26주 하락 편중)
    S1-a 균형   & S1-b DN편중   → 모델 절편 편향 (클래스 가중·보정기)
    S1-a 균형   & S1-b 균형     → 편향이 앙상블 합성 단계에서 생김 (게이트·가중)

## ⚠ 진단 전용이다

**어떤 산출도 조치 근거가 아니다.** 특히 "예측을 뒤집으면 적중률이 오른다"는
역방향 검정 결과를 그대로 정책에 반영하지 말 것 — 3분류 문제에서 한쪽으로
치우친 예측기의 반전은 표본 편향만으로도 개선처럼 보인다. 조치는 313차 원칙대로
**주간회의 승인**을 거친다(456차 계획서 §6).

일자단위 검정을 쓰는 이유는 372차가 확인한 대로 신호단위 n이 독립이 아니기
때문이다. 같은 분의 6개 호라이즌, 인접 분끼리 전부 상관돼 있다.

읽기 전용: predictions.db만 읽는다. 출력: stdout + data/direction_bias/*.{json,md}
(런타임 산출물 — 커밋 금지).

실행:
    python scripts/direction_bias_diagnosis.py --days 60
    python scripts/direction_bias_diagnosis.py --days 5 --horizons 3m,5m
"""
from __future__ import print_function

import argparse
import datetime
import json
import math
import os
import sys
from collections import OrderedDict, defaultdict

_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _utf8_console():
    """cp949 콘솔 인코딩 가드 — CLI 실행 시에만."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


from config.settings import PREDICTIONS_DB, HORIZONS  # noqa: E402

OUT_DIR = os.path.join(_ROOT, "data", "direction_bias")

#: 3분류 랜덤 기준선. 적중률을 이 값과 비교한다.
RANDOM_ACC = 1.0 / 3.0

#: 일자단위 검정에 필요한 최소 거래일 수. 이보다 적으면 판정하지 않고 표만 낸다.
MIN_DAYS = 20

#: 일자당 최소 채점 표본 — 이보다 적은 날은 그 호라이즌에서 제외(개장 직후 재기동 등).
MIN_DAY_ROWS = 10


# ── 통계 헬퍼 (외부 의존 없이 — py37_32/py310_64 양쪽에서 동일 동작) ─────────

def mean(xs):
    return sum(xs) / float(len(xs)) if xs else float("nan")


def stdev(xs):
    n = len(xs)
    if n < 2:
        return float("nan")
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def ttest_1samp(xs, mu=0.0):
    """일표본 t검정 — (t, df). p는 정규근사로 별도 산출한다."""
    n = len(xs)
    if n < 2:
        return float("nan"), 0
    sd = stdev(xs)
    if not sd or sd <= 0:
        return float("nan"), n - 1
    return (mean(xs) - mu) / (sd / math.sqrt(n)), n - 1


def norm_p_two_sided(t):
    """|t|의 양측 p — 정규근사(df≥20에서 충분).

    scipy 의존을 피한다: 이 프로젝트는 py37_32에서 scipy 1.5.4 고정이라
    분석 스크립트가 py310_64로도 돌아야 한다(CLAUDE.md 운영환경).
    """
    if t != t:  # NaN
        return float("nan")
    z = abs(float(t))
    # Abramowitz-Stegun 26.2.17 — 표준정규 상측꼬리
    p_one = 0.5 * math.erfc(z / math.sqrt(2.0))
    return min(1.0, 2.0 * p_one)


# ── 데이터 로드 ────────────────────────────────────────────────────────────

def load_rows(days, horizons):
    """predictions.db에서 채점 완료 행을 읽는다. (rows, dates)

    rows: [(date, horizon, direction, actual, up_prob, down_prob, flat_prob), ...]
    """
    from utils.analysis_db import connect_ro
    con = connect_ro(PREDICTIONS_DB)
    cur = con.cursor()
    cur.execute(
        "SELECT DISTINCT substr(ts,1,10) d FROM predictions "
        "WHERE actual IS NOT NULL ORDER BY d DESC LIMIT ?", (int(days),)
    )
    dates = sorted(r[0] for r in cur.fetchall())
    if not dates:
        return [], []
    qmarks = ",".join("?" * len(dates))
    hz_marks = ",".join("?" * len(horizons))
    cur.execute(
        "SELECT substr(ts,1,10), horizon, direction, actual, "
        "       up_prob, down_prob, flat_prob "
        "FROM predictions "
        "WHERE actual IS NOT NULL AND substr(ts,1,10) IN (%s) AND horizon IN (%s)"
        % (qmarks, hz_marks),
        tuple(dates) + tuple(horizons),
    )
    rows = cur.fetchall()
    con.close()
    return rows, dates


def group_by_day_hz(rows):
    """(horizon, date) → 그 날 그 호라이즌의 행 목록."""
    g = defaultdict(list)
    for r in rows:
        g[(r[1], r[0])].append(r)
    return g


# ── S1-a: 실현 레이블 분포 ─────────────────────────────────────────────────

def s1a_label_distribution(grouped, horizons):
    """실현 라벨(actual)의 UP/DN/FLAT 비율 — 일자단위 평균 ± 검정.

    학습 레이블 자체가 하락 편중이면 모델의 SHORT 편향은 '학습한 대로' 나온 것이다.
    반대로 라벨이 균형인데 예측만 치우쳤다면 원인은 모델/합성 쪽이다.
    """
    out = OrderedDict()
    for hz in horizons:
        day_skews, day_up, day_dn, day_fl, ndays = [], [], [], [], 0
        for (h, d), rs in grouped.items():
            if h != hz or len(rs) < MIN_DAY_ROWS:
                continue
            n = float(len(rs))
            up = sum(1 for r in rs if r[3] == 1) / n
            dn = sum(1 for r in rs if r[3] == -1) / n
            fl = sum(1 for r in rs if r[3] == 0) / n
            day_up.append(up); day_dn.append(dn); day_fl.append(fl)
            day_skews.append(up - dn)   # >0 이면 그날 라벨이 UP 우위
            ndays += 1
        if ndays == 0:
            out[hz] = None
            continue
        t, df = ttest_1samp(day_skews, 0.0)
        out[hz] = {
            "n_days": ndays,
            "up_ratio": mean(day_up), "dn_ratio": mean(day_dn), "flat_ratio": mean(day_fl),
            "skew_mean": mean(day_skews), "skew_sd": stdev(day_skews),
            "t": t, "df": df, "p": norm_p_two_sided(t),
        }
    return out


# ── S1-b: 예측 확률 절편 편향 ──────────────────────────────────────────────

def s1b_prob_intercept(grouped, horizons):
    """up_prob / down_prob 평균의 일자단위 차이 — 확률 출력 자체의 치우침.

    direction은 argmax라 임계 근방에서 표본 편향이 증폭된다. 확률 평균을 직접 보면
    "모델이 그렇게 확신하는가" 대 "argmax가 그렇게 갈리는가"를 분리할 수 있다.
    """
    out = OrderedDict()
    for hz in horizons:
        day_gap, day_up, day_dn, day_fl, ndays = [], [], [], [], 0
        for (h, d), rs in grouped.items():
            if h != hz or len(rs) < MIN_DAY_ROWS:
                continue
            up = mean([float(r[4] or 0.0) for r in rs])
            dn = mean([float(r[5] or 0.0) for r in rs])
            fl = mean([float(r[6] or 0.0) for r in rs])
            day_up.append(up); day_dn.append(dn); day_fl.append(fl)
            day_gap.append(up - dn)   # <0 이면 그날 확률이 DN 쪽으로 치우침
            ndays += 1
        if ndays == 0:
            out[hz] = None
            continue
        t, df = ttest_1samp(day_gap, 0.0)
        out[hz] = {
            "n_days": ndays,
            "up_prob": mean(day_up), "down_prob": mean(day_dn), "flat_prob": mean(day_fl),
            "gap_mean": mean(day_gap), "gap_sd": stdev(day_gap),
            "t": t, "df": df, "p": norm_p_two_sided(t),
        }
    return out


# ── S1-c: 편향 검정 + 혼동행렬 + 역방향 검정 ───────────────────────────────

def s1c_bias_test(grouped, horizons):
    """예측 skew 와 실현 skew 의 **차이**를 일자단위로 검정한다.

    핵심: 예측이 DN 쪽이어도 그날 시장이 정말 내렸다면 편향이 아니다. 그래서
    (pred_up−pred_dn) − (actual_up−actual_dn) 을 관측치로 삼는다. 이 값이 0에서
    유의하게 음수면 **시장 대비 구조적으로 SHORT를 더 낸다**는 뜻이다.
    """
    out = OrderedDict()
    m = len(horizons)   # Bonferroni 보정 인자 (호라이즌 수)
    for hz in horizons:
        deltas, accs, rev_accs, ndays = [], [], [], 0
        conf = defaultdict(int)   # (pred, actual) → count
        for (h, d), rs in grouped.items():
            if h != hz or len(rs) < MIN_DAY_ROWS:
                continue
            n = float(len(rs))
            p_up = sum(1 for r in rs if r[2] == 1) / n
            p_dn = sum(1 for r in rs if r[2] == -1) / n
            a_up = sum(1 for r in rs if r[3] == 1) / n
            a_dn = sum(1 for r in rs if r[3] == -1) / n
            deltas.append((p_up - p_dn) - (a_up - a_dn))
            accs.append(sum(1 for r in rs if r[2] == r[3]) / n)
            # 역방향 검정 — 비FLAT 예측만 뒤집는다(FLAT의 반대는 정의되지 않는다)
            rev_accs.append(
                sum(1 for r in rs if (-r[2] if r[2] != 0 else 0) == r[3]) / n
            )
            for r in rs:
                conf[(r[2], r[3])] += 1
            ndays += 1
        if ndays == 0:
            out[hz] = None
            continue
        t, df = ttest_1samp(deltas, 0.0)
        p = norm_p_two_sided(t)
        t_acc, _ = ttest_1samp(accs, RANDOM_ACC)
        out[hz] = {
            "n_days": ndays,
            "delta_mean": mean(deltas), "delta_sd": stdev(deltas),
            "t": t, "df": df, "p": p,
            "p_bonferroni": min(1.0, p * m),
            "significant": (p * m < 0.05) if p == p else False,
            "acc_mean": mean(accs), "acc_t_vs_random": t_acc,
            "acc_p_vs_random": norm_p_two_sided(t_acc),
            "rev_acc_mean": mean(rev_accs),
            "confusion": {"%d|%d" % k: v for k, v in sorted(conf.items())},
        }
    return out


# ── 리포트 ────────────────────────────────────────────────────────────────

def _fmt(v, spec="%.4f"):
    if v is None or (isinstance(v, float) and v != v):
        return "  n/a "
    return spec % v


def render(dates, horizons, a, b, c):
    L = []
    W = L.append
    W("# 방향 편향 진단 (457차 A1)\n")
    W("- 구간: %s ~ %s (%d거래일)" % (dates[0], dates[-1], len(dates)))
    W("- 일자단위 독립관측 · Bonferroni 보정(m=%d) · 랜덤 기준 %.4f" % (len(horizons), RANDOM_ACC))
    W("- ⚠ **진단 전용** — 조치 근거로 쓰지 말 것 (313차, 주간회의 승인 필요)\n")

    if len(dates) < MIN_DAYS:
        W("> ⚠ 거래일 %d < %d — **판정하지 않는다.** 아래는 표만 참고할 것.\n"
          % (len(dates), MIN_DAYS))

    W("## S1-a 실현 레이블 분포 (actual)\n")
    W("| 호라이즌 | 일수 | UP | DN | FLAT | skew(UP−DN) | t | p |")
    W("|---|---|---|---|---|---|---|---|")
    for hz in horizons:
        r = a.get(hz)
        if not r:
            W("| %s | — | — | — | — | — | — | — |" % hz); continue
        W("| %s | %d | %s | %s | %s | %s | %s | %s |" % (
            hz, r["n_days"], _fmt(r["up_ratio"], "%.3f"), _fmt(r["dn_ratio"], "%.3f"),
            _fmt(r["flat_ratio"], "%.3f"), _fmt(r["skew_mean"], "%+.4f"),
            _fmt(r["t"], "%+.2f"), _fmt(r["p"], "%.4f")))
    W("\n> skew < 0 이고 유의하면 **학습 라벨 자체가 하락 편중**이다.\n")

    W("## S1-b 예측 확률 절편 (up_prob / down_prob)\n")
    W("| 호라이즌 | 일수 | up_prob | down_prob | flat_prob | gap(up−dn) | t | p |")
    W("|---|---|---|---|---|---|---|---|")
    for hz in horizons:
        r = b.get(hz)
        if not r:
            W("| %s | — | — | — | — | — | — | — |" % hz); continue
        W("| %s | %d | %s | %s | %s | %s | %s | %s |" % (
            hz, r["n_days"], _fmt(r["up_prob"], "%.3f"), _fmt(r["down_prob"], "%.3f"),
            _fmt(r["flat_prob"], "%.3f"), _fmt(r["gap_mean"], "%+.4f"),
            _fmt(r["t"], "%+.2f"), _fmt(r["p"], "%.4f")))
    W("\n> gap < 0 이고 유의하면 **확률 출력 자체가 DN 쪽으로 치우쳐** 있다"
      " (argmax 표본 편향이 아니다).\n")

    W("## S1-c 시장 대비 편향 검정\n")
    W("관측치 = (예측 UP비−DN비) − (실현 UP비−DN비). 0이면 시장을 그대로 따라간 것.\n")
    W("| 호라이즌 | 일수 | Δ평균 | t | p | p(Bonf) | 유의 | 적중률 | vs랜덤 t | 반전적중 |")
    W("|---|---|---|---|---|---|---|---|---|---|")
    for hz in horizons:
        r = c.get(hz)
        if not r:
            W("| %s | — | — | — | — | — | — | — | — | — |" % hz); continue
        W("| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            hz, r["n_days"], _fmt(r["delta_mean"], "%+.4f"), _fmt(r["t"], "%+.2f"),
            _fmt(r["p"], "%.4f"), _fmt(r["p_bonferroni"], "%.4f"),
            "🔴 예" if r["significant"] else "아니오",
            _fmt(r["acc_mean"], "%.4f"), _fmt(r["acc_t_vs_random"], "%+.2f"),
            _fmt(r["rev_acc_mean"], "%.4f")))
    W("")

    W("### 혼동행렬 (예측|실현 → 건수)\n")
    for hz in horizons:
        r = c.get(hz)
        if not r:
            continue
        W("**%s**  " % hz + "  ".join(
            "`%s`=%d" % (k, v) for k, v in sorted(r["confusion"].items())))
    W("")

    # ── 원인 후보 판별 (S1-a × S1-b 조합) ──
    W("## 원인 후보 (S1-a × S1-b 조합)\n")
    W("| 호라이즌 | 라벨 DN편중? | 확률 DN편중? | 시사점 |")
    W("|---|---|---|---|")
    for hz in horizons:
        ra, rb = a.get(hz), b.get(hz)
        if not ra or not rb:
            W("| %s | — | — | 표본 부족 |" % hz); continue
        lab_dn = (ra["skew_mean"] < 0) and (ra["p"] < 0.05)
        prb_dn = (rb["gap_mean"] < 0) and (rb["p"] < 0.05)
        if lab_dn and prb_dn:
            note = "레이블/학습창 — 임계 비대칭·26주 하락 편중 의심"
        elif (not lab_dn) and prb_dn:
            note = "**모델 절편** — 클래스 가중·보정기 의심"
        elif (not lab_dn) and (not prb_dn):
            note = "확률은 균형 — 편향은 앙상블 합성/게이트 단계에서 발생"
        else:
            note = "라벨은 DN인데 확률은 균형 — 모델이 라벨을 덜 따름"
        W("| %s | %s | %s | %s |" % (
            hz, "예" if lab_dn else "아니오", "예" if prb_dn else "아니오", note))
    W("")
    W("> ⚠ 이 표는 **가설 분해**다. 확정 진단이 아니며, 조치는 주간회의 승인을 거친다.")
    return "\n".join(L)


def main():
    _utf8_console()
    ap = argparse.ArgumentParser(
        description="방향 예측 편향 진단 (457차 A1, 읽기 전용·진단 전용)")
    ap.add_argument("--days", type=int, default=60, help="최근 N거래일 (기본 60)")
    ap.add_argument("--horizons", type=str, default="",
                    help="쉼표 구분 (기본: 전 호라이즌)")
    ap.add_argument("--no-save", action="store_true", help="파일 저장 생략")
    args = ap.parse_args()

    # 라이브 DB를 대량 읽는다 — 장중이면 CB⑤를 유발할 수 있어 차단한다(456차 F8).
    from utils.analysis_db import guard_intraday
    guard_intraday("direction_bias_diagnosis")

    horizons = ([h.strip() for h in args.horizons.split(",") if h.strip()]
                or list(HORIZONS))

    rows, dates = load_rows(args.days, horizons)
    if not rows:
        print("채점 완료 예측이 없다 — predictions.db 확인 필요")
        return 1
    print("predictions %d행, %d거래일 (%s ~ %s)"
          % (len(rows), len(dates), dates[0], dates[-1]))

    grouped = group_by_day_hz(rows)
    a = s1a_label_distribution(grouped, horizons)
    b = s1b_prob_intercept(grouped, horizons)
    c = s1c_bias_test(grouped, horizons)

    md = render(dates, horizons, a, b, c)
    print()
    print(md)

    if not args.no_save:
        stamp = datetime.date.today().strftime("%Y%m%d")
        try:
            os.makedirs(OUT_DIR)
        except OSError:
            pass
        base = os.path.join(OUT_DIR, "direction_bias_%s" % stamp)
        with open(base + ".md", "w", encoding="utf-8") as fh:
            fh.write(md)
        with open(base + ".json", "w", encoding="utf-8") as fh:
            json.dump({"dates": dates, "horizons": horizons,
                       "s1a": a, "s1b": b, "s1c": c}, fh,
                      ensure_ascii=False, indent=2)
        print("\n저장: %s.{md,json}" % base)
    return 0


if __name__ == "__main__":
    sys.exit(main())
