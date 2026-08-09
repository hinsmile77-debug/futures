# model/atb_labeling.py — 적응형 트리플 배리어 (ATB v2, 병행 트랙 전용)
"""
[MW0601 454차 / ATB-B1] 적응형 트리플 배리어 라벨링 — Lopez de Prado (2018) ch.2~4.

기존 섀도 TB(`model/target_builder.py:build_triple_barrier_label`, 검증캠페인 [1] 채널)와
**완전히 분리된 병행 트랙**이다. [1] 채널은 5m 첫 판정(OOS 누적 중)을 보호하기 위해
일절 건드리지 않는다 — 이 모듈의 산출물은 `{MODEL_DIR}/shadow_atb_v2/`에만 저장되고
판정 개시는 [1] 5m 첫 판정 이후로 게이트된다(`VALIDATION_CAMPAIGN["atb_v2"]` 주석 참조).

기존 TB 대비 추가되는 것 (스펙: docs/Spec for feature/ML Model Labeling/):
  ① CUSUM 이벤트 필터    — 아무 일도 없는 구간의 라벨(순수 노이즈) 제거.
                            부수효과: 라벨 구간 중복(고유성 문제) 자체가 줄어든다.
  ② ATR 하한 클리핑      — 점심 횡보에서 배리어가 무한히 좁아지는 것 방지.
  ③ 세션 클립(15:10)     — 수직 배리어가 당일 강제청산(절대원칙 §1)을 넘지 않는다.
                            기존 TB는 14:40 이후 30m 라벨이 실행 불가능한 거래를
                            정답으로 가르치는 갭이 있었다.
  ④ min_edge 비용 필터   — 익절폭 < 왕복비용인 이벤트는 애초에 먹을 게 없으므로 폐기.
  ⑤ 고유성·수익귀속 가중치 — 겹친 라벨의 표본 수 부풀림 억제 + 손익비를 배점으로 반영.
  ⑥ 시간 기반 퍼지드 스플릿 — CUSUM 이벤트는 비등간격이라 행수 절단 퍼징이 성립하지
                            않으므로 [i0, i1] 실터치 구간 겹침 기반으로 퍼징한다.

동일하게 유지되는 것: 동시터치 손절 우선(conservative), 시간 배리어 → FLAT,
ATR×배수 배리어 폭(실제 청산 배수와 정렬).

py37_32 호환 문법으로 작성(런타임 import 가능성 대비). 실행은 py310_64 오프라인
스크립트(`scripts/atb_v2_build_and_eval.py`) 전용이다.
"""
import datetime
import math
from typing import Dict, List, Optional, Tuple

import numpy as np

from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT

TOUCH_UPPER = "upper"
TOUCH_LOWER = "lower"
TOUCH_TIME = "time"

_TS_FMT = "%Y-%m-%d %H:%M:%S"

# 절대원칙 §1 — 15:10 강제 청산. 수직 배리어는 이 시각을 절대 넘지 않는다.
FORCE_EXIT_HHMM = (15, 10)


def _parse_ts(ts):
    return datetime.datetime.strptime(ts, _TS_FMT)


def _minute_ts(ts, offset):
    return (_parse_ts(ts) + datetime.timedelta(minutes=offset)).strftime(_TS_FMT)


# ---------------------------------------------------------------------------
# ② ATR 하한 클리핑
# ---------------------------------------------------------------------------

def floor_clip_atr(atr_list, floor_quantile=0.20, window=500):
    """ATR 시계열에 롤링 분위 하한을 건다 (스펙 STEP 1의 floor clipping).

    σ→0 횡보 구간에서 배리어가 노이즈만 잡는 것을 막는다. 워밍업 구간
    (window 미만)은 지금까지의 분위값을 쓴다.
    """
    arr = np.asarray(atr_list, dtype=float)
    out = arr.copy()
    for i in range(len(arr)):
        lo = max(0, i - window + 1)
        seg = arr[lo:i + 1]
        seg = seg[np.isfinite(seg) & (seg > 0)]
        if len(seg) >= 5:
            floor = float(np.quantile(seg, floor_quantile))
            if np.isfinite(out[i]) and out[i] < floor:
                out[i] = floor
    return out


# ---------------------------------------------------------------------------
# ① CUSUM 이벤트 필터
# ---------------------------------------------------------------------------

def cusum_events(closes, thresholds):
    """누적 로그수익률 편차가 임계치를 넘는 시점(위치 인덱스)만 반환.

    thresholds: 각 시점의 임계치 배열 (보통 k × ATR%, 변동성 적응형).
    스펙 STEP 2 이식 — 임계 도달 시 누적치 리셋.
    """
    c = np.asarray(closes, dtype=float)
    log_p = np.log(c)
    diff = np.diff(log_p, prepend=log_p[0])
    thr = np.asarray(thresholds, dtype=float)

    s_pos = 0.0
    s_neg = 0.0
    events = []
    for i in range(1, len(c)):
        h = thr[i]
        if not np.isfinite(h) or h <= 0:
            continue
        d = diff[i]
        if not np.isfinite(d):
            continue
        s_pos = max(0.0, s_pos + d)
        s_neg = min(0.0, s_neg + d)
        if s_pos > h:
            s_pos = 0.0
            events.append(i)
        elif s_neg < -h:
            s_neg = 0.0
            events.append(i)
    return events


# ---------------------------------------------------------------------------
# ③ 세션 클립 — 수직 배리어가 15:10을 넘지 않는다
# ---------------------------------------------------------------------------

def effective_horizon_minutes(ts, h_min):
    """당일 15:10(강제청산)까지 남은 분과 h_min 중 작은 쪽.

    반환 0 이하 = 라벨 불가(강제청산 이후 진입 가정이 되므로 폐기).
    """
    dt = _parse_ts(ts)
    force = dt.replace(hour=FORCE_EXIT_HHMM[0], minute=FORCE_EXIT_HHMM[1],
                       second=0, microsecond=0)
    remain = int((force - dt).total_seconds() // 60)
    return min(int(h_min), remain)


# ---------------------------------------------------------------------------
# 라벨 생성 본체 (④ min_edge + conservative 경로 스캔 포함)
# ---------------------------------------------------------------------------

def build_atb_labels(
    candles,            # type: List[dict]  # [{"ts","high","low","close"}, ...] 시간순
    h_min,              # type: int
    cusum_k=3.0,        # type: float
    stop_mult=1.5,      # type: float
    tp_mult=3.0,        # type: float
    min_edge_pt=0.0,    # type: float
    atr_period=14,      # type: int
    atr_floor_quantile=0.20,  # type: float
):
    # type: (...) -> Dict
    """ATB 라벨 일괄 생성 (스펙 STEP 1~5 통합).

    Returns:
        {"labels": [{"ts","i0","i1","label","touch_type","touch_minute",
                     "t1_ts","realized_ret_pt","atr_at_t"}, ...],
         "stats": {"n_bars", "n_events", "event_rate",
                   "n_dropped_session", "n_dropped_edge", "n_dropped_data"}}

    라벨 규칙 (기존 섀도 TB와 동일 축):
      상단(TP=ATR×tp_mult) 선터치 → UP / 하단(SL=ATR×stop_mult) 선터치 → DOWN
      동시터치 → 보수적으로 DOWN(손절 우선) / 시간 배리어 → FLAT
    """
    from features.technical.atr import ATRCalculator

    n = len(candles)
    closes = [float(c["close"]) for c in candles]

    calc = ATRCalculator(period=atr_period)
    atr_raw = []
    for c in candles:
        r = calc.update(float(c["high"]), float(c["low"]), float(c["close"]))
        atr_raw.append(float(r.get("atr") or 0.0))
    atr = floor_clip_atr(atr_raw, floor_quantile=atr_floor_quantile)

    # CUSUM 임계 = k × ATR% (변동성 적응형)
    atr_pct = np.where(np.asarray(closes) > 0,
                       np.asarray(atr) / np.asarray(closes), np.nan)
    events = cusum_events(closes, cusum_k * atr_pct)

    bar_pos = {c["ts"]: i for i, c in enumerate(candles)}
    bar_map = {c["ts"]: c for c in candles}

    labels = []
    n_drop_session = 0
    n_drop_edge = 0
    n_drop_data = 0

    for i0 in events:
        c0_bar = candles[i0]
        ts = c0_bar["ts"]
        c0 = float(c0_bar["close"])
        a = float(atr[i0])
        if not (c0 > 0 and a > 0):
            n_drop_data += 1
            continue

        # ③ 세션 클립
        h_eff = effective_horizon_minutes(ts, h_min)
        if h_eff < 1:
            n_drop_session += 1
            continue

        # ④ min_edge — 익절폭(pt)이 왕복비용(pt)에 못 미치면 폐기
        if min_edge_pt > 0 and tp_mult * a < min_edge_pt:
            n_drop_edge += 1
            continue

        upper = c0 + tp_mult * a
        lower = c0 - stop_mult * a

        label = None
        for m in range(1, h_eff + 1):
            mid_ts = _minute_ts(ts, m)
            bar = bar_map.get(mid_ts)
            if bar is None:
                continue
            hi = bar.get("high")
            lo = bar.get("low")
            if hi is None or lo is None:
                continue
            touched_up = float(hi) >= upper
            touched_dn = float(lo) <= lower
            if touched_dn and touched_up:
                # 동시터치 — 봉 내부 순서 불명 → 보수적으로 손절 우선
                label = {"label": DIRECTION_DOWN, "touch_type": TOUCH_LOWER,
                         "touch_minute": m, "t1_ts": mid_ts,
                         "realized_ret_pt": lower - c0}
                break
            if touched_up:
                label = {"label": DIRECTION_UP, "touch_type": TOUCH_UPPER,
                         "touch_minute": m, "t1_ts": mid_ts,
                         "realized_ret_pt": upper - c0}
                break
            if touched_dn:
                label = {"label": DIRECTION_DOWN, "touch_type": TOUCH_LOWER,
                         "touch_minute": m, "t1_ts": mid_ts,
                         "realized_ret_pt": lower - c0}
                break

        if label is None:
            # 시간 배리어 — 세션 클립된 h_eff 끝의 실측 종가로 FLAT 판정
            end_ts = None
            for m in range(h_eff, 0, -1):
                cand = _minute_ts(ts, m)
                if cand in bar_map:
                    end_ts = cand
                    break
            if end_ts is None:
                n_drop_data += 1
                continue
            label = {"label": DIRECTION_FLAT, "touch_type": TOUCH_TIME,
                     "touch_minute": h_eff, "t1_ts": end_ts,
                     "realized_ret_pt": float(bar_map[end_ts]["close"]) - c0}

        label["ts"] = ts
        label["i0"] = i0
        label["i1"] = bar_pos.get(label["t1_ts"], i0)
        label["atr_at_t"] = a
        labels.append(label)

    return {
        "labels": labels,
        "stats": {
            "n_bars": n,
            "n_events": len(events),
            "event_rate": (len(events) / float(n)) if n else 0.0,
            "n_dropped_session": n_drop_session,
            "n_dropped_edge": n_drop_edge,
            "n_dropped_data": n_drop_data,
        },
    }


# ---------------------------------------------------------------------------
# ⑤ 고유성·수익귀속 표본 가중치 (스펙 STEP 6)
# ---------------------------------------------------------------------------

def concurrency_counts(n_bars, labels):
    """각 봉 위치에서 동시에 살아 있는 라벨 수 c_t (스펙 num_concurrent_events)."""
    delta = np.zeros(n_bars + 1)
    for lb in labels:
        i0, i1 = int(lb["i0"]), int(lb["i1"])
        delta[i0] += 1
        delta[min(i1, n_bars - 1) + 1] -= 1
    return np.cumsum(delta[:-1])


def average_uniqueness(n_bars, labels):
    """라벨별 평균 고유성 ∈ (0,1]. 1=완전 독립. 평균 0.3 미만이면 라벨 설계 회귀."""
    conc = concurrency_counts(n_bars, labels)
    inv = np.where(conc > 0, 1.0 / np.maximum(conc, 1e-12), 0.0)
    cum = np.concatenate([[0.0], np.cumsum(inv)])
    out = np.zeros(len(labels))
    for k, lb in enumerate(labels):
        i0, i1 = int(lb["i0"]), min(int(lb["i1"]), n_bars - 1)
        span = float(i1 - i0 + 1)
        out[k] = (cum[i1 + 1] - cum[i0]) / span if span > 0 else 0.0
    return out


def return_attribution_weights(closes, labels):
    """수익 귀속 가중치 w_i = |Σ_{t∈[i0,i1]} r_t / c_t| (평균 1 정규화).

    분자 r_t → 크게 움직인 구간의 표본이 큰 배점 (손익비 반영)
    분모 c_t → 겹친 라벨끼리 수익을 나눠 가짐 (중복 억제)
    """
    c = np.asarray(closes, dtype=float)
    n = len(c)
    r = np.diff(np.log(c), prepend=np.log(c[0]) if n else 0.0)
    r = np.nan_to_num(r)
    conc = concurrency_counts(n, labels)
    contrib = np.where(conc > 0, r / np.maximum(conc, 1e-12), 0.0)
    cum = np.concatenate([[0.0], np.cumsum(contrib)])
    w = np.zeros(len(labels))
    for k, lb in enumerate(labels):
        i0, i1 = int(lb["i0"]), min(int(lb["i1"]), n - 1)
        w[k] = abs(cum[i1 + 1] - cum[i0])
    total = w.sum()
    if total > 0:
        w = w * (len(w) / total)
    else:
        w = np.ones(len(w))
    return w


def combined_sample_weight(class_weight, uniq_weight, ret_weight):
    """최종 가중치 = 클래스 역빈도 × 수익귀속 (평균 1 정규화).

    고유성은 ret_weight의 분모(c_t)에 이미 반영돼 있으므로 이중 적용하지 않는다 —
    uniq_weight 인자는 진단용으로 받아 두되 곱하지 않는다(스펙 make_sample_weights와
    동일한 구성: w_return이 uniqueness를 내포).
    """
    w = np.asarray(class_weight, dtype=float) * np.asarray(ret_weight, dtype=float)
    m = w.mean()
    return w / m if m > 0 else np.ones(len(w))


# ---------------------------------------------------------------------------
# ⑥ 시간(구간) 기반 퍼지드 스플릿 — 비등간격 이벤트용
# ---------------------------------------------------------------------------

def purged_event_splits(labels, n_splits=3, embargo_bars=0):
    """이벤트 리스트를 시간 연속 블록 n_splits개로 나눠 (train, val) 쌍을 생성.

    val 블록의 봉 구간 [V0, V1]과 [i0, i1]이 겹치는 train 이벤트를 제거(퍼징)하고,
    val 종료 후 embargo_bars 이내에 시작하는 이벤트도 배제(엠바고).
    스펙 purged_kfold_splits의 위치 기반 이식 — 이벤트가 비등간격(CUSUM)이라
    행수 절단이 아니라 구간 겹침으로 판정해야 한다.

    Yields: (train_positions, val_positions) — labels 리스트 내 위치 배열.
    """
    m = len(labels)
    if m < n_splits:
        return
    i0s = np.array([int(lb["i0"]) for lb in labels])
    i1s = np.array([int(lb["i1"]) for lb in labels])
    blocks = np.array_split(np.arange(m), n_splits)
    for blk in blocks:
        if len(blk) == 0:
            continue
        v0 = int(i0s[blk].min())
        v1 = int(i1s[blk].max())
        keep = []
        for j in range(m):
            if j in set(blk.tolist()):
                continue
            # 퍼징: 라벨 구간 겹침
            if i1s[j] >= v0 and i0s[j] <= v1:
                continue
            # 엠바고: val 종료 직후 시작하는 이벤트 배제
            if embargo_bars > 0 and v1 < i0s[j] <= v1 + embargo_bars:
                continue
            keep.append(j)
        yield np.array(keep, dtype=int), blk


def leakage_selftest_events(labels, n_splits=3, embargo_bars=0):
    """퍼지드 스플릿이 실제로 겹침 0인지 확인 (스펙 leakage_selftest 이식).

    Returns: [{"fold", "n_train", "n_val", "overlap_count", "ok"}, ...]
    """
    i0s = np.array([int(lb["i0"]) for lb in labels])
    i1s = np.array([int(lb["i1"]) for lb in labels])
    rows = []
    for k, (tr, blk) in enumerate(
            purged_event_splits(labels, n_splits, embargo_bars)):
        v0 = int(i0s[blk].min())
        v1 = int(i1s[blk].max())
        overlap = int(np.sum((i1s[tr] >= v0) & (i0s[tr] <= v1))) if len(tr) else 0
        rows.append({"fold": k, "n_train": int(len(tr)), "n_val": int(len(blk)),
                     "overlap_count": overlap, "ok": overlap == 0})
    return rows
