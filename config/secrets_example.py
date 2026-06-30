# config/secrets_example.py
# =============================================================
# 이 파일을 복사하여 config/secrets.py 로 저장 후 실제 값 입력
# secrets.py 는 .gitignore 에 포함 — 절대 Git 에 올리지 말 것
# =============================================================

# [CREON] 대신증권 계좌 정보
# FUTURES_CODE_PREFIX: KOSPI200 선물은 "A05", 모의투자는 "A01"
FUTURES_CODE_PREFIX = "A05"   # 실투자: "A05" / 모의투자: "A01"

# 계좌 번호 및 비밀번호
# python scripts/set_cybos_credential.py 로 Windows Credential Manager 에 등록 권장
ACCOUNT_NO  = ""   # 예: "12345678901"
ACCOUNT_PWD = ""   # 계좌 비밀번호 (4자리 또는 6자리)

# Cybos Plus API Key (선택 — 필요 시)
APP_KEY    = ""
APP_SECRET = ""

# 외부 API (선택)
KAKAO_TOKEN  = ""   # 카카오 알림톡 토큰
BOK_API_KEY  = ""   # 한국은행 API 키 (거시경제 피처)
FRED_API_KEY = ""   # FRED API 키 (미국 금리 등)

# Slack 알림 (선택)
SLACK_BOT_TOKEN   = ""
SLACK_CHANNEL_ID  = ""
