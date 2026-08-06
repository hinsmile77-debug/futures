# MW0602 브랜치 공유 설정 가이드

## 배경

| 항목 | MW0601 | MW0602 |
|---|---|---|
| API | Cybos Plus (대신증권) | CREON Plus (대신증권) |
| HTS 실행파일 | `C:\DAISHIN\STARTER\ncStarter.exe` | `C:\CREON\STARTER\coStarter.exe` |
| 자격증명 키 | `cybosplus` | `creonplus` |
| UAC 상승 필요 | 불필요 | 필요 (coStarter.exe UIPI 제약) |

두 PC 는 **동일한 `dev` 브랜치**를 공유하고, PC별 차이는 gitignore 된 `machine.cfg` 한 파일로 분기한다.

> 이 방식이 실제 채택된 접근이다. 별도 브랜치(`maitreya_dist`)로 배포 설정을 분리하는 초기 계획
> (`_archive/docs/260629_MAITREYA_DIST_DEPLOYMENT_PLAN.md`)은 공유-`dev`-브랜치 + `machine.cfg`
> 분기 방식으로 대체 운영 중이다.

---

## 머신 전용 파일 목록 (gitignore 대상)

아래 파일들은 커밋되지 않으며, 각 PC 에 로컬로만 존재한다.

### 공통 gitignore
| 파일 | 설명 |
|---|---|
| `machine.cfg` | 브로커 지정 설정 (아래 참조) |

### MW0601 전용 (git 추적 제외)
| 파일 | 설명 |
|---|---|
| `CYBOS5.bat` | Cybos5 HTS 세션 런처 (스케줄 등록: `Cybos5_HTS` 08:56) |

> [2026-08-06] `CYBOS_PLUS.bat` / `start_mireuk_Cybos.bat` **삭제됨.**
> 실제 스케줄에 등록된 것은 `LAUNCH_API.bat`(`Cybos Plus` 08:35)과
> `start_mireuk.bat`(`미륵이` 08:40)이며, 둘 다 `machine.cfg`의 `BROKER`로
> cybos/creon을 분기한다. 삭제한 구버전 2개는 같은 로그파일에 기록해
> 사후 분석 시 어느 런처의 출력인지 구분할 수 없게 만들었다.

### MW0602 전용 (git 추적 제외)
| 파일 | 설명 |
|---|---|
| `CREON_PLUS.bat` | CREON Plus API 연결 런처 (구버전) |
| `start_mireuk_CREON.bat` | 미륵이 CREON 실행 런처 (구버전) |

> **구버전 런처는 로컬에 남겨도 무방하다.** 신규 통합 런처(`LAUNCH_API.bat`, `start_mireuk.bat`)로 이전 완료 후 삭제 가능.

### 주의: 추가 배타적 파일 가능성

아래 파일들은 공유 코드이지만 MW0602 환경에 맞게 조정된 내용을 포함할 수 있다.  
MW0602 전용 수정이 생기면 해당 파일도 `machine.cfg` 와 동일하게 gitignore 추가를 검토한다.

| 파일 | 주의 사항 |
|---|---|
| `scripts/cybos_autologin.py` | Cybos/CREON 공용 로그인 스크립트. `--broker` 인자(=machine.cfg의 BROKER)로 내부 분기하며 CREON 좌표는 MW0602 모니터 기준으로 보정됨. 별도 파일로 분리하지 않고 이 파일 하나를 양쪽 PC가 공유한다 — 화면 해상도/배율이 PC마다 다르면 좌표 diverge 가능하니 수정 시 양쪽 모두 재검증할 것. |
| `register_eod_scheduler.ps1` | Windows 작업 스케줄러 등록 경로가 PC마다 달라 gitignore 대상 (machine.cfg 방식과 동일). |

---

## MW0602 최초 설정 절차

### 1. `git pull` 로 최신 dev 브랜치 동기화

```cmd
cd C:\Users\<유저명>\PycharmProjects\futures
git pull origin dev
```

### 2. `machine.cfg` 생성

`machine.cfg` 를 메모장으로 열어 수정완료:

```ini
BROKER=creon
```

### 3. 자격증명 등록 (최초 1회)

```cmd
cmdkey /add:creonplus /user:대신증권아이디 /pass:비밀번호
```

### 4. `conda init cmd.exe` 확인 (MW0602 필수)

MW0602 에서 `conda activate py37_32` 가 CMD 에서 동작하려면 conda init 이 필요하다.

```cmd
conda init cmd.exe
```

이후 **CMD 창을 완전히 닫고 새로 열어야** 적용된다.

> 미실행 시 `start_mireuk.bat` 가 PY32 하드코딩 경로로 자동 탐색하므로  
> 동작은 하지만 경고 메시지가 출력된다.

### 5. py37_32 환경 확인

```cmd
conda activate py37_32
python -c "import struct; print(struct.calcsize('P'))"
```

출력값이 `4` 이어야 한다 (32-bit). `8` 이면 64-bit 환경 — 재생성 필요:

```cmd
conda create -n py37_32 python=3.7 --force
```

---

## 신규 통합 런처 사용법

| 런처 | 역할 | 실행 순서 |
|---|---|---|
| `LAUNCH_API.bat` | CREON Plus HTS 자동 로그인 | ① 먼저 실행 |
| `start_mireuk.bat` | 미륵이 본체 실행 | ② 이후 실행 |

> `LAUNCH_API.bat` 는 관리자 권한으로 자동 재실행된다 (UAC 승인 필요).

두 런처 모두 `machine.cfg` 의 `BROKER=creon` 을 읽어 CREON 모드로 동작한다.

---

## gitignore 에 파일 추가하는 방법 (필요 시)

MW0602 에만 존재해야 하는 파일이 추가되면:

1. `.gitignore` 에 해당 파일명 추가
2. 이미 추적 중인 경우: `git rm --cached <파일명>`
3. 커밋: `git commit -m "gitignore: <register_eod_scheduler.ps1> PC별 경로 하드코딩으로 제외"` (예시)
4. MW0601 에 `git pull` 하면 해당 파일이 git 에서 제거됨 (로컬 파일은 유지)

---

## 브랜치 공유 구조 요약

```
dev 브랜치 (공유)
├── machine.cfg.example       ← 템플릿 (커밋됨)
├── LAUNCH_API.bat            ← 통합 런처, machine.cfg 읽음 (커밋됨)
├── start_mireuk.bat          ← 통합 런처, machine.cfg 읽음 (커밋됨)
├── scripts/cybos_autologin.py ← Cybos/CREON 공용, --broker 인자로 내부 분기 (커밋됨)
└── ... (공유 코드)

MW0601 로컬만 존재 (gitignore)
├── machine.cfg               ← BROKER=cybos
├── register_eod_scheduler.ps1 ← 이 PC 사용자 경로로 하드코딩
└── CYBOS5.bat                ← Cybos5 HTS 세션 (08:56 스케줄)

MW0602 로컬만 존재 (gitignore)
├── machine.cfg               ← BROKER=creon
├── register_eod_scheduler.ps1 ← 이 PC 사용자 경로로 하드코딩
├── CREON_PLUS.bat            ← 구버전 (사용 중이면 유지, 아니면 삭제 가능)
└── start_mireuk_CREON.bat
```
