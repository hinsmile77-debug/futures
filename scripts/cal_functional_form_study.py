# scripts/cal_functional_form_study.py — 보정기 함수형·오염 영향 오프라인 연구 [461차 P-D]
"""앙상블 보정기의 span 붕괴 원인을 **읽기 전용**으로 분해한다.

⚠ 이 스크립트는 라이브 경로에 아무 영향을 주지 않는다.
   - 저장본(`data/ensemble_calibrator.pkl`)을 **읽기만** 한다. 쓰지 않는다.
   - `predictions.db`도 SELECT만 한다.
   - 결과는 stdout + 선택적 JSON 리포트. 모델 교체·설정 변경을 하지 않는다.

실행 (py310_64 전용 — sklearn 1.0.2, 32-bit OOM 회피):
    C:/Users/pc1/anaconda3/envs/py310_64/python.exe scripts/cal_functional_form_study.py
    ... --json out.json      결과를 JSON으로도 저장
    ... --db-days 20         predictions.db에서 최근 N거래일 표본도 함께 분석

## 무엇을 답하려는 스크립트인가

430차는 "raw conf의 순위 AUC가 0.489라 정보가 없다 → 어떤 임계·함수형도 소용없다"고
확정했고, 그 결론이 `DEGENERATE_AUC_MIN`·보정 함수형에 대한 **금지선**이 됐다.
461차가 발견한 것은 그 진단이 내려진 표본의 21%가 WeightCollapse 인위값(raw=1.0,
무정보)이었다는 사실이다. 금지선을 깨자는 게 아니라, **금지선의 전제를 재측정**한다.

출력 4블록:
  [1] 표본 구성    — 오염행 비중, 기저율, raw 분포
  [2] 오염 영향    — 전체 vs clean 윈도의 AUC·span·out_max 대조
  [3] 정규화 스윕  — C 값별 계수/span/out_max (C=0.02가 span을 봉인하는지 확인)
  [4] 함수형 비교  — Platt / Isotonic / Beta-like(로짓 2모수) 의 도달가능성

## 읽을 때 주의 (313차)

- 윈도 200건은 **작다**. AUC 차이 0.01~0.03은 SE(≈0.041) 안이다 — 방향만 본다.
- `out_max >= min_conf`가 됐다고 "진입이 는다"가 아니다. [39]는 min_conf 게이트가
  품질 필터가 아니라 무작위 샘플러라고 판정했다. 도달가능성은 **필요조건**일 뿐이다.
- 여기서 좋아 보이는 함수형을 바로 배포하지 말 것. §9 사전등록 → 섀도 → 주간회의.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

import numpy as np

# 콘솔이 cp949면 em-dash(U+2014) 등에서 UnicodeEncodeError가 난다 — utf-8로 고정.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

try:
    import joblib
    from sklearn.linear_model import LogisticRegression
    from sklearn.isotonic import IsotonicRegression
    from sklearn.metrics import roc_auc_score
except ImportError as e:  # pragma: no cover - 환경 문제는 즉시 알린다
    print("[FATAL] sklearn/joblib 로드 실패: %s" % e)
    print("        py310_64 환경으로 실행할 것 "
          "(C:/Users/pc1/anaconda3/envs/py310_64/python.exe)")
    sys.exit(2)

_PROBE = np.linspace(0.0, 1.0, 11).reshape(-1, 1)
# 인위값 판정 문턱 — WeightCollapse 안전망은 정확히 1.0을 넣는다. 부동소수 여유만 둔다.
_ARTIFACT_MIN = 0.999


def _fit_diag(probs: np.ndarray, labels: np.ndarray, C: float) -> Optional[dict]:
    """Platt(C) 적합 후 진단값. 표본/라벨 부족이면 None."""
    if len(probs) < 30 or len(np.unique(labels)) < 2:
        return None
    lr = LogisticRegression(C=C, solver="lbfgs").fit(probs.reshape(-1, 1), labels)
    out = lr.predict_proba(_PROBE)[:, 1]
    return {
        "n":       int(len(probs)),
        "base":    float(labels.mean()),
        "coef":    float(lr.coef_[0][0]),
        "span":    float(out.max() - out.min()),
        "out_max": float(out.max()),
        "out_min": float(out.min()),
        "auc":     float(roc_auc_score(labels, probs)),
    }


def _load_pkl(path: str):
    if not os.path.exists(path):
        print("[SKIP] 저장본 없음: %s" % path)
        return None, None
    st = joblib.load(path)
    return np.array(st.get("probs", [])), np.array(st.get("labels", []))


def _load_db(days: int):
    """predictions.db에서 1m 앙상블 raw conf ↔ 적중 표본을 읽는다 (SELECT only)."""
    try:
        from config.settings import PREDICTIONS_DB
        from utils.db_utils import fetchall
    except Exception as e:
        print("[SKIP] DB 표본 로드 불가(설정 임포트 실패): %s" % e)
        return None, None
    try:
        rows = fetchall(
            PREDICTIONS_DB,
            """
            SELECT e.confidence_raw AS raw,
                   p.direction      AS pdir,
                   p.actual         AS actual,
                   e.weight_collapsed AS wc
              FROM ensemble_decisions e
              JOIN predictions p ON p.ts = e.ts AND p.horizon = '1m'
             WHERE p.actual IS NOT NULL
               AND e.confidence_raw IS NOT NULL
               AND date(e.ts) >= date('now', 'localtime', ?)
             ORDER BY e.ts
            """,
            ("-%d day" % int(days),),
        )
    except Exception as e:
        print("[SKIP] DB 조회 실패: %s" % e)
        return None, None
    if not rows:
        print("[SKIP] DB 표본 0건 (최근 %d일)" % days)
        return None, None
    raw = np.array([float(r["raw"]) for r in rows])
    ok = np.array([1 if int(r["pdir"]) == int(r["actual"]) else 0 for r in rows])
    wc = np.array([bool(r["wc"]) for r in rows])
    print("[DB] 최근 %d일 표본 %d건 (붕괴행 %d건 %.1f%%)"
          % (days, len(raw), int(wc.sum()), 100.0 * wc.mean()))
    # 저장본과 같은 규약으로 오염 판정: 붕괴 플래그 OR raw≈1.0
    return raw, ok, wc


def _report_block(title: str, probs: np.ndarray, labels: np.ndarray,
                  artifact: np.ndarray, out: dict) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)

    # [1] 표본 구성
    share = float(artifact.mean()) if len(artifact) else 0.0
    print("\n[1] 표본 구성")
    print("    n=%d  기저율(적중)=%.4f  오염행=%d건 (%.1f%%)"
          % (len(probs), labels.mean(), int(artifact.sum()), 100.0 * share))
    if artifact.sum():
        print("    오염행 적중률=%.4f  (기저율과의 차 %+.4f → 0 근방이면 무정보)"
              % (labels[artifact].mean(), labels[artifact].mean() - labels.mean()))
    qs = np.percentile(probs, [0, 25, 50, 75, 100])
    print("    raw 분위: min %.3f / p25 %.3f / med %.3f / p75 %.3f / max %.3f" % tuple(qs))
    out["sample"] = {
        "n": int(len(probs)), "base": float(labels.mean()),
        "artifact_n": int(artifact.sum()), "artifact_share": share,
    }

    # [2] 오염 영향
    clean = ~artifact
    print("\n[2] 오염 영향 — 전체 vs clean (동일 C=0.02)")
    d_all = _fit_diag(probs, labels, 0.02)
    d_cln = _fit_diag(probs[clean], labels[clean], 0.02)
    for tag, d in (("전체 ", d_all), ("clean", d_cln)):
        if d is None:
            print("    %s : 표본 부족" % tag)
            continue
        print("    %s : n=%3d base=%.4f AUC=%.4f coef=%+.4f span=%.5f out_max=%.4f"
              % (tag, d["n"], d["base"], d["auc"], d["coef"], d["span"], d["out_max"]))
    if d_all and d_cln:
        print("    → AUC 변화 %+.4f / span 변화 %+.5f / out_max 변화 %+.4f"
              % (d_cln["auc"] - d_all["auc"], d_cln["span"] - d_all["span"],
                 d_cln["out_max"] - d_all["out_max"]))
        print("    ⚠ AUC 차이는 n=%d에서 SE≈%.3f — 이보다 작으면 방향만 참고할 것."
              % (len(probs), 0.5 / np.sqrt(max(len(probs), 1)) * 1.15))
    out["contamination"] = {"all": d_all, "clean": d_cln}

    # [3] 정규화 스윕
    print("\n[3] 정규화(C) 스윕 — span 붕괴가 C 때문인지 확인")
    print("    %-6s | %-24s | %-24s" % ("C", "전체", "clean"))
    sweep = {}
    for C in (0.02, 0.05, 0.1, 0.5, 1.0, 10.0):
        a = _fit_diag(probs, labels, C)
        c = _fit_diag(probs[clean], labels[clean], C)
        f = lambda d: ("coef%+.3f span%.4f max%.3f" % (d["coef"], d["span"], d["out_max"])
                       if d else "표본부족")
        print("    %-6s | %-24s | %-24s" % (C, f(a), f(c)))
        sweep[str(C)] = {"all": a, "clean": c}
    out["c_sweep"] = sweep

    # [4] 함수형 비교 — 도달가능성 관점
    print("\n[4] 함수형 비교 — out_max 기준 도달가능성")
    try:
        from config.settings import ENS_CONF_FLOOR_FOR_AUTO as _static_floor
    except Exception:
        _static_floor = 0.33
    forms = {}
    # Platt C=0.02 (현행) / C=1.0 (약규제)
    for tag, C in (("platt C=0.02(현행)", 0.02), ("platt C=1.0", 1.0)):
        d = _fit_diag(probs[clean], labels[clean], C)
        if d:
            forms[tag] = d["out_max"]
    # Isotonic
    if clean.sum() >= 30 and len(np.unique(labels[clean])) >= 2:
        iso = IsotonicRegression(out_of_bounds="clip").fit(probs[clean], labels[clean])
        forms["isotonic"] = float(np.max(iso.predict(_PROBE.ravel())))
    print("    정적 하한 conf_floor=%.3f" % _static_floor)
    for tag, om in forms.items():
        print("    %-20s out_max=%.4f  정적하한 %s"
              % (tag, om, "도달O" if om >= _static_floor else "도달X"))
    print("    ⚠ 도달가능성은 필요조건일 뿐이다 — [39](min_conf=무작위 샘플러) 참조.")
    print("    ⚠ isotonic은 소표본에서 저단이 0.0으로 떨어지는 계단이 생긴다."
          " 여기 out_max만 보고 채택하지 말 것.")
    out["forms"] = forms


def main() -> int:
    ap = argparse.ArgumentParser(description="보정기 함수형·오염 영향 오프라인 연구 (읽기 전용)")
    ap.add_argument("--pkl", default=None, help="보정기 저장본 경로 (기본: settings)")
    ap.add_argument("--db-days", type=int, default=0, help="predictions.db 최근 N일도 분석")
    ap.add_argument("--json", default=None, help="결과 JSON 저장 경로")
    args = ap.parse_args()

    path = args.pkl
    if path is None:
        try:
            from config.settings import ENSEMBLE_CALIBRATOR_PATH
            path = ENSEMBLE_CALIBRATOR_PATH
        except Exception:
            path = os.path.join(_ROOT, "data", "ensemble_calibrator.pkl")

    print("보정기 함수형·오염 영향 연구 [461차 P-D] — 읽기 전용")
    print("저장본: %s" % path)

    result = {}
    probs, labels = _load_pkl(path)
    if probs is not None and len(probs):
        artifact = probs >= _ARTIFACT_MIN
        result["pkl"] = {}
        _report_block("A. 보정기 저장본 윈도 (라이브가 실제로 쓰는 표본)",
                      probs, labels, artifact, result["pkl"])

    if args.db_days > 0:
        loaded = _load_db(args.db_days)
        if loaded and loaded[0] is not None:
            raw, ok, wc = loaded
            # 붕괴 플래그가 있으면 그것을 신뢰하고, 없으면 raw≈1.0으로 폴백
            artifact = wc | (raw >= _ARTIFACT_MIN)
            result["db"] = {}
            _report_block("B. predictions.db 최근 %d일 (장기 표본)" % args.db_days,
                          raw, ok, artifact, result["db"])

    if not result:
        print("\n[FATAL] 분석할 표본이 없다.")
        return 1

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=float)
        print("\n[저장] %s" % args.json)

    print()
    print("=" * 78)
    print("해석 지침 — 이 출력만으로 배포 결정을 내리지 말 것")
    print("  · span 붕괴의 직접 원인이 C인지 오염인지를 [3]에서 먼저 가른다.")
    print("  · clean AUC 상승이 SE 안이면 '정보 부재' 진단은 아직 유효하다(430차).")
    print("  · 함수형 교체는 §9 사전등록 → 섀도 → 주간회의. [45]·449차 R4와 한 안건.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
