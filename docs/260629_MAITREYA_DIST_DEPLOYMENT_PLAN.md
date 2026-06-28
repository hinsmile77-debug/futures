# 미륵이 타 PC 배포 실행계획 및 TODO

> 작성일: 2026-06-29  
> 목표 브랜치: `maitreya_dist` (GitHub: hinsmile77-debug/futures)  
> 배포 목적: MW0601 PC의 미륵이 운영 환경을 타 PC에서 그대로 재현  

---

## 1. 배포 목표

타 PC에서 아래 두 BAT만 순서대로 실행하면 미륵이가 정상 작동한다.

```
1단계: CREON_PLUS.bat  → Cybos Plus (대신증권 HTS) 연결
2단계: start_mireuk_CREON.bat → 미륵이 본체 실행
```

배포 방법: `maitreya_dist` 브랜치를 크론 또는 수동으로 `git pull` 하여 갱신.

---

## 2. 전제 조건 (타 PC 필수 설치 항목)

| 항목 | 설명 | 비고 |
|---|---|---|
| **Windows 10 (32-bit 드라이버 가능)** | Cybos Plus COM 필수 | 64-bit OS + 32-bit Python 가능 |
| **Cybos Plus (대신증권 HTS)** | `C:\DAISHIN\STARTER\ncStarter.exe` | 계좌 개설 필수 |
| **Anaconda (32-bit 또는 64-bit)** | `py37_32` conda 환경 생성용 | miniconda 불가 (GUI 필요) |
| **Python 3.7 32-bit** | conda env `py37_32` 내부 | `INSTALL.bat` 자동 생성 |
| **Git** | 브랜치 pull용 | PATH 등록 필수 |

---

## 3. 배포 브랜치 파일 구성

### 3-1. 포함 파일 (gitignore 수정 후 강제 추가)

```
futures/
├── CREON.bat                    # CREON API 연결 (단독 세션 확인용)
├── CREON_PLUS.bat               # Cybos Plus 자동 로그인 런처
├── start_mireuk_CREON.bat       # 미륵이 실행 + 자동 재시작 루프
├── EOD_RETRAIN.bat              # EOD 재학습 (py310_64 환경)
├── INSTALL.bat                  # [신규] 타 PC 최초 설치 자동화
├── SETUP_GUIDE.md               # [신규] 타 PC 설치 가이드 (한글)
├── requirements.txt             # py37_32 의존성
├── requirements_310.txt         # [신규] py310_64 EOD 재학습 의존성
├── main.py                      # 진입점
├── config/
│   ├── settings.py
│   ├── constants.py
│   ├── strategy_params.py
│   ├── strategy_registry.py
│   ├── krx_holidays.py
│   ├── secrets_example.py       # [신규] secrets.py 템플릿
│   └── __init__.py
├── model/
│   ├── *.py                     # 모델 코드
│   └── scaler/                  # [gitignore 제외] GBM pkl + scaler + feature_names
├── data/
│   ├── *.json                   # 상태 파일 (초기화 버전)
│   ├── *.pkl                    # ensemble_calibrator, meta_conf_state
│   └── db/                      # [gitignore 제외] 초기 빈 DB 파일들
├── scripts/                     # 모든 스크립트
├── features/                    # 피처 모듈
├── strategy/                    # 전략 모듈
├── collection/                  # 데이터 수집 모듈
├── learning/                    # 온라인 학습 모듈
├── safety/                      # Circuit Breaker 등
├── dashboard/                   # Qt 대시보드
├── utils/                       # 공통 유틸
├── docs/                        # 문서
├── CLAUDE.md
├── CORE.md
├── ROADMAP.md
└── PROJECT_DESIGN.md
```

### 3-2. 제외 파일 (배포 브랜치에도 제외)

```
config/secrets.py          # 계좌정보 — 타 PC에서 직접 입력
logs/                      # 로그는 실행 후 생성
data/raw/                  # 원시 데이터 (실행 시 수집)
data/processed/            # 전처리 데이터 (실행 시 생성)
data/db/*.bak_*            # DB 백업 파일
__pycache__/
.idea/ .vscode/ .claude/
```

---

## 4. 타 PC 최초 설치 순서

### STEP 1: 저장소 클론

```bat
git clone -b maitreya_dist https://github.com/hinsmile77-debug/futures.git
cd futures
```

### STEP 2: Cybos Plus HTS 설치

1. 대신증권 홈페이지에서 **Cybos Plus** 다운로드 및 설치
2. 설치 경로 기본값: `C:\DAISHIN\`
3. 로그인 테스트 후 종료

### STEP 3: INSTALL.bat 실행 (conda 환경 자동 구성)

```bat
INSTALL.bat
```

- `py37_32` conda env 자동 생성
- **32-bit SSL DLL 자동 복사** (`libssl-1_1.dll` → `DLLs/`) — pip SSL 오류 선제 해결
- `requirements.txt` 패키지 자동 설치 (`PYTHONUTF8=1` 적용)
- `lightgbm`, `pywinauto`, `psutil` 추가 설치 (requirements.txt 외 필수 패키지)
- `py310_64` conda env 생성 (EOD 재학습용)
- `requirements_310.txt` 패키지 설치

### STEP 4: CREON 자격증명 등록 (Windows Credential Manager)

```bat
conda activate py37_32
python scripts\set_cybos_credential.py
```

또는 직접:
```bat
cmdkey /add:creonplus /user:대신증권아이디 /pass:비밀번호
```

> `cybos_autologin.py --broker creon`이 `creonplus` 키를 참조하여 자동 로그인합니다.

### STEP 5: secrets.py 생성

```bat
copy config\secrets_example.py config\secrets.py
```

`config\secrets.py` 편집:
```python
ACCOUNT_NO   = "계좌번호"
ACCOUNT_PWD  = "계좌비밀번호"
BOK_API_KEY  = ""   # 선택 (거시경제 피처)
KAKAO_TOKEN  = ""   # 선택 (알림)
```

### STEP 6: 첫 실행

```bat
CREON_PLUS.bat          # Cybos Plus 연결
start_mireuk_CREON.bat  # 미륵이 실행
```

---

## 5. 크론 자동 업데이트 설정

타 PC에서 자동으로 최신 코드를 받아 실행하려면:

### 방법 A: Windows 작업 스케줄러

```bat
REM 매일 08:50에 git pull 후 미륵이 실행
git -C "%USERPROFILE%\PycharmProjects\futures" pull origin maitreya_dist
start_mireuk_CREON.bat
```

### 방법 B: PowerShell 스케줄 스크립트

`register_eod_scheduler.ps1` 참고하여 작업 스케줄러 등록.

---

## 6. 배포 브랜치 유지 전략

```
dev           ← 개발 브랜치 (MW0601 PC 작업)
main          ← 안정 릴리즈
maitreya_dist ← 배포 전용 (타 PC pull 대상)
```

- MW0601 PC에서 `dev → main` 머지 후 `maitreya_dist` 에 cherry-pick 또는 rebase
- 모델 파일(pkl) 변경 시 배포 브랜치도 함께 업데이트
- `config/secrets.py`는 절대 커밋하지 않음

---

## 7. TODO LIST

### 7-1. 브랜치 생성 / 초기 설정

- [x] `docs/260629_MAITREYA_DIST_DEPLOYMENT_PLAN.md` 작성
- [x] `maitreya_dist` 브랜치 생성 (from dev) — 완료
- [x] `.gitignore` 수정: `model/scaler/`, `model/horizons/`, `data/db/` 제외 줄 주석 처리 → 추적 포함
- [x] `config/secrets_example.py` 작성
- [x] `SETUP_GUIDE.md` 작성 (타 PC 설치 한글 가이드)
- [x] `INSTALL.bat` 작성 + 수정 (SSL DLL 자동 복사, lightgbm·pywinauto 추가, PYTHONUTF8=1)
- [x] `requirements_310.txt` 작성 (py310_64 재학습 의존성)
- [x] `start_mireuk_CREON.bat` 신규 생성 (CREON 전용 런처, 자동 재시작 루프)
- [x] `scripts/set_cybos_credential.py` 신규 생성 (Windows Credential Manager 자격증명 등록)
- [x] `scripts/close_other_windows.ps1` 신규 생성 (런처 실행 전 창 최소화)

### 7-2. 모델 / 데이터 파일

- [x] `model/scaler/*.pkl` 배포 브랜치에 추가 — git ls-files로 추적 확인
- [x] `model/horizons/*.pkl` (GBM 6종 + RF + feature_names) 추적 확인
- [x] `data/db/` — 운영 DB 7종 + json 3종 추적 포함 (raw_data·predictions·trades 등 대용량은 gitignore 유지)
- [ ] `data/*.json` 상태 파일 초기화 버전 검토 — 현재 운영 데이터 포함됨, 타 PC 배포 시 수동 초기화 필요

### 7-3. 검증

- [ ] 타 PC 에서 `INSTALL.bat` → `cmdkey 자격증명 등록` → `CREON_PLUS.bat` → `start_mireuk_CREON.bat` 순서 실행 테스트
- [ ] 모의투자 모드 연결 확인
- [ ] Circuit Breaker 정상 작동 확인

---

## 8. 주의 사항

1. **모델 파일 크기**: `rf_horizons.pkl` 약 60MB — 현재 git 직접 추적 중. 100MB 미만이므로 LFS 불필요
2. **secrets.py 절대 커밋 금지**: `.gitignore`에 `config/secrets.py` 유지
3. **py310_64 환경**: EOD 재학습(`EOD_RETRAIN.bat`)은 py310_64 전용 — py37_32로 실행 시 OOM 발생
4. **Cybos Plus 32-bit COM**: `py37_32` 환경만 COM 오브젝트 접근 가능
5. **포지션 상태 초기화**: 타 PC 배포 시 `data/position_state.json`은 빈 상태(`{}`)로 초기화
6. **32-bit conda SSL 문제**: py37_32 최초 생성 후 pip SSL 오류 발생 시 → `INSTALL.bat`이 자동 처리 (`libssl-1_1.dll`을 `Library\bin\` → `DLLs\`에 복사)
7. **CREON 자격증명**: 타 PC 최초 1회 `cmdkey /add:creonplus /user:ID /pass:PW` 또는 `python scripts\set_cybos_credential.py` 실행 필수

---

## 9. 파일 크기 체크 (모델 파일)

배포 전 아래 명령으로 모델 파일 크기 확인:

```powershell
Get-ChildItem "model\scaler" -Recurse | Measure-Object -Property Length -Sum
# 100MB 초과 시 Git LFS 설정 필요
```

GitHub 단일 파일 제한: 100MB / 저장소 권장 한도: 1GB  
초과 시 → `git lfs track "*.pkl"` 설정 후 커밋
