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
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import (
    PREDICTIONS_DB, TRADES_DB, RAW_DATA_DB, DATA_DIR, MODEL_DIR,
    HORIZONS, VALIDATION_CAMPAIGN, FUTURES_COMMISSION_RATE, TICK_SIZE,
    ENTRY_STARVATION_WEEKLY_MIN, ENTRY_STARVATION_MITIGATION_LADDER,
    HURST_RANGE_THRESHOLD, REGIME_EXHAUSTION_EXT_ATR_THRESHOLD,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN
from strategy.position.position_tracker import compute_trailing_stop_tier  # [361차]
from utils.db_utils import (  # [384차] TB 채널 판정 유지(carry-forward)
    save_tb_verdict, fetch_latest_tb_verdicts,
)

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
    """[384차] 383차가 규명한 구조결함(평가창이 매주 재학습으로 리셋돼 5m~30m이
    min_samples_hz 영구 미달) 해법: 호라이즌별로 실제 OOS n이 min_samples_hz에
    도달한 주에만 신선하게 판정하고 tb_verdict_log에 기록한다. 그 아래 주는 그
    "최근 판정"을 그대로 이어받아(carry-forward) 채널 집계에 반영 — n_pass/verdict
    계산 로직 자체는 res["status"]만 보므로 변경 불요."""
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

    try:
        carried_verdicts = fetch_latest_tb_verdicts()
    except Exception as e:
        carried_verdicts = {}
        print("[TB채널] tb_verdict_log 조회 실패: %s" % e)

    now_dt = datetime.datetime.now()

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
            cv = carried_verdicts.get(hz)
            if cv is not None:
                res["status"] = cv["verdict"]
                res["carried"] = True
                res["judged_at"] = cv["judged_at"]
                res["ic_tb"] = cv["ic_tb"]
                res["ic_3class"] = cv["ic_3class"]
                res["reason"] = (
                    "누적중 (%d/%d) — 최근 판정 유지: %s (%s 판정, n=%d)"
                    % (n, cr["min_samples_hz"], cv["verdict"], cv["judged_at"][:10], cv["n_samples"])
                )
            else:
                res["reason"] = "OOS 표본 부족 (%d < %d) — 첫 판정 대기" % (n, cr["min_samples_hz"])
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
        res["carried"] = False
        res["judged_at"] = now_dt.strftime(_TS_FMT)
        try:
            save_tb_verdict(
                horizon=hz, judged_at=res["judged_at"], eval_start=eval_start,
                model_mtime=mtime.strftime(_TS_FMT), n_samples=n,
                ic_tb=res["ic_tb"], ic_3class=res["ic_3class"], verdict=res["status"],
            )
        except Exception as e:
            res["reason"] = (res.get("reason", "") + " (판정 기록 실패: %s)" % e).strip()

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
            # [357차] 계측 생존 점검 — 최근 7일 소스 컬럼 적재량(방향 무관).
            # 0이면 "표본 대기"가 아니라 스코어러 사망(모델 로드 실패 등) 의심.
            _7d = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(_TS_FMT)
            src_7d = conn.execute(
                """SELECT COUNT(*) AS n FROM ensemble_decisions
                   WHERE meta_entry_quality_prob IS NOT NULL AND ts >= ?""",
                (_7d,),
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    out["src_nonnull_7d"] = int(src_7d)
    if src_7d == 0:
        out["no_data"] = True

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
        if out.get("no_data"):
            out["reason"] += (" — **최근 7일 소스(meta_entry_quality_prob) 적재 0건**: "
                              "스코어러 모델 로드 실패 등 계측 사망 의심, 표본 대기가 아님 (357차)")
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
            # [357차] 계측 생존 점검 — [2]와 동일 취지 (분위 스코어러 사망 감지)
            _7d = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(_TS_FMT)
            src_7d = conn.execute(
                """SELECT COUNT(*) AS n FROM ensemble_decisions
                   WHERE quantile_q10_pt IS NOT NULL AND ts >= ?""",
                (_7d,),
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    out["src_nonnull_7d"] = int(src_7d)
    if src_7d == 0:
        out["no_data"] = True

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
        if out.get("no_data"):
            out["reason"] += (" — **최근 7일 소스(quantile_q10_pt) 적재 0건**: "
                              "스코어러 모델 로드 실패 등 계측 사망 의심, 표본 대기가 아님 (357차)")
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
# [9] OPEN_VOLATILE 시가이격 필터 counterfactual — resolve + 누적 판정 (§14, 354차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_open_gap() -> dict:
    """open_gap_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.
    hurst_gate_shadow와 완전히 동일한 판정 로직 — 대상 테이블만 다르다.

    PASS = 게이트 존치 (차단된 신호가 실제로 손실 방향이었거나 완화 기준 미충족).
    FAIL = 재설계 검토 권고 (2026-07-16 정기점검 P2-d — 세션 시가 고정 기준점 +
    ATR 압축으로 임계가 좁아지는 구조적 결함이 실제로 피해를 낸다는 실측 근거가
    이번에 처음 확보됐다는 뜻. 즉시 언블록이 아니라 그때의 실측 gap_pt/atr_at_block
    값을 근거로 기준점(예: 최근 N분 VWAP)·임계 재설계 착수).
    """
    cr = VALIDATION_CAMPAIGN["open_gap_shadow"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM open_gap_shadow WHERE resolved = 0 ORDER BY ts"
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
            # hyp_pnl_pts: (+) = 차단 안 했으면 이득이었다(재설계 근거), (-) = 차단이 손실 회피
            hyp = (cf_price - entry_p) if is_long else (entry_p - cf_price)
            updates.append((cf_outcome, cf_price, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE open_gap_shadow
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
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither,
                          AVG(gap_pt) AS avg_gap_pt, AVG(atr_at_block) AS avg_atr
                   FROM open_gap_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM open_gap_shadow WHERE resolved=0"
            ).fetchone()["n"]
            baseline = conn.execute(
                """SELECT AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0
                                   THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ?""",
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
        "avg_gap_pt": round(float(agg["avg_gap_pt"] or 0.0), 2),
        "avg_atr_at_block": round(float(agg["avg_atr"] or 0.0), 2),
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
            "OPEN_VOLATILE 시가이격 필터 재설계 검토 권고 — 실측 gap_pt/atr_at_block "
            "근거로 기준점(예: 최근 N분 VWAP)·임계 재설계 착수 (즉시 언블록 금지, P2-d)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [21] 방향별 순EV 감시 (402차 후속5) — [13] grade_ev_inversion의 미러
# ──────────────────────────────────────────────────────────────

def eval_direction_ev_watch() -> dict:
    """LONG/SHORT 방향별 실현 순EV를 캠페인 시작일 이후 누적 판정한다.

    [13] grade_ev_inversion과 동일 구조(축만 등급→방향). 실제 체결의 net_pnl_krw를
    그대로 집계하므로 counterfactual 시뮬레이션 불필요.

    **[13]과 필터가 다르다(의도적)**: [13]은 `grade IN ('A','B','C')`이라
    구버전 entry_source=NULL·OPERATOR_MANUAL 행이 포함되지만, 이 채널은
    `entry_source='SYSTEM_AUTO'` 한정이다 — 방향 편향은 시스템 판단의 문제이므로
    수동·레거시 진입을 섞으면 안 된다. 두 채널의 표본 수가 다른 것은 결함이 아니다
    (config/settings.py:VALIDATION_CAMPAIGN['direction_ev_watch'] 주석 참조).

    또한 trades는 부분청산을 같은 entry_ts로 여러 행에 나눠 기록하므로 그대로 세면
    TP1/TP2 부분청산이 각각 '승리'로 집계돼 승률이 부풀려진다(402차가 실제로 이
    함정에 걸렸다). 여기서는 **진입 1건 단위**로 묶어 집계한다.

    PASS = 두 방향 모두 평균 순EV ≥ 0, 또는 두 방향 모두 < 0(방향이 아니라 전반 문제).
    FAIL = 한 방향만 평균 순EV < 0 이고 양쪽 표본 충분 → 그 방향 min_conf 상향/사이징
    축소를 **섀도로** 먼저 검증할지 주간회의에서 결정(§9 — 즉시 적용 아님).
    """
    cr = VALIDATION_CAMPAIGN.get("direction_ev_watch", {})
    src = cr.get("entry_source", "SYSTEM_AUTO")
    min_n = int(cr.get("min_samples_per_direction", 20))
    out = {"verdict": "INSUFFICIENT", "entry_source_filter": src}

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT entry_ts, direction,
                          COALESCE(net_pnl_krw, pnl_krw) AS pnl
                     FROM trades
                    WHERE exit_ts IS NOT NULL AND exit_ts >= ?
                      AND COALESCE(entry_source,'') = ?
                      AND direction IN ('LONG','SHORT')""",
                (_campaign_start(), src),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    # 진입 1건 단위로 병합 — 부분청산 행 중복 제거(합산이 그 진입의 실현 손익)
    from collections import defaultdict
    merged = defaultdict(lambda: {"dir": None, "pnl": 0.0})
    for r in rows:
        k = (r["entry_ts"], r["direction"])
        merged[k]["dir"] = r["direction"]
        merged[k]["pnl"] += float(r["pnl"] or 0.0)

    by_dir = defaultdict(list)
    for v in merged.values():
        by_dir[v["dir"]].append(v["pnl"])

    stats = {}
    for d, pnls in by_dir.items():
        arr = np.array(pnls, dtype=float)
        stats[d] = {
            "n": len(pnls),
            "avg_pnl_krw": round(float(arr.mean()), 0),
            "total_pnl_krw": round(float(arr.sum()), 0),
            "win_rate": round(float((arr > 0).mean()), 4),
            "min_pnl_krw": round(float(arr.min()), 0),
            "stdev_pnl_krw": round(float(arr.std(ddof=1)) if len(pnls) > 1 else 0.0, 0),
        }
    out["by_direction"] = stats
    out["n_entries_merged"] = len(merged)
    out["n_rows_raw"] = len(rows)

    lo = stats.get("LONG")
    sh = stats.get("SHORT")
    if not lo or not sh or lo["n"] < min_n or sh["n"] < min_n:
        out["reason"] = ("방향별 표본 부족 (LONG %d / SHORT %d, 각 %d 필요) — 판정 보류"
                         % (lo["n"] if lo else 0, sh["n"] if sh else 0, min_n))
        return out

    neg = [d for d in ("LONG", "SHORT") if stats[d]["avg_pnl_krw"] < 0]
    if len(neg) == 1:
        d = neg[0]
        out["verdict"] = "FAIL"
        out["recommendation"] = (
            "%s 방향만 평균 순EV 음수(%s원, n=%d, 최대손실 %s원, 표준편차 %s원) — "
            "해당 방향 min_conf 상향/사이징 축소를 섀도로 먼저 검증할지 주간회의에서 "
            "결정(즉시 적용 아님). 최대손실·표준편차로 단일건 지배 여부를 먼저 확인할 것."
            % (d, format(stats[d]["avg_pnl_krw"], ",.0f"), stats[d]["n"],
               format(stats[d]["min_pnl_krw"], ",.0f"),
               format(stats[d]["stdev_pnl_krw"], ",.0f"))
        )
    else:
        out["verdict"] = "PASS"
        if len(neg) == 2:
            out["reason"] = "두 방향 모두 평균 순EV 음수 — 방향 편향이 아니라 전반 성능 문제"
    return out


# ──────────────────────────────────────────────────────────────
# [22] MFE 캡처율 관찰 (402차 후속5) — verdict 항상 OBSERVE
# ──────────────────────────────────────────────────────────────

def eval_mfe_capture_watch() -> dict:
    """캡처율 = 실현 pt / 진입 후 최대 유리폭(MFE) pt 를 누적 관찰한다.

    fast_reversal_watch·exit_fill_slippage_watch와 동일한 관찰 계열 — verdict는 항상
    OBSERVE 고정이며 이 수치로 정책을 바꾸지 않는다. 이 지표로 내릴 결정
    ("청산을 더 늦춰라")은 이미 [12] tp1_trail_shadow가 판정 중이므로, 이 채널은
    그 판정을 해석할 맥락("캡처율이 이렇게 낮은데도 트레일링이 안 낫다")만 제공한다.

    두 가지를 함께 낸다:
      capture_in_hold  실현 / 보유구간(진입~청산) MFE — "고점에서 나왔나"
      capture_to_close 실현 / 진입~15:10 MFE        — "더 들고 갈 수 있었나"

    집계 단위는 진입 1건(부분청산 행 병합, 수량가중 평균 실현 pt).
    """
    cr = VALIDATION_CAMPAIGN.get("mfe_capture_watch", {})
    src = cr.get("entry_source", "SYSTEM_AUTO")
    min_note = int(cr.get("min_samples_for_note", 20))
    out = {"verdict": "OBSERVE", "entry_source_filter": src}

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT entry_ts, exit_ts, direction, entry_price,
                          pnl_pts, quantity
                     FROM trades
                    WHERE exit_ts IS NOT NULL AND exit_ts >= ?
                      AND COALESCE(entry_source,'') = ?
                      AND direction IN ('LONG','SHORT')
                    ORDER BY entry_ts""",
                (_campaign_start(), src),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out
    if not rows:
        out["reason"] = "표본 없음"
        return out

    from collections import defaultdict
    merged = {}
    for r in rows:
        k = (r["entry_ts"], r["direction"], round(float(r["entry_price"] or 0.0), 2))
        m = merged.setdefault(k, {"pts_w": 0.0, "qty": 0, "exit_ts": r["exit_ts"]})
        q = int(r["quantity"] or 1)
        m["pts_w"] += float(r["pnl_pts"] or 0.0) * q
        m["qty"] += q
        if (r["exit_ts"] or "") > (m["exit_ts"] or ""):
            m["exit_ts"] = r["exit_ts"]

    earliest = min(k[0] for k in merged)[:10] + " 00:00:00"
    _, high_map, low_map = _load_candle_maps(earliest)

    def mfe(entry_ts, until_ts, ep, is_long):
        t = datetime.datetime.strptime(entry_ts[:19], _TS_FMT).replace(second=0)
        end = datetime.datetime.strptime(until_ts[:19], _TS_FMT).replace(second=0)
        best = 0.0
        seen = False
        while t <= end:
            t += datetime.timedelta(minutes=1)
            key = t.strftime(_TS_FMT)
            hi = high_map.get(key)
            lo = low_map.get(key)
            if hi is None or lo is None:
                continue
            seen = True
            fav = (hi - ep) if is_long else (ep - lo)
            if fav > best:
                best = fav
        return best if seen else None

    samples = []
    for (ets, d, ep), m in sorted(merged.items()):
        if not m["qty"]:
            continue
        realized = m["pts_w"] / m["qty"]
        is_long = d == "LONG"
        cutoff = ets[:10] + " 15:10:00"
        mfe_hold = mfe(ets, m["exit_ts"], ep, is_long)
        mfe_close = mfe(ets, cutoff, ep, is_long)
        samples.append({"ts": ets, "dir": d, "realized_pt": round(realized, 3),
                        "mfe_hold_pt": round(mfe_hold, 3) if mfe_hold is not None else None,
                        "mfe_close_pt": round(mfe_close, 3) if mfe_close is not None else None})

    out["n_entries"] = len(merged)
    out["n_rows_raw"] = len(rows)

    # [402차 후속5] 캡처율은 **비율의 평균이 아니라 풀링 비율**로 낸다.
    # 손실 거래는 분자가 음수인데 분모(MFE)가 0에 가까워 개별 비율이 폭발한다
    # (초안이 실제로 -672.9%를 출력했다). ΣRealized/ΣMFE는 그 특이점이 없다.
    # 아울러 pt 단위 "미실현 잔여(MFE-실현)"를 함께 낸다 — 비율보다 해석이 직관적이고
    # 합산이 되며, 애초에 F 제안이 물었던 "얼마나 흘렸나"에 직접 답한다.
    def pooled(key):
        pair = [(s["realized_pt"], s[key]) for s in samples
                if s[key] is not None and s[key] > 0]
        if not pair:
            return None, None, 0
        num = sum(p[0] for p in pair)
        den = sum(p[1] for p in pair)
        left = [p[1] - p[0] for p in pair]
        return (round(num / den, 4) if den else None,
                round(float(np.mean(left)), 3), len(pair))

    ch, lh, nh = pooled("mfe_hold_pt")
    cc, lc, nc = pooled("mfe_close_pt")
    out["capture_in_hold_pooled"] = ch
    out["avg_left_in_hold_pt"] = lh
    out["n_hold"] = nh
    out["capture_to_close_pooled"] = cc
    out["avg_left_to_close_pt"] = lc
    out["n_close"] = nc

    # 승리 거래만의 캡처율 — "이겼을 때 고점 대비 얼마나 챙겼나".
    # 손실 거래의 캡처율은 의미가 없으므로(음수/양수 비율) 분리해서 본다.
    win = [s for s in samples if s["realized_pt"] > 0 and s["mfe_close_pt"]]
    if win:
        out["capture_to_close_pooled_winners"] = round(
            sum(s["realized_pt"] for s in win) / sum(s["mfe_close_pt"] for s in win), 4)
        out["n_winners"] = len(win)

    _mh = [s["mfe_hold_pt"] for s in samples if s["mfe_hold_pt"] is not None]
    _mc = [s["mfe_close_pt"] for s in samples if s["mfe_close_pt"] is not None]
    if _mh:
        out["avg_mfe_hold_pt"] = round(float(np.mean(_mh)), 3)
    if _mc:
        out["avg_mfe_close_pt"] = round(float(np.mean(_mc)), 3)
    out["avg_realized_pt"] = (round(float(np.mean([s["realized_pt"] for s in samples])), 3)
                              if samples else None)
    # 상위 5건은 비율이 아니라 **잔여 pt**로 정렬 — 가장 많이 흘린 순
    out["most_left5"] = sorted(
        [s for s in samples if s["mfe_close_pt"] is not None],
        key=lambda s: -(s["mfe_close_pt"] - s["realized_pt"]))[:5]
    if nc < min_note:
        out["reason"] = ("표본 %d < %d — 참고 수치만 (관찰 채널이라 판정은 없음)"
                         % (nc, min_note))
    return out


# ──────────────────────────────────────────────────────────────
# [23] EOD 모델가드 판정 괴리 감시 (404차 신설)
# ──────────────────────────────────────────────────────────────

def eval_guard_shadow_channel(days: int) -> dict:
    """가드가 실제 판정에 쓰는 acc.txt 기준 결과(actual_verdict)와, old_acc_live
    (동일폴드 재측정) vs new(cv)의 공정비교 결과(fair_verdict)가 얼마나 자주
    어긋나는지 누적 판정한다(guard_shadow_log 테이블).

    missed_upgrade = fair_verdict가 REPLACE인데 actual_verdict가 HOLD인 행 —
    "공정비교로는 신모델이 나은데 acc.txt 때문에 가드가 구모델을 유지시킨" 경우.
    07-31 최초 라이브 관측(6개 호라이즌 중 3개, dev_memory/DECISION_LOG.md
    404차 항목)이 이 채널을 만든 계기이지만, PASS/FAIL 임계값은 그 단일일
    관측치에 맞추지 않고 독립적으로 고정했다(313차 원칙).
    """
    cr = VALIDATION_CAMPAIGN["guard_shadow"]
    out = {"verdict": "INSUFFICIENT", "n_samples": 0, "n_days": 0}
    cutoff = max(
        (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT),
        _campaign_start(),
    )
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT ts, horizon, acc_txt, old_acc_live, new_cv, live_note,
                          distortion, actual_verdict, fair_verdict
                     FROM guard_shadow_log
                    WHERE ts >= ? AND source = 'eod'
                    ORDER BY ts""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    out["n_samples"] = len(rows)
    out["n_days"] = len({r["ts"][:10] for r in rows})
    _live_fail = [r for r in rows if r["fair_verdict"] is None]
    out["n_live_measure_failed"] = len(_live_fail)

    fair_rows = [r for r in rows if r["fair_verdict"] is not None]
    if len(rows) < cr["min_samples"] or out["n_days"] < cr["min_days"]:
        out["reason"] = "표본 부족 (%d건/%d일 < %d건/%d일)" % (
            len(rows), out["n_days"], cr["min_samples"], cr["min_days"])
        return out
    if not fair_rows:
        out["reason"] = "공정비교 가능 표본 없음 (동일폴드 재측정 전부 실패)"
        return out

    missed = [r for r in fair_rows
              if r["fair_verdict"] == "REPLACE" and r["actual_verdict"] == "HOLD"]
    out["n_fair"] = len(fair_rows)
    out["missed_upgrade_n"] = len(missed)
    out["missed_upgrade_rate"] = round(len(missed) / len(fair_rows), 4)
    _dist = [r["distortion"] for r in fair_rows if r["distortion"] is not None]
    if _dist:
        out["mean_distortion"] = round(float(np.mean(_dist)), 4)

    by_hz = {}
    for r in fair_rows:
        b = by_hz.setdefault(r["horizon"], {"n": 0, "missed": 0})
        b["n"] += 1
        if r["fair_verdict"] == "REPLACE" and r["actual_verdict"] == "HOLD":
            b["missed"] += 1
    out["by_horizon"] = by_hz

    out["verdict"] = (
        "FAIL" if out["missed_upgrade_rate"] >= cr["missed_upgrade_rate_max"] else "PASS"
    )
    return out


# ──────────────────────────────────────────────────────────────
# [24] TP1 보호전환 반납 관찰 (404차 후속3) — verdict 항상 OBSERVE
# ──────────────────────────────────────────────────────────────

def eval_tp1_protect_giveback_watch() -> dict:
    """qty=1 TP1 보호전환에서 "장부이익 대비 실제로 얼마를 지켰는가"를 관찰한다.

    소스는 synthetic_partial_exits — 보호전환 시점의 TP1 장부이익(synthetic_pnl_pts)과
    보호스톱(stop_after)이 기록돼 있는데 **캠페인 소비처가 하나도 없어 방치돼 있었다**
    (402차 후속3 toxicity_block_shadow와 같은 계열의 사각지대).

    청산 기하 10개 차원 중 "보호전환 offset 폭"(차원 D)이 통째로 미계측이었고,
    이 채널이 그 눈을 뜬다. 처방(offset을 얼마로 할지) 검증은 [25]가 맡는다 —
    여기서는 판정하지 않는다(verdict 항상 OBSERVE).

    평균이 아니라 **중앙값**을 주 지표로 낸다: 0729 폭락일 2건이 평균을 5배 끌어올려
    "평균 반납 0.21pt(8%)"와 "중앙값 반납 1.00pt"가 정반대 인상을 준다(372차 원칙).
    """
    out = {"verdict": "OBSERVE"}
    try:
        with _conn(TRADES_DB) as conn:
            hooks = conn.execute(
                """SELECT ts, entry_ts, direction, entry_price, synthetic_price,
                          synthetic_pnl_pts, protect_mode, stop_after
                     FROM synthetic_partial_exits
                    WHERE ts >= ? ORDER BY ts""", (_campaign_start(),)).fetchall()
            rows = []
            for h in hooks:
                real = conn.execute(
                    """SELECT sum(pnl_pts*quantity)/sum(quantity) FROM trades
                        WHERE entry_ts = ? AND exit_ts IS NOT NULL""",
                    (h["entry_ts"],)).fetchone()[0]
                if real is None:
                    continue
                paper = float(h["synthetic_pnl_pts"] or 0.0)
                rows.append({
                    "ts": h["ts"], "mode": h["protect_mode"], "paper": paper,
                    "real": float(real), "give": paper - float(real),
                    "offset": abs(float(h["stop_after"]) - float(h["entry_price"])),
                })
    except Exception as e:
        out["error"] = str(e)
        return out

    out["n"] = len(rows)
    out["n_days"] = len({r["ts"][:10] for r in rows})
    if not rows:
        out["reason"] = "표본 없음"
        return out

    g = np.array([r["give"] for r in rows])
    o = np.array([r["offset"] for r in rows])
    p = np.array([r["paper"] for r in rows])
    out["n_gaveback"] = int((g > 0).sum())
    out["n_ranfurther"] = int((g < 0).sum())
    out["mean_give_pt"] = round(float(g.mean()), 4)
    out["median_give_pt"] = round(float(np.median(g)), 4)
    out["mean_paper_pt"] = round(float(p.mean()), 4)
    out["median_paper_pt"] = round(float(np.median(p)), 4)
    out["mean_offset_pt"] = round(float(o.mean()), 4)
    if np.median(p) > 0:
        out["median_giveback_rate"] = round(float(np.median(g) / np.median(p)), 4)
    if len(rows) > 2 and o.std() > 0 and g.std() > 0:
        out["offset_vs_give_corr"] = round(float(np.corrcoef(o, g)[0, 1]), 4)
    modes = {}
    for r in rows:
        modes[r["mode"]] = modes.get(r["mode"], 0) + 1
    out["by_mode"] = modes
    return out


# ──────────────────────────────────────────────────────────────
# [25] TP1 보호전환 offset A/B (404차 후속3) — 오프라인 스크립트 위임
# [23] TP1/손절 초기 기하 A/B (403차 P1-6) — 오프라인 스크립트 위임
# ──────────────────────────────────────────────────────────────

def eval_offline_geometry_channels() -> dict:
    """[404차 후속3, 23-B/25] 오프라인 A/B 스크립트 2종을 리포트에 편입한다.

    두 스크립트 모두 라이브 계측이 아니라 저장된 데이터 재생이라 리포트 생성
    시점에 그대로 호출하면 된다. 종전에는 별도 실행해야만 결과가 보여 주간회의
    에서 사실상 아무도 보지 않았다(§23은 403차 신설 이후 리포트 미노출).

    스크립트 실패가 리포트 전체를 죽이면 안 되므로 각각 격리한다.
    """
    out = {}
    for key, mod in (("tp1_geometry_shadow", "scripts.tp1_geometry_shadow"),
                     ("tp1_protect_offset_shadow", "scripts.tp1_protect_offset_shadow")):
        try:
            import importlib
            m = importlib.import_module(mod)
            out[key] = m.summarize(m.compute(_campaign_start()[:10]))
        except Exception as e:
            out[key] = {"verdict": "INSUFFICIENT", "error": "%s: %s" % (type(e).__name__, e)}
    return out


def eval_intraday_cv_watch(days: int) -> dict:
    """[404차 후속] intraday 계측 CV(source='intraday') 관찰 — 판정 없음.

    mfe_capture_watch·exit_fill_slippage_watch와 동일한 순수 관찰 채널이다.
    실측(dev_memory/DECISION_LOG.md 404차 후속 §1): 동일 데이터·시드만 다른
    재현 분산이 5m 기준 8.83%p로 EOD 가드 허용폭(2.5%p)의 3.5배 — 이 채널의
    수치로 자동 게이트를 걸면 신호가 아니라 모델 재현 잡음을 판정하게 된다.
    지금은 "intraday cv_acc가 실제로 하락 추세인가"를 판단할 표본을 쌓는
    용도로만 쓴다. 다음 결정(게이트 도입 여부)은 이 관찰이 최소 수 주 쌓인
    뒤 사람이 내린다(§9).
    """
    out = {"verdict": "OBSERVE", "n_samples": 0, "n_days": 0}
    cutoff = max(
        (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT),
        _campaign_start(),
    )
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT ts, horizon, old_acc_live, new_cv, distortion, fair_verdict
                     FROM guard_shadow_log
                    WHERE ts >= ? AND source = 'intraday'
                    ORDER BY ts""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    out["n_samples"] = len(rows)
    out["n_days"] = len({r["ts"][:10] for r in rows})
    if not rows:
        out["reason"] = "표본 없음"
        return out

    by_hz = {}
    for r in rows:
        b = by_hz.setdefault(r["horizon"], {"cv": [], "dist": [], "hold_n": 0})
        b["cv"].append(r["new_cv"])
        if r["distortion"] is not None:
            b["dist"].append(r["distortion"])
        if r["fair_verdict"] == "HOLD":
            b["hold_n"] += 1

    out["by_horizon"] = {
        hz: {
            "n": len(v["cv"]),
            "mean_cv": round(float(np.mean(v["cv"])), 4),
            "std_cv": round(float(np.std(v["cv"])), 4) if len(v["cv"]) > 1 else None,
            "mean_distortion": round(float(np.mean(v["dist"])), 4) if v["dist"] else None,
            # fair_would_hold: "EOD처럼 가드를 걸었다면 통과 못 했을" 비율 — 참고용,
            # 판정 아님(§1 실측: 이 신호 자체가 시드 재현 잡음에 파묻혀 있음).
            "fair_would_hold_rate": round(v["hold_n"] / len(v["cv"]), 4),
        }
        for hz, v in by_hz.items()
    }
    return out


# ──────────────────────────────────────────────────────────────
# [20] BAR_ONLY_RELAX 수용/롤백 감시 (402차 후속)
# ──────────────────────────────────────────────────────────────

# 401차 커밋(2026-07-29 16:26)이 장 마감 후라 발효는 다음 세션부터.
BAR_ONLY_RELAX_EFFECTIVE_DATE = "2026-07-30"


def eval_weight_collapse_watch(days: int) -> dict:
    """BAR_ONLY_RELAX 활성화(401차)의 효과·부작용을 일자 단위로 감시한다.

    fast_reversal_watch·exit_fill_slippage_watch와 동일한 관찰 계열 —
    자동으로 롤백하지 않고 판정 문구만 노출한다(§9 사전등록 원칙).

    효과 지표는 `ensemble_decisions.weight_collapsed` 일별 비율,
    부작용 지표는 완화 대상 호라이즌(3m/5m)의 일별 방향 적중률이다.
    Q3(2026-06-25)가 bar_only로 막으려던 "학습/추론 분포 불일치"가 실제로
    해를 끼치면 그 두 호라이즌 적중률에 먼저 나타난다.

    주의: `weight_collapsed`는 398차(2026-07-28 저녁) 배포분부터 기록되므로,
    그 이전 일자는 컬럼이 NULL이다 — "collapse 0건"이 아니라 "미계측"이라
    집계에서 제외한다. 완화 전 기준선이 단일일(2026-07-29)뿐이라는 뜻이므로
    판정에 min_days를 둔다(313차 원칙).
    """
    cfg = VALIDATION_CAMPAIGN.get("weight_collapse_watch", {})
    out = {"verdict": "OBSERVE", "effective_date": BAR_ONLY_RELAX_EFFECTIVE_DATE}
    min_days = int(cfg.get("min_days", 3))
    target = float(cfg.get("target_ratio", 0.20))
    tol = float(cfg.get("target_tolerance", 0.07))
    ineff = float(cfg.get("ineffective_ratio_min", 0.40))
    over = float(cfg.get("overrelax_ratio_max", 0.05))
    floors = dict(cfg.get("hz_acc_floor", {}))
    streak_need = int(cfg.get("regression_streak_days", 3))
    since = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")

    daily = {}
    try:
        with _conn(PREDICTIONS_DB) as conn:
            for r in conn.execute(
                """SELECT substr(ts,1,10) d, COUNT(*) n,
                          SUM(CASE WHEN weight_collapsed IS NULL THEN 1 ELSE 0 END) n_null,
                          SUM(COALESCE(weight_collapsed,0)) n_wc
                     FROM ensemble_decisions
                    WHERE substr(ts,1,10) >= ?
                    GROUP BY d ORDER BY d""", (since,)
            ):
                n_meas = int(r["n"]) - int(r["n_null"])
                if n_meas <= 0:
                    continue          # 미계측일 — 집계 제외
                daily[r["d"]] = {"n": n_meas, "wc": int(r["n_wc"]),
                                 "ratio": float(r["n_wc"]) / n_meas, "acc": {}}
            for r in conn.execute(
                """SELECT substr(ts,1,10) d, horizon, AVG(CAST(correct AS FLOAT)) acc,
                          COUNT(*) n
                     FROM predictions
                    WHERE substr(ts,1,10) >= ? AND correct IS NOT NULL
                      AND horizon IN ('3m','5m')
                    GROUP BY d, horizon""", (since,)
            ):
                if r["d"] in daily:
                    daily[r["d"]]["acc"][r["horizon"]] = round(float(r["acc"]), 4)
    except Exception as e:
        out["error"] = str(e)
        return out

    pre = {d: v for d, v in daily.items() if d < BAR_ONLY_RELAX_EFFECTIVE_DATE}
    post = {d: v for d, v in daily.items() if d >= BAR_ONLY_RELAX_EFFECTIVE_DATE}
    out["n_days_pre"] = len(pre)
    out["n_days_post"] = len(post)
    out["baseline_ratio"] = (round(sum(v["ratio"] for v in pre.values()) / len(pre), 4)
                             if pre else None)
    out["daily"] = {d: {"ratio": round(v["ratio"], 4), "n": v["n"], "acc": v["acc"]}
                    for d, v in sorted(daily.items())}

    if len(post) < min_days:
        out["reason"] = ("완화 후 계측일 %d일 < 최소 %d일 — 판정 보류 (발효 %s)"
                         % (len(post), min_days, BAR_ONLY_RELAX_EFFECTIVE_DATE))
        out["verdict"] = "INSUFFICIENT"
        return out

    mean_post = sum(v["ratio"] for v in post.values()) / len(post)
    out["post_ratio"] = round(mean_post, 4)

    if mean_post >= ineff:
        effect = "INEFFECTIVE"
    elif mean_post <= over:
        effect = "OVER_RELAXED"
    elif abs(mean_post - target) <= tol:
        effect = "ON_TARGET"
    else:
        effect = "OFF_TARGET"
    out["effect"] = effect

    regressed = []
    for hz, floor in sorted(floors.items()):
        streak = worst = 0
        for d in sorted(post):
            a = post[d]["acc"].get(hz)
            if a is None:
                streak = 0
                continue
            if a < float(floor):
                streak += 1
                worst = max(worst, streak)
            else:
                streak = 0
        if worst >= streak_need:
            regressed.append("%s %d일연속<%.0f%%" % (hz, worst, float(floor) * 100))
    out["regressed"] = regressed

    if regressed:
        out["verdict"] = "ROLLBACK_REVIEW"
        out["recommendation"] = (
            "Q3 분포 불일치 부작용 의심(%s) — `BAR_ONLY_RELAX_ENABLED=False` 롤백을 "
            "주간회의에서 검토(즉시 자동 롤백 아님)" % " / ".join(regressed))
    elif effect == "ON_TARGET":
        out["verdict"] = "ACCEPT"
        out["recommendation"] = "효과 목표 구간·부작용 없음 — 완화 존치 수용"
    elif effect == "INEFFECTIVE":
        out["verdict"] = "INVESTIGATE"
        out["recommendation"] = (
            "완화가 듣지 않음(%.1f%% ≥ %.1f%%) — 원인이 bar age가 아닐 가능성. "
            "롤백보다 원인 재조사 우선" % (mean_post * 100, ineff * 100))
    return out


# ──────────────────────────────────────────────────────────────
# [19] ToxicityGate action="block" counterfactual — resolve + 누적 판정 (신설)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_toxicity_block() -> dict:
    """toxicity_block_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.
    resolve_and_eval_open_gap()과 완전히 동일한 로직 — 대상 테이블만 다르다.

    PASS = 게이트 존치 (차단된 신호가 실제로 손실 방향이었거나 완화 기준 미충족).
    FAIL = 재설계 검토 권고 — block_threshold(0.45)가 그때의 실측 toxicity_score
    분포와 맞는지 재검토 착수(즉시 완화 금지, §9 사전등록 원칙).
    """
    cr = VALIDATION_CAMPAIGN["toxicity_block_shadow"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM toxicity_block_shadow WHERE resolved = 0 ORDER BY ts"
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
                # 동시 터치 → 보수적으로 STOP 우선 (open_gap_shadow와 동일 관례)
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
            # hyp_pnl_pts: (+) = 차단 안 했으면 이득이었다(재설계 근거), (-) = 차단이 손실 회피
            hyp = (cf_price - entry_p) if is_long else (entry_p - cf_price)
            updates.append((cf_outcome, cf_price, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE toxicity_block_shadow
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
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither,
                          AVG(toxicity_score) AS avg_score, AVG(toxicity_score_ma) AS avg_score_ma
                   FROM toxicity_block_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM toxicity_block_shadow WHERE resolved=0"
            ).fetchone()["n"]
            baseline = conn.execute(
                """SELECT AVG(CASE WHEN COALESCE(net_pnl_krw, pnl_krw) > 0
                                   THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades WHERE exit_ts IS NOT NULL AND exit_ts >= ?""",
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
        "avg_toxicity_score": round(float(agg["avg_score"] or 0.0), 4),
        "avg_toxicity_score_ma": round(float(agg["avg_score_ma"] or 0.0), 4),
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
            "ToxicityGate block_threshold(0.45) 재검토 권고 — 실측 toxicity_score "
            "분포 근거로 임계값 재보정 착수 (즉시 완화 금지, §9 사전등록 원칙)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [18] RegimeExhaustionGate counterfactual — resolve + 판정 (379차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_regime_exhaustion() -> dict:
    """regime_exhaustion_shadow(main.py에서 기록) resolve + 판정.

    hurst_gate_shadow·open_gap_shadow와 resolve 메커니즘은 동일(발동 시점의
    가상 진입가·스톱·TP1이 cf_window_min 이내에 무엇에 먼저 닿았는지)이나,
    이 채널은 "게이트가 이미 차단 중인데 그게 옳았나"가 아니라 "탈진 반전
    가설 자체가 유효한가"를 묻는 것이라 PASS/FAIL 의미가 반대로 뒤집힌다:

    hyp_pnl_pts = 신호 방향(연장·추격 방향)으로 갔을 때의 결과.
      (+) = 신호 방향이 맞았음(탈진이 아니라 진짜 추세 지속) → 가설 반증 쪽.
      (-) = 신호 방향이 반전(스톱)에 먼저 닿음 → "탈진 반전" 가설 지지.

    SUPPORTS_GATE = 누적 hyp_pnl_pts가 유의하게 음수(왕복비용의 2배 이상 손실)
      — 이 방향으로 계속 갔으면 평균적으로 손해였다는 뜻. REGIME_EXHAUSTION_
      GATE_ENABLED 전환(등급 강등) 또는 3-2 제안(반대방향 신규 시그널)의 근거로
      쌓인다. 단 이 리포트는 권고만 — 즉시 자동 전환 없음(§9 사전등록 원칙).
    REJECTS_GATE = 누적 hyp_pnl_pts가 유의하게 양수 — 신호가 오히려 방향을
      맞췄다는 뜻. 가설 기각, 게이트 개발 중단 권고.
    OBSERVE = 표본은 충분하나 방향이 애매(왕복비용 2배 미만) — 계속 관찰.
    """
    cr = VALIDATION_CAMPAIGN["regime_exhaustion_watch"]
    window_min = int(cr.get("cf_window_min", 30))
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM regime_exhaustion_shadow WHERE resolved = 0 ORDER BY ts"
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
                if hit_stop:
                    cf_outcome, cf_price = "STOP", stop_p
                    break
                if hit_tp:
                    cf_outcome, cf_price = "TP1", tp1_p
                    break
            if cf_price is None:
                if last_close is None:
                    continue
                cf_price = last_close
            entry_p = float(r["entry_price"])
            hyp = (cf_price - entry_p) if is_long else (entry_p - cf_price)
            updates.append((cf_outcome, cf_price, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE regime_exhaustion_shadow
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
                          SUM(CASE WHEN cf_outcome='STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='TP1' THEN 1 ELSE 0 END) AS n_tp1,
                          SUM(CASE WHEN cf_outcome='NEITHER' THEN 1 ELSE 0 END) AS n_neither,
                          AVG(ext_atr_60m) AS avg_ext60m, AVG(hurst) AS avg_hurst,
                          SUM(chase_failed) AS n_chase_failed,
                          SUM(countertrend_failed) AS n_ctr_failed
                   FROM regime_exhaustion_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM regime_exhaustion_shadow WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "cf_stop": int(agg["n_stop"] or 0),
        "cf_tp1": int(agg["n_tp1"] or 0),
        "cf_neither": int(agg["n_neither"] or 0),
        "avg_ext_atr_60m": round(float(agg["avg_ext60m"] or 0.0), 3),
        "avg_hurst": round(float(agg["avg_hurst"] or 0.0), 3),
        "n_chase_failed": int(agg["n_chase_failed"] or 0),
        "n_countertrend_failed": int(agg["n_ctr_failed"] or 0),
    })
    if n < int(cr["min_samples"]):
        out["verdict"] = "INSUFFICIENT"
        out["reason"] = "표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    if total_hyp < -cost_pt * 2.0:
        out["verdict"] = "SUPPORTS_GATE"
        out["recommendation"] = (
            "탈진 반전 가설 지지 — REGIME_EXHAUSTION_GATE_ENABLED 전환(등급 강등) 또는 "
            "반대방향 신규 진입 시그널(3-2 제안) 개발을 주간회의에서 검토 (§9 사전등록 원칙 — "
            "즉시 자동 전환 금지)"
        )
    elif total_hyp > cost_pt * 2.0:
        out["verdict"] = "REJECTS_GATE"
        out["recommendation"] = "가설 기각 — 신호 방향이 오히려 우세, 게이트 개발 중단 권고"
    else:
        out["verdict"] = "OBSERVE"
    return out


# ──────────────────────────────────────────────────────────────
# [10] TP2 홀드 A/B counterfactual — resolve + 누적 판정 (361차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_tp2_hold() -> dict:
    """tp2_hold_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.

    0720 정기점검 "TP3 도달 0건" 딥다이브 결과: 원인은 트레일링 폭이 아니라
    qty=2 스테이지 배분(TP2에서 잔량 1계약 전량 종료, TP3 몫이 항상 0)이었음.
    이 채널은 그 순간 "홀드했다면 TP3/트레일링까지 갔을 때 어땠을지"를 당일
    15:10까지 분봉으로 사후 시뮬레이션한다. 트레일링 티어는
    strategy.position.position_tracker.compute_trailing_stop_tier()를 그대로
    재사용(라이브 로직과 동일 소스, 드리프트 방지). ATR은 훅 시점 값을 고정
    사용(단순화 — 봉별 ATR 재계산은 하지 않음), 가상 트레일링 anchor는 TP1 이후
    상태를 정확히 재현하지 않고 TP2 시점부터 entry_price 기준으로 새로 시작한다
    (둘 다 §3-5류 채널들의 "고정 스톱/TP 기준" 단순화와 동일 원칙).

    PASS = 현행(TP2 전량종료) 유지 — 홀드가 평균적으로 손해.
    FAIL = 재배분(TP1만 정리 후 TP3/트레일링까지 보유) 채택 검토 권고
           (즉시 코드 변경 아님 — 주간회의 수동 결정, §9 사전등록 원칙).
    """
    cr = VALIDATION_CAMPAIGN["tp2_hold_shadow"]
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM tp2_hold_shadow WHERE resolved = 0 ORDER BY ts"
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
            day_end = base.replace(hour=15, minute=10, second=0, microsecond=0)
            if now < day_end + datetime.timedelta(minutes=2):
                continue  # 당일 장 마감까지 아직 안 지남 — 다음 실행에서 재시도
            is_long = str(r["direction"]) == "LONG"
            direction = "LONG" if is_long else "SHORT"
            entry_p = float(r["entry_price"])
            tp3_p = float(r["tp3_price"] or 0.0)
            atr = float(r["atr_at_hook"] or 0.0)

            anchor = entry_p
            stop = float(r["stop_price_at_hook"] or entry_p)
            cf_outcome, cf_price, cf_minutes = None, None, 0
            last_close, last_m = None, 0
            m = 0
            while True:
                m += 1
                mid = base + datetime.timedelta(minutes=m)
                if mid.time() > datetime.time(15, 10):
                    break
                mid_ts = mid.strftime(_TS_FMT)
                hi = high_map.get(mid_ts)
                lo = low_map.get(mid_ts)
                cl = close_map.get(mid_ts)
                if hi is None or lo is None or cl is None:
                    continue
                last_close, last_m = cl, m
                # 라이브와 동일하게 매분 종가로만 트레일링 1회 갱신
                anchor, stop = compute_trailing_stop_tier(
                    entry_p, direction, atr, cl, anchor, stop
                )
                hit_tp3 = tp3_p > 0 and (hi >= tp3_p if is_long else lo <= tp3_p)
                hit_stop = lo <= stop if is_long else hi >= stop
                # 동시 터치 → 보수적으로 STOP 우선 (기존 섀도 채널들과 동일 관례)
                if hit_stop:
                    cf_outcome, cf_price, cf_minutes = "TRAIL_STOP", stop, m
                    break
                if hit_tp3:
                    cf_outcome, cf_price, cf_minutes = "TP3", tp3_p, m
                    break
            if cf_price is None:
                if last_close is None:
                    continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                cf_outcome, cf_price, cf_minutes = "FORCE_EXIT", last_close, last_m
            tp2_p = float(r["tp2_price"])
            # hyp_pnl_pts: (+) = 홀드가 이득(재배분 근거), (-) = TP2 조기청산이 나았음
            hyp = (cf_price - tp2_p) if is_long else (tp2_p - cf_price)
            updates.append((cf_outcome, cf_price, cf_minutes, round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE tp2_hold_shadow
                       SET resolved=1, cf_outcome=?, cf_exit_price=?,
                           cf_hold_minutes=?, hyp_pnl_pts=?
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
                          SUM(CASE WHEN cf_outcome='TP3' THEN 1 ELSE 0 END) AS n_tp3,
                          SUM(CASE WHEN cf_outcome='TRAIL_STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='FORCE_EXIT' THEN 1 ELSE 0 END) AS n_force
                   FROM tp2_hold_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM tp2_hold_shadow WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
        "cf_tp3": int(agg["n_tp3"] or 0),
        "cf_trail_stop": int(agg["n_stop"] or 0),
        "cf_force_exit": int(agg["n_force"] or 0),
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "TP2 전량종료 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    adopt = total_hyp > cost_pt * 2.0
    out["verdict"] = "FAIL" if adopt else "PASS"
    if adopt:
        out["recommendation"] = (
            "qty=2 스테이지 재배분(TP1만 정리 후 TP3/트레일링까지 보유) 채택 검토 "
            "— 주간회의 수동 결정 (§9 사전등록 원칙)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [11] qty=1 손실1차(Loss Tier1) 조기청산 counterfactual — resolve + 누적 판정 (363차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_loss_tier1_qty1_shadow() -> dict:
    """loss_tier1_qty1_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.

    0721 정기점검 딥다이브: is_loss_tier1_hit()가 qty<=1을 물리적 분할 불가로 원천
    제외해, qty=1 손실 포지션은 entry~stop 절반 지점을 지나도 아무 조치 없이 최종
    손절가까지 그대로 노출된다. tp2_hold_shadow와 달리 이 채널은 실제 포지션이
    그대로 진행되므로 candle 시뮬레이션이 필요 없다 — 실거래(trades 테이블)가
    최종적으로 낸 pnl_pts를 entry_ts 근사 조인(±10초, 체결보정 타이밍 오차 흡수)으로
    가져와 "그 시점에 tier1가에서 전량 조기청산했다면"과 그대로 대조한다.

    hyp_pnl_pts = tier1 조기청산 pt − 실제 실현 pt (양수 = 조기청산이 유리했음).
    PASS = 현행(qty=1 조기청산 없음) 유지 — 조기청산이 평균적으로 이득 아님.
    FAIL = qty=1 조기청산 정책 채택 검토 권고 (즉시 코드 변경 아님 — 주간회의 수동
           결정, §9 사전등록 원칙 — hurst_gate_shadow·open_gap_shadow와 동일 순서).

    [363차 후속, 0721 딥다이브 제안3 편입] 진입 시점 quantile 기대엣지/불확실성
    (main.py:_ts_execute_entry가 캡처)도 함께 저장돼, edge_ratio(=|expected_pt|/
    uncertainty_pt)와 실현 pnl_pts의 스피어만 상관을 보조 지표로 보고한다 — 이
    상관 자체는 PASS/FAIL 게이트가 아니라 참고용(§9와 동일 원칙, 표본이 쌓인 뒤
    등급/사이징 강화 여부는 사람이 별도 판단).
    """
    cr = VALIDATION_CAMPAIGN["loss_tier1_qty1_shadow"]
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM loss_tier1_qty1_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        updates = []
        with _conn(TRADES_DB) as conn:
            for r in unresolved:
                # entry_ts 근사 조인(±10초) — position.entry_time(섀도 기록 시각 기준)과
                # trades.entry_ts(체결보정 후 확정)가 완전히 동일하지 않을 수 있음.
                match = conn.execute(
                    """SELECT pnl_pts FROM trades
                       WHERE direction = ?
                         AND ABS((julianday(entry_ts) - julianday(?)) * 86400) <= 10
                         AND exit_ts IS NOT NULL
                       ORDER BY ABS((julianday(entry_ts) - julianday(?)) * 86400)
                       LIMIT 1""",
                    (r["direction"], r["entry_ts"], r["entry_ts"]),
                ).fetchone()
                if match is None:
                    continue  # 실거래가 아직 청산 전 — 다음 실행에서 재시도
                actual_pnl = float(match["pnl_pts"] or 0.0)
                is_long = str(r["direction"]) == "LONG"
                entry_p = float(r["entry_price"])
                tier1_p = float(r["loss_tier1_price"])
                tier1_cut_pts = (tier1_p - entry_p) if is_long else (entry_p - tier1_p)
                hyp = tier1_cut_pts - actual_pnl
                updates.append((round(actual_pnl, 4), round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE loss_tier1_qty1_shadow
                       SET resolved=1, actual_pnl_pts=?, hyp_pnl_pts=?
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
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win
                   FROM loss_tier1_qty1_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM loss_tier1_qty1_shadow WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
    })

    # [363차 후속, §11-보조] quantile 기대엣지/불확실성 비율 vs 실현 pnl 상관 —
    # 정책 게이트 아님, 참고용 상관관계만 보고한다. "체크리스트/메타 등급과 무관하게
    # edge_ratio가 낮았던 진입이 실제로도 더 나쁜 결과를 냈는가"(0721 딥다이브 관찰)를
    # 표본이 쌓이는 대로 실측 확인 — 등급/사이징 강화 여부는 이 상관이 충분히 쌓인
    # 뒤 별도로 사람이 판단(§9와 동일 원칙, 이 값 자체가 자동으로 아무것도 바꾸지 않음).
    try:
        with _conn(TRADES_DB) as conn:
            edge_rows = conn.execute(
                """SELECT quantile_expected_pt AS exp_pt, quantile_uncertainty_pt AS unc_pt,
                          actual_pnl_pts AS pnl
                   FROM loss_tier1_qty1_shadow
                   WHERE resolved=1 AND ts >= ?
                     AND quantile_expected_pt IS NOT NULL
                     AND quantile_uncertainty_pt IS NOT NULL
                     AND quantile_uncertainty_pt > 0""",
                (_campaign_start(),),
            ).fetchall()
    except Exception:
        edge_rows = []
    edge_ratios = [abs(float(r["exp_pt"])) / float(r["unc_pt"]) for r in edge_rows]
    edge_pnls = [float(r["pnl"]) for r in edge_rows]
    out["n_edge_samples"] = len(edge_ratios)
    if len(edge_ratios) >= 10:
        _ec = _spearman(edge_ratios, edge_pnls)
        out["edge_uncertainty_corr"] = None if np.isnan(_ec) else round(_ec, 4)
        out["edge_ratio_mean"] = round(float(np.mean(edge_ratios)), 4)

    if n < int(cr["min_samples"]):
        out["reason"] = "tier1 터치 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    adopt = total_hyp > cost_pt * 2.0
    out["verdict"] = "FAIL" if adopt else "PASS"
    if adopt:
        out["recommendation"] = (
            "qty=1 손실1차 조기청산 정책 채택 검토 — 주간회의 수동 결정 (§9 사전등록 원칙)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [14] Tier1 발동 후 잔여계약 2단계 조기청산 counterfactual — resolve + 누적 판정 (367차)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_loss_tier2_remainder_shadow() -> dict:
    """loss_tier2_remainder_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.

    loss_tier1_qty1_shadow와 동일한 패턴이나, 조인 대상이 "원 포지션 전체"가 아니라
    "Tier1 이후 남은 잔여계약의 최종 청산 레그"다 — Tier1 체결 시 trades 테이블에
    별도 행(exit_reason='손절1차 조기축소')이 하나 생기고, 잔여계약은 그 뒤 별도
    행으로 최종 청산되므로 그 행만 골라 조인한다(direction+entry_ts+quantity로
    특정, tier1 레그 자체는 exit_reason으로 제외).

    hyp_pnl_pts = tier2가 조기청산 pt − 실제(잔여계약) 실현 pt (양수=조기청산 유리).
    PASS = 현행(잔여계약 추가조치 없음) 유지 — 조기청산이 평균적으로 이득 아님.
    FAIL = 잔여계약 2단계 조기청산 정책 채택 검토 권고 (즉시 코드 변경 아님 —
           주간회의 수동 결정, §9 사전등록 원칙 — loss_tier1_qty1_shadow와 동일 순서).
    """
    cr = VALIDATION_CAMPAIGN["loss_tier2_remainder_shadow"]
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM loss_tier2_remainder_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        updates = []
        with _conn(TRADES_DB) as conn:
            for r in unresolved:
                match = conn.execute(
                    """SELECT pnl_pts FROM trades
                       WHERE direction = ? AND quantity = ?
                             AND exit_reason != '손절1차 조기축소'
                             AND ABS((julianday(entry_ts) - julianday(?)) * 86400) <= 10
                             AND exit_ts IS NOT NULL
                       ORDER BY ABS((julianday(entry_ts) - julianday(?)) * 86400)
                       LIMIT 1""",
                    (r["direction"], r["remaining_qty"], r["entry_ts"], r["entry_ts"]),
                ).fetchone()
                if match is None:
                    continue  # 잔여계약이 아직 청산 전 — 다음 실행에서 재시도
                actual_pnl = float(match["pnl_pts"] or 0.0)
                is_long = str(r["direction"]) == "LONG"
                entry_p = float(r["entry_price"])
                tier2_p = float(r["loss_tier2_price"])
                # entry_price는 원 포지션 진입가 — tier2_cut_pts는 "그 진입가 기준"
                # 실현 pt와 같은 기준(entry_price 대비)으로 맞춰야 actual_pnl(마찬가지로
                # trades.pnl_pts, entry_price 기준)과 동일 척도로 비교 가능.
                tier2_cut_pts = (tier2_p - entry_p) if is_long else (entry_p - tier2_p)
                hyp = tier2_cut_pts - actual_pnl
                updates.append((round(actual_pnl, 4), round(hyp, 4), r["id"]))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE loss_tier2_remainder_shadow
                       SET resolved=1, actual_pnl_pts=?, hyp_pnl_pts=?
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
                          SUM(CASE WHEN hyp_pnl_pts > 0 THEN 1 ELSE 0 END) AS n_win
                   FROM loss_tier2_remainder_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM loss_tier2_remainder_shadow WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
    })

    if n < int(cr["min_samples"]):
        out["reason"] = "tier2 터치 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    adopt = total_hyp > cost_pt * 2.0
    out["verdict"] = "FAIL" if adopt else "PASS"
    if adopt:
        out["recommendation"] = (
            "잔여계약 2단계 조기청산 정책 채택 검토 — 주간회의 수동 결정 (§9 사전등록 원칙)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [15] 급행 풀스톱(TP1 미도달) 관찰 채널 (367차, 관찰 전용 — PASS/FAIL 판정 없음)
# ──────────────────────────────────────────────────────────────

def eval_fast_reversal_watch(days: int) -> dict:
    """하드스톱 청산 중 (a) 보유시간이 짧고(fast_exit_max_sec 이내) (b) TP1 보호전환이
    한 번도 발동하지 않은 포지션의 등급별 발생률·손익을 집계한다.

    0722 정기점검 딥다이브(4주 9건 사례, -2,161,020원 — A등급 4주 누적손실의 84%)에서
    발견한 패턴을 지속 관찰하기 위한 채널. GradeEVGuard·loss_tier1_qty1_shadow처럼
    거래가 완결돼야 표본이 쌓이는 채널과 달리, "TP1 도달 여부"는 로그에서 직접 읽을
    수 있어 정책 게이트 없이도 등급별 추세를 빠르게 볼 수 있다.

    PASS/FAIL 판정을 내리지 않는다 — 이 패턴 자체를 "차단"할 기존 메커니즘이 없어
    (즉 완화 정책이 아직 없어) 판정이 의미가 없기 때문. 순수 관찰용 — kelly_skip·
    grade_ev_inversion과 달리 verdict는 항상 "OBSERVE"로 고정.
    """
    fast_max_sec = int(VALIDATION_CAMPAIGN["fast_reversal_watch"]["fast_exit_max_sec"])
    out = {"verdict": "OBSERVE", "fast_exit_max_sec": fast_max_sec}
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT)

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT entry_ts, exit_ts, direction, grade, quantity,
                          pnl_pts, net_pnl_krw
                   FROM trades
                   WHERE entry_ts >= ? AND exit_ts IS NOT NULL
                         AND exit_reason LIKE '%하드스톱%'""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    candidates = []
    for r in rows:
        try:
            t0 = datetime.datetime.strptime(r["entry_ts"], _TS_FMT)
            t1 = datetime.datetime.strptime(r["exit_ts"], _TS_FMT)
        except (TypeError, ValueError):
            continue
        hold_sec = (t1 - t0).total_seconds()
        if hold_sec <= fast_max_sec:
            candidates.append((r, hold_sec))

    out["n_fast_hardstop"] = len(candidates)
    if not candidates:
        out["reason"] = "관찰 대상(급행 하드스톱) 0건"
        return out

    # TP1 도달 여부 — 같은 날짜의 TRADE.log에서 entry_ts~exit_ts 구간에 "TP1"
    # 문자열이 등장하는지 확인(main.py가 TP1 보호전환/부분청산 시 항상 이 문자열을
    # 남김 — synthetic_tp1(qty=1)·실제 부분청산(qty>=2) 모두 커버).
    by_date = {}
    for r, hold_sec in candidates:
        date_key = r["entry_ts"][:10].replace("-", "")
        by_date.setdefault(date_key, []).append((r, hold_sec))

    log_dir = os.path.join(ROOT, "logs")
    by_grade = {}
    for date_key, items in by_date.items():
        log_path = os.path.join(log_dir, f"{date_key}_TRADE.log")
        try:
            with open(log_path, encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            lines = None  # 로그 유실 — TP1 판정 불가로 보수적으로 "도달함" 취급(과다경보 방지)
        for r, hold_sec in items:
            reached_tp1 = True
            if lines is not None:
                reached_tp1 = any(
                    r["entry_ts"] <= ln[:19] <= r["exit_ts"] and "TP1" in ln
                    for ln in lines
                )
            if reached_tp1:
                continue  # TP1 도달 후 짧게 청산된 건 이 채널의 관심사가 아님(정상 동작)
            g = (r["grade"] or "?") or "?"
            slot = by_grade.setdefault(g, {"n": 0, "total_pnl_krw": 0.0, "n_loss": 0})
            slot["n"] += 1
            slot["total_pnl_krw"] += float(r["net_pnl_krw"] or 0.0)
            if float(r["net_pnl_krw"] or 0.0) < 0:
                slot["n_loss"] += 1

    out["by_grade"] = {
        g: {
            "n": v["n"],
            "total_pnl_krw": round(v["total_pnl_krw"], 0),
            "n_loss": v["n_loss"],
        }
        for g, v in by_grade.items()
    }
    out["n_no_tp1"] = sum(v["n"] for v in by_grade.values())
    return out


# [16] chase+foreign 조합 관찰 채널 (368차, 관찰 전용 — PASS/FAIL 판정 없음)
def eval_chase_foreign_combo_watch() -> dict:
    """10_chase(연장추격)와 6_foreign(외인 옵션 수급) 두 체크리스트 항목이 동시에
    실패(나머지 항목 무관)한 진입의 등급별 발생률·손익을 집계한다.

    0722 정기점검 딥다이브(MW0601 실측): 09:32~09:53 21분 사이 이 조합(나머지 9개
    항목 전부 통과)이 3회 발화해 3회 전부 하드스톱(-536,097원, 그날 최대
    손실뭉치 -742,800원의 72%). trades.db에 체크리스트 개별 항목이 저장되지
    않아 fast_reversal_watch(367차)와 동일 방식으로 entry_ts를 키 삼아
    TRADE.log의 [진입체크] 라인과 매칭한다.

    CHASE_FOREIGN_COMBO_GUARD_ENABLED(섀도) 판정 근거 표본 축적용 — 아직
    이 조합을 강등할 정책이 섀도 단계라 PASS/FAIL 판정은 하지 않는다
    (fast_reversal_watch와 동일 원칙). verdict는 항상 OBSERVE로 고정.
    """
    days = int(VALIDATION_CAMPAIGN["chase_foreign_combo_watch"]["lookback_days"])
    out = {"verdict": "OBSERVE", "lookback_days": days}
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT)

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT entry_ts, exit_ts, direction, grade, quantity,
                          pnl_pts, net_pnl_krw
                   FROM trades
                   WHERE entry_ts >= ? AND exit_ts IS NOT NULL""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    by_date = {}
    for r in rows:
        date_key = r["entry_ts"][:10].replace("-", "")
        by_date.setdefault(date_key, []).append(r)

    log_dir = os.path.join(ROOT, "logs")
    by_grade = {}
    n_matched = 0
    for date_key, items in by_date.items():
        log_path = os.path.join(log_dir, f"{date_key}_TRADE.log")
        try:
            with open(log_path, encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            continue  # 로그 유실 — 이 채널은 관찰용이라 보수적 취급 없이 스킵

        entry_lines = [ln for ln in lines if "[진입체크]" in ln]
        for r in items:
            # entry_ts는 [Position]체결 시각(초 단위로 [진입체크]보다 0~수초 늦음) —
            # 정확히 같은 초가 아닐 수 있어 직전 5초 이내 가장 가까운 [진입체크] 채택.
            try:
                r_dt = datetime.datetime.strptime(r["entry_ts"][:19], _TS_FMT)
            except (TypeError, ValueError):
                continue
            match, best_diff = None, None
            for ln in entry_lines:
                try:
                    ln_dt = datetime.datetime.strptime(ln[:19], _TS_FMT)
                except ValueError:
                    continue
                diff = (r_dt - ln_dt).total_seconds()
                if 0 <= diff <= 5 and (best_diff is None or diff < best_diff):
                    match, best_diff = ln, diff
            if match is None:
                continue
            n_matched += 1
            if "chas❌" in match and "fore❌" in match:
                g = (r["grade"] or "?") or "?"
                slot = by_grade.setdefault(g, {"n": 0, "total_pnl_krw": 0.0, "n_loss": 0})
                slot["n"] += 1
                slot["total_pnl_krw"] += float(r["net_pnl_krw"] or 0.0)
                if float(r["net_pnl_krw"] or 0.0) < 0:
                    slot["n_loss"] += 1

    out["n_matched"] = n_matched
    out["by_grade"] = {
        g: {"n": v["n"], "total_pnl_krw": round(v["total_pnl_krw"], 0), "n_loss": v["n_loss"]}
        for g, v in by_grade.items()
    }
    out["n_combo"] = sum(v["n"] for v in by_grade.values())
    out["total_pnl_krw"] = round(sum(v["total_pnl_krw"] for v in by_grade.values()), 0)
    if out["n_combo"] == 0:
        out["reason"] = "관찰 대상(chase+foreign 동시 실패) 0건"
    return out


# [17] 청산 주문 체결 슬리피지 관찰 채널 (369차, 관찰 전용 — PASS/FAIL 판정 없음)
def eval_exit_fill_slippage_watch(days: int) -> dict:
    """청산 주문의 의도가(price_hint)와 실체결가(fill_price) 괴리를 청산 사유별로
    집계한다(exit_fill_slippage 테이블, main.py::_ts_record_exit_fill_slippage()).

    0723 정기점검 딥다이브 계기: TP1 ATR보호전환(+0.35pt 확정 예정)이 하드스톱(틱)
    체결 슬리피지(주문가 1122.49 → 체결가 1122.12, 0.37pt≈18틱 불리)로 순손실
    (-0.02pt)로 뒤집힌 사례를 발견했으나, VALIDATION_CAMPAIGN 전 채널의 왕복비용
    계산이 가정하는 slippage_ticks_per_side(=1.0, 0.02pt)이 실측과 맞는지 검증할
    데이터가 그때까지 전혀 없었다.

    fast_reversal_watch·chase_foreign_combo_watch와 동일 원칙 — 이 실측치로
    slippage_ticks_per_side를 "즉시 자동 재보정"하지 않는다(캠페인 전 채널의
    공통 가정이므로 바꾸려면 §3 사전등록 원칙에 따라 검증 시계 리셋이 필요).
    verdict는 항상 OBSERVE로 고정, min_samples_for_note 이상 쌓이면 재보정
    검토가 필요하다는 note만 노출한다.
    """
    days_cfg = VALIDATION_CAMPAIGN.get("exit_fill_slippage_watch", {})
    min_note = int(days_cfg.get("min_samples_for_note", 20))
    out = {"verdict": "OBSERVE", "assumed_ticks_per_side": float(
        VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))}
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(_TS_FMT)

    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT reason, slippage_pts FROM exit_fill_slippage
                   WHERE ts >= ?""",
                (cutoff,),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    out["n"] = len(rows)
    if not rows:
        out["reason"] = "체결 슬리피지 기록 0건"
        return out

    vals = [float(r["slippage_pts"]) for r in rows]
    out["avg_slippage_pts"] = round(sum(vals) / len(vals), 4)
    out["max_slippage_pts"] = round(max(vals), 4)
    out["assumed_slippage_pts_per_side"] = round(
        out["assumed_ticks_per_side"] * TICK_SIZE, 4)

    by_reason = {}
    for r in rows:
        reason = str(r["reason"] or "?") or "?"
        slot = by_reason.setdefault(reason, {"n": 0, "sum_pts": 0.0})
        slot["n"] += 1
        slot["sum_pts"] += float(r["slippage_pts"])
    out["by_reason"] = {
        k: {"n": v["n"], "avg_pts": round(v["sum_pts"] / v["n"], 4)}
        for k, v in by_reason.items()
    }

    if out["n"] >= min_note and out["avg_slippage_pts"] > out["assumed_slippage_pts_per_side"]:
        out["note"] = (
            f"실측 평균슬리피지({out['avg_slippage_pts']:.3f}pt)가 캠페인 가정"
            f"({out['assumed_slippage_pts_per_side']:.3f}pt)을 초과 — "
            f"slippage_ticks_per_side 재보정 여부를 주간회의에서 검토할 가치 있음"
            f"(§3 사전등록 원칙 — 즉시 자동 변경 금지)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# [12] qty=1 TP1 이후 트레일 폭 counterfactual — resolve + 누적 판정 (363차 후속)
# ──────────────────────────────────────────────────────────────

def resolve_and_eval_tp1_trail_shadow() -> dict:
    """tp1_trail_shadow(main.py에서 기록) resolve + PASS/FAIL 판정.

    0721 정기점검 딥다이브 제안4 편입 — 361차 tp2_hold_shadow와 동일한 패턴·판정
    로직이며 트레일링 시뮬레이션도 같은 순수함수(compute_trailing_stop_tier)를
    재사용한다(단일 소스 유지, 라이브 로직과 계측 시뮬레이션 드리프트 방지).
    qty=1은 TP1 이후 update_trailing_stop() 4단계 트레일링 대신 static ATR-lock
    1회 보호전환만 받는데, "그때부터 qty=2와 동일한 4단계 트레일링을 계속 적용
    했다면" 당일 15:10까지 분봉으로 사후 시뮬레이션하고, 실거래(trades 테이블)가
    최종적으로 낸 pnl_pts를 entry_ts 근사 조인(±10초, loss_tier1_qty1_shadow와
    동일 방식)으로 가져와 그대로 대조한다 — anchor 시작값은 tp2_hold_shadow의
    "entry_price로 단순화"와 달리 훅 시점에 이미 도달이 확인된 tp1_price를 사용
    (아는 값을 굳이 버릴 이유가 없음, stop 시작값은 실제 적용된 static lock).

    hyp_pnl_pts = (4단계 트레일링 지속 시뮬레이션 pt) − (실제 실현 pt).
    PASS = 현행(static lock) 유지 — 트레일링 지속이 평균적으로 이득 아님.
    FAIL = qty=1도 4단계 트레일링 적용 채택 검토 권고 (즉시 코드 변경 아님 —
           주간회의 수동 결정, §9 사전등록 원칙 — tp2_hold_shadow와 동일 순서).
    """
    cr = VALIDATION_CAMPAIGN["tp1_trail_shadow"]
    out = {"verdict": "INSUFFICIENT", "resolved_now": 0}

    try:
        with _conn(TRADES_DB) as conn:
            unresolved = conn.execute(
                "SELECT * FROM tp1_trail_shadow WHERE resolved = 0 ORDER BY ts"
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    if unresolved:
        earliest = min(r["ts"] for r in unresolved)
        close_map, high_map, low_map = _load_candle_maps(earliest)
        now = datetime.datetime.now()
        updates = []
        with _conn(TRADES_DB) as conn:
            for r in unresolved:
                base = datetime.datetime.strptime(r["ts"], _TS_FMT)
                day_end = base.replace(hour=15, minute=10, second=0, microsecond=0)
                if now < day_end + datetime.timedelta(minutes=2):
                    continue  # 당일 장 마감까지 아직 안 지남 — 다음 실행에서 재시도
                # 실거래 실현 pnl 먼저 확인 — entry_ts 근사 조인(±10초)
                match = conn.execute(
                    """SELECT pnl_pts FROM trades
                       WHERE direction = ?
                         AND ABS((julianday(entry_ts) - julianday(?)) * 86400) <= 10
                         AND exit_ts IS NOT NULL
                       ORDER BY ABS((julianday(entry_ts) - julianday(?)) * 86400)
                       LIMIT 1""",
                    (r["direction"], r["entry_ts"], r["entry_ts"]),
                ).fetchone()
                if match is None:
                    continue  # 실거래가 아직 청산 전 — 다음 실행에서 재시도
                actual_pnl = float(match["pnl_pts"] or 0.0)

                is_long = str(r["direction"]) == "LONG"
                direction = "LONG" if is_long else "SHORT"
                entry_p = float(r["entry_price"])
                atr = float(r["atr_at_hook"] or 0.0)
                anchor = float(r["tp1_price"])
                stop = float(r["protect_stop_at_hook"])
                cf_outcome, cf_price, cf_minutes = None, None, 0
                last_close, last_m = None, 0
                m = 0
                while True:
                    m += 1
                    mid = base + datetime.timedelta(minutes=m)
                    if mid.time() > datetime.time(15, 10):
                        break
                    mid_ts = mid.strftime(_TS_FMT)
                    hi = high_map.get(mid_ts)
                    lo = low_map.get(mid_ts)
                    cl = close_map.get(mid_ts)
                    if hi is None or lo is None or cl is None:
                        continue
                    last_close, last_m = cl, m
                    anchor, stop = compute_trailing_stop_tier(
                        entry_p, direction, atr, cl, anchor, stop
                    )
                    hit_stop = lo <= stop if is_long else hi >= stop
                    if hit_stop:
                        cf_outcome, cf_price, cf_minutes = "TRAIL_STOP", stop, m
                        break
                if cf_price is None:
                    if last_close is None:
                        continue  # 분봉 데이터 자체가 없음 — 다음 실행에서 재시도
                    cf_outcome, cf_price, cf_minutes = "FORCE_EXIT", last_close, last_m
                cf_pnl = (cf_price - entry_p) if is_long else (entry_p - cf_price)
                hyp = cf_pnl - actual_pnl
                updates.append((
                    round(actual_pnl, 4), cf_outcome, round(cf_price, 4),
                    cf_minutes, round(hyp, 4), r["id"],
                ))

        if updates:
            with _conn(TRADES_DB) as conn:
                conn.executemany(
                    """UPDATE tp1_trail_shadow
                       SET resolved=1, actual_pnl_pts=?, cf_outcome=?, cf_exit_price=?,
                           cf_hold_minutes=?, hyp_pnl_pts=?
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
                          SUM(CASE WHEN cf_outcome='TRAIL_STOP' THEN 1 ELSE 0 END) AS n_stop,
                          SUM(CASE WHEN cf_outcome='FORCE_EXIT' THEN 1 ELSE 0 END) AS n_force
                   FROM tp1_trail_shadow WHERE resolved=1 AND ts >= ?""",
                (_campaign_start(),),
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) AS n FROM tp1_trail_shadow WHERE resolved=0"
            ).fetchone()["n"]
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(agg["n"] or 0)
    total_hyp = float(agg["total_hyp"] or 0.0)
    avg_price = float(agg["avg_price"] or 0.0) or 300.0
    win_rate = (int(agg["n_win"] or 0) / n) if n else 0.0
    out.update({
        "n_resolved": n,
        "n_pending": int(pending),
        "total_hyp_pnl_pts": round(total_hyp, 4),
        "win_rate": round(win_rate, 4),
        "cf_trail_stop": int(agg["n_stop"] or 0),
        "cf_force_exit": int(agg["n_force"] or 0),
    })
    if n < int(cr["min_samples"]):
        out["reason"] = "TP1 보호전환 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    cost_pt = _roundtrip_cost_pt(avg_price)
    out["cost_pt"] = round(cost_pt, 4)
    adopt = total_hyp > cost_pt * 2.0
    out["verdict"] = "FAIL" if adopt else "PASS"
    if adopt:
        out["recommendation"] = (
            "qty=1도 4단계 트레일링(update_trailing_stop) 적용 채택 검토 "
            "— 주간회의 수동 결정 (§9 사전등록 원칙)"
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
# [8] KellyAdvisedSkip × C등급 누적 성과 — 게이트 승격 검토 (341차 신설)
# ──────────────────────────────────────────────────────────────

def eval_kelly_skip_grade_c() -> dict:
    """켈리(PositionSizer)가 "자본 대비 1계약도 부적절"이라 판단했는데
    (kelly_advised_skip=1) MINI_MIN_CONTRACTS 최소수량 강제로 그대로 체결된
    C등급 트레이드의 누적 성과를 4주 단위로 판정한다.

    signal_decay·hurst_gate_shadow·joint_gate_shadow와 달리 실제로 체결된
    진입(exec_1m_shadow·synthetic_partial_exits와 동일 계열)이므로
    counterfactual 시뮬레이션이 불필요 — trades 테이블의 실현 net_pnl_krw를
    그대로 집계하면 된다.

    PASS = 현행 유지 (C+KellySkip 조합이 특별히 나쁘지 않음, 또는 표본 부족).
    FAIL = 4주 누적 순손실 확정 → C등급+KellySkip 조합 진입 차단(사이징 0 또는
    등급 강등)을 단계 도입 검토 — 즉시 자동 차단이 아니라 권고만 출력(§9 원칙).
    """
    cr = VALIDATION_CAMPAIGN["kelly_skip"]
    out = {"verdict": "INSUFFICIENT"}
    try:
        with _conn(TRADES_DB) as conn:
            target = conn.execute(
                """SELECT COUNT(*) AS n,
                          SUM(net_pnl_krw) AS total_pnl,
                          AVG(net_pnl_krw) AS avg_pnl,
                          AVG(CASE WHEN net_pnl_krw > 0 THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades
                   WHERE exit_ts >= ? AND net_pnl_krw IS NOT NULL
                         AND grade = 'C' AND kelly_advised_skip = 1""",
                (_campaign_start(),),
            ).fetchone()
            baseline = conn.execute(
                """SELECT COUNT(*) AS n,
                          AVG(net_pnl_krw) AS avg_pnl,
                          AVG(CASE WHEN net_pnl_krw > 0 THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades
                   WHERE exit_ts >= ? AND net_pnl_krw IS NOT NULL
                         AND grade = 'C' AND COALESCE(kelly_advised_skip, 0) = 0""",
                (_campaign_start(),),
            ).fetchone()
            grade_split = conn.execute(
                """SELECT COALESCE(NULLIF(grade,''),'?') AS grade, COUNT(*) AS n,
                          SUM(net_pnl_krw) AS total_pnl,
                          AVG(CASE WHEN net_pnl_krw > 0 THEN 1.0 ELSE 0.0 END) AS wr
                   FROM trades
                   WHERE exit_ts >= ? AND net_pnl_krw IS NOT NULL
                         AND kelly_advised_skip = 1
                   GROUP BY grade""",
                (_campaign_start(),),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    n = int(target["n"] or 0)
    total_pnl = float(target["total_pnl"] or 0.0)
    base_n = int(baseline["n"] or 0)
    base_avg = float(baseline["avg_pnl"] or 0.0) if base_n else None
    base_wr = float(baseline["wr"] or 0.0) if base_n else None

    out.update({
        "n": n,
        "total_pnl_krw": round(total_pnl, 0),
        "avg_pnl_krw": round(float(target["avg_pnl"] or 0.0), 0),
        "win_rate": round(float(target["wr"] or 0.0), 4),
        "baseline_n": base_n,
        "baseline_avg_pnl_krw": round(base_avg, 0) if base_avg is not None else None,
        "baseline_win_rate": round(base_wr, 4) if base_wr is not None else None,
        "grade_split": {
            row["grade"]: {
                "n": int(row["n"] or 0),
                "total_pnl_krw": round(float(row["total_pnl"] or 0.0), 0),
                "win_rate": round((int(row["n"] or 0) and float(row["wr"] or 0.0)), 4),
            }
            for row in grade_split
        },
    })

    if n < int(cr["min_samples"]):
        out["reason"] = "C등급+KellySkip 표본 부족 (%d < %d) — 판정 보류" % (n, cr["min_samples"])
        return out

    out["verdict"] = "FAIL" if total_pnl < 0 else "PASS"
    if out["verdict"] == "FAIL":
        out["recommendation"] = (
            "C등급+KellySkip 조합 누적 순손실 확정 — 진입 차단(사이징 0 또는 등급 "
            "강등) 단계 도입 검토 (§9 사전등록 원칙에 따라 적용은 수동 결정)"
        )
    return out


def eval_grade_ev_inversion() -> dict:
    """[366차 신설] §13 등급별 순EV 역전 감시 — A등급(체크리스트 pass_count≥6)의
    누적 순EV가 C등급보다 낮은 "역전" 현상을 캠페인 시작일 이후 누적 판정한다.

    kelly_skip과 동일 계열 — 실제로 체결된 진입(trades 테이블)이므로
    counterfactual 시뮬레이션이 불필요. 0722 정기점검 딥다이브에서 A등급 평균
    신뢰도(37.4%)가 C등급(35.9%)과 거의 동일한데도 순EV는 정반대(A 음수·C
    양수)임을 확인 — 신뢰도가 아니라 체크리스트 pass_count(등급) 자체가
    실현 엣지와 반비례하는 구조적 문제로 진단.

    PASS = A등급 평균 순EV ≥ 0 (역전 해소 또는 애초에 미발생).
    FAIL = A등급 평균 순EV < 0 이고 A/C 모두 표본 충분 → GradeEVGuard
    (config.settings.GRADE_EV_GUARD_ENABLED) 활성화를 주간회의에서 검토
    (§9 사전등록 원칙 — 즉시 자동 적용 아님).
    """
    cr = VALIDATION_CAMPAIGN["grade_ev_inversion"]
    out = {"verdict": "INSUFFICIENT"}
    try:
        with _conn(TRADES_DB) as conn:
            rows = conn.execute(
                """SELECT COALESCE(NULLIF(grade,''),'?') AS grade,
                          COALESCE(net_pnl_krw, pnl_krw) AS pnl
                   FROM trades
                   WHERE exit_ts >= ? AND grade IN ('A','B','C')""",
                (_campaign_start(),),
            ).fetchall()
    except Exception as e:
        out["error"] = str(e)
        return out

    # [367차, 제안4 편입] min(최대손실)·표준편차 보강 — 평균만으로는 "고르게 나쁨"과
    # "소수 초대형 손실이 평균을 끌어내리는 fat-tail"을 구분할 수 없다(0722 딥다이브:
    # A등급 4주 손실의 84%가 급행 풀스톱 9건에 집중). SQLite에 STDEV가 없어 Python에서
    # 계산 — numpy(이미 상단에서 import).
    from collections import defaultdict
    pnl_by_grade = defaultdict(list)
    for row in rows:
        pnl_by_grade[row["grade"]].append(float(row["pnl"] or 0.0))

    by_grade = {}
    for g, pnls in pnl_by_grade.items():
        arr = np.array(pnls, dtype=float)
        by_grade[g] = {
            "n": len(pnls),
            "avg_pnl_krw": round(float(arr.mean()), 0),
            "total_pnl_krw": round(float(arr.sum()), 0),
            "win_rate": round(float((arr > 0).mean()), 4),
            "min_pnl_krw": round(float(arr.min()), 0),
            "stdev_pnl_krw": round(float(arr.std(ddof=1)) if len(pnls) > 1 else 0.0, 0),
        }
    out["by_grade"] = by_grade

    min_n = int(cr["min_samples_per_grade"])
    a = by_grade.get("A")
    c = by_grade.get("C")
    if not a or a["n"] < min_n or not c or c["n"] < min_n:
        _a_n = a["n"] if a else 0
        _c_n = c["n"] if c else 0
        out["reason"] = (
            "등급별 표본 부족 (A=%d, C=%d, 각각 %d 필요) — 판정 보류" %
            (_a_n, _c_n, min_n)
        )
        return out

    out["verdict"] = "FAIL" if a["avg_pnl_krw"] < 0 else "PASS"
    if out["verdict"] == "FAIL":
        out["recommendation"] = (
            "A등급 누적 순EV 음수 확정(C등급은 양수) — GradeEVGuard "
            "(config.settings.GRADE_EV_GUARD_ENABLED) 활성화를 주간회의에서 검토"
            " (§9 사전등록 원칙에 따라 적용은 수동 결정)"
        )
    return out


# ──────────────────────────────────────────────────────────────
# 리포트 생성
# ──────────────────────────────────────────────────────────────

def _fmt_verdict(v: str) -> str:
    return {
        "PASS": "✅ PASS", "FAIL": "❌ FAIL",
        "OK": "✅ OK", "STARVED": "🚨 STARVED",
        "OBSERVE": "👁 OBSERVE",  # [367차] 순수 관찰 채널(정책 게이트 없음) — PASS/FAIL 미판정
        # [379차] RegimeExhaustionGate 전용 — 하드 차단이 없어 PASS/FAIL 대신 가설
        # 지지/기각으로 표기(resolve_and_eval_regime_exhaustion() 참조)
        "SUPPORTS_GATE": "🔶 SUPPORTS_GATE",
        "REJECTS_GATE": "🔷 REJECTS_GATE",
    }.get(v, "⏳ INSUFFICIENT")


def _fmt_channel_verdict(out: dict) -> str:
    """[357차] INSUFFICIENT(표본 축적 대기)와 NO-DATA(소스 적재 자체가 0 — 계측
    사망 의심)를 구분 표기. [2]/[3] 채널이 스코어러 로드 실패로 캠페인 전 기간
    표본 0이었는데 '표본 부족'으로만 표시돼 2주간 발견되지 못한 재발 방지.
    판정값(metrics json의 verdict)은 사전등록 어휘 그대로 유지 — 표시만 구분."""
    if out.get("no_data"):
        return "🔴 NO-DATA(계측 점검 필요)"
    return _fmt_verdict(out.get("verdict", ""))


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
    ks = eval_kelly_skip_grade_c()
    og = resolve_and_eval_open_gap()
    txb = resolve_and_eval_toxicity_block()
    t2 = resolve_and_eval_tp2_hold()
    lt1 = resolve_and_eval_loss_tier1_qty1_shadow()
    t1t = resolve_and_eval_tp1_trail_shadow()
    gei = eval_grade_ev_inversion()
    lt2 = resolve_and_eval_loss_tier2_remainder_shadow()
    frw = eval_fast_reversal_watch(days)
    cfc = eval_chase_foreign_combo_watch()
    efs = eval_exit_fill_slippage_watch(days)
    reg = resolve_and_eval_regime_exhaustion()
    wcw = eval_weight_collapse_watch(days)
    dev = eval_direction_ev_watch()
    mcw = eval_mfe_capture_watch()
    gsc = eval_guard_shadow_channel(days)
    icw = eval_intraday_cv_watch(days)
    tpg = eval_tp1_protect_giveback_watch()
    off = eval_offline_geometry_channels()

    metrics = {
        "generated_at": now_str,
        "days": days,
        "criteria": VALIDATION_CAMPAIGN,
        "sample_starvation": ss,
        "tb": tb, "meta_gate": mg, "quantile": qt,
        "signal_decay": sd, "hurst_regime": hr, "hurst_gate_shadow": hg,
        "joint_gate_shadow": jg, "kelly_skip": ks, "open_gap_shadow": og,
        "tp2_hold_shadow": t2, "loss_tier1_qty1_shadow": lt1,
        "tp1_trail_shadow": t1t, "grade_ev_inversion": gei,
        "loss_tier2_remainder_shadow": lt2, "fast_reversal_watch": frw,
        "chase_foreign_combo_watch": cfc, "exit_fill_slippage_watch": efs,
        "regime_exhaustion_watch": reg, "toxicity_block_shadow": txb,
        "weight_collapse_watch": wcw,
        "direction_ev_watch": dev, "mfe_capture_watch": mcw,
        "guard_shadow": gsc, "intraday_cv_watch": icw,
        "tp1_protect_giveback_watch": tpg,
        "tp1_geometry_shadow": off.get("tp1_geometry_shadow"),
        "tp1_protect_offset_shadow": off.get("tp1_protect_offset_shadow"),
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
        _fmt_channel_verdict(mg), mg.get("top_ev_pt", "—"),
        mg.get("separation_pt", "—"), mg.get("required_sep_pt", "—")))
    L.append("| [3] 분위 회귀 | %s | 커버리지=%s (밴드 %s) 상관=%s |" % (
        _fmt_channel_verdict(qt), qt.get("coverage", "—"),
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
    L.append("| [8] KellyAdvisedSkip×C등급 | %s | 누적 순PnL=%s원 승률=%s (n=%s) |" % (
        _fmt_verdict(ks["verdict"]),
        format(ks["total_pnl_krw"], ",.0f") if "total_pnl_krw" in ks else "—",
        ("%.1f%%" % (ks["win_rate"] * 100)) if "win_rate" in ks else "—",
        ks.get("n", 0)))
    L.append("| [9] OPEN_VOLATILE 시가이격 counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s) |" % (
        _fmt_verdict(og["verdict"]), og.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (og["win_rate"] * 100)) if "win_rate" in og else "—",
        og.get("n_resolved", 0), og.get("n_pending", 0)))
    L.append("| [10] TP2 홀드 counterfactual (qty=2 재배분 A/B) | %s | 누적 hyp=%spt 승률=%s "
              "(n=%s, 보류 %s) TP3=%s건 트레일=%s건 강제청산=%s건 |" % (
        _fmt_verdict(t2["verdict"]), t2.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (t2["win_rate"] * 100)) if "win_rate" in t2 else "—",
        t2.get("n_resolved", 0), t2.get("n_pending", 0),
        t2.get("cf_tp3", "—"), t2.get("cf_trail_stop", "—"), t2.get("cf_force_exit", "—")))
    L.append("| [11] qty=1 손실1차 조기청산 counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s) |" % (
        _fmt_verdict(lt1["verdict"]), lt1.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (lt1["win_rate"] * 100)) if "win_rate" in lt1 else "—",
        lt1.get("n_resolved", 0), lt1.get("n_pending", 0)))
    L.append("| [12] qty=1 TP1 이후 트레일 폭 counterfactual | %s | 누적 hyp=%spt 승률=%s "
              "(n=%s, 보류 %s) 트레일스톱=%s건 강제청산=%s건 |" % (
        _fmt_verdict(t1t["verdict"]), t1t.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (t1t["win_rate"] * 100)) if "win_rate" in t1t else "—",
        t1t.get("n_resolved", 0), t1t.get("n_pending", 0),
        t1t.get("cf_trail_stop", "—"), t1t.get("cf_force_exit", "—")))
    _gei_a = gei.get("by_grade", {}).get("A", {})
    _gei_c = gei.get("by_grade", {}).get("C", {})
    L.append("| [13] 등급별 순EV 역전 감시 | %s | A=%s원(n=%s, 최대손실=%s원) C=%s원(n=%s) |" % (
        _fmt_verdict(gei["verdict"]),
        format(_gei_a["avg_pnl_krw"], ",.0f") if _gei_a else "—", _gei_a.get("n", 0),
        format(_gei_a["min_pnl_krw"], ",.0f") if _gei_a else "—",
        format(_gei_c["avg_pnl_krw"], ",.0f") if _gei_c else "—", _gei_c.get("n", 0)))
    L.append("| [14] Tier1 잔여계약 2단계 조기청산 counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s) |" % (
        _fmt_verdict(lt2["verdict"]), lt2.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (lt2["win_rate"] * 100)) if "win_rate" in lt2 else "—",
        lt2.get("n_resolved", 0), lt2.get("n_pending", 0)))
    _frw_a = frw.get("by_grade", {}).get("A", {})
    L.append("| [15] 급행 풀스톱(TP1 미도달) 관찰 | %s | 급행하드스톱=%s건 중 TP1미도달=%s건"
              " (A: n=%s 누적=%s원) |" % (
        _fmt_verdict(frw["verdict"]),
        frw.get("n_fast_hardstop", 0), frw.get("n_no_tp1", 0),
        _frw_a.get("n", 0),
        format(_frw_a["total_pnl_krw"], ",.0f") if _frw_a else "—"))
    L.append("| [16] chase+foreign 조합 관찰 | %s | 동시실패=%s건 누적=%s원 (매칭=%s건) |" % (
        _fmt_verdict(cfc["verdict"]),
        cfc.get("n_combo", 0),
        format(cfc["total_pnl_krw"], ",.0f") if cfc.get("n_combo") else "—",
        cfc.get("n_matched", 0)))
    L.append("| [17] 청산 체결 슬리피지 관찰 | %s | n=%s 평균=%spt (가정 %spt) |" % (
        _fmt_verdict(efs["verdict"]),
        efs.get("n", 0),
        efs.get("avg_slippage_pts", "—"),
        efs.get("assumed_slippage_pts_per_side", "—")))
    L.append("| [18] RegimeExhaustionGate(탈진반전) | %s | 발동=%s건 누적hyp=%spt "
              "(STOP=%s/TP1=%s/NEITHER=%s) |" % (
        _fmt_verdict(reg["verdict"]),
        reg.get("n_resolved", 0),
        reg.get("total_hyp_pnl_pts", "—"),
        reg.get("cf_stop", 0), reg.get("cf_tp1", 0), reg.get("cf_neither", 0)))
    L.append("| [19] ToxicityGate block counterfactual | %s | 누적 hyp=%spt 승률=%s (n=%s, 보류 %s) |" % (
        _fmt_verdict(txb["verdict"]), txb.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (txb["win_rate"] * 100)) if "win_rate" in txb else "—",
        txb.get("n_resolved", 0), txb.get("n_pending", 0)))
    L.append("| [20] BAR_ONLY_RELAX 수용/롤백 | %s | 완화후 collapse=%s (기준선 %s, 목표 %.0f%%±%.0f%%p) 계측일 전%s/후%s |" % (
        _fmt_verdict(wcw["verdict"]),
        ("%.1f%%" % (wcw["post_ratio"] * 100)) if wcw.get("post_ratio") is not None else "—",
        ("%.1f%%" % (wcw["baseline_ratio"] * 100)) if wcw.get("baseline_ratio") is not None else "—",
        float(VALIDATION_CAMPAIGN.get("weight_collapse_watch", {}).get("target_ratio", 0.20)) * 100,
        float(VALIDATION_CAMPAIGN.get("weight_collapse_watch", {}).get("target_tolerance", 0.07)) * 100,
        wcw.get("n_days_pre", 0), wcw.get("n_days_post", 0)))
    _dv = dev.get("by_direction", {})
    L.append("| [21] 방향별 순EV (SYSTEM_AUTO) | %s | %s |" % (
        _fmt_verdict(dev["verdict"]),
        " / ".join("%s: n=%d 평균=%s원 최대손실=%s원" % (
            d, _dv[d]["n"], format(_dv[d]["avg_pnl_krw"], ",.0f"),
            format(_dv[d]["min_pnl_krw"], ",.0f"))
            for d in ("LONG", "SHORT") if d in _dv) or "표본 없음"))
    L.append("| [22] MFE 캡처율 관찰 | %s | 풀링캡처 보유내=%s 종가까지=%s / 평균잔여 %s pt (진입 %s건) |" % (
        _fmt_verdict(mcw["verdict"]),
        ("%.1f%%" % (mcw["capture_in_hold_pooled"] * 100)) if mcw.get("capture_in_hold_pooled") is not None else "—",
        ("%.1f%%" % (mcw["capture_to_close_pooled"] * 100)) if mcw.get("capture_to_close_pooled") is not None else "—",
        mcw.get("avg_left_to_close_pt", "—"), mcw.get("n_entries", 0)))
    L.append("| [23] EOD 모델가드 판정 괴리 | %s | missed_upgrade=%s (n=%s/%s, %d일) |" % (
        _fmt_channel_verdict(gsc),
        ("%.1f%%" % (gsc["missed_upgrade_rate"] * 100)) if gsc.get("missed_upgrade_rate") is not None else "—",
        gsc.get("missed_upgrade_n", "—"), gsc.get("n_fair", "—"), gsc.get("n_days", 0)))
    _g23 = off.get("tp1_geometry_shadow") or {}
    _g25 = off.get("tp1_protect_offset_shadow") or {}
    L.append("| [23-B] TP1/손절 초기 기하 A/B | %s | %s (진입 %s건/%s일) |" % (
        _fmt_verdict(_g23.get("verdict", "")), _g23.get("reason", _g23.get("error", "—")),
        _g23.get("n_trades", "—"), _g23.get("n_days", "—")))
    L.append("| [24] TP1 보호전환 반납 관찰 | %s | 중앙값 반납=%s pt (반납 %s / 달림 %s, n=%s) |" % (
        _fmt_verdict(tpg.get("verdict", "OBSERVE")),
        tpg.get("median_give_pt", "—"), tpg.get("n_gaveback", "—"),
        tpg.get("n_ranfurther", "—"), tpg.get("n", 0)))
    L.append("| [25] TP1 보호전환 offset A/B | %s | %s (전환 %s건/%s일) |" % (
        _fmt_verdict(_g25.get("verdict", "")), _g25.get("reason", _g25.get("error", "—")),
        _g25.get("n_hooks", "—"), _g25.get("n_days", "—")))
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
        _status = r.get("status", "—")
        if r.get("carried"):
            _status = "%s (유지, %s 판정)" % (_status, str(r.get("judged_at", ""))[:10])
        L.append("| %s | %s | %s | %s | %s | %s |" % (
            hz, _status, r.get("ic_tb", "—"), r.get("ic_3class", "—"),
            r.get("n_samples", "—"), r.get("reason", "")))
    if tb.get("error"):
        L.append("")
        L.append("> ⚠ %s" % tb["error"])
    L.append("")
    L.append("> [357차 해석 확정] 1m은 앙상블 가중치 영구 0 퇴역(331차 후속2) 상태 —")
    L.append("> 1m이 IC 기준을 합격해도 \"1m 앙상블 복귀\"가 아니라 1m 활용방안 A·C")
    L.append("> (331차 후속3, 섀도우 경로)의 근거로만 사용한다. **실질 승격 검토 대상은")
    L.append("> 3m/5m로 한정** (30m은 296차 퇴역). 합격선 자체는 불변 — 해석만 확정")
    L.append("> (시계 리셋 불요).")
    L.append("> [384차] 383차가 규명한 구조결함(평가창이 매주 재학습으로 리셋돼 5m~30m이")
    L.append("> min_samples_hz 영구 미달) 해법 적용 — 이제 호라이즌별 실제 OOS n이")
    L.append("> min_samples_hz에 도달한 주에만 신선하게 판정하고, 그 아래 주는 `tb_verdict_log`의")
    L.append("> 최근 판정을 그대로 유지(위 표의 \"(유지, YYYY-MM-DD 판정)\")한다. 10m/15m/30m은")
    L.append("> 판정 주기 자체가 몇 주~십수 주 단위로 길 뿐 표본은 끊기지 않고 계속 누적된다.")
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

    # [8] KellyAdvisedSkip × C등급 상세
    L.append("## [8] KellyAdvisedSkip × C등급 누적 성과 (341차 신설)")
    L.append("")
    L.append("- C등급+KellySkip 체결 n=%s | 누적 순PnL=%s원 | 평균=%s원 | 승률=%s" % (
        ks.get("n", 0),
        format(ks["total_pnl_krw"], ",.0f") if "total_pnl_krw" in ks else "—",
        format(ks["avg_pnl_krw"], ",.0f") if "avg_pnl_krw" in ks else "—",
        ("%.1f%%" % (ks["win_rate"] * 100)) if "win_rate" in ks else "—",
    ))
    if ks.get("baseline_n"):
        L.append("- 비교(C등급, KellySkip 아님) n=%s | 평균=%s원 | 승률=%s" % (
            ks["baseline_n"],
            format(ks["baseline_avg_pnl_krw"], ",.0f") if ks.get("baseline_avg_pnl_krw") is not None else "—",
            ("%.1f%%" % (ks["baseline_win_rate"] * 100)) if ks.get("baseline_win_rate") is not None else "—",
        ))
    if ks.get("grade_split"):
        L.append("- 등급별(KellySkip=1 전체, 참고용):")
        for grade, v in sorted(ks["grade_split"].items()):
            L.append("  - %s급: n=%d 누적PnL=%s원 승률=%.1f%%" % (
                grade, v["n"], format(v["total_pnl_krw"], ",.0f"), v["win_rate"] * 100))
    if ks.get("recommendation"):
        L.append("- **권고**: %s" % ks["recommendation"])
    if ks.get("reason"):
        L.append("- %s" % ks["reason"])
    L.append("")

    # [9] OPEN_VOLATILE 시가이격 counterfactual 상세
    L.append("## [9] OPEN_VOLATILE 시가이격 counterfactual (§14, 354차)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        og.get("resolved_now", 0), og.get("n_resolved", 0), og.get("n_pending", 0)))
    L.append("- counterfactual 분포: STOP %s / TP1 %s / NEITHER %s" % (
        og.get("cf_stop", 0), og.get("cf_tp1", 0), og.get("cf_neither", 0)))
    L.append("- 누적 hyp_pnl_pts(차단 안 했으면 얻었을 pt): **%s pt** / 승률 %s (기준선 %s)" % (
        og.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (og["win_rate"] * 100)) if "win_rate" in og else "—",
        ("%.1f%%" % (og["baseline_win_rate"] * 100)) if og.get("baseline_win_rate") is not None else "—",
    ))
    if "avg_gap_pt" in og:
        L.append("- 평균 gap_pt=%s / 평균 atr_at_block=%s (기준점 재설계 시 캘리브레이션 근거)" % (
            og["avg_gap_pt"], og["avg_atr_at_block"]))
    if og.get("recommendation"):
        L.append("- **권고**: %s" % og["recommendation"])
    if og.get("reason"):
        L.append("- %s" % og["reason"])
    L.append("")

    # [11] qty=1 손실1차 조기청산 counterfactual 상세
    L.append("## [11] qty=1 손실1차(Loss Tier1) 조기청산 counterfactual (363차)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        lt1.get("resolved_now", 0), lt1.get("n_resolved", 0), lt1.get("n_pending", 0)))
    L.append("- 누적 hyp_pnl_pts(tier1가 조기청산 vs 실제 실현 pt 차이): **%s pt** / 승률 %s" % (
        lt1.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (lt1["win_rate"] * 100)) if "win_rate" in lt1 else "—",
    ))
    if lt1.get("recommendation"):
        L.append("- **권고**: %s" % lt1["recommendation"])
    if lt1.get("reason"):
        L.append("- %s" % lt1["reason"])
    if "edge_uncertainty_corr" in lt1:
        L.append("- [제안3 편입, 참고용] edge_ratio(=|기대엣지|/불확실성, n=%s, 평균=%s) vs "
                  "실현 pt 스피어만 상관: **%s** (게이트 아님 — 등급/사이징 강화 여부는 "
                  "표본이 더 쌓인 뒤 별도 검토)" % (
            lt1.get("n_edge_samples", "—"), lt1.get("edge_ratio_mean", "—"),
            lt1.get("edge_uncertainty_corr", "—")))
    elif lt1.get("n_edge_samples", 0) > 0:
        L.append("- [제안3 편입] edge_ratio 표본 %s건 — 상관 계산 최소치(10건) 미달, 축적 대기" %
                  lt1.get("n_edge_samples", 0))
    L.append("")

    # [12] qty=1 TP1 이후 트레일 폭 counterfactual 상세
    L.append("## [12] qty=1 TP1 이후 트레일 폭 counterfactual (363차 후속, 0721 제안4 편입)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        t1t.get("resolved_now", 0), t1t.get("n_resolved", 0), t1t.get("n_pending", 0)))
    L.append("- counterfactual 분포: TRAIL_STOP %s / FORCE_EXIT %s" % (
        t1t.get("cf_trail_stop", 0), t1t.get("cf_force_exit", 0)))
    L.append("- 누적 hyp_pnl_pts(4단계 트레일링 지속 vs 실제 static lock 실현 pt 차이): "
              "**%s pt** / 승률 %s" % (
        t1t.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (t1t["win_rate"] * 100)) if "win_rate" in t1t else "—",
    ))
    if t1t.get("recommendation"):
        L.append("- **권고**: %s" % t1t["recommendation"])
    if t1t.get("reason"):
        L.append("- %s" % t1t["reason"])
    L.append("")

    # [13] 등급별 순EV 역전 감시 상세
    L.append("## [13] 등급별 순EV 역전 감시 (366차, 0722 정기점검 딥다이브)")
    L.append("")
    if gei.get("by_grade"):
        L.append("| 등급 | n | 평균 순EV(원) | 누적(원) | 승률 | 최대손실(원) | 표준편차(원) |")
        L.append("|---|---|---|---|---|---|---|")
        for g in ("A", "B", "C"):
            v = gei["by_grade"].get(g)
            if not v:
                continue
            L.append("| %s | %d | %s | %s | %.1f%% | %s | %s |" % (
                g, v["n"], format(v["avg_pnl_krw"], ",.0f"),
                format(v["total_pnl_krw"], ",.0f"), v["win_rate"] * 100,
                format(v["min_pnl_krw"], ",.0f"), format(v["stdev_pnl_krw"], ",.0f")))
        L.append("")
        L.append("> [367차, 제안4 편입] 최대손실·표준편차 보강 — 평균만으로는 \"등급 전체가")
        L.append("> 고르게 나쁨\"과 \"소수 초대형 손실(fat-tail)이 평균을 끌어내림\"을 구분할")
        L.append("> 수 없다. 0722 딥다이브: A등급 4주 누적손실의 84%가 [15]에서 관찰하는")
        L.append("> \"TP1 도달 전 급행 풀스톱\" 9건에 집중돼 있었음 — 표준편차가 크고")
        L.append("> 최대손실이 평균의 여러 배면 이 fat-tail 구조를 의심할 것.")
    if gei.get("recommendation"):
        L.append("- **권고**: %s" % gei["recommendation"])
    if gei.get("reason"):
        L.append("- %s" % gei["reason"])
    if gei.get("error"):
        L.append("- ⚠ %s" % gei["error"])
    L.append("")

    # [14] Tier1 잔여계약 2단계 조기청산 counterfactual 상세
    L.append("## [14] Tier1 잔여계약 2단계 조기청산 counterfactual (367차)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        lt2.get("resolved_now", 0), lt2.get("n_resolved", 0), lt2.get("n_pending", 0)))
    L.append("- 누적 hyp_pnl_pts(tier2가 조기청산 vs 실제 잔여계약 실현 pt 차이): **%s pt** / 승률 %s" % (
        lt2.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (lt2["win_rate"] * 100)) if "win_rate" in lt2 else "—",
    ))
    if lt2.get("recommendation"):
        L.append("- **권고**: %s" % lt2["recommendation"])
    if lt2.get("reason"):
        L.append("- %s" % lt2["reason"])
    if lt2.get("error"):
        L.append("- ⚠ %s" % lt2["error"])
    L.append("")

    # [15] 급행 풀스톱(TP1 미도달) 관찰 상세
    L.append("## [15] 급행 풀스톱(TP1 미도달) 관찰 (367차, 관찰 전용 — 정책 게이트 아님)")
    L.append("")
    L.append("- 관찰 기준: 하드스톱 청산 + 보유시간 ≤ %s초 + 진입~청산 구간에 TP1 관련 로그"
              " 없음" % frw.get("fast_exit_max_sec", "—"))
    L.append("- 급행 하드스톱 %s건 중 TP1 미도달 %s건" % (
        frw.get("n_fast_hardstop", 0), frw.get("n_no_tp1", 0)))
    if frw.get("by_grade"):
        L.append("")
        L.append("| 등급 | n | 누적 순PnL(원) | 손실건수 |")
        L.append("|---|---|---|---|")
        for g, v in sorted(frw["by_grade"].items()):
            L.append("| %s | %d | %s | %d |" % (
                g, v["n"], format(v["total_pnl_krw"], ",.0f"), v["n_loss"]))
    if frw.get("reason"):
        L.append("- %s" % frw["reason"])
    if frw.get("error"):
        L.append("- ⚠ %s" % frw["error"])
    L.append("- 이 채널은 PASS/FAIL을 판정하지 않는다 — 이 패턴 자체를 차단할 정책이")
    L.append("  아직 없어 판정이 무의미하다. GradeEVGuard·loss_tier1_qty1_shadow·")
    L.append("  loss_tier2_remainder_shadow가 다루는 문제의 선행지표로만 참고할 것.")
    L.append("")

    # [16] chase+foreign 조합 관찰 상세
    L.append("## [16] chase+foreign 조합 관찰 (368차, 관찰 전용 — 정책 게이트 아님)")
    L.append("")
    L.append("- 관찰 기준: [진입체크] 로그에서 `10_chase`·`6_foreign` 두 항목만 동시 실패"
              " (나머지 항목 무관)")
    L.append("- 로그-DB 매칭 %s건 중 동시실패 %s건" % (
        cfc.get("n_matched", 0), cfc.get("n_combo", 0)))
    if cfc.get("by_grade"):
        L.append("")
        L.append("| 등급 | n | 누적 순PnL(원) | 손실건수 |")
        L.append("|---|---|---|---|")
        for g, v in sorted(cfc["by_grade"].items()):
            L.append("| %s | %d | %s | %d |" % (
                g, v["n"], format(v["total_pnl_krw"], ",.0f"), v["n_loss"]))
    if cfc.get("reason"):
        L.append("- %s" % cfc["reason"])
    if cfc.get("error"):
        L.append("- ⚠ %s" % cfc["error"])
    L.append("- CHASE_FOREIGN_COMBO_GUARD_ENABLED(config/settings.py, 섀도) 활성화 여부")
    L.append("  판단 근거 표본 축적용. P4(CVD+OFI, 268차)와 동일 계열 논리이나 표본이")
    L.append("  작아(368차 등록 시점 n=5) 즉시 정책화하지 않는다 — §9 사전등록 원칙.")
    L.append("")

    # [17] 청산 체결 슬리피지 관찰 상세
    L.append("## [17] 청산 체결 슬리피지 관찰 (369차, 0723 정기점검, 관찰 전용 — 정책 게이트 아님)")
    L.append("")
    L.append("- 관찰 대상: 모든 청산 주문의 의도가(price_hint) vs 실체결가(fill_price)")
    L.append("  (exit_fill_slippage 테이블, main.py::_ts_record_exit_fill_slippage())")
    L.append("- 표본 n=%s, 평균 슬리피지 %s pt, 최대 %s pt (캠페인 가정 %s pt/편도)" % (
        efs.get("n", 0), efs.get("avg_slippage_pts", "—"),
        efs.get("max_slippage_pts", "—"), efs.get("assumed_slippage_pts_per_side", "—")))
    if efs.get("by_reason"):
        L.append("")
        L.append("| 청산사유 | n | 평균 슬리피지(pt) |")
        L.append("|---|---|---|")
        for reason, v in sorted(efs["by_reason"].items(), key=lambda kv: -kv[1]["n"]):
            L.append("| %s | %d | %s |" % (reason, v["n"], v["avg_pts"]))
    if efs.get("note"):
        L.append("- ⚠ **%s**" % efs["note"])
    if efs.get("reason"):
        L.append("- %s" % efs["reason"])
    if efs.get("error"):
        L.append("- ⚠ %s" % efs["error"])
    L.append("- 계기: 0723 유일 거래에서 TP1 ATR보호전환(+0.35pt 확정 예정)이 체결")
    L.append("  슬리피지로 순손실(-0.02pt)로 뒤집힘. slippage_ticks_per_side(현재 1.0,")
    L.append("  0.02pt)는 캠페인 전 채널의 왕복비용 계산에 쓰이는 공통 가정이므로,")
    L.append("  이 채널의 실측치가 그 가정과 다르더라도 즉시 자동 재보정하지 않는다")
    L.append("  — 바꾸려면 §3 사전등록 원칙에 따라 검증 시계를 리셋해야 한다.")
    L.append("")

    # [18] RegimeExhaustionGate 상세
    L.append("## [18] RegimeExhaustionGate 탈진 반전 counterfactual (379차, 관찰 전용 — 정책 게이트 아님)")
    L.append("")
    L.append("- 발동 조건: hurst<%.2f(평균회귀) AND 60분 느린 연장폭(price_extension_atr_60m)"
              " |값|>%.1fATR AND (10_chase 또는 11_countertrend 소프트 실패)" % (
        HURST_RANGE_THRESHOLD, REGIME_EXHAUSTION_EXT_ATR_THRESHOLD))
    L.append("- 계기: 0723 정기점검 딥다이브 — 진입 직후 반복 반전 패턴 3항. 10_chase"
              "(10분 룩백)는 여러 다리에 걸친 느린 탈진을 놓친다는 게 핵심 발견"
              "(0723 11:41 SHORT — 직전 10분은 안정, 이전 90분간 -35pt).")
    L.append("- 해석: hyp_pnl_pts는 **신호 방향(추격 방향)대로 갔을 때의 결과** — "
              "다른 섀도 채널과 부호 해석이 반대다. 음수 우세면 탈진 반전 가설 지지.")
    L.append("- 표본: 해결=%s건 대기중=%s건, 누적 hyp_pnl_pts=%spt "
              "(STOP=%s / TP1=%s / NEITHER=%s)" % (
        reg.get("n_resolved", 0), reg.get("n_pending", 0),
        reg.get("total_hyp_pnl_pts", "—"),
        reg.get("cf_stop", 0), reg.get("cf_tp1", 0), reg.get("cf_neither", 0)))
    if "avg_ext_atr_60m" in reg:
        L.append("- 평균 60분 연장폭=%spt(ATR배수) 평균 hurst=%s "
                  "(chase실패=%s건 / countertrend실패=%s건)" % (
            reg.get("avg_ext_atr_60m"), reg.get("avg_hurst"),
            reg.get("n_chase_failed", 0), reg.get("n_countertrend_failed", 0)))
    if reg.get("recommendation"):
        L.append("- **%s**" % reg["recommendation"])
    if reg.get("reason"):
        L.append("- %s" % reg["reason"])
    if reg.get("error"):
        L.append("- ⚠ %s" % reg["error"])
    L.append("- REGIME_EXHAUSTION_GATE_ENABLED(config/settings.py, 섀도) 활성화 여부")
    L.append("  판단 근거 표본 축적용(목표 min_samples=%d, hurst_gate_shadow·"
              "open_gap_shadow와 동일 기준) — §9 사전등록 원칙, 즉시 자동 전환 없음." % (
        VALIDATION_CAMPAIGN["regime_exhaustion_watch"]["min_samples"]))
    L.append("")

    # [19] ToxicityGate block counterfactual 상세
    L.append("## [19] ToxicityGate block counterfactual (신설)")
    L.append("")
    L.append("- 이번 실행 resolve: %d건 / 누적 판정 %s건 (미판정 %s건)" % (
        txb.get("resolved_now", 0), txb.get("n_resolved", 0), txb.get("n_pending", 0)))
    L.append("- counterfactual 분포: STOP %s / TP1 %s / NEITHER %s" % (
        txb.get("cf_stop", 0), txb.get("cf_tp1", 0), txb.get("cf_neither", 0)))
    L.append("- 누적 hyp_pnl_pts(차단 안 했으면 얻었을 pt): **%s pt** / 승률 %s (기준선 %s)" % (
        txb.get("total_hyp_pnl_pts", "—"),
        ("%.1f%%" % (txb["win_rate"] * 100)) if "win_rate" in txb else "—",
        ("%.1f%%" % (txb["baseline_win_rate"] * 100)) if txb.get("baseline_win_rate") is not None else "—",
    ))
    if "avg_toxicity_score" in txb:
        L.append("- 평균 toxicity_score=%s / 평균 toxicity_score_ma=%s (block_threshold 재검토 시 캘리브레이션 근거)" % (
            txb["avg_toxicity_score"], txb["avg_toxicity_score_ma"]))
    if txb.get("recommendation"):
        L.append("- **권고**: %s" % txb["recommendation"])
    if txb.get("reason"):
        L.append("- %s" % txb["reason"])
    L.append("- action=\"reduce\"는 실제 축소 체결로 trades에 남으므로 이 채널 대상 아님 —"
              " action=\"block\"만 계측(open_gap_shadow와 동일 원칙).")
    L.append("")

    # [20] BAR_ONLY_RELAX 수용/롤백 상세
    L.append("## [20] BAR_ONLY_RELAX 수용/롤백 감시 (402차 후속, 관찰 전용 — 자동 롤백 아님)")
    L.append("")
    if wcw.get("error"):
        L.append("> ⚠ %s" % wcw["error"])
    else:
        L.append("- 발효일 **%s** (401차 커밋이 2026-07-29 장 마감 후라 다음 세션부터 적용)"
                  % wcw.get("effective_date", "—"))
        L.append("- 계측일: 완화 전 %s일 / 완화 후 %s일"
                  % (wcw.get("n_days_pre", 0), wcw.get("n_days_post", 0)))
        L.append("- collapse 비율: 기준선 %s → 완화 후 %s (목표 %s±%s)" % (
            ("%.1f%%" % (wcw["baseline_ratio"] * 100)) if wcw.get("baseline_ratio") is not None else "—",
            ("%.1f%%" % (wcw["post_ratio"] * 100)) if wcw.get("post_ratio") is not None else "—",
            "%.0f%%" % (float(VALIDATION_CAMPAIGN.get("weight_collapse_watch", {}).get("target_ratio", 0.20)) * 100),
            "%.0f%%p" % (float(VALIDATION_CAMPAIGN.get("weight_collapse_watch", {}).get("target_tolerance", 0.07)) * 100),
        ))
        if wcw.get("effect"):
            L.append("- 효과 판정: **%s**" % wcw["effect"])
        if wcw.get("regressed"):
            L.append("- **회귀 감지(Q3 분포 불일치 부작용 의심)**: %s" % " / ".join(wcw["regressed"]))
        if wcw.get("daily"):
            L.append("")
            L.append("| 일자 | 계측 분봉 | collapse% | 3m 적중 | 5m 적중 | 구분 |")
            L.append("|---|---|---|---|---|---|")
            for d, v in sorted(wcw["daily"].items()):
                _a3 = v["acc"].get("3m")
                _a5 = v["acc"].get("5m")
                L.append("| %s | %d | %.1f%% | %s | %s | %s |" % (
                    d, v["n"], v["ratio"] * 100,
                    ("%.1f%%" % (_a3 * 100)) if _a3 is not None else "—",
                    ("%.1f%%" % (_a5 * 100)) if _a5 is not None else "—",
                    "완화후" if d >= wcw.get("effective_date", "") else "완화전"))
        if wcw.get("recommendation"):
            L.append("")
            L.append("- **권고**: %s" % wcw["recommendation"])
        if wcw.get("reason"):
            L.append("")   # 표 직후 리스트가 붙으면 Markdown 표 렌더링이 깨진다
            L.append("- %s" % wcw["reason"])
    L.append("")
    L.append("> `weight_collapsed`는 398차(2026-07-28 저녁) 배포분부터 기록된다 — 그 이전")
    L.append("> 일자는 컬럼이 NULL이라 \"collapse 0건\"이 아니라 \"미계측\"이므로 집계에서")
    L.append("> 제외한다. 완화 전 기준선이 사실상 2026-07-29 단일일이라는 뜻이므로,")
    L.append("> min_days(기본 3거래일) 미만에서는 판정을 보류한다(313차 원칙).")
    L.append("> 롤백은 `config/settings.py:BAR_ONLY_RELAX_ENABLED = False` 1줄로 즉시 가역.")
    L.append("> 일 단위 확인은 `scripts/weight_collapse_monitor.py`.")
    L.append("")

    # [21] 방향별 순EV 상세
    L.append("## [21] 방향별 순EV 감시 (402차 후속5, [13]의 방향 축 미러)")
    L.append("")
    if dev.get("error"):
        L.append("> ⚠ %s" % dev["error"])
    else:
        L.append("- 필터: `entry_source='%s'` — 진입 %s건(원본 %s행, 부분청산 병합)"
                  % (dev.get("entry_source_filter", "?"),
                     dev.get("n_entries_merged", 0), dev.get("n_rows_raw", 0)))
        L.append("")
        L.append("| 방향 | n | 평균 순EV(원) | 누적(원) | 승률 | 최대손실(원) | 표준편차(원) |")
        L.append("|---|---|---|---|---|---|---|")
        for d in ("LONG", "SHORT"):
            v = _dv.get(d)
            if not v:
                continue
            L.append("| %s | %d | %s | %s | %.1f%% | %s | %s |" % (
                d, v["n"], format(v["avg_pnl_krw"], ",.0f"),
                format(v["total_pnl_krw"], ",.0f"), v["win_rate"] * 100,
                format(v["min_pnl_krw"], ",.0f"), format(v["stdev_pnl_krw"], ",.0f")))
        if dev.get("recommendation"):
            L.append("")
            L.append("- **권고**: %s" % dev["recommendation"])
        if dev.get("reason"):
            L.append("")
            L.append("- %s" % dev["reason"])
    L.append("")
    L.append("> **[13]과 필터가 다르다(의도적)**. [13]은 `grade IN ('A','B','C')`이라")
    L.append("> 구버전 `entry_source=NULL`·`OPERATOR_MANUAL` 행이 포함되지만, 이 채널은")
    L.append("> `SYSTEM_AUTO` 한정이다 — 방향 편향은 시스템 판단의 문제이므로 수동·레거시")
    L.append("> 진입을 섞으면 안 된다. 두 채널의 표본 수가 다른 것은 결함이 아니다.")
    L.append("> 또한 부분청산 행 중복을 진입 1건 단위로 병합한다 — 그대로 세면 TP1/TP2")
    L.append("> 부분청산이 각각 '승리'로 집계돼 승률이 부풀려진다(402차 실제 오류 사례).")
    L.append("")

    # [22] MFE 캡처율 상세
    L.append("## [22] MFE 캡처율 관찰 (402차 후속5, 관찰 전용 — 판정 없음)")
    L.append("")
    if mcw.get("error"):
        L.append("> ⚠ %s" % mcw["error"])
    else:
        L.append("- 필터: `entry_source='%s'` — 진입 %s건(원본 %s행 병합)"
                  % (mcw.get("entry_source_filter", "?"),
                     mcw.get("n_entries", 0), mcw.get("n_rows_raw", 0)))
        L.append("- 평균 실현 %s pt / 보유구간 MFE %s pt / 15:10까지 MFE %s pt" % (
            mcw.get("avg_realized_pt", "—"), mcw.get("avg_mfe_hold_pt", "—"),
            mcw.get("avg_mfe_close_pt", "—")))
        L.append("- **풀링 캡처율**(ΣRealized/ΣMFE) 보유구간 %s (n=%s) / 15:10까지 %s (n=%s)" % (
            ("%.1f%%" % (mcw["capture_in_hold_pooled"] * 100)) if mcw.get("capture_in_hold_pooled") is not None else "—",
            mcw.get("n_hold", 0),
            ("%.1f%%" % (mcw["capture_to_close_pooled"] * 100)) if mcw.get("capture_to_close_pooled") is not None else "—",
            mcw.get("n_close", 0)))
        L.append("- **승리 거래만** 15:10까지 풀링 캡처율 %s (n=%s)" % (
            ("%.1f%%" % (mcw["capture_to_close_pooled_winners"] * 100))
            if mcw.get("capture_to_close_pooled_winners") is not None else "—",
            mcw.get("n_winners", 0)))
        L.append("- **평균 미실현 잔여**(MFE−실현) 보유구간 %s pt / 15:10까지 %s pt" % (
            mcw.get("avg_left_in_hold_pt", "—"), mcw.get("avg_left_to_close_pt", "—")))
        if mcw.get("most_left5"):
            L.append("")
            L.append("가장 많이 흘린 5건 (15:10 MFE − 실현):")
            L.append("")
            L.append("| 진입 | 방향 | 실현pt | 보유MFE | 15:10MFE | 잔여pt |")
            L.append("|---|---|---|---|---|---|")
            for s in mcw["most_left5"]:
                L.append("| %s | %s | %s | %s | %s | %.2f |" % (
                    s["ts"], s["dir"], s["realized_pt"],
                    s["mfe_hold_pt"] if s["mfe_hold_pt"] is not None else "—",
                    s["mfe_close_pt"] if s["mfe_close_pt"] is not None else "—",
                    s["mfe_close_pt"] - s["realized_pt"]))
        if mcw.get("reason"):
            L.append("")
            L.append("- %s" % mcw["reason"])
    L.append("")
    L.append("> 이 채널은 **판정하지 않는다**(verdict 항상 OBSERVE). 여기서 나올 결정")
    L.append("> (\"청산을 더 늦춰라\")은 이미 [12] tp1_trail_shadow가 판정 중이므로, 이")
    L.append("> 수치는 그 판정을 해석할 맥락(\"캡처율이 이렇게 낮은데도 트레일링이 안")
    L.append("> 낫다\"가 성립하는지)만 제공한다. 단일일 극단 사례로 결론 내지 말 것")
    L.append("> (2026-07-29 캡처율 7.7%는 -15.6% 폭락일 1건이다 — 313차 원칙).")
    L.append("")

    # [23] EOD 모델가드 판정 괴리 상세
    L.append("## [23] EOD 모델가드 판정 괴리 감시 (404차 신설)")
    L.append("")
    if gsc.get("error"):
        L.append("> ⚠ %s" % gsc["error"])
    elif gsc.get("reason"):
        L.append("- %s" % gsc["reason"])
    else:
        L.append("- 표본 %s건 / %s거래일 (재측정 실패 %s건 별도 제외)" % (
            gsc.get("n_samples", 0), gsc.get("n_days", 0),
            gsc.get("n_live_measure_failed", 0)))
        L.append("- **missed_upgrade_rate** (공정비교=REPLACE인데 acc.txt 기준=HOLD였던 비율): "
                  "**%s** (n=%s/%s)" % (
                      ("%.1f%%" % (gsc["missed_upgrade_rate"] * 100))
                      if gsc.get("missed_upgrade_rate") is not None else "—",
                      gsc.get("missed_upgrade_n", "—"), gsc.get("n_fair", "—")))
        if gsc.get("mean_distortion") is not None:
            L.append("- 평균 왜곡(acc.txt − 동일폴드 재측정) = %+.4f" % gsc["mean_distortion"])
        if gsc.get("by_horizon"):
            L.append("")
            L.append("| 호라이즌 | n | missed_upgrade |")
            L.append("|---|---|---|")
            for hz, v in sorted(gsc["by_horizon"].items()):
                L.append("| %s | %d | %d |" % (hz, v["n"], v["missed"]))
    L.append("")
    L.append("> **판정 기준**(관측 전 고정, §9): missed_upgrade_rate ≥ %.0f%% → FAIL"
              "(판정기준을 old_acc_live로 교체할지 주간회의 검토), 미만 → PASS(acc.txt 유지)."
              % (VALIDATION_CAMPAIGN["guard_shadow"]["missed_upgrade_rate_max"] * 100))
    L.append("> 07-31 최초 라이브 관측(6개 호라이즌 중 3개 불일치)이 이 채널을 만든 계기이나,")
    L.append("> 임계값은 그 단일일 관측치에 맞추지 않고 독립적으로 고정했다 — 이 리포트가")
    L.append("> 그 계기가 된 날의 데이터를 포함하더라도 임계값 자체는 사후 조정이 아니다.")
    L.append("> (근거: `dev_memory/DECISION_LOG.md` 404차 항목, 313차·§9 원칙)")
    L.append("")

    # [23-부속] intraday 계측 CV 관찰 (판정 없음)
    L.append("### [23-부속] intraday 계측 CV 관찰 (404차 후속, 관찰 전용 — 판정 없음)")
    L.append("")
    if icw.get("error"):
        L.append("> ⚠ %s" % icw["error"])
    elif icw.get("reason"):
        L.append("- %s" % icw["reason"])
    elif icw.get("by_horizon"):
        L.append("- 표본 %s건 / %s거래일" % (icw.get("n_samples", 0), icw.get("n_days", 0)))
        L.append("")
        L.append("| 호라이즌 | n | 평균 cv_acc | σ(cv_acc) | 평균 왜곡 | fair_would_hold |")
        L.append("|---|---|---|---|---|---|")
        for hz, v in sorted(icw["by_horizon"].items()):
            L.append("| %s | %d | %.4f | %s | %s | %s |" % (
                hz, v["n"], v["mean_cv"],
                ("%.4f" % v["std_cv"]) if v["std_cv"] is not None else "—",
                ("%+.4f" % v["mean_distortion"]) if v["mean_distortion"] is not None else "—",
                ("%.0f%%" % (v["fair_would_hold_rate"] * 100))))
    L.append("")
    L.append("> **판정하지 않는다**(verdict 항상 OBSERVE). 실측(404차 후속 §1): 동일 데이터·")
    L.append("> 시드만 다른 재현 분산이 5m 기준 8.83%p로 EOD 가드 허용폭(2.5%p)의 3.5배 —")
    L.append("> 이 표의 σ(cv_acc)가 크게 나오는 것은 결함이 아니라 그 잡음이 실측되는 것이다.")
    L.append("> `fair_would_hold`가 높다고 즉시 intraday 가드를 도입하지 말 것 — 표본이")
    L.append("> 충분히(수 주) 쌓여 잡음이 아닌 추세인지 확인한 뒤 사람이 판단한다(§9).")
    L.append("")

    # [23-B] TP1/손절 초기 기하 A/B 상세 (403차 P1-6 — 404차 후속3에서 리포트 편입)
    L.append("## [23-B] TP1/손절 초기 기하 A/B (403차 P1-6, 404차 후속3 리포트 편입)")
    L.append("")
    if _g23.get("error"):
        L.append("> ⚠ 스크립트 실행 실패: %s" % _g23["error"])
    else:
        L.append("- 진입 %s건 (ATR 결측 제외 %s건) / 거래일 %s일"
                  % (_g23.get("n_trades", "—"), _g23.get("n_skipped", "—"),
                     _g23.get("n_days", "—")))
        pv = _g23.get("per_variant") or {}
        if pv:
            L.append("")
            L.append("| 변형 | n | TP1 | STOP | 승률 | 누적pt | 현행 대비 |")
            L.append("|---|---|---|---|---|---|---|")
            for k, v in pv.items():
                L.append("| %s | %d | %d | %d | %.1f%% | %+.2f | %s |" % (
                    k, v["n"], v["n_tp1"], v["n_stop"], v["win_rate"] * 100,
                    v["total_pt"],
                    ("%+.2f" % v["delta_vs_current"]) if v["delta_vs_current"] is not None else "—"))
        L.append("")
        L.append("- **판정: %s** — %s" % (_g23.get("verdict"), _g23.get("reason")))
    L.append("")
    L.append("> 종전에는 `scripts/tp1_geometry_shadow.py`를 따로 실행해야만 보여 주간회의에")
    L.append("> 노출되지 않았다(403차 신설 이후). 404차 후속3에서 계산부를 `compute()`/")
    L.append("> `summarize()`로 추출해 이 리포트가 직접 호출한다 — 판정 기준·로직 무변경.")
    L.append("> ⚠ `current`의 절대값은 실현손익이 아니다(qty=1 보호전환을 'TP1 전량청산'으로")
    L.append("> 단순화). **변형 간 상대비교 전용.**")
    L.append("> ⚠ 이 채널은 MW0601에서 `tp1_x2` **+32.78pt**(현행 초과=FAIL 방향)가 나왔으나")
    L.append("> MW0602에서는 **−19.04pt**(PASS 방향)로 **부호가 뒤집힌다.** 두 PC의 거래집합이")
    L.append("> 달라서이며(protect mode 무관 — 이 시뮬은 protect mode를 쓰지 않는다), n≈60·12일")
    L.append("> 로는 기하를 결정할 수 없다는 뜻이다(313차).")
    L.append("")

    # [24] TP1 보호전환 반납 관찰
    L.append("## [24] TP1 보호전환 반납 관찰 (404차 후속3, 관찰 전용 — 판정 없음)")
    L.append("")
    if tpg.get("error"):
        L.append("> ⚠ %s" % tpg["error"])
    elif tpg.get("reason"):
        L.append("- %s" % tpg["reason"])
    else:
        L.append("- 보호전환 %s건 / %s거래일 (모드 분포: %s)"
                  % (tpg.get("n", 0), tpg.get("n_days", 0),
                     ", ".join("%s=%d" % kv for kv in (tpg.get("by_mode") or {}).items()) or "—"))
        L.append("- **반납 %s건 / 더 달림 %s건**"
                  % (tpg.get("n_gaveback", "—"), tpg.get("n_ranfurther", "—")))
        L.append("- TP1 장부이익 평균 %s pt / 중앙값 %s pt   |   평균 보호폭 %s pt"
                  % (tpg.get("mean_paper_pt", "—"), tpg.get("median_paper_pt", "—"),
                     tpg.get("mean_offset_pt", "—")))
        L.append("- **반납 중앙값 %s pt** (평균 %s pt) → 중앙값 기준 반납률 %s"
                  % (tpg.get("median_give_pt", "—"), tpg.get("mean_give_pt", "—"),
                     ("%.0f%%" % (tpg["median_giveback_rate"] * 100))
                     if tpg.get("median_giveback_rate") is not None else "—"))
        if tpg.get("offset_vs_give_corr") is not None:
            L.append("- 보호폭 vs 반납 상관계수 **%.3f** (음수 = 좁은 보호폭일수록 더 반납)"
                      % tpg["offset_vs_give_corr"])
    L.append("")
    L.append("> **판정하지 않는다**(verdict 항상 OBSERVE). 처방(offset을 얼마로 할지)은 [25]가 맡는다.")
    L.append("> **평균이 아니라 중앙값을 볼 것** — 0729 폭락일 2건이 평균을 5배 끌어올려")
    L.append("> 평균 반납은 무해해 보이는데 중앙값은 그 몇 배다. 두 수치가 정반대 인상을")
    L.append("> 주는 전형적 사례이므로 평균만 인용하지 말 것(372차 원칙).")
    L.append("> 소스(`synthetic_partial_exits`)는 339차부터 쌓였으나 404차 후속3까지 **캠페인")
    L.append("> 소비처가 없어 방치**돼 있었다 — 402차 후속3 `toxicity_block_shadow`와 같은 계열.")
    L.append("")

    # [25] TP1 보호전환 offset A/B
    L.append("## [25] TP1 보호전환 offset A/B (404차 후속3 신설)")
    L.append("")
    if _g25.get("error"):
        L.append("> ⚠ 스크립트 실행 실패: %s" % _g25["error"])
    else:
        L.append("- 보호전환 %s건 (제외 %s건) / 거래일 %s일"
                  % (_g25.get("n_hooks", "—"), _g25.get("n_skipped", "—"),
                     _g25.get("n_days", "—")))
        pv = _g25.get("per_variant") or {}
        if pv:
            L.append("")
            L.append("| 변형 | n | STOP | TP2 | 승률 | 누적pt | 중앙값 | 현행 대비 | 건별 우세 |")
            L.append("|---|---|---|---|---|---|---|---|---|")
            for k, v in pv.items():
                L.append("| %s | %d | %d | %d | %.1f%% | %+.2f | %+.3f | %s | %s |" % (
                    k, v["n"], v["n_stop"], v["n_tp2"], v["win_rate"] * 100,
                    v["total_pt"], v["median_pt"],
                    ("%+.2f" % v["delta_vs_current"]) if v["delta_vs_current"] is not None else "—",
                    ("%s/%d" % (v["beats_current_n"], v["n"])) if v.get("beats_current_n") is not None else "—"))
        L.append("")
        L.append("- **판정: %s** — %s" % (_g25.get("verdict"), _g25.get("reason")))
    L.append("")
    L.append("> ⚠ **사전등록 정직성 고지**: `breakeven` 변형은 이 채널 신설 **전에** 404차")
    L.append("> 후속3 조사에서 이미 1회 측정됐다(현행이 22/23 우세) — 재확인용이지 사전등록된")
    L.append("> 검증이 아니다. 사전등록 가치는 `atr_lock_0.50/0.75`·`bar_range`에 있다.")
    L.append("> ⚠ **FAIL이 떠도 즉시 적용 금지** — 372차 이상치 분해상 현행 초과 대안들은")
    L.append("> **최대 기여 1건만 빼면 부호가 역전**된다(atr_lock_0.75 +0.92→−1.33pt,")
    L.append("> bar_range +0.81→−0.29pt). 건별 우세도 8/23·7/23으로 소수이고 중앙값 차이는")
    L.append("> 0.000pt다. 표본이 더 쌓일 때까지 **현행 유지가 합리적**이다.")
    L.append("> ⚠ [12] tp1_trail_shadow가 기각한 \"TP1 **이후** 트레일 폭\"과 다른 질문이다")
    L.append("> — 이건 TP1 **시점**의 초기 보호 offset이다.")
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
