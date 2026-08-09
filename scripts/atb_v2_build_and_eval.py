# -*- coding: utf-8 -*-
"""[MW0601 454차 / ATB-B2] ATB v2 라벨 생성 + 학습 + 퍼지드 CV 평가 (오프라인 전용).

py310_64에서 수동 실행한다. EOD 체인에 연결하지 않는다 — 판정 개시는
[1] TB 채널 5m 첫 판정 이후(구현계획 문서·VALIDATION_CAMPAIGN["atb_v2"] 주석 참조).

기존 섀도 TB([1] 채널, shadow_triple_barrier/)와의 차이는 정확히 4가지다:
CUSUM 이벤트 필터 / 세션 클립(15:10) + ATR 하한 / min_edge 비용 필터 /
고유성·수익귀속 표본 가중치. 배리어 배수(ATR_STOP_MULT·ATR_HORIZON_TP1_MULT)와
피처 로드 경로는 [1]과 동일하게 유지해 실험 변수를 새 요소로 격리한다.

산출물:
  {HORIZON_DIR}/shadow_atb_v2/gbm_{hz}_atb_v2.pkl (+scaler, feature_names) — protocol=4
  {DATA_DIR}/atb_v2/atb_v2_eval_YYYYMMDD.json / .md  (런타임 산출물 — 커밋 금지)

실행:
  conda activate py310_64
  python scripts/atb_v2_build_and_eval.py --horizons 3m,5m --weeks-back 26
"""
import argparse
import datetime
import json
import os
import pickle
import sqlite3
import sys

import numpy as np

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Windows 콘솔(cp949)에서 특수문자 출력 크래시 방지
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from config.settings import (  # noqa: E402
    RAW_DATA_DB, HORIZON_DIR, DATA_DIR, HORIZONS,
    ATR_STOP_MULT, ATR_HORIZON_TP1_MULT, ATR_TP1_MULT,
    FUTURES_COMMISSION_RATE, TICK_SIZE, VALIDATION_CAMPAIGN,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN  # noqa: E402
from model.atb_labeling import (  # noqa: E402
    build_atb_labels, average_uniqueness, return_attribution_weights,
    combined_sample_weight, purged_event_splits, leakage_selftest_events,
)
from model.multi_horizon_model import apply_robust_preprocess  # noqa: E402
from learning.batch_retrainer import (  # noqa: E402
    _make_sample_weight, _shadow_tb_row_is_live,
)

ATB_DIRNAME = "shadow_atb_v2"
_TS_FMT = "%Y-%m-%d %H:%M:%S"


def _spearman(x, y):
    """numpy 전용 스피어만 — generate_validation_campaign_report._spearman과 동일.

    scipy.spearmanr는 이 환경에서 MKL 지연로드 크래시(0xc06d007f)를 일으킨다 —
    캠페인 리포트가 numpy 전용으로 짠 것과 같은 이유. IC 방법론도 [1]과 정확히
    일치해야 하므로 같은 구현을 쓴다.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if len(x) < 3 or len(x) != len(y):
        return float("nan")
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    sx = rx.std()
    sy = ry.std()
    if sx < 1e-12 or sy < 1e-12:
        return float("nan")
    return float(((rx - rx.mean()) * (ry - ry.mean())).mean() / (sx * sy))


def _roundtrip_cost_pt(avg_price):
    """왕복 비용(pt) — generate_validation_campaign_report._roundtrip_cost_pt와 동일 산식."""
    slip = float(VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))
    return 2.0 * avg_price * FUTURES_COMMISSION_RATE + 2.0 * slip * TICK_SIZE


def _load_rows(conn, hz, cutoff):
    """[1] 채널과 동일한 피처 로드 경로 — raw_features_horizon → raw_features 폴백
    (+418차 백필행 제외)."""
    fallback = False
    rows = conn.execute(
        "SELECT ts, features FROM raw_features_horizon "
        "WHERE horizon=? AND ts>=? ORDER BY ts", (hz, cutoff),
    ).fetchall()
    if not rows:
        rows = conn.execute(
            "SELECT ts, features FROM raw_features WHERE ts>=? ORDER BY ts",
            (cutoff,),
        ).fetchall()
        fallback = True
        n_pre = len(rows)
        rows = [r for r in rows if _shadow_tb_row_is_live(r["features"], json)]
        if len(rows) < n_pre:
            print("  [%s] raw_features 폴백 — 백필행 %d/%d 제외 (418차)"
                  % (hz, n_pre - len(rows), n_pre))
    return rows, fallback


def _parse_features(rows):
    """features JSON 파싱 — 피처명은 키 수가 최대인 행 기준 (섀도 TB와 동일 관례)."""
    feat_names, feat_count = None, 0
    records = []
    for r in rows:
        try:
            fd = json.loads(r["features"])
        except (ValueError, TypeError):
            continue
        if not isinstance(fd, dict):
            continue
        keys = list(fd.keys())
        if feat_names is None or len(keys) >= feat_count:
            feat_count = len(keys)
            feat_names = keys
        records.append((r["ts"], fd))
    return records, feat_names


def run_horizon(conn, hz, h_min, cutoff, cusum_k, model_factory, out_dir):
    print("== %s (h=%d분) ==" % (hz, h_min))
    res = {"horizon": hz}

    candle_rows = conn.execute(
        "SELECT ts, high, low, close FROM raw_candles WHERE ts>=? ORDER BY ts",
        (cutoff,),
    ).fetchall()
    candles = [dict(r) for r in candle_rows]
    if len(candles) < 1000:
        res["error"] = "분봉 부족 (%d)" % len(candles)
        return res

    rows, fallback = _load_rows(conn, hz, cutoff)
    records, feat_names = _parse_features(rows)
    if not records or feat_names is None:
        res["error"] = "피처 없음"
        return res
    feat_by_ts = {ts: fd for ts, fd in records}

    closes = [float(c["close"]) for c in candles]
    avg_price = float(np.mean(closes))
    min_edge = _roundtrip_cost_pt(avg_price)
    tp_mult = float(ATR_HORIZON_TP1_MULT.get(hz, ATR_TP1_MULT))

    built = build_atb_labels(
        candles, h_min, cusum_k=cusum_k,
        stop_mult=float(ATR_STOP_MULT), tp_mult=tp_mult,
        min_edge_pt=min_edge,
    )
    stats = built["stats"]
    # 피처가 있는 이벤트만 학습 대상
    labels = [lb for lb in built["labels"] if lb["ts"] in feat_by_ts]
    res["label_stats"] = stats
    res["min_edge_pt"] = round(min_edge, 4)
    res["tp_mult"] = tp_mult
    res["n_trainable"] = len(labels)
    print("  이벤트율 %.1f%% (%d/%d) | 학습가능 %d | 세션클립 제외 %d | edge 제외 %d"
          % (100 * stats["event_rate"], stats["n_events"], stats["n_bars"],
             len(labels), stats["n_dropped_session"], stats["n_dropped_edge"]))
    if len(labels) < 200:
        res["error"] = "이벤트 표본 부족 (%d < 200) — cusum_k를 낮추거나 기간 확대" % len(labels)
        return res

    n_bars = len(candles)
    uniq = average_uniqueness(n_bars, labels)
    w_ret = return_attribution_weights(closes, labels)
    res["mean_uniqueness"] = round(float(uniq.mean()), 4)
    dist = {}
    for lb in labels:
        dist[int(lb["label"])] = dist.get(int(lb["label"]), 0) + 1
    res["label_dist"] = dist
    print("  평균 고유성 %.3f (전봉 TB 이론치 ≈ %.3f) | 라벨분포 %s"
          % (uniq.mean(), 1.0 / max(h_min, 1), dist))

    # 누출 자가진단 — overlap 0 필수
    selftest = leakage_selftest_events(labels, n_splits=3)
    res["leakage_selftest"] = selftest
    if any(not r["ok"] for r in selftest):
        res["error"] = "퍼지드 스플릿 누출 검출 — 진행 중단"
        return res

    y = np.array([int(lb["label"]) for lb in labels])
    X = np.array(
        [[float(feat_by_ts[lb["ts"]].get(f, 0.0) or 0.0) for f in feat_names]
         for lb in labels], dtype=np.float32)
    X = apply_robust_preprocess(X, list(feat_names))
    w_cls = _make_sample_weight(y, hz)
    w_final = combined_sample_weight(w_cls, uniq, w_ret)

    # ── 퍼지드 CV: 이벤트 acc + 전분(all-minute) IC (이벤트/비이벤트 분리) ──
    from sklearn.preprocessing import StandardScaler
    close_map = {c["ts"]: float(c["close"]) for c in candles}
    ts_sorted = [c["ts"] for c in candles]
    event_ts = set(lb["ts"] for lb in labels)

    cv_accs, ic_all, ic_event, ic_nonevent = [], [], [], []
    for tr_pos, va_pos in purged_event_splits(labels, n_splits=3):
        if len(tr_pos) < 100 or len(va_pos) < 30:
            continue
        y_tr = y[tr_pos]
        if len(np.unique(y_tr)) < 2:
            continue
        sc = StandardScaler()
        X_tr = sc.fit_transform(X[tr_pos])
        model = model_factory()
        model.fit(X_tr, y_tr, sample_weight=w_final[tr_pos])

        # (a) 이벤트 단위 val 정확도 (참고용 — 판정 지표 아님)
        X_va = sc.transform(X[va_pos])
        cv_accs.append(float((model.predict(X_va) == y[va_pos]).mean()))

        # (b) val 봉 구간의 **모든 분**에 대해 IC (매분 추론 분포 검증)
        v_i0 = min(int(labels[p]["i0"]) for p in va_pos)
        v_i1 = max(int(labels[p]["i1"]) for p in va_pos)
        sc_ts, sc_move, sc_flag = [], [], []
        for i in range(v_i0, v_i1 + 1):
            ts = ts_sorted[i]
            fd = feat_by_ts.get(ts)
            if fd is None:
                continue
            fut = (datetime.datetime.strptime(ts, _TS_FMT)
                   + datetime.timedelta(minutes=h_min)).strftime(_TS_FMT)
            c1 = close_map.get(fut)
            if c1 is None:
                continue
            sc_ts.append(ts)
            sc_move.append(c1 - close_map[ts])
            sc_flag.append(ts in event_ts)
        if len(sc_ts) < 30:
            continue
        Xa = np.array(
            [[float(feat_by_ts[t].get(f, 0.0) or 0.0) for f in feat_names]
             for t in sc_ts], dtype=np.float32)
        Xa = sc.transform(apply_robust_preprocess(Xa, list(feat_names)))
        proba = model.predict_proba(Xa)
        cls = list(model.classes_)
        p_up = proba[:, cls.index(DIRECTION_UP)] if DIRECTION_UP in cls else np.zeros(len(sc_ts))
        p_dn = proba[:, cls.index(DIRECTION_DOWN)] if DIRECTION_DOWN in cls else np.zeros(len(sc_ts))
        score = p_up - p_dn
        move = np.array(sc_move)
        flag = np.array(sc_flag)
        ic_all.append(_spearman(score, move))
        if flag.sum() >= 10:
            ic_event.append(_spearman(score[flag], move[flag]))
        if (~flag).sum() >= 10:
            ic_nonevent.append(_spearman(score[~flag], move[~flag]))

    def _m(v):
        v = [x for x in v if np.isfinite(x)]
        return round(float(np.mean(v)), 4) if v else None

    res.update({
        "cv_acc_event": _m(cv_accs),
        "ic_all_minutes": _m(ic_all),
        "ic_event_minutes": _m(ic_event),
        "ic_nonevent_minutes": _m(ic_nonevent),
        "n_folds": len(cv_accs),
    })
    print("  CV acc(이벤트)=%s | IC 전분=%s / 이벤트분=%s / 비이벤트분=%s"
          % (res["cv_acc_event"], res["ic_all_minutes"],
             res["ic_event_minutes"], res["ic_nonevent_minutes"]))

    # ── 최종 모델 학습·저장 (전체 이벤트) ──
    sc = StandardScaler()
    X_all = sc.fit_transform(X)
    final = model_factory()
    final.fit(X_all, y, sample_weight=w_final)
    # 섀도 TB(shadow_triple_barrier)와 같은 위치 규약 — model/horizons/ 아래
    # (gitignore 대상, 런타임 산출물 커밋 금지)
    shadow_dir = os.path.join(HORIZON_DIR, ATB_DIRNAME)
    os.makedirs(shadow_dir, exist_ok=True)
    for name, obj in (
        ("gbm_%s_atb_v2.pkl" % hz, final),
        ("scaler_%s_atb_v2.pkl" % hz, sc),
        ("feature_names_%s_atb_v2.pkl" % hz, list(feat_names)),
    ):
        p = os.path.join(shadow_dir, name)
        with open(p + ".tmp", "wb") as f:
            pickle.dump(obj, f, protocol=4)
        os.replace(p + ".tmp", p)
    res["model_saved"] = os.path.join(ATB_DIRNAME, "gbm_%s_atb_v2.pkl" % hz)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizons", default="3m,5m",
                    help="쉼표 구분 (기본 3m,5m — 357차 실질 승격 검토 대상)")
    ap.add_argument("--weeks-back", type=int, default=26)
    ap.add_argument("--cusum-k", type=float, default=3.0)
    args = ap.parse_args()

    from sklearn.ensemble import HistGradientBoostingClassifier
    from learning.batch_retrainer import HIST_GBM_PARAMS

    def model_factory():
        return HistGradientBoostingClassifier(**HIST_GBM_PARAMS)

    cutoff = (datetime.datetime.now()
              - datetime.timedelta(weeks=args.weeks_back)).strftime(_TS_FMT)
    out_dir = os.path.join(DATA_DIR, "atb_v2")
    os.makedirs(out_dir, exist_ok=True)

    results = {"generated_at": datetime.datetime.now().strftime(_TS_FMT),
               "cusum_k": args.cusum_k, "weeks_back": args.weeks_back,
               "horizons": {}}
    with sqlite3.connect(RAW_DATA_DB, timeout=10) as conn:
        conn.row_factory = sqlite3.Row
        for hz in [h.strip() for h in args.horizons.split(",") if h.strip()]:
            if hz not in HORIZONS:
                print("무시: 알 수 없는 호라이즌 %s" % hz)
                continue
            try:
                results["horizons"][hz] = run_horizon(
                    conn, hz, HORIZONS[hz], cutoff, args.cusum_k,
                    model_factory, out_dir)
            except Exception as e:
                import traceback
                traceback.print_exc()
                results["horizons"][hz] = {"error": str(e)}

    stamp = datetime.date.today().strftime("%Y%m%d")
    jp = os.path.join(out_dir, "atb_v2_eval_%s.json" % stamp)
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n결과 저장: %s" % jp)
    print("(판정 아님 — VALIDATION_CAMPAIGN['atb_v2'] 판정 개시는 [1] 5m 첫 판정 이후)")


if __name__ == "__main__":
    main()
