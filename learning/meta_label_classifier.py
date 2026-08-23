# learning/meta_label_classifier.py — [260704 감사 P1] Meta-labeling 진입품질 분류기
"""
`meta_labels` 테이블(learning/meta_labeling.py가 STEP 1 예측검증마다 축적, 6개 호라이즌
합산 65,000+건 — 260704 감사가 "이미 존재하고 rollout 리포트가 '메타 라벨 준비 완료'라고
말하는데 자산이 놀고 있다"고 지적한 데이터)을 학습 데이터로 써서 "이 신호로 진입하면
방향이 맞고 실이익이 나는가"를 직접 학습하는 호라이즌별 이진 분류기.

레이블: meta_action != "skip" (take/reduce — derive_meta_label()에서 이미
        realized_move > 0 조건을 통과한 케이스) → 1
        meta_action == "skip" (오답 또는 무이익) → 0

주의 — 실거래 게이트 미연결: strategy/entry/meta_gate.py에서 섀도우 신호
(entry_quality_prob)로만 로깅되며 action/size_multiplier에는 아직 영향을 주지 않는다.
9항목 체크리스트(strategy/entry/checklist.py)를 실제로 대체하려면 이 확률과 실현
손익의 상관을 충분 기간 검증한 뒤 결정할 것 (ROADMAP.md 참조).
"""
import json
import logging
import os
import pickle
import sqlite3
from typing import Dict, Optional

import numpy as np

try:
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import roc_auc_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.utils.class_weight import compute_sample_weight
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False

from config.settings import PREDICTIONS_DB, HORIZONS, MODEL_DIR

logger = logging.getLogger("LEARNING")

# model/horizons/ 는 .gitignore 처리되어 있음 — 그 아래에 두어 PC별 학습 산출물로 취급
_MODEL_SUBDIR = os.path.join(MODEL_DIR, "horizons", "meta_gate")
MIN_ROWS_PER_HORIZON = 2000
HGB_PARAMS = dict(max_iter=200, max_depth=4, learning_rate=0.05, min_samples_leaf=30, random_state=42)


def _train_cfg() -> Dict:
    """[MW0602 490차 / P0] 학습 위생 설정 — 없으면 **종전 동작**으로 폴백한다.

    ⚠ 폴백 값이 종전과 같아야 한다(nan_fill/purged=False, use_scaler=True).
      설정이 사라졌을 때 조용히 새 동작을 하면 "언제 바뀌었는지 모르는 변경"이 된다.
    """
    try:
        from config.settings import META_SCORER_TRAINING as _cfg
        return dict(_cfg or {})
    except Exception:
        return {"nan_fill": False, "use_scaler": True, "purged_cv": False,
                "n_splits": 3, "shadow_labels": False,
                "metrics_file": "training_metrics.json", "history_keep": 26}


_TRAIN_CFG = _train_cfg()
_METRICS_PATH = os.path.join(
    _MODEL_SUBDIR, str(_TRAIN_CFG.get("metrics_file") or "training_metrics.json"))


def _net_cost_pt() -> float:
    """순이익 라벨의 손익분기 — 캠페인 왕복비용과 **같은 정의**를 쓴다.

    `scripts/generate_validation_campaign_report.py:_roundtrip_cost_pt()` 와 동일:
        2 × price × 수수료율  +  2 × 슬리피지틱 × 틱크기
    가격은 호출 시점 평균가를 모르므로 `meta_labels.target_close` 대신 캠페인
    리포트와 같은 기본값 경로를 쓴다 — 상수를 **새로 만들지 않는다**(471차 G-2).
    """
    try:
        from config.settings import (VALIDATION_CAMPAIGN, FUTURES_COMMISSION_RATE,
                                     TICK_SIZE)
        slip = float(VALIDATION_CAMPAIGN.get("slippage_ticks_per_side", 1.0))
        # 평균가는 최근 캠페인 실측 수준(약 1,015)을 쓰지 않고, 비용의 지배항인
        # 슬리피지만으로 하한을 잡는다 — 가격 의존을 없애 라벨을 안정시킨다.
        return 2.0 * slip * float(TICK_SIZE) + 2.0 * 1000.0 * float(FUTURES_COMMISSION_RATE)
    except Exception:
        return 0.07


def _fmt(v) -> str:
    return ("%.4f" % v) if isinstance(v, float) else "N/A"


def _write_metrics_sidecar(results: Dict) -> Optional[str]:
    """[MW0602 490차 / P0-①] 학습 지표 사이드카 — 이력 누적.

    **왜 필요한가**: 종전에는 AUC가 EOD 로그에만 찍혀, 캠페인 리포트도 수집기 §12도
    그 값을 볼 수 없었다. 매주 찍히는데 **아무도 읽지 않는 상태**가 몇 달 이어졌다
    (292·303·371·468차와 같은 계열). 이 파일이 그 소비 경로를 연다.

    구조: {"latest": {...}, "history": [{"trained_at", "horizons": {...}}, ...]}
    ⚠ `model/horizons/` 는 gitignore 대상 — **PC별 산출물**이며 커밋되지 않는다.
    """
    import datetime
    try:
        prev = {}
        if os.path.exists(_METRICS_PATH):
            with open(_METRICS_PATH, encoding="utf-8") as f:
                prev = json.load(f) or {}
        entry = {
            "trained_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "horizons": {h: r for h, r in results.items() if r.get("ok")},
        }
        hist = list(prev.get("history") or [])
        hist.append(entry)
        keep = int(_TRAIN_CFG.get("history_keep", 26))
        if keep > 0:
            hist = hist[-keep:]
        payload = {"latest": entry, "history": hist,
                   "config": {k: _TRAIN_CFG.get(k) for k in
                              ("nan_fill", "schema_rule", "use_scaler",
                               "purged_cv", "n_splits", "shadow_labels")}}
        tmp = _METRICS_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, _METRICS_PATH)
        return _METRICS_PATH
    except Exception as e:      # 사이드카 실패가 학습을 죽이면 안 된다
        logger.warning("[MetaLabelClf] 지표 사이드카 기록 실패(무해): %s", e)
        return None


def load_training_metrics() -> Dict:
    """사이드카 판독 — 리포트/점검 수집기용. 없으면 빈 dict."""
    try:
        with open(_METRICS_PATH, encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def _load_meta_label_rows(horizon: str):
    """[MW0602 490차 / P0] 병기 AUC 4종에 필요한 열을 함께 읽는다.

    종전에는 `features`·`meta_action` 둘만 읽었다. 490차 탐색 실험이
    **방향성-only AUC**와 **순이익 라벨 AUC**가 운영 AUC와 크게 다르다는 것을
    보였으므로(부록 A), 그 계산에 필요한 `predicted`·`realized_move`·`threshold_move`를
    같이 가져온다. **학습 입력은 그대로 `features`뿐이다** — 이 열들은 평가에만 쓴다.
    """
    if not os.path.exists(PREDICTIONS_DB):
        return []
    with sqlite3.connect(PREDICTIONS_DB, timeout=10) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT ts, features, meta_action, predicted, realized_move, threshold_move "
            "  FROM meta_labels WHERE horizon=? ORDER BY ts",
            (horizon,),
        ).fetchall()
    return rows


def _resolve_schema(records) -> list:
    """[MW0602 490차 / P0-②] `feat_names` 채택 — **마지막 거래일 키 교집합**.

    종전 규칙("키가 가장 많은 행")의 문제: 451차가 폐기한 `program_*` 3종이
    2026-07-28~08-07 구간의 144키 행에 남아 있어, 그 행이 계속 스키마로 뽑히면서
    폐기 피처가 배포 모델에 **영구 고착**됐다(서빙 시 항상 0.0).
    매주 재학습해도 낫지 않는 구조였다.

    새 규칙은 **마지막 거래일의 모든 행에 존재하는 키**만 쓴다 —
    그 집합은 정의상 **현재 서빙이 주는 것**과 일치하고, 새 상수를 만들지 않는다.

    ⚠ 그날 한 행이라도 축퇴(피처 결손)면 교집합이 줄어든다. **보수적 방향**이라
      안전하지만, 스키마 크기를 사이드카에 남겨 드리프트가 보이게 한다.
    """
    if not records:
        return []
    last_day = max(str(r["ts"])[:10] for r in records)
    day_rows = [r for r in records if str(r["ts"])[:10] == last_day]
    schema = None
    for r in day_rows:
        keys = set(r["fd"].keys())
        schema = keys if schema is None else (schema & keys)
    return sorted(schema or set())


def _purged_splits(n: int, n_splits: int, embargo: int):
    """[MW0602 490차 / P0-③] 엠바고를 둔 시계열 폴드.

    라벨이 T→T+h를 보므로 폴드 경계 직전 h개 행은 검증 구간의 미래를 이미 담고 있다.
    `TimeSeriesSplit` 그대로 쓰면 그만큼 누수가 섞인다 — 학습분 **꼬리 `embargo`개**를 잘라낸다.
    (`scripts/validate_feature_set_purged_cv.py`와 같은 철학.)

    yields: (train_idx, val_idx)
    """
    fold = n // (n_splits + 1)
    if fold <= 0:
        return
    for k in range(1, n_splits + 1):
        tr_end = fold * k
        va_end = fold * (k + 1) if k < n_splits else n
        tr_end_purged = max(0, tr_end - int(embargo))
        if tr_end_purged <= 0 or va_end <= tr_end:
            continue
        yield np.arange(0, tr_end_purged), np.arange(tr_end, va_end)


def train_entry_quality_models(min_rows: int = MIN_ROWS_PER_HORIZON) -> Dict:
    """호라이즌별 진입품질(수익여부) 이진 분류기 학습 + 저장.

    [MW0602 490차 / P0] 학습 위생 3종을 적용한다 — 설정은
    `config/settings.py:META_SCORER_TRAINING`(사전등록, 근거 주석 포함):
      ① 결측 채움 `0.0` → `NaN`   ② 스키마 = 마지막 거래일 키 교집합
      ③ StandardScaler 제거 + Purged CV(엠바고 = 호라이즌 분 수)
    그리고 **병기 AUC 4종**을 같은 홀드아웃·같은 모델 점수로 계산해 사이드카에 남긴다.

    ⚠ **매매 경로 무관** — 스코어러는 섀도다(`strategy/entry/meta_gate.py:105`).

    Returns: {"ok", "horizons": {hz: {...}}, "model_dir", "metrics_path"}
    """
    if not _SKLEARN_OK:
        return {"ok": False, "error": "scikit-learn 미설치"}

    cfg = dict(_TRAIN_CFG)
    use_nan = bool(cfg.get("nan_fill", True))
    use_scaler = bool(cfg.get("use_scaler", False))
    use_purged = bool(cfg.get("purged_cv", True))
    n_splits = int(cfg.get("n_splits", 3))
    want_shadow = bool(cfg.get("shadow_labels", True))

    os.makedirs(_MODEL_SUBDIR, exist_ok=True)
    results = {}
    for hz in HORIZONS:
        rows = _load_meta_label_rows(hz)
        if len(rows) < min_rows:
            results[hz] = {"ok": False, "error": "데이터 부족 (%d < %d)" % (len(rows), min_rows)}
            continue

        records = []
        for r in rows:
            try:
                fd = json.loads(r["features"]) if r["features"] else {}
            except (ValueError, TypeError):
                fd = {}
            if not isinstance(fd, dict) or not fd:
                continue
            records.append({
                "ts": r["ts"], "fd": fd, "act": r["meta_action"],
                "pred": int(r["predicted"] or 0),
                "rm": float(r["realized_move"] or 0.0),
                "tm": float(r["threshold_move"] or 0.0),
            })

        feat_names = _resolve_schema(records)
        if not records or not feat_names:
            results[hz] = {"ok": False, "error": "피처 파싱 실패 또는 스키마 공집합"}
            continue

        _miss = np.nan if use_nan else 0.0

        def _val(fd, key):
            """py37 호환 — walrus 금지(이 모듈은 py37_32 런타임이 import한다)."""
            v = fd.get(key)
            if v is None:
                return _miss
            try:
                return float(v)
            except (TypeError, ValueError):
                return _miss

        X = np.array([[_val(rec["fd"], f) for f in feat_names] for rec in records],
                     dtype=np.float32)
        y = np.array([0 if rec["act"] == "skip" else 1 for rec in records], dtype=int)

        # 병기 AUC용 보조 배열 — **학습 입력이 아니다. 평가에만 쓴다.**
        is_dir = np.array([rec["pred"] != 0 for rec in records], dtype=bool)
        y_net = np.array([1 if rec["rm"] >= _net_cost_pt() else 0 for rec in records], dtype=int)
        y_strong = np.array(
            [1 if rec["rm"] >= max(2.0 * rec["tm"], 0.05) else 0 for rec in records], dtype=int)

        if len(np.unique(y)) < 2:
            results[hz] = {"ok": False, "error": "레이블 단일 클래스 — 학습 불가"}
            continue

        # ── CV — 엠바고를 둔 시계열 폴드 (③) ────────────────────────────────
        embargo = int(HORIZONS.get(hz, 1)) if use_purged else 0
        splits = (list(_purged_splits(len(X), n_splits, embargo)) if use_purged
                  else list(TimeSeriesSplit(n_splits=n_splits).split(X)))

        # 폴드 홀드아웃 예측을 모아 4종 AUC를 **같은 점수**로 계산한다.
        oof_score, oof_idx = [], []
        for train_idx, val_idx in splits:
            y_tr, y_val = y[train_idx], y[val_idx]
            if len(np.unique(y_tr)) < 2 or len(np.unique(y_val)) < 2:
                continue
            X_tr, X_val = X[train_idx], X[val_idx]
            if use_scaler:
                _sc = StandardScaler()
                X_tr, X_val = _sc.fit_transform(X_tr), _sc.transform(X_val)
            model = HistGradientBoostingClassifier(**HGB_PARAMS)
            model.fit(X_tr, y_tr, sample_weight=compute_sample_weight("balanced", y_tr))
            oof_score.append(model.predict_proba(X_val)[:, 1])
            oof_idx.append(val_idx)

        aucs = {}
        if oof_score:
            sc_all = np.concatenate(oof_score)
            ix_all = np.concatenate(oof_idx)
            d_all = is_dir[ix_all]

            def _auc(labels, mask=None):
                lab = labels[ix_all] if mask is None else labels[ix_all][mask]
                s = sc_all if mask is None else sc_all[mask]
                if len(lab) < 2 or len(np.unique(lab)) < 2:
                    return None
                return round(float(roc_auc_score(lab, s)), 4)

            aucs["auc_mixed"] = _auc(y)                       # 종전 값(하위호환·FLAT 포함)
            aucs["auc_directional"] = _auc(y, d_all)          # [2] 모집단과 일치
            if want_shadow:
                aucs["auc_net_directional"] = _auc(y_net, d_all)        # P1 게이트 지표
                aucs["auc_strong_directional"] = _auc(y_strong, d_all)  # P2 섀도 게이지
            aucs["n_oof"] = int(len(ix_all))
            aucs["n_oof_directional"] = int(d_all.sum())

        # ── 전체 데이터로 최종 모델 학습 + 저장 ─────────────────────────────
        X_fit = X
        if use_scaler:
            final_scaler = StandardScaler()
            X_fit = final_scaler.fit_transform(X)
            _scaler_path = os.path.join(_MODEL_SUBDIR, "%s_entry_quality_scaler.pkl" % hz)
            _tmp_s = _scaler_path + ".tmp"
            with open(_tmp_s, "wb") as f:
                pickle.dump(final_scaler, f, protocol=4)
            os.replace(_tmp_s, _scaler_path)
        else:
            # [MW0602 490차 / P0-③] 구 스케일러 잔재 제거 — **함정 차단**.
            # 사이드카가 유실되면 `_scaled_flag()`가 종전 동작(True)으로 폴백하는데,
            # 그때 파일이 남아 있으면 **NaN이 섞인 입력에 구 스케일러가 적용돼**
            # 조용히 쓰레기 점수가 나온다. 파일을 없애면 그 경로에서 모델이
            # 로드되지 않아(= score None) **틀린 값 대신 부재로 실패**한다.
            _stale = os.path.join(_MODEL_SUBDIR, "%s_entry_quality_scaler.pkl" % hz)
            if os.path.exists(_stale):
                try:
                    os.remove(_stale)
                    logger.info("[MetaLabelClf] %s 구 스케일러 제거(스케일 미사용 전환)", hz)
                except OSError as _e:
                    logger.warning("[MetaLabelClf] %s 구 스케일러 제거 실패(무해): %s", hz, _e)
        final_model = HistGradientBoostingClassifier(**HGB_PARAMS)
        final_model.fit(X_fit, y, sample_weight=compute_sample_weight("balanced", y))

        _model_path = os.path.join(_MODEL_SUBDIR, "%s_entry_quality.pkl" % hz)
        _tmp = _model_path + ".tmp"
        with open(_tmp, "wb") as f:
            pickle.dump(final_model, f, protocol=4)
        os.replace(_tmp, _model_path)

        _fn_path = os.path.join(_MODEL_SUBDIR, "%s_entry_quality_features.pkl" % hz)
        _tmp_f = _fn_path + ".tmp"
        with open(_tmp_f, "wb") as f:
            pickle.dump(list(feat_names), f, protocol=4)
        os.replace(_tmp_f, _fn_path)

        pos_rate = float(y.mean())
        _auc_main = aucs.get("auc_mixed")
        logger.info(
            "[MetaLabelClf] %s AUC=%s n=%d pos_rate=%.3f "
            "| 방향성 AUC=%s 순이익 AUC=%s 강한추종 AUC=%s (방향성 n=%s) "
            "| 스키마 %d개(%s) nan=%s scaler=%s purged=%s",
            hz, ("%.4f" % _auc_main) if _auc_main is not None else "N/A",
            len(X), pos_rate,
            _fmt(aucs.get("auc_directional")), _fmt(aucs.get("auc_net_directional")),
            _fmt(aucs.get("auc_strong_directional")), aucs.get("n_oof_directional", "—"),
            len(feat_names), (max(str(r["ts"])[:10] for r in records) if records else "—"),
            use_nan, use_scaler, use_purged,
        )
        results[hz] = {
            "ok": True,
            # 하위호환 — 종전 키 `auc`는 auc_mixed를 가리킨다.
            # 🔴 개선 근거로 쓰지 말 것: FLAT 행이 만드는 착시다(490차 실험 발견 ①).
            "auc": _auc_main,
            "n_samples": len(X),
            "pos_rate": round(pos_rate, 4),
            "n_features": len(feat_names),
            "schema_day": (max(str(r["ts"])[:10] for r in records) if records else None),
            "scaled": use_scaler,
            "nan_fill": use_nan,
            "purged_cv": use_purged,
            "embargo_rows": embargo,
        }
        results[hz].update(aucs)

    metrics_path = _write_metrics_sidecar(results)
    return {"ok": True, "horizons": results, "model_dir": _MODEL_SUBDIR,
            "metrics_path": metrics_path}


class EntryQualityScorer:
    """저장된 호라이즌별 진입품질 분류기를 로드해 실시간 확률 스코어링.

    실거래 게이트에는 아직 연결되지 않음 — MetaGate가 섀도우 신호로만 사용한다.
    """

    def __init__(self, model_dir: str = _MODEL_SUBDIR):
        self._model_dir = model_dir
        self._cache: Dict[str, Optional[tuple]] = {}  # hz -> (model, scaler, feat_names) 또는 None(미존재 캐시)
        # [357차] 스코어링 실패 무음 방지 — 호라이즌당 최초 1회만 WARNING, 이후 debug.
        # ([2] Meta-Gate 채널이 로드 실패 debug 무음으로 캠페인 전 기간 표본 0이었던 재발 방지)
        self._score_warned: set = set()

    def _load(self, horizon: str):
        if horizon in self._cache:
            return self._cache[horizon]
        model_path = os.path.join(self._model_dir, "%s_entry_quality.pkl" % horizon)
        scaler_path = os.path.join(self._model_dir, "%s_entry_quality_scaler.pkl" % horizon)
        fn_path = os.path.join(self._model_dir, "%s_entry_quality_features.pkl" % horizon)
        # [MW0602 490차 / P0-③] 스케일러는 **선택**이다 — HGB는 트리라 스케일 불변이고,
        # NaN 채움과 만나면 전-NaN 열에서 오히려 해가 된다. 학습본이 스케일러를 쓰지
        # 않았으면(`training_metrics.json:scaled=false`) 파일이 남아 있어도 적용하지 않는다.
        # ⚠ 하위호환: 사이드카가 없으면 **종전대로 스케일러를 요구**한다 —
        #   재학습 전 구 모델의 서빙이 조용히 달라지면 안 된다.
        want_scaled = self._scaled_flag(horizon)
        need = [model_path, fn_path] + ([scaler_path] if want_scaled else [])
        if not all(os.path.exists(p) for p in need):
            self._cache[horizon] = None
            return None
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            scaler = None
            if want_scaled:
                with open(scaler_path, "rb") as f:
                    scaler = pickle.load(f)
            with open(fn_path, "rb") as f:
                feat_names = pickle.load(f)
            bundle = (model, scaler, feat_names)
            self._cache[horizon] = bundle
            return bundle
        except Exception as e:
            logger.warning("[MetaLabelClf] %s 모델 로드 실패: %s", horizon, e)
            self._cache[horizon] = None
            return None

    def _scaled_flag(self, horizon: str) -> bool:
        """이 호라이즌 학습본이 스케일러를 썼는가 — 사이드카 선언 우선.

        사이드카가 없거나 해당 호라이즌 항목이 없으면 **True**(종전 동작)를 돌려준다.
        """
        try:
            m = load_training_metrics()
            hz_meta = ((m.get("latest") or {}).get("horizons") or {}).get(horizon)
            if isinstance(hz_meta, dict) and "scaled" in hz_meta:
                return bool(hz_meta["scaled"])
        except Exception:
            pass
        return True

    def score(self, horizon: str, features: Dict) -> Optional[float]:
        """진입품질(수익 확률) 스코어. 모델 미존재/오류 시 None.

        [MW0602 490차 / P0-①] 결측 채움이 학습과 **같아야** 한다 — 학습이 NaN으로
        채웠으면 서빙도 NaN이어야 한다. 0.0으로 채우면 모델이 "값이 0인 관측"으로
        오해한다(학습/서빙 괴리).
        """
        bundle = self._load(horizon)
        if bundle is None:
            return None
        model, scaler, feat_names = bundle
        _miss = np.nan if bool(_TRAIN_CFG.get("nan_fill", False)) else 0.0
        try:
            row = []
            for f in feat_names:
                v = features.get(f)
                if v is None:
                    row.append(_miss)
                    continue
                try:
                    row.append(float(v))
                except (TypeError, ValueError):
                    row.append(_miss)
            x = np.array([row], dtype=np.float32)
            x_s = scaler.transform(x) if scaler is not None else x
            return float(model.predict_proba(x_s)[0, 1])
        except Exception as e:
            if horizon not in self._score_warned:
                self._score_warned.add(horizon)
                logger.warning("[MetaLabelClf] %s 스코어링 실패(세션 최초 1회 경고): %s", horizon, e)
            else:
                logger.debug("[MetaLabelClf] %s 스코어링 실패: %s", horizon, e)
            return None

    def reload(self, horizon: Optional[str] = None) -> None:
        """캐시 무효화 — 재학습 후 최신 모델 반영."""
        if horizon:
            self._cache.pop(horizon, None)
        else:
            self._cache.clear()


_scorer: Optional[EntryQualityScorer] = None


def get_entry_quality_scorer() -> EntryQualityScorer:
    global _scorer
    if _scorer is None:
        _scorer = EntryQualityScorer()
    return _scorer
