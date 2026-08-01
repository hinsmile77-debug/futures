# scripts/tp1_geometry_shadow.py
"""[403차 종합 P1-6] TP1/손절 초기 기하 A/B 카운터팩추얼 — 읽기 전용.

무엇을 묻는가
--------------
현행 청산 기하는 손절:TP1 비율이 호라이즌만으로 결정되고 전 레짐에 상시 적용된다.

    stop = ATR × ATR_STOP_MULT(1.5)       × hurst_mult
    TP1  = ATR × ATR_HORIZON_TP1_MULT[hz] × hurst_mult

hurst_mult가 양쪽에 똑같이 곱해져 비율에서 약분되므로 결과는

    1m 5.00:1    3m 3.00:1    5m 2.14:1

이며 trend/neutral/mean-revert 어느 버킷에서도 동일하다. 이 스크립트는 "다른 기하를
썼다면 실현손익이 어땠을까"를 실제 분봉으로 재생해 비교한다.

왜 라이브 코드를 안 건드리는가
------------------------------
필요한 입력이 전부 이미 저장돼 있다 — trades(진입가·방향·호라이즌·hurst·entry_ts),
ensemble_decisions.features(진입 분봉의 atr), raw_candles(고저가). 진입 경로에 섀도
INSERT를 심을 이유가 없고, 심지 않는 만큼 라이브 회귀 위험이 0이다.

무엇을 결론으로 삼을 수 있나 / 없나
-----------------------------------
- 사전등록 기준은 config/settings.py VALIDATION_CAMPAIGN["tp1_geometry_shadow"]에
  **관측 전에** 고정돼 있다. 여기서 기준을 바꾸지 말 것(§9).
- 313차 원칙: min_days 미달이면 판정하지 않는다. 단일일 결과로 기하를 바꾸지 않는다.
- 스톱 축소안은 노이즈 스톱아웃 증가를 동반하므로 승률·최대손실·표준편차를 함께 본다.
- [12] tp1_trail_shadow가 이미 기각한 "TP1 이후 더 느슨한 트레일링"과는 다른 질문이다
  (그건 트레일 폭, 이건 초기 기하).

한계 (반드시 함께 읽을 것)
--------------------------
- 1분봉 고저가 기준이라 봉 내 도달 순서를 알 수 없다. 스톱·TP가 같은 봉에서 모두
  닿으면 보수적으로 STOP을 먼저 적용한다(캠페인 다른 채널과 동일 관례).
- qty=1 포지션의 현행 TP1은 물리적 부분청산이 아니라 보호스톱 전환이다. 여기서는
  비교 가능성을 위해 모든 변형에서 "TP1 도달 = 그 가격에 전량 청산"으로 단순화한다.
  따라서 현행(current)의 시뮬 손익은 실제 실현손익과 다르며, 변형 간 상대비교로만
  읽어야 한다. 절대값을 실적으로 인용하지 말 것.
- 슬리피지·수수료는 왕복 1회분만 차감한다(캠페인 공통 가정).

사용법
------
    python scripts/tp1_geometry_shadow.py [--since 2026-06-01] [--horizon 5m]
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# [404차 후속10] 단독 실행 시 콘솔/파이프 인코딩이 cp949로 잡혀 main()의 em-dash·⚠에서
# UnicodeEncodeError로 죽던 문제 — tp1_protect_offset_shadow.py에 이미 있던 패턴을 맞춘다.
# 리포트 경로(compute()/summarize())는 UTF-8 파일에 쓰므로 원래 영향이 없었고, 이 수정도
# 계산·판정에는 무관하다(콘솔 출력 한정).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import (  # noqa: E402
    TRADES_DB, PREDICTIONS_DB, RAW_DATA_DB,
    ATR_STOP_MULT, ATR_TP1_MULT, ATR_HORIZON_TP1_MULT,
    HURST_REGIME_ATR_MULT, HURST_REGIME_ATR_MULT_ENABLED,
    VALIDATION_CAMPAIGN,
)
from config.constants import MINI_FUTURES_PT_VALUE  # noqa: E402

_TS_FMT = "%Y-%m-%d %H:%M:%S"
_CR = VALIDATION_CAMPAIGN.get("tp1_geometry_shadow", {})
_MAX_HOLD_MIN = 45          # 최대 보유 분 (미도달 시 그 시점 종가로 마감)
_COST_PTS = 0.10            # 왕복 비용 가정 (수수료+슬리피지, pt) — 보수적 근사


def _load_candles(since: str):
    hi, lo, cl = {}, {}, {}
    with sqlite3.connect(RAW_DATA_DB) as c:
        for ts, h, l, k in c.execute(
            "SELECT ts, high, low, close FROM raw_candles WHERE ts >= ?", (since,)
        ):
            hi[ts], lo[ts], cl[ts] = h, l, k
    return hi, lo, cl


def _load_atr_map(since: str):
    """진입 분봉의 atr — ensemble_decisions.features(JSON)에서 뽑는다."""
    out = {}
    with sqlite3.connect(PREDICTIONS_DB) as c:
        for ts, feat in c.execute(
            "SELECT ts, features FROM ensemble_decisions WHERE ts >= ? AND features IS NOT NULL",
            (since,),
        ):
            try:
                v = json.loads(feat).get("atr")
            except (ValueError, TypeError):
                continue
            if v:
                out[ts] = float(v)
    return out


def _load_trades(since: str, horizon=None):
    """부분청산 레그를 entry_ts 기준으로 병합해 '진입 1건'으로 만든다."""
    src = _CR.get("entry_source", "SYSTEM_AUTO")
    sql = (
        "SELECT entry_ts, direction, entry_price, entry_horizon, hurst_bucket, "
        "       SUM(COALESCE(net_pnl_krw, pnl_krw)) AS krw, SUM(quantity) AS qty "
        "FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND entry_source = ? "
    )
    args = [since, src]
    if horizon:
        sql += "AND entry_horizon = ? "
        args.append(horizon)
    sql += "GROUP BY entry_ts, direction, entry_price ORDER BY entry_ts"
    with sqlite3.connect(TRADES_DB) as c:
        c.row_factory = sqlite3.Row
        return [dict(r) for r in c.execute(sql, args)]


def _geometry(horizon, hurst_bucket, atr, stop_override, tp1_override):
    """현행 산식 그대로. override가 주어지면 그 배수로 대체한다."""
    m = (HURST_REGIME_ATR_MULT.get(hurst_bucket or "", {})
         if HURST_REGIME_ATR_MULT_ENABLED else {})
    stop_mult = ATR_STOP_MULT if stop_override is None else stop_override
    tp1_base = ATR_HORIZON_TP1_MULT.get(horizon, ATR_TP1_MULT)
    tp1_mult = tp1_base if tp1_override is None else tp1_override
    return (atr * stop_mult * m.get("stop", 1.0),
            atr * tp1_mult * m.get("tp1", 1.0))


def _simulate(entry_ts, is_long, entry_px, stop_pts, tp1_pts, hi, lo, cl):
    """분봉 고저가로 STOP/TP1 선후 판정. 동시 도달 시 보수적으로 STOP."""
    base = datetime.datetime.strptime(entry_ts, _TS_FMT).replace(second=0)
    stop_px = entry_px - stop_pts if is_long else entry_px + stop_pts
    tp1_px = entry_px + tp1_pts if is_long else entry_px - tp1_pts
    last = None
    for k in range(1, _MAX_HOLD_MIN + 1):
        mid = base + datetime.timedelta(minutes=k)
        if mid.time() > datetime.time(15, 10):
            break
        key = mid.strftime(_TS_FMT)
        h, l = hi.get(key), lo.get(key)
        if h is None:
            continue
        last = cl.get(key, last)
        hit_stop = (l <= stop_px) if is_long else (h >= stop_px)
        hit_tp = (h >= tp1_px) if is_long else (l <= tp1_px)
        if hit_stop:
            return "STOP", (stop_px - entry_px) if is_long else (entry_px - stop_px)
        if hit_tp:
            return "TP1", (tp1_px - entry_px) if is_long else (entry_px - tp1_px)
    if last is None:
        return None, None
    return "TIMEOUT", (last - entry_px) if is_long else (entry_px - last)


def compute(since: str = "2026-06-01", horizon=None) -> dict:
    """[404차 후속3, 23-B] 계산부 — main()의 출력과 분리해 재사용 가능하게 추출.

    generate_validation_campaign_report.py가 이 함수를 import해 `[23]` 채널로
    노출한다(종전에는 이 스크립트를 따로 실행해야만 결과가 보여, 주간회의에서
    사실상 아무도 보지 않는 상태였다). 계산 로직·판정 기준 무변경 — 순수 추출.

    Returns: {variants, n_trades, n_skipped, n_days, cost_pts, rows: {name: [(outcome, pts)]}}
    """
    hi, lo, cl = _load_candles(since)
    atr_map = _load_atr_map(since)
    trades = _load_trades(since, horizon)

    variants = _CR.get("variants", {"current": {"stop_mult": None, "tp1_mult": None}})
    res = {name: [] for name in variants}
    # [MW0601 405차 / P1-4] 행별 entry_ts를 res와 같은 순서로 병렬 보관 — OOS 분리용.
    # res의 튜플 형태를 바꾸면 이 파일의 언팩 지점 8곳과 main() 출력이 전부 영향을
    # 받으므로, 기존 구조는 그대로 두고 평행 리스트만 추가한다(회귀 위험 0).
    res_ts = {name: [] for name in variants}
    days, skipped = set(), 0

    for t in trades:
        ets = t["entry_ts"]
        atr = atr_map.get(ets[:17] + "00") or atr_map.get(ets)
        if not atr:
            skipped += 1
            continue
        is_long = str(t["direction"]).upper() == "LONG"
        px = float(t["entry_price"])
        days.add(ets[:10])
        for name, cfg in variants.items():
            sp, tp = _geometry(t["entry_horizon"], t["hurst_bucket"], atr,
                               cfg.get("stop_mult"), cfg.get("tp1_mult"))
            outcome, pts = _simulate(ets, is_long, px, sp, tp, hi, lo, cl)
            if outcome is None:
                continue
            res[name].append((outcome, pts - _COST_PTS))
            res_ts[name].append(ets)

    return {
        "variants": list(variants),
        "n_trades": len(trades) - skipped,
        "n_skipped": skipped,
        "n_days": len(days),
        "cost_pts": _COST_PTS,
        "rows": res,
        "rows_ts": res_ts,
        "since": since,
    }


def summarize(out: dict) -> dict:
    """[404차 후속3, 23-B] compute() 결과 → 리포트용 요약 dict.

    판정 기준은 사전등록(VALIDATION_CAMPAIGN['tp1_geometry_shadow']) 그대로:
    PASS = 모든 대안이 현행 이하 / FAIL = 현행 초과 대안 존재.
    표본 미달이면 INSUFFICIENT (313차 원칙).
    """
    res = out["rows"]
    base = res.get("current", [])
    base_total = sum(p for _, p in base) if base else None
    per = {}
    for name in out["variants"]:
        rows = res.get(name, [])
        if not rows:
            continue
        pts = [p for _, p in rows]
        per[name] = {
            "n": len(pts),
            "total_pt": round(sum(pts), 4),
            "avg_pt": round(sum(pts) / len(pts), 4),
            "win_rate": round(sum(1 for p in pts if p > 0) / len(pts), 4),
            "max_loss_pt": round(min(pts), 4),
            "n_tp1": sum(1 for o, _ in rows if o == "TP1"),
            "n_stop": sum(1 for o, _ in rows if o == "STOP"),
            "n_timeout": sum(1 for o, _ in rows if o == "TIMEOUT"),
            "delta_vs_current": (round(sum(pts) - base_total, 4)
                                 if base_total is not None else None),
        }
    min_n = int(_CR.get("min_samples", 20))
    min_d = int(_CR.get("min_days", 3))
    n_cur = len(base)
    if n_cur < min_n or out["n_days"] < min_d:
        verdict = "INSUFFICIENT"
        reason = "표본 부족 (n=%d<%d 또는 거래일=%d<%d)" % (
            n_cur, min_n, out["n_days"], min_d)
    else:
        beat = [k for k, v in per.items()
                if k != "current" and (v["delta_vs_current"] or 0) > 0]
        verdict = "FAIL" if beat else "PASS"
        reason = ("현행 초과 대안: %s" % ", ".join(beat)) if beat else "모든 대안이 현행 이하"
    # [MW0601 405차 / P1-4] OOS 부분집계 — **판정 미반영, 표시 전용**.
    #
    # 왜 필요한가: 이 채널의 대안(특히 tp1_x2)이 현행을 크게 앞선다는 결과는
    # **가설을 세운 그 기간의 in-sample**이다(403차 P1-6이 55건/11일로 처음 실행).
    # 403차가 이미 두 한계를 명시했다 — (a) in-sample (b) qty=1 TP1 보호전환을
    # "TP1 전량청산"으로 단순화한 시뮬이라 current의 절대값이 실현손익과 다르다.
    # 게다가 [23-B]는 PC간 부호가 뒤집혔다(MW0601 +32.78 vs MW0602 -19.04) —
    # 404차 후속11이 "FAIL이지만 미적용"으로 확정한 이유다.
    # 그래서 가설 수립 이후(oos_start) 신규 발생분만 따로 세어, 같은 방향이 유지되는지를
    # 별도로 누적 관찰한다. **누적 verdict는 종전 기준 그대로 계산된다** —
    # 합격선을 바꾸면 §9-4 검증 시계가 리셋되므로 여기서는 숫자만 병기한다.
    oos_start = str(_CR.get("oos_start", "")) or None
    if oos_start:
        ts_map = out.get("rows_ts") or {}
        oos = {}
        for name in out["variants"]:
            rows = res.get(name, [])
            tss = ts_map.get(name, [])
            if not rows or len(tss) != len(rows):
                continue
            pts = [p for (_, p), t in zip(rows, tss) if t >= oos_start]
            if pts:
                oos[name] = {
                    "n": len(pts),
                    "total_pt": round(sum(pts), 4),
                    "avg_pt": round(sum(pts) / len(pts), 4),
                    "win_rate": round(sum(1 for p in pts if p > 0) / len(pts), 4),
                }
        if oos:
            _ob = oos.get("current", {}).get("total_pt")
            for name, v in oos.items():
                v["delta_vs_current"] = (round(v["total_pt"] - _ob, 4)
                                         if _ob is not None else None)
            out_oos = {
                "oos_start": oos_start,
                "per_variant": oos,
                "n_days": len({t for tss in ts_map.values() for t in tss
                               if t >= oos_start}),
                "note": ("가설 수립(%s) 이후 신규 발생분만 — **판정 미반영, 표시 전용**. "
                         "누적 verdict는 in-sample 포함 종전 기준 그대로다(§9-4)." % oos_start),
            }
        else:
            out_oos = {"oos_start": oos_start, "per_variant": {},
                       "note": "OOS 구간 표본 없음 (%s 이후 진입 0건)" % oos_start}
    else:
        out_oos = None

    return {
        "verdict": verdict, "reason": reason, "per_variant": per,
        "n_trades": out["n_trades"], "n_days": out["n_days"],
        "n_skipped": out["n_skipped"], "min_samples": min_n, "min_days": min_d,
        "oos": out_oos,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-06-01")
    ap.add_argument("--horizon", default=None)
    args = ap.parse_args()

    out = compute(args.since, args.horizon)
    res, variants = out["rows"], out["variants"]
    days, skipped, trades = out["n_days"], out["n_skipped"], out["n_trades"]

    print("=" * 90)
    print("TP1/손절 초기 기하 A/B 카운터팩추얼   기간 %s~   호라이즌 %s"
          % (args.since, args.horizon or "전체"))
    print("사전등록 기준: config/settings.py VALIDATION_CAMPAIGN['tp1_geometry_shadow']")
    print("=" * 90)
    print("진입 %d건 (atr 결측으로 제외 %d건) / 거래일 %d일   왕복비용 가정 %.2fpt"
          % (trades, skipped, days, _COST_PTS))
    print()
    print("%-14s %5s %7s %7s %7s %9s %9s %9s %9s"
          % ("변형", "n", "TP1", "STOP", "만료", "승률", "누적pt", "평균pt", "최대손실"))
    base_total = None
    for name in variants:
        rows = res[name]
        if not rows:
            print("%-14s (표본 없음)" % name)
            continue
        pts = [p for _, p in rows]
        total = sum(pts)
        if name == "current":
            base_total = total
        n_tp = sum(1 for o, _ in rows if o == "TP1")
        n_st = sum(1 for o, _ in rows if o == "STOP")
        n_to = sum(1 for o, _ in rows if o == "TIMEOUT")
        wr = 100.0 * sum(1 for p in pts if p > 0) / len(pts)
        print("%-14s %5d %7d %7d %7d %8.1f%% %+9.2f %+9.3f %+9.2f"
              % (name, len(pts), n_tp, n_st, n_to, wr, total,
                 total / len(pts), min(pts)))

    print()
    if base_total is not None:
        print("현행 대비 차이 (pt / 1계약 환산 원):")
        for name in variants:
            if name == "current" or not res[name]:
                continue
            d = sum(p for _, p in res[name]) - base_total
            print("  %-14s %+8.2f pt   %+12s 원"
                  % (name, d, format(int(d * MINI_FUTURES_PT_VALUE), ",")))

    print()
    n_cur = len(res.get("current", []))
    min_n = int(_CR.get("min_samples", 20))
    min_d = int(_CR.get("min_days", 3))
    if n_cur < min_n or days < min_d:
        print("판정: INSUFFICIENT — n=%d(<%d) 또는 거래일=%d(<%d). "
              "313차 원칙상 결론 내지 않는다." % (n_cur, min_n, days, min_d))
    else:
        print("판정 근거는 위 표의 '누적pt'다. 사전등록 기준(PASS=현행 이하 / "
              "FAIL=현행 초과)에 따라 주간회의에서 수동 결정할 것 — 이 스크립트는 "
              "판정을 자동 적용하지 않는다(§9).")
    print()
    print("⚠ current의 절대값은 실제 실현손익이 아니다 — qty=1의 TP1 보호전환을 "
          "'TP1 전량청산'으로 단순화했기 때문. 변형 간 상대비교로만 읽을 것.")


if __name__ == "__main__":
    main()
