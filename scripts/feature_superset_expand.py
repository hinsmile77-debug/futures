# -*- coding: utf-8 -*-
"""[MW0601 473차 / D8·P2-B] 학습 피처 슈퍼셋 97 → N 확장 — 스냅샷·확장·롤백.

무엇을 푸는가
-------------
`horizon_feature_sets.json`에 이름을 올려도, `raw_features_horizon`에 값이
정상 수집돼도, 그 피처는 **학습에 들어가지 못한다.** 상위에 개수 고정 슈퍼셋이
있고 그걸 늘릴 수 있는 코드 경로가 존재하지 않기 때문이다.

    X 컬럼 후보 = shap_feature_registry.json:active_features  (97)   ← 절대 상한
          ↓
    호라이즌 X = horizon_feature_sets.json include ∩ 97              ← 교집합에서 탈락

🔴 **범인 줄에 대한 정정.** `CLAUDE.md`와 458차 딥다이브는 `batch_retrainer.py`의
   `use_feat_names`(Phase 2)를 지목했다. 그 줄이 합집합 결과를 덮어쓰는 것은
   사실이나, **Phase 2는 프로덕션에서 돌지 않는다**(`--phase2` 수동 전용,
   라이브 로그에 `[Retrain-P2]` 0건). EOD·장중을 모두 잡고 있는 것은 Phase 1의
   registry 교집합이다. 둘 다 97이라 증상이 같아 구분되지 않았다.
   → **registry를 안 늘리면 pkl만 늘려도 아무 일도 일어나지 않는다.**

자기유지 루프
-------------
    batch_retrainer: 전 구간 키 합집합 → registry(97)과 교집합 → 97
                     → `_save_feature_names(97)` 로 pkl에 재기입
    main.py:_sync_feature_registry_with_model()  : **비어 있을 때만** 채움
    multi_horizon_model:_check_registry_...()    : 불일치 시 ERROR 로그만, 교정 없음
    유일한 갱신 경로: 주간 SHAP 1:1 교체 — **개수 불변**

지켜야 할 3-튜플 불변식
-----------------------
    active_features == feature_names.pkl == scaler_{h}.pkl.n_features_in_ == N

하나라도 어긋나면 `multi_horizon_model.validate_and_resync()`가 **6/6 호라이즌을
`_is_fitted=False`로 끈다** = 예측 전면 중단. 이것이 이 작업의 유일한 진짜 위험이다.

사용
----
    python scripts/feature_superset_expand.py                 # 현황만 (기본)
    python scripts/feature_superset_expand.py --snapshot      # 롤백 스냅샷 생성
    python scripts/feature_superset_expand.py --plan          # 확장 계획 dry-run
    python scripts/feature_superset_expand.py --plan --include-pending
    python scripts/feature_superset_expand.py --apply --governance-approved
    python scripts/feature_superset_expand.py --rollback DIR  # 스냅샷 복원

🔴 **`--apply`는 기본적으로 거부된다.** `active_features` 직접 편집은 331차가
  명시적으로 배제한 경로이기 때문이다 — 신규 피처는 `DYNAMIC_FEATURES_POOL`에
  등록해 주간 SHAP 심사가 교체 후보로 제안하는 문만 여는 것이 관례이고, 근거는
  `CLAUDE.md` §6(알파 자동 통합 금지)다. 그 관례로는 개수가 97에 고정되며(1:1 교체),
  그 제약을 푸는 것이 D8이자 **거버넌스 결정**이다.

⚠ `--apply` 다음에 **반드시** 비거래일 전체 재학습이 이어져야 한다. 확장만 하고
  재학습을 안 하면 registry·pkl(N)과 스케일러(97)가 갈려 예측이 멈춘다.
  절차 전문은 `dev_memory/NEXT_TODO.md` 473차 D8 항목.

정보만 필요하면 프로덕션을 건드릴 이유가 없다 — `BatchRetrainer(model_dir=,
scaler_dir=)`가 둘 다 파라미터라(346차 통합테스트 선례) 스크래치 디렉터리로
확장 재학습을 돌려 전환 거동만 관찰할 수 있다.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import pickle
import shutil
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

REGISTRY = os.path.join(_ROOT, "data", "db", "shap_feature_registry.json")
MODEL_DIR = os.path.join(_ROOT, "model", "horizons")
SCALER_DIR = os.path.join(_ROOT, "model", "scaler")
SNAP_ROOT = os.path.join(_ROOT, "data", "superset_snapshots")

_HORIZONS = ("1m", "3m", "5m", "10m", "15m", "30m")


# ── 현황 ────────────────────────────────────────────────────────────────────

def _load_registry():
    with open(REGISTRY, encoding="utf-8") as f:
        return json.load(f)


def _load_pkl(path):
    try:
        with open(path, "rb") as f:
            return list(pickle.load(f))
    except (IOError, OSError, pickle.UnpicklingError, EOFError):
        return None


def _scaler_width(hz):
    p = os.path.join(SCALER_DIR, "scaler_%s.pkl" % hz)
    try:
        with open(p, "rb") as f:
            sc = pickle.load(f)
        return int(getattr(sc, "n_features_in_", -1))
    except Exception:
        return None


def survey():
    """3-튜플 현황. 확장 전후로 같은 함수를 돌려 불변식을 확인한다."""
    reg = _load_registry()
    active = list(reg.get("active_features") or [])
    baseline = list(reg.get("baseline_features") or [])
    shared = _load_pkl(os.path.join(MODEL_DIR, "feature_names.pkl"))
    out = {
        "registry_active": len(active),
        "registry_baseline": len(baseline),
        "shared_pkl": len(shared) if shared is not None else None,
        "pending_change": reg.get("pending_change") or {},
        "per_horizon": {},
        "consistent": None,
    }
    for hz in _HORIZONS:
        out["per_horizon"][hz] = {
            "hz_pkl": (lambda v: len(v) if v is not None else None)(
                _load_pkl(os.path.join(MODEL_DIR, "feature_names_%s.pkl" % hz))),
            "scaler_width": _scaler_width(hz),
        }
    widths = {v["scaler_width"] for v in out["per_horizon"].values()
              if v["scaler_width"] is not None}
    out["consistent"] = (
        len(active) == len(baseline)
        and out["shared_pkl"] == len(active)
        and widths == {len(active)}
    )
    out["scaler_widths"] = sorted(widths)
    return out


def _need_add():
    """레지스트리에서 `pkl: need_add`로 표시된 피처 — 확장 후보.

    ⚠ `get_need_add_features()`는 **평평한 합집합 리스트**를 준다(호라이즌별이
      아니다). 어느 호라이즌이 무엇을 못 쓰는지가 D8 판단에 필요하므로 여기서
      직접 분해한다. 합집합 결과는 그 함수와 대조해 일치를 확인한다.
    """
    from features.horizon_feature_registry import (_registry, _HORIZONS as _RHZ,
                                                   get_need_add_features)
    reg = _registry() or {}
    per_hz, merged = {}, []
    for hz in _RHZ:
        names = []
        for entry in (reg.get(hz, {}) or {}).get("include", []) or []:
            if entry.get("pkl") == "need_add" and entry.get("name"):
                names.append(entry["name"])
                if entry["name"] not in merged:
                    merged.append(entry["name"])
        per_hz[hz] = names

    official = list(get_need_add_features() or [])
    if set(official) != set(merged):
        print("⚠ need_add 분해가 공식 함수와 다르다 — 분해 %d vs 공식 %d"
              % (len(merged), len(official)))
    return per_hz, merged


# ── 스냅샷 / 롤백 ───────────────────────────────────────────────────────────

_SNAP_FILES = (
    ("data/db", "shap_feature_registry.json"),
    ("model/horizons", "feature_names.pkl"),
    ("model/horizons", "rf_horizons.pkl"),
)


def _snap_targets():
    items = list(_SNAP_FILES)
    for hz in _HORIZONS:
        items.append(("model/horizons", "feature_names_%s.pkl" % hz))
        items.append(("model/horizons", "gbm_%s.pkl" % hz))
        items.append(("model/horizons", "gbm_%s_meta.json" % hz))
        items.append(("model/horizons", "gbm_%s_acc.txt" % hz))
        items.append(("model/scaler", "scaler_%s.pkl" % hz))
    return items


def snapshot(stamp=None):
    """롤백 경로. **이걸 안 만들면 `--apply`가 거부된다.**"""
    stamp = stamp or _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(SNAP_ROOT, stamp)
    copied, missing = [], []
    for rel, name in _snap_targets():
        src = os.path.join(_ROOT, rel, name)
        if not os.path.exists(src):
            missing.append(os.path.join(rel, name))
            continue
        d = os.path.join(dest, rel)
        os.makedirs(d, exist_ok=True)
        shutil.copy2(src, os.path.join(d, name))
        copied.append(os.path.join(rel, name))
    with open(os.path.join(dest, "_survey.json"), "w", encoding="utf-8") as f:
        json.dump({"stamp": stamp, "survey": survey(),
                   "copied": copied, "missing": missing},
                  f, ensure_ascii=False, indent=1)
    return dest, copied, missing


def rollback(snap_dir):
    restored = []
    for rel, name in _snap_targets():
        src = os.path.join(snap_dir, rel, name)
        if not os.path.exists(src):
            continue
        shutil.copy2(src, os.path.join(_ROOT, rel, name))
        restored.append(os.path.join(rel, name))
    return restored


def _latest_snapshot():
    if not os.path.isdir(SNAP_ROOT):
        return None
    dirs = sorted(d for d in os.listdir(SNAP_ROOT)
                  if os.path.isdir(os.path.join(SNAP_ROOT, d)))
    return os.path.join(SNAP_ROOT, dirs[-1]) if dirs else None


# ── 확장 계획 ───────────────────────────────────────────────────────────────

def plan(include_pending=False, coverage_min=0.0):
    """확장 계획. **순서 보존 append만** — 기존 97의 인덱스를 흔들지 않는다.

    `main.py:_rebuild_sgd_feat_indices()`와
    `multi_horizon_model:_rebuild_hz_feat_indices()`가 **인덱스 기반**이라,
    중간에 끼워 넣으면 기존 피처의 위치가 밀려 조용히 다른 값을 읽는다.
    """
    reg = _load_registry()
    active = list(reg.get("active_features") or [])
    per_hz, cands = _need_add()

    if include_pending:
        from features.horizon_feature_registry import get_feature_set
        for hz in _HORIZONS:
            for name in (get_feature_set(hz, True) or []):
                if name not in active and name not in cands:
                    cands.append(name)

    cov = _coverage(cands) if cands else {}
    accepted, rejected = [], []
    for name in cands:
        c = cov.get(name)
        if c is None:
            rejected.append((name, "DB 존재율 산출 실패"))
        elif c < coverage_min:
            rejected.append((name, "존재율 %.1f%% < 하한 %.1f%%"
                             % (100 * c, 100 * coverage_min)))
        else:
            accepted.append(name)

    return {
        "current_n": len(active),
        "per_horizon_need_add": per_hz,
        "candidates": cands,
        "coverage": cov,
        "accepted": accepted,
        "rejected": rejected,
        "new_n": len(active) + len(accepted),
        "new_features_appended_in_order": accepted,
    }


def _coverage(names):
    """학습창(최근 26주) 안에서 각 피처가 실제로 존재하는 행 비율.

    🔴 이 검사가 왜 필요한가 — `batch_retrainer`가 X를 만들 때
      `rec[1].get(f, 0.0)`로 채운다. 어떤 피처가 특정 시점부터만 수집됐다면
      (`opt_chain_pcr` = 2026-07-15~) **그 이전 구간이 전부 0.0으로 깔려**
      "값이 0인 기간"이라는 **가짜 신호**가 학습에 들어간다.
      존재율을 먼저 보고 하한을 걸거나 학습창을 줄여야 한다.
    """
    from utils.analysis_db import connect_ro
    from config.settings import RAW_DATA_DB
    want = set(names)
    hit = dict.fromkeys(want, 0)
    total = 0
    try:
        con = connect_ro(RAW_DATA_DB)
    except Exception:
        return {}
    try:
        cur = con.execute(
            "SELECT features FROM raw_features "
            "WHERE ts >= date('now','-182 day') ORDER BY ts"
        )
        for (feats,) in cur:
            try:
                d = json.loads(feats)
            except (ValueError, TypeError):
                continue
            total += 1
            for n in want:
                if n in d:
                    hit[n] += 1
    finally:
        con.close()
    if not total:
        return {}
    return {n: hit[n] / float(total) for n in want}


def apply_expansion(accepted, snap_dir):
    """registry(active+baseline)와 공유 pkl을 **동시에** 늘린다.

    ⚠ `baseline_features`도 함께 늘려야 한다 — `main.py`의 baseline 원복
      경로가 그것을 쓰므로, 안 늘리면 원복 버튼 한 번에 97로 되돌아간다.

    🔴 **이 함수는 확립된 관례를 벗어난다 — 승인 없이 부르지 말 것.**
      331차가 명시적으로 정했다: 신규 피처는 `config/constants.py:
      DYNAMIC_FEATURES_POOL`에 등록해 **주간 SHAP 심사가 "교체 후보"로 제안할
      수 있는 문만 열고**, `active_features`는 **직접 편집하지 않는다** —
      근거는 `CLAUDE.md` §6(알파 자동 통합 금지)이다.
      그 관례로는 개수가 97에 고정된다(1:1 교체뿐). 그 제약을 푸는 것이 D8이고,
      그것은 **거버넌스 결정**이지 스크립트가 넘을 선이 아니다.
      → `--apply`는 `--governance-approved`를 함께 요구한다.
    """
    if not snap_dir or not os.path.isdir(snap_dir):
        raise SystemExit("스냅샷 없이 확장할 수 없다 — 먼저 --snapshot")
    if not accepted:
        raise SystemExit("확장 대상 0건")

    reg = _load_registry()
    active = list(reg.get("active_features") or [])
    baseline = list(reg.get("baseline_features") or [])
    for n in accepted:
        if n not in active:
            active.append(n)          # append only — 인덱스 보존
        if n not in baseline:
            baseline.append(n)
    reg["active_features"] = active
    reg["baseline_features"] = baseline
    with open(REGISTRY, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=1)

    shared_path = os.path.join(MODEL_DIR, "feature_names.pkl")
    shared = _load_pkl(shared_path) or []
    for n in accepted:
        if n not in shared:
            shared.append(n)
    with open(shared_path, "wb") as f:
        pickle.dump(shared, f, protocol=4)   # py37_32 로드 호환 (protocol=4 고정)
    return len(active), len(shared)


# ── CLI ─────────────────────────────────────────────────────────────────────

def _print_survey(s):
    print("현황 — 3-튜플 불변식")
    print("  registry active   : %s" % s["registry_active"])
    print("  registry baseline : %s" % s["registry_baseline"])
    print("  공유 feature_names.pkl : %s" % s["shared_pkl"])
    print("  scaler 폭 : %s" % (s["scaler_widths"] or "—"))
    print("  호라이즌별 pkl : %s" % ", ".join(
        "%s=%s" % (h, v["hz_pkl"]) for h, v in s["per_horizon"].items()))
    print("  pending_change : %s" % (s["pending_change"] or "{}"))
    print("  → 정합: %s" % ("OK" if s["consistent"] else "🔴 불일치 — 확장 전 해소 필요"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--rollback", metavar="DIR")
    ap.add_argument("--include-pending", action="store_true")
    ap.add_argument("--coverage-min", type=float, default=0.0,
                    help="학습창 내 존재율 하한(0~1). 미만이면 확장 대상에서 제외")
    ap.add_argument("--governance-approved", action="store_true",
                    help="active_features 직접 편집에 대한 주간회의/사용자 승인이 "
                         "있음을 명시. --apply에 필수 (331차 관례 — CLAUDE.md §6)")
    args = ap.parse_args()

    if args.rollback:
        done = rollback(args.rollback)
        print("복원 %d개:" % len(done))
        for d in done:
            print("  " + d)
        _print_survey(survey())
        return 0

    s = survey()
    _print_survey(s)

    if args.snapshot:
        dest, copied, missing = snapshot()
        print()
        print("스냅샷: %s" % dest)
        print("  복사 %d개 / 누락 %d개%s"
              % (len(copied), len(missing),
                 (" → " + ", ".join(missing)) if missing else ""))
        return 0

    if not (args.plan or args.apply):
        print()
        print("확장 절차: --snapshot → --plan → --apply --governance-approved")
        print("⚠ --apply 는 거버넌스 승인 플래그 없이는 거부된다(331차 관례, CLAUDE.md §6).")
        print("  전환 거동만 보고 싶으면 샌드박스 재학습을 쓸 것 — 프로덕션 위험 0.")
        return 0

    p = plan(include_pending=args.include_pending, coverage_min=args.coverage_min)
    print()
    print("확장 계획  %d → %d" % (p["current_n"], p["new_n"]))
    print("  호라이즌별 need_add:")
    for hz in _HORIZONS:
        v = p["per_horizon_need_add"].get(hz) or []
        if v:
            print("    %-4s %d종  %s" % (hz, len(v), ", ".join(v)))
    print("  후보 %d종 (append 순서 보존):" % len(p["candidates"]))
    for n in p["candidates"]:
        c = p["coverage"].get(n)
        print("    %-32s 학습창 존재율 %s"
              % (n, ("%.1f%%" % (100 * c)) if c is not None else "N/A"))
    if p["rejected"]:
        print("  제외 %d종:" % len(p["rejected"]))
        for n, why in p["rejected"]:
            print("    %-32s %s" % (n, why))

    if not args.apply:
        print()
        print("dry-run. 실제 반영하려면 --apply (스냅샷 선행 필수).")
        return 0

    if not args.governance_approved:
        print()
        print("🔴 --apply 거부 — `--governance-approved` 가 없다.")
        print()
        print("   `active_features` **직접 편집**은 331차가 명시적으로 배제한 경로다:")
        print("     신규 피처는 config/constants.py:DYNAMIC_FEATURES_POOL 에 등록해")
        print("     주간 SHAP 심사가 '교체 후보'로 제안하는 문만 연다 —")
        print("     근거는 CLAUDE.md §6(알파 자동 통합 금지).")
        print("   그 경로는 개수가 97에 고정된다(1:1 교체). 그 제약을 푸는 것이 D8이며")
        print("   **거버넌스 결정**이다. 승인 후 --governance-approved 를 붙일 것.")
        print()
        print("   ⚠ 전례를 먼저 읽을 것 — 292차가 MW0602에서 97→105를 실제로 했고,")
        print("     기계적으로는 성공했으나 후속 사고가 이어졌다:")
        print("       · ScalerWarmup 0-패딩 → long 50분 정확도 14~20% 급락")
        print("       · feature_names=105 vs scaler=10 → 전 호라이즌 비활성화")
        print("       · Phase2 pkl 덮어쓰기 → 추론이 12피처 공간으로 축소")
        print("   정보만 필요하면 프로덕션을 건드리지 말 것 —")
        print("   BatchRetrainer(model_dir=, scaler_dir=)로 샌드박스 재학습이 가능하다.")
        return 2

    snap = _latest_snapshot()
    if not snap:
        print()
        print("🔴 스냅샷이 없다 — 먼저 --snapshot 을 돌릴 것. 중단한다.")
        return 2
    n_reg, n_pkl = apply_expansion(p["accepted"], snap)
    print()
    print("확장 완료 — registry %d · pkl %d (스냅샷 %s)" % (n_reg, n_pkl, snap))
    print()
    print("🔴 여기서 멈추면 안 된다 — scaler는 아직 %s 폭이다."
          % (s["scaler_widths"] or "?"))
    print("   비거래일에 전체 재학습을 이어서 돌릴 것:")
    print("     <py310_64> python scripts/eod_retrain.py --weeks 26 --force")
    print("   그 다음 이 스크립트를 인자 없이 다시 돌려 3-튜플 정합을 확인한다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
