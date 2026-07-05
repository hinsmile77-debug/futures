# scripts/test_program_investor_probe.py
"""
[260704 감사 P2] request_program_investor() / request_investor_futures() 검증용 임시 스크립트.
관리자 권한 터미널(Creon Plus 연결된 세션)에서 직접 실행해 결과를 확인한다.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from collection.cybos.api_connector import CybosAPI

api = CybosAPI()
print("=== request_program_investor() ===")
print(api.request_program_investor())
print()
print("=== request_investor_futures() ===")
print(api.request_investor_futures())
