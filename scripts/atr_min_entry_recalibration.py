# -*- coding: utf-8 -*-
"""[MW0601 539차] ATR 진입 하한(`ATR_MIN_ENTRY`) 26주 WFA 재검증 도구.

무엇을 재는가
-------------
`config/settings.py:ATR_MIN_ENTRY = 1.0`(pt)은 **절대 포인트 고정 임계**다.
그런데 ATR은 지수 수준에 비례해 커진다 — 같은 1.0pt가 종가 430일 때와 1,150일 때
전혀 다른 엄격도를 갖는다. 실측(2026-09-07):

    월       종가중앙   ATR중앙   ATR<1.0pt 비율
    2025-08    429      0.18        100.0%
    2026-03    821      1.27         27.9%
    2026-07  1,117      3.33          0.3%
    2026-09  1,050      1.03         45.6%

**아무도 값을 바꾸지 않았는데 게이트의 실효 강도가 0.3% ~ 100% 를 오갔다.**
이것이 이 항목을 26주 주기에 넣는 이유이며, `ATR_MAX_ENTRY`(상한)가 273차에
적응형으로 바뀐 것과 달리 **하한은 2026-05-08 도입 이래 한 번도 재보정된 적이 없다**
(`git log -S ATR_MIN_ENTRY` = 커밋 1건, `9524008`).

읽기 전용 진단이다 — `config/settings.py`를 자동 변경하지 않는다.

무엇을 하지 않는가
------------------
- **정답을 미리 정하지 않는다.** 절대 pt / 상대 bp / 적응형 분위 중 무엇이 맞는지는
  이 스크립트가 고르지 않는다. 실측을 내고 **판정만** 한다(§5). 재보정은 317차 절차
  (그리드서치 → OOS 검증 → 안정성 체크)를 따로 밟아야 한다.
- **차단군 손익 카운터팩추얼을 「완화하라」는 근거로 바로 쓰지 않는다.**
  `hurst_gate_shadow`와 같은 순서다 — 하드차단 해제가 아니라 임계 재보정부터.

실행
----
    python scripts/atr_min_entry_recalibration.py            # --verify 기본
    python scripts/atr_min_entry_recalibration.py --days 182 # 창 지정(기본 26주=182일)
    python scripts/atr_min_entry_recalibration.py --out data/daily_reports/atr_min_20260907.md

🔴 장 마감(15:35) 후에만. `utils.analysis_db.guard_intraday`가 장중 실행을 막는다.
   (`raw_features` · `ensemble_decisions` 전수 스캔이다 — 456차 CB⑤ 사고 참조)
"""
from __future__ import annotations

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
import re  # noqa: E402
import sqlite3  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from config.settings import (  # noqa: E402
    ATR_MIN_ENTRY, ATR_MAX_ENTRY, ATR_STOP_MULT, RAW_DATA_DB, PREDICTIONS_DB,
)

# ── 사전등록 판정 기준 (데이터를 보기 전에 고정한다 — SOP §11 / 458차 D6) ──────────
#
# 무엇을 FAIL로 볼 것인가: **차단률이 창마다 크게 흔들리면** 그 임계는 시장이 아니라
# 가격 수준을 재고 있는 것이다. 절대값이 얼마인지가 아니라 **안정성**이 판정 대상이다.
#
# 밴드는 도입 시점 의도에서 역산했다 — 이 게이트는 "1분봉 노이즈가 손절거리를 삼키는
# 극단 저변동"만 걸러내라고 만들어졌다(settings.py 의 ATR_MIN_ENTRY 바로 위 주석).
# 그런 구간이 장중의
# 20%를 넘으면 게이트가 원래 취지를 넘어 정상 장을 자르고 있는 것이고, 0.5% 미만이면
# 사실상 죽은 게이트다.
BLOCK_RATE_BAND = (0.005, 0.20)      # 월별 차단률 허용 밴드 (0.5% ~ 20%)
MAX_MONTHLY_SPREAD = 0.30            # 월별 차단률 최대−최소 허용 폭 (30%p)
MIN_MONTHS_FOR_VERDICT = 3           # 이보다 적으면 판정 보류

CF_HORIZON_MIN = 30                  # 카운터팩추얼 관찰 창(분) — hurst_gate_shadow와 동일


def _ro(path):
    return sqlite3.connect("file:%s?mode=ro" % str(path).replace("\\", "/"), uri=True)


def _pct(x):
    return "—" if x is None else "%.2f%%" % (x * 100.0)


def _med(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def _two_prop_z(k1, n1, k2, n2):
    """2표본 비율 z검정 (양측). scipy 없이 — BLAS 경로를 타지 않는다."""
    import math
    if not n1 or not n2:
        return float("nan"), float("nan")
    p1, p2 = k1 / float(n1), k2 / float(n2)
    p = (k1 + k2) / float(n1 + n2)
    se = math.sqrt(p * (1.0 - p) * (1.0 / n1 + 1.0 / n2))
    if se <= 0:
        return float("nan"), float("nan")
    z = (p1 - p2) / se
    return z, math.erfc(abs(z) / math.sqrt(2.0))


def _quantile(xs, q):
    if not xs:
        return None
    s = sorted(xs)
    i = int(round(q * (len(s) - 1)))
    return s[max(0, min(i, len(s) - 1))]


# ─────────────────────────── §1 실발동 ───────────────────────────
def measure_live_blocks(since):
    """`ensemble_decisions.entry_block_reason` 에서 이 게이트가 **구속 사유**였던 건.

    ⚠ main.py 는 elif 체인이라 앞선 게이트(IntradayRegime·Hurst)가 먼저 걸리면
    ATR 사유가 기록되지 않는다. 즉 이 수는 **이 게이트가 단독으로 막은 것**이며,
    "ATR<임계인 분" 전체와 혼동하면 안 된다(계측 4원칙 ③ — 절단을 값으로 위장 금지).
    """
    con = _ro(PREDICTIONS_DB)
    rows = con.execute(
        "SELECT ts, entry_block_reason FROM ensemble_decisions "
        "WHERE ts >= ? AND entry_block_reason IS NOT NULL AND entry_block_reason <> ''",
        (since,)).fetchall()
    total = con.execute("SELECT COUNT(*) FROM ensemble_decisions WHERE ts >= ?",
                        (since,)).fetchone()[0]
    con.close()

    lo, hi, days, vals = 0, 0, set(), []
    reasons = Counter()
    for ts, r in rows:
        r = r or ""
        m = re.match(r"\[차단\]\s*([^\d]{0,18})", r)
        reasons[(m.group(1).strip() if m else r[:18])] += 1
        if "변동성 부족" in r:
            lo += 1
            days.add(ts[:10])
            mv = re.search(r"ATR ([\d.]+)pt", r)
            if mv:
                vals.append(float(mv.group(1)))
        elif "고변동성 진입 차단" in r:
            hi += 1
    return {"cycles": total, "blocked": len(rows), "lo": lo, "hi": hi,
            "lo_days": len(days), "lo_atr_vals": vals, "reasons": reasons}


# ─────────────────────────── §2 드리프트 ───────────────────────────
def measure_drift(since):
    """월별 ATR·종가 수준과 현행 임계의 차단률. **이 항목의 존재 이유**를 재는 곳."""
    con = _ro(RAW_DATA_DB)
    cur = con.execute(
        "SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts", (since,))
    by_month = defaultdict(lambda: {"atr": [], "close": [], "bp": []})
    while True:
        chunk = cur.fetchmany(5000)
        if not chunk:
            break
        for ts, blob in chunk:
            hhmm = ts[11:16]
            if not ("09:15" <= hhmm < "15:10"):
                continue
            try:
                d = json.loads(blob)
            except Exception:
                continue
            a = d.get("atr")
            if a is None or a <= 0:
                continue          # 미측정 — 0으로 채우지 않는다(계측 4원칙 ②)
            m = ts[:7]
            by_month[m]["atr"].append(float(a))
    con.close()

    # 종가는 봉에서 (features 에 close 가 없을 수 있다)
    con = _ro(RAW_DATA_DB)
    for ts, c in con.execute("SELECT ts, close FROM raw_candles WHERE ts >= ?", (since,)):
        hhmm = ts[11:16]
        if "09:15" <= hhmm < "15:10" and c:
            by_month[ts[:7]]["close"].append(float(c))
    con.close()

    out = []
    for m in sorted(by_month):
        a = by_month[m]["atr"]
        c = by_month[m]["close"]
        if len(a) < 200:
            continue
        rate = sum(1 for x in a if x < ATR_MIN_ENTRY) / float(len(a))
        med_a, med_c = _med(a), _med(c)
        out.append({"month": m, "n": len(a), "atr_med": med_a, "close_med": med_c,
                    "bp_med": (med_a / med_c * 10000.0) if (med_a and med_c) else None,
                    "block_rate": rate})
    return out


# ────────────────────── §3 차단군 카운터팩추얼 ──────────────────────
def counterfactual(since):
    """ATR < 임계였던 분에 **가상 진입**했다면 stop/TP1 중 무엇에 먼저 닿았나.

    `hurst_gate_shadow`(297차)와 같은 방식이며 방향을 예측하지 않는다 — 양방향을
    모두 넣고 "그 구간이 실제로 휩쏘였는가(=스톱 우선 비율이 높은가)"만 본다.
    도입 근거가 「휩쏘 손절 급증 방지」이므로, 이 비율이 정상 구간과 같으면
    **도입 근거 자체가 소멸한다.**
    """
    con = _ro(RAW_DATA_DB)
    bars = con.execute(
        "SELECT ts, high, low, close FROM raw_candles WHERE ts >= ? ORDER BY ts",
        (since,)).fetchall()
    atr_by_ts = {}
    cur = con.execute("SELECT ts, features FROM raw_features WHERE ts >= ?", (since,))
    while True:
        chunk = cur.fetchmany(5000)
        if not chunk:
            break
        for ts, blob in chunk:
            try:
                a = json.loads(blob).get("atr")
            except Exception:
                a = None
            if a and a > 0:
                atr_by_ts[ts] = float(a)
    con.close()

    by_day = defaultdict(list)
    for ts, h, l, c in bars:
        by_day[ts[:10]].append((ts, h, l, c))

    res = {"low": Counter(), "normal": Counter()}
    for day, rows in by_day.items():
        n = len(rows)
        for i, (ts, h, l, c) in enumerate(rows):
            hhmm = ts[11:16]
            if not ("09:15" <= hhmm < "15:10"):
                continue
            atr = atr_by_ts.get(ts)
            if not atr:
                continue
            bucket = "low" if atr < ATR_MIN_ENTRY else "normal"
            for direction in (1, -1):
                entry = c
                stop = entry - direction * ATR_STOP_MULT * atr
                tp1 = entry + direction * 0.5 * atr        # 캠페인 sim 의 tp1_atr
                out = "NEITHER"
                for j in range(i + 1, min(i + 1 + CF_HORIZON_MIN, n)):
                    _, hj, lj, _cj = rows[j]
                    hit_stop = (lj <= stop) if direction > 0 else (hj >= stop)
                    hit_tp = (hj >= tp1) if direction > 0 else (lj <= tp1)
                    if hit_stop:                            # 동시 도달 시 스톱 우선(보수)
                        out = "STOP"
                        break
                    if hit_tp:
                        out = "TP1"
                        break
                res[bucket][out] += 1
    return res


# ─────────────────────── §4 임계 후보 안정성 ───────────────────────
def threshold_stability(drift_rows):
    """절대 pt 임계 vs 상대 bp 임계 — 어느 쪽이 창에 덜 흔들리는가.

    ⚠ **상대 임계를 권고하는 것이 아니다.** 「고정 pt가 흔들린다」는 §2 관찰이
    측정 방식 탓인지 확인하는 대조군이다. 상대 bp 도 함께 흔들리면 원인은
    가격 수준이 아니라 변동성 레짐 자체이며, 처방이 달라진다.
    """
    rows = [r for r in drift_rows if r["bp_med"]]
    if len(rows) < MIN_MONTHS_FOR_VERDICT:
        return None
    bps = [r["bp_med"] for r in rows]
    ref_bp = _quantile(bps, 0.05)
    out = []
    for r in rows:
        out.append({"month": r["month"], "abs_rate": r["block_rate"],
                    "atr_med": r["atr_med"], "bp_med": r["bp_med"]})
    return {"ref_bp": ref_bp, "rows": out}


# ────────────────────────────── 판정 ──────────────────────────────
def verdict(drift_rows, live):
    if len(drift_rows) < MIN_MONTHS_FOR_VERDICT:
        return "SKIP", "표본 미달 — 월 %d개 < %d" % (len(drift_rows), MIN_MONTHS_FOR_VERDICT)
    rates = [r["block_rate"] for r in drift_rows]
    lo, hi = min(rates), max(rates)
    spread = hi - lo
    fails = []
    if spread > MAX_MONTHLY_SPREAD:
        fails.append("월별 차단률 변동폭 %.1f%%p > 허용 %.1f%%p"
                     % (spread * 100, MAX_MONTHLY_SPREAD * 100))
    out_band = [r for r in drift_rows
                if not (BLOCK_RATE_BAND[0] <= r["block_rate"] <= BLOCK_RATE_BAND[1])]
    if len(out_band) > len(drift_rows) / 2.0:
        fails.append("월 %d/%d 이 허용 밴드(%s~%s) 밖"
                     % (len(out_band), len(drift_rows),
                        _pct(BLOCK_RATE_BAND[0]), _pct(BLOCK_RATE_BAND[1])))
    return ("FAIL", " · ".join(fails)) if fails else ("PASS", "차단률이 밴드 안에서 안정")


def main():
    ap = argparse.ArgumentParser(description="ATR_MIN_ENTRY 26주 WFA 재검증")
    ap.add_argument("--days", type=int, default=182, help="점검 창(일). 기본 182 = 26주")
    ap.add_argument("--out", default=None, help="마크다운 저장 경로")
    ap.add_argument("--verify", action="store_true", help="(기본 동작) 재검증 수행")
    ap.add_argument("--allow-intraday", action="store_true",
                    help="장중 실행 강제 — 의도를 남기는 장치. 평소 쓰지 말 것")
    args = ap.parse_args()

    if not args.allow_intraday:
        from utils.analysis_db import guard_intraday
        guard_intraday("atr_min_entry_recalibration")

    import datetime
    since = (datetime.date.today() - datetime.timedelta(days=args.days)).isoformat()

    L = []
    def w(s=""):
        L.append(s)

    w("# ATR 진입 하한 재검증 — `ATR_MIN_ENTRY = %.2f pt`" % ATR_MIN_ENTRY)
    w("")
    w("생성: %s · 창: 최근 %d일(%s 이후) · 스크립트 `scripts/atr_min_entry_recalibration.py`"
      % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), args.days, since))
    w("")
    w("현행 상수: `ATR_MIN_ENTRY=%.2f` / `ATR_MAX_ENTRY=%.2f`(정적) / `ATR_STOP_MULT=%.2f`"
      % (ATR_MIN_ENTRY, ATR_MAX_ENTRY, ATR_STOP_MULT))
    w("")

    # §1
    live = measure_live_blocks(since)
    w("## 1. 이 게이트가 실제로 몇 번 막았나")
    w("")
    w("| 항목 | 값 |")
    w("|---|---|")
    w("| 파이프라인 사이클 | %d |" % live["cycles"])
    w("| 차단 기록 전체 | %d |" % live["blocked"])
    w("| **ATR 하한 차단(변동성 부족)** | **%d건 / %d거래일** |" % (live["lo"], live["lo_days"]))
    w("| ATR 상한 차단(고변동성) | %d건 |" % live["hi"])
    if live["lo_atr_vals"]:
        v = live["lo_atr_vals"]
        w("| 차단 시 ATR (min/중앙/max) | %.2f / %.2f / %.2f |" % (min(v), _med(v), max(v)))
    w("")
    w("⚠ `main.py` 는 elif 체인이라 앞 게이트(IntradayRegime·Hurst)가 먼저 걸리면 이 사유가")
    w("기록되지 않는다. 위 수는 **이 게이트가 단독으로 막은 건**이며 「ATR<임계인 분」 전체가 아니다.")
    w("")
    w("상위 차단 사유:")
    w("")
    w("| 사유 | 건수 |")
    w("|---|---|")
    for k, v in live["reasons"].most_common(8):
        w("| %s | %d |" % (k, v))
    w("")

    # §2
    drift = measure_drift(since)
    w("## 2. 임계의 실효 강도가 창에 따라 흔들리는가 — 이 항목의 존재 이유")
    w("")
    w("| 월 | 분 | 종가 중앙 | ATR 중앙 | ATR/종가(bp) | **ATR<%.2fpt 비율** |" % ATR_MIN_ENTRY)
    w("|---|---|---|---|---|---|")
    for r in drift:
        w("| %s | %d | %.1f | %.2f | %.2f | **%s** |"
          % (r["month"], r["n"], r["close_med"] or float("nan"), r["atr_med"],
             r["bp_med"] or float("nan"), _pct(r["block_rate"])))
    w("")
    if drift:
        rates = [r["block_rate"] for r in drift]
        w("변동폭: 최소 %s ~ 최대 %s (%.1f%%p)"
          % (_pct(min(rates)), _pct(max(rates)), (max(rates) - min(rates)) * 100))
        w("")
    w("> ATR은 지수 수준에 비례한다. **값을 바꾸지 않아도** 지수가 오르면 같은 1.0pt가")
    w("> 느슨해지고, 내리면 조여진다. 이 표가 그 드리프트를 직접 보여준다.")
    w("")

    # §3
    cf = counterfactual(since)
    w("## 3. 도입 근거 재검 — 저ATR 구간이 정말 「휩쏘」인가")
    w("")
    w("도입 주석은 「1분봉 노이즈가 %.1f×ATR 손절거리를 초과 → 휩쏘 손절 급증 방지」다."
      % ATR_STOP_MULT)
    w("양방향 가상 진입 후 %d분 내 스톱/TP1 중 먼저 닿은 것을 센다(동시 도달 시 스톱 우선)."
      % CF_HORIZON_MIN)
    w("")
    w("| 구간 | 가상진입 | STOP 우선 | TP1 우선 | 미도달 | **STOP 비율** |")
    w("|---|---|---|---|---|---|")
    for bucket, lab in (("low", "ATR < %.2fpt (차단 대상)" % ATR_MIN_ENTRY),
                        ("normal", "ATR ≥ %.2fpt (정상)" % ATR_MIN_ENTRY)):
        c = cf[bucket]
        tot = sum(c.values())
        if not tot:
            w("| %s | 0 | | | | 표본없음 |" % lab)
            continue
        w("| %s | %d | %d | %d | %d | **%s** |"
          % (lab, tot, c["STOP"], c["TP1"], c["NEITHER"], _pct(c["STOP"] / float(tot))))
    lo_t = sum(cf["low"].values())
    no_t = sum(cf["normal"].values())
    if lo_t and no_t:
        p1 = cf["low"]["STOP"] / float(lo_t)
        p2 = cf["normal"]["STOP"] / float(no_t)
        d = p1 - p2
        z, pv = _two_prop_z(cf["low"]["STOP"], lo_t, cf["normal"]["STOP"], no_t)
        w("")
        w("차이: **%+.2f%%p** (2표본 비율검정 z=%+.2f, p=%.3f)." % (d * 100, z, pv))
        if pv >= 0.05:
            w("")
            w("🔴 **유의하지 않다 — 「휩쏘 방지」라는 도입 근거가 실측으로 지지되지 않는다.**")
            w("표본이 %s건인데도 갈리지 않는다는 것은 차이가 없다는 뜻에 가깝다."
              % format(lo_t + no_t, ",d"))
        else:
            w("")
            w("저ATR 구간이 실제로 스톱을 더 맞는다 — 도입 근거는 유지된다(크기는 별개로 볼 것).")
    w("")
    w("⚠ 이 표만으로 게이트를 풀지 말 것 — `hurst_gate_shadow`(297차)와 같은 순서다.")
    w("하드차단 해제가 아니라 **임계 재보정**부터 검토한다.")
    w("")

    # §4
    st = threshold_stability(drift)
    w("## 4. 대조 — 상대 임계로 재면 덜 흔들리는가")
    w("")
    if not st:
        w("표본 미달.")
    else:
        w("참조 상대임계(전 구간 bp 5분위): **%.2f bp**" % st["ref_bp"])
        w("")
        w("⚠ 상대 임계를 **권고하는 것이 아니다.** §2의 흔들림이 「고정 pt」 탓인지")
        w("변동성 레짐 자체 탓인지 가르는 대조군이다. 둘 다 흔들리면 처방이 달라진다.")
    w("")

    # §5
    v, why = verdict(drift, live)
    w("## 5. 판정")
    w("")
    w("사전등록 기준(데이터 확인 전 고정): 월별 차단률이 **%s ~ %s** 밴드 안이고,"
      % (_pct(BLOCK_RATE_BAND[0]), _pct(BLOCK_RATE_BAND[1])))
    w("월별 변동폭이 **%.0f%%p 이하**일 것. 월 %d개 미만이면 SKIP."
      % (MAX_MONTHLY_SPREAD * 100, MIN_MONTHS_FOR_VERDICT))
    w("")
    w("### 판정: **%s** — %s" % (v, why))
    w("")
    if v == "FAIL":
        w("**다음 절차(317차와 동일)**: ① 그리드서치(절대 pt · 상대 bp · 적응형 분위)")
        w("→ ② OOS 검증(라벨 소스는 게이트 입력과 독립일 것) → ③ 안정성 체크(±10~20% 파라미터)")
        w("→ ④ 재보정. 재보정 시 **불연속 마커**(`strategy_events` `METRIC_REDEFINITION`)를")
        w("남기고 CLAUDE.md 26주 목록 항목과 이 스크립트의 밴드를 함께 갱신할 것.")
        w("")
        w("⚠ **조이는 방향으로 먼저 가지 말 것.** 317차 FalseBlock 교훈 — 그때도 HurstGate가")
        w("진짜 추세를 72.3% 오판하고 있었고 해법은 게이트를 **푸는 것**이었다.")
    w("")

    text = "\n".join(L)
    print(text)
    if args.out:
        d = os.path.dirname(os.path.abspath(args.out))
        if d and not os.path.isdir(d):
            os.makedirs(d)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("\n[saved] %s" % args.out)
    return 0 if v in ("PASS", "SKIP") else 2


if __name__ == "__main__":
    raise SystemExit(main())
