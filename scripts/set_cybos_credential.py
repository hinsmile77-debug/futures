# -*- coding: utf-8 -*-
"""
Windows Credential Manager에 HTS 자격증명 등록 스크립트
- win32cred.CredWrite로 CRED_TYPE_GENERIC(1)으로 저장
- cmdkey는 DOMAIN(Type=2)로 저장해 cybos_autologin.py가 읽지 못하는 문제를 회피

사용법:
  conda activate py37_32 && python scripts/set_cybos_credential.py --broker creon
  conda activate py37_32 && python scripts/set_cybos_credential.py --broker cybos
  (--broker 생략 시 BROKER_TYPE 환경변수 또는 대화형 선택)
"""
import os
import sys
import getpass

try:
    import win32cred
except ImportError:
    print("[ERROR] pywin32 미설치 -- 'pip install pywin32' 후 재시도")
    sys.exit(1)

_BROKER_INFO = {
    "creon": {
        "target":   "creonplus",
        "bat_login": "CREON_PLUS.bat",
        "bat_start": "start_mireuk_CREON.bat",
        "label":    "CREON Plus",
    },
    "cybos": {
        "target":   "cybosplus",
        "bat_login": "CYBOS_PLUS.bat",
        "bat_start": "start_mireuk_Cybos.bat",
        "label":    "CYBOS Plus",
    },
}


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


def _resolve_broker():
    # 1. --broker 인수 우선
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--broker" and i + 2 <= len(sys.argv[1:]):
            return sys.argv[i + 2].lower()
        if arg.startswith("--broker="):
            return arg.split("=", 1)[1].lower()
    # 2. BROKER_TYPE 환경변수
    env = os.getenv("BROKER_TYPE", "").strip().lower()
    if env in _BROKER_INFO:
        return env
    # 3. 대화형 선택
    print("HTS 종류를 선택하세요:")
    print("  1) CREON Plus (MW0602 - 대신증권 Creon)")
    print("  2) CYBOS Plus (MW0601 - 대신증권 Cybos)")
    choice = input("선택 (1/2): ").strip()
    return "creon" if choice == "1" else "cybos"


def main():
    broker = _resolve_broker()
    if broker not in _BROKER_INFO:
        print("[ERROR] 알 수 없는 브로커: %s (creon 또는 cybos 입력)" % broker)
        sys.exit(1)

    info = _BROKER_INFO[broker]
    print("=" * 60)
    print("  Mireuk - %s 자격증명 등록 (GENERIC Type)" % info["label"])
    print("  win32cred.CredWrite 사용 -- cmdkey 대신 사용하세요.")
    print("=" * 60)
    print()

    uid = input("%s ID (대신증권 아이디): " % info["label"]).strip()
    if not uid:
        print("[ERROR] ID를 입력하세요.")
        sys.exit(1)

    pw = getpass.getpass("%s 비밀번호 (HTS 로그인 비밀번호): " % info["label"])
    if not pw:
        print("[ERROR] 비밀번호를 입력하세요.")
        sys.exit(1)

    write_generic_credential(info["target"], uid, pw)

    print()
    print("=" * 60)
    print("  [완료] 자격증명 등록이 완료되었습니다.")
    print()
    print("  다음 단계:")
    print("  1. %s 실행 (HTS 연결)" % info["bat_login"])
    print("  2. %s 실행 (미륵이 시작)" % info["bat_start"])
    print("=" * 60)


if __name__ == "__main__":
    main()
