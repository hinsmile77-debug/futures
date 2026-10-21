"""표본실측 스크립트 공통 경로 — 저장소 위치를 하드코딩하지 않는다(두 PC 공유).

REPO   : 이 파일 기준 3단계 위(docs/가격움직임패턴연구/표본실측 → 저장소 루트)
DB     : data/db/<파일명>
PC_DIR : 이 폴더 아래 <PC명>/ — 산출 CSV 는 PC별로 분리한다(README.md 공유 규약)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from utils.db_utils import pc_id  # noqa: E402

PC = pc_id()
PC_DIR = os.path.join(HERE, PC)


def db(name):
    return os.path.join(REPO, "data", "db", name)


def out(name):
    os.makedirs(PC_DIR, exist_ok=True)
    return os.path.join(PC_DIR, name)
