# -*- coding: utf-8 -*-
"""[MW0602 458차 / 3-B] 조기청산 반사실 — [49] early_trail_exit_watch.

무엇을 재는가
--------------
**TP1 도달 전에 트레일 틱스톱으로 익절된 청산**(2026-07-14~ 실측 58건 — 익절의
최빈 형태, 계약당 평균 +0.452pt)에 대해, "그 시점에 끊지 않고 **원 사다리**
(진입 시 로그에 기록된 실제 손절가·2차 목표가)를 유지했다면"을 반사실로 잰다.

왜 이 축인가 — 458차 실측(`docs/미륵이고도화3/손익원천이전_제안_2026-08-10.md`):

  · TP1 도달률 6.6% (10/152) — 기존 채널([25]/[25-B]/tp1_trail_shadow)은 전부
    **TP1 도달 이후**의 축이라, 도달률 바깥 93.4% 영역은 어느 채널도 안 본다.
  · 승리 중앙값 +0.171R — 이익 실현의 부스러기화가 손익비 0.58의 주 원인.
  · 단, 트레일 기계 전체는 단순사다리 대비 +38.8pt 순기여 — **기계 제거가 아니라
    이 특정 발동 지점의 회수 가치**만 묻는다.

456차 꼬리스톱 가설(스톱 트리거 방식 고저vs종가 — 기각)과 **다른 질문**이다:
그건 "어떻게 끊는가", 이것은 "언제부터 끊기 시작하는가"다.

반사실 정의 (개입의 정의이지 충실도 타협이 아님)
------------------------------------------------
청산 다음 분부터 그날 15:09까지, 청산된 수량에 대해:

  arm "orig"      : 원 손절가 / 원 2차(TP2)가 / 세션 종가 중 먼저 닿는 것으로 전량 청산
  arm "breakeven" : 손절을 진입가로 강등한 병기 팔 (반사실 손익 하한 0 근방)

같은 봉에서 스톱·목표 동시 히트면 **스톱 우선**(캠페인 공통 보수 관례).
사다리 레벨은 시뮬 재구성이 아니라 **진입 시점 TRADE 로그의 실제 값**
(`[Position] 진입 ... 손절=S 1차=T1(×m) 2차=T2`)을 쓴다 — [47] 충실도 문제가
반사실 팔에 적용되지 않는 이유다(실현 팔은 실거래 그 자체, 반사실 팔은 정의된 개입).

판정 (사전등록: config/settings.py VALIDATION_CAMPAIGN["early_trail_exit_watch"])
---------------------------------------------------------------------------------
  개선(improvement) = 반사실 pt − 실현 pt   (계약당, 레그 단위)
  FAIL(회수 가치 있음 → 트레일 완화 변형 2차 등록 검토):
      n ≥ min_samples AND 거래일 ≥ min_days
      AND 주팔(orig) 평균 개선 > roundtrip_cost_pt
      AND 일자단위 부호검정 p < 0.05
  PASS(현행 유지): 표본 충족 + 위 조건 미달
  INSUFFICIENT: 표본 미달

⚠ FAIL이 나와도 자동 적용 금지 — 트레일 완화 변형의 A/B는 별도 사전등록이 필요하고
([25]와 같은 형식), MW0601 대조 없이는 안건으로 올리지 않는다(0808 D2 교훈).

사용
----
    python scripts/early_trail_exit_counterfactual.py                # 사전등록 창 전체
    python scripts/early_trail_exit_counterfactual.py --since 2026-08-01
    python scripts/early_trail_exit_counterfactual.py --json

읽기 전용 — DB·로그에 아무것도 쓰지 않는다. py310_64/py37_32 양쪽 동작.
"""
import argparse
import collections
import datetime
import glob
import io
import json
import math
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MIREUK_TEST_MODE", "1")

from config.settings import TRADES_DB, RAW_DATA_DB, VALIDATION_CAMPAIGN  # noqa: E402

_TS = "%Y-%m-%d %H:%M:%S"
_SESSION_LAST = "15:09"
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

# 진입 로그 줄 — 예:
# [Position] 진입 SHORT 1계약 @ 978.9 | 손절=981.85 1차=977.92(×0.60) 2차=975.95 horizon=3m hurst=trend
_ENTRY_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[Position\] 진입 (LONG|SHORT) .*@ ([\d.]+) \| "
    r"손절=([\d.]+) 1차=([\d.]+).*2차=([\d.]+)(?: horizon=(\S+))?",
    re.MULTILINE)


def _conn(path):
    c = sqlite3.connect("file:%s?mode=ro" % str(path).replace("\\", "/"), uri=True)
    c.row_factory = sqlite3.Row
    return c


def load_entry_ladders(since):
    """TRADE 로그에서 실제 사다리 레벨을 파싱한다. {로그시각: dict}."""
    out = {}
    for f in sorted(glob.glob(os.path.join(_LOG_DIR, "2026*_TRADE.log"))):
        day = os.path.basename(f)[:8]
        day_iso = "%s-%s-%s" % (day[:4], day[4:6], day[6:8])
        if day_iso < since[:10]:
            continue
        try:
            text = io.open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in _ENTRY_RE.finditer(text.replace("\r", "")):
            ts, dirn, px, stop, tp1, tp2, hz = m.groups()
            out[ts] = {
                "direction": dirn, "entry_px": float(px), "stop_px": float(stop),
                "tp1_px": float(tp1), "tp2_px": float(tp2), "horizon": hz or "",
            }
    return out


def _match_ladder(ladders, entry_ts, tol_sec=90):
    """trades.entry_ts(체결 시각)와 로그의 진입 시각을 ±tol초로 짝짓는다."""
    if entry_ts in ladders:
        return ladders[entry_ts]
    try:
        t0 = datetime.datetime.strptime(entry_ts, _TS)
    except ValueError:
        return None
    best, best_d = None, tol_sec + 1
    for ts, lad in ladders.items():
        try:
            d = abs((datetime.datetime.strptime(ts, _TS) - t0).total_seconds())
        except ValueError:
            continue
        if d < best_d:
            best, best_d = lad, d
    return best if best_d <= tol_sec else None


def load_population(since):
    """모집단: TP1 미도달 포지션의 익절성 틱스톱 레그."""
    with _conn(TRADES_DB) as c:
        legs = [dict(r) for r in c.execute(
            "SELECT entry_ts, exit_ts, direction, entry_price, exit_price, "
            "       quantity, pnl_pts, exit_reason "
            "  FROM trades WHERE entry_ts >= ? ORDER BY entry_ts, exit_ts", (since,))]
    by_pos = collections.defaultdict(list)
    for l in legs:
        by_pos[l["entry_ts"]].append(l)
    pop = []
    for ets, ls in by_pos.items():
        if any("TP1" in (l["exit_reason"] or "") for l in ls):
            continue                       # TP1 도달 포지션은 [25]/trail_shadow 영역
        for l in ls:
            if l["exit_reason"] == "하드스톱(틱)" and (l["pnl_pts"] or 0) > 0:
                pop.append(l)
    return pop


def load_bars(since):
    bars = {}
    with _conn(RAW_DATA_DB) as c:
        for r in c.execute("SELECT ts, high, low, close FROM raw_candles WHERE ts >= ?",
                           (since,)):
            bars[str(r["ts"])] = (float(r["high"]), float(r["low"]), float(r["close"]))
    return bars


def continuation(exit_ts, entry_px, stop_px, tp2_px, sign, bars):
    """청산 다음 분부터 15:09까지 원 사다리 연속 재생. 반환: 계약당 pt (진입가 기준)."""
    try:
        cur = datetime.datetime.strptime(exit_ts, _TS).replace(second=0)
    except ValueError:
        return None
    day = exit_ts[:10]
    last_cl = None
    for _ in range(400):
        cur += datetime.timedelta(minutes=1)
        if cur.strftime("%Y-%m-%d") != day or cur.strftime("%H:%M") > _SESSION_LAST:
            break
        bar = bars.get(cur.strftime(_TS))
        if bar is None:
            continue
        hi, lo, cl = bar
        last_cl = cl
        hit_stop = (lo <= stop_px) if sign > 0 else (hi >= stop_px)
        hit_tp2 = (hi >= tp2_px) if sign > 0 else (lo <= tp2_px)
        if hit_stop:                        # 동시 히트 → 스톱 우선 (보수)
            return (stop_px - entry_px) * sign
        if hit_tp2:
            return (tp2_px - entry_px) * sign
    if last_cl is None:
        return None                         # 청산 후 봉 없음 (세션 끝) → 측정 불가
    return (last_cl - entry_px) * sign


def _comb(n, k):
    """py37_32 호환 (math.comb는 3.8+)."""
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))


def _binom_two_sided(k, n):
    if n == 0:
        return 1.0
    p = sum(_comb(n, i) for i in range(0, min(k, n - k) + 1)) / float(2 ** n) * 2
    return min(1.0, p)


def evaluate(since=None, as_json=False):
    cr = VALIDATION_CAMPAIGN.get("early_trail_exit_watch") or {}
    since = since or cr.get("start_date", "2026-07-14")
    ladders = load_entry_ladders(since)
    pop = load_population(since)
    bars = load_bars(since)

    rows, unmatched, unmeasurable = [], 0, 0
    for l in pop:
        lad = _match_ladder(ladders, l["entry_ts"])
        if lad is None:
            unmatched += 1
            continue
        sign = 1 if l["direction"] == "LONG" else -1
        cf_orig = continuation(l["exit_ts"], lad["entry_px"], lad["stop_px"],
                               lad["tp2_px"], sign, bars)
        cf_be = continuation(l["exit_ts"], lad["entry_px"], lad["entry_px"],
                             lad["tp2_px"], sign, bars)
        if cf_orig is None or cf_be is None:
            unmeasurable += 1
            continue
        realized = float(l["pnl_pts"] or 0.0)
        rows.append({
            "entry_ts": l["entry_ts"], "exit_ts": l["exit_ts"],
            "direction": l["direction"], "horizon": lad["horizon"],
            "realized_pt": round(realized, 4),
            "cf_orig_pt": round(cf_orig, 4), "imp_orig": round(cf_orig - realized, 4),
            "cf_breakeven_pt": round(cf_be, 4), "imp_breakeven": round(cf_be - realized, 4),
        })

    out = {
        "channel": "early_trail_exit_watch", "since": since,
        "n": len(rows), "n_days": len({r["exit_ts"][:10] for r in rows}),
        "n_unmatched_ladder": unmatched, "n_unmeasurable": unmeasurable,
        "preregistered": {k: cr.get(k) for k in
                          ("min_samples", "min_days", "roundtrip_cost_pt", "primary_arm")},
    }
    if rows:
        for arm in ("orig", "breakeven"):
            key = "imp_%s" % arm
            imps = [r[key] for r in rows]
            by_day = collections.defaultdict(float)
            for r in rows:
                by_day[r["exit_ts"][:10]] += r[key]
            pos_days = sum(1 for v in by_day.values() if v > 0)
            out["arm_%s" % arm] = {
                "sum_pt": round(sum(imps), 2),
                "mean_pt": round(sum(imps) / len(imps), 4),
                "n_improved": sum(1 for v in imps if v > 0),
                "days_improved": "%d/%d" % (pos_days, len(by_day)),
                "sign_test_p": round(_binom_two_sided(pos_days, len(by_day)), 4),
            }
        # 판정 — 사전등록 조건 (모듈 docstring 참조)
        prim = out["arm_%s" % (cr.get("primary_arm") or "orig")]
        if out["n"] < int(cr.get("min_samples", 60)) or out["n_days"] < int(cr.get("min_days", 10)):
            out["verdict"] = "INSUFFICIENT"
            out["reason"] = "표본 부족 (%d건/%d일 < %d건/%d일)" % (
                out["n"], out["n_days"], cr.get("min_samples", 60), cr.get("min_days", 10))
        elif (prim["mean_pt"] > float(cr.get("roundtrip_cost_pt", 0.0716))
              and prim["sign_test_p"] < 0.05):
            out["verdict"] = "FAIL"
            out["reason"] = ("회수 가치 검출 — 트레일 완화 변형 A/B 2차 등록 검토 "
                             "(자동 적용 금지, MW0601 대조 필수)")
        else:
            out["verdict"] = "PASS"
            out["reason"] = "현행 유지 — 개선이 비용·유의 문턱 미달"
    else:
        out["verdict"] = "INSUFFICIENT"
        out["reason"] = "표본 없음"

    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return out

    print("=" * 66)
    print("[49] 조기청산 반사실 — TP1 도달 전 익절성 틱스톱의 '유지했다면'")
    print("=" * 66)
    print("창 %s~ | 모집단 %d건 → 측정 %d건/%d일 (사다리 미매칭 %d · 측정불가 %d)"
          % (since, len(pop), out["n"], out["n_days"], unmatched, unmeasurable))
    for arm, label in (("orig", "주팔 orig (원 손절가 유지)"),
                       ("breakeven", "병기 breakeven (본전 강등)")):
        a = out.get("arm_%s" % arm)
        if not a:
            continue
        print("\n  %s" % label)
        print("    개선 합계 %+8.2fpt | 건당 %+.4fpt | 개선 레그 %d/%d"
              % (a["sum_pt"], a["mean_pt"], a["n_improved"], out["n"]))
        print("    일자단위 개선일 %s | 부호검정 p=%.4f" % (a["days_improved"], a["sign_test_p"]))
    print("\n  판정: %s — %s" % (out["verdict"], out["reason"]))
    print("  (사전등록: n>=%s·%s일, 비용 %spt, 주팔 %s — settings early_trail_exit_watch)"
          % (out["preregistered"]["min_samples"], out["preregistered"]["min_days"],
             out["preregistered"]["roundtrip_cost_pt"], out["preregistered"]["primary_arm"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    evaluate(a.since, a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
