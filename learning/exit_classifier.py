# -*- coding: utf-8 -*-
"""[MW0602 428차 / B-2] 청산 측 학습기 — **섀도 전용, 라이브 미배선**.

무엇을 하는가
-------------
`exit_outcome_labeler`가 만든 포지션×분 라벨로 **"지금 끊을까 더 들고 갈까"** 를
학습한다. 진입 측 학습기(GBM/RF 방향, SGD 방향, meta_confidence·meta_labeling
방향적중)와 달리 **청산 축에는 학습기가 하나도 없었다.**

⚠ **라이브 청산에 배선되어 있지 않다.** 예측은 `exit_model_shadow`에 기록만 하며,
   실거래 판단에 관여하지 않는다. 배선은 [41] 채널 판정 후 주간회의 결정이다
   (§9 사전등록 원칙 — quantile_regressor·triple-barrier와 같은 순서).
   `docs/미륵이고도화3` 계획서 2장이 경고한 "기준선을 흔드는 변경"이므로
   **D-day(08-14) 스냅샷 이후**에 배선 논의를 시작할 것.

가장 중요한 설계 — 스스로 학습을 거부한다
-----------------------------------------
현재 표본은 **395행 / 98포지션 / 16거래일**이고, 행은 같은 포지션 안에서 강하게
상관돼 있다(포지션당 4.03행). 따라서 **유효표본은 행 수가 아니라 포지션 수**다.

피처 14개 · 양성률 32%에서 EPV(events per variable)는

    98 × 0.32 / 14 ≈ 2.2

로, 통상 기준 10의 **5분의 1**이다. 이 상태로 학습하면 학습이 아니라 암기다.
그래서 이 모듈은 **EPV 하한을 넘기 전에는 학습 자체를 거부**하고, 대신
"얼마나 더 필요한가"를 계산해 돌려준다([33] faststop_rerun_watch와 같은
게이지 방식 — 사람이 기억하지 않아도 되게 한다).

학습이 열리면
-------------
· `GroupKFold(groups=entry_ts)` — 같은 포지션의 행이 학습/검증에 갈라져 들어가면
  누출이다. 행 단위 KFold는 **절대 쓰지 않는다.**
· OOF 예측만 기록한다 — in-sample 점수는 이 표본 크기에서 무의미하다.
· 기준선(항상 다수클래스)과 함께 보고한다. AUC 0.55짜리를 "학습됨"으로 읽지 않게.
"""
import datetime
import json
import logging
import os
import sqlite3

logger = logging.getLogger("LEARNING")

# 통상 기준. 이보다 낮으면 계수 추정이 표본 잡음에 지배된다.
MIN_EVENTS_PER_VARIABLE = 10.0
MIN_DAYS = 20            # 313차 — 일자 다양성이 없으면 레짐 하나를 외운다
LABEL_PRIMARY = "y_hold_better"


def _conn(path):
    c = sqlite3.connect(path, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def ensure_table(trades_db):
    """`exit_model_shadow` 멱등 생성 — 계측 전용, 실거래 무관여."""
    with _conn(trades_db) as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS exit_model_shadow (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_ts      TEXT NOT NULL,   -- 학습·기록 실행 시각
            entry_ts    TEXT NOT NULL,   -- trades.entry_ts 조인 키
            ts          TEXT NOT NULL,   -- 그 분
            held_min    REAL,
            label       TEXT,            -- 어떤 라벨로 학습했나
            y_true      INTEGER,
            p_hold      REAL,            -- OOF 예측 확률 (계속 보유가 유리할 확률)
            n_positions INTEGER,         -- 학습 시점 표본 규모 (사후 해석용)
            n_features  INTEGER,
            created_at  TEXT DEFAULT (datetime('now','localtime'))
        )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_ems_entry_ts "
                  "ON exit_model_shadow(entry_ts)")
        c.commit()


def readiness(summary_dict, n_features):
    """학습 가능한가 — EPV·거래일 기준. 미달이면 **얼마나 더 필요한지** 함께 낸다."""
    n_pos = int(summary_dict.get("n_positions") or 0)
    n_days = int(summary_dict.get("n_days") or 0)
    rate = float(summary_dict.get(LABEL_PRIMARY + "_rate") or 0.0)
    out = {
        "n_positions": n_pos, "n_days": n_days, "pos_rate": round(rate, 4),
        "n_features": int(n_features),
        "min_events_per_variable": MIN_EVENTS_PER_VARIABLE, "min_days": MIN_DAYS,
    }
    if rate <= 0 or n_features <= 0:
        out["ready"] = False
        out["reason"] = "양성 표본이 없어 EPV를 계산할 수 없다"
        return out
    out["epv"] = round(n_pos * rate / float(n_features), 3)
    need_pos = int(round(MIN_EVENTS_PER_VARIABLE * n_features / rate))
    out["positions_required"] = need_pos
    out["positions_short"] = max(0, need_pos - n_pos)
    out["ready"] = bool(out["epv"] >= MIN_EVENTS_PER_VARIABLE and n_days >= MIN_DAYS)
    if not out["ready"]:
        out["reason"] = (
            "EPV %.2f < %.0f (포지션 %d/%d, %d건 부족) · 거래일 %d/%d — **학습 거부**. "
            "이 표본으로 학습하면 학습이 아니라 암기다"
            % (out["epv"], MIN_EVENTS_PER_VARIABLE, n_pos, need_pos,
               out["positions_short"], n_days, MIN_DAYS))
    return out


def train_or_defer(rows, summary_dict, feature_names, trades_db=None,
                   persist=False, label=LABEL_PRIMARY):
    """표본이 차면 학습하고, 아니면 **거부 사유와 함께 그대로 돌려준다**.

    반환 dict의 `trained`가 False면 아무것도 학습·기록하지 않았다는 뜻이다.
    """
    rd = readiness(summary_dict, len(feature_names))
    out = {"trained": False, "label": label, "readiness": rd}
    if not rd.get("ready"):
        out["reason"] = rd.get("reason")
        return out

    try:
        import numpy as np
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.model_selection import GroupKFold
        from sklearn.metrics import roc_auc_score
    except Exception as e:                       # pragma: no cover
        out["reason"] = "sklearn 로드 실패: %s" % e
        return out

    X = np.array([[float(r[f]) for f in feature_names] for r in rows], dtype=float)
    y = np.array([int(r[label]) for r in rows], dtype=int)
    groups = np.array([r["entry_ts"] for r in rows])

    # ⚠ 포지션 단위 그룹 분할 — 같은 포지션의 행이 학습/검증에 갈리면 누출이다.
    n_splits = min(5, len(set(groups)))
    oof = np.full(len(y), np.nan)
    for tr, te in GroupKFold(n_splits=n_splits).split(X, y, groups):
        m = GradientBoostingClassifier(random_state=428, n_estimators=120,
                                       max_depth=2, learning_rate=0.05)
        m.fit(X[tr], y[tr])
        oof[te] = m.predict_proba(X[te])[:, 1]

    mask = ~np.isnan(oof)
    out["trained"] = True
    out["n_rows"] = int(mask.sum())
    out["base_rate"] = round(float(y[mask].mean()), 4)
    # 기준선: 항상 다수클래스. AUC 0.5가 곧 무정보다.
    out["baseline_acc"] = round(max(out["base_rate"], 1 - out["base_rate"]), 4)
    out["oof_acc"] = round(float(((oof[mask] >= 0.5).astype(int) == y[mask]).mean()), 4)
    try:
        out["oof_auc"] = round(float(roc_auc_score(y[mask], oof[mask])), 4)
    except Exception:
        out["oof_auc"] = None

    if persist and trades_db:
        ensure_table(trades_db)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        recs = [(now, rows[i]["entry_ts"], rows[i]["ts"], float(rows[i]["held_min"]),
                 label, int(y[i]), float(oof[i]), int(rd["n_positions"]),
                 int(len(feature_names)))
                for i in range(len(y)) if mask[i]]
        with _conn(trades_db) as c:
            c.executemany(
                "INSERT INTO exit_model_shadow (run_ts, entry_ts, ts, held_min, label,"
                " y_true, p_hold, n_positions, n_features) "
                "VALUES (?,?,?,?,?,?,?,?,?)", recs)
            c.commit()
        out["persisted"] = len(recs)
    return out
