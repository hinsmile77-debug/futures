# utils/setup_dirs.py — 새 PC 배포 시 1회 실행
"""
1. 필요한 폴더를 모두 생성합니다.
2. secrets.py.example을 secrets.py로 복사합니다 (없는 경우).
3. 전체 DB를 초기화합니다.

사용법:
    python utils/setup_dirs.py
"""
import os
import shutil
import sys

# 프로젝트 루트를 sys.path에 추가
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config.settings import (
    DATA_DIR, RAW_DIR, PROCESSED_DIR, DB_DIR, LOG_DIR,
    MODEL_DIR, HORIZON_DIR, SCALER_DIR,
)

DIRS = [
    DATA_DIR, RAW_DIR, PROCESSED_DIR, DB_DIR, LOG_DIR,
    MODEL_DIR, HORIZON_DIR, SCALER_DIR,
    os.path.join(BASE_DIR, "config"),
    os.path.join(BASE_DIR, "collection", "kiwoom"),
    os.path.join(BASE_DIR, "collection", "macro"),
    os.path.join(BASE_DIR, "collection", "news"),
    os.path.join(BASE_DIR, "collection", "options"),
    os.path.join(BASE_DIR, "features", "technical"),
    os.path.join(BASE_DIR, "features", "supply_demand"),
    os.path.join(BASE_DIR, "features", "options"),
    os.path.join(BASE_DIR, "features", "macro"),
    os.path.join(BASE_DIR, "features", "sentiment"),
    os.path.join(BASE_DIR, "learning", "shap"),
    os.path.join(BASE_DIR, "learning", "self_learning"),
    os.path.join(BASE_DIR, "learning", "rl"),
    os.path.join(BASE_DIR, "safety"),
    os.path.join(BASE_DIR, "strategy", "entry"),
    os.path.join(BASE_DIR, "strategy", "exit"),
    os.path.join(BASE_DIR, "strategy", "position"),
    os.path.join(BASE_DIR, "dashboard"),
    os.path.join(BASE_DIR, "backtest"),
    os.path.join(BASE_DIR, "utils"),
    os.path.join(BASE_DIR, "logs"),
    os.path.join(BASE_DIR, "docs"),
    os.path.join(BASE_DIR, "logging_system"),
]


def create_dirs():
    for d in DIRS:
        os.makedirs(d, exist_ok=True)
    print("[setup] 폴더 생성 완료")


def copy_secrets():
    example = os.path.join(BASE_DIR, "config", "secrets.py.example")
    target  = os.path.join(BASE_DIR, "config", "secrets.py")
    if not os.path.exists(target) and os.path.exists(example):
        shutil.copy(example, target)
        print(f"[setup] secrets.py 생성됨 → config/secrets.py 열어서 계좌 정보 입력 필요")
    elif os.path.exists(target):
        print("[setup] secrets.py 이미 존재")
    else:
        print("[setup] secrets.py.example 없음 — 수동으로 config/secrets.py 생성 필요")


def init_dbs():
    from utils.db_utils import init_all_dbs
    init_all_dbs()
    print("[setup] DB 초기화 완료")


if __name__ == "__main__":
    print("=" * 50)
    print("미륵이 — 초기 설정 시작")
    print("=" * 50)
    create_dirs()
    copy_secrets()
    init_dbs()
    print("=" * 50)
    print("설정 완료! 다음 단계:")
    print("  1. config/secrets.py 열어서 계좌 정보 입력")
    print("  2. python main.py 실행")
    print("=" * 50)
