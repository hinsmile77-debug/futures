# cybos_autologin.py 디버깅 세션 기록

> 작성일: 2026-05-11  
> 목적: `scripts/cybos_autologin.py` 완전 자동 로그인 구현을 위한 에러/픽스 전체 정리

---

## 전체 흐름 목표

```
_ncStarter_.exe 실행
  → "CYBOS" 보안 다이얼로그 → "사용안함" 자동 클릭
  → "CYBOS Starter" 로그인 창 → 비밀번호 자동 입력 + 로그인 버튼
  → "모의투자 선택" 창 → "모의투자 접속" 자동 클릭
  → CybosPlus IsConnect == 1 확인
```

---

## 에러 #1 — main.py: CybosPlusConnect() 필수 파라미터 오류

### 증상
```
pywintypes.com_error: (-2147352561, '필수 매개 변수입니다.', None, None)
  File "collection/cybos/api_connector.py", line 224, in connect
    self._cp_cybos.CybosPlusConnect()
RuntimeError: U-CYBOS/CYBOS Plus is not connected.
```

### 원인
`api_connector.py`의 `connect()` 메서드가 `IsConnect == 0`일 때 `CybosPlusConnect()`를 인수 없이 호출.
이 함수는 `(user_id, password, pki_password)` 3개 인수가 필수.

### 픽스
`collection/cybos/api_connector.py`에서 `CybosPlusConnect` / `CreonPlusConnect` 호출 블록 전체 제거.
설계 원칙: autologin 스크립트가 로그인을 완료한 뒤 main.py가 기존 세션을 사용하도록 역할 분리.

```python
# 제거된 코드 (connect() 내부)
if not self.is_connected:
    try:
        if hasattr(self._cp_cybos, "CybosPlusConnect"):
            self._cp_cybos.CybosPlusConnect()   ← 인수 없이 호출 → 오류
        ...
    except Exception:
        logger.exception("[Cybos] connect request failed")
    deadline = time.time() + 5.0
    while ...
```

---

## 에러 #2 — autologin: 잘못된 실행 파일 경로

### 증상
```
[INFO] CybosPlus HTS 재시작 중...
[INFO] 로그인 창 대기 중...
[ERROR] 로그인 창을 찾지 못했습니다.
```
동시에 화면에 "ncStarter" 팝업:
> "실행한 프로세스가 종료되어 프로그램을 종료합니다.  
> 시작화면의 [설정] > '최신파일 상세비교'를 체크하신 후 재접속하시기 바랍니다."

### 원인
`CYBOS_EXE = r"C:\DAISHIN\CYBOSPLUS\CpStart.exe"` — 잘못된 경로.  
실제 런처는 `C:\DAISHIN\STARTER\_ncStarter_.exe`.  
`_ncStarter_.exe`가 `CpStart.exe`를 자식 프로세스로 관리하는 구조인데,  
스크립트가 `CpStart.exe`를 kill하자 ncStarter가 "자식 종료됨" 에러를 내고 스스로 종료.

### 픽스
```python
CYBOS_EXE = r"C:\DAISHIN\STARTER\_ncStarter_.exe"
CYBOS_PROC_NAMES = ["_ncstarter_.exe", "cpstart.exe"]
```

---

## 에러 #3 — Kill 순서 문제 → ncStarter 에러 팝업

### 증상
`CpStart.exe`를 먼저 kill하면 ncStarter가 에러 다이얼로그(제목: "ncStarter")를 띄운 뒤 종료.
이후 `subprocess.Popen([CYBOS_EXE])` 로 CpStart.exe를 직접 시작 → 로그인 창 안 뜸.

### 원인
ncStarter가 자신이 관리하는 CpStart.exe가 외부에서 종료되면 에러 감지 후 자기 종료.
CpStart.exe 단독 실행은 지원하지 않음 (ncStarter 경유 필수).

### 픽스
Kill 순서를 `_ncstarter_.exe` 먼저, `cpstart.exe` 나중으로 변경.
ncStarter가 에러 다이얼로그를 띄우기 전에 먼저 종료시킴.

---

## 에러 #4 — ShellExecute vs Popen: 로그인 창 미출현

### 증상
`subprocess.Popen([CYBOS_EXE])` 후 40초 대기해도 로그인 창 없음.

### 원인
- `Popen`은 작업 디렉터리(cwd)를 설치 폴더로 지정하지 않음 → DLL 로드 실패 가능
- UAC manifest가 설정된 경우 `Popen`으로 실행하면 관리자 권한 없이 실행

### 픽스
`ShellExecute`로 변경 (설치 폴더를 cwd로, UAC manifest 존중):
```python
import win32api, win32con
exe_dir = os.path.dirname(CYBOS_EXE)
win32api.ShellExecute(0, "open", CYBOS_EXE, None, exe_dir, win32con.SW_SHOW)
```

---

## 에러 #5 — 보안 다이얼로그 탐지 실패 (핵심 미해결 이슈)

### 증상
화면 3번 모니터에 "CYBOS" 제목의 보안 다이얼로그가 보임.  
`FindWindow(None, "CYBOS")` / `EnumWindows` 25초 내내 탐지 실패.

### 탐지 시도 목록 (모두 실패)

| 시도 | 방법 | 결과 |
|---|---|---|
| 1 | `FindWindow(None, "CYBOS")` | 탐지 안 됨 |
| 2 | `EnumWindows` + IsWindowVisible 필터 | "CYBOSPLUS" = Explorer 탐지 (오탐) |
| 3 | `EnumChildWindows("CYBOSPLUS")` 전체 덤프 | Explorer UI 컨트롤만 나옴 |
| 4 | 모든 top-level 창의 child에서 "사용안함" 텍스트 버튼 탐색 | 탐지 안 됨 |
| 5 | `FindWindow("#32770", "CYBOS")` 클래스+제목 | 탐지 안 됨 |
| 6 | `ctypes.windll.user32.FindWindowW(None, "CYBOS")` | 탐지 안 됨 |

### 5초 후 발견된 단서
창 목록에 `"CYBOSPLUS"` 있음 → 실제로는 Windows 탐색기가 `C:\DAISHIN\CYBOSPLUS` 폴더를 열어둔 것  
(`주소: C:\DAISHIN\CYBOSPLUS` 주소창이 자식 목록에 포함됨).

### 현재 가설 (미확정)
RAON K Hybrid Agent(보안 소프트웨어)가 보안 다이얼로그를 자체 프로세스 컨텍스트에서 렌더링.
일반 `EnumWindows`로 탐지되지 않는 이유:
- RAON이 별도 Win32 Desktop 사용 가능성
- 또는 다이얼로그가 ncStarter 초기화 중 매우 짧게 뜨고 사라짐
- 또는 `IsWindowVisible == False` 상태로 렌더링됨

### 중요 타이밍 발견
- ncStarter가 초기화하는 데 **10~15초** 소요
- 5초 / 10초 탐색 시점에는 보안 다이얼로그가 아직 미생성
- **15초 시점에 "CYBOS Starter" 로그인 창 출현** (부분 매칭으로 오탐)

### 오탐 버그
`if any(k in title for k in ["CYBOS"])` → "CYBOS Starter"도 매칭됨.  
픽스: `FindWindow(None, "CYBOS")` 정확 일치만 사용.

---

## 에러 #6 — 버튼 클릭 방식 문제

### 증상
"CYBOS" 창에서 "사용안함" 버튼을 `GetWindowText`로 탐지 성공했지만 실제 클릭 안 됨.

### 시도 1: `PostMessage(BM_CLICK)` → 실패
커스텀 owner-drawn 버튼은 `BM_CLICK` 메시지에 반응 안 함.

### 시도 2: `_physical_click(cx, cy)` with `SetCursorPos + mouse_event` → 마우스 미이동
`_force_foreground` (AttachThreadInput) 시도했으나 창이 다른 프로세스 권한으로 실행 중이어서 SetForegroundWindow 실패.

### 현재 상태
버튼을 찾아 좌표를 계산하고 `ctypes.windll.user32.SetCursorPos(x, y)` + `mouse_event` 호출은 구현됨.
보안 다이얼로그 자체를 아직 탐지하지 못하는 상태라 클릭 시험 자체가 차단된 상황.

---

## 현재 구현 상태 (autologin.py)

### 설정값
```python
CYBOS_EXE       = r"C:\DAISHIN\STARTER\_ncStarter_.exe"
CRED_TARGET     = "cybosplus"
MOCK_MODE       = True
CONNECT_TIMEOUT = 90
CYBOS_PROC_NAMES = ["_ncstarter_.exe", "cpstart.exe"]
SECURITY_WINDOW_TITLES = {"CYBOS", "RAON K Hybrid Agent"}
LOGIN_WINDOW_KEYWORDS = ("CYBOS Starter", "CYBOS Plus", "CYBOSPLUS")
```

### 처리 순서
```
1. IsConnect 확인 → 이미 연결됨이면 즉시 반환
2. Windows Credential Manager에서 ID/PW 로드
3. 기존 Cybos 프로세스 kill (ncStarter 먼저, CpStart 나중)
4. ShellExecute로 _ncStarter_.exe 실행
5. [120초 통합 루프] 매초:
   - FindWindow(None,"CYBOS") + FindWindowW + FindWindow("#32770","CYBOS") → 보안 다이얼로그 탐색
   - EnumWindows → "CYBOS Starter" / "CYBOS Plus" 로그인 창 탐색
   - 보안 다이얼로그 발견 시 즉시 "사용안함" 물리 클릭 시도
   - 로그인 창 발견 시 루프 종료
6. 로그인 창에서 비밀번호 클립보드 붙여넣기 + 로그인 버튼 클릭
7. [MOCK_MODE=True] "모의투자 선택" 창 → "모의투자 접속" 클릭
8. IsConnect 확인 대기 (최대 90초)
```

### 중요 버그 (linter 도입)
라인 43: `SECURITY_BUTTON_TEXTS = {"?ъ슜?덊븿", "?ъ슜 ?덊븿"}` — 인코딩 깨짐.
올바른 값: `{"사용안함", "사용 안함"}`

---

## 남은 문제

### [미해결] 보안 다이얼로그 자동 탐지

**핵심 질문**: "CYBOS" 다이얼로그가 `FindWindow`으로 탐지되지 않는 이유?

**다음 시도 후보:**
1. ncStarter를 관리자 권한(`runas`)으로 ShellExecute — 보안 다이얼로그가 elevated 프로세스 창일 가능성
2. 다이얼로그 뜨는 정확한 타이밍 확인: ncStarter 실행 후 몇 초 후에 보이는지 스톱워치로 측정
3. `Spy++` 또는 `WinSpy`로 보안 다이얼로그 실제 hwnd, 클래스, 프로세스 ID 확인
4. `SetWinEventHook(EVENT_OBJECT_SHOW)` — 새 창 생성 이벤트 훅으로 다이얼로그 캐치
5. 모니터 3번 좌표를 계산해서 고정 좌표 블라인드 클릭

### [확인 필요] 모의투자 선택 창 자동 클릭

첫 부분 성공 실행 시 Ctrl+C로 중단됨. 실제로 30초 내에 탐지되는지 미확인.

---

## 성공한 부분 (확인됨)

| 단계 | 상태 |
|---|---|
| 기존 프로세스 kill | ✅ |
| ShellExecute로 _ncStarter_.exe 실행 | ✅ |
| "CYBOS Starter" 로그인 창 탐지 | ✅ (hwnd 정상 반환) |
| 비밀번호 클립보드 붙여넣기 | ✅ |
| 로그인 버튼 클릭 | ✅ |
| "모의투자 선택" 창 뜨는 것 확인 | ✅ (Ctrl+C로 인터럽트됨) |
| api_connector.py connect() 오류 제거 | ✅ |

---

## 참고: CybosPlus 창 구조

```
_ncStarter_.exe (C:\DAISHIN\STARTER\)
  ├── 초기화 (~15초)
  ├── [보안 다이얼로그] 제목="CYBOS" — FindWindow 불가 (원인 미상)
  │     버튼: "보안프로그램 사용" | "사용안함"
  └── "CYBOS Starter" 로그인 창 (cls=#32770)
        ├── Edit (아이디)
        ├── Edit (비밀번호)
        └── 로그인 버튼
              └── [MOCK_MODE] "모의투자 선택" 창
                    드롭다운: "상시모의투자"
                    버튼: "모의투자 접속" | "모의투자 참가신청"
```

---

## 실행 환경

- Python: 3.7 32-bit (`conda activate py37_32`)
- OS: Windows 10 Pro (다중 모니터 3대)
- 보안 다이얼로그 위치: 모니터 3번 (왼쪽 모니터)
- 로그인 창 위치: 모니터 1번 (주 모니터, rect 약 919,389 ~ 1641,1011)
- 관련 보안 소프트웨어: RAON K Hybrid Agent (항상 실행 중)
