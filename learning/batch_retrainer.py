# learning/batch_retrainer.py — GBM 배치 재학습기
"""
주간/월간 전체 모델 재학습

온라인 학습(SGD)은 매 분봉 실시간 — 이 모듈은 배치 GBM 담당

재학습 트리거:
  주간: Walk-Forward 검증 갱신 (매주 월요일 장 전)
  월간: 전체 GBM 모델 재학습 (매월 1일)
  수동: batch_retrainer.retrain_now() 호출

재학습 절차:
  1. DB에서 최근 N주 데이터 로드
  2. target_builder 로 라벨 생성
  3. feature_builder 로 피처 계산
  4. 각 호라이즌 GBM 학습 + 교차검증
  5. 성능 향상 시에만 모델 교체 (안전 교체)
  6. HTML 리포트 생성

Python 3.7 32-bit 호환 (scikit-learn GradientBoostingClassifier)
"""
import os
import logging
import datetime
import pickle
from typing import Optional, Dict, List

import numpy as np

try:
    from sklearn.ensemble import (
        GradientBoostingClassifier, RandomForestClassifier,
        HistGradientBoostingClassifier,
    )
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import accuracy_score, roc_auc_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.utils.class_weight import compute_sample_weight
    _SKLEARN_OK = True
    # HistGBM 가용 여부 별도 확인 (sklearn 0.21+ 필요, 1.0.2에서 확인됨)
    try:
        _test = HistGradientBoostingClassifier(max_iter=1)
        _HIST_GBM_OK = True
    except Exception:
        _HIST_GBM_OK = False
except ImportError:
    _SKLEARN_OK = False
    _HIST_GBM_OK = False

from config.settings import (
    MODEL_DIR, HORIZON_DIR, SCALER_DIR, HORIZONS, DB_DIR,
    GBM_WEIGHT_DEFAULT, GBM_MIN_SAMPLES_LEAF,
    RETRAIN_WEEKS_BACK, MAX_TRAIN_BARS, RAW_DATA_PRUNE_WEEKS,
    EOD_MODEL_GUARD_DROP_TOLERANCE, EOD_MODEL_GUARD_DROP_TOLERANCE_DEFAULT,
    EOD_GUARD_FAIR_HOLDOUT,
)
from config.constants import DIRECTION_UP, DIRECTION_DOWN, DIRECTION_FLAT
from learning.eod_model_guard import evaluate_model_replace

logger = logging.getLogger("LEARNING")


# P6b: 경로 조건부 레이블 파라미터
# UP/DOWN 후보이더라도 중간 경로에서 이 비율 이상 역행하면 FLAT 처리
# 0.45 → 0.55: FLAT 과다 레이블 방지 (11시 반전 시 FLAT 고착 CB③ 발동 원인)
# 임계값의 55% 이상 역행 시만 FLAT → FLAT 비율 줄고 UP/DOWN 예측 증가
PATH_LABEL_RATIO: float = 0.55

# 호라이즌별 경로 조건부 레이블 비율 — 장기 호라이즌일수록 중간 역행이 자연스럽게 많아
# 30m는 0.55 기준이 FL 레이블을 과소 생성해 GBM이 UP/DN을 과잉 예측하는 문제 해소
PATH_LABEL_RATIO_BY_HZ: dict = {
    "1m": 0.60, "3m": 0.58, "5m": 0.55,
    "10m": 0.52, "15m": 0.50, "30m": 0.45,
}


def _path_conditioned_label(
    close_map: dict,
    ts: str,
    h_min: int,
    threshold: float,
    path_ratio: float = PATH_LABEL_RATIO,
) -> int:
    """
    경로 조건부 레이블: T분 후 방향 + 중간 경로 최대 역행폭 조건.

    UP 후보라도 중간에 threshold × path_ratio 이상 하락하면 FLAT.
    DOWN 후보라도 중간에 threshold × path_ratio 이상 상승하면 FLAT.

    경로 데이터 불완전(경계 구간) → build_single_target 방식 fallback.
    """
    c0 = close_map.get(ts)
    if not c0:
        return DIRECTION_FLAT

    future_ts = (
        datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        + datetime.timedelta(minutes=h_min)
    ).strftime("%Y-%m-%d %H:%M:%S")
    cf = close_map.get(future_ts)
    if not cf or threshold <= 0:
        return DIRECTION_FLAT

    end_ret = (cf - c0) / c0

    if end_ret > threshold:  # UP 후보
        # 중간 경로의 최대 하락폭 계산
        path_closes = []
        for m in range(1, h_min):
            mid_ts = (
                datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                + datetime.timedelta(minutes=m)
            ).strftime("%Y-%m-%d %H:%M:%S")
            mc = close_map.get(mid_ts)
            if mc:
                path_closes.append(mc)
        if path_closes:
            max_dd = (min(path_closes) - c0) / c0   # 음수
            if abs(max_dd) > path_ratio * threshold:
                return DIRECTION_FLAT   # 중간 역행 → 노이즈
        return DIRECTION_UP

    elif end_ret < -threshold:  # DOWN 후보
        path_closes = []
        for m in range(1, h_min):
            mid_ts = (
                datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                + datetime.timedelta(minutes=m)
            ).strftime("%Y-%m-%d %H:%M:%S")
            mc = close_map.get(mid_ts)
            if mc:
                path_closes.append(mc)
        if path_closes:
            max_ru = (max(path_closes) - c0) / c0   # 양수
            if max_ru > path_ratio * threshold:
                return DIRECTION_FLAT
        return DIRECTION_DOWN

    return DIRECTION_FLAT

def _leak_overlap_count(train_idx, val_idx, h_min):
    """[MW0601 454차 / ATB-A2] CV 경계 누출 자가진단 — 퍼징 후 0이어야 정상.

    train 표본 i의 라벨은 미래 창 [i+1, i+h_min]을 보고 결정되므로, i + h_min이
    val 시작 위치 이상이면 그 표본은 val 구간의 정답을 이미 본 것이다. 위치(행)
    기반 경량판 — 스펙(docs/Spec for feature/ML Model Labeling) leakage_selftest의
    시각 기반 검사와 달리 행수≈분수 가정을 쓴다(결측 분봉 시 과잉 방향으로만 어긋남).
    진단 전용: 호출부는 경고 로그만 남기고 재학습을 절대 막지 않는다.
    """
    if h_min <= 0 or len(train_idx) == 0 or len(val_idx) == 0:
        return 0
    v0 = int(val_idx[0])
    return int(np.sum(np.asarray(train_idx) + h_min >= v0))


# ── sklearn GBM (HistGBM 불가 시 fallback) ───────────────────────
# 정상 환경(_HIST_GBM_OK=True)에서는 사용 안 됨.
GBM_PARAMS = {
    "n_estimators":     300,
    "max_depth":        5,
    "learning_rate":    0.04,
    "subsample":        0.8,
    "min_samples_leaf": GBM_MIN_SAMPLES_LEAF,
    "random_state":     42,
}
GBM_PARAMS_INTRADAY = {
    "n_estimators":     100,
    "max_depth":        4,
    "learning_rate":    0.08,
    "subsample":        0.8,
    "min_samples_leaf": GBM_MIN_SAMPLES_LEAF,
    "random_state":     42,
}

# ── HistGradientBoostingClassifier (주 경로) ─────────────────────
# 벤치마크 실측 (20k봉×97피처, daemon thread, 20260611):
#   GBM(n=100):     total=272s  main_blocked=253,706ms (93%)
#   HistGBM(n=100): total=  0.6s  main_blocked=559ms   (0.2%)
# C++ OpenMP 백엔드가 fit() 중 GIL을 해제 → S2 5s 차단 근본 제거
HIST_GBM_PARAMS = {
    "max_iter":         300,   # GBM n_estimators=300 동등
    "max_depth":        5,
    "learning_rate":    0.04,
    "min_samples_leaf": GBM_MIN_SAMPLES_LEAF,
    "random_state":     42,
}
HIST_GBM_PARAMS_INTRADAY = {
    "max_iter":         100,
    "max_depth":        4,
    "learning_rate":    0.08,
    "min_samples_leaf": GBM_MIN_SAMPLES_LEAF,
    "random_state":     42,
}

# 최소 학습 데이터 (분봉 수)
# RETRAIN_WEEKS_BACK=26 기준 실측 ~44,000봉 → 충분히 초과
# (구 weeks_back=10 기준 ~15,750봉으로 간신히 달성 → 26주로 확장)
MIN_TRAIN_BARS = 15000

# 장중 재학습 최대 봉 수: 최근 ~2.5주 (최신 데이터 우선 + 속도 우선)
#
# [404차 후속2] 20,000 → 4,800으로 정정. 20,000봉은 실측 54거래일(10.8주)로
# 위 주석의 의도(2.5주)와 4배 어긋나 있었다 — 데이터가 누적되면서 같은 상수가
# 뜻하는 기간이 늘어난 것. 그 결과 "오늘"이 학습표본의 1.5%, 연속 재학습 간
# 신규분은 0.29%뿐이라 DriftRetrain이 목표하는 "장중 레짐 변화 반영"이
# 구조적으로 불가능했다. 4,800 = 12.5거래일 × 384봉(최근 15거래일 중앙값).
#   근거: dev_memory/DECISION_LOG.md 2026-08-01(404차 후속2) 항목.
#   롤백: 이 값을 20_000으로 되돌리면 즉시 종전 동작.
MAX_TRAIN_BARS_INTRADAY = 4_800

# [404차 후속2] CV 폴드 학습셋 상한 — 32-bit Python 메모리 방어 전용.
#
# 원래 이 목적에도 MAX_TRAIN_BARS_INTRADAY를 재사용하고 있었으나, 두 상수는
# 목적이 다르다(학습 창 크기 vs OOM 방어). 분리하지 않고 위 값을 4,800으로
# 낮추면 PreRetrain(08:55, intraday=False·full_cv=False)의 CV 폴드 학습셋까지
# 20,000→4,800으로 조용히 축소돼 의도치 않은 회귀가 된다 — 실제 호출 경로
# 확인 결과 retrain_intraday.py가 full_cv를 넘기지 않아(기본 False) 해당됨.
# 여기서 종전 값(20,000)을 그대로 유지해 그 경로의 동작을 보존한다.
# (EOD는 full_cv=True라 이 캡 자체를 타지 않는다 — 영향 없음)
MAX_CV_FOLD_BARS = 20_000

# Phase 2: 호라이즌별 학습 최소 데이터 — 시간 등가 기준 (72k 봉 기준 전 호라이즌 충족)
MIN_TRAIN_BARS_PER_HORIZON = {
    "1m": 15000, "3m": 5000, "5m": 3000,
    "10m": 1500, "15m": 1000, "30m": 500,
}

# Phase 2-D: 호라이즌별 학습 윈도우 상한 (봉 수)
# 단기 모델은 최근 데이터로 현재 레짐 반응, 장기 모델은 넓은 역사적 맥락 활용.
# None  = weeks_back 전체 사용 (변경 없음)
# int   = 가장 최근 N봉 상한. MIN_TRAIN_BARS_PER_HORIZON 미달 시 전체 사용으로 자동 후퇴.
# Stage 3(50일+ go-forward 누적) 이후 단기 효과 발현:
#   3m 누적이 ~30k봉에 달할 때 window=5000 → 최근 5주 데이터만 사용.
# V8 계획서 원안(90/60/48)은 온라인학습 메모리 개념이라 배치학습 MIN_BARS 미달 → 현재 값으로 조정.
TRAINING_WINDOW_BARS = {
    "1m":   None,   # Phase 2 미사용 (raw_features 경로)
    "3m":   5000,   # 최근 5k봉 상한 — Stage 3 이후 단기 반응 효과 발현
    "5m":   3000,   # 최근 3k봉 상한
    "10m":  None,   # session_all 의도: 데이터 충분 시 세션 필터 구현 예정
    "15m":  None,
    "30m":  None,   # multi_day: weeks_back 전체로 장기 맥락 최대화
}

# P0: 호라이즌별 FLAT 상한 — 동적 가중치에서도 FLAT 과잉 억제 유지
# 3m/5m: 0.75/0.85 → 0.55 하향 근거:
#   HORIZON_THRESHOLDS["3m"]=0.060% 기준 훈련 데이터에서 FL≈47%.
#   inv_freq_FL=0.71 < FLAT_CAP=0.75 → 캡 미발동 → FL이 UP(0.65)보다 9% 높은 가중치.
#   결과: GBM FL 과잉 예측 → 09:00~10:00 UP=0건(상승장에도 불구).
#   0.55로 하향 시 FL_w=0.55 < UP_w=0.65 → UP/DN 상대 강화, FL 균형.
_FLAT_CAP = {
    "1m": 0.75, "3m": 0.55, "5m": 0.55,
    "10m": 0.65, "15m": 0.60, "30m": 0.55,
}
_DYN_HALFLIFE   = 70    # (구값·하한 전용) 165차 도입 100 → 186차 70. 아래 주석 참조.
_DYN_CLIP_RATIO = 3.0   # 최대 가중치 = 중간값 × 배율 (역보정 폭발 방지)

# [404차 후속2] 시간감쇠 반감기를 절대 봉수 → 학습창 길이 비례로 전환.
#
# 무엇이 문제였나 (설계 의도 자체는 정상 — 오해 주의):
#   decay는 per-sample 가중치가 아니라 **클래스 빈도를 최근 구간 기준으로 추정**
#   하는 데만 쓰인다. 이는 165차(커밋 88cf7fd) "동적 역빈도+시간감쇠 class weight"의
#   명시적 설계이며 구현 누락이 아니다. 반환되는 per-sample 값은 라벨별 클래스
#   가중치이고, 그게 sklearn sample_weight의 올바른 사용법이다.
#
#   진짜 결함은 반감기 70봉이 **유효표본 101봉**밖에 되지 않는다는 점이다. 그
#   101봉에서 추정한 클래스 가중치가 학습창 전체(4,800~39,209봉)에 적용된다.
#   가장 오래된 표본의 감쇠 가중치는 EOD 기준 2^-560으로 언더플로해 0이 된다.
#   실측(연속 재학습 5시점, 58봉 간격):
#     5m DOWN 가중치 1.217~2.142 (범위 0.925, ±38%)
#     1m DOWN 가중치 0.857~1.419 (범위 0.562)
#   즉 재학습마다 클래스 가중치가 요동쳐 모델 예측이 함께 흔들린다 — 404차 후속이
#   측정한 "연속 재학습 간 예측 불일치 16~22%"의 원인 중 하나.
#
# 해결: 반감기를 max(n × _DYN_HALFLIFE_FRAC, _DYN_HALFLIFE)로 계산한다.
#   - 학습창이 커지면 반감기도 비례해 커져 유효표본이 창의 약 36%로 유지된다
#     (기하급수 합: ESS ≈ hl/ln2 = 0.361n when hl = n/4).
#   - 소표본(n < 280)에서는 하한 70이 그대로 적용돼 종전 동작과 동일 —
#     온라인/테스트 경로 회귀 없음.
#   - "최근 분포를 반영한다"는 165차 의도는 유지된다(여전히 최근 가중).
#   근거: dev_memory/DECISION_LOG.md 2026-08-01(404차 후속2) 항목.
#   롤백: _DYN_HALFLIFE_FRAC = 0.0 으로 두면 하한 70만 남아 종전 동작 복원.
_DYN_HALFLIFE_FRAC = 0.25


def _resolve_halflife(n: int) -> float:
    """[404차 후속2] 학습창 길이에 비례한 시간감쇠 반감기.

    n이 작으면 하한(_DYN_HALFLIFE=70)이 적용돼 종전 동작을 그대로 보존한다.
    multi_horizon_model._resolve_halflife 와 동일 로직 유지 필수.
    """
    return max(float(n) * _DYN_HALFLIFE_FRAC, float(_DYN_HALFLIFE), 1.0)


def _make_sample_weight(y: np.ndarray, horizon_key: str) -> np.ndarray:
    """
    P0: 동적 역빈도 + 시간감쇠 class weight (반환은 per-sample 배열).

    y는 시간순 정렬 레이블 (DB ORDER BY ts 보장).
    decay는 **클래스 빈도 추정에만** 쓰인다(per-sample 감쇠가 아님 — 165차 설계).
    DOWN 과다 시 DN 가중치 자동 감소. 클리핑 = 중간값×3으로 역보정 폭발 방지.
    반감기는 _resolve_halflife(n) — 학습창 비례(404차 후속2).
    multi_horizon_model._make_sample_weight 와 동일 로직 유지 필수.
    """
    n = len(y)
    if n == 0:
        return np.ones(0, dtype=np.float64)

    decay = np.exp(-np.arange(n)[::-1] * (np.log(2) / _resolve_halflife(n)))

    weighted_counts = {}
    for cls in [DIRECTION_FLAT, DIRECTION_UP, DIRECTION_DOWN]:
        mask = (y == cls)
        weighted_counts[cls] = float(decay[mask].sum()) if mask.any() else 1e-6

    total = sum(weighted_counts.values())
    inv_freq = {cls: total / (3.0 * cnt) for cls, cnt in weighted_counts.items()}

    median_w = sorted(inv_freq.values())[1]
    max_w = median_w * _DYN_CLIP_RATIO
    weights = {cls: min(v, max_w) for cls, v in inv_freq.items()}

    flat_cap = _FLAT_CAP.get(horizon_key)
    if flat_cap is not None:
        weights[DIRECTION_FLAT] = min(weights[DIRECTION_FLAT], flat_cap)

    logger.debug(
        "[Retrain] %s 동적가중치 FL=%.2f UP=%.2f DN=%.2f",
        horizon_key,
        weights.get(DIRECTION_FLAT, 1.0),
        weights.get(DIRECTION_UP, 1.0),
        weights.get(DIRECTION_DOWN, 1.0),
    )
    return np.array([weights.get(int(lbl), 1.0) for lbl in y], dtype=np.float64)


# ── [260704 감사 P1] Triple-barrier 섀도우 병행 학습 ─────────────────
# 프로덕션 champion 모델(gbm_{hz}.pkl)과 완전히 분리된 디렉터리에 저장 —
# 실거래 의사결정에 전혀 사용되지 않는 순수 병행(shadow) 트랙.
SHADOW_TB_DIRNAME = "shadow_triple_barrier"


def _shadow_model_factory():
    """섀도우 학습 전용 모델 팩토리 — 프로덕션 정규 재학습과 동일 파라미터(비-intraday)."""
    if _HIST_GBM_OK:
        def _make():
            return HistGradientBoostingClassifier(**HIST_GBM_PARAMS)
    else:
        def _make():
            return GradientBoostingClassifier(**GBM_PARAMS)
    return _make


def _cusum_filter(records, close_map, h_mult=0.7):
    """
    P1: CUSUM 이벤트 필터.

    연속 하락/상승 구간에서 동일 방향 신호가 반복 학습되는 것을 방지.
    CUSUM 누적통계가 동적 임계값 h를 초과하는 시점만 선택.
    선택 결과가 원본의 30% 미만이면 전체 반환 (데이터 부족 안전망).

    records: [(ts, feat_dict), ...]  — 시간순 정렬
    close_map: {ts: float}
    h_mult: 임계값 배율 (평균 표준편차 × h_mult)
      0.5 → 0.7 변경 근거: 6/12 장전 재학습에서 40211→12067봉(70% 제거)으로
      안전망 30% 경계선에서 학습 데이터 부족 경고 상시 발생. h_mult 상향으로
      이벤트 선택 기준 완화 → ~50% 유지 목표 (최소 20000봉 확보).
    """
    n = len(records)
    if n < 40:
        return list(range(n))

    closes = [close_map.get(ts, 0.0) for ts, _ in records]

    stds = []
    for i in range(20, n):
        window = closes[i - 20:i]
        mean_w = sum(window) / 20.0
        if mean_w <= 0:
            continue
        var_w = sum((x - mean_w) ** 2 for x in window) / 19.0
        stds.append(var_w ** 0.5)

    if not stds:
        return list(range(n))
    h = (sum(stds) / len(stds)) * h_mult
    if h <= 0:
        return list(range(n))

    selected = []
    s_pos, s_neg = 0.0, 0.0
    for i in range(1, n):
        prev_c, curr_c = closes[i - 1], closes[i]
        if prev_c <= 0 or curr_c <= 0:
            continue
        diff = curr_c - prev_c
        s_pos = max(0.0, s_pos + diff)
        s_neg = min(0.0, s_neg + diff)
        if s_pos > h or s_neg < -h:
            selected.append(i)
            s_pos = s_neg = 0.0

    if len(selected) < n * 0.30:
        logger.info(
            "[CUSUM] 이벤트 %d/%d (%.1f%%) < 30%% — 전체 사용",
            len(selected), n, 100.0 * len(selected) / max(n, 1),
        )
        return list(range(n))

    logger.info(
        "[CUSUM] %d → %d봉 (%.1f%% 유지)",
        n, len(selected), 100.0 * len(selected) / max(n, 1),
    )
    return selected


class BatchRetrainer:
    """
    GBM 모델 배치 재학습기

    사용:
        retrainer = BatchRetrainer()
        result    = retrainer.retrain_now(weeks_back=RETRAIN_WEEKS_BACK)
    """

    def __init__(self, model_dir: str = HORIZON_DIR, scaler_dir: str = SCALER_DIR):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)

        # [P0 260719] scaler_dir을 model_dir과 별개로 항상 전역 SCALER_DIR에 고정하던
        # 버그 수정 — 346차 통합테스트가 model_dir만 임시경로로 격리하고 스케일러는
        # 격리 못 해 라이브 model/scaler/*.pkl에 10피처 합성테스트 스케일러가 새어나가
        # 프로덕션 6개 호라이즌 전부가 무력화된 사고(0719 정기점검 발견) 재발 방지.
        # 기본값은 기존과 동일한 SCALER_DIR — 운영 경로에는 영향 없음.
        self.scaler_dir = scaler_dir
        os.makedirs(scaler_dir, exist_ok=True)

        self._last_retrain:  Optional[datetime.datetime] = None
        self._retrain_count: int = 0
        # [MW0602 468차 G-1] 직전 학습이 **실제로 쓴** 레이블 규칙. `_save_model`이
        # 사이드카에 새기고, 런타임(main.py `_model_label_scheme_current`)이 그것으로
        # "지금 적재된 모델이 현행 레이블 학습본인가"를 판정한다.
        # 초기값 None = "모른다" — 그 상태로 기록되면 런타임은 보수(제한 유지)로 간다.
        self._last_label_scheme: Optional[str] = None
        self._last_label_params: dict = {}

    def restore_stats(self, last_retrain_str: str, total_count: int) -> None:
        """재시동 후 이전 세션 이력 복원."""
        if last_retrain_str:
            try:
                self._last_retrain = datetime.datetime.strptime(last_retrain_str, "%Y-%m-%d %H:%M")
            except Exception:
                pass
        if total_count > 0:
            self._retrain_count = total_count

    # ── 재학습 스케줄 판단 ────────────────────────────────────────
    def should_retrain_weekly(self, now: Optional[datetime.datetime] = None) -> bool:
        """월요일 08:50~09:00 사이 주간 재학습 여부"""
        if now is None:
            now = datetime.datetime.now()
        return (
            now.weekday() == 0           # 월요일
            and now.hour == 8
            and 50 <= now.minute < 60
        )

    def should_retrain_monthly(self, now: Optional[datetime.datetime] = None) -> bool:
        """매월 1일 07:00 월간 재학습 여부"""
        if now is None:
            now = datetime.datetime.now()
        return now.day == 1 and now.hour == 7

    # ── 재학습 메인 ───────────────────────────────────────────────
    def retrain_now(
        self,
        X:                    Optional[np.ndarray] = None,
        y_dict:               Optional[Dict[str, np.ndarray]] = None,
        feature_names:        Optional[List[str]] = None,
        weeks_back:           int = RETRAIN_WEEKS_BACK,
        force:                bool = False,
        use_horizon_features: bool = False,
        intraday:             bool = False,
        full_cv:              bool = False,
        horizons:             Optional[List[str]] = None,
    ) -> Dict:
        """
        GBM 모델 전체 재학습

        Args:
            X:                    피처 행렬 (None이면 DB에서 로드)
            y_dict:               {horizon: label_array} (None이면 DB에서 로드)
            weeks_back:           학습 기간 (주)
            force:                성능 저하여도 강제 교체
            use_horizon_features: Phase 2 경로 활성화 — raw_features_horizon 테이블 사용
            intraday:             True이면 경량 파라미터 사용 (장중 GIL 차단 방지)

        Returns:
            재학습 결과 딕셔너리
        """
        if not _SKLEARN_OK:
            return {"ok": False, "error": "scikit-learn 미설치"}

        # [MW0602 468차 G-1] 호출자가 X/y를 직접 넘기면 아래 두 레이블 생성 경로가 전부
        # 건너뛰어진다 — 그때 직전 학습의 값이 남아 있으면 **이번 pkl의 레이블 규칙인 양
        # 사이드카에 새겨진다.** 매 호출 초기화해서 그 경우 `None`(=모른다)이 기록되게
        # 한다. 런타임은 모르면 보수(사이즈 제한 유지)로 가므로 안전한 쪽으로 틀린다.
        if X is not None and y_dict is not None:
            self._last_label_scheme = None
            self._last_label_params = {}

        logger.info(
            "[Retrain] 배치 재학습 시작 (weeks_back=%d, phase2=%s, intraday=%s)",
            weeks_back, use_horizon_features, intraday,
        )
        start_time = datetime.datetime.now()

        # Phase 2: 호라이즌별 독립 X로 재학습
        if use_horizon_features and (X is None or y_dict is None):
            if self._has_horizon_features_table():
                return self._retrain_phase2(weeks_back, force, start_time, full_cv=full_cv)
            else:
                logger.warning("[Retrain] raw_features_horizon 테이블 없음 — Phase 1 경로로 fallback")

        # 데이터 로드 (Phase 0/1 경로)
        if X is None or y_dict is None:
            X, y_dict, feature_names = self._load_from_db(weeks_back, intraday=intraday)

        # [404차 후속2] intraday는 학습창 자체가 MAX_TRAIN_BARS_INTRADAY로 설계돼
        # 있으므로 MIN_TRAIN_BARS(15,000 — 26주 전량 로드 기준)를 그대로 요구하면
        # 구조적으로 항상 미달한다. 창 크기를 20,000→4,800으로 정정하면서 드러난
        # 결합이다(종전에는 20,000 > 15,000이라 우연히 통과하고 있었을 뿐).
        # _load_from_db가 절단 **전에** 이미 MIN_TRAIN_BARS를 검사하므로(하단 참조)
        # 여기서 확인할 것은 "완전한 장중 창을 확보했는가"뿐이다.
        # 이 정정이 없으면 DriftRetrain·WarmupRetrain·EKS해제·ExchangeCB 재학습 등
        # 모든 intraday 경로가 ok=False로 전량 실패한다(실측으로 확인).
        _min_required = MAX_TRAIN_BARS_INTRADAY if intraday else MIN_TRAIN_BARS
        if X is None or len(X) < _min_required:
            msg = "학습 데이터 부족 ({} < {})".format(
                len(X) if X is not None else 0, _min_required
            )
            logger.warning("[Retrain] %s", msg)
            return {"ok": False, "error": msg}

        # 장중 모드: 최신 데이터 MAX_TRAIN_BARS_INTRADAY 봉만 사용 (GIL 블로킹 시간 비례 단축)
        if intraday and len(X) > MAX_TRAIN_BARS_INTRADAY:
            logger.info(
                "[Retrain] 장중 경량 모드: %d → %d봉 (최신 데이터 우선)", len(X), MAX_TRAIN_BARS_INTRADAY
            )
            X = X[-MAX_TRAIN_BARS_INTRADAY:]
            y_dict = {h: y[-MAX_TRAIN_BARS_INTRADAY:] for h, y in y_dict.items()}
            # [MW0602 457차] ts 목록도 같이 잘라 X와의 행 정렬을 유지한다.
            _tsl = getattr(self, "_last_train_ts", None)
            if _tsl:
                self._last_train_ts = _tsl[-MAX_TRAIN_BARS_INTRADAY:]
                self._last_train_end_ts = self._last_train_ts[-1]
                self._last_train_start_ts = self._last_train_ts[0]

        if feature_names is None:
            feature_names = ["feature_{}".format(i) for i in range(X.shape[1])]

        # Robust 전처리 — 예측 경로(predict_proba)와 동일 변환 적용 (일관성 보장)
        from model.multi_horizon_model import apply_robust_preprocess
        X = apply_robust_preprocess(X, feature_names)

        # Phase C: 호라이즌별 피처셋 레지스트리 로드
        try:
            from features.horizon_feature_registry import get_available_feature_set
            _registry_ok = True
        except ImportError:
            _registry_ok = False

        # [MW0602 457차] 교체 스코프 — None이면 전체(종전 동작). ConstOut 유발
        # 재학습만 트리거 호라이즌으로 좁힌다. 근거·부작용은
        # config/settings.py CONST_OUT_RETRAIN_SCOPED 주석.
        _scope = set(horizons) if horizons else None
        if _scope:
            _skipped = [h for h in HORIZONS if h not in _scope]
            logger.info(
                "[Retrain] 교체 스코프 제한: %s 만 재학습 (스킵 %s — 구모델 유지)",
                sorted(_scope), _skipped,
            )

        results = {}
        for horizon_key in HORIZONS:
            if horizon_key not in y_dict:
                continue
            if _scope and horizon_key not in _scope:
                continue
            y = y_dict[horizon_key]
            if len(y) != len(X):
                continue

            # 호라이즌별 피처 슬라이싱 (Phase C)
            if _registry_ok:
                h_names = get_available_feature_set(horizon_key, feature_names)
            else:
                h_names = None

            if h_names and len(h_names) < len(feature_names):
                # 해당 호라이즌 전용 컬럼만 추출
                h_idx = [feature_names.index(n) for n in h_names]
                X_h = X[:, h_idx]
                logger.info(
                    "[Retrain] %s 호라이즌 피처 슬라이싱: %d → %d개",
                    horizon_key, len(feature_names), len(h_names),
                )
            else:
                X_h = X
                h_names = feature_names

            result = self._train_horizon(
                horizon_key,
                X_h,
                y,
                feature_names=h_names,
                force=force,
                intraday=intraday,
                full_cv=full_cv,
                X_full=X if X_h is not X else None,
                h_idx=h_idx if X_h is not X else None,
            )
            results[horizon_key] = result

            # 호라이즌 전용 pkl 저장 (Phase C) — 모델이 실제 교체된 경우에만 저장
            # 미교체 시 저장하면 구 모델(97피처)과 feature_names_hz(12피처) 불일치 발생
            # → 다음 _load_all에서 _hz_feat_indices=12, model.n_features_in_=97 → ERR-FATAL
            if result.get("replaced"):
                self._save_feature_names(h_names, horizon_key=horizon_key)

        # 공유 pkl도 유지 (backward compat: 구 모델·ScalerWarmup 경로)
        self._save_feature_names(feature_names)

        # P6c: RF 이종 앙상블 학습 — 장중 모드에서는 스킵 (GIL 블로킹 추가 방지)
        if intraday:
            logger.info("[Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)")
        else:
            try:
                from model.rf_horizon_model import RFHorizonModel
                rf_model = RFHorizonModel(self.model_dir)
                rf_model.train(X, y_dict, feature_names)
                if rf_model.is_ready():
                    # [346차] EOD 모델가드 — GBM과 동일 원칙을 OOB에 적용. rf_horizons.pkl은
                    # 6개 호라이즌이 한 파일에 묶여 있어(GBM처럼 호라이즌별 개별 파일이 아님)
                    # 저장 직전에 호라이즌 슬롯 단위로 override_horizon()해 부분 유지한다.
                    if not force:
                        _old_rf = RFHorizonModel(self.model_dir)
                        _old_rf_loaded = _old_rf.load_all()
                        _old_oob = _old_rf.get_oob_scores() if _old_rf_loaded else {}
                        for _hz, _new_oob in rf_model.get_oob_scores().items():
                            _rf_old_acc = _old_oob.get(_hz, 0.0)
                            _rf_ok, _rf_reason = evaluate_model_replace(
                                _hz, _new_oob, _rf_old_acc,
                                EOD_MODEL_GUARD_DROP_TOLERANCE, EOD_MODEL_GUARD_DROP_TOLERANCE_DEFAULT,
                            )
                            if not _rf_ok:
                                logger.warning(
                                    "[Retrain] RF %s 교체 보류(EOD 모델가드) — %s — "
                                    "참고용 저장, 구모델 유지", _hz, _rf_reason,
                                )
                                self._save_rejected_rf_model(
                                    _hz, rf_model.get_model(_hz), _new_oob, _rf_old_acc,
                                )
                                if _old_rf_loaded and _old_rf.get_model(_hz) is not None:
                                    rf_model.override_horizon(
                                        _hz, _old_rf.get_model(_hz), _rf_old_acc,
                                    )
                                try:
                                    from utils.notify import notify
                                    notify(
                                        "[EOD 모델가드] RF %s 교체 보류 — %s (참고용 저장, 구모델 유지)"
                                        % (_hz, _rf_reason),
                                        level="WARNING",
                                    )
                                except Exception as _rne:
                                    logger.debug("[Retrain] RF 알림 실패 (무해): %s", _rne)
                    rf_model.save_all()
                    logger.info("[Retrain] RF 학습 완료 OOB=%s", rf_model.get_oob_scores())
            except Exception as _rf_exc:
                logger.warning("[Retrain] RF 학습 실패 (GBM 계속 사용): %s", _rf_exc)

        elapsed = (datetime.datetime.now() - start_time).total_seconds()
        self._last_retrain  = datetime.datetime.now()
        self._retrain_count += 1

        summary = {
            "ok":           True,
            "retrain_count": self._retrain_count,
            "elapsed_sec":  round(elapsed, 1),
            "data_size":    len(X),
            "horizons":     results,
            "timestamp":    self._last_retrain.strftime("%Y-%m-%d %H:%M"),
        }

        logger.info(
            f"[Retrain] 완료 | {elapsed:.1f}초 | "
            f"성공={sum(1 for r in results.values() if r.get('replaced'))}/"
            f"{len(results)} 호라이즌"
        )
        return summary

    # ── 개별 호라이즌 학습 ────────────────────────────────────────
    def _run_cv_folds(self, X, y, X_full, h_idx, horizon_key, full_cv, make_model):
        """[404차 후속] TimeSeriesSplit(3) 폴드 학습·검증 — `_train_horizon()`의
        기존 EOD 전용 CV 루프를 그대로 추출한 순수 함수다(동작 무변화 리팩터링).

        intraday 계측 CV(§1 아래)가 이 함수를 재사용할 수 있도록 분리했다 —
        이 함수 자체는 반환값을 어디에 쓸지 모르고, 모델 저장·acc.txt 갱신 등
        어떤 부작용도 일으키지 않는다. 호출부가 결과를 판정에 연결할지
        계측에만 쓸지 결정한다.

        Returns: (cv_accs: List[float], val_idx_all: List[int])
        """
        cv_accs = []
        val_idx_all = []
        h_min = HORIZONS.get(horizon_key, 0)
        tscv = TimeSeriesSplit(n_splits=3)
        for train_idx, val_idx in tscv.split(X):
            # [MW0601 454차 / ATB-A1a] 경계 퍼징 — train 꼬리 h_min행의 라벨은
            # val 구간의 미래를 보고 만들어졌다(라벨 창 [i+1, i+h_min]).
            # TimeSeriesSplit이라 셔플 누출은 없지만 이 경계 누출은 남는다.
            # 뒤의 MAX_CV_FOLD_BARS 절단과 X_full[train_idx][-len(X_tr):] 미러는
            # train_idx를 여기서 줄여도 그대로 정합 — 인덱스 기반이므로 무변경.
            if 0 < h_min < len(train_idx):
                train_idx = train_idx[:-h_min]
            _leak = _leak_overlap_count(train_idx, val_idx, h_min)
            if _leak:
                logger.warning(
                    "[LeakGuard] %s fold 퍼징 실패 — train 라벨 %d건이 val 미래와 겹침"
                    " (판정 무영향, 즉시 조사 필요)", horizon_key, _leak,
                )
            X_tr, X_val = X[train_idx], X[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]

            # [404차 후속2] MAX_TRAIN_BARS_INTRADAY → MAX_CV_FOLD_BARS로 교체.
            # 이 절단은 "장중 학습 창 크기"가 아니라 32-bit OOM 방어가 목적이라
            # 상수를 분리했다(상수 정의부 주석 참조). 값은 종전과 동일(20,000)이라
            # 이 지점의 동작은 변하지 않는다.
            if not full_cv and len(X_tr) > MAX_CV_FOLD_BARS:
                X_tr = X_tr[-MAX_CV_FOLD_BARS:]
                y_tr = y_tr[-MAX_CV_FOLD_BARS:]

            if len(np.unique(y_tr)) < 2:
                continue

            # 스케일러는 항상 전체 97개 피처 기준 (predict_proba 경로와 일치)
            X_tr_full = X_full[train_idx][-len(X_tr):] if X_full is not None else X_tr
            X_val_full = X_full[val_idx] if X_full is not None else X_val
            scaler = StandardScaler()
            X_tr_full_s = scaler.fit_transform(X_tr_full)
            X_val_full_s = scaler.transform(X_val_full)
            # GBM은 스케일된 전체 피처에서 호라이즌 전용 열만 추출
            X_tr_s = X_tr_full_s[:, h_idx] if h_idx is not None else X_tr_full_s
            X_val_s = X_val_full_s[:, h_idx] if h_idx is not None else X_val_full_s

            model = make_model()
            model.fit(X_tr_s, y_tr, sample_weight=_make_sample_weight(y_tr, horizon_key))
            acc = accuracy_score(y_val, model.predict(X_val_s))
            cv_accs.append(acc)
            val_idx_all.extend(list(val_idx))
        return cv_accs, val_idx_all

    def _train_horizon(
        self,
        horizon_key: str,
        X:           np.ndarray,
        y:           np.ndarray,
        feature_names: List[str],
        force:       bool = False,
        intraday:    bool = False,
        full_cv:     bool = False,
        X_full:      "Optional[np.ndarray]" = None,
        h_idx:       "Optional[List[int]]"  = None,
    ) -> Dict:
        """
        단일 호라이즌 학습 + 교차검증

        HistGBM 가용 시 HistGradientBoostingClassifier 우선 사용 (GIL-free).
        불가 시 GradientBoostingClassifier fallback.
        intraday=True: 경량 파라미터 + CV 없이 전체 직접 학습.
        """
        # 모델 팩토리 선택 — HistGBM은 GIL을 학습 중 해제 (C++ OpenMP)
        if _HIST_GBM_OK:
            _params = HIST_GBM_PARAMS_INTRADAY if intraday else HIST_GBM_PARAMS
            def _make_model():
                return HistGradientBoostingClassifier(**_params)
        else:
            _params = GBM_PARAMS_INTRADAY if intraday else GBM_PARAMS
            def _make_model():
                return GradientBoostingClassifier(**_params)

        cv_accs = []
        # [403차 종합 P0-4] 각 폴드의 검증 인덱스를 모아 둔다 — 현행 프로덕션 모델을
        # "신규 모델과 똑같은 데이터"로 재채점하기 위함(아래 _measure_incumbent_acc).
        _val_idx_all = []
        if not intraday:
            # 정규 재학습: 시계열 교차검증 3폴드
            # full_cv=False (기본): 32-bit Python 메모리 방어 — fold 훈련 세트를 20k행으로 절단
            #   (Cybos+Qt+데이터수집 동시 실행 구간 — 장중·프리마켓)
            # full_cv=True: Cybos 단절 후 장 마감 재학습 전용 — 캡 해제, 전체 데이터로 정직한 CV
            cv_accs, _val_idx_all = self._run_cv_folds(
                X, y, X_full, h_idx, horizon_key, full_cv, _make_model,
            )
            if not cv_accs:
                return {"ok": False, "error": "교차검증 실패"}

        cv_acc = float(np.mean(cv_accs)) if cv_accs else None

        # [404차 후속] intraday 계측 전용 CV — cv_acc/_val_idx_all(판정·_save_model
        # 경로)에는 절대 연결하지 않는다. 실측 근거(dev_memory/DECISION_LOG.md
        # 404차 후속 §1): 동일 데이터·시드만 다른 재현 분산이 5m 기준 8.83%p로
        # EOD 가드 허용폭(2.5%p)의 3.5배 — 지금 intraday에 가드를 걸면 신호가
        # 아니라 모델 재현 잡음을 판정하게 된다. 그래서 게이트 없이 관찰만 한다.
        # 실패해도 재학습 자체는 절대 막지 않는다(try/except로 완전 격리).
        _intraday_cv_accs, _intraday_val_idx = [], []
        if intraday:
            try:
                _intraday_cv_accs, _intraday_val_idx = self._run_cv_folds(
                    X, y, X_full, h_idx, horizon_key, False, _make_model,
                )
            except Exception as _icv_e:
                logger.debug("[GuardShadow] intraday CV 계측 실패 (무해): %s", _icv_e)

        # 전체 데이터로 최종 학습 (장중 모드: CV 없이 여기만 실행)
        # 스케일러는 97개 전체 피처 기준 — predict_proba의 scaler.transform(97개) 경로와 일치
        _t_scaler_start = datetime.datetime.now()
        final_scaler = StandardScaler()
        X_for_scaler = X_full if X_full is not None else X
        X_for_scaler_scaled = final_scaler.fit_transform(X_for_scaler)
        X_scaled = X_for_scaler_scaled[:, h_idx] if h_idx is not None else X_for_scaler_scaled
        _t_scaler_sec = (datetime.datetime.now() - _t_scaler_start).total_seconds()

        final_model = _make_model()
        _t_fit_start = datetime.datetime.now()
        final_model.fit(X_scaled, y, sample_weight=_make_sample_weight(y, horizon_key))
        _t_fit_sec = (datetime.datetime.now() - _t_fit_start).total_seconds()

        _model_type = "HistGBM" if _HIST_GBM_OK else "GBM"
        _n_feats = X_scaled.shape[1]
        logger.info(
            "[Retrain-Timing] %s %s | n=%d feat=%d | scaler=%.2fs fit=%.2fs",
            _model_type, horizon_key, len(X), _n_feats, _t_scaler_sec, _t_fit_sec,
        )

        # 기존 모델과 성능 비교
        old_acc  = self._load_model_acc(horizon_key)
        replaced = False
        guard_rejected = False

        # ── [403차 종합 P0-4] old_acc 재측정 (섀도 로깅 전용, 판정 무영향) ──────
        # 현행 가드는 acc.txt에 적힌 수치를 old_acc로 쓰는데, 그 수치에는 두 겹의
        # 문제가 있다(MW0601 07-30 실측으로 확인):
        #   ① 분포 불일치 — acc.txt는 그 모델이 교체되던 날의 CV 정확도다. 오늘의
        #      cv_acc는 폭락 4일이 포함된 오늘 데이터에서 나왔다. 데이터가 어려워지면
        #      신규 모델은 구조적으로 항상 진다 → 레짐 전환기에 6/6 전량 보류
        #      (07-30 MW0601: 1m .3805 / 3m .4651 vs 오늘 .2807 / .3196).
        #   ② 대상 부존재 — intraday 재학습은 가드를 건너뛰고(687행) gbm_{h}.pkl을
        #      덮어쓰지만 acc.txt는 보존한다(_save_model, 의도된 동작). 07-30 실측
        #      gbm_*.pkl mtime은 14:52(마지막 intraday)인데 3m의 acc.txt는 7/22자였다.
        #      즉 가드가 비교한 상대는 이미 8회 덮어써져 존재하지 않는 모델이었다.
        # 여기서는 현행 프로덕션 모델을 "신규와 똑같은 검증 폴드"로 재채점해 그
        # 왜곡의 크기를 로그로 드러낸다. 판정에는 아직 쓰지 않는다(§9) — 최소 1주
        # 관측 후 교체 여부를 결정한다.
        _old_acc_live, _live_note = self._measure_incumbent_acc(
            horizon_key, X, y, X_full, h_idx, feature_names, _val_idx_all,
        )
        if not intraday and cv_acc is not None:
            if _old_acc_live is not None:
                logger.info(
                    "[GuardShadow] %s old_acc(acc.txt)=%.4f vs old_acc(동일폴드 재측정)=%.4f "
                    "| new(cv)=%.4f | 왜곡=%+.4f — 판정에는 acc.txt를 사용(섀도)",
                    horizon_key, old_acc, _old_acc_live, cv_acc,
                    old_acc - _old_acc_live,
                )
            else:
                logger.info(
                    "[GuardShadow] %s 재측정 불가 (%s) — acc.txt=%.4f new(cv)=%.4f",
                    horizon_key, _live_note, old_acc, cv_acc,
                )

        # ── [MW0601 405차 P1-1] 공정 홀드아웃 섀도 (판정 무영향) ──────────────
        # 위 GuardShadow는 "현행이 이미 학습한 폴드"로 재채점하므로 현행에 유리하다.
        # 여기서는 최신 구간을 학습에서 완전히 뺀 도전자를 따로 학습해 둘 다 그
        # 구간으로 채점한다. 3거래일 관측 후 old_acc 인자 교체 여부를 수동 결정(§9).
        _fair_new = _fair_old = None
        _fair_n, _fair_note = 0, "미실행"
        _fair_valid = None
        if not intraday and cv_acc is not None:
            _fair_new, _fair_old, _fair_n, _fair_note = self._measure_fair_holdout(
                horizon_key, X, y, X_full, h_idx, feature_names,
                _make_model, _make_sample_weight,
            )
            if _fair_new is not None and _fair_old is not None:
                # [MW0602 457차] 유효성은 _measure_fair_holdout 안에서 판정돼
                # note 앞머리에 "ok"/"무효"로 실린다. 여기서 그 결과를 컬럼으로 뽑는다.
                _fair_valid = 1 if str(_fair_note).startswith("ok") else 0
                logger.info(
                    "[GuardFair] %s 공정홀드아웃(최신 %d봉) new=%.4f vs old=%.4f "
                    "| 격차=%+.4f | acc.txt=%.4f new(cv)=%.4f | %s — 판정 무영향(섀도)",
                    horizon_key, _fair_n, _fair_new, _fair_old,
                    _fair_new - _fair_old, old_acc, cv_acc, _fair_note,
                )
                if not _fair_valid:
                    # 무효 행을 성능차로 읽는 것이 457차가 막으려는 바로 그 오독이다.
                    logger.warning(
                        "[GuardFair] %s ⚠ 이 격차는 성능차가 아니다 — 현행이 홀드아웃을 "
                        "이미 학습했다. 판정·인용 금지 (%s)", horizon_key, _fair_note,
                    )
            else:
                logger.info(
                    "[GuardFair] %s 측정 불가 (%s)", horizon_key, _fair_note,
                )

        # [346차] intraday/force는 가드 자체를 건너뜀(기존 동작 그대로) — intraday는
        # CV 없음(cv_acc=None), force는 명시적 강제 요구(웜업 복구 등). 그 외(EOD 정규
        # 재학습, force=False)만 호라이즌별 허용 하락폭으로 판정한다.
        if intraday or force:
            _guard_ok, _guard_reason = True, "intraday" if intraday else "force"
        else:
            _guard_ok, _guard_reason = evaluate_model_replace(
                horizon_key, cv_acc, old_acc,
                EOD_MODEL_GUARD_DROP_TOLERANCE, EOD_MODEL_GUARD_DROP_TOLERANCE_DEFAULT,
            )

        if _guard_ok:
            _disp_acc = cv_acc if cv_acc is not None else float("nan")
            # [MW0602 457차] 사이드카 메타에 새길 경로 태그. "eod"만 CV 가드를 통과한
            # 모델이고, intraday/force는 검증 없이 교체된 것이다 — GuardFair가 현행을
            # 신뢰할 수 있는지 판정할 때 이 구분이 결정적이다.
            self._save_source = _guard_reason if _guard_reason in ("intraday", "force") else "eod"
            self._save_model(horizon_key, final_model, final_scaler, _disp_acc, feature_names)
            replaced = True
            if intraday:
                logger.info(
                    "[Retrain] %s 교체 (intraday — CV 없음 | fit=%.2fs | old_acc=%.4f)",
                    horizon_key, _t_fit_sec, old_acc,
                )
            else:
                logger.info(f"[Retrain] {horizon_key} 교체 (acc {old_acc:.4f}→{_disp_acc:.4f})")
        else:
            guard_rejected = True
            _disp_acc = cv_acc if cv_acc is not None else float("nan")
            logger.warning(
                "[Retrain] %s 교체 보류(EOD 모델가드) — %s — 참고용 저장, 구모델 유지",
                horizon_key, _guard_reason,
            )
            # [MW0602 464차 P5-b 계측] 이 HOLD가 **유령 기준과의 비교**였는지 명시.
            # 현행 pkl의 457차 메타가 source=intraday(acc_kind=none)면, old_acc로 쓴
            # acc.txt는 이미 파괴된 과거 EOD 모델의 점수다 — "구모델 유지"의 그
            # 구모델은 검증된 적이 없다. 0811 실측: 3m acc.txt=0.4756(7/29 EOD값,
            # 8/1 동결)로 검증된 도전자를 7 EOD 연속 보류시키는 동안 현행 pkl은
            # 무검증 장중본(마지막 13:01)이었다.
            # **판정은 바꾸지 않는다** — 457차가 명시적으로 유보했고 사전등록 채널
            # [22] guard_shadow가 그 결정을 관할한다. 단 [22]의 missed_upgrade_rate는
            # 공정비교 유효행만 세는데 이 모드는 fair_valid=0(현행이 홀드아웃 학습)이라
            # **구조적으로 측정 불능**이다 — 그래서 최소한 로그로는 매일 드러나야 한다.
            # 해소는 1회성 수동 결정(acc.txt 리셋 → 콜드스타트 교체) 몫이다.
            try:
                _inc_meta = self._read_model_meta(horizon_key)
                if _inc_meta and _inc_meta.get("source") in ("intraday", "force"):
                    logger.warning(
                        "[Retrain] %s ⚠ 유령 기준 HOLD — 현행 pkl은 %s 무검증본"
                        "(written_at=%s, acc_kind=%s)인데 비교 기준 acc.txt=%.4f는 "
                        "과거 EOD 모델의 점수다. 이 보류로 살아남는 것은 검증된 적 "
                        "없는 모델이다 — 해소하려면 acc.txt 리셋(콜드스타트) 수동 결정 필요",
                        horizon_key, _inc_meta.get("source"),
                        _inc_meta.get("written_at"), _inc_meta.get("acc_kind"),
                        old_acc,
                    )
            except Exception as _gm_e:
                logger.debug("[Retrain] 유령 기준 계측 실패 (무해): %s", _gm_e)
            self._save_rejected_model(
                horizon_key, final_model, final_scaler, _disp_acc, old_acc, feature_names,
            )
            try:
                from utils.notify import notify
                notify(
                    "[EOD 모델가드] %s 교체 보류 — %s (참고용 저장, 구모델 유지)"
                    % (horizon_key, _guard_reason),
                    level="WARNING",
                )
            except Exception as _ne:
                logger.debug("[Retrain] 알림 실패 (무해): %s", _ne)

        # [404차, P0-4 후속] GuardShadow 영속화 — 지금까지 로그 한 줄로만 존재해
        # 사후 추적이 불가능했다(dev_memory/DECISION_LOG.md 404차 항목). old_acc_live
        # vs new(cv) 공정비교를 DB에 남겨 generate_validation_campaign_report.py가
        # "acc.txt 기준 실제 판정이 공정비교와 얼마나 자주 어긋나는지" 누적 판정할 수
        # 있게 한다. 로그 발생 조건(701행)과 동일하게 EOD 경로에서만 기록한다.
        if not intraday and cv_acc is not None:
            try:
                from utils.db_utils import save_guard_shadow
                save_guard_shadow(
                    ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    horizon=horizon_key,
                    acc_txt=old_acc,
                    old_acc_live=_old_acc_live,
                    new_cv=cv_acc,
                    live_note=_live_note,
                    actual_verdict="REPLACE" if _guard_ok else "HOLD",
                    n_samples=len(X),
                    # [405차 P1-1] 공정 홀드아웃 섀도 — 판정 무영향, 누적 관찰용
                    fair_new=_fair_new, fair_old=_fair_old,
                    fair_hold_bars=(_fair_n or None), fair_note=_fair_note,
                    fair_valid=_fair_valid,   # [MW0602 457차]
                )
            except Exception as _gs_e:
                logger.debug("[GuardShadow] DB 저장 실패 (무해): %s", _gs_e)

        # [404차 후속] intraday 계측 CV 영속화 — source="intraday"로 EOD 행과
        # 분리 저장한다. actual_verdict은 항상 "REPLACE"다(intraday는 가드 자체가
        # 없어 무조건 교체되므로 있는 그대로 기록). fair_verdict은 "EOD처럼
        # 가드를 걸었다면 통과했을지"를 보여주는 참고값일 뿐 어떤 결정에도
        # 관여하지 않는다 — §1 결론(가드 도입 반대)에 따라 지금은 관찰만 한다.
        if intraday and _intraday_cv_accs:
            try:
                _intraday_cv_acc = float(np.mean(_intraday_cv_accs))
                _intraday_old_live, _intraday_note = self._measure_incumbent_acc(
                    horizon_key, X, y, X_full, h_idx, feature_names, _intraday_val_idx,
                )
                from utils.db_utils import save_guard_shadow
                save_guard_shadow(
                    ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    horizon=horizon_key,
                    acc_txt=old_acc,
                    old_acc_live=_intraday_old_live,
                    new_cv=_intraday_cv_acc,
                    live_note=_intraday_note,
                    actual_verdict="REPLACE",
                    n_samples=len(X),
                    source="intraday",
                )
            except Exception as _igs_e:
                logger.debug("[GuardShadow] intraday DB 저장 실패 (무해): %s", _igs_e)

        return {
            "ok":             True,
            "cv_acc":         round(cv_acc, 4) if cv_acc is not None else None,
            "old_acc":        round(old_acc, 4),
            "replaced":       replaced,
            "guard_rejected": guard_rejected,
            "n_samples":      len(X),
        }

    # ── 모델 저장/로드 ────────────────────────────────────────────
    def _read_model_meta(self, horizon_key: str):
        """[MW0602 457차] `gbm_{h}_meta.json` 사이드카를 읽는다. 없으면 None.

        457차 이전에 저장된 모델에는 이 파일이 없다 — 그 경우 "모른다"이지
        "괜찮다"가 아니므로, 호출부는 None을 **무효**로 처리해야 한다.
        """
        try:
            import json as _json
            p = os.path.join(self.model_dir, "gbm_%s_meta.json" % horizon_key)
            if not os.path.exists(p):
                return None
            with open(p, "r", encoding="utf-8") as f:
                return _json.load(f)
        except Exception:
            return None

    def _fair_validity(self, horizon_key: str, holdout_bars: int):
        """공정 홀드아웃 비교가 유효한가 — (bool, 사유).

        유효 조건: **현행 모델이 홀드아웃 구간을 학습하지 않았을 것.**
        현행의 `train_end_ts`가 홀드아웃 시작 시각보다 앞서야 한다.

        무효여도 측정 자체는 계속한다(값은 그대로 기록) — 무효 표본을 지우면
        "얼마나 자주 무효인가"를 알 수 없게 된다. 판정에서만 걸러낸다.
        """
        meta = self._read_model_meta(horizon_key)
        if not meta:
            return False, "현행 메타 없음(457차 이전 모델) — 오염 여부 불명"
        _end = meta.get("train_end_ts")
        _src = meta.get("source", "unknown")
        if not _end:
            return False, "현행 train_end_ts 없음 — 오염 여부 불명"
        tsl = getattr(self, "_last_train_ts", None)
        if not tsl or len(tsl) <= holdout_bars:
            return False, "홀드아웃 경계 ts 불명(학습 ts 목록 없음/부족)"
        _ho_start = tsl[-holdout_bars]
        if str(_end) >= str(_ho_start):
            return False, ("현행이 홀드아웃 학습함 — train_end=%s >= holdout_start=%s (source=%s)"
                           % (str(_end)[:16], str(_ho_start)[:16], _src))
        return True, ("유효 — 현행 train_end=%s < holdout_start=%s (source=%s)"
                      % (str(_end)[:16], str(_ho_start)[:16], _src))

    def _measure_fair_holdout(
        self, horizon_key, X, y, X_full, h_idx, feature_names,
        make_model, make_sample_weight,
    ):
        """[MW0601 405차 / P1-1] 공정 홀드아웃 섀도 — **판정 무영향, 로그·DB 전용**.

        `_measure_incumbent_acc`(403차 P0-4)는 현행 모델을 신규와 "같은 검증 폴드"로
        재채점하지만, 그 폴드는 현행 모델이 이미 학습한 구간과 겹쳐 현행에 유리하다
        (그 함수 docstring이 스스로 명시한 한계). 404차는 그 값을 DB에 영속화했을
        뿐 비교 자체는 그대로였고, 결과는 12거래일 연속 교체 0건이었다.

        여기서는 최신 `holdout_bars`행을 **학습에서 완전히 제외**한 도전자를 따로
        학습해, 도전자·현행 둘 다 그 구간으로 채점한다. 도전자에게는 완전 OOS다.

        ⚠ **여전히 완전히 공정하지는 않다.** 현행 pkl은 intraday 재학습이 매일
        덮어쓰므로(403차 교차검증 #6, mtime 실측) 홀드아웃 구간을 이미 학습했을 수
        있다. 즉 측정된 격차는 실제의 **하한**이며, 판단 재료로 pkl mtime을 함께
        돌려준다. 이 한계를 없애려면 현행 모델의 학습 컷오프를 메타데이터로 남기는
        별건 작업이 필요하다.

        데이터는 시간순 정렬이 보장된다(TimeSeriesSplit·`X[-N:]`=최신 관례가 이미
        그 전제 위에 있다). 타임스탬프가 이 경로까지 전달되지 않으므로 홀드아웃은
        **행 위치 기준**으로 자른다.

        Returns: (new_acc, old_acc, n_holdout, note) — 측정 불가 시 (None, None, 0, 사유)
        """
        cfg = EOD_GUARD_FAIR_HOLDOUT or {}
        if not cfg.get("enabled", False):
            return None, None, 0, "비활성"
        H = int(cfg.get("holdout_bars", 1850))
        min_hold = int(cfg.get("min_holdout_bars", 300))
        min_train = int(cfg.get("min_train_bars_after_holdout", 10000))
        n = len(X)
        if H < min_hold:
            return None, None, 0, "홀드아웃 설정 과소 (%d < %d)" % (H, min_hold)
        # [MW0601 454차 / ATB-A1c] 홀드아웃 경계 퍼징 — 도전자 학습을 홀드아웃
        # 직전 h_min행 앞에서 끊는다. 그 h_min행의 라벨은 홀드아웃 구간의 미래를
        # 보고 만들어졌으므로, 포함하면 도전자가 채점 구간의 정답 일부를 학습한다.
        # 홀드아웃 자체([-H:])와 현행 모델 채점은 무변경 — 계측 정의만 정직해진다.
        _purge = max(0, int(HORIZONS.get(horizon_key, 0)))
        cut = H + _purge
        if n - cut < min_train:
            return None, None, 0, ("홀드아웃 후 학습표본 부족 (%d-%d=%d < %d)"
                                   % (n, cut, n - cut, min_train))
        try:
            import pickle as _pk
            src = X_full if X_full is not None else X
            tr_src, ho_src = src[:-cut], src[-H:]
            y_tr, y_ho = y[:-cut], y[-H:]

            # 도전자 — 홀드아웃을 뺀 구간으로만 스케일러·모델을 새로 학습
            sc = StandardScaler()
            tr_scaled = sc.fit_transform(tr_src)
            ho_scaled = sc.transform(ho_src)
            if h_idx is not None:
                tr_scaled = tr_scaled[:, h_idx]
                ho_scaled = ho_scaled[:, h_idx]
            ch = make_model()
            ch.fit(tr_scaled, y_tr, sample_weight=make_sample_weight(y_tr, horizon_key))
            new_acc = float((ch.predict(ho_scaled) == y_ho).mean())

            # 현행 프로덕션 모델 — 자기 스케일러로 같은 홀드아웃 채점
            mp = os.path.join(self.model_dir, "gbm_%s.pkl" % horizon_key)
            sp = os.path.join(self.scaler_dir, "scaler_%s.pkl" % horizon_key)
            fp = os.path.join(self.model_dir, "feature_names_%s.pkl" % horizon_key)
            if not (os.path.exists(mp) and os.path.exists(sp)):
                return new_acc, None, H, "구모델/스케일러 pkl 없음"
            with open(mp, "rb") as f:
                old_model = _pk.load(f)
            with open(sp, "rb") as f:
                old_scaler = _pk.load(f)
            if os.path.exists(fp):
                with open(fp, "rb") as f:
                    saved = list(_pk.load(f))
                if list(feature_names) != saved:
                    return new_acc, None, H, ("피처셋 변경 %d→%d개"
                                              % (len(saved), len(feature_names)))
            ho_old = old_scaler.transform(ho_src)
            if h_idx is not None:
                ho_old = ho_old[:, h_idx]
            nf = getattr(old_model, "n_features_in_", None)
            if nf is not None and ho_old.shape[1] != nf:
                return new_acc, None, H, ("피처 수 불일치 %d vs %d"
                                          % (ho_old.shape[1], nf))
            old_acc = float((old_model.predict(ho_old) == y_ho).mean())
            mt = datetime.datetime.fromtimestamp(
                os.path.getmtime(mp)).strftime("%Y-%m-%d %H:%M")
            # [MW0602 457차] 비교 유효성 판정 — docstring이 지목한 "별건 작업"의 구현.
            # 도전자는 홀드아웃을 확실히 못 봤지만 현행은 봤을 수 있고, 그러면 이
            # 격차는 성능차가 아니라 **in-sample 프리미엄**이다. 457차 이전 실측이
            # 정확히 그 상태였다: 36행 중 35행(97%)에서 도전자 열위, 평균 -0.1161,
            # 그리고 fair_note의 구모델 mtime이 전부 **당일 장중 재학습**(예: 08-10
            # 14:16)이라 홀드아웃 1850봉을 통째로 학습한 모델과 비교하고 있었다.
            # 이제 사이드카 메타의 train_end_ts로 오염 여부를 직접 판정한다.
            _valid, _vnote = self._fair_validity(horizon_key, H)
            return new_acc, old_acc, H, "%s (구모델 pkl mtime=%s) | %s" % (
                "ok" if _valid else "무효", mt, _vnote)
        except Exception as e:
            return None, None, 0, "측정 실패: %s" % e

    def _save_model(self, horizon_key: str, model, scaler, acc: float, feature_names: List[str]):
        path       = os.path.join(self.model_dir, f"gbm_{horizon_key}.pkl")
        acc_path   = os.path.join(self.model_dir, f"gbm_{horizon_key}_acc.txt")
        scaler_dir = self.scaler_dir
        scaler_path = os.path.join(scaler_dir, f"scaler_{horizon_key}.pkl")
        os.makedirs(scaler_dir, exist_ok=True)
        # [S2-D] 원자 쓰기: .tmp 에 먼저 쓴 뒤 os.replace() 로 교체
        # — 직접 open(path,"wb") 은 쓰는 중 main 스레드가 joblib.load() 하면 불완전 파일 읽기 발생
        _tmp_model  = path       + ".tmp"
        _tmp_scaler = scaler_path + ".tmp"
        with open(_tmp_model, "wb") as f:
            pickle.dump(model, f, protocol=4)   # py37_32 호환 상한
        os.replace(_tmp_model, path)
        with open(_tmp_scaler, "wb") as f:
            pickle.dump(scaler, f, protocol=4)  # py37_32 호환 상한
        os.replace(_tmp_scaler, scaler_path)
        # intraday 재학습(CV 없음)은 acc=nan — 파일을 덮어쓰면 다음 재학습의
        # old_acc 로그가 무의미해지므로(연쇄 nan), 유효한 값일 때만 갱신하고
        # 그 외에는 EOD 전체 재학습(CV 있음)의 마지막 실측값을 그대로 보존한다.
        if not np.isnan(acc):
            with open(acc_path, "w") as f:
                f.write(str(acc))

        # ── [MW0602 457차] 사이드카 메타 — pkl과 acc.txt의 정합성을 사후에 알 수 있게 ──
        #
        # **왜 필요한가**: 위 `if not np.isnan(acc)` 가드는 의도된 동작이지만, 그
        # 결과로 **acc.txt가 이미 존재하지 않는 모델을 기술하는 상태**가 생긴다.
        #   · intraday 재학습은 acc=nan → pkl만 갈리고 acc.txt는 그대로
        #   · EOD 가드가 HOLD를 내면 `_save_model` 자체가 호출되지 않아 acc.txt 동결
        # 두 경로가 겹치면 acc.txt가 영구 고착된다. 2026-08-10 실측:
        # `gbm_3m_acc.txt` mtime **2026-08-01**(9거래일 정체, 값 0.4756 고정)인데
        # `gbm_3m.pkl` mtime은 **2026-08-10 14:16**(그날 5번째 무검증 장중 재학습본).
        # 즉 EOD 가드가 "구모델 유지"라고 판정한 그 구모델은 실재하지 않는다.
        #
        # **여기서 판정을 바꾸지 않는다.** acc.txt 의미론·가드 로직 전부 무변경이다.
        # 404차 `guard_shadow` 채널이 이미 판정 기준 교체 여부를 사전등록해 두었고
        # (missed_upgrade_rate ≥ 0.30 → 주간회의), 실측은 3/42=0.071로 **PASS**다.
        # 이 메타는 그 판정을 대체하는 게 아니라, GuardFair가 "현행이 홀드아웃을 이미
        # 학습했는가"를 **알 수 있게** 하는 입력이다(405차 docstring이 지목한 별건 작업).
        #
        # 실패해도 학습을 깨지 않는다 — 메타는 진단용이고 없으면 없는 대로 동작한다.
        try:
            import json as _json
            _meta = {
                "horizon":        horizon_key,
                "written_at":     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                # 이 pkl을 쓴 경로. "eod"만 CV 검증을 거쳤다.
                "source":         getattr(self, "_save_source", "unknown"),
                # 학습창 양 끝 — GuardFair가 홀드아웃 겹침을 판정하는 근거.
                "train_start_ts": getattr(self, "_last_train_start_ts", None),
                "train_end_ts":   getattr(self, "_last_train_end_ts", None),
                "n_features":     len(feature_names) if feature_names else None,
                # acc.txt에 실제로 쓰인 값과 그 출처. nan이면 미갱신(직전 값 보존).
                "acc":            (None if np.isnan(acc) else float(acc)),
                "acc_kind":       ("cv" if not np.isnan(acc) else "none(intraday)"),
                # [MW0602 468차 G-1] 이 pkl을 만든 **레이블 규칙**.
                # 런타임이 "지금 적재된 모델이 현행 레이블 규칙 학습본인가"를 직접
                # 묻는 근거다(main.py `_model_label_scheme_current`). 값이 없으면
                # (구버전 사이드카) 런타임은 **모른다 → 보수적으로 제한 유지**로 간다.
                "label_scheme":   getattr(self, "_last_label_scheme", None),
                "label_param":    (getattr(self, "_last_label_params", {}) or {}).get(
                    horizon_key),
            }
            _mp = os.path.join(self.model_dir, f"gbm_{horizon_key}_meta.json")
            _tmp_meta = _mp + ".tmp"
            with open(_tmp_meta, "w", encoding="utf-8") as f:
                _json.dump(_meta, f, ensure_ascii=False)
            os.replace(_tmp_meta, _mp)
        except Exception as _me:
            logger.debug("[Retrain] %s 메타 저장 실패 (무해): %s", horizon_key, _me)
        # Phase C 원자성 보장: 모델 저장 직후 feature_names_{h}.pkl도 함께 저장.
        # 외부 호출자(_train_horizon 이후)의 _save_feature_names와 중복이지만 무해.
        # subprocess 타임아웃 강제 종료 시 모델은 저장되지만 외부 _save_feature_names는
        # 미실행될 수 있어 pkl 불일치가 발생했으므로 여기서 선점 저장한다.
        _n_model = getattr(model, "n_features_in_", None)
        if feature_names and _n_model is not None and len(feature_names) == _n_model:
            h_fn_path = os.path.join(self.model_dir, f"feature_names_{horizon_key}.pkl")
            # Phase C 피처셋 변경 감지 로그 — _registry_ok=False 등으로 전체 피처가
            # 투입됐을 때 기존 슬라이싱 pkl을 조용히 덮어쓰는 상황을 운영 중 탐지.
            if os.path.exists(h_fn_path):
                try:
                    with open(h_fn_path, "rb") as _rf:
                        _prev = pickle.load(_rf)
                    _prev_n = len(_prev)
                    _new_n  = len(feature_names)
                    if _prev_n != _new_n:
                        _direction = "비활성화" if _new_n > _prev_n else "재슬라이싱"
                        logger.warning(
                            "[Retrain] %s feature_names_%s.pkl %d개→%d개 변경 — "
                            "Phase C 슬라이싱 %s "
                            "(horizon_feature_sets.json 미반영 또는 _registry_ok=False 의심)",
                            horizon_key, horizon_key, _prev_n, _new_n, _direction,
                        )
                except Exception:
                    pass
            _tmp_fn = h_fn_path + ".tmp"
            with open(_tmp_fn, "wb") as f:
                pickle.dump(list(feature_names), f, protocol=4)
            os.replace(_tmp_fn, h_fn_path)

    def _save_rejected_model(
        self, horizon_key: str, model, scaler, new_acc: float, old_acc: float,
        feature_names: List[str],
    ) -> None:
        """[346차] EOD 모델가드가 교체를 보류한 신규 모델을 참고용으로 보관한다.

        프로덕션 gbm_{horizon}.pkl은 건드리지 않는다(구모델 그대로 유지) — 이건
        "이번에 뭘 새로 학습했었는지" 사후 분석용 별도 사본이다. 타임스탬프를
        파일명에 넣어 여러 번의 보류 이력을 모두 남긴다(관찰 목적 — 지금 극단
        변동성 구간에서 실제로 몇 번 발동하는지 보는 게 이 가드를 넣은 이유 중 하나).
        """
        try:
            rejected_dir = os.path.join(self.model_dir, "rejected")
            os.makedirs(rejected_dir, exist_ok=True)
            _ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            _base = f"gbm_{horizon_key}_{_ts}"
            with open(os.path.join(rejected_dir, f"{_base}.pkl"), "wb") as f:
                pickle.dump(model, f, protocol=4)
            with open(os.path.join(rejected_dir, f"{_base}_scaler.pkl"), "wb") as f:
                pickle.dump(scaler, f, protocol=4)
            with open(os.path.join(rejected_dir, f"{_base}_features.pkl"), "wb") as f:
                pickle.dump(list(feature_names), f, protocol=4)
            import json
            _tol = EOD_MODEL_GUARD_DROP_TOLERANCE.get(
                horizon_key, EOD_MODEL_GUARD_DROP_TOLERANCE_DEFAULT
            )
            with open(os.path.join(rejected_dir, f"{_base}.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "horizon": horizon_key,
                    "ts": _ts,
                    "new_acc": round(new_acc, 4) if new_acc is not None else None,
                    "old_acc": round(old_acc, 4),
                    "drop": round(old_acc - new_acc, 4) if new_acc is not None else None,
                    "tolerance": _tol,
                }, f, ensure_ascii=False, indent=2)
            logger.info("[Retrain] %s 보류 모델 참고용 저장: %s/", horizon_key, rejected_dir)
        except Exception as _se:
            logger.warning("[Retrain] %s 보류 모델 저장 실패 (무해 — 구모델은 정상 유지): %s",
                            horizon_key, _se)

    def _save_rejected_rf_model(
        self, horizon_key: str, model, new_oob: float, old_oob: float,
    ) -> None:
        """[346차] RF 버전 _save_rejected_model() — rf_horizons.pkl은 6개 호라이즌이
        한 파일에 묶여 있어 개별 호라이즌만 따로 pkl로 뽑아 참고용 보관한다."""
        try:
            rejected_dir = os.path.join(self.model_dir, "rejected")
            os.makedirs(rejected_dir, exist_ok=True)
            _ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            _base = f"rf_{horizon_key}_{_ts}"
            with open(os.path.join(rejected_dir, f"{_base}.pkl"), "wb") as f:
                pickle.dump(model, f, protocol=2)  # RF는 protocol=2 (py37_32 호환, save_all과 동일)
            import json
            _tol = EOD_MODEL_GUARD_DROP_TOLERANCE.get(
                horizon_key, EOD_MODEL_GUARD_DROP_TOLERANCE_DEFAULT
            )
            with open(os.path.join(rejected_dir, f"{_base}.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "horizon": horizon_key,
                    "ts": _ts,
                    "new_oob": round(new_oob, 4) if new_oob is not None else None,
                    "old_oob": round(old_oob, 4),
                    "drop": round(old_oob - new_oob, 4) if new_oob is not None else None,
                    "tolerance": _tol,
                }, f, ensure_ascii=False, indent=2)
            logger.info("[Retrain] RF %s 보류 모델 참고용 저장: %s/", horizon_key, rejected_dir)
        except Exception as _se:
            logger.warning("[Retrain] RF %s 보류 모델 저장 실패 (무해 — 구모델은 정상 유지): %s",
                            horizon_key, _se)

    def _save_feature_names(self, feature_names: List[str], horizon_key: str = None) -> None:
        """feature_names 저장.

        horizon_key 지정 시: feature_names_{horizon_key}.pkl (호라이즌 전용)
        항상: feature_names.pkl (공유, backward compat)
        """
        if horizon_key:
            h_path = os.path.join(self.model_dir, "feature_names_{}.pkl".format(horizon_key))
            with open(h_path, "wb") as f:
                pickle.dump(list(feature_names), f, protocol=4)   # py37_32 호환 상한
        else:
            # 공유 pkl: 전체 피처셋 저장 (구버전 모델과의 호환성)
            feature_path = os.path.join(self.model_dir, "feature_names.pkl")
            with open(feature_path, "wb") as f:
                pickle.dump(list(feature_names), f, protocol=4)   # py37_32 호환 상한

    def _load_feature_names(self, horizon_key: str = None):
        # type: (str) -> list
        """저장된 feature_names 로드.

        horizon_key 지정 시 전용 pkl → 없으면 공유 pkl → 없으면 빈 리스트.
        """
        if horizon_key:
            h_path = os.path.join(self.model_dir, "feature_names_{}.pkl".format(horizon_key))
            if os.path.exists(h_path):
                try:
                    with open(h_path, "rb") as f:
                        return pickle.load(f)
                except (IOError, OSError, pickle.UnpicklingError):
                    pass
        # fallback: 공유 pkl
        feature_path = os.path.join(self.model_dir, "feature_names.pkl")
        try:
            with open(feature_path, "rb") as f:
                return pickle.load(f)
        except (IOError, OSError, pickle.UnpicklingError):
            return []

    def _measure_incumbent_acc(
        self, horizon_key, X, y, X_full, h_idx, feature_names, val_idx_all,
    ):
        """[403차 종합 P0-4] 현행 프로덕션 모델을 신규와 동일한 검증 폴드로 재채점.

        acc.txt(과거 날짜·과거 분포)가 아니라 "오늘 데이터에서 지금 모델이 실제로
        몇 %인가"를 측정한다. 읽기 전용이며 어떤 파일도 쓰지 않는다.

        피처셋이 바뀌었으면(오늘 슬라이싱 결과 != 저장된 feature_names_{h}.pkl)
        비교 자체가 무의미하므로 측정하지 않고 사유를 돌려준다.

        ⚠ 한계 — 완전히 공정한 비교는 아니다. 이 검증 폴드는 현행 모델이 어제
        학습할 때 이미 본 구간을 상당 부분 포함하므로 현행 모델에 유리하다
        (즉 여기서 측정된 왜곡은 실제 왜곡의 하한이다). 진짜 공정한 비교는 두
        모델 모두 학습에 쓰지 않은 최근 홀드아웃 구간이 필요하며, 그건 학습
        파이프라인 구조 변경이라 별건으로 남긴다.

        Returns: (acc: float | None, note: str)
        """
        if not val_idx_all:
            return None, "검증 폴드 없음"
        try:
            import pickle as _pk
            _mp = os.path.join(self.model_dir, "gbm_%s.pkl" % horizon_key)
            _sp = os.path.join(self.scaler_dir, "scaler_%s.pkl" % horizon_key)
            _fp = os.path.join(self.model_dir, "feature_names_%s.pkl" % horizon_key)
            if not (os.path.exists(_mp) and os.path.exists(_sp)):
                return None, "구모델/스케일러 pkl 없음"
            with open(_mp, "rb") as f:
                _model = _pk.load(f)
            with open(_sp, "rb") as f:
                _scaler = _pk.load(f)
            if os.path.exists(_fp):
                with open(_fp, "rb") as f:
                    _saved_names = list(_pk.load(f))
                if list(feature_names) != _saved_names:
                    return None, ("피처셋 변경 %d→%d개"
                                  % (len(_saved_names), len(feature_names)))
            _idx = np.array(sorted(set(int(i) for i in val_idx_all)))
            _src = X_full if X_full is not None else X
            _Xv = _scaler.transform(_src[_idx])
            if h_idx is not None:
                _Xv = _Xv[:, h_idx]
            _nfeat = getattr(_model, "n_features_in_", None)
            if _nfeat is not None and _Xv.shape[1] != _nfeat:
                return None, "피처 수 불일치 %d vs %d" % (_Xv.shape[1], _nfeat)
            return float(accuracy_score(y[_idx], _model.predict(_Xv))), "ok"
        except Exception as e:
            return None, "측정 예외: %s" % e

    def _load_model_acc(self, horizon_key: str) -> float:
        acc_path = os.path.join(self.model_dir, f"gbm_{horizon_key}_acc.txt")
        try:
            with open(acc_path, "r") as f:
                return float(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0.0

    def load_model(self, horizon_key: str):
        """저장된 GBM 모델 로드"""
        path = os.path.join(self.model_dir, f"gbm_{horizon_key}.pkl")
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return pickle.load(f)

    # ── 스케일러 워밍업용 피처 로드 ──────────────────────────────────

    def load_features_for_warmup(
        self, lookback_bars: int = 500
    ):
        """raw_data.db 에서 최근 N봉 피처만 로드 (라벨 계산 없음).

        refit_scalers_only() 에 전달할 X 행렬과 feature_names 반환.
        데이터 부족 또는 오류 시 (None, None) 반환.
        """
        import json as _json
        import sqlite3

        from config.settings import RAW_DATA_DB

        raw_db = RAW_DATA_DB
        if not os.path.exists(raw_db):
            logger.warning("[ScalerWarmup] raw_data.db 없음 — 워밍업 건너뜀")
            return None, None

        try:
            with sqlite3.connect(raw_db, timeout=10) as conn:
                conn.row_factory = sqlite3.Row
                feat_rows = conn.execute(
                    "SELECT features FROM raw_features ORDER BY ts DESC LIMIT ?",
                    (lookback_bars,),
                ).fetchall()
        except Exception as _e:
            logger.warning("[ScalerWarmup] DB 읽기 실패: %s", _e)
            return None, None

        if not feat_rows:
            logger.warning("[ScalerWarmup] raw_features 비어있음 — 워밍업 건너뜀")
            return None, None

        # feature_names.pkl(모델 기준 97개)을 우선 사용.
        # DB 봉에는 need_add 피처가 섞여 키 수가 더 많을 수 있는데,
        # 최대 키 봉 기준으로 X를 만들면 refit_scalers_only() 재정렬이 필요하고
        # 피처 수 불일치 로그가 발생함. pkl 기준으로 직접 구성해 불일치를 제거한다.
        model_feat_names = self._load_feature_names() or None  # [] → None 처리

        records = []
        db_feat_names = None   # model pkl 없을 때 fallback
        db_feat_count = 0
        for r in feat_rows:
            try:
                fd = _json.loads(r["features"])
            except (ValueError, TypeError):
                continue
            if not isinstance(fd, dict):
                continue
            if model_feat_names is None:
                curr_keys = list(fd.keys())
                if db_feat_names is None or len(curr_keys) > db_feat_count:
                    db_feat_count = len(curr_keys)
                    db_feat_names = curr_keys
            records.append(fd)

        if not records:
            return None, None

        feat_names = model_feat_names or db_feat_names
        if feat_names is None:
            return None, None

        X = np.array(
            [[rec.get(f, 0.0) for f in feat_names] for rec in records],
            dtype=np.float32,
        )
        _src = "" if model_feat_names else " (db_fallback)"
        logger.info("[ScalerWarmup] 피처 로드 완료 n=%d feat=%d%s", len(X), len(feat_names), _src)
        return X, feat_names

    # ── Phase 2: 호라이즌별 독립 재학습 ─────────────────────────
    def _has_horizon_features_table(self):
        # type: () -> bool
        """raw_features_horizon 테이블 존재 여부 확인."""
        import sqlite3
        from config.settings import RAW_DATA_DB
        if not os.path.exists(RAW_DATA_DB):
            return False
        try:
            with sqlite3.connect(RAW_DATA_DB, timeout=5) as conn:
                row = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='raw_features_horizon'"
                ).fetchone()
                if row is None:
                    return False
                cnt = conn.execute(
                    "SELECT COUNT(*) FROM raw_features_horizon"
                ).fetchone()
                return (cnt[0] if cnt else 0) > 0
        except Exception:
            return False

    def _retrain_phase2(self, weeks_back, force, start_time, full_cv=False):
        # type: (int, bool, object, bool) -> dict
        """Phase 2 경로: raw_features_horizon 테이블에서 호라이즌별 독립 X 로드 후 재학습."""
        import json as _json2
        import sqlite3

        from config.settings import RAW_DATA_DB, HORIZON_THRESHOLDS
        from model.multi_horizon_model import apply_robust_preprocess

        raw_db = RAW_DATA_DB
        cutoff = (
            datetime.datetime.now() - datetime.timedelta(weeks=weeks_back)
        ).strftime("%Y-%m-%d %H:%M:%S")

        results = {}
        # Phase 2에서는 feature_names.pkl을 덮어쓰지 않음.
        # 1m 모델(Phase 1 경로)은 기존 105+ 피처 기반이므로 전역 feature_names 보존.
        # 각 호라이즌 모델의 피처명은 _train_horizon 내부에서 해당 pkl에 저장됨.
        _existing_feat_names = self._load_feature_names()  # 기존 전역 피처명 백업

        for hz, h_min in HORIZONS.items():
            min_bars = MIN_TRAIN_BARS_PER_HORIZON.get(hz, MIN_TRAIN_BARS)
            try:
                with sqlite3.connect(raw_db, timeout=10) as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute(
                        "SELECT ts, features FROM raw_features_horizon "
                        "WHERE horizon=? AND ts>=? ORDER BY ts",
                        (hz, cutoff),
                    ).fetchall()
                    candle_rows = conn.execute(
                        "SELECT ts, close FROM raw_candles WHERE ts>=? ORDER BY ts",
                        (cutoff,),
                    ).fetchall()
            except Exception as _e:
                logger.warning("[Retrain-P2] %s DB 조회 실패: %s", hz, _e)
                results[hz] = {"replaced": False, "error": str(_e)}
                continue

            if len(rows) < min_bars:
                logger.warning(
                    "[Retrain-P2] %s 데이터 부족 %d < %d -- 건너뜀",
                    hz, len(rows), min_bars,
                )
                results[hz] = {"replaced": False, "error": "데이터 부족"}
                continue

            close_map = {r["ts"]: float(r["close"]) for r in candle_rows}

            # X 행렬 구성
            # [260704 감사 P3] 기존엔 "가장 키가 많은 1개 행"을 canonical feat_names로
            # 썼는데, 옵션체인 피처(opt_gex_bn 등)는 5분마다만 갱신돼 그 행이 항상
            # 최다-키 행이 된다는 보장이 없다 — 결과적으로 다른 행에만 있는 피처가
            # use_feat_names에서 누락돼 전 구간에서 조용히 0.0으로 깔림(30m 퇴역 심사
            # 중 opt_gex_bn이 raw_features_horizon엔 있는데 학습 피처엔 없는 원인으로 확인).
            # 전 구간 키의 합집합(첫 등장 순서 보존)으로 교체 — 있는 피처를 못 쓰는
            # 손실만 없앨 뿐 기존 피처 값·순서는 그대로.
            feat_names = None
            records = []
            for r in rows:
                try:
                    fd = _json2.loads(r["features"])
                except (ValueError, TypeError):
                    continue
                if not isinstance(fd, dict):
                    continue
                if feat_names is None:
                    feat_names = dict.fromkeys(fd.keys())
                else:
                    for k in fd.keys():
                        if k not in feat_names:
                            feat_names[k] = None
                records.append((r["ts"], fd))
            feat_names = list(feat_names) if feat_names is not None else None

            if not records or feat_names is None:
                results[hz] = {"replaced": False, "error": "피처 파싱 실패"}
                continue

            # P1: CUSUM 이벤트 필터
            cusum_idx = _cusum_filter(records, close_map)
            if len(cusum_idx) < len(records):
                records = [records[i] for i in cusum_idx]

            # Phase 2-D: 호라이즌별 학습 윈도우 상한 적용 (최신 N봉 우선)
            _tw = TRAINING_WINDOW_BARS.get(hz)
            if isinstance(_tw, int) and _tw > 0 and len(records) > _tw:
                _min_b = MIN_TRAIN_BARS_PER_HORIZON.get(hz, MIN_TRAIN_BARS)
                if _tw >= _min_b:
                    logger.info(
                        "[Retrain-P2] %s TRAINING_WINDOW=%d 적용 (%d→%d봉 최신 우선)",
                        hz, _tw, len(records), _tw,
                    )
                    records = records[-_tw:]
                else:
                    logger.debug(
                        "[Retrain-P2] %s TRAINING_WINDOW=%d < MIN_BARS=%d — 전체 사용 (%d봉)",
                        hz, _tw, _min_b, len(records),
                    )

            # global feature_names(1m 기준)로 X 구성 → 추론 공간과 일치.
            # raw_features_horizon의 cvd_direction/atr 등은 build_for_horizon에서
            # N분봉 완성봉 기반으로 재계산되어 저장되므로 (127차~) 자동 반영됨.
            use_feat_names = _existing_feat_names if _existing_feat_names else feat_names
            X_hz = np.array(
                [[rec[1].get(f, 0.0) for f in use_feat_names] for rec in records],
                dtype=np.float32,
            )
            # N분봉 재계산 피처 채움 검증: cvd_direction 비제로 비율 로깅
            _cvd_idx = (use_feat_names.index("cvd_direction")
                        if "cvd_direction" in use_feat_names else None)
            if _cvd_idx is not None:
                _nonzero = int(np.count_nonzero(X_hz[:, _cvd_idx]))
                logger.info(
                    "[Retrain-P2] %s cvd_direction 비제로 %d/%d (%.1f%%)",
                    hz, _nonzero, len(records),
                    100.0 * _nonzero / max(len(records), 1),
                )
            X_hz = apply_robust_preprocess(X_hz, use_feat_names)

            # y 레이블 (Phase 2는 고정 임계값 사용)
            _fixed_thresh = HORIZON_THRESHOLDS.get(hz, 0.0003)
            # [MW0602 468차 G-1] 이 경로가 **실제로 쓴** 레이블 규칙을 남긴다.
            # Phase 2는 설정과 무관하게 항상 고정 임계값이다 — `USE_FIXED_LABEL_THRESHOLD`를
            # 읽지 않고 이 사실을 그대로 적는다. 여기를 빼먹으면 EOD 주경로(Phase 2)로
            # 저장된 사이드카가 `label_scheme=None`이 되고, 런타임은 "모른다"로 읽어
            # 사이즈 제한을 영영 안 푼다(보수 폴백이라 안전하되 G-1이 무력화된다).
            self._last_label_scheme = "fixed"
            if not isinstance(getattr(self, "_last_label_params", None), dict):
                self._last_label_params = {}
            self._last_label_params[hz] = float(_fixed_thresh)
            _plr = PATH_LABEL_RATIO_BY_HZ.get(hz, PATH_LABEL_RATIO)
            y_hz = []
            for ts, _ in records:
                label = _path_conditioned_label(close_map, ts, h_min, _fixed_thresh, path_ratio=_plr)
                y_hz.append(label)
            y_hz = np.array(y_hz, dtype=int)

            # Phase C: horizon_feature_sets.json 기반 호라이즌별 피처 슬라이싱
            # Phase 1 경로와 동일한 방식 — 스케일러는 97개 전체(X_hz)로 fit,
            # GBM은 스케일 후 호라이즌 전용 컬럼만 추출해 학습.
            _h_names_p2 = None
            _h_idx_p2 = None
            try:
                from features.horizon_feature_registry import get_available_feature_set as _get_avail_p2
                _h_names_p2 = _get_avail_p2(hz, use_feat_names)
            except ImportError:
                pass

            if _h_names_p2 and len(_h_names_p2) < len(use_feat_names):
                _h_idx_p2 = [use_feat_names.index(n) for n in _h_names_p2]
                X_h_p2 = X_hz[:, _h_idx_p2]
                logger.info(
                    "[Retrain-P2] %s 피처 슬라이싱: %d → %d개 (horizon_feature_sets.json)",
                    hz, len(use_feat_names), len(_h_names_p2),
                )
            else:
                _h_names_p2 = use_feat_names
                _h_idx_p2 = None
                X_h_p2 = X_hz

            result = self._train_horizon(
                hz, X_h_p2, y_hz,
                feature_names=_h_names_p2,
                force=force, full_cv=full_cv,
                X_full=X_hz if _h_idx_p2 is not None else None,
                h_idx=_h_idx_p2,
            )
            results[hz] = result

            # 호라이즌 전용 피처명 pkl 저장 (Phase C) — 모델이 실제 교체된 경우에만 저장
            # 미교체 시 저장하면 구 모델(97피처)과 feature_names_hz(12피처) 불일치 발생
            if result.get("replaced"):
                self._save_feature_names(_h_names_p2, horizon_key=hz)

        # 전역 feature_names.pkl 복원 (Phase 2는 1m 기존 피처명 보존)
        if _existing_feat_names:
            self._save_feature_names(_existing_feat_names)
            logger.info("[Retrain-P2] feature_names.pkl 보존 (n=%d, 1m 기준)", len(_existing_feat_names))

        # RF 재학습 (Phase 2에서는 생략 — 1m X 없음)

        elapsed = (datetime.datetime.now() - start_time).total_seconds()
        self._last_retrain  = datetime.datetime.now()
        self._retrain_count += 1
        return {
            "ok":           True,
            "phase2":       True,
            "retrain_count": self._retrain_count,
            "elapsed_sec":  round(elapsed, 1),
            "horizons":     results,
            "timestamp":    self._last_retrain.strftime("%Y-%m-%d %H:%M"),
        }

    # ── [260704 감사 P1] Triple-barrier 섀도우 병행 학습 ─────────────
    def retrain_shadow_triple_barrier(
        self,
        weeks_back: int = RETRAIN_WEEKS_BACK,
        stop_mult: Optional[float] = None,
        tp_mult_by_horizon: Optional[Dict[str, float]] = None,
    ) -> Dict:
        """
        Triple-barrier 레이블로 호라이즌별 섀도우 모델을 학습해
        `{model_dir}/shadow_triple_barrier/`에 저장한다.

        레이블 = 진입(롱 가정) 후 {TP 배리어(ATR×tp_mult) / SL 배리어(ATR×stop_mult) /
        시간 배리어(호라이즌 분)} 중 무엇이 먼저 닿는가 — 실제 청산 배수와 동일하게
        맞춰 "모델 예측 = 시스템 실행"이 되도록 한다 (감사 §1-3 ①).

        기존 3클래스(path-conditioned) 프로덕션 모델은 전혀 건드리지 않는다.
        실거래 의사결정에 사용하지 말 것 — 2~4주 병행 후 예측-손익 상관으로
        승격 여부를 별도 판정한다(ROADMAP.md Phase 5 이후 항목).

        Returns:
            {"ok": bool, "horizons": {hz: {"cv_acc", "champion_cv_acc", "n_samples", "label_dist"}}}
        """
        import sqlite3
        import json as _json3
        from config.settings import RAW_DATA_DB, ATR_STOP_MULT, ATR_HORIZON_TP1_MULT, ATR_TP1_MULT
        from model.target_builder import build_triple_barrier_label
        from model.multi_horizon_model import apply_robust_preprocess

        if not _SKLEARN_OK:
            return {"ok": False, "error": "scikit-learn 미설치"}
        if not self._has_horizon_features_table():
            return {"ok": False, "error": "raw_features_horizon 테이블 없음 — Phase2 데이터 필요"}

        stop_mult = float(stop_mult) if stop_mult is not None else float(ATR_STOP_MULT)
        tp_mult_by_horizon = tp_mult_by_horizon or ATR_HORIZON_TP1_MULT

        shadow_dir = os.path.join(self.model_dir, SHADOW_TB_DIRNAME)
        os.makedirs(shadow_dir, exist_ok=True)

        raw_db = RAW_DATA_DB
        cutoff = (
            datetime.datetime.now() - datetime.timedelta(weeks=weeks_back)
        ).strftime("%Y-%m-%d %H:%M:%S")
        _make_model = _shadow_model_factory()

        # [384차] 383차가 규명한 구조결함(평가창이 매주 재학습으로 리셋돼 5m~30m이
        # min_samples_hz 영구 미달) 해법: 검증캠페인 리포트(generate_validation_
        # campaign_report.py, campaign_steps.py 순서상 이 재학습보다 먼저 실행됨)가
        # 오늘 새로 판정한 호라이즌만 tb_verdict_log에 기록한다 — 그 목록에 없는
        # 호라이즌(아직 OOS n이 min_samples_hz 미달)은 기존 모델 파일을 그대로 두어
        # mtime을 보존하고, 다음 주에도 진짜 OOS가 계속 누적되게 한다. 최초 부트스트랩
        # (모델 파일 자체가 없는 호라이즌)은 이 게이트와 무관하게 항상 학습한다.
        try:
            from utils.db_utils import fetch_tb_verdicts_judged_on
            _today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            _judged_today = set(fetch_tb_verdicts_judged_on(_today_str))
        except Exception as _e:
            logger.warning(
                "[ShadowTB] tb_verdict_log 조회 실패(%s) — 이번 회차는 안전하게 "
                "전 호라이즌 재학습 보류(기존 모델 유지)", _e)
            _judged_today = set()

        results = {}
        for hz, h_min in HORIZONS.items():
            _existing_model_p = os.path.join(shadow_dir, "gbm_%s_shadow_tb.pkl" % hz)
            if os.path.exists(_existing_model_p) and hz not in _judged_today:
                logger.info(
                    "[ShadowTB] %s 재학습 보류(스킵) — 오늘(%s) 판정 미도달, "
                    "기존 모델 유지(OOS 누적 보존)", hz, _today_str)
                results[hz] = {
                    "ok": True, "skipped": True,
                    "reason": "판정 미도달 — 기존 모델 유지(OOS 누적 보존)",
                }
                continue

            min_bars = MIN_TRAIN_BARS_PER_HORIZON.get(hz, MIN_TRAIN_BARS)
            try:
                with sqlite3.connect(raw_db, timeout=10) as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute(
                        "SELECT ts, features FROM raw_features_horizon "
                        "WHERE horizon=? AND ts>=? ORDER BY ts",
                        (hz, cutoff),
                    ).fetchall()
                    _fallback_used = False
                    if len(rows) < min_bars:
                        # 1m은 설계상 raw_features_horizon에 기록되지 않음
                        # (TRAINING_WINDOW_BARS 주석: "1m: Phase 2 미사용 (raw_features 경로)").
                        # 감사 보고서가 "유일한 실측 엣지"로 지목한 호라이즌이므로 raw_features
                        # (전역 피처 스냅샷, Phase 0/1 경로)로 폴백해 섀도우 검증에서 빠지지 않게 한다.
                        rows = conn.execute(
                            "SELECT ts, features FROM raw_features WHERE ts>=? ORDER BY ts",
                            (cutoff,),
                        ).fetchall()
                        _fallback_used = True
                    candle_rows = conn.execute(
                        "SELECT ts, high, low, close FROM raw_candles WHERE ts>=? ORDER BY ts",
                        (cutoff,),
                    ).fetchall()
            except Exception as _e:
                logger.warning("[ShadowTB] %s DB 조회 실패: %s", hz, _e)
                results[hz] = {"ok": False, "error": str(_e)}
                continue

            if len(rows) < min_bars:
                logger.info("[ShadowTB] %s 데이터 부족 %d < %d — 건너뜀", hz, len(rows), min_bars)
                results[hz] = {"ok": False, "error": "데이터 부족 (%d < %d)" % (len(rows), min_bars)}
                continue
            if _fallback_used:
                logger.info("[ShadowTB] %s raw_features_horizon 데이터 없음 — raw_features 폴백 사용", hz)

            close_map = {r["ts"]: float(r["close"]) for r in candle_rows}
            high_map  = {r["ts"]: float(r["high"])  for r in candle_rows}
            low_map   = {r["ts"]: float(r["low"])   for r in candle_rows}

            records = []
            feat_names = None
            feat_name_count = 0
            for r in rows:
                try:
                    fd = _json3.loads(r["features"])
                except (ValueError, TypeError):
                    continue
                if not isinstance(fd, dict):
                    continue
                curr_keys = list(fd.keys())
                if feat_names is None or len(curr_keys) >= feat_name_count:
                    feat_name_count = len(curr_keys)
                    feat_names = curr_keys
                records.append((r["ts"], fd))

            if not records or feat_names is None:
                results[hz] = {"ok": False, "error": "피처 파싱 실패"}
                continue

            tp_mult = float(tp_mult_by_horizon.get(hz, ATR_TP1_MULT))
            y_hz = []
            for ts, fd in records:
                atr = float(fd.get("atr", 0.0) or 0.0)
                label = build_triple_barrier_label(
                    ts, h_min, close_map, high_map, low_map,
                    atr=atr, stop_mult=stop_mult, tp_mult=tp_mult,
                )
                y_hz.append(label)
            y_hz = np.array(y_hz, dtype=int)

            if len(np.unique(y_hz)) < 2:
                results[hz] = {"ok": False, "error": "레이블 단일 클래스 — 학습 불가"}
                continue

            X_hz = np.array(
                [[rec[1].get(f, 0.0) for f in feat_names] for rec in records],
                dtype=np.float32,
            )
            X_hz = apply_robust_preprocess(X_hz, feat_names)

            # 프로덕션과 동일하게 3폴드 시계열 CV
            tscv = TimeSeriesSplit(n_splits=3)
            cv_accs = []
            for train_idx, val_idx in tscv.split(X_hz):
                # [MW0601 454차 / ATB-A1b] 경계 퍼징 — _run_cv_folds와 동일 사유.
                # 라벨 정의·최종 모델 학습은 무변경(CV 계측만 정직해진다) —
                # [1] TB 채널의 OOS 평가(모델 mtime 기준)와 무관.
                if 0 < h_min < len(train_idx):
                    train_idx = train_idx[:-h_min]
                _leak = _leak_overlap_count(train_idx, val_idx, h_min)
                if _leak:
                    logger.warning(
                        "[LeakGuard] ShadowTB %s fold 퍼징 실패 — %d건 겹침", hz, _leak,
                    )
                X_tr, X_val = X_hz[train_idx], X_hz[val_idx]
                y_tr, y_val = y_hz[train_idx], y_hz[val_idx]
                if len(np.unique(y_tr)) < 2:
                    continue
                scaler = StandardScaler()
                X_tr_s = scaler.fit_transform(X_tr)
                X_val_s = scaler.transform(X_val)
                model = _make_model()
                model.fit(X_tr_s, y_tr, sample_weight=_make_sample_weight(y_tr, hz))
                cv_accs.append(accuracy_score(y_val, model.predict(X_val_s)))

            cv_acc = float(np.mean(cv_accs)) if cv_accs else None

            # 전체 데이터로 최종 섀도우 모델 학습 + 저장 (프로덕션 모델과 완전 분리된 경로)
            final_scaler = StandardScaler()
            X_scaled = final_scaler.fit_transform(X_hz)
            final_model = _make_model()
            final_model.fit(X_scaled, y_hz, sample_weight=_make_sample_weight(y_hz, hz))

            _model_path = os.path.join(shadow_dir, f"gbm_{hz}_shadow_tb.pkl")
            _tmp_model = _model_path + ".tmp"
            with open(_tmp_model, "wb") as f:
                pickle.dump(final_model, f, protocol=4)
            os.replace(_tmp_model, _model_path)

            _scaler_path = os.path.join(shadow_dir, f"scaler_{hz}_shadow_tb.pkl")
            _tmp_scaler = _scaler_path + ".tmp"
            with open(_tmp_scaler, "wb") as f:
                pickle.dump(final_scaler, f, protocol=4)
            os.replace(_tmp_scaler, _scaler_path)

            _fn_path = os.path.join(shadow_dir, f"feature_names_{hz}_shadow_tb.pkl")
            with open(_fn_path, "wb") as f:
                pickle.dump(list(feat_names), f, protocol=4)

            label_dist = {int(c): int((y_hz == c).sum()) for c in np.unique(y_hz)}
            champion_acc = self._load_model_acc(hz)
            logger.info(
                "[ShadowTB] %s cv_acc=%s n=%d 레이블분포=%s (champion cv_acc=%.4f)",
                hz, ("%.4f" % cv_acc) if cv_acc is not None else "N/A",
                len(X_hz), label_dist, champion_acc,
            )
            results[hz] = {
                "ok": True,
                "cv_acc": round(cv_acc, 4) if cv_acc is not None else None,
                "champion_cv_acc": champion_acc,
                "n_samples": len(X_hz),
                "label_dist": label_dist,
                "source": "raw_features(fallback)" if _fallback_used else "raw_features_horizon",
            }

        return {"ok": True, "horizons": results, "shadow_dir": shadow_dir}

    # ── DB 로드 (raw_features + raw_candles 기반) ────────────────
    def _load_from_db(self, weeks_back: int, intraday: bool = False):
        """
        raw_data.db 의 raw_features / raw_candles 테이블에서 학습 데이터 로드.

        raw_features: ts, features(JSON)
        raw_candles:  ts, close
        라벨: 각 호라이즌 N분 후 수익률 방향 (+1/0/-1)
        """
        import json as _json
        import sqlite3

        from config.settings import RAW_DATA_DB, HORIZON_THRESHOLDS
        from model.target_builder import build_single_target

        raw_db = RAW_DATA_DB
        if not os.path.exists(raw_db):
            logger.warning("[Retrain] raw_data.db 없음 — 학습 데이터 축적 대기")
            return None, None, None

        try:
            cutoff = (
                datetime.datetime.now() - datetime.timedelta(weeks=weeks_back)
            ).strftime("%Y-%m-%d %H:%M:%S")

            with sqlite3.connect(raw_db, timeout=10) as conn:
                conn.row_factory = sqlite3.Row

                feat_rows = conn.execute(
                    "SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts",
                    (cutoff,),
                ).fetchall()

                candle_rows = conn.execute(
                    "SELECT ts, close FROM raw_candles WHERE ts >= ? ORDER BY ts",
                    (cutoff,),
                ).fetchall()

            # close 맵 (ts → close)
            close_map = {r["ts"]: float(r["close"]) for r in candle_rows}

            # X 행렬 구성
            # [318차] 기존엔 "가장 키가 많은 1개 행"을 canonical feat_names로 썼는데,
            # 5분마다만 갱신되는 옵션체인 피처처럼 항상 최다-키 행이 된다는 보장이 없는
            # 피처가 있으면 다른 행에만 있는 피처가 조용히 누락됨(260704 감사 P3가
            # Phase2/raw_features_horizon 경로에서 이미 확인한 것과 같은 클래스의 버그 —
            # 여기 Phase1/global 경로는 그때 함께 고쳐지지 않고 남아있었음, hurst_ready
            # 학습 피처 미편입의 원인 중 하나). 전 구간 키의 합집합(첫 등장 순서 보존)으로 교체.
            records = []
            feat_names = None
            for r in feat_rows:
                try:
                    fd = _json.loads(r["features"])
                except (ValueError, TypeError):
                    continue
                if not isinstance(fd, dict):
                    continue
                if feat_names is None:
                    feat_names = dict.fromkeys(fd.keys())
                else:
                    for k in fd.keys():
                        if k not in feat_names:
                            feat_names[k] = None
                records.append((r["ts"], fd))
            feat_names = list(feat_names) if feat_names is not None else None

            if not records or feat_names is None:
                return None, None, None

            registry_path = os.path.join(DB_DIR, "shap_feature_registry.json")
            try:
                import json as _json2
                if os.path.exists(registry_path):
                    with open(registry_path, "r", encoding="utf-8") as fh:
                        registry = _json2.load(fh)
                    active_features = list(registry.get("active_features") or [])
                    if active_features:
                        available = set(feat_names)
                        managed = [name for name in active_features if name in available]
                        if managed:
                            feat_names = managed
                            logger.info(
                                "[Retrain] managed feature set 적용: %d개",
                                len(feat_names),
                            )
            except Exception as exc:
                logger.warning("[Retrain] managed feature set load 실패: %s", exc)

            # ── 미래 가격 없는 행 제거 (BUG-B 수정) ──────────────────────────
            # 오늘 세션 끝 근처 행은 max_horizon(30m) 후 가격이 close_map에 없음
            # → _path_conditioned_label이 FLAT 반환 → validation fold acc 하락
            # → EOD Retrain에서 acc가 89%로 폭등하는 역현상 방지
            # 해결: 30m 미래 가격이 close_map에 없는 행을 학습 전 제거
            _max_h_min = max(HORIZONS.values())  # 30
            _n_before = len(records)
            records = [
                (ts, feat) for ts, feat in records
                if (
                    datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    + datetime.timedelta(minutes=_max_h_min)
                ).strftime("%Y-%m-%d %H:%M:%S") in close_map
            ]
            _n_dropped = _n_before - len(records)
            if _n_dropped > 0:
                logger.info(
                    "[Retrain] 미래 가격 불완전 행 %d개 제거 (max_horizon=%dm 후 종가 없음)",
                    _n_dropped, _max_h_min,
                )

            # P2: MIN_TRAIN_BARS 체크를 미래가격 제거 후 실제 행 수 기준으로 수행
            if len(records) < MIN_TRAIN_BARS:
                logger.warning(
                    "[Retrain] 학습 데이터 부족 (미래가격 제거 후 %d < %d)",
                    len(records), MIN_TRAIN_BARS,
                )
                return None, None, None

            # MAX_TRAIN_BARS 상한: weeks_back 오설정·이상 입력으로 행 수 폭증 방지
            # 슬라이딩 창(26주) 정상 운영 시 ~40,000행 → 50,000 초과 불가
            # 초과 시 최신 N행 사용 (시계열 특성상 최신 우선)
            if len(records) > MAX_TRAIN_BARS:
                logger.warning(
                    "[Retrain] MAX_TRAIN_BARS 상한 적용: %d → %d행",
                    len(records), MAX_TRAIN_BARS,
                )
                records = records[-MAX_TRAIN_BARS:]

            # P1: CUSUM 이벤트 필터 — 연속 구간 반복학습 차단
            cusum_idx = _cusum_filter(records, close_map)
            if len(cusum_idx) < len(records):
                records = [records[i] for i in cusum_idx]

            # 장중 경량 모드: np.array 변환 전 최신 N행으로 제한 (32-bit OOM 방지)
            # retrain_now()의 사후 슬라이싱은 np.array 생성 이후라 이미 늦음 —
            # 변환 전에 잘라야 39,880행→20,000행으로 메모리 절반 감소
            if intraday and len(records) > MAX_TRAIN_BARS_INTRADAY:
                logger.info(
                    "[Retrain] 장중 경량 모드(DB): %d → %d행 사전 제한 (OOM 방지)",
                    len(records), MAX_TRAIN_BARS_INTRADAY,
                )
                records = records[-MAX_TRAIN_BARS_INTRADAY:]

            X = np.array(
                [[rec[1].get(f, 0.0) for f in feat_names] for rec in records],
                dtype=np.float32,
            )

            # y 라벨 (호라이즌별 미래 수익률 방향)
            # 방법B: 각 봉의 시점별 rolling sigma × k 로 threshold 계산
            # → 날별 변동성 차이를 레이블에 반영 (FLAT std 14%p → 3%p)
            from collections import deque as _deque
            import math as _math
            from config.settings import (
                SIGMA_K as _SK, SIGMA_W as _SW, SIGMA_W_MIN as _SW_MIN,
                USE_ROLLING_SIGMA_THRESHOLD as _USE_ROLLING,
                SIGMA_K_PER_HORIZON as _SK_PER_H,
                USE_FIXED_LABEL_THRESHOLD as _USE_FIXED_LABEL,
            )

            # 개선 4: 학습 레이블 고정화
            # USE_FIXED_LABEL_THRESHOLD=True → HORIZON_THRESHOLDS 고정값으로 레이블 생성
            # 실전 rolling sigma와 학습 임계값을 분리 → 레이블 드리프트 제거
            _use_fixed = _USE_FIXED_LABEL
            if _use_fixed:
                logger.info("[Retrain] 레이블 고정 임계값 사용 (USE_FIXED_LABEL_THRESHOLD=True)")

            y_dict = {}
            for hz, h_min in HORIZONS.items():
                y = []
                _sigma_buf_rt = _deque(maxlen=_SW)
                # P5: 호라이즌별 최적 k (없으면 공통 k fallback)
                _hz_k = _SK_PER_H.get(hz, _SK)
                # 고정 임계값 (개선 4)
                _fixed_thresh = HORIZON_THRESHOLDS.get(hz, 0.0003)

                for ts, _ in records:
                    if _use_fixed:
                        # 개선 4: 고정 임계값 — rolling sigma 계산 생략
                        threshold = _fixed_thresh
                    elif _USE_ROLLING:
                        # 기존 rolling sigma 방식
                        _c0 = close_map.get(ts)
                        _t_prev = (
                            datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                            - datetime.timedelta(minutes=1)
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        _c_prev = close_map.get(_t_prev)
                        if _c0 and _c_prev and _c_prev > 0:
                            _sigma_buf_rt.append((_c0 - _c_prev) / _c_prev * 100)

                        _n = len(_sigma_buf_rt)
                        if _n >= _SW_MIN and _n > 1:
                            _v = list(_sigma_buf_rt)
                            _m = sum(_v) / _n
                            _sig = _math.sqrt(sum((x - _m) ** 2 for x in _v) / (_n - 1))
                            threshold = _sig / 100.0 * _hz_k * _math.sqrt(h_min)
                        else:
                            threshold = _fixed_thresh
                    else:
                        threshold = _fixed_thresh

                    # P6b: 경로 조건부 레이블
                    # 중간 역행 과다 케이스를 FLAT으로 처리 → 레이블 순도 향상
                    label = _path_conditioned_label(
                        close_map, ts, h_min, threshold,
                        path_ratio=PATH_LABEL_RATIO_BY_HZ.get(hz, PATH_LABEL_RATIO),
                    )
                    y.append(label)
                y_dict[hz] = np.array(y, dtype=int)

            # [MW0602 468차 G-1] **이 학습에 실제로 쓴 레이블 규칙**을 인스턴스에 남긴다.
            # `_save_model`이 사이드카에 새겨, 런타임이 "지금 적재된 pkl이 현행 레이블
            # 규칙으로 학습된 것인가"라는 **상태**를 직접 물을 수 있게 한다
            # (종전 `_pre_retrain_done`은 "재학습 콜백이 돌았나"라는 **이벤트**였다).
            # ⚠ 설정값이 아니라 **이 루프에서 실제로 쓴 값**을 남긴다 — 설정을 바꾼 뒤
            #   재학습 전이라면 둘이 다르고, 그 차이를 감지하는 것이 이 필드의 목적이다.
            try:
                self._last_label_scheme = "fixed" if _use_fixed else (
                    "rolling_sigma" if _USE_ROLLING else "atr")
                self._last_label_params = {}
                for hz in HORIZONS:
                    if _use_fixed:
                        self._last_label_params[hz] = float(
                            HORIZON_THRESHOLDS.get(hz, 0.0003))
                    elif _USE_ROLLING:
                        self._last_label_params[hz] = float(_SK_PER_H.get(hz, _SK))
                    else:
                        self._last_label_params[hz] = None
            except Exception:
                self._last_label_scheme = None
                self._last_label_params = {}

            # [MW0602 457차] 학습창 끝 시각을 인스턴스에 남긴다 — `_save_model`이
            # 사이드카 메타에 새겨 "이 pkl이 어디까지 봤는가"를 사후에 알 수 있게 한다.
            # 반환 시그니처를 바꾸지 않는 이유: `_load_from_db` 호출부가 여럿이고
            # 전부 3-튜플 언팩이라 확장하면 조용히 깨진다.
            # `_last_train_ts`는 X와 **행 위치가 1:1로 맞는다** — 위 필터(미래가격
            # 제거·MAX_TRAIN_BARS·CUSUM·장중 제한)가 전부 `records` 단계에서 끝난 뒤
            # 바로 그 `records`로 X를 만들기 때문이다. 소비처는 반드시 `len()` 대조로
            # 정렬을 확인할 것(X를 직접 넘겨받는 retrain_now 호출 경로에서는 어긋난다).
            try:
                self._last_train_ts = [str(r[0]) for r in records]
                self._last_train_end_ts = self._last_train_ts[-1]
                self._last_train_start_ts = self._last_train_ts[0]
            except Exception:
                self._last_train_ts = None
                self._last_train_end_ts = self._last_train_start_ts = None
            logger.info(
                f"[Retrain] DB 로드 완료: {len(X)}행 × {len(feat_names)}피처 "
                f"(cutoff={cutoff[:10]} ~ {(self._last_train_end_ts or '?')[:16]})"
            )
            return X, y_dict, feat_names

        except Exception as e:
            logger.warning(f"[Retrain] DB 로드 오류: {e}")
            return None, None, None

    def prune_raw_data_db(self, keep_weeks: int = RAW_DATA_PRUNE_WEEKS) -> int:
        """raw_data.db 오래된 데이터 정리 — 매주 월요일 EOD 1회 호출 권장.

        keep_weeks 이전 데이터를 raw_features / raw_candles / raw_features_horizon 에서 삭제.
        RETRAIN_WEEKS_BACK(26주)의 2배(52주)를 기본 보존 기간으로 유지.
        삭제된 총 행 수를 반환.
        """
        import sqlite3
        from config.settings import RAW_DATA_DB

        if not os.path.exists(RAW_DATA_DB):
            return 0

        cutoff = (
            datetime.datetime.now() - datetime.timedelta(weeks=keep_weeks)
        ).strftime("%Y-%m-%d %H:%M:%S")

        deleted = 0
        try:
            with sqlite3.connect(RAW_DATA_DB, timeout=15) as conn:
                for table in ("raw_features", "raw_candles", "raw_features_horizon"):
                    try:
                        r = conn.execute(
                            "DELETE FROM {} WHERE ts < ?".format(table), (cutoff,)
                        )
                        deleted += r.rowcount
                    except Exception:
                        pass  # 테이블 없으면 무시
                conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
            logger.info(
                "[Retrain] DB pruning 완료: %d행 삭제 (cutoff=%s, keep=%d주)",
                deleted, cutoff[:10], keep_weeks,
            )
        except Exception as e:
            logger.warning("[Retrain] DB pruning 실패: %s", e)
        return deleted

    def get_stats(self) -> dict:
        return {
            "retrain_count": self._retrain_count,
            "last_retrain":  self._last_retrain.strftime("%Y-%m-%d %H:%M") if self._last_retrain else "없음",
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if _SKLEARN_OK:
        retrainer = BatchRetrainer()
        # 더미 데이터로 테스트
        np.random.seed(42)
        X_dummy = np.random.randn(6000, 20).astype(np.float32)
        y_dummy = {hz: np.random.randint(0, 2, 6000) for hz in ["1m", "5m", "15m"]}
        result  = retrainer.retrain_now(
            X=X_dummy,
            y_dict=y_dummy,
            feature_names=[f"feature_{i}" for i in range(X_dummy.shape[1])],
            force=True,
        )
        print(f"재학습 결과: {result}")
    else:
        print("scikit-learn 미설치")
