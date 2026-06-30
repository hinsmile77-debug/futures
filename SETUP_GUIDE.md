# 미륵이 타 PC 설치 가이드

> 대상 브랜치: `maitreya_dist`  
> 최종 목표: `CREON_PLUS.bat` → `start_mireuk_CREON.bat` 순서 실행으로 미륵이 정상 작동

---

## 0. 시스템 요구사항

| 항목 | 최소 사양 |
|---|---|
| OS | Windows 10 (64-bit OS + 32-bit Python 혼용 가능) |
| RAM | 최소 8 GB (권장 16 GB) |
| 저장소 | SSD 20 GB 이상 여유 공간 |
| 네트워크 | 안정적인 유선 인터넷 |
| 기타 | 대신증권 계좌 (Cybos Plus 사용 권한) |

---

## 1. Cybos Plus (대신증권 HTS) 설치

1. 대신증권 홈페이지 → HTS → **Cybos Plus** 다운로드
2. 설치 — 기본 경로: `C:\DAISHIN\`
3. 반드시 **모의투자** 또는 **실투자** 로그인 테스트 확인 후 HTS 종료
4. ncStarter.exe 위치 확인: `C:\DAISHIN\STARTER\ncStarter.exe`

---

## 2. Anaconda 설치 (32-bit Python 지원)

> Cybos Plus COM/OCX 연동을 위해 **32-bit Python 3.7** 이 필수입니다.

1. [Anaconda 공식 홈페이지](https://www.anaconda.com/download) → Windows 64-bit 설치 (OS 64-bit, Python 환경은 32-bit 가상환경 생성)
2. 설치 경로 기본값: `%USERPROFILE%\anaconda3`
3. 설치 후 **Anaconda Prompt** 실행 확인

---

## 3. 저장소 클론

Git이 설치되어 있어야 합니다.

```bat
git clone -b maitreya_dist https://github.com/hinsmile77-debug/futures.git %USERPROFILE%\PycharmProjects\futures
cd %USERPROFILE%\PycharmProjects\futures
```

---

## 4. INSTALL.bat 실행 (환경 자동 구성)

```bat
INSTALL.bat
```

이 스크립트가 자동으로 수행하는 작업:
- `py37_32` conda 가상환경 생성 (Python 3.7 32-bit)
- `requirements.txt` 패키지 설치
- `py310_64` conda 가상환경 생성 (Python 3.10 64-bit, EOD 재학습용)
- `requirements_310.txt` 패키지 설치

설치 완료까지 약 5~15분 소요.

---

## 5. 계좌 정보 등록

Windows Credential Manager 에 Cybos Plus 인증 정보를 등록합니다.

```bat
conda activate py37_32
python scripts\set_cybos_credential.py
```

입력 항목:
- **Cybos Plus ID**: 대신증권 아이디
- **Cybos Plus 비밀번호**: 로그인 비밀번호
- **계좌번호**: 선물 거래 계좌 번호
- **계좌 비밀번호**: 계좌 비밀번호

등록 후 Credential Manager에서 확인 가능:
`제어판 → 사용자 계정 → 자격 증명 관리자 → Windows 자격 증명`

---

## 6. secrets.py 생성

```bat
copy config\secrets_example.py config\secrets.py
```

메모장 또는 에디터로 `config\secrets.py` 를 열어 아래 항목 입력:

```python
FUTURES_CODE_PREFIX = "A01"   # 모의투자: "A01" / 실투자: "A05"
ACCOUNT_NO  = "계좌번호"
ACCOUNT_PWD = "계좌비밀번호"
```

> **주의**: `secrets.py` 는 `.gitignore` 에 포함되어 절대 Git 에 업로드되지 않습니다.

---

## 7. 첫 실행

두 개의 CMD 창을 순서대로 엽니다.

### 7-1. CREON Plus 연결 (첫 번째 CMD)

```bat
CREON_PLUS.bat
```

- Cybos Plus 자동 로그인 실행
- 모의투자 연결 팝업 → 자동 클릭
- 연결 성공 시: `[OK] Cybos Plus session ready` 출력

### 7-2. 미륵이 실행 (두 번째 CMD)

```bat
start_mireuk_CREON.bat
```

- `CREON_PLUS.bat` 창을 닫지 말고 유지
- 미륵이 대시보드(Qt 창) 실행 확인

---

## 8. 크론 자동 업데이트 설정

### 방법: Windows 작업 스케줄러

1. 작업 스케줄러 열기: `taskschd.msc`
2. 기본 작업 만들기
3. 트리거: 매일 08:40
4. 동작: 프로그램 실행

```
프로그램: %USERPROFILE%\PycharmProjects\futures\auto_update.bat
```

`auto_update.bat` 내용:
```bat
@ECHO OFF
git -C "%USERPROFILE%\PycharmProjects\futures" pull origin maitreya_dist
```

---

## 9. 문제 해결

### Q1. `CREON_PLUS.bat` 실행 시 "auto-login failed"
- `C:\DAISHIN\STARTER\ncStarter.exe` 존재 확인
- `python scripts\set_cybos_credential.py` 재실행으로 인증 정보 재등록
- Cybos Plus HTS 수동 실행 후 연결 확인

### Q2. `py37_32` 환경이 없다고 오류
- `INSTALL.bat` 재실행
- 또는 수동: `conda create -n py37_32 python=3.7 --channel conda-forge`

### Q3. COM 오류 `win32com` not found
- 32-bit Python에서 `pywin32` 설치 필요:
  ```bat
  conda activate py37_32
  pip install pywin32
  python scripts\win32com_postinstall.py
  ```

### Q4. Qt 플러그인 오류
- BAT 파일이 `QT_PLUGIN_PATH` 를 자동 설정합니다
- 문제 지속 시: `conda activate py37_32 && pip install PyQt5==5.15.10`

### Q5. 로그 확인
```
logs\creon_plus_launch.log   -- CREON Plus 연결 로그
logs\Mireuk_batch\           -- 미륵이 실행 로그
```

---

## 10. EOD 재학습 (선택)

종가 이후 GBM 모델 재학습:

```bat
EOD_RETRAIN.bat
```

> **주의**: `py310_64` 환경 전용. `py37_32` 에서 실행 시 OOM 발생.

---

## 11. 업데이트

새 버전을 받으려면:

```bat
git -C "%USERPROFILE%\PycharmProjects\futures" pull origin maitreya_dist
```

모델 파일(pkl)이 변경된 경우 자동으로 업데이트됩니다.
