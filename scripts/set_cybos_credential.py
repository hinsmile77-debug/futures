# -*- coding: utf-8 -*-
"""
Windows Credential Manager에 CREON Plus 자격증명 등록 스크립트
- win32cred.CredWrite로 CRED_TYPE_GENERIC(1)으로 저장
- cmdkey는 DOMAIN(Type=2)로 저장해 cybos_autologin.py가 읽지 못하는 문제를 회피

사용법: conda activate py37_32 && python scripts/set_cybos_credential.py
"""
import sys
import getpass

try:
    import win32cred
except ImportError:
    print("[ERROR] pywin32 미설치 -- 'pip install pywin32' 후 재시도")
    sys.exit(1)


def write_generic_credential(target, username, password):
    cred = {
        "Type": win32cred.CRED_TYPE_GENERIC,
        "TargetName": target,
        "UserName": username,
        "CredentialBlob": password,
        "Persist": win32cred.CRED_PERSIST_LOCAL_MACHINE,
        "Comment": "Mireuk auto-login credential",
    }
    win32cred.CredWrite(cred, 0)
    print("[OK] '%s' GENERIC 자격증명 등록 완료." % target)


def main():
    print("=" * 60)
    print("  Mireuk - CREON Plus 자격증명 등록 (GENERIC Type)")
    print("  win32cred.CredWrite 사용 -- cmdkey 대신 사용하세요.")
    print("=" * 60)
    print()

    creon_id = input("CREON Plus ID (대신증권 아이디): ").strip()
    if not creon_id:
        print("[ERROR] ID를 입력하세요.")
        sys.exit(1)

    creon_pw = getpass.getpass("CREON Plus 비밀번호 (HTS 로그인 비밀번호): ")
    if not creon_pw:
        print("[ERROR] 비밀번호를 입력하세요.")
        sys.exit(1)

    write_generic_credential("creonplus", creon_id, creon_pw)

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
