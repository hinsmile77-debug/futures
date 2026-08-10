# scripts/check_scaler_feature_drift.py — 스케일러 ↔ 최근 실측 분포 괴리 진단 (456차, 읽기 전용)
"""저장된 호라이즌 스케일러의 center/scale이 최근 실측 분포와 얼마나 벌어졌는지 진단한다.

## 왜 필요한가

2026-08-10 점검에서 `opt_pcr_extreme`(10m 실사용)·`opt_pcr_slope_norm`(15m·30m 실사용)
등이 `[ScalerMonitor] max_z=+4.66`으로 하루 종일 찍히고 `[AutoMasked]` 격리가 86회
발생했다. 원인 가설은 **450차(2026-08-09)가 PCR 가드 스케일 드리프트를 고쳐 이 피처들이
"전 구간 0"에서 되살아났는데, 스케일러는 아직 죽어 있던 시기 분포로 적합돼 있다**는 것.

`[AutoMasked]`는 CORE가 아닌 이상값 피처를 예측에서 격리하므로, 오탐이면 멀쩡한
피처가 매분 버려진다. 반대로 진짜 드리프트면 그 피처의 z가 폭발해 모델 입력이 오염된다.
**어느 쪽인지는 스케일러 파라미터와 실측 분포를 직접 대조해야만 알 수 있다.**

## 무엇을 하지 않는가

읽기 전용이다. 스케일러를 재적합하지도, 저장하지도 않는다. 조치 판단은 사람이 한다
([[feedback_instrument_before_wiring]] — 계측 먼저, 그다음 배선).

## 실행

    python scripts/check_scaler_feature_drift.py                  # 최근 1거래일
    python scripts/check_scaler_feature_drift.py --days 5         # 최근 5거래일
    python scripts/check_scaler_feature_drift.py --feature opt_pcr_extreme
    python scripts/check_scaler_feature_drift.py --horizon 30m --top 20

py37_32 / py310_64 어느 쪽에서도 동작한다(스케일러 pkl은 protocol=4).
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sqlite3
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

HORIZONS = ["1m", "3m", "5m", "10m", "15m", "30m"]
SCALER_DIR = os.path.join(PROJECT_ROOT, "model", "scaler")
HORIZON_DIR = os.path.join(PROJECT_ROOT, "model", "horizons")
RAW_DB = os.path.join(PROJECT_ROOT, "data", "db", "raw_data.db")

# ── Robust 전처리 미러 ────────────────────────────────────────────────────
# 스케일러는 `apply_robust_preprocess()` **이후** 값으로 적합된다. raw_features JSON의
# 원본값을 그대로 스케일러 파라미터와 대조하면 log1p 피처에서 허위 경보가 난다
# (첫 실행에서 avg_volume이 z=+736으로 찍혔다 — 원본 294 vs log 공간 mean 5.56 비교).
# config에서 직접 읽어 정의가 갈라지지 않게 한다.
from config.settings import SCALER_CLIP_FEATURES, SCALER_LOG1P_FEATURES  # noqa: E402

# 갭 오프셋(_PRICE_LEVEL_FEATURES: microprice/vwap)은 당일 시가에 의존하는 런타임
# 상태라 오프라인 재현이 불가하다 — 해당 피처는 진단에서 제외한다.
_GAP_OFFSET_FEATURES = ("microprice", "vwap")

# AutoMask 임계 — model/multi_horizon_model.py 의 이상값 판정과 같은 값.
# 여기서 하드코딩하는 이유: 이 스크립트는 진단 전용이라 런타임 설정 로딩(무거운 import
# 체인 + COM 의존)을 피한다. 값이 바뀌면 이 상수도 함께 고칠 것.
AUTOMASK_Z = 4.0
WATCH_Z = 2.5


def _load_scaler(hz):
    p = os.path.join(SCALER_DIR, "scaler_%s.pkl" % hz)
    if not os.path.exists(p):
        return None
    with open(p, "rb") as f:
        return pickle.load(f)


def _load_feature_names():
    """공유 피처셋(스케일러 컬럼 순서)과 호라이즌별 실사용 피처셋을 함께 읽는다."""
    import joblib

    shared = joblib.load(os.path.join(HORIZON_DIR, "feature_names.pkl"))
    per_hz = {}
    for hz in HORIZONS:
        p = os.path.join(HORIZON_DIR, "feature_names_%s.pkl" % hz)
        per_hz[hz] = list(joblib.load(p)) if os.path.exists(p) else list(shared)
    return list(shared), per_hz


def _load_recent_features(days):
    """raw_features(JSON blob)에서 최근 N거래일 피처를 dict 리스트로 읽는다."""
    con = sqlite3.connect("file:%s?mode=ro" % RAW_DB.replace("\\", "/"), uri=True)
    cur = con.cursor()
    cur.execute(
        "SELECT DISTINCT DATE(ts) d FROM raw_features ORDER BY d DESC LIMIT ?", (days,)
    )
    dates = [r[0] for r in cur.fetchall()]
    if not dates:
        return [], []
    qs = ",".join("?" * len(dates))
    cur.execute(
        "SELECT features FROM raw_features WHERE DATE(ts) IN (%s) ORDER BY ts" % qs,
        dates,
    )
    rows = []
    for (blob,) in cur.fetchall():
        try:
            rows.append(json.loads(blob))
        except Exception:
            continue
    con.close()
    return rows, sorted(dates)


def _preprocess(name, v):
    """`apply_robust_preprocess()`와 동일한 변환을 스칼라 1개에 적용."""
    import math

    if name in SCALER_LOG1P_FEATURES:
        return math.log1p(max(v, 0.0))
    rng = SCALER_CLIP_FEATURES.get(name)
    if rng is not None:
        lo, hi = rng
        return min(max(v, lo), hi)
    return v


def _stats(vals):
    n = len(vals)
    if n == 0:
        return None
    m = sum(vals) / n
    var = sum((v - m) ** 2 for v in vals) / n if n > 1 else 0.0
    return m, var ** 0.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=1, help="최근 N거래일 (기본 1)")
    ap.add_argument("--horizon", default="", help="특정 호라이즌만 (기본 전체)")
    ap.add_argument("--feature", default="", help="특정 피처만 (부분일치)")
    ap.add_argument("--top", type=int, default=12, help="호라이즌별 상위 N개 (기본 12)")
    ap.add_argument("--active-only", action="store_true",
                    help="해당 호라이즌 실사용 피처만 (기본: 전체 스캔)")
    args = ap.parse_args()

    shared, per_hz = _load_feature_names()
    rows, dates = _load_recent_features(args.days)
    if not rows:
        print("raw_features 데이터 없음 — 중단")
        return 1

    print("# 스케일러 드리프트 진단 — 관찰창 %s (%d봉)" % (", ".join(dates), len(rows)))
    print("# AutoMask 임계 |z|>=%.1f · 관찰 임계 |z|>=%.1f" % (AUTOMASK_Z, WATCH_Z))
    print()

    # 6개 호라이즌 스케일러는 같은 X·같은 피처셋으로 적합되므로 파라미터가 동일하다
    # (실측 확인). 같은 표를 6번 찍으면 진짜 차이가 있을 때 눈에 안 띄므로, 동일하면
    # 한 번만 출력하고 "실사용" 열에 호라이즌 목록을 적는다.
    loaded = {}
    for hz in (HORIZONS if not args.horizon else [args.horizon]):
        sc = _load_scaler(hz)
        if sc is not None and hasattr(sc, "mean_"):
            loaded[hz] = sc
    if not loaded:
        print("스케일러 없음/미적합 — 중단")
        return 1

    def _key(sc):
        return (tuple(round(float(x), 9) for x in sc.mean_),
                tuple(round(float(x), 9) for x in sc.scale_))

    groups = {}
    for hz, sc in loaded.items():
        groups.setdefault(_key(sc), []).append(hz)
    if len(groups) == 1:
        print("> 6개 호라이즌 스케일러 파라미터 동일 — 통합 1개 표로 출력한다.")
        print()

    any_alarm = False
    for gi, (_gk, hz_list) in enumerate(groups.items()):
        sc = loaded[hz_list[0]]
        title = ", ".join(hz_list)
        recs = []
        for i, name in enumerate(shared):
            if i >= len(sc.mean_):
                break
            if args.feature and args.feature not in name:
                continue
            if name in _GAP_OFFSET_FEATURES:
                continue   # 갭 오프셋은 오프라인 재현 불가 (상단 주석)
            users = [h for h in hz_list if name in (per_hz.get(h) or [])]
            if args.active_only and not users:
                continue
            vals = [_preprocess(name, float(r[name])) for r in rows
                    if isinstance(r.get(name), (int, float))]
            st = _stats(vals)
            if st is None:
                continue
            live_mean, live_std = st
            s_mean = float(sc.mean_[i])
            s_scale = float(sc.scale_[i]) if float(sc.scale_[i]) else 1e-9
            # 실측 평균이 스케일러 기준으로 몇 시그마에 놓이는가 = 중심 이동
            z_center = (live_mean - s_mean) / s_scale
            # 실측 표준편차 / 스케일러 표준편차 = 폭 비율
            ratio = live_std / s_scale if s_scale else float("inf")
            # 실측 표본 중 |z|>=AUTOMASK_Z 인 비율 = 실제 격리 유발률
            hit = sum(1 for v in vals if abs((v - s_mean) / s_scale) >= AUTOMASK_Z)
            recs.append((abs(z_center), name, z_center, ratio, hit, len(vals), users))
        recs.sort(reverse=True)
        shown = [r for r in recs if r[0] >= WATCH_Z or r[4] > 0][: args.top]
        print("## 스케일러 그룹 %d — %s" % (gi + 1, title))
        if not shown:
            print("|z|>=%.1f 또는 격리유발 피처 없음 ✅" % WATCH_Z)
            print()
            continue
        any_alarm = True
        print()
        print("| 피처 | 실사용 호라이즌 | 중심이동 z | 폭비율(실측σ/스케일러σ) | 격리유발 |")
        print("|---|---|---|---|---|")
        for _, name, zc, ratio, hit, n, users in shown:
            flag = "🔴" if abs(zc) >= AUTOMASK_Z else "🟡"
            print("| `%s` | %s | %s %+.2f | %.2f× | %d/%d (%.0f%%) |" % (
                name, ",".join(users) if users else "—", flag, zc, ratio, hit, n,
                100.0 * hit / n if n else 0.0))
        print()

    print("---")
    if any_alarm:
        print("🔴 = AutoMask 임계 초과(격리 발생 중) · 🟡 = 관찰 구간")
        print()
        print("**읽는 법**: `중심이동 z`가 크면 스케일러의 학습 분포와 지금 시장이 다르다는 뜻이다.")
        print("`실사용 호라이즌`이 붙은 피처만 모델 입력에 실제로 들어간다 — `—`는 스캔 대상일")
        print("뿐이라 z가 커도 예측에 영향이 없다(ZeroDiag `(candidate)` 태그와 같은 구분).")
        print("단 `—`도 `last_extreme_features`에는 올라가므로 AutoMask 상위 5칸을 잠식할 수 있다.")
        print()
        print("**조치 판단**: 실사용 피처가 🔴이면 EOD P8(`retrain_eod.py`, 최근 500봉 재적합)이")
        print("다음 거래일에 해소하는지 먼저 확인할 것. 이틀 이상 남으면 그때 강제 재적합을")
        print("검토한다 — 500봉은 약 1.3거래일이라 하루면 대부분 흡수된다.")
    else:
        print("✅ 이상 없음.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
