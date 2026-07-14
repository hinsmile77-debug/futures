# scripts/generate_validation_campaign_report.py
"""
[260705 검증 캠페인] 섀도우 채널 주간 판정 리포트.

docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md §3의 사전 등록 합격선
(config.settings.VALIDATION_CAMPAIGN — 변경 금지)에 대해 5개 채널의 KPI를
계산하고 PASS / FAIL / INSUFFICIENT를 판정한다.

  [1] Triple-Barrier: 섀도우 TB 모델 OOS 재생(replay) IC vs 프로덕션 3클래스 IC
  [2] Meta-Gate:      entry_quality_prob 3분위별 실현 순EV 분리도
  [3] 분위 회귀:       [q10,q90] 커버리지 + 불확실성-실현폭 상관
  [4] 신호소멸청산:    counterfactual 판정(resolve) + "아낀 pt − 놓친 pt" 누적
  [5] 레짐 ATR 배수:   hurst_bucket별 실거래 순EV

읽기 전용 진단 + signal_decay_exits.resolved 갱신만 수행 — 어떤 정책도
자동으로 켜거나 끄지 않는다. 판정 결과는 권고이며 적용은 수동(주간 회의)이다.

실행 (py310_64 — EOD 체인 scripts/eod_retrain.py가 금요일마다 자동 호출):
    python scripts/generate_validation_campaign_report.py [--days 28]

출력: 콘솔 + data/validation_campaign_report.md + data/validation_campaign_metrics.json
(둘 다 gitignore 대상 PC별 산출물 — 재생성 가능)
"""
import argparse
import datetime
import json
import os
import pickle
import sqlite3
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import (
    PREDICTIONS_DB, TRADES_DB, RAW_DATA_DB, DATA_DIR, MODEL_DIR,
    HORIZONS, VALIDATION_CAMPAIGN, FUTURES_COMMISSION_RATE, TICK_SIZE,
    ENTRY_STARVATION_WEEKLY_MIN, ENTRY_STARVATION_MITIGATION_LADDER,
    HURST_RANGE_THRESHOLD,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN

SHADOW_TB_DIR = os.path.join(MODEL_DIR, "horizons", "shadow_triple_barrier")
_TS_FMT = "%Y-%m-%d %H:%M:%S"

# 호라이즌당 replay 상한 — 모델 mtime이 오래됐을 때 메모리/시간 폭주 방지
_MAX_REPLAY_ROWS = 12000

# 유령 진입(pending 미등록 상태로 들어온 외부체결) 제외 — baseline_ensemble_report.py와
# 동일 컨벤션. 미제외 시 [0]/[5]/[6]/[7]의 표본·EV·승률 집계가 오염된다(NEXT_TODO.md
# 2026-07-12 P0 항목 참조).
_NOT_GHOST_SQL = "COALESCE(entry_source,'') != 'GHOST_PENDING_MISS'"


# ──────────────────────────────────────────────────────────────
# 공통 유틸
# ──────────────────────────────────────────────────────────────

def _spearman(x, y) -> float:
    """numpy 전용 스피어만 상관 (scipy 의존 회피)."""
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


def _conn(db_path):
    conn = sqlite3.connect(db_path, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn


def _roundtrip_cost_pt(avg_price: float) -> float:
    """왕복 비용(pt) = 수수료 2×price×rate + 슬리피지 2×틱 (캠페인 공통 가정)."""
    slip = float(VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))
    return 2.0 * avg_price * FUTURES_COMMISSION_RATE + 2.0 * slip * TICK_SIZE


def _campaign_start() -> str:
    return VALIDATION_CAMPAIGN.get("start_date", "2026-07-05") + " 00:00:00"


def _load_candle_maps(cutoff_ts: str):
    with _conn(RAW_DATA_DB) as conn:
        rows = conn.execute(
            "SELECT ts, high, low, close FROM raw_candles WHERE ts >= ? ORDER BY ts",
            (cutoff_ts,),
        ).fetchall()
    close_map = {r["ts"]: float(r["close"]) for r in rows}
    high_map = {r["ts"]: float(r["high"]) for r in rows}
    low_map = {r["ts"]: float(r["low"]) for r in rows}
    return close_map, high_map, low_map


def _ts_plus_min(ts: str, minutes: int) -> str:
    return (
        datetime.datetime.strptime(ts, _TS_FMT) + datetime.timedelta(minutes=minutes)
    ).strftime(_TS_FMT)


# ──────────────────────────────────────────────────────────────
# [0] 캠페인 표본 기아 조기경보 + 완화 사다리 (§3-8, P1-7, 297차)
# ──────────────────────────────────────────────────────────────

def eval_sample_starvation() -> dict:
    """주간 진입 체결 건수를 §3-8 사전등록 하한과 비교하고, 완화 사다리의
    현재 단계를 판단한다. 자동으로 아무것도 변경하지 않는다 — 사다리 적용은
    항상 사용자 수동 결정 + DECISION_LOG 기록."""
    out = {"verdict": "OK", "floor": ENTRY_STARVATION_WEEKLY_MIN}
    try:
        with _conn(TRADES_DB) as conn:
            cutoff = (
                datetime.datetime.now() - datetime.timedelta(days=7)
            ).strftime(_TS_FMT)
            n_weekly = conn.execute(
                "SELECT COUNT(*) AS n FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ?"
                " AND " + _NOT_GHOST_SQL,
                (cutoff,),
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n_weekly = int(n_weekly or 0)
    starved = n_weekly < ENTRY_STARVATION_WEEKLY_MIN
    projected_28d = n_weekly * 4
    out.update({
        "n_weekly_entries": n_weekly,
        "starved": starved,
        "projected_28d_entries": projected_28d,
    })

    at_risk = []
    _mg = VALIDATION_CAMPAIGN["meta_gate"]
    if projected_28d < _mg["min_per_tercile"] * 3:
        at_risk.append("Meta-Gate(§3-2, 분위당 %d건×3 필요)" % _mg["min_per_tercile"])
    _hr = VALIDATION_CAMPAIGN["hurst_regime"]
    if projected_28d < _hr["min_per_bucket"] * 2:
        at_risk.append("레짐 ATR 배수(§3-5②, 버킷당 %d건×2 필요)" % _hr["min_per_bucket"])
    out["kpis_at_risk"] = at_risk

    ladder = ENTRY_STARVATION_MITIGATION_LADDER
    step3 = next(s for s in ladder if s["step"] == 3)
    step3_applied = abs(HURST_RANGE_THRESHOLD - step3["mitigated_value"]) < 1e-6

    if step3_applied:
        out["ladder_status"] = "3단계(Hurst 완화) 적용됨 — 사다리 소진, 추가 완화 여지 없음"
        out["current_step"] = 3
    elif not starved:
        out["ladder_status"] = "정상 — 사다리 미적용 상태 유지"
        out["current_step"] = 0
    else:
        step1 = next(s for s in ladder if s["step"] == 1)
        deployed = datetime.datetime.strptime(step1["deployed_date"], "%Y-%m-%d")
        days_since = (datetime.datetime.now() - deployed).days
        if days_since < 5:
            out["ladder_status"] = (
                "1단계 관찰 중 (FQAdj 수정 후 %d거래일 경과, 5일 채울 때까지 대기)" % days_since
            )
            out["current_step"] = 1
        else:
            out["ladder_status"] = (
                "1단계 관찰 기간(5거래일) 경과 후에도 기아 지속 — "
                "2단계(MetaGate take_ceil 0.570→0.52) 검토 권고 (사용자 결정 필요)"
            )
            out["current_step"] = 2

    out["verdict"] = "STARVED" if starved else "OK"
    return out


# ──────────────────────────────────────────────────────────────
# [1] Triple-Barrier 채널 — OOS replay IC vs 3클래스 IC
# ──────────────────────────────────────────────────────────────

def eval_tb_channel(days: int) -> dict:
    cr = VALIDATION_CAMPAIGN["tb"]
    out = {"horizons": {}, "verdict": "INSUFFICIENT", "n_pass": 0}

    if not os.path.isdir(SHADOW_TB_DIR):
        out["error"] = "섀도우 TB 모델 디렉토리 없음 — 첫 주간 재학습 대기"
        return out

    try:
        from model.multi_horizon_model import apply_robust_preprocess
    except Exception as e:
        out["error"] = "apply_robust_preprocess 임포트 실패: %s" % e
        return out

    for hz, h_min in HORIZONS.items():
        res = {"status": "INSUFFICIENT"}
        out["horizons"][hz] = res
        model_p = os.path.join(SHADOW_TB_DIR, "gbm_%s_shadow_tb.pkl" % hz)
        scaler_p = os.path.join(SHADOW_TB_DIR, "scaler_%s_shadow_tb.pkl" % hz)
        fn_p = os.path.join(SHADOW_TB_DIR, "feature_names_%s_shadow_tb.pkl" % hz)
        if not all(os.path.exists(p) for p in (model_p, scaler_p, fn_p)):
            res["reason"] = "모델 파일 없음"
            continue

        # OOS 보장: 모델 파일 mtime 이후 데이터만 평가 (학습 표본과 완전 분리)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(model_p))
        eval_start = max(
            mtime.strftime(_TS_FMT),
            _campaign_start(),
            (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT),
        )
        res["eval_start"] = eval_start

        try:
            with open(model_p, "rb") as f:
                model = pickle.load(f)
            with open(scaler_p, "rb") as f:
                scaler = pickle.load(f)
            with open(fn_p, "rb") as f:
                feat_names = pickle.load(f)
        except Exception as e:
            res["reason"] = "모델 로드 실패: %s" % e
            continue

        # 피처 행 로드 — batch_retrainer.retrain_shadow_triple_barrier와 동일 경로
        # (1m은 설계상 raw_features, 그 외는 raw_features_horizon → 부족 시 폴백)
        try:
            with _conn(RAW_DATA_DB) as conn:
                if hz == "1m":
                    rows = conn.execute(
                        "SELECT ts, features FROM raw_features WHERE ts > ? ORDER BY ts",
                        (eval_start,),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT ts, features FROM raw_features_horizon "
                        "WHERE horizon=? AND ts > ? ORDER BY ts",
                        (hz, eval_start),
                    ).fetchall()
                    if not rows:
                        rows = conn.execute(
                            "SELECT ts, features FROM raw_features WHERE ts > ? ORDER BY ts",
                            (eval_start,),
                        ).fetchall()
        except Exception as e:
            res["reason"] = "피처 조회 실패: %s" % e
            continue

        rows = rows[-_MAX_REPLAY_ROWS:]
        if not rows:
            res["reason"] = "OOS 표본 0건 (모델 mtime 이후 데이터 대기)"
            continue

        close_map, _hi, _lo = _load_candle_maps(eval_start)

        ts_list, X_list, y_list = [], [], []
        for r in rows:
            try:
                fd = json.loads(r["features"])
            except (ValueError, TypeError):
                continue
            if not isinstance(fd, dict):
                continue
            c0 = close_map.get(r["ts"])
            c1 = close_map.get(_ts_plus_min(r["ts"], h_min))
            if c0 is None or c1 is None:
                continue
            ts_list.append(r["ts"])
            X_list.append([float(fd.get(f, 0.0) or 0.0) for f in feat_names])
            y_list.append(c1 - c0)  # 실현 변동 (pt, 부호 포함)

        n = len(X_list)
        res["n_samples"] = n
        if n < int(cr["min_samples_hz"]):
            res["reason"] = "OOS 표본 부족 (%d < %d)" % (n, cr["min_samples_hz"])
            continue

        try:
            X = np.array(X_list, dtype=np.float32)
            X = apply_robust_preprocess(X, list(feat_names))
            X_s = scaler.transform(X)
            proba = model.predict_proba(X_s)
            cls = list(getattr(model, "classes_", []))
            i_up = cls.index(DIRECTION_UP) if DIRECTION_UP in cls else None
            i_dn = cls.index(DIRECTION_DOWN) if DIRECTION_DOWN in cls else None
            p_up = proba[:, i_up] if i_up is not None else np.zeros(n)
            p_dn = proba[:, i_dn] if i_dn is not None else np.zeros(n)
            tb_score = p_up - p_dn
        except Exception as e:
            res["reason"] = "replay 실패: %s" % e
            continue

        ic_tb = _spearman(tb_score, y_list)

        # 3클래스 baseline: 같은 기간·같은 호라이즌 meta_labels의 up/down_prob
        try:
            with _conn(PREDICTIONS_DB) as conn:
                mrows = conn.execute(
                    """SELECT up_prob, down_prob, target_close, future_close
                       FROM meta_labels
                       WHERE horizon=? AND ts > ?
                         AND up_prob IS NOT NULL AND down_prob IS NOT NULL
                         AND target_close IS NOT NULL AND future_close IS NOT NULL""",
                    (hz, eval_start),
                ).fetchall()
        except Exception as e:
            res["reason"] = "meta_labels 조회 실패: %s" % e
            continue

        base_score = [float(m["up_prob"]) - float(m["down_prob"]) for m in mrows]
        base_move = [float(m["future_close"]) - float(m["target_close"]) for m in mrows]
        ic_3c = _spearman(base_score, base_move) if len(base_score) >= 3 else float("nan")

        res.update({
            "ic_tb": None if np.isnan(ic_tb) else round(ic_tb, 4),
            "ic_3class": None if np.isnan(ic_3c) else round(ic_3c, 4),
            "n_baseline": len(base_score),
        })
        if np.isnan(ic_tb) or np.isnan(ic_3c):
            res["reason"] = "IC 계산 불가 (분산 0 또는 표본 부족)"
            continue

        passed = (ic_tb > ic_3c + cr["ic_delta_min"]) and (ic_tb > cr["ic_abs_min"])
        res["status"] = "PASS" if passed else "FAIL"

    n_pass = sum(1 for r in out["horizons"].values() if r.get("status") == "PASS")
    n_judged = sum(1 for r in out["horizons"].values() if r.get("status") in ("PASS", "FAIL"))
    out["n_pass"] = n_pass
    if n_judged == 0:
        out["verdict"] = "INSUFFICIENT"
    elif n_pass >= int(cr["min_horizons_pass"]):
        out["verdict"] = "PASS"
    else:
        out["verdict"] = "FAIL"
    return out


# ──────────────────────────────────────────────────────────────
# [2] Meta-Gate 채널 — entry_quality_prob 3분위별 실현 순EV
# ──────────────────────────────────────────────────────────────

def eval_meta_gate_channel(days: int) -> dict:
    cr = VALIDATION_CAMPAIGN["meta_gate"]
    out = {"verdict": "INSUFFICIENT"}
    cutoff = max(
        _campaign_start(),
        (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT),
    )

    try:
        with _conn(PREDICTIONS_DB) as conn:
            cols = {r["name"] for r in conn.execute(
                "PRAGMA table_info(ensemble_decisions)").fetchall()}
            hz_col = "meta_gate_horizon" if "meta_gate_horizon" in cols else None
            rows = conn.execute(
                """SELECT ts, direction, meta_entry_quality_prob AS prob%s
                   FROM ensemble_decisions
                   WHERE meta_entry_quality_prob IS NOT NULL
                     AND direction != 0 AND ts >= ?
                   ORDER BY ts""" % (
                    (", %s AS hz" % hz_col) if hz_col else ""),
                (cutoff,),
            ).fetchall()
            mrows = conn.execute(
                """SELECT ts, horizon, target_close, future_close FROM meta_labels
                   WHERE ts >= ? AND target_close IS NOT NULL AND future_close IS NOT NULL""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    move_map = {(m["ts"], m["horizon"]): float(m["future_close"]) - float(m["target_close"])
                for m in mrows}

    samples = []  # (prob, direction_conditioned_move_pt)
    prices = []
    for r in rows:
        hz = (r["hz"] if ("hz" in r.keys()) else "") or "1m"
        key = (r["ts"], hz)
        if key not in move_map:
            key = (r["ts"], "1m")  # 구버전 행 fallback
            if key not in move_map:
                continue
        samples.append((float(r["prob"]), move_map[key] * int(r["direction"])))
    # 평균 가격 → 왕복 비용 산정
    avg_price = float(np.mean([float(m["target_close"]) for m in mrows])) if mrows else 1300.0
    cost_pt = _roundtrip_cost_pt(avg_price)

    out["n_samples"] = len(samples)
    out["cost_pt"] = round(cost_pt, 4)
    if len(samples) < 3 * int(cr["min_per_tercile"]):
        out["reason"] = "표본 부족 (%d < %d)" % (len(samples), 3 * cr["min_per_tercile"])
        return out

    samples.sort(key=lambda s: s[0])
    n = len(samples)
    k = n // 3
    bottom = [s[1] - cost_pt for s in samples[:k]]
    top = [s[1] - cost_pt for s in samples[-k:]]
    mid = [s[1] - cost_pt for s in samples[k:n - k]]

    top_ev = float(np.mean(top))
    bot_ev = float(np.mean(bottom))
    out.update({
        "tercile_n": k,
        "top_ev_pt": round(top_ev, 4),
        "mid_ev_pt": round(float(np.mean(mid)), 4) if mid else None,
        "bottom_ev_pt": round(bot_ev, 4),
        "separation_pt": round(top_ev - bot_ev, 4),
        "required_sep_pt": round(cr["sep_cost_mult"] * cost_pt, 4),
    })
    if k < int(cr["min_per_tercile"]):
        out["reason"] = "분위별 표본 부족 (%d < %d)" % (k, cr["min_per_tercile"])
        return out

    passed = (top_ev > cr["top_ev_min_pt"]) and \
             ((top_ev - bot_ev) > cr["sep_cost_mult"] * cost_pt)
    out["verdict"] = "PASS" if passed else "FAIL"
    return out


# ──────────────────────────────────────────────────────────────
# [3] 분위 회귀 채널 — 커버리지 + 불확실성 상관
# ──────────────────────────────────────────────────────────────

def eval_quantile_channel(days: int) -> dict:
    cr = VALIDATION_CAMPAIGN["quantile"]
    out = {"verdict": "INSUFFICIENT"}
    cutoff = max(
        _campaign_start(),
        (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT),
    )

    try:
        with _conn(PREDICTIONS_DB) as conn:
            cols = {r["name"] for r in conn.execute(
                "PRAGMA table_info(ensemble_decisions)").fetchall()}
            if "quantile_q10_pt" not in cols:
                out["reason"] = "quantile_q10_pt 컬럼 없음 — 마이그레이션 전 데이터"
                return out
            rows = conn.execute(
                """SELECT ts, quantile_q10_pt AS q10, quantile_q90_pt AS q90,
                          COALESCE(NULLIF(meta_gate_horizon, ''), '1m') AS hz
                   FROM ensemble_decisions
                   WHERE quantile_q10_pt IS NOT NULL AND quantile_q90_pt IS NOT NULL
                     AND ts >= ?""",
                (cutoff,),
            ).fetchall()
            mrows = conn.execute(
                """SELECT ts, horizon, target_close, future_close FROM meta_labels
                   WHERE ts >= ? AND target_close IS NOT NULL AND future_close IS NOT NULL""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    move_map = {(m["ts"], m["horizon"]): float(m["future_close"]) - float(m["target_close"])
                for m in mrows}

    covered, widths, abs_moves = [], [], []
    for r in rows:
        mv = move_map.get((r["ts"], r["hz"]))
        if mv is None:
            continue
        q10, q90 = float(r["q10"]), float(r["q90"])
        covered.append(1.0 if (q10 <= mv <= q90) else 0.0)
        widths.append(q90 - q10)
        abs_moves.append(abs(mv))

    n = len(covered)
    out["n_samples"] = n
    if n < int(cr["min_samples"]):
        out["reason"] = "표본 부족 (%d < %d)" % (n, cr["min_samples"])
        return out

    coverage = float(np.mean(covered))
    unc_corr = _spearman(widths, abs_moves)
    out.update({
        "coverage": round(coverage, 4),
        "coverage_band": [cr["coverage_lo"], cr["coverage_hi"]],
        "unc_corr": None if np.isnan(unc_corr) else round(unc_corr, 4),
    })
    if np.isnan(unc_corr):
        out["reason"] = "상관 계산 불가"
        return out
    passed = (cr["coverage_lo"] <= coverage <= cr["coverage_hi"]) and \
             (unc_corr > cr["unc_corr_min"])
    out["verdict"] = "PASS" if passed else "FAIL"
    return out


# ──────────────────────────────────────────────────────────────
# [4] 신호소멸청산 counterfactual — resolve + 누적 판정
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_signal_decay() -> dict:
    cr = VALIDATION_CAMPAIGN["signal_decay"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM signal_decay_exits WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        close_map, high_map, low_map = _load_candle_maps(earliest)
        now = datetime.datetime.now()
        updates = []
        for r in unresolved:
            base = datetime.datetime.strptime(r["ts"], _TS_FMT)
            # 관찰 창이 아직 안 끝났으면(미래 데이터 부족) 다음 실행으로 미룸
            if now < base + datetime.timedelta(minutes=window_min + 2):
                continue
            is_long = str(r["direction"]) == "LONG"
            stop_p = float(r["stop_price"] or 0.0)
            tp1_p = float(r["tp1_price"] or 0.0)
            cf_outcome, cf_price = "NEITHER", None
            last_close = None
            # 창 종료 or 15:10 중 이른 쪽까지 분봉 스캔
            for m in range(1, window_min + 1):
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                if hi is None or lo is None:
                    continue
                last_close = close_map.get(mid_ts, last_close)
                if is_long:
                    hit_stop = stop_p > 0 and lo <= stop_p
                    hit_tp = tp1_p > 0 and hi >= tp1_p
                else:
                    hit_stop = stop_p > 0 and hi >= stop_p
                    hit_tp = tp1_p > 0 and lo <= tp1_p
                # 동시 터치 → 보수적으로 STOP 우선 (target_builder TB 레이블과 동일 관례)
                if hit_stop:
                    cf_outcome, cf_price = "STOP", stop_p
                    break
                if hit_tp:
                    cf_outcome, cf_price = "TP1", tp1_p
                    break
            if cf_price is None:
                if last_close is None:
                    continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                cf_price = last_close
            exit_p = float(r["exit_price"])
            # saved_pts: (+) = 조기청산이 더 나은 가격이었다 (아낀 pt)
            saved = (exit_p - cf_price) if is_long else (cf_price - exit_p)
            updates.append((cf_outcome, cf_price, round(saved, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE signal_decay_exits
                       SET resolved=1, cf_outcome=?, cf_exit_price=?, saved_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    # 누적 집계 (캠페인 시작 이후 전체)
    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(saved_pts) AS total_saved,
                          SUM(CASE WHEN cf_outcome='STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='TP1' THEN 1 ELSE 0 END) AS n_tp1,
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither
                   FROM signal_decay_exits WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM signal_decay_exits WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_saved = float(agg["total_saved"] or 0.0)
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_saved_pts": round(total_saved, 4),
        "cf_stop": int(agg["n_stop"] or 0),
        "cf_tp1": int(agg["n_tp1"] or 0),
        "cf_neither": int(agg["n_neither"] or 0),
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "발동 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out
    # PASS = 유지, FAIL = 롤백 권고 (§3-5: conf 임계 강화 → 그래도 음수면 OFF)
    out["verdict"] = "PASS" if total_saved >= 0 else "FAIL"
    if out["verdict"] == "FAIL":
        out["recommendation"] = "conf 임계를 zone_mc+0.05로 강화 후 2주 재관찰, 재음수 시 OFF"
    return out


# ──────────────────────────────────────────────────────────────
# [6] Hurst 게이트 counterfactual — resolve + 누적 판정 (§3-6, P1-4, 297차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_hurst_gate() -> dict:
    """hurst_gate_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.

    PASS = 게이트 존치 (차단된 신호가 실제로 손실 방향이었거나 완화 기준 미충족).
    FAIL = 사이징 완화 권고 (하드차단→×0.5로 먼저 완화, 즉시 언블록 아님 — §3-6).
    """
    cr = VALIDATION_CAMPAIGN["hurst_gate_shadow"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM hurst_gate_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        close_map, high_map, low_map = _load_candle_maps(earliest)
        now = datetime.datetime.now()
        updates = []
        for r in unresolved:
            base = datetime.datetime.strptime(r["ts"], _TS_FMT)
            if now < base + datetime.timedelta(minutes=window_min + 2):
                continue
            is_long = str(r["direction"]) == "LONG"
            stop_p = float(r["stop_price"] or 0.0)
            tp1_p = float(r["tp1_price"] or 0.0)
            cf_outcome, cf_price = "NEITHER", None
            last_close = None
            for m in range(1, window_min + 1):
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                if hi is None or lo is None:
                    continue
                last_close = close_map.get(mid_ts, last_close)
                if is_long:
                    hit_stop = stop_p > 0 and lo <= stop_p
                    hit_tp = tp1_p > 0 and hi >= tp1_p
                else:
                    hit_stop = stop_p > 0 and hi >= stop_p
                    hit_tp = tp1_p > 0 and lo <= tp1_p
                # 동시 터치 → 보수적으로 STOP 우선 (signal_decay·TB 레이블과 동일 관례)
                if hit_stop:
                    cf_outcome, cf_price = "STOP", stop_p
                    break
                if hit_tp:
                    cf_outcome, cf_price = "TP1", tp1_p
                    break
            if cf_price is None:
                if last_close is None:
                    continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                cf_price = last_close
            entry_p = float(r["entry_price"])
            # hyp_pnl_pts: (+) = 차단 안 했으면 이득이었다(완화 근거), (-) = 차단이 손실 회피
            hyp = (cf_price - entry_p) if is_long else (entry_p - cf_price)
            updates.append((cf_outcome, cf_price, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE hurst_gate_shadow
                       SET resolved=1, cf_outcome=?, cf_exit_price=?, hyp_pnl_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          AVG(entry_price) AS avg_price,
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win,
                          SUM(CASE WHEN cf_outcome='STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='TP1' THEN 1 ELSE 0 END) AS n_tp1,
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither
                   FROM hurst_gate_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM hurst_gate_shadow WHERE resolved=0"
            ).fetchone()["n"]
            baseline = conn.execute(
                """SELECT AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0
                                   THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ? AND %s"""
                % _NOT_GHOST_SQL,
                (_campaign_start(),),
            ).fetchone()
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    baseline_wr = (
        float(baseline["wr"]) if baseline and baseline["wr"] is not None else None
    )
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
        "baseline_win_rate": round(baseline_wr, 4) if baseline_wr is not None else None,
        "cf_stop": int(agg["n_stop"] or 0),
        "cf_tp1": int(agg["n_tp1"] or 0),
        "cf_neither": int(agg["n_neither"] or 0),
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "차단 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    mitigate = (
        total_hyp > cost_pt * 2.0
        and baseline_wr is not None
        and win_rate > baseline_wr
    )
    out["verdict"] = "FAIL" if mitigate else "PASS"
    if mitigate:
        out["recommendation"] = (
            "Hurst 하드차단 → 사이징 ×0.5로 완화 권고 (즉시 언블록 금지, §3-6)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [7] JointGateBlock counterfactual — resolve + 누적 판정 (§3-7, 327차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_joint_gate() -> dict:
    """joint_gate_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.
    hurst_gate_shadow와 완전히 동일한 판정 로직 — 대상 테이블만 다르다.

    PASS = 게이트 존치 (차단된 신호가 실제로 손실 방향이었거나 완화 기준 미충족).
    FAIL = 완화 권고 (하드차단→임계값 0.50 완화부터 검토, 즉시 언블록 아님 — §3-7).

    추가로 meta_size 구간별(< 0.55 / ≥ 0.55) 승률·hyp_pnl_pts를 함께 집계한다 —
    ToxicityGate reduce의 size_multiplier가 상수 0.7이라 joint_mult이 사실상
    meta_size 단일 임계와 동치라는 구조적 의문(07-14 실측 분석,
    docs/Ref/jointfateBlock.txt)을 표본이 쌓이면 검증할 수 있게 하기 위함.
    """
    cr = VALIDATION_CAMPAIGN["joint_gate_shadow"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM joint_gate_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        close_map, high_map, low_map = _load_candle_maps(earliest)
        now = datetime.datetime.now()
        updates = []
        for r in unresolved:
            base = datetime.datetime.strptime(r["ts"], _TS_FMT)
            if now < base + datetime.timedelta(minutes=window_min + 2):
                continue
            is_long = str(r["direction"]) == "LONG"
            stop_p = float(r["stop_price"] or 0.0)
            tp1_p = float(r["tp1_price"] or 0.0)
            cf_outcome, cf_price = "NEITHER", None
            last_close = None
            for m in range(1, window_min + 1):
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                if hi is None or lo is None:
                    continue
                last_close = close_map.get(mid_ts, last_close)
                if is_long:
                    hit_stop = stop_p > 0 and lo <= stop_p
                    hit_tp = tp1_p > 0 and hi >= tp1_p
                else:
                    hit_stop = stop_p > 0 and hi >= stop_p
                    hit_tp = tp1_p > 0 and lo <= tp1_p
                # 동시 터치 → 보수적으로 STOP 우선 (signal_decay·hurst_gate와 동일 관례)
                if hit_stop:
                    cf_outcome, cf_price = "STOP", stop_p
                    break
                if hit_tp:
                    cf_outcome, cf_price = "TP1", tp1_p
                    break
            if cf_price is None:
                if last_close is None:
                    continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                cf_price = last_close
            entry_p = float(r["entry_price"])
            # hyp_pnl_pts: (+) = 차단 안 했으면 이득이었다(완화 근거), (-) = 차단이 손실 회피
            hyp = (cf_price - entry_p) if is_long else (entry_p - cf_price)
            updates.append((cf_outcome, cf_price, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE joint_gate_shadow
                       SET resolved=1, cf_outcome=?, cf_exit_price=?, hyp_pnl_pts=?
                       WHERE id=?""",
                    updates,
                )
                conn.commit()
            out["resolved_now"] = len(updates)

    try:
        with _conn(TRADES_DB) as conn:
            agg = conn.execute(
                """SELECT COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          AVG(entry_price) AS avg_price,
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win,
                          SUM(CASE WHEN cf_outcome='STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='TP1' THEN 1 ELSE 0 END) AS n_tp1,
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither
                   FROM joint_gate_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM joint_gate_shadow WHERE resolved=0"
            ).fetchone()["n"]
            baseline = conn.execute(
                """SELECT AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0
                                   THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ? AND %s"""
                % _NOT_GHOST_SQL,
                (_campaign_start(),),
            ).fetchone()
            # meta_size 구간별(<0.55 / >=0.55) 분리 집계 — tox_size 상수 구조 의문 검증용
            meta_split = conn.execute(
                """SELECT CASE WHEN meta_size >= 0.55 THEN 'high' ELSE 'low' END AS bucket,
                          COUNT(*) AS n, SUM(hyp_pnl_pts) AS total_hyp,
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win
                   FROM joint_gate_shadow
                   WHERE resolved=1 AND ts >= ?
                   GROUP BY bucket""",
                (_campaign_start(),),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    baseline_wr = (
        float(baseline["wr"]) if baseline and baseline["wr"] is not None else None
    )
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
        "baseline_win_rate": round(baseline_wr, 4) if baseline_wr is not None else None,
        "cf_stop": int(agg["n_stop"] or 0),
        "cf_tp1": int(agg["n_tp1"] or 0),
        "cf_neither": int(agg["n_neither"] or 0),
        "meta_size_split": {
            row["bucket"]: {
                "n": int(row["n"] or 0),
                "total_hyp_pnl_pts": round(float(row["total_hyp"] or 0.0), 4),
                "win_rate": round((int(row["n_win"] or 0) / row["n"]), 4) if row["n"] else 0.0,
            }
            for row in meta_split
        },
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "차단 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    mitigate = (
        total_hyp > cost_pt * 2.0
        and baseline_wr is not None
        and win_rate > baseline_wr
    )
    out["verdict"] = "FAIL" if mitigate else "PASS"
    if mitigate:
        out["recommendation"] = (
            "JointGateBlock 임계값 0.50 → 완화 검토 (즉시 언블록 금지, §3-7)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [5] 레짐 조건부 ATR 배수 — hurst_bucket별 순EV
# ──────────────────────────────────────────────────────────────

def eval_hurst_regime() -> dict:
    cr = VALIDATION_CAMPAIGN["hurst_regime"]
    out = {"verdict": "INSUFFICIENT", "buckets": {}}
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT COALESCE(NULLIF(hurst_bucket,''),'?') AS bucket,
                          COUNT(*) AS n,
                          AVG(net_pnl_krw) AS avg_ev,
                          SUM(net_pnl_krw) AS total_ev,
                          AVG(CASE WHEN net_pnl_krw > 0 THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades
                   WHERE exit_ts >= ? AND net_pnl_krw IS NOT NULL AND %s
                   GROUP BY bucket""" % _NOT_GHOST_SQL,
                (_campaign_start(),),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    for r in rows:
        out["buckets"][r["bucket"]] = {
            "n": int(r["n"]),
            "avg_ev_krw": round(float(r["avg_ev"] or 0.0), 0),
            "total_ev_krw": round(float(r["total_ev"] or 0.0), 0),
            "win_rate": round(float(r["wr"] or 0.0), 3),
        }

    trend = out["buckets"].get("trend")
    neutral = out["buckets"].get("neutral")
    min_n = int(cr["min_per_bucket"])
    if not trend or trend["n"] < min_n or not neutral or neutral["n"] < min_n:
        out["reason"] = "버킷별 표본 부족 (trend/neutral 각 %d건 필요)" % min_n
        return out
    # FAIL = trend 배수 1.20→1.10 후퇴 권고
    bad = trend["avg_ev_krw"] < 0 and trend["avg_ev_krw"] < neutral["avg_ev_krw"]
    out["verdict"] = "FAIL" if bad else "PASS"
    if bad:
        out["recommendation"] = "HURST_REGIME_ATR_MULT trend 1.20 → 1.10 후퇴 권고"
    return out


# ──────────────────────────────────────────────────────────────
# 리포트 생성
# ──────────────────────────────────────────────────────────────

def _fmt_verdict(v: str) -> str:
    return {
        "PASS": "✅ PASS", "FAIL": "❌ FAIL",
        "OK": "✅ OK", "STARVED": "🚨 STARVED",
    }.get(v, "⏳ INSUFFICIENT")


def build_report(days: int) -> tuple:
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ss = eval_sample_starvation()
    tb = eval_tb_channel(days)
    mg = eval_meta_gate_channel(days)
    qt = eval_quantile_channel(days)
    sd = resolve_and_eval_signal_decay()
    hr = eval_hurst_regime()
    hg = resolve_and_eval_hurst_gate()
    jg = resolve_and_eval_joint_gate()

    metrics = {
        "generated_at": now_str,
        "days": days,
        "criteria": VALIDATION_CAMPAIGN,
        "sample_starvation": ss,
        "tb": tb, "meta_gate": mg, "quantile": qt,
        "signal_decay": sd, "hurst_regime": hr, "hurst_gate_shadow": hg,
        "joint_gate_shadow": jg,
    }

    L = []
    L.append("# 검증 캠페인 주간 판정 리포트")
    L.append("")
    L.append("- 생성: %s  (분석 창 %d일, 캠페인 시작 %s)" % (
        now_str, days, VALIDATION_CAMPAIGN.get("start_date")))
    L.append("- 합격선: `config/settings.py:VALIDATION_CAMPAIGN` (사전 등록 — 변경 금지)")
    L.append("- 근거: `docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md` §3")
    L.append("")
    L.append("| 채널 | 판정 | 핵심 수치 |")
    L.append("|---|---|---|")
    L.append("| [0] 표본 기아 경보 | %s | 주간진입=%s건(하한 %s) 4주투영=%s건 |" % (
        _fmt_verdict(ss["verdict"]), ss.get("n_weekly_entries", "—"),
        ss.get("floor", "—"), ss.get("projected_28d_entries", "—")))
    L.append("| [1] Triple-Barrier | %s | 합격 호라이즌 %d개 (기준 %d개) |" % (
        _fmt_verdict(tb["verdict"]), tb.get("n_pass", 0),
        VALIDATION_CAMPAIGN["tb"]["min_horizons_pass"]))
    L.append("| [2] Meta-Gate | %s | 상위EV=%s 분리도=%s (필요 %s) |" % (
        _fmt_verdict(mg["verdict"]), mg.get("top_ev_pt", "—"),
        mg.get("separation_pt", "—"), mg.get("required_sep_pt", "—")))
    L.append("| [3] 분위 회귀 | %s | 커버리지=%s (밴드 %s) 상관=%s |" % (
        _fmt_verdict(qt["verdict"]), qt.get("coverage", "—"),
        qt.get("coverage_band", "—"), qt.get("unc_corr", "—")))
    L.append("| [4] 신호소멸청산 | %s | 누적 saved=%spt (n=%s, 보류 %s) |" % (
        _fmt_verdict(sd["verdict"]), sd.get("total_saved_pts", "—"),
        sd.get("n_resolved", 0), sd.get("n_pending", 0)))
    L.append("| [5] 레짐 ATR 배수 | %s | %s |" % (
        _fmt_verdict(hr["verdict"]),
        " / ".join("%s: n=%d EV=%s원" % (b, v["n"], format(v["avg_ev_krw"], ",.0f"))
                   for b, v in sorted(hr.get("buckets", {}).items())) or "거래 없음"))
    L.append("| [6] Hurst 게이트 counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s) |" % (
        _fmt_verdict(hg["verdict"]), hg.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (hg["win_rate"] * 100)) if "win_rate" in hg else "—",
        hg.get("n_resolved", 0), hg.get("n_pending", 0)))
    L.append("| [7] JointGateBlock counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s) |" % (
        _fmt_verdict(jg["verdict"]), jg.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (jg["win_rate"] * 100)) if "win_rate" in jg else "—",
        jg.get("n_resolved", 0), jg.get("n_pending", 0)))
    L.append("")

    # [0] 표본 기아 경보 상세
    L.append("## [0] 캠페인 표본 기아 경보 + 완화 사다리 (§3-8)")
    L.append("")
    if ss.get("error"):
        L.append("> ⚠ %s" % ss["error"])
    else:
        L.append("- 주간(7일) 진입 체결: **%d건** (하한 %d건) → 4주 투영 %d건" % (
            ss["n_weekly_entries"], ss["floor"], ss["projected_28d_entries"]))
        if ss.get("kpis_at_risk"):
            L.append("- **표본 미달 위험 KPI**: " + " / ".join(ss["kpis_at_risk"]))
        L.append("- **완화 사다리 상태**: %s" % ss.get("ladder_status", "—"))
        L.append("")
        L.append("| 단계 | 조치 | 상태 |")
        L.append("|---|---|---|")
        for s in ENTRY_STARVATION_MITIGATION_LADDER:
            _mark = "**← 현재**" if s["step"] == ss.get("current_step") else ""
            L.append("| %d | %s | %s |" % (s["step"], s["action"], _mark))
        L.append("")
        L.append("> 사다리 적용은 항상 사용자 수동 결정 — 자동 변경 없음. 적용 시"
                  " `dev_memory/DECISION_LOG.md`에 기록할 것.")
    L.append("")

    # [1] TB 상세
    L.append("## [1] Triple-Barrier — OOS replay IC vs 3클래스 IC")
    L.append("")
    L.append("| 호라이즌 | 판정 | IC_TB | IC_3class | OOS n | 비고 |")
    L.append("|---|---|---|---|---|---|")
    for hz in HORIZONS:
        r = tb["horizons"].get(hz, {})
        L.append("| %s | %s | %s | %s | %s | %s |" % (
            hz, r.get("status", "—"), r.get("ic_tb", "—"), r.get("ic_3class", "—"),
            r.get("n_samples", "—"), r.get("reason", "")))
    if tb.get("error"):
        L.append("")
        L.append("> ⚠ %s" % tb["error"])
    L.append("")

    # [2] Meta-Gate 상세
    L.append("## [2] Meta-Gate — entry_quality_prob 3분위 순EV (왕복비용 %s pt 차감)" %
             mg.get("cost_pt", "—"))
    L.append("")
    if "top_ev_pt" in mg:
        L.append("| 분위 | 순EV(pt) | n |")
        L.append("|---|---|---|")
        L.append("| 상위 33%% | %s | %s |" % (mg["top_ev_pt"], mg.get("tercile_n")))
        L.append("| 중위 33%% | %s | — |" % mg.get("mid_ev_pt"))
        L.append("| 하위 33%% | %s | %s |" % (mg["bottom_ev_pt"], mg.get("tercile_n")))
    else:
        L.append("- %s" % mg.get("reason", mg.get("error", "데이터 없음")))
    L.append("")

    # [3] 분위 회귀 상세
    L.append("## [3] 분위 회귀 — 캘리브레이션")
    L.append("")
    L.append("- 표본: %s건 / 커버리지 %s (합격 밴드 %s~%s) / 불확실성-실현폭 상관 %s (하한 %s)" % (
        qt.get("n_samples", 0), qt.get("coverage", "—"),
        VALIDATION_CAMPAIGN["quantile"]["coverage_lo"],
        VALIDATION_CAMPAIGN["quantile"]["coverage_hi"],
        qt.get("unc_corr", "—"), VALIDATION_CAMPAIGN["quantile"]["unc_corr_min"]))
    if qt.get("reason"):
        L.append("- %s" % qt["reason"])
    L.append("")

    # [4] 신호소멸청산 상세
    L.append("## [4] 신호소멸청산 counterfactual (§3-5 롤백 기준 ①)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        sd.get("resolved_now", 0), sd.get("n_resolved", 0), sd.get("n_pending", 0)))
    L.append("- counterfactual 분포: STOP %s / TP1 %s / NEITHER %s" % (
        sd.get("cf_stop", 0), sd.get("cf_tp1", 0), sd.get("cf_neither", 0)))
    L.append("- 누적 saved_pts(아낀 pt − 놓친 pt): **%s pt**" % sd.get("total_saved_pts", "—"))
    if sd.get("recommendation"):
        L.append("- **권고**: %s" % sd["recommendation"])
    if sd.get("reason"):
        L.append("- %s" % sd["reason"])
    L.append("")

    # [5] 레짐 배수 상세
    L.append("## [5] 레짐 조건부 ATR 배수 (§3-5 롤백 기준 ②)")
    L.append("")
    if hr.get("buckets"):
        L.append("| 버킷 | n | 평균 순EV(원) | 누적(원) | 승률 |")
        L.append("|---|---|---|---|---|")
        for b, v in sorted(hr["buckets"].items()):
            L.append("| %s | %d | %s | %s | %.1f%% |" % (
                b, v["n"], format(v["avg_ev_krw"], ",.0f"),
                format(v["total_ev_krw"], ",.0f"), v["win_rate"] * 100))
    if hr.get("recommendation"):
        L.append("")
        L.append("- **권고**: %s" % hr["recommendation"])
    if hr.get("reason"):
        L.append("")
        L.append("- %s" % hr["reason"])
    L.append("")

    # [6] Hurst 게이트 counterfactual 상세
    L.append("## [6] Hurst 게이트 counterfactual (§3-6, P1-4)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        hg.get("resolved_now", 0), hg.get("n_resolved", 0), hg.get("n_pending", 0)))
    L.append("- counterfactual 분포: STOP %s / TP1 %s / NEITHER %s" % (
        hg.get("cf_stop", 0), hg.get("cf_tp1", 0), hg.get("cf_neither", 0)))
    L.append("- 누적 hyp_pnl_pts(차단 안 했으면 얻었을 pt): **%s pt** / 승률 %s (기준선 %s)" % (
        hg.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (hg["win_rate"] * 100)) if "win_rate" in hg else "—",
        ("%.1f%%" % (hg["baseline_win_rate"] * 100)) if hg.get("baseline_win_rate") is not None else "—",
    ))
    if hg.get("recommendation"):
        L.append("- **권고**: %s" % hg["recommendation"])
    if hg.get("reason"):
        L.append("- %s" % hg["reason"])
    L.append("")

    # [7] JointGateBlock counterfactual 상세
    L.append("## [7] JointGateBlock counterfactual (§3-7, 327차)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        jg.get("resolved_now", 0), jg.get("n_resolved", 0), jg.get("n_pending", 0)))
    L.append("- counterfactual 분포: STOP %s / TP1 %s / NEITHER %s" % (
        jg.get("cf_stop", 0), jg.get("cf_tp1", 0), jg.get("cf_neither", 0)))
    L.append("- 누적 hyp_pnl_pts(차단 안 했으면 얻었을 pt): **%s pt** / 승률 %s (기준선 %s)" % (
        jg.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (jg["win_rate"] * 100)) if "win_rate" in jg else "—",
        ("%.1f%%" % (jg["baseline_win_rate"] * 100)) if jg.get("baseline_win_rate") is not None else "—",
    ))
    if jg.get("meta_size_split"):
        L.append("- meta_size 구간별(tox_size 상수 구조 검증용):")
        for bucket, v in sorted(jg["meta_size_split"].items()):
            L.append("  - %s(meta%s0.55): n=%d hyp=%spt 승률=%.1f%%" % (
                bucket, "≥" if bucket == "high" else "<",
                v["n"], v["total_hyp_pnl_pts"], v["win_rate"] * 100))
    if jg.get("recommendation"):
        L.append("- **권고**: %s" % jg["recommendation"])
    if jg.get("reason"):
        L.append("- %s" % jg["reason"])
    L.append("")
    L.append("---")
    L.append("")
    L.append("> 이 리포트는 권고만 출력한다. 정책 적용/롤백은 주간 회의에서 수동 결정하고")
    L.append("> `dev_memory/DECISION_LOG.md`에 기록할 것 (§2 사전등록 원칙, §9 계엄령).")

    return "\n".join(L), metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=28,
                        help="분석 창(일). 기본 28 — 캠페인 4주 전체")
    args = parser.parse_args()

    report_md, metrics = build_report(args.days)

    os.makedirs(DATA_DIR, exist_ok=True)
    md_path = os.path.join(DATA_DIR, "validation_campaign_report.md")
    json_path = os.path.join(DATA_DIR, "validation_campaign_metrics.json")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2, default=str)

    print(report_md)
    print("\n저장: %s / %s" % (md_path, json_path))


if __name__ == "__main__":
    main()
