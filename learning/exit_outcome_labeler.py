# -*- coding: utf-8 -*-
"""[MW0602 428차 / B-1] 청산 라벨 생성기 — 포지션 × 분 단위.

무엇을 만드는가
---------------
보유 중인 각 분(minute)마다 한 행을 만든다. 질문은 **"지금 끊을까 더 들고 갈까"** 이고,
라벨은 그 답을 사후에 채점한 것이다.

  y_hold_better : 1 = **그 시점에 끊는 것보다 계속 보유한 쪽이 나았다**
                  (최종 청산가가 그 시점 가격보다 방향보정 후 유리)
  y_tp1_first   : 1 = 그 시점 이후 스톱보다 TP1에 먼저 닿았다

왜 `y_hold_better`가 주 라벨인가
--------------------------------
`y_tp1_first`는 실측 도달률이 **19%**(100포지션 중 19)로 심하게 불균형이고,
"TP1 도달"은 청산 정책의 한 갈래일 뿐이다. 반면 `y_hold_better`는

  · **결정과 1:1 대응한다** — 매분 실제로 내리는 선택이 "끊기 vs 들고가기"다.
  · 자연스럽게 균형에 가깝다(실측은 `summary()`가 찍는다).
  · **방향 예측이 필요 없다.** 이미 진입한 포지션의 조건부 문제라, 428차 [40]에서
    방향 축이 무작위와 구분되지 않음(p=0.79)이 확인된 것과 무관하게 성립한다.

왜 이 축이 비어 있었나
----------------------
학습기가 전부 진입 측이다 — GBM/RF 6호라이즌(방향), SGD(방향),
`meta_confidence`(`_quality_label(conf, **correct**)` = 방향 적중),
`meta_labeling`(take/reduce/skip = 방향 적중 + 추종폭). **청산은 전부 규칙이다**
(ATR 고정배수·트레일링 계단·손절계단화). 그런데 425차가 확인한 대로 스톱은
16건 중 14건이 옳았고, 돈은 청산 기하에서 나온다.

⚠ 누출 방지
-----------
피처는 **그 시점까지의 정보만** 쓴다. 라벨은 미래 경로에서 오지만 그것이 지도학습의
정의다. 위험한 것은 피처 쪽이며, 여기서는 `raw_features`의 동시점 값과 포지션
상대상태(경과분·미실현·스톱/TP1까지 거리)만 쓴다.

읽기 전용이다 — DB에 쓰지 않는다. 학습·기록은 `learning/exit_classifier.py`가 한다.
"""
import collections
import datetime
import json
import logging
import os
import sqlite3

logger = logging.getLogger("LEARNING")

_TS = "%Y-%m-%d %H:%M:%S"
_SESSION_LAST = "15:09"
_SYSTEM_AUTO_SQL = (
    "(COALESCE(entry_source,'') = 'SYSTEM_AUTO' "
    " OR (entry_source IS NULL AND COALESCE(grade,'') <> 'MANUAL'))"
)

# 시장 피처는 **소수만** 쓴다. 385행 규모에서 100+ 피처를 넣으면 학습이 아니라
# 암기가 된다(B-2가 표본 하한으로 그것을 막지만, 애초에 넣지 않는 편이 낫다).
# 선정 기준: 청산 판단과 기제가 직결되고 결측이 적은 것.
MARKET_FEATURES = ("atr", "vwap_position", "ofi_norm", "cvd_divergence",
                   "toxicity_score", "spread_ticks", "hurst")

# 포지션 상대 상태 — 방향·가격 수준에 불변인 형태로만 만든다.
STATE_FEATURES = ("held_min", "upnl_atr", "dist_stop_atr", "dist_tp1_atr",
                  "mfe_atr", "mae_atr", "tp1_done")

FEATURE_NAMES = STATE_FEATURES + MARKET_FEATURES


def _conn(path):
    c = sqlite3.connect(path, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def _load_positions(trades_db, since):
    # [MW0601 440차] entry_horizon·hurst_bucket 추가 — 라이브와 같은 TP1/스톱
    # 기하를 쓰기 위해 필요하다(build_labels 주석 참조).
    with _conn(trades_db) as c:
        return [dict(r) for r in c.execute(
            "SELECT entry_ts, MAX(exit_ts) AS exit_ts, MIN(direction) AS direction, "
            "       MIN(entry_price) AS entry_price, "
            "       MIN(entry_horizon) AS entry_horizon, "
            "       MIN(hurst_bucket) AS hurst_bucket, "
            "       SUM(COALESCE(net_pnl_krw, pnl_krw)) AS pnl_krw "
            "  FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND %s "
            " GROUP BY entry_ts ORDER BY entry_ts" % _SYSTEM_AUTO_SQL, (since,))]


def _load_market(pred_db, raw_db, since):
    """분 단위 시장 피처 맵 + 분봉 맵."""
    feats = {}
    with _conn(pred_db) as c:
        for r in c.execute("SELECT ts, features FROM ensemble_decisions WHERE ts >= ?",
                           (since,)):
            try:
                d = json.loads(r["features"]) or {}
            except (ValueError, TypeError):
                continue
            feats[str(r["ts"])[:16]] = d
    bars = collections.defaultdict(list)
    with _conn(raw_db) as c:
        for r in c.execute("SELECT ts, high, low, close FROM raw_candles WHERE ts >= ?",
                           (since,)):
            bars[str(r["ts"])[:10]].append(
                (str(r["ts"]), float(r["high"]), float(r["low"]), float(r["close"])))
    for d in bars:
        bars[d].sort()
    return feats, bars


def _feat_at(feats, ts_min):
    """T → T-1 폴백. 427차 후속 실측대로 결정행이 1분 앞설 수 있다."""
    if ts_min in feats:
        return feats[ts_min]
    try:
        prev = (datetime.datetime.strptime(ts_min + ":00", _TS)
                - datetime.timedelta(minutes=1)).strftime(_TS)[:16]
    except ValueError:
        return None
    return feats.get(prev)


def build_labels(trades_db, pred_db, raw_db, since,
                 atr_stop_mult, atr_tp1_mult):
    """포지션 × 분 라벨 행 목록을 만든다.

    Returns: list of dict — FEATURE_NAMES + y_hold_better / y_tp1_first + 메타

    ⚠ [MW0601 440차 수정] **호라이즌별 TP1 기하를 쓴다.**
    ------------------------------------------------------
    종전에는 호출측이 넘긴 `atr_tp1_mult`(= `ATR_TP1_MULT` = **1.0**, "entry_horizon
    미지정 시 fallback")를 전 포지션에 그대로 썼다. 라이브 TP1은 374/387차부터
    호라이즌별(`1m .3 / 3m .5 / 5m .7`)이고 hurst 레짐 배수까지 곱하므로, 라벨러의
    TP1 거리는 **1.4~3.3배 과대**였다(캠페인 표본 호라이즌 분포: 3m 57 / 5m 49 /
    1m 11건 — 전건이 영향권). 스톱도 hurst 배수가 빠져 있었다.

    그 결과 오염된 것:
        · `dist_tp1_atr` 피처   — TP1까지 거리를 실제보다 멀게 본다
        · `tp1_done` 피처       — 이미 도달했는데 미도달로 읽는다
        · `y_tp1_first` 라벨    — 도달률이 구조적으로 과소
    표본을 더 모아도 **잘못 라벨된 표본이 늘 뿐**이라, [41] 게이지가 요구하는
    267포지션을 기다리기 전에 고쳐야 한다.

    기하는 `scripts/exit_replay.geometry()` 단일 소스에서 가져온다 — 재생기와
    라벨러가 서로 다른 기하를 쓰면 같은 표류가 반복된다(432차 "3중 정의" 교훈).
    호라이즌을 모르는 행은 종전대로 호출측 인자를 쓴다(하위호환).
    """
    try:
        from scripts.exit_replay import geometry as _geom
    except Exception:                                   # 순환/경로 문제 시 종전 동작
        _geom = None
    positions = _load_positions(trades_db, since)
    feats, bars = _load_market(pred_db, raw_db, since)
    rows = []

    for p in positions:
        ets, xts = str(p["entry_ts"]), str(p["exit_ts"])
        day = ets[:10]
        sign = 1 if str(p["direction"]) == "LONG" else -1
        px = float(p["entry_price"] or 0.0)
        f0 = _feat_at(feats, ets[:16])
        atr = float((f0 or {}).get("atr") or 0.0)
        if px <= 0 or atr <= 0:
            continue
        _hz = p.get("entry_horizon") or None
        if _geom is not None and _hz:
            _sp, _tp1p, _, _ = _geom(_hz, p.get("hurst_bucket"), atr)
            stop = px - sign * _sp
            tp1 = px + sign * _tp1p
        else:
            stop = px - sign * atr * atr_stop_mult
            tp1 = px + sign * atr * atr_tp1_mult

        path = [b for b in bars.get(day, ())
                if ets[:16] < b[0][:16] <= xts[:16] and b[0][11:16] <= _SESSION_LAST]
        if not path:
            continue
        exit_px = path[-1][3]          # 최종 청산 시점 분봉 종가(근사)

        mfe = mae = 0.0
        tp1_done = False
        for i, (ts, hi, lo, cl) in enumerate(path):
            # ── 그 시점까지의 정보만으로 상태를 만든다 ──────────────
            mfe = max(mfe, (hi - px) * sign if sign > 0 else (px - lo))
            mae = min(mae, (lo - px) * sign if sign > 0 else (px - hi))
            upnl = (cl - px) * sign
            if not tp1_done:
                tp1_done = (hi >= tp1) if sign > 0 else (lo <= tp1)

            mkt = _feat_at(feats, ts[:16]) or {}
            row = {
                "entry_ts": ets, "ts": ts, "day": day, "direction": sign,
                "held_min": float(i + 1),
                "upnl_atr": upnl / atr,
                "dist_stop_atr": (cl - stop) * sign / atr,
                "dist_tp1_atr": (tp1 - cl) * sign / atr,
                "mfe_atr": mfe / atr,
                "mae_atr": mae / atr,
                "tp1_done": 1.0 if tp1_done else 0.0,
            }
            _ok = True
            for k in MARKET_FEATURES:
                v = mkt.get(k)
                if v is None:
                    _ok = False
                    break
                try:
                    row[k] = float(v)
                except (TypeError, ValueError):
                    _ok = False
                    break
            if not _ok:
                continue

            # ── 라벨 (미래 경로) ────────────────────────────────────
            row["y_hold_better"] = 1 if (exit_px - cl) * sign > 0 else 0
            fut = path[i + 1:]
            y2 = 0
            for _ts, _hi, _lo, _cl in fut:
                hs = (_lo <= stop) if sign > 0 else (_hi >= stop)
                ht = (_hi >= tp1) if sign > 0 else (_lo <= tp1)
                if hs:
                    break
                if ht:
                    y2 = 1
                    break
            row["y_tp1_first"] = y2
            rows.append(row)
    return rows


def summary(rows):
    """표본 규모·균형·상관 구조를 요약한다 — B-2의 학습 가부 판단 재료."""
    out = {"n_rows": len(rows)}
    if not rows:
        return out
    out["n_positions"] = len({r["entry_ts"] for r in rows})
    out["n_days"] = len({r["day"] for r in rows})
    for y in ("y_hold_better", "y_tp1_first"):
        pos = sum(r[y] for r in rows)
        out[y + "_pos"] = int(pos)
        out[y + "_rate"] = round(pos / float(len(rows)), 4)
    # 행이 포지션 안에서 강하게 상관된다 — 유효표본은 행 수가 아니라 포지션 수에
    # 가깝다. 그 사실을 숫자로 남긴다(B-2가 이 값으로 학습을 막는다).
    out["rows_per_position"] = round(len(rows) / float(out["n_positions"]), 2)
    return out
