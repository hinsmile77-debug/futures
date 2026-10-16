# MW0601 2026-10-16 — 아침 CREON Plus 기동 흐름 · coStarter ACCESS_VIOLATION 팝업 딥다이브

- 작성: 2026-10-16 08:50 (장전 — 라이브 DB 미사용, 로그·이벤트로그·프로세스만)
- 대상 팝업: `coStarter — Unhandled exception has occured / ExceptionCode: C0000005 (ACCESS_VIOLATION) / ExceptionAddress: 42397A (coStarter.exe)`
- 선행: `MW0601-20261015-CREON런처기동흐름-딥다이브.md` (이상점 B·E · F-E1)

## 0. 결론 한 줄

**전날 세션의 CpStart·DibServer 가 밤새 「좀비」로 남는다.** 아침 08:35 첫 COM 접속에 DibServer 가
죽고(매일 08:35:1x, 6거래일 연속 재현), 죽지 않는 CpStart 때문에 coStarter 가 「이미 실행중 → 예」를
거치며 **DibServer 와 함께 크래시**한다 — 그것이 화면의 팝업이다. 그 뒤 자동로그인 재시도는 전부 헛돈다.

## 1. 오늘 타임라인

| 시각 | 사건 | 근거 |
|---|---|---|
| 10-15 14:18 | 마지막 API 세션 기동(CpStart) | `creon_plus_launch.log` |
| 10-15 15:47:15 | 미륵이 `auto_shutdown` — **API 세션(CpStart/DibServer)은 그대로 둔다** | 런처 로그 |
| (밤사이) | 서버 쪽 세션 종료 → 프로세스만 남은 좀비(IsConnect=0) | 08:35:19 `PlusDisconnect … NOT_CONNECTED` |
| 08:35:00 | `CREON Plus` 작업 → LAUNCH_API 첫 IsConnect 판독(COM 접속) | `creon_plus_launch.log` |
| **08:35:13** | **DIBSERVER.EXE ACCESS_VIOLATION** (이벤트 1000) | Application 로그 |
| 08:35:17–36 | 자동로그인: PlusDisconnect=NOT_CONNECTED → kill → **CpStart 11720 「예외 없이 생존」** | diag |
| 08:35:39 | coStarter 기동 → 08:35:51 「CPSTART 이미 실행중 — 종료?」 → '예' | diag |
| **08:35:51–54** | **DIBSERVER 재크래시 2회 + coStarter 크래시**(덤프 `261016_083554coStarter.exe.dmp`) = **팝업** | 이벤트로그 · 덤프 |
| 08:39:44 | 1차 240초 무연결(크래시한 coStarter 는 팝업에 막혀 생존 — 08:39:55 kill 실패) | diag |
| 08:39:59 | 2차 시도 시작 — 결과 기록 없음 | diag |
| 08:40:00 | 미륵이 런처 STEP 4 대기 | `launcher_20261016_084001` |
| 08:42:07 · 08:42:11 | 미륵이 런처 · CREON Plus 작업 **둘 다 종료**(사람이 창을 닫은 것으로 보임 — 결과 줄 없음) | 작업 스케줄러 201 |
| 08:43 | CREON HTS 경로 사인온 `ID - [SMART7NA]` (수동) | `ncstarter.log` |
| 08:44:50–51 | API(DL) 사인온 → 새 DibServer·CpStart → 세션 783343908 (수동) | `ncstarter.log` · 프로세스 |
| 08:45:32 | `미륵이` 수동 실행(이벤트 110) → 08:45:55 preflight PASS(783343908) → main.py | 런처 |
| 08:47:03–31 | `CREON_AutoStart`(08:42 예약분) HTS 로그인 11초 · **계좌 비밀번호 창(783293269) 자동 처리** · 전후 API 783343908 유지. 08:47:04 수동 중복 실행은 뮤텍스로 물러남 ✅ | `creon_start.log` · `creon_acct_pw.log` |

## 2. 원인 근거

### 2-1. 「매일 08:35:1x DibServer 크래시」 — 우연이 아니다

Application 로그 60일, DIBSERVER.EXE 크래시 시각:

| 날짜 | 08:35 첫 크래시 |
|---|---|
| 09-24(목) | 08:35:13 |
| 10-05(월) | 08:35:14 |
| 10-06(화) | 08:35:10 |
| 10-13(화) | 08:35:13 |
| 10-15(목) | 08:35:13 |
| 10-16(금) | 08:35:13 |

전부 **`CREON Plus` 작업(08:35:00) 시작 10–14초 뒤** = LAUNCH_API 의 첫 COM 판독 시점이다.
그 밖의 크래시(05:45·06:14·07:17·07:24·20:35·21:25)도 **장 밖 시각에 처음 접속한 순간**이다.
→ 밤을 넘긴 DibServer 는 첫 COM 클라이언트를 받는 순간 죽는다.

### 2-2. coStarter 크래시는 「이미 실행중 → 예」 직후다 (3/3)

| 날짜 | '예' 클릭 | coStarter 덤프 |
|---|---|---|
| 10-13 | (17:18–17:19 재로그인 중) | 17:19:26 |
| 10-15 | 08:35:40 | 08:35:44 |
| 10-16 | 08:35:51 | 08:35:54 |

'예' 는 coStarter 에게 기존 CpStart 를 내리라는 뜻인데, 그 CpStart 는 좀비이고 우리 kill 로도 안 내려간다.
coStarter 가 그 정리 과정에서 DibServer 와 함께 접근 위반을 낸다(덤프 · 이벤트로그 시각 일치).
⚠ coStarter 내부 원인(42397A 지점)은 벤더 코드라 확정 불가 — **촉발 조건**만 확정이다.

### 2-3. 그 뒤가 왜 다 헛도는가

크래시한 coStarter 는 이 **팝업(모달)** 에 붙들려 살아 있다 → 자동로그인의 kill 무효(이상점 E) →
2·3차 시도가 같은 상태에서 다시 시작된다. 08:40 미륵이 런처의 300초 대기도 그 안에 끝날 수 없다.

### 2-4. 어제 넣은 F-E1(PlusDisconnect 선행)이 오늘 못 막은 이유

`PlusDisconnect()` 는 **연결이 살아 있을 때만** 부른다(`IsConnect==1`). 좀비는 IsConnect=0 이라
`NOT_CONNECTED` 로 건너뛰었다. 어제 13:41 에 효과를 본 것은 연결이 살아 있던 세션이었다.

## 3. Fix 계획

| ID | 내용 | 근거 | 위험 | 우선 |
|---|---|---|---|---|
| **M-1** | **장후 API 세션 정리** — 연결이 살아 있을 때 `PlusDisconnect()` 로 내린다(어제 13:41 실효 확인된 유일한 방법). 시점: API 를 쓰는 장후 작업(15:52 RegularCollect · 16:05/16:20 OptionFlowBackfill 등)이 끝난 뒤, **미륵이 main.py 가 떠 있지 않을 때만** | 좀비의 출발점 제거 — 아침이 「깨끗한 시작」이 된다 | 저녁 수동 세션과 겹치지 않게 조건 필요 | **P0** |
| **M-2** | 자동로그인: 좀비 감지(`CpStart 생존 && IsConnect=0`) 시 **「이미 실행중」에 '예' 를 누르지 않는다** — 누르면 크래시가 확정이다. 대신 좀비 정리 시도(PlusDisconnect 를 IsConnect 무관하게 1회 · CpStart 창 WM_CLOSE) → 그래도 남으면 **즉시 실패 + 사유 명시**(12분 헛돌기 대신) | 2-2 의 3/3 상관 | 정리 수단의 효과는 **미검증** — 내일 아침 좀비로 1회 시험 필요 | P1 |
| **M-3** | 자동로그인: coStarter 「Unhandled exception」 창 감지 → 확인 클릭 → 크래시 사실 로그 → 240초를 기다리지 않고 다음 단계 | 2-3 | 낮음 | P1 |
| **M-4** | LAUNCH_API 첫 IsConnect 판독이 좀비 DibServer 를 죽이는 것은 **증상**이다 — M-1 로 사라지면 따로 손대지 않는다 | 2-1 | — | 관찰 |

## 3-1. 구현 (2026-10-16 장후, 사용자 지시)

**정리 시각 16:30 — 장후 작업 실측(10-12–10-16)으로 결정**

| 작업 | API(COM) | 실측 시작–종료 |
|---|---|---|
| 15:52 RegularCollect (`collect_regular_futures.py`) | 사용 | 15:52:02–15:52:23 |
| 15:55 신동2 장후 (`shindong2_run.ps1` → Claude) | 미사용(스크립트 COM 0) — 결과는 사다리 「신동2 해설」 패널 | 15:55–16:06:25 |
| 16:20 OptionFlowBackfill (`backfill_option_flow.py`) | 사용 | 16:20:00–**16:23:09** (가장 늦음) |
| (비정기) `aggregate_and_backfill.py` 17:40대 빈 로그 | — | 예약 아님 |

→ 16:23:09 + 약 7분. 실행 시점에 COM 스크립트가 돌고 있으면 최대 15분 기다리고, 그래도 돌면 API 정리는 건너뛴다.

| ID | 구현 | 검증 |
|---|---|---|
| **M-1** | `scripts/eod_session_cleanup.ps1`(ASCII, 사다리 스크립트와 같은 형식) + 예약작업 `\Mireuk\Mireuk_EodSessionCleanup` 월–금 16:30 · RunLevel Highest · StartWhenAvailable **없음**(저녁 늦은 부팅은 사용자 세션일 수 있다). 순서: ① **미륵이 main.py 가 떠 있으면 전부 건너뜀**(사용자가 다시 올려 쓰는 중) ② COM 스크립트 대기 ③ 사다리 서버·콘솔 종료 ④ `scripts/broker_session_cleanup.py`(py37_32) — PlusDisconnect 후 CpStart 소멸 확인. CREON HTS(coMain)는 건드리지 않는다 | **16:39 실실행**: 사다리 서버 23908·콘솔 30576 종료 · `RESULT=DISCONNECTED was_connected=1 cpstart [20564]→[]` · DibServer 도 소멸 · 새 판독 IsConnect=0 |
| 사다리 종료 | M-1 에 포함. 미륵이 15:47 종료 시점이 아니라 16:30 인 이유: 신동2 장후(16:06 끝)의 해설을 사다리 패널로 보기 때문 | 위와 동일 |
| **M-2** | 자동로그인 `PlusDisconnect` 를 IsConnect 와 무관하게 요청(좀비 대비) — 출력에 `was_connected` | 정적 테스트. **좀비에 대한 효과는 미검증**(M-1 로 좀비 자체가 안 생기면 관측 기회도 없다) |
| **M-3** | 대기 루프가 coStarter 「Unhandled exception / ACCESS_VIOLATION」 팝업(coStarter.exe 소유 창만)을 닫고 남은 대기를 버린 뒤 즉시 다음 시도. 「이미 실행중 → 예」 는 유지 — 10-16 08:39:55 판독상 '예' 뒤 좀비 CpStart 는 사라져 있었다(남은 건 팝업에 붙은 coStarter 뿐) | 정적 테스트. 실제 팝업에서는 미검증 |

테스트: `tests/test_692_eod_session_cleanup.py`(5) · `test_631_autologin_retry_guard.py`(+2).

## 4. 오늘 정상 동작 확인된 것 (어제 배포분)

- `creon_start.ps1`: 대기 진행 로그(Cybos 1·2분, main.py 1분) · **단일 인스턴스(08:47:04 수동 중복 실행 물러남)** · 새 coMain 판정(11초) · 전후 API 계좌 판독
- `creon_acct_pw_dialog`: HTS 계좌 비밀번호 창 **자동 처리(2일 연속)**
- 미륵이 preflight 783343908 PASS
