# Cybos Plus 자동 로그인 흐름

파일: `scripts/cybos_autologin.py`  
최종 갱신: 2026-05-15

---

## 전체 흐름 개요

```
ncStarter.exe 실행
        │
        ▼
STEP 1+2  보안 다이얼로그 클릭 + 로그인 창 대기          (최대 120초)
        │
        ▼
STEP 3    비밀번호 입력 + 로그인                          (즉시)
        │
        ▼
STEP 4    모의투자 선택 창 감지 → 모의투자 접속 클릭      (최대 65초)
        │
        ▼
          공지사항 팝업 닫기                              (최대 10초)
        │
        ▼
STEP 5    연결 완료 대기 (IsConnect == 1)                 (최대 90초)
        │
        ▼
[OK]  미륵이(main.py) 인계
```

---

## 각 단계 상세

### STEP 1+2 — 보안 다이얼로그 + 로그인 창 대기

**함수**: `_wait_for_login_clicking_security(timeout=120)`

| 순서 | 동작 |
|---|---|
| 1 | `ncStarter.exe /prj:cp` ShellExecute 실행 |
| 2 | WinEventHook(`EVENT_OBJECT_SHOW`) 설치 — 창 등장 즉시 포착 |
| 3 | 200ms 간격 폴링: "CYBOS" 보안 다이얼로그 탐지 |
| 4 | 보안 창 발견 → "사용안함" 버튼 BM_CLICK |
| 5 | 12~17초 구간에서도 보안 창 미탐지 시 블라인드 클릭으로 보완 |
| 6 | "CYBOS Starter" 로그인 창 발견 시 hwnd 반환 |

**보안 창 탐지 3중화**
```
WinEventHook (실시간)
    ↓ 실패 시
FindWindowW / FindWindow (폴링)
    ↓ 실패 시
블라인드 클릭 (12~17초 구간, 최후 수단)
```

---

### STEP 3 — 비밀번호 입력 + 로그인

**함수**: `_perform_login(hwnd, password)`

| 순서 | 동작 |
|---|---|
| 1 | 로그인 창 포그라운드 활성화 |
| 2 | 자식 Edit 컨트롤 탐지 (높이 휴리스틱 → 위치 휴리스틱) |
| 3 | `WM_SETTEXT`로 비밀번호 입력 |
| 4 | Enter 전송 |
| 5 | "로그인" 버튼 BM_CLICK (Enter 실패 보완) |
| 6 | 비밀번호 갱신 확인 팝업 처리 (최대 5초) |

**비밀번호 로드 우선순위**
```
PASSWORD_OVERRIDE 상수 (현재: "amazin16")
    ↓ 비어 있으면
Windows Credential Manager (cmdkey /add:cybosplus)
```

---

### STEP 4 — 모의투자 선택 창

**함수**: `_handle_mock_select_dialog(timeout=45, min_wait=20)`

#### 타이밍

```
로그인 클릭
    │
    ├─ min_wait 구간 (0~20초): 매초 탐지
    │     └─ 감지되면 즉시 클릭 → 종료
    │
    ├─ 20초 경과 후 창 미발견 시:
    │     Enter 전송 (기본 선택 강제) → 3초 대기
    │
    └─ 폴링 루프 (최대 45초): 매초 탐지
          └─ 감지되면 즉시 클릭 → 종료
```

#### 창 탐지 4단계

| 단계 | 방법 | 비고 |
|---|---|---|
| 1차 | `FindWindow(None, "모의투자 선택")` | top-level, 가장 빠름 |
| 2차 | `EnumWindows` + 제목 키워드 매칭 | top-level 전체 순회 |
| 3차 | `#32770` 다이얼로그 클래스 + 키워드 | 표준 Win32 모달 다이얼로그 |
| 4차 | `EnumChildWindows` 전수 탐색 | **Cybos가 자식 창으로 생성 시 대비** |

**4차 탐색 상세**
```
EnumWindows → 각 top-level 창에 EnumChildWindows 적용
    자식 중 "모의투자 접속" 버튼 발견
        → GetParent(버튼) = 다이얼로그 창 반환
```

#### 버튼 클릭 3단계 (`_click_mock_access_in_window`)

| 단계 | 조건 | 동작 |
|---|---|---|
| 1차 | `MOCK_ACCESS_BUTTON_TEXTS` 정확한 텍스트 매치 | BM_CLICK |
| 2차 | "접속" 또는 "모의" 부분 매치 | BM_CLICK |
| 3차 | 다이얼로그 내 모든 Button 중 가장 아래쪽 | BM_CLICK |
| fallback | 버튼 미발견 | 포그라운드 + Enter 전송 |

---

### STEP 4.5 — 공지사항 팝업 닫기

**함수**: `_dismiss_notice_popups(timeout=10)`

모의투자 접속 직후 자동으로 실행. 최대 10초 간 매초 탐색.

| 탐지 방법 | 대상 키워드 |
|---|---|
| `FindWindow` 직접 | `공지사항`, `오늘의공지`, `Cybos공지`, `공지` |
| `EnumWindows` 키워드 | 동일 + 메인 창 제목은 제외 |

닫기 버튼(`닫기`, `확인`, `OK`) BM_CLICK → 없으면 `WM_CLOSE`

---

### STEP 5 — 연결 완료 대기

**함수**: `autologin()` 내 루프

```python
CpUtil.CpCybos.IsConnect == 1  # 매초 폴링, 최대 90초
```

루프마다 `_dismiss_error_dialogs()` 호출 — `CpStart`, `CPUTIL`, `공지사항` 에러창 자동 닫기.

---

## 설정 상수 (`cybos_autologin.py` 상단)

| 상수 | 현재값 | 설명 |
|---|---|---|
| `CYBOS_EXE` | `C:\DAISHIN\STARTER\ncStarter.exe` | HTS 실행 파일 경로 |
| `MOCK_MODE` | `True` | True=모의투자, False=실투자 |
| `MOCK_POPUP_MIN_WAIT` | `20` | 로그인 후 모의투자 창 최소 대기(초) |
| `CONNECT_TIMEOUT` | `90` | 연결 완료 최대 대기(초) |
| `PASSWORD_OVERRIDE` | `"amazin16"` | 임시 비밀번호 (비워두면 Credential Manager 사용) |

---

## 오류 대응 요약

| 증상 | 원인 | 대응 |
|---|---|---|
| 보안 다이얼로그 미탐지 | WinEventHook 실패 | 12~17초 구간 블라인드 클릭 |
| 로그인 창 미탐지 120초 초과 | 프로세스 이상 | `sys.exit(1)` — 수동 확인 필요 |
| `candidates=[]` (모의투자 창) | Cybos가 자식 창으로 생성 | 4차 탐색(`EnumChildWindows`) 대응 |
| 공지사항 팝업으로 연결 지연 | Cybos 공지 | Step 4.5 + Step 5 루프 이중 처리 |
| 연결 타임아웃 90초 초과 | 서버 이상 | `autologin()` False 반환 |
