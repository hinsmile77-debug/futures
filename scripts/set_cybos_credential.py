# -*- coding: utf-8 -*-
"""
Windows Credential Manager에 CREON Plus 자격증명 등록 스크립트
사용법: conda activate py37_32 && python scripts/set_cybos_credential.py
"""
import subprocess
import sys
import getpass


def register_credential(target, username, password):
    cmd = ["cmdkey", "/add:" + target, "/user:" + username, "/pass:" + password]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[OK] '{target}' 자격증명 등록 완료.")
    else:
        print(f"[ERROR] 등록 실패: {result.stderr.strip()}")
        sys.exit(1)


def main():
    print("=" * 60)
    print("  Mireuk - CREON Plus 자격증명 등록")
    print("  Windows Credential Manager에 저장됩니다.")
    print("=" * 60)
    print()
    print("1. CREON Plus (대신증권) 로그인 정보")
    print("   - ID: 대신증권 아이디")
    print("   - PW: 대신증권 비밀번호 (HTS 로그인 비밀번호)")
    print()

    creon_id = input("CREON Plus ID: ").strip()
    if not creon_id:
        print("[ERROR] ID를 입력하세요.")
        sys.exit(1)

    creon_pw = getpass.getpass("CREON Plus 비밀번호: ")
    if not creon_pw:
        print("[ERROR] 비밀번호를 입력하세요.")
        sys.exit(1)

    print()
    register_credential("creonplus", creon_id, creon_pw)

    print()
    print("=" * 60)
    print("  [완료] 자격증명 등록이 완료되었습니다.")
    print()
    print("  다음 단계:")
    print("  1. CREON_PLUS.bat 실행 (Cybos Plus 연결)")
    print("  2. start_mireuk_CREON.bat 실행 (미륵이 시작)")
    print("=" * 60)


if __name__ == "__main__":
    main()
