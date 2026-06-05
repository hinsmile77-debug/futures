"""
P0 긴급 수정: shap_feature_registry.json의 active_features / baseline_features를
feature_names.pkl(105개) 기준으로 교체.

dry_run=True  → 변경 내용만 출력, 파일 미수정
dry_run=False → 실제 저장
"""
import pickle, json, os, sys, shutil, datetime

DRY_RUN = "--apply" not in sys.argv  # 기본은 dry-run

PKL_PATH      = "model/horizons/feature_names.pkl"
REGISTRY_PATH = "data/db/shap_feature_registry.json"

# ── 1. pkl 읽기 ─────────────────────────────────────────────
with open(PKL_PATH, "rb") as f:
    feat_names = pickle.load(f)

print("=== feature_names.pkl ===")
print("  피처 수:", len(feat_names))
print("  처음 5개:", feat_names[:5])
print("  마지막 5개:", feat_names[-5:])

# ── 2. 현재 registry 읽기 ────────────────────────────────────
with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
    registry = json.load(f)

print("\n=== 현재 registry ===")
print("  active_features 수  :", len(registry.get("active_features") or []))
print("  baseline_features 수:", len(registry.get("baseline_features") or []))
print("  pending_change      :", registry.get("pending_change"))

# ── 3. 교체 내용 확인 ────────────────────────────────────────
old_active   = list(registry.get("active_features") or [])
old_baseline = list(registry.get("baseline_features") or [])

missing_in_active   = [f for f in feat_names if f not in old_active]
extra_in_active     = [f for f in old_active   if f not in feat_names]
missing_in_baseline = [f for f in feat_names if f not in old_baseline]
extra_in_baseline   = [f for f in old_baseline if f not in feat_names]

print("\n=== active_features 차이 ===")
print("  pkl에 있지만 registry에 없는 것 ({})".format(len(missing_in_active)), missing_in_active[:10])
print("  registry에 있지만 pkl에 없는 것 ({})".format(len(extra_in_active)), extra_in_active[:10])

print("\n=== baseline_features 차이 ===")
print("  pkl에 있지만 baseline에 없는 것 ({})".format(len(missing_in_baseline)), missing_in_baseline[:10])
print("  baseline에 있지만 pkl에 없는 것 ({})".format(len(extra_in_baseline)), extra_in_baseline[:10])

if DRY_RUN:
    print("\n[DRY RUN] 실제 변경 없음. 적용하려면: python _fix_registry_p0.py --apply")
    sys.exit(0)

# ── 4. 백업 ─────────────────────────────────────────────────
backup_path = REGISTRY_PATH + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(REGISTRY_PATH, backup_path)
print("\n백업 완료:", backup_path)

# ── 5. 교체 ─────────────────────────────────────────────────
registry["active_features"]   = list(feat_names)
registry["baseline_features"] = list(feat_names)
registry["pending_change"]    = {}  # pending 클리어

with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("=== 적용 완료 ===")
print("  active_features  →", len(feat_names), "개")
print("  baseline_features→", len(feat_names), "개")
print("  pending_change   →  클리어")
print("\n다음 ScalerWarmup에서 feat=105 확인 필요")
