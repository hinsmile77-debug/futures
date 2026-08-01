# scripts/quantile_tp_shadow.py
"""[404차 후속10, 3-B] 분위회귀 기반 TP1 거리 A/B 카운터팩추얼 — 읽기 전용.

무엇을 묻는가
--------------
현행 TP1은 **신호 내용과 무관한** 변동성 고정비율이다.

    TP1 = ATR × ATR_HORIZON_TP1_MULT[hz] × hurst_mult   (1m 0.3 / 3m 0.5 / 5m 0.7)

"지금 이 분봉이 어디까지 갈 것 같은가"는 전혀 반영되지 않는다. 분위회귀 채널
([3], learning/quantile_regressor.py)은 그 답을 이미 매 분봉 계산해 저장하고 있으나
(ensemble_decisions.quantile_q10_pt / quantile_q90_pt) 실거래에는 미연결이다.

감사 §3-3이 정한 승격 형태가 정확히 이것이다 — *"TP 거리 산정 보조(q90 기반 TP
상향/하향)부터 — 사이징 반영은 그 다음."* 이 스크립트는 그 승격안을 실제 분봉으로
재생해 현행과 비교한다.

왜 "q90"이 아니라 "방향 정합 분위"인가
--------------------------------------
`quantile_q90_pt`는 **가격변동(pt)의 상위 90분위**다. LONG의 이익 방향은 상방이므로
q90이 맞지만, SHORT의 이익 방향은 하방이므로 q90이 아니라 |q10|을 써야 한다.
감사 §3-3의 "q90 기반"이 뜻하는 바는 '이익 방향 꼬리까지의 거리'이므로, 방향별로
favorable quantile을 고른다 (LONG → q90, SHORT → |q10|). q90을 SHORT에도 그대로
쓰면 "손실 방향 꼬리"를 TP로 삼는 꼴이라 의미가 없다.

왜 스톱은 전 변형 고정인가
--------------------------
[23-B] tp1_geometry_shadow의 `sym_1.0_1.0`은 TP1 확대와 스톱 축소를 동시에 바꿔
기여 분해가 불가능했다(stop_1.0 단독 +0.53 vs sym +1.38 — 이득의 출처 특정 불가).
이 채널은 **TP1 축만** 바꾸고 스톱은 현행(ATR×1.5×hurst)으로 고정한다.

왜 라이브 코드를 안 건드리는가
------------------------------
필요한 입력이 전부 이미 저장돼 있다 — trades(진입가·방향·호라이즌·hurst·entry_ts),
ensemble_decisions(features의 atr, quantile_q10_pt/quantile_q90_pt), raw_candles(고저가).
진입 경로에 섀도 INSERT를 심을 이유가 없고, 심지 않는 만큼 라이브 회귀 위험이 0이다.
[23-B]·[25]와 동일 설계.

무엇을 결론으로 삼을 수 있나 / 없나
-----------------------------------
- 사전등록 기준은 config/settings.py VALIDATION_CAMPAIGN["quantile_tp_shadow"]에
  **관측 전에** 고정돼 있다. 여기서 기준을 바꾸지 말 것(§9).
- **이 채널의 verdict는 [3] 분위회귀 본채널의 verdict에 절대 반영하지 않는다.**
  [3]의 합격선은 커버리지·불확실성상관 두 개 그대로다(§9-4 사후 변경 금지).
- 313차 원칙: min_days 미달이면 판정하지 않는다.
- FAIL이 떠도 즉시 적용 금지 — drop-max 이상치 분해(372차 원칙)·건별 우세·MW0601
  교차확인 3종을 반드시 함께 읽을 것. [25]가 정확히 이 검사에서 무너졌다.

한계 (반드시 함께 읽을 것)
--------------------------
- **quantile_q90_pt는 2026-07-20부터 적재됐다**(그 이전 0행). 07-16 이전 진입은
  구조적으로 제외되며 초기 표본은 n≈40 수준에서 시작한다.
- 1분봉 고저가 기준이라 봉 내 도달 순서를 알 수 없다. 스톱·TP가 같은 봉에서 모두
  닿으면 보수적으로 STOP을 먼저 적용한다(캠페인 다른 채널과 동일 관례).
- qty=1 포지션의 현행 TP1은 물리적 부분청산이 아니라 보호스톱 전환이다. 여기서는
  비교 가능성을 위해 모든 변형에서 "TP1 도달 = 그 가격에 전량 청산"으로 단순화한다.
  따라서 current의 시뮬 손익은 실제 실현손익과 다르며 **변형 간 상대비교 전용**이다.
- 어느 한 변형이라도 시뮬 불가(캔들 결측 등)한 진입은 **전 변형에서 함께 제외**한다.
  변형별로 표본이 달라지면 delta_vs_current가 의미를 잃기 때문이다([23-B]는 변형별
  개별 skip이라 이론상 unpaired가 될 수 있었다 — 이 채널은 그 구멍을 막았다).
- 슬리피지·수수료는 왕복 1회분만 차감한다(캠페인 공통 가정, [23-B]와 동일 0.10pt).

사용법
------
    python scripts/quantile_tp_shadow.py [--since 2026-07-05] [--horizon 5m]
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 단독 실행 시 콘솔/파이프 인코딩이 cp949로 잡히면 em-dash·⚠에서 UnicodeEncodeError가
# 난다 — tp1_protect_offset_shadow.py·tp1_geometry_shadow.py와 동일 패턴.
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

_TS_FMT = "%Y-%m-%d %H:%M:%S"
_CR = VALIDATION_CAMPAIGN.get("quantile_tp_shadow", {})
_MAX_HOLD_MIN = 45          # 최대 보유 분 — [23-B]와 동일
_COST_PTS = 0.10            # 왕복 비용 가정 (pt) — [23-B]와 동일
_MIN_TP_PTS = 0.05          # 이보다 좁은 TP는 무의미(진입 즉시 체결) — 해당 진입 제외


def _load_candles(since: str):
    hi, lo, cl = {}, {}, {}
    with sqlite3.connect(RAW_DATA_DB) as c:
        for ts, h, l, k in c.execute(
            "SELECT ts, high, low, close FROM raw_candles WHERE ts >= ?", (since,)
        ):
            hi[ts], lo[ts], cl[ts] = h, l, k
    return hi, lo, cl


def _load_signal_map(since: str):
    """진입 분봉의 (atr, q10, q90) — ensemble_decisions 한 번에 읽는다.

    atr은 features JSON 안에 있고(= [23-B] _load_atr_map과 동일 경로), 분위는
    전용 컬럼이다. 둘을 한 쿼리로 묶어 ts 정렬 불일치 가능성을 없앤다.
    """
    out = {}
    with sqlite3.connect(PREDICTIONS_DB) as c:
        c.row_factory = sqlite3.Row
        for r in c.execute(
            """SELECT ts, features, quantile_q10_pt AS q10, quantile_q90_pt AS q90
               FROM ensemble_decisions WHERE ts >= ?""",
            (since,),
        ):
            atr = None
            if r["features"]:
                try:
                    atr = json.loads(r["features"]).get("atr")
                except (ValueError, TypeError):
                    atr = None
            out[r["ts"]] = {
                "atr": float(atr) if atr else None,
                "q10": None if r["q10"] is None else float(r["q10"]),
                "q90": None if r["q90"] is None else float(r["q90"]),
            }
    return out


def _load_trades(since: str, horizon=None):
    """부분청산 레그를 entry_ts 기준으로 병합해 '진입 1건'으로 만든다([23-B]와 동일)."""
    src = _CR.get("entry_source", "SYSTEM_AUTO")
    sql = (
        "SELECT entry_ts, direction, entry_price, entry_horizon, hurst_bucket "
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


def _hurst_mult(hurst_bucket, key):
    m = (HURST_REGIME_ATR_MULT.get(hurst_bucket or "", {})
         if HURST_REGIME_ATR_MULT_ENABLED else {})
    return m.get(key, 1.0)


def _favorable_quantile(is_long, q10, q90):
    """이익 방향 꼬리까지의 거리(pt, 양수). 부호가 반대면 None(= 신호가 그 방향
    여력을 인정하지 않음 → 해당 진입 제외)."""
    if is_long:
        return q90 if (q90 is not None and q90 > 0) else None
    return (-q10) if (q10 is not None and q10 < 0) else None


def _tp1_for(variant, horizon, hurst_bucket, atr, fav):
    """변형별 TP1 거리(pt). 스톱은 전 변형 공통이라 여기서 다루지 않는다."""
    cur = (atr * ATR_HORIZON_TP1_MULT.get(horizon, ATR_TP1_MULT)
           * _hurst_mult(hurst_bucket, "tp1"))
    if variant == "current":
        return cur
    if variant == "q_raw":
        return fav
    if variant == "q_x0.7":
        return fav * 0.7
    if variant == "q_blend":
        return (cur + fav) / 2.0
    raise ValueError("알 수 없는 변형: %s" % variant)


def _simulate(entry_ts, is_long, entry_px, stop_pts, tp1_pts, hi, lo, cl):
    """분봉 고저가로 STOP/TP1 선후 판정. 동시 도달 시 보수적으로 STOP([23-B] 관례)."""
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


def compute(since: str = "2026-07-05", horizon=None) -> dict:
    """계산부 — generate_validation_campaign_report.py가 [3-B] 채널로 import한다.

    Returns: {variants, n_trades, n_days, skip:{...}, cost_pts, rows: {name: [(outcome, pts)]}}
    rows는 **전 변형 동일 길이·동일 순서**(paired)임이 보장된다.
    """
    hi, lo, cl = _load_candles(since)
    sig = _load_signal_map(since)
    trades = _load_trades(since, horizon)
    variants = list(_CR.get("variants", ["current"]))

    res = {name: [] for name in variants}
    days = set()
    skip = {"atr": 0, "quantile": 0, "unfavorable": 0, "tp_too_tight": 0, "sim": 0}

    for t in trades:
        ets = t["entry_ts"]
        s = sig.get(ets[:17] + "00") or sig.get(ets) or {}
        atr = s.get("atr")
        if not atr:
            skip["atr"] += 1
            continue
        if s.get("q10") is None or s.get("q90") is None:
            # 2026-07-20 이전 진입은 여기서 걸린다(컬럼 미적재) — 표본 한계, 결함 아님.
            skip["quantile"] += 1
            continue
        is_long = str(t["direction"]).upper() == "LONG"
        fav = _favorable_quantile(is_long, s["q10"], s["q90"])
        if fav is None:
            skip["unfavorable"] += 1
            continue

        px = float(t["entry_price"])
        stop_pts = atr * ATR_STOP_MULT * _hurst_mult(t["hurst_bucket"], "stop")

        # 전 변형을 먼저 계산해 하나라도 불가하면 이 진입을 통째로 버린다(paired 보장).
        staged, bad = [], False
        for name in variants:
            tp = _tp1_for(name, t["entry_horizon"], t["hurst_bucket"], atr, fav)
            if tp is None or tp < _MIN_TP_PTS:
                skip["tp_too_tight"] += 1
                bad = True
                break
            outcome, pts = _simulate(ets, is_long, px, stop_pts, tp, hi, lo, cl)
            if outcome is None:
                skip["sim"] += 1
                bad = True
                break
            staged.append((name, outcome, pts - _COST_PTS))
        if bad:
            continue

        days.add(ets[:10])
        for name, outcome, net in staged:
            res[name].append((outcome, net))

    return {
        "variants": variants,
        "n_trades": len(res[variants[0]]) if variants else 0,
        "n_candidates": len(trades),
        "n_days": len(days),
        "skip": skip,
        "cost_pts": _COST_PTS,
        "rows": res,
        "since": since,
    }


def summarize(out: dict) -> dict:
    """compute() 결과 → 리포트용 요약 dict.

    판정 기준은 사전등록(VALIDATION_CAMPAIGN['quantile_tp_shadow']) 그대로:
    PASS = 모든 대안이 현행 이하 / FAIL = 현행 초과 대안 존재 / 표본 미달 → INSUFFICIENT.

    delta_drop_max는 372차 원칙(이상치 분해)의 자동화다 — 현행 대비 **가장 크게 기여한
    1건**을 뺐을 때의 델타. 부호가 뒤집히면 그 대안은 단일 거래가 만든 착시다.
    """
    res = out["rows"]
    base = res.get("current", [])
    base_pts = [p for _, p in base]
    base_total = sum(base_pts) if base_pts else None

    per = {}
    for name in out["variants"]:
        rows = res.get(name, [])
        if not rows:
            continue
        pts = [p for _, p in rows]
        d = {
            "n": len(pts),
            "total_pt": round(sum(pts), 4),
            "avg_pt": round(sum(pts) / len(pts), 4),
            "median_pt": round(sorted(pts)[len(pts) // 2], 4),
            "win_rate": round(sum(1 for p in pts if p > 0) / len(pts), 4),
            "max_loss_pt": round(min(pts), 4),
            "n_tp1": sum(1 for o, _ in rows if o == "TP1"),
            "n_stop": sum(1 for o, _ in rows if o == "STOP"),
            "n_timeout": sum(1 for o, _ in rows if o == "TIMEOUT"),
        }
        if base_total is not None and len(pts) == len(base_pts):
            diffs = [p - q for p, q in zip(pts, base_pts)]
            d["delta_vs_current"] = round(sum(diffs), 4)
            d["beats_current_n"] = sum(1 for x in diffs if x > 0)
            # 이상치 분해: 델타에 가장 크게 기여한 1건 제거 (372차 원칙)
            if name != "current" and diffs:
                d["delta_drop_max"] = round(sum(diffs) - max(diffs), 4)
                d["sign_flips_on_drop"] = (
                    (d["delta_vs_current"] > 0) != (d["delta_drop_max"] > 0))
        else:
            d["delta_vs_current"] = None
        per[name] = d

    min_n = int(_CR.get("min_samples", 20))
    min_d = int(_CR.get("min_days", 3))
    n_cur = len(base)
    if n_cur < min_n or out["n_days"] < min_d:
        verdict = "INSUFFICIENT"
        reason = "표본 부족 (n=%d<%d 또는 거래일=%d<%d)" % (
            n_cur, min_n, out["n_days"], min_d)
    else:
        beat = [k for k, v in per.items()
                if k != "current" and (v.get("delta_vs_current") or 0) > 0]
        verdict = "FAIL" if beat else "PASS"
        reason = ("현행 초과 대안: %s" % ", ".join(beat)) if beat else "모든 대안이 현행 이하"
        fragile = [k for k in beat if per[k].get("sign_flips_on_drop")]
        if fragile:
            reason += " (단 %s는 최대기여 1건 제거 시 부호 역전 — 372차)" % ", ".join(fragile)

    return {
        "verdict": verdict, "reason": reason, "per_variant": per,
        "n_trades": out["n_trades"], "n_candidates": out["n_candidates"],
        "n_days": out["n_days"], "skip": out["skip"],
        "min_samples": min_n, "min_days": min_d,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=VALIDATION_CAMPAIGN.get("start_date", "2026-07-05"))
    ap.add_argument("--horizon", default=None)
    args = ap.parse_args()

    out = compute(args.since, args.horizon)
    s = summarize(out)

    print("=" * 96)
    print("분위회귀 기반 TP1 거리 A/B 카운터팩추얼   기간 %s~   호라이즌 %s"
          % (args.since, args.horizon or "전체"))
    print("사전등록 기준: config/settings.py VALIDATION_CAMPAIGN['quantile_tp_shadow']")
    print("스톱은 전 변형 공통(현행 ATR×%.2f×hurst) — TP1 축만 비교" % ATR_STOP_MULT)
    print("=" * 96)
    sk = out["skip"]
    print("진입 후보 %d건 → 시뮬 %d건 / 거래일 %d일   왕복비용 %.2fpt"
          % (out["n_candidates"], out["n_trades"], out["n_days"], out["cost_pts"]))
    print("  제외: atr결측 %d / 분위결측 %d(07-20 이전) / 이익방향분위 부호반대 %d / TP과협 %d / 시뮬불가 %d"
          % (sk["atr"], sk["quantile"], sk["unfavorable"], sk["tp_too_tight"], sk["sim"]))
    print("-" * 96)
    print("%-10s %4s %4s %5s %5s %7s %9s %9s %9s %8s"
          % ("변형", "n", "TP1", "STOP", "만료", "승률", "누적pt", "현행대비", "drop-max", "건별우세"))
    for name in out["variants"]:
        d = s["per_variant"].get(name)
        if not d:
            continue
        dv = d.get("delta_vs_current")
        dm = d.get("delta_drop_max")
        print("%-10s %4d %4d %5d %5d %6.1f%% %+9.2f %9s %9s %8s"
              % (name, d["n"], d["n_tp1"], d["n_stop"], d["n_timeout"],
                 d["win_rate"] * 100, d["total_pt"],
                 "-" if dv is None else "%+.2f" % dv,
                 "-" if dm is None else "%+.2f" % dm,
                 "-" if d.get("beats_current_n") is None
                 else "%d/%d" % (d["beats_current_n"], d["n"])))
    print("-" * 96)
    print("판정: %s - %s" % (s["verdict"], s["reason"]))
    print()
    print("⚠ 이 채널의 판정은 [3] 분위회귀 본채널의 verdict에 반영하지 않는다(§9-4).")
    print("⚠ 절대값은 실현손익이 아니다(qty=1 보호전환을 'TP1 전량청산'으로 단순화).")
    print("  변형 간 상대비교 전용. FAIL이 떠도 drop-max·건별우세·MW0601 교차확인 필수.")


if __name__ == "__main__":
    main()
